#!/usr/bin/env python3
"""Review and install the bounded NemaVG coordinator generation.

The two stroke-cap renderers remain retained stock providers.  This tool only
restores the source-owned no-argument coordinator at ``0x0051C5EC`` and may
record compiler-output pins after two independent observations per profile
agree.  It never compiles, signs, flashes, publishes, or contacts hardware.
"""

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
SOURCE = (
    ROOT / "components/apollo_main/core_overlay/"
    "runtime_nemavg_draw_caps_dispatch.c"
)
COORDINATOR = "open_cfw_nemavg_draw_caps_dispatch"
START_ENDPOINT = "open_cfw_nemavg_draw_start_cap_endpoint"
END_ENDPOINT = "open_cfw_nemavg_draw_end_cap_endpoint"
NEMA_FUNCTIONS = {COORDINATOR, START_ENDPOINT, END_ENDPOINT}
NEMA_ENTRIES = {0x0051B8F0, 0x0051BF7C, 0x0051C5EC}
SOURCE_IDENTITY = {
    "evidence": "docs/research/g2-nemavg-stroke-caps-source-candidate.md",
    "license": "MIT",
    "origin": (
        "clean-room NemaVG draw_caps coordinator over authenticated retained "
        "draw_start_cap, draw_end_cap, and NemaVG error-provider ABIs"
    ),
    "path": (
        "components/apollo_main/core_overlay/"
        "runtime_nemavg_draw_caps_dispatch.c"
    ),
    "sha256": "aa27ae41426f34111174d9520812c795ec59b0915aa474672978eccaa66c9966",
    "size": 2304,
}
PATCH = {
    "branch": "b_w",
    "expected_sha256": (
        "7487038aa5bf05ee5c13296625a2ddf2c7ea592f5dc975661b7f6e0c7a3c1c27"
    ),
    "expected_size": 3306,
    "name": "replace_nemavg_draw_caps_dispatch_01",
    "runtime_address": 0x0051C5EC,
    "target_function": COORDINATOR,
}
FLAGS = [
    "-mthumb",
    "-mcpu=cortex-m55",
    "-Oz",
    "-ffreestanding",
    "-fno-jump-tables",
    "-fomit-frame-pointer",
    "-fno-builtin",
    "-mno-unaligned-access",
    "-fno-unwind-tables",
    "-fno-asynchronous-unwind-tables",
    "-fropi",
    "-ffunction-sections",
    "-fdata-sections",
    "-Wall",
    "-Wextra",
    "-Werror",
    "-mllvm",
    "-enable-machine-outliner=never",
    "-fno-ident",
    "-DOPEN_CFW_NEMAVG_DRAW_CAPS_DISPATCH_ONLY=1",
]


def _load(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


admission = _load(
    "g2_canonical_admission",
    ROOT / "tools/apply_g2_canonical_observations.py",
)
builder = admission._load_core_builder()


def _pins(
    observation: dict[str, Any], expected_offsets: tuple[int, int, int]
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    leaves = admission._indexed_leaves(
        observation["core_stage"], "relocated_leaves"
    )
    item = leaves.get(COORDINATOR)
    if not isinstance(item, dict):
        raise admission.AdmissionError("coordinator leaf is absent from observation")
    pins = copy.deepcopy(item.get("pins"))
    if not isinstance(pins, dict):
        raise admission.AdmissionError("coordinator pins are malformed")
    relocations = pins.pop("relocations", None)
    if not isinstance(relocations, list) or len(relocations) != 3:
        raise admission.AdmissionError("coordinator relocation receipt changed")
    expected_targets = (
        ("open_cfw_retained_nemavg_draw_start_cap", 0x0051B8F0),
        ("open_cfw_retained_nemavg_draw_end_cap", 0x0051BF7C),
        ("open_cfw_retained_nemavg_set_error", 0x0051565C),
    )
    if any(not isinstance(item, dict) for item in relocations):
        raise admission.AdmissionError("coordinator relocation receipt changed")
    if tuple(
        (item.get("symbol"), item.get("target_address"))
        for item in relocations
    ) != expected_targets or tuple(
        item.get("offset") for item in relocations
    ) != expected_offsets:
        raise admission.AdmissionError("coordinator relocation receipt changed")
    if any(
        item.get("target_function") is not None
        or item.get("type") != "R_ARM_THM_CALL"
        or item.get("symbol_type") != "STT_NOTYPE"
        for item in relocations
    ):
        raise admission.AdmissionError(
            "coordinator no longer retains both endpoint providers"
        )
    return pins, relocations


def _restore_semantics(
    config: dict[str, Any], apple: dict[str, Any], linux: dict[str, Any]
) -> dict[str, Any]:
    proposed = copy.deepcopy(config)
    proposed["functions"] = [
        name for name in proposed.get("functions", []) if name not in NEMA_FUNCTIONS
    ]
    proposed["functions"].append(COORDINATOR)
    proposed["patch_sites"] = [
        item for item in proposed.get("patch_sites", [])
        if item.get("runtime_address") not in NEMA_ENTRIES
        and item.get("target_function") not in NEMA_FUNCTIONS
    ]
    proposed["patch_sites"].append(copy.deepcopy(PATCH))
    proposed["relocated_leaves"] = [
        item for item in proposed.get("relocated_leaves", [])
        if item.get("function") not in NEMA_FUNCTIONS
    ]

    apple_pins, apple_relocations = _pins(apple, (2, 8, 34))
    linux_pins, linux_relocations = _pins(linux, (2, 8, 30))
    proposed["relocated_leaves"].append({
        "expected": apple_pins,
        "function": COORDINATOR,
        "relocations": apple_relocations,
        "source": copy.deepcopy(SOURCE_IDENTITY),
        "strict_relocation_contract": True,
        "toolchain": {
            "flags": copy.deepcopy(FLAGS),
            "reviewed_version_prefix": "Apple clang version 21.0.0",
            "target": "thumbv7em-none-eabi",
        },
        "toolchain_profiles": {
            "linux-clang": {
                "reviewed_version_prefix": "Homebrew clang version 22.1.8",
                "expected": linux_pins,
                "relocations": linux_relocations,
            }
        },
    })

    proposed["core_stage_expected"] = copy.deepcopy(
        apple["core_stage"]["expected"]
    )
    proposed["toolchain_profiles"]["linux-clang"]["core_stage_expected"] = (
        copy.deepcopy(linux["core_stage"]["expected"])
    )
    providers = proposed["post_link_providers"]["liblc3_ltpf"]["profiles"]
    for profile, observation in (
        ("apple-clang", apple), ("linux-clang", linux)
    ):
        liblc3 = observation["liblc3_ltpf"]
        providers[profile]["overlay"] = {
            "size": liblc3["payload_size"],
            "sha256": liblc3["payload_sha256"],
        }
        providers[profile]["component"] = {
            "size": liblc3["component_size"],
            "sha256": liblc3["component_sha256"],
        }
    return proposed


def review(paths: list[Path]) -> tuple[dict[str, Any], dict[str, Any]]:
    if len(paths) != 4:
        raise admission.AdmissionError("exactly four observations are required")
    apple_pair = admission.admit_reproducible_pair(paths[:2], "apple-clang")
    linux_pair = admission.admit_reproducible_pair(paths[2:], "linux-clang")
    admission.validate_observation_independence((*apple_pair, *linux_pair))
    apple_receipt = apple_pair[0]
    linux_receipt = linux_pair[0]
    admission.validate_generation(apple_receipt, linux_receipt)
    apple = apple_receipt["observation"]
    linux = linux_receipt["observation"]

    if SOURCE.stat().st_size != SOURCE_IDENTITY["size"]:
        raise admission.AdmissionError("coordinator source size changed")
    if admission._digest(SOURCE.read_bytes()) != SOURCE_IDENTITY["sha256"]:
        raise admission.AdmissionError("coordinator source digest changed")
    config = json.loads(CONFIG.read_text(encoding="utf-8"))
    proposed = _restore_semantics(config, apple, linux)

    snapshot = builder._canonical_input_snapshot(ROOT, CONFIG, proposed)
    admission.validate_current_inputs(apple["source_inputs"], snapshot)
    for profile, observation in (
        ("apple-clang", apple), ("linux-clang", linux)
    ):
        admission._require_reviewed_core_leaf_pins(
            proposed, profile, observation
        )
        checked = copy.deepcopy(proposed)
        admission.update_profile_pins(checked, profile, observation)
    report = {
        "schema_version": 1,
        "status": "reviewed-coordinator-core-pin-proposal",
        "analysis_mode": (
            "offline; no hardware, MMIO, signing, flashing, or publishing operation"
        ),
        "source_inputs": {
            "entries": len(snapshot),
            "sha256": builder._canonical_input_report(snapshot)["sha256"],
        },
        "apple_core_stage": apple["core_stage"]["expected"],
        "linux_core_stage": linux["core_stage"]["expected"],
        "endpoint_entries_unpatched": ["0x0051B8F0", "0x0051BF7C"],
        "coordinator_entry": "0x0051C5EC",
        "coordinator_source": copy.deepcopy(SOURCE_IDENTITY),
        "hardware_operations": [],
    }
    return proposed, report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--review-observations", nargs=4, required=True, type=Path,
        metavar=("APPLE_A", "APPLE_B", "LINUX_A", "LINUX_B"),
    )
    parser.add_argument("--proposal", required=True, type=Path)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    if args.proposal.resolve() == CONFIG.resolve():
        raise SystemExit("proposal path must differ from live config")
    proposed, report = review(args.review_observations)
    payload = (json.dumps(proposed, indent=2) + "\n").encode("utf-8")
    admission.atomic_write(args.proposal, payload)
    if args.apply:
        admission.atomic_write(CONFIG, payload)
        report["status"] = "reviewed-coordinator-core-pins-installed"
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
