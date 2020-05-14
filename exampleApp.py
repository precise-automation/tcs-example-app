import threading
import time
import queue

from TCSInterface.TCSInterface import *
from exampleAppGUI import *



DEFAULT_IP = "192.168.0.2"
STATUS_PORT = 10000
MOTION_PORT = 10100
HEARTBEAT_INTERVAL = 0.5 #sec
LOCATION_COUNT = 5
ACTION_COUNT = 3
SAVE_PATH = "/flash/exampleAppLocations.gpo" # (directory must already exist)



class ExampleApplication:
    def __init__(self):
        self.gui = None
        self.hostIP = None
        self.statusQueue = queue.Queue(maxsize=40)
        self.motionQueue = queue.Queue(maxsize=40)
        self.statusThread = threading.Thread(target=self.statusThreadTarget, daemon=True)
        self.motionThread = threading.Thread(target=self.motionThreadTarget, daemon=True)
        self.statusBusy = False
        self.motionBusy = False
        self.statusRobot = TCSRobot()
        self.motionRobot = TCSRobot()
        self.heartbeatThread = threading.Thread(target=self.heartbeatThreadTarget, daemon=True)

        self.statusRobot.connection.verbose = True
        self.motionRobot.connection.verbose = True
        self.statusLog = None
        self.motionLog = None

        self.appLocations = []
        self.appActions = []

        self.initConnection()
        self.startApplication()

    def initConnection(self):
        dialogue = InitConnectionGUI(defaultIP=DEFAULT_IP)
        while True:
            # wait for IP input
            hostIP = dialogue.getHostIP()
            try:
                # attempt connection
                self.statusRobot.connect(hostIP, STATUS_PORT)
                self.motionRobot.connect(hostIP, MOTION_PORT)
                self.hostIP = hostIP
                dialogue.close()
                break
            except:
                # error connecting. ask for IP again
                dialogue.showDialogue()
        return

    def startApplication(self):

        self.gui = ExampleApplicationGUI(self, self.hostIP)
        self.statusRobot.connection.logUpdate = lambda: self.gui.updateStatusLog(self.statusRobot.connection.log)
        self.motionRobot.connection.logUpdate = lambda: self.gui.updateMotionLog(self.motionRobot.connection.log)
        self.statusThread.start()
        self.motionThread.start()
        self.heartbeatThread.start()

        self.statusRobot.connection.logUpdate()
        self.motionRobot.connection.logUpdate()
        
        for i in range(LOCATION_COUNT):
            self.appLocations.append(self.getLocation(i+1))
            self.appLocations[i].name = "Station {}".format(i+1)

        for i in range(ACTION_COUNT):
            self.appActions.append(AppPickPlaceAction())

        self.gui.generateLocationRows(self.appLocations)
        self.gui.generateActionRows(self.appActions, self.appLocations)
        self.gui.window.mainloop()

    def heartbeatThreadTarget(self):
        time.sleep(1)
        self.statusRobot.selectRobot(1)
        self.heartbeat()
        if HEARTBEAT_INTERVAL <= 0:
            return
        while True:
            self.statusQueue.put_nowait(lambda: self.heartbeat())
            time.sleep(HEARTBEAT_INTERVAL)

    def heartbeat(self):
        stateCode = int(self.statusRobot.sysState(mute=True).message)
        self.gui.updateSysState(stateCode)
        loc = AppLocation()
        loc.setInfoFromWhereC(self.statusRobot.whereC(mute=True).message)
        self.gui.updateCartesianReadout(loc)

    def statusThreadTarget(self):
        while True:
            command = self.statusQueue.get()
            self.statusBusy = True
            reply = command()
            self.statusBusy = False

    def motionThreadTarget(self):
        while True:
            command = self.motionQueue.get()
            print("setting motion busy true")
            self.motionBusy = True
            reply = command()
            print("setting motion busy false")
            self.motionBusy = False




    # Calls from GUI

    def estop(self):
        self.statusQueue.put_nowait(lambda: self.statusRobot.hp(0))

    def enable(self, callback=None):
        self.motionQueue.put_nowait(lambda: self.motionRobot.hp(1))
        self.motionQueue.put_nowait(lambda: self.motionRobot.attach(1))
        if callback is not None:
            self.motionQueue.put_nowait(callback)
    
    def home(self, callback=None):
        self.motionQueue.put_nowait(lambda: self.motionRobot.home())
        if callback is not None:
            self.motionQueue.put_nowait(callback)
        
    def free(self, callback=None):
        self.motionQueue.put_nowait(lambda: self.motionRobot.freeMode(0))
        if callback is not None:
            self.motionQueue.put_nowait(callback)
        
    def lock(self, callback=None):
        self.motionQueue.put_nowait(lambda: self.motionRobot.freeMode(-1))
        if callback is not None:
            self.motionQueue.put_nowait(callback)

    def statusRaw(self, cmd, callback=None):
        self.statusQueue.put_nowait(lambda: self.statusRobot.rawString(cmd))
        if callback is not None:
            self.motionQueue.put_nowait(callback)

    def motionRaw(self, cmd, callback=None):
        self.motionQueue.put_nowait(lambda: self.motionRobot.rawString(cmd))
        if callback is not None:
            self.motionQueue.put_nowait(callback)

    def runActions(self, actions, callback=None):
        for i in range(len(actions)):
            self.runSingleAction(actions[i].sourceIdx, actions[i].destinationIdx)

        if callback is not None:
            self.motionQueue.put_nowait(callback)

    def runSingleAction(self, source, destination):
        self.motionQueue.put_nowait(lambda: self.motionRobot.pickPlate(source))
        self.motionQueue.put_nowait(lambda: self.motionRobot.placePlate(destination))

    def halt(self, callback):
        self.statusQueue.put_nowait(lambda: self.haltLoop())
        self.statusQueue.put_nowait(lambda: self.haltCallback())
        if callback is not None:
            self.statusQueue.put_nowait(callback)

    def haltLoop(self):
        # NOTE: Halt will only cancel the current motion, so if a TCS command
        # contains several motion commands (e.g. pickPlate or placePlate), then 
        # halt will need be called until the TCS command returns a value.
        self.statusRobot.halt()
        with self.motionQueue.mutex:
            self.motionQueue.queue.clear()
        while self.motionBusy:
            self.statusRobot.halt()

    def haltCallback(self):
        print("finished halting")

    def saveToFlash(self, callback):
        self.statusQueue.put_nowait(lambda: self.statusRobot.storeFile(SAVE_PATH))
        if callback is not None:
            self.statusQueue.put_nowait(callback)

    def loadFromFlash(self, callback):
        self.statusQueue.put_nowait(lambda: self.loadAndUpdateGUI())
        if callback is not None:
            self.statusQueue.put_nowait(callback)

    def loadAndUpdateGUI(self):
        self.statusRobot.loadFile(SAVE_PATH)
        for i in range(LOCATION_COUNT):
            self.appLocations[i] = self.getLocation(i+1)
            self.gui.updateLocationRows(self.appLocations)
            


    # Commands that return must be blocking, so the queue isn't used
    # and these are run in the main thread

    def recordLocation(self, idx):
        response = self.motionRobot.teachPlate(idx)
        if response.success:
            return self.getLocation(idx)
    
    def getLocation(self, idx):
        response = self.motionRobot.loc(idx)
        # force cartesian for now
        # TODO: add support for angles type locations
        if response.success:
            if response.message[0] == "1":
                self.motionRobot.locXYZ(idx, 0, 0, 0, 0, 0, 0)
            response = self.motionRobot.loc(idx)
            loc = AppLocation()
            loc.setInfo(response.message)
            return loc


class AppLocation:
    def __init__(self, name="undefined"):
        self.name = name
        self.angle = [0 for i in range(13)]
        self.config = 0x00
        self.type = 0
        self.x = 0
        self.y = 0
        self.z = 0
        self.yaw = 0
        self.pitch = 0
        self.roll = 0
        self.zClearance = 0
        self.zWorld = False

    def setInfo(self, coordString):
        # coordString is input from TCS "loc" command
        info = coordString.split(" ")
        info = [float(i) for i in info]
        self.x = info[2]
        self.y = info[3]
        self.z = info[4]
        self.yaw = info[5]
        self.pitch = info[6]
        self.roll = info[7]

    def setInfoFromWhereC(self, coordString):
        # coordString is input from TCS "wherec" command
        #TODO: merge wtih self.setInfo?
        info = coordString.split(" ")
        info = [float(i) for i in info]
        self.x = info[0]
        self.y = info[1]
        self.z = info[2]
        self.yaw = info[3]
        self.pitch = info[4]
        self.roll = info[5]


class AppPickPlaceAction:
    def __init__(self, sourceIdx=1, destinationIdx=1):
        self.sourceIdx = sourceIdx
        self.destinationIdx = destinationIdx


def main():

    print("starting app")
    app = ExampleApplication()
    print("exiting app")
    return


if __name__ == "__main__":
    main()

