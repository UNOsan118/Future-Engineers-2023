# 2023 obstacle
from basic_motion_testUNO import Basic_motion
import hub
import time

class Gyro_remake(Basic_motion):
    def __init__(self, motor_steer, motor): # Initial Settings, Definition of variables to be used
        super().__init__(motor_steer, motor) 
        self.difference_steer = 0 
        self.direction = 1 
        self.destination = 0
        self.straight_rotation = -10000  # Avoid reading other lines from the turn to the next TURN zone.

        self.motor_steer = motor_steer
        self.motor = motor
        self.past_change = 0  # 0change, 1back

        self.section_count = -1
        self.sign_count = 0
        self.turn = 85    # Spike Hub gyro sensor updated values when turning a corner
        self.turn2 = 87   # Use different values for clockwise and semi-clockwise


    # The function to run in the specified direction
    def straightening(self, throttle, bias):
        st_roll = self.motor.get()[0]
        repair_yaw = hub.motion.yaw_pitch_roll()[0] # Get current Hub's yaw angle

        # Calculate the steering value from the current Hub's yaw angle and the direction you want to face
        self.difference_steer = int(-2 * (repair_yaw + bias))  

        # Cut values to avoid unreasonable angles
        if self.difference_steer < -55:
            self.difference_steer = -55
        elif self.difference_steer > 55:
            self.difference_steer = 55

        super().move(throttle, self.difference_steer)

        return 0


    # Method to update yaw angle at the corner
    def change_steer(self, throttle, rot, go_angle, steer ,running_backturn_flag):
        check_line = False

        blue_camera = (rot == 1)
        orange_camera = (rot == 2)

        current_dist = self.motor.get()[0]
        if (current_dist - self.straight_rotation >= 2100) and (running_backturn_flag!=1):
            # Recognize the blue line = When the semi-clockwise rotation
            if blue_camera:
                print("blue_get")
                self.section_count = self.section_count + 1
                rel_pos = self.motor.get()[0]
                this_angle = rel_pos

                # Go straight and then turn. The amount of straight-ahead depends on the color of the sign you see before you turn.
                while (this_angle-rel_pos) < go_angle:
                    self.straightening(throttle, 0)
                    this_angle = self.motor.get()[0]

                # Printed when go_angle amount is advanced.
                print("finish go_angle")
                rel_pos = self.motor.get()[0]

                # Hub's angle update
                y = hub.motion.yaw_pitch_roll()[0]
                hub.motion.yaw_pitch_roll(self.turn+y) 
                self.destination = 0
                self.direction = -1
                self.straight_rotation = self.motor.get()[0]
                check_line = True
                self.past_change = 0

            # The orange line read = clockwise (from this point on, the processing is the same as when blue is recognized)
            elif orange_camera:
                print("orange_get")
                self.section_count = self.section_count + 1
                rel_pos = self.motor.get()[0]
                this_angle = rel_pos
                while (this_angle-rel_pos) < go_angle:
                    self.straightening(throttle, 0)
                    this_angle = self.motor.get()[0]

                print("finish go_angle")
                rel_pos = self.motor.get()[0]

                y = hub.motion.yaw_pitch_roll()[0]
                hub.motion.yaw_pitch_roll(-1*self.turn2+y)

                self.destination = 0
                self.direction = 1
                self.straight_rotation = self.motor.get()[0]
                check_line = True
                self.past_change = 0

        return check_line

