# Module with all the conversion functions used for registers

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
    return "%s ah" % value


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
    temp = value & 0b0000000000001111
    if temp == 0x0:
        stat.append("normal")
    elif temp == 0x01:
        stat.append("over volt")
    elif temp == 0x02:
        stat.append("under volt")
    elif temp == 0x03:
        stat.append("low volt disconnect")
    elif temp == 0x04:
        stat.append("fault")
    else:
        raise RuntimeError("No such battery voltage status: %s" % value)

    stat.append(", Battery Temperature:")
    temp = (value & 0b0000000011110000) >> 4
    if temp == 0x0:
        stat.append("normal")
    elif temp == 0x01:
        stat.append("higher than settings)")
    elif temp == 0x02:
        stat.append("lower than settings")
    else:
        raise RuntimeError("No such battery temperature status: %s" % value)

    stat.append(", Battery internal resistance:") # D8
    temp = (value & 0b0000000100000000) >> 8
    if temp == 0x0:
        stat.append("normal")
    elif temp == 0x01:
        stat.append("abnormal")
    else:
        raise RuntimeError("No such battery resistance status: %s" % value)

    stat.append(", Rated voltage ID:") # D15
    temp = (value & 0b1000000000000000) >>  15
    if temp == 0x0:
        stat.append("normal")
    elif temp == 0x01:
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
    return "hour:minute %s:%s" % (hour, minute)


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


def OVERTEMP(value, times):
    return "Yes" if value == 1 else "No"


def DAYNIGHT(value, times):
    return "Night" if value == 1 else "Day"


def FORCELOAD(value, times):
    return "On" if value == 1 else "Off"

