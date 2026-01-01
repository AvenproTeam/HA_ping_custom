"""The GC-6612Pro Ping integration."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .config_flow import PingCustomConfigFlow  # ← ¡ESTA IMPORTACIÓN ES LA CLAVE!
from .const import DOMAIN

# Lista de plataformas soportadas
PLATFORMS: list[Platform] = [Platform.BINARY_SENSOR]

_LOGGER = logging.getLogger(__name__)

async def async_setup(hass: HomeAssistant, config: dict[str, Any]) -> bool:
    """Configuración alternativa si es necesario (opcional para integraciones modernas)."""
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Configura la integración desde una entrada de configuración."""
    # Deshabilita la entrada futura si es necesario
    entry.async_on_unload(
        hass.bus.async_listen(
            f"{DOMAIN}_updated", lambda e: hass.config_entries.async_reload(entry.entry_id)
        )
    )

    # Forward al sensor binario
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    _LOGGER.info("Integración GC-6612Pro Ping configurada correctamente para %s", entry.title)
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Descarga una entrada de configuración."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        # Limpia datos si los hay
        if DOMAIN in hass.data and entry.entry_id in hass.data[DOMAIN]:
            hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
