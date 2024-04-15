import os.path
import sys
import argparse
import logging

from resizeimage import resizeimage
from datetime import datetime
from PIL import Image

resolutionsBase = [1080, 720, 414, 375, 360, 320] # display horizontal resolutions
resolutions     = [972, 648, 373, 338, 324, 288]  # image horizontal resolutions

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


def convert_to_jpg(dest_dir) -> None:
    for root, dirs, files in os.walk(dest_dir):
        
        number_of_files = len(next(os.walk(dest_dir))[2])
        i = 1        
        
        for file in files:


            file = root + str(os.sep) + file

            logging.info("Processing conversion, current: " + file + ", " + str(i) + " out of " + str(number_of_files) + " files")
            
            try:
                image = Image.open(file)
                image = image.convert("RGBA")

                filename, extension = os.path.splitext(file)                
                
                if str(extension) == ".webp":
                    image.save(filename + ".jpg", "jpeg", optimize = True, quality = 10) # main file to display
                    break

                if str(extension) == ".jpg":
                    image.save(filename + ".webp", "webp", optimize = True, quality = 10) # fallback file to display
                    break

                image.save(filename + ".jpg", "jpeg", optimize = True, quality = 10)
                image.save(filename + ".webp", "webp", optimize = True, quality = 10)
                
            except:
                logging.warning("Error while saving file " + file + " as webp, skipping")
                break
            os.remove(file)
            i+=1
                

def replace_white_with_transparent(dest_dir) -> None:
    for root, dirs, files in os.walk(dest_dir):

        number_of_files = len(next(os.walk(dest_dir))[2])
        i = 1
        
        for file in files:

            filename, fileextension = os.path.splitext(file)
            if str(fileextension).lower() != ".wepb":
                break

            file = root + str(os.sep) + file

            logging.info("Processing removing bg, current: " + file + ", " + str(i) + " out of " + str(number_of_files) + " files")
            
            img = Image.open(file)
            img = img.convert("RGBA")
            
            pixdata = img.load()
            
            width, height = img.size
            for y in range(height):
                for x in range(width):
                    if pixdata[x, y] == (255, 255, 255, 255):
                        pixdata[x, y] = (255, 255, 255, 0)
            try:
                img.save(file)
            except:
                logging.warning("Couldn't save file " + file + " when removing white background")
            i+=1


def resize(dest_dir, donotresize) -> None:
    for root, dirs, files in os.walk(dest_dir):
        
        number_of_files = len(next(os.walk(dest_dir))[2])
        i = 1
        
        for file in files:
            
            file = root + str(os.sep) + file

            logging.info("Processing resizing, current: " + file + ", " + str(i) + " out of " + str(number_of_files) + " files")
            
            with Image.open(file) as image:
                width, height = image.size
                
                imageALPHA = image.convert("RGBA")
                image = image.convert("RGB")

                filename, fileextension = os.path.splitext(file)
                j = 0
                
                while j < len(resolutions):
                    
                    if (width > resolutions[j] or height > height * resolutions[j] / width) and not donotresize:
                        cover = resizeimage.resize_cover(image, [resolutions[j], height * resolutions[j] / width],
                                                            validate=False)
                        
                        coverALPHA = resizeimage.resize_cover(imageALPHA, [resolutions[j], height * resolutions[j] / width],
                                                            validate=False)
                        
                        try:
                            # save as jpg
                            cover.save(filename + ".jpg", "jpeg", optimize=False, quality=100)
                            
                            # save as WebP
                            coverALPHA.save(filename + ".webp", "WebP", quality=100)

                        except Exception as error:
                            logging.warning("Error while saving file after resize " + file + ". ", error)
                            break
                        
                    elif donotresize:
                        coverALPHA = resizeimage.resize_cover(imageALPHA, [width, height], validate=False)
                        
                        try:
                            # save as WebP
                            coverALPHA.save(filename + ".webp", "WebP", quality=100)
                        except Exception as error:
                            logging.warning("Error while saving file after resize " + file + " as webp" + ". ", error)
                            break
                        
                    else:
                        
                        cover = resizeimage.resize_cover(image, [width, height], validate=False)
                        coverALPHA = resizeimage.resize_cover(imageALPHA, [width, height], validate=False)

                        try:
                            # save as jpg
                            cover.save(filename + ".jpg", "jpeg", optimize=False, quality=100)
                            
                            # save as WebP
                            coverALPHA.save(filename + ".webp", "WebP", quality=100)
                        except Exception as error:
                            logging.warning("Error while saving file after resize " + file + ". ", error)
                            break
                    j+=1
                        
def compress(dest_dir) -> None:
    for root, dirs, files in os.walk(dest_dir):
        
        number_of_files = len(next(os.walk(dest_dir))[2])
        i = 0
        
        for file in files:
            
            file = root + str(os.sep) + file

            logging.info("Processing compression, current: " + file + ", " + str(i) + " out of " + str(number_of_files) + " files")
            
            try:
                image = Image.open(file)
                image = image.convert("RGBA")

                image.save(file, optimize = True, quality = 70) # fallback file to display
            except:
                logging.warning("Error while saving file " + file + " as webp, skipping")
                break            
            i+=1


def main(self) -> None:

    parser = argparse.ArgumentParser(usage="%(prog)s [options]", description="This is a tool to convert, \
                                     remove alpha chanel, resize and compress images for the website")
    
    parser.add_argument(
        "dest_dir", metavar='/path/to/your.dir', type=str,
        help="input path to folder with images"
    )
    
    parser.add_argument(
        "donotresize",
        metavar="do-not-resize",
        action=argparse.BooleanOptionalAction,
        help="skip resizing for files in folder"
    )

    args = parser.parse_args()
    dest_dir = args.dest_dir
    donotresize = args.donotresize
    
    convert_to_jpg(dest_dir)
    replace_white_with_transparent(dest_dir)
    resize(dest_dir, donotresize)
    compress(dest_dir)


if __name__ == '__main__':
    main(sys.argv)