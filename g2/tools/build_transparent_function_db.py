#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Merge every G2 Ghidra artifact into one normalized function database.

The G2 evidence corpus records the same functions in several independent
places: the harvested decompilation, the unanchored provenance census, 300-odd
per-family function maps, and the compiled overlay configuration.  Each knows
something the others do not -- bounds and bodies, family attribution and
confidence, upstream names and behavioral notes, and which functions already
have reviewed source.

This tool reconciles them into a single address-keyed database, and then walks
the whole image so that *every* byte lands in exactly one region: a function
body, or a classified gap between function bodies.  Nothing is left implicit.

Output (under ``--output``):
    function-db.json     one record per function, sorted by address
    region-map.json      contiguous, gapless cover of the whole image
    DB-SUMMARY.json      counts, byte accounting, and input provenance

Usage:
    tools/build_transparent_function_db.py --output build/transparent
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable

REPO_ROOT = Path(__file__).resolve().parent.parent

#: The Apollo main payload is loaded so that file offset 0x20 is the vector
#: table at run address 0x00438000; the 32-byte OTA preamble precedes it.
APOLLO_BLOB = REPO_ROOT / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
APOLLO_PREAMBLE_BYTES = 0x20
APOLLO_VECTOR_BASE = 0x00438000
APOLLO_LOAD_BASE = APOLLO_VECTOR_BASE - APOLLO_PREAMBLE_BYTES
APOLLO_VECTOR_WORDS = 256

DEFAULT_HARVEST = REPO_ROOT / "research/corpus/apollo-main/ghidra/decomp"
CENSUS_TSV = REPO_ROOT / "tools/manifests/g2-apollo-unanchored-census-functions.tsv"
MANIFEST_DIR = REPO_ROOT / "tools/manifests"
OVERLAY_JSON = REPO_ROOT / "components/apollo_main/core_overlay/overlay.json"

#: Column aliases seen across the 302 hand-authored function maps.
NAME_COLUMNS = ("stock_name", "function", "name", "symbol")
START_COLUMNS = ("stock_start", "entry", "start", "body_start")
END_COLUMNS = ("stock_end_exclusive", "end_exclusive", "end", "body_end_exclusive")

#: Evidence tiers, weakest to strongest.  A function keeps the strongest tier
#: any input can justify.
TIER_ORDER = (
    "unrecovered",   # no decompilation and no evidence
    "decompiled",    # readable C recovered from the image, nothing more
    "identified",    # census attributes it to a provider family
    "attributed",    # a function map gives it a real name
    "candidate",     # a reviewed behavioral or upstream source route exists
    "source",        # reviewed source already compiled into the overlay
)

#: Function-map signals that a reviewed source route exists for a function.
CANDIDATE_STATUS = re.compile(
    r"recreated|exact|source_route|reimplement", re.IGNORECASE
)


class DatabaseError(RuntimeError):
    pass


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def parse_address(value: str | None) -> int | None:
    if value is None:
        return None
    text = value.strip()
    if not text:
        return None
    try:
        return int(text, 16) if text.lower().startswith("0x") else int(text, 16)
    except ValueError:
        try:
            return int(text)
        except ValueError:
            return None


def stronger(current: str, candidate: str) -> str:
    return candidate if TIER_ORDER.index(candidate) > TIER_ORDER.index(current) else current


def read_tsv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    """Read a manifest TSV, skipping the repository's ``#`` comment banners."""
    lines = [line for line in path.read_text(encoding="utf-8").splitlines() if line]
    body = [line for line in lines if not line.startswith("#")]
    if not body:
        return [], []
    reader = csv.DictReader(body, delimiter="\t")
    return list(reader.fieldnames or []), list(reader)


def pick_column(fieldnames: Iterable[str], candidates: Iterable[str]) -> str | None:
    available = list(fieldnames)
    for candidate in candidates:
        if candidate in available:
            return candidate
    return None


def load_harvest(harvest_dir: Path) -> tuple[dict[int, dict[str, Any]], dict[str, Any]]:
    records_path = harvest_dir / "functions.jsonl"
    summary_path = harvest_dir / "HARVEST.json"
    if not records_path.is_file():
        raise DatabaseError(
            f"no harvest at {records_path}; run tools/harvest_ghidra_decomp.py first"
        )
    functions: dict[int, dict[str, Any]] = {}
    with records_path.open(encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            record = json.loads(line)
            entry = int(record["entry"], 16)
            start = parse_address(record.get("body_start")) or entry
            end_inclusive = parse_address(record.get("body_end_inclusive"))
            size = int(record.get("body_bytes") or 0)
            end = (end_inclusive + 1) if end_inclusive is not None else start + size
            # A Ghidra function body is an address *set*: 107 Apollo functions
            # are split across several ranges, so min..max would swallow the
            # unrelated code sitting in the holes.  Carry the real ranges.
            ranges = [
                (parse_address(low), (parse_address(high) or 0) + 1)
                for low, high in record.get("ranges", [])
            ]
            ranges = [pair for pair in ranges if pair[0] is not None]
            if not ranges:
                ranges = [(start, end)]
            functions[entry] = {
                "ranges": [[low, high] for low, high in sorted(ranges)],
                "entry": entry,
                "start": start,
                "end": end,
                "size": size,
                "ghidra_name": record.get("name"),
                "signature": record.get("signature"),
                "calling_convention": record.get("calling_convention"),
                "thunk": bool(record.get("thunk")),
                "decompiled": bool(record.get("decompiled")),
                "body_sha256": record.get("body_sha256"),
                "callees": [int(value, 16) for value in record.get("callees", [])],
            }
    summary = json.loads(summary_path.read_text(encoding="utf-8")) if summary_path.is_file() else {}
    return functions, summary


def load_census(path: Path) -> dict[int, dict[str, str]]:
    if not path.is_file():
        return {}
    _, rows = read_tsv(path)
    census: dict[int, dict[str, str]] = {}
    for row in rows:
        entry = parse_address(row.get("entry"))
        if entry is None:
            continue
        census[entry] = {
            "bucket": row.get("bucket", ""),
            "evidence": row.get("evidence", ""),
            "confidence": row.get("confidence", ""),
            "detail": row.get("detail", ""),
            "official_opaque_bytes": row.get("official_opaque_bytes", ""),
        }
    return census


def load_function_maps(manifest_dir: Path) -> tuple[dict[int, list[dict[str, Any]]], list[str]]:
    """Collect every named interval from the per-family function maps."""
    named: dict[int, list[dict[str, Any]]] = defaultdict(list)
    consumed: list[str] = []
    for path in sorted(manifest_dir.glob("*function-map.tsv")):
        fieldnames, rows = read_tsv(path)
        name_column = pick_column(fieldnames, NAME_COLUMNS)
        start_column = pick_column(fieldnames, START_COLUMNS)
        if not name_column or not start_column:
            continue
        end_column = pick_column(fieldnames, END_COLUMNS)
        family = path.name.removesuffix("-function-map.tsv")
        used = False
        for row in rows:
            start = parse_address(row.get(start_column))
            name = (row.get(name_column) or "").strip()
            if start is None or not name:
                continue
            used = True
            record = {
                "name": name,
                "family": family,
                "manifest": path.name,
                "end": parse_address(row.get(end_column)) if end_column else None,
            }
            for extra in (
                "candidate_symbol",
                "behavior",
                "identity",
                "stock_status",
                "upstream_source_lines",
                "ownership_category",
                "evidence",
                "status",
                "object",
            ):
                value = (row.get(extra) or "").strip() if extra in row else ""
                if value:
                    record[extra] = value
            named[start].append(record)
        if used:
            consumed.append(path.name)
    return named, consumed


def load_overlay_sources(path: Path) -> dict[str, dict[str, Any]]:
    """Map already-source-owned symbol names to their overlay provenance."""
    if not path.is_file():
        return {}
    overlay = json.loads(path.read_text(encoding="utf-8"))
    owned: dict[str, dict[str, Any]] = {}
    for key in ("isolated_leaves", "relocated_leaves", "in_place_leaves"):
        for leaf in overlay.get(key, []):
            name = leaf.get("function")
            if not name:
                continue
            source = leaf.get("source", {})
            owned[name] = {
                "kind": key,
                "path": source.get("path"),
                "license": source.get("license"),
                "origin": source.get("origin"),
                "upstream": source.get("upstream"),
                "evidence": source.get("evidence"),
                "runtime_address": leaf.get("runtime_address"),
            }
    return owned


def classify_gap(data: bytes, start: int) -> str:
    """Describe a non-function region well enough to act on it later."""
    if not data:
        return "empty"
    if start == APOLLO_VECTOR_BASE:
        return "vector-table"
    unique = set(data)
    if unique <= {0x00}:
        return "zero-fill"
    if unique <= {0xFF}:
        return "erased-fill"
    if len(unique) == 1:
        return "constant-fill"
    printable = sum(1 for byte in data if 0x20 <= byte < 0x7F or byte in (0x09, 0x0A, 0x0D))
    if printable >= len(data) * 0.85 and len(data) >= 8:
        return "string-pool"
    # Dense pointer tables into the image read as ascending word-aligned values
    # inside the load window; that is the common shape for jump and vtable data.
    if len(data) >= 16 and len(data) % 4 == 0:
        words = [
            int.from_bytes(data[index:index + 4], "little")
            for index in range(0, len(data), 4)
        ]
        in_image = sum(
            1 for word in words
            if APOLLO_VECTOR_BASE <= (word & ~1) < APOLLO_LOAD_BASE + (1 << 22)
        )
        if in_image >= len(words) * 0.75:
            return "pointer-table"
    return "data"


def build(harvest_dir: Path, output_dir: Path) -> dict[str, Any]:
    if not APOLLO_BLOB.is_file():
        raise DatabaseError(
            f"official payload {APOLLO_BLOB} is absent; see blobs/official/*/PROVENANCE.md"
        )
    image = APOLLO_BLOB.read_bytes()
    image_start = APOLLO_LOAD_BASE
    image_end = image_start + len(image)

    functions, harvest_summary = load_harvest(harvest_dir)
    census = load_census(CENSUS_TSV)
    named, consumed_manifests = load_function_maps(MANIFEST_DIR)
    overlay_owned = load_overlay_sources(OVERLAY_JSON)

    for entry, record in functions.items():
        record["tier"] = "decompiled" if record["decompiled"] else "unrecovered"
        record["sources"] = ["ghidra-harvest"]

        census_row = census.get(entry)
        if census_row:
            record["bucket"] = census_row["bucket"]
            record["census_evidence"] = census_row["evidence"]
            record["census_confidence"] = census_row["confidence"]
            record["census_detail"] = census_row["detail"]
            record["sources"].append("unanchored-census")
            if census_row["evidence"] and census_row["evidence"] != "none":
                record["tier"] = stronger(record["tier"], "identified")

        matches = named.get(entry, [])
        if matches:
            record["sources"].append("function-map")
            record["names"] = [match["name"] for match in matches]
            record["families"] = sorted({match["family"] for match in matches})
            record["name"] = matches[0]["name"]
            record["map_records"] = matches
            record["tier"] = stronger(record["tier"], "attributed")
            for match in matches:
                candidate = match.get("candidate_symbol")
                status = match.get("stock_status", "")
                if candidate or match.get("upstream_source_lines") or CANDIDATE_STATUS.search(status):
                    record["tier"] = stronger(record["tier"], "candidate")
                    if candidate:
                        record["candidate_symbol"] = candidate
                for symbol in (candidate, match["name"]):
                    if symbol and symbol in overlay_owned:
                        record["tier"] = stronger(record["tier"], "source")
                        record["source_owned"] = overlay_owned[symbol]
                        record["sources"].append("overlay-source")
        record.setdefault("name", record.get("ghidra_name"))
        record["sources"] = sorted(set(record["sources"]))

    ordered = [functions[entry] for entry in sorted(functions)]

    # Function bodies may abut or, rarely, overlap after Ghidra merges blocks.
    # Walk the image once and emit a gapless cover so byte accounting is exact.
    regions: list[dict[str, Any]] = []
    cursor = image_start

    def emit_gap(start: int, end: int) -> None:
        if end <= start:
            return
        data = image[start - image_start:end - image_start]
        regions.append({
            "kind": "gap",
            "start": start,
            "end": end,
            "size": end - start,
            "classification": classify_gap(data, start),
            "sha256": sha256_bytes(data),
        })

    if APOLLO_PREAMBLE_BYTES:
        preamble = image[:APOLLO_PREAMBLE_BYTES]
        regions.append({
            "kind": "preamble",
            "start": image_start,
            "end": image_start + APOLLO_PREAMBLE_BYTES,
            "size": APOLLO_PREAMBLE_BYTES,
            "classification": "ota-staging-header",
            "sha256": sha256_bytes(preamble),
        })
        cursor = image_start + APOLLO_PREAMBLE_BYTES

    # Flatten every function's ranges into one address-ordered cover.  Ranges
    # are disjoint across functions, so a plain sort is enough; any residual
    # overlap is reported rather than silently absorbed.
    by_entry = {record["entry"]: record for record in ordered}
    for record in ordered:
        record["covered_bytes"] = 0
    flattened = sorted(
        (low, high, record["entry"])
        for record in ordered
        for low, high in record["ranges"]
    )

    overlaps = 0
    for low, high, entry in flattened:
        record = by_entry[entry]
        start = max(low, cursor)
        if high <= start:
            overlaps += 1
            continue
        if low > cursor:
            emit_gap(cursor, low)
        record["covered_bytes"] += high - start
        data = image[start - image_start:high - image_start]
        regions.append({
            "kind": "function",
            "start": start,
            "end": high,
            "size": high - start,
            "entry": entry,
            "name": record.get("name"),
            "tier": record["tier"],
            "classification": "code",
            "sha256": sha256_bytes(data),
        })
        cursor = high
    emit_gap(cursor, image_end)

    tier_counts = Counter(record["tier"] for record in ordered)
    tier_bytes = Counter()
    for record in ordered:
        tier_bytes[record["tier"]] += record.get("covered_bytes", 0)
    gap_bytes = Counter()
    gap_counts = Counter()
    for region in regions:
        if region["kind"] == "function":
            continue
        gap_bytes[region["classification"]] += region["size"]
        gap_counts[region["classification"]] += 1

    covered = sum(region["size"] for region in regions)
    if covered != len(image):
        raise DatabaseError(
            f"region cover is {covered} bytes but the image is {len(image)}"
        )

    output_dir.mkdir(parents=True, exist_ok=True)
    database = {
        "schema_version": 1,
        "generator": "tools/build_transparent_function_db.py",
        "image": {
            "path": str(APOLLO_BLOB.relative_to(REPO_ROOT)),
            "sha256": sha256_file(APOLLO_BLOB),
            "size": len(image),
            "load_base": image_start,
            "vector_base": APOLLO_VECTOR_BASE,
            "vector_words": APOLLO_VECTOR_WORDS,
        },
        "functions": ordered,
    }
    (output_dir / "function-db.json").write_text(
        json.dumps(database, indent=1, sort_keys=True) + "\n", encoding="utf-8"
    )
    (output_dir / "region-map.json").write_text(
        json.dumps({"schema_version": 1, "regions": regions}, indent=1, sort_keys=True)
        + "\n",
        encoding="utf-8",
    )

    summary = {
        "schema_version": 1,
        "generator": "tools/build_transparent_function_db.py",
        "inputs": {
            "harvest": str(harvest_dir.relative_to(REPO_ROOT)) if harvest_dir.is_relative_to(REPO_ROOT) else str(harvest_dir),
            "harvest_functions": harvest_summary.get("counts", {}).get("functions"),
            "census_rows": len(census),
            "function_maps_consumed": len(consumed_manifests),
            "function_map_intervals": sum(len(value) for value in named.values()),
            "overlay_source_functions": len(overlay_owned),
        },
        "image_bytes": len(image),
        "function_count": len(ordered),
        "overlapping_functions_dropped": overlaps,
        "tier_counts": dict(sorted(tier_counts.items())),
        "tier_bytes": dict(sorted(tier_bytes.items())),
        "code_bytes": sum(tier_bytes.values()),
        "gap_counts": dict(sorted(gap_counts.items())),
        "gap_bytes": dict(sorted(gap_bytes.items())),
        "non_code_bytes": sum(gap_bytes.values()),
    }
    (output_dir / "DB-SUMMARY.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return summary


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--harvest", type=Path, default=DEFAULT_HARVEST)
    parser.add_argument("--output", type=Path, default=REPO_ROOT / "build/transparent")
    args = parser.parse_args(argv)

    try:
        summary = build(args.harvest.resolve(), args.output.resolve())
    except DatabaseError as failure:
        print(f"error: {failure}", file=sys.stderr)
        return 2

    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
