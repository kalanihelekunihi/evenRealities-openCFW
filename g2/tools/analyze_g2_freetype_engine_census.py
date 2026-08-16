#!/usr/bin/env python3
"""FreeType engine census of the 0x51xxxx/0x52xxxx no-evidence frontier.

The Apollo unanchored-function provenance census
(``analyze_g2_apollo_unanchored_census.py``) buckets exactly 2 functions (946
official bytes) as FreeType 2.9.1 — the byte-exact ``FT_Done_Face`` envelope
at 0x00526814 and one call-topology neighbour — and leaves 342 no-evidence
functions (75,016 official bytes) in the ``0x51xxxx``/``0x52xxxx`` regions
hypothesized as the FreeType engine frontier.  This analyzer attributes that
frontier to FreeType 2.9.1 modules where distinctive evidence supports it,
against the authenticated VER-2-9-1 snapshot vendored under
``third_party/freetype``.

Scope is exactly 344 functions: the 342-function ``0x51xxxx``/``0x52xxxx``
no-evidence frontier plus the 2-function parent-census freetype bucket.  The
two rejected oversized envelopes whose entries sit in these regions
(``0x00513E2E``, ``0x00514F3C``) stay rejected and are never in scope; the
boundary-envelopes audit's finding that the ``0x00513E2E`` span is 98.7%
accepted-envelope code with 774 interstitial rodata bytes is consistent with
this census, because that accepted code *is* the frontier's discovered
functions.

Evidence tiers, applied in strict priority order; every in-scope function
gets exactly one status, module, evidence class, and confidence level:

1. ``documented-api-anchor`` (high) -- the seven function entries named by
   address in the reviewed FreeType recovery/config audits
   (``FT_Init_FreeType``, ``FT_Add_Default_Modules``, ``FT_Add_Module``,
   ``FT_New_Library``, ``destroy_face``, ``FT_Done_Face``, ``FT_Open_Face``).
   Each anchor is re-verified structurally on every run (exact body span,
   pinned interior instruction addresses, or exact static callee sets).
2. ``documented-interior-pin`` (high) -- ``open_face`` (static, ftobjs.c):
   its body contains the audit-pinned face-internal allocation at 0x00525A0C
   and references the ``incr`` tag literal cell at 0x005262A8, whose image
   word must be 0x696E6372.
3. ``ps-property-string-signature`` (high) -- ``ps_property_set`` /
   ``ps_property_get`` (base/ftpsprop.c): the function references the pointer
   cells of exactly the property-name set parsed from the hash-verified
   snapshot ``ftpsprop.c`` source (four names for set, three for get; the
   get/set asymmetry — ``random-seed`` is set-only — is itself verified
   against the snapshot).
4. ``base-call-graph-direct`` (medium) -- a member of the closed static
   call-graph community grown from the high-confidence anchors that has a
   direct static call edge to a tier-1/2/3 function and whose outbound
   static targets are all community members or allowlisted externals.
5. ``base-call-graph-indirect`` (low) -- remaining community members:
   reachable only through other community functions or through neutral
   leaf/runtime-passthrough helpers.
6. ``investigation-required`` (none) -- no admissible FreeType evidence; a
   deterministic hypothesis is recorded from the external caller families
   and hardware hints.

The call-graph community closure is fail-closed: an outbound static target
is admissible only if it is already in the community, is one of fourteen
curated external identities (the three documented ``am_ftsystem.c``/vendor
ftsystem functions plus eleven body-verified C runtime routines), or bottoms
out in such functions within one further hop (neutral passthrough).  The
derived 83-function attribution is pinned entry-for-entry; any drift raises
``CensusError``.

Corroborating, non-attributing pins: eight flat constant tables parsed from
the hash-verified snapshot sources ``cffload.c``/``t1decode.c``/``psmodule.c``
must yield exactly seven unique byte matches in the official image at pinned
addresses, and no in-scope function may reference any of them — evidence
that the CFF/psaux/psnames driver bodies linked outside this frontier, not
absence of those modules from the build (the authenticated ten-entry
``ft_default_modules[]`` table already proves they are linked).

The analyzer is read-only and deterministic.  It re-derives the frontier
from the parent census (authenticated image, corpus, and manifests) on
every run; any drift in the 342/75,016 frontier, the 2/946 bucket, the
anchor set, the string/table censuses, the closure rule inputs, or the
pinned attribution map raises ``CensusError``.
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
SNAPSHOT = ROOT / "third_party/freetype"
PROVENANCE = SNAPSHOT / "PROVENANCE.json"

FRONTIER_BASE = 0x00510000
FRONTIER_END = 0x00530000
EXPECTED_FRONTIER_FUNCTIONS = 342
EXPECTED_FRONTIER_OFFICIAL_BYTES = 75_016
EXPECTED_FRONTIER_51_FUNCTIONS = 87
EXPECTED_FRONTIER_51_OFFICIAL_BYTES = 36_812
EXPECTED_FRONTIER_52_FUNCTIONS = 255
EXPECTED_FRONTIER_52_OFFICIAL_BYTES = 38_204
EXPECTED_FREETYPE_BUCKET_FUNCTIONS = 2
EXPECTED_FREETYPE_BUCKET_OFFICIAL_BYTES = 946
EXPECTED_SCOPE_FUNCTIONS = 344

# Rejected oversized envelopes whose entries sit inside the frontier regions.
# They are never in scope (parent bucket ``rejected-oversized-envelope``);
# pinned here so a scope leak fails closed.
REGION_REJECTED_ENVELOPES = (0x00513E2E, 0x00514F3C)

# Tier 1: documented API anchors.  Each check is re-derived from the corpus
# and image on every run:
#   body      -- exact [body_start, body_end_exclusive) span
#   contains  -- audit-pinned instruction addresses inside the body
#   calls     -- exact static callee set
#   called_by -- required static callers
#   refs_word -- a DAT-referenced cell whose stored word is this value
RECOVERY_AUDIT = "docs/research/freetype-recovery-audit.md"
FT_DEFAULT_MODULES = 0x0073EEF8
INCR_TAG_LITERAL_CELL = 0x005262A8
INCR_TAG_VALUE = 0x696E6372  # 'incr'
FACE_INTERNAL_ALLOC_SITE = 0x00525A0C
DOCUMENTED_ANCHORS = {
    0x00526814: {
        "name": "FT_Done_Face",
        "source": RECOVERY_AUDIT + ": exact FT_Done_Face at [0x00526814,0x0052687E)",
        "body": (0x00526814, 0x0052687E),
        "calls": (0x005292E6, 0x00529324, 0x00529256, 0x005258A8),
    },
    0x005264A6: {
        "name": "FT_Open_Face",
        "source": RECOVERY_AUDIT + ": FT_Open_Face cleanup calls at "
        "0x0052659C and 0x005267D0",
        "contains": (0x0052659C, 0x005267D0),
        "calls_include": (0x00526814,),
    },
    0x0052431C: {
        "name": "FT_Init_FreeType",
        "source": RECOVERY_AUDIT + ": FT_Init_FreeType at 0x0052431C",
        "calls": (0x005676A0, 0x005676C6, 0x005274B2, 0x005242FC),
    },
    0x005242FC: {
        "name": "FT_Add_Default_Modules",
        "source": RECOVERY_AUDIT + ": FT_Add_Default_Modules at 0x005242FC "
        "walking ft_default_modules[] at 0x0073EEF8",
        "calls": (0x0052729C,),
        "refs_word": FT_DEFAULT_MODULES,
    },
    0x0052729C: {
        "name": "FT_Add_Module",
        "source": RECOVERY_AUDIT + ": FT_Add_Module at 0x0052729C",
        "called_by": (0x005242FC,),
    },
    0x005274B2: {
        "name": "FT_New_Library",
        "source": RECOVERY_AUDIT + ": FT_New_Library writes version 2/9/1 at "
        "0x005274DA/0x005274DE/0x005274E2",
        "contains": (0x005274DA, 0x005274DE, 0x005274E2),
    },
    0x005258A8: {
        "name": "destroy_face",
        "source": RECOVERY_AUDIT + ": private destroy_face body at 0x005258A8",
        "called_by": (0x00526814,),
    },
}

# Tier 2: open_face, pinned by two interior audit addresses.
EXPECTED_OPEN_FACE = 0x005259BE

# Tier 3: ps_property_set/ps_property_get from base/ftpsprop.c.  The property
# name sets are parsed from the hash-verified snapshot source on every run
# and must equal these pinned sets exactly.
PSPROP_SOURCE = "src/base/ftpsprop.c"
EXPECTED_PS_PROPERTY_SET_NAMES = (
    "darkening-parameters",
    "hinting-engine",
    "no-stem-darkening",
    "random-seed",
)
EXPECTED_PS_PROPERTY_GET_NAMES = (
    "darkening-parameters",
    "hinting-engine",
    "no-stem-darkening",
)
EXPECTED_PS_PROPERTY_SET_ENTRY = 0x00527F0A
EXPECTED_PS_PROPERTY_GET_ENTRY = 0x00527FF2

# External allowlist for the call-graph community closure.  Every entry is a
# corpus function outside the scope with a curated, cited identity:
# the vendor ftsystem functions documented in the recovery audit, and C
# runtime routines identified by their decompiled bodies (word-parallel
# zero-detection idioms, byte loops, and image-wide fan-in).
EXTERNAL_ALLOWLIST = {
    0x005675E8: "FT_Stream_Open (vendor ftsystem; " + RECOVERY_AUDIT + " stream support)",
    0x005676A0: "FT_New_Memory (am_ftsystem.c; " + RECOVERY_AUDIT + " section 5)",
    0x005676C6: "FT_Done_Memory (am_ftsystem.c; " + RECOVERY_AUDIT + " section 5)",
    0x00439710: "memmove (C runtime; overlapping-copy body)",
    0x00439BE4: "memcpy variant (C runtime; word-parallel copy body)",
    0x00439C04: "memcpy (C runtime; word-parallel copy body)",
    0x0043C0E4: "memset (C runtime; splatted-byte fill body)",
    0x0043C0EC: "memset tail (C runtime; called only from 0x0043C0E4)",
    0x0044A43C: "strlen (C runtime; 0xFEFEFEFF zero-detection idiom)",
    0x0044B5A0: "strncpy (C runtime; 0xFEFEFEFF zero-detection idiom)",
    0x0046CACC: "strcmp (C runtime; byte-wise compare loop)",
    0x0044B63A: "strstr (C runtime; strchr-driven scan loop)",
    0x004751C8: "memcmp (C runtime; word-wise compare with byte-swap order)",
    0x00481818: "strchr (C runtime; byte scan loop)",
}

# Snapshot sources parsed for flat scalar constant tables; every file is
# hash-verified against the authenticated PROVENANCE.json before parsing.
TABLE_SOURCES = (
    "src/cff/cffload.c",
    "src/psaux/t1decode.c",
    "src/psnames/psmodule.c",
)
MIN_TABLE_BYTES = 16
EXPECTED_TABLES_PARSED = 8
# The seven uniquely byte-matched tables, at pinned image addresses.  These
# tables prove the CFF/psaux/psnames constant data linked into the image;
# no in-scope function references them, which bounds those drivers' code
# outside this frontier.
EXPECTED_LOCATED_TABLES = {
    "src/cff/cffload.c:cff_expert_encoding": 0x006C0150,
    "src/cff/cffload.c:cff_isoadobe_charset": 0x006C1C60,
    "src/cff/cffload.c:cff_expert_charset": 0x006C93B0,
    "src/cff/cffload.c:cff_expertsubset_charset": 0x006D22FC,
    "src/psaux/t1decode.c:t1_args_count": 0x006D7C60,
    "src/psnames/psmodule.c:ft_extra_glyph_unicodes": 0x0074D214,
    "src/psnames/psmodule.c:ft_extra_glyph_name_offsets": 0x0074D23C,
}

# Out-of-scope documented/derived observations, never re-bucketed here.
EXPECTED_EXTERNAL_OBSERVATIONS = 4
EXTERNAL_FTSYSTEM = (0x005675E8, 0x005676A0, 0x005676C6)
# FT_Stream_New (static, ftobjs.c): direct static callee of the FT_Open_Face
# anchor that the parent census bucketed ``lvgl`` by call topology.  Its
# decompiled body dispatches FT_OPEN_MEMORY -> 0x005288B8 (FT_Stream_OpenMemory),
# FT_OPEN_PATHNAME -> 0x005675E8 (FT_Stream_Open), FT_OPEN_STREAM -> reuse.
EXPECTED_FT_STREAM_NEW = 0x00524F96
EXPECTED_FT_STREAM_NEW_CALLS = (0x00529148, 0x005288B8, 0x005675E8, 0x00529256)

# The whole 83-row attribution result, pinned.  Any derived drift raises.
# entry -> (status, module, evidence, confidence)
EXPECTED_ATTRIBUTION = {
    0x00526814: ("module", "base", "documented-api-anchor", "high"),
    0x005264A6: ("module", "base", "documented-api-anchor", "high"),
    0x0052431C: ("module", "base", "documented-api-anchor", "high"),
    0x005242FC: ("module", "base", "documented-api-anchor", "high"),
    0x0052729C: ("module", "base", "documented-api-anchor", "high"),
    0x005274B2: ("module", "base", "documented-api-anchor", "high"),
    0x005258A8: ("module", "base", "documented-api-anchor", "high"),
    0x005259BE: ("module", "base", "documented-interior-pin", "high"),
    0x00527F0A: ("module", "base", "ps-property-string-signature", "high"),
    0x00527FF2: ("module", "base", "ps-property-string-signature", "high"),
    0x0052502A: ("cluster", "base", "base-call-graph-direct", "medium"),
    0x00525386: ("cluster", "base", "base-call-graph-direct", "medium"),
    0x005253F4: ("cluster", "base", "base-call-graph-direct", "medium"),
    0x0052586E: ("cluster", "base", "base-call-graph-direct", "medium"),
    0x0052594A: ("cluster", "base", "base-call-graph-direct", "medium"),
    0x00525ADE: ("cluster", "base", "base-call-graph-direct", "medium"),
    0x00525B6E: ("cluster", "base", "base-call-graph-direct", "medium"),
    0x0052687E: ("cluster", "base", "base-call-graph-direct", "medium"),
    0x005270D2: ("cluster", "base", "base-call-graph-direct", "medium"),
    0x00527466: ("cluster", "base", "base-call-graph-direct", "medium"),
    0x005288E0: ("cluster", "base", "base-call-graph-direct", "medium"),
    0x00529148: ("cluster", "base", "base-call-graph-direct", "medium"),
    0x00529256: ("cluster", "base", "base-call-graph-direct", "medium"),
    0x005292E6: ("cluster", "base", "base-call-graph-direct", "medium"),
    0x00529304: ("cluster", "base", "base-call-graph-direct", "medium"),
    0x00529324: ("cluster", "base", "base-call-graph-direct", "medium"),
    0x00529378: ("cluster", "base", "base-call-graph-direct", "medium"),
    0x00524B88: ("cluster", "base", "base-call-graph-indirect", "low"),
    0x00524BA8: ("cluster", "base", "base-call-graph-indirect", "low"),
    0x00524BC4: ("cluster", "base", "base-call-graph-indirect", "low"),
    0x00524C1E: ("cluster", "base", "base-call-graph-indirect", "low"),
    0x00524C3A: ("cluster", "base", "base-call-graph-indirect", "low"),
    0x00524C88: ("cluster", "base", "base-call-graph-indirect", "low"),
    0x00524CC4: ("cluster", "base", "base-call-graph-indirect", "low"),
    0x00524CD6: ("cluster", "base", "base-call-graph-indirect", "low"),
    0x00524E08: ("cluster", "base", "base-call-graph-indirect", "low"),
    0x00524E58: ("cluster", "base", "base-call-graph-indirect", "low"),
    0x00524E7A: ("cluster", "base", "base-call-graph-indirect", "low"),
    0x0052504C: ("cluster", "base", "base-call-graph-indirect", "low"),
    0x005250A2: ("cluster", "base", "base-call-graph-indirect", "low"),
    0x0052525C: ("cluster", "base", "base-call-graph-indirect", "low"),
    0x0052526C: ("cluster", "base", "base-call-graph-indirect", "low"),
    0x005252BC: ("cluster", "base", "base-call-graph-indirect", "low"),
    0x00525334: ("cluster", "base", "base-call-graph-indirect", "low"),
    0x00525832: ("cluster", "base", "base-call-graph-indirect", "low"),
    0x00525936: ("cluster", "base", "base-call-graph-indirect", "low"),
    0x00525B02: ("cluster", "base", "base-call-graph-indirect", "low"),
    0x00525B20: ("cluster", "base", "base-call-graph-indirect", "low"),
    0x00525C08: ("cluster", "base", "base-call-graph-indirect", "low"),
    0x00526DA2: ("cluster", "base", "base-call-graph-indirect", "low"),
    0x00526E38: ("cluster", "base", "base-call-graph-indirect", "low"),
    0x00526E5A: ("cluster", "base", "base-call-graph-indirect", "low"),
    0x0052705A: ("cluster", "base", "base-call-graph-indirect", "low"),
    0x00527096: ("cluster", "base", "base-call-graph-indirect", "low"),
    0x005270BC: ("cluster", "base", "base-call-graph-indirect", "low"),
    0x0052716C: ("cluster", "base", "base-call-graph-indirect", "low"),
    0x005271C0: ("cluster", "base", "base-call-graph-indirect", "low"),
    0x00527228: ("cluster", "base", "base-call-graph-indirect", "low"),
    0x0052724C: ("cluster", "base", "base-call-graph-indirect", "low"),
    0x005273B8: ("cluster", "base", "base-call-graph-indirect", "low"),
    0x005273F2: ("cluster", "base", "base-call-graph-indirect", "low"),
    0x00528470: ("cluster", "base", "base-call-graph-indirect", "low"),
    0x00528508: ("cluster", "base", "base-call-graph-indirect", "low"),
    0x00528524: ("cluster", "base", "base-call-graph-indirect", "low"),
    0x005285D4: ("cluster", "base", "base-call-graph-indirect", "low"),
    0x0052862C: ("cluster", "base", "base-call-graph-indirect", "low"),
    0x00528720: ("cluster", "base", "base-call-graph-indirect", "low"),
    0x00528842: ("cluster", "base", "base-call-graph-indirect", "low"),
    0x005288B8: ("cluster", "base", "base-call-graph-indirect", "low"),
    0x005288CE: ("cluster", "base", "base-call-graph-indirect", "low"),
    0x00528914: ("cluster", "base", "base-call-graph-indirect", "low"),
    0x00528992: ("cluster", "base", "base-call-graph-indirect", "low"),
    0x005289B0: ("cluster", "base", "base-call-graph-indirect", "low"),
    0x005289D0: ("cluster", "base", "base-call-graph-indirect", "low"),
    0x00528A66: ("cluster", "base", "base-call-graph-indirect", "low"),
    0x00528B4A: ("cluster", "base", "base-call-graph-indirect", "low"),
    0x00528BA8: ("cluster", "base", "base-call-graph-indirect", "low"),
    0x00528C14: ("cluster", "base", "base-call-graph-indirect", "low"),
    0x00529176: ("cluster", "base", "base-call-graph-indirect", "low"),
    0x0052919C: ("cluster", "base", "base-call-graph-indirect", "low"),
    0x005291E4: ("cluster", "base", "base-call-graph-indirect", "low"),
    0x00529262: ("cluster", "base", "base-call-graph-indirect", "low"),
    0x00529296: ("cluster", "base", "base-call-graph-indirect", "low"),
}

EXPECTED_ATTRIBUTED_FUNCTIONS = 83
EXPECTED_ATTRIBUTED_OFFICIAL_BYTES = 7_874
EXPECTED_INVESTIGATION_FUNCTIONS = 261
EXPECTED_INVESTIGATION_OFFICIAL_BYTES = 68_088

# Per-module roll-up over the 344-function scope (attributed rows only).
# module -> (functions, official_opaque_bytes)
EXPECTED_MODULE_SUMMARY = {
    "base": (83, 7_874),
}

# Body-shape hypotheses for community members whose decompiled bodies match
# textbook ftutil.c/ftobjs.c internals; used in the manifest attribution
# column.  Everything else carries a structural detail string only.
MEMBER_HYPOTHESES = {
    0x005292E6: "FT_List_Find candidate (ftutil.c list search)",
    0x00529324: "FT_List_Remove candidate (ftutil.c list unlink)",
    0x00529304: "FT_List_Add candidate (ftutil.c list append)",
    0x00529378: "FT_List_Finalize candidate (ftutil.c list destroy)",
    0x00529256: "ft_mem_free candidate (FT_FREE wrapper through memory->free)",
    0x00529148: "ft_mem_alloc candidate (zeroing allocation wrapper)",
    0x00529176: "ft_mem_qalloc candidate (allocation through memory->alloc)",
    0x0052687E: "faces_list insertion helper candidate (FT_Open_Face outlined block)",
}

MODULES = ("base",)
EVIDENCE_CLASSES = (
    "documented-api-anchor",
    "documented-interior-pin",
    "ps-property-string-signature",
    "base-call-graph-direct",
    "base-call-graph-indirect",
    "none",
)
STATUSES = ("module", "cluster", "investigation-required")
CONFIDENCE_ORDER = ("high", "medium", "low", "none")

FUNCTION_BEGIN_RE = re.compile(
    r"OPENCFW_FUNCTION_BEGIN entry=([0-9a-f]+) "
    r"body_start=([0-9a-f]+) body_end=([0-9a-f]+) name=(\S+)",
    re.IGNORECASE,
)
FUNCTION_END_RE = re.compile(r"OPENCFW_FUNCTION_END entry=([0-9a-f]+)", re.IGNORECASE)
ADDRESS_TOKEN_RE = re.compile(r"(?<![0-9a-fA-F])([0-9a-f]{8})(?![0-9a-fA-F])")
CALL_RE = re.compile(r"\bFUN_([0-9a-f]{8})\s*\(")
DAT_RE = re.compile(r"\bDAT_([0-9a-f]{8})")

C_COMMENT_RE = re.compile(r"/\*.*?\*/", re.DOTALL)
LINE_COMMENT_RE = re.compile(r"//[^\n]*")
PS_PROPERTY_NAME_RE = re.compile(r'ft_strcmp\(\s*property_name,\s*"([^"]+)"\s*\)')

TABLE_DECL_RE = re.compile(
    r"(?:static\s+)?const\s+"
    r"(FT_UShort|FT_Short|FT_UInt16|FT_Int16|FT_Byte|FT_UByte|"
    r"FT_UInt32|FT_Int32|FT_UInt|FT_Int|FT_ULong|FT_Long|FT_Pos|FT_Fixed)\s+"
    r"(\w+)((?:\s*\[[^\]]*\])+)\s*=\s*\{"
)
INT_TOKEN_RE = re.compile(r"[+-]?(0x[0-9a-fA-F]+|\d+)[uUlL]*")
TABLE_TYPE_FORMAT = {
    "FT_UShort": "H",
    "FT_Short": "h",
    "FT_UInt16": "H",
    "FT_Int16": "h",
    "FT_Byte": "B",
    "FT_UByte": "B",
    "FT_UInt32": "I",
    "FT_Int32": "i",
    "FT_UInt": "I",
    "FT_Int": "i",
    "FT_ULong": "I",
    "FT_Long": "i",
    "FT_Pos": "i",
    "FT_Fixed": "i",
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
        "apollo_unanchored_census_for_freetype", PARENT_ANALYZER
    )
    if spec is None or spec.loader is None:
        raise CensusError(f"cannot load {PARENT_ANALYZER}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def parse_corpus(logs: list[Path]) -> dict[int, dict[str, Any]]:
    """Per-function body spans, static call sets, DAT refs, address tokens."""

    functions: dict[int, dict[str, Any]] = {}
    current: dict[str, Any] | None = None
    for log in logs:
        for line in log.read_text(encoding="utf-8", errors="strict").splitlines():
            begin = FUNCTION_BEGIN_RE.search(line)
            if begin:
                current = {
                    "entry": int(begin.group(1), 16),
                    "body_start": int(begin.group(2), 16),
                    "body_end_exclusive": int(begin.group(3), 16) + 1,
                    "calls": set(),
                    "dat_refs": set(),
                    "tokens": set(),
                }
                functions[current["entry"]] = current
                continue
            if FUNCTION_END_RE.search(line):
                current = None
                continue
            if current is not None:
                current["calls"].update(
                    int(token, 16) for token in CALL_RE.findall(line)
                )
                current["dat_refs"].update(
                    int(token, 16) for token in DAT_RE.findall(line)
                )
                current["tokens"].update(
                    int(token, 16) for token in ADDRESS_TOKEN_RE.findall(line)
                )
    return functions


def caller_map(functions: dict[int, dict[str, Any]]) -> dict[int, set[int]]:
    callers: dict[int, set[int]] = defaultdict(set)
    for entry, row in functions.items():
        for target in row["calls"]:
            if target != entry:
                callers[target].add(entry)
    return callers


def verify_snapshot_files(snapshot: Path, names: tuple[str, ...]) -> None:
    """Every parsed snapshot source must hash to the authenticated manifest."""

    if not PROVENANCE.is_file():
        raise CensusError("missing freetype PROVENANCE.json")
    provenance = json.loads(PROVENANCE.read_text(encoding="utf-8"))
    recorded = {
        row["local_path"]: row["sha256"] for row in provenance.get("files", [])
    }
    if len(recorded) != 297:
        raise CensusError(
            f"provenance file census changed: {len(recorded)} != 297"
        )
    for name in names:
        path = snapshot / name
        if name not in recorded:
            raise CensusError(f"snapshot manifest lacks {name}")
        if not path.is_file():
            raise CensusError(f"missing snapshot source {name}")
        if _sha256_bytes(path.read_bytes()) != recorded[name]:
            raise CensusError(f"snapshot source drifted: {name}")


def _clean_source(text: str) -> str:
    return LINE_COMMENT_RE.sub(" ", C_COMMENT_RE.sub(" ", text))


def parse_ps_property_names(snapshot: Path) -> tuple[tuple[str, ...], tuple[str, ...]]:
    """Property-name sets of ps_property_set/ps_property_get from ftpsprop.c.

    The 2.9.1 source defines ps_property_set before ps_property_get; the
    split point is the ps_property_get definition.
    """

    verify_snapshot_files(snapshot, (PSPROP_SOURCE,))
    text = _clean_source((snapshot / PSPROP_SOURCE).read_text(encoding="utf-8"))
    set_marker = text.find("ps_property_set")
    get_marker = text.find("ps_property_get", set_marker)
    if set_marker < 0 or get_marker < 0:
        raise CensusError("ftpsprop.c no longer defines ps_property_set/get")
    set_names = tuple(PS_PROPERTY_NAME_RE.findall(text[set_marker:get_marker]))
    get_names = tuple(PS_PROPERTY_NAME_RE.findall(text[get_marker:]))
    if set_names != EXPECTED_PS_PROPERTY_SET_NAMES:
        raise CensusError(f"ps_property_set property census changed: {set_names!r}")
    if get_names != EXPECTED_PS_PROPERTY_GET_NAMES:
        raise CensusError(f"ps_property_get property census changed: {get_names!r}")
    return set_names, get_names


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
        if not INT_TOKEN_RE.fullmatch(token):
            return None
        values.append(int(token.rstrip("uUlL"), 0))
    fmt = "<" + TABLE_TYPE_FORMAT[element_type] * len(values)
    try:
        return struct.pack(fmt, *values)
    except struct.error:
        return None


def parse_snapshot_tables(snapshot: Path) -> dict[str, bytes]:
    """Parse flat scalar C arrays from the hash-verified snapshot sources."""

    verify_snapshot_files(snapshot, TABLE_SOURCES)
    tables: dict[str, bytes] = {}
    for name in TABLE_SOURCES:
        text = _clean_source((snapshot / name).read_text(encoding="utf-8"))
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


def string_cell_targets(blob: bytes, load_base: int, strings: tuple[str, ...]) -> dict[int, str]:
    """Map image addresses (string bodies and pointer cells) to name."""

    targets: dict[int, str] = {}
    for text in strings:
        needle = text.encode("ascii") + b"\x00"
        cursor = 0
        while True:
            offset = blob.find(needle, cursor)
            if offset < 0:
                break
            string_address = load_base + offset
            targets[string_address] = text
            cell_needle = struct.pack("<I", string_address)
            cell_cursor = 0
            while True:
                cell_offset = blob.find(cell_needle, cell_cursor)
                if cell_offset < 0:
                    break
                targets[load_base + cell_offset] = text
                cell_cursor = cell_offset + 1
            cursor = offset + 1
    return targets


def grow_community(
    seeds: set[int],
    scope: set[int],
    functions: dict[int, dict[str, Any]],
    callers: dict[int, set[int]],
    allowlist: set[int],
) -> set[int]:
    """Closed static call-graph community grown from the seeds.

    An outbound static target is admissible only when it is already in the
    community, is allowlisted, or is neutral: every one of its own outbound
    targets is allowlisted or a leaf (zero outbound static calls).  A scope
    function joins when all of its outbound targets are admissible and it
    has at least one static edge to the community.
    """

    def outbound(entry: int) -> set[int]:
        return functions[entry]["calls"] - {entry}

    def neutral(target: int) -> bool:
        if target not in functions:
            return False
        return all(
            follow in allowlist
            or (follow in functions and not outbound(follow))
            for follow in outbound(target)
        )

    community = set(seeds)
    changed = True
    while changed:
        changed = False
        for entry in sorted(scope - community):
            out = outbound(entry)
            if not all(
                target in community or target in allowlist or neutral(target)
                for target in out
            ):
                continue
            if (out & community) or (callers.get(entry, set()) & community):
                community.add(entry)
                changed = True
    return community


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

    # --- Scope derivation: the 0x51/0x52xxxx no-evidence frontier + bucket.
    frontier = {
        entry: row
        for entry, row in parent_records.items()
        if row["bucket"] == "investigation-required-no-evidence"
        and FRONTIER_BASE <= entry < FRONTIER_END
    }
    if len(frontier) != EXPECTED_FRONTIER_FUNCTIONS:
        raise CensusError(
            f"0x51/0x52xxxx no-evidence frontier changed: {len(frontier)} != "
            f"{EXPECTED_FRONTIER_FUNCTIONS}"
        )
    frontier_bytes = sum(row["official_opaque_bytes"] for row in frontier.values())
    if frontier_bytes != EXPECTED_FRONTIER_OFFICIAL_BYTES:
        raise CensusError(
            f"frontier official bytes changed: {frontier_bytes} != "
            f"{EXPECTED_FRONTIER_OFFICIAL_BYTES}"
        )
    frontier_51 = {e: r for e, r in frontier.items() if e < 0x00520000}
    frontier_52 = {e: r for e, r in frontier.items() if e >= 0x00520000}
    if len(frontier_51) != EXPECTED_FRONTIER_51_FUNCTIONS or sum(
        row["official_opaque_bytes"] for row in frontier_51.values()
    ) != EXPECTED_FRONTIER_51_OFFICIAL_BYTES:
        raise CensusError("0x51xxxx frontier split changed")
    if len(frontier_52) != EXPECTED_FRONTIER_52_FUNCTIONS or sum(
        row["official_opaque_bytes"] for row in frontier_52.values()
    ) != EXPECTED_FRONTIER_52_OFFICIAL_BYTES:
        raise CensusError("0x52xxxx frontier split changed")
    bucket = {
        entry: row
        for entry, row in parent_records.items()
        if row["bucket"] == "freetype"
    }
    if len(bucket) != EXPECTED_FREETYPE_BUCKET_FUNCTIONS:
        raise CensusError(
            f"freetype bucket changed: {len(bucket)} != "
            f"{EXPECTED_FREETYPE_BUCKET_FUNCTIONS}"
        )
    bucket_bytes = sum(row["official_opaque_bytes"] for row in bucket.values())
    if bucket_bytes != EXPECTED_FREETYPE_BUCKET_OFFICIAL_BYTES:
        raise CensusError(
            f"freetype bucket official bytes changed: {bucket_bytes} != "
            f"{EXPECTED_FREETYPE_BUCKET_OFFICIAL_BYTES}"
        )
    scope = {**frontier, **bucket}
    if len(scope) != EXPECTED_SCOPE_FUNCTIONS:
        raise CensusError("frontier and freetype bucket overlap; scope changed")
    for entry in REGION_REJECTED_ENVELOPES:
        if entry in scope:
            raise CensusError(
                f"rejected envelope 0x{entry:08X} leaked into the census scope"
            )
        if parent_records[entry]["bucket"] != "rejected-oversized-envelope":
            raise CensusError(
                f"0x{entry:08X} is no longer a rejected oversized envelope"
            )

    # --- Corpus call graph.
    logs = path_module.verify_corpus(corpus_root)
    functions = parse_corpus(logs)
    callers = caller_map(functions)
    for entry in scope:
        if entry not in functions:
            raise CensusError(f"scope function 0x{entry:08X} missing from corpus")

    # --- Tier 1: documented API anchors, structurally re-verified.
    for entry, anchor in DOCUMENTED_ANCHORS.items():
        if entry not in scope:
            raise CensusError(f"documented anchor 0x{entry:08X} left the scope")
        row = functions[entry]
        if "body" in anchor:
            start, end = anchor["body"]
            if (row["body_start"], row["body_end_exclusive"]) != (start, end):
                raise CensusError(
                    f"anchor {anchor['name']} body span changed: "
                    f"[0x{row['body_start']:08X},0x{row['body_end_exclusive']:08X})"
                )
        for site in anchor.get("contains", ()):
            if not row["body_start"] <= site < row["body_end_exclusive"]:
                raise CensusError(
                    f"anchor {anchor['name']} lost pinned interior site "
                    f"0x{site:08X}"
                )
        callees = row["calls"] - {entry}
        if "calls" in anchor and set(anchor["calls"]) != callees:
            raise CensusError(
                f"anchor {anchor['name']} callee set changed: "
                + ", ".join(f"0x{c:08x}" for c in sorted(callees))
            )
        for required in anchor.get("calls_include", ()):
            if required not in callees:
                raise CensusError(
                    f"anchor {anchor['name']} no longer calls 0x{required:08X}"
                )
        for required in anchor.get("called_by", ()):
            if entry not in functions[required]["calls"]:
                raise CensusError(
                    f"anchor {anchor['name']} lost caller 0x{required:08X}"
                )
        if "refs_word" in anchor:
            if not any(
                _word(blob, load_base, ref) == anchor["refs_word"]
                for ref in row["dat_refs"]
            ):
                raise CensusError(
                    f"anchor {anchor['name']} no longer references "
                    f"0x{anchor['refs_word']:08X}"
                )

    # --- Tier 2: open_face interior pins.
    open_face = EXPECTED_OPEN_FACE
    if open_face not in scope:
        raise CensusError("open_face left the census scope")
    row = functions[open_face]
    if not row["body_start"] <= FACE_INTERNAL_ALLOC_SITE < row["body_end_exclusive"]:
        raise CensusError("open_face lost the face-internal allocation site")
    if INCR_TAG_LITERAL_CELL not in row["dat_refs"]:
        raise CensusError("open_face no longer references the incr tag literal cell")
    if _word(blob, load_base, INCR_TAG_LITERAL_CELL) != INCR_TAG_VALUE:
        raise CensusError("incr tag literal cell no longer holds 0x696E6372")

    # --- Tier 3: ps_property_set/get string signatures.
    set_names, get_names = parse_ps_property_names(snapshot_dir)
    targets = string_cell_targets(blob, load_base, set_names)
    string_hits: dict[int, set[str]] = {}
    for entry in scope:
        names = {targets[ref] for ref in functions[entry]["dat_refs"] if ref in targets}
        if names:
            string_hits[entry] = names
    if set(string_hits) != {EXPECTED_PS_PROPERTY_SET_ENTRY, EXPECTED_PS_PROPERTY_GET_ENTRY}:
        raise CensusError(
            "ps-property string evidence set changed: "
            + ", ".join(f"0x{e:08x}" for e in sorted(string_hits))
        )
    if string_hits[EXPECTED_PS_PROPERTY_SET_ENTRY] != set(set_names):
        raise CensusError("ps_property_set candidate references changed")
    if string_hits[EXPECTED_PS_PROPERTY_GET_ENTRY] != set(get_names):
        raise CensusError("ps_property_get candidate references changed")

    # --- Corroborating snapshot table census (never attributing).
    parsed_tables = parse_snapshot_tables(snapshot_dir)
    if len(parsed_tables) != EXPECTED_TABLES_PARSED:
        raise CensusError(
            f"snapshot table census changed: {len(parsed_tables)} != "
            f"{EXPECTED_TABLES_PARSED}"
        )
    located = locate_tables(blob, load_base, parsed_tables)
    if located != EXPECTED_LOCATED_TABLES:
        raise CensusError(
            "located table census changed: "
            + ", ".join(
                f"{key}@0x{address:08X}" for key, address in sorted(located.items())
            )
        )
    for entry in scope:
        for ref in functions[entry]["dat_refs"]:
            candidates = [ref]
            value = _word(blob, load_base, ref)
            if value is not None:
                candidates.append(value)
            for key, address in located.items():
                end = address + len(parsed_tables[key])
                if any(address <= candidate < end for candidate in candidates):
                    raise CensusError(
                        f"scope function 0x{entry:08X} now references located "
                        f"table {key}; the out-of-frontier driver bound changed"
                    )

    # --- Tiers 4/5: closed static call-graph community from the anchors.
    high = (
        set(DOCUMENTED_ANCHORS)
        | {open_face}
        | {EXPECTED_PS_PROPERTY_SET_ENTRY, EXPECTED_PS_PROPERTY_GET_ENTRY}
    )
    for entry in EXTERNAL_ALLOWLIST:
        if entry not in functions:
            raise CensusError(
                f"allowlisted external 0x{entry:08X} is no longer a corpus function"
            )
        if entry in scope:
            raise CensusError(
                f"allowlisted external 0x{entry:08X} entered the census scope"
            )
    community = grow_community(
        set(high), set(scope), functions, callers, set(EXTERNAL_ALLOWLIST)
    )
    if not high <= community:
        raise CensusError("anchor set is not a subset of its own community")

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

    for entry, anchor in sorted(DOCUMENTED_ANCHORS.items()):
        put(entry, "module", "base", "documented-api-anchor", "high",
            anchor["name"], anchor["source"])
    put(open_face, "module", "base", "documented-interior-pin", "high",
        "open_face (static, ftobjs.c)",
        RECOVERY_AUDIT + ": face-internal 0x44-byte allocation at 0x00525A0C "
        "and incr tag literal 0x696E6372 at 0x005262A8")
    put(EXPECTED_PS_PROPERTY_SET_ENTRY, "module", "base",
        "ps-property-string-signature", "high", "ps_property_set (ftpsprop.c)",
        "references the pointer cells of all four 2.9.1 ps_property_set "
        "property names: " + "|".join(set_names))
    put(EXPECTED_PS_PROPERTY_GET_ENTRY, "module", "base",
        "ps-property-string-signature", "high", "ps_property_get (ftpsprop.c)",
        "references the pointer cells of exactly the three 2.9.1 "
        "ps_property_get property names (random-seed is set-only): "
        + "|".join(get_names))
    for entry in sorted(community - high):
        out = functions[entry]["calls"] - {entry}
        direct = bool((out & high) or (callers.get(entry, set()) & high))
        pure = all(
            target in community or target in EXTERNAL_ALLOWLIST for target in out
        )
        hypothesis = MEMBER_HYPOTHESES.get(entry, "")
        if direct and pure:
            neighbours = sorted((out | callers.get(entry, set())) & high)
            extra_names = {
                open_face: "open_face",
                EXPECTED_PS_PROPERTY_SET_ENTRY: "ps_property_set",
                EXPECTED_PS_PROPERTY_GET_ENTRY: "ps_property_get",
            }
            name_list = ",".join(
                DOCUMENTED_ANCHORS[n]["name"] if n in DOCUMENTED_ANCHORS
                else extra_names[n]
                for n in neighbours
            )
            put(entry, "cluster", "base", "base-call-graph-direct", "medium",
                hypothesis,
                "direct static call edge to " + name_list
                + "; every outbound static target is community or allowlisted runtime")
        else:
            put(entry, "cluster", "base", "base-call-graph-indirect", "low",
                hypothesis,
                "reachable from the anchor community only through other "
                "community members or neutral leaf/runtime helpers")

    # --- Fail-closed comparison against the pinned attribution map.
    derived = {
        entry: (row["status"], row["module"], row["evidence"], row["confidence"])
        for entry, row in rows.items()
    }
    if derived != EXPECTED_ATTRIBUTION:
        only_derived = sorted(set(derived) - set(EXPECTED_ATTRIBUTION))
        only_expected = sorted(set(EXPECTED_ATTRIBUTION) - set(derived))
        changed = sorted(
            entry
            for entry in set(derived) & set(EXPECTED_ATTRIBUTION)
            if derived[entry] != EXPECTED_ATTRIBUTION[entry]
        )
        raise CensusError(
            "attribution map changed: only-derived "
            + ",".join(f"0x{e:08X}" for e in only_derived)
            + " only-expected "
            + ",".join(f"0x{e:08X}" for e in only_expected)
            + " changed "
            + ",".join(f"0x{e:08X}" for e in changed)
        )

    # --- Investigation-required remainder with deterministic hypotheses.
    for entry in sorted(scope):
        if entry in rows:
            continue
        row = scope[entry]
        external = sorted(callers.get(entry, set()) - {entry})
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
                + ",".join(f"0x{caller:08X}" for caller in external[:8])
                + ("..." if len(external) > 8 else "")
                + ")"
            )
        else:
            hints.append(
                "no static caller in the corpus; candidate "
                "class/interface-record-referenced internal or dead-stripped envelope"
            )
        rejected_calls = sorted(
            target
            for target in functions[entry]["calls"]
            if target in REGION_REJECTED_ENVELOPES
        )
        if rejected_calls:
            hints.append(
                "calls rejected oversized envelope "
                + "|".join(f"0x{target:08X}" for target in rejected_calls)
            )
        tokens = functions[entry]["tokens"]
        if any(0x4000_0000 <= token < 0x6000_0000 for token in tokens):
            hints.append("references peripheral registers")
        if any(0x2000_0000 <= token < 0x2008_0000 for token in tokens):
            hints.append("references SRAM globals")
        hints.append("no FreeType anchor, string, or call-community evidence")
        put(entry, "investigation-required", None, "none", "none", "",
            "; ".join(hints))

    # --- Reconciliation.
    def official(entry: int) -> int:
        return scope[entry]["official_opaque_bytes"]

    attributed = sorted(EXPECTED_ATTRIBUTION)
    attributed_bytes = sum(official(entry) for entry in attributed)
    investigation = sorted(set(scope) - set(EXPECTED_ATTRIBUTION))
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
        EXPECTED_FRONTIER_OFFICIAL_BYTES + EXPECTED_FREETYPE_BUCKET_OFFICIAL_BYTES
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

    # --- Out-of-scope observations (never re-bucketed here).
    stream_new = EXPECTED_FT_STREAM_NEW
    if stream_new in scope:
        raise CensusError("FT_Stream_New candidate entered the census scope")
    if (functions[stream_new]["calls"] - {stream_new}) != set(EXPECTED_FT_STREAM_NEW_CALLS):
        raise CensusError("FT_Stream_New candidate callee set changed")
    observations = []
    for entry in EXTERNAL_FTSYSTEM:
        observations.append(
            {
                "entry": entry,
                "module": "base",
                "attribution": EXTERNAL_ALLOWLIST[entry],
                "evidence": "documented-external",
                "confidence": "high",
                "parent_bucket": parent_records.get(entry, {}).get("bucket")
                if entry in parent_records
                else "path-anchored",
            }
        )
    observations.append(
        {
            "entry": stream_new,
            "module": "base",
            "attribution": "FT_Stream_New candidate (static, ftobjs.c); body "
            "dispatches FT_OPEN_MEMORY/FT_OPEN_PATHNAME/FT_OPEN_STREAM",
            "evidence": "anchor-callee-external",
            "confidence": "medium",
            "parent_bucket": parent_records[stream_new]["bucket"],
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
                "scope": "frontier" if entry in frontier else "freetype-bucket",
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
            "snapshot": "third_party/freetype (PROVENANCE.json-verified sources)",
            "provenance": PROVENANCE.name,
        },
        "reconciliation": {
            "frontier_functions": len(frontier),
            "frontier_official_bytes": frontier_bytes,
            "frontier_51_functions": len(frontier_51),
            "frontier_51_official_bytes": sum(
                row["official_opaque_bytes"] for row in frontier_51.values()
            ),
            "frontier_52_functions": len(frontier_52),
            "frontier_52_official_bytes": sum(
                row["official_opaque_bytes"] for row in frontier_52.values()
            ),
            "freetype_bucket_functions": len(bucket),
            "freetype_bucket_official_bytes": bucket_bytes,
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
            "the face-open path is vendor-extended (the 9-slot font fallback loader below FT_Open_Face); cluster membership does not imply stock 2.9.1 bodies",
            "base-call-graph-indirect members rest on community topology alone; shared utility functions also called by other modules are included at low confidence",
            "upstream-table-match located seven snapshot constant tables in the image, all referenced only outside this frontier; the CFF/TrueType/sfnt/smooth/autofit driver bodies are therefore bounded outside the 0x51/0x52xxxx regions",
            "Ghidra envelope boundaries are analyzer artifacts inherited from the corpus",
        ],
        "functions": map_rows,
    }


def map_tsv(report: dict[str, Any]) -> str:
    lines = [
        "# G2 FreeType engine census; regenerated by "
        "tools/analyze_g2_freetype_engine_census.py",
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
        "G2 FreeType engine census: PASS",
        f"  frontier: {reconciliation['frontier_functions']} functions, "
        f"{reconciliation['frontier_official_bytes']} official bytes "
        f"(0x51xxxx {reconciliation['frontier_51_functions']}/"
        f"{reconciliation['frontier_51_official_bytes']}, 0x52xxxx "
        f"{reconciliation['frontier_52_functions']}/"
        f"{reconciliation['frontier_52_official_bytes']})",
        f"  freetype bucket: {reconciliation['freetype_bucket_functions']} functions, "
        f"{reconciliation['freetype_bucket_official_bytes']} official bytes",
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
        help="write g2-freetype-engine-census.tsv and -summary.json into DIRECTORY",
    )
    args = parser.parse_args()
    report = analyze(
        args.ghidra_corpus, manifests_dir=args.manifests, snapshot_dir=args.snapshot
    )
    if args.write_manifests is not None:
        directory = args.write_manifests
        directory.mkdir(parents=True, exist_ok=True)
        (directory / "g2-freetype-engine-census.tsv").write_text(
            map_tsv(report), encoding="utf-8"
        )
        (directory / "g2-freetype-engine-census-summary.json").write_text(
            summary_json(report), encoding="utf-8"
        )
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(_text(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
