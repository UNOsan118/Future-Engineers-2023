# 2023 obstacle
import hub
class Basic_motion:
    def __init__(self,motor_steer,motor): # 使用するモーターを定義
        self.motor_steer = motor_steer
        self.motor = motor


    def move(self,throttle, steer): # 一定のステアリング値と一定のスピードで走行する関数
        self.motor.run_at_speed(throttle)
        once = False
        count = 0

        if steer > 90:   # 無理な角度にならないように一定以上の値はカットする
            steer = 90
        elif steer < -90:
            steer = -90

        elif steer > 70: # 同様に一定以上の値はカットする
            steer = 70
        elif steer < -70:
            steer = -70

        while True:
            if(self.motor_steer.busy(type=1)): # if motor_steer is moving 
                count = count + 1
                continue
            elif once: # 一度だけ動かすため
                break
            else:
                self.motor_steer.run_to_position(steer) # ステアリングモータの角度を[steer]にする
                once = True


    def stop(self):
        self.motor.brake()
        self.motor_steer.brake()
