from basic_motion import Basic_motion
import hub
import time

class Gyro_remake(Basic_motion):
    def __init__(self, motor_steer, motor):
        super().__init__(motor_steer, motor)
        self.old_destination = 0
        self.difference_steer = 0
        self.direction = 1
        self.destination = 0
        self.straight_rotation = -10000  # 曲がってから次のturnゾーンに行くまでに他の線を読まないようにする

        self.motor_steer = motor_steer
        self.motor = motor
        self.past_change = 0  # 0change 1back

        self.section_count = -1
        self.sign_count = 0
        self.turn = 84 # change_steerするときに今の角度をこの角度にする

    # 真っ直ぐ走るためのメソッド
    def straightening(self, throttle, bias):
        st_roll = self.motor.get()[0]
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

    # 角でヨウ角を更新するメソッド
    def change_steer(self, throttle, rot, go_angle, steer):
        check_line = False
        blue_camera = (rot == 1)
        orange_camera = (rot == 2)
        current_dist = self.motor.get()[0]
        #print("c-s", current_dist-self.straight_rotation)
        if current_dist - self.straight_rotation >= 2100:

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

#予選用。青周りしか作っていないので橙も作る必要あり。あといらんとこの削除
    def QU_change_steer(self, throttle, rot, go_angle, steer,dist_sensor_right,dist_sensor_left):
        check_line = False
        blue_camera = (rot == 1)
        orange_camera = (rot == 2)
        current_dist = self.motor.get()[0]
        #print("c-s", current_dist-self.straight_rotation)
        if current_dist - self.straight_rotation >= 2100:

            if blue_camera:
                self.section_count = self.section_count + 1
                rel_pos = self.motor.get()[0]
                this_angle = rel_pos

                Nonecount = 0
                Distcount = 0

                while dist_sensor_left.get(2)[0] != None or Nonecount < 5:
                    #print(dist_sensor_left.get(2)[0])
                    #time.sleep(0.5)
                    self.straightening(throttle, 0)
                    this_angle = self.motor.get()[0]

                    #Noneがノイズで入っても大丈夫なように連続したときのみwhileを抜ける動作
                    if dist_sensor_left.get(2)[0] == None:
                        Nonecount += 1
                        #print(Nonecount)
                    else:
                        Nonecount = 0
                        Distcount = 1

                if Distcount == 0 and dist_sensor_right.get(2)[0] == None:
                    print("straight_get")
                    while (this_angle-rel_pos) < 650:
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

