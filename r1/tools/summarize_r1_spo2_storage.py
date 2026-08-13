#!/usr/bin/env python3
"""Validate exact SpO2 consumer, cache, invalid-clock FIFO, merge, and ACK boundaries."""

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
    (0x0005BAEC, 0x0005BAF0): "06936d0536d64e86c623270163a043c1b484bbc978af8fbf56cd1650cbfb6587",
    (0x0005BAF4, 0x0005BB10): "da6a43bd3e679596d98d487f6b16e95f14d398b5f308b78819e58d56f18c65ee",
    (0x0005BB14, 0x0005BB28): "fcc1bfdaee98ac75b1b172b5e944d20fccd163a39ce9d30ee2f5f1f4be195e4a",
    (0x0005BB2C, 0x0005BC0C): "219518df0374821451f370f079250c5b9c0f2e59a3ea7218a7e84b0d7d0ef19d",
    (0x0008A8AE, 0x0008A8D8): "5bc8f850dcfdeb2d7ec55fc779f0a92b7e3061c21c9c5267f819d1a38cdfe824",
    (0x00090DD4, 0x00090DEE): "0fc63dc6ade30c59fe37b1c6f9fd6fd4f416986d8e245f9badcaf77f4070a79f",
    (0x00090DF0, 0x00090E48): "dd590d0b7f810c1abd350573b42dbf593194b73873a54ad743b2151e4af9e928",
    (0x00090E4C, 0x00090E66): "150e1b53fd4eb585b73557fbbdd9921ed3657099d4cbe1a3683854ef0e43966a",
    (0x0008E27C, 0x0008E32E): "5ada8559cd5f877d362125d31c99b92948d37fa10f4348a341a35d7afafaa0d7",
    (0x00043CA0, 0x00043D2E): "721cbb521d61f9b7cecca16dc4fe7c5931b34f3c0117c87927ae63475d356aee",
    (0x00043D90, 0x00043D9E): "67fcd7ee83d2e426bbcd020ef70acfadb2ebe130f7656d220a0e2f1ef25a049e",
    (0x00043DA4, 0x00043E5E): "985d0a3f09c6adc8f3ca7141ddf28c1bb7f0441028fc63c01ea5fbf0152cd61f",
    (0x00043EB0, 0x00043FC0): "0acb6155808c2b7799476c43871f8a2ec38a81abed7ff6f90008277d8cbc383e",
    (0x000448B0, 0x000449E2): "5e41ad37d48c08635e372cc2364c04a98d05ac117d82ff481c286141e72ba591",
    (0x0008CD60, 0x0008D0AC): "7828072e528c65a3f363768717ae2907681b96d1ce5dad7afbb95dd9e497ff89",
}

EXPECTED_BRANCHES = {
    0x0005BAF4: [0x0008E538],
    0x0005BB14: [0x0008E54E],
    0x0005BB2C: [0x0008A8CC],
    0x0008A8AE: [0x00042972],
    0x0008E27C: [0x00090E3C],
    0x00043CA0: [0x00043FAC],
    0x00043D90: [0x000448B8, 0x0008CEF8, 0x0008D046],
    0x00043DA4: [0x0008E326],
    0x000448B0: [0x0008D08C],
    0x0008CD60: [0x0008B164, 0x0008B9AC],
}

EXPECTED_LITERALS = {
    0x0005BAF0: 0x200165A0,
    0x0005BB10: 0x200165A0,
    0x0005BB28: 0x200165A0,
    0x0005BC0C: 0x200165A0,
    0x00090E48: 0x38640900,
    0x0008E330: 0x38640900,
    0x00043D30: 0x2000679B,
    0x00043D34: 0x200158EC,
    0x00043DA0: 0x2000679B,
    0x00043EA8: 0x200158EC,
    0x00043EAC: 0x2000679B,
    0x000449E4: 0x2000679B,
    0x000449E8: 0x200158EC,
    0x0008D294: 0x00043EB1,
    0x0008D338: 0x2000679B,
}

DESCRIPTOR_ADDRESS = 0x00099C04
EXPECTED_DESCRIPTOR = bytes.fromhex("01030000f10d09004d0e0900d50d0900")


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
    branches: dict[str, list[str]] = {}
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
        raise ValueError(f"unexpected SpO2 descriptor: {descriptor.hex()}")
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
            "consumer": "0x0008a8ae",
            "minimum_accepted": 70,
            "consumer_upper_bound": None,
            "timestamp_always_replaced": True,
            "notification_metric": 1,
            "aggregate": "0x0005bb2c",
            "two_independent_hour_calls": True,
            "cache_address": "0x200165a0",
            "cache_bytes": 84,
            "layout": {
                "24_byte_aggregate_slots": "0x00...0x47",
                "signed_offset_minutes": "0x48...0x49",
                "reserved": "0x4a",
                "latest_point": "0x4b...0x4f",
                "local_day_start": "0x50...0x53",
            },
            "latest_requires_nonzero_value": True,
            "rolling_accumulator_address": "0x20016650",
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
            "metadata_address": "0x2000679b",
            "entry_storage_address": "0x200158ec",
            "capacity": 24,
            "entry_bytes": 16,
            "entry_layout": {
                "aggregate": "0x00...0x02",
                "retained": "0x03",
                "day_start": "0x04...0x07",
                "recorded_timestamp": "0x08...0x0b",
                "signed_offset": "0x0c...0x0d",
                "hour": "0x0e",
                "retained_tail": "0x0f",
            },
            "full_overwrites_oldest": True,
            "ack_consumes_contiguous_oldest_prefix": True,
            "merge_overwrites_repeated_hour": True,
        },
        "acknowledgement": {
            "callback": "0x00043eb0",
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
