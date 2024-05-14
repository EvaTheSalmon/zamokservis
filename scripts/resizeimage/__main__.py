import os.path
import sys
import argparse
import logging
import numpy as np

from datetime import datetime
from PIL import Image
from pathlib import Path

width_canonical = [1080, 720, 414, 375, 360, 320]  # display !horizontal resolutions
width_modified = [972, 648, 373, 338, 324, 288]  # image !horizontal resolutions
qualityN: int = 70  # Output image quality

if not Path("logs").is_dir():
    Path("logs").mkdir()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)-5.5s]  %(message)s",
    handlers=[
        logging.FileHandler(
            "logs/" + f"{datetime.now().strftime('%d-%b-%Y %H_%M_%S')}.log"
        ),
        logging.StreamHandler(sys.stdout),
    ],
)


def pr_arr(arr):
    for i in arr:
        print(i)


def convert(file: str, list_of_files: list[str]) -> None:
    """
    Function converts all pictures in dirrectory into webp's and jpg's
    Non jpg or webp files will be removed.
    Files are affected recursevile, file structure preserved
    JPEG and WeBP are separated due to absence of alpha channel in JPEG
    """

    image = Image.open(file).convert("RGBA")

    filename = Path(file).stem
    extension = Path(file).suffix
    path_no_extenstion = Path(file).with_suffix("")

    if str(extension) == ".webp":

        bg = Image.new("RGBA", image.size, (255, 255, 255))

        alpha_composite = Image.alpha_composite(bg, image).convert("RGB")

        alpha_composite.save(
            f"{path_no_extenstion}.jpg", "jpeg", optimize=False, quality=100
        )
        list_of_files.append(f"{path_no_extenstion}.jpg")

        return

    elif str(extension) == ".jpg":

        image.save(f"{path_no_extenstion}.webp", "webp", optimize=False, quality=100)
        list_of_files.append(f"{path_no_extenstion}.webp")

        return

    else:
        bg = Image.new("RGBA", image.size, (255, 255, 255))

        alpha_composite = Image.alpha_composite(bg, image).convert("RGB")

        alpha_composite.save(
            f"{path_no_extenstion}.jpg", "jpeg", optimize=False, quality=100
        )
        list_of_files.append(f"{path_no_extenstion}.jpg")

        image.save(f"{path_no_extenstion}.webp", "webp", optimize=False, quality=100)
        list_of_files.append(f"{path_no_extenstion}.webp")

        os.remove(file)

        list_of_files.remove(file)


def replace_white_with_transparent(file: str) -> None:
    """
    Function replaces white color with alpha channel for webp files
    """

    extension = Path(file).suffix

    if not extension.lower() == ".webp":
        return

    image = Image.open(file)
    if image.mode != "RGBA":
        image = image.convert("RGBA")

    data = image.getdata()
    data_transparent_background = []

    for pixel in data:
        if pixel[0] > 240 and pixel[1] > 240 and pixel[2] > 240:
            data_transparent_background.append((255, 255, 255, 0))

        else:
            data_transparent_background.append(pixel)

    image.putdata(data_transparent_background)

    image.save(file, "WebP", optimize=False, quality=100)


def resize(file: str) -> None:
    """
    Function resizes images to predifined picture heights for css @media at-rules for different screen sizes
    Also compression is done on this step
    """

    with Image.open(file) as image:
        width, height = image.size

        filename = Path(file).stem
        extension = Path(file).suffix
        path_no_extenstion = Path(file).with_suffix("")

        for width_target, width_name in zip(width_modified, width_canonical):

            if width <= width_target:
                image.save(f"{path_no_extenstion}{width_name}{extension}")
                continue

            height_target = int(
                width_target * (height / width)
            )  # new width with propper aspect ratio
            resized_image = image.resize(
                (width_target, height_target), Image.Resampling.BICUBIC
            )
            resized_image.save(f"{path_no_extenstion}{width_name}{extension}")


def compress(file) -> None:
    """
    Function for image compression
    """

    image = Image.open(file)
    image.save(file, optimize=True, quality=qualityN)


def main(self) -> None:

    parser = argparse.ArgumentParser(
        usage="%(prog)s [options]",
        description="This is a tool to convert, \
                                     remove alpha chanel, resize and compress images for the website",
    )

    parser.add_argument(
        "dest_dir",
        metavar="/path/to/your.dir",
        type=str,
        help="input path to folder with images",
    )

    parser.add_argument(
        "--do_not_resize",
        action=argparse.BooleanOptionalAction,
        help="skip resizing for files in folder",
    )

    args = parser.parse_args()
    dest_dir = args.dest_dir
    donotresize = args.do_not_resize

    number_of_files = 0
    file_counter = 1

    list_of_files = []
    processed_files = set()

    for root, _, files in os.walk(dest_dir):
        for file in files:
            list_of_files.append(os.path.join(root, file))

    number_of_files = len(list_of_files)
    logging.info(f"Total files found: {number_of_files}")

    for file in list_of_files:
        
        print(f'Is in? : {bool(set(processed_files) & set(file))}')
        if not bool(set(processed_files) & set(file)):

            processed_files.add(file)

            print(f'current processed data is')
            pr_arr(processed_files)

            logging.info(f"File: {file}. {file_counter} out of {number_of_files}")
            file_counter += 1

            # logging.info("Converting...")
            convert(file, list_of_files)
            number_of_files = len(list_of_files)
            
            # logging.info("Removing white bg...")
            replace_white_with_transparent(file)

            # logging.info("Resizing...")
            if not donotresize:
                resize(file)

            # logging.info("Compressing...")
            # compress(file)


if __name__ == "__main__":
    main(sys.argv)
