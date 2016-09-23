import time
import math
import Adafruit_PCA9685
from Servo import Servo

#pwm = Adafruit_PCA9685.PCA9685()
servo_min = 150
servo_max = 585
# pwm.set_pwm_freq(60)

pan = 0
tilt = 1

tilt_min = 10
tilt_max = 150

pan_min = 0
pan_max = 150

target = open('data.csv', 'w')
target.truncate()
target.write('time,position,velocity\n')

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

def goToSmooth(channel, start, end):
    print 'Smoothly moving from {} to {}'.format(start, end)
    distance = end - start
    initialVelocity = 0.0
    maxVelocity = 200.0 # Must be a decimal and > 0

    acceleration = 500.0 # Must be a decimal and > 0
    deceleration = 0 - acceleration
    if distance > 0:
        direction = 1
    else:
        direction = -1

    position = start

    rampUpTime = (maxVelocity - initialVelocity) / acceleration
    rampUpDistance = calculateDistance(initialVelocity, acceleration, rampUpTime) * direction

    rampDownTime = maxVelocity / acceleration

    rampDownDistance = calculateDistance(maxVelocity, deceleration, rampDownTime) * direction

    print('ramp up: {0:.3f}, ramp down: {1:.3f}, distance: {1:.3f}'.format(rampUpDistance, rampDownDistance, distance))
    if math.fabs(rampUpDistance + rampDownDistance) > math.fabs(distance):
        print('Ramp up and down bigger than distance!!!!')

    else:
        cruiseDistance = distance - rampUpDistance - rampDownDistance
        cruiseTime = math.fabs(cruiseDistance / maxVelocity)

        startRampUp = 0
        startCruise = rampUpTime
        startRampDown = rampUpTime + cruiseTime
        finished = startRampDown + rampDownTime

        startTime = time.time()

        currentTime = time.time() - startTime

        while currentTime < finished:
            if startRampUp <= currentTime and currentTime < startCruise:
                position = start + calculateDistance(initialVelocity, acceleration, currentTime) * direction
                velocity = initialVelocity * direction + acceleration * currentTime * direction
            elif startCruise <= currentTime and currentTime <= startRampDown:
                position = start + rampUpDistance + maxVelocity * (currentTime - startCruise) * direction
                velocity = maxVelocity * direction
            elif startRampDown < currentTime and currentTime < finished:
                position = start + rampUpDistance + cruiseDistance + calculateDistance(maxVelocity, deceleration, currentTime - startRampDown) * direction
                velocity = maxVelocity * direction + deceleration * (currentTime - startRampDown) * direction
            print('{0:.3f}, {1:.3f}, {2:.3f}\n'.format(currentTime, position, velocity))
            target.write('{0:.3f}, {1:.3f}, {2:.3f}\n'.format(currentTime, position, velocity))
            # pwm.set_pwm(channel, 0, covD2S(position))
            currentTime = time.time() - startTime
            time.sleep(0.005)

        print('RAMP UP   distance: {0:.3f}, time: {1:.3f}'.format(rampUpDistance, rampUpTime))
        print('MAXV      distance: {0:.3f}, time: {1:.3f}'.format(cruiseDistance, cruiseTime))
        print('RAMP DOWN distance: {0:.3f}, time: {1:.3f}'.format(rampDownDistance, rampDownTime))
        print('total     distance: {0:.3f}, time: {1:.3f}'.format(distance, time.time() - startTime))

        # pwm.set_pwm(channel, 0, covD2S(end))


def goToIn(channel, start, end, t):
    print 'Moving from {} to {} in {}s'.format(start, end, t)
    distance = end - start
    dTime = distance / t
    startTime = time.time()
    endTime = time.time() + t
    while time.time() < endTime:
        currentTime = time.time() - startTime
        location = start + dTime * currentTime
        # pwm.set_pwm(channel, 0, covD2S(location))
        time.sleep(0.005)

    # pwm.set_pwm(channel, 0, covD2S(end))

    # pwm.set_pwm(0, 0, covD2S(end))

panServo = Servo(0, pan_max, pan_min)

panServo.position = pan_min

startTime = time.time()

goToSmooth(pan, pan_min, pan_max)

panServo.updateTarget(pan_max)

while panServo.position != panServo.target:
    panServo.updatePosition(time.time())
    target.write('{0:.3f}, {1:.3f}, {2:.3f}\n'.format(time.time() - startTime, panServo.position, panServo.velocity))
    time.sleep(0.005)

print(panServo.position)
print(panServo.target)
print('RUD: {0:.3f}, RDD: {1:.3f}, CD{2:.3f}, DIS: {3:.3f}'.format(panServo.rampUpDistance, panServo.rampDownDistance, panServo.cruiseDistance, panServo.target - panServo.startPosition))


target.close()


print('Moving servo 0:')
