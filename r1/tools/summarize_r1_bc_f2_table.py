#!/usr/bin/env python3
"""Decode the R1 channel-1 command 0xf2 dispatch table from startup RAM data."""

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


EXPECTED_SHA256 = "0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a"
TABLE_ADDRESS = 0x20006C60
TABLE_COUNT = 0x48

# Labels describe the immediate wrapper behavior proven by the decompile. Where the wrapped
# low-level hardware operation is not uniquely named, the label deliberately remains mechanical.
KNOWN: dict[int, dict[str, Any]] = {
    0x00: {"handler": 0x62D12, "operation": "PPG chip-ID probe", "response_bytes": 5},
    0x01: {"handler": 0x62CD0, "operation": "IMU chip-ID probe", "response_bytes": 5},
    0x02: {"handler": 0x62CFC, "operation": "PMIC chip-ID probe", "response_bytes": 5},
    0x03: {
        "handler": 0x62D54,
        "operation": "refresh and return cached battery millivolts",
        "response_bytes": 6,
    },
    0x04: {
        "handler": 0x62D28,
        "operation": "average two temperature-channel reads, then multiply by 100",
        "response_bytes": 8,
    },
    0x05: {
        "handler": 0x62DB0,
        "operation": "set device marker 0x5a then destructive ship-mode pulse",
        "response_bytes": 4,
    },
    0x06: {"handler": 0x62DD4, "operation": "destructive ship-mode pulse", "response_bytes": 4},
    0x08: {
        "handler": 0x62D84,
        "operation": "PPG factory mode select from payload bytes 4 and 5",
        "response_bytes": 4,
    },
    0x09: {
        "handler": 0x62D6A,
        "operation": "echo then delayed reset with reason 3",
        "response_bytes": 4,
    },
    0x12: {
        "handler": 0x62C90,
        "operation": "restart periodic factory timer",
        "response_bytes": None,
    },
    0x1B: {"handler": 0x62D3E, "operation": "touch-controller ID/readiness probe", "response_bytes": 5},
    0x1F: {"handler": 0x62CE6, "operation": "NFC chip-ID probe", "response_bytes": 5},
    0x2C: {
        "handler": 0x62C74,
        "operation": "two-channel trimmed/calibrated temperature sample",
        "response_bytes": "5 + 2 * payload[4] (normally 9)",
    },
    0x30: {
        "handler": 0x62C5E,
        "operation": "two-channel temperature chip-ID probe",
        "response_bytes": 10,
    },
    0x47: {
        "handler": 0x62C48,
        "operation": "NFC-rectifier raw ADC and separately sampled millivolts",
        "response_bytes": 8,
    },
}


def summarize(image_path: Path, base: int) -> dict[str, Any]:
    image = image_path.read_bytes()
    digest = hashlib.sha256(image).hexdigest()
    source_offset = mapped_offset(DEFAULT_SCATTER_SOURCE, base, len(image))
    runtime, consumed = decompress_scatter(
        image[source_offset:], DEFAULT_SCATTER_LENGTH
    )
    table_offset = TABLE_ADDRESS - DEFAULT_SCATTER_RUNTIME
    table_size = TABLE_COUNT * 4
    if table_offset < 0 or table_offset + table_size > len(runtime):
        raise ValueError("f2 table is outside the decompressed startup image")

    entries: list[dict[str, Any]] = []
    populated: list[int] = []
    for index in range(TABLE_COUNT):
        pointer = struct.unpack_from("<I", runtime, table_offset + index * 4)[0]
        entry: dict[str, Any] = {
            "subcommand": f"0x{index:02x}",
            "slot_address": f"0x{TABLE_ADDRESS + index * 4:08x}",
            "handler_thumb_pointer": f"0x{pointer:08x}" if pointer else None,
            "handler_entry": f"0x{pointer & ~1:08x}" if pointer else None,
            "populated": pointer != 0,
        }
        if pointer:
            populated.append(index)
            known = KNOWN.get(index)
            if known is None:
                raise ValueError(f"unexpected populated f2 slot 0x{index:02x}")
            if pointer != (known["handler"] | 1):
                raise ValueError(
                    f"slot 0x{index:02x}: got 0x{pointer:08x}, "
                    f"expected 0x{known['handler'] | 1:08x}"
                )
            entry.update(
                {key: value for key, value in known.items() if key != "handler"}
            )
        entries.append(entry)

    if set(populated) != set(KNOWN):
        raise ValueError("known/populated f2 slot sets do not match")

    return {
        "image": str(image_path),
        "image_bytes": len(image),
        "image_sha256": digest,
        "expected_image_sha256": EXPECTED_SHA256,
        "expected_image": digest == EXPECTED_SHA256,
        "load_base": f"0x{base:08x}",
        "scatter_source": f"0x{DEFAULT_SCATTER_SOURCE:08x}",
        "scatter_runtime": f"0x{DEFAULT_SCATTER_RUNTIME:08x}",
        "scatter_output_bytes": len(runtime),
        "scatter_input_bytes_consumed": consumed,
        "table_address": f"0x{TABLE_ADDRESS:08x}",
        "table_slots": TABLE_COUNT,
        "populated_count": len(populated),
        "null_count": TABLE_COUNT - len(populated),
        "populated_subcommands": [f"0x{index:02x}" for index in populated],
        "entries": entries,
    }


def parse_integer(value: str) -> int:
    return int(value, 0)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", type=Path)
    parser.add_argument("--base", type=parse_integer, default=DEFAULT_BASE)
    arguments = parser.parse_args()
    print(json.dumps(summarize(arguments.image, arguments.base), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
