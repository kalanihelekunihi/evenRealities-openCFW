#!/usr/bin/env python3
"""Classify the complement of the authenticated EM9305 function map."""

from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import struct
from typing import Any, Sequence

import analyze_em9305_sdk_discovery as discovery
import analyze_em9305_sdk_link_order as link_order


VECTOR_START = discovery.APP_BASE
VECTOR_END = 0x0030_2508
VECTOR_SHA256 = "8a75d411f79f380a21da285778a62241d3b2acc236244ac46c51bbd814d82779"
POST_TEXT_START = 0x0033_3E9A
POST_TEXT_END = discovery.APP_BASE + discovery.APP_SIZE
POST_TEXT_SHA256 = "802191f5b086b2a3c66f2775cd3686d31faead39e929372b70f1462d824eca45"
NOP_S = b"\xE0\x78"

EXPECTED_COMPLEMENT_BYTES = 43_204
EXPECTED_SEGMENT_COUNTS = {
    "stock_retained_vector_table": 1,
    "stock_retained_alignment_nop": 906,
    "stock_retained_post_text_tables_data": 1,
    "stock_retained_unresolved_code_or_mixed": 175,
}
EXPECTED_STATUS_BYTES = {
    "stock_retained_vector_table": 264,
    "stock_retained_alignment_nop": 1_812,
    "stock_retained_post_text_tables_data": 7_470,
    "stock_retained_unresolved_code_or_mixed": 33_658,
}


class ResidualSegmentError(RuntimeError):
    """Raised when a residual-segment identity or invariant changes."""


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def complement(intervals: Sequence[tuple[int, int]]) -> list[tuple[int, int]]:
    """Return gaps in the complete application after merging input intervals."""
    gaps: list[tuple[int, int]] = []
    cursor = discovery.APP_BASE
    for start, end in link_order.merge_intervals(intervals):
        if start < discovery.APP_BASE or end > POST_TEXT_END or start >= end:
            raise ResidualSegmentError("function interval outside EM9305 application")
        if cursor < start:
            gaps.append((cursor, start))
        cursor = max(cursor, end)
    if cursor < POST_TEXT_END:
        gaps.append((cursor, POST_TEXT_END))
    return gaps


def split_gap(start: int, end: int, body: bytes) -> list[dict[str, Any]]:
    """Split boundary NOPs and structural data from an unclaimed map gap."""
    if end - start != len(body) or start >= end:
        raise ResidualSegmentError("invalid residual gap")
    low = 0
    high = len(body)
    while low + 2 <= high and body[low:low + 2] == NOP_S:
        low += 2
    while high - 2 >= low and body[high - 2:high] == NOP_S:
        high -= 2

    ranges: list[tuple[int, int, str, str]] = []
    if low:
        ranges.append((
            start,
            start + low,
            "stock_retained_alignment_nop",
            "fully_classified_padding",
        ))

    residual_start = start + low
    residual_end = start + high
    if residual_start < residual_end:
        cuts = sorted({
            residual_start,
            residual_end,
            *(
                boundary
                for boundary in (VECTOR_START, VECTOR_END, POST_TEXT_START, POST_TEXT_END)
                if residual_start < boundary < residual_end
            ),
        })
        for part_start, part_end in zip(cuts, cuts[1:]):
            if VECTOR_START <= part_start and part_end <= VECTOR_END:
                status = "stock_retained_vector_table"
                state = "format_fully_identified_contents_stock_retained"
            elif POST_TEXT_START <= part_start and part_end <= POST_TEXT_END:
                status = "stock_retained_post_text_tables_data"
                state = "data_classified_semantics_partial"
            else:
                status = "stock_retained_unresolved_code_or_mixed"
                state = "opaque_or_partially_reversed"
            ranges.append((part_start, part_end, status, state))

    if high < len(body):
        ranges.append((
            start + high,
            end,
            "stock_retained_alignment_nop",
            "fully_classified_padding",
        ))

    return [
        {
            "start": part_start,
            "end": part_end,
            "size": part_end - part_start,
            "status": status,
            "reverse_engineering_state": state,
            "sha256": sha256(body[part_start - start:part_end - start]),
        }
        for part_start, part_end, status, state in ranges
    ]


def analyze(
    baseline_output: Path,
    enforced_output: Path,
    round2_output: Path,
    round1_min8_output: Path,
    round2_min8_output: Path,
    application_objdump: Path,
    *,
    image: Path = discovery.DEFAULT_IMAGE,
) -> dict[str, Any]:
    exact = discovery.analyze_low_floor(
        baseline_output,
        enforced_output,
        round2_output,
        round1_min8_output,
        round2_min8_output,
        application_objdump,
        image=image,
        include_functions=True,
    )
    placed = link_order.analyze(
        baseline_output,
        enforced_output,
        round2_output,
        round1_min8_output,
        round2_min8_output,
        application_objdump,
        image=image,
    )
    provenance_intervals = [
        (item["address"], item["end"])
        for item in exact["functions"]
    ] + [
        (item["address"], item["end"])
        for item in placed["placements"]
    ]
    gaps = complement(provenance_intervals)
    image_bytes = image.resolve().read_bytes()
    application = image_bytes[
        discovery.APP_FILE_OFFSET:discovery.APP_FILE_OFFSET + discovery.APP_SIZE
    ]
    if len(application) != discovery.APP_SIZE:
        raise ResidualSegmentError("official EM9305 application record truncated")

    vector = application[VECTOR_START - discovery.APP_BASE:VECTOR_END - discovery.APP_BASE]
    post_text = application[
        POST_TEXT_START - discovery.APP_BASE:POST_TEXT_END - discovery.APP_BASE
    ]
    vector_words = [
        struct.unpack_from("<I", vector, offset)[0]
        for offset in range(0, len(vector), 4)
    ]
    if (
        sha256(vector) != VECTOR_SHA256
        or len(vector_words) != 66
        or vector_words[0] != 0x0010_03D0
        or sum(discovery.APP_BASE <= value < POST_TEXT_END for value in vector_words[1:]) != 58
        or sum(0x0010_0000 <= value < 0x0011_0000 for value in vector_words[1:]) != 7
    ):
        raise ResidualSegmentError("EM9305 vector-table identity changed")
    if (
        sha256(post_text) != POST_TEXT_SHA256
        or b"MyApp\x00" not in post_text
        or b"qf_dyn\x00" not in post_text
        or b"WsfOs\x00" not in post_text
        or max(item["end"] for item in exact["functions"]) != POST_TEXT_START
    ):
        raise ResidualSegmentError("EM9305 post-text table/data identity changed")

    segments: list[dict[str, Any]] = []
    for start, end in gaps:
        body = application[start - discovery.APP_BASE:end - discovery.APP_BASE]
        segments.extend(split_gap(start, end, body))

    status_counts = Counter(item["status"] for item in segments)
    status_bytes = Counter()
    for item in segments:
        status_bytes[item["status"]] += item["size"]
    if (
        dict(status_counts) != EXPECTED_SEGMENT_COUNTS
        or dict(status_bytes) != EXPECTED_STATUS_BYTES
        or sum(item["size"] for item in segments) != EXPECTED_COMPLEMENT_BYTES
        or len(gaps) != 880
    ):
        raise ResidualSegmentError(
            "EM9305 residual-segment census changed: "
            f"gaps={len(gaps)}, segments={dict(status_counts)}, "
            f"bytes={dict(status_bytes)}, total={sum(item['size'] for item in segments)}"
        )

    previous_end: int | None = None
    for item in segments:
        if previous_end is not None and item["start"] < previous_end:
            raise ResidualSegmentError("residual segments overlap")
        previous_end = item["end"]

    unresolved = [
        item for item in segments
        if item["status"] == "stock_retained_unresolved_code_or_mixed"
    ]
    return {
        "application_base": discovery.APP_BASE,
        "application_end": POST_TEXT_END,
        "application_bytes": discovery.APP_SIZE,
        "function_provenance_identified_bytes": placed["provenance_identified_application_bytes"],
        "residual_gap_count_before_splitting": len(gaps),
        "residual_segment_count": len(segments),
        "residual_bytes": sum(item["size"] for item in segments),
        "status_segment_counts": dict(status_counts),
        "status_bytes": dict(status_bytes),
        "structurally_classified_non_code_bytes": (
            status_bytes["stock_retained_vector_table"]
            + status_bytes["stock_retained_alignment_nop"]
            + status_bytes["stock_retained_post_text_tables_data"]
        ),
        "unresolved_code_or_mixed_bytes": status_bytes[
            "stock_retained_unresolved_code_or_mixed"
        ],
        "largest_unresolved_segments": sorted(
            unresolved,
            key=lambda item: (-item["size"], item["start"]),
        )[:32],
        "segments": segments,
    }


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--batch-output", type=Path, required=True)
    parser.add_argument("--enforced-output", type=Path, required=True)
    parser.add_argument("--round2-output", type=Path, required=True)
    parser.add_argument("--round1-min8-output", type=Path, required=True)
    parser.add_argument("--round2-min8-output", type=Path, required=True)
    parser.add_argument("--application-objdump", type=Path, required=True)
    parser.add_argument("--image", type=Path, default=discovery.DEFAULT_IMAGE)
    parser.add_argument("--json", action="store_true")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    report = analyze(
        args.batch_output,
        args.enforced_output,
        args.round2_output,
        args.round1_min8_output,
        args.round2_min8_output,
        args.application_objdump,
        image=args.image,
    )
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print("EM9305 residual segment census: PASS")
        print(json.dumps(
            {key: value for key, value in report.items() if key not in {"segments", "largest_unresolved_segments"}},
            sort_keys=True,
        ))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
