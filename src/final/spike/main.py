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

# class definition
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
    # Preparation for serial communication
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

    # Variable Definitions
    # モーターの制御量に関する変数
    throttle = 0 # 駆動モーターの回転速度
    steer = 0 # ステアリングモーターの角度

    # 進行方向に関する変数
    rot = 0 # 進行方向(時計回りか反時計回りか)を記録
    rotation_mode = "" # rotをstr型で記録 "blue" or "orange"

    # 見える標識に関する変数
    sign_flag = 0 # 現在見えている標識と壁の情報
    last_sign_flag = 0 # 1つ前のsign_flagの値
    over_sign = 0 # 曲がる先に見える標識を記録
    last_over_sign = 0 # 1つ前のover_signの値

    # バックターンに関する変数
    determine_backturn_flag = 0 # バックターンするかどうかの判定に用いる 0:not yet determined.  1:need to backturn.  2:determined.
    running_backturn_flag = 0 # バックターンの状態を示す 0:still not backturn.  1:backturn now.  2:backturned.
    backturn_orientation = -120 # バックターン中のステアリングモーターの角度
    determine_backturn_sec = 0 # バックターンをするかどうかの判断をするセクション
    new_rot = 0 # バックターン後のrot

    # 各セクションの標識の配置を記録するための変数
    count_check_red = 0 # 赤色の標識が見えている時に増加する
    count_check_green = 0 # 緑色の標識が見えている時に増加する
    simple_memory_sign = [0, 0, 0, 0] # 各セクションの標識の色の配置を記録する配列
    first_memory_flag = 0 # 各セクションごとで最初に見えた標識を記録
    determine_memory_flag = 0 # 各セクションで標識の色の配置を記録済みかを記録

    # その他の情報を記録するための変数
    memory_M_L = [0, 0, 0, 0] # 曲がり始めてからfirst_memory_flagが記録されるまでの駆動モーターの回転数を記録
    memory_last_oversign = [100, 100, 100, 100] # 各セクションのlast_over_signの値を記録

    # セクション1の真ん中にsignがあるかどうかを判断するための変数
    sec1_check = 0 # 走行開始から最初に曲がるまで増え続ける
    sec1_center_sign_flag = 0 # セクション1の真ん中にsignがあるかどうかを記録

    # その他の用途で用いる変数
    go_angle = 0 # 曲がる際の直進量
    finish_go = 2100 # 最後の角を曲がってから止まるまでの駆動モーターの回転数
    last_run = 1000000  # Record how far you have progressed since the last turnaround.
    info_yaw = 0 # 標識を避ける際にHubのヨー角に応じて少し角度を変えるのに用いる

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

        # Processing to be done in the section to be stopped
        if gyro_testUNO.section_count >= 11:
            # After recognizing the blue or orange line, it stops after a certain number of revolutions.
            # Change the distance to go by the distance to the wall just before the turn.
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

            # Stops when advanced a certain distance.
            if(
                ( motor.get()[0] - last_run >= finish_go )
            ):
                basic.stop()
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
                    last_sign_flag = sign_flag
                sign_flag = int(cmd_list[0].split(",")[2])
                break

        # Determine if you are going right or left.
        if rotation_mode == "":
            if rot == 1:
                rotation_mode = "blue"
            elif rot == 2:
                rotation_mode = "orange"

        # 過去のoversignを記録
        if (gyro_testUNO.section_count >= 0
            and gyro_testUNO.section_count <= 3
            and memory_last_oversign[gyro_testUNO.section_count] == 100
        ):
            memory_last_oversign[gyro_testUNO.section_count] = last_over_sign

        # first_memory_flagの決定
        if (gyro_testUNO.section_count >= 0 
            and gyro_testUNO.section_count <= 3 # 各セクションを初めて通過するとき
            and first_memory_flag == 0 # まだfirst_memory_flagの決定がされていない
            and(
                (motor.get()[0] - last_run >= 400      #曲がりはじめてからある程度すすんだところで、
                and (count_check_red >= 2 or count_check_green >= 2)) # 赤か緑が見えたら
                or
                (motor.get()[0] - last_run >= 3300)    # 曲がりはじめてある程度進みきったら
            )
        ):
            memory_M_L[gyro_testUNO.section_count] = motor.get()[0] - last_run 
            if (last_over_sign % 10) != 0:
                first_memory_flag = last_over_sign % 10 + 10 # 曲がる直前に何らかの標識が見えていたならそれが最初に見える標識
            else:
                if(count_check_red >= count_check_green):      # 最初に見えたのが赤なら
                    first_memory_flag = 1
                else:                                     # 最初に見えたのが緑なら
                    first_memory_flag = 2
            print(count_check_red, count_check_green, first_memory_flag, last_over_sign)

        # simple_memory_signの決定
        if (gyro_testUNO.section_count >= 1 # 各セクションを通り過ぎたら
            and gyro_testUNO.section_count <= 4
            and determine_memory_flag == 1
        ):
            print(count_check_red, count_check_green, first_memory_flag)

            if gyro_testUNO.section_count == 1 and sec1_check <= 15: # 増えた量でスタートセクションの真ん中に標識があるかないか判断
                sec1_center_sign_flag = 1
                print("sec1 center sign is here. sec1_check = ", sec1_check)

            if count_check_red >= 2 and count_check_green >= 2: # 両方の標識を認識
                if first_memory_flag % 10 == 1:              # 先に見えたのが赤なら
                    simple_memory_sign[gyro_testUNO.section_count - 1] = 3   #red -> green
                else:                                        # 先に見えたのが緑なら
                    simple_memory_sign[gyro_testUNO.section_count - 1] = 4   #green -> red

            else:                                         # 片方の色の標識だけを認識 or 認識できなかったとき
                if(count_check_red == 0 and count_check_green == 0): # 認識できなかったとき
                    if memory_last_oversign[gyro_testUNO.section_count -1]%10 == 1: # 過去のoversignの値を用いて決定
                        simple_memory_sign[gyro_testUNO.section_count - 1] = 1   # red only
                    elif memory_last_oversign[gyro_testUNO.section_count -1]%10 == 2:
                        simple_memory_sign[gyro_testUNO.section_count - 1] = 2   # green only
                    else:
                        simple_memory_sign[gyro_testUNO.section_count - 1] = 2   # green only

                elif(count_check_red >= count_check_green): # 多く見えていたのが赤なら
                    if first_memory_flag == 12:
                        simple_memory_sign[gyro_testUNO.section_count - 1] = 4   # green -> red
                    else:
                        simple_memory_sign[gyro_testUNO.section_count - 1] = 1   # red only

                else:                                       # 緑なら
                    if first_memory_flag == 11:
                        simple_memory_sign[gyro_testUNO.section_count - 1] = 3   # red -> green
                    else:
                        simple_memory_sign[gyro_testUNO.section_count - 1] = 2   # green only
            print(simple_memory_sign)
            print("----------")

            # 次の判断のために変数を初期化
            count_check_red = 0
            count_check_green = 0
            first_memory_flag = 0
            determine_memory_flag = 0

        # 逆走するかどうかの判定
        if(determine_backturn_flag == 0 and gyro_testUNO.section_count == 7):
            if sec1_center_sign_flag == 1: # sec1の真ん中に標識があるとき
                determine_backturn_sec = -1

            elif memory_last_oversign[3]%10 != 0: # 曲がる先の標識が見えているとき（真ん中にあるときは弾けているので曲がってすぐのところのみ）
                determine_backturn_flag = memory_last_oversign[3]%10

            elif ( # 曲がる先の標識が見えないけど内側を通ってるとき
                (rotation_mode == "blue" and memory_last_oversign[3] == 10)
                or
                (rotation_mode == "orange" and memory_last_oversign[3] == 20)
            ):
                determine_backturn_sec = -1

            elif ( # 外側を通ってるとき
                (rotation_mode == "orange" and memory_last_oversign[3] == 10)
                or
                (rotation_mode == "blue" and memory_last_oversign[3] == 20)
            ):
                if memory_M_L[3] < 1300 or memory_M_L[3] > 2800:
                    determine_backturn_sec = 1
                else:
                    determine_backturn_sec = -1

            else: # 壁も標識も見えないとき
                if memory_M_L[3] < 1300 or memory_M_L[3] > 2800:
                    determine_backturn_sec = 1
                else:
                    determine_backturn_sec = -1

            if determine_backturn_flag == 0: # determine_backturn_flagが未定
                if determine_backturn_sec == 1: # スタートセクションで判断する
                    if simple_memory_sign[3] == 1 or simple_memory_sign[3] == 3: # red only or red -> green
                        determine_backturn_flag = 1
                    else:                                                        # green only or green -> red
                        determine_backturn_flag = 2
                else:                           # スタートセクションの1つ前ので判断する
                    if simple_memory_sign[2] == 1 or simple_memory_sign[2] == 4: # red only or green -> red
                        determine_backturn_flag = 1
                    else:                                                        # green only or red -> green
                        determine_backturn_flag = 2
            print("determine_backturn_flag: ", determine_backturn_flag)

        # make someone run backwards
        if(gyro_testUNO.section_count == 8 and determine_backturn_flag == 1): # バックターンするべきセクションで
            running_backturn_flag = 0
            y = hub.motion.yaw_pitch_roll()[0]

            # The process to update the yaw angle of Spike Hub
            if rotation_mode == "blue":
                rotation_mode = "orange"
                backturn_yaw = 93+y
                if(backturn_yaw > 179): # Spike Hub's yaw angle definition range is -180 ~ 179, so adjust
                    backturn_yaw = backturn_yaw - 360

            elif rotation_mode == "orange":
                rotation_mode = "blue"
                backturn_yaw = -95+y
                if(backturn_yaw < -180):
                    backturn_yaw = backturn_yaw + 360

            hub.motion.yaw_pitch_roll(backturn_yaw)
            determine_backturn_flag = 2
            y = hub.motion.yaw_pitch_roll()[0]

            # Process looking back on the spot to some extent
            # 曲がったすぐ先にある標識に応じてバックターンする際の向きを変える
            if simple_memory_sign[3] == 2 or simple_memory_sign[3] == 3:
                backturn_orientation = 120
            else:
                backturn_orientation = -120
            while abs(y) > 30:
                basic.move(30, backturn_orientation)
                y = hub.motion.yaw_pitch_roll()[0]
                running_backturn_flag = 1
            gyro_testUNO.section_count = 7
            running_backturn_flag = 2

        # スタートしてから最初に曲がるまで変数を増やす(増えた量でスタートセクションの真ん中に標識があるかないか判断)
        if (gyro_testUNO.section_count == -1):
            sec1_check = sec1_check + 1

        # When the sign is not recognized as anything, it returns 0, and when it is recognized, it returns a non-zero value.
        if sign_flag == 0 or sign_flag == 3:
            # If you have avoided a sign immediately before, run while facing slightly in the opposite direction from the direction you avoided it.
            if (
                motor.get()[0] - gyro_testUNO.straight_rotation >= 1000 
                and motor.get()[0] - gyro_testUNO.straight_rotation <= 2500
                and gyro_testUNO.past_change == 0
            ):
                if rotation_mode == "blue" and (last_sign_flag == 2 or last_sign_flag == 8):
                    gyro_testUNO.straightening(throttle, -10)

                elif rotation_mode == "blue" and (last_sign_flag == 1 or last_sign_flag == 7):
                    gyro_testUNO.straightening(throttle, 5)

                elif rotation_mode == "orange" and (last_sign_flag == 1 or last_sign_flag == 7):
                    gyro_testUNO.straightening(throttle, 10)

                elif rotation_mode == "orange" and (last_sign_flag == 2 or last_sign_flag == 8):
                    gyro_testUNO.straightening(throttle, -5)

                else:
                    gyro_testUNO.straightening(throttle, 0)
            else:
                gyro_testUNO.straightening(throttle, 0)

        # sign_flag == 4,7,8 are close to the wall, sign_flag == 5 has a wall in front
        else:
            yaw = hub.motion.yaw_pitch_roll()[0]
            straight_flag = False
            # When close to either left or right wall
            if sign_flag == 4 or sign_flag == 7 or sign_flag == 8:
                # If the yaw angle of the hub is large, increase the steering value.
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

                # 標識の記録のために赤色か緑色が見えていることを記録
                if (gyro_testUNO.section_count >= 0
                    and gyro_testUNO.section_count <= 3
                    and motor.get()[0] - last_run >= 300
                    and motor.get()[0] - last_run <= 3000
                ):
                    if sign_flag == 7: # Red is visible and the wall is close.
                        count_check_red = count_check_red + 1
                    elif sign_flag == 8: # Green is visible and the wall is close.
                        count_check_green = count_check_green + 1

            # Processing when a wall is visible in front
            elif sign_flag == 5:
                throttle = throttle + 10
                if yaw < 0:
                    if yaw > 60:
                        steer = 120
                    else:
                        steer = 120
                else:
                    steer = -120
                if abs(yaw) < 20:
                    if rotation_mode == "orange":
                        steer = -120
                        throttle = throttle - 10
                    elif rotation_mode == "blue":
                        steer = 120
                        throttle = throttle - 10

            elif sign_flag == 6:
                pass

            # Processing when the red sign is visible
            elif sign_flag == 1:
                info_yaw = yaw / 5
                # 標識の記録のために赤色が見えていることを記録
                if (gyro_testUNO.section_count >= 0
                    and gyro_testUNO.section_count <= 3
                    and motor.get()[0] - last_run >= 300
                    and motor.get()[0] - last_run <= 3000
                ):
                    count_check_red = count_check_red + 1

                # Moderates the turn when the yaw angle of the Hub exceeds a certain value.
                if (
                    yaw > 20
                    and motor.get()[0] - gyro_testUNO.straight_rotation >= 360 * 4
                ):
                    throttle = throttle + 10
                    steer = steer - 70
                    if steer < -5:
                        steer = -5

                # When the bend begins to turn around the semi-clock, make the turn steeper.
                elif (
                    yaw >= 30
                    and yaw <= 180
                    and motor.get()[0] - gyro_testUNO.straight_rotation < 360 * 3
                    and rotation_mode == "blue"
                    and gyro_testUNO.past_change == 0
                ):
                    if yaw > 85:  # Yaw angle is more than 85 degrees when reading red in a counterclockwise direction (= situation where red is visible ahead just before the turn).
                        throttle = throttle + 10
                        steer = steer + 10
                    else:
                        throttle = throttle + 10
                        steer = steer + 20

                # When it starts to turn clockwise, if the yaw angle is above a certain level, it turns gently.
                if (
                    yaw > -5
                    and motor.get()[0] - gyro_testUNO.straight_rotation < 360 * 3
                    and rotation_mode == "orange"
                    and gyro_testUNO.past_change == 0
                ):
                    steer = steer - 30
                    if steer < 10:
                        steer = 10
                    pass

                # Constant steering value when the yaw angle is opposite to the direction in which you want to turn.
                if (
                    yaw < 0
                    and yaw > -60
                    and steer == 0
                    and motor.get()[0] - gyro_testUNO.straight_rotation > 360 * 3
                ):
                    steer = 30

            # Processing when the green sign is visible(The process described below is almost identical to that for recognizing red signs.)
            elif sign_flag == 2:
                info_yaw = -1 * yaw / 5
                # 標識の記録のために緑色が見えていることを記録
                if (gyro_testUNO.section_count >= 0
                    and gyro_testUNO.section_count <= 3
                    and motor.get()[0] - last_run >= 300
                    and motor.get()[0] - last_run <= 3000
                ):
                    count_check_green = count_check_green + 1

                if (
                    yaw < -20
                    and motor.get()[0] - gyro_testUNO.straight_rotation >= 360 * 4
                ):
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
                    steer = -50

            # Prevent the robot from stopping
            if throttle < 5:
                throttle = 5
            # Go straight ahead.
            if straight_flag:
                gyro_testUNO.straightening(throttle, 0)
            # Running facing the specified direction
            else:
                basic.move(throttle, steer + info_yaw)

        # Process if you need to run the third lap facing the opposite direction.
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

        # Processing turning at the corner
        # The amount of manipulation is determined by what you see in the back when you turn the corner.
        if determine_backturn_flag != 1:
            if blue_camera:  # counterclockwise rotation
                if (over_sign % 10) == 0:  # can't see anything in the back.
                    if(over_sign >= 20):   # When close to the right wall
                        go_angle = 100 
                    elif(over_sign >= 10): # When close to the left wall
                        go_angle = 600
                    else:                  # When not close to the wall of both sides
                        go_angle = 300
                elif (over_sign % 10) == 1:  # can see red in the back.
                    if(over_sign >= 20):
                        go_angle = 300
                    elif(over_sign >= 10):
                        go_angle = 1430
                    else:
                        go_angle = 800
                elif (over_sign % 10) == 2:  # can see green in the back.
                    if(over_sign >= 20):
                        go_angle = 0
                    elif(over_sign >= 10):
                        go_angle = 520
                    else:
                        go_angle = 315
                # Update Hub's yaw angle
                if gyro_testUNO.change_steer(30, new_rot, go_angle, steer, running_backturn_flag):
                    print("blue  over_sign = ", over_sign)
                    print("C M-L:", motor.get()[0] - last_run)
                    last_run = motor.get()[0]
                    last_over_sign = over_sign
                    gyro_testUNO.sign_count = 0
                    last_sign_flag = 0
                    determine_memory_flag = 1
                    print("section_count:", gyro_testUNO.section_count)

            elif orange_camera:  # clockwise rotation
                if (over_sign % 10) == 0:  # can't see anything in the back.
                    if(over_sign >= 20):
                        go_angle = 600
                    elif(over_sign >= 10):
                        go_angle = 100 
                    else:
                        go_angle = 300 
                elif (over_sign % 10) == 1:  # can see red in the back.
                    if(over_sign >= 20):
                        go_angle = 520
                    elif(over_sign >= 10):
                        go_angle = 0
                    else:
                        go_angle = 315
                elif (over_sign % 10) == 2:  # can see green in the back.
                    if(over_sign >= 20):
                        go_angle = 1430
                    elif(over_sign >= 10):
                        go_angle = 300 
                    else:
                        go_angle = 850 
                if gyro_testUNO.change_steer(30, new_rot, go_angle, steer, running_backturn_flag):
                    print("C M-L:", motor.get()[0] - last_run)
                    print("orange over_sign = ", over_sign)
                    last_run = motor.get()[0]
                    last_over_sign = over_sign
                    gyro_testUNO.sign_count = 0
                    last_sign_flag = 0
                    determine_memory_flag = 1
                    print("lookred_section_count:", gyro_testUNO.section_count)
        # When the timing is right for the reverse run to begin.
        else :
            # 進行方向と直前に通った標識の色によって直進量を変える
            if rotation_mode == "blue":
                if simple_memory_sign[3] == 1 or simple_memory_sign[3] == 4: 
                    go_angle = 800
                else:
                    go_angle = 1200
            elif rotation_mode == "orange":
                if simple_memory_sign[3] == 1 or simple_memory_sign[3] == 4:
                    go_angle = 1200
                else:
                    go_angle = 800
            else:
                go_angle = 1000
            if gyro_testUNO.change_steer(30, new_rot, go_angle, steer, running_backturn_flag):
                print("backturn", go_angle)
                print("C M-L:", motor.get()[0] - last_run)
                last_run = motor.get()[0]
                gyro_testUNO.sign_count = 0
                last_sign_flag = 0
                determine_memory_flag = 1
                print("section_count:", gyro_testUNO.section_count)

        resetSerialBuffer()

    # After stopping, move motor_steer so that it reaches 0 degrees in absolute angle
    motor_steer.run_to_position(0,5)

