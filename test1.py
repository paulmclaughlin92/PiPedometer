#!/usr/bin/env python
import math
import time
from ctypes import *
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
import numpy as np
#cdll.LoadLibrary("./bcm2835.so")

sensor = CDLL("./sensor.so")

class MMA8491Q_DATA(Structure):
	_fields_  = [("Xout", c_int16),
	("Yout", c_int16),
	("Zout", c_int16)]

class mma8491q:
	def __init__(self):
		if (0 == sensor.bcm2835_init()):
			print "bcm3835 driver init failed."
			return	

	def init(self):
		sensor.MMA8491Q_Init()
		
	def enable(self):
		sensor.MMA8491Q_Enable()

	def disEnable(self):
		sensor.MMA8491Q_DisEnable()
		
	def writeRegister(self, register, value):
		sensor.MMA8491Q_WRITE_REGISTER()

	def readRegister(self, register):
		return sensor.MMA8491Q_READ_REGISTER()

	def read(self, data):
		sensor.MMA8491_Read(data)	

	def getAccelerometer(self):
		data = 	MMA8491Q_DATA()
		pdata = pointer(data)
		self.read(pdata)
		return (data.Xout, data.Yout, data.Zout);
		
	def __str__(self):
		ret_str = ""
		(x, y, z) = self.getAccelerometer()
		ret_str += "X: "+str(x) + "  "
		ret_str += "Y: "+str(y) + "  "
		ret_str += "Z: "+str(z)
		
		return ret_str
		
	def twosToInt(self, val, len):
		# Convert twos compliment to integer
		if(val & (1 << len - 1)):
			val = val - (1<<len)

		return val

		
mma = mma8491q()
mma.init()
mma.enable()
steps=0


win = pg.GraphicsWindow()
win.setWindowTitle('PiPedometer')
p1 = win.addPlot()
p2 = win.addPlot()
win.nextRow()
p3 = win.addPlot()
p4 = win.addPlot()
win.nextRow()
p5 = win.addPlot()
p1.setLabels(left=('X [mg]'))
p1.setLabels(bottom=('Samples'))
p2.setLabels(left=('Y [mg]','m'))
p2.setLabels(bottom=('Samples'))
p3.setLabels(left=('Y [mg]'))
p3.setLabels(bottom=('Samples'))
p4.setLabels(left=('Magnitude [mg]'))
p4.setLabels(bottom=('Samples'))
p5.setLabels(left=('Steps'))
p5.setLabels(bottom=('Samples'))

data1 = np.random.normal(size=20)*0
data2 = np.random.normal(size=20)*0
data3 = np.random.normal(size=20)*0
data4 = np.random.normal(size=20)*0
data5 = np.random.normal(size=20)*0
curve1 = p1.plot(data1)
curve2 = p2.plot(data2)
curve3 = p3.plot(data3)
curve4 = p4.plot(data4)
curve5 = p5.plot(data5)

ptr1 = 0
def update1():
    global data1, curve1, ptr1
    global data2, curve2
    global data3, curve3
    global data4, curve4
    global data5, curve5
    global mag, steps
    mma.enable()
    time.sleep(0.05)
    (x, y, z) = mma.getAccelerometer()
    mag= math.sqrt(x*x+y*y+z*z)
    if mag>1400:
        steps=steps+1
    data1[:-1] = data1[1:]  
    data1[-1] = x
    data2[:-1] = data2[1:]  
    data2[-1] = y
    data3[:-1] = data3[1:]  
    data3[-1] = z
    data4[:-1] = data4[1:]  
    data4[-1] = mag
    data5[:-1] = data5[1:]  
    data5[-1] = steps

    
    ptr1 += 1
    curve1.setData(data1)
    curve1.setPos(ptr1, 0)
    curve2.setData(data2)
    curve2.setPos(ptr1, 0)
    curve3.setData(data3)
    curve3.setPos(ptr1, 0)
    curve4.setData(data4)
    curve4.setPos(ptr1, 0)
    curve5.setData(data5)
    curve5.setPos(ptr1, 0)


# update all plots
def update():
    update1()

timer = pg.QtCore.QTimer()
timer.timeout.connect(update)
timer.start(10)



## Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()


