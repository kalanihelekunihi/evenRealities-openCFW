#!/usr/bin/env python3
"""Validate and summarize R1 global-health enablement and the GoMore module/resource gate.

This is static, read-only analysis for application 2.2.6.0009. It emits topology and policy only:
no captured health values, settings write, private event, or worker-control action is performed.
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
    decompress_scatter,
    mapped_offset,
)


GOMORE_STATE = 0x20006DA0
MODULE_DESCRIPTOR_OFFSET = 0x24
MODULE_DESCRIPTOR_BYTES = 0x10
MODULE_COUNT = 7
EXPECTED_DEPENDENCY_MASKS = [0x02, 0x1E, 0x1E, 0x02, 0x04, 0x0C, 0x00]

FUNCTION_SIGNATURES = {
    # Registered system 01/00/0e handler. Its method bit selects the read path below or the
    # set path at 0x83fc4; keeping the common entry pinned avoids treating the latter as a
    # separate protocol handler.
    0x00083F24: "2de9f041804648790e4640f340014748474a0027801ac00803228ab002eb0045",
    0x00073868: "70b50e4d8eb00e46044634226946286800f05af89df81800",  # dev_info bit/timestamp
    0x00042122: "c0b207f0eaba",                                      # event 0x100d thunk
    0x000496FC: "70b5040001d0012500e0002547f0f0fec00703d147f0ecfe",  # normalize/update
    0x0008F6F8: "1cb504460020009069460190d9f72efc9df8050050b10020a04206d084f00100",
    0x00068F64: "1cb50c460246074841f2301100680144684609f0ebfa0098",  # provider read +0x1130
    0x0008ED10: "10b50146044841f2301200681044e3f7",                  # provider write +0x1130
    0x00049410: "f8b50f467d4c7e497e4a2378891acd0863b1072808d204f1",  # module gate
    0x0006AAE8: "084a002002eb001109788b0703d5c90701d00120",          # acc dependency scan
    0x0006AB60: "084a002002eb001109784b0703d5c90701d00120",          # raw_hr scan
    0x0006AB10: "084a002002eb001109780b0703d5c90701d00120",          # hr scan
    0x0006AB38: "084a002002eb00110978cb0603d5c90701d00120",          # hrv scan
    0x0006AD04: "0749002001eb00121278d20701d000207047401c",          # any-active scan
}

CALLSITE_SIGNATURES = {
    # Read response construction: zero 12 bytes, copy the persisted timestamp to bytes 0...3,
    # copy the health byte to byte 4, then explicitly zero bytes 5...11 before transmission.
    0x00083F48: "0697079705a902a80897eff721fc059806909df808008df81c00cdf81d70adf821708df82370",
    # Compare requested health byte with stored byte, persist normalized bit/timestamp, publish 100d.
    0x0008402E: "20799df80c108842c2d0216800b10120eff713fc0122211d41f20d0009f057fc",
    # Normalize and update persistent active-low state, then gate modules 0 and 3.
    0x00049744: "284645f0d7ff29460020fff75ffe2946bde870400320fff7",
    # Known module-index call sites: activity 0, stress 1, sleep-stage PPG 4, HR/HRV 5.
    0x00048DE6: "0121002000f011fbbde81040",
    0x0004B33E: "01460120fef765b8",
    0x0004C388: "00210420fdf740f80748",
    0x00049B26: "01210520fff771fc0020",
    # The common gate uses the any-active scan and a 1,000 ms idle/tick timer.
    0x00049578: "21f0c4fb254a244b03219a1ad2084ff0406701eb024608b1a06918b121f0b6fbd8b134e000224ff47a71374840f0e0fe",
}

POINTER_WORDS = {
    # System registration table entry 01/00/0e at 0x9a524.
    0x0009A524: 0x0000000E,
    0x0009A528: 0x00083F25,
    0x0004960C: GOMORE_STATE,
    0x00049650: 0x0006B115,
    0x00049660: 0x0006B229,
    0x0004966C: 0x0006B1B9,
    0x00049670: 0x0006B1F5,
    0x00049680: 0x0006ACA5,
}

WORKER_NAMES = {
    0x0004965C: b"acc\0",
    0x00049664: b"raw_hr\0",
    0x00049668: b"hr\0",
    0x00049674: b"hrv\0",
}


def flash_bytes(image: bytes, base: int, address: int, length: int) -> bytes:
    offset = mapped_offset(address, base, len(image))
    return image[offset:offset + length]


def flash_word(image: bytes, base: int, address: int) -> int:
    return struct.unpack("<I", flash_bytes(image, base, address, 4))[0]


def require_prefix(image: bytes, base: int, address: int, expected_hex: str) -> None:
    expected = bytes.fromhex(expected_hex)
    actual = flash_bytes(image, base, address, len(expected))
    if actual != expected:
        raise ValueError(
            f"unexpected bytes at 0x{address:08x}: {actual.hex()} != {expected.hex()}"
        )


def runtime_byte(runtime: bytes, runtime_base: int, address: int) -> int:
    offset = address - runtime_base
    if offset < 0 or offset >= len(runtime):
        raise ValueError(f"runtime byte 0x{address:08x} is outside scatter image")
    return runtime[offset]


def summarize(
    image_path: Path,
    base: int,
    scatter_source: int,
    scatter_runtime: int,
    scatter_length: int,
) -> dict[str, Any]:
    image = image_path.read_bytes()
    for address, signature in FUNCTION_SIGNATURES.items():
        require_prefix(image, base, address, signature)
    for address, signature in CALLSITE_SIGNATURES.items():
        require_prefix(image, base, address, signature)
    for address, expected in POINTER_WORDS.items():
        actual = flash_word(image, base, address)
        if actual != expected:
            raise ValueError(
                f"unexpected pointer at 0x{address:08x}: 0x{actual:08x} != 0x{expected:08x}"
            )
    for address, expected in WORKER_NAMES.items():
        actual = flash_bytes(image, base, address, len(expected))
        if actual != expected:
            raise ValueError(
                f"unexpected worker name at 0x{address:08x}: {actual!r} != {expected!r}"
            )

    source_offset = mapped_offset(scatter_source, base, len(image))
    runtime, consumed = decompress_scatter(image[source_offset:], scatter_length)
    dependency_masks = [
        runtime_byte(
            runtime,
            scatter_runtime,
            GOMORE_STATE + MODULE_DESCRIPTOR_OFFSET + index * MODULE_DESCRIPTOR_BYTES,
        )
        for index in range(MODULE_COUNT)
    ]
    if dependency_masks != EXPECTED_DEPENDENCY_MASKS:
        raise ValueError(
            f"unexpected GoMore module masks: {dependency_masks} != {EXPECTED_DEPENDENCY_MASKS}"
        )

    semantics = [
        "activity",
        "stress",
        "unresolved compiled slot",
        "sleep baseline",
        "sleep-stage PPG",
        "heart-rate/HRV timing",
        "unresolved compiled slot",
    ]
    worker_bits = ((1, "acc"), (2, "raw_hr"), (3, "hr"), (4, "hrv"))
    modules = []
    for index, mask in enumerate(dependency_masks):
        modules.append({
            "index": index,
            "semantic": semantics[index],
            "initial_active": bool(mask & 1),
            "dependency_mask_raw": mask & 0x1E,
            "workers": [name for bit, name in worker_bits if mask & (1 << bit)],
        })

    return {
        "image": str(image_path),
        "image_bytes": len(image),
        "image_sha256": hashlib.sha256(image).hexdigest(),
        "load_base": f"0x{base:08x}",
        "scatter": {
            "source": f"0x{scatter_source:08x}",
            "compressed_end": f"0x{scatter_source + consumed:08x}",
            "runtime": f"0x{scatter_runtime:08x}",
            "runtime_bytes": len(runtime),
        },
        "public_health_setting": {
            "module": "0x01",
            "command": "0x00",
            "subcommand": "0x0e",
            "registration_entry": "0x0009a524",
            "handler": "0x00083f24",
            "read_response_bytes": 12,
            "read_response_timestamp_range": "0...3",
            "read_response_health_byte_offset": 4,
            "read_response_zero_reserved_range": "5...11",
            "read_response_shape_static_verified": True,
            "set_payload_health_byte_offset": 4,
            "first_party_payload_bytes": 12,
            "set_ack_precedes_persistence_and_effect_attempt": True,
            "public_handler_persists_dev_info_health_bit_and_timestamp": True,
            "publishes_internal_event_only_when_raw_byte_changes": True,
            "internal_event": "0x100d",
            "internal_nonzero_values_normalize_to_enabled": True,
        },
        "global_health_effect": {
            "active_low_provider_block_offset": "0x1135",
            "enabled_provider_byte": 0,
            "disabled_provider_byte": 1,
            "gomore_module_indices_set_to_normalized_state": [0, 3],
            "gomore_module_semantics": ["activity", "sleep baseline"],
            "gomore_auth_must_be_initialized_for_module_gate": True,
        },
        "gomore_module_gate": {
            "runtime_state": f"0x{GOMORE_STATE:08x}",
            "module_count": MODULE_COUNT,
            "descriptor_bytes": MODULE_DESCRIPTOR_BYTES,
            "active_bit": 0,
            "dependency_bits": {"1": "acc", "2": "raw_hr", "3": "hr", "4": "hrv"},
            "modules": modules,
            "workers_are_reference_counted_across_active_modules": True,
            "idle_tick_timer_ms_while_any_module_active": 1_000,
            "idle_tick_timer_removed_when_all_modules_inactive": True,
        },
        "safety": {
            "static_parser_only": True,
            "captured_health_values_emitted": False,
            "public_setting_is_state_changing_and_power_sensitive": True,
            "private_event_sender_exposed": False,
            "raw_module_gate_sender_exposed": False,
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
