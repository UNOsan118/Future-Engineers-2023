import numpy as np
import cv2
import os


def load_img(img=None, path=""):
    assert not (img is None and path == ""), "画像か画像のパスを指定してください"
    if path != "":
        img = cv2.imread(path)

    return img  # (height, width, channel)

def plot_grid(img, interval=50):
    img_width = img.shape[1]
    grid = np.arrange(start=0, stop=img_width, step=interval)



def crop_roi(img, x, y, w, h):
    img_shape = img.shape[:2]
    assert x < img_shape[1], "Coordinate of window is out of range, please check coordinate: x,y"
    assert y < img_shape[0], "Coordinate of window is out of range, please check coordinate: x,y"
    assert x + w < img_shape[1], "Coordinate of window is out of range, please check box with, height: w,h"
    assert y + h < img_shape[0], "Coordinate of window is out of range, please check box with, height: w,h"

    # crop roi based on (x1,y1),(x2,y2)
    x1, y1 = x, y
    x2, y2 = x1 + w, y1 + h
    img_roi = img[y1:y2, x1:x2]

    # plot roi in the image
    cv2.rectangle(img, pt1=(x1, y1), pt2=(x2, y2), color=(0, 0, 255))
    cv2.imshow("cropping area", img)
    cv2.imshow("roi", img_roi)

    if cv2.waitKey() == ord("q"):
        cv2.destroyAllWindows()
        return img_roi


def calculate_statistic(img_roi, color_space="hsv"):

    num_params = 2  # mean and std
    if color_space == "hsv":
        img_roi = cv2.cvtColor(img_roi, cv2.COLOR_BGR2HSV)

    num_ch = img_roi.shape[2]
    stat_roi = np.empty(shape=(num_ch, num_params), dtype=np.float64)

    for ch in range(num_ch):
        mean = np.mean(img_roi[:, :, ch])
        std = np.std(img_roi[:, :, ch])
        stat_roi[ch, 0] = mean
        stat_roi[ch, 1] = std

    return stat_roi

def get_range(stat_roi):
    num_params = stat_roi.shape[1]
    num_ch = stat_roi.shape[0]
    stat_roi_range = np.empty(shape=stat_roi.shape, dtype=np.uint8)

    for ch in range(num_ch):
        mean = stat_roi[ch, 0]
        std = stat_roi[ch, 1]
        stat_roi_range[ch, 0] = mean - std
        stat_roi_range[ch, 1] = mean + std

    return stat_roi_range


img = load_img(path="/home/pi/Desktop/000000.jpg")
img_roi = crop_roi(img, 102, 140, 20, 40)
stat_roi = calculate_statistic(img_roi)
stat_roi_range = get_range(stat_roi)

print("stat_roi:\n{}\n".format(stat_roi))
print("stat_roi_range: \n{}".format(stat_roi_range))

