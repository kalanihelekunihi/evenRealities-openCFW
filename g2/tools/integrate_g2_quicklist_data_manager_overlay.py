#!/usr/bin/env python3
"""Prepare and promote the clean-room Quicklist data-manager overlay."""

import argparse
import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HELPER = ROOT / "tools/integrate_g2_lvgl_font_manager_overlay.py"
SPEC = importlib.util.spec_from_file_location("g2_quicklist_overlay_base", HELPER)
base = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(base)

base.SOURCE = ROOT / "components/apollo_main/core_overlay/quicklist_data_manager.c"
base.RECORDER = "apple-quicklist-data-manager-record"
base.LEAF_DEFINE_PREFIX = "OPEN_CFW_QUICKLIST_"
base.PATCH_PREFIX = "replace_quicklist_data_manager_"
base.EVIDENCE = "docs/research/g2-quicklist-data-manager-recovery.md"
base.ORIGIN = "clean-room G2 Quicklist bounded record and packet state manager"
base.LICENSE = "MIT"
base.SELECTORS = (
    ("INITIALIZE", "open_cfw_quicklist_data_initialize", 0x0058D51C, 0x0058D668),
    ("APPEND", "open_cfw_quicklist_data_append", 0x0058D668, 0x0058D9C0),
    ("COPY", "open_cfw_quicklist_record_copy", 0x0058DA28, 0x0058DACA),
)
base.PROVIDERS = {}


def prepare() -> None:
    base.prepare()
    config = json.loads(base.CONFIG.read_text())
    for leaf in config.get("relocated_leaves", []):
        if leaf.get("function") not in {
            "open_cfw_quicklist_data_initialize",
            "open_cfw_quicklist_data_append",
        }:
            continue
        for relocation in leaf.get("relocations", []):
            if relocation.get("symbol") == "open_cfw_quicklist_record_copy":
                relocation.pop("target_function", None)
                relocation["target_address"] = 0x007EF600
    header = ROOT / "components/apollo_main/core_overlay/quicklist_data_manager.h"
    relative = header.relative_to(ROOT).as_posix()
    config["sources"] = [
        item for item in config.get("sources", []) if item.get("path") != relative
    ]
    payload = header.read_bytes()
    config["sources"].append({
        "evidence": base.EVIDENCE,
        "license": "MIT",
        "origin": "public resident-ABI types for the clean-room Quicklist manager",
        "path": relative,
        "sha256": base.sha(payload),
        "size": len(payload),
    })
    base.CONFIG.write_text(json.dumps(config, indent=2) + "\n")


def enable_linux() -> None:
    config = json.loads(base.CONFIG.read_text())
    functions = {item[1] for item in base.SELECTORS}
    for leaf in config.get("relocated_leaves", []):
        if leaf.get("function") in functions:
            profiles = leaf.setdefault("profiles", ["apple-clang"])
            if "linux-clang" not in profiles:
                profiles.append("linux-clang")
            linux_pins = {
                "open_cfw_quicklist_data_initialize": {
                    "size": 100, "sha256": "7108fa4c891849fc3ef1b1417fdcfa932acfb25434ae64a63b75d1f518f130f3",
                    "alignment": 4, "offset": 157840,
                    "unrelocated_sha256": "d4ca2e57b8a402fc3c723fa28441d7c3268ccf0fe43aada5fa9711c704b219e3",
                },
                "open_cfw_quicklist_data_append": {
                    "size": 252, "sha256": "aa8779ef1dcb2f996939535e7be96c7155adfebdf692fe59f070242c3349f087",
                    "alignment": 4, "offset": 157940,
                    "unrelocated_sha256": "54b812d8723643936aec37a487088e80d24734b617ed62bcb604736aadda9293",
                },
                "open_cfw_quicklist_record_copy": {
                    "size": 206, "sha256": "ef62621cc2e51f93403021f70a402172bdd75501c718faea68bc8aafe902fad4",
                    "alignment": 4, "offset": 158192,
                    "unrelocated_sha256": "ef62621cc2e51f93403021f70a402172bdd75501c718faea68bc8aafe902fad4",
                },
            }
            profile = leaf.setdefault("toolchain_profiles", {}).setdefault(
                "linux-clang", {}
            )
            profile["reviewed_version_prefix"] = "Homebrew clang version 22.1.8"
            profile["expected"] = linux_pins[leaf["function"]]
            if leaf["function"] == "open_cfw_quicklist_data_initialize":
                profile["relocations"] = [{
                    "offset": 54, "type": "R_ARM_THM_CALL",
                    "symbol": "open_cfw_quicklist_record_copy",
                    "symbol_type": "STT_NOTYPE", "target_address": 0x007BAD14,
                }]
            elif leaf["function"] == "open_cfw_quicklist_data_append":
                profile["relocations"] = [{
                    "offset": 160, "type": "R_ARM_THM_CALL",
                    "symbol": "open_cfw_quicklist_record_copy",
                    "symbol_type": "STT_NOTYPE", "target_address": 0x007BAD14,
                }]
            else:
                profile["relocations"] = []
    for site in config.get("patch_sites", []):
        if site.get("name", "").startswith(base.PATCH_PREFIX):
            profiles = site.setdefault("profiles", ["apple-clang"])
            if "linux-clang" not in profiles:
                profiles.append("linux-clang")
    base.CONFIG.write_text(json.dumps(config, indent=2) + "\n")


def promote() -> None:
    base.promote()
    enable_linux()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=("prepare", "promote"))
    args = parser.parse_args()
    prepare() if args.action == "prepare" else promote()


if __name__ == "__main__":
    main()
