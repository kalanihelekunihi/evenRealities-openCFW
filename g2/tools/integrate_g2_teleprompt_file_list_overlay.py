#!/usr/bin/env python3
"""Prepare and promote the clean-room G2 teleprompt file-list overlay."""

import argparse
import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HELPER = ROOT / "tools/integrate_g2_lvgl_font_manager_overlay.py"
SPEC = importlib.util.spec_from_file_location("g2_teleprompt_file_list_base", HELPER)
base = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(base)

base.SOURCE = ROOT / "components/apollo_main/core_overlay/teleprompt_file_list.c"
base.RECORDER = "apple-teleprompt-file-list-record"
base.LEAF_DEFINE_PREFIX = "OPEN_CFW_TELEPROMPT_FILE_LIST_"
base.PATCH_PREFIX = "replace_teleprompt_file_list_"
base.EVIDENCE = "docs/research/g2-teleprompt-file-list-recovery.md"
base.ORIGIN = "clean-room G2 teleprompt file-list fixed-record storage"
base.LICENSE = "MIT"
base.SELECTORS = (
    ("UPDATE", "open_cfw_teleprompt_file_list_update", 0x0058BCE0, 0x0058BD70),
    ("GET", "open_cfw_teleprompt_file_list_get", 0x0058BD70, 0x0058BD74),
    ("RESET", "open_cfw_teleprompt_file_list_reset", 0x0058BD74, 0x0058BD86),
)
base.PROVIDERS = {
    "open_cfw_teleprompt_file_list_memcpy": 0x00439BE4,
    "open_cfw_teleprompt_file_list_memset": 0x0043C0E4,
}


def prepare() -> None:
    base.prepare()
    config = json.loads(base.CONFIG.read_text())
    functions = {item[1] for item in base.SELECTORS}
    for leaf in config.get("relocated_leaves", []):
        if leaf.get("function") in functions:
            profiles = leaf.setdefault("profiles", [])
            if "linux-clang" not in profiles:
                profiles.append("linux-clang")
    for site in config.get("patch_sites", []):
        if site.get("name", "").startswith(base.PATCH_PREFIX):
            profiles = site.setdefault("profiles", [])
            if "linux-clang" not in profiles:
                profiles.append("linux-clang")

    header = ROOT / "components/apollo_main/core_overlay/teleprompt_file_list.h"
    relative = header.relative_to(ROOT).as_posix()
    config["sources"] = [
        item for item in config.get("sources", [])
        if item.get("path") != relative
    ]
    payload = header.read_bytes()
    config["sources"].append({
        "evidence": base.EVIDENCE,
        "license": "MIT",
        "origin": "public ABI for the clean-room G2 teleprompt file-list store",
        "path": relative,
        "sha256": base.sha(payload),
        "size": len(payload),
    })
    base.CONFIG.write_text(json.dumps(config, indent=2) + "\n")


def admit_linux(report_path: Path) -> None:
    config = json.loads(base.CONFIG.read_text())
    report = json.loads(report_path.read_text())
    observed = {
        item["extraction"]["function"]: item["pins"]
        for item in report.get("relocated_leaves", [])
        if item.get("source", {}).get("path")
        == "components/apollo_main/core_overlay/teleprompt_file_list.c"
    }
    expected_names = {item[1] for item in base.SELECTORS}
    if set(observed) != expected_names:
        raise SystemExit("Linux teleprompt file-list observation is incomplete")
    canonical = report.get("canonical_observation", {})
    core_expected = canonical.get("core_stage", {}).get("expected")
    liblc3 = canonical.get("liblc3_ltpf")
    if not isinstance(core_expected, dict) or not isinstance(liblc3, dict):
        raise SystemExit("Linux teleprompt file-list stage observation is absent")
    config["core_stage_expected"] = dict(config["expected"])
    config["toolchain_profiles"]["linux-clang"]["expected"] = core_expected
    config["toolchain_profiles"]["linux-clang"]["core_stage_expected"] = dict(
        core_expected
    )
    provider = config["post_link_providers"]["liblc3_ltpf"]["profiles"][
        "linux-clang"
    ]
    provider["overlay"] = {
        "size": liblc3["payload_size"], "sha256": liblc3["payload_sha256"]
    }
    provider["component"] = {
        "size": liblc3["component_size"], "sha256": liblc3["component_sha256"]
    }
    for leaf in config.get("relocated_leaves", []):
        function = leaf.get("function")
        if function not in observed:
            continue
        pins = dict(observed[function])
        relocations = pins.pop("relocations", [])
        leaf.setdefault("toolchain_profiles", {})["linux-clang"] = {
            "reviewed_version_prefix": "Homebrew clang version 22.1.8",
            "expected": pins,
            "relocations": relocations,
        }
    base.CONFIG.write_text(json.dumps(config, indent=2) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=("prepare", "promote", "linux-pins"))
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    if args.action == "prepare":
        prepare()
    elif args.action == "promote":
        base.promote()
    else:
        if args.report is None:
            raise SystemExit("linux-pins requires --report")
        admit_linux(args.report)


if __name__ == "__main__":
    main()
