"""The Arduino module provides an interface to the Arduino firmware."""
from __future__ import annotations

import logging
from contextlib import contextmanager
from time import sleep
from types import MappingProxyType
from typing import Generator, NamedTuple, Optional

from serial import Serial, SerialException, serial_for_url
from serial.tools.list_ports import comports

from .exceptions import BoardDisconnectionError
from .logging import log_to_debug
from .utils import Board, BoardIdentity, get_USB_identity

logger = logging.getLogger(__name__)
DEFAULT_BAUDRATE = 115200


class RawSerialDevice(NamedTuple):
    """A serial device to look for by serial number."""
    serial_number: str
    baudrate: int = DEFAULT_BAUDRATE


class RawSerial(Board):
    """
    The raw serial interface.

    This is intended to be used to communicate with Arduinos running custom
    firmwares and other custom boards.

    :param serial_port: The serial port to connect to.
    :param baudrate: The baudrate to use when connecting.
    :param identity: The identity of the board, as reported by the USB descriptor.
    """
    __slots__ = ('_serial', '_identity', 'delay_after_connect')

    @staticmethod
    def get_board_type() -> str:
        """
        Return the type of the board.
        For this class, it is unused.

        :return: The literal string 'RawSerial'.
        """
        return 'RawSerial'

    def __init__(
        self,
        serial_port: str,
        baudrate: int = DEFAULT_BAUDRATE,
        identity: Optional[BoardIdentity] = None,
    ) -> None:
        if identity is None:
            identity = BoardIdentity()

        # We know nothing about the board,
        # so we need to get the identity from the USB descriptor
        self._identity = identity

        # Open the serial port
        self._serial = serial_for_url(
            serial_port,
            baudrate=baudrate,
            timeout=0.5,  # 500ms timeout
            do_not_open=True,
        )

        # Certain boards will reset when the serial port is opened
        # Wait for the board to be ready to receive data
        self.delay_after_connect = 2
        self._reconnect()

    @classmethod
    def _get_supported_boards(
        cls,
        serial_devices: list[tuple[str, int]],
    ) -> MappingProxyType[str, RawSerial]:
        """
        Discover connected serial devices filtered by serial number.

        :param serial_devices: A list of serial ports to check (serial_number, baudrate),
            these are matched by serial number.
        :return: A mapping of board serial numbers to Arduinos
        """
        boards = {}
        serial_device_objs = [
            RawSerialDevice(serial_number, baudrate)
            for serial_number, baudrate in serial_devices
        ]
        device_lookup = {
            device.serial_number: device for device in serial_device_objs
        }

        serial_ports = comports()
        for port in serial_ports:
            found_device = device_lookup.get(port.serial_number)  # type: ignore[arg-type]
            if found_device is not None:
                # Create board identity from USB port info
                identity = get_USB_identity(port)
                identity = BoardIdentity(
                    manufacturer=identity.manufacturer,
                    board_type=identity.board_type,
                    asset_tag=identity.asset_tag,
                    sw_version=f"{port.vid:04x}:{port.pid:04x}",
                )

                try:
                    board = cls(port.device, found_device.baudrate, identity)
                except Exception as err:
                    logger.warning(
                        f"Failed to connect to {found_device.serial_number} because: {err}")
                    continue

                boards[identity.asset_tag] = board

        return MappingProxyType(boards)

    @log_to_debug
    def identify(self) -> BoardIdentity:
        """
        Get the cached identity of the port from the USB descriptor.

        :return: The identity of the port.
        """
        return self._identity

    @property
    @log_to_debug
    def port(self) -> Serial:
        """
        The pySerial Serial object.

        :return: The raw serial port.
        """
        return self._serial

    @log_to_debug
    def write(self, data: bytes) -> None:
        """
        Send bytes to the port.

        :param data: The bytes to send.
        """
        with self._handle_serial_reconnect():
            self._serial.write(data)

    @log_to_debug
    def read(self, size: int) -> bytes:
        """
        Read a line from the port.

        :param size: The number of bytes to read.
        :return: The line read from the port.
        """
        with self._handle_serial_reconnect():
            return self._serial.read(size)

    @log_to_debug
    def read_until(self, terminator: bytes = b'\n') -> bytes:
        """
        Read until a terminator is reached.

        :param terminator: The terminator character to stop reading at.
        :return: The data read from the port.
        """
        with self._handle_serial_reconnect():
            return self._serial.read_until(terminator)

    @contextmanager
    def _handle_serial_reconnect(self) -> Generator[None, None, None]:
        """
        A context manager to handle reconnecting the serial ports on faults.
        """
        if not self._serial.is_open:
            if not self._reconnect():
                # If the serial port cannot be opened raise an error
                raise BoardDisconnectionError(
                    f'Connection to port {self._identity.board_type}:'
                    f'{self._identity.asset_tag} could not be established',
                )
        try:
            yield
        except (SerialException, OSError):
            # Serial connection failed, close the port and raise an error
            self._serial.close()
            logger.warning(
                f'Port {self._identity.board_type}:{self._identity.asset_tag} disconnected',
            )
            raise BoardDisconnectionError(
                f'Port {self._identity.board_type}:{self._identity.asset_tag} '
                'disconnected during transaction',
            )

    def _reconnect(self) -> bool:
        """
        Connect to the class's serial port.

        This is called automatically when a message is sent to the board if the port is closed.

        :raises serial.SerialException: If the serial port cannot be opened.
        :return: True if the serial port was opened successfully, False otherwise.
        """
        try:
            self._serial.open()
            # Wait for the board to be ready to receive data
            # Certain boards will reset when the serial port is opened
            sleep(self.delay_after_connect)
            self._serial.reset_input_buffer()
        except SerialException:
            logger.error(
                'Failed to connect to port '
                f'{self._identity.board_type}:{self._identity.asset_tag}',
            )
            return False

        logger.info(
            f'Connected to port {self._identity.board_type}: {self._identity.asset_tag}',
        )
        return True

    def __repr__(self) -> str:
        return f"<{self.__class__.__qualname__}: {self._serial}>"
