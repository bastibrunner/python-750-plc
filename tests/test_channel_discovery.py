"""Test the Controller."""

# pylint: disable=protected-access,redefined-outer-name,unused-argument
import logging
import re

from wg750xxx.settings import ChannelConfig, HubConfig, ModuleConfig
from wg750xxx.wg750xxx import PLCHub

from .mock.mock_modbus_tcp_client import MockModbusTcpClient

logger = logging.getLogger(__name__)

# Using fixtures from conftest.py


def test_channel_config_without_config(
    modbus_mock_with_modules: MockModbusTcpClient,
) -> None:
    """Test channel config without config."""
    hub = PLCHub(HubConfig(host="dummy", port=502), initialize=True)
    assert len(hub.modules[0].channels) == 0, "Should have 0 channels"
    assert len(hub.modules[1].channels) == 4, "Should have 4 channels"
    expected_channel_names = re.compile(r"(\w+ )+\d+")
    expected_channel_types = re.compile(r"(\w+ )+")
    expected_channel_ids = re.compile(r"\d+_.\w+_\d+_\w+")
    for module in hub.modules:
        for channel in module.channels:
            assert expected_channel_names.match(channel.name), (
                f"Channels name {channel.name} doesn't match expected pattern {expected_channel_names.pattern}"
            )
            assert expected_channel_types.match(channel.channel_type), (
                f"Channels type {channel.channel_type} doesn't match expected pattern {expected_channel_types.pattern}"
            )
            assert expected_channel_ids.match(channel.config.id), (
                f"Channels id {channel.config.id} doesn't match expected pattern {expected_channel_ids.pattern}"
            )


def test_channel_config_with_matching_config(
    modbus_mock_with_modules: MockModbusTcpClient,
) -> None:
    """Test module config with mismatching config."""
    hub = PLCHub(HubConfig(host="dummy", port=502), initialize=True)
    modules_config = []
    for i, module in enumerate(hub.modules):
        channels_config = []
        for j, channel in enumerate(module.channels):
            channels_config.append(
                ChannelConfig(
                    name=f"Test Channel {j}",
                    type=channel.channel_type,
                    index=j,
                    update_interval=4321,
                    device_class="Test Device Class",
                    unit_of_measurement="Test Unit of Measurement",
                    icon="Test Icon",
                    value_template="Test Value Template",
                    platform="Test Platform",
                )
            )
        modules_config.append(
            ModuleConfig(
                name=f"test_module_{module.index}",
                type=module.config.type,
                index=i,
                update_interval=1234,
                channels=channels_config,
            )
        )

    hub.config = HubConfig(host="dummy", port=502, modules=modules_config)
    for i, module in enumerate(hub.modules):
        # assert module.config.update_interval == 1234, f"Module {i} should have update interval 1234"
        assert module.config.index == i, f"Module {i} should have index {i}"
        assert module.config.name == f"test_module_{module.index}", (
            f"Module {i} should have name test_module_{module.index}"
        )
        assert len(module.channels) > 0, f"Module {i} should have channels"
        for j, channel in enumerate(module.channels):
            assert channel.name == f"Test Channel {j}", (
                f"Channel {j} should have name Test Channel {j}"
            )
            assert channel.config.update_interval == 4321, (
                f"Channel {j} should have update interval 4321"
            )
            assert channel.config.module_id == f"test_module_{module.index}", (
                f"Channel {j} should have module id test_module_{module.index}"
            )
            assert channel.config.device_class == "Test Device Class", (
                f"Channel {j} should have device class Test Device Class"
            )
            assert channel.config.unit_of_measurement == "Test Unit of Measurement", (
                f"Channel {j} should have unit of measurement Test Unit of Measurement"
            )
            assert channel.config.icon == "Test Icon", (
                f"Channel {j} should have icon Test Icon"
            )
            assert channel.config.value_template == "Test Value Template", (
                f"Channel {j} should have value template Test Value Template"
            )
            assert channel.config.platform == "Test Platform", (
                f"Channel {j} should have platform Test Platform"
            )

    hub = PLCHub(
        HubConfig(host="dummy", port=502, modules=modules_config), initialize=True
    )

    assert len(hub.modules[0].channels) == 0, "Should have 4 channels"
    assert len(hub.modules[1].channels) == 4, "Should have 4 channels"
    assert hub.modules[1].channels[0].name == "Test Channel 0", (
        "Should have name Test Channel 0"
    )
    assert hub.modules[1].channels[1].name == "Test Channel 1", (
        "Should have name Test Channel 1"
    )
    assert hub.modules[1].channels[2].name == "Test Channel 2", (
        "Should have name Test Channel 2"
    )
    assert hub.modules[1].channels[3].name == "Test Channel 3", (
        "Should have name Test Channel 3"
    )
    assert hub.modules[1].channels[0].channel_type == "Int16 Out", (
        "Should have type Int16 Out"
    )
    assert hub.modules[1].channels[1].channel_type == "Int16 Out", (
        "Should have type Int16 Out"
    )
    assert hub.modules[1].channels[2].channel_type == "Int16 Out", (
        "Should have type Int16 Out"
    )
    assert hub.modules[1].channels[3].channel_type == "Int16 Out", (
        "Should have type Int16 Out"
    )
    assert hub.modules[1].channels[0].config.id == "1_559_0_int16_out", (
        "Should have id 1_559_0_int16_out"
    )
    assert hub.modules[1].channels[1].config.id == "1_559_1_int16_out", (
        "Should have id 1_559_1_int16_out"
    )
    assert hub.modules[1].channels[2].config.id == "1_559_2_int16_out", (
        "Should have id 1_559_2_int16_out"
    )
    assert hub.modules[1].channels[3].config.id == "1_559_3_int16_out", (
        "Should have id 1_559_3_int16_out"
    )
