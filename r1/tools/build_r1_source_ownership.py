#!/usr/bin/env python3
"""Build the conservative R1 function-by-function source-ownership ledger.

The ledger is an admission-control artifact, not an authorship verdict. A vendor
classification requires function-local evidence or an existing high-confidence
source correlation. Everything else remains blocked for ownership research.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from collections import Counter
from pathlib import Path

# --- evidence modules live in tools/evidence/ ---
import sys as _sys
from pathlib import Path as _Path

_sys.path.insert(0, str(_Path(__file__).resolve().parent / "evidence"))

from summarize_r1_software_twi_engines import SOFTWARE_TWI_FUNCTIONS
from summarize_r1_rtc_device_boundary import RTC_DEVICE_FUNCTIONS
from summarize_r1_pmic_transport import YHM2710_STACMD_FUNCTIONS
from summarize_r1_watchdog_device_boundary import WATCHDOG_DEVICE_FUNCTIONS
from summarize_r1_sensor_algorithm_heap import (
    SENSOR_ALGORITHM_HEAP_FUNCTIONS,
    SENSOR_ALGORITHM_HEAP_ROUTING,
)
from summarize_r1_gomore_initializer_boundary import GOMORE_INITIALIZER_FUNCTIONS
from summarize_r1_gomore_neural_runtime import GOMORE_NEURAL_RUNTIME_FUNCTIONS
from summarize_r1_gomore_sleep_graphs import GOMORE_SLEEP_GRAPH_FUNCTIONS
from summarize_r1_gomore_activity_state_classifier import (
    GOMORE_ACTIVITY_STATE_FUNCTIONS,
)
from summarize_r1_gomore_energy_model import GOMORE_ENERGY_MODEL_FUNCTIONS
from summarize_r1_gomore_iir_designer import GOMORE_IIR_DESIGNER_FUNCTIONS
from summarize_r1_gomore_auth_parser import GOMORE_AUTH_PARSER_FUNCTIONS
from summarize_r1_gomore_sleep_stage_statistics import (
    GOMORE_SLEEP_STAGE_STATISTICS_FUNCTIONS,
)
from summarize_r1_goodix_integrity_boundary import GOODIX_INTEGRITY_NEW_FUNCTIONS
from summarize_r1_goodix_nadt_boundary import GOODIX_NADT_FUNCTIONS
from summarize_r1_goodix_hr_boundary import GOODIX_HR_FUNCTIONS
from summarize_r1_goodix_hrv_boundary import GOODIX_HRV_FUNCTIONS
from summarize_r1_goodix_channel_decoder import GOODIX_CHANNEL_DECODER_FUNCTIONS
from summarize_r1_goodix_nadt_quality import GOODIX_NADT_QUALITY_FUNCTIONS
from summarize_r1_goodix_nadt_peak_mask import GOODIX_NADT_PEAK_MASK_FUNCTIONS
from summarize_r1_goodix_nadt_accumulation import GOODIX_NADT_ACCUMULATION_FUNCTIONS
from summarize_r1_goodix_register_profile import GOODIX_REGISTER_PROFILE_FUNCTIONS
from summarize_r1_goodix_spo2_dlcom_boundary import (
    GOODIX_SPO2_DLCOM_ALL_FUNCTIONS,
    GOODIX_SPO2_DLCOM_FUNCTIONS,
)
from summarize_r1_freertos_static_memory import FREERTOS_STATIC_MEMORY_FUNCTIONS
from summarize_r1_freertos_stack_overflow import FREERTOS_STACK_OVERFLOW_FUNCTIONS
from summarize_r1_nordic_system_init import NORDIC_SYSTEM_INIT_FUNCTIONS
from summarize_r1_nordic_twim_completeness import NORDIC_TWIM_COMPLETENESS_FUNCTIONS
from summarize_r1_nordic_gatt_cache_closure import NORDIC_GATT_CACHE_CLOSURE_FUNCTIONS
from summarize_r1_nordic_ble_static_helpers import NORDIC_BLE_STATIC_HELPER_FUNCTIONS
from summarize_r1_nordic_advertising_closure import NORDIC_ADVERTISING_FUNCTIONS
from summarize_r1_nordic_buttonless_dfu_closure import (
    NORDIC_BUTTONLESS_DFU_FUNCTIONS,
)
from summarize_r1_nordic_power_management_closure import (
    NORDIC_POWER_MANAGEMENT_FUNCTIONS,
)
from summarize_r1_reset_trace_closure import R1_RESET_TRACE_FUNCTIONS
from summarize_r1_reset_reason_closure import R1_RESET_REASON_FUNCTIONS
from summarize_r1_connection_control import R1_CONNECTION_CONTROL_FUNCTIONS
from summarize_r1_peer_manager_event_policy import R1_PEER_MANAGER_EVENT_FUNCTIONS
from summarize_r1_touch_slider_closure import R1_TOUCH_SLIDER_FUNCTIONS
from summarize_r1_health_daily_test import R1_HEALTH_DAILY_TEST_FUNCTIONS
from summarize_r1_nv_recovery_closure import R1_NV_RECOVERY_FUNCTIONS
from summarize_r1_nv_compiled_restore import R1_NV_COMPILED_RESTORE_FUNCTIONS
from summarize_r1_resolved_thunks import RESOLVED_THUNKS
from summarize_r1_structured_log_cache import R1_STRUCTURED_LOG_FUNCTIONS
from summarize_r1_log_bin_writer import R1_LOG_BIN_WRITER_FUNCTIONS
from summarize_r1_hrv_sync_flush import R1_HRV_SYNC_FLUSH_FUNCTIONS
from summarize_r1_hr_sync_flush import R1_HR_SYNC_FLUSH_FUNCTIONS
from summarize_r1_spo2_sync_flush import R1_SPO2_SYNC_FLUSH_FUNCTIONS
from summarize_r1_touch_task_dispatcher import R1_TOUCH_TASK_DISPATCHER_FUNCTIONS
from summarize_r1_sensor_stream_unregister import SENSOR_STREAM_UNREGISTER_FUNCTIONS
from summarize_r1_sensor_stream_register import SENSOR_STREAM_REGISTER_FUNCTIONS
from summarize_r1_sensor_stream_dispatch import SENSOR_STREAM_DISPATCH_FUNCTIONS
from summarize_r1_ble_tx_queue_dispatch import R1_BLE_TX_QUEUE_FUNCTIONS
from summarize_r1_wear_fusion_closure import R1_WEAR_FUSION_FUNCTIONS
from summarize_r1_connection_parameter_policy import R1_CONNECTION_PARAMETER_FUNCTIONS
from summarize_r1_sleep_sync_packet import R1_SLEEP_SYNC_PACKET_FUNCTIONS
from summarize_r1_nfc_dock_policy import R1_NFC_DOCK_POLICY_FUNCTIONS
from summarize_r1_peer_target_policy import R1_PEER_TARGET_FUNCTIONS
from summarize_r1_legacy_command_dispatch import (
    R1_LEGACY_COMMAND_DISPATCH_FUNCTIONS,
)
from summarize_r1_validated_sleep_delivery import (
    R1_VALIDATED_SLEEP_DELIVERY_FUNCTIONS,
)
from summarize_r1_quantized_pooling_boundary import (
    QUANTIZED_POOLING_RUNTIME_FUNCTIONS,
)
from summarize_r1_connection_role_assignment import (
    R1_CONNECTION_ROLE_ASSIGNMENT_FUNCTIONS,
)
from summarize_r1_eus_rx_reassembly import R1_EUS_RX_REASSEMBLY_FUNCTIONS
from summarize_r1_bae8_event_router import R1_BAE8_EVENT_ROUTER_FUNCTIONS
from summarize_r1_ati_calibration_command import R1_ATI_CALIBRATION_COMMAND_FUNCTIONS
from summarize_r1_battery_runtime_service import R1_BATTERY_RUNTIME_SERVICE_FUNCTIONS
from summarize_r1_goodix_hr_init_boundary import GOODIX_HR_INIT_FUNCTIONS
from summarize_r1_hrv_flash_merge import R1_HRV_FLASH_MERGE_FUNCTIONS
from summarize_r1_scalar_health_flash_merge import (
    R1_SCALAR_HEALTH_FLASH_MERGE_FUNCTIONS,
)
from summarize_r1_hrv_timing_start import R1_HRV_TIMING_START_FUNCTIONS
from summarize_r1_hrv_ram_cache_merge import R1_HRV_RAM_CACHE_MERGE_FUNCTIONS
from summarize_r1_scalar_health_ram_cache_merge import (
    R1_SCALAR_HEALTH_RAM_CACHE_MERGE_FUNCTIONS,
)
from summarize_r1_protocol_response import R1_PROTOCOL_RESPONSE_FUNCTIONS
from summarize_r1_export_state_machine import R1_EXPORT_STATE_MACHINE_FUNCTIONS
from summarize_r1_delayed_event_timer import R1_DELAYED_EVENT_TIMER_FUNCTIONS
from summarize_r1_pmic_charge_event import R1_PMIC_CHARGE_EVENT_FUNCTIONS
from summarize_r1_pmic_charged_notification import (
    R1_PMIC_CHARGED_NOTIFICATION_FUNCTIONS,
)
from summarize_r1_iqs7211e_ati_audit import R1_IQS7211E_ATI_AUDIT_FUNCTIONS
from summarize_r1_frontier_35x import (
    GOMORE_FRONTIER_35X_FUNCTIONS,
    R1_FRONTIER_35X_PRODUCT_FUNCTIONS,
)
from summarize_r1_frontier_334_342 import (
    GOODIX_FRONTIER_334_342_FUNCTIONS,
    GOMORE_FRONTIER_334_342_FUNCTIONS,
    R1_FRONTIER_334_342_PRODUCT_FUNCTIONS,
)
from summarize_r1_frontier_314_328 import (
    GOMORE_FRONTIER_314_328_FUNCTIONS,
    R1_FRONTIER_314_328_PRODUCT_FUNCTIONS,
)
from summarize_r1_frontier_280_308 import (
    GOODIX_FRONTIER_280_308_FUNCTIONS,
    R1_FRONTIER_280_308_PRODUCT_FUNCTIONS,
)
from summarize_r1_frontier_264_274 import (
    GOMORE_FRONTIER_264_274_FUNCTIONS,
    R1_FRONTIER_264_274_PRODUCT_FUNCTIONS,
)
from summarize_r1_frontier_256_262 import (
    GOMORE_FRONTIER_256_262_FUNCTIONS,
    R1_FRONTIER_256_262_GOODIX_ADAPTER_FUNCTIONS,
    R1_FRONTIER_256_262_PRODUCT_FUNCTIONS,
)
from summarize_r1_frontier_230_248 import (
    GOMORE_FRONTIER_230_248_FUNCTIONS,
    R1_FRONTIER_230_248_PRODUCT_FUNCTIONS,
    R1_FRONTIER_230_248_PRODUCT_HELPERS,
    SHARED_QUANTIZED_FRONTIER_230_248_FUNCTIONS,
)
from summarize_r1_frontier_224_230 import (
    NORDIC_FRONTIER_224_230_FUNCTIONS,
    R1_FRONTIER_224_230_PRODUCT_FUNCTIONS,
    R1_FRONTIER_224_230_PRODUCT_HELPERS,
    SHARED_QUANTIZED_FRONTIER_224_230_FUNCTIONS,
)
from summarize_r1_frontier_212_222 import (
    GOODIX_FRONTIER_212_222_FUNCTIONS,
    R1_FRONTIER_212_222_CMBACKTRACE_ADAPTERS,
    R1_FRONTIER_212_222_NORDIC_ADAPTERS,
    R1_FRONTIER_212_222_PRODUCT_FUNCTIONS,
    UNKNOWN_SENSOR_STREAM_FRONTIER_212_222_FUNCTIONS,
)
from summarize_r1_frontier_204_210 import (
    R1_FRONTIER_204_210_NORDIC_ADAPTERS,
    R1_FRONTIER_204_210_PRODUCT_FUNCTIONS,
    R1_FRONTIER_204_210_STORAGE_ADAPTERS,
    SHARED_TENSOR_FRONTIER_204_210_FUNCTIONS,
)
from summarize_r1_frontier_128_202 import (
    DEVICE_REGISTRY_FRONTIER_128_202_FUNCTIONS,
    GOODIX_FRONTIER_128_202_FUNCTIONS,
    GOMORE_FRONTIER_128_202_FUNCTIONS,
    NORDIC_FRONTIER_128_202_FUNCTIONS,
    QUANTIZED_RUNTIME_FRONTIER_128_202_FUNCTIONS,
    R1_FRONTIER_128_202_PRODUCT_FUNCTIONS,
    SENSOR_STREAM_FRONTIER_128_202_FUNCTIONS,
    TIME_CALENDAR_FRONTIER_128_202_FUNCTIONS,
    YHM_FRONTIER_128_202_FUNCTIONS,
)
from summarize_r1_frontier_64_127 import (
    ALL_FUNCTIONS as FRONTIER_64_127_FUNCTIONS,
    GOODIX_FRONTIER_64_127_FUNCTIONS,
    GOMORE_FRONTIER_64_127_FUNCTIONS,
    NORDIC_FRONTIER_64_127_FUNCTIONS,
    R1_FRONTIER_64_127_FUNCTIONS,
    TOOLCHAIN_FRONTIER_64_127_FUNCTIONS,
    YHM_FRONTIER_64_127_FUNCTIONS,
)
from summarize_r1_frontier_32_63 import (
    ALL_FUNCTIONS as FRONTIER_32_63_FUNCTIONS,
    GOODIX_FRONTIER_32_63_FUNCTIONS,
    GOMORE_FRONTIER_32_63_FUNCTIONS,
    R1_FRONTIER_32_63_FUNCTIONS,
)
from summarize_r1_frontier_sub32 import (
    ALL_FUNCTIONS as FRONTIER_LT32_FUNCTIONS,
    GOODIX_FRONTIER_LT32_FUNCTIONS,
    GOMORE_FRONTIER_LT32_FUNCTIONS,
    NORDIC_FRONTIER_LT32_FUNCTIONS,
    R1_FRONTIER_LT32_FUNCTIONS,
    TOOLCHAIN_FRONTIER_LT32_FUNCTIONS,
    YHM_FRONTIER_LT32_FUNCTIONS,
)
from summarize_r1_frontier_final53 import (
    ALL_FUNCTIONS as FRONTIER_FINAL53_FUNCTIONS,
    GOMORE_FRONTIER_FINAL53_FUNCTIONS,
    GOODIX_FRONTIER_FINAL53_FUNCTIONS,
    NORDIC_FRONTIER_FINAL53_FUNCTIONS,
    R1_FRONTIER_FINAL53_FUNCTIONS,
)


def _candidate_label(item: dict) -> str:
    """Deterministic short label for an unresolved-provider candidate entry."""
    import re as _re
    words = _re.findall(r"[a-z0-9]+", str(item["role"]).lower())
    label = "_".join(words[:5]) or "candidate"
    return f"{label}_{int(item['entry']):05x}"


ROOT = Path(__file__).resolve().parents[1]
DECOMP = ROOT / "research" / "decompilation"
BOOT_RECON = ROOT / "research" / "bootloader-reconstruction" / "generated"
class _DocsDir:
    """Resolve a document by name across the ``docs/`` subdirectories.

    Documents are filed by kind (``correlation/``, ``boundaries/``,
    ``closures/``, ``reference/``) while this tooling refers to them by bare
    name. Resolving here keeps both true without 118 call-site edits.
    """

    __slots__ = ("_root",)
    _SUBDIRS = ("correlation", "boundaries", "closures", "reference")

    def __init__(self, root):
        self._root = root

    def __truediv__(self, name):
        direct = self._root / name
        if direct.exists():
            return direct
        for sub in self._SUBDIRS:
            candidate = self._root / sub / name
            if candidate.exists():
                return candidate
        return direct

    def __getattr__(self, item):
        return getattr(self._root, item)

    def __fspath__(self):
        return str(self._root)

    def __str__(self):
        return str(self._root)

DOCS = _DocsDir(ROOT / "docs")
OUTPUT = DOCS / "FUNCTION-OWNERSHIP.csv"
SUMMARY = DOCS / "FUNCTION-OWNERSHIP-SUMMARY.json"
REFERENCE_OUTPUT = ROOT / "docs/reference/FUNCTION-OWNERSHIP.csv"
REFERENCE_SUMMARY = ROOT / "docs/reference/FUNCTION-OWNERSHIP-SUMMARY.json"

FIELDS = [
    "image", "inventory_source", "entry", "end", "size", "recovered_name", "provider_family",
    "source_disposition", "upstream_symbol", "confidence", "evidence",
]

DEFAULT = {
    "provider_family": "unclassified",
    "source_disposition": "investigate_before_implementing",
    "upstream_symbol": "",
    "confidence": "unclassified",
    "evidence": "No provider-specific function-local evidence has been accepted.",
}


APP_NORDIC_GPIO_SYMBOL_GROUPS = {
    "nrf_gpio_cfg": (
        0x00078DEA, 0x00078E1C, 0x00078E82, 0x00078EB4, 0x00078EE6,
        0x00078F18, 0x00078F4A, 0x00078F7C, 0x00078FB0,
    ),
    "nrf_gpio_cfg_default": (0x0007903E, 0x00079050),
    "nrf_gpio_cfg_input": (
        0x00079062, 0x00079074, 0x00079086, 0x00079098, 0x000790AA,
    ),
    "nrf_gpio_cfg_output": (
        0x000790BC, 0x000790D0, 0x000790E4, 0x000790F8, 0x0007910C,
    ),
    "nrf_gpio_cfg_sense_set": (0x00079120,),
    "nrf_gpio_latches_read_and_clear": (0x00079150,),
    "nrf_gpio_pin_clear": (0x0007920C, 0x00079220),
    "nrf_gpio_pin_port_decode": (
        0x00079234, 0x00079250, 0x00079288, 0x000792A4, 0x000792C0,
        0x000792DC, 0x000792F8, 0x00079314, 0x00079330, 0x0007934C,
        0x00079368,
    ),
    "nrf_gpio_pin_read": (
        0x000793B0, 0x000793C6, 0x000793DC, 0x000793F2, 0x00079408,
        0x0007941E,
    ),
    "nrf_gpio_pin_set": (
        0x00079434, 0x00079448, 0x0007945C, 0x00079470, 0x00079484,
        0x00079498, 0x000794AC, 0x000794C0, 0x000794D4, 0x000794E8,
    ),
}

APP_NORDIC_GPIOTE_SYMBOLS = {
    0x000794FC: "nrf_gpiote_event_clear",
    0x00079510: "nrf_gpiote_event_is_set",
}

APP_NORDIC_HAL_INLINE_SYMBOLS = {
    0x0007A58A: "nrf_spim_event_check",
    0x00079CDC: "nrf_nfct_event_check",
    0x00079CEC: "nrf_nfct_event_clear",
    0x00079CFC: "nrf_nfct_int_enable_check",
    0x00079D14: "nrf_pdm_event_check",
    0x00079D24: "nrf_pdm_event_clear",
    0x00079D38: "nrf_pwm_event_check",
    0x00079D42: "nrf_pwm_event_clear",
    0x00079DE8: "nrf_rtc_event_clear",
    0x00079DF4: "nrf_rtc_event_clear",
    0x00079E00: "nrf_saadc_buffer_init",
    0x00079E24: "nrf_saadc_event_check",
    0x00079E34: "nrf_saadc_event_clear",
    0x0007A60C: "nrf_timer_event_clear",
    0x0007A618: "nrf_twim_event_check",
    0x0007A622: "nrf_twim_event_clear",
}

APP_NORDIC_HAL_INLINE_SOURCES = {
    0x0007A58A: "modules/nrfx/hal/nrf_spim.h",
    0x00079CDC: "modules/nrfx/hal/nrf_nfct.h",
    0x00079CEC: "modules/nrfx/hal/nrf_nfct.h",
    0x00079CFC: "modules/nrfx/hal/nrf_nfct.h",
    0x00079D14: "modules/nrfx/hal/nrf_pdm.h",
    0x00079D24: "modules/nrfx/hal/nrf_pdm.h",
    0x00079D38: "modules/nrfx/hal/nrf_pwm.h",
    0x00079D42: "modules/nrfx/hal/nrf_pwm.h",
    0x00079DE8: "modules/nrfx/hal/nrf_rtc.h",
    0x00079DF4: "modules/nrfx/hal/nrf_rtc.h",
    0x00079E00: "modules/nrfx/hal/nrf_saadc.h",
    0x00079E24: "modules/nrfx/hal/nrf_saadc.h",
    0x00079E34: "modules/nrfx/hal/nrf_saadc.h",
    0x0007A60C: "modules/nrfx/hal/nrf_timer.h",
    0x0007A618: "modules/nrfx/hal/nrf_twim.h",
    0x0007A622: "modules/nrfx/hal/nrf_twim.h",
}

APP_NORDIC_CLOCK_DRIVER_SYMBOLS = {
    0x0003BC78: "__sd_nvic_app_accessible_irq",
    0x0004EBEC: "sd_nvic_critical_region_enter",
    0x0004EC34: "sd_nvic_critical_region_exit",
    0x000584AC: "clock_clk_started_notify",
    0x000584D4: "clock_irq_handler",
    0x00072BCA: "item_enqueue",
    0x000788C8: "nrf_drv_clock_init",
    0x00078990: "nrf_drv_clock_lfclk_request",
    0x00090814: "softdevice_evt_irq_disable",
    0x00090854: "softdevices_evt_irq_enable",
    0x0007A630: "nrf_wdt_started",
    0x0007A640: "nrfx_clock_enable",
    0x0007A66C: "nrfx_clock_init",
    0x0007A68C: "nrfx_clock_lfclk_start",
}

APP_NORDIC_CLOCK_DRIVER_SOURCES = {
    0x0003BC78: "components/softdevice/s140/headers/nrf_nvic.h",
    0x0004EBEC: "components/softdevice/s140/headers/nrf_nvic.h",
    0x0004EC34: "components/softdevice/s140/headers/nrf_nvic.h",
    0x000584AC: "integration/nrfx/legacy/nrf_drv_clock.c",
    0x000584D4: "integration/nrfx/legacy/nrf_drv_clock.c",
    0x00072BCA: "integration/nrfx/legacy/nrf_drv_clock.c",
    0x000788C8: "integration/nrfx/legacy/nrf_drv_clock.c",
    0x00078990: "integration/nrfx/legacy/nrf_drv_clock.c",
    0x00090814: "components/softdevice/common/nrf_sdh.c",
    0x00090854: "components/softdevice/common/nrf_sdh.c",
    0x0007A630: "modules/nrfx/hal/nrf_wdt.h",
    0x0007A640: "modules/nrfx/drivers/src/nrfx_clock.c",
    0x0007A66C: "modules/nrfx/drivers/src/nrfx_clock.c",
    0x0007A68C: "modules/nrfx/drivers/src/nrfx_clock.c",
}

APP_NORDIC_WDT_DRIVER_SYMBOLS = {
    int(item["entry"]): str(item["symbol"])
    for item in WATCHDOG_DEVICE_FUNCTIONS
    if item["provider_family"] == "nordic_nrf5_sdk_17_1_0"
}

APP_NORDIC_WDT_DRIVER_SOURCES = {
    entry: "modules/nrfx/drivers/src/nrfx_wdt.c"
    for entry in APP_NORDIC_WDT_DRIVER_SYMBOLS
}

APP_NORDIC_DELAY_MS_ENTRIES = (
    0x000784B0, 0x000784D0, 0x000784F0, 0x00078510,
    0x00078530, 0x00078550, 0x00078570, 0x0007F15C,
)

APP_NORDIC_DELAY_MACHINE_CODE_ENTRIES = (
    0x00099340, 0x00099CB0, 0x00099CC0, 0x00099CD0, 0x00099CE0,
    0x00099CF0, 0x00099D00, 0x00099D10, 0x0009A5F0, 0x0009A610,
    0x0009A670, 0x0009A6A0, 0x0009A710, 0x0009BB10, 0x0009C9E0,
)

APP_NORDIC_DELAY_TWI_SYMBOLS = {
    0x0002EB34: "nrf_delay_ms",
    0x00078490: "nrf_power_event_check",
    0x0007849E: "nrf_power_event_clear",
    0x0007A71C: "nrfx_coredep_delay_us",
    0x0007A72C: "nrfx_coredep_delay_us",
    0x000938BC: "twi_clear_bus",
    **{entry: "nrf_delay_ms" for entry in APP_NORDIC_DELAY_MS_ENTRIES},
    **{
        entry: "nrfx_coredep_delay_us::delay_machine_code"
        for entry in APP_NORDIC_DELAY_MACHINE_CODE_ENTRIES
    },
}

APP_NORDIC_DELAY_TWI_SOURCES = {
    0x0002EB34: "components/libraries/delay/nrf_delay.h",
    0x00078490: "modules/nrfx/hal/nrf_power.h",
    0x0007849E: "modules/nrfx/hal/nrf_power.h",
    0x0007A71C: "modules/nrfx/soc/nrfx_coredep.h",
    0x0007A72C: "modules/nrfx/soc/nrfx_coredep.h",
    0x000938BC: "integration/nrfx/legacy/nrf_drv_twi.c",
    **{
        entry: "components/libraries/delay/nrf_delay.h"
        for entry in APP_NORDIC_DELAY_MS_ENTRIES
    },
    **{
        entry: "modules/nrfx/soc/nrfx_coredep.h"
        for entry in APP_NORDIC_DELAY_MACHINE_CODE_ENTRIES
    },
}


APP_NORDIC_GPIOTE_DRIVER_SYMBOLS = {
    0x0002D3B4: "nrfx_gpiote_irq_handler",
    0x00057934: "channel_free",
    0x00057950: "channel_port_alloc",
    0x00057998: "channel_port_get",
    0x00078176: "nrf_bitmask_bit_is_set",
    0x0007A73C: "nrfx_gpiote_in_event_disable",
    0x0007A784: "nrfx_gpiote_in_event_enable",
    0x0007A81C: "nrfx_gpiote_in_init",
    0x0007A8EC: "nrfx_gpiote_in_uninit",
    0x0007F0E0: "pin_configured_check",
    0x0007F0F4: "pin_configured_clear",
    0x0007F110: "pin_configured_set",
    0x0007F12C: "pin_in_use_by_port",
    0x0007F144: "pin_in_use_by_te",
    0x00080F78: "port_handler_polarity_get",
    0x00080EA8: "port_event_handle",
}

APP_NORDIC_GPIOTE_DRIVER_SOURCES = {
    entry: "modules/nrfx/drivers/src/nrfx_gpiote.c"
    for entry in APP_NORDIC_GPIOTE_DRIVER_SYMBOLS
}
APP_NORDIC_GPIOTE_DRIVER_SOURCES[0x00078176] = "components/libraries/util/nrf_bitmask.h"


APP_NORDIC_TWI_DRIVER_SYMBOLS = {
    0x00031A74: "nrfx_twim_0_irq_handler",
    0x00031A84: "nrfx_twim_1_irq_handler",
    0x000789E4: "nrf_drv_twi_init",
    0x00078A24: "nrf_drv_twi_tx",
    0x00078A32: "nrf_drv_twi_tx",
    0x0007AC04: "nrfx_is_in_ram",
    0x0007ACD4: "nrfx_prs_acquire",
    0x0007AD0E: "nrfx_prs_release",
    0x0007B22C: "nrfx_twim_disable",
    0x0007B268: "nrfx_twim_enable",
    0x0007B370: "nrfx_twim_rx",
    0x0007B3A0: "nrfx_twim_tx",
    0x0007B3D8: "nrfx_twim_uninit",
    0x0007B448: "nrfx_twim_xfer",
    0x00084CD8: "prs_box_get",
    **{
        int(function["entry"]): str(function["symbol"])
        for function in NORDIC_TWIM_COMPLETENESS_FUNCTIONS
    },
}

APP_NORDIC_TWI_DRIVER_SOURCES = {
    entry: "modules/nrfx/drivers/src/nrfx_twim.c"
    for entry in APP_NORDIC_TWI_DRIVER_SYMBOLS
}
for _function in NORDIC_TWIM_COMPLETENESS_FUNCTIONS:
    APP_NORDIC_TWI_DRIVER_SOURCES[int(_function["entry"])] = str(_function["source"])
APP_NORDIC_TWI_DRIVER_SOURCES[0x000789E4] = "integration/nrfx/legacy/nrf_drv_twi.c"
APP_NORDIC_TWI_DRIVER_SOURCES[0x00078A24] = "integration/nrfx/legacy/nrf_drv_twi.h"
APP_NORDIC_TWI_DRIVER_SOURCES[0x00078A32] = "integration/nrfx/legacy/nrf_drv_twi.h"
APP_NORDIC_TWI_DRIVER_SOURCES[0x0007AC04] = "modules/nrfx/drivers/nrfx_common.h"
for _prs_entry in (0x0007ACD4, 0x0007AD0E, 0x00084CD8):
    APP_NORDIC_TWI_DRIVER_SOURCES[_prs_entry] = "modules/nrfx/drivers/src/prs/nrfx_prs.c"


APP_NORDIC_SPIM_DRIVER_SYMBOLS = {
    0x00031A94: "nrfx_spim_2_irq_handler",
}

APP_NORDIC_SPIM_DRIVER_SOURCES = {
    entry: "modules/nrfx/drivers/src/nrfx_spim.c"
    for entry in APP_NORDIC_SPIM_DRIVER_SYMBOLS
}


APP_NORDIC_RTC_TIMER_DRIVER_SYMBOLS = {
    0x00031750: "nrfx_rtc_2_irq_handler",
    0x00033828: "nrfx_timer_2_irq_handler",
    0x0003383C: "nrfx_timer_4_irq_handler",
    0x0007294C: "irq_handler",
    0x000729EC: "irq_handler",
    0x0007AD20: "nrfx_rtc_enable",
    0x0007AD6C: "nrfx_rtc_init",
    0x0007AE4C: "nrfx_rtc_tick_enable",
    0x0007B1C4: "nrfx_timer_clear",
    0x0007B1CC: "nrfx_timer_enable",
}

APP_NORDIC_RTC_TIMER_DRIVER_SOURCES = {
    0x00031750: "modules/nrfx/drivers/src/nrfx_rtc.c",
    0x00033828: "modules/nrfx/drivers/src/nrfx_timer.c",
    0x0003383C: "modules/nrfx/drivers/src/nrfx_timer.c",
    0x0007294C: "modules/nrfx/drivers/src/nrfx_rtc.c",
    0x000729EC: "modules/nrfx/drivers/src/nrfx_timer.c",
    0x0007AD20: "modules/nrfx/drivers/src/nrfx_rtc.c",
    0x0007AD6C: "modules/nrfx/drivers/src/nrfx_rtc.c",
    0x0007AE4C: "modules/nrfx/drivers/src/nrfx_rtc.c",
    0x0007B1C4: "modules/nrfx/drivers/src/nrfx_timer.c",
    0x0007B1CC: "modules/nrfx/drivers/src/nrfx_timer.c",
}


APP_NORDIC_NFCT_DRIVER_SYMBOLS = {
    0x0003060C: "nrfx_nfct_irq_handler",
    0x0007AC14: "nrfx_nfct_field_check",
    0x0007AC24: "nrfx_nfct_field_event_handler",
    0x0007ACB8: "nrfx_nfct_frame_delay_max_set",
}

APP_NORDIC_NFCT_DRIVER_SOURCES = {
    entry: "modules/nrfx/drivers/src/nrfx_nfct.c"
    for entry in APP_NORDIC_NFCT_DRIVER_SYMBOLS
}


APP_NORDIC_PEER_MANAGER_EXACT_SYMBOLS = {
    0x0007F276: "pm_conn_sec_config_reply",
    0x0007F280: "pm_conn_sec_status_get",
    0x0007F294: "pm_conn_secure",
    0x00080980: "pm_pdb_evt_handler",
    0x00080A98: "pm_peer_data_bonding_load",
    0x00080AAC: "pm_peer_data_load",
    0x00080AD4: "pm_peer_delete",
    0x00080AE8: "pm_peer_rank_highest",
    0x00080C38: "pm_peer_ranks_get",
    0x00080D5C: "pm_peers_delete",
    0x00080E28: "pm_register",
    0x00080E54: "pm_sec_params_set",
    0x00080E68: "pm_sm_evt_handler",
}

APP_NORDIC_PEER_MANAGER_EXACT_SOURCES = {
    entry: "components/ble/peer_manager/peer_manager.c"
    for entry in APP_NORDIC_PEER_MANAGER_EXACT_SYMBOLS
}


APP_NORDIC_SECURITY_DISPATCHER_EXACT_SYMBOLS = {
    0x0004C6D0: "allow_repairing",
    0x00059C68: "conn_sec_failure",
    0x0005D314: "encryption_failure",
    0x00075038: "link_secure_failure",
    0x0007E2F0: "pairing",
    0x0007E3A4: "pairing_success_evt_send",
    0x000891B8: "sec_info_request_process",
    0x0008965A: "send_config_req",
    0x000896C8: "send_unexpected_error",
    0x00090334: "smd_conn_sec_config_reply",
    0x000906C8: "smd_link_secure",
    0x000906F0: "smd_params_reply",
}

APP_NORDIC_SECURITY_DISPATCHER_EXACT_SOURCES = {
    entry: "components/ble/peer_manager/security_dispatcher.c"
    for entry in APP_NORDIC_SECURITY_DISPATCHER_EXACT_SYMBOLS
}

APP_NORDIC_SECURITY_MANAGER_EXACT_SYMBOLS = {
    0x0005EB94: "events_send_from_err_code",
    0x0005ED08: "evt_send",
    0x00064F44: "flags_set_from_err_code",
    0x00074F38: "link_secure",
    0x00075074: "link_secure_pending_handle",
    0x0007719C: "new_context_get",
    0x000771B0: "new_evt",
    0x0007E3D8: "params_req_send",
    0x00089598: "sec_req_process",
}

APP_NORDIC_SECURITY_MANAGER_EXACT_SOURCES = {
    entry: "components/ble/peer_manager/security_manager.c"
    for entry in APP_NORDIC_SECURITY_MANAGER_EXACT_SYMBOLS
}

APP_NORDIC_GATT_CACHE_EXACT_SYMBOLS = {
    **{int(x["entry"]): str(x["symbol"]) for x in NORDIC_GATT_CACHE_CLOSURE_FUNCTIONS},
    0x000896A0: "send_unexpected_error",
}

APP_NORDIC_GATT_CACHE_EXACT_SOURCES = {
    entry: "components/ble/peer_manager/gatt_cache_manager.c"
    for entry in APP_NORDIC_GATT_CACHE_EXACT_SYMBOLS
}
for _function in NORDIC_GATT_CACHE_CLOSURE_FUNCTIONS:
    APP_NORDIC_GATT_CACHE_EXACT_SOURCES[int(_function["entry"])] = str(_function["source"])

APP_NORDIC_BLE_STATIC_HELPER_SYMBOLS = {
    int(function["entry"]): str(function["symbol"])
    for function in NORDIC_BLE_STATIC_HELPER_FUNCTIONS
}

APP_NORDIC_BLE_STATIC_HELPER_SOURCES = {
    int(function["entry"]): str(function["source"])
    for function in NORDIC_BLE_STATIC_HELPER_FUNCTIONS
}

APP_NORDIC_ADVERTISING_SYMBOLS = {
    int(function["entry"]): str(function["symbol"])
    for function in NORDIC_ADVERTISING_FUNCTIONS
}

APP_NORDIC_ADVERTISING_SOURCES = {
    int(function["entry"]): str(function["source"])
    for function in NORDIC_ADVERTISING_FUNCTIONS
}

APP_NORDIC_BUTTONLESS_DFU_SYMBOLS = {
    int(function["entry"]): str(function["symbol"])
    for function in NORDIC_BUTTONLESS_DFU_FUNCTIONS
}

APP_NORDIC_BUTTONLESS_DFU_SOURCES = {
    int(function["entry"]): str(function["source"])
    for function in NORDIC_BUTTONLESS_DFU_FUNCTIONS
}

APP_NORDIC_POWER_MANAGEMENT_SYMBOLS = {
    int(function["entry"]): str(function["symbol"])
    for function in NORDIC_POWER_MANAGEMENT_FUNCTIONS
}

APP_NORDIC_POWER_MANAGEMENT_SOURCES = {
    int(function["entry"]): "components/libraries/pwr_mgmt/nrf_pwr_mgmt.c"
    for function in NORDIC_POWER_MANAGEMENT_FUNCTIONS
}

APP_NORDIC_SAADC_DRIVER_SYMBOLS = {
    0x000317CC: "nrfx_saadc_irq_handler",
    0x0007AEAC: "nrfx_saadc_channel_init",
    0x0007AF38: "nrfx_saadc_channel_uninit",
    0x0007AF7C: "nrfx_saadc_init",
    0x0007B010: "nrfx_saadc_limits_set",
    0x0007B090: "nrfx_saadc_sample_convert",
    0x0007B150: "nrfx_saadc_uninit",
}

APP_NORDIC_SAADC_DRIVER_SOURCES = {
    entry: "modules/nrfx/drivers/src/nrfx_saadc.c"
    for entry in APP_NORDIC_SAADC_DRIVER_SYMBOLS
}


# Ghidra retained the 0x00031fcc entry as a four-byte NOP-only function even
# though every caller enters there and execution falls through the complete
# battery service body. The corrected extent ends immediately before its
# literal pool and the next independent function.
APP_INVENTORY_EXTENT_OVERRIDES = {
    0x00031FCC: 0x19C,
    # Ghidra's body-size field omits the final two-byte back-edge even though
    # its inclusive end and the recovered instruction stream end at 0x3190b.
    0x000317CC: 0x140,
    # Ghidra's body-size field omits the final two-byte return back-edge even
    # though its inclusive end and disassembly extend through 0x326b1.
    0x00032598: 0x11A,
    # Ghidra's decimal size omits the final ten bytes even though its inclusive
    # end and the recovered control flow continue through 0x00081853.
    0x00081744: 0x110,
    # Ghidra's decimal size omits the final case-4 and default branches even
    # though its inclusive end and disassembly continue through 0x00062b4b.
    0x00062A5C: 0xF0,
    # Ghidra's decimal size stops eight bytes before the independently pinned
    # event-14 consumer return boundary at 0x0008ba80.
    0x0008B8E8: 0x198,
    # These decimal sizes each omit the final six executable bytes even though
    # the inclusive ends and recovered disassembly retain those instructions.
    0x000628F6: 0xDC,
    0x00063D50: 0xDA,
    0x0008EF28: 0xE0,
}


# Exact executable extents established independently of Ghidra's function
# inventory. Most manual provenance supplements intentionally retain blank
# extents. The two CLOCK statics and the FlashDB helpers below have
# unambiguous return/tail-call or callback boundaries, so their full bodies can
# be byte-pinned.
APP_MANUAL_SUPPLEMENT_EXTENTS = {
    # Installed by descriptor constructor 0x74BE0 as Thumb token 0x85B9D;
    # Ghidra missed the complete float dense executor before its literal pool.
    0x00085B9C: 252,
    # Ghidra emitted only LAB_00085dc4+1 even though the constructor at
    # 0x74B44 installs this complete Thumb executor and its next independent
    # prologue is byte-pinned at 0x86BAC.
    0x00085DC4: 3560,
    0x0003C0D8: 272,
    0x0003FCEC: 272,
    0x00040BD4: 272,
    0x00043EB0: 272,
    0x000584AC: 32,
    0x000584D4: 24,
    0x00059C68: 60,
    0x0007294C: 154,
    0x000729EC: 70,
    0x0006A158: 30,
    0x0006A176: 30,
    0x00087428: 18,
    0x00090334: 4,
    0x00067488: 196,
    0x0006825C: 232,
    0x0006B114: 164,
    0x0006B228: 74,
    0x0007D09C: 12,
    0x0008F49C: 24,
    0x000502AC: 20,
    0x0006F1A8: 20,
    0x0006F1BC: 30,
    0x0006F1DA: 2,
    0x0006F380: 20,
    0x0006F394: 30,
    0x0006F3B2: 2,
    0x0006F400: 4,
    0x0006F404: 20,
    0x000552E4: 66,
    0x00054F90: 44,
    0x00054FC4: 44,
    0x00056508: 18,
    0x00056520: 18,
    0x00056538: 18,
    0x00056550: 18,
    0x0006F418: 30,
    0x0006F436: 18,
    0x0006F448: 84,
    0x0006F4A0: 154,
    0x00054970: 24,
    0x0005498C: 90,
    0x000549F0: 78,
    0x00054A4C: 58,
    0x00054A8C: 20,
    0x00054AA4: 72,
    0x0005C40C: 80,
    0x0005C464: 24,
    0x0005C480: 62,
    0x0005DC08: 86,
    0x0005BCEC: 220,
    0x0005BE7C: 248,
    0x0005BB2C: 224,
    0x0008A8D8: 36,
    0x0008A8AE: 42,
    0x0008A8FC: 44,
    0x00082BE8: 36,
    0x00082C10: 52,
    0x00082C44: 70,
    0x00082C8A: 68,
    0x00082CCE: 70,
    0x00082D14: 70,
    0x00082D5A: 68,
    0x00082E34: 50,
    0x00082E66: 52,
    0x00082E9A: 52,
    0x00049068: 252,
    0x00091918: 56,
    0x00054864: 140,
    0x000548F0: 76,
    0x0007AEAC: 140,
    0x0007AF38: 68,
    0x0007AF7C: 148,
    0x0007B010: 128,
    0x0007B090: 192,
    0x0007B150: 116,
}
APP_MANUAL_SUPPLEMENT_EXTENTS.update({
    int(item["entry"]): int(item["size"])
    for item in SOFTWARE_TWI_FUNCTIONS
})
APP_MANUAL_SUPPLEMENT_EXTENTS.update({
    int(item["entry"]): int(item["size"])
    for item in R1_NV_RECOVERY_FUNCTIONS
    if item["inventory"] == "manual_provenance_supplement"
})
APP_MANUAL_SUPPLEMENT_EXTENTS.update({
    int(item["entry"]): int(item["size"])
    for item in RTC_DEVICE_FUNCTIONS
})
APP_MANUAL_SUPPLEMENT_EXTENTS.update({
    int(item["entry"]): int(item["size"])
    for item in YHM2710_STACMD_FUNCTIONS
})
APP_MANUAL_SUPPLEMENT_EXTENTS.update({
    int(item["entry"]): int(item["size"])
    for item in WATCHDOG_DEVICE_FUNCTIONS
})
APP_MANUAL_SUPPLEMENT_EXTENTS.update({
    int(item["entry"]): int(item["size"])
    for item in NORDIC_BUTTONLESS_DFU_FUNCTIONS
})
APP_MANUAL_SUPPLEMENT_EXTENTS.update({
    int(item["entry"]): int(item["size"])
    for item in GOODIX_SPO2_DLCOM_ALL_FUNCTIONS
    if item["inventory"] == "manual_provenance_supplement"
})
APP_MANUAL_SUPPLEMENT_EXTENTS.update({
    int(item["entry"]): int(item["size"])
    for item in R1_TOUCH_SLIDER_FUNCTIONS
    if item["inventory"] == "manual_provenance_supplement"
})
APP_MANUAL_SUPPLEMENT_EXTENTS.update({
    int(item["entry"]): int(item["size"])
    for item in R1_STRUCTURED_LOG_FUNCTIONS
    if item["inventory"] == "manual_provenance_supplement"
})


# Product behavior already established by the decompilation/audit corpus. This
# does not claim original authorship: it records that no third-party implementation
# has been identified and that only behavior may inform an independent implementation.
APP_PRODUCT_FUNCTIONS = {
    0x00031FCC: "r1_battery_runtime_service",
    0x0003DB70: "r1_battery_stuck_charge_recovery",
    0x0003DD0C: "r1_battery_charged_state_refresh",
    0x0003BDD8: "r1_activity_offline_queue_consume",
    0x0003BCF8: "r1_activity_acknowledgement_timestamp_clamp",
    0x0003BDAC: "r1_activity_day_builder_reset",
    0x0003BED0: "r1_activity_offline_queue_empty",
    0x0003BEE4: "r1_activity_offline_queue_enqueue",
    0x0003C0D8: "r1_activity_sync_acknowledgement",
    0x0003C304: "r1_activity_ram_cache_merge",
    0x0003C578: "r1_activity_day_packet_flush",
    0x0003C958: "r1_activity_flash_record_merge",
    0x0003CB80: "r1_activity_offline_queue_merge",
    0x0003FAA4: "r1_heart_rate_offline_queue_consume",
    0x0003FB90: "r1_heart_rate_offline_queue_empty",
    0x0003FBA4: "r1_heart_rate_offline_queue_enqueue",
    0x0003FCEC: "r1_heart_rate_sync_acknowledgement",
    0x00040700: "r1_heart_rate_offline_queue_merge",
    0x00040984: "r1_hrv_offline_queue_consume",
    0x00040A74: "r1_hrv_offline_queue_empty",
    0x00040A88: "r1_hrv_offline_queue_enqueue",
    0x00040BD4: "r1_hrv_sync_acknowledgement",
    0x00041638: "r1_hrv_offline_queue_merge",
    0x00043CA0: "r1_spo2_offline_queue_consume",
    0x00043D90: "r1_spo2_offline_queue_empty",
    0x00043DA4: "r1_spo2_offline_queue_enqueue",
    0x00043EB0: "r1_spo2_sync_acknowledgement",
    0x000448B0: "r1_spo2_offline_queue_merge",
    0x00048288: "r1_activity_daily_cache_reset",
    0x000482A8: "r1_activity_daily_cache_read",
    0x0004832C: "r1_activity_daily_cache_write",
    0x0005A9F0: "r1_activity_daily_cache_accessor",
    0x0005A9F8: "r1_activity_daily_cache_refresh_metadata",
    0x0005A28C: "r1_health_crash_record_validator",
    0x0005A2B8: "r1_health_crash_record_initializer",
    0x0005A324: "r1_health_crash_snapshot_builder",
    0x00058914: "r1_health_crash_provider_blob_clear",
    0x0005893C: "r1_health_crash_snapshot_clear",
    0x00058960: "r1_health_crash_time_clear",
    0x00058980: "r1_health_crash_provider_blob_accessor",
    0x000589B0: "r1_health_crash_snapshot_accessor",
    0x000589E8: "r1_health_crash_time_accessor",
    0x00058A24: "r1_health_crash_record_magic_probe",
    0x00059EE4: "r1_health_crash_snapshot_restore",
    0x00070030: "r1_health_database_startup_orchestrator",
    0x0007F030: "r1_retained_log_printf_sink",
    0x00048D48: "r1_activity_pending_delta_accessor",
    0x00048E68: "r1_activity_periodic_accumulator",
    0x00049068: "r1_activity_explicit_refresh_accumulator",
    0x0005AA14: "r1_activity_delta_cache_accumulator",
    0x0007062C: "r1_heart_rate_daily_cache_reset",
    0x00070648: "r1_heart_rate_daily_cache_read",
    0x000706A4: "r1_heart_rate_daily_cache_write",
    0x000706BE: "r1_hrv_daily_cache_reset",
    0x000706D8: "r1_hrv_daily_cache_read",
    0x0007073C: "r1_hrv_daily_cache_write",
    0x00090DD4: "r1_spo2_daily_cache_reset",
    0x00090DF0: "r1_spo2_daily_cache_read",
    0x00090E4C: "r1_spo2_daily_cache_write",
    0x0005ABA0: "r1_shared_u8_hourly_average",
    0x0005AB6C: "r1_shared_hourly_accumulator_snapshot",
    0x0005ACC4: "r1_shared_hourly_accumulator_restore",
    0x0005ACE0: "r1_heart_rate_daily_cache_accessor",
    0x0005ACE8: "r1_heart_rate_latest_sample_accessor",
    0x0005AD08: "r1_heart_rate_daily_cache_refresh_metadata",
    0x0005AD90: "r1_heart_rate_sample_storage_aggregator",
    0x0005AF18: "r1_hrv_daily_cache_accessor",
    0x0005AF20: "r1_hrv_latest_sample_accessor",
    0x0005AF44: "r1_hrv_daily_cache_refresh_metadata",
    0x0005AF60: "r1_hrv_sample_storage_aggregator",
    0x0005BAEC: "r1_spo2_daily_cache_accessor",
    0x0005BAF4: "r1_spo2_latest_sample_accessor",
    0x0005BB14: "r1_spo2_daily_cache_refresh_metadata",
    0x0005BB2C: "r1_spo2_sample_storage_aggregator",
    0x0005BCCC: "r1_stress_daily_cache_accessor",
    0x0005BCD4: "r1_stress_daily_cache_refresh_metadata",
    0x0005BCEC: "r1_stress_sample_storage_aggregator",
    0x0005BE5C: "r1_temperature_daily_cache_accessor",
    0x0005BE64: "r1_temperature_daily_cache_refresh_metadata",
    0x0005BE7C: "r1_temperature_sample_storage_aggregator",
    0x0008A8D8: "r1_stress_event_storage_consumer",
    0x0008A80A: "r1_heart_rate_event_storage_consumer",
    0x0008A83E: "r1_hrv_event_storage_consumer",
    0x0008A8AE: "r1_spo2_event_storage_consumer",
    0x0008A8FC: "r1_temperature_event_storage_consumer",
    0x0008A7F4: "r1_activity_event_storage_consumer",
    0x00091124: "r1_stress_daily_cache_reset",
    0x0009113E: "r1_stress_daily_cache_read",
    0x00091158: "r1_stress_daily_cache_write",
    0x000918DE: "r1_temperature_daily_cache_reset",
    0x00091918: "r1_temperature_daily_cache_read",
    0x00091954: "r1_temperature_daily_cache_write",
    0x0003E274: "r1_output_dispatch",
    0x00044F50: "r1_output_worker",
    0x00048B02: "r1_dual_aes128_decrypt",
    0x0004CBB0: "r1_authenticated_phone_connection_gate",
    0x0004A24C: "r1_hrv_producer",
    0x0004FE5C: "r1_battery_charging_progress_reset",
    0x0004FE70: "r1_battery_charging_cadence",
    0x0004FF3C: "r1_battery_charging_initial_curve",
    0x00050004: "r1_battery_discharge_curve",
    0x000526CC: "r1_bae8_hvx_send",
    0x00052B20: "r1_bae8_raw_observer",
    0x000575D8: "r1_hrv_rmssd",
    0x0005B39C: "r1_sleep_sync_iterator",
    0x0005B6F4: "r1_sleep_sync_marker",
    0x0005D87C: "r1_crc16_modbus",
    0x0005D8A4: "r1_crc32_castagnoli",
    0x0007BA78: "r1_device_serial_get",
    0x00082BE8: "r1_health_registration_dispatcher",
    0x00083298: "r1_health_registration_binary_search",
    0x00082C10: "r1_activity_refresh_handler",
    0x00082C44: "r1_activity_daily_handler",
    0x00082C8A: "r1_heart_rate_daily_handler",
    0x00082CCE: "r1_hrv_daily_handler",
    0x00082D14: "r1_sleep_daily_handler",
    0x00082D5A: "r1_spo2_daily_handler",
    0x00082E34: "r1_heart_rate_point_handler",
    0x00082E66: "r1_hrv_point_handler",
    0x00082E9A: "r1_spo2_point_handler",
    0x00083930: "r1_heart_rate_point_response_wrapper",
    0x00083972: "r1_hrv_point_response_wrapper",
    0x00083028: "r1_ack_resolver",
    0x00083872: "r1_system_response_wrapper",
    0x00083D5C: "r1_device_info_handler",
    0x00083DB0: "r1_device_serial_handler",
    0x00083DE4: "r1_device_status_handler",
    0x000842CC: "r1_packet_ack_handler",
    0x000842EC: "r1_pair_role_handler",
    0x00084A10: "r1_user_profile_handler",
    0x000891A4: "r1_dual_aes128_decrypt_callback",
    0x0008B8E8: "r1_health_event14_consumer",
    0x0008B138: "r1_automatic_health_sync_gate",
    0x0008B818: "r1_unsynchronized_sleep_batch_sync",
    0x0008BAEC: "r1_activity_history_sync",
    0x0008C150: "r1_heart_rate_history_sync",
    0x0008C750: "r1_hrv_history_sync",
    0x0008CD60: "r1_spo2_history_sync",
    0x0008FC6C: "r1_sleep_sector_select",
    0x0008FE28: "r1_sleep_writable_sector_find",
    0x0008FE98: "r1_sleep_journal_append",
    0x000901E4: "r1_sleep_sector_close",
    0x00098E22: "r1_xor_bytes",
}
APP_PRODUCT_FUNCTIONS.update({
    int(item["entry"]): str(item["symbol"])
    for item in R1_RESET_TRACE_FUNCTIONS
    if int(item["entry"]) != 0x0007A5E0
})
APP_PRODUCT_FUNCTIONS.update({
    int(item["entry"]): str(item["symbol"])
    for item in R1_NV_RECOVERY_FUNCTIONS
})

APP_PRODUCT_SECURITY_PRESERVING = {
    int(item["entry"]): str(item["symbol"])
    for item in R1_NV_RECOVERY_FUNCTIONS
}
APP_PRODUCT_SECURITY_PRESERVING.update({
    int(item["entry"]): str(item["symbol"])
    for item in R1_NV_COMPILED_RESTORE_FUNCTIONS
})
APP_PRODUCT_SECURITY_PRESERVING.update({
    int(item["entry"]): str(item["symbol"])
    for item in R1_EUS_RX_REASSEMBLY_FUNCTIONS
})
APP_PRODUCT_FUNCTIONS.update({
    int(item["entry"]): str(item["symbol"])
    for item in R1_RESET_REASON_FUNCTIONS
    if int(item["entry"]) == 0x0008198C
})
APP_PRODUCT_FUNCTIONS.update({
    int(item["entry"]): str(item["symbol"])
    for item in R1_CONNECTION_CONTROL_FUNCTIONS
})
APP_PRODUCT_FUNCTIONS.update({
    int(item["entry"]): str(item["symbol"])
    for item in R1_PEER_MANAGER_EVENT_FUNCTIONS
})
APP_PRODUCT_FUNCTIONS.update({
    int(item["entry"]): str(item["symbol"])
    for item in R1_TOUCH_SLIDER_FUNCTIONS
})
APP_PRODUCT_FUNCTIONS.update({
    int(item["entry"]): str(item["symbol"])
    for item in R1_HEALTH_DAILY_TEST_FUNCTIONS
})
APP_PRODUCT_FUNCTIONS.update({
    int(item["entry"]): str(item["symbol"])
    for item in R1_STRUCTURED_LOG_FUNCTIONS
})
APP_PRODUCT_FUNCTIONS.update({
    int(item["entry"]): str(item["symbol"])
    for item in R1_LOG_BIN_WRITER_FUNCTIONS
})
APP_PRODUCT_FUNCTIONS.update({
    int(item["entry"]): str(item["symbol"])
    for item in R1_HRV_SYNC_FLUSH_FUNCTIONS
})
APP_PRODUCT_FUNCTIONS.update({
    int(item["entry"]): str(item["symbol"])
    for item in R1_HR_SYNC_FLUSH_FUNCTIONS
})
APP_PRODUCT_FUNCTIONS.update({
    int(item["entry"]): str(item["symbol"])
    for item in R1_SPO2_SYNC_FLUSH_FUNCTIONS
})
APP_PRODUCT_FUNCTIONS.update({
    int(item["entry"]): str(item["symbol"])
    for item in R1_WEAR_FUSION_FUNCTIONS
})
APP_PRODUCT_FUNCTIONS.update({
    int(item["entry"]): str(item["symbol"])
    for item in R1_CONNECTION_PARAMETER_FUNCTIONS
})
APP_PRODUCT_FUNCTIONS.update({
    int(item["entry"]): str(item["symbol"])
    for item in R1_SLEEP_SYNC_PACKET_FUNCTIONS
})
APP_PRODUCT_FUNCTIONS.update({
    int(item["entry"]): str(item["symbol"])
    for item in R1_PEER_TARGET_FUNCTIONS
})
APP_PRODUCT_FUNCTIONS.update({
    int(item["entry"]): str(item["symbol"])
    for item in R1_LEGACY_COMMAND_DISPATCH_FUNCTIONS
})
APP_PRODUCT_FUNCTIONS.update({
    int(item["entry"]): str(item["symbol"])
    for item in R1_VALIDATED_SLEEP_DELIVERY_FUNCTIONS
})
APP_PRODUCT_FUNCTIONS.update({
    int(item["entry"]): str(item["symbol"])
    for item in R1_CONNECTION_ROLE_ASSIGNMENT_FUNCTIONS
})
APP_PRODUCT_FUNCTIONS.update({
    int(item["entry"]): str(item["symbol"])
    for item in R1_EUS_RX_REASSEMBLY_FUNCTIONS
})
APP_PRODUCT_FUNCTIONS.update({
    int(item["entry"]): str(item["symbol"])
    for item in R1_BAE8_EVENT_ROUTER_FUNCTIONS
})
APP_PRODUCT_FUNCTIONS.update({
    int(item["entry"]): str(item["symbol"])
    for item in R1_ATI_CALIBRATION_COMMAND_FUNCTIONS
})
APP_PRODUCT_FUNCTIONS.update({
    int(item["entry"]): str(item["symbol"])
    for item in R1_BATTERY_RUNTIME_SERVICE_FUNCTIONS
})
APP_PRODUCT_FUNCTIONS.update({
    int(item["entry"]): str(item["symbol"])
    for item in R1_HRV_FLASH_MERGE_FUNCTIONS
})
APP_PRODUCT_FUNCTIONS.update({
    int(item["entry"]): str(item["symbol"])
    for item in R1_SCALAR_HEALTH_FLASH_MERGE_FUNCTIONS
})
APP_PRODUCT_FUNCTIONS.update({
    int(item["entry"]): str(item["symbol"])
    for item in R1_HRV_TIMING_START_FUNCTIONS
})
APP_PRODUCT_FUNCTIONS.update({
    int(item["entry"]): str(item["symbol"])
    for item in R1_HRV_RAM_CACHE_MERGE_FUNCTIONS
})
APP_PRODUCT_FUNCTIONS.update({
    int(item["entry"]): str(item["symbol"])
    for item in R1_SCALAR_HEALTH_RAM_CACHE_MERGE_FUNCTIONS
})
APP_PRODUCT_FUNCTIONS.update({
    int(item["entry"]): str(item["symbol"])
    for item in R1_PROTOCOL_RESPONSE_FUNCTIONS
})
APP_PRODUCT_FUNCTIONS.update({
    int(item["entry"]): str(item["symbol"])
    for item in R1_EXPORT_STATE_MACHINE_FUNCTIONS
})
APP_PRODUCT_FUNCTIONS.update({
    int(item["entry"]): str(item["symbol"])
    for item in R1_DELAYED_EVENT_TIMER_FUNCTIONS
})
APP_PRODUCT_FUNCTIONS.update({
    int(item["entry"]): str(item["symbol"])
    for item in R1_PMIC_CHARGE_EVENT_FUNCTIONS
})
APP_PRODUCT_FUNCTIONS.update({
    int(item["entry"]): str(item["symbol"])
    for item in R1_PMIC_CHARGED_NOTIFICATION_FUNCTIONS
})
APP_PRODUCT_FUNCTIONS.update({
    int(item["entry"]): str(item["symbol"])
    for item in R1_IQS7211E_ATI_AUDIT_FUNCTIONS
})
APP_PRODUCT_FUNCTIONS.update({
    int(item["entry"]): str(item["symbol"])
    for item in R1_FRONTIER_35X_PRODUCT_FUNCTIONS
})
APP_PRODUCT_FUNCTIONS.update({
    int(item["entry"]): str(item["symbol"])
    for item in R1_FRONTIER_334_342_PRODUCT_FUNCTIONS
})
APP_PRODUCT_FUNCTIONS.update({
    int(item["entry"]): str(item["symbol"])
    for item in R1_FRONTIER_314_328_PRODUCT_FUNCTIONS
})
APP_PRODUCT_FUNCTIONS.update({
    int(item["entry"]): str(item["symbol"])
    for item in R1_FRONTIER_280_308_PRODUCT_FUNCTIONS
})
APP_PRODUCT_FUNCTIONS.update({
    int(item["entry"]): str(item["symbol"])
    for item in R1_FRONTIER_264_274_PRODUCT_FUNCTIONS
})
APP_PRODUCT_FUNCTIONS.update({
    int(item["entry"]): str(item["symbol"])
    for item in R1_FRONTIER_256_262_PRODUCT_FUNCTIONS
})
APP_PRODUCT_FUNCTIONS.update({
    int(item["entry"]): str(item["symbol"])
    for item in (
        R1_FRONTIER_230_248_PRODUCT_FUNCTIONS
        + R1_FRONTIER_230_248_PRODUCT_HELPERS
    )
    if item["source_disposition"] == "clean_room_behavior_only"
})
APP_PRODUCT_FUNCTIONS.update({
    int(item["entry"]): str(item["symbol"])
    for item in (
        R1_FRONTIER_224_230_PRODUCT_FUNCTIONS
        + R1_FRONTIER_224_230_PRODUCT_HELPERS
    )
})
APP_PRODUCT_FUNCTIONS.update({
    int(item["entry"]): str(item["symbol"])
    for item in R1_FRONTIER_212_222_PRODUCT_FUNCTIONS
})
APP_PRODUCT_FUNCTIONS.update({
    int(item["entry"]): str(item["symbol"])
    for item in R1_FRONTIER_204_210_PRODUCT_FUNCTIONS
})
APP_PRODUCT_FUNCTIONS.update({
    int(item["entry"]): str(item["symbol"])
    for item in R1_FRONTIER_128_202_PRODUCT_FUNCTIONS
})
APP_PRODUCT_FUNCTIONS.update({
    int(item["entry"]): str(item["symbol"])
    for item in (
        R1_FRONTIER_64_127_FUNCTIONS
        + R1_FRONTIER_32_63_FUNCTIONS
        + R1_FRONTIER_LT32_FUNCTIONS
        + R1_FRONTIER_FINAL53_FUNCTIONS
    )
})
APP_PRODUCT_DATA_MODEL_FUNCTIONS = {
    int(item["entry"]): str(item["symbol"])
    for item in R1_FRONTIER_230_248_PRODUCT_HELPERS
    if item["source_disposition"] == "clean_room_data_model_only"
}
APP_PRODUCT_FUNCTIONS.update({
    int(item["entry"]): str(item["symbol"])
    for item in R1_BLE_TX_QUEUE_FUNCTIONS
})


# R1-owned configuration/adapters whose underlying implementation is supplied
# by a pinned provider. Only the recovered parameters and call boundary may be
# implemented here; the vendor module itself must remain upstream source.
APP_PROVIDER_GLUE_FUNCTIONS = {
    **{
        int(item["entry"]): str(item["symbol"])
        for item in FREERTOS_STATIC_MEMORY_FUNCTIONS
    },
    **{
        int(item["entry"]): str(item["symbol"])
        for item in FREERTOS_STACK_OVERFLOW_FUNCTIONS
    },
    0x00048A28: "r1_nordic_advertising_configuration",
    0x0004DF18: "r1_nordic_ble_bootstrap_configuration",
    0x0004E4B4: "r1_nordic_peer_manager_configuration",
    0x0004E66C: "r1_bae8_transport_provider_configuration",
    0x000529BC: "r1_bae8_service_configuration",
    0x000539B8: "r1_nordic_softdevice_resource_bootstrap_configuration",
    0x00066C4C: "r1_nordic_gap_identity_configuration",
}


# Product-owned access and clock/hour policy around the pinned FlashDB provider
# and six metric callback adapters. OpenR1 may reproduce the bounded binding,
# orchestration, and cursor rules, but allocation, TSDB encoding/I/O,
# calendar/time providers, and metric implementations remain external.
APP_HEALTH_STORAGE_ADAPTERS = {
    0x0005DCE8: "r1_health_hour_boundary_storage_orchestrator",
    0x0005E698: "r1_health_time_transition_storage_orchestrator",
    0x00070028: "r1_health_database_provider_handle_accessor",
}


# R1-owned register-transfer, completion, and blocking-wait policy around Nordic's TWI
# driver and the authenticated CMSIS-RTOS2 wrapper.  The provider callbacks,
# semaphore implementation, kernel state, tick frequency, and delay primitive
# remain in their attributable upstream sources.
APP_NORDIC_CMSIS_ADAPTERS = {
    0x00054FF8: "r1_twi_primary_register_read_adapter",
    0x0005505C: "r1_twi_primary_register_write_adapter",
    0x000550C0: "r1_twi_secondary_register_read_adapter",
    0x00055120: "r1_twi_secondary_register_write_adapter",
    0x00055180: "r1_twi_primary_shutdown_adapter",
    0x000551B4: "r1_twi_secondary_shutdown_adapter",
    0x00055278: "r1_twi_primary_initialize_configuration_adapter",
    0x000552E4: "r1_twi_secondary_initialize_configuration_adapter",
    0x00070778: "r1_twi_transfer_completion_adapter",
    0x00070820: "r1_twi_primary_wait_adapter",
    0x0007088C: "r1_twi_secondary_wait_adapter",
}


# The retained trace and fault tag are product policy; the terminal reset is
# supplied by the pinned Nordic SDK's CMSIS core header.
APP_RESET_TRACE_CMSIS_ADAPTERS = {
    0x0007A5E0: "r1_fault_reset_adapter -> CMSIS NVIC_SystemReset",
}


# R1-owned fixed bus-record binding around the unidentified stock global
# registry. OpenR1 retains the recovered board data through direct typed
# provider bindings and does not recreate the registry or software-I2C engine.
APP_DEVICE_REGISTRY_CONFIGURATION_ADAPTERS = {
    0x00054F90: "r1_twi_primary_device_binding_configuration",
    0x00054FC4: "r1_twi_secondary_device_binding_configuration",
    0x00056508: "r1_software_twi_i2c_2_binding_configuration",
    0x00056520: "r1_software_twi_i2c_3_binding_configuration",
    0x00056538: "r1_software_twi_i2c_4_binding_configuration",
    0x00056550: "r1_software_twi_i2c_5_binding_configuration",
    0x000563C4: "r1_rtc_device_binding_configuration",
    0x000565F4: "r1_yhm2710_stacmd_binding_configuration",
    0x00056694: "r1_watchdog_binding_configuration",
}


# Four compiler-instantiated GPIO-driven two-wire engines omitted by Ghidra's
# function inventory. Their exact extents and behavior are recovered, but no
# attributable source, version, or license has been established. Keep all
# provider bodies gated until an attributable implementation can be selected.
APP_UNKNOWN_SOFTWARE_TWI_CANDIDATES = {
    int(item["entry"]): str(item["symbol"])
    for item in SOFTWARE_TWI_FUNCTIONS
}


# The adjacent RTC-device layer is not Nordic driver code: only its direct
# nrfx_rtc_init dependency is attributable. The ten generic named-record,
# calendar, epoch, callback, and ops-veneer bodies are reduced to compilable C
# under the owner-authorized full reduction (2026-08-14); see
# docs/correlation/RTC-DEVICE-REDUCTION-CORRELATION.md.
APP_UNKNOWN_RTC_DEVICE_CANDIDATES = {
    int(item["entry"]): str(item["symbol"])
    for item in RTC_DEVICE_FUNCTIONS
    if item["provider_family"] == "unknown_rtc_device_provider_candidate"
}


# The Goodix goodix_mem/GdMem memory-pool boundary: thirteen exact allocator
# census bodies plus twenty-one guarded alloc/free call-site glue bodies.
# Provenance is resolved to the Goodix GH3X2X SDK common DSP support library
# (config tag gh3x2x-v2.23_7ecd2a) by the public goodix_mem.h -1/-2 error
# contract and instruction-level comparison against the Goodix common-DSP
# library object.  This dict remains the label census; the per-entry
# provider routing lives in SENSOR_ALGORITHM_HEAP_ROUTING.
APP_SENSOR_ALGORITHM_HEAP_BOUNDARY = {
    int(item["entry"]): str(item["symbol"])
    for item in SENSOR_ALGORITHM_HEAP_FUNCTIONS
}


# The complete device_stacmd executable closure is tied by its scatter-loaded
# operation table and P1.01 callback record to the YHM2710 power path. Exact
# wire behavior is independently reconstructed under the owner-authorized
# full-reduction policy; the original vendor package remains unlicensed.
APP_YHM2710_STACMD_CANDIDATES = {
    int(item["entry"]): str(item["symbol"])
    for item in YHM2710_STACMD_FUNCTIONS
    if item["provider_family"] == "yhmicros_yhm2710_candidate"
}

# The 128...202-byte frontier adds the chip-ID 0xA0 verification body called
# from the pinned YHM2710 diagnostic at 0x0003510C and the 8-step float-ladder
# register-field update over the same single-wire transport. Both remain
# owner-authorized reconstructed behavior in reconstructed/yhm2710/.
APP_YHM2710_FRONTIER_CANDIDATES = {
    0x0003530C: "yhm2710_chip_id_verify",
    0x00035508: "yhm2710_ladder_field_update",
}
APP_YHM2710_FRONTIER_CANDIDATES.update({
    int(item["entry"]): str(item["symbol"]) or _candidate_label(item)
    for item in YHM_FRONTIER_64_127_FUNCTIONS + YHM_FRONTIER_LT32_FUNCTIONS
})


# Product lifecycle and feed scheduling around Nordic's attributable WDT
# driver. Only the fixed recovered configuration and scheduler seam are local.
APP_NORDIC_WDT_ADAPTERS = {
    int(item["entry"]): str(item["symbol"])
    for item in WATCHDOG_DEVICE_FUNCTIONS
    if item["provider_family"] == "r1_nordic_wdt_provider_adapter"
}


# Nordic's prefix formatter is retained with an R1 wall-clock/date hook. The
# SDK formatter remains the provider; only this product-specific prefix seam may
# be implemented locally.
APP_NORDIC_ADAPTERS = {
    0x000551E8: "r1_software_twi_i2c_2_shutdown_adapter",
    0x0005520C: "r1_software_twi_i2c_3_shutdown_adapter",
    0x00055230: "r1_software_twi_i2c_4_shutdown_adapter",
    0x00055254: "r1_software_twi_i2c_5_shutdown_adapter",
    0x0007CF4C: "Nordic ble_nus on_write skeleton + R1 four-characteristic BAE8 event adapter",
    0x0008185C: "prefix_process + R1 wall-clock log prefix",
    0x00077E98: "r1_reset_reason_nordic_adapter",
}
APP_NORDIC_ADAPTERS.update({
    int(item["entry"]): str(item["symbol"])
    for item in R1_FRONTIER_212_222_NORDIC_ADAPTERS
})
APP_NORDIC_ADAPTERS.update({
    int(item["entry"]): str(item["symbol"])
    for item in R1_FRONTIER_204_210_NORDIC_ADAPTERS
})


# The stock device_flash layer owns only the recovered nRF52840 geometry,
# callback/serialization policy, FAL binding, and calls into Nordic fstorage.
# The generic RT-style registry is not reproduced by openR1.
APP_INTERNAL_FLASH_ADAPTERS = {
    0x00054970: "r1_internal_flash_callback_configuration",
    0x0005498C: "r1_internal_flash_erase_and_geometry_control",
    0x000549F0: "r1_internal_flash_fstorage_configuration",
    0x00054A4C: "r1_internal_flash_device_read",
    0x00054A8C: "r1_internal_flash_device_registration",
    0x00054AA4: "r1_internal_flash_device_write",
    0x0005C40C: "r1_internal_flash_fstorage_erase_adapter",
    0x0005C464: "r1_internal_flash_memory_mapped_read_adapter",
    0x0005C480: "r1_internal_flash_fstorage_write_adapter",
    0x00071054: "r1_internal_flash_fal_binding",
}
APP_INTERNAL_FLASH_ADAPTERS.update({
    int(item["entry"]): str(item["symbol"])
    for item in R1_FRONTIER_204_210_STORAGE_ADAPTERS
})


# R1-owned ADC naming, route configuration, sample filtering, and conversion
# around Nordic's unmodified nrfx_saadc provider. No generic stock registry or
# Nordic driver body is recreated locally.
APP_ANALOG_ADAPTERS = {
    0x00054864: "r1_saadc_device_lookup_and_channel_configuration",
    0x000548F0: "r1_saadc_named_sample_adapter",
    0x0005493C: "r1_saadc_record_registration",
    0x00091184: "r1_battery_five_sample_filter_and_conversion",
}


# Stock name-based device registry and operation-table dispatch. The complete
# semantics are recovered, but no attributable provider source or license has
# been identified. Keep this framework blocked; clean ports bind product
# adapters directly to admitted Nordic/vendor providers instead of recreating it.
APP_UNKNOWN_DEVICE_REGISTRY_CANDIDATES = {
    0x00085CBA: "device_operation_dispatch_slot_0c",
    0x00085CCC: "device_operation_dispatch_slot_18",
    0x00085CE0: "device_registry_find_by_name",
    0x00085D08: "device_operation_dispatch_slot_00",
    0x00085D1A: "device_operation_dispatch_slot_08",
    0x00085D2C: "device_operation_dispatch_slot_10",
    0x00085D46: "device_operation_dispatch_slot_20",
    0x00085D58: "device_registry_register",
    0x00085DA8: "device_operation_dispatch_slot_14",
}
APP_UNKNOWN_DEVICE_REGISTRY_CANDIDATES.update({
    0x0005DB14: "device_registry_name_task_insert",
    0x000734E8: "device_registry_module_enabled_scan",
})

APP_UNKNOWN_SENSOR_STREAM_CANDIDATES = {
    int(item["entry"]): str(item["symbol"])
    for item in SENSOR_STREAM_UNREGISTER_FUNCTIONS +
    SENSOR_STREAM_REGISTER_FUNCTIONS + SENSOR_STREAM_DISPATCH_FUNCTIONS
}
APP_UNKNOWN_SENSOR_STREAM_CANDIDATES.update({
    int(item["entry"]): str(item["symbol"])
    for item in UNKNOWN_SENSOR_STREAM_FRONTIER_212_222_FUNCTIONS
})
APP_UNKNOWN_SENSOR_STREAM_CANDIDATES.update({
    0x000896F0: "sensor_stream_object_create",
})

APP_UNKNOWN_QUANTIZED_NEURAL_RUNTIME_CANDIDATES = {
    int(item["entry"]): str(item["symbol"])
    for item in (
        QUANTIZED_POOLING_RUNTIME_FUNCTIONS
        + SHARED_QUANTIZED_FRONTIER_230_248_FUNCTIONS
        + SHARED_QUANTIZED_FRONTIER_224_230_FUNCTIONS
        + SHARED_TENSOR_FRONTIER_204_210_FUNCTIONS
    )
}
APP_UNKNOWN_QUANTIZED_NEURAL_RUNTIME_CANDIDATES.update({
    0x0005D244: "quantized_runtime_float_softmax_executor",
    0x00074AAC: "quantized_runtime_descriptor_constructor",
    0x00085B9C: "quantized_runtime_float_dense_execute",
    0x00098EDC: "quantized_runtime_float_add_executor",
})


# Complete clock-backend, Unix/Gregorian conversion, timezone, and local
# hour/bucket helper cluster. Its behavior is known, but the implementation is
# not present in Nordic SDK 17.1.0 and no attributable source/version/license
# has been established. Keep it blocked rather than treating generic calendar
# arithmetic as proof of product authorship.
APP_UNKNOWN_TIME_CALENDAR_CANDIDATES = {
    0x0005A7BC: "time_calendar_unix_to_broken_down",
    0x0005A8AC: "time_calendar_broken_down_to_unix",
    0x0005A990: "time_clock_backend_snapshot",
    0x0005AC74: "time_activity_ten_minute_bucket",
    0x0005ACA6: "time_local_hour",
    0x0008AD40: "time_local_timestamp",
    0x0008AD64: "time_local_day_start",
    0x0008AD98: "time_status_accessor",
    0x0008ADA4: "time_backend_timestamp_thunk",
    0x0008ADB4: "time_utc_offset_accessor",
    0x0008AE58: "time_calendar_to_utc_adapter",
    0x0008AEA4: "time_update_flag_setter",
    0x0008AEB0: "time_backend_update_adapter",
    0x0008AF40: "time_utc_to_calendar_adapter",
}
APP_UNKNOWN_TIME_CALENDAR_CANDIDATES.update({
    0x0008AC28: "time_calendar_local_datetime_fill",
})


# The 64...127-byte, 32...63-byte, and sub-32-byte frontier closures add their
# unresolved-provider candidates to the same blocked families. Labels derive
# deterministically from the recovered roles.
_FRONTIER_TIER2_FUNCTIONS = (
    tuple(FRONTIER_64_127_FUNCTIONS)
    + tuple(FRONTIER_32_63_FUNCTIONS)
    + tuple(FRONTIER_LT32_FUNCTIONS)
    + tuple(FRONTIER_FINAL53_FUNCTIONS)
)
for _item in _FRONTIER_TIER2_FUNCTIONS:
    _entry = int(_item["entry"])
    _label = str(_item["symbol"]) or _candidate_label(_item)
    _family = _item["provider_family"]
    if _family == "unknown_time_calendar_provider_candidate":
        APP_UNKNOWN_TIME_CALENDAR_CANDIDATES[_entry] = _label
    elif _family == "unknown_generic_device_registry_candidate":
        APP_UNKNOWN_DEVICE_REGISTRY_CANDIDATES[_entry] = _label
    elif _family == "unknown_sensor_stream_framework_candidate":
        APP_UNKNOWN_SENSOR_STREAM_CANDIDATES[_entry] = _label
    elif _family == "unknown_shared_quantized_neural_runtime_candidate":
        APP_UNKNOWN_QUANTIZED_NEURAL_RUNTIME_CANDIDATES[_entry] = _label
    elif _family == "unknown_sensor_algorithm_heap_provider_candidate":
        APP_SENSOR_ALGORITHM_HEAP_BOUNDARY[_entry] = _label
    elif _family == "unknown_rtc_device_provider_candidate":
        APP_UNKNOWN_RTC_DEVICE_CANDIDATES[_entry] = _label
    elif _family == "unknown_software_twi_provider_candidate":
        APP_UNKNOWN_SOFTWARE_TWI_CANDIDATES[_entry] = _label
del _item, _entry, _label, _family


# Exact semantic/source correlations to Nordic modules. These functions must be
# supplied by the pinned SDK rather than reconstructed locally. Each newly
# admitted entry has a function-local SDK fingerprint plus matching control flow;
# generic template strings and application handlers remain unclassified.
APP_NORDIC_SYMBOLS = {
    **{
        entry: symbol
        for symbol, entries in APP_NORDIC_GPIO_SYMBOL_GROUPS.items()
        for entry in entries
    },
    **APP_NORDIC_GPIOTE_SYMBOLS,
    **APP_NORDIC_HAL_INLINE_SYMBOLS,
    **APP_NORDIC_CLOCK_DRIVER_SYMBOLS,
    **APP_NORDIC_WDT_DRIVER_SYMBOLS,
    **APP_NORDIC_DELAY_TWI_SYMBOLS,
    **APP_NORDIC_GPIOTE_DRIVER_SYMBOLS,
    **APP_NORDIC_TWI_DRIVER_SYMBOLS,
    **APP_NORDIC_SPIM_DRIVER_SYMBOLS,
    **APP_NORDIC_RTC_TIMER_DRIVER_SYMBOLS,
    **APP_NORDIC_NFCT_DRIVER_SYMBOLS,
    **APP_NORDIC_PEER_MANAGER_EXACT_SYMBOLS,
    **APP_NORDIC_SECURITY_DISPATCHER_EXACT_SYMBOLS,
    **APP_NORDIC_SECURITY_MANAGER_EXACT_SYMBOLS,
    **APP_NORDIC_GATT_CACHE_EXACT_SYMBOLS,
    **APP_NORDIC_BLE_STATIC_HELPER_SYMBOLS,
    **APP_NORDIC_ADVERTISING_SYMBOLS,
    **APP_NORDIC_BUTTONLESS_DFU_SYMBOLS,
    **APP_NORDIC_POWER_MANAGEMENT_SYMBOLS,
    **APP_NORDIC_SAADC_DRIVER_SYMBOLS,
    **{
        int(function["entry"]): str(function["symbol"])
        for function in NORDIC_SYSTEM_INIT_FUNCTIONS
    },
    **{
        int(function["entry"]): str(function["symbol"])
        for function in NORDIC_FRONTIER_224_230_FUNCTIONS
    },
    **{
        int(function["entry"]): str(function["symbol"])
        for function in NORDIC_FRONTIER_128_202_FUNCTIONS
    },
    **{
        int(function["entry"]): str(function["symbol"])
        for function in NORDIC_FRONTIER_64_127_FUNCTIONS
            + NORDIC_FRONTIER_LT32_FUNCTIONS
            + NORDIC_FRONTIER_FINAL53_FUNCTIONS
    },
    0x000272B8: "nrf_atfifo_wspace_req",
    0x000272F0: "nrf_atfifo_wspace_close",
    0x00027302: "nrf_atfifo_rspace_req",
    0x0002733C: "nrf_atfifo_rspace_close",
    0x0002734E: "nrf_atfifo_space_clear",
    0x00027380: "nrf_atomic_internal_mov",
    0x00027398: "nrf_atomic_internal_orr",
    0x000273B2: "nrf_atomic_internal_and",
    0x000273CC: "nrf_atomic_internal_eor",
    0x000273E6: "nrf_atomic_internal_add",
    0x00027400: "nrf_atomic_internal_sub",
    0x0002741A: "nrf_atomic_internal_cmp_exch",
    0x00027444: "nrf_atomic_internal_sub_hs",
    0x00027488: "Reset_Handler",
    0x0002749C: "NMI_Handler",
    0x000274A2: "Default_Handler",
    0x00037530: "__NVIC_ClearPendingIRQ",
    0x00038166: "__NVIC_ClearPendingIRQ",
    0x00038180: "__NVIC_SystemReset",
    0x000381C8: "__NVIC_SystemReset",
    0x0004FB6C: "auth_status_success_process",
    0x0004826C: "active_flag_count",
    0x0004898C: "addr_compare",
    0x000489B2: "addr_is_aligned32",
    0x000489BE: "addr_is_within_bounds",
    0x00048CD0: "ah",
    0x00051440: "bcs_internal_state_reset",
    0x000514E0: "blcm_link_ctx_get",
    0x00051528: "ble_advdata_encode",
    0x000516AA: "ble_advdata_parse",
    0x000516CA: "ble_advdata_search",
    0x00051E04: "ble_conn_state_conn_idx",
    0x00051E18: "ble_conn_state_encrypted",
    0x00051E38: "ble_conn_state_for_each_connected",
    0x00051E4C: "ble_conn_state_for_each_set_user_flag",
    0x00051E78: "ble_conn_state_init",
    0x00051E7C: "ble_conn_state_lesc",
    0x00051E9C: "ble_conn_state_mitm_protected",
    0x00051EBC: "ble_conn_state_peripheral_conn_count",
    0x00051EDC: "ble_conn_state_role",
    0x00051F00: "ble_conn_state_status",
    0x00051F24: "ble_conn_state_user_flag_acquire",
    0x00051F3C: "ble_conn_state_user_flag_get",
    0x00051F6C: "ble_conn_state_user_flag_set",
    0x00051FA4: "ble_conn_state_valid",
    0x00051FB8: "ble_device_addr_encode",
    0x00052018: "ble_dfu_buttonless_async_svci_init",
    0x0005380C: "ble_evt_handler",
    0x00053924: "ble_evt_handler",
    0x000539A8: "ble_srv_is_indication_enabled",
    0x000539B0: "ble_srv_is_notification_enabled",
    0x000566AC: "buf_prealloc",
    0x00056774: "buffer_is_empty",
    0x000578CC: "car_update_needed",
    0x000579A8: "characteristic_add",
    0x00058218: "claim",
    0x00059BA0: "conn_handle_list_get",
    0x00059BDE: "conn_int_encode",
    0x0005A65C: "data_length_update",
    0x0005C110: "delete_execute",
    0x0005CCFC: "dropped_sat16_get",
    0x0005D514: "erase",
    0x0005E5B0: "event_prepare",
    0x0005E624: "event_send",
    0x0005E644: "event_send",
    0x0005EC88: "evt_send",
    0x0005ECA4: "evt_send",
    0x0005ECC0: "evt_send",
    0x0005ECEC: "evt_send",
    0x00063E30: "fds_file_delete",
    0x00063E78: "fds_gc",
    0x00063EB8: "fds_init",
    0x00063FA4: "fds_record_close",
    0x00063FEC: "fds_record_find",
    0x00063FFA: "fds_record_find_by_key",
    0x0006400A: "fds_record_find_in_file",
    0x0006401A: "fds_record_id_from_desc",
    0x0006402C: "fds_record_open",
    0x00064078: "fds_record_update",
    0x00064088: "fds_record_write",
    0x00064090: "fds_register",
    0x000640C0: "fds_stat",
    0x00064160: "record_key_within_pm_range",
    0x00064EEC: "flag_id_init",
    0x00064EFE: "flag_id_init",
    0x00064F10: "flag_toggle",
    0x00065094: "for_each_set_flag",
    0x00066D24: "gc_execute",
    0x00066E88: "gc_state_advance",
    0x00066EF8: "gc_swap_pages",
    0x00066F28: "gcm_ble_evt_handler",
    0x000672E0: "gcm_im_evt_handler",
    0x0006731C: "gcm_init",
    0x0006EEB4: "gscm_local_db_cache_update",
    0x0006FE60: "header_check",
    0x0006FE8C: "header_has_next",
    0x00070C1C: "im_address_resolve",
    0x00070C64: "im_ble_addr_get",
    0x00070C9C: "im_ble_evt_handler",
    0x00070D78: "im_conn_handle_get",
    0x00070DB8: "im_find_duplicate_bonding_data",
    0x00070DF0: "im_is_duplicate_bonding_data",
    0x00070E62: "im_master_id_is_valid",
    0x00070E7A: "im_master_ids_compare",
    0x00070EA4: "im_new_peer_id",
    0x00070EB8: "im_peer_free",
    0x00070EE4: "im_peer_id_get_by_conn_handle",
    0x00070F08: "im_peer_id_get_by_master_id",
    0x000710A0: "init",
    0x000720F0: "init_execute",
    0x00072848: "invalid_packets_omit",
    0x00072B70: "is_busy",
    0x00072BBE: "is_word_aligned",
    0x00072BAA: "is_valid_irk",
    0x00075B20: "local_db_update_in_evt",
    0x00075CE4: "log_skip",
    0x00076088: "manuf_specific_data_encode",
    0x00076178: "memobj_op",
    0x000765DC: "mutex_lock_status_get",
    0x000770BC: "name_encode",
    0x000771E2: "next_id_get",
    0x00077F30: "nrf_atfifo_clear",
    0x00077F40: "nrf_atfifo_init",
    0x00077F66: "nrf_atfifo_item_alloc",
    0x00077F7C: "nrf_atfifo_item_free",
    0x00077F92: "nrf_atfifo_item_get",
    0x00077FA8: "nrf_atfifo_item_put",
    0x00077FBE: "nrf_atflags_clear",
    0x00077FD4: "nrf_atflags_fetch_set",
    0x00077FF4: "nrf_atflags_find_and_set_flag",
    0x0007803E: "nrf_atflags_get",
    0x00078054: "nrf_atflags_set",
    0x00078068: "nrf_atomic_flag_clear_fetch",
    0x0007806E: "nrf_atomic_flag_set",
    0x00078074: "nrf_atomic_flag_set_fetch",
    0x0007807A: "nrf_atomic_u32_add",
    0x00078086: "nrf_atomic_u32_and",
    0x00078092: "nrf_atomic_u32_fetch_add",
    0x000780A6: "nrf_atomic_u32_fetch_or",
    0x000780B0: "nrf_atomic_u32_fetch_store",
    0x000780C6: "nrf_atomic_u32_sub",
    0x000780D2: "nrf_balloc_alloc",
    0x00078116: "nrf_balloc_free",
    0x00078146: "nrf_balloc_init",
    0x00078186: "nrf_ble_gatt_init",
    0x000781B4: "nrf_ble_gatt_on_ble_evt",
    0x000783B6: "nrf_ble_qwr_init",
    0x000783DA: "nrf_ble_qwr_on_ble_evt",
    0x00078590: "nrf_dfu_svci_vector_table_set",
    0x00078C4C: "nrf_fstorage_erase",
    0x00078C78: "nrf_fstorage_init",
    0x00078C80: "nrf_fstorage_is_busy",
    0x00078CD0: "nrf_fstorage_sdh_req_handler",
    0x00078CE8: "nrf_fstorage_sdh_state_handler",
    0x00078D08: "nrf_fstorage_sys_evt_handler",
    0x00078DAC: "nrf_fstorage_write",
    0x00078A40: "nrf_fprintf",
    0x00078A5A: "nrf_fprintf_buffer_flush",
    0x00079520: "nrf_log_backend_add",
    0x00079576: "nrf_log_backend_rtt_init",
    0x00079598: "nrf_log_backend_serial_put",
    0x0007965C: "nrf_log_color_id_get",
    0x0007968C: "nrf_log_default_backends_init",
    0x000796A8: "nrf_log_frontend_dequeue",
    0x00079918: "nrf_log_frontend_hexdump",
    0x000799C0: "nrf_log_frontend_std_0",
    0x000799C8: "nrf_log_frontend_std_1",
    0x000799D6: "nrf_log_frontend_std_2",
    0x000799E6: "nrf_log_frontend_std_3",
    0x000799F8: "nrf_log_frontend_std_4",
    0x00079A0C: "nrf_log_frontend_std_5",
    0x00079A28: "nrf_log_frontend_std_6",
    0x00079A44: "nrf_log_hexdump_entry_process",
    0x00079AF4: "nrf_log_init",
    0x00079B1C: "nrf_log_panic",
    0x00079B48: "nrf_log_std_entry_process",
    0x00079BFE: "nrf_memobj_alloc",
    0x00079C5E: "nrf_memobj_free",
    0x00079C90: "nrf_memobj_get",
    0x00079C98: "nrf_memobj_pool_init",
    0x00079C9C: "nrf_memobj_put",
    0x00079CBA: "nrf_memobj_read",
    0x00079CCA: "nrf_memobj_write",
    0x00079DCC: "nrf_ringbuf_init",
    0x00079E58: "nrf_sdh_ble_app_ram_start_get",
    0x00079E6C: "nrf_sdh_ble_default_cfg_set",
    0x0007A0EC: "nrf_sdh_ble_enable",
    0x0007A38C: "nrf_sdh_ble_evts_poll",
    0x0007A3EC: "nrf_sdh_disable_request",
    0x0007A440: "nrf_sdh_enable_request",
    0x0007A4B4: "nrf_sdh_evts_poll",
    0x0007A4D8: "nrf_sdh_is_enabled",
    0x0007A4E4: "nrf_sdh_request_continue",
    0x0007A500: "nrf_sdh_soc_evts_poll",
    0x0007A53C: "nrf_section_iter_init",
    0x0007A56A: "nrf_section_iter_next",
    0x0007A594: "nrf_strerror_find",
    0x0007A5CC: "nrf_strerror_get",
    0x0007CE34: "on_exchange_mtu_request_evt",
    0x0007E0D4: "page_identify",
    0x0007E0F8: "page_offsets_update",
    0x0007E114: "page_scan",
    0x0007E180: "page_tag_write_data",
    0x0007E19C: "page_tag_write_swap",
    0x0007E1C0: "pages_init",
    0x0007E414: "pdb_init",
    0x0007E3D8: "params_req_send",
    0x0007E3F8: "pdb_evt_send",
    0x0007E574: "pdb_peer_data_ptr_get",
    0x0007E57C: "pdb_peer_free",
    0x0007E678: "pdb_write_buf_get",
    0x0007E77C: "pdb_write_buf_release",
    0x0007E790: "pdb_write_buf_store",
    0x0007E7C8: "pds_evt_send",
    0x0007E7D8: "pds_init",
    0x0007E90C: "pds_next_deleted_peer_id_get",
    0x0007E910: "pds_next_peer_id_get",
    0x0007E914: "pds_peer_data_iterate",
    0x0007E96C: "pds_peer_data_iterate_prepare",
    0x0007E97C: "pds_peer_data_read",
    0x0007E9F0: "pds_peer_data_store",
    0x0007EAD4: "pds_peer_id_allocate",
    0x0007EADC: "pds_peer_id_free",
    0x0007EAF2: "pds_peer_id_is_allocated",
    0x0007EB30: "peer_data_delete_process",
    0x0007EC04: "peer_data_find",
    0x0007EC34: "peer_data_id_is_valid",
    0x0007EC58: "peer_data_point_to_buffer",
    0x0007EC74: "peer_id_allocate",
    0x0007EC80: "peer_id_delete",
    0x0007ECA4: "peer_id_free",
    0x0007ECC0: "peer_id_get_next_deleted",
    0x0007ECCC: "peer_id_get_next_used",
    0x0007ECFC: "peer_id_init",
    0x0007ED08: "peer_id_is_allocated",
    0x0007ED1C: "peer_id_is_deleted",
    0x0007F194: "pm_buffer_block_acquire",
    0x0007F1F8: "pm_buffer_init",
    0x0007F21C: "pm_buffer_ptr_get",
    0x0007F244: "pm_buffer_release",
    0x0007FA5C: "pm_handler_flash_clean",
    0x0007FDE4: "pm_handler_on_pm_evt",
    0x0007FE74: "pm_handler_pm_evt_log",
    0x0008056C: "pm_im_evt_handler",
    0x00080570: "pm_init",
    0x000813E0: "postfix_process",
    0x0008743C: "queue_buf_get",
    0x00087458: "queue_buf_store",
    0x00087468: "queue_free",
    0x0008747C: "queue_process",
    0x00087520: "queue_process",
    0x000875C0: "queue_start",
    0x000875DC: "queue_start",
    0x00087B20: "read",
    0x00087F20: "record_find",
    0x00087FB0: "record_find_by_desc",
    0x00088050: "record_find_next",
    0x000880AC: "record_header_flag_dirty",
    0x000880E8: "records_stat",
    0x000883F8: "rmap",
    0x000890CC: "service_changed_send_in_evt",
    0x00089148: "sdh_request_observer_notify",
    0x00089178: "sdh_state_observer_notify",
    0x000892F4: "sec_keyset_fill",
    0x000894C0: "sec_params_verify",
    0x00089538: "sec_proc_start",
    0x00090308: "sm_ble_evt_handler",
    0x00090338: "sm_conn_sec_status_get",
    0x000903DC: "sm_init",
    0x0009045C: "sm_link_secure",
    0x00090468: "sm_pdb_evt_handler",
    0x000904AC: "sm_sec_is_sufficient",
    0x000904D4: "sm_sec_params_set",
    0x00090534: "smd_ble_evt_handler",
    0x00090638: "smd_init",
    0x00090FEC: "std_n",
    0x0008ABA0: "service_data_encode",
    0x00093EA2: "uint16_encode",
    0x00093EC4: "uninit",
    0x00094E30: "user_flag_is_acquired",
    0x00095540: "uuid_list_encode",
    0x00095570: "uuid_list_sized_encode",
    0x00095114: "user_mem_reply",
    0x00096E08: "wmap",
    0x00096FE0: "write",
    0x00097030: "write_buf_store",
    0x00097214: "write_buf_store_in_event",
    0x000972B4: "write_buffer_record_find",
    0x000972E8: "write_buffer_record_find_next",
    0x00097318: "write_buffer_record_invalidate",
    0x00097334: "write_buffer_record_release",
    0x00097360: "write_enqueue",
    0x00097454: "write_execute",
    0x000975C4: "write_space_free",
    0x000975DC: "write_space_reserve",
    0x000881E4: "release",
}

APP_NORDIC_SOURCES = {
    **{
        entry: "modules/nrfx/hal/nrf_gpio.h"
        for entries in APP_NORDIC_GPIO_SYMBOL_GROUPS.values()
        for entry in entries
    },
    **{
        entry: "modules/nrfx/hal/nrf_gpiote.h"
        for entry in APP_NORDIC_GPIOTE_SYMBOLS
    },
    **APP_NORDIC_HAL_INLINE_SOURCES,
    **APP_NORDIC_CLOCK_DRIVER_SOURCES,
    **APP_NORDIC_WDT_DRIVER_SOURCES,
    **APP_NORDIC_DELAY_TWI_SOURCES,
    **APP_NORDIC_GPIOTE_DRIVER_SOURCES,
    **APP_NORDIC_TWI_DRIVER_SOURCES,
    **APP_NORDIC_SPIM_DRIVER_SOURCES,
    **APP_NORDIC_RTC_TIMER_DRIVER_SOURCES,
    **APP_NORDIC_NFCT_DRIVER_SOURCES,
    **APP_NORDIC_PEER_MANAGER_EXACT_SOURCES,
    **APP_NORDIC_SECURITY_DISPATCHER_EXACT_SOURCES,
    **APP_NORDIC_SECURITY_MANAGER_EXACT_SOURCES,
    **APP_NORDIC_GATT_CACHE_EXACT_SOURCES,
    **APP_NORDIC_BLE_STATIC_HELPER_SOURCES,
    **APP_NORDIC_ADVERTISING_SOURCES,
    **APP_NORDIC_BUTTONLESS_DFU_SOURCES,
    **APP_NORDIC_POWER_MANAGEMENT_SOURCES,
    **APP_NORDIC_SAADC_DRIVER_SOURCES,
    **{
        int(function["entry"]): str(function["source"])
        for function in NORDIC_SYSTEM_INIT_FUNCTIONS
    },
    **{
        int(function["entry"]): "modules/nrfx/drivers/src/nrfx_pdm.c"
        for function in NORDIC_FRONTIER_224_230_FUNCTIONS
    },
    **{
        int(function["entry"]): "modules/nrfx/drivers/src/nrfx_pwm.c"
        for function in NORDIC_FRONTIER_128_202_FUNCTIONS
    },
    0x00087ED0: "components/ble/peer_manager/peer_database.c",
    0x00030CA8: "modules/nrfx/drivers/src/nrfx_pwm.c",
    0x00030CB8: "modules/nrfx/drivers/src/nrfx_pwm.c",
    0x00030CC8: "modules/nrfx/drivers/src/nrfx_pwm.c",
    0x00093960: "integration/nrfx/legacy/nrf_drv_twi.c",
    0x0005C034: "components/ble/peer_manager/gatt_cache_manager.c",
    0x00034A7C: "modules/nrfx/drivers/src/nrfx_wdt.c",
    0x00034410: "modules/nrfx/drivers/src/prs/nrfx_prs.c",
    0x000272B8: "components/libraries/atomic_fifo/nrf_atfifo_internal.h",
    0x000272F0: "components/libraries/atomic_fifo/nrf_atfifo_internal.h",
    0x00027302: "components/libraries/atomic_fifo/nrf_atfifo_internal.h",
    0x0002733C: "components/libraries/atomic_fifo/nrf_atfifo_internal.h",
    0x0002734E: "components/libraries/atomic_fifo/nrf_atfifo_internal.h",
    0x00027380: "components/libraries/atomic/nrf_atomic_internal.h",
    0x00027398: "components/libraries/atomic/nrf_atomic_internal.h",
    0x000273B2: "components/libraries/atomic/nrf_atomic_internal.h",
    0x000273CC: "components/libraries/atomic/nrf_atomic_internal.h",
    0x000273E6: "components/libraries/atomic/nrf_atomic_internal.h",
    0x00027400: "components/libraries/atomic/nrf_atomic_internal.h",
    0x0002741A: "components/libraries/atomic/nrf_atomic_internal.h",
    0x00027444: "components/libraries/atomic/nrf_atomic_internal.h",
    0x00027488: "modules/nrfx/mdk/arm_startup_nrf52840.s",
    0x0002749C: "modules/nrfx/mdk/arm_startup_nrf52840.s",
    0x000274A2: "modules/nrfx/mdk/arm_startup_nrf52840.s",
    0x00037530: "components/toolchain/cmsis/include/core_cm4.h",
    0x00038166: "components/toolchain/cmsis/include/core_cm4.h",
    0x00038180: "components/toolchain/cmsis/include/core_cm4.h",
    0x000381C8: "components/toolchain/cmsis/include/core_cm4.h",
    0x0004FB6C: "components/ble/peer_manager/security_dispatcher.c",
    0x0004826C: "components/ble/common/ble_conn_state.c",
    0x0004898C: "components/ble/peer_manager/id_manager.c",
    0x000489B2: "components/libraries/fstorage/nrf_fstorage.c",
    0x000489BE: "components/libraries/fstorage/nrf_fstorage.c",
    0x00048CD0: "components/ble/peer_manager/id_manager.c",
    0x00051440: "components/ble/common/ble_conn_state.c",
    0x000514E0: "components/ble/ble_link_ctx_manager/ble_link_ctx_manager.c",
    0x00051528: "components/ble/common/ble_advdata.c",
    0x000516AA: "components/ble/common/ble_advdata.c",
    0x000516CA: "components/ble/common/ble_advdata.c",
    0x00051E04: "components/ble/common/ble_conn_state.c",
    0x00051E18: "components/ble/common/ble_conn_state.c",
    0x00051E38: "components/ble/common/ble_conn_state.c",
    0x00051E4C: "components/ble/common/ble_conn_state.c",
    0x00051E78: "components/ble/common/ble_conn_state.c",
    0x00051E7C: "components/ble/common/ble_conn_state.c",
    0x00051E9C: "components/ble/common/ble_conn_state.c",
    0x00051EBC: "components/ble/common/ble_conn_state.c",
    0x00051EDC: "components/ble/common/ble_conn_state.c",
    0x00051F00: "components/ble/common/ble_conn_state.c",
    0x00051F24: "components/ble/common/ble_conn_state.c",
    0x00051F3C: "components/ble/common/ble_conn_state.c",
    0x00051F6C: "components/ble/common/ble_conn_state.c",
    0x00051FA4: "components/ble/common/ble_conn_state.c",
    0x00052018: "components/ble/ble_services/ble_dfu/ble_dfu_unbonded.c",
    0x0005380C: "components/ble/common/ble_conn_state.c",
    0x00053924: "components/ble/peer_manager/peer_manager.c",
    0x000539A8: "components/ble/common/ble_srv_common.c",
    0x000539B0: "components/ble/common/ble_srv_common.c",
    0x000566AC: "components/libraries/log/src/nrf_log_frontend.c",
    0x00056774: "components/libraries/log/src/nrf_log_frontend.c",
    0x000578CC: "components/ble/peer_manager/gatt_cache_manager.c",
    0x000579A8: "components/ble/common/ble_srv_common.c",
    0x00058218: "components/ble/peer_manager/peer_id.c",
    0x00059BA0: "components/ble/common/ble_conn_state.c",
    0x00059BDE: "components/ble/common/ble_advdata.c",
    0x0005A65C: "components/ble/nrf_ble_gatt/nrf_ble_gatt.c",
    0x0005C110: "components/libraries/fds/fds.c",
    0x0005CCFC: "components/libraries/log/src/nrf_log_frontend.c",
    0x0005D514: "components/libraries/fstorage/nrf_fstorage_sd.c",
    0x0005E5B0: "components/libraries/fds/fds.c",
    0x0005E624: "components/libraries/fds/fds.c",
    0x0005E644: "components/libraries/fstorage/nrf_fstorage_sd.c",
    0x0005EC88: "components/ble/peer_manager/gatt_cache_manager.c",
    0x0005ECA4: "components/ble/peer_manager/gatts_cache_manager.c",
    0x0005ECC0: "components/ble/peer_manager/peer_manager.c",
    0x0005ECEC: "components/ble/peer_manager/security_dispatcher.c",
    0x00063E30: "components/libraries/fds/fds.c",
    0x00063E78: "components/libraries/fds/fds.c",
    0x00063EB8: "components/libraries/fds/fds.c",
    0x00063FA4: "components/libraries/fds/fds.c",
    0x00063FEC: "components/libraries/fds/fds.c",
    0x00063FFA: "components/libraries/fds/fds.c",
    0x0006400A: "components/libraries/fds/fds.c",
    0x0006401A: "components/libraries/fds/fds.c",
    0x0006402C: "components/libraries/fds/fds.c",
    0x00064078: "components/libraries/fds/fds.c",
    0x00064088: "components/libraries/fds/fds.c",
    0x00064090: "components/libraries/fds/fds.c",
    0x000640C0: "components/libraries/fds/fds.c",
    0x00064160: "components/ble/peer_manager/peer_data_storage.c",
    0x00064EEC: "components/ble/peer_manager/security_dispatcher.c",
    0x00064EFE: "components/ble/peer_manager/security_manager.c",
    0x00064F10: "components/ble/common/ble_conn_state.c",
    0x00065094: "components/ble/common/ble_conn_state.c",
    0x00066D24: "components/libraries/fds/fds.c",
    0x00066E88: "components/libraries/fds/fds.c",
    0x00066EF8: "components/libraries/fds/fds.c",
    0x00066F28: "components/ble/peer_manager/gatt_cache_manager.c",
    0x000672E0: "components/ble/peer_manager/gatt_cache_manager.c",
    0x0006731C: "components/ble/peer_manager/gatt_cache_manager.c",
    0x0006EEB4: "components/ble/peer_manager/gatts_cache_manager.c",
    0x0006FE60: "components/libraries/fds/fds.c",
    0x0006FE8C: "components/libraries/fds/fds.c",
    0x00070C1C: "components/ble/peer_manager/id_manager.c",
    0x00070C64: "components/ble/peer_manager/id_manager.c",
    0x00070C9C: "components/ble/peer_manager/id_manager.c",
    0x00070D78: "components/ble/peer_manager/id_manager.c",
    0x00070DB8: "components/ble/peer_manager/id_manager.c",
    0x00070DF0: "components/ble/peer_manager/id_manager.c",
    0x00070E62: "components/ble/peer_manager/id_manager.c",
    0x00070E7A: "components/ble/peer_manager/id_manager.c",
    0x00070EA4: "components/ble/peer_manager/id_manager.c",
    0x00070EB8: "components/ble/peer_manager/id_manager.c",
    0x00070EE4: "components/ble/peer_manager/id_manager.c",
    0x00070F08: "components/ble/peer_manager/id_manager.c",
    0x000710A0: "components/libraries/fstorage/nrf_fstorage_sd.c",
    0x000720F0: "components/libraries/fds/fds.c",
    0x00072848: "components/libraries/log/src/nrf_log_frontend.c",
    0x00072B70: "components/libraries/fstorage/nrf_fstorage_sd.c",
    0x00072BBE: "components/libraries/util/app_util.h",
    0x00072BAA: "components/ble/peer_manager/id_manager.c",
    0x00075B20: "components/ble/peer_manager/gatt_cache_manager.c",
    0x00075CE4: "components/libraries/log/src/nrf_log_frontend.c",
    0x00076088: "components/ble/common/ble_advdata.c",
    0x00076178: "components/libraries/memobj/nrf_memobj.c",
    0x000765DC: "components/ble/peer_manager/pm_buffer.c",
    0x000770BC: "components/ble/common/ble_advdata.c",
    0x000771E2: "components/ble/peer_manager/peer_id.c",
    0x00077F30: "components/libraries/atomic_fifo/nrf_atfifo.c",
    0x00077F40: "components/libraries/atomic_fifo/nrf_atfifo.c",
    0x00077F66: "components/libraries/atomic_fifo/nrf_atfifo.c",
    0x00077F7C: "components/libraries/atomic_fifo/nrf_atfifo.c",
    0x00077F92: "components/libraries/atomic_fifo/nrf_atfifo.c",
    0x00077FA8: "components/libraries/atomic_fifo/nrf_atfifo.c",
    0x00077FBE: "components/libraries/atomic_flags/nrf_atflags.c",
    0x00077FD4: "components/libraries/atomic_flags/nrf_atflags.c",
    0x00077FF4: "components/libraries/atomic_flags/nrf_atflags.c",
    0x0007803E: "components/libraries/atomic_flags/nrf_atflags.c",
    0x00078054: "components/libraries/atomic_flags/nrf_atflags.c",
    0x00078068: "components/libraries/atomic/nrf_atomic.c",
    0x0007806E: "components/libraries/atomic/nrf_atomic.c",
    0x00078074: "components/libraries/atomic/nrf_atomic.c",
    0x0007807A: "components/libraries/atomic/nrf_atomic.c",
    0x00078086: "components/libraries/atomic/nrf_atomic.c",
    0x00078092: "components/libraries/atomic/nrf_atomic.c",
    0x000780A6: "components/libraries/atomic/nrf_atomic.c",
    0x000780B0: "components/libraries/atomic/nrf_atomic.c",
    0x000780C6: "components/libraries/atomic/nrf_atomic.c",
    0x000780D2: "components/libraries/balloc/nrf_balloc.c",
    0x00078116: "components/libraries/balloc/nrf_balloc.c",
    0x00078146: "components/libraries/balloc/nrf_balloc.c",
    0x00078186: "components/ble/nrf_ble_gatt/nrf_ble_gatt.c",
    0x000781B4: "components/ble/nrf_ble_gatt/nrf_ble_gatt.c",
    0x00078590: "components/libraries/bootloader/dfu/nrf_dfu_svci.c",
    0x00078C4C: "components/libraries/fstorage/nrf_fstorage.c",
    0x00078C78: "components/libraries/fstorage/nrf_fstorage.c",
    0x00078C80: "components/libraries/fstorage/nrf_fstorage.c",
    0x00078CD0: "components/libraries/fstorage/nrf_fstorage_sd.c",
    0x00078CE8: "components/libraries/fstorage/nrf_fstorage_sd.c",
    0x00078D08: "components/libraries/fstorage/nrf_fstorage_sd.c",
    0x00078DAC: "components/libraries/fstorage/nrf_fstorage.c",
    0x00078A40: "external/fprintf/nrf_fprintf.c",
    0x00078A5A: "external/fprintf/nrf_fprintf.c",
    0x00079520: "components/libraries/log/src/nrf_log_frontend.c",
    0x00079576: "components/libraries/log/src/nrf_log_backend_rtt.c",
    0x00079598: "components/libraries/log/src/nrf_log_backend_serial.c",
    0x0007965C: "components/libraries/log/src/nrf_log_str_formatter.c",
    0x0007968C: "components/libraries/log/src/nrf_log_default_backends.c",
    0x000796A8: "components/libraries/log/src/nrf_log_frontend.c",
    0x00079918: "components/libraries/log/src/nrf_log_frontend.c",
    0x000799C0: "components/libraries/log/src/nrf_log_frontend.c",
    0x000799C8: "components/libraries/log/src/nrf_log_frontend.c",
    0x000799D6: "components/libraries/log/src/nrf_log_frontend.c",
    0x000799E6: "components/libraries/log/src/nrf_log_frontend.c",
    0x000799F8: "components/libraries/log/src/nrf_log_frontend.c",
    0x00079A0C: "components/libraries/log/src/nrf_log_frontend.c",
    0x00079A28: "components/libraries/log/src/nrf_log_frontend.c",
    0x00079A44: "components/libraries/log/src/nrf_log_str_formatter.c",
    0x00079AF4: "components/libraries/log/src/nrf_log_frontend.c",
    0x00079B1C: "components/libraries/log/src/nrf_log_frontend.c",
    0x00079B48: "components/libraries/log/src/nrf_log_str_formatter.c",
    0x00079BFE: "components/libraries/memobj/nrf_memobj.c",
    0x00079C5E: "components/libraries/memobj/nrf_memobj.c",
    0x00079C90: "components/libraries/memobj/nrf_memobj.c",
    0x00079C98: "components/libraries/memobj/nrf_memobj.c",
    0x00079C9C: "components/libraries/memobj/nrf_memobj.c",
    0x00079CBA: "components/libraries/memobj/nrf_memobj.c",
    0x00079CCA: "components/libraries/memobj/nrf_memobj.c",
    0x00079DCC: "components/libraries/ringbuf/nrf_ringbuf.c",
    0x00079E58: "components/softdevice/common/nrf_sdh_ble.c",
    0x00079E6C: "components/softdevice/common/nrf_sdh_ble.c",
    0x0007A0EC: "components/softdevice/common/nrf_sdh_ble.c",
    0x0007A38C: "components/softdevice/common/nrf_sdh_ble.c",
    0x0007A3EC: "components/softdevice/common/nrf_sdh.c",
    0x0007A440: "components/softdevice/common/nrf_sdh.c",
    0x0007A4B4: "components/softdevice/common/nrf_sdh.c",
    0x0007A4D8: "components/softdevice/common/nrf_sdh.c",
    0x0007A4E4: "components/softdevice/common/nrf_sdh.c",
    0x0007A500: "components/softdevice/common/nrf_sdh_soc.c",
    0x0007A53C: "components/libraries/experimental_section_vars/nrf_section_iter.c",
    0x0007A56A: "components/libraries/experimental_section_vars/nrf_section_iter.c",
    0x0007A594: "components/libraries/strerror/nrf_strerror.c",
    0x0007A5CC: "components/libraries/strerror/nrf_strerror.c",
    0x0007CE34: "components/ble/nrf_ble_gatt/nrf_ble_gatt.c",
    0x0007E0D4: "components/libraries/fds/fds.c",
    0x0007E0F8: "components/libraries/fds/fds.c",
    0x0007E114: "components/libraries/fds/fds.c",
    0x0007E180: "components/libraries/fds/fds.c",
    0x0007E19C: "components/libraries/fds/fds.c",
    0x0007E1C0: "components/libraries/fds/fds.c",
    0x0007E414: "components/ble/peer_manager/peer_database.c",
    0x0007E3D8: "components/ble/peer_manager/security_manager.c",
    0x0007E3F8: "components/ble/peer_manager/peer_database.c",
    0x0007E574: "components/ble/peer_manager/peer_database.c",
    0x0007E57C: "components/ble/peer_manager/peer_database.c",
    0x0007E678: "components/ble/peer_manager/peer_database.c",
    0x0007E77C: "components/ble/peer_manager/peer_database.c",
    0x0007E790: "components/ble/peer_manager/peer_database.c",
    0x0007E7C8: "components/ble/peer_manager/peer_data_storage.c",
    0x0007E7D8: "components/ble/peer_manager/peer_data_storage.c",
    0x0007E90C: "components/ble/peer_manager/peer_data_storage.c",
    0x0007E910: "components/ble/peer_manager/peer_data_storage.c",
    0x0007E914: "components/ble/peer_manager/peer_data_storage.c",
    0x0007E96C: "components/ble/peer_manager/peer_data_storage.c",
    0x0007E97C: "components/ble/peer_manager/peer_data_storage.c",
    0x0007E9F0: "components/ble/peer_manager/peer_data_storage.c",
    0x0007EAD4: "components/ble/peer_manager/peer_data_storage.c",
    0x0007EADC: "components/ble/peer_manager/peer_data_storage.c",
    0x0007EAF2: "components/ble/peer_manager/peer_data_storage.c",
    0x0007EB30: "components/ble/peer_manager/peer_data_storage.c",
    0x0007EC04: "components/ble/peer_manager/peer_data_storage.c",
    0x0007EC34: "components/ble/peer_manager/peer_data_storage.c",
    0x0007EC58: "components/ble/peer_manager/peer_database.c",
    0x00051FB8: "components/ble/common/ble_advdata.c",
    0x000783B6: "components/ble/nrf_ble_qwr/nrf_ble_qwr.c",
    0x000783DA: "components/ble/nrf_ble_qwr/nrf_ble_qwr.c",
    0x0007EC74: "components/ble/peer_manager/peer_id.c",
    0x0007EC80: "components/ble/peer_manager/peer_id.c",
    0x0007ECA4: "components/ble/peer_manager/peer_id.c",
    0x0007ECC0: "components/ble/peer_manager/peer_id.c",
    0x0007ECCC: "components/ble/peer_manager/peer_id.c",
    0x0007ECFC: "components/ble/peer_manager/peer_id.c",
    0x0007ED08: "components/ble/peer_manager/peer_id.c",
    0x0007ED1C: "components/ble/peer_manager/peer_id.c",
    0x0007F194: "components/ble/peer_manager/pm_buffer.c",
    0x0007F1F8: "components/ble/peer_manager/pm_buffer.c",
    0x0007F21C: "components/ble/peer_manager/pm_buffer.c",
    0x0007F244: "components/ble/peer_manager/pm_buffer.c",
    0x0007FA5C: "components/ble/peer_manager/peer_manager_handler.c",
    0x0007FDE4: "components/ble/peer_manager/peer_manager_handler.c",
    0x0007FE74: "components/ble/peer_manager/peer_manager_handler.c",
    0x0008056C: "components/ble/peer_manager/peer_manager.c",
    0x00080570: "components/ble/peer_manager/peer_manager.c",
    0x000813E0: "components/libraries/log/src/nrf_log_str_formatter.c",
    0x0008743C: "components/libraries/fds/fds.c",
    0x00087458: "components/libraries/fds/fds.c",
    0x00087468: "components/libraries/fstorage/nrf_fstorage_sd.c",
    0x0008747C: "components/libraries/fds/fds.c",
    0x00087520: "components/libraries/fstorage/nrf_fstorage_sd.c",
    0x000875C0: "components/libraries/fds/fds.c",
    0x000875DC: "components/libraries/fstorage/nrf_fstorage_sd.c",
    0x00087B20: "components/libraries/fstorage/nrf_fstorage_sd.c",
    0x00087F20: "components/libraries/fds/fds.c",
    0x00087FB0: "components/libraries/fds/fds.c",
    0x00088050: "components/libraries/fds/fds.c",
    0x000880AC: "components/libraries/fds/fds.c",
    0x000880E8: "components/libraries/fds/fds.c",
    0x000883F8: "components/libraries/fstorage/nrf_fstorage_sd.c",
    0x000890CC: "components/ble/peer_manager/gatt_cache_manager.c",
    0x00089148: "components/softdevice/common/nrf_sdh.c",
    0x00089178: "components/softdevice/common/nrf_sdh.c",
    0x000892F4: "components/ble/peer_manager/security_dispatcher.c",
    0x000894C0: "components/ble/peer_manager/security_manager.c",
    0x00089538: "components/ble/peer_manager/security_dispatcher.c",
    0x00090308: "components/ble/peer_manager/security_manager.c",
    0x00090338: "components/ble/peer_manager/security_manager.c",
    0x000903DC: "components/ble/peer_manager/security_manager.c",
    0x0009045C: "components/ble/peer_manager/security_manager.c",
    0x00090468: "components/ble/peer_manager/security_manager.c",
    0x000904AC: "components/ble/peer_manager/security_manager.c",
    0x000904D4: "components/ble/peer_manager/security_manager.c",
    0x00090534: "components/ble/peer_manager/security_dispatcher.c",
    0x00090638: "components/ble/peer_manager/security_dispatcher.c",
    0x00090FEC: "components/libraries/log/src/nrf_log_frontend.c",
    0x0008ABA0: "components/ble/common/ble_advdata.c",
    0x00093EA2: "components/libraries/util/app_util.h",
    0x00093EC4: "components/libraries/fstorage/nrf_fstorage_sd.c",
    0x00094E30: "components/ble/common/ble_conn_state.c",
    0x00095540: "components/ble/common/ble_advdata.c",
    0x00095570: "components/ble/common/ble_advdata.c",
    0x00095114: "components/ble/nrf_ble_qwr/nrf_ble_qwr.c",
    0x00096E08: "components/libraries/fstorage/nrf_fstorage_sd.c",
    0x00096FE0: "components/libraries/fstorage/nrf_fstorage_sd.c",
    0x00097030: "components/ble/peer_manager/peer_database.c",
    0x00097214: "components/ble/peer_manager/peer_database.c",
    0x000972B4: "components/ble/peer_manager/peer_database.c",
    0x000972E8: "components/ble/peer_manager/peer_database.c",
    0x00097318: "components/ble/peer_manager/peer_database.c",
    0x00097334: "components/ble/peer_manager/peer_database.c",
    0x00097360: "components/libraries/fds/fds.c",
    0x00097454: "components/libraries/fds/fds.c",
    0x000975C4: "components/libraries/fds/fds.c",
    0x000975DC: "components/libraries/fds/fds.c",
    0x000881E4: "components/ble/peer_manager/peer_id.c",
}


# SEGGER implementations shipped inside the pinned Nordic SDK. These remain
# third-party source even though the SDK is their distribution container.
APP_SEGGER_RTT_SYMBOLS = {
    0x00031948: "SEGGER_RTT_Init",
    0x0003194C: "SEGGER_RTT_Read",
    0x00031964: "SEGGER_RTT_ReadNoLock",
    0x000319E0: "SEGGER_RTT_Write",
    0x00031A18: "SEGGER_RTT_WriteNoLock",
    0x00036D68: "SEGGER_RTT_Init",
    0x00036F72: "_GetAvailWriteSpace",
    0x00037EB6: "_WriteBlocking",
    0x00037F10: "_WriteNoCheck",
}

APP_SEGGER_FPRINTF_SYMBOLS = {
    0x00056744: "buffer_add",
    0x00072310: "int_print",
    0x00078A72: "nrf_fprintf_fmt",
    0x00093EF8: "unsigned_print",
}


# Standard C/Arm EABI helpers retained from the stock toolchain runtime. These
# are linked from the selected compiler runtime rather than recreated locally.
APP_TOOLCHAIN_RUNTIME_SYMBOLS = {
    0x000274E8: "__aeabi_uldivmod",
    0x0002754A: "__aeabi_ldivmod",
    0x000275AC: "__aeabi_llsl",
    0x000275CA: "__aeabi_llsr",
    0x000275F4: "isspace",
    0x00027606: "qsort",
    0x000276A4: "rand",
    0x000276B8: "srand",
    0x000276C8: "gmtime",
    0x0002775C: "memmove",
    0x0002779C: "__aeabi_memset",
    0x000277AA: "__aeabi_memclr",
    0x000277AE: "memset",
    0x000277C0: "strcat",
    0x000277D8: "strncpy",
    0x000277F0: "strlen",
    0x000277FE: "strcmp",
    0x0002781A: "memcmp",
    0x00027834: "strncmp",
    0x00027854: "strtok",
    0x00027898: "sscanf",
    0x00027AFC: "__aeabi_dadd",
    0x00027C3E: "__aeabi_dsub",
    0x00027C44: "__aeabi_drsub",
    0x00027C4A: "__aeabi_dmul",
    0x00027D2E: "__aeabi_ddiv",
    0x00027E0C: "__aeabi_l2f",
    0x00027E38: "__aeabi_i2d",
    0x00027E5A: "__aeabi_ui2d",
    0x00027E74: "__aeabi_d2iz",
    0x00027EB2: "__aeabi_d2uiz",
    0x00027EE4: "__aeabi_f2d",
    0x00027F0C: "__aeabi_cdrcmple",
    0x00027F3C: "__aeabi_cdcmple",
    0x00027F6C: "__aeabi_d2f",
    0x00027FA4: "__aeabi_uidiv",
    0x00027FD0: "__aeabi_lasr",
    0x00028334: "__aeabi_d2ulz",
    0x000283A0: "__scatterload",
    0x000286F4: "__scatterload_decompress",
    0x00038060: "printf",
    0x00038080: "snprintf",
    0x000380B4: "sprintf",
    0x000380DC: "vsnprintf",
    0x000381F0: "atan",
    0x000384C8: "atan2f",
    0x00038774: "atanf",
    0x000388D8: "ceil",
    0x000389F0: "ceilf",
    0x00038A5C: "cosf",
    0x00038BB0: "exp",
    0x00038F08: "expf",
    0x000390F0: "fabs",
    0x00039108: "floor",
    0x00039220: "floorf",
    0x00039290: "fmaxf",
    0x000392D8: "fminf",
    0x00039320: "log",
    0x000396E4: "log10f",
    0x00039864: "logf",
    0x000399D0: "pow",
    0x0003A620: "powf",
    0x0003AC88: "round",
    0x0003AD68: "roundf",
    0x0003AE04: "sinf",
    0x0003AF94: "sqrt",
    0x0003B00E: "sqrtf",
    0x0003B048: "tanf",
    0x0003B1C8: "tanh",
    0x0003B328: "tanhf",
    0x0003B5C0: "expm1",
}
APP_TOOLCHAIN_RUNTIME_SYMBOLS.update({
    int(item["entry"]): str(item["symbol"])
    for item in TOOLCHAIN_FRONTIER_64_127_FUNCTIONS
        + TOOLCHAIN_FRONTIER_LT32_FUNCTIONS
})

# Stripped Arm C-library internals whose provider and role are proven by their
# complete semantics and runtime-only call graph, but whose private upstream
# symbol spelling is not a stable ABI. These labels are descriptive, not claims
# about the vendor's original private names.
APP_TOOLCHAIN_RUNTIME_INTERNALS = {
    0x000275EC: "internal:ctype_table_pointer_get",
    0x000278D0: "internal:scanf_integer_conversion",
    0x00027A1C: "internal:scanf_string_conversion",
    0x00027FF4: "internal:scanf_digit_value",
    0x00028010: "internal:scanf_format_getc",
    0x0002801C: "internal:vsscanf_descriptor_init",
    0x00028038: "internal:sscanf_input_getc",
    0x00028056: "internal:sscanf_input_ungetc",
    0x00028078: "internal:binary32_round_to_even",
    0x0002808A: "internal:binary32_pack_from_u64",
    0x000280E6: "internal:binary32_round_to_integral_even",
    0x00028122: "internal:binary64_round_to_even",
    0x00028140: "internal:binary64_pack",
    0x000281DC: "internal:binary64_scale_pow2_flush_underflow",
    0x0002820A: "internal:binary64_sqrt",
    0x000282AC: "internal:binary64_round_to_integral_even",
    0x00028364: "internal:binary32_compare_flags",
    0x0002839A: "internal:floating_environment_control_stub",
    0x000283C4: "internal:scanf_core",
    0x00038110: "internal:binary64_classify",
    0x00038140: "internal:binary32_classify",
    0x0003F530: "internal:printf_binary64_decimal_conversion",
    0x00043080: "internal:printf_core",
    0x00043734: "internal:printf_left_padding",
    0x00043758: "internal:printf_width_padding",
    0x00043BBC: "internal:printf_bounded_buffer_putc",
    0x00044A6C: "internal:printf_buffer_putc",
    0x0006570A: "internal:printf_stdout_putc_adapter",
    0x0003B40C: "internal:binary64_polynomial_evaluate",
    0x0003B508: "internal:binary64_positive_infinity_raise_divzero",
    0x0003B538: "internal:binary64_self_add",
    0x0003B54C: "internal:binary64_add_pair",
    0x0003B560: "internal:binary64_invalid_zero_div_zero",
    0x0003B580: "internal:binary64_overflow_raise_square",
    0x0003B5A0: "internal:binary64_underflow_raise_square",
    0x0003BAB4: "internal:binary32_positive_infinity_raise_divzero",
    0x0003BAC8: "internal:binary32_self_add",
    0x0003BACE: "internal:binary32_add_pair",
    0x0003BAD4: "internal:binary32_invalid_zero_div_zero",
    0x0003BAE4: "internal:binary32_overflow_raise_square",
    0x0003BAF4: "internal:binary32_underflow_raise_square",
    0x0003BB04: "internal:binary32_trig_argument_reduce",
    0x0003BC9C: "internal:errno_set",
}


# Exact CMSIS-FreeRTOS v10.5.1 correlations.  The public wrappers are ordered
# alphabetically in the recovered linked image; the function-local control
# flow, error values, static-control-block sizes, and FreeRTOS calls match the
# authenticated Arm snapshot.  IRQ_Context is the wrapper's inlined context
# classifier emitted as a standalone local function by the original build.
APP_PRODUCT_FUNCTIONS.update({
    int(item["entry"]): str(item["symbol"])
    for item in RESOLVED_THUNKS
    if item["provider"] == "r1_product_specific"
})


APP_CMSIS_FREERTOS_SYMBOLS = {
    0x0002FEBC: "IRQ_Context",
    0x0007D154: "osDelay",
    0x0007D172: "osEventFlagsNew",
    0x0007D1A0: "osEventFlagsSet",
    0x0007D200: "osEventFlagsWait",
    0x0007D26C: "osKernelGetState",
    0x0007D28C: "osKernelGetTickCount",
    0x0007D2A4: "osKernelGetTickFreq",
    0x0007D310: "osMessageQueueGet",
    0x0007D388: "osMessageQueueGetCapacity",
    0x0007D390: "osMessageQueueGetCount",
    0x0007D3B4: "osMessageQueueNew",
    0x0007D40C: "osMessageQueuePut",
    0x0007D488: "osMutexAcquire",
    0x0007D4D6: "osMutexNew",
    0x0007D536: "osMutexRelease",
    0x0007D57C: "osSemaphoreAcquire",
    0x0007D5E8: "osSemaphoreGetCount",
    0x0007D60C: "osSemaphoreNew",
    0x0007D698: "osSemaphoreRelease",
    0x0007D6F4: "osThreadFlagsSet",
    0x0007D780: "osThreadFlagsWait",
    0x0007D814: "osThreadGetId",
    0x0007D818: "osThreadNew",
    0x0007D8A6: "osThreadSetPriority",
    0x0007D8D6: "osThreadTerminate",
    0x0007D90C: "osTimerNew",
    0x0007D9B0: "osTimerStart",
    0x0007D9EA: "osTimerStop",
}


# FreeRTOS attribution is exact-entry-only. The apparent kernel interval also
# contains product algorithms, Nordic storage, Bosch, FlashDB, and other code;
# range membership is therefore never accepted as provider evidence.
APP_FREERTOS_EXACT_SYMBOLS = {
    0x00027218: "vPortSVCHandler",
    0x00027238: "vPortStartFirstTask",
    0x0002725C: "xPortPendSVHandler",
    0x000316E8: "xPortSysTickHandler",
    0x0005CF78: "eTaskConfirmSleepModeStatus",
    0x0005CFAC: "eTaskGetState",
    0x00084CF0: "prvAddCurrentTaskToDelayedList",
    0x00084D68: "prvAddNewTaskToReadyList",
    0x0008522C: "prvIsQueueEmpty",
    0x0009566C: "uxTaskGetNumberOfTasks",
    0x00085468: "prvResetNextTaskUnblockTime",
    0x00085534: "prvUnlockQueue",
    0x00084E58: "prvCheckForValidListAndQueue",
    0x00084EA4: "prvCopyDataFromQueue",
    0x00084ECA: "prvCopyDataToQueue",
    0x00084F36: "prvDeleteTCB",
    0x00084F68: "prvGetExpectedIdleTime",
    0x00084F98: "prvHeapInit",
    0x0008507C: "prvInitialiseMutex",
    0x00085094: "prvInitialiseNewQueue",
    0x000850B6: "prvInitialiseNewTask",
    0x0008515A: "prvInitialiseNewTimer",
    0x000851A4: "prvInsertBlockIntoFreeList",
    0x000851F4: "prvInsertTimerInActiveList",
    0x00085248: "prvListTasksWithinSingleList",
    0x000852A0: "prvProcessExpiredTimer",
    0x000852E0: "prvProcessReceivedCommands",
    0x000853D4: "prvProcessTimerOrBlockTask",
    0x00085440: "prvReloadTimer",
    0x00085484: "prvSampleTimeNow + inlined prvSwitchTimerLists",
    0x000854CC: "prvTaskCheckFreeStackSpace",
    0x000854E0: "prvTaskExitError",
    0x000854FC: "prvTestWaitCondition",
    0x000855A0: "pvPortMalloc",
    0x00085684: "pvTaskIncrementMutexHeldCount",
    0x0008569C: "xTaskGetApplicationTaskTag",
    0x000856C0: "pxPortInitialiseStack",
    0x00093EAC: "ulPortRaiseBASEPRI",
    0x00093EB8: "ulPortRaiseBASEPRI",
    0x0009560E: "uxListRemove",
    0x00095678: "uxTaskGetSystemState",
    0x00095738: "uxTaskResetEventItemValue",
    0x00095C90: "vListInitialise",
    0x00095CA6: "vListInitialiseItem",
    0x00095CAC: "vListInsert",
    0x00095CDC: "vListInsertEnd",
    0x00095CF4: "vPortEnterCritical",
    0x00095D24: "vPortExitCritical",
    0x00095D48: "vPortFree",
    0x00095DA4: "vPortSetupTimerInterrupt",
    0x00095DE4: "vPortSuppressTicksAndSleep",
    0x00095F18: "vPortValidateInterruptPriority",
    0x00095F70: "vQueueDelete",
    0x00095F8E: "vQueueWaitForMessageRestricted",
    0x00095FD4: "vTaskDelay",
    0x00096020: "vTaskDelete",
    0x000960B4: "vTaskGetInfo",
    0x00096160: "vTaskSetTimeOutState",
    0x00096170: "vTaskMissedYield",
    0x00096188: "vTaskPlaceOnUnorderedEventList",
    0x000961B8: "vTaskPlaceOnEventList",
    0x00096208: "vTaskPlaceOnEventListRestricted",
    0x0009626C: "vTaskPriorityDisinheritAfterTimeout",
    0x00096314: "vTaskPrioritySet",
    0x000963E8: "xTaskRemoveFromUnorderedEventList",
    0x000964C8: "vTaskStartScheduler",
    0x0009653C: "vTaskStepTick",
    0x0009659C: "vTaskSuspendAll",
    0x000965AC: "vTaskSwitchContext",
    0x0009779C: "xEventGroupCreate",
    0x000977B8: "xEventGroupCreateStatic",
    0x000977DE: "xEventGroupGetBitsFromISR",
    0x000977F4: "xEventGroupSetBits",
    0x0009787C: "xTimerPendFunctionCallFromISR",
    0x0009788C: "xEventGroupWaitBits",
    0x000979DC: "xPortStartScheduler",
    0x00097A88: "xQueueCreateCountingSemaphore",
    0x00097AB0: "xQueueCreateCountingSemaphoreStatic",
    0x00097ADE: "xQueueCreateMutex",
    0x00097AF4: "xQueueCreateMutexStatic",
    0x00097B0E: "xQueueGenericCreate",
    0x00097B62: "xQueueGenericCreateStatic",
    0x00097BA4: "prvInitialiseNewQueue",
    0x00097C50: "xQueueGenericSend",
    0x00097DA4: "xQueueGenericSendFromISR",
    0x00097E6C: "xQueueGiveFromISR",
    0x00097F14: "xQueueGiveMutexRecursive",
    0x00097F50: "xQueueReceive",
    0x0009807C: "xQueueReceiveFromISR",
    0x00098120: "xQueueSemaphoreTake",
    0x00098284: "xQueueTakeMutexRecursive",
    0x00098340: "xTaskCheckForTimeOut",
    0x000983B8: "xTaskCreate",
    0x00098418: "xTaskCreateStatic",
    0x00098484: "xTaskGenericNotify",
    0x000985AC: "xTaskGenericNotifyFromISR",
    0x00098700: "xTaskNotifyWait",
    0x0009879C: "xTaskGetCurrentTaskHandle",
    0x000987A8: "xTaskGetSchedulerState",
    0x000987C4: "xTaskGetTickCount",
    0x000987E0: "xTaskIncrementTick",
    0x00098910: "xTaskPriorityDisinherit",
    0x000989AC: "xTaskPriorityInherit",
    0x00098A4C: "xTaskRemoveFromEventList",
    0x00098B24: "xTaskResumeAll",
    0x00098C48: "xTimerCreate",
    0x00098C7C: "xTimerCreateStatic",
    0x00098CA8: "xTimerCreateTimerTask",
    0x00098D04: "xTimerGenericCommand",
    0x00098D68: "xTimerIsTimerActive",
}

APP_FREERTOS_EXACT_SOURCES = {
    0x00027218: "external/freertos/portable/GCC/nrf52/port.c",
    0x00027238: "external/freertos/portable/GCC/nrf52/port.c",
    0x0002725C: "external/freertos/portable/GCC/nrf52/port.c",
    0x000316E8: "external/freertos/portable/CMSIS/nrf52/port_cmsis_systick.c",
    0x0005CF78: "external/freertos/source/tasks.c",
    0x0005CFAC: "external/freertos/source/tasks.c",
    0x00084CF0: "external/freertos/source/tasks.c",
    0x00084D68: "external/freertos/source/tasks.c",
    0x0008522C: "external/freertos/source/queue.c",
    0x0009566C: "external/freertos/source/tasks.c",
    0x00085468: "external/freertos/source/tasks.c",
    0x00085534: "external/freertos/source/queue.c",
    0x00084E58: "external/freertos/source/timers.c",
    0x00084EA4: "external/freertos/source/queue.c",
    0x00084ECA: "external/freertos/source/queue.c",
    0x00084F36: "external/freertos/source/tasks.c",
    0x00084F68: "external/freertos/source/tasks.c",
    0x00084F98: "external/freertos/source/portable/MemMang/heap_4.c",
    0x0008507C: "external/freertos/source/queue.c",
    0x00085094: "external/freertos/source/queue.c",
    0x000850B6: "external/freertos/source/tasks.c",
    0x0008515A: "external/freertos/source/timers.c",
    0x000851A4: "external/freertos/source/portable/MemMang/heap_4.c",
    0x000851F4: "external/freertos/source/timers.c",
    0x00085248: "external/freertos/source/tasks.c",
    0x000852A0: "external/freertos/source/timers.c",
    0x000852E0: "external/freertos/source/timers.c",
    0x000853D4: "external/freertos/source/timers.c",
    0x00085440: "external/freertos/source/timers.c",
    0x00085484: "external/freertos/source/timers.c",
    0x000854CC: "external/freertos/source/tasks.c",
    0x000854E0: "external/freertos/portable/CMSIS/nrf52/port_cmsis.c",
    0x000854FC: "external/freertos/source/event_groups.c",
    0x000855A0: "external/freertos/source/portable/MemMang/heap_4.c",
    0x00085684: "external/freertos/source/tasks.c",
    0x0008569C: "external/freertos/source/tasks.c",
    0x000856C0: "external/freertos/portable/CMSIS/nrf52/port_cmsis.c",
    0x00093EAC: "external/freertos/portable/CMSIS/nrf52/portmacro_cmsis.h",
    0x00093EB8: "external/freertos/portable/CMSIS/nrf52/portmacro_cmsis.h",
    0x00095C90: "external/freertos/source/list.c",
    0x00095CA6: "external/freertos/source/list.c",
    0x00095CAC: "external/freertos/source/list.c",
    0x00095CDC: "external/freertos/source/list.c",
    0x0009560E: "external/freertos/source/list.c",
    0x00095678: "external/freertos/source/tasks.c",
    0x00095738: "external/freertos/source/tasks.c",
    0x00095CF4: "external/freertos/portable/CMSIS/nrf52/port_cmsis.c",
    0x00095D24: "external/freertos/portable/CMSIS/nrf52/port_cmsis.c",
    0x00095D48: "external/freertos/source/portable/MemMang/heap_4.c",
    0x00095DA4: "external/freertos/portable/CMSIS/nrf52/port_cmsis_systick.c",
    0x00095DE4: (
        "external/freertos/portable/CMSIS/nrf52/port_cmsis_systick.c + "
        "components/libraries/pwr_mgmt/nrf_pwr_mgmt.c"
    ),
    0x00095F18: "external/freertos/portable/CMSIS/nrf52/port_cmsis.c",
    0x00095F70: "external/freertos/source/queue.c",
    0x00095F8E: "external/freertos/source/queue.c",
    0x00095FD4: "external/freertos/source/tasks.c",
    0x00096020: "external/freertos/source/tasks.c",
    0x000960B4: "external/freertos/source/tasks.c",
    0x00096160: "external/freertos/source/tasks.c",
    0x00096170: "external/freertos/source/tasks.c",
    0x00096188: "external/freertos/source/tasks.c",
    0x000961B8: "external/freertos/source/tasks.c",
    0x00096208: "external/freertos/source/tasks.c",
    0x0009626C: "external/freertos/source/tasks.c",
    0x00096314: "external/freertos/source/tasks.c",
    0x000963E8: "external/freertos/source/tasks.c",
    0x000964C8: "external/freertos/source/tasks.c",
    0x0009653C: "external/freertos/source/tasks.c",
    0x0009659C: "external/freertos/source/tasks.c",
    0x000965AC: "external/freertos/source/tasks.c",
    0x0009779C: "external/freertos/source/event_groups.c",
    0x000977B8: "external/freertos/source/event_groups.c",
    0x000977DE: "external/freertos/source/event_groups.c",
    0x000977F4: "external/freertos/source/event_groups.c",
    0x0009787C: "external/freertos/source/timers.c",
    0x0009788C: "external/freertos/source/event_groups.c",
    0x000979DC: "external/freertos/portable/CMSIS/nrf52/port_cmsis.c",
    0x00097A88: "external/freertos/source/queue.c",
    0x00097AB0: "external/freertos/source/queue.c",
    0x00097ADE: "external/freertos/source/queue.c",
    0x00097AF4: "external/freertos/source/queue.c",
    0x00097B0E: "external/freertos/source/queue.c",
    0x00097B62: "external/freertos/source/queue.c",
    0x00097BA4: "external/freertos/source/queue.c",
    0x00097C50: "external/freertos/source/queue.c",
    0x00097DA4: "external/freertos/source/queue.c",
    0x00097E6C: "external/freertos/source/queue.c",
    0x00097F14: "external/freertos/source/queue.c",
    0x00097F50: "external/freertos/source/queue.c",
    0x0009807C: "external/freertos/source/queue.c",
    0x00098120: "external/freertos/source/queue.c",
    0x00098284: "external/freertos/source/queue.c",
    0x00098340: "external/freertos/source/tasks.c",
    0x000983B8: "external/freertos/source/tasks.c",
    0x00098418: "external/freertos/source/tasks.c",
    0x00098484: "external/freertos/source/tasks.c",
    0x000985AC: "external/freertos/source/tasks.c",
    0x00098700: "external/freertos/source/tasks.c",
    0x0009879C: "external/freertos/source/tasks.c",
    0x000987A8: "external/freertos/source/tasks.c",
    0x000987C4: "external/freertos/source/tasks.c",
    0x000987E0: "external/freertos/source/tasks.c",
    0x00098910: "external/freertos/source/tasks.c",
    0x000989AC: "external/freertos/source/tasks.c",
    0x00098A4C: "external/freertos/source/tasks.c",
    0x00098B24: "external/freertos/source/tasks.c",
    0x00098C48: "external/freertos/source/timers.c",
    0x00098C7C: "external/freertos/source/timers.c",
    0x00098CA8: "external/freertos/source/timers.c",
    0x00098D04: "external/freertos/source/timers.c",
    0x00098D68: "external/freertos/source/timers.c",
}


# Exact functions retained from Armink's CmBacktrace core. The R1 image proves
# compatibility with the authenticated 4abadfa0..73714489 interval. These
# functions are provider-owned even though the exact vendor checkout (or a
# possible fork) cannot be narrowed to one commit.
APP_CMBACKTRACE_SYMBOLS = {
    0x0002746A: "cmb_get_psp",
    0x00027470: "cmb_get_sp",
    0x000584F0: "cm_backtrace_call_stack_any",
    0x000588A4: "cm_backtrace_init",
    0x0005C568: "disassembly_ins_is_bl_blx",
    0x0005CD14: "dump_stack",
    0x000634CC: "fault_diagnosis",
}


# Functions which combine the provider's algorithm/skeleton with recovered R1
# hooks, formatting, FreeRTOS accessors, or vector policy. Production uses the
# authenticated provider and permits only these bounded product adapters.
APP_CMBACKTRACE_ADAPTERS = {
    0x000274AC: "NMI_Handler -> cm_backtrace_fault",
    0x000274B8: "HardFault_Handler -> cm_backtrace_fault",
    0x000274C4: "MemoryManagement_Handler -> cm_backtrace_fault",
    0x000274D0: "BusFault_Handler -> cm_backtrace_fault",
    0x000274DC: "UsageFault_Handler -> cm_backtrace_fault",
    0x000585BC: "cm_backtrace_fault + R1 fault diagnostics",
    0x0005882C: "R1 fault-time logger",
    0x0006A098: "vTaskName",
    0x0006A0B0: "get_cur_thread_stack_info + R1 FreeRTOS stack adapters",
    0x00081918: "print_call_stack + R1 formatting adapter",
    0x00096138: "R1 FreeRTOS saved-SP accessor",
    0x0009613C: "R1 FreeRTOS used-stack-word accessor",
    0x000964B0: "R1 FreeRTOS current-task stack-base accessor",
    0x000964BC: "R1 FreeRTOS current-task stack-depth accessor",
}
APP_CMBACKTRACE_ADAPTERS.update({
    int(item["entry"]): str(item["symbol"])
    for item in R1_FRONTIER_212_222_CMBACKTRACE_ADAPTERS
})


# Eight complete AES-128 inverse-core bodies match kokke/tiny-AES-c. The
# recovered key schedule is the 176-byte AES-128 schedule and the aggregate
# call graph preserves tiny-AES-c's AddRoundKey -> InvMixColumns/InvShiftRows/
# InvSubBytes -> Multiply -> xtime structure. v1.0.0 is the pinned public
# provider snapshot; the exact vendor checkout is not uniquely proven.
APP_TINY_AES_SYMBOLS = {
    0x00048948: "AddRoundKey",
    0x00048AC8: "InvCipher",
    0x00061740: "KeyExpansion",
    0x0007272E: "InvMixColumns",
    0x000727FC: "InvShiftRows",
    0x00072830: "InvSubBytes",
    0x00076570: "Multiply",
    0x00098E38: "xtime",
}


# Bosch BMA456 SensorAPI v2.29.0 functions accepted by function-local semantic
# comparison.  The recovered null_pointer_check tests delay_us at bma4_dev
# offset 0x2c; v2.24.1 tested intf_ptr instead, while Bosch v2.29.0 makes the
# exact recovered change.  Public and static bodies below match that release.
APP_BMA456_SYMBOLS = {
    0x000543C4: "bma456w_init",
    0x00054408: "bma4_get_advance_power_save",
    0x00054440: "bma4_get_fifo_length",
    0x0005447E: "bma4_init",
    0x00054534: "bma4_read_regs",
    0x000545CA: "bma4_set_accel_config",
    0x00054640: "bma4_set_accel_enable",
    0x0005468E: "bma4_set_advance_power_save",
    0x000546D0: "bma4_set_fifo_config",
    0x0005475A: "bma4_write_regs",
    0x00070FDA: "increment_feature_config_addr",
    0x0007B61C: "null_pointer_check",
    0x00087BBC: "read_regs",
    0x00087E58: "read_within_len_regs",
    0x0008EDD8: "set_feature_config_start_addr",
    0x00096820: "validate_odr_bandwidth_perfmode",
    0x0009756A: "write_regs",
    0x000976B8: "write_within_len_regs",
}


# Product-side calls around the Bosch provider.  These functions contain R1
# logging, fixed configuration, buffer ownership, or bus/event policy and are
# therefore the only locally implementable part of this boundary.
APP_BMA456_ADAPTERS = {
    0x00053AA4: "r1_bma456_delay_us_port",
    0x00053AB4: "r1_bma456_i2c_read_port",
    0x00053AD0: "r1_bma456_i2c_write_port",
    0x00053AEC: "r1_bma456_device_context_init",
    0x00053B2C: "r1_bma456w_identity_probe",
    0x00053C6C: "r1_bma456w_configuration",
    0x000541A8: "r1_bma456w_fifo_read",
    0x000544C8: "r1_bma456w_bounded_fifo_transfer",
}


# ST LIS2DW12 standard C driver bodies.  R1 diagnostics call the part
# "LIS2DOC", but WHO_AM_I 0x44 and every retained register/bit operation match
# LIS2DW12.  The ctx mdelay layout requires commit 18b0866 or later; the
# guarded INT1 route reads and two-argument reset setter exclude v2.2+ and
# v2.3+ respectively.  v2.1.0 is the newest compatible official release.
APP_LIS2DW12_SYMBOLS = {
    0x000750B8: "lis2dw12_block_data_update_set",
    0x00075120: "lis2dw12_data_rate_set",
    0x0007517C: "lis2dw12_device_id_get",
    0x000753AC: "lis2dw12_fifo_data_level_get",
    0x000753C6: "lis2dw12_fifo_mode_set",
    0x000753F4: "lis2dw12_fifo_watermark_set",
    0x00075422: "lis2dw12_full_scale_set",
    0x00075450: "lis2dw12_filter_path_set",
    0x000754AC: "lis2dw12_filter_bandwidth_set",
    0x000756CC: "lis2dw12_pin_int1_route_get",
    0x000756DA: "lis2dw12_pin_int1_route_set",
    0x0007575A: "lis2dw12_power_mode_set",
    0x000757C4: "lis2dw12_read_reg",
    0x000757D2: "lis2dw12_reset_get",
    0x000757EC: "lis2dw12_reset_set",
    0x0007581A: "lis2dw12_tap_detection_on_z_set",
    0x00075848: "lis2dw12_tap_detection_on_y_set",
    0x00075876: "lis2dw12_tap_detection_on_x_set",
    0x000758A4: "lis2dw12_tap_dur_set",
    0x000758D2: "lis2dw12_tap_mode_set",
    0x00075900: "lis2dw12_tap_quiet_set",
    0x0007592E: "lis2dw12_tap_shock_set",
    0x0007595C: "lis2dw12_tap_threshold_x_set",
    0x0007598A: "lis2dw12_tap_threshold_y_set",
    0x000759B8: "lis2dw12_tap_threshold_z_set",
    0x000759E6: "lis2dw12_write_reg",
}


APP_LIS2DW12_ADAPTERS = {
    0x000750A0: "r1_lis2dw12_accel_burst_read",
    0x000750E8: "r1_lis2dw12_fifo_read",
    0x0007518A: "r1_lis2dw12_register_0x17_setup",
    0x000751B8: "r1_lis2dw12_double_tap_disable",
    0x000754DC: "r1_lis2dw12_identity_probe",
    0x00075510: "r1_lis2dw12_configuration",
}


# Product-wide selection and sample-normalization functions around the three
# installed-motion candidates. The clean-room image admits only the licensed
# ST and Bosch providers; QMA remains a disabled provider boundary.
APP_MOTION_ADAPTERS = {
    0x00050128: "r1_motion_interrupt_input_lookup",
    0x00050150: "r1_motion_bus_lookup",
    0x00050170: "r1_motion_bus_release",
    0x0005017C: "r1_motion_bus_acquire",
    0x00050188: "r1_motion_bus_read_request",
    0x000501C8: "r1_motion_bus_write_request",
    0x00050208: "r1_motion_probe_and_select_provider",
    0x0005025C: "r1_motion_refresh_selection",
    0x00050270: "r1_motion_selected_provider_initialize",
    0x00050294: "r1_motion_selected_interrupt_dispatch",
    0x000502AC: "r1_motion_selected_fifo_read",
    0x0006F1A8: "r1_bma456w_probe_wrapper",
    0x0006F1BC: "r1_bma456w_configuration_wrapper",
    0x0006F1DA: "r1_bma456w_interrupt_noop",
    0x0006F1DC: "r1_bma456w_fifo_normalize",
    0x0006F228: "r1_motion_orientation_accumulator",
    0x0006F304: "r1_motion_sample_event_adapter",
    0x0006F380: "r1_lis2dw12_probe_wrapper",
    0x0006F394: "r1_lis2dw12_configuration_wrapper",
    0x0006F3B2: "r1_lis2dw12_interrupt_noop",
    0x0006F3B4: "r1_lis2dw12_fifo_normalize",
    0x0006F400: "r1_motion_initialize_entry",
    0x0006F4A0: "r1_motion_thirty_sample_batch_producer",
}


# Symbols accepted from source diagnostics and semantic comparison with pinned
# FlashDB 2.0.0. Reverse-time traversal and _fdb_db_path jointly distinguish
# this exact release from older snapshots. Other FlashDB-marked functions
# retain provider-only matches.
FLASHDB_SYMBOLS = {
    0x0003F014: "_fdb_db_path",
    0x0003F022: "_fdb_flash_erase",
    0x0003F03E: "_fdb_flash_read",
    0x0003F05A: "_fdb_flash_write",
    0x0003F076: "_fdb_get_status",
    0x0003F094: "_fdb_init_ex",
    0x0003F2EC: "_fdb_init_finish",
    0x0003F384: "_fdb_set_status",
    0x0003F3B0: "_fdb_write_status",
    0x00057EB4: "check_sec_hdr_cb",
    0x0006366C: "fdb_blob_make",
    0x00063672: "fdb_blob_read",
    0x00063694: "fdb_tsdb_control",
    0x00063814: "fdb_tsdb_init",
    0x00063A28: "fdb_tsl_append",
    0x00063AB8: "fdb_tsl_clean",
    0x00063AD8: "fdb_tsl_iter_by_time",
    0x00063CB4: "fdb_tsl_query_count",
    0x00063D40: "fdb_tsl_to_blob",
    0x000650C4: "format_all_cb",
    0x000650D4: "format_sector",
    0x0006A158: "get_last_sector_addr",
    0x0006A176: "get_last_tsl_addr",
    0x0006A194: "get_next_sector_addr",
    0x0006A1B2: "get_next_tsl_addr",
    0x00087428: "query_count_cb",
    0x00087C24: "read_sector_info",
    0x00087E14: "read_tsl",
    0x000895F4: "sector_iterator",
    0x00093744: "tsl_append",
    0x00093828: "tsl_format_all",
    0x00094AE0: "update_sec_status",
    0x0009763C: "write_tsl",
}


# The FAL sources bundled by FlashDB 2.0.0 report version 0.5.99. These are
# complete upstream bodies; only the R1 flash device and seven-entry partition
# configuration belong in local code.
FAL_SYMBOLS = {
    0x00057E1C: "check_and_update_part_cache",
    0x00062DF4: "fal_flash_device_find",
    0x00062E68: "fal_flash_init",
    0x00062F40: "fal_init",
    0x00062FF4: "fal_partition_erase",
    0x00063150: "fal_partition_find",
    0x000631C0: "fal_partition_init",
    0x000631E8: "fal_partition_read",
    0x00063358: "fal_partition_write",
    0x00064F74: "flash_device_find_by_part",
}


# QST-authored QMA6100 V1.0 lineage is publicly visible in an unlicensed
# evaluation/demo snapshot (Yangzhiqiang@qst, 2020-05-27). It proves these
# bodies originated in the provider codebase but is correlation evidence only,
# not a production dependency. A lawfully licensed QST source remains required.
APP_QMA6100_PROVIDER_SYMBOLS = {
    0x00086E34: "qma6100_chip_id",
    0x00087188: "qma6100_set_range",
    0x000871C4: "qma6100_soft_reset",
}


# Owner-authorized full reductions of the two small named sensor families.
# These retain their attribution-family labels while routing their recovered
# bodies to independently compiled C under r1/reconstructed/.
APP_GXT310_RECONSTRUCTED_SYMBOLS = {
    0x00050F9C: "gxt310_enable_pair",
    0x0006F804: "gxt310_channel_0_switch_mode",
    0x0006F818: "gxt310_channel_0_trigger_one_shot",
    0x0006F81E: "gxt310_channel_2_switch_mode",
    0x0006F832: "gxt310_channel_2_trigger_one_shot",
}


# Owner-authorized first algorithm reductions: small, fully recovered Goodix
# and GoMore primitives.  Opaque static-table addresses are explicit typed
# bindings in the reconstruction, never copied absolute firmware pointers.
APP_GOODIX_PRIMITIVES_RECONSTRUCTED_SYMBOLS = {
    0x000928CA: "gomore_primitives_scale",
    0x0006E540: "goodix_primitives_nadt_result_binding",
    0x0006E838: "goodix_primitives_nadt_preprocess_execute",
    0x0007DD58: "goodix_primitives_nadt_alternate_state_classify",
    0x00029656: "goodix_primitives_float_buffer_mean",
    0x0006DA9C: "goodix_primitives_hrv_configuration_binding",
    0x0006DAD0: "goodix_primitives_hrv_context_destroy",
    0x0006DB58: "goodix_primitives_hrv_context_destroy",
    0x0006DB5C: "goodix_primitives_hrv_context_create",
    0x0006DF14: "goodix_primitives_hrv_initialize_for_sample_count",
    0x0006DF60: "goodix_primitives_build_hrv_version",
    0x0002CC5C: "goodix_primitives_hrv_initialize_dispatch",
    0x0002F224: "goodix_primitives_sample_variance",
    0x00034A58: "goodix_primitives_sample_standard_deviation",
    0x00034CBC: "goodix_primitives_hr_extrema_tracker_update",
    0x00034500: "goodix_primitives_spo2_report_analyze",
    0x0003738C: "goodix_primitives_float_buffer_standard_deviation",
    0x0007DCD8: "goodix_primitives_sample_variance_or_zero",
    0x0007DD18: "goodix_primitives_population_variance_or_zero",
    0x00061FD4: "goodix_primitives_sample_standard_deviation_or_zero",
    0x00061FEA: "goodix_primitives_population_standard_deviation_or_zero",
    0x0006EB00: "goodix_primitives_copy_preprocess_version",
    0x0006CC34: "goodix_primitives_copy_process_version",
    0x00029C74: "goodix_primitives_dispatch_state",
    0x0002ACF4: "goodix_primitives_record_initialize_once",
    0x0002D16C: "goodix_primitives_initialize_device",
    0x00029D34: "goodix_primitives_select_fixed_pair",
    0x00029F88: "goodix_primitives_record_initialize",
    0x0002A474: "goodix_primitives_reset_state_record",
    0x0006F9D4: "goodix_primitives_call_hook",
    0x0002ABEC: "goodix_primitives_clear_state_flags",
    0x0006A140: "goodix_primitives_library_code",
    0x0006A130: "goodix_primitives_table_9d640",
    0x0006A138: "goodix_primitives_table_a04cc",
    0x0006A148: "goodix_primitives_table_a50b0",
    0x0006A150: "goodix_primitives_table_a692c",
    0x0006A018: "goodix_primitives_table_ad1ac",
    0x0006CC2C: "goodix_primitives_table_ad13c",
    0x0006EAF8: "goodix_primitives_table_ad160",
    0x0002E8C8: "goodix_primitives_constant_one_a",
    0x0002E8C4: "goodix_primitives_constant_four",
    0x0002AE00: "goodix_primitives_constant_one_b",
    0x0002963A: "goodix_primitives_buffer_record_initialize",
    0x00096A20: "goodix_primitives_buffer_record_create",
    0x0007CBA0: "goodix_primitives_buffer_record_destroy",
    0x000929B6: "goodix_primitives_integer_max_index",
    0x000667E4: "goodix_primitives_copy_dlcom_version",
    0x000664F4: "goodix_primitives_word_window_push",
    0x0003EFD8: "goodix_primitives_logistic_score",
    0x0002A9D2: "goodix_primitives_noop_a",
    0x0002E950: "goodix_primitives_noop_b",
    0x0002A54C: "goodix_primitives_zero_a",
    0x0002A610: "goodix_primitives_zero_b",
    0x0002D458: "goodix_primitives_second_word",
    0x000294F8: "goodix_primitives_transformed_differs",
    0x0002950C: "goodix_primitives_transform_in_place",
    0x0002CAC6: "goodix_primitives_initialize_status",
    0x00034A66: "goodix_primitives_is_evenly_divisible",
    0x00035F44: "goodix_primitives_truncate_decimal",
    0x00036718: "goodix_primitives_unsigned_power",
    0x00036EB4: "goodix_primitives_bit_reverse_permute_pairs",
    0x00037A84: "goodix_primitives_nadt_peak_dispersion_quality",
    0x0003E6C8: "goodix_primitives_nadt_gaussian_interval_probability",
    0x0003DE20: "goodix_primitives_hr_mad_inlier_mask",
    0x00037F54: "goodix_primitives_spo2_expand_packed_banks",
    0x000372B0: "goodix_primitives_spo2_decimal_residual",
    0x00041F4C: "goodix_primitives_spo2_rolling_percentile_select",
    0x00066B30: "goodix_primitives_nadt_symmetric_fir_i32",
    0x0006671C: "goodix_primitives_spo2_biquad_cascade_process",
    0x00075E1C: "goodix_primitives_fft_real_magnitude_256",
    0x000765E4: "goodix_primitives_fft_magnitude_prepare",
    0x000768B8: "goodix_primitives_fft_complex_128_dif",
    0x00037710: "goodix_primitives_float_buffer_full",
    0x00037720: "goodix_primitives_float_buffer_get",
    0x00037B68: "goodix_primitives_centered_i8",
    0x00037DB4: "goodix_primitives_finalize_warmup_average",
    0x00038030: "goodix_primitives_float_sum",
    0x00056828: "goodix_primitives_decrement_counter",
    0x0005D5D0: "goodix_primitives_tensor_descriptor_initialize",
    0x00061EF2: "goodix_primitives_filter_code",
    0x00061FB4: "goodix_primitives_float_sum",
    0x00066394: "goodix_primitives_word_window_last",
    0x00066490: "goodix_primitives_word_window_count",
    0x00066890: "goodix_primitives_store_version_qualifier",
    0x000668A4: "goodix_primitives_normalize_by_max",
    0x00095750: "goodix_primitives_nadt_clip_normalize",
    0x00028CF4: "goodix_primitives_spo2_smoothed_scale",
    0x00032788: "goodix_primitives_nadt_default_initialize",
    0x0006E574: "goodix_primitives_nadt_context_reset",
    0x0006E664: "goodix_primitives_nadt_context_initialize",
    0x00066C18: "goodix_primitives_percentile_lookup",
    0x0006DAA4: "goodix_primitives_copy_process_version_v1_1",
    0x0006E548: "goodix_primitives_copy_process_version_v1_0",
    0x00085CA4: "goodix_primitives_reverse_low_bits",
    0x00087A78: "goodix_primitives_float_mean",
    0x000928E0: "goodix_primitives_sum_squares",
    0x00092900: "goodix_primitives_dot_product",
    0x00028E5C: "goodix_primitives_transformed_differs",
    0x00029090: "goodix_primitives_copy_indexed_record",
    0x000290DC: "goodix_primitives_round_nearest",
    0x0002A168: "goodix_primitives_transform_packed24_lsb",
    0x0002A1CC: "goodix_primitives_visit_packed24",
    0x0002ADD0: "goodix_primitives_swap_u16_bytes",
    0x00029AA0: "goodix_primitives_mask_columns_any",
    0x0002F260: "goodix_primitives_counted_word_history_push",
    0x00030090: "goodix_primitives_running_triplet_update",
    0x00036394: "goodix_primitives_i16_sample_standard_deviation",
    0x00036282: "goodix_primitives_update_transition",
    0x00035812: "goodix_primitives_insertion_sort_floats",
    0x000368D0: "goodix_primitives_replace_far_from_median",
    0x0003F740: "goodix_primitives_spo2_expand_packed_triplicate",
    0x00070B60: "goodix_primitives_hr_count_mean_outliers",
    0x0006D424: "goodix_primitives_build_hr_version",
    0x0006F838: "goodix_primitives_three_stage_u8_pipeline",
    0x00036EFC: "goodix_primitives_top_descending_strided",
    0x00098E4C: "goodix_primitives_i16_local_extrema_indices",
    0x00028DDA: "goodix_primitives_f32_bits_to_packed_6_9",
    0x00034490: "goodix_primitives_grouped_row_weighted_sums",
    0x0003773C: "goodix_primitives_sample_cardinal_spline",
    0x00037DEC: "goodix_primitives_hr_rebalance_record_pair",
    0x00048018: "goodix_primitives_cardinal_spline_point",
    0x000481A4: "goodix_primitives_align_event_pairs",
    0x000663B4: "goodix_primitives_u8_population_standard_deviation",
    0x000377D8: "goodix_primitives_positive_cosine_similarity",
    0x00087618: "goodix_primitives_collect_extrema_indices",
    0x00030E1C: "goodix_primitives_copy_fresh_gated_triplet",
    0x000419C8: "goodix_primitives_accumulate_threshold_crossings",
    0x00031774: "goodix_primitives_strict_local_peak_max",
    0x000299EC: "goodix_primitives_merge_six_float_state",
    0x00072FB8: "goodix_primitives_zero_masked_sign_runs",
    0x0005CED4: "goodix_primitives_running_i32_statistics_update",
    0x00028B18: "goodix_primitives_second_order_difference_output",
    0x000373A4: "goodix_primitives_nadt_optical_sample_transform",
    0x000367C4: "goodix_primitives_spo2_dispatch_logistic_score",
    0x00030368: "goodix_primitives_hr_weighted_feature_update",
    0x00037588: "goodix_primitives_hr_interpolate_periodic_sample",
    0x00072C48: "goodix_primitives_hr_secondary_context_initialize",
    0x0006D204: "goodix_primitives_hr_primary_context_create",
    0x000766AC: "goodix_primitives_nadt_spectral_peak_prepare",
    0x000708F8: "goodix_primitives_spo2_normalized_spectra_prepare",
    0x00037890: "goodix_primitives_nadt_generated_graph_execute",
    0x00034194: "goodix_primitives_nadt_generated_subgraph_execute",
    0x00036F88: "goodix_primitives_nadt_output_state_select",
    0x00037B80: "goodix_primitives_nadt_auxiliary_state_classify",
    0x00095828: "goodix_primitives_nadt_signal_confidence_update",
    0x00088E80: "goodix_primitives_nadt_channel_quality_update",
    0x00036034: "goodix_primitives_nadt_sample_prepare",
    0x00086BAC: "goodix_primitives_hr_candidate_window_select",
    0x000968C4: "goodix_primitives_nadt_inference_bridge",
    0x00030B6C: "goodix_primitives_nadt_window_filter_i32",
    0x00042BD0: "goodix_primitives_nadt_periodic_peak_rate",
    0x0002FF10: "goodix_primitives_spo2_spectral_peak_concentration_db",
    0x00029AD8: "goodix_primitives_spo2_report_state_update",
    0x00034B54: "goodix_primitives_spo2_packed_channel_standard_deviations",
    0x00061DA4: "goodix_primitives_spo2_channel_records_assemble",
    0x000335B4: "goodix_primitives_spo2_channel_scale_decode",
    0x00034B08: "goodix_primitives_command_status_poll",
    0x0003E6B0: "goodix_primitives_algorithm_context_destroy",
    0x00029BBC: "goodix_primitives_record_family_teardown",
    0x000567C4: "goodix_primitives_float_median",
    0x00028AD4: "goodix_primitives_dispatch_indexed_operation",
    0x0002907C: "goodix_primitives_nadt_graph_execute_veneer",
    0x000290BC: "goodix_primitives_nadt_summary_dispatch",
    0x00029144: "goodix_primitives_nadt_dual_window_features_extract",
    0x0003F89C: "goodix_primitives_nadt_sample_statistics",
    0x00035772: "goodix_primitives_float_transform_prefix_copy",
    0x00030CD8: "goodix_primitives_float_quantile_interpolated",
    0x0007309C: "goodix_primitives_nadt_quartile_mask",
    0x00030970: "goodix_primitives_nadt_nonuniform_mask_count",
    0x0002F2F8: "goodix_primitives_nadt_positive_difference_statistics",
    0x0007311E: "goodix_primitives_nadt_difference_summary_execute",
    0x00036DD4: "goodix_primitives_nadt_rolling_feature_update",
    0x0002FEE2: "goodix_primitives_nadt_feature_pair_update",
    0x0002F660: "goodix_primitives_nadt_channel_ratio_update",
    0x00061C48: "goodix_primitives_nadt_vector_geometry_update",
    0x000357CE: "goodix_primitives_nadt_accumulation_execute",
    0x00072DCC: "goodix_primitives_nadt_batch_accumulate",
    0x00076A68: "goodix_primitives_nadt_record_encode",
    0x00036974: "goodix_primitives_nadt_output_record_build",
    0x00044A78: "goodix_primitives_nadt_output_record_quality_update",
    0x00077D2C: "goodix_primitives_nadt_channel_analysis_execute",
    0x00030178: "goodix_primitives_nadt_extrema_neighborhood_mask",
    0x00076B78: "goodix_primitives_nadt_peak_mask_columns",
    0x00047FA8: "goodix_primitives_nadt_peak_index_collect",
    0x0003441C: "goodix_primitives_nadt_peak_histories_update",
    0x00030114: "goodix_primitives_nadt_primary_ratio_peak_update",
    0x00066900: "goodix_primitives_nadt_local_maximum_prefix_counts",
    0x00036734: "goodix_primitives_nadt_local_peak_indices",
    0x00092A04: "goodix_primitives_centered_cross_correlation",
    0x000666A4: "goodix_primitives_nadt_normalized_autocorrelation",
    0x00091870: "goodix_primitives_nadt_sample_summary_build",
    0x0002A65C: "goodix_primitives_send_fixed_aa_pair",
    0x0003497C: "goodix_primitives_peak_quality_update",
    0x00031624: "goodix_primitives_i16_autocorrelation_transform",
    0x00035F70: "goodix_primitives_i32_autocorrelation_transform",
    0x0002E8CC: "goodix_primitives_reset_register_fields",
    0x0005CEA8: "goodix_primitives_dispatch_word_copy",
    0x0005CDF8: "goodix_primitives_timed_dispatch_scaled_output",
    0x00035084: "goodix_primitives_round_float_half_away_from_zero",
    0x0006CC60: "goodix_primitives_processing_context_destroy",
    0x0006CCC0: "goodix_primitives_spo2_input_diagnostics_emit",
    0x00036B58: "quantized_runtime_goodix_in_place_float_to_int8",
    0x00095B04: "quantized_runtime_goodix_configured_in_place_float_to_int8",
    0x0006E788: "goodix_primitives_build_nadt_version",
    0x0002F7DC: "quantized_runtime_goodix_nadt_projection_execute",
    0x00029394: "goodix_primitives_normalize_rows_by_range",
    0x0004FDB8: "goodix_primitives_record32_history_push",
    0x00066AB2: "goodix_primitives_select_mask_row",
    0x00032744: "goodix_primitives_channel_scale_copy",
    0x000357A2: "goodix_primitives_i32_range",
    0x000361D8: "goodix_primitives_i32_squared_deviation_sum",
    0x0003623C: "goodix_primitives_indexed_i16_trimmed_mean",
    0x00036BD4: "goodix_primitives_processing_record_initialize",
    0x0002F65C: "goodix_primitives_clear_mode_buffers",
    0x00036BFA: "goodix_primitives_clear_mode_buffers",
    0x00036C32: "goodix_primitives_update_transition",
    0x0003754A: "goodix_primitives_sort_floats",
    0x00037574: "goodix_primitives_sort_floats",
    0x0004304C: "goodix_primitives_sorted_insert",
    0x00043860: "goodix_primitives_i16_descriptor_mean",
    0x0005144C: "goodix_primitives_i32_mean",
    0x0009775C: "goodix_primitives_reverse_clamped_weighted_sum",
    0x00097984: "goodix_primitives_extrema_history_update",
    0x00043B30: "goodix_primitives_update_elapsed_slot",
    0x00099010: "goodix_primitives_update_elapsed_slot",
    0x00061F94: "goodix_primitives_float_mean_or_zero",
    0x00061F04: "goodix_primitives_strided_sample_standard_deviation",
    0x00066430: "goodix_primitives_float_buffer_incremental_standard_deviation",
    0x000662DA: "goodix_primitives_word_window_full",
    0x00066458: "goodix_primitives_i16_mean",
    0x00066470: "goodix_primitives_float_window_mean",
    0x00066494: "goodix_primitives_float_window_remove",
    0x0006652A: "goodix_primitives_i16_window_push",
    0x00066560: "goodix_primitives_byte_window_push",
    0x000665A0: "goodix_primitives_decimated_i16_window_push",
    0x00066608: "goodix_primitives_decimated_float_window_push",
    0x000668DC: "goodix_primitives_i16_min_index",
    0x00092988: "goodix_primitives_float_min_index",
    0x000929D6: "goodix_primitives_float_max_index",
    0x00092B68: "goodix_primitives_float_mean_or_zero",
    0x00028EAC: "goodix_primitives_release_and_clear",
    0x00036230: "goodix_primitives_release_if_present",
    0x0003757C: "goodix_primitives_release_if_present",
    0x00034A3C: "goodix_primitives_allocate_record_pair",
    0x00036C60: "goodix_primitives_release_context_pair",
    0x000662EA: "goodix_primitives_buffer_descriptor_initialize",
    0x00066304: "goodix_primitives_buffer_descriptor_initialize",
    0x0006631E: "goodix_primitives_extended_descriptor_initialize",
    0x0006633A: "goodix_primitives_extended_descriptor_initialize",
    0x0006635C: "goodix_primitives_float_descriptor_initialize",
    0x00028EC0: "goodix_primitives_release_context_pair",
    0x00056860: "goodix_primitives_release_and_clear",
    0x00066276: "goodix_primitives_release_and_clear",
    0x0006628A: "goodix_primitives_release_and_clear",
    0x0006629E: "goodix_primitives_release_and_clear",
    0x000662B2: "goodix_primitives_release_and_clear",
    0x000662C6: "goodix_primitives_release_and_clear",
    0x000667C0: "goodix_primitives_release_if_present",
    0x00073154: "goodix_primitives_release_two_and_clear",
    0x00092B58: "goodix_primitives_byte_fill",
    0x00092B60: "goodix_primitives_byte_fill",
    0x00098FFC: "goodix_primitives_release_two",
    0x0005683C: "goodix_primitives_dual_buffer_descriptor_initialize",
    0x00056874: "goodix_primitives_float_storage_initialize",
    0x000667C6: "goodix_primitives_pair_buffer_initialize",
    0x00093E3A: "goodix_primitives_release_two_and_clear",
    0x0003DF18: "goodix_primitives_channel_state_initialize",
    0x000304A0: "goodix_primitives_channel_state_release",
    0x0005CD90: "goodix_primitives_session_state_initialize",
    0x00091890: "goodix_primitives_session_state_release",
    0x000362B6: "goodix_primitives_owned_float_record_create",
    0x00033800: "goodix_primitives_owned_float_record_destroy",
    0x00034AA0: "goodix_primitives_channel_record_array_create",
    0x000305D8: "goodix_primitives_channel_record_array_destroy",
    0x00031914: "goodix_primitives_dual_i16_storage_initialize",
    0x0003727C: "goodix_primitives_session_aggregate_create",
    0x00037E8A: "goodix_primitives_session_aggregate_destroy",
    0x0002F624: "quantized_runtime_goodix_model_owner_initialize",
    0x00030800: "quantized_runtime_goodix_layer_block_build",
    0x0002951A: "quantized_runtime_goodix_five_stage_32_execute",
    0x0006EB30: "goodix_primitives_outer_session_destroy",
    0x0006EB94: "goodix_primitives_outer_session_create",
    0x00066840: "goodix_primitives_copy_dsp_version",
    0x0006EC90: "goodix_primitives_build_spo2_version",
    0x00036C26: "quantized_runtime_goodix_model_instance_create",
    0x00036408: "quantized_runtime_recurrent_range_adjust",
    0x00036590: "quantized_runtime_recurrent_range_adjust",
    0x000617F8: "quantized_runtime_goodix_second_executor_execute",
    0x00035D6E: "quantized_runtime_goodix_five_stage_27_execute",
    0x0003F7F8: "quantized_runtime_goodix_f32_three_stage_execute",
    0x00042024: "quantized_runtime_goodix_u8_three_stage_execute",
    0x0004387C: "quantized_runtime_goodix_graph_build",
    0x0005D01C: "quantized_runtime_goodix_second_graph_build",
    0x0006FDE0: "quantized_runtime_recurrent_zero_point",
    0x000739A8: "quantized_runtime_recurrent_execute",
    0x0007400C: "quantized_runtime_float_min_max",
    0x0007405C: "quantized_runtime_u8_matrix_vector",
    0x0007412C: "goodix_primitives_quartic_evaluate",
    0x00074190: "goodix_primitives_peak_select",
    0x0005A5EC: "goodix_primitives_integrity_encode",
    0x000759F4: "goodix_primitives_integrity_invalid",
    0x00028E14: "goodix_primitives_integrity_invalid",
    0x00028E70: "goodix_primitives_integrity_encode",
    0x000294BC: "goodix_primitives_integrity_encode",
    0x00028DE0: "goodix_primitives_packed_5_10_to_f32_bits",
    0x00028DE6: "goodix_primitives_packed_6_9_to_f32_bits",
    0x00028DEC: "goodix_primitives_u32_to_u16_transform",
    0x000742E4: "quantized_runtime_goodix_executor_execute",
    0x0003007E: "quantized_runtime_goodix_executor_execute",
    0x00038050: "quantized_runtime_goodix_executor_execute",
    0x000417F0: "quantized_runtime_goodix_executor_execute",
    0x00085DC4: "quantized_runtime_i8_conv1d_execute",
    0x000876C8: "quantized_runtime_goodix_layer_execute",
    0x00074A20: "quantized_runtime_recurrent_layer_descriptor_construct",
    0x00074AA4: "goodix_primitives_release_context_pair_vector",
    0x00074B44: "quantized_runtime_aligned_descriptor_construct",
    0x00074C6C: "quantized_runtime_packed_pool_descriptor_initialize",
    0x00074C90: "quantized_runtime_executor_vector_30534",
    0x00074CB4: "quantized_runtime_cursor_pair_add_descriptor_construct",
}

APP_GOODIX_HEAP_RECONSTRUCTED_SYMBOLS = {
    0x0002D460: "goodix_heap_free",
    0x0002D54C: "goodix_heap_zero_allocate",
    0x0002D5C0: "goodix_heap_reallocate",
    0x00042D1C: "goodix_heap_control",
    0x0006DFC8: "goodix_heap_free",
    0x0006DFCC: "goodix_heap_available_bytes",
    0x0006DFD6: "goodix_heap_initialize",
    0x0006E004: "goodix_heap_zero_allocate",
    0x00076A44: "goodix_heap_unlink_free_block",
    0x00093E14: "goodix_heap_size_to_bin",
    0x00093E5E: "goodix_heap_insert_free_block",
    0x000982C2: "goodix_heap_allocate_core",
}

APP_GOMORE_PRIMITIVES_RECONSTRUCTED_SYMBOLS = {
    0x000948D8: "gomore_primitives_shift_negated_filter_history",
    0x000823D8: "gomore_primitives_log_u32",
    0x00060990: "gomore_primitives_accelerometer_resample25",
    0x00090F44: "gomore_primitives_sleep_engine_open",
    0x0005D560: "gomore_primitives_csv4_prefix_compare",
    0x00091E02: "quantized_runtime_tensor_slice",
    0x00065538: "gomore_tensor_dual_affine_activate",
    0x000655A8: "gomore_tensor_gated_dual_affine_activate",
    0x00096E0C: "gomore_primitives_sequence_replay",
    0x000649BC: "gomore_primitives_interval_nonzero_argmax",
    0x00080F88: "gomore_primitives_round_decimal_places",
    0x00071CD8: "gomore_primitives_time_engine_initialize",
    0x00058256: "gomore_primitives_circular_signal_predicate",
    0x00069FA8: "gomore_primitives_average_sign_crossing_spacing",
    0x00070AF8: "gomore_primitives_dominant_sorted_i32",
    0x00057C44: "gomore_primitives_validate_key_and_update_status",
    0x00057C84: "gomore_primitives_decimal_config_update",
    0x000967C8: "gomore_primitives_runtime_version_validate",
    0x0009196E: "gomore_tensor_add",
    0x0006562C: "gomore_tensor_blend",
    0x000656AA: "gomore_tensor_int8_float_affine",
    0x00035D12: "gomore_tensor_strided_copy_2d",
    0x0007D09C: "gomore_primitives_one_minus",
    0x0008F49C: "gomore_primitives_logistic",
    0x000304D8: "gomore_primitives_scaled_product",
    0x00056920: "gomore_primitives_linear_sign_classify",
    0x0004B698: "gomore_primitives_register_mode_topics",
    0x00061720: "gomore_primitives_exponential_affine",
    0x00065028: "gomore_primitives_seed_and_test_text_class",
    0x00065050: "gomore_primitives_validate_record_bytes",
    0x00065070: "gomore_primitives_validate_su_signature",
    0x00071100: "gomore_primitives_sps_engine_initialize",
    0x0008EC7C: "gomore_primitives_state_mode_dispatch",
    0x0008ED10: "gomore_primitives_commit_valid_time_record_adapter",
    0x000641F0: "gomore_primitives_iir_filter_apply",
    0x00076120: "gomore_primitives_thresholded_mean5",
    0x0008F688: "gomore_primitives_magnitude_score10",
    0x000569BC: "gomore_primitives_circular_count_predicate",
    0x0008F728: "gomore_primitives_run_length_encode_2bit",
    0x0007266A: "gomore_primitives_propagate_packed_status",
    0x00071C38: "gomore_primitives_filter_bank_initialize",
    0x00069546: "gomore_primitives_target_runs",
    0x000748D4: "gomore_primitives_shift_marked_history",
    0x00071D62: "gomore_primitives_mode_state_configure",
    0x00071DD8: "gomore_primitives_large_filter_state_initialize",
    0x00071DB6: "gomore_primitives_engine_state_initialize",
    0x0008245C: "gomore_primitives_resample25_and_filter",
    0x0008247E: "gomore_primitives_resample25_and_filter_tail",
    0x00058AB8: "gomore_primitives_prepare_filter_input",
    0x0007260C: "gomore_primitives_commit_valid_time_record",
    0x00077E48: "gomore_primitives_signed_power_third",
    0x00088264: "gomore_primitives_trim_below_reference_tail",
    0x00080FF4: "gomore_primitives_selector_transition",
    0x00064174: "gomore_primitives_fill_packed_time_gap",
    0x00074880: "gomore_primitives_centered_ratio",
    0x0006AAC0: "gomore_primitives_seeded_random_offset",
    0x00028B8A: "gomore_primitives_allocate_mode2_state",
    0x00048D22: "gomore_primitives_allocate_mode1_state",
    0x0004FB44: "gomore_primitives_decimal_parse",
    0x000651A4: "gomore_primitives_tensor_call_optional_finish",
    0x000295DE: "gomore_primitives_all_class_0x20",
    0x0002960C: "gomore_primitives_all_class_0x20",
    0x00071CA0: "gomore_primitives_filter_state_initialize",
    0x000908AC: "gomore_primitives_quality_samples_copy",
    0x00068F8C: "gomore_primitives_dual_stage",
    0x00071B42: "gomore_primitives_composite_record_initialize",
    0x0005A40E: "gomore_primitives_quality_code",
    0x000723B6: "gomore_primitives_i16_standard_deviation",
    0x00069D20: "gomore_primitives_energy_core",
    0x00069D80: "gomore_primitives_energy_scaled",
    0x00069F3C: "gomore_primitives_state_word_24",
    0x00090EFC: "gomore_primitives_split_signed_root",
    0x000676E0: "gomore_primitives_clamped_rational",
    0x000684B4: "gomore_primitives_table_record11",
    0x0005D31E: "gomore_primitives_status_or_random",
    0x00056C2A: "gomore_primitives_vector_pair_transform",
    0x00059D70: "gomore_primitives_encode_short_record",
    0x0007D0A8: "gomore_primitives_accumulate_i8x4_milli",
    0x00048960: "gomore_primitives_shift_presence_history",
    0x000641C4: "gomore_primitives_fill_float_progression",
    0x00072420: "gomore_primitives_time_record_valid",
    0x0004EC6C: "gomore_primitives_float_argmax_range",
    0x0004ECE0: "gomore_primitives_float_argmax_above_floor",
    0x000568F0: "gomore_primitives_i16_range",
    0x0008ED2C: "gomore_primitives_packed_2bit_set",
    0x000568AC: "gomore_primitives_rational_transform",
    0x0008F4B4: "gomore_primitives_i16_mean_absolute_difference",
    0x0004B560: "gomore_primitives_u16_all_within_300",
    0x00056980: "gomore_primitives_nonzero_i16_mean8",
    0x00067750: "gomore_primitives_circular_u8_dot18",
    0x00077162: "gomore_primitives_filtered_u8_mean",
    0x00058C40: "gomore_primitives_complex_multiply",
    0x0007EAF6: "gomore_primitives_count_hysteresis_crossings",
    0x00058CE8: "gomore_primitives_nullable_compare_n",
    0x00072AF0: "gomore_primitives_recent_interval_predicate",
    0x00093DCC: "gomore_primitives_record_quality_classify",
    0x00033330: "gomore_primitives_low24_binding_initialize",
    0x00074C48: "gomore_primitives_pack4_binding_initialize",
    0x000722EC: "gomore_primitives_i16_mean",
    0x000883FC: "gomore_primitives_float_floor_update",
    0x00057C20: "gomore_primitives_validate_selector",
    0x00058D26: "gomore_primitives_nullable_compare",
    0x0005CBC0: "gomore_primitives_compact_u32_stride",
    0x00069F80: "gomore_primitives_status_record_extract",
    0x00071594: "gomore_primitives_half_span_initialize",
    0x00071D3E: "gomore_primitives_parameter_state_initialize",
    0x000967A0: "gomore_primitives_count_encoded_i32",
    0x0007316C: "gomore_primitives_scaled_ratio",
    0x0004AA98: "gomore_primitives_piecewise_clamp_70_100",
    0x00058480: "gomore_primitives_missing_window_initialize",
    0x0006951E: "gomore_primitives_modulo_value_get",
    0x000710D4: "gomore_primitives_mode8_state_initialize",
    0x00064B06: "gomore_primitives_find_next_nonnegative_i16",
    0x000484CA: "gomore_primitives_shift_two_u8_windows5",
    0x00068238: "gomore_primitives_normalized_position",
    0x00069500: "gomore_primitives_packed_2bit_get",
    0x00090E68: "gomore_primitives_energy_state_reset",
    0x000720CE: "gomore_primitives_large_default_state_initialize",
    0x000764DC: "gomore_primitives_scale_milli",
    0x000883B0: "gomore_primitives_sps_state_reset",
    0x00094250: "gomore_primitives_shift_status_windows",
    0x000327E4: "gomore_primitives_count_byte_plus_one",
    0x000484A8: "gomore_primitives_accumulate_pair",
    0x0005D2EC: "gomore_primitives_selected_state_reset",
    0x00071188: "gomore_primitives_pattern17_initialize",
    0x000715D4: "gomore_primitives_energy_record_initialize",
    0x000715F8: "gomore_primitives_large_state_initialize",
    0x00091080: "gomore_primitives_noop_91080",
    0x0006476C: "gomore_primitives_set_second_word",
    0x00072ACE: "gomore_primitives_return_zero",
    0x00071B24: "gomore_primitives_clear_72",
    0x000720C8: "gomore_primitives_store_first_word",
    0x0007170A: "gomore_primitives_clear_first_byte",
    0x00071D96: "gomore_primitives_clear_first_byte",
    0x000711AA: "gomore_primitives_triplet_initialize",
    0x0002F614: "gomore_primitives_interpolate",
    0x0004AAC0: "gomore_primitives_byte_in_70_100",
    0x0005D360: "gomore_primitives_clear_flag_1000",
    0x00067470: "gomore_primitives_cubic_scale",
    0x0006773C: "gomore_primitives_linear_evaluate",
    0x000484E8: "gomore_primitives_shift_u8_window5",
    0x0008F674: "gomore_primitives_nullable_strlen",
    0x0004B598: "gomore_primitives_u16_in_30000_50000",
    0x00071154: "gomore_primitives_clear_36",
    0x00071D9E: "gomore_primitives_step_record_initialize",
    0x00058464: "gomore_primitives_clear_124",
    0x0007116C: "gomore_primitives_float_state_initialize",
    0x00070758: "gomore_primitives_half_to_float_bits",
    0x00071A10: "gomore_primitives_store_half_as_float_bits",
    0x0006AD04: "gomore_primitives_records_all_clear",
    0x000715B8: "gomore_primitives_record5_initialize",
    0x000883D4: "gomore_primitives_clear_two_records",
    0x00071B2A: "gomore_primitives_fill_missing_pair",
    0x00068FBC: "gomore_primitives_prepare_and_score",
    0x00072AD4: "gomore_primitives_float_in_encoded_range",
    0x000928DA: "gomore_primitives_scale",
    0x00094A4C: "gomore_primitives_callback_record_initialize",
    0x00071A20: "gomore_primitives_span_initialize",
    0x00087600: "gomore_primitives_sort_float_subrange",
    0x00091A56: "gomore_primitives_max_index",
    0x00068720: "gomore_primitives_size_736",
    0x0006841A: "gomore_primitives_size_14816",
    0x00071704: "gomore_primitives_clear_90",
    0x00064770: "gomore_primitives_set_second_word",
    0x0005A442: "gomore_primitives_return_zero",
    0x00076500: "gomore_primitives_noop_76500",
    0x000578C8: "gomore_primitives_noop_578c8",
    0x00049E58: "gomore_primitives_noop_49e58",
    0x00072B34: "gomore_primitives_state_window_predicate",
    0x0006AB88: "gomore_primitives_key_or_cached_copy",
    0x0008ECD8: "gomore_primitives_slot_state_transition",
    0x0006AD28: "gomore_primitives_copy_key_blob",
    0x000726C4: "gomore_primitives_stage_32_and_consume",
    0x00062000: "gomore_primitives_mean",
    0x000760EC: "gomore_primitives_argmax_from_zero",
    0x0004C37C: "gomore_primitives_reset_provider_state",
    0x0006C640: "gomore_primitives_sample_plausible",
    0x0006ACD8: "gomore_primitives_stamp_time_record",
    0x00068570: "gomore_primitives_clamp_hysteresis",
    0x000726FA: "gomore_primitives_parameter_commit",
    0x0006AB60: "gomore_primitives_records_any_bit2",
    0x0006AB38: "gomore_primitives_records_any_bit4",
    0x0006AB10: "gomore_primitives_records_any_bit3",
    0x0006AAE8: "gomore_primitives_records_any_bit1",
    0x0004EC9C: "gomore_primitives_quantized_argmin",
    0x00064774: "gomore_primitives_max_difference_index",
    0x00062034: "gomore_primitives_median",
    0x0006208C: "gomore_primitives_standard_deviation",
    0x000728D4: "gomore_primitives_logistic_score",
    0x00094938: "gomore_primitives_modulo5_record",
    0x0008EEBA: "gomore_primitives_compact_25_windows",
    0x00094300: "gomore_primitives_decimated_ring_write",
    0x00091A0E: "gomore_tensor_map",
    0x00091C80: "gomore_tensor_multiply",
    0x00091CCC: "gomore_tensor_leaky_relu",
    0x00091EDC: "gomore_tensor_softmax",
    0x000919BA: "gomore_tensor_dequant_bias_add",
    0x00091D30: "gomore_tensor_int8_float_dot",
}


# These retain the QST routine skeleton but add R1 identity acceptance,
# configuration values, I2C/delay callbacks, logging, bounds, or event policy.
# Only those bounded product seams may be local, and they remain disabled until
# a licensed provider implementation is available.
APP_QMA6100_ADAPTERS = {
    0x0006F404: "r1_qma6100_probe_wrapper",
    0x0006F418: "r1_qma6100_configuration_wrapper",
    0x0006F436: "r1_qma6100_interrupt_wrapper",
    0x0006F448: "r1_qma6100_fifo_normalize",
    0x00086D40: "r1_qma6100_anymotion_configuration",
    0x00086E48: "r1_qma6100_delay_port",
    0x00086E68: "r1_qma6100_identity_and_layout_adapter",
    0x00086EE4: "r1_qma6100_initialize_configuration",
    0x00086FA8: "r1_qma6100_irq_event_adapter",
    0x00086FF4: "r1_qma6100_bounded_fifo_read",
    0x0008714C: "r1_qma6100_read_transport",
    0x00087250: "r1_qma6100_step_configuration",
    0x000872E4: "r1_qma6100_tap_configuration",
    0x000873F4: "r1_qma6100_write_transport",
}


# Exact function entries covered by the SHA-pinned, read-only GoMore algorithm
# audit. Each cited audit independently verifies the complete code-only range,
# relevant constants, and direct-call topology. This is a conservative provider
# boundary: it proves that these bodies participate in the vendor algorithm
# domain, but does not assert an original private symbol or SDK release.
APP_GOMORE_AUDIT_GROUPS = {
    "energy_pipeline": (
        0x0005F56C, 0x00061274, 0x00068728, 0x0007316C, 0x00067D48, 0x000763D8,
        0x00061720, 0x00068238, 0x0002F108, 0x0002F614, 0x000883FC, 0x00071E34,
        0x0006ABF8, 0x000720C8,
    ),
    "algorithm_domains": (
        0x00060A14, 0x0008247E, 0x00060680, 0x00069834, 0x000948D8, 0x00068840,
        0x00056C54, 0x00056DC0, 0x000647C4, 0x00064380, 0x0004857C, 0x00076120,
        0x000967A0, 0x0005ED14, 0x0005F4B6, 0x00093DCC, 0x0009413C, 0x00057F8C,
        0x00058060, 0x00067A40, 0x00061198, 0x00048960, 0x00071D9E, 0x000710D4,
        0x0004834A, 0x000484FC, 0x00067E4C, 0x00058480, 0x000722EC, 0x000723B6,
        0x000568F0, 0x0008F4B4, 0x00056980, 0x000569BC, 0x00058256, 0x00056A0C,
        0x000583C8, 0x000582C4, 0x0005C5F0, 0x0008F4E8, 0x00074880, 0x00056920,
        0x00056D78, 0x00056CF4, 0x00056F94, 0x0008F3C8, 0x00058AEE, 0x0007EAF6,
        0x000761F8, 0x00071188, 0x00094250, 0x0005A40E, 0x00080FF4, 0x00057C20,
        0x00067B24, 0x00070AF8, 0x00077162, 0x000484E8, 0x000484CA,
    ),
    "gomore_initializer_boundary": tuple(
        int(item["entry"]) for item in GOMORE_INITIALIZER_FUNCTIONS
    ),
    "gomore_output_producers": (
        0x0005FF94, 0x00060680, 0x0005F4B6, 0x0005EF1C, 0x000610C8, 0x0005F56C,
        0x00060B80, 0x00060DC4, 0x00061198, 0x00061274, 0x00071714, 0x00069834,
        0x00067558, 0x000692E4, 0x00058B70, 0x0005C19C, 0x0009413C, 0x00094590,
        0x00059D9C, 0x0005FEB8, 0x000715F8, 0x00096E0C, 0x000721B4, 0x00069F80,
    ),
    "dormant_estimator": (
        0x0005FEB8, 0x000715F8, 0x00096E0C, 0x000721B4, 0x00069F80, 0x0005FF94,
        0x00071714, 0x00059D9C, 0x000908E0, 0x00090A50, 0x00070498, 0x0005D2EC,
        0x00094270, 0x00096634, 0x00094698, 0x0004C6DC, 0x00029382, 0x0002938A,
        0x000676E0, 0x00080F88, 0x00090C54, 0x000888A0, 0x00069D20, 0x00067470,
        0x00069D80, 0x000695A8, 0x000568AC, 0x0006818C, 0x00068420, 0x0006808C,
        0x000675DC, 0x00058C7A, 0x00058C40, 0x00056C2A, 0x00077E48, 0x000908AC,
        0x00090EFC, 0x00068D18, 0x00069DC8, 0x0008141C, 0x00067488, 0x0006825C,
    ),
    "heart_rate_selector": (
        0x000605DC, 0x0007170A, 0x00071714, 0x00094590, 0x0005F3D8, 0x0005FF94,
    ),
    "sps_speed_selector": (
        0x00071714, 0x00094590, 0x0005EF1C, 0x000610C8, 0x000684FC, 0x00068DE0,
        0x00068E5C, 0x00069E94, 0x00069F3C, 0x00071100, 0x00070F44, 0x000883B0,
        0x0006773C, 0x000484A8, 0x00071DB6,
    ),
    "sleep_algorithm": (
        0x00060B80, 0x00060DC4, 0x00067558, 0x000692E4, 0x00058B70, 0x0005C19C,
        0x00088450, 0x000684B4, 0x0008ED2C, 0x00064174, 0x00069644, 0x0008FA3C,
        0x0008F728, 0x00067BBC, 0x0004A704, 0x00068F8C, 0x0006778C, 0x00072AF0,
        0x000748D4, 0x0004B4B0, 0x0004B5B0, 0x0004B698, 0x00081040, 0x0008F0F0,
        0x000881F4, 0x00064CC8, 0x00069546, 0x00088AAC, 0x00074D60, 0x00076502,
        0x00064B06, 0x0007D0A8, 0x0004ECE0, 0x0005F264, 0x0005F3D8, 0x000651A4,
        0x00070758, 0x000711AA, 0x00071594, 0x00071618, 0x00071A10, 0x0009196E,
        0x00090F44, 0x0005D360, 0x00060AF4, 0x0008EE3A, 0x00058AB8, 0x00064A28,
        0x000649BC, 0x0004EC6C, 0x00088264, 0x00059D70, 0x000641F0, 0x000711B4,
        0x00071CA0, 0x00071D62, 0x000882EC, 0x00094590, 0x00060A14, 0x0008247E,
        0x00071C38, 0x0006FEA0, 0x00060990, 0x0008245C, 0x00058464, 0x00071154,
        0x0007116C, 0x000764DC, 0x00074914, 0x0005CBC0, 0x00059E60, 0x0008F688,
        0x00067750, 0x0007D09C, 0x0008F49C,
    ),
    "gomore_neural_runtime": tuple(
        int(item["entry"]) for item in GOMORE_NEURAL_RUNTIME_FUNCTIONS
    ),
    "gomore_sleep_graphs": tuple(
        int(item["entry"]) for item in GOMORE_SLEEP_GRAPH_FUNCTIONS
    ),
    "gomore_activity_state_classifier": tuple(
        int(item["entry"]) for item in GOMORE_ACTIVITY_STATE_FUNCTIONS
    ),
    "gomore_energy_model": tuple(
        int(item["entry"]) for item in GOMORE_ENERGY_MODEL_FUNCTIONS
    ),
    "gomore_iir_designer": tuple(
        int(item["entry"]) for item in GOMORE_IIR_DESIGNER_FUNCTIONS
    ),
    "gomore_auth_parser": tuple(
        int(item["entry"]) for item in GOMORE_AUTH_PARSER_FUNCTIONS
    ),
    "gomore_sleep_stage_statistics": tuple(
        int(item["entry"]) for item in GOMORE_SLEEP_STAGE_STATISTICS_FUNCTIONS
    ),
    "gomore_sensor_update_path": tuple(
        int(item["entry"]) for item in GOMORE_FRONTIER_35X_FUNCTIONS
    ),
    "gomore_frontier_334_342": tuple(
        int(item["entry"]) for item in GOMORE_FRONTIER_334_342_FUNCTIONS
    ),
    "gomore_frontier_314_328": tuple(
        int(item["entry"]) for item in GOMORE_FRONTIER_314_328_FUNCTIONS
    ),
    "gomore_frontier_264_274": tuple(
        int(item["entry"]) for item in GOMORE_FRONTIER_264_274_FUNCTIONS
    ),
    "gomore_frontier_256_262": tuple(
        int(item["entry"]) for item in GOMORE_FRONTIER_256_262_FUNCTIONS
    ),
    "gomore_frontier_230_248": tuple(
        int(item["entry"]) for item in GOMORE_FRONTIER_230_248_FUNCTIONS
    ),
    "gomore_frontier_128_202": tuple(
        int(item["entry"]) for item in GOMORE_FRONTIER_128_202_FUNCTIONS
    ),
    "gomore_frontier_64_127": tuple(
        int(item["entry"]) for item in GOMORE_FRONTIER_64_127_FUNCTIONS
    ),
    "gomore_frontier_32_63": tuple(
        int(item["entry"]) for item in GOMORE_FRONTIER_32_63_FUNCTIONS
    ),
    "gomore_frontier_lt32": tuple(
        int(item["entry"]) for item in GOMORE_FRONTIER_LT32_FUNCTIONS
    ),
    "gomore_frontier_final53": tuple(
        int(item["entry"]) for item in GOMORE_FRONTIER_FINAL53_FUNCTIONS
    ),
}

APP_GOMORE_AUDIT_FUNCTIONS: dict[int, tuple[str, ...]] = {}
for _group, _entries in APP_GOMORE_AUDIT_GROUPS.items():
    for _entry in _entries:
        APP_GOMORE_AUDIT_FUNCTIONS[_entry] = (
            *APP_GOMORE_AUDIT_FUNCTIONS.get(_entry, ()), _group,
        )


# The audit also exposes two complete R1 topic callbacks immediately outside
# the provider algorithm bodies. They perform bounded input conversion and
# readiness bookkeeping before handing data to the GoMore integration path.
# Only this product-owned adapter behavior may be implemented locally, and the
# path remains disabled until a licensed GoMore provider is admitted.
APP_GOMORE_ADAPTERS = {
    0x0005DC08: "r1_gomore_time_transition_adapter",
    0x0006B114: "r1_gomore_acc_topic_adapter",
    0x0006B228: "r1_gomore_raw_hr_topic_adapter",
}


# Goodix's own developer-community trace reproduces these exact embedded
# GH3X2X algorithm/version strings and hashes, including GH_HR
# v2.0.3.0/21d2063d/002271a1, GH_HRV v1.0.1.0/ed953ff3, GH_SPO2
# v2.1.10.0/277e89de/1f1cf98b, GH_NADT v1.0.2.0/548d894d, DSP
# v1.3.0/30234f22, dlCom v1.3.0/c00c91c9, and driver v2.23/7ecd2a.
# The descriptive roles below are boundary labels, not asserted private
# Goodix symbols. Processing wrappers are included because their direct call
# topology consumes the corresponding versioned algorithm interface.
APP_GOODIX_EXACT_CANDIDATES = {
    0x00085DC4: "Goodix signed-int8 grouped 1-D convolution executor",
    **{
        int(item["entry"]): str(item["role"])
        for item in GOODIX_FRONTIER_212_222_FUNCTIONS
    },
    **{
        int(item["entry"]): str(item["role"])
        for item in GOODIX_FRONTIER_280_308_FUNCTIONS
    },
    **{
        int(item["entry"]): str(item["role"])
        for item in GOODIX_FRONTIER_334_342_FUNCTIONS
    },
    **{
        int(item["entry"]): str(item["role"])
        for item in GOODIX_FRONTIER_128_202_FUNCTIONS
    },
    **{
        int(item["entry"]): str(item["role"])
        for item in GOODIX_FRONTIER_64_127_FUNCTIONS
            + GOODIX_FRONTIER_32_63_FUNCTIONS
            + GOODIX_FRONTIER_LT32_FUNCTIONS
            + GOODIX_FRONTIER_FINAL53_FUNCTIONS
    },
    **{
        int(item["entry"]): str(item["role"])
        for item in GOODIX_INTEGRITY_NEW_FUNCTIONS
    },
    **{
        int(item["entry"]): str(item["role"])
        for item in GOODIX_NADT_FUNCTIONS
    },
    **{
        int(item["entry"]): str(item["role"])
        for item in GOODIX_HR_FUNCTIONS
    },
    **{
        int(item["entry"]): str(item["role"])
        for item in GOODIX_HRV_FUNCTIONS
    },
    **{
        int(item["entry"]): str(item["role"])
        for item in GOODIX_CHANNEL_DECODER_FUNCTIONS
    },
    **{
        int(item["entry"]): str(item["role"])
        for item in GOODIX_NADT_QUALITY_FUNCTIONS
    },
    **{
        int(item["entry"]): str(item["role"])
        for item in GOODIX_NADT_PEAK_MASK_FUNCTIONS
    },
    **{
        int(item["entry"]): str(item["role"])
        for item in GOODIX_NADT_ACCUMULATION_FUNCTIONS
    },
    **{
        int(item["entry"]): str(item["role"])
        for item in GOODIX_REGISTER_PROFILE_FUNCTIONS
    },
    **{
        int(item["entry"]): str(item["role"])
        for item in GOODIX_SPO2_DLCOM_FUNCTIONS
    },
    **{
        int(item["entry"]): str(item["role"])
        for item in GOODIX_SPO2_DLCOM_ALL_FUNCTIONS
        if item["inventory"] == "manual_provenance_supplement"
    },
    **{
        int(item["entry"]): str(item["role"])
        for item in GOODIX_HR_INIT_FUNCTIONS
    },
    0x0002A0F4: "algorithm-version dispatcher",
    0x0002A55C: "demo-version getter",
    0x0002A598: "driver-library-version getter",
    0x0002A754: "provider initialization core",
    0x0002AAD0: "provider callback setter",
    0x0002AADC: "provider operation-callback registration",
    0x0002AAF8: "SPI-operation registration",
    0x0002ABFC: "algorithm-enable state setter",
    0x0002AC1C: "provider sampling parameter setter",
    0x0002D824: "enabled-algorithm output dispatcher",
    0x00032788: "NADT output wrapper",
    0x0005A5EC: "GH_HR integrity-bit encoder",
    0x0002E358: "demo start-sampling wrapper",
    0x0002E6A8: "demo stop-sampling wrapper",
    0x0002E778: "demo algorithm-state reset",
    0x0002EDEC: "demo state initializer",
    0x0002EE28: "demo event-state initializer",
    0x0002EE50: "demo multisensor-state initializer",
    0x0002F0F8: "demo output-state initializer",
    0x00066840: "DSP version builder",
    0x00066890: "shared version qualifier",
    0x0006A020: "GH3X2X driver version builder",
    0x0006A4D8: "provider algorithm-output callback dispatcher",
    0x0006A500: "provider configuration-table loader",
    0x0006D424: "heart-rate version builder",
    0x0006D51C: "heart-rate algorithm core",
    0x0006DF14: "HRV output wrapper",
    0x0006DF60: "HRV version builder",
    0x0006E788: "NADT version builder",
    0x0006EC28: "SpO2 output wrapper",
    0x0006EC90: "SpO2 version builder",
    0x000759F4: "GH_HR input integrity validator",
}


# Frozen direct-call-graph closure of the marker/version/demo seeds in the
# contiguous 0x00029F88..0x0002F107 GH3X2X-linked region.  The closure has 149
# nodes: 32 explicit Goodix seeds above, the 116 entries below, and one already
# resolved Nordic nrfx_gpiote_irq_handler.  Twenty-five isolated functions in
# the same address interval are deliberately not swept in.  Generic two/four-
# byte thunks remain candidates rather than being assigned private symbols:
# identical BSim matches against unrelated SDK thunks are not authorship proof.
APP_GOODIX_CLUSTER_CANDIDATES = {
    0x00029F9C, 0x0002A090, 0x0002A168, 0x0002A198, 0x0002A1CC, 0x0002A1F8,
    0x0002A204, 0x0002A214, 0x0002A266, 0x0002A2AC, 0x0002A31C, 0x0002A328,
    0x0002A488, 0x0002A4B4, 0x0002A508, 0x0002A540, 0x0002A550, 0x0002A5C4,
    0x0002A5D0, 0x0002A5EC, 0x0002A604, 0x0002A658, 0x0002A65A, 0x0002A7F4,
    0x0002A810, 0x0002A814, 0x0002A84C, 0x0002A86C, 0x0002A8DC, 0x0002A968,
    0x0002A99E, 0x0002A9D2, 0x0002A9D4, 0x0002A9EC, 0x0002AA10, 0x0002AA74,
    0x0002AA98, 0x0002ABA4, 0x0002ABDC, 0x0002AC10, 0x0002AC30, 0x0002AC40,
    0x0002AC4C, 0x0002AC8C, 0x0002ACCC, 0x0002AD14, 0x0002AD18, 0x0002AD7C,
    0x0002ADB0, 0x0002AE04, 0x0002AE06, 0x0002AE08, 0x0002AE28, 0x0002AF84,
    0x0002B010, 0x0002B0B8, 0x0002B0DC, 0x0002B148, 0x0002B180, 0x0002B218,
    0x0002B4C4, 0x0002B4D8, 0x0002B4F8, 0x0002B524, 0x0002B6A4, 0x0002B8EC,
    0x0002B91C, 0x0002B998, 0x0002BD84, 0x0002BE24, 0x0002BFAA, 0x0002C148,
    0x0002C178, 0x0002C248, 0x0002C27C, 0x0002C2A4, 0x0002C43C, 0x0002C4C0,
    0x0002C4E4, 0x0002C4FC, 0x0002C640, 0x0002C694, 0x0002C930, 0x0002C944,
    0x0002CAA4, 0x0002CAD8, 0x0002CC94, 0x0002CCC0, 0x0002CCD0, 0x0002CCF4,
    0x0002CDD4, 0x0002CFE8, 0x0002D184, 0x0002D324, 0x0002D33C, 0x0002D348,
    0x0002D354, 0x0002D3A8, 0x0002D658, 0x0002D66C, 0x0002E340, 0x0002E734,
    0x0002E746, 0x0002E7A4, 0x0002E8CC, 0x0002E8E8, 0x0002E950, 0x0002EB0C,
    0x0002EB4E, 0x0002EB80, 0x0002ED98, 0x0002EDAA, 0x0002EDE0, 0x0002EDFC,
    0x0002EE38, 0x0002EE44,
}
APP_GOODIX_RESOLVED_THUNKS = {
    int(item["entry"]): str(item["symbol"])
    for item in RESOLVED_THUNKS
    if item["provider"] == "goodix_gh3x2x_candidate"
}


# R1 power, transport, lifecycle, profile-routing, and command glue around the
# proprietary Goodix provider.  These bodies call the GH3X2X demo/library
# boundary but do not implement its biometric algorithms.  The clean-room
# openR1 adapter preserves the observed call ordering and mask values while
# failing closed when a licensed provider is not bound.
APP_GOODIX_ADAPTERS = {
    0x0005036C: "r1_goodix_transport_release",
    0x00050372: "r1_goodix_transport_prepare",
    0x00050870: "r1_goodix_stop_stock_profiles",
    0x00050892: "r1_goodix_start_profile_4000",
    0x000508B6: "r1_goodix_start_profile_2000",
    0x000508DA: "r1_goodix_identity_probe",
    0x00050904: "r1_goodix_switch_profile",
    0x000509A4: "r1_goodix_board_line_release",
    0x000509B0: "r1_goodix_board_line_prepare",
    0x000509E0: "r1_goodix_initialize_probe",
    0x00050AB0: "r1_goodix_secondary_line_release",
    0x00050AE0: "r1_goodix_power_enable",
    0x00050AF0: "r1_goodix_power_disable",
    0x00050BE0: "r1_goodix_reference_counted_release",
    0x0006249C: "r1_goodix_profile_2_command_adapter",
    0x000624C8: "r1_goodix_profile_40_command_adapter",
}
APP_GOODIX_ADAPTERS.update({
    int(item["entry"]): str(item["symbol"])
    for item in RESOLVED_THUNKS
    if item["provider"] == "r1_goodix_provider_adapter"
})
APP_GOODIX_ADAPTERS.update({
    int(item["entry"]): str(item["symbol"])
    for item in R1_FRONTIER_256_262_GOODIX_ADAPTER_FUNCTIONS
})
APP_GOODIX_ADAPTERS.update({
    0x0002E734: "r1_goodix_sampling_mode_glue",
    0x0003DDF4: "r1_goodix_gomore_ops_cross_wiring",
    0x0006A4D8: "r1_goodix_frame_data_hook",
    0x0006F920: "r1_goodix_gsensor_cache_sample",
    0x0006F964: "r1_goodix_gsensor_cache_commit",
    0x0006F9D4: "r1_goodix_gsensor_cache_query",
})


# Goodix GH3X2X demo-kernel/driver bodies with function-level identity proven
# against the pinned public Goodix-licensed SDK copy
# (third-party component `goodix-gh3x2x-democode`, commit 2c0034a2, Goodix
# 5-clause license; clause 4 satisfied because the R1 ring contains the GH3x2x
# IC).  Evidence per entry: control-flow + constants + log-string topology, per
# docs/boundaries/goodix_gh3x2x_candidate-ATTRIBUTION-2026-08.md and the
# per-entry mapping docs/boundaries/GOODIX-DEMO-DRIVER-MAPPING-2026-08.md.
APP_GOODIX_PUBLIC_DEMOCODE = {
    0x00029F9C: "Gh3x2xDemoStopAlgoInner",
    0x0002A090: "GH3X2X_AlgoMemConfig",
    0x0002A0F4: "GH3X2X_AlgoVersion",
    0x0002A198: "GH3X2X_CheckChipModel",
    0x0002A1F8: "GH3X2X_ClearDivZeroFlag",
    0x0002A204: "GH3X2X_ClearSoftEvent",
    0x0002A214: "GH3X2X_CommunicateConfirm",
    0x0002A2AC: "GH3X2X_DelayUs",
    0x0002A31C: "GH3X2X_DumpModeSet",
    0x0002A328: "GH3X2X_EnterLowPowerMode",
    0x0002A380: "GH3X2X_ExitLowPowerMode",
    0x0002A488: "GH3X2X_FifoWatermarkThrConfig",
    0x0002A4B4: "GH3X2X_FunctionStart",
    0x0002A508: "GH3X2X_FunctionStop",
    0x0002A540: "GH3X2X_GetAlgoMemStatus",
    0x0002A550: "GH3X2X_GetConfigFuncMode",
    0x0002A55C: "GH3X2X_GetDemoVersion",
    0x0002A598: "GH3X2X_GetDriverLibVersion",
    0x0002A5D0: "GH3X2X_GetIrqStatus",
    0x0002A604: "GH3X2X_GetSoftEvent",
    0x0002A614: "GH3X2X_GetVirtualRegVersion",
    0x0002A754: "GH3X2X_Init",
    0x0002A8DC: "GH3X2X_LoadNewRegConfigArr",
    0x0002A968: "GH3X2X_Memcpy",
    0x0002A99E: "GH3X2X_Memset",
    0x0002AA10: "GH3X2X_ReadFifodata",
    0x0002AA74: "GH3X2X_ReadReg",
    0x0002AA98: "GH3X2X_ReadRegBitField",
    0x0002AAD0: "GH3X2X_RegisterDelayUsCallback",
    0x0002AADC: "GH3X2X_RegisterHookFunc",
    0x0002AAF8: "GH3X2X_RegisterI2cOperationFunc",
    0x0002ABA4: "GH3X2X_ResetHardAdt",
    0x0002ABDC: "GH3X2X_SendCmd",
    0x0002ABFC: "GH3X2X_SetChipSleepFlag",
    0x0002AC10: "GH3X2X_SetConfigFuncMode",
    0x0002AC1C: "GH3X2X_SetMaxNumWhenReadFifo",
    0x0002AC30: "GH3X2X_SetSoftEvent",
    0x0002AC40: "GH3X2X_SlotEnRegSet",
    0x0002ACCC: "GH3X2X_SoftReset",
    0x0002AD18: "GH3X2X_StartSampling",
    0x0002AD7C: "GH3X2X_StopSampling",
    0x0002AE08: "GH3X2X_TryWakeUp",
    0x0002AE28: "GH3X2X_UpdateAgcInfo",
    0x0002AF84: "GH3X2X_WriteChnlMapConfigWithVirtualReg",
    0x0002B010: "GH3X2X_WriteFunctionConfigWithVirtualReg",
    0x0002B0B8: "GH3X2X_WriteReg",
    0x0002B0DC: "GH3X2X_WriteRegBitField",
    0x0002B148: "GH3X2X_WriteSwConfigWithVirtualReg",
    0x0002B180: "GH3X2X_WriteVirtualReg",
    0x0002C248: "GH3x2xCalFunctionSlotBit",
    0x0002C27C: "GH3x2xCalGsensorStep",
    0x0002C2A4: "GH3x2xCreatTagArray",
    0x0002C2EC: "Gh3x2xDemoSearchCfgListByFunc",
    0x0002C43C: "GH3x2xFunctionProcess",
    0x0002C4FC: "GH3x2xGetFrameDataAndProcess",
    0x0002C640: "GH3x2xGetFrameNum",
    0x0002C694: "GH3x2xHandleFrameData",
    0x0002CCC0: "GH3x2xSetFunctionChnlMap",
    0x0002CCD0: "GH3x2xSetFunctionChnlNum",
    0x0002CD00: "GH3x2xSlotTimeInfo",
    0x0002D33C: "GH3x2x_GetActiveChipResetFlag",
    0x0002D348: "GH3x2x_GetChipResetRecoveringFlag",
    0x0002D3A8: "GH3x2x_SetChipResetRecoveringFlag",
    0x0002D658: "GetNextEventPointer",
    0x0002D670: "Gh3x2xDemoArrayCfgSwitch",
    0x0002D824: "Gh3x2xDemoFunctionProcess",
    0x0002D87C: "Gh3x2xDemoInit",
    0x0002DB8C: "Gh3x2xDemoInterruptProcess",
    0x0002E0D0: "Gh3x2xDemoSamplingControl",
    0x0002E340: "Gh3x2xDemoStartAlgoInner",
    0x0002E358: "Gh3x2xDemoStartSampling",
    0x0002E36C: "Gh3x2xDemoStartSamplingInner",
    0x0002E61C: "Gh3x2xDemoStartSamplingWithCfgSwitch",
    0x0002E6A8: "Gh3x2xDemoStopSampling",
    0x0002E6BC: "Gh3x2xDemoStopSamplingInner",
    0x0002E746: "Gh3x2xFifoRecovery",
    0x0002E778: "Gh3x2xFunctionInfoForUserInit",
    0x0002E7A4: "Gh3x2xFunctionSlotBitInit",
    0x0002E7C4: "Gh3x2xGetConfigVersion",
    0x0002E964: "Gh3x2xSetCurrentSlotEnReg",
    0x0002EB0C: "Gh3x2xSetFrameFlag2",
    0x0002EB80: "Gh3x2x_UserHandleCurrentInfo",
    0x0002EB84: "Gh3x2x_WearEventHook",
    0x0002ED98: "GH3X2X_ReinitAllSwModuleParam",
    0x0002EDAA: "GH3X2X_WriteSwConfigWithVirtualReg_0x1100_arm",
    0x0002EDE0: "GhDrvConfigManagerGetCurFunctionSupprort",
    0x0002EDEC: "GhDrvConfigManagerInit",
    0x0002EDFC: "GhGetFunctionIdViaVirReg",
    0x0002EE28: "GhMultiSensorTimerInit",
    0x0002EE38: "GhGsMoveDetecterIsEnable",
    0x0002EE44: "GhMultSensorWearEventManagerGetCurTs",
    0x0002EE50: "GhMultSensorWearEventManagerInit",
    0x0002EF6C: "GhMultiSensorPrintAllEvt",
    0x0002F0F8: "GhGsMoveDetecterInit",
    0x00029C98: "GH32x2xMedSel",
    0x00029CC0: "GH3X2XDrvConfigInit",
    0x00029CDC: "GH3X2X_AdtAlgorithmResultReport",
    0x00029D0A: "GH3X2X_AgcGetExtremum",
    0x00029D34: "GH3X2X_AgcGetThreshold",
    0x00029D58: "GH3x2xAgcInfoUpdate",
    0x00029D5C: "GH3X2X_AgcSubChnlGainAdj",
    0x00029E8C: "GH3X2X_AlgoCalculate",
    0x00029F88: "GH3X2X_AlgoChnlMapInit",
    0x0002A266: "GH3X2X_DecodeRegCfgArr",
    0x0002A474: "GH3X2X_FifoControlInit",
    0x0002A5EC: "GH3X2X_GetRegBitField",
    0x0002A630: "GH3X2X_HbaAlgoChnlMapDefultSet",
    0x0002A658: "GH3X2X_HrAlgorithmResultReport",
    0x0002A65A: "GH3X2X_HrvAlgorithmResultReport",
    0x0002A810: "GH3x2xAgcChnlInfoInit_veneer",
    0x0002A814: "GH3X2X_LedAgcPramWrite",
    0x0002A84C: "GH3X2X_LedAgcProcess",
    0x0002A86C: "GH3X2X_LedAgcReset",
    0x0002A9EC: "GH3X2X_ReadFifo",
    0x0002AC4C: "GH3X2X_SoftAdtGreenAlgorithmResultReport",
    0x0002AC8C: "GH3X2X_SoftAdtIrAlgorithmResultReport",
    0x0002ACF4: "GH3X2X_Spo2AlgoChnlMapDefultSet",
    0x0002AD14: "GH3X2X_Spo2AlgorithmResultReport",
    0x0002ADB0: "GH3X2X_StoreDrvCurrentAfterAgc",
    0x0002AE00: "GH3X2X_TimestampSyncGetFrameDataFlag",
    0x0002AE04: "GH3X2X_TimestampSyncPpgInit",
    0x0002AE06: "GH3X2X_TimestampSyncSetPpgIntFlag",
    0x0002AEDC: "GH3X2X_WriteAlgConfigWithVirtualReg",
    0x0002AF32: "GH3X2X_WriteAlgParametersWithVirtualReg",
    0x0002B218: "GH3x2xAdtAlgoExe",
    0x0002B4C4: "GH3x2xAdtAlgoInit",
    0x0002B4D8: "GH3x2xAdtVersion",
    0x0002B4F8: "GH3x2xAgcCalDrvCurrent",
    0x0002B524: "GH3x2xAgcCalDrvCurrentAndGain",
    0x0002B6A4: "GH3x2xAgcCalExtremum",
    0x0002B6E0: "GH3x2xAgcChnlInfoInit",
    0x0002B8EC: "GH3x2xAgcFindSubChnlSlotInfo",
    0x0002B91C: "GH3x2xAgcInfoUpdate",
    0x0002B998: "GH3x2xAgcMainChnlKeyValueCal",
    0x0002BD84: "GH3x2xAgcMeanInfoReset",
    0x0002BE24: "GH3x2xAgcRegParse",
    0x0002BFAA: "GH3x2xAgcRegvalGet",
    0x0002C148: "GH3x2xAgcRegvalReset",
    0x0002C178: "GH3x2xAgcSubChnlAdjGainAndClearCnt",
    0x0002C4C0: "GH3x2xGetAgcReg",
    0x0002C4E4: "GH3x2xGetDrvCurrent",
    0x0002C930: "GH3x2xHrAlgoDeinit",
    0x0002C944: "GH3x2xHrAlgoExe",
    0x0002CAA4: "GH3x2xHrAlgoInit",
    0x0002CAD8: "GH3x2xHrvAlgoExe",
    0x0002CC94: "GH3x2xSetAgcReg",
    0x0002CCF4: "Gh3x2xSleepFlagGet",
    0x0002CDD4: "GH3x2xSoftAdtAlgoExe",
    0x0002CFE8: "GH3x2xSpo2AlgoExe",
    0x0002D16C: "GH3x2xSpo2AlgoInit",
    0x0002D184: "GH3x2x_AgcAdjustGainByExtremum",
    0x0002D324: "GH3x2x_BitCount",
    0x0002D354: "GH3x2x_Round",
    0x0002E8C4: "Gh3x2xGetHrAlgoSupportChnl",
    0x0002E8C8: "Gh3x2xGetSpo2AlgoSupportChnl",
    0x0002E8E8: "Gh3x2xMovingAvaFilter",
    0x0006A018: "get_Spo2WRWeights_addr",
    0x0006A020: "get_Spo2WRWeights_version",
    0x0006A130: "get_knConfNetWeightsArr_addr",
    0x0006A148: "get_knTdfusionWeightsArr_addr",
    0x0006A150: "get_knWeightsArr_addr",
    0x0006A500: "GH3X2X_AlgoCallConfigInit",
    0x0006CC2C: "goodix_hba_config_get_arr",
    0x0006CC34: "goodix_hrv_config_get_version",
    0x0006D3C0: "goodix_hba_init_func",
    0x0006EAF8: "goodix_spo2_config_get_instance",
    0x0006EB00: "goodix_spo2_config_get_version",
    0x0006EC28: "goodix_spo2_init_func",
}

# Moderate-confidence mappings from the same mapping pass: structural match but
# with a documented caveat (upstream body divergence or partial body).
APP_GOODIX_PUBLIC_DEMOCODE_MODERATE = {
    0x0002A5C4: "GH3X2X_GetGsensorEnableFlag",
    0x0002A7F4: "GH3X2X_InitSensorParameters",
    0x0002A9D4: "GH3X2X_ReadElectrodeWearDumpData",
    0x0002ABEC: "GH3X2X_SensorPramInit",
    0x0002D66C: "Gh2x2xUploadDataToMaster",
    0x0002EB4E: "Gh3x2x_NormalizeGsensorSensitivity",
}


# The attributable IQS7211E references supply the controller/register/state-
# machine semantics. These byte-pinned functions are the recovered R1 product
# configuration, generic bus port, communication-window glue, IRQ routing, and
# retry policy. None is treated as an unidentified vendor driver body.
APP_IQS7211E_CONFIGURATIONS = {
    0x0002F880: "r1_iqs7211e_configure",
}

APP_IQS7211E_ADAPTERS = {
    0x0002F866: "r1_iqs7211e_factory_communication_end",
    0x0002FDC8: "r1_iqs7211e_irq_config_refresh",
    0x0002FDE2: "r1_iqs7211e_communication_end",
    0x0002FDF8: "r1_iqs7211e_suspend",
    0x0002FE9C: "r1_iqs7211e_register_read_port",
    0x0002FEAC: "r1_iqs7211e_register_write_port",
    0x00030E6C: "r1_iqs7211e_irq_worker",
    **{
        int(item["entry"]): str(item["symbol"])
        for item in R1_TOUCH_TASK_DISPATCHER_FUNCTIONS
    },
    0x0006F9E4: "r1_iqs7211e_ati_recovery_policy",
    0x0006FCE8: "r1_iqs7211e_reset_reconfigure",
    0x00087BA4: "r1_iqs7211e_read_word_adapter",
}


# ST's BSD-3-Clause ST25DVxxKC component source at the pinned fp-sns-stbox1
# commit supplies these device-driver bodies. ReadReg and WriteReg are exact
# BSim matches; the remainder retain the same public API roles, register
# constants, IO-table layout, chunking, status decoding, and control flow.
# These names are public upstream symbols and may be compiled from the pinned
# vendor snapshot instead of being recreated locally.
APP_ST25DVXXKC_SYMBOLS = {
    0x00031B32: "ST25DVxxKC_GetGPO1_ALL",
    0x00031B46: "ST25DVxxKC_GetGPO2_ALL",
    0x00031B62: "ST25DVxxKC_GetGPOStatus",
    0x00031B96: "ST25DVxxKC_GetI2C_SSO_DYN_I2CSSO",
    0x00031BF4: "ST25DVxxKC_GetMB_CTRL_DYN_ALL",
    0x00031C0A: "ST25DVxxKC_GetFTM_MBMODE",
    0x00031C26: "ST25DVxxKC_Init",
    0x00031CA4: "ST25DVxxKC_IsDeviceReady",
    0x00031CB6: "ST25DVxxKC_ReadI2CSecuritySession_Dyn",
    0x00031CD2: "ST25DVxxKC_ReadID",
    0x00031D36: "ST25DVxxKC_ReadMBMode",
    0x00031D78: "ST25DVxxKC_ReadReg",
    0x00031D88: "ST25DVxxKC_RegisterBusIO",
    0x00031DC8: "ST25DVxxKC_ResetEHENMode_Dyn",
    0x00031DDA: "ST25DVxxKC_SetEH_CTRL_DYN_EH_EN",
    0x00031E0E: "ST25DVxxKC_SetGPO1_ALL",
    0x00031E22: "ST25DVxxKC_SetGPO2_ALL",
    0x00031E64: "ST25DVxxKC_SetMB_CTRL_DYN_MBEN",
    0x00031E98: "ST25DVxxKC_WriteData",
    0x00031F2C: "ST25DVxxKC_WriteReg",
    0x00031F3A: "ST25DVxxKC_WriteRegister",
    0x00077CE4: "ST25DVxxKC_ReadITSTStatus_Dyn",
    0x00077CF0: "ST25DVxxKC_ReadMailboxData",
    0x00077CFC: "ST25DVxxKC_ReadMBCtrl_Dyn",
    0x00077D08: "ST25DVxxKC_ReadMBLength_Dyn",
    0x00077D14: "ST25DVxxKC_SetMBEN_Dyn",
    0x00077D20: "ST25DVxxKC_WriteMailboxData",
}


# These functions are product policy and board integration around the ST
# provider. The mailbox receive seam is intentionally named "bounded": the
# stock image trusts the tag-reported length, while openR1 must reject or cap a
# length above the 20-byte product buffer before calling the upstream driver.
APP_ST25DVXXKC_ADAPTERS = {
    0x00044BEC: "r1_st25dvxxkc_bus_registration",
    0x00044C90: "r1_st25dvxxkc_password_present",
    0x00044C9C: "r1_st25dvxxkc_security_session",
    0x00044CE8: "r1_st25dvxxkc_gpo_configuration",
    0x00077764: "r1_st25dvxxkc_initialize_configuration",
    0x00077BE0: "r1_st25dvxxkc_bounded_mailbox_receive",
    0x00077C50: "r1_st25dvxxkc_identity_log_adapter",
    **{
        int(item["entry"]): str(item["symbol"])
        for item in R1_NFC_DOCK_POLICY_FUNCTIONS
    },
}


# Board/power ownership surrounding the shared NFC/YHM2710 conductor pair is
# R1 product glue, not a recreation of either device driver.  The three NFC
# entries configure/toggle the ring-specific P1.10 board-enable line and take
# or release i2c_5.  The two power entries maintain client ownership while the
# electrical transition itself remains behind the unresolved YHM2710 provider.
APP_I2C5_RESOURCE_ADAPTERS = {
    0x00050464: "r1_i2c5_nfc_resource_registration",
    0x000504C0: "r1_i2c5_nfc_resource_release",
    0x000504D8: "r1_i2c5_nfc_resource_acquire",
    0x00050758: "r1_shared_power_client_release",
    0x00050778: "r1_shared_power_client_acquire",
}


APP_VENDOR_MARKERS = [
    ("goodix_gh3x2x_candidate", re.compile(
        r"gh3x2x|Goodix|MultiSensor|search_cfg_app_mode|CfgIndex|"
        r"cfg_d_switch|particular_watermark|Array_None|Config_Version|"
        r"Current_uchSlotEn", re.I),
     "vendor_source_required_not_redistributable",
     "Function references GH3X2X/Goodix-specific data or diagnostics; exact SDK/demo ownership must be resolved."),
    ("gomore_health_algorithm_candidate", re.compile(r"gomore", re.I),
     "vendor_source_required_not_redistributable",
     "Function references GoMore-specific health-algorithm APIs or diagnostics; exact SDK version, source, and redistribution rights must be resolved."),
    ("azoteq_iqs7211e_candidate", re.compile(r"IQS7211E", re.I),
     "vendor_source_required_not_redistributable",
     "Function references Azoteq IQS7211E-specific configuration or diagnostics; official v1.1 example source is public but carries no admitted redistribution license."),
    ("gxcas_gxt310_candidate", re.compile(r"GXT310", re.I),
     "vendor_source_required_not_redistributable",
     "Function references GXCAS GXT310-specific temperature-sensor variants, addresses, configuration, or diagnostics; exact provider-source lineage and license are unresolved."),
    ("yhmicros_yhm2710_candidate", re.compile(r"YHM2710", re.I),
     "clean_room_reimplementation_owner_authorized",
     "Function references YHMICROS YHM2710-specific identification, configuration, or diagnostics. The exact vendor source remains unlicensed; the complete 36-entry closure is independently reconstructed in reconstructed/yhm2710 under the owner-authorized full-reduction policy."),
    ("bosch_bma456_candidate", re.compile(r"BMA456", re.I),
     "resolve_provider_before_implementation",
     "Function references BMA456-specific data or diagnostics; distinguish Bosch driver from R1 adapter before implementation."),
    ("stmicro_lis2doc_candidate", re.compile(r"LIS2DOC", re.I),
     "resolve_provider_before_implementation",
     "Function references LIS2DOC-specific data or diagnostics; exact ST driver/version ownership is unresolved."),
    ("qst_qma6100_candidate", re.compile(r"QMA6100", re.I),
     "resolve_provider_before_implementation",
     "Function references QMA6100-specific data or diagnostics; exact QST driver/version ownership is unresolved."),
    ("armink_cmbacktrace_candidate", re.compile(r"cm_backtrace|CmBacktrace", re.I),
     "resolve_provider_before_implementation",
     "Function contains a CmBacktrace-specific reference; exact upstream version correlation is required."),
]


def read_functions(image: str) -> list[dict[str, str]]:
    path = DECOMP / image / "functions.csv"
    with path.open(newline="") as stream:
        rows = list(csv.DictReader(stream))
    if not rows:
        raise ValueError(f"empty function inventory: {path}")
    return rows


def read_boot_reconstruction_functions() -> list[dict[str, str]]:
    path = BOOT_RECON / "functions.csv"
    with path.open(newline="") as stream:
        generated = list(csv.DictReader(stream))
    if not generated:
        raise ValueError(f"empty function inventory: {path}")
    return [
        {
            "entry": row["entry"],
            "end": row["body_max"],
            "size": row["body_bytes"],
            "name": row["name"],
            "inventory_source": "ghidra_functions_csv",
        }
        for row in generated
    ]


def read_decompiler_blocks(image: str) -> dict[int, str]:
    text = (DECOMP / image / "decompiler-output.c").read_text(errors="replace")
    matches = list(re.finditer(
        r"/\* ={20,}\n \* entry: (0x[0-9a-fA-F]+).*?\* name:\s+([^\n]+)", text, re.S))
    result: dict[int, str] = {}
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        result[int(match.group(1), 16)] = text[match.start():end]
    return result


def base_row(image: str, raw: dict[str, str]) -> dict[str, str]:
    entry = int(raw["entry"], 16)
    if image == "application" and entry in APP_INVENTORY_EXTENT_OVERRIDES:
        size = str(APP_INVENTORY_EXTENT_OVERRIDES[entry])
        end = f"0x{entry + int(size) - 1:08x}"
    else:
        size = raw["size"]
        end = raw["end"].lower()
    return {
        "image": image,
        "inventory_source": raw.get("inventory_source", "ghidra_functions_csv"),
        "entry": raw["entry"].lower(),
        "end": end,
        "size": size,
        "recovered_name": raw["name"],
        **DEFAULT,
    }


def classify_application(raw: dict[str, str], block: str) -> dict[str, str]:
    row = base_row("application", raw)
    entry = int(raw["entry"], 16)
    if entry in FLASHDB_SYMBOLS:
        row.update(
            provider_family="flashdb_2_0_0",
            source_disposition="use_pinned_upstream",
            upstream_symbol=FLASHDB_SYMBOLS[entry],
            confidence="high",
            evidence=(
                "Function-local control flow matches pinned FlashDB 2.0.0; "
                "reverse-time traversal and _fdb_db_path discriminate the release."
            ),
        )
        return row
    if entry in FAL_SYMBOLS:
        row.update(
            provider_family="fal_0_5_99_flashdb_bundled",
            source_disposition="use_pinned_upstream",
            upstream_symbol=FAL_SYMBOLS[entry],
            confidence="high",
            evidence=(
                "Exact FAL 0.5.99 body bundled by pinned FlashDB 2.0.0; only "
                "the R1 flash-device port and partition configuration are local."
            ),
        )
        return row
    if entry in APP_GXT310_RECONSTRUCTED_SYMBOLS:
        row.update(
            provider_family="gxcas_gxt310_candidate",
            source_disposition="clean_room_reimplementation_owner_authorized",
            upstream_symbol=APP_GXT310_RECONSTRUCTED_SYMBOLS[entry],
            confidence="high",
            evidence=(
                "Owner-authorized full reduction of the five-function GXT310 "
                "closure from SHA-pinned decompilation evidence; independently "
                "compiled C in reconstructed/gxt310/, not vendor source."
            ),
        )
        return row
    if entry in APP_QMA6100_PROVIDER_SYMBOLS:
        row.update(
            provider_family="qst_qma6100_v1_0_lineage_unlicensed",
            source_disposition="clean_room_reimplementation_owner_authorized",
            upstream_symbol=APP_QMA6100_PROVIDER_SYMBOLS[entry],
            confidence="high",
            evidence=(
                "Function control flow matches the public QST-authored QMA6100 "
                "V1.0 lineage. Under the owner-authorized full reduction the "
                "body is reconstructed from the stock-image evidence in "
                "reconstructed/qma6100/; this is not QST source."
            ),
        )
        return row
    if entry in APP_QMA6100_ADAPTERS:
        row.update(
            provider_family="r1_qst_qma6100_provider_adapter",
            source_disposition="clean_room_reimplementation_owner_authorized",
            upstream_symbol=APP_QMA6100_ADAPTERS[entry],
            confidence="high",
            evidence=(
                "QST QMA6100 V1.0-lineage skeleton with an R1 identity, "
                "configuration, transport, bounds, or event seam; reduced with "
                "the complete owner-authorized 17-entry QMA source module in "
                "reconstructed/qma6100/."
            ),
        )
        return row
    if entry in APP_GOODIX_HEAP_RECONSTRUCTED_SYMBOLS:
        row.update(
            provider_family="goodix_gh3x2x_candidate",
            source_disposition="clean_room_reimplementation_owner_authorized",
            upstream_symbol=APP_GOODIX_HEAP_RECONSTRUCTED_SYMBOLS[entry],
            confidence="high",
            evidence=(
                "Owner-authorized clean-room reconstruction of the complete "
                "Goodix goodix_mem/GdMem heap core from SHA-pinned Ghidra and "
                "Thumb-2 evidence in reconstructed/goodix_heap/. The C pool "
                "uses checked relative offsets and contains no Goodix source "
                "or opaque firmware bytes."
            ),
        )
        return row
    if entry in APP_GOODIX_PRIMITIVES_RECONSTRUCTED_SYMBOLS:
        reconstructed_symbol = APP_GOODIX_PRIMITIVES_RECONSTRUCTED_SYMBOLS[entry]
        if reconstructed_symbol.startswith("quantized_runtime_"):
            reconstructed_evidence = (
                "Owner-authorized clean-room reconstruction of the complete "
                "Goodix graph/runtime behavior from SHA-pinned Ghidra and "
                "Thumb-2 evidence in reconstructed/quantized_runtime/. "
                "Foreign executor addresses are local bindings or explicit "
                "provider tokens; no Goodix source or opaque firmware bytes "
                "are incorporated."
            )
        elif reconstructed_symbol.startswith("gomore_primitives_"):
            reconstructed_evidence = (
                "Owner-authorized clean-room reconstruction of the complete "
                "shared small-function behavior from SHA-pinned Ghidra and "
                "Thumb-2 evidence in reconstructed/gomore_primitives/. The "
                "alternate stock entry maps to the same typed C body; no "
                "Goodix or GoMore source or opaque firmware bytes are "
                "incorporated."
            )
        else:
            reconstructed_evidence = (
                "Owner-authorized clean-room reconstruction of the complete "
                "small-function behavior from SHA-pinned Ghidra and Thumb-2 "
                "evidence in reconstructed/goodix_primitives/. Absolute stock "
                "table pointers are explicit typed bindings; no Goodix source "
                "or opaque firmware bytes are incorporated."
            )
        if entry == 0x00092B60:
            primitive_family = "r1_product_specific"
        elif entry in APP_GOODIX_PUBLIC_DEMOCODE or \
                entry in APP_GOODIX_PUBLIC_DEMOCODE_MODERATE:
            primitive_family = \
                "goodix_gh3x2x_democode_v1_6_drvlib_v4_3_0_0"
        elif entry in APP_GOODIX_ADAPTERS:
            primitive_family = "r1_goodix_provider_adapter"
        else:
            primitive_family = "goodix_gh3x2x_candidate"
        row.update(
            provider_family=primitive_family,
            source_disposition="clean_room_reimplementation_owner_authorized",
            upstream_symbol=reconstructed_symbol,
            confidence="high",
            evidence=reconstructed_evidence,
        )
        return row
    if entry in APP_GOMORE_PRIMITIVES_RECONSTRUCTED_SYMBOLS:
        row.update(
            provider_family="gomore_health_algorithm_candidate",
            source_disposition="clean_room_reimplementation_owner_authorized",
            upstream_symbol=APP_GOMORE_PRIMITIVES_RECONSTRUCTED_SYMBOLS[entry],
            confidence="high",
            evidence=(
                "Owner-authorized clean-room reconstruction of the complete "
                "small-function behavior from SHA-pinned Ghidra and Thumb-2 "
                "evidence in reconstructed/gomore_primitives/ and "
                "reconstructed/gomore_tensor_runtime/ or the typed shared "
                "runtime in reconstructed/quantized_runtime/. Provider calls "
                "are typed bindings; no GoMore source, model data, or opaque "
                "firmware bytes are incorporated."
            ),
        )
        return row
    if entry in APP_ST25DVXXKC_SYMBOLS:
        row.update(
            provider_family="stmicro_st25dvxxkc_bsd_compatible",
            source_disposition="use_authenticated_upstream_snapshot",
            upstream_symbol=APP_ST25DVXXKC_SYMBOLS[entry],
            confidence="high",
            evidence=(
                "Function-local control flow, register constants, IO-table layout, "
                "status decoding, and mailbox/data transport semantics match the "
                "pinned official ST25DVxxKC BSD component; ReadReg and WriteReg "
                "also produce exact BSim similarity 1.0 matches."
            ),
        )
        return row
    if entry in APP_ST25DVXXKC_ADAPTERS:
        symbol = APP_ST25DVXXKC_ADAPTERS[entry]
        mailbox_note = (
            " The recovered stock receive path does not enforce its 20-byte "
            "destination bound; the clean-room adapter must reject or cap the "
            "reported mailbox length before invoking ST's provider."
            if entry == 0x00077BE0 else ""
        )
        row.update(
            provider_family="r1_st25dvxxkc_provider_adapter",
            source_disposition="clean_room_adapter_only_use_pinned_provider",
            upstream_symbol=symbol,
            confidence="high",
            evidence=(
                "R1-specific bus, password, security-session, GPO, initialization, "
                "mailbox-policy, or identity/logging seam around the pinned official "
                "ST25DVxxKC provider." + mailbox_note
            ),
        )
        return row
    if entry in APP_I2C5_RESOURCE_ADAPTERS:
        row.update(
            provider_family="r1_i2c5_resource_adapter",
            source_disposition="clean_room_adapter_only_vendor_io_abstract",
            upstream_symbol=APP_I2C5_RESOURCE_ADAPTERS[entry],
            confidence="high",
            evidence=(
                "SHA-pinned R1-only board-enable, exclusive i2c_5 ownership, "
                "or battery/optical/touch client-mask policy. ST25DVxxKC "
                "operations come from the pinned ST provider; reconstructed "
                "YHM2710 electrical/register operations remain behind the "
                "abstract shared-resource seam."
            ),
        )
        return row
    if entry in APP_GOMORE_ADAPTERS:
        row.update(
            provider_family="r1_gomore_provider_adapter",
            source_disposition="clean_room_adapter_only_use_licensed_provider",
            upstream_symbol=APP_GOMORE_ADAPTERS[entry],
            confidence="high",
            evidence=(
                "SHA-pinned R1 topic-input or time-transition adapter with "
                "bounded sample-count, numeric-conversion, axis-layout, "
                "readiness-bit, or backward-clock threshold behavior. "
                "Only this adapter seam may be local after licensed GoMore "
                "provider admission."
            ),
        )
        return row
    if entry in APP_GOODIX_ADAPTERS:
        row.update(
            provider_family="r1_goodix_provider_adapter",
            source_disposition="clean_room_adapter_only_use_licensed_provider",
            upstream_symbol=APP_GOODIX_ADAPTERS[entry],
            confidence="high",
            evidence=(
                "SHA-pinned R1 power, transport, lifecycle, profile-mask, "
                "reference-count, or command-routing seam around the proprietary "
                "Goodix GH3X2X provider. Only this product adapter may be local; "
                "biometric processing remains provider-owned."
            ),
        )
        return row
    if entry in APP_IQS7211E_CONFIGURATIONS:
        row.update(
            provider_family="r1_iqs7211e_provider_adapter",
            source_disposition="clean_room_configuration_only_use_pinned_provider",
            upstream_symbol=APP_IQS7211E_CONFIGURATIONS[entry],
            confidence="high",
            evidence=(
                "SHA-pinned R1-only IQS7211E register profile, electrode layout, "
                "ring-size calibration selection, and final control word around "
                "the attributable provider semantics."
            ),
        )
        return row
    if entry in APP_IQS7211E_ADAPTERS:
        row.update(
            provider_family="r1_iqs7211e_provider_adapter",
            source_disposition="clean_room_adapter_only_use_pinned_provider",
            upstream_symbol=APP_IQS7211E_ADAPTERS[entry],
            confidence="high",
            evidence=(
                "SHA-pinned R1 transport, communication-window, lifecycle, IRQ, "
                "reset, suspend, or bounded ATI-recovery seam around the pinned "
                "IQS7211E provider references and Nordic SDK bus primitives."
            ),
        )
        return row
    if entry in APP_UNKNOWN_QUANTIZED_NEURAL_RUNTIME_CANDIDATES:
        row.update(
            provider_family="unknown_shared_quantized_neural_runtime_candidate",
            source_disposition="clean_room_reimplementation_owner_authorized",
            upstream_symbol=APP_UNKNOWN_QUANTIZED_NEURAL_RUNTIME_CANDIDATES[entry],
            confidence="high",
            evidence=(
                "SHA-pinned indirect quantized tensor runtime or descriptor "
                "reached through constructors shared by separately gated GoMore "
                "and Goodix model graphs. No attributable source, version, or "
                "license exists (2026-08 re-examination: boundaries/unknown_"
                "shared_quantized_neural_runtime_candidate-ATTRIBUTION-2026-08.md; "
                "the closed Bravechip ChipletRing/BCL603M platform is the "
                "supported origin). Under the owner-authorized full reduction "
                "(SOURCE-ADMISSION.md, 2026-08-14) the twenty-seven-entry family "
                "is reconstructed from the decompilation evidence as "
                "independently compiled C in reconstructed/quantized_runtime/ "
                "with per-function provenance; the reconstruction is not vendor "
                "source. Contract, divergences, and test mapping: "
                "correlation/QUANTIZED-RUNTIME-REDUCTION-CORRELATION.md."
            ),
        )
        return row
    if entry in APP_GOODIX_PUBLIC_DEMOCODE:
        row.update(
            provider_family="goodix_gh3x2x_democode_v1_6_drvlib_v4_3_0_0",
            source_disposition="use_pinned_upstream",
            upstream_symbol=APP_GOODIX_PUBLIC_DEMOCODE[entry],
            confidence="high",
            evidence=(
                "Function-level identity with the pinned public Goodix-licensed "
                "GH3X2X democode (third-party component goodix-gh3x2x-democode, "
                "pebbleos-nonfree gh3x2x/ @ 2c0034a2, democode v1.6 / DrvLib "
                "v4.3.0.0, Goodix 5-clause license with clause-4 Goodix-IC use "
                "satisfied by the R1 ring) is proven by control-flow, constant, "
                "and log-string topology per "
                "docs/boundaries/goodix_gh3x2x_candidate-ATTRIBUTION-2026-08.md "
                "and docs/boundaries/GOODIX-DEMO-DRIVER-MAPPING-2026-08.md; the "
                "R1 body carries a chip-errata register patch absent from "
                "public v4.3.0.0 where noted."
            ),
        )
        return row
    if entry in APP_GOODIX_PUBLIC_DEMOCODE_MODERATE:
        row.update(
            provider_family="goodix_gh3x2x_democode_v1_6_drvlib_v4_3_0_0",
            source_disposition="use_pinned_upstream",
            upstream_symbol=APP_GOODIX_PUBLIC_DEMOCODE_MODERATE[entry],
            confidence="candidate",
            evidence=(
                "Moderate-confidence mapping to the pinned public Goodix-licensed "
                "GH3X2X democode (goodix-gh3x2x-democode @ 2c0034a2) per "
                "docs/boundaries/GOODIX-DEMO-DRIVER-MAPPING-2026-08.md: structural "
                "match with a documented caveat (upstream divergence or partial "
                "body); re-verify before compiling against this entry."
            ),
        )
        return row
    if entry in APP_GOODIX_EXACT_CANDIDATES:
        role = APP_GOODIX_EXACT_CANDIDATES[entry]
        row.update(
            provider_family="goodix_gh3x2x_candidate",
            source_disposition="vendor_source_required_not_redistributable",
            upstream_symbol="",
            confidence="high",
            evidence=(
                f"Exact Goodix GH3X2X {role} boundary. Goodix's primary-source "
                "developer trace reproduces the embedded algorithm names, versions, "
                "component hashes, and demo output; no private symbol or "
                "redistributable source package is asserted."
            ),
        )
        return row
    if entry in APP_GOODIX_RESOLVED_THUNKS:
        row.update(
            provider_family="goodix_gh3x2x_candidate",
            source_disposition="vendor_source_required_not_redistributable",
            upstream_symbol="",
            confidence="high",
            evidence=(
                "Exact four-byte B.W thunk into the frozen Goodix GH3X2X provider "
                "component. The branch destination and sole caller are byte-pinned; "
                "the thunk does not authorize a local substitute for its proprietary target."
            ),
        )
        return row
    if entry in APP_GOODIX_CLUSTER_CANDIDATES:
        row.update(
            provider_family="goodix_gh3x2x_candidate",
            source_disposition="vendor_source_required_not_redistributable",
            upstream_symbol="",
            confidence="candidate",
            evidence=(
                "Entry belongs to the frozen direct-call-graph component anchored "
                "by exact Goodix GH3X2X version/demo/config/event functions in the "
                "0x00029F88..0x0002F107 linked region. This is a conservative "
                "provider gate, not an asserted private symbol; licensed-source "
                "comparison is required before any finer implementation split."
            ),
        )
        return row
    if entry in APP_GOMORE_AUDIT_FUNCTIONS:
        audit_groups = ", ".join(APP_GOMORE_AUDIT_FUNCTIONS[entry])
        row.update(
            provider_family="gomore_health_algorithm_candidate",
            source_disposition="vendor_source_required_not_redistributable",
            upstream_symbol="",
            confidence="candidate",
            evidence=(
                "Function entry is covered by SHA-pinned GoMore algorithm audit "
                f"scope(s): {audit_groups}. The audited code range, constants, and "
                "direct-call topology establish a vendor-algorithm boundary, but the "
                "exact SDK version, private symbol, source package, and license remain unresolved."
            ),
        )
        return row
    if entry in APP_PRODUCT_SECURITY_PRESERVING:
        security_evidence = (
            "SHA-pinned R1 MAC-keyed compiled-default restore behavior and identity-table "
            "extent. Only an abstract caller-supplied restore policy may be local; the "
            "recovered identity table, identity logging, and live persistent mutation remain disabled."
            if entry == 0x0007C52C else
            "SHA-pinned R1 EUS fragment reassembly and outer-CRC behavior. Valid wire behavior "
            "is implemented with bounded per-link state; malformed duplicate, discontinuous, "
            "oversized, and repeated-checksum-inconsistent trains are rejected."
            if entry == 0x00032198 else
            "SHA-pinned R1 nonvolatile recovery/report/merge behavior. Only bounded internal "
            "planning is admitted; the identity-bearing BLE restore sender and persistent "
            "mutation surface remain disabled."
        )
        row.update(
            provider_family="r1_product_specific",
            source_disposition="clean_room_behavior_only_security_preserving",
            upstream_symbol=APP_PRODUCT_SECURITY_PRESERVING[entry],
            confidence="high",
            evidence=security_evidence,
        )
        return row
    if entry in APP_PRODUCT_DATA_MODEL_FUNCTIONS:
        row.update(
            provider_family="r1_product_specific",
            source_disposition="clean_room_data_model_only",
            upstream_symbol=APP_PRODUCT_DATA_MODEL_FUNCTIONS[entry],
            confidence="high",
            evidence=(
                "SHA-pinned R1 fixed-record accessor already represented by a "
                "bounded clean-room data field. Persistent lookup, logging, live "
                "flash access, and transport remain outside the local model."
            ),
        )
    elif entry in APP_PRODUCT_FUNCTIONS:
        row.update(
            provider_family="r1_product_specific",
            source_disposition="clean_room_behavior_only",
            upstream_symbol=APP_PRODUCT_FUNCTIONS[entry],
            confidence="high",
            evidence="Accepted R1 decompilation/security-audit behavior address; no third-party implementation identified.",
        )
    elif entry in APP_HEALTH_STORAGE_ADAPTERS:
        health_storage_evidence = (
            "Four-byte R1 singleton accessor used by the public health-history "
            "synchronizers to obtain the pinned FlashDB provider object; the "
            "object and all TSDB operations remain provider-owned."
            if entry == 0x00070028 else
            "SHA-pinned R1 time/hour orchestration around the pinned FlashDB "
            "provider and bounded metric callbacks. Only planning and cursor "
            "policy may be local; TSDB, allocation, clock, calendar, and "
            "metric-provider internals remain external."
        )
        row.update(
            provider_family="r1_health_storage_provider_adapter",
            source_disposition="clean_room_adapter_only_use_pinned_provider",
            upstream_symbol=APP_HEALTH_STORAGE_ADAPTERS[entry],
            confidence="high",
            evidence=health_storage_evidence,
        )
    elif entry in APP_NORDIC_CMSIS_ADAPTERS:
        row.update(
            provider_family="r1_nordic_cmsis_provider_adapter",
            source_disposition="clean_room_adapter_only_use_nordic_sdk_and_cmsis",
            upstream_symbol=APP_NORDIC_CMSIS_ADAPTERS[entry],
            confidence="high",
            evidence=(
                "SHA-pinned R1 TWI register-transfer, completion, blocking-wait, or lifecycle policy around "
                "Nordic nrfx/nrf_drv_twi and the authenticated CMSIS-RTOS2 "
                "wrapper. Only the product state/status mapping, timeout policy, "
                "lifecycle configuration, and provider calls may be local; driver, RTOS, semaphore, kernel, "
                "tick, and delay implementations remain upstream."
            ),
        )
    elif entry in APP_RESET_TRACE_CMSIS_ADAPTERS:
        row.update(
            provider_family="r1_nordic_cmsis_provider_adapter",
            source_disposition="clean_room_adapter_only_use_nordic_sdk_and_cmsis",
            upstream_symbol=APP_RESET_TRACE_CMSIS_ADAPTERS[entry],
            confidence="high",
            evidence=(
                "SHA-pinned R1 fault-tag and retained reset-trace policy around "
                "the pinned Nordic SDK CMSIS NVIC_SystemReset primitive. Only "
                "the product record/capture adapter is local; barriers, AIRCR "
                "reset request, and terminal reset behavior remain provider code."
            ),
        )
    elif entry in APP_DEVICE_REGISTRY_CONFIGURATION_ADAPTERS:
        if entry == 0x000563C4:
            registry_configuration_evidence = (
                "Exact-extent R1 fixed RTC record/operation-table binding around "
                "the unidentified stock global registry. Preserve the product "
                "record through a direct typed Nordic RTC/provider interface; do "
                "not recreate the registry or the unidentified RTC-device layer."
            )
        elif entry == 0x000565F4:
            registry_configuration_evidence = (
                "Exact-extent R1 fixed device_stacmd record/operation-table binding. "
                "Preserve the direct typed provider binding; the reconstructed "
                "YHM2710 transport is bound without recreating the stock registry."
            )
        elif entry == 0x00056694:
            registry_configuration_evidence = (
                "Exact-extent R1 fixed watchdog record/operation-table binding. "
                "Preserve the product configuration through a direct Nordic nrfx_wdt "
                "adapter and do not recreate the stock generic registry."
            )
        else:
            registry_configuration_evidence = (
                "Exact-extent R1 fixed bus-record configuration wrapper around "
                "the unidentified stock global registry. Preserve board binding "
                "through direct typed Nordic/vendor provider interfaces; do not "
                "recreate the registry or software-I2C engine. CMSIS semaphore "
                "creation remains an authenticated upstream provider operation."
            )
        row.update(
            provider_family="r1_device_registry_configuration_adapter",
            source_disposition="clean_room_configuration_only_direct_typed_binding",
            upstream_symbol=APP_DEVICE_REGISTRY_CONFIGURATION_ADAPTERS[entry],
            confidence="high",
            evidence=registry_configuration_evidence,
        )
    elif entry in APP_UNKNOWN_SOFTWARE_TWI_CANDIDATES:
        row.update(
            provider_family="unknown_software_twi_provider_candidate",
            source_disposition="clean_room_reimplementation_owner_authorized",
            upstream_symbol=APP_UNKNOWN_SOFTWARE_TWI_CANDIDATES[entry],
            confidence="high",
            evidence=(
                "Exact executable extent, GPIO-driven wire semantics, and four-bus "
                "compiler-instantiated family structure are recovered and SHA-pinned; "
                "no attributable source, provider version, or license exists "
                "(2026-08 re-examination: boundaries/unknown_software_twi_provider"
                "_candidate-ATTRIBUTION-2026-08.md; the engine is B210/Bravechip "
                "ChipletRing platform middleware). Under the owner-authorized "
                "full reduction (SOURCE-ADMISSION.md, 2026-08-14) the "
                "forty-entry family is reconstructed from the decompilation "
                "evidence as independently compiled C in "
                "reconstructed/software_twi/ with per-function provenance; the "
                "reconstruction is not vendor source. Contract, divergences, "
                "and test mapping: "
                "correlation/SOFTWARE-TWI-REDUCTION-CORRELATION.md."
            ),
        )
    elif entry in APP_UNKNOWN_RTC_DEVICE_CANDIDATES:
        row.update(
            provider_family="unknown_rtc_device_provider_candidate",
            source_disposition="clean_room_reimplementation_owner_authorized",
            upstream_symbol=APP_UNKNOWN_RTC_DEVICE_CANDIDATES[entry],
            confidence="high",
            evidence=(
                "Exact executable extent and RTC-device semantics are recovered "
                "and SHA-pinned; no attributable source, provider version, or "
                "license exists (2026-08 re-examination: boundaries/unknown_rtc_"
                "device_provider_candidate-ATTRIBUTION-2026-08.md; first-party "
                "B210/Bravechip ChipletRing authorship is the supported origin). "
                "Under the owner-authorized full reduction (SOURCE-ADMISSION.md, "
                "2026-08-14) the ten-entry family is reconstructed from the "
                "decompilation evidence as independently compiled C in "
                "reconstructed/rtc_device/ with per-function provenance; the "
                "reconstruction is not vendor source. Contract, divergences, "
                "and test mapping: correlation/RTC-DEVICE-REDUCTION-CORRELATION.md."
            ),
        )
    elif entry in APP_SENSOR_ALGORITHM_HEAP_BOUNDARY:
        family, disposition, confidence, basis = \
            SENSOR_ALGORITHM_HEAP_ROUTING[entry]
        if family == "r1_product_specific":
            heap_evidence = (
                "SHA-pinned R1 integrator glue around the Goodix GH3X2X "
                f"goodix_mem/GdMem pool manager: {basis}. The public GH3X2X "
                "SDK header goodix_mem.h declares Gh3x2xPoolIsNotEnough as an "
                "integrator-supplied extern; only this product behavior may "
                "be local, never the vendor allocator it serves."
            )
        elif confidence == "high":
            heap_evidence = (
                "SHA-pinned Goodix GH3X2X goodix_mem/GdMem allocator "
                f"internal: {basis}. Instruction-level comparison against the "
                "Goodix common-DSP library object and the public goodix_mem.h "
                "-1/-2 error contract establish the boundary; the restrictive "
                "binary-only Goodix SDK license bars any local recreation."
            )
        else:
            heap_evidence = (
                "SHA-pinned guarded alloc/free call-site glue inside the "
                f"Goodix GH3X2X gated consumer closure: {basis}. Reached "
                "only from goodix_gh3x2x_candidate bodies and wrapping the "
                "Goodix goodix_mem/GdMem pool manager, it is conservatively "
                "gated with the calling provider; no local substitute is "
                "authorized."
            )
        row.update(
            provider_family=family,
            source_disposition=disposition,
            upstream_symbol=APP_SENSOR_ALGORITHM_HEAP_BOUNDARY[entry],
            confidence=confidence,
            evidence=heap_evidence,
        )
    elif entry in APP_YHM2710_FRONTIER_CANDIDATES:
        row.update(
            provider_family="yhmicros_yhm2710_candidate",
            source_disposition="clean_room_reimplementation_owner_authorized",
            upstream_symbol=APP_YHM2710_FRONTIER_CANDIDATES[entry],
            confidence="high",
            evidence=(
                "SHA-pinned YHM2710 transport/register behavior. Under the "
                "owner-authorized full reduction (SOURCE-ADMISSION.md, "
                "2026-08-14), the complete closure is independently "
                "reconstructed in reconstructed/yhm2710; the reconstruction "
                "is not YHMICROS or Even Realities source."
            ),
        )
    elif entry in APP_YHM2710_STACMD_CANDIDATES:
        row.update(
            provider_family="yhmicros_yhm2710_candidate",
            source_disposition="clean_room_reimplementation_owner_authorized",
            upstream_symbol=APP_YHM2710_STACMD_CANDIDATES[entry],
            confidence="high",
            evidence=(
                "Exact executable closure of the scatter-loaded device_stacmd "
                "operation table and P1.01 wire callback record used by the "
                "YHM2710 power path. The exact vendor source remains unlicensed; "
                "the owner-authorized independent reconstruction is compiled "
                "from reconstructed/yhm2710."
            ),
        )
    elif entry in APP_NORDIC_WDT_ADAPTERS:
        row.update(
            provider_family="r1_nordic_wdt_provider_adapter",
            source_disposition="clean_room_adapter_only_use_nordic_sdk",
            upstream_symbol=APP_NORDIC_WDT_ADAPTERS[entry],
            confidence="high",
            evidence=(
                "SHA-pinned R1 watchdog lifecycle or feed adapter around Nordic "
                "nRF5 SDK 17.1.0 nrfx_wdt. Only the fixed 10-second, priority-6, "
                "single-channel product configuration and scheduler seam are local."
            ),
        )
    elif entry in APP_PROVIDER_GLUE_FUNCTIONS:
        row.update(
            provider_family="r1_provider_configuration_glue",
            source_disposition="clean_room_configuration_only_use_pinned_provider",
            upstream_symbol=APP_PROVIDER_GLUE_FUNCTIONS[entry],
            confidence="high",
            evidence="Recovered R1-specific configuration/call boundary; implementation internals are supplied by the pinned Nordic SDK provider.",
        )
    elif entry in APP_NORDIC_ADAPTERS:
        nordic_adapter_evidence = (
            "SHA-pinned R1 boot reset-reason lifecycle around Nordic nrf_power "
            "RESETREAS get/clear primitives. Only report storage, product decode "
            "dispatch, and provider calls may be local; register access remains "
            "Nordic HAL code."
            if entry == 0x00077E98 else
            "Function-local Nordic SDK control flow with a bounded R1-specific "
            "service, event, or formatting seam; only that product seam is local."
        )
        row.update(
            provider_family="r1_nordic_sdk_provider_adapter",
            source_disposition="clean_room_adapter_only_use_nordic_sdk",
            upstream_symbol=APP_NORDIC_ADAPTERS[entry],
            confidence="high",
            evidence=nordic_adapter_evidence,
        )
    elif entry in APP_INTERNAL_FLASH_ADAPTERS:
        row.update(
            provider_family="r1_internal_flash_provider_adapter",
            source_disposition="clean_room_adapter_only_use_nordic_sdk_and_fal",
            upstream_symbol=APP_INTERNAL_FLASH_ADAPTERS[entry],
            confidence="high",
            evidence=(
                "Recovered R1-specific 36-page internal-flash geometry, callback "
                "serialization, device operation, or FAL-binding seam. Nordic "
                "nrf_fstorage and pinned upstream FAL supply the provider internals; "
                "the generic stock device registry is not recreated."
            ),
        )
    elif entry in APP_ANALOG_ADAPTERS:
        row.update(
            provider_family="r1_analog_provider_adapter",
            source_disposition="clean_room_adapter_only_use_nordic_sdk",
            upstream_symbol=APP_ANALOG_ADAPTERS[entry],
            confidence="high",
            evidence=(
                "Recovered R1-specific ADC record naming, nRF52840 route, startup "
                "settling, sample filtering, or conversion seam. Nordic nrfx_saadc "
                "supplies the driver internals; the generic stock registry is not recreated."
            ),
        )
    elif entry in APP_UNKNOWN_DEVICE_REGISTRY_CANDIDATES:
        row.update(
            provider_family="unknown_generic_device_registry_candidate",
            source_disposition="clean_room_reimplementation_owner_authorized",
            upstream_symbol=APP_UNKNOWN_DEVICE_REGISTRY_CANDIDATES[entry],
            confidence="high",
            evidence=(
                "Complete function-local name-list or operation-table dispatch semantics "
                "identify the stock generic device registry; no attributable source, "
                "provider version, or license exists (2026-08 re-examination: "
                "boundaries/unknown_generic_device_registry_candidate-ATTRIBUTION"
                "-2026-08.md; every fingerprint is globally unique to this firmware "
                "and the registry is B210/Bravechip ChipletRing platform "
                "middleware). Under the owner-authorized full reduction "
                "(SOURCE-ADMISSION.md, 2026-08-14) the forty-entry family is "
                "reconstructed from the decompilation evidence as independently "
                "compiled C in reconstructed/generic_device_registry/ with "
                "per-function provenance; the reconstruction is not vendor "
                "source. Contract, divergences, and test mapping: "
                "correlation/GENERIC-DEVICE-REGISTRY-REDUCTION-CORRELATION.md."
            ),
        )
    elif entry in APP_UNKNOWN_TIME_CALENDAR_CANDIDATES:
        row.update(
            provider_family="unknown_time_calendar_provider_candidate",
            source_disposition="clean_room_reimplementation_owner_authorized",
            upstream_symbol=APP_UNKNOWN_TIME_CALENDAR_CANDIDATES[entry],
            confidence="high",
            evidence=(
                "Complete clock-backend, Unix/Gregorian conversion, timezone, "
                "or local-hour/bucket semantics are recovered and byte-pinned; "
                "no attributable provider source, version, or license exists "
                "(2026-08 re-examination: boundaries/unknown_time_calendar"
                "_provider_candidate-ATTRIBUTION-2026-08.md; the seconds-to-tm "
                "converter matches the old-newlib _mktm_r idiom behaviorally "
                "with no exact public body, and the 1970-2029 validating "
                "inverse converter is unique to this firmware). Under the "
                "owner-authorized full reduction (SOURCE-ADMISSION.md, "
                "2026-08-14) the sixteen-entry family is reconstructed from "
                "the decompilation evidence as independently compiled C in "
                "reconstructed/time_calendar/ with per-function provenance; "
                "the reconstruction is not vendor source. Contract, "
                "divergences, and test mapping: "
                "correlation/TIME-CALENDAR-REDUCTION-CORRELATION.md."
            ),
        )
    elif entry in APP_NORDIC_SYMBOLS:
        row.update(
            provider_family="nordic_nrf5_sdk_17_1_0",
            source_disposition="use_nordic_sdk",
            upstream_symbol=APP_NORDIC_SYMBOLS[entry],
            confidence="high",
            evidence=(
                f"Exact function-local SDK evidence and semantic control flow correlate to "
                f"Nordic SDK 17.1.0 {APP_NORDIC_SOURCES[entry]}::"
                f"{APP_NORDIC_SYMBOLS[entry]}."
            ),
        )
    elif entry in APP_SEGGER_RTT_SYMBOLS:
        row.update(
            provider_family="segger_rtt_6_18a_sdk_bundled",
            source_disposition="use_nordic_sdk_bundled_upstream",
            upstream_symbol=APP_SEGGER_RTT_SYMBOLS[entry],
            confidence="high",
            evidence=(
                "Exact SEGGER RTT 6.18a control-block access and semantic control "
                "flow from the pinned Nordic SDK external/segger_rtt source."
            ),
        )
    elif entry in APP_SEGGER_FPRINTF_SYMBOLS:
        row.update(
            provider_family="segger_fprintf_6_14d_sdk_bundled",
            source_disposition="use_nordic_sdk_bundled_upstream",
            upstream_symbol=APP_SEGGER_FPRINTF_SYMBOLS[entry],
            confidence="high",
            evidence=(
                "Exact SEGGER-derived nrf_fprintf 6.14d formatter control flow "
                "from the pinned Nordic SDK external/fprintf source."
            ),
        )
    elif entry in APP_TOOLCHAIN_RUNTIME_SYMBOLS:
        row.update(
            provider_family="arm_toolchain_runtime",
            source_disposition="use_toolchain_runtime",
            upstream_symbol=APP_TOOLCHAIN_RUNTIME_SYMBOLS[entry],
            confidence="high",
            evidence=(
                "Exact standard C/Arm EABI helper semantics and calling convention; "
                "link the selected toolchain runtime rather than implementing locally."
            ),
        )
    elif entry in APP_TOOLCHAIN_RUNTIME_INTERNALS:
        row.update(
            provider_family="arm_toolchain_runtime",
            source_disposition="use_toolchain_runtime",
            upstream_symbol=APP_TOOLCHAIN_RUNTIME_INTERNALS[entry],
            confidence="high",
            evidence=(
                "Complete runtime-only control flow identifies an Arm C-library "
                "internal; the descriptive role is not an asserted private symbol name. "
                "Use the selected toolchain runtime rather than implementing it locally."
            ),
        )
    elif entry in APP_CMSIS_FREERTOS_SYMBOLS:
        row.update(
            provider_family="arm_cmsis_freertos_10_5_1",
            source_disposition="use_authenticated_upstream_snapshot",
            upstream_symbol=APP_CMSIS_FREERTOS_SYMBOLS[entry],
            confidence="high",
            evidence=(
                "Exact CMSIS-FreeRTOS v10.5.1 control-flow correlation; the ISR "
                "event-flag read/OR behavior distinguishes this revision from v10.4.6."
            ),
        )
    elif entry in APP_FREERTOS_EXACT_SYMBOLS:
        row.update(
            provider_family="freertos_10_5_1_nordic_nrf52_port",
            source_disposition="use_authenticated_upstream_snapshot_and_nordic_port",
            upstream_symbol=APP_FREERTOS_EXACT_SYMBOLS[entry],
            confidence="high",
            evidence=(
                "Exact FreeRTOS-Kernel 10.5.1 core or Nordic nRF52 port function-local control flow; "
                f"compile {APP_FREERTOS_EXACT_SOURCES[entry]} from the authenticated core or pinned SDK port. The product-owned seam "
                "is limited to FreeRTOSConfig tick/tickless and pre-sleep-hook selection."
            ),
        )
    elif entry in APP_CMBACKTRACE_SYMBOLS:
        row.update(
            provider_family="armink_cmbacktrace_1_4_2_compatible",
            source_disposition="use_authenticated_upstream_snapshot",
            upstream_symbol=APP_CMBACKTRACE_SYMBOLS[entry],
            confidence="high",
            evidence=(
                "Function-local control flow matches authenticated Armink "
                "CmBacktrace source in the proven R1-compatible interval "
                "4abadfa0..73714489; exact vendor checkout is not claimed."
            ),
        )
        return row
    elif entry in APP_UNKNOWN_SENSOR_STREAM_CANDIDATES:
        row.update(
            provider_family="unknown_sensor_stream_framework_candidate",
            source_disposition="clean_room_reimplementation_owner_authorized",
            upstream_symbol=APP_UNKNOWN_SENSOR_STREAM_CANDIDATES[entry],
            confidence="high",
            evidence=(
                "SHA-pinned generic named sensor-stream listener registration, "
                "timer dispatch, unregistration, buffer-resize, and rate-retiming "
                "behavior used across product and "
                "provider callers. No attributable source, version, or license "
                "exists (2026-08 re-examination: "
                "boundaries/unknown_sensor_stream_framework_candidate-ATTRIBUTION"
                "-2026-08.md; the MultiTimer library (both generations) is "
                "rejected line-by-line, every distinctive string is globally "
                "unique, and B210/Bravechip ChipletRing platform authorship "
                "stands). Under the owner-authorized full reduction "
                "(SOURCE-ADMISSION.md, 2026-08-14) the thirty-two-entry family "
                "is reconstructed from the decompilation evidence as "
                "independently compiled C in reconstructed/sensor_stream/ "
                "with per-function provenance; the reconstruction is not "
                "vendor source. Contract, divergences, and test mapping: "
                "correlation/SENSOR-STREAM-REDUCTION-CORRELATION.md."
            ),
        )
        return row
    elif entry in APP_CMBACKTRACE_ADAPTERS:
        row.update(
            provider_family="r1_cmbacktrace_provider_adapter",
            source_disposition="clean_room_adapter_only_use_authenticated_provider",
            upstream_symbol=APP_CMBACKTRACE_ADAPTERS[entry],
            confidence="high",
            evidence=(
                "Recovered function combines CmBacktrace behavior with an R1 "
                "exception, logging, formatting, or FreeRTOS integration seam; "
                "only the bounded adapter may be local."
            ),
        )
        return row
    elif entry in APP_TINY_AES_SYMBOLS:
        row.update(
            provider_family="kokke_tiny_aes_c_v1_0_0_compatible",
            source_disposition="use_pinned_upstream",
            upstream_symbol=APP_TINY_AES_SYMBOLS[entry],
            confidence="high",
            evidence=(
                "Exact AES-128 inverse-core function and aggregate call-graph "
                "match to kokke/tiny-AES-c; use pinned v1.0.0 provider source. "
                "The exact original checkout is not claimed."
            ),
        )
        return row
    elif entry in APP_BMA456_SYMBOLS:
        row.update(
            provider_family="bosch_bma456_sensorapi_2_29_0",
            source_disposition="use_pinned_upstream",
            upstream_symbol=APP_BMA456_SYMBOLS[entry],
            confidence="high",
            evidence=(
                "Function-local control flow, bma4_dev offsets, register values, "
                "and error/delay behavior match Bosch BMA456 SensorAPI v2.29.0; "
                "the delay_us null check distinguishes it from v2.24.1."
            ),
        )
        return row
    elif entry in APP_BMA456_ADAPTERS:
        row.update(
            provider_family="r1_bosch_bma456_provider_adapter",
            source_disposition="clean_room_adapter_only_use_pinned_provider",
            upstream_symbol=APP_BMA456_ADAPTERS[entry],
            confidence="high",
            evidence=(
                "Recovered R1 wrapper supplies product logging, configuration, "
                "buffer, or bus/event policy around the pinned Bosch provider; "
                "the Bosch driver body is not reimplemented locally."
            ),
        )
        return row
    elif entry in APP_LIS2DW12_SYMBOLS:
        row.update(
            provider_family="stmicro_lis2dw12_pid_v2_1_0_compatible",
            source_disposition="use_pinned_upstream",
            upstream_symbol=APP_LIS2DW12_SYMBOLS[entry],
            confidence="high",
            evidence=(
                "Function-local register, bitfield, and error-guard control flow "
                "matches ST's LIS2DW12 standard C driver. v2.1.0 is the newest "
                "official release compatible with the recovered mdelay ctx, "
                "guarded INT1 routing, and valued reset setter."
            ),
        )
        return row
    elif entry in APP_LIS2DW12_ADAPTERS:
        row.update(
            provider_family="r1_st_lis2dw12_provider_adapter",
            source_disposition="clean_room_adapter_only_use_pinned_provider",
            upstream_symbol=APP_LIS2DW12_ADAPTERS[entry],
            confidence="high",
            evidence=(
                "Recovered R1 wrapper supplies product logging, fixed setup, "
                "FIFO bounds, identity policy, or bus/event glue around the "
                "pinned ST provider. The LIS2DOC diagnostic name is an R1 label "
                "for the WHO_AM_I 0x44 LIS2DW12 path."
            ),
        )
        return row
    elif entry in APP_MOTION_ADAPTERS:
        row.update(
            provider_family="r1_motion_provider_adapter",
            source_disposition="clean_room_adapter_only_use_licensed_providers",
            upstream_symbol=APP_MOTION_ADAPTERS[entry],
            confidence="high",
            evidence=(
                "Recovered R1 provider selection or common six-byte FIFO sample "
                "normalization around the licensed ST/Bosch paths. The stock "
                "QMA fallback remains unavailable without licensed source."
            ),
        )
        return row

    # A source marker is stronger than a product-behavior classification. The
    # current overlap is FlashDB's internal health append at 0x93744.
    if re.search(r"s__FlashDB__(?:tsl__|utils__)?", block) or "third_party_DB_FlashDB" in block:
        symbol = FLASHDB_SYMBOLS.get(entry, "")
        row.update(
            provider_family="flashdb_2_0_0",
            source_disposition="use_pinned_upstream",
            upstream_symbol=symbol,
            confidence="high" if symbol or "third_party_DB_FlashDB" in block else "medium",
            evidence=(
                "Function-local FlashDB source path/diagnostic plus semantic match to pinned FlashDB 2.0.0."
                if symbol else
                "Function-local FlashDB diagnostic identifies the provider; exact upstream symbol remains unresolved."
            ),
        )
        return row

    # A marker proves provider interaction but not whether the function is a
    # vendor driver or an R1 adapter, so implementation remains blocked.
    for provider, pattern, disposition, evidence in APP_VENDOR_MARKERS:
        if pattern.search(block):
            row.update(
                provider_family=provider,
                source_disposition=disposition,
                upstream_symbol="",
                confidence="candidate",
                evidence=evidence,
            )
            break
    return row


def boot_provider(name: str, evidence: str) -> tuple[str, str]:
    lower_name = name.lower()
    lower_evidence = evidence.lower()
    if any(token in lower_name for token in ("cc310", "crys_", "pka", "sasi_")) or "cryptocell" in lower_evidence:
        return "arm_cryptocell_cc310", "use_nordic_supplied_provider"
    if lower_name.startswith(("pb_", "nanopb_")) or \
            lower_name in {"iter_from_extension", "read_raw_value"} or \
            "nanopb" in lower_evidence:
        return "nanopb", "use_nordic_sdk_bundled_upstream"
    if lower_name.startswith("armcc_") or lower_name in {"memmove", "memset", "strlen", "memcmp", "strncmp"}:
        return "arm_toolchain_runtime", "use_toolchain_runtime"
    nordic_names = {
        "busfault_handler", "cryptocell_irqhandler", "debugmon_handler", "default_handler",
        "hardfault_handler", "memorymanagement_handler", "nmi_handler", "pendsv_handler",
        "reset_handler", "rtc2_irqhandler", "svc_handler", "swi0_egu0_irqhandler",
        "swi2_egu2_irqhandler", "swi2_egu2_irqhandler_vector", "systick_handler",
        "usagefault_handler", "ble_srv_is_notification_enabled", "crc32_compute",
        "event_send", "nvmc_wait", "on_data_obj_execute_request_sched",
        "sdh_request_observer_notify", "sdh_state_observer_notify", "settings_write",
        "timer_activate", "update_data_size_get",
    }
    if lower_name.startswith(("nrf_", "app_util_")) or lower_name in nordic_names:
        return "nordic_nrf5_sdk_17_1_0", "use_nordic_sdk"
    return "unclassified", "investigate_before_implementing"


BOOT_NORDIC_EXACT_SYMBOLS = {
    0x000F8218: "nrf_atfifo_wspace_req",
    0x000F8250: "nrf_atfifo_wspace_close",
    0x000F8262: "nrf_atfifo_rspace_req",
    0x000F829C: "nrf_atfifo_rspace_close",
    0x000F82AE: "nrf_atfifo_space_clear",
    0x000F9A10: "SystemInit",
    0x000F9C64: "__sd_nvic_app_accessible_irq",
    0x000F9C88: "addr_is_aligned32",
    0x000F9C94: "addr_is_within_bounds",
    0x000F9D44: "advertising_start",
    0x000F9DC4: "app_error_handler_bare",
    0x000F9DC8: "app_sched_event_put",
    0x000F9E68: "app_sched_execute",
    0x000F9EA8: "app_sched_init",
    0x000F9F9C: "ble_dfu_init",
    0x000FA060: "ble_dfu_req_handler_callback",
    0x000FA118: "ble_dfu_transport_close",
    0x000FA178: "ble_dfu_transport_init",
    0x000FA210: "ble_evt_handler",
    0x000FA3F0: "boot_validate",
    0x000FA400: "boot_validation_crc",
    0x000FA40C: "boot_validation_extract",
    0x000FA4A4: "bootloader_reset",
    0x000FA64C: "cmd_response_offset_and_crc_set",
    0x000FA698: "crc_ok",
    0x000FA6B8: "crypto_init",
    0x000FA908: "nrf_bootloader_dfu_observer",
    0x000FA950: "nrf_dfu_observer",
    0x000FA978: "__NVIC_SystemReset",
    0x000FAABA: "ext_err_code_handle",
    0x000FAAC8: "ext_error_get",
    0x000FAAD8: "ext_error_set",
    0x000FAA30: "nrf_fstorage_nvmc_event_send",
    0x000FAAFC: "fw_hash_ok",
    0x000FAC3C: "image_copy",
    0x000FAD38: "is_major_softdevice_update",
    0x000FADC8: "main",
    0x000FADF8: "nrf_atfifo_clear",
    0x000FAE2E: "nrf_atfifo_item_alloc",
    0x000FAE44: "nrf_atfifo_item_free",
    0x000FAE5A: "nrf_atfifo_item_get",
    0x000FAE70: "nrf_atfifo_item_put",
    0x000FAE86: "nrf_atomic_flag_clear",
    0x000FB5C4: "nrf_dfu_command_req",
    0x000FB658: "nrf_dfu_data_req",
    0x000FB6CC: "nrf_dfu_flash_erase",
    0x000FB6F8: "nrf_dfu_flash_store",
    0x000FB710: "nrf_dfu_init",
    0x000FB758: "nrf_dfu_mbr_init_sd",
    0x000FB7D8: "nrf_dfu_req_handler_req_process",
    0x000FB8E4: "nrf_dfu_settings_additional_erase",
    0x000FB918: "nrf_dfu_settings_adv_name_copy",
    0x000FB988: "nrf_dfu_settings_backup",
    0x000FB9B0: "nrf_dfu_settings_progress_reset",
    0x000FBAAC: "nrf_dfu_settings_write",
    0x000FB73C: "nrf_dfu_init_user",
    0x000FBB00: "nrf_dfu_softdevice_start_address",
    0x000FBC28: "nrf_dfu_validation_init",
    0x000FBC4C: "nrf_dfu_validation_init_cmd_append",
    0x000FBCC8: "nrf_dfu_validation_init_cmd_execute",
    0x000FBD5C: "nrf_dfu_validation_init_cmd_present",
    0x000FBED4: "nrf_fstorage_erase",
    0x000FBF90: "nrf_fstorage_sys_evt_handler",
    0x000FC030: "nrf_fstorage_write",
    0x000FC070: "nrf_nvmc_page_erase",
    0x000FC0A0: "nrf_nvmc_write_word",
    0x000FC0D0: "nrf_nvmc_write_words",
    0x000FC134: "nrf_sdh_ble_default_cfg_set",
    0x000FC1D0: "nrf_sdh_ble_enable",
    0x000FC1E4: "nrf_sdh_soc_evts_poll",
    0x000FC244: "nrf_sdh_disable_request",
    0x000FC298: "nrf_sdh_enable_request",
    0x000FC330: "nrf_sdh_is_enabled",
    0x000FC394: "nrf_section_iter_init",
    0x000FC468: "on_ctrl_pt_write",
    0x000FC654: "app_error_fault_handler",
    0x000FC684: "on_flash_write",
    0x000FC690: "on_rw_authorize_req",
    0x000FCFF0: "postvalidate",
    0x000FD0F0: "queue_free",
    0x000FD104: "queue_process",
    0x000FD1A0: "queue_start",
    0x000FD242: "response_crc_add",
    0x000FD264: "response_send",
    0x000FD2F4: "sd_req_check",
    0x000FD338: "sd_req_ok",
    0x000FD3FC: "settings_backup",
    0x000FD410: "settings_crc_get",
    0x000FD46C: "softdevice_evt_irq_disable",
    0x000FD4AC: "softdevices_evt_irq_enable",
    0x000FD504: "stored_init_cmd_decode",
    0x000FD62C: "timer_init",
    0x000FD6A0: "timer_start",
    0x000FD6BC: "timer_stop",
    0x000FD6D0: "uint32_encode",
    0x000FD76C: "verify_context",
    0x000FD78C: "wdt_feed",
    0x000FD7C8: "wdt_feed_timer_handler",
    0x000FD8B0: "nrfx_coredep_delay_machine_code_dfu_timers",
    0x000FDAA0: "nrfx_coredep_delay_machine_code_ble_dfu",
}


def classify_bootloader(raw: dict[str, str], names: dict[int, dict[str, str]]) -> dict[str, str]:
    row = base_row("bootloader", raw)
    entry = int(raw["entry"], 16)
    named = names.get(entry)
    if not named:
        return row
    applied = named["applied_name"]
    row["recovered_name"] = applied
    if named["name_kind"] == "synthetic_descriptive":
        row["evidence"] = "Synthetic structural name only; it is not provider or authorship evidence. " + named["evidence"]
        return row

    exact_nordic = BOOT_NORDIC_EXACT_SYMBOLS.get(entry)
    if exact_nordic == applied:
        row.update(
            provider_family="nordic_nrf5_sdk_17_1_0",
            source_disposition="use_nordic_sdk",
            upstream_symbol=applied,
            confidence=named["confidence"],
            evidence=named["evidence"],
        )
        return row

    provider, disposition = boot_provider(applied, named["evidence"])
    if provider != "unclassified":
        row.update(
            provider_family=provider,
            source_disposition=disposition,
            upstream_symbol=applied,
            confidence=named["confidence"],
            evidence=named["evidence"],
        )
        return row

    if applied in {"main", "gap_params_init", "dfu_advertising_name_get", "bootloader_adv_name_record_valid"}:
        row.update(
            provider_family="r1_product_specific",
            source_disposition="clean_room_behavior_only_security_preserving",
            upstream_symbol=applied,
            confidence=named["confidence"],
            evidence=named["evidence"] + "; product integration classification, security behavior must remain fail-closed.",
        )
    else:
        row.update(
            upstream_symbol=applied,
            confidence=named["confidence"],
            evidence="Recovered name is accepted, but provider ownership is unresolved. " + named["evidence"],
        )
    return row


def load_boot_names() -> dict[int, dict[str, str]]:
    with (BOOT_RECON / "function-names.csv").open(newline="") as stream:
        return {int(row["entry"], 16): row for row in csv.DictReader(stream)}


def build() -> tuple[list[dict[str, str]], dict[str, object]]:
    blocks = read_decompiler_blocks("application")
    app_raw = read_functions("application")
    boot_raw = read_boot_reconstruction_functions()
    names = load_boot_names()
    app_entries = {int(raw["entry"], 16) for raw in app_raw}
    supplement_symbols = {
        **APP_PRODUCT_FUNCTIONS,
        **APP_NORDIC_SYMBOLS,
        **FLASHDB_SYMBOLS,
        **APP_SEGGER_RTT_SYMBOLS,
        **APP_SEGGER_FPRINTF_SYMBOLS,
        **APP_TOOLCHAIN_RUNTIME_SYMBOLS,
        **APP_TOOLCHAIN_RUNTIME_INTERNALS,
        **{
            entry: "gomore_audit_" + "_".join(groups)
            for entry, groups in APP_GOMORE_AUDIT_FUNCTIONS.items()
        },
        **APP_GOMORE_ADAPTERS,
        **APP_MOTION_ADAPTERS,
        **APP_QMA6100_ADAPTERS,
        **APP_INTERNAL_FLASH_ADAPTERS,
        **APP_ANALOG_ADAPTERS,
        **APP_NORDIC_SAADC_DRIVER_SYMBOLS,
        **APP_NORDIC_CMSIS_ADAPTERS,
        **APP_DEVICE_REGISTRY_CONFIGURATION_ADAPTERS,
        **APP_UNKNOWN_SOFTWARE_TWI_CANDIDATES,
        **APP_UNKNOWN_RTC_DEVICE_CANDIDATES,
        **APP_UNKNOWN_QUANTIZED_NEURAL_RUNTIME_CANDIDATES,
        **APP_SENSOR_ALGORITHM_HEAP_BOUNDARY,
        **APP_YHM2710_STACMD_CANDIDATES,
        **APP_NORDIC_WDT_ADAPTERS,
        **APP_GOODIX_EXACT_CANDIDATES,
    }
    supplemental_raw = [
        {
            "entry": f"0x{entry:08x}",
            "end": (
                f"0x{entry + APP_MANUAL_SUPPLEMENT_EXTENTS[entry] - 1:08x}"
                if entry in APP_MANUAL_SUPPLEMENT_EXTENTS else ""
            ),
            "size": str(APP_MANUAL_SUPPLEMENT_EXTENTS.get(entry, "")),
            "name": symbol,
            "inventory_source": "manual_provenance_supplement",
        }
        for entry, symbol in supplement_symbols.items()
        if entry not in app_entries
    ]
    all_app_raw = sorted(app_raw + supplemental_raw, key=lambda raw: int(raw["entry"], 16))
    rows = [classify_application(raw, blocks.get(int(raw["entry"], 16), "")) for raw in all_app_raw]
    rows.extend(classify_bootloader(raw, names) for raw in boot_raw)

    keys = [(row["image"], row["entry"]) for row in rows]
    if len(keys) != len(set(keys)):
        raise ValueError("duplicate image/entry in ownership ledger")
    expected = len(app_raw) + len(supplemental_raw) + len(boot_raw)
    if len(rows) != expected:
        raise ValueError(f"expected {expected} functions, generated {len(rows)}")

    providers = Counter(row["provider_family"] for row in rows)
    dispositions = Counter(row["source_disposition"] for row in rows)
    summary: dict[str, object] = {
        "schema_version": 1,
        "function_count": len(rows),
        "image_counts": dict(Counter(row["image"] for row in rows)),
        "ghidra_inventory_count": len(app_raw) + len(boot_raw),
        "manual_provenance_supplement_count": len(supplemental_raw),
        "provider_counts": dict(sorted(providers.items())),
        "disposition_counts": dict(sorted(dispositions.items())),
        "unclassified_count": providers["unclassified"],
        "policy": "Unclassified and vendor-candidate functions are blocked from implementation until ownership is resolved.",
        "inputs": {},
    }
    inputs = [
        DECOMP / "application" / "functions.csv",
        DECOMP / "application" / "decompiler-output.c",
        BOOT_RECON / "functions.csv",
        BOOT_RECON / "function-names.csv",
    ]
    summary_inputs = summary["inputs"]
    assert isinstance(summary_inputs, dict)
    for path in inputs:
        summary_inputs[str(path.relative_to(ROOT))] = hashlib.sha256(path.read_bytes()).hexdigest()
    return rows, summary


def render_csv(rows: list[dict[str, str]]) -> bytes:
    import io
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=FIELDS, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return stream.getvalue().encode()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="fail if generated files differ")
    args = parser.parse_args()
    rows, summary = build()
    expected_csv = render_csv(rows)
    expected_summary = (json.dumps(summary, indent=2, sort_keys=True) + "\n").encode()
    if args.check:
        if any(not path.exists() or path.read_bytes() != expected_csv
               for path in (OUTPUT, REFERENCE_OUTPUT)):
            raise SystemExit("FUNCTION-OWNERSHIP.csv is stale; run this script without --check")
        if any(not path.exists() or path.read_bytes() != expected_summary
               for path in (SUMMARY, REFERENCE_SUMMARY)):
            raise SystemExit("FUNCTION-OWNERSHIP-SUMMARY.json is stale; run this script without --check")
    else:
        for path in (OUTPUT, REFERENCE_OUTPUT):
            path.write_bytes(expected_csv)
        for path in (SUMMARY, REFERENCE_SUMMARY):
            path.write_bytes(expected_summary)
    print(f"verified {len(rows)} functions; {summary['unclassified_count']} remain unclassified")


if __name__ == "__main__":
    main()
