#!/usr/bin/env python3
"""Validate every production call into the R1 GoMore shared-resource gate.

This static parser decodes Thumb-2 direct branches to gate 0x49410, verifies the exact argument
setup at every call site, and checks the scatter-initialized module descriptors. It never runs the
firmware, changes a health setting, starts a worker, or emits captured health data.
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


GATE_ADDRESS = 0x00049410
STATE_ADDRESS = 0x20006DA0
DESCRIPTOR_OFFSET = 0x24
DESCRIPTOR_BYTES = 0x10
EXPECTED_DESCRIPTOR_HEX = [
    "02000000000000000000000000000000",
    "1e000000000000000000000000000000",
    "1e000000000000000000000000000000",
    "02000000000000000000000000000000",
    "04000000000000000000000000000000",
    "0c000000000000000000000000000000",
    "00000000000000000000000000000000",
]

# Context begins before the branch so the argument registers and conditional state are pinned.
EXPECTED_CALLSITES = {
    0x00048DEA: {
        "context": (0x00048DE6, "0121002000f011fb"),
        "module": 0,
        "request": "enable",
        "purpose": "activity initialization while global health is enabled",
    },
    0x0004974E: {
        "context": (0x0004974A, "29460020fff75ffe"),
        "module": 0,
        "request": "propagate global-health state",
        "purpose": "global-health transition",
    },
    0x0004975A: {
        "context": (0x00049752, "2946bde870400320fff759be"),
        "module": 3,
        "request": "propagate global-health state",
        "purpose": "global-health transition",
    },
    0x00049B2A: {
        "context": (0x00049B26, "01210520fff771fc"),
        "module": 5,
        "request": "enable",
        "purpose": "heart-rate/SpO2 timing start",
    },
    0x00049CB4: {
        "context": (0x00049CB0, "00210520fff7acfb"),
        "module": 5,
        "request": "disable",
        "purpose": "heart-rate timing timeout",
    },
    0x00049DA0: {
        "context": (0x00049D9C, "00210520fff736bb"),
        "module": 5,
        "request": "disable",
        "purpose": "heart-rate wear-status cleanup",
    },
    0x0004A5A2: {
        "context": (0x0004A59E, "01210320fef735ff"),
        "module": 3,
        "request": "enable",
        "purpose": "sleep-baseline initialization",
    },
    0x0004A8DE: {
        "context": (0x0004A8DA, "01210520fef797fd"),
        "module": 5,
        "request": "enable",
        "purpose": "sleep-liveness probe start",
    },
    0x0004A908: {
        "context": (0x0004A904, "00210520fef782fd"),
        "module": 5,
        "request": "disable",
        "purpose": "sleep-liveness probe startup rollback",
    },
    0x0004A9EC: {
        "context": (0x0004A9E8, "00210520fef710fd"),
        "module": 5,
        "request": "disable",
        "purpose": "sleep-liveness probe stop",
    },
    0x0004B342: {
        "context": (0x0004B33E, "01460120fef765b8"),
        "module": 1,
        "request": "propagate requested state",
        "purpose": "stress measurement control",
    },
    0x0004C38C: {
        "context": (0x0004C388, "00210420fdf740f8"),
        "module": 4,
        "request": "disable",
        "purpose": "GoMore health-index reinitialization cleanup",
    },
    0x0006B1E4: {
        "context": (0x0006B1E0, "00210520def714b9"),
        "module": 5,
        "request": "disable",
        "purpose": "heart-rate worker result",
    },
    0x0006B552: {
        "context": (0x0006B54E, "00210420ddf75dff"),
        "module": 4,
        "request": "disable",
        "purpose": "sleep force-awake cleanup",
    },
    0x0006C438: {
        "context": (0x0006C430, "002100e001210420dcf7eaff"),
        "module": 4,
        "request": "toggle to requested sleep-stage state",
        "purpose": "sleep-stage PPG transition",
    },
}


def flash_bytes(image: bytes, base: int, address: int, length: int) -> bytes:
    offset = mapped_offset(address, base, len(image))
    return image[offset:offset + length]


def direct_thumb_branches_to(image: bytes, base: int, target: int) -> list[tuple[int, str]]:
    """Decode Thumb-2 BL/B.W immediates and return every exact branch target match."""
    hits: list[tuple[int, str]] = []
    for offset in range(0, len(image) - 3, 2):
        first, second = struct.unpack_from("<HH", image, offset)
        if first & 0xF800 != 0xF000:
            continue
        if second & 0xD000 == 0xD000:
            kind = "BL"
        elif second & 0xD000 == 0x9000:
            kind = "B.W"
        else:
            continue
        sign = (first >> 10) & 1
        j1 = (second >> 13) & 1
        j2 = (second >> 11) & 1
        i1 = 1 - (j1 ^ sign)
        i2 = 1 - (j2 ^ sign)
        immediate = (
            (sign << 24)
            | (i1 << 23)
            | (i2 << 22)
            | ((first & 0x03FF) << 12)
            | ((second & 0x07FF) << 1)
        )
        if sign:
            immediate -= 1 << 25
        address = base + offset
        if address + 4 + immediate == target:
            hits.append((address, kind))
    return hits


def summarize(
    image_path: Path,
    base: int,
    scatter_source: int,
    scatter_runtime: int,
    scatter_length: int,
) -> dict[str, Any]:
    image = image_path.read_bytes()
    branches = direct_thumb_branches_to(image, base, GATE_ADDRESS)
    branch_addresses = [address for address, _ in branches]
    expected_addresses = sorted(EXPECTED_CALLSITES)
    if branch_addresses != expected_addresses:
        raise ValueError(
            f"unexpected GoMore gate branches: {branch_addresses} != {expected_addresses}"
        )

    for callsite in EXPECTED_CALLSITES.values():
        address, expected_hex = callsite["context"]
        expected = bytes.fromhex(expected_hex)
        actual = flash_bytes(image, base, address, len(expected))
        if actual != expected:
            raise ValueError(
                f"unexpected call context at 0x{address:08x}: "
                f"{actual.hex()} != {expected.hex()}"
            )

    source_offset = mapped_offset(scatter_source, base, len(image))
    runtime, consumed = decompress_scatter(image[source_offset:], scatter_length)
    descriptor_start = STATE_ADDRESS + DESCRIPTOR_OFFSET - scatter_runtime
    descriptor_hex = [
        runtime[
            descriptor_start + index * DESCRIPTOR_BYTES:
            descriptor_start + (index + 1) * DESCRIPTOR_BYTES
        ].hex()
        for index in range(len(EXPECTED_DESCRIPTOR_HEX))
    ]
    if descriptor_hex != EXPECTED_DESCRIPTOR_HEX:
        raise ValueError(
            f"unexpected GoMore descriptors: {descriptor_hex} != {EXPECTED_DESCRIPTOR_HEX}"
        )

    pointer_needles = (
        struct.pack("<I", GATE_ADDRESS),
        struct.pack("<I", GATE_ADDRESS | 1),
    )
    pointer_locations = sorted(
        base + offset
        for needle in pointer_needles
        for offset in range(len(image))
        if image.startswith(needle, offset)
    )
    if pointer_locations:
        raise ValueError(f"unexpected literal gate function pointers: {pointer_locations}")

    callsites = []
    counts = {index: 0 for index in range(7)}
    kind_by_address = dict(branches)
    for address in expected_addresses:
        expected = EXPECTED_CALLSITES[address]
        counts[expected["module"]] += 1
        callsites.append({
            "address": f"0x{address:08x}",
            "branch_kind": kind_by_address[address],
            "module_index": expected["module"],
            "request": expected["request"],
            "purpose": expected["purpose"],
        })

    dormant = [index for index, count in counts.items() if count == 0]
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
        "gomore_gate": {
            "address": f"0x{GATE_ADDRESS:08x}",
            "direct_static_callsite_count": len(callsites),
            "literal_function_pointer_locations": [],
            "callsites": callsites,
            "callsite_count_by_module": {str(index): counts[index] for index in counts},
        },
        "module_descriptors": {
            "runtime_address": f"0x{STATE_ADDRESS + DESCRIPTOR_OFFSET:08x}",
            "descriptor_bytes": DESCRIPTOR_BYTES,
            "initial_raw_hex": descriptor_hex,
            "initial_callback_words_are_zero": True,
            "slots_without_static_callers": dormant,
            "unreferenced_slot_2_dependency_mask": "0x1e",
            "unreferenced_slot_6_dependency_mask": "0x00",
        },
        "interpretation": {
            "slot_0": "activity",
            "slot_1": "stress",
            "slot_2": "compiled descriptor with no production caller",
            "slot_3": "sleep baseline",
            "slot_4": "sleep-stage PPG",
            "slot_5": "timed optical measurements including HR/SpO2 and sleep liveness",
            "slot_6": "compiled descriptor with no production caller",
        },
        "safety": {
            "static_parser_only": True,
            "workers_started": False,
            "health_settings_changed": False,
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
