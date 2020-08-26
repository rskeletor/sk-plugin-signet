#!/usr/bin/python

import serial, time, threading, json, sys

# crack open the serial port for reading. 
#
ser = serial.Serial('/dev/serial/by-id/usb-FTDI_FT232R_USB_UART_AR0K4EHD-if00-port0',9600,serial.SEVENBITS,serial.PARITY_ODD,serial.STOPBITS_ONE,1)

#message types we are looking for from signet.
#
messageTypes = {
    'Cd': { 'key': 'environment.water.depth.belowSurface' , 'f2m' : 1 },
    'Hd': { 'key': 'environment.water.temperature', 'f2k': 1 },
    'Ad': { 'key': 'navigation.speedThroughWater', 'k2m': 1 },
    'Dd': { 'key': 'environment.wind.speedApparent', 'k2m': 1 },
    'Wd': { 'key': 'environment.wind.speedTrue', 'k2m': 1 },
    'Ed': { 'key': 'environment.wind.angleApparent', 'rad': 1 }
    }

data = {}		# blank dictionary for values

# send data out to signalk once per second.
#
def outputSk():
    global messageTypes, data
    updates = []
    
    for d in data:
    	# print(messageTypes[d]['key']+ ' - ' + data[d])
    	val = 0
    	try:
	    	if 'rad' in messageTypes[d]:
	    		val = float(data[d][2:5]) * 0.0174533		# convert to rad.
	    		if data[d][:1] == 'P':		# port values are negative
	    			val = val * -1

	    	if 'f2m' in messageTypes[d]:  	# convert feet to meters
			val = float(data[d]) * 0.3048
	 
     		if 'f2k' in messageTypes[d]:		# convert F to K for temp
			val = (float(data[d]) - 32) * 5/9 + 275.15
 
	     	if 'k2m' in messageTypes[d]:		# convert kts to m/s for speeds.
			val = float(data[d]) * 0.514444		# convert to rad.
			
	    	updates.append({"path": messageTypes[d]['key'], "value": val})			
	except:
		continue		# if any conversion errors just drop it.
   			
    delta = {"updates": [{"source": {"label": "Signet"},"values": updates}]}
    
    # print json.dumps(delta)
    # sys.stdout.flush()
    sys.stdout.write(json.dumps(delta))
    sys.stdout.write('\n')
    sys.stdout.flush()
    #
    threading.Timer(1.0, outputSk).start()		# fire it up in another second.

threading.Timer(1.0, outputSk).start()

# main loop
#
while True:
    try:
        response = ser.readline()
        rsp = str(response).split("$")
     
        for msg in rsp:
            mt = msg[:2]
        
            if not mt in messageTypes:    # skip anything not in the dictionary 
            	continue
        	
            info = messageTypes[mt]	# get data from the dict
            val =  msg[2:7]		# pull the value out

	    if not '?' in val:        
	        data[mt] = val		# save last values, unless there is a ? in the data
        
        #print(info['key'] + val)
    except KeyboardInterrupt:
        sys.stderr.write("exit")
        sys.stderr.write('\n')
        sys.stderr.flush()
        ser.close()
        sys.exit()

