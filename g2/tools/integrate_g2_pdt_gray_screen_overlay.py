#!/usr/bin/env python3
"""Prepare, review, and promote the clean-room G2 production gray screen."""

import argparse
import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SHARED = ROOT / "tools/integrate_g2_service_time_overlay.py"
SPEC = importlib.util.spec_from_file_location("g2_pdt_gray_screen_shared", SHARED)
shared = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(shared)
base = shared.base

base.SOURCE = ROOT / "components/apollo_main/core_overlay/pdt_gray_screen.c"
base.RECORDER = "apple-pdt-gray-screen-record"
base.LEAF_DEFINE_PREFIX = "OPEN_CFW_PDT_GRAY_"
base.PATCH_PREFIX = "replace_pdt_gray_screen_"
base.EVIDENCE = "docs/research/g2-pdt-gray-screen-recovery.md"
base.ORIGIN = "clean-room G2 production gray-screen callbacks and LVGL bands"
base.LICENSE = "MIT"
base.SELECTORS = (
    ("COMMON_DATA", "open_cfw_pdt_gray_common_data_handler",
     0x005CF634, 0x005CF67A),
    ("PREDICATE", "open_cfw_pdt_gray_predicate", 0x005CF67A, 0x005CF67E),
    ("SCREEN_EVENT", "open_cfw_pdt_gray_screen_event",
     0x005CF67E, 0x005CF788),
)
base.PROVIDERS = {
    "open_cfw_retained_pdt_gray_object_create": 0x0043DE82,
    "open_cfw_retained_pdt_gray_clear_flags": 0x0043DFA4,
    "open_cfw_retained_pdt_gray_set_width": 0x0043F506,
    "open_cfw_retained_pdt_gray_set_height": 0x0043F568,
    "open_cfw_retained_pdt_gray_set_size": 0x0043F4C0,
    "open_cfw_retained_pdt_gray_set_pos": 0x0043F09A,
    "open_cfw_retained_pdt_gray_color_hex": 0x0044104C,
    "open_cfw_retained_pdt_gray_color_make": 0x00441068,
    "open_cfw_retained_pdt_gray_set_bg_color": 0x0044127E,
    "open_cfw_retained_pdt_gray_set_bg_opacity": 0x0044129E,
    "open_cfw_retained_pdt_gray_set_border_color": 0x004412EC,
    "open_cfw_retained_pdt_gray_set_border_width": 0x0044131C,
    "open_cfw_retained_pdt_gray_set_scrollbar_mode": 0x0044146A,
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

    header = ROOT / "components/apollo_main/core_overlay/pdt_gray_screen.h"
    relative = header.relative_to(ROOT).as_posix()
    config["sources"] = [
        item for item in config.get("sources", [])
        if item.get("path") != relative
    ]
    payload = header.read_bytes()
    config["sources"].append({
        "evidence": base.EVIDENCE,
        "license": "MIT",
        "origin": "public ABI for the clean-room G2 production gray screen",
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
