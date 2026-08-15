#!/usr/bin/env python3
"""Decode the production R1 YHM2710 state-command transport descriptors.

This is a read-only static-image parser. It reports the software-driven two-wire pins and exact
byte phases emitted by firmware; it does not access hardware or construct a live sender.
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


EXPECTED_IMAGE_SHA256 = "0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a"

I2C_DESCRIPTOR = 0x20007550
I2C_OPERATIONS = 0x200075A4
STACMD_DESCRIPTOR = 0x200075C4
STACMD_OPERATIONS = 0x20007614
STACMD_IRQ_DESCRIPTOR = 0x200071C8
REGISTER1_SCALE_ADDRESS = 0x0003558C
REGISTER1_TABLE_POINTER_ADDRESS = 0x00035590
COLD_SETPOINT_ADDRESS = 0x00096CB8
NORMAL_SETPOINT_ADDRESS = 0x00096CC0
SHARED_POWER_ACQUIRE = 0x00050778
SHARED_POWER_RELEASE = 0x00050758
REGISTER2_INACTIVE_WRITE = 0x00035594
REGISTER2_ACTIVE_WRITE = 0x000355A8
REGISTER2_HIGH_TEMPERATURE_WRITE = 0x00035684
REGISTER3_CHARGING_EVENT_SET = 0x000350E0


def _function(
    entry: int,
    end_exclusive: int,
    symbol: str,
    role: str,
    sha256: str,
    provider_family: str = "yhmicros_yhm2710_candidate",
    segments: tuple[tuple[int, int], ...] = (),
) -> dict[str, Any]:
    return {
        "entry": entry,
        "end_exclusive": end_exclusive,
        "size": sum(end - start for start, end in segments) if segments
        else end_exclusive - entry,
        "symbol": symbol,
        "role": role,
        "provider_family": provider_family,
        "sha256": sha256,
        "segments": segments,
    }


# Complete executable closure of the separately recovered P1.01 state-command
# transport.  The 0x5cbe4 entry has two out-of-line branches separated by
# literal pools, so its digest is over the three executable spans in order.
YHM2710_STACMD_FUNCTIONS = [
    _function(0x00028BB0, 0x00028C68, "yhm2710_stacmd_read_frame_candidate",
              "read_frame_and_per_byte_parity", "47849a4670adddd4a40ed07d81082356a80a836740a6a9dd7bd428b48496e78f"),
    _function(0x00028C6C, 0x00028CEE, "yhm2710_stacmd_write_frame_candidate",
              "write_frame_and_per_byte_parity", "50d2291df19b191c8db8dceb2f0431860de47fa50dc58aacfcb882e9e7d9e373"),
    _function(0x00035698, 0x0003570C, "yhm2710_stacmd_write_retry_candidate",
              "ten_attempt_write_retry", "c6a1ca30c13f32a283cef80e62a07b55fb7c146b642945df0d020185992ab714"),
    _function(0x00056568, 0x00056576, "yhm2710_stacmd_close_candidate",
              "device_close", "66f5dba3883e20e6e18d2438b2b344fa94af393e2568291b99f7a6ae12b6ae74"),
    _function(0x0005657C, 0x0005658C, "yhm2710_stacmd_open_candidate",
              "device_open", "e9b47e2b31c854f46214cd211f680247d6b61c6a8c94045806127d2eeb2844ef"),
    _function(0x00056590, 0x000565EE, "yhm2710_stacmd_read_adapter_candidate",
              "validated_ten_attempt_read", "b1b4c14b0c3b13d2fd0f85614249b64d595d0214dd988ee22742e6a31da91712"),
    _function(0x000565F4, 0x00056606, "r1_yhm2710_stacmd_binding_configuration",
              "fixed_record_and_operation_table_registration", "f861716068d2a6de5645d8ce65b86f81a6219d9e49abb147cc170086b3a56c8d",
              "r1_device_registry_configuration_adapter"),
    _function(0x0005660C, 0x00056634, "yhm2710_stacmd_write_adapter_candidate",
              "validated_write_adapter", "01d4c1162ec4273b2ba5ac2a4a7b00af5a267db463b2efa6b4f332f295b23202"),
    _function(0x0005CBE4, 0x0005CC62, "yhm2710_stacmd_drive_bit_candidate",
              "timed_zero_or_one_drive", "eb391912a97f1acece03fde1656394eec28577eaabe9dee48f5c0c2c6714d861",
              segments=((0x0005CBE4, 0x0005CBEE), (0x0005CBF0, 0x0005CC26),
                        (0x0005CC2C, 0x0005CC62))),
    _function(0x0005CC68, 0x0005CC8C, "yhm2710_stacmd_write_bits_candidate",
              "seven_or_eight_bit_msb_first_write", "b1bae782110a30723577fc1d611ffaf865c69f56b8ad6333aa593f993e9736de"),
    _function(0x0005CC8C, 0x0005CCC6, "yhm2710_stacmd_bus_recovery_candidate",
              "single_wire_recovery_sequence", "7be521964d7f7a7629ba211547de289318c7e6eef02824bd34a967ee36ccffa8"),
    _function(0x0005CCCC, 0x0005CCF6, "yhm2710_stacmd_idle_candidate",
              "single_wire_idle_sequence", "886ede38acd5968998d79a4464678892f9c8d26db3616d743c2cdc58ea1e632c"),
    _function(0x00087B30, 0x00087B9E, "yhm2710_stacmd_read_bit_candidate",
              "bounded_edge_wait_and_bit_sample", "68463f038a9ab010a6f65dcdab02b2e34d732704aa2c9f6c5472db96d6f1632a"),
    _function(0x000968A8, 0x000968C2, "yhm2710_stacmd_parity_candidate",
              "byte_xor_parity", "ab8ebd42399f646054cc1f2b250658cd30425acf5597259e81a241d5f09626ae"),
    _function(0x000969EC, 0x000969FC, "yhm2710_stacmd_read_bit_adapter_candidate",
              "read_bit_result_adapter", "3db701dfcf43a78e8cc2c06a64b9b6e4844951606a19337772719c00084b5738"),
]


def word(block: bytes, offset: int) -> int:
    return struct.unpack_from("<I", block, offset)[0]


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


def runtime_slice(runtime: bytes, runtime_base: int, address: int, length: int) -> bytes:
    offset = address - runtime_base
    if offset < 0 or offset + length > len(runtime):
        raise ValueError(f"runtime range 0x{address:08x}+0x{length:x} is outside scatter image")
    return runtime[offset:offset + length]


def thumb_pointer(value: int) -> str:
    if value == 0 or value & 1 == 0:
        raise ValueError(f"expected a nonzero Thumb pointer, got 0x{value:08x}")
    return f"0x{value:08x}"


def flash_word(image: bytes, base: int, address: int) -> int:
    return struct.unpack_from("<I", image, mapped_offset(address, base, len(image)))[0]


def flash_float(image: bytes, base: int, address: int) -> float:
    return struct.unpack_from("<f", image, mapped_offset(address, base, len(image)))[0]


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


def summarize(
    image_path: Path,
    base: int,
    scatter_source: int,
    scatter_runtime: int,
    scatter_length: int,
) -> dict[str, Any]:
    image = image_path.read_bytes()
    image_digest = hashlib.sha256(image).hexdigest()
    if image_digest != EXPECTED_IMAGE_SHA256:
        raise ValueError(f"unexpected application image SHA-256: {image_digest}")
    source_offset = mapped_offset(scatter_source, base, len(image))
    runtime, consumed = decompress_scatter(image[source_offset:], scatter_length)

    bus = runtime_slice(runtime, scatter_runtime, I2C_DESCRIPTOR, 0x54)
    bus_operations = runtime_slice(runtime, scatter_runtime, I2C_OPERATIONS, 0x10)
    stacmd = runtime_slice(runtime, scatter_runtime, STACMD_DESCRIPTOR, 0x30)
    stacmd_operations = runtime_slice(runtime, scatter_runtime, STACMD_OPERATIONS, 0x10)
    irq = runtime_slice(runtime, scatter_runtime, STACMD_IRQ_DESCRIPTOR, 0x10)

    bus_name = c_string(image, word(bus, 0), base)
    stacmd_name = c_string(image, word(stacmd, 0), base)
    irq_name = c_string(image, word(irq, 0), base)
    if bus_name != "i2c_5" or stacmd_name != "device_stacmd" \
            or irq_name != "device_stacmd_irq":
        raise ValueError("unexpected production PMIC transport descriptor names")

    # Functions 0x55ad2/0x5608e show field +0x0c is clock and +0x10 is data:
    # data changes first, then clock is raised/lowered for each MSB-first bit.
    clock_pin = word(bus, 0x0C)
    data_pin = word(bus, 0x10)
    status_pin = word(stacmd, 0x0C)
    if word(irq, 0x08) != status_pin:
        raise ValueError("state-command and IRQ descriptors disagree on their GPIO")

    operation_names = ["open", "close", "read", "write"]
    bus_operation_pointers = {
        name: thumb_pointer(word(bus_operations, index * 4))
        for index, name in enumerate(operation_names)
    }
    stacmd_operation_pointers = {
        name: thumb_pointer(word(stacmd_operations, index * 4))
        for index, name in enumerate(operation_names)
    }
    if stacmd_operation_pointers != {
        "open": "0x0005657d", "close": "0x00056569",
        "read": "0x00056591", "write": "0x0005660d",
    }:
        raise ValueError("unexpected device_stacmd operation table")

    function_census = []
    for function in YHM2710_STACMD_FUNCTIONS:
        segments = function["segments"] or ((function["entry"], function["end_exclusive"]),)
        body = b"".join(
            flash_bytes(image, base, int(start), int(end) - int(start))
            for start, end in segments
        )
        if len(body) != function["size"] or hashlib.sha256(body).hexdigest() != function["sha256"]:
            raise ValueError(f"YHM2710 STACMD function changed at 0x{function['entry']:08x}")
        function_census.append({
            **function,
            "entry": f"0x{function['entry']:08x}",
            "end_exclusive": f"0x{function['end_exclusive']:08x}",
            "segments": [
                {"start": f"0x{start:08x}", "end_exclusive": f"0x{end:08x}"}
                for start, end in segments
            ],
        })
    register_examples = {
        f"0x{register:02x}": {
            "read_transmit_phases": [[register, 0, 0], [register | 1]],
            "write_one_byte": [register, 0, 0, 0xA5],
        }
        for register in range(10)
    }
    register1_scale = flash_float(image, base, REGISTER1_SCALE_ADDRESS)
    multiplier_table = flash_word(image, base, REGISTER1_TABLE_POINTER_ADDRESS)
    multipliers = [flash_float(image, base, multiplier_table + index * 4) for index in range(8)]
    setpoints = [register1_scale * multiplier for multiplier in multipliers]
    cold_setpoint = flash_float(image, base, COLD_SETPOINT_ADDRESS)
    normal_setpoint = flash_float(image, base, NORMAL_SETPOINT_ADDRESS)

    # Bound the raw register-policy report to this exact image. These signatures cover the client
    # index range checks/bitmask transitions and the literal-value register writers; no code runs.
    require_prefix(image, base, SHARED_POWER_RELEASE, "03280ad2054a0121814010680142")
    require_prefix(image, base, SHARED_POWER_ACQUIRE, "70b503280bd2064d0124844028680442")
    require_prefix(image, base, REGISTER2_INACTIVE_WRITE, "08b528208df800006a4601210220")
    require_prefix(image, base, REGISTER2_ACTIVE_WRITE, "08b5a8208df800006a4601210220")
    require_prefix(image, base, REGISTER2_HIGH_TEMPERATURE_WRITE, "08b5f8208df800006a4601210220")
    require_prefix(image, base, REGISTER3_CHARGING_EVENT_SET, "1cb500208df800006a4601210320")

    return {
        "image": str(image_path),
        "image_bytes": len(image),
        "image_sha256": image_digest,
        "load_base": f"0x{base:08x}",
        "scatter_source": f"0x{scatter_source:08x}",
        "scatter_compressed_end": f"0x{scatter_source + consumed:08x}",
        "scatter_runtime": f"0x{scatter_runtime:08x}",
        "bus_descriptor": {
            "address": f"0x{I2C_DESCRIPTOR:08x}",
            "name": bus_name,
            "clock": gpio(clock_pin),
            "data": gpio(data_pin),
            "half_cycle_delay_argument": word(bus, 0x08),
            "delay_callback": thumb_pointer(word(bus, 0x28)),
            "delay_callback_has_no_effect": word(bus, 0x28) == 0x00054AF1,
            "operations_address": f"0x{I2C_OPERATIONS:08x}",
            "operations": bus_operation_pointers,
        },
        "state_command_device": {
            "descriptor_address": f"0x{STACMD_DESCRIPTOR:08x}",
            "name": stacmd_name,
            "operations_address": f"0x{STACMD_OPERATIONS:08x}",
            "operations": stacmd_operation_pointers,
            "status_or_irq_gpio": gpio(status_pin),
            "irq_descriptor_address": f"0x{STACMD_IRQ_DESCRIPTOR:08x}",
            "irq_name": irq_name,
            "irq_configuration_word": f"0x{word(irq, 0x0C):08x}",
        },
        "state_command_function_census": {
            "function_count": len(function_census),
            "function_bytes": sum(int(item["size"]) for item in function_census),
            "vendor_candidate_bytes": sum(
                int(item["size"]) for item in function_census
                if item["provider_family"] == "yhmicros_yhm2710_candidate"
            ),
            "local_transport_implementation_authorized": True,
            "functions": function_census,
        },
        "wire_contract": {
            "classification": "software-driven I2C-style STACMD, not conventional fixed-address I2C",
            "bit_order": "MSB first",
            "ack_after_each_transmitted_byte": True,
            "read_ack_all_but_final_byte": True,
            "clock_stretch_wait_present": False,
            "fixed_subaddress_bytes": [0, 0],
            "read_sequence": [
                "START", "register command byte", "00", "00", "REPEATED START",
                "register command byte OR 01", "read bytes; ACK all but final byte", "STOP",
            ],
            "write_sequence": [
                "START", "register command byte", "00", "00", "payload bytes", "STOP",
            ],
            "register_examples": register_examples,
        },
        "charge_temperature_register_policy": {
            "register_1_upper_field_shift": 5,
            "register_1_upper_field_mask": "0xe0",
            "setpoint_units": "not proven without YHM2710 documentation",
            "scale": register1_scale,
            "multipliers": multipliers,
            "code_setpoints": setpoints,
            "selection": "minimum absolute difference; strict-less comparison keeps earlier code on ties",
            "temperature_input": "six-bit unsigned whole degrees derived from charge temperature",
            "actions": [
                {"whole_degrees": "0", "action": "preserve current registers"},
                {
                    "whole_degrees": "1...14",
                    "target": cold_setpoint,
                    "selected_code": min(range(8), key=lambda index: abs(setpoints[index] - cold_setpoint)),
                },
                {
                    "whole_degrees": "15...44",
                    "target": normal_setpoint,
                    "selected_code": min(range(8), key=lambda index: abs(setpoints[index] - normal_setpoint)),
                },
                {"whole_degrees": "45...63", "write_register_2": "0xf8"},
            ],
        },
        "raw_register_policy": {
            "register_2": {
                "initialization_writes": ["0x01", "0xa0"],
                "shared_power_lease": {
                    "physical_meaning": "not proven without YHM2710 documentation",
                    "acquire_function": f"0x{SHARED_POWER_ACQUIRE:08x}",
                    "release_function": f"0x{SHARED_POWER_RELEASE:08x}",
                    "client_bits": {
                        "0": "transient battery sampling",
                        "1": "optical/PPG",
                        "2": "touch",
                    },
                    "first_acquire_write": "0xa8",
                    "additional_or_duplicate_acquire_write": None,
                    "nonfinal_or_duplicate_release_write": None,
                    "last_release_write": "0x28",
                },
                "charge_temperature_45_through_63_write": "0xf8",
            },
            "register_3": {
                "initialization_write": "0x02",
                "charging_event_set_mask": "0x08",
                "nfc_readiness_repair_set_mask": "0x40",
                "remaining_bit_meanings": "not proven",
            },
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
