import logging
from homeassistant.components.binary_sensor import BinarySensorEntity
from .ping_util import ping

_LOGGER = logging.getLogger(__name__)

class FixedPingSensor(BinarySensorEntity):
    """Representation of a Fixed-ID Ping binary sensor."""

    def __init__(self, host, name):
        """Initialize the sensor."""
        self._host = host
        self._name = name
        self._is_on = False
        self._latency = None

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def is_on(self):
        """Return True if host responds to ping."""
        return self._is_on

    @property
    def extra_state_attributes(self):
        """Return additional state attributes."""
        return {"latency_ms": self._latency}

    def update(self):
        """Perform the ping and update state."""
        try:
            success, latency = ping(self._host)
            self._is_on = success
            self._latency = latency
        except Exception as e:
            _LOGGER.error("Error pinging host %s: %s", self._host, e)
            self._is_on = False
            self._latency = None
