# カラー検出及び制御量の算出と制御 # 本戦用 # テスト用 # 2023
import serial
import time
import color_tracking_remake
import cv2
import os
import numpy as np

ser = serial.Serial("/dev/ttyAMA1", 115200)
throttle = 80

data_dir = "/home/pi/WRO2022/data"
save_dir = os.path.join(data_dir, "train")
SAVE_FPS = 0.5

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

    # 黒色の比の大きさでどこの壁なのかを特定
    if black_right_ratio > 0.75 and black_left_ratio > 0.75:
        wall_right = True
        wall_left = True
    elif black_right_ratio > 0.4 or black_left_ratio > 0.4:
        if black_right_ratio > black_left_ratio:
            wall_right = True
        else:
            wall_left = True

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

    # 周回の向き決定
    if rotation_mode == "":
        #if 1:
        if ok_blue and ok_orange:
            if orange_center_y > blue_center_y:
                rotation_mode = "orange"
                # print("orange1")
            else:
                rotation_mode = "blue"
                ## print("blue1")
        elif ok_blue:
            rotation_mode = "blue"
            # print("blue2")
        elif ok_orange:
            rotation_mode = "orange"
            # print("orange2")
        else:
            rotation_mode = ""
            # print("None")

    steer = 0
    max_area = 0.4
    speed = 30
    rmode = 0
    force_sign = -1

    if red_ratio >= 0.0025 or green_ratio >= 0.0025:
        center_frame = width / 2

        if red_ratio > green_ratio:
            if red_ratio < 0.4:
                sign_flag = 1
                distance = red_ratio / max_area  # 最大面積との比で標識までの距離を概算
                center_ratio_red = center_red_x / width # 0(一番左)~1(一番右)の範囲で赤の中心x座標を表現
                wide = center_ratio_red - 0.5 + 0.2 # 避けたい方向のx座標を示す

                if (  # 角で右回りしたい時に手前に緑があった時のフラグ
                    rotation_mode == "orange"
                    and ok_orange
                    and green_ratio > 0.001
                    and center_green_x / width >= 0.1
                    and center_green_x / width <= 0.8
                ):
                    pass

                if wide > 1:
                    wide = 1

                steer = (  # 三つのパラメータからステアリング値を計算 この辺の式をいじってよくする
                    (20*3) #20*4 changed
                    / max_area
                    * (90-(np.arccos(wide*distance)*180)/np.pi)
                )
                # 赤色の標識が接近してきた時の処理
                if center_ratio_red < 0.15: #0.15
                    if red_ratio > 0.05:
                        steer = (red_ratio / 0.05) * 110
                    elif red_ratio > 0.008:
                        steer = 0
                    elif red_ratio > 0.004:
                        steer = steer * 1
                    else:
                        steer = steer * 1

                elif center_ratio_red < 0.5:
                    if red_ratio > 0.015:
                        steer = (red_ratio / 0.015) * 55

                    elif red_ratio > 0.008:
                        steer = (red_ratio / 0.008) * 45

                elif center_ratio_red < 0.75:
                    if red_ratio > 0.015:
                        steer = (red_ratio / 0.015) * 90
                    if steer < 0 and red_ratio > 0.01:
                        steer = 0
                    elif red_ratio > 0.0011:
                        steer = steer * 2

                else:
                    if red_ratio > 0.01:
                        steer = steer * 4
                    else:
                        steer = steer
                        # steer = steer * 3.5
                        # print("CRR",center_ratio_red)
                        # print("RR",red_ratio)
                        # print(steer)
                        # print("YABAI")

                # 右に曲がりたい時に内壁が近くなってきた場合左に少し避ける処理
                if black_right_ratio > 0.15 and (rotation_mode == "orange"):
                    if (
                        red_ratio < 0.02
                        and orange_center_y > 0.6
                        and orange_center_y < 0.8
                        and center_ratio_red < 0.5
                        and center_ratio_red > 0.2
                    ):
                        steer = -40 # -50
                        speed = 40 # 50
                    elif (
                        red_ratio < 0.02
                        and orange_center_y >= 0.8
                        and orange_center_y < 1
                        and center_ratio_red < 0.5
                        and center_ratio_red > 0.2
                    ):
                        steer = -40
                        speed = 40

                if red_ratio > 0.15:  # avoid
                    steer = 100 # 100
                    speed = 30

                # 0にするとstraighteningになるので、1を送る
                if int(steer) == 0:
                    steer = 1

        else:
            if green_ratio < 0.4:
                sign_flag = 2
                distance = green_ratio / max_area  # 最大面積との比で標識までの距離を概算
                center_ratio_green = center_green_x / width # 0(一番左)~1(一番右)の範囲で緑の中心x座標を表現
                wide = center_ratio_green - 0.5 - 0.2 # 避けたい方向のx座標を示す

                if (  # 角で左回りしたい時に手前に赤があった時のフラグ
                    rotation_mode == "blue"
                    and ok_blue
                    and red_ratio > 0.001
                    and center_red_x / width <= 0.9
                    and center_red_x / width > 0.2
                ):
                    pass

                if wide < -1:
                    wide = -1

                steer = (  # 三つのパラメータからステアリング値を計算 この辺の式をいじってよくする
                    (20*3) #20*4 changed
                    / max_area
                    * (90 - (np.arccos(wide * distance) * 180) / np.pi)
                )

                # 緑色の標識が接近してきた時の処理
                if center_ratio_green > 0.85:
                    if green_ratio > 0.05:
                        steer = -(green_ratio / 0.05) * 110
                    elif green_ratio > 0.008:
                        steer = -(green_ratio / 0.05) * 40
                    elif green_ratio > 0.004:
                        steer = steer * 1
                    else:
                        steer = steer * 1

                elif center_ratio_green > 0.6:
                    if green_ratio > 0.015:
                        steer = -(green_ratio / 0.02) * 55
                    elif green_ratio > 0.008:
                        steer = -(green_ratio / 0.008) * 45
                    else:
                        steer = steer

                elif center_ratio_green > 0.25:
                    if green_ratio > 0.015:
                        steer = -(green_ratio / 0.015) * 90
                    if steer > 0 and green_ratio > 0.01:
                        steer = 0
                    elif green_ratio > 0.011:
                        steer = steer * 2
                    else:
                        steer = steer

                else:
                    if green_ratio > 0.01:
                        steer = steer * 4
                    else:
                        steer = steer
                        # steer = steer * 3.5


                # 左に曲がりたい時に左壁が近くなってきた場合右に少し避ける処理
                if black_left_ratio > 0.15 and (rotation_mode == "blue"):
                    if (
                        green_ratio < 0.02
                        and blue_center_y > 0.6
                        and blue_center_y < 0.8
                        and center_ratio_green > 0.5
                        and center_ratio_green < 0.8
                    ):
                        steer = 40
                        speed = 40
                    elif (
                        green_ratio < 0.02
                        and blue_center_y >= 0.8
                        and blue_center_y < 1
                        and center_ratio_green > 0.5
                        and center_ratio_green < 0.8
                    ):
                        steer = 40
                        speed = 40

                if green_ratio > 0.15:  # avoid
                    steer = -100 # -120
                    speed = 30

                if int(steer) == 0:
                    steer = -1

    if (ok_blue or ok_orange) and rotation_mode == "blue":  # 青色認識 ok_blue or ok_orange
        # 壁に近くなくても少し右に曲がる処理
        if (
            blue_center_y < 0.75
            and sign_flag == 2
            and center_ratio_green < 0.7
            and green_ratio < 0.005
        ):
            sign_flag = 6
            rmode = 1
            #steer = 50
        if (
            black_left_ratio > 0.3
            or (sign_flag == 2 and center_ratio_green > 0.7 and green_ratio < 0.012)
        ) and blue_center_y < 1:
            rmode = 1
            sign_flag = 6
            #steer = 90 # 120
            speed = speed #- 20
        elif sign_flag == 2 and center_ratio_green <= 0.65:
            rmode = 1
        else:
            rmode = 1

    elif (ok_orange or ok_blue) and rotation_mode == "orange":  # 橙色認識 ok_orange """or ok_blue"""
        # 壁に近くなくても少し左に曲がる処理
        if (
            orange_center_y < 0.75
            and sign_flag == 1
            and center_red_x / width > 0.3
            and red_ratio < 0.005 #0.012
        ):
            sign_flag = 6
            rmode = 2
            #steer = -50
        if (
            black_right_ratio > 0.3
            or (sign_flag == 1 and center_red_x / width < 0.4 and red_ratio < 0.012)
        ) and orange_center_y < 1:
            rmode = 2
            sign_flag = 6
            #steer = -90 # 120
            speed = speed #- 20
        elif sign_flag == 1 and center_red_x / width >= 0.35:
            rmode = 2
        else:
            rmode = 2

    # print("r_ratio", black_right_ratio)
    # print("l_ratio", black_left_ratio)
    # spikeで正負の処理を行う.
    # 右壁が近い時の処理
    if wall_right:
        if sign_flag == 1:
            sign_flag = 7
            steer = -30
            speed =30
        elif sign_flag == 2:
            pass
        else:
            sign_flag = 4
            steer = -70
            speed = 30

    # 左壁が近い時の処理
    elif wall_left:
        if sign_flag == 2:
            sign_flag = 8
            steer = 30
            speed = 30
        elif sign_flag == 1:
            pass
        else:
            sign_flag = 4
            steer = 70
            speed = 30

    # 正面に壁がある時の処理
    if wall_right and wall_left:
        sign_flag = 5

    if sign_flag == 0:
        speed = 50

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
    if green_ratio < 0.001 and red_ratio < 0.001: # 何も標識が見えていない
        if black_left_ratio >= 0.1 or black_right_ratio >= 0.1:  # 壁が近いかどうか
            if black_left_ratio > black_right_ratio:
                over_sign = over_sign + 10 #左の壁が近い
            else:
                over_sign = over_sign + 20 #右の壁が近い
        else:
            pass

    else: # 何かしら標識がみえる
        if red_ratio > green_ratio: # 赤の占める面積が大きい
            if green_ratio > 0.001:
                if center_green_y > 0.65:
                    over_sign = 1
                else:
                    over_sign = 2
            elif center_red_y < 0.65: # 赤がすぐ近くにない（＝奥にある）or近くのを通り過ぎていて見えない
                over_sign = 1
            else:
                over_sign = 0

            if black_left_ratio >= 0.1 or black_right_ratio >= 0.1:  # 壁が近いかどうか
                if black_left_ratio > black_right_ratio:
                    over_sign = over_sign + 10 #左の壁が近い
                else:
                    over_sign = over_sign + 20 #右の壁が近い
            else:
                pass

        else: # 緑の占める面積が大きい
            if red_ratio > 0.001: # 緑のほうが近いのに赤の標識を認識する
                if center_red_y > 0.65:
                    over_sign = 2
                else:
                    over_sign = 1
            elif center_green_y < 0.65: # 緑がすぐ近くにない（＝奥にある）or近くのを通り過ぎていて見えない
                over_sign = 2
            else:
                over_sign = 0

            if black_left_ratio >= 0.1 or black_right_ratio >= 0.1:  # 壁が近いかどうか
                if black_left_ratio > black_right_ratio:
                    over_sign = over_sign + 10 #左の壁が近い
                else:
                    over_sign = over_sign + 20 #右の壁が近い
            else:
                pass
    """
    over_sign値決定の説明
    奥に何が見えるか...一の位で表現 0:何も見えない 1:奥に赤 2:奥に緑
    壁に近いか...十の位で表現 0:近くに壁なし 1:左に壁が近い 2:右に壁が近い
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

    cmd = "{:4d},{:3d},{},{},{:3d}@".format(steer_int, speed, sign_flag, rmode, over_sign)
    # print(cmd)
    ser.write(cmd.encode("utf-8"))
    # print(cmd.encode("utf-8"))

    for i in range(1):  # 読み飛ばす処理（遅延して昔の値を取っている場合があるため）
        img = cap.read()

    end = time.perf_counter()
    elapsed_time = end - start

cv2.destroyAllWindows()
frame_writer.release()
ser.write("end@".encode())
