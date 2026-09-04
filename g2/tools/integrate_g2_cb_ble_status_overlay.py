#!/usr/bin/env python3
"""Prepare the clean-room G2 BLE-status callback facade for admission."""

import argparse
import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HELPER = ROOT / "tools/integrate_g2_lvgl_font_manager_overlay.py"
SPEC = importlib.util.spec_from_file_location("g2_cb_ble_status_base", HELPER)
base = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(base)

base.SOURCE = ROOT / "components/apollo_main/core_overlay/cb_ble_status.c"
base.RECORDER = "apple-cb-ble-status-record"
base.LEAF_DEFINE_PREFIX = "OPEN_CFW_CB_BLE_STATUS_"
base.PATCH_PREFIX = "replace_cb_ble_status_"
base.EVIDENCE = "docs/research/g2-cb-ble-status-recovery.md"
base.ORIGIN = (
    "clean-room G2 BLE-status facade over the source-owned generic callback "
    "manager ABI"
)
base.LICENSE = "MIT"
base.SELECTORS = (
    ("REGISTER", "open_cfw_cb_ble_status_register", 0x004ABCC6, 0x004ABD14),
    ("UNREGISTER", "open_cfw_cb_ble_status_unregister", 0x004ABD14, 0x004ABD60),
    ("NOTIFY", "open_cfw_cb_ble_status_notify", 0x004ABD60, 0x004ABD6E),
)
base.PROVIDERS = {
    "open_cfw_callback_mgr_register": 0x00510240,
    "open_cfw_callback_mgr_unregister": 0x005103C4,
    "open_cfw_callback_mgr_notify": 0x005105BC,
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

    header = ROOT / "components/apollo_main/core_overlay/cb_ble_status.h"
    relative = header.relative_to(ROOT).as_posix()
    config["sources"] = [
        item for item in config.get("sources", [])
        if item.get("path") != relative
    ]
    payload = header.read_bytes()
    config["sources"].append({
        "evidence": base.EVIDENCE,
        "license": "MIT",
        "origin": "public interface for the clean-room G2 BLE-status facade",
        "path": relative,
        "sha256": base.sha(payload),
        "size": len(payload),
    })
    base.CONFIG.write_text(json.dumps(config, indent=2) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=("prepare",))
    parser.parse_args()
    prepare()


if __name__ == "__main__":
    main()
