import argparse
import matplotlib.pyplot as plt
import numpy as np
from numpy import genfromtxt

# python graph.py [csv file] [image location] [title: optional]


parser = argparse.ArgumentParser(description='Generates images from csv files')
parser.add_argument('csv')
parser.add_argument('image')
parser.add_argument('--title')
args = parser.parse_args()

argDict = vars(args)

timeCol = 0
positionCol = 1
velocityCol = 2

data = genfromtxt(argDict['csv'], delimiter=',', skip_header=1)

plt.plot(data[:,timeCol], data[:,positionCol])
plt.plot(data[:,timeCol], data[:,velocityCol])
if argDict['title']:
    plt.title(argDict['title'])
plt.xlabel('Time(s)')
plt.margins(0.05)
plt.savefig(argDict['image'])
