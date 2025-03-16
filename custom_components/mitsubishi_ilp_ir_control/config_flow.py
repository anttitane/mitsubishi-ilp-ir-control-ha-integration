import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult

from .const import DOMAIN

class MitsubishiIlpIrControlConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Mitsubishi ILP IR Control."""

    VERSION = 1

    async def async_step_user(self, user_input=None) -> FlowResult:
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            return self.async_create_entry(title="Mitsubishi ILP IR Control", data=user_input)

        data_schema = vol.Schema(
            {
                vol.Required("host"): str,
            }
        )

        return self.async_show_form(step_id="user", data_schema=data_schema, errors=errors)
