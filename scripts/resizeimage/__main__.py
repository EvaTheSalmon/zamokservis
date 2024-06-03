import os.path
import sys
import argparse
import logging

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


def convert(file: str) -> None:
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

    elif str(extension) == ".jpg":

        image.save(f"{path_no_extenstion}.webp", "webp", optimize=False, quality=100)

    else:

        bg = Image.new("RGBA", image.size, (255, 255, 255))

        alpha_composite = Image.alpha_composite(bg, image).convert("RGB")

        alpha_composite.save(
            f"{path_no_extenstion}.jpg", "jpeg", optimize=False, quality=100
        )

        image.save(f"{path_no_extenstion}.webp", "webp", optimize=False, quality=100)

        os.remove(file)


def replace_white_with_transparent(file: str) -> None:
    """
    Function replaces white color with alpha channel for webp files
    """

    whiteness = 235  # out of 255
    extension = Path(file).suffix

    if not extension.lower() == ".webp":
        return

    image = Image.open(file)
    if image.mode != "RGBA":
        image = image.convert("RGBA")

    data = image.getdata()
    data_transparent_background = []

    for pixel in data:
        if pixel[0] > whiteness and pixel[1] > whiteness and pixel[2] > whiteness:
            data_transparent_background.append((255, 255, 255, 0))

        else:
            data_transparent_background.append(pixel)

    image.putdata(data_transparent_background)

    image.save(file, "WebP", optimize=False, quality=100)
    logging.info("File saved")


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


def scan_dir_for_files(dest_dir: str) -> list[str]:
    list_of_files = []
    for root, _, files in os.walk(dest_dir):
        for file in files:
            list_of_files.append(os.path.join(root, file))

    return list_of_files


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

    list_of_files = []

    list_of_files = scan_dir_for_files(dest_dir)
    number_of_files = len(list_of_files)
    file_counter = 0

    logging.info(f"Starting converting...")
    logging.info(f"Total files found: {number_of_files}")

    while file_counter < number_of_files:

        file = list_of_files[file_counter]

        logging.info(
            f"Converting file: {file}. {file_counter + 1} out of {number_of_files}"
        )
        convert(file)

        file_counter += 1

    list_of_files = scan_dir_for_files(dest_dir)
    number_of_files = len(list_of_files)
    file_counter = 0

    logging.info(f"Starting removing bg, (resizing) and compressing...")
    logging.info(f"Total files found: {number_of_files}")

    while file_counter < number_of_files:

        file = list_of_files[file_counter]

        logging.info(
            f"Processing file: {file}. {file_counter + 1} out of {number_of_files}"
        )

        logging.info("Removing white bg...")
        replace_white_with_transparent(file)

        if not donotresize:
            logging.info("Resizing...")
            resize(file)

        logging.info("Compressing...")
        compress(file)

        file_counter += 1


if __name__ == "__main__":
    main(sys.argv)
