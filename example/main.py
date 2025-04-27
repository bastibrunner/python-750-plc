"""This is a simple demo of the Wago 750xxx Module.

It will connect to the Wago 750xxx bus, print the discovered modules and their channels.
The modules will be polled regularly and the updated values will be printed to the console.
"""

import logging
import sys
import time
from typing import Any

import yaml

from wg750xxx.modules.channel import WagoChannel
from wg750xxx.settings import HubConfig
from wg750xxx.wg750xxx import PLCHub


def on_change_callback(new_value: Any, channel: WagoChannel) -> None:
    """Callback function for when a channel value changes.
    It will print the channel id and the new value.
    """
    print(f"{channel.config.id} {new_value}")


def main() -> None:
    """Main function."""
    log = logging.getLogger()
    log.setLevel(logging.INFO)
    log.addHandler(logging.StreamHandler(sys.stdout))

    hub = PLCHub(HubConfig(host="10.22.22.16", port=502), True)
    print(
        yaml.dump(
            {"modules": [str(m.module_identifier) for m in hub.modules]}, indent=2
        )
    )

    for module in hub.modules:
        for channel in module.channels or []:
            channel.on_change_callback = on_change_callback
            channel.update_interval = 5000

    # Get the DALI module(s) if present
    dali_modules = hub.modules.get("641")
    if isinstance(dali_modules, list):
        for dali_module in dali_modules:
            if hasattr(dali_module, "on_change_callback"):
                dali_module.on_change_callback = on_change_callback
    elif dali_modules is not None and hasattr(dali_modules, "on_change_callback"):
        dali_modules.on_change_callback = on_change_callback

    if hub.connection is not None:
        hub.connection.start_continuous_update(
            30, discrete_interval=100, input_interval=100
        )

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        hub.connection.stop_continuous_update()


if __name__ == "__main__":
    main()
