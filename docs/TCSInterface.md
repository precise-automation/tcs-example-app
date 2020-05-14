# TCS Interface

Before using this interface, it is important to have an understanding of TCS, as this package is built upon it. Read the documentation in the TCS_Users_Guide at preciseautomation.com for more information.

This API provides the class and function for connecting to Precise Automation Robots through the TCP/IP Command Server. This API includes implementation of several commonly used TCS commands, the flexibility to issue custom (non-implemented TCS commands), and allows for the opening of multiple communication "ports" for multi-threading applications.

## Quickstart

A simple connection over TCS can easily be established as follows:

### Connecting to a robot

First, create a new robot instance:

```python
from TCSInterface import *

my_robot = TCSRobot()
```

Call the ```TCSRobot.connect(host, port)``` method to begin attempting to connect to the robot. 
```python
my_robot.connect("192.168.0.1", 10100)
```

A failure to connect will raise a ```"Could not establish connection"``` error. This could mean that the Robot is not running the ```Tcp_cmd_server.gpl``` program, or that the ```host``` or ```port``` are incorrect.

### Issuing Commands to a Robot

Once a robot is connected, issuing commands to the given robot is as simple as calling the various methods of the ```TCSRobot``` instance. Before motion commmands can be sent, the robot's high power must be on, the robot must be attached, and the robot must be homed, so it may be useful to do all of these actions immediately.
```python
my_robot.hp(1)       #set high power (enable servo)
my_robot.attach(1)   #attach the robot
if my_robot.isHomed is False
    my_robot.home()  #home if necessary
```
Alternately, the user may want control of these actions via buttons in an interface. Keep in mind that in the event of a physical collsision, the robot may disable power and un-attach the robot.

### Closing a Client Connection

When the robot is no longer needed, the ```TCSRobot.disconnect()``` method can be called to safely close the communication link.
```python
my_robot.Close()
```

A full explanation of the ```TCSRobot``` class and its methods can be found below.

## Classes and Functions

### TCSRobot

By default, the ```Tcp_cmd_server.gpl``` program that is running on the robot listenes for ASCII string commands over several ports. The ```TCSRobot``` class provides a convenient way to connect, send, and receive data over one of these ports.
In practice, most applications connect to two of these ports, the "Status" port (10000) and the "Robot" port (10100). More information on this can be found in the TCS documentation.

#### Instantiation
```python
my_robot = TCSRobot()
```

#### Properties
| Property | Description |
| ----------- | ----------- |
| Robot.connection | The ```TCSConnection``` instance that this robot will use to send and receive data. |
| Robot.isSelected | The selection state of the robot (provided to reduce redundant use of ```TCSRobot.selectRobot()```). |
| Robot.isAttached | The attachment state of the robot. |
| Robot.isHp | The power state of the robot. |
| Robot.isHomed | The homed state of the robot. |

#### Methods
| Method | Description |
| ----------- | ----------- |
| TCSRobot.connect(host, port) | Opens a connection with a robot running TCS at a specified host IP and port number. |
| TCSRobot.disconnect() | Closes the current connection. |
| TCSRobot.nop() | No operation. Returns empty, successful TCSResponse. |
| TCSRobot.mspeed() | See ```mspeed```. Returns TCSResponse. |
| TCSRobot.selectRobot(arg1=None) | See ```selectRobot```. To poll the selection state, use the ```TCSRobot.isSelected``` property instead to reduce TCP/IP traffic. Returns TCSResponse. |
| TCSRobot.attach(arg1=None) | See ```attach```. To poll the attachment state, use the ```TCSRobot.isAttached``` property instead to reduce TCP/IP traffic. Returns TCSResponse. |
| TCSRobot.hp(cmd=None, waitTime=0) | See ```hp```. To poll the high power state, use the ```TCSRobot.isHp``` property instead to reduce TCP/IP traffic. Returns TCSResponse. |
| TCSRobot.home() | See ```home```. Returns TCSResponse. |
| TCSRobot.waitForEOM() | See ```waitForEOM```. Returns TCSResponse. |
| TCSRobot.halt() | See ```halt```. Returns TCSResponse. |
| TCSRobot.wherej() | See ```wherej```. Returns TCSResponse. |
| TCSRobot.wherec() | See ```wherec```. Returns TCSResponse. |
| TCSRobot.tool(toolOffset=None) | See ```tool```. Returns TCSResponse. |
| TCSRobot.sysState() | See ```stsState```. Returns TCSResponse. |
| TCSRobot.payload() | See ```payload```. Returns TCSResponse. |
| TCSRobot.profile(arg1=None, arg2=None, arg3=None, arg4=None, arg5=None, arg6=None, arg7=None, arg8=None, arg9=None) | See ```profile```. Returns TCSResponse. |
| TCSRobot.hereJ(arg1) | See ```hereJ```. Returns TCSResponse. |
| TCSRobot.hereC(arg1) | See ```hereC```. Returns TCSResponse. |
| TCSRobot.loc(arg1) | See ```loc```. Returns TCSResponse. |
| TCSRobot.locXYZ(arg1, arg2=None, arg3=None, arg4=None, arg5=None, arg6=None, arg7=None) | See ```locXYZ```. Returns TCSResponse. |
| TCSRobot.storeFile(arg1=None) | See ```storeFile```. Returns TCSResponse. |
| TCSRobot.loadFile(arg1=None) | See ```loadFile```. Returns TCSResponse. |
| TCSRobot.freeMode() | See ```freeMode```. Returns TCSResponse. |
| TCSRobot.graspData() |  See ```graspData```. Returns TCSResponse. |
| TCSRobot.teachPlate() | See ```teachPlate```. Returns TCSResponse. |
| TCSRobot.pickPlate() | See ```pickPlate```. Returns TCSResponse. |
| TCSRobot.placePlate() | See ```placePlate```. Returns TCSResponse. |
| TCSRobot.waitforEOM() | See ```waitForEom```. Returns TCSResponse. |
| TCSRobot.homeAllIfNoPlate() | See ```homeAllIfNoPlate```. Returns TCSResponse. |
| TCSRobot.getHomedState() | Checks an internal parameter to see if the robot is homed. Returns ```Bool```. |
| TCSRobot.getLastError() | Checks an internal parameter to see the last error of the robot. Returns an error code ```Int```. |
| TCSRobot.rawString(cmd) | Sends the raw string input to TCS directly. Useful for debugging or testing custom commands not included in this API. Returns TCSResponse. |


### TCS Response

All data received from the robot is parsed in the TCSConnection class and returned in a simple container class, ```TCSResponse```. This class provides a quick and easy way to check if the command was executed successfully on the robot, and if not, what the error code was.

#### Properties
| Property | Description |
| ----------- | ----------- |
| bool TCSResponse.success | If the reply string from the robot starts with ```0```, then the command was processed successfully and this property is set true. If the reply string starts with ```-```, then command failed and the reply string is an error code. |
| int TCSResponse.error | If successful, the error is None. If unsuccessful, the error is a negative number corresponding to the reason the command failed. |
| str TCSResponse.message | If successful, the message is the section of the reply string after the leading ```0 ```. If unsuccessful, the message is None. |
