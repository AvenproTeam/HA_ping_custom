"""The Ping Custom integration."""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.const import Platform

# List the platforms this integration supports
PLATFORMS = [Platform.BINARY_SENSOR]

# Optional: store coordinators or data per entry
# hass.data[DOMAIN][entry.entry_id] = ...

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Ping Custom from a config entry."""
    # Forward the setup to the binary_sensor platform
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    # Optional: clean up hass.data if you stored anything
    return unload_ok