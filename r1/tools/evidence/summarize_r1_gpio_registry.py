#!/usr/bin/env python3
"""Reconstruct the production R1 GPIO-input and GPIO-output device registries.

This is a read-only static-image parser. It decompresses initialized RAM and verifies the exact
registry records, registration loops and known lookup sites; it never reads or drives a GPIO.
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


INPUT_RECORD_SIZE = 0x2C
OUTPUT_RECORD_SIZE = 0x38
INPUT_REGISTRY = 0x200070C0
OUTPUT_REGISTRY = 0x20007228
INPUT_OPERATIONS = 0x200071F4
OUTPUT_OPERATIONS = 0x20007358
INPUT_REGISTRATION_FUNCTION = 0x00054C24
OUTPUT_REGISTRATION_FUNCTION = 0x00054E78

INPUTS = (
    ("acc_int_1", 0x200070C0, 15, 0x00000100, 0x00050128,
     "installed accelerometer interrupt"),
    ("ppg_int", 0x200070EC, 21, 0x00000200, 0x00050944,
     "GH3X2X optical/PPG interrupt"),
    ("touch_rdy_in", 0x20007118, 17, 0x00000200, 0x00051310,
     "IQS7211E active-low RDY interrupt"),
    ("mcu_reset_irq", 0x20007144, 18, 0x00000200, None,
     "firmware-named MCU-reset IRQ input; purpose unconsumed"),
    ("pmic_irq", 0x20007170, 33, 0x00000200, None,
     "firmware-named PMIC IRQ alias; purpose unconsumed"),
    ("nfc_gpo_irq", 0x2000719C, 3, 0x00000100, 0x00050464,
     "ST25DVxxKC GPO interrupt"),
    ("device_stacmd_irq", 0x200071C8, 33, 0x00000200, 0x00050578,
     "YHM2710 state-command/status interrupt"),
)

OUTPUTS = (
    ("ppg_led_en", 0x20007228, 10, False, 0x000502C4,
     "GH3X2X optical-emitter power enable"),
    ("touch_ldo_en", 0x20007260, 30, False, 0x000502C4,
     "IQS7211E LDO enable"),
    ("ppg_reset_en", 0x20007298, 36, False, 0x00050944,
     "GH3X2X reset enable"),
    ("ship_mode_en", 0x200072D0, 9, False, 0x00050578,
     "YHM2710 destructive ship-mode pulse"),
    ("touch_rdy_out", 0x20007308, 17, True, 0x00051310,
     "IQS7211E startup/reset RDY drive"),
)

LOOKUP_PREFIXES = {
    0x00050128: "10b500f011f8044ca068002803d103a0",
    0x000502C4: "10b5074c206818b906a035f007fd2060",
    0x00050464: "38b5104c206818b90fa035f037fc2060",
    0x00050578: "10b5114c606818b910a035f0adfb6060",
    0x00050944: "10b50b4c206818b90aa035f0c7f92060",
    0x00051310: "10b50a4c606818b909a034f0e1fc6060",
}


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


def find_registry_string_address(image: bytes, base: int, value: str) -> int:
    needle = value.encode() + b"\x00"
    addresses: list[int] = []
    start = 0
    while True:
        offset = image.find(needle, start)
        if offset < 0:
            break
        addresses.append(base + offset)
        start = offset + 1
    if not addresses:
        raise ValueError(f"missing string {value!r}")
    return max(addresses)


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


def verify_operations(runtime: bytes, runtime_base: int) -> tuple[dict[str, Any], dict[str, Any]]:
    input_words = [
        word(runtime_slice(runtime, runtime_base, INPUT_OPERATIONS, 0x20), offset)
        for offset in range(0, 0x20, 4)
    ]
    expected_input = [0, 0, 0x00054B91, 0x00054B41, 0x00054ED1, 0, 0, 0]
    if input_words != expected_input:
        raise ValueError(f"unexpected GPIO-input operations: {[hex(value) for value in input_words]}")

    output_words = [
        word(runtime_slice(runtime, runtime_base, OUTPUT_OPERATIONS, 0x20), offset)
        for offset in range(0, 0x20, 4)
    ]
    expected_output = [
        0, 0, 0x00054D99, 0x00054C59, 0x00054E21, 0, 0x00054D21, 0x00054CD1,
    ]
    if output_words != expected_output:
        raise ValueError(
            f"unexpected GPIO-output operations: {[hex(value) for value in output_words]}"
        )

    return (
        {
            "address": f"0x{INPUT_OPERATIONS:08x}",
            "open": "0x00054b91",
            "close": "0x00054b41",
            "read": "0x00054ed1",
        },
        {
            "address": f"0x{OUTPUT_OPERATIONS:08x}",
            "open": "0x00054d99",
            "close": "0x00054c59",
            "read": "0x00054e21",
            "control": "0x00054d21",
            "configure_callbacks": "0x00054cd1",
        },
    )


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

    require_prefix(
        image, base, INPUT_REGISTRATION_FUNCTION,
        "70b50b4d002405f59a7600bf04eb4400",
    )
    require_prefix(
        image, base, OUTPUT_REGISTRATION_FUNCTION,
        "70b50a4d002405f5987600bfc4ebc400",
    )
    for address, prefix in LOOKUP_PREFIXES.items():
        require_prefix(image, base, address, prefix)

    input_operations, output_operations = verify_operations(runtime, scatter_runtime)
    inputs: list[dict[str, Any]] = []
    outputs: list[dict[str, Any]] = []

    for name, address, pin, expected_config, lookup, role in INPUTS:
        block = runtime_slice(runtime, scatter_runtime, address, INPUT_RECORD_SIZE)
        registry_string = c_string(image, word(block, 0), base)
        if registry_string != name:
            raise ValueError(f"unexpected input name {registry_string!r} at 0x{address:08x}")
        if word(block, 8) != pin or word(block, 0x0C) != expected_config:
            raise ValueError(f"unexpected pin/config for {name}")
        if any(block[offset] for offset in range(4, INPUT_RECORD_SIZE) if offset not in range(8, 16)):
            raise ValueError(f"unexpected nonzero initialized runtime field for {name}")
        occurrences = string_occurrence_count(image, name)
        expected_occurrences = 1 if lookup is None else 2
        if occurrences != expected_occurrences:
            raise ValueError(f"unexpected {name} string occurrence count {occurrences}")
        polarity_raw = (expected_config >> 8) & 0xFF
        inputs.append({
            "name": name,
            "descriptor_address": f"0x{address:08x}",
            "pin": gpio(pin),
            "configuration_raw": f"0x{expected_config:08x}",
            "pull_raw": expected_config & 0xFF,
            "pull": "none",
            "polarity_raw": polarity_raw,
            "polarity": "low-to-high" if polarity_raw == 1 else "high-to-low",
            "uses_high_accuracy_gpiote_channel": False,
            "has_recovered_name_lookup_consumer": lookup is not None,
            "lookup_function": None if lookup is None else f"0x{lookup:08x}",
            "compiled_string_occurrences": occurrences,
            "role": role,
        })

    for name, address, pin, startup_high, lookup, role in OUTPUTS:
        block = runtime_slice(runtime, scatter_runtime, address, OUTPUT_RECORD_SIZE)
        registry_string = c_string(image, word(block, 0), base)
        if registry_string != name:
            raise ValueError(f"unexpected output name {registry_string!r} at 0x{address:08x}")
        expected_config = 0x00030101 if startup_high else 0x00030100
        if word(block, 8) != pin or word(block, 0x0C) != expected_config:
            raise ValueError(f"unexpected pin/config for {name}")
        if word(block, 0x10) != 1 or any(block[offset] for offset in range(0x11, OUTPUT_RECORD_SIZE)):
            raise ValueError(f"unexpected initialized output tail for {name}")
        occurrences = string_occurrence_count(image, name)
        if occurrences != 2:
            raise ValueError(f"unexpected {name} string occurrence count {occurrences}")
        outputs.append({
            "name": name,
            "descriptor_address": f"0x{address:08x}",
            "pin": gpio(pin),
            "configuration_raw": f"0x{expected_config:08x}",
            "startup_level": "high" if startup_high else "low",
            "driver_backend_raw": (expected_config >> 8) & 0xFF,
            "gpiote_action_raw": (expected_config >> 16) & 0xFF,
            "gpiote_action": "toggle",
            "gpiote_initial_state_high": False,
            "gpiote_task_pin": True,
            "has_recovered_name_lookup_consumer": True,
            "lookup_function": f"0x{lookup:08x}",
            "compiled_string_occurrences": occurrences,
            "role": role,
            "destructive_if_asserted": name == "ship_mode_en",
        })

    return {
        "image": str(image_path),
        "image_bytes": len(image),
        "image_sha256": hashlib.sha256(image).hexdigest(),
        "load_base": f"0x{base:08x}",
        "scatter_source": f"0x{scatter_source:08x}",
        "scatter_compressed_end": f"0x{scatter_source + consumed:08x}",
        "scatter_runtime": f"0x{scatter_runtime:08x}",
        "scatter_output_bytes": len(runtime),
        "input_registry": {
            "address": f"0x{INPUT_REGISTRY:08x}",
            "record_bytes": INPUT_RECORD_SIZE,
            "registration_function": f"0x{INPUT_REGISTRATION_FUNCTION:08x}",
            "operations": input_operations,
            "records": inputs,
        },
        "output_registry": {
            "address": f"0x{OUTPUT_REGISTRY:08x}",
            "record_bytes": OUTPUT_RECORD_SIZE,
            "registration_function": f"0x{OUTPUT_REGISTRATION_FUNCTION:08x}",
            "operations": output_operations,
            "records": outputs,
        },
        "pin_aliases": {
            "P0.17": ["touch_rdy_in", "touch_rdy_out"],
            "P1.01": ["pmic_irq", "device_stacmd_irq"],
        },
        "registry_summary": {
            "input_count": len(inputs),
            "output_count": len(outputs),
            "unconsumed_input_names": [
                item["name"] for item in inputs
                if not item["has_recovered_name_lookup_consumer"]
            ],
            "startup_high_output_names": [
                item["name"] for item in outputs if item["startup_level"] == "high"
            ],
        },
        "safety": {
            "static_parser_only": True,
            "live_gpio_access": False,
            "ship_mode_control_exposed": False,
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
