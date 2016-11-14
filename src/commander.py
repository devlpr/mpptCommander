#!/usr/bin/env python
#
# Author: Darin Velarde
#
# Commander interface for Renogy 20A charge controller.
# 
# The first question you might ask is why I wrote this.  The answer is that I
# hadn't found the one here https://github.com/kasbert/epsolar-tracer yet. The
# other half of the answer is that I probably would have anyway since I had
# never used modbus before. There are some interesting similarities between this
# library and the epsolar-tracer, namely the Register data type and it's data
# fields. They are not 100% compatible but whoever wrote tracer and I obviously
# thought similarly about the problem space.
#
# One important distinction is that this library does not use pymodbus. So there
# is one less dependency to deal with.
#
# This library is also about twice as fast as tracer. Meaning that it gets the
# data about twice as fast. It takes quite a while to gather all the fields.
#
# This file is the entry point in order to use the controller over RS 485
import crc
import os
import platform
import rrdtool
import serial
import serial.rs485
import sys
import time

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
        # hard coded to rs485. That driver can be found here along with another
        # python implementation that does something similar to this one.
        # https://github.com/kasbert/epsolar-tracer
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

    Given an array of bytes, return the same array with two more bytes appended
    to the end.  These two new bytes are the CRC.

    Notice that there is no return value.  The bytes are added in situ.
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
    Combine multiple bytes into a final value.  The data argument is expected to
    be an iterable container that contains 'len % 2 == 0' elements.  It will
    iterate over each set of two elements and combine the low and high bytes
    shifting each time it encounters a new byte pair.  The resulting value is
    the integer value of the combined bytes.
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
    @param: deviceId The ID number of the device on the bus that we want to
                     communicate with
    @param: address The address of the register that we will be querying
    @param: register The Register struct that we are passing

    """
    # Split the value into low and high bytes
    low = 0x00FF & address
    high = (0xFF00 & address) >> 8

    # Command changes based on register address.  This has to do with coils
    # vs input registers vs realtime status etc.
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

    byteMessage = [deviceId, command, high, low, 0x0, register.numWords]

    addCRC(byteMessage) # This puts the CRC on the message in situ

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
            # Received empty, call it done
            break

    # If we have debug on, print out what we send and receive
    if debug:
        print "\tReceive:",
        for m in rec:
            print '0x%01x' % m,
        print

    # Strip off the header and CRC then convert it using the unit function 
    # pointer
    data = rec[3:-2] 
    return combineBytes(data)


if __name__ == "__main__":
    """
    Test getting data from the Commander and print it to the screen
    """
    ser = getRs485()

    try:
        # The ID of the device we are going to communicate with.
        deviceId = 0x01

        # Query the device 10 times and exit
        for _ in xrange(10):
            for addr, reg in sorted(mappings.REGISTERS.iteritems()):
                value = communicate(ser, deviceId, addr, reg, debug=False)

                # Convert to readable text
                readable = reg.unit(value, reg.times)

                print "%s \"%s\": %s" % (hex(addr), reg.name, readable)
            time.sleep(1)
    except:
        raise
    finally:
        # Close the port regardless of errors
        ser.close()


