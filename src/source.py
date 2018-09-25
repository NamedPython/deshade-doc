import os
import sys
import cv2
import numpy as np

IMG_DIR = f'{os.path.dirname(os.path.abspath(__file__))}/../img'
RESULT_DIR = f'{os.path.dirname(os.path.abspath(__file__))}/../result'
IMG = ''

try:
    IMG = sys.argv[1]
except Exception as e:
    IMG = 'note.png' 

def write_out(img, name):
    cv2.imwrite(f'{RESULT_DIR}/{name}.png', img)

image = cv2.imread(f'{IMG_DIR}/{IMG}')
image_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

ret, thed = cv2.threshold(image_gray, 0, 255, cv2.THRESH_OTSU)

write_out(thed, 'thed')

kernel = np.ones((14, 14), np.uint8)
morphed = cv2.morphologyEx(thed, cv2.MORPH_CLOSE, kernel)

write_out(morphed, 'morphedA')

kernel = np.ones((20, 20), np.uint8)
morphed = cv2.morphologyEx(morphed, cv2.MORPH_RECT, kernel)

write_out(morphed, 'morphedB')

inv_morphed = cv2.bitwise_not(morphed)

write_out(inv_morphed, 'inv_morphedA')

conts_im, conts, hierarchy = cv2.findContours(inv_morphed, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)

# draw contours in thesholded image
# size = image.shape[:3]
# colored = np.zeros(size, dtype=np.uint8)
# colored.fill(0)
# for x, row in enumerate(thed):
#     for y, cell in enumerate(row):
#         if cell != 0:
#             colored[x][y] = (255, 255, 255)

# for index in range(len(conts)):
#     print(index)
#     cv2.drawContours(conts_drawed, conts, index, 255, -1)

choosed = 0

mask = np.zeros_like(image_gray)
cv2.drawContours(mask, conts, choosed, 255, -1)

write_out(mask, 'conts_drawed')

cropped = np.zeros_like(mask)

cropped[mask == 255] = image_gray[mask == 255]

(x, y) = np.where(mask == 255)
(topx, topy) = (np.min(x), np.min(y))
(bottomx, bottomy) = (np.max(x), np.max(y))
cropped = cropped[topx:bottomx+1, topy:bottomy+1]

write_out(cropped, 'cropped')
