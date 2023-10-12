Power and sense management
====
This directory contains mobility management corresponding to reference in the discussion sections 1.

### System Configuration Chart
***
<img src="./images/ElectricalScheme.png" width="100%">

***
### SPIKE Prime Hardware

## 1. Large Hub 

<img src="./images/Spike_L_hub.png" width="100%">

| part                  | Description                                                             |
|-----------------------|-------------------------------------------------------------------------|
| CPU                   | STM32F413 (Architecture: ARM Cortex M4, ROM: 1M, RAM: 320k, Clock: 100MHz) |
| Power                 | Requires large hub battery (batteries are not acceptable)               |
| Sense                 | Built-in 6-axis gyro sensor<br>   3-axis acceleration sensor + 3-axis gyro sensor<br>   Gyroscope mode (3-axis)/Acceleration/Tilt mode (3-axis)<br>   Tap/double-tap/shake gesture detection               |
| Button                 | 3 buttons<br>   center button:Large hub on/off, Select/run programs<br>   Left button, right button: program selection             |
| Internal storage      | 32MB flash memory (IC: Winbond W25Q256JV)                               |
| Wireless connectivity | Bluetooth supporting 1 BT and 4 BLE connections (IC: TI CC2564C)        |
| Wired connectivity    | Micro USB cable                                                         |
| Display               | 25 white LEDs in a 5x5 grid and 1 RGB LED (Driver IC: TI TLC5955)       |
| Motor Drivers         | 	6 motor outputs (Driver ICs: 3 x LB1836)  |
| Battery Management    | Lithium ion battery management (IC: MPS 2639A)   |
| Accerometer           | Three-axis accelerometer (IC: LSM6DS3TR) |
| Gyroscope             | Three-axis gyroscope (IC: LSM6DS3TR)       |
| Ports                 | 6 LPF2 ports = 4 normal speed (115kB), 2 high speed (?kB)<br>Input/Output dual use               |

## 2. Large Hub Battery

<img src="./images/Spike_L_hub_battery.png" width="100%">

| part                  | Description                                                             |
|-----------------------|-------------------------------------------------------------------------|
| Features | Rechargeable lithium-ion battery for SPIKE Prime Large Hub |
| Rated capacity | 2100mAH |
| Rated voltage | 7.3V |
| At watt-hour Rated capacity | 15.33Wh (calculated from rated capacity and rated voltage) Lifetime: 500 cycles |
| Charging | Charged via micro USB cable<br>Charging time depends on the capability of the charger used. |

References are [these](https://afrel.co.jp/product/spike/technology/spec/)


### Raspberry pi and other Hardware

## 1. RaspberryPi 4 modelB

<img src="./images/Raspberrypi4.png" width="100%">

| part          | Description                                                                                                                                                 |
|---------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Processor     | Broadcom BCM2711 quad-core Cortex-A72 (ARM v8) 64-bit SoC @ 1.5GHz                                                                                          |
| Memory        | 8GB                                                                                                                                                         |
| Connectivity  | 2.4 GHz and 5.0 GHz IEEE 802.11b/g/n/ac wirelessLAN, Bluetooth 5.0, BLE<br>Gigabit Ethernet<br>2 × USB 3.0 ports<br>2 × USB 2.0 ports.                      |
| GPIO          | Standard 40-pin GPIO header                                                                                                                                 |
| Video & sound | 2 × micro HDMI ports (up to 4Kp60 supported)<br>2-lane MIPI DSI display port<br>2-lane MIPI CSI camera port<br>4-pole stereo audio and composite video port |
| Multimedia    | H.265 (4Kp60 decode);<br>H.264 (1080p60 decode, 1080p30 encode);<br>OpenGL ES, 3.0 graphics                                                                 |
| SD card support              | Micro SD card slot for loading operating system and data storage                                                                                            |
| Input power              | 5V DC via USB-C connector (minimum 3A1)<br>5V DC via GPIO header (minimum 3A1)<br>Power over Ethernet (PoE)–enabled(requires separate PoE HAT)                                                                                                                                                            |
| Environment                         | Operating temperature 0–50ºC                                                                                                                                                                                                                                                    |

## 2. Lithium Battery

<img src="./images/Battery.png" width="100%">

| part       | Description           |
|------------|-----------------------|
| capability | 10000mAh/37Wh         |
| input      | 5V/3A(maximum)        |
| output     | 5V/3A(maximum)        |
| size       | 13.2 * 6.8 * 1.2 [cm] |
| weight     | 198 [g]               |

# Feature
* The power supply does not turn off by itself.
* Automatic switching between external power supply and battery power supply.

## 3. Connector
<img src="./images/Connector.png" width="100%">
Used for serial communication between SPIKE and Raspberry Pi.

## 3. Camera module
<img src="./images/Camera.png" width="100%">


### Explanation of how power is supplied
When you run a Raspberry Pi on a typical mobile battery,
* The power feed drops out on its own.
* USB power supply and battery power supply do not switch.
As described above, this is not a suitable power supply for the Raspberry Pi because of its intelligent features for smartphones.The Lithium-ion Battery Expansion Board for Raspberry Pi is used to solve the problem of power loss and the problem of not switching between USB power and battery power. The Lithium-ion Battery Expansion Board for Raspberry Pi is powered by the mobile battery and relays power to the Spike Hub.
References are [here](https://voltechno.com/blog/raspberrypi-battery/)