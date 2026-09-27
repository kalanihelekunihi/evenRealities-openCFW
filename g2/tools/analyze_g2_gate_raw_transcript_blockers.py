#!/usr/bin/env python3
"""Summarize the raw public transcript sources that fail source ownership."""

from __future__ import annotations

import hashlib
import json
import re
import struct
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import analyze_g2_production_raw_encoding_quality as raw_quality
import analyze_g2_am_mixed_boundary_debt as mixed_boundary


OUT = ROOT / "tools/manifests/g2-gate-raw-transcript-blockers.json"
AM_HELPER_RE = re.compile(r"runtime_liblc3_am(\d+)_helpers\.c$")
APOLLO_MAIN_BASE = 0x00400000
APOLLO_MAIN_IMAGE = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
AM142_RECEIPT = ROOT / "tools/manifests/g2-apollo-am142-pullthrough-candidate.json"


def _digest(values: object) -> str:
    return hashlib.sha256(json.dumps(
        values, sort_keys=True, separators=(",", ":")
    ).encode()).hexdigest()


def _am142_receipt_addresses() -> dict[int, dict[str, object]]:
    if not AM142_RECEIPT.exists():
        return {}
    receipt = json.loads(AM142_RECEIPT.read_text(encoding="utf-8"))
    if not receipt.get("target_compile_verified"):
        return {}
    result = {}
    for address in receipt.get("candidate_addresses", []):
        result[int(address, 16)] = {
            "semantic_receipt_available": True,
            "semantic_receipt_manifest": str(AM142_RECEIPT.relative_to(ROOT)),
            "semantic_receipt_object_sha256": receipt["object_sha256"],
            "semantic_receipt_symbol_count": receipt["symbol_count"],
            "semantic_receipt_target_compile_verified": True,
        }
    return result


def _with_am142_receipt_status(
    entry_address: int,
    frontier: dict[str, object],
) -> dict[str, object]:
    receipt = _am142_receipt_addresses().get(entry_address)
    if receipt is None:
        return frontier
    return {
        **frontier,
        **receipt,
        "implementation_readiness": (
            "semantic_receipt_ready_requires_overlay_routing"
        ),
    }


def _ranges(values: list[int]) -> list[dict[str, int]]:
    if not values:
        return []
    ordered = sorted(values)
    result = []
    start = previous = ordered[0]
    for value in ordered[1:]:
        if value == previous + 1:
            previous = value
            continue
        result.append({"first": start, "last": previous, "count": previous - start + 1})
        start = previous = value
    result.append({"first": start, "last": previous, "count": previous - start + 1})
    return result


def _am_helper_number(source: str) -> int | None:
    match = AM_HELPER_RE.search(Path(source).name)
    return int(match.group(1)) if match else None


def _raw_helper_batches(rows: list[dict], ranges: list[dict[str, int]]) -> list[dict]:
    by_number = {
        _am_helper_number(row["source"]): row
        for row in rows
        if _am_helper_number(row["source"]) is not None
    }
    batches = []
    for item in ranges:
        members = [
            by_number[number]
            for number in range(item["first"], item["last"] + 1)
            if number in by_number
        ]
        batches.append({
            **item,
            "inst_directive_bytes": sum(
                row["inst_directive_bytes"] for row in members),
            "largest_source": max(
                (
                    {
                        "source": row["source"],
                        "inst_directive_bytes": row["inst_directive_bytes"],
                        "source_sha256": row["source_sha256"],
                    }
                    for row in members
                ),
                key=lambda row: (row["inst_directive_bytes"], row["source"]),
            ),
        })
    return sorted(
        batches,
        key=lambda row: (-row["inst_directive_bytes"], row["first"]),
    )


def _top_batch_decomposition(rows: list[dict], batch: dict) -> dict:
    members = []
    for row in rows:
        number = _am_helper_number(row["source"])
        if number is None or not (batch["first"] <= number <= batch["last"]):
            continue
        members.append({
            "number": number,
            "source": row["source"],
            "inst_directive_bytes": row["inst_directive_bytes"],
            "source_sha256": row["source_sha256"],
        })
    members.sort(key=lambda row: (-row["inst_directive_bytes"], row["number"]))
    # Split the largest AM helper run into deterministic roughly equal spans so
    # future source-replacement work can close it incrementally.
    subranges = []
    start = batch["first"]
    while start <= batch["last"]:
        end = min(start + 18, batch["last"])
        subset = [
            row for row in members
            if start <= row["number"] <= end
        ]
        subranges.append({
            "first": start,
            "last": end,
            "count": len(subset),
            "inst_directive_bytes": sum(
                row["inst_directive_bytes"] for row in subset),
            "largest_source": max(
                subset,
                key=lambda row: (row["inst_directive_bytes"], row["source"]),
            ),
        })
        start = end + 1
    return {
        "first": batch["first"],
        "last": batch["last"],
        "count": batch["count"],
        "inst_directive_bytes": batch["inst_directive_bytes"],
        "top_sources": members[:20],
        "subranges": sorted(
            subranges,
            key=lambda row: (-row["inst_directive_bytes"], row["first"]),
        ),
    }


def _focused_subrange_decomposition(
    rows: list[dict],
    mixed_sources: list[dict],
    first: int,
    last: int,
) -> dict:
    mixed_by_source = {row["source"]: row for row in mixed_sources}
    members = []
    reason_counts: dict[str, int] = {}
    for row in rows:
        number = _am_helper_number(row["source"])
        if number is None or not (first <= number <= last):
            continue
        mixed = mixed_by_source[row["source"]]
        for reason in mixed["reasons"]:
            reason_counts[reason] = reason_counts.get(reason, 0) + 1
        members.append({
            "number": number,
            "source": row["source"],
            "inst_directive_bytes": row["inst_directive_bytes"],
            "source_sha256": row["source_sha256"],
            "blocked_function_count": mixed["blocked_function_count"],
            "blocked_function_bytes": mixed["blocked_function_bytes"],
            "reasons": mixed["reasons"],
            "blocked_functions": mixed["blocked_functions"],
        })
    members.sort(key=lambda row: (-row["inst_directive_bytes"], row["number"]))
    top_source = members[0] if members else None
    top_blocked_functions = [] if top_source is None else top_source[
        "blocked_functions"]
    next_source = members[1] if len(members) > 1 else None
    next_source_blocked_functions = [] if next_source is None else next_source[
        "blocked_functions"]
    third_source = members[2] if len(members) > 2 else None
    third_source_blocked_functions = [] if third_source is None else third_source[
        "blocked_functions"]
    return {
        "first": first,
        "last": last,
        "count": len(members),
        "inst_directive_bytes": sum(
            row["inst_directive_bytes"] for row in members),
        "reason_counts": dict(sorted(reason_counts.items())),
        "top_source_function_frontier": None if top_source is None else {
            "number": top_source["number"],
            "source": top_source["source"],
            "inst_directive_bytes": top_source["inst_directive_bytes"],
            "blocked_function_count": top_source["blocked_function_count"],
            "blocked_function_bytes": top_source["blocked_function_bytes"],
            "blocked_functions": top_blocked_functions,
            "largest_blocked_function_shape": _raw_function_shape(
                top_source["source"],
                top_blocked_functions[0]["function"],
            ),
            "next_blocked_function_shape": _raw_function_shape(
                top_source["source"],
                top_blocked_functions[1]["function"],
            ),
            "third_blocked_function_shape": _raw_function_shape(
                top_source["source"],
                top_blocked_functions[2]["function"],
            ),
            "fourth_blocked_function_shape": _raw_function_shape(
                top_source["source"],
                top_blocked_functions[3]["function"],
            ),
            "fifth_blocked_function_shape": _raw_function_shape(
                top_source["source"],
                top_blocked_functions[4]["function"],
            ),
            "sixth_blocked_function_shape": _raw_function_shape(
                top_source["source"],
                top_blocked_functions[5]["function"],
            ),
            "seventh_blocked_function_shape": _raw_function_shape(
                top_source["source"],
                top_blocked_functions[6]["function"],
            ),
            "eighth_blocked_function_shape": _raw_function_shape(
                top_source["source"],
                top_blocked_functions[7]["function"],
            ),
            "ninth_blocked_function_shape": _raw_function_shape(
                top_source["source"],
                top_blocked_functions[8]["function"],
            ),
            "tenth_blocked_function_shape": _raw_function_shape(
                top_source["source"],
                top_blocked_functions[9]["function"],
            ),
            "eleventh_blocked_function_shape": _raw_function_shape(
                top_source["source"],
                top_blocked_functions[10]["function"],
            ),
            "twelfth_blocked_function_shape": _raw_function_shape(
                top_source["source"],
                top_blocked_functions[11]["function"],
            ),
            "thirteenth_blocked_function_shape": _raw_function_shape(
                top_source["source"],
                top_blocked_functions[12]["function"],
            ),
            "fourteenth_blocked_function_shape": _raw_function_shape(
                top_source["source"],
                top_blocked_functions[13]["function"],
            ),
            "fifteenth_blocked_function_shape": _raw_function_shape(
                top_source["source"],
                top_blocked_functions[14]["function"],
            ),
            "sixteenth_blocked_function_shape": _raw_function_shape(
                top_source["source"],
                top_blocked_functions[15]["function"],
            ),
            "seventeenth_blocked_function_shape": _raw_function_shape(
                top_source["source"],
                top_blocked_functions[16]["function"],
            ),
            "eighteenth_blocked_function_shape": _raw_function_shape(
                top_source["source"],
                top_blocked_functions[17]["function"],
            ),
            "nineteenth_blocked_function_shape": _raw_function_shape(
                top_source["source"],
                top_blocked_functions[18]["function"],
            ),
            "twentieth_blocked_function_shape": _raw_function_shape(
                top_source["source"],
                top_blocked_functions[19]["function"],
            ),
            "twenty_first_blocked_function_shape": _raw_function_shape(
                top_source["source"],
                top_blocked_functions[20]["function"],
            ),
            "twenty_second_blocked_function_shape": _raw_function_shape(
                top_source["source"],
                top_blocked_functions[21]["function"],
            ),
            "twenty_third_blocked_function_shape": _raw_function_shape(
                top_source["source"],
                top_blocked_functions[22]["function"],
            ),
            "twenty_fourth_blocked_function_shape": _raw_function_shape(
                top_source["source"],
                top_blocked_functions[23]["function"],
            ),
            "twenty_fifth_blocked_function_shape": _raw_function_shape(
                top_source["source"],
                top_blocked_functions[24]["function"],
            ),
            "twenty_sixth_blocked_function_shape": _raw_function_shape(
                top_source["source"],
                top_blocked_functions[25]["function"],
            ),
            "twenty_seventh_blocked_function_shape": _raw_function_shape(
                top_source["source"],
                top_blocked_functions[26]["function"],
            ),
            "twenty_eighth_blocked_function_shape": _raw_function_shape(
                top_source["source"],
                top_blocked_functions[27]["function"],
            ),
            "twenty_ninth_blocked_function_shape": _raw_function_shape(
                top_source["source"],
                top_blocked_functions[28]["function"],
            ),
            "thirtieth_blocked_function_shape": _raw_function_shape(
                top_source["source"],
                top_blocked_functions[29]["function"],
            ),
        },
        "next_source_function_frontier": None if next_source is None else {
            "number": next_source["number"],
            "source": next_source["source"],
            "inst_directive_bytes": next_source["inst_directive_bytes"],
            "blocked_function_count": next_source["blocked_function_count"],
            "blocked_function_bytes": next_source["blocked_function_bytes"],
            "blocked_functions": next_source_blocked_functions[:10],
            "blocked_function_shapes": [
                _raw_function_shape(next_source["source"], row["function"])
                for row in next_source_blocked_functions
            ],
            "largest_blocked_function_shape": _raw_function_shape(
                next_source["source"],
                next_source_blocked_functions[0]["function"],
            ),
            "next_blocked_function_shape": _raw_function_shape(
                next_source["source"],
                next_source_blocked_functions[1]["function"],
            ),
            "third_blocked_function_shape": _raw_function_shape(
                next_source["source"],
                next_source_blocked_functions[2]["function"],
            ),
            "fourth_blocked_function_shape": _raw_function_shape(
                next_source["source"],
                next_source_blocked_functions[3]["function"],
            ),
            "fifth_blocked_function_shape": _raw_function_shape(
                next_source["source"],
                next_source_blocked_functions[4]["function"],
            ),
            "sixth_blocked_function_shape": _raw_function_shape(
                next_source["source"],
                next_source_blocked_functions[5]["function"],
            ),
            "seventh_blocked_function_shape": _raw_function_shape(
                next_source["source"],
                next_source_blocked_functions[6]["function"],
            ),
            "eighth_blocked_function_shape": _raw_function_shape(
                next_source["source"],
                next_source_blocked_functions[7]["function"],
            ),
            "ninth_blocked_function_shape": _raw_function_shape(
                next_source["source"],
                next_source_blocked_functions[8]["function"],
            ),
            "tenth_blocked_function_shape": _raw_function_shape(
                next_source["source"],
                next_source_blocked_functions[9]["function"],
            ),
        },
        "third_source_function_frontier": None if third_source is None else {
            "number": third_source["number"],
            "source": third_source["source"],
            "inst_directive_bytes": third_source["inst_directive_bytes"],
            "blocked_function_count": third_source["blocked_function_count"],
            "blocked_function_bytes": third_source["blocked_function_bytes"],
            "blocked_functions": third_source_blocked_functions,
            "blocked_function_shapes": [
                _raw_function_shape(third_source["source"], row["function"])
                for row in third_source_blocked_functions
            ],
        },
        "source_function_frontiers": [
            {
                "number": member["number"],
                "source": member["source"],
                "inst_directive_bytes": member["inst_directive_bytes"],
                "blocked_function_count": member["blocked_function_count"],
                "blocked_function_bytes": member["blocked_function_bytes"],
                "blocked_functions": member["blocked_functions"],
                "blocked_function_shapes": [
                    _raw_function_shape(member["source"], row["function"])
                    for row in member["blocked_functions"]
                ],
            }
            for member in members
        ],
        "top_sources": members,
    }


def _largest_source_function_frontier(
    rows: list[dict],
    mixed_sources: list[dict],
) -> dict:
    mixed_by_source = {row["source"]: row for row in mixed_sources}
    largest = max(
        rows,
        key=lambda row: (row["inst_directive_bytes"], row["source"]),
    )
    mixed = mixed_by_source[largest["source"]]
    largest_function = mixed["blocked_functions"][0]
    next_blocked_function = (
        mixed["blocked_functions"][1]
        if len(mixed["blocked_functions"]) > 1 else None
    )
    third_blocked_function = (
        mixed["blocked_functions"][2]
        if len(mixed["blocked_functions"]) > 2 else None
    )
    fourth_blocked_function = (
        mixed["blocked_functions"][3]
        if len(mixed["blocked_functions"]) > 3 else None
    )
    fifth_blocked_function = (
        mixed["blocked_functions"][4]
        if len(mixed["blocked_functions"]) > 4 else None
    )
    sixth_blocked_function = (
        mixed["blocked_functions"][5]
        if len(mixed["blocked_functions"]) > 5 else None
    )
    seventh_blocked_function = (
        mixed["blocked_functions"][6]
        if len(mixed["blocked_functions"]) > 6 else None
    )
    eighth_blocked_function = (
        mixed["blocked_functions"][7]
        if len(mixed["blocked_functions"]) > 7 else None
    )
    ninth_blocked_function = (
        mixed["blocked_functions"][8]
        if len(mixed["blocked_functions"]) > 8 else None
    )
    tenth_blocked_function = (
        mixed["blocked_functions"][9]
        if len(mixed["blocked_functions"]) > 9 else None
    )
    eleventh_blocked_function = (
        mixed["blocked_functions"][10]
        if len(mixed["blocked_functions"]) > 10 else None
    )
    twelfth_blocked_function = (
        mixed["blocked_functions"][11]
        if len(mixed["blocked_functions"]) > 11 else None
    )
    thirteenth_blocked_function = (
        mixed["blocked_functions"][12]
        if len(mixed["blocked_functions"]) > 12 else None
    )
    fourteenth_blocked_function = (
        mixed["blocked_functions"][13]
        if len(mixed["blocked_functions"]) > 13 else None
    )
    fifteenth_blocked_function = (
        mixed["blocked_functions"][14]
        if len(mixed["blocked_functions"]) > 14 else None
    )
    sixteenth_blocked_function = (
        mixed["blocked_functions"][15]
        if len(mixed["blocked_functions"]) > 15 else None
    )
    seventeenth_blocked_function = (
        mixed["blocked_functions"][16]
        if len(mixed["blocked_functions"]) > 16 else None
    )
    eighteenth_blocked_function = (
        mixed["blocked_functions"][17]
        if len(mixed["blocked_functions"]) > 17 else None
    )
    nineteenth_blocked_function = (
        mixed["blocked_functions"][18]
        if len(mixed["blocked_functions"]) > 18 else None
    )
    twentieth_blocked_function = (
        mixed["blocked_functions"][19]
        if len(mixed["blocked_functions"]) > 19 else None
    )
    twenty_first_blocked_function = (
        mixed["blocked_functions"][20]
        if len(mixed["blocked_functions"]) > 20 else None
    )
    twenty_second_blocked_function = (
        mixed["blocked_functions"][21]
        if len(mixed["blocked_functions"]) > 21 else None
    )
    twenty_third_blocked_function = (
        mixed["blocked_functions"][22]
        if len(mixed["blocked_functions"]) > 22 else None
    )
    twenty_fourth_blocked_function = (
        mixed["blocked_functions"][23]
        if len(mixed["blocked_functions"]) > 23 else None
    )
    twenty_fifth_blocked_function = (
        mixed["blocked_functions"][24]
        if len(mixed["blocked_functions"]) > 24 else None
    )
    twenty_sixth_blocked_function = (
        mixed["blocked_functions"][25]
        if len(mixed["blocked_functions"]) > 25 else None
    )
    twenty_seventh_blocked_function = (
        mixed["blocked_functions"][26]
        if len(mixed["blocked_functions"]) > 26 else None
    )
    return {
        "number": _am_helper_number(largest["source"]),
        "source": largest["source"],
        "inst_directive_bytes": largest["inst_directive_bytes"],
        "source_sha256": largest["source_sha256"],
        "blocked_function_count": mixed["blocked_function_count"],
        "blocked_function_bytes": mixed["blocked_function_bytes"],
        "reasons": mixed["reasons"],
        "blocked_functions": mixed["blocked_functions"],
        "largest_function_shape": _raw_function_shape(
            largest["source"],
            largest_function["function"],
        ),
        "next_blocked_function_shape": (
            None if next_blocked_function is None else _raw_function_shape(
                largest["source"],
                next_blocked_function["function"],
            )
        ),
        "third_blocked_function_shape": (
            None if third_blocked_function is None else _raw_function_shape(
                largest["source"],
                third_blocked_function["function"],
            )
        ),
        "fourth_blocked_function_shape": (
            None if fourth_blocked_function is None else _raw_function_shape(
                largest["source"],
                fourth_blocked_function["function"],
            )
        ),
        "fifth_blocked_function_shape": (
            None if fifth_blocked_function is None else _raw_function_shape(
                largest["source"],
                fifth_blocked_function["function"],
            )
        ),
        "sixth_blocked_function_shape": (
            None if sixth_blocked_function is None else _raw_function_shape(
                largest["source"],
                sixth_blocked_function["function"],
            )
        ),
        "seventh_blocked_function_shape": (
            None if seventh_blocked_function is None else _raw_function_shape(
                largest["source"],
                seventh_blocked_function["function"],
            )
        ),
        "eighth_blocked_function_shape": (
            None if eighth_blocked_function is None else _raw_function_shape(
                largest["source"],
                eighth_blocked_function["function"],
            )
        ),
        "ninth_blocked_function_shape": (
            None if ninth_blocked_function is None else _raw_function_shape(
                largest["source"],
                ninth_blocked_function["function"],
            )
        ),
        "tenth_blocked_function_shape": (
            None if tenth_blocked_function is None else _raw_function_shape(
                largest["source"],
                tenth_blocked_function["function"],
            )
        ),
        "eleventh_blocked_function_shape": (
            None if eleventh_blocked_function is None else _raw_function_shape(
                largest["source"],
                eleventh_blocked_function["function"],
            )
        ),
        "twelfth_blocked_function_shape": (
            None if twelfth_blocked_function is None else _raw_function_shape(
                largest["source"],
                twelfth_blocked_function["function"],
            )
        ),
        "thirteenth_blocked_function_shape": (
            None if thirteenth_blocked_function is None else _raw_function_shape(
                largest["source"],
                thirteenth_blocked_function["function"],
            )
        ),
        "fourteenth_blocked_function_shape": (
            None if fourteenth_blocked_function is None else _raw_function_shape(
                largest["source"],
                fourteenth_blocked_function["function"],
            )
        ),
        "fifteenth_blocked_function_shape": (
            None if fifteenth_blocked_function is None else _raw_function_shape(
                largest["source"],
                fifteenth_blocked_function["function"],
            )
        ),
        "sixteenth_blocked_function_shape": (
            None if sixteenth_blocked_function is None else _raw_function_shape(
                largest["source"],
                sixteenth_blocked_function["function"],
            )
        ),
        "seventeenth_blocked_function_shape": (
            None if seventeenth_blocked_function is None else _raw_function_shape(
                largest["source"],
                seventeenth_blocked_function["function"],
            )
        ),
        "eighteenth_blocked_function_shape": (
            None if eighteenth_blocked_function is None else _raw_function_shape(
                largest["source"],
                eighteenth_blocked_function["function"],
            )
        ),
        "nineteenth_blocked_function_shape": (
            None if nineteenth_blocked_function is None else _raw_function_shape(
                largest["source"],
                nineteenth_blocked_function["function"],
            )
        ),
        "twentieth_blocked_function_shape": (
            None if twentieth_blocked_function is None else _raw_function_shape(
                largest["source"],
                twentieth_blocked_function["function"],
            )
        ),
        "twenty_first_blocked_function_shape": (
            None if twenty_first_blocked_function is None else _raw_function_shape(
                largest["source"],
                twenty_first_blocked_function["function"],
            )
        ),
        "twenty_second_blocked_function_shape": (
            None if twenty_second_blocked_function is None else _raw_function_shape(
                largest["source"],
                twenty_second_blocked_function["function"],
            )
        ),
        "twenty_third_blocked_function_shape": (
            None if twenty_third_blocked_function is None else _raw_function_shape(
                largest["source"],
                twenty_third_blocked_function["function"],
            )
        ),
        "twenty_fourth_blocked_function_shape": (
            None if twenty_fourth_blocked_function is None else _raw_function_shape(
                largest["source"],
                twenty_fourth_blocked_function["function"],
            )
        ),
        "twenty_fifth_blocked_function_shape": (
            None if twenty_fifth_blocked_function is None else _raw_function_shape(
                largest["source"],
                twenty_fifth_blocked_function["function"],
            )
        ),
        "twenty_sixth_blocked_function_shape": (
            None if twenty_sixth_blocked_function is None else _raw_function_shape(
                largest["source"],
                twenty_sixth_blocked_function["function"],
            )
        ),
        "twenty_seventh_blocked_function_shape": (
            None if twenty_seventh_blocked_function is None else _raw_function_shape(
                largest["source"],
                twenty_seventh_blocked_function["function"],
            )
        ),
    }


def _raw_function_shape(source: str, function: str) -> dict[str, object]:
    text = (ROOT / source).read_text()
    match = re.search(
        rf"void {re.escape(function)}\(void\)\n"
        r"\{\n    __asm__ volatile\(\n(?P<body>.*?)\n    \);\n\}",
        text,
        re.S,
    )
    if match is None:
        raise RuntimeError(f"cannot find raw function body: {function}")
    halfwords = [
        int(value, 16)
        for value in re.findall(
            r"\.inst\.n\s+0x([0-9a-fA-F]+)",
            match.group("body"),
        )
    ]
    prologue_indexes = [
        index for index, value in enumerate(halfwords)
        if value & 0xFF00 == 0xB500
    ]
    return_indexes = [
        index for index, value in enumerate(halfwords)
        if value & 0xFF00 == 0xBD00 or value == 0x4770
    ]
    branch_like_indexes = [
        index for index, value in enumerate(halfwords)
        if value & 0xF000 == 0xD000 or value & 0xF800 == 0xE000
    ]
    first_prologue = prologue_indexes[0] if prologue_indexes else None
    first_return = return_indexes[0] if return_indexes else None
    base_address_match = re.search(r"_0x([0-9a-fA-F]+)$", function)
    base_address = (
        int(base_address_match.group(1), 16)
        if base_address_match is not None else None
    )
    entry_candidates = []
    for index, prologue in enumerate(prologue_indexes):
        next_prologue = (
            prologue_indexes[index + 1]
            if index + 1 < len(prologue_indexes) else len(halfwords)
        )
        local_return = next(
            (value for value in return_indexes if value >= prologue),
            None,
        )
        entry_candidates.append({
            "entry_halfword_index": prologue,
            "entry_byte_offset": prologue * 2,
            "entry_address": (
                base_address + prologue * 2
                if base_address is not None else None
            ),
            "prologue_halfword": f"0x{halfwords[prologue]:04x}",
            "next_entry_halfword_index": (
                next_prologue if next_prologue != len(halfwords) else None
            ),
            "next_entry_address": (
                base_address + next_prologue * 2
                if base_address is not None and next_prologue != len(halfwords)
                else None
            ),
            "span_to_next_entry_bytes": (next_prologue - prologue) * 2,
            "return_halfword_index": local_return,
            "return_byte_offset": (
                local_return * 2 if local_return is not None else None
            ),
            "return_address": (
                base_address + local_return * 2
                if base_address is not None and local_return is not None
                else None
            ),
            "return_halfword": (
                f"0x{halfwords[local_return]:04x}"
                if local_return is not None else None
            ),
            "bytes_through_return": (
                (local_return - prologue + 1) * 2
                if local_return is not None else None
            ),
            "post_return_tail_bytes": (
                (next_prologue - local_return - 1) * 2
                if local_return is not None and local_return < next_prologue
                else None
            ),
            "post_return_tail_halfwords": (
                [
                    f"0x{value:04x}"
                    for value in halfwords[local_return + 1:next_prologue]
                ]
                if local_return is not None and local_return < next_prologue
                else []
            ),
            "overlaps_next_entry": (
                local_return is not None and local_return >= next_prologue
            ),
            "has_local_return": local_return is not None,
        })
    bounded_entries = [
        row for row in entry_candidates
        if row["has_local_return"] and not row["overlaps_next_entry"]
    ]
    ranked_entries = sorted(
        bounded_entries,
        key=lambda row: (
            row["bytes_through_return"],
            row["span_to_next_entry_bytes"],
            row["entry_byte_offset"],
        ),
    )
    ranked_queue = [
        {
            **row,
            "rank": rank,
            "status": "requires_c_pull_through",
            "implementation_readiness": "bounded_local_return_chunk",
            "thumb_decode_summary": _thumb_decode_summary(
                halfwords,
                row,
                include_instructions=False,
            ),
            "semantic_frontier": _am115_ranked_entry_semantic_frontier(
                row,
            ),
        }
        for rank, row in enumerate(ranked_entries, 1)
    ]
    next_entry_candidate = None if not ranked_queue else dict(ranked_queue[0])
    if next_entry_candidate is not None:
        next_entry_candidate.pop("thumb_decode_summary", None)
        if next_entry_candidate.get("semantic_frontier") is None:
            next_entry_candidate.pop("semantic_frontier", None)
        next_entry_candidate["thumb_decode"] = _thumb_decode_summary(
            halfwords,
            next_entry_candidate,
        )
        next_entry_candidate["semantic_model"] = (
            _am115_0x546e02_semantic_model_summary(next_entry_candidate)
        )
    return {
        "directive_halfword_count": len(halfwords),
        "directive_byte_count": len(halfwords) * 2,
        "first_halfwords": [f"0x{value:04x}" for value in halfwords[:12]],
        "first_prologue_halfword_index": first_prologue,
        "prefix_before_first_prologue_halfwords": (
            first_prologue if first_prologue is not None else len(halfwords)
        ),
        "push_like_prologue_count": len(prologue_indexes),
        "return_like_count": len(return_indexes),
        "first_return_halfword_index": first_return,
        "branch_like_halfword_count": len(branch_like_indexes),
        "zero_halfword_count": sum(1 for value in halfwords if value == 0),
        "post_first_return_halfword_count": (
            0 if first_return is None else len(halfwords) - first_return - 1
        ),
        "entry_candidate_count": len(entry_candidates),
        "entry_candidates": entry_candidates,
        "bounded_local_return_entry_count": len(bounded_entries),
        "unbounded_or_overlapping_entry_count": (
            len(entry_candidates) - len(bounded_entries)
        ),
        "ranked_entry_semantic_rollup": _ranked_entry_semantic_rollup(
            ranked_queue,
            next_entry_candidate,
        ),
        "ranked_entry_pull_through_queue": ranked_queue,
        "next_entry_pull_through_candidate": next_entry_candidate,
        "function_semantic_frontier": _am115_function_semantic_frontier(
            function,
            {
                "base_address": base_address,
                "first_return_halfword_index": first_return,
                "directive_halfword_count": len(halfwords),
                "directive_byte_count": len(halfwords) * 2,
            },
        ),
    }


def _am115_function_semantic_frontier(
    function: str,
    shape: dict[str, object],
) -> dict[str, object] | None:
    if function == "open_cfw_runtime_am115_0x00544d60":
        return {
            "available": True,
            "kind": "prologueless_retry_transaction_tail_fill_u16_result",
            "entry_address": shape["base_address"],
            "uses_existing_stack_frame": True,
            "retry_limit": 3,
            "result_pointer_register": "r5",
            "scratch_buffer_offset": 0x10,
            "scratch_buffer_bytes": 0x1A,
            "transaction_call": 0x00544532,
            "cleanup_call": 0x00544660,
            "debug_gate_call": 0x004050EE,
            "debug_log_call": 0x00405594,
            "debug_emit_call": 0x00404EBE,
            "short_read_threshold": 2,
            "success_return_value": 0,
            "failure_return_value": -1,
            "terminal_return_halfword_index": shape["first_return_halfword_index"],
            "implementation_readiness": "needs_retry_tail_semantics",
            "firmware_routing_status": "not_yet_routed_into_overlay",
        }
    if function == "open_cfw_runtime_am115_0x005456f6":
        return {
            "available": True,
            "kind": "split_status_query_debug_tail_and_embedded_probe",
            "entry_address": shape["base_address"],
            "uses_existing_stack_frame": True,
            "prefix_selector_register": "r2",
            "prefix_status_stack_offset": 0x10,
            "prefix_success_return_value": 0,
            "prefix_default_error_return": -1,
            "prefix_terminal_return_halfword_index": (
                shape["first_return_halfword_index"]
            ),
            "embedded_entry_address": 0x005457B4,
            "embedded_stack_frame_bytes": 0x14,
            "embedded_status_stack_offset": 0x10,
            "embedded_clear_call": 0x00404104,
            "embedded_query_call": 0x00544E98,
            "embedded_timeout": 0xC8,
            "debug_gate_call": 0x004050EE,
            "debug_log_call": 0x00405594,
            "debug_emit_call": 0x00404EBE,
            "implementation_readiness": "needs_split_status_query_semantics",
            "firmware_routing_status": "not_yet_routed_into_overlay",
        }
    if function == "open_cfw_runtime_am115_0x005453fe":
        return {
            "available": True,
            "kind": "split_u8_status_query_tail_and_embedded_probe_pair",
            "entry_address": shape["base_address"],
            "uses_existing_stack_frame": True,
            "prefix_status_stack_offset": 0x26,
            "prefix_cleanup_stack_offset": 0x14,
            "prefix_cleanup_call": 0x00544660,
            "prefix_failure_return_value": -1,
            "first_embedded_entry_address": 0x00545438,
            "second_embedded_entry_address": 0x00545504,
            "embedded_status_stack_offset": 0x10,
            "embedded_stack_frame_bytes": 0x14,
            "debug_gate_call": 0x004050EE,
            "debug_log_call": 0x00405594,
            "debug_emit_call": 0x00404EBE,
            "implementation_readiness": "needs_split_u8_status_probe_semantics",
            "firmware_routing_status": "not_yet_routed_into_overlay",
        }
    if function == "open_cfw_runtime_am115_0x00545320":
        return {
            "available": True,
            "kind": "prologueless_retry_read_status_tail_with_cleanup",
            "entry_address": shape["base_address"],
            "uses_existing_stack_frame": True,
            "retry_service_call": 0x00543B0C,
            "read_call": 0x00543D26,
            "cleanup_stack_offset": 0x14,
            "cleanup_call": 0x00544660,
            "status_count_stack_offset": 0x26,
            "source_cursor_stack_offset": 0x22,
            "output_register": "r5",
            "transaction_context_register": "r8",
            "debug_gate_call": 0x004050EE,
            "debug_log_call": 0x00405594,
            "debug_emit_call": 0x00404EBE,
            "success_return_value": 0,
            "implementation_readiness": "needs_retry_read_status_tail_semantics",
            "firmware_routing_status": "not_yet_routed_into_overlay",
        }
    if function == "open_cfw_runtime_am115_0x00544f6c":
        return {
            "available": True,
            "kind": "prologueless_u16_status_pack_tail_with_cleanup",
            "entry_address": shape["base_address"],
            "uses_existing_stack_frame": True,
            "status_output_register": "r5",
            "status_pack_source_registers": ["r0", "r1"],
            "status_pack_operation": "r1_or_r0_shift_left_8",
            "success_cleanup_stack_offset": 0x10,
            "cleanup_call": 0x00544660,
            "failure_status_stack_offset": 0x22,
            "success_return_value": 0,
            "failure_return_value": -1,
            "caller_epilogue_stack_adjust": 0x30,
            "debug_gate_call": 0x004050EE,
            "debug_log_call": 0x00405594,
            "debug_emit_call": 0x00404EBE,
            "implementation_readiness": "needs_u16_status_pack_tail_semantics",
            "firmware_routing_status": "not_yet_routed_into_overlay",
        }
    if function == "open_cfw_runtime_am115_0x005450a4":
        return {
            "available": True,
            "kind": "prologueless_retry_transaction_tail_fill_u8_result",
            "entry_address": shape["base_address"],
            "uses_existing_stack_frame": True,
            "retry_counter_register": "r7",
            "retry_limit": 3,
            "scratch_buffer_offset": 0x14,
            "scratch_buffer_bytes": 0x1A,
            "result_pointer_register": "r5",
            "result_status_stack_offset": 0x26,
            "source_cursor_stack_offset": 0x22,
            "transaction_call": 0x00544532,
            "cleanup_call": 0x00544660,
            "debug_gate_call": 0x004050EE,
            "debug_log_call": 0x00405594,
            "debug_emit_call": 0x00404EBE,
            "success_return_value": 0,
            "caller_epilogue_stack_adjust": 0x34,
            "terminal_return_halfword_index": shape["first_return_halfword_index"],
            "implementation_readiness": (
                "needs_retry_transaction_u8_tail_semantics"
            ),
            "firmware_routing_status": "not_yet_routed_into_overlay",
        }
    if function == "open_cfw_runtime_am115_0x005477ac":
        return {
            "available": True,
            "kind": "prologueless_dual_path_filter_join_tail",
            "entry_address": shape["base_address"],
            "uses_existing_stack_frame": True,
            "primary_path_stack_offset": 0x520,
            "secondary_path_stack_offset": 0x41C,
            "primary_source_stack_offset": 0x61C,
            "primary_filter_output_stack_offset": 0x31C,
            "secondary_filter_output_stack_offset": 0x21C,
            "path_append_call": 0x0052FCA0,
            "path_copy_call": 0x004135C0,
            "path_clear_call": 0x00404104,
            "empty_path_fill_call": 0x00455560,
            "strlen_call": 0x0041245C,
            "filter_join_call": 0x00546AC8,
            "filter_join_call_count": 2,
            "failure_log_call": 0x0043B40E,
            "failure_return_value": 0,
            "delimiter_literal": "/",
            "implementation_readiness": "needs_dual_path_filter_join_tail_semantics",
            "firmware_routing_status": "not_yet_routed_into_overlay",
        }
    if function == "open_cfw_runtime_am115_0x00545264":
        return {
            "available": True,
            "kind": "prologueless_transaction_setup_tail_to_retry_read_status",
            "entry_address": shape["base_address"],
            "uses_existing_stack_frame": True,
            "scratch_buffer_offset": 0x14,
            "scratch_buffer_bytes": 0x1A,
            "parameter_buffer_offset": 0x30,
            "status_word_stack_offset": 0x10,
            "clear_call": 0x00404104,
            "preflight_call": 0x00543AA8,
            "literal_copy_call": 0x00401C24,
            "parameter_validate_call": 0x00557B58,
            "retry_service_call": 0x00543B0C,
            "transaction_start_call": 0x00544462,
            "success_tail_entry": 0x00545320,
            "transaction_context_register": "r8",
            "retry_counter_register": "r7",
            "debug_gate_call": 0x004050EE,
            "debug_log_call": 0x00405594,
            "debug_emit_call": 0x00404EBE,
            "implementation_readiness": (
                "needs_transaction_setup_tail_semantics"
            ),
            "firmware_routing_status": "not_yet_routed_into_overlay",
        }
    if function == "open_cfw_runtime_am115_0x005476e4":
        return {
            "available": True,
            "kind": "prologueless_dual_path_input_staging_tail",
            "entry_address": shape["base_address"],
            "uses_existing_stack_frame": True,
            "max_path_length": 0xFF,
            "primary_length_stack_offset": 0x04,
            "secondary_length_stack_offset": 0x00,
            "primary_path_stack_offset": 0x71C,
            "secondary_path_stack_offset": 0x61C,
            "joined_path_stack_offset": 0x520,
            "bounded_copy_call": 0x00401C04,
            "joined_path_clear_call": 0x00404104,
            "failure_log_call": 0x0043B40E,
            "failure_return_value": 0,
            "continuation_tail_entry": 0x005477AC,
            "continuation_kind": "prologueless_dual_path_filter_join_tail",
            "implementation_readiness": (
                "needs_dual_path_input_staging_tail_semantics"
            ),
            "firmware_routing_status": "not_yet_routed_into_overlay",
        }
    if function == "open_cfw_runtime_am115_0x00544cf6":
        return {
            "available": True,
            "kind": "literal_prefix_embedded_retry_search_entry",
            "entry_address": shape["base_address"],
            "embedded_entry_address": 0x00544D0C,
            "prefix_literal_halfwords": 11,
            "stack_frame_bytes": 0x30,
            "input_register": "r1",
            "context_register": "r2",
            "loop_index_register": "r6",
            "result_register": "r4",
            "null_input_return_value": -1,
            "default_result_value": -1,
            "debug_gate_call": 0x004050EE,
            "debug_log_call": 0x00405594,
            "debug_emit_call": 0x00404EBE,
            "implementation_readiness": (
                "needs_embedded_retry_search_entry_semantics"
            ),
            "firmware_routing_status": "not_yet_routed_into_overlay",
        }
    if function == "open_cfw_runtime_am115_0x0054566c":
        return {
            "available": True,
            "kind": "prologueless_u8_status_debug_return_tail",
            "entry_address": shape["base_address"],
            "uses_existing_stack_frame": True,
            "status_register": "r5",
            "status_transform": "uxtb",
            "success_return_value": 0,
            "epilogue_stack_adjust": 0x14,
            "terminal_return_halfword_index": shape["first_return_halfword_index"],
            "post_return_literal_halfwords": 9,
            "embedded_following_entry_address": 0x005456D4,
            "debug_gate_call": 0x004050EE,
            "debug_log_call": 0x00405594,
            "debug_emit_call": 0x00404EBE,
            "implementation_readiness": "needs_u8_status_debug_tail_semantics",
            "firmware_routing_status": "not_yet_routed_into_overlay",
        }
    if function == "open_cfw_runtime_am115_0x0054503a":
        return {
            "available": True,
            "kind": "literal_prefix_embedded_retry_option_initializer",
            "entry_address": shape["base_address"],
            "embedded_entry_address": 0x00545044,
            "prefix_literal_halfwords": 5,
            "stack_frame_bytes": 0x30,
            "input_register": "r1",
            "context_register": "r2",
            "option_source_register": "r0",
            "option_stack_offset": 0x10,
            "loop_index_register": "r7",
            "result_register": "r4",
            "null_input_return_value": -1,
            "default_result_value": -1,
            "debug_gate_call": 0x004050EE,
            "debug_log_call": 0x00405594,
            "implementation_readiness": (
                "needs_embedded_retry_option_initializer_semantics"
            ),
            "firmware_routing_status": "not_yet_routed_into_overlay",
        }
    if function == "open_cfw_runtime_am115_0x005455e4":
        return {
            "available": True,
            "kind": "prologueless_u16_status_query_via_retry_search_tail",
            "entry_address": shape["base_address"],
            "uses_existing_stack_frame": True,
            "selector_register": "r0",
            "selector_saved_register": "r5",
            "status_stack_offset": 0x10,
            "status_buffer_bytes": 2,
            "clear_call": 0x00404104,
            "retry_search_call": 0x00544D0C,
            "query_timeout": 0xC8,
            "success_status_value": 1,
            "success_tail_entry": 0x0054566E,
            "debug_gate_call": 0x004050EE,
            "debug_log_call": 0x00405594,
            "implementation_readiness": (
                "needs_u16_status_retry_search_tail_semantics"
            ),
            "firmware_routing_status": "not_yet_routed_into_overlay",
        }
    if function == "open_cfw_runtime_am115_0x00545c5a":
        return {
            "available": True,
            "kind": "vfp_wrapper_and_embedded_u64_compare_body",
            "entry_address": shape["base_address"],
            "prefix_literal_halfwords": 3,
            "wrapper_entry_address": 0x00545C60,
            "embedded_compare_entry_address": 0x00545C74,
            "uses_vfp_registers": True,
            "wrapper_call_target": 0x00545C74,
            "compare_stack_registers": ["r4", "r5", "r6", "lr"],
            "exponent_mask": 0x7FF,
            "it_halfword_indexes": [22, 28],
            "implementation_readiness": (
                "needs_vfp_compare_wrapper_and_body_semantics"
            ),
            "firmware_routing_status": "not_yet_routed_into_overlay",
        }
    if function == "open_cfw_runtime_am115_0x00545868":
        return {
            "available": True,
            "kind": "split_debug_tail_literal_pool_and_embedded_status_setup",
            "entry_address": shape["base_address"],
            "uses_existing_stack_frame": True,
            "tail_debug_condition_halfword_index": 0,
            "tail_debug_call": 0x00404EBE,
            "tail_success_return_value": 0,
            "tail_epilogue_stack_adjust": 0x18,
            "terminal_return_halfword_index": shape["first_return_halfword_index"],
            "post_return_literal_halfwords": 8,
            "embedded_status_entry_address": 0x00545890,
            "embedded_status_stack_frame_bytes": 0x14,
            "embedded_clear_call": 0x00404104,
            "embedded_timeout": 0xC8,
            "authenticated_decompile_entry": 0x00545868,
            "authenticated_decompile_kind": "crc16_ccitt_byte_loop",
            "boundary_conflict": (
                "raw_helper_body_decodes_as_prior_debug_tail_plus_literal_pool_"
                "and_following_status_setup"
            ),
            "implementation_readiness": (
                "needs_boundary_reconciliation_before_crc_or_status_semantics"
            ),
            "firmware_routing_status": "not_yet_routed_into_overlay",
        }
    if function == "open_cfw_runtime_am115_0x00545594":
        return {
            "available": True,
            "kind": "prologueless_four_stage_debug_log_dispatch_tail",
            "entry_address": shape["base_address"],
            "uses_existing_stack_frame": True,
            "argument_spill_stack_offset": 0,
            "literal_load_count": 3,
            "log_format_call": 0x00405594,
            "debug_gate_call": 0x004050EE,
            "debug_emit_call": 0x00404EBE,
            "debug_gate_checks": 2,
            "authenticated_decompile_calls": [
                0x0044122A,
                0x00441238,
                0x0044120E,
                0x0044121C,
            ],
            "implementation_readiness": "needs_four_stage_debug_log_tail_semantics",
            "firmware_routing_status": "not_yet_routed_into_overlay",
        }
    if function == "open_cfw_runtime_am115_0x00545644":
        return {
            "available": True,
            "kind": "prologueless_compass_debug_tail_to_shared_return",
            "entry_address": shape["base_address"],
            "uses_existing_stack_frame": True,
            "prefix_halfword_is_prior_wide_call_suffix": True,
            "status_stack_offset": 0x10,
            "debug_gate_call": 0x0043D0CE,
            "debug_emit_call": 0x0043CE9E,
            "debug_emit_code": 0x04800000,
            "debug_gate_checks": 2,
            "zero_status_default_return": -1,
            "shared_return_tail_entry": 0x0054566A,
            "authenticated_decompile_entry": 0x00545644,
            "authenticated_decompile_calls": [
                0x0043D574,
                0x0043D0CE,
                0x0043D0CE,
                0x0043CE9E,
            ],
            "implementation_readiness": (
                "needs_compass_debug_tail_boundary_semantics"
            ),
            "firmware_routing_status": "not_yet_routed_into_overlay",
        }
    if function == "open_cfw_runtime_am115_0x00545844":
        return {
            "available": True,
            "kind": "prologueless_condition_flag_debug_emit_tail",
            "entry_address": shape["base_address"],
            "uses_existing_stack_frame": True,
            "condition_source": "incoming_negative_flag_or_debug_gate_bit29",
            "line_literal": 0x33A,
            "line_stack_offset": 0,
            "condition_stack_offset": 4,
            "log_format_call": 0x0043D574,
            "debug_gate_call": 0x0043D0CE,
            "debug_emit_call": 0x0043CE9E,
            "debug_emit_code": 0x10800000,
            "authenticated_decompile_entry": 0x00545844,
            "authenticated_decompile_calls": [0x0043D0CE, 0x0043CE9E],
            "implementation_readiness": (
                "needs_condition_flag_debug_emit_tail_semantics"
            ),
            "firmware_routing_status": "not_yet_routed_into_overlay",
        }
    if function == "open_cfw_runtime_am115_0x005456d6":
        return {
            "available": True,
            "kind": "prologueless_status_query_setup_tail_with_decompile_conflict",
            "entry_address": shape["base_address"],
            "uses_existing_stack_frame": True,
            "stack_frame_adjust": 0x14,
            "status_stack_offset": 0x10,
            "status_buffer_bytes": 2,
            "clear_call": 0x00404104,
            "query_call": 0x00544E98,
            "query_selector": 1,
            "query_timeout": 0xC8,
            "result_register": "r4",
            "failure_branch_target": 0x005456FC,
            "authenticated_decompile_entry": 0x005456D6,
            "authenticated_decompile_kind": "two_byte_affine_mixer_no_callees",
            "boundary_conflict": (
                "raw_thumb_stream_decodes_as_status_query_tail_not_isolated_"
                "byte_mixer"
            ),
            "implementation_readiness": (
                "needs_status_query_tail_boundary_reconciliation"
            ),
            "firmware_routing_status": "not_yet_routed_into_overlay",
        }
    if function == "open_cfw_runtime_am115_0x005455c6":
        return {
            "available": True,
            "kind": "split_return_literal_pool_and_embedded_two_call_entry",
            "entry_address": shape["base_address"],
            "uses_existing_stack_frame": True,
            "success_return_value": 0,
            "epilogue_stack_adjust": 0x18,
            "terminal_return_halfword_index": shape["first_return_halfword_index"],
            "post_return_literal_halfwords": 10,
            "embedded_entry_address": 0x005455E0,
            "embedded_prologue_registers": ["r4", "r5", "lr"],
            "authenticated_decompile_entry": 0x005455C6,
            "authenticated_decompile_calls": [0x004411F2, 0x00441200],
            "boundary_conflict": (
                "raw_helper_body_decodes_as_prior_return_tail_literal_pool_"
                "and_embedded_following_prologue"
            ),
            "implementation_readiness": (
                "needs_two_call_entry_boundary_reconciliation"
            ),
            "firmware_routing_status": "not_yet_routed_into_overlay",
        }
    if function == "open_cfw_runtime_am115_0x00545588":
        return {
            "available": True,
            "kind": "prologueless_opacity_debug_literal_prefix",
            "entry_address": shape["base_address"],
            "uses_existing_stack_frame": True,
            "guard_branch_target": 0x005455A8,
            "literal_stack_offset": 4,
            "line_literal": 0x306,
            "authenticated_decompile_entry": 0x00545588,
            "authenticated_decompile_call": 0x0044BDEA,
            "authenticated_decompile_call_immediate": 0x62,
            "boundary_conflict": (
                "short_raw_prefix_lacks_the_authenticated_call_body_in_this_"
                "helper_slice"
            ),
            "implementation_readiness": (
                "needs_opacity_debug_prefix_boundary_reconciliation"
            ),
            "firmware_routing_status": "not_yet_routed_into_overlay",
        }
    if function == "open_cfw_runtime_am115_0x00544cec":
        return {
            "available": True,
            "kind": "prologueless_retry_service_tail_branch_fragment",
            "entry_address": shape["base_address"],
            "uses_existing_stack_frame": True,
            "prefix_halfword_is_prior_wide_call_suffix": True,
            "failure_return_value": -1,
            "tail_branch_target": 0x00544C96,
            "local_loop_branch_target": 0x00544CF0,
            "authenticated_decompile_entry": 0x00544CEC,
            "authenticated_decompile_call": 0x00544C78,
            "authenticated_context_offset": 0x10,
            "implementation_readiness": (
                "needs_retry_service_tail_branch_semantics"
            ),
            "firmware_routing_status": "not_yet_routed_into_overlay",
        }
    return None


def _ranked_entry_semantic_rollup(
    ranked_queue: list[dict[str, object]],
    next_entry_candidate: dict[str, object] | None,
) -> dict[str, object]:
    semantic_model_ranks = []
    if next_entry_candidate is not None and next_entry_candidate.get(
        "semantic_model"
    ):
        semantic_model_ranks.append(next_entry_candidate["rank"])
    semantic_frontier_ranks = [
        row["rank"] for row in ranked_queue if row.get("semantic_frontier")
    ]
    semantic_frontier_kinds = {}
    for row in ranked_queue:
        frontier = row.get("semantic_frontier")
        if frontier:
            kind = frontier["kind"]
            semantic_frontier_kinds[kind] = (
                semantic_frontier_kinds.get(kind, 0) + 1
            )
    classified_ranks = set(semantic_model_ranks) | set(semantic_frontier_ranks)
    decode_only_ranks = [
        row["rank"] for row in ranked_queue if row["rank"] not in classified_ranks
    ]
    return {
        "ranked_entry_count": len(ranked_queue),
        "semantic_model_count": len(semantic_model_ranks),
        "semantic_model_ranks": semantic_model_ranks,
        "semantic_frontier_count": len(semantic_frontier_ranks),
        "semantic_frontier_ranks": semantic_frontier_ranks,
        "semantic_frontier_kind_counts": dict(
            sorted(semantic_frontier_kinds.items())
        ),
        "decode_only_count": len(decode_only_ranks),
        "decode_only_ranks": decode_only_ranks,
        "classified_rank_count": len(classified_ranks),
        "implementation_readiness": (
            "complete_semantic_frontier"
            if not decode_only_ranks
            else "partial_semantic_frontier"
            if classified_ranks
            else "decode_only"
        ),
    }


def _thumb_decode_summary(
    halfwords: list[int],
    candidate: dict[str, object],
    include_instructions: bool = True,
) -> dict[str, object]:
    try:
        from capstone import CS_ARCH_ARM, CS_MODE_MCLASS, CS_MODE_THUMB, Cs
    except ImportError:
        return {"available": False, "reason": "capstone_unavailable"}

    start = int(candidate["entry_halfword_index"])
    byte_count = int(candidate["bytes_through_return"])
    address = int(candidate["entry_address"])
    selected = halfwords[start:start + byte_count // 2]
    code = b"".join(struct.pack("<H", value) for value in selected)
    decoder = Cs(CS_ARCH_ARM, CS_MODE_THUMB | CS_MODE_MCLASS)
    instructions = [
        {
            "address": instruction.address,
            "bytes": instruction.bytes.hex(),
            "mnemonic": instruction.mnemonic,
            "op_str": instruction.op_str,
        }
        for instruction in decoder.disasm(code, address)
    ]
    call_targets = [
        instruction["op_str"]
        for instruction in instructions
        if instruction["mnemonic"] == "bl"
    ]
    literal_pool_references = _literal_pool_references(instructions)
    summary = {
        "available": True,
        "instruction_count": len(instructions),
        "decoded_byte_count": sum(
            len(bytes.fromhex(instruction["bytes"]))
            for instruction in instructions
        ),
        "pc_relative_load_count": sum(
            1 for instruction in instructions
            if instruction["mnemonic"].startswith("ldr")
            and "[pc" in instruction["op_str"]
        ),
        "branch_count": sum(
            1 for instruction in instructions
            if instruction["mnemonic"].startswith("b")
        ),
        "call_targets": call_targets,
        "literal_pool_references": literal_pool_references,
        "terminal_instruction": (
            None if not instructions else
            f"{instructions[-1]['mnemonic']} {instructions[-1]['op_str']}"
        ),
    }
    if include_instructions:
        summary["instructions"] = instructions
    return summary


def _literal_pool_references(
    instructions: list[dict[str, object]],
) -> list[dict[str, object]]:
    if not APOLLO_MAIN_IMAGE.exists():
        return []
    blob = APOLLO_MAIN_IMAGE.read_bytes()
    references = []
    for instruction in instructions:
        mnemonic = str(instruction["mnemonic"])
        op_str = str(instruction["op_str"])
        if not mnemonic.startswith("ldr") or "[pc" not in op_str:
            continue
        match = re.match(
            r"(?P<register>r\d+), \[pc, #0x(?P<offset>[0-9a-fA-F]+)\]",
            op_str,
        )
        if match is None:
            continue
        address = int(instruction["address"])
        offset = int(match.group("offset"), 16)
        pc = (address + 4) & ~3
        literal_address = pc + offset
        image_offset = literal_address - APOLLO_MAIN_BASE
        word = None
        if 0 <= image_offset <= len(blob) - 4:
            word = struct.unpack_from("<I", blob, image_offset)[0]
        references.append({
            "instruction_address": address,
            "register": match.group("register"),
            "pc_base": pc,
            "literal_address": literal_address,
            "image_offset": image_offset,
            "word": word,
        })
    return references


def _am115_0x546e02_semantic_model_summary(
    candidate: dict[str, object],
) -> dict[str, object] | None:
    if candidate.get("entry_address") != 0x00546E02:
        return None
    return {
        "available": True,
        "source": (
            "components/apollo_main/core_overlay/"
            "runtime_liblc3_am115_semantic_model.c"
        ),
        "test": "tests/test_runtime_liblc3_am115_semantic_model.py",
        "function": "open_cfw_am115_0x546e02_semantic_model",
        "kind": "gated_literal_call_returns_zero",
        "entry_address": 0x00546E02,
        "gate_pointer": 0x200746A8,
        "call_r0": 0x0078E144,
        "call_r1": 0x200031B4,
        "call_target": 0x0043B40E,
        "return_value": 0,
        "firmware_routing_status": "not_yet_routed_into_overlay",
    }


def _am115_ranked_entry_semantic_frontier(
    candidate: dict[str, object],
) -> dict[str, object] | None:
    entry_address = candidate.get("entry_address")
    if entry_address == 0x00545EC4:
        return {
            "available": True,
            "kind": "u16_argument_tail_call_wrapper",
            "entry_address": entry_address,
            "argument_register": "r1",
            "argument_transform": "uxth",
            "call_target": 0x00486876,
            "return_register_passthrough": "r0",
            "implementation_readiness": "needs_tail_call_wrapper_semantics",
            "firmware_routing_status": "not_yet_routed_into_overlay",
        }
    if entry_address == 0x005463F8:
        return {
            "available": True,
            "kind": "zero_zero_service_call_returns_zero",
            "entry_address": entry_address,
            "call_r0": 0,
            "call_r1": 0,
            "call_target": 0x0049B554,
            "return_value": 0,
            "implementation_readiness": "needs_zero_service_call_semantics",
            "firmware_routing_status": "not_yet_routed_into_overlay",
        }
    if entry_address == 0x00546406:
        return {
            "available": True,
            "kind": "literal_source_copy_returns_zero",
            "entry_address": entry_address,
            "destination_register": "r0",
            "length_register": "r1_to_r2",
            "source_literal": 0x0078B944,
            "copy_call": 0x004135C0,
            "return_value": 0,
            "implementation_readiness": "needs_literal_copy_semantics",
            "firmware_routing_status": "not_yet_routed_into_overlay",
        }
    if entry_address == 0x00545E1C:
        return {
            "available": True,
            "kind": "fixed_type_literal_event_call",
            "entry_address": entry_address,
            "event_type": 2,
            "event_literal_source": "pc_relative_addw",
            "call_target": 0x00509300,
            "return_register_passthrough": "r0",
            "implementation_readiness": "needs_fixed_event_call_semantics",
            "firmware_routing_status": "not_yet_routed_into_overlay",
        }
    if entry_address in (0x00546414, 0x0054642A):
        mode = 1 if entry_address == 0x00546414 else 0
        return {
            "available": True,
            "kind": "mode_set_delay_flush_returns_zero",
            "entry_address": entry_address,
            "mode_value": mode,
            "mode_call": 0x00473E86,
            "delay_value": 0x64,
            "delay_call": 0x00411396,
            "flush_call": 0x004130CE,
            "return_value": 0,
            "implementation_readiness": "needs_mode_delay_flush_semantics",
            "firmware_routing_status": "not_yet_routed_into_overlay",
        }
    if entry_address == 0x00545ED0:
        return {
            "available": True,
            "kind": "string_cursor_advance_or_default_returns_pointer",
            "entry_address": entry_address,
            "input_pointer_register": "r0",
            "delimiter_register": "r1",
            "cursor_output_register": "r2",
            "length_call": 0x00509B72,
            "default_literal_source": "adr",
            "return_register": "r0",
            "implementation_readiness": "needs_string_cursor_semantics",
            "firmware_routing_status": "not_yet_routed_into_overlay",
        }
    if entry_address == 0x00545E9C:
        return {
            "available": True,
            "kind": "optional_callback_then_free_and_scheduler_cleanup",
            "entry_address": entry_address,
            "context_register": "r0",
            "callback_pointer_offset": 0,
            "callback_arg0_offset": 4,
            "callback_arg1_offset": 0x104,
            "free_call": 0x0041E230,
            "scheduler_cleanup_call": 0x0041D8BC,
            "deferred_cleanup_call": 0x0041CACE,
            "implementation_readiness": "needs_callback_cleanup_semantics",
            "firmware_routing_status": "not_yet_routed_into_overlay",
        }
    if entry_address == 0x00546048:
        return {
            "available": True,
            "kind": "ring_distance_from_triple_word_state",
            "entry_address": entry_address,
            "state_register": "r0",
            "assert_call": 0x005C20C4,
            "base_offset": 0,
            "read_offset": 4,
            "limit_offset": 8,
            "wrap_adjusts_by_limit": True,
            "return_register": "r0",
            "implementation_readiness": "needs_ring_distance_semantics",
            "firmware_routing_status": "not_yet_routed_into_overlay",
        }
    if entry_address == 0x00546110:
        return {
            "available": True,
            "kind": "bounded_buffer_write_updates_write_cursor",
            "entry_address": entry_address,
            "state_register": "r0",
            "source_register": "r1",
            "requested_length_register": "r2",
            "limit_register": "r3",
            "flags_offset": 0x1C,
            "cursor_offset": 4,
            "transfer_call": 0x00546288,
            "return_value": "bytes_written",
            "implementation_readiness": "needs_bounded_write_semantics",
            "firmware_routing_status": "not_yet_routed_into_overlay",
        }
    if entry_address == 0x00546240:
        return {
            "available": True,
            "kind": "bounded_buffer_read_updates_read_cursor",
            "entry_address": entry_address,
            "state_register": "r0",
            "destination_register": "r1",
            "requested_length_register": "r2",
            "available_register": "r3",
            "flags_offset": 0x1C,
            "cursor_offset": 0,
            "transfer_call": 0x00546316,
            "return_value": "bytes_read",
            "implementation_readiness": "needs_bounded_read_semantics",
            "firmware_routing_status": "not_yet_routed_into_overlay",
        }
    if entry_address == 0x00545F9C:
        return {
            "available": True,
            "kind": "guarded_ring_descriptor_initialize",
            "entry_address": entry_address,
            "assert_call": 0x005C20C4,
            "descriptor_register": "stack_arg0",
            "minimum_capacity": 5,
            "descriptor_size": 0x24,
            "mode_when_flag_clear": 2,
            "mode_when_flag_set": 3,
            "initializer_call": 0x005463C4,
            "flags_offset": 0x1C,
            "initialized_flag_mask": 2,
            "return_value": "descriptor_or_zero",
            "implementation_readiness": "needs_ring_descriptor_init_semantics",
            "firmware_routing_status": "not_yet_routed_into_overlay",
        }
    if entry_address == 0x0054595C:
        return {
            "available": True,
            "kind": "u8_status_query_with_debug_logs",
            "entry_address": entry_address,
            "input_register": "r0",
            "status_buffer_offset": 0x10,
            "status_buffer_bytes": 1,
            "clear_call": 0x00404104,
            "query_call": 0x00545044,
            "query_timeout": 0xC8,
            "debug_gate_call": 0x004050EE,
            "debug_log_call": 0x00405594,
            "debug_emit_call": 0x00404EBE,
            "success_status_value": 1,
            "default_error_return_value": -1,
            "success_return_value": 0,
            "implementation_readiness": "needs_status_query_semantics",
            "firmware_routing_status": "not_yet_routed_into_overlay",
        }
    if entry_address == 0x00545438:
        return {
            "available": True,
            "kind": "u8_status_query_with_debug_logs",
            "entry_address": entry_address,
            "input_register": "none",
            "status_buffer_offset": 0x10,
            "status_buffer_bytes": 1,
            "clear_call": 0x00404104,
            "query_call": 0x00544850,
            "query_timeout": 0xC8,
            "debug_gate_call": 0x004050EE,
            "debug_log_call": 0x00405594,
            "debug_emit_call": 0x00404EBE,
            "success_status_value": 1,
            "default_error_return_value": -1,
            "success_return_value": 0,
            "implementation_readiness": "needs_status_query_semantics",
            "firmware_routing_status": "not_yet_routed_into_overlay",
        }
    if entry_address == 0x00545C60:
        return {
            "available": True,
            "kind": "vfp_d0_d1_compare_wrapper",
            "entry_address": entry_address,
            "input_vfp_registers": ["d0", "d1"],
            "core_arg_registers": ["r0", "r1", "r2", "r3"],
            "call_target": 0x00545C74,
            "return_vfp_register": "d0",
            "implementation_readiness": (
                "needs_vfp_compare_wrapper_semantics"
            ),
            "firmware_routing_status": "not_yet_routed_into_overlay",
        }
    if entry_address == 0x00545A60:
        return {
            "available": True,
            "kind": "retry_transaction_fill_compact_result",
            "entry_address": entry_address,
            "output_register": "r0",
            "retry_count": 3,
            "scratch_buffer_offset": 0x14,
            "scratch_buffer_bytes": 0x1A,
            "transaction_context_literal_source": "pc_relative_literal",
            "start_call": 0x00544462,
            "read_call": 0x00543D26,
            "cleanup_call": 0x00544660,
            "debug_gate_call": 0x004050EE,
            "debug_log_call": 0x00405594,
            "debug_emit_call": 0x00404EBE,
            "output_status_byte_offset": 0,
            "output_value_u16_offset": 2,
            "success_return_value": 0,
            "null_output_return_value": -1,
            "implementation_readiness": "needs_retry_transaction_semantics",
            "firmware_routing_status": "not_yet_routed_into_overlay",
        }
    if entry_address == 0x00546622:
        return {
            "available": True,
            "kind": "u16_probe_format_write_returns_zero",
            "entry_address": entry_address,
            "destination_register": "r0",
            "format_argument_register": "r1",
            "probe_output_stack_offset": 0,
            "probe_call": 0x0055AFBA,
            "format_call": 0x00413748,
            "format_literal_source": "pc_relative_literal",
            "return_value": 0,
            "implementation_readiness": "needs_probe_format_write_semantics",
            "firmware_routing_status": "not_yet_routed_into_overlay",
        }
    if entry_address == 0x005466EC:
        return {
            "available": True,
            "kind": "status_byte_string_selector",
            "entry_address": entry_address,
            "status_selector_arg": 1,
            "status_provider_call": 0x004D13AE,
            "handled_status_values": [1, 2, 3, 4, 5],
            "default_literal_source": "pc_relative_literal",
            "return_register": "r0",
            "implementation_readiness": "needs_status_string_semantics",
            "firmware_routing_status": "not_yet_routed_into_overlay",
        }
    if entry_address == 0x00546646:
        return {
            "available": True,
            "kind": "literal_registration_burst",
            "entry_address": entry_address,
            "literal_count": 10,
            "registration_call": 0x0054C7CC,
            "return_register_passthrough": "r0",
            "implementation_readiness": "needs_literal_registration_semantics",
            "firmware_routing_status": "not_yet_routed_into_overlay",
        }
    if entry_address == 0x00546722:
        return {
            "available": True,
            "kind": "device_state_format_buffer_returns_pointer",
            "entry_address": entry_address,
            "output_literal_source": "pc_relative_literal",
            "output_buffer_bytes": 0x14,
            "clear_call": 0x00404104,
            "state_call": 0x00422588,
            "device_read_call": 0x00544684,
            "format_call": 0x00413748,
            "device_read_timeout": 0x3E8,
            "return_buffer_register": "r0",
            "implementation_readiness": "needs_device_state_format_semantics",
            "firmware_routing_status": "not_yet_routed_into_overlay",
        }
    dynamic_dispatch_variants = {
        0x0054651C: {
            "match_length": 2,
            "action_kind": "mode_call",
            "action_call": 0x005576BA,
            "action_arg0": 1,
        },
        0x0054657A: {
            "match_length": 6,
            "action_kind": "no_arg_call",
            "action_call": 0x004DA9BC,
            "action_arg0": None,
        },
    }
    dispatch_variant = dynamic_dispatch_variants.get(entry_address)
    if dispatch_variant is not None:
        return {
            "available": True,
            "kind": "dynamic_segment_command_dispatch_returns_zero",
            "entry_address": entry_address,
            "destination_register": "r0",
            "fallback_length_register": "r1",
            "input_context_register": "r2",
            "dynamic_segment_call": 0x0054C91C,
            "dynamic_segment_mode": 1,
            "fallback_copy_call": 0x004135C0,
            "match_call": 0x00413630,
            **dispatch_variant,
            "return_value": 0,
            "implementation_readiness": "needs_dynamic_dispatch_semantics",
            "firmware_routing_status": "not_yet_routed_into_overlay",
        }
    if entry_address == 0x00546AC8:
        return {
            "available": True,
            "kind": "gated_path_component_filter_join_returns_status",
            "entry_address": entry_address,
            "gate_pointer": 0x200746A8,
            "input_output_buffer_register": "r0",
            "stack_frame_bytes": 0x4FC,
            "scratch_buffer_offset": 0,
            "scratch_buffer_bytes": 0xFF,
            "component_vector_offset": 0x100,
            "max_component_count": 0xFF,
            "delimiter_literal": "/",
            "skip_component_literals": [".", ".."],
            "zero_fill_call": 0x004135C0,
            "tokenizer_call": 0x0055C8A4,
            "compare_call": 0x00434AEC,
            "append_call": 0x0052FCA0,
            "empty_path_fill_call": 0x00455560,
            "length_call": 0x0041245C,
            "overflow_length_limit": 0xFF,
            "success_return_value": 0,
            "overflow_return_value": -1,
            "implementation_readiness": "needs_path_component_filter_semantics",
            "firmware_routing_status": "not_yet_routed_into_overlay",
        }
    if entry_address == 0x00546BB4:
        return {
            "available": True,
            "kind": "gated_dynamic_path_normalize_query_persist_returns_zero",
            "entry_address": entry_address,
            "gate_pointer": 0x200746A8,
            "input_context_register": "r2",
            "stack_frame_bytes": 0x240,
            "dynamic_segment_call": 0x0054C91C,
            "dynamic_segment_mode": 1,
            "path_builder_call": 0x00413748,
            "normalizer_call": 0x00546AC8,
            "query_prepare_call": 0x00497C86,
            "query_commit_call": 0x00497D18,
            "bounded_copy_call": 0x004135C0,
            "error_log_call": 0x0043B40E,
            "primary_literal": 0x200031B4,
            "overflow_log_literal": 0x0078272C,
            "path_error_log_literal": 0x00782F40,
            "path_format_literal": 0x0078E13C,
            "final_call_context": 0x20071AC8,
            "raw_path_buffer_offset": 0x13C,
            "normalized_path_buffer_offset": 0x3C,
            "query_state_buffer_offset": 8,
            "copy_back_bytes": 0x80,
            "success_return_value": 0,
            "implementation_readiness": "needs_normalize_query_persist_semantics",
            "firmware_routing_status": "not_yet_routed_into_overlay",
        }
    if entry_address == 0x00547570:
        return {
            "available": True,
            "kind": "storage_context_metrics_log_returns_zero",
            "entry_address": entry_address,
            "context_pointer": 0x20074ABC,
            "open_context_call": 0x00498736,
            "metrics_buffer_offset": 4,
            "metrics_buffer_bytes": 0x10,
            "clear_metrics_call": 0x00404104,
            "query_metrics_call": 0x004985A0,
            "query_metrics_selector": 0x0057F531,
            "capacity_base_constant": 0x70800,
            "capacity_bias_constant": 0x0C74,
            "capacity_helper_call": 0x0049861A,
            "log_call": 0x0043B40E,
            "log_literal_count": 18,
            "percent_warning_threshold": 0x4C,
            "percent_error_threshold": 0x5B,
            "return_value": 0,
            "implementation_readiness": "needs_storage_metrics_semantics",
            "firmware_routing_status": "not_yet_routed_into_overlay",
        }
    am135_delegate_tails = {
        0x0058CD04: {
            "kind": "am135_literal_dual_runtime_call_tail",
            "call_targets": [0x00414FB8, 0x00415110],
            "literal_pool_word": 0x007555AC,
            "branch_count": 2,
        },
        0x0058CD98: {
            "kind": "am135_dual_runtime_call_tail",
            "call_targets": [0x004157D8, 0x00417778],
            "branch_count": 4,
        },
        0x0058CDC6: {
            "kind": "am135_multi_runtime_call_tail",
            "call_targets": [
                0x00405FC4,
                0x00405FC4,
                0x00405EF4,
                0x00405EF4,
                0x00461436,
            ],
            "branch_count": 5,
        },
        0x0058CCBC: {
            "kind": "am135_literal_runtime_store_tail",
            "call_targets": [0x0041527C, 0x00406100],
            "literal_pool_word_count": 5,
            "branch_count": 6,
        },
        0x0058CC64: {
            "kind": "am135_literal_multi_runtime_store_tail",
            "call_targets": [0x0041527C, 0x004060A6, 0x00405EF4, 0x00419690],
            "literal_pool_word_count": 5,
            "branch_count": 6,
        },
        0x0058CD24: {
            "kind": "am135_literal_local_delegate_tail",
            "call_targets": [0x00405EF4, 0x0058C752, 0x00415BE4, 0x0058CD04],
            "literal_pool_word": 0x0076CA58,
            "branch_count": 4,
        },
        0x0058EFD0: {
            "kind": "am135_short_runtime_call_tail_returns_pointer",
            "call_targets": [0x0041C766],
            "branch_count": 1,
        },
        0x0058EFDC: {
            "kind": "am135_local_then_runtime_dispatch_tail",
            "call_targets": [0x0058EFD0, 0x004090C6, 0x00401C04],
            "branch_count": 3,
        },
        0x0058F00A: {
            "kind": "am135_literal_runtime_service_tail",
            "call_targets": [
                0x0044C40E,
                0x00417738,
                0x0041527C,
                0x0041C758,
                0x0044C496,
            ],
            "literal_pool_word_count": 5,
            "branch_count": 17,
        },
        0x0058C8C6: {
            "kind": "am135_literal_runtime_store_tail",
            "call_targets": [0x0041527C],
            "literal_pool_word_count": 5,
            "branch_count": 3,
        },
        0x0058C8F8: {
            "kind": "am135_literal_repeated_runtime_store_tail",
            "call_targets": [0x0041527C, 0x0041C788, 0x0041527C],
            "literal_pool_word_count": 8,
            "branch_count": 16,
        },
        0x0058DC18: {
            "kind": "am135_large_state_machine_delegate_tail",
            "call_targets": [
                0x00419718,
                0x004182A6,
                0x0041AF18,
                0x0041AF7E,
                0x004165A6,
                0x0058ECFC,
                0x0058EE24,
                0x0058EE24,
                0x00419690,
                0x0058EE24,
                0x00419980,
                0x0058DD10,
                0x0044ADA8,
                0x0058DF58,
                0x0058E83C,
                0x0058E434,
                0x0058EA8C,
            ],
            "literal_pool_word": 0x007552EC,
            "branch_count": 30,
        },
        0x0058DB30: {
            "kind": "am135_repeated_runtime_call_tail",
            "call_targets": [0x0044AB20, 0x0044AB20],
            "branch_count": 2,
        },
    }
    am135_tail = am135_delegate_tails.get(entry_address)
    if am135_tail is not None:
        return {
            "available": True,
            "entry_address": entry_address,
            "decoded_byte_count": candidate["bytes_through_return"],
            "return_register": "r0",
            **am135_tail,
            "implementation_readiness": "needs_am135_tail_semantics",
            "firmware_routing_status": "not_yet_routed_into_overlay",
        }
    am135_tiny_call_tails = {
        0x0058F16A,
        0x0058F174,
        0x0058F188,
        0x0058F192,
        0x0058F19C,
        0x0058F1A6,
        0x0058F1B0,
        0x0058F1BA,
        0x0058F1C4,
        0x0058F1CE,
        0x0058F1D8,
    }
    if entry_address in am135_tiny_call_tails:
        return {
            "available": True,
            "kind": "am135_tiny_runtime_call_tail",
            "entry_address": entry_address,
            "decoded_byte_count": candidate["bytes_through_return"],
            "call_targets": [0x00413E0A],
            "branch_count": 1,
            "return_register": "r0",
            "implementation_readiness": "needs_am135_tiny_tail_semantics",
            "firmware_routing_status": "not_yet_routed_into_overlay",
        }
    am136_literal_tails = {
        0x00590268: {
            "kind": "am136_literal_runtime_store_tail",
            "call_targets": [0x0041527C],
            "literal_pool_word_count": 5,
            "branch_count": 3,
        },
        0x0059029A: {
            "kind": "am136_literal_runtime_store_tail",
            "call_targets": [0x0041527C],
            "literal_pool_word_count": 5,
            "branch_count": 3,
        },
        0x0059018C: {
            "kind": "am136_literal_runtime_store_tail",
            "call_targets": [0x0041527C],
            "literal_pool_word_count": 5,
            "branch_count": 3,
        },
        0x00590228: {
            "kind": "am136_literal_runtime_store_tail",
            "call_targets": [0x0041527C],
            "literal_pool_word_count": 5,
            "branch_count": 3,
        },
        0x00590344: {
            "kind": "am136_literal_local_delegate_tail",
            "call_targets": [0x0041527C, 0x0059018C, 0x0058FEE4],
            "literal_pool_word_count": 5,
            "branch_count": 5,
        },
        0x0059013C: {
            "kind": "am136_literal_dual_runtime_tail",
            "call_targets": [0x0041527C, 0x00461818],
            "literal_pool_word_count": 5,
            "branch_count": 6,
        },
        0x0059038C: {
            "kind": "am136_literal_local_delegate_tail",
            "call_targets": [0x0041527C, 0x0059018C, 0x0058FEE4],
            "literal_pool_word_count": 5,
            "branch_count": 6,
        },
        0x005901C8: {
            "kind": "am136_literal_mixed_runtime_tail",
            "call_targets": [0x0041527C, 0x0058F916, 0x0049D6E0],
            "literal_pool_word_count": 5,
            "branch_count": 9,
        },
        0x005902E4: {
            "kind": "am136_literal_multi_runtime_tail",
            "call_targets": [0x0041527C, 0x00461F18, 0x00461F4A, 0x00461736, 0x00461772],
            "literal_pool_word_count": 5,
            "branch_count": 9,
        },
        0x005903E0: {
            "kind": "am136_literal_large_local_delegate_tail",
            "call_targets": [
                0x0041527C,
                0x0059018C,
                0x00461850,
                0x0058F920,
                0x0058F916,
                0x00407DFA,
                0x00461A7C,
                0x0058FEE4,
            ],
            "literal_pool_word_count": 5,
            "branch_count": 11,
        },
        0x0058FFF8: {
            "kind": "am136_literal_runtime_store_tail",
            "call_targets": [0x0041527C],
            "literal_pool_word_count": 5,
            "branch_count": 6,
        },
        0x0058FEE4: {
            "kind": "am136_literal_large_runtime_delegate_tail",
            "call_targets": [
                0x0041527C,
                0x00461818,
                0x0040768C,
                0x0058F916,
                0x00461850,
                0x004164CA,
                0x00416A24,
                0x00407E90,
                0x004164CA,
                0x00416A24,
                0x004165A6,
                0x004169FA,
                0x00407E36,
                0x004165A6,
                0x004169FA,
                0x00590884,
                0x0059090C,
            ],
            "literal_pool_word_count": 6,
            "branch_count": 28,
        },
        0x0058FD1E: {
            "kind": "am136_literal_local_delegate_tail",
            "call_targets": [0x0041527C, 0x0059018C, 0x0058FEE4, 0x0059018C, 0x0058FC12],
            "literal_pool_word_count": 5,
            "branch_count": 8,
        },
    }
    am136_literal_tail = am136_literal_tails.get(entry_address)
    if am136_literal_tail is not None:
        return {
            "available": True,
            "entry_address": entry_address,
            "decoded_byte_count": candidate["bytes_through_return"],
            "return_register": "r0",
            **am136_literal_tail,
            "implementation_readiness": "needs_am136_literal_tail_semantics",
            "firmware_routing_status": "not_yet_routed_into_overlay",
        }
    am136_delegate_tails = {
        0x005905C0: {
            "kind": "am136_repeated_runtime_call_tail",
            "call_targets": [0x00417778, 0x00417778, 0x00417778],
            "branch_count": 6,
        },
        0x005904F4: {
            "kind": "am136_large_runtime_delegate_tail",
            "call_targets": [
                0x00461436,
                0x004195F2,
                0x00407526,
                0x0046144E,
                0x00419760,
                0x00419760,
                0x00405EF4,
                0x00405FC4,
                0x0058FEE4,
                0x00590884,
            ],
            "branch_count": 10,
        },
    }
    am136_delegate_tail = am136_delegate_tails.get(entry_address)
    if am136_delegate_tail is not None:
        return {
            "available": True,
            "entry_address": entry_address,
            "decoded_byte_count": candidate["bytes_through_return"],
            "return_register": "r0",
            **am136_delegate_tail,
            "implementation_readiness": "needs_am136_delegate_tail_semantics",
            "firmware_routing_status": "not_yet_routed_into_overlay",
        }
    am136_tiny_call_tails = {
        0x0058F8EA,
        0x0058F8F4,
        0x0058F8FE,
        0x0058F908,
        0x0058F916,
    }
    if entry_address in am136_tiny_call_tails:
        return {
            "available": True,
            "kind": "am136_tiny_runtime_call_tail",
            "entry_address": entry_address,
            "decoded_byte_count": candidate["bytes_through_return"],
            "call_targets": [0x00413E0A],
            "branch_count": 1,
            "return_register": "r0",
            "implementation_readiness": "needs_am136_tiny_tail_semantics",
            "firmware_routing_status": "not_yet_routed_into_overlay",
        }
    am137_delegate_tails = {
        0x005934B6: {
            "kind": "am137_short_runtime_wrapper_tail",
            "call_targets": [0x0051F6F6],
            "branch_count": 1,
        },
        0x005934BE: {
            "kind": "am137_short_runtime_wrapper_tail",
            "call_targets": [0x0051F738],
            "branch_count": 1,
        },
        0x005934E6: {
            "kind": "am137_short_runtime_wrapper_tail",
            "call_targets": [0x0051F7C6],
            "branch_count": 1,
        },
        0x005934A2: {
            "kind": "am137_short_runtime_wrapper_tail",
            "call_targets": [0x0051F556],
            "branch_count": 1,
        },
        0x005934AC: {
            "kind": "am137_short_runtime_wrapper_tail",
            "call_targets": [0x0051F5D0],
            "branch_count": 1,
        },
        0x005934C6: {
            "kind": "am137_runtime_wrapper_tail_returns_pointer",
            "call_targets": [0x0051F78A],
            "branch_count": 5,
        },
        0x0059133E: {
            "kind": "am137_runtime_call_tail_returns_pointer",
            "call_targets": [0x00405FC4],
            "branch_count": 2,
        },
        0x00590FC8: {
            "kind": "am137_literal_runtime_call_tail",
            "call_targets": [0x00418520],
            "literal_pool_word": 0x005C86AF,
            "branch_count": 1,
        },
        0x0059101C: {
            "kind": "am137_dual_runtime_call_tail",
            "call_targets": [0x0044AFCA, 0x00401C04],
            "branch_count": 2,
        },
    }
    am137_tail = am137_delegate_tails.get(entry_address)
    if am137_tail is not None:
        return {
            "available": True,
            "entry_address": entry_address,
            "decoded_byte_count": candidate["bytes_through_return"],
            "return_register": "r0",
            **am137_tail,
            "implementation_readiness": "needs_am137_tail_semantics",
            "firmware_routing_status": "not_yet_routed_into_overlay",
        }
    am137_tiny_call_tails = {
        0x0059345A,
        0x00593464,
        0x0059346E,
        0x00593478,
        0x00593482,
        0x0059348C,
        0x00593496,
        0x00591334,
    }
    if entry_address in am137_tiny_call_tails:
        return {
            "available": True,
            "kind": "am137_tiny_runtime_call_tail",
            "entry_address": entry_address,
            "decoded_byte_count": candidate["bytes_through_return"],
            "call_targets": [0x00413E0A],
            "branch_count": 1,
            "return_register": "r0",
            "implementation_readiness": "needs_am137_tiny_tail_semantics",
            "firmware_routing_status": "not_yet_routed_into_overlay",
        }
    am138_literal_tails = {
        0x005940B4: {
            "kind": "am138_literal_local_delegate_tail",
            "call_targets": [0x0041527C, 0x005944C6],
            "literal_pool_word_count": 5,
            "branch_count": 5,
        },
        0x00594102: {
            "kind": "am138_literal_local_delegate_tail",
            "call_targets": [0x0041527C, 0x005944C6],
            "literal_pool_word_count": 5,
            "branch_count": 11,
        },
        0x00594202: {
            "kind": "am138_literal_local_delegate_tail",
            "call_targets": [0x0041527C, 0x005944C6],
            "literal_pool_word_count": 5,
            "branch_count": 12,
        },
        0x00594174: {
            "kind": "am138_literal_local_delegate_tail",
            "call_targets": [0x0041527C, 0x005944C6],
            "literal_pool_word_count": 5,
            "branch_count": 12,
        },
        0x0059461C: {
            "kind": "am138_literal_multi_runtime_delegate_tail",
            "call_targets": [
                0x00418520,
                0x004183F6,
                0x004186EE,
                0x00418428,
                0x00418708,
                0x004186EE,
                0x00418428,
                0x00587F74,
                0x00587F9A,
            ],
            "literal_pool_word": 0x00450771,
            "branch_count": 9,
        },
    }
    am138_literal_tail = am138_literal_tails.get(entry_address)
    if am138_literal_tail is not None:
        return {
            "available": True,
            "entry_address": entry_address,
            "decoded_byte_count": candidate["bytes_through_return"],
            "return_register": "r0",
            **am138_literal_tail,
            "implementation_readiness": "needs_am138_literal_tail_semantics",
            "firmware_routing_status": "not_yet_routed_into_overlay",
        }
    am138_delegate_tails = {
        0x0059478C: {
            "kind": "am138_short_runtime_call_tail",
            "call_targets": [0x00418520],
            "branch_count": 1,
        },
        0x005946E8: {
            "kind": "am138_short_local_call_tail",
            "call_targets": [0x00587B14],
            "branch_count": 1,
        },
        0x005946F8: {
            "kind": "am138_short_local_call_tail",
            "call_targets": [0x00587C24],
            "branch_count": 1,
        },
        0x005946CC: {
            "kind": "am138_runtime_then_local_tail",
            "call_targets": [0x00405FC4, 0x0059461C],
            "branch_count": 2,
        },
        0x00594758: {
            "kind": "am138_multi_runtime_call_tail",
            "call_targets": [0x00405FC4, 0x00405EF4, 0x00405EF4],
            "branch_count": 3,
        },
        0x00593B92: {
            "kind": "am138_dual_runtime_branch_tail",
            "call_targets": [0x00407DBE, 0x00407DFA],
            "branch_count": 8,
        },
    }
    am138_delegate_tail = am138_delegate_tails.get(entry_address)
    if am138_delegate_tail is not None:
        return {
            "available": True,
            "entry_address": entry_address,
            "decoded_byte_count": candidate["bytes_through_return"],
            "return_register": "r0",
            **am138_delegate_tail,
            "implementation_readiness": "needs_am138_delegate_tail_semantics",
            "firmware_routing_status": "not_yet_routed_into_overlay",
        }
    am138_tiny_call_tails = {
        0x0059471A,
        0x00594724,
        0x0059472E,
        0x00594738,
        0x00594742,
        0x0059474C,
    }
    if entry_address in am138_tiny_call_tails:
        return {
            "available": True,
            "kind": "am138_tiny_runtime_call_tail",
            "entry_address": entry_address,
            "decoded_byte_count": candidate["bytes_through_return"],
            "call_targets": [0x00413E0A],
            "branch_count": 1,
            "return_register": "r0",
            "implementation_readiness": "needs_am138_tiny_tail_semantics",
            "firmware_routing_status": "not_yet_routed_into_overlay",
        }
    am141_literal_tails = {
        0x00599E92: {
            "kind": "am141_literal_branch_tail",
            "call_targets": [],
            "literal_pool_word": 0x005D1F69,
            "branch_count": 1,
        },
        0x0059978A: {
            "kind": "am141_literal_runtime_call_tail",
            "call_targets": [0x00404104],
            "literal_pool_word": 0x0078E334,
            "branch_count": 3,
        },
        0x00599532: {
            "kind": "am141_literal_dual_runtime_call_tail",
            "call_targets": [0x004ECBC8, 0x00401C24],
            "literal_pool_word": 0x00764530,
            "branch_count": 6,
        },
    }
    am141_literal_tail = am141_literal_tails.get(entry_address)
    if am141_literal_tail is not None:
        return {
            "available": True,
            "entry_address": entry_address,
            "decoded_byte_count": candidate["bytes_through_return"],
            "return_register": "r0",
            **am141_literal_tail,
            "implementation_readiness": "needs_am141_literal_tail_semantics",
            "firmware_routing_status": "not_yet_routed_into_overlay",
        }
    am141_delegate_tails = {
        0x00599DF4: {
            "kind": "am141_short_local_call_tail",
            "call_targets": [0x00599D4A],
            "branch_count": 1,
        },
        0x00599E00: {
            "kind": "am141_short_local_call_tail",
            "call_targets": [0x00599D4A],
            "branch_count": 1,
        },
        0x00599868: {
            "kind": "am141_short_runtime_call_tail",
            "call_targets": [0x00401C24],
            "branch_count": 2,
        },
        0x00599EBC: {
            "kind": "am141_short_runtime_call_tail",
            "call_targets": [0x004F1276],
            "branch_count": 1,
        },
        0x00599D22: {
            "kind": "am141_short_local_call_tail",
            "call_targets": [0x005984BE],
            "branch_count": 1,
        },
        0x0059A3B0: {
            "kind": "am141_short_local_call_tail",
            "call_targets": [0x0059A34C],
            "branch_count": 3,
        },
        0x0059A32E: {
            "kind": "am141_short_runtime_call_tail",
            "call_targets": [0x004F1276],
            "branch_count": 1,
        },
        0x0059A3DA: {
            "kind": "am141_short_local_call_tail",
            "call_targets": [0x0059AA2A],
            "branch_count": 2,
        },
        0x005998E8: {
            "kind": "am141_dual_local_call_tail",
            "call_targets": [0x0059987E, 0x005998AA],
            "branch_count": 3,
        },
        0x00599DCA: {
            "kind": "am141_local_call_branch_tail",
            "call_targets": [0x00599D84],
            "branch_count": 5,
        },
        0x0059987E: {
            "kind": "am141_runtime_call_branch_tail",
            "call_targets": [0x004ECCF6],
            "branch_count": 4,
        },
        0x0059A34C: {
            "kind": "am141_local_call_branch_tail",
            "call_targets": [0x0059AA2A],
            "branch_count": 2,
        },
        0x00599978: {
            "kind": "am141_dual_local_call_branch_tail",
            "call_targets": [0x0059990E, 0x005998E8],
            "branch_count": 4,
        },
        0x0059A160: {
            "kind": "am141_local_runtime_call_branch_tail",
            "call_targets": [0x00599326, 0x004F1276],
            "branch_count": 4,
        },
        0x0059A3FA: {
            "kind": "am141_local_runtime_call_branch_tail",
            "call_targets": [0x0059A34C, 0x00401C04],
            "branch_count": 4,
        },
        0x00599D84: {
            "kind": "am141_runtime_call_branch_tail",
            "call_targets": [0x00434AEC],
            "branch_count": 8,
        },
        0x00599EF0: {
            "kind": "am141_runtime_call_branch_tail",
            "call_targets": [0x00434AEC],
            "branch_count": 10,
        },
        0x0059990E: {
            "kind": "am141_runtime_call_branch_tail",
            "call_targets": [0x004ECCF6],
            "branch_count": 9,
        },
        0x00599A58: {
            "kind": "am141_runtime_then_local_call_tail",
            "call_targets": [0x00404104, 0x0059978A, 0x0059978A],
            "branch_count": 5,
        },
        0x00599B6A: {
            "kind": "am141_runtime_then_local_call_tail",
            "call_targets": [0x00404104, 0x00404104, 0x00599D3C],
            "branch_count": 20,
        },
        0x005995BA: {
            "kind": "am141_short_runtime_call_tail",
            "call_targets": [0x00401C24],
            "branch_count": 2,
        },
        0x005993BE: {
            "kind": "am141_dual_local_call_tail",
            "call_targets": [0x0059933C, 0x00599368],
            "branch_count": 3,
        },
        0x0059963A: {
            "kind": "am141_dual_local_call_tail",
            "call_targets": [0x005995D0, 0x005995FC],
            "branch_count": 3,
        },
        0x005995D0: {
            "kind": "am141_runtime_call_branch_tail",
            "call_targets": [0x004ECCF6],
            "branch_count": 4,
        },
        0x0059933C: {
            "kind": "am141_runtime_call_branch_tail",
            "call_targets": [0x004ECCF6],
            "branch_count": 4,
        },
        0x0059944E: {
            "kind": "am141_dual_local_call_branch_tail",
            "call_targets": [0x005993E4, 0x005993BE],
            "branch_count": 5,
        },
        0x005993E4: {
            "kind": "am141_runtime_call_branch_tail",
            "call_targets": [0x004ECCF6],
            "branch_count": 9,
        },
        0x005991B0: {
            "kind": "am141_dual_local_call_tail",
            "call_targets": [0x00598A88, 0x005981AA],
            "branch_count": 2,
        },
        0x0059923A: {
            "kind": "am141_dual_local_call_tail",
            "call_targets": [0x00598A88, 0x005981FE],
            "branch_count": 2,
        },
        0x00599252: {
            "kind": "am141_dual_local_call_tail",
            "call_targets": [0x00598A88, 0x00598C24],
            "branch_count": 2,
        },
        0x0059926E: {
            "kind": "am141_dual_local_call_tail",
            "call_targets": [0x00598A88, 0x00598CE2],
            "branch_count": 2,
        },
        0x00598A88: {
            "kind": "am141_short_local_call_tail",
            "call_targets": [0x00598756],
            "branch_count": 1,
        },
    }
    am141_delegate_tail = am141_delegate_tails.get(entry_address)
    if am141_delegate_tail is not None:
        return {
            "available": True,
            "entry_address": entry_address,
            "decoded_byte_count": candidate["bytes_through_return"],
            "return_register": "r0",
            **am141_delegate_tail,
            "implementation_readiness": "needs_am141_delegate_tail_semantics",
            "firmware_routing_status": "not_yet_routed_into_overlay",
        }
    am141_branch_tails = {
        0x00599ED4: 1,
        0x00599EE2: 1,
        0x0059A1B6: 9,
    }
    am141_branch_count = am141_branch_tails.get(entry_address)
    if am141_branch_count is not None:
        return {
            "available": True,
            "kind": "am141_branch_tail",
            "entry_address": entry_address,
            "decoded_byte_count": candidate["bytes_through_return"],
            "call_targets": [],
            "branch_count": am141_branch_count,
            "return_register": "r0",
            "implementation_readiness": "needs_am141_branch_tail_semantics",
            "firmware_routing_status": "not_yet_routed_into_overlay",
        }
    am142_literal_tails = {
        0x0059B00E: {
            "kind": "am142_literal_runtime_call_tail",
            "call_targets": [0x00404104],
            "literal_pool_words": [0x005D2F23, 0x005D2F35, 0x005D2F81],
            "branch_count": 1,
        },
    }
    am142_literal_tail = am142_literal_tails.get(entry_address)
    if am142_literal_tail is not None:
        return _with_am142_receipt_status(entry_address, {
            "available": True,
            "entry_address": entry_address,
            "decoded_byte_count": candidate["bytes_through_return"],
            "return_register": "r0",
            **am142_literal_tail,
            "implementation_readiness": "needs_am142_literal_tail_semantics",
            "firmware_routing_status": "not_yet_routed_into_overlay",
        })
    am142_delegate_tails = {
        0x0059AF42: {
            "kind": "am142_short_local_call_tail",
            "call_targets": [0x005999A6],
            "branch_count": 1,
        },
        0x0059AF1E: {
            "kind": "am142_repeated_runtime_call_tail",
            "call_targets": [0x004F1276, 0x004F1276],
            "branch_count": 3,
        },
        0x0059B2AA: {
            "kind": "am142_short_runtime_call_tail",
            "call_targets": [0x004EC774],
            "branch_count": 1,
        },
        0x0059AEC8: {
            "kind": "am142_runtime_call_branch_tail",
            "call_targets": [0x004EC774],
            "branch_count": 9,
        },
        0x0059B33E: {
            "kind": "am142_runtime_call_branch_tail",
            "call_targets": [0x00404104],
            "branch_count": 3,
        },
        0x0059AF54: {
            "kind": "am142_dual_am141_call_branch_tail",
            "call_targets": [0x00599978, 0x005998E8],
            "branch_count": 9,
        },
        0x0059B382: {
            "kind": "am142_runtime_then_am141_call_tail",
            "call_targets": [0x00404104, 0x0059A1B6],
            "branch_count": 8,
        },
        0x0059AFA0: {
            "kind": "am142_multi_am141_call_branch_tail",
            "call_targets": [0x00599978, 0x0059987E, 0x005998AA, 0x005998AA, 0x005998AA],
            "branch_count": 12,
        },
        0x0059C052: {
            "kind": "am142_short_am141_call_tail",
            "call_targets": [0x0059A32E],
            "branch_count": 1,
        },
        0x0059C530: {
            "kind": "am142_local_call_branch_tail",
            "call_targets": [0x0059B70A, 0x0059C774, 0x0059C060],
            "branch_count": 5,
        },
        0x0059B52C: {
            "kind": "am142_short_runtime_call_tail",
            "call_targets": [0x004ECBC8],
            "branch_count": 1,
        },
        0x0059B53C: {
            "kind": "am142_local_runtime_call_tail",
            "call_targets": [0x005999A6, 0x004ECE9A],
            "branch_count": 2,
        },
        0x0059CB44: {
            "kind": "am142_local_call_branch_tail",
            "call_targets": [0x0059AA2A],
            "branch_count": 3,
        },
        0x0059CB6C: {
            "kind": "am142_dual_local_call_branch_tail",
            "call_targets": [0x0059CB44, 0x0059EDB8],
            "branch_count": 5,
        },
        0x0059CB98: {
            "kind": "am142_local_call_branch_tail",
            "call_targets": [0x0059CB44],
            "branch_count": 5,
        },
        0x0059B654: {
            "kind": "am142_short_runtime_call_tail",
            "call_targets": [0x00404104],
            "branch_count": 1,
        },
        0x0059CB1E: {
            "kind": "am142_short_runtime_call_tail",
            "call_targets": [0x00404104],
            "branch_count": 1,
        },
    }
    am142_delegate_tail = am142_delegate_tails.get(entry_address)
    if am142_delegate_tail is not None:
        return _with_am142_receipt_status(entry_address, {
            "available": True,
            "entry_address": entry_address,
            "decoded_byte_count": candidate["bytes_through_return"],
            "return_register": "r0",
            **am142_delegate_tail,
            "implementation_readiness": "needs_am142_delegate_tail_semantics",
            "firmware_routing_status": "not_yet_routed_into_overlay",
        })
    am142_branch_tails = {
        0x0059B272: 1,
        0x0059B3DE: 1,
        0x0059B454: 2,
    }
    am142_branch_count = am142_branch_tails.get(entry_address)
    if am142_branch_count is not None:
        return _with_am142_receipt_status(entry_address, {
            "available": True,
            "kind": "am142_branch_tail",
            "entry_address": entry_address,
            "decoded_byte_count": candidate["bytes_through_return"],
            "call_targets": [],
            "branch_count": am142_branch_count,
            "return_register": "r0",
            "implementation_readiness": "needs_am142_branch_tail_semantics",
            "firmware_routing_status": "not_yet_routed_into_overlay",
        })
    am140_delegate_tails = {
        0x005986E6: {
            "kind": "am140_literal_repeated_runtime_call_tail",
            "call_targets": [0x004F1276, 0x004F1276, 0x004F1276],
            "literal_pool_word": 0xDEADBEEF,
            "branch_count": 4,
        },
        0x005986A2: {
            "kind": "am140_runtime_then_local_delegate_tail",
            "call_targets": [0x004F1168, 0x00401C04, 0x00598594, 0x004F1276],
            "branch_count": 7,
        },
        0x005984BE: {
            "kind": "am140_branch_tail_returns_pointer",
            "call_targets": [],
            "branch_count": 5,
        },
        0x00598756: {
            "kind": "am140_local_call_tail_returns_pointer",
            "call_targets": [0x0059873C],
            "branch_count": 10,
        },
        0x0059889C: {
            "kind": "am140_local_call_tail_returns_pointer",
            "call_targets": [0x0059873C],
            "branch_count": 14,
        },
        0x00598834: {
            "kind": "am140_local_call_tail_returns_pointer",
            "call_targets": [0x00598756],
            "branch_count": 11,
        },
        0x00598508: {
            "kind": "am140_literal_multi_runtime_tail",
            "call_targets": [0x004F11BC, 0x004F11BC, 0x00401C24, 0x004F1276],
            "literal_pool_word_count": 2,
            "branch_count": 9,
        },
        0x00597B82: {
            "kind": "am140_literal_match_call_tail",
            "call_targets": [0x00413630],
            "literal_pool_word": 0x006CAF20,
            "branch_count": 10,
        },
        0x00597B14: {
            "kind": "am140_repeated_local_delegate_tail",
            "call_targets": [0x005979BA, 0x00597958, 0x00597958, 0x00597958],
            "branch_count": 17,
        },
    }
    am140_tail = am140_delegate_tails.get(entry_address)
    if am140_tail is not None:
        return {
            "available": True,
            "entry_address": entry_address,
            "decoded_byte_count": candidate["bytes_through_return"],
            "return_register": "r0",
            **am140_tail,
            "implementation_readiness": "needs_am140_tail_semantics",
            "firmware_routing_status": "not_yet_routed_into_overlay",
        }
    am143_delegate_tails = {
        0x005A045A: {
            "kind": "am143_repeated_runtime_call_tail",
            "call_targets": [0x004EC718, 0x004EC718],
            "branch_count": 9,
        },
        0x0059EE42: {
            "kind": "am143_repeated_runtime_call_tail",
            "call_targets": [0x004F1276, 0x004F1276],
            "branch_count": 3,
        },
        0x0059EE70: {
            "kind": "am143_local_call_tail_returns_pointer",
            "call_targets": [0x0059AA2A],
            "branch_count": 3,
        },
        0x0059EE9C: {
            "kind": "am143_local_call_tail_returns_pointer",
            "call_targets": [0x0059AA2A],
            "branch_count": 3,
        },
        0x0059EEC8: {
            "kind": "am143_repeated_local_call_tail",
            "call_targets": [0x0059AA2A, 0x0059AA2A],
            "branch_count": 6,
        },
        0x0059EDEA: {
            "kind": "am143_multi_runtime_call_tail",
            "call_targets": [0x004F1168, 0x004F11BC, 0x004F1276],
            "branch_count": 6,
        },
        0x0059EF00: {
            "kind": "am143_local_call_tail_returns_pointer",
            "call_targets": [0x0059AA2A],
            "branch_count": 9,
        },
        0x0059EF58: {
            "kind": "am143_dual_local_delegate_tail",
            "call_targets": [0x0059EE64, 0x0059AA2A],
            "branch_count": 10,
        },
    }
    am143_tail = am143_delegate_tails.get(entry_address)
    if am143_tail is not None:
        return {
            "available": True,
            "entry_address": entry_address,
            "decoded_byte_count": candidate["bytes_through_return"],
            "return_register": "r0",
            **am143_tail,
            "implementation_readiness": "needs_am143_tail_semantics",
            "firmware_routing_status": "not_yet_routed_into_overlay",
        }
    am144_delegate_tails = {
        0x005A1942: {
            "kind": "am144_literal_runtime_call_tail",
            "call_targets": [0x004ECF64],
            "literal_pool_word": 0x00788230,
            "branch_count": 1,
        },
        0x005A1B48: {
            "kind": "am144_literal_dual_local_delegate_tail",
            "call_targets": [0x005A1970, 0x005A1ADC],
            "literal_pool_word": 0x20070A20,
            "branch_count": 3,
        },
        0x005A1ADC: {
            "kind": "am144_literal_multi_local_delegate_tail",
            "call_targets": [
                0x005A1AC2,
                0x005A1A64,
                0x005A1AC2,
                0x005A1A64,
                0x005A19E0,
            ],
            "literal_pool_word": 0x20070A20,
            "branch_count": 15,
        },
        0x005A1970: {
            "kind": "am144_literal_clear_and_runtime_tail",
            "call_targets": [0x00404104],
            "literal_pool_word": 0x20070A20,
            "branch_count": 3,
        },
        0x005A1398: {
            "kind": "am144_short_local_call_tail_returns_pointer",
            "call_targets": [0x005A1172],
            "branch_count": 1,
        },
        0x005A115C: {
            "kind": "am144_clear_tail_returns_pointer",
            "call_targets": [0x00404104],
            "branch_count": 1,
        },
        0x005A1120: {
            "kind": "am144_dual_local_delegate_tail",
            "call_targets": [0x005A0F6E, 0x005A0EF0],
            "branch_count": 2,
        },
        0x005A1172: {
            "kind": "am144_repeated_local_call_tail",
            "call_targets": [0x005A0F60, 0x005A0F60],
            "branch_count": 2,
        },
        0x005A1138: {
            "kind": "am144_repeated_local_call_tail",
            "call_targets": [0x005A0F3C, 0x005A0F3C],
            "branch_count": 2,
        },
        0x005A13A2: {
            "kind": "am144_repeated_runtime_then_local_tail",
            "call_targets": [0x004EC50E, 0x004EC50E, 0x005A118E],
            "branch_count": 3,
        },
        0x005A1274: {
            "kind": "am144_local_call_tail_returns_pointer",
            "call_targets": [0x005A0F80],
            "branch_count": 4,
        },
        0x005A136A: {
            "kind": "am144_repeated_local_call_tail",
            "call_targets": [0x005A1120, 0x005A1120],
            "branch_count": 4,
        },
        0x005A118E: {
            "kind": "am144_local_call_tail_returns_pointer",
            "call_targets": [0x005A0FCE],
            "branch_count": 9,
        },
        0x005A13F6: {
            "kind": "am144_short_local_call_tail_returns_pointer",
            "call_targets": [0x005A1172],
            "branch_count": 1,
        },
        0x005A1482: {
            "kind": "am144_literal_clear_tail_returns_pointer",
            "call_targets": [0x00404104],
            "literal_pool_word_count": 6,
            "branch_count": 1,
        },
        0x005A15A0: {
            "kind": "am144_repeated_local_parser_tail",
            "call_targets": [0x005A14E0, 0x005A14E0],
            "branch_count": 34,
        },
        0x005A0F80: {
            "kind": "am144_dual_local_delegate_tail",
            "call_targets": [0x005A0F6E, 0x005A0CFE],
            "branch_count": 2,
        },
        0x005A0F3C: {
            "kind": "am144_multi_local_delegate_tail",
            "call_targets": [0x005A0C96, 0x005A0C96, 0x005A0B30],
            "branch_count": 3,
        },
        0x005A0C96: {
            "kind": "am144_local_then_runtime_tail",
            "call_targets": [0x005A0BC2, 0x004F1276],
            "branch_count": 4,
        },
        0x005A0CC8: {
            "kind": "am144_runtime_call_tail_returns_status",
            "call_targets": [0x004F11BC],
            "branch_count": 3,
        },
        0x005A0C5E: {
            "kind": "am144_local_call_tail_returns_pointer",
            "call_targets": [0x005A0BE0],
            "branch_count": 3,
        },
        0x005A0CFE: {
            "kind": "am144_local_call_tail_returns_pointer",
            "call_targets": [0x005A0CC8],
            "branch_count": 3,
        },
        0x005A2BA2: {
            "kind": "am144_literal_runtime_call_tail",
            "call_targets": [0x004ECF64],
            "literal_pool_word": 0x00738644,
            "branch_count": 1,
        },
        0x005A2B5A: {
            "kind": "am144_literal_repeated_local_call_tail",
            "call_targets": [0x005A43E4, 0x005A43E4],
            "literal_pool_word_count": 2,
            "branch_count": 7,
        },
        0x005A2BAE: {
            "kind": "am144_runtime_call_tail_returns_pointer",
            "call_targets": [0x004F11BC],
            "branch_count": 7,
        },
        0x005A08F4: {
            "kind": "am144_runtime_call_tail_returns_pointer",
            "call_targets": [0x004F1276],
            "branch_count": 2,
        },
        0x005A2E74: {
            "kind": "am144_runtime_call_tail_returns_pointer",
            "call_targets": [0x004F1276],
            "branch_count": 1,
        },
        0x005A0B30: {
            "kind": "am144_runtime_call_tail_returns_pointer",
            "call_targets": [0x004F1276],
            "branch_count": 1,
        },
        0x005A0AF0: {
            "kind": "am144_multi_local_delegate_tail",
            "call_targets": [0x005A115C, 0x005A0AC4, 0x005A13CC, 0x005A1482],
            "branch_count": 4,
        },
    }
    am144_tail = am144_delegate_tails.get(entry_address)
    if am144_tail is not None:
        return {
            "available": True,
            "entry_address": entry_address,
            "decoded_byte_count": candidate["bytes_through_return"],
            "return_register": "r0",
            **am144_tail,
            "implementation_readiness": "needs_am144_tail_semantics",
            "firmware_routing_status": "not_yet_routed_into_overlay",
        }
    if entry_address == 0x005A14E0:
        return {
            "available": True,
            "kind": "am144_literal_branch_table_tail_returns_pointer",
            "entry_address": entry_address,
            "decoded_byte_count": candidate["bytes_through_return"],
            "literal_pool_word": 0x005FABB0,
            "branch_count": 22,
            "return_register": "r0",
            "implementation_readiness": "needs_am144_branch_table_semantics",
            "firmware_routing_status": "not_yet_routed_into_overlay",
        }
    am146_delegate_tails = {
        0x005A95B4: {
            "kind": "am146_large_runtime_delegate_tail",
            "call_targets": [0x0052F7B0],
            "branch_count": 6,
        },
        0x005A8526: {
            "kind": "am146_short_runtime_call_tail_returns_pointer",
            "call_targets": [0x004EE964],
            "branch_count": 1,
        },
        0x005A8504: {
            "kind": "am146_runtime_call_tail_returns_pointer",
            "call_targets": [0x004F09D0],
            "branch_count": 1,
        },
        0x005A7524: {
            "kind": "am146_literal_short_local_tail",
            "call_targets": [0x005A74F4],
            "literal_pool_word": 0x68617364,
            "branch_count": 1,
        },
        0x005A7530: {
            "kind": "am146_literal_short_local_tail",
            "call_targets": [0x005A74F4],
            "literal_pool_word": 0x62617464,
            "branch_count": 1,
        },
        0x005A74F4: {
            "kind": "am146_literal_runtime_call_tail",
            "call_targets": [0x004F0C34],
            "literal_pool_word": 0x006EA958,
            "branch_count": 4,
        },
        0x005A753C: {
            "kind": "am146_literal_repeated_runtime_call_tail",
            "call_targets": [0x004F0C34, 0x004F0C34],
            "literal_pool_word_count": 3,
            "branch_count": 9,
        },
        0x005A79F8: {
            "kind": "am146_literal_runtime_call_tail",
            "call_targets": [0x004F0C34],
            "literal_pool_word_count": 2,
            "branch_count": 3,
        },
        0x005A7AF8: {
            "kind": "am146_literal_branch_tail_returns_pointer",
            "call_targets": [],
            "literal_pool_word_count": 2,
            "branch_count": 4,
        },
        0x005A7B38: {
            "kind": "am146_literal_runtime_call_tail",
            "call_targets": [0x004F0C34],
            "literal_pool_word_count": 3,
            "branch_count": 8,
        },
        0x005A7A2C: {
            "kind": "am146_literal_multi_runtime_delegate_tail",
            "call_targets": [
                0x004F09F0,
                0x004F0AC0,
                0x004F0AC0,
                0x004F0A86,
                0x004F11BC,
                0x004F09F0,
                0x004F0AC0,
                0x004F0AC0,
                0x004F0A86,
            ],
            "literal_pool_word": 0x67657270,
            "branch_count": 20,
        },
        0x005A78D2: {
            "kind": "am146_literal_runtime_call_tail",
            "call_targets": [0x004F09B2],
            "literal_pool_word": 0x636b6170,
            "branch_count": 4,
        },
        0x005A8022: {
            "kind": "am146_literal_local_delegate_tail",
            "call_targets": [0x004F0934, 0x005A7D40, 0x005A7F7A],
            "literal_pool_word": 0x706d6174,
            "branch_count": 10,
        },
        0x005A71A2: {
            "kind": "am146_dual_local_runtime_tail",
            "call_targets": [0x005A7178, 0x004F0900],
            "branch_count": 6,
        },
    }
    am146_tail = am146_delegate_tails.get(entry_address)
    if am146_tail is not None:
        return {
            "available": True,
            "entry_address": entry_address,
            "decoded_byte_count": candidate["bytes_through_return"],
            "return_register": "r0",
            **am146_tail,
            "implementation_readiness": "needs_am146_tail_semantics",
            "firmware_routing_status": "not_yet_routed_into_overlay",
        }
    am147_delegate_tails = {
        0x005A9DC8: {
            "kind": "am147_short_local_call_tail_returns_pointer",
            "call_targets": [0x005A9A5C],
            "branch_count": 1,
        },
        0x005A9DDA: {
            "kind": "am147_short_local_call_tail_returns_pointer",
            "call_targets": [0x005A9BFE],
            "branch_count": 1,
        },
        0x005A9DB2: {
            "kind": "am147_short_local_call_tail_returns_pointer",
            "call_targets": [0x005A97E2],
            "branch_count": 1,
        },
        0x005A9D8C: {
            "kind": "am147_local_call_tail_returns_pointer",
            "call_targets": [0x005A9638],
            "branch_count": 1,
        },
        0x005A9F2A: {
            "kind": "am147_literal_multi_delegate_tail",
            "call_targets": [0x0052F79C, 0x004EF528, 0x005A95B4],
            "literal_pool_word": 0x0077B9E4,
            "branch_count": 6,
        },
        0x005A9E9E: {
            "kind": "am147_repeated_local_delegate_tail",
            "call_targets": [0x005A9DEE, 0x005A9DEE, 0x005A9DEE],
            "branch_count": 12,
        },
        0x005A9BFE: {
            "kind": "am147_branch_tail_returns_pointer",
            "call_targets": [],
            "branch_count": 8,
        },
        0x005A9DEE: {
            "kind": "am147_clear_tail_returns_pointer",
            "call_targets": [0x00404104],
            "branch_count": 18,
        },
        0x005A9A5C: {
            "kind": "am147_dual_local_delegate_tail",
            "call_targets": [0x005A9A0A, 0x005A97E2],
            "branch_count": 19,
        },
        0x005AA268: {
            "kind": "am147_runtime_call_tail_returns_pointer",
            "call_targets": [0x004F1276],
            "branch_count": 1,
        },
        0x005AA244: {
            "kind": "am147_runtime_call_tail_returns_pointer",
            "call_targets": [0x004F1168],
            "branch_count": 2,
        },
        0x005AA2D8: {
            "kind": "am147_clear_then_runtime_tail",
            "call_targets": [0x00404104, 0x004EFAEE],
            "branch_count": 3,
        },
        0x005AA2A2: {
            "kind": "am147_dual_runtime_tail",
            "call_targets": [0x004EFBC0, 0x004EFB4E],
            "branch_count": 6,
        },
        0x005AA680: {
            "kind": "am147_short_local_call_tail_returns_pointer",
            "call_targets": [0x005AA300],
            "branch_count": 1,
        },
        0x005AA68E: {
            "kind": "am147_short_local_call_tail_returns_pointer",
            "call_targets": [0x005AA300],
            "branch_count": 1,
        },
        0x005A9638: {
            "kind": "am147_local_delegate_tail_returns_pointer",
            "call_targets": [0x005A95B4],
            "branch_count": 9,
        },
    }
    am147_tail = am147_delegate_tails.get(entry_address)
    if am147_tail is not None:
        return {
            "available": True,
            "entry_address": entry_address,
            "decoded_byte_count": candidate["bytes_through_return"],
            "return_register": "r0",
            **am147_tail,
            "implementation_readiness": "needs_am147_tail_semantics",
            "firmware_routing_status": "not_yet_routed_into_overlay",
        }
    am147_simple_tails = {
        0x005AA292,
        0x005AA27C,
    }
    if entry_address in am147_simple_tails:
        return {
            "available": True,
            "kind": "am147_short_branch_tail_returns_pointer",
            "entry_address": entry_address,
            "decoded_byte_count": candidate["bytes_through_return"],
            "branch_count": 1,
            "return_register": "r0",
            "implementation_readiness": "needs_am147_short_tail_semantics",
            "firmware_routing_status": "not_yet_routed_into_overlay",
        }
    am148_delegate_tails = {
        0x005B298E: {
            "kind": "am148_literal_local_delegate_tail",
            "call_targets": [0x004182A6, 0x004164B8, 0x005B2946],
            "literal_pool_word": 0x2006D8D0,
            "branch_count": 6,
        },
        0x005B27FC: {
            "kind": "am148_literal_runtime_call_tail",
            "call_targets": [0x00405EF4],
            "literal_pool_word": 0x2006D8D0,
            "branch_count": 4,
        },
        0x005B2946: {
            "kind": "am148_literal_multi_local_delegate_tail",
            "call_targets": [0x0055F344, 0x005B28EE, 0x005B2830],
            "literal_pool_word": 0x2006D8D0,
            "branch_count": 9,
        },
        0x005B2830: {
            "kind": "am148_literal_multi_local_delegate_tail",
            "call_targets": [0x0055F344, 0x00405EF4, 0x005B2788],
            "literal_pool_word": 0x2006D8D0,
            "branch_count": 11,
        },
        0x005B28EE: {
            "kind": "am148_runtime_then_local_tail",
            "call_targets": [0x0055F344, 0x005B2888],
            "branch_count": 11,
        },
        0x005B269A: {
            "kind": "am148_literal_clear_and_delegate_tail",
            "call_targets": [0x00404104, 0x005B22E2, 0x00451566],
            "literal_pool_word": 0x200771DC,
            "branch_count": 8,
        },
        0x005B2888: {
            "kind": "am148_literal_runtime_call_tail",
            "call_targets": [0x0055F344],
            "literal_pool_word": 0x2006D8D0,
            "branch_count": 10,
        },
        0x005B2788: {
            "kind": "am148_literal_multi_runtime_delegate_tail",
            "call_targets": [
                0x0055F39C,
                0x00405EF4,
                0x004070BA,
                0x004074E0,
                0x005B2584,
                0x00405FC4,
            ],
            "literal_pool_word": 0x2006D8D0,
            "branch_count": 11,
        },
        0x005B26FA: {
            "kind": "am148_literal_dual_runtime_tail",
            "call_targets": [0x0055F344, 0x004074E0],
            "literal_pool_word": 0x2006D8D0,
            "branch_count": 10,
        },
        0x005B3BB6: {
            "kind": "am148_literal_dual_local_delegate_tail",
            "call_targets": [0x005B33E6, 0x005AD4B8],
            "literal_pool_word": 0x2006D8D0,
            "branch_count": 6,
        },
        0x005B2510: {
            "kind": "am148_runtime_call_tail_returns_status",
            "call_targets": [0x0055F39C],
            "branch_count": 8,
        },
        0x005B2544: {
            "kind": "am148_literal_local_delegate_tail",
            "call_targets": [0x005B2510, 0x005B2312],
            "literal_pool_word_count": 3,
            "branch_count": 11,
        },
        0x005B032C: {
            "kind": "am148_runtime_call_tail_returns_status",
            "call_targets": [0x0055F34A],
            "branch_count": 7,
        },
        0x005B3FCE: {
            "kind": "am148_literal_dual_runtime_call_tail",
            "call_targets": [0x0046144E, 0x00416A4E],
            "literal_pool_word": 0x2006D8D0,
            "branch_count": 5,
        },
        0x005B3C7C: {
            "kind": "am148_quad_runtime_helper_tail",
            "call_targets": [0x0040924A, 0x00409258, 0x0040922E, 0x0040923C],
            "branch_count": 4,
        },
    }
    am148_tail = am148_delegate_tails.get(entry_address)
    if am148_tail is not None:
        return {
            "available": True,
            "entry_address": entry_address,
            "decoded_byte_count": candidate["bytes_through_return"],
            "return_register": "r0",
            **am148_tail,
            "implementation_readiness": "needs_am148_tail_semantics",
            "firmware_routing_status": "not_yet_routed_into_overlay",
        }
    if entry_address == 0x005B0184:
        return {
            "available": True,
            "kind": "am148_literal_prologueless_tail_returns_via_lr",
            "entry_address": entry_address,
            "decoded_byte_count": candidate["bytes_through_return"],
            "literal_pool_word_count": 3,
            "branch_count": 2,
            "terminal_instruction": "bx lr",
            "implementation_readiness": "needs_am148_prologueless_tail_semantics",
            "firmware_routing_status": "not_yet_routed_into_overlay",
        }
    am151_delegate_tails = {
        0x005BA270: {
            "kind": "am151_short_local_call_tail_returns_pointer",
            "call_targets": [0x005C0F52],
            "branch_count": 1,
        },
        0x005BC354: {
            "kind": "am151_runtime_call_tail_returns_pointer",
            "call_targets": [0x004F11BC],
            "branch_count": 3,
        },
        0x005BC2F0: {
            "kind": "am151_runtime_then_local_tail",
            "call_targets": [0x004F11BC, 0x005BC288],
            "branch_count": 4,
        },
        0x005BC288: {
            "kind": "am151_repeated_runtime_call_tail",
            "call_targets": [0x004F1276, 0x004F1276, 0x004F1276, 0x004F1276],
            "branch_count": 4,
        },
        0x005BC06E: {
            "kind": "am151_repeated_runtime_call_tail",
            "call_targets": [
                0x004F1276,
                0x004F1276,
                0x004F1276,
                0x004F1276,
                0x004F1276,
            ],
            "branch_count": 11,
        },
        0x005BB004: {
            "kind": "am151_local_call_tail_returns_pointer",
            "call_targets": [0x005BADB4],
            "branch_count": 5,
        },
        0x005BB032: {
            "kind": "am151_dual_local_delegate_tail",
            "call_targets": [0x005BA8BE, 0x005BADB4],
            "branch_count": 16,
        },
        0x005BC54E: {
            "kind": "am151_local_then_runtime_dispatch_tail",
            "call_targets": [0x005BC23A, 0x00401C24, 0x00401C24, 0x00401C24],
            "branch_count": 5,
        },
        0x005B9DFA: {
            "kind": "am151_short_local_call_tail_returns_pointer",
            "call_targets": [0x005B9D22],
            "branch_count": 1,
        },
        0x005B9DF0: {
            "kind": "am151_short_local_call_tail_returns_pointer",
            "call_targets": [0x005B9D22],
            "branch_count": 1,
        },
    }
    am151_tail = am151_delegate_tails.get(entry_address)
    if am151_tail is not None:
        return {
            "available": True,
            "entry_address": entry_address,
            "decoded_byte_count": candidate["bytes_through_return"],
            "return_register": "r0",
            **am151_tail,
            "implementation_readiness": "needs_am151_tail_semantics",
            "firmware_routing_status": "not_yet_routed_into_overlay",
        }
    if entry_address == 0x005BC5E0:
        return {
            "available": True,
            "kind": "am151_short_branch_tail_returns_pointer",
            "entry_address": entry_address,
            "decoded_byte_count": candidate["bytes_through_return"],
            "branch_count": 1,
            "return_register": "r0",
            "implementation_readiness": "needs_am151_short_tail_semantics",
            "firmware_routing_status": "not_yet_routed_into_overlay",
        }
    am153_delegate_tails = {
        0x005BF65A: {
            "kind": "am153_large_branch_tail_returns_pointer",
            "call_targets": [],
            "branch_count": 21,
        },
        0x005C12B2: {
            "kind": "am153_runtime_call_tail_returns_pointer",
            "call_targets": [0x004F09D0],
            "branch_count": 1,
        },
        0x005C154C: {
            "kind": "am153_dual_runtime_call_tail",
            "call_targets": [0x004F1276, 0x004F09D0],
            "branch_count": 2,
        },
        0x005C137C: {
            "kind": "am153_literal_runtime_call_tail",
            "call_targets": [0x004F09B2],
            "literal_pool_word": 0x6666696D,
            "branch_count": 5,
        },
        0x005C13C4: {
            "kind": "am153_literal_runtime_call_tail",
            "call_targets": [0x004F09B2],
            "literal_pool_word": 0x706F6570,
            "branch_count": 5,
        },
        0x005C12C8: {
            "kind": "am153_literal_multi_runtime_delegate_tail",
            "call_targets": [0x004F11BC, 0x004F09F0, 0x004F0AC0, 0x004F0A86, 0x005BB38C],
            "literal_pool_word": 0x63737020,
            "branch_count": 15,
        },
        0x005C106A: {
            "kind": "am153_short_runtime_call_tail_returns_pointer",
            "call_targets": [0x004ECCA8],
            "branch_count": 1,
        },
    }
    am153_tail = am153_delegate_tails.get(entry_address)
    if am153_tail is not None:
        return {
            "available": True,
            "entry_address": entry_address,
            "decoded_byte_count": candidate["bytes_through_return"],
            "return_register": "r0",
            **am153_tail,
            "implementation_readiness": "needs_am153_tail_semantics",
            "firmware_routing_status": "not_yet_routed_into_overlay",
        }
    am149_delegate_tails = {
        0x005B4B1A: {
            "kind": "am149_short_local_call_tail_returns_pointer",
            "call_targets": [0x005B4ACC],
            "branch_count": 1,
        },
        0x005B4AA4: {
            "kind": "am149_runtime_profile_tail_returns_status",
            "call_targets": [0x0055F364, 0x004458EE],
            "branch_count": 6,
        },
        0x005B4C0A: {
            "kind": "am149_local_service_tail_returns_pointer",
            "call_targets": [0x005AD4B0],
            "branch_count": 5,
        },
        0x005B4B72: {
            "kind": "am149_literal_local_call_tail",
            "call_targets": [0x005B4A84],
            "literal_pool_word": 0x2006D8D0,
            "branch_count": 5,
        },
        0x005B4B28: {
            "kind": "am149_multi_runtime_metric_tail",
            "call_targets": [
                0x0040906C,
                0x0040930C,
                0x0040932C,
                0x0055180E,
                0x005518B2,
            ],
            "branch_count": 10,
        },
        0x005B4ACC: {
            "kind": "am149_runtime_then_local_delegate_tail",
            "call_targets": [0x0055F34A, 0x005B4A68, 0x0055F3D2],
            "branch_count": 11,
        },
        0x005B4C3A: {
            "kind": "am149_literal_multi_local_delegate_tail",
            "call_targets": [
                0x005B4B72,
                0x005B4B72,
                0x0055171C,
                0x005B4BA8,
                0x005B4C0A,
            ],
            "literal_pool_word": 0x2006D8D0,
            "branch_count": 10,
        },
        0x005B4BA8: {
            "kind": "am149_literal_repeated_local_delegate_tail",
            "call_targets": [0x005B4A68, 0x005B4B28, 0x005B4B28],
            "literal_pool_word": 0x2006D8D0,
            "branch_count": 10,
        },
        0x005B4A68: {
            "kind": "am149_runtime_call_tail_returns_pointer",
            "call_targets": [0x0055F34A],
            "branch_count": 5,
        },
        0x005B49E0: {
            "kind": "am149_literal_runtime_call_tail",
            "call_targets": [0x004157D8],
            "literal_pool_word": 0x2006D8D0,
            "branch_count": 2,
        },
        0x005B4A20: {
            "kind": "am149_quad_runtime_helper_tail",
            "call_targets": [0x0040924A, 0x00409258, 0x0040922E, 0x0040923C],
            "branch_count": 4,
        },
        0x005B4000: {
            "kind": "am149_literal_runtime_call_tail",
            "call_targets": [0x0046144E],
            "literal_pool_word": 0x2006D8D0,
            "branch_count": 2,
        },
        0x005B4288: {
            "kind": "am149_literal_multi_runtime_service_tail",
            "call_targets": [
                0x00415CC2,
                0x004157D8,
                0x004157D8,
                0x0055F3FC,
                0x005AD4A4,
                0x004094A8,
            ],
            "literal_pool_word": 0x2006D8D0,
            "branch_count": 10,
        },
        0x005B5DE8: {
            "kind": "am149_literal_format_tail_returns_status",
            "call_targets": [0x00413748],
            "literal_pool_word": 0x0078C45C,
            "branch_count": 5,
        },
        0x005B5E16: {
            "kind": "am149_literal_length_match_delegate_tail",
            "call_targets": [0x0041245C, 0x00413630, 0x005B5B10],
            "literal_pool_word": 0x00789FB0,
            "branch_count": 6,
        },
        0x005B5E50: {
            "kind": "am149_local_path_format_tail_returns_status",
            "call_targets": [0x005B5AFC, 0x00455894, 0x005B5BC2],
            "branch_count": 17,
        },
        0x005B4790: {
            "kind": "am149_literal_multi_runtime_service_tail",
            "call_targets": [
                0x00415CC2,
                0x004157D8,
                0x004157D8,
                0x0055F3FC,
                0x005AD4A4,
                0x004094A8,
            ],
            "literal_pool_word": 0x2006D8D0,
            "branch_count": 10,
        },
        0x005B70D0: {
            "kind": "am149_literal_compare_tail_returns_status",
            "call_targets": [0x00434AEC],
            "literal_pool_word": 0x007845D4,
            "branch_count": 6,
        },
        0x005B5768: {
            "kind": "am149_dual_local_delegate_tail",
            "call_targets": [0x005B4ED2, 0x005AD462],
            "branch_count": 2,
        },
    }
    am149_tail = am149_delegate_tails.get(entry_address)
    if am149_tail is not None:
        return {
            "available": True,
            "entry_address": entry_address,
            "decoded_byte_count": candidate["bytes_through_return"],
            "return_register": "r0",
            **am149_tail,
            "implementation_readiness": "needs_am149_tail_semantics",
            "firmware_routing_status": "not_yet_routed_into_overlay",
        }
    if entry_address == 0x005B8FD4:
        return {
            "available": True,
            "kind": "am150_short_runtime_call_tail_returns_pointer",
            "entry_address": entry_address,
            "decoded_byte_count": candidate["bytes_through_return"],
            "call_targets": [0x004F1398],
            "branch_count": 1,
            "return_register": "r0",
            "implementation_readiness": "needs_am150_short_tail_semantics",
            "firmware_routing_status": "not_yet_routed_into_overlay",
        }
    if entry_address == 0x005A4A66:
        return {
            "available": True,
            "kind": "am145_large_state_tail_calls_prior_entry",
            "entry_address": entry_address,
            "call_target": 0x005A49BC,
            "decoded_byte_count": candidate["bytes_through_return"],
            "branch_count": 23,
            "return_register_passthrough": "r0",
            "implementation_readiness": "needs_am145_state_tail_semantics",
            "firmware_routing_status": "not_yet_routed_into_overlay",
        }
    if entry_address == 0x005A4802:
        return {
            "available": True,
            "kind": "am145_state_tail_calls_prior_entry",
            "entry_address": entry_address,
            "call_target": 0x005A47B0,
            "decoded_byte_count": candidate["bytes_through_return"],
            "branch_count": 5,
            "return_register_passthrough": "r0",
            "implementation_readiness": "needs_am145_tail_wrapper_semantics",
            "firmware_routing_status": "not_yet_routed_into_overlay",
        }
    if entry_address == 0x005A6E34:
        return {
            "available": True,
            "kind": "am145_short_conditional_tail_returns_pointer",
            "entry_address": entry_address,
            "decoded_byte_count": candidate["bytes_through_return"],
            "branch_count": 3,
            "return_register": "r0",
            "implementation_readiness": "needs_am145_conditional_tail_semantics",
            "firmware_routing_status": "not_yet_routed_into_overlay",
        }
    am145_delegate_tails = {
        0x005A67D2: {
            "kind": "am145_delegate_tail_calls_local_parser",
            "call_targets": [0x005A6290],
            "branch_count": 5,
        },
        0x005A66CC: {
            "kind": "am145_multi_delegate_tail_calls_local_parsers",
            "call_targets": [0x005A6672, 0x005A65B0, 0x005A660E],
            "branch_count": 11,
        },
        0x005A674A: {
            "kind": "am145_multi_delegate_tail_calls_local_parsers",
            "call_targets": [0x005A6672, 0x005A65B0, 0x005A660E],
            "branch_count": 11,
        },
        0x005A6C52: {
            "kind": "am145_single_call_tail_returns_pointer",
            "call_targets": [0x005A812E],
            "branch_count": 1,
        },
        0x005A6C7C: {
            "kind": "am145_runtime_call_tail_returns_pointer",
            "call_targets": [0x004F1276],
            "branch_count": 1,
        },
        0x005A4286: {
            "kind": "am145_runtime_call_tail_returns_pointer",
            "call_targets": [0x004F09D0],
            "branch_count": 3,
        },
        0x005A6270: {
            "kind": "am145_runtime_call_tail_returns_pointer",
            "call_targets": [0x004F1276],
            "branch_count": 3,
        },
    }
    delegate_tail = am145_delegate_tails.get(entry_address)
    if delegate_tail is not None:
        return {
            "available": True,
            "entry_address": entry_address,
            "decoded_byte_count": candidate["bytes_through_return"],
            "return_register": "r0",
            **delegate_tail,
            "implementation_readiness": "needs_am145_delegate_tail_semantics",
            "firmware_routing_status": "not_yet_routed_into_overlay",
        }
    am145_simple_tails = {
        0x005A6C94: "am145_short_condition_tail_returns_pointer",
        0x005A6CA2: "am145_short_condition_tail_returns_pointer",
    }
    simple_tail_kind = am145_simple_tails.get(entry_address)
    if simple_tail_kind is not None:
        return {
            "available": True,
            "kind": simple_tail_kind,
            "entry_address": entry_address,
            "decoded_byte_count": candidate["bytes_through_return"],
            "branch_count": 1,
            "return_register": "r0",
            "implementation_readiness": "needs_am145_short_tail_semantics",
            "firmware_routing_status": "not_yet_routed_into_overlay",
        }
    if entry_address == 0x005A6C5E:
        return {
            "available": True,
            "kind": "am145_literal_pointer_tail_returns_pointer",
            "entry_address": entry_address,
            "decoded_byte_count": candidate["bytes_through_return"],
            "literal_pool_word": 0x005DEE33,
            "branch_count": 1,
            "return_register": "r0",
            "implementation_readiness": "needs_am145_literal_tail_semantics",
            "firmware_routing_status": "not_yet_routed_into_overlay",
        }
    am152_delegate_tails = {
        0x005BE50E: {
            "kind": "am152_dual_local_delegate_tail",
            "call_targets": [0x005BE23C, 0x005BE30A],
            "branch_count": 15,
        },
        0x005BE44C: {
            "kind": "am152_dual_local_delegate_tail",
            "call_targets": [0x005BE23C, 0x005BE30A],
            "branch_count": 16,
        },
        0x005BDA08: {
            "kind": "am152_local_wrapper_tail_returns_pointer",
            "call_targets": [0x005BCDAE],
            "branch_count": 1,
        },
        0x005BDAB0: {
            "kind": "am152_runtime_call_tail_returns_pointer",
            "call_targets": [0x004EC718],
            "branch_count": 1,
        },
        0x005BDB5E: {
            "kind": "am152_literal_local_call_tail",
            "call_targets": [0x005BCCA2],
            "literal_pool_word": 0x005F4BCF,
            "branch_count": 1,
        },
        0x005BDB7C: {
            "kind": "am152_literal_local_call_tail",
            "call_targets": [0x005BCCA2],
            "literal_pool_word": 0x005F4C2B,
            "branch_count": 1,
        },
        0x005BDA46: {
            "kind": "am152_dual_local_wrapper_tail",
            "call_targets": [0x005BCED2, 0x005BCDAE],
            "branch_count": 2,
        },
        0x005BDE5A: {
            "kind": "am152_runtime_dispatch_tail_returns_pointer",
            "call_targets": [0x00401C24],
            "branch_count": 4,
        },
        0x005BDEA0: {
            "kind": "am152_runtime_dispatch_tail_returns_pointer",
            "call_targets": [0x00401C24],
            "branch_count": 4,
        },
        0x005BDEE6: {
            "kind": "am152_runtime_dispatch_tail_returns_pointer",
            "call_targets": [0x00401C24],
            "branch_count": 4,
        },
        0x005BDA1C: {
            "kind": "am152_dual_local_wrapper_tail",
            "call_targets": [0x005BCED2, 0x005BCDAE],
            "branch_count": 2,
        },
        0x005BDD9C: {
            "kind": "am152_multi_local_delegate_tail",
            "call_targets": [0x005BCED2, 0x005BCED2, 0x005BCDAE],
            "branch_count": 11,
        },
        0x005BDC8E: {
            "kind": "am152_repeated_runtime_call_tail",
            "call_targets": [0x004EC718, 0x004EC718, 0x004EC718],
            "branch_count": 18,
        },
        0x005BD44E: {
            "kind": "am152_short_local_call_tail_returns_pointer",
            "call_targets": [0x005BD3D8],
            "branch_count": 2,
        },
        0x005BD45C: {
            "kind": "am152_short_local_call_tail_returns_pointer",
            "call_targets": [0x005BD3D8],
            "branch_count": 2,
        },
        0x005BD3AA: {
            "kind": "am152_local_parser_tail_returns_pointer",
            "call_targets": [0x005BD29A],
            "branch_count": 8,
        },
        0x005BD51E: {
            "kind": "am152_local_decoder_tail_returns_pointer",
            "call_targets": [0x005BC80E],
            "branch_count": 5,
        },
        0x005BD46A: {
            "kind": "am152_large_local_parser_tail_returns_pointer",
            "call_targets": [0x005BD29A],
            "branch_count": 18,
        },
        0x005BD07E: {
            "kind": "am152_runtime_call_tail_returns_pointer",
            "call_targets": [0x004EC626],
            "branch_count": 1,
        },
        0x005BD1B2: {
            "kind": "am152_local_call_tail_returns_pointer",
            "call_targets": [0x005BCA8E],
            "branch_count": 1,
        },
        0x005BD060: {
            "kind": "am152_runtime_call_tail_returns_pointer",
            "call_targets": [0x004EC6B0],
            "branch_count": 3,
        },
        0x005BD130: {
            "kind": "am152_runtime_call_tail_returns_pointer",
            "call_targets": [0x004EC718],
            "branch_count": 4,
        },
        0x005BD1E8: {
            "kind": "am152_runtime_dispatch_tail_returns_pointer",
            "call_targets": [0x00401730],
            "branch_count": 5,
        },
        0x005BC942: {
            "kind": "am152_repeated_runtime_call_tail",
            "call_targets": [0x004EC626, 0x004EC626],
            "branch_count": 4,
        },
        0x005BCED2: {
            "kind": "am152_runtime_call_tail_returns_status",
            "call_targets": [0x004EC922],
            "branch_count": 3,
        },
        0x005BD7FA: {
            "kind": "am152_local_decoder_tail_returns_pointer",
            "call_targets": [0x005BC7DE],
            "branch_count": 5,
        },
        0x005BC780: {
            "kind": "am152_local_then_runtime_tail",
            "call_targets": [0x005BC6D8, 0x004EC774],
            "branch_count": 2,
        },
        0x005BC7B4: {
            "kind": "am152_local_then_runtime_tail",
            "call_targets": [0x005BC6D8, 0x004EC774],
            "branch_count": 2,
        },
        0x005BD972: {
            "kind": "am152_local_wrapper_tail_returns_pointer",
            "call_targets": [0x005BCDAE],
            "branch_count": 3,
        },
        0x005BD902: {
            "kind": "am152_local_wrapper_tail_returns_pointer",
            "call_targets": [0x005BCED2],
            "branch_count": 7,
        },
        0x005BC73A: {
            "kind": "am152_local_then_runtime_tail",
            "call_targets": [0x005BC6D8, 0x004EC718],
            "branch_count": 2,
        },
        0x005BC6D8: {
            "kind": "am152_dual_local_then_runtime_tail",
            "call_targets": [0x005BC61A, 0x005BC61A, 0x004EC55C],
            "branch_count": 8,
        },
        0x005BCD7A: {
            "kind": "am152_local_call_tail_returns_pointer",
            "call_targets": [0x005BC658],
            "branch_count": 1,
        },
        0x005BCD90: {
            "kind": "am152_local_call_tail_returns_pointer",
            "call_targets": [0x005BC658],
            "branch_count": 1,
        },
    }
    am152_tail = am152_delegate_tails.get(entry_address)
    if am152_tail is not None:
        return {
            "available": True,
            "entry_address": entry_address,
            "decoded_byte_count": candidate["bytes_through_return"],
            "return_register": "r0",
            **am152_tail,
            "implementation_readiness": "needs_am152_tail_semantics",
            "firmware_routing_status": "not_yet_routed_into_overlay",
        }
    am152_simple_tails = {
        0x005BE3C2: {"kind": "am152_short_branch_tail_returns_pointer", "branch_count": 2},
        0x005BE5AC: {"kind": "am152_medium_branch_tail_returns_pointer", "branch_count": 6},
        0x005BE79A: {"kind": "am152_medium_branch_tail_returns_pointer", "branch_count": 8},
        0x005BE6B2: {"kind": "am152_large_branch_tail_returns_pointer", "branch_count": 9},
        0x005BDBC0: {"kind": "am152_branch_table_tail_returns_pointer", "branch_count": 7},
        0x005BDC14: {"kind": "am152_branch_table_tail_returns_pointer", "branch_count": 6},
        0x005BD574: {"kind": "am152_short_branch_tail_returns_pointer", "branch_count": 1},
        0x005BD61E: {"kind": "am152_short_branch_tail_returns_pointer", "branch_count": 1},
        0x005BED12: {"kind": "am152_conditional_tail_returns_pointer", "branch_count": 3},
        0x005BD196: {"kind": "am152_short_branch_tail_returns_pointer", "branch_count": 1},
        0x005BD10A: {"kind": "am152_conditional_tail_returns_pointer", "branch_count": 4},
        0x005BD162: {"kind": "am152_conditional_tail_returns_pointer", "branch_count": 5},
        0x005BCF04: {"kind": "am152_short_branch_tail_returns_pointer", "branch_count": 1},
        0x005BCFEA: {"kind": "am152_conditional_tail_returns_pointer", "branch_count": 3},
        0x005BCFC8: {"kind": "am152_conditional_tail_returns_pointer", "branch_count": 3},
    }
    am152_simple_tail = am152_simple_tails.get(entry_address)
    if am152_simple_tail is not None:
        return {
            "available": True,
            "entry_address": entry_address,
            "decoded_byte_count": candidate["bytes_through_return"],
            "return_register": "r0",
            **am152_simple_tail,
            "implementation_readiness": "needs_am152_branch_tail_semantics",
            "firmware_routing_status": "not_yet_routed_into_overlay",
        }
    if entry_address == 0x00547294:
        return {
            "available": True,
            "kind": "gated_dynamic_path_normalize_iterative_query_dump_returns_zero",
            "entry_address": entry_address,
            "gate_pointer": 0x200746A8,
            "input_context_register": "r2",
            "stack_frame_bytes": 0x44C,
            "dynamic_segment_call": 0x0054C91C,
            "dynamic_segment_mode": 1,
            "raw_path_buffer_offset": 0x34C,
            "normalized_path_buffer_offset": 0x24C,
            "path_builder_call": 0x00413748,
            "normalizer_call": 0x00546AC8,
            "query_context": 0x20071AC8,
            "query_state_buffer_offset": 0xF0,
            "query_record_buffer_offset": 0x144,
            "query_open_call": 0x00497AAA,
            "query_prepare_call": 0x00497AB4,
            "query_record_call": 0x00497B60,
            "query_close_call": 0x00497AF0,
            "iterator_state_buffer_offset": 0x58,
            "iterator_item_buffer_offset": 0x18,
            "iterator_begin_call": 0x0055D46E,
            "iterator_next_call": 0x0055D598,
            "dump_buffer_offset": 8,
            "dump_buffer_bytes": 0x10,
            "dump_build_call": 0x0055D628,
            "primary_literal": 0x200031B4,
            "path_format_literal": 0x0078E13C,
            "error_log_call": 0x0043B40E,
            "return_value": 0,
            "implementation_readiness": "needs_iterative_query_dump_semantics",
            "firmware_routing_status": "not_yet_routed_into_overlay",
        }
    if entry_address == 0x00546E2C:
        return {
            "available": True,
            "kind": "gated_two_token_path_compare_update_returns_zero",
            "entry_address": entry_address,
            "gate_pointer": 0x200746A8,
            "input_context_register": "r2",
            "stack_frame_bytes": 0x91C,
            "token_delimiter": "space",
            "token_count": 2,
            "token_length_limit": 0xFF,
            "first_token_buffer_offset": 0x81C,
            "second_token_buffer_offset": 0x71C,
            "first_path_buffer_offset": 0x61C,
            "second_path_buffer_offset": 0x520,
            "first_normalized_path_buffer_offset": 0x420,
            "second_normalized_path_buffer_offset": 0x31C,
            "compare_status_buffer_offset": 0x214,
            "update_status_buffer_offset": 0x10C,
            "merged_path_buffer_offset": 0x0C,
            "primary_literal": 0x200031B4,
            "query_context": 0x20071AC8,
            "copy_call": 0x004135C0,
            "clear_call": 0x00404104,
            "copy_string_call": 0x00455560,
            "length_call": 0x0041245C,
            "append_call": 0x0052FCA0,
            "find_char_call": 0x0052FC84,
            "normalizer_call": 0x00546AC8,
            "query_open_call": 0x00497AAA,
            "query_update_call": 0x00497AA0,
            "debug_gate_call": 0x004050EE,
            "debug_log_call": 0x00405594,
            "debug_emit_call": 0x00404EBE,
            "error_log_call": 0x0043B40E,
            "return_value": 0,
            "implementation_readiness": "needs_two_token_path_update_semantics",
            "firmware_routing_status": "not_yet_routed_into_overlay",
        }
    path_builder_variants = {
        0x00546940: {
            "kind": "gated_dynamic_path_query_extended_output_returns_zero",
            "stack_frame_bytes": 0x118,
            "variant_log_literal": None,
            "variant_success_call": 0x00497AB4,
            "fallback_call": 0x00497AF0,
            "extra_output_buffer_offset": 4,
            "final_call_context_register": "r6",
            "input_context_register": "r2",
            "dynamic_segment_call": 0x0054C91C,
            "dynamic_segment_mode": 1,
            "path_join_buffer_offset": 0x44,
            "path_join_buffer_bytes": 0x80,
            "query_output_buffer_offset": 0xC4,
            "query_output_buffer_bytes": 0x40,
            "query_success_call": 0x00497B60,
        },
        0x00546A2A: {
            "kind": "gated_stack_path_builder_returns_zero",
            "stack_frame_bytes": 0x104,
            "variant_log_literal": None,
            "variant_success_call": 0x00497A96,
            "fallback_call": None,
            "extra_output_buffer_offset": None,
            "final_call_context_register": "r0",
        },
        0x00546C9C: {
            "kind": "gated_stack_path_builder_status_log_returns_zero",
            "stack_frame_bytes": 0x104,
            "variant_log_literal": 0x0076FDD8,
            "variant_success_call": 0x00497C7C,
            "fallback_call": None,
            "extra_output_buffer_offset": None,
            "final_call_context_register": "r0",
        },
        0x00546D46: {
            "kind": "gated_stack_path_builder_extended_output_returns_zero",
            "stack_frame_bytes": 0x158,
            "variant_log_literal": 0x0076FDD8,
            "variant_success_call": 0x00497AB4,
            "fallback_call": 0x00497AF0,
            "extra_output_buffer_offset": 0x104,
            "final_call_context_register": "r4",
        },
    }
    variant = path_builder_variants.get(entry_address)
    if variant is not None:
        return {
            "available": True,
            **variant,
            "entry_address": entry_address,
            "gate_pointer": 0x200746A8,
            "success_stack_buffer_offset": 4,
            "max_stack_buffer_bytes": 0x100,
            "path_length_limit": 0x101,
            "primary_literal": 0x200031B4,
            "overflow_log_literal": 0x0078272C,
            "final_call_context": 0x20071AC8,
            "return_value": 0,
            "implementation_readiness": "needs_path_helper_semantics",
            "firmware_routing_status": "not_yet_routed_into_overlay",
        }
    return None


def analyze() -> dict:
    quality = raw_quality.analyze()
    mixed = mixed_boundary.analyze()
    rows = quality["public_unrouted_raw_instruction_sources"]
    am_numbers = []
    for row in rows:
        number = _am_helper_number(row["source"])
        if number is not None:
            am_numbers.append(number)
    sources = [row["source"] for row in rows]
    raw_transcript_bytes = sum(row["inst_directive_bytes"] for row in rows)
    if mixed["inst_directive_bytes"] != raw_transcript_bytes:
        raise RuntimeError("AM mixed-boundary bytes disagree with gate raw transcript bytes")
    helper_ranges = _ranges(am_numbers)
    batches = _raw_helper_batches(rows, helper_ranges)
    return {
        "schema_version": 1,
        "quality_gate": quality["quality_gate"],
        "source_ownership_suitable": quality["source_ownership_suitable"],
        "raw_transcript_source_count": len(rows),
        "raw_transcript_bytes": raw_transcript_bytes,
        "source_path_sha256": _digest(sources),
        "am_helper_ranges": helper_ranges,
        "raw_helper_batch_frontier": batches,
        "top_raw_helper_batch_decomposition": _top_batch_decomposition(
            rows,
            batches[0],
        ),
        "focused_raw_helper_subrange": _focused_subrange_decomposition(
            rows,
            mixed["sources"],
            135,
            153,
        ),
        "largest_source_function_frontier": _largest_source_function_frontier(
            rows,
            mixed["sources"],
        ),
        "mixed_boundary_reason_counts": mixed["reason_counts"],
        "mixed_boundary_function_class_counts": mixed["function_class_counts"],
        "largest_sources": sorted(
            rows, key=lambda row: (-row["inst_directive_bytes"], row["source"])
        )[:12],
        "sources": rows,
    }


def main() -> int:
    report = analyze()
    OUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps({
        "source_ownership_suitable": report["source_ownership_suitable"],
        "raw_transcript_source_count": report["raw_transcript_source_count"],
        "raw_transcript_bytes": report["raw_transcript_bytes"],
        "mixed_boundary_reason_counts": report["mixed_boundary_reason_counts"],
        "am_helper_ranges": report["am_helper_ranges"],
        "source_path_sha256": report["source_path_sha256"],
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
