#!/usr/bin/env python3
"""Decode the production R1 scatter image and summarize its nRF52840 ADC registry."""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
from pathlib import Path
from typing import Any


DEFAULT_BASE = 0x27000
DEFAULT_SCATTER_SOURCE = 0xC4610
DEFAULT_SCATTER_RUNTIME = 0x200064A8
DEFAULT_SCATTER_LENGTH = 0x195C
DEFAULT_REGISTRY = 0x20006EF8
DEFAULT_COUNT = 3
RECORD_SIZE = 0x28

INPUTS = {
    0: ("disconnected", None),
    1: ("AIN0", "P0.02"),
    2: ("AIN1", "P0.03"),
    3: ("AIN2", "P0.04"),
    4: ("AIN3", "P0.05"),
    5: ("AIN4", "P0.28"),
    6: ("AIN5", "P0.29"),
    7: ("AIN6", "P0.30"),
    8: ("AIN7", "P0.31"),
    9: ("VDD", None),
}
GAINS = ["1/6", "1/5", "1/4", "1/3", "1/2", "1", "2", "4"]
ACQUISITION_MICROSECONDS = [3, 5, 10, 15, 20, 40]


def mapped_offset(address: int, base: int, image_size: int) -> int:
    offset = address - base
    if offset < 0 or offset >= image_size:
        raise ValueError(f"address 0x{address:08x} is outside the image")
    return offset


def c_string(image: bytes, address: int, base: int, maximum: int = 128) -> str:
    start = mapped_offset(address, base, len(image))
    end = image.find(b"\0", start, min(len(image), start + maximum + 1))
    if end < 0:
        raise ValueError(f"unterminated string at 0x{address:08x}")
    return image[start:end].decode("ascii")


def decompress_scatter(source: bytes, output_length: int) -> tuple[bytes, int]:
    """Mirror firmware function 0x286f4's bounded zero/back-reference decoder."""
    cursor = 0
    output = bytearray()
    while len(output) < output_length:
        if cursor >= len(source):
            raise ValueError("compressed scatter input ended early")
        tag = source[cursor]
        cursor += 1
        literal_code = tag & 0x07
        if literal_code == 0:
            if cursor >= len(source):
                raise ValueError("missing extended literal count")
            literal_code = source[cursor]
            cursor += 1
        run_length = tag >> 4
        if run_length == 0:
            if cursor >= len(source):
                raise ValueError("missing extended run length")
            run_length = source[cursor]
            cursor += 1

        literal_length = literal_code - 1
        if literal_length < 0 or cursor + literal_length > len(source):
            raise ValueError("invalid literal run")
        output.extend(source[cursor:cursor + literal_length])
        cursor += literal_length

        if tag & 0x08:
            if cursor >= len(source):
                raise ValueError("missing back-reference distance")
            distance = source[cursor]
            cursor += 1
            if distance == 0 or distance > len(output):
                raise ValueError(f"invalid back-reference distance {distance}")
            for _ in range(run_length + 2):
                output.append(output[-distance])
        else:
            output.extend(b"\0" * run_length)
        if len(output) > output_length:
            raise ValueError("scatter run exceeds requested output length")
    return bytes(output), cursor


def input_summary(raw: int) -> dict[str, Any]:
    if raw not in INPUTS:
        raise ValueError(f"unknown SAADC input selector {raw}")
    name, gpio = INPUTS[raw]
    return {"raw": raw, "name": name, "gpio": gpio}


def configuration_summary(fields: bytes) -> dict[str, Any]:
    if len(fields) != 7:
        raise ValueError("SAADC configuration requires seven fields")
    positive_resistor, negative_resistor, gain, reference, acquisition, mode, burst = fields
    if gain >= len(GAINS) or acquisition >= len(ACQUISITION_MICROSECONDS):
        raise ValueError("SAADC configuration has an unknown enum value")
    raw = (
        (positive_resistor & 0x03)
        | (negative_resistor & 0x03) << 4
        | (gain & 0x07) << 8
        | (reference & 0x01) << 12
        | (acquisition & 0x07) << 16
        | (mode & 0x01) << 20
        | (burst & 0x01) << 24
    )
    return {
        "raw_register": f"0x{raw:08x}",
        "positive_resistor_raw": positive_resistor,
        "negative_resistor_raw": negative_resistor,
        "gain_raw": gain,
        "gain": GAINS[gain],
        "reference_raw": reference,
        "reference": "internal 0.6 V" if reference == 0 else "VDD/4",
        "acquisition_time_raw": acquisition,
        "acquisition_time_microseconds": ACQUISITION_MICROSECONDS[acquisition],
        "mode_raw": mode,
        "mode": "single-ended" if mode == 0 else "differential",
        "burst_raw": burst,
        "burst": bool(burst),
    }


def summarize(
    image_path: Path,
    base: int,
    scatter_source: int,
    scatter_runtime: int,
    scatter_length: int,
    registry_address: int,
    count: int,
) -> dict[str, Any]:
    image = image_path.read_bytes()
    source_offset = mapped_offset(scatter_source, base, len(image))
    runtime, consumed = decompress_scatter(image[source_offset:], scatter_length)
    registry_offset = registry_address - scatter_runtime
    if registry_offset < 0 or registry_offset + count * RECORD_SIZE > len(runtime):
        raise ValueError("ADC registry is outside the decompressed scatter image")

    records: list[dict[str, Any]] = []
    for index in range(count):
        record_address = registry_address + index * RECORD_SIZE
        record = runtime[
            registry_offset + index * RECORD_SIZE:
            registry_offset + (index + 1) * RECORD_SIZE
        ]
        name_pointer = struct.unpack_from("<I", record)[0]
        name = c_string(image, name_pointer, base)
        source_selector = record[5]
        # Function 0x54864 copies byte +5 to byte +0x0d before passing record +6 to
        # function 0x7aeac, making it param_2[7]/PSELP. PSELN is record byte +0x0e.
        effective_positive_selector = source_selector
        effective_negative_selector = record[14]
        records.append({
            "index": index,
            "record_address": f"0x{record_address:08x}",
            "record_hex": record.hex(),
            "name": name,
            "name_pointer": f"0x{name_pointer:08x}",
            "open_flag_initial": record[4],
            "source_selector_byte": source_selector,
            "saadc_channel": index,
            "positive_input": input_summary(effective_positive_selector),
            "negative_input": input_summary(effective_negative_selector),
            "configuration": configuration_summary(record[6:13]),
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
        "registry_address": f"0x{registry_address:08x}",
        "record_size": RECORD_SIZE,
        "record_count": count,
        "records": records,
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
    parser.add_argument("--registry-address", type=parse_integer, default=DEFAULT_REGISTRY)
    parser.add_argument("--count", type=int, default=DEFAULT_COUNT)
    arguments = parser.parse_args()
    if arguments.count <= 0:
        parser.error("--count must be positive")
    print(json.dumps(summarize(
        arguments.image,
        arguments.base,
        arguments.scatter_source,
        arguments.scatter_runtime,
        arguments.scatter_length,
        arguments.registry_address,
        arguments.count,
    ), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
