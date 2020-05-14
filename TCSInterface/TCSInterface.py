"""
A Python interface for commanding a Precise Automation robot.

Use of this interface requires TCS to be running on the Precise Automation robot.
"""

import telnetlib
import time



class TCSRobot:
    """The primary interface for commanding a Precise Automation robot."""

    def __init__(self):
        self.connection = TCSConnection()
        self.isSelected = False
        self.isAttached = False
        self.isHp = False
        self.isHomed = False

    # Telnet communication
    def connect(self, host, port):
        """Opens connection to TCS and queries for basic robot state information.

        Args:
            host (str): The IP address of the robot.
            port (int): The port number to connect to (10000 for status, 10100 for motion)
        """
        self.connection.Connect(host, port)
        self.hp()
        self.selectRobot()
        self.attach()
        self.getHomedState()

    def disconnect(self):
        """Closes connection to TCS."""
        self.connection.Disconnect()

    # Standard Commands
    def nop(self):
        """No operation. Returns standard (empty) response."""
        return self.connection.SendCommand("nop")

    def mspeed(self, speed=None):
        """Sets or gets the global system speed. See documentation for DataID 601."""
        if speed is None:
            response = self.connection.SendCommand("mspeed")
        else:
            if 0 <= speed <= 100:
                response = self.connection.SendCommand("mspeed {}".format(speed))
            else:
                raise Exception("Invalid speed in mspeed command")
        return response

    def attach(self, arg1=None):
        """Attaches or releases the robot. The robot must be attached to allow motion commands."""
        if arg1 is None:
            response = self.connection.SendCommand("attach")
            self.isAttached = bool(int(response.message))
        else:
            response =  self.connection.SendCommand("attach {}".format(arg1))
            if response.success and arg1 == 1:
                self.isAttached = True
            elif response.success and arg1 == 0:
                self.isAttached = False
        return response

    def selectRobot(self, arg1=None):
        """Changes the robot associated with this com link. Does not affect the operation of attachment state of the robot."""
        if arg1 is None:
            response = self.connection.SendCommand("selectRobot")
            self.isSelected = bool(int(response.message))
        else:
            response = self.connection.SendCommand("selectRobot {}".format(arg1))
            if response.success and arg1 > 0:
                self.isSelected = True
            elif response.success and arg1 == 0:
                self.isSelected = False
        return response

    def hp(self, cmd=None, waitTime=0):
        """Enables or disables the robot high power."""
        if cmd is None and waitTime == 0:
            response = self.connection.SendCommand("hp")
            self.isHp = bool(int(response.message))
        else:
            response = self.connection.SendCommand("hp {} {}".format(cmd, waitTime))
            if response.success and cmd == 0:
                self.isHp = False
            elif response.success and cmd == 1:
                # wait for power to be enabled
                for i in range(0, 20):
                    self.hp()
                    if self.isHp: break
                    time.sleep(0.5)
            return response

    def home(self):
        """Homes the robot associated with this thread. Requires power to be enabled and robot to be attached."""
        response = self.connection.SendCommand("home")
        if response.success:
            self.isHomed = True
        else:
            self.getHomedState()
        return response

    def waitForEOM(self):
        """Waits for the robot to reach the end of the current motion."""
        return self.connection.SendCommand("waitForEOM")

    def halt(self):
        """Stops the current robot immediately but leaves power on."""
        return self.connection.SendCommand("halt")

    def whereJ(self):
        """Returns the current Joint position for the selected robot. Response is 'axis1 axis2 ... axisn'."""
        return self.connection.SendCommand("wherej", mute)

    def whereC(self, mute=False):
        """Returns the current Cartesian position for the selected robot. Response is 'X Y Z yaw pitch roll config'."""
        return self.connection.SendCommand("wherec", mute)

    def tool(self, toolOffset=None):
        """Sets or gets the robot tool transformation. The robot must be attached."""
        if toolOffset is None:
            return self.connection.SendCommand("tool")
        else:
            return self.connection.SendCommand("tool {}".format(toolOffset))

    def sysState(self, mute=False):
        """Returns the global system state code. See documentation for DataID 234."""
        return self.connection.SendCommand("sysState", mute)

    def payload(self, arg1):
        """Sets or gets the payload for the currently selected robot."""
        if arg1 is None:
            return self.connection.SendCommand("payload")
        else:
            if 0 <= arg1 <= 100:
                return self.connection.SendCommand("payload {}".format(arg1))
            else:
                raise Exception("Invalid input {} to payload command. Value must be 0-100".format(arg1))

    # Location and Profile Commands
    def profile(self, arg1=None, arg2=None, arg3=None, arg4=None, arg5=None, arg6=None, arg7=None, arg8=None, arg9=None):
        """Sets or gets all profile properties at once.
        Get returns 'Speed Speed2 Accel Decel AccelRamp DecelRamp InRange Straight'."""
        if all(v is None for v in [arg2, arg3, arg3, arg5, arg6, arg7, arg8, arg9]):
            return self.connection.SendCommand("profile {}".format(arg1))
        elif all(v is not None for v in [arg1, arg2, arg3, arg4, arg5, arg6, arg7, arg8, arg9]):
            return self.connection.SendCommand("profile {} {} {} {} {} {} {} {} {}".format(arg1, arg2, arg3, arg4, arg5, arg6, arg7, arg8, arg9))
        else:
            raise Exception("Invalid number of arguments")

    def hereJ(self, arg1):
        """Records the current position of the selected robot into the specified location. The type is automatically set to 'Joint'"""
        return self.connection.SendCommand("hereJ {}".format(arg1))
    
    def hereC(self, arg1):
        """Records the current position of the selected robot into the specified location. The type is automatically set to 'Cartesian'"""
        return self.connection.SendCommand("hereC {}".format(arg1))

    def loc(self, arg1):
        """Returns the specified location value, including any offsets due to pallet indexing."""
        return self.connection.SendCommand("loc {}".format(arg1))
        
    def locXYZ(self, arg1, arg2=None, arg3=None, arg4=None, arg5=None, arg6=None, arg7=None):
        """Gets or sets location Cartesian position. Error if you attempt to get Cartesian position from an angles type location."""
        if all(v is None for v in [arg2, arg3, arg3, arg5, arg6, arg7]):
            return self.connection.SendCommand("locXYZ {}".format(arg1))
        elif all(v is not None for v in [arg1, arg2, arg3, arg4, arg5, arg6, arg7]):
            return self.connection.SendCommand("locXYZ {} {} {} {} {} {} {}".format(arg1, arg2, arg3, arg4, arg5, arg6, arg7))
        else:
            raise Exception("Invalid number of arguments")

    # Save/Load Commands
    def storeFile(self, arg1=None):
        """Writes the station and profile data for the current robot to the specified file."""
        if arg1 is None:
            return self.connection.SendCommand("storeFile")
        else:
            return self.connection.SendCommand("storeFile {}".format(arg1))
        
    def loadFile(self, arg1=None):
        """Loads all location and profile data from the specified file. All previous location and profile data is lost."""
        if arg1 is None:
            return self.connection.SendCommand("loadFile")
        else:
            return self.connection.SendCommand("loadFile {}".format(arg1))

    # PARobot Module Commands
    def freeMode(self, arg1):
        """Activates or deactivates free mode. The robot must be attached."""
        return self.connection.SendCommand("freeMode {}".format(arg1))

    def graspData(self, arg1=None, arg2=None, arg3=None):
        """Gets or sets the data to be used for the next PickPlate grip operation."""
        if arg1 is None and arg2 is None and arg3 is None:
            return self.connection.SendCommand("graspData")
        else:
            return self.connection.SendCommand("graspData {} {} {}".format(arg1, arg2, arg3))

    def teachPlate(self, arg1, arg2=50):
        """Sets the specified plate location to the current position and configuration."""
        return self.connection.SendCommand("teachPlate {} {}".format(arg1, arg2))

    def pickPlate(self, arg1, arg2=0, arg3=0):
        """Moves to a predifined position and picks up a plate."""
        return self.connection.SendCommand("pickPlate {} {} {}".format(arg1, arg2, arg3))

    def placePlate(self, arg1, arg2=0, arg3=0):
        """Moves to a predefined position and places a plate."""
        return self.connection.SendCommand("placePlate {} {} {}".format(arg1, arg2, arg3))

    def homeAllIfNoPlate(self):
        """Tests if the gripper is holding a plate. If not, enables power and homes. Returns 0 if plate detected; returns -1 if no plate and command succeeded."""
        return self.connection.SendCommand("homeAll_IfNoPlate")

    # Additional, Helpful (non-standard) Commands
    def getHomedState(self):
        if (self.connection.port == 10000):
            # homed state not returned from status port
            return
        response = self.connection.SendCommand("pd 2800")
        if response.success:
            self.isHomed = bool(int(response.message))
        return self.isHomed

    def getLastError(self):
        lastError = self.connection.SendCommand("pd 320")
        return int(lastError)

    # Raw String Command
    def rawString(self, cmd):
        return self.connection.SendCommand(cmd)



class TCSConnection:
    """A TCP/IP communication manager to establish and route messages to TCS. This is
    typically generated as part of a TCSRobot instance."""
    def __init__(self):
        self.host = None
        self.port = None
        self.connection = None
        self.verbose = False
        self.log = ""
        self.logUpdate = None

    def Connect(self, host, port):
        """Establishes connection to a TCS port."""
        self.host = host
        self.port = port
        self.TCSPrint("Initializing connection to {}:{}...".format(host, port))
        try:
            self.connection = telnetlib.Telnet(self.host, self.port, 5)
        except:
            self.TCSPrint("Could not establish connection")
            raise Exception("Could not establish connection")
        self.TCSPrint("Connection ready")
        self.SendCommand("mode 0") #initialize to "computer" mode

    def SendCommand(self, command, mute=False):
        """Sends a string command to TCS and returns the response as a TCSResponse."""
        response = TCSResponse()
        try:
            if (self.connection is None):
                raise Exception("No connection established yet")

            self.TCSPrint("> {}".format(command), mute)
            self.connection.write((command.encode("ascii") + b"\n"))

            reply = self.connection.read_until(b"\r\n").rstrip().decode("ascii")
            self.TCSPrint("< {}".format(reply), mute)
            
            # parse reply in mode 0 (see TCS docs for format spec)
            if reply == "0":
                response.success = True
            elif reply[0] == "0":
                response.success = True
                response.message = reply[2:]
            elif reply[0] == "-":
                response.success = False
                response.error = reply
                raise Exception("TCS error: {}".format(reply))
            else:
                # invalid response? mode not correct?
                raise Exception("Invalid TCS response: '{}'".format(reply))

        except Exception as e:
            print(e)

        return response

    def Disconnect(self):
        """Closes connection on this port."""
        self.SendCommand("exit")
        self.connection.close()


    def TCSPrint(self, text, mute=False):
        """Convenience command to capture data sent to and from TCS."""
        if mute:
            return
        if self.verbose:
            print(text)
        self.log += "{}\n".format(text)
        if self.logUpdate is not None:
            self.logUpdate()



class TCSResponse:
    """A container class for the response from TCS."""
    def __init__(self, success=False, error=None, message=None):
        self.success = False
        self.error = None
        self.message = None

