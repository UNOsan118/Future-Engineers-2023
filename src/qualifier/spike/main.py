# 2023 open
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
    end_flag = False
    throttle = 0
    steer = 0
    rot = 0
    over_sign = 0

    go_angle = 0

    bias_roll = 0
    last_run = 1000000  # Record how far you have progressed since the last turnaround.

    sign_flag = 0
    last_flag = 0

    determine_backturn_flag = 0 # 0:not yet determined.  1:need to backturn.  2:determined.
    running_backturn_flag = 0 # 0:still not backturn.  1:backturn now.  2:backturned.
    count_check_red = 0
    count_check_green = 0

    new_rot = 0 

    memory_sign = [[0, 0], [0, 0], [0, 0], [0, 0]]

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

        # Processing to be done in the section to be stopped
        if gyro_testUNO.section_count >= 11:
            if  motor.get()[0] - last_run >= 2450:
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
                sign_flag = int(cmd_list[0].split(",")[2])
                rot       = int(cmd_list[0].split(",")[3])
                over_sign = int(cmd_list[0].split(",")[4])

                if (int(sign_flag) != int(cmd_list[0].split(",")[2])) and (
                    sign_flag == 1 or sign_flag == 2
                ):
                    last_flag = sign_flag
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

                break

        # Determine if you are going right or left.
        if rotation_mode == "":
            if rot == 1:
                rotation_mode = "blue"
            elif rot == 2:
                rotation_mode = "orange"

        # When the sign is not recognized as anything, it returns 0, and when it is recognized, it returns a non-zero value.
        if sign_flag == 0 or sign_flag == 3:
            if bias_roll >= 600:
                bias_roll = 0
            st_roll = motor.get()[0]

            if rotation_mode == "blue":
                gyro_testUNO.straightening(throttle, -6)
            elif rotation_mode == "orange":
                gyro_testUNO.straightening(throttle, 6)
            else:
                gyro_testUNO.straightening(throttle, 0)

            en_roll = motor.get()[0]
            bias_roll += en_roll - st_roll

        # sign_flag == 4,7,8 are close to the wall sign_flag == 5 has a wall in front
        else:
            yaw = hub.motion.yaw_pitch_roll()[0]
            straight_flag = False
             # When close to either left or right wall
            if sign_flag == 4:
                # If the yaw angle of the hub is large, increase the steering value.
                if abs(yaw) > 30 and motor.get()[0] - last_run <= 2100:
                    if yaw > 0:
                        throttle = throttle
                        steer = -60
                    elif yaw < 0:
                        throttle = throttle
                        steer = 60

            elif sign_flag == 7:
                if abs(yaw) > 30 and motor.get()[0] - last_run <= 2300:
                    if yaw > 0:
                        throttle = throttle
                        steer = -60
                    elif yaw < 0:
                        throttle = throttle
                        steer = 60

            # Processing when a wall is visible in front
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

            if throttle < 5:
                throttle = 5
            if straight_flag:
                gyro_testUNO.straightening(throttle, 0)
            else:
                basic.move(throttle, steer)


        blue_camera = rot == 1
        orange_camera = rot == 2
        new_rot = rot

        # The amount of manipulation is determined by what you see in the back when you turn the corner.
        if blue_camera:  # counterclockwise rotation
            if(over_sign >= 20):
                go_angle = 620
            elif(over_sign >= 10):
                go_angle = 920
            else:
                go_angle = 1070

            # Update Hub's yaw angle
            if gyro_testUNO.change_steer(40, new_rot, go_angle, steer, running_backturn_flag):
                print("none1", over_sign)
                last_run = motor.get()[0]
                last_over_sign = over_sign
                gyro_testUNO.sign_count = 0
                print("section_count:", gyro_testUNO.section_count)

        elif orange_camera:  # clockwise rotation
            if(over_sign >= 20):
                go_angle = 920
            elif(over_sign >= 10):
                go_angle = 620
            else:
                go_angle = 1070

            if gyro_testUNO.change_steer(40, new_rot, go_angle, steer, running_backturn_flag):
                print("none2", over_sign)
                last_run = motor.get()[0]
                last_over_sign = over_sign
                gyro_testUNO.sign_count = 0
                print("lookred_section_count:", gyro_testUNO.section_count)

        resetSerialBuffer()

    # After stopping, move motor_steer so that it reaches 0 degrees in absolute angle
    motor_steer.run_to_position(0,5)

