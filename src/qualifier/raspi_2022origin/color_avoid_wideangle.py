# カラー検出及び制御量の算出と制御 # 予選用
import serial
import time
import color_tracking_QU
import cv2
import os
import numpy as np

ser = serial.Serial("/dev/ttyAMA1", 115200)
throttle = 80

data_dir = "/home/pi/WRO2022/data"
save_dir = os.path.join(data_dir, "train")
SAVE_FPS = 0.5

threshold = 10000  # 回避動作を開始する画像中の物体の面積
steer = 0
WIDTH = 160 * 2
HEIGHT = 120 * 2

cap = cv2.VideoCapture(0)
assert cap.isOpened(), "カメラを認識していません！"
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
steer = 0
sign_flag = 0

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
    ) = color_tracking_QU.detect_sign_area(cap)

    # 黒色の比の大きさでどこの壁なのかを特定
    if black_right_ratio > 0.7 and black_left_ratio > 0.7:
        wall_right = True
        wall_left = True
    elif black_right_ratio > 0.4 or black_left_ratio > 0.4:
        if black_right_ratio > black_left_ratio:
            wall_right = True
        else:
            wall_left = True

    height, width, channels = frame.shape[:3]

    if mode == "get_img" and elapsed_time > 1 / SAVE_FPS:
        id_path = "{:06}.jpg".format(_id)
        frame_path = os.path.join(save_dir, id_path)
        cv2.imwrite(frame_path, cut_frame)
        _id += 1
        elapsed_time = 0

    # 周回の向き決定
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


    if ok_blue and rotation_mode == "blue":  # 青色認識
        rmode = 1

    elif ok_orange and rotation_mode == "orange":  # 橙色認識
        rmode = 2

    #print("r_ratio", black_right_ratio)
    #print("l_ratio", black_left_ratio)
    # spikeで正負の処理を行う.
    # 右壁が近い時の処理
    if wall_right:
        sign_flag = 4
        steer = -100
        speed = 30
    # 左壁が近い時の処理
    elif wall_left:
        sign_flag = 4
        steer = 100
        speed = 30

    # 正面に壁がある時の処理
    if wall_right and wall_left:
        sign_flag = 5

    if sign_flag == 0:
        speed = 50

    steer_int = int(steer)
    if steer_int > 120:
        steer_int = 120
    elif steer_int < -120:
        steer_int = -120

    side_flag = 0

    cmd = "{:4d},{:3d},{},{},{}@".format(steer_int, speed, sign_flag, rmode, side_flag)
    ser.write(cmd.encode("utf-8"))

    for i in range(1):  # 読み飛ばす処理（遅延して昔の値を取っている場合があるため）
        img = cap.read()

    end = time.perf_counter()
    elapsed_time = end - start

cv2.destroyAllWindows()
frame_writer.release()
ser.write("end@".encode())
