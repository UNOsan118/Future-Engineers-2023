
from basic_motion import Basic_motion
import hub
import time


class Gyro(Basic_motion):
    def __init__(self, motor_steer, motor):
        super().__init__(motor_steer, motor)
        self.old_destination = 0
        self.difference_steer = 0
        # self.light_sensor=light_sensor
        self.direction = 1
        self.destination = 0
        self.straight_rotation = -10000  # 曲がってから次のturnゾーンに行くまでに青線を他の線を読まないようにする

        self.motor_steer = motor_steer
        self.motor = motor
        self.past_change = 0  # 0chnge 1back

        self.section_count = -1
        self.sign_count = 0
        self.turn = 60
        #self.memory_sign = [[0,0],[0,0],[0,0],[0,0]]

    def straightening(self, throttle, bias):
        st_roll = self.motor.get()[0]

        #print("destination: ",self.destination)
        repair_yaw = hub.motion.yaw_pitch_roll()[0]

        if abs(repair_yaw) <= 30:
            self.difference_steer = int(-1.4 * (repair_yaw + bias))
        else:
            self.difference_steer = int(-1.4 * (repair_yaw + bias))

        if self.difference_steer < -40:
            self.difference_steer = -40
        elif self.difference_steer > 40:
            self.difference_steer = 40

        super().move(throttle, self.difference_steer)

        return 0

    def change_steer(self, throttle, rot, go_angle, steer):
        check_line = False
        blue_camera = (rot == 1)
        orange_camera = (rot == 2)
        xx = self.motor.get()[0]

        #terms_light_sensor = (h >  210-130) and ( h < 210+130) and(s > 256) and (s < 1024) and(v >= 0) and (v <= 1023)
        if xx-self.straight_rotation >= 2100:

            if blue_camera:
                self.section_count = self.section_count + 1
                rel_pos = self.motor.get()[0]
                this_angle = rel_pos

                while (this_angle-rel_pos) < go_angle:
                    self.straightening(throttle, 0)
                    this_angle = self.motor.get()[0]

                print("-------\n")
                print("blue get")
                rel_pos = self.motor.get()[0]

                y = hub.motion.yaw_pitch_roll()[0]
                hub.motion.yaw_pitch_roll(self.turn+y)
                self.destination = 0
                self.direction = -1
                self.straight_rotation = self.motor.get()[0]
                check_line = True
                self.past_change = 0

            elif orange_camera:
                self.section_count = self.section_count + 1
                rel_pos = self.motor.get()[0]
                this_angle = rel_pos
                while (this_angle-rel_pos) < go_angle:
                    self.straightening(throttle, 0)
                    this_angle = self.motor.get()[0]

                print("-------\n")
                print("orange get")

                rel_pos = self.motor.get()[0]

                y = hub.motion.yaw_pitch_roll()[0]
                hub.motion.yaw_pitch_roll(-1*self.turn+y)

                self.destination = 0
                self.direction = 1
                self.straight_rotation = self.motor.get()[0]
                check_line = True
                self.past_change = 0

        return check_line

    def back_turn(self, throttle, rot, go_angle, last_flag):
        check_line = False

        blue_camera = (rot == 1)  # 反時計回り
        orange_camera = (rot == 2)  # 時計回り
        xx = self.motor.get()[0]
        # print("angle",xx)
        #terms_light_sensor = (h >  210-130) and ( h < 210+130) and(s > 256) and (s < 1024)
        if xx-self.straight_rotation >= 2200:

            if blue_camera:
                print("-------\n")
                print("blue get_back")
                self.destination = 0
                self.direction = -1

                self.section_count = self.section_count + 1
                self.sign_count = 0
                rel_pos = self.motor.get()[0]
                this_angle = rel_pos
                start = time.ticks_us()

                while (this_angle-rel_pos) <= go_angle:
                    if last_flag == 1:
                        self.straightening(65, 5)
                    else:
                        self.straightening(65, -10)
                    this_angle = self.motor.get()[0]
                    end = time.ticks_us()
                    if (end-start)/1000 >= 3000:
                        break

                y = hub.motion.yaw_pitch_roll()[0]
                hub.motion.yaw_pitch_roll(self.turn+y)
                start = time.ticks_us()

                while hub.motion.yaw_pitch_roll()[0] >= 0:
                    # print("--d_steer--",d_steer)
                    super().move(-70, 120)
                    end = time.ticks_us()
                    if (end-start)/1000 >= 3000:
                        break
                rel_pos = self.motor.get()[0]
                if last_flag == 1:
                    self.back_dist = -800
                else:
                    self.back_dist = -1200

                while self.motor.get()[0]-rel_pos >= self.back_dist:
                    super().move(-70, 0)
                    end = time.ticks_us()
                    if (end-start)/1000 >= 4000:
                        break
                self.straight_rotation = self.motor.get()[0]
                rel_pos = self.motor.get()[0]
                while self.motor.get()[0]-rel_pos <= 400:
                    super().move(50, 0)
                check_line = True
                self.past_change = 1

            elif orange_camera:
                print("-------\n")
                print("orange get_back")
                self.destination = 0
                self.direction = 1

                self.section_count = self.section_count + 1
                self.sign_count = 0
                rel_pos = self.motor.get()[0]
                this_angle = rel_pos
                start = time.ticks_us()

                while (this_angle-rel_pos) <= go_angle:
                    if last_flag == 2:
                        self.straightening(65, -5)
                    else:
                        self.straightening(65, 10)
                    this_angle = self.motor.get()[0]
                    end = time.ticks_us()
                    if (end-start)/1000 >= 3000:
                        break

                y = hub.motion.yaw_pitch_roll()[0]
                hub.motion.yaw_pitch_roll(-1*self.turn+y)

                start = time.ticks_us()

                while hub.motion.yaw_pitch_roll()[0] <= 0:
                    # print("--d_steer--",d_steer)
                    super().move(-70, -120)
                    end = time.ticks_us()
                    if (end-start)/1000 >= 3000:
                        break
                rel_pos = self.motor.get()[0]

                if last_flag == 2:
                    self.back_dist = -800
                else:
                    self.back_dist = -1200

                while self.motor.get()[0]-rel_pos >= self.back_dist:
                    super().move(-70, 0)
                    end = time.ticks_us()
                    if (end-start)/1000 >= 4000:
                        break
                self.straight_rotation = self.motor.get()[0]
                rel_pos = self.motor.get()[0]
                while self.motor.get()[0]-rel_pos <= 400:
                    super().move(50, 0)
                check_line = True
                self.past_change = 1

        return check_line

    def change_steer2(self, throttle, rot, go_angle, steer):
        check_line = False
        blue_camera = (rot == 1)
        orange_camera = (rot == 2)
        xx = self.motor.get()[0]
        #terms_light_sensor = (h >  210-130) and ( h < 210+130) and(s > 256) and (s < 1024) and(v >= 0) and (v <= 1023)
        if xx-self.straight_rotation >= 2200:

            if blue_camera or orange_camera:

                rel_pos = self.motor.get()[0]
                this_angle = rel_pos
                while (this_angle-rel_pos) < go_angle:
                    super().move(throttle, 0)
                    this_angle = self.motor.get()[0]

                while abs(hub.motion.yaw_pitch_roll()[0]) <= 80:
                    if blue_camera:
                        super().move(throttle, -125)
                    elif orange_camera:
                        super().move(throttle, 125)
                super().move(20, 0)
                self.section_count = self.section_count + 1

            if blue_camera:
                print("-------\n")
                print("blue get")

                hub.motion.yaw_pitch_roll(
                    self.turn+(hub.motion.yaw_pitch_roll()[0]))
                self.direction = -1
                self.straight_rotation = self.motor.get()[0]
                check_line = True

            elif orange_camera:
                print("-------\n")
                print("orange get")

                hub.motion.yaw_pitch_roll(-1*self.turn +
                                        (hub.motion.yaw_pitch_roll()[0]))
                self.direction = 1
                self.straight_rotation = self.motor.get()[0]
                check_line = True

        return check_line
