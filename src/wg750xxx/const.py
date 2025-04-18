"""Constants for the WAGO wg750xxx module."""

DEFAULT_HOST = "10.22.22.16"
DEFAULT_PORT = 502
DEFAULT_SCAN_INTERVAL = 10
DEFAULT_TIMEOUT = 5

ERROR_CODES = {
    0x01: "Illegal function",
    0x02: "Illegal data address",
    0x03: "Illegal data value",
    0x04: "Slave device failure",
    0x05: "Acknowledge",
    0x06: "Server busy",
    0x08: "Memory parity error",
    0x0A: "Gateway path unavailable",
    0x0B: "Gateway target device failed to respond",
}
