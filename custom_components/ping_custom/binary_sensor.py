import logging
import voluptuous as vol
from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.const import CONF_NAME
import homeassistant.helpers.config_validation as cv
from .ping_util import ping
from .const import DOMAIN, CONF_HOST, DEFAULT_NAME

_LOGGER = logging.getLogger(__name__)

# Platform schema for configuration
PLATFORM_SCHEMA = cv.PLATFORM_SCHEMA.extend({
    vol.Required(CONF_HOST): cv.string,
    vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
})

def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the fixed ping binary sensor."""
    host = config[CONF_HOST]
    name = config[CONF_NAME]

    add_entities([FixedPingSensor(host, name)], True)

class FixedPingSensor(BinarySensorEntity):
    """Representation of a Fixed-ID Ping binary sensor."""

    def __init__(self, host, name):
        self._host = host
        self._name = name
        self._is_on = False
        self._latency = None

    @property
    def name(self):
        return self._name

    @property
    def is_on(self):
        return self._is_on

    @property
    def extra_state_attributes(self):
        return {"latency_ms": self._latency}

    def update(self):
        """Perform the ping and update state."""
        success, latency = ping(self._host)
        self._is_on = success
        self._latency = latency
