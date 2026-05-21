# Immich Frame Home Assistant Integration

Home Assistant Integration for Immich Frame

This Home Assistant integration allows you to locally control an Immich Frame app running on your local network. You must be running the iOS or Android app for this to work; you cannot just be running Immich Frame in the browser on a tablet/mobile device.

## Supported Features

- Dim (Turn display off)
- Undim (Turn display on)
- Set Brightness
- Skip Picture
- Pause
- Previous Picture

## Installation

### [HACS](https://hacs.xyz) (Recommended)

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=mpross512&repository=ha-immich-frame&category=Integration)

1. Have [HACS](https://github.com/custom-components/hacs) installed, this will allow you to easily update
2. Add `https://github.com/mpross512/ha-immich-frame` as a [custom repository](https://hacs.xyz/docs/faq/custom_repositories) and Type: Integration
3. Click install under "Immich Frame", restart your instance.

### Manual Installation

1. Download this repository as a ZIP (green button, top right) and unzip the archive
2. Copy the `immich_frame` folder inside the `custom_components` folder to the Home Assistant `/<config path>/custom_components/` directory
   - You may need to create the `custom_components` in your Home Assistant installation folder if it does not exist
   - On Home Assistant (formerly Hass.io) and Home Assistant Container the final location should be `/config/custom_components/immich_frane`
   - On Home Assistant Supervised, Home Assistant Core, and Hassbian the final location should be `/home/homeassistant/.homeassistant/custom_components/immich_frame`
3. Restart your instance.

## Support

[!["Buy Me A Coffee"](https://cdn.buymeacoffee.com/buttons/v2/arial-yellow.png)](https://www.buymeacoffee.com/mpross512)
