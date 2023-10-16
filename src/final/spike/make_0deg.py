# Adjust the angle of the steering motor to 0 degrees
# It is not a program to be used during the competition.
import hub
import time
import re
from gyro_testUNO import Gyro_remake
from basic_motion_testUNO import Basic_motion
print("--device init--")

# initialization
while True:
    motor = hub.port.C.motor
    motor_steer = hub.port.E.motor
    if motor_steer == None:
        print("Please check port!!")
        time.sleep(0.5)
        continue
    motor_steer.mode(3) # See absolute angle of motor
    break

# Preset the absolute angle of the current motor_steer (run_to_position will not work without this)
abs_pos = motor_steer.get()[0]
motor_steer.preset(abs_pos)

basic = Basic_motion(motor_steer, motor)
# Move motor_steer so that the absolute angle is 0 degrees
motor_steer.run_to_position(0,5)

print("OK!")