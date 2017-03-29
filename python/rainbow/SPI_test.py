#!/usr/bin/python

import spidev
import time

spi = spidev.SpiDev()
spi.open(0, 0)
spi.max_speed_hz = 10000

# Split an integer input into a two byte array to send via SPI
def write_pot(input):
	msb = input >> 8
	lsb = input & 0xFF
	resp = spi.xfer([msb,lsb])
	#print str([msb,lsb]) + ' - ' + str(resp)

# Repeatedly switch a MCP4151 digital pot off then on
while True:
	for i in range (0,255,10):
		write_pot(i)
		time.sleep(0.1)
	write_pot(255)
	time.sleep(1)
	for i in range (255,0,-10):
		write_pot(i)
		time.sleep(0.1)
	write_pot(0)
	time.sleep(1)
