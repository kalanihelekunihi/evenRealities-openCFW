#!/usr/bin/env python3
"""Decode the production R1 IQS7211E ring-size calibration registry."""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
from pathlib import Path
from typing import Any

from summarize_r1_adc_registry import decompress_scatter, mapped_offset


DEFAULT_BASE = 0x27000
DEFAULT_SCATTER_SOURCE = 0xC4610
DEFAULT_SCATTER_RUNTIME = 0x200064A8
DEFAULT_SCATTER_LENGTH = 0x195C
DEFAULT_POINTER_TABLE = 0x20007760
RING_SIZES = range(6, 16)
RECORD_SIZE = 0x1E
LAYOUTS = (
    (
        "eight_transmit_by_three_receive",
        8,
        24,
        [2, 6, 3, 5, 8, 7, 11, 0, 9, 12, 1, 11, 12],
    ),
    (
        "seven_transmit_by_three_receive",
        7,
        21,
        [2, 6, 3, 5, 8, 7, 11, 0, 9, 1, 10, 11, 12],
    ),
)


def image_slice(image: bytes, address: int, length: int, base: int) -> bytes:
    offset = mapped_offset(address, base, len(image))
    end = offset + length
    if end > len(image):
        raise ValueError(f"range 0x{address:08x}+0x{length:x} exceeds the image")
    return image[offset:end]


def summarize(
    image_path: Path,
    base: int,
    scatter_source: int,
    scatter_runtime: int,
    scatter_length: int,
    pointer_table: int,
) -> dict[str, Any]:
    image = image_path.read_bytes()
    source_offset = mapped_offset(scatter_source, base, len(image))
    runtime, consumed = decompress_scatter(image[source_offset:], scatter_length)
    table_offset = pointer_table - scatter_runtime
    pointer_count = len(LAYOUTS) * len(RING_SIZES)
    pointer_bytes = pointer_count * 4
    if table_offset < 0 or table_offset + pointer_bytes > len(runtime):
        raise ValueError("touch calibration pointer table is outside the scatter image")

    layouts: list[dict[str, Any]] = []
    for layout_index, (
        name,
        transmit_count,
        channel_count,
        mapping_slots,
    ) in enumerate(LAYOUTS):
        records: list[dict[str, Any]] = []
        for ring_index, ring_size in enumerate(RING_SIZES):
            pointer_index = layout_index * len(RING_SIZES) + ring_index
            record_pointer = struct.unpack_from(
                "<I", runtime, table_offset + pointer_index * 4
            )[0]
            record = image_slice(image, record_pointer, RECORD_SIZE, base)
            if record[1] != 0 or record[29] != 0:
                raise ValueError(
                    f"unexpected record padding for {name}, ring size {ring_size}"
                )
            minimum_trim_index = record[3]
            maximum_trim_index = record[4]
            if maximum_trim_index <= minimum_trim_index:
                raise ValueError(
                    f"invalid trim span for {name}, ring size {ring_size}"
                )
            channel_slots = list(record[5:29])
            active_channels = [
                channel for channel in channel_slots[:channel_count] if channel != 0xff
            ]
            expected_active_channels = list(range(
                minimum_trim_index * 3,
                (maximum_trim_index + 1) * 3,
            ))
            if active_channels != expected_active_channels:
                raise ValueError(
                    f"unexpected active-channel range for {name}, ring size {ring_size}"
                )
            if any(channel != 0xff for channel in channel_slots[channel_count:]):
                raise ValueError(
                    f"unused channel slot is active for {name}, ring size {ring_size}"
                )

            cycles: list[dict[str, Any]] = []
            for cycle_index in range(21):
                prox_a: int | None = None
                prox_b: int | None = None
                if cycle_index < transmit_count * 2:
                    transmit_index = cycle_index // 2
                    slot_offset = transmit_index * 3
                    if cycle_index % 2 == 0:
                        prox_a_raw = channel_slots[slot_offset]
                        prox_b_raw = channel_slots[slot_offset + 1]
                    else:
                        prox_a_raw = channel_slots[slot_offset + 2]
                        prox_b_raw = 0xff
                    prox_a = None if prox_a_raw == 0xff else prox_a_raw
                    prox_b = None if prox_b_raw == 0xff else prox_b_raw
                if prox_a is not None and prox_a % 3 not in (0, 2):
                    raise ValueError("ProxA allocation uses a ProxB-mapped receive channel")
                if prox_b is not None and prox_b % 3 != 1:
                    raise ValueError("ProxB allocation uses a ProxA-mapped receive channel")
                cycles.append({
                    "cycle_index": cycle_index,
                    "prox_a_channel_index": prox_a,
                    "prox_b_channel_index": prox_b,
                })

            records.append({
                "ring_size": ring_size,
                "record_address": f"0x{record_pointer:08x}",
                "record_hex": record.hex(),
                "raw_bytes": list(record),
                "default_trackpad_ati_compensation_divider": record[0],
                "trackpad_fine_fractional_divider": record[2],
                "minimum_trim_index": minimum_trim_index,
                "maximum_trim_index": maximum_trim_index,
                "trim_span": maximum_trim_index - minimum_trim_index,
                "active_channel_indices": active_channels,
                "cycle_allocations": cycles,
            })
        layouts.append({
            "layout": name,
            "transmit_electrode_count": transmit_count,
            "receive_electrode_count": 3,
            "channel_count": channel_count,
            "pointer_table_address": f"0x{pointer_table + layout_index * 0x28:08x}",
            "rx_tx_mapping_slots": mapping_slots,
            "receive_electrode_indices": mapping_slots[:3],
            "transmit_electrode_indices": mapping_slots[3:3 + transmit_count],
            "mapping_register_payload_hex": bytes(mapping_slots + [0]).hex(),
            "records": records,
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
        "pointer_table_address": f"0x{pointer_table:08x}",
        "record_size": RECORD_SIZE,
        "coordinate_units_per_trim_index_float32": 213.3333282470703,
        "scaled_coordinate_maximum": 200,
        "layouts": layouts,
    }


def parse_integer(value: str) -> int:
    return int(value, 0)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", type=Path)
    parser.add_argument("--base", type=parse_integer, default=DEFAULT_BASE)
    parser.add_argument(
        "--scatter-source", type=parse_integer, default=DEFAULT_SCATTER_SOURCE
    )
    parser.add_argument(
        "--scatter-runtime", type=parse_integer, default=DEFAULT_SCATTER_RUNTIME
    )
    parser.add_argument(
        "--scatter-length", type=parse_integer, default=DEFAULT_SCATTER_LENGTH
    )
    parser.add_argument(
        "--pointer-table", type=parse_integer, default=DEFAULT_POINTER_TABLE
    )
    arguments = parser.parse_args()
    print(json.dumps(summarize(
        arguments.image,
        arguments.base,
        arguments.scatter_source,
        arguments.scatter_runtime,
        arguments.scatter_length,
        arguments.pointer_table,
    ), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
