"""Settings for the Wago 750."""

from pydantic import BaseModel, Field, computed_field
from zlib import crc32

class ChannelConfig(BaseModel):
    """Channel Settings."""

    name: str | None = Field(description="The name of the channel", default=None)
    type: str = Field(description="The type of the channel")
    platform: str | None = Field(
        description="The platform of the channel", default=None
    )
    # mapping: Optional[str] = Field(description='The mapping of the channel', default=None)
    # logic: Optional[list[str]] = Field(description='The logic of the channel', default=None)
    device_class: str | None = Field(
        description="The device class of the channel", default=None
    )
    unit_of_measurement: str | None = Field(
        description="The unit of measurement of the channel", default=None
    )
    icon: str | None = Field(description="The icon of the channel", default=None)
    value_template: str | None = Field(
        description="The value template of the channel", default=None
    )
    index: int | None = Field(description="The index of the channel", default=None)
    module_id: str | None = Field(description="The id of the module", default=None)
    update_interval: int | None = Field(
        description="The update interval of the module in milliseconds", default=100
    )

    @computed_field
    @property
    def id(self) -> str:
        """Generate a unique id for the channel."""

        return f"{self.module_id}_{self.index}_{str(self.type).replace(' ', '_').lower()}"


class ModuleConfig(BaseModel):
    """Connected Modules Settings."""

    name: str = Field(description="The name of the module")
    type: str = Field(description="The type of the module")
    index: int | None = Field(
        description="The index/position of the module", default=None
    )
    update_interval: int = Field(
        description="The update interval of the module in milliseconds", default=100
    )
    channels: list[ChannelConfig] | None = Field(
        description="The channels of the module", default=None
    )

    @computed_field
    @property
    def id(self) -> str:
        """Generate a unique id for the module."""

        return f"{self.index}_{str(self.type).replace(' ', '_').lower()}"


class HubConfig(BaseModel):
    """Hub Settings."""

    host: str = Field(
        description="The hostname or IP address of the Wago Modbus TCP server"
    )
    port: int = Field(description="The port of the Wago Modbus TCP server", default=502)
    modules: list[ModuleConfig] = Field(description="The modules of the hub", default=[])
    update_interval: int = Field(description="The global update interval of the hub in milliseconds", default=100)

class ModbusSettings(BaseModel):
    """Settings for the Modbus server."""

    server: str = Field(
        description="The hostname or IP address of the Wago Modbus TCP server"
    )
    port: int = Field(description="The port of the Wago Modbus TCP server", default=502)
