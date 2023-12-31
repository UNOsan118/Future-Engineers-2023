Power and Sense Management
====

This directory primarily contains the Power and Sense Management content referenced in Discussion Section 2.

# System Configuration Chart

We have attempted to create a wiring diagram for the vehicle that includes specialized information. Currently, however, LEGO does not provide electrical schematics for Spike products. We therefore created a wiring diagram that could reproduce the wiring of the car as closely as possible.

<img src="./images/ElectricalScheme.png" width="100%">

See below for a description of all sensors and connectors used.

***
# SPIKE Prime Hardware

## 1. Large Hub 

<img src="./images/Spike_L_hub.png" width="25%">

### Product Information
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

### Reasons for selecting this part
* Easy integration with Raspberry Pi.
* Easy and accurate control of motor mechanisms using Python.
* I have handled it since middle school and have experience and knowledge.

### How this is used
The Spike Large Hub (hereafter Hub) is a programmable control unit that can be used to control a variety of sensors and motors. The sensor on the Spike side is a gyro sensor built into the Hub. Based on the value of this sensor and the control amount sent from the Raspberry Pi via serial communication, the final control amount of the motor is determined and the actual control is performed. The language used is Python (Lego MicroPython to be precise).

Reference is [here](https://github.com/gpdaniels/spike-prime/blob/master/specifications/spike-prime/large-hub.pdf)

***
## 2. Large Hub Battery

<img src="./images/Spike_L_hub_battery.png" width="25%">

### Product Information
| part                  | Description                                                             |
|-----------------------|-------------------------------------------------------------------------|
| Features | Rechargeable lithium-ion battery for SPIKE Prime Large Hub |
| Rated capacity | 2100mAH |
| Rated voltage | 7.3V |
| At watt-hour Rated capacity | 15.33Wh (calculated from rated capacity and rated voltage) Lifetime: 500 cycles |
| Charging | Charged via micro USB cable<br>Charging time depends on the capability of the charger used. |

### Reasons for selecting this part
* The battery is compatible with Spike large hubs.

### How this is used
This battery is used to power the Hub.

Reference is [here](https://github.com/gpdaniels/spike-prime/blob/master/specifications/spike-prime/large-hub-rechargeable-battery.pdf)

***
# Raspberry pi Hardware

## 1. RaspberryPi 4 modelB

<img src="./images/Raspberrypi4.png" width="50%">

### Product Information
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

### Reasons for selecting this part
* It is lightweight, fast, and the easiest-to-use single-board computer we can handle.
* Compatible with SPIKE.
* It is highly flexible and can use a variety of sensors.
* It is relatively inexpensive and can handle breakdowns and problems.

### How this is used
The Raspberry Pi 4 is a small single-board computer. It is responsible for processing and analyzing images obtained from the camera in real-time. The language used is Python and the opencv library is used for image processing. The image analysis determines the amount of control for the motors based on the view captured from the camera. The calculation results are sent to the Hub using serial communication.

Reference is [here](https://www.iodata.jp/product/pc/raspberrypi/ud-rp4b/spec.htm)

***
## 2. Lithium Battery

<img src="./images/Battery.png" width="50%">

### Product Information
| part              | Description           |
|-------------------|-----------------------|
| capability        | 10000mAh/37Wh         |
| Manufacturer      | INIU                  |
| Item model number | BI-B3                 |
| input             | 5V/3A(maximum)        |
| output            | 5V/3A(maximum)        |
| size              | 13.2 * 6.8 * 1.2 [cm] |
| weight            | 198 [g]               |

### Reasons for selecting this part
* The power supply does not turn off by itself.
* Automatic switching between external power supply and battery power supply.
* A stable power supply to the Raspberry Pi.

### How this is used
It is used to supply power to the Raspberry Pi4. This power is further supplied to the Hub via a cable.

Reference is to the instructions that come with the product.<br>
Product Page is [here](https://www.amazon.com/INIU-Portable-External-Powerbank-Compatible/dp/B07H6LB4J4).<br>
This battery came with the [FaBo JetBot Kit](https://fabo.store/products/jetbot-kit). <br>

***
## 3. Camera module
<img src="./images/Camera.png" width="25%">

### Product Information
| part           | Description                                                                                            |
|----------------|--------------------------------------------------------------------------------------------------------|
| Compatibility  | Raspberry Pi model A/B                                                                                 |
| Powered by     | 5 MP Omnivision 5647 camera module                                                                     |
| Resolution     | 2592 * 1944                                                                                            |
| FOV            | 160 [degree]                                                                                           |
| Video          | 1080 p @ 30 fps<br/>720 p @ 60 fps<br/>640 x 480 p 60/90                                               |
| size           | 25×24×9[mm] <br/>0.99×0.95×0.36 [inch]                                                                 |

### Reasons for selecting this part
* Raspberry Pi is supported.
* With a 160-degree viewing angle, it is possible to see a wide area at a time.
* high resolution (of an image).

### How this is used
The camera is used in this vehicle to assess the surroundings. No other sensors, such as distance sensors, are used, and this camera is the only way to understand the surroundings. In other words, the camera recognizes not only the signs but also the walls on both sides. The resulting images are processed on a Raspberry Pi using the Python language.

Reference is [here](https://jp.sainsmart.com/products/wide-angle-fov160-5-megapixel-camera-module-for-raspberry-pi)


***
The robot will work without the Raspberry Pi Hardware described below. However, it will be more stable and secure with it.
***
## 4. Cooling fan for Raspberry Pi4
<img src="./images/RaspberryPi4_fan.png" width="25%">

### Product Information
| part                  | Description           |
|-----------------------|-----------------------|
| Manufacturer          | Miuzei                |
| Rated voltage/current | DC 5[V], 0.16[A]      |

### Reasons for selecting this part
* To prevent the Raspberry Pi4 from getting excessively hot.

### How this is used
Used for cooling Raspberry Pi. Attached to Raspberry Pi for use. The power supply is connected to the GPIO pins of the Raspberry Pi. Refer to it manual for the connection method.

***
## 5. Heat sink for Raspberry Pi4
<img src="./images/RaspberryPi4_heat_sink.png" width="25%">

### Product Information
| part                  | Description           |
|-----------------------|-----------------------|
| Manufacturer          | Miuzei                |

### Reasons for selecting this part
* To prevent the Raspberry Pi4 from getting excessively hot.

### How this is used
Used for cooling Raspberry Pi. Attached to Raspberry Pi for use. No power supply is required.

***
## 6. The case for Raspberry Pi4
<img src="./images/RaspberryPi4_case.png" width="35%">

### Product Information
| part                  | Description           |
|-----------------------|-----------------------|
| Manufacturer          | Miuzei                |

### Reasons for selecting this part
* It can reliably protect Raspberry Pi and is compatible with cooling fans and heat sinks.
* The square shape makes it easy to load into a vehicle.

### How this is used
Used to protect the Raspberry Pi.

***
Parts for items 4 ~ 6 can be purchased together [here](https://www.amazon.co.jp/Miuzei-%E6%9C%80%E6%96%B0Raspberry-Raspberry-B%E5%AF%BE%E5%BF%9C%EF%BC%88Raspberry-%E6%9C%AC%E4%BD%93%E5%90%AB%E3%81%BE%E3%82%8A%E3%81%BE%E3%81%9B%E3%82%93%EF%BC%89/dp/B07VB24K9W/ref=pd_lpo_sccl_2/356-8666249-0520814?pd_rd_w=3FbQG&content-id=amzn1.sym.d769922e-188a-40cc-a180-3315f856e8d6&pf_rd_p=d769922e-188a-40cc-a180-3315f856e8d6&pf_rd_r=472QV3E8M306498J15KX&pd_rd_wg=SoyRf&pd_rd_r=8f839c79-4c5d-4acc-86d7-16290f623915&pd_rd_i=B07VB24K9W&psc=1).
***

# Cables

## 1. GPIO - Spike Hub Port Connector
<img src="./images/Conn1.png" width="55%">

### Reasons for selecting this part
* Enables simple wired connection between RaspberryPi4 and Spike.

### How this is used
Used for serial communication between SPIKE and Raspberry Pi.The GPIO side is plugged into the GPIO pins of the Raspberry Pi, and the Spike Hub Port side is connected to the Spike Hub. Please refer to the [System Configuration Chart](#system-configuration-chart) for the connection method.

### Connection part
<img src="./images/Conn1_GPIO_serial.png" width="30%">          <img src="./images/Conn1_Spike_serial.png" width="30%">

<img src="./images/SPIKE_Prime_Cable.png" width="100%">

reference: Afrel Corporation - SPIKE automated robot assembly guide

***
## 2. USB Type A - USB Type C Connector
<img src="./images/Conn2.png" width="30%">

### Reasons for selecting this part
* Able to provide a stable power supply.

### How this is used
It is connected between the mobile battery and the Raspberry Pi and supplies power from the battery to the Raspberry Pi.The USB Type A side plugs into the mobile battery's output port, and the USB Type C side plugs into the Raspberry Pi's power supply port.

### Connection part
<img src="./images/Conn2_Battery_A_power1.png" width="30%">          <img src="./images/Conn2_Raspi_C_power1.png" width="30%">

***
## 3. USB Type A - Micro USB Type B Connector
<img src="./images/Conn3.png" width="30%">

### Reasons for selecting this part
* Able to provide a stable power supply.

### How this is used
The USB Type A side is connected to a USB 2.0 Standard A port and the Micro USB Type B side is connected to the Spike Hub's Micro USB Type B port.

### Connection part
<img src="./images/Conn3_Raspi_A_power2.png" width="30%">          <img src="./images/Conn3_Spike_micro_power2.png" width="30%">

***
## 4. Spike L Motor - Spike Hub Port Connector
<img src="./images/Conn4.png" width="55%">

### How this is used
This cable is a non-removable wire that is an integral part of the SPIKE Prime L angular motor; it connects to the Spike hub port and provides the connection between the Spike Hub and the motor. The Drive motor connects to port C of the Spike Large Hub, and the Steering motor connects to port E.

### Connection part
<img src="./images/Conn4_motor.png" width="30%">          <img src="./images/Conn4_Spike_motor.png" width="30%">

***
## 5. Flexible flat cable 15-pin
<img src="./images/Conn5.png" width="55%">

### How this is used
This cable is integrated with the camera module and is used to connect the Raspberry Pi. The cable is plugged into the connection on the Raspberry Pi side for connection. I used [this site](https://tora-k.com/2020/11/15/raspberrypi4-cammoj/) as a reference for how to plug it in.

### Connection part
<img src="./images/Conn5_Camera.png" width="30%">          <img src="./images/Conn5_Raspi_camera.png" width="30%">

***
# Explanation of how power is supplied

Using a Raspberry Pi 4, the procedure for powering the Raspberry Pi 4 from the mobile battery and then powering the Spike Large Hub from the Raspberry Pi 4 is as follows

1. **Prepare the mobile battery**:<br>
   First, prepare a mobile battery with sufficient capacity. Choose the capacity of the battery based on the power requirements of the device you are using. 2.

2. **Connecting the mobile battery to the Raspberry Pi 4**:<br>
   Connect the USB cable to the power supply port on the Raspberry Pi 4 using the mobile battery's output port (usually the USB port).

3. **Powering the Raspberry Pi 4**:<br>
   To power the Raspberry Pi 4, start the mobile battery. This will start powering the Raspberry Pi 4.

4. **Powering the Raspberry Pi 4 to the Spike Large Hub**:<br>
   The Raspberry Pi 4 can power other USB devices via its USB port; to power the Spike Large Hub, connect the Spike Large Hub to the USB port on the Raspberry Pi 4.

5. **Powering the Spike Large Hub**:<br>
   The Raspberry Pi 4 will power the Spike Large Hub and the Spike Large Hub will boot up. 6.

6. **Using the device**:<br>
   Now, starting with the mobile battery, the Spike Large Hub is powered via the Raspberry Pi 4 and each device should be up and running. the Raspberry Pi 4 controls the Spike Large Hub and can communicate data and perform other tasks.

Notes:
- Keep in mind the capacity of the mobile battery and the power consumption of the Raspberry Pi 4 and make sure that the battery can supply the appropriate amount of time.
- Use the proper standard and quality of USB cables and ports. Poor quality cables and ports can cause power supply problems.
- Take appropriate measures to ensure security and safety concerns related to power supply.
- Pay attention to the thermal management of the device as well and take necessary measures to prevent overheating.

***
# Power Consumption

1. **Power consumption of Raspberry Pi 4**:<br>
   The power consumption of the Raspberry Pi 4 will vary depending on usage conditions, but approximate estimates are as follows
   - Idle state: approx. 2.7 W
   - Light load (e.g. web browsing): 3-4 W
   - Full load (CPU/GPU heavy work): 7-8 W

   Thus, if the Raspberry Pi 4 runs continuously at maximum load, it will consume up to about 8 W of power.

2. **Spike Large Hub power consumption**:<br>
   The power consumption of the LEGO Spike Large Hub is generally low. It typically consumes less than 0.5 W. 

3. **Mobile battery capability**:<br>
   The capacity of the mobile battery provided is 10000 mAh (milliamp-hours) and 3.7 Wh (watt-hours). The power capacity of the mobile battery should be converted from ampere-hours (mAh) to watt-hours (Wh). Power (Wh) is the product of current (A) and voltage (V).

   Mobile battery capacity (Wh) = capacity (mAh) x voltage (V) / 1000<br>
   Thus, a 10000mAh battery can provide approximately 37Wh of power.

4. **Estimate power consumption**:<br>
   To estimate the total power consumption of the Raspberry Pi 4 and Spike Large Hub, sum the power consumption of each and compare it to the capacity of the mobile battery.

   - Raspberry Pi 4: 8 W
   - Spike Large Hub: 0.5 W

   Total power consumption: 8 W + 0.5 W = 8.5 W<br>
   Mobile battery capacity: 37 Wh

Thus, the mobile battery can operate for approximately 4.35 hours (37 Wh / 8.5 W) with a total power consumption of 8.5 W. 

This calculation is based on the assumption that the Raspberry Pi4 continues to operate at maximum power consumption, so it will actually run longer. However, as the battery power decreases, so does the output power, so we change the batteries every couple of hours or so.