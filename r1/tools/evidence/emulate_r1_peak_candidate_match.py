#!/usr/bin/env python3
"""Assert the stock 0x64380 peak-candidate matching contract."""

from __future__ import annotations

import argparse
import json
import struct
from pathlib import Path
from typing import Any

from emulate_r1_locomotion_window import LocomotionFirmwareFixture, RAM_BASE


PEAK_CANDIDATE_MATCH = 0x00064380
SIGNAL = RAM_BASE + 0x60000
CANDIDATES = RAM_BASE + 0x61000
REFERENCES = RAM_BASE + 0x61100
CANDIDATE_COUNT = RAM_BASE + 0x61200
REFERENCE_COUNT = RAM_BASE + 0x61210
MEDIAN = RAM_BASE + 0x61220
WORKSPACE = RAM_BASE + 0x61300


def run_fixture(
    image: bytes,
    candidates: list[int],
    references: list[int],
    candidate_values: list[float],
    valleys: list[int],
) -> dict[str, Any]:
    machine = LocomotionFirmwareFixture(image)
    signal = [10.0] * 250
    for position, value in zip(candidates, candidate_values):
        signal[position] = value
    for position in valleys:
        signal[position] = 0.0
    machine.uc.mem_write(SIGNAL, struct.pack("<250f", *signal))
    machine.uc.mem_write(
        CANDIDATES, bytes(candidates) + bytes([0xA5]) * (20 - len(candidates))
    )
    machine.uc.mem_write(
        REFERENCES, bytes(references) + bytes([0xA5]) * (20 - len(references))
    )
    machine.uc.mem_write(CANDIDATE_COUNT, bytes([len(candidates)]))
    machine.uc.mem_write(REFERENCE_COUNT, bytes([len(references)]))
    machine.uc.mem_write(MEDIAN, b"\xa5" * 4)
    machine.uc.mem_write(WORKSPACE, b"\xa5" * 100)
    result = machine.call(
        PEAK_CANDIDATE_MATCH,
        SIGNAL, CANDIDATES, REFERENCES, CANDIDATE_COUNT,
        REFERENCE_COUNT, MEDIAN, WORKSPACE,
    )
    candidate_count = bytes(machine.uc.mem_read(CANDIDATE_COUNT, 1))[0]
    reference_count = bytes(machine.uc.mem_read(REFERENCE_COUNT, 1))[0]
    median_bits = struct.unpack(
        "<I", bytes(machine.uc.mem_read(MEDIAN, 4))
    )[0]
    return {
        "return": result,
        "candidate_count": candidate_count,
        "reference_count": reference_count,
        "candidates": list(machine.uc.mem_read(CANDIDATES, candidate_count)),
        "references": list(machine.uc.mem_read(REFERENCES, reference_count)),
        "median_spacing_bits": f"0x{median_bits:08x}",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", type=Path)
    args = parser.parse_args()
    image = args.image.read_bytes()

    regular = [20, 40, 60, 80]
    valleys = [12, 32, 52, 72]
    valley_recovery = run_fixture(
        image, regular, regular, [10.0] * 4, valleys
    )
    assert valley_recovery == {
        "return": 0,
        "candidate_count": 4,
        "reference_count": 4,
        "candidates": regular,
        "references": valleys,
        "median_spacing_bits": "0x41a00000",
    }

    aligned_reference = run_fixture(
        image, regular, [18, 38, 58, 78], [10.0] * 4, []
    )
    assert aligned_reference["return"] == 0
    assert aligned_reference["candidates"] == regular
    assert aligned_reference["references"] == [18, 38, 58, 78]
    assert aligned_reference["median_spacing_bits"] == "0x41a00000"

    outlier_filter = run_fixture(
        image, [20, 40, 60, 80, 100], [20, 40, 60, 80, 100],
        [1.0, 2.0, 3.0, 4.0, 100.0], valleys,
    )
    assert outlier_filter["return"] == 0
    assert outlier_filter["candidate_count"] == 4
    assert outlier_filter["candidates"] == regular
    assert outlier_filter["references"] == valleys
    assert outlier_filter["median_spacing_bits"] == "0x41a00000"

    insufficient = run_fixture(image, [20], [20], [10.0], [12])
    assert insufficient == {
        "return": 1,
        "candidate_count": 0,
        "reference_count": 0,
        "candidates": [],
        "references": [],
        "median_spacing_bits": "0x00000000",
    }

    print(json.dumps({
        "function": "0x00064380",
        "valley_recovery": valley_recovery,
        "aligned_reference": aligned_reference,
        "outlier_filter": outlier_filter,
        "insufficient_candidates": insufficient,
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
