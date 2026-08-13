#!/usr/bin/env python3
"""Provenance census of the Apollo-main unanchored Ghidra functions.

The authenticated 64-shard Lorelei corpus discovers 7,370 functions in the
official G2 ``s200_v2.2.6.10`` Apollo-main image.  The embedded source-path
census anchors 1,760 of them to retained ``__FILE__`` paths, leaving 5,610
discovered functions without a retained-path anchor.  This analyzer converts
that flat remainder into a defensible provider-family triage map.

Evidence tiers, applied in strict priority order:

1. ``rejected-oversized-envelope`` -- Ghidra envelopes larger than the
   16,384-byte trustworthy-envelope cap used by the origin accounting.  These
   eight envelopes are rejected analyzer artifacts over mixed data regions,
   not trustworthy functions.
2. ``closed-module-manifest`` -- the function entry is named by an existing
   fail-closed per-module function-map manifest under ``tools/manifests/``.
   The provider family comes from the curated audit that produced the
   manifest; this is prior reviewed work, not a new inference.
3. ``library-string-signature`` -- the function references an IAR DLIB
   diagnostic string (or its pointer cell) that no other provider emits.
4. ``call-topology-single-family`` -- every closed-world call target of the
   function (path-anchored function, manifest-mapped function, or DLIB string
   signature function) collapses to exactly one provider family.
5. ``link-order-sandwich`` -- the nearest labelled functions on both sides in
   address order share one family.  Link order groups translation units, so
   this is a low-confidence triage signal only.
6. ``investigation-required-mixed`` -- call targets span multiple families.
7. ``investigation-required-no-evidence`` -- no corroborating evidence.

Byte accounting reuses the origin-accounting model: envelope bytes are only
trusted up to the 16,384-byte cap, and "official opaque bytes" are counted
through the canonical flash plan's ``official_blob`` regions after removing
builder-controlled patch sites.  The sum over all unanchored accepted
envelopes must reproduce the origin accounting's 675,636-byte unanchored
bucket exactly; any drift raises ``CensusError``.

The analyzer is read-only and deterministic.  It re-derives the unanchored
set from the authenticated image, corpus, and manifests; nothing is
hardcoded from prior census output.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import json
import re
import struct
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PATH_ANALYZER = ROOT / "tools/analyze_apollo_embedded_source_paths.py"
MANIFESTS = ROOT / "tools/manifests"
DEFAULT_PLAN = ROOT / "build/source/flash-plan.json"
DEFAULT_COMPONENT_REPORT = ROOT / "components/apollo_main/core_overlay/build/build-report.json"
PLAN_SHA256 = "97230c89e27b9fea1db1d0cc9c2ca6bed5449ece6d35ea98cf101d7a219b1d9e"

MAX_TRUSTWORTHY_FUNCTION_ENVELOPE = 16_384
EXPECTED_CORPUS_FUNCTIONS = 7_370
EXPECTED_ANCHORED_FUNCTIONS = 1_760
EXPECTED_UNANCHORED_FUNCTIONS = 5_610
EXPECTED_OVERSIZED_ENTRIES = (
    0x0047CC60,
    0x0048949C,
    0x00509708,
    0x00513E2E,
    0x00514F3C,
    0x00541B74,
    0x0055F994,
    0x005FA120,
)
EXPECTED_COMPONENT_OPAQUE_BASE_BYTES = 3_424_780
EXPECTED_UNANCHORED_OFFICIAL_BYTES = 675_636
EXPECTED_MANIFEST_FILES = 302

# ``*-function-map.tsv`` manifests that deliberately target a non-Apollo
# image.  ``g2-box`` maps the charging-case STM32G0 firmware at 0x08000000
# (firmware_box.bin), not the Apollo-main corpus; it is counted in the
# manifest census above and skipped here so no foreign address can alias an
# Apollo function.  Any other unknown stem or schema still fails closed.
NON_APOLLO_MANIFEST_STEMS = frozenset({"g2-box"})

# IAR DLIB diagnostic strings.  The ``_s`` Annex-K spellings and the
# constraint-handler message are emitted only by the IAR DLIB runtime; no
# vendored or first-party translation unit contains them.  Addresses are
# re-derived from the authenticated image on every run, never hardcoded.
DLIB_SIGNATURE_STRINGS = (
    "printf: bad %n argument",
    "printf_s: bad %s argument",
    "printf_s: %n disallowed",
    "scanf_s: bad %n argument",
    "scanf_s: bad integer argument",
    "scanf_s: bad %c, %s, or %[ size",
    "scanf_s: bad floating-point argument",
    "scanf_s: bad %c, %s, or %[ argument",
    " constraint handler: bad message",
    "0123456789abcdefABCDEF",
)

# Manifest stems whose provider family is a third-party dependency rather
# than first-party Even code.  Every other ``g2-*`` stem names an Even
# application module (for example ``g2-lvgl-font-manager`` is the first-party
# ``app\gui\common\lvgl_font_manager.c`` glue object, not LVGL itself).
NON_FIRST_PARTY_G2_STEMS = {
    "g2-freertos-plus-cli-filesystem": "freertos-plus-cli",
    "g2-iar-float-exponent": "iar-dlib",
    "g2-json-parser": "cjson",
}
MANIFEST_PREFIX_FAMILIES = (
    ("packetcraft-cordio-", "cordio"),
    ("ambiqsuite-cordio-", "ambiqsuite"),
    ("ambiq-cordio-", "ambiqsuite"),
    ("ambiqsuite-ancc-", "ambiqsuite-ancc"),
    ("cordio-", "cordio"),
    ("cmsis-freertos-", "cmsis-freertos"),
)

PROVIDER_FAMILIES: dict[str, dict[str, str]] = {
    "lvgl": {
        "label": "LVGL 9.3.0-development vendor fork (Ambiq backend)",
        "ownership": "authenticated upstream source (vendor-fork interval)",
    },
    "cordio": {
        "label": "Packetcraft/Ambiq Cordio BLE host (r20.05-r20.05c interval)",
        "ownership": "authenticated upstream source (compatibility interval)",
    },
    "ambiqsuite": {
        "label": "AmbiqSuite proprietary Cordio/WSF port objects",
        "ownership": "licensed or proprietary source dependency",
    },
    "ambiqsuite-ancc": {
        "label": "AmbiqSuite ANCC/ANCS client profile",
        "ownership": "licensed or proprietary source dependency",
    },
    "cmsis-freertos": {
        "label": "CMSIS-FreeRTOS v10.5.1 os2 wrapper",
        "ownership": "authenticated upstream source",
    },
    "freertos-plus-cli": {
        "label": "FreeRTOS-Plus-CLI interpreter object",
        "ownership": "authenticated upstream source (compatibility baseline)",
    },
    "cjson": {
        "label": "DaveGamble cJSON v1.7.9-v1.7.12 parser",
        "ownership": "authenticated upstream source (compatibility interval)",
    },
    "iar-dlib": {
        "label": "IAR DLIB compiler runtime (EWARM 9.20+ candidate)",
        "ownership": "licensed or proprietary source dependency",
    },
    "littlefs": {
        "label": "littlefs v2.10.1-equivalent",
        "ownership": "authenticated upstream source",
    },
    "tlsf": {
        "label": "TLSF v3.1-equivalent allocator",
        "ownership": "authenticated upstream source",
    },
    "tinyframe": {
        "label": "TinyFrame exact-core interval",
        "ownership": "authenticated upstream source",
    },
    "easylogger": {
        "label": "EasyLogger 2.2.99-compatible core",
        "ownership": "authenticated upstream source (compatible interval)",
    },
    "ring-buffer": {
        "label": "AndersKaloer/Ring-Buffer dynamic-buffer interval",
        "ownership": "authenticated upstream source (compatible interval)",
    },
    "nanopb": {
        "label": "nanopb 0.4.7-0.4.9.1-compatible protobuf runtime",
        "ownership": "authenticated upstream source (compatibility interval)",
    },
    "lz4": {
        "label": "LZ4 v1.10.0 decompress-only decoder",
        "ownership": "authenticated upstream source (compatibility selection)",
    },
    "freetype": {
        "label": "FreeType 2.9.1 engine (LVGL-bundled)",
        "ownership": "authenticated upstream source (exact snapshot)",
    },
    "liblc3": {
        "label": "Google liblc3 v1.1.3-era encoder",
        "ownership": "authenticated upstream source (compatibility interval)",
    },
    "first-party": {
        "label": "Even first-party application/platform code",
        "ownership": "clean-room G2 implementation target (first-party stock code)",
    },
    "rejected-oversized-envelope": {
        "label": "oversized Ghidra envelope rejected by the trust cap",
        "ownership": "generated or non-executable content (analyzer artifact)",
    },
    "investigation-required-mixed": {
        "label": "call targets span multiple provider families",
        "ownership": "investigation required",
    },
    "investigation-required-no-evidence": {
        "label": "no corroborating provenance evidence",
        "ownership": "investigation required",
    },
}

# Anchored third-party dependency names -> census family keys.
ANCHOR_FAMILY = {
    "lvgl_v9.3": "lvgl",
    "cordio": "cordio",
    "littlefs": "littlefs",
    "tlsf": "tlsf",
    "TinyFrame": "tinyframe",
    "EasyLogger-master": "easylogger",
    "ringBuffer": "ring-buffer",
}

# Curated documented-family evidence for upstream families that leave no
# retained ``__FILE__`` path and have no ``*-function-map.tsv`` manifest.
# Every entry cites the reviewed project record that authenticates it; the
# analyzer re-validates each span against the corpus on every run.
LIBLC3_ENTRY_MAP = MANIFESTS / "g2-liblc3-public-entry-map.tsv"
EXPECTED_LIBLC3_PUBLIC_ENTRIES = (0x00590E64, 0x00590F78, 0x00591374, 0x0059138A)
DOCUMENTED_FAMILY_EVIDENCE = (
    {
        "family": "nanopb",
        "kind": "span",
        "start": 0x0048F000,
        "end_exclusive": 0x00491400,
        "confidence": "medium",
        "source": "docs/upstream-inventory.md nanopb row: runtime at "
        "0x0048F000-0x00491400 compatible with pristine upstream 0.4.7-0.4.9.1",
    },
    {
        "family": "lz4",
        "kind": "entries",
        "entries": (0x0054EE90, 0x0054EF08, 0x0054F338),
        "confidence": "high",
        "source": "docs/upstream-inventory.md LZ4 row: read_variable_length "
        "0x0054EE90, LZ4_decompress_generic 0x0054EF08, LZ4_decompress_safe 0x0054F338",
    },
    {
        "family": "freetype",
        "kind": "span",
        "start": 0x00526814,
        "end_exclusive": 0x0052687E,
        "confidence": "high",
        "source": "docs/research/freetype-recovery-audit.md: exact FT_Done_Face "
        "at [0x00526814,0x0052687E)",
    },
)

FUNCTION_BEGIN_RE = re.compile(
    r"OPENCFW_FUNCTION_BEGIN entry=([0-9a-f]+) "
    r"body_start=([0-9a-f]+) body_end=([0-9a-f]+) name=(\S+)",
    re.IGNORECASE,
)
FUNCTION_END_RE = re.compile(r"OPENCFW_FUNCTION_END entry=([0-9a-f]+)", re.IGNORECASE)
ADDRESS_TOKEN_RE = re.compile(r"(?<![0-9a-fA-F])([0-9a-f]{8})(?![0-9a-fA-F])")

CONFIDENCE_ORDER = ("high", "medium", "low", "none")


class CensusError(RuntimeError):
    """Raised when authenticated evidence or a closed census changes."""


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _load_path_analyzer():
    spec = importlib.util.spec_from_file_location(
        "apollo_paths_for_unanchored_census", PATH_ANALYZER
    )
    if spec is None or spec.loader is None:
        raise CensusError(f"cannot load {PATH_ANALYZER}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _manifest_family(stem: str) -> str:
    if stem in NON_FIRST_PARTY_G2_STEMS:
        return NON_FIRST_PARTY_G2_STEMS[stem]
    for prefix, family in MANIFEST_PREFIX_FAMILIES:
        if stem.startswith(prefix):
            return family
    if stem.startswith("g2-"):
        return "first-party"
    raise CensusError(f"function-map manifest has no provider family rule: {stem}")


def _parse_hex(value: str | None) -> int | None:
    try:
        return int((value or "").strip(), 16)
    except ValueError:
        return None


def load_manifest_function_maps(
    manifests_dir: Path = MANIFESTS,
) -> dict[int, tuple[str, str]]:
    """Map stock function start addresses to (family, manifest stem).

    Every ``*-function-map.tsv`` file must use a known address schema and a
    stem with an explicit provider-family rule; both conditions fail closed.
    """

    files = sorted(manifests_dir.glob("*-function-map.tsv"))
    if len(files) != EXPECTED_MANIFEST_FILES:
        raise CensusError(
            f"expected {EXPECTED_MANIFEST_FILES} function-map manifests, "
            f"found {len(files)}"
        )
    start_columns = ("stock_start", "start", "entry")
    end_columns = ("stock_end_exclusive", "end_exclusive")
    mapping: dict[int, tuple[str, str]] = {}
    skipped: list[str] = []
    for path in files:
        stem = path.name[: -len("-function-map.tsv")]
        if stem in NON_APOLLO_MANIFEST_STEMS:
            skipped.append(stem)
            continue
        family = _manifest_family(stem)
        lines = [
            line
            for line in path.read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.startswith("#")
        ]
        if not lines:
            raise CensusError(f"empty function-map manifest: {path.name}")
        reader = csv.DictReader(lines, delimiter="\t")
        columns = reader.fieldnames or ()
        start_column = next((c for c in start_columns if c in columns), None)
        end_column = next((c for c in end_columns if c in columns), None)
        single_column: str | None = None
        if start_column is None and "stock_address" in columns:
            single_column = "stock_address"
        if start_column is None and single_column is None:
            raise CensusError(f"unknown function-map schema in {path.name}: {columns!r}")
        if start_column is not None and end_column is None:
            raise CensusError(f"function-map manifest lacks an end column: {path.name}")
        for row in reader:
            address = _parse_hex(row.get(single_column) if single_column else row.get(start_column))
            if address is None:
                continue
            mapping.setdefault(address, (family, stem))
    if sorted(skipped) != sorted(NON_APOLLO_MANIFEST_STEMS):
        raise CensusError(
            f"non-Apollo manifest census changed: skipped {sorted(skipped)}"
        )
    return mapping


def load_liblc3_entries(manifests_dir: Path = MANIFESTS) -> dict[int, str]:
    """Authenticated liblc3 public entries from the source-boundary audit."""

    path = manifests_dir / LIBLC3_ENTRY_MAP.name
    if not path.is_file():
        raise CensusError(f"missing liblc3 entry map: {path.name}")
    lines = [
        line
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.startswith("#")
    ]
    reader = csv.DictReader(lines, delimiter="\t")
    columns = reader.fieldnames or ()
    if "stock_start" not in columns:
        raise CensusError(f"unknown liblc3 entry-map schema: {columns!r}")
    entries: dict[int, str] = {}
    for row in reader:
        address = _parse_hex(row.get("stock_start"))
        if address is not None:
            entries[address] = (row.get("function") or "").strip()
    if tuple(sorted(entries)) != EXPECTED_LIBLC3_PUBLIC_ENTRIES:
        raise CensusError(
            "liblc3 public entry census changed: "
            + ", ".join(f"0x{address:08x}" for address in sorted(entries))
        )
    return {address: name for address, name in entries.items()}


def parse_corpus_functions(logs: list[Path]) -> dict[int, dict[str, Any]]:
    functions: dict[int, dict[str, Any]] = {}
    current: dict[str, Any] | None = None
    for log in logs:
        for line in log.read_text(encoding="utf-8", errors="strict").splitlines():
            begin = FUNCTION_BEGIN_RE.search(line)
            if begin:
                entry, body_start, body_end = (int(value, 16) for value in begin.groups()[:3])
                if entry in functions:
                    raise CensusError(f"duplicate Ghidra function entry 0x{entry:08x}")
                current = {
                    "entry": entry,
                    "body_start": body_start,
                    "body_end_inclusive": body_end,
                    "name": begin.group(4),
                    "tokens": set(),
                }
                functions[entry] = current
                continue
            end = FUNCTION_END_RE.search(line)
            if end:
                entry = int(end.group(1), 16)
                if current is None or current["entry"] != entry:
                    raise CensusError(f"unbalanced Ghidra function marker 0x{entry:08x}")
                current = None
                continue
            if current is not None:
                current["tokens"].update(
                    int(token, 16) for token in ADDRESS_TOKEN_RE.findall(line)
                )
    if current is not None:
        raise CensusError("unterminated Ghidra function at end of corpus")
    if len(functions) != EXPECTED_CORPUS_FUNCTIONS:
        raise CensusError(
            f"expected {EXPECTED_CORPUS_FUNCTIONS} Ghidra functions, "
            f"found {len(functions)}"
        )
    return functions


def dlib_signature_targets(blob: bytes, load_base: int) -> set[int]:
    """Image addresses of the DLIB signature strings and their pointer cells."""

    targets: set[int] = set()
    for text in DLIB_SIGNATURE_STRINGS:
        needle = text.encode("ascii") + b"\x00"
        cursor = 0
        while True:
            offset = blob.find(needle, cursor)
            if offset < 0:
                break
            string_address = load_base + offset
            targets.add(string_address)
            cell_needle = struct.pack("<I", string_address)
            cell_cursor = 0
            while True:
                cell_offset = blob.find(cell_needle, cell_cursor)
                if cell_offset < 0:
                    break
                targets.add(load_base + cell_offset)
                cell_cursor = cell_offset + 1
            cursor = offset + 1
    if not targets:
        raise CensusError("no IAR DLIB signature strings located in the image")
    return targets


def _mark(mask: bytearray, start: int, end: int, base: int) -> None:
    first = max(0, start - base)
    last = min(len(mask), end - base)
    if last > first:
        mask[first:last] = b"\1" * (last - first)


def _clear_and_count(mask: bytearray, start: int, end: int, base: int) -> int:
    first = max(0, start - base)
    last = min(len(mask), end - base)
    if last <= first:
        return 0
    overlap = sum(mask[first:last])
    mask[first:last] = b"\0" * (last - first)
    return overlap


def build_official_mask(
    plan_path: Path,
    component_report_path: Path,
    image_size: int,
    load_base: int,
) -> bytearray:
    """Official opaque Apollo-main bytes, after removing controlled patches."""

    if _sha256_bytes(plan_path.read_bytes()) != PLAN_SHA256:
        raise CensusError("canonical flash plan identity changed")
    plan = json.loads(plan_path.read_text())
    component_report = json.loads(component_report_path.read_text())
    official = bytearray(image_size)
    for row in plan["flash_regions"]:
        if row.get("component") == "apollo_main" and row.get("address_status") == "official_blob":
            _mark(official, row["target_address"], row["end_exclusive"], load_base)
    for site in component_report["overlay"]["patched_sites"]:
        size = len(bytes.fromhex(site["replacement_hex"]))
        _clear_and_count(official, site["runtime_address"], site["runtime_address"] + size, load_base)
    for leaf in component_report.get("in_place_leaves", []):
        placement = leaf["placement"]
        _clear_and_count(
            official,
            placement["runtime_address"],
            placement["runtime_address"] + placement["size"],
            load_base,
        )
    if sum(official) != EXPECTED_COMPONENT_OPAQUE_BASE_BYTES:
        raise CensusError(
            f"official opaque base changed: {sum(official)} != "
            f"{EXPECTED_COMPONENT_OPAQUE_BASE_BYTES}"
        )
    return official


def analyze(
    corpus_root: Path,
    manifests_dir: Path = MANIFESTS,
    plan_path: Path = DEFAULT_PLAN,
    component_report_path: Path = DEFAULT_COMPONENT_REPORT,
) -> dict[str, Any]:
    path_module = _load_path_analyzer()
    path_report = path_module.analyze(corpus_root=corpus_root)
    correlation = path_report["ghidra_correlation"]
    load_base = path_module.LOAD_BASE
    image_size = path_module.IMAGE_SIZE
    blob = path_module.DEFAULT_IMAGE.read_bytes()

    anchored: dict[int, dict[str, Any]] = {
        row["entry"]: row for row in correlation["functions"]
    }
    if len(anchored) != EXPECTED_ANCHORED_FUNCTIONS:
        raise CensusError(
            f"anchored function census changed: {len(anchored)} != "
            f"{EXPECTED_ANCHORED_FUNCTIONS}"
        )

    logs = path_module.verify_corpus(corpus_root)
    functions = parse_corpus_functions(logs)
    unanchored = {entry: row for entry, row in functions.items() if entry not in anchored}
    if len(unanchored) != EXPECTED_UNANCHORED_FUNCTIONS:
        raise CensusError(
            f"unanchored function census changed: {len(unanchored)} != "
            f"{EXPECTED_UNANCHORED_FUNCTIONS}"
        )

    official = build_official_mask(plan_path, component_report_path, image_size, load_base)
    manifest_map = load_manifest_function_maps(manifests_dir)

    # Resolve manifest stock addresses to corpus function entries.  A manifest
    # row normally names a function start; a handful name an interior address,
    # which is mapped to the containing accepted envelope.
    manifest_labels: dict[int, tuple[str, str]] = {}
    for address, (family, stem) in sorted(manifest_map.items()):
        target = address if address in functions else None
        if target is None:
            for entry, row in functions.items():
                if row["body_start"] <= address <= row["body_end_inclusive"]:
                    target = entry
                    break
        if target is not None:
            manifest_labels.setdefault(target, (family, stem))

    oversized = sorted(
        entry
        for entry, row in functions.items()
        if row["body_end_inclusive"] - row["body_start"] + 1 > MAX_TRUSTWORTHY_FUNCTION_ENVELOPE
    )
    if tuple(oversized) != EXPECTED_OVERSIZED_ENTRIES:
        raise CensusError(
            "oversized envelope census changed: "
            + ", ".join(f"0x{entry:08x}" for entry in oversized)
        )
    if any(entry in anchored for entry in oversized):
        raise CensusError("an oversized rejected envelope gained a source-path anchor")
    oversized_set = set(oversized)

    # Tier 2.5: curated documented-family evidence for families without a
    # function-map manifest.  Spans match on function entry address; exact
    # entries match the entry exactly.  Every curated span must label at
    # least one unanchored corpus function or the census fails closed.
    documented_labels: dict[int, tuple[str, str, str]] = {}
    liblc3_entries = load_liblc3_entries(manifests_dir)
    for address, name in sorted(liblc3_entries.items()):
        if address in functions:
            documented_labels[address] = (
                "liblc3",
                "high",
                f"liblc3 public entry {name} (g2-liblc3-public-entry-map.tsv)",
            )
    if len(documented_labels) != len(EXPECTED_LIBLC3_PUBLIC_ENTRIES):
        raise CensusError("a liblc3 public entry is no longer a discovered function")
    for evidence in DOCUMENTED_FAMILY_EVIDENCE:
        family = evidence["family"]
        matched = 0
        if evidence["kind"] == "span":
            for entry, row in functions.items():
                if evidence["start"] <= entry < evidence["end_exclusive"]:
                    documented_labels.setdefault(
                        entry,
                        (family, evidence["confidence"], evidence["source"]),
                    )
                    matched += 1
        else:
            for address in evidence["entries"]:
                if address in functions:
                    documented_labels.setdefault(
                        address,
                        (family, evidence["confidence"], evidence["source"]),
                    )
                    matched += 1
        if matched == 0:
            raise CensusError(f"documented {family} evidence matched no corpus function")

    # Tier 3: IAR DLIB diagnostic-string users.
    dlib_targets = dlib_signature_targets(blob, load_base)
    dlib_functions = sorted(
        entry
        for entry, row in unanchored.items()
        if entry not in oversized_set and row["tokens"] & dlib_targets
    )

    # Seed labels used by the topology and sandwich tiers: path anchors,
    # manifest labels, and DLIB string-signature functions.
    def anchor_family(entry: int) -> str:
        row = anchored[entry]
        dependencies = row.get("third_party_dependencies") or []
        if dependencies:
            return ANCHOR_FAMILY[dependencies[0]]
        return "first-party"

    seed_label: dict[int, str] = {}
    for entry in anchored:
        seed_label[entry] = anchor_family(entry)
    for entry, (family, _stem) in manifest_labels.items():
        seed_label.setdefault(entry, family)
    for entry, (family, _confidence, _detail) in documented_labels.items():
        seed_label.setdefault(entry, family)
    for entry in dlib_functions:
        seed_label[entry] = "iar-dlib"

    # Address-ordered accepted envelopes for the link-order sandwich tier.
    accepted_order = sorted(
        (entry for entry in functions if entry not in oversized_set),
        key=lambda entry: functions[entry]["body_start"],
    )
    position = {entry: index for index, entry in enumerate(accepted_order)}

    # Per-function official-byte attribution mirrors the origin accounting's
    # mask semantics: anchored envelopes claim first, then each unanchored
    # envelope claims its remaining bytes in address order, so the 15 known
    # overlapping unanchored envelope pairs are counted exactly once.
    claimed = bytearray(image_size)
    for entry in anchored:
        if entry not in oversized_set:
            row = functions[entry]
            _mark(claimed, row["body_start"], row["body_end_inclusive"] + 1, load_base)

    def attribute_official_bytes(body_start: int, body_end: int) -> int:
        count = 0
        first = max(0, body_start - load_base)
        last = min(image_size, body_end - load_base)
        for index in range(first, last):
            if official[index] and not claimed[index]:
                count += 1
        _mark(claimed, body_start, body_end, load_base)
        return count

    records: list[dict[str, Any]] = []
    for entry in sorted(unanchored, key=lambda value: functions[value]["body_start"]):
        row = functions[entry]
        body_start = row["body_start"]
        body_end = row["body_end_inclusive"] + 1
        envelope_bytes = body_end - body_start
        tokens = row["tokens"]
        record: dict[str, Any] = {
            "entry": entry,
            "body_start": body_start,
            "body_end_exclusive": body_end,
            "envelope_bytes": envelope_bytes,
            "official_opaque_bytes": 0,
            "bucket": None,
            "evidence": None,
            "confidence": None,
            "detail": "",
        }
        if entry in oversized_set:
            record.update(
                bucket="rejected-oversized-envelope",
                evidence="analyzer-artifact",
                confidence="high",
                detail="envelope exceeds the 16,384-byte trust cap; mixed data region",
            )
            records.append(record)
            continue
        record["official_opaque_bytes"] = attribute_official_bytes(body_start, body_end)
        if entry in manifest_labels:
            family, stem = manifest_labels[entry]
            record.update(
                bucket=family,
                evidence="closed-module-manifest",
                confidence="high",
                detail=f"function-map manifest {stem}",
            )
            records.append(record)
            continue
        if entry in documented_labels:
            family, confidence, detail = documented_labels[entry]
            record.update(
                bucket=family,
                evidence="documented-family-evidence",
                confidence=confidence,
                detail=detail,
            )
            records.append(record)
            continue
        if entry in dlib_functions:
            record.update(
                bucket="iar-dlib",
                evidence="library-string-signature",
                confidence="high",
                detail="references IAR DLIB printf_s/scanf_s/constraint diagnostics",
            )
            records.append(record)
            continue
        seed_families = {
            seed_label[token] for token in tokens if token in seed_label
        }
        if len(seed_families) == 1:
            family = next(iter(seed_families))
            record.update(
                bucket=family,
                evidence="call-topology-single-family",
                confidence="medium",
                detail="every closed-world call target is " + family,
            )
            records.append(record)
            continue
        if len(seed_families) > 1:
            record.update(
                bucket="investigation-required-mixed",
                evidence="call-topology-mixed",
                confidence="none",
                detail="call targets span " + "|".join(sorted(seed_families)),
            )
            records.append(record)
            continue
        # Link-order sandwich: nearest labelled accepted functions on both
        # sides.  Labels propagate only from high-confidence seeds, never from
        # other tier-4/5 assignments.
        index = position[entry]
        previous_label = next_label = None
        cursor = index - 1
        while cursor >= 0:
            candidate = accepted_order[cursor]
            if candidate in seed_label:
                previous_label = seed_label[candidate]
                break
            cursor -= 1
        cursor = index + 1
        while cursor < len(accepted_order):
            candidate = accepted_order[cursor]
            if candidate in seed_label:
                next_label = seed_label[candidate]
                break
            cursor += 1
        if previous_label is not None and previous_label == next_label:
            record.update(
                bucket=previous_label,
                evidence="link-order-sandwich",
                confidence="low",
                detail="bracketed in link order by " + previous_label,
            )
            records.append(record)
            continue
        hints = []
        if any(0x2000_0000 <= token < 0x2008_0000 for token in tokens):
            hints.append("references SRAM globals")
        if any(0x4000_0000 <= token < 0x6000_0000 for token in tokens):
            hints.append("references peripheral registers")
        if row["name"].startswith("thunk_"):
            hints.append("linker veneer")
        record.update(
            bucket="investigation-required-no-evidence",
            evidence="none",
            confidence="none",
            detail="; ".join(hints) if hints else "no closed-world evidence",
        )
        records.append(record)

    official_total = sum(record["official_opaque_bytes"] for record in records)
    if official_total != EXPECTED_UNANCHORED_OFFICIAL_BYTES:
        raise CensusError(
            f"unanchored official-byte reconciliation changed: {official_total} != "
            f"{EXPECTED_UNANCHORED_OFFICIAL_BYTES}"
        )

    buckets: dict[str, dict[str, Any]] = {}
    for family, meta in PROVIDER_FAMILIES.items():
        buckets[family] = {
            "functions": 0,
            "accepted_envelope_bytes": 0,
            "official_opaque_bytes": 0,
            "label": meta["label"],
            "ownership_category": meta["ownership"],
            "evidence_classes": Counter(),
            "confidence": Counter(),
        }
    for record in records:
        bucket = buckets[record["bucket"]]
        bucket["functions"] += 1
        if record["bucket"] != "rejected-oversized-envelope":
            bucket["accepted_envelope_bytes"] += record["envelope_bytes"]
            bucket["official_opaque_bytes"] += record["official_opaque_bytes"]
        bucket["evidence_classes"][record["evidence"]] += 1
        bucket["confidence"][record["confidence"]] += 1
    bucket_rows = []
    for family in PROVIDER_FAMILIES:
        bucket = buckets[family]
        if bucket["functions"] == 0:
            continue
        bucket_rows.append(
            {
                "bucket": family,
                "label": bucket["label"],
                "ownership_category": bucket["ownership_category"],
                "functions": bucket["functions"],
                "accepted_envelope_bytes": bucket["accepted_envelope_bytes"],
                "official_opaque_bytes": bucket["official_opaque_bytes"],
                "evidence_classes": dict(sorted(bucket["evidence_classes"].items())),
                "confidence": {
                    level: bucket["confidence"].get(level, 0)
                    for level in CONFIDENCE_ORDER
                    if bucket["confidence"].get(level, 0)
                },
            }
        )

    return {
        "schema_version": 1,
        "analysis_mode": "read-only; no signing, flashing, erase, or hardware operation",
        "target": "official G2 s200_v2.2.6.10 Apollo main",
        "inputs": {
            "image_sha256": path_report["image"]["sha256"],
            "ghidra_sha256sums_sha256": correlation["corpus"]["sha256sums_sha256"],
            "flash_plan_sha256": PLAN_SHA256,
            "function_map_manifests": EXPECTED_MANIFEST_FILES,
        },
        "reconciliation": {
            "corpus_functions": len(functions),
            "path_anchored_functions": len(anchored),
            "unanchored_functions": len(unanchored),
            "unanchored_official_opaque_bytes": official_total,
            "origin_accounting_unanchored_bytes": EXPECTED_UNANCHORED_OFFICIAL_BYTES,
            "oversized_rejected_envelopes": len(oversized),
        },
        "limitations": [
            "function-level buckets are provider-family triage, not per-function source ownership or pristine-body claims",
            "call-topology and link-order tiers are heuristic evidence; only manifest and string-signature tiers are reviewed classifications",
            "official opaque bytes count flash-plan official_blob bytes inside accepted envelopes; envelope shape is a Ghidra analyzer artifact",
            "rejected oversized envelopes stay in the origin accounting's outside-envelope bucket and are not per-byte classified here",
        ],
        "buckets": bucket_rows,
        "functions": records,
    }


BUCKETS_TSV_HEADER = (
    "bucket\tfunctions\taccepted_envelope_bytes\tofficial_opaque_bytes\t"
    "evidence_classes\tconfidence\townership_category\tlabel"
)
FUNCTIONS_TSV_HEADER = (
    "entry\tbody_start\tbody_end_exclusive\tenvelope_bytes\t"
    "official_opaque_bytes\tbucket\tevidence\tconfidence\tdetail"
)


def buckets_tsv(report: dict[str, Any]) -> str:
    lines = [
        "# G2 Apollo unanchored-function provenance census; regenerated by "
        "tools/analyze_g2_apollo_unanchored_census.py",
        BUCKETS_TSV_HEADER,
    ]
    for bucket in report["buckets"]:
        evidence = "|".join(
            f"{name}={count}" for name, count in bucket["evidence_classes"].items()
        )
        confidence = "|".join(
            f"{name}={count}" for name, count in bucket["confidence"].items()
        )
        lines.append(
            "\t".join(
                (
                    bucket["bucket"],
                    str(bucket["functions"]),
                    str(bucket["accepted_envelope_bytes"]),
                    str(bucket["official_opaque_bytes"]),
                    evidence,
                    confidence,
                    bucket["ownership_category"],
                    bucket["label"],
                )
            )
        )
    return "\n".join(lines) + "\n"


def functions_tsv(report: dict[str, Any]) -> str:
    lines = [
        "# G2 Apollo unanchored-function provenance census; regenerated by "
        "tools/analyze_g2_apollo_unanchored_census.py",
        FUNCTIONS_TSV_HEADER,
    ]
    for record in report["functions"]:
        lines.append(
            "\t".join(
                (
                    f"0x{record['entry']:08X}",
                    f"0x{record['body_start']:08X}",
                    f"0x{record['body_end_exclusive']:08X}",
                    str(record["envelope_bytes"]),
                    str(record["official_opaque_bytes"]),
                    record["bucket"],
                    record["evidence"],
                    record["confidence"],
                    record["detail"],
                )
            )
        )
    return "\n".join(lines) + "\n"


def _text(report: dict[str, Any]) -> str:
    reconciliation = report["reconciliation"]
    lines = [
        "G2 Apollo unanchored-function provenance census: PASS",
        f"  corpus functions: {reconciliation['corpus_functions']}",
        f"  path-anchored: {reconciliation['path_anchored_functions']}",
        f"  unanchored: {reconciliation['unanchored_functions']}",
        "  unanchored official opaque bytes: "
        f"{reconciliation['unanchored_official_opaque_bytes']}",
        f"  oversized rejected envelopes: {reconciliation['oversized_rejected_envelopes']}",
        "  buckets:",
    ]
    for bucket in report["buckets"]:
        lines.append(
            f"    {bucket['bucket']}: {bucket['functions']} functions, "
            f"{bucket['official_opaque_bytes']} official bytes, "
            f"confidence {bucket['confidence']}"
        )
    lines.append("hardware/flash operations: none")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ghidra-corpus", type=Path, required=True)
    parser.add_argument("--manifests", type=Path, default=MANIFESTS)
    parser.add_argument("--flash-plan", type=Path, default=DEFAULT_PLAN)
    parser.add_argument("--component-report", type=Path, default=DEFAULT_COMPONENT_REPORT)
    parser.add_argument("--json", action="store_true")
    parser.add_argument(
        "--write-manifests",
        type=Path,
        metavar="DIRECTORY",
        help="write g2-apollo-unanchored-census-{buckets,functions}.tsv into DIRECTORY",
    )
    args = parser.parse_args()
    report = analyze(
        args.ghidra_corpus,
        manifests_dir=args.manifests,
        plan_path=args.flash_plan,
        component_report_path=args.component_report,
    )
    if args.write_manifests is not None:
        directory = args.write_manifests
        directory.mkdir(parents=True, exist_ok=True)
        (directory / "g2-apollo-unanchored-census-buckets.tsv").write_text(
            buckets_tsv(report), encoding="utf-8"
        )
        (directory / "g2-apollo-unanchored-census-functions.tsv").write_text(
            functions_tsv(report), encoding="utf-8"
        )
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(_text(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
