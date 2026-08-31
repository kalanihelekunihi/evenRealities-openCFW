#!/usr/bin/env python3
"""Install and review all three source-owned G2 NemaVG stroke-cap leaves."""

# SPDX-License-Identifier: MIT

from __future__ import annotations

import argparse
import copy
import importlib.util
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "components/apollo_main/core_overlay/overlay.json"
SOURCE = ROOT / "components/apollo_main/core_overlay/runtime_nemavg_stroke_cap_endpoints.c"
SOURCE_IDENTITY = {
    "evidence": "docs/research/g2-nemavg-stroke-caps-source-candidate.md",
    "license": "MIT",
    "origin": (
        "clean-room NemaVG 1.1.8 stroke-cap geometry over authenticated G2 "
        "context layout and retained public NemaGFX raster-provider ABIs"
    ),
    "path": "components/apollo_main/core_overlay/runtime_nemavg_stroke_cap_endpoints.c",
    "sha256": "33c9292bb52e276982e9b6c4c51bc02d9381eec98f50f223c876c7f691a986a4",
    "size": 15_166,
}
ROUTES = (
    ("START", "open_cfw_nemavg_draw_start_cap_endpoint", 0x0051B8F0, 1_668,
     "549fd3c4e21f1074d6f2b04309e72283b3f85b575f41bd31fc4718f7a63e3382"),
    ("END", "open_cfw_nemavg_draw_end_cap_endpoint", 0x0051BF7C, 1_640,
     "d022571f745517bf7494d69d79e5c1ba934faf8dc65c0cb6f465d4f36fb81d56"),
    ("DISPATCH", "open_cfw_nemavg_draw_caps_dispatch", 0x0051C5EC, 3_306,
     "7487038aa5bf05ee5c13296625a2ddf2c7ea592f5dc975661b7f6e0c7a3c1c27"),
)
NEMA_FUNCTIONS = {route[1] for route in ROUTES} | {
    "open_cfw_nemavg_draw_start_cap", "open_cfw_nemavg_draw_end_cap",
    "open_cfw_nemavg_draw_caps",
}
NEMA_ENTRIES = {route[2] for route in ROUTES}
BASE_FLAGS = [
    "-mthumb", "-mcpu=cortex-m55", "-mfpu=fp-armv8", "-mfloat-abi=hard",
    "-Oz", "-ffreestanding", "-fno-jump-tables", "-fomit-frame-pointer",
    "-fno-builtin", "-mno-unaligned-access", "-fno-unwind-tables",
    "-fno-asynchronous-unwind-tables", "-fropi", "-ffunction-sections",
    "-fdata-sections", "-Wall", "-Wextra", "-Werror", "-mllvm",
    "-enable-machine-outliner=never", "-fno-ident",
]


def _load(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


admission = _load("g2_canonical_admission", ROOT / "tools/apply_g2_canonical_observations.py")
builder = admission._load_core_builder()


def _observation(path: Path, profile: str) -> dict[str, Any]:
    report = json.loads(path.read_text(encoding="utf-8"))
    observation = report.get("canonical_observation")
    if not isinstance(observation, dict) or observation.get("complete") is not True:
        raise admission.AdmissionError(f"incomplete observation: {path}")
    if observation.get("profile") != profile:
        raise admission.AdmissionError(f"observation profile mismatch: {path}")
    return observation


def _leaf_map(observation: dict[str, Any]) -> dict[str, dict[str, Any]]:
    leaves = admission._indexed_leaves(observation["core_stage"], "relocated_leaves")
    selected = {function: copy.deepcopy(leaves[function])
                for function in (route[1] for route in ROUTES) if function in leaves}
    if set(selected) != {route[1] for route in ROUTES}:
        raise admission.AdmissionError("observed NemaVG leaf set is incomplete")
    for function, leaf in selected.items():
        pins = leaf.get("pins")
        if not isinstance(pins, dict) or not isinstance(pins.get("relocations"), list):
            raise admission.AdmissionError(f"observed pins are malformed: {function}")
    return selected


def _set_stage_pins(config: dict[str, Any], profile: str,
                    observation: dict[str, Any]) -> None:
    if profile == "apple-clang":
        config["core_stage_expected"] = copy.deepcopy(observation["core_stage"]["expected"])
    else:
        config["toolchain_profiles"][profile]["core_stage_expected"] = copy.deepcopy(
            observation["core_stage"]["expected"])
    liblc3 = observation["liblc3_ltpf"]
    provider = config["post_link_providers"]["liblc3_ltpf"]["profiles"][profile]
    provider["overlay"] = {"size": liblc3["payload_size"],
                           "sha256": liblc3["payload_sha256"]}
    provider["component"] = {"size": liblc3["component_size"],
                             "sha256": liblc3["component_sha256"]}


def _proposed(config: dict[str, Any], apple: dict[str, Any],
              linux: dict[str, Any]) -> dict[str, Any]:
    proposed = copy.deepcopy(config)
    proposed["functions"] = [function for function in proposed.get("functions", [])
                             if function not in NEMA_FUNCTIONS]
    proposed["functions"].extend(route[1] for route in ROUTES)
    proposed["patch_sites"] = [item for item in proposed.get("patch_sites", [])
                               if item.get("runtime_address") not in NEMA_ENTRIES
                               and item.get("target_function") not in NEMA_FUNCTIONS]
    for index, (_, function, entry, size, digest) in enumerate(ROUTES, 1):
        proposed["patch_sites"].append({
            "branch": "b_w", "expected_sha256": digest, "expected_size": size,
            "name": f"replace_nemavg_stroke_caps_{index:02d}",
            "runtime_address": entry, "target_function": function,
        })
    proposed["relocated_leaves"] = [
        item for item in proposed.get("relocated_leaves", [])
        if item.get("function") not in NEMA_FUNCTIONS]
    apple_leaves, linux_leaves = _leaf_map(apple), _leaf_map(linux)
    for selector, function, _, _, _ in ROUTES:
        apple_pins = copy.deepcopy(apple_leaves[function]["pins"])
        apple_relocations = apple_pins.pop("relocations")
        linux_pins = copy.deepcopy(linux_leaves[function]["pins"])
        linux_relocations = linux_pins.pop("relocations")
        proposed["relocated_leaves"].append({
            "expected": apple_pins, "function": function,
            "relocations": apple_relocations, "source": copy.deepcopy(SOURCE_IDENTITY),
            "strict_relocation_contract": True,
            "toolchain": {
                "flags": BASE_FLAGS + [f"-DOPEN_CFW_NEMAVG_STROKE_CAPS_{selector}_ONLY=1"],
                "reviewed_version_prefix": "Apple clang version 21.0.0",
                "target": "thumbv7em-none-eabi",
            },
            "toolchain_profiles": {"linux-clang": {
                "reviewed_version_prefix": "Homebrew clang version 22.1.8",
                "expected": linux_pins, "relocations": linux_relocations,
            }},
        })
    _set_stage_pins(proposed, "apple-clang", apple)
    _set_stage_pins(proposed, "linux-clang", linux)
    return proposed


def _review(paths: list[Path]) -> tuple[dict[str, Any], dict[str, Any]]:
    apple_pair = admission.admit_reproducible_pair(paths[:2], "apple-clang")
    linux_pair = admission.admit_reproducible_pair(paths[2:], "linux-clang")
    admission.validate_observation_independence((*apple_pair, *linux_pair))
    admission.validate_generation(apple_pair[0], linux_pair[0])
    apple, linux = apple_pair[0]["observation"], linux_pair[0]["observation"]
    proposed = _proposed(json.loads(CONFIG.read_text(encoding="utf-8")), apple, linux)
    snapshot = builder._canonical_input_snapshot(ROOT, CONFIG, proposed)
    admission.validate_current_inputs(apple["source_inputs"], snapshot)
    for profile, observation in (("apple-clang", apple), ("linux-clang", linux)):
        admission._require_reviewed_core_leaf_pins(proposed, profile, observation)
        admission.update_profile_pins(proposed, profile, observation)
    return proposed, {"mode": "reviewed-four-observation",
                      "source_inputs_sha256": builder._canonical_input_report(snapshot)["sha256"]}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--bootstrap-observations", nargs=2, type=Path,
                       metavar=("APPLE", "LINUX"))
    group.add_argument("--review-observations", nargs=4, type=Path,
                       metavar=("APPLE_A", "APPLE_B", "LINUX_A", "LINUX_B"))
    parser.add_argument("--proposal", type=Path)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    if SOURCE.stat().st_size != SOURCE_IDENTITY["size"] or admission._digest(
            SOURCE.read_bytes()) != SOURCE_IDENTITY["sha256"]:
        raise SystemExit("NemaVG production source identity changed")
    if args.review_observations:
        proposed, receipt = _review(args.review_observations)
    else:
        apple = _observation(args.bootstrap_observations[0], "apple-clang")
        linux = _observation(args.bootstrap_observations[1], "linux-clang")
        proposed = _proposed(json.loads(CONFIG.read_text(encoding="utf-8")), apple, linux)
        receipt = {"mode": "bootstrap-from-reviewed-leaf-pins"}
    payload = (json.dumps(proposed, indent=2) + "\n").encode("utf-8")
    if args.proposal:
        if args.proposal.resolve() == CONFIG.resolve():
            raise SystemExit("proposal path must differ from live config")
        admission.atomic_write(args.proposal, payload)
    if args.apply:
        admission.atomic_write(CONFIG, payload)
    receipt.update({"applied": args.apply,
                    "proposal": str(args.proposal) if args.proposal else None,
                    "functions": [route[1] for route in ROUTES],
                    "hardware_operations": []})
    print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
