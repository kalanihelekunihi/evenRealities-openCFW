#!/usr/bin/env python3
"""Boundary-role and oversized-envelope region audit for Apollo-main.

This analyzer closes two follow-up frontiers of the unanchored-function
provenance census (``docs/research/g2-apollo-unanchored-census.md``):

1. **Mixed-evidence boundary objects** -- the census's
   ``investigation-required-mixed`` bucket (38 functions, 9,032 official
   opaque bytes).  These functions call into more than one provider family;
   they are the adapter seams the ownership model expects to be mixed.  For
   each function this audit enumerates the closed-world call edges in both
   directions, cross-checks the spanned family set against the census record
   (fail closed on any drift), and assigns a declared boundary role from a
   closed role table keyed by the seam family pair.
2. **Oversized envelopes** -- the eight Ghidra envelopes rejected by the
   origin accounting's 16,384-byte trust cap.  Each envelope span is
   partitioned byte-exactly into the bytes already covered by accepted
   (trustworthy) corpus envelopes and the interstitial remainder, which is
   classified by deterministic structural rules (pointer/jump tables,
   Thumb code candidates, ASCII strings, zero fill, opaque blobs, rodata
   tables, mixed code+data, alignment gaps).  Classification is region
   triage, not source ownership; ambiguous regions stay
   ``mixed-code-data`` or low-confidence data classes.

The analyzer is read-only and deterministic.  It re-derives everything from
the authenticated official image, the authenticated 64-shard Ghidra corpus,
and the checked-in manifests on every run, re-running the unanchored census
itself so its frontier sets cannot drift from the census, and raises
``BoundaryError`` on any drift from the pinned constants below.
"""

from __future__ import annotations

import argparse
import csv
import importlib.util
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
CENSUS_ANALYZER = ROOT / "tools/analyze_g2_apollo_unanchored_census.py"
MANIFESTS = ROOT / "tools/manifests"
CENSUS_FUNCTIONS_TSV = MANIFESTS / "g2-apollo-unanchored-census-functions.tsv"

EXPECTED_MIXED_FUNCTION_COUNT = 38
EXPECTED_MIXED_ENVELOPE_BYTES = 9_380
EXPECTED_MIXED_OFFICIAL_BYTES = 9_032
EXPECTED_OVERSIZED_ENVELOPE_COUNT = 8

# Pinned seam census of the mixed bucket (family pair -> functions).
EXPECTED_SEAM_CENSUS = {
    "first-party|lvgl": 20,
    "ambiqsuite|cordio": 7,
    "first-party|nanopb": 5,
    "cmsis-freertos|first-party": 2,
    "first-party|littlefs": 2,
    "cmsis-freertos|nanopb": 1,
    "cordio|first-party": 1,
}

# Closed boundary-role table.  Every seam pair present in the census's mixed
# bucket must map to exactly one declared boundary role; an unknown seam
# fails closed.  Roles are boundary declarations (which families meet and
# which direction adaptation flows), never source-ownership claims.
BOUNDARY_ROLES: dict[tuple[str, ...], dict[str, str]] = {
    ("first-party", "lvgl"): {
        "role": "g2-lvgl-ui-adapter",
        "label": "first-party UI adapter over the LVGL vendor fork",
        "flow": "first-party UI code calling LVGL vendor-fork services",
    },
    ("ambiqsuite", "cordio"): {
        "role": "ambiq-cordio-port-shim",
        "label": "AmbiqSuite proprietary port shim around the Cordio host",
        "flow": "Cordio host calling AmbiqSuite port services and vice versa",
    },
    ("first-party", "nanopb"): {
        "role": "g2-nanopb-schema-glue",
        "label": "first-party protobuf schema glue over the nanopb runtime",
        "flow": "first-party message code calling nanopb runtime primitives",
    },
    ("cmsis-freertos", "nanopb"): {
        "role": "g2-nanopb-rtos-glue",
        "label": "nanopb schema glue adjacent to the CMSIS-FreeRTOS wrapper",
        "flow": "RTOS-wrapper-adjacent glue calling nanopb runtime primitives",
    },
    ("first-party", "littlefs"): {
        "role": "g2-littlefs-volume-glue",
        "label": "first-party filesystem glue over littlefs",
        "flow": "first-party storage code calling littlefs volume primitives",
    },
    ("cmsis-freertos", "first-party"): {
        "role": "g2-rtos-service-glue",
        "label": "first-party glue over the CMSIS-FreeRTOS os2 wrapper",
        "flow": "first-party service code calling CMSIS-FreeRTOS wrapper entries",
    },
    ("cordio", "first-party"): {
        "role": "g2-cordio-application-callback",
        "label": "first-party application callback into the Cordio host",
        "flow": "AmbiqSuite/Cordio-invoked application code calling Cordio and first-party services",
    },
}

# Region classes for the oversized-envelope interstitial partition.
# ``accepted-function-code`` is coverage by trustworthy corpus envelopes;
# every other class describes bytes no accepted envelope claims.
REGION_CLASSES = (
    "accepted-function-code",
    "thumb-code-candidate",
    "mixed-code-data",
    "thumb-jump-table",
    "pointer-table",
    "ascii-strings",
    "zero-fill",
    "opaque-blob",
    "rodata-table",
    "alignment-gap",
)

# Structural classification thresholds, calibrated against known accepted
# envelopes (Thumb code: >= 9.7 validated BLs per KB) and the asset tail
# beyond the last discovered function (<= 0.5 BLs per KB).
POINTER_RUN_MIN_WORDS = 3
BL_DENSE_PER_KB = 10.0
BL_PRESENT_PER_KB = 4.0
CODE_MIN_BYTES = 256
ASCII_STRINGS_RATIO = 0.8
ZERO_FILL_RATIO = 0.9
OPAQUE_BLOB_MIN_DISTINCT_BYTES = 128
GAP_MAX_BYTES = 16

# Pinned per-envelope interstitial/accepted byte partition.  Derived from the
# authenticated image and corpus; any drift raises ``BoundaryError``.
EXPECTED_ENVELOPE_REGIONS: dict[int, dict[str, Any]] = {
    0x0047CC60: {
        "body_start": 0x0047CC60,
        "body_end_exclusive": 0x004D2B9A,
        "classes": {
            "accepted-function-code": 264458,
            "alignment-gap": 1560,
            "ascii-strings": 96,
            "pointer-table": 18232,
            "rodata-table": 1428,
            "thumb-code-candidate": 65788,
            "thumb-jump-table": 496,
        },
    },
    0x0048949C: {
        "body_start": 0x0048949C,
        "body_end_exclusive": 0x004D558E,
        "classes": {
            "accepted-function-code": 230772,
            "alignment-gap": 1426,
            "ascii-strings": 78,
            "pointer-table": 17140,
            "rodata-table": 1014,
            "thumb-code-candidate": 60796,
            "thumb-jump-table": 312,
        },
    },
    0x00509708: {
        "body_start": 0x00509708,
        "body_end_exclusive": 0x0055EA06,
        "classes": {
            "accepted-function-code": 262730,
            "alignment-gap": 1686,
            "pointer-table": 14424,
            "rodata-table": 2572,
            "thumb-code-candidate": 67198,
            "thumb-jump-table": 316,
        },
    },
    0x00513E2E: {
        "body_start": 0x00513E2E,
        "body_end_exclusive": 0x0052296A,
        "classes": {
            "accepted-function-code": 59446,
            "alignment-gap": 156,
            "pointer-table": 76,
            "rodata-table": 512,
            "thumb-code-candidate": 30,
        },
    },
    0x00514F3C: {
        "body_start": 0x00514F3C,
        "body_end_exclusive": 0x00563954,
        "classes": {
            "accepted-function-code": 238236,
            "alignment-gap": 1518,
            "mixed-code-data": 4284,
            "pointer-table": 12344,
            "rodata-table": 2796,
            "thumb-code-candidate": 62578,
            "thumb-jump-table": 316,
        },
    },
    0x00541B74: {
        "body_start": 0x00541B74,
        "body_end_exclusive": 0x00585130,
        "classes": {
            "accepted-function-code": 179648,
            "alignment-gap": 1166,
            "mixed-code-data": 4284,
            "pointer-table": 14836,
            "rodata-table": 3120,
            "thumb-code-candidate": 72410,
            "thumb-jump-table": 436,
        },
    },
    0x0055F994: {
        "body_start": 0x0055F994,
        "body_end_exclusive": 0x0058EAC2,
        "classes": {
            "accepted-function-code": 135916,
            "alignment-gap": 766,
            "mixed-code-data": 4284,
            "pointer-table": 10920,
            "rodata-table": 2202,
            "thumb-code-candidate": 38394,
            "thumb-jump-table": 332,
        },
    },
    0x005FA120: {
        "body_start": 0x00442134,
        "body_end_exclusive": 0x005FA132,
        "classes": {
            "accepted-function-code": 1322324,
            "alignment-gap": 7370,
            "ascii-strings": 196,
            "mixed-code-data": 8466,
            "pointer-table": 83428,
            "rodata-table": 11966,
            "thumb-code-candidate": 366436,
            "thumb-jump-table": 2052,
        },
    },
}

CALL_TARGET_RE = re.compile(r"\bFUN_([0-9a-f]{8})\s*\(", re.IGNORECASE)


class BoundaryError(RuntimeError):
    """Raised when authenticated evidence or a closed census changes."""


def _load_census_analyzer():
    spec = importlib.util.spec_from_file_location(
        "apollo_unanchored_census_for_boundary", CENSUS_ANALYZER
    )
    if spec is None or spec.loader is None:
        raise BoundaryError(f"cannot load {CENSUS_ANALYZER}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def boundary_role(seam_families: tuple[str, ...]) -> dict[str, str]:
    """Declared boundary role for a seam family pair; fails closed."""

    role = BOUNDARY_ROLES.get(tuple(sorted(seam_families)))
    if role is None:
        raise BoundaryError(f"no declared boundary role for seam {seam_families!r}")
    return role


def validate_seam_census(actual: dict[str, int]) -> None:
    if actual != EXPECTED_SEAM_CENSUS:
        raise BoundaryError(
            f"mixed-bucket seam census changed: {actual!r} != {EXPECTED_SEAM_CENSUS!r}"
        )


def parse_corpus_call_edges(logs: list[Path], census_module) -> dict[int, set[int]]:
    """Direct call edges: caller entry -> set of callee entries.

    The decompiled corpus names every call target ``FUN_<address>(...)``; a
    target without the call parenthesis is a data reference and is ignored.
    """

    edges: dict[int, set[int]] = defaultdict(set)
    current: int | None = None
    for log in logs:
        for line in log.read_text(encoding="utf-8", errors="strict").splitlines():
            begin = census_module.FUNCTION_BEGIN_RE.search(line)
            if begin:
                current = int(begin.group(1), 16)
                continue
            if census_module.FUNCTION_END_RE.search(line):
                current = None
                continue
            if current is not None:
                for match in CALL_TARGET_RE.finditer(line):
                    edges[current].add(int(match.group(1), 16))
    if current is not None:
        raise BoundaryError("unterminated Ghidra function at end of corpus")
    return edges


def build_seed_labels(census_module, corpus_root: Path) -> dict[int, str]:
    """Rebuild the census's closed-world seed labels with its own helpers.

    Mirrors the census seed construction exactly: path anchors, function-map
    manifests, curated documented evidence, liblc3 public entries, and IAR
    DLIB string-signature functions.  The span cross-check against the census
    records in ``analyze`` proves the replica cannot drift silently.
    """

    path_module = census_module._load_path_analyzer()
    path_report = path_module.analyze(corpus_root=corpus_root)
    anchored = {row["entry"]: row for row in path_report["ghidra_correlation"]["functions"]}
    logs = path_module.verify_corpus(corpus_root)
    functions = census_module.parse_corpus_functions(logs)

    manifest_labels: dict[int, str] = {}
    for address, (family, _stem) in sorted(
        census_module.load_manifest_function_maps().items()
    ):
        target = address if address in functions else None
        if target is None:
            for entry, row in functions.items():
                if row["body_start"] <= address <= row["body_end_inclusive"]:
                    target = entry
                    break
        if target is not None:
            manifest_labels.setdefault(target, family)

    documented: dict[int, str] = {}
    for address in sorted(census_module.load_liblc3_entries()):
        if address in functions:
            documented[address] = "liblc3"
    for evidence in census_module.DOCUMENTED_FAMILY_EVIDENCE:
        if evidence["kind"] == "span":
            for entry in functions:
                if evidence["start"] <= entry < evidence["end_exclusive"]:
                    documented.setdefault(entry, evidence["family"])
        else:
            for address in evidence["entries"]:
                if address in functions:
                    documented.setdefault(address, evidence["family"])

    blob = path_module.DEFAULT_IMAGE.read_bytes()
    dlib_targets = census_module.dlib_signature_targets(blob, path_module.LOAD_BASE)
    oversized = {
        entry
        for entry, row in functions.items()
        if row["body_end_inclusive"] - row["body_start"] + 1
        > census_module.MAX_TRUSTWORTHY_FUNCTION_ENVELOPE
    }
    dlib_functions = {
        entry
        for entry, row in functions.items()
        if entry not in anchored
        and entry not in oversized
        and row["tokens"] & dlib_targets
    }

    seed: dict[int, str] = {}
    for entry, row in anchored.items():
        dependencies = row.get("third_party_dependencies") or []
        seed[entry] = (
            census_module.ANCHOR_FAMILY[dependencies[0]] if dependencies else "first-party"
        )
    for entry, family in manifest_labels.items():
        seed.setdefault(entry, family)
    for entry, family in documented.items():
        seed.setdefault(entry, family)
    for entry in dlib_functions:
        seed[entry] = "iar-dlib"
    return seed


def _is_pointer_word(word: int, load_base: int, image_end: int) -> bool:
    return (
        load_base <= word < image_end
        or load_base <= (word & ~1) < image_end
        or 0x2000_0000 <= word < 0x2008_0000
        or 0x4000_0000 <= word < 0x6000_0000
    )


def thumb_bl_targets(data: bytes, region_start: int, load_base: int, image_end: int) -> list[int]:
    """In-image Thumb-2 ``BL`` instruction offsets inside ``data``.

    A 32-bit ``BL`` whose sign-extended target lands inside the loaded image
    at an even address is strong structural code evidence; data almost never
    reproduces both the encoding and the in-range target.
    """

    positions: list[int] = []
    size = len(data)
    index = 0
    while index + 3 < size:
        half = data[index] | (data[index + 1] << 8)
        if (half & 0xF800) == 0xF000:
            second = data[index + 2] | (data[index + 3] << 8)
            if (second & 0xD000) == 0xD000:
                sign = (half >> 10) & 1
                imm10 = half & 0x3FF
                j1 = (second >> 13) & 1
                j2 = (second >> 11) & 1
                offset = (
                    (sign << 24)
                    | ((j1 ^ sign ^ 1) << 23)
                    | ((j2 ^ sign ^ 1) << 22)
                    | (imm10 << 12)
                    | ((second & 0x7FF) << 1)
                )
                if sign:
                    offset -= 1 << 25
                target = region_start + index + 4 + offset
                if load_base <= target < image_end and target % 2 == 0:
                    positions.append(region_start + index)
                index += 4
                continue
        index += 2
    return positions


def classify_piece(
    blob: bytes, start: int, end: int, load_base: int, image_end: int
) -> tuple[str, str]:
    """Classify one interstitial piece (pointer runs already carved out)."""

    size = end - start
    if size < GAP_MAX_BYTES:
        return "alignment-gap", "low"
    data = blob[start - load_base : end - load_base]
    if data.count(0) / size >= ZERO_FILL_RATIO:
        return "zero-fill", "high"
    printable = sum(1 for value in data if 0x20 <= value < 0x7F)
    if printable / size >= ASCII_STRINGS_RATIO:
        return "ascii-strings", "high"
    bl_positions = thumb_bl_targets(data, start, load_base, image_end)
    bl_per_kb = len(bl_positions) / size * 1024
    if bl_per_kb >= BL_DENSE_PER_KB and size >= CODE_MIN_BYTES:
        return "thumb-code-candidate", "high"
    if bl_per_kb >= BL_PRESENT_PER_KB:
        return "thumb-code-candidate", "medium"
    if bl_positions:
        return "mixed-code-data", "medium"
    if len(set(data)) >= OPAQUE_BLOB_MIN_DISTINCT_BYTES:
        return "opaque-blob", "medium"
    return "rodata-table", "low"


def classify_span(
    blob: bytes,
    start: int,
    end: int,
    accepted: list[tuple[int, int]],
    load_base: int,
    image_end: int,
) -> list[tuple[int, int, str, str]]:
    """Partition ``[start, end)`` into (start, end, class, confidence) rows.

    Accepted corpus envelopes claim their covered bytes first; every
    remaining byte falls into exactly one interstitial class.
    """

    rows: list[tuple[int, int, str, str]] = []
    interstitial: list[tuple[int, int]] = []
    cursor = start
    for acc_start, acc_end in accepted:
        if acc_end <= start or acc_start >= end:
            continue
        piece_start = max(acc_start, start)
        piece_end = min(acc_end, end)
        if piece_start > cursor:
            interstitial.append((cursor, piece_start))
        if piece_end > cursor:
            rows.append((max(piece_start, cursor), piece_end, "accepted-function-code", "high"))
            cursor = piece_end
    if cursor < end:
        interstitial.append((cursor, end))

    for seg_start, seg_end in interstitial:
        if seg_end - seg_start < 4:
            rows.append((seg_start, seg_end, "alignment-gap", "low"))
            continue
        # Carve maximal runs of >= POINTER_RUN_MIN_WORDS consecutive aligned
        # pointer words (literal pools, data pointer tables, jump tables).
        aligned_start = seg_start & ~3
        if aligned_start < seg_start:
            aligned_start += 4
        aligned_end = seg_end - ((seg_end - aligned_start) % 4)
        carved: list[tuple[int, int]] = []
        run_begin: int | None = None
        cursor = aligned_start
        while cursor < aligned_end:
            word = int.from_bytes(blob[cursor - load_base : cursor - load_base + 4], "little")
            if _is_pointer_word(word, load_base, image_end):
                if run_begin is None:
                    run_begin = cursor
            else:
                if run_begin is not None:
                    if cursor - run_begin >= POINTER_RUN_MIN_WORDS * 4:
                        carved.append((run_begin, cursor))
                    run_begin = None
            cursor += 4
        if run_begin is not None and aligned_end - run_begin >= POINTER_RUN_MIN_WORDS * 4:
            carved.append((run_begin, aligned_end))
        pieces: list[tuple[int, int, bool]] = []
        cursor = seg_start
        for run_start, run_end in carved:
            if run_start > cursor:
                pieces.append((cursor, run_start, False))
            pieces.append((run_start, run_end, True))
            cursor = run_end
        if cursor < seg_end:
            pieces.append((cursor, seg_end, False))
        for piece_start, piece_end, is_table in pieces:
            if is_table:
                total = (piece_end - piece_start) // 4
                odd = sum(
                    1
                    for word_at in range(piece_start, piece_end, 4)
                    if int.from_bytes(
                        blob[word_at - load_base : word_at - load_base + 4], "little"
                    )
                    & 1
                )
                region_class = "thumb-jump-table" if total and odd * 2 >= total else "pointer-table"
                rows.append((piece_start, piece_end, region_class, "medium"))
            elif piece_end - piece_start >= 4:
                region_class, confidence = classify_piece(
                    blob, piece_start, piece_end, load_base, image_end
                )
                rows.append((piece_start, piece_end, region_class, confidence))
            else:
                rows.append((piece_start, piece_end, "alignment-gap", "low"))
    return rows


def _load_census_tsv_buckets(path: Path) -> dict[str, set[int]]:
    """Entries per bucket from the checked-in census functions manifest."""

    if not path.is_file():
        raise BoundaryError(f"missing census functions manifest: {path.name}")
    lines = [
        line
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.startswith("#")
    ]
    reader = csv.DictReader(lines, delimiter="\t")
    columns = reader.fieldnames or ()
    if "entry" not in columns or "bucket" not in columns:
        raise BoundaryError(f"unknown census functions schema: {columns!r}")
    buckets: dict[str, set[int]] = defaultdict(set)
    for row in reader:
        try:
            entry = int((row.get("entry") or "").strip(), 16)
        except ValueError:
            continue
        buckets[(row.get("bucket") or "").strip()].add(entry)
    return buckets


def validate_envelope_partition(
    entry: int,
    body_start: int,
    body_end_exclusive: int,
    classes: dict[str, int],
) -> None:
    """Fail-closed check of one oversized envelope's byte partition."""

    expected = EXPECTED_ENVELOPE_REGIONS.get(entry)
    if expected is None:
        raise BoundaryError(f"oversized envelope 0x{entry:08X} has no pinned region map")
    if (
        body_start != expected["body_start"]
        or body_end_exclusive != expected["body_end_exclusive"]
    ):
        raise BoundaryError(f"oversized envelope 0x{entry:08X} span drifted")
    if any(name not in REGION_CLASSES for name in classes):
        raise BoundaryError(f"oversized envelope 0x{entry:08X} has an unknown region class")
    if sum(classes.values()) != body_end_exclusive - body_start:
        raise BoundaryError(
            f"oversized envelope 0x{entry:08X} partition is not byte-exact"
        )
    if dict(sorted(classes.items())) != expected["classes"]:
        raise BoundaryError(
            f"oversized envelope 0x{entry:08X} region partition changed: "
            f"{dict(sorted(classes.items()))!r} != {expected['classes']!r}"
        )


def analyze(
    corpus_root: Path,
    manifests_dir: Path = MANIFESTS,
) -> dict[str, Any]:
    census_module = _load_census_analyzer()
    census_report = census_module.analyze(corpus_root)

    mixed_records = [
        record
        for record in census_report["functions"]
        if record["bucket"] == "investigation-required-mixed"
    ]
    oversized_records = [
        record
        for record in census_report["functions"]
        if record["bucket"] == "rejected-oversized-envelope"
    ]
    if len(mixed_records) != EXPECTED_MIXED_FUNCTION_COUNT:
        raise BoundaryError(
            f"mixed-boundary census changed: {len(mixed_records)} != "
            f"{EXPECTED_MIXED_FUNCTION_COUNT}"
        )
    if len(oversized_records) != EXPECTED_OVERSIZED_ENVELOPE_COUNT:
        raise BoundaryError(
            f"oversized-envelope census changed: {len(oversized_records)} != "
            f"{EXPECTED_OVERSIZED_ENVELOPE_COUNT}"
        )
    mixed_envelope_bytes = sum(record["envelope_bytes"] for record in mixed_records)
    mixed_official_bytes = sum(record["official_opaque_bytes"] for record in mixed_records)
    if mixed_envelope_bytes != EXPECTED_MIXED_ENVELOPE_BYTES:
        raise BoundaryError(
            f"mixed-bucket envelope bytes changed: {mixed_envelope_bytes} != "
            f"{EXPECTED_MIXED_ENVELOPE_BYTES}"
        )
    if mixed_official_bytes != EXPECTED_MIXED_OFFICIAL_BYTES:
        raise BoundaryError(
            f"mixed-bucket official bytes changed: {mixed_official_bytes} != "
            f"{EXPECTED_MIXED_OFFICIAL_BYTES}"
        )

    # Cross-check the re-derived frontier sets against the checked-in census
    # manifest so a stale or regenerated-but-different census fails closed.
    tsv_buckets = _load_census_tsv_buckets(manifests_dir / CENSUS_FUNCTIONS_TSV.name)
    if tsv_buckets.get("investigation-required-mixed", set()) != {
        record["entry"] for record in mixed_records
    }:
        raise BoundaryError("checked-in census manifest mixed set drifted")
    if tsv_buckets.get("rejected-oversized-envelope", set()) != {
        record["entry"] for record in oversized_records
    }:
        raise BoundaryError("checked-in census manifest oversized set drifted")

    path_module = census_module._load_path_analyzer()
    load_base = path_module.LOAD_BASE
    image_end = load_base + path_module.IMAGE_SIZE
    blob = path_module.DEFAULT_IMAGE.read_bytes()
    logs = path_module.verify_corpus(corpus_root)
    functions = census_module.parse_corpus_functions(logs)
    seed_labels = build_seed_labels(census_module, corpus_root)
    call_edges = parse_corpus_call_edges(logs, census_module)

    inbound: dict[int, set[int]] = defaultdict(set)
    for caller, callees in call_edges.items():
        for callee in callees:
            inbound[callee].add(caller)

    boundary_rows: list[dict[str, Any]] = []
    seam_census: Counter[str] = Counter()
    for record in mixed_records:
        entry = record["entry"]
        tokens = functions[entry]["tokens"]
        span_families = sorted({seed_labels[token] for token in tokens if token in seed_labels})
        census_detail = record["detail"].replace("call targets span ", "")
        if "|".join(span_families) != census_detail:
            raise BoundaryError(
                f"mixed function 0x{entry:08X} span drifted: "
                f"{'|'.join(span_families)} != {census_detail}"
            )
        out_edges = sorted(
            target for target in call_edges.get(entry, set()) if target in seed_labels
        )
        out_families = sorted({seed_labels[target] for target in out_edges})
        if out_families != span_families:
            raise BoundaryError(
                f"mixed function 0x{entry:08X} has a span family without a "
                f"direct call edge: span {span_families!r} calls {out_families!r}"
            )
        in_families = Counter(
            seed_labels[caller] for caller in inbound.get(entry, set()) if caller in seed_labels
        )
        role = boundary_role(tuple(span_families))
        confidence = "medium" if in_families else "low"
        seam = "|".join(span_families)
        seam_census[seam] += 1
        boundary_rows.append(
            {
                "entry": entry,
                "body_start": record["body_start"],
                "body_end_exclusive": record["body_end_exclusive"],
                "envelope_bytes": record["envelope_bytes"],
                "official_opaque_bytes": record["official_opaque_bytes"],
                "seam": seam,
                "boundary_role": role["role"],
                "role_label": role["label"],
                "adaptation_flow": role["flow"],
                "confidence": confidence,
                "outbound_edges": [
                    {"target": target, "family": seed_labels[target]}
                    for target in out_edges
                ],
                "inbound_seed_callers": dict(sorted(in_families.items())),
            }
        )
    validate_seam_census(dict(sorted(seam_census.items())))

    accepted = sorted(
        (row["body_start"], row["body_end_inclusive"] + 1)
        for entry, row in functions.items()
        if row["body_end_inclusive"] - row["body_start"] + 1
        <= census_module.MAX_TRUSTWORTHY_FUNCTION_ENVELOPE
    )
    envelope_rows: list[dict[str, Any]] = []
    for record in oversized_records:
        entry = record["entry"]
        rows = classify_span(
            blob,
            record["body_start"],
            record["body_end_exclusive"],
            accepted,
            load_base,
            image_end,
        )
        classes: Counter[str] = Counter()
        confidence_bytes: Counter[tuple[str, str]] = Counter()
        segments = 0
        for row_start, row_end, region_class, confidence in rows:
            classes[region_class] += row_end - row_start
            confidence_bytes[(region_class, confidence)] += row_end - row_start
            segments += 1
        validate_envelope_partition(
            entry,
            record["body_start"],
            record["body_end_exclusive"],
            dict(classes),
        )
        interstitial = {
            name: size for name, size in classes.items() if name != "accepted-function-code"
        }
        dominant = max(sorted(interstitial), key=lambda name: interstitial[name])
        # Byte-weighted majority confidence of the dominant interstitial
        # class; ties break alphabetically for determinism.
        dominant_confidence = max(
            sorted(
                confidence
                for (region_class, confidence) in confidence_bytes
                if region_class == dominant
            ),
            key=lambda confidence: confidence_bytes[(dominant, confidence)],
        )
        detail = (
            f"analyzer artifact: {100 * classes['accepted-function-code'] // record['envelope_bytes']}%"
            f" of span is accepted-envelope code; {segments} classified regions"
        )
        if entry == 0x005FA120:
            detail += "; entry sits near the end of its own body, which swallows the image head"
        envelope_rows.append(
            {
                "entry": entry,
                "body_start": record["body_start"],
                "body_end_exclusive": record["body_end_exclusive"],
                "span_bytes": record["envelope_bytes"],
                "accepted_function_code_bytes": classes["accepted-function-code"],
                "interstitial_bytes": record["envelope_bytes"]
                - classes["accepted-function-code"],
                "region_classes": dict(sorted(classes.items())),
                "dominant_interstitial_class": dominant,
                "confidence": dominant_confidence,
                "classified_regions": segments,
                "detail": detail,
            }
        )

    return {
        "schema_version": 1,
        "analysis_mode": "read-only; no signing, flashing, erase, or hardware operation",
        "target": "official G2 s200_v2.2.6.10 Apollo main",
        "inputs": {
            "image_sha256": census_report["inputs"]["image_sha256"],
            "ghidra_sha256sums_sha256": census_report["inputs"]["ghidra_sha256sums_sha256"],
            "flash_plan_sha256": census_report["inputs"]["flash_plan_sha256"],
            "census_functions_tsv": CENSUS_FUNCTIONS_TSV.name,
        },
        "reconciliation": {
            "mixed_functions": len(boundary_rows),
            "mixed_envelope_bytes": mixed_envelope_bytes,
            "mixed_official_opaque_bytes": mixed_official_bytes,
            "oversized_envelopes": len(envelope_rows),
            "seam_census": dict(sorted(seam_census.items())),
        },
        "limitations": [
            "boundary roles are declared adapter roles from closed-world call topology, not source ownership or behavioral reconstruction",
            "inbound direction evidence uses only seed-labelled callers; unlabeled callers stay unclaimed",
            "thumb-code-candidate regions are structural code evidence (in-image BL topology), not discovered functions; they remain outside the trustworthy-envelope corpus",
            "BL-free code (leaf or jump-table-only-reached functions) lands in the data classes; rodata-table is low confidence by construction",
            "envelope spans overlap each other; per-envelope byte partitions are independent views, not additive",
        ],
        "boundary_functions": boundary_rows,
        "envelope_regions": envelope_rows,
    }


MIXED_TSV_HEADER = (
    "entry\tbody_start\tbody_end_exclusive\tenvelope_bytes\tofficial_opaque_bytes\t"
    "seam\tboundary_role\tconfidence\tinbound_seed_callers\toutbound_call_edges\t"
    "adaptation_flow"
)
ENVELOPE_TSV_HEADER = (
    "entry\tbody_start\tbody_end_exclusive\tspan_bytes\taccepted_function_code_bytes\t"
    "interstitial_bytes\tregion_classes\tdominant_interstitial_class\tconfidence\t"
    "classified_regions\tdetail"
)


def mixed_boundary_tsv(report: dict[str, Any]) -> str:
    lines = [
        "# G2 Apollo mixed-evidence boundary-role map; regenerated by "
        "tools/analyze_g2_boundary_envelopes.py",
        MIXED_TSV_HEADER,
    ]
    for row in report["boundary_functions"]:
        inbound = "|".join(
            f"{family}={count}" for family, count in row["inbound_seed_callers"].items()
        )
        outbound = "|".join(
            f"{edge['family']}:0x{edge['target']:08X}" for edge in row["outbound_edges"]
        )
        lines.append(
            "\t".join(
                (
                    f"0x{row['entry']:08X}",
                    f"0x{row['body_start']:08X}",
                    f"0x{row['body_end_exclusive']:08X}",
                    str(row["envelope_bytes"]),
                    str(row["official_opaque_bytes"]),
                    row["seam"],
                    row["boundary_role"],
                    row["confidence"],
                    inbound or "-",
                    outbound,
                    row["adaptation_flow"],
                )
            )
        )
    return "\n".join(lines) + "\n"


def envelope_regions_tsv(report: dict[str, Any]) -> str:
    lines = [
        "# G2 Apollo oversized-envelope region classification; regenerated by "
        "tools/analyze_g2_boundary_envelopes.py",
        ENVELOPE_TSV_HEADER,
    ]
    for row in report["envelope_regions"]:
        classes = "|".join(
            f"{name}={size}" for name, size in row["region_classes"].items()
        )
        lines.append(
            "\t".join(
                (
                    f"0x{row['entry']:08X}",
                    f"0x{row['body_start']:08X}",
                    f"0x{row['body_end_exclusive']:08X}",
                    str(row["span_bytes"]),
                    str(row["accepted_function_code_bytes"]),
                    str(row["interstitial_bytes"]),
                    classes,
                    row["dominant_interstitial_class"],
                    row["confidence"],
                    str(row["classified_regions"]),
                    row["detail"],
                )
            )
        )
    return "\n".join(lines) + "\n"


def _text(report: dict[str, Any]) -> str:
    reconciliation = report["reconciliation"]
    lines = [
        "G2 Apollo boundary-role and oversized-envelope audit: PASS",
        f"  mixed boundary functions: {reconciliation['mixed_functions']} "
        f"({reconciliation['mixed_official_opaque_bytes']} official bytes)",
        "  seams: "
        + ", ".join(
            f"{seam}={count}"
            for seam, count in reconciliation["seam_census"].items()
        ),
        f"  oversized envelopes classified: {reconciliation['oversized_envelopes']}",
    ]
    for row in report["envelope_regions"]:
        lines.append(
            f"    0x{row['entry']:08X}: {row['span_bytes']} span bytes, "
            f"{row['accepted_function_code_bytes']} accepted-code, "
            f"dominant interstitial {row['dominant_interstitial_class']} "
            f"({row['confidence']})"
        )
    lines.append("hardware/flash operations: none")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ghidra-corpus", type=Path, required=True)
    parser.add_argument("--manifests", type=Path, default=MANIFESTS)
    parser.add_argument("--json", action="store_true")
    parser.add_argument(
        "--write-manifests",
        type=Path,
        metavar="DIRECTORY",
        help="write g2-mixed-boundary-map.tsv and g2-oversized-envelope-regions.tsv into DIRECTORY",
    )
    args = parser.parse_args()
    report = analyze(args.ghidra_corpus, manifests_dir=args.manifests)
    if args.write_manifests is not None:
        directory = args.write_manifests
        directory.mkdir(parents=True, exist_ok=True)
        (directory / "g2-mixed-boundary-map.tsv").write_text(
            mixed_boundary_tsv(report), encoding="utf-8"
        )
        (directory / "g2-oversized-envelope-regions.tsv").write_text(
            envelope_regions_tsv(report), encoding="utf-8"
        )
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(_text(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
