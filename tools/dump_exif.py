from exif import Image
from datetime import datetime


def dump_exif(image):
    with open(image, 'rb') as image_file:
        img = Image(image_file)
        for data in img.list_all():
            print(f'{data}: {img.get(data)}')


#dump_exif('photo_0683.jpg')
dump_exif('Photo1.jpg')