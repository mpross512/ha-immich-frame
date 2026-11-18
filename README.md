# Immich Frame Home Assistant Integration

Home Assistant Integration for [Immich Frame](https://immichframe.dev/)

This Home Assistant integration allows you to locally control an Immich Frame app running on your local network. You must be running the iOS or Android app for this to work; you cannot just be running Immich Frame in the browser on a tablet/mobile device.

## Supported Features

- Dim (Turn display off)
- Undim (Turn display on)
- Set Brightness
- Skip Picture
- Pause
- Previous Picture
- Open the app's settings screen
- Hand brightness back to the device's own setting

## Entities

- **Display** (light): on, off and brightness. Its **System brightness** effect hands brightness back to the device's own setting; moving the slider takes it back.
- **Slideshow** (media player): play, pause, next and previous, using the standard media controls.
- **Open settings** (button): opens the app's settings screen on the frame.
- **Reload** (button): makes the frame re-read its settings and reconnect to its server. Only on frames whose app supports it.

> [!WARNING]
> **Breaking change:** the **Next photo**, **Previous photo** and **Pause slideshow** buttons have been removed in favour of the Slideshow entity. Automations that pressed them should call `media_player.media_next_track`, `media_player.media_previous_track` and `media_player.media_pause` or `media_player.media_play` on the Slideshow entity instead. The old button entities are removed automatically on upgrade.

## State Reporting

Newer builds of the Android app expose a `/status` endpoint. When a frame has it, this integration polls it every 30 seconds and:

- shows the display's real on/off state and brightness, rather than assuming them
- marks the frame's entities as unavailable when it stops responding
- shows whether the slideshow is playing or paused, rather than assuming it (native mode only; the app cannot see this in WebView mode)
- shows the current photo's location and date on the Slideshow entity
- adds **Screen on** and **Playing video** binary sensors
- adds an **Uptime** diagnostic sensor, which drops back to zero when the app restarts

Frames without `/status` keep working exactly as before, with assumed state and no extra sensors. If a frame gains `/status` through an app update, reload the integration to pick up the new sensors.

> [!NOTE]
> `/status` is not in a released version of the app yet. It is proposed in [ImmichFrame_Android#75](https://github.com/immichFrame/ImmichFrame_Android/pull/75).

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
