# MQTT client to control BroadLink RM devices
 
## Installation
Install required Python modules using  
`pip install paho-mqtt broadlink`

## Configuration
All configurable parameters are present in `mqtt.conf` file  
Recorded commands are saved under the `commands/` folder  
Macros are saved under the `macros/` folder

## Start
Just start `mqtt.py` script using Python interpreter

## MQTT commands
###Recording
To record new command just send `record` message to the topic `broadlink/COMMAND_ID`,  
where COMMAND_ID is any identifier that can be used for file name (slashes are also allowed)  
**Example**: to record power button for Samsung TV send  
`record` -> `broadlink/tv/samsung/power`  
and recorded interpretation of IR signal will be saved to file `commands/tv/samsung/power`

###Replay
To replay previously recorded command send `replay` message to the topic `broadlink/COMMAND_ID`,  
where COMMAND_ID is identifier if the command  
**Example**: to replay power button for Samsung TV send  
`replay` -> `broadlink/tv/samsung/power`  
and saved interpretation of IR signal will be replayed from file `commands/tv/samsung/power`

###Smart mode
Smart mode means that if file with command doesn't exist it will be recorded.  
Every next execution of the command will replay it.  
This mode is very convenient for home automation systems.  
To start smart mode need to send empty string or `auto` to the command topic   
**Example:**  
first time: `auto` -> `broadlink/tv/samsung/power` records command  
every next time: `auto` -> `broadlink/tv/samsung/power` replays command  

###Macros
Macros are created to send several IR signals for single MQTT message.  
To start macros execution send `macro` message to the topic `broadlink/MACRO_ID`,  
where `MACRO_ID` is a path to scenario file in `macros/` folder.  

Macros scenario file could contain:
 - IR commands (same as `COMMAND_ID` in replay mode)
 - pause instructions (`pause DELAY_IN_MILLISECONDS`)
 - comments (lines started with `#`)
 