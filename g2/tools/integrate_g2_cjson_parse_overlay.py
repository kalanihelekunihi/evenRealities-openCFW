#!/usr/bin/env python3
"""Install and review the authenticated G2 cJSON parse-side source route."""

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
SOURCE = ROOT / "components/shared/cjson/runtime_cjson_parse.c"
FUNCTION_MAP = ROOT / "tools/manifests/g2-json-parser-function-map.tsv"
SOURCE_IDENTITY = {
    "evidence": "docs/research/g2-json-parser-source-candidate-audit.md",
    "license": "MIT",
    "origin": (
        "bounded freestanding adaptation of the authenticated DaveGamble/cJSON "
        "v1.7.12 parse-side closure for the G2 SRAM hook/error ABI"
    ),
    "path": "components/shared/cjson/runtime_cjson_parse.c",
    "sha256": "710c9d2357e850730b169fb48b190fbe06e08b8da09f34736b38c3122c6dad63",
    "size": 26_626,
    "upstream": "https://github.com/DaveGamble/cJSON/tree/v1.7.12",
    "upstream_commit": "3c8935676a97c7c97bf006db8312875b4f292f6c",
}
BASE_FLAGS = [
    "-mthumb", "-mcpu=cortex-m55", "-mfpu=fp-armv8", "-mfloat-abi=hard",
    "-Oz", "-ffreestanding", "-fno-jump-tables", "-fomit-frame-pointer",
    "-fno-builtin", "-mno-unaligned-access", "-fno-unwind-tables",
    "-fno-asynchronous-unwind-tables", "-fropi", "-ffunction-sections",
    "-fdata-sections", "-Wall", "-Wextra", "-Werror", "-mllvm",
    "-enable-machine-outliner=never", "-fno-ident", "-DOPEN_CFW_CJSON_G2=1",
]
INCLUDE_DIRS = ["third_party/cJSON/g2-compat", "third_party/cJSON"]

# Ordered relocation signatures are compiler-independent across the reviewed
# Apple clang 21 and Homebrew clang 22 profiles.  Offsets are observed and
# replaced during canonical recording.
CALLS: dict[str, tuple[tuple[str, str], ...]] = {
    "cJSON_Delete": (("R_ARM_THM_CALL", "cJSON_Delete"),),
    "utf16_literal_to_utf8": (
        ("R_ARM_THM_CALL", "parse_hex4"),
        ("R_ARM_THM_CALL", "parse_hex4"),
    ),
    "parse_string": (("R_ARM_THM_CALL", "utf16_literal_to_utf8"),),
    "cJSON_ParseWithOpts": (
        ("R_ARM_THM_CALL", "cJSON_New_Item"),
        ("R_ARM_THM_CALL", "skip_utf8_bom"),
        ("R_ARM_THM_CALL", "buffer_skip_whitespace"),
        ("R_ARM_THM_CALL", "parse_value"),
        ("R_ARM_THM_CALL", "buffer_skip_whitespace"),
        ("R_ARM_THM_CALL", "cJSON_Delete"),
    ),
    "parse_value": (
        ("R_ARM_THM_JUMP24", "parse_string"),
        ("R_ARM_THM_JUMP24", "parse_number"),
        ("R_ARM_THM_JUMP24", "parse_array"),
        ("R_ARM_THM_JUMP24", "parse_object"),
    ),
    "cJSON_Parse": (("R_ARM_THM_JUMP24", "cJSON_ParseWithOpts"),),
    "parse_array": (
        ("R_ARM_THM_CALL", "buffer_skip_whitespace"),
        ("R_ARM_THM_CALL", "cJSON_New_Item"),
        ("R_ARM_THM_CALL", "buffer_skip_whitespace"),
        ("R_ARM_THM_CALL", "parse_value"),
        ("R_ARM_THM_CALL", "buffer_skip_whitespace"),
        ("R_ARM_THM_CALL", "cJSON_Delete"),
    ),
    "parse_object": (
        ("R_ARM_THM_CALL", "buffer_skip_whitespace"),
        ("R_ARM_THM_CALL", "cJSON_New_Item"),
        ("R_ARM_THM_CALL", "buffer_skip_whitespace"),
        ("R_ARM_THM_CALL", "parse_string"),
        ("R_ARM_THM_CALL", "buffer_skip_whitespace"),
        ("R_ARM_THM_CALL", "buffer_skip_whitespace"),
        ("R_ARM_THM_CALL", "parse_value"),
        ("R_ARM_THM_CALL", "buffer_skip_whitespace"),
        ("R_ARM_THM_CALL", "cJSON_Delete"),
    ),
    "cJSON_GetArrayItem": (("R_ARM_THM_JUMP24", "get_array_item"),),
    "get_object_item": (("R_ARM_THM_CALL", "case_insensitive_strcmp"),),
    "cJSON_GetObjectItem": (("R_ARM_THM_JUMP24", "get_object_item"),),
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
        source_rows = list(csv.DictReader(handle, delimiter="\t"))
    if len(source_rows) != 21:
        raise admission.AdmissionError("cJSON function map must contain 21 rows")
    rows: list[dict[str, Any]] = []
    for row in source_rows:
        rows.append({
            "function": row["function"],
            "start": int(row["stock_start"], 0),
            "size": int(row["stock_bytes"], 0),
            "sha256": row["stock_sha256"],
        })
    return rows


def _relocations(function: str, entries: dict[str, int]) -> list[dict[str, Any]]:
    result = []
    for index, (kind, symbol) in enumerate(CALLS.get(function, ())) :
        item: dict[str, Any] = {
            "offset": index * 2,
            "type": kind,
            "symbol": symbol,
            "symbol_type": "STT_FUNC",
        }
        if symbol == function:
            item["target_function"] = symbol
        else:
            item["target_address"] = entries[symbol]
        result.append(item)
    return result


def _stub_config(config: dict[str, Any]) -> dict[str, Any]:
    proposed = copy.deepcopy(config)
    rows = _rows()
    functions = [row["function"] for row in rows]
    entries = {row["function"]: row["start"] for row in rows}
    entry_set = set(entries.values())
    function_set = set(functions)
    proposed["functions"] = [
        function for function in proposed.get("functions", [])
        if function not in function_set
    ] + functions
    proposed["patch_sites"] = [
        item for item in proposed.get("patch_sites", [])
        if item.get("runtime_address") not in entry_set
        and item.get("target_function") not in function_set
    ]
    for index, row in enumerate(rows, 1):
        proposed["patch_sites"].append({
            "branch": "b_w",
            "expected_sha256": row["sha256"],
            "expected_size": row["size"],
            "name": f"replace_cjson_parse_{index:02d}",
            "runtime_address": row["start"],
            "target_function": row["function"],
        })
    proposed["relocated_leaves"] = [
        item for item in proposed.get("relocated_leaves", [])
        if item.get("function") not in function_set
    ]
    for function in functions:
        alignment = (
            8 if function == "parse_number" else
            4 if function in {"cJSON_Delete", "cJSON_ParseWithOpts"} else 2
        )
        placeholder = {
            "alignment": alignment,
            "offset": 0,
            "sha256": "0" * 64,
            "size": 1,
            "unrelocated_sha256": "0" * 64,
        }
        relocations = _relocations(function, entries)
        proposed["relocated_leaves"].append({
            "expected": copy.deepcopy(placeholder),
            "function": function,
            "relocations": relocations,
            "source": copy.deepcopy(SOURCE_IDENTITY),
            "strict_relocation_contract": True,
            "allow_discarded_alloc_sections": True,
            **({"allow_self_relocation": True} if function == "cJSON_Delete" else {}),
            "toolchain": {
                "flags": BASE_FLAGS,
                "include_dirs": INCLUDE_DIRS,
                "reviewed_version_prefix": "Apple clang version 21.0.0",
                "target": "thumbv7em-none-eabi",
            },
            "toolchain_profiles": {
                "linux-clang": {
                    "reviewed_version_prefix": "Homebrew clang version 22.1.8",
                    "expected": copy.deepcopy(placeholder),
                    "relocations": copy.deepcopy(relocations),
                }
            },
        })
    return proposed


def _observation(path: Path, profile: str) -> dict[str, Any]:
    report = json.loads(path.read_text(encoding="utf-8"))
    observation = report.get("canonical_observation")
    if not isinstance(observation, dict) or observation.get("complete") is not True:
        raise admission.AdmissionError(f"incomplete observation: {path}")
    if observation.get("profile") != profile:
        raise admission.AdmissionError(f"observation profile mismatch: {path}")
    return observation


def _leaf_map(observation: dict[str, Any]) -> dict[str, dict[str, Any]]:
    indexed = admission._indexed_leaves(
        observation["core_stage"], "relocated_leaves"
    )
    functions = {row["function"] for row in _rows()}
    selected = {
        function: copy.deepcopy(indexed[function])
        for function in functions if function in indexed
    }
    if set(selected) != functions:
        raise admission.AdmissionError("observed cJSON leaf set is incomplete")
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
        metavar=("APPLE_A", "APPLE_B", "LINUX_A", "LINUX_B")
    )
    parser.add_argument("--proposal", type=Path)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    payload = SOURCE.read_bytes()
    if len(payload) != SOURCE_IDENTITY["size"] or _digest(payload) != SOURCE_IDENTITY["sha256"]:
        raise SystemExit("cJSON production source identity changed")
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
        "functions": [row["function"] for row in _rows()],
        "hardware_operations": [],
    })
    print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
