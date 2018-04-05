#!/usr/bin/python3

import socket
import json
# from Stepper import stepper

class Position(object):

    def __init__(self, pitch = 0, roll = 0):
        super(Position, self).__init__()
        self.stepsPitch = pitch
        self.stepsRoll = roll
        
class Device(object):

    def __init__(self, arg):

        super(Device, self).__init__()
        self.position = Position()
        self.rollStepper = Stepper([22, 17, 23]) # Step pin, direction pin, enable pin
        self.pitchStepper = Stepper([22, 17, 23]) # Step pin, direction pin, enable pin

    def isSafeMove(self, stepsRoll, stepsPitch):

        return True # TODO: Make this work correctly.

    def moveBySteps(self, stepsRoll, stepsPitch):

        if not isSafeMove(stepsRoll, stepsPitch):
            raise Exception("Movement is not safe to perform.")

        rollDirection = ""
        if stepsRoll > 0: # TODO: Figure out which direction is which.
            rollDirection = stepper.DIR_LEFT
        else:
            rollDirection = stepper.DIR_RIGHT

        pitchDirection = ""
        if stepsPitch > 0: # TODO: Figure out which direction is which.
            pitchDirection = stepper.DIR_LEFT
        else:
            pitchDirection = stepper.DIR_RIGHT

        self.rollStepper.step(abs(stepsRoll), rollDirection) #steps, dir, speed, stayOn
        self.pitchStepper.step(abs(stepsPitch), pitchDirection) #steps, dir, speed, stayOn

    def moveByDegrees(self, degreesRoll, degreesPitch):

        moveBySteps(degreesToSteps(degreesRoll), degreesToSteps(degreesPitch))

    def degreesToSteps(self, degrees):

        return degrees * 100 # TODO: Replace this with the correct multiplier.

    def getPosition(self):

        return self.position

def parseMessage(message):

    print("Parsing message ")
    print(message)
    print("end message")
    contents = json.loads(message)
    return (contents['x'], contents['y'], contents['type'])
    pass

def sendMessage(clientsocket, message):

    if message is Position:
        text = json.dumps({'x': (message.stepsPitch), 'y': (message.stepsRoll), 'type': ('absolute')})
        clientsocket.send(text)
    else:
        clientsocket.send(message)

def handleConnection(clientsocket, clientAddress, device):

    # {"x":15,"y":30,"type":"absolute"}
    message = bytes.decode(clientsocket.recv(2048))
    while not (message == ""):
        
        motionRoll, motionPitch, commandType = parseMessage(message)
        print("Got message ")
        print(motionRoll)
        message = bytes.decode(clientsocket.recv(2048))
        # if commandType == "steps":
        #     device.moveBySteps(motionRoll, motionPitch)
        # elif commandType == "degrees":
        #     device.moveByDegrees(motionRoll, motionPitch)
        # elif commandType == "getSteps":
        #     pos = device.getPosition()
        #     sendMessage(clientsocket, pos.stepsRoll + "," + pos.stepsPitch)
        # else:
        #     raise Exception("unknown commandType")    

def main():

    dev = "" #= Device()
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(("localhost", 1337)) # TODO: Decide on a port.
    sock.listen(1)
    while 1:
        (clientsocket, address) = sock.accept()
        handleConnection(clientsocket, address, dev)

if __name__ == '__main__':

    main()
