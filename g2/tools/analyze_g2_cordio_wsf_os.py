#!/usr/bin/env python3
"""Fail-closed G2 Cordio/Ambiq FreeRTOS WSF OS and queue audit."""

from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import json
import struct
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from apollo_artifact_consistency import validate_apollo_main_artifacts
IMAGE = ROOT / "blobs" / "official" / "g2-2.2.6.10" / "ota_s200_firmware_ota.bin"
RECOVERY_ANALYZER = ROOT / "tools" / "recover_apollo_embedded_source_paths.py"
LOAD_BASE = 0x00437FE0
IMAGE_BYTES = 3_523_396
IMAGE_SHA256 = "36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863"
CORPUS_MANIFEST_SHA256 = "3ff8aa908e5841823df9384cfbffca91d657816274797f332a45ff93a8aa832f"

OS_START, OS_END = 0x0052B8A4, 0x0052BAB8
OS_SHA256 = "7ed04ab36ab918395ca59c417aaff620aa2777d8721720efc123a0cc729fb408"
LITERALS_START, LITERALS_END = 0x0052BAB8, 0x0052BACC
LITERALS_SHA256 = "3806c76818681d6c5562202b5458198dbcd6d50f5653793814cadafaca6d73ff"
QUEUE_START, QUEUE_END = 0x00538C24, 0x00538D16
QUEUE_SHA256 = "a1288313d8580bb67c5d5dc23170f4484dbac464db2cb754293545547f26c0a9"

OS_MAP = ROOT / "tools/manifests/ambiqsuite-cordio-wsf-os-function-map.tsv"
OS_PROVENANCE = ROOT / "tools/manifests/ambiqsuite-cordio-wsf-os-provenance.tsv"
OS_VARIANTS = ROOT / "tools/manifests/ambiqsuite-cordio-wsf-os-variant-provenance.tsv"
QUEUE_MAP = ROOT / "tools/manifests/ambiqsuite-cordio-wsf-queue-function-map.tsv"
QUEUE_PROVENANCE = ROOT / "tools/manifests/ambiqsuite-cordio-wsf-queue-provenance.tsv"
QUEUE_SOURCE_ONLY = ROOT / "tools/manifests/ambiqsuite-cordio-wsf-queue-source-only.tsv"
MATRIX_CONFIG = ROOT / "tools/manifests/readiness-cordio-wsf-os-queue-stockabi-config-summary.tsv"
MATRIX_BEST = ROOT / "tools/manifests/readiness-cordio-wsf-os-queue-stockabi-best-size.tsv"
MATRIX_SOURCE = ROOT / "tools/manifests/readiness-cordio-wsf-os-queue-stockabi-source-identities.tsv"
MATRIX_PROVIDERS = ROOT / "tools/manifests/readiness-cordio-wsf-os-queue-stockabi-provider-closure.tsv"
MATRIX_MANIFEST = ROOT / "research/readiness/wsf-os-queue-stockabi/SHA256SUMS"
CANDIDATE_OS_C = ROOT / "components/shared/cordio/runtime_cordio_wsf_os_candidate.c"
CANDIDATE_OS_H = ROOT / "components/shared/cordio/runtime_cordio_wsf_os_candidate.h"
CANDIDATE_QUEUE_C = ROOT / "components/shared/cordio/runtime_cordio_wsf_queue_candidate.c"
CANDIDATE_QUEUE_H = ROOT / "components/shared/cordio/runtime_cordio_wsf_queue_candidate.h"
OVERLAY_CONFIG = ROOT / "components/apollo_main/core_overlay/overlay.json"
BUILD_REPORT = ROOT / "components/apollo_main/core_overlay/build/build-report.json"
SOURCE_MANIFEST = ROOT / "manifests/g2-2.2.6.10-core-source.json"
PACKAGE = ROOT / "build/source/package/g2-openCFW-s200_v2.2.6.10-core-source.evenota.bin"
FLASH_PLAN = ROOT / "build/source/flash-plan.json"

FILE_HASHES = {
    OS_MAP: "76b22daa34cd9ddec9959f47b686c3a602771f2ab8bf2ab468dd63bd4b78c9d1",
    OS_PROVENANCE: "19f58adec018354cbb1173f7c272d254567bd13ed7ddaa9b8e2368474ce17659",
    OS_VARIANTS: "d0ad37fa8440cf1fcc49d15a85e6a3b5f27b95bdfbaaa4137d69f6eef8f602fc",
    QUEUE_MAP: "8ce663e02b241c1ccd7178d2b4d7c4e3652f64453106a7cb216dfa1e1265a186",
    QUEUE_PROVENANCE: "019c117683d466b7a5a269f11a28d30dc614e128912acc8501c6c75497e917d4",
    QUEUE_SOURCE_ONLY: "b73a9087d54c1d1d9129900db1c2082dd4bbfb34b0c24fc4aa3d0f4659dd757e",
    MATRIX_CONFIG: "50caae8ae9f3b3ae6c8ec2ebe09eb453968c4b03c752926f574b75452c4cf206",
    MATRIX_BEST: "d6eddd6b685e16a9177dd5fea63d66895119df5cea581c398b79d7118c391811",
    MATRIX_SOURCE: "d166324a7b6b291e1bae593caf5bb0b03bdf0e68833342c8f57ae646a92ac6e2",
    MATRIX_PROVIDERS: "e99bc73d7bf500a51a32fd0639d3ff42977aabb4f667697b6ca35caaadc539c0",
    MATRIX_MANIFEST: "0636c55d2ec637d32f6833df404c259299efae41b8dcf1ac25226de21da67861",
    CANDIDATE_OS_C: "b5e06661616d083661894394f89c2e7dd8039afde238e9400148208f4b44c60a",
    CANDIDATE_OS_H: "6301598c71dc1e8cea215173d1810669d85abb0732ab3b44ba63816a823dbef5",
    CANDIDATE_QUEUE_C: "da33f0b38236af81b4aa33b91c5c785e52b5b81867820c4877b9b87c417eec4e",
    CANDIDATE_QUEUE_H: "e64b75cb6d2d7d26ad9db3f1bebe4ef4d3b1b0c33e684160ac115b37d57d42ed",
}

OS_PRODUCTION_FUNCTIONS = [
    "open_cfw_cordio_wsf_cs_enter_candidate",
    "open_cfw_cordio_wsf_cs_exit_candidate",
    "open_cfw_cordio_wsf_task_lock_candidate",
    "open_cfw_cordio_wsf_task_unlock_candidate",
    "open_cfw_cordio_wsf_set_os_specific_event_candidate",
    "open_cfw_cordio_wsf_set_event_candidate",
    "open_cfw_cordio_wsf_task_set_ready_candidate",
    "open_cfw_cordio_wsf_task_message_queue_candidate",
    "open_cfw_cordio_wsf_os_set_next_handler_candidate",
    "open_cfw_cordio_wsf_os_ready_to_sleep_candidate",
    "open_cfw_cordio_wsf_os_init_candidate",
    "open_cfw_cordio_wsf_os_dispatcher_candidate",
]
QUEUE_PRODUCTION_FUNCTIONS = [
    "open_cfw_cordio_wsf_queue_enqueue_candidate",
    "open_cfw_cordio_wsf_queue_dequeue_candidate",
    "open_cfw_cordio_wsf_queue_push_candidate",
    "open_cfw_cordio_wsf_queue_insert_candidate",
    "open_cfw_cordio_wsf_queue_remove_candidate",
    "open_cfw_cordio_wsf_queue_count_candidate",
]

OS_CALLERS = {
    0x0052B8A4: [0x0052B8CA,0x0052B924,0x0052B962,0x0052B9E0,0x0052BA64,0x0053046E,0x005304FC,0x00538C2E,0x00538C4E,0x00538C74,0x00538C94,0x00538CD0,0x00538CFC],
    0x0052B8B6: [0x0052B8D2,0x0052B954,0x0052B972,0x0052B9EE,0x0052BA7E,0x00530454,0x00530482,0x0053050A,0x00538C44,0x00538C66,0x00538C86,0x00538CC2,0x00538CF0,0x00538D0C],
    0x0052B8C8: [0x004B329A,0x004B32BC,0x004B564C,0x004B6332,0x004B63A8,0x004B63B6,0x004B6C2A,0x004B6C6A,0x004B6D6E,0x004B6D9E,0x004B71E4,0x004B73A6,0x004BAC2E,0x004C581A,0x004C584C,0x004D27E2,0x0052A42C,0x0052A4D6,0x0052A4EA,0x0052A51E,0x0052A546,0x00533C7C,0x005353B4,0x005353F4,0x005369EC,0x00536A9A,0x00536B1A,0x0055BB42],
    0x0052B8D0: [0x004B32B2,0x004B32C4,0x004B567C,0x004B634A,0x004B63AE,0x004B63C0,0x004B6C58,0x004B6C7C,0x004B6D90,0x004B6DC4,0x004B723E,0x004B73BA,0x004BAC48,0x004C5828,0x004C5862,0x004D27F0,0x0052A462,0x0052A4E0,0x0052A514,0x0052A53A,0x0052A564,0x0052A56C,0x00533CBA,0x005353E2,0x00535434,0x005369FA,0x00536AAA,0x00536B2A,0x0055BB62],
    0x0052B8D8: [0x0052B958,0x0052B976],
    0x0052B91E: [0x004B4A72,0x004B4AAC,0x004B4B12,0x004B4BEC,0x004B4C06,0x004B4C62,0x00530CAC],
    0x0052B95E: [0x004BF9D8,0x0052A46E,0x0052A4FC],
    0x0052B97C: [0x004BF9C4],
    0x0052B980: [0x004B7FF4,0x004B8002,0x004B803E,0x004B8058,0x004B8072,0x004B8096,0x004B80A4,0x004B80B2],
    0x0052B99E: [0x0052BA9A],
    0x0052B9B2: [0x004B7F66],
    0x0052B9D0: [0x004D0A62],
}

QUEUE_CALLERS = {
    0x00538C24: [0x004BF9E6,0x00538CA8,0x005A60F2],
    0x00538C4A: [0x004BF9F0,0x00534CF8,0x005A61EE],
    0x00538C6E: [0x00538CB6],
    0x00538C8C: [0x0052A45E,0x005353D8],
    0x00538CC8: [0x0052A41A,0x0052A55C],
    0x00538CF6: [0x0052AD44,0x005A605E],
}

CALLEES = {
    0x0052B8A4: [], 0x0052B8B6: [],
    0x0052B8C8: [(0x0052B8CA,0x0052B8A4)],
    0x0052B8D0: [(0x0052B8D2,0x0052B8B6)],
    0x0052B8D8: [(0x0052B8E2,0x00442228),(0x0052B8F4,0x0047EE4A),(0x0052B910,0x0047ED76),(0x0052B918,0x004420BC)],
    0x0052B91E: [(0x0052B924,0x0052B8A4),(0x0052B954,0x0052B8B6),(0x0052B958,0x0052B8D8)],
    0x0052B95E: [(0x0052B962,0x0052B8A4),(0x0052B972,0x0052B8B6),(0x0052B976,0x0052B8D8)],
    0x0052B97C: [], 0x0052B980: [], 0x0052B99E: [],
    0x0052B9B2: [(0x0052B9BC,0x0043C0E4),(0x0052B9C8,0x0047EBD8)],
    0x0052B9D0: [(0x0052B9D4,0x0052A574),(0x0052B9E0,0x0052B8A4),(0x0052B9EE,0x0052B8B6),(0x0052BA08,0x004BF9B0),(0x0052BA12,0x004BF9EC),(0x0052BA32,0x0052A542),(0x0052BA64,0x0052B8A4),(0x0052BA7E,0x0052B8B6),(0x0052BA96,0x0052A574),(0x0052BA9A,0x0052B99E),(0x0052BAB2,0x0047EBF8)],
    0x00538C24: [(0x00538C2E,0x0052B8A4),(0x00538C44,0x0052B8B6)],
    0x00538C4A: [(0x00538C4E,0x0052B8A4),(0x00538C66,0x0052B8B6)],
    0x00538C6E: [(0x00538C74,0x0052B8A4),(0x00538C86,0x0052B8B6)],
    0x00538C8C: [(0x00538C94,0x0052B8A4),(0x00538CA8,0x00538C24),(0x00538CB6,0x00538C6E),(0x00538CC2,0x0052B8B6)],
    0x00538CC8: [(0x00538CD0,0x0052B8A4),(0x00538CF0,0x0052B8B6)],
    0x00538CF6: [(0x00538CFC,0x0052B8A4),(0x00538D0C,0x0052B8B6)],
}


class AuditError(RuntimeError):
    """Raised when any closed WSF OS/queue evidence changes."""


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _rows(path: Path) -> list[dict[str, str]]:
    lines = [line for line in path.read_text().splitlines() if not line.startswith("#")]
    return list(csv.DictReader(lines, delimiter="\t"))


def _load_recovery():
    tools = str(ROOT / "tools")
    if tools not in sys.path:
        sys.path.insert(0, tools)
    spec = importlib.util.spec_from_file_location("wsf_os_recovery", RECOVERY_ANALYZER)
    if spec is None or spec.loader is None:
        raise AuditError("cannot load Thumb call decoder")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _verify_corpus(root: Path) -> int:
    manifest = root / "SHA256SUMS"
    accepted = {
        CORPUS_MANIFEST_SHA256,
        "87d0befa001f042918bd6af83b0f50e13dd95aab160b0e520f2cb0bc55c6404e",
    }
    if not manifest.is_file() or _sha256(manifest.read_bytes()) not in accepted:
        raise AuditError("authenticated Apollo Ghidra corpus manifest changed")
    checked = 0
    for line in manifest.read_text().splitlines():
        expected, relative = line.split(None, 1)
        target = root / relative.lstrip("* ")
        if not target.is_file() or _sha256(target.read_bytes()) != expected:
            raise AuditError(f"Apollo Ghidra corpus member changed: {relative}")
        checked += 1
    if checked != 133:
        raise AuditError("Apollo Ghidra corpus checksum census changed")
    return checked


def _direct_callers(blob: bytes, decoder: Any, targets: set[int]) -> dict[int, list[int]]:
    found = {target: [] for target in targets}
    for address in range(LOAD_BASE, LOAD_BASE + len(blob) - 3, 2):
        target = decoder._thumb_bl_target(blob, address)
        if target in found:
            found[target].append(address)
    return found


def _verify_no_stored_pointers(blob: bytes, intervals: list[tuple[int, int]]) -> None:
    targets = {
        address | thumb
        for start, end in intervals
        for address in range(start, end, 2)
        for thumb in (0, 1)
    }
    excluded = set()
    for start, end in intervals:
        excluded.update(range(start - LOAD_BASE, end - LOAD_BASE, 4))
    hits = []
    for offset in range(0, len(blob) - 3, 4):
        if offset in excluded:
            continue
        value = struct.unpack_from("<I", blob, offset)[0]
        if value in targets:
            hits.append((LOAD_BASE + offset, value))
    if hits:
        raise AuditError(f"unexpected stored OS/queue pointer ingress: {hits[:4]}")


def analyze(corpus_root: Path, image: Path = IMAGE) -> dict[str, Any]:
    decoder = _load_recovery()
    if image.stat().st_size != IMAGE_BYTES:
        raise AuditError("official G2 image size changed")
    blob = image.read_bytes()
    if _sha256(blob) != IMAGE_SHA256:
        raise AuditError("official G2 image SHA-256 changed")
    corpus_files = _verify_corpus(corpus_root)

    for path, expected in FILE_HASHES.items():
        if not path.is_file() or _sha256(path.read_bytes()) != expected:
            raise AuditError(f"authenticated WSF OS/queue input changed: {path.name}")

    os_body = blob[OS_START - LOAD_BASE:OS_END - LOAD_BASE]
    queue_body = blob[QUEUE_START - LOAD_BASE:QUEUE_END - LOAD_BASE]
    literals = blob[LITERALS_START - LOAD_BASE:LITERALS_END - LOAD_BASE]
    if len(os_body) != 532 or _sha256(os_body) != OS_SHA256:
        raise AuditError("complete WSF OS module changed")
    if len(queue_body) != 242 or _sha256(queue_body) != QUEUE_SHA256:
        raise AuditError("bounded WSF queue module changed")
    if len(literals) != 20 or _sha256(literals) != LITERALS_SHA256:
        raise AuditError("WSF OS literal table changed")

    os_rows, queue_rows = _rows(OS_MAP), _rows(QUEUE_MAP)
    if (len(os_rows), len(queue_rows)) != (12, 6):
        raise AuditError("WSF OS/queue function-map census changed")
    all_rows = [("wsf_os", row) for row in os_rows] + [("wsf_queue", row) for row in queue_rows]
    entries = {int(row["stock_start"], 0) for _unit, row in all_rows}
    callers = _direct_callers(blob, decoder, entries)
    functions = []
    for unit, row in all_rows:
        start, end = int(row["stock_start"], 0), int(row["stock_end_exclusive"], 0)
        body = blob[start - LOAD_BASE:end - LOAD_BASE]
        if len(body) != int(row["stock_bytes"]) or _sha256(body) != row["stock_sha256"]:
            raise AuditError(f"stock body changed for {row['stock_name']}")
        expected_callers = (OS_CALLERS if unit == "wsf_os" else QUEUE_CALLERS)[start]
        if callers[start] != expected_callers:
            raise AuditError(f"caller closure changed for {row['stock_name']}")
        for site, target in CALLEES[start]:
            if not start <= site < end or decoder._thumb_bl_target(blob, site) != target:
                raise AuditError(f"callee closure changed for {row['stock_name']}")
        functions.append({
            "unit": unit, "name": row["stock_name"], "entry": start,
            "end_exclusive": end, "size": len(body), "sha256": row["stock_sha256"],
            "ghidra_state": row["ghidra_state"], "classification": row["classification"],
            "direct_bl_callers": callers[start],
            "direct_bl_callees": [{"callsite": site, "target": target} for site, target in CALLEES[start]],
        })
    _verify_no_stored_pointers(blob, [(OS_START, OS_END), (QUEUE_START, QUEUE_END)])

    literal_words = struct.unpack("<5I", literals)
    expected_words = (0x20075045, 0x20074EF0, 0xE000ED04, 0x20073230, 0x20073264)
    if literal_words != expected_words:
        raise AuditError("WSF OS globals changed")

    os_provenance, variants = _rows(OS_PROVENANCE), _rows(OS_VARIANTS)
    queue_provenance, source_only = _rows(QUEUE_PROVENANCE), _rows(QUEUE_SOURCE_ONLY)
    if [row["release"] for row in os_provenance] != ["2.4.2", "2.5.1"]:
        raise AuditError("WSF OS release interval changed")
    if len(variants) != 2 or {row["git_blob"] for row in variants} != {"c37a11641314c53d30d8051937f4c808acc71cfb"}:
        raise AuditError("ten-handler Ambiq corroboration changed")
    if len(queue_provenance) != 2 or len(source_only) != 1 or source_only[0]["source_name"] != "WsfQueueEmpty":
        raise AuditError("WSF queue provenance/source-only census changed")

    config_rows, best_rows = _rows(MATRIX_CONFIG), _rows(MATRIX_BEST)
    source_rows, provider_rows = _rows(MATRIX_SOURCE), _rows(MATRIX_PROVIDERS)
    if len(config_rows) != 13 or len(best_rows) != 18 or len(source_rows) != 2 or len(provider_rows) != 25:
        raise AuditError("Lorelei stock-ABI matrix census changed")
    if any(row["raw_matches"] != "0" or row["strict_normalized_matches"] != "0" for row in config_rows):
        raise AuditError("Lorelei stock-ABI matrix verdict changed")
    best_config = min(config_rows, key=lambda row: int(row["aggregate_abs_size_delta"]))
    if best_config["config"] != "Os_nosibling" or best_config["aggregate_abs_size_delta"] != "74":
        raise AuditError("Lorelei stock-ABI best common configuration changed")
    exact_best = [row["function"] for row in best_rows if row["best_abs_delta"] == "0"]
    if exact_best != ["WsfTaskLock", "WsfTaskUnlock", "wsfOsReadyToSleep", "WsfQueueDeq", "WsfQueueRemove", "WsfQueueCount"]:
        raise AuditError("Lorelei per-function exact-size set changed")
    if provider_rows[-1] != {"scope": "linked_closure", "symbol": "(none)", "status": "zero_undefined_all_13_configs"}:
        raise AuditError("Lorelei provider closure changed")

    overlay = json.loads(OVERLAY_CONFIG.read_text())
    production = {}
    for unit, source, prefix, mapped, names, first_offset, expected_metrics in (
        (
            "wsf_os", CANDIDATE_OS_C, "replace_cordio_wsf_os_", os_rows,
            OS_PRODUCTION_FUNCTIONS, 265540, (614, 10, 25),
        ),
        (
            "wsf_queue", CANDIDATE_QUEUE_C, "replace_cordio_wsf_queue_",
            queue_rows, QUEUE_PRODUCTION_FUNCTIONS, 266164, (272, 4, 16),
        ),
    ):
        source_path = source.relative_to(ROOT).as_posix()
        leaves = [
            row for row in overlay["relocated_leaves"]
            if row.get("source", {}).get("path") == source_path
        ]
        if len(leaves) != len(names) or any(
            row.get("source", {}).get("sha256") != FILE_HASHES[source]
            for row in leaves
        ):
            raise AuditError(f"{unit} production source inventory changed")
        sites = {row["name"]: row for row in overlay["patch_sites"]}
        for index, (row, function) in enumerate(zip(mapped, names), 1):
            start = int(row["stock_start"], 0)
            end = int(row["stock_end_exclusive"], 0)
            site = sites.get(f"{prefix}{index:02d}")
            if (
                site is None
                or site.get("runtime_address") != start
                or site.get("target_function") != function
                or site.get("branch") != "b_w"
                or site.get("expected_size") != end - start
                or site.get("expected_sha256") != row["stock_sha256"]
                or function not in overlay["functions"]
            ):
                raise AuditError(f"{unit} production route {index} changed")
        compiled = sum(row["expected"]["size"] for row in leaves)
        alignment = leaves[0]["expected"]["offset"] - first_offset
        alignment += sum(
            leaves[index + 1]["expected"]["offset"]
            - leaves[index]["expected"]["offset"]
            - leaves[index]["expected"]["size"]
            for index in range(len(leaves) - 1)
        )
        relocations = sum(len(row["relocations"]) for row in leaves)
        if (compiled, alignment, relocations) != expected_metrics:
            raise AuditError(f"{unit} production metrics changed")
        production[unit] = {
            "functions": names,
            "compiled_text_bytes": compiled,
            "alignment_bytes": alignment,
            "strict_relocations": relocations,
            "guarded_redirects": len(names),
        }

    build = json.loads(BUILD_REPORT.read_text())
    validate_apollo_main_artifacts(ROOT, AuditError, "WSF OS/queue")
    manifest = json.loads(SOURCE_MANIFEST.read_text())
    override = manifest["component_overrides"]["apollo_main"]
    provider = override["provider"]
    regions = override["regions"]
    if (
        len([row for row in regions if row["name"].startswith("cordio_wsf_os_")]) != 29
        or len([row for row in regions if row["name"].startswith("cordio_wsf_queue_")]) != 14
    ):
        raise AuditError("WSF OS/queue manifest ownership changed")

    os_functions = [item for item in functions if item["unit"] == "wsf_os"]
    queue_functions = [item for item in functions if item["unit"] == "wsf_queue"]
    return {
        "schema_version": 1,
        "analysis_mode": "read-only stock and production-route audit; no hardware or flash operation",
        "authenticated_inputs": {
            "image_sha256": IMAGE_SHA256,
            "ghidra_corpus_manifest_sha256": CORPUS_MANIFEST_SHA256,
            "ghidra_corpus_files_verified": corpus_files,
        },
        "modules": {
            "wsf_os": {"start": OS_START, "end_exclusive": OS_END, "size": 532, "sha256": OS_SHA256, "functions": os_functions},
            "wsf_queue": {"start": QUEUE_START, "end_exclusive": QUEUE_END, "size": 242, "sha256": QUEUE_SHA256, "functions": queue_functions, "padding_after": [0x00538D16, 0x00538D18]},
            "stored_entry_or_interior_pointers": 0,
        },
        "abi": {
            "max_handlers": 10,
            "handler_event_mask_bits": 8,
            "task_size": 0x40,
            "task_offsets": {"handlers": 0x00, "handler_event_masks": 0x28, "message_queue": 0x34, "task_event_mask": 0x3C, "number_of_handlers": 0x3D},
            "queue_size": 8,
            "queue_offsets": {"head": 0, "tail": 4},
            "globals": {"critical_section_nesting": literal_words[0], "radio_event_group": literal_words[1], "scb_icsr": literal_words[2], "task": literal_words[3], "message_queue": literal_words[4]},
            "task_event_bits": {"message_queue": 1, "timer": 2, "handler": 4},
        },
        "lineage": {
            "classification": "AmbiqSuite 2.5.1 FreeRTOS implementation family; later official ten-handler source variant corroborates the stock-effective ABI",
            "selected_release": "2.5.1",
            "os_source_sha256": os_provenance[1]["source_sha256"],
            "os_git_blob": os_provenance[1]["source_git_blob"],
            "queue_source_sha256": queue_provenance[1]["source_sha256"],
            "queue_git_blob": queue_provenance[1]["source_git_blob"],
            "stock_discriminator": "dispatcher has the R2.5.1 second timer update and ready-to-sleep guard",
            "stock_effective_handler_count": 10,
            "exact_g2_handler_count_definition_site": "unavailable",
            "later_ten_handler_corroboration": variants,
            "license": "proprietary Wicentric/ARM source used as an oracle and not redistributed",
        },
        "candidate": {
            "production": "routed",
            "modules": [str(CANDIDATE_OS_C.relative_to(ROOT)), str(CANDIDATE_QUEUE_C.relative_to(ROOT))],
            "behaviorally_recreated_stock_functions": 18,
            "behaviorally_recreated_stock_bytes": 774,
            "source_only_queue_functions": ["WsfQueueEmpty"],
            "stock_queue_empty_body_bounded": False,
            "combined_arm_header_and_source_compile_gate": True,
            "direct_isr_pendsv_behavior_recreated_through_explicit_seam": True,
            "production_metrics": production,
        },
        "stock_abi_matrix": {
            "archive": str(MATRIX_MANIFEST.relative_to(ROOT)),
            "archive_sha256": FILE_HASHES[MATRIX_MANIFEST],
            "configs": 13,
            "functions": 18,
            "comparison_rows": 234,
            "elapsed_ns": 3_521_196_588,
            "raw_matches": 0,
            "strict_normalized_matches": 0,
            "linked_unresolved_symbols": 0,
            "best_common_config": best_config["config"],
            "best_common_abs_size_delta": int(best_config["aggregate_abs_size_delta"]),
            "per_function_exact_size": exact_best,
            "verdict": "GCC structural comparator only; no row proves exact IAR output",
        },
        "limitations": [
            "no retained stock __FILE__ path anchors wsf_os.c or wsf_queue.c; identity rests on source order, semantics, ABI, call topology, and release discriminators",
            "the exact G2 definition site producing WSF_MAX_HANDLERS=10 is unavailable; a later official Ambiq source differs from R2.5.1 only by changing the guarded default from 9 to 10",
            "WsfQueueEmpty has no independently bounded linked stock body and is excluded from recovered-byte coverage",
            "all eighteen bounded functions are guarded-routed from maintained C; WsfQueueEmpty remains source-only because no independent stock body exists",
            "live controller scheduling, ISR wake behavior, handler ordering, and sleep/wakeup remain blocked by unavailable physical evidence; future qualification requires authorized physical evidence",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ghidra-corpus", type=Path, required=True)
    parser.add_argument("--image", type=Path, default=IMAGE)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    report = analyze(args.ghidra_corpus, args.image)
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print("G2 Cordio/Ambiq WSF OS and queue recovery")
        print("  OS: 12 functions / 532 bytes")
        print("  queue: 6 bounded functions / 242 bytes")
        print("  lineage: AmbiqSuite 2.5.1 family; stock-effective 10 handlers")
        print("  production: eighteen clean-room functions guarded-routed and package-verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
