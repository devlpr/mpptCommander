from collections import namedtuple
# Module with all the conversion functions used for registers
#
# All conversion functions follow an upper case convention to differentiate them
# from other regular functions.

class Result(namedtuple("Result", ["register", "unit", "value"])):
    """
    @type register: integer
    @param register: The integer used to describe a register (e.g. 0x3000)
    @type unit: string
    @param unit: The units that the value is in
    @type value: number or string
    @param value: The result in the units mentioned above
    """
    __slots__ = ()
    def __str__(self):
        return "Result(register: %s, unit: %s, value: %s)" % (self.register,
                                                              self.unit,
                                                              self.value)

def __getLowAndHighBytes(value):
    high = (value & 0b1111111100000000) >> 8
    low = value & 0b0000000011111111
    return (high, low)


def V(address, value, times):
    return Result(address, "Volts", value / float(times))


def A(address, value, times):
    return Result(address, "Amps", value / float(times))


def W(address, value, times):
    return Result(address, "Watts", value / float(times))


def D(address, value, times):
    return Result(address, "Degrees C", value / float(times))


def P(address, value, times):
    return Result(address, "Percent", value)


def KWH(address, value, times):
    return Result(address, "KWH", value / float(times))


def AH(address, value, times):
    return Result(address, "AH", value)


def SEC(address, value, times):
    return Result(address, "Seconds", (value / float(times)))


def MIN(address, value, times):
    return Result(address, "Minute", (value / float(times)))


def HOUR(address, value, times):
    return Result(address, "Hour", (value / float(times)))


def MONTH(address, value, times):
    return Result(address, "Month", (value / float(times)))


def HOURMIN(address, value, times):
    hour, minute = __getLowAndHighBytes(value)
    results = []
    results.append(Result(address, "Hour", hour))
    results.append(Result(address, "Minute", minute))
    return results


def RTCSECMIN(address, value, times):
    minute, second = __getLowAndHighBytes(value)
    results = []
    results.append(Result(address, "Minute", minute))
    results.append(Result(address, "Seconds", second))
    return results


def RTCHOURDAY(address, value, times):
    day, hour = __getLowAndHighBytes(value)
    results = []
    results.append(Result(address, "Day", day))
    results.append(Result(address, "Hour", hour))
    return results


def RTCYEARMONTH(address, value, times):
    year, month = __getLowAndHighBytes(value)
    results = []
    results.append(Result(address, "Year", year))
    results.append(Result(address, "Month", month))
    return results


def OVERTEMP(address, value, times):
    return Result(address, "Over Temp", "Yes" if value == 1 else "No")


def DAYNIGHT(address, value, times):
    return Result(address, "Night", True if value == 1 else False)


def OFFON(address, value, times):
    return Result(address, "On", True if value == 1 else False)


def COEF(address, value, times):
    return Result(address, "mV/C/2", value / times)


def MANAGEMENTMODES(address, value, times):
    return Result(address,
                  "Management Mode",
                  "SOC" if value == 1 else "voltage compensation")


def CHARGINGMODE(address, value, times):
    ret = None
    if value == 0x00:
        ret = "Connect/Disconnect"
    elif value == 0x01:
        ret = "PWM"
    elif value == 0x02:
        ret = "MPPT"
    else:
        raise RuntimeError("No Such Charging Mode: %s" % value)
    return Result(address, "Charging Mode", ret)


def BATTERYTYPE(address, value, times):
    ret = None
    if value == 0x01:
        ret = "Sealed"
    elif value == 0x02:
        ret = "Gel"
    elif value == 0x03:
        ret = "Flooded"
    elif value == 0x0:
        ret = "User defined"
    else:
        raise RuntimeError("No Such Battery Type: %s" % value)
    return Result(address, "Battery Type", ret)


def BATTERYRATEDVOLTAGE(address, value, times):
    """
    0, auto recognize. 1-12V, 2-24V
    """
    ret = None
    if value == 0:
        ret = "auto recognize"
    elif value == 1:
        ret = "12v"
    elif value == 2:
        ret = "24v"
    else:
        raise RuntimeError("No Such Battery Rated Voltage: %s" % value)
    return Result(address, "Battery Rated Voltage", ret)


def LOADCONTROLMODES(address, value, times):
    ret = None
    if value == 0x0:
        ret = "User defined"
    elif value == 0x01:
        ret = "Light ON/OFF"
    elif value == 0x02:
        ret = "Light ON+ Timer"
    elif value == 0x03:
        ret = "Time Control"
    else:
        raise RuntimeError("No Such Battery Type: %s" % value)
    return Result(address, "Load Control Modes", ret)


def LOADTIMINGCONTROLSELECTION(address, value, times):
    """
    Selected timing period of the load
    0, using one timer, 1-using two timer, etc...
    """
    return Result(address,
                  "Load Timing Control Selection (Number of timers)",
                  value + 1)


def MANUALMODE(address, value, times):
    ret = None
    if value == 0x0:
        ret = "Auto"
    elif value == 0x01:
        ret = "Manual"
    else:
        raise RuntimeError("No Such Mode: %s" % value)
    return Result(address, "Manual Mode", ret)



def ENABLETEST(address, value, times):
    ret = None
    if value == 0x0:
        ret = "Enabled"
    elif value == 0x01:
        ret = "Disabled"
    else:
        raise RuntimeError("No Such Test Mode: %s" % value)
    return Result(address, "Enable Test", ret)


def BATTERYSTATUS(address, value, times):
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
    results = []
    res = None
    temp = value & 0b0000000000001111
    if temp == 0x0:
        res = "normal"
    elif temp == 0x01:
        res = "over volt"
    elif temp == 0x02:
        res = "under volt"
    elif temp == 0x03:
        res = "low volt disconnect"
    elif temp == 0x04:
        res = "fault"
    else:
        raise RuntimeError("No such battery voltage status: %s" % value)
    results.append(Result(address, "Battery Voltage", res))

    res = None
    temp = (value & 0b0000000011110000) >> 4
    if temp == 0x0:
        res = "normal"
    elif temp == 0x01:
        res = "higher than settings)"
    elif temp == 0x02:
        res = "lower than settings"
    else:
        raise RuntimeError("No such battery temperature status: %s" % value)
    results.append(Result(address, "Battery Temperature", res))

    res = None
    temp = (value & 0b0000000100000000) >> 8
    if temp == 0x0:
        res = "normal"
    elif temp == 0x01:
        res = "abnormal"
    else:
        raise RuntimeError("No such battery resistance status: %s" % value)
    results.append(Result(address, "Battery Internal Resistance", res))

    res = 0
    temp = (value & 0b1000000000000000) >>  15
    if temp == 0x0:
        res = "normal"
    elif temp == 0x01:
        res = "wrong"
    else:
        raise RuntimeError("No such battery id value: %s" % value)
    results.append(Result(address, "Rated Voltage ID", res))
    return results


def CHARGINGEQUIPMENTSTATUS(address, value, times):
    """
    D15-D14:
        00H normal
        01H low
        02H high
        03H no access input volt error
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
    results = []
    res = None
    temp = (value & 0b1100000000000000) >> 14
    if temp == 0x0:
        res = "normal"
    elif temp == 0x01:
        res = "low"
    elif temp == 0x02:
        res = "high"
    elif temp == 0x03:
        res = "no access input volt error"
    else:
        raise RuntimeError("No such charging equipment status: %s" % value)
    results.append(Result(address, "Charging Equipment Status", res))

    res = None
    temp = (value & 0b0011000000000000) >> 12
    if temp == 0x0:
        res = "light"
    elif temp == 0x01:
        res = "moderate"
    elif temp == 0x02:
        res = "rated"
    elif temp == 0x03:
        res = "overload"
    else:
        raise RuntimeError("No such output power: %s" % value)
    results.append(Result(address, "Output Power", res))

    tuples = [("Short Circuit", 0b0000100000000000, 11),
              ("Unable To Discharge", 0b0000010000000000, 10),
              ("Unable To Stop Discharging", 0b0000001000000000, 9),
              ("OutputVoltageAbnormal", 0b0000000100000000, 8),
              ("Input Overpressure", 0b0000000010000000, 7),
              ("High Voltage Side Short", 0b0000000001000000, 6),
              ("Boost Overpressure", 0b0000000000100000, 5),
              ("Output Overpressure", 0b0000000000010000, 4),
              ("Fault", 0b0000000000000010, 1),
              ("Running", 0b0000000000000001, 0)]

    # Iterate through the above tuples and generate output for each bitmasked
    # and shifted value
    for tup in tuples:
        name = tup[0]
        mask = tup[1]
        shift = tup[2]
        temp = (value & mask) >> shift
        res = None
        if temp == 0x1:
            res = "True"
        else:
            res = "False"
        results.append(Result(address, name, res))

    return results


def DISCHARGINGEQUIPMENTSTATUS(address, value, times):
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
    D9: The load is over current.
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
    results = []
    res = None
    stat = ["InputVoltStatus", ]
    temp = (value & 0b1100000000000000) >> 14
    if temp == 0x0:
        res = "normal"
    elif temp == 0x01:
        res = "no power connected"
    elif temp == 0x02:
        res = "higher volt input"
    elif temp == 0x03:
        res = "input voltage error"
    else:
        raise RuntimeError("No such input volt status: %s" % value)
    results.append(Result(address, "Input Volt Status", res))

    res = None
    temp = (value & 0b0000000000001100) >> 2
    if temp == 0x0:
        res = "no charging"
    elif temp == 0x01:
        res = "float"
    elif temp == 0x02:
        res = "boost"
    elif temp == 0x03:
        res = "equalization"
    else:
        raise RuntimeError("No such charging status: %s" % value)
    results.append(Result(address, "Charging Status", res))

    tuples = [("Charging MOSFET Short", 0b0010000000000000, 13),
              ("Charging/Anti-Reverse MOSFET Short", 0b0001000000000000, 12),
              ("Anti-reverse MOSFET Short", 0b0000100000000000, 11),
              ("Input Overcurrent", 0b0000010000000000, 10),
              ("Load Overcurrent", 0b0000001000000000, 9),
              ("Load Short", 0b0000000100000000, 8),
              ("Load MOSFET Short", 0b0000000010000000, 7),
              ("PV Short", 0b0000000001000000, 4),
              ("Status", 0b0000000000000010, 1),
              ("Running", 0b0000000000000001, 0)]

    # Iterate through the above tuples and generate output for each bitmasked
    # and shifted value
    for tup in tuples:
        name = tup[0]
        mask = tup[1]
        shift = tup[2]
        res = None
        temp = (value & mask) >> shift
        if temp == 0x1:
            res = "True"
        else:
            res = "False"
        results.append(Result(address, name, res))

    return results


