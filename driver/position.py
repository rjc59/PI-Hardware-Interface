#!/usr/bin/python3

from websocket import create_connection
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
sleepTimeMotors = 0.000001
sleepTimeSensors = 1

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
            print("haveRPi init", flush=True)
            #use the broadcom layout for the gpio
            gpio.setmode(gpio.BCM)

            #set gpio pins
            gpio.setup(self.stepPin, gpio.OUT)
            gpio.setup(self.directionPin, gpio.OUT)
            gpio.setup(self.enablePin, gpio.OUT)

            #set enable to high (i.e. power is NOT going to the motor)
            gpio.output(self.enablePin, True)

        print("Stepper initialized (step=" + str(self.stepPin) + ", direction=" + str(self.directionPin) + ", enable=" + str(self.enablePin) + ")", flush=True)

    # clears GPIO settings
    def cleanGPIO(self):

        if haveRPi:
            print("haveRPi cleanup", flush=True)
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
            print("STEPPER ERROR: invalid direction supplied", flush=True)
            return False

        if haveRPi:
            print("haveRPi step", flush=True)
            #set enable to low (i.e. power IS going to the motor)
            gpio.output(self.enablePin, False)
            gpio.output(self.directionPin, turnLeft)

            #turning the gpio on and off tells the easy driver to take one step
            gpio.output(self.stepPin, True)
            gpio.output(self.stepPin, False)

            if stayOn == False:
                #set enable to high (i.e. power is NOT going to the motor)
                gpio.output(self.enablePin, True)

class Motors(object):

    def __init__(self):

        super(Motors, self).__init__()
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

class Sensors(object):
    """docstring for Sensors"""
    def __init__(self):
        super(Sensors, self).__init__()

def parseMessage(message):

    print("Parsing message ", flush=True)
    print(message)
    print("end message", flush=True)
    contents = json.loads(message)
    if 'type' in contents:
        return (contents['x'], contents['y'], contents['type'])
    else:
        return (contents['x'], contents['y'])

def sendMessage(clientsocket, message):

    if isinstance(message, Position):
        clientsocket.send(text)
    else:
        clientsocket.send(message)

def threadMonitorSensors():

    sensor = Sensors()
    while 1:
        # Check sensor readings.
        # Determine if we should send an update.
        # Send that update.
        sleep(sleepTimeSensors)
        pass

def threadRecieveCommand(ws):

    # Set up the socket to listen for connections.
    while 1:

        # Do everything related to that connection for as long as it's open.
        message = "not empty"
        while not (message == ""):
            # Get the message as a string.
            message = ws.recv()
            print("got message " + message, flush=True)
            position = parseMessage(message)

            # Put the parsed message into a queue to be consumed by another thread.
            qRecieve.put(position)

def threadConsumeCommand():

    device = Motors()
    while 1:
        # Get a command from the queue, the optional True means this call will block until there is something ready to get.
        message = qRecieve.get(True)
        device.startMove(message)
        while not device.isMoveFinished():
            device.step()
            # After every step we send an updated position back to the server.
            qSend.put(device.getPosition())
            # Sleep until the motor is ready for another step
            sleep(sleepTimeMotors)

def threadSendPosition(ws):

    # TODO: Open a connection back to the logic engine and send the message
    while 1:
        message = qSend.get(True)
        print("sending message " + str(message), flush=True)
        ws.send(json.dumps({"x": message[0], "y": message[1]}))

def main():

    ws = create_connection("ws://localhost:9001/")

    thread.start_new_thread(threadMonitorSensors, ()) # Start new thread requires a function and a tuple as arguments.
    thread.start_new_thread(threadRecieveCommand, (ws,)) # The tuple contains any necessary arguments for the function.
    thread.start_new_thread(threadConsumeCommand, ()) # I don't need to pass any arguments, so I just pass and empty tuple.
    thread.start_new_thread(threadSendPosition,   (ws,))

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
