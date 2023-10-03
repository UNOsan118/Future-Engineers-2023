# 2023 obstacle
import hub
import time
import re
from gyro_testUNO import Gyro_remake
from basic_motion_testUNO import Basic_motion

print("--device init--")

# デバイスの取得
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

gyro_testUNO = Gyro_remake(motor_steer, motor)
basic = Basic_motion(motor_steer, motor)

# シリアルバッファの中を空にする
def resetSerialBuffer():
    while True:
        reply = ser.read(10000)
        if reply == b"":
            break

ser_size = 17

if True:
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
    end_flag = False
    throttle = 0
    steer = 0
    p_steer = 0
    rot = 0
    over_sign = 0

    go_angle = 0

    count = 0
    bias_roll = 0
    last_run = 1000000  # 最後の切り返しからどれだけ進んだのか記録

    info_yaw = 0

    sign_flag = 0
    last_flag = 0

    determine_backturn_flag = 0 # 0:not yet determined.  1:need to backturn.  2:determined.
    running_backturn_flag = 0 # 0:still not backturn.  1:backturn now.  2:backturned.
    count_check_red = 0
    count_check_green = 0

    new_rot = 0 #変数名かえよう

    memory_sign = [[0, 0], [0, 0], [0, 0], [0, 0]]

    done_firstsec = False
    rotation_mode = ""

    finish_go = 2100
    last_over_sign = 0

    # ボタンが押されるまで始まらない
    while not (center_button.is_pressed()):
        pass

    hub.motion.yaw_pitch_roll(0)
    while True:
        cmd = ""
        # 三周終わった時
        if gyro_testUNO.section_count >= 12:
            basic.stop()
            break

        if gyro_testUNO.section_count >= 11:
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

            if(
                ( motor.get()[0] - last_run >= finish_go )
            ):
                basic.stop()
                print(finish_go)
                break

        # シリアル通信でデータを受信
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

                if (#int(sign_flag) != int(cmd_list[0].split(",")[2])) and (
                    sign_flag == 1 or sign_flag == 2 or sign_flag == 7 or sign_flag == 8
                ):
                    last_flag = sign_flag
                    """
                    section_count = gyro_testUNO.section_count
                    sign_count = gyro_testUNO.sign_count

                    if (
                        section_count >= 0
                        and section_count < 4
                        and gyro_testUNO.sign_count < 2
                    ):
                        memory_sign[section_count][sign_count] = sign_flag
                        gyro_testUNO.sign_count = gyro_testUNO.sign_count + 1
                        start = time.ticks_us()
                        end = time.ticks_us()
                    """
                sign_flag = int(cmd_list[0].split(",")[2])
                break
        """
        if gyro_testUNO.section_count == -1:
            sign_flag = 0
        """

        # 右回りか左回りかを確定させる
        if rotation_mode == "":
            if rot == 1:
                rotation_mode = "blue"
            elif rot == 2:
                rotation_mode = "orange"

        #print(" M-L: ",motor.get()[0] - last_run," sf: ",sign_flag)
        # 最後の標識の色で逆走するかどうか判断する
        """
        if (gyro_testUNO.section_count == 7           #最後の標識があるセクションで、==7
            and determine_backturn_flag == 0          #まだバックターンをするかの判断をしていなく、
            and motor.get()[0] - last_run >= 400      #曲がりはじめてからある程度すすんだところで、
            and (count_check_red >= 3 or count_check_green >= 3)
        ):
        """
        if (gyro_testUNO.section_count == 7           #最後の標識があるセクションで、==7
            and determine_backturn_flag == 0          #まだバックターンをするかの判断をしていなく、
            and(
                (motor.get()[0] - last_run >= 400      #曲がりはじめてからある程度すすんだところで、
                and (count_check_red >= 4 or count_check_green >= 4))
                or
                (motor.get()[0] - last_run >= 2800)
            )
        ):
            print(count_check_red, count_check_green)

            if(count_check_red >= count_check_green):      #赤なら
                determine_backturn_flag = 1           #バックターンする必要があるフラグ
                print("red -> backturn")
            else:                                     #緑なら
                determine_backturn_flag = 2           #もう判断済みのフラグ
                print("green -> not backturn")

        #逆走させる
        if(
            gyro_testUNO.section_count == 8
            and determine_backturn_flag == 1
        ):
            running_backturn_flag = 0
            y = hub.motion.yaw_pitch_roll()[0]

            if rotation_mode == "blue":
                rotation_mode = "orange"
                backturn_yaw = 93+y
                if(backturn_yaw > 179): #-180 ~ 179
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

            while abs(y) > 30:
                basic.move(30,-120)
                y = hub.motion.yaw_pitch_roll()[0]
                running_backturn_flag = 1
            gyro_testUNO.section_count = 7
            running_backturn_flag = 2

        # 標識を何も認識していない時は0で、認識している時は0以外を返すようにしている
        if sign_flag == 0 or sign_flag == 3:
            if bias_roll >= 600:
                bias_roll = 0
            st_roll = motor.get()[0]
            # print(motor.get()[0] - gyro_testUNO.straight_rotation)
            if (
                motor.get()[0] - gyro_testUNO.straight_rotation >= 1000 # <= 360 * 0.8
                and motor.get()[0] - gyro_testUNO.straight_rotation <= 2500
                and gyro_testUNO.past_change == 0
            ):
                if rotation_mode == "blue" and (last_flag == 2 or last_flag == 8):
                    # basic.move(30, 30)
                    gyro_testUNO.straightening(throttle, -10)
                    print("last_flag = ",last_flag," move1")

                elif rotation_mode == "blue" and (last_flag == 1 or last_flag == 7):
                    # basic.move(30, -20)
                    gyro_testUNO.straightening(throttle, 10)
                    print("last_flag = ",last_flag," move2")

                elif rotation_mode == "orange" and (last_flag == 1 or last_flag == 7):
                    # basic.move(30, -30)
                    gyro_testUNO.straightening(throttle, 10)
                    print("last_flag = ",last_flag," move3")

                elif rotation_mode == "orange" and (last_flag == 2 or last_flag == 8):
                    # basic.move(30, 20)
                    gyro_testUNO.straightening(throttle, -5)
                    print("last_flag = ",last_flag," move4")

                else:
                    gyro_testUNO.straightening(throttle, 0)
                # gyro_testUNO.straightening(throttle, 0)
            else:
                gyro_testUNO.straightening(throttle, 0)

            en_roll = motor.get()[0]
            bias_roll += en_roll - st_roll

        # sign_flag == 4,7,8は壁が近いsign_flag == 5は正面に壁がある
        else:
            yaw = hub.motion.yaw_pitch_roll()[0]
            straight_flag = False
            if sign_flag == 4 or sign_flag == 7 or sign_flag == 8:
                if (
                    abs(yaw) > 50 # 70
                    and motor.get()[0] - gyro_testUNO.straight_rotation <= 1500
                ):
                    if yaw > 0:
                        throttle = throttle - 10
                        steer = -70 # -120
                    elif yaw < 0:
                        throttle = throttle
                        steer = 70 # 120

                if (gyro_testUNO.section_count == 7        #最後の標識があるセクションで
                    and determine_backturn_flag == 0
                    and sign_flag == 7 #赤が見えていて壁が近い
                ):
                    count_check_red = count_check_red + 1

                elif (gyro_testUNO.section_count == 7        #最後の標識があるセクションで
                    and determine_backturn_flag == 0
                    and sign_flag == 8 #緑が見えていて壁が近い
                ):
                    count_check_green = count_check_green + 1

            elif sign_flag == 5:
                throttle = throttle + 10
                if yaw < 0:
                    if yaw > 60:
                        steer = 120
                    else:
                        steer = 120
                else:
                    steer = -1200
                if abs(yaw) < 20:  # おそらく、このパターンは内側だけ
                    if rotation_mode == "orange":
                        steer = -120
                        throttle = throttle - 10
                    elif rotation_mode == "blue":
                        steer = 120
                        throttle = throttle - 10

            elif sign_flag == 6:
                pass

            elif sign_flag == 1:  # red
                bias_roll = 0
                info_yaw = yaw / 5

                if (gyro_testUNO.section_count == 7        #最後の標識があるセクションで、== 7
                    and determine_backturn_flag == 0
                ):
                    count_check_red = count_check_red + 1

                if (
                    yaw > 20
                    and motor.get()[0] - gyro_testUNO.straight_rotation >= 360 * 4
                ):
                    print("paturn 1")
                    throttle = throttle + 10
                    steer = steer - 70
                    if steer < -3:
                        steer = -3

                elif (
                    yaw >= 30
                    and yaw <= 180
                    and motor.get()[0] - gyro_testUNO.straight_rotation < 360 * 3
                    and rotation_mode == "blue"
                    and gyro_testUNO.past_change == 0
                ):
                    print("paturn 2")
                    if yaw > 85:  # 反時計周りで赤を読んだときヨウ角が85度以上(=曲がる直前で先に赤が見えている状況)
                        throttle = throttle + 10
                        steer = steer + 10
                    else:
                        throttle = throttle + 10
                        steer = steer + 20

                if (
                    yaw > -5
                    and motor.get()[0] - gyro_testUNO.straight_rotation < 360 * 3
                    and rotation_mode == "orange"
                    and gyro_testUNO.past_change == 0
                ):
                    print("paturn 3")
                    throttle = throttle #-20
                    steer = steer - 30
                    if steer < 10:
                        steer = 10
                    pass

                if (
                    yaw < 0
                    and yaw > -60
                    and steer == 0
                    and motor.get()[0] - gyro_testUNO.straight_rotation > 360 * 3
                ):
                    print("paturn 4")
                    steer = 30

            elif sign_flag == 2:  # green
                if (gyro_testUNO.section_count == 7        #最後の標識があるセクションで、== 7
                    and determine_backturn_flag == 0
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
                    throttle = throttle # -20
                    steer = steer + 30  # +30
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

            if throttle < 5:
                throttle = 5
            if straight_flag:
                gyro_testUNO.straightening(throttle, 0)
            else:
                basic.move(throttle, steer + info_yaw)

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

        # 角を曲がるときに奥に何が見えているかで操作量を決めている
        if determine_backturn_flag != 1:
            if blue_camera:  # 左回り
                if (over_sign % 10) == 0:  # 奥に
                    if(over_sign >= 20):
                        go_angle = 100 # 0
                    elif(over_sign >= 10):
                        go_angle = 600
                    else:
                        go_angle = 300
                    if gyro_testUNO.change_steer(30, new_rot, go_angle, steer, running_backturn_flag):
                        print("none1", over_sign)
                        last_run = motor.get()[0]
                        last_over_sign = over_sign
                        gyro_testUNO.sign_count = 0
                        last_flag = 0
                        print("section_count:", gyro_testUNO.section_count)

                elif (over_sign % 10) == 1:  # 奥に赤が見えている
                    if(over_sign >= 20):
                        go_angle = 300 # 0
                    elif(over_sign >= 10):
                        go_angle = 1400
                    else:
                        go_angle = 800 #500 #1100
                    if gyro_testUNO.change_steer(30, new_rot, go_angle, steer, running_backturn_flag):
                        print("red get1", over_sign)
                        last_run = motor.get()[0]
                        last_over_sign = over_sign
                        gyro_testUNO.sign_count = 0
                        last_flag = 0
                        print("section_count:", gyro_testUNO.section_count)

                elif (over_sign % 10) == 2:  # 奥に緑が見えている
                    if(over_sign >= 20):
                        go_angle = 0
                    elif(over_sign >= 10):
                        go_angle = 500 # 550 300
                    else:
                        go_angle = 330 # 0
                    if gyro_testUNO.change_steer(30, new_rot, go_angle, steer, running_backturn_flag):
                        print("green get1", over_sign)
                        last_run = motor.get()[0]
                        last_over_sign = over_sign
                        gyro_testUNO.sign_count = 0
                        last_flag = 0
                        print("section_count:", gyro_testUNO.section_count)

            elif orange_camera:  # 右回り
                if (over_sign % 10) == 0:  # 奥に
                    if(over_sign >= 20):
                        go_angle = 600
                    elif(over_sign >= 10):
                        go_angle = 100 # 200
                    else:
                        go_angle = 300 # 300
                    if gyro_testUNO.change_steer(30, new_rot, go_angle, steer, running_backturn_flag):
                        print("none2", over_sign)
                        last_run = motor.get()[0]
                        last_over_sign = over_sign
                        gyro_testUNO.sign_count = 0
                        last_flag = 0
                        print("lookred_section_count:", gyro_testUNO.section_count)

                elif (over_sign % 10) == 1:  # 奥に赤が見えている
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

                elif (over_sign % 10) == 2:  # 奥に緑が見えている
                    if(over_sign >= 20):
                        go_angle = 1430
                    elif(over_sign >= 10):
                        go_angle = 300 # 0
                    else:
                        go_angle = 500 # 1100
                    if gyro_testUNO.change_steer(30, new_rot, go_angle, steer, running_backturn_flag):
                        print("green get2", over_sign)
                        last_run = motor.get()[0]
                        last_over_sign = over_sign
                        gyro_testUNO.sign_count = 0
                        last_flag = 0
                        print("lookgreen_section_count:", gyro_testUNO.section_count)

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

        # print("M-L",motor.get()[0] - last_run)
        #yaw = hub.motion.yaw_pitch_roll()[0]
        # print(count_check_red, count_check_green)
        # print(gyro_testUNO.section_count,motor.get()[0] - last_run)
        # print("sign_flag:",sign_flag)
        # print("steer:",steer)

        resetSerialBuffer()
        p_steer = steer

    #絶対角度で0度になるように motor_steer を動かす
    motor_steer.run_to_position(0,5)

