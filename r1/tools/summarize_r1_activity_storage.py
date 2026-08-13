#!/usr/bin/env python3
"""Validate the production activity delta/cache/FIFO/daily-sync implementation.

This parser is static and read-only. It never connects to a ring, reads health storage, publishes
an internal event, invokes BLE, or mutates firmware.
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
from summarize_r1_gomore_input_abi import IMAGE_SHA256


RANGES = {
    (0x5A9F0, 0x5A9F8): "3a658f2b30ba9a8384bc0ea7fcc48fad958fdadb56c8f15199f87aeb3f92e8b7",
    (0x5A9F8, 0x5AA14): "8e633275adc195d1d021e26f5a8898c830c4d30a3fdbaf239e86eb06763eb68f",
    (0x5AA14, 0x5AB0A): "90c63f8ffa27c90d548d4f0bb7f1400cf354a3aa8833e3314a249a61d7ca7f82",
    (0x5AC74, 0x5ACA6): "8258898551d51a347e2dc9b680fdcd15334a7d92fcfc67700ba4e952ba2eff79",
    (0x48288, 0x482A6): "7beb2d39482a69e371adffb65b14a0df64ac2763595d5eb4961f7f4b5880ee2e",
    (0x482A8, 0x48324): "4ae6c99bb32b377253d86ace3629c39ecf7f12df7a381e527c4e58b05128c850",
    (0x4832C, 0x4834A): "8ff6f860f42ea830dae6f0cab97f770b3ae196e82a2775dc5ad4484e85a6bfc3",
    (0x8A64C, 0x8A718): "7ee68b0089bf6e2836055619fe34f5dc6baf3bae0e15842f2d5bf11c42b6ebb3",
    (0x3BDD8, 0x3BE66): "305cde7f9cb8be236cff6a630ec93abce98392eaba26f07e52e6eeea5c8fe0d2",
    (0x3BED0, 0x3BEDE): "67fcd7ee83d2e426bbcd020ef70acfadb2ebe130f7656d220a0e2f1ef25a049e",
    (0x3BEE4, 0x3BFD6): "99c1d053687332f6f6d9ab75132393c4ce1f7fb881760c2a9b843bd359c72fa5",
    (0x3C0D8, 0x3C1E8): "46e98644ffd3bd224644d25a0845fa0a88c22110c1930438947c4b2b94ffeb30",
    (0x3C304, 0x3C4AC): "1641cae24f8940cd20b32dc638dfe22f15cbeee4199338cdc73d41b302692f24",
    (0x3C578, 0x3C958): "1f6669508caf74812b07ee60766d6bee6878879ed98dc2e3b5cfc7a26352b4ea",
    (0x3C958, 0x3CB80): "927837c46aa145f9ca616b6cb97956258ce567609c98a9683b459e12aa4a0820",
    (0x3CB80, 0x3CCD0): "501b6e04eb30e5d453a207ccec3011893af67d76f68889d6a0783fb21925accb",
    (0x8BAEC, 0x8BE3C): "02c16956b74720e338b7251b88d6af0f2b9c11895b734f66e317de9c4c5df15e",
}

BRANCHES = {
    0x5A9F0: [0x3C362, 0x4828E, 0x482AE, 0x48332, 0x59F1C, 0x5A366, 0x8B25A],
    0x5AA14: [0x8A7FA],
    0x5AC74: [0x5AA22, 0x5AA2A],
    0x3BDD8: [0x3C1D4],
    0x3BED0: [0x3CB88, 0x8BC84, 0x8BDD6],
    0x3BEE4: [0x8A708],
    0x3C304: [0x8BE30],
    0x3C578: [0x3C498, 0x3CA7A, 0x3CC2A, 0x8BDD2, 0x8BE22],
    0x3CB80: [0x8BE1C],
    0x8A64C: [0x4830A],
    0x8BAEC: [0x8B170, 0x8BA58],
}

LITERALS = {
    0x5A9F4: 0x200166C4,
    0x5AA10: 0x200166C4,
    0x5AB68: 0x200166C4,
    0x48324: 946_080_000,
    0x48328: 0x003FF000,
    0x3BE68: 0x200067A8,
    0x3BE6C: 0x20015A6C,
    0x3C0D0: 0x20015A6C,
    0x3C0D4: 0x200067A8,
    0x3CCD0: 0x200067A8,
    0x3CCD4: 0x20015A6C,
    0x3CCD8: 0x003FF000,
    0x8A718: 946_080_000,
    0x8C048: 0x00099BF4,
    0x8C04C: 0x0003C0D9,
    0x8C0FC: 0x0003C959,
    0x8C100: 0x200067A8,
}

DESCRIPTOR_ADDRESS = 0x99C34
EXPECTED_DESCRIPTOR = bytes.fromhex("04180000a98204002d83040089820400")


def flash_bytes(image: bytes, base: int, start: int, end: int) -> bytes:
    offset = mapped_offset(start, base, len(image))
    return image[offset:offset + end - start]


def summarize(path: Path, base: int) -> dict[str, Any]:
    image = path.read_bytes()
    digest = hashlib.sha256(image).hexdigest()
    if digest != IMAGE_SHA256:
        raise ValueError(f"unexpected image sha256: {digest}")

    ranges = []
    for (start, end), wanted in RANGES.items():
        actual = hashlib.sha256(flash_bytes(image, base, start, end)).hexdigest()
        if actual != wanted:
            raise ValueError(f"range 0x{start:x}...0x{end:x}: {actual}")
        ranges.append({
            "start": f"0x{start:08x}",
            "end_exclusive": f"0x{end:08x}",
            "sha256": actual,
        })

    branches = {}
    for target, wanted in BRANCHES.items():
        actual = [address for address, _ in direct_thumb_branches_to(image, base, target)]
        if actual != wanted:
            raise ValueError(f"branches to 0x{target:x}: {actual}")
        branches[f"0x{target:08x}"] = [f"0x{address:08x}" for address in actual]

    literals = {}
    for address, wanted in LITERALS.items():
        actual = struct.unpack("<I", flash_bytes(image, base, address, address + 4))[0]
        if actual != wanted:
            raise ValueError(f"literal 0x{address:x}: 0x{actual:x}")
        literals[f"0x{address:08x}"] = f"0x{actual:08x}"

    descriptor = flash_bytes(
        image, base, DESCRIPTOR_ADDRESS, DESCRIPTOR_ADDRESS + len(EXPECTED_DESCRIPTOR)
    )
    if descriptor != EXPECTED_DESCRIPTOR:
        raise ValueError(f"activity descriptor: {descriptor.hex()}")

    return {
        "image": str(path),
        "image_sha256": digest,
        "load_base": f"0x{base:08x}",
        "verified_ranges": ranges,
        "direct_branches": branches,
        "literals": literals,
        "descriptor": {
            "address": f"0x{DESCRIPTOR_ADDRESS:08x}",
            "raw_hex": descriptor.hex(),
            "metric_index": 4,
            "hour_slot_bytes": 24,
            "callbacks_thumb": [
                f"0x{struct.unpack_from('<I', descriptor, offset)[0]:08x}"
                for offset in (4, 8, 12)
            ],
        },
        "delta_event": {
            "identifier": "0x000b",
            "bytes": 12,
            "fields": [
                "all_kcal UInt16LE",
                "active_kcal UInt16LE",
                "steps UInt16LE",
                "duration_seconds UInt16LE",
                "timestamp UInt32LE",
            ],
            "selected_bucket": "local ten-minute bucket(timestamp-duration)",
            "cross_bucket_split": False,
            "field_wrap_bits": [10, 10, 12],
            "storage_notification": None,
        },
        "cache": {
            "address": "0x200166c4",
            "bytes": 584,
            "packed_words": 144,
            "hours": 24,
            "words_per_hour": 6,
            "packed_fields": "steps[11:0], active_kcal[21:12], all_kcal[31:22]",
            "utc_offset_offset": "0x240",
            "reserved_offset": "0x242",
            "local_day_start_offset": "0x244",
            "reset_preserves_reserved_u16": True,
            "stock_index_bounds": False,
        },
        "offline_queue": {
            "metadata_address": "0x200067a8",
            "storage_address": "0x20015a6c",
            "capacity": 144,
            "entry_bytes": 16,
            "entry_fields": [
                "packed UInt32LE",
                "day UInt32LE",
                "recorded_timestamp UInt32LE",
                "utc_offset Int16LE",
                "absolute_bucket UInt8",
                "retained byte",
            ],
            "full_policy": "overwrite oldest",
            "ack_policy": "consume oldest timestamp prefix",
            "repeated_bucket_merge": "last value, one packet item",
        },
        "sync": {
            "automatic_phone_route": True,
            "flash_backfill_limit_seconds": 259_200,
            "day_builder_bytes": 0x49C,
            "daily_packet_prefix_bytes": 7,
            "daily_item_bytes": 7,
            "ack_modes": {"0": "flash cursor", "1": "offline FIFO", "2": "RAM cursor"},
            "clock_sampled_before_every_ack_mode": True,
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
