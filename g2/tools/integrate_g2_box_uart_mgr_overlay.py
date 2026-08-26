#!/usr/bin/env python3
"""Prepare, promote, and package the reviewed G2 case-UART manager closure."""

import argparse
import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE_HELPER = ROOT / "tools/integrate_g2_lvgl_font_manager_overlay.py"
SPEC = importlib.util.spec_from_file_location("g2_box_uart_integration_base", BASE_HELPER)
base = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(base)

base.SOURCE = ROOT / "components/apollo_main/core_overlay/box_uart_mgr.c"
base.RECORDER = "apple-box-uart-record"
base.LEAF_DEFINE_PREFIX = "OPEN_CFW_BOX_UART_"
base.PATCH_PREFIX = "replace_box_uart_mgr_"
base.EVIDENCE = "docs/research/g2-box-uart-mgr-recovery.md"
base.ORIGIN = (
    "clean-room G2 case-UART framing, receive rotation, channel lifecycle, "
    "and product-test dispatch over retained UART and device-manager ABIs"
)
base.SELECTORS = (
    ("UNPACK", "open_cfw_box_uart_unpack", 0x00539E94, 0x0053A010),
    ("SEND", "open_cfw_box_uart_send", 0x0053A010, 0x0053A01C),
    ("RECEIVE", "open_cfw_box_uart_receive", 0x0053A01C, 0x0053A09C),
    ("INIT", "open_cfw_box_uart_init", 0x0053A09C, 0x0053A0B6),
    ("HANDLE", "open_cfw_box_uart_handle", 0x0053A0B6, 0x0053A3A4),
)
base.PROVIDERS = {
    "open_cfw_retained_box_uart_memcpy": 0x00439BE4,
    "open_cfw_retained_box_uart_memset": 0x0043C0E4,
    "open_cfw_retained_box_uart_queue": 0x004C659A,
    "open_cfw_retained_box_uart_register_receive": 0x0055E8F0,
    "open_cfw_retained_box_uart_resume": 0x0055E5BC,
    "open_cfw_retained_box_uart_start": 0x0055E68E,
    "open_cfw_retained_box_uart_stop": 0x0055E75A,
    "open_cfw_retained_box_uart_clear": 0x0055E90C,
    "open_cfw_retained_box_uart_flush": 0x0055E956,
    "open_cfw_retained_box_uart_product_test": 0x0056F4A0,
    "open_cfw_retained_box_uart_execute": 0x0056F92C,
    "open_cfw_retained_box_uart_delay": 0x00449376,
    "open_cfw_ui_display_sink": "open_cfw_ui_display_sink",
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
        "clean-room display, sensor, health, font, RTOS, and case-UART policy"
    )
    stock = sorted(base.SELECTORS, key=lambda item: item[2])
    first_start, last_end = stock[0][2], stock[-1][3]
    regions = [
        item for item in override["regions"]
        if not item["name"].startswith("box_uart_mgr_")
    ]
    if not any(
        item.get("address_status") == "official_blob"
        and item.get("target_address", 0) <= first_start
        and item.get("target_address", 0) + item["size"] >= last_end
        for item in regions
    ):
        regions.append(base.region(
            "box_uart_mgr_resplit_owner",
            "Official case-UART bytes before source replacement",
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
                f"box_uart_mgr_retained_gap_{index:02d}",
                "Official case-UART literal/alignment bytes", "official_blob",
                32 + cursor - run_base, start - cursor, cursor,
                f"apollo510b/main-opaque-box-uart-gap-0x{cursor:08x}.bin",
            ))
        split.append(base.region(
            f"box_uart_mgr_{index:02d}_source_replacement",
            f"Generated guarded redirect replacing {function}",
            "generated_source_entry_replacement", 32 + start - run_base,
            end - start, start,
            f"apollo510b/main-generated-box-uart-{index:02d}-0x{start:08x}.bin",
        ))
        cursor = end
    if cursor < owner_end:
        split.append(base.region(
            "opaque_after_box_uart_mgr",
            "Official Apollo bytes after the source-replaced case-UART object",
            "official_blob", 32 + cursor - run_base, owner_end - cursor, cursor,
            f"apollo510b/main-opaque-0x{cursor:08x}.bin",
        ))
    regions[owner_index:owner_index + 1] = split

    leaves = [
        item for item in report["relocated_leaves"]
        if item.get("source", {}).get("path", "").endswith("box_uart_mgr.c")
    ]
    for item in leaves:
        extraction, placement = item["extraction"], item["placement"]
        function = extraction["function"]
        slug = function.removeprefix("open_cfw_box_uart_").replace("_", "-")
        if placement["padding_before"]:
            address = placement["runtime_address"] - placement["padding_before"]
            regions.append(base.region(
                f"box_uart_mgr_{slug}_overlay_alignment",
                f"Generated runtime alignment before {function}",
                "generated_alignment", 32 + address - run_base,
                placement["padding_before"], address,
                f"apollo510b/main-source-box-uart-{slug}-alignment.bin",
            ))
        regions.append(base.region(
            f"box_uart_mgr_{slug}_source_text",
            f"Clean-room case-UART leaf ({function}) compiled from C",
            "source_compiled", 32 + placement["runtime_address"] - run_base,
            extraction["size"], placement["runtime_address"],
            f"apollo510b/main-source-box-uart-{slug}-0x{placement['runtime_address']:08x}.bin",
        ))
    regions.sort(key=lambda item: item["file_offset"])
    final = max(item["file_offset"] + item["size"] for item in regions)
    if final != provider["size"]:
        raise SystemExit(
            f"manifest tiling ends at {final}, provider has {provider['size']} bytes"
        )
    override["regions"] = regions
    # Explicit nulls override the pinned package inherited through ``extends``
    # while the new package is being assembled.  Removing these keys would
    # expose the stock base-manifest pins and fail before they can be renewed.
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
