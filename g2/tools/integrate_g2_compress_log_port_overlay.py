#!/usr/bin/env python3
"""Install/review the complete G2 compact-log file-port source route."""

# SPDX-License-Identifier: MIT

from __future__ import annotations

import argparse
import copy
import csv
import hashlib
import importlib.util
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "components/apollo_main/core_overlay/overlay.json"
SOURCE = ROOT / "components/apollo_main/core_overlay/compress_log_port.c"
HEADER = SOURCE.with_suffix(".h")
FUNCTION_MAP = ROOT / "tools/manifests/g2-compress-log-port-function-map.tsv"
SOURCE_SHA256 = "473ddda6dd3b0f37d0cac08b9a1cbc6d3730fb79540598b9eb99c4c239b2226e"
SOURCE_SIZE = 17_905
HEADER_SHA256 = "76379ea92735573dfa4d3291259ed869bb2412794a8925f52cafdb26407a8a8a"
HEADER_SIZE = 1_095
BASE_FLAGS = [
    "-mthumb", "-mcpu=cortex-m55", "-O2", "-ffreestanding",
    "-fno-jump-tables", "-fomit-frame-pointer", "-fno-builtin",
    "-mno-unaligned-access", "-fno-unwind-tables",
    "-fno-asynchronous-unwind-tables", "-fropi", "-ffunction-sections",
    "-fdata-sections", "-Wall", "-Wextra", "-Werror", "-mllvm",
    "-enable-machine-outliner=never",
]

FUNCTIONS = (
    ("PATH", "open_cfw_compress_log_path_format"),
    ("EXISTS", "open_cfw_compress_log_file_exists"),
    ("RECONCILE", "open_cfw_compress_log_manager_reconcile"),
    ("LOAD", "open_cfw_compress_log_manager_load"),
    ("SAVE", "open_cfw_compress_log_manager_save"),
    ("REMOVE", "open_cfw_compress_log_file_remove"),
    ("HEADER", "open_cfw_compress_log_write_file_version_header"),
    ("ROTATE", "open_cfw_compress_log_rotate_file"),
    ("SYNC", "open_cfw_compress_log_sync_to_files"),
    ("TIMEOUT", "open_cfw_compress_log_export_timeout_callback"),
    ("NOTIFY", "open_cfw_compress_log_export_notify"),
    ("ACTIVE", "open_cfw_compress_log_export_active"),
)
SELECTOR = {function: selector for selector, function in FUNCTIONS}
LEAF_ORDER = (
    "open_cfw_compress_log_path_format",
    "open_cfw_compress_log_file_exists",
    "open_cfw_compress_log_manager_save",
    "open_cfw_compress_log_manager_reconcile",
    "open_cfw_compress_log_manager_load",
    "open_cfw_compress_log_file_remove",
    "open_cfw_compress_log_write_file_version_header",
    "open_cfw_compress_log_rotate_file",
    "open_cfw_compress_log_sync_to_files",
    "open_cfw_compress_log_export_timeout_callback",
    "open_cfw_compress_log_export_notify",
    "open_cfw_compress_log_export_active",
)
STOCK_NAMES = (
    "compress_log_path_format",
    "compress_log_file_exists",
    "compress_log_manager_reconcile",
    "compress_log_manager_load",
    "compress_log_manager_save",
    "compress_log_file_remove",
    "_write_file_version_header",
    "compress_log_rotate_file",
    "compress_log_sync_to_files",
    "compress_log_export_timeout_callback",
    "compress_log_export_notify",
    "compress_log_export_active",
)

CALLS: dict[str, tuple[tuple[str, str], ...]] = {
    "open_cfw_compress_log_path_format": (
        ("R_ARM_THM_JUMP24", "open_cfw_runtime_snprintf"),
    ),
    "open_cfw_compress_log_file_exists": (
        ("R_ARM_THM_CALL", "open_cfw_compress_log_path_format"),
        ("R_ARM_THM_CALL", "open_cfw_file_open"),
        ("R_ARM_THM_CALL", "open_cfw_file_close"),
    ),
    "open_cfw_compress_log_manager_reconcile": (
        ("R_ARM_THM_CALL", "open_cfw_compress_log_file_exists"),
        ("R_ARM_THM_CALL", "open_cfw_compress_log_file_exists"),
        ("R_ARM_THM_JUMP24", "open_cfw_compress_log_manager_save"),
    ),
    "open_cfw_compress_log_manager_load": (
        ("R_ARM_THM_CALL", "open_cfw_file_open"),
        ("R_ARM_THM_CALL", "open_cfw_file_read"),
        ("R_ARM_THM_CALL", "open_cfw_file_close"),
        ("R_ARM_THM_JUMP24", "open_cfw_compress_log_manager_reconcile"),
    ),
    "open_cfw_compress_log_manager_save": (
        ("R_ARM_THM_CALL", "open_cfw_file_open"),
        ("R_ARM_THM_CALL", "open_cfw_file_write"),
        ("R_ARM_THM_CALL", "open_cfw_file_close"),
    ),
    "open_cfw_compress_log_file_remove": (
        ("R_ARM_THM_CALL", "open_cfw_compress_log_path_format"),
        ("R_ARM_THM_CALL", "open_cfw_file_remove"),
    ),
    "open_cfw_compress_log_write_file_version_header": (
        ("R_ARM_THM_CALL", "open_cfw_runtime_snprintf"),
        ("R_ARM_THM_CALL", "open_cfw_file_seek"),
        ("R_ARM_THM_CALL", "open_cfw_file_write"),
    ),
    "open_cfw_compress_log_rotate_file": (
        ("R_ARM_THM_CALL", "open_cfw_compress_log_file_remove"),
        ("R_ARM_THM_CALL", "open_cfw_compress_log_path_format"),
        ("R_ARM_THM_CALL", "open_cfw_file_open"),
        ("R_ARM_THM_CALL", "open_cfw_compress_log_write_file_version_header"),
        ("R_ARM_THM_CALL", "open_cfw_file_close"),
        ("R_ARM_THM_CALL", "open_cfw_compress_log_manager_save"),
    ),
    "open_cfw_compress_log_sync_to_files": (
        ("R_ARM_THM_CALL", "open_cfw_compress_log_manager_load"),
        ("R_ARM_THM_CALL", "open_cfw_compress_log_rotate_file"),
        ("R_ARM_THM_CALL", "open_cfw_compress_log_path_format"),
        ("R_ARM_THM_CALL", "open_cfw_file_open"),
        ("R_ARM_THM_CALL", "open_cfw_file_open"),
        ("R_ARM_THM_CALL", "open_cfw_compress_log_write_file_version_header"),
        ("R_ARM_THM_CALL", "open_cfw_file_seek"),
        ("R_ARM_THM_CALL", "open_cfw_file_write"),
        ("R_ARM_THM_CALL", "open_cfw_file_close"),
        ("R_ARM_THM_CALL", "open_cfw_compress_log_manager_save"),
    ),
    "open_cfw_compress_log_export_notify": (
        ("R_ARM_THM_MOVW_PREL_NC", "open_cfw_compress_log_export_timeout_callback"),
        ("R_ARM_THM_MOVT_PREL", "open_cfw_compress_log_export_timeout_callback"),
        ("R_ARM_THM_CALL", "open_cfw_event_loop_remove_delayed"),
        ("R_ARM_THM_MOVW_PREL_NC", "open_cfw_compress_log_export_timeout_callback"),
        ("R_ARM_THM_MOVT_PREL", "open_cfw_compress_log_export_timeout_callback"),
        ("R_ARM_THM_CALL", "open_cfw_event_loop_push_delayed"),
    ),
}

CLOSURE_SIGNATURES = {
    "open_cfw_compress_log_path_format": (
        ("R_ARM_THM_MOVW_PREL_NC", ".L.str"),
        ("R_ARM_THM_MOVT_PREL", ".L.str"),
        ("R_ARM_THM_JUMP24", "open_cfw_runtime_snprintf"),
    ),
    "open_cfw_compress_log_file_exists": (
        ("R_ARM_THM_CALL", "open_cfw_compress_log_path_format"),
        ("R_ARM_THM_MOVW_PREL_NC", ".L.str"),
        ("R_ARM_THM_MOVT_PREL", ".L.str"),
        ("R_ARM_THM_CALL", "open_cfw_file_open"),
        ("R_ARM_THM_CALL", "open_cfw_file_close"),
    ),
    "open_cfw_compress_log_manager_load": (
        ("R_ARM_THM_MOVW_PREL_NC", ".L.str"),
        ("R_ARM_THM_MOVT_PREL", ".L.str"),
        ("R_ARM_THM_MOVW_PREL_NC", ".L.str.1"),
        ("R_ARM_THM_MOVT_PREL", ".L.str.1"),
        ("R_ARM_THM_CALL", "open_cfw_file_open"),
        ("R_ARM_THM_CALL", "open_cfw_file_read"),
        ("R_ARM_THM_CALL", "open_cfw_file_close"),
        ("R_ARM_THM_JUMP24", "open_cfw_compress_log_manager_reconcile"),
    ),
    "open_cfw_compress_log_manager_save": (
        ("R_ARM_THM_MOVW_PREL_NC", ".L.str"),
        ("R_ARM_THM_MOVT_PREL", ".L.str"),
        ("R_ARM_THM_MOVW_PREL_NC", ".L.str.1"),
        ("R_ARM_THM_MOVT_PREL", ".L.str.1"),
        ("R_ARM_THM_CALL", "open_cfw_file_open"),
        ("R_ARM_THM_CALL", "open_cfw_file_write"),
        ("R_ARM_THM_CALL", "open_cfw_file_close"),
    ),
    "open_cfw_compress_log_write_file_version_header": (
        ("R_ARM_THM_MOVW_PREL_NC", ".L.str"),
        ("R_ARM_THM_MOVT_PREL", ".L.str"),
        ("R_ARM_THM_MOVW_PREL_NC", ".L.str.1"),
        ("R_ARM_THM_MOVT_PREL", ".L.str.1"),
        ("R_ARM_THM_CALL", "open_cfw_runtime_snprintf"),
        ("R_ARM_THM_CALL", "open_cfw_file_seek"),
        ("R_ARM_THM_CALL", "open_cfw_file_write"),
    ),
    "open_cfw_compress_log_rotate_file": (
        ("R_ARM_THM_CALL", "open_cfw_compress_log_file_remove"),
        ("R_ARM_THM_CALL", "open_cfw_compress_log_path_format"),
        ("R_ARM_THM_MOVW_PREL_NC", ".L.str"),
        ("R_ARM_THM_MOVT_PREL", ".L.str"),
        ("R_ARM_THM_CALL", "open_cfw_file_open"),
        ("R_ARM_THM_CALL", "open_cfw_compress_log_write_file_version_header"),
        ("R_ARM_THM_CALL", "open_cfw_file_close"),
        ("R_ARM_THM_CALL", "open_cfw_compress_log_manager_save"),
    ),
    "open_cfw_compress_log_sync_to_files": (
        ("R_ARM_THM_CALL", "open_cfw_compress_log_manager_load"),
        ("R_ARM_THM_CALL", "open_cfw_compress_log_rotate_file"),
        ("R_ARM_THM_CALL", "open_cfw_compress_log_path_format"),
        ("R_ARM_THM_MOVW_PREL_NC", ".L.str"),
        ("R_ARM_THM_MOVT_PREL", ".L.str"),
        ("R_ARM_THM_CALL", "open_cfw_file_open"),
        ("R_ARM_THM_MOVW_PREL_NC", ".L.str.1"),
        ("R_ARM_THM_MOVT_PREL", ".L.str.1"),
        ("R_ARM_THM_CALL", "open_cfw_file_open"),
        ("R_ARM_THM_CALL", "open_cfw_compress_log_write_file_version_header"),
        ("R_ARM_THM_CALL", "open_cfw_file_seek"),
        ("R_ARM_THM_CALL", "open_cfw_file_write"),
        ("R_ARM_THM_CALL", "open_cfw_file_close"),
        ("R_ARM_THM_CALL", "open_cfw_compress_log_manager_save"),
    ),
}

APPLE_TEXT_SIZES = {
    "open_cfw_compress_log_path_format": 20,
    "open_cfw_compress_log_file_exists": 46,
    "open_cfw_compress_log_manager_reconcile": 164,
    "open_cfw_compress_log_manager_load": 186,
    "open_cfw_compress_log_manager_save": 80,
    "open_cfw_compress_log_file_remove": 24,
    "open_cfw_compress_log_write_file_version_header": 86,
    "open_cfw_compress_log_rotate_file": 142,
    "open_cfw_compress_log_sync_to_files": 258,
    "open_cfw_compress_log_export_timeout_callback": 14,
    "open_cfw_compress_log_export_notify": 58,
    "open_cfw_compress_log_export_active": 12,
}
RODATA = {
    "open_cfw_compress_log_path_format": (25, "9f5fe161d8c958244a6a3b751dbdee40b1b6c044b7bc7c380dcbea52784ebaeb", ((".L.str", 0, 25),)),
    "open_cfw_compress_log_file_exists": (3, "ef4a3d25250e72708f6f82d59e29b96880728d971ae0b4862d37c9cd927bb082", ((".L.str", 0, 3),)),
    "open_cfw_compress_log_manager_load": (29, "19dfed9c8c2c9a2fe9c44689039998f601d3e01b008235119651908c0ce12bd4", ((".L.str", 0, 26), (".L.str.1", 26, 3))),
    "open_cfw_compress_log_manager_save": (29, "9eb0b0394d450e189ee3ceb118643cfded899c1948f804230a89cc0f1408be5e", ((".L.str", 0, 26), (".L.str.1", 26, 3))),
    "open_cfw_compress_log_write_file_version_header": (31, "3e33b380b678d790a8e142f1006ae81dd3d89c480115b2c5adaae0eff47b1eaf", ((".L.str", 0, 22), (".L.str.1", 22, 9))),
    "open_cfw_compress_log_rotate_file": (3, "229b7c9a4f22005ef2af2aa0e5b226b59c93e9fe97ffd2a05019cb831eaa6121", ((".L.str", 0, 3),)),
    "open_cfw_compress_log_sync_to_files": (8, "7ee96647cbdacba45660055d9def003a4eb4982f8ba768aeead70602ce5aef32", ((".L.str", 0, 4), (".L.str.1", 4, 4))),
}


def _load(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


admission = _load(
    "g2_canonical_admission", ROOT / "tools/apply_g2_canonical_observations.py"
)
builder = admission._load_core_builder()


def _digest(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _rows() -> list[dict[str, Any]]:
    with FUNCTION_MAP.open(newline="", encoding="utf-8") as handle:
        raw = list(csv.DictReader(handle, delimiter="\t"))
    if len(raw) != len(FUNCTIONS):
        raise admission.AdmissionError("compact-log map must contain 12 rows")
    rows = []
    for index, row in enumerate(raw):
        if row["function"] != STOCK_NAMES[index]:
            raise admission.AdmissionError("compact-log function order changed")
        rows.append({
            "function": FUNCTIONS[index][1],
            "start": int(row["stock_start"], 0),
            "size": int(row["stock_bytes"], 0),
            "sha256": row["stock_sha256"],
        })
    return rows


def _source_records() -> list[dict[str, Any]]:
    common = {
        "evidence": "docs/research/g2-compress-log-port-recovery.md",
        "license": "MIT",
        "origin": (
            "clean-room reconstruction of the complete G2 compact-log "
            "file-port persistence, rotation, and export-timeout policy"
        ),
    }
    return [
        {**common, "path": "components/apollo_main/core_overlay/compress_log_port.c",
         "sha256": SOURCE_SHA256, "size": SOURCE_SIZE},
        {**common, "path": "components/apollo_main/core_overlay/compress_log_port.h",
         "sha256": HEADER_SHA256, "size": HEADER_SIZE},
    ]


def _relocations(function: str) -> list[dict[str, Any]]:
    result = []
    signature = CALLS.get(function, ())
    for index, (kind, symbol) in enumerate(signature):
        item = {
            "offset": index * 2,
            "type": kind,
            "symbol": symbol,
        }
        if not symbol.startswith(".L."):
            item.update({
                "symbol_type": "STT_NOTYPE",
                "target_function": symbol,
            })
        result.append(item)
    return result


def _stub_config(config: dict[str, Any]) -> dict[str, Any]:
    proposed = copy.deepcopy(config)
    rows = _rows()
    functions = [row["function"] for row in rows]
    function_set = set(functions)
    entries = {row["start"] for row in rows}
    proposed["functions"] = [
        item for item in proposed.get("functions", []) if item not in function_set
    ] + functions
    proposed["sources"] = [
        item for item in proposed.get("sources", [])
        if "compress_log_port" not in item.get("path", "")
    ] + [_source_records()[1]]
    proposed["patch_sites"] = [
        item for item in proposed.get("patch_sites", [])
        if item.get("runtime_address") not in entries
        and item.get("target_function") not in function_set
    ]
    for index, row in enumerate(rows, 1):
        proposed["patch_sites"].append({
            "branch": "b_w",
            "expected_sha256": row["sha256"],
            "expected_size": row["size"],
            "name": f"replace_compress_log_port_{index:02d}",
            "runtime_address": row["start"],
            "target_function": row["function"],
        })
    proposed["relocated_leaves"] = [
        item for item in proposed.get("relocated_leaves", [])
        if item.get("function") not in function_set
    ]
    for function in LEAF_ORDER:
        text_size = APPLE_TEXT_SIZES[function]
        placeholder = {
            "alignment": 4,
            "offset": 0,
            "sha256": "0" * 64,
            "size": text_size,
            "unrelocated_sha256": "0" * 64,
        }
        leaf = {
            "expected": copy.deepcopy(placeholder),
            "function": function,
            "relocations": _relocations(function),
            "source": copy.deepcopy(_source_records()[0]),
            "strict_relocation_contract": True,
            "allow_discarded_alloc_sections": True,
            "toolchain": {
                "flags": [
                    *BASE_FLAGS,
                    f"-DOPEN_CFW_COMPRESS_LOG_{SELECTOR[function]}_ONLY=1",
                ],
                "reviewed_version_prefix": "Apple clang version 21.0.0",
                "target": "thumbv7em-none-eabi",
            },
            "toolchain_profiles": {
                "linux-clang": {
                    "reviewed_version_prefix": "Homebrew clang version 22.1.8",
                    "expected": copy.deepcopy(placeholder),
                    "relocations": copy.deepcopy(_relocations(function)),
                }
            },
        }
        proposed["relocated_leaves"].append(leaf)
    return proposed


def _leaf_map(observation: dict[str, Any]) -> dict[str, dict[str, Any]]:
    indexed = admission._indexed_leaves(
        observation["core_stage"], "relocated_leaves"
    )
    functions = {item[1] for item in FUNCTIONS}
    selected = {
        function: copy.deepcopy(indexed[function])
        for function in functions if function in indexed
    }
    if set(selected) != functions:
        raise admission.AdmissionError("observed compact-log leaf set is incomplete")
    return selected


def _set_stage_pins(
    config: dict[str, Any], profile: str, observation: dict[str, Any]
) -> None:
    if profile == "apple-clang":
        config["core_stage_expected"] = copy.deepcopy(
            observation["core_stage"]["expected"]
        )
    else:
        config["toolchain_profiles"][profile]["core_stage_expected"] = copy.deepcopy(
            observation["core_stage"]["expected"]
        )
    provider = config["post_link_providers"]["liblc3_ltpf"]["profiles"][profile]
    liblc3 = observation["liblc3_ltpf"]
    provider["overlay"] = {
        "size": liblc3["payload_size"], "sha256": liblc3["payload_sha256"]
    }
    provider["component"] = {
        "size": liblc3["component_size"], "sha256": liblc3["component_sha256"]
    }


def _review(paths: list[Path]) -> tuple[dict[str, Any], dict[str, Any]]:
    apple_pair = admission.admit_reproducible_pair(paths[:2], "apple-clang")
    linux_pair = admission.admit_reproducible_pair(paths[2:], "linux-clang")
    admission.validate_observation_independence((*apple_pair, *linux_pair))
    admission.validate_generation(apple_pair[0], linux_pair[0])
    apple = apple_pair[0]["observation"]
    linux = linux_pair[0]["observation"]
    proposed = _stub_config(json.loads(CONFIG.read_text(encoding="utf-8")))
    apple_leaves = _leaf_map(apple)
    linux_leaves = _leaf_map(linux)
    for leaf in proposed["relocated_leaves"]:
        function = leaf.get("function")
        if function not in apple_leaves:
            continue
        apple_pins = copy.deepcopy(apple_leaves[function]["pins"])
        leaf["relocations"] = apple_pins.pop("relocations")
        leaf["expected"] = apple_pins
        linux_pins = copy.deepcopy(linux_leaves[function]["pins"])
        leaf["toolchain_profiles"]["linux-clang"]["relocations"] = (
            linux_pins.pop("relocations")
        )
        leaf["toolchain_profiles"]["linux-clang"]["expected"] = linux_pins
    _set_stage_pins(proposed, "apple-clang", apple)
    _set_stage_pins(proposed, "linux-clang", linux)
    snapshot = builder._canonical_input_snapshot(ROOT, CONFIG, proposed)
    admission.validate_current_inputs(apple["source_inputs"], snapshot)
    for profile, observation in (("apple-clang", apple), ("linux-clang", linux)):
        admission._require_reviewed_core_leaf_pins(proposed, profile, observation)
        admission.update_profile_pins(proposed, profile, observation)
    return proposed, {
        "mode": "reviewed-four-observation",
        "source_inputs_sha256": builder._canonical_input_report(snapshot)["sha256"],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--prepare", action="store_true")
    mode.add_argument(
        "--review-observations", nargs=4, type=Path,
        metavar=("APPLE_A", "APPLE_B", "LINUX_A", "LINUX_B"),
    )
    parser.add_argument("--proposal", type=Path)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    for path, expected_size, expected_sha in (
        (SOURCE, SOURCE_SIZE, SOURCE_SHA256),
        (HEADER, HEADER_SIZE, HEADER_SHA256),
    ):
        payload = path.read_bytes()
        if len(payload) != expected_size or _digest(payload) != expected_sha:
            raise SystemExit(f"compact-log source identity changed: {path.name}")
    if args.prepare:
        proposed = _stub_config(json.loads(CONFIG.read_text(encoding="utf-8")))
        receipt = {"mode": "observation-stub"}
    else:
        proposed, receipt = _review(args.review_observations)
    encoded = (json.dumps(proposed, indent=2) + "\n").encode("utf-8")
    if args.proposal:
        if args.proposal.resolve() == CONFIG.resolve():
            raise SystemExit("proposal path must differ from live config")
        admission.atomic_write(args.proposal, encoded)
    if args.apply:
        admission.atomic_write(CONFIG, encoded)
    receipt.update({
        "applied": args.apply,
        "proposal": str(args.proposal) if args.proposal else None,
        "functions": [item[1] for item in FUNCTIONS],
        "hardware_operations": [],
    })
    print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
