import logging
import aiohttp
from homeassistant.components.climate import ClimateEntity, HVACMode, ClimateEntityFeature
from homeassistant.const import UnitOfTemperature, ATTR_TEMPERATURE
from homeassistant.const import PRECISION_WHOLE
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

SUPPORT_FLAGS = (
    ClimateEntityFeature.TARGET_TEMPERATURE
    | ClimateEntityFeature.FAN_MODE
    | ClimateEntityFeature.SWING_MODE
    | ClimateEntityFeature.SWING_HORIZONTAL_MODE
)

# Fan mode mappings
FAN_MODE_DISPLAY_TO_INTERNAL = {
    "Auto": "auto",
    "Low": "low",
    "Medium": "med",
    "High": "high"
}
FAN_MODE_INTERNAL_TO_DISPLAY = {v: k for k, v in FAN_MODE_DISPLAY_TO_INTERNAL.items()}

# Vertical swing mode mappings
SWING_MODE_DISPLAY_TO_INTERNAL = {
    "Auto": "auto",
    "Top": "top",
    "Middle Top": "middle_top",
    "Middle": "middle",
    "Middle Bottom": "middle_bottom",
    "Bottom": "bottom",
    "Swing": "swing"
}
SWING_MODE_INTERNAL_TO_DISPLAY = {v: k for k, v in SWING_MODE_DISPLAY_TO_INTERNAL.items()}

# Horizontal swing mode mappings
SWING_HORIZ_MODE_DISPLAY_TO_INTERNAL = {
    "Not Set": "not_set",
    "Left": "left",
    "Middle Left": "middle_left",
    "Middle": "middle",
    "Middle Right": "middle_right",
    "Right": "right",
    "Swing": "swing"
}
SWING_HORIZ_MODE_INTERNAL_TO_DISPLAY = {
    v: k for k, v in SWING_HORIZ_MODE_DISPLAY_TO_INTERNAL.items()
}


class MitsubishiIlpIrControl(ClimateEntity):
    def __init__(self, host):
        """Initialize the air pump."""
        _LOGGER.debug("Initializing Mitsubishi ILP IR Control entity")
        self._host = host
        self._hvac_mode = HVACMode.OFF
        self._target_temperature = 21
        self._attr_precision = PRECISION_WHOLE
        self._attr_target_temperature_step = 1.0
        self._fan_mode = "auto"
        self._swing_mode = "middle_top"
        self._swing_horizontal_mode = "middle"
        self._attr_temperature_unit = UnitOfTemperature.CELSIUS
        self._attr_unique_id = f"mitsubishi_ilp_ir_control_{host}"
        self._attr_name = "Mitsubishi ILP IR Control"

    @property
    def device_info(self):
        """Return device information to link entity to a device."""
        return {
            "identifiers": {(DOMAIN, self._host)},
            "name": "Mitsubishi ILP IR Control",
            "manufacturer": "@anttitane",
            "model": "Smart AC",
            "sw_version": "1.0",
        }

    @property
    def name(self):
        """Return the name of the climate entity."""
        return "Mitsubishi ILP IR Control"

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

    #
    # FAN MODES
    #
    @property
    def fan_modes(self):
        """Return the list of fan modes to show in the UI."""
        return list(FAN_MODE_DISPLAY_TO_INTERNAL.keys())

    @property
    def fan_mode(self):
        """Return the *display* version of the current fan mode."""
        return FAN_MODE_INTERNAL_TO_DISPLAY.get(self._fan_mode, "Auto")

    async def async_set_fan_mode(self, fan_mode):
        """
        Translate the selected display fan mode (e.g. "Medium")
        back to internal value ("med") for sending to controller.
        """
        internal_fan_mode = FAN_MODE_DISPLAY_TO_INTERNAL.get(fan_mode, "auto")
        self._fan_mode = internal_fan_mode
        await self._async_send_command()

    #
    # SWING MODES (VERTICAL)
    #
    @property
    def swing_modes(self):
        """Return available vertical swing modes (display labels)."""
        return list(SWING_MODE_DISPLAY_TO_INTERNAL.keys())

    @property
    def swing_mode(self):
        """Return the current vertical swing mode in display form."""
        return SWING_MODE_INTERNAL_TO_DISPLAY.get(self._swing_mode, "Auto")

    async def async_set_swing_mode(self, swing_mode):
        """Set the vertical swing mode from display label to internal value."""
        internal_mode = SWING_MODE_DISPLAY_TO_INTERNAL.get(swing_mode, "auto")
        if internal_mode in SWING_MODE_DISPLAY_TO_INTERNAL.values():
            self._swing_mode = internal_mode
            await self._async_send_command()
        else:
            _LOGGER.warning("Invalid swing mode: %s", swing_mode)

    #
    # SWING MODES (HORIZONTAL)
    #
    @property
    def swing_horizontal_modes(self):
        """Return available horizontal swing modes (display labels)."""
        return list(SWING_HORIZ_MODE_DISPLAY_TO_INTERNAL.keys())

    @property
    def swing_horizontal_mode(self):
        """Return the current horizontal swing mode in display form."""
        return SWING_HORIZ_MODE_INTERNAL_TO_DISPLAY.get(self._swing_horizontal_mode, "Not Set")

    async def async_set_swing_horizontal_mode(self, swing_horizontal_mode):
        """Set the horizontal swing mode from display label to internal value."""
        internal_horiz_mode = SWING_HORIZ_MODE_DISPLAY_TO_INTERNAL.get(swing_horizontal_mode, "not_set")
        if internal_horiz_mode in SWING_HORIZ_MODE_DISPLAY_TO_INTERNAL.values():
            self._swing_horizontal_mode = internal_horiz_mode
            await self._async_send_command()
        else:
            _LOGGER.warning("Invalid swing horizontal mode: %s", swing_horizontal_mode)

    #
    # SET TEMPERATURE / HVAC MODE
    #
    async def async_set_temperature(self, **kwargs):
        """Set the target temperature."""
        if ATTR_TEMPERATURE in kwargs:
            self._target_temperature = kwargs[ATTR_TEMPERATURE]
            await self._async_send_command()

    async def async_set_hvac_mode(self, hvac_mode):
        """Set the HVAC mode."""
        if hvac_mode in self.hvac_modes:
            self._hvac_mode = hvac_mode
            await self._async_send_command()
        else:
            _LOGGER.warning("Invalid HVAC mode: %s", hvac_mode)

    #
    # COMMAND SENDER
    #
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
            "vertical_mode": self._swing_mode,
            "horizontal_mode": self._swing_horizontal_mode
        }

        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(url, json=data) as response:
                    response_data = await response.json()
                    _LOGGER.info("Sent command: %s", response_data)
            except aiohttp.ClientError as e:
                _LOGGER.error("Error sending command: %s", e)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    """Set up the Mitsubishi ILP IR Control climate entity."""
    _LOGGER.debug("async_setup_entry called for Mitsubishi ILP IR Control")
    host = entry.data.get("host")
    if not host:
        _LOGGER.error("No host provided for Mitsubishi ILP IR Control entity")
        return

    entity = MitsubishiIlpIrControl(host)
    _LOGGER.debug(f"Adding entity: {entity.name}")
    async_add_entities([entity], True)
