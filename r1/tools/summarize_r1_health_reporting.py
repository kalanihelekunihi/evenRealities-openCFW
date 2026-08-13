#!/usr/bin/env python3
"""Validate R1 report-enable and automatic health-sync behavior without sending commands.

Application 2.2.6.0009 registers health command 7f/01 as ``reportEnable``, but its RAM flag is
write-only in this image. Automatic reports instead use a phone-connection gate and a shared
three-hour timestamp updated by both automatic batches and explicit history queries.
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


REPORT_STATE_ADDRESS = 0x200067A0
REPORT_FLAG_OFFSET = 0
LAST_SYNC_OR_QUERY_OFFSET = 4
AUTOMATIC_SYNC_INTERVAL_SECONDS = 10_800

EXPECTED_POINTER_OCCURRENCES = [0x0008B180, 0x0008B8E4, 0x0008BAE4]

FUNCTION_PREFIXES = {
    # Registered 7f/01 handler: no-payload branch reads address zero, otherwise payload byte zero.
    0x00082ECE: "08890c380004000c05d00c31087800b1012008f0a8bc0021f8e7",
    # Runtime boolean logger/setter. The final store is strb r4,[0x200067a0].
    0x0008B834: (
        "10b5044605f058fec00703d105f054fe400706d523460ca20ba14ff0446005f0f1fe"
        "05f049fe80070ad5144814492246401ac008032101eb004012a1eef7aaf81b48047010bd"
    ),
    # Phone-role connection-handle check at connection context +8.
    0x0004CBB0: "04480089a0f57f41ff3901d00120704700207047",
    # Common automatic batch gate, exact 10,800-second boundary, call order, and timestamp update.
    0x0008B138: (
        "70b5c1f739fd00281dd0fff72ffe0e4d0446686830b1844204d3201a42f63021884210d3"
        "002000f0f7ff002001f0fcfd002001f0f1fa002000f0bcfc0021012000f04efb6c6070bd"
        "a0670020"
    ),
    # Every internal history query writes now to shared state +4 before route selection.
    0x0008B8E8: (
        "30b585b0044605f0fdfdc00703d105f0f9fd400708d56078009023785ea25ea14ff04860"
        "05f094fe05f0ecfd80070bd5654866496378401ac008032101eb0040227863a1eef753f8"
        "fff738fa6b496c4d48602078"
    ),
    # Unsynchronized sleep iterator wrapper used as the fifth automatic batch leg.
    0x0008B818: "08b56a468df80000adf8021002490120cff7b8fd08bd",
    # Valid point/session consumers that reach the common batch gate.
    0x0008A7F4: "10b5002806d0d0f70bf9bde81040042000f098bc10bd",  # activity
    0x0008A80A: (
        "1cb5040015d02078282812d3dc2810d8606810b900f0c1fa606020788df800006068"
        "cdf801006846d0f7adfa002000f07efc1cbd"
    ),  # heart rate
    0x0008A83E: (
        "1cb50446406810b900f0adfa60602088adf800006068cdf802006846d0f781fb0520"
        "00f06afc1cbd"
    ),  # HRV
    0x0008A8AE: (
        "1cb5040010d0207846280dd300f073fa606021788df80010cdf801006846d1f72ef9"
        "012000f031fc1cbd"
    ),  # SpO2
    0x0008DC94: (
        "70b52049204a4ff08065891ac908012202eb014450b1c18b203189b2cdf7eefdc0b1"
        "bde870400620fdf73cba03f014fcc00703d1"
    ),  # validated sleep result
}

HEALTH_TABLE_ENTRY_ADDRESS = 0x0009A4BC
HEALTH_TABLE_ENTRY = bytes.fromhex("017f0000cf2e0800")

SYNC_LEGS = [
    ("heart rate", 0x0008C150),
    ("blood oxygen", 0x0008CD60),
    ("heart-rate variability", 0x0008C750),
    ("activity", 0x0008BAEC),
    ("unsynchronized sleep", 0x0008B818),
]

TRIGGERS = [
    ("heart rate point", "0x0006", 0x0008A80A),
    ("heart-rate variability point", "0x0007", 0x0008A83E),
    ("blood-oxygen point", "0x0008", 0x0008A8AE),
    ("activity delta", "0x000b", 0x0008A7F4),
    ("validated sleep result", "0x000d", 0x0008DC94),
]

AOT_VARIANTS = [
    (
        "blutter_output_2.2.0",
        "[pp+0x242a8] Obj!BleRing1SubCmd@20b17f1",
    ),
    (
        "blutter_output",
        "[pp+0x35d58] Obj!BleRing1SubCmd@1f21c21",
    ),
]


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


def occurrences(image: bytes, base: int, value: int) -> list[int]:
    needle = struct.pack("<I", value)
    result: list[int] = []
    cursor = 0
    while True:
        offset = image.find(needle, cursor)
        if offset < 0:
            return result
        result.append(base + offset)
        cursor = offset + 1


def audit_first_party_aot(root: Path) -> dict[str, Any]:
    variants = []
    for directory_name, marker in AOT_VARIANTS:
        asm_root = root / "firmware" / directory_name / "asm"
        if not asm_root.is_dir():
            raise ValueError(f"missing first-party AOT assembly directory: {asm_root}")
        matches: list[str] = []
        for path in sorted(asm_root.rglob("*.dart")):
            text = path.read_text(errors="replace")
            if marker in text:
                matches.extend([str(path.relative_to(root))] * text.count(marker))
        if len(matches) != 1 or not matches[0].endswith(
            "even_connect/ring1/models/ble_ring1_enum.dart"
        ):
            raise ValueError(
                f"unexpected {directory_name} reportEnable references: {matches}"
            )
        variants.append({
            "corpus": directory_name,
            "typed_enum_object_reference_count": len(matches),
            "only_reference": matches[0],
            "reference_role": "enum-to-wire mapping",
            "typed_sender_found": False,
        })
    return {
        "audited": True,
        "variants": variants,
        "typed_sender_found_in_audited_variants": False,
    }


def summarize(
    image_path: Path,
    base: int,
    scatter_source: int,
    scatter_runtime: int,
    scatter_length: int,
    first_party_root: Path | None,
) -> dict[str, Any]:
    image = image_path.read_bytes()
    for address, signature in FUNCTION_PREFIXES.items():
        require_prefix(image, base, address, signature)
    if flash_bytes(image, base, HEALTH_TABLE_ENTRY_ADDRESS, 8) != HEALTH_TABLE_ENTRY:
        raise ValueError("health 7f/01 registration entry changed")

    pointer_occurrences = occurrences(image, base, REPORT_STATE_ADDRESS)
    if pointer_occurrences != EXPECTED_POINTER_OCCURRENCES:
        raise ValueError(
            f"unexpected report-state references: {pointer_occurrences}"
        )

    source_offset = mapped_offset(scatter_source, base, len(image))
    runtime, consumed = decompress_scatter(image[source_offset:], scatter_length)
    state_offset = REPORT_STATE_ADDRESS - scatter_runtime
    initial_state = runtime[state_offset:state_offset + 8]
    if initial_state != bytes(8):
        raise ValueError(f"unexpected initialized report state: {initial_state.hex()}")

    aot = (
        audit_first_party_aot(first_party_root)
        if first_party_root is not None
        else {"audited": False}
    )
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
        "report_enable_command": {
            "module": "0x02",
            "command": "0x7f",
            "subcommand": "0x01",
            "handler": "0x00082ece",
            "canonical_payload_bytes": 1,
            "zero_means_disabled": True,
            "nonzero_means_enabled": True,
            "trailing_payload_bytes_ignored": True,
            "zero_payload_reads_absolute_address_zero": True,
            "method_and_acknowledgement_bits_checked_by_handler": False,
            "protocol_response_or_ack_emitted": False,
            "persistent_write_performed": False,
        },
        "runtime_state": {
            "address": f"0x{REPORT_STATE_ADDRESS:08x}",
            "report_flag_offset": REPORT_FLAG_OFFSET,
            "last_automatic_batch_or_history_query_timestamp_offset": LAST_SYNC_OR_QUERY_OFFSET,
            "initial_report_flag": False,
            "initial_timestamp_seconds": 0,
            "pointer_literal_locations": [
                f"0x{address:08x}" for address in pointer_occurrences
            ],
            "report_flag_has_compiled_reader": False,
            "timestamp_has_automatic_gate_reader_writer": True,
            "timestamp_has_history_query_writer": True,
        },
        "automatic_health_sync": {
            "gate": "authenticated phone-role connection handle is not 0xffff",
            "interval_seconds": AUTOMATIC_SYNC_INTERVAL_SECONDS,
            "fires_when_timestamp_is_zero": True,
            "fires_when_clock_is_before_timestamp": True,
            "fires_when_elapsed_is_at_least_interval": True,
            "suppresses_when_elapsed_is_below_interval": True,
            "report_enable_flag_consulted": False,
            "trigger_sources": [
                {"semantic": name, "internal_event": event, "consumer": f"0x{consumer:08x}"}
                for name, event, consumer in TRIGGERS
            ],
            "batch_legs_in_call_order": [
                {"semantic": name, "function": f"0x{function:08x}", "serial_id": 0}
                for name, function in SYNC_LEGS
            ],
            "timestamp_updated_after_batch_calls_without_aggregate_success_check": True,
            "explicit_internal_history_query_resets_same_timestamp_before_route_selection": True,
            "temperature_and_stress_are_not_batch_legs": True,
        },
        "first_party_aot": aot,
        "safety": {
            "static_parser_only": True,
            "captured_health_values_emitted": False,
            "live_report_enable_sender_exposed": False,
            "automatic_sync_trigger_exposed": False,
            "private_timestamp_mutation_exposed": False,
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
    parser.add_argument(
        "--first-party-root",
        type=Path,
        help="Optional SybilSight-v2 root containing both first-party AOT assembly corpora",
    )
    arguments = parser.parse_args()
    print(json.dumps(summarize(
        arguments.image,
        arguments.base,
        arguments.scatter_source,
        arguments.scatter_runtime,
        arguments.scatter_length,
        arguments.first_party_root,
    ), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
