import os.path
import sys
import argparse
import logging
from datetime import datetime
from PIL import Image
from pathlib import Path

# Target display widths for different devices
# Display horizontal resolutions
width_canonical = [1080, 720, 414, 375, 360, 320]
# Corresponding image widths for optimization
width_modified = [972, 648, 373, 338, 324, 288]
qualityN: int = 70  # Output image quality for compression

# Ensure the logs directory exists
if not Path("logs").is_dir():
    Path("logs").mkdir()

# Configure logging to file and stdout
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
    Convert image files in the directory to both JPEG and WebP formats.
    Non-JPEG or WebP files will be removed after conversion.
    Files are processed recursively, and directory structure is preserved.
    JPEG and WebP formats are used due to the absence of an alpha channel in JPEG.
    """
    image = Image.open(file).convert("RGBA")
    filename = Path(file).stem
    extension = Path(file).suffix
    path_no_extension = Path(file).with_suffix("")

    if str(extension) == ".webp":
        bg = Image.new("RGBA", image.size, (255, 255, 255))
        alpha_composite = Image.alpha_composite(bg, image).convert("RGB")
        alpha_composite.save(
            f"{path_no_extension}.jpg", "jpeg", optimize=False, quality=100
        )
    elif str(extension) == ".jpg":
        image.save(f"{path_no_extension}.webp", "webp", optimize=False, quality=100)
    else:
        bg = Image.new("RGBA", image.size, (255, 255, 255))
        alpha_composite = Image.alpha_composite(bg, image).convert("RGB")
        alpha_composite.save(
            f"{path_no_extension}.jpg", "jpeg", optimize=False, quality=100
        )
        image.save(f"{path_no_extension}.webp", "webp", optimize=False, quality=100)
        os.remove(file)


def replace_white_with_transparent(file: str) -> None:
    """
    Replace white background with transparency in WebP images.
    """
    whiteness = 235  # Threshold for whiteness
    extension = Path(file).suffix

    if extension.lower() != ".webp":
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
    Resize images to predefined widths for different screen sizes,
    maintaining the aspect ratio. Compression is also applied.
    """
    with Image.open(file) as image:
        width, height = image.size
        filename = Path(file).stem
        extension = Path(file).suffix
        path_no_extension = Path(file).with_suffix("")

        for width_target, width_name in zip(width_modified, width_canonical):
            if width <= width_target:
                image.save(f"{path_no_extension}{width_name}{extension}")
                continue

            # New height with proper aspect ratio
            height_target = int(width_target * (height / width))
            resized_image = image.resize(
                (width_target, height_target), Image.Resampling.BICUBIC
            )
            resized_image.save(f"{path_no_extension}{width_name}{extension}")


def compress(file: str) -> None:
    """
    Compress image file to reduce size while maintaining quality.
    """
    image = Image.open(file)
    image.save(file, optimize=True, quality=qualityN)


def scan_dir_for_files(dest_dir: str) -> list[str]:
    """
    Scan directory recursively and return a list of all file paths.
    """
    list_of_files = []
    for root, _, files in os.walk(dest_dir):
        for file in files:
            list_of_files.append(os.path.join(root, file))
    return list_of_files


def main(self) -> None:
    """
    Main function to parse arguments and process images:
    - Convert images to JPEG and WebP formats.
    - Replace white backgrounds with transparency in WebP files.
    - Optionally resize images for different screen sizes.
    - Compress images to reduce file size.
    """
    parser = argparse.ArgumentParser(
        usage="%(prog)s [options]",
        description="Tool to convert, remove alpha channel, resize, and compress images for the web.",
    )

    parser.add_argument(
        "dest_dir",
        metavar="/path/to/your.dir",
        type=str,
        help="Input path to the folder with images",
    )

    parser.add_argument(
        "--do_not_resize",
        action=argparse.BooleanOptionalAction,
        help="Skip resizing of files in the folder",
    )

    args = parser.parse_args()
    dest_dir = args.dest_dir
    donotresize = args.do_not_resize

    list_of_files = scan_dir_for_files(dest_dir)
    number_of_files = len(list_of_files)

    logging.info("Starting conversion...")
    logging.info(f"Total files found: {number_of_files}")

    for file_counter, file in enumerate(list_of_files, start=1):
        logging.info(
            f"Converting file: {file}. {file_counter} out of {number_of_files}"
        )
        convert(file)

    list_of_files = scan_dir_for_files(dest_dir)
    number_of_files = len(list_of_files)

    logging.info("Starting background removal, (resizing), and compression...")
    logging.info(f"Total files found: {number_of_files}")

    for file_counter, file in enumerate(list_of_files, start=1):
        logging.info(
            f"Processing file: {file}. {file_counter} out of {number_of_files}"
        )
        logging.info("Removing white background...")
        replace_white_with_transparent(file)

        if not donotresize:
            logging.info("Resizing...")
            resize(file)

        logging.info("Compressing...")
        compress(file)


if __name__ == "__main__":
    main(sys.argv)
