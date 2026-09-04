#!/usr/bin/env python3
"""Prepare the clean-room G2 eAT filesystem-command overlay."""

import argparse
import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SHARED = ROOT / "tools/integrate_g2_service_time_overlay.py"
SPEC = importlib.util.spec_from_file_location("g2_at_fs_shared", SHARED)
shared = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(shared)
base = shared.base

base.SOURCE = ROOT / "components/apollo_main/core_overlay/at_fs.c"
base.RECORDER = "apple-at-fs-record"
base.LEAF_DEFINE_PREFIX = "OPEN_CFW_AT_FS_"
base.PATCH_PREFIX = "replace_at_fs_"
base.EVIDENCE = "docs/research/g2-at-fs-recovery.md"
base.ORIGIN = "clean-room G2 eAT remove, recursive list, and mkdir handlers"
base.LICENSE = "MIT"
base.SELECTORS = (
    ("REMOVE", "open_cfw_at_fs_remove", 0x005A5530, 0x005A55A0),
    ("LIST_RECURSIVE", "open_cfw_at_fs_list_recursive", 0x005A55A0, 0x005A567A),
    ("LIST", "open_cfw_at_fs_list", 0x005A567A, 0x005A56A0),
    ("MKDIR", "open_cfw_at_fs_mkdir", 0x005A56A0, 0x005A56D0),
)
base.PROVIDERS = {
    "open_cfw_retained_at_fs_memset": 0x0043C0E4,
    "open_cfw_retained_at_fs_delay": 0x00449376,
    "open_cfw_retained_at_fs_strcmp": 0x0046CACC,
    "open_cfw_retained_at_fs_open": 0x00474550,
    "open_cfw_retained_at_fs_close": 0x004745F4,
    "open_cfw_retained_at_fs_seek": 0x00474814,
    "open_cfw_retained_at_fs_tell": 0x00474870,
    "open_cfw_retained_at_fs_remove": 0x0047498C,
    "open_cfw_retained_at_fs_opendir": 0x00474B02,
    "open_cfw_retained_at_fs_readdir": 0x00474BB8,
    "open_cfw_retained_at_fs_closedir": 0x00474C66,
    "open_cfw_retained_at_fs_format": 0x004B4728,
    "open_cfw_retained_at_fs_mkdir": 0x004CFC5C,
    "open_cfw_retained_at_fs_output": 0x00541430,
    "open_cfw_retained_at_fs_append": 0x00567C80,
    "open_cfw_at_fs_list_recursive": 0x005A55A0,
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
                if leaf.get("function") == "open_cfw_at_fs_list_recursive":
                    leaf["allow_self_relocation"] = True
    for site in config.get("patch_sites", []):
        allowed = site.get("profiles")
        if isinstance(allowed, list):
            site["profiles"] = [
                profile for profile in allowed if profile != base.RECORDER
            ]
    config["patch_sites"] = [
        site for site in config.get("patch_sites", [])
        if not site.get("name", "").startswith(base.PATCH_PREFIX)
    ]

    record_source = ROOT / "components/apollo_main/core_overlay/at_fs_command_records.c"
    record_relative = record_source.relative_to(ROOT).as_posix()
    record_payload = record_source.read_bytes()
    config["in_place_data"] = [
        item for item in config.get("in_place_data", [])
        if item.get("symbol") != "open_cfw_at_fs_command_records"
    ]
    common_flags = [
        "-mthumb", "-mcpu=cortex-m55", "-O2", "-ffreestanding",
        "-fno-jump-tables", "-fomit-frame-pointer", "-fno-builtin",
        "-mno-unaligned-access", "-fno-unwind-tables",
        "-fno-asynchronous-unwind-tables", "-fropi",
        "-ffunction-sections", "-fdata-sections", "-Wall", "-Wextra",
        "-Werror", "-mllvm", "-enable-machine-outliner=never",
    ]
    config["in_place_data"].append({
        "expected": {
            "alignment": 4,
            "size": 48,
            "sha256": "c7cbc79d40993df166e0c92e556a7654b36d8c6873dd3560fac0aa68933f3e65",
        },
        "placements": [{
            "name": "at_fs_command_records",
            "runtime_address": 0x006C92B0,
            "size": 48,
            "source_offset": 0,
            "stock_sha256": "d3c96fd8597a5e40134e051efe123fdc96858afb4ea22b1f65350ba75a54f624",
        }],
        "profiles": ["apple-clang", "linux-clang"],
        "section": ".rodata.open_cfw_at_fs_command_records",
        "source": {
            "evidence": base.EVIDENCE,
            "license": "MIT",
            "origin": "clean-room profile-specific eAT command routing records",
            "path": record_relative,
            "sha256": base.sha(record_payload),
            "size": len(record_payload),
        },
        "symbol": "open_cfw_at_fs_command_records",
        "toolchain": {
            "flags": common_flags,
            "reviewed_version_prefix": "Apple clang version 21.0.0",
            "target": "thumbv7em-none-eabi",
        },
        "toolchain_profiles": {
            "linux-clang": {
                "reviewed_version_prefix": "Homebrew clang version 22.1.8",
                "flags": common_flags + [
                    "-DOPEN_CFW_AT_FS_REMOVE_ADDRESS=0x007BC6B4u",
                    "-DOPEN_CFW_AT_FS_LIST_ADDRESS=0x007BC80Cu",
                    "-DOPEN_CFW_AT_FS_MKDIR_ADDRESS=0x007BC838u",
                ],
                "expected": {
                    "alignment": 4,
                    "size": 48,
                    "sha256": "c987cd7c793a0b28d4d77605d3f0838fb2607b74a67721436506916931a6c36f",
                },
            }
        },
    })

    header = ROOT / "components/apollo_main/core_overlay/at_fs.h"
    relative = header.relative_to(ROOT).as_posix()
    config["sources"] = [
        item for item in config.get("sources", [])
        if item.get("path") != relative
    ]
    payload = header.read_bytes()
    config["sources"].append({
        "evidence": base.EVIDENCE,
        "license": "MIT",
        "origin": "public ABI for the clean-room G2 eAT filesystem handlers",
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
