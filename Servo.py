import time
import math
from collections import deque
# import Adafruit_PCA9685
#
# pwm = Adafruit_PCA9685.PCA9685()
# pwm.set_pwm_freq(60)

class Servo:
    """
    Controls the position of a Servo using velocity and acceleration to
    move the sevro to different target positions
    """

    global covD2S, covS2D, calculateDistance

    class State:
        """
        Holds state information
        """
        def __init__(self, name):
            self.name = name
            self.time = 0
            self.distance = 0
            self.initialVelocity = 0
            self.acceleration = 0

        def __str__(self):
            return "State: {0:8} t: {1:8.3f} d: {2:8.3f} iv: {3:8.3f} a:{4:8.3f}".format(self.name, self.time, self.distance, self.initialVelocity, self.acceleration)


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
        self.cruiseVelocity = 0

        self.stateQueue = deque()
        self.distanceCovered = 0
        self.timePassed = 0

    def updateTarget(self, newTarget):
        self.stateQueue.clear()

        self.startTime = time.time()
        self.timePassed = 0
        self.target = newTarget
        self.startPosition = self.position
        self.distanceCovered = self.startPosition
        self.initialVelocity = self.velocity
        distance = self.target - self.startPosition

        rampUp = self.State('rampUp')
        cruise = self.State('cruise')
        rampDown = self.State('rampDown')

        if distance > 0: # positive direction
            rampUp.acceleration = self.maxABSacceleration
            rampDown.acceleration = -self.maxABSacceleration
            self.cruiseVelocity = self.maxABSVelocity
        else: # negative direction
            rampUp.acceleration = -self.maxABSacceleration
            rampDown.acceleration = self.maxABSacceleration
            self.cruiseVelocity = -self.maxABSVelocity

        cruise.acceleration = 0

        rampUp.initialVelocity = self.initialVelocity
        cruise.initialVelocity = self.cruiseVelocity
        rampDown.initialVelocity = cruise.initialVelocity

        rampUp.time = math.fabs((self.cruiseVelocity - self.initialVelocity) / rampUp.acceleration)
        rampUp.distance = calculateDistance(self.initialVelocity, rampUp.acceleration, rampUp.time)

        rampDown.time = math.fabs(self.cruiseVelocity / rampDown.acceleration)
        rampDown.distance = calculateDistance(self.cruiseVelocity, rampDown.acceleration, rampDown.time)


        if math.fabs(rampUp.distance + rampDown.distance) > math.fabs(distance): # overshoot
            rampUp.distance = distance / 2
            rampUp.time = math.sqrt(math.fabs(distance / self.maxABSacceleration))

            rampDown.distance = rampUp.distance
            rampDown.time = rampUp.time
            rampDown.initialVelocity = rampUp.time * rampUp.acceleration

            cruise.distance = 0
            cruise.time = 0
            cruise.initialVelocity = rampUp.time * rampUp.acceleration

            if((rampUp.initialVelocity < 0 and cruise.initialVelocity > 0) or (rampUp.initialVelocity > 0 and cruise.initialVelocity < 0)):
                slowDown = self.State('slowDown')
                slowDown.initialVelocity = rampUp.initialVelocity
                slowDown.acceleration = rampUp.acceleration
                slowDown.time = math.fabs(self.initialVelocity / rampUp.acceleration)
                slowDown.distance = calculateDistance(self.initialVelocity, slowDown.acceleration, slowDown.time)
                rampUp.initialVelocity = 0
                self.stateQueue.append(slowDown)

                cruise.distance = -slowDown.distance
                cruise.time = cruise.distance / cruise.initialVelocity

            if((rampUp.initialVelocity < 0 and cruise.initialVelocity < 0) or (rampUp.initialVelocity > 0 and cruise.initialVelocity > 0)):
                slowDown = self.State('slowDown')
                slowDown.initialVelocity = rampUp.initialVelocity
                slowDown.acceleration = -rampUp.acceleration
                slowDown.time = math.fabs(self.initialVelocity / rampUp.acceleration)
                slowDown.distance = calculateDistance(self.initialVelocity, slowDown.acceleration, slowDown.time)
                rampUp.initialVelocity = 0
                self.stateQueue.append(slowDown)

                distance -= slowDown.distance

                rampUp.distance = distance / 2
                rampUp.time = math.sqrt(math.fabs(distance / self.maxABSacceleration))

                rampDown.distance = rampUp.distance
                rampDown.time = rampUp.time
                rampDown.initialVelocity = rampUp.time * rampUp.acceleration
                cruise.initialVelocity = rampUp.time * rampUp.acceleration
        else:
            cruise.distance = distance - rampUp.distance - rampDown.distance
            cruise.time = math.fabs(cruise.distance / self.cruiseVelocity)

        self.stateQueue.append(rampUp)
        self.stateQueue.append(cruise)
        self.stateQueue.append(rampDown)

        print(rampUp)
        print(cruise)
        print(rampDown)
    def getCurrentState(self, ctime):
        if (len(self.stateQueue) == 0):
            return None
        cstate = self.stateQueue[0]

        if (cstate.time < ctime - self.timePassed):
            self.distanceCovered += cstate.distance
            self.timePassed += cstate.time
            self.stateQueue.popleft();
        if (len(self.stateQueue) == 0):
            self.velocity = 0
            self.position = self.target
            return None
        else:
            return self.stateQueue[0]

    def updatePosition(self, time):
        ctime = time - self.startTime
        cState = self.getCurrentState(ctime)
        if(not cState):
            return self.position

        stateTime = ctime - self.timePassed
        self.position = self.distanceCovered
        self.position += calculateDistance(cState.initialVelocity, cState.acceleration, stateTime)
        self.velocity = cState.initialVelocity + cState.acceleration * stateTime

        print('{0:10} position: {1:8.3f}, velocity: {2:8.3f}, time:{3:8.3f}'.format(cState.name, self.position, self.velocity, ctime))
        # pwm.set_pwm(self.port, 0, covD2S(self.position))

        return self.position

    def setPosition(self, pos):
        self.position = pos
        # pwm.set_pwm(self.port, 0, covD2S(pos))
