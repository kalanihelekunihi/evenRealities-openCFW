#!/usr/bin/env python3
"""Fail closed unless every canonical R1 production surface has a ledger disposition.

This verifier composes the existing read-only firmware parsers. It never connects to a ring,
publishes an internal event, reads personal data, contacts a vendor service, or mutates firmware.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import struct
import sys
from collections import Counter
from pathlib import Path
from typing import Any

import summarize_r1_adc_registry as adc
import summarize_r1_bus_registry as bus
import summarize_r1_factory_table as factory
import summarize_r1_flash_layout as flash
import summarize_r1_gpio_registry as gpio
import summarize_r1_internal_events as events


IMAGE_SHA256 = "0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a"
SYSTEM_TABLE_ADDRESS = 0x0009_A4CC
SYSTEM_ENTRY_COUNT = 20
HEALTH_TABLE_ADDRESS = 0x0009_A454
HEALTH_ENTRY_COUNT = 14
PROTOCOL_RECORD_BYTES = 8
TESTABLE_REGISTRATION_ADDRESS = 0x0009_A588

# These phrases described transient workspace failures that no longer exist. Keeping them in the
# capability ledger would make the residual-gap audit claim work remains blocked after a clean
# whole-workspace build has succeeded.
STALE_LEDGER_BUILD_MARKERS = (
    "missing SettingsHealthDataView",
    "RoutinesHomeView build errors",
    "RoutinesHomeView errors",
    "actor-isolation build errors",
    "aggregate runner",
)

# Each of these rows originally named a later static implementation or workspace-repair task in
# `next_gate`. Later ledger rows or verified whole-workspace builds now close those tasks. Their
# only honest remaining gates are physical/cross-version validation and semantic naming from
# legitimate captures.
SUPERSEDED_STATIC_NEXT_GATE_MARKERS: dict[str, tuple[str, ...]] = {
    "R1-129": ("Implement the exact descriptor-driven",),
    "R1-135": ("Continue from the exact200-sample",),
    "R1-136": ("Recover and validate autocorrelation",),
    "R1-137": ("Recover 200-sample crossing estimator",),
    "R1-138": ("Feed the now-complete62-byte",),
    "R1-152": ("Close all remaining",),
    "R1-153": ("Compose and production-bit-match", "then close"),
    "R1-154": ("Close and production-bit-match", "then compose"),
    "R1-155": ("Close finalizer", "then compose"),
    "R1-156": ("Close coefficient builder", "then compose"),
    "R1-157": ("Close coefficient builder", "then compose"),
    "R1-158": ("Close alternate solver", "then compose"),
    "R1-159": ("Close finalizer", "compose both complete"),
    "R1-160": ("Compose targets", "close their remaining"),
    "R1-163": ("Compose scheduler", "for full capture replay"),
    "R1-178": ("resolve the unrelated test-target drift",),
    "R1-179": ("resolve unrelated workspace test drift",),
    "R1-192": ("Recover exact userInfo and nvRecover phone responders next",),
}

RESIDUAL_CLOSURE_CAPABILITY = "R1-197"

# Public names containing "unresolved" are intentional product boundaries, not free-form TODOs.
# Count and map every one so a newly exposed opaque field cannot silently bypass the ledger.
UNRESOLVED_PUBLIC_SYMBOL_CAPABILITIES: dict[
    str, tuple[int, tuple[str, ...]]
] = {
    "unresolvedPrefix": (1, ("R1-109",)),
    "unresolvedTail": (2, ("R1-109",)),
    "unresolvedSettingsFlagBits": (1, ("R1-109",)),
    "unresolvedTimestampOffset8Raw": (1, ("R1-109",)),
    "unresolvedTimestampOffset20Raw": (1, ("R1-109",)),
    "healthSyncUnresolvedOffsets": (1, ("R1-109",)),
    "unresolvedHealthSyncCursorByteOffsets": (1, ("R1-113",)),
    "unresolvedSlot2": (1, ("R1-115",)),
    "unresolvedSlot6": (1, ("R1-115",)),
    "unresolved": (1, ("R1-122",)),
    "exactConstantPurposeUnresolved": (1, ("R1-122",)),
    "reciprocalPaceSecondsPerUnresolvedDistanceUnit": (1, ("R1-134",)),
    "unresolvedAuxiliaryRawBits": (1, ("R1-145",)),
    "unresolvedAuxiliary": (1, ("R1-145",)),
    "unresolvedAuxiliaryInputOffsets": (1, ("R1-145",)),
    "stockUnresolvedAuxiliaryRawBits": (1, ("R1-145",)),
    "unresolvedAuxiliaryHasPostInitializerWriter": (1, ("R1-145",)),
}

# "Unknown" enum cases are normally forward-compatibility values rather than open research gaps,
# but they are still public generic boundaries. Pin them separately from the explicitly unresolved
# semantic fields above.
UNKNOWN_PUBLIC_SYMBOL_CAPABILITIES: dict[
    str, tuple[int, tuple[str, ...]]
] = {
    "unknown": (
        6,
        ("R1-001", "R1-006", "R1-007", "R1-055", "R1-060", "R1-111"),
    ),
    "unknownSystem83HandlerAddress": (1, ("R1-185",)),
    "unknownStatus": (1, ("R1-195",)),
    "unknownFieldsRemainRaw": (1, ("R1-122",)),
    "rejectedOrUnknown": (1, ("R1-123", "R1-139")),
    "wearStateIsUnknown": (2, ("R1-121",)),
    "wearStateIsUnknownRaw": (1, ("R1-121",)),
    "wearUnknownBooleanOffset": (1, ("R1-121",)),
    "queryMapsConfirmedWearToUnknown": (1, ("R1-176",)),
}


PROTOCOL_CAPABILITIES: dict[str, tuple[str, ...]] = {
    "system:01": ("R1-006", "R1-190"),
    "system:02": ("R1-013", "R1-189"),
    "system:03": ("R1-007", "R1-190"),
    "system:04": ("R1-014", "R1-118", "R1-194"),
    "system:05": ("R1-004", "R1-113", "R1-192"),
    "system:07": ("R1-032",),
    "system:08": ("R1-040", "R1-191"),
    "system:09": ("R1-030",),
    "system:0a": ("R1-005", "R1-191"),
    "system:0b": ("R1-017", "R1-195"),
    "system:0c": ("R1-017", "R1-105", "R1-195"),
    "system:0e": ("R1-016", "R1-116"),
    "system:0f": ("R1-015", "R1-036"),
    "system:10": ("R1-013", "R1-189"),
    "system:11": ("R1-029", "R1-193"),
    "system:12": ("R1-028",),
    "system:7e": ("R1-026", "R1-188"),
    "system:7f": ("R1-186",),
    "system:82": ("R1-187",),
    "system:83": ("R1-185",),
    "health:0101": ("R1-018", "R1-170"),
    "health:0102": ("R1-018", "R1-078"),
    "health:0103": ("R1-018",),
    "health:0201": ("R1-019", "R1-169"),
    "health:0202": ("R1-019", "R1-078"),
    "health:0203": ("R1-019",),
    "health:0401": ("R1-021", "R1-168"),
    "health:0402": ("R1-021", "R1-078"),
    "health:0403": ("R1-077",),
    "health:0501": ("R1-022", "R1-173", "R1-174"),
    "health:0502": ("R1-022", "R1-174", "R1-175"),
    "health:0601": ("R1-023", "R1-111"),
    "health:0602": ("R1-024", "R1-178"),
    "health:7f01": ("R1-016", "R1-116"),
    "testable:0001": ("R1-079",),
}


INTERNAL_EVENT_CAPABILITIES: dict[str, tuple[str, ...]] = {
    "0x0001": ("R1-112",),
    "0x0002": ("R1-112",),
    "0x0003": ("R1-113", "R1-192"),
    "0x0004": ("R1-113",),
    "0x0005": ("R1-114",),
    "0x0006": ("R1-073", "R1-170"),
    "0x0007": ("R1-165", "R1-166", "R1-167", "R1-168"),
    "0x0008": ("R1-073", "R1-169"),
    "0x0009": ("R1-074", "R1-171"),
    "0x000a": ("R1-075", "R1-172"),
    "0x000b": ("R1-173", "R1-175"),
    "0x000c": ("R1-126", "R1-177", "R1-178"),
    "0x000d": ("R1-178", "R1-179"),
    "0x000e": ("R1-078",),
    "0x000f": ("R1-079",),
    "0x0010": ("R1-079",),
    "0x1000": ("R1-112",),
    "0x1001": ("R1-018", "R1-114"),
    "0x1002": ("R1-018",),
    "0x1003": ("R1-019", "R1-114"),
    "0x1004": ("R1-019",),
    "0x1005": ("R1-020", "R1-114"),
    "0x1006": ("R1-020", "R1-074"),
    "0x1007": ("R1-075", "R1-172"),
    "0x1008": ("R1-075", "R1-172"),
    "0x1009": ("R1-174", "R1-175"),
    "0x100a": ("R1-118", "R1-194"),
    "0x100b": ("R1-006", "R1-177"),
    "0x100c": ("R1-178",),
    "0x100d": ("R1-115", "R1-116"),
    "0x100e": ("R1-024", "R1-178"),
    "0x2000": ("R1-179", "R1-180", "R1-181", "R1-182", "R1-183"),
    "0x2001": ("R1-111", "R1-184"),
    "0x2002": ("R1-183",),
    "0x2003": ("R1-106",),
    "0x2004": ("R1-105", "R1-195"),
    "0x2005": ("R1-029", "R1-064"),
    "0x2006": ("R1-112",),
}


FACTORY_CAPABILITIES: dict[str, tuple[str, ...]] = {
    "AT^INFO": ("R1-013", "R1-049", "R1-052"),
    "AT^CHARGE_VER": ("R1-052", "R1-060"),
    "AT^CHARGE_HW_VER": ("R1-052", "R1-060"),
    "AT^RESET_RING": ("R1-052",),
    "AT^DOCK_ADV_SET": ("R1-052", "R1-060"),
    "AT^DEVID": ("R1-013", "R1-052"),
    "AT^DFU": ("R1-030", "R1-052"),
    "AT^PMIC_READ": ("R1-052", "R1-081"),
    "AT^CHARGE_TEMP": ("R1-052", "R1-087"),
    "AT^BAT_ADC": ("R1-052", "R1-083"),
    "AT^PMIC_OFF": ("R1-052", "R1-081"),
    "AT^PMIC_ISNS": ("R1-052", "R1-081"),
    "AT^TOUCH_INIT": ("R1-052", "R1-091"),
    "AT^TOUCH_HW": ("R1-052", "R1-091"),
    "AT^KV_READ": ("R1-052", "R1-108", "R1-109"),
    "AT^WEAR_STATUS": ("R1-007", "R1-052", "R1-176"),
    "AT^TEMP": ("R1-052", "R1-053", "R1-054"),
    "AT^LOG": ("R1-027", "R1-052", "R1-107"),
    "AT^BFAST": ("R1-052", "R1-062"),
    "AT^BSLOW": ("R1-052", "R1-062"),
    "AT^STOPADV": ("R1-052", "R1-062"),
    "AT^SLOWADV": ("R1-052", "R1-062"),
    "AT^FASTADV": ("R1-052", "R1-062"),
    "AT^SDVER": ("R1-052",),
    "AT^BLE_LOG": ("R1-052", "R1-062"),
    "AT^BLE_KEEPCONNECT": ("R1-052", "R1-062"),
    "AT^ACC_OPEN": ("R1-052", "R1-061"),
    "AT^ACC_CLOSE": ("R1-052", "R1-061"),
    "AT^HR_OPEN": ("R1-052", "R1-053"),
    "AT^HR_CLOSE": ("R1-052", "R1-053"),
    "AT^SPO2_OPEN": ("R1-052", "R1-053"),
    "AT^SPO2_CLOSE": ("R1-052", "R1-053"),
    "AT^TEMP_OPEN": ("R1-052", "R1-053", "R1-090"),
    "AT^TEMP_CLOSE": ("R1-052", "R1-053", "R1-090"),
    "AT^HRV_OPEN": ("R1-052", "R1-053"),
    "AT^HRV_CLOSE": ("R1-052", "R1-053"),
    "AT^ACTIVITY_READ": ("R1-052", "R1-053"),
}


BUS_CAPABILITIES: dict[str, tuple[str, ...]] = {
    "i2c_0": ("R1-091", "R1-097", "R1-101"),
    "i2c_1": ("R1-061", "R1-101"),
    "i2c_2": ("R1-090", "R1-101"),
    "i2c_3": ("R1-101",),
    "i2c_4": ("R1-068", "R1-101"),
    "i2c_5": ("R1-055", "R1-081", "R1-086", "R1-101"),
}


ADC_CAPABILITIES: dict[str, tuple[str, ...]] = {
    "vbat_adc": ("R1-082", "R1-083"),
    "vpmic_isns_adc": ("R1-081", "R1-082", "R1-083"),
    "vnfc_rect_adc": ("R1-060", "R1-082", "R1-083"),
}


GPIO_CAPABILITIES: dict[str, tuple[str, ...]] = {
    "acc_int_1": ("R1-061", "R1-102"),
    "ppg_int": ("R1-068", "R1-102"),
    "touch_rdy_in": ("R1-097", "R1-098", "R1-102"),
    "mcu_reset_irq": ("R1-102",),
    "pmic_irq": ("R1-081", "R1-102"),
    "nfc_gpo_irq": ("R1-055", "R1-102"),
    "device_stacmd_irq": ("R1-086", "R1-102"),
    "ppg_led_en": ("R1-068", "R1-088", "R1-102"),
    "touch_ldo_en": ("R1-088", "R1-097", "R1-102"),
    "ppg_reset_en": ("R1-068", "R1-102"),
    "ship_mode_en": ("R1-081", "R1-102"),
    "touch_rdy_out": ("R1-097", "R1-102"),
}


PARTITION_CAPABILITIES: dict[str, tuple[str, ...]] = {
    "kv.bin": ("R1-104", "R1-108", "R1-109"),
    "health.db": ("R1-104", "R1-110"),
    "sleep.db": ("R1-104", "R1-110", "R1-180", "R1-181", "R1-182", "R1-183", "R1-184"),
    "pKey.bin": ("R1-104", "R1-105"),
    "reserve": ("R1-104",),
    "ep.bin": ("R1-104", "R1-106"),
    "log.bin": ("R1-027", "R1-104", "R1-107"),
}


SDK_COMMAND_CAPABILITIES: dict[str, tuple[str, ...]] = {
    "deviceStatus": ("R1-006", "R1-190"),
    "deviceInfo": ("R1-013", "R1-189"),
    "wearStatus": ("R1-007", "R1-190"),
    "userInfo": ("R1-014", "R1-118", "R1-194"),
    "systemTime": ("R1-004", "R1-192"),
    "touchStatus": ("R1-032", "R1-077", "R1-199"),
    "touchSwitch": ("R1-032",),
    "pairAuth": ("R1-040", "R1-191"),
    "otaStart": ("R1-030",),
    "advertiseStart": ("R1-005", "R1-191"),
    "algorithmKeyStatus": ("R1-017", "R1-195"),
    "setAlgorithmKey": ("R1-017", "R1-105", "R1-195"),
    "healthSettings": ("R1-016", "R1-036"),
    "setHealthSettings": ("R1-016", "R1-116"),
    "systemSettings": ("R1-015", "R1-036"),
    "setSystemSettings": ("R1-015", "R1-036", "R1-196"),
    "deviceSerial": ("R1-013", "R1-189"),
    "nonvolatileRecovery": ("R1-029", "R1-193"),
    "powerControl": ("R1-028",),
    "packetAcknowledgement": ("R1-026", "R1-188"),
    "heartbeat": ("R1-186",),
    "glassesHeartbeat": ("R1-005", "R1-038", "R1-077", "R1-199"),
    "glassesHandshake": ("R1-005", "R1-038", "R1-077", "R1-199"),
    "removeRingNotification": ("R1-187",),
    "heartRateDaily": ("R1-018", "R1-170"),
    "heartRatePoint": ("R1-018", "R1-078"),
    "heartRateMeasure": ("R1-018",),
    "bloodOxygenDaily": ("R1-019", "R1-169"),
    "bloodOxygenPoint": ("R1-019", "R1-078"),
    "bloodOxygenMeasure": ("R1-019",),
    "temperatureDaily": ("R1-020", "R1-077", "R1-199"),
    "temperaturePoint": ("R1-020", "R1-077", "R1-199"),
    "temperatureMeasure": ("R1-020", "R1-077", "R1-199"),
    "hrvDaily": ("R1-021", "R1-168"),
    "hrvPoint": ("R1-021", "R1-078"),
    "hrvMeasure": ("R1-021", "R1-077"),
    "activityDaily": ("R1-022", "R1-174"),
    "activityAllDay": ("R1-022", "R1-174", "R1-175"),
    "sleepDaily": ("R1-023", "R1-111"),
    "sleepForceAwake": ("R1-024", "R1-178"),
    "healthReportEnable": ("R1-016", "R1-116"),
    "sportStart": ("R1-025", "R1-077"),
    "sportStop": ("R1-025", "R1-077"),
    "sportSample": ("R1-025", "R1-077"),
}


PUBLIC_R1_SDK_METHOD_CAPABILITIES: dict[str, tuple[str, ...]] = {
    "cancelR1FirmwareFlash": ("R1-030",),
    "flashR1Firmware": ("R1-030",),
    "requestR1ReadOnlySnapshot": ("R1-006", "R1-007", "R1-013", "R1-015", "R1-016"),
    "requestR1ReadOnly": ("R1-003", "R1-077"),
    "requestR1FactoryReadOnly": ("R1-002", "R1-052"),
    "requestR1Measurement": ("R1-018", "R1-019", "R1-021"),
    "setR1HealthTrackingEnabled": ("R1-016",),
    "setR1LowPerformanceModeEnabled": ("R1-196",),
    "unlockR1Bootloader": ("R1-030", "R1-056"),
    "requestR1SleepFinalization": ("R1-024", "R1-178"),
}


KNOWN_UNREGISTERED_SDK_COMMANDS = {
    "touchStatus",
    "glassesHeartbeat",
    "glassesHandshake",
    "temperatureDaily",
    "temperaturePoint",
    "temperatureMeasure",
    "sportStart",
    "sportStop",
    "sportSample",
}


NEGATIVE_SURFACE_CAPABILITIES: dict[str, tuple[str, ...]] = {
    "no_stock_raw_optical_ble_stream": ("R1-042", "R1-068"),
    "no_stock_raw_accelerometer_ble_stream": ("R1-043", "R1-061"),
    "no_gyroscope_or_magnetometer_inventory": ("R1-044", "R1-049"),
    "no_ring_haptic_or_user_led_output": ("R1-046", "R1-049"),
    "no_ring_microphone_or_audio_stream": ("R1-047", "R1-049"),
    "no_ecg_bp_glucose_or_respiration_public_metric": ("R1-048", "R1-123"),
}


# Every reusable Python evidence generator is assigned to the capability row(s) whose claims it
# can reproduce. Summary/replay pairs intentionally share one topic. This is an inventory gate,
# not an instruction to execute the scripts against a device: all inputs remain the pinned OTA
# image or caller-supplied offline fixtures.
ANALYZER_TOPIC_CAPABILITIES: dict[str, tuple[str, ...]] = {
    "activity_accumulator": ("R1-141",),
    "activity_accumulator_service": ("R1-141",),
    "activity_public_route": ("R1-174",),
    "activity_storage": ("R1-173",),
    "adc_registry": ("R1-082",),
    "algorithm_domains": ("R1-123",),
    "algorithm_key_mediation": ("R1-195",),
    "ati_calibration_command": ("R1-100",),
    "bae8_event_router": ("R1-202",),
    "battery_runtime_service": ("R1-082", "R1-083", "R1-084", "R1-085"),
    "battery_tables": ("R1-084",),
    "bc_f2_table": ("R1-052",),
    "ble_tx_queue_dispatch": ("R1-202",),
    "bootloader_security": ("R1-030", "R1-056", "R1-080"),
    "bus_registry": ("R1-101",),
    "clock_watchdog": ("R1-103",),
    "connection_control": ("R1-191",),
    "connection_parameter_policy": ("R1-062", "R1-200"),
    "connection_role_assignment": ("R1-004", "R1-191"),
    "decimal_rounder": ("R1-153",),
    "delayed_event_timer": ("R1-112", "R1-202"),
    "dormant_estimator": ("R1-144", "R1-145", "R1-164"),
    "dormant_heart_rate_filter": ("R1-147",),
    "dormant_heart_rate_gate": ("R1-149",),
    "dormant_iteration": ("R1-163",),
    "dormant_ratio_accumulator": ("R1-148",),
    "dormant_speed_baseline": ("R1-154",),
    "dormant_speed_filters": ("R1-146",),
    "dormant_speed_reducer": ("R1-155",),
    "dormant_speed_roots": ("R1-156", "R1-157", "R1-158", "R1-159", "R1-160"),
    "dormant_speed_routes": ("R1-151", "R1-162"),
    "dormant_speed_smoother": ("R1-150",),
    "dormant_speed_threshold": ("R1-152",),
    "energy_pipeline": ("R1-125",),
    "ep_store": ("R1-106",),
    "eus_rx_reassembly": ("R1-003",),
    "eus_trace": ("R1-003", "R1-041"),
    "export_state_machine": ("R1-027", "R1-107"),
    "factory_table": ("R1-052",),
    "first_party_sport_aot": ("R1-025", "R1-198"),
    "first_party_unregistered_aot": ("R1-020", "R1-032", "R1-038", "R1-199"),
    "flash_layout": ("R1-104",),
    "freertos_kernel_version": ("R1-080", "R1-197"),
    "freertos_stack_overflow": ("R1-080", "R1-197"),
    "freertos_static_memory": ("R1-080", "R1-197"),
    "frontier_334_342": ("R1-117", "R1-123", "R1-197"),
    "frontier_35x": ("R1-117", "R1-123", "R1-197"),
    "gatt_btsnoop": ("R1-089",),
    "global_health_gate": ("R1-115",),
    "gomore_activity_state_classifier": ("R1-117", "R1-122"),
    "gomore_auth_parser": ("R1-105", "R1-119"),
    "gomore_call_graph": ("R1-117",),
    "gomore_energy_model": ("R1-125",),
    "gomore_iir_designer": ("R1-123", "R1-131"),
    "gomore_input_abi": ("R1-121",),
    "gomore_initializer_boundary": ("R1-117", "R1-119"),
    "gomore_lifecycle": ("R1-119",),
    "gomore_neural_runtime": ("R1-130",),
    "gomore_output_abi": ("R1-120",),
    "gomore_output_producers": ("R1-122",),
    "gomore_sleep_graphs": ("R1-126", "R1-128", "R1-129", "R1-130"),
    "gomore_sleep_stage_statistics": ("R1-127",),
    "gomore_store": ("R1-105",),
    "goodix_channel_decoder": ("R1-068", "R1-072"),
    "goodix_hr_boundary": ("R1-068", "R1-073"),
    "goodix_hr_init_boundary": ("R1-068", "R1-073"),
    "goodix_hrv_boundary": ("R1-068", "R1-165"),
    "goodix_integrity_boundary": ("R1-068",),
    "goodix_nadt_accumulation": ("R1-069", "R1-070"),
    "goodix_nadt_boundary": ("R1-069", "R1-070"),
    "goodix_nadt_peak_mask": ("R1-069",),
    "goodix_nadt_quality": ("R1-069",),
    "goodix_register_profile": ("R1-068",),
    "goodix_spo2_dlcom_boundary": ("R1-068", "R1-072"),
    "gpio_registry": ("R1-102",),
    "health_daily_test": ("R1-079",),
    "health_reporting": ("R1-116",),
    "health_history_dispatch": ("R1-078",),
    "health_sleep_store": ("R1-110", "R1-126"),
    "health_startup": ("R1-114",),
    "heart_rate_selector": ("R1-143",),
    "hr_storage": ("R1-170",),
    "hr_sync_flush": ("R1-170",),
    "hrv_daily_cache": ("R1-168",),
    "hrv_flash_merge": ("R1-168",),
    "hrv_ram_cache_merge": ("R1-168",),
    "hrv_rmssd": ("R1-165",),
    "hrv_storage": ("R1-166", "R1-167"),
    "hrv_sync_flush": ("R1-168",),
    "hrv_timing_start": ("R1-166",),
    "identity_routes": ("R1-189",),
    "internal_events": ("R1-112",),
    "iqs7211e_ati_audit": ("R1-100",),
    "kv_store": ("R1-108", "R1-109"),
    "legacy_command_dispatch": ("R1-052", "R1-077"),
    "locomotion_window": ("R1-135",),
    "log_bin_writer": ("R1-107",),
    "log_store": ("R1-107",),
    "motion_classifier": ("R1-136", "R1-137", "R1-138", "R1-139", "R1-140"),
    "nfc_dock_policy": ("R1-055", "R1-060"),
    "nfc_mailbox_versions": ("R1-055",),
    "nordic_advertising_closure": ("R1-062", "R1-200", "R1-201"),
    "nordic_ble_static_helpers": ("R1-200", "R1-201"),
    "nordic_buttonless_dfu_closure": ("R1-030", "R1-056"),
    "nordic_gatt_cache_closure": ("R1-089", "R1-200"),
    "nordic_package": ("R1-080",),
    "nordic_power_management_closure": ("R1-080", "R1-103"),
    "nordic_system_init": ("R1-080", "R1-200"),
    "nordic_twim_completeness": ("R1-101",),
    "nv_compiled_restore": ("R1-064",),
    "nv_recovery_closure": ("R1-029", "R1-193"),
    "packet_ack": ("R1-188",),
    "peer_manager_event_policy": ("R1-040", "R1-089", "R1-200"),
    "peer_target_policy": ("R1-191",),
    "phone_nv_mediation": ("R1-193",),
    "phone_user_info_mediation": ("R1-194",),
    "pmic_charge_event": ("R1-060", "R1-081", "R1-084"),
    "pmic_charged_notification": ("R1-060", "R1-081", "R1-084"),
    "pmic_transport": ("R1-081", "R1-086"),
    "power_control": ("R1-028", "R1-109"),
    "protocol_response": ("R1-003", "R1-041"),
    "quantized_pooling_boundary": ("R1-123", "R1-130"),
    "remove_ring": ("R1-187",),
    "reset_reason_closure": ("R1-103", "R1-197"),
    "reset_trace_closure": ("R1-103", "R1-197"),
    "resolved_thunks": ("R1-197",),
    "rtc_device_boundary": ("R1-103", "R1-113"),
    "scalar_health_flash_merge": ("R1-168", "R1-169", "R1-170", "R1-171"),
    "scalar_health_ram_cache_merge": ("R1-168", "R1-169", "R1-170", "R1-171"),
    "sensor_algorithm_heap": ("R1-115", "R1-123"),
    "sensor_stream_dispatch": ("R1-068", "R1-112"),
    "sensor_stream_register": ("R1-068", "R1-112"),
    "sensor_stream_unregister": ("R1-068", "R1-112"),
    "sleep_algorithm": (
        "R1-126", "R1-127", "R1-128", "R1-129",
        "R1-130", "R1-131", "R1-132", "R1-133",
    ),
    "sleep_append_planner": ("R1-180",),
    "sleep_final_publication": ("R1-127", "R1-178"),
    "sleep_iterator_marker": ("R1-184",),
    "sleep_maintenance": ("R1-183",),
    "sleep_record_writer": ("R1-182",),
    "sleep_sector_policy": ("R1-181",),
    "sleep_sync": ("R1-111", "R1-179", "R1-184"),
    "sleep_sync_packet": ("R1-111", "R1-179"),
    "software_twi_engines": ("R1-101",),
    "spo2_storage": ("R1-169",),
    "spo2_sync_flush": ("R1-169",),
    "sps_accelerometer": ("R1-142",),
    "sps_speed_selector": ("R1-124",),
    "status_routes": ("R1-190",),
    "step_accumulator": ("R1-134",),
    "stress_storage": ("R1-172",),
    "structured_log_cache": ("R1-107",),
    "system_83": ("R1-185",),
    "system_heartbeat": ("R1-186",),
    "system_settings_route": ("R1-196",),
    "system_time_route": ("R1-192",),
    "temperature_storage": ("R1-171",),
    "time_health_rollover": ("R1-113",),
    "touch_calibration": ("R1-093", "R1-100"),
    "touch_slider_closure": ("R1-093", "R1-095"),
    "touch_task_dispatcher": ("R1-098", "R1-112"),
    "touch_transport": ("R1-097", "R1-098", "R1-099", "R1-100"),
    "user_profile": ("R1-118",),
    "validated_sleep_delivery": ("R1-179",),
    "watchdog_device_boundary": ("R1-103",),
    "wear_fusion_closure": ("R1-070", "R1-176", "R1-177"),
    "wear_fusion_service": ("R1-176",),
    "wear_runtime_bridge": ("R1-177",),
}


def load_ledger(path: Path, errors: list[str]) -> tuple[list[dict[str, str]], set[str]]:
    try:
        with path.open(newline="", encoding="utf-8") as stream:
            rows = list(csv.DictReader(stream))
    except (OSError, csv.Error) as error:
        errors.append(f"{path}: cannot read capability ledger: {error}")
        return [], set()
    expected_fields = {
        "id", "domain", "capability", "evidence", "readiness",
        "current_sybilsight", "next_gate", "risk",
    }
    if set(rows[0] if rows else ()) != expected_fields:
        errors.append(f"{path}: unexpected columns")
    ids = [row.get("id", "") for row in rows]
    if len(ids) != len(set(ids)):
        errors.append(f"{path}: duplicate capability IDs")
    expected_ids = [f"R1-{index:03d}" for index in range(1, len(ids) + 1)]
    if ids != expected_ids:
        errors.append(f"{path}: capability IDs are not sequential")
    for row in rows:
        for field in expected_fields:
            if not row.get(field, "").strip():
                errors.append(f"{row.get('id', '<unknown>')}: blank {field}")
        combined = " ".join(row.get(field, "") for field in expected_fields)
        for marker in STALE_LEDGER_BUILD_MARKERS:
            if marker in combined:
                errors.append(
                    f"{row.get('id', '<unknown>')}: stale build blocker {marker!r}"
                )
        for marker in SUPERSEDED_STATIC_NEXT_GATE_MARKERS.get(
            row.get("id", ""), ()
        ):
            if marker in row.get("next_gate", ""):
                errors.append(
                    f"{row.get('id', '<unknown>')}: superseded static next gate "
                    f"{marker!r}"
                )
    if RESIDUAL_CLOSURE_CAPABILITY not in ids:
        errors.append(
            f"{path}: missing residual closure capability "
            f"{RESIDUAL_CLOSURE_CAPABILITY}"
        )
    return rows, set(ids)


def validate_mapping(
    label: str,
    actual: set[str],
    mapping: dict[str, tuple[str, ...]],
    ledger_ids: set[str],
    errors: list[str],
) -> None:
    expected = set(mapping)
    if actual != expected:
        errors.append(
            f"{label} coverage mismatch: "
            f"unmapped={sorted(actual - expected)} stale={sorted(expected - actual)}"
        )
    for surface, capabilities in mapping.items():
        if not capabilities:
            errors.append(f"{label} {surface}: no capability disposition")
        for capability in capabilities:
            if capability not in ledger_ids:
                errors.append(f"{label} {surface}: unknown capability {capability}")


def protocol_rows(image: bytes, base: int, address: int, count: int) -> list[tuple[int, int]]:
    offset = address - base
    rows: list[tuple[int, int]] = []
    for index in range(count):
        identifier, handler = struct.unpack_from(
            "<II", image, offset + index * PROTOCOL_RECORD_BYTES
        )
        if handler & 1 == 0:
            raise ValueError(f"protocol row {index} has a non-Thumb handler")
        rows.append((identifier, handler))
    return rows


def sdk_command_symbols(source: str) -> set[str]:
    start = source.index("public enum R1CommandCatalog")
    end = source.index("public static let all:", start)
    catalog = source[start:end]
    return set(re.findall(
        r"public\s+static\s+let\s+(\w+)\s*=\s*(?:command|healthCommand)\(",
        catalog,
    ))


def public_r1_sdk_method_symbols(source: str) -> set[str]:
    return set(re.findall(r"public\s+func\s+(\w*R1\w*)\s*\(", source))


def unresolved_public_symbols(source: str) -> Counter[str]:
    declarations = re.findall(
        r"^\s*(?:"
        r"public\s+(?:static\s+)?(?:let|var)\s+"
        r"|case\s+"
        r")([A-Za-z_]\w*[Uu]nresolved\w*|unresolved\w*)\b",
        source,
        flags=re.MULTILINE,
    )
    return Counter(declarations)


def unknown_public_symbols(source: str) -> Counter[str]:
    declarations = re.findall(
        r"^\s*(?:"
        r"public\s+(?:static\s+)?(?:let|var)\s+"
        r"|case\s+"
        r")([A-Za-z_]\w*[Uu]nknown\w*|unknown\w*)\b",
        source,
        flags=re.MULTILINE,
    )
    return Counter(declarations)


def analyzer_topic(path: Path) -> str | None:
    match = re.fullmatch(r"(?:summarize|emulate)_r1_(.+)\.py", path.name)
    return match.group(1) if match else None


def audit_tracked_surfaces(
    root: Path,
    ledger_ids: set[str],
    errors: list[str],
) -> dict[str, int]:
    """Validate source-derived surfaces available in every clean checkout."""
    sdk_path = (
        root
        / "Vendor/SybilSightBluetoothSDK/ios/Source/controllers/R1ProtocolModels.swift"
    )
    sdk_source = sdk_path.read_text(encoding="utf-8")
    sdk_symbols = sdk_command_symbols(sdk_source)
    validate_mapping(
        "SDK command", sdk_symbols, SDK_COMMAND_CAPABILITIES, ledger_ids, errors,
    )
    for symbol in KNOWN_UNREGISTERED_SDK_COMMANDS:
        if symbol not in sdk_symbols:
            errors.append(f"known-unregistered SDK command disappeared: {symbol}")

    unresolved_symbols = unresolved_public_symbols(sdk_source)
    expected_unresolved_symbols = Counter({
        symbol: expected_count
        for symbol, (expected_count, _) in
        UNRESOLVED_PUBLIC_SYMBOL_CAPABILITIES.items()
    })
    if unresolved_symbols != expected_unresolved_symbols:
        errors.append(
            "public unresolved-symbol inventory changed: "
            f"added_or_increased={dict(unresolved_symbols - expected_unresolved_symbols)} "
            f"removed_or_decreased={dict(expected_unresolved_symbols - unresolved_symbols)}"
        )
    for symbol, (_, capabilities) in (
        UNRESOLVED_PUBLIC_SYMBOL_CAPABILITIES.items()
    ):
        for capability in capabilities:
            if capability not in ledger_ids:
                errors.append(
                    f"public unresolved symbol {symbol}: "
                    f"unknown capability {capability}"
                )

    unknown_symbols = unknown_public_symbols(sdk_source)
    expected_unknown_symbols = Counter({
        symbol: expected_count
        for symbol, (expected_count, _) in
        UNKNOWN_PUBLIC_SYMBOL_CAPABILITIES.items()
    })
    if unknown_symbols != expected_unknown_symbols:
        errors.append(
            "public unknown-symbol inventory changed: "
            f"added_or_increased={dict(unknown_symbols - expected_unknown_symbols)} "
            f"removed_or_decreased={dict(expected_unknown_symbols - unknown_symbols)}"
        )
    for symbol, (_, capabilities) in UNKNOWN_PUBLIC_SYMBOL_CAPABILITIES.items():
        for capability in capabilities:
            if capability not in ledger_ids:
                errors.append(
                    f"public unknown symbol {symbol}: "
                    f"unknown capability {capability}"
                )

    public_sdk_path = root / "Vendor/SybilSightBluetoothSDK/ios/Source/SybilSightBluetoothSDK.swift"
    public_sdk_source = public_sdk_path.read_text(encoding="utf-8")
    public_r1_methods = public_r1_sdk_method_symbols(public_sdk_source)
    validate_mapping(
        "public R1 SDK method",
        public_r1_methods,
        PUBLIC_R1_SDK_METHOD_CAPABILITIES,
        ledger_ids,
        errors,
    )
    bridge_source = (root / "SybilSight/Core/CoreBridge.swift").read_text(encoding="utf-8")
    telemetry_store_source = (
        root / "SybilSight/Services/R1TelemetryStore.swift"
    ).read_text(encoding="utf-8")
    live_bridge_start = bridge_source.index("final class LiveCoreBridge")
    live_bridge_source = bridge_source[live_bridge_start:]
    for method in sorted(public_r1_methods):
        method_pattern = rf"\bfunc\s+{re.escape(method)}\s*\("
        if re.search(method_pattern, bridge_source) is None:
            errors.append(f"public R1 SDK method is absent from CoreBridge: {method}")
        if re.search(method_pattern, live_bridge_source) is None:
            errors.append(f"public R1 SDK method is absent from LiveCoreBridge: {method}")
        if re.search(rf"\b{re.escape(method)}\s*\(", telemetry_store_source) is None:
            errors.append(f"public R1 SDK method is absent from R1TelemetryStore: {method}")

    validate_mapping(
        "negative surface",
        set(NEGATIVE_SURFACE_CAPABILITIES),
        NEGATIVE_SURFACE_CAPABILITIES,
        ledger_ids,
        errors,
    )

    analyzer_paths = sorted(
        path
        for path in (root / "tools").glob("*.py")
        if analyzer_topic(path) is not None
    )
    analyzer_topics = {
        topic
        for path in analyzer_paths
        if (topic := analyzer_topic(path)) is not None
    }
    validate_mapping(
        "R1 evidence-generator topic",
        analyzer_topics,
        ANALYZER_TOPIC_CAPABILITIES,
        ledger_ids,
        errors,
    )

    return {
        "sdk_command_descriptors": len(sdk_symbols),
        "public_r1_sdk_methods": len(public_r1_methods),
        "known_unregistered_sdk_commands": len(KNOWN_UNREGISTERED_SDK_COMMANDS),
        "public_unresolved_symbol_declarations": sum(unresolved_symbols.values()),
        "public_unresolved_symbol_names": len(unresolved_symbols),
        "public_unknown_symbol_declarations": sum(unknown_symbols.values()),
        "public_unknown_symbol_names": len(unknown_symbols),
        "explicit_negative_surfaces": len(NEGATIVE_SURFACE_CAPABILITIES),
        "evidence_generator_scripts": len(analyzer_paths),
        "evidence_generator_topics": len(analyzer_topics),
    }


def audit(root: Path, image_path: Path) -> tuple[dict[str, Any], list[str]]:
    errors: list[str] = []
    ledger_rows, ledger_ids = load_ledger(root / "docs/reference/r1-capability-matrix.csv", errors)

    image = image_path.read_bytes()
    digest = hashlib.sha256(image).hexdigest()
    if digest != IMAGE_SHA256:
        errors.append(f"firmware SHA-256 changed: {digest}")

    health_rows = protocol_rows(
        image, adc.DEFAULT_BASE, HEALTH_TABLE_ADDRESS, HEALTH_ENTRY_COUNT
    )
    system_rows = protocol_rows(
        image, adc.DEFAULT_BASE, SYSTEM_TABLE_ADDRESS, SYSTEM_ENTRY_COUNT
    )
    protocol_surfaces = {
        f"health:{identifier:04x}" for identifier, _ in health_rows
    } | {
        f"system:{identifier:02x}" for identifier, _ in system_rows
    }
    testable_offset = TESTABLE_REGISTRATION_ADDRESS - adc.DEFAULT_BASE
    testable_identifier, testable_handler = struct.unpack_from(
        "<II", image, testable_offset
    )
    if testable_handler & 1 == 0:
        errors.append("testable registration has a non-Thumb handler")
    protocol_surfaces.add(f"testable:{testable_identifier:04x}")
    validate_mapping(
        "production protocol", protocol_surfaces, PROTOCOL_CAPABILITIES,
        ledger_ids, errors,
    )

    event_report = events.summarize(
        image_path,
        adc.DEFAULT_BASE,
        adc.DEFAULT_SCATTER_SOURCE,
        adc.DEFAULT_SCATTER_RUNTIME,
        adc.DEFAULT_SCATTER_LENGTH,
    )
    validate_mapping(
        "internal event",
        {item["identifier"] for item in event_report["events"]},
        INTERNAL_EVENT_CAPABILITIES,
        ledger_ids,
        errors,
    )

    factory_report = factory.summarize(
        image_path,
        adc.DEFAULT_BASE,
        factory.DEFAULT_TABLE,
        factory.DEFAULT_COUNT,
    )
    validate_mapping(
        "factory command",
        {item["command"] for item in factory_report["entries"]},
        FACTORY_CAPABILITIES,
        ledger_ids,
        errors,
    )

    bus_report = bus.summarize(
        image_path,
        adc.DEFAULT_BASE,
        adc.DEFAULT_SCATTER_SOURCE,
        adc.DEFAULT_SCATTER_RUNTIME,
        adc.DEFAULT_SCATTER_LENGTH,
    )
    validate_mapping(
        "two-wire bus",
        {item["name"] for item in bus_report["buses"]},
        BUS_CAPABILITIES,
        ledger_ids,
        errors,
    )

    adc_report = adc.summarize(
        image_path,
        adc.DEFAULT_BASE,
        adc.DEFAULT_SCATTER_SOURCE,
        adc.DEFAULT_SCATTER_RUNTIME,
        adc.DEFAULT_SCATTER_LENGTH,
        adc.DEFAULT_REGISTRY,
        adc.DEFAULT_COUNT,
    )
    validate_mapping(
        "ADC",
        {item["name"] for item in adc_report["records"]},
        ADC_CAPABILITIES,
        ledger_ids,
        errors,
    )

    gpio_report = gpio.summarize(
        image_path,
        adc.DEFAULT_BASE,
        adc.DEFAULT_SCATTER_SOURCE,
        adc.DEFAULT_SCATTER_RUNTIME,
        adc.DEFAULT_SCATTER_LENGTH,
    )
    gpio_names = {
        item["name"] for item in gpio_report["input_registry"]["records"]
    } | {
        item["name"] for item in gpio_report["output_registry"]["records"]
    }
    validate_mapping(
        "GPIO", gpio_names, GPIO_CAPABILITIES, ledger_ids, errors,
    )

    flash_report = flash.summarize(
        image_path,
        adc.DEFAULT_BASE,
        adc.DEFAULT_SCATTER_SOURCE,
        adc.DEFAULT_SCATTER_RUNTIME,
        adc.DEFAULT_SCATTER_LENGTH,
    )
    validate_mapping(
        "flash partition",
        {
            item["name"]
            for item in flash_report["partition_table"]["partitions"]
        },
        PARTITION_CAPABILITIES,
        ledger_ids,
        errors,
    )

    tracked_surface_counts = audit_tracked_surfaces(root, ledger_ids, errors)

    report = {
        "analysis": "R1 production surface-to-capability closure audit",
        "mode": "full-evidence",
        "firmware_evidence_checked": True,
        "firmware": str(image_path),
        "firmware_sha256": digest,
        "ledger_rows": len(ledger_rows),
        "surface_counts": {
            "production_protocol_registrations": len(protocol_surfaces),
            "internal_event_slots": len(event_report["events"]),
            "populated_internal_event_slots": event_report["populated_slot_count"],
            "factory_commands": len(factory_report["entries"]),
            "two_wire_buses": len(bus_report["buses"]),
            "adc_inputs": len(adc_report["records"]),
            "gpio_devices": len(gpio_names),
            "flash_partitions": len(
                flash_report["partition_table"]["partitions"]
            ),
            **tracked_surface_counts,
        },
        "mapped_surface_count": sum([
            len(PROTOCOL_CAPABILITIES),
            len(INTERNAL_EVENT_CAPABILITIES),
            len(FACTORY_CAPABILITIES),
            len(BUS_CAPABILITIES),
            len(ADC_CAPABILITIES),
            len(GPIO_CAPABILITIES),
            len(PARTITION_CAPABILITIES),
            len(SDK_COMMAND_CAPABILITIES),
            len(NEGATIVE_SURFACE_CAPABILITIES),
        ]),
        "residual_documentation_integrity": {
            "closure_capability": RESIDUAL_CLOSURE_CAPABILITY,
            "stale_build_markers_rejected": len(STALE_LEDGER_BUILD_MARKERS),
            "superseded_static_next_gate_rows_rejected": len(
                SUPERSEDED_STATIC_NEXT_GATE_MARKERS
            ),
        },
        "known_unregistered_sdk_commands": sorted(KNOWN_UNREGISTERED_SDK_COMMANDS),
        "safety": {
            "static_firmware_read_only": True,
            "physical_device_access": False,
            "ble_access": False,
            "sensor_access": False,
            "internal_event_publication": False,
            "flash_mutation": False,
            "vendor_cloud_access": False,
            "captured_identity_or_health_data_read": False,
        },
        "valid": not errors,
        "errors": errors,
    }
    return report, errors


def audit_tracked_only(root: Path) -> tuple[dict[str, Any], list[str]]:
    """Audit committed ledgers and source mappings without the ignored firmware image."""
    errors: list[str] = []
    ledger_rows, ledger_ids = load_ledger(
        root / "docs/reference/r1-capability-matrix.csv",
        errors,
    )

    binary_mappings = (
        ("production protocol", PROTOCOL_CAPABILITIES),
        ("internal event", INTERNAL_EVENT_CAPABILITIES),
        ("factory command", FACTORY_CAPABILITIES),
        ("two-wire bus", BUS_CAPABILITIES),
        ("ADC", ADC_CAPABILITIES),
        ("GPIO", GPIO_CAPABILITIES),
        ("flash partition", PARTITION_CAPABILITIES),
    )
    for label, mapping in binary_mappings:
        # The firmware image is intentionally absent from a clean checkout. Still fail closed on
        # empty or unknown ledger dispositions; full mode separately proves the inventory keys.
        validate_mapping(label, set(mapping), mapping, ledger_ids, errors)

    tracked_surface_counts = audit_tracked_surfaces(root, ledger_ids, errors)
    surface_counts = {
        "production_protocol_dispositions": len(PROTOCOL_CAPABILITIES),
        "internal_event_dispositions": len(INTERNAL_EVENT_CAPABILITIES),
        "factory_command_dispositions": len(FACTORY_CAPABILITIES),
        "two_wire_bus_dispositions": len(BUS_CAPABILITIES),
        "adc_dispositions": len(ADC_CAPABILITIES),
        "gpio_dispositions": len(GPIO_CAPABILITIES),
        "flash_partition_dispositions": len(PARTITION_CAPABILITIES),
        **tracked_surface_counts,
    }
    report = {
        "analysis": "R1 tracked source-to-capability integrity audit",
        "mode": "tracked-only",
        "firmware_evidence_checked": False,
        "expected_firmware_sha256": IMAGE_SHA256,
        "ledger_rows": len(ledger_rows),
        "surface_counts": surface_counts,
        "mapped_surface_count": sum([
            len(PROTOCOL_CAPABILITIES),
            len(INTERNAL_EVENT_CAPABILITIES),
            len(FACTORY_CAPABILITIES),
            len(BUS_CAPABILITIES),
            len(ADC_CAPABILITIES),
            len(GPIO_CAPABILITIES),
            len(PARTITION_CAPABILITIES),
            len(SDK_COMMAND_CAPABILITIES),
            len(NEGATIVE_SURFACE_CAPABILITIES),
        ]),
        "residual_documentation_integrity": {
            "closure_capability": RESIDUAL_CLOSURE_CAPABILITY,
            "stale_build_markers_rejected": len(STALE_LEDGER_BUILD_MARKERS),
            "superseded_static_next_gate_rows_rejected": len(
                SUPERSEDED_STATIC_NEXT_GATE_MARKERS
            ),
        },
        "known_unregistered_sdk_commands": sorted(KNOWN_UNREGISTERED_SDK_COMMANDS),
        "safety": {
            "firmware_binary_read": False,
            "physical_device_access": False,
            "ble_access": False,
            "sensor_access": False,
            "internal_event_publication": False,
            "flash_mutation": False,
            "vendor_cloud_access": False,
            "captured_identity_or_health_data_read": False,
        },
        "valid": not errors,
        "errors": errors,
    }
    return report, errors


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "image",
        type=Path,
        nargs="?",
        default=Path("research/decompilation/rebuild/rebuilt-application.bin"),
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
    )
    parser.add_argument(
        "--tracked-only",
        action="store_true",
        help=(
            "validate committed ledgers and source mappings without requiring "
            "the intentionally untracked firmware image"
        ),
    )
    arguments = parser.parse_args()
    if arguments.tracked_only:
        report, errors = audit_tracked_only(arguments.root.resolve())
    else:
        report, errors = audit(arguments.root.resolve(), arguments.image.resolve())
    print(json.dumps(report, indent=2, sort_keys=True))
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
