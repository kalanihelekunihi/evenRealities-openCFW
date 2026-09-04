#!/usr/bin/env python3
"""Prepare, review, and promote the clean-room G2 eAT core overlay."""

import argparse
import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SHARED = ROOT / "tools/integrate_g2_service_time_overlay.py"
SPEC = importlib.util.spec_from_file_location("g2_at_core_shared", SHARED)
shared = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(shared)
base = shared.base

base.SOURCE = ROOT / "components/apollo_main/core_overlay/at_core.c"
base.RECORDER = "apple-at-core-record"
base.LEAF_DEFINE_PREFIX = "OPEN_CFW_AT_CORE_"
base.PATCH_PREFIX = "replace_at_core_"
base.EVIDENCE = "docs/research/g2-at-core-recovery.md"
base.ORIGIN = "clean-room G2 eAT callback, parser, formatter, and command-dispatch core"
base.LICENSE = "MIT"
base.SELECTORS = (
    ("REGISTER_CALLBACK", "open_cfw_at_core_register_callback",
     0x005412E0, 0x00541302),
    ("INIT", "open_cfw_at_core_init", 0x00541302, 0x0054136C),
    ("HANDLER", "open_cfw_at_core_handler", 0x0054136C, 0x00541430),
    ("OUTPUT", "open_cfw_at_core_output", 0x00541430, 0x005414BA),
    ("DISPATCH_COMMAND", "open_cfw_at_core_dispatch_command",
     0x005414BA, 0x0054157A),
)
base.PROVIDERS = {
    "open_cfw_retained_at_core_parser_init": 0x0057DDFC,
    "open_cfw_retained_at_core_parser_next": 0x0057DEB0,
    "open_cfw_retained_at_core_parser_adapt": 0x0057DE0A,
    # This stock entry is itself a guarded source redirect in the core overlay.
    "open_cfw_runtime_vsnprintf_wrapper": 0x0044B76C,
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

    header = ROOT / "components/apollo_main/core_overlay/at_core.h"
    relative = header.relative_to(ROOT).as_posix()
    config["sources"] = [
        item for item in config.get("sources", [])
        if item.get("path") != relative
    ]
    payload = header.read_bytes()
    config["sources"].append({
        "evidence": base.EVIDENCE,
        "license": "MIT",
        "origin": "public ABI for the clean-room G2 eAT core",
        "path": relative,
        "sha256": base.sha(payload),
        "size": len(payload),
    })
    base.CONFIG.write_text(json.dumps(config, indent=2) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "action", choices=("prepare", "promote", "linux-pins", "review")
    )
    parser.add_argument("--report", type=Path)
    parser.add_argument("--reports", nargs=4, type=Path)
    args = parser.parse_args()
    if args.action == "prepare":
        prepare()
    elif args.action == "promote":
        base.promote()
    elif args.action == "linux-pins":
        if args.report is None:
            raise SystemExit("linux-pins requires --report")
        shared.admit_linux(args.report)
    else:
        if args.reports is None:
            raise SystemExit("review requires four --reports")
        shared.review_observations(args.reports)


if __name__ == "__main__":
    main()
