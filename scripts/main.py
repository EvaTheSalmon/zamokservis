import os
import os.path
import sys

from PIL import Image
from resizeimage import resizeimage

resolutionsBase = [1080, 720, 414, 375, 360, 320]
resolutions = [972, 648, 373, 338, 324, 288]
qualityN = 75


# parser = argparse.ArgumentParser()
# parser.add_argument("-r", "--rewrite", dest="rewrite", help="Rewrite files that already exist", default='0', type=bool)
# args = parser.parse_args()
# print("Rewrite {}".format(args.rewrite))


def compress(numb, image, filename, width, height, path_string, donotresize):
    if (width > resolutions[numb] or height > height * resolutions[numb] / width) and int(donotresize) != 1:
        cover = resizeimage.resize_cover(image, [resolutions[numb], height * resolutions[numb] / width],
                                            validate=False)
        # save as jpg
        cover.save(path_string + str(resolutionsBase[numb]) + "\\" + filename, image.format, optimize=True,
                    quality=qualityN)
        # save as WebP
        cover.save(path_string + str(resolutionsBase[numb]) + "\\" + filename[:-4] + ".webp", "WebP",
                    quality=qualityN)
    elif int(donotresize) == 1:
        cover = resizeimage.resize_cover(image, [width, height], validate=False)
        # save as WebP
        cover.save(path_string + "\\" + filename[:-4] + ".webp", "WebP", quality=qualityN)
    else:
        cover = resizeimage.resize_cover(image, [width, height], validate=False)
        # save as jpg
        cover.save(path_string + str(resolutionsBase[numb]) + "\\" + filename, image.format, optimize=True,
                    quality=qualityN)
        # save as WebP
        cover.save(path_string + str(resolutionsBase[numb]) + "\\" + filename[:-4] + ".webp", "WebP",
                    quality=qualityN)


def convert(path_string, donotresize):
    onlyfiles = next(os.walk(path_string))[2]  # dir is your directory path as string
    l = len(onlyfiles)
    i = 0
    for filename in os.listdir(path_string):
        with open(os.path.join(path_string, filename), "r+b") as f:
            with Image.open(f) as image:
                width, height = image.size
                j = 0
                while j < len(resolutions):
                    compress(j, image, filename, width, height, path_string, int(donotresize))
                    j += 1
                i += 1
                sys.stdout.write("\rDone %i images out of " % i + str(l))
                sys.stdout.flush()


convert("C:\\Users\\Oleg\\git\\zamokservis\\static\\img\\src", 0)
convert("C:\\Users\\Oleg\\git\\zamokservis\\static\\img\\car_brands", 1)
convert("C:\\Users\\Oleg\\git\\zamokservis\\static\\img\\door_brands", 1)
convert("C:\\Users\\Oleg\\git\\zamokservis\\static\\img\\key_brands", 1)
