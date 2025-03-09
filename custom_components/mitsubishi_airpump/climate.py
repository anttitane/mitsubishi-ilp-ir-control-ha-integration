import logging
import requests
from homeassistant.components.climate import ClimateEntity, HVACMode, ClimateEntityFeature
from homeassistant.components.climate.const import (
    SUPPORT_TARGET_TEMPERATURE,
    SUPPORT_FAN_MODE
)
from homeassistant.const import TEMP_CELSIUS, ATTR_TEMPERATURE

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

    @property
    def name(self):
        """Return the name of the climate entity."""
        return "Mitsubishi Air Pump"

    @property
    def temperature_unit(self):
        """Return the unit of measurement."""
        return TEMP_CELSIUS

    @property
    def hvac_modes(self):
        """List the available HVAC modes."""
        return [HVACMode.OFF, HVACMode.COOL, HVACMode.HEAT]

    @property
    def hvac_mode(self):
        """Return current HVAC mode."""
        return self._hvac_mode

    @property
    def supported_features(self):
        """Return the supported features."""
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

    def set_temperature(self, **kwargs):
        """Set the target temperature."""
        if ATTR_TEMPERATURE in kwargs:
            self._target_temperature = kwargs[ATTR_TEMPERATURE]
            self._send_command()

    def set_fan_mode(self, fan_mode):
        """Set the fan mode."""
        self._fan_mode = fan_mode
        self._send_command()

    def set_hvac_mode(self, hvac_mode):
        """Set the HVAC mode."""
        if hvac_mode in self.hvac_modes:
            self._hvac_mode = hvac_mode
            self._send_command()
        else:
            _LOGGER.warning("Invalid HVAC mode: %s", hvac_mode)

    def _send_command(self):
        """Send command to FastAPI server."""
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

        try:
            response = requests.post(url, json=data)
            response.raise_for_status()
            _LOGGER.info("Sent command: %s", response.json())
        except requests.exceptions.RequestException as e:
            _LOGGER.error("Error sending command: %s", e)
