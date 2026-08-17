#!/usr/bin/env python3
"""Validate and summarize the R1 stored-sleep synchronization/ACK lifecycle.

This parser is static and read-only. It validates application 2.2.6.0009, emits no captured
sleep values, and exposes no BLE, flash-write, erase, or synchronization-marker command.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
from pathlib import Path
from typing import Any

from summarize_r1_gomore_call_graph import direct_thumb_branches_to
from summarize_r1_adc_registry import (
    DEFAULT_BASE,
    DEFAULT_SCATTER_LENGTH,
    DEFAULT_SCATTER_RUNTIME,
    DEFAULT_SCATTER_SOURCE,
    decompress_scatter,
    mapped_offset,
)
from summarize_r1_gomore_input_abi import IMAGE_SHA256


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_IMAGE = ROOT / "research/decompilation/rebuild/rebuilt-application.bin"


STORAGE_EVENT_DISPATCH_BASE = 0x200066FC
SLEEP_WRITE_EVENT = 0x2000
SLEEP_MARKER_EVENT = 0x2001
SLEEP_CRC_ERROR_EVENT = 0x2002
ACK_CONTEXT_BYTES = 12
SYNCHRONIZED_MARKER = 0x11223344

R1_SLEEP_SYNC_REPORT_FUNCTIONS = ({
    "entry": 0x0008F954,
    "end_exclusive": 0x0008F9CA,
    "size": 118,
    "symbol": "r1_sleep_sync_plan_report_callback",
    "role": "stored-record synchronization skip and packet-builder dispatch policy",
    "sha256": "32061a5ba2b5791a49e9f0590a8c4b41dcc597f4494ef2264374be6c71ad3edb",
    "callers": (),
    "registered_pointer": 0x0008B830,
    "inventory": "manual_provenance_supplement",
    "provider_family": "r1_product_specific",
    "source_disposition": "clean_room_behavior_only",
},)

FUNCTION_SIGNATURES = {
    0x0005B39C: "2de9f74f754a764894b0101ac0080122",  # skip-synchronized iterator
    0x0005B6F4: "2de9f047374b384a88b09a1ad2080123",  # checked marker writer
    0x000836BA: "2de9fe439946ddf8288016460c460500",  # phone send without callback
    0x00083704: "2de9ff5f9a46dde90e4b91460d460600",  # phone send + ACK callback
    0x0008DA24: "2de9ff4f867f044606eb4600203083b0",  # compact-to-phone expansion
    0x0008E1E0: "10b520b119b1bde81040cdf783ba03f0",  # event 0x2001 consumer
    0x0008F780: "2de9fc410400354835494ff08067a0eb",  # transport ACK callback
    0x0008F954: "feb50c4606461d0007d03078012805d0",  # iterator/report callback
    0x00042BCA: "4bf009bb",                          # event consumer thunk
    0x0008D888: "70b58188c5688ab20189901e8cb240f6",  # task event dispatcher
    0x0008D8FC: "2de9f04188460446401e40f6fe7186b0",  # internal event publisher
}

REQUIRED_DIAGNOSTICS = (
    b"sleep sync alloc ack ctx fail\0",
    b"sleep sync send failed: %d-%d\0",
    b"sleep sync ack ctx is null\0",
    b"sleep sync ack msg send fail\0",
    b"sleep sync ack ok: head=0x%08X, start=%u, end=%u\0",
    b"sleep storage write synchronize to head fail:%d\0",
)


def flash_bytes(image: bytes, base: int, address: int, length: int) -> bytes:
    offset = mapped_offset(address, base, len(image))
    return image[offset:offset + length]


def require_prefix(image: bytes, base: int, address: int, expected_hex: str) -> None:
    expected = bytes.fromhex(expected_hex)
    actual = flash_bytes(image, base, address, len(expected))
    if actual != expected:
        raise ValueError(
            f"unexpected bytes at 0x{address:08x}: {actual.hex()} != {expected.hex()}"
        )


def flash_word(image: bytes, base: int, address: int) -> int:
    return struct.unpack("<I", flash_bytes(image, base, address, 4))[0]


def runtime_word(runtime: bytes, runtime_base: int, address: int) -> int:
    offset = address - runtime_base
    if offset < 0 or offset + 4 > len(runtime):
        raise ValueError(f"runtime word 0x{address:08x} is outside scatter image")
    return struct.unpack_from("<I", runtime, offset)[0]


def summarize(
    image_path: Path,
    base: int,
    scatter_source: int,
    scatter_runtime: int,
    scatter_length: int,
) -> dict[str, Any]:
    image = image_path.read_bytes()
    image_digest = hashlib.sha256(image).hexdigest()
    if image_digest != IMAGE_SHA256:
        raise ValueError(f"unexpected recovered application image: {image_digest}")
    for address, prefix in FUNCTION_SIGNATURES.items():
        require_prefix(image, base, address, prefix)
    for diagnostic in REQUIRED_DIAGNOSTICS:
        if diagnostic not in image:
            raise ValueError(f"missing expected diagnostic {diagnostic[:-1]!r}")

    source_offset = mapped_offset(scatter_source, base, len(image))
    runtime, consumed = decompress_scatter(image[source_offset:], scatter_length)
    dispatch_words = [
        runtime_word(runtime, scatter_runtime, STORAGE_EVENT_DISPATCH_BASE + index * 4)
        for index in range(8)
    ]
    expected_dispatch_words = [
        0, 0x00042BC7, 0x00042BCB, 0x00042BC3,
        0x00042BB1, 0x00042B21, 0x00042BBF, 0,
    ]
    if dispatch_words != expected_dispatch_words:
        raise ValueError("unexpected storage event dispatch table")
    if dispatch_words[1 + SLEEP_MARKER_EVENT - 0x2000] != 0x00042BCB:
        raise ValueError("event 0x2001 does not resolve to the sleep-marker consumer thunk")
    if flash_word(image, base, 0x0005B61C) != SYNCHRONIZED_MARKER:
        raise ValueError("unexpected sleep synchronization marker")
    if flash_word(image, base, 0x0008DC08) != 0x0008F781:
        raise ValueError("unexpected stored-sleep ACK callback pointer")

    report_function = R1_SLEEP_SYNC_REPORT_FUNCTIONS[0]
    report_entry = int(report_function["entry"])
    report_body = flash_bytes(
        image, base, report_entry, int(report_function["size"])
    )
    report_callers = tuple(direct_thumb_branches_to(image, base, report_entry))
    registered_pointer = int(report_function["registered_pointer"])
    if len(report_body) != int(report_function["size"]) or \
            hashlib.sha256(report_body).hexdigest() != report_function["sha256"] or \
            report_callers != report_function["callers"] or \
            flash_word(image, base, registered_pointer) != report_entry + 1:
        raise ValueError("stored-sleep report callback closure changed")

    return {
        "image": str(image_path),
        "image_bytes": len(image),
        "image_sha256": image_digest,
        "load_base": f"0x{base:08x}",
        "scatter_source": f"0x{scatter_source:08x}",
        "scatter_compressed_end": f"0x{scatter_source + consumed:08x}",
        "scatter_runtime": f"0x{scatter_runtime:08x}",
        "request_and_send": {
            "iterator": "0x0005b39c",
            "iterator_skips_marker_0x11223344": True,
            "maximum_stored_payload_bytes": 232,
            "report_callback": "0x0008f954",
            "phone_expander": "0x0008da24",
            "protocol_model_identifier": "0x0601",
            "send_with_registered_callback": "0x00083704",
            "registered_callback_thumb": "0x0008f781",
        },
        "report_callback": {
            "entry": "0x0008f954",
            "end_exclusive": "0x0008f9ca",
            "size": report_function["size"],
            "sha256": report_function["sha256"],
            "symbol": report_function["symbol"],
            "direct_callers": [],
            "registered_pointer": "0x0008b830",
            "registered_thumb_value": "0x0008f955",
            "null_context_returns_false": True,
            "synchronization_flag_1_skips_send": True,
            "other_flags_invoke_packet_builder": True,
            "context_layout": [
                "report type UInt8 @0",
                "alignment/reserved UInt8 @1",
                "stage count UInt16LE @2",
            ],
        },
        "acknowledgement": {
            "callback": "0x0008f780",
            "private_context_bytes": ACK_CONTEXT_BYTES,
            "private_context_layout": [
                "absolute record-header flash address UInt32LE @0",
                "copied start timestamp UInt32LE @4",
                "copied end timestamp UInt32LE @8",
            ],
            "context_is_phone_visible": False,
            "callback_publishes_internal_event": f"0x{SLEEP_MARKER_EVENT:04x}",
            "callback_frees_context_after_publish_attempt": True,
            "send_or_callback_registration_failure_marks_record": False,
        },
        "marker_commit": {
            "storage_event_dispatch": {
                f"0x{SLEEP_WRITE_EVENT:04x}": f"0x{dispatch_words[1]:08x}",
                f"0x{SLEEP_MARKER_EVENT:04x}": f"0x{dispatch_words[2]:08x}",
                f"0x{SLEEP_CRC_ERROR_EVENT:04x}": f"0x{dispatch_words[3]:08x}",
            },
            "event_consumer": "0x0008e1e0",
            "marker_writer": "0x0005b6f4",
            "marker_value": "0x11223344",
            "marker_header_offset": 20,
            "batch_item_bytes": ACK_CONTEXT_BYTES,
            "batch_count_expression": "low8(byte_count / 12)",
            "maximum_nonwrapping_batch_items": 255,
            "stale_slot_guard": (
                "read the current 24-byte header and require both stored start/end timestamps "
                "to equal the copied ACK context before writing the marker"
            ),
            "crc_revalidated_at_commit": False,
            "payload_revalidated_at_commit": False,
        },
        "safety": {
            "static_parser_only": True,
            "captured_sleep_values_emitted": False,
            "absolute_partition_address_is_runtime_dependent": True,
            "offline_reconciler_is_non_mutating": True,
            "live_internal_event_sender_exposed": False,
            "live_flash_marker_sender_exposed": False,
            "delayed_ack_protection_supported": True,
        },
    }


def parse_integer(value: str) -> int:
    return int(value, 0)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", nargs="?", type=Path, default=DEFAULT_IMAGE)
    parser.add_argument("--base", type=parse_integer, default=DEFAULT_BASE)
    parser.add_argument("--scatter-source", type=parse_integer, default=DEFAULT_SCATTER_SOURCE)
    parser.add_argument("--scatter-runtime", type=parse_integer, default=DEFAULT_SCATTER_RUNTIME)
    parser.add_argument("--scatter-length", type=parse_integer, default=DEFAULT_SCATTER_LENGTH)
    arguments = parser.parse_args()
    print(json.dumps(
        summarize(
            arguments.image,
            arguments.base,
            arguments.scatter_source,
            arguments.scatter_runtime,
            arguments.scatter_length,
        ),
        indent=2,
        sort_keys=True,
    ))


if __name__ == "__main__":
    main()
