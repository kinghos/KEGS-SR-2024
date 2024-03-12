from .arduino import AnalogPins, GPIOPinMode
from .astoria import RobotMode
from .exceptions import (
    BoardDisconnectionError, MetadataKeyError, MetadataNotReadyError,
)
from .kch import Colour, UserLED
from .logging import add_trace_level
from .motor_board import MotorPower
from .power_board import Note, PowerOutputPosition
from .raw_serial import RawSerialDevice
from .robot import Robot
from .utils import list_ports

add_trace_level()

BRAKE = MotorPower.BRAKE
COAST = MotorPower.COAST

A0 = AnalogPins.A0
A1 = AnalogPins.A1
A2 = AnalogPins.A2
A3 = AnalogPins.A3
A4 = AnalogPins.A4
A5 = AnalogPins.A5

COMP = RobotMode.COMP
DEV = RobotMode.DEV

INPUT = GPIOPinMode.INPUT
INPUT_PULLUP = GPIOPinMode.INPUT_PULLUP
OUTPUT = GPIOPinMode.OUTPUT

OUT_H0 = PowerOutputPosition.H0
OUT_H1 = PowerOutputPosition.H1
OUT_L0 = PowerOutputPosition.L0
OUT_L1 = PowerOutputPosition.L1
OUT_L3 = PowerOutputPosition.L3
OUT_FIVE_VOLT = PowerOutputPosition.FIVE_VOLT

LED_A = UserLED.A
LED_B = UserLED.B
LED_C = UserLED.C

__all__ = [
    "A0",
    "A1",
    "A2",
    "A3",
    "A4",
    "A5",
    "BRAKE",
    "BoardDisconnectionError",
    "COAST",
    "COMP",
    "Colour",
    "DEV",
    "INPUT",
    "INPUT_PULLUP",
    "LED_A",
    "LED_B",
    "LED_C",
    "MetadataKeyError",
    "MetadataNotReadyError",
    "Note",
    "OUTPUT",
    "OUT_FIVE_VOLT",
    "OUT_H0",
    "OUT_H1",
    "OUT_L0",
    "OUT_L1",
    "OUT_L3",
    "RawSerialDevice",
    "Robot",
    "list_ports",
]
