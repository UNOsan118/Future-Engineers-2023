# 2023 obstacle
import hub
class Basic_motion:
    def __init__(self,motor_steer,motor): # Definition of motors used
        self.motor_steer = motor_steer
        self.motor = motor


    def move(self,throttle, steer): # Functions running at constant steering value and constant speed
        self.motor.run_at_speed(throttle)
        once = False

        if steer > 90:   # Cut values above a certain level to avoid unreasonable angles
            steer = 90
        elif steer < -90:
            steer = -90

        elif steer > 70: # Similarly, values above a certain level are cut
            steer = 70
        elif steer < -70:
            steer = -70

        while True:
            if(self.motor_steer.busy(type=1)): # if motor_steer is moving 
                continue
            elif once: # To be moved only once
                break
            else:
                self.motor_steer.run_to_position(steer) # Set the steering motor angle to [steer]
                once = True

    # Function to stop the motor
    def stop(self):
        self.motor.brake()
        self.motor_steer.brake()
