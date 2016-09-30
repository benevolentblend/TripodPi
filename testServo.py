import os
import time
from Servo import Servo
from csvFile import csvFile

servo_max = 100
servo_min = -100

servo = Servo(0, servo_max, servo_min)

servo.maxABSVelocity = 20
servo.maxABSacceleration = 5

csvHeader = 'time,position,velocity'

def generateImage(csv, image, title):
    os.system('python graph.py {0} {1} --title="{2}"'.format(csv.filename, image, title))


""" ****************************************
                Standard Test
***************************************** """

standardPV = csvFile('data/standardPV.csv')

standardPV.open()
standardPV.write(csvHeader)

startTime = time.time()

servo.setPosition(-25)
servo.updateTarget(75)

while servo.position != servo.target:
    servo.updatePosition(time.time())
    currentTime = time.time() - startTime
    standardPV.write('{0:.3f}, {1:.3f}, {2:.3f}\n'.format(currentTime, servo.position, servo.velocity))
    time.sleep(0.005)

standardPV.close()
generateImage(standardPV, 'graphs/standardPV', 'Standard Positive Velocity')

standardNV = csvFile('data/standardPN.csv')

standardNV.open()
standardNV.write(csvHeader)

startTime = time.time()

servo.setPosition(75)
servo.updateTarget(-25)

while servo.position != servo.target:
    servo.updatePosition(time.time())
    currentTime = time.time() - startTime
    standardNV.write('{0:.3f}, {1:.3f}, {2:.3f}\n'.format(currentTime, servo.position, servo.velocity))
    time.sleep(0.005)

standardNV.close()
generateImage(standardNV, 'graphs/standardNV', 'Standard Negative Velocity')

""" ****************************************
              Update Target Test
***************************************** """

updateTargetPV = csvFile('data/updateTarget.csv')

updateTargetPV.open()
updateTargetPV.write(csvHeader)

startTime = time.time()

servo.setPosition(0)
servo.updateTarget(100)

updated = False

while servo.position != servo.target:
    currentTime = time.time() - startTime
    if not updated and currentTime > 2:
        servo.updateTarget(-100)
        updated = True

    servo.updatePosition(time.time())
    updateTargetPV.write('{0:.3f}, {1:.3f}, {2:.3f}\n'.format(currentTime, servo.position, servo.velocity))
    time.sleep(0.005)

updateTargetPV.close()
generateImage(updateTargetPV, 'graphs/updateTarget', 'Update Test')
