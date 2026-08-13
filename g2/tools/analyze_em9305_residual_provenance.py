#!/usr/bin/env python3
"""Classify EM9305 residual code-or-mixed segments by provenance evidence.

This analyzer consumes the authenticated residual-segment census
(``analyze_em9305_residual_segments.py``) and assigns every one of its 175
``stock_retained_unresolved_code_or_mixed`` segments (33,658 bytes) a
structural class, a source-ownership category, a confidence, and a compact
evidence record.  Evidence comes only from authenticated, locally checkable
inputs:

- the official firmware blob (hash enforced by the upstream analyzers);
- the authenticated whole-application GNU ARCv2 EM objdump (hash enforced);
- the authenticated exact and link-order function-provenance maps;
- the authenticated nine-entry QF/QK hook function-pointer table at
  ``[0x00335B94,0x00335BB8)`` (hash pinned here from the QP/C audit).

Seven source-ownership categories are used:

1. ``public_upstream_redistribution_safe`` -- a positive match to public
   source with redistribution-safe terms exists.  No residual segment earns
   this category: the tier is defined by the absence of any archive match,
   and no public-source comparison is claimed by this analyzer.
2. ``sdk_oracle_matched_license_unresolved`` -- identity established only
   through the third-party EM9305 SDK v4.2 oracle, which has no
   repository-level license.  No residual segment earns this category for
   the same definitional reason; the category is retained so future
   promotions are explicit.
3. ``vendor_modified_upstream_identified`` -- an upstream role is identified
   but the stock body differs.  Link-order modified placements already cover
   those functions; residual segments have no symbol identity, so none is
   assigned here.
4. ``proprietary_modern_controller_source_unavailable`` -- call-topology
   evidence ties the segment to the modern Packetcraft/EM Bleu controller
   (``LL_VER_NUM=28992``) or to EM vendor system/power support whose
   authoritative source is not publicly obtainable.  Recommendation is
   explicit hash-pinned retention behind the declared controller boundary.
5. ``toolchain_or_linker_generated`` -- MetaWare compiler runtime support or
   linker/vector artifacts.  These are reconstructible without proprietary
   source once the compiler runtime is pinned.
6. ``first_party_application_retained`` -- Even/application-level hook and
   startup glue identified by the authenticated hook-pointer table and the
   QP/C audit.  Stock-retained; clean-room reimplementation is a project
   decision, not a third-party licensing question.
7. ``unclassified_insufficient_evidence`` -- code or mixed bytes whose
   family cannot be established from authenticated evidence.  Retention
   applies; no ownership claim is made.

The analyzer is fail-closed: every aggregate total, the structural hashes of
key segments, and the category census are pinned and verified on each run.
"""

from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import struct
from typing import Any, Sequence

import analyze_em9305_sdk_discovery as discovery
import analyze_em9305_residual_segments as residual
import analyze_em9305_sdk_link_order as link_order


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_IMAGE = discovery.DEFAULT_IMAGE
DEFAULT_CORPUS = ROOT / "research/corpus/em9305"
DEFAULT_TSV = ROOT / "tools/manifests/em9305-residual-provenance-map.tsv"

APP_BASE = discovery.APP_BASE
APP_END = APP_BASE + discovery.APP_SIZE
PACKAGE_MAP_BASE = 0x0030_1FDC
ROM_LO, ROM_HI = 0x0010_0000, 0x0011_0000
RAM_LO, RAM_HI = 0x0080_0000, 0x0081_0000

# Authenticated nine-entry QF/QK hook function-pointer table (QP/C ARCompact
# audit).  Two of its nine little-endian targets fall inside residual
# segments; the other seven are already function-provenance identified.
HOOK_TABLE_START = 0x0033_5B94
HOOK_TABLE_END = 0x0033_5BB8
HOOK_TABLE_SHA256 = "1370d2789d143388ecbd5c84edf4dfaaaf2c059ff69ec59e0f68ff0df0514b51"
HOOK_TABLE_TARGETS = (
    0x0030_EB8C,
    0x0030_ECF8,
    0x0031_114C,
    0x0031_1150,
    0x0031_11A0,
    0x0031_11A4,
    0x0031_161C,
    0x0031_1620,
    0x0031_17E8,
)

# Named 4-byte vendor internal-hook stubs pinned by the QP/C ARCompact audit:
# each is a single ARC ``b`` to the vendor hook implementation.
NAMED_HOOK_STUBS = {
    0x0031_1150: ("QF_onResumeInternalHook", 0x0031_0798),
    0x0031_11A4: ("QF_onStartupInternalHook", 0x0030_482C),
}

# Vendor hook-implementation targets of those stubs.  Only targets that are
# themselves residual-segment starts are classified by this lane.
NAMED_HOOK_TARGET_SEGMENTS = {
    0x0030_482C: "QF_onStartupInternalHook_target",
}

# Authenticated non-portable assertion call sites from the QP/C ARCompact
# audit's exhaustive 31-call topology.  A residual segment containing the
# ``MyApp`` site is first-party application module code; the ``WsfOs`` site
# is already function-provenance identified and is pinned here only as a
# negative guard.
ASSERTION_SITE_MODULES = {
    0x0030_EACE: ("MyApp", 181),
}
ASSERTION_SITE_IDENTIFIED_GUARD = {
    0x0031_40E2: ("WsfOs", 653),
}

# MetaWare runtime segments identified by instruction vocabulary, caller
# topology, and memory-reference patterns (see the audit document).
MEMCPY_MEMSET_SEGMENT_START = 0x0033_2FC4
MEMCPY_MEMSET_SEGMENT_END = 0x0033_3062
ARITH_RUNTIME_SEGMENT_START = 0x0030_2664
STACK_LIMIT_LOW = 0x0080_E978
STACK_LIMIT_HIGH = 0x0080_F978

# Ownership categories (seven; see module docstring).
CAT_PUBLIC_UPSTREAM = "public_upstream_redistribution_safe"
CAT_SDK_ORACLE = "sdk_oracle_matched_license_unresolved"
CAT_VENDOR_MODIFIED = "vendor_modified_upstream_identified"
CAT_PROPRIETARY_CONTROLLER = "proprietary_modern_controller_source_unavailable"
CAT_TOOLCHAIN = "toolchain_or_linker_generated"
CAT_FIRST_PARTY_APP = "first_party_application_retained"
CAT_UNCLASSIFIED = "unclassified_insufficient_evidence"
OWNERSHIP_CATEGORIES = (
    CAT_PUBLIC_UPSTREAM,
    CAT_SDK_ORACLE,
    CAT_VENDOR_MODIFIED,
    CAT_PROPRIETARY_CONTROLLER,
    CAT_TOOLCHAIN,
    CAT_FIRST_PARTY_APP,
    CAT_UNCLASSIFIED,
)

# Archive-label families used for call-frontier inference.
PACKETCRAFT_ARCHIVES = {
    "emb_controller",
    "emb_controller_iso",
    "emb_peripheral",
    "emb_ll_pal",
    "emb_audio",
    "emb_central",
    "radio",
}
EM_VENDOR_ARCHIVES = {
    "em_system",
    "em_system_di03",
    "em_system_stack",
    "em_hw_api",
    "em_hw_api_di03",
    "nvm_fix",
    "nvm_entry",
    "pml",
    "pml_di03",
    "prot_timer",
    "sleep_manager",
    "sleep_timer",
    "unitimer",
    "rc_calib",
    "transport",
    "aoad",
}
FIRST_PARTY_ARCHIVES = {"app_entry", "em_core"}
QPC_ARCHIVES = {"qpc"}

# Packetcraft object-file prefixes seen in link-order placements.
PACKETCRAFT_OBJECT_PREFIXES = (
    "lctr", "ll_", "bb_", "sch_", "lmgr", "hci", "wsf", "pal", "lhci",
)

EXPECTED_RESIDUAL_SEGMENTS = 175
EXPECTED_RESIDUAL_BYTES = 33_658

# Fail-closed pins for the classification produced from the authenticated
# inputs.  Any rule, input, or map drift raises ResidualProvenanceError.
EXPECTED_CATEGORY_COUNTS = {
    CAT_PROPRIETARY_CONTROLLER: 130,
    CAT_TOOLCHAIN: 2,
    CAT_FIRST_PARTY_APP: 7,
    CAT_UNCLASSIFIED: 36,
}
EXPECTED_CATEGORY_BYTES = {
    CAT_PROPRIETARY_CONTROLLER: 30_564,
    CAT_TOOLCHAIN: 980,
    CAT_FIRST_PARTY_APP: 1_224,
    CAT_UNCLASSIFIED: 890,
}
EXPECTED_FAMILY_BYTES = {
    "em_vendor_rom_stub": 16,
    "em_vendor_rom_wrapper": 54,
    "em_vendor_system": 2_952,
    "packetcraft_modern_controller": 27_542,
}
EXPECTED_STRUCTURAL_COUNTS = {
    "code_fragment": 63,
    "code_function": 77,
    "code_leaf_accessor": 12,
    "code_veneer": 13,
    "constant_or_struct_candidate": 5,
    "hook_stub": 2,
    "runtime_support_code": 2,
    "startup_hook_glue": 1,
}
EXPECTED_KEY_SEGMENTS = {
    # start: (size, structural_class, category, family_hint, confidence)
    0x0030_2508: (16, "code_veneer", CAT_PROPRIETARY_CONTROLLER,
                  "em_vendor_rom_stub", "medium"),
    0x0030_2664: (822, "runtime_support_code", CAT_TOOLCHAIN,
                  "metaware_arith_runtime", "high"),
    0x0030_482C: (130, "startup_hook_glue", CAT_FIRST_PARTY_APP,
                  "application_startup_hook", "high"),
    0x0030_4CDC: (18, "code_veneer", CAT_PROPRIETARY_CONTROLLER,
                  "em_vendor_rom_wrapper", "medium"),
    0x0030_EA08: (258, "code_fragment", CAT_FIRST_PARTY_APP,
                  "application_module_myapp", "high"),
    0x0030_EB8C: (270, "code_function", CAT_FIRST_PARTY_APP,
                  "application_hook", "high"),
    0x0030_ECF8: (538, "code_function", CAT_FIRST_PARTY_APP,
                  "application_hook", "high"),
    0x0031_1150: (4, "hook_stub", CAT_FIRST_PARTY_APP,
                  "qpc_vendor_hook", "high"),
    0x0031_11A4: (4, "hook_stub", CAT_FIRST_PARTY_APP,
                  "qpc_vendor_hook", "high"),
    0x0031_1620: (20, "code_function", CAT_FIRST_PARTY_APP,
                  "application_hook", "high"),
    0x0031_369C: (14, "code_veneer", CAT_UNCLASSIFIED,
                  "unknown", "low"),
    0x0031_3F98: (16, "code_veneer", CAT_PROPRIETARY_CONTROLLER,
                  "em_vendor_rom_wrapper", "medium"),
    0x0032_9888: (3_126, "code_function", CAT_PROPRIETARY_CONTROLLER,
                  "packetcraft_modern_controller", "high"),
    0x0033_2FC4: (158, "runtime_support_code", CAT_TOOLCHAIN,
                  "metaware_memory_runtime", "high"),
}

LINE_RE = re.compile(r"^\s*([0-9a-f]+):\s+((?:[0-9a-f]{4}\s+)+)\s*(\S+)(.*)$")
TARGET_RE = re.compile(r";0x([0-9a-f]+)")
IMM_RE = re.compile(r"0x([0-9a-f]{6,8})")
BRANCH_PREFIXES = ("b", "j", "bl", "jl", "br", "lp")
BL_PREFIXES = ("bl",)
PROLOGUE_PREFIXES = ("enter_s", "push_s")
RUNTIME_ARITH_MNEMONICS = {"norm", "divu", "div", "mac", "macdu", "mpy", "mpyuw"}


class ResidualProvenanceError(RuntimeError):
    """Raised when an authenticated identity or classification invariant drifts."""


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _is_branch(mnemonic: str) -> bool:
    return mnemonic.split(".")[0].startswith(BRANCH_PREFIXES)


def _is_bl(mnemonic: str) -> bool:
    return mnemonic.split(".")[0].startswith(BL_PREFIXES)


def _base(mnemonic: str) -> str:
    return mnemonic.split(".")[0]


def load_objdump(application_objdump: Path) -> dict[int, tuple[str, str, int]]:
    """Parse the authenticated objdump into address -> (mnemonic, rest, bytes)."""
    application_objdump = application_objdump.resolve()
    digest = hashlib.sha256(application_objdump.read_bytes()).hexdigest()
    if digest != discovery.EXPECTED_APPLICATION_OBJDUMP_SHA256:
        raise ResidualProvenanceError("authenticated EM9305 application objdump changed")
    instructions: dict[int, tuple[str, str, int]] = {}
    for line in application_objdump.read_text().splitlines():
        match = LINE_RE.match(line)
        if match:
            instructions[int(match.group(1), 16)] = (
                match.group(3),
                match.group(4).strip(),
                2 * len(match.group(2).split()),
            )
    if not instructions:
        raise ResidualProvenanceError("authenticated EM9305 objdump decoded no instructions")
    return instructions


def _archive_family(labels: Sequence[str]) -> str | None:
    stems = {label.split(":", 1)[-1] for label in labels}
    if stems & PACKETCRAFT_ARCHIVES:
        return "packetcraft_modern_controller"
    if stems & EM_VENDOR_ARCHIVES:
        return "em_vendor_system"
    if stems & FIRST_PARTY_ARCHIVES:
        return "first_party_application"
    if stems & QPC_ARCHIVES:
        return "qpc_public"
    return None


def _object_family(objects: Sequence[str]) -> str | None:
    for obj in objects:
        stem = obj.split(".", 1)[0].lower()
        if stem.startswith(PACKETCRAFT_OBJECT_PREFIXES):
            return "packetcraft_modern_controller"
    for obj in objects:
        stem = obj.split(".", 1)[0].lower()
        if stem.startswith(("em", "nvm", "pml", "sleep", "prot", "rc", "aoad", "ti_")):
            return "em_vendor_system"
    return None


def classify_segment(record: dict[str, Any]) -> tuple[str, str, str, str, list[str]]:
    """Assign (structural_class, category, family_hint, confidence, evidence).

    The rule order is deliberate: authenticated table/name evidence first,
    then MetaWare runtime vocabulary, then small-island shapes, then
    call-frontier family inference, then an explicit unclassified fallback.
    """
    start = record["start"]
    evidence: list[str] = []

    if start in NAMED_HOOK_STUBS:
        name, target = NAMED_HOOK_STUBS[start]
        if record["size"] != 4 or record["insns"] != [(f"b", f";0x{target:x}")]:
            raise ResidualProvenanceError(f"named hook stub decode changed at 0x{start:08X}")
        evidence.append(f"authenticated_hook_stub:{name}")
        evidence.append(f"branch_target:0x{target:08X}")
        return ("hook_stub", CAT_FIRST_PARTY_APP, "qpc_vendor_hook", "high", evidence)

    if start in NAMED_HOOK_TARGET_SEGMENTS:
        name = NAMED_HOOK_TARGET_SEGMENTS[start]
        evidence.append(f"authenticated_hook_stub_branch_target:{name}")
        if record["has_blink_return"]:
            evidence.append("blink_return")
        if record["id_tail_refs"]:
            evidence.append(f"identified_tail_refs:{record['id_tail_refs']}")
        return ("startup_hook_glue", CAT_FIRST_PARTY_APP,
                "application_startup_hook", "high", evidence)

    if record["assertion_sites"]:
        site_offset, module, assert_id = record["assertion_sites"][0]
        evidence.append(f"authenticated_assertion_site:{module}@{site_offset}#ID{assert_id}")
        if record["named_callees"]:
            evidence.append("named_callees:" + "|".join(record["named_callees"]))
        if record["rom_calls"]:
            evidence.append(f"rom_calls:{record['rom_calls']}")
        return ("code_fragment", CAT_FIRST_PARTY_APP,
                f"application_module_{module.lower()}", "high", evidence)

    if record["hook_table_entry"]:
        evidence.append("authenticated_hook_pointer_table_entry")
        if record["prologue"]:
            evidence.append("prologue")
        if record["named_callees"]:
            evidence.append("named_callees:" + "|".join(record["named_callees"]))
        return ("code_function", CAT_FIRST_PARTY_APP, "application_hook", "high", evidence)

    if start == 0x0030_2508:
        evidence.append("post_vector_default_handler_stubs")
        evidence.append("self_loop_bl_s_pairs")
        return ("code_veneer", CAT_PROPRIETARY_CONTROLLER,
                "em_vendor_rom_stub", "medium", evidence)

    if start == ARITH_RUNTIME_SEGMENT_START:
        if not record["runtime_arith"] or not record["stack_limit_refs"] or not record["has_brk"]:
            raise ResidualProvenanceError("MetaWare arithmetic-runtime vocabulary changed")
        evidence.append("metaware_arith_vocabulary:" + "|".join(record["runtime_arith"]))
        evidence.append("stack_limit_refs")
        evidence.append("brk_s_stack_guard")
        evidence.append(f"entry_branches:{record['entry_branches']}")
        return ("runtime_support_code", CAT_TOOLCHAIN,
                "metaware_arith_runtime", "high", evidence)

    if start == MEMCPY_MEMSET_SEGMENT_START:
        if record["bl_count"] != 0 or record["rom_calls"] != 0:
            raise ResidualProvenanceError("MetaWare memory-runtime call topology changed")
        evidence.append("mem_move_set_loops_no_external_calls")
        evidence.append(f"incoming_identified_calls:{record['incoming_calls']}")
        return ("runtime_support_code", CAT_TOOLCHAIN,
                "metaware_memory_runtime", "high", evidence)

    # ROM-call wrappers: tiny, no BL, at least one branch target in the
    # authenticated EM ROM window.  Register shuffling around the tail branch
    # is expected, so branch-only is not required.
    if (
        record["size"] <= 24
        and record["bl_count"] == 0
        and record["rom_branch_targets"] > 0
        and record["ninsn"] <= 10
    ):
        evidence.append(f"rom_branch_targets:{record['rom_branch_targets']}")
        if record["branch_only"]:
            evidence.append("branch_only_island")
        return ("code_veneer", CAT_PROPRIETARY_CONTROLLER,
                "em_vendor_rom_wrapper", "medium", evidence)

    # Zero/copy-init stubs that tail-branch into the authenticated MetaWare
    # memory runtime; ownership of the caller is not evidenced.
    if (
        record["size"] <= 16
        and record["bl_count"] == 0
        and record["mem_runtime_tail_ref"]
    ):
        evidence.append("metaware_memory_runtime_tail_stub")
        return ("code_veneer", CAT_UNCLASSIFIED, "unknown", "low", evidence)

    # Tiny leaf accessors over RAM globals; ownership is not evidenced.
    if (
        record["size"] <= 16
        and record["bl_count"] == 0
        and record["ram_imm_refs"] > 0
        and record["has_blink_return"]
        and record["ninsn"] <= 5
    ):
        evidence.append(f"ram_global_access:{record['ram_imm_refs']}")
        evidence.append("blink_return_leaf")
        return ("code_leaf_accessor", CAT_UNCLASSIFIED,
                "unknown", "low", evidence)

    # Small branch-only islands (switch-case stubs or trampolines of unknown
    # family) and tiny immediate-referenced items.
    if record["size"] <= 16 and record["ninsn"] <= 3:
        if record["branch_only"] and record["ninsn"] >= 1:
            evidence.append("branch_only_island")
            if record["imm_in"] > 0:
                evidence.append(f"referenced_by_immediate:{record['imm_in']}")
            return ("code_veneer", CAT_UNCLASSIFIED, "unknown", "low", evidence)
        if not record["branch_only"]:
            evidence.append(f"imm_references:{record['imm_in']}")
            return ("constant_or_struct_candidate", CAT_UNCLASSIFIED,
                    "unknown", "low", evidence)

    # General code: family inference from the identified call frontier.
    frontier = Counter(record["callee_families"] + record["tail_families"])
    family: str | None = None
    if frontier:
        family, _ = frontier.most_common(1)[0]
    if family is None and record["rom_calls"] > 0:
        family = "em_vendor_system"
    if family is None and record["neighbor_families"]:
        neighbor = Counter(f for f in record["neighbor_families"] if f)
        if neighbor:
            candidate, count = neighbor.most_common(1)[0]
            if count == len(record["neighbor_families"]):
                family = candidate
                evidence.append("family_from_identified_neighbors_only")

    weak_code = (
        (record["has_blink_return"] and record["ninsn"] >= 2)
        or record["has_internal_branch"]
        or bool(record["runtime_arith"])
    )
    code_evidence = (
        record["prologue"]
        or record["entry_branches"] > 0
        or record["incoming_calls"] > 0
        or record["bl_count"] > 0
        or record["res_calls"] > 0
        or record["id_tail_refs"] > 0
        or weak_code
    )
    structural = "code_function" if record["prologue"] else "code_fragment"
    if record["prologue"]:
        evidence.append("prologue")
    if record["entry_branches"]:
        evidence.append(f"entry_branches:{record['entry_branches']}")
    if record["incoming_calls"]:
        evidence.append(f"incoming_identified_calls:{record['incoming_calls']}")
    if record["named_callees"]:
        evidence.append("named_callees:" + "|".join(record["named_callees"]))
    if record["named_tail_targets"]:
        evidence.append("named_tail_targets:" + "|".join(record["named_tail_targets"]))
    if record["rom_calls"]:
        evidence.append(f"rom_calls:{record['rom_calls']}")
    if record["res_calls"]:
        evidence.append(f"residual_calls:{record['res_calls']}")
    if weak_code and not (
        record["prologue"] or record["entry_branches"] or record["incoming_calls"]
        or record["bl_count"] or record["res_calls"] or record["id_tail_refs"]
    ):
        evidence.append("weak_code_features_only")

    if family == "packetcraft_modern_controller" and code_evidence:
        confidence = "high" if (record["prologue"] or record["entry_branches"]) and sum(
            1 for f in record["callee_families"] if f == family) >= 3 else "medium"
        return (structural, CAT_PROPRIETARY_CONTROLLER, family, confidence, evidence)
    if family == "em_vendor_system" and code_evidence:
        confidence = "high" if (record["prologue"] or record["entry_branches"]) and (
            record["rom_calls"] > 0
            or sum(1 for f in record["callee_families"] if f == family) >= 2
        ) else "medium"
        return (structural, CAT_PROPRIETARY_CONTROLLER, family, confidence, evidence)
    if family in {"first_party_application", "qpc_public"} and code_evidence:
        # Frontier-only application/QP adjacency is weaker than table evidence.
        return (structural, CAT_UNCLASSIFIED, family, "low", evidence)
    if code_evidence:
        return (structural, CAT_UNCLASSIFIED, "unknown", "low", evidence)

    evidence.append("no_positive_code_or_data_evidence")
    return ("opaque_code_or_data", CAT_UNCLASSIFIED, "unknown", "low", evidence)


def analyze(
    batch_output: Path,
    enforced_output: Path,
    round2_output: Path,
    round1_min8_output: Path,
    round2_min8_output: Path,
    application_objdump: Path,
    *,
    image: Path = DEFAULT_IMAGE,
) -> dict[str, Any]:
    census = residual.analyze(
        batch_output,
        enforced_output,
        round2_output,
        round1_min8_output,
        round2_min8_output,
        application_objdump,
        image=image,
    )
    exact = discovery.analyze_low_floor(
        batch_output,
        enforced_output,
        round2_output,
        round1_min8_output,
        round2_min8_output,
        application_objdump,
        image=image,
        include_functions=True,
    )
    placed = link_order.analyze(
        batch_output,
        enforced_output,
        round2_output,
        round1_min8_output,
        round2_min8_output,
        application_objdump,
        image=image,
    )
    segments = [
        item
        for item in census["segments"]
        if item["status"] == "stock_retained_unresolved_code_or_mixed"
    ]
    if (
        len(segments) != EXPECTED_RESIDUAL_SEGMENTS
        or sum(item["size"] for item in segments) != EXPECTED_RESIDUAL_BYTES
    ):
        raise ResidualProvenanceError("EM9305 residual unresolved census changed")

    # Authenticated assertion-topology guards: the portable/QP sites and the
    # ``WsfOs`` site are already identified; the ``MyApp`` site must remain
    # inside exactly one residual segment.
    for site in ASSERTION_SITE_IDENTIFIED_GUARD:
        if any(item["start"] <= site < item["end"] for item in segments):
            raise ResidualProvenanceError(
                f"identified assertion site 0x{site:08X} entered the residual tier"
            )
    for site in ASSERTION_SITE_MODULES:
        if sum(item["start"] <= site < item["end"] for item in segments) != 1:
            raise ResidualProvenanceError(
                f"residual assertion site 0x{site:08X} containment changed"
            )

    image_bytes = image.resolve().read_bytes()

    def app_bytes(start: int, end: int) -> bytes:
        return image_bytes[start - PACKAGE_MAP_BASE:end - PACKAGE_MAP_BASE]

    hook_table = app_bytes(HOOK_TABLE_START, HOOK_TABLE_END)
    hook_targets = tuple(
        struct.unpack_from("<I", hook_table, offset)[0]
        for offset in range(0, len(hook_table), 4)
    )
    if sha256(hook_table) != HOOK_TABLE_SHA256 or hook_targets != HOOK_TABLE_TARGETS:
        raise ResidualProvenanceError("authenticated EM9305 hook-pointer table changed")
    hook_residual_entries = {item["start"] for item in segments} & set(hook_targets)
    if hook_residual_entries != {
        0x0030_EB8C,
        0x0030_ECF8,
        0x0031_1150,
        0x0031_11A4,
        0x0031_1620,
    }:
        raise ResidualProvenanceError("hook-table residual membership changed")

    instructions = load_objdump(application_objdump)

    # Identified interval lookup (exact functions plus link-order placements).
    identified: list[tuple[int, int, str, dict[str, Any]]] = sorted(
        [(f["address"], f["end"], "exact", f) for f in exact["functions"]]
        + [(p["address"], p["end"], "placed", p) for p in placed["placements"]]
    )
    id_starts = [item[0] for item in identified]

    import bisect

    def lookup_identified(address: int) -> tuple[str, dict[str, Any]] | tuple[None, None]:
        index = bisect.bisect_right(id_starts, address) - 1
        if index >= 0:
            start, end, kind, payload = identified[index]
            if start <= address < end:
                return kind, payload
        return None, None

    def identified_family(kind: str, payload: dict[str, Any]) -> str | None:
        if kind == "exact":
            return _archive_family(payload["archives"])
        family = _object_family([payload.get("object", "")])
        return family

    unresolved_index = {
        (item["start"], item["end"]): item for item in segments
    }
    unresolved_bounds = sorted(unresolved_index)

    def lookup_unresolved(address: int) -> tuple[int, int] | None:
        index = bisect.bisect_right(unresolved_bounds, (address, APP_END + 1)) - 1
        if index >= 0:
            start, end = unresolved_bounds[index]
            if start <= address < end:
                return start, end
        return None

    # Incoming references from identified code into unresolved segments.
    incoming_branch: dict[int, list[tuple[int, int, str]]] = {
        item["start"]: [] for item in segments
    }
    incoming_imm: Counter[int] = Counter()
    for address, (mnemonic, rest, _nbytes) in instructions.items():
        kind, _payload = lookup_identified(address)
        if kind is None:
            continue
        target_match = TARGET_RE.search(rest)
        if target_match and _is_branch(mnemonic):
            target = int(target_match.group(1), 16)
            hit = lookup_unresolved(target)
            if hit is not None:
                incoming_branch[hit[0]].append((address, target, mnemonic))
        for imm in IMM_RE.findall(rest):
            value = int(imm, 16)
            hit = lookup_unresolved(value)
            if hit is not None and not (
                target_match and int(target_match.group(1), 16) == value
            ):
                incoming_imm[hit[0]] += 1

    records: list[dict[str, Any]] = []
    for item in segments:
        start, end = item["start"], item["end"]
        body = app_bytes(start, end)
        if sha256(body) != item["sha256"]:
            raise ResidualProvenanceError(f"residual segment hash changed at 0x{start:08X}")
        decoded = sorted(
            (a, v) for a, v in instructions.items() if start <= a < end
        )
        bl_sites = [(a, v) for a, v in decoded if _is_bl(v[0]) and TARGET_RE.search(v[1])]
        id_calls = 0
        res_calls = 0
        rom_calls = 0
        named: set[str] = set()
        families: list[str] = []
        for _a, (mnemonic, rest, _nb) in bl_sites:
            target = int(TARGET_RE.search(rest).group(1), 16)
            kind, payload = lookup_identified(target)
            if kind is not None:
                id_calls += 1
                if kind == "exact":
                    named.add(sorted(payload["names"])[0])
                else:
                    named.add(payload["name"])
                fam = identified_family(kind, payload)
                if fam:
                    families.append(fam)
            elif ROM_LO <= target < ROM_HI:
                rom_calls += 1
            else:
                res_calls += 1
        branch_mnemonics = [v[0] for _a, v in decoded]
        branch_targets = [
            int(TARGET_RE.search(v[1]).group(1), 16)
            for _a, v in decoded
            if _is_branch(v[0]) and TARGET_RE.search(v[1])
        ]
        # Non-BL branch (tail-jump/case) references into identified code.
        id_tail_refs = 0
        tail_families: list[str] = []
        named_tail: set[str] = set()
        for _a, v in decoded:
            if _is_bl(v[0]) or not _is_branch(v[0]) or not TARGET_RE.search(v[1]):
                continue
            target = int(TARGET_RE.search(v[1]).group(1), 16)
            if start <= target < end:
                continue
            kind, payload = lookup_identified(target)
            if kind is not None:
                id_tail_refs += 1
                if kind == "exact":
                    named_tail.add(sorted(payload["names"])[0])
                else:
                    named_tail.add(payload["name"])
                fam = identified_family(kind, payload)
                if fam:
                    tail_families.append(fam)
        assertion_sites = [
            (f"0x{site:08X}", module, assert_id)
            for site, (module, assert_id) in ASSERTION_SITE_MODULES.items()
            if start <= site < end
        ]
        immediates = {
            int(imm, 16)
            for _a, v in decoded
            for imm in IMM_RE.findall(v[1])
        }
        incoming = incoming_branch[start]
        entry_branches = sum(1 for _site, target, _m in incoming if target == start)
        incoming_calls = sum(
            1 for _site, _target, m in incoming if _is_bl(m)
        )
        # Neighbor family hints (recorded, used only as a last-resort hint).
        neighbors: list[str] = []
        index = bisect.bisect_right(id_starts, start) - 1
        for neighbor_index in (index, index + 1):
            if 0 <= neighbor_index < len(identified):
                n_start, n_end, n_kind, n_payload = identified[neighbor_index]
                if n_end == start or n_start == end:
                    fam = identified_family(n_kind, n_payload)
                    if fam:
                        neighbors.append(fam)
        first_mnemonic = decoded[0][1][0] if decoded else None
        record = {
            "start": start,
            "end": end,
            "size": item["size"],
            "sha256": item["sha256"],
            "ninsn": len(decoded),
            "insns": [(v[0], TARGET_RE.search(v[1]).group(0) if TARGET_RE.search(v[1]) else v[1])
                      for _a, v in decoded] if item["size"] <= 8 else [],
            "bl_count": len(bl_sites),
            "id_calls": id_calls,
            "res_calls": res_calls,
            "rom_calls": rom_calls,
            "named_callees": sorted(named)[:8],
            "callee_families": families,
            "neighbor_families": neighbors,
            "branch_only": bool(decoded) and all(_is_branch(m) for m in branch_mnemonics),
            "rom_branch_targets": sum(1 for t in branch_targets if ROM_LO <= t < ROM_HI),
            "mem_runtime_tail_ref": any(
                MEMCPY_MEMSET_SEGMENT_START <= t < MEMCPY_MEMSET_SEGMENT_END
                for t in branch_targets
            ),
            "has_internal_branch": any(start <= t < end for t in branch_targets),
            "id_tail_refs": id_tail_refs,
            "tail_families": tail_families,
            "named_tail_targets": sorted(named_tail)[:8],
            "assertion_sites": assertion_sites,
            "ram_imm_refs": sum(1 for v in immediates if RAM_LO <= v < RAM_HI),
            "stack_limit_refs": int(
                {STACK_LIMIT_LOW, STACK_LIMIT_HIGH} <= immediates
            ),
            "has_brk": any(_base(m) == "brk_s" for m in branch_mnemonics),
            "has_blink_return": any("[blink]" in v[1] and _base(v[0]) in {"j_s", "j"}
                                    for _a, v in decoded),
            "runtime_arith": sorted(
                {_base(m) for m in branch_mnemonics} & RUNTIME_ARITH_MNEMONICS
            ),
            "prologue": first_mnemonic is not None
            and first_mnemonic.startswith(PROLOGUE_PREFIXES),
            "entry_branches": entry_branches,
            "incoming_calls": incoming_calls,
            "imm_in": incoming_imm[start],
            "hook_table_entry": start in hook_residual_entries,
        }
        structural, category, family_hint, confidence, evidence = classify_segment(record)
        record.update(
            structural_class=structural,
            ownership_category=category,
            family_hint=family_hint,
            confidence=confidence,
            evidence=evidence,
        )
        records.append(record)

    # Fail-closed census of the classification itself.
    category_counts = Counter(item["ownership_category"] for item in records)
    category_bytes = Counter()
    family_bytes = Counter()
    structural_counts = Counter(item["structural_class"] for item in records)
    confidence_counts = Counter(item["confidence"] for item in records)
    for item in records:
        category_bytes[item["ownership_category"]] += item["size"]
        if item["ownership_category"] == CAT_PROPRIETARY_CONTROLLER:
            family_bytes[item["family_hint"]] += item["size"]
    if (
        dict(category_counts) != EXPECTED_CATEGORY_COUNTS
        or dict(category_bytes) != EXPECTED_CATEGORY_BYTES
        or dict(family_bytes) != EXPECTED_FAMILY_BYTES
        or dict(structural_counts) != EXPECTED_STRUCTURAL_COUNTS
    ):
        raise ResidualProvenanceError(
            "EM9305 residual provenance classification changed: "
            f"categories={dict(category_counts)}, bytes={dict(category_bytes)}, "
            f"families={dict(family_bytes)}, structural={dict(structural_counts)}"
        )
    by_start = {item["start"]: item for item in records}
    for start, (size, structural, category, family_hint, confidence) in EXPECTED_KEY_SEGMENTS.items():
        item = by_start.get(start)
        if item is None or (
            item["size"],
            item["structural_class"],
            item["ownership_category"],
            item["family_hint"],
            item["confidence"],
        ) != (size, structural, category, family_hint, confidence):
            raise ResidualProvenanceError(
                f"EM9305 key residual segment classification changed at 0x{start:08X}"
            )

    return {
        "application_base": APP_BASE,
        "application_end": APP_END,
        "residual_unresolved_segments": len(records),
        "residual_unresolved_bytes": sum(item["size"] for item in records),
        "ownership_categories": list(OWNERSHIP_CATEGORIES),
        "category_segment_counts": dict(category_counts),
        "category_bytes": dict(category_bytes),
        "proprietary_family_bytes": dict(family_bytes),
        "structural_class_counts": dict(structural_counts),
        "confidence_counts": dict(confidence_counts),
        "retention_recommendation": (
            "all classified spans remain hash-pinned stock retentions behind the "
            "declared EM9305 controller boundary; no category asserts source "
            "availability or redistribution rights"
        ),
        "segments": [
            {
                key: item[key]
                for key in (
                    "start",
                    "end",
                    "size",
                    "sha256",
                    "structural_class",
                    "ownership_category",
                    "family_hint",
                    "confidence",
                    "evidence",
                )
            }
            for item in records
        ],
    }


def format_tsv(report: dict[str, Any]) -> str:
    """Render the classification map deterministically."""
    lines = [
        "start\tend\tsize\tsha256\tstructural_class\townership_category\t"
        "family_hint\tconfidence\tevidence"
    ]
    for item in report["segments"]:
        lines.append(
            "\t".join(
                (
                    f"0x{item['start']:08X}",
                    f"0x{item['end']:08X}",
                    str(item["size"]),
                    item["sha256"],
                    item["structural_class"],
                    item["ownership_category"],
                    item["family_hint"],
                    item["confidence"],
                    ";".join(item["evidence"]),
                )
            )
        )
    return "\n".join(lines) + "\n"


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--batch-output",
        type=Path,
        default=DEFAULT_CORPUS / "sdk-comparison/batch16-min16",
    )
    parser.add_argument(
        "--enforced-output",
        type=Path,
        default=DEFAULT_CORPUS / "sdk-comparison/fast-enforced",
    )
    parser.add_argument(
        "--round2-output",
        type=Path,
        default=DEFAULT_CORPUS / "sdk-comparison/round2",
    )
    parser.add_argument(
        "--round1-min8-output",
        type=Path,
        default=DEFAULT_CORPUS / "sdk-comparison/batch16",
    )
    parser.add_argument(
        "--round2-min8-output",
        type=Path,
        default=DEFAULT_CORPUS / "sdk-comparison/round2-min8",
    )
    parser.add_argument(
        "--application-objdump",
        type=Path,
        default=DEFAULT_CORPUS / "size-delta/opencfw-em9305-application-objdump.txt",
    )
    parser.add_argument("--image", type=Path, default=DEFAULT_IMAGE)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--tsv", type=Path, help="write the classification map TSV")
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
    if args.tsv:
        args.tsv.write_text(format_tsv(report))
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print("EM9305 residual provenance classification: PASS")
        print(json.dumps(
            {key: value for key, value in report.items() if key != "segments"},
            indent=2,
            sort_keys=True,
        ))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
