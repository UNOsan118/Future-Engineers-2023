モビリティマネジメントに関する欄
Japan 決勝大会 でのドキュメントを英訳する感じで足りない部分は足す

Electromechanical diagrams
====

ElectricalScheme.png内の構成要素に関する詳細は次の通りです．

## HardWare

***
### SPIKE Prime Hardware

### 1. Large Hub 

| part                  | Description                                                             |
|-----------------------|-------------------------------------------------------------------------|
| CPU                   | STM32F413 (Architecture: ARM Cortex M4, ROM: 1M, RAM: 320k, Clock: 100MHz) |
| Internal storage      | 32MB flash memory (IC: Winbond W25Q256JV)                               |
| Wireless connectivity | Bluetooth supporting 1 BT and 4 BLE connections (IC: TI CC2564C)        |
| Wired connectivity    | Micro USB cable                                                         |
| Display               | 25 white LEDs in a 5x5 grid and 1 RGB LED (Driver IC: TI TLC5955)       |
| Motor Drivers         | 	6 motor outputs (Driver ICs: 3 x LB1836)  |
| Battery Management    | Lithium ion battery management (IC: MPS 2639A)   |
| Accerometer           | Three-axis accelerometer (IC: LSM6DS3TR) |
| Gyroscope             | Three-axis gyroscope (IC: LSM6DS3TR)       |
| Ports                 | 6 LPF2 ports = 4 normal speed (115kB), 2 high speed (?kB)               |

### 2. Large Angular Motor


| part                         | Description                                                                           |
|------------------------------|---------------------------------------------------------------------------------------|
| Connector type               | LEGO® Power Functions 2.0 (LPF2) for connection to LEGO Smarthubs                     |
| Wire length                  | 250 mm                                                                                |
| Motor output(Voltage range)  | 5[V] ~ 9[V]                                                                           |
| Motor output(No load)        | Torque: 0 Ncm<br> Speed: 175 RPM +/- 15%<br> Current consumption: 135 mA +/- 15%      |
| Motor output(Maximum efficiency) | Torque: 8 Ncm<br> Speed: 135 RPM +/- 15%<br> Current consumption: 430 mA +/- 15%      |
| Motor output(Stall)          | Torque: 25 Ncm<br> Speed: 0 RPM +/- 15%<br> Current consumption: 1900 mA +/- 15%      |
| Sensor input                 | Resolution: 360 counts per revolution <br> Accuracy: Accuracy: ≤+/- 3 degrees <br> Update rate: 100 Hz|

SPIKE Primeの構成要素に関する公式仕様書は[こちら](https://github.com/gpdaniels/spike-prime/tree/master/specifications/spike-prime)を参照してください．

### [広角カメラ](https://jp.sainsmart.com/products/wide-angle-fov160-5-megapixel-camera-module-for-raspberry-pi)
| part           | Description                                                                                            |
|----------------|--------------------------------------------------------------------------------------------------------|
| Compatibility  | Raspberry Pi model A/B                                                                                 |
| Powered by     | 5 MP Omnivision 5647 camera module                                                                     |
| Resolution     | 2592 * 1944                                                                                            |
| FOV            | 160 [degree]                                                                                           |
| Video          | 1080 p @ 30 fps<br/>720 p @ 60 fps<br/>640 x 480 p 60/90                                               |
| size           | 25×24×9[mm] <br/>0.99×0.95×0.36 [inch]                                                                 |

### RaspberryPi 4 modelB
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

### Battery
| part       | Description           |
|------------|-----------------------|
| capability | 10000mAh/37Wh         |
| input      | 5V/3A(maximum)        |
| output     | 5V/3A(maximum)        |
| size       | 13.2 * 6.8 * 1.2 [cm] |
| weight     | 198 [g]               |

## シリアル通信

WRO FEでは，コース上の情報をRaspberryPiのカメラから取得し，操作量などの情報をHubに送る必要があります．ElectricalScheme.pngに示したように，HubのDポートとRaspberryPiのGPIOピンをシリアルケーブルで接続します．詳細については以下の図を参考にしてください．　
また，micro USBケーブルもしくはbluetoothを通じて，Hub上のファイルシステムへのアクセスや，プログラムの書き込みや実行が可能です．そちらの詳細については，こちらを参照してください．


