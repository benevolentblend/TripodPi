import time
import math
import Adafruit_PCA9685

pwm = Adafruit_PCA9685.PCA9685()
pwm.set_pwm_freq(60)

class Servo:
    """
    Controls the position of a Servo using velocity and acceleration to
    move the sevro to different target positions
    """

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

        self.maxABSVelocity = 200.0 # Must be a decimal and > 0
        self.maxABSacceleration = 500.0 # Must be a decimal and > 0

        self.startPosition = 0
        self.startTime = 0
        self.initialVelocity = 0
        self.direction = 1

        self.rampUpAcceleration = 0
        self.rampDownAcceleration = 0
        self.cruiseVelocity = 0

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

        if distance > 0: # positive direction
            self.rampUpAcceleration = self.maxABSacceleration
            self.rampDownAcceleration = -self.maxABSacceleration
            self.cruiseVelocity = self.maxABSVelocity
        else: # negative direction
            self.rampUpAcceleration = -self.maxABSacceleration
            self.rampDownAcceleration = self.maxABSacceleration
            self.cruiseVelocity = -self.maxABSVelocity

        self.rampUpTime = math.fabs((self.cruiseVelocity - self.initialVelocity) / self.rampUpAcceleration)
        self.rampUpDistance = calculateDistance(self.initialVelocity, self.rampUpAcceleration, self.rampUpTime)

        self.rampDownTime = math.fabs(self.cruiseVelocity / self.rampDownAcceleration)
        self.rampDownDistance = calculateDistance(self.cruiseVelocity, self.rampDownAcceleration, self.rampDownTime)

        # overshoot
        if math.fabs(self.rampUpDistance + self.rampUpDistance) > math.fabs(distance):

            self.rampUpDistance = distance / 2
            self.rampUpTime = math.sqrt(math.fabs(distance / self.maxABSacceleration))

            self.rampDownDistance = self.rampUpDistance
            self.rampDownTime = self.rampUpTime

            self.cruiseDistance = 0
            self.cruiseTime = 0
            self.cruiseVelocity = self.rampUpTime * self.rampUpAcceleration

            if math.fabs(self.initialVelocity + self.cruiseVelocity) > math.fabs(self.cruiseVelocity): # initial velocity approaching cruise velocity
                timeDiff = math.fabs(self.initialVelocity / self.rampUpAcceleration)
                distanceDiff = calculateDistance(0, self.rampUpAcceleration, timeDiff)

                self.rampUpTime -= timeDiff
                self.rampUpDistance -= distanceDiff
                self.cruiseTime = distanceDiff / self.cruiseVelocity
                self.cruiseDistance = distanceDiff


            if math.fabs(self.initialVelocity + self.cruiseVelocity) < math.fabs(self.cruiseVelocity): # initial velocity dissenting cruise velocity

                self.position = self.target
                return

        else:
            self.cruiseDistance = distance - self.rampUpDistance - self.rampDownDistance
            self.cruiseTime = math.fabs(self.cruiseDistance / self.cruiseVelocity)

        self.startRampUp = 0
        self.startCruise = self.rampUpTime
        self.startRampDown = self.startCruise + self.cruiseTime
        self.finished = self.startRampDown + self.rampDownTime
        self.startTime = time.time()

    def updatePosition(self, ctime):
        if self.position == self.target:
            return self.position

        currentTime = time.time() - self.startTime

        if self.startRampUp <= currentTime and currentTime < self.startCruise:
            self.position = self.startPosition + calculateDistance(self.initialVelocity, self.rampUpAcceleration, currentTime)
            self.velocity = self.initialVelocity + self.rampUpAcceleration * currentTime
            stage = 'RAMP UP'
        elif self.startCruise <= currentTime and currentTime < self.startRampDown:
            self.position = self.startPosition + self.rampUpDistance + self.cruiseVelocity * (currentTime - self.startCruise)
            self.velocity = self.cruiseVelocity
            stage = 'CRUISE'
        elif self.startRampDown <= currentTime and currentTime < self.finished:
            self.position = self.startPosition + self.rampUpDistance + self.cruiseDistance + calculateDistance(self.cruiseVelocity, self.rampDownAcceleration, currentTime - self.startRampDown)
            self.velocity = self.cruiseVelocity + self.rampDownAcceleration * (currentTime - self.startRampDown)
            stage = 'RAMP DOWN'
        else:
            self.position = self.target
            self.velocity = 0
            stage = 'DONE'

        print('{0:10} position: {1:8.3f}, velocity: {2:8.3f}, time:{3:8.3f}'.format(stage, self.position, self.velocity, currentTime))
        pwm.set_pwm(self.port, 0, covD2S(self.position))

        return self.position

    def setPosition(self, pos):
        self.position = pos
        pwm.set_pwm(self.port, 0, covD2S(pos))
