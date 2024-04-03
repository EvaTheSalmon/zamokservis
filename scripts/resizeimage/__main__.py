import os.path
import sys
import argparse
import resizeimage
import logging
import datetime

from PIL import Image

resolutionsBase = [1080, 720, 414, 375, 360, 320] # display horizontal resolutions
resolutions     = [972, 648, 373, 338, 324, 288]  # image horizontal resolutions

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)-5.5s]  %(message)s",
    handlers=[
        logging.FileHandler(
            "logs/" + f"{datetime.now().strftime('%d-%b-%Y %H_%M_%S')}.log"),
        logging.StreamHandler(sys.stdout)
    ]
)

async def main(self) -> None:

    parser = argparse.ArgumentParser(usage="%(prog)s [options]", description="This is a tool to convert, \
                                     remove alpha chanel, resize and compress images for the website")
    
    parser.add_argument(
        "dest_dir", metavar='/path/to/your.dir', type=str,
        help="input path to folder with images"
    )
    
    parser.add_argument(
        "donotresize",
        metavar="do-not-resize",
        action=argparse.BooleanOptionalAction
    )

    args = parser.parse_args()
    dest_dir = args.dest_dir
    donotresize = args.donotresize
    
    convert_to_png(dest_dir)
    replace_white_with_transparent(dest_dir)
    resize(dest_dir, donotresize)
    compress(dest_dir)


if __name__ == '__main__':
    main(sys.argv)


def convert_to_png(dest_dir) -> None:
    for files in os.walk(dest_dir):
        
        number_of_files = len(next(files)[2])
        i = 1        
        
        for file in files:
            
            logging.info("Processing conversion, current: {file}, {i} out of {number_of_files} files")
            
            try:
                image = Image.open(file)
                image = image.convert("RGBA")

                filename, fileextension = os.path.splitext(file)
                
                image.save(filename + ".webp", "webp", optimize = True, quality = 10) # main file to display
                image.save(filename + ".webp", "webp", optimize = True, quality = 10) # fallback file to display
            except:
                logging.warn(f'Error while saving file {file} as webp, skipping')
                break
            os.remove(file)
            i+=1
                

def replace_white_with_transparent(dest_dir) -> None:
    for files in os.walk(dest_dir):
        
        number_of_files = len(next(files)[2])
        i = 1
        
        for file in files:
            
            logging.info("Processing removing bg, current: {file}, {i} out of {number_of_files} files")
            
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
                logging.warn(f"Couldn't save file {file} when removing white background")
            i+=1


def resize(dest_dir, donotresize) -> None:
    for files in os.walk(dest_dir):
        
        number_of_files = len(next(files)[2])
        j = 1
        
        for file in files:
            
            logging.info("Processing resizing, current: {file}, {i} out of {number_of_files} files")
            
            with Image.open(file) as image:
                width, height = image.size
                
                filename, fileextension = os.path.splitext(file)
                i = 0
                
                while i < len(resolutions):
                    if (width > resolutions[i] or height > height * resolutions[i] / width) and not donotresize:
                        cover = resizeimage.resize_cover(image, [resolutions[i], height * resolutions[i] / width],
                                                            validate=False)
                        
                        try:
                            # save as jpg
                            cover.save(filename + ".jpg", image.format, optimize=False, quality=100)
                            
                            # save as WebP
                            cover.save(filename + ".webp", "WebP", quality=100)
                        except:
                            logging.warn(f'Error while saving file after resize {file}')
                            break
                        
                    elif donotresize:
                        cover = resizeimage.resize_cover(image, [width, height], validate=False)
                        
                        try:
                            # save as WebP
                            cover.save(filename + ".webp", "WebP", quality=100)
                        except:
                            logging.warn(f'Error while saving file after resize {file} as webp')
                            break
                        
                    else:
                        cover = resizeimage.resize_cover(image, [width, height], validate=False)
                        try:
                            # save as jpg
                            cover.save(filename + ".jpg", image.format, optimize=False, quality=100)
                            
                            # save as WebP
                            cover.save(filename + ".webp", "WebP", quality=100)
                        except:
                            logging.warn(f'Error while saving file after resize {file}')
                            break
            j+=1
                        
def compress(dest_dir) -> None:
    for files in os.walk(dest_dir):
        
        number_of_files = len(next(files)[2])
        i = 0
        
        for file in files:
            
            logging.info("Processing compression, current: {file}, {i} out of {number_of_files} files")
            
            try:
                image = Image.open(file)
                image = image.convert("RGBA")

                image.save(file, optimize = True, quality = 70) # fallback file to display
            except:
                logging.warn(f'Error while saving file {file} as webp, skipping')
                break
            os.remove(file)
            i+=1