# 2023 obstacle
import hub
import time
import re
from gyro_testUNO import Gyro_remake
from basic_motion_testUNO import Basic_motion

print("--device init--")

# Device Acquisition
while True:
    motor = hub.port.C.motor
    motor_steer = hub.port.E.motor
    ser = hub.port.D
    center_button = hub.button.center
    if ser == None or motor == None or motor_steer == None:
        print("Please check port!!")
        time.sleep(1)
        continue
    motor.mode(2)
    ser.mode(hub.port.MODE_FULL_DUPLEX)
    motor_steer.mode(2)
    time.sleep(2)
    ser.baud(115200)
    time.sleep(1)
    break

# クラス定義
gyro_testUNO = Gyro_remake(motor_steer, motor)
basic = Basic_motion(motor_steer, motor)

# Empty the serial buffer
def resetSerialBuffer():
    while True:
        reply = ser.read(10000)
        if reply == b"":
            break

ser_size = 17

if True:
    # シリアル通信の準備
    time.sleep(1)
    start = time.ticks_us()

    while True:
        reply = ser.read(10000)
        print(reply)
        if reply == b"":
            break
    
    end = time.ticks_us()
    print("elapse_time: {}[ms]".format((end - start) / 1000))
    print("--waiting RasPi--")

    # 変数の定義
    end_flag = False
    throttle = 0
    steer = 0
    p_steer = 0
    rot = 0
    over_sign = 0

    go_angle = 0

    count = 0
    bias_roll = 0
    last_run = 1000000  # Record how far you have progressed since the last turnaround.

    info_yaw = 0

    sign_flag = 0
    last_flag = 0

    determine_backturn_flag = 0 # 0:not yet determined.  1:need to backturn.  2:determined.
    running_backturn_flag = 0 # 0:still not backturn.  1:backturn now.  2:backturned.
    count_check_red = 0
    count_check_green = 0

    new_rot = 0 

    memory_sign = [[0, 0], [0, 0], [0, 0], [0, 0]]

    done_firstsec = False
    rotation_mode = ""

    finish_go = 2100
    last_over_sign = 0

    # It doesn't start until a button is pressed.
    while not (center_button.is_pressed()):
        pass

    hub.motion.yaw_pitch_roll(0)
    while True:
        cmd = ""
        # At the end of three laps
        if gyro_testUNO.section_count >= 12:
            basic.stop()
            break

        # 停止するべきセクションで行われる処理
        if gyro_testUNO.section_count >= 11:
            # 青かオレンジ色の線を認識してから一定回転数進んだところで停止する
            # 曲がる直前の壁との距離で進む距離を変える
            if rotation_mode == "blue":
                if(last_over_sign >= 20):
                    finish_go = 2500
                elif(last_over_sign >= 10):
                    finish_go = 1700
                else:
                    finish_go = 2100

            elif rotation_mode == "orange":
                if(last_over_sign >= 20):
                    finish_go = 1700
                elif(last_over_sign >= 10):
                    finish_go = 2500
                else:
                    finish_go = 2100
            else:
                finish_go = 2100

            # 一定距離進んだら停止する
            if(
                ( motor.get()[0] - last_run >= finish_go )
            ):
                basic.stop()
                print(finish_go)
                break

        # Receive data via serial communication
        while True:
            reply = ser.read(ser_size - len(cmd))
            reply = reply.decode("utf-8")
            cmd = cmd + reply
            if len(cmd) >= ser_size and cmd[-1:] == "@":
                cmd_list = cmd.split("@")
                if len(cmd_list) != 2:
                    print(len(cmd_list))
                    cmd = ""
                    continue

                steer     = int(cmd_list[0].split(",")[0])
                throttle  = int(cmd_list[0].split(",")[1])

                rot       = int(cmd_list[0].split(",")[3])
                over_sign = int(cmd_list[0].split(",")[4])

                if (
                    sign_flag == 1 or sign_flag == 2 or sign_flag == 7 or sign_flag == 8
                ):
                    last_flag = sign_flag
                sign_flag = int(cmd_list[0].split(",")[2])
                break

        # Determine if you are going right or left.
        if rotation_mode == "":
            if rot == 1:
                rotation_mode = "blue"
            elif rot == 2:
                rotation_mode = "orange"

        # The color of the last sign determines if you're going the wrong way or not.
        if (gyro_testUNO.section_count == 7           # At the section with the last sign.
            and determine_backturn_flag == 0          # haven't yet made a decision on whether to make a back turn.
            and(
                (motor.get()[0] - last_run >= 400      # Start to turn and go a little further.
                and (count_check_red >= 4 or count_check_green >= 4))
                or
                (motor.get()[0] - last_run >= 2800)
            )
        ):
            print(count_check_red, count_check_green)

            if(count_check_red >= count_check_green):  # If it's red
                determine_backturn_flag = 1            # Flags that need to be backturned
                print("red -> backturn")
            else:                                      # If it's green
                determine_backturn_flag = 2            # Flag already judged
                print("green -> not backturn")

        # make someone run backwards
        if(
            gyro_testUNO.section_count == 8
            and determine_backturn_flag == 1
        ):
            running_backturn_flag = 0
            y = hub.motion.yaw_pitch_roll()[0]

            # Spike Hubのヨー角を更新する処理
            if rotation_mode == "blue":
                rotation_mode = "orange"
                backturn_yaw = 93+y
                if(backturn_yaw > 179): # Spike Hubのヨー角の定義域は -180 ~ 179 なので調整
                    backturn_yaw = backturn_yaw - 360
                hub.motion.yaw_pitch_roll(backturn_yaw)

            elif rotation_mode == "orange":
                rotation_mode = "blue"
                backturn_yaw = -93+y
                if(backturn_yaw < -180): #-180 ~ 179
                    backturn_yaw = backturn_yaw + 360
                hub.motion.yaw_pitch_roll(backturn_yaw)

            determine_backturn_flag = 2
            y = hub.motion.yaw_pitch_roll()[0]

            # ある程度その場で振り返る処理
            while abs(y) > 30:
                basic.move(30,-120)
                y = hub.motion.yaw_pitch_roll()[0]
                running_backturn_flag = 1
            gyro_testUNO.section_count = 7
            running_backturn_flag = 2

        # When the sign is not recognized as anything, it returns 0, and when it is recognized, it returns a non-zero value.
        if sign_flag == 0 or sign_flag == 3:
            if bias_roll >= 600:
                bias_roll = 0
            st_roll = motor.get()[0]
            # 直前に標識を避けていた場合に、少しだけ避けた方向と逆に向きながら走行する
            if (
                motor.get()[0] - gyro_testUNO.straight_rotation >= 1000 # <= 360 * 0.8
                and motor.get()[0] - gyro_testUNO.straight_rotation <= 2500
                and gyro_testUNO.past_change == 0
            ):
                if rotation_mode == "blue" and (last_flag == 2 or last_flag == 8):
                    gyro_testUNO.straightening(throttle, -10)
                    print("last_flag = ",last_flag," move1")

                elif rotation_mode == "blue" and (last_flag == 1 or last_flag == 7):
                    gyro_testUNO.straightening(throttle, 10)
                    print("last_flag = ",last_flag," move2")

                elif rotation_mode == "orange" and (last_flag == 1 or last_flag == 7):
                    gyro_testUNO.straightening(throttle, 10)
                    print("last_flag = ",last_flag," move3")

                elif rotation_mode == "orange" and (last_flag == 2 or last_flag == 8):
                    gyro_testUNO.straightening(throttle, -5)
                    print("last_flag = ",last_flag," move4")

                else:
                    gyro_testUNO.straightening(throttle, 0)
            else:
                gyro_testUNO.straightening(throttle, 0)

            en_roll = motor.get()[0]
            bias_roll += en_roll - st_roll

        # sign_flag == 4,7,8 are close to the wall, sign_flag == 5 has a wall in front
        else:
            yaw = hub.motion.yaw_pitch_roll()[0]
            straight_flag = False
            # 左右のどちらかの壁に近いとき
            if sign_flag == 4 or sign_flag == 7 or sign_flag == 8:
                # Hubのヨー角が大きければ、ステアリング値を大きくするc
                if (
                    abs(yaw) > 50 
                    and motor.get()[0] - gyro_testUNO.straight_rotation <= 1500
                ):
                    if yaw > 0:
                        throttle = throttle - 10
                        steer = -70 
                    elif yaw < 0:
                        throttle = throttle - 10
                        steer = 70 

                # バックターンのために赤色と緑色の標識が見えている量を把握するための処理
                if (gyro_testUNO.section_count == 7       # At the section with the last sign.
                    and determine_backturn_flag == 0      # haven't made the decision to backturn yet.
                    and sign_flag == 7                    # Red is visible and the wall is close.
                ):
                    count_check_red = count_check_red + 1

                elif (gyro_testUNO.section_count == 7      # At the section with the last sign.
                    and determine_backturn_flag == 0       # haven't made the decision to backturn yet.
                    and sign_flag == 8                     # Green is visible and the wall is close.
                ):
                    count_check_green = count_check_green + 1

            # 正面に壁が見えている時の処理
            elif sign_flag == 5:
                throttle = throttle + 10
                if yaw < 0:
                    if yaw > 60:
                        steer = 120
                    else:
                        steer = 120
                else:
                    steer = -1200
                if abs(yaw) < 20:  # Perhaps this pattern is only inside
                    if rotation_mode == "orange":
                        steer = -120
                        throttle = throttle - 10
                    elif rotation_mode == "blue":
                        steer = 120
                        throttle = throttle - 10

            elif sign_flag == 6:
                pass

            # 赤色の標識が見えている時の処理
            elif sign_flag == 1:
                bias_roll = 0
                info_yaw = yaw / 5

                # バックターンのために赤色の標識が見えている量を把握するための処理
                if (gyro_testUNO.section_count == 7        # At the section with the last sign.
                    and determine_backturn_flag == 0       # haven't made the decision to backturn yet.
                ):
                    count_check_red = count_check_red + 1

                # Hubのヨー角が一定以上のとき曲がり方を緩やかにする
                if (
                    yaw > 20
                    and motor.get()[0] - gyro_testUNO.straight_rotation >= 360 * 4
                ):
                    print("paturn 1")
                    throttle = throttle + 10
                    steer = steer - 70
                    if steer < -3:
                        steer = -3

                # 半時計周りで曲がり始めたとき曲がり方を急にする
                elif (
                    yaw >= 30
                    and yaw <= 180
                    and motor.get()[0] - gyro_testUNO.straight_rotation < 360 * 3
                    and rotation_mode == "blue"
                    and gyro_testUNO.past_change == 0
                ):
                    print("paturn 2")
                    if yaw > 85:  # Yaw angle is more than 85 degrees when reading red in a counterclockwise direction (= situation where red is visible ahead just before the turn).
                        throttle = throttle + 10
                        steer = steer + 10
                    else:
                        throttle = throttle + 10
                        steer = steer + 20

                # 時計回りで曲がり始めた時ヨー角が一定以上なら緩やかに曲がる
                if (
                    yaw > -5
                    and motor.get()[0] - gyro_testUNO.straight_rotation < 360 * 3
                    and rotation_mode == "orange"
                    and gyro_testUNO.past_change == 0
                ):
                    print("paturn 3")
                    steer = steer - 30
                    if steer < 10:
                        steer = 10
                    pass

                # ヨー角が曲がりたい方向と逆向きのとき一定のステアリング値にする
                if (
                    yaw < 0
                    and yaw > -60
                    and steer == 0
                    and motor.get()[0] - gyro_testUNO.straight_rotation > 360 * 3
                ):
                    print("paturn 4")
                    steer = 30

            # 緑色の標識が見えている時の処理(以下は赤色の標識が見えている時と対照的な処理)
            elif sign_flag == 2:
                if (gyro_testUNO.section_count == 7        # At the section with the last sign.
                    and determine_backturn_flag == 0       # haven't made the decision to backturn yet.
                ):
                    count_check_green = count_check_green + 1

                bias_roll = 0
                if (
                    yaw < -20
                    and motor.get()[0] - gyro_testUNO.straight_rotation >= 360 * 4
                ):
                    print("paturn 1")
                    throttle = throttle + 10
                    steer = steer + 70
                    if steer > 5:
                        steer = 5

                elif (
                    yaw <= -30
                    and yaw >= -180
                    and motor.get()[0] - gyro_testUNO.straight_rotation < 360 * 3
                    and rotation_mode == "orange"
                    and gyro_testUNO.past_change == 0
                ):
                    print("paturn 2")
                    if yaw < -85:
                        throttle = throttle + 10
                        steer = steer - 10
                    else:
                        throttle = throttle + 10
                        steer = steer - 20

                if (
                    yaw < 5
                    and motor.get()[0] - gyro_testUNO.straight_rotation < 360 * 4
                    and rotation_mode == "blue"
                    and gyro_testUNO.past_change == 0
                ):
                    print("paturn 3")
                    throttle = throttle 
                    steer = steer + 30  
                    if steer > -10:
                        steer = -10
                    pass

                if (
                    yaw > 0
                    and yaw < 60
                    and steer == 0
                    and motor.get()[0] - gyro_testUNO.straight_rotation > 360 * 3
                ):
                    print("paturn 4")
                    steer = -50

                info_yaw = -1 * yaw / 5

            # ロボットの走行が停止するのを防ぐ
            if throttle < 5:
                throttle = 5
            # 直進する
            if straight_flag:
                gyro_testUNO.straightening(throttle, 0)
            # 任意の方向を向いて走行
            else:
                basic.move(throttle, steer + info_yaw)

        # 3周目に逆走する必要がある時の処理
        if(running_backturn_flag == 2):
            blue_camera = rot == 2
            orange_camera = rot == 1
            if(rot == 1):
                new_rot = 2
            elif(rot == 2):
                new_rot = 1
            else:
                new_rot = 0
        else:
            blue_camera = rot == 1
            orange_camera = rot == 2
            new_rot = rot

        # 角で曲がる処理
        # The amount of manipulation is determined by what you see in the back when you turn the corner.
        if determine_backturn_flag != 1:
            if blue_camera:  # counterclockwise rotation
                if (over_sign % 10) == 0:  # can't see anything in the back.
                    if(over_sign >= 20):   # 右側の壁に近いとき
                        go_angle = 100 
                    elif(over_sign >= 10): # 左側の壁に近いとき
                        go_angle = 600
                    else:                  # 両側の壁に近くないとき
                        go_angle = 300
                    
                    # Hubのヨー角を更新
                    if gyro_testUNO.change_steer(30, new_rot, go_angle, steer, running_backturn_flag):
                        print("none1", over_sign)
                        last_run = motor.get()[0]
                        last_over_sign = over_sign
                        gyro_testUNO.sign_count = 0
                        last_flag = 0
                        print("section_count:", gyro_testUNO.section_count)

                elif (over_sign % 10) == 1:  # can see red in the back.
                    if(over_sign >= 20):
                        go_angle = 300
                    elif(over_sign >= 10):
                        go_angle = 1400
                    else:
                        go_angle = 800
                    if gyro_testUNO.change_steer(30, new_rot, go_angle, steer, running_backturn_flag):
                        print("red get1", over_sign)
                        last_run = motor.get()[0]
                        last_over_sign = over_sign
                        gyro_testUNO.sign_count = 0
                        last_flag = 0
                        print("section_count:", gyro_testUNO.section_count)

                elif (over_sign % 10) == 2:  # can see green in the back.
                    if(over_sign >= 20):
                        go_angle = 0
                    elif(over_sign >= 10):
                        go_angle = 500
                    else:
                        go_angle = 330
                    if gyro_testUNO.change_steer(30, new_rot, go_angle, steer, running_backturn_flag):
                        print("green get1", over_sign)
                        last_run = motor.get()[0]
                        last_over_sign = over_sign
                        gyro_testUNO.sign_count = 0
                        last_flag = 0
                        print("section_count:", gyro_testUNO.section_count)

            elif orange_camera:  # clockwise rotation
                if (over_sign % 10) == 0:  # can't see anything in the back.
                    if(over_sign >= 20):
                        go_angle = 600
                    elif(over_sign >= 10):
                        go_angle = 100 
                    else:
                        go_angle = 300 
                    if gyro_testUNO.change_steer(30, new_rot, go_angle, steer, running_backturn_flag):
                        print("none2", over_sign)
                        last_run = motor.get()[0]
                        last_over_sign = over_sign
                        gyro_testUNO.sign_count = 0
                        last_flag = 0
                        print("lookred_section_count:", gyro_testUNO.section_count)

                elif (over_sign % 10) == 1:  # can see red in the back.
                    if(over_sign >= 20):
                        go_angle = 500
                    elif(over_sign >= 10):
                        go_angle = 0
                    else:
                        go_angle = 300
                    if gyro_testUNO.change_steer(30, new_rot, go_angle, steer, running_backturn_flag):
                        print("red get2", over_sign)
                        last_run = motor.get()[0]
                        last_over_sign = over_sign
                        gyro_testUNO.sign_count = 0
                        last_flag = 0
                        print("lookred_section_count:", gyro_testUNO.section_count)

                elif (over_sign % 10) == 2:  # can see green in the back.
                    if(over_sign >= 20):
                        go_angle = 1430
                    elif(over_sign >= 10):
                        go_angle = 300 
                    else:
                        go_angle = 500 
                    if gyro_testUNO.change_steer(30, new_rot, go_angle, steer, running_backturn_flag):
                        print("green get2", over_sign)
                        last_run = motor.get()[0]
                        last_over_sign = over_sign
                        gyro_testUNO.sign_count = 0
                        last_flag = 0
                        print("lookgreen_section_count:", gyro_testUNO.section_count)

        # 逆走が始まるタイミングのとき
        else :
            if rotation_mode == "orange":
                go_angle = 300
            else:
                go_angle = 0
            if gyro_testUNO.change_steer(30, new_rot, go_angle, steer, running_backturn_flag):
                print("backturn")
                last_run = motor.get()[0]
                gyro_testUNO.sign_count = 0
                last_flag = 0
                print("section_count:", gyro_testUNO.section_count)

        resetSerialBuffer()
        p_steer = steer

    # After stopping, move motor_steer so that it reaches 0 degrees in absolute angle
    motor_steer.run_to_position(0,5)

