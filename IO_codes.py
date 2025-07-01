OEG_MODE = {
    1: "Enabled",
    2: "Homed",
    4: "Ready",
    8: "Faulted",
    16: "Warning",
    32: "Faul or Warning",
    64: "Default mode of operation",
    128: "Alternate mode of operation",
    4096: "Startup complete"
}

IEG_MOTION = {
    4: "Stop Motion",
    8: "Pause Move",
    16: "Jog Positive",
    32: "Jog Negative",
    64: "Jog Fast",
    256: "Initiate Home Move",
    1024: "Emergency Move",
    1024: "Emergency Move",
}

OEG_MOTION = {
    1: "Stopped",
    2: "Paused",
    4: "Jogging",
    8: "Jogging plus",
    16: "Jogging minus",
    32: "Homing active",
    64: "Startup active",
    128: "N/A",
    256: "Dedicated move active",
    512: "Move active",
    1024: "Secondary move active",
    2048: "N/A",
    4096: "In position",
    8192: "At home position one",
    16384: "At home position two",
    32768: "Dedicated move position",
}


IEG_MODE = {
    1: "Enable Momentary",
    2: "Enable maintained",
    128: "Enable Alternate operating mode",
    1024: "Define home position 1",
    2048: "Define home position 2",
    16384: "Break override",
    32768: "Fault Reset",
}

FAULTS = {
    1: "PEAK CURRENT",
    2: "CONTINOUS CURRENT",
    4: "POSITION TRACKING",
    8: "MOVE TerminaTION",
    16: "Low BUS VOLTAGE",
    32: "HIGH BUS VOLTAGE",
    64: "FOLLOWING ERROR",
    128: "BOARD TEMPERATURE",
    256: "ACTUATOR TEMP",
    512: "LOSS of SIGNAL",
    1024: "COMMUNICATION FAULT",
    2048: "HARDWARE OVERCURRENT",
    4096: "ABSOLUTE HALL BOARD BATTERY",
    8192: "USER PARAMETER ERROR",
    16384: "FACTORY PARAMETERS FAULT",
    32768: "RESTART FAULT" 
}

OPTIONS = {
    16: "plimitminusenabled",
    32: "plimitPlusEnabled"
}