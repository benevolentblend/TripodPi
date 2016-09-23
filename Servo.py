import time
import math

class Servo:
    """docstring for Servo."""

    global covD2S, covS2D, calculateDistance

    def covD2S(deg):
        sig = int((29 * deg) / 12 + 150)
        if(sig > 585):
            return 585
        elif(sig < 0):
            return 0
        else:
            return int(sig)

    def covS2D(sig):
        deg = int((12 * sig) / 29 - 62)
        if(deg > 180):
            return 180
        elif(deg < 0):
            return 0
        else:
            return deg

    def calculateDistance(iV, a, t):
        return (iV * t) + 0.5 * a * t ** 2

    def __init__(self, port, max, min):
        self.port = port
        self.max = max
        self.min = min

        self.target = min
        self.position = min
        self.velocity = 0

        self.maxVelocity = 200.0 # Must be a decimal and > 0
        self.acceleration = 500.0 # Must be a decimal and > 0

        self.startPosition = 0
        self.startTime = 0
        self.initialVelocity = 0
        self.direction = 1

        self.rampUpTime = 0
        self.cruiseTime = 0
        self.rampDownTime = 0

        self.rampUpDistance = 0
        self.cruiseDistance = 0
        self.rampDownDistance = 0

        self.startRampUp = 0
        self.startCruise = 0
        self.startRampDown = 0
        self.finished = 0


    def updateTarget(self, newTarget):
        if newTarget == self.position:
            return

        self.startPosition = self.position
        self.initialVelocity = self.velocity
        self.target = newTarget
        distance = self.target - self.startPosition

        if distance > 0:
            self.direction = 1
        else:
            self.direction = -1

        self.rampUpTime = (self.maxVelocity - self.initialVelocity) / self.acceleration
        self.rampUpDistance = calculateDistance(self.initialVelocity, self.acceleration, self.rampUpTime) * self.direction

        self.rampDownTime = self.maxVelocity / self.acceleration
        self.rampDownDistance = calculateDistance(self.maxVelocity, 0 - self.acceleration, self.rampDownTime) * self.direction



        if math.fabs(self.rampUpDistance + self.rampUpDistance) > math.fabs(distance):
            print('Ramp up and down bigger than distance!!!!')
            self.target = self.position
        else:
            self.cruiseDistance = distance - self.rampUpDistance - self.rampDownDistance
            self.cruiseTime = math.fabs(self.cruiseDistance / self.maxVelocity)

            self.startTime = time.time()

            self.startRampUp = 0
            self.startCruise = self.rampUpTime
            self.startRampDown = self.startCruise + self.cruiseTime
            self.finished = self.startRampDown + self.rampDownTime



    def updatePosition(self, ctime):
        if self.position == self.target:
            return self.position

        currentTime = time.time() - self.startTime

        if self.startRampUp <= currentTime and currentTime < self.startCruise:
            self.position = self.startPosition + calculateDistance(self.initialVelocity, self.acceleration, currentTime) * self.direction
            self.velocity = self.initialVelocity * self.direction + self.acceleration * currentTime * self.direction
            stage = 'RAMP UP'
        elif self.startCruise <= currentTime and currentTime < self.startRampDown:
            self.position = self.startPosition + self.rampUpDistance + self.maxVelocity * (currentTime - self.startCruise) * self.direction
            self.velocity = self.maxVelocity * self.direction
            stage = 'CRUISE'
        elif self.startRampDown <= currentTime and currentTime < self.finished:
            self.position = self.startPosition + self.rampUpDistance + self.cruiseDistance + calculateDistance(self.maxVelocity, 0 - self.acceleration, currentTime - self.startRampDown) * self.direction
            self.velocity = self.maxVelocity * self.direction + (0 - self.acceleration) * (currentTime - self.startRampDown) * self.direction
            stage = 'RAMP DOWN'
        else:
            self.position = self.target
            self.velocity = 0
            stage = 'DONE'

        print('{0:10} position: {1:7.3f}, velocity: {2:7.3f}'.format(stage, self.position, self.velocity))

        return self.position
