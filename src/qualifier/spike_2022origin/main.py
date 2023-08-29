import hub # 予選用
import time
import re
from gyro_QU import Gyro_QU
from basic_motion_QU import Basic_motion_QU

print("--device init--")

# デバイスの取得
while True:
    motor = hub.port.C.motor
    motor_steer = hub.port.E.motor
    ser = hub.port.D
    center_button = hub.button.center

    # 距離センサ追加
    dist_sensor_right = hub.port.B.device
    dist_sensor_left = hub.port.F.device

    if ser == None or motor == None or motor_steer == None:
        print("Please check port!!")
        time.sleep(1)
        continue
    motor.mode(2)
    ser.mode(hub.port.MODE_FULL_DUPLEX)
    motor_steer.mode(2)

    dist_sensor_right.mode(1)
    dist_sensor_left.mode(1)

    time.sleep(2)
    ser.baud(115200)
    time.sleep(1)
    break

gyro = Gyro_QU(motor_steer, motor)
basic = Basic_motion_QU(motor_steer, motor)
st_roll = 0

# シリアルバッファの中を空にする


def resetSerialBuffer():
    while True:
        reply = ser.read(10000)
        if reply == b"":
            break


ser_size = 15

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

    count = 0
    bias_roll = 0
    last_run = 1000000  # 最後の切り返しからどれだけ進んだのか記録

    sign_flag = 0
    last_flag = 0

    side_flag = 0

    done_firstsec = False
    rotation_mode = ""

    # ボタンが押されるまで始まらない
    while not(center_button.is_pressed()):
        pass

    hub.motion.yaw_pitch_roll(0)
    while True:
        cmd = ""
        # 三周終わった時
        if (gyro.section_count == 11) and (
            (motor.get()[0] - last_run >= 2100)
            # or (motor.get()[0] - last_run >= 1000 and (rot == 1 or rot == 2))
        ):
            basic.stop()
            break
        side_flag = 0

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

                steer = int(cmd_list[0].split(",")[0])
                throttle = int(cmd_list[0].split(",")[1])

                rot = int(cmd_list[0].split(",")[3])

                side_flag = int(cmd_list[0].split(",")[4])

                if (int(sign_flag) != int(cmd_list[0].split(",")[2])) and (
                    sign_flag == 1 or sign_flag == 2
                ):
                    last_flag = sign_flag
                    section_count = gyro.section_count
                    sign_count = gyro.sign_count

                sign_flag = int(cmd_list[0].split(",")[2])
                break

        # 右回りか左回りかを確定させる
        if rotation_mode == "":
            if rot == 1:
                rotation_mode = "blue"
            elif rot == 2:
                rotation_mode = "orange"

        # 標識を何も認識していない時は0で、認識している時は0以外を返すようにしている
        if sign_flag == 0 or sign_flag == 3:
            throttle = 40
            gyro.straightening(throttle, 0)

        # sign_flag == 4は壁が近いときsign_flag == 5は壁が正面にあるとき
        else:
            yow = hub.motion.yaw_pitch_roll()[0]
            straight_flag = False
            if sign_flag == 4:
                en_roll = motor.get()[0]
                preset_interval = en_roll - st_roll
                # print("preset_interval", preset_interval)
                if abs(yow) > 20:
                    if yow > 0:
                        steer = -110
                        # print("right wall")
                        # if preset_interval <= 1200 and preset_interval >= 400:
                        #    hub.motion.yaw_pitch_roll(15)
                        #    gyro.straightening(throttle, 0)
                        #    print("right preset yaw")
                    elif yow < 0:
                        steer = 110
                        # print("left wall")
                        # if preset_interval <= 1200 and preset_interval >= 400:
                        #    hub.motion.yaw_pitch_roll(-15)
                        #    gyro.straightening(throttle, 0)
                        #    print("left preset yaw")
                    else:
                        pass
            elif sign_flag == 5:
                throttle = throttle
                if yow < 0:
                    print("front wall avoid right")
                    steer = 120
                else:
                    print("front wall avoid left")
                    steer = -120
                if abs(yow) < 20:  # おそらく、このパターンは内側だけ
                    if rotation_mode == "orange":
                        steer = -120
                        throttle = throttle - 10
                    elif rotation_mode == "blue":
                        steer = 120
                        throttle = throttle - 10
            elif sign_flag == 6:
                pass

                info_yow = -1 * yow / 5
            info_yow = 0

            if throttle < 5:
                throttle = 5
            if straight_flag:
                gyro.straightening(throttle, 0)
            else:
                basic.move(throttle, steer + info_yow)

        # ゴール直前じゃない
        if gyro.section_count < 10:
            if gyro.QU_change_steer(
                30, rot, steer, dist_sensor_right, dist_sensor_left
            ):
                st_roll = motor.get()[0]
                gyro.sign_count = 0
                print("section_count:", gyro.section_count)

        # ゴール直前だったらlast_runを取得する
        else:
            if gyro.QU_change_steer(
                30, rot, steer, dist_sensor_right, dist_sensor_left
            ):
                st_roll = motor.get()[0]
                last_run = motor.get()[0]
                gyro.sign_count = 0
                print("section_count:", gyro.section_count)

        # if(gyro.section_count == 0):
            # throttle = 30

        print(steer)


        resetSerialBuffer()
        p_steer = steer
