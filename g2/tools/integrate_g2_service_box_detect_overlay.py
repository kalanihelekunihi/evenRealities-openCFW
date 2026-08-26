#!/usr/bin/env python3
"""Prepare, promote, and package the reviewed G2 box-detect closure."""

import argparse
import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE_HELPER = ROOT / "tools/integrate_g2_lvgl_font_manager_overlay.py"
SPEC = importlib.util.spec_from_file_location("g2_box_detect_integration_base", BASE_HELPER)
base = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(base)

base.SOURCE = ROOT / "components/apollo_main/core_overlay/service_box_detect.c"
base.RECORDER = "apple-box-detect-record"
base.LEAF_DEFINE_PREFIX = "OPEN_CFW_BOX_DETECT_"
base.PATCH_PREFIX = "replace_service_box_detect_"
base.EVIDENCE = "docs/research/g2-service-box-detect-dependency-boundary.md"
base.ORIGIN = (
    "clean-room G2 case-state intersection, timers, display, ring reconnect, "
    "device-manager event, and glasses-case synchronization policy"
)
base.SELECTORS = (
    ("PUBLISH_STATUS", "open_cfw_box_detect_publish_status", 0x004ABEC8, 0x004ABF86),
    ("REFRESH_DISPLAY", "open_cfw_box_detect_refresh_display", 0x004ABF86, 0x004ABFAC),
    ("SET_WEAR_OUT", "open_cfw_box_detect_set_wear_out", 0x004ABFAC, 0x004ABFBA),
    ("CLEAR_FORCE", "open_cfw_box_detect_clear_force_on_real_out", 0x004ABFBA, 0x004AC016),
    ("TIMER_FORCE_CALLBACK", "open_cfw_box_detect_timer_force_callback", 0x004AC016, 0x004AC020),
    ("TIMER_RECONNECT_CALLBACK", "open_cfw_box_detect_timer_reconnect_callback", 0x004AC020, 0x004AC02A),
    ("TIMERS_INIT", "open_cfw_box_detect_timers_init", 0x004AC02A, 0x004AC0F8),
    ("TIMERS_DEINIT", "open_cfw_box_detect_timers_deinit", 0x004AC0F8, 0x004AC130),
    ("FORCE_TIMER_EXPIRED", "open_cfw_box_detect_force_timer_expired", 0x004AC130, 0x004AC154),
    ("FORCE_TIMER_START", "open_cfw_box_detect_force_timer_start", 0x004AC154, 0x004AC16C),
    ("NOTIFY_DEVICE", "open_cfw_box_detect_notify_device", 0x004AC16C, 0x004AC19C),
    ("TRY_RECONNECT", "open_cfw_box_detect_try_reconnect", 0x004AC19C, 0x004AC278),
    ("HANDLE_EVENT", "open_cfw_box_detect_handle_event", 0x004AC278, 0x004AC59A),
    ("GET_WEAR_OUT", "open_cfw_box_detect_get_wear_out", 0x004AC59A, 0x004AC5A2),
    ("SET_FORCE_OUT", "open_cfw_box_detect_set_force_out", 0x004AC5A2, 0x004AC66A),
    ("GET_FORCE_OUT", "open_cfw_box_detect_get_force_out", 0x004AC66A, 0x004AC672),
    ("NOTIFY_FORCE_OUT", "open_cfw_box_detect_notify_force_out", 0x004AC672, 0x004AC718),
    ("SET_LOCAL_LEVEL", "open_cfw_box_detect_set_local_level", 0x004AC718, 0x004AC726),
    ("GET_LOCAL_LEVEL", "open_cfw_box_detect_get_local_level", 0x004AC726, 0x004AC72E),
    ("SET_LOCAL_CHARGING", "open_cfw_box_detect_set_local_charging", 0x004AC72E, 0x004AC73C),
    ("GET_LOCAL_CHARGING", "open_cfw_box_detect_get_local_charging", 0x004AC73C, 0x004AC744),
    ("SET_LOCAL_LID", "open_cfw_box_detect_set_local_lid", 0x004AC744, 0x004AC752),
    ("GET_LOCAL_LID", "open_cfw_box_detect_get_local_lid", 0x004AC752, 0x004AC75A),
    ("IS_OUT", "open_cfw_box_detect_is_out", 0x004AC75A, 0x004AC776),
    ("GET_LOCAL_STATE", "open_cfw_box_detect_get_local_state", 0x004AC776, 0x004AC798),
    ("STATE_UPDATED", "open_cfw_box_detect_state_updated", 0x004AC798, 0x004AC80C),
    ("SEND_STATE", "open_cfw_box_detect_send_state", 0x004AC828, 0x004AC890),
    ("PROCESS_CASE_STATE", "open_cfw_box_detect_process_case_state", 0x004AC890, 0x004ACA98),
    ("GET_EFFECTIVE_LEVEL", "open_cfw_box_detect_get_effective_level", 0x004ACAA0, 0x004ACAA8),
    ("GET_EFFECTIVE_CHARGING", "open_cfw_box_detect_get_effective_charging", 0x004ACAAC, 0x004ACAB4),
    ("GET_EFFECTIVE_LID", "open_cfw_box_detect_get_effective_lid", 0x004ACAB4, 0x004ACABC),
    ("GET_EFFECTIVE_WEAR", "open_cfw_box_detect_get_effective_wear", 0x004ACAC0, 0x004ACAC6),
    ("EFFECTIVE_OUT", "open_cfw_box_detect_effective_out", 0x004ACAD0, 0x004ACAF8),
    ("COMMON_DATA", "open_cfw_box_detect_common_data", 0x004ACB40, 0x004ACD46),
)
base.PROVIDERS = {
    "open_cfw_retained_box_detect_memcpy": 0x00439BE4,
    "open_cfw_retained_box_detect_memset": 0x0043C0E4,
    "open_cfw_retained_box_detect_timer_new": 0x004493B0,
    "open_cfw_retained_box_detect_timer_start": 0x00449498,
    "open_cfw_retained_box_detect_timer_stop": 0x004494D8,
    "open_cfw_retained_box_detect_timer_is_running": 0x00449522,
    "open_cfw_retained_box_detect_timer_delete": 0x0044953E,
    "open_cfw_retained_box_detect_display_ready": 0x00443484,
    "open_cfw_retained_box_detect_should_publish_status": 0x004487AC,
    "open_cfw_retained_box_detect_lens_side": 0x0045A568,
    "open_cfw_retained_box_detect_send_notification": 0x00464F76,
    "open_cfw_retained_box_detect_send_sync": 0x00465480,
    "open_cfw_retained_box_detect_display_is_active": 0x0046B0EC,
    "open_cfw_retained_box_detect_ring_state_changed": 0x0047243A,
    "open_cfw_retained_box_detect_display_open": 0x00474100,
    "open_cfw_retained_box_detect_display_close": 0x0047432C,
    "open_cfw_retained_box_detect_ring_reconnect": 0x004A2658,
    "open_cfw_retained_box_detect_ring_reconnect_queue": 0x004A316C,
    "open_cfw_retained_box_detect_product_mode": 0x004ABE60,
    "open_cfw_retained_box_detect_queue": 0x004C659A,
    "open_cfw_retained_box_detect_device_state": 0x0050938E,
    "open_cfw_retained_box_detect_case_request": 0x00510A0C,
    "open_cfw_retained_box_detect_case_status": 0x00510DEC,
    "open_cfw_retained_box_detect_case_interrupt": 0x00510FE2,
    "open_cfw_retained_box_detect_input_out": 0x005130A6,
}


def sync_manifest() -> None:
    manifest = json.loads(base.MANIFEST.read_text())
    report = json.loads(base.REPORT.read_text())
    run_base = json.loads(base.CONFIG.read_text())["run_base"]
    override = manifest["component_overrides"]["apollo_main"]
    provider = override["provider"]
    provider_path = ROOT / provider["path"]
    provider["size"] = provider_path.stat().st_size
    provider["sha256"] = base.sha(provider_path.read_bytes())
    override["function"] = (
        "Even Apollo510B main firmware with maintained source overlays including "
        "clean-room display, sensor, health, case-UART, and box-detect policy"
    )
    regions = [
        item for item in override["regions"]
        if not item["name"].startswith("service_box_detect_")
    ]
    stock = sorted(base.SELECTORS, key=lambda item: item[2])
    first_start, last_end = stock[0][2], stock[-1][3]
    owner_index = next(
        index for index, item in enumerate(regions)
        if item.get("address_status") == "official_blob"
        and item.get("target_address", 0) <= first_start
        and item.get("target_address", 0) + item["size"] >= last_end
    )
    owner = regions[owner_index]
    owner_start = owner["target_address"]
    owner_end = owner_start + owner["size"]
    split = []
    if owner_start < first_start:
        before = dict(owner)
        before["size"] = first_start - owner_start
        split.append(before)
    cursor = first_start
    for index, (_selector, function, start, end) in enumerate(stock, 1):
        if cursor < start:
            split.append(base.region(
                f"service_box_detect_retained_gap_{index:02d}",
                "Official box-detect literal/alignment bytes", "official_blob",
                32 + cursor - run_base, start - cursor, cursor,
                f"apollo510b/main-opaque-box-detect-gap-0x{cursor:08x}.bin",
            ))
        split.append(base.region(
            f"service_box_detect_{index:02d}_source_replacement",
            f"Generated guarded redirect replacing {function}",
            "generated_source_entry_replacement", 32 + start - run_base,
            end - start, start,
            f"apollo510b/main-generated-box-detect-{index:02d}-0x{start:08x}.bin",
        ))
        cursor = end
    if cursor < owner_end:
        split.append(base.region(
            "service_box_detect_opaque_after",
            "Official Apollo bytes after the source-replaced box-detect object",
            "official_blob", 32 + cursor - run_base, owner_end - cursor, cursor,
            f"apollo510b/main-opaque-0x{cursor:08x}.bin",
        ))
    regions[owner_index:owner_index + 1] = split
    leaves = [
        item for item in report["relocated_leaves"]
        if item.get("source", {}).get("path", "").endswith("service_box_detect.c")
    ]
    for item in leaves:
        extraction, placement = item["extraction"], item["placement"]
        function = extraction["function"]
        slug = function.removeprefix("open_cfw_box_detect_").replace("_", "-")
        if placement["padding_before"]:
            address = placement["runtime_address"] - placement["padding_before"]
            regions.append(base.region(
                f"service_box_detect_{slug}_overlay_alignment",
                f"Generated runtime alignment before {function}",
                "generated_alignment", 32 + address - run_base,
                placement["padding_before"], address,
                f"apollo510b/main-source-box-detect-{slug}-alignment.bin",
            ))
        regions.append(base.region(
            f"service_box_detect_{slug}_source_text",
            f"Clean-room box-detect leaf ({function}) compiled from C",
            "source_compiled", 32 + placement["runtime_address"] - run_base,
            extraction["size"], placement["runtime_address"],
            f"apollo510b/main-source-box-detect-{slug}-0x{placement['runtime_address']:08x}.bin",
        ))
    regions.sort(key=lambda item: item["file_offset"])
    final = max(item["file_offset"] + item["size"] for item in regions)
    if final != provider["size"]:
        raise SystemExit(
            f"manifest tiling ends at {final}, provider has {provider['size']} bytes"
        )
    override["regions"] = regions
    manifest["package"]["expected_size"] = None
    manifest["package"]["expected_sha256"] = None
    base.MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "action", choices=("prepare", "promote", "sync-manifest", "pin-package")
    )
    action = parser.parse_args().action
    if action == "prepare":
        base.prepare()
    elif action == "promote":
        base.promote()
    elif action == "sync-manifest":
        sync_manifest()
    else:
        base.pin_package()


if __name__ == "__main__":
    main()
