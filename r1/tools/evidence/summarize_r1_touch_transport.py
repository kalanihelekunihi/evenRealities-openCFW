#!/usr/bin/env python3
"""Decode the production R1 IQS7211E electrical transport and lifecycle.

This is a read-only static-image parser. It never opens a host bus, toggles GPIO, or emits a
controller command; it records the exact board descriptors and compiled sequencing needed to
reason about safe phone-side support.
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


I2C_DESCRIPTOR = 0x20006FF4
I2C_OPERATIONS = 0x20007030
TOUCH_RUNTIME_STATE = 0x200067F8
IQS_RUNTIME_STATE = 0x2000772C
TOUCH_RDY_IN_DESCRIPTOR = 0x20007118
TOUCH_LDO_DESCRIPTOR = 0x20007260
TOUCH_RDY_OUT_DESCRIPTOR = 0x20007308
TWIM_CONFIGURATION = 0x0009A5F0


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
    source_offset = mapped_offset(scatter_source, base, len(image))
    runtime, consumed = decompress_scatter(image[source_offset:], scatter_length)

    bus = runtime_slice(runtime, scatter_runtime, I2C_DESCRIPTOR, 0x60)
    operations = runtime_slice(runtime, scatter_runtime, I2C_OPERATIONS, 0x18)
    state = runtime_slice(runtime, scatter_runtime, TOUCH_RUNTIME_STATE, 0x20)
    iqs_state = runtime_slice(runtime, scatter_runtime, IQS_RUNTIME_STATE, 0x24)
    rdy_in = runtime_slice(runtime, scatter_runtime, TOUCH_RDY_IN_DESCRIPTOR, 0x2C)
    ldo = runtime_slice(runtime, scatter_runtime, TOUCH_LDO_DESCRIPTOR, 0x38)
    rdy_out = runtime_slice(runtime, scatter_runtime, TOUCH_RDY_OUT_DESCRIPTOR, 0x38)

    names = {
        "bus": c_string(image, word(bus, 0), base),
        "rdy_in": c_string(image, word(rdy_in, 0), base),
        "ldo": c_string(image, word(ldo, 0), base),
        "rdy_out": c_string(image, word(rdy_out, 0), base),
    }
    expected_names = {
        "bus": "i2c_0",
        "rdy_in": "touch_rdy_in",
        "ldo": "touch_ldo_en",
        "rdy_out": "touch_rdy_out",
    }
    if names != expected_names:
        raise ValueError(f"unexpected production touch device names: {names}")
    if word(rdy_in, 8) != word(rdy_out, 8):
        raise ValueError("RDY input and output descriptors disagree on their physical GPIO")
    if rdy_in[0x0C] != 0 or rdy_in[0x0D] != 2 or word(rdy_in, 0x0C) != 0x00000200:
        raise ValueError("unexpected unpulled high-to-low RDY input configuration")

    twim_frequency_raw = flash_word(image, base, TWIM_CONFIGURATION + 0x10)
    packed_twim_options = flash_word(image, base, TWIM_CONFIGURATION + 0x14)
    if twim_frequency_raw != 0x06680000 or packed_twim_options != 0x00010002:
        raise ValueError("unexpected production TWIM frequency/options record")
    expected_iqs_state = bytes(5) + b"\xff" + bytes(0x24 - 6)
    if iqs_state != expected_iqs_state:
        raise ValueError(f"unexpected initial IQS runtime state: {iqs_state.hex()}")

    # These signatures bind the reported lifecycle to this image without executing it.
    require_prefix(image, base, 0x00046650, "2de9f0410446400201d5fff735fc")
    require_prefix(image, base, 0x0004E070, "10b51d4904460020487343f037fa")
    require_prefix(image, base, 0x0004EB60, "064810b50178002907d000210170")
    require_prefix(image, base, 0x0004EB80, "10b5154c2078002824d101f0f8fb")
    require_prefix(image, base, 0x0002FDC8, "1cb56c208df8040001200346009001aa")
    require_prefix(image, base, 0x0002FDE2, "1cb501200090002301aaff21562000f0")
    require_prefix(image, base, 0x0002F866, "1cb500208df8040001200346009001aa")
    require_prefix(image, base, 0x0002FDF8, "10b5332057f0d2fe40f40061332067f0")
    require_prefix(image, base, 0x0002FE9C, "30b414460846214630bc1a4663f070ba")
    require_prefix(image, base, 0x0002FEAC, "30b414460846214630bc1a4663f07cba")
    require_prefix(image, base, 0x000502C4, "10b5074c206818b906a035f007fd")
    require_prefix(image, base, 0x00051310, "10b50a4c606818b909a034f0e1fc")
    require_prefix(image, base, 0x00051368, "174810b5007858b142f034f8002825d1")
    require_prefix(image, base, 0x00054B90, "feb5214d0646002404eb440000ebc400")
    require_prefix(image, base, 0x00054FF8, "2de9fc47164fddf828808df804100026")
    require_prefix(image, base, 0x0005505C, "f0b595b005461a9e502b02d9092015b0")
    require_prefix(image, base, 0x0006ED94, "2de9f0410b4e0f460546002404eb4400")
    require_prefix(image, base, 0x0006F9E4, "2de9fc4121f080fdc0074ff0806703d1")
    require_prefix(image, base, 0x0006FCE8, "70b521f0fffbc0074ff0406503d121f0")
    require_prefix(image, base, 0x0007A81C, "2de9fc41dff8bc80044608eb04000027")
    require_prefix(image, base, 0x0008E6A0, "70b5184d064601246869b4400442")
    require_prefix(image, base, 0x0008E7B0, "10b5054804f026fe044804f0e5fdbde8")
    require_prefix(image, base, 0x0008E7D0, "70b5174c054601266069ae400642")
    require_prefix(image, base, 0x000933FC, "012000f081b80000")
    require_prefix(image, base, 0x00030E6C, "f0b56c4c8fb0207830b1fef7a7fffef7")
    require_prefix(image, base, 0x00046EAC, "10b52bf0e5fc4af01bfbc00703d14af0")
    require_prefix(image, base, 0x0007287C, "01490020087170472c770020")
    require_prefix(image, base, 0x00072888, "02480079002800d0012070472c770020")

    operation_names = ["reserved_0", "reserved_1", "open", "close", "read", "write"]
    operation_pointers = {
        name: (None if word(operations, index * 4) == 0 else
               f"0x{word(operations, index * 4):08x}")
        for index, name in enumerate(operation_names)
    }

    return {
        "image": str(image_path),
        "image_bytes": len(image),
        "image_sha256": hashlib.sha256(image).hexdigest(),
        "load_base": f"0x{base:08x}",
        "scatter_source": f"0x{scatter_source:08x}",
        "scatter_compressed_end": f"0x{scatter_source + consumed:08x}",
        "scatter_runtime": f"0x{scatter_runtime:08x}",
        "controller": {
            "model": "IQS7211E",
            "i2c_7_bit_address": word(state, 0x14),
            "data_word_order": "little-endian",
            "runtime_state_address": f"0x{IQS_RUNTIME_STATE:08x}",
            "runtime_state_initial_hex": iqs_state.hex(),
            "runtime_state_initial": {
                "suspend_request_latch": bool(iqs_state[0]),
                "local_recovery_gate": iqs_state[1],
                "consecutive_ati_error_irqs": iqs_state[2],
                "hardware_restart_attempts": iqs_state[3],
                "hardware_restart_pending": bool(iqs_state[4]),
                "diagnostic_bank_selector": iqs_state[5],
            },
        },
        "bus": {
            "descriptor_address": f"0x{I2C_DESCRIPTOR:08x}",
            "name": names["bus"],
            "scl": gpio(word(bus, 8)),
            "sda": gpio(word(bus, 0x0C)),
            "peripheral_instance_index": word(bus, 0x10),
            "peripheral_register_base": f"0x{word(bus, 0x14):08x}",
            "frequency_register_raw": f"0x{twim_frequency_raw:08x}",
            "frequency_hz": 400_000,
            "interrupt_priority": packed_twim_options & 0xFF,
            "clear_bus_initialization": bool((packed_twim_options >> 8) & 0xFF),
            "hold_bus_uninitialized": bool((packed_twim_options >> 16) & 0xFF),
            "configuration_padding_byte": (packed_twim_options >> 24) & 0xFF,
            "operations_address": f"0x{I2C_OPERATIONS:08x}",
            "operations": operation_pointers,
        },
        "gpio": {
            "ldo_enable": {
                "descriptor_address": f"0x{TOUCH_LDO_DESCRIPTOR:08x}",
                "name": names["ldo"],
                "pin": gpio(word(ldo, 8)),
                "configuration_raw": f"0x{word(ldo, 0x0C):08x}",
                "initial_value_raw": word(ldo, 0x10),
            },
            "ready_input": {
                "descriptor_address": f"0x{TOUCH_RDY_IN_DESCRIPTOR:08x}",
                "name": names["rdy_in"],
                "pin": gpio(word(rdy_in, 8)),
                "configuration_raw": f"0x{word(rdy_in, 0x0C):08x}",
                "pull_raw": rdy_in[0x0C],
                "polarity_raw": rdy_in[0x0D],
                "polarity": "high-to-low",
                "uses_high_accuracy_gpiote_channel": False,
                "uses_low_accuracy_port_event": True,
                "asserted_level": "low",
            },
            "ready_output": {
                "descriptor_address": f"0x{TOUCH_RDY_OUT_DESCRIPTOR:08x}",
                "name": names["rdy_out"],
                "pin": gpio(word(rdy_out, 8)),
                "configuration_raw": f"0x{word(rdy_out, 0x0C):08x}",
                "initial_value_raw": word(rdy_out, 0x10),
            },
            "ready_is_one_bidirectional_physical_line": True,
        },
        "service_lease": {
            "active_source_mask_runtime_offset": "touch state + 0x14",
            "known_source_ids": {
                "0": "glasses/wear and glasses touch switch",
                "2": "factory ATI diagnostic",
            },
            "first_acquire_posts_event": "0x00000002",
            "additional_or_duplicate_acquire_posts_event": None,
            "nonfinal_or_duplicate_release_posts_event": None,
            "final_release_synthesizes_touch_release": True,
            "final_release_posts_event": "0x00000004",
        },
        "hardware_open_sequence": [
            "acquire shared PMIC client bit 2",
            "schedule shared PMIC client-bit release with raw delay 0x800",
            "delay 1",
            "enable touch_ldo_en",
            "delay 10",
            "disarm/close touch_rdy_in",
            "open touch_rdy_out and drive high, then low",
            "delay 130",
            "drive touch_rdy_out high",
            "delay 10",
            "close touch_rdy_out",
            "delay 20",
            "open touch_rdy_in and arm its callback",
            "delay 20",
            "mark touch hardware active",
        ],
        "hardware_close_sequence": [
            "mark touch hardware inactive",
            "disarm/close touch_rdy_in",
            "disable touch_ldo_en",
            "open touch_rdy_out and drive low",
        ],
        "task_event_bits": {
            "0x000001": "RDY/IRQ worker",
            "0x000002": "hardware open",
            "0x000004": "hardware close",
            "0x000010": "ALP ATI error log only",
            "0x000020": "trackpad ATI error log only",
            "0x000040...0x000800": "six factory communication-end marker transactions",
            "0x400000": "separate deferred callback path",
            "0x800000": "fatal task/storage path",
        },
        "ready_interrupt": {
            "generic_gpio_dispatcher_address": "0x0006ed94",
            "registered_callback_address": "0x000933fc",
            "posted_task_event": "0x00000001",
            "task_thunk_address": "0x0008e7ac",
            "worker_address": "0x00051368",
            "worker_gates": [
                "ignore when touch service is inactive",
                "ignore when sampled RDY level is high/deasserted",
                "open i2c_0 only for an active-low assertion",
                "process the IQS7211E IRQ record",
                "close i2c_0 after processing",
            ],
            "factory_poll": {
                "initial_delay_raw": 40,
                "retry_delay_raw": 2,
                "maximum_level_reads": 100,
            },
        },
        "communication": {
            "config_register": "0x34",
            "production_config_word": "0x476c",
            "enabled_config_bits": [
                "trackpad touch event",
                "trackpad event",
                "gesture event",
                "event mode",
                "communication end command",
                "watchdog",
                "automatic ALP re-ATI",
                "automatic trackpad re-ATI",
            ],
            "disabled_config_bits": [
                "ALP event",
                "re-ATI event",
                "manual mode control",
                "communication request",
            ],
            "normal_irq_config_low_byte_refresh_frame": ["0x34", "0x6c"],
            "read_register_preamble_bytes": 1,
            "read_uses_repeated_start": True,
            "read_address_phase_timeout_raw": 500,
            "short_read_length_threshold_exclusive": 50,
            "short_read_data_phase_timeout_raw": 200,
            "long_read_data_phase_timeout_raw": 500,
            "maximum_write_data_bytes": 80,
            "normal_communication_end_frame": ["0xff"],
            "factory_communication_end_frames": [
                ["0xff", f"0x{value:02x}"] for value in range(1, 7)
            ],
            "factory_task_event_bits": [
                "0x000040",
                "0x000080",
                "0x000100",
                "0x000200",
                "0x000400",
                "0x000800",
            ],
            "factory_payload_values_are_end_markers_not_controller_commands": True,
        },
        "controller_recovery": {
            "system_control_register": "0x33",
            "normal_irq_worker_address": "0x00030e6c",
            "show_reset_flag": "0x0080",
            "show_reset_action": "rewrite the complete production configuration",
            "initializer_final_frame": [
                "0x33", "0xa0", "0x00", "0x6c", "0x47", "0x00", "0x00",
            ],
            "initializer_system_control_word": "0x00a0",
            "initializer_acknowledges_reset": True,
            "initializer_queues_trackpad_re_ati": True,
            "trackpad_re_ati_frame": ["0x33", "0x20", "0x00"],
            "trackpad_ati_error_task_event": "0x00000020",
            "consecutive_error_threshold_for_restart": 5,
            "consecutive_error_counter_saturates_at": 255,
            "maximum_hardware_restart_attempts": 3,
            "restart_close_task_event": "0x00000004",
            "restart_delay_raw": "0x66",
            "restart_log_delay_milliseconds": 100,
            "restart_timer_callback_address": "0x00046eac",
            "restart_timer_callback_clears_pending": True,
            "restart_timer_callback_open_task_event": "0x00000002",
            "successful_nonfactory_irq_clears_error_and_attempt_counters": True,
            "factory_marker_0x55_suppresses_recovery_and_counter_clear": True,
            "suspend": {
                "compiled_branch_address": "0x0002fdf8",
                "system_control_mask": "0x0800",
                "operation": "read register 0x33, OR bit 11, write register 0x33, then end communication",
                "initial_latch": False,
                "recovered_production_setter": False,
                "stock_reachability": "dormant/unproven",
            },
        },
        "connection_fast_mode": {
            "function_address": "0x0004e070",
            "deferred_callback_address": "0x000882ac",
            "classification": "BLE connection-parameter mode, not IQS7211E sensing/report mode",
            "callback_event_to_ble_thread_message": {
                "0": "0x40",
                "1": "0x10",
                "2": "0x20",
            },
            "set_fast_mode_cancels_events": [0, 1],
            "set_fast_mode_schedules_immediate_event": 2,
            "fast_observed_when_max_connection_interval_raw_below": 0x32,
            "observed_fast_equal_interval_values_raw": [0x24, 0x27],
        },
        "safety": {
            "static_parser_only": True,
            "live_gpio_or_i2c_sender_exposed": False,
            "stock_phone_protocol_exposes_raw_bus": False,
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
