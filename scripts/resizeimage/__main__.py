import os.path
import sys
import argparse
import logging
import numpy as np

from resizeimage import resizeimage
from datetime import datetime
from PIL import Image

resolutionsBase = [1080, 720, 414, 375, 360, 320] # display horizontal resolutions
resolutions     = [972, 648, 373, 338, 324, 288]  # image horizontal resolutions
qualityN        = 70

if not os.path.exists("logs"):
        os.makedirs("logs")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)-5.5s]  %(message)s",
    handlers=[
        logging.FileHandler(
            "logs/" + f"{datetime.now().strftime('%d-%b-%Y %H_%M_%S')}.log"),
        logging.StreamHandler(sys.stdout)
    ]
)


def convert(file) -> None:

    # Function converts all pictures in dirrectory into webp's and jpg's
    # Originals are deleting. Files are affected recursevile, file structure preserved

    #JPEG and WeBP are separated due to absence of alpha channel in JPEG

    image = Image.open(file)
    image = image.convert("RGBA")

    filename, extension = os.path.splitext(file)

    if str(extension) == ".webp":
        white_mask = Image.new('RGB', image.size, (255, 255, 255))
        Image.Image.paste(white_mask, image, (0, 0))
        
        white_mask.save(filename + ".jpg", "jpeg", optimize = True, quality = 100)
        return

    if str(extension) == ".jpg":
        image.save(filename + ".webp", "webp", optimize = True, quality = 100)
        return

    image.save(filename + ".webp", "webp", optimize = True, quality = 100)

    white_mask = Image.new('RGB', image.size, (255, 255, 255))
    Image.Image.paste(white_mask, image, (0, 0))

    white_mask.save(filename + ".jpg", "jpeg", optimize = True, quality = 100)

    os.remove(file)
            

def replace_white_with_transparent(file) -> None:
    
    # Function replaces white color with alpha channel for webp files

    _, extension = os.path.splitext(file)

    if not extension.lower()==".webp":
        return 
    
    img = Image.open(file).convert("RGBA")
    
    array = np.array(img, dtype=np.ubyte)
    mask = (array[:,:,:3] == (255, 255, 255)).all(axis=2)
    alpha = np.where(mask, 0, 255)
    array[:,:,-1] = alpha
    
    img = Image.fromarray(np.ubyte(array))
    img.save(file, "WebP", quality=100)
    

def resize(file) -> None:

    # Function resizes images to predifined picture heights for css @media at-rules for different screen sizes
    # Also compression is done on this step

    with Image.open(file) as image:
        width, height = image.size
        
        imageALPHA = image.convert("RGBA")
        image = image.convert("RGB")

        filename, _ = os.path.splitext(file)
        
        for res in resolutions:
            
            res_name = str(resolutionsBase[resolutions.index(res)])

            if (width > res or height > height * res / width):
                
                cover = resizeimage.resize_cover(image, [res, height * res / width], validate=False)
                coverALPHA = resizeimage.resize_cover(imageALPHA, [res, height * res / width], validate=False)
                
                cover.save(filename + res_name + ".jpg", "jpeg", optimize=False, quality=qualityN)
                coverALPHA.save(filename  + res_name + ".webp", "WebP", quality=qualityN)
                
            else:
                
                cover = resizeimage.resize_cover(image, [width, height], validate=False)
                coverALPHA = resizeimage.resize_cover(imageALPHA, [width, height], validate=False)

                cover.save(filename + res_name + ".jpg", "jpeg", optimize=False, quality=qualityN)
                coverALPHA.save(filename + res_name + ".webp", "WebP", quality=qualityN)
            

def compress(file) -> None:

    # Function for image compression

    image = Image.open(file)
    image.save(file, optimize = True, quality = qualityN)


def main(self) -> None:

    parser = argparse.ArgumentParser(usage="%(prog)s [options]", description="This is a tool to convert, \
                                     remove alpha chanel, resize and compress images for the website")
    
    parser.add_argument(
        "dest_dir", metavar='/path/to/your.dir', type=str,
        help="input path to folder with images"
    )
    
    parser.add_argument(
        "--do_not_resize",
        action=argparse.BooleanOptionalAction,
        help="skip resizing for files in folder"
    )

    args = parser.parse_args()
    dest_dir = args.dest_dir
    donotresize = args.do_not_resize
    

    number_of_files = 0
    list_of_files = []
    file_counter = 1

    for root, dirs, files in os.walk(dest_dir):
        for file in files:
            list_of_files.append(os.path.join(root, file))

    number_of_files = len(list_of_files)
    logging.info("Total files found: " + str(number_of_files))

    for file in list_of_files:
        
        logging.info("File: " + file + ". " + str(file_counter) + " out of " + str(number_of_files))
        file_counter += 1

        logging.info("Converting...")
        convert(file)

        logging.info("Resizing...")
        if not donotresize:
            resize(file)

        logging.info("Removing white bg...")
        replace_white_with_transparent(file)

        logging.info("Compressing...")
        compress(file)


if __name__ == '__main__':
    main(sys.argv)