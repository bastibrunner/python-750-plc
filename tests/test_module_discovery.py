"""Test the Controller."""

# pylint: disable=protected-access,redefined-outer-name,unused-argument
import logging

import pytest

from wg750xxx.modules.exceptions import WagoModuleError
from wg750xxx.settings import HubConfig, ModuleConfig
from wg750xxx.wg750xxx import PLCHub

from .mock.mock_modbus_tcp_client import MockModbusTcpClient

logger = logging.getLogger(__name__)

# Using fixtures from conftest.py


def test_module_config_with_no_modules(modbus_mock: MockModbusTcpClient) -> None:
    """Test module config with no config and initialize false."""
    hub = PLCHub(HubConfig(host="dummy", port=502), initialize=False)
    assert hub.config.modules == [], "Config should be empty"
    hub.initialize()
    hub.run_discovery()
    assert len(hub.modules) == 0, "Should have 0 modules"


def test_module_config_with_no_config_and_initialize_false(
    modbus_mock_with_modules: MockModbusTcpClient,
) -> None:
    """Test module config with no config and initialize false."""
    hub = PLCHub(HubConfig(host="dummy", port=502), initialize=False)
    assert hub.config.modules == [], "Config should be empty"
    hub.initialize(discovery=False)
    assert len(hub.modules) == 0, (
        "Should have 0 modules after initialization with discovery false"
    )
    hub.run_discovery()
    assert len(hub.modules) == 13, "Should have 13 modules after discovery"


def test_module_config_with_no_config_and_initialize_true(
    modbus_mock_with_modules: MockModbusTcpClient,
) -> None:
    """Test module config with no config and initialize true."""
    hub = PLCHub(HubConfig(host="dummy", port=502), initialize=True)
    assert len(hub.modules) == 13, "Should have 13 modules"
    assert len(hub.config.modules) == 13, "Config should have 13 modules"


def test_module_config_with_matching_config(
    modbus_mock_with_modules: MockModbusTcpClient,
) -> None:
    """Test module config with mismatching config."""
    modules_config = [
        ModuleConfig(
            name="test_module_1", type="352", index=0, update_interval=100, channels=[]
        ),
        ModuleConfig(
            name="test_module_2", type="559", index=1, update_interval=101, channels=[]
        ),
        ModuleConfig(
            name="test_module_3", type="559", index=2, update_interval=102, channels=[]
        ),
        ModuleConfig(
            name="test_module_4", type="DO", index=3, update_interval=103, channels=[]
        ),
        ModuleConfig(
            name="test_module_5", type="DO", index=4, update_interval=104, channels=[]
        ),
        ModuleConfig(
            name="test_module_6", type="DI", index=5, update_interval=105, channels=[]
        ),
        ModuleConfig(
            name="test_module_7", type="DI", index=6, update_interval=106, channels=[]
        ),
        ModuleConfig(
            name="test_module_8", type="459", index=7, update_interval=107, channels=[]
        ),
        ModuleConfig(
            name="test_module_9", type="453", index=8, update_interval=108, channels=[]
        ),
        ModuleConfig(
            name="test_module_10", type="460", index=9, update_interval=109, channels=[]
        ),
        ModuleConfig(
            name="test_module_11",
            type="451",
            index=10,
            update_interval=110,
            channels=[],
        ),
        ModuleConfig(
            name="test_module_12",
            type="404",
            index=11,
            update_interval=111,
            channels=[],
        ),
        ModuleConfig(
            name="test_module_13", type="DI", index=12, update_interval=112, channels=[]
        ),
    ]
    hub = PLCHub(
        HubConfig(host="dummy", port=502, modules=modules_config), initialize=True
    )
    assert len(hub.modules) == 13, "Should have 13 modules"
    assert len(hub.config.modules) == 13, "Config should have 13 modules"
    assert hub.modules[0].name == "test_module_1", (
        "Module 1 should have name test_module_1"
    )
    assert hub.modules[0].index == 0, "Module 1 should have index 0"
    assert hub.modules[0].config.update_interval == 100, (
        "Module 1 should have polling interval 100"
    )
    assert hub.modules[1].name == "test_module_2", (
        "Module 2 should have name test_module_2"
    )
    assert hub.modules[1].index == 1, "Module 2 should have index 1"
    assert hub.modules[1].config.update_interval == 101, (
        "Module 2 should have polling interval 101"
    )
    assert hub.modules[2].name == "test_module_3", (
        "Module 3 should have name test_module_3"
    )
    assert hub.modules[2].index == 2, "Module 3 should have index 2"
    assert hub.modules[3].name == "test_module_4", (
        "Module 4 should have name test_module_4"
    )
    assert hub.modules[3].index == 3, "Module 4 should have index 3"
    assert hub.modules[3].config.update_interval == 103, (
        "Module 4 should have polling interval 103"
    )
    assert hub.modules[4].name == "test_module_5", (
        "Module 5 should have name test_module_5"
    )
    assert hub.modules[4].index == 4, "Module 5 should have index 4"
    assert hub.modules[5].name == "test_module_6", (
        "Module 6 should have name test_module_6"
    )
    assert hub.modules[5].index == 5, "Module 6 should have index 5"
    assert hub.modules[5].config.update_interval == 105, (
        "Module 6 should have polling interval 105"
    )
    assert hub.modules[6].name == "test_module_7", (
        "Module 7 should have name test_module_7"
    )
    assert hub.modules[6].index == 6, "Module 7 should have index 6"
    assert hub.modules[7].name == "test_module_8", (
        "Module 8 should have name test_module_8"
    )
    assert hub.modules[7].index == 7, "Module 8 should have index 7"
    assert hub.modules[7].config.update_interval == 107, (
        "Module 8 should have polling interval 107"
    )
    assert hub.modules[8].name == "test_module_9", (
        "Module 9 should have name test_module_9"
    )
    assert hub.modules[8].index == 8, "Module 9 should have index 8"
    assert hub.modules[8].config.update_interval == 108, (
        "Module 9 should have polling interval 108"
    )
    assert hub.modules[9].name == "test_module_10", (
        "Module 10 should have name test_module_10"
    )
    assert hub.modules[9].index == 9, "Module 10 should have index 9"
    assert hub.modules[9].config.update_interval == 109, (
        "Module 10 should have polling interval 109"
    )
    assert hub.modules[10].name == "test_module_11", (
        "Module 11 should have name test_module_11"
    )
    assert hub.modules[10].index == 10, "Module 11 should have index 10"
    assert hub.modules[10].config.update_interval == 110, (
        "Module 11 should have polling interval 110"
    )
    assert hub.modules[11].name == "test_module_12", (
        "Module 12 should have name test_module_12"
    )
    assert hub.modules[11].index == 11, "Module 12 should have index 10"
    assert hub.modules[11].config.update_interval == 111, (
        "Module 12 should have polling interval 111"
    )
    assert hub.modules[12].name == "test_module_13", (
        "Module 13 should have name test_module_13"
    )
    assert hub.modules[12].index == 12, "Module 13 should have index 11"
    assert hub.modules[12].config.update_interval == 112, (
        "Module 13 should have polling interval 112"
    )


def test_module_config_with_mismatching_config_typemismatch(
    modbus_mock_with_modules: MockModbusTcpClient,
) -> None:
    """Test module config with mismatching config."""
    modules_config = [
        ModuleConfig(name="test_module_1", type="wrong_type"),
        ModuleConfig(name="test_module_2", type="wrong_type"),
        ModuleConfig(name="test_module_3", type="wrong_type"),
        ModuleConfig(name="test_module_4", type="wrong_type"),
        ModuleConfig(name="test_module_5", type="wrong_type"),
        ModuleConfig(name="test_module_6", type="wrong_type"),
        ModuleConfig(name="test_module_7", type="wrong_type"),
        ModuleConfig(name="test_module_8", type="wrong_type"),
        ModuleConfig(name="test_module_9", type="wrong_type"),
        ModuleConfig(name="test_module_10", type="wrong_type"),
        ModuleConfig(name="test_module_11", type="wrong_type"),
        ModuleConfig(name="test_module_12", type="wrong_type"),
        ModuleConfig(name="test_module_13", type="wrong_type"),
    ]
    with pytest.raises(WagoModuleError):
        _hub = PLCHub(
            HubConfig(host="dummy", port=502, modules=modules_config), initialize=True
        )


def test_module_config_with_mismatching_config_indexmismatch(
    modbus_mock_with_modules: MockModbusTcpClient,
) -> None:
    """Test module config with mismatching config."""
    modules_config = [
        ModuleConfig(
            name="test_module_1", type="352", index=12, update_interval=100, channels=[]
        ),
        ModuleConfig(
            name="test_module_2", type="559", index=11, update_interval=101, channels=[]
        ),
        ModuleConfig(
            name="test_module_3", type="559", index=10, update_interval=102, channels=[]
        ),
        ModuleConfig(
            name="test_module_4", type="DO", index=9, update_interval=103, channels=[]
        ),
        ModuleConfig(
            name="test_module_5", type="DO", index=8, update_interval=104, channels=[]
        ),
        ModuleConfig(
            name="test_module_6", type="DI", index=7, update_interval=105, channels=[]
        ),
        ModuleConfig(
            name="test_module_7", type="DI", index=6, update_interval=106, channels=[]
        ),
        ModuleConfig(
            name="test_module_8", type="459", index=5, update_interval=107, channels=[]
        ),
        ModuleConfig(
            name="test_module_9", type="453", index=4, update_interval=108, channels=[]
        ),
        ModuleConfig(
            name="test_module_10", type="460", index=3, update_interval=109, channels=[]
        ),
        ModuleConfig(
            name="test_module_11", type="451", index=2, update_interval=110, channels=[]
        ),
        ModuleConfig(
            name="test_module_12", type="404", index=1, update_interval=111, channels=[]
        ),
        ModuleConfig(
            name="test_module_13", type="DI", index=0, update_interval=112, channels=[]
        ),
    ]
    with pytest.raises(ValueError):
        _hub = PLCHub(
            HubConfig(host="dummy", port=502, modules=modules_config), initialize=True
        )


def test_module_config_with_mismatching_config_too_short(
    modbus_mock_with_modules: MockModbusTcpClient,
) -> None:
    """Test module config with mismatching config."""
    modules_config = [
        ModuleConfig(
            name="test_module_1", type="352", index=0, update_interval=100, channels=[]
        ),
        ModuleConfig(
            name="test_module_2", type="559", index=1, update_interval=101, channels=[]
        ),
        ModuleConfig(
            name="test_module_3", type="559", index=2, update_interval=102, channels=[]
        ),
        ModuleConfig(
            name="test_module_4", type="DO", index=3, update_interval=103, channels=[]
        ),
    ]
    hub = PLCHub(
        HubConfig(host="dummy", port=502, modules=modules_config), initialize=True
    )
    assert len(hub.modules) == 13, "Should have 13 modules"
    assert hub.modules[0].name == "test_module_1", (
        "Module 1 should have name test_module_1"
    )
    assert hub.modules[1].name == "test_module_2", (
        "Module 2 should have name test_module_2"
    )
    assert hub.modules[2].name == "test_module_3", (
        "Module 3 should have name test_module_3"
    )
    assert hub.modules[3].name == "test_module_4", (
        "Module 4 should have name test_module_4"
    )
    assert hub.modules[4].name == "DO", "Module 5 should have name DO"
    assert hub.modules[5].name == "DI", "Module 6 should have name DI"
    assert hub.modules[6].name == "DI", "Module 7 should have name DI"
    assert hub.modules[7].name == "460", "Module 8 should have name DI"
    assert hub.modules[8].name == "460", "Module 9 should have name 459"
    assert hub.modules[9].name == "460", "Module 10 should have name 453"
    assert hub.modules[10].name == "451", "Module 11 should have name 451"
    assert hub.modules[11].name == "404", "Module 12 should have name 404"
    assert hub.modules[12].name == "DI", "Module 13 should have name DI"


def test_module_config_with_mismatching_config_too_long(
    modbus_mock_with_modules: MockModbusTcpClient,
) -> None:
    """Test module config with mismatching config."""
    modules_config = [
        ModuleConfig(
            name="test_module_1", type="352", index=0, update_interval=100, channels=[]
        ),
        ModuleConfig(
            name="test_module_2", type="559", index=1, update_interval=101, channels=[]
        ),
        ModuleConfig(
            name="test_module_3", type="559", index=2, update_interval=102, channels=[]
        ),
        ModuleConfig(
            name="test_module_4", type="DO", index=3, update_interval=103, channels=[]
        ),
        ModuleConfig(
            name="test_module_5", type="DO", index=4, update_interval=104, channels=[]
        ),
        ModuleConfig(
            name="test_module_6", type="DI", index=5, update_interval=105, channels=[]
        ),
        ModuleConfig(
            name="test_module_7", type="DI", index=6, update_interval=106, channels=[]
        ),
        ModuleConfig(
            name="test_module_8", type="459", index=7, update_interval=107, channels=[]
        ),
        ModuleConfig(
            name="test_module_9", type="453", index=8, update_interval=108, channels=[]
        ),
        ModuleConfig(
            name="test_module_10", type="460", index=9, update_interval=109, channels=[]
        ),
        ModuleConfig(
            name="test_module_11",
            type="451",
            index=10,
            update_interval=110,
            channels=[],
        ),
        ModuleConfig(
            name="test_module_12",
            type="404",
            index=11,
            update_interval=111,
            channels=[],
        ),
        ModuleConfig(
            name="test_module_13", type="DI", index=12, update_interval=112, channels=[]
        ),
        ModuleConfig(
            name="test_module_14", type="DI", index=13, update_interval=113, channels=[]
        ),
    ]
    hub = PLCHub(
        HubConfig(host="dummy", port=502, modules=modules_config), initialize=True
    )
    assert len(hub.modules) == 13, "Should have 13 modules"
    assert hub.modules[0].name == "test_module_1", (
        "Module 1 should have name test_module_1"
    )
    assert hub.modules[1].name == "test_module_2", (
        "Module 2 should have name test_module_2"
    )
    assert hub.modules[2].name == "test_module_3", (
        "Module 3 should have name test_module_3"
    )
    assert hub.modules[3].name == "test_module_4", (
        "Module 4 should have name test_module_4"
    )
    assert hub.modules[4].name == "test_module_5", (
        "Module 5 should have name test_module_5"
    )
    assert hub.modules[5].name == "test_module_6", (
        "Module 6 should have name test_module_6"
    )
    assert hub.modules[6].name == "test_module_7", (
        "Module 7 should have name test_module_7"
    )
    assert hub.modules[7].name == "test_module_8", (
        "Module 8 should have name test_module_8"
    )
    assert hub.modules[8].name == "test_module_9", (
        "Module 9 should have name test_module_9"
    )
    assert hub.modules[9].name == "test_module_10", (
        "Module 10 should have name test_module_10"
    )
    assert hub.modules[10].name == "test_module_11", (
        "Module 11 should have name test_module_11"
    )
    assert hub.modules[11].name == "test_module_12", (
        "Module 12 should have name test_module_12"
    )
    assert hub.modules[12].name == "test_module_13", (
        "Module 13 should have name test_module_13"
    )
