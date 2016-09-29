import matplotlib.pyplot as plt
import numpy as np
from numpy import genfromtxt

timeCol = 0
positionCol = 1
velocityCol = 2

data = genfromtxt('data.csv', delimiter=',', skip_header=1)

plt.plot(data[:,timeCol], data[:,positionCol])
plt.plot(data[:,timeCol], data[:,velocityCol])
plt.xlabel('Time(s)')
plt.savefig('graph.png')
