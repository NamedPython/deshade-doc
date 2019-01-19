import os, sys
import cv2
import numpy as np
import subprocess as sp

IMG_DIR = f'{os.path.dirname(os.path.abspath(__file__))}/../img'
RESULT_DIR = f'{os.path.dirname(os.path.abspath(__file__))}/../result'
SRC_DIR = f'{os.path.dirname(os.path.abspath(__file__))}/../src'
SCANNER_PREFIX = 'scanner_'
THED_COMPLETED = 'thed_completed.png'
RESIZE_THRESH = 1500
IMG = ''

def write_out(img, name):
    cv2.imwrite(f'{RESULT_DIR}/{name}.png', img)

def norm_size(im):
    h = im.shape[1]
    if h > RESIZE_THRESH or h < RESIZE_THRESH:
        persentage = RESIZE_THRESH / h
        im = cv2.resize(im, dsize=None, fx=persentage, fy=persentage)
    print(f'size: {im.shape}')

    return im

try:
    IMG = sys.argv[1]
except Exception as e:
    IMG = 'note01.jpg'

scanned = cv2.imread(f'{IMG_DIR}/{SCANNER_PREFIX}{IMG}', cv2.IMREAD_GRAYSCALE)
base = cv2.imread(f'{IMG_DIR}/{IMG}', cv2.IMREAD_GRAYSCALE)

# execute deshade-doc
print('deshade-doc by subprocess executed....')
deshade_doc = sp.run(['python', f'{SRC_DIR}/source.py', IMG])

if deshade_doc.returncode is not 0:
    print('OMG!! deshade-doc does not work correctly, check the argument and way to run.')
    exit()
else:
    print('Yay!! deshade-doc completed, gonna evaluate that :D')

# it's already deshaded and thresholded ;D
deshaded = cv2.imread(f'{RESULT_DIR}/{THED_COMPLETED}', cv2.IMREAD_GRAYSCALE)

# make them thresholded
_, scanned = cv2.threshold(scanned, 0, 255, cv2.THRESH_OTSU)
_, base = cv2.threshold(base, 0, 255, cv2.THRESH_OTSU)

write_out(scanned, 'thed_scanned')
write_out(base, 'thed_base')

# make them sizes nearly

scanned = norm_size(scanned)
base = norm_size(base)
deshaded = norm_size(deshaded)

# see here about compare with matching:
# http://labs.eecs.tottori-u.ac.jp/sd/Member/oyamada/OpenCV/html/py_tutorials/py_feature2d/py_matcher/py_matcher.html

bf = cv2.BFMatcher(cv2.NORM_HAMMING)
detector = cv2.AKAZE_create()

(scanned_kp, scanned_des) = detector.detectAndCompute(scanned, None)

print('result:')

for name, target in {'base': base, 'deshaded': deshaded}.items():
    try:
        (target_kp, target_des) = detector.detectAndCompute(target, None)
        matches = bf.knnMatch(scanned_des, target_des, k=2)
        good = []
        ndists = []
        for m, n in matches:
            if m.distance < 0.3 * n.distance:
                ndists.append(n.distance * 0.4)
                good.append(m)
        dists = [d.distance for d in good] # + ndists
        ret = sum(dists) / len(dists)

        drawed = cv2.drawMatches(scanned, scanned_kp, target, target_kp, good, None)
        write_out(drawed, f'scanned-m-{name}')
    except cv2.error:
        ret = 100000

    print(f'{name}: {ret}')


