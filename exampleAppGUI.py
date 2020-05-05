from tkinter import ttk

from tkinter import *
from tkinter.ttk import *


APP_TITLE = "TCS Example Application"
APP_AUTHOR = "Precise Automation"
APP_VERSION = "1.0"
APP_COLOR_1 = "#326edb"



class InitConnectionGUI:
    def __init__(self, defaultIP="192.168.0.1"):
        self.hostIP = None
        self.defaultIP = defaultIP
        self.window = Tk()
        self.window.title("{}: Initialize Connection".format(APP_TITLE))

        # Ttk style
        s = ttk.Style()
        s.configure("TButton", padding=(6, 3), width=0, relief="flat")
        s.configure("TFrame") #, background=APP_COLOR_1)
        s.configure("h1.TLabel", anchor="center", font="TkDefaultFont 12") #, background=APP_COLOR_1, foreground="#fff")
        s.configure("h2.TLabel", anchor="center", font="TkDefaultFont 8") #, background=APP_COLOR_1, foreground="#fff")

        self.showDialogue(ConnectingError=False)

    def getHostIP(self):
        while self.hostIP is None:
            self.window.update_idletasks()
            self.window.update()
        self.showConnecting()
        return self.hostIP

    def connectButtonPress(self):
        self.hostIP = self.ip_entry.get()

    def showDialogue(self, ConnectingError=True):
        self.hostIP = None
        for widget in self.window.winfo_children():
            widget.destroy()

        #Frame
        self.window.columnconfigure(0, weight=1)
        self.splashframe = ttk.Frame(self.window, padding=12)
        self.splashframe.grid(sticky="news")
        self.splashframe.columnconfigure(0, weight=1)

        #Title
        Label(self.splashframe, style="h1.TLabel", text=APP_TITLE).grid(row=0, column=0, columnspan=3, sticky="news")
        Label(self.splashframe, style="h2.TLabel", text="{}, v{}".format(APP_AUTHOR, APP_VERSION)).grid(row=1, column=0, columnspan=3, pady=(0,18), sticky="news")

        self.ip_entry = ttk.Entry(self.splashframe, width=25, font="verdana 8")
        self.ip_entry.grid(row=2, column=0, sticky="news")
        self.ip_entry.insert(END, self.defaultIP)
        self.ip_entry.bind('<Return>', self.connectButtonPress)
        Button(self.splashframe, text="Connect", command=self.connectButtonPress).grid(row=2, column=1, padx=(8,0), sticky="news")
        Button(self.splashframe, text="Exit", command=self.close).grid(row=2, column=2, padx=(8,0), sticky="news")

        if(ConnectingError):
            Label(self.splashframe, text="Could not connect with provided IP.", background="#fdd", foreground="#f00", anchor=W).grid(row=3, column=0, columnspan=3, pady=(8,0), sticky="news")

        self.window.update_idletasks()
        self.window.update()

        #Position the Window
        sheight, swidth, wheight, wwidth = (self.window.winfo_screenheight(), self.window.winfo_screenwidth(), self.window.winfo_height(), self.window.winfo_width())
        locx, locy = ((int(swidth/2)-int(wwidth/2)), (int(sheight/2)-int(wheight/2)))
        screenOffset = "+"+str(locx)+"+"+str(locy)
        self.window.geometry(screenOffset)

        #self.window.overrideredirect(1)
        self.window.update_idletasks()
        self.window.update()

    def showConnecting(self):
        for widget in self.window.winfo_children():
            widget.destroy()

        self.window.title("{}: Connecting...".format(APP_TITLE))

        #Frame
        self.window.columnconfigure(0, weight=1)
        self.splashframe = ttk.Frame(self.window, padding=12)
        self.splashframe.grid(sticky="news")
        self.splashframe.columnconfigure(0, weight=1)

        #Title
        #Label(self.splashframe, style="h1.TLabel", text=APP_TITLE).grid(row=0, column=0, columnspan=3, sticky="news")
        #Label(self.splashframe, style="h2.TLabel", text="{}, v{}".format(APP_AUTHOR, APP_VERSION)).grid(row=1, column=0, columnspan=3, pady=(0,18), sticky="news")

        Label(self.splashframe, text="Connecting...", anchor="center", font="TkDefaultFont 8 italic").grid(row=2, column=0, columnspan=3, sticky="ew", padx=80, pady=30)

        self.window.update_idletasks()
        self.window.update()

    def close(self):
        self.window.destroy()



class ExampleApplicationGUI:
    def __init__(self, app, hostIP):
        self.app = app

        self.locationRows = []
        self.actionRows = []

        self.window = Tk()

        self.window.title("{} ({})".format(APP_TITLE, hostIP))
        self.window.configure(padx=6, pady=6)
        self.window.columnconfigure(0, weight=2)
        self.window.columnconfigure(1, weight=2)
        
        # ttk configure
        fp = 4
        s = ttk.Style()
        s.configure("TButton", padding=(6, 3), width=0, relief="flat")
        s.configure("robot.TButton", padding=(6))
        s.configure("estop.TButton", padding=(24, 12))
        s.configure("h1.TLabel", anchor="w", padding=(0, 0, 0, 8))
        s.configure("state.TLabel", anchor="center", foreground="#fff", padding=12)
        s.configure("main.TLabelframe", padding=fp)
        s.configure("main.TLabelframe.Label", font="TkDefaultFont 8 italic", foreground=APP_COLOR_1)
        s.configure("clabel.TLabel", font="TkDefaultFont 8", foreground="#666")
        s.configure("ccoord.TLabel", font="Consolas 8", foreground="#666")
        s.configure("speed.TScale", bigincrement=2)

        self.ipString = StringVar()
        self.ipString.set(hostIP)

        self.sysState = StringVar()
        self.sysState.set("Undefined")

        self.debugger1 = None
        self.debugger1MessageArray = []
        self.debugger2 = None
        self.debugger2MessageArray = []


        self.Connection_frame =     Labelframe(self.window, style="main.TLabelframe", text="Connection")
        self.Robot_frame =          Labelframe(self.window, style="main.TLabelframe", text="Robot")
        self.Location_frame =       Labelframe(self.window, style="main.TLabelframe", text="Locations")
        self.Action_frame =         Labelframe(self.window, style="main.TLabelframe", text="Actions")
        self.Log1_frame =           Labelframe(self.window, style="main.TLabelframe", text="Status Thread Log")
        self.Log2_frame =           Labelframe(self.window, style="main.TLabelframe", text="Motion Thread Log")

        self.Connection_frame.grid( row=0, column=0, padx=fp, pady=fp, sticky="news")
        self.Robot_frame.grid(      row=0, column=1, padx=fp, pady=fp, sticky="news") #, columnspan=2)
        self.Location_frame.grid(   row=1, column=0, padx=fp, pady=fp, sticky="news")
        self.Action_frame.grid(     row=1, column=1, padx=fp, pady=fp, sticky="news")
        self.Log1_frame.grid(       row=2, column=0, padx=fp, pady=fp, sticky="news")
        self.Log2_frame.grid(       row=2, column=1, padx=fp, pady=fp, sticky="news")
        
        #Connection Frame
        self.Connection_frame.grid_columnconfigure(1, weight=1)
        Label(self.Connection_frame, text="Robot IP:", anchor=W).grid(row=1, column=0, padx=(0, 8))
        Entry(self.Connection_frame, textvariable=self.ipString).grid(row=1, column=1, sticky="ew")
        
        #Robot Frame
        self.Robot_frame.grid_columnconfigure(0, weight=1)
        self.Robot_frame.columnconfigure(1, weight=1)
        self.Robot_frame.columnconfigure(2, weight=1)
        self.Robot_frame.columnconfigure(3, weight=1)
        #self.Robot_frame.grid_columnconfigure(1, weight=1)

        #self.RobotLeft_frame = Frame(self.Robot_frame)
        #self.RobotLeft_frame.grid(row=0, column=0, sticky="news", padx=(0,8))
        #self.RobotLeft_frame.columnconfigure(0, weight=1)
        #self.RobotLeft_frame.columnconfigure(1, weight=1)
        #self.RobotLeft_frame.columnconfigure(2, weight=1)
        #self.RobotLeft_frame.columnconfigure(3, weight=1)
        #self.RobotLeft_frame.columnconfigure(4, weight=1)
        #self.RobotLeft_frame.columnconfigure(5, weight=1)

        #self.RobotRight_frame = Frame(self.Robot_frame)
        #self.RobotRight_frame.grid(row=0, column=1, sticky="news")
        #self.RobotRight_frame.columnconfigure(0, weight=1)
        #self.RobotRight_frame.columnconfigure(1, weight=1)
        #self.RobotRight_frame.columnconfigure(2, weight=1)
        #self.RobotRight_frame.columnconfigure(3, weight=1)
        
        # (left)
        #Label(self.RobotLeft_frame, text="x",     anchor="center", style="clabel.TLabel").grid(row=0, column=0, sticky="news")
        #Label(self.RobotLeft_frame, text="y",     anchor="center", style="clabel.TLabel").grid(row=0, column=1, sticky="news")
        #Label(self.RobotLeft_frame, text="z",     anchor="center", style="clabel.TLabel").grid(row=0, column=2, sticky="news")
        #Label(self.RobotLeft_frame, text="yaw",   anchor="center", style="clabel.TLabel").grid(row=0, column=3, sticky="news")
        #Label(self.RobotLeft_frame, text="pitch", anchor="center", style="clabel.TLabel").grid(row=0, column=4, sticky="news")
        #Label(self.RobotLeft_frame, text="roll",  anchor="center", style="clabel.TLabel").grid(row=0, column=5, sticky="news")
        #self.CCoordX        = Label(self.RobotLeft_frame, text="----.--", anchor="center", style="ccoord.TLabel")
        #self.CCoordY        = Label(self.RobotLeft_frame, text="----.--", anchor="center", style="ccoord.TLabel")
        #self.CCoordZ        = Label(self.RobotLeft_frame, text="----.--", anchor="center", style="ccoord.TLabel")
        #self.CCoordYaw      = Label(self.RobotLeft_frame, text="----.--", anchor="center", style="ccoord.TLabel")
        #self.CCoordPitch    = Label(self.RobotLeft_frame, text="----.--", anchor="center", style="ccoord.TLabel")
        #self.CCoordRoll     = Label(self.RobotLeft_frame, text="----.--", anchor="center", style="ccoord.TLabel")
        #self.CCoordX.grid(      row=1, column=0, sticky="news")
        #self.CCoordY.grid(      row=1, column=1, sticky="news")
        #self.CCoordZ.grid(      row=1, column=2, sticky="news")
        #self.CCoordYaw.grid(    row=1, column=3, sticky="news")
        #self.CCoordPitch.grid(  row=1, column=4, sticky="news")
        #self.CCoordRoll.grid(   row=1, column=5, sticky="news")
        #self.speedScale = Scale(self.RobotLeft_frame, from_=0, to=100, style="speed.TScale")
        #self.speedScale.grid(row=2, column=0, columnspan=6, padx=8, pady=(8,0), stick="ew")

        # (right)
        self.sysStateLabel = Label(self.Robot_frame, textvariable=self.sysState, style="state.TLabel")
        self.sysStateLabel.grid(row=0, column=0, columnspan=4, sticky="news", pady=(0,8))
        self.enableButton = Button(self.Robot_frame, style="robot.TButton", text="Enable", command=self.Enable)
        self.homeButton = Button(self.Robot_frame, style="robot.TButton", text="Home", command=self.Home)
        self.freeButton = Button(self.Robot_frame, style="robot.TButton", text="Free", command=self.Free)
        self.lockButton = Button(self.Robot_frame, style="robot.TButton", text="Lock", command=self.Lock)
        self.enableButton.grid(row=1, column=0, sticky="ew")
        self.homeButton.grid(row=1, column=1, sticky="ew")
        self.freeButton.grid(row=1, column=2, sticky="ew")
        self.lockButton.grid(row=1, column=3, sticky="ew")
        Button(self.Robot_frame, style="estop.TButton", text="ESTOP", command=self.EStop).grid(row=0, column=5, rowspan=2, sticky="news", padx=(8,0))





        #Location Frame
        self.Location_frame.grid_columnconfigure(0, weight=1)
        self.LocationRows_frame = Frame(self.Location_frame)
        self.LocationRows_frame.grid(row=0, column=0, columnspan=3, sticky="news")
        # (location rows dynamically added with application start up)
        self.LocationButton_frame = Frame(self.Location_frame)
        self.LocationButton_frame.grid(row=1, column=0, columnspan=3, pady=4, sticky="ew")
        self.loadButton = Button(self.LocationButton_frame, text="Load", command=self.LoadLocations)
        self.saveButton = Button(self.LocationButton_frame, text="Save", command=self.SaveLocations)
        self.loadButton.pack(side="right")
        self.saveButton.pack(side="right", padx=4)

        #Actions Frame
        self.Action_frame.grid_columnconfigure(0, weight=1)
        self.ActionRows_frame = Frame(self.Action_frame)
        self.ActionRows_frame.grid(row=0, column=0, sticky="news")
        # (action rows dynamically added with application start up)
        self.ActionButton_frame = Frame(self.Action_frame)
        self.ActionButton_frame.grid(row=1, column=0, pady=8, sticky="ew")
        self.haltButton = Button(self.ActionButton_frame, text="Halt", command=self.haltActions)
        self.haltButton.pack(side="right")
        Button(self.ActionButton_frame, text="Run", command=self.runActions).pack(side="right", padx=4)

        
        #Logs
        self.Log1_frame.columnconfigure(0, weight=1)
        self.Log2_frame.columnconfigure(0, weight=1)

        self.debugger1 = Text(self.Log1_frame, width=36, height=16, fg="#666", font=("Consolas 8"))
        self.debugger1.grid(row=0, sticky="ew")
        self.debugger2 = Text(self.Log2_frame, width=36, height=16, fg="#666", font=("Consolas 8"))
        self.debugger2.grid(row=0, sticky="ew")
        
        self.sb1 = Scrollbar(self.Log1_frame)
        self.sb1.grid(row=0, column=1, sticky="ns")
        self.sb2 = Scrollbar(self.Log2_frame)
        self.sb2.grid(row=0, column=1, sticky="ns")
        self.debugger1.config(yscrollcommand=self.sb1.set)
        self.debugger2.config(yscrollcommand=self.sb2.set)
        self.sb1.config(command=self.debugger1.yview)
        self.sb2.config(command=self.debugger2.yview)

        self.ManualEntry1_frame = Frame(self.Log1_frame, padding=(0,8,0,0))
        self.ManualEntry2_frame = Frame(self.Log2_frame, padding=(0,8,0,0))

        self.ManualEntry1_frame.grid(row=1, column=0, columnspan=2, sticky="ew")
        self.ManualEntry1_frame.grid_columnconfigure(0, weight=1)
        self.rawStatusInput = Entry(self.ManualEntry1_frame)
        self.rawStatusInput.grid(row=0, column=0, sticky="news", padx=(0,8))
        Button(self.ManualEntry1_frame, text="Send", command=self.SendRawStatus).grid(row=0, column=1)
        
        self.ManualEntry2_frame.grid(row=1, column=0, columnspan=2, sticky="ew")
        self.ManualEntry2_frame.grid_columnconfigure(0, weight=1)
        self.rawMotionInput = Entry(self.ManualEntry2_frame)
        self.rawMotionInput.grid(row=0, column=0, sticky="news", padx=(0,8))
        Button(self.ManualEntry2_frame, text="Send", command=self.SendRawMotion).grid(row=0, column=1)

        #self.window.update_idletasks()
        #self.window.update()



    def generateLocationRows(self, locations):
        for i in range(len(locations)):
            self.locationRows.append(LocationRow(self, self.LocationRows_frame, i, locations[i]))

    def updateLocationRows(self, locations):
        for i in range(len(locations)):
            self.locationRows[i].updateLocation(locations[i])
            self.locationRows[i].updateDisplay()

    def recordLocation(self, idx):
        return self.app.recordLocation(idx)

    def generateActionRows(self, actions, locations):
        for i in range(len(actions)):
            self.actionRows.append(ActionRow(self.ActionRows_frame, i, locations, actions[i]))
    

    def runActions(self):
        actions = []
        for i in range(len(self.actionRows)):
            a = self.actionRows[i].getAction()
            if a:
                actions.append(a)
        self.app.runActions(actions, self.actionsFinished)

    def actionsFinished(self):
        print("actions finished")
        
    def haltActions(self):
        self.app.halt(self.haltCallback)
        self.haltButton.configure(state=DISABLED)

    def haltCallback(self):
        self.haltButton.configure(state=NORMAL)

    def Free(self):
        self.app.free(self.FreeCallback)
        self.freeButton.configure(state=DISABLED)

    def FreeCallback(self):
        self.freeButton.configure(state=NORMAL)

    def Lock(self):
        self.app.lock(self.LockCallback)
        self.lockButton.configure(state=DISABLED)

    def LockCallback(self):
        self.lockButton.configure(state=NORMAL)

    def Enable(self):
        self.app.enable(self.EnableCallback)
        self.enableButton.configure(state=DISABLED)

    def EnableCallback(self):
        self.enableButton.configure(state=NORMAL)

    def Home(self):
        self.app.home(self.HomeCallback)
        self.homeButton.configure(state=DISABLED)

    def HomeCallback(self):
        self.homeButton.configure(state=NORMAL)

    def EStop(self):
        self.app.estop()

    def SaveLocations(self):
        self.app.saveToFlash(self.SaveLocationsCallback)
        self.saveButton.configure(state=DISABLED)

    def SaveLocationsCallback(self):
        self.saveButton.configure(state=NORMAL)

    def LoadLocations(self):
        self.app.loadFromFlash(self.LoadLocationsCallback)
        self.loadButton.configure(state=DISABLED)

    def LoadLocationsCallback(self):
        self.loadButton.configure(state=NORMAL)

    def SendRawStatus(self):
        cmd = self.rawStatusInput.get()
        self.app.statusRaw(cmd)

    def SendRawMotion(self):
        cmd = self.rawMotionInput.get()
        self.app.motionRaw(cmd)

    def updateStatusLog(self, text):
        self.debugger1.delete(1.0, END)
        self.debugger1.insert(END, text)
        self.debugger1.see(END)

    def updateMotionLog(self, text):
        self.debugger2.delete(1.0, END)
        self.debugger2.insert(END, text)
        self.debugger2.see(END)

    def updateSysState(self, code):
        state = StateLookup().GetShortState(code)
        self.sysState.set(state)
        self.sysStateLabel.configure(background=StateLookup().GetStateColor(code))

    def updateCartesianReadout(self, loc):
        #self.CCoordX.configure(     text="{:4.2f}".format(loc.x))
        #self.CCoordY.configure(     text="{:4.2f}".format(loc.y))
        #self.CCoordZ.configure(     text="{:4.2f}".format(loc.z))
        #self.CCoordYaw.configure(   text="{:4.2f}".format(loc.yaw))
        #self.CCoordPitch.configure( text="{:4.2f}".format(loc.pitch))
        #self.CCoordRoll.configure(  text="{:4.2f}".format(loc.roll))
        return







class LocationRow:
    def __init__(self, appGUI, frame, row, appLocation):
        self.appGUI = appGUI
        self.appLocation = appLocation
        self.ID = row + 1
        
        frame.columnconfigure(1, weight=1)
        Label(frame, text=self.appLocation.name).grid(row=row, column=0, sticky="ew")
        self.coordsLabel = Label(frame, font="TkDefaultFont 8", foreground="#666", width=30)
        self.coordsLabel.grid(row=row, column=1, padx=(10,10), sticky="ew")
        Button(frame, text="Record", command=self.recordPress).grid(row=row, column=2, sticky="ew")

        self.updateDisplay()

    def updateLocation(self, appLocation):
        self.appLocation = appLocation

    def updateDisplay(self):
        self.coordsLabel.config(text=self.coordsToString(self.appLocation))

    def recordPress(self):
        self.appLocation = self.appGUI.recordLocation(self.ID)
        self.updateDisplay()

    def coordsToString(self, loc):
        s = "{:.0f}, {:.0f}, {:.0f}, {:.0f}, {:.0f}, {:.0f}".format(loc.x, loc.y, loc.z, loc.yaw, loc.pitch, loc.roll)
        return s


class ActionRow:
    def __init__(self, frame, row, locationList, appAction):

        self.locationList = locationList
        self.appAction = appAction
        self.ID = row
        self.sourceName = None
        self.destinationName = None

        self.locationStrings = [loc.name for loc in self.locationList]

        self.pickCombo = ttk.Combobox(frame, values=self.locationStrings)
        self.pickCombo.grid(row=row, column=0, sticky="news", pady=4, padx=(0,4))
        Label(frame, text=">").grid(row=row, column=1)
        self.placeCombo = ttk.Combobox(frame, values=self.locationStrings)
        self.placeCombo.grid(row=row, column=2, sticky="news", pady=4, padx=(4,0))

    def getAction(self):
        # Get source and validate
        self.sourceName = self.pickCombo.get()
        if self.sourceName in self.locationStrings:
            self.appAction.sourceIdx = self.locationStrings.index(self.sourceName) + 1
        else:
            print("invalid source")
            return None

        # Get destination and validate
        self.destinationName = self.placeCombo.get()
        if self.destinationName in self.locationStrings:
            self.appAction.destinationIdx = self.locationStrings.index(self.destinationName) + 1
        else:
            print("invalid destination")
            return None

        return self.appAction


        







class StateLookup:
    def __init__(self):

        self.colors = {
            "red":      "#ff5964",
            "yellow":   "#FFE066",
            "green":    "#06D6A0",
            "blue":     "#35A7FF",
            "darkblue": "#38618C",
            "grey":     "#333333"
        }

        # Look at documentation for DataID 234 for more information
        # Format:
        # state code: ("short description", "official description") 
        self.states = {
            0:  (self.colors["grey"],       "Initializing",    "Power off, Initializing at startup"),
            1:  (self.colors["red"],        "Fatal error",     "Power off, fatal error"),
            2:  (self.colors["grey"],       "Power Off",       "Power off, restarting after fault"),
            3:  (self.colors["grey"],       "Disabling",       "Power going down, no fault"),
            4:  (self.colors["grey"],       "Disabling",       "Power going down, fault"),
            5:  (self.colors["grey"],       "Power Off",       "Power off, fault occurred"),
            6:  (self.colors["grey"],       "Power Off",       "Power off, waiting for CANopen power request FALSE"),
            7:  (self.colors["grey"],       "Power Off",       "Power off, waiting for power request TRUE"),
            8:  (self.colors["darkblue"],   "Enabling",        "Power on, enabling amplifiers"),
            9:  (self.colors["darkblue"],   "Commutating",     "Power on, performing commutation"),
            10: (self.colors["darkblue"],   "Enabling",        "Power on, enabling servos, releasing brakes"),
            11: (self.colors["blue"],       "Power On",        "Power on, waiting for auto mode"),
            12: (self.colors["blue"],       "Power On",        "Power on, executing auto mode"),
            15: (self.colors["grey"],       "Power Off",       "Power off, hard e-stop asserted"),
            20: (self.colors["blue"],       "Power On",        "Power on, ready to have GPL attach robot"),
            21: (self.colors["blue"],       "Power On",        "GPL project executing and attached to a robot"),
            22: (self.colors["grey"],       "Other",           "Digital input to fixed positions (DIO MotionBlocks) executing"),
            23: (self.colors["grey"],       "Other",           "Analog input controlled velocity executing "),
            24: (self.colors["grey"],       "Other",           "Analog input controlled torque executing "),
            25: (self.colors["grey"],       "Other",           "Master/slave mode executing"),
            26: (self.colors["grey"],       "Other",           "CANopen via CAN net executing"),
            27: (self.colors["grey"],       "Other",           "CANopen via serial line executing"),
            28: (self.colors["yellow"],     "Homing",          "Homing executing"),
            29: (self.colors["yellow"],     "Jog Mode",        "Virtual MCP Jog mode executing"),
            30: (self.colors["grey"],       "Other",           "External trajectory mode executing"),
            31: (self.colors["yellow"],     "Jog Mode",        "Hardware MCP Jog mode executing")
        }
        return

    def GetShortState(self, code):
        if code in self.states:
            return self.states[code][1]
        else:
            return "(No communication)"

    def GetStateColor(self, code):
        if code in self.states:
            return self.states[code][0]

