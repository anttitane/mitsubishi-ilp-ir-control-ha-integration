# 🌡️ Mitsubishi ILP IR Control Home Assistant Integration

This repository contains a Home Assistant integration to control Mitsubishi air conditioners via Infrared using a Raspberry Pi. The integration communicates with a separate IR control server hosted on a Raspberry Pi.

## 📖 Overview

The **Mitsubishi ILP IR Control** integration provides a convenient way to control your Mitsubishi air pump unit using Home Assistant's familiar interface. It supports basic functionalities such as:

- Power control (On/Off)
- Temperature setting
- HVAC mode (Heating/Cooling)
- Fan speed control
- Vertical and Horizontal swing modes

## 📦 Components

The integration consists of:
- `climate.py`: Implements the Climate entity in Home Assistant, enabling control over temperature, fan modes, and swing modes.
- `config_flow.py`: Provides a user-friendly configuration flow in the Home Assistant UI.
- `manifest.json`: Defines metadata and integration details for Home Assistant.
- `const.py`: Contains constant definitions used across the integration.
- `config_flow.py`: Enables configuration through Home Assistant UI with dynamic forms.
- `en.json`: Localization strings for Home Assistant.

## ⚙️ Dependencies

- The integration relies on a backend IR server running on a separate device (Raspberry Pi Zero W). The backend is available in the [mitsubishi-ilp-ir-control](https://github.com/anttitane/mitsubishi-ilp-ir-control) repository.

## 🚀 Installation

1. Clone or download this repository.
2. Place the folder `mitsubishi_ilp_ir_control` from the repo folder `custom_components` in your Home Assistant `custom_components` directory.
3. Restart Home Assistant.

## 🛠️ Configuration

### Setup via Home Assistant UI

1. In Home Assistant, navigate to `Settings` > `Devices & Services`.
2. Click `+ Add Integration`.
3. Search for `Mitsubishi ILP IR Control` and select it.
4. Enter the IP address of the device running the IR server (Raspberry Pi).

## 📌 Services Provided

| Service                    | Description                            |
|----------------------------|----------------------------------------|
| `set_temperature`           | Sets the target temperature.          |
| `set_fan_mode`              | Sets the fan speed (auto, low, medium, high). |
| `set_swing_mode` | Adjusts the vertical swing mode.        |
| `set_swing_horizontal_mode` | Adjusts the horizontal swing mode.     |

## 🏠 Adding the Climate Entity to Home Assistant Lovelace UI

After installing the custom integration, you can add the `climate.mitsubishi_ilp_ir_control` entity to your Lovelace dashboard. An example configuration snippet (YAML mode) is shown below:

```yaml
- type: thermostat
  entity: climate.mitsubishi_ilp_ir_control
  name: Mitsubishi FD25
  features:
    - type: climate-hvac-modes
      hvac_modes:
        - heat
        - cool
        - "off"
    - type: climate-fan-modes
      fan_modes:
        - Auto
        - Low
        - Medium
        - High
    - type: climate-swing-modes
      swing-modes:
        - auto
        - top
        - middle_top
        - middle
        - middle_bottom
        - bottom
```

## 🧾 Troubleshooting

If issues arise, check the logs from Home Assistant and ensure:
- Your backend IR control server is running properly.
- IP addresses and network configurations are correct.

## 🤝 Contributing

Feel free to submit issues, feature requests, or pull requests.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

