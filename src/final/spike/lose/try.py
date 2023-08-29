import hub
import time
import re
from gyro import Gyro
from basic_motion import Basic_motion
print("--device init--")

def move(throttle, steer):
    motor.run_at_speed(throttle)
    once = False
    count = 0
    if steer > 30:
        steer = 30
    elif steer < -30:
        steer = -30

    while True:

        if(motor_steer.busy(type=1)): #if motor_steer is moving
            #print("motor_steer:",self.motor_steer.get(2)[0])
            count = count + 1
            continue
        elif once:
            break
        else:
            motor_steer.run_to_position(steer)
            once = True

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
    motor_steer.mode(3)
    #light_sensor.mode(6)
    time.sleep(2)
    ser.baud(115200)
    time.sleep(1)
    #print("default:",motor_steer.default())
    #time.sleep(100)
    break

hub.motion.yaw_pitch_roll(0)
print(hub.motion.yaw_pitch_roll()[0])

"""
while True:
    y = hub.motion.yaw_pitch_roll()[0]
    if(abs(y) > 5):
        move(15,-1 * y)
    else:
        move(15,0)
"""

def move(throttle, steer):
    motor.run_at_speed(throttle)
    once = False
    count = 0
    if steer > 30:
        steer = 30
    elif steer < -30:
        steer = -30

    while True:

        if(motor_steer.busy(type=1)): #if motor_steer is moving
            #print("motor_steer:",self.motor_steer.get(2)[0])
            count = count + 1
            continue
        elif once:
            break
        else:
            motor_steer.run_to_position(steer)
            once = True

y = hub.motion.yaw_pitch_roll()[0]
coce_mode = 1
throttle = 50

move(30,0)
