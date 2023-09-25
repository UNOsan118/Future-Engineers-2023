#ステアリングモーターの角度を０度に調整する
#機体を持ち上げてやったほうが良い
import hub
import time
import re
from gyro_testUNO import Gyro_remake
from basic_motion_testUNO import Basic_motion
print("--device init--")

#初期設定
while True:
    motor = hub.port.C.motor
    motor_steer = hub.port.E.motor
    if motor_steer == None:
        print("Please check port!!")
        time.sleep(0.5)
        continue
    motor_steer.mode(3) #mode(3)でモーターの絶対角度を参照
    break

#現在の motor_steer の絶対角度を preset する（これをしないと run_to_position が働かない）
abs_pos = motor_steer.get()[0]
motor_steer.preset(abs_pos)

basic = Basic_motion(motor_steer, motor)
#絶対角度で0度になるように motor_steer を動かす
motor_steer.run_to_position(0,5)

print("OK!")
"""
time.sleep(5)
while 1:
    y = hub.motion.yaw_pitch_roll()[0]
    print("y:",y)
    time.sleep(0.1)
"""

