#!/usr/bin/env python3
"""Install/review the complete G2 compact-record core source route."""

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
SOURCE = ROOT / "components/apollo_main/core_overlay/compress_log_core.c"
HEADER = SOURCE.with_suffix(".h")
FUNCTION_MAP = ROOT / "tools/manifests/g2-compress-log-core-function-map.tsv"
SOURCE_SHA256 = "5d7fdbcad7bd290e593af153d787b1351d3b7bdb47de9ebd69fdd60462ee9c38"
SOURCE_SIZE = 21_095
HEADER_SHA256 = "9ee8284247da8bc538b3288845e00e39672d4de7be1d7cca748b696e6983305b"
HEADER_SIZE = 899
BASE_FLAGS = [
    "-mthumb", "-mcpu=cortex-m55", "-O2", "-ffreestanding",
    "-fno-jump-tables", "-fomit-frame-pointer", "-fno-builtin",
    "-mno-unaligned-access", "-fno-unwind-tables",
    "-fno-asynchronous-unwind-tables", "-fropi", "-ffunction-sections",
    "-fdata-sections", "-Wall", "-Wextra", "-Werror", "-mllvm",
    "-enable-machine-outliner=never",
]

FUNCTIONS = (
    ("MUTEX_INIT", "open_cfw_compress_log_mutex_init"),
    ("RING_READ_LOCKED", "open_cfw_compress_log_ring_read_locked"),
    ("GET_ALL", "open_cfw_compress_log_get_all_buffer"),
    ("RING_WRITE", "open_cfw_compress_log_ring_write"),
    ("ENCODE", "open_cfw_compress_log_encode_record"),
    ("OUTPUT", "open_cfw_compress_log_output"),
    ("PERIODIC_SYNC", "open_cfw_compress_log_periodic_sync"),
    ("FORCE_SYNC", "open_cfw_compress_log_force_sync"),
)
SELECTOR = {function: selector for selector, function in FUNCTIONS}
STOCK_NAMES = (
    "compress_log_mutex_init",
    "compress_log_ring_read_locked",
    "_log_get_all_buffer",
    "compress_log_ring_write",
    "compress_log_encode_record",
    "compress_log_output",
    "svc_compress_log_sync_to_files",
    "svc_compress_log_force_sync_to_files",
)
APPLE_TEXT_SIZES = {
    "open_cfw_compress_log_mutex_init": 46,
    "open_cfw_compress_log_ring_read_locked": 282,
    "open_cfw_compress_log_get_all_buffer": 272,
    "open_cfw_compress_log_ring_write": 352,
    "open_cfw_compress_log_encode_record": 902,
    "open_cfw_compress_log_output": 94,
    "open_cfw_compress_log_periodic_sync": 252,
    "open_cfw_compress_log_force_sync": 298,
}

TARGETS: dict[str, tuple[str, int | str]] = {
    "open_cfw_freertos_queue_create_mutex_static": ("function", "open_cfw_freertos_queue_create_mutex_static"),
    "open_cfw_freertos_queue_take_mutex_recursive": ("function", "open_cfw_freertos_queue_take_mutex_recursive"),
    "open_cfw_freertos_queue_give_mutex_recursive": ("function", "open_cfw_freertos_queue_give_mutex_recursive"),
    "open_cfw_freertos_port_enter_critical": ("function", "open_cfw_freertos_port_enter_critical"),
    "open_cfw_freertos_port_exit_critical": ("function", "open_cfw_freertos_port_exit_critical"),
    "open_cfw_cmsis_kernel_get_tick_count": ("function", "open_cfw_cmsis_kernel_get_tick_count"),
    "open_cfw_wall_time_seconds": ("function", "open_cfw_wall_time_seconds"),
    "open_cfw_compress_log_export_active": ("function", "open_cfw_compress_log_export_active"),
    "open_cfw_compress_log_sync_to_files": ("function", "open_cfw_compress_log_sync_to_files"),
    "open_cfw_compress_log_ring_read_locked": ("function", "open_cfw_compress_log_ring_read_locked"),
    "open_cfw_compress_log_get_all_buffer": ("function", "open_cfw_compress_log_get_all_buffer"),
    "open_cfw_compress_log_ring_write": ("function", "open_cfw_compress_log_ring_write"),
    "open_cfw_compress_log_encode_record": ("function", "open_cfw_compress_log_encode_record"),
    "open_cfw_retained_compress_log_set_interrupt_mask": ("address", 0x005FA0A4),
    "open_cfw_retained_compress_log_clear_interrupt_mask": ("address", 0x005FA0BA),
    "open_cfw_retained_compress_log_mode": ("address", 0x0043D0CE),
    "open_cfw_retained_compress_log_filter_level": ("address", 0x0043D0DA),
    "open_cfw_retained_compress_log_pressure_allowed_a": ("address", 0x00443484),
    "open_cfw_retained_compress_log_pressure_allowed_b": ("address", 0x004487AC),
    "open_cfw_retained_compress_log_schedule_sync": ("address", 0x00448F7C),
}

CALLS: dict[str, tuple[tuple[str, str], ...]] = {
    "open_cfw_compress_log_mutex_init": (
        ("R_ARM_THM_CALL", "open_cfw_freertos_queue_create_mutex_static"),
        ("R_ARM_THM_CALL", "open_cfw_retained_compress_log_set_interrupt_mask"),
    ),
    "open_cfw_compress_log_ring_read_locked": (
        ("R_ARM_THM_CALL", "open_cfw_freertos_queue_take_mutex_recursive"),
        ("R_ARM_THM_CALL", "open_cfw_freertos_queue_give_mutex_recursive"),
    ),
    "open_cfw_compress_log_get_all_buffer": (
        ("R_ARM_THM_CALL", "open_cfw_retained_compress_log_set_interrupt_mask"),
        ("R_ARM_THM_CALL", "open_cfw_freertos_port_enter_critical"),
        ("R_ARM_THM_CALL", "open_cfw_retained_compress_log_clear_interrupt_mask"),
        ("R_ARM_THM_CALL", "open_cfw_freertos_port_exit_critical"),
    ),
    "open_cfw_compress_log_ring_write": (
        ("R_ARM_THM_CALL", "open_cfw_freertos_queue_take_mutex_recursive"),
        ("R_ARM_THM_CALL", "open_cfw_freertos_queue_give_mutex_recursive"),
        ("R_ARM_THM_CALL", "open_cfw_retained_compress_log_mode"),
        ("R_ARM_THM_CALL", "open_cfw_freertos_queue_give_mutex_recursive"),
        ("R_ARM_THM_CALL", "open_cfw_retained_compress_log_mode"),
        ("R_ARM_THM_CALL", "open_cfw_retained_compress_log_pressure_allowed_a"),
        ("R_ARM_THM_CALL", "open_cfw_retained_compress_log_pressure_allowed_b"),
        ("R_ARM_THM_CALL", "open_cfw_retained_compress_log_schedule_sync"),
        ("R_ARM_THM_CALL", "open_cfw_retained_compress_log_schedule_sync"),
        ("R_ARM_THM_CALL", "open_cfw_freertos_queue_give_mutex_recursive"),
    ),
    "open_cfw_compress_log_encode_record": (
        ("R_ARM_THM_CALL", "open_cfw_retained_compress_log_mode"),
        ("R_ARM_THM_CALL", "open_cfw_retained_compress_log_filter_level"),
        ("R_ARM_THM_CALL", "open_cfw_cmsis_kernel_get_tick_count"),
        ("R_ARM_THM_CALL", "open_cfw_wall_time_seconds"),
        ("R_ARM_THM_CALL", "open_cfw_compress_log_ring_write"),
    ),
    "open_cfw_compress_log_output": (
        ("R_ARM_THM_CALL", "open_cfw_compress_log_export_active"),
        ("R_ARM_THM_CALL", "open_cfw_freertos_queue_take_mutex_recursive"),
        ("R_ARM_THM_CALL", "open_cfw_compress_log_encode_record"),
        ("R_ARM_THM_CALL", "open_cfw_freertos_queue_give_mutex_recursive"),
    ),
    "open_cfw_compress_log_periodic_sync": (
        ("R_ARM_THM_CALL", "open_cfw_cmsis_kernel_get_tick_count"),
        *(("R_ARM_THM_CALL", "open_cfw_compress_log_ring_read_locked"),
          ("R_ARM_THM_CALL", "open_cfw_compress_log_sync_to_files")) * 8,
        ("R_ARM_THM_CALL", "open_cfw_compress_log_ring_read_locked"),
        ("R_ARM_THM_JUMP24", "open_cfw_compress_log_sync_to_files"),
    ),
    "open_cfw_compress_log_force_sync": (
        *(("R_ARM_THM_CALL", "open_cfw_compress_log_ring_read_locked"),
          ("R_ARM_THM_CALL", "open_cfw_compress_log_sync_to_files")) * 9,
        ("R_ARM_THM_CALL", "open_cfw_compress_log_get_all_buffer"),
        ("R_ARM_THM_JUMP24", "open_cfw_compress_log_sync_to_files"),
    ),
}

LINUX_CALLS = copy.deepcopy(CALLS)
LINUX_CALLS["open_cfw_compress_log_ring_write"] = (
    ("R_ARM_THM_CALL", "open_cfw_freertos_queue_take_mutex_recursive"),
    ("R_ARM_THM_CALL", "open_cfw_freertos_queue_give_mutex_recursive"),
    ("R_ARM_THM_CALL", "open_cfw_retained_compress_log_mode"),
    ("R_ARM_THM_CALL", "open_cfw_retained_compress_log_pressure_allowed_a"),
    ("R_ARM_THM_CALL", "open_cfw_retained_compress_log_pressure_allowed_b"),
    ("R_ARM_THM_CALL", "open_cfw_retained_compress_log_schedule_sync"),
    ("R_ARM_THM_CALL", "open_cfw_retained_compress_log_schedule_sync"),
    ("R_ARM_THM_CALL", "open_cfw_retained_compress_log_mode"),
    ("R_ARM_THM_CALL", "open_cfw_freertos_queue_give_mutex_recursive"),
    ("R_ARM_THM_CALL", "open_cfw_freertos_queue_give_mutex_recursive"),
)


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
        raise admission.AdmissionError("compact-log core map must contain 8 rows")
    rows = []
    for index, row in enumerate(raw):
        if row["function"] != STOCK_NAMES[index]:
            raise admission.AdmissionError("compact-log core function order changed")
        rows.append({
            "function": FUNCTIONS[index][1],
            "start": int(row["stock_start"], 0),
            "size": int(row["stock_bytes"], 0),
            "sha256": row["stock_sha256"],
        })
    return rows


def _source_records() -> list[dict[str, Any]]:
    common = {
        "evidence": "docs/research/g2-compress-log-core-recovery.md",
        "license": "MIT",
        "origin": (
            "clean-room reconstruction of the complete G2 compact-record "
            "ring, encoder, filtering, and persistence scheduling core"
        ),
    }
    return [
        {**common, "path": "components/apollo_main/core_overlay/compress_log_core.c",
         "sha256": SOURCE_SHA256, "size": SOURCE_SIZE},
        {**common, "path": "components/apollo_main/core_overlay/compress_log_core.h",
         "sha256": HEADER_SHA256, "size": HEADER_SIZE},
    ]


def _relocations(function: str, profile: str = "apple-clang") -> list[dict[str, Any]]:
    result = []
    calls = CALLS if profile == "apple-clang" else LINUX_CALLS
    for index, (kind, symbol) in enumerate(calls.get(function, ())):
        item: dict[str, Any] = {
            "offset": index * 2,
            "type": kind,
            "symbol": symbol,
            "symbol_type": "STT_NOTYPE",
        }
        target_kind, target = TARGETS[symbol]
        item["target_function" if target_kind == "function" else "target_address"] = target
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
        if "compress_log_core" not in item.get("path", "")
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
            "name": f"replace_compress_log_core_{index:02d}",
            "runtime_address": row["start"],
            "target_function": row["function"],
        })
    proposed["relocated_leaves"] = [
        item for item in proposed.get("relocated_leaves", [])
        if item.get("function") not in function_set
    ]
    for function in functions:
        placeholder = {
            "alignment": 4,
            "offset": 0,
            "sha256": "0" * 64,
            "size": APPLE_TEXT_SIZES[function],
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
                    f"-DOPEN_CFW_COMPRESS_LOG_CORE_{SELECTOR[function]}_ONLY=1",
                ],
                "reviewed_version_prefix": "Apple clang version 21.0.0",
                "target": "thumbv7em-none-eabi",
            },
            "toolchain_profiles": {
                "linux-clang": {
                    "reviewed_version_prefix": "Homebrew clang version 22.1.8",
                    "expected": copy.deepcopy(placeholder),
                    "relocations": copy.deepcopy(_relocations(function, "linux-clang")),
                }
            },
        }
        proposed["relocated_leaves"].append(leaf)
    return proposed


def _leaf_map(observation: dict[str, Any]) -> dict[str, dict[str, Any]]:
    indexed = admission._indexed_leaves(observation["core_stage"], "relocated_leaves")
    functions = {item[1] for item in FUNCTIONS}
    selected = {
        function: copy.deepcopy(indexed[function])
        for function in functions if function in indexed
    }
    if set(selected) != functions:
        raise admission.AdmissionError("observed compact-log core leaf set is incomplete")
    return selected


def _set_stage_pins(config: dict[str, Any], profile: str, observation: dict[str, Any]) -> None:
    if profile == "apple-clang":
        config["core_stage_expected"] = copy.deepcopy(observation["core_stage"]["expected"])
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
        leaf["toolchain_profiles"]["linux-clang"]["relocations"] = linux_pins.pop("relocations")
        leaf["toolchain_profiles"]["linux-clang"]["expected"] = linux_pins
    _set_stage_pins(proposed, "apple-clang", apple)
    _set_stage_pins(proposed, "linux-clang", linux)
    config_entries = [
        item for item in apple["source_inputs"]["entries"]
        if item.get("path", "").endswith(
            "compress-log-core-overlay.proposal.json"
        )
    ]
    if len(config_entries) != 1:
        raise admission.AdmissionError(
            "canonical compact-log observation config identity is ambiguous"
        )
    observation_config = ROOT / config_entries[0]["path"]
    snapshot = builder._canonical_input_snapshot(
        ROOT, observation_config, proposed
    )
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
            raise SystemExit(f"compact-log core source identity changed: {path.name}")
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
