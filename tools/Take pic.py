from picamzero import Camera
from time import sleep
import os

cam = Camera()
sleep_interval = 1

#cam.capture_sequence('sequence.jpg', num_images=2, interval=5)
image1 = 'new_image.jpg'
image2 = 'new_image1.jpg'
print(f'taking image {image1}')
cam.take_photo(image1)
print(f'Wait {sleep_interval} sec')
sleep(sleep_interval)
print(f'taking image {image2}')
cam.take_photo(image2)
