import logging
import aiohttp
from homeassistant.components.climate import ClimateEntity, HVACMode, ClimateEntityFeature
from homeassistant.const import UnitOfTemperature, ATTR_TEMPERATURE
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

_LOGGER = logging.getLogger(__name__)

SUPPORT_FLAGS = ClimateEntityFeature.TARGET_TEMPERATURE | ClimateEntityFeature.FAN_MODE

class MitsubishiAirPump(ClimateEntity):
    """Representation of a Mitsubishi Air Pump."""

    def __init__(self, host):
        """Initialize the air pump."""
        self._host = host
        self._hvac_mode = HVACMode.OFF
        self._target_temperature = 21
        self._fan_mode = "auto"
        self._attr_temperature_unit = UnitOfTemperature.CELSIUS

    @property
    def name(self):
        """Return the name of the climate entity."""
        return "Mitsubishi Air Pump"

    @property
    def hvac_modes(self):
        """Return available HVAC modes."""
        return {HVACMode.OFF, HVACMode.COOL, HVACMode.HEAT}

    @property
    def hvac_mode(self):
        """Return current HVAC mode."""
        return self._hvac_mode

    @property
    def supported_features(self):
        """Return supported features."""
        return SUPPORT_FLAGS

    @property
    def target_temperature(self):
        """Return the target temperature."""
        return self._target_temperature

    @property
    def fan_modes(self):
        """Return the available fan modes."""
        return ["auto", "low", "med", "high"]

    @property
    def fan_mode(self):
        """Return the current fan mode."""
        return self._fan_mode
    
    @property
    def device_info(self):
        """Return device information to group the entity under a device."""
        return {
            "identifiers": {("mitsubishi_airpump", self._host)},
            "name": "Mitsubishi Air Pump",
            "manufacturer": "Mitsubishi Electric, integration @anttitane",
            "model": "Smart AC",
            "sw_version": "1.0",
    }

    async def async_set_temperature(self, **kwargs):
        """Set the target temperature."""
        if ATTR_TEMPERATURE in kwargs:
            self._target_temperature = kwargs[ATTR_TEMPERATURE]
            await self._async_send_command()

    async def async_set_fan_mode(self, fan_mode):
        """Set the fan mode."""
        self._fan_mode = fan_mode
        await self._async_send_command()

    async def async_set_hvac_mode(self, hvac_mode):
        """Set the HVAC mode."""
        if hvac_mode in self.hvac_modes:
            self._hvac_mode = hvac_mode
            await self._async_send_command()
        else:
            _LOGGER.warning("Invalid HVAC mode: %s", hvac_mode)

    async def _async_send_command(self):
        """Send command to FastAPI server asynchronously."""
        url = f"http://{self._host}:8000/air_pump/"

        if self._hvac_mode == HVACMode.COOL:
            url += "cool/"
        elif self._hvac_mode == HVACMode.HEAT:
            url += "heat/"
        else:
            url += "off/"

        data = {
            "temperature": self._target_temperature,
            "fan_speed": self._fan_mode,
            "vertical_mode": "middle",
            "horizontal_mode": "middle"
        }

        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(url, json=data) as response:
                    response_data = await response.json()
                    _LOGGER.info("Sent command: %s", response_data)
            except aiohttp.ClientError as e:
                _LOGGER.error("Error sending command: %s", e)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    """Set up the Mitsubishi Air Pump climate entity."""
    _LOGGER.debug("async_setup_entry called for Mitsubishi Air Pump")

    host = entry.data.get("host")
    if not host:
        _LOGGER.error("No host provided for Mitsubishi Air Pump entity")
        return

    entity = MitsubishiAirPump(host)
    _LOGGER.debug(f"Adding entity: {entity.name}")

    async_add_entities([entity], True)
