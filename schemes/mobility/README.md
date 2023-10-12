## Mobility management

Explanation of a simple method of transportation:
Our robot is a 4-wheeled car with two motors. The back two wheels are for driving and the front two wheels are for steering control.
The back two wheels are for driving and the front two wheels are for steering control (rear wheel drive).
The two motors are connected to a SPIKE L hub and controlled using the Python language.

Implementation of the drive mechanism:
The drive mechanism does not simply connect the drive motor and tires, but uses differential gears.
The drive mechanism does not simply connect the drive motor and tires, but uses differential gears. 
This mechanism is made by assembling LEGO parts and can be easily reproduced.
This mechanism is made from a combination of LEGO parts and can be easily reproduced. 
The motor and tires can be assembled in a few simple steps.
The Sanukitec.net website (https://sanuki-tech.net/micro-bit/lego/tricycle-differential-gear/) was used as a reference for the assembly.

Image of the part where the differential gear is actually used

<img src="./images/differential_gear1.png" width="100%">
<img src="./images/differential_gear2.png" width="100%">

The role of this gear is to absorb the difference in speed between the inside and outside of a curve while transmitting power from the engine to both the left and right axles.

The gear absorbs the difference in speed between the inside and outside of the curve and allows the car to go around the curve better.

The gear is used to change the direction of travel when following a sign, or to change the direction of a turn. 

This is a perfect mechanism for this competition where there is a lot of turning, such as when changing direction according to a sign, or when turning a corner on a track.

This mechanism is perfect for this competition where there are many turns to be made, such as when changing direction according to a sign, or when taking a corner of a course. 

This mechanism is
This mechanism can be officially used in the Q&A on the web page of WRO (not WRO Japan, but the world standard site).

This mechanism has been officially approved for use in the Q&A on the web page of WRO (not WRO Japan, but the world standard website).

Implementation of the steering mechanism:
The steering mechanism is a simple mechanism that controls the angle of the tires based on the size of the motor's angle of rotation.
The steering mechanism is a simple mechanism that controls the position and angle of the tires according to the size of the motor's rotation.
 If the motor rotation is transmitted directly to the tires, it is difficult to control the angle of the tires.
Therefore, a gear is used to slow down the movement.
The motor rotation is controlled by the size of the motor's bolt and the position of the tires.

<img src="./images/front_wheel1.png" width="100%">
<img src="./images/front_wheel2.png" width="100%">

Image of the realized steering mechanism

The gear parts are actually held in place by separate parts to prevent them from falling.

<img src="./images/front_wheel3.png" width="100%">

It's holding down the gears.

Here, the gear directly connected to the motor has 9 gears, (second one has 20 gears,) third one has 28 gears, so the rotation of the motor is 9/28 ≈ 0.32 times the tire's position.
(second) is 20 teeth (third) is 28 teeth (third) is 28 teeth (third) is 28 teeth. 
This means that if the motor is moved 30 degrees, the tire will move approximately 10 degrees.
The motor is designed to move about 10 degrees when the motor is moved 30 degrees.

Selected motor:
SPIKE Prime L Angular Motor * 2 (for drive and steering control)

Motor Specifications:
モーターの仕様：

| part                         | Description                                                                           |
|------------------------------|---------------------------------------------------------------------------------------|
| Connector type               | LEGO® Power Functions 2.0 (LPF2) for connection to LEGO Smarthubs                     |
| Wire length                  | 250 mm                                                                                |
| Motor output(Voltage range)  | 5[V] ~ 9[V]                                                                           |
| Motor output(No load)        | Torque: 0 Ncm<br> Speed: 175 RPM +/- 15%<br> Current consumption: 135 mA +/- 15%      |
| Motor output(Maximum efficiency) | Torque: 8 Ncm<br> Speed: 135 RPM +/- 15%<br> Current consumption: 430 mA +/- 15%      |
| Motor output(Stall)          | Torque: 25 Ncm<br> Speed: 0 RPM +/- 15%<br> Current consumption: 1900 mA +/- 15%      |
| Sensor input                 | Resolution: 360 counts per revolution <br> Accuracy: Accuracy: ≤+/- 3 degrees <br> Update rate: 100 Hz|

The official specifications for the components of SPIKE Prime can be found [here](https://github.com/gpdaniels/spike-prime/tree/master/specifications/spike-prime).

A rough explanation of the overall structure of the car:
The car is based on the contents of the LEGO Education SPIKE Prime set.
The car body is designed and built by combining RaspberryPi, camera module, mobile battery and other LEGO components based on the contents of the LEGO Education SPIKE Prime set.
The car body is designed and built by combining RaspberryPi, camera module, mobile battery and other LEGO parts based on the contents of LEGO Education SPIKE Prime set.
RaspberryPi, camera module and mobile battery are not LEGO parts.
The RaspberryPi, camera module, and mobile battery are not LEGO parts, so we used LEGO parts to create a framework and a space in which to install them.
and a space to install them. Especially for the camera module, it is possible to place the placement without interfering with the camera image.
and the camera is positioned slightly downward. In addition, there is no effect on driving.
In addition, we have taken into consideration that the weight of the wires should not be so heavy that it would affect driving.

Development environment:
開発環境：
Development is done by displaying the screen of RaspberryPi4 running on RaspberryPi OS to a PC with MacOS using an application called VNC Viewer.
The development is operated by displaying the screen of RaspberryPi4 running on RaspberryPi OS to a PC with MacOS using an application called VNC Viewer.
Wireless connection via Wi-Fi is also possible, but this time we will use a wired connection with a LAN cable.
Wireless connection via Wi-Fi is also possible, but this time a wired connection using a LAN cable is used.
The Python code is written using Mu-editor.
Mu-editor is an editor that supports both Python3 and LEGO micro python,
It can not only execute programs on SPIKE and RaspberryPi, but also write programs to SPIKE hub.
It can not only run programs on SPIKE and RaspberryPi, but also write programs to the SPIKE hub.