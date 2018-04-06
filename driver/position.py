#!/usr/bin/python3

import socket
import json
import _thread as thread # The module is officially named '_thread' in python3 for backwards compatibility reasons.
from queue import Queue # Thread safe, blocking queue

from time import sleep
haveRPi = False
try:
    import RPi.GPIO as gpio
    haveRPi = True
except Exception as e:
    pass
sleepTime = 0.000001

qRecieve = Queue()
qSend = Queue()

class Stepper:

    DIR_LEFT = "left"
    DIR_RIGHT = "right"
    DIR_NONE = "none"
    # instantiate stepper 
    # pins = [stepPin, directionPin, enablePin]
    def __init__(self, pins):
        #setup pins
        self.pins = pins
        self.stepPin = self.pins[0]
        self.directionPin = self.pins[1]
        self.enablePin = self.pins[2]
        self.stepTime = 0.000001
        self.position = 0
        
        if haveRPi:
            print("haveRPi init")
            #use the broadcom layout for the gpio
            gpio.setmode(gpio.BCM)
            
            #set gpio pins
            gpio.setup(self.stepPin, gpio.OUT)
            gpio.setup(self.directionPin, gpio.OUT)
            gpio.setup(self.enablePin, gpio.OUT)
            
            #set enable to high (i.e. power is NOT going to the motor)
            gpio.output(self.enablePin, True)
        
        print("Stepper initialized (step=" + str(self.stepPin) + ", direction=" + str(self.directionPin) + ", enable=" + str(self.enablePin) + ")")
    
    # clears GPIO settings
    def cleanGPIO(self):

        if haveRPi:
            print("haveRPi cleanup")
            gpio.cleanup()
    
    # step the motor
    # dir = direction stepper will move
    # stayOn = defines whether or not stepper should stay "on" or not. If stepper will need to receive a new step command immediately, this should be set to "True." Otherwise, it should remain at "False."
    def step(self, dir, stayOn=False):

        #set the output to true for left and false for right
        turnLeft = True
        if dir == self.DIR_RIGHT:
            turnLeft = False;
            self.position += 1
        elif dir == self.DIR_LEFT:
            turnLeft = True
            self.position -= 1
        else:
            print("STEPPER ERROR: invalid direction supplied")
            return False

        if haveRPi:
            print("haveRPi step")
            #set enable to low (i.e. power IS going to the motor)
            gpio.output(self.enablePin, False)
            gpio.output(self.directionPin, turnLeft)

            #turning the gpio on and off tells the easy driver to take one step
            gpio.output(self.stepPin, True)
            gpio.output(self.stepPin, False)

            if stayOn == False:
                #set enable to high (i.e. power is NOT going to the motor)
                gpio.output(self.enablePin, True)

class Device(object):

    def __init__(self):

        super(Device, self).__init__()
        self.destination = (0, 0)
        self.rollStepper = Stepper([22, 17, 23]) # Step pin, direction pin, enable pin
        self.pitchStepper = Stepper([24, 18, 25]) # Step pin, direction pin, enable pin

    def isSafeMove(self, stepsRoll, stepsPitch):

        return True # TODO: Make this work correctly.

    def step(self):

        stepsRoll = self.getPosition()[0] - self.destination[0]
        stepsPitch = self.getPosition()[1] - self.destination[1]

        if not self.isSafeMove(stepsRoll, stepsPitch):
            raise Exception("Movement is not safe to perform.")

        rollDirection = ""
        if stepsRoll > 0:
            self.rollStepper.step(Stepper.DIR_LEFT)
        elif stepsRoll < 0:
            self.rollStepper.step(Stepper.DIR_RIGHT)
        else:
            pass

        pitchDirection = ""
        if stepsPitch > 0:
            self.pitchStepper.step(Stepper.DIR_LEFT)
        elif stepsPitch < 0:
            self.pitchStepper.step(Stepper.DIR_RIGHT)
        else: 
            pass

    def startMove(self, position):

        self.destination = position

    def getPosition(self):

        return (self.rollStepper.position, self.pitchStepper.position)

    def isMoveFinished(self):

        return self.getPosition()[0] == self.destination[0] and self.getPosition()[1] == self.destination[1]

def parseMessage(message):

    print("Parsing message ")
    print(message)
    print("end message")
    contents = json.loads(message)
    return (contents['x'], contents['y'], contents['type'])

def sendMessage(clientsocket, message):

    if isinstance(message, Position):
        text = json.dumps({'x': message.stepsPitch, 'y': message.stepsRoll, 'type': 'absolute'})
        clientsocket.send(text)
    else:
        clientsocket.send(message)

def threadRecieveCommand():

    # Set up the socket to listen for connections.
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(("localhost", 1337)) # TODO: Decide on a port.
    sock.listen(1)
    while 1:
        # Receive a connection
        (recieveSocket, address) = sock.accept()

        # Do everything related to that connection for as long as it's open.
        message = "not empty"
        while not (message == ""):
            # Get the message as a string.
            message = bytes.decode(recieveSocket.recv(2048)).strip()
            print("got message " + message)
            position = parseMessage(message)

            # Put the parsed message into a queue to be consumed by another thread.
            qRecieve.put(position)

def threadConsumeCommand():

    device = Device()
    while 1:
        # Get a command from the queue, the optional True means this call will block until there is something ready to get.
        message = qRecieve.get(True)
        device.startMove(message)
        while not device.isMoveFinished():
            device.step()
            # After every step we send an updated position back to the server.
            qSend.put(device.getPosition())
            # Sleep until the motor is ready for another step.
            sleep(sleepTime)

def threadSendPosition():

    # TODO: Open a connection back to the logic engine and send the message
    while 1:
        message = qSend.get(True)
        print("sending message " + str(message))
        # sendMessage(sendSocket, message)

def main():

    thread.start_new_thread(threadRecieveCommand, ()) # Start new thread requires a function and a tuple as arguments.
    thread.start_new_thread(threadConsumeCommand, ())
    thread.start_new_thread(threadSendPosition, ())

    # Spin loop so that the threads can keep running.
    while 1:
        pass



if __name__ == '__main__':

    main()

""" Test commands
{"x":15,"y":30,"type":"absolute"}
{"x":10,"y":30,"type":"absolute"}
{"x":10,"y":35,"type":"absolute"}
{"x":15,"y":25,"type":"absolute"}
{"x":0,"y":0,"type":"absolute"}
"""