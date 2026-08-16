#!/usr/bin/env python3
"""Verify pinned openR1 vendor source trees without modifying them."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess


HERE = Path(__file__).resolve().parent
MANIFEST = json.loads((HERE / "manifest.json").read_text())
CMSIS_FREERTOS = HERE.parents[1] / "g2" / "third_party" / "cmsis-freertos"
CMBACKTRACE = HERE.parents[1] / "g2" / "third_party" / "cmbacktrace"
FREERTOS_KERNEL = HERE.parents[1] / "g2" / "third_party" / "freertos-kernel"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def component(identifier: str) -> dict[str, object]:
    return next(item for item in MANIFEST["components"] if item["id"] == identifier)


def require_text(path: Path, marker: str) -> None:
    if not path.is_file() or marker not in path.read_text(errors="strict"):
        raise AssertionError(f"missing {marker!r} in {path}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sdk-root", type=Path, required=True)
    parser.add_argument("--flashdb-root", type=Path, required=True)
    parser.add_argument("--bma456-root", type=Path, required=True)
    parser.add_argument("--lis2dw12-root", type=Path, required=True)
    parser.add_argument("--st25dvxxkc-root", type=Path, required=True)
    parser.add_argument("--tiny-aes-root", type=Path, required=True)
    parser.add_argument("--iqs7211e-root", type=Path, required=True)
    parser.add_argument("--azoteq-settings-root", type=Path, required=True)
    parser.add_argument("--goodix-democode-root", type=Path, required=False)
    args = parser.parse_args()

    sdk = args.sdk_root.resolve()
    flashdb = args.flashdb_root.resolve()
    bma456 = args.bma456_root.resolve()
    lis2dw12 = args.lis2dw12_root.resolve()
    st25dvxxkc = args.st25dvxxkc_root.resolve()
    tiny_aes = args.tiny_aes_root.resolve()
    iqs7211e = args.iqs7211e_root.resolve()
    azoteq_settings = args.azoteq_settings_root.resolve()
    softdevice = component("nordic-s140")
    softdevice_path = sdk / str(softdevice["path"])
    if sha256(softdevice_path) != softdevice["sha256"]:
        raise AssertionError("S140 7.2.0 image hash mismatch")
    require_text(sdk / "external/freertos/portable/GCC/nrf52/port.c", "FreeRTOS Kernel V10.0.0")
    require_text(FREERTOS_KERNEL / "timers.c", "FreeRTOS Kernel V10.5.1")
    require_text(FREERTOS_KERNEL / "timers.c", "static void prvReloadTimer")
    subprocess.run(["python3", str(FREERTOS_KERNEL / "verify_snapshot.py")], check=True)
    require_text(sdk / "components/softdevice/s140/headers/nrf_soc.h", "SVCALL")
    require_text(sdk / "components/ble/nrf_ble_gatt/nrf_ble_gatt.c", "nrf_ble_gatt_init")

    segger_rtt = component("segger-rtt")
    segger_rtt_source = sdk / str(segger_rtt["path"]) / "SEGGER_RTT.c"
    if sha256(segger_rtt_source) != segger_rtt["source_sha256"]:
        raise AssertionError("SEGGER RTT source hash mismatch")
    require_text(segger_rtt_source, "RTT version: 6.18a")
    require_text(sdk / str(segger_rtt["license_path"]), "freely redistributed")

    segger_fprintf = component("segger-fprintf")
    segger_fprintf_root = sdk / str(segger_fprintf["path"])
    if sha256(segger_fprintf_root / "nrf_fprintf_format.c") != \
            segger_fprintf["format_source_sha256"]:
        raise AssertionError("SEGGER printf formatter source hash mismatch")
    if sha256(segger_fprintf_root / "nrf_fprintf.c") != \
            segger_fprintf["nordic_wrapper_sha256"]:
        raise AssertionError("Nordic printf wrapper source hash mismatch")
    require_text(segger_fprintf_root / "nrf_fprintf_format.c", "RTT version: 6.14d")

    wrapper = component("arm-cmsis-freertos")
    if wrapper["commit"] != "d213f261b5be6bb29a7cce8b84071706b72f4d53":
        raise AssertionError("CMSIS-FreeRTOS commit pin changed")
    require_text(CMSIS_FREERTOS / "README.openCFW.md", "CMSIS-FreeRTOS v10.5.1")
    wrapper_source = (
        CMSIS_FREERTOS / "CMSIS-FreeRTOS/CMSIS/RTOS2/FreeRTOS/Source/cmsis_os2.c"
    )
    if sha256(wrapper_source) != wrapper["source_sha256"]:
        raise AssertionError("CMSIS-FreeRTOS wrapper source hash mismatch")
    require_text(wrapper_source, "xEventGroupGetBitsFromISR")
    require_text(wrapper_source, "rflags |= flags")
    require_text(CMSIS_FREERTOS / "CMSIS_5/LICENSE.txt", "Apache License")

    cmbacktrace = component("cmbacktrace")
    if cmbacktrace["commit"] != "73714489f9d8af130aacb515586b397b604a5768":
        raise AssertionError("CmBacktrace compatibility snapshot pin changed")
    if sha256(CMBACKTRACE / "cm_backtrace/cm_backtrace.c") != \
            cmbacktrace["source_sha256"]:
        raise AssertionError("CmBacktrace source hash mismatch")
    require_text(CMBACKTRACE / "LICENSE", "Permission is hereby granted")
    subprocess.run(["python3", str(CMBACKTRACE / "verify_snapshot.py")], check=True)

    flashdb_component = component("flashdb")
    if flashdb_component["commit"] != \
            "4e5677408256f82d47cd56a6b04605dcee35ed9a":
        raise AssertionError("FlashDB commit pin changed")
    if sha256(flashdb / "src/fdb.c") != flashdb_component["core_source_sha256"]:
        raise AssertionError("FlashDB core source hash mismatch")
    if sha256(flashdb / "src/fdb_tsdb.c") != \
            flashdb_component["tsdb_source_sha256"]:
        raise AssertionError("FlashDB TSDB source hash mismatch")
    if sha256(flashdb / "src/fdb_utils.c") != \
            flashdb_component["utils_source_sha256"]:
        raise AssertionError("FlashDB utilities source hash mismatch")
    require_text(flashdb / "inc/fdb_def.h", '#define FDB_SW_VERSION                 "2.0.0"')
    require_text(flashdb / "src/fdb.c", "const char *_fdb_db_path")
    require_text(flashdb / "src/fdb_tsdb.c", "get_last_sector_addr")
    require_text(flashdb / "src/fdb_tsdb.c", "It will be a reverse iterator")

    fal_component = component("fal")
    fal_root = flashdb / str(fal_component["path"])
    if sha256(fal_root / "src/fal.c") != fal_component["core_source_sha256"]:
        raise AssertionError("FAL core source hash mismatch")
    if sha256(fal_root / "src/fal_flash.c") != \
            fal_component["flash_source_sha256"]:
        raise AssertionError("FAL flash source hash mismatch")
    if sha256(fal_root / "src/fal_partition.c") != \
            fal_component["partition_source_sha256"]:
        raise AssertionError("FAL partition source hash mismatch")
    require_text(flashdb / "port/fal/inc/fal_def.h", '#define FAL_SW_VERSION                 "0.5.99"')
    require_text(flashdb / "port/fal/src/fal_partition.c", "flash_device_find_by_part")
    require_text(flashdb / "LICENSE", "Apache License")
    require_text(flashdb / "port/fal/LICENSE", "Apache License")

    bosch = component("bosch-bma456-sensorapi")
    if bosch["commit"] != "3266db2c5de15be1a00232b8c0f2fd23e07934e0":
        raise AssertionError("Bosch BMA456 SensorAPI pin changed")
    if sha256(bma456 / "bma4.c") != bosch["core_source_sha256"]:
        raise AssertionError("Bosch BMA456 core source hash mismatch")
    if sha256(bma456 / "bma4.h") != bosch["core_header_sha256"]:
        raise AssertionError("Bosch BMA456 core header hash mismatch")
    if sha256(bma456 / "bma4_defs.h") != bosch["defs_header_sha256"]:
        raise AssertionError("Bosch BMA456 definitions header hash mismatch")
    if sha256(bma456 / "bma456w.c") != bosch["variant_source_sha256"]:
        raise AssertionError("Bosch BMA456W variant source hash mismatch")
    if sha256(bma456 / "bma456w.h") != bosch["variant_header_sha256"]:
        raise AssertionError("Bosch BMA456W variant header hash mismatch")
    if sha256(bma456 / "LICENSE") != bosch["license_sha256"]:
        raise AssertionError("Bosch BMA456 license hash mismatch")
    require_text(bma456 / "bma4.c", "@version    V2.29.0")
    require_text(bma456 / "bma4.c", "dev->delay_us == NULL")
    require_text(bma456 / "LICENSE", "BSD-3-Clause")

    st = component("st-lis2dw12-pid")
    if st["commit"] != "8d4bd522015004a9646102702901ba5a15ec6d39":
        raise AssertionError("ST LIS2DW12 provider pin changed")
    if sha256(lis2dw12 / "lis2dw12_reg.c") != st["source_sha256"]:
        raise AssertionError("ST LIS2DW12 source hash mismatch")
    if sha256(lis2dw12 / "lis2dw12_reg.h") != st["header_sha256"]:
        raise AssertionError("ST LIS2DW12 header hash mismatch")
    if sha256(lis2dw12 / "LICENSE") != st["license_sha256"]:
        raise AssertionError("ST LIS2DW12 license hash mismatch")
    require_text(lis2dw12 / "lis2dw12_reg.h", "stmdev_mdelay_ptr   mdelay")
    require_text(lis2dw12 / "lis2dw12_reg.h", "void *priv_data")
    require_text(lis2dw12 / "lis2dw12_reg.c", "lis2dw12_pin_int1_route_set")
    require_text(lis2dw12 / "lis2dw12_reg.c", "lis2dw12_reset_set(const stmdev_ctx_t *ctx, uint8_t val)")
    require_text(lis2dw12 / "LICENSE", "BSD 3-Clause License")

    st25 = component("st-st25dvxxkc-bsp")
    if st25["commit"] != "e9a35449b777699b5e1dd0f1466de0ead554893a":
        raise AssertionError("ST25DVxxKC provider pin changed")
    st25_files = {
        "st25dvxxkc.c": "source_sha256",
        "st25dvxxkc.h": "header_sha256",
        "st25dvxxkc_reg.c": "register_source_sha256",
        "st25dvxxkc_reg.h": "register_header_sha256",
        "LICENSE.md": "license_sha256",
    }
    for filename, manifest_key in st25_files.items():
        if sha256(st25dvxxkc / filename) != st25[manifest_key]:
            raise AssertionError(f"ST25DVxxKC {filename} hash mismatch")
    require_text(st25dvxxkc / "st25dvxxkc.c", "ST25DVxxKC_ReadMailboxData")
    require_text(st25dvxxkc / "st25dvxxkc.c", "ST25DVxxKC_RegisterBusIO")
    require_text(st25dvxxkc / "st25dvxxkc_reg.h", "ST25DVXXKC_MBLEN_DYN_REG")
    require_text(st25dvxxkc / "LICENSE.md", "Redistribution and use in source and binary forms")

    tiny = component("tiny-aes-c")
    if tiny["commit"] != "e72b6eff0884673997d0ca6385169bbd9b31936d":
        raise AssertionError("tiny-AES-c compatibility snapshot pin changed")
    if sha256(tiny_aes / "aes.c") != tiny["source_sha256"]:
        raise AssertionError("tiny-AES-c source hash mismatch")
    if sha256(tiny_aes / "aes.h") != tiny["header_sha256"]:
        raise AssertionError("tiny-AES-c header hash mismatch")
    if sha256(tiny_aes / "unlicense.txt") != tiny["license_sha256"]:
        raise AssertionError("tiny-AES-c license hash mismatch")
    require_text(tiny_aes / "aes.c", "static void InvCipher")
    require_text(tiny_aes / "aes.c", "static uint8_t xtime")
    require_text(tiny_aes / "unlicense.txt", "free and unencumbered software")

    iqs = component("flipperone-iqs7211e")
    if iqs["commit"] != "0a88e26bb8fd5b6afcdcc607fd748d7bc3d2b067":
        raise AssertionError("Flipper One IQS7211E snapshot pin changed")
    iqs_files = {
        "lib/drivers/iqs7211e/iqs7211e.c": "source_sha256",
        "lib/drivers/iqs7211e/iqs7211e.h": "header_sha256",
        "lib/drivers/iqs7211e/iqs7211e_reg.h": "register_header_sha256",
        "lib/drivers/iqs7211e/IQS7211E_init.h": "settings_header_sha256",
        "REUSE.toml": "reuse_sha256",
        "LICENSE.md": "license_readme_sha256",
    }
    for relative, manifest_key in iqs_files.items():
        if sha256(iqs7211e / relative) != iqs[manifest_key]:
            raise AssertionError(f"Flipper One IQS7211E {relative} hash mismatch")
    require_text(iqs7211e / "REUSE.toml", 'SPDX-License-Identifier = "MIT"')
    require_text(iqs7211e / "lib/drivers/iqs7211e/iqs7211e.c", "iqs7211e_load_config")
    require_text(iqs7211e / "lib/drivers/iqs7211e/iqs7211e_reg.h", "IQS7211E_PRODUCT_NUM 0x0458")

    settings = component("azoteq-iqs7211e-settings")
    if settings["commit"] != "436d3c42172abf812ec104521f29384fc02fc50e":
        raise AssertionError("Azoteq IQS7211E settings snapshot pin changed")
    settings_path = azoteq_settings / str(settings["path"])
    if sha256(settings_path) != settings["source_sha256"]:
        raise AssertionError("Azoteq IQS7211E settings header hash mismatch")
    require_text(settings_path, "Copyright (c) 2018 Azoteq (Pty) Ltd")
    require_text(settings_path, "Permission is hereby granted, free of charge")

    if args.goodix_democode_root is not None:
        goodix = args.goodix_democode_root.resolve()
        democode = component("goodix-gh3x2x-democode")
        if democode["commit"] != "2c0034a23b675a5f9a29e4a47e8b504c7a88e321":
            raise AssertionError("Goodix GH3X2X democode snapshot pin changed")
        if sha256(goodix / "LICENSE") != democode["license_sha256"]:
            raise AssertionError("Goodix GH3X2X democode license hash mismatch")
        require_text(goodix / "LICENSE", "Goodix")
        require_text(
            goodix / "demo_code/demo_kernel_code/kernel/gh_demo_version.h",
            "GH3X2X_DEMO_MAJOR_VERSION_NUMBER",
        )
        require_text(
            goodix / "demo_code/demo_kernel_code/driver/inc/gh_drv_version.h",
            "2024-12-27",
        )
        require_text(
            goodix / "demo_code/demo_kernel_code/kernel/gh_demo.c",
            "Gh3x2xDemoStartSamplingInner",
        )
        require_text(
            goodix / "demo_code/demo_kernel_code/driver/src/gh_drv_control.c",
            "GH3X2X_Init",
        )

    print("openR1 vendor inputs verified: nRF5 SDK 17.1.0/S140 7.2.0; "
          "SEGGER RTT 6.18a/fprintf 6.14d; "
          "FreeRTOS-Kernel 10.5.1/Nordic nRF52 port/CMSIS-FreeRTOS; CmBacktrace 1.4.2-compatible; "
          "FlashDB 2.0.0/FAL 0.5.99; Bosch BMA456 SensorAPI 2.29.0; "
          "ST LIS2DW12 v2.1.0-compatible; ST25DVxxKC compatible BSP; "
          "tiny-AES-c v1.0.0-compatible; Flipper One IQS7211E provider reference; "
          "Azoteq MIT settings template")


if __name__ == "__main__":
    main()
