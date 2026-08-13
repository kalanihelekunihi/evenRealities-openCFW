#!/usr/bin/env python3
"""Validate the internal R1 direct/estimated heart-rate selector.

This version-pinned static parser connects the host direct-HR input to the internal selector,
validates its one-byte state, exact output record, validity constants, and downstream-only routing.
It never reads live SRAM, starts a worker, or injects physiological data.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
from pathlib import Path
from typing import Any

from summarize_r1_adc_registry import DEFAULT_BASE, mapped_offset
from summarize_r1_gomore_call_graph import direct_thumb_branches_to
from summarize_r1_gomore_input_abi import FIELDS as INPUT_FIELDS, IMAGE_SHA256
from summarize_r1_gomore_output_abi import FIELDS as OUTPUT_FIELDS


EXPECTED_RANGE_SHA256 = {
    (0x000605DC, 0x00060660):
        "b95ad80db5161c33b6998d221caf574b67ee23558effc8093fb0162a6649a772",
    (0x0007170A, 0x00071712):
        "71901dacf0e9d57b7c001d4c0609c5b9fdd0667f5892fac5eb68ba0a693ac4fa",
    (0x00071714, 0x000717A2):
        "3112c51e53dd2e756960eb870445b953280183300cc7b70a3c5ae25fc74940af",
    (0x00094590, 0x00094694):
        "e0ec2adb814118836f143c52750a75bc91ffc913845942ddab6de0f7f9a82fb8",
    (0x0005F3D8, 0x0005F4B6):
        "4d4ed646ba3e8cad56053fe854ab539f026a8f0371ae59ce066d246c54b2f581",
    (0x0005FF94, 0x000605DA):
        "316edbabcbe75e09edbfc16176e77aa0e6938e21ba63199015b0f1f47ee993c1",
}

EXPECTED_DIRECT_BRANCHES = {
    0x000605DC: [0x000601E4, 0x000601F6],
    0x0007170A: [0x00071A84],
    0x0005F3D8: [0x0006018C, 0x0006019C],
}

SELECTOR_DIAGNOSTIC = "[inhr]=%f [enhr]=%f\r\n"
VALIDITY_ADDEND_BITS = 0xBDE00000
VALIDITY_UNSIGNED_LIMIT = 0x01500001


def flash_bytes(image: bytes, base: int, start: int, end: int) -> bytes:
    offset = mapped_offset(start, base, len(image))
    return image[offset:offset + (end - start)]


def c_string(image: bytes, base: int, address: int) -> str:
    offset = mapped_offset(address, base, len(image))
    return image[offset:image.index(b"\0", offset)].decode("ascii")


def summarize(image_path: Path, base: int) -> dict[str, Any]:
    image = image_path.read_bytes()
    digest = hashlib.sha256(image).hexdigest()
    if digest != IMAGE_SHA256:
        raise ValueError(f"unexpected image SHA-256: {digest}")

    verified_ranges = []
    for (start, end), expected in EXPECTED_RANGE_SHA256.items():
        actual = hashlib.sha256(flash_bytes(image, base, start, end)).hexdigest()
        if actual != expected:
            raise ValueError(
                f"unexpected HR-selector range 0x{start:08x}...0x{end:08x}: {actual}"
            )
        verified_ranges.append({
            "start": f"0x{start:08x}",
            "end_exclusive": f"0x{end:08x}",
            "sha256": actual,
        })

    branches: dict[str, list[str]] = {}
    for target, expected in EXPECTED_DIRECT_BRANCHES.items():
        actual = [address for address, _ in direct_thumb_branches_to(image, base, target)]
        if actual != expected:
            raise ValueError(
                f"unexpected branches to 0x{target:08x}: {actual} != {expected}"
            )
        branches[f"0x{target:08x}"] = [f"0x{address:08x}" for address in actual]

    diagnostic = c_string(image, base, 0x00060660)
    if diagnostic != SELECTOR_DIAGNOSTIC:
        raise ValueError(f"unexpected HR-selector diagnostic: {diagnostic!r}")
    addend_bits, zero_bits = struct.unpack(
        "<II", flash_bytes(image, base, 0x00060678, 0x00060680)
    )
    if addend_bits != VALIDITY_ADDEND_BITS or zero_bits != 0:
        raise ValueError(
            f"unexpected HR-selector literals: 0x{addend_bits:08x}, 0x{zero_bits:08x}"
        )

    direct_fields = [field for field in INPUT_FIELDS if field["io_offset"] == 0x28]
    if direct_fields != [{
        "io_offset": 0x28,
        "width": 4,
        "storage": "float32",
        "semantic": "direct_heart_rate",
        "writer": "heart_rate_callback",
        "consumption": "every_update",
    }]:
        raise ValueError(f"unexpected direct-HR input ABI: {direct_fields}")

    selected_record_engine_bytes = set(range(0x104, 0x10D))
    copied_engine_bytes = {
        byte
        for field in OUTPUT_FIELDS
        for byte in range(field["engine_offset"], field["engine_offset"] + field["width"])
    }
    if selected_record_engine_bytes & copied_engine_bytes:
        raise ValueError("internal selected-HR record unexpectedly entered copied host ABI")

    return {
        "image": str(image_path),
        "image_sha256": digest,
        "load_base": f"0x{base:08x}",
        "diagnostic": diagnostic,
        "selector": {
            "function": "0x000605dc",
            "state_engine_offset": "0x0c54",
            "state_bytes": 1,
            "state_initializer": "0x0007170a",
            "initialized_state": 0,
            "state_is_written_by_selector": False,
            "elapsed_argument_is_used": False,
            "direct_input_engine_offset": "0x002c",
            "direct_input_host_io_offset": "0x0028",
            "estimated_input_engine_offset": "0x00f8",
            "estimated_input_layout": {
                "heart_rate_float32": 0,
                "quality_float32": 4,
                "bytes": 8,
            },
            "selected_record_engine_offset": "0x0104",
            "selected_record_layout": {
                "heart_rate_float32": 0,
                "quality_float32": 4,
                "source_uint8": 8,
                "bytes": 9,
            },
            "validity": {
                "raw_unsigned_expression":
                    "(float32_bits + 0xbde00000) mod 2^32 < 0x01500001",
                "finite_positive_equivalent_bpm": {
                    "minimum_inclusive": 40.0,
                    "maximum_inclusive": 240.0,
                },
            },
            "priority": [
                "direct input when valid and state byte is zero",
                "estimated candidate when valid",
                "unavailable",
            ],
            "outputs": {
                "direct": {"source_code": 0, "quality": 1.0},
                "estimated": {"source_code": 1, "quality": "copied losslessly"},
                "unavailable": {"source_code": 0x40, "heart_rate": 0.0, "quality": 0.0},
            },
        },
        "stock_provenance": {
            "engine_initializer_zeroes_estimated_input": True,
            "immediately_preceding_motion_stage_writes_engine_f0_and_f4_only": True,
            "estimated_input_producer_recovered": False,
            "stock_state_keeps_direct_input_enabled": True,
            "selected_record_is_copied_to_host": False,
            "selected_record_is_consumed_by_downstream_energy_and_health_stages": True,
        },
        "verified_ranges": verified_ranges,
        "direct_branches": branches,
        "safety": {
            "live_sram_read": False,
            "worker_start": False,
            "input_injection": False,
            "firmware_write": False,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", type=Path)
    parser.add_argument("--base", type=lambda value: int(value, 0), default=DEFAULT_BASE)
    args = parser.parse_args()
    print(json.dumps(summarize(args.image, args.base), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
