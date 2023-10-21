"""KCH Driver."""
from __future__ import annotations

import atexit
import warnings
from enum import IntEnum, unique
from typing import Optional

try:
    import RPi.GPIO as GPIO  # isort: ignore
    HAS_HAT = True
except ImportError:
    HAS_HAT = False


@unique
class RobotLEDs(IntEnum):
    """Mapping of LEDs to GPIO Pins."""

    START = 9

    USER_A_RED = 24
    USER_A_GREEN = 10
    USER_A_BLUE = 25
    USER_B_RED = 27
    USER_B_GREEN = 23
    USER_B_BLUE = 22
    USER_C_RED = 4
    USER_C_GREEN = 18
    USER_C_BLUE = 17

    @classmethod
    def all_leds(cls) -> list[int]:
        """Get all LEDs."""
        return [c.value for c in cls]

    @classmethod
    def user_leds(cls) -> list[tuple[int, int, int]]:
        """Get the user programmable LEDs."""
        return [
            (cls.USER_A_RED, cls.USER_A_GREEN, cls.USER_A_BLUE),
            (cls.USER_B_RED, cls.USER_B_GREEN, cls.USER_B_BLUE),
            (cls.USER_C_RED, cls.USER_C_GREEN, cls.USER_C_BLUE),
        ]


@unique
class UserLED(IntEnum):
    """User Programmable LEDs."""

    A = 0
    B = 1
    C = 2


class Colour():
    """User LED colours."""

    OFF = (False, False, False)
    RED = (True, False, False)
    YELLOW = (True, True, False)
    GREEN = (False, True, False)
    CYAN = (False, True, True)
    BLUE = (False, False, True)
    MAGENTA = (True, False, True)
    WHITE = (True, True, True)


class KCH:
    """KCH Board."""
    __slots__ = ('_leds', '_pwm')

    def __init__(self) -> None:
        if HAS_HAT:
            GPIO.setmode(GPIO.BCM)
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")

                # If this is not the first time the code is run this init will
                # cause a warning as the gpio are already initialized, we can
                # suppress this as we know the reason behind the warning
                GPIO.setup(RobotLEDs.all_leds(), GPIO.OUT, initial=GPIO.LOW)
            self._pwm: Optional[GPIO.PWM] = None
        self._leds = tuple(
            LED(rgb_led) for rgb_led in RobotLEDs.user_leds()
        )

        if HAS_HAT:
            # We are not running cleanup so the LED state persists after the code completes,
            # this will cause a warning with `GPIO.setup()` which we can suppress
            # atexit.register(GPIO.cleanup)

            # Cleanup just the start LED to turn it off when the code exits
            # Mypy isn't aware of the version of atexit.register(func, *args)
            atexit.register(GPIO.cleanup, RobotLEDs.START)  # type: ignore[call-arg]

    @property
    def _start(self) -> bool:
        """Get the state of the start LED."""
        return GPIO.input(RobotLEDs.START) if HAS_HAT else False

    @_start.setter
    def _start(self, value: bool) -> None:
        """Set the state of the start LED."""
        if HAS_HAT:
            if self._pwm:
                # stop any flashing the LED is doing
                self._pwm.stop()
                self._pwm = None
            GPIO.output(RobotLEDs.START, GPIO.HIGH if value else GPIO.LOW)

    def _flash_start(self) -> None:
        """Set the start LED flashing at 1Hz."""
        if HAS_HAT:
            self._pwm = GPIO.PWM(RobotLEDs.START, 1)
            self._pwm.start(50)

    @property
    def leds(self) -> tuple['LED', ...]:
        """User programmable LEDs."""
        return self._leds


class LED:
    """User programmable LED."""
    __slots__ = ('_led',)

    def __init__(self, led: tuple[int, int, int]):
        self._led = led

    @property
    def r(self) -> bool:
        """Get the state of the Red LED segment."""
        return GPIO.input(self._led[0]) if HAS_HAT else False

    @r.setter
    def r(self, value: bool) -> None:
        """Set the state of the Red LED segment."""
        if HAS_HAT:
            GPIO.output(self._led[0], GPIO.HIGH if value else GPIO.LOW)

    @property
    def g(self) -> bool:
        """Get the state of the Green LED segment."""
        return GPIO.input(self._led[1]) if HAS_HAT else False

    @g.setter
    def g(self, value: bool) -> None:
        """Set the state of the Green LED segment."""
        if HAS_HAT:
            GPIO.output(self._led[1], GPIO.HIGH if value else GPIO.LOW)

    @property
    def b(self) -> bool:
        """Get the state of the Blue LED segment."""
        return GPIO.input(self._led[2]) if HAS_HAT else False

    @b.setter
    def b(self, value: bool) -> None:
        """Set the state of the Blue LED segment."""
        if HAS_HAT:
            GPIO.output(self._led[2], GPIO.HIGH if value else GPIO.LOW)

    @property
    def colour(self) -> tuple[bool, bool, bool]:
        """Get the colour of the user LED."""
        if HAS_HAT:
            return (
                GPIO.input(self._led[0]),
                GPIO.input(self._led[1]),
                GPIO.input(self._led[2]),
            )
        else:
            return False, False, False

    @colour.setter
    def colour(self, value: tuple[bool, bool, bool]) -> None:
        """Set the colour of the user LED."""
        if not isinstance(value, (tuple, list)) or len(value) != 3:
            raise ValueError("The LED requires 3 values for it's colour")

        if HAS_HAT:
            GPIO.output(
                self._led,
                tuple(
                    GPIO.HIGH if v else GPIO.LOW for v in value
                ),
            )
