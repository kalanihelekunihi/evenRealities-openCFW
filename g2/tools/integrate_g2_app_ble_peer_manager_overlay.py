#!/usr/bin/env python3
"""Prepare and review the clean-room G2 BLE peer-manager overlay."""

import argparse
import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SHARED = ROOT / "tools/integrate_g2_service_time_overlay.py"
SPEC = importlib.util.spec_from_file_location(
    "g2_app_ble_peer_manager_shared", SHARED
)
shared = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(shared)
base = shared.base

base.SOURCE = ROOT / "components/apollo_main/core_overlay/app_ble_peer_manager.c"
base.RECORDER = "apple-app-ble-peer-manager-record"
base.LEAF_DEFINE_PREFIX = "OPEN_CFW_APP_BLE_PEER_MANAGER_"
base.PATCH_PREFIX = "replace_app_ble_peer_manager_"
base.EVIDENCE = "docs/research/g2-app-ble-peer-manager-recovery.md"
base.ORIGIN = "clean-room G2 Cordio application BLE peer-manager adapter"
base.LICENSE = "MIT"
base.SELECTORS = (
    (
        "FIND",
        "open_cfw_app_ble_peer_manager_find_conn_id_by_addr",
        0x004D8F4C,
        0x004D8FF6,
    ),
    (
        "CLEAR",
        "open_cfw_app_master_sec_clear_addr",
        0x004D8FF6,
        0x004D900C,
    ),
    (
        "GET",
        "open_cfw_app_master_sec_get_addr",
        0x004D900C,
        0x004D9010,
    ),
    (
        "UNPAIR",
        "open_cfw_app_ble_master_peer_mgr_unpair_dev",
        0x004D9010,
        0x004D910A,
    ),
)
base.PROVIDERS = {
    "open_cfw_retained_dm_conn_peer_addr": 0x004B6EEA,
    "open_cfw_retained_bda_cmp": 0x004D294A,
    "open_cfw_retained_app_master_active_conn_id": 0x004A22E8,
    "open_cfw_retained_app_master_auth_mode_set": 0x004A2168,
    "open_cfw_retained_app_master_reset_retry": 0x004A2300,
    "open_cfw_retained_event_loop_remove_delayed": 0x00476ACE,
    "open_cfw_retained_app_master_set_target_addr_name": 0x004A2068,
    "open_cfw_retained_app_master_unpair_dev_event": 0x004A1F38,
    "open_cfw_retained_app_master_unpair_conn_id_event": 0x004A1FC4,
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

    header = ROOT / "components/apollo_main/core_overlay/app_ble_peer_manager.h"
    relative = header.relative_to(ROOT).as_posix()
    config["sources"] = [
        item for item in config.get("sources", [])
        if item.get("path") != relative
    ]
    payload = header.read_bytes()
    config["sources"].append({
        "evidence": base.EVIDENCE,
        "license": "MIT",
        "origin": "public ABI for the clean-room G2 BLE peer-manager adapter",
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
