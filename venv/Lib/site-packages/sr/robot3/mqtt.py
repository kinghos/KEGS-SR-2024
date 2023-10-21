from __future__ import annotations

import atexit
import json
import logging
from threading import Lock
from typing import Any, Callable, Optional, TypedDict, Union
from urllib.parse import urlparse

import paho.mqtt.client as mqtt

LOGGER = logging.getLogger(__name__)


class MQTTClient:
    def __init__(
        self,
        client_name: Optional[str] = None,
        topic_prefix: Optional[str] = None,
        mqtt_version: int = mqtt.MQTTv5,
        use_tls: Union[bool, str] = False,
        username: str = '',
        password: str = '',
    ) -> None:
        self._subscriptions_lock = Lock()
        self._subscriptions: dict[
            str, Callable[[mqtt.Client, Any, mqtt.MQTTMessage], None]
        ] = {}
        self.topic_prefix = topic_prefix
        self._client_name = client_name

        self._client = mqtt.Client(client_id=client_name, protocol=mqtt_version)
        self._client.on_connect = self._on_connect

        if use_tls:
            self._client.tls_set()
            if use_tls == 'insecure':
                self._client.tls_insecure_set(True)

        if username:
            self._client.username_pw_set(username, password)

    def connect(self, host: str, port: int) -> None:
        """
        Connect to the MQTT broker and start event loop in background thread.

        Registers an atexit routine that tears down the client.
        """
        if self._client.is_connected():
            LOGGER.error("Attempting connection, but client is already connected.")
            return

        try:
            self._client.connect(host, port, keepalive=60)
        except (TimeoutError, ValueError, ConnectionRefusedError):
            LOGGER.error(f"Failed to connect to MQTT broker at {host}:{port}")
            return
        self._client.loop_start()
        atexit.unregister(self.disconnect)  # Avoid duplicate atexit handlers
        atexit.register(self.disconnect)

    @classmethod
    def establish(
        cls, host: str, port: int, **kwargs: Any,
    ) -> 'MQTTClient':
        """Create client and connect."""
        client = cls(**kwargs)
        client.connect(host, port)
        return client

    def disconnect(self) -> None:
        """Disconnect from the broker and close background event loop."""
        self._client.disconnect()
        self._client.loop_stop()
        atexit.unregister(self.disconnect)

    def subscribe(
        self,
        topic: str,
        callback: Callable[[mqtt.Client, Any, mqtt.MQTTMessage], None],
        abs_path: bool = False,
    ) -> None:
        """Subscribe to a topic and assign a callback for messages."""
        if not abs_path and self.topic_prefix is not None:
            full_topic = f"{self.topic_prefix}/{topic}"
        else:
            full_topic = topic

        with self._subscriptions_lock:
            self._subscriptions[full_topic] = callback
        self._subscribe(full_topic, callback)

    def _subscribe(
        self,
        topic: str,
        callback: Callable[[mqtt.Client, Any, mqtt.MQTTMessage], None],
    ) -> None:
        LOGGER.debug(f"Subscribing to {topic}")
        self._client.message_callback_add(topic, callback)
        self._client.subscribe(topic, qos=1)

    def unsubscribe(self, topic: str) -> None:
        """Unsubscribe from a topic."""
        try:
            with self._subscriptions_lock:
                del self._subscriptions[topic]
        except KeyError:
            pass
        self._client.message_callback_remove(topic)
        self._client.unsubscribe(topic)

    def publish(
        self,
        topic: str,
        payload: Union[bytes, str],
        retain: bool = False,
        *,
        abs_topic: bool = False,
    ) -> None:
        """Publish a message to the broker."""
        if not self._client.is_connected():
            LOGGER.debug(
                "Attempted to publish message, but client is not connected.",
            )
            return

        if not abs_topic and self.topic_prefix:
            topic = f"{self.topic_prefix}/{topic}"

        try:
            self._client.publish(topic, payload=payload, retain=retain, qos=1)
        except ValueError as e:
            raise ValueError(f"Cannot publish to MQTT topic: {topic}") from e

    def wrapped_publish(
        self,
        topic: str,
        payload: Union[bytes, str],
        retain: bool = False,
        *,
        abs_topic: bool = True,
    ) -> None:
        """Wrap a payload up to be decodable as JSON."""
        if isinstance(payload, bytes):
            payload = payload.decode('utf-8')
        self.publish(
            topic,
            json.dumps({"data": payload}),
            retain=retain, abs_topic=abs_topic)

    def _on_connect(
        self, client: mqtt.Client, userdata: Any, flags: dict[str, int], rc: int,
        properties: Optional[mqtt.Properties] = None,
    ) -> None:
        """Callback run each time the client connects to the broker."""
        if rc != mqtt.CONNACK_ACCEPTED:
            LOGGER.warning(
                f"Failed to connect to MQTT broker. Return code: {mqtt.error_string(rc)}"
            )
            return

        LOGGER.debug("Connected to MQTT broker.")

        with self._subscriptions_lock:
            for topic, callback in self._subscriptions.items():
                self._subscribe(topic, callback)


class MQTTVariables(TypedDict):
    host: str
    port: int
    topic_prefix: str
    use_tls: Union[bool, str]
    username: Optional[str]
    password: Optional[str]


def unpack_mqtt_url(url: str) -> MQTTVariables:
    """
    Unpack an MQTT URL into its components to be passed to MQTTClient.

    The URL should be in the format:
    mqtt[s]://[<username>[:<password>]]@<host>[:<port>]/<topic_root>
    """
    url_parts = urlparse(url)

    if url_parts.scheme not in ('mqtt', 'mqtts'):
        raise ValueError(f"Invalid scheme: {url_parts.scheme}")

    use_tls = (url_parts.scheme == 'mqtts')

    if url_parts.hostname is None:
        raise ValueError("No hostname given")

    return MQTTVariables(
        host=url_parts.hostname,
        port=url_parts.port or (8883 if use_tls else 1883),
        topic_prefix=url_parts.path,
        use_tls=use_tls,
        username=url_parts.username,
        password=url_parts.password,
    )
