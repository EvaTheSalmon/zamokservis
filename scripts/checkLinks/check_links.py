import requests
from requests import Response
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urljoin, urlparse, urlunparse
import time
from typing import Set, Dict, List, Tuple, Optional, Union
import logging
import os
import asyncio
import aiohttp
from tqdm import tqdm
import re

# --- Конфигурация ---
BASE_URL = "https://beta.zamokservis.com" # Базовый URL для проверки внутренних ссылок
URL_INPUT_FILE = "urls_to_check.txt"   # Файл со списком URL для проверки
LOG_FILE = 'link_checker.log'        # Имя файла логов
MAX_WORKERS = 10                      # Количество параллельных потоков
REQUEST_TIMEOUT = 15                  # Таймаут для HTTP запросов (в секундах)
USER_AGENT = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
              'AppleWebKit/537.36 (KHTML, like Gecko) '
              'Chrome/91.0.4472.124 Safari/537.36')
# Расширения файлов, которые не нужно парсить как HTML
EXCLUDED_EXTENSIONS = {'.pdf', '.doc', '.docx', '.xls', '.xlsx', '.jpg', '.jpeg', '.png', '.gif', '.zip', '.rar'}
# --- Конец Конфигурации ---

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(threadName)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        logging.StreamHandler()
    ]
)

# Тип для хранения информации о битой ссылке
BrokenLinkInfo = Tuple[str, Union[int, str]] # (url, status_code_or_error_string)

class LinkChecker:
    """
    Класс для проверки доступности страниц, изображений и ссылок на заданном
    наборе URL в пределах одного домена.
    """
    def __init__(self, base_url: str):
        if not base_url.endswith('/'):
            base_url += '/'
        self.base_url = base_url
        self.base_domain = urlparse(base_url).netloc
        self.checked_urls: Set[str] = set()
        self.broken_links: Dict[str, List[BrokenLinkInfo]] = {
            'pages': [],
            'images': [],
            'links': []
        }
        # Используем сессию для переиспользования соединений и заголовков
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': USER_AGENT})

    def _normalize_url(self, url: str) -> str:
        """Удаляет якоря и завершающий слэш из URL для унификации."""
        parsed = urlparse(url)
        # Убираем якорь (#fragment)
        path = parsed.path
        # Убираем завершающий слэш, если путь не '/'
        if path != '/' and path.endswith('/'):
            path = path.rstrip('/')
        return urlunparse((parsed.scheme, parsed.netloc, path, parsed.params, parsed.query, ''))


    def is_internal_and_parsable(self, url: str) -> bool:
        """
        Проверяет, является ли URL внутренним (относится к base_url)
        и не указывает ли на файл, который не нужно парсить.
        """
        if not url:
            return False
        # Убираем якоря
        url_no_anchor = url.split('#')[0]
        # Проверяем домен
        if not url_no_anchor.startswith(self.base_url):
             # Позволяем относительные ссылки, которые будут разрешены позже
            if not url_no_anchor.startswith('/') and not url_no_anchor.startswith('./') and not url_no_anchor.startswith('../'):
                # Проверяем, не является ли ссылка протокол-относительной на том же домене
                 if not url_no_anchor.startswith('//' + self.base_domain):
                     return False # Внешняя ссылка

        # Проверяем расширение файла
        path = urlparse(url_no_anchor).path
        file_ext = os.path.splitext(path)[1].lower()
        return file_ext not in EXCLUDED_EXTENSIONS

    def check_resource(self, url: str, method: str = 'GET') -> Tuple[Optional[int], Optional[str], Optional[Response]]:
        """
        Проверяет доступность ресурса (URL или изображения).
        Возвращает (status_code, error_message, response_object).
        status_code=None при ошибке соединения/таймауте.
        error_message содержит текст ошибки при status_code=None.
        response_object содержит объект ответа requests при успехе.
        """
        try:
            if method.upper() == 'HEAD':
                response = self.session.head(url, timeout=REQUEST_TIMEOUT, allow_redirects=True)
            else:
                response = self.session.get(url, timeout=REQUEST_TIMEOUT, allow_redirects=True)
            # Не вызываем raise_for_status(), чтобы обработать 4xx/5xx вручную
            return response.status_code, None, response
        except requests.Timeout:
            logging.warning(f"Таймаут при запросе {method} {url}")
            return None, "Timeout", None
        except requests.RequestException as e:
            logging.warning(f"Ошибка запроса {method} {url}: {e}")
            # Избегаем слишком длинных сообщений об ошибках SSL/Connection
            error_str = str(e).split('\n')[0][:200] # Ограничиваем длину строки ошибки
            return None, error_str, None
        except Exception as e:
            logging.error(f"Неожиданная ошибка при запросе {method} {url}: {e}")
            return None, f"Unexpected error: {str(e)[:100]}", None

    def process_page(self, url: str):
        """
        Обрабатывает одну страницу: проверяет ее доступность,
        находит и проверяет все внутренние ссылки и изображения.
        """
        normalized_url = self._normalize_url(url)
        if normalized_url in self.checked_urls:
            logging.debug(f"URL уже проверен (пропуск): {url}")
            return
        self.checked_urls.add(normalized_url)

        logging.info(f"Проверка страницы: {url}")

        # 1. Проверяем доступность самой страницы
        page_status, page_error, page_response = self.check_resource(url, method='GET')

        if page_status is None or page_status >= 400:
            error_info = page_status if page_status is not None else page_error
            logging.warning(f"Страница недоступна: {url} - {error_info}")
            self.broken_links['pages'].append((url, error_info or "Unknown Error"))
            return # Нет смысла парсить недоступную страницу

        # 2. Парсим HTML, если страница доступна и имеет тип text/html
        content_type = page_response.headers.get('content-type', '').lower()
        if 'text/html' not in content_type:
             logging.info(f"Страница {url} не является HTML ({content_type}), пропуск парсинга ссылок/изображений.")
             return

        try:
            # Используем page_response.content для корректной обработки кодировки
            soup = BeautifulSoup(page_response.content, 'html.parser')
        except Exception as e:
            logging.error(f"Ошибка парсинга HTML страницы {url}: {e}")
            # Можно добавить страницу в ошибки, если парсинг критичен
            # self.broken_links['pages'].append((url, f"HTML Parse Error: {str(e)[:100]}"))
            return # Прерываем обработку, если не можем распарсить

        # 3. Проверяем все изображения
        for img_tag in soup.find_all('img'):
            img_src = img_tag.get('src')
            if not img_src:
                continue # Пропускаем теги img без src

            img_url = urljoin(url, img_src) # Создаем абсолютный URL
            normalized_img_url = self._normalize_url(img_url)

            # Проверяем только внутренние изображения и еще не проверенные
            # (хотя для изображений повторная проверка менее критична)
            if normalized_img_url not in self.checked_urls and self.is_internal_and_parsable(img_url):
                self.checked_urls.add(normalized_img_url) # Отмечаем как проверенный (или попытку проверки)
                logging.debug(f"Проверка изображения: {img_url} (на странице {url})")
                img_status, img_error, _ = self.check_resource(img_url, method='HEAD') # HEAD быстрее для изображений

                if img_status is None or img_status >= 400:
                    error_info = img_status if img_status is not None else img_error
                    logging.warning(f"Битое изображение: {img_url} - {error_info} (на странице {url})")
                    self.broken_links['images'].append((img_url, error_info or "Unknown Error"))

        # 4. Проверяем все ссылки
        for link_tag in soup.find_all('a'):
            link_href = link_tag.get('href')
            if not link_href:
                continue # Пропускаем теги <a> без href

            # Игнорируем ссылки типа mailto:, tel:, javascript: и т.д.
            if link_href.startswith(('#', 'mailto:', 'tel:', 'javascript:')):
                continue

            link_url = urljoin(url, link_href) # Создаем абсолютный URL
            normalized_link_url = self._normalize_url(link_url)

            # Проверяем только внутренние, парсабельные ссылки, которые еще не были проверены
            if normalized_link_url not in self.checked_urls and self.is_internal_and_parsable(link_url):
                self.checked_urls.add(normalized_link_url) # Отмечаем как проверенный (или попытку проверки)
                logging.debug(f"Проверка ссылки: {link_url} (на странице {url})")
                link_status, link_error, _ = self.check_resource(link_url, method='GET') # GET для ссылок

                if link_status is None or link_status >= 400:
                    error_info = link_status if link_status is not None else link_error
                    logging.warning(f"Битая ссылка: {link_url} - {error_info} (на странице {url})")
                    self.broken_links['links'].append((link_url, error_info or "Unknown Error"))

    def run_checks(self, initial_urls: List[str]):
        """
        Запускает проверку всех URL из списка initial_urls в несколько потоков.
        """
        # Добавляем начальные URL в множество для проверки, чтобы избежать дублирования
        urls_to_process = list(set(self._normalize_url(u) for u in initial_urls))
        logging.info(f"Начинаем проверку {len(urls_to_process)} уникальных URL в {MAX_WORKERS} потоках...")

        # Используем ThreadPoolExecutor для параллельного выполнения
        with ThreadPoolExecutor(max_workers=MAX_WORKERS, thread_name_prefix='Checker') as executor:
            # map выполняет функцию process_page для каждого элемента urls_to_process
            # list() используется, чтобы дождаться завершения всех задач
            list(executor.map(self.process_page, urls_to_process))

    def print_results(self):
        """Выводит итоговые результаты проверки в лог."""
        logging.info("\n--- Результаты проверки ---")

        total_broken = 0
        for category, broken_list in self.broken_links.items():
            if broken_list:
                count = len(broken_list)
                total_broken += count
                logging.info(f"\nНайдены битые {category} ({count} шт.):")
                # Сортируем для более удобного просмотра
                sorted_list = sorted(broken_list, key=lambda x: x[0])
                for item_url, status_or_error in sorted_list:
                    logging.info(f"  - {item_url} (Статус/Ошибка: {status_or_error})")

        if total_broken == 0:
            logging.info("\nПроверка завершена. Битых ссылок, страниц или изображений не найдено.")
        else:
             logging.info(f"\nВсего найдено проблем: {total_broken}")
        logging.info("--------------------------")

def load_urls_from_file(filepath: str) -> List[str]:
    """Загружает список URL из файла, игнорируя пустые строки и комментарии (#)."""
    urls = []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    urls.append(line)
        logging.info(f"Загружено {len(urls)} URL из файла {filepath}")
        return urls
    except FileNotFoundError:
        logging.error(f"Ошибка: Файл с URL не найден: {filepath}")
        return []
    except Exception as e:
        logging.error(f"Ошибка при чтении файла {filepath}: {e}")
        return []

def main():
    """Основная функция скрипта."""
    start_time = time.time()
    logging.info("=== Запуск проверки ссылок ===")

    initial_urls = load_urls_from_file(URL_INPUT_FILE)
    if not initial_urls:
        logging.warning("Список URL для проверки пуст. Завершение работы.")
        return

    checker = LinkChecker(BASE_URL)
    try:
        checker.run_checks(initial_urls)
    except Exception as e:
        logging.exception(f"Критическая ошибка во время выполнения проверок: {e}")
    finally:
        # Всегда выводим результаты, даже если была ошибка в run_checks
        end_time = time.time()
        logging.info(f"\nПроверка заняла {end_time - start_time:.2f} секунд")
        checker.print_results()
        logging.info("=== Проверка ссылок завершена ===")

if __name__ == "__main__":
    main()