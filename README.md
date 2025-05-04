# Python Module for WAGO 750-xxx series PLCs

This third party Python module provides an abstraction layer for interacting with WAGO 750 series PLCs through Modbus TCP communication. It offers an object-oriented interface to control and monitor various WAGO PLC modules and their channels.

## Installation

```bash
pip install wg750xxx
```

## Overview

The WAGO 750 series PLC is a modular system with a central Hub. There are Hubs available using the Modbus TCP protocol, which this module supports. Each module can have multiple channels and supports different functionalities like digital/analog I/O, temperature sensors, counters, motor controllers, DALI lighting control, and many more.

This module provides a high-level abstraction that represents the PLC Hub and its connected modules as Python objects, making it easy to interact with the physical hardware through simple Python code.

## Usage Example

```python
from wg750xxx import PlcHub

# Create a hub instance (automatically connects to Modbus)
hub = PlcHub(ip_address="0.2.2.100")

# Access a digital output module by index
light_control = hub.modules[4].channels[1]
light_control.value = 100  # Set light to 100%

# Access a dimmer module by type
from wg750xxx.modules import AO4
dimmer = hub.modules.get(AO4)[0].channels[1]
dimmer.value = 50  # Set dimmer to 50%

# Complex module example (DALI)
dali_module = hub.modules["DALI"][0]
dali_module.add_to_group(channel=1, group=1)  # Add light to group 1
dali_module.create_scene(group=1, scene=1)    # Create scene 1
dali_module.set_group_level(group=1, level=80)  # Set group brightness
```

## Features

- **Automatic Module Detection**: The Hub automatically identifies connected modules
- **Flexible Configuration**: Support for both minimal and detailed module configurations
- **Smart Module Matching**: Intelligent configuration validation and module matching
- **Value Transformations**: Built-in support for value scaling and mapping
- **Event Handling**: Support for complex input patterns (e.g., button gestures)
- **Direct I/O Mapping**: Configure direct relationships between inputs and outputs
- **Runtime Configuration**: Ability to modify and persist configurations during runtime

## Documentation

For more detailed documentation, please refer to the [project repository](https://github.com/yourusername/python-wg750xxx).

## License

MIT License
