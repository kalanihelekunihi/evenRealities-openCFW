#!/usr/bin/env python3
"""Pin the R1 EUS receive reassembly and outer-CRC gate."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from summarize_r1_gomore_call_graph import direct_thumb_branches_to


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_IMAGE = ROOT / "research/decompilation/rebuild/rebuilt-application.bin"
LOAD_BASE = 0x00027000
EXPECTED_IMAGE_SHA256 = "0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a"

R1_EUS_RX_REASSEMBLY_FUNCTIONS: tuple[dict[str, Any], ...] = ({
    "entry": 0x00032198,
    "end_exclusive": 0x00032340,
    "size": 424,
    "role": "EUS receive fragment reassembly and outer CRC gate",
    "symbol": "r1_eus_rx_reassembly",
    "sha256": "a91ae73ec32df232276ab2e01dcd4c4e29f864de03b66f5addcea96350688df5",
    "callers": ((0x0005D69C, "BL"),),
    "inventory": "ghidra_functions_csv",
    "provider_family": "r1_product_specific",
    "source_disposition": "clean_room_behavior_only_security_preserving",
},)


def summarize(image_path: Path) -> dict[str, Any]:
    image = image_path.read_bytes()
    digest = hashlib.sha256(image).hexdigest()
    if digest != EXPECTED_IMAGE_SHA256:
        raise ValueError(f"unexpected recovered application image: {digest}")

    functions = []
    for function in R1_EUS_RX_REASSEMBLY_FUNCTIONS:
        entry = int(function["entry"])
        end = int(function["end_exclusive"])
        body = image[entry - LOAD_BASE:end - LOAD_BASE]
        callers = tuple(direct_thumb_branches_to(image, LOAD_BASE, entry))
        if len(body) != int(function["size"]) or \
                hashlib.sha256(body).hexdigest() != function["sha256"] or \
                callers != function["callers"]:
            raise ValueError(f"EUS receive reassembly changed at 0x{entry:08x}")
        functions.append({
            **function,
            "entry": f"0x{entry:08x}",
            "end_exclusive": f"0x{end:08x}",
            "callers": [
                {"callsite": f"0x{address:08x}", "kind": kind}
                for address, kind in callers
            ],
        })

    return {
        "analysis": "R1 EUS receive reassembly and outer-CRC gate",
        "image": str(image_path),
        "image_sha256": digest,
        "function_count": 1,
        "function_bytes": 424,
        "functions": functions,
        "wire_contract": {
            "minimum_fragment_bytes": 5,
            "header_bytes": 5,
            "payload_bytes_per_full_fragment": 239,
            "maximum_sequence": 16,
            "maximum_fragment_count": 17,
            "maximum_inbound_logical_bytes": 4063,
            "completion_sequence": 0,
            "outer_checksum": "CRC-32/Castagnoli, MSB-first, zero seed and final xor",
            "checksum_offset": 1,
            "payload_offset": 5,
        },
        "stock_behavior": {
            "allocation_formula": "(first_sequence + 1) * 239",
            "sequence_one_uses_static_buffer": True,
            "sequence_zero_uses_fragment_payload_directly": True,
            "same_sequence_retransmit_replaces_previous_fragment": True,
            "cross_fragment_checksum_consistency_enforced": False,
            "strict_sequence_continuity_enforced": False,
            "dynamic_buffer_released_after_terminal_fragment": True,
            "checksum_failure_emits_six_byte_transport_error": True,
        },
        "clean_room_behavior": {
            "implementation": "src/r1_protocol.c::r1_reassembler_feed",
            "bounded_per_link_storage": True,
            "dynamic_allocation_required": False,
            "strict_sequence_continuity_enforced": True,
            "cross_fragment_checksum_consistency_enforced": True,
            "duplicate_fragment_rejected": True,
            "stock_malformed_train_acceptance_preserved": False,
        },
        "dependencies": {
            "memmove": "Arm toolchain runtime",
            "allocation_and_release": "FreeRTOS 10.5.1 heap_4",
            "logging": "Nordic SDK plus R1 structured-log adapter",
            "crc32": "R1 product behavior at 0x0005d8a4",
            "dependency_implementations_included": False,
        },
        "boundary": {
            "provider_family": "r1_product_specific",
            "source_disposition": "clean_room_behavior_only_security_preserving",
            "vendor_implementation_identified": False,
            "stock_unsafe_or_ambiguous_edges_preserved": False,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", nargs="?", type=Path, default=DEFAULT_IMAGE)
    print(json.dumps(summarize(parser.parse_args().image), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
