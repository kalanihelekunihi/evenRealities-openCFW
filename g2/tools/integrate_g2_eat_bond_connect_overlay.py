#!/usr/bin/env python3
"""Prepare and review the clean-room G2 eAT bond/connect overlay."""

import argparse
import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SHARED = ROOT / "tools/integrate_g2_service_time_overlay.py"
SPEC = importlib.util.spec_from_file_location("g2_eat_bond_connect_shared", SHARED)
shared = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(shared)
base = shared.base

base.SOURCE = ROOT / "components/apollo_main/core_overlay/eat_bond_connect.c"
base.RECORDER = "apple-eat-bond-connect-record"
base.LEAF_DEFINE_PREFIX = "OPEN_CFW_EAT_"
base.PATCH_PREFIX = "replace_eat_bond_connect_"
base.EVIDENCE = "docs/research/g2-eat-bond-connect-recovery.md"
base.ORIGIN = "clean-room G2 eAT bond-clean and keep-connect command handlers"
base.LICENSE = "MIT"
base.SELECTORS = (
    ("CLEAN_BOND", "open_cfw_eat_clean_bond_handler",
     0x005A4FA4, 0x005A4FB4),
    ("KEEP_CONNECT", "open_cfw_eat_keep_connect_handler",
     0x005A4FB4, 0x005A4FC6),
)
base.PROVIDERS = {
    "open_cfw_retained_eat_clean_bond": 0x004B46CE,
    "open_cfw_retained_eat_keep_connect": 0x0046F2DC,
    "open_cfw_retained_eat_output": 0x00541430,
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
                leaf["profiles"] = [
                    profile for profile in allowed if profile != base.RECORDER
                ]
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
            site["profiles"] = [
                profile for profile in allowed if profile != base.RECORDER
            ]
        if site.get("name", "").startswith(base.PATCH_PREFIX):
            site["profiles"] = ["apple-clang", "linux-clang"]

    header = ROOT / "components/apollo_main/core_overlay/eat_bond_connect.h"
    relative = header.relative_to(ROOT).as_posix()
    config["sources"] = [
        item for item in config.get("sources", [])
        if item.get("path") != relative
    ]
    payload = header.read_bytes()
    config["sources"].append({
        "evidence": base.EVIDENCE,
        "license": "MIT",
        "origin": "public ABI for the clean-room G2 eAT bond/connect pair",
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
