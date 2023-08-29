import hub
class Basic_motion:
    def __init__(self,motor_steer,motor):
        self.motor_steer = motor_steer
        self.motor = motor

    def move(self,throttle, steer):
        self.motor.run_at_speed(throttle)
        once = False
        count = 0
        steer = steer * 0.85

        if abs(steer) > 110:#90

            if steer > 110:
                steer = 110
            elif steer < -110:
                steer = -110

        elif steer > 60:
            steer = 60
        elif steer < -60:
            steer = -60

        while True:

            if(self.motor_steer.busy(type=1)): #if motor_steer is moving
                #print("motor_steer:",self.motor_steer.get(2)[0])
                count = count + 1
                continue
            elif once:
                break
            else:
                self.motor_steer.run_to_position(steer)
                once = True

    def stop(self):
        self.motor.brake()
        self.motor_steer.brake()
