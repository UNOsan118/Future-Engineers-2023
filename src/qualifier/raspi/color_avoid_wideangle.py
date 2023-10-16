# Color detection and control amount calculation and control 
# For open 2023
import serial
import time
import color_tracking_remake
import cv2
import os
import numpy as np

ser = serial.Serial("/dev/ttyAMA1", 115200)
throttle = 50

data_dir = "/home/pi/WRO2022/data"
save_dir = os.path.join(data_dir, "train")
SAVE_FPS = 0.5

steer = 0
WIDTH = 160 * 2
HEIGHT = 120 * 2

cap = cv2.VideoCapture(0)
assert cap.isOpened(), "Camera not recognized!"
cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, WIDTH)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, HEIGHT)
values = ""
ser.reset_input_buffer()

green = 0
red = 0
count = 0
_id = 0

mode = "get_img"
frame_rate = 10
size = (640, 480)
fmt = cv2.VideoWriter_fourcc("m", "p", "4", "v")
os.makedirs("../../results/", exist_ok=True)
frame_writer = cv2.VideoWriter(
    "../../results/frame.mp4", fmt, frame_rate, size)

start = time.perf_counter()
rotation_mode = ""
sign_flag = 0
over_sign = 0

while True:
    end = time.perf_counter()
    elapsed_time = end - start
    blob_red, blob_green = {}, {}
    area_red, area_green = 0, 0
    ok_blue, ok_orange = False, False
    blue_center_y, orange_center_y = 0, 0
    red, green = 0, 0
    sign_flag = 0
    wall_right, wall_left = False, False
    black_right_ratio, black_left_ratio = 0, 0
    (
        frame,
        cut_frame,
        mask_red,
        mask_green,
        blob_red,
        blob_green,
        blue_center_x,
        orange_center_x,
        blue_center_y,
        orange_center_y,
        ok_blue,
        ok_orange,
        black_right_ratio,
        black_left_ratio
    ) = color_tracking_remake.detect_sign_area(cap)

    area_red = blob_red["area"]
    area_green = blob_green["area"]

    center_red = blob_red["center"]
    center_green = blob_green["center"]

    height, width, channels = frame.shape[:3]

    center_red_x = center_red[0]
    center_green_x = center_green[0]

    center_red_y = center_red[1] / height
    center_green_y = center_green[1] / height

    red_ratio = area_red / (width * height)
    green_ratio = area_green / (width * height)

    if mode == "get_img" and elapsed_time > 1 / SAVE_FPS:
        id_path = "{:06}.jpg".format(_id)
        frame_path = os.path.join(save_dir, id_path)
        cv2.imwrite(frame_path, cut_frame)
        _id += 1
        elapsed_time = 0

    # Determining the direction of laps
    if rotation_mode == "":
        if ok_blue and ok_orange:
            if orange_center_y > blue_center_y:
                rotation_mode = "orange"
            else:
                rotation_mode = "blue"
        elif ok_blue:
            rotation_mode = "blue"
        elif ok_orange:
            rotation_mode = "orange"
        else:
            rotation_mode = ""

    steer = 0
    max_area = 0.4
    speed = 50
    rmode = 0
    force_sign = -1

    # Identify where the wall is by the size of the black ratio
    if black_right_ratio > 0.65 and black_left_ratio > 0.65:
        wall_right = True
        wall_left = True
    elif black_right_ratio > 0.3 or black_left_ratio > 0.3:
        if black_right_ratio > black_left_ratio:
            wall_right = True
        else:
            wall_left = True

    # Runs slightly outside
    if rotation_mode == "blue":
        if black_right_ratio > 0.7:
            sign_flag = 4
            steer = -50
            speed = 40
        elif black_left_ratio > 0.4:
            sign_flag = 4
            steer = 50
            speed = 40
        elif black_left_ratio > 0.15:
            sign_flag = 4
            steer = 20
        elif black_right_ratio > 0.5:
            sign_flag = 4
            steer = -20

    elif rotation_mode == "orange":
        if black_left_ratio > 0.7:
            sign_flag = 4
            steer = 50
            speed = 40
        elif black_right_ratio > 0.4:
            sign_flag = 4
            steer = -50
            speed = 40
        elif black_right_ratio > 0.15:
            sign_flag = 4
            steer = -20
        elif black_left_ratio > 0.5:
            sign_flag = 4
            steer = 20

    else:
        if wall_right:     # The right wall is close.
            sign_flag = 4
            steer = -50
            speed = 40

        elif wall_left:    # The left wall is close.
            sign_flag = 4
            steer = 70
            speed = 40

    if ok_blue and rotation_mode == "blue": # Recognize the blue line
        rmode = 1
    elif ok_orange and rotation_mode == "orange": # Recognize the orange line
        rmode = 2

    steer = steer * 0.8
    if abs(steer) < 1 and steer != 0:
        if steer > 0:
            steer = 1
        else:
            steer = -1

    steer_int = int(steer)
    if steer_int > 120:
        steer_int = 120
    elif steer_int < -120:
        steer_int = -120

    if force_sign != -1:
        sign_flag = force_sign

    # 線をまたいでいる標識が何色かを判定
    over_sign = 0
    if black_left_ratio >= 0.1 or black_right_ratio >= 0.1:  # Whether the wall is close or not
        if black_left_ratio > black_right_ratio:
            over_sign = over_sign + 10 # The left wall is close.
        else:
            over_sign = over_sign + 20 # The right wall is close.
    else:
        pass

    """
    Explanation of over_sign value determination
    Distance to the wall:The tenth place is...  0: No wall nearby 1: Wall is on the left side 2: Wall is on the right side
    """

    # print("r_ratio", red_ratio)
    # print("g_ratio: ", green_ratio)
    # print("c_r_x", center_red_x / width)
    # print("c_g_x", center_green_x / width)
    # print("c_r_y", center_red_y)
    # print("c_g_y", center_green_y)
    # print("b_c_y", blue_center_y)
    # print("o_c_y", orange_center_y)
    # print("s_flag", sign_flag)
    # print("o_sign", over_sign)
    # print("r_mode", rotation_mode)
    # print("wall_left", wall_left)
    # print("wall_right", wall_right)
    # print("black_left_ratio", black_left_ratio)
    # print("black_right_ratio", black_right_ratio)
    # print("steer", steer)
    # print("rmode", rmode)
    # time.sleep(0.3)

    # Serial communication (transmission) processing
    cmd = "{:4d},{:3d},{},{},{:3d}@".format(steer_int, speed, sign_flag, rmode, over_sign)
    ser.write(cmd.encode("utf-8"))

    for i in range(1):  # Process of skipping readings (because they may be delayed and take old values)
        img = cap.read()

    end = time.perf_counter()
    elapsed_time = end - start

cv2.destroyAllWindows()
frame_writer.release()
ser.write("end@".encode())
