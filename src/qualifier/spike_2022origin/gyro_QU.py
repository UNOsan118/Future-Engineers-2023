from basic_motion_QU import Basic_motion_QU # 予選用
import hub
import time

class Gyro_QU(Basic_motion_QU):
    def __init__(self, motor_steer, motor):
        super().__init__(motor_steer, motor)
        self.difference_steer = 0
        self.straight_rotation = -10000  # 曲がってから次のturnゾーンに行くまでに他の線を読まないようにする

        self.motor_steer = motor_steer
        self.motor = motor
        self.past_change = 0  # 0change 1back

        self.section_count = -1
        self.sign_count = 0
        self.turn = 85 # change_steerするときに今の角度をこの角度にする

    # 真っ直ぐ走るためのメソッド
    def straightening(self, throttle, bias):
        st_roll = self.motor.get()[0]
        repair_yaw = hub.motion.yaw_pitch_roll()[0]

        if abs(repair_yaw) <= 30:
            self.difference_steer = int(-1.9 * (repair_yaw + bias)) #1.4
        else:
            self.difference_steer = int(-1.9 * (repair_yaw + bias))

        if self.difference_steer < -52: #40
            self.difference_steer = -52
        elif self.difference_steer > 52:
            self.difference_steer = 52

        super().move(throttle, self.difference_steer)

        return 0


    def QU_change_steer(self, throttle, rot, steer, dist_sensor_right, dist_sensor_left):
        check_line = False
        blue_camera = (rot == 1)
        orange_camera = (rot == 2)
        current_dist = self.motor.get()[0]
        if current_dist - self.straight_rotation >= 2000:

            if blue_camera:
                print("blue get")
                # print("c - s", current_dist - self.straight_rotation)
                self.section_count = self.section_count + 1
                rel_pos = self.motor.get()[0]
                this_angle = rel_pos

                Nonecount = 14
                Distcount = 0

                while dist_sensor_left.get(2)[0] != None or Nonecount < 5:
                    print("while")
                    self.straightening(throttle, 0)
                    this_angle = self.motor.get()[0]
                    if dist_sensor_left.get(2)[0] != None:
                        Nonecount = 0

                    #Noneがノイズで入っても大丈夫なように連続したときのみwhileを抜ける動作
                    if dist_sensor_left.get(2)[0] == None:
                        Nonecount += 1
                    else:
                        Nonecount = 0
                        Distcount = 1

                if Distcount == 0 and dist_sensor_right.get(2)[0] == None: #左壁を避けてない かつ 右Dist反応なし
                    print("straight_get 500")
                    while (this_angle-rel_pos) < 500:
                        self.straightening(throttle, 0)
                        this_angle = self.motor.get()[0]

                elif dist_sensor_right.get(2)[0] != None: #右壁の反応あり
                    print("straight_get 300")
                    while (this_angle-rel_pos) < 300:
                        self.straightening(throttle, 0)
                        this_angle = self.motor.get()[0]
                else:
                    print("else straight_get 200")
                    while (this_angle-rel_pos) < 200:
                        self.straightening(throttle, 0)
                        this_angle = self.motor.get()[0]

                print("-------\n")
                # print("blue get")

                rel_pos = self.motor.get()[0]
                y = hub.motion.yaw_pitch_roll()[0]
                hub.motion.yaw_pitch_roll(self.turn+y)
                self.straight_rotation = self.motor.get()[0]
                check_line = True
                self.past_change = 0

            elif orange_camera:
                print("orange get")
                # print("c - s", current_dist - self.straight_rotation)
                self.section_count = self.section_count + 1
                rel_pos = self.motor.get()[0]
                this_angle = rel_pos

                Nonecount = 14
                Distcount = 0

                while dist_sensor_right.get(2)[0] != None or Nonecount < 5:
                    print("while")
                    self.straightening(throttle, 0)
                    this_angle = self.motor.get()[0]
                    if dist_sensor_right.get(2)[0] != None:
                        Nonecount = 0

                    #Noneがノイズで入っても大丈夫なように連続したときのみwhileを抜ける動作
                    if dist_sensor_right.get(2)[0] == None:
                        Nonecount += 1
                    else:
                        Nonecount = 0
                        Distcount = 1

                if Distcount == 0 and dist_sensor_left.get(2)[0] == None:
                    print("straight_get 500")
                    while (this_angle-rel_pos) < 500:
                        self.straightening(throttle, 0)
                        this_angle = self.motor.get()[0]

                elif dist_sensor_right.get(2)[0] != None:
                    print("straight_get 300")
                    while (this_angle-rel_pos) < 300:
                        self.straightening(throttle, 0)
                        this_angle = self.motor.get()[0]
                else:
                    print("else straight_get 200")
                    while (this_angle-rel_pos) < 200:
                        self.straightening(throttle, 0)
                        this_angle = self.motor.get()[0]

                print("-------\n")
                # print("orange get")

                rel_pos = self.motor.get()[0]
                y = hub.motion.yaw_pitch_roll()[0]
                hub.motion.yaw_pitch_roll(-1*self.turn+y)
                self.straight_rotation = self.motor.get()[0]
                check_line = True
                self.past_change = 0

        return check_line
