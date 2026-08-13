#!/usr/bin/env python3
"""Validate exact HR consumer, cache, invalid-clock FIFO, merge, and ACK boundaries."""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
from pathlib import Path
from typing import Any

from summarize_r1_adc_registry import DEFAULT_BASE, mapped_offset
from summarize_r1_gomore_call_graph import direct_thumb_branches_to
from summarize_r1_gomore_input_abi import IMAGE_SHA256


EXPECTED_RANGES = {
    (0x0005ACE0, 0x0005ACE4): "06936d0536d64e86c623270163a043c1b484bbc978af8fbf56cd1650cbfb6587",
    (0x0005ACE8, 0x0005AD04): "da6a43bd3e679596d98d487f6b16e95f14d398b5f308b78819e58d56f18c65ee",
    (0x0005AD08, 0x0005AD5C): "0149c2804e41a0e3d8a4935fa0628005b3480a93cc4a2d5f83452b14f0a117b3",
    (0x0005AD90, 0x0005AE6C): "2c2faf5817d9b459a42b0fb8469dfef737174aae0c0a3dfa9733d002bdd58dab",
    (0x0008A80A, 0x0008A83E): "7b38604669ced28aadd46d2798772ae71ed7dd3c7c5d9da3e792c9f9a7bff681",
    (0x0007062C, 0x00070646): "800b62608919a88d0cf34db07455c4335237a43b0d3c61f89af5e52982df5936",
    (0x00070648, 0x000706A0): "7f98fbcbc10c0d7564e6dca198497fb89e47e4c4882a713b08c766d7acfdd106",
    (0x000706A4, 0x000706BE): "ae498d295638441c1a6f46b46f4e31320b43cbcf4a6a8bb7b04a324ed887893b",
    (0x0008D538, 0x0008D5EC): "523334879827eebd879df9015d20b95d9e748080ae1a8e5562f521e578db0240",
    (0x0003FAA4, 0x0003FB32): "601f73cde8a7bc1adf460265ed653eb26608827570cc74647704745b96b54487",
    (0x0003FB90, 0x0003FBA0): "7b3c871d659d3e40a7214bf77fc23ac5c53de132f7f8318e8c63da6b9168ac6f",
    (0x0003FBA4, 0x0003FCE4): "1a218b1d3e5a80d23dcb67af6328502a513765b563c6c400338649bde1ad9d5b",
    (0x0003FCEC, 0x0003FDFA): "26846ce90cc075edcf4edbf705178fd6378c2ee4c7cf17612a13c02d59cce71a",
    (0x00040700, 0x00040832): "71aa183edeaf3bad5f358b853dd3c5d632bf694fea4a474fb9de946a14ea273d",
    (0x0008C150, 0x0008C49A): "dc1285911c51765504381c8177ca54c9619b9fe44c59ed063fac6e9d477d3c3f",
}

EXPECTED_BRANCHES = {
    0x0005ACE8: [0x0008D6C0],
    0x0005AD08: [0x0008D534],
    0x0005AD90: [0x0008A832],
    0x0008A80A: [0x0004289E],
    0x0008D538: [0x00070694],
    0x0003FAA4: [0x0003FDE6],
    0x0003FB90: [0x00040708, 0x0008C2E8, 0x0008C434],
    0x0003FBA4: [0x0008D5E2],
    0x00040700: [0x0008C47A],
    0x0008C150: [0x0008B15E, 0x0008B95C],
}

EXPECTED_LITERALS = {
    0x0005ACE4: 0x2001654C,
    0x0005AD04: 0x2001654C,
    0x0005AD5C: 0x2001654C,
    0x0005AE6C: 0x2001654C,
    0x000706A0: 0x38640900,
    0x0008D5EC: 0x38640900,
    0x0003FB34: 0x20006798,
    0x0003FB38: 0x2001576C,
    0x0003FBA0: 0x20006798,
    0x0003FCE4: 0x2001576C,
    0x0003FCE8: 0x20006798,
    0x00040834: 0x20006798,
    0x00040838: 0x2001576C,
    0x0008C670: 0x0003FCED,
    0x0008C70C: 0x20006798,
}

DESCRIPTOR_ADDRESS = 0x00099BF4
EXPECTED_DESCRIPTOR = bytes.fromhex("0003000049060700a50607002d060700")


def flash_bytes(image: bytes, base: int, start: int, end: int) -> bytes:
    offset = mapped_offset(start, base, len(image))
    return image[offset:offset + end - start]


def summarize(image_path: Path, base: int) -> dict[str, Any]:
    image = image_path.read_bytes()
    digest = hashlib.sha256(image).hexdigest()
    if digest != IMAGE_SHA256:
        raise ValueError(f"unexpected image SHA-256: {digest}")
    ranges = []
    for (start, end), expected in EXPECTED_RANGES.items():
        actual = hashlib.sha256(flash_bytes(image, base, start, end)).hexdigest()
        if actual != expected:
            raise ValueError(f"unexpected range 0x{start:08x}...0x{end:08x}: {actual}")
        ranges.append({"start": f"0x{start:08x}", "end_exclusive": f"0x{end:08x}", "sha256": actual})
    branches = {}
    for target, expected in EXPECTED_BRANCHES.items():
        actual = [address for address, _ in direct_thumb_branches_to(image, base, target)]
        if actual != expected:
            raise ValueError(f"unexpected branches to 0x{target:08x}: {actual}")
        branches[f"0x{target:08x}"] = [f"0x{address:08x}" for address in actual]
    literals = {}
    for address, expected in EXPECTED_LITERALS.items():
        actual = struct.unpack("<I", flash_bytes(image, base, address, address + 4))[0]
        if actual != expected:
            raise ValueError(f"unexpected literal at 0x{address:08x}: 0x{actual:08x}")
        literals[f"0x{address:08x}"] = f"0x{actual:08x}"
    descriptor = flash_bytes(image, base, DESCRIPTOR_ADDRESS, DESCRIPTOR_ADDRESS + 16)
    if descriptor != EXPECTED_DESCRIPTOR:
        raise ValueError(f"unexpected HR descriptor: {descriptor.hex()}")
    return {
        "image": str(image_path),
        "image_sha256": digest,
        "load_base": f"0x{base:08x}",
        "verified_ranges": ranges,
        "direct_branches": branches,
        "literals": literals,
        "descriptor": {
            "address": f"0x{DESCRIPTOR_ADDRESS:08x}",
            "raw_hex": descriptor.hex(),
            "metric_index": descriptor[0],
            "slot_bytes": descriptor[1],
            "callbacks_thumb": [
                f"0x{struct.unpack_from('<I', descriptor, offset)[0]:08x}"
                for offset in (4, 8, 12)
            ],
        },
        "consumer_and_cache": {
            "consumer": "0x0008a80a",
            "accepted_range": [40, 220],
            "timestamp_zero_filled_nonzero_preserved": True,
            "notification_metric": 0,
            "aggregate": "0x0005ad90",
            "two_independent_hour_calls": True,
            "cache_address": "0x2001654c",
            "cache_bytes": 84,
            "rolling_accumulator_address": "0x20016648",
            "latest_requires_nonzero_value": True,
        },
        "invalid_clock_path": {
            "cutoff": 946_080_000,
            "signed_offset_loaded_as_uint16": True,
            "negative_300_minutes_becomes_hours": 1087,
            "three_independent_clock_reads": True,
            "nonzero_early_slot_always_redacted": True,
            "stock_callback_index_bounds": False,
        },
        "unsynced_queue": {
            "metadata_address": "0x20006798",
            "entry_storage_address": "0x2001576c",
            "capacity": 24,
            "entry_bytes": 16,
            "retained_offsets": [3, 15],
            "full_overwrites_oldest": True,
            "ack_consumes_contiguous_oldest_prefix": True,
            "merge_overwrites_repeated_hour": True,
        },
        "acknowledgement": {
            "callback": "0x0003fcec",
            "clock_sampled_before_mode_switch": True,
            "mode_1_consumes_queue_without_cursor_update": True,
            "modes_0_and_2_update_nonfuture_newer_cursor": True,
        },
        "safety": {
            "executes_firmware": False,
            "physical_device_access": False,
            "ble_access": False,
            "sensor_access": False,
            "flash_writes": False,
            "health_store_access": False,
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
