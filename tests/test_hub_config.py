"""Test the Hub configuration functionality."""

# pylint: disable=protected-access,redefined-outer-name
import pytest

from wg750xxx.settings import HubConfig, ModuleConfig
from wg750xxx.wg750xxx import PLCHub

# ruff: noqa: SLF001


def test_hub_accepts_only_hubconfig():
    """Test that Hub only accepts HubConfig as parameter."""
    # Valid configuration should work fine
    hub_config = HubConfig(host="test_host", port=1234)
    hub = PLCHub(hub_config, initialize=False)
    assert hub._modbus_host == "test_host"
    assert hub._modbus_port == 1234
    assert hub._init_config == []

    # Test with modules included
    module_config = ModuleConfig(name="test_module", type="test_type", index=0)
    hub_config_with_modules = HubConfig(
        host="test_host", port=1234, modules=[module_config]
    )
    hub = PLCHub(hub_config_with_modules, initialize=False)
    assert hub._init_config == [module_config]


def test_hub_config_getter():
    """Test the config property returns the correct HubConfig without modules_dict."""
    hub_config = HubConfig(host="test_host", port=1234)
    hub = PLCHub(hub_config, initialize=False)

    # Add a module to the hub
    module_config = ModuleConfig(name="test_module", type="test_type", index=0)
    hub._init_config = [module_config]

    # Get the config
    config = hub.config

    # Verify the config
    assert config.host == "test_host"
    assert config.port == 1234
    assert len(config.modules) == 0  # No modules since we didn't initialize the hub


def test_hub_config_setter():
    """Test that the config setter only accepts HubConfig."""
    hub_config = HubConfig(host="test_host", port=1234)
    hub = PLCHub(hub_config, initialize=False)

    # Update with a new HubConfig
    new_config = HubConfig(
        host="new_host",
        port=5678,
        modules=[ModuleConfig(name="new_module", type="new_type", index=0)],
    )
    hub.config = new_config

    # Verify the config was updated
    assert hub._modbus_host == "new_host"
    assert hub._modbus_port == 5678
    assert len(hub._init_config) == 1
    assert hub._init_config[0].name == "new_module"

    # Test with invalid config
    with pytest.raises(TypeError):
        hub.config = "invalid_config"
