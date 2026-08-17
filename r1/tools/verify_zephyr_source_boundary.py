#!/usr/bin/env python3
"""Offline structural gate for the opaque-free Zephyr target."""

from __future__ import annotations

import ast
import json
import re
from pathlib import Path


PROJECT = Path(__file__).resolve().parents[1]
BACKEND = PROJECT / "platform" / "nrf52840" / "zephyr"
MANIFEST = PROJECT.parent / "third-party" / "fetched" / "manifest.json"
RECONSTRUCTED = (
    "rtc_device.c",
    "generic_device_registry.c",
    "software_twi.c",
    "sensor_stream.c",
    "time_calendar.c",
    "r1_model_data.c",
    "quantized_runtime.c",
    "gxt310.c",
    "qma6100.c",
    "yhm2710.c",
    "goodix_primitives.c",
    "goodix_heap.c",
    "gomore_primitives.c",
    "gomore_tensor_runtime.c",
)
GOODIX_PROVIDER_OBJECTS = (
    "gh_drv_config.c",
    "gh_drv_control.c",
    "gh_drv_dump.c",
    "gh_drv_interface.c",
    "gh_demo.c",
    "gh_demo_hook.c",
    "gh_demo_reg_array.c",
    "gh_demo_user.c",
    "gh_agc.c",
    "gh_changeinttime.c",
    "gh_movedetect.c",
    "gh_multi_sen_pro.c",
    "goodix_spo2_config_for_gh3x2x-v2.23_7ecd2a.c",
    "r1_gh3x2x_port.c",
    "r1_gh3x2x_bind.c",
    "r1_gh3x2x_stubs.c",
)
SOURCE_IDS = {
    "zephyr": "zephyr-rtos",
    "hal_nordic": "zephyr-hal-nordic",
    "cmsis": "zephyr-cmsis",
    "tinycrypt": "zephyr-tinycrypt",
    "mcuboot": "mcuboot",
}
FILE_SOURCE_IDS = {
    "bosch_bma456": {
        "component": "bosch-bma456-sensorapi",
        "files": {
            "bma4.c": "core_source_sha256",
            "bma4.h": "core_header_sha256",
            "bma4_defs.h": "defs_header_sha256",
            "bma456w.c": "variant_source_sha256",
            "bma456w.h": "variant_header_sha256",
            "LICENSE": "license_sha256",
        },
    },
    "st_lis2dw12": {
        "component": "st-lis2dw12-pid",
        "files": {
            "lis2dw12_reg.c": "source_sha256",
            "lis2dw12_reg.h": "header_sha256",
            "LICENSE": "license_sha256",
        },
    },
    "st_st25dvxxkc": {
        "component": "st-st25dvxxkc-bsp",
        "files": {
            "st25dvxxkc.c": "source_sha256",
            "st25dvxxkc.h": "header_sha256",
            "st25dvxxkc_reg.c": "register_source_sha256",
            "st25dvxxkc_reg.h": "register_header_sha256",
            "LICENSE.md": "license_sha256",
        },
    },
    "flashdb": {
        "component": "flashdb",
        "lock_fields": ("commit", "archive_sha256"),
        "files": {
            "src/fdb.c": "core_source_sha256",
            "src/fdb_tsdb.c": "tsdb_source_sha256",
            "src/fdb_utils.c": "utils_source_sha256",
        },
    },
    "fal": {
        "component": "fal",
        "lock_fields": ("version", "license"),
        "files": {
            "port/fal/src/fal.c": "core_source_sha256",
            "port/fal/src/fal_flash.c": "flash_source_sha256",
            "port/fal/src/fal_partition.c": "partition_source_sha256",
        },
    },
    "goodix_democode": {
        "component": "goodix-gh3x2x-democode",
        "lock_fields": (
            "commit",
            "archive_sha256",
            "license_sha256",
            "admitted_source_file_count",
            "admitted_source_aggregate_sha256",
        ),
        "files": {},
    },
}


def require(text: str, needle: str, label: str) -> None:
    if needle not in text:
        raise AssertionError(f"{label} is missing {needle!r}")


def package_source_lock() -> dict[str, dict[str, str]]:
    tree = ast.parse((PROJECT / "tools" / "package_zephyr_bundle.py").read_text())
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(
            isinstance(target, ast.Name) and target.id == "SOURCE_LOCK"
            for target in node.targets
        ):
            value = ast.literal_eval(node.value)
            if not isinstance(value, dict):
                break
            return value
    raise AssertionError("package_zephyr_bundle.py has no literal SOURCE_LOCK")


def main() -> None:
    cmake = (BACKEND / "CMakeLists.txt").read_text()
    linker = (BACKEND / "openr1_reconstructed.ld").read_text()
    for source in RECONSTRUCTED:
        require(cmake, f"/{source}", "Zephyr CMake source corpus")
        require(linker, f"*{source}.obj", "Zephyr linker retention corpus")
    if cmake.count("${OPENR1_ROOT}/reconstructed/") != len(RECONSTRUCTED):
        raise AssertionError("Zephyr reconstructed CMake corpus is not exactly 14 entries")
    if linker.count("KEEP(*") != len(RECONSTRUCTED):
        raise AssertionError("Zephyr linker retention corpus is not exactly 14 entries")

    opaque_suffixes = {".a", ".bin", ".hex", ".lib", ".o", ".obj", ".zip"}
    opaque = [path for path in BACKEND.rglob("*") if path.suffix.lower() in opaque_suffixes]
    if opaque:
        raise AssertionError(f"opaque input present in Zephyr backend: {opaque}")
    scanned = "\n".join(
        path.read_text(errors="strict")
        for path in sorted(BACKEND.rglob("*"))
        if path.suffix in {".c", ".h", ".conf", ".txt"} or path.name == "CMakeLists.txt"
    )
    forbidden = re.findall(r"\b(?:sd_ble_[A-Za-z0-9_]*|nrf_sdh[A-Za-z0-9_]*)\b|S140", scanned)
    if forbidden:
        raise AssertionError(f"SoftDevice dependency found in Zephyr sources: {sorted(set(forbidden))}")

    sysbuild = (BACKEND / "sysbuild.conf").read_text()
    boot = (BACKEND / "sysbuild" / "mcuboot.conf").read_text()
    require(sysbuild, "SB_CONFIG_BOOTLOADER_MCUBOOT=y", "sysbuild configuration")
    require(sysbuild, "SB_CONFIG_BOOT_SIGNATURE_TYPE_ECDSA_P256=y", "sysbuild configuration")
    require(boot, "CONFIG_SINGLE_APPLICATION_SLOT=y", "MCUboot configuration")
    require(boot, "CONFIG_BOOT_VALIDATE_SLOT0=y", "MCUboot configuration")
    require(boot, "CONFIG_MCUBOOT_SERIAL=n", "MCUboot configuration")
    configuration = (BACKEND / "prj.conf").read_text()
    require(configuration, "CONFIG_FLASH=y", "Zephyr product-storage configuration")
    require(configuration, "CONFIG_FLASH_MAP=y", "Zephyr product-storage configuration")
    require(configuration, "CONFIG_BT_SETTINGS=y", "Zephyr Bluetooth persistence configuration")
    require(configuration, "CONFIG_SETTINGS=y", "Zephyr settings configuration")
    require(configuration, "CONFIG_NVS=y", "Zephyr settings configuration")
    require(configuration, "CONFIG_SETTINGS_NVS=y", "Zephyr settings configuration")
    require(configuration, "CONFIG_SETTINGS_NVS_SECTOR_COUNT=3",
            "Zephyr settings partition geometry")
    require(configuration, "CONFIG_ADC=y", "Zephyr SAADC configuration")
    require(configuration, "CONFIG_I2C=y", "Zephyr motion-bus configuration")
    require(configuration, "CONFIG_EVENTS=y", "Zephyr touch-worker configuration")
    require(configuration, "CONFIG_SYS_CLOCK_TICKS_PER_SEC=1024",
            "Zephyr recovered scheduler cadence")
    require(configuration, "CONFIG_WATCHDOG=y", "Zephyr watchdog configuration")
    board_kconfig = (BACKEND / "boards" / "openr1" / "openr1_nrf52840" /
                     "Kconfig.openr1_nrf52840").read_text()
    require(board_kconfig, "config BOARD_OPENR1_ENABLE_DCDC",
            "Zephyr stock REG1 board configuration")
    require(board_kconfig, "select SOC_DCDC_NRF52X",
            "Zephyr stock REG1 board selection")
    for source in ("openr1_storage_zephyr.c", "openr1_databases_zephyr.c"):
        require(cmake, source, "Zephyr storage source binding")
    main_source = (BACKEND / "src" / "main.c").read_text()
    require(main_source, "openr1_storage_zephyr_initialize()", "Zephyr storage startup")
    require(main_source, "openr1_databases_zephyr_initialize(", "Zephyr database startup")
    require(main_source, "settings_load()", "Zephyr Bluetooth settings startup")
    require(main_source, "openr1_analog_zephyr_initialize()", "Zephyr SAADC startup")
    require(main_source, "openr1_reset_zephyr_initialize()", "Zephyr reset-reason startup")
    require(main_source, "openr1_watchdog_zephyr_initialize()", "Zephyr watchdog startup")
    require(main_source, "openr1_clock_zephyr_initialize(", "Zephyr wall-clock startup")
    require(main_source, "openr1_power_zephyr_initialize()", "Zephyr REG1 startup")
    require(main_source, "openr1_motion_zephyr_initialize()", "Zephyr motion startup")
    require(main_source, "openr1_sensor_stream_zephyr_initialize()",
            "Zephyr sensor-stream startup")
    require(main_source, "openr1_sensor_stream_zephyr_poll()",
            "Zephyr sensor-stream polling")
    require(main_source, "openr1_touch_zephyr_initialize()", "Zephyr touch startup")
    require(main_source, "openr1_nfc_zephyr_initialize()", "Zephyr NFC startup")
    require(main_source, "openr1_yhm2710_zephyr_initialize()",
            "Zephyr YHM2710 shared-power startup")
    require(main_source, "openr1_temperature_zephyr_initialize()",
            "Zephyr GXT310 temperature startup")
    require(main_source, "openr1_optical_zephyr_initialize()",
            "Zephyr optical-provider startup")
    require(main_source, "openr1_nfc_resources_zephyr_initialize()",
            "Zephyr NFC dock-resource startup")
    require(main_source, "r1_runtime_set_touch_handler(",
            "Zephyr runtime touch-enable binding")
    clock_startup = main_source.find("openr1_clock_zephyr_initialize(")
    database_startup = main_source.find("openr1_databases_zephyr_initialize(")
    if clock_startup < 0 or database_startup < clock_startup:
        raise AssertionError("Zephyr clock must initialize before health database recovery")
    temperature_startup = main_source.find("openr1_temperature_zephyr_initialize()")
    stream_startup = main_source.find("openr1_sensor_stream_zephyr_initialize()")
    if temperature_startup < 0 or stream_startup < temperature_startup:
        raise AssertionError(
            "Zephyr temperature provider must initialize before sensor streams")
    if "openr1_sensor_stream_zephyr_temperature_once_set(" in main_source:
        raise AssertionError(
            "Zephyr startup must not start the dormant temperature one-shot")
    if "openr1_sensor_stream_zephyr_gomore_accelerometer_stage_set(" in main_source:
        raise AssertionError(
            "Zephyr startup must not start dormant GoMore input staging")
    yhm_startup = main_source.find("openr1_yhm2710_zephyr_initialize(")
    optical_startup = main_source.find("openr1_optical_zephyr_initialize(")
    if yhm_startup < 0 or optical_startup < yhm_startup:
        raise AssertionError("Zephyr YHM2710 must initialize before the optical provider")
    if "openr1_optical_zephyr_start(" in main_source:
        raise AssertionError("Zephyr startup must not start optical sampling")
    storage_source = (BACKEND / "src" / "openr1_storage_zephyr.c").read_text()
    require(storage_source, "FIXED_PARTITION_ID(openr1_data_partition)",
            "Zephyr product-storage partition binding")
    require(storage_source, "flash_area_write", "Zephyr source flash provider")

    dts = (BACKEND / "boards" / "openr1" / "openr1_nrf52840" /
           "openr1_nrf52840.dts").read_text()
    expected_partitions = {
        "mcuboot": (0x00000000, 0x0000C000),
        "image-0": (0x0000C000, 0x000C5000),
        "openr1-settings": (0x000D1000, 0x00003000),
        "openr1-data": (0x000D4000, 0x00024000),
        "retail-boot-migration-reserve": (0x000F8000, 0x00008000),
    }
    for label, (address, size) in expected_partitions.items():
        pattern = rf'label\s*=\s*"{re.escape(label)}";\s*reg\s*=\s*<0x{address:08x}\s+0x{size:08x}>;'
        if re.search(pattern, dts, re.DOTALL | re.IGNORECASE) is None:
            raise AssertionError(f"missing exact devicetree partition: {label}")
    require(dts, "zephyr,settings-partition = &settings_partition;",
            "Zephyr settings partition binding")
    for needle in (
        'io-channel-names = "battery", "pmic-current", "nfc-rectifier";',
        "zephyr,input-positive = <NRF_SAADC_AIN5>",
        "zephyr,input-positive = <NRF_SAADC_AIN3>",
        "zephyr,input-positive = <NRF_SAADC_AIN2>",
        'zephyr,gain = "ADC_GAIN_1_2";',
        'zephyr,gain = "ADC_GAIN_1_6";',
        "ADC_ACQ_TIME(ADC_ACQ_TIME_MICROSECONDS, 40)",
        "ADC_ACQ_TIME(ADC_ACQ_TIME_MICROSECONDS, 10)",
        "zephyr,resolution = <12>;",
        "zephyr,oversampling = <0>;",
        "motion-bus = <&i2c1>;",
        "motion-interrupt-gpios = <&gpio0 15 GPIO_ACTIVE_HIGH>;",
        "touch-bus = <&i2c0>;",
        "touch-ldo-gpios = <&gpio0 30 GPIO_ACTIVE_HIGH>;",
        "touch-rdy-gpios = <&gpio0 17 GPIO_ACTIVE_HIGH>;",
        "nfc-bus = <&i2c1>;",
        "nfc-gpo-gpios = <&gpio0 3 GPIO_ACTIVE_HIGH>;",
        "nfc-enable-gpios = <&gpio1 10 GPIO_ACTIVE_HIGH>;",
        "pmic-stacmd-gpios = <&gpio1 1 GPIO_ACTIVE_HIGH>;",
        "optical-interrupt-gpios = <&gpio0 21 GPIO_ACTIVE_LOW>;",
        "optical-emitter-gpios = <&gpio0 10 GPIO_ACTIVE_HIGH>;",
        "optical-reset-gpios = <&gpio1 4 GPIO_ACTIVE_HIGH>;",
        'compatible = "nordic,nrf-twim";',
        "clock-frequency = <I2C_BITRATE_FAST>;",
    ):
        require(dts, needle, "Zephyr recovered SAADC geometry")
    require(cmake, "openr1_analog_zephyr.c", "Zephyr SAADC source binding")
    require(cmake, "openr1_platform.ld", "Zephyr platform API retention")
    platform_linker = (BACKEND / "openr1_platform.ld").read_text()
    require(platform_linker, "KEEP(*(.openr1_platform_api))",
            "Zephyr platform API retention")
    analog_source = (BACKEND / "src" / "openr1_analog_zephyr.c").read_text()
    require(analog_source, "adc_read_dt(", "Zephyr source SAADC provider")
    require(analog_source, "return -ENOTSUP;", "Zephyr battery-power fail-closed gate")
    for source in ("openr1_reset_zephyr.c", "openr1_watchdog_zephyr.c"):
        require(cmake, source, "Zephyr reset/watchdog source binding")
    require(dts, "&wdt0", "Zephyr watchdog devicetree binding")
    watchdog_source = (BACKEND / "src" / "openr1_watchdog_zephyr.c").read_text()
    for needle in (
        "OPENR1_WATCHDOG_RELOAD_MILLISECONDS 10000u",
        "OPENR1_WATCHDOG_FEED_TICKS 1024u",
        "WDT_FLAG_RESET_SOC",
        "WDT_OPT_PAUSE_HALTED_BY_DBG",
    ):
        require(watchdog_source, needle, "Zephyr recovered watchdog policy")
    reset_source = (BACKEND / "src" / "openr1_reset_zephyr.c").read_text()
    require(reset_source, "nrf_power_resetreas_get(NRF_POWER)",
            "Zephyr reset-reason hardware binding")
    require(reset_source, "retained_reset_trace __noinit",
            "Zephyr retained reset trace")
    require(reset_source, "void k_sys_fatal_error_handler(",
            "Zephyr fatal reset-trace binding")
    require(reset_source, "esf->basic.pc", "Zephyr fatal program-counter capture")
    require(reset_source, "esf->basic.lr", "Zephyr fatal return-address capture")
    require(cmake, "openr1_clock_zephyr.c", "Zephyr wall-clock source binding")
    clock_source = (BACKEND / "src" / "openr1_clock_zephyr.c").read_text()
    require(clock_source, "OPENR1_CLOCK_CADENCE_TICKS 1024u",
            "Zephyr recovered wall-clock cadence")
    require(clock_source, "r1_clock_synchronize(", "Zephyr wall-clock adoption")
    require(clock_source, "time_calendar_unix_to_broken_down(",
            "Zephyr reconstructed calendar provider")
    require(cmake, "openr1_power_zephyr.c", "Zephyr REG1 source binding")
    power_source = (BACKEND / "src" / "openr1_power_zephyr.c").read_text()
    require(power_source, "nrf_power_dcdcen_set(NRF_POWER, enabled)",
            "Zephyr source REG1 provider")
    require(power_source, "nrf_power_dcdcen_get(NRF_POWER)",
            "Zephyr REG1 write verification")
    databases_source = (
        BACKEND / "src" / "openr1_databases_zephyr.c").read_text()
    require(databases_source, "time_calendar_unix_to_broken_down(",
            "Zephyr reconstructed local-day calendar provider")
    require(databases_source,
            "system_settings[4] != R1_SYSTEM_SETTINGS_SWITCH_TYPE_REG1",
            "Zephyr REG1 command-type gate")
    commit = databases_source.find("r1_kv_store_commit(&kv_store)")
    apply = databases_source.find("openr1_power_zephyr_set_reg1(enabled)")
    if commit < 0 or apply < commit:
        raise AssertionError("Zephyr REG1 action must follow successful persistence")
    for needle in (
        "r1_fal_bind(flash)",
        "fal_init() != 7",
        'fal_partition_find("health.db")',
        "UINT32_C(0x00002000)",
        "UINT32_C(0x00006000)",
        "fdb_tsdb_control(",
        "fdb_tsdb_init(",
        "fdb_tsl_iter_by_time(",
        "record->log_len == R1_HEALTH_DB_RECORD_BYTES",
        "bytes != R1_HEALTH_DB_RECORD_BYTES",
        "r1_health_db_decode_record(",
        "r1_health_db_restore_record(",
        "record->time < 0",
        "decoded.recorded_timestamp < recovery->from_timestamp",
        "r1_health_db_build_record(",
        "r1_health_db_encode_record(",
        "fdb_tsl_append(",
        "plan.current_day_recovery_requested",
        "plan.daily_cache_reset_requested",
        "health_time_recovery_failures",
        "health_destructive_actions_suppressed",
        "health_gomore_actions_suppressed",
        "R1_KV_HSYNC",
        "r1_health_sync_cursor_decode(",
        "r1_health_reconcile_sync_cursors(",
        "r1_health_sync_cursor_encode(",
        "health_cursor_updates_persisted",
        "health_cursor_update_failures",
        "K_MUTEX_DEFINE(kv_mutex)",
        "openr1_databases_zephyr_multicast_time_transition",
        "r1_activity_cache_reset(",
        "r1_health_u8_cache_reset(",
        "r1_health_u16_cache_reset(",
        "openr1_databases_zephyr_multicast_hour",
        "recovery_records_decoded",
        "recovery_records_restored",
        "recovery_records_rejected",
        "R1_HEALTH_DB_STARTUP_COMPLETED",
        "retained_health_crash_record __noinit",
        "&runtime->device.health.activity",
        "&runtime->device.health.heart_rate",
        "&runtime->device.health.blood_oxygen",
        "&runtime->device.health.heart_rate_variability",
        "databases_zephyr_api",
    ):
        require(databases_source, needle, "Zephyr health TSDB source binding")
    health_db_header = (
        PROJECT / "include" / "openr1" / "r1_health_db.h").read_text()
    health_db_source = (PROJECT / "src" / "r1_health_db.c").read_text()
    for needle in (
        "R1_HEALTH_DB_POPULATED_BYTES 50u",
        "R1_HEALTH_DB_RESERVED_TAIL_BYTES 78u",
        "r1_health_db_record",
        "r1_health_db_decode_record",
        "r1_health_db_encode_record",
        "r1_health_db_build_record",
        "r1_health_db_restore_record",
    ):
        require(health_db_header, needle, "transparent health record contract")
    for needle in (
        "length != R1_HEALTH_DB_RECORD_BYTES",
        "health_db_read_i16(input)",
        "record->recorded_timestamp = health_db_read_u32(input + 4u)",
        "health_db_read_u32(input + 20u + index * 4u)",
        "packed & UINT32_C(0x0fff)",
        "(packed >> 12u) & UINT32_C(0x03ff)",
        "(packed >> 22u) & UINT32_C(0x03ff)",
        "current_hour == 0u",
        "record->recorded_timestamp - (int64_t)seconds_into_day",
        "r1_activity_cache_write_hour(",
        "r1_health_u8_cache_write_slot(",
        "r1_health_u16_cache_write_slot(",
        "health_db_pack_activity(",
    ):
        require(health_db_source, needle, "transparent health record codec")
    if "fdb_tsl_clean(" in databases_source:
        raise AssertionError(
            "Zephyr health append must not expose stock destructive retry")
    for needle in (
        "local_hour_known",
        "current_local_hour != last_local_hour",
        "old_clock_available",
        "r1_health_plan_time_transition(&transition, &plan)",
        "openr1_databases_zephyr_multicast_time_transition(",
        "openr1_databases_zephyr_multicast_hour(",
    ):
        require(clock_source, needle, "Zephyr recovered hour producer")
    for needle in (
        "r1_gomore_time_transition_adapter(",
        "health_suppress_gomore_reinitialization",
        "health_gomore_actions_suppressed += 1u",
    ):
        require(databases_source, needle, "Zephyr GoMore time adapter binding")
    for needle in (
        "OPENR1_FLASHDB_ROOT",
        "zephyr_get(OPENR1_FLASHDB_ROOT SYSBUILD GLOBAL)",
        "${OPENR1_ROOT}/port/r1_fal_port.c",
        "${OPENR1_FLASHDB_ROOT}/src/fdb.c",
        "${OPENR1_FLASHDB_ROOT}/src/fdb_tsdb.c",
        "${OPENR1_FLASHDB_ROOT}/src/fdb_utils.c",
        "${OPENR1_FLASHDB_ROOT}/port/fal/src/fal.c",
        "${OPENR1_FLASHDB_ROOT}/port/fal/src/fal_flash.c",
        "${OPENR1_FLASHDB_ROOT}/port/fal/src/fal_partition.c",
    ):
        require(cmake, needle, "Zephyr pinned health storage source binding")
    fdb_configuration = (PROJECT / "port" / "fdb_cfg.h").read_text()
    for needle in ("FDB_USING_TSDB", "FDB_USING_FAL_MODE",
                   "FDB_WRITE_GRAN 32", "FDB_PRINT"):
        require(fdb_configuration, needle, "Zephyr FlashDB product configuration")
    fal_configuration = (PROJECT / "port" / "fal_cfg.h").read_text()
    for needle in ('"health.db"', "0x02000", "0x06000",
                   '"device_flash"'):
        require(fal_configuration, needle, "Zephyr recovered FAL partition table")
    require((PROJECT / "port" / "r1_fal_port.c").read_text(),
            "UINT32_C(0x24000)", "Zephyr recovered FAL device geometry")
    for needle in (
        "OPENR1_BMA456_ROOT",
        "OPENR1_LIS2DW12_ROOT",
        "zephyr_get(OPENR1_BMA456_ROOT SYSBUILD GLOBAL)",
        "zephyr_get(OPENR1_LIS2DW12_ROOT SYSBUILD GLOBAL)",
        "${OPENR1_BMA456_ROOT}/bma4.c",
        "${OPENR1_BMA456_ROOT}/bma456w.c",
        "${OPENR1_LIS2DW12_ROOT}/lis2dw12_reg.c",
        "openr1_motion_zephyr.c",
        "openr1_sensor_stream_zephyr.c",
    ):
        require(cmake, needle, "Zephyr pinned motion source binding")
    motion_source = (BACKEND / "src" / "openr1_motion_zephyr.c").read_text()
    for needle in (
        "openr1_twim1_zephyr_write_read(",
        "openr1_twim1_zephyr_write(",
        "OPENR1_MOTION_I2C_ADDRESS UINT8_C(0x18)",
        "R1_MOTION_POLICY_AUTO_LICENSED",
        "GPIO_INT_EDGE_TO_ACTIVE",
        "r1_motion_adapter_read_fifo(",
    ):
        require(motion_source, needle, "Zephyr source motion provider")
    sensor_stream_source = (
        BACKEND / "src" / "openr1_sensor_stream_zephyr.c").read_text()
    for needle in (
        "sensor_stream_initialize(",
        "sensor_stream_bind_singleton_providers(",
        "sensor_stream_acc_object_create(",
        "sensor_stream_temp_object_create(",
        "generic_device_registry_list_append_alloc(",
        "openr1_motion_zephyr_read_fifo(",
        "R1_MOTION_BATCH_SAMPLE_LIMIT",
        "r1_motion_batch_encode(",
        "openr1_databases_zephyr_accelerometer_calibration(",
        "openr1_temperature_zephyr_read_stream(",
        "temperature_provider",
        '"temp"',
        '"once"',
        "gomore_primitives_temperature_measurement_begin(",
        "gomore_primitives_temperature_measurement_step(",
        "gomore_primitives_scaled_sample_publish(",
        "SENSOR_STREAM_MODE_PER_SAMPLE",
        "openr1_databases_zephyr_consume_temperature_event(",
        '"gomore"',
        "gomore_primitives_topic_accelerometer_ingest(",
        "openr1_sensor_stream_zephyr_gomore_accelerometer_stage_set(",
        "SENSOR_STREAM_MODE_BATCH",
        "k_uptime_ticks()",
        "sensor_stream_timer_poll(",
    ):
        require(sensor_stream_source, needle,
                "Zephyr accelerometer sensor-stream binding")
    motion_model = (PROJECT / "src" / "r1_motion.c").read_text()
    for needle in (
        "r1_motion_batch_encode(",
        "R1_MOTION_BATCH_COUNT_OFFSET",
        "R1_MOTION_BATCH_TIMESTAMP_OFFSET",
        "calibration_in_progress",
    ):
        require(motion_model, needle, "R1 motion batch contract")
    health_model = (PROJECT / "src" / "r1_health.c").read_text()
    for needle in (
        "r1_temperature_pair_stream_value(",
        "const uint32_t magnitude = (uint16_t)entry->offset",
        "const uint32_t toward_zero = sum + (sum >> 31u)",
    ):
        require(health_model, needle, "R1 temperature stream contract")
    gomore_model = (
        PROJECT / "reconstructed" / "gomore_primitives" /
        "gomore_primitives.c").read_text()
    for needle in (
        "sizeof(gomore_primitives_scaled_sample_state) == 120u",
        "attempt_count) == 11u",
        "measurement_active) == 12u",
        "capture_enabled) == 14u",
        "capture_count) == 16u",
        "captured) == 18u",
        "clear_bytes((uint8_t *)state, 14u)",
        "state->attempt_count > 30u",
        "state->recent_count = 0u",
        "gomore_primitives_topic_accelerometer_ingest(",
        "gomore_primitives_topic_raw_optical_ingest(",
        "gomore_primitives_topic_heart_rate_ingest(",
        "gomore_primitives_topic_hrv_ingest(",
        "gomore_primitives_topic_update_take_ready(",
        "gomore_primitives_topic_update_complete(",
        "bits_float(UINT32_C(0x3F7A0000))",
        "state->ready_flags = 0u",
    ):
        require(gomore_model, needle,
                "R1 temperature one-shot reducer contract")
    database_source = (
        BACKEND / "src" / "openr1_databases_zephyr.c").read_text()
    for needle in (
        "openr1_databases_zephyr_consume_temperature_event(",
        "length != 8u",
        "R1_TEMPERATURE_PUBLISHED_MIN",
        "R1_TEMPERATURE_PUBLISHED_MAX",
        "openr1_clock_zephyr_epoch(",
        "openr1_clock_zephyr_local_tm(",
        "r1_temperature_store_sample(",
    ):
        require(database_source, needle,
                "Zephyr temperature event/cache consumer")
    pinctrl = (BACKEND / "boards" / "openr1" / "openr1_nrf52840" /
               "openr1_nrf52840-pinctrl.dtsi").read_text()
    for needle in (
        "NRF_PSEL(TWIM_SDA, 0, 1)",
        "NRF_PSEL(TWIM_SCL, 0, 12)",
        "NRF_PSEL(TWIM_SDA, 0, 14)",
        "NRF_PSEL(TWIM_SCL, 0, 11)",
    ):
        require(pinctrl, needle, "Zephyr recovered TWIM pin geometry")
    require(cmake, "openr1_touch_zephyr.c", "Zephyr touch source binding")
    touch_source = (BACKEND / "src" / "openr1_touch_zephyr.c").read_text()
    touch_header = (BACKEND / "src" / "openr1_touch_zephyr.h").read_text()
    for needle in (
        "i2c_write_read(",
        "i2c_write(",
        "R1_IQS7211E_ADDRESS",
        "R1_IQS7211E_CONFIG_MAX_WRITE",
        "GPIO_INT_EDGE_TO_INACTIVE",
        "r1_iqs7211e_configure(",
        "atomic_get(&identity_valid) == 0",
        "!power_provider_complete()",
        "k_sleep(K_TICKS(130))",
        "k_sleep(K_TICKS(20))",
    ):
        require(touch_source, needle, "Zephyr source touch provider")
    for needle in (
        "OPENR1_TOUCH_ZEPHYR_POWER_CLIENT_BIT UINT8_C(2)",
        "OPENR1_TOUCH_ZEPHYR_POWER_RELEASE_TICKS UINT32_C(0x800)",
        "OPENR1_TOUCH_ZEPHYR_SOURCE_WEAR 0u",
        "OPENR1_TOUCH_ZEPHYR_SOURCE_FACTORY 2u",
    ):
        require(touch_header, needle, "Zephyr recovered touch policy")
    for needle in (
        "OPENR1_ST25DVXXKC_ROOT",
        "zephyr_get(OPENR1_ST25DVXXKC_ROOT SYSBUILD GLOBAL)",
        "${OPENR1_ST25DVXXKC_ROOT}/st25dvxxkc.c",
        "${OPENR1_ST25DVXXKC_ROOT}/st25dvxxkc_reg.c",
        "openr1_nfc_zephyr.c",
        "openr1_twim1_zephyr.c",
    ):
        require(cmake, needle, "Zephyr pinned NFC source binding")
    twim1_source = (BACKEND / "src" / "openr1_twim1_zephyr.c").read_text()
    for needle in (
        "OPENR1_MOTION_SCL_PIN NRF_GPIO_PIN_MAP(0, 11)",
        "OPENR1_MOTION_SDA_PIN NRF_GPIO_PIN_MAP(0, 14)",
        "OPENR1_NFC_SCL_PIN NRF_GPIO_PIN_MAP(1, 11)",
        "OPENR1_NFC_SDA_PIN NRF_GPIO_PIN_MAP(1, 14)",
        "nrf_twim_disable(NRF_TWIM1)",
        "nrf_twim_pins_set(NRF_TWIM1, scl, sda)",
        "owner == OPENR1_TWIM1_ZEPHYR_OWNER_NFC",
        "error = -EBUSY",
    ):
        require(twim1_source, needle, "Zephyr shared TWIM1 ownership")
    nfc_source = (BACKEND / "src" / "openr1_nfc_zephyr.c").read_text()
    for needle in (
        "ST25DVxxKC_RegisterBusIO(",
        "St25Dvxxkc_Drv.Init(",
        "R1_ST25DVXXKC_MAILBOX_CAPACITY",
        "OPENR1_NFC_MAX_WRITE_BYTES 256u",
        "GPIO_INT_EDGE_TO_ACTIVE",
        "openr1_twim1_zephyr_acquire(",
        "!resources_complete()",
        "r1_st25dvxxkc_poll(",
    ):
        require(nfc_source, needle, "Zephyr source NFC provider")
    for source in ("openr1_yhm2710_zephyr.c",
                   "openr1_nfc_resources_zephyr.c"):
        require(cmake, source, "Zephyr shared-power/dock resource binding")
    yhm_source = (BACKEND / "src" / "openr1_yhm2710_zephyr.c").read_text()
    for needle in (
        "OPENR1_YHM2710_PIN NRF_GPIO_PIN_MAP(1, 1)",
        ".input_pull = NRF_GPIO_PIN_PULLUP",
        ".delay_cycles = delay_microseconds",
        ".delay_cycles = delay_core_cycles",
        "yhm2710_configure(&pmic)",
        "r1_power_lease_bind(",
        "openr1_analog_zephyr_bind_power(",
        "openr1_touch_zephyr_bind_power(",
        "R1_POWER_CLIENT_BATTERY_SAMPLING",
        "R1_POWER_CLIENT_OPTICAL_PPG",
        "R1_POWER_CLIENT_TOUCH",
        "openr1_yhm2710_zephyr_optical_acquire",
        "openr1_yhm2710_zephyr_optical_release",
    ):
        require(yhm_source, needle, "Zephyr reconstructed YHM2710 binding")
    reconstructed_yhm = (
        PROJECT / "reconstructed" / "yhm2710" / "yhm2710.c").read_text()
    require(reconstructed_yhm, "UINT8_C(0xA8)",
            "YHM2710 first-client power action")
    require(reconstructed_yhm, "UINT8_C(0x28)",
            "YHM2710 final-client power action")
    nfc_resources = (
        BACKEND / "src" / "openr1_nfc_resources_zephyr.c").read_text()
    for needle in (
        "OPENR1_NFC_BOARD_ENABLE_PIN NRF_GPIO_PIN_MAP(1, 10)",
        "OPENR1_NFC_BOARD_SETTLE_TICKS UINT32_C(10)",
        "NRF_GPIO_PIN_H0H1",
        "k_mutex_lock(&nfc_dock_bus_mutex, K_NO_WAIT)",
        "openr1_nfc_zephyr_bind_resources(",
    ):
        require(nfc_resources, needle, "Zephyr NFC dock-resource binding")

    for needle in (
        "OPENR1_GOODIX_DEMOCODE_ROOT",
        "zephyr_get(OPENR1_GOODIX_DEMOCODE_ROOT SYSBUILD GLOBAL)",
        "${OPENR1_GOODIX_DRIVER_DIR}/src/gh_drv_control.c",
        "${OPENR1_GOODIX_KERNEL_DIR}/gh_demo.c",
        "${OPENR1_GOODIX_MODULE_DIR}/gh_agc/gh_agc.c",
        "goodix_spo2_config_for_gh3x2x-v2.23_7ecd2a.c",
        "r1_gh3x2x_bind.c",
        "r1_gh3x2x_stubs.c",
        "openr1_optical_zephyr.c",
        "openr1_goodix.ld",
    ):
        require(cmake, needle, "Zephyr pinned Goodix source binding")
    goodix_linker = (BACKEND / "openr1_goodix.ld").read_text()
    for source in GOODIX_PROVIDER_OBJECTS:
        require(goodix_linker, f"*{source}.obj", "Zephyr Goodix linker retention corpus")
    if goodix_linker.count("KEEP(*") != len(GOODIX_PROVIDER_OBJECTS):
        raise AssertionError("Zephyr Goodix linker corpus is not exactly 16 entries")
    if re.search(r"(?:^|[/(])[^\s)]*\.a(?:[/(]|$)", goodix_linker):
        raise AssertionError("Zephyr Goodix linker retention names an archive")
    software_twi_source = (
        BACKEND / "src" / "openr1_software_twi_zephyr.c").read_text()
    for needle in (
        "NRF_GPIO_PIN_MAP(1, 13)",
        "NRF_GPIO_PIN_MAP(0, 28)",
        "NRF_GPIO_PIN_MAP(1, 9)",
        "NRF_GPIO_PIN_MAP(0, 31)",
        "software_twi_i2c_2_open()",
        "software_twi_i2c_4_open()",
        "software_twi_i2c_2_read(0u, 0u, request)",
        "software_twi_i2c_2_write(0u, 0u, request)",
        "software_twi_i2c_4_read(0u, 0u, request)",
        "software_twi_i2c_4_write(0u, 0u, request)",
        ".input_pull = NRF_GPIO_PIN_NOPULL",
        "K_MUTEX_DEFINE(software_twi_mutex)",
    ):
        require(software_twi_source, needle, "Zephyr software-TWI owner")
    temperature_source = (
        BACKEND / "src" / "openr1_temperature_zephyr.c").read_text()
    databases_source = (
        BACKEND / "src" / "openr1_databases_zephyr.c").read_text()
    for needle in (
        "R1_KV_NV_R1",
        "R1_NV_RECOVERY_TEMPERATURE_CALIBRATION_OFFSET",
        "R1_NV_RECOVERY_TEMPERATURE_CALIBRATION_BYTES",
        "r1_temperature_pair_calibration_decode(",
        "openr1_databases_zephyr_temperature_calibration(",
        "R1_NV_RECOVERY_ACCELEROMETER_CALIBRATION_OFFSET",
        "R1_NV_RECOVERY_ACCELEROMETER_CALIBRATION_BYTES",
        "r1_nv_accelerometer_calibration_decode(",
        "openr1_databases_zephyr_accelerometer_calibration(",
        "R1_KV_POWER",
        "r1_nv_battery_configuration_decode(",
        "r1_runtime_configure_battery(",
        "openr1_databases_zephyr_battery_configuration(",
        "R1_KV_RING_SIZE",
        "r1_nv_ring_size_decode(",
        "openr1_databases_zephyr_ring_size(",
    ):
        require(databases_source, needle,
                "Zephyr persisted temperature calibration")
    for needle in (
        "OPENR1_GXT310_REGISTER_TEMPERATURE UINT8_C(0x00)",
        "OPENR1_GXT310_REGISTER_ID UINT8_C(0x03)",
        "OPENR1_GXT310_EXPECTED_ID UINT8_C(0x50)",
        "OPENR1_GXT310_STARTUP_MS UINT32_C(80)",
        "OPENR1_GXT310_SAMPLE_INTERVAL_MS UINT32_C(5)",
        "SOFTWARE_TWI_BUS_I2C_2",
        "gxt310_enable_pair(&temperature_provider)",
        "r1_temperature_gxt310_decode_milliunits(bytes)",
        "r1_temperature_pair_reduce(",
        "r1_temperature_pair_stream_value(",
        "openr1_temperature_zephyr_read_stream(",
        "openr1_databases_zephyr_temperature_calibration(",
        "persisted_calibration_present ? &persisted_calibration : NULL",
        "provider_ready = true",
    ):
        require(temperature_source, needle, "Zephyr GXT310 temperature provider")
    for source in ("openr1_software_twi_zephyr.c",
                   "openr1_temperature_zephyr.c"):
        require(cmake, source, "Zephyr temperature source binding")
    optical_source = (BACKEND / "src" / "openr1_optical_zephyr.c").read_text()
    for needle in (
        "OPENR1_GOODIX_DEVICE_ID UINT8_C(0x28)",
        "openr1_software_twi_zephyr_open(",
        "openr1_software_twi_zephyr_write(",
        "openr1_software_twi_zephyr_read(",
        "openr1_software_twi_zephyr_close(",
        "(uint16_t)(((uint16_t)command[0] << 8u) | command[1])",
        "hal_gh3x2x_int_handler_call_back();",
        "k_work_submit(&optical_interrupt_work)",
        "Gh3x2xDemoInterruptProcess();",
        "GPIO_INT_EDGE_TO_ACTIVE",
        "openr1_yhm2710_zephyr_optical_acquire()",
        "openr1_yhm2710_zephyr_optical_release()",
        "r1_goodix_adapter_bind(",
        "r1_goodix_start_stock_profile(",
        "r1_goodix_switch_profile(",
        "r1_goodix_stop_stock_profiles(",
        "GPIO_OUTPUT_INACTIVE",
    ):
        require(optical_source, needle, "Zephyr source optical provider")
    goodix_stubs = (
        PROJECT / "port" / "goodix_gh3x2x" / "r1_gh3x2x_stubs.c").read_text()
    for function in ("GH3X2X_AlgoInit", "GH3X2X_AlgoDeinit",
                     "GH3X2X_AlgoCalculate"):
        match = re.search(
            rf"GS8\s+{function}\([^)]*\)\s*\{{.*?"
            r"return\s+GH3X2X_RET_RESOURCE_ERROR\s*;.*?\}",
            goodix_stubs, re.DOTALL)
        if match is None:
            raise AssertionError(f"Goodix global algorithm ABI is not fail-closed: {function}")

    bae8 = (BACKEND / "src" / "openr1_bae8_zephyr.c").read_text()
    for uuid in ("0xbae80001", "0xbae80010", "0xbae80011", "0xbae80012", "0xbae80013"):
        require(bae8, uuid, "BAE8 service")
    require(bae8, "r1_runtime_receive_eus(", "BAE8 channel-2 route")
    require(bae8, "Channel 1 remains fail-closed", "BAE8 channel-1 policy")
    require(bae8, "OPENR1_NOTIFICATION_SLOTS 4u", "completion-tracked notification pool")

    source_lock = package_source_lock()
    manifest = json.loads(MANIFEST.read_text())
    components = {component["id"]: component for component in manifest["components"]}
    for lock_name, component_id in SOURCE_IDS.items():
        if lock_name not in source_lock or component_id not in components:
            raise AssertionError(f"missing Zephyr source provenance: {lock_name}/{component_id}")
        lock = source_lock[lock_name]
        component = components[component_id]
        for field in ("commit", "tree"):
            if lock[field] != component[field]:
                raise AssertionError(f"source-lock drift: {lock_name}.{field}")
    for lock_name, specification in FILE_SOURCE_IDS.items():
        component_id = specification["component"]
        if lock_name not in source_lock or component_id not in components:
            raise AssertionError(f"missing file-source provenance: {lock_name}/{component_id}")
        lock = source_lock[lock_name]
        component = components[component_id]
        for field in specification.get(
                "lock_fields", ("commit", "archive_sha256")):
            if lock[field] != component[field]:
                raise AssertionError(f"source-lock drift: {lock_name}.{field}")
        for filename, manifest_field in specification["files"].items():
            if lock["files"][filename] != component[manifest_field]:
                raise AssertionError(
                    f"source-lock drift: {lock_name}.files.{filename}")

    readme = " ".join((BACKEND / "README.md").read_text().split())
    for phrase in (
        "not a production trust anchor",
        "sensor",
        "hardware-validated",
        "migration procedure",
    ):
        require(readme, phrase, "Zephyr limitations")
    print("openR1 Zephyr source boundary verified: 14 recovered modules, source BLE/boot/health-storage/optical-transport stack, no opaque input")


if __name__ == "__main__":
    main()
