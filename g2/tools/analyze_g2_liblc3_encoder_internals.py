#!/usr/bin/env python3
"""liblc3 encoder-internals census of the 0x59xxxx no-evidence frontier.

The Apollo unanchored-function provenance census
(``analyze_g2_apollo_unanchored_census.py``) buckets 10 functions (1,694
official bytes) as the Google liblc3 v1.1.3-era encoder via four documented
public entries, and leaves 62 no-evidence functions (17,874 official bytes)
in the ``0x59xxxx`` region hypothesized as encoder internals below those
entries.  This analyzer extends the attribution inward through the
``lc3_encode`` dispatch graph, against the admitted byte-authenticated
liblc3 v1.1.3 snapshot under ``third_party/liblc3``.

Scope is exactly 72 functions: the 62-function ``0x59xxxx`` no-evidence
frontier plus the 10-function parent-census liblc3 bucket.  Eight further
functions that the dispatch graph reaches outside that scope (the
``0x43xxxx`` ltpf/bits cluster, ``lc3_hr_setup_encoder`` at 0x0059123A, and
``lc3_tns_analyze`` at 0x0059AA84, both parent-bucketed ``first-party``)
are recorded as out-of-scope observations only; this analyzer never
re-buckets the parent census.

Evidence tiers, applied in strict priority order; every in-scope function
gets exactly one status, module, evidence class, and confidence level:

1. ``documented-public-entry`` (high) -- the four public entries named by
   the authenticated ``g2-liblc3-public-entry-map.tsv``.
2. ``documented-internal-tail`` (high) -- an in-scope function named by
   address in the entry-map qualification text (``lc3_hr_frame_bytes``).
3. ``loader-table-entry`` (high) -- the four PCM-format loader functions
   whose Thumb pointers are stored, byte-verified against the image, in
   ``lc3_encode``'s static ``load[]`` dispatch table.
4. ``upstream-table-match`` (high) -- the function's literal-pool cells
   point (directly, or through one pointer indirection) into a table that
   matches a vendored-snapshot C array byte-for-byte and is private to
   exactly one liblc3 module.  Multi-module conflicts fail closed.
5. ``dispatch-graph-direct`` (medium) -- a direct static callee of
   ``lc3_encode`` whose position in the decompiled call sequence matches
   the fixed v1.1.3 ``analyze()``/``encode()`` source order in ``lc3.c``.
6. ``dispatch-graph-indirect`` (low) -- reachable only through tier-4/5
   internals; the liblc3-side caller set must match the pinned expectation.
7. ``investigation-required`` (none) -- no admissible liblc3 evidence; a
   deterministic hypothesis is recorded from the external caller families.

Corroborating pins: the documented SNS ``FLT_MAX`` discriminator from
``g2-liblc3-source-boundary.tsv`` must exist in the image and be referenced
by the SNS analysis function.  Shared liblc3 characteristics tables never
confer module attribution alone.

The analyzer is read-only and deterministic.  It re-derives the frontier
from the parent census (authenticated image, corpus, and manifests) on
every run; any drift in the 62/17,874 frontier, the 10/1,694 bucket, the
loader table, the dispatch order, the table census, the caller sets, or
the pinned attribution map raises ``CensusError``.
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
from collections import defaultdict
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PARENT_ANALYZER = ROOT / "tools/analyze_g2_apollo_unanchored_census.py"
MANIFESTS = ROOT / "tools/manifests"
SNAPSHOT = ROOT / "third_party/liblc3"
SOURCE_BOUNDARY = MANIFESTS / "g2-liblc3-source-boundary.tsv"

FRONTIER_BASE = 0x00590000
FRONTIER_END = 0x005A0000
EXPECTED_FRONTIER_FUNCTIONS = 62
EXPECTED_FRONTIER_OFFICIAL_BYTES = 17_874
EXPECTED_LIBLC3_BUCKET_FUNCTIONS = 10
EXPECTED_LIBLC3_BUCKET_OFFICIAL_BYTES = 1_694
EXPECTED_SCOPE_FUNCTIONS = 72
EXPECTED_EXTERNAL_OBSERVATIONS = 8
EXPECTED_TABLES_PARSED = 88
EXPECTED_TABLES_LOCATED = 84

# Snapshot sources parsed for constant tables.  Each file must be covered
# by the admitted SNAPSHOT.sha256 manifest; verification fails closed.
TABLE_SOURCES = (
    "tables.c",
    "sns.c",
    "spec.c",
    "tns.c",
    "mdct.c",
    "bwdet.c",
    "attdet.c",
    "energy.c",
    "ltpf.c",
    "bits.c",
    "lc3.c",
)

# Minimum byte length for a parsed array to be used as a byte-match needle.
MIN_TABLE_BYTES = 16

# Module-private table ownership.  A table confers module attribution only
# when exactly one rule claims it; everything else is shared liblc3-common
# evidence that never attributes a module by itself.
TABLE_MODULE_RULES = (
    ("sns", ("sns.c:", "tables.c:lc3_sns_")),
    ("tns", ("tns.c:", "tables.c:lc3_tns_")),
    ("spec", ("spec.c:", "tables.c:lc3_spectrum_")),
    ("mdct", ("tables.c:mdct_win_", "tables.c:mdct_rot_", "tables.c:fft_")),
    ("ltpf", ("ltpf.c:",)),
)

# The ordered in-frontier static callees of lc3_encode, in decompiled call
# order.  The v1.1.3 lc3.c source fixes this sequence: analyze() runs
# attdet, [ltpf, memmove -- out of frontier], mdct, energy, bwdet, sns,
# tns, spec; encode() runs [bits setup -- out of frontier], bwdet put_bw,
# spec put_side, tns put_data, [pitch bit], sns put_data, [ltpf put_data],
# spec encode.  The corpus call sequence must match exactly.  0x0059AA84
# (lc3_tns_analyze) sits outside the no-evidence frontier: the parent
# census bucketed it first-party via call topology.
EXPECTED_DISPATCH = (
    (0x00598284, "attdet", "lc3_attdet_run"),
    (0x00598AB8, "mdct", "lc3_mdct_forward"),
    (0x00598DEC, "energy", "lc3_energy_compute"),
    (0x00598F14, "bwdet", "lc3_bwdet_run"),
    (0x00599714, "sns", "lc3_sns_analyze"),
    (0x0059AA84, "tns", "lc3_tns_analyze"),
    (0x0059BAE4, "spec", "lc3_spec_analyze"),
    (0x00599080, "bwdet", "lc3_bwdet_put_bw"),
    (0x0059C1C4, "spec", "lc3_spec_put_side"),
    (0x0059B5C4, "tns", "lc3_tns_put_data"),
    (0x0059A910, "sns", "lc3_sns_put_data"),
    (0x0059C204, "spec", "lc3_spec_encode"),
)

# Out-of-frontier static callees of lc3_encode, in decompiled call order.
# Observations only; they are outside this census scope.
EXPECTED_EXTERNAL_DISPATCH = (
    (0x00438FB8, "ltpf", "lc3_ltpf_analyse (ltpf.c, linked in the 0x43xxxx cluster)"),
    (0x00439710, None, "IAR memmove (compiler runtime, not liblc3)"),
    (0x00439868, "bits", "lc3_setup_bits (bits.c, 0x43xxxx cluster)"),
    (0x00439B12, "bits", "lc3_put_bits slow path (bits.c, 0x43xxxx cluster)"),
    (0x004396C2, "ltpf", "lc3_ltpf_put_data (ltpf.c, 0x43xxxx cluster)"),
    (0x004399E4, "bits", "lc3_flush_bits (bits.c, 0x43xxxx cluster)"),
)

# PCM loader table names in LC3_PCM_FORMAT enum order (lc3.h).
LOADER_NAMES = ("load_s16", "load_s24", "load_s24_3le", "load_float")

# lc3_hr_frame_bytes at 0x00590F68 is named by address in the entry-map
# qualification text.  lc3_hr_setup_encoder at 0x0059123A is documented the
# same way but sits outside the census scope (parent bucket first-party).
EXPECTED_DOCUMENTED_INTERNAL = 0x00590F68
EXPECTED_EXTERNAL_DOCUMENTED = (0x0059123A,)

# Indirect internals: in-frontier functions reachable only through the
# dispatch tier.  The pinned liblc3-side caller set of each must match the
# corpus exactly.  The table tier may still override the evidence class.
EXPECTED_INDIRECT = (
    (0x0059845C, "mdct", (0x00598AB8,),
     "mdct.c FFT core candidate (radix-3 divide constants in literal pool)"),
    (0x0059898C, "mdct", (0x00598AB8,),
     "mdct.c vector scale helper (partially decoded MVE/Helium body)"),
    (0x00599050, "bwdet", (0x00599080, 0x0059BAE4),
     "lc3_bwdet_get_nbits candidate (shared bwdet/spec bit-budget helper)"),
    (0x005990CC, "bits", (0x0059A910,),
     "lc3_put_bits out-of-line clone; overflow tail-calls 0x00439B12 bits slow path"),
    (0x00599328, "sns", (0x00599714,),
     "sns.c compute_scale_factors candidate (shares lc3_num_bands users with energy.c)"),
    (0x0059A9C8, "bits", (0x0059B5C4,),
     "lc3_put_symbol arithmetic-coder clone; tail-calls 0x00439B54 carry helper"),
    (0x0059AA00, "tns", (0x0059AA84,),
     "tns.c quantize/unquantize helper; 6-byte Ghidra entry overlapping 0x0059AA06"),
    (0x0059B6A0, None, (0x0059B6D0, 0x0059B76C, 0x0059B80C, 0x0059B852),
     "lc3_hr(sr) out-of-line clone (common.h header inline; no owning object)"),
    (0x0059B6AC, "bits", (0x0059C1C4, 0x0059C204),
     "lc3_put_bits out-of-line clone; overflow tail-calls 0x00439B12 bits slow path"),
    (0x0059B6D0, "spec", (0x0059BAE4,), "spec.c estimate_gain candidate"),
    (0x0059B714, "spec", (0x0059B76C,),
     "spec.c unquantize_gain candidate (local iq literal pool near 0x0059C248)"),
    (0x0059B76C, "spec", (0x0059BAE4,), "spec.c adjust_gain candidate"),
    (0x0059B80C, "spec", (0x0059B852,), "spec.c compute_nbits sub-mode helper candidate"),
    (0x0059BA96, "spec", (0x0059BAE4, 0x0059C1C4),
     "spec.c side-information bit-accounting helper candidate"),
)

# Bucket-member internals (lc3.c) attributed through the dispatch graph.
# 0x0059123A (documented lc3_hr_setup_encoder) is an allowed out-of-scope
# caller of the resolve helpers.
EXPECTED_LC3_INTERNALS = (
    (0x00590E6C, "lc3", (0x00590F68,),
     "lc3_hr_frame_block_bytes candidate (called by documented lc3_hr_frame_bytes)"),
    (0x00590D3C, "lc3", (0x00590E6C, 0x0059123A),
     "resolve_dt candidate (shared by hr_frame_block_bytes and hr_setup_encoder)"),
    (0x00590D74, "lc3", (0x00590E6C, 0x0059123A),
     "resolve_srate candidate (shared by hr_frame_block_bytes and hr_setup_encoder)"),
)

# Module-private table evidence, pinned per function: the exact set of
# vendored-snapshot tables ("<source>:<name>") each function's pointer
# cells must hit, and the module they imply.
EXPECTED_TABLE_EVIDENCE = {
    0x005990F0: (
        "sns",
        ("sns.c:dct16_m", "tables.c:lc3_sns_hfcb", "tables.c:lc3_sns_lfcb"),
        "sns.c scale-factor VQ quantize unit (dct16 + lfcb/hfcb codebooks)",
    ),
    0x00599290: (
        "sns",
        ("tables.c:lc3_sns_mpvq_offsets",),
        "sns.c MPVQ gain/shape quantization unit (mpvq offset table)",
    ),
    0x00599714: (
        "sns",
        ("sns.c:dct16_m", "tables.c:lc3_sns_hfcb"),
        "lc3_sns_analyze (inlined scale-factor path; FLT_MAX quantization pin)",
    ),
    0x0059B4B8: (
        "tns",
        ("tables.c:lc3_tns_coeffs_bits", "tables.c:lc3_tns_order_bits"),
        "lc3_tns_get_nbits (tns arithmetic-coding bit tables)",
    ),
    0x0059B852: (
        "spec",
        ("tables.c:lc3_spectrum_bits", "tables.c:lc3_spectrum_lookup"),
        "spec.c compute_nbits (spectrum arithmetic-coding tables)",
    ),
    0x0059C204: (
        "spec",
        ("tables.c:lc3_spectrum_lookup",),
        "lc3_spec_encode (spectrum symbol lookup table)",
    ),
}

# The whole 72-row attribution result, pinned.  Any derived drift raises.
# entry -> (status, module, evidence, confidence)
EXPECTED_ATTRIBUTION = {
    0x00590E64: ("module", "lc3", "documented-public-entry", "high"),
    0x00590F78: ("module", "lc3", "documented-public-entry", "high"),
    0x00591374: ("module", "lc3", "documented-public-entry", "high"),
    0x0059138A: ("module", "lc3", "documented-public-entry", "high"),
    0x00590F68: ("module", "lc3", "documented-internal-tail", "high"),
    0x00590F84: ("module", "lc3", "loader-table-entry", "high"),
    0x00591060: ("module", "lc3", "loader-table-entry", "high"),
    0x0059112E: ("module", "lc3", "loader-table-entry", "high"),
    0x005911B0: ("module", "lc3", "loader-table-entry", "high"),
    0x00599714: ("module", "sns", "upstream-table-match", "high"),
    0x005990F0: ("module", "sns", "upstream-table-match", "high"),
    0x00599290: ("module", "sns", "upstream-table-match", "high"),
    0x0059B4B8: ("module", "tns", "upstream-table-match", "high"),
    0x0059B852: ("module", "spec", "upstream-table-match", "high"),
    0x0059C204: ("module", "spec", "upstream-table-match", "high"),
    0x00598284: ("module", "attdet", "dispatch-graph-direct", "medium"),
    0x00598AB8: ("module", "mdct", "dispatch-graph-direct", "medium"),
    0x00598DEC: ("module", "energy", "dispatch-graph-direct", "medium"),
    0x00598F14: ("module", "bwdet", "dispatch-graph-direct", "medium"),
    0x00599080: ("module", "bwdet", "dispatch-graph-direct", "medium"),
    0x0059A910: ("module", "sns", "dispatch-graph-direct", "medium"),
    0x0059B5C4: ("module", "tns", "dispatch-graph-direct", "medium"),
    0x0059BAE4: ("module", "spec", "dispatch-graph-direct", "medium"),
    0x0059C1C4: ("module", "spec", "dispatch-graph-direct", "medium"),
    0x0059845C: ("module", "mdct", "dispatch-graph-indirect", "low"),
    0x0059898C: ("module", "mdct", "dispatch-graph-indirect", "low"),
    0x00599050: ("module", "bwdet", "dispatch-graph-indirect", "low"),
    0x005990CC: ("module", "bits", "dispatch-graph-indirect", "low"),
    0x00599328: ("module", "sns", "dispatch-graph-indirect", "low"),
    0x0059A9C8: ("module", "bits", "dispatch-graph-indirect", "low"),
    0x0059AA00: ("module", "tns", "dispatch-graph-indirect", "low"),
    0x0059B6A0: ("cluster", None, "dispatch-graph-indirect", "low"),
    0x0059B6AC: ("module", "bits", "dispatch-graph-indirect", "low"),
    0x0059B6D0: ("module", "spec", "dispatch-graph-indirect", "low"),
    0x0059B714: ("module", "spec", "dispatch-graph-indirect", "low"),
    0x0059B76C: ("module", "spec", "dispatch-graph-indirect", "low"),
    0x0059B80C: ("module", "spec", "dispatch-graph-indirect", "low"),
    0x0059BA96: ("module", "spec", "dispatch-graph-indirect", "low"),
    0x00590E6C: ("module", "lc3", "dispatch-graph-indirect", "low"),
    0x00590D3C: ("module", "lc3", "dispatch-graph-indirect", "low"),
    0x00590D74: ("module", "lc3", "dispatch-graph-indirect", "low"),
}

EXPECTED_ATTRIBUTED_FUNCTIONS = 41
EXPECTED_ATTRIBUTED_OFFICIAL_BYTES = 16_128
EXPECTED_INVESTIGATION_FUNCTIONS = 31
EXPECTED_INVESTIGATION_OFFICIAL_BYTES = 3_440

# Per-module roll-up over the 72-function scope (attributed rows only).
# module -> (functions, official_opaque_bytes)
EXPECTED_MODULE_SUMMARY = {
    "lc3": (12, 1_834),
    "attdet": (1, 468),
    "mdct": (3, 2_122),
    "energy": (1, 270),
    "bwdet": (3, 414),
    "sns": (5, 6_240),
    "tns": (3, 460),
    "spec": (9, 4_180),
    "bits": (3, 128),
}

MODULES = ("lc3", "attdet", "bwdet", "energy", "mdct", "sns", "tns", "spec", "bits")
EVIDENCE_CLASSES = (
    "documented-public-entry",
    "documented-internal-tail",
    "loader-table-entry",
    "upstream-table-match",
    "dispatch-graph-direct",
    "dispatch-graph-indirect",
    "dispatch-graph-external",
    "none",
)
CONFIDENCE_ORDER = ("high", "medium", "low", "none")

FUNCTION_BEGIN_RE = re.compile(
    r"OPENCFW_FUNCTION_BEGIN entry=([0-9a-f]+) "
    r"body_start=([0-9a-f]+) body_end=([0-9a-f]+) name=(\S+)",
    re.IGNORECASE,
)
FUNCTION_END_RE = re.compile(r"OPENCFW_FUNCTION_END entry=([0-9a-f]+)", re.IGNORECASE)
CALL_RE = re.compile(r"\bFUN_([0-9a-f]{8})\s*\(")
PTR_TABLE_RE = re.compile(r"\bPTR_FUN_([0-9a-f]{8})_1_([0-9a-f]{8})")
DAT_RE = re.compile(r"\bDAT_([0-9a-f]{8})")
QUALIFICATION_ADDR_RE = re.compile(r"\b([A-Za-z_]\w*) at (0x[0-9A-Fa-f]{8})\b")

TABLE_DECL_RE = re.compile(
    r"(?:static\s+)?const\s+"
    r"(float|int32_t|uint16_t|uint8_t|int16_t|int)\s+"
    r"(\w+)((?:\s*\[[^\]]*\])+)\s*=\s*\{"
)
C_COMMENT_RE = re.compile(r"/\*.*?\*/", re.DOTALL)
LINE_COMMENT_RE = re.compile(r"//[^\n]*")
FLOAT_TOKEN_RE = re.compile(r"[+-]?(\d+\.?\d*|\.\d+)([eE][+-]?\d+)?")
INT_TOKEN_RE = re.compile(r"[+-]?(0x[0-9a-fA-F]+|\d+)[uUlL]*")

TYPE_FORMAT = {
    "float": "f",
    "int32_t": "i",
    "int": "i",
    "uint16_t": "H",
    "int16_t": "h",
    "uint8_t": "B",
}

MAP_TSV_HEADER = (
    "entry\tbody_start\tbody_end_exclusive\tenvelope_bytes\t"
    "official_opaque_bytes\tscope\tparent_bucket\tstatus\tmodule\t"
    "attribution\tevidence\tconfidence\tdetail"
)


class CensusError(RuntimeError):
    """Raised when authenticated evidence or a closed census changes."""


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _load_parent():
    spec = importlib.util.spec_from_file_location(
        "apollo_unanchored_census_for_liblc3", PARENT_ANALYZER
    )
    if spec is None or spec.loader is None:
        raise CensusError(f"cannot load {PARENT_ANALYZER}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def parse_corpus(logs: list[Path]) -> dict[int, dict[str, Any]]:
    """Per-function ordered static calls, dispatch-table labels, DAT refs."""

    functions: dict[int, dict[str, Any]] = {}
    current: dict[str, Any] | None = None
    for log in logs:
        for line in log.read_text(encoding="utf-8", errors="strict").splitlines():
            begin = FUNCTION_BEGIN_RE.search(line)
            if begin:
                current = {
                    "entry": int(begin.group(1), 16),
                    "calls_ordered": [],
                    "dat_refs": set(),
                    "ptr_tables": set(),
                }
                functions[current["entry"]] = current
                continue
            if FUNCTION_END_RE.search(line):
                current = None
                continue
            if current is not None:
                current["calls_ordered"].extend(
                    int(token, 16) for token in CALL_RE.findall(line)
                )
                current["dat_refs"].update(
                    int(token, 16) for token in DAT_RE.findall(line)
                )
                current["ptr_tables"].update(
                    (int(target, 16), int(table, 16))
                    for target, table in PTR_TABLE_RE.findall(line)
                )
    return functions


def caller_map(functions: dict[int, dict[str, Any]]) -> dict[int, set[int]]:
    callers: dict[int, set[int]] = defaultdict(set)
    for entry, row in functions.items():
        for target in dict.fromkeys(row["calls_ordered"]):
            if target != entry:
                callers[target].add(entry)
    return callers


def verify_snapshot_files(snapshot: Path, names: tuple[str, ...]) -> None:
    """Every parsed snapshot source must hash to the admitted manifest."""

    manifest_path = snapshot / "SNAPSHOT.sha256"
    if not manifest_path.is_file():
        raise CensusError("missing liblc3 SNAPSHOT.sha256")
    recorded: dict[str, str] = {}
    for line in manifest_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            digest, _, name = line.partition("  ")
            recorded[name] = digest
    for name in names:
        relative = f"src/{name}"
        path = snapshot / "src" / name
        if relative not in recorded:
            raise CensusError(f"snapshot manifest lacks {relative}")
        if not path.is_file():
            raise CensusError(f"missing snapshot source {relative}")
        if _sha256_bytes(path.read_bytes()) != recorded[relative]:
            raise CensusError(f"snapshot source drifted: {relative}")


def _parse_array_body(element_type: str, body: str) -> bytes | None:
    tokens = [
        token.strip()
        for token in re.sub(r"[{}]", " ", body).split(",")
        if token.strip()
    ]
    if not tokens:
        return None
    values = []
    for token in tokens:
        if element_type == "float":
            text = token.rstrip("fF")
            if not FLOAT_TOKEN_RE.fullmatch(text):
                return None
            values.append(float(text))
        else:
            if not INT_TOKEN_RE.fullmatch(token):
                return None
            values.append(int(token.rstrip("uUlL"), 0))
    fmt = "<" + TYPE_FORMAT[element_type] * len(values)
    try:
        return struct.pack(fmt, *values)
    except struct.error:
        return None


def parse_snapshot_tables(snapshot: Path) -> dict[str, bytes]:
    """Parse flat scalar C arrays from the vendored snapshot sources.

    Arrays with expressions, designated initializers, or pointer members
    are skipped by construction (their tokens fail the scalar grammar).
    """

    verify_snapshot_files(snapshot, TABLE_SOURCES)
    tables: dict[str, bytes] = {}
    for name in TABLE_SOURCES:
        text = (snapshot / "src" / name).read_text(encoding="utf-8")
        text = C_COMMENT_RE.sub(" ", text)
        text = LINE_COMMENT_RE.sub(" ", text)
        for match in TABLE_DECL_RE.finditer(text):
            element_type, table_name = match.group(1), match.group(2)
            depth = 1
            cursor = match.end()
            start = cursor
            while cursor < len(text) and depth:
                char = text[cursor]
                if char == "{":
                    depth += 1
                elif char == "}":
                    depth -= 1
                cursor += 1
            data = _parse_array_body(element_type, text[start : cursor - 1])
            if data is not None and len(data) >= MIN_TABLE_BYTES:
                key = f"{name}:{table_name}"
                if key in tables:
                    raise CensusError(f"duplicate parsed table {key}")
                tables[key] = data
    if not tables:
        raise CensusError("no snapshot tables parsed")
    return tables


def table_module(key: str) -> str | None:
    """Owning liblc3 module for a table, or None for shared tables."""

    matches = [
        module
        for module, prefixes in TABLE_MODULE_RULES
        if any(key.startswith(prefix) for prefix in prefixes)
    ]
    if len(matches) > 1:
        raise CensusError(f"table module rules overlap on {key}")
    return matches[0] if matches else None


def locate_tables(blob: bytes, load_base: int, tables: dict[str, bytes]) -> dict[str, int]:
    """Uniquely byte-matched snapshot tables in the official image."""

    located: dict[str, int] = {}
    for key, data in sorted(tables.items()):
        if blob.count(data) == 1:
            located[key] = load_base + blob.find(data)
    return located


def _word(blob: bytes, load_base: int, address: int) -> int | None:
    offset = address - load_base
    if 0 <= offset <= len(blob) - 4:
        return struct.unpack_from("<I", blob, offset)[0]
    return None


def extract_table_evidence(
    entry: int,
    functions: dict[int, dict[str, Any]],
    spans: list[tuple[int, int, str, str | None]],
    blob: bytes,
    load_base: int,
) -> tuple[set[str], set[str]]:
    """(private table keys, shared table keys) referenced by a function.

    A reference is a decompiled ``DAT_`` cell whose address falls inside a
    located table, or whose stored 32-bit word points inside one.
    """

    private_hits: set[str] = set()
    shared_hits: set[str] = set()
    for ref in sorted(functions[entry]["dat_refs"]):
        candidates = [ref]
        value = _word(blob, load_base, ref)
        if value is not None:
            candidates.append(value)
        for candidate in candidates:
            for start, end, key, module in spans:
                if start <= candidate < end:
                    (private_hits if module else shared_hits).add(key)
    return private_hits, shared_hits


def load_source_boundary(path: Path = SOURCE_BOUNDARY) -> dict[str, str]:
    if not path.is_file():
        raise CensusError(f"missing {path.name}")
    lines = [
        line
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    reader = csv.DictReader(lines, delimiter="\t")
    if list(reader.fieldnames or ()) != ["metric", "value"]:
        raise CensusError(f"unknown source-boundary schema: {reader.fieldnames!r}")
    return {row["metric"]: row["value"] for row in reader}


def load_entry_map_qualifications(parent, manifests_dir: Path) -> dict[int, str]:
    """Internal functions named by address in entry-map qualifications."""

    path = manifests_dir / "g2-liblc3-public-entry-map.tsv"
    if not path.is_file():
        raise CensusError(f"missing {path.name}")
    lines = [
        line
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.startswith("#")
    ]
    reader = csv.DictReader(lines, delimiter="\t")
    if "qualification" not in (reader.fieldnames or ()):
        raise CensusError("entry map lacks a qualification column")
    named: dict[int, str] = {}
    for row in reader:
        for function_name, address_text in QUALIFICATION_ADDR_RE.findall(
            row.get("qualification") or ""
        ):
            named[int(address_text, 16)] = function_name
    return named


def _ordered_unique(values: list[int]) -> list[int]:
    return list(dict.fromkeys(values))


def analyze(
    corpus_root: Path,
    manifests_dir: Path = MANIFESTS,
    snapshot_dir: Path = SNAPSHOT,
) -> dict[str, Any]:
    parent = _load_parent()
    parent_report = parent.analyze(corpus_root=corpus_root, manifests_dir=manifests_dir)
    path_module = parent._load_path_analyzer()
    load_base = path_module.LOAD_BASE
    blob = path_module.DEFAULT_IMAGE.read_bytes()

    parent_records = {row["entry"]: row for row in parent_report["functions"]}

    # --- Scope derivation: the 0x59xxxx no-evidence frontier + liblc3 bucket.
    frontier = {
        entry: row
        for entry, row in parent_records.items()
        if row["bucket"] == "investigation-required-no-evidence"
        and FRONTIER_BASE <= entry < FRONTIER_END
    }
    if len(frontier) != EXPECTED_FRONTIER_FUNCTIONS:
        raise CensusError(
            f"0x59xxxx no-evidence frontier changed: {len(frontier)} != "
            f"{EXPECTED_FRONTIER_FUNCTIONS}"
        )
    frontier_bytes = sum(row["official_opaque_bytes"] for row in frontier.values())
    if frontier_bytes != EXPECTED_FRONTIER_OFFICIAL_BYTES:
        raise CensusError(
            f"frontier official bytes changed: {frontier_bytes} != "
            f"{EXPECTED_FRONTIER_OFFICIAL_BYTES}"
        )
    bucket = {
        entry: row for entry, row in parent_records.items() if row["bucket"] == "liblc3"
    }
    if len(bucket) != EXPECTED_LIBLC3_BUCKET_FUNCTIONS:
        raise CensusError(
            f"liblc3 bucket changed: {len(bucket)} != {EXPECTED_LIBLC3_BUCKET_FUNCTIONS}"
        )
    bucket_bytes = sum(row["official_opaque_bytes"] for row in bucket.values())
    if bucket_bytes != EXPECTED_LIBLC3_BUCKET_OFFICIAL_BYTES:
        raise CensusError(
            f"liblc3 bucket official bytes changed: {bucket_bytes} != "
            f"{EXPECTED_LIBLC3_BUCKET_OFFICIAL_BYTES}"
        )
    scope = {**frontier, **bucket}
    if len(scope) != EXPECTED_SCOPE_FUNCTIONS:
        raise CensusError("frontier and liblc3 bucket overlap; scope changed")

    # --- Corpus call graph.
    logs = path_module.verify_corpus(corpus_root)
    functions = parse_corpus(logs)
    callers = caller_map(functions)

    # --- Public entries and documented internals from the entry map.
    public_entries = parent.load_liblc3_entries(manifests_dir)
    lc3_encode = next(
        address for address, name in public_entries.items() if name == "lc3_encode"
    )
    named_internals = load_entry_map_qualifications(parent, manifests_dir)
    in_scope_documented = {
        address: name
        for address, name in named_internals.items()
        if address in scope and address not in public_entries
    }
    if tuple(sorted(in_scope_documented)) != (EXPECTED_DOCUMENTED_INTERNAL,):
        raise CensusError(
            "documented internal census changed: "
            + ", ".join(f"0x{a:08x}" for a in sorted(in_scope_documented))
        )
    external_documented = tuple(
        sorted(
            address
            for address in named_internals
            if address not in scope and address in functions
        )
    )
    if external_documented != EXPECTED_EXTERNAL_DOCUMENTED:
        raise CensusError(
            "external documented internal census changed: "
            + ", ".join(f"0x{a:08x}" for a in external_documented)
        )

    # --- lc3_encode dispatch sequence.  The decompiled signature line
    # self-matches the call regex, so the entry itself is excluded.  The
    # dispatch universe adds 0x0059AA84 (lc3_tns_analyze), which the parent
    # census bucketed first-party: it is verified here but only recorded as
    # an external observation, never re-bucketed.
    dispatch_universe = set(scope) | {0x0059AA84}
    encode_calls = [
        target
        for target in _ordered_unique(functions[lc3_encode]["calls_ordered"])
        if target != lc3_encode
    ]
    dispatch_observed = [target for target in encode_calls if target in dispatch_universe]
    dispatch_expected = [entry for entry, _module, _name in EXPECTED_DISPATCH]
    if dispatch_observed != dispatch_expected:
        raise CensusError(
            "lc3_encode dispatch sequence changed: "
            + ", ".join(f"0x{t:08x}" for t in dispatch_observed)
        )
    external_observed = [
        target
        for target in encode_calls
        if target not in dispatch_universe and target in functions
    ]
    external_expected = [entry for entry, _module, _name in EXPECTED_EXTERNAL_DISPATCH]
    if external_observed != external_expected:
        raise CensusError(
            "lc3_encode external dispatch sequence changed: "
            + ", ".join(f"0x{t:08x}" for t in external_observed)
        )

    # --- PCM loader dispatch table, byte-verified against the image.
    ptr_tables = functions[lc3_encode]["ptr_tables"]
    if len(ptr_tables) != 1:
        raise CensusError(f"lc3_encode dispatch-table labels changed: {ptr_tables!r}")
    first_target, table_address = next(iter(ptr_tables))
    loader_targets = []
    for index in range(len(LOADER_NAMES)):
        word = _word(blob, load_base, table_address + 4 * index)
        if word is None or not word & 1 or (word & ~1) not in functions:
            raise CensusError(
                f"loader table entry {index} at 0x{table_address + 4 * index:08X} "
                "is not a Thumb function pointer"
            )
        loader_targets.append(word & ~1)
    if loader_targets[0] != first_target:
        raise CensusError("loader table label disagrees with its first entry")
    following = _word(blob, load_base, table_address + 4 * len(LOADER_NAMES))
    if following is not None and following & 1 and (following & ~1) in functions:
        raise CensusError("loader table grew beyond the LC3_PCM_FORMAT count")
    if any(target not in bucket for target in loader_targets):
        raise CensusError("loader table targets drifted out of the liblc3 bucket")

    # --- Vendored-snapshot tables, byte-matched in the official image.
    parsed_tables = parse_snapshot_tables(snapshot_dir)
    if len(parsed_tables) != EXPECTED_TABLES_PARSED:
        raise CensusError(
            f"snapshot table census changed: {len(parsed_tables)} != "
            f"{EXPECTED_TABLES_PARSED}"
        )
    located = locate_tables(blob, load_base, parsed_tables)
    if len(located) != EXPECTED_TABLES_LOCATED:
        raise CensusError(
            f"located table census changed: {len(located)} != "
            f"{EXPECTED_TABLES_LOCATED}"
        )
    spans = [
        (address, address + len(parsed_tables[key]), key, table_module(key))
        for key, address in sorted(located.items())
    ]
    table_evidence: dict[int, tuple[set[str], set[str]]] = {}
    for entry in scope:
        table_evidence[entry] = extract_table_evidence(
            entry, functions, spans, blob, load_base
        )
    observed_table_evidence = {
        entry: hits for entry, (hits, _shared) in table_evidence.items() if hits
    }
    if set(observed_table_evidence) != set(EXPECTED_TABLE_EVIDENCE):
        raise CensusError(
            "module-private table evidence set changed: "
            + ", ".join(f"0x{e:08x}" for e in sorted(observed_table_evidence))
        )
    for entry, (module, keys, _label) in EXPECTED_TABLE_EVIDENCE.items():
        observed_keys = tuple(sorted(observed_table_evidence[entry]))
        if observed_keys != tuple(sorted(keys)):
            raise CensusError(
                f"table evidence for 0x{entry:08x} changed: {observed_keys!r}"
            )
        modules = {table_module(key) for key in observed_keys}
        if modules != {module}:
            raise CensusError(
                f"table evidence for 0x{entry:08x} spans modules {modules!r}"
            )

    # --- Documented SNS FLT_MAX quantization discriminator.
    boundary = load_source_boundary(manifests_dir / SOURCE_BOUNDARY.name)
    flt_max_address = int(boundary["stock_sns_flt_max_address"], 16)
    flt_max_bits = int(boundary["stock_sns_flt_max_bits"], 16)
    if _word(blob, load_base, flt_max_address) != flt_max_bits:
        raise CensusError("SNS FLT_MAX discriminator missing from the image")
    if flt_max_address not in functions[0x00599714]["dat_refs"]:
        raise CensusError("SNS FLT_MAX literal is no longer referenced by 0x00599714")

    # --- Attribution assembly (72 in-scope rows).
    allowed_callers = (
        set(scope)
        | set(EXPECTED_EXTERNAL_DOCUMENTED)
        | {entry for entry, _m, _n in EXPECTED_DISPATCH}
        | {entry for entry, _m, _n in EXPECTED_EXTERNAL_DISPATCH}
    )
    rows: dict[int, dict[str, Any]] = {}

    def put(entry: int, status, module, evidence, confidence, attribution, detail):
        if entry in rows:
            raise CensusError(f"duplicate attribution for 0x{entry:08x}")
        rows[entry] = {
            "entry": entry,
            "status": status,
            "module": module,
            "evidence": evidence,
            "confidence": confidence,
            "attribution": attribution,
            "detail": detail,
        }

    for address, name in sorted(public_entries.items()):
        put(address, "module", "lc3", "documented-public-entry", "high", name,
            "authenticated by g2-liblc3-public-entry-map.tsv")
    for address, name in sorted(in_scope_documented.items()):
        put(address, "module", "lc3", "documented-internal-tail", "high", name,
            "named by address in the entry-map qualification text")
    for index, target in enumerate(loader_targets):
        put(target, "module", "lc3", "loader-table-entry", "high", LOADER_NAMES[index],
            f"Thumb pointer {index} in lc3_encode's static load[] table at "
            f"0x{table_address:08X}")
    for entry, (module, keys, label) in sorted(EXPECTED_TABLE_EVIDENCE.items()):
        put(entry, "module", module, "upstream-table-match", "high", label,
            "references byte-matched snapshot tables: " + "|".join(sorted(keys)))
    for entry, module, name in EXPECTED_DISPATCH:
        if entry not in scope:
            continue  # 0x0059AA84 lc3_tns_analyze: external observation only.
        if entry in rows:
            # Table-tier winners keep their class; verify module agreement.
            if rows[entry]["module"] != module:
                raise CensusError(
                    f"dispatch/table module conflict at 0x{entry:08x}: "
                    f"{rows[entry]['module']} vs {module}"
                )
            continue
        put(entry, "module", module, "dispatch-graph-direct", "medium", name,
            "direct lc3_encode callee at the v1.1.3 analyze()/encode() source position")
    for entry, module, expected_callers, hypothesis in (
        EXPECTED_INDIRECT + EXPECTED_LC3_INTERNALS
    ):
        if entry in rows:
            continue
        observed = sorted(
            caller for caller in callers.get(entry, ()) if caller in allowed_callers
        )
        if tuple(observed) != tuple(sorted(expected_callers)):
            raise CensusError(
                f"liblc3-side callers of 0x{entry:08x} changed: "
                + ", ".join(f"0x{c:08x}" for c in observed)
            )
        outside = sorted(
            caller for caller in callers.get(entry, ()) if caller not in allowed_callers
        )
        if outside:
            raise CensusError(
                f"0x{entry:08x} gained a non-liblc3 caller: "
                + ", ".join(f"0x{c:08x}" for c in outside)
            )
        status = "module" if module else "cluster"
        put(entry, status, module, "dispatch-graph-indirect", "low", hypothesis,
            "reachable only through liblc3 internals; caller set pinned")
    # Verify caller sets of table-tier functions that sit below the dispatch.
    for entry in (0x005990F0, 0x00599290, 0x0059B4B8, 0x0059B852):
        expected_caller = {
            0x005990F0: 0x00599714,
            0x00599290: 0x00599714,
            0x0059B4B8: 0x0059BAE4,
            0x0059B852: 0x0059BAE4,
        }[entry]
        observed = sorted(callers.get(entry, ()))
        if observed != [expected_caller]:
            raise CensusError(
                f"caller set of table-pinned 0x{entry:08x} changed: "
                + ", ".join(f"0x{c:08x}" for c in observed)
            )

    # Everything left stays investigation-required with a deterministic
    # hypothesis derived from its external caller families.
    for entry in sorted(scope):
        if entry in rows:
            continue
        row = scope[entry]
        external = sorted(callers.get(entry, ()))
        families = sorted(
            {
                parent_records[caller]["bucket"]
                if caller in parent_records
                else "path-anchored"
                for caller in external
            }
        )
        hints = []
        if external:
            hints.append(
                "called only from "
                + ("|".join(families))
                + " functions ("
                + ",".join(f"0x{caller:08X}" for caller in external)
                + ")"
            )
        else:
            hints.append("no static caller in the corpus; possible dead-stripped "
                         "internal or data-adjacent envelope")
        if row["official_opaque_bytes"] == 0:
            hints.append("envelope bytes fully production source-owned")
        hints.append("no liblc3 dispatch-graph or module-table evidence")
        put(entry, "investigation-required", None, "none", "none", "", "; ".join(hints))

    # --- Fail-closed comparison against the pinned attribution map.
    derived = {
        entry: (row["status"], row["module"], row["evidence"], row["confidence"])
        for entry, row in rows.items()
    }
    for entry, expected in EXPECTED_ATTRIBUTION.items():
        if entry not in derived:
            raise CensusError(f"pinned attribution missing for 0x{entry:08x}")
        if derived[entry] != expected:
            raise CensusError(
                f"attribution for 0x{entry:08x} changed: {derived[entry]!r} != "
                f"{expected!r}"
            )
    if set(derived) != scope.keys():
        raise CensusError("attribution rows do not cover the 72-function scope")
    investigation = sorted(set(scope) - set(EXPECTED_ATTRIBUTION))

    # --- Reconciliation.
    def official(entry: int) -> int:
        return scope[entry]["official_opaque_bytes"]

    attributed = sorted(EXPECTED_ATTRIBUTION)
    attributed_bytes = sum(official(entry) for entry in attributed)
    investigation_bytes = sum(official(entry) for entry in investigation)
    if len(attributed) != EXPECTED_ATTRIBUTED_FUNCTIONS:
        raise CensusError("attributed function count changed")
    if attributed_bytes != EXPECTED_ATTRIBUTED_OFFICIAL_BYTES:
        raise CensusError(
            f"attributed official bytes changed: {attributed_bytes} != "
            f"{EXPECTED_ATTRIBUTED_OFFICIAL_BYTES}"
        )
    if len(investigation) != EXPECTED_INVESTIGATION_FUNCTIONS:
        raise CensusError("investigation-required function count changed")
    if investigation_bytes != EXPECTED_INVESTIGATION_OFFICIAL_BYTES:
        raise CensusError(
            f"investigation-required official bytes changed: {investigation_bytes} != "
            f"{EXPECTED_INVESTIGATION_OFFICIAL_BYTES}"
        )
    if attributed_bytes + investigation_bytes != (
        EXPECTED_FRONTIER_OFFICIAL_BYTES + EXPECTED_LIBLC3_BUCKET_OFFICIAL_BYTES
    ):
        raise CensusError("official-byte reconciliation failed")

    module_summary: dict[str, dict[str, int]] = {}
    for entry in attributed:
        module = EXPECTED_ATTRIBUTION[entry][1]
        if module is None:
            continue
        summary = module_summary.setdefault(module, {"functions": 0, "official_bytes": 0})
        summary["functions"] += 1
        summary["official_bytes"] += official(entry)
    observed_summary = {
        module: (summary["functions"], summary["official_bytes"])
        for module, summary in sorted(module_summary.items())
    }
    if observed_summary != EXPECTED_MODULE_SUMMARY:
        raise CensusError(f"module summary changed: {observed_summary!r}")

    # --- Out-of-scope dispatch observations (never re-bucketed here).
    observations = []
    for entry, module, name in EXPECTED_EXTERNAL_DISPATCH:
        observations.append(
            {
                "entry": entry,
                "module": module,
                "attribution": name,
                "evidence": "dispatch-graph-external",
                "confidence": "medium" if module else "low",
                "parent_bucket": parent_records.get(entry, {}).get("bucket")
                if entry in parent_records
                else "outside-unanchored-census",
            }
        )
    for entry in EXPECTED_EXTERNAL_DOCUMENTED:
        observations.append(
            {
                "entry": entry,
                "module": "lc3",
                "attribution": named_internals[entry],
                "evidence": "documented-internal-tail",
                "confidence": "high",
                "parent_bucket": parent_records.get(entry, {}).get("bucket")
                if entry in parent_records
                else "outside-unanchored-census",
            }
        )
    tns_entry = 0x0059AA84
    observations.append(
        {
            "entry": tns_entry,
            "module": "tns",
            "attribution": "lc3_tns_analyze",
            "evidence": "dispatch-graph-direct",
            "confidence": "medium",
            "parent_bucket": parent_records[tns_entry]["bucket"],
        }
    )
    if len(observations) != EXPECTED_EXTERNAL_OBSERVATIONS:
        raise CensusError("external observation census changed")

    # --- Output rows in address order.
    map_rows = []
    for entry in sorted(scope, key=lambda value: scope[value]["body_start"]):
        row = rows[entry]
        parent_row = scope[entry]
        map_rows.append(
            {
                "entry": entry,
                "body_start": parent_row["body_start"],
                "body_end_exclusive": parent_row["body_end_exclusive"],
                "envelope_bytes": parent_row["envelope_bytes"],
                "official_opaque_bytes": parent_row["official_opaque_bytes"],
                "scope": "frontier" if entry in frontier else "liblc3-bucket",
                "parent_bucket": parent_row["bucket"],
                "status": row["status"],
                "module": row["module"] or "",
                "attribution": row["attribution"],
                "evidence": row["evidence"],
                "confidence": row["confidence"],
                "detail": row["detail"],
            }
        )

    return {
        "schema_version": 1,
        "analysis_mode": "read-only; no signing, flashing, erase, or hardware operation",
        "target": "official G2 s200_v2.2.6.10 Apollo main",
        "inputs": {
            "image_sha256": parent_report["inputs"]["image_sha256"],
            "ghidra_sha256sums_sha256": parent_report["inputs"]["ghidra_sha256sums_sha256"],
            "snapshot": "third_party/liblc3 (SNAPSHOT.sha256-verified sources)",
            "source_boundary": SOURCE_BOUNDARY.name,
        },
        "reconciliation": {
            "frontier_functions": len(frontier),
            "frontier_official_bytes": frontier_bytes,
            "liblc3_bucket_functions": len(bucket),
            "liblc3_bucket_official_bytes": bucket_bytes,
            "scope_functions": len(scope),
            "attributed_functions": len(attributed),
            "attributed_official_bytes": attributed_bytes,
            "investigation_functions": len(investigation),
            "investigation_official_bytes": investigation_bytes,
            "external_observations": len(observations),
            "snapshot_tables_parsed": len(parsed_tables),
            "snapshot_tables_located": len(located),
        },
        "module_summary": [
            {
                "module": module,
                "functions": summary[0],
                "official_opaque_bytes": summary[1],
            }
            for module, summary in EXPECTED_MODULE_SUMMARY.items()
        ],
        "external_observations": observations,
        "limitations": [
            "module attribution is evidence-tiered triage, not per-function source ownership or behavioral reconstruction",
            "dispatch-graph positions match the v1.1.3 lc3.c analyze()/encode() source order; low-confidence internals are candidates, not proofs",
            "upstream-table-match proves the stock function reads a byte-identical snapshot table; it does not prove the whole body is pristine upstream code",
            "Ghidra envelope boundaries and partial MVE/Helium decoding are analyzer artifacts inherited from the corpus",
        ],
        "functions": map_rows,
    }


def map_tsv(report: dict[str, Any]) -> str:
    lines = [
        "# G2 liblc3 encoder-internals census; regenerated by "
        "tools/analyze_g2_liblc3_encoder_internals.py",
        MAP_TSV_HEADER,
    ]
    for row in report["functions"]:
        lines.append(
            "\t".join(
                (
                    f"0x{row['entry']:08X}",
                    f"0x{row['body_start']:08X}",
                    f"0x{row['body_end_exclusive']:08X}",
                    str(row["envelope_bytes"]),
                    str(row["official_opaque_bytes"]),
                    row["scope"],
                    row["parent_bucket"],
                    row["status"],
                    row["module"],
                    row["attribution"],
                    row["evidence"],
                    row["confidence"],
                    row["detail"],
                )
            )
        )
    return "\n".join(lines) + "\n"


def summary_json(report: dict[str, Any]) -> str:
    summary = {
        key: report[key]
        for key in (
            "schema_version",
            "analysis_mode",
            "target",
            "inputs",
            "reconciliation",
            "module_summary",
            "external_observations",
            "limitations",
        )
    }
    return json.dumps(summary, indent=2, sort_keys=True) + "\n"


def _text(report: dict[str, Any]) -> str:
    reconciliation = report["reconciliation"]
    lines = [
        "G2 liblc3 encoder-internals census: PASS",
        f"  frontier: {reconciliation['frontier_functions']} functions, "
        f"{reconciliation['frontier_official_bytes']} official bytes",
        f"  liblc3 bucket: {reconciliation['liblc3_bucket_functions']} functions, "
        f"{reconciliation['liblc3_bucket_official_bytes']} official bytes",
        f"  attributed: {reconciliation['attributed_functions']} functions, "
        f"{reconciliation['attributed_official_bytes']} official bytes",
        f"  investigation-required: {reconciliation['investigation_functions']} "
        f"functions, {reconciliation['investigation_official_bytes']} official bytes",
        f"  snapshot tables: {reconciliation['snapshot_tables_parsed']} parsed, "
        f"{reconciliation['snapshot_tables_located']} uniquely located",
        "  modules:",
    ]
    for module in report["module_summary"]:
        lines.append(
            f"    {module['module']}: {module['functions']} functions, "
            f"{module['official_opaque_bytes']} official bytes"
        )
    lines.append(
        f"  external observations: {reconciliation['external_observations']}"
    )
    lines.append("hardware/flash operations: none")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ghidra-corpus", type=Path, required=True)
    parser.add_argument("--manifests", type=Path, default=MANIFESTS)
    parser.add_argument("--snapshot", type=Path, default=SNAPSHOT)
    parser.add_argument("--json", action="store_true")
    parser.add_argument(
        "--write-manifests",
        type=Path,
        metavar="DIRECTORY",
        help="write g2-liblc3-encoder-internals-map.tsv and -summary.json into DIRECTORY",
    )
    args = parser.parse_args()
    report = analyze(
        args.ghidra_corpus, manifests_dir=args.manifests, snapshot_dir=args.snapshot
    )
    if args.write_manifests is not None:
        directory = args.write_manifests
        directory.mkdir(parents=True, exist_ok=True)
        (directory / "g2-liblc3-encoder-internals-map.tsv").write_text(
            map_tsv(report), encoding="utf-8"
        )
        (directory / "g2-liblc3-encoder-internals-summary.json").write_text(
            summary_json(report), encoding="utf-8"
        )
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(_text(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
