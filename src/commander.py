#!/usr/bin/env python

import crc
import platform
import rrdtool
import os
import serial
import serial.rs485
import sys
import time
from rrdtool import update as rrd_update

import mappings

PLATFORM = platform.platform()


def getRs485(port=None):
    """
    Return the opened serial port to be used for communication.

    ** Note that rs485 mode is not supported on OS X**
    It still may be possible to use this if it is used like it is on Linux.

    On Linux the driver hard-codes the port to rs485 instead of setting it here.
    """
    ser = None
    if PLATFORM.startswith("Linux"):
        if not port:
            port = '/dev/ttyXRUSB0'
        ser = serial.Serial(port=port,
                            baudrate=115200,
                            timeout=1, # set a timeout value, None for waiting forever
                            parity=serial.PARITY_NONE, # enable parity checking
                            stopbits=serial.STOPBITS_ONE, # number of stop bits
                            bytesize=serial.EIGHTBITS, # number of data bits
                            xonxoff=0, # enable software flow control
                            rtscts=0) # enable RTS/CTS flow control
        # On linux the rs485 settings are not used.  The driver has the port
        # hard coded to rs485
    else:
        if not port:
            port = "COM4"
        ser = serial.Serial(port=port,
                            baudrate=115200,
                            timeout=1, # set a timeout value, None for waiting forever
                            parity=serial.PARITY_NONE, # enable parity checking
                            stopbits=serial.STOPBITS_ONE, # number of stop bits
                            bytesize=serial.EIGHTBITS, # number of data bits
                            xonxoff=0, # enable software flow control
                            rtscts=1) # enable RTS/CTS flow control
        ser.rs485_mode = serial.rs485.RS485Settings()
    return ser


def addCRC(messageBytes):
    """
    Adds CRC to the byte buffer as the last two indices
    """
    crcv = crc.INITIAL_MODBUS
    for ch in messageBytes:
        crcv = crc.calcByte(ch, crcv)
    high = 0x00FF & crcv
    low = (0xFF00 & crcv) >> 8
    messageBytes.append(high)
    messageBytes.append(low)


def combineBytes(data):
    """
    Combine multiple bytes into a final value
    """
    combined = 0
    bits = 8
    for high, low in reversed(zip(data, data[1:])[::2]):
        # Use bit masking and shifting to make the two bytes one.
        combined = combined << bits
        combined = (combined | high)
        combined = combined << bits
        combined = (combined | low)
    return combined


def communicate(ser, deviceId, address, register, debug=False):
    """
    Used to send and receive from the MPPT controller

    @param: ser The serial connection used to communicate
    @param: address The address of the register that we will be querying
    @param: register The Register struct that we are passing

    """
    # Split the value into low and high bytes
    low = 0x00FF & address
    high = (0xFF00 & address) >> 8

    # Command changes based on register address.  This has to do with coils
    # vs input registers vs realtime status
    command = None
    if address >= 0x1000 and address < 0x3000:
        command = 0x04
    elif address >= 0x3000 and address < 0x9000:
        command = 0x04
    elif address >= 0x9000:
        command = 0x03
    elif address < 0x15:
        command = 0x01
    else:
        raise RuntimeError("Inapropriate register address")

    byteMessage = [deviceId, command, high, low, 0x0, v.numWords]

    addCRC(byteMessage)

    # If we have debug on, print out what we send and receive
    if debug:
        message = []
        for m in byteMessage:
            message.append(str(hex(m)))
        print "\tSending:", " ".join(message)

    ser.write(byteMessage)
    ser.flush()

    rec = bytearray()
    for i in xrange(100):
        r = ser.read(1)
        if r:
            rec.append(r)
        else:
            # Received Empty, call it done
            break

    # If we have debug on, print out what we send and receive
    if debug:
        print "\tReceive:",
        for m in rec:
            print '0x%01x' % m,
        print

    # Strip off the header and CRC then convert it using the unit function pointer
    data = rec[3:-2] 
    return v.unit(combineBytes(data), v.times)


if __name__ == "__main__":
    """
    Test getting data from the Commander and print it to the screen
    """
    rrdfile = os.path.expanduser("~/solarDb.rrd")
    print rrdfile
    if not os.path.exists(rrdfile):
        ret = rrdtool.create(rrdfile, "--step", "1", "--start", '0',
                             "DS:0x3000:GAUGE:2000:U:U",
                             "DS:0x3001:GAUGE:2000:U:U",
                             "DS:0x331A:GAUGE:2000:U:U",
                             "RRA:AVERAGE:0.5:1s:10d",
                             "RRA:AVERAGE:0.5:1m:90d",
                             "RRA:AVERAGE:0.5:1h:18M",
                             "RRA:AVERAGE:0.5:1d:10y",
                             "RRA:MAX:0.5:1s:10d",
                             "RRA:MAX:0.5:1m:90d",
                             "RRA:MAX:0.5:1h:18M",
                             "RRA:MAX:0.5:1d:10y")
        print "Created", os.path.exists(rrdfile)

    ser = getRs485()

    try:
        # The ID of the device we are going to communicate with.
        deviceId = 0x01
        for _ in xrange(1):
            toLog = {}
            for addr, v in sorted(mappings.RegistersA.iteritems()):
                value = communicate(ser, deviceId, addr, v, debug=False)
                print "%s \"%s\": %s" % (hex(addr), v.name, value)

            #ret = rrd_update(rrdfile, 'N:%s:%s:%s' %(items[0], items[1], items[2]))
            time.sleep(1)
    except:
        raise
    finally:
        # Close the port regardless of errors
        ser.close()


