#!/usr/bin/env python3
"""Promote the reviewed eleven-function G2 Cordio WSF timer candidate."""

import argparse
import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HELPER = ROOT / "tools/integrate_g2_lvgl_font_manager_overlay.py"
SPEC = importlib.util.spec_from_file_location("g2_wsf_timer_integration_base", HELPER)
base = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(base)

base.SOURCE = ROOT / "components/shared/cordio/runtime_cordio_wsf_timer_candidate.c"
base.RECORDER = "apple-cordio-wsf-timer-record"
base.LEAF_DEFINE_PREFIX = "OPEN_CFW_WSF_TIMER_"
base.PATCH_PREFIX = "replace_cordio_wsf_timer_"
base.EVIDENCE = "docs/research/cordio-wsf-timer-source-recovery.md"
base.ORIGIN = (
    "clean-room G2 Cordio/Ambiq FreeRTOS WSF timer implementation over the "
    "authenticated AmbiqSuite 2.5.1 behavior family and retained WSF/RTOS ABIs"
)
base.FLAGS = [*base.FLAGS, "-DOPEN_CFW_WSF_TIMER_PRODUCTION=1"]
base.INCLUDE_DIRS = ["components/shared/cordio"]
base.SELECTORS = (
    ("REMOVE", "open_cfw_cordio_wsf_timer_remove_candidate", 0x0052A3FC, 0x0052A424),
    ("INSERT", "open_cfw_cordio_wsf_timer_insert_candidate", 0x0052A424, 0x0052A468),
    ("CALLBACK", "open_cfw_cordio_wsf_timer_callback_candidate", 0x0052A468, 0x0052A474),
    ("INIT", "open_cfw_cordio_wsf_timer_init_candidate", 0x0052A474, 0x0052A4B8),
    ("START_SEC", "open_cfw_cordio_wsf_timer_start_sec_candidate", 0x0052A4B8, 0x0052A4C4),
    ("START_MS", "open_cfw_cordio_wsf_timer_start_ms_candidate", 0x0052A4C4, 0x0052A4D2),
    ("STOP", "open_cfw_cordio_wsf_timer_stop_candidate", 0x0052A4D2, 0x0052A4E6),
    ("UPDATE", "open_cfw_cordio_wsf_timer_update_candidate", 0x0052A4E6, 0x0052A51A),
    ("NEXT", "open_cfw_cordio_wsf_timer_next_expiration_candidate", 0x0052A51A, 0x0052A542),
    ("EXPIRED", "open_cfw_cordio_wsf_timer_service_expired_candidate", 0x0052A542, 0x0052A574),
    ("UPDATE_TICKS", "open_cfw_cordio_wsf_timer_update_ticks_candidate", 0x0052A574, 0x0052A614),
)
base.PROVIDERS = {
    "open_cfw_cordio_wsf_timer_queue_candidate": 0x200741B0,
    "open_cfw_cordio_wsf_freertos_timer_candidate": 0x20074EF4,
    "open_cfw_cordio_wsf_last_tick_candidate": 0x20074EF8,
    "open_cfw_cordio_wsf_queue_remove_candidate": 0x00538CC8,
    "open_cfw_cordio_wsf_queue_insert_candidate": 0x00538C8C,
    "open_cfw_cordio_wsf_task_lock_candidate": 0x0052B8C8,
    "open_cfw_cordio_wsf_task_unlock_candidate": 0x0052B8D0,
    "open_cfw_cordio_wsf_task_set_ready_candidate": 0x0052B95E,
    "open_cfw_cordio_wsf_tick_counter_get_candidate": 0x00454EFE,
    "open_cfw_cordio_wsf_timer_create_candidate": 0x0047E6DC,
    "open_cfw_cordio_wsf_timer_command_candidate": 0x0047E7B0,
    "open_cfw_cordio_wsf_timer_fatal_candidate": 0x005FA0A4,
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
        "clean-room display, sensor, health, RTOS, case-UART, and Cordio WSF timer policy"
    )
    regions = [
        item for item in override["regions"]
        if not item["name"].startswith("cordio_wsf_timer_")
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
                f"cordio_wsf_timer_retained_gap_{index:02d}",
                "Official WSF timer compatibility bytes", "official_blob",
                32 + cursor - run_base, start - cursor, cursor,
                f"apollo510b/main-opaque-wsf-timer-gap-0x{cursor:08x}.bin",
            ))
        split.append(base.region(
            f"cordio_wsf_timer_{index:02d}_source_replacement",
            f"Generated guarded redirect replacing {function}",
            "generated_source_entry_replacement", 32 + start - run_base,
            end - start, start,
            f"apollo510b/main-generated-wsf-timer-{index:02d}-0x{start:08x}.bin",
        ))
        cursor = end
    if cursor < owner_end:
        split.append(base.region(
            "opaque_after_cordio_wsf_timer",
            "Official Apollo bytes after the source-replaced Cordio WSF timer",
            "official_blob", 32 + cursor - run_base, owner_end - cursor, cursor,
            f"apollo510b/main-opaque-0x{cursor:08x}.bin",
        ))
    regions[owner_index:owner_index + 1] = split

    leaves = [
        item for item in report["relocated_leaves"]
        if item.get("source", {}).get("path", "").endswith(
            "runtime_cordio_wsf_timer_candidate.c"
        )
    ]
    for item in leaves:
        extraction, placement = item["extraction"], item["placement"]
        function = extraction["function"]
        slug = function.removeprefix("open_cfw_cordio_wsf_timer_").removesuffix(
            "_candidate"
        ).replace("_", "-")
        if placement["padding_before"]:
            address = placement["runtime_address"] - placement["padding_before"]
            regions.append(base.region(
                f"cordio_wsf_timer_{slug}_overlay_alignment",
                f"Generated runtime alignment before {function}",
                "generated_alignment", 32 + address - run_base,
                placement["padding_before"], address,
                f"apollo510b/main-source-wsf-timer-{slug}-alignment.bin",
            ))
        regions.append(base.region(
            f"cordio_wsf_timer_{slug}_source_text",
            f"Clean-room Cordio WSF timer leaf ({function}) compiled from C",
            "source_compiled", 32 + placement["runtime_address"] - run_base,
            extraction["size"], placement["runtime_address"],
            f"apollo510b/main-source-wsf-timer-{slug}-0x{placement['runtime_address']:08x}.bin",
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
