#!/usr/bin/env python3
"""Prepare, promote, and package the reviewed G2 product-RTOS closure."""

import argparse
import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE_HELPER = ROOT / "tools/integrate_g2_lvgl_font_manager_overlay.py"
SPEC = importlib.util.spec_from_file_location("g2_overlay_integration_base", BASE_HELPER)
base = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(base)

base.SOURCE = ROOT / "components/apollo_main/core_overlay/product_rtos.c"
base.RECORDER = "apple-product-rtos-record"
base.LEAF_DEFINE_PREFIX = "OPEN_CFW_PRODUCT_RTOS_"
base.PATCH_PREFIX = "replace_product_rtos_"
base.EVIDENCE = "docs/research/g2-product-rtos-recovery.md"
base.ORIGIN = (
    "clean-room G2 task-vote policy and application FreeRTOS hooks over "
    "retained CMSIS-FreeRTOS, IRQ, watchdog, logging, and Apollo510 sleep ABIs"
)
base.FLAGS = [*base.FLAGS, "-DOPEN_CFW_PRODUCT_RTOS_LEAF_ONLY=1"]
base.SELECTORS = (
    ("FIND_SLOT", "open_cfw_product_rtos_find_slot", 0x0046D67C, 0x0046D69A),
    ("FIND_FREE", "open_cfw_product_rtos_find_free_slot", 0x0046D69A, 0x0046D6B6),
    ("INIT", "open_cfw_product_rtos_init", 0x0046D6B6, 0x0046D70E),
    ("ACQUIRE_HANDLE", "open_cfw_product_rtos_acquire_for_handle", 0x0046D70E, 0x0046D78C),
    ("RELEASE_HANDLE", "open_cfw_product_rtos_release_for_handle", 0x0046D78C, 0x0046D7E6),
    ("BLOCKS_SLEEP", "open_cfw_product_rtos_blocks_deep_sleep", 0x0046D7E6, 0x0046D816),
    ("ACQUIRE_CURRENT", "open_cfw_product_rtos_acquire_current", 0x0046D816, 0x0046D826),
    ("RELEASE_CURRENT", "open_cfw_product_rtos_release_current", 0x0046D826, 0x0046D836),
    ("SLEEP", "am_freertos_sleep", 0x0046D836, 0x0046D856),
    ("WAKEUP", "am_freertos_wakeup", 0x0046D856, 0x0046D85E),
    ("MALLOC_FAILED", "vApplicationMallocFailedHook", 0x0046D85E, 0x0046D868),
    ("STACK_OVERFLOW", "vApplicationStackOverflowHook", 0x0046D86C, 0x0046D878),
    ("IDLE", "vApplicationIdleHook", 0x0046D898, 0x0046D8A0),
)
base.PROVIDERS = {
    "open_cfw_retained_product_rtos_memset": 0x0043C0E4,
    "open_cfw_retained_product_rtos_irq_save_disable": 0x00473940,
    "open_cfw_retained_product_rtos_current_thread": 0x004491AA,
    "open_cfw_retained_product_rtos_sleep": 0x0044AB42,
    "open_cfw_retained_product_rtos_watchdog_feed": 0x004B29F8,
    "open_cfw_retained_product_rtos_log": 0x004733EE,
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
        "clean-room display, sensor, health, font, and product-RTOS policy"
    )
    stock = sorted(base.SELECTORS, key=lambda item: item[2])
    first_start, last_end = stock[0][2], stock[-1][3]
    regions = [
        item for item in override["regions"]
        if not item["name"].startswith("product_rtos_")
    ]
    if not any(
        item.get("address_status") == "official_blob"
        and item.get("target_address", 0) <= first_start
        and item.get("target_address", 0) + item["size"] >= last_end
        for item in regions
    ):
        regions.append(base.region(
            "product_rtos_resplit_owner",
            "Official product-RTOS bytes before source replacement",
            "official_blob", 32 + first_start - run_base,
            last_end - first_start, first_start,
            f"apollo510b/main-opaque-0x{first_start:08x}.bin",
        ))
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
                f"product_rtos_retained_gap_{index:02d}",
                "Official product-RTOS literal/alignment bytes", "official_blob",
                32 + cursor - run_base, start - cursor, cursor,
                f"apollo510b/main-opaque-product-rtos-gap-0x{cursor:08x}.bin",
            ))
        split.append(base.region(
            f"product_rtos_{index:02d}_source_replacement",
            f"Generated guarded redirect replacing {function}",
            "generated_source_entry_replacement", 32 + start - run_base,
            end - start, start,
            f"apollo510b/main-generated-product-rtos-{index:02d}-0x{start:08x}.bin",
        ))
        cursor = end
    if cursor < owner_end:
        split.append(base.region(
            "opaque_after_product_rtos",
            "Official Apollo bytes after the source-replaced product RTOS object",
            "official_blob", 32 + cursor - run_base, owner_end - cursor, cursor,
            f"apollo510b/main-opaque-0x{cursor:08x}.bin",
        ))
    regions[owner_index:owner_index + 1] = split

    leaves = [
        item for item in report["relocated_leaves"]
        if item.get("source", {}).get("path", "").endswith("product_rtos.c")
    ]
    for item in leaves:
        extraction, placement = item["extraction"], item["placement"]
        function = extraction["function"]
        slug = function.removeprefix("open_cfw_product_rtos_").replace("_", "-")
        if placement["padding_before"]:
            address = placement["runtime_address"] - placement["padding_before"]
            regions.append(base.region(
                f"product_rtos_{slug}_overlay_alignment",
                f"Generated runtime alignment before {function}",
                "generated_alignment", 32 + address - run_base,
                placement["padding_before"], address,
                f"apollo510b/main-source-product-rtos-{slug}-alignment.bin",
            ))
        regions.append(base.region(
            f"product_rtos_{slug}_source_text",
            f"Clean-room product-RTOS leaf ({function}) compiled from C",
            "source_compiled", 32 + placement["runtime_address"] - run_base,
            extraction["size"], placement["runtime_address"],
            f"apollo510b/main-source-product-rtos-{slug}-0x{placement['runtime_address']:08x}.bin",
        ))
    regions.sort(key=lambda item: item["file_offset"])
    final = max(item["file_offset"] + item["size"] for item in regions)
    if final != provider["size"]:
        raise SystemExit(
            f"manifest tiling ends at {final}, provider has {provider['size']} bytes"
        )
    override["regions"] = regions
    manifest["package"].pop("expected_size", None)
    manifest["package"].pop("expected_sha256", None)
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
