#!/usr/bin/env python3
"""liblc3 ltpf/bits cluster census of the 0x43xxxx island.

The liblc3 encoder-internals census
(``analyze_g2_liblc3_encoder_internals.py``) attributes 41 of the 72
``0x59xxxx``-scope functions to liblc3 v1.1.3 modules and records, as
out-of-scope dispatch observations, that the ``ltpf.c`` and ``bits.c``
cores are linked in the early ``0x43xxxx`` island: six functions reached
directly from ``lc3_encode`` (``lc3_ltpf_analyse`` 0x00438FB8, IAR
``memmove`` 0x00439710, ``lc3_setup_bits`` 0x00439868, the
``lc3_put_bits`` slow path 0x00439B12, ``lc3_ltpf_put_data`` 0x004396C2,
``lc3_flush_bits`` 0x004399E4).  This analyzer censuses that island
cluster as an additive, self-contained increment; it never modifies or
re-buckets the parent censuses.

Scope is exactly 26 rows, derived deterministically from the
authenticated corpus and image:

1. ``seed-closure`` (15) -- the forward static-call closure, inside the
   island, of the six ``lc3_encode`` island callees.
2. ``seed-closure-extension`` (4) -- island functions whose entire corpus
   caller set lies inside the closure union the parent-census liblc3
   universe (the 41 attributed functions plus ``lc3_tns_analyze``).
3. ``dispatch-table`` (4) -- in-corpus targets of the byte-verified
   ``resample_12k8[]`` static pointer table at 0x00439680, referenced by
   ``lc3_ltpf_analyse`` and stored in ``LC3_SRATE`` enum order.
4. ``dispatch-table-non-corpus`` (2) -- table targets 0x00438400 and
   0x00438604, which Ghidra never emitted as functions; their Thumb
   addresses are byte-verified table entries but no envelope exists in
   the corpus.
5. ``dispatch-table-callee`` (1) -- the outlined helper 0x00438BF0 whose
   caller set is exactly two dispatch-table entries.

Evidence tiers, applied in strict priority order; every row gets exactly
one status, module, evidence class, and confidence level:

1. ``dispatch-graph-direct`` (medium) -- the five liblc3 seeds, direct
   static callees of ``lc3_encode`` at fixed v1.1.3 ``lc3.c``
   ``analyze()``/``encode()`` source positions, re-derived from the
   corpus on every run and cross-checked against the parent census's
   pinned external-dispatch observations.
2. ``dispatch-graph-external`` (low) -- the sixth seed, IAR ``memmove``,
   a compiler-runtime callee of ``lc3_encode``; never module-attributed.
3. ``dispatch-table-entry`` (high) -- the six distinct
   ``resample_12k8[]`` targets, Thumb pointers byte-verified against the
   image in ``LC3_SRATE`` enum order; in-corpus entries cross-checked
   against their module-private resample-coefficient tables.
4. ``upstream-table-match`` (high) -- literal-pool cells point (directly
   or through one indirection) into a vendored-snapshot C array matched
   byte-for-byte in the image and private to exactly one liblc3 module.
5. ``dispatch-graph-indirect`` (low) -- reachable only through cluster
   or parent-census liblc3 functions; the full corpus caller set is
   pinned exactly.
6. ``caller-family-shared`` (low) -- called from both the liblc3 cluster
   and non-liblc3 code; a shared compiler-runtime helper, never
   module-attributed (``sqrtf`` candidate 0x004397A8 and its
   domain-error helper 0x00439CA4).
7. ``investigation-required`` (none) -- no admissible liblc3 module
   evidence (0x004396B8).

The analyzer is read-only and deterministic.  It re-derives the scope,
the seed sequence, the dispatch table, the table evidence, every caller
set, and the island composition from authenticated inputs on every run;
any drift against the pinned expectations raises ``CensusError``.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SIBLING_ANALYZER = ROOT / "tools/analyze_g2_liblc3_encoder_internals.py"
MANIFESTS = ROOT / "tools/manifests"
SNAPSHOT = ROOT / "third_party/liblc3"

ISLAND_BASE = 0x00438000
ISLAND_END = 0x00440000

EXPECTED_ISLAND_FUNCTIONS = 197
EXPECTED_ISLAND_PARENT_ROWS = 159
EXPECTED_ISLAND_PATH_ANCHORED = 38
# Parent-census buckets over island rows after this census claims its 24
# corpus functions out of the 68-row island no-evidence bucket.
EXPECTED_ISLAND_PARENT_BUCKETS = {
    "lvgl": 79,
    "investigation-required-no-evidence": 68,
    "easylogger": 7,
    "first-party": 5,
}

EXPECTED_TABLES_PARSED = 88
EXPECTED_TABLES_LOCATED = 84

# The ordered island static callees of lc3_encode, in decompiled call
# order, at the fixed v1.1.3 lc3.c analyze()/encode() source positions.
# Re-derived from the corpus and cross-checked against the parent
# census's pinned external-dispatch observations on every run.
EXPECTED_SEEDS = (
    (0x00438FB8, "ltpf", "lc3_ltpf_analyse",
     "analyze() position 2 (after attdet); sole static caller lc3_encode"),
    (0x00439710, None, "IAR memmove",
     "analyze() position 3 (compiler runtime, not liblc3); called from "
     "liblc3 and first-party code"),
    (0x00439868, "bits", "lc3_setup_bits",
     "encode() position 1; sole static caller lc3_encode"),
    (0x00439B12, "bits", "lc3_put_bits_generic",
     "encode() pitch-bit overflow slow path (lc3_put_bits inline spill); "
     "all callers liblc3-side"),
    (0x004396C2, "ltpf", "lc3_ltpf_put_data",
     "encode() position 7 (pitch bit + 9-bit pitch index); sole static "
     "caller lc3_encode"),
    (0x004399E4, "bits", "lc3_flush_bits",
     "encode() final position (padding loop + inlined ac_terminate); sole "
     "static caller lc3_encode"),
)

# Full corpus caller sets of the six seeds, pinned exactly.
EXPECTED_SEED_CALLERS = {
    0x00438FB8: (0x0059138A,),
    0x004396C2: (0x0059138A,),
    0x00439868: (0x0059138A,),
    0x004399E4: (0x0059138A,),
    0x00439B12: (0x004396C2, 0x004399E4, 0x0059138A, 0x00599080, 0x005990CC,
                 0x0059B5C4, 0x0059B6AC),
    0x00439710: (0x00438FB8, 0x0045475A, 0x00524CD6, 0x0054EF08, 0x0056786C,
                 0x0059138A, 0x00599328, 0x005D8E02, 0x005EAB8E, 0x005F51C8),
}

# resample_12k8[] static pointer table: 7 Thumb entries in LC3_SRATE
# enum order (lc3.c common.h: 8K, 16K, 24K, 32K, 48K, 48K_HR, 96K_HR).
# The table address is re-derived from lc3_ltpf_analyse's PTR_FUN label;
# the words are byte-verified against the image.  0x00438400 (16K) and
# 0x00438604 (48K/48K_HR) are absent from the Ghidra corpus.
EXPECTED_RESAMPLE_TABLE = (
    (0x00438D8A, "LC3_SRATE_8K", "resample_8k_12k8"),
    (0x00438400, "LC3_SRATE_16K", "resample_16k_12k8"),
    (0x00438EBA, "LC3_SRATE_24K", "resample_24k_12k8"),
    (0x00438504, "LC3_SRATE_32K", "resample_32k_12k8"),
    (0x00438604, "LC3_SRATE_48K", "resample_48k_12k8"),
    (0x00438604, "LC3_SRATE_48K_HR", "resample_48k_12k8"),
    (0x00438ED4, "LC3_SRATE_96K_HR", "resample_96k_12k8"),
)
EXPECTED_RESAMPLE_NON_CORPUS = (0x00438400, 0x00438604)

# Module-private table evidence, pinned per function: the exact set of
# vendored-snapshot tables ("<source>:<name>") each function's pointer
# cells must hit, and the module they imply.
EXPECTED_TABLE_EVIDENCE = {
    0x00438D8A: ("ltpf", ("ltpf.c:h_8k_12k8_q15",),
                 "resample_8k_12k8 coefficient matrix"),
    0x00438504: ("ltpf", ("ltpf.c:h_32k_12k8_q15",),
                 "resample_32k_12k8 coefficient matrix"),
    0x00438EBA: ("ltpf", ("ltpf.c:h_24k_12k8_q15",),
                 "resample_24k_12k8 coefficient matrix"),
    0x00438ED4: ("ltpf", ("ltpf.c:h_96k_12k8_q15",),
                 "resample_96k_12k8 coefficient matrix"),
    0x00438924: ("ltpf", ("ltpf.c:h4_q15",),
                 "interpolate 4-tap phase filter (in-island table at "
                 "0x00438BD0)"),
}

# Indirect internals: cluster functions reachable only through cluster
# or parent-census liblc3 functions.  The full corpus caller set of each
# is pinned exactly.
EXPECTED_INDIRECT = (
    (0x00438770, "ltpf", (0x00438FB8,),
     "dot candidate (float vector dot product, partially decoded MVE/Helium "
     "body; sole caller lc3_ltpf_analyse)"),
    (0x004387B0, "ltpf", (0x00438FB8,),
     "correlate candidate (correlation vector loop; sole caller "
     "lc3_ltpf_analyse)"),
    (0x00438924, "ltpf", (0x00438FB8,),
     "interpolate (table-pinned h4_q15; sole caller lc3_ltpf_analyse)"),
    (0x00438EF0, "ltpf", (0x00438FB8,),
     "interpolate_corr candidate (8-tap float phase interpolation through "
     "DAT_004396B4 -> 0x006D54D8; sole caller lc3_ltpf_analyse)"),
    (0x00438BF0, "ltpf", (0x00438EBA, 0x00438ED4),
     "resample_x192k_12k8 candidate (outlined helper shared by "
     "resample_24k_12k8 and resample_96k_12k8)"),
    (0x004397D0, "bits", (0x004399E4,),
     "ac_get_range_bits candidate (range bit-count loop; sole caller "
     "lc3_flush_bits)"),
    (0x004397FA, "bits", (0x00439914,),
     "get_bits_left candidate (arithmetic-coder pending-bits accounting; "
     "sole caller lc3_get_bits_left)"),
    (0x00439914, "bits", (0x0059C204,),
     "lc3_get_bits_left candidate (LC3_MAX(get_bits_left, 0); sole caller "
     "lc3_spec_encode 0x0059C204)"),
    (0x0043992C, "bits", (0x004399E4, 0x00439B12),
     "accu_flush clone (backward accumulator flush; callers lc3_flush_bits "
     "and lc3_put_bits_generic, matching the bits.c source callers)"),
    (0x0043996C, "bits", (0x004399E4, 0x00439B54),
     "ac_shift clone (carry propagation; callers lc3_flush_bits (inlined "
     "ac_terminate) and lc3_ac_write_renorm)"),
    (0x00439B54, "bits", (0x0059A9C8, 0x0059B5C4, 0x0059C204),
     "lc3_ac_write_renorm (renormalization loop over ac_shift; callers are "
     "the three lc3_put_symbol sites: 0x0059A9C8 clone, lc3_tns_put_data, "
     "lc3_spec_encode)"),
)

# Shared compiler-runtime helpers inside the closure: their caller sets
# span non-liblc3 code, so they are never module-attributed.  The full
# corpus caller set is pinned exactly.
EXPECTED_SHARED_RUNTIME = (
    (0x004397A8,
     (0x00438FB8, 0x0043A698, 0x004A5D38, 0x00514F3C, 0x005156B8, 0x005171F8,
      0x005179D0, 0x00517E18, 0x00519290, 0x0051A8EC, 0x0051D2E0, 0x0051F798,
      0x005202EC, 0x005639E8, 0x005657D8, 0x00598AB8, 0x00599714, 0x0059BAE4),
     "IAR DLIB sqrtf candidate (SQRT intrinsic; domain-error path through "
     "0x00439CA4; called from ltpf/mdct/sns/spec internals and first-party "
     "code)"),
    (0x00439CA4, (0x004397A8, 0x0059C800),
     "IAR DLIB math domain-error helper candidate (stores EDOM 0x21 through "
     "DAT_00439CD4; called from the sqrtf candidate and first-party "
     "0x0059C800)"),
)

# In-scope but without admissible liblc3 module evidence.
EXPECTED_INVESTIGATION = {
    0x004396B8: (
        (0x0059BAE4,),
        "no ltpf.c/bits.c table, dispatch, or shape evidence; sole caller "
        "lc3_spec_analyze 0x0059BAE4 (parent-census spec.c); 10-byte body "
        "(x*10+1) matches no ltpf.c/bits.c source",
    ),
}

# Scope partition, pinned.
EXPECTED_CLOSURE = (
    0x00438770, 0x004387B0, 0x00438924, 0x00438EF0, 0x00438FB8, 0x004396C2,
    0x00439710, 0x004397A8, 0x004397D0, 0x00439868, 0x0043992C, 0x0043996C,
    0x004399E4, 0x00439B12, 0x00439CA4,
)
EXPECTED_CLOSURE_EXTENSION = (
    0x004396B8, 0x004397FA, 0x00439914, 0x00439B54,
)
EXPECTED_TABLE_CALLEE = (0x00438BF0,)

# The whole 26-row attribution result, pinned.  Any derived drift raises.
# entry -> (status, module, evidence, confidence)
EXPECTED_ATTRIBUTION = {
    0x00438FB8: ("module", "ltpf", "dispatch-graph-direct", "medium"),
    0x004396C2: ("module", "ltpf", "dispatch-graph-direct", "medium"),
    0x00439868: ("module", "bits", "dispatch-graph-direct", "medium"),
    0x00439B12: ("module", "bits", "dispatch-graph-direct", "medium"),
    0x004399E4: ("module", "bits", "dispatch-graph-direct", "medium"),
    0x00439710: ("shared-runtime", None, "dispatch-graph-external", "low"),
    0x00438D8A: ("module", "ltpf", "dispatch-table-entry", "high"),
    0x00438400: ("module", "ltpf", "dispatch-table-entry", "high"),
    0x00438EBA: ("module", "ltpf", "dispatch-table-entry", "high"),
    0x00438504: ("module", "ltpf", "dispatch-table-entry", "high"),
    0x00438604: ("module", "ltpf", "dispatch-table-entry", "high"),
    0x00438ED4: ("module", "ltpf", "dispatch-table-entry", "high"),
    0x00438924: ("module", "ltpf", "upstream-table-match", "high"),
    0x00438770: ("module", "ltpf", "dispatch-graph-indirect", "low"),
    0x004387B0: ("module", "ltpf", "dispatch-graph-indirect", "low"),
    0x00438EF0: ("module", "ltpf", "dispatch-graph-indirect", "low"),
    0x00438BF0: ("module", "ltpf", "dispatch-graph-indirect", "low"),
    0x004397D0: ("module", "bits", "dispatch-graph-indirect", "low"),
    0x004397FA: ("module", "bits", "dispatch-graph-indirect", "low"),
    0x00439914: ("module", "bits", "dispatch-graph-indirect", "low"),
    0x0043992C: ("module", "bits", "dispatch-graph-indirect", "low"),
    0x0043996C: ("module", "bits", "dispatch-graph-indirect", "low"),
    0x00439B54: ("module", "bits", "dispatch-graph-indirect", "low"),
    0x004397A8: ("shared-runtime", None, "caller-family-shared", "low"),
    0x00439CA4: ("shared-runtime", None, "caller-family-shared", "low"),
    0x004396B8: ("investigation-required", None, "none", "none"),
}

EXPECTED_SCOPE_ROWS = 26
EXPECTED_SCOPE_CORPUS_ROWS = 24
EXPECTED_ATTRIBUTED_ROWS = 22
EXPECTED_ATTRIBUTED_OFFICIAL_BYTES = 5_108
EXPECTED_SHARED_RUNTIME_ROWS = 3
EXPECTED_SHARED_RUNTIME_OFFICIAL_BYTES = 0
EXPECTED_INVESTIGATION_ROWS = 1
EXPECTED_INVESTIGATION_OFFICIAL_BYTES = 10
# Remaining island no-evidence rows after this census claims its 24.
EXPECTED_ISLAND_FRONTIER_REMAINDER = 44

# Per-module roll-up over the 26-row scope: module -> (rows, corpus
# functions, official_opaque_bytes).  The two non-corpus ltpf rows carry
# no byte attribution.
EXPECTED_MODULE_SUMMARY = {
    "ltpf": (13, 11, 4_094),
    "bits": (9, 9, 1_014),
}

MODULES = ("ltpf", "bits")
STATUSES = ("module", "shared-runtime", "investigation-required")
EVIDENCE_CLASSES = (
    "dispatch-graph-direct",
    "dispatch-graph-external",
    "dispatch-table-entry",
    "upstream-table-match",
    "dispatch-graph-indirect",
    "caller-family-shared",
    "none",
)
CONFIDENCE_ORDER = ("high", "medium", "low", "none")

MAP_TSV_HEADER = (
    "entry\tbody_start\tbody_end_exclusive\tenvelope_bytes\t"
    "official_opaque_bytes\tscope\tparent_bucket\tstatus\tmodule\t"
    "attribution\tevidence\tconfidence\tdetail"
)


class CensusError(RuntimeError):
    """Raised when authenticated evidence or a closed census changes."""


def _load_sibling():
    spec = importlib.util.spec_from_file_location(
        "liblc3_encoder_internals_for_ltpf_bits_cluster", SIBLING_ANALYZER
    )
    if spec is None or spec.loader is None:
        raise CensusError(f"cannot load {SIBLING_ANALYZER}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def parse_tables(snapshot_dir: Path = SNAPSHOT) -> dict[str, bytes]:
    """SNAPSHOT.sha256-verified snapshot tables via the parent parser."""

    sibling = _load_sibling()
    try:
        return sibling.parse_snapshot_tables(snapshot_dir)
    except sibling.CensusError as error:
        raise CensusError(str(error)) from error


def _ordered_unique(values: list[int]) -> list[int]:
    return list(dict.fromkeys(values))


def analyze(
    corpus_root: Path,
    manifests_dir: Path = MANIFESTS,
    snapshot_dir: Path = SNAPSHOT,
) -> dict[str, Any]:
    """Fail-closed wrapper: sibling analyzer errors surface as CensusError."""

    try:
        return _analyze_impl(corpus_root, manifests_dir, snapshot_dir)
    except CensusError:
        raise
    except Exception as error:
        # The dynamically loaded parent/sibling analyzers raise their own
        # CensusError classes; surface all of them as this module's.
        if type(error).__name__ == "CensusError":
            raise CensusError(str(error)) from error
        raise


def _analyze_impl(
    corpus_root: Path,
    manifests_dir: Path = MANIFESTS,
    snapshot_dir: Path = SNAPSHOT,
) -> dict[str, Any]:
    sibling = _load_sibling()
    parent = sibling._load_parent()
    parent_report = parent.analyze(corpus_root=corpus_root, manifests_dir=manifests_dir)
    path_module = parent._load_path_analyzer()
    load_base = path_module.LOAD_BASE
    blob = path_module.DEFAULT_IMAGE.read_bytes()

    parent_records = {row["entry"]: row for row in parent_report["functions"]}

    # --- Corpus call graph.
    logs = path_module.verify_corpus(corpus_root)
    functions = sibling.parse_corpus(logs)
    callers = sibling.caller_map(functions)

    # --- Island composition.
    island = sorted(e for e in functions if ISLAND_BASE <= e < ISLAND_END)
    if len(island) != EXPECTED_ISLAND_FUNCTIONS:
        raise CensusError(
            f"0x43xxxx island function census changed: {len(island)} != "
            f"{EXPECTED_ISLAND_FUNCTIONS}"
        )
    island_parent = [e for e in island if e in parent_records]
    if len(island_parent) != EXPECTED_ISLAND_PARENT_ROWS:
        raise CensusError("island parent-census row count changed")
    island_path_anchored = len(island) - len(island_parent)
    if island_path_anchored != EXPECTED_ISLAND_PATH_ANCHORED:
        raise CensusError("island path-anchored function count changed")

    # --- The six seeds: island callees of lc3_encode, in decompiled order.
    public_entries = parent.load_liblc3_entries(manifests_dir)
    lc3_encode = next(
        address for address, name in public_entries.items() if name == "lc3_encode"
    )
    encode_calls = [
        target
        for target in _ordered_unique(functions[lc3_encode]["calls_ordered"])
        if target != lc3_encode
    ]
    seeds_observed = [
        target for target in encode_calls if ISLAND_BASE <= target < ISLAND_END
    ]
    seeds_expected = [entry for entry, _m, _n, _d in EXPECTED_SEEDS]
    if seeds_observed != seeds_expected:
        raise CensusError(
            "lc3_encode island dispatch sequence changed: "
            + ", ".join(f"0x{t:08x}" for t in seeds_observed)
        )
    # Cross-check against the parent census's pinned external observations.
    sibling_external = [
        (entry, module) for entry, module, _name in sibling.EXPECTED_EXTERNAL_DISPATCH
    ]
    if sibling_external != [
        (entry, module) for entry, module, _n, _d in EXPECTED_SEEDS
    ]:
        raise CensusError("parent-census external dispatch observations changed")
    for entry, _module, _name, _detail in EXPECTED_SEEDS:
        observed_callers = tuple(sorted(callers.get(entry, ())))
        if observed_callers != EXPECTED_SEED_CALLERS[entry]:
            raise CensusError(
                f"caller set of seed 0x{entry:08x} changed: "
                + ", ".join(f"0x{c:08X}" for c in observed_callers)
            )

    # --- Scope derivation.
    liblc3_universe = set(sibling.EXPECTED_ATTRIBUTION) | {0x0059AA84}

    closure: set[int] = set()
    stack = list(seeds_expected)
    while stack:
        entry = stack.pop()
        if entry in closure:
            continue
        closure.add(entry)
        for target in functions[entry]["calls_ordered"]:
            if (
                ISLAND_BASE <= target < ISLAND_END
                and target != entry
                and target in functions
            ):
                stack.append(target)
    if tuple(sorted(closure)) != EXPECTED_CLOSURE:
        raise CensusError(
            "seed call closure changed: "
            + ", ".join(f"0x{e:08X}" for e in sorted(closure))
        )

    extension: set[int] = set()
    changed = True
    while changed:
        changed = False
        for entry in island:
            if entry in closure or entry in extension:
                continue
            entry_callers = callers.get(entry, set())
            if entry_callers and entry_callers <= (closure | extension | liblc3_universe):
                extension.add(entry)
                changed = True
    if tuple(sorted(extension)) != EXPECTED_CLOSURE_EXTENSION:
        raise CensusError(
            "closure extension changed: "
            + ", ".join(f"0x{e:08X}" for e in sorted(extension))
        )

    # --- resample_12k8[] dispatch table, byte-verified against the image.
    ltpf_analyse = seeds_expected[0]
    ptr_tables = functions[ltpf_analyse]["ptr_tables"]
    if len(ptr_tables) != 1:
        raise CensusError(
            f"lc3_ltpf_analyse dispatch-table labels changed: {ptr_tables!r}"
        )
    first_target, table_address = next(iter(ptr_tables))
    table_span = 4 * len(EXPECTED_RESAMPLE_TABLE)
    other_labels = [
        (entry, table)
        for entry, row in functions.items()
        for _target, table in row["ptr_tables"]
        if table_address <= table < table_address + table_span
        and entry != ltpf_analyse
    ]
    if other_labels:
        raise CensusError(
            "resample_12k8[] table gained another referrer: "
            + ", ".join(f"0x{e:08x}" for e, _t in other_labels)
        )
    table_targets = []
    for index, (expected_entry, _slot, _name) in enumerate(EXPECTED_RESAMPLE_TABLE):
        word = sibling._word(blob, load_base, table_address + 4 * index)
        if word is None or not word & 1:
            raise CensusError(
                f"resample table entry {index} at 0x{table_address + 4 * index:08X} "
                "is not a Thumb pointer"
            )
        if word & ~1 != expected_entry:
            raise CensusError(
                f"resample table entry {index} changed: 0x{word & ~1:08X} != "
                f"0x{expected_entry:08X}"
            )
        table_targets.append(word & ~1)
    if table_targets[0] != first_target:
        raise CensusError("resample table label disagrees with its first entry")
    following = sibling._word(blob, load_base, table_address + table_span)
    if following is not None and following & 1 and (following & ~1) in functions:
        raise CensusError("resample table grew beyond the LC3_SRATE count")
    table_corpus = sorted({t for t in table_targets if t in functions})
    table_non_corpus = tuple(
        sorted({t for t in table_targets if t not in functions})
    )
    if table_non_corpus != EXPECTED_RESAMPLE_NON_CORPUS:
        raise CensusError(
            "non-corpus resample table entries changed: "
            + ", ".join(f"0x{e:08X}" for e in table_non_corpus)
        )
    table_callee = sorted(
        {
            target
            for entry in table_corpus
            for target in functions[entry]["calls_ordered"]
            if ISLAND_BASE <= target < ISLAND_END
            and target != entry
            and target in functions
            and callers.get(target, set())
            and callers[target] <= set(table_corpus)
        }
    )
    if tuple(table_callee) != EXPECTED_TABLE_CALLEE:
        raise CensusError(
            "dispatch-table callee set changed: "
            + ", ".join(f"0x{e:08X}" for e in table_callee)
        )

    scope: dict[int, str] = {}
    for entry in sorted(closure):
        scope[entry] = "seed-closure"
    for entry in sorted(extension):
        scope[entry] = "seed-closure-extension"
    for entry in table_corpus:
        if entry in scope:
            raise CensusError(f"0x{entry:08X} in both closure and dispatch table")
        scope[entry] = "dispatch-table"
    for entry in table_non_corpus:
        scope[entry] = "dispatch-table-non-corpus"
    for entry in table_callee:
        if entry in scope:
            raise CensusError(f"0x{entry:08X} in both closure and table callees")
        scope[entry] = "dispatch-table-callee"
    if len(scope) != EXPECTED_SCOPE_ROWS:
        raise CensusError(f"scope changed: {len(scope)} != {EXPECTED_SCOPE_ROWS}")
    corpus_scope = [e for e in scope if e in functions]
    if len(corpus_scope) != EXPECTED_SCOPE_CORPUS_ROWS:
        raise CensusError("corpus scope row count changed")

    # --- Vendored-snapshot tables, byte-matched in the official image.
    parsed_tables = sibling.parse_snapshot_tables(snapshot_dir)
    if len(parsed_tables) != EXPECTED_TABLES_PARSED:
        raise CensusError(
            f"snapshot table census changed: {len(parsed_tables)} != "
            f"{EXPECTED_TABLES_PARSED}"
        )
    located = sibling.locate_tables(blob, load_base, parsed_tables)
    if len(located) != EXPECTED_TABLES_LOCATED:
        raise CensusError(
            f"located table census changed: {len(located)} != "
            f"{EXPECTED_TABLES_LOCATED}"
        )
    spans = [
        (address, address + len(parsed_tables[key]), key, sibling.table_module(key))
        for key, address in sorted(located.items())
    ]
    # Module-private table evidence over the whole island: exactly the
    # pinned functions may hold private (ltpf) table hits.
    observed_table_evidence: dict[int, set[str]] = {}
    for entry in island:
        private, _shared = sibling.extract_table_evidence(
            entry, functions, spans, blob, load_base
        )
        if private:
            observed_table_evidence[entry] = private
    if set(observed_table_evidence) != set(EXPECTED_TABLE_EVIDENCE):
        raise CensusError(
            "island module-private table evidence set changed: "
            + ", ".join(f"0x{e:08x}" for e in sorted(observed_table_evidence))
        )
    for entry, (module, keys, _label) in EXPECTED_TABLE_EVIDENCE.items():
        observed_keys = tuple(sorted(observed_table_evidence[entry]))
        if observed_keys != tuple(sorted(keys)):
            raise CensusError(
                f"table evidence for 0x{entry:08x} changed: {observed_keys!r}"
            )
        modules = {sibling.table_module(key) for key in observed_keys}
        if modules != {module}:
            raise CensusError(
                f"table evidence for 0x{entry:08x} spans modules {modules!r}"
            )

    # --- Caller-set pins for indirect, shared-runtime, and triage rows.
    for entry, _module, expected_callers, _hypothesis in EXPECTED_INDIRECT:
        observed = tuple(sorted(callers.get(entry, ())))
        if observed != tuple(sorted(expected_callers)):
            raise CensusError(
                f"caller set of 0x{entry:08x} changed: "
                + ", ".join(f"0x{c:08X}" for c in observed)
            )
    for entry, expected_callers, _hypothesis in EXPECTED_SHARED_RUNTIME:
        observed = tuple(sorted(callers.get(entry, ())))
        if observed != tuple(sorted(expected_callers)):
            raise CensusError(
                f"caller set of shared helper 0x{entry:08x} changed: "
                + ", ".join(f"0x{c:08X}" for c in observed)
            )
        if set(observed) <= (closure | extension | liblc3_universe):
            raise CensusError(
                f"shared helper 0x{entry:08x} lost its non-liblc3 caller family"
            )
    for entry, (expected_callers, _detail) in EXPECTED_INVESTIGATION.items():
        observed = tuple(sorted(callers.get(entry, ())))
        if observed != tuple(sorted(expected_callers)):
            raise CensusError(
                f"caller set of investigation row 0x{entry:08x} changed: "
                + ", ".join(f"0x{c:08X}" for c in observed)
            )

    # --- Attribution assembly (26 rows), tiers in strict priority order.
    rows: dict[int, dict[str, Any]] = {}

    def put(entry, status, module, evidence, confidence, attribution, detail):
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

    for entry, module, name, detail in EXPECTED_SEEDS:
        if module is None:
            put(entry, "shared-runtime", None, "dispatch-graph-external", "low",
                name, detail)
        else:
            put(entry, "module", module, "dispatch-graph-direct", "medium",
                name, "direct lc3_encode island callee at the fixed v1.1.3 "
                "lc3.c source position; " + detail)
    slot_names = {entry: name for entry, _slot, name in EXPECTED_RESAMPLE_TABLE}
    for entry in sorted(set(table_targets)):
        name = slot_names[entry]
        slots = [
            s for e, s, n in EXPECTED_RESAMPLE_TABLE if e == entry
        ]
        detail = (
            f"Thumb pointer in resample_12k8[] slot(s) {'|'.join(slots)} at "
            f"0x{table_address:08X}, byte-verified against the image"
        )
        if entry in EXPECTED_TABLE_EVIDENCE:
            _module, keys, label = EXPECTED_TABLE_EVIDENCE[entry]
            detail += (
                "; references byte-matched snapshot table(s): "
                + "|".join(sorted(keys))
                + f" ({label})"
            )
        else:
            detail += "; body absent from the Ghidra corpus (address-only row)"
        put(entry, "module", "ltpf", "dispatch-table-entry", "high", name, detail)
    for entry, (module, keys, label) in sorted(EXPECTED_TABLE_EVIDENCE.items()):
        if entry in rows:
            # Dispatch-table-tier winners keep their class; verify agreement.
            if rows[entry]["module"] != module:
                raise CensusError(
                    f"dispatch-table/table module conflict at 0x{entry:08x}: "
                    f"{rows[entry]['module']} vs {module}"
                )
            continue
        put(entry, "module", module, "upstream-table-match", "high", label,
            "references byte-matched snapshot table(s): " + "|".join(sorted(keys)))
    for entry, module, _callers, hypothesis in EXPECTED_INDIRECT:
        if entry in rows:
            # Table-tier winners keep their class; verify module agreement.
            if rows[entry]["module"] != module:
                raise CensusError(
                    f"indirect/table module conflict at 0x{entry:08x}: "
                    f"{rows[entry]['module']} vs {module}"
                )
            continue
        put(entry, "module", module, "dispatch-graph-indirect", "low", hypothesis,
            "reachable only through cluster or parent-census liblc3 functions; "
            "caller set pinned")
    for entry, _callers, hypothesis in EXPECTED_SHARED_RUNTIME:
        put(entry, "shared-runtime", None, "caller-family-shared", "low",
            hypothesis, "caller families span non-liblc3 code; shared compiler "
            "runtime, never module-attributed")
    for entry, (_callers, detail) in sorted(EXPECTED_INVESTIGATION.items()):
        put(entry, "investigation-required", None, "none", "none", "", detail)

    # --- Fail-closed comparison against the pinned attribution map.
    derived = {
        entry: (row["status"], row["module"], row["evidence"], row["confidence"])
        for entry, row in rows.items()
    }
    if derived != EXPECTED_ATTRIBUTION:
        for entry in sorted(set(derived) | set(EXPECTED_ATTRIBUTION)):
            if derived.get(entry) != EXPECTED_ATTRIBUTION.get(entry):
                raise CensusError(
                    f"attribution for 0x{entry:08x} changed: "
                    f"{derived.get(entry)!r} != {EXPECTED_ATTRIBUTION.get(entry)!r}"
                )
        raise CensusError("attribution map drifted")
    if set(derived) != set(scope):
        raise CensusError("attribution rows do not cover the 26-row scope")

    # --- Reconciliation.
    def official(entry: int) -> int:
        if entry not in parent_records:
            return 0
        return parent_records[entry]["official_opaque_bytes"]

    def envelope(entry: int) -> int:
        if entry not in parent_records:
            return 0
        return parent_records[entry]["envelope_bytes"]

    for entry in corpus_scope:
        bucket = parent_records[entry]["bucket"]
        if bucket != "investigation-required-no-evidence":
            raise CensusError(
                f"parent bucket of 0x{entry:08x} changed: {bucket!r}"
            )

    attributed = sorted(
        e for e, r in rows.items() if r["status"] == "module"
    )
    shared = sorted(e for e, r in rows.items() if r["status"] == "shared-runtime")
    investigation = sorted(
        e for e, r in rows.items() if r["status"] == "investigation-required"
    )
    attributed_bytes = sum(official(e) for e in attributed)
    shared_bytes = sum(official(e) for e in shared)
    investigation_bytes = sum(official(e) for e in investigation)
    if len(attributed) != EXPECTED_ATTRIBUTED_ROWS:
        raise CensusError("attributed row count changed")
    if attributed_bytes != EXPECTED_ATTRIBUTED_OFFICIAL_BYTES:
        raise CensusError(
            f"attributed official bytes changed: {attributed_bytes} != "
            f"{EXPECTED_ATTRIBUTED_OFFICIAL_BYTES}"
        )
    if len(shared) != EXPECTED_SHARED_RUNTIME_ROWS:
        raise CensusError("shared-runtime row count changed")
    if shared_bytes != EXPECTED_SHARED_RUNTIME_OFFICIAL_BYTES:
        raise CensusError("shared-runtime official bytes changed")
    if len(investigation) != EXPECTED_INVESTIGATION_ROWS:
        raise CensusError("investigation-required row count changed")
    if investigation_bytes != EXPECTED_INVESTIGATION_OFFICIAL_BYTES:
        raise CensusError(
            f"investigation-required official bytes changed: "
            f"{investigation_bytes} != {EXPECTED_INVESTIGATION_OFFICIAL_BYTES}"
        )

    module_summary: dict[str, dict[str, int]] = {}
    for entry in attributed:
        module = rows[entry]["module"]
        summary = module_summary.setdefault(
            module, {"rows": 0, "corpus_functions": 0, "official_bytes": 0}
        )
        summary["rows"] += 1
        summary["corpus_functions"] += 1 if entry in functions else 0
        summary["official_bytes"] += official(entry)
    observed_summary = {
        module: (s["rows"], s["corpus_functions"], s["official_bytes"])
        for module, s in sorted(module_summary.items())
    }
    if observed_summary != EXPECTED_MODULE_SUMMARY:
        raise CensusError(f"module summary changed: {observed_summary!r}")

    # --- Island triage after the claim.
    remaining_buckets: dict[str, int] = {}
    for entry in island_parent:
        bucket = parent_records[entry]["bucket"]
        remaining_buckets[bucket] = remaining_buckets.get(bucket, 0) + 1
    if remaining_buckets != EXPECTED_ISLAND_PARENT_BUCKETS:
        raise CensusError(f"island parent buckets changed: {remaining_buckets!r}")
    frontier_remainder = (
        remaining_buckets["investigation-required-no-evidence"] - len(corpus_scope)
    )
    if frontier_remainder != EXPECTED_ISLAND_FRONTIER_REMAINDER:
        raise CensusError("island no-evidence remainder changed")

    # --- Output rows in address order.
    map_rows = []
    for entry in sorted(scope, key=lambda e: (parent_records.get(e) or {}).get(
        "body_start", e
    )):
        row = rows[entry]
        parent_row = parent_records.get(entry)
        map_rows.append(
            {
                "entry": entry,
                "body_start": parent_row["body_start"] if parent_row else entry,
                "body_end_exclusive": parent_row["body_end_exclusive"]
                if parent_row
                else entry,
                "envelope_bytes": envelope(entry),
                "official_opaque_bytes": official(entry),
                "scope": scope[entry],
                "parent_bucket": parent_row["bucket"]
                if parent_row
                else "not-in-ghidra-corpus",
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
        },
        "reconciliation": {
            "island_functions": len(island),
            "island_parent_rows": len(island_parent),
            "island_path_anchored": island_path_anchored,
            "scope_rows": len(scope),
            "scope_corpus_rows": len(corpus_scope),
            "attributed_rows": len(attributed),
            "attributed_official_bytes": attributed_bytes,
            "shared_runtime_rows": len(shared),
            "shared_runtime_official_bytes": shared_bytes,
            "investigation_rows": len(investigation),
            "investigation_official_bytes": investigation_bytes,
            "island_frontier_remainder": frontier_remainder,
            "snapshot_tables_parsed": len(parsed_tables),
            "snapshot_tables_located": len(located),
            "resample_table_address": f"0x{table_address:08X}",
            "resample_table_non_corpus": [
                f"0x{e:08X}" for e in table_non_corpus
            ],
        },
        "module_summary": [
            {
                "module": module,
                "rows": summary[0],
                "corpus_functions": summary[1],
                "official_opaque_bytes": summary[2],
            }
            for module, summary in EXPECTED_MODULE_SUMMARY.items()
        ],
        "island_composition": {
            "cluster_scope_corpus": len(corpus_scope),
            "parent_buckets": remaining_buckets,
            "path_anchored": island_path_anchored,
        },
        "limitations": [
            "module attribution is evidence-tiered triage, not per-function source ownership or behavioral reconstruction",
            "dispatch-graph-direct positions match the fixed v1.1.3 lc3.c analyze()/encode() source order; indirect names are candidates, not proofs",
            "upstream-table-match proves the stock function reads a byte-identical snapshot table; it does not prove the whole body is pristine upstream code",
            "0x00438400 and 0x00438604 are byte-verified resample_12k8[] entries that Ghidra never emitted as functions; they carry no envelope or byte attribution",
            "the ltpf.c h4 float table parse truncates at implicit trailing initializers, so the strict unique byte-match fails closed and 0x00438EF0 stays a low-confidence candidate despite its pointer landing on h4 row 0 at 0x006D54D8",
            "several bits.c and shared-runtime envelopes report zero official opaque bytes (already production source-owned in the parent census accounting)",
            "Ghidra envelope boundaries and partial MVE/Helium decoding are analyzer artifacts inherited from the corpus",
        ],
        "functions": map_rows,
    }


def map_tsv(report: dict[str, Any]) -> str:
    lines = [
        "# G2 liblc3 ltpf/bits 0x43xxxx cluster census; regenerated by "
        "tools/analyze_g2_liblc3_ltpf_bits_cluster.py",
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
            "island_composition",
            "limitations",
        )
    }
    return json.dumps(summary, indent=2, sort_keys=True) + "\n"


def _text(report: dict[str, Any]) -> str:
    reconciliation = report["reconciliation"]
    lines = [
        "G2 liblc3 ltpf/bits 0x43xxxx cluster census: PASS",
        f"  island: {reconciliation['island_functions']} functions "
        f"({reconciliation['island_parent_rows']} parent-census rows, "
        f"{reconciliation['island_path_anchored']} path-anchored)",
        f"  scope: {reconciliation['scope_rows']} rows "
        f"({reconciliation['scope_corpus_rows']} corpus)",
        f"  attributed: {reconciliation['attributed_rows']} rows, "
        f"{reconciliation['attributed_official_bytes']} official bytes",
        f"  shared-runtime: {reconciliation['shared_runtime_rows']} rows, "
        f"{reconciliation['shared_runtime_official_bytes']} official bytes",
        f"  investigation-required: {reconciliation['investigation_rows']} row, "
        f"{reconciliation['investigation_official_bytes']} official bytes",
        f"  island no-evidence remainder: "
        f"{reconciliation['island_frontier_remainder']} functions",
        f"  snapshot tables: {reconciliation['snapshot_tables_parsed']} parsed, "
        f"{reconciliation['snapshot_tables_located']} uniquely located",
        "  modules:",
    ]
    for module in report["module_summary"]:
        lines.append(
            f"    {module['module']}: {module['rows']} rows "
            f"({module['corpus_functions']} corpus), "
            f"{module['official_opaque_bytes']} official bytes"
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
        help="write g2-liblc3-ltpf-bits-cluster-map.tsv and -summary.json into DIRECTORY",
    )
    args = parser.parse_args()
    report = analyze(
        args.ghidra_corpus, manifests_dir=args.manifests, snapshot_dir=args.snapshot
    )
    if args.write_manifests is not None:
        directory = args.write_manifests
        directory.mkdir(parents=True, exist_ok=True)
        (directory / "g2-liblc3-ltpf-bits-cluster-map.tsv").write_text(
            map_tsv(report), encoding="utf-8"
        )
        (directory / "g2-liblc3-ltpf-bits-cluster-summary.json").write_text(
            summary_json(report), encoding="utf-8"
        )
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(_text(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
