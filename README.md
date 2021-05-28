# MQTT client to control BroadLink devices

* Supported devices
    * [**RM Pro / RM2 / RM3 mini / RM4**](#rm2rm3rm4) IR/RF controllers (device_type = 'rm' or 'rm4')
    * [**SP1/SP2**](#sp1sp2) smart plugs (device_type = 'sp1' or 'sp2')
    * [**A1**](#a1) sensor (device_type = 'a1')
    * [**MP1**](#mp1) power strip (device_type = 'mp1')
    * [**Dooya DT360E**](#dooya-dt360e) curtain motor (device_type = 'dooya')
    * [**BG1**](#bg1) BG smart socket (device_type = 'bg1')
* [Installation](#installation)
* [Configuration](#configuration)
    * [Multiple devices configuration](#multiple-devices-configuration)
* [Connect Broadlink device to wifi](#connect-broadlink-device-to-wifi)
* [Start](#start)
    * [Auto-startup (Linux)](#auto-startup--linux-)
* [Error messages](#error-messages)

 
## Installation
Clone *broadlink-mqtt* repository using  
`git clone https://github.com/eschava/broadlink-mqtt.git`  
or download and unpack latest archive from  
https://github.com/eschava/broadlink-mqtt/archive/master.zip

Ensure that a python development environment is setup:
`sudo apt-get install python-pip python-dev`

Ensure that the *libffi-dev* and *libssl-dev* packages are installed:
`sudo apt-get install libffi-dev libssl-dev`

From the newly created  *broadlink-mqtt* folder, install the required Python modules:
`pip install -r requirements.txt`

## Configuration
By default, *broadlink-mqtt* will configure using parameters from `mqtt.conf`. This configuration file may be altered during a repository update, so another configuration file is provided for editing: `custom.conf`. This will not be overwritten when updating *broadlink-mqtt*.

`custom.conf` overrides `mqtt.conf`. Copy the contents of `mqtt.conf` into `custom.conf` and continue editing only `custom.conf`. 

Recorded commands are saved under the `commands/` folder  
Macros are saved under the `macros/` folder

### Multiple devices configuration
Usually *broadlink-mqtt* works with single Broadlink device only, but there is an experimental feature to support several devices connected to the same network.   
Configuration parameters:   
`device_type = 'multiple_lookup'`  
`mqtt_multiple_subprefix_format = '{type}_{mac_nic}/'`  
Second parameter defines format of sub-prefix for every found device. E.g. for RM2 device having MAC address 11:22:33:44:55:66, MQTT prefix will be  
`broadlink/RM2_44_55_66/`  
Format supports next placeholders:  
   * `{type}` - type of the device (RM2, A1, etc)  
   * `{host}` - host name of the device  
   * `{mac}` - MAC address of the device  
   * `{mac_nic}` - last 3 octets of the MAC address (NIC)  

## Connect Broadlink device to wifi
You need to use the [Broadlink e-control app](https://play.google.com/store/apps/details?id=com.broadlink.rmt) or [Broadlink Intelligent Home Center](https://play.google.com/store/apps/details?id=cn.com.broadlink.econtrol.plus) to get the device connected to wifi. **Don't use** [BroadLink -Universal TV Remote](https://play.google.com/store/apps/details?id=cn.com.broadlink.econtrol.international), as it is known to lock devices. Other apps have not been tested.

Press the reset-button for 5+ seconds till the led starts flashing continuously. Now it is in "smart mode". Go to the `e-control` or `Intelligent home Center` app and add a new device. Fill in the wifi-credentials and start scanning while staying close to the device. When the led starts flashing slower, it is discovered. When the led turns off, it is configured.

You (theoretically) can configure multiple devices at one.

## Start
Just start `mqtt.py` script using Python interpreter. You may have to use `python3`.

### Auto-startup (Linux)
(From https://github.com/eschava/broadlink-mqtt/issues/29#issuecomment-630254666)

    sudo nano /lib/systemd/system/broadlink-mqtt.service

Copy and paste the following, then save:

`[Unit]`  
`Description=Broadlink MQTT Service`  
`After=multi-user.target`  
`Conflicts=getty@tty1.service` 

`[Service]`  
`Type=simple`  
`ExecStart=/usr/bin/python3 /home/pi/broadlink-mqtt/mqtt.py`  
`StandardInput=tty-force`  

`[Install]`  
`WantedBy=multi-user.target`

Reload the daemon:
`sudo systemctl daemon-reload`

To start the service:  
`sudo systemctl start broadlink-mqtt.service`
    
To see the service status:  
`sudo systemctl status broadlink-mqtt.service`
    
To stop the service:  
`sudo systemctl stop broadlink-mqtt.service`
    
To restart the service:  
`sudo systemctl restart broadlink-mqtt.service`

## Error messages
- **ERROR No Broadlink devices found**: No wifi-device on the network is a Broadlink device recognized by the library. If you see a device connected to your wifi that starts with the device type, like "RM4-44-b6-a2" for a RM4, then it could be that the device is not supported yet. If you see no device connected (which is in most cases), make sure it is connected to your wifi network.
- **broadlink.exceptions.AuthenticationError: Authentication failed**: The device is locked by an app. Use the instructions above to reset the device and connect it to wifi without lock.
- **with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s: AttributeError: __exit__**: this library requires Python3, and you used Python2. Start the library with `python3 ./mqtt.py`.
- **ERROR MQTT topic broadlink/RMx_xx_xx_xx/projector/power has no recognized device reference, expected one of RMy_yy_yy_yy/**: replace the device ID `RMx_xx_xx_xx` with `RMy_yy_yy_yy` in your mqtt-command.
- **FileNotFoundError: [Errno 2] No such file or directory: '/opt/broadlink-mqtt/commands/projector/power'**: You need to manually create a directory per device.
- **WARNING OOOOPS! MQTT disconnection**: It happens

If you think you see reasons to improve the library, you are very welcome to contribute!

# RM2/RM3/RM4
### MQTT commands to control IR/RF
#### Recording (IR or RF)
To record new command just send `record` message for IR command or `recordrf` for RF command to the topic `broadlink/COMMAND_ID`,  
where COMMAND_ID is any identifier that can be used for file name (slashes are also allowed)  
> **NOTE**: It seems that Python3 is a must for recording RF signals  

**Example**: to record power button for Samsung TV send  
`record` -> `broadlink/tv/samsung/power`  
and recorded interpretation of IR signal will be saved to file `commands/tv/samsung/power`

#### Replay
To replay previously recorded command send `replay` message to the topic `broadlink/COMMAND_ID`,  
where COMMAND_ID is identifier if the command  
**Example**: to replay power button for Samsung TV send  
`replay` -> `broadlink/tv/samsung/power`  
and saved interpretation of IR signal will be replayed from file `commands/tv/samsung/power`

Another format for replaying recorded command is using file name as a message and folder as MQTT topic.  
**Example**: to replay power button for Samsung TV send  
`power` -> `broadlink/tv/samsung`  
and saved interpretation of IR signal will be replayed from file `commands/tv/samsung/power`

#### Smart mode
Smart mode means that if file with command doesn't exist it will be recorded.  
Every next execution of the command will replay it.  
This mode is very convenient for home automation systems.  
To start smart mode need to send `auto` for IR command or `autorf` for RF command to the command topic   
**Example:**  
first time: `auto` -> `broadlink/tv/samsung/power` records command  
every next time: `auto` -> `broadlink/tv/samsung/power` replays command  

#### Macros
Macro command sends several IR signals for single MQTT message.  
To start macros execution send `macro` message to the topic `broadlink/MACRO_ID`,  
where `MACRO_ID` is a path to scenario file in `macros/` folder.  
Alternative way of sending macro command is sending `MACRO_ID` message to the `broadlink/macro` topic.  

Macros scenario file could contain:
 - IR commands (same as `COMMAND_ID` in replay mode)
 - pause instructions (`pause DELAY_IN_MILLISECONDS`)
 - comments (lines started with `#`)
 
### Subscription to current temperature (RM2/RM4 devices)
Need to set `broadlink_rm_temperature_interval` configuration parameter to a number of seconds between periodic updates.  
E.g. 
`broadlink_rm_temperature_interval`=120
means current temperature will be published to topic `broadlink/temperature` every 2 minutes

# SP1/SP2
### MQTT commands to control power
To switch power on (off) need to send command `on` (`off`) to `broadlink/power` topic  
Commands `1` / `0` are also supported

### Subscription to current used energy (SP2 device)
Need to set `broadlink_sp_energy_interval` configuration parameter to a number of seconds between periodic updates.  
E.g.  
`broadlink_sp_energy_interval`=120  
means current used energy will be published to topic `broadlink/energy` every 2 minutes

# A1
### Subscription to current sensors data
Need to set `broadlink_a1_sensors_interval` configuration parameter to a number of seconds between periodic updates.  
E.g.  
`broadlink_a1_sensors_interval`=120
means current sensors data will be published to topics `broadlink/sensors/[temperature/humidity/light/air_quality/noise]` every 2 minutes  

# MP1
### MQTT commands to control power
To switch power on (off) on outlet number N need to send command `on` (`off`) to `broadlink/power/N` topic.  
Commands `1` / `0` are also supported  
**Example:**  
switch on 2-nd outlet: `on` -> `broadlink/power/2`

### Subscription to current state
Need to set `broadlink_mp1_state_interval` configuration parameter to a number of seconds between periodic updates.  
E.g.  
`broadlink_mp1_state_interval`=120  
means current state will be published to topics `broadlink/state/[s1/s2/s3/s4]` every 2 minutes    

# Dooya DT360E
### MQTT commands to control curtain motor
To open/close curtains need to send a command to `broadlink/action` topic.  
Possible commands are:  
  - `open` to open curtains
  - `close` to close curtains
  - `stop` to stop curtains in the current state  

Also it's possible to set fixed position of curtains sending numeric position in percents to the topic `broadlink/set`

### Subscription to current curtain position
Need to set `broadlink_dooya_position_interval` configuration parameter to a number of seconds between periodic updates.  
E.g.  
`broadlink_dooya_position_interval`=30  
means current curtain position in percents will be published to topic `broadlink/position` every 30 seconds  

# BG1
### MQTT commands to control
To change brightness of LED need to send value in percents to `broadlink/brightness` topic  
To switch power on (off) on all (or single only) outlets need to send command `on` (`off`) to `broadlink/power` topic.  
To switch power on (off) on outlet number N need to send command `on` (`off`) to `broadlink/power/N` topic.  
Commands `1` / `0` are also supported  
**Example:**  
switch on 2-nd outlet: `on` -> `broadlink/power/2`  

### Subscription to current state
Need to set `broadlink_bg1_state_interval` configuration parameter to a number of seconds between periodic updates.  
E.g.  
`broadlink_bg1_state_interval`=120  
means current state will be published to topics `broadlink/state/[pwr/pwr1/pwr2/maxworktime/maxworktime1/maxworktime2/idcbrightness]` every 2 minutes    
