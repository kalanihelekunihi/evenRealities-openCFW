#!/usr/bin/env python3
"""Emit the exact R1 sensor-algorithm heap provider-boundary census.

This parser records executable extents and recovered allocator semantics for
the owner-authorized transparent reconstruction.

Provenance is resolved: the censused component is Goodix's ``goodix_mem`` /
``GdMem`` memory-pool manager from the Goodix GH3X2X health-sensor algorithm
SDK common DSP support library (R1 carries config tag ``gh3x2x-v2.23_7ecd2a``).
The public GH3X2X SDK header ``goodix_mem.h`` declares
``goodix_mem_init``/``deinit``/``malloc``/``free``/``get_free_size`` with the
-1/-2 error contract the R1 init body implements, and declares
``extern void Gh3x2xPoolIsNotEnough(void)`` as an integrator-supplied
callback.  Instruction-level comparison against the Goodix common-DSP library
object matched the R1 allocator internals (GdMemInit, GdMemMalloc, GdMemFree,
GdMemRealloc, unlink, insert, GdMemGetFreeSize). Under the owner-authorized
full reduction, the twelve Goodix-owned core functions are independently
reconstructed in ``reconstructed/goodix_heap/``; this is not Goodix source.
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


# Resolved ownership routing for the complete 34-row boundary: the thirteen
# exact allocator census bodies above plus the twenty-one guarded
# alloc/free call-site glue bodies imported from the sub-32-byte frontier
# census.  Each entry maps to (provider_family, source_disposition,
# confidence, routing basis).  Allocator internals carry instruction-level
# matches to the Goodix common-DSP library object; call-site glue sits inside
# already Goodix-gated consumer closures and is conservatively gated with the
# calling provider; only the two integrator-authored glue bodies are R1
# product behavior.
_GOODIX_INTERNAL = (
    "goodix_gh3x2x_candidate", "clean_room_reimplementation_owner_authorized",
    "high",
)
_GOODIX_CALLSITE_GLUE = (
    "goodix_gh3x2x_candidate", "clean_room_reimplementation_owner_authorized",
    "candidate",
)
_R1_INTEGRATOR_GLUE = (
    "r1_product_specific", "clean_room_behavior_only", "high",
)
SENSOR_ALGORITHM_HEAP_ROUTING = {
    # Allocator internals: instruction-level Goodix goodix_mem/GdMem match.
    0x0002D460: _GOODIX_INTERNAL + ("GdMemFree validated free/coalescing",),
    0x0002D54C: _GOODIX_INTERNAL + (
        "GdMemMalloc minimum-8 zeroing allocation entry",
    ),
    0x0002D5C0: _GOODIX_INTERNAL + ("GdMemRealloc grow/copy/free body",),
    0x00042D1C: _GOODIX_INTERNAL + (
        "pool control-pointer accessor used only by GdMem bodies",
    ),
    0x0006DFC8: _GOODIX_INTERNAL + ("goodix_mem_free tail-call thunk",),
    0x0006DFCC: _GOODIX_INTERNAL + (
        "GdMemGetFreeSize behind goodix_mem_get_free_size",
    ),
    0x0006DFD6: _GOODIX_INTERNAL + (
        "goodix_mem_init (-1/-2 contract) tail-calling GdMemInit",
    ),
    0x0006E004: _GOODIX_INTERNAL + ("goodix_mem_malloc tail-call thunk",),
    0x00076A44: _GOODIX_INTERNAL + ("GdMem free-list unlink internal",),
    0x00093E14: _GOODIX_INTERNAL + ("GdMem size-to-bin mapping internal",),
    0x00093E5E: _GOODIX_INTERNAL + ("GdMem free-list insert internal",),
    0x000982C2: _GOODIX_INTERNAL + (
        "GdMemMalloc bitmap search/remove/split/mark core",
    ),
    # Integrator-authored R1 glue around the vendor pool manager.
    0x0002E952: _R1_INTEGRATOR_GLUE + (
        "integrator-supplied Gh3x2xPoolIsNotEnough: logs "
        "'sensor_algo_mem_fatal, info1: %u', flushes, terminal loop",
    ),
    0x00092B60: (
        "r1_product_specific", "clean_room_reimplementation_owner_authorized",
        "high",
        "R1 product byte-fill (memset) used by goodix_mem_init pool clearing",
    ),
    # Goodix consumer call-site glue (guarded alloc/free wrappers), gated
    # with the calling Goodix provider.
    0x00028EAC: _GOODIX_CALLSITE_GLUE + (
        "guarded free-and-null; caller Goodix teardown 0x0007CBA0",
    ),
    0x00028EC0: _GOODIX_CALLSITE_GLUE + (
        "teardown tail-branch step; caller Goodix session teardown 0x0006EB30",
    ),
    0x0002963A: _GOODIX_CALLSITE_GLUE + (
        "0x40 zero-allocate and clear; caller Goodix buffer-pool init 0x00096A20",
    ),
    0x00034A3C: _GOODIX_CALLSITE_GLUE + (
        "0x18-array zero-allocate; caller Goodix 0x0006EB94",
    ),
    0x00036230: _GOODIX_CALLSITE_GLUE + (
        "guarded free returning 0; caller Goodix context destroy 0x0003E6B0",
    ),
    0x00036C60: _GOODIX_CALLSITE_GLUE + (
        "context destroy free; reached only via Goodix teardown step 0x00028EC0",
    ),
    0x0003757C: _GOODIX_CALLSITE_GLUE + (
        "guarded free returning 0; no resolved caller, wraps GdMemFree "
        "between Goodix-gated neighbors",
    ),
    0x00056860: _GOODIX_CALLSITE_GLUE + (
        "guarded free of *p; exclusive Goodix caller 0x0006DAD0",
    ),
    0x00066276: _GOODIX_CALLSITE_GLUE + (
        "guarded free-and-null; caller Goodix 0x00093E3A",
    ),
    0x0006628A: _GOODIX_CALLSITE_GLUE + (
        "guarded free-and-null; callers Goodix 0x00029BBC plus glue 0x00073154",
    ),
    0x0006629E: _GOODIX_CALLSITE_GLUE + (
        "guarded free-and-null; caller Goodix teardown 0x0006CC60",
    ),
    0x000662B2: _GOODIX_CALLSITE_GLUE + (
        "guarded free-and-null; caller Goodix 0x00091890",
    ),
    0x000662C6: _GOODIX_CALLSITE_GLUE + (
        "guarded free-and-null; callers Goodix 0x00029BBC/0x000304A0/"
        "0x000305D8/0x00033800/0x0006CC60/0x00091890",
    ),
    0x000662EA: _GOODIX_CALLSITE_GLUE + (
        "buffer-descriptor init with heap zero-allocate; caller Goodix 0x0003727C",
    ),
    0x00066304: _GOODIX_CALLSITE_GLUE + (
        "buffer-descriptor init with heap zero-allocate; callers Goodix "
        "0x00031914/0x00072C48",
    ),
    0x0006631E: _GOODIX_CALLSITE_GLUE + (
        "buffer-descriptor init with heap zero-allocate; caller Goodix 0x0006D204",
    ),
    0x000667C0: _GOODIX_CALLSITE_GLUE + (
        "tail free of *(p+4); exclusive Goodix caller 0x00029BBC",
    ),
    0x00073154: _GOODIX_CALLSITE_GLUE + (
        "record-field frees via glue 0x0006628A; caller Goodix teardown 0x00037E8A",
    ),
    0x00092B58: _GOODIX_CALLSITE_GLUE + (
        "2-byte thunk into R1 memset 0x00092B60; sole caller goodix_mem_init",
    ),
    0x00098FFC: _GOODIX_CALLSITE_GLUE + (
        "field frees via GdMemFree; caller Goodix session teardown 0x0006EB30",
    ),
}


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
        family, disposition, confidence, basis = SENSOR_ALGORITHM_HEAP_ROUTING[entry]
        functions.append({
            **function,
            "provider_family": family,
            "source_disposition": disposition,
            "confidence": confidence,
            "routing_basis": basis,
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
            "status": "goodix_gh3x2x_goodix_mem_gdmem_provider",
            "goodix_link": "initialized directly by Goodix-candidate entry 0x0002a090",
            "attribution": (
                "Goodix goodix_mem/GdMem memory-pool manager from the GH3X2X "
                "health-sensor algorithm SDK common DSP support library "
                "(config tag gh3x2x-v2.23_7ecd2a); public goodix_mem.h "
                "-1/-2 error contract plus instruction-level match to the "
                "Goodix common-DSP library object"
            ),
            "integrator_supplied": [
                "Gh3x2xPoolIsNotEnough fatal handler at 0x0002e952",
                "R1 product byte-fill (memset) at 0x00092b60",
            ],
            "excluded_matches": [
                "Nordic SDK FreeRTOS 10.0.0 heap_4",
                "Matthew Conte TLSF v3.1",
            ],
            "local_implementation_authorized": True,
            "reason": (
                "The owner-authorized full reduction independently reconstructs "
                "the byte-pinned allocator behavior in transparent C; the "
                "restrictively licensed Goodix binary remains evidence only."
            ),
        },
        "safety": {
            "static_parser_only": True,
            "allocator_reimplementation_emitted": True,
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
