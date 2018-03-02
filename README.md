# MQTT client to control BroadLink devices
 
## Installation
Clone *broadlink-mqtt* repository using  
`git clone https://github.com/eschava/broadlink-mqtt.git`  
or download and unpack latest archive from  
https://github.com/eschava/broadlink-mqtt/archive/master.zip  

Also need to install required Python modules using  
`pip install paho-mqtt broadlink`

## Configuration
All configurable parameters are present in `mqtt.conf` file. But there is also `custom.conf` file. Changes from `custom.conf` overrides `mqtt.conf` and it's better to put changed configuration parameters there, to avoid conflicts while updating branch from repository.   
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


## Start
Just start `mqtt.py` script using Python interpreter

## MQTT commands to control IR (RM2/RM3 devices)
### Recording
To record new command just send `record` message to the topic `broadlink/COMMAND_ID`,  
where COMMAND_ID is any identifier that can be used for file name (slashes are also allowed)  
**Example**: to record power button for Samsung TV send  
`record` -> `broadlink/tv/samsung/power`  
and recorded interpretation of IR signal will be saved to file `commands/tv/samsung/power`

### Replay
To replay previously recorded command send `replay` message to the topic `broadlink/COMMAND_ID`,  
where COMMAND_ID is identifier if the command  
**Example**: to replay power button for Samsung TV send  
`replay` -> `broadlink/tv/samsung/power`  
and saved interpretation of IR signal will be replayed from file `commands/tv/samsung/power`

### Smart mode
Smart mode means that if file with command doesn't exist it will be recorded.  
Every next execution of the command will replay it.  
This mode is very convenient for home automation systems.  
To start smart mode need to send empty string or `auto` to the command topic   
**Example:**  
first time: `auto` -> `broadlink/tv/samsung/power` records command  
every next time: `auto` -> `broadlink/tv/samsung/power` replays command  

### Macros
Macros are created to send several IR signals for single MQTT message.  
To start macros execution send `macro` message to the topic `broadlink/MACRO_ID`,  
where `MACRO_ID` is a path to scenario file in `macros/` folder.  

Macros scenario file could contain:
 - IR commands (same as `COMMAND_ID` in replay mode)
 - pause instructions (`pause DELAY_IN_MILLISECONDS`)
 - comments (lines started with `#`)
 
## MQTT commands to control power (SP1/SP2 devices)
To switch power on (off) need to send command `on` (`off`) to `broadlink/power` topic

## MQTT commands to control power (MP1 device)
To switch power on (off) on outlet number N need to send command `on` (`off`) to `broadlink/power/N` topic.
**Example:**  
switch on 2-nd outlet: `on` -> `broadlink/power/2`

## Subscription to current temperature (RM2 device)
Need to set `broadlink_rm_temperature_interval` configuration parameter to number of seconds between periodic updates.
E.g. 
`broadlink_rm_temperature_interval`=120
means current temperature will be published to topic `broadlink/temperature` every 2 minutes

## Subscription to current used energy (SP2 device)
Need to set `broadlink_sp_energy_interval` configuration parameter to number of seconds between periodic updates.
E.g. 
`broadlink_sp_energy_interval`=120
means current used energy will be published to topic `broadlink/energy` every 2 minutes

## Subscription to current sensors data (A1 device)
Need to set `broadlink_a1_sensors_interval` configuration parameter to number of seconds between periodic updates.
E.g. 
`broadlink_a1_sensors_interval`=120
means current sensors data will be published to topics `broadlink/sensors/[temperature/humidity/light/air_quality/noise]` every 2 minutes

