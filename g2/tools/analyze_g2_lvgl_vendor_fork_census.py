#!/usr/bin/env python3
"""LVGL vendor-fork object census for the Apollo-main unanchored frontier.

The [Apollo unanchored-function provenance census](analyze_g2_apollo_unanchored_census.py)
buckets 1,054 unanchored functions (97,430 official opaque bytes) as the LVGL
9.3.0-development vendor fork and hypotheses two no-evidence address seas as
LVGL-related draw internals:

- ``0x5Dxxxx``: 300 functions / 52,866 official bytes ("LVGL vendor-fork
  draw/Nema internals"), and
- ``0x5Axxxx``: 130 functions / 37,058 official bytes ("LVGL/first-party
  draw pipeline").

This analyzer deepens that triage to per-source-object/module granularity
where the authenticated evidence supports it, and keeps every other function
explicitly investigation-required.  Scope (1,484 functions) is re-derived on
every run from the checked-in parent census manifest
``g2-apollo-unanchored-census-functions.tsv`` (itself regenerated and guarded
byte-identically by the parent analyzer), the authenticated Ghidra corpus,
and the authenticated embedded source-path census.

Evidence tiers, applied in strict priority order; every scoped function gets
exactly one module label (or ``investigation-required``), one evidence class,
and one confidence level:

1. ``call-topology-single-file`` (medium) -- every call target that is an
   LVGL-path-anchored corpus function belongs to exactly one retained LVGL
   source file.  This refines the parent census's single-family tier one
   level finer; it is the same structural inference, not a reviewed
   classification.
2. ``call-topology-single-module`` (medium) -- anchored LVGL call targets
   span several files of exactly one module.
3. ``call-topology-second-order-file`` (low) -- no anchored LVGL call
   targets, but every call target carrying a medium-confidence label from
   tier 1/2 belongs to one file.  Propagates only from medium labels, never
   from other low-confidence assignments.
4. ``call-topology-second-order-module`` (low) -- the same collapse at
   module granularity.
5. ``link-order-file-sandwich`` (low) -- the nearest LVGL-path-anchored
   functions on both sides in address order share one file.
6. ``link-order-module-sandwich`` (low) -- the same bracket at module
   granularity.
7. ``investigation-required-mixed`` (none) -- LVGL call evidence spans
   multiple modules.
8. ``investigation-required-no-evidence`` (none) -- no within-LVGL evidence;
   the detail field records the observed external caller/callee families so
   the parent census's region hypotheses are checked, not assumed.

Module labels come only from the 78 retained ``third_party\\lvgl_v9.3``
source paths; the mapping is total and fails closed on any unmapped path.
The Ambiq/Nema vendor-fork backend (``LVGL/src/draw/ambiq``,
``lvgl_ambiq_porting``, ``am_ftsystem.c``) is reported separately from the
public LVGL core.

The analyzer is read-only and deterministic.  Module and file labels are
triage attributions for queue ordering, not per-function source ownership,
behavioral reconstruction, or candidate-readiness claims.
"""

from __future__ import annotations

import argparse
import csv
import importlib.util
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PATH_ANALYZER = ROOT / "tools/analyze_apollo_embedded_source_paths.py"
PARENT_ANALYZER = ROOT / "tools/analyze_g2_apollo_unanchored_census.py"
PARENT_CENSUS_TSV = ROOT / "tools/manifests/g2-apollo-unanchored-census-functions.tsv"

EXPECTED_PARENT_CENSUS_ROWS = 5_610
EXPECTED_LVGL_PATHS = 78
EXPECTED_LVGL_ANCHORED_FUNCTIONS = 344
EXPECTED_SCOPE = {
    # scope: function count
    "lvgl-topology": 613,
    "lvgl-sandwich": 441,
    "sea-0x5d": 300,
    "sea-0x5a": 130,
}
EXPECTED_LVGL_BUCKET_FUNCTIONS = 1_054
EXPECTED_LVGL_BUCKET_OFFICIAL_BYTES = 97_430

LVGL_PATH_PREFIX = "third_party\\lvgl_v9.3\\"

# Vendor-fork backend modules, reported separately from the public LVGL
# core.  ``ambiq-draw-backend`` is the exact public Ambiq subtree
# 1e774257...; the display port is private Ambiq/Even glue (already
# source-owned); ``am_ftsystem.c`` is the Ambiq FreeType system glue.
VENDOR_BACKEND_MODULES = frozenset(
    {"ambiq-draw-backend", "ambiq-display-port", "ambiq-freetype-system"}
)

EVIDENCE_CLASSES = (
    "call-topology-single-file",
    "call-topology-single-module",
    "call-topology-second-order-file",
    "call-topology-second-order-module",
    "link-order-file-sandwich",
    "link-order-module-sandwich",
    "call-topology-mixed",
    "none",
)
CONFIDENCE_BY_EVIDENCE = {
    "call-topology-single-file": "medium",
    "call-topology-single-module": "medium",
    "call-topology-second-order-file": "low",
    "call-topology-second-order-module": "low",
    "link-order-file-sandwich": "low",
    "link-order-module-sandwich": "low",
    "call-topology-mixed": "none",
    "none": "none",
}

# Frozen census expectations, derived from the authenticated inputs on the
# first closed run and pinned so any drift in scope, module census, or
# evidence census raises VendorForkCensusError.
EXPECTED_SCOPE_OFFICIAL_BYTES: dict[str, int] = {
    "lvgl-topology": 67_074,
    "lvgl-sandwich": 30_356,
    "sea-0x5d": 52_866,
    "sea-0x5a": 37_058,
}
EXPECTED_MODULE_CENSUS: dict[str, dict[str, int]] = {
    "ambiq-display-port": {"functions": 1, "official_opaque_bytes": 0},
    "ambiq-draw-backend": {"functions": 13, "official_opaque_bytes": 3_932},
    "ambiq-freetype-system": {"functions": 1, "official_opaque_bytes": 148},
    "investigation-required": {"functions": 680, "official_opaque_bytes": 128_646},
    "lvgl-bin-decoder": {"functions": 2, "official_opaque_bytes": 218},
    "lvgl-cache": {"functions": 13, "official_opaque_bytes": 710},
    "lvgl-core": {"functions": 555, "official_opaque_bytes": 31_740},
    "lvgl-display": {"functions": 17, "official_opaque_bytes": 628},
    "lvgl-draw": {"functions": 33, "official_opaque_bytes": 1_972},
    "lvgl-font": {"functions": 4, "official_opaque_bytes": 922},
    "lvgl-freetype-wrapper": {"functions": 13, "official_opaque_bytes": 604},
    "lvgl-layouts": {"functions": 7, "official_opaque_bytes": 312},
    "lvgl-misc": {"functions": 107, "official_opaque_bytes": 15_232},
    "lvgl-osal-freertos": {"functions": 11, "official_opaque_bytes": 258},
    "lvgl-stdlib": {"functions": 1, "official_opaque_bytes": 76},
    "lvgl-widgets": {"functions": 26, "official_opaque_bytes": 1_956},
}
EXPECTED_EVIDENCE_CENSUS: dict[str, int] = {
    "call-topology-mixed": 57,
    "call-topology-second-order-file": 71,
    "call-topology-second-order-module": 6,
    "call-topology-single-file": 526,
    "call-topology-single-module": 30,
    "link-order-file-sandwich": 81,
    "link-order-module-sandwich": 90,
    "none": 623,
}


class VendorForkCensusError(RuntimeError):
    """Raised when authenticated evidence or the closed census changes."""


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise VendorForkCensusError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def lvgl_module(relative: str) -> tuple[str, str]:
    """Map a retained ``third_party\\lvgl_v9.3`` path to (module, source file).

    The rule set is total over the 78 retained LVGL paths; any unmapped path
    raises ``VendorForkCensusError``.  Returns the module key and a
    repo-style source-file label such as ``LVGL/src/core/lv_obj_style.c``.
    """

    if not relative.startswith(LVGL_PATH_PREFIX):
        raise VendorForkCensusError(f"not an LVGL path: {relative}")
    rest = relative[len(LVGL_PATH_PREFIX):]
    parts = rest.split("\\")
    source_file = rest.replace("\\", "/")
    if parts[0] == "lvgl_ambiq_porting" and parts[-1] == "lv_ambiq_display.c":
        return "ambiq-display-port", source_file
    if parts[0] == "lvgl_ambiq_demo" and parts[-1] == "am_ftsystem.c":
        return "ambiq-freetype-system", source_file
    if parts[0] != "LVGL" or len(parts) < 3 or parts[1] != "src":
        raise VendorForkCensusError(f"LVGL path has no module rule: {relative}")
    sub = parts[2:]
    if sub[0] == "draw" and len(sub) > 1 and sub[1] == "ambiq":
        return "ambiq-draw-backend", source_file
    if sub[0] == "libs" and len(sub) > 1 and sub[1] == "freetype":
        return "lvgl-freetype-wrapper", source_file
    if sub[0] == "libs" and len(sub) > 1 and sub[1] == "bin_decoder":
        return "lvgl-bin-decoder", source_file
    if sub[0] == "libs" and len(sub) > 1 and sub[1] == "bmp":
        return "lvgl-bmp-decoder", source_file
    if sub[0] == "libs" and len(sub) > 1 and sub[1] == "fsdrv":
        return "lvgl-fsdrv", source_file
    if sub[0] == "libs":
        return "lvgl-libs", source_file
    if sub[0] == "misc" and len(sub) > 1 and sub[1] == "cache":
        return "lvgl-cache", source_file
    simple = {
        "core": "lvgl-core",
        "display": "lvgl-display",
        "draw": "lvgl-draw",
        "font": "lvgl-font",
        "indev": "lvgl-indev",
        "layouts": "lvgl-layouts",
        "misc": "lvgl-misc",
        "osal": "lvgl-osal-freertos",
        "stdlib": "lvgl-stdlib",
        "themes": "lvgl-themes",
        "tick": "lvgl-tick",
        "widgets": "lvgl-widgets",
    }
    if sub[0] in simple:
        return simple[sub[0]], source_file
    if len(sub) == 1 and sub[0] == "lv_init.c":
        return "lvgl-core", source_file
    raise VendorForkCensusError(f"LVGL path has no module rule: {relative}")


def load_parent_census(tsv_path: Path = PARENT_CENSUS_TSV) -> dict[int, dict[str, Any]]:
    """Per-function rows of the checked-in parent census manifest."""

    if not tsv_path.is_file():
        raise VendorForkCensusError(f"missing parent census manifest: {tsv_path}")
    lines = [
        line
        for line in tsv_path.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.startswith("#")
    ]
    reader = csv.DictReader(lines, delimiter="\t")
    columns = reader.fieldnames or ()
    required = {
        "entry",
        "body_start",
        "body_end_exclusive",
        "envelope_bytes",
        "official_opaque_bytes",
        "bucket",
        "evidence",
        "confidence",
    }
    if not required <= set(columns):
        raise VendorForkCensusError(f"parent census schema changed: {columns!r}")
    rows: dict[int, dict[str, Any]] = {}
    for row in reader:
        entry = int(row["entry"], 16)
        if entry in rows:
            raise VendorForkCensusError(f"duplicate parent census entry {row['entry']}")
        rows[entry] = row
    if len(rows) != EXPECTED_PARENT_CENSUS_ROWS:
        raise VendorForkCensusError(
            f"parent census row count changed: {len(rows)} != "
            f"{EXPECTED_PARENT_CENSUS_ROWS}"
        )
    return rows


def _scope_of(row: dict[str, Any]) -> str | None:
    entry = int(row["entry"], 16)
    if row["bucket"] == "lvgl" and row["evidence"] == "call-topology-single-family":
        return "lvgl-topology"
    if row["bucket"] == "lvgl" and row["evidence"] == "link-order-sandwich":
        return "lvgl-sandwich"
    if row["bucket"] == "investigation-required-no-evidence":
        if 0x5D0000 <= entry < 0x5E0000:
            return "sea-0x5d"
        if 0x5A0000 <= entry < 0x5B0000:
            return "sea-0x5a"
    return None


def analyze(
    corpus_root: Path,
    census_tsv: Path = PARENT_CENSUS_TSV,
) -> dict[str, Any]:
    parent = _load_module("apollo_unanchored_for_lvgl_census", PARENT_ANALYZER)
    path_module = parent._load_path_analyzer()
    path_report = path_module.analyze(corpus_root=corpus_root)

    # LVGL-path-anchored seed functions, labelled per retained source file.
    lvgl_paths = [
        record
        for record in path_report["paths"]
        if record["third_party_dependency"] == "lvgl_v9.3"
    ]
    if len(lvgl_paths) != EXPECTED_LVGL_PATHS:
        raise VendorForkCensusError(
            f"retained LVGL path census changed: {len(lvgl_paths)} != "
            f"{EXPECTED_LVGL_PATHS}"
        )
    anchor_label: dict[int, tuple[str, str]] = {}
    multi_path = 0
    for record in lvgl_paths:
        module, source_file = lvgl_module(record["relative"])
        for reference in record.get("function_references", []):
            entry = reference["entry"]
            label = (module, source_file)
            if entry in anchor_label and anchor_label[entry] != label:
                multi_path += 1
                continue
            anchor_label[entry] = label
    if multi_path:
        raise VendorForkCensusError(
            f"functions anchored to multiple distinct LVGL paths: {multi_path}"
        )
    if len(anchor_label) != EXPECTED_LVGL_ANCHORED_FUNCTIONS:
        raise VendorForkCensusError(
            f"LVGL anchored function census changed: {len(anchor_label)} != "
            f"{EXPECTED_LVGL_ANCHORED_FUNCTIONS}"
        )

    logs = path_module.verify_corpus(corpus_root)
    functions = parent.parse_corpus_functions(logs)
    function_entries = set(functions)

    parent_rows = load_parent_census(census_tsv)

    # Scope derivation and parent-census reconciliation.
    scope: dict[int, str] = {}
    for entry, row in parent_rows.items():
        selected = _scope_of(row)
        if selected is not None:
            scope[entry] = selected
    scope_counts = Counter(scope.values())
    lvgl_bucket_rows = [
        row for row in parent_rows.values() if row["bucket"] == "lvgl"
    ]
    if len(lvgl_bucket_rows) != EXPECTED_LVGL_BUCKET_FUNCTIONS:
        raise VendorForkCensusError(
            f"parent LVGL bucket changed: {len(lvgl_bucket_rows)} != "
            f"{EXPECTED_LVGL_BUCKET_FUNCTIONS}"
        )
    lvgl_bucket_bytes = sum(int(row["official_opaque_bytes"]) for row in lvgl_bucket_rows)
    if lvgl_bucket_bytes != EXPECTED_LVGL_BUCKET_OFFICIAL_BYTES:
        raise VendorForkCensusError(
            f"parent LVGL bucket bytes changed: {lvgl_bucket_bytes} != "
            f"{EXPECTED_LVGL_BUCKET_OFFICIAL_BYTES}"
        )
    for name, count in EXPECTED_SCOPE.items():
        if scope_counts.get(name, 0) != count:
            raise VendorForkCensusError(
                f"scope {name} changed: {scope_counts.get(name, 0)} != {count}"
            )
    # Every scoped row must be a genuine unanchored corpus function with the
    # body range recorded by the parent census.
    for entry, row in parent_rows.items():
        if entry not in scope:
            continue
        corpus_row = functions.get(entry)
        if corpus_row is None:
            raise VendorForkCensusError(f"scoped entry 0x{entry:08X} not in corpus")
        if (
            corpus_row["body_start"] != int(row["body_start"], 16)
            or corpus_row["body_end_inclusive"] + 1 != int(row["body_end_exclusive"], 16)
        ):
            raise VendorForkCensusError(
                f"scoped entry 0x{entry:08X} body range drifted"
            )
        if entry in anchor_label:
            raise VendorForkCensusError(
                f"scoped entry 0x{entry:08X} gained an LVGL path anchor"
            )

    def call_targets(entry: int) -> set[int]:
        return functions[entry]["tokens"] & function_entries

    # First pass: topology against LVGL-path-anchored seeds.
    first_pass: dict[int, dict[str, Any]] = {}
    medium_label: dict[int, tuple[str, str]] = {}
    for entry in sorted(scope):
        anchored_hits = {anchor_label[t] for t in call_targets(entry) if t in anchor_label}
        if not anchored_hits:
            continue
        files = {label[1] for label in anchored_hits}
        modules = {label[0] for label in anchored_hits}
        if len(files) == 1:
            label = next(iter(anchored_hits))
            first_pass[entry] = {
                "module": label[0],
                "source_file": label[1],
                "evidence": "call-topology-single-file",
                "detail": "every LVGL-anchored call target is in " + label[1],
            }
            medium_label[entry] = label
        elif len(modules) == 1:
            module = next(iter(modules))
            first_pass[entry] = {
                "module": module,
                "source_file": "",
                "evidence": "call-topology-single-module",
                "detail": "LVGL-anchored call targets span "
                + "|".join(sorted(files))
                + " of "
                + module,
            }
            medium_label[entry] = (module, "")
        else:
            first_pass[entry] = {
                "module": "investigation-required",
                "source_file": "",
                "evidence": "call-topology-mixed",
                "detail": "LVGL call evidence spans " + "|".join(sorted(modules)),
            }

    # Second pass: second-order topology from medium labels, then the
    # link-order sandwich against anchored seeds.
    ordered = sorted(function_entries, key=lambda value: functions[value]["body_start"])
    position = {entry: index for index, entry in enumerate(ordered)}

    def sandwich(entry: int) -> tuple[tuple[str, str] | None, tuple[str, str] | None]:
        index = position[entry]
        previous = next(
            (
                anchor_label[ordered[cursor]]
                for cursor in range(index - 1, -1, -1)
                if ordered[cursor] in anchor_label
            ),
            None,
        )
        following = next(
            (
                anchor_label[ordered[cursor]]
                for cursor in range(index + 1, len(ordered))
                if ordered[cursor] in anchor_label
            ),
            None,
        )
        return previous, following

    records: list[dict[str, Any]] = []
    for entry in sorted(scope):
        row = parent_rows[entry]
        record: dict[str, Any] = {
            "entry": entry,
            "body_start": int(row["body_start"], 16),
            "body_end_exclusive": int(row["body_end_exclusive"], 16),
            "envelope_bytes": int(row["envelope_bytes"]),
            "official_opaque_bytes": int(row["official_opaque_bytes"]),
            "scope": scope[entry],
            "module": None,
            "source_file": None,
            "evidence": None,
            "confidence": None,
            "detail": "",
        }
        if entry in first_pass:
            record.update(first_pass[entry])
        else:
            second_order = {
                medium_label[t] for t in call_targets(entry) if t in medium_label
            }
            files = {label[1] for label in second_order if label[1]}
            modules = {label[0] for label in second_order}
            if len(files) == 1 and len(second_order) >= 1 and len(modules) == 1:
                record.update(
                    module=next(iter(modules)),
                    source_file=next(iter(files)),
                    evidence="call-topology-second-order-file",
                    detail="every medium-labelled call target is in " + next(iter(files)),
                )
            elif len(modules) == 1 and second_order:
                record.update(
                    module=next(iter(modules)),
                    source_file="",
                    evidence="call-topology-second-order-module",
                    detail="medium-labelled call targets span " + "|".join(sorted(files)),
                )
            elif len(modules) > 1:
                record.update(
                    module="investigation-required",
                    source_file="",
                    evidence="call-topology-mixed",
                    detail="medium-labelled call targets span " + "|".join(sorted(modules)),
                )
            else:
                previous, following = sandwich(entry)
                if previous is not None and previous == following:
                    record.update(
                        module=previous[0],
                        source_file=previous[1],
                        evidence="link-order-file-sandwich",
                        detail="bracketed in link order by " + previous[1],
                    )
                elif (
                    previous is not None
                    and following is not None
                    and previous[0] == following[0]
                ):
                    record.update(
                        module=previous[0],
                        source_file="",
                        evidence="link-order-module-sandwich",
                        detail="bracketed in link order by " + previous[0],
                    )
                else:
                    record.update(
                        module="investigation-required",
                        source_file="",
                        evidence="none",
                        detail="",
                    )
        record["confidence"] = CONFIDENCE_BY_EVIDENCE[record["evidence"]]
        records.append(record)

    # Honest evidence detail for functions that stay investigation-required:
    # which provider families call into them and which they call, so the
    # parent census's region hypotheses are tested rather than assumed.
    by_entry = {record["entry"]: record for record in records}
    caller_families: dict[int, set[str]] = defaultdict(set)
    for other, corpus_row in functions.items():
        if other in by_entry:
            continue
        for target in call_targets(other) & by_entry.keys():
            family = parent_rows.get(other, {}).get("bucket") or _anchored_family(
                path_report, other
            )
            caller_families[target].add(family)
    for record in records:
        if record["evidence"] != "none":
            continue
        hints = []
        callers = caller_families.get(record["entry"])
        if callers:
            hints.append("external callers: " + "|".join(sorted(callers)))
        callee_buckets = {
            parent_rows[t]["bucket"]
            for t in call_targets(record["entry"])
            if t in parent_rows and t not in by_entry
        }
        callee_buckets.discard("investigation-required-no-evidence")
        if callee_buckets:
            hints.append("calls: " + "|".join(sorted(callee_buckets)))
        record["detail"] = "; ".join(hints) if hints else "no closed-world LVGL evidence"

    return _report(records, path_report, path_module)


def _anchored_family(path_report: dict[str, Any], entry: int) -> str:
    for record in path_report["paths"]:
        for reference in record.get("function_references", []):
            if reference["entry"] == entry:
                dependency = record["third_party_dependency"]
                return dependency if dependency else "first-party-anchored"
    return "anchored"


def _report(
    records: list[dict[str, Any]],
    path_report: dict[str, Any],
    path_module: Any,
) -> dict[str, Any]:
    scope_stats: dict[str, dict[str, int]] = defaultdict(
        lambda: {"functions": 0, "official_opaque_bytes": 0}
    )
    module_stats: dict[str, dict[str, Any]] = defaultdict(
        lambda: {
            "functions": 0,
            "official_opaque_bytes": 0,
            "backend": False,
            "scopes": Counter(),
            "evidence": Counter(),
            "confidence": Counter(),
            "files": Counter(),
        }
    )
    evidence_stats: Counter[str] = Counter()
    for record in records:
        scope = scope_stats[record["scope"]]
        scope["functions"] += 1
        scope["official_opaque_bytes"] += record["official_opaque_bytes"]
        evidence_stats[record["evidence"]] += 1
        module = module_stats[record["module"]]
        module["functions"] += 1
        module["official_opaque_bytes"] += record["official_opaque_bytes"]
        module["backend"] = record["module"] in VENDOR_BACKEND_MODULES
        module["scopes"][record["scope"]] += 1
        module["evidence"][record["evidence"]] += 1
        module["confidence"][record["confidence"]] += 1
        if record["source_file"]:
            module["files"][record["source_file"]] += 1

    derived_scope_bytes = {
        name: stats["official_opaque_bytes"] for name, stats in scope_stats.items()
    }
    if derived_scope_bytes != EXPECTED_SCOPE_OFFICIAL_BYTES:
        raise VendorForkCensusError(
            f"scope byte census changed: {derived_scope_bytes!r}"
        )
    derived_modules = {
        name: {
            "functions": stats["functions"],
            "official_opaque_bytes": stats["official_opaque_bytes"],
        }
        for name, stats in sorted(module_stats.items())
    }
    if derived_modules != EXPECTED_MODULE_CENSUS:
        raise VendorForkCensusError("module census changed")
    derived_evidence = dict(sorted(evidence_stats.items()))
    if derived_evidence != EXPECTED_EVIDENCE_CENSUS:
        raise VendorForkCensusError("evidence census changed")

    module_rows = []
    for name, stats in sorted(module_stats.items()):
        module_rows.append(
            {
                "module": name,
                "vendor_backend": stats["backend"],
                "functions": stats["functions"],
                "official_opaque_bytes": stats["official_opaque_bytes"],
                "scopes": dict(sorted(stats["scopes"].items())),
                "evidence": dict(sorted(stats["evidence"].items())),
                "confidence": dict(sorted(stats["confidence"].items())),
                "top_files": dict(stats["files"].most_common(8)),
            }
        )

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
            "lvgl_retained_paths": EXPECTED_LVGL_PATHS,
            "lvgl_anchored_seed_functions": EXPECTED_LVGL_ANCHORED_FUNCTIONS,
        },
        "reconciliation": {
            "scope_functions": len(records),
            "scopes": {name: dict(stats) for name, stats in sorted(scope_stats.items())},
            "parent_lvgl_bucket_functions": EXPECTED_LVGL_BUCKET_FUNCTIONS,
            "parent_lvgl_bucket_official_bytes": EXPECTED_LVGL_BUCKET_OFFICIAL_BYTES,
            "evidence_classes": derived_evidence,
        },
        "limitations": [
            "module and file labels are triage attributions for queue ordering, not per-function source ownership or behavioral reconstruction",
            "call-topology tiers infer membership from call targets into retained-path anchor functions; a caller that only uses another file's API is indistinguishable from a member of that file",
            "second-order and link-order tiers are low-confidence hypotheses and never feed further propagation",
            "functions with no within-LVGL evidence stay investigation-required; the parent census's 0x5D/0x5A LVGL hypotheses are not confirmed by this census",
        ],
        "modules": module_rows,
        "functions": records,
    }


CENSUS_TSV_HEADER = (
    "entry\tbody_start\tbody_end_exclusive\tenvelope_bytes\t"
    "official_opaque_bytes\tscope\tmodule\tsource_file\tevidence\tconfidence\tdetail"
)


def census_tsv(report: dict[str, Any]) -> str:
    lines = [
        "# G2 LVGL vendor-fork object census; regenerated by "
        "tools/analyze_g2_lvgl_vendor_fork_census.py",
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
                    record["scope"],
                    record["module"],
                    record["source_file"],
                    record["evidence"],
                    record["confidence"],
                    record["detail"],
                )
            )
        )
    return "\n".join(lines) + "\n"


def summary_json(report: dict[str, Any]) -> str:
    summary = {key: report[key] for key in ("schema_version", "analysis_mode", "target", "inputs", "reconciliation", "limitations")}
    summary["modules"] = report["modules"]
    return json.dumps(summary, indent=2, sort_keys=True) + "\n"


def _text(report: dict[str, Any]) -> str:
    reconciliation = report["reconciliation"]
    lines = [
        "G2 LVGL vendor-fork object census: PASS",
        f"  scoped functions: {reconciliation['scope_functions']}",
    ]
    for name, stats in reconciliation["scopes"].items():
        lines.append(
            f"  {name}: {stats['functions']} functions, "
            f"{stats['official_opaque_bytes']} official bytes"
        )
    lines.append("  modules:")
    for module in report["modules"]:
        lines.append(
            f"    {module['module']}: {module['functions']} functions, "
            f"{module['official_opaque_bytes']} official bytes, "
            f"evidence {module['evidence']}"
        )
    lines.append("hardware/flash operations: none")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ghidra-corpus", type=Path, required=True)
    parser.add_argument("--parent-census", type=Path, default=PARENT_CENSUS_TSV)
    parser.add_argument("--json", action="store_true")
    parser.add_argument(
        "--write-manifests",
        type=Path,
        metavar="DIRECTORY",
        help="write g2-lvgl-vendor-fork-census.tsv and -summary.json into DIRECTORY",
    )
    args = parser.parse_args()
    report = analyze(args.ghidra_corpus, census_tsv=args.parent_census)
    if args.write_manifests is not None:
        directory = args.write_manifests
        directory.mkdir(parents=True, exist_ok=True)
        (directory / "g2-lvgl-vendor-fork-census.tsv").write_text(
            census_tsv(report), encoding="utf-8"
        )
        (directory / "g2-lvgl-vendor-fork-census-summary.json").write_text(
            summary_json(report), encoding="utf-8"
        )
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(_text(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
