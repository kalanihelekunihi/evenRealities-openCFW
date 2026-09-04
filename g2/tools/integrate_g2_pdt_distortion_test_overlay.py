#!/usr/bin/env python3
"""Prepare, review, and promote the clean-room G2 distortion-test screen."""

import argparse
import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SHARED = ROOT / "tools/integrate_g2_service_time_overlay.py"
SPEC = importlib.util.spec_from_file_location(
    "g2_pdt_distortion_test_shared", SHARED
)
shared = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(shared)
base = shared.base

base.SOURCE = (
    ROOT / "components/apollo_main/core_overlay/pdt_distortion_test.c"
)
base.RECORDER = "apple-pdt-distortion-test-record"
base.LEAF_DEFINE_PREFIX = "OPEN_CFW_PDT_DISTORTION_"
base.PATCH_PREFIX = "replace_pdt_distortion_test_"
base.EVIDENCE = "docs/research/g2-pdt-distortion-test-recovery.md"
base.ORIGIN = (
    "clean-room G2 distortion-test callbacks and nested LVGL resource layout"
)
base.LICENSE = "MIT"
base.SELECTORS = (
    ("ZERO_STYLES", "open_cfw_pdt_distortion_zero_styles",
     0x005CF2B4, 0x005CF2E6),
    ("COMMON_DATA", "open_cfw_pdt_distortion_common_data_handler",
     0x005CF2E6, 0x005CF32C),
    ("PREDICATE", "open_cfw_pdt_distortion_predicate",
     0x005CF32C, 0x005CF330),
    ("SCREEN_EVENT", "open_cfw_pdt_distortion_screen_event",
     0x005CF330, 0x005CF606),
)
base.PROVIDERS = {
    "open_cfw_retained_pdt_distortion_object_create": 0x0043DE82,
    "open_cfw_retained_pdt_distortion_clear_flags": 0x0043DFA4,
    "open_cfw_retained_pdt_distortion_add_flags": 0x0043DED4,
    "open_cfw_retained_pdt_distortion_set_width": 0x0043F506,
    "open_cfw_retained_pdt_distortion_set_height": 0x0043F568,
    "open_cfw_retained_pdt_distortion_set_size": 0x0043F4C0,
    "open_cfw_retained_pdt_distortion_set_pos": 0x0043F09A,
    "open_cfw_retained_pdt_distortion_align": 0x0043F6B8,
    "open_cfw_retained_pdt_distortion_color_hex": 0x0044104C,
    "open_cfw_retained_pdt_distortion_set_style_0": 0x0044122A,
    "open_cfw_retained_pdt_distortion_set_style_1": 0x00441238,
    "open_cfw_retained_pdt_distortion_set_style_2": 0x0044120E,
    "open_cfw_retained_pdt_distortion_set_style_3": 0x0044121C,
    "open_cfw_retained_pdt_distortion_set_layout_gap_0": 0x00441246,
    "open_cfw_retained_pdt_distortion_set_layout_gap_1": 0x00441254,
    "open_cfw_retained_pdt_distortion_set_frame_style_0": 0x0044133A,
    "open_cfw_retained_pdt_distortion_set_frame_style_1": 0x00441378,
    "open_cfw_retained_pdt_distortion_set_frame_style_2": 0x00441386,
    "open_cfw_retained_pdt_distortion_set_frame_style_3": 0x004413B0,
    "open_cfw_retained_pdt_distortion_set_frame_style_4": 0x00441394,
    "open_cfw_retained_pdt_distortion_set_frame_style_5": 0x004413A2,
    "open_cfw_retained_pdt_distortion_set_bg_color": 0x0044127E,
    "open_cfw_retained_pdt_distortion_set_bg_opacity": 0x0044129E,
    "open_cfw_retained_pdt_distortion_set_border_color": 0x004412EC,
    "open_cfw_retained_pdt_distortion_set_border_opacity": 0x0044130C,
    "open_cfw_retained_pdt_distortion_set_border_width": 0x0044131C,
    "open_cfw_retained_pdt_distortion_set_shadow_color": 0x0044140E,
    "open_cfw_retained_pdt_distortion_set_shadow_opacity": 0x0044142E,
    "open_cfw_retained_pdt_distortion_set_scrollbar_mode": 0x0044146A,
    "open_cfw_retained_pdt_distortion_set_flex_flow": 0x0048BA78,
    "open_cfw_retained_pdt_distortion_set_flex_align": 0x0048BA92,
    "open_cfw_retained_pdt_distortion_image_create": 0x00498668,
    "open_cfw_retained_pdt_distortion_image_set_source": 0x00498680,
    "open_cfw_retained_pdt_distortion_label_create": 0x00499416,
    "open_cfw_retained_pdt_distortion_label_set_text": 0x0049942E,
    "open_cfw_retained_pdt_distortion_translation": 0x0045FFFE,
    "open_cfw_retained_pdt_distortion_translation_id": 0x00460084,
    "open_cfw_retained_pdt_distortion_set_text_color": 0x0044140E,
    "open_cfw_retained_pdt_distortion_set_font": 0x0044143E,
    "open_cfw_retained_pdt_distortion_set_text_align": 0x0044145A,
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

    header = (
        ROOT / "components/apollo_main/core_overlay/pdt_distortion_test.h"
    )
    relative = header.relative_to(ROOT).as_posix()
    config["sources"] = [
        item for item in config.get("sources", [])
        if item.get("path") != relative
    ]
    payload = header.read_bytes()
    config["sources"].append({
        "evidence": base.EVIDENCE,
        "license": "MIT",
        "origin": "public ABI for the clean-room G2 distortion-test screen",
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
