# ここにコードを書いてね :-)
import hub
import time
import re
from gyro import Gyro
from basic_motion import Basic_motion
print("--device init--")

while True:
    motor = hub.port.C.motor
    motor_steer = hub.port.E.motor
    ser = hub.port.D
    center_button = hub.button.center
    #light_sensor = hub.port.A.device
    if ser == None or motor == None or motor_steer == None:
        print("Please check port!!")
        time.sleep(1)
        continue
    motor.mode(2)
    ser.mode(hub.port.MODE_FULL_DUPLEX)
    motor_steer.mode(2)
    #light_sensor.mode(6)
    time.sleep(2)
    ser.baud(115200)
    time.sleep(1)
    #print("default:",motor_steer.default())
    #time.sleep(100)
    break

gyro = Gyro(motor_steer,motor)
basic = Basic_motion(motor_steer,motor)
def resetSerialBuffer():
    while True:
        reply = ser.read(10000)
        #print(reply)
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
    print("elapse_time: {}[ms]".format((end-start)/1000))
    print("--waiting RasPi--")
    end_flag = False
    throttle = 0
    steer = 0
    p_steer = 0
    rot = 0

    count = 0
    bias_roll=0
    last_run=1000000 #最後の切り返しからどれだけ進んだのか記録

    sign_flag = 0
    last_flag = 0

    side_flag = 0

    memory_sign = [[0,0],[0,0],[0,0],[0,0]]

    done_firstsec = False
    rotation_mode = ""
    while not(center_button.is_pressed()):
        pass
    hub.motion.yaw_pitch_roll(0)
    while True:
        cmd = ""
        if (gyro.section_count == 11) and (motor.get()[0]-last_run >= 2100):
            basic.stop()
            break
        side_flag = 0
        while True:
            #time.sleep(50/1000)
            reply = ser.read(ser_size - len(cmd))
            reply = reply.decode("utf-8")
            #print("reply: ",reply)
            cmd = cmd + reply
            #send distance
            '''distance = dist_sensor.get(2)[0]
            time.sleep(1/1000)
            #print("Distance: {}[cm]".format(distance))
            #time.sleep(1)
            if distance:
                ser.write("{:3d}@".format(distance))
            else:
                ser.write("{:3d}@".format(0))'''

            if len(cmd) >= ser_size and cmd[-1:] == "@":
                #print(cmd)
                cmd_list = cmd.split("@")
                if len(cmd_list) != 2:
                    print(len(cmd_list))
                    cmd = ""
                    continue


                steer = int(cmd_list[0].split(",")[0])
                throttle = int(cmd_list[0].split(",")[1])

                rot = int(cmd_list[0].split(",")[3])

                side_flag = int(cmd_list[0].split(",")[4])

                #print("sectioncount:",gyro.section_count)
                #print("done_firstsec:",done_firstsec)
                if (int(sign_flag) !=  int(cmd_list[0].split(",")[2]))and(sign_flag ==1 or sign_flag == 2):
                    last_flag=sign_flag
                    section_count = gyro.section_count
                    sign_count = gyro.sign_count

                    if section_count >= 0 and section_count < 4 and gyro.sign_count < 2:
                        memory_sign[section_count][sign_count] = sign_flag
                        gyro.sign_count = gyro.sign_count + 1
                        start = time.ticks_us()
                        print("sec,signcount:",gyro.section_count,gyro.sign_count)
                        print("sign_flag,last_flag;",sign_flag,last_flag)
                        print("memory_sign:",memory_sign)
                        end = time.ticks_us()
                        print("elapse_time: {}[us]", end-start)

                sign_flag = int(cmd_list[0].split(",")[2])
                break
        if rotation_mode == "":
            if rot == 1:
                rotation_mode = "blue"
            elif rot == 2:
                rotation_mode = "orange"
        if end_flag:
            print("inendflag")
            motor.brake()
            motor_steer.barke()
            break
        #標識を何も認識していない時は0で、認識している時は0以外を返すようにしている
        if sign_flag == 0 or sign_flag == 3:
            if bias_roll>=600:
                bias_roll=0
            st_roll=motor.get()[0]
            if motor.get()[0] - gyro.straight_rotation <= 360 * 0.8 and gyro.past_change == 0:
                if rotation_mode == "blue" and last_flag == 2:
                    basic.move(50,-30)
                elif rotation_mode == "orange" and last_flag == 1:
                    basic.move(50,30)
                #elif rotation_mode == "blue" and last_flag == 1 and motor.get()[0] - gyro.straight_rotation <= 360 * 1:
                #    basic.move(50,-10)
                #elif rotation_mode == "orange" and last_flag == 2 and motor.get()[0] - gyro.straight_rotation <= 360 * 1:
                #    basic.move(50, 10)
                else:
                    gyro.straightening(throttle,0)
            else:
                gyro.straightening(throttle,0)

            en_roll=motor.get()[0]
            bias_roll+=en_roll-st_roll

            #gyro.change_steer()
        else:
            yow = hub.motion.yaw_pitch_roll()[0]
            straight_flag = False
            #print("yow,difference",yow,motor.get()[0] - gyro.straight_rotation)
            if sign_flag == 4:
                if abs(yow) > 70:
                    if yow > 0:
                        steer = -100
                    elif yow < 0:
                        steer = 100
            elif sign_flag == 5:
                throttle = throttle + 10
                if yow < 0:
                    steer = 120
                else:
                    steer = -120
                if abs(yow) < 20:#おそらく、このパターンは内側だけ
                    if rotation_mode == "orange":
                        steer = -120
                        throttle = throttle - 10
                    elif rotation_mode == "blue":
                        steer = 120
                        throttle = throttle - 10
            elif sign_flag == 6:
                """if rotation_mode == "blue" and yow < 60:
                    steer = p_steer
                elif rotation_mode == "orange" and yow > -60:
                    steer = p_steer"""
                pass
            elif sign_flag == 1 :#red
                bias_roll=0
                info_yow = yow/5
                """if yow > 48 and motor.get()[0] - gyro.straight_rotation >= 360 * 3:
                    steer = steer  - 50
                    if steer < 0:
                        steer = 0"""
                if yow > 20 and motor.get()[0] - gyro.straight_rotation >= 360 * 4:
                    throttle = throttle + 10
                    steer = steer - 50
                    if steer < 0:
                        steer = 0
                elif yow >= 30 and yow <= 180 and motor.get()[0] - gyro.straight_rotation < 360 * 3 and rotation_mode == "blue" and gyro.past_change == 0:
                    if yow > 85:
                        throttle = throttle + 15
                        steer = steer - 10
                    else:
                        throttle = throttle + 10
                    steer = steer + 20

                    #if steer < 10:
                        #steer = 10
                    #throttle = throttle + 20
                """elif yow > 105 and motor.get()[0] - gyro.straight_rotation < 360 * 3:
                    if steer > 80:
                        steer = steer
                    else:
                        steer = 0
                    throttle = throttle + 30"""
                if yow > -5 and motor.get()[0] - gyro.straight_rotation < 360 * 3 and rotation_mode == "orange" and gyro.past_change == 0:
                    throttle = throttle - 20
                    steer = steer - 30
                    if steer < 0:
                        steer = 0
                    pass
                #if yow < -15 and  yow > -50 and steer > 0:
                    #steer = (-1 * yow) + steer
                if yow < 0 and yow > -60 and steer == 0 and motor.get()[0] - gyro.straight_rotation > 360 * 3:
                    steer = 50
            elif sign_flag == 2: #green
                bias_roll=0
                """if yow < -48 and motor.get()[0] - gyro.straight_rotation >= 360 * 3:
                    steer = steer + 70
                    if steer > 0:
                        steer = 0"""
                if yow < -20 and motor.get()[0] - gyro.straight_rotation >= 360 * 4:
                    throttle = throttle + 10
                    steer = steer + 50
                    if steer > 0:
                        steer = 0

                elif yow<= -30 and yow >= -180 and motor.get()[0] - gyro.straight_rotation < 360 * 3 and rotation_mode == "orange" and gyro.past_change == 0:
                    if yow > -85:
                        throttle = throttle + 15
                        steer = steer + 10
                    else:
                        throttle = throttle + 10
                    steer = steer - 20
                    #if steer >= -10:
                        #steer = -10
                    #throttle = throttle + 20
                """elif yow < -105 and motor.get()[0] - gyro.straight_rotation < 360 * 3:
                    #steer = steer - 10
                    if steer < - 80:
                        steer = steer
                    else:
                        steer = 0
                    throttle = throttle + 30"""
                #if yow > 15 and  yow < 50 and steer < 0 :
                    #steer = (-1 * yow) + steer
                if yow < 5 and motor.get()[0] - gyro.straight_rotation < 360 * 3 and rotation_mode == "blue" and gyro.past_change == 0:
                    throttle = throttle - 20
                    steer = steer + 30
                    if steer > 0:
                        steer = 0
                    pass
                if yow > 0 and yow < 60 and steer == 0 and motor.get()[0] - gyro.straight_rotation > 360 * 3:
                    steer = -50
                info_yow = -1 * yow/5
            info_yow = 0
            #print("steer",steer)
            if throttle < 5:
                throttle = 5
            if straight_flag:
                gyro.straightening(throttle,0)
            else:
                basic.move(throttle,steer + info_yow)
        """h = light_sensor.get(2)[0]
        s = light_sensor.get(2)[1]
        v = light_sensor.get(2)[2]"""
        blue_camera = (rot == 1)
        orange_camera = (rot == 2)
        #terms_light_sensor = (h >  210-130) and ( h < 210+130) and(s > 256) and (s < 1024) and(v >= 0) and (v <= 1023)

        """
        if gyro.change_steer(40,rot,0):
            gyro.sign_count = 0
            print("section_count:",gyro.section_count)
                #print(memory_sign)
        """

        """
        #back_turn(前進のスピード,rot,前進する距離)

        if gyro.section_count < 10:#ゴール直前じゃない
            if sign_flag == 1 or sign_flag == 2:#ブロックがみえる

                if rot == 1:#反時計回り
                    if sign_flag ==1:#みえるブロックが赤
                        if gyro.back_turn(50,rot,2200):
                            gyro.sign_count = 0
                            print("section_count:",gyro.section_count)

                    else:#みえるブロックが緑
                        if gyro.back_turn(50,rot,1500):
                            gyro.sign_count = 0
                            print("section_count:",gyro.section_count)

                elif rot==2:#時計回り
                    if sign_flag ==2:#みえるブロックが緑
                        if gyro.back_turn(50,rot,2200):
                            gyro.sign_count = 0
                            print("section_count:",gyro.section_count)

                    else:#みえるブロックが赤
                        if gyro.back_turn(50,rot,1500):
                            gyro.sign_count = 0
                            print("section_count:",gyro.section_count)
            else:
                if side_flag == 0 and ((rot == 1 and last_flag == 2 and sign_flag != 1) or (rot == 2 and last_flag == 1 and sign_flag != 2)):
                    if gyro.change_steer(50,rot,400,steer):
                        gyro.sign_count = 0
                        print("section_count:",gyro.section_count)
                else:
                    if gyro.change_steer(20,rot,0,steer):
                        gyro.sign_count = 0
                        print("section_count:",gyro.section_count)
                #print(memory_sign)
        else:
            if gyro.back_turn(50,rot,1700):
                last_run=motor.get()[0]
                gyro.sign_count = 0
                print("section_count 11!!")
    """
        if gyro.section_count < 10:#ゴール直前じゃない
            if sign_flag != 0:
                if gyro.change_steer(43,rot,400,steer):
                    gyro.sign_count = 0
                    print("section_count:",gyro.section_count)

            else:
                if gyro.change_steer(43,rot,400,steer):
                    gyro.sign_count = 0
                    print("section_count:",gyro.section_count)

        else:
            if gyro.change_steer(43,rot,400,steer):
                last_run=motor.get()[0]
                gyro.sign_count = 0
                print("section_count 11!!")


        """
        if rot==1:
            if last_flag==0 or last_flag==1:
                print("1")
                if gyro.change_steer(20,rot)==True:
                    bias_roll=100000
            elif last_flag==2:
                print("2")
                if gyro.buck_turn(20,rot)==True:
                    bias_roll=100000
        elif rot==2:
            if last_flag==0 or last_flag==1:
                print("3")
                if gyro.back_turn(20,rot)==True:
                    bias_roll=100000
            elif last_flag==2:
                print("4")
                if gyro.change_steer(20,rot)==True:
                    bias_roll=100000
        """

        resetSerialBuffer()
        p_steer = steer



