from picamzero import Camera
from exif import Image
from datetime import datetime
from astro_pi_orbit import ISS

def get_time(image):
    with open(image, 'rb') as image_file:
        img = Image(image_file)
        time_str = img.get('datetime_original')
        time = datetime.strptime(time_str, '%Y:%m:%d %H:%M:%S')
        return time

def dump_EXIF(image):
    with open(image, 'rb') as image_file:
        img = Image(image_file)
        for data in img.list_all():
            print(f'{data}: {img.get(data)}')

image_file_name = 'Photo1.jpg'

"""
cam.start_preview()
cam.take_photo(image_file_name) #save the image to your desktop
cam.stop_preview()
"""
'''
iss = ISS()
point = iss.coordinates()
coordinates = (point.latitude.signed_dms(), point.longitude.signed_dms())
'''

'''
cam = Camera()
cam.take_photo(image_file_name, gps_coordinates=coordinates)
'''
#print(f'Picture with the name {image_file_name} is taken at {get_time(image_file_name)}')
print(dump_EXIF(image_file_name))

estimate_kmps = 7.1234567890
estimate_kmps_formatted= f'{estimate_kmps:.4f}'
file_path = 'result.txt'
with open(file_path, 'w') as file:
    file.write(estimate_kmps_formatted)
    
    print('Data written to', file_path)