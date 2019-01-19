import os
import sys
import cv2
import numpy as np

from PIL import Image

IMG_DIR = f'{os.path.dirname(os.path.abspath(__file__))}/../img'
RESULT_DIR = f'{os.path.dirname(os.path.abspath(__file__))}/../result'
IMG = ''
RESIZE_THRESH = 1280

def write_out(img, name):
    cv2.imwrite(f'{RESULT_DIR}/{name}.png', img)

def crop(mask, target):
    cropped = cv2.merge((mask, mask, mask))
    cropped[mask == 255] = target[mask == 255]
    alpha = np.ones_like(cropped) * 255
    cropped = cv2.merge((cropped, alpha[:, :, 1]))

    cropped[mask == 0] = (0, 0, 0, 0)

    (x, y) = np.where(mask == 255)
    (topx, topy) = (np.min(x), np.min(y))
    (bottomx, bottomy) = (np.max(x), np.max(y))

    return topx, topy, cropped[topx:bottomx+1, topy:bottomy+1]

def light_up(target, gamma=1.18):
    look_up_table = np.zeros((256, 1), dtype=np.uint8)

    for i in range(256):
        look_up_table[i] =  255 * pow(float(i) / 255, 1.0 / gamma)

    return cv2.LUT(target, look_up_table)

try:
    IMG = sys.argv[1]
except Exception as e:
    IMG = 'note01.jpg'

counter = 0
while(True):
    print(f'starting loop: {counter}')
    image = cv2.imread(f'{IMG_DIR}/{IMG}')

    h = image.shape[1]
    if h > RESIZE_THRESH or h < RESIZE_THRESH:
        print(f'height: {h}, too big, resize')
        persentage = RESIZE_THRESH / h
        image = cv2.resize(image, dsize=None, fx=persentage, fy=persentage)

    image_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    ret, thed = cv2.threshold(image_gray, 0, 255, cv2.THRESH_OTSU)

    write_out(thed, f'thed')

    kernel = np.ones((8, 8), np.uint8)
    morphed = cv2.morphologyEx(thed, cv2.MORPH_CLOSE, kernel)

    # write_out(morphed, 'morphedA')

    kernel = np.ones((8, 8), np.uint8)
    morphed = cv2.morphologyEx(morphed, cv2.MORPH_OPEN, kernel)

    # write_out(morphed, 'morphedB')

    inv_morphed = cv2.bitwise_not(morphed)

    # write_out(inv_morphed, 'inv_morphedA')

    conts_im, conts, hierarchy = cv2.findContours(inv_morphed, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)

    # draw contours in thesholded image
    colored = cv2.merge((morphed, morphed, morphed))
    for index in range(len(conts)):
        cv2.drawContours(colored, conts, index, (255, 0, 255), 3)

    # write_out(colored, 'colored')

    mask = np.zeros_like(image_gray)
    stopper = 0
    for index in range(len(conts)):
        if (cv2.contourArea(conts[index]) > 12000): # TODO: change to scheme
            cv2.drawContours(mask, conts, index, 255, -1)
            stopper+=1

    if stopper == 0:
        print("there aren't shade to remove. exit.")
        break;

    # write_out(mask, 'shade_mask')
    x, y, shade_cropped = crop(mask, image)
    write_out(shade_cropped, 'shade_cropped')
    lighted_up_shade = light_up(shade_cropped)
    write_out(lighted_up_shade, 'lighted_up_shade')

    back = Image.fromarray(image[:,:,::-1])
    lighted_up_shade = cv2.cvtColor(lighted_up_shade, cv2.COLOR_BGRA2RGBA)
    target = Image.fromarray(lighted_up_shade)

    back.paste(target, (y, x), target)

    # back = back.convert('RGB')
    back.save(f'{RESULT_DIR}/complete.png')
    back.save(f'{IMG_DIR}/complete.png')

    complete = cv2.imread(f'{RESULT_DIR}/complete.png', 0)
    _, th_complete = cv2.threshold(complete, 0, 255, cv2.THRESH_OTSU)

    write_out(th_complete, 'thed_completed')

    IMG = 'complete.png' # gonna loop baby
    counter+=1

    # if counter == 1:
    #     break
