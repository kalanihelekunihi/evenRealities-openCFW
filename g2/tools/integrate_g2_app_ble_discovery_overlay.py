#!/usr/bin/env python3
"""Prepare and review the clean-room G2 BLE discovery-policy overlay."""

import argparse
import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SHARED = ROOT / "tools/integrate_g2_service_time_overlay.py"
SPEC = importlib.util.spec_from_file_location(
    "g2_app_ble_discovery_shared", SHARED
)
shared = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(shared)
base = shared.base

base.SOURCE = ROOT / "components/apollo_main/core_overlay/app_ble_discovery.c"
base.RECORDER = "apple-app-ble-discovery-record"
base.LEAF_DEFINE_PREFIX = "OPEN_CFW_APP_BLE_DISCOVERY_"
base.PATCH_PREFIX = "replace_app_ble_discovery_"
base.EVIDENCE = "docs/research/g2-app-ble-discovery-recovery.md"
base.ORIGIN = "clean-room G2 Cordio application BLE discovery policy"
base.LICENSE = "MIT"
base.SELECTORS = (
    (
        "START",
        "open_cfw_app_start_service_discovery",
        0x005354C2,
        0x00535598,
    ),
    (
        "CALLBACK",
        "open_cfw_app_ble_server_disc_callback",
        0x005355E0,
        0x0053609C,
    ),
)
base.PROVIDERS = {
    "open_cfw_retained_event_loop_remove_delayed": 0x00476ACE,
    "open_cfw_retained_app_ble_connection_record": 0x004BB07C,
    "open_cfw_retained_app_ble_record_state_set": 0x0047B488,
    "open_cfw_retained_app_ble_record_reset": 0x0047B3CC,
    "open_cfw_retained_app_ble_message_allocate": 0x004BF99E,
    "open_cfw_retained_app_ble_message_send": 0x004BF9BA,
    "open_cfw_retained_dm_conn_role": 0x004B73C4,
    "open_cfw_retained_app_disc_begin": 0x00532EB4,
    "open_cfw_retained_app_disc_fail": 0x005336E0,
    "open_cfw_retained_app_disc_phone_ready": 0x00503EA8,
    "open_cfw_retained_app_disc_configure": 0x004B59C0,
    "open_cfw_retained_app_disc_state_set": 0x0053303C,
    "open_cfw_retained_app_disc_service_begin": 0x00533474,
    "open_cfw_retained_app_disc_database_hash": 0x004C487C,
    "open_cfw_retained_app_disc_ancs": 0x004BF82C,
    "open_cfw_retained_app_product_signal": 0x004C543E,
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

    header = ROOT / "components/apollo_main/core_overlay/app_ble_discovery.h"
    relative = header.relative_to(ROOT).as_posix()
    config["sources"] = [
        item for item in config.get("sources", [])
        if item.get("path") != relative
    ]
    payload = header.read_bytes()
    config["sources"].append({
        "evidence": base.EVIDENCE,
        "license": "MIT",
        "origin": "public ABI for the clean-room G2 BLE discovery policy",
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
