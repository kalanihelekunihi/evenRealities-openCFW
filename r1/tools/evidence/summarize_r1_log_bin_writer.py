#!/usr/bin/env python3
"""Pin the R1 log.bin circular-page writer around the upstream FAL boundary."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from summarize_r1_gomore_call_graph import direct_thumb_branches_to


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_IMAGE = ROOT / "research/decompilation/rebuild/rebuilt-application.bin"
LOAD_BASE = 0x00027000
EXPECTED_IMAGE_SHA256 = "0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a"


def _function(
    entry: int,
    end_exclusive: int,
    role: str,
    symbol: str,
    sha256: str,
    caller_count: int,
    caller_digest: str,
) -> dict[str, Any]:
    return {
        "entry": entry,
        "end_exclusive": end_exclusive,
        "size": end_exclusive - entry,
        "role": role,
        "symbol": symbol,
        "sha256": sha256,
        "caller_count": caller_count,
        "caller_digest": caller_digest,
        "inventory": "ghidra_functions_csv",
    }


R1_LOG_BIN_WRITER_FUNCTIONS = (
    _function(
        0x0005908C, 0x0005909A,
        "partition sector-count accessor",
        "r1_log_bin_sector_count",
        "21450daee8c274c4e8624652e88389df19dc391791309912b5695c8d7092fffd",
        4, "3282e59acd638a018b5d3220d8563ab1788f928d13cb52547545ba7a13619281",
    ),
    _function(
        0x000590AC, 0x000591AE,
        "partition/provider lookup and erased-page scan",
        "r1_log_bin_initialize",
        "a32f6f33a5dc99a62914e9c08ba200681c512e81a853c0f0b1ddadc08d765d44",
        2, "89f92b61ff0a78f72be99639c3eb376733c53305992a06577f1cc1c5c9540732",
    ),
    _function(
        0x00059670, 0x000598CC,
        "bounded circular-page append and pre-erase policy",
        "r1_log_bin_write",
        "0654e2e5cd542e5c57069d59ff92a9b753e616b515974ddbc9207f3e847f8594",
        1, "114957e53bc5deded94f9a2b26c29d9bddc3566004c04f09405d36bcaebf7958",
    ),
)


def summarize(image_path: Path) -> dict[str, Any]:
    image = image_path.read_bytes()
    if hashlib.sha256(image).hexdigest() != EXPECTED_IMAGE_SHA256:
        raise ValueError("unexpected recovered application image")

    functions = []
    for function in R1_LOG_BIN_WRITER_FUNCTIONS:
        start = int(function["entry"])
        end = int(function["end_exclusive"])
        body = image[start - LOAD_BASE:end - LOAD_BASE]
        if len(body) != int(function["size"]) or \
                hashlib.sha256(body).hexdigest() != function["sha256"]:
            raise ValueError(f"log.bin writer body mismatch at 0x{start:08x}")
        callers = direct_thumb_branches_to(image, LOAD_BASE, start)
        caller_digest = hashlib.sha256("".join(
            f"{address:08x}:{kind}\n" for address, kind in callers
        ).encode()).hexdigest()
        if len(callers) != int(function["caller_count"]) or \
                caller_digest != function["caller_digest"]:
            raise ValueError(f"log.bin writer caller set mismatch at 0x{start:08x}")
        functions.append({
            **function,
            "entry": f"0x{start:08x}",
            "end_exclusive": f"0x{end:08x}",
        })

    return {
        "analysis": "R1 log.bin circular-page writer closure",
        "image": str(image_path),
        "image_sha256": EXPECTED_IMAGE_SHA256,
        "function_count": len(functions),
        "function_bytes": sum(int(function["size"]) for function in functions),
        "functions": functions,
        "partition": {
            "name": "log.bin",
            "relative_offset_bytes": 0x18000,
            "length_bytes": 0xC000,
            "sector_bytes": 0x1000,
            "sector_count": 12,
            "erased_probe_word_offset": 4,
        },
        "writer": {
            "maximum_input_bytes": 0x1000,
            "initialize_on_first_write": True,
            "advance_before_cross_page_write": True,
            "erase_selected_nonempty_page": True,
            "preerase_next_nonempty_page_after_write": True,
            "wrap_modulo_partition_sector_count": True,
            "full_partition_scan_fallback_sector": 0,
            "direct_caller": "0x000914d2",
        },
        "boundary": {
            "provider_family": "r1_product_specific",
            "source_disposition": "clean_room_behavior_only",
            "third_party_implementation_identified": False,
            "fal_lookup_reimplemented": False,
            "flash_read_write_erase_reimplemented": False,
            "nordic_logging_reimplemented": False,
            "structured_log_encoder_reimplemented": False,
            "virtual_export_or_transport_sender_emitted": False,
        },
        "safety": {
            "static_parser_only": True,
            "private_log_content_read": False,
            "live_export_sender_exposed": False,
            "raw_flash_mutation_interface_exposed": False,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", nargs="?", type=Path, default=DEFAULT_IMAGE)
    arguments = parser.parse_args()
    print(json.dumps(summarize(arguments.image), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
