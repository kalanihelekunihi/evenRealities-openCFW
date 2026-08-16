#!/usr/bin/env python3
"""Cordio link-layer-island census of the 0x5Dxxxx no-evidence sea.

The Apollo unanchored-function provenance census
(``analyze_g2_apollo_unanchored_census.py``) leaves 300 no-evidence functions
(52,866 official bytes) in the ``0x5Dxxxx`` region, initially hypothesized as
LVGL/Nema draw internals.  The LVGL vendor-fork census
(``analyze_g2_lvgl_vendor_fork_census.py``) actively contradicted that: the
sea's only external callers are the Cordio-anchored ``dm_conn.c`` function at
``0x005D2BAE`` (8 edges) and the medium-confidence Cordio function at
``0x005D2E0C`` (4 edges); no LVGL or Ambiq-backend function calls in.  This
analyzer attributes the sea inward from those two anchored Cordio seeds
through the closed call graph and records, per function, exactly one bucket,
one evidence class, and one confidence level.

Evidence tiers, applied in strict priority order:

1. ``cordio-anchor-callee`` (medium) -- a direct static call target of the
   anchored ``dm_conn.c`` function ``0x005D2BAE`` inside the sea.
2. ``cordio-medium-callee`` (medium) -- a direct static call target of the
   medium-confidence Cordio function ``0x005D2E0C`` inside the sea.
3. ``cordio-island-caller`` (low) -- a sea function that statically calls one
   of the two seeds (caller-side evidence only).
4. ``cordio-closure-hop-N`` (low) -- reachable from tiers 1-3 through
   sea-internal static call edges at call-graph hop N (2, 3, or 4).
5. ``none`` (none) -- no directed call path from the dm_conn.c island seeds;
   stays ``investigation-required`` with a deterministic hypothesis.

Cross-checks, all fail-closed:

- The vendored Packetcraft r20.05c ``wsf/include/hci_defs.h`` HCI opcode
  inventory (OGF/OCF macro-resolved) must parse to the pinned census, and no
  sea body may reference any opcode value in a comparison/case context.  This
  tests the HCI-dispatch module hypothesis and rejects it; the three sea
  functions whose *data offsets* alias opcode values (0x200C-0x2010 field
  offsets in serialized storage records) are documented false-positive
  exclusions, verified by context.
- The checked-in LVGL vendor-fork census manifest must record exactly the
  tier-1/tier-2 set as the sea's ``external callers: cordio`` rows and the
  tier-3 function as its single ``calls: cordio`` row.
- The embedded source-path census must keep ``0x005D2BAE`` as the only
  Cordio-anchored function in ``0x5C0000``-``0x5FFFFF``, anchored by the
  ``dm_conn.c`` path string.

The vendored Cordio snapshot (``third_party/cordio``, r20.05c) contains no
link-layer/controller sources -- the five vendored translation units are
host/profile/WSF oracles and the tree closure covers only the 41 selected
paths -- so per-module attribution to public Packetcraft lhci/lmgr/ctrl or
sec units is not defensible offline.  The closure is therefore bucketed as
the ``cordio-ll-island`` vendor link-layer cluster adjacent to the anchored
``dm_conn.c`` island; per-function source ownership requires unavailable
vendor controller source.  Triage labels are queue-ordering evidence, not
ownership claims.

The analyzer is read-only and deterministic.  It re-derives the sea, the
seeds, the closure, and every cross-check from the authenticated image, the
authenticated 64-shard Ghidra corpus, the checked-in parent and LVGL census
manifests, and the vendored Cordio headers on every run; any drift raises
``SeaCensusError``.
"""

from __future__ import annotations

import argparse
import csv
import importlib.util
import json
import re
import sys
from collections import Counter, defaultdict, deque
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PARENT_ANALYZER = ROOT / "tools/analyze_g2_apollo_unanchored_census.py"
PARENT_CENSUS_TSV = ROOT / "tools/manifests/g2-apollo-unanchored-census-functions.tsv"
LVGL_CENSUS_TSV = ROOT / "tools/manifests/g2-lvgl-vendor-fork-census.tsv"
CORDIO_SNAPSHOT = ROOT / "third_party/cordio"
HCI_DEFS_H = CORDIO_SNAPSHOT / "wsf/include/hci_defs.h"

EXPECTED_PARENT_CENSUS_ROWS = 5_610
EXPECTED_LVGL_CENSUS_ROWS = 1_484

SEA_BASE = 0x005D0000
SEA_END = 0x005E0000
EXPECTED_SEA_FUNCTIONS = 300
EXPECTED_SEA_OFFICIAL_BYTES = 52_866
EXPECTED_SEA_LARGEST_ENTRY = 0x005D4ED0
EXPECTED_SEA_LARGEST_ENVELOPE_BYTES = 7_880

# Cordio island seeds.  0x005D2BAE is the only Cordio-path-anchored function
# in 0x5C0000-0x5FFFFF (path third_party\cordio\ble-host\sources\stack\dm\
# dm_conn.c, string evidence); 0x005D2E0C is the parent census's
# medium-confidence Cordio topology member inside the sea address window.
ANCHOR_ENTRY = 0x005D2BAE
MEDIUM_ENTRY = 0x005D2E0C
ANCHOR_PATH = "third_party\\cordio\\ble-host\\sources\\stack\\dm\\dm_conn.c"
ANCHOR_REGION = (0x005C0000, 0x00600000)

# Tier sets, derived from the closed corpus call graph on the first closed
# run and pinned; any drift raises SeaCensusError.
EXPECTED_ANCHOR_CALLEES = (
    0x005D2418,
    0x005D2A18,
    0x005D3238,
    0x005D323E,
    0x005D3252,
    0x005D3268,
    0x005D3272,
    0x005D327E,
)
EXPECTED_MEDIUM_CALLEES = (
    0x005D2A0A,
    0x005D350C,
    0x005D351C,
    0x005D4ED0,
)
EXPECTED_ISLAND_CALLERS = (0x005D3068,)

# Directed sea-internal closure from the seed tiers (BFS hop census).
EXPECTED_HOP_CENSUS = {1: 13, 2: 59, 3: 22, 4: 8}
EXPECTED_CLOSURE_FUNCTIONS = 102
EXPECTED_CLOSURE_OFFICIAL_BYTES = 19_222

# Per-evidence-class (functions, official bytes) roll-up.
EXPECTED_EVIDENCE_CENSUS: dict[str, dict[str, int]] = {
    "cordio-anchor-callee": {"functions": 8, "official_opaque_bytes": 1_492},
    "cordio-medium-callee": {"functions": 4, "official_opaque_bytes": 7_928},
    "cordio-island-caller": {"functions": 1, "official_opaque_bytes": 448},
    "cordio-closure-hop-2": {"functions": 59, "official_opaque_bytes": 5_006},
    "cordio-closure-hop-3": {"functions": 22, "official_opaque_bytes": 3_400},
    "cordio-closure-hop-4": {"functions": 8, "official_opaque_bytes": 948},
    "none": {"functions": 198, "official_opaque_bytes": 33_644},
}
EXPECTED_INVESTIGATION_FUNCTIONS = 198
EXPECTED_INVESTIGATION_OFFICIAL_BYTES = 33_644

# Investigation-required hypothesis census: caller-side neighbours of the
# closure (undirected intra-sea component members with no directed path from
# the seeds), rest functions with external callers outside the sea, and the
# remainder with no static caller at all.
EXPECTED_COMPONENT_ADJACENT = (0x005D188A, 0x005D18C8, 0x005D18EE, 0x005D1958, 0x005D2F22)
EXPECTED_REST_EXTERNAL_CALLEE_ROWS = 6
EXPECTED_REST_NO_CALLER_FUNCTIONS = 192

# Sea-level external topology pins (outside-sea endpoints only).
EXPECTED_SEA_EXTERNAL_CALLERS = (
    0x005CF9E8,
    0x005D2BAE,
    0x005D2E0C,
    0x005E0002,
    0x005E12C8,
    0x005F9FE8,
)
EXPECTED_SEA_FIRST_PARTY_CALLEES = (0x0044A43C, 0x0046CACC, 0x004751C8, 0x005BF004)
EXPECTED_SEA_CORDIO_CALLEE = MEDIUM_ENTRY
EXPECTED_SEA_NO_EVIDENCE_CALLEES = 46

# Vendored hci_defs.h inventory pins and the sea cross-check result.  The
# three documented false positives alias opcode values 0x200C-0x2010 as
# big-endian field offsets into serialized storage records; the
# comparison/case-context scan must find zero opcode references.
EXPECTED_HCI_OGF_OCF_DEFINES = 152
EXPECTED_HCI_OPCODES = 140
EXPECTED_HCI_OPCODE_COMPARISON_HITS = 0
EXPECTED_OPCODE_ALIAS_ROWS = (0x005DD584, 0x005DD780, 0x005DD832)

EVIDENCE_CLASSES = (
    "cordio-anchor-callee",
    "cordio-medium-callee",
    "cordio-island-caller",
    "cordio-closure-hop-2",
    "cordio-closure-hop-3",
    "cordio-closure-hop-4",
    "none",
)
CONFIDENCE_BY_EVIDENCE = {
    "cordio-anchor-callee": "medium",
    "cordio-medium-callee": "medium",
    "cordio-island-caller": "low",
    "cordio-closure-hop-2": "low",
    "cordio-closure-hop-3": "low",
    "cordio-closure-hop-4": "low",
    "none": "none",
}

CENSUS_TSV_HEADER = (
    "entry\tbody_start\tbody_end_exclusive\tenvelope_bytes\t"
    "official_opaque_bytes\tbucket\tevidence\tconfidence\thop\tdetail"
)

OGF_OCF_DEF_RE = re.compile(
    r"#define\s+(HCI_OGF_\w+|HCI_OCF_\w+)\s+(0x[0-9A-Fa-f]+|\d+)\b"
)
OPCODE_DEF_RE = re.compile(
    r"#define\s+HCI_OPCODE_\w+\s+HCI_OPCODE\((HCI_OGF_\w+),\s*(HCI_OCF_\w+)\)"
)
FUNCTION_BEGIN_RE = re.compile(r"OPENCFW_FUNCTION_BEGIN entry=([0-9a-f]+) ")
FUNCTION_END_RE = re.compile(r"OPENCFW_FUNCTION_END entry=([0-9a-f]+)")
COMPARISON_TOKEN_RE = re.compile(r"(?:==|!=|case)\s*\(?\s*0x([0-9a-f]{1,8})\b", re.IGNORECASE)
HEX_TOKEN_RE = re.compile(r"(?<![0-9a-fA-Fx])0x([0-9a-f]{2,8})(?![0-9a-fA-F])", re.IGNORECASE)


class SeaCensusError(RuntimeError):
    """Raised when authenticated evidence or the closed census changes."""


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise SeaCensusError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _load_tsv(path: Path, required: set[str], expected_rows: int, label: str) -> dict[int, dict[str, Any]]:
    if not path.is_file():
        raise SeaCensusError(f"missing {label} manifest: {path}")
    lines = [
        line
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.startswith("#")
    ]
    reader = csv.DictReader(lines, delimiter="\t")
    columns = reader.fieldnames or ()
    if not required <= set(columns):
        raise SeaCensusError(f"{label} schema changed: {columns!r}")
    rows: dict[int, dict[str, Any]] = {}
    for row in reader:
        entry = int(row["entry"], 16)
        if entry in rows:
            raise SeaCensusError(f"duplicate {label} entry {row['entry']}")
        rows[entry] = row
    if len(rows) != expected_rows:
        raise SeaCensusError(
            f"{label} row count changed: {len(rows)} != {expected_rows}"
        )
    return rows


def load_parent_census(tsv_path: Path = PARENT_CENSUS_TSV) -> dict[int, dict[str, Any]]:
    return _load_tsv(
        tsv_path,
        {
            "entry",
            "body_start",
            "body_end_exclusive",
            "envelope_bytes",
            "official_opaque_bytes",
            "bucket",
            "evidence",
            "confidence",
        },
        EXPECTED_PARENT_CENSUS_ROWS,
        "parent census",
    )


def load_lvgl_census(tsv_path: Path = LVGL_CENSUS_TSV) -> dict[int, dict[str, Any]]:
    return _load_tsv(
        tsv_path,
        {"entry", "scope", "module", "evidence", "confidence", "detail"},
        EXPECTED_LVGL_CENSUS_ROWS,
        "LVGL vendor-fork census",
    )


def parse_hci_opcodes(header_path: Path = HCI_DEFS_H) -> dict[int, str]:
    """Resolve the vendored r20.05c HCI opcode inventory.

    ``hci_defs.h`` defines ``HCI_OGF_*``/``HCI_OCF_*`` numerics and derives
    every ``HCI_OPCODE_*`` name through ``HCI_OPCODE(ogf, ocf)``.  The parsed
    census is pinned; any header drift raises ``SeaCensusError``.
    """

    if not header_path.is_file():
        raise SeaCensusError(f"missing vendored header: {header_path}")
    text = header_path.read_text(encoding="utf-8")
    values = {name: int(value, 0) for name, value in OGF_OCF_DEF_RE.findall(text)}
    if len(values) != EXPECTED_HCI_OGF_OCF_DEFINES:
        raise SeaCensusError(
            f"HCI OGF/OCF define census changed: {len(values)} != "
            f"{EXPECTED_HCI_OGF_OCF_DEFINES}"
        )
    opcodes: dict[int, str] = {}
    for ogf, ocf in OPCODE_DEF_RE.findall(text):
        if ogf not in values or ocf not in values:
            raise SeaCensusError(f"unresolved HCI opcode operands {ogf}/{ocf}")
        opcode = (values[ogf] << 10) + values[ocf]
        if opcode in opcodes:
            raise SeaCensusError(f"duplicate HCI opcode value 0x{opcode:04X}")
        opcodes[opcode] = f"HCI_OPCODE({ogf},{ocf})"
    if len(opcodes) != EXPECTED_HCI_OPCODES:
        raise SeaCensusError(
            f"HCI opcode census changed: {len(opcodes)} != {EXPECTED_HCI_OPCODES}"
        )
    return opcodes


def _sea_bodies(logs: list[Path], sea: set[int]) -> dict[int, list[str]]:
    """Decompiled body lines of the sea functions (context scans only)."""

    bodies: dict[int, list[str]] = {}
    current: int | None = None
    for log in logs:
        for line in log.read_text(encoding="utf-8", errors="strict").splitlines():
            begin = FUNCTION_BEGIN_RE.search(line)
            if begin:
                current = int(begin.group(1), 16)
                if current in sea:
                    bodies[current] = []
                continue
            if FUNCTION_END_RE.search(line):
                current = None
                continue
            if current is not None and current in bodies:
                bodies[current].append(line)
    if set(bodies) != sea:
        raise SeaCensusError("sea body extraction drifted")
    return bodies


def analyze(
    corpus_root: Path,
    parent_census: Path = PARENT_CENSUS_TSV,
    lvgl_census: Path = LVGL_CENSUS_TSV,
    hci_defs: Path = HCI_DEFS_H,
) -> dict[str, Any]:
    parent = _load_module("apollo_unanchored_for_cordio_ll_sea", PARENT_ANALYZER)
    path_module = parent._load_path_analyzer()
    path_report = path_module.analyze(corpus_root=corpus_root)

    # --- Seed authentication: the dm_conn.c path anchor. -------------------
    anchor_paths = []
    region_cordio_anchors = []
    for record in path_report["paths"]:
        if record["third_party_dependency"] != "cordio":
            continue
        for reference in record.get("function_references", []):
            entry = reference["entry"]
            if entry == ANCHOR_ENTRY:
                anchor_paths.append((record["relative"], tuple(reference["evidence"])))
            if ANCHOR_REGION[0] <= entry < ANCHOR_REGION[1]:
                region_cordio_anchors.append(entry)
    if anchor_paths != [(ANCHOR_PATH, ("string",))]:
        raise SeaCensusError(
            f"0x{ANCHOR_ENTRY:08X} is no longer the dm_conn.c string anchor: "
            f"{anchor_paths!r}"
        )
    if sorted(set(region_cordio_anchors)) != [ANCHOR_ENTRY]:
        raise SeaCensusError(
            "Cordio anchor census in 0x5C0000-0x5FFFFF changed: "
            + ", ".join(f"0x{e:08X}" for e in sorted(set(region_cordio_anchors)))
        )

    logs = path_module.verify_corpus(corpus_root)
    functions = parent.parse_corpus_functions(logs)
    function_entries = set(functions)

    parent_rows = load_parent_census(parent_census)
    lvgl_rows = load_lvgl_census(lvgl_census)

    # --- Sea derivation from the checked-in parent census. -----------------
    sea = {
        entry
        for entry, row in parent_rows.items()
        if row["bucket"] == "investigation-required-no-evidence"
        and SEA_BASE <= entry < SEA_END
    }
    if len(sea) != EXPECTED_SEA_FUNCTIONS:
        raise SeaCensusError(
            f"0x5Dxxxx sea changed: {len(sea)} != {EXPECTED_SEA_FUNCTIONS}"
        )
    sea_bytes = sum(int(parent_rows[entry]["official_opaque_bytes"]) for entry in sea)
    if sea_bytes != EXPECTED_SEA_OFFICIAL_BYTES:
        raise SeaCensusError(
            f"sea official bytes changed: {sea_bytes} != {EXPECTED_SEA_OFFICIAL_BYTES}"
        )
    for entry in sea:
        corpus_row = functions.get(entry)
        if corpus_row is None:
            raise SeaCensusError(f"sea entry 0x{entry:08X} not in corpus")
        row = parent_rows[entry]
        if (
            corpus_row["body_start"] != int(row["body_start"], 16)
            or corpus_row["body_end_inclusive"] + 1 != int(row["body_end_exclusive"], 16)
        ):
            raise SeaCensusError(f"sea entry 0x{entry:08X} body range drifted")
    largest = max(sea, key=lambda entry: int(parent_rows[entry]["envelope_bytes"]))
    if (
        largest != EXPECTED_SEA_LARGEST_ENTRY
        or int(parent_rows[largest]["envelope_bytes"]) != EXPECTED_SEA_LARGEST_ENVELOPE_BYTES
    ):
        raise SeaCensusError("largest sea member changed")

    medium_row = parent_rows.get(MEDIUM_ENTRY)
    if medium_row is None or (
        medium_row["bucket"],
        medium_row["evidence"],
        medium_row["confidence"],
    ) != ("cordio", "call-topology-single-family", "medium"):
        raise SeaCensusError(
            f"medium Cordio seed 0x{MEDIUM_ENTRY:08X} parent-census row changed"
        )

    def call_targets(entry: int) -> set[int]:
        return functions[entry]["tokens"] & function_entries

    # --- Evidence tiers. ----------------------------------------------------
    anchor_callees = tuple(sorted(t for t in call_targets(ANCHOR_ENTRY) if t in sea))
    if anchor_callees != EXPECTED_ANCHOR_CALLEES:
        raise SeaCensusError(
            "dm_conn.c anchor sea-callee set changed: "
            + ", ".join(f"0x{t:08X}" for t in anchor_callees)
        )
    medium_callees = tuple(
        sorted(t for t in call_targets(MEDIUM_ENTRY) if t in sea and t not in anchor_callees)
    )
    if medium_callees != EXPECTED_MEDIUM_CALLEES:
        raise SeaCensusError(
            "medium Cordio seed sea-callee set changed: "
            + ", ".join(f"0x{t:08X}" for t in medium_callees)
        )
    seed_set = {ANCHOR_ENTRY, MEDIUM_ENTRY}
    island_callers = tuple(
        sorted(
            entry
            for entry in sea
            if call_targets(entry) & seed_set
            and entry not in anchor_callees
            and entry not in medium_callees
        )
    )
    if island_callers != EXPECTED_ISLAND_CALLERS:
        raise SeaCensusError(
            "sea caller-of-seed set changed: "
            + ", ".join(f"0x{t:08X}" for t in island_callers)
        )

    # Directed sea-internal closure from the seed tiers.
    hop: dict[int, int] = {entry: 1 for entry in anchor_callees + medium_callees + island_callers}
    queue = deque(sorted(hop))
    while queue:
        current = queue.popleft()
        for target in sorted(call_targets(current) & sea):
            if target not in hop:
                hop[target] = hop[current] + 1
                queue.append(target)
    hop_census = dict(sorted(Counter(hop.values()).items()))
    if hop_census != EXPECTED_HOP_CENSUS:
        raise SeaCensusError(f"closure hop census changed: {hop_census!r}")
    closure = set(hop)
    if len(closure) != EXPECTED_CLOSURE_FUNCTIONS:
        raise SeaCensusError("closure function count changed")
    closure_bytes = sum(int(parent_rows[e]["official_opaque_bytes"]) for e in closure)
    if closure_bytes != EXPECTED_CLOSURE_OFFICIAL_BYTES:
        raise SeaCensusError(
            f"closure official bytes changed: {closure_bytes} != "
            f"{EXPECTED_CLOSURE_OFFICIAL_BYTES}"
        )

    # --- Undirected intra-sea components, for caller-side adjacency. --------
    adjacent: dict[int, set[int]] = defaultdict(set)
    for entry in sea:
        for target in call_targets(entry) & sea:
            if target != entry:
                adjacent[entry].add(target)
                adjacent[target].add(entry)
    seen: set[int] = set()
    component_adjacent: list[int] = []
    for entry in sorted(sea):
        if entry in seen:
            continue
        stack = [entry]
        component: set[int] = set()
        while stack:
            cursor = stack.pop()
            if cursor in component:
                continue
            component.add(cursor)
            stack.extend(adjacent[cursor])
        seen |= component
        if component & closure:
            component_adjacent.extend(sorted(component - closure))
    if tuple(component_adjacent) != EXPECTED_COMPONENT_ADJACENT:
        raise SeaCensusError(
            "caller-side closure-adjacent set changed: "
            + ", ".join(f"0x{e:08X}" for e in component_adjacent)
        )
    component_adjacent_set = set(component_adjacent)

    # --- Sea-level external topology pins. ----------------------------------
    callers_into_sea: dict[int, set[int]] = defaultdict(set)
    for entry in function_entries:
        for target in call_targets(entry):
            if target in sea and target != entry and entry not in sea:
                callers_into_sea[target].add(entry)
    sea_external_callers = tuple(
        sorted({caller for targets_set in callers_into_sea.values() for caller in targets_set})
    )
    if sea_external_callers != EXPECTED_SEA_EXTERNAL_CALLERS:
        raise SeaCensusError(
            "sea external caller census changed: "
            + ", ".join(f"0x{c:08X}" for c in sea_external_callers)
        )
    sea_external_callees = sorted(
        {t for entry in sea for t in call_targets(entry) if t not in sea}
    )
    first_party_callees = tuple(
        t for t in sea_external_callees
        if parent_rows.get(t, {}).get("bucket") == "first-party"
    )
    if first_party_callees != EXPECTED_SEA_FIRST_PARTY_CALLEES:
        raise SeaCensusError(
            "sea first-party callee census changed: "
            + ", ".join(f"0x{t:08X}" for t in first_party_callees)
        )
    cordio_callees = tuple(
        t for t in sea_external_callees
        if parent_rows.get(t, {}).get("bucket") == "cordio"
    )
    if cordio_callees != (EXPECTED_SEA_CORDIO_CALLEE,):
        raise SeaCensusError("sea Cordio callee census changed")
    no_evidence_callees = sum(
        1
        for t in sea_external_callees
        if parent_rows.get(t, {}).get("bucket") == "investigation-required-no-evidence"
    )
    if no_evidence_callees != EXPECTED_SEA_NO_EVIDENCE_CALLEES:
        raise SeaCensusError(
            f"sea no-evidence callee census changed: {no_evidence_callees} != "
            f"{EXPECTED_SEA_NO_EVIDENCE_CALLEES}"
        )
    other_callees = [
        t
        for t in sea_external_callees
        if parent_rows.get(t, {}).get("bucket")
        not in ("first-party", "cordio", "investigation-required-no-evidence")
    ]
    if other_callees:
        raise SeaCensusError(
            "sea gained callees of another family: "
            + ", ".join(f"0x{t:08X}" for t in other_callees)
        )

    # --- LVGL census cross-check: the contradiction finding must persist. ---
    lvgl_cordio_caller_rows = sorted(
        entry
        for entry in sea
        if "external callers: cordio" in (lvgl_rows[entry]["detail"] or "")
    )
    if lvgl_cordio_caller_rows != sorted(set(anchor_callees) | set(medium_callees)):
        raise SeaCensusError("LVGL census cordio-caller rows no longer match the seed callees")
    lvgl_calls_cordio_rows = sorted(
        entry for entry in sea if "calls: cordio" in (lvgl_rows[entry]["detail"] or "")
    )
    if lvgl_calls_cordio_rows != list(EXPECTED_ISLAND_CALLERS):
        raise SeaCensusError("LVGL census calls-cordio rows no longer match the island callers")
    for entry in sea:
        lvgl_row = lvgl_rows[entry]
        if (lvgl_row["scope"], lvgl_row["module"], lvgl_row["evidence"]) != (
            "sea-0x5d",
            "investigation-required",
            "none",
        ):
            raise SeaCensusError(
                f"LVGL census row for sea entry 0x{entry:08X} changed"
            )

    # --- Vendored-header HCI opcode cross-check. ----------------------------
    opcodes = parse_hci_opcodes(hci_defs)
    bodies = _sea_bodies(logs, sea)
    comparison_hits = {}
    alias_rows = {}
    for entry in sorted(sea):
        for line in bodies[entry]:
            for token in COMPARISON_TOKEN_RE.findall(line):
                value = int(token, 16)
                if value in opcodes:
                    comparison_hits.setdefault(entry, set()).add(value)
            for token in HEX_TOKEN_RE.findall(line):
                value = int(token, 16)
                if value in opcodes:
                    alias_rows.setdefault(entry, set()).add(value)
    if comparison_hits:
        raise SeaCensusError(
            "sea bodies reference vendored HCI opcodes in comparison context: "
            + ", ".join(f"0x{e:08X}" for e in sorted(comparison_hits))
        )
    if len(comparison_hits) != EXPECTED_HCI_OPCODE_COMPARISON_HITS:
        raise SeaCensusError("HCI opcode comparison census changed")
    if tuple(sorted(alias_rows)) != EXPECTED_OPCODE_ALIAS_ROWS:
        raise SeaCensusError(
            "opcode-value alias census changed: "
            + ", ".join(f"0x{e:08X}" for e in sorted(alias_rows))
        )

    # --- Row assembly. --------------------------------------------------------
    records: list[dict[str, Any]] = []
    for entry in sorted(sea):
        row = parent_rows[entry]
        record: dict[str, Any] = {
            "entry": entry,
            "body_start": int(row["body_start"], 16),
            "body_end_exclusive": int(row["body_end_exclusive"], 16),
            "envelope_bytes": int(row["envelope_bytes"]),
            "official_opaque_bytes": int(row["official_opaque_bytes"]),
            "bucket": None,
            "evidence": None,
            "confidence": None,
            "hop": None,
            "detail": "",
        }
        if entry in anchor_callees:
            record.update(
                bucket="cordio-ll-island",
                evidence="cordio-anchor-callee",
                hop=1,
                detail=f"direct static callee of the anchored dm_conn.c function "
                f"0x{ANCHOR_ENTRY:08X}",
            )
        elif entry in medium_callees:
            record.update(
                bucket="cordio-ll-island",
                evidence="cordio-medium-callee",
                hop=1,
                detail=f"direct static callee of the medium-confidence Cordio "
                f"function 0x{MEDIUM_ENTRY:08X}",
            )
        elif entry in island_callers:
            record.update(
                bucket="cordio-ll-island",
                evidence="cordio-island-caller",
                hop=1,
                detail=f"statically calls the Cordio-island seed "
                f"0x{MEDIUM_ENTRY:08X}; caller-side evidence",
            )
        elif entry in hop:
            distance = hop[entry]
            record.update(
                bucket="cordio-ll-island",
                evidence=f"cordio-closure-hop-{distance}",
                hop=distance,
                detail=f"reachable from the dm_conn.c island seeds at call-graph "
                f"hop {distance} through sea-internal edges",
            )
        else:
            hints = []
            external = sorted(callers_into_sea.get(entry, ()))
            if external:
                families = sorted(
                    {
                        parent_rows[caller]["bucket"]
                        if caller in parent_rows
                        else "path-anchored"
                        for caller in external
                    }
                )
                hints.append(
                    "external callers: "
                    + "|".join(families)
                    + " ("
                    + ",".join(f"0x{caller:08X}" for caller in external)
                    + ")"
                )
            else:
                hints.append(
                    "no static caller in the corpus; function-pointer/"
                    "table-dispatched or dead-stripped candidate"
                )
            if entry in component_adjacent_set:
                hints.append(
                    "caller-side neighbour of the Cordio-island closure "
                    "(undirected intra-sea component member)"
                )
            hints.append("no directed call path from the dm_conn.c island seeds")
            record.update(
                bucket="investigation-required",
                evidence="none",
                detail="; ".join(hints),
            )
        record["confidence"] = CONFIDENCE_BY_EVIDENCE[record["evidence"]]
        records.append(record)

    # --- Fail-closed census reconciliation. -----------------------------------
    evidence_stats: dict[str, dict[str, int]] = defaultdict(
        lambda: {"functions": 0, "official_opaque_bytes": 0}
    )
    for record in records:
        stats = evidence_stats[record["evidence"]]
        stats["functions"] += 1
        stats["official_opaque_bytes"] += record["official_opaque_bytes"]
    derived_evidence = {name: dict(stats) for name, stats in sorted(evidence_stats.items())}
    if derived_evidence != EXPECTED_EVIDENCE_CENSUS:
        raise SeaCensusError(f"evidence census changed: {derived_evidence!r}")
    investigation = [record for record in records if record["bucket"] == "investigation-required"]
    if len(investigation) != EXPECTED_INVESTIGATION_FUNCTIONS:
        raise SeaCensusError("investigation-required function count changed")
    investigation_bytes = sum(record["official_opaque_bytes"] for record in investigation)
    if investigation_bytes != EXPECTED_INVESTIGATION_OFFICIAL_BYTES:
        raise SeaCensusError("investigation-required official bytes changed")
    rest_external = [r for r in investigation if callers_into_sea.get(r["entry"])]
    if len(rest_external) != EXPECTED_REST_EXTERNAL_CALLEE_ROWS:
        raise SeaCensusError("rest external-caller census changed")
    rest_no_caller = [r for r in investigation if not callers_into_sea.get(r["entry"])]
    if len(rest_no_caller) != EXPECTED_REST_NO_CALLER_FUNCTIONS:
        raise SeaCensusError("rest no-caller census changed")

    attributed = [record for record in records if record["bucket"] == "cordio-ll-island"]
    attributed_bytes = sum(record["official_opaque_bytes"] for record in attributed)

    return {
        "schema_version": 1,
        "analysis_mode": "read-only; no signing, flashing, erase, or hardware operation",
        "target": "official G2 s200_v2.2.6.10 Apollo main",
        "inputs": {
            "image_sha256": path_report["image"]["sha256"],
            "ghidra_sha256sums_sha256": path_report["ghidra_correlation"]["corpus"][
                "sha256sums_sha256"
            ],
            "parent_census_manifest": PARENT_CENSUS_TSV.name,
            "lvgl_census_manifest": LVGL_CENSUS_TSV.name,
            "cordio_snapshot": "third_party/cordio (r20.05c; headers only for this census)",
        },
        "seeds": {
            "anchor_entry": f"0x{ANCHOR_ENTRY:08X}",
            "anchor_path": ANCHOR_PATH,
            "anchor_evidence": "string",
            "medium_entry": f"0x{MEDIUM_ENTRY:08X}",
            "medium_parent_evidence": "call-topology-single-family",
        },
        "reconciliation": {
            "sea_functions": len(records),
            "sea_official_bytes": sea_bytes,
            "sea_largest_entry": f"0x{EXPECTED_SEA_LARGEST_ENTRY:08X}",
            "sea_largest_envelope_bytes": EXPECTED_SEA_LARGEST_ENVELOPE_BYTES,
            "attributed_functions": len(attributed),
            "attributed_official_bytes": attributed_bytes,
            "investigation_functions": len(investigation),
            "investigation_official_bytes": investigation_bytes,
            "hop_census": {str(k): v for k, v in hop_census.items()},
            "evidence_classes": derived_evidence,
            "sea_external_callers": [f"0x{c:08X}" for c in sea_external_callers],
            "sea_first_party_callees": [f"0x{t:08X}" for t in first_party_callees],
            "hci_opcodes_parsed": len(opcodes),
            "hci_opcode_comparison_hits": len(comparison_hits),
            "opcode_alias_rows": [f"0x{e:08X}" for e in sorted(alias_rows)],
            "component_adjacent": [f"0x{e:08X}" for e in component_adjacent],
        },
        "limitations": [
            "bucket membership is call-topology triage for queue ordering, not per-function source ownership or behavioral reconstruction",
            "the cordio-ll-island bucket is a vendor link-layer cluster hypothesis anchored on the dm_conn.c path-string island; the vendored r20.05c snapshot contains no controller/LL sources, so public-Packetcraft per-module attribution (lhci/lmgr/ctrl/sec) is not defensible offline",
            "hop-N closure labels are low-confidence structural inferences and never feed further propagation",
            "call targets are recovered from address tokens in decompiled bodies; data references that alias function entries are indistinguishable from calls",
            "the HCI opcode cross-check rejects HCI dispatch in the sea only for the vendored public opcode inventory; vendor-specific opcodes (OGF 0x3F) are not enumerable from the snapshot",
        ],
        "functions": records,
    }


def census_tsv(report: dict[str, Any]) -> str:
    lines = [
        "# G2 Cordio link-layer-island census of the 0x5Dxxxx sea; regenerated by "
        "tools/analyze_g2_cordio_ll_sea_census.py",
        CENSUS_TSV_HEADER,
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
                    "" if record["hop"] is None else str(record["hop"]),
                    record["detail"],
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
            "seeds",
            "reconciliation",
            "limitations",
        )
    }
    return json.dumps(summary, indent=2, sort_keys=True) + "\n"


def _text(report: dict[str, Any]) -> str:
    reconciliation = report["reconciliation"]
    lines = [
        "G2 Cordio link-layer-island sea census: PASS",
        f"  sea: {reconciliation['sea_functions']} functions, "
        f"{reconciliation['sea_official_bytes']} official bytes",
        f"  cordio-ll-island: {reconciliation['attributed_functions']} functions, "
        f"{reconciliation['attributed_official_bytes']} official bytes",
        f"  investigation-required: {reconciliation['investigation_functions']} "
        f"functions, {reconciliation['investigation_official_bytes']} official bytes",
        f"  closure hops: {reconciliation['hop_census']}",
        f"  HCI opcode cross-check: {reconciliation['hci_opcodes_parsed']} vendored "
        f"opcodes, {reconciliation['hci_opcode_comparison_hits']} comparison-context hits",
        "hardware/flash operations: none",
    ]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ghidra-corpus", type=Path, required=True)
    parser.add_argument("--parent-census", type=Path, default=PARENT_CENSUS_TSV)
    parser.add_argument("--lvgl-census", type=Path, default=LVGL_CENSUS_TSV)
    parser.add_argument("--hci-defs", type=Path, default=HCI_DEFS_H)
    parser.add_argument("--json", action="store_true")
    parser.add_argument(
        "--write-manifests",
        type=Path,
        metavar="DIRECTORY",
        help="write g2-cordio-ll-sea-census.tsv and -summary.json into DIRECTORY",
    )
    args = parser.parse_args()
    report = analyze(
        args.ghidra_corpus,
        parent_census=args.parent_census,
        lvgl_census=args.lvgl_census,
        hci_defs=args.hci_defs,
    )
    if args.write_manifests is not None:
        directory = args.write_manifests
        directory.mkdir(parents=True, exist_ok=True)
        (directory / "g2-cordio-ll-sea-census.tsv").write_text(
            census_tsv(report), encoding="utf-8"
        )
        (directory / "g2-cordio-ll-sea-census-summary.json").write_text(
            summary_json(report), encoding="utf-8"
        )
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(_text(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
