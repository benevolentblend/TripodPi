import time
from Servo import Servo

servo_min = 150
servo_max = 585

pan = 0
tilt = 1

tilt_min = 10
tilt_max = 150

pan_min = 0
pan_max = 180

target = open('data.csv', 'w')
target.truncate()
target.write('time,position,velocity\n')

panServo = Servo(pan, pan_max, pan_min)
tiltServo = Servo(tilt, tilt_max, tilt_min)

panServo.setPosition(10)
tiltServo.setPosition(tilt_min)

# time.sleep(1)


panServo.maxABSVelocity = 1000.0
panServo.maxABSacceleration = 25.0

startTime = time.time()

panServo.updateTarget(pan_max)
tiltServo.updateTarget(10)
updated = False

while panServo.position != panServo.target:

    # if not updated and time.time() - startTime > 1:
    #     panServo.updateTarget(pan_min)
    #     updated = True
    #     print('Updated target =================================================')
    panServo.updatePosition(time.time())
    target.write('{0:.3f}, {1:.3f}, {2:.3f}\n'.format(time.time() - startTime, panServo.position, panServo.velocity))
    time.sleep(0.005)

print('Total Time: {0:.3f}'.format(time.time() - startTime))
print('RUD: {0:.3f}, RDD: {1:.3f}, CD{2:.3f}, DIS: {3:.3f}'.format(panServo.rampUpDistance, panServo.rampDownDistance, panServo.cruiseDistance, panServo.target - panServo.startPosition))
print('RUT: {0:.3f}, RDT: {1:.3f}, CT:{2:.3f}'.format(panServo.rampUpTime, panServo.rampDownTime, panServo.cruiseTime))
target.close()
