import functools
import logging
import sys
from copy import deepcopy
from enum import Enum
from json import JSONDecodeError
from pathlib import Path
from threading import Event, Lock
from time import sleep
from typing import Any, ClassVar, NewType, Optional, Tuple

from paho.mqtt.client import Client as MQTT
from paho.mqtt.client import MQTTMessage, MQTTv5, MQTTv311
from pydantic import BaseModel, ValidationError

from .mqtt import MQTTClient

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib

ASTORIA_VERSION = '0.11.2'

LOGGER = logging.getLogger(__name__)
CONFIG_SEARCH_PATHS = [
    Path("astoria.toml"),
    Path("/etc/astoria.toml"),
]


# Astoria config

class MQTTBrokerInfo(BaseModel):
    """MQTT Broker Information."""
    class Config:
        extra = 'forbid'

    host: str
    port: int
    enable_tls: bool = False
    topic_prefix: str = "astoria"
    force_protocol_version_3_1: bool = False


class AstoriaConfig(BaseModel):
    """Config schema for Astoria."""

    mqtt: MQTTBrokerInfo

    @classmethod
    def _get_config_path(cls, config_path: Optional[str] = None) -> Path:
        """Check for a config file or search the filesystem for one."""
        if config_path is None:
            for path in CONFIG_SEARCH_PATHS:
                if path.is_file():
                    return path
        else:
            path = Path(config_path)
            if path.is_file():
                return path
        raise FileNotFoundError("Unable to find config file.")

    @classmethod
    def load(cls, config_str: Optional[str] = None) -> "AstoriaConfig":
        """Load the config."""
        config_path = cls._get_config_path(config_str)
        with config_path.open("rb") as fh:
            return cls.parse_obj(tomllib.load(fh))


# Metadata

class RobotMode(Enum):
    """Running Status of the manager daemon."""

    COMP = "COMP"
    DEV = "DEV"


class Metadata(BaseModel):
    """
    Astoria Metadata.

    As the metadata is passed into a templating engine for initial log lines,
    please do not add nested fields to this schema.
    """
    class Config:
        # Revalidate the model when fields are changed
        validate_assignment = True

    # From Meta USB
    arena: str = "A"
    zone: int = 0
    mode: RobotMode = RobotMode.DEV
    marker_offset: int = 0
    game_timeout: Optional[int] = None
    wifi_enabled: bool = True

    # From robot settings file
    wifi_ssid: Optional[str] = None
    wifi_psk: Optional[str] = None
    wifi_region: Optional[str] = None


# Process manager fields

class CodeStatus(str, Enum):
    """Status of the running code."""

    STARTING = "code_starting"
    RUNNING = "code_running"
    KILLED = "code_killed"
    FINISHED = "code_finished"
    CRASHED = "code_crashed"


DiskUUID = NewType("DiskUUID", str)


class DiskType(Enum):
    """Type of disk."""

    USERCODE = "USERCODE"
    METADATA = "METADATA"
    NOACTION = "NOACTION"


class DiskInfo(BaseModel):
    """Information about a mounted disk."""

    uuid: DiskUUID
    mount_path: Path
    disk_type: DiskType


# Manager messages

class ManagerMessage(BaseModel):
    """Common data that all manager messages output."""

    class Status(Enum):
        """Running Status of the manager daemon."""

        STOPPED = "STOPPED"
        RUNNING = "RUNNING"

    status: Status
    astoria_version: str = ASTORIA_VERSION


class ProcessManagerMessage(ManagerMessage):
    """
    Status message for Process Manager.

    Published to astoria/astprocd
    """

    code_status: Optional[CodeStatus]
    disk_info: Optional[DiskInfo]
    pid: Optional[int]


class MetadataManagerMessage(ManagerMessage):
    """
    Status message for Metadata Manager.

    Published to /astoria/astmetad
    """

    metadata: Metadata


# Remote start event
@functools.total_ordering
class StartButtonBroadcastEvent(BaseModel):
    """
    Schema for a remote start event.

    Trigger the robot code if it is waiting for the start button to be
    pressed. Does not affect or interact with the physical button as that
    is handled by the usercode driver.
    """

    name: ClassVar[str] = "start_button"

    event_name: str
    sender_name: str
    priority: int = 0

    def __gt__(self, other: "StartButtonBroadcastEvent") -> bool:
        return self.priority > other.priority


# Module Logic

class AstoriaInterface:
    def __init__(self, mqtt_client: MQTTClient) -> None:
        self._mqtt = mqtt_client
        self._metadata = Metadata()
        self._mount_path = Path("/dev/null")
        self._astoria_lock = Lock()
        self._start_pressed = Event()

        self._mqtt.subscribe("broadcast/start_button", self._process_remote_start)
        self._mqtt.subscribe("astmetad", self._process_metadata_update)
        self._mqtt.subscribe("astprocd", self._handle_astprocd_message)
        # Wait a short time for the mount path to be updated
        sleep(0.05)

    def _process_remote_start(
        self, client: MQTT, userdata: Any, msg: MQTTMessage,
    ) -> None:
        """Receive a remote start event."""
        try:
            event: StartButtonBroadcastEvent = StartButtonBroadcastEvent.parse_raw(msg.payload)
            LOGGER.debug(f"Received a {event.event_name} event from {event.sender_name}")
            self._start_pressed.set()
        except (JSONDecodeError, ValidationError) as e:
            LOGGER.debug(f"Unable to parse start button message: {e}")

    def _process_metadata_update(
        self, client: MQTT, userdata: Any, msg: MQTTMessage,
    ) -> None:
        """Update the metadata."""
        try:
            MetadataManagerMessage.update_forward_refs()
            message = MetadataManagerMessage.parse_raw(msg.payload)
            if message.status == MetadataManagerMessage.Status.RUNNING:
                LOGGER.debug("Received metadata")
                with self._astoria_lock:
                    self._metadata = message.metadata
            else:
                LOGGER.debug("Cannot get metadata, astmetad is not running")
        except (JSONDecodeError, ValidationError) as e:
            LOGGER.debug(f"Unable to parse metadata message: {e}")

    def _handle_astprocd_message(
        self, client: MQTT, userdata: Any, msg: MQTTMessage,
    ) -> None:
        """Update the mount path."""
        try:
            message = ProcessManagerMessage.parse_raw(msg.payload)
            if message.status == ProcessManagerMessage.Status.RUNNING:
                LOGGER.debug("Received process info")
                if message.disk_info:
                    with self._astoria_lock:
                        self._mount_path = message.disk_info.mount_path
            else:
                LOGGER.debug("Cannot get process info, astprocd is not running")
        except (JSONDecodeError, ValidationError) as e:
            LOGGER.debug(f"Unable to parse process message: {e}")

    def fetch_current_metadata(self) -> Metadata:
        """Fetch the current metadata."""
        with self._astoria_lock:
            return deepcopy(self._metadata)

    def fetch_mount_path(self) -> Path:
        """Fetch the current mount path."""
        with self._astoria_lock:
            return self._mount_path

    def get_start_button_pressed(self) -> bool:
        """Get the start button pressed status."""
        pressed = self._start_pressed.is_set()
        self._start_pressed.clear()
        return pressed


def init_mqtt(config: AstoriaConfig, client_name: str = 'sr-robot3') -> 'MQTTClient':
    """
    Helper method to create an MQTT client and connect.

    Uses values from astoria's config.
    """
    client = MQTTClient.establish(
        host=config.mqtt.host,
        port=config.mqtt.port,
        client_name=client_name,
        mqtt_version=MQTTv311 if config.mqtt.force_protocol_version_3_1 else MQTTv5,
        topic_prefix=config.mqtt.topic_prefix,
    )
    return client


def init_astoria_mqtt() -> Tuple[MQTTClient, AstoriaInterface]:
    """Initialise the MQTT client & Astoria integrations."""
    try:
        astoria_config = AstoriaConfig.load()
    except FileNotFoundError:
        LOGGER.warning("Unable to find astoria.toml, using default values")
        astoria_config = AstoriaConfig(mqtt=MQTTBrokerInfo(host="localhost", port=1883))

    mqtt_client = init_mqtt(astoria_config)
    astoria = AstoriaInterface(mqtt_client)

    return mqtt_client, astoria
