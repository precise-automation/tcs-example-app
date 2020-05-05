# Precise Automation TCS Example Application

The TCS Example Application is a simple scheduling interface written in Python, provided as an example on how to integrate custom software with a Precise Automation robot. To that end, this example includes the following:

  * Best practice for commonly used commands (enable power, home, halt, etc.)
  * How to manage two separate connections to the robot for motion and status
  * How a queue might be implemented to schedule robot commands
  * How a heartbeat might be established to poll for status changes

The application makes use of the standard TCP/IP Command Server (TCS) software running on the robot. For more information on TCS, [download the latest TCS software](http://preciseautomation.com/Support/LatestSoftwareUpdates.html) from the Precise Automation website and look through its documentation.

This package was created with Python 3.8.1. 



## Installation

The example project can be run by simply cloning this entire repository and following the Running the Example section.



## Usage Requirements

In order to use the API with a Precise Automation Robot, the Robot must be running the TCS project. Failure to do so will result in a connection timeout error in the Python file. In addition, some commands of the commonly used commands that have been implemented make use of TCS plugins. Without purchase of the plugins, the issuing of such commands will result in error.



## Running the Example

In a command terminal, navigate to the Advanced Example Client Directory and type the following.

```bash
python exampleApp.py
```

Below is the main window of the GUI (v1.0)

![alt text](/Documentation/images/gui-1.0.png "Screenshot of the main window with power enabled")



## Writing Your Own Application

In an attempt to keep this example as modular as possible, the core interface functionality was condensed into a single file, **TCSInterface.py**. To begin writing your own application, simply include this file in your project. More information can be found in its [documentation](Documentation/TCS%20Interface.md).



## License

*Permission is granted to customers of Precise Automation to use this software for any purpose, including commercial applications, and to alter it and redistribute it freely, so long as this notice is included with any modified or unmodified version of this software.*

*This software is provided "as is," without warranty of any kind, express or implied. In no event shall Precise Automation be held liable for any direct, indirect, incidental, special or consequential damages arising out of the use of or inability to use this software.*
