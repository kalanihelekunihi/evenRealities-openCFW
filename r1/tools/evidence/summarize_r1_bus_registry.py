#!/usr/bin/env python3
"""Locate every production R1 i2c_<n> descriptor in the initialized scatter image.

This is a read-only static-image parser. It decompresses initialized RAM and reports candidate
descriptor words; it never opens a bus or contacts a ring.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
from pathlib import Path
from typing import Any

from summarize_r1_adc_registry import (
    DEFAULT_BASE,
    DEFAULT_SCATTER_LENGTH,
    DEFAULT_SCATTER_RUNTIME,
    DEFAULT_SCATTER_SOURCE,
    c_string,
    decompress_scatter,
    mapped_offset,
)


BUS_NAMES = tuple(f"i2c_{index}" for index in range(6))
BUS_ADDRESSES = {
    "i2c_0": 0x20006FF4,
    "i2c_1": 0x20007060,
    "i2c_2": 0x20007400,
    "i2c_3": 0x20007470,
    "i2c_4": 0x200074E0,
    "i2c_5": 0x20007550,
}
HARDWARE_CONFIG_ADDRESSES = {
    "i2c_0": 0x0009A5F0,
    "i2c_1": 0x0009A610,
}
BUS_ROLES = {
    "i2c_0": ["IQS7211E capacitive-touch controller"],
    "i2c_1": ["installed accelerometer variant"],
    "i2c_2": ["two GXT310 temperature channels"],
    "i2c_3": [],
    "i2c_4": ["GH3X2X optical/PPG controller"],
    "i2c_5": ["ST25DVxxKC NFC tag", "YHM2710 state-command wrapper"],
}
LOOKUP_FUNCTIONS = {
    "i2c_0": 0x00051310,
    "i2c_1": 0x00050150,
    "i2c_2": 0x00050F08,
    "i2c_3": None,
    "i2c_4": 0x00050944,
    "i2c_5": 0x00050464,
}
REGISTRATION_FUNCTIONS = {
    "i2c_0": 0x00054F90,
    "i2c_1": 0x00054FC4,
    "i2c_2": 0x00056508,
    "i2c_3": 0x00056520,
    "i2c_4": 0x00056538,
    "i2c_5": 0x00056550,
}
SOFTWARE_DELAY_CALLBACKS = {
    "i2c_2": 0x0007A6DD,
    "i2c_3": 0x0007A6ED,
    "i2c_4": 0x0007081D,
    "i2c_5": 0x00054AF1,
}
STACMD_DESCRIPTOR = 0x200075C4


def word(block: bytes, offset: int) -> int:
    return struct.unpack_from("<I", block, offset)[0]


def runtime_slice(runtime: bytes, runtime_base: int, address: int, length: int) -> bytes:
    offset = address - runtime_base
    if offset < 0 or offset + length > len(runtime):
        raise ValueError(f"runtime range 0x{address:08x}+0x{length:x} is outside scatter image")
    return runtime[offset:offset + length]


def flash_bytes(image: bytes, base: int, address: int, length: int) -> bytes:
    offset = mapped_offset(address, base, len(image))
    return image[offset:offset + length]


def flash_word(image: bytes, base: int, address: int) -> int:
    return word(flash_bytes(image, base, address, 4), 0)


def require_prefix(image: bytes, base: int, address: int, expected_hex: str) -> None:
    expected = bytes.fromhex(expected_hex)
    actual = flash_bytes(image, base, address, len(expected))
    if actual != expected:
        raise ValueError(
            f"unexpected bytes at 0x{address:08x}: {actual.hex()} != {expected.hex()}"
        )


def gpio(linear_index: int) -> dict[str, Any]:
    if not 0 <= linear_index < 48:
        raise ValueError(f"nRF52840 GPIO index {linear_index} is outside P0/P1")
    port, pin = divmod(linear_index, 32)
    return {
        "linear_index": linear_index,
        "port": port,
        "pin": pin,
        "name": f"P{port}.{pin:02d}",
    }


def thumb_pointer(value: int) -> str:
    if value == 0 or value & 1 == 0:
        raise ValueError(f"expected nonzero Thumb pointer, got 0x{value:08x}")
    return f"0x{value:08x}"


def find_c_string_address(image: bytes, base: int, value: str) -> int:
    needle = value.encode() + b"\x00"
    candidates: list[int] = []
    start = 0
    while True:
        offset = image.find(needle, start)
        if offset < 0:
            break
        candidates.append(base + offset)
        start = offset + 1
    if not candidates:
        raise ValueError(f"missing string {value!r}")
    # Registry names are the high-address copies grouped near one another, rather than log text.
    return max(candidates)


def string_occurrence_count(image: bytes, value: str) -> int:
    needle = value.encode() + b"\x00"
    count = 0
    start = 0
    while True:
        offset = image.find(needle, start)
        if offset < 0:
            return count
        count += 1
        start = offset + 1


def operation_pointers(block: bytes, offset: int) -> dict[str, str]:
    if word(block, offset) != 0 or word(block, offset + 4) != 0:
        raise ValueError("unexpected non-null reserved bus operation")
    names = ["open", "close", "read", "write"]
    return {
        name: thumb_pointer(word(block, offset + 8 + index * 4))
        for index, name in enumerate(names)
    }


def summarize(
    image_path: Path,
    base: int,
    scatter_source: int,
    scatter_runtime: int,
    scatter_length: int,
) -> dict[str, Any]:
    image = image_path.read_bytes()
    source_offset = mapped_offset(scatter_source, base, len(image))
    runtime, consumed = decompress_scatter(image[source_offset:], scatter_length)

    require_prefix(image, base, 0x00054F90, "0b4810b50168416200f13c0181622430")
    require_prefix(image, base, 0x00054FC4, "0b4810b50168416200f13c0181622430")
    for address in (0x00056508, 0x00056520, 0x00056538, 0x00056550):
        require_prefix(image, base, address, "04480168416300f14c01816334302ff0")
    require_prefix(image, base, 0x00050150, "10b5044c2068002803d103a035f0c0fd")
    require_prefix(image, base, 0x00050F08, "10b5044c2068002803d103a034f0e4fe")
    require_prefix(image, base, 0x00050944, "10b50b4c206818b90aa035f0c7f92060")
    require_prefix(image, base, 0x00050464, "38b5104c206818b90fa035f037fc2060")
    require_prefix(image, base, 0x00051310, "10b50a4c606818b909a034f0e1fc6060")

    stacmd = runtime_slice(runtime, scatter_runtime, STACMD_DESCRIPTOR, 4)
    stacmd_name = c_string(image, word(stacmd, 0), base)
    if stacmd_name != "device_stacmd":
        raise ValueError(f"unexpected i2c_5 state-command client name {stacmd_name!r}")

    buses: list[dict[str, Any]] = []
    for name in BUS_NAMES:
        name_address = find_c_string_address(image, base, name)
        encoded = struct.pack("<I", name_address)
        offsets = [
            offset for offset in range(0, len(runtime) - 3, 4)
            if runtime[offset:offset + 4] == encoded
        ]
        expected_address = BUS_ADDRESSES[name]
        expected_offset = expected_address - scatter_runtime
        if offsets != [expected_offset]:
            raise ValueError(
                f"unexpected {name} descriptor offsets: {[hex(value) for value in offsets]}"
            )
        hardware = name in HARDWARE_CONFIG_ADDRESSES
        block = runtime_slice(runtime, scatter_runtime, expected_address, 0x6C if hardware else 0x70)
        common: dict[str, Any] = {
            "index": int(name[-1]),
            "name": name,
            "descriptor_address": f"0x{expected_address:08x}",
            "registration_function": f"0x{REGISTRATION_FUNCTIONS[name]:08x}",
            "lookup_function": (
                None if LOOKUP_FUNCTIONS[name] is None
                else f"0x{LOOKUP_FUNCTIONS[name]:08x}"
            ),
            "compiled_string_occurrences": string_occurrence_count(image, name),
            "has_recovered_consumer": LOOKUP_FUNCTIONS[name] is not None,
            "roles": BUS_ROLES[name],
            "clock": gpio(word(block, 0x08 if hardware else 0x0C)),
            "data": gpio(word(block, 0x0C if hardware else 0x10)),
            "operations": operation_pointers(block, 0x3C if hardware else 0x4C),
        }
        if hardware:
            config_address = HARDWARE_CONFIG_ADDRESSES[name]
            frequency = flash_word(image, base, config_address + 0x10)
            options = flash_word(image, base, config_address + 0x14)
            if frequency != 0x06680000 or options & 0xFF != 2:
                raise ValueError(f"unexpected {name} TWIM frequency/options")
            common.update({
                "transport": "nRF TWIM",
                "peripheral_instance_index": word(block, 0x10),
                "peripheral_register_base": f"0x{word(block, 0x14):08x}",
                "configuration_address": f"0x{config_address:08x}",
                "frequency_register_raw": f"0x{frequency:08x}",
                "frequency_hz": 400_000,
                "interrupt_priority": options & 0xFF,
                "clear_bus_initialization": bool((options >> 8) & 0xFF),
                "hold_bus_uninitialized": bool((options >> 16) & 0xFF),
                "configuration_padding_byte": (options >> 24) & 0xFF,
            })
        else:
            delay_callback = word(block, 0x28)
            if delay_callback != SOFTWARE_DELAY_CALLBACKS[name]:
                raise ValueError(f"unexpected {name} delay callback 0x{delay_callback:08x}")
            common.update({
                "transport": "software-driven two-wire",
                "half_cycle_delay_argument_raw": word(block, 0x08),
                "delay_callback": thumb_pointer(delay_callback),
                "delay_callback_has_no_effect": name == "i2c_5",
            })
        buses.append(common)

    return {
        "image": str(image_path),
        "image_bytes": len(image),
        "image_sha256": hashlib.sha256(image).hexdigest(),
        "load_base": f"0x{base:08x}",
        "scatter_source": f"0x{scatter_source:08x}",
        "scatter_compressed_end": f"0x{scatter_source + consumed:08x}",
        "scatter_runtime": f"0x{scatter_runtime:08x}",
        "scatter_output_bytes": len(runtime),
        "buses": buses,
        "registry_summary": {
            "bus_count": len(buses),
            "hardware_twim_count": sum(bus["transport"] == "nRF TWIM" for bus in buses),
            "software_two_wire_count": sum(
                bus["transport"] == "software-driven two-wire" for bus in buses
            ),
            "unconsumed_bus_indices": [
                bus["index"] for bus in buses if not bus["has_recovered_consumer"]
            ],
            "i2c_5_state_command_client": {
                "descriptor_address": f"0x{STACMD_DESCRIPTOR:08x}",
                "name": stacmd_name,
            },
        },
        "safety": {
            "static_parser_only": True,
            "live_bus_access": False,
        },
    }


def parse_integer(value: str) -> int:
    return int(value, 0)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", type=Path)
    parser.add_argument("--base", type=parse_integer, default=DEFAULT_BASE)
    parser.add_argument("--scatter-source", type=parse_integer, default=DEFAULT_SCATTER_SOURCE)
    parser.add_argument("--scatter-runtime", type=parse_integer, default=DEFAULT_SCATTER_RUNTIME)
    parser.add_argument("--scatter-length", type=parse_integer, default=DEFAULT_SCATTER_LENGTH)
    arguments = parser.parse_args()
    print(json.dumps(summarize(
        arguments.image,
        arguments.base,
        arguments.scatter_source,
        arguments.scatter_runtime,
        arguments.scatter_length,
    ), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
