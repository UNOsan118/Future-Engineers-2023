# 2023 open
from basic_motion_testUNO import Basic_motion
import hub
import time

class Gyro_remake(Basic_motion):
    def __init__(self, motor_steer, motor):
        super().__init__(motor_steer, motor)
        self.old_destination = 0
        self.difference_steer = 0
        self.direction = 1
        self.destination = 0
        self.straight_rotation = -10000  # Avoid reading other lines from the turn to the next TURN zone.

        self.motor_steer = motor_steer
        self.motor = motor
        self.past_change = 0  # 0change,1back

        self.section_count = -1
        self.sign_count = 0
        self.turn = 84
        self.turn2 = 87


    # Methods for running straight
    def straightening(self, throttle, bias):
        st_roll = self.motor.get()[0]
        repair_yaw = hub.motion.yaw_pitch_roll()[0]

        if abs(repair_yaw) <= 30:
            self.difference_steer = int(-2 * (repair_yaw + bias))
            if self.difference_steer < -30:
                self.difference_steer = -30
            elif self.difference_steer > 30:
                self.difference_steer = 30
        else:
            self.difference_steer = int(-1 * (repair_yaw + bias))

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
            if blue_camera:
                print("blue_get")
                self.section_count = self.section_count + 1
                rel_pos = self.motor.get()[0]
                this_angle = rel_pos

                while (this_angle-rel_pos) < go_angle:
                    self.straightening(throttle, 0)
                    this_angle = self.motor.get()[0]

                # Printed when go_angle amount is advanced.
                print("finish go_angle")
                rel_pos = self.motor.get()[0]

                y = hub.motion.yaw_pitch_roll()[0]
                hub.motion.yaw_pitch_roll(self.turn+y)
                self.destination = 0
                self.direction = -1
                self.straight_rotation = self.motor.get()[0]
                check_line = True
                self.past_change = 0

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

