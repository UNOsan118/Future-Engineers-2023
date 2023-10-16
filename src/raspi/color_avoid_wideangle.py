# Color detection and control amount calculation and control 
# For obstacle 2023
import serial
import time
import color_tracking_remake
import cv2
import os
import numpy as np

ser = serial.Serial("/dev/ttyAMA1", 115200)
throttle = 80

data_dir = "/home/pi/WRO2023/data"
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
    speed = 30
    rmode = 0
    force_sign = -1

    if red_ratio >= 0.0025 or green_ratio >= 0.0025:
        center_frame = width / 2

        if red_ratio > green_ratio:
            if red_ratio < 0.4:
                sign_flag = 1
                distance = red_ratio / max_area  # Approximate distance to sign by ratio to maximum area
                center_ratio_red = center_red_x / width # Expresses the x-coordinate of the center of red in the range 0(left-most)~1(right-most).
                wide = center_ratio_red - 0.5 + 0.2 # Indicates the x-coordinate of the direction to be avoided

                if (  # When the car wants to turn right at the corner and there is green in front of the car
                    rotation_mode == "orange"
                    and ok_orange
                    and green_ratio > 0.001
                    and center_green_x / width >= 0.1
                    and center_green_x / width <= 0.8
                ):
                    pass

                if wide > 1:
                    wide = 1

                steer = (  # Calculate steering values from three parameters
                    (20*3) 
                    / max_area
                    * (90-(np.arccos(wide*distance)*180)/np.pi)
                )
                # Processing when a red sign is approaching
                if center_ratio_red < 0.15:
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

                # If the car wants to turn to the right and the inside wall is getting close, avoid it a little to the left.
                if black_right_ratio > 0.15 and (rotation_mode == "orange"):
                    if (
                        red_ratio < 0.02
                        and orange_center_y > 0.6
                        and orange_center_y < 0.8
                        and center_ratio_red < 0.5
                        and center_ratio_red > 0.2
                    ):
                        steer = -40 
                        speed = 40 
                    elif (
                        red_ratio < 0.02
                        and orange_center_y >= 0.8
                        and orange_center_y < 1
                        and center_ratio_red < 0.5
                        and center_ratio_red > 0.2
                    ):
                        steer = -40
                        speed = 40

                if red_ratio > 0.15:  
                    steer = 100 
                    speed = 30

                # Set to 0 for straitening, send 1
                if int(steer) == 0:
                    steer = 1

        else:
            if green_ratio < 0.4:
                sign_flag = 2
                distance = green_ratio / max_area  # Approximate distance to sign by ratio to maximum area.
                center_ratio_green = center_green_x / width  # Expresses the x-coordinate of the center of green in the range 0(left-most)~1(right-most).
                wide = center_ratio_green - 0.5 - 0.2  # Indicates the x-coordinate of the direction to be avoided.

                if (  # When the car wants to turn left at the corner green there is green in front of the car.
                    rotation_mode == "blue"
                    and ok_blue
                    and red_ratio > 0.001
                    and center_red_x / width <= 0.9
                    and center_red_x / width > 0.2
                ):
                    pass

                if wide < -1:
                    wide = -1

                steer = (  # Calculate steering values from three parameters
                    (20*3)
                    / max_area
                    * (90 - (np.arccos(wide * distance) * 180) / np.pi)
                )

                # Processing when a red sign is approaching
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

                # If the car wants to turn left and the left wall is getting close, avoid a little to the right.
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

                if green_ratio > 0.15:  
                    steer = -100 
                    speed = 30

                if int(steer) == 0:
                    steer = -1

    if (ok_blue or ok_orange) and rotation_mode == "blue":  # Recognize the blue line
        # Process a slight right turn without being close to the wall.
        if (
            blue_center_y < 0.75
            and sign_flag == 2
            and center_ratio_green < 0.7
            and green_ratio < 0.005
        ):
            rmode = 1
        if (
            black_left_ratio > 0.3
            or (sign_flag == 2 and center_ratio_green > 0.7 and green_ratio < 0.012)
        ) and blue_center_y < 1:
            rmode = 1
            speed = speed
        elif sign_flag == 2 and center_ratio_green <= 0.65:
            rmode = 1
        else:
            rmode = 1

    elif (ok_orange or ok_blue) and rotation_mode == "orange":  # Recognize the orange line
        # Process a slight left turn without being close to the wall.
        if (
            orange_center_y < 0.75
            and sign_flag == 1
            and center_red_x / width > 0.3
            and red_ratio < 0.005 
        ):
            rmode = 2
        if (
            black_right_ratio > 0.3
            or (sign_flag == 1 and center_red_x / width < 0.4 and red_ratio < 0.012)
        ) and orange_center_y < 1:
            rmode = 2
            speed = speed 
        elif sign_flag == 1 and center_red_x / width >= 0.35:
            rmode = 2
        else:
            rmode = 2

    # Identify where the wall is by the size of the black ratio
    if black_right_ratio > 0.75 and black_left_ratio > 0.75:
        wall_right = True
        wall_left = True
    elif black_right_ratio > 0.35 or black_left_ratio > 0.35:
        if black_right_ratio > black_left_ratio:
            wall_right = True
        else:
            wall_left = True

    # Processing when close to the right wall
    if wall_right:
        if sign_flag == 1:
            sign_flag = 7
            steer = -30
            speed =30
        elif black_right_ratio > 0.85:
            sign_flag = 4
            steer = -70
            speed = 30
        elif sign_flag == 2:
            pass
        else:
            sign_flag = 4
            steer = -50
            speed = 30

    # Processing when close to the left wall
    elif wall_left:
        if sign_flag == 2:
            sign_flag = 8
            steer = 30
            speed = 30
        elif black_left_ratio > 0.85:
            sign_flag = 4
            steer = 70
            speed = 30
        elif sign_flag == 1:
            pass
        else:
            sign_flag = 4
            steer = 50
            speed = 30

    # Processing when approaching the front
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


    # Determine what color the sign over there is at the turn.
    over_sign = 0
    if green_ratio < 0.001 and red_ratio < 0.001: # don't see any signs.
        if black_left_ratio >= 0.1 or black_right_ratio >= 0.1:  # Whether the wall is close or not
            if black_left_ratio > black_right_ratio:
                over_sign = over_sign + 10 # The left wall is close.
            else:
                over_sign = over_sign + 20 # The right wall is close.
        else:
            pass

    else: # see some kind of sign.
        if red_ratio > green_ratio: # Red occupies a large area.
            if green_ratio > 0.0015:
                if center_green_y > 0.65:
                    over_sign = 1
                else:
                    over_sign = 2
            elif center_red_y < 0.65: # Red is not immediately nearby (i.e., in the back) OR you are passing close by and can't see it.
                over_sign = 1
            else:
                over_sign = 0

            if black_left_ratio >= 0.1 or black_right_ratio >= 0.1:  # 壁が近いかどうか
                if black_left_ratio > black_right_ratio:
                    over_sign = over_sign + 10 # The left wall is close.
                else:
                    over_sign = over_sign + 20 # The right wall is close.
            else:
                pass

        else: # Green occupies a large area.
            if red_ratio > 0.0015: # Recognize red signs when green is closer.
                if center_red_y > 0.65:
                    over_sign = 2
                else:
                    over_sign = 1
            elif center_green_y < 0.65: # Green is not in the immediate vicinity (i.e., in the back) OR you are passing by a nearby one and can't see it.
                over_sign = 2
            else:
                over_sign = 0

            if black_left_ratio >= 0.1 or black_right_ratio >= 0.1:  # 壁が近いかどうか
                if black_left_ratio > black_right_ratio:
                    over_sign = over_sign + 10 # The left wall is close.
                else:
                    over_sign = over_sign + 20 # The right wall is close.
            else:
                pass
    """
    Explanation of over_sign value determination
    What you see at the back: The first place is... 0: Nothing is visible 1: The back is red 2: The back is green
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
