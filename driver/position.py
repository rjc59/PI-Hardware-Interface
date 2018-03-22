import socket
from Stepper import stepper

class Position(object):

    def __init__(self, tilt = 0, roll = 0):
        super(Position, self).__init__()
        self.stepsTilt = tilt
        self.stepsRoll = roll
        
class Device(object):

    def __init__(self, arg):

        super(Device, self).__init__()
        self.position = Position()
        self.rollStepper = Stepper([22, 17, 23]) # Step pin, direction pin, enable pin
        self.tiltStepper = Stepper([22, 17, 23]) # Step pin, direction pin, enable pin

    def isSafeMove(stepsRoll, stepsTilt):

        return True # TODO: Make this work correctly.

    def moveBySteps(stepsRoll, stepsTilt):

        if not isSafeMove(stepsRoll, stepsTilt):
            raise Exception("Movement is not safe to perform.")

        rollDirection = ""
        if stepsRoll > 0: # TODO: Figure out which direction is which.
            rollDirection = "left"
        else:
            rollDirection = "right"

        tiltDirection = ""
        if stepsTilt > 0: # TODO: Figure out which direction is which.
            tiltDirection = "left"
        else:
            tiltDirection = "right"

        self.rollStepper.step(abs(stepsRoll), rollDirection) #steps, dir, speed, stayOn
        self.tiltStepper.step(abs(stepsTilt), tiltDirection) #steps, dir, speed, stayOn

    def moveByDegrees(degreesRoll, degreesTilt):

        moveBySteps(degreesToSteps(degreesRoll), degreesToSteps(degreesTilt))

    def degreesToSteps(degrees):

        return degrees * 100 # TODO: Replace this with the correct multiplier.

    def getPosition():

        return self.position

def parseMessage():

    # TODO: Figure out a message format.
    pass

def sendMessage(clientsocket, message):

    clientsocket.send(message)

def handleConnection(clientsocket, clientAddress, device):

    message = clientsocket.recv(2048) # TODO: Figure out a better number of bytes to receive.
    while not (message == ""):
        
        message = clientsocket.recv(2048) # TODO: Figure out a better number of bytes to receive.
        commandType, motionRoll, motionTilt = parseMessage(message)
        if commandType == "steps":
            device.moveBySteps(motionRoll, motionTilt)
        elif commandType == "degrees":
            device.moveByDegrees(motionRoll, motionTilt)
        elif commandType == "getSteps":
            pos = device.getPosition()
            sendMessage(clientsocket, pos.stepsRoll + "," + pos.stepsTilt)
        else:
            raise Exception("unknown commandType")

def main():

    dev = Device()
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind("localhost", 1337) # TODO: Decide on a port.
    sock.listen(1)
    while 1:
        (clientsocket, address) = serversocket.accept()
        handleConnection(clientsocket, address, dev)

if __name__ == '__main__':

    main()