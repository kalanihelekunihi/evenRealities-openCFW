#!/usr/bin/env python3
"""Prepare and review the clean-room S200 board-config initializer overlay."""

import argparse
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SHARED = ROOT / "tools/integrate_g2_service_time_overlay.py"
SPEC = importlib.util.spec_from_file_location("g2_s200_board_config_shared", SHARED)
shared = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(shared)
base = shared.base

base.SOURCE = ROOT / "components/apollo_main/core_overlay/s200_board_config.c"
base.RECORDER = "apple-s200-board-config-record"
base.LEAF_DEFINE_PREFIX = "OPEN_CFW_S200_BOARD_CONFIG_"
base.PATCH_PREFIX = "replace_s200_board_config_"
base.EVIDENCE = "docs/research/g2-s200-board-config-recovery.md"
base.ORIGIN = "clean-room S200 board-dependent charger initialization policy"
base.LICENSE = "MIT"
base.SELECTORS = (
    ("INIT", "open_cfw_s200_board_config_initialize", 0x005093D4, 0x00509446),
)
base.PROVIDERS = {
    "open_cfw_retained_s200_board_config_record": 0x0050938E,
    "open_cfw_retained_s200_board_config_npmx_init": 0x00512644,
    # Calls stay at the released entry addresses.  Those entries are already
    # guarded redirects to their source-owned charger implementations, and
    # using the stable ingress avoids profile-dependent overlay ordering.
    "open_cfw_bq25180_hardware_init": 0x0053AE7E,
    "open_cfw_bq27427_hardware_init": 0x0053C0FE,
}


def prepare() -> None:
    base.prepare()
    config = json.loads(base.CONFIG.read_text())
    config.get("toolchain_profiles", {}).pop(base.RECORDER, None)
    functions = {item[1] for item in base.SELECTORS}
    for key in ("isolated_leaves", "relocated_leaves", "in_place_leaves"):
        for leaf in config.get(key, []):
            allowed = leaf.get("profiles")
            if isinstance(allowed, list):
                leaf["profiles"] = [p for p in allowed if p != base.RECORDER]
            profiles = leaf.get("toolchain_profiles")
            if isinstance(profiles, dict):
                profiles.pop(base.RECORDER, None)
                if not profiles:
                    leaf.pop("toolchain_profiles", None)
            if leaf.get("function") in functions:
                leaf["profiles"] = ["apple-clang", "linux-clang"]
    for site in config.get("patch_sites", []):
        allowed = site.get("profiles")
        if isinstance(allowed, list):
            site["profiles"] = [p for p in allowed if p != base.RECORDER]
        if site.get("name", "").startswith(base.PATCH_PREFIX):
            site["profiles"] = ["apple-clang", "linux-clang"]

    header = ROOT / "components/apollo_main/core_overlay/s200_board_config.h"
    relative = header.relative_to(ROOT).as_posix()
    config["sources"] = [
        item for item in config.get("sources", []) if item.get("path") != relative
    ]
    payload = header.read_bytes()
    config["sources"].append({
        "evidence": base.EVIDENCE,
        "license": "MIT",
        "origin": "public ABI for the S200 board configuration policy",
        "path": relative,
        "sha256": base.sha(payload),
        "size": len(payload),
    })
    base.CONFIG.write_text(json.dumps(config, indent=2) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=("prepare", "review"))
    parser.add_argument("--reports", nargs=4, type=Path)
    args = parser.parse_args()
    if args.action == "prepare":
        prepare()
    else:
        if args.reports is None:
            raise SystemExit("review requires four --reports")
        shared.review_observations(args.reports)


if __name__ == "__main__":
    main()
