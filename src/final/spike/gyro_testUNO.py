# 2023 obstacle
from basic_motion_testUNO import Basic_motion
import hub
import time

class Gyro_remake(Basic_motion):
    def __init__(self, motor_steer, motor): # 初期設定, 使用する変数の定義
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
        self.turn = 85    # 角を曲がる際のSpike Hubジャイロセンサの更新値
        self.turn2 = 87   # 時計回りと半時計周りで別の値を用いる


    # 任意の方向を向いて走る関数
    def straightening(self, throttle, bias):
        st_roll = self.motor.get()[0]
        repair_yaw = hub.motion.yaw_pitch_roll()[0] # 現在のHubのヨー角を取得

        # 現在のHubのヨー角と向きたい方向からステアリング値を計算
        self.difference_steer = int(-2 * (repair_yaw + bias))  

        # 無理な角度にならないよう値をカット
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
            # 青色の線を認識 = 半時計周りのとき
            if blue_camera:
                print("blue_get")
                self.section_count = self.section_count + 1
                rel_pos = self.motor.get()[0]
                this_angle = rel_pos

                # 直進してから曲がる。曲がる先に見えている標識の色によって直進する量は変わる。
                while (this_angle-rel_pos) < go_angle:
                    self.straightening(throttle, 0)
                    this_angle = self.motor.get()[0]

                # Printed when go_angle amount is advanced.
                print("finish go_angle")
                rel_pos = self.motor.get()[0]

                # Hubの角度更新
                y = hub.motion.yaw_pitch_roll()[0]
                hub.motion.yaw_pitch_roll(self.turn+y) 
                self.destination = 0
                self.direction = -1
                self.straight_rotation = self.motor.get()[0]
                check_line = True
                self.past_change = 0

            # オレンジ色の線を読んだ = 時計周りのとき (これ以降、青色を認識した時と同様の処理)
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

