#!/usr/bin/env python3
"""Prepare and review the dual-profile G2 AT^NUS source overlay."""

# SPDX-License-Identifier: MIT

from __future__ import annotations

import argparse
import copy
import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SHARED = ROOT / "tools/integrate_g2_service_time_overlay.py"
SPEC = importlib.util.spec_from_file_location("g2_at_nus_shared", SHARED)
shared = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(shared)
base = shared.base

base.SOURCE = ROOT / "components/apollo_main/core_overlay/at_nus.c"
base.RECORDER = "apple-at-nus-record"
base.LEAF_DEFINE_PREFIX = "OPEN_CFW_AT_NUS_"
base.PATCH_PREFIX = "replace_at_nus_"
base.EVIDENCE = "docs/research/g2-at-nus-recovery.md"
base.ORIGIN = "clean-room pathless G2 AT^NUS command handler"
base.LICENSE = "MIT"
base.SELECTORS = (
    ("HANDLER", "open_cfw_at_nus_handler", 0x005A5520, 0x005A5530),
)
base.PROVIDERS = {
    "open_cfw_retained_at_nus_output": 0x00541430,
}
APPLE_FUNCTION = "open_cfw_at_nus_handler"
LINUX_FUNCTION = "open_cfw_at_nus_handler_linux"


def prepare() -> None:
    """Keep Apple placement and append a profile-disjoint Linux leaf."""
    config = json.loads(base.CONFIG.read_text())
    leaves = [
        leaf for leaf in config.get("relocated_leaves", [])
        if leaf.get("function") in {APPLE_FUNCTION, LINUX_FUNCTION}
    ]
    if len(leaves) == 2 and all(
        leaf.get("function") == APPLE_FUNCTION for leaf in leaves
    ):
        apple = next(
            leaf for leaf in leaves if leaf.get("profiles") == ["apple-clang"]
        )
        linux = next(
            leaf for leaf in leaves if leaf.get("profiles") == ["linux-clang"]
        )
    elif len(leaves) == 1:
        apple = leaves[0]
        linux = copy.deepcopy(apple)
        apple["profiles"] = ["apple-clang"]
        linux["profiles"] = ["linux-clang"]
        config["relocated_leaves"].append(linux)
        leaves = [apple, linux]
    elif len(leaves) == 2:
        apple = next(
            leaf for leaf in leaves if leaf.get("function") == APPLE_FUNCTION
        )
        linux = next(
            leaf for leaf in leaves if leaf.get("function") == LINUX_FUNCTION
        )
    else:
        raise SystemExit("expected profile-disjoint Apple/Linux AT^NUS leaves")
    source_payload = base.SOURCE.read_bytes()
    source_sha256 = base.sha(source_payload)
    linux_changed = (
        linux.get("function") != LINUX_FUNCTION
        or linux.get("source", {}).get("sha256") != source_sha256
    )
    apple["function"] = APPLE_FUNCTION
    apple["profiles"] = ["apple-clang"]
    linux["function"] = LINUX_FUNCTION
    linux["profiles"] = ["linux-clang"]
    if linux_changed:
        linux["expected"] = {
            "size": apple["expected"]["size"],
            "sha256": "0" * 64,
            "alignment": apple["expected"]["alignment"],
            "offset": config["toolchain_profiles"]["linux-clang"]
            ["expected"]["overlay_size"],
            "unrelocated_sha256": apple["expected"]["unrelocated_sha256"],
        }
    for leaf in (apple, linux):
        leaf["strict_relocation_contract"] = True
        leaf["source"]["sha256"] = source_sha256
        leaf["source"]["size"] = len(source_payload)
    linux_flags = [
        flag for flag in linux["toolchain"]["flags"]
        if not flag.startswith("-DOPEN_CFW_AT_NUS_HANDLER_NAME=")
    ]
    linux_flags.append(
        "-DOPEN_CFW_AT_NUS_HANDLER_NAME=open_cfw_at_nus_handler_linux"
    )
    linux["toolchain"]["flags"] = linux_flags
    functions = config.setdefault("functions", [])
    if LINUX_FUNCTION not in functions:
        functions.append(LINUX_FUNCTION)
    sites = [
        (index, site) for index, site in enumerate(config.get("patch_sites", []))
        if site.get("name", "").startswith("replace_at_nus")
    ]
    if len(sites) == 1:
        index, apple_site = sites[0]
        linux_site = copy.deepcopy(apple_site)
        config["patch_sites"].insert(index + 1, linux_site)
    elif len(sites) == 2:
        apple_site = next(
            site for _index, site in sites
            if site.get("profiles") == ["apple-clang"]
            or site.get("target_function") == APPLE_FUNCTION
        )
        linux_site = next(site for _index, site in sites if site is not apple_site)
    else:
        raise SystemExit("expected one or two established AT^NUS redirects")
    apple_site["name"] = "replace_at_nus_handler_apple"
    apple_site["profiles"] = ["apple-clang"]
    apple_site["target_function"] = APPLE_FUNCTION
    linux_site["name"] = "replace_at_nus_handler_linux"
    linux_site["profiles"] = ["linux-clang"]
    linux_site["target_function"] = LINUX_FUNCTION
    base.CONFIG.write_text(json.dumps(config, indent=2) + "\n")


def review_observations(paths: list[Path]) -> None:
    admission = shared.admission
    apple_pair = admission.admit_reproducible_pair(paths[:2], "apple-clang")
    linux_pair = admission.admit_reproducible_pair(paths[2:], "linux-clang")
    admission.validate_observation_independence((*apple_pair, *linux_pair))
    admission.validate_generation(apple_pair[0], linux_pair[0])
    observations = {
        "apple-clang": apple_pair[0]["observation"],
        "linux-clang": linux_pair[0]["observation"],
    }
    config = json.loads(base.CONFIG.read_text())
    leaves = [
        leaf for leaf in config.get("relocated_leaves", [])
        if leaf.get("function") in {APPLE_FUNCTION, LINUX_FUNCTION}
    ]
    if len(leaves) != 2:
        raise SystemExit("AT^NUS profile-disjoint leaf set is incomplete")
    for profile, observation in observations.items():
        function = APPLE_FUNCTION if profile == "apple-clang" else LINUX_FUNCTION
        rows = admission._indexed_leaves(
            observation["core_stage"], "relocated_leaves"
        )
        if function not in rows:
            raise SystemExit(f"{profile} AT^NUS observation is incomplete")
        matches = [leaf for leaf in leaves if leaf.get("profiles") == [profile]]
        if len(matches) != 1:
            raise SystemExit(f"{profile} AT^NUS config leaf is ambiguous")
        pins = copy.deepcopy(rows[function]["pins"])
        matches[0]["relocations"] = pins.pop("relocations")
        matches[0]["expected"] = pins
        if profile == "apple-clang":
            config["core_stage_expected"] = copy.deepcopy(
                observation["core_stage"]["expected"]
            )
        else:
            config["toolchain_profiles"][profile]["core_stage_expected"] = (
                copy.deepcopy(observation["core_stage"]["expected"])
            )
        provider = config["post_link_providers"]["liblc3_ltpf"]["profiles"][
            profile
        ]
        liblc3 = observation["liblc3_ltpf"]
        provider["overlay"] = {
            "size": liblc3["payload_size"],
            "sha256": liblc3["payload_sha256"],
        }
        provider["component"] = {
            "size": liblc3["component_size"],
            "sha256": liblc3["component_sha256"],
        }
    for profile, observation in observations.items():
        admission._require_reviewed_core_leaf_pins(config, profile, observation)
        admission.update_profile_pins(config, profile, observation)
    admission.atomic_write(
        base.CONFIG, (json.dumps(config, indent=2) + "\n").encode()
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=("prepare", "review"))
    parser.add_argument("--reports", nargs=4, type=Path)
    args = parser.parse_args()
    if args.action == "prepare":
        prepare()
        return
    if args.reports is None:
        raise SystemExit("review requires four --reports")
    review_observations(args.reports)


if __name__ == "__main__":
    main()
