"""Media player platform for Immich Frame."""

from __future__ import annotations

from homeassistant.components.media_player import (
    MediaPlayerEntity,
    MediaPlayerEntityFeature,
    MediaPlayerState,
    MediaType,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .coordinator import ImmichFrameCoordinator
from .entity import ImmichFrameEntity, get_coordinator


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Immich Frame slideshow entity."""
    async_add_entities([ImmichFrameSlideshow(get_coordinator(hass, config_entry), config_entry)])


class ImmichFrameSlideshow(ImmichFrameEntity, MediaPlayerEntity):
    """
    The frame's slideshow, as a media player.

    This gives play, pause, next and previous the standard media controls. Newer builds of
    the app can be told to play or pause outright. Older ones only have a pause toggle, so
    for those play and pause are sent only when they would change something.
    """

    _attr_supported_features = (
        MediaPlayerEntityFeature.NEXT_TRACK
        | MediaPlayerEntityFeature.PAUSE
        | MediaPlayerEntityFeature.PLAY
        | MediaPlayerEntityFeature.PREVIOUS_TRACK
    )

    def __init__(self, coordinator: ImmichFrameCoordinator, config_entry: ConfigEntry) -> None:
        super().__init__(
            coordinator=coordinator,
            config_entry=config_entry,
            name="Slideshow",
            key="slideshow",
        )
        self._assumed_paused = False
        # Set after a toggle and shown until the frame's next report confirms it
        self._pending_paused: bool | None = None

    @callback
    def _handle_coordinator_update(self) -> None:
        self._pending_paused = None
        super()._handle_coordinator_update()

    @property
    def _reported_paused(self) -> bool | None:
        """Return the frame's own paused flag, or None when it does not report one."""
        status = self.status
        if not status:
            return None
        paused = status.get("paused")
        return paused if isinstance(paused, bool) else None

    @property
    def _has_explicit_commands(self) -> bool:
        """Return whether this frame can be told to play or pause outright."""
        # The explicit commands arrived in the same build of the app as the media report.
        # They do not apply in WebView mode, where the frame reports no paused flag.
        status = self.status
        return bool(status) and "media" in status and self._reported_paused is not None

    @property
    def _media(self) -> list[dict[str, object]]:
        """Return what is on screen: two photos when the frame has split its view."""
        status = self.status
        media = status.get("media") if status else None
        if not isinstance(media, list):
            return []
        return [item for item in media if isinstance(item, dict)]

    @property
    def media_content_type(self) -> MediaType | None:
        media = self._media
        if not media:
            return None
        return MediaType.VIDEO if media[0].get("type") == "video" else MediaType.IMAGE

    @property
    def media_content_id(self) -> str | None:
        """
        Return an identifier that changes whenever the picture does.

        A video gives its Immich asset id. A photo gives a fingerprint of its content,
        since the frame's server does not tell it the photo's asset id.
        """
        ids = [item.get("id") or item.get("fingerprint") for item in self._media]
        return ",".join(value for value in ids if isinstance(value, str)) or None

    @property
    def media_title(self) -> str | None:
        """Return each photo's location and date, as the frame itself shows them."""
        titles = []
        for item in self._media:
            parts = [item.get("location"), item.get("date")]
            title = " - ".join(part for part in parts if isinstance(part, str) and part)
            if title:
                titles.append(title)
        return " | ".join(titles) or None

    @property
    def assumed_state(self) -> bool:
        return self._reported_paused is None

    @property
    def state(self) -> MediaPlayerState:
        status = self.status
        if status and status.get("active") is False:
            return MediaPlayerState.OFF

        paused = self._pending_paused
        if paused is None:
            paused = self._reported_paused
        if paused is None:
            paused = self._assumed_paused
        return MediaPlayerState.PAUSED if paused else MediaPlayerState.PLAYING

    async def _async_set_paused(self, paused: bool) -> None:
        state = self.state
        if state == MediaPlayerState.OFF:
            # A frame that is off must not have its slideshow started in the dark
            return

        if self._has_explicit_commands:
            if paused:
                await self._async_send_command("pause", "value=true")
            else:
                await self._async_send_command("play")
        elif (state == MediaPlayerState.PAUSED) != paused:
            # Only a toggle to work with, so send it only if it would change something
            await self._async_send_command("pause")
        else:
            return

        self._assumed_paused = paused
        self._pending_paused = paused
        self.async_write_ha_state()

    async def async_media_play(self) -> None:
        """Resume the slideshow."""
        await self._async_set_paused(False)

    async def async_media_pause(self) -> None:
        """Pause the slideshow."""
        await self._async_set_paused(True)

    async def async_media_next_track(self) -> None:
        """Show the next photo."""
        await self._async_send_command("next")

    async def async_media_previous_track(self) -> None:
        """Show the previous photo."""
        await self._async_send_command("previous")
