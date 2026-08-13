#!/usr/bin/env python3
"""Emit the exact Goodix-linked packed-word integrity-helper boundary.

This parser is static and read-only.  It records duplicate helper bodies,
constant tables, and complete direct-caller sets without assigning private
Goodix symbol names or emitting a replacement implementation.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
from pathlib import Path
from typing import Any

from summarize_r1_gomore_call_graph import direct_thumb_branches_to


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_IMAGE = ROOT / "research/decompilation/rebuild/rebuilt-application.bin"
LOAD_BASE = 0x00027000
EXPECTED_IMAGE_SHA256 = "0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a"
INTEGRITY_TABLE_WORDS = (0x6B851EB7, 0x4147AE13, 0x28F5C28F, 0x15C28F5B)
INTEGRITY_TABLE_SHA256 = "448ddc2f827f6109a389e73dcc8a34db1ba3b44812f760451944fb015221d936"


def _function(
    entry: int,
    end_exclusive: int,
    role: str,
    sha256: str,
    callsites: tuple[int, ...],
    table_address: int | None = None,
    newly_resolved: bool = True,
) -> dict[str, Any]:
    return {
        "entry": entry,
        "end_exclusive": end_exclusive,
        "size": end_exclusive - entry,
        "role": role,
        "provider_family": "goodix_gh3x2x_candidate",
        "sha256": sha256,
        "callsites": callsites,
        "table_address": table_address,
        "newly_resolved": newly_resolved,
    }


# Roles are descriptive boundary labels, not claims about private Goodix names.
# The first five entries were previously unclassified.  The last two are the
# already gated GH_HR copies and are retained here to prove the three-way
# encoder identity and the shared integrity protocol.
GOODIX_INTEGRITY_FUNCTIONS = [
    _function(
        0x00028E5C, 0x00028E70,
        "packed_24_bit_integrity_validator_copy_a",
        "e170a2ec96dd076d2f8a43cbcf0d26a23a1567ab4484ce62d66409f8aa759e1c",
        (0x00061DD6, 0x0006C6CE),
    ),
    _function(
        0x00028E70, 0x00028EA6,
        "packed_24_bit_integrity_encoder_copy_a",
        "f6556685cb2ed54dc42e8ff378ad47ff2fcc02ae4948b261bf5bb58ca4a78572",
        (0x00028E60,),
        0x000BCF18,
    ),
    _function(
        0x000294BC, 0x000294F2,
        "packed_24_bit_integrity_encoder_copy_b",
        "f6556685cb2ed54dc42e8ff378ad47ff2fcc02ae4948b261bf5bb58ca4a78572",
        (0x000294FC, 0x00029512),
        0x000B0EFC,
    ),
    _function(
        0x000294F8, 0x0002950C,
        "packed_24_bit_integrity_validator_copy_b",
        "337eb903836302f7b54bf349024090cf19cadce10f1616602eb80c74b27bd958",
        (0x0002A1E6,),
    ),
    _function(
        0x0002950C, 0x0002951A,
        "packed_24_bit_integrity_inserter_copy_b",
        "87b5e5c122a602e9a39e1de262a17c11a9c7cc82ea48f14b0f8748b770412252",
        (0x0002A186,),
    ),
    _function(
        0x0005A5EC, 0x0005A622,
        "gh_hr_packed_24_bit_integrity_encoder",
        "f6556685cb2ed54dc42e8ff378ad47ff2fcc02ae4948b261bf5bb58ca4a78572",
        (0x000759F8,),
        0x000B149C,
        False,
    ),
    _function(
        0x000759F4, 0x00075A08,
        "gh_hr_packed_24_bit_integrity_validator",
        "144db00be4dbeff89e673850917c4d4bcbbac8ba2740e7ea056d14a8da04cb80",
        (0x0006D53E,),
        newly_resolved=False,
    ),
]


GOODIX_INTEGRITY_NEW_FUNCTIONS = [
    function for function in GOODIX_INTEGRITY_FUNCTIONS
    if bool(function["newly_resolved"])
]


def summarize(image_path: Path) -> dict[str, object]:
    image = image_path.read_bytes()
    digest = hashlib.sha256(image).hexdigest()
    if digest != EXPECTED_IMAGE_SHA256:
        raise ValueError(f"unexpected application image SHA-256: {digest}")

    functions = []
    tables = []
    for function in GOODIX_INTEGRITY_FUNCTIONS:
        entry = int(function["entry"])
        end = int(function["end_exclusive"])
        body = image[entry - LOAD_BASE:end - LOAD_BASE]
        if len(body) != function["size"] or \
                hashlib.sha256(body).hexdigest() != function["sha256"]:
            raise ValueError(f"Goodix integrity boundary changed at 0x{entry:08x}")
        actual_callsites = tuple(
            address for address, _ in direct_thumb_branches_to(image, LOAD_BASE, entry)
        )
        if actual_callsites != function["callsites"]:
            raise ValueError(
                f"Goodix integrity callers changed at 0x{entry:08x}: "
                f"{actual_callsites} != {function['callsites']}"
            )
        table_address = function["table_address"]
        if table_address is not None:
            table = image[table_address - LOAD_BASE:table_address - LOAD_BASE + 16]
            words = struct.unpack("<4I", table)
            if words != INTEGRITY_TABLE_WORDS or \
                    hashlib.sha256(table).hexdigest() != INTEGRITY_TABLE_SHA256:
                raise ValueError(
                    f"Goodix integrity table changed at 0x{table_address:08x}"
                )
            tables.append({
                "address": f"0x{table_address:08x}",
                "sha256": INTEGRITY_TABLE_SHA256,
                "words": [f"0x{word:08x}" for word in words],
            })
        functions.append({
            **function,
            "entry": f"0x{entry:08x}",
            "end_exclusive": f"0x{end:08x}",
            "callsites": [f"0x{address:08x}" for address in actual_callsites],
            "table_address": (
                f"0x{table_address:08x}" if table_address is not None else None
            ),
        })

    return {
        "analysis": "R1 Goodix-linked packed-word integrity-helper boundary",
        "image": str(image_path),
        "image_sha256": digest,
        "function_count": len(functions),
        "function_bytes": sum(int(item["size"]) for item in functions),
        "newly_resolved_function_count": len(GOODIX_INTEGRITY_NEW_FUNCTIONS),
        "newly_resolved_function_bytes": sum(
            int(item["size"]) for item in GOODIX_INTEGRITY_NEW_FUNCTIONS
        ),
        "functions": functions,
        "tables": tables,
        "recovered_semantics": {
            "packed_word_bits": 24,
            "integrity_bit": 0,
            "table_selector_bits": "1..2",
            "table_words": [f"0x{word:08x}" for word in INTEGRITY_TABLE_WORDS],
            "operation": "masked_xor_popcount_parity_inserted_at_bit_zero",
        },
        "source_lineage": {
            "status": "goodix_gh3x2x_candidate",
            "private_symbols_claimed": False,
            "local_implementation_authorized": False,
            "reason": (
                "Two copies are called exclusively by the frozen Goodix demo/provider "
                "component. The other duplicate is already called by the exact GH_HR "
                "core; copy A is reached by GH_NADT and another Goodix-rooted algorithm "
                "path. Byte identity is corroborating evidence, not the sole basis."
            ),
        },
        "safety": {
            "static_parser_only": True,
            "integrity_helper_reimplementation_emitted": False,
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
