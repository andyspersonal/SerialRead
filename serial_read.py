#!/usr/bin/env python
import time
import serial
import datetime
import sys
import urllib2
import Adafruit_CharLCD as LCD

#print "hello"
lastDataLogged = datetime.datetime(2010,1,1)
lastDataReceived = datetime.datetime(2010,1,1)
#lcd constants
# Raspberry Pi pin configuration:
lcd_rs        = 27  # Note this might need to be changed to 21 for older revisi$
lcd_en        = 22
lcd_d4        = 25
lcd_d5        = 24
lcd_d6        = 23
lcd_d7        = 18
lcd_backlight = 4

# Define LCD column and row size for 16x2 LCD.
lcd_columns = 16
lcd_rows    = 2



def SaveReading(reading):
	global lastDataLogged
	strDate = str(datetime.datetime.now())
	data = '{"Temperature": ' + reading + ', '
	data = data + '"TakenDateTime": "' + strDate + '",'
	data = data + '"SensorName": "Sensor1"}'
	print 'sending ' + data + 'to api'
	clen = len(data)
	url = "http://localhost:80/api/TemperatureReading"
	req = urllib2.Request(url,data, {'Content-Type': 'application/json','Content-Length': clen})

	f = urllib2.urlopen(req)
	response = f.read()
	f.close()
	lastDataLogged = datetime.datetime.now()
	#print response


def ProcessTemperature(reading):
	global lastDataReceived
	global lastDataLogged 
	try:
		#get the value of the reading
		reading = reading.replace('\n','')
		reading = reading.replace('\r','')
		reading = reading.replace('END','')
		reading = reading.replace('START','')

		#calculate and print date differences
		currentDate = datetime.datetime.now()
		dateDiffSinceLogged  = currentDate - lastDataLogged
		dateDiffSinceReceived = currentDate - lastDataReceived
		print ('Date Diff Since logged is ', dateDiffSinceLogged.total_seconds() / 60)
		print ('Date Diff since received is ',  dateDiffSinceReceived.total_seconds() / 60)

		#if we have a reading then 
		if reading != '':
			#set the date that we last received a reading
			lastDataReceived = datetime.datetime.now()
			#writ e to the lcd display
			msg = ''
			msg = reading
			msg = msg + 'C' + '\n'
			strCurDate = datetime.datetime.now().strftime("%d/%m %H:%M:%S")
			msg = msg + strCurDate
			#print msg
			lcd.clear()
			lcd.message(msg)
			#log the reafing to the database if it has been 15 mins since the last reading
			if (dateDiffSinceLogged.total_seconds() / 60) > 10:
				SaveReading(reading)
	except Exception, e:
		print ('Failed processing temperature ' , str(e))

ser = serial.Serial('/dev/ttyUSB0',9600,parity=serial.PARITY_NONE,stopbits=serial.STOPBITS_ONE,bytesize=serial.EIGHTBITS,timeout=10)
counter = 0
lcd = LCD.Adafruit_CharLCD(lcd_rs, lcd_en, lcd_d4, lcd_d5, lcd_d6, lcd_d7,
                           lcd_columns, lcd_rows, lcd_backlight)
while 1:
	try:
		x=ser.readline()
		print str(datetime.datetime.now()) + ' received data ' + x
		ProcessTemperature(x)
		sys.stdout.flush()
	except Exception, e:
		print('Failed reading from serial port',str(e))


