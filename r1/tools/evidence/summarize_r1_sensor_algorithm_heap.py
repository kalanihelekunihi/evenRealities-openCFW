#!/usr/bin/env python3
"""Emit the exact R1 sensor-algorithm heap provider-boundary census.

This parser is static and read-only.  It records executable extents and
recovered allocator semantics without claiming authorship or exposing a
replacement allocator for the still-unattributed provider component.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_IMAGE = ROOT / "research/decompilation/rebuild/rebuilt-application.bin"
LOAD_BASE = 0x00027000
EXPECTED_IMAGE_SHA256 = "0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a"


def _function(
    entry: int,
    end_exclusive: int,
    symbol: str,
    role: str,
    sha256: str,
    segments: tuple[tuple[int, int], ...] = (),
) -> dict[str, Any]:
    executable_segments = segments or ((entry, end_exclusive),)
    return {
        "entry": entry,
        "end_exclusive": end_exclusive,
        "size": sum(end - start for start, end in executable_segments),
        "symbol": symbol,
        "role": role,
        "provider_family": "unknown_sensor_algorithm_heap_provider_candidate",
        "sha256": sha256,
        "segments": segments,
    }


# Ghidra correctly reports the aggregate executable sizes of the four
# scatter-loaded functions below, but its entry/end columns span unrelated
# intervening code.  Digests concatenate only the listed executable spans, in
# control-flow order, and exclude literal pools.
SENSOR_ALGORITHM_HEAP_FUNCTIONS = [
    _function(
        0x0002D460, 0x00037530,
        "sensor_algorithm_heap_free_candidate",
        "validated_free_and_bidirectional_coalescing",
        "a8e129fa871645cef4b3fb81905ec18d8547c61a0cd4f01cd44686021f018f28",
        ((0x0002D460, 0x0002D4D6), (0x00037480, 0x00037530)),
    ),
    _function(
        0x0002D54C, 0x0002D5C0,
        "sensor_algorithm_heap_zero_allocate_candidate",
        "minimum_eight_byte_zeroing_allocation_wrapper",
        "1d5c425841dc5df88d88d264b28e99e087ac9d6d2c2f7bb94449ced636f7e532",
    ),
    _function(
        0x0002D5C0, 0x0002D658,
        "sensor_algorithm_heap_reallocate_candidate",
        "allocate_copy_free_or_in_place_shrink",
        "c3f676ec6c386354e1654696ec9fcc63760ea7979bcd40e2b017caea317c8635",
    ),
    _function(
        0x0002E952, 0x000926AA,
        "sensor_algorithm_heap_fatal_candidate",
        "sensor_algo_mem_fatal_log_flush_and_terminal_loop",
        "ca349eab17fd792348a0b4a99d260adb2f2e9c65bfb85aacf80fec4d0bad5369",
        ((0x0002E952, 0x0002E964), (0x00092670, 0x000926AA)),
    ),
    _function(
        0x00042D1C, 0x00042D22,
        "sensor_algorithm_heap_control_accessor_candidate",
        "load_control_pointer_from_0x20007c64",
        "579f66b93cd2bbcb53693929db18e36025cdc6e5d94aa3e7590989e1d8a117b1",
    ),
    _function(
        0x0006DFC8, 0x0006DFCC,
        "sensor_algorithm_heap_free_thunk_candidate",
        "tail_call_free_wrapper",
        "0bffb8b23eaedef5bb71bbecb723c77f97a7878e7b50f2e0b3e134ad129b9ad3",
    ),
    _function(
        0x0006DFCC, 0x0006DFD6,
        "sensor_algorithm_heap_available_bytes_candidate",
        "tail_free_space_query",
        "ca7bc8ec0c785670e410153de9e72674385950650e45c0d6c1b123c96331cc50",
        ((0x0006DFCC, 0x0006DFD6), (0x0002D4D6, 0x0002D4F4)),
    ),
    _function(
        0x0006DFD6, 0x0006E004,
        "sensor_algorithm_heap_initialize_candidate",
        "clear_pool_initialize_two_bins_and_one_tail_block",
        "dab9a92e720146d0e0d0b9b3413112765ea4bb8ea404ec6c41b648f61b1f6208",
        ((0x0006DFD6, 0x0006E004), (0x0002D4F4, 0x0002D542)),
    ),
    _function(
        0x0006E004, 0x0006E008,
        "sensor_algorithm_heap_allocate_thunk_candidate",
        "tail_call_zeroing_allocate_wrapper",
        "a40930b5c8c91fbbf34f343c83676cc599b033578a63baf90d12d7320aefd678",
    ),
    _function(
        0x00076A44, 0x00076A66,
        "sensor_algorithm_heap_unlink_free_block_candidate",
        "unlink_free_list_node_and_clear_empty_bin_bit",
        "776ebb1dab7b2f3cee0720bcf13e594cac4a7f6287db22fd1e3b19802a1e4170",
    ),
    _function(
        0x00093E14, 0x00093E3A,
        "sensor_algorithm_heap_size_to_bin_candidate",
        "map_adjusted_size_to_one_of_two_bins",
        "a4034e87968ea8710751b740fd92420bb40b25b47fad5a385c6d6e8609485f8b",
    ),
    _function(
        0x00093E5E, 0x00093EA2,
        "sensor_algorithm_heap_insert_free_block_candidate",
        "size_ordered_circular_free_list_insert",
        "59abaa52a4a02c67a5a3649840801e8fe1050da271c79756db3ffd0744cd3288",
    ),
    _function(
        0x000982C2, 0x00098340,
        "sensor_algorithm_heap_allocate_core_candidate",
        "bitmap_search_remove_split_mark_and_return_payload",
        "3841469090c0e0b0fc30cfc9848cc87a8d8fd49a6ef1e864f8641d45160e0a65",
        ((0x000982C2, 0x00098340), (0x0003DF80, 0x0003DFF8)),
    ),
]


def summarize(image_path: Path) -> dict[str, object]:
    image = image_path.read_bytes()
    image_digest = hashlib.sha256(image).hexdigest()
    if image_digest != EXPECTED_IMAGE_SHA256:
        raise ValueError(f"unexpected application image SHA-256: {image_digest}")

    functions = []
    for function in SENSOR_ALGORITHM_HEAP_FUNCTIONS:
        entry = int(function["entry"])
        end = int(function["end_exclusive"])
        segments = function["segments"] or ((entry, end),)
        body = b"".join(
            image[start - LOAD_BASE:segment_end - LOAD_BASE]
            for start, segment_end in segments
        )
        if len(body) != function["size"] or \
                hashlib.sha256(body).hexdigest() != function["sha256"]:
            raise ValueError(f"sensor-algorithm heap boundary changed at 0x{entry:08x}")
        functions.append({
            **function,
            "entry": f"0x{entry:08x}",
            "end_exclusive": f"0x{end:08x}",
            "segments": [
                {"start": f"0x{start:08x}", "end_exclusive": f"0x{segment_end:08x}"}
                for start, segment_end in segments
            ],
        })

    return {
        "analysis": "R1 sensor-algorithm heap provider boundary census",
        "image": str(image_path),
        "image_sha256": image_digest,
        "function_count": len(functions),
        "function_bytes": sum(int(item["size"]) for item in functions),
        "functions": functions,
        "recovered_layout": {
            "control_pointer_storage": "0x20007c64",
            "pool_base_from_goodix_candidate_init": "0x2003024c",
            "control_block_bytes": 44,
            "bin_count": 2,
            "minimum_request_bytes": 8,
            "request_alignment_bytes": 4,
            "pool_start_alignment_bytes": 8,
            "block_header_bytes": 8,
            "minimum_split_remainder_bytes": 16,
            "minimum_pool_bytes_exclusive": 1024,
        },
        "source_lineage": {
            "status": "unidentified_sensor_algorithm_provider_candidate",
            "goodix_link": "initialized directly by Goodix-candidate entry 0x0002a090",
            "excluded_matches": [
                "Nordic SDK FreeRTOS 10.0.0 heap_4",
                "Matthew Conte TLSF v3.1",
            ],
            "local_implementation_authorized": False,
            "reason": (
                "Exact allocator semantics and its sensor_algo_mem_fatal path are recovered, "
                "but no attributable source, version, private API, or license is established."
            ),
        },
        "safety": {
            "static_parser_only": True,
            "allocator_reimplementation_emitted": False,
            "vendor_algorithm_reimplementation_emitted": False,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("image", nargs="?", type=Path, default=DEFAULT_IMAGE)
    args = parser.parse_args()
    print(json.dumps(summarize(args.image), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
