from collections import namedtuple


class Register(namedtuple("Register", ["name",
                                       "desc",
                                       "unit",
                                       "times",
                                       "numWords"])):
   __slots__ = () 


def V(value, times):
    return "%s volts" % (value / float(times))

def A(value, times):
    return "%s amps" % (value / float(times))

def W(value, times):
    return "%s watts" % (value / float(times))

def D(value, times):
    return "%s degrees C" % (value / float(times))

def P(value, times):
    return "%s percent" % value

def KWH(value, times):
    return "%s kwh" % (value / float(100))

def KWH(value, times):
    return "%s kwh" % (value / float(100))

def AH(value, times):
    return "%s ah" % (value / float(100))

def STR(value, times):
    return " :: %s" % value

def SEC(value, times):
    return "%s seconds" % (value / float(times))

def MIN(value, times):
    return "%s minute" % (value / float(times))

def HOUR(value, times):
    return "%s hour" % (value / float(times))

def MONTH(value, times):
    return "%s month" % (value / float(times))

def ChargingMode(value, times):
    if value == 0x00:
        return "Connect/Disconnect"
    elif value == 0x01:
        return "PWM"
    elif value == 0x02:
        return "MPPT"
    else:
        raise RuntimeError("No Such Charging Mode: %s" % value)

def BatteryType(value, times):
    if value == 0x01:
        return "Sealed"
    elif value == 0x02:
        return "Gel"
    elif value == 0x03:
        return "Flooded"
    elif value == 0x0:
        return "User defined"
    else:
        raise RuntimeError("No Such Battery Type: %s" % value)

def LoadControlModes(value, times):
    if value == 0x0:
        return "User defined"
    elif value == 0x01:
        return "Light ON/OFF"
    elif value == 0x02:
        return "Light ON+ Timer"
    elif value == 0x03:
        return "Time Control"
    else:
        raise RuntimeError("No Such Battery Type: %s" % value)

def COEF(value, times):
    return "%s mV/C/2" % (value / times)


def MANUALMODE(value, times):
    if value == 0x0:
        return "AUTO"
    elif value == 0x01:
        return "Manual"
    else:
        raise RuntimeError("No Such Mode: %s" % value)


def ENABLETEST(value, times):
    if value == 0x0:
        return "Enabled"
    elif value == 0x01:
        return "Disabled"
    else:
        raise RuntimeError("No Such Test Mode: %s" % value)


def BatteryStatus(value, times):
    """
    D3-D0:
        00H Normal,
        01H Overvolt,
        02H Under Volt,
        03H Low Volt Disconnect,
        04H Fault

    D7-D4:
        00H Normal,
        01H Over Temp.(Higher than the warning settings),
        02H Low Temp.(Lower than the warning settings),

    D8:
        Battery inner resistance abnormal 1, normal 0

    D15:
        1-Wrong identification for rated voltage
    """
    stat = ["Battery Voltage:", ]
    one = value & 0b0000000000001111
    if one == 0x0:
        stat.append("normal")
    elif one == 0x01:
        stat.append("over volt")
    elif one == 0x02:
        stat.append("under volt")
    elif one == 0x03:
        stat.append("low volt disconnect")
    elif one == 0x04:
        stat.append("fault")
    else:
        raise RuntimeError("No such battery voltage status: %s" % value)

    stat.append(", Battery Temperature:")
    two = value & 0b0000000011110000
    if two == 0x0:
        stat.append("normal")
    elif two == 0x01:
        stat.append("higher than settings)")
    elif two == 0x02:
        stat.append("lower than settings")
    else:
        raise RuntimeError("No such battery temperature status: %s" % value)

    stat.append(", Battery internal resistance:") # D8
    three = value & 0b0000000100000000
    if three == 0x0:
        stat.append("normal")
    elif three == 0x01:
        stat.append("abnormal")
    else:
        raise RuntimeError("No such battery resistance status: %s" % value)

    stat.append(", Rated voltage ID:") # D15
    four = value & 0b1000000000000000
    if four == 0x0:
        stat.append("normal")
    elif four == 0x01:
        stat.append("wrong")
    else:
        raise RuntimeError("No such battery id value: %s" % value)
    return " ".join(stat)


def ChargingEquipmentStatus(value, times):
    """
    D15-D14:
        00H normal
        01H low
        02H High
        03H no access Input volt error
    D13-D12: output power:
        00-light load,
        01-moderate,
        02-rated,
        03-overload
    D11: short circuit
    D10: unable to discharge
    D9: unable to stop discharging
    D8: output voltage abnormal
    D7: input overpressure
    D6: high voltage side short circuit
    D5: boost overpressure
    D4: output overpressure
    D1: 0 Normal, 1 Fault.
    D0: 1 Running, 0 Standby.
    """
    return "TODO: %s" % value
    if value == 0x0:
        return "Enabled"
    elif value == 0x01:
        return "Disabled"
    else:
        raise RuntimeError("No Such Test Mode: %s" % value)


def DischargingEquipmentStatus(value, times):
    """
    D15-D14: Input volt status.
        00 normal
        01 no power connected
        02H Higher volt input
        03H Input volt error
    D13: Charging MOSFET is short.
    D12: Charging or Anti-reverse MOSFET is short.
    D11: Anti-reverse MOSFET is short.
    D10: Input is over current.
    D9: The load is Over current.
    D8: The load is short.
    D7: Load MOSFET is short.
    D4: PV Input is short.
    D3-2: Charging status.
        00 No charging
        01 Float
        02 Boost
        03 Equalization
    D1: 0 Normal, 1 Fault.
    D0: 1 Running, 0 Standby.
    """
    return "TODO: %s" % value
    if value == 0x0:
        return "Enabled"
    elif value == 0x01:
        return "Disabled"
    else:
        raise RuntimeError("No Such Test Mode: %s" % value)


def LENNIGHT(value, times):
    hour = (value & 0b1111111100000000) >> 8
    minute = value & 0b0000000011111111
    return "hour:sec %s:%s" % (hour, minute)

def RTCSECMIN(value, times):
    minute = (value & 0b1111111100000000) >> 8
    sec = value & 0b0000000011111111
    return "%s:%s" % (minute, sec)

def RTCHOURDAY(value, times):
    day = (value & 0b1111111100000000) >> 8
    hour = value & 0b0000000011111111
    return "%s:%s" % (day, hour)

def RTCYEARMONTH(value, times):
    year = (value & 0b1111111100000000) >> 8
    month = value & 0b0000000011111111
    return "%s:%s" % (year, month)


# The last argument to Register is the number of 16 bit words in the data
# returned for that item
RegistersA = {
    0x3000: Register("Charging equipment rated input voltage", "PV array rated voltage", V, 100, 1),
    0x3001: Register("Charging equipment rated input current", "PV array rated current", A, 100, 1),
    0x3002: Register("Charging equipment rated input power", "PV array rated power (low 16 bits)", W, 100, 2),
    0x3004: Register("Charging equipment rated output voltage", None, V, 100, 1),
    0x3005: Register("Charging equipment rated output current", "Rated charging current to battery", A, 100, 1),
    0x3006: Register("Charging equipment rated output power", "Rated charging power to battery", W, 100, 2),
    0x3008: Register("Charging mode", "0001H-PWM", ChargingMode, None, 1),
    0x300E: Register("Rated output current of load", None, A, 100, 1),
    0x3100: Register("Charging equipment input voltage", "Solar charge controller--PV array voltage", V, 100, 1),
    0x3101: Register("Charging equipment input current", "Solar charge controller--PV array current", A, 100, 1),
    0x3102: Register("Charging equipment input power", "Solar charge controller--PV array power", W, 100, 2),
    0x3104: Register("Charging equipment output voltage", "Battery voltage", V, 100, 1),
    0x3105: Register("Charging equipment output current", "Battery charging current", A, 100, 1),
    0x3106: Register("Charging equipment output power", "Battery charging power", W, 100, 2),
    0x310C: Register("Disharging equipment output voltage", "Load voltage voltage", V, 100, 1),
    0x310D: Register("Disharging equipment output current", "Load current current", A, 100, 1),
    0x310E: Register("Disharging equipment output power", "Load power", W, 100, 2),
    0x3110: Register("Battery Temperature", "Battery Temperature", D, 100, 1),
    0x3111: Register("Temperature inside equipment", "Temperature inside case", D, 100, 1),
    0x3112: Register("Power components temperature", "Heat sink temperature of power components", D, 100, 1),
    0x311A: Register("Battery SOC", "Percentage of battery's remaining capacity", P, 100, 1),
    0x311B: Register("Remote battery temperature", "Battery temperature measured by remote sensor", D, 100, 1),
    0x311D: Register("Battery real rated power", "Current system rated voltage (1200, 2400 represents 12v, 24v", V, 100, 1),
    0x3300: Register("Maximum input (PV) today", "00: 00 Refresh every day", V, 100, 1),
    0x3301: Register("Minimum input (PV) today", "00: 00 Refresh every day", V, 100, 1),
    0x3302: Register("Maximum battery volt today", "00: 00 Refresh every day", V, 100, 1),
    0x3303: Register("Minimum battery volt today", "00: 00 Refresh every day", V, 100, 1),
    0x3304: Register("Consumed energy today", "00: 00 Clear every day", KWH, 100, 2),
    0x3306: Register("Consumed energy this month", "00: 00 Clear on the first day of the month", KWH, 100, 2),
    0x3308: Register("Consumed energy this year", "00: 00 Clear on 1, Jan.", KWH, 100, 2),
    #0x3309: Register("Consumed energy this year H", "00: 00 Clear on 1, Jan.", KWH, 100, 1),
    0x330A: Register("Total consumed energy", "Total consumed energy", KWH, 100, 2),
    0x330C: Register("Generated energy today", "00: 00 Clear every day", KWH, 100, 2),
    0x330E: Register("Generated energy this month", "00: 00 Clear on the first day of the month", KWH, 100, 2),
    0x3310: Register("Generated energy this year", "00: 00 Clear on Jan 1", KWH, 100, 2),
    0x3312: Register("Total generated energy", "Total generated energy", KWH, 100, 2),
    0x331A: Register("Battery voltage", "Battery voltage", V, 100, 1),
    0x331B: Register("Battery current", "Battery current", AH, 100, 2),

    0x9000: Register("Battery type", "Battery make-up (Sealed, Gel, Flooded, User)", BatteryType, None, 1),
    0x9001: Register("Battery capacity", "Rated capacity of battery", AH, None, 1),
    0x9002: Register("Temperature compensation coefficient", "Range 0-9", COEF, 1, 1),
    0x9003: Register("High volt disconnect", "High volt disconnect", V, 100, 1),
    0x9004: Register("Charging limit voltage", "Charging limit voltage", V, 100, 1),
    0x9005: Register("Over voltage reconnect", "Over voltage reconnect", V, 100, 1),
    0x9006: Register("Equalization voltage", "Equalization voltage", V, 100, 1),
    0x9007: Register("Boost voltage", "Boost Voltage", V, 100, 1),
    0x9008: Register("Float voltage", "Float voltage", V, 100, 1),
    0x9009: Register("Boost reconnect voltage", "Boost reconnect voltage", V, 100, 1),
    0x900a: Register("Low voltage reconnect", "Low voltage reconnect", V, 100, 1),
    0x900b: Register("Under voltage recover", "Under voltage recover", V, 100, 1),
    0x900c: Register("Under voltage warning", "Under voltage warning", V, 100, 1),
    0x900d: Register("Low voltage disconnect", "Low voltage disconnect", V, 100, 1),
    0x900e: Register("Discharging limit voltage", "Discharging limit voltage", V, 100, 1),
    0x9013: Register("Real time clock D7-0 Sec, D15-8 Min", "Year, Month, Day, Min, Sec should be written simultaneously", RTCSECMIN, 1, 1),
    0x9014: Register("Real time clock D7-0 Hour, D15-8 Day", "D7-0 Hour, D15-8 Day", RTCHOURDAY, 1, 1),
    0x9015: Register("Real time clock D7-0 Month, D15-8 Year", "D7-0 Month, D15-8 Year", RTCYEARMONTH, 1, 1),
    0x9017: Register("Battery temperature warning upper limit", "Battery temp warning upper limit", D, 100, 1),
    0x9018: Register("Battery temperature warning lower limit", "Battery temp warning lower limit", D, 100, 1),
    0x9019: Register("Controller inner temperature upper limit", "Controller inner temperature upper limit", D, 100, 1),
    0x901a: Register("Controller inner temperature upper limit recover", "Controller inner temperature upper limit recover", D, 100, 1),
    0x901e: Register("Day time threshold volt", "Day time threshold volt", V, 100, 1),

    # New ones
    0x901E: Register("Night TimeThreshold Volt.(NTTV)", " PV lower lower than this value, controller would detect it as sundown", V, 100, 1),
    0x901F: Register("Light signal startup (night) delay time", "PV voltage lower than NTTV, and duration exceeds the Light signal startup (night) delay time, controller would detect it as night time.", MIN, 1, 1),
    0x9020: Register("Day Time Threshold Volt.(DTTV)", "PV voltage higher than this value, controller would detect it as sunrise", V, 100, 1),
    0x9021: Register("Light signal turn off(day) delay time", "PV voltage higher than DTTV, and duration exceeds Light signal turn off(day, 1) delay time delay time, controller would detect it as daytime.", MIN, 1, 1),
    0x903D: Register("Load controlling modes", "0000H Manual Control, 0001H Light ON/OFF, 0002H Light ON+ Timer/, 0003H Time Control", LoadControlModes, 1, 1),
    0x903E: Register("Working time length 1", "The length of load output timer1, D15-D8,hour, D7-D0, minute", STR, 1, 1),
    0x903F: Register("Working time length 2", "The length of load output timer2, D15-D8, hour, D7-D0, minute", STR, 1, 1),
    0x9042: Register("Turn on timing 1 sec", "Turn on timing 1 sec", SEC, 1, 1),
    0x9043: Register("Turn on timing 1 min", "Turn on timing 1 min", MIN, 1, 1),
    0x9044: Register("Turn on timing 1 hour", "Turn on timing 1 hour", HOUR, 1, 1),
    0x9045: Register("Turn off timing 1 sec", "Turn off timing 1 sec", SEC, 1, 1),
    0x9046: Register("Turn off timing 1 min", "Turn off timing 1 min", MIN, 1, 1),
    0x9047: Register("Turn off timing 1 hour", "Turn off timing 1 hour", HOUR, 1, 1),
    0x9048: Register("Turn on timing 2 sec", "Turn on timing 2 sec", SEC, 1, 1),
    0x9049: Register("Turn on timing 2 min", "Turn on timing 2 min", MIN, 1, 1),
    0x904A: Register("Turn on timing 2 hour", "Turn on timing 2 hour", HOUR, 1, 1),
    0x904B: Register("Turn off timing 2 sec", "Turn off timing 2 sec", SEC, 1, 1),
    0x904C: Register("Turn off timing 2 min", "Turn off timing 2 min", MIN, 1, 1),
    0x904D: Register("Turn off timing 2 hour", "Turn off timing 2 hour", HOUR, 1, 1),
    0x9065: Register("Length of night", "Set default values of the whole night length of time. D15-D8,hour, D7-D0, minute", LENNIGHT, 1, 1),
    0x9067: Register("Battery rated voltage code", "0, auto recognize. 1-12V, 2-24V", STR, 1, 1),
    0x9069: Register("Load timing control selection", "Selected timeing period of the load.0, using one timer, 1-using two timer, likewise.", STR, 1, 1),
    0x906A: Register("Default Load On/Off in manual mode", "0-off, 1-on", STR, 1, 1),
    0x906B: Register("Equalize duration", "Usually 60-120 minutes.", MIN, 1, 1),
    0x906C: Register("Boost duration", "Usually 60-120 minutes.", MIN, 1, 1),
    0x906D: Register("Discharging percentage", "Usually 20%-80%. The percentage of battery's remaining capacity when stop charging", P, 1, 1),
    0x906E: Register("Charging percentage", "Depth of charge, 20%-100%.", P, 1, 1),
    0x9070: Register("Management modes of battery charging and discharging", "Management modes of battery charge and discharge, voltage compensation : 0 and SOC : 1.", STR, 1, 1),
    0x3200: Register("Battery status", "Battery real time state", BatteryStatus, None, 1),
    0x3201: Register("Charging equipement status", "Charging equipment status", ChargingEquipmentStatus, None, 1),
    0x3202: Register("Discharging equipement status", "Discharging equipment status", DischargingEquipmentStatus, None, 1),
    # Coils
    2: Register("Manual control the load", "When the load is manual mode, 1-manual on, 0 -manual off", MANUALMODE, 1, 1),
    5: Register("Enable load test mode", "1 Enable, 0 Disable(normal)", ENABLETEST, 1, 1)}

# Coils(read-write)
coils = {
    6: Register("Force the load on/off", "1 Turn on, 0 Turn off (used for temporary test of the load)", STR, 1, 1),
    # Discrete input (read-only)
    0x2000: Register("Over temperature inside the device", "1 The temperature inside the controller is higher than the over-temperature protection point. 0 Normal", STR, 1, 1),
    0x200C: Register("Day/Night", "1-Night, 0-Day", STR, 1, 1)
    }
