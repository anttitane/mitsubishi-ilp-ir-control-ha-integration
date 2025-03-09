from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

DOMAIN = "mitsubishi_airpump"

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up the Mitsubishi Air Pump integration asynchronously."""
    hass.data.setdefault(DOMAIN, {})
    return True
