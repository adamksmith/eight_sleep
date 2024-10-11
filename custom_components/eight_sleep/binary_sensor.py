"""Support for Eight Sleep binary sensors."""
from __future__ import annotations

from custom_components.eight_sleep.pyEight.user import EightUser

from .pyEight.eight import EightSleep

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from . import EightSleepBaseEntity, EightSleepConfigEntryData
from .const import DOMAIN

BED_PRESENCE_DESCRIPTION = BinarySensorEntityDescription(
    key="bed_presence",
    name="Bed Presence",
    device_class=BinarySensorDeviceClass.OCCUPANCY,
)

SNORE_MITIGATION_DESCRIPTION = BinarySensorEntityDescription(
    key="snore_mitigation",
    name="Snore Mitigaton",
    icon="mdi:account-alert",
    device_class=BinarySensorDeviceClass.RUNNING,
)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the eight sleep binary sensor."""
    config_entry_data: EightSleepConfigEntryData = hass.data[DOMAIN][entry.entry_id]
    eight = config_entry_data.api

    entities: list[BinarySensorEntity] = []

    for user in eight.users.values():
        entities.append(EightBinaryEntity(
            entry,
            config_entry_data.heat_coordinator,
            eight,
            user,
            BED_PRESENCE_DESCRIPTION,
            lambda: user.bed_presence))

        if eight.has_base:
            entities.append(EightBinaryEntity(
                entry,
                config_entry_data.user_coordinator,
                eight,
                user,
                SNORE_MITIGATION_DESCRIPTION,
                lambda: user.in_snore_mitigation))

    async_add_entities(entities)


class EightBinaryEntity(EightSleepBaseEntity, BinarySensorEntity):
    """Representation of an Eight Sleep binary entity."""

    def __init__(
        self,
        entry: ConfigEntry,
        coordinator: DataUpdateCoordinator,
        eight: EightSleep,
        user: EightUser | None,
        entity_description: BinarySensorEntityDescription,
        value_getter: callable
    ) -> None:
        super().__init__(entry, coordinator, eight, user, entity_description.key)
        self.entity_description = entity_description
        self._value_getter = value_getter

    @property
    def is_on(self) -> bool | None:
        return self._value_getter()
