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
    # Variables related to the control amount of the motor
    throttle = 0 # Rotation speed of the drive motor
    steer = 0 # Steering motor angle

    # Variables related to the direction of travel
    rot = 0 # Record the direction of travel (clockwise or counterclockwise)
    rotation_mode = "" # Record "rot" as str type "blue" or "orange"

    # Variables for visible signs
    sign_flag = 0 # Information about the currently visible sign and wall
    last_sign_flag = 0 # The value of the previous sign_flag
    over_sign = 0 # Record the signs that can be seen ahead of the turn.
    last_over_sign = 0 # Value of one previous over_sign

    # Variables on backturns
    determine_backturn_flag = 0 # Used to determine whether to make a back turn 0:not yet determined.  1:need to backturn.  2:determined.
    running_backturn_flag = 0 # Indicates back-turn status 0:still not backturn.  1:backturn now.  2:backturned.
    backturn_orientation = -120 # Steering motor angle during the back turn
    determine_backturn_sec = 0 # Section to decide whether to make a backturn or not.
    new_rot = 0 # "rot" after back turn

    # Variables to record the placement of signs in each section
    count_check_red = 0 # Increase while red signs are visible
    count_check_green = 0 # Increase while green signs are visible
    simple_memory_sign = [0, 0, 0, 0] # Array to record the color placement of the signs in each section
    first_memory_flag = 0 # Record the first sign seen in each section
    determine_memory_flag = 0 # If the color of the sign is recorded in each section, record this.

    # Variables for recording other information
    memory_M_L = [0, 0, 0, 0] # Record the number of revolutions of the drive motor from the time it starts to turn the corner until the "first_memory_flag" is recorded.
    memory_last_oversign = [100, 100, 100, 100] # Record the "last_over_sign" value for each section

    # Variable to determine if there is a "sign" in the middle of section 1
    sec1_check = 0 # Continuously increasing from the start of driving until the first turn.
    sec1_center_sign_flag = 0 # Record if there is a "sign" in the middle of section 1

    # Variables used for other purposes
    go_angle = 0 # Amount of straight line when turning
    finish_go = 2100 # Number of revolutions of the drive motor from turning the last corner to stopping
    last_run = 1000000  # Record how far you have progressed since the last turnaround.
    info_yaw = 0 # Used to slightly change the angle depending on the yaw angle of the Hub when avoiding signsr

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

        # Record past "over signs
        if (gyro_testUNO.section_count >= 0
            and gyro_testUNO.section_count <= 3
            and memory_last_oversign[gyro_testUNO.section_count] == 100
        ):
            memory_last_oversign[gyro_testUNO.section_count] = last_over_sign

        # Determination of "first_memory_flag
        if (gyro_testUNO.section_count >= 0 
            and gyro_testUNO.section_count <= 3 # When passing through each section for the first time
            and first_memory_flag == 0 # First_memory_flag" has not been determined yet
            and(
                (motor.get()[0] - last_run >= 400      #After some progress from the beginning of the turn.
                and (count_check_red >= 2 or count_check_green >= 2)) # If you see red or green
                or
                (motor.get()[0] - last_run >= 3300)    # When you start to turn and have made some progress
            )
        ):
            memory_M_L[gyro_testUNO.section_count] = motor.get()[0] - last_run 
            if (last_over_sign % 10) != 0:
                first_memory_flag = last_over_sign % 10 + 10 # If you saw some kind of sign just before you turned, that's the first sign you'll see
            else:
                if(count_check_red >= count_check_green):      # If the first thing you see is red.
                    first_memory_flag = 1
                else:                                     # If the first thing you see is green.
                    first_memory_flag = 2
            print(count_check_red, count_check_green, first_memory_flag, last_over_sign)

        # Determination of "simple_memory_sign
        if (gyro_testUNO.section_count >= 1 # After passing through each section
            and gyro_testUNO.section_count <= 4
            and determine_memory_flag == 1
        ):
            print(count_check_red, count_check_green, first_memory_flag)

            if gyro_testUNO.section_count == 1 and sec1_check <= 15: # Determine if there is a sign in the center of the starting section by the amount of increase
                sec1_center_sign_flag = 1
                print("sec1 center sign is here. sec1_check = ", sec1_check)

            if count_check_red >= 2 and count_check_green >= 2: # Recognize both signs
                if first_memory_flag % 10 == 1:              # If the first thing you see is red.
                    simple_memory_sign[gyro_testUNO.section_count - 1] = 3   #red -> green
                else:                                        # If what you see ahead is green.
                    simple_memory_sign[gyro_testUNO.section_count - 1] = 4   #green -> red

            else:                                         # Recognizes only one color sign or When not recognized
                if(count_check_red == 0 and count_check_green == 0): # When not recognized
                    if memory_last_oversign[gyro_testUNO.section_count -1]%10 == 1: # Determined using previous "oversign" values
                        simple_memory_sign[gyro_testUNO.section_count - 1] = 1   # red only
                    elif memory_last_oversign[gyro_testUNO.section_count -1]%10 == 2:
                        simple_memory_sign[gyro_testUNO.section_count - 1] = 2   # green only
                    else:
                        simple_memory_sign[gyro_testUNO.section_count - 1] = 2   # green only

                elif(count_check_red >= count_check_green): # If what you were seeing a lot of is red
                    if first_memory_flag == 12:
                        simple_memory_sign[gyro_testUNO.section_count - 1] = 4   # green -> red
                    else:
                        simple_memory_sign[gyro_testUNO.section_count - 1] = 1   # red only

                else:                                       # If it's green...
                    if first_memory_flag == 11:
                        simple_memory_sign[gyro_testUNO.section_count - 1] = 3   # red -> green
                    else:
                        simple_memory_sign[gyro_testUNO.section_count - 1] = 2   # green only
            print(simple_memory_sign)
            print("----------")

            # Initialize variables for the next decision
            count_check_red = 0
            count_check_green = 0
            first_memory_flag = 0
            determine_memory_flag = 0

        # Determining whether to run in reverse
        if(determine_backturn_flag == 0 and gyro_testUNO.section_count == 7):
            if sec1_center_sign_flag == 1: # When there is a sign in the middle of sec1
                determine_backturn_sec = -1

            elif memory_last_oversign[3]%10 != 0: # When you see the sign for the destination of the turn (only immediately after the turn, as it is excluded if it is in the center)
                determine_backturn_flag = memory_last_oversign[3]%10

            elif ( # When you can't see the sign ahead of the turn, but you're passing on the inside.
                (rotation_mode == "blue" and memory_last_oversign[3] == 10)
                or
                (rotation_mode == "orange" and memory_last_oversign[3] == 20)
            ):
                determine_backturn_sec = -1

            elif ( # When running on the outside
                (rotation_mode == "orange" and memory_last_oversign[3] == 10)
                or
                (rotation_mode == "blue" and memory_last_oversign[3] == 20)
            ):
                if memory_M_L[3] < 1300 or memory_M_L[3] > 2800:
                    determine_backturn_sec = 1
                else:
                    determine_backturn_sec = -1

            else: # When you can't see the walls or the signs
                if memory_M_L[3] < 1300 or memory_M_L[3] > 2800:
                    determine_backturn_sec = 1
                else:
                    determine_backturn_sec = -1

            if determine_backturn_flag == 0: # "determine_backturn_flag" is undecided
                if determine_backturn_sec == 1: # To be determined in the starting section
                    if simple_memory_sign[3] == 1 or simple_memory_sign[3] == 3: # red only or red -> green
                        determine_backturn_flag = 1
                    else:                                                        # green only or green -> red
                        determine_backturn_flag = 2
                else:                           # The decision will be made in the section one before the start section.
                    if simple_memory_sign[2] == 1 or simple_memory_sign[2] == 4: # red only or green -> red
                        determine_backturn_flag = 1
                    else:                                                        # green only or red -> green
                        determine_backturn_flag = 2
            print("determine_backturn_flag: ", determine_backturn_flag)

        # make someone run backwards
        if(gyro_testUNO.section_count == 8 and determine_backturn_flag == 1): # In the section where you should backturn.
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
            # Change the direction of the back turn depending on the sign just beyond the turn.
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

        # From the start to the first turn, keep increasing the variable (the way it is increased determines whether there is a sign in the center of the starting section).
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

                # For the record of the marker, record that the red color or green color is visible.
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
                # For the record of the marker, record that the red color is visible.
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
                # For the record of the marker, record that the green color is visible.
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
            # Changes the amount of straight travel depending on the direction of travel and the color of the sign passed just before.
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

