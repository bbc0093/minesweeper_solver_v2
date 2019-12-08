import pyautogui as gui
import numpy as np
import imutils
import cv2
import sys


def imagesearch_screen(image, scale, precision=0.8):
    im = gui.screenshot()

    img_rgb = np.array(im)
    img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)
    template = cv2.imread(image, 0)
    resized = imutils.resize(template, width = int(template.shape[1] * scale))

    res = cv2.matchTemplate(img_gray, resized, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    print(min_val, max_val)
    if max_val < precision:
        return [-1, -1]
    return max_loc

def imagesearch(image, parent_grey, scale, precision=0.8):
    template = cv2.imread(image, cv2.IMREAD_GRAYSCALE)
    resized = imutils.resize(template, width = int(template.shape[1] * scale))

    res = cv2.matchTemplate(parent_grey, resized, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    if max_val < precision:
        return [-1, -1]
    return max_loc


def imagesearch_all(image, parent_grey, scale, precision=0.8):
    template = cv2.imread(image, cv2.IMREAD_GRAYSCALE)
    resized = imutils.resize(template, width = int(template.shape[1] * scale))

    res = cv2.matchTemplate(parent_grey, resized, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    match_locations = np.where(res >= precision)

    return match_locations

def find_scale(image, precision=0.85, num_runs = 100, start_val = .1, end_val = 5):
        im = gui.screenshot()
    
        img_rgb = np.array(im)
        img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)
        (iH, iW) = img_gray.shape[:2]
        template = cv2.imread(image, 0)
        max = 0
    
        for run, scale in enumerate(np.linspace(start_val, end_val, num_runs)):
            sys.stdout.write("\rAnalizing " + str(run+1) + " of " + str(num_runs))
            resized = imutils.resize(template, width = int(template.shape[1] * scale))
            (tH, tW) = resized.shape[::-1]
    
            if(tH > iH or tW > iW):
                print(tH, iH, tW, iW)
                break
    
            res = cv2.matchTemplate(img_gray, resized, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, __, loc = cv2.minMaxLoc(res)
            print()
            print(scale, max_val)
           
            if max_val > precision:
                if(max_val > max):        # it is possible to have multiple scale meet criteria
                    max = max_val         # if they do choose the best 
                    max_scale = scale
                    max_loc = loc
                    max_H = tH
                    max_W = tW
    
            else:
                if(max):
                    sys.stdout.write("\n")
                    return max_scale, max_loc[0], max_loc[1], max_H, max_W
                
        sys.stdout.write("\n")
        return None