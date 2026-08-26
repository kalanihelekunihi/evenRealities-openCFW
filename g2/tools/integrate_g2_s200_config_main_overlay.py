#!/usr/bin/env python3
"""Prepare, promote, and package the reviewed G2 S200 startup closure."""

import argparse
import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE_HELPER = ROOT / "tools/integrate_g2_lvgl_font_manager_overlay.py"
SPEC = importlib.util.spec_from_file_location("g2_s200_main_integration_base", BASE_HELPER)
base = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(base)

base.SOURCE = ROOT / "components/apollo_main/core_overlay/s200_config_main.c"
base.RECORDER = "apple-s200-config-main-record"
base.LEAF_DEFINE_PREFIX = "OPEN_CFW_S200_MAIN_"
base.PATCH_PREFIX = "replace_s200_config_main_"
base.EVIDENCE = "docs/research/g2-s200-config-main-recovery.md"
base.ORIGIN = (
    "clean-room G2 LVGL product widget callbacks, platform initialization, "
    "reset-reason side effects, release registration, and startup hand-off"
)
base.SELECTORS = (
    ("CLASS_EVENT", "open_cfw_s200_main_class_event", 0x005CDB46, 0x005CDB7E),
    ("INPUT_EVENT", "open_cfw_s200_main_input_event", 0x005CDBAC, 0x005CDC90),
    ("WIDGET_INIT", "open_cfw_s200_main_widget_init", 0x005CDC90, 0x005CDD0C),
    ("PLATFORM_INIT", "open_cfw_s200_main_platform_init", 0x005CDD14, 0x005CDD6C),
    ("REPORT_RESET", "open_cfw_s200_main_report_reset", 0x005CDD6C, 0x005CE01E),
    ("THREAD", "open_cfw_s200_main_thread", 0x005CE01E, 0x005CE138),
)
base.PROVIDERS = {
    "open_cfw_retained_s200_event_is_class": 0x004516F8,
    "open_cfw_retained_s200_event_code": 0x00450286,
    "open_cfw_retained_s200_parent": 0x0044DCA2,
    "open_cfw_retained_s200_value_get": 0x005CDA66,
    "open_cfw_retained_s200_value_set": 0x005CD7CC,
    "open_cfw_retained_s200_event_send": 0x00451670,
    "open_cfw_retained_s200_input_device": 0x00452EF8,
    "open_cfw_retained_s200_input_point": 0x0044E75E,
    "open_cfw_retained_s200_object_width": 0x0043FE16,
    "open_cfw_retained_s200_object_height": 0x0043FE70,
    "open_cfw_retained_s200_value_direction": 0x005CD7C0,
    "open_cfw_retained_s200_content_width": 0x0043FDDA,
    "open_cfw_retained_s200_content_height": 0x0043FD9E,
    "open_cfw_retained_s200_object_size": 0x0043F4C0,
    "open_cfw_retained_s200_layout": 0x0048BA78,
    "open_cfw_retained_s200_object_create": 0x0043DE82,
    "open_cfw_retained_s200_object_configure": 0x0044DC0A,
    "open_cfw_retained_s200_display_width": 0x0044FBE6,
    "open_cfw_retained_s200_object_align": 0x0048BA92,
    "open_cfw_retained_s200_object_mode": 0x0048BAC8,
    "open_cfw_retained_s200_object_limit": 0x0043F506,
    "open_cfw_retained_s200_reset_capture": 0x004D3554,
    "open_cfw_retained_s200_watchdog_prepare": 0x004B29D8,
    "open_cfw_retained_s200_clock_prepare": 0x0044B068,
    "open_cfw_retained_s200_clock_select": 0x0044B07E,
    "open_cfw_retained_s200_transport_prepare": 0x004C2AE8,
    "open_cfw_retained_s200_power_prepare": 0x00474EB4,
    "open_cfw_retained_s200_power_select": 0x00474F32,
    "open_cfw_retained_s200_performance_select": 0x0047F0A0,
    "open_cfw_retained_s200_runtime_prepare": 0x004842E6,
    "open_cfw_retained_s200_service_prepare": 0x0059FAE0,
    "open_cfw_retained_s200_release_register": 0x005939AE,
    "open_cfw_retained_s200_reset_status_clear": 0x004D3534,
    "open_cfw_retained_s200_delay": 0x004910F4,
    "open_cfw_retained_s200_application_prepare": 0x005BF0BC,
    "open_cfw_retained_s200_product_rtos_init": 0x0046D6B6,
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
        "clean-room system startup, display, sensor, health, and case policy"
    )
    regions = [
        item for item in override["regions"]
        if not item["name"].startswith("s200_config_main_")
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
                f"s200_config_main_retained_gap_{index:02d}",
                "Official S200 startup literal/data bytes", "official_blob",
                32 + cursor - run_base, start - cursor, cursor,
                f"apollo510b/main-opaque-s200-config-main-gap-0x{cursor:08x}.bin",
            ))
        split.append(base.region(
            f"s200_config_main_{index:02d}_source_replacement",
            f"Generated guarded redirect replacing {function}",
            "generated_source_entry_replacement", 32 + start - run_base,
            end - start, start,
            f"apollo510b/main-generated-s200-config-main-{index:02d}-0x{start:08x}.bin",
        ))
        cursor = end
    if cursor < owner_end:
        split.append(base.region(
            "opaque_after_s200_config_main",
            "Official Apollo bytes after the source-replaced S200 startup object",
            "official_blob", 32 + cursor - run_base, owner_end - cursor, cursor,
            f"apollo510b/main-opaque-0x{cursor:08x}.bin",
        ))
    regions[owner_index:owner_index + 1] = split

    leaves = [
        item for item in report["relocated_leaves"]
        if item.get("source", {}).get("path", "").endswith("s200_config_main.c")
    ]
    for item in leaves:
        extraction, placement = item["extraction"], item["placement"]
        function = extraction["function"]
        slug = function.removeprefix("open_cfw_s200_main_").replace("_", "-")
        if placement["padding_before"]:
            address = placement["runtime_address"] - placement["padding_before"]
            regions.append(base.region(
                f"s200_config_main_{slug}_overlay_alignment",
                f"Generated runtime alignment before {function}",
                "generated_alignment", 32 + address - run_base,
                placement["padding_before"], address,
                f"apollo510b/main-source-s200-config-main-{slug}-alignment.bin",
            ))
        regions.append(base.region(
            f"s200_config_main_{slug}_source_text",
            f"Clean-room S200 startup leaf ({function}) compiled from C",
            "source_compiled", 32 + placement["runtime_address"] - run_base,
            extraction["size"], placement["runtime_address"],
            f"apollo510b/main-source-s200-config-main-{slug}-0x{placement['runtime_address']:08x}.bin",
        ))
    regions.sort(key=lambda item: item["file_offset"])
    final = max(item["file_offset"] + item["size"] for item in regions)
    if final != provider["size"]:
        raise SystemExit(f"manifest tiling ends at {final}, provider has {provider['size']} bytes")
    override["regions"] = regions
    manifest["package"].pop("expected_size", None)
    manifest["package"].pop("expected_sha256", None)
    base.MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=("prepare", "promote", "sync-manifest", "pin-package"))
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
