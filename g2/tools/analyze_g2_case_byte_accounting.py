#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Sub-classify the charging-case 40,866-byte typed_external_or_unsupported bucket.

`g2-case-final-classification.md` proves the whole-blob split (32 generated
wrapper + 14,886 admitted-function candidate source + 40,866
`typed_external_or_unsupported`) but does not further divide the 40,866
bucket. `g2-box-stm32g0-platform-recovery.md` separately names 1,202 bytes of
it as evidence-anchored upstream/first-party islands and leaves a 54,550-byte
lump ("bulk kernel body, HAL drivers, policy, rodata, log corpus") that
predates the final-frontier function map and therefore double-counts bytes
the frontier later closed.

This analyzer reconciles both records against the pinned stock oracle and
produces one authoritative, non-overlapping accounting of every byte in
`0x08000000..0x0800D9C8`:

  1. `admitted_function_source_candidate` (14,886 B) -- excluded from the
     40,866 total; cross-checked against the final-frontier corpus only.
  2. Within the 40,866-byte remainder, in priority order:
     a. `gap_frontier_<classification>` -- the 229 inter-function spans
        `g2-case-final-classification.py` already typed (2,184 B).
     b. `platform_<ownership_category>` -- the evidence-anchored islands
        `analyze_g2_box_stm32g0_platform.py` names (upstream CMSIS/FreeRTOS/
        STM32-HAL islands, first-party G2 islands).
     c. Bytes covered by neither record are sub-typed by content alone:
        `residual_zero_fill` / `residual_ff_fill` (unambiguous flash-erase or
        zero padding runs >= 4 bytes), `residual_log_string_candidate`
        (printable ASCII runs >= 6 bytes, the compressed-log string corpus),
        and `residual_unresolved_code_or_data` (everything else: still
        opaque, still requires a full function map to close).

This is accounting only. No bytes leave "opaque" status by being named here;
naming is a precondition for routing reviewed source at those addresses, not
a substitute for it. No hardware operation is used or implied.

Run:
    PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 \\
        tools/analyze_g2_case_byte_accounting.py [--write-manifests]

Test:
    PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 \\
        -m unittest tests.test_analyze_g2_case_byte_accounting -v
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOLS_DIR = Path(__file__).resolve().parent
MANIFEST_DIR = ROOT / "tools/manifests"
BLOB = ROOT / "blobs/official/g2-2.2.6.10/firmware_box.bin"
CORPUS = ROOT / "research/corpus/case/ghidra/final-frontier/functions.jsonl"
GAP_FRONTIER = MANIFEST_DIR / "g2-case-final-gap-frontier.tsv"

BLOB_SHA256 = "36ca0c13558f252af286ae2b36b5e576d087d21d37b15d778e7da9f502a70374"
APP_BASE = 0x08000000
WRAPPER = 32
APP_BYTES = 55752
CORPUS_SHA256 = "03474766c2bef410d520dbd71fe6a0b8565ef1b117168e1639cc8ab4700773ed"

FRONTIER_FUNCTION_BYTES = 14886
FRONTIER_GAP_BYTES = 2184
TYPED_EXTERNAL_OR_UNSUPPORTED_BYTES = 40866

ZERO_RUN_MIN = 4
FF_RUN_MIN = 4
STRING_RUN_MIN = 6


class AuditError(RuntimeError):
    pass


def require(condition, message):
    if not condition:
        raise AuditError(message)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _load_platform_module():
    """Import the sibling platform-attribution analyzer by path.

    Reused (not reimplemented) so the island list has one source of truth;
    importing runs no analysis and has no side effects (guarded by
    `if __name__ == "__main__":`).
    """
    spec = importlib.util.spec_from_file_location(
        "analyze_g2_box_stm32g0_platform",
        TOOLS_DIR / "analyze_g2_box_stm32g0_platform.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _read_tsv(path):
    with path.open(newline="") as handle:
        return list(csv.DictReader(
            (line for line in handle if not line.startswith("#")),
            delimiter="\t"))


def _load_function_spans():
    spans = []
    with CORPUS.open(encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            record = json.loads(line)
            start = record["address"] - APP_BASE
            end = start + record["size"]
            spans.append((start, end))
    return spans


def _load_gap_spans():
    spans = []
    for row in _read_tsv(GAP_FRONTIER):
        start = int(row["start"], 16) - APP_BASE
        end = int(row["end_exclusive"], 16) - APP_BASE
        spans.append((start, end, row["classification"]))
    return spans


def _load_platform_islands(platform, blob):
    islands = []
    for region in platform._regions(blob):
        if region["file_start"] is None:
            continue  # aggregate "unresolved" lump or a preserved SN window
        start = region["file_start"] - WRAPPER
        end = region["file_end_exclusive"] - WRAPPER
        if end <= 0 or start >= APP_BYTES:
            continue  # wrapper-only region (generated_transport), out of range
        islands.append((max(start, 0), min(end, APP_BYTES),
                        region["ownership_category"], region["evidence"]))
    return islands


def _mark(cover, spans, tag=None):
    """Tag every byte in each (start, end[, per_span_tag]) span.

    Fails closed if a span overlaps one already tagged. Pass a fixed `tag`
    for uniformly-tagged spans, or 3-tuples carrying a per-span tag.
    """
    for start, end, *rest in spans:
        span_tag = rest[0] if rest else tag
        for index in range(start, end):
            require(cover[index] is None,
                    f"byte {APP_BASE + index:#010x} already tagged "
                    f"{cover[index]!r} before {span_tag!r}")
            cover[index] = span_tag


def _sub_type_residual(app: bytes, cover: list, tag_prefix: str):
    """Content-only sub-typing of every still-untagged byte."""
    index = 0
    n = len(app)
    while index < n:
        if cover[index] is not None:
            index += 1
            continue
        byte = app[index]
        if byte == 0x00:
            end = index
            while end < n and cover[end] is None and app[end] == 0x00:
                end += 1
            if end - index >= ZERO_RUN_MIN:
                for i in range(index, end):
                    cover[i] = f"{tag_prefix}zero_fill"
                index = end
                continue
        elif byte == 0xFF:
            end = index
            while end < n and cover[end] is None and app[end] == 0xFF:
                end += 1
            if end - index >= FF_RUN_MIN:
                for i in range(index, end):
                    cover[i] = f"{tag_prefix}ff_fill"
                index = end
                continue
        elif 0x20 <= byte < 0x7F:
            end = index
            while end < n and cover[end] is None and 0x20 <= app[end] < 0x7F:
                end += 1
            if end - index >= STRING_RUN_MIN:
                for i in range(index, end):
                    cover[i] = f"{tag_prefix}log_string_candidate"
                index = end
                continue
        cover[index] = f"{tag_prefix}unresolved_code_or_data"
        index += 1


def _collapse(cover: list, app: bytes):
    rows = []
    index = 0
    n = len(cover)
    while index < n:
        tag = cover[index]
        end = index
        while end < n and cover[end] == tag:
            end += 1
        rows.append({
            "start": APP_BASE + index, "end": APP_BASE + end,
            "bytes": end - index, "category": tag,
            "content_sha256": sha256(app[index:end]),
        })
        index = end
    return rows


def analyze():
    platform = _load_platform_module()
    blob = BLOB.read_bytes()
    require(sha256(blob) == BLOB_SHA256, "case blob identity changed")
    app = blob[WRAPPER:]
    require(len(app) == APP_BYTES, "case application size changed")
    require(sha256(CORPUS.read_bytes()) == CORPUS_SHA256,
            "case final-frontier corpus identity changed")

    function_spans = _load_function_spans()
    require(len(function_spans) == 222 and
            sum(e - s for s, e in function_spans) == FRONTIER_FUNCTION_BYTES,
            "admitted function baseline changed")

    gap_spans = _load_gap_spans()
    require(len(gap_spans) == 229 and
            sum(e - s for s, e, _ in gap_spans) == FRONTIER_GAP_BYTES,
            "gap-frontier baseline changed")

    islands = _load_platform_islands(platform, blob)

    # Priority order: admitted functions (Ghidra-authenticated bodies with
    # reviewed clean-room source, the strongest evidence) first, then the
    # evidence-anchored platform islands (named by instruction-level match),
    # then the generic inter-function gap typing (weakest evidence:
    # "outside every discovered body", no positive identification). The
    # platform-island and gap-frontier records predate the final-frontier
    # function map and were produced independently, so all three overlap in
    # places; evidence strength breaks every tie by only claiming bytes the
    # stronger source left untagged (soft-mark, not `_mark`'s hard overlap
    # failure, which stays reserved for genuine same-priority conflicts).
    cover = [None] * APP_BYTES
    _mark(cover, function_spans, "admitted_function_source_candidate")
    admitted_bytes = sum(1 for tag in cover if tag is not None)
    require(admitted_bytes == FRONTIER_FUNCTION_BYTES,
            "admitted-function coverage changed")

    for start, end, category, _evidence in islands:
        for index in range(start, end):
            if cover[index] is None:
                cover[index] = f"platform_{category}"
    for start, end, classification in gap_spans:
        for index in range(start, end):
            if cover[index] is None:
                cover[index] = f"gap_frontier_{classification}"

    pre_residual_typed = sum(
        1 for tag in cover
        if tag is not None and tag != "admitted_function_source_candidate")

    _sub_type_residual(app, cover, "residual_")

    typed_external_bytes = sum(
        1 for tag in cover if tag != "admitted_function_source_candidate")
    require(typed_external_bytes == TYPED_EXTERNAL_OR_UNSUPPORTED_BYTES,
            "typed_external_or_unsupported total changed")

    rows = _collapse(cover, app)
    require(sum(r["bytes"] for r in rows) == APP_BYTES,
            "accounting does not conserve the application byte count")

    bucket_bytes = {}
    for row in rows:
        bucket_bytes[row["category"]] = bucket_bytes.get(row["category"], 0) + row["bytes"]

    island_evidence: dict[str, list[str]] = {}
    for _, _, category, evidence in islands:
        island_evidence.setdefault(f"platform_{category}", []).append(evidence)

    return {
        "schema_version": 1,
        "component": "G2 charging-case typed_external_or_unsupported byte accounting",
        "app_base": APP_BASE, "app_bytes": APP_BYTES,
        "rows": rows,
        "bucket_bytes": bucket_bytes,
        "island_evidence": island_evidence,
        "metrics": {
            "admitted_function_source_candidate_bytes": admitted_bytes,
            "typed_external_or_unsupported_bytes": typed_external_bytes,
            "pre_residual_typed_bytes": pre_residual_typed,
            "residual_bytes": typed_external_bytes - pre_residual_typed,
            "residual_zero_fill_bytes": bucket_bytes.get("residual_zero_fill", 0),
            "residual_ff_fill_bytes": bucket_bytes.get("residual_ff_fill", 0),
            "residual_log_string_candidate_bytes":
                bucket_bytes.get("residual_log_string_candidate", 0),
            "residual_unresolved_code_or_data_bytes":
                bucket_bytes.get("residual_unresolved_code_or_data", 0),
            "gap_frontier_bytes": sum(v for k, v in bucket_bytes.items()
                                       if k.startswith("gap_frontier_")),
            "platform_attributed_bytes": sum(v for k, v in bucket_bytes.items()
                                             if k.startswith("platform_")),
            "row_count": len(rows),
        },
        "identity_windows_in_range": {
            "count": 0,
            "note": ("The case OTA updater's preserved SN identity windows "
                     "(0x0803F000..0x0803F00F, 0x0803F800..0x0803F807, "
                     "and the bank-2 mirrors at 0x0807Fxxx) are proven by "
                     "g2-box-stm32g0-platform-recovery.md to lie far beyond "
                     "this 55,752-byte application image "
                     "(image_contains_preserved_windows: false). Zero "
                     "identity-window bytes exist inside "
                     "0x08000000..0x0800D9C8; there is nothing to "
                     "reconstruct or divergence-document for identity "
                     "windows within this range."),
        },
        "hardware_validation": "blocked by unavailable physical evidence",
        "hardware_operations": [],
        "production_routed": False,
        "note": ("Naming a byte range here is a precondition for routing "
                 "reviewed source at those addresses, not source ownership "
                 "itself. residual_unresolved_code_or_data remains opaque "
                 "and needs a full Ghidra function map (recommended next "
                 "action in g2-box-stm32g0-platform-recovery.md) before it "
                 "can be reduced further."),
    }


def write_manifests(result):
    rows_path = MANIFEST_DIR / "g2-case-byte-accounting.tsv"
    with rows_path.open("w", newline="") as handle:
        writer = csv.writer(handle, delimiter="\t", lineterminator="\n")
        writer.writerow(["# SPDX-License-Identifier: MIT"])
        writer.writerow(["start", "end_exclusive", "bytes", "category", "content_sha256"])
        for row in result["rows"]:
            writer.writerow([f"0x{row['start']:08X}", f"0x{row['end']:08X}",
                             row["bytes"], row["category"], row["content_sha256"]])
    summary_path = MANIFEST_DIR / "g2-case-byte-accounting-summary.json"
    slim = {k: v for k, v in result.items() if k != "rows"}
    slim["row_count"] = len(result["rows"])
    summary_path.write_text(json.dumps(slim, indent=2, sort_keys=True) + "\n")
    return [rows_path, summary_path]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-manifests", action="store_true")
    args = parser.parse_args()
    result = analyze()
    if args.write_manifests:
        for path in write_manifests(result):
            print(f"wrote {path.relative_to(ROOT)}")
    print(json.dumps(result["metrics"], sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AuditError as exc:
        raise SystemExit(f"Case byte accounting failed: {exc}") from exc
