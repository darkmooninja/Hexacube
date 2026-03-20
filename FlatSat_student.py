"""
The Python code you will write for this module should read
acceleration data from the IMU. When a reading comes in that surpasses
an acceleration threshold (indicating a shake), your Pi should pause,
trigger the camera to take a picture, then save the image with a
descriptive filename. You may use GitHub to upload your images automatically,
but for this activity it is not required.

The provided functions are only for reference, you do not need to use them. 
You will need to complete the take_photo() function and configure the VARIABLES section
"""

#AUTHOR: 
#DATE:

#import libraries
import time
import board
import math
import numpy as np
from PIL import Image
from adafruit_lsm6ds.lsm6dsox import LSM6DSOX as LSM6DS
from adafruit_lis3mdl import LIS3MDL
from git import Repo
from picamera2 import Picamera2

#VARIABLES
THRESHOLD = 15      #Any desired value from the accelerometer
REPO_PATH = "/home/pi/Hexacube"     #Your github repo path: ex. /home/pi/FlatSatChallenge
FOLDER_PATH = "/Images"   #Your image folder path in your GitHub repo: ex. /Images
Brightness_threshold = 80
Shadow_threshold = 20
Sun_Degree = 30
PixelRatio = 0.001

#imu and camera initialization
i2c = board.I2C()
accel_gyro = LSM6DS(i2c)
mag = LIS3MDL(i2c)
picam2 = Picamera2()


def git_push():
    """
    This function is complete. Stages, commits, and pushes new images to your GitHub repo.
    """
    try:
        repo = Repo(REPO_PATH)
        origin = repo.remote('origin')
        print('added remote')
        origin.pull()
        print('pulled changes')
        repo.git.add(REPO_PATH + FOLDER_PATH)
        repo.index.commit('New Photo')
        print('made the commit')
        origin.push()
        print('pushed changes')
    except:
        print('Couldn\'t upload to git')


def img_gen(name):
    """
    This function is complete. Generates a new image name.

    Parameters:
        name (str): your name ex. MasonM
    """
    t = time.strftime("_%H%M%S")
    imgname = (f'{REPO_PATH}/{FOLDER_PATH}/{name}{t}.jpg')
    return imgname


def take_photo():
    """
    This function is NOT complete. Takes a photo when the FlatSat is shaken.
    Replace psuedocode with your own code.
    """
    while True:
        accel_x, accel_y, accel_z = accel_gyro.acceleration
        magnitude = (accel_x**2 + accel_y**2 + accel_z**2) ** 0.5
        #CHECKS IF READINGS ARE ABOVE THRESHOLD
        if magnitude > THRESHOLD:
            print("SHAKE")

            #PAUSE
            name = "Test"
            photo_name = img_gen(name)

            picam2.start()
            image = picam2.capture_image("main")
            image.save(photo_name)

            ShadowMap(image)
            
            git_push()
            print("picture done")
            picam2.stop()
            #PUSH PHOTO TO GITHUB

            
            time.sleep(1)  # debounce
            break
        
        #PAUSE
def test_take_photo():
    print("Test Mode: Click 'Space' then 'Enter' to take a photo")
    while True:
        key = input()
        if key == " ":
            print("SPACE")
            name = "Test"
            photo_name = img_gen(name)

            picam2.start()
            time.sleep(1)
            image = picam2.capture_image("main")
            image.save(photo_name)

            ShadowMap(image)
            
            git_push()
            print("picture done")
            picam2.stop()
            #PUSH PHOTO TO GITHUB

            
            time.sleep(1)  #debounce
        elif key.lower() == "q":
            print("Exiting test mode")
            break


def ShadowMap(image):
    ImgMap = np.array(image)
    if len(ImgMap.shape) == 3:
        gray = 0.299 * ImgMap[:, :, 0] + 0.587 * ImgMap[:, :, 1] + 0.114 * ImgMap[:, :, 2]
    else:
        gray = ImgMap
    
    mask = gray < Brightness_threshold

    Shadow_Width = 0

    best_row = -1
    best_start = -1
    best_end = -1

    for row_idx in range(mask.shape[0]):
        row = mask[row_idx]
        shadow_array = np.where(row)[0]

        if len(shadow_array) < Shadow_threshold:
            continue

        start = shadow_array[0]
        end = shadow_array[-1]
        width = end - start + 1

        if width > Shadow_Width:
            Shadow_Width = width
            best_row = row_idx
            best_start = start
            best_end = end        

        if width > Shadow_Width:
            Shadow_Width = width

    if Shadow_Width == 0:
        print("No clear shadow detected.")
        return
    
    Shadow_length = Shadow_Width * PixelRatio
    Depth = Shadow_length * math.tan(math.radians(Sun_Degree))

    print("Shadow width:", Shadow_Width, "pixels")
    print("Shadow length:", Shadow_length, "meters")
    print("Estimated crater depth:", Depth, "meters")

    if len(ImgMap.shape) == 2:
        display_img = np.stack([ImgMap] * 3, axis=-1)
    else:
        display_img = ImgMap.copy()

    display_img = display_img.astype(np.uint8)
    
    display_img[best_row, best_start:best_end + 1] = [255, 0, 0, 255]

    marked_name = f"{REPO_PATH}/{FOLDER_PATH}/shadow_marked.jpg"
    marked_image = Image.fromarray(display_img)
    marked_image = marked_image.convert("RGB")
    marked_image.save(marked_name)
    print("Marked image saved as:", marked_name)    



def main():
    #take_photo()           #Comment for testing with movement
    test_take_photo()       #Comment for Testing with Keyboard Input


if __name__ == '__main__':
    main()