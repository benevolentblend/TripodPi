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

panServo = Servo(pan, pan_max, pan_min)

panServo.position = pan_min
panServo.maxVelocity = 50
panServo.acceleration = 50

startTime = time.time()

panServo.updateTarget(pan_max)
updated = False

while panServo.position != panServo.target:

    if not updated and time.time() - startTime > 2:
        panServo.updateTarget(pan_min)
        updated = True
        print('Updated target =================================================')
    panServo.updatePosition(time.time())
    target.write('{0:.3f}, {1:.3f}, {2:.3f}\n'.format(time.time() - startTime, panServo.position, panServo.velocity))
    time.sleep(0.005)

print('Total Time: {0:.3f}'.format(time.time() - startTime))
print('RUD: {0:.3f}, RDD: {1:.3f}, CD{2:.3f}, DIS: {3:.3f}'.format(panServo.rampUpDistance, panServo.rampDownDistance, panServo.cruiseDistance, panServo.target - panServo.startPosition))

target.close()
