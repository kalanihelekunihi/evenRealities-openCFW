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
    "goodix_hba_config.c",
    "goodix_hrv_config.c",
    "goodix_spo2_config_for_gh3x2x-v2.23_7ecd2a.c",
    "r1_gh3x2x_port.c",
    "r1_gh3x2x_bind.c",
    "r1_gh3x2x_provider_composer.c",
    "r1_gh3x2x_reconstructed_roots.c",
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
    require(boot, "CONFIG_MCUBOOT_ACTION_HOOKS=y", "MCUboot recovery configuration")
    require(boot, "CONFIG_BT=y", "MCUboot recovery Bluetooth configuration")
    require(boot, "CONFIG_BT_CTLR=y", "MCUboot recovery controller configuration")
    recovery_source = (BACKEND / "recovery_module" / "openr1_recovery.c").read_text()
    for needle in (
        "void mcuboot_status_change(",
        "MCUBOOT_STATUS_NO_BOOTABLE_IMAGE_FOUND",
        "FIXED_PARTITION_ID(slot0_partition)",
        "FIXED_PARTITION_ID(settings_partition)",
        "FIXED_PARTITION_ID(migration_reserve_partition)",
        "clean_opaque_regions()",
        "flash_area_erase(",
        "flash_area_write(",
        "OPENR1_RECOVERY_REQUEST",
    ):
        require(recovery_source, needle, "source BLE recovery loader")
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
    require(configuration, "CONFIG_COUNTER=y", "Zephyr RTC2 configuration")
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
    require(main_source, "openr1_storage_zephyr_structured_log_typed(",
            "Zephyr structured-log producer startup")
    require(main_source, "openr1_storage_zephyr_structured_log_service(",
            "Zephyr structured-log persistence service")
    require(main_source, "openr1_databases_zephyr_initialize(", "Zephyr database startup")
    require(main_source, "settings_load()", "Zephyr Bluetooth settings startup")
    require(main_source, "openr1_analog_zephyr_initialize()", "Zephyr SAADC startup")
    require(main_source, "openr1_reset_zephyr_initialize()", "Zephyr reset-reason startup")
    require(main_source, "openr1_watchdog_zephyr_initialize()", "Zephyr watchdog startup")
    require(main_source, "openr1_clock_zephyr_initialize(", "Zephyr wall-clock startup")
    require(main_source, "openr1_rtc_zephyr_initialize()", "Zephyr RTC2 startup")
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
    require(main_source, "openr1_battery_zephyr_initialize(",
            "Zephyr live battery startup")
    require(main_source, "openr1_temperature_zephyr_initialize()",
            "Zephyr GXT310 temperature startup")
    require(main_source, "openr1_optical_zephyr_initialize()",
            "Zephyr optical-provider startup")
    require(main_source, "openr1_health_results_zephyr_initialize(",
            "Zephyr checked optical-result health route startup")
    require(main_source, "openr1_gomore_zephyr_sync(",
            "Zephyr source-built GoMore engine reconciliation")
    require(main_source, "openr1_gomore_zephyr_poll(",
            "Zephyr source-built GoMore live topic consumption")
    require(main_source, "openr1_nfc_resources_zephyr_initialize()",
            "Zephyr NFC dock-resource startup")
    require(main_source, "r1_runtime_schedule_automatic_health_sync(",
            "Zephyr automatic health-sync scheduling")
    require(main_source, "r1_runtime_service_automatic_health_sync(",
            "Zephyr automatic health-sync service")
    require(main_source, "r1_runtime_set_touch_handler(",
            "Zephyr runtime touch-enable binding")
    clock_startup = main_source.find("openr1_clock_zephyr_initialize(")
    rtc_startup = main_source.find("openr1_rtc_zephyr_initialize()")
    database_startup = main_source.find("openr1_databases_zephyr_initialize(")
    if rtc_startup < 0 or clock_startup < rtc_startup or \
            database_startup < clock_startup:
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
    battery_startup = main_source.find("openr1_battery_zephyr_initialize(")
    optical_startup = main_source.find("openr1_optical_zephyr_initialize(")
    health_results_startup = main_source.find(
        "openr1_health_results_zephyr_initialize(")
    if yhm_startup < 0 or battery_startup < yhm_startup or \
            optical_startup < battery_startup:
        raise AssertionError(
            "Zephyr YHM2710 must initialize before battery and optical providers")
    if health_results_startup < optical_startup:
        raise AssertionError(
            "Zephyr optical provider must initialize before its health result route")
    if "openr1_optical_zephyr_start(" in main_source:
        raise AssertionError("Zephyr startup must not start optical sampling")
    storage_source = (BACKEND / "src" / "openr1_storage_zephyr.c").read_text()
    require(storage_source, "FIXED_PARTITION_ID(openr1_data_partition)",
            "Zephyr product-storage partition binding")
    require(storage_source, "flash_area_write", "Zephyr source flash provider")
    for needle in (
        'r1_storage_partition("ep.bin")',
        "r1_ep_plan_initialization(",
        "r1_ep_scan_flash_cursor(",
        "openr1_storage_zephyr_ep_scan(",
        'r1_storage_partition("log.bin")',
        "r1_log_bin_initialize(",
        "openr1_storage_zephyr_log_append(",
        "openr1_storage_zephyr_log_sector_count(",
        "r1_structured_log_cache_initialize(",
        "r1_structured_log_encode_typed(",
        "r1_structured_log_encode_format(",
        "r1_structured_log_periodic_persist(",
        "openr1_storage_zephyr_structured_log_service(",
        "r1_log_export_snapshot_prepare(",
        "r1_log_export_snapshot_read(",
        "r1_log_export_snapshot_finish(",
        "openr1_storage_zephyr_diagnostic_export_begin(",
        "openr1_storage_zephyr_diagnostic_export_read(",
        "openr1_storage_zephyr_diagnostic_export_finish(",
    ):
        require(storage_source, needle,
                "Zephyr product-storage and structured-log binding")

    require(cmake, "src/openr1_battery_zephyr.c",
            "Zephyr live battery source binding")
    battery_source = (BACKEND / "src" / "openr1_battery_zephyr.c").read_text()
    require(battery_source, "openr1_databases_zephyr_battery_configuration(",
            "Zephyr persisted battery compensation input")
    require(battery_source, "openr1_yhm2710_zephyr_charge_state(",
            "Zephyr live charge-state input")
    require(battery_source, "openr1_analog_zephyr_update_runtime_battery(",
            "Zephyr live battery runtime update")
    require(battery_source, "R1_SYSTEM_SUBCOMMAND_DEVICE_STATUS",
            "Zephyr recovered status-access refresh")
    require(battery_source, "(request->status & UINT8_C(0x02)) == 0u",
            "Zephyr read-only status-access gate")
    require(battery_source, "r1_runtime_set_request_observer(",
            "Zephyr pre-dispatch battery observer binding")
    require(battery_source, "(void)openr1_battery_zephyr_refresh();",
            "Zephyr boot battery seed")
    yhm_source = (BACKEND / "src" / "openr1_yhm2710_zephyr.c").read_text()
    require(yhm_source, "yhm2710_register_read_byte(",
            "Zephyr YHM2710 live status read")
    require(yhm_source, "UINT8_C(6)", "Zephyr YHM2710 charge register")
    require(yhm_source, "return -EIO;", "Zephyr YHM2710 fail-closed read")
    runtime_source = (PROJECT / "src" / "r1_runtime.c").read_text()
    dispatch_header = (PROJECT / "include" / "openr1" / "r1_dispatch.h").read_text()
    require(dispatch_header, "R1_DISPATCH_RESPONSE_MAX 32u",
            "worst-case scalar-history dispatch capacity")
    require(dispatch_header, "R1_DISPATCH_FRAGMENT_MAX 50u",
            "atomic shared-EUS fragment capacity")
    require(dispatch_header, "R1_DISPATCH_ARENA_MAX",
            "fragment-bounded packed dispatch arena")
    require(dispatch_header, "uint8_t arena[R1_DISPATCH_ARENA_MAX]",
            "dispatch arena storage")
    dispatch_source = (PROJECT / "src" / "r1_dispatch.c").read_text()
    require(dispatch_source, "reserve_response_model(",
            "bounded dispatch-arena reservation")
    require(dispatch_source, "remove_last_response(",
            "atomic dispatch-arena rollback")
    observer_position = runtime_source.find("runtime->request_observer(")
    dispatch_position = runtime_source.find(
        "const r1_error dispatch_error = r1_dispatch(", observer_position)
    if observer_position < 0 or dispatch_position < observer_position:
        raise AssertionError(
            "runtime request observer must execute before dispatch snapshots state")
    health_settings_callback = runtime_source.find(
        "runtime->health_settings_handler(")
    acknowledgement_enqueue = runtime_source.find(
        "error = enqueue_dispatch(runtime, connection);")
    if acknowledgement_enqueue < 0 or \
            health_settings_callback < acknowledgement_enqueue:
        raise AssertionError(
            "health-settings platform effects must follow acknowledgement enqueue")

    dts = (BACKEND / "boards" / "openr1" / "openr1_nrf52840" /
           "openr1_nrf52840.dts").read_text()
    expected_partitions = {
        "mcuboot": (0x00000000, 0x00027000),
        "image-0": (0x00027000, 0x000AA000),
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
        "&rtc2 {",
        "prescaler = <4095>;",
        "interrupts = <36 6>;",
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
    require(cmake, "openr1_rtc_zephyr.c", "Zephyr RTC2 source binding")
    require(cmake, "openr1_rtc_service.c", "Zephyr RTC/registry composition binding")
    clock_source = (BACKEND / "src" / "openr1_clock_zephyr.c").read_text()
    require(clock_source, "OPENR1_CLOCK_CADENCE_TICKS 1024u",
            "Zephyr recovered wall-clock cadence")
    require(clock_source, "r1_clock_synchronize(", "Zephyr wall-clock adoption")
    require(clock_source, "time_calendar_unix_to_broken_down(",
            "Zephyr reconstructed calendar provider")
    require(clock_source, "openr1_rtc_zephyr_adopt_phone_time(",
            "Zephyr reconstructed RTC phone-time adoption")
    rtc_source = (BACKEND / "src" / "openr1_rtc_zephyr.c").read_text()
    for needle in (
        "DEVICE_DT_GET(DT_NODELABEL(rtc2))",
        "OPENR1_RTC_PRESCALER 4095u",
        "OPENR1_RTC_IRQ_PRIORITY 6u",
        "counter_set_channel_alarm(",
        "counter_start(",
        "openr1_rtc_service_initialize(",
        "openr1_rtc_service_set_time(",
        "openr1_rtc_service_snapshot(",
    ):
        require(rtc_source, needle, "Zephyr reconstructed RTC2 service")
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
    storage_core = (PROJECT / "src" / "r1_storage.c").read_text()
    kv_core = (PROJECT / "src" / "r1_kv_store.c").read_text()
    nv_recovery_core = (PROJECT / "src" / "r1_nv_recovery.c").read_text()
    peer_target_core = (PROJECT / "src" / "r1_peer_target.c").read_text()
    sleep_core = (PROJECT / "src" / "r1_sleep_db.c").read_text()
    deployment_tool = (
        PROJECT / "tools" / "prepare_zephyr_deployment.py").read_text()
    deployment_verifier = (
        PROJECT / "tools" / "verify_zephyr_deployment.py").read_text()
    swd_deployer = (
        PROJECT / "tools" / "deploy_zephyr_swd.py").read_text()
    recovery_assembler = (
        PROJECT / "tools" / "assemble_r1_ace_recovery.py").read_text()
    for needle in (
        "r1_memory_flash_fail_after_bytes(",
        "byte_mutation_allowed(",
    ):
        require(storage_core, needle, "byte-granular flash fault injection")
    for needle in (
        "snapshot_valid(store, target, &verified)",
        "verified_generation != generation",
    ):
        require(kv_core, needle, "kv.bin commit readback verification")
    for needle in (
        "r1_nv_recovery_store_load(",
        "r1_nv_recovery_store_merge_commit(",
        "store->dirty[R1_KV_NV_R1] = false",
    ):
        require(nv_recovery_core, needle,
                "transactional local NV recovery")
    for needle in (
        "openr1_databases_zephyr_apply_local_nv_recovery(",
        "r1_nv_recovery_store_merge_commit(",
        "k_mutex_lock(&kv_mutex, K_FOREVER)",
    ):
        require(databases_source, needle,
                "Zephyr local NV recovery binding")
    for needle in (
        "r1_remove_ring_clear_connected_flag(",
        "r1_remove_ring_clear_peer_slots(",
        "r1_remove_ring_metadata_commit(",
        "r1_kv_store_commit(store)",
    ):
        require(peer_target_core, needle,
                "transactional remove-ring metadata composition")
    for needle in (
        "openr1_databases_zephyr_remove_ring_metadata(",
        "r1_remove_ring_metadata_commit(&kv_store)",
        "k_mutex_lock(&kv_mutex, K_FOREVER)",
    ):
        require(databases_source, needle,
                "Zephyr remove-ring metadata binding")
    bae8_source = (BACKEND / "src" / "openr1_bae8_zephyr.c").read_text()
    for needle in (
        "remove_ring_work_handler(",
        "queue_remove_ring(",
        "r1_runtime_set_remove_ring_handler(",
        "atomic_inc(&remove_ring_failures)",
        "openr1_bae8_zephyr_remove_ring_failures(",
    ):
        require(bae8_source, needle,
                "Zephyr bounded remove-ring worker")
    for needle in (
        "R1_SLEEP_DB_RECORD_RESERVED",
        "R1_SLEEP_DB_RECORD_COMMITTED",
        "discard_torn_sector(",
        "db_range_erased(",
    ):
        require(sleep_core, needle, "failure-atomic sleep journal")
    for needle in (
        "openr1-offline-deployment-preflight",
        "mass_erase_forbidden",
        "openr1-internal-flash-recovery.hex",
        "openr1-expected-internal-flash.bin",
        "openr1-uicr-backup.bin",
        "openr1-uicr-recovery.hex",
        "post_install_readback_required",
        "uicr_erase_before_restore_required",
        "return [[0, DATA_START], [DATA_LIMIT, FLASH_LIMIT]]",
        "classify_first_install_settings(",
        "FDS_PAGE_MAGIC = 0xDEADC0DE",
        "settings preflight found an interrupted retail FDS layout",
        "reset_held_until_readback_verified",
        '"retail_credentials_imported": False',
        "unaddressed_install_bytes_must_be_erased",
        "validate_backup_provenance(",
        "live ACE page provenance differs at",
        "verify_bundle(",
    ):
        require(deployment_tool, needle, "offline deployment preflight")
    for needle in (
        "source-proven-mbr-config",
        "pinned-official-reconstruction",
        "live-ace-page-readback",
        "live_application != application",
        "live_bootloader != bootloader",
        "MBR_CONFIG_START = 0xFF8",
    ):
        require(recovery_assembler, needle,
                "mixed-provenance ACE recovery assembly")
    for needle in (
        "build_expected_internal_flash(",
        "verify_deployment_package(",
        "recovery HEX is not the canonical backup encoding",
        "UICR recovery HEX is not the canonical backup encoding",
        "deployment plan differs from verified bundle and backup",
        "post-install readback differs at",
        "post-install UICR readback differs at",
        "verify_recovery_readback(",
        "post-recovery readback differs at",
        "post-recovery UICR readback differs at",
    ):
        require(deployment_verifier, needle,
                "offline deployment readback verification")
    for needle in (
        '"auto_unlock": False',
        '"chip_erase": "sector"',
        '"resume_on_disconnect": False',
        '"connect_mode": "under-reset"',
        "FICR_PART_ADDRESS = 0x10000100",
        "NVMC_ERASEPAGE = 0x4001E508",
        "NVMC_ERASEUICR = 0x4001E514",
        "nvmc_sector_erase(",
        "nvmc_program(",
        "execute_recovery_session(",
        "validate_recovery_contract(",
        "non_erased_chunks(",
        "pre-install internal flash",
        "post-install internal flash",
        "post-install UICR",
        "pre-recovery installed flash",
        "post-recovery internal flash",
        "verify_recovery_readback(",
        "nvmc_restore_uicr(",
        "validate_uicr_confirmation(",
        "UICR did not read back erased before restoration",
        "target.reset()",
        "mass_erase_used\": False",
        "uicr_written\": False",
    ):
        require(swd_deployer, needle,
                "fail-closed sector-bounded SWD deployment")
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
        "health_gomore_reinitializations",
        "health_gomore_reinitialization_failures",
        "r1_runtime_set_health_settings_handler(",
        "r1_health_settings_store_dev_info(",
        "plan->persistent_update_requested",
        "plan->private_event_publish_requested",
        "health_settings_updates_persisted",
        "health_settings_update_failures",
        "R1_KV_HSYNC",
        "r1_health_sync_cursor_decode(",
        "r1_health_reconcile_sync_cursors(",
        "r1_health_sync_cursor_encode(",
        "r1_health_bind_scalar_history_query(",
        "r1_health_bind_hrv_history_query(",
        "r1_health_bind_activity_history_query(",
        "r1_health_bind_sync_cursor_commit(",
        "r1_health_u8_flash_record_merge(",
        "r1_health_u8_offline_merge(",
        "r1_health_u8_ram_cache_merge(",
        "r1_health_u16_flash_record_merge(",
        "r1_health_u16_offline_merge(",
        "r1_health_u16_ram_cache_merge(",
        "r1_activity_flash_record_merge(",
        "r1_activity_offline_merge(",
        "r1_activity_ram_cache_merge(",
        "R1_HEALTH_HISTORY_FLASH_WINDOW_SECONDS",
        "R1_HEALTH_ACK_FLASH_HISTORY",
        "R1_HEALTH_ACK_CURRENT_RAM",
        "scalar_history_flash_record",
        "hrv_history_flash_record",
        "activity_history_flash_record",
        "query.error == R1_ERROR_CAPACITY",
        "health_execute_storage_notification(",
        "r1_runtime_schedule_automatic_health_sync(",
        "r1_runtime_service_automatic_health_sync(runtime)",
        "health_commit_scalar_sync_cursor",
        "health_cursor_updates_persisted",
        "health_cursor_update_failures",
        "K_MUTEX_DEFINE(kv_mutex)",
        "openr1_databases_zephyr_multicast_time_transition",
        "r1_activity_cache_reset(",
        "r1_health_u8_cache_reset(",
        "r1_health_u16_cache_reset(",
        "openr1_databases_zephyr_multicast_hour",
        "r1_nv_product_serial_decode(",
        "r1_nv_factory_mode_decode(",
        "openr1_databases_zephyr_product_serial(",
        "openr1_databases_zephyr_factory_mode(",
        "memcpy(runtime->device.serial_number, product_serial",
        "recovery_records_decoded",
        "recovery_records_restored",
        "recovery_records_rejected",
        "R1_HEALTH_DB_STARTUP_COMPLETED",
        "retained_health_crash_record __noinit",
        "r1_health_crash_record_clear_provider_blob(",
        "r1_health_crash_record_initialize(",
        "provider_blob_copied) != R1_OK || provider_blob_copied",
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
        "health_reinitialize_gomore",
        "openr1_gomore_zephyr_reinitialize(health_context.runtime)",
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
        "openr1_gomore_zephyr.c",
    ):
        require(cmake, needle, "Zephyr pinned motion source binding")
    motion_source = (BACKEND / "src" / "openr1_motion_zephyr.c").read_text()
    for needle in (
        "openr1_twim1_zephyr_write_read(",
        "openr1_twim1_zephyr_write(",
        "OPENR1_MOTION_I2C_ADDRESS UINT8_C(0x18)",
        '"qma6100/qma6100.h"',
        "QMA6100_ADDRESS_1, QMA6100_ADDRESS_2",
        "qma6100_initialize(&qma_device, &qma_bindings)",
        "R1_MOTION_VARIANT_QMA6100,",
        "qma6100_interrupt_wrapper(&qma_device)",
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
        "gomore_primitives_topic_raw_optical_ingest(",
        "gomore_primitives_topic_heart_rate_ingest(",
        "gomore_primitives_topic_hrv_ingest(",
        "K_MUTEX_DEFINE(gomore_topic_mutex)",
        "openr1_sensor_stream_zephyr_gomore_consume_ready(",
        "gomore_primitives_topic_update_take_ready(",
        "gomore_primitives_topic_update_complete(",
        "gomore_primitives_authorization_dispatch(",
        "openr1_sensor_stream_zephyr_gomore_active_slot_mask(",
        "dependency_masks[GOMORE_PRIMITIVES_RECORD_COUNT]",
        "UINT8_C(0x02), UINT8_C(0x1e), UINT8_C(0x1e), UINT8_C(0x02)",
        "UINT8_C(0x04), UINT8_C(0x0c), UINT8_C(0x00)",
        "const uint32_t slots[2] = {0u, 3u}",
        "openr1_sensor_stream_zephyr_goodix_raw_hr_append(",
        "openr1_optical_zephyr_start_functions(",
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
        "algo_params/HR/04_EXCLUSIVE/goodix_hba_config.c",
        "algo_params/goodix_hrv_config.c",
        "goodix_spo2_config_for_gh3x2x-v2.23_7ecd2a.c",
        "r1_gh3x2x_bind.c",
        "r1_gh3x2x_provider_composer.c",
        "r1_gh3x2x_reconstructed_roots.c",
        "r1_gh3x2x_stubs.c",
        "openr1_optical_zephyr.c",
        "openr1_health_results_zephyr.c",
        "openr1_gomore_zephyr.c",
        "openr1_goodix.ld",
    ):
        require(cmake, needle, "Zephyr pinned Goodix source binding")
    goodix_linker = (BACKEND / "openr1_goodix.ld").read_text()
    for source in GOODIX_PROVIDER_OBJECTS:
        require(goodix_linker, f"*{source}.obj", "Zephyr Goodix linker retention corpus")
    require(goodix_linker,
            "r1_gh3x2x_stubs.c.obj(.text .text.* .rodata .rodata.* .openr1_goodix_api)",
            "Zephyr named Goodix API retention")
    if goodix_linker.count("KEEP(*") != len(GOODIX_PROVIDER_OBJECTS):
        raise AssertionError("Zephyr Goodix linker corpus size differs from its source inventory")
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
    goodix_bridge = (
        PROJECT / "port" / "goodix_gh3x2x" /
        "r1_gh3x2x_algo_bridge.h").read_text()
    goodix_primitive_adapter = (
        PROJECT / "port" / "goodix_gh3x2x" /
        "r1_gh3x2x_primitive_adapter.h").read_text()
    goodix_composer = (
        PROJECT / "port" / "goodix_gh3x2x" /
        "r1_gh3x2x_provider_composer.c").read_text()
    goodix_roots = (
        PROJECT / "port" / "goodix_gh3x2x" /
        "r1_gh3x2x_reconstructed_roots.c").read_text()
    for needle in (
        "R1_GH3X2X_ALGO_FUNCTION_COUNT 20u",
        "R1_GH3X2X_ALGO_RESULT_COUNT 16u",
        "R1_GH3X2X_ALGO_FUNCTION_HR 1u",
        "R1_GH3X2X_ALGO_FUNCTION_HRV 2u",
        "R1_GH3X2X_ALGO_FUNCTION_HSM 3u",
        "R1_GH3X2X_ALGO_FUNCTION_SPO2 6u",
        "r1_gh3x2x_algo_frame",
        "r1_gh3x2x_algo_result",
        "r1_gh3x2x_algo_input",
        "R1_GH3X2X_ALGO_INPUT_CHANNELS 12u",
        "r1_gh3x2x_algo_prepare_hr_input",
        "r1_gh3x2x_algo_prepare_hr_mapped_input",
        "r1_gh3x2x_algo_prepare_hrv_input",
        "r1_gh3x2x_algo_prepare_spo2_input",
        "r1_gh3x2x_algo_hr_default_channel_map",
        "r1_gh3x2x_algo_spo2_default_channel_map",
        "supported_functions",
        "r1_gh3x2x_algo_bind_provider",
        "r1_gh3x2x_algo_bind_result_observer",
        "r1_gh3x2x_algo_bind_frame_observer",
    ):
        require(goodix_bridge, needle, "Goodix normalized algorithm ABI")
    for needle in (
        "_Static_assert(GH3X2X_FUNC_OFFSET_MAX",
        "_Static_assert(GH3X2X_ALGO_RESULT_MAX_NUM",
        "_Static_assert(GH3X2X_FUNC_OFFSET_HR",
        "_Static_assert(GH3X2X_FUNC_OFFSET_HRV",
        "_Static_assert(GH3X2X_FUNC_OFFSET_HSM",
        "_Static_assert(GH3X2X_FUNC_OFFSET_SPO2",
        "gh3x2x_bridge_frame(",
        "gh3x2x_bridge_input_base(",
        "source == UINT8_MAX",
        "source >= frame->channel_count",
        "static const uint8_t recovered[R1_GH3X2X_ALGO_INPUT_CHANNELS]",
        "result.value_count !=",
        "gh3x2x_bridge_population(result.value_mask)",
        "GH3X2X_RET_RESOURCE_ERROR",
        "GH3X2X_RET_PARAMETER_ERROR",
        "g_algo_provider.write_virtual_register",
        "g_result_observer(",
        "g_frame_observer(",
    ):
        require(goodix_stubs, needle, "Goodix checked global algorithm bridge")
    for needle in (
        "goodix_primitives_hba_process_input",
        "goodix_primitives_hrv_process_input",
        "goodix_primitives_spo2_calc_input",
        "r1_gh3x2x_algo_bind_hr_primitive_input",
        "r1_gh3x2x_algo_bind_hrv_primitive_input",
        "r1_gh3x2x_algo_bind_spo2_primitive_input",
    ):
        require(goodix_primitive_adapter, needle,
                "Goodix reconstructed primitive input adapter")
    for needle in (
        "R1_GH3X2X_HR_RESULT_MASK",
        "R1_GH3X2X_HRV_RESULT_MASK",
        "R1_GH3X2X_SPO2_RESULT_MASK",
        "r1_gh3x2x_algo_hr_default_channel_map(",
        "r1_gh3x2x_algo_prepare_hr_mapped_input(",
        "r1_gh3x2x_algo_prepare_hrv_input(",
        "r1_gh3x2x_algo_spo2_default_channel_map(",
        "r1_gh3x2x_algo_prepare_spo2_input(",
        "composer->last_hr = (uint8_t)public_output[0]",
        "result->values[6] = result->values[0]",
        "result->values[7] = 0",
        "r1_gh3x2x_provider_composer_build(",
    ):
        require(goodix_composer, needle,
                "Goodix recovered wrapper provider composer")
    for needle in (
        "goodix_primitives_hba_process(",
        "goodix_primitives_hrv_process(",
        "goodix_primitives_spo2_calc(",
        "root_words[12] != 1u",
        "output[1] = signed_word(root_words[11])",
        "output[2] = diagnostic * 100",
        "goodix_primitives_build_hr_version(",
        "goodix_primitives_build_hrv_version(",
        "goodix_primitives_build_spo2_version(",
        "r1_gh3x2x_make_hba_root_binding(",
        "r1_gh3x2x_make_hrv_root_binding(",
        "r1_gh3x2x_make_spo2_root_binding(",
    ):
        require(goodix_roots, needle,
                "Goodix reconstructed root executor")

    health_results_source = (
        BACKEND / "src" / "openr1_health_results_zephyr.c").read_text()
    for needle in (
        "R1_GH3X2X_ALGO_FUNCTION_HR",
        "R1_GH3X2X_ALGO_FUNCTION_SPO2",
        "result_has_fields(",
        "UINT16_C(0x000b)",
        "UINT16_C(0x003f)",
        "r1_hr_once_result_plan(",
        "r1_spo2_once_result_plan(",
        "openr1_databases_zephyr_consume_heart_rate_event(",
        "openr1_databases_zephyr_consume_spo2_event(",
        "openr1_databases_zephyr_consume_hrv_event(",
        "openr1_sensor_stream_zephyr_goodix_hrv_update(",
        "R1_GH3X2X_ALGO_FUNCTION_HSM",
        "frame->raw_values[0]",
        "r1_gh3x2x_algo_bind_result_observer(",
        "r1_gh3x2x_algo_bind_frame_observer(",
    ):
        require(health_results_source, needle,
                "Zephyr checked Goodix health result route")

    gomore_source = (
        BACKEND / "src" / "openr1_gomore_zephyr.c").read_text()
    for needle in (
        "OPENR1_GOMORE_ENGINE_BYTES 0x39E0u",
        "OPENR1_GOMORE_PREVIOUS_BYTES 0x2E0u",
        "OPENR1_GOMORE_PKEY_OFFSET 0xA000u",
        "OPENR1_GOMORE_RETRY_MILLISECONDS 5000u",
        "gomore_primitives_iir_low_high_coefficients(",
        "gomore_primitives_iir_bandpass_coefficients(",
        ".age_years = 28.0f",
        ".height_centimeters = 175.0f",
        ".weight_kilograms = 75.0f",
        ".seed_random = srand",
        ".random_value = rand",
        "gomore_primitives_sleep_algorithm_initialize(",
        "gomore_primitives_previous_state_restore(",
        "gomore_primitives_previous_state_append(",
        "r1_crc32_castagnoli(&header[8], 64u)",
        "header[index] != UINT8_MAX",
        "engine authorization does",
        "runtime->device.health_settings[4] != 0u",
        "profile_matches(",
        "gomore_release(false);",
        "k_calloc(1u, OPENR1_GOMORE_ENGINE_BYTES)",
        "OPENR1_GOMORE_SLEEP_BELOW_DESCRIPTOR_ADDRESS",
        "OPENR1_GOMORE_SLEEP_UPPER_DESCRIPTOR_ADDRESS",
        "gomore_sleep_model_bind(",
        "gomore_primitives_output_orchestrate(",
        "gomore_primitives_host_input_adapter_update(",
        "gomore_primitives_sensor_update_orchestrate(",
        "gomore_primitives_copy_algorithm_output_snapshot(",
        "openr1_sensor_stream_zephyr_gomore_consume_ready(",
        "gomore_primitives_output_lifecycle_dispatch(",
        "openr1_sensor_stream_zephyr_gomore_active_slot_mask(",
        "openr1_sensor_stream_zephyr_gomore_authorization_set(",
        "openr1_databases_zephyr_consume_activity_cumulative(",
        "gomore_primitives_final_sleep_build(",
        "gomore_primitives_final_sleep_record_serialize(",
        "openr1_databases_zephyr_consume_sleep_record(",
        "gomore_primitives_update_failure_counter(",
        "openr1_gomore_zephyr_reinitialize(",
        "gomore_state.force_fresh_previous = true",
    ):
        require(gomore_source, needle,
                "Zephyr transparent GoMore engine initialization")
    for stage in (
        "GOMORE_PRIMITIVES_OUTPUT_STAGE_RESPIRATORY_RATE",
        "GOMORE_PRIMITIVES_OUTPUT_STAGE_LOCOMOTION_PREPROCESS",
        "GOMORE_PRIMITIVES_OUTPUT_STAGE_MOTION_CLASSIFIER",
        "GOMORE_PRIMITIVES_OUTPUT_STAGE_SPS_CANDIDATE",
        "GOMORE_PRIMITIVES_OUTPUT_STAGE_SPS_SELECT",
        "GOMORE_PRIMITIVES_OUTPUT_STAGE_SLEEP_MOTION",
        "GOMORE_PRIMITIVES_OUTPUT_STAGE_HEART_RATE_SELECT",
        "GOMORE_PRIMITIVES_OUTPUT_STAGE_ENERGY",
        "GOMORE_PRIMITIVES_OUTPUT_STAGE_DORMANT_ESTIMATOR",
        "GOMORE_PRIMITIVES_OUTPUT_STAGE_MOTION_GATE",
        "GOMORE_PRIMITIVES_OUTPUT_STAGE_SLEEP_CYCLE",
        "GOMORE_PRIMITIVES_OUTPUT_STAGE_SLEEP_OPTICAL_PEAK",
        "GOMORE_PRIMITIVES_OUTPUT_STAGE_SLEEP_STREAM",
        "GOMORE_PRIMITIVES_OUTPUT_STAGE_ACTIVITY_WINDOW",
        "GOMORE_PRIMITIVES_OUTPUT_STAGE_STEP_ACCUMULATE",
        "GOMORE_PRIMITIVES_OUTPUT_STAGE_ACTIVITY_ACCUMULATE",
    ):
        require(gomore_source, stage,
                "Zephyr complete GoMore output-stage binding")
    for needle in (
        "R1_DEV_INFO_HEALTH_TIMESTAMP_OFFSET",
        "R1_DEV_INFO_HEALTH_FLAG_MASK",
        "openr1_databases_zephyr_consume_heart_rate_event(",
        "openr1_databases_zephyr_consume_spo2_event(",
        "openr1_databases_zephyr_consume_hrv_event(",
        "r1_heart_rate_store_sample(",
        "r1_spo2_store_sample(",
        "r1_hrv_store_sample(",
        "r1_activity_accumulator_periodic(",
        "r1_activity_consume_delta_event(",
        "r1_sleep_decode_compact(",
        "r1_sleep_plan_validated_delivery(",
        "r1_sleep_persist_tracked(",
        "r1_sleep_store(",
        "r1_sleep_restore(",
        "r1_health_bind_sleep_sync_commit(",
    ):
        require(databases_source, needle,
                "Zephyr persisted health gate and scalar storage edges")

    bae8 = (BACKEND / "src" / "openr1_bae8_zephyr.c").read_text()
    for uuid in ("0xbae80001", "0xbae80010", "0xbae80011", "0xbae80012", "0xbae80013"):
        require(bae8, uuid, "BAE8 service")
    require(bae8, "r1_runtime_receive_eus(", "BAE8 channel-2 route")
    for marker in (
        "r1_legacy_command_route_frame(",
        "route != R1_LEGACY_COMMAND_ROUTE_0X89",
        "r1_runtime_receive_glasses_status(",
        "openr1_power_zephyr_set_reg1(false)",
        "openr1_power_zephyr_set_reg1(true)",
        "OPENR1_TOUCH_ZEPHYR_SOURCE_WEAR",
        "BT_LE_CONN_PARAM_INIT(16u, 16u, 2u, 600u)",
        "BT_LE_CONN_PARAM_INIT(72u, 84u, 4u, 600u)",
        "bt_conn_le_param_update(",
        "K_TICKS(plan.ble_slow_delay_ticks)",
        "glasses_connection_slow_work_handler",
        "transmit_event(&response, false)",
    ):
        require(bae8, marker,
                "BAE8 bounded authorized channel-1 glasses-status policy")
    require(bae8, "OPENR1_NOTIFICATION_SLOTS 4u", "completion-tracked notification pool")
    require(bae8, "openr1_databases_zephyr_product_serial(",
            "persisted product serial advertising binding")
    require(bae8, "R1_NV_PRODUCT_SERIAL_BYTES : 0u",
            "optional fixed-width product serial manufacturer data")
    for marker in (
        "SETTINGS_STATIC_HANDLER_DEFINE(",
        "OPENR1_OWNER_SETTINGS_KEY",
        "r1_owner_authorization_state_load(",
        "r1_owner_authorization_state_matches(",
        "r1_owner_authorization_state_reset(",
        "settings_save_one(",
        "bt_foreach_bond(",
        "bt_conn_auth_info_cb_register(",
        "openr1_bae8_zephyr_revoke_owner(",
        "r1_runtime_connection_is_authorized_phone(",
        "openr1_bae8_zephyr_diagnostic_export_begin(",
        "openr1_bae8_zephyr_diagnostic_export_read(",
        "openr1_bae8_zephyr_diagnostic_export_finish(",
        "diagnostic_export_abort(",
    ):
        require(bae8, marker, "independent persisted owner authorization")
    if "secure, secure, secure" in bae8:
        raise AssertionError(
            "BAE8 transport security must not grant product authorization")
    for marker in (
        "OPENR1_FAST_INTERVAL UINT16_C(0x00a0)",
        "OPENR1_SLOW_INTERVAL UINT16_C(0x0640)",
        "OPENR1_FAST_DURATION_SECONDS 60u",
        "static const char suffix[] = \"_FAC\"",
        "openr1_databases_zephyr_factory_mode()",
        "k_work_init_delayable(",
        "both_product_roles_occupied(",
        "r1_runtime_connection_role(runtime, connection)",
    ):
        require(bae8, marker, "Zephyr recovered advertising lifecycle")

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
        "OPENR1-RECOVERY",
        "former retail bootloader/settings window",
    ):
        require(readme, phrase, "Zephyr limitations")
    print("openR1 Zephyr source boundary verified: 14 recovered families plus live target composition, source BLE/boot/health-storage/optical stack, no opaque input")


if __name__ == "__main__":
    main()
