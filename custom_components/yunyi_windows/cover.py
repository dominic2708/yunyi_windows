from functools import partial
import logging

import voluptuous as vol

import homeassistant.helpers.config_validation as cv
from homeassistant.components.cover import (CoverEntity, PLATFORM_SCHEMA, )
from homeassistant.const import (CONF_NAME, CONF_HOST, CONF_TOKEN, )
from homeassistant.exceptions import PlatformNotReady
from datetime import timedelta

_LOGGER = logging.getLogger(__name__)

DEFAULT_NAME = 'Xiaomi Miio Device'
DATA_KEY = 'cover.yunyi_windows'


CONF_UPDATE_INSTANT = 'update_instant'

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
    vol.Required(CONF_HOST): cv.string,
    vol.Required(CONF_TOKEN): vol.All(cv.string, vol.Length(min=32, max=32)),
    vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
    vol.Optional(CONF_UPDATE_INSTANT, default=True): cv.boolean,
    },
    extra=vol.ALLOW_EXTRA,
)

REQUIREMENTS = ['python-miio>=0.4.5']

ATTR_MODEL = 'model'
ATTR_FIRMWARE_VERSION = 'firmware_version'
ATTR_HARDWARE_VERSION = 'hardware_version'

SUCCESS = ['ok']

SCAN_INTERVAL = timedelta(seconds=15)


def async_setup_platform(hass, config, async_add_devices, discovery_info=None):
    """Set up the sensor from config."""
    from miio import Device, DeviceException
    if DATA_KEY not in hass.data:
        hass.data[DATA_KEY] = {}

    host = config.get(CONF_HOST)
    token = config.get(CONF_TOKEN)

    _LOGGER.info("Initializing with host %s (token %s...)", host, token[:5])

    try:
        miio_device = Device(host, token)
        device_info = miio_device.info()
        model = device_info.model
        _LOGGER.info("%s %s %s detected",
                     model,
                     device_info.firmware_version,
                     device_info.hardware_version)

        device = YunyiCover(miio_device, config, device_info)
    except DeviceException:
        raise PlatformNotReady

    hass.data[DATA_KEY][host] = device
    async_add_devices([device], update_before_add=True)


class YunyiCover(CoverEntity):

    def __init__(self, device, config, device_info):
        """Initialize the entity."""
        self._device = device

        self._name = config.get(CONF_NAME)

        self._unique_id = "{}-{}".format(device_info.model, device_info.mac_address)
        self._model = device_info.model
        self._available = None
        self._update_instant = config.get(CONF_UPDATE_INSTANT)
        self._skip_update = False

        self._is_closed = False
        self._current_cover_position = 100
        self._current_cover_tilt_position = 100
        self._state_attrs = {
            ATTR_MODEL: self._model,
            ATTR_FIRMWARE_VERSION: device_info.firmware_version,
            ATTR_HARDWARE_VERSION: device_info.hardware_version
        }

    @property
    def should_poll(self):
        """Poll the miio device."""
        return True

    @property
    def name(self):
        """Return the name of this entity, if any."""
        return self._name

    @property
    def unique_id(self):
        """Return an unique ID."""
        return self._unique_id

    @property
    def available(self):
        """Return true when state is known."""
        return self._available

    @property
    def is_closed(self):
        return self._is_closed

    @property
    def current_cover_position(self):
        """Return the current position of the cover."""
        return self._current_cover_position

    @property
    def current_cover_tilt_position(self):
        """Return the current position of the cover."""
        return self._current_cover_tilt_position

    @property
    def device_state_attributes(self):
        """Return the state attributes of the device."""
        return self._state_attrs

    async def async_update(self):
        """Fetch state from the device."""
        from miio import DeviceException

        # On state change some devices doesn't provide the new state immediately.
        if self._update_instant is False and self._skip_update:
            self._skip_update = False
            return

        try:
            cover_info = self._device.send('get_prop', 'progress,child_lock')
            try:
                cover_info[1]
            except:
                return

            current_cover_position = cover_info[0]
            current_cover_tilt_position = self.tilt_closed(cover_info[1])
            
            self._is_closed = self.closed(current_cover_position)

            self._current_cover_position = current_cover_position
            self._current_cover_tilt_position = current_cover_tilt_position 
            self._available = True
            self._state_attrs.update({
                "current_position": current_cover_position,
                "current_tilt_position": current_cover_tilt_position
            })

        except DeviceException as ex:
            self._available = False
            _LOGGER.error("Got exception while fetching the state: %s", ex)

    def closed(self, current_cover_position):
        if current_cover_position == 0:
            return True
        else:
            return False

    def tilt_closed(self, current_cover_tilt_position):
        if current_cover_tilt_position == 0:
            return 0
        else:
            return 100

    async def _try_command(self, mask_error, func, *args, **kwargs):
        """Call a device command handling error messages."""
        from miio import DeviceException
        try:
            result = await self.hass.async_add_job(
                partial(func, *args, **kwargs))

            _LOGGER.info("Response received from miio device: %s", result)

            return result == SUCCESS
        except DeviceException as exc:
            _LOGGER.error(mask_error, exc)
            return False

    async def async_stop_cover(self, **kwargs):
        result = await self._try_command(
            "Turning the miio device on failed.", self._device.send,
            'setStatus', [0])

    async def async_open_cover(self, **kwargs):
        result = await self._try_command(
            "Turning the miio device on failed.", self._device.send,
            'setStatus', [1])

    async def async_close_cover(self, **kwargs):
        result = await self._try_command(
            "Turning the miio device on failed.", self._device.send,
            'setStatus', [2])

    async def async_set_cover_position(self, **kwargs):
        position = kwargs.get('position')
        result = await self._try_command(
            "Turning the miio device on failed.", self._device.send,
            'setProgress', [position])

    async def async_open_cover_tilt(self, **kwargs):
        result = await self._try_command(
            "Turning the miio device on failed.", self._device.send,
            'setChildLock', [1])

    async def async_close_cover_tilt(self, **kwargs):
        result = await self._try_command(
            "Turning the miio device on failed.", self._device.send,
            'setChildLock', [0])
