# WAGO 750 Python Module

This Python module provides an abstraction layer for interacting with WAGO 750 series PLCs through Modbus TCP communication. It offers a clean, object-oriented interface to control and monitor various WAGO PLC modules and their channels.

## Overview

The WAGO 750 series PLC is a modular system where a central PLC Hub communicates with connected modules using Modbus TCP protocol. Each module can have multiple channels and supports different functionalities like digital/analog I/O, temperature sensors, counters, motor controllers, DALI lighting control, and more.

This module provides a high-level abstraction that represents the PLC Hub and its connected modules as Python objects, making it easy to interact with the physical hardware through simple Python code.

## Architecture

### Core Components

- **Hub Class**: The main interface to the PLC system

  - Manages Modbus TCP connection
  - Automatically detects connected modules
  - Handles configuration management
  - Provides access to all connected modules

- **Module Classes**: Abstract representations of physical PLC modules

  - Each module type has its own implementation
  - Inherits from a base module class
  - Handles module-specific Modbus register configurations
  - Manages module state and channels

- **Channel Objects**: Represent individual I/O points within modules
  - Provide read/write access to physical values
  - Support value transformations and validation
  - Enable event-based interactions

### Configuration System

The module uses a YAML-based configuration system to store additional information about modules and their channels:

- Module and channel names
- Value mappings and transformations
- Event handling rules
- Input/output relationships

The configuration can be:

- Read from a YAML file during runtime
- Modified through Python code
- Persisted back to the YAML file
- Validated against actual hardware configuration

## Features

- **Automatic Module Detection**: The Hub automatically identifies connected modules
- **Flexible Configuration**: Support for both minimal and detailed module configurations
- **Smart Module Matching**: Intelligent configuration validation and module matching
- **Value Transformations**: Built-in support for value scaling and mapping
- **Event Handling**: Support for complex input patterns (e.g., button gestures)
- **Direct I/O Mapping**: Configure direct relationships between inputs and outputs
- **Runtime Configuration**: Ability to modify and persist configurations during runtime

## Module Types

The module supports various WAGO module types:

- Digital Input/Output modules
- Analog Input/Output modules
- Temperature sensors (PT100, etc.)
- Impulse counters
- Encoders
- Motor controllers
- DALI lighting control
- Serial communication modules

Each module type implements specific functionality and register mappings.

## Usage Example

Here's a basic example of how to use the module:

```python
from wg750xxx import PlcHub

# Create a hub instance (automatically connects to Modbus)
hub = PlcHub(ip_address="192.168.1.100")

# Access a digital output module by index
light_control = hub.connected_modules[4].channels[1]
light_control.value = 100  # Set light to 100%

# Access modules by type (more robust)
dimmer = hub.modules["AO4"][0].channels[1]
dimmer.value = 50  # Set dimmer to 50%

# Complex module example (DALI)
dali_module = hub.modules["DALI"][0]
dali_module.add_to_group(channel=1, group=1)  # Add light to group 1
dali_module.create_scene(group=1, scene=1)    # Create scene 1
dali_module.set_group_level(group=1, level=80)  # Set group brightness
```

## Advanced Features

### Value Transformations

The module supports various value transformations:

- Scaling analog values
- Mapping digital states to meaningful values
- Temperature unit conversions
- Custom transformation functions

### Event Handling

Support for complex input patterns:

- Button gesture detection (short press, long press, double press)
- Debouncing
- Threshold monitoring
- Custom event definitions

### I/O Mapping

Configure direct relationships between inputs and outputs:

- Button to light control
- Temperature sensor to heating control
- Complex multi-channel relationships
- Conditional mappings

## Configuration Example

```yaml
modules:
  - type: "DI4"
    name: "Wall Switches"
    channels:
      - name: "Living Room Light"
        mapping: Light_Dimmers_Living_Room_Dimmer
        logic:
          - type: "short_press"
            action: "toggle"
          - type: "long_press"
            action: "dim"

  - type: "AO4"
    name: "Light Dimmers"
    channels:
      - name: "Living Room Dimmer"
```

## Error Handling

The module includes robust error handling:

- Connection management
- Configuration validation
- Value range checking
- Module-specific error handling
- Detailed error messages and logging

## Development

### Adding New Module Types

1. Create a new module class inheriting from the base module class
2. Implement module-specific register mappings
3. Add channel management
4. Implement module-specific methods and properties
5. Add configuration validation

### Testing

The module includes a comprehensive test suite:

- Unit tests for each module type
- Integration tests for the hub
- Configuration validation tests
- Error handling tests

## Dependencies

- pymodbus (for Modbus TCP communication)
- pyyaml (for configuration management)
- [Add other dependencies]

## License

[Add license information]

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## API Documentation

### Core Classes

#### Hub

The `Hub` class is the main entry point for interacting with the WAGO 750 PLC system.

```python
from wg750xxx.settings import ModbusSettings, ModuleConfig
from wg750xxx.hub import Hub

# Create ModbusSettings with connection parameters
modbus_settings = ModbusSettings(
    server="192.168.1.100",  # IP address of the WAGO controller
    port=502                 # Default Modbus TCP port
)

# Initialize empty configuration or provide preconfigured modules
module_config = []  # Initialize with empty config for auto-discovery

# Create a hub instance
hub = Hub(
    modbus=modbus_settings,
    config=module_config,
    discovery=True           # Auto-discover connected modules
)
```

##### Hub Properties

- `info`: `ControllerInfo` - Information about the controller (revision, firmware version, etc.)
- `connected_modules`: `list[WagoModule]` - List of all connected modules by position
- `modules`: `dict[str, list[WagoModule]]` - Modules grouped by type name
- `next_address`: `AddressDict` - The next available Modbus address for each register type

##### Hub Methods

- `initialize(discovery: bool = True)`: Initialize the hub connection and module discovery
- `get_digital_modules()`: Returns a list of digital I/O modules
- `get_analog_modules()`: Returns a list of analog I/O modules
- `close()`: Close the Modbus TCP connection
- `reset_modules()`: Reset the module configuration
- `append_module(module: WagoModule)`: Add a module to the hub

#### WagoModule

Base class for all WAGO module types. Specific module implementations inherit from this class.

##### Module Types

- Digital I/O:
  - `Wg750DigitalIn`: For digital input modules (750-4xx series)
  - `Wg750DigitalOut`: For digital output modules (750-5xx series)
- Analog I/O:
  - `Wg750AnalogIn1Ch`, `Wg750AnalogIn2Ch`, `Wg750AnalogIn4Ch`, `Wg750AnalogIn8Ch`: For analog input modules
  - `Wg750AnalogOut2Ch`, `Wg750AnalogOut4Ch`: For analog output modules
- Specialized Modules:
  - `Wg750Counter`: For counter modules (750-404)
  - `Wg750DaliMaster`: For DALI lighting control modules (750-641)

##### Module Properties

- `spec`: `ModuleSpec` - Specification of the module including I/O types and channel counts
- `display_name`: String name for identifying the module
- `channel`: List of `WagoChannel` objects representing the I/O channels of the module
- `config`: `ModuleConfig` - Configuration details for the module

##### Module Methods

- `create_channels()`: Creates the appropriate channel objects for the module
- `append_channel(channel: WagoChannel)`: Adds a channel to the module
- `get_next_address()`: Returns the next available Modbus address

#### WagoChannel

Base class for all channel types. Each module contains multiple channels.

##### Channel Types

- Digital: `DigitalIn`, `DigitalOut`
- Analog: `Int8In`, `Int8Out`, `Int16In`, `Int16Out`, `Float16In`, `Float16Out`
- Special: `Counter32Bit`, `DaliChannel`

##### Channel Properties

- `channel_type`: Identifies the type of channel
- `modbus_channel`: The underlying Modbus channel
- `name`: Optional name for the channel
- `config`: `ChannelConfig` - Configuration details for the channel

##### Channel Methods

- `read()`: Read the current value from the channel
- `write(value)`: Write a value to the channel (output channels only)

### Usage Examples

#### 1. Basic Connection and Discovery

```python
from wg750xxx.settings import ModbusSettings
from wg750xxx.hub import Hub

# Connect to a WAGO PLC
modbus_settings = ModbusSettings(server="192.168.1.100")
hub = Hub(modbus=modbus_settings, config=[], discovery=True)

# Print controller information
print(f"Controller: {hub.info.SERIES}-{hub.info.ITEM}")
print(f"Firmware: {hub.info.FW_VERS}")

# Print discovered modules
for index, module in enumerate(hub.connected_modules):
    print(f"Module {index}: {module.display_name} ({module.description})")
```

#### 2. Reading Digital Inputs

```python
# Get all digital input modules
digital_inputs = [m for m in hub.modules.get("DI", [])]

if digital_inputs:
    # Access the first digital input module
    di_module = digital_inputs[0]

    # Read values from all channels
    for i, channel in enumerate(di_module.channel):
        state = channel.read()
        print(f"Input {i}: {'ON' if state else 'OFF'}")
```

#### 3. Controlling Digital Outputs

```python
# Get digital output modules by type
if "DO" in hub.modules:
    do_module = hub.modules["DO"][0]

    # Turn on first output
    do_module.channel[0].write(True)

    # Turn off second output
    do_module.channel[1].write(False)

    # Toggle third output
    current_state = do_module.channel[2].read()
    do_module.channel[2].write(not current_state)
```

#### 4. Working with Analog Values

```python
# Reading analog inputs
if "AI4" in hub.modules:
    ai_module = hub.modules["AI4"][0]

    # Read raw value from first analog input
    raw_value = ai_module.channel[0].read()

    # Convert to physical value (example: 0-10V range)
    voltage = raw_value * 10.0 / 32767  # Scaling depends on module type
    print(f"Voltage: {voltage:.2f}V")

# Writing to analog outputs
if "AO2" in hub.modules:
    ao_module = hub.modules["AO2"][0]

    # Set output to 50% (assuming 0-32767 range)
    ao_module.channel[0].write(16383)

    # Set output to 5V (assuming 0-10V range)
    value = int(5.0 * 32767 / 10.0)
    ao_module.channel[1].write(value)
```

#### 5. Working with DALI Lighting

```python
# Using DALI module for lighting control
if "Dali" in hub.modules:
    dali = hub.modules["Dali"][0]

    # Set individual light level
    dali.channel[0].write(75)  # Set to 75% brightness

    # Control light groups
    dali.groups[0].write(50)   # Set group 0 to 50% brightness

    # Turn all lights on
    dali.all.write(100)        # Set all lights to 100%
```

#### 6. Working with Counters

```python
# Reading counter values
if "750-404" in hub.modules:
    counter = hub.modules["750-404"][0]

    # Read current count
    count = counter.channel[0].read()
    print(f"Counter value: {count}")
```

### Configuration

The module supports configuration via `ModuleConfig` and `ChannelConfig` objects:

```python
from wg750xxx.settings import ModbusSettings, ModuleConfig, ChannelConfig

# Create configuration for a digital input module
di_config = ModuleConfig(
    name="Wall Switches",
    type="DI",
    channels=[
        ChannelConfig(
            name="Living Room Light Switch",
            type="Digital In",
            device_class="binary_sensor",
            icon="mdi:light-switch"
        ),
        ChannelConfig(
            name="Kitchen Light Switch",
            type="Digital In",
            device_class="binary_sensor"
        )
    ]
)

# Create settings with configuration
modules_config = [di_config]
modbus_settings = ModbusSettings(server="192.168.1.100")

# Initialize hub with configuration
hub = Hub(modbus=modbus_settings, config=modules_config)
```

### Error Handling

The module includes custom exceptions for error handling:

```python
from wg750xxx.modules.exceptions import WagoModuleError

try:
    # Try to read from a module
    value = hub.modules["AI4"][0].channel[0].read()
except WagoModuleError as e:
    print(f"Module error: {e}")
except ConnectionError as e:
    print(f"Connection error: {e}")
finally:
    # Close connection when done
    hub.close()
```

### Supported Module Types

The library includes support for many WAGO 750 series modules:

- Digital I/O (750-4xx and 750-5xx)
- Analog inputs (750-450, 750-451, 750-452, etc.)
- Analog outputs (750-550, 750-552, 750-554, etc.)
- Counters (750-404)
- DALI lighting control (750-641)

Check the module aliases in each class to see the list of supported module types.

### Best Practices

1. Always use `hub.close()` when finished to properly close connections
2. Use module access by type rather than index when possible for robustness
3. Implement proper error handling for connection and module errors
4. Use a discovery phase during startup to detect the connected modules
5. Provide meaningful names in configurations for better traceability

## Implementation Status

After reviewing the wg750xxx module code, here's the current implementation status and suggested improvements:

### Current Status

- **Core Architecture**: The core architecture is implemented, including the Hub class for PLC connection, module detection, and channel abstraction.
- **Module Types**: Basic support for various module types is in place:
  - Digital Input/Output modules
  - Analog Input/Output modules
  - DALI modules
  - Counter modules
  - Controller modules
- **Testing**: Several test files exist, but some are empty placeholders (analog.py, counter.py, digital.py, controller.py).

### Missing Features

1. **Error Handling**: Some error handling is implemented, but comprehensive error handling for connection issues, module failures, and Modbus communication errors could be enhanced.
2. **Value Transformations**: The infrastructure for value transformations is present, but implementation for specific module types may be incomplete.
3. **Event Handling**: Event-based interactions mentioned in the overview are not fully implemented.
4. **YAML Configuration**: Configuration validation and loading from YAML files need improvement.
5. **Documentation**: Module-specific documentation is limited or missing for some module types.

### Implementation Gaps

1. **Empty Test Files**: Several test files are empty placeholders, indicating that test coverage for analog modules, counter modules, and controller modules is missing.
2. **Module Support Completeness**: Support for all WAGO 750 series modules might not be complete.
3. **Advanced DALI Features**: DALI scene management and comprehensive control features might need additional implementation.

### Improvement Suggestions

1. **Complete Test Coverage**: Implement tests for all module types, including analog, counter, and controller modules.
2. **Async Support**: Add async support to the module. Polling and state updates should be async.
3. **Special Module Configuration**: Add special module configuration auto discovery. New module implementations should be added to the `modules` folder and be auto discovered, if they have special configuration options, their config should be available in the api, so that the frontend can show it (eg. DALI groups).
4. **Module Removal**: Add module change handling. When discovered modules do not match the config, the api should handle this gracefully, but notify the user that configuration has changed, so that they can update the config.
5. **Enhance Error Handling**: Add more comprehensive error checking and recovery mechanisms.
6. **Improve Documentation**: Add detailed usage examples for each module type.
7. **Value Mapping Enhancements**: Expand value transformation capabilities, particularly for analog modules.
8. **Event System Implementation**: Complete the implementation of the event handling system described in the overview.
9. **Configuration Validation**: Strengthen configuration validation to ensure compatibility with physical hardware.
10. **Code Comments**: Add more explanatory comments in complex parts of the code.
11. **Performance Optimization**: Review and optimize polling mechanisms for better performance.

### Priority Tasks

1. Complete the empty test files to ensure all module types are properly tested
2. Enhance error handling for robustness in production environments
3. Expand documentation with practical examples for each module type
4. Implement missing features from the implementation plan
