#!/usr/bin/env python3
"""Verify the clean-room R1 compatibility core and its evidence-pinned invariants."""

from __future__ import annotations

import csv
import hashlib
import json
import os
import re
import subprocess
from collections import Counter
from pathlib import Path

# --- evidence modules live in tools/evidence/ ---
import sys as _sys
from pathlib import Path as _Path

_sys.path.insert(0, str(_Path(__file__).resolve().parent / "evidence"))

from summarize_r1_software_twi_engines import (
    SOFTWARE_TWI_FUNCTIONS,
    summarize as summarize_software_twi,
)
from summarize_r1_rtc_device_boundary import (
    RTC_DEVICE_FUNCTIONS,
    summarize as summarize_rtc_device,
)
from summarize_r1_pmic_transport import (
    DEFAULT_BASE as PMIC_DEFAULT_BASE,
    DEFAULT_SCATTER_LENGTH as PMIC_DEFAULT_SCATTER_LENGTH,
    DEFAULT_SCATTER_RUNTIME as PMIC_DEFAULT_SCATTER_RUNTIME,
    DEFAULT_SCATTER_SOURCE as PMIC_DEFAULT_SCATTER_SOURCE,
    YHM2710_STACMD_FUNCTIONS,
    summarize as summarize_pmic_transport,
)
from summarize_r1_watchdog_device_boundary import (
    WATCHDOG_DEVICE_FUNCTIONS,
    summarize as summarize_watchdog_device,
)
from summarize_r1_sensor_algorithm_heap import (
    SENSOR_ALGORITHM_HEAP_FUNCTIONS,
    SENSOR_ALGORITHM_HEAP_ROUTING,
    summarize as summarize_sensor_algorithm_heap,
)
from summarize_r1_gomore_initializer_boundary import (
    GOMORE_INITIALIZER_FUNCTIONS,
    summarize as summarize_gomore_initializer,
)
from summarize_r1_goodix_integrity_boundary import (
    GOODIX_INTEGRITY_FUNCTIONS,
    GOODIX_INTEGRITY_NEW_FUNCTIONS,
    INTEGRITY_TABLE_SHA256,
    INTEGRITY_TABLE_WORDS,
    summarize as summarize_goodix_integrity,
)
from summarize_r1_freertos_static_memory import (
    FREERTOS_STATIC_MEMORY_FUNCTIONS,
    summarize as summarize_freertos_static_memory,
)
from summarize_r1_freertos_stack_overflow import (
    FREERTOS_STACK_OVERFLOW_FUNCTIONS,
    summarize as summarize_freertos_stack_overflow,
)
from summarize_r1_nordic_system_init import (
    NORDIC_SYSTEM_INIT_FUNCTIONS,
    summarize as summarize_nordic_system_init,
)
from summarize_r1_nordic_twim_completeness import (
    NORDIC_TWIM_COMPLETENESS_FUNCTIONS,
    summarize as summarize_nordic_twim_completeness,
)
from summarize_r1_nordic_gatt_cache_closure import (
    NORDIC_GATT_CACHE_CLOSURE_FUNCTIONS,
    summarize as summarize_nordic_gatt_cache_closure,
)
from summarize_r1_nordic_ble_static_helpers import (
    NORDIC_BLE_STATIC_HELPER_FUNCTIONS,
    summarize as summarize_nordic_ble_static_helpers,
)
from summarize_r1_nordic_advertising_closure import (
    NORDIC_ADVERTISING_FUNCTIONS,
    summarize as summarize_nordic_advertising_closure,
)
from summarize_r1_nordic_buttonless_dfu_closure import (
    NORDIC_BUTTONLESS_DFU_FUNCTIONS,
    summarize as summarize_nordic_buttonless_dfu_closure,
)
from summarize_r1_nordic_power_management_closure import (
    NORDIC_POWER_MANAGEMENT_FUNCTIONS,
    summarize as summarize_nordic_power_management_closure,
)
from summarize_r1_reset_trace_closure import (
    R1_RESET_TRACE_FUNCTIONS,
    function_bytes as reset_trace_function_bytes,
    summarize as summarize_r1_reset_trace_closure,
)
from summarize_r1_reset_reason_closure import (
    R1_RESET_REASON_FUNCTIONS,
    summarize as summarize_r1_reset_reason_closure,
)
from summarize_r1_goodix_nadt_boundary import (
    GOODIX_NADT_FUNCTIONS,
    summarize as summarize_r1_goodix_nadt_boundary,
)
from summarize_r1_goodix_hr_boundary import (
    GOODIX_HR_FUNCTIONS,
    summarize as summarize_r1_goodix_hr_boundary,
)
from summarize_r1_goodix_hr_init_boundary import (
    GOODIX_HR_INIT_FUNCTIONS,
    summarize as summarize_r1_goodix_hr_init_boundary,
)
from summarize_r1_goodix_hrv_boundary import (
    GOODIX_HRV_FUNCTIONS,
    summarize as summarize_r1_goodix_hrv_boundary,
)
from summarize_r1_goodix_channel_decoder import (
    GOODIX_CHANNEL_DECODER_FUNCTIONS,
    summarize as summarize_r1_goodix_channel_decoder,
)
from summarize_r1_goodix_nadt_quality import (
    GOODIX_NADT_QUALITY_FUNCTIONS,
    summarize as summarize_r1_goodix_nadt_quality,
)
from summarize_r1_goodix_nadt_peak_mask import (
    GOODIX_NADT_PEAK_MASK_FUNCTIONS,
    summarize as summarize_r1_goodix_nadt_peak_mask,
)
from summarize_r1_goodix_nadt_accumulation import (
    GOODIX_NADT_ACCUMULATION_FUNCTIONS,
    summarize as summarize_r1_goodix_nadt_accumulation,
)
from summarize_r1_goodix_register_profile import (
    GOODIX_REGISTER_PROFILE_FUNCTIONS,
    summarize as summarize_r1_goodix_register_profile,
)
from summarize_r1_goodix_spo2_dlcom_boundary import (
    GOODIX_SPO2_DLCOM_ALL_FUNCTIONS,
    summarize as summarize_r1_goodix_spo2_dlcom_boundary,
)
from summarize_r1_connection_control import (
    R1_CONNECTION_CONTROL_FUNCTIONS,
    summarize as summarize_r1_connection_control,
)
from summarize_r1_peer_manager_event_policy import (
    R1_PEER_MANAGER_EVENT_FUNCTIONS,
    summarize as summarize_r1_peer_manager_event_policy,
)
from summarize_r1_touch_slider_closure import (
    R1_TOUCH_SLIDER_FUNCTIONS,
    summarize as summarize_r1_touch_slider_closure,
)
from summarize_r1_nv_recovery_closure import (
    R1_NV_RECOVERY_FUNCTIONS,
    summarize as summarize_r1_nv_recovery_closure,
)
from summarize_r1_nv_compiled_restore import (
    R1_NV_COMPILED_RESTORE_FUNCTIONS,
    summarize as summarize_r1_nv_compiled_restore,
)
from summarize_r1_health_daily_test import (
    R1_HEALTH_DAILY_TEST_FUNCTIONS,
    summarize as summarize_r1_health_daily_test,
)
from summarize_r1_gomore_neural_runtime import (
    GOMORE_NEURAL_RUNTIME_FUNCTIONS,
    summarize as summarize_r1_gomore_neural_runtime,
)
from summarize_r1_gomore_sleep_graphs import (
    GOMORE_SLEEP_GRAPH_FUNCTIONS,
    summarize as summarize_r1_gomore_sleep_graphs,
)
from summarize_r1_gomore_activity_state_classifier import (
    GOMORE_ACTIVITY_STATE_FUNCTIONS,
    summarize as summarize_r1_gomore_activity_state_classifier,
)
from summarize_r1_gomore_energy_model import (
    GOMORE_ENERGY_MODEL_FUNCTIONS,
    summarize as summarize_r1_gomore_energy_model,
)
from summarize_r1_gomore_iir_designer import (
    GOMORE_IIR_DESIGNER_FUNCTIONS,
    summarize as summarize_r1_gomore_iir_designer,
)
from summarize_r1_gomore_auth_parser import (
    GOMORE_AUTH_PARSER_FUNCTIONS,
    summarize as summarize_r1_gomore_auth_parser,
)
from summarize_r1_gomore_sleep_stage_statistics import (
    GOMORE_SLEEP_STAGE_STATISTICS_FUNCTIONS,
    summarize as summarize_r1_gomore_sleep_stage_statistics,
)
from summarize_r1_structured_log_cache import (
    R1_STRUCTURED_LOG_FUNCTIONS,
    summarize as summarize_r1_structured_log_cache,
)
from summarize_r1_log_bin_writer import (
    R1_LOG_BIN_WRITER_FUNCTIONS,
    summarize as summarize_r1_log_bin_writer,
)
from summarize_r1_hrv_sync_flush import (
    R1_HRV_SYNC_FLUSH_FUNCTIONS,
    summarize as summarize_r1_hrv_sync_flush,
)
from summarize_r1_hr_sync_flush import (
    R1_HR_SYNC_FLUSH_FUNCTIONS,
    summarize as summarize_r1_hr_sync_flush,
)
from summarize_r1_spo2_sync_flush import (
    R1_SPO2_SYNC_FLUSH_FUNCTIONS,
    summarize as summarize_r1_spo2_sync_flush,
)
from summarize_r1_touch_task_dispatcher import (
    R1_TOUCH_TASK_DISPATCHER_FUNCTIONS,
    summarize as summarize_r1_touch_task_dispatcher,
)
from summarize_r1_sensor_stream_unregister import (
    SENSOR_STREAM_UNREGISTER_FUNCTIONS,
    summarize as summarize_r1_sensor_stream_unregister,
)
from summarize_r1_sensor_stream_register import (
    SENSOR_STREAM_REGISTER_FUNCTIONS,
    summarize as summarize_r1_sensor_stream_register,
)
from summarize_r1_sensor_stream_dispatch import (
    SENSOR_STREAM_DISPATCH_FUNCTIONS,
    summarize as summarize_r1_sensor_stream_dispatch,
)
from summarize_r1_legacy_command_dispatch import (
    OPCODE_HANDLERS as R1_LEGACY_COMMAND_OPCODE_HANDLERS,
    R1_LEGACY_COMMAND_DISPATCH_FUNCTIONS,
    summarize as summarize_r1_legacy_command_dispatch,
)
from summarize_r1_validated_sleep_delivery import (
    R1_VALIDATED_SLEEP_DELIVERY_FUNCTIONS,
    summarize as summarize_r1_validated_sleep_delivery,
)
from summarize_r1_quantized_pooling_boundary import (
    QUANTIZED_POOLING_RUNTIME_FUNCTIONS,
    summarize as summarize_r1_quantized_pooling_boundary,
)
from summarize_r1_connection_role_assignment import (
    R1_CONNECTION_ROLE_ASSIGNMENT_FUNCTIONS,
    summarize as summarize_r1_connection_role_assignment,
)
from summarize_r1_eus_rx_reassembly import (
    R1_EUS_RX_REASSEMBLY_FUNCTIONS,
    summarize as summarize_r1_eus_rx_reassembly,
)
from summarize_r1_bae8_event_router import (
    R1_BAE8_EVENT_ROUTER_FUNCTIONS,
    summarize as summarize_r1_bae8_event_router,
)
from summarize_r1_ati_calibration_command import (
    R1_ATI_CALIBRATION_COMMAND_FUNCTIONS,
    summarize as summarize_r1_ati_calibration_command,
)
from summarize_r1_battery_runtime_service import (
    R1_BATTERY_RUNTIME_SERVICE_FUNCTIONS,
    summarize as summarize_r1_battery_runtime_service,
)
from summarize_r1_hrv_flash_merge import R1_HRV_FLASH_MERGE_FUNCTIONS
from summarize_r1_scalar_health_flash_merge import (
    R1_SCALAR_HEALTH_FLASH_MERGE_FUNCTIONS,
    summarize as summarize_r1_scalar_health_flash_merge,
)
from summarize_r1_hrv_timing_start import (
    R1_HRV_TIMING_START_FUNCTIONS,
    summarize as summarize_r1_hrv_timing_start,
)
from summarize_r1_hrv_ram_cache_merge import (
    R1_HRV_RAM_CACHE_MERGE_FUNCTIONS,
    summarize as summarize_r1_hrv_ram_cache_merge,
)
from summarize_r1_scalar_health_ram_cache_merge import (
    R1_SCALAR_HEALTH_RAM_CACHE_MERGE_FUNCTIONS,
    summarize as summarize_r1_scalar_health_ram_cache_merge,
)
from summarize_r1_protocol_response import (
    R1_PROTOCOL_RESPONSE_FUNCTIONS,
    summarize as summarize_r1_protocol_response,
)
from summarize_r1_export_state_machine import (
    R1_EXPORT_STATE_MACHINE_FUNCTIONS,
    summarize as summarize_r1_export_state_machine,
)
from summarize_r1_frontier_35x import (
    ALL_FUNCTIONS as R1_FRONTIER_35X_FUNCTIONS,
    summarize as summarize_r1_frontier_35x,
)
from summarize_r1_frontier_334_342 import (
    ALL_FUNCTIONS as R1_FRONTIER_334_342_FUNCTIONS,
    summarize as summarize_r1_frontier_334_342,
)
from summarize_r1_frontier_314_328 import (
    ALL_FUNCTIONS as R1_FRONTIER_314_328_FUNCTIONS,
    summarize as summarize_r1_frontier_314_328,
)
from summarize_r1_frontier_280_308 import (
    ALL_FUNCTIONS as R1_FRONTIER_280_308_FUNCTIONS,
    summarize as summarize_r1_frontier_280_308,
)
from summarize_r1_frontier_264_274 import (
    ALL_FUNCTIONS as R1_FRONTIER_264_274_FUNCTIONS,
    summarize as summarize_r1_frontier_264_274,
)
from summarize_r1_frontier_256_262 import (
    ALL_FUNCTIONS as R1_FRONTIER_256_262_FUNCTIONS,
    summarize as summarize_r1_frontier_256_262,
)
from summarize_r1_frontier_230_248 import (
    ALL_FUNCTIONS as R1_FRONTIER_230_248_FUNCTIONS,
    SHARED_QUANTIZED_FRONTIER_230_248_FUNCTIONS,
    summarize as summarize_r1_frontier_230_248,
)
from summarize_r1_frontier_224_230 import (
    ALL_FUNCTIONS as R1_FRONTIER_224_230_FUNCTIONS,
    SHARED_QUANTIZED_FRONTIER_224_230_FUNCTIONS,
    summarize as summarize_r1_frontier_224_230,
)
from summarize_r1_frontier_212_222 import (
    ALL_FUNCTIONS as R1_FRONTIER_212_222_FUNCTIONS,
    summarize as summarize_r1_frontier_212_222,
)
from summarize_r1_frontier_204_210 import (
    ALL_FUNCTIONS as R1_FRONTIER_204_210_FUNCTIONS,
    SHARED_TENSOR_FRONTIER_204_210_FUNCTIONS,
    summarize as summarize_r1_frontier_204_210,
)
from summarize_r1_frontier_128_202 import (
    ALL_FUNCTIONS as R1_FRONTIER_128_202_FUNCTIONS,
    summarize as summarize_r1_frontier_128_202,
)
from summarize_r1_frontier_64_127 import (
    ALL_FUNCTIONS as R1_FRONTIER_64_127_FUNCTIONS,
    summarize as summarize_r1_frontier_64_127,
)
from summarize_r1_frontier_32_63 import (
    ALL_FUNCTIONS as R1_FRONTIER_32_63_FUNCTIONS,
    summarize as summarize_r1_frontier_32_63,
)
from summarize_r1_frontier_sub32 import (
    ALL_FUNCTIONS as R1_FRONTIER_LT32_FUNCTIONS,
    summarize as summarize_r1_frontier_sub32,
)
from summarize_r1_frontier_final53 import (
    ALL_FUNCTIONS as R1_FRONTIER_FINAL53_FUNCTIONS,
    summarize as summarize_r1_frontier_final53,
)
from summarize_r1_delayed_event_timer import (
    R1_DELAYED_EVENT_TIMER_FUNCTIONS,
    summarize as summarize_r1_delayed_event_timer,
)
from summarize_r1_pmic_charge_event import (
    R1_PMIC_CHARGE_EVENT_FUNCTIONS,
    summarize as summarize_r1_pmic_charge_event,
)
from summarize_r1_pmic_charged_notification import (
    R1_PMIC_CHARGED_NOTIFICATION_FUNCTIONS,
    summarize as summarize_r1_pmic_charged_notification,
)
from summarize_r1_iqs7211e_ati_audit import (
    R1_IQS7211E_ATI_AUDIT_FUNCTIONS,
    summarize as summarize_r1_iqs7211e_ati_audit,
)
from summarize_r1_ble_tx_queue_dispatch import (
    R1_BLE_TX_QUEUE_FUNCTIONS,
    summarize as summarize_r1_ble_tx_queue_dispatch,
)
from summarize_r1_freertos_kernel_version import (
    FREERTOS_VERSION_FUNCTIONS,
    summarize as summarize_freertos_kernel_version,
)
from summarize_r1_resolved_thunks import (
    RESOLVED_THUNKS,
    summarize as summarize_resolved_thunks,
)


ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT / "."
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


def require(path: Path, marker: str) -> None:
    text = path.read_text()
    if marker not in text:
        raise AssertionError(f"missing {marker!r} in {path.relative_to(ROOT)}")


def parse_number(header: Path, name: str) -> int:
    match = re.search(rf"^#define {re.escape(name)} (\d+)(?:[uU])?$",
                      header.read_text(), re.MULTILINE)
    if match is None:
        raise AssertionError(f"missing numeric define {name}")
    return int(match.group(1))


def recovered_application_bytes() -> bytes:
    include = (ROOT / "research" / "decompilation" / "rebuild" /
               "application.bytes.inc").read_text()
    return bytes(int(value, 16) for value in re.findall(r"0x([0-9a-fA-F]{2})", include))


# Goodix GH3X2X entries attributed to the pinned public democode
# (goodix-gh3x2x-democode @ 2c0034a2); mirrors the generator tables.
goodix_democode_symbols = {
    0x00029C98: ("GH32x2xMedSel", "high"),
    0x00029CC0: ("GH3X2XDrvConfigInit", "high"),
    0x00029CDC: ("GH3X2X_AdtAlgorithmResultReport", "high"),
    0x00029D0A: ("GH3X2X_AgcGetExtremum", "high"),
    0x00029D34: ("GH3X2X_AgcGetThreshold", "high"),
    0x00029D58: ("GH3x2xAgcInfoUpdate", "high"),
    0x00029D5C: ("GH3X2X_AgcSubChnlGainAdj", "high"),
    0x00029E8C: ("GH3X2X_AlgoCalculate", "high"),
    0x00029F88: ("GH3X2X_AlgoChnlMapInit", "high"),
    0x00029F9C: ("Gh3x2xDemoStopAlgoInner", "high"),
    0x0002A090: ("GH3X2X_AlgoMemConfig", "high"),
    0x0002A0F4: ("GH3X2X_AlgoVersion", "high"),
    0x0002A198: ("GH3X2X_CheckChipModel", "high"),
    0x0002A1F8: ("GH3X2X_ClearDivZeroFlag", "high"),
    0x0002A204: ("GH3X2X_ClearSoftEvent", "high"),
    0x0002A214: ("GH3X2X_CommunicateConfirm", "high"),
    0x0002A266: ("GH3X2X_DecodeRegCfgArr", "high"),
    0x0002A2AC: ("GH3X2X_DelayUs", "high"),
    0x0002A31C: ("GH3X2X_DumpModeSet", "high"),
    0x0002A328: ("GH3X2X_EnterLowPowerMode", "high"),
    0x0002A380: ("GH3X2X_ExitLowPowerMode", "high"),
    0x0002A474: ("GH3X2X_FifoControlInit", "high"),
    0x0002A488: ("GH3X2X_FifoWatermarkThrConfig", "high"),
    0x0002A4B4: ("GH3X2X_FunctionStart", "high"),
    0x0002A508: ("GH3X2X_FunctionStop", "high"),
    0x0002A540: ("GH3X2X_GetAlgoMemStatus", "high"),
    0x0002A550: ("GH3X2X_GetConfigFuncMode", "high"),
    0x0002A55C: ("GH3X2X_GetDemoVersion", "high"),
    0x0002A598: ("GH3X2X_GetDriverLibVersion", "high"),
    0x0002A5D0: ("GH3X2X_GetIrqStatus", "high"),
    0x0002A5EC: ("GH3X2X_GetRegBitField", "high"),
    0x0002A604: ("GH3X2X_GetSoftEvent", "high"),
    0x0002A614: ("GH3X2X_GetVirtualRegVersion", "high"),
    0x0002A630: ("GH3X2X_HbaAlgoChnlMapDefultSet", "high"),
    0x0002A658: ("GH3X2X_HrAlgorithmResultReport", "high"),
    0x0002A65A: ("GH3X2X_HrvAlgorithmResultReport", "high"),
    0x0002A754: ("GH3X2X_Init", "high"),
    0x0002A810: ("GH3x2xAgcChnlInfoInit_veneer", "high"),
    0x0002A814: ("GH3X2X_LedAgcPramWrite", "high"),
    0x0002A84C: ("GH3X2X_LedAgcProcess", "high"),
    0x0002A86C: ("GH3X2X_LedAgcReset", "high"),
    0x0002A8DC: ("GH3X2X_LoadNewRegConfigArr", "high"),
    0x0002A968: ("GH3X2X_Memcpy", "high"),
    0x0002A99E: ("GH3X2X_Memset", "high"),
    0x0002A9EC: ("GH3X2X_ReadFifo", "high"),
    0x0002AA10: ("GH3X2X_ReadFifodata", "high"),
    0x0002AA74: ("GH3X2X_ReadReg", "high"),
    0x0002AA98: ("GH3X2X_ReadRegBitField", "high"),
    0x0002AAD0: ("GH3X2X_RegisterDelayUsCallback", "high"),
    0x0002AADC: ("GH3X2X_RegisterHookFunc", "high"),
    0x0002AAF8: ("GH3X2X_RegisterI2cOperationFunc", "high"),
    0x0002ABA4: ("GH3X2X_ResetHardAdt", "high"),
    0x0002ABDC: ("GH3X2X_SendCmd", "high"),
    0x0002ABFC: ("GH3X2X_SetChipSleepFlag", "high"),
    0x0002AC10: ("GH3X2X_SetConfigFuncMode", "high"),
    0x0002AC1C: ("GH3X2X_SetMaxNumWhenReadFifo", "high"),
    0x0002AC30: ("GH3X2X_SetSoftEvent", "high"),
    0x0002AC40: ("GH3X2X_SlotEnRegSet", "high"),
    0x0002AC4C: ("GH3X2X_SoftAdtGreenAlgorithmResultReport", "high"),
    0x0002AC8C: ("GH3X2X_SoftAdtIrAlgorithmResultReport", "high"),
    0x0002ACCC: ("GH3X2X_SoftReset", "high"),
    0x0002ACF4: ("GH3X2X_Spo2AlgoChnlMapDefultSet", "high"),
    0x0002AD14: ("GH3X2X_Spo2AlgorithmResultReport", "high"),
    0x0002AD18: ("GH3X2X_StartSampling", "high"),
    0x0002AD7C: ("GH3X2X_StopSampling", "high"),
    0x0002ADB0: ("GH3X2X_StoreDrvCurrentAfterAgc", "high"),
    0x0002AE00: ("GH3X2X_TimestampSyncGetFrameDataFlag", "high"),
    0x0002AE04: ("GH3X2X_TimestampSyncPpgInit", "high"),
    0x0002AE06: ("GH3X2X_TimestampSyncSetPpgIntFlag", "high"),
    0x0002AE08: ("GH3X2X_TryWakeUp", "high"),
    0x0002AE28: ("GH3X2X_UpdateAgcInfo", "high"),
    0x0002AEDC: ("GH3X2X_WriteAlgConfigWithVirtualReg", "high"),
    0x0002AF32: ("GH3X2X_WriteAlgParametersWithVirtualReg", "high"),
    0x0002AF84: ("GH3X2X_WriteChnlMapConfigWithVirtualReg", "high"),
    0x0002B010: ("GH3X2X_WriteFunctionConfigWithVirtualReg", "high"),
    0x0002B0B8: ("GH3X2X_WriteReg", "high"),
    0x0002B0DC: ("GH3X2X_WriteRegBitField", "high"),
    0x0002B148: ("GH3X2X_WriteSwConfigWithVirtualReg", "high"),
    0x0002B180: ("GH3X2X_WriteVirtualReg", "high"),
    0x0002B218: ("GH3x2xAdtAlgoExe", "high"),
    0x0002B4C4: ("GH3x2xAdtAlgoInit", "high"),
    0x0002B4D8: ("GH3x2xAdtVersion", "high"),
    0x0002B4F8: ("GH3x2xAgcCalDrvCurrent", "high"),
    0x0002B524: ("GH3x2xAgcCalDrvCurrentAndGain", "high"),
    0x0002B6A4: ("GH3x2xAgcCalExtremum", "high"),
    0x0002B6E0: ("GH3x2xAgcChnlInfoInit", "high"),
    0x0002B8EC: ("GH3x2xAgcFindSubChnlSlotInfo", "high"),
    0x0002B91C: ("GH3x2xAgcInfoUpdate", "high"),
    0x0002B998: ("GH3x2xAgcMainChnlKeyValueCal", "high"),
    0x0002BD84: ("GH3x2xAgcMeanInfoReset", "high"),
    0x0002BE24: ("GH3x2xAgcRegParse", "high"),
    0x0002BFAA: ("GH3x2xAgcRegvalGet", "high"),
    0x0002C148: ("GH3x2xAgcRegvalReset", "high"),
    0x0002C178: ("GH3x2xAgcSubChnlAdjGainAndClearCnt", "high"),
    0x0002C248: ("GH3x2xCalFunctionSlotBit", "high"),
    0x0002C27C: ("GH3x2xCalGsensorStep", "high"),
    0x0002C2A4: ("GH3x2xCreatTagArray", "high"),
    0x0002C2EC: ("Gh3x2xDemoSearchCfgListByFunc", "high"),
    0x0002C43C: ("GH3x2xFunctionProcess", "high"),
    0x0002C4C0: ("GH3x2xGetAgcReg", "high"),
    0x0002C4E4: ("GH3x2xGetDrvCurrent", "high"),
    0x0002C4FC: ("GH3x2xGetFrameDataAndProcess", "high"),
    0x0002C640: ("GH3x2xGetFrameNum", "high"),
    0x0002C694: ("GH3x2xHandleFrameData", "high"),
    0x0002C930: ("GH3x2xHrAlgoDeinit", "high"),
    0x0002C944: ("GH3x2xHrAlgoExe", "high"),
    0x0002CAA4: ("GH3x2xHrAlgoInit", "high"),
    0x0002CAD8: ("GH3x2xHrvAlgoExe", "high"),
    0x0002CC94: ("GH3x2xSetAgcReg", "high"),
    0x0002CCC0: ("GH3x2xSetFunctionChnlMap", "high"),
    0x0002CCD0: ("GH3x2xSetFunctionChnlNum", "high"),
    0x0002CCF4: ("Gh3x2xSleepFlagGet", "high"),
    0x0002CD00: ("GH3x2xSlotTimeInfo", "high"),
    0x0002CDD4: ("GH3x2xSoftAdtAlgoExe", "high"),
    0x0002CFE8: ("GH3x2xSpo2AlgoExe", "high"),
    0x0002D16C: ("GH3x2xSpo2AlgoInit", "high"),
    0x0002D184: ("GH3x2x_AgcAdjustGainByExtremum", "high"),
    0x0002D324: ("GH3x2x_BitCount", "high"),
    0x0002D33C: ("GH3x2x_GetActiveChipResetFlag", "high"),
    0x0002D348: ("GH3x2x_GetChipResetRecoveringFlag", "high"),
    0x0002D354: ("GH3x2x_Round", "high"),
    0x0002D3A8: ("GH3x2x_SetChipResetRecoveringFlag", "high"),
    0x0002D658: ("GetNextEventPointer", "high"),
    0x0002D670: ("Gh3x2xDemoArrayCfgSwitch", "high"),
    0x0002D824: ("Gh3x2xDemoFunctionProcess", "high"),
    0x0002D87C: ("Gh3x2xDemoInit", "high"),
    0x0002DB8C: ("Gh3x2xDemoInterruptProcess", "high"),
    0x0002E0D0: ("Gh3x2xDemoSamplingControl", "high"),
    0x0002E340: ("Gh3x2xDemoStartAlgoInner", "high"),
    0x0002E358: ("Gh3x2xDemoStartSampling", "high"),
    0x0002E36C: ("Gh3x2xDemoStartSamplingInner", "high"),
    0x0002E61C: ("Gh3x2xDemoStartSamplingWithCfgSwitch", "high"),
    0x0002E6A8: ("Gh3x2xDemoStopSampling", "high"),
    0x0002E6BC: ("Gh3x2xDemoStopSamplingInner", "high"),
    0x0002E746: ("Gh3x2xFifoRecovery", "high"),
    0x0002E778: ("Gh3x2xFunctionInfoForUserInit", "high"),
    0x0002E7A4: ("Gh3x2xFunctionSlotBitInit", "high"),
    0x0002E7C4: ("Gh3x2xGetConfigVersion", "high"),
    0x0002E8C4: ("Gh3x2xGetHrAlgoSupportChnl", "high"),
    0x0002E8C8: ("Gh3x2xGetSpo2AlgoSupportChnl", "high"),
    0x0002E8E8: ("Gh3x2xMovingAvaFilter", "high"),
    0x0002E964: ("Gh3x2xSetCurrentSlotEnReg", "high"),
    0x0002EB0C: ("Gh3x2xSetFrameFlag2", "high"),
    0x0002EB84: ("Gh3x2x_WearEventHook", "high"),
    0x0002ED98: ("GH3X2X_ReinitAllSwModuleParam", "high"),
    0x0002EDAA: ("GH3X2X_WriteSwConfigWithVirtualReg_0x1100_arm", "high"),
    0x0002EDEC: ("GhDrvConfigManagerInit", "high"),
    0x0002EDFC: ("GhGetFunctionIdViaVirReg", "high"),
    0x0002EE28: ("GhMultiSensorTimerInit", "high"),
    0x0002EE38: ("GhGsMoveDetecterIsEnable", "high"),
    0x0002EE44: ("GhMultSensorWearEventManagerGetCurTs", "high"),
    0x0002EE50: ("GhMultSensorWearEventManagerInit", "high"),
    0x0002EF6C: ("GhMultiSensorPrintAllEvt", "high"),
    0x0002F0F8: ("GhGsMoveDetecterInit", "high"),
    0x0006A018: ("get_Spo2WRWeights_addr", "high"),
    0x0006A020: ("get_Spo2WRWeights_version", "high"),
    0x0006A130: ("get_knConfNetWeightsArr_addr", "high"),
    0x0006A148: ("get_knTdfusionWeightsArr_addr", "high"),
    0x0006A500: ("GH3X2X_AlgoCallConfigInit", "high"),
    0x0006CC34: ("goodix_hrv_config_get_version", "high"),
    0x0006EAF8: ("goodix_spo2_config_get_instance", "high"),
    0x0006EB00: ("goodix_spo2_config_get_version", "high"),
    0x0006EC28: ("goodix_spo2_init_func", "high"),
    0x0002A5C4: ("GH3X2X_GetGsensorEnableFlag", "candidate"),
    0x0002A7F4: ("GH3X2X_InitSensorParameters", "candidate"),
    0x0002A9D4: ("GH3X2X_ReadElectrodeWearDumpData", "candidate"),
    0x0002ABEC: ("GH3X2X_SensorPramInit", "candidate"),
    0x0002EB4E: ("Gh3x2x_NormalizeGsensorSensitivity", "candidate"),
    }

# Even/Bravechip-authored glue reclassified out of the Goodix provider gate by
# the 2026-08-14 residual mapping pass.
GOODIX_ADAPTER_GLUE_SYMBOLS = {
    0x0002E734: "r1_goodix_sampling_mode_glue",
    0x0003DDF4: "r1_goodix_gomore_ops_cross_wiring",
    0x0006A4D8: "r1_goodix_frame_data_hook",
    0x0006F920: "r1_goodix_gsensor_cache_sample",
    0x0006F964: "r1_goodix_gsensor_cache_commit",
    0x0006F9D4: "r1_goodix_gsensor_cache_query",
}


def apply_goodix_democode_attribution(function):
    """Rewrite a frontier census expectation for democode-attributed entries."""
    rewritten = dict(function)
    entry = int(rewritten["entry"])
    if entry in goodix_democode_symbols:
        rewritten["provider_family"] = "goodix_gh3x2x_democode_v1_6_drvlib_v4_3_0_0"
        rewritten["source_disposition"] = "use_pinned_upstream"
        rewritten["symbol"] = goodix_democode_symbols[entry][0]
    elif entry in GOODIX_ADAPTER_GLUE_SYMBOLS:
        rewritten["provider_family"] = "r1_goodix_provider_adapter"
        rewritten["symbol"] = GOODIX_ADAPTER_GLUE_SYMBOLS[entry]
    return rewritten



def main() -> None:
    protocol = PROJECT / "include" / "openr1" / "r1_protocol.h"
    expected = {
        "R1_MODEL_HEADER_LENGTH": 12,
        "R1_FRAGMENT_HEADER_LENGTH": 5,
        "R1_FRAGMENT_PAYLOAD_MAX": 239,
        "R1_BLE_VALUE_MAX": 244,
        "R1_SEQUENCE_MAX": 16,
        "R1_LOGICAL_INBOUND_MAX": 4063,
        "R1_LOGICAL_SAFE_OUTBOUND_MAX": 4062,
    }
    for name, value in expected.items():
        actual = parse_number(protocol, name)
        if actual != value:
            raise AssertionError(f"{name}: {actual} != {value}")

    event = PROJECT / "include" / "openr1" / "r1_event.h"
    event_expected = {
        "R1_NORMAL_QUEUE_CAPACITY": 20,
        "R1_EUS_QUEUE_CAPACITY": 50,
        "R1_HVN_CREDIT_MAX": 4,
        "R1_TX_ENQUEUE_WAIT_TICKS": 100,
        "R1_EUS_CREDIT_WAIT_TICKS": 200,
        "R1_EUS_RESOURCE_RETRY_TICKS": 1000,
    }
    for name, value in event_expected.items():
        actual = parse_number(event, name)
        if actual != value:
            raise AssertionError(f"{name}: {actual} != {value}")

    health = PROJECT / "include" / "openr1" / "r1_health.h"
    health_expected = {
        "R1_HEALTH_HOURLY_SLOTS": 24,
        "R1_ACTIVITY_BUCKETS": 144,
        "R1_SLEEP_SESSION_MAX": 16,
        "R1_SLEEP_COMPACT_STAGE_MAX": 200,
        "R1_SLEEP_STORED_MAX_BYTES": 232,
        "R1_PENDING_ACK_CAPACITY": 32,
        "R1_HRV_RR_INTERVAL_MAX": 100,
        "R1_ACTIVITY_OFFLINE_CAPACITY": 144,
    }
    for name, value in health_expected.items():
        actual = parse_number(health, name)
        if actual != value:
            raise AssertionError(f"{name}: {actual} != {value}")

    storage = (PROJECT / "src" / "r1_storage.c").read_text()
    for name, offset, length in (
        ("kv.bin", "0x00000", "0x02000"),
        ("health.db", "0x02000", "0x06000"),
        ("sleep.db", "0x08000", "0x02000"),
        ("pKey.bin", "0x0a000", "0x01000"),
        ("reserve", "0x0b000", "0x0b000"),
        ("ep.bin", "0x16000", "0x02000"),
        ("log.bin", "0x18000", "0x0c000"),
    ):
        if not all(item in storage for item in (name, offset, length)):
            raise AssertionError(f"partition mismatch for {name}")

    kv_store = PROJECT / "include" / "openr1" / "r1_kv_store.h"
    kv_expected = {
        "R1_KV_PARTITION_BYTES": 8192,
        "R1_KV_SECTOR_BYTES": 4096,
        "R1_KV_SLOT_BYTES": 2048,
        "R1_KV_SLOT_COUNT": 4,
        "R1_KV_CLASS_BLOCK_BYTES": 256,
        "R1_KV_CLASS_HEADER_BYTES": 24,
        "R1_KV_CLASS_COUNT": 7,
        "R1_KV_CLASS_PAYLOAD_MAX": 124,
    }
    for name, value in kv_expected.items():
        actual = parse_number(kv_store, name)
        if actual != value:
            raise AssertionError(f"{name}: {actual} != {value}")
    kv_source = PROJECT / "src" / "r1_kv_store.c"
    for marker in (
        "UINT32_C(0x45503130)", "dev_info", "ble_mult", "health", "hsync",
        "power", "nv_r1", "r_size", "meta_name", "generation_newer",
        "write_record(store, target, 0u",
    ):
        require(kv_source, marker)
    fdb_config = (PROJECT / "port" / "fdb_cfg.h").read_text()
    if "FDB_USING_KVDB" in fdb_config:
        raise AssertionError("FlashDB KVDB must not replace the recovered R1 kv.bin format")
    require(DOCS / "KV-STORE-CORRELATION.md", "not FlashDB KVDB")
    nv_recovery_header = PROJECT / "include" / "openr1" / "r1_nv_recovery.h"
    for marker in (
        "R1_NV_RECOVERY_BODY_BYTES 116u",
        "R1_NV_RECOVERY_CONFIG_BYTES 124u",
        "R1_NV_RECOVERY_POWER_BYTES 4u",
        "R1_NV_RECOVERY_CHANGED_CONFIG",
        "r1_nv_recovery_build_body",
        "r1_nv_recovery_merge",
        "normal BLE",
    ):
        require(nv_recovery_header, marker)
    nv_recovery_source = PROJECT / "src" / "r1_nv_recovery.c"
    for marker in (
        "PRODUCT_BSN_LENGTH_OFFSET = 30",
        "PRODUCT_SN_LENGTH_OFFSET = 61",
        "BODY_BATTERY_TYPE_OFFSET = 92",
        "BODY_VOLTAGE_COMPENSATION_OFFSET = 94",
        "BODY_RING_SIZE_OFFSET = 96",
        "r1_crc16_modbus",
        "voltage_recovery_valid",
        "UINT8_MAX",
    ):
        require(nv_recovery_source, marker)
    require(PROJECT / "tests" / "test_openr1.c", "test_nv_recovery_merge")

    sleep_db = PROJECT / "include" / "openr1" / "r1_sleep_db.h"
    sleep_expected = {
        "R1_SLEEP_DB_BYTES": 8192,
        "R1_SLEEP_DB_SECTORS": 2,
        "R1_SLEEP_DB_RECORDS_PER_SECTOR": 8,
        "R1_SLEEP_DB_SECTOR_HEADER_BYTES": 16,
        "R1_SLEEP_DB_RECORD_HEADER_BYTES": 24,
        "R1_SLEEP_DB_BODY_START": 208,
        "R1_SLEEP_DB_APPEND_MAX": 3888,
        "R1_SLEEP_DB_SYNC_READ_MAX": 232,
    }
    for name, value in sleep_expected.items():
        actual = parse_number(sleep_db, name)
        if actual != value:
            raise AssertionError(f"{name}: {actual} != {value}")
    require(sleep_db, "UINT32_C(0xccffaabb)")
    require(sleep_db, "UINT32_C(0x66889977)")
    require(sleep_db, "UINT32_C(0x11223344)")
    require(PROJECT / "src" / "r1_sleep_db.c", "body_offset + aligned")
    require(PROJECT / "src" / "r1_persistence.c", "r1_sleep_encode_compact")
    require(PROJECT / "src" / "r1_persistence.c", "r1_sleep_commit_synchronized")
    require(PROJECT / "src" / "r1_health.c", "sleep_sync_commit")

    linker = PROJECT / "platform" / "nrf52840" / "openr1.ld"
    require(linker, "ORIGIN = 0x00027000")
    require(linker, "ORIGIN = 0x200064A8")
    sdk_linker = PROJECT / "platform" / "nrf52840" / "sdk" / "openr1_sdk.ld"
    require(sdk_linker, "ORIGIN = 0x00027000")
    require(sdk_linker, "ORIGIN = 0x200064a8")
    require(sdk_linker, ".openr1_noinit (NOLOAD)")
    require(sdk_linker, "PROVIDE(_sstack = __StackLimit)")
    require(sdk_linker, "PROVIDE(_stext = ORIGIN(FLASH))")
    sdk_config = PROJECT / "platform" / "nrf52840" / "sdk" / "config" / "sdk_config.h"
    sdk_expected = {
        "NRF_SDH_BLE_PERIPHERAL_LINK_COUNT": 3,
        "NRF_SDH_BLE_CENTRAL_LINK_COUNT": 0,
        "NRF_SDH_BLE_TOTAL_LINK_COUNT": 3,
        "NRF_SDH_BLE_GAP_EVENT_LENGTH": 6,
        "NRF_SDH_BLE_GATT_MAX_MTU_SIZE": 247,
        "NRF_SDH_BLE_GATTS_ATTR_TAB_SIZE": 2048,
        "NRF_SDH_BLE_VS_UUID_COUNT": 2,
        "NRF_SDH_BLE_SERVICE_CHANGED": 1,
        "NRF_SDH_CLOCK_LF_RC_CTIV": 16,
        "NRF_SDH_CLOCK_LF_RC_TEMP_CTIV": 2,
        "NRF_SDH_CLOCK_LF_ACCURACY": 1,
        "NRF_SDH_DISPATCH_MODEL": 2,
        "PEER_MANAGER_ENABLED": 1,
        "PM_CENTRAL_ENABLED": 0,
        "PM_BLE_OBSERVER_PRIO": 1,
        "BLE_CONN_STATE_BLE_OBSERVER_PRIO": 0,
        "FDS_ENABLED": 1,
        "FDS_VIRTUAL_PAGES": 3,
        "FDS_VIRTUAL_PAGE_SIZE": 1024,
        "FDS_VIRTUAL_PAGES_RESERVED": 36,
        "FDS_BACKEND": 2,
        "NRF_FSTORAGE_ENABLED": 1,
        "NRF_SORTLIST_ENABLED": 1,
        "APP_TIMER_ENABLED": 1,
        "BLE_ADVERTISING_ENABLED": 1,
        "BLE_ADV_BLE_OBSERVER_PRIO": 1,
        "NRF_BLE_GATT_ENABLED": 1,
        "NRF_BLE_GATT_MTU_EXCHANGE_INITIATION_ENABLED": 1,
        "NRF_BLE_GATT_BLE_OBSERVER_PRIO": 1,
        "NRFX_CLOCK_ENABLED": 1,
        "NRFX_CLOCK_CONFIG_LF_SRC": 0,
        "NRFX_SAADC_ENABLED": 1,
        "NRFX_SAADC_CONFIG_RESOLUTION": 2,
        "NRFX_SAADC_CONFIG_OVERSAMPLE": 0,
        "NRFX_SAADC_CONFIG_LP_MODE": 0,
        "NRFX_SAADC_CONFIG_IRQ_PRIORITY": 6,
        "NRFX_WDT_ENABLED": 1,
        "NRFX_WDT_CONFIG_BEHAVIOUR": 1,
        "NRFX_WDT_CONFIG_RELOAD_VALUE": 10000,
        "NRFX_WDT_CONFIG_IRQ_PRIORITY": 6,
        "NRFX_WDT_CONFIG_NO_IRQ": 0,
    }
    for name, value in sdk_expected.items():
        actual = parse_number(sdk_config, name)
        if actual != value:
            raise AssertionError(f"{name}: {actual} != {value}")
    freertos_config = (
        PROJECT / "platform" / "nrf52840" / "sdk" / "config" /
        "FreeRTOSConfig.h"
    )
    for name, value in {
        "configTICK_RATE_HZ": 1024,
        "configMAX_PRIORITIES": 56,
        "configMINIMAL_STACK_SIZE": 256,
        "configTOTAL_HEAP_SIZE": 32768,
        "configTIMER_TASK_PRIORITY": 40,
        "configTIMER_QUEUE_LENGTH": 32,
        "configTIMER_TASK_STACK_DEPTH": 256,
        "configCHECK_FOR_STACK_OVERFLOW": 2,
    }.items():
        actual = parse_number(freertos_config, name)
        if actual != value:
            raise AssertionError(f"{name}: {actual} != {value}")
    for marker in (
        "#define configTICK_SOURCE FREERTOS_USE_RTC",
        "#define configUSE_PREEMPTION 1",
        "#define configUSE_TICKLESS_IDLE 1",
        "#define configSUPPORT_STATIC_ALLOCATION 1",
        "#define configSUPPORT_DYNAMIC_ALLOCATION 1",
        "#define configUSE_OS2_THREAD_FLAGS 1",
        "no local implementation is supplied",
    ):
        require(freertos_config, marker)
    require(PROJECT / "platform" / "nrf52840" / "sdk" / "main.c",
            "nrf_sdh_ble_default_cfg_set")
    require(PROJECT / "platform" / "nrf52840" / "sdk" / "main.c",
            "BLE_COMMON_OPT_EXTENDED_RC_CAL")
    bae8 = PROJECT / "platform" / "nrf52840" / "sdk" / "openr1_bae8.c"
    for marker in (
        "0x1f, 0x9d, 0x32, 0xf7", "OPENR1_BAE8_CHANNEL1_RX_UUID",
        "OPENR1_BAE8_CHANNEL2_TX_UUID", "characteristic_add",
        "BLE_GATTS_OP_PREP_WRITE_REQ", "r1_runtime_receive_eus",
        "openr1_bae8_transmit", "openr1_scheduler_complete_credits",
        "openr1_scheduler_reset_credits", "NRF_SDH_BLE_OBSERVER",
    ):
        require(bae8, marker)
    require(bae8, "sd_ble_gatts_value_get")
    peer = PROJECT / "platform" / "nrf52840" / "sdk" / "openr1_peer.c"
    for marker in (
        "pm_init", "pm_sec_params_set", "pm_register", "allow_repairing = true",
        "security.bond = 1u", "security.mitm = 0u", "security.lesc = 0u",
        "security.min_key_size = 7u", "security.max_key_size = 16u",
        "security.kdist_own.enc = 1u", "security.kdist_own.id = 1u",
        "security.kdist_peer.enc = 1u", "security.kdist_peer.id = 1u",
        "status.encrypted", "status.bonded", "false",
        "pm_conn_secure", "NRF_ERROR_BUSY", "r1_runtime_set_role_handler",
    ):
        require(peer, marker)
    sdk_makefile = PROJECT / "platform" / "nrf52840" / "sdk" / "Makefile"
    for marker in (
        "components/libraries/fds/fds.c",
        "components/libraries/fstorage/nrf_fstorage_sd.c",
        "components/ble/common/ble_conn_state.c",
        "components/ble/peer_manager/peer_manager.c",
        "components/ble/peer_manager/peer_manager_handler.c",
        "components/ble/peer_manager/security_manager.c",
        "components/libraries/timer/app_timer_freertos.c",
        "FREERTOS_KERNEL_ROOT := $(abspath $(PROJ_DIR)/../g2/third_party/freertos-kernel)",
        "$(FREERTOS_KERNEL_ROOT)/tasks.c",
        "$(FREERTOS_KERNEL_ROOT)/queue.c",
        "$(FREERTOS_KERNEL_ROOT)/timers.c",
        "$(FREERTOS_KERNEL_ROOT)/portable/MemMang/heap_4.c",
        "external/freertos/portable/GCC/nrf52/port.c",
        "CMSIS-FreeRTOS/CMSIS/RTOS2/FreeRTOS/Source/cmsis_os2.c",
        "CMBACKTRACE_ROOT)/cm_backtrace/cm_backtrace.c",
        "BMA456_ROOT)/bma4.c",
        "BMA456_ROOT)/bma456w.c",
        "LIS2DW12_ROOT)/lis2dw12_reg.c",
        "ST25DVXXKC_ROOT)/st25dvxxkc.c",
        "ST25DVXXKC_ROOT)/st25dvxxkc_reg.c",
        "TINY_AES_ROOT)/aes.c",
        "src/r1_crypto.c",
        "src/r1_kv_store.c",
        "src/r1_nv_recovery.c",
        "src/r1_power_lease.c",
        "src/r1_motion.c",
        "src/r1_battery.c",
        "modules/nrfx/drivers/src/nrfx_saadc.c",
        "modules/nrfx/drivers/src/nrfx_wdt.c",
        "openr1_analog.c",
        "openr1_cmbacktrace_port.c",
        "openr1_cmbacktrace_fault.S",
        "openr1_motion.c",
        "openr1_watchdog.c",
        "openr1_scheduler.c",
        "CONFIG_NFCT_PINS_AS_GPIOS",
        "CONFIG_GPIO_AS_PINRESET",
    ):
        require(sdk_makefile, marker)
    scheduler = PROJECT / "platform" / "nrf52840" / "sdk" / "openr1_scheduler.c"
    for marker in (
        "osKernelInitialize", "osKernelStart", "osThreadNew",
        "osThreadFlagsSet", "osThreadFlagsWait", "nrf_sdh_evts_poll",
        "osMessageQueueNew", "osMessageQueuePut", "osMessageQueueGet",
        "osSemaphoreNew", "osSemaphoreAcquire", "osSemaphoreRelease", "osDelay",
        "R1_TX_ENQUEUE_WAIT_TICKS", "R1_EUS_CREDIT_WAIT_TICKS",
        "r1_bae8_plan_hvx_result", "plan.retry_delay_ticks",
        'name = "channel1_tx"',
        "SD_EVT_IRQHandler", 'name = "eus_tx"', 'name = "BLE"',
        "vApplicationGetIdleTaskMemory", "vApplicationGetTimerTaskMemory",
        "vApplicationStackOverflowHook", "SEGGER_RTT_WriteString",
        "openr1_scheduler_current_stack",
        "openr1_watchdog_initialize",
    ):
        require(scheduler, marker)
    freertos_static_memory = DOCS / "FREERTOS-STATIC-MEMORY-CORRELATION.md"
    for marker in (
        "Two exact functions / 36 executable bytes",
        "0x00095BB8..<0x00095BCA",
        "0x00095BD0..<0x00095BE2",
        "112 bytes for `StaticTask_t`",
        "256 four-byte `StackType_t` words",
        "configTIMER_TASK_STACK_DEPTH` to 256",
        "No FreeRTOS function body is recreated locally",
    ):
        require(freertos_static_memory, marker)
    freertos_stack_overflow = DOCS / "FREERTOS-STACK-OVERFLOW-CORRELATION.md"
    for marker in (
        "0x00095BFC..<0x00095C44",
        "vApplicationStackOverflowHook",
        "0x000965E4",
        "configCHECK_FOR_STACK_OVERFLOW` to 2",
        "first four stack words",
        "No FreeRTOS function body is recreated locally",
    ):
        require(freertos_stack_overflow, marker)
    nordic_system_init = DOCS / "NORDIC-SYSTEM-INIT-CORRELATION.md"
    for marker in (
        "Two exact functions / 544 executable bytes",
        "0x00033364..<0x00033576",
        "0x0007CA7C..<0x0007CA8A",
        "CONFIG_NFCT_PINS_AS_GPIOS",
        "CONFIG_GPIO_AS_PINRESET",
        "No Nordic startup body is recreated locally",
    ):
        require(nordic_system_init, marker)
    nordic_twim_completeness = DOCS / "NORDIC-TWIM-COMPLETENESS-CORRELATION.md"
    for marker in (
        "0x00098DC0..<0x00098E22",
        "xfer_completeness_check",
        "0x00093A44",
        "0x00093DB8",
        "ENABLE = 0` followed by `ENABLE = 6",
        "No Nordic TWIM body is",
    ):
        require(nordic_twim_completeness, marker)
    nordic_gatt_cache = DOCS / "NORDIC-GATT-CACHE-CLOSURE.md"
    for marker in ("Ten exact functions / 784 executable bytes", "0x0006EDCC..<0x0006EDE2",
                   "0x0006EDE8..<0x0006EDF8", "0x0006EDFC..<0x0006EEA4",
                   "0x0006F0F8..<0x0006F116", "0x0006F118..<0x0006F194",
                   "0x00075A08..<0x00075AF2", "0x00075B10..<0x00075B1A",
                   "0x0008A928..<0x0008A934",
                   "0x00091084..<0x0009110A", "0x00094AB0..<0x00094AD2",
                   "No Peer Manager or GATT-cache body"):
        require(nordic_gatt_cache, marker)
    nordic_ble_helpers = DOCS / "NORDIC-BLE-STATIC-HELPERS-CORRELATION.md"
    for marker in (
        "Five exact Nordic SDK functions / 158 Ghidra-counted executable bytes",
        "0x00074F20..<0x00074F38", "link_init",
        "0x00087A94..<0x00087AA8", "ram_end_address_get",
        "0x00087AAC..<0x00087AC8", "rank_highest",
        "0x00087AC8..<0x00087AF4", "rank_vars_update",
        "0x0008EE0A..<0x0008EE3A", "set_security_req",
        "six-byte inline", "Thumb jump table",
        "No BLE common, SoftDevice handler, or Peer Manager body is recreated locally",
    ):
        require(nordic_ble_helpers, marker)
    freertos_version = DOCS / "FREERTOS-KERNEL-VERSION-CORRELATION.md"
    for marker in ("authenticated FreeRTOS-Kernel 10.5.1 core", "Nordic's nRF52",
                   "0x00085440..<0x00085468", "prvReloadTimer",
                   "d03d69b29abd0f1d1fd5c818b9cda349717d56534de9709497af868b7cb4b635",
                   "0x000852C2", "0x00085354", "no kernel or port body is"):
        require(freertos_version, marker)
    watchdog = PROJECT / "platform" / "nrf52840" / "sdk" / "openr1_watchdog.c"
    for marker in (
        "NRF_WDT_BEHAVIOUR_RUN_SLEEP",
        "OPENR1_WATCHDOG_RELOAD_MILLISECONDS 10000u",
        "OPENR1_WATCHDOG_INTERRUPT_PRIORITY 6u",
        "OPENR1_WATCHDOG_FEED_TICKS 1024u",
        "nrfx_wdt_init", "nrfx_wdt_channel_alloc",
        "nrfx_wdt_channel_feed", "nrfx_wdt_enable",
        "osThreadNew", 'name = "watchdog"',
    ):
        require(watchdog, marker)
    cmbacktrace_config = (
        PROJECT / "platform" / "nrf52840" / "sdk" / "config" /
        "cmb_user_cfg.h"
    )
    for marker in (
        "CMB_OS_PLATFORM_FREERTOS", "CMB_CPU_ARM_CORTEX_M4",
        "CMB_NAME_MAX 20", "CMB_CALL_STACK_MAX_DEPTH 32",
        "CMB_DUMP_STACK_DEPTH_SIZE 16", "openr1_cmbacktrace_log",
    ):
        require(cmbacktrace_config, marker)
    cmbacktrace_port = (
        PROJECT / "platform" / "nrf52840" / "sdk" /
        "openr1_cmbacktrace_port.c"
    )
    for marker in (
        "cm_backtrace_init", '"603MV1.9.3"', '"2.2.6.0009"',
        ".openr1_noinit", "vTaskStackAddr", "vTaskStackSize", "vTaskName",
    ):
        require(cmbacktrace_port, marker)
    require(PROJECT / "platform" / "nrf52840" / "sdk" / "main.c",
            "openr1_cmbacktrace_initialize")
    cmbacktrace_fault = (
        PROJECT / "platform" / "nrf52840" / "sdk" /
        "openr1_cmbacktrace_fault.S"
    )
    for marker in (
        "NMI_Handler", "HardFault_Handler", "MemoryManagement_Handler",
        "BusFault_Handler", "UsageFault_Handler", "cm_backtrace_fault",
        "openr1_reset_trace_fault_and_reset",
    ):
        require(cmbacktrace_fault, marker)
    reset_trace_header = PROJECT / "include" / "openr1" / "r1_reset_trace.h"
    for marker in (
        "R1_RESET_TRACE_BYTES 16u",
        "R1_RESET_TRACE_FIELD_COUNT 13u",
        "R1_RESET_TRACE_FAULT_TAG 7u",
        "r1_reset_trace_get_snapshot",
    ):
        require(reset_trace_header, marker)
    reset_trace_source = PROJECT / "src" / "r1_reset_trace.c"
    for marker in (
        "r1_crc16_modbus",
        "r1_reset_trace_clear_addresses",
        "r1_reset_trace_set_persist_tag",
        "r1_reset_trace_capture_site",
    ):
        require(reset_trace_source, marker)
    reset_trace_port = (
        PROJECT / "platform" / "nrf52840" / "sdk" /
        "openr1_reset_trace_port.c"
    )
    for marker in (
        ".openr1_noinit",
        "openr1_reset_trace_retained_record",
        "NVIC_SystemReset",
        ".openr1_reset_trace_api",
    ):
        require(reset_trace_port, marker)
    require(PROJECT / "tests" / "test_openr1.c", "test_retained_reset_trace")
    reset_reason_header = PROJECT / "include" / "openr1" / "r1_reset_reason.h"
    for marker in (
        "R1_RESET_REASON_KNOWN_MASK UINT32_C(0x0007000f)",
        "power_on_or_brownout",
        "software_trace_valid",
        "r1_reset_reason_decode",
    ):
        require(reset_reason_header, marker)
    require(PROJECT / "src" / "r1_reset_reason.c", "raw & R1_RESET_REASON_KNOWN_MASK")
    require(PROJECT / "tests" / "test_openr1.c", "test_reset_reason_decode")
    reset_reason_port = (
        PROJECT / "platform" / "nrf52840" / "sdk" /
        "openr1_reset_reason.c"
    )
    for marker in (
        "nrf_power_resetreas_get",
        "nrf_power_resetreas_clear",
        "openr1_reset_trace_retained_record",
        ".openr1_reset_reason_api",
    ):
        require(reset_reason_port, marker)
    app_timer_compat = (
        PROJECT / "platform" / "nrf52840" / "sdk" /
        "openr1_app_timer_compat.c"
    )
    require(app_timer_compat, "xTaskGetTickCount")
    require(app_timer_compat, "APP_TIMER_MAX_CNT_VAL")
    gatt = PROJECT / "platform" / "nrf52840" / "sdk" / "openr1_gatt.c"
    for marker in (
        "NRF_BLE_GATT_DEF", "nrf_ble_gatt_init",
        "nrf_ble_gatt_att_mtu_periph_set", "nrf_ble_gatt_att_mtu_central_set",
        "nrf_ble_gatt_data_length_set", "UINT16_C(247)", "UINT8_C(251)",
        "nrf_ble_gatt_eff_mtu_get", "nrf_ble_gatt_data_length_get",
    ):
        require(gatt, marker)
    for marker in (
        "components/ble/nrf_ble_gatt/nrf_ble_gatt.c",
        "components/libraries/strerror/nrf_strerror.c",
    ):
        require(sdk_makefile, marker)
    advertising = PROJECT / "platform" / "nrf52840" / "sdk" / "openr1_advertising.c"
    for marker in (
        "BLE_ADVERTISING_DEF", "ble_advertising_init", "ble_advertising_start",
        "BLE_ADVDATA_FULL_NAME", "BLE_GAP_ADV_FLAGS_LE_ONLY_GENERAL_DISC_MODE",
        "UINT16_C(0x0240)", "UINT16_C(0x5245)", "UINT16_C(0x00a0)",
        "UINT16_C(0x1770)", "UINT16_C(0x0640)", "address->addr[3]",
        "address->addr[2]", "address->addr[1]", '"EVEN R1_"', '"_FAC"',
        "sd_ble_gap_device_name_set", "sd_ble_gap_appearance_set",
        "sd_ble_gap_ppcp_set",
    ):
        require(advertising, marker)
    for marker in (
        "components/ble/ble_advertising/ble_advertising.c",
        "components/ble/common/ble_advdata.c",
    ):
        require(sdk_makefile, marker)
    require(PROJECT / "src" / "r1_runtime.c", "R1_CHECKSUM_PHONE_COMPACT_CCITT")
    require(PROJECT / "src" / "r1_runtime.c", "r1_fragment_message")
    require(PROJECT / "src" / "r1_runtime.c", "R1_EUS_CREDIT_WAIT_TICKS")
    require(PROJECT / "src" / "r1_runtime.c", "R1_EUS_RESOURCE_RETRY_TICKS")
    require(PROJECT / "src" / "r1_runtime.c", "resource_retry_pending")
    require(PROJECT / "src" / "r1_dispatch.c", "Pair-role selection is not an authorization primitive")
    require(PROJECT / "src" / "r1_dispatch.c", "static const uint8_t pair_result = 0u")
    require(PROJECT / "src" / "r1_runtime.c", "commit_role_change")
    require(PROJECT / "src" / "r1_dispatch.c", "Exact 2.2.6.0009 behavior")
    require(PROJECT / "src" / "r1_health.c", "r1_health_acknowledge")
    require(PROJECT / "src" / "r1_health.c", "r1_hrv_producer_ingest")
    require(PROJECT / "src" / "r1_goodix.c", "R1_GOODIX_MASK_SWITCH_CLEAR")
    require(PROJECT / "src" / "r1_goodix.c", "R1_ERROR_UNSUPPORTED")
    require(PROJECT / "include" / "openr1" / "r1_goodix.h",
            "proprietary Goodix GH3X2X boundary")
    require(PROJECT / "tests" / "test_openr1.c", "test_goodix_provider_boundary")
    require(PROJECT / "tests" / "test_openr1.c", "test_battery_provider_boundary")
    require(PROJECT / "tests" / "test_openr1.c", "test_battery_controller")
    require(PROJECT / "tests" / "test_openr1.c", "test_automatic_health_sync")
    require(PROJECT / "tests" / "test_openr1.c", "test_activity_offline_sync")
    require(PROJECT / "src" / "r1_battery.c", "BATTERY_SCALE_NUMERATOR")
    require(PROJECT / "src" / "r1_battery.c", "BATTERY_CHARGING_DIVIDER")
    require(PROJECT / "src" / "r1_battery.c", "r1_battery_controller_update")
    require(PROJECT / "src" / "r1_runtime.c", "r1_runtime_update_battery")
    require(PROJECT / "platform" / "nrf52840" / "sdk" / "openr1_analog.c",
            "openr1_analog_update_runtime_battery")
    require(PROJECT / "src" / "r1_health.c", "R1_HEALTH_AUTO_SYNC_COOLDOWN_ELAPSED")
    require(PROJECT / "src" / "r1_health.c", "r1_health_run_automatic_sync")
    require(PROJECT / "src" / "r1_runtime.c",
            "r1_runtime_run_automatic_health_sync")
    require(PROJECT / "platform" / "nrf52840" / "sdk" / "openr1_health.c",
            ".openr1_health_api")
    for marker in (
        "r1_activity_offline_enqueue",
        "r1_activity_offline_consume_through",
        "r1_activity_offline_merge",
        "r1_activity_offline_acknowledge",
        "activity offline record layout must remain 16 bytes",
        "HR/SpO2 offline record layout must remain 16 bytes",
        "HRV offline record layout must remain 20 bytes",
        "r1_health_u8_offline_enqueue",
        "r1_health_u16_offline_acknowledge",
        "r1_activity_cache_reset",
        "r1_activity_cache_read_hour",
        "r1_activity_cache_write_hour",
        "r1_activity_clamp_acknowledgement_timestamp",
        "r1_activity_day_builder_reset",
        "r1_activity_day_builder_flush",
        "r1_activity_ram_cache_merge",
        "r1_activity_flash_record_merge",
    ):
        require(PROJECT / "src" / "r1_health.c", marker)
    correlation_review = DOCS / "SOURCE-CORRELATION-REVIEW.md"
    for marker in (
        "0x0002907C..<0x0002908E",
        "0x00035412..<0x0003541A",
        "0x00071704..<0x0007170A",
        "0x00071B24..<0x00071B2A",
        "byte identity of a generic thunk alone is insufficient",
    ):
        require(correlation_review, marker)
    registry_boundary = DOCS / "GENERIC-DEVICE-REGISTRY-BOUNDARY.md"
    for marker in (
        "unknown_generic_device_registry_candidate",
        "0x00085D58",
        "0x00085CE0",
        "0x00085DA8..<0x00085DC2",
        "direct typed bindings",
    ):
        require(registry_boundary, marker)
    automatic_health_sync = DOCS / "AUTOMATIC-HEALTH-SYNC-CORRELATION.md"
    for marker in (
        "0x0004CBB0..<0x0004CBC4",
        "0x0008B138..<0x0008B180",
        "0x0008C150..<0x0008C49A",
        "10,800",
        "serial identifier zero",
        ".openr1_health_api",
    ):
        require(automatic_health_sync, marker)
    activity_offline_sync = DOCS / "ACTIVITY-OFFLINE-SYNC-CORRELATION.md"
    for marker in (
        "0x0003BDD8..<0x0003BE66",
        "0x0003C0D8..<0x0003C1E8",
        "0x200067A8",
        "144 records of exactly 16 bytes",
        "repeated bucket replaces",
        "Corrupt state returns an error",
    ):
        require(activity_offline_sync, marker)
    scalar_health_offline_sync = \
        DOCS / "SCALAR-HEALTH-OFFLINE-SYNC-CORRELATION.md"
    for marker in (
        "0x0003FAA4..<0x0003FB32",
        "0x0003FCEC..<0x0003FDFC",
        "0x00040BD4..<0x00040CE4",
        "0x00043EB0..<0x00043FC0",
        "24 records of exactly 16 bytes",
        "exactly 20 bytes",
        "firmware_clock_sampled",
        "Corrupt state returns `R1_ERROR_STATE`",
    ):
        require(scalar_health_offline_sync, marker)
    activity_daily_cache = DOCS / "ACTIVITY-DAILY-CACHE-CORRELATION.md"
    for marker in (
        "0x00048288..<0x000482A6",
        "0x000482A8..<0x00048324",
        "0x0004832C..<0x0004834A",
        "946080000",
        "signed offset bits as an unsigned value",
        "subsequently admitted",
    ):
        require(activity_daily_cache, marker)
    scalar_health_daily_cache = \
        DOCS / "SCALAR-HEALTH-DAILY-CACHE-CORRELATION.md"
    for marker in (
        "0x0007062C..<0x00070646",
        "0x00070648..<0x000706A0",
        "0x000706BE..<0x000706D8",
        "0x000706D8..<0x00070736",
        "0x00090DD4..<0x00090DEE",
        "0x00090DF0..<0x00090E48",
        "946080000",
        "1,087 hours",
        "three independent clock samples",
        "latest point",
    ):
        require(scalar_health_daily_cache, marker)
    scalar_health_storage = \
        DOCS / "SCALAR-HEALTH-SAMPLE-STORAGE-CORRELATION.md"
    for marker in (
        "0x0005ACE0..<0x0005ACE4",
        "0x0005AD90..<0x0005AE6C",
        "0x0005AF60..<0x0005B042",
        "0x0005BB2C..<0x0005BC0C",
        "0x0008A80A..<0x0008A83E",
        "0x0008A83E..<0x0008A866",
        "0x0008A8AE..<0x0008A8D8",
        "40...220",
        "minimum of 70",
        "metric IDs 0, 1, and 5",
        "Goodix",
        "GoMore",
    ):
        require(scalar_health_storage, marker)
    scalar_health_flash_merge = \
        DOCS / "SCALAR-HEALTH-FLASH-MERGE-CORRELATION.md"
    for marker in (
        "0x00040508..<0x00040692",
        "0x000446B4..<0x0004483E",
        "exact 128-byte record",
        "first record for an hour wins",
        "r1_health_u8_flash_record_merge",
        "FlashDB blob",
        "calendar conversion",
    ):
        require(scalar_health_flash_merge, marker)
    hrv_timing_start = DOCS / "HRV-TIMING-START-CORRELATION.md"
    for marker in (
        "0x00049F0C..<0x0004A08A",
        "second 3,450 through 3,599",
        "120-second one-shot timeout",
        "208-byte R1 workspace",
        "r1_hrv_plan_timing_start",
        "sensor-stream",
    ):
        require(hrv_timing_start, marker)
    hrv_ram_cache_merge = DOCS / "HRV-RAM-CACHE-MERGE-CORRELATION.md"
    for marker in (
        "0x00040DE0..<0x00040F5C",
        "0x0008CA90",
        "current hour",
        "inclusive `[window, now]`",
        "six-byte latest-HRV prefix",
        "r1_health_u16_ram_cache_merge",
        "no HRV calculation",
    ):
        require(hrv_ram_cache_merge, marker)
    scalar_ram_cache_merge = DOCS / "SCALAR-HEALTH-RAM-CACHE-MERGE-CORRELATION.md"
    for marker in (
        "0x0003FEF4..<0x00040060",
        "0x000440C4..<0x00044230",
        "0x0008C48E",
        "0x0008D0A0",
        "inclusive `[window, now]`",
        "r1_health_u8_ram_cache_merge",
        "does not calculate heart rate or",
    ):
        require(scalar_ram_cache_merge, marker)
    protocol_response = DOCS / "PROTOCOL-RESPONSE-CORRELATION.md"
    for marker in (
        "0x000828B4..<0x00082A20",
        "0x00082F9C..<0x00083024",
        "two functions / 500 bytes",
        "payload length + 12",
        "result 2",
        "returns 5",
        "3 for allocation",
        "4 for transport",
        "r1_protocol_send_response",
        "CRC-16/MODBUS",
        "post-increments",
        "FreeRTOS allocation",
    ):
        require(protocol_response, marker)
    export_state_machine = DOCS / "EXPORT-STATE-MACHINE-CORRELATION.md"
    for marker in (
        "0x0004E740..<0x0004E8AC",
        "0x00045114",
        "10-byte status/length/checksum",
        "50 milliseconds",
        "4,096 bytes",
        "Result 2 resets",
        "r1_export_plan_command",
        "no live raw private-log export sender",
    ):
        require(export_state_machine, marker)
    frontier_35x = DOCS / "FRONTIER-35X-CORRELATION.md"
    for marker in (
        "0x00033DBC..<0x00033F1E",
        "0x0008216C..<0x000822CC",
        "0x000425B0..<0x00042710",
        "0x00094384..<0x000944E2",
        "0x0006A714..<0x0006A870",
        "LTK output redacted",
        "(payload + 15) & ~3",
        "2-year/9-cm/9-kg",
        "0x96000",
        "0x7800",
        "licensed-provider",
    ):
        require(frontier_35x, marker)
    frontier_334_342 = DOCS / "FRONTIER-334-342-CORRELATION.md"
    for marker in (
        "0x00033AF8..<0x00033C4E",
        "0x0004D024..<0x0004D176",
        "0x000653E6..<0x00065536",
        "0x00090ACC..<0x00090C1A",
        "0x00074190..<0x000742DE",
        "every 60 invocations",
        "0x2800",
        "mode 3",
        "licensed-provider-only",
    ):
        require(frontier_334_342, marker)
    frontier_314_328 = DOCS / "FRONTIER-314-328-CORRELATION.md"
    for marker in (
        "0x0008B184..<0x0008B2CC",
        "0x00051108..<0x00051250",
        "0x000317CC..<0x0003190C",
        "0x00091B08..<0x00091C42",
        "0x000651CA..<0x00065304",
        "discards one minimum and one maximum",
        "nrfx_saadc_irq_handler",
        "licensed-provider-only",
        "no persistent database mutation",
    ):
        require(frontier_314_328, marker)
    frontier_280_308 = DOCS / "FRONTIER-280-308-CORRELATION.md"
    for marker in (
        "0x00065B4C..<0x00065C80",
        "0x00033850..<0x00033982",
        "0x00029D5C..<0x00029E88",
        "0x00083F24..<0x00084050",
        "0x00032598..<0x000326B2",
        "44 direct callers",
        "non-reflected CRC-32C",
        "1 -> 2",
        "Goodix licensed-provider boundary",
    ):
        require(frontier_280_308, marker)
    frontier_264_274 = DOCS / "FRONTIER-264-274-CORRELATION.md"
    for marker in (
        "0x00067C30..<0x00067D42",
        "0x00032408..<0x00032518",
        "0x0003D9B8..<0x0003DAC4",
        "0x0003EE34..<0x0003EF3C",
        "0x00064274..<0x0006437C",
        "0x000641C4..<0x000641F0",
        "five-cycle",
        "timestamps are zero",
        "licensed-provider-only",
        "no raw ep.bin payload",
    ):
        require(frontier_264_274, marker)
    frontier_256_262 = DOCS / "FRONTIER-256-262-CORRELATION.md"
    for marker in (
        "0x00081744..<0x00081854",
        "0x0007CA94..<0x0007CB98",
        "0x00084524..<0x00084628",
        "0x0007244E..<0x00072550",
        "0x0004B718..<0x0004B818",
        "1,306 executable bytes",
        "every 500 ticks",
        "period 600",
        "licensed-provider-only",
        "perform no live",
    ):
        require(frontier_256_262, marker)
    frontier_230_248 = DOCS / "FRONTIER-230-248-CORRELATION.md"
    for marker in (
        "0x000947DE..<0x000948D6",
        "0x00095168..<0x00095260",
        "0x00035E34..<0x00035F26",
        "0x0005E228..<0x0005E314",
        "0x00062A5C..<0x00062B4C",
        "1,208 bytes",
        "length 13",
        "shared by GoMore and Goodix",
        "licensed-provider-only",
        "no live flash",
    ):
        require(frontier_230_248, marker)
    frontier_224_230 = DOCS / "FRONTIER-224-230-CORRELATION.md"
    for marker in (
        "0x00049838..<0x0004991E",
        "0x00065D64..<0x00065E48",
        "0x00094C74..<0x00094D56",
        "0x0004D2F4..<0x0004D3D4",
        "0x000309DC..<0x00030ABC",
        "0x00036C7C..<0x00036D60",
        "1,360 bytes",
        "nrfx_pdm_irq_handler",
        "sd_ble_gap_phy_update",
        "600",
        "shared quantized-neural runtime",
    ):
        require(frontier_224_230, marker)
    frontier_212_222 = DOCS / "FRONTIER-212-222-CORRELATION.md"
    for marker in (
        "0x00072FB8..<0x00073096",
        "0x0008A45C..<0x0008A53A",
        "0x0008F780..<0x0008F85C",
        "0x0008EF28..<0x0008F008",
        "0x0003E7A8..<0x0003E880",
        "0x000628F6..<0x000629D2",
        "0x00063D50..<0x00063E2A",
        "1,542 executable bytes",
        "sensor-stream framework",
        "uxTaskGetSystemState",
        "event `0x2001`",
        "r1_bae8_plan_hvx_result",
        "openr1_storage_plan_fds_event",
        "private TCB fields",
    ):
        require(frontier_212_222, marker)
    frontier_204_210 = DOCS / "FRONTIER-204-210-CORRELATION.md"
    for marker in (
        "0x00089EEC..<0x00089FBE",
        "0x00093628..<0x000936F8",
        "0x0008A64C..<0x0008A718",
        "0x00064B24..<0x00064BF0",
        "0x0004D4AC..<0x0004D578",
        "five functions / 1,030 bytes",
        "r1_sensor_stream_registration_plan",
        "r1_activity_flash_record_enqueue_plan",
        "sd_ble_gap_ppcp_set",
        "r1_latest_valid_flash_slot_scan_adapter",
        "branch-looking data",
        "twelve tensor descriptors",
        "investigate_before_implementing",
    ):
        require(frontier_204_210, marker)
    frontier_128_202 = DOCS / "FRONTIER-128-202-CORRELATION.md"
    for marker in (
        "63 functions",
        "10,126 declared body bytes",
        "0x00072A32..<0x00072ACE",
        "modules/nrfx/drivers/src/nrfx_pwm.c",
        "0x20019EF4",
        "0x20015708",
        "0x00030AC9",
        "SD_BLE_GAP_TX_POWER_SET",
        "dev_info",
        "0x00074CB0",
        "0x00074CE0",
        "0xA0",
        "investigate_before_implementing",
    ):
        require(frontier_128_202, marker)
    frontier_64_127 = DOCS / "FRONTIER-64-127-CORRELATION.md"
    for marker in (
        "150 functions",
        "0x00087ED0",
        "reattempt_previous_operations",
        "peer_database.c",
        "0x00090E8C",
        "acc_int_1",
        "device_stacmd_irq",
        "2.2.6.0009",
        "investigate_before_implementing",
    ):
        require(frontier_64_127, marker)
    frontier_32_63 = DOCS / "FRONTIER-32-63-CORRELATION.md"
    for marker in (
        "151 functions",
        "0x20007DE8",
        "kv.bin",
        "twelve-descriptor tensor-arena",
        "0x00091C48",
        "0x00050F34",
        "investigate_before_implementing",
    ):
        require(frontier_32_63, marker)
    frontier_sub32 = DOCS / "FRONTIER-SUB32-CORRELATION.md"
    for marker in (
        "268 functions",
        "nrfx_pwm_0_irq_handler",
        "0x4001C000",
        "fabsf",
        "malloc-failed hook",
        "investigate_before_implementing",
    ):
        require(frontier_sub32, marker)
    frontier_final53 = DOCS / "FRONTIER-FINAL53-CORRELATION.md"
    for marker in (
        "53 functions",
        "uxTaskGetNumberOfTasks",
        "nrfx_prs_box_4_irq_handler",
        "db_update_pending_handle",
        "nrfx_wdt_irq_handler",
        "twi_evt_handler",
        "prvIncrementQueueTxLock",
        "investigate_before_implementing",
    ):
        require(frontier_final53, marker)
    delayed_event_timer = DOCS / "DELAYED-EVENT-TIMER-CORRELATION.md"
    for marker in (
        "0x00065F84..<0x000660FC",
        "0x00065C78",
        "0x00065E40",
        "64 logical slots",
        "0xFFFFFFFF",
        "0x7FFFFFFF",
        "r1_delayed_event_timer_step",
        "no live",
    ):
        require(delayed_event_timer, marker)
    health_history_routing = DOCS / "HEALTH-HISTORY-ROUTING-CORRELATION.md"
    for marker in (
        "0x00082BE8..<0x00082C0C",
        "0x00083298..<0x000832D2",
        "0x0008B8E8..<0x0008BA80",
        "0/1/0/3/3/5/0/7/7/9/7/11/11/13",
        "exactly eight bytes",
        "temperature and stress",
        "259,200 seconds",
        "does not expose an internal-event sender",
    ):
        require(health_history_routing, marker)
    time_health_rollover = DOCS / "TIME-HEALTH-ROLLOVER-CORRELATION.md"
    for marker in (
        "0x0005DC08..<0x0005DC5E",
        "0x0005DCE8..<0x0005DE98",
        "0x0005E698..<0x0005E956",
        "30/31-second boundary",
        "180 seconds",
        "3,600 seconds",
        "offsets 8 and 20",
        "0 -> 23",
        "no slot-2 subscriber",
        "does not publish private events",
    ):
        require(time_health_rollover, marker)
    temperature_stress_cache = \
        DOCS / "TEMPERATURE-STRESS-DAILY-CACHE-CORRELATION.md"
    for marker in (
        "0x0005ABA0..<0x0005AC38",
        "0x0005BCEC..<0x0005BDC8",
        "0x0005BE7C..<0x0005BF74",
        "0x0008A8D8..<0x0008A8FC",
        "0x0008A8FC..<0x0008A928",
        "0x00091124..<0x0009113E",
        "0x00091918..<0x00091950",
        "250...500",
        "published minus 250",
        "GXCAS",
        "GoMore",
    ):
        require(temperature_stress_cache, marker)
    activity_day_merge = DOCS / "ACTIVITY-DAY-MERGE-CORRELATION.md"
    for marker in (
        "0x0003BCF8..<0x0003BD4C",
        "0x0003BDAC..<0x0003BDD6",
        "0x0003C304..<0x0003C4A2",
        "0x0003C578..<0x0003C796",
        "0x0003C958..<0x0003CB04",
        "144 presence bytes",
        "current bucket index",
        "exactly at local midnight",
        "Flash records fill only previously absent",
    ):
        require(activity_day_merge, marker)
    remaining_frontier = DOCS / "REMAINING-FUNCTION-FRONTIER.md"
    for marker in (
        "zero remain `unclassified`",
        "Thirty-four sensor-algorithm heap functions are now provenance-resolved",
        "FRONTIER-FINAL53-CORRELATION.md",
        "Eight composite-initializer functions / 586 bytes",
        "Six paired sleep-classifier graph-builder/allocator functions / 2,188 bytes",
        "Six activity-state window-classifier functions / 1,890 bytes",
        "Nine energy-model dispatcher/estimator functions / 2,360 bytes",
        "Five packed-word integrity helpers / 162 bytes",
        "57 formerly unclassified processing functions / 19,148 bytes",
        "0x0006E838 -> 0x000766AC -> 0x00035850",
        "31 formerly unclassified functions / 7,144 executable bytes",
        "seven formerly unclassified functions / 1,154 executable bytes",
        "82 formerly unclassified Ghidra functions / 19,520 executable bytes",
        "twelve formerly unclassified Ghidra functions / 2,776 bytes",
        "health-daily synthetic test fixture / 1,344 bytes",
        "four-function / 1,740-byte R1 product closure",
        "six-function / 1,890-byte GoMore activity-state window classifier",
        "four-function / 1,128-byte extension of the Goodix GH_SPO2/dlCom boundary",
        "58 functions / 19,274 bytes",
        "nineteen-function / 3,246-byte extension of the Goodix GH_NADT boundary",
        "0x0006E838` at `0x0006EA88",
        "nine-function / 2,360-byte GoMore energy-model boundary",
        "former 380-byte leader at `0x00040DE0`",
        "`0x00096CC8`",
        "former 374-byte leader at `0x00096CC8`",
        "strict 50/4,200 mV gates",
        "tied 372-byte leader at `0x00072C48`",
        "0x158-byte subcontext",
        "former 372-byte leader at `0x00041A40`",
        "10,000-tick",
        "seven-function / 1,964-byte extension of the Goodix GH_NADT boundary",
        "0x0006E838 -> 0x000968C4 -> 0x0002907C -> 0x00037890 -> 0x00034194",
        "0x00046FD4",
        "0x00059670",
        "0x000717AC",
        "0x0004101C",
        "0x00046650",
        "one-function / 578-byte R1 touch-task dispatcher boundary",
        "three-function / 1,448-byte unresolved sensor-stream framework boundary",
        "one-function / 416-byte R1 ATI calibration command closure",
        "native 406-byte R1 battery runtime entry",
        "one-function / 402-byte R1 PMIC charge-event policy closure",
        "two-function / 560-byte R1 BLE transmit-queue producer boundary",
        "0x0004011C",
        "16-function / 1,802-byte R1 structured-log record and live-cache boundary",
        "Twelve formerly unclassified Ghidra functions / 1,720 bytes",
        "four exact manual functions / 82 bytes",
        "three-function / 876-byte R1 `log.bin` circular-page writer boundary",
        "602 bytes is now routed into the licensed GoMore",
        "bringing the GoMore boundary to 248 exact",
        "two-function / 616-byte R1 HRV synchronization-flush boundary",
        "two-function / 578-byte R1 heart-rate synchronization-flush boundary",
        "two-function / 578-byte R1 SpO2 synchronization-flush boundary",
        "one-function / 528-byte GoMore SDK",
        "two-function / 856-byte Goodix packed-channel boundary",
        "one-function / 518-byte Goodix GH_NADT",
        "one-function / 514-byte Goodix register-profile",
        "seven-function / 1,098-byte Goodix GH_NADT peak-mask",
        "one-function / 494-byte R1 compiled-default restore",
        "30-function / 5,126-byte Goodix GH_NADT accumulation",
        "Two FreeRTOS static-memory callbacks / 36 bytes",
        "A FreeRTOS stack-overflow callback / 72 bytes",
        "Application `SystemInit` and `nvmc_config` / 544 bytes",
        "Nordic `xfer_completeness_check` / 98 bytes",
        "Ten Nordic Peer Manager GATT-cache functions / 784 bytes",
        "Five Nordic BLE/Peer Manager static helpers / 158 bytes",
        "FreeRTOS 10.5.1 `prvReloadTimer` / 40 bytes",
        "Eight resolved branch-only thunks / 32 bytes",
        "Eight Nordic BLE advertising functions / 992 bytes",
        "Eight newly routed Nordic buttonless-DFU functions / 668 Ghidra bytes",
        "Two Nordic power-management shutdown functions / 332 bytes",
        "Twelve retained reset-trace functions / 598 bytes",
        "Two reset-reason functions / 834 bytes",
        "1,736-byte BLE-thread event consumer",
        "former 464-byte leader at `0x0004E258`",
        "all 23 handler destinations",
        "three-function / 850-byte R1",
        "3,599/3,600-second boundary",
        "former 434-byte leader at `0x00041816`",
        "unknown_shared_quantized_neural_runtime_candidate",
        "two-function / 860-byte R1",
        "explicit cross-role conflict",
        "0x0003FAA4",
        "0x00043CA0",
        "0x00040984",
        "time/hour rollover planners",
    ):
        require(remaining_frontier, marker)
    resolved_thunks_doc = DOCS / "RESOLVED-THUNK-CLOSURE.md"
    for marker in (
        "Eight formerly unclassified application entries",
        "0x00029D58..<0x00029D5C",
        "0x0006F8F6..<0x0006F8FA",
        "0x0008E69C..<0x0008E6A0",
        "python3 tools/evidence/summarize_r1_resolved_thunks.py",
        "aliases of already implemented product-owned metadata operations",
    ):
        require(resolved_thunks_doc, marker)
    nordic_advertising_doc = DOCS / "NORDIC-ADVERTISING-START-CLOSURE.md"
    for marker in (
        "Eight formerly unclassified application functions",
        "0x00051710..<0x00051716",
        "0x00051716..<0x000517FE",
        "0x000517FE..<0x00051806",
        "0x00051806..<0x00051870",
        "0x00051870..<0x00051AA0",
        "0x00064F1A..<0x00064F42",
        "0x0007F0C8..<0x0007F0DE",
        "0x00094DD8..<0x00094DF0",
        "components/ble/ble_advertising/ble_advertising.c",
        "python3 tools/evidence/summarize_r1_nordic_advertising_closure.py",
    ):
        require(nordic_advertising_doc, marker)
    nordic_buttonless_dfu_doc = DOCS / "NORDIC-BUTTONLESS-DFU-CLOSURE.md"
    for marker in (
        "Ten recovered application functions",
        "NRF_DFU_BLE_BUTTONLESS_SUPPORTS_BONDS=0",
        "0x0005203C..<0x0005204A",
        "0x0005207C..<0x00052090",
        "0x00052154..<0x000521D4",
        "0x000522D8..<0x00052326",
        "0x0007CDC8..<0x0007CE2C",
        "manual provenance supplement",
        "python3 tools/evidence/summarize_r1_nordic_buttonless_dfu_closure.py",
    ):
        require(nordic_buttonless_dfu_doc, marker)
    nordic_power_mgmt_doc = DOCS / "NORDIC-POWER-MANAGEMENT-CLOSURE.md"
    for marker in (
        "Two formerly unclassified application functions / 332 bytes",
        "0x00079D50..<0x00079DA8",
        "0x0008F234..<0x0008F328",
        "NRF_PWR_MGMT_CONFIG_USE_SCHEDULER=0",
        "SOFTDEVICE_PRESENT",
        "python3 tools/evidence/summarize_r1_nordic_power_management_closure.py",
    ):
        require(nordic_power_mgmt_doc, marker)
    reset_trace_doc = DOCS / "RESET-TRACE-CORRELATION.md"
    for marker in (
        "Twelve recovered functions / 598 bytes",
        "0x00027484..<0x00027488",
        "0x00058A9A..<0x00058AB8",
        "0x0007EEDA..<0x0007EF06",
        "0x0007A5E0..<0x0007A604",
        "Modbus CRC16",
        "persist tag `7`",
        "Nordic SDK 17.1.0 CMSIS `NVIC_SystemReset`",
        "python3 tools/evidence/summarize_r1_reset_trace_closure.py",
    ):
        require(reset_trace_doc, marker)
    reset_reason_doc = DOCS / "RESET-REASON-CORRELATION.md"
    for marker in (
        "Two recovered functions / 834 bytes",
        "0x00077E98..<0x00077EE8",
        "0x0008198C..<0x00081BF8",
        "0x00081FB8..<0x0008203E",
        "0x0007000F",
        "Nordic `nrf_power_resetreas_get/clear`",
        "python3 tools/evidence/summarize_r1_reset_reason_closure.py",
    ):
        require(reset_reason_doc, marker)
    connection_control_doc = DOCS / "CONNECTION-CONTROL-CORRELATION.md"
    for marker in (
        "1,736 executable bytes",
        "0x00045184..<0x00045B16",
        "0x00091FD2",
        "pm_conn_secure(connection, false)",
        "event `0x00000200`",
        "device-info offsets 8 and 14",
        "unclassified along with unresolved timer/role/accessor callees",
        "python3 tools/evidence/summarize_r1_connection_control.py",
        "python3 tools/evidence/emulate_r1_connection_control.py",
    ):
        require(connection_control_doc, marker)
    peer_manager_event_doc = DOCS / "PEER-MANAGER-EVENT-POLICY-CORRELATION.md"
    for marker in (
        "1,052-byte R1 product callback",
        "0x0007F2B0..<0x0007F6AA",
        "0x0007F9EC..<0x0007FA0E",
        "0x0007F2B1",
        "pm_handler_on_pm_evt",
        "pm_handler_flash_clean",
        "allow_repairing = true",
        "performs no whitelist mutation",
        "never logs",
        "python3 tools/evidence/summarize_r1_peer_manager_event_policy.py",
    ):
        require(peer_manager_event_doc, marker)
    nv_recovery_doc = DOCS / "NV-RECOVERY-CORRELATION.md"
    for marker in (
        "Four functions / 1,740 executable bytes",
        "Two functions / 1,458 bytes",
        "two valid functions / 282 bytes",
        "0x0007B634",
        "0x0007BBE8",
        "0x0007BD68",
        "0x0007C450",
        "CRC-16/MODBUS",
        "fill-only merge planner",
        "normal dispatcher continues to refuse live `nvRecover`",
        "python3 tools/evidence/summarize_r1_nv_recovery_closure.py",
    ):
        require(nv_recovery_doc, marker)
    nv_compiled_restore_doc = DOCS / "NV-COMPILED-RESTORE-CORRELATION.md"
    for marker in (
        "0x0007C52C` / 494 executable bytes",
        "0x00042BBE",
        "internal storage event `0x2005`",
        "0x0009A0F8..<0x0009A432",
        "4f0fe353d4a0b2d5ecdfc49a1a6d8c73f790d693c12ca3462ecbacb0bee5cf5c",
        "raw 59 identity rows are intentionally neither rendered",
        "live restore path remains disabled",
        "python3 tools/evidence/summarize_r1_nv_compiled_restore.py",
    ):
        require(nv_compiled_restore_doc, marker)
    touch_slider_doc = DOCS / "TOUCH-SLIDER-CORRELATION.md"
    for marker in (
        "Thirteen functions / 2,784 executable bytes",
        "twelve formerly unclassified Ghidra functions / 2,776 bytes",
        "0x00092CBD",
        "0x0008E7CC",
        "0x00092CBC",
        "0x0003E938",
        "0x000933FC..<0x00093404",
        "213.3333282470703",
        "2,501-raw-unit window",
        "0x80",
        "python3 tools/evidence/summarize_r1_touch_slider_closure.py",
    ):
        require(touch_slider_doc, marker)
    health_daily_test_doc = DOCS / "HEALTH-DAILY-TEST-CORRELATION.md"
    for marker in (
        "0x0008B378",
        "1,344-byte dormant R1 product test fixture",
        "No direct caller",
        "0x0008D40C..<0x0008D4C2",
        "0x0008E560..<0x0008E626",
        "75cfeeac1565b8d44e251089066133f06e946af53ed3a849f230787c436ee255",
        "python3 tools/evidence/summarize_r1_health_daily_test.py",
    ):
        require(health_daily_test_doc, marker)
    gomore_neural_runtime_doc = DOCS / "GOMORE-NEURAL-RUNTIME-BOUNDARY.md"
    for marker in (
        "0x00076BDC..<0x000770AE",
        "1,234-byte indirect",
        "0x00076BDD",
        "0x00074B40",
        "sixteen exact direct callsites",
        "0x0002874C",
        "0x0002966C",
        "0x0004387C",
        "61c6cdae7f85eb4096726de5fe67c5c7f85ce4bc6991ef4d45a19825779875ea",
        "python3 tools/evidence/summarize_r1_gomore_neural_runtime.py",
    ):
        require(gomore_neural_runtime_doc, marker)
    gomore_sleep_graph_doc = DOCS / "GOMORE-SLEEP-GRAPH-PROVIDER-BOUNDARY.md"
    for marker in (
        "Six formerly unclassified functions / 2,188 executable bytes",
        "0x0002874C",
        "0x00028B8A",
        "0x0002966C",
        "0x000340A0",
        "0x00048D22",
        "0x00072BE0",
        "0x000BCF40",
        "0x00072BE1, 0x00048D23, 0x00028B8B",
        "21,824",
        "0x0004387C",
        "vendor_source_required_not_redistributable",
        "python3 tools/evidence/summarize_r1_gomore_sleep_graphs.py",
    ):
        require(gomore_sleep_graph_doc, marker)
    gomore_activity_state_doc = DOCS / "GOMORE-ACTIVITY-STATE-PROVIDER-BOUNDARY.md"
    for marker in (
        "Six formerly unclassified functions / 1,890 executable bytes",
        "0x0006138C",
        "0x00064A98",
        "0x0006859C",
        "0x00069FA8",
        "0x00093FAC",
        "0x00096E74",
        "three eight-byte `TBB` data tables",
        "25-sample",
        "250 samples",
        "seven internal states",
        "vendor_source_required_not_redistributable",
        "python3 tools/evidence/summarize_r1_gomore_activity_state_classifier.py",
    ):
        require(gomore_activity_state_doc, marker)
    gomore_energy_model_doc = DOCS / "GOMORE-ENERGY-MODEL-PROVIDER-BOUNDARY.md"
    for marker in (
        "Nine formerly unclassified functions / 2,360 executable bytes",
        "0x0005F56C",
        "0x0002F488",
        "0x0007DA30",
        "0x00088BD0",
        "0x00088D4C..<0x00088D4E",
        "4a1eeec9e1e5b6b5563e814c2f17e74d9adb8f1af90fe46a85e6bf95c59aed6a",
        "vendor_source_required_not_redistributable",
        "python3 tools/evidence/summarize_r1_gomore_energy_model.py",
    ):
        require(gomore_energy_model_doc, marker)
    gomore_iir_designer_doc = DOCS / "GOMORE-IIR-DESIGNER-PROVIDER-BOUNDARY.md"
    for marker in (
        "0x000717AC` / 602 executable bytes",
        "0x000717AC..<0x00071A06",
        "0x00071D62",
        "0x00071D76",
        "0x00038A5C",
        "0x0003AE04",
        "0x0003A620",
        "248 exact functions",
        "vendor_source_required_not_redistributable",
        "emits no algorithm or generated coefficients",
        "python3 tools/evidence/summarize_r1_gomore_iir_designer.py",
    ):
        require(gomore_iir_designer_doc, marker)
    gomore_auth_parser_doc = DOCS / "GOMORE-AUTH-PARSER-PROVIDER-BOUNDARY.md"
    for marker in (
        "0x0008EA0C` / 528 executable bytes",
        "0x0006B27C",
        "0x0006B38A",
        "gomore_setAuthParameters",
        "4d168fed892590719ff7187b985bd55011be122106dc85f192cc300a05c660d0",
        "89c30133f274cf13ec81bdd160439e31ea792bd70e19e157451895aeb4d851d7",
        "0x000891A4",
        "0x00027854",
        "vendor_source_required_not_redistributable",
        "exposes no live authentication operation",
        "python3 tools/evidence/summarize_r1_gomore_auth_parser.py",
    ):
        require(gomore_auth_parser_doc, marker)
    gomore_sleep_statistics_doc = \
        DOCS / "GOMORE-SLEEP-STAGE-STATISTICS-PROVIDER-BOUNDARY.md"
    for marker in (
        "Three formerly unclassified functions / 796 executable bytes",
        "0x00068FD4..<0x0006911A",
        "0x00069128..<0x000692D6",
        "0x0006951E..<0x00069546",
        "7602275b0249f68eed4ef03295b1c3ae05adc949d71b71ea9b81f668afbeda0c",
        "0x00068FB4 -> 0x00069128",
        "seven-value interval/efficiency block",
        "twelve-value stage-statistics block",
        "vendor_source_required_not_redistributable",
        "python3 tools/evidence/summarize_r1_gomore_sleep_stage_statistics.py",
    ):
        require(gomore_sleep_statistics_doc, marker)
    structured_log_doc = DOCS / "STRUCTURED-LOG-CACHE-CORRELATION.md"
    for marker in (
        "Sixteen functions / 1,802 executable bytes",
        "Twelve are Ghidra inventory",
        "four exact functions / 82 bytes",
        "0x00046FD4",
        "0x00091638",
        "0x00041D30",
        "0x7B",
        "0xDC000000",
        "32 bytes",
        "sixteen bytes",
        "4,096-byte persistence",
        "10,000 timing gate",
        "Nordic SDK 17.1.0 logging sources",
        "Arm C/EABI",
        "log.bin` flash writer",
        "no live ring or private log content",
        "python3 tools/evidence/summarize_r1_structured_log_cache.py",
    ):
        require(structured_log_doc, marker)
    log_bin_writer_doc = DOCS / "LOG-BIN-WRITER-CORRELATION.md"
    for marker in (
        "Three formerly unclassified functions / 876 executable bytes",
        "0x0005908C",
        "0x000590AC",
        "0x00059670",
        "0x000914D2",
        "twelve 4,096-byte sectors",
        "byte offset four",
        "FAL 0.5.99",
        "flash device's read, write, and erase callbacks",
        "composite private-log virtual file",
        "exposes no live sender or flash-mutation interface",
        "python3 tools/evidence/summarize_r1_log_bin_writer.py",
    ):
        require(log_bin_writer_doc, marker)
    hrv_sync_flush_doc = DOCS / "HRV-SYNC-FLUSH-CORRELATION.md"
    for marker in (
        "Two formerly unclassified functions / 616 executable bytes",
        "0x00040964",
        "0x0004101C",
        "0x00041638",
        "0x0008C750",
        "13 + count * 7",
        "eight-byte context",
        "pvPortMalloc` / `vPortFree",
        "0x0008ADA4",
        "0x0008ACFC",
        "0x0008362C",
        "exposes no live sender",
        "python3 tools/evidence/summarize_r1_hrv_sync_flush.py",
    ):
        require(hrv_sync_flush_doc, marker)
    hr_sync_flush_doc = DOCS / "HR-SYNC-FLUSH-CORRELATION.md"
    for marker in (
        "Two formerly unclassified functions / 578 executable bytes",
        "0x0003FA84",
        "0x0004011C",
        "0x00040700",
        "0x0008C150",
        "12 + count * 4",
        "eight-byte context",
        "pvPortMalloc` / `vPortFree",
        "0x0008ADA4",
        "0x0008ACFC",
        "0x0008359E",
        "exposes no live sender",
        "python3 tools/evidence/summarize_r1_hr_sync_flush.py",
    ):
        require(hr_sync_flush_doc, marker)
    spo2_sync_flush_doc = DOCS / "SPO2-SYNC-FLUSH-CORRELATION.md"
    for marker in (
        "Two formerly unclassified functions / 578 executable bytes",
        "0x00043C80",
        "0x000442F4",
        "0x000448B0",
        "0x0008CD60",
        "12 + count * 4",
        "eight-byte context",
        "pvPortMalloc` / `vPortFree",
        "0x0008ADA4",
        "0x0008ACFC",
        "0x00083792",
        "exposes no live sender",
        "python3 tools/evidence/summarize_r1_spo2_sync_flush.py",
    ):
        require(spo2_sync_flush_doc, marker)
    touch_task_dispatcher_doc = DOCS / "TOUCH-TASK-DISPATCHER-CORRELATION.md"
    for marker in (
        "0x00046650` / 578 executable bytes",
        "0x00046650..<0x000467FA",
        "0x0004FB24..<0x0004FB3E",
        "3019299c9c23cbed488c51229722b18cf0166ccae126bef2cdc3a49b615fab00",
        "0x00092822",
        "0x000040...0x000800",
        "0x00046F60",
        "0x0002F866",
        "0x00046F54",
        "clean_room_adapter_only_use_pinned_provider",
        "performs no live GPIO or I2C operation",
        "python3 tools/evidence/summarize_r1_touch_task_dispatcher.py",
    ):
        require(touch_task_dispatcher_doc, marker)
    sensor_stream_framework_doc = DOCS / "SENSOR-STREAM-FRAMEWORK-BOUNDARY.md"
    for marker in (
        "three-function / 1,448-byte",
        "0x00089890` / 464 executable bytes",
        "0x00089890..<0x00089A60",
        "2c0548e1abf6024d7dcb79b9e1768a9ac4687de976aaa80896ccd6912866e15c",
        "0x0008A1E1",
        "0x0008A1E0..<0x0008A310",
        "0x00089BA8..<0x00089C1E",
        "86e00a0dc3b033c1b4c0ab1414c1fc94b87e0679190ead386c6b2df7f8d444e4",
        "unknown_sensor_stream_framework_candidate",
        "0x00089B08..<0x00089B60",
        "0x0008A180..<0x0008A1AA",
        "6fd417efc7c460d1d8e2a3c234f8fd33b9d04b4324f04f2fcb251a07acefcf3a",
        "25 direct callsites in 20 caller functions",
        "0x00049410",
        "0x0006F228",
        "1024 / maximum_rate",
        "must not clone this unidentified registry architecture",
        "python3 tools/evidence/summarize_r1_sensor_stream_register.py",
        "python3 tools/evidence/summarize_r1_sensor_stream_unregister.py",
        "python3 tools/evidence/summarize_r1_sensor_stream_dispatch.py",
    ):
        require(sensor_stream_framework_doc, marker)
    ble_tx_queue_doc = DOCS / "BLE-TX-QUEUE-DISPATCH-CORRELATION.md"
    for marker in (
        "Two formerly unclassified functions / 560 executable bytes",
        "0x00034064",
        "0x00034070",
        "0x0003E274..<0x0003E48C",
        "align4(payload_length + 15)",
        "at least 90 percent",
        "raw timeout 100",
        "thread flag 1",
        "0x0004CB34",
        "0x0004CBA4",
        "exposes no live BLE sender",
        "python3 tools/evidence/summarize_r1_ble_tx_queue_dispatch.py",
    ):
        require(ble_tx_queue_doc, marker)
    wear_fusion_doc = DOCS / "WEAR-FUSION-CORRELATION.md"
    for marker in (
        "seven R1 product functions byte-pinned",
        "seven Ghidra functions total 1,506 bytes",
        "0x0003D45C..<0x0003D63C",
        "9,050,000",
        "strictly between `972.0` and `1076.0`",
        "sensor-stream framework",
        "tools/evidence/summarize_r1_wear_fusion_closure.py",
    ):
        require(wear_fusion_doc, marker)
    connection_parameter_doc = DOCS / "CONNECTION-PARAMETER-POLICY-CORRELATION.md"
    for marker in (
        "four R1 product functions / 498 bytes byte-pinned",
        "0x00051AA0..<0x00051C78",
        "strictly below `50`",
        "4 ms delay",
        "2,000 ms",
        "tools/evidence/summarize_r1_connection_parameter_policy.py",
    ):
        require(connection_parameter_doc, marker)
    sleep_sync_packet_doc = DOCS / "SLEEP-SYNC-PACKET-CORRELATION.md"
    for marker in (
        "472-byte product function byte-pinned",
        "0x0008DA24..<0x0008DBFC",
        "d3804f3dd415358d10ced85de5f8cccc64da4db33d40e37830d05096b7b86ac5",
        "946080000",
        "r1_sleep_build_sync_packet",
        "tools/evidence/summarize_r1_sleep_sync_packet.py",
    ):
        require(sleep_sync_packet_doc, marker)
    nfc_dock_policy_doc = DOCS / "NFC-DOCK-POLICY-CORRELATION.md"
    for marker in (
        "Four R1 adapter functions / 620 executable bytes",
        "0x00077430..<0x00077602",
        "ae5760b9a6ac03ac46642f7e19b90b11b0e630c406e443902ce1cb31c99a30e1",
        "23-byte product packet",
        "heartbeat 61",
        "tools/evidence/summarize_r1_nfc_dock_policy.py",
    ):
        require(nfc_dock_policy_doc, marker)
    peer_target_doc = DOCS / "PEER-TARGET-POLICY-CORRELATION.md"
    for marker in (
        "three R1 product functions / 550 executable bytes",
        "0x0004CCCC..<0x0004CE9C",
        "46631ec1f7328b6ae5946d07214624383b3f700d29da918fbb5b9662c96a00e3",
        "three seven-byte slots",
        "accepts the connection",
        "must not be promoted into a trust boundary",
        "tools/evidence/summarize_r1_peer_target_policy.py",
    ):
        require(peer_target_doc, marker)
    legacy_command_dispatch_doc = DOCS / "LEGACY-COMMAND-DISPATCH-CORRELATION.md"
    for marker in (
        "one R1 product function / 464 executable bytes",
        "0x0004E258..<0x0004E428",
        "be3357d945c4470611d70da7e97691fe9fb6a87bbda16b8da2e6d3eea48e3ca1",
        "23 recognized opcodes",
        "0x2001A174",
        "3-to-36-byte",
        "handler retains its own ownership",
        "python3 tools/evidence/summarize_r1_legacy_command_dispatch.py",
    ):
        require(legacy_command_dispatch_doc, marker)
    validated_sleep_delivery_doc = DOCS / "VALIDATED-SLEEP-DELIVERY-CORRELATION.md"
    for marker in (
        "three R1 product functions / 850 executable bytes",
        "0x0005B890..<0x0005B9AC",
        "0x0008DD90..<0x0008DF42",
        "5f375de1093b593b9df32fa774b51ffa063e7086884562e01633838373530e6c",
        "Exactly 3,600 passes",
        "storage event `0x2000`",
        "argument `6`",
        "at most 3,888 bytes",
        "destructive reset",
        "python3 tools/evidence/summarize_r1_validated_sleep_delivery.py",
    ):
        require(validated_sleep_delivery_doc, marker)
    quantized_pooling_doc = DOCS / "QUANTIZED-POOLING-PROVIDER-BOUNDARY.md"
    for marker in (
        "six functions / 1,328 bytes",
        "0x00041816..<0x000419C8",
        "a1ac9ab4d9a3ea8143872c726b60ae7c4d778f66ac8afab9b4d39816dca0cb09",
        "0x00074C6C",
        "0x00074C8C",
        "0x000293FC..<0x000294B6",
        "0x00035E34..<0x00035F26",
        "0x00074CE4..<0x00074D02",
        "0x00093628..<0x000936F8",
        "GoMore sleep classifier",
        "Goodix GH_SPO2 graph",
        "unknown_shared_quantized_neural_runtime_candidate",
        "Similarity to generic",
        "python3 tools/evidence/summarize_r1_quantized_pooling_boundary.py",
    ):
        require(quantized_pooling_doc, marker)
    connection_role_doc = DOCS / "CONNECTION-ROLE-ASSIGNMENT-CORRELATION.md"
    for marker in (
        "two symmetric R1 product functions / 860 executable bytes",
        "0x0004D654..<0x0004D802",
        "0x0004DA28..<0x0004DBD6",
        "0x200064B2",
        "R1_CONNECTION_ROLE_ASSIGN_CROSS_ROLE_CONFLICT",
        "python3 tools/evidence/summarize_r1_connection_role_assignment.py",
    ):
        require(connection_role_doc, marker)
    eus_rx_doc = DOCS / "EUS-RX-REASSEMBLY-CORRELATION.md"
    for marker in (
        "0x00032198..<0x00032340",
        "424",
        "a91ae73ec32df232276ab2e01dcd4c4e29f864de03b66f5addcea96350688df5",
        "0x0005D69C",
        "4,063 inbound logical bytes",
        "(first_sequence + 1) * 239",
        "duplicate or discontinuous sequences",
        "clean_room_behavior_only_security_preserving",
        "python3 tools/evidence/summarize_r1_eus_rx_reassembly.py",
    ):
        require(eus_rx_doc, marker)
    bae8_router_doc = DOCS / "BAE8-EVENT-ROUTER-CORRELATION.md"
    for marker in (
        "0x0005D5E0..<0x0005D782",
        "a767809ef6dd28fd1e49ca67838942c7eae79ea180b781f0e8dcc7d078d3c7d3",
        "0x0005D5E1",
        "0x0004E6E4",
        "0x0004E66C",
        "0x000529BC",
        "service callback offset `0x2C`",
        "`6`, `7`",
        "r1_runtime_plan_bae8_event",
        "python3 tools/evidence/summarize_r1_bae8_event_router.py",
    ):
        require(bae8_router_doc, marker)
    ati_calibration_doc = DOCS / "ATI-CALIBRATION-COMMAND-CORRELATION.md"
    for marker in (
        "0x0006210C",
        "416 executable bytes",
        "843951c84bc7b1def3a71058540210ee6eab68aacd2d20eb17e1e3e772664f98",
        "0x00062132",
        "opcode `0x91`",
        "eleven subcommands",
        "`0x40` through `0x800`",
        "source `2`",
        "r1_ati_calibration_plan_command",
        "python3 tools/evidence/summarize_r1_ati_calibration_command.py",
    ):
        require(ati_calibration_doc, marker)
    pmic_charge_event_doc = DOCS / "PMIC-CHARGE-EVENT-CORRELATION.md"
    for marker in (
        "0x00096AD0..<0x00096C62",
        "a079977932ae1d297bb451311bc998e001d9b3ae13efe0ff2769f14bc00ef67a",
        "0x000463DE",
        "0x00047F68",
        "0x00047F82",
        "24-byte working",
        "ASCII `2.2.6.0009`",
        "0x40808312",
        "0x4160F5C3",
        "02=F8",
        "r1_pmic_plan_charge_event",
        "python3 tools/evidence/summarize_r1_pmic_charge_event.py",
    ):
        require(pmic_charge_event_doc, marker)
    pmic_charged_notification_doc = \
        DOCS / "PMIC-CHARGED-NOTIFICATION-CORRELATION.md"
    for marker in (
        "0x00047F10..<0x00047F9A",
        "0x00096CC8..<0x00096DB4",
        "a00d2417c36d598e48d0372052fabccf0444ea0ced5a0252ba33983ad912a34f",
        "0x00046218",
        "0x000463D4",
        "strictly below 50 mV",
        "strictly below 4,200 mV",
        "while retaining\nthe incremented counter",
        "5,120 ms",
        "r1_pmic_plan_charged_notification",
        "python3 tools/evidence/summarize_r1_pmic_charged_notification.py",
    ):
        require(pmic_charged_notification_doc, marker)
    iqs_ati_audit_doc = DOCS / "IQS7211E-ATI-AUDIT-CORRELATION.md"
    for marker in (
        "0x00041A40..<0x00041BB4",
        "51820b7e27a675b7dd1b217f477e4aeaa7d3cd75ee5dd913bbdae642d4c109c3",
        "0x0006FA2A",
        "at least 10,000 ticks",
        "register `0xE3`",
        "21 little-endian UInt16",
        "r1_iqs7211e_ati_audit_begin",
        "r1_iqs7211e_ati_audit_summarize",
        "python3 tools/evidence/summarize_r1_iqs7211e_ati_audit.py",
    ):
        require(iqs_ati_audit_doc, marker)
    goodix_nadt_doc = DOCS / "GOODIX-NADT-PROVIDER-BOUNDARY.md"
    for marker in (
        "58 functions / 19,274 executable bytes",
        "57 functions / 19,148 bytes",
        "0x0002CDD4",
        "0x0006E008",
        "0x000856EC",
        "0x00047240",
        "0x0006E838 -> 0x000766AC -> 0x00035850",
        "0x0006E838 -> 0x00036F88",
        "0x0006E838 -> 0x00095828 -> 0x00029144",
        "0x0006E838 -> 0x000968C4 -> 0x0002907C -> 0x00037890 -> 0x00034194",
        "seven-function / 1,964-byte",
        "18b51a96c3f0c3d0c9c47727c5ec8f5a569e603ad2c882e74fef43f84588e285",
        "functions / 3,246 bytes",
        "509a3440ed4c47ba3c10db0911eb66bff2fbe1bf804e294ad5fe024dad5b98eb",
        "1c454b3b53453c7d2e53dc9c04a6ed66c3d82d85b1e3dc7d389085d1cc59f3f3",
        "c9fbb161215e9026649909ed8ef04b628221d7d51cbd4affb3c04f0a4c6a6c7a",
        "adf8c54c2b2af59806f5a940cb1470aa71c010e3918ce4725559063151b25c33",
        "GH_NADT_pre",
        "v1.0.2.0",
        "548d894d",
        "25 samples",
        "vendor_source_required_not_redistributable",
        "python3 tools/evidence/summarize_r1_goodix_nadt_boundary.py",
    ):
        require(goodix_nadt_doc, marker)
    goodix_hr_doc = DOCS / "GOODIX-HR-PROCESSING-PROVIDER-BOUNDARY.md"
    for marker in (
        "31 formerly unclassified functions / 7,144 executable bytes",
        "0x00032808` / 2,814 bytes",
        "0x0006D51C",
        "0x0006D5FA",
        "at most four levels",
        "zero outside direct callers",
        "GH_HR_exc_pv_v2.0.3.0_CONF_nc_21d2063d_002271a1",
        "vendor_source_required_not_redistributable",
        "0x00032808..<0x00032C10",
        "python3 tools/evidence/summarize_r1_goodix_hr_boundary.py",
    ):
        require(goodix_hr_doc, marker)
    goodix_hrv_doc = DOCS / "GOODIX-HRV-PROVIDER-BOUNDARY.md"
    for marker in (
        "nine-function / 1,288-byte lifecycle",
        "Seven formerly unclassified functions / 1,154 bytes",
        "0x0002CAC6",
        "0x0002CC5C",
        "0x0006DAD0",
        "0x0006DB5C",
        "0x0006DF14",
        "0x0006DF60",
        "pv_v1.1.0",
        "GH_HRV_pre_pv_v1.0.1.0_ed953ff3",
        "vendor_source_required_not_redistributable",
        "python3 tools/evidence/summarize_r1_goodix_hrv_boundary.py",
    ):
        require(goodix_hrv_doc, marker)
    goodix_channel_decoder_doc = DOCS / "GOODIX-CHANNEL-DECODER-PROVIDER-BOUNDARY.md"
    for marker in (
        "Two formerly unclassified functions / 856 executable bytes",
        "0x000335B4",
        "0x00061DA4",
        "0x0006E874",
        "0x00066890",
        "0x00061E42",
        "0x00061E86",
        "0x00061ECA",
        "vendor_source_required_not_redistributable",
        "emits no private coefficients",
        "python3 tools/evidence/summarize_r1_goodix_channel_decoder.py",
    ):
        require(goodix_channel_decoder_doc, marker)
    goodix_nadt_quality_doc = DOCS / "GOODIX-NADT-QUALITY-PROVIDER-BOUNDARY.md"
    for marker in (
        "0x00088E80` / 518 executable bytes",
        "0x0006E916",
        "0x0006E838",
        "GH_NADT_pre v1.0.2.0 / 548d894d",
        "21a9202e4352d08144ee2a1e8a2bf7e63d6776a408fda69b0a98923af823fb52",
        "vendor_source_required_not_redistributable",
        "emits no private thresholds",
        "python3 tools/evidence/summarize_r1_goodix_nadt_quality.py",
    ):
        require(goodix_nadt_quality_doc, marker)
    goodix_nadt_peak_mask_doc = DOCS / "GOODIX-NADT-PEAK-MASK-PROVIDER-BOUNDARY.md"
    for marker in (
        "Seven formerly unclassified functions / 1,098 executable bytes",
        "0x00030178",
        "0x0006E8E6",
        "GH_NADT_pre v1.0.2.0 / 548d894d",
        "vendor_source_required_not_redistributable",
        "emits no algorithm implementation",
        "python3 tools/evidence/summarize_r1_goodix_nadt_peak_mask.py",
    ):
        require(goodix_nadt_peak_mask_doc, marker)
    goodix_nadt_accumulation_doc = \
        DOCS / "GOODIX-NADT-ACCUMULATION-PROVIDER-BOUNDARY.md"
    for marker in (
        "Thirty formerly unclassified functions / 5,126 executable bytes",
        "0x00072DCC` / 490 bytes",
        "zero outside non-Goodix callers",
        "0x0002FEE2..<0x0002FF0E",
        "0x0009293E..<0x0009295A",
        "GH_NADT_pre v1.0.2.0 / 548d894d",
        "vendor_source_required_not_redistributable",
        "python3 tools/evidence/summarize_r1_goodix_nadt_accumulation.py",
    ):
        require(goodix_nadt_accumulation_doc, marker)
    goodix_register_profile_doc = DOCS / "GOODIX-REGISTER-PROFILE-PROVIDER-BOUNDARY.md"
    for marker in (
        "0x0002B6E0` / 514 executable bytes",
        "0x0002A810",
        "25a1ec257775b73fe1310c36758df77a32bed3314de24d61b8574c0fe9e61a4f",
        "f00d34b85455f97445d8df49ec029d56a569c909aa1fcc2c5941c90202669f0e",
        "vendor_source_required_not_redistributable",
        "no live register I/O",
        "python3 tools/evidence/summarize_r1_goodix_register_profile.py",
    ):
        require(goodix_register_profile_doc, marker)
    goodix_spo2_dlcom_doc = DOCS / "GOODIX-SPO2-DLCOM-PROVIDER-BOUNDARY.md"
    for marker in (
        "85 functions / 19,568 executable bytes",
        "Ghidra functions / 19,520 executable bytes",
        "three manual provenance supplements / 48 bytes",
        "0x0002C944",
        "0x0002CA24",
        "0x0006C6A8",
        "0x000742E4",
        "0x0006EB94 -> 0x0002F624 -> 0x00036C26",
        "0x00099030",
        "0x0009903C",
        "0x0004387C",
        "1,128 bytes",
        "0x000739A9",
        "0x00074A98",
        "seven functions / 2,264 bytes",
        "0x00036590",
        "0x00085F36",
        "0x000617F8",
        "0x000876C8",
        "0x000BD668",
        "provider-owned dormant residue",
        "0x000BCF58",
        "dlCom_pre2exc_pv_v1.3.0_c00c91c9",
        "GH_SPO2_pre_pv_v2.1.10.0",
        "277e89de",
        "1f1cf98b",
        "vendor_source_required_not_redistributable",
        "outside-caller exclusivity",
        "python3 tools/evidence/summarize_r1_goodix_spo2_dlcom_boundary.py",
    ):
        require(goodix_spo2_dlcom_doc, marker)
    time_calendar_boundary = DOCS / "TIME-CALENDAR-PROVIDER-BOUNDARY.md"
    for marker in (
        "Fourteen recovered functions",
        "unknown_time_calendar_provider_candidate",
        "0x0005A7BC..<0x0005A8A0",
        "0x0005A8AC..<0x0005A984",
        "0x0005AC74..<0x0005ACA6",
        "0x0008AD40..<0x0008AD5C",
        "0x0008AF40..<0x0008AF8A",
        "Nordic nRF5 SDK 17.1.0 tree has no matching",
        "implementation-blocked",
    ):
        require(time_calendar_boundary, marker)
    activity_accumulator = DOCS / "ACTIVITY-ACCUMULATOR-CORRELATION.md"
    for marker in (
        "0x00048D48..<0x00048D96",
        "0x00048E68..<0x00048FE4",
        "0x00049068..<0x00049164",
        "0x0005AA14..<0x0005AB0A",
        "0x0008A7F4..<0x0008A80A",
        "24-byte state",
        "595...599",
        "900 seconds inclusive",
        "steps 12 bits",
        "licensed-provider boundaries",
    ):
        require(activity_accumulator, marker)
    health_crash_snapshot = DOCS / "HEALTH-CRASH-SNAPSHOT-CORRELATION.md"
    for marker in (
        "Eleven recovered entries",
        "0x00058914..<0x00058936",
        "0x0005893C..<0x0005895C",
        "0x00058960..<0x0005897C",
        "0x00058980..<0x000589AA",
        "0x000589B0..<0x000589E4",
        "0x000589E8..<0x00058A1E",
        "0x00058A24..<0x00058A3A",
        "0x00059EE4..<0x0005A150",
        "0x0005A28C..<0x0005A2B4",
        "0x0005A2B8..<0x0005A320",
        "0x0005A324..<0x0005A3CE",
        "0x0003F47C..<0x0003F530",
        "966 bytes",
        "896-byte opaque",
        "Modbus CRC16",
        "one-shot",
        "`0x0006ABE4`, the recovered blob lookup",
    ):
        require(health_crash_snapshot, marker)
    health_database_startup = \
        DOCS / "HEALTH-DATABASE-STARTUP-CORRELATION.md"
    for marker in (
        "0x00070028..<0x0007002C",
        "06936d0536d64e86c623270163a043c1b484bbc978af8fbf56cd1650cbfb6587",
        "0x00070030..<0x0007023E",
        "526-byte body",
        "67cf421c59889f89122546e1bfc3b349b163d78a2b679c398144f13c9fec55db",
        "at most 120 schema bytes",
        "health.db",
        "channels 1 followed by 0",
        "skip both database recovery",
        "fdb_tsl_iter_by_time",
        ".openr1_health_db_api",
        "r1_health_db_provider_handle",
        "time/calendar implementation remains blocked",
    ):
        require(health_database_startup, marker)
    require(PROJECT / "include" / "openr1" / "r1_health_db.h",
            "r1_health_db_startup_ops")
    require(PROJECT / "src" / "r1_health_db.c", "r1_health_db_startup")
    require(PROJECT / "tests" / "test_openr1.c",
            "test_health_database_startup")
    twi_sync = DOCS / "TWI-SYNCHRONIZATION-CORRELATION.md"
    for marker in (
        "0x00054FF8..<0x00055058",
        "c8acd79964fe902e645c7746a558e55c48193863ce1afd3ac589d89229230a64",
        "0x0005505C..<0x000550BA",
        "85b332cad963abfdc137fb17b01ee74e1a49cdbe74fcae0b371b4c5a1c307ed0",
        "0x000550C0..<0x0005511A",
        "1f2765c8851ddaeda3f395bd94de4d461671d3b76daf54ae3bce067a1b3fe0ca",
        "0x00055120..<0x0005517A",
        "92b75b75fcbc59ee64b0a6ae5730da7e3429c19c79f642ea158d3e5af5ea9f9b",
        "0x00055278..<0x000552DC",
        "4516b8fdac0d5e34250cc0b59617c94e06a17faf0d15e6d9bf880deadd81b08d",
        "0x000552E4..<0x00055326",
        "9f391a5cad85e928b15715c8d0ead9bc34b40b4cd96797a96dbb4da73bc8c1fe",
        "0x00070778..<0x000707C6",
        "ad1afebbb00454d0462173c6483d046232415ca58a07a27245e5ac8e3599a290",
        "0x00070820..<0x00070884",
        "e01f111c235bb727f1c37721cde083152dcf02e91c05f3ba4a16e5a2a1d6c30b",
        "0x0007088C..<0x000708F0",
        "5109e14190c48c15212304581af701dea173926b74dcc682d42aa6ad5dc599be",
        "state `0x20006FE8`",
        "state `0x20007054`",
        "`osKernelGetState()` returns exactly `2`",
        "nrfx_coredep_delay_us(64)",
        "payloads over 80 bytes",
        "NRF_ERROR_BUSY",
        "clean_room_adapter_only_use_nordic_sdk_and_cmsis",
        ".openr1_twi_sync_api",
        "not by proximity",
    ):
        require(twi_sync, marker)
    require(PROJECT / "include" / "openr1" / "r1_twi_sync.h",
            "r1_twi_sync_ops")
    require(PROJECT / "src" / "r1_twi_sync.c", "r1_twi_sync_wait")
    twi_sdk_adapter = PROJECT / "platform" / "nrf52840" / "sdk" / \
        "openr1_twi_sync.c"
    for marker in (
        "NRF_GPIO_PIN_DIR_OUTPUT",
        "NRF_GPIO_PIN_INPUT_DISCONNECT",
        "NRF_GPIO_PIN_NOPULL",
        "NRF_GPIO_PIN_S0S1",
        "(nrf_drv_twi_frequency_t)config->frequency",
        ".interrupt_priority = config->interrupt_priority",
        ".clear_bus_init = config->clear_bus_init",
        ".hold_bus_uninit = config->hold_bus_uninit",
        "nrfx_twim_disable",
        "nrfx_twim_uninit",
        "UINT32_C(0x0ffc)",
    ):
        require(twi_sdk_adapter, marker)
    require(PROJECT / "tests" / "test_openr1.c",
            "test_twi_synchronization_adapter")
    require(PROJECT / "src" / "r1_twi_sync.c",
            "r1_twi_primary_lifecycle_initialize")
    require(PROJECT / "src" / "r1_twi_sync.c",
            "r1_twi_secondary_lifecycle_initialize")
    bus_registration = DOCS / "BUS-REGISTRATION-CORRELATION.md"
    for marker in (
        "0x00054F90..<0x00054FBC",
        "0e1b2dbfdc68ac597dc2f5cacc0e26a9b14466bb5afe1ce353fd89ce5766a7cc",
        "0x00054FC4..<0x00054FF0",
        "2a087f558d9bc124cf2ad77e0621ee2776ef8f87aee88270a35262dcf561d83b",
        "0x00056508..<0x0005651A",
        "c7d415efc98ffaf074711600bdeaf04a11fec5528111b893e69c4797c499a826",
        "0x00056550..<0x00056562",
        "c6003bad98c688df45118e27e1ef5b17b9f4552c584701d9e05b9aae86957979",
        "clean_room_configuration_only_direct_typed_binding",
        "does not admit a GPIO-driven software-I2C engine",
    ):
        require(bus_registration, marker)
    software_twi_boundary = DOCS / "SOFTWARE-TWI-PROVIDER-BOUNDARY.md"
    for marker in (
        "Forty recovered functions",
        "3,524 executable bytes",
        "unknown_software_twi_provider_candidate",
        "0x00055330..<0x00055410",
        "0x0005547C..<0x00056274",
        "0x20007400",
        "P0.28 / P1.13",
        "P1.11 / P1.14",
        "implementation-blocked",
        "no live GPIO or I2C sender",
    ):
        require(software_twi_boundary, marker)
    rtc_device_boundary = DOCS / "RTC-DEVICE-PROVIDER-BOUNDARY.md"
    for marker in (
        "Nine exact functions",
        "798 executable bytes",
        "unknown_rtc_device_provider_candidate",
        "0x00056274..<0x000562E0",
        "0x000563C4..<0x000563F0",
        "0x0007AD6C..<0x0007AE20",
        "4,095",
        "produces eight ticks per",
        "implementation-blocked",
        "no live clock mutation",
    ):
        require(rtc_device_boundary, marker)
    yhm2710_boundary = DOCS / "YHM2710-I2C5-RESOURCE-BOUNDARY.md"
    for marker in (
        "Fifteen exact state-command functions",
        "1,018 executable bytes",
        "Fourteen functions / 1,000",
        "0x200075A4",
        "0x20007614",
        "yhmicros_yhm2710_candidate",
        "licensed provider",
    ):
        require(yhm2710_boundary, marker)
    watchdog_boundary = DOCS / "WATCHDOG-DEVICE-CORRELATION.md"
    for marker in (
        "seven exact functions",
        "386 executable bytes",
        "0x00056638..<0x00056654",
        "0x00056694..<0x000566A6",
        "0x0007B570..<0x0007B5E6",
        "10,000 milliseconds",
        "priority 6",
        "nrfx_wdt.c",
    ):
        require(watchdog_boundary, marker)
    sensor_heap_boundary = DOCS / "SENSOR-ALGORITHM-HEAP-PROVIDER-BOUNDARY.md"
    for marker in (
        "thirteen exact functions",
        "1,202 executable bytes",
        "unknown_sensor_algorithm_heap_provider_candidate",
        "sensor_algo_mem_fatal",
        "0x0002D460..<0x0002D4D6",
        "0x000982C2..<0x00098340",
        "not FreeRTOS `heap_4`",
        "not TLSF v3.1",
        "implementation-blocked",
    ):
        require(sensor_heap_boundary, marker)
    goodix_integrity_boundary = \
        DOCS / "GOODIX-PACKED-WORD-INTEGRITY-BOUNDARY.md"
    for marker in (
        "Seven exact functions / 236 executable bytes",
        "Five functions / 162 bytes",
        "0x00028E5C..<0x00028E70",
        "0x000294BC..<0x000294F2",
        "0x0005A5EC..<0x0005A622",
        "448ddc2f827f6109a389e73dcc8a34db1ba3b44812f760451944fb015221d936",
        "vendor_source_required_not_redistributable",
        "must not be recreated locally",
    ):
        require(goodix_integrity_boundary, marker)
    retained_log = DOCS / "RETAINED-LOG-CORRELATION.md"
    for marker in (
        "0x0007F030..<0x0007F0C2",
        "146-byte body",
        "3,008-byte retained buffer",
        "3,007-byte append-length ceiling",
        "3,006-byte normal payload",
        "SEGGER_RTT_Write",
        "vsnprintf",
        "out-of-bounds edge",
        ".openr1_retained_log_api",
    ):
        require(retained_log, marker)
    require(PROJECT / "src" / "r1_retained_log.c",
            "r1_retained_log_append_rendered")
    require(PROJECT / "tests" / "test_openr1.c", "test_retained_crash_log")
    require(PROJECT / "src" / "r1_iqs7211e.c", "R1_IQS7211E_ATI_RESTART_THRESHOLD")
    require(PROJECT / "src" / "r1_iqs7211e.c", "make_cycle_payload")
    require(PROJECT / "include" / "openr1" / "r1_iqs7211e.h",
            "R1_IQS7211E_RESTART_DELAY_TICKS")
    require(PROJECT / "tests" / "test_openr1.c", "test_iqs7211e_provider_boundary")
    require(PROJECT / "tests" / "test_openr1.c", "test_iqs7211e_ati_audit_policy")
    require(PROJECT / "src" / "r1_iqs7211e.c", "r1_iqs7211e_ati_audit_begin")
    require(PROJECT / "src" / "r1_iqs7211e.c", "r1_iqs7211e_ati_audit_summarize")
    require(PROJECT / "src" / "r1_st25dvxxkc.c",
            "r1_st25dvxxkc_mailbox_length_allowed")
    require(PROJECT / "src" / "r1_st25dvxxkc.c",
            "R1_ST25DVXXKC_SESSION_CLOSE_MSB")
    require(PROJECT / "src" / "r1_st25dvxxkc.c",
            "r1_st25dvxxkc_plan_dock_frame")
    require(PROJECT / "include" / "openr1" / "r1_st25dvxxkc.h",
            "R1_ST25DVXXKC_DOCK_CONTROL_PACKET_SIZE")
    require(PROJECT / "platform" / "nrf52840" / "sdk" / "openr1_nfc.c",
            "ST25DVxxKC_RegisterBusIO")
    require(PROJECT / "platform" / "nrf52840" / "sdk" / "openr1_nfc.c",
            "OPENR1_NFC_TWIM_SCL_PIN")
    require(PROJECT / "tests" / "test_openr1.c",
            "test_st25dvxxkc_provider_boundary")
    require(PROJECT / "tests" / "test_openr1.c",
            "test_st25dvxxkc_dock_policy")
    require(PROJECT / "src" / "r1_peer_target.c",
            "r1_peer_is_target_glasses")
    require(PROJECT / "include" / "openr1" / "r1_peer_target.h",
            "R1_PEER_SLOT_COUNT")
    require(PROJECT / "tests" / "test_openr1.c", "test_peer_target_policy")
    require(PROJECT / "src" / "r1_dispatch.c",
            "r1_legacy_command_route_frame")
    require(PROJECT / "src" / "r1_dispatch.c",
            "R1_LEGACY_COMMAND_ROUTE_PAIR_AUTH_0X88")
    require(PROJECT / "include" / "openr1" / "r1_dispatch.h",
            "R1_LEGACY_COMMAND_WORKSPACE_SIZE")
    require(PROJECT / "tests" / "test_openr1.c",
            "test_legacy_command_routing")
    require(PROJECT / "src" / "r1_dispatch.c",
            "r1_ati_calibration_plan_command")
    require(PROJECT / "include" / "openr1" / "r1_dispatch.h",
            "R1_ATI_CALIBRATION_ACTION_SEND_CONFIGURATION")
    require(PROJECT / "tests" / "test_openr1.c",
            "test_ati_calibration_command")
    require(PROJECT / "src" / "r1_battery.c",
            "r1_pmic_plan_charge_event")
    require(PROJECT / "src" / "r1_battery.c",
            "r1_pmic_plan_charged_notification")
    require(PROJECT / "include" / "openr1" / "r1_battery.h",
            "R1_PMIC_THERMAL_LOW_TARGET_WORD")
    require(PROJECT / "tests" / "test_openr1.c",
            "test_pmic_charge_event_policy")
    require(PROJECT / "tests" / "test_openr1.c",
            "test_pmic_charged_notification_policy")
    require(PROJECT / "src" / "r1_health.c",
            "r1_health_u16_ram_cache_merge")
    require(PROJECT / "tests" / "test_openr1.c",
            "test_hrv_ram_cache_merge")
    require(PROJECT / "src" / "r1_health.c",
            "r1_health_u8_ram_cache_merge")
    require(PROJECT / "tests" / "test_openr1.c",
            "test_scalar_health_ram_cache_merge")
    require(PROJECT / "src" / "r1_protocol.c",
            "r1_protocol_send_response")
    require(PROJECT / "tests" / "test_openr1.c",
            "test_protocol_response_orchestration")
    require(PROJECT / "src" / "r1_storage.c",
            "r1_export_plan_command")
    require(PROJECT / "tests" / "test_openr1.c", "test_export_planner")
    require(PROJECT / "src" / "r1_runtime.c",
            "r1_ble_thread_message_encode")
    require(PROJECT / "src" / "r1_runtime.c",
            "r1_glasses_status_plan_command")
    require(PROJECT / "src" / "r1_state.c",
            "r1_user_profile_plan_transition")
    require(PROJECT / "src" / "r1_peer_target.c",
            "r1_peer_bond_diagnostic_plan")
    require(PROJECT / "tests" / "test_openr1.c",
            "test_next_frontier_product_policies")
    require(PROJECT / "src" / "r1_runtime.c",
            "r1_factory_thread_message_encode")
    require(PROJECT / "src" / "r1_runtime.c",
            "r1_peripheral_watchdog_plan_step")
    require(PROJECT / "tests" / "test_openr1.c",
            "test_next_frontier_334_342_policies")
    require(PROJECT / "src" / "r1_health.c",
            "r1_health_clear_all_caches")
    require(PROJECT / "src" / "r1_health.c",
            "r1_temperature_pair_reduce")
    require(PROJECT / "tests" / "test_openr1.c",
            "test_next_frontier_314_328_policies")
    require(PROJECT / "src" / "r1_protocol.c",
            "r1_pb_fragment_message")
    require(PROJECT / "src" / "r1_event.c",
            "r1_delayed_event_schedule")
    require(PROJECT / "src" / "r1_health.c",
            "r1_health_settings_plan_command")
    require(PROJECT / "tests" / "test_openr1.c",
            "test_next_frontier_280_308_policies")
    require(PROJECT / "src" / "r1_battery.c",
            "r1_battery_diagnostic_cadence_step")
    require(PROJECT / "src" / "r1_storage.c",
            "r1_ep_scan_cursor")
    require(PROJECT / "src" / "r1_protocol.c",
            "r1_fragment_message")
    require(PROJECT / "tests" / "test_openr1.c",
            "test_next_frontier_264_274_policies")
    require(PROJECT / "src" / "r1_state.c",
            "r1_system_settings_plan_command")
    require(PROJECT / "src" / "r1_state.c",
            "r1_temperature_mode_plan_transition")
    require(PROJECT / "src" / "r1_goodix.c",
            "r1_goodix_diagnostic_select")
    require(PROJECT / "tests" / "test_openr1.c",
            "test_next_frontier_256_262_policies")
    require(PROJECT / "src" / "r1_storage.c",
            "r1_ep_plan_initialization")
    require(PROJECT / "src" / "r1_dispatch.c",
            "r1_legacy_device_info_build")
    require(PROJECT / "tests" / "test_openr1.c",
            "test_next_frontier_230_248_policies")
    require(PROJECT / "src" / "r1_event.c",
            "r1_delayed_event_cancel")
    require(PROJECT / "src" / "r1_state.c",
            "r1_heart_rate_mode_plan_transition")
    require(PROJECT / "src" / "r1_motion.c",
            "r1_ring_stability_observe")
    require(PROJECT / "src" / "r1_connection_params.c",
            "r1_connection_phy_update_plan")
    require(PROJECT / "platform" / "nrf52840" / "sdk" / "openr1_bae8.c",
            "sd_ble_gap_phy_update")
    require(PROJECT / "tests" / "test_openr1.c",
            "test_next_frontier_224_230_policies")
    require(PROJECT / "src" / "r1_storage.c",
            "r1_sleep_sync_plan_acknowledgement")
    require(PROJECT / "src" / "r1_state.c",
            "r1_system_control_command_37_plan")
    require(PROJECT / "src" / "r1_runtime.c",
            "r1_bae8_plan_hvx_result")
    require(PROJECT / "src" / "r1_storage.c",
            "r1_fds_plan_event")
    require(PROJECT / "platform" / "nrf52840" / "sdk" / "openr1_storage.c",
            "openr1_storage_plan_fds_event")
    require(PROJECT / "platform" / "nrf52840" / "sdk" /
            "openr1_cmbacktrace_port.c", "uxTaskGetSystemState")
    require(PROJECT / "tests" / "test_openr1.c",
            "test_next_frontier_212_222_policies")
    require(PROJECT / "src" / "r1_goodix.c",
            "r1_sensor_stream_registration_plan")
    require(PROJECT / "src" / "r1_health.c",
            "r1_activity_flash_record_enqueue_plan")
    require(PROJECT / "src" / "r1_connection_params.c",
            "r1_connection_parameter_mode_adapter")
    require(PROJECT / "platform" / "nrf52840" / "sdk" /
            "openr1_connection_params.c", "sd_ble_gap_ppcp_set")
    require(PROJECT / "platform" / "nrf52840" / "sdk" /
            "openr1_connection_params.c", "sd_ble_gap_conn_param_update")
    require(PROJECT / "src" / "r1_storage.c",
            "r1_latest_valid_flash_slot_scan_adapter")
    require(PROJECT / "tests" / "test_openr1.c",
            "test_next_frontier_204_210_policies")
    require(PROJECT / "tests" / "test_openr1.c",
            "test_legacy_device_info_builder")
    require(PROJECT / "src" / "r1_event.c",
            "r1_delayed_event_timer_step")
    require(PROJECT / "tests" / "test_openr1.c",
            "test_delayed_event_timer_step")
    require(PROJECT / "src" / "r1_health.c",
            "r1_sleep_plan_validated_delivery")
    require(PROJECT / "src" / "r1_health.c",
            "r1_sleep_plan_storage_consumer")
    require(PROJECT / "src" / "r1_sleep_db.c",
            "for (size_t attempt = 0u; attempt < 2u; ++attempt)")
    require(PROJECT / "include" / "openr1" / "r1_health.h",
            "R1_SLEEP_VALIDATED_MIN_DURATION_SECONDS")
    require(PROJECT / "tests" / "test_openr1.c",
            "test_validated_sleep_delivery_plans")
    require(PROJECT / "src" / "r1_connection_params.c",
            "r1_connection_role_assign")
    require(PROJECT / "tests" / "test_openr1.c",
            "test_connection_role_assignment")
    power_header = PROJECT / "include" / "openr1" / "r1_power_lease.h"
    for marker in (
        "R1_POWER_CLIENT_BATTERY_SAMPLING",
        "R1_POWER_CLIENT_OPTICAL_PPG",
        "R1_POWER_CLIENT_TOUCH",
        "set_shared_power_enabled",
    ):
        require(power_header, marker)
    power_source = PROJECT / "src" / "r1_power_lease.c"
    for marker in (
        "r1_power_lease_acquire", "r1_power_lease_release",
        "R1_ERROR_UNSUPPORTED", "active_client_mask == 0u",
    ):
        require(power_source, marker)
    require(PROJECT / "tests" / "test_openr1.c", "test_shared_power_lease")
    i2c5_resources = (
        PROJECT / "platform" / "nrf52840" / "sdk" /
        "openr1_i2c5_resources.c"
    )
    for marker in (
        "NRF_GPIO_PIN_MAP(1, 10)", "NRF_GPIO_PIN_H0H1",
        "osMutexNew", "osMutexAcquire", "openr1_nfc_bind_resources",
    ):
        require(i2c5_resources, marker)
    require(PROJECT / "platform" / "nrf52840" / "sdk" / "main.c",
            "openr1_i2c5_resources_initialize")
    motion_core = PROJECT / "src" / "r1_motion.c"
    for marker in (
        "R1_MOTION_POLICY_AUTO_LICENSED", "select_provider",
        "r1_motion_adapter_read_fifo", "normalize_axis",
        "R1_MOTION_FIFO_SAMPLE_LIMIT",
    ):
        require(motion_core, marker)
    motion_port = (
        PROJECT / "platform" / "nrf52840" / "sdk" / "openr1_motion.c"
    )
    for marker in (
        "openr1_twim1_acquire", "NRF_GPIO_PIN_MAP(0, 11)",
        "NRF_GPIO_PIN_MAP(0, 14)", "NRF_GPIO_PIN_MAP(0, 15)",
        "bma456w_init", "lis2dw12_device_id_get", "openr1_motion_api",
        "NRFX_GPIOTE_CONFIG_IN_SENSE_LOTOHI", "nrfx_gpiote_in_init",
        "osThreadFlagsSet", "selected_interrupt_dispatch",
    ):
        require(motion_port, marker)
    twim1_arbiter = (
        PROJECT / "platform" / "nrf52840" / "sdk" / "openr1_twim1_arbiter.c"
    )
    for marker in (
        "NRFX_TWIM_INSTANCE(1)", "openr1_twim1_acquire",
        "openr1_twim1_release", "openr1_twim1_tx", "openr1_twim1_rx",
        "OPENR1_TWIM1_CLIENT_MOTION", "OPENR1_TWIM1_CLIENT_NFC",
    ):
        require(twim1_arbiter, marker)
    require(PROJECT / "platform" / "nrf52840" / "sdk" / "main.c",
            "openr1_motion_initialize")
    require(PROJECT / "platform" / "nrf52840" / "sdk" / "openr1_sdk.ld",
            "KEEP(*(.openr1_motion_api))")
    require(PROJECT / "tests" / "test_openr1.c", "test_motion_provider_boundary")
    storage_port = (
        PROJECT / "platform" / "nrf52840" / "sdk" / "openr1_storage.c"
    )
    for marker in (
        "OPENR1_STORAGE_BYTES", "NRF_UICR->NRFFW[0]",
        "NRF_FICR->CODEPAGESIZE * NRF_FICR->CODESIZE",
        "storage_instance.end_addr = flash_end - 1u",
        "current != softdevice_event_thread", "nrf_fstorage_init",
        "nrf_fstorage_write", "nrf_fstorage_erase", "osWaitForever",
        "r1_fal_bind", "fal_init() != OPENR1_FAL_PARTITION_COUNT",
        ".openr1_storage_api",
    ):
        require(storage_port, marker)
    require(PROJECT / "platform" / "nrf52840" / "sdk" /
            "openr1_storage.h", "OPENR1_STORAGE_PAGE_COUNT UINT32_C(36)")
    require(PROJECT / "platform" / "nrf52840" / "sdk" / "main.c",
            "openr1_storage_initialize")
    require(PROJECT / "platform" / "nrf52840" / "sdk" / "openr1_sdk.ld",
            "KEEP(*(.openr1_storage_api))")
    require(DOCS / "INTERNAL-FLASH-CORRELATION.md", "0x000D4000..<0x000F8000")
    require(DOCS / "INTERNAL-FLASH-CORRELATION.md", "non-SoftDevice worker")
    require(DOCS / "SECURITY.md", "244-to-36-byte channel-1 overwrite")
    require(DOCS / "SOURCE-ADMISSION.md", "Goodix")
    require(DOCS / "MOTION-PROVIDER-CORRELATION.md", "BMA456 SensorAPI v2.29.0")
    require(DOCS / "MOTION-PROVIDER-CORRELATION.md", "LIS2DW12")
    require(DOCS / "ST25DVXXKC-CORRELATION.md", "ST25DVxxKC_ReadReg")
    require(DOCS / "ST25DVXXKC-CORRELATION.md", "20-byte")
    require(DOCS / "TINY-AES-CORRELATION.md", "tiny-AES-c v1.0.0")
    crypto = PROJECT / "src" / "r1_crypto.c"
    for marker in (
        "AES_init_ctx", "AES_ECB_decrypt", "R1_AES_BLOCK_BYTES",
        "ranges_overlap", "secure_clear", "chain = key",
        "key + R1_AES_BLOCK_BYTES", "chain_block",
    ):
        require(crypto, marker)

    manifest = json.loads((PROJECT / ".." / "third-party" / "fetched" / "manifest.json").read_text())
    components = {item["id"]: item for item in manifest["components"]}
    if components["nordic-nrf5-sdk"]["version"] != "17.1.0_ddde560":
        raise AssertionError("Nordic SDK pin changed")
    if components["nordic-s140"]["version"] != "7.2.0":
        raise AssertionError("S140 pin changed")
    freertos_kernel = components["freertos-kernel"]
    if freertos_kernel["version"] != "10.5.1" or \
            freertos_kernel["tag"] != "V10.5.1" or \
            freertos_kernel["commit"] != "def7d2df2b0506d3d249334974f51e427c17a41c" or \
            freertos_kernel["tree"] != "7496dfa815c3cea2f45a090c6e92d113f494b930" or \
            freertos_kernel["disposition"] != "authenticated_upstream_snapshot":
        raise AssertionError("FreeRTOS provider pin changed")
    freertos_port = components["nordic-freertos-nrf52-port"]
    if freertos_port["container"] != "nordic-nrf5-sdk" or \
            freertos_port["disposition"] != "pinned_upstream_bundled_port_only":
        raise AssertionError("Nordic FreeRTOS port pin changed")
    cmsis_wrapper = components["arm-cmsis-freertos"]
    if cmsis_wrapper["commit"] != "d213f261b5be6bb29a7cce8b84071706b72f4d53" or \
            cmsis_wrapper["source_sha256"] != \
            "8a0d60b56ad30c4f7957f64fa581158017b6812ec94b832d974c773ae4f2bc36":
        raise AssertionError("CMSIS-FreeRTOS provider pin changed")
    if components["flashdb"]["commit"] != \
            "4e5677408256f82d47cd56a6b04605dcee35ed9a" or \
            components["flashdb"]["version"] != "2.0.0":
        raise AssertionError("FlashDB pin changed")
    if components["fal"]["version"] != "0.5.99" or \
            components["fal"]["disposition"] != "pinned_upstream" or \
            components["fal"]["license"] != "Apache-2.0":
        raise AssertionError("FAL provider pin changed")
    cmbacktrace = components["cmbacktrace"]
    if cmbacktrace["commit"] != "73714489f9d8af130aacb515586b397b604a5768" or \
            cmbacktrace["compatible_floor_commit"] != \
            "4abadfa0c4f86f22352aa5ab9ebbb4f687125a1c" or \
            cmbacktrace["first_incompatible_commit"] != \
            "55e7b6990640c481e83ae8a3c0f3af2092b9f7a6" or \
            cmbacktrace["exact_vendor_checkout_proven"] is not False or \
            cmbacktrace["disposition"] != \
            "pinned_upstream_snapshot_adapter_required":
        raise AssertionError("CmBacktrace provider correlation gate changed")
    if components["goodix-gh3x2x"]["disposition"] != \
            "vendor_source_required_not_redistributable":
        raise AssertionError("Goodix vendor boundary missing")
    iqs = components["flipperone-iqs7211e"]
    if iqs["commit"] != "0a88e26bb8fd5b6afcdcc607fd748d7bc3d2b067" or \
            iqs["archive_sha256"] != \
            "4a957ea082ae2146692567ece71abd0b122a6c7c914bc964cee64d3d68656199" or \
            iqs["disposition"] != "pinned_upstream_reference_port_required":
        raise AssertionError("IQS7211E provider reference pin changed")
    azoteq_settings = components["azoteq-iqs7211e-settings"]
    if azoteq_settings["commit"] != \
            "436d3c42172abf812ec104521f29384fc02fc50e" or \
            azoteq_settings["source_sha256"] != \
            "266efea581cb5c55726e2e06402ca0c657e14c4a5e684fa4880160f81ca2c5ba" or \
            azoteq_settings["license"] != "MIT":
        raise AssertionError("Azoteq IQS7211E settings reference pin changed")
    tiny_aes = components["tiny-aes-c"]
    if tiny_aes["commit"] != "e72b6eff0884673997d0ca6385169bbd9b31936d" or \
            tiny_aes["archive_sha256"] != \
            "ed9099a1e25880eaaaba1da98ff2ff68b21498f0bf35b38ef0ebf7223448d265" or \
            tiny_aes["exact_vendor_checkout_proven"] is not False or \
            tiny_aes["disposition"] != \
            "pinned_upstream_compatible_adapter_required":
        raise AssertionError("tiny-AES-c provider correlation gate changed")
    bosch = components["bosch-bma456-sensorapi"]
    if bosch["commit"] != "3266db2c5de15be1a00232b8c0f2fd23e07934e0" or \
            bosch["archive_sha256"] != \
            "8c362c3bd107d0fdc480376788d18bccf908f46576530935cb25a58213491ffb" or \
            bosch["disposition"] != "pinned_upstream_adapter_required":
        raise AssertionError("Bosch BMA456 provider correlation gate changed")
    st = components["st-lis2dw12-pid"]
    if st["commit"] != "8d4bd522015004a9646102702901ba5a15ec6d39" or \
            st["compatible_floor_commit"] != \
            "18b0866fb6907dd5f4f52b79da36b3be88af719d" or \
            st["first_incompatible_commit"] != \
            "24580d635896d81ed2abad30c4309f8e1c65b152" or \
            st["exact_vendor_checkout_proven"] is not False or \
            st["disposition"] != "pinned_upstream_compatible_adapter_required":
        raise AssertionError("ST LIS2DW12 provider correlation gate changed")
    st25 = components["st-st25dvxxkc-bsp"]
    if st25["commit"] != "e9a35449b777699b5e1dd0f1466de0ead554893a" or \
            st25["archive_sha256"] != \
            "eecdc6795d5c949874d95739403aacaf6f0527c3fd476f7f78fda31e4d35faa6" or \
            st25["source_sha256"] != \
            "00469629a6b6cf76127a82dd0ab198855d8c794320df7f2d2f41509a289146e9" or \
            st25["register_source_sha256"] != \
            "dff34273b0656f8d45acb751cc576bf55add248d3f02b5c6e6dde0d679463106" or \
            st25["exact_vendor_checkout_proven"] is not False or \
            st25["disposition"] != \
            "pinned_upstream_compatible_adapter_required":
        raise AssertionError("ST25DVxxKC provider correlation gate changed")
    qma = components["qst-qma6100"]
    if qma["disposition"] != "official_source_required_before_implementation" or \
            qma["correlation_only"] is not True or \
            qma["correlation_commit"] != \
            "3903bd7d632c0aa6b101e623b1fd27c84184208e" or \
            qma["correlation_source_sha256"] != \
            "2307dc7532425af63087b59a6b56e3905c6a9689098d9c7792c94f46ebda0c95" or \
            qma["license"] is not None:
        raise AssertionError("QST official-source boundary missing")
    segger_rtt = components["segger-rtt"]
    if segger_rtt["version"] != "6.18a" or \
            segger_rtt["source_sha256"] != \
            "52f9a10baa6cea801134e7eb87848631fd03232540366c407c2a9183641c9088" or \
            segger_rtt["disposition"] != "pinned_upstream_bundled":
        raise AssertionError("SEGGER RTT provider pin changed")
    segger_fprintf = components["segger-fprintf"]
    if segger_fprintf["version"] != "SEGGER 6.14d formatter" or \
            segger_fprintf["format_source_sha256"] != \
            "d377680d31d9d2a31a360ed9693954fc3247acfa6848c9a2f01da2d97a064487" or \
            segger_fprintf["disposition"] != "pinned_upstream_bundled":
        raise AssertionError("SEGGER printf provider pin changed")

    subprocess.run([
        "python3", str(ROOT / "tools" / "build_r1_source_ownership.py"),
        "--check",
    ], check=True)
    subprocess.run([
        "python3", str(ROOT / "tools" / "evidence" /
                       "summarize_r1_wear_fusion_closure.py"),
    ], check=True, stdout=subprocess.DEVNULL)
    subprocess.run([
        "python3", str(ROOT / "tools" / "evidence" /
                       "summarize_r1_connection_parameter_policy.py"),
    ], check=True, stdout=subprocess.DEVNULL)
    subprocess.run([
        "python3", str(ROOT / "tools" / "evidence" /
                       "summarize_r1_sleep_sync_packet.py"),
    ], check=True, stdout=subprocess.DEVNULL)
    subprocess.run([
        "python3", str(ROOT / "tools" / "evidence" /
                       "summarize_r1_nfc_dock_policy.py"),
    ], check=True, stdout=subprocess.DEVNULL)
    subprocess.run([
        "python3", str(ROOT / "tools" / "evidence" /
                       "summarize_r1_peer_target_policy.py"),
    ], check=True, stdout=subprocess.DEVNULL)
    subprocess.run([
        "python3", str(ROOT / "tools" / "evidence" /
                       "summarize_r1_legacy_command_dispatch.py"),
    ], check=True, stdout=subprocess.DEVNULL)
    subprocess.run([
        "python3", str(ROOT / "tools" / "evidence" /
                       "summarize_r1_validated_sleep_delivery.py"),
    ], check=True, stdout=subprocess.DEVNULL)
    subprocess.run([
        "python3", str(ROOT / "tools" / "evidence" /
                       "summarize_r1_quantized_pooling_boundary.py"),
    ], check=True, stdout=subprocess.DEVNULL)
    subprocess.run([
        "python3", str(ROOT / "tools" / "evidence" /
                       "summarize_r1_connection_role_assignment.py"),
    ], check=True, stdout=subprocess.DEVNULL)
    subprocess.run([
        "python3", str(ROOT / "tools" / "evidence" /
                       "summarize_r1_eus_rx_reassembly.py"),
    ], check=True, stdout=subprocess.DEVNULL)
    subprocess.run([
        "python3", str(ROOT / "tools" / "evidence" /
                       "summarize_r1_bae8_event_router.py"),
    ], check=True, stdout=subprocess.DEVNULL)
    subprocess.run([
        "python3", str(ROOT / "tools" / "evidence" /
                       "summarize_r1_frontier_35x.py"),
    ], check=True, stdout=subprocess.DEVNULL)
    subprocess.run([
        "python3", str(ROOT / "tools" / "evidence" /
                       "summarize_r1_frontier_334_342.py"),
    ], check=True, stdout=subprocess.DEVNULL)
    subprocess.run([
        "python3", str(ROOT / "tools" / "evidence" /
                       "summarize_r1_frontier_314_328.py"),
    ], check=True, stdout=subprocess.DEVNULL)
    subprocess.run([
        "python3", str(ROOT / "tools" / "evidence" /
                       "summarize_r1_frontier_280_308.py"),
    ], check=True, stdout=subprocess.DEVNULL)
    subprocess.run([
        "python3", str(ROOT / "tools" / "evidence" /
                       "summarize_r1_frontier_264_274.py"),
    ], check=True, stdout=subprocess.DEVNULL)
    subprocess.run([
        "python3", str(ROOT / "tools" / "evidence" /
                       "summarize_r1_frontier_256_262.py"),
    ], check=True, stdout=subprocess.DEVNULL)
    subprocess.run([
        "python3", str(ROOT / "tools" / "evidence" /
                       "summarize_r1_frontier_230_248.py"),
    ], check=True, stdout=subprocess.DEVNULL)
    subprocess.run([
        "python3", str(ROOT / "tools" / "evidence" /
                       "summarize_r1_frontier_224_230.py"),
    ], check=True, stdout=subprocess.DEVNULL)
    subprocess.run([
        "python3", str(ROOT / "tools" / "evidence" /
                       "summarize_r1_frontier_204_210.py"),
    ], check=True, stdout=subprocess.DEVNULL)
    subprocess.run([
        "python3", str(ROOT / "tools" / "evidence" /
                       "summarize_r1_frontier_128_202.py"),
    ], check=True, stdout=subprocess.DEVNULL)
    subprocess.run([
        "python3", str(ROOT / "tools" / "evidence" /
                       "summarize_r1_frontier_64_127.py"),
    ], check=True, stdout=subprocess.DEVNULL)
    subprocess.run([
        "python3", str(ROOT / "tools" / "evidence" /
                       "summarize_r1_frontier_32_63.py"),
    ], check=True, stdout=subprocess.DEVNULL)
    subprocess.run([
        "python3", str(ROOT / "tools" / "evidence" /
                       "summarize_r1_frontier_sub32.py"),
    ], check=True, stdout=subprocess.DEVNULL)
    subprocess.run([
        "python3", str(ROOT / "tools" / "evidence" /
                       "summarize_r1_frontier_final53.py"),
    ], check=True, stdout=subprocess.DEVNULL)
    subprocess.run([
        "python3", str(ROOT / "tools" / "evidence" /
                       "summarize_r1_pmic_charge_event.py"),
    ], check=True, stdout=subprocess.DEVNULL)
    subprocess.run([
        "python3", str(ROOT / "tools" / "evidence" /
                       "summarize_r1_pmic_charged_notification.py"),
    ], check=True, stdout=subprocess.DEVNULL)
    subprocess.run([
        "python3", str(ROOT / "tools" / "evidence" /
                       "summarize_r1_iqs7211e_ati_audit.py"),
    ], check=True, stdout=subprocess.DEVNULL)
    subprocess.run([
        "python3", str(ROOT / "tools" / "evidence" /
                       "summarize_r1_hrv_ram_cache_merge.py"),
    ], check=True, stdout=subprocess.DEVNULL)
    subprocess.run([
        "python3", str(ROOT / "tools" / "evidence" /
                       "summarize_r1_scalar_health_ram_cache_merge.py"),
    ], check=True, stdout=subprocess.DEVNULL)
    subprocess.run([
        "python3", str(ROOT / "tools" / "evidence" /
                       "summarize_r1_protocol_response.py"),
    ], check=True, stdout=subprocess.DEVNULL)
    subprocess.run([
        "python3", str(ROOT / "tools" / "evidence" /
                       "summarize_r1_export_state_machine.py"),
    ], check=True, stdout=subprocess.DEVNULL)
    subprocess.run([
        "python3", str(ROOT / "tools" / "evidence" /
                       "summarize_r1_delayed_event_timer.py"),
    ], check=True, stdout=subprocess.DEVNULL)
    with (DOCS / "FUNCTION-OWNERSHIP.csv").open(newline="") as handle:
        ownership_rows = list(csv.DictReader(handle))
    expected_function_keys = set()
    inventory_paths = {
        "application": ROOT / "research" / "decompilation" / "application" / "functions.csv",
        "bootloader": ROOT / "research" / "bootloader-reconstruction" / "generated" / "functions.csv",
    }
    for image, inventory_path in inventory_paths.items():
        with inventory_path.open(newline="") as handle:
            expected_function_keys.update(
                (image, row["entry"].lower()) for row in csv.DictReader(handle)
            )
    ownership_keys = {(row["image"], row["entry"]) for row in ownership_rows}
    ghidra_keys = {
        (row["image"], row["entry"]) for row in ownership_rows
        if row["inventory_source"] == "ghidra_functions_csv"
    }
    supplemental_keys = {
        (row["image"], row["entry"]) for row in ownership_rows
        if row["inventory_source"] == "manual_provenance_supplement"
    }
    if ghidra_keys != expected_function_keys or len(ownership_rows) != len(ownership_keys):
        raise AssertionError("function ownership ledger is not a one-to-one Ghidra inventory")
    if not supplemental_keys or supplemental_keys & expected_function_keys:
        raise AssertionError("manual function supplements are missing or overlap Ghidra inventory")
    if any(not row["source_disposition"] for row in ownership_rows):
        raise AssertionError("function ownership row missing source disposition")
    if any(row["provider_family"] == "unclassified" and
           row["source_disposition"] != "investigate_before_implementing"
           for row in ownership_rows):
        raise AssertionError("unclassified function bypasses source-admission gate")
    ownership_by_key = {(row["image"], row["entry"]): row for row in ownership_rows}
    boot_provider_counts = Counter(
        row["provider_family"] for row in ownership_rows if row["image"] == "bootloader"
    )
    expected_boot_provider_counts = {
        "arm_cryptocell_cc310": 41,
        "arm_toolchain_runtime": 12,
        "nanopb": 30,
        "nordic_nrf5_sdk_17_1_0": 218,
        "r1_product_specific": 3,
    }
    if boot_provider_counts != expected_boot_provider_counts:
        raise AssertionError(
            f"bootloader provider closure changed: {boot_provider_counts}"
        )

    application_provider_counts = Counter(
        row["provider_family"] for row in ownership_rows if row["image"] == "application"
    )
    if application_provider_counts["unclassified"] != 0:
        raise AssertionError("application unclassified-function count changed")
    if application_provider_counts["nordic_nrf5_sdk_17_1_0"] != 547:
        raise AssertionError("application Nordic provider count changed")
    if application_provider_counts["r1_product_specific"] != 671:
        raise AssertionError("R1 product-function count changed")
    if application_provider_counts["unknown_generic_device_registry_candidate"] != 40:
        raise AssertionError("unknown generic device-registry boundary count changed")
    if application_provider_counts["unknown_time_calendar_provider_candidate"] != 16:
        raise AssertionError("unknown time/calendar provider boundary count changed")
    if application_provider_counts["unknown_software_twi_provider_candidate"] != 40:
        raise AssertionError("unknown software-TWI provider boundary count changed")
    if application_provider_counts["unknown_rtc_device_provider_candidate"] != 10:
        raise AssertionError("unknown RTC-device provider boundary count changed")
    if application_provider_counts[
            "unknown_sensor_algorithm_heap_provider_candidate"] != 0:
        raise AssertionError("unknown sensor-algorithm heap boundary count changed")
    if application_provider_counts[
            "unknown_sensor_stream_framework_candidate"] != 32:
        raise AssertionError("unknown sensor-stream framework boundary count changed")
    if application_provider_counts[
            "unknown_shared_quantized_neural_runtime_candidate"] != 26:
        raise AssertionError("unknown quantized-neural runtime boundary count changed")
    if application_provider_counts["gomore_health_algorithm_candidate"] != 362:
        raise AssertionError("GoMore provider-boundary count changed")
    if application_provider_counts["r1_gomore_provider_adapter"] != 3:
        raise AssertionError("R1 GoMore adapter count changed")
    if application_provider_counts["r1_health_storage_provider_adapter"] != 3:
        raise AssertionError("R1 health-storage adapter count changed")
    if application_provider_counts["r1_nordic_cmsis_provider_adapter"] != 12:
        raise AssertionError("R1 Nordic/CMSIS synchronization adapter count changed")
    if application_provider_counts["r1_device_registry_configuration_adapter"] != 9:
        raise AssertionError("R1 device-registry configuration adapter count changed")
    if application_provider_counts["yhmicros_yhm2710_candidate"] != 36:
        raise AssertionError("YHM2710 provider-boundary count changed")
    if application_provider_counts["r1_nordic_wdt_provider_adapter"] != 2:
        raise AssertionError("R1 Nordic-WDT adapter count changed")
    if application_provider_counts["r1_provider_configuration_glue"] != 10:
        raise AssertionError("R1 provider-configuration glue count changed")
    if application_provider_counts["goodix_gh3x2x_candidate"] != 325:
        raise AssertionError("Goodix GH3X2X provider-boundary count changed")
    if application_provider_counts["goodix_gh3x2x_democode_v1_6_drvlib_v4_3_0_0"] != 168:
        raise AssertionError("Goodix GH3X2X public-democode attribution count changed")
    if application_provider_counts["r1_goodix_provider_adapter"] != 24:
        raise AssertionError("R1 Goodix adapter count changed")
    if application_provider_counts["r1_iqs7211e_provider_adapter"] != 12:
        raise AssertionError("R1 IQS7211E adapter count changed")
    if application_provider_counts["stmicro_st25dvxxkc_bsd_compatible"] != 27:
        raise AssertionError("ST25DVxxKC provider-boundary count changed")
    if application_provider_counts["r1_st25dvxxkc_provider_adapter"] != 11:
        raise AssertionError("R1 ST25DVxxKC adapter count changed")
    if application_provider_counts["r1_i2c5_resource_adapter"] != 5:
        raise AssertionError("R1 i2c_5 resource-adapter count changed")
    if application_provider_counts["r1_motion_provider_adapter"] != 23:
        raise AssertionError("R1 common motion-adapter count changed")
    if application_provider_counts["r1_qst_qma6100_provider_adapter"] != 14:
        raise AssertionError("R1 QMA6100 adapter count changed")
    if application_provider_counts["r1_internal_flash_provider_adapter"] != 11:
        raise AssertionError("R1 internal-flash adapter count changed")
    if application_provider_counts["r1_analog_provider_adapter"] != 4:
        raise AssertionError("R1 analog adapter count changed")
    gomore_rows = [
        row for row in ownership_rows
        if row["image"] == "application" and
        row["provider_family"] == "gomore_health_algorithm_candidate"
    ]
    if any(
        row["source_disposition"] != "vendor_source_required_not_redistributable"
        for row in gomore_rows
    ):
        raise AssertionError("GoMore function bypasses the licensed-provider gate")
    gomore_entry_digest = hashlib.sha256("".join(
        f"{row['entry']}\n" for row in gomore_rows
    ).encode()).hexdigest()
    if gomore_entry_digest != \
            "420cb2b1df95d4b956b4f4c155a6877e9fdb125d987b36cfb8140c06107ef359":
        raise AssertionError("GoMore exact function-entry set changed")
    goodix_rows = [
        row for row in ownership_rows
        if row["image"] == "application" and
        row["provider_family"] == "goodix_gh3x2x_candidate"
    ]
    goodix_entry_digest = hashlib.sha256("".join(
        f"{row['entry']}\n" for row in goodix_rows
    ).encode()).hexdigest()
    if goodix_entry_digest != \
            "9fd3924c5175ad59654f696df9d7a2ec893832d8ba4059ca4deebdc2af6c0c11":
        raise AssertionError("Goodix exact function-entry set changed")
    goodix_democode_rows = [
        row for row in ownership_rows
        if row["image"] == "application" and
        row["provider_family"] == "goodix_gh3x2x_democode_v1_6_drvlib_v4_3_0_0"
    ]
    if any(
        row["source_disposition"] != "use_pinned_upstream"
        for row in goodix_democode_rows
    ):
        raise AssertionError("Goodix public-democode function lost its upstream pin")
    goodix_democode_entry_digest = hashlib.sha256("".join(
        f"{row['entry']}\n" for row in goodix_democode_rows
    ).encode()).hexdigest()
    if goodix_democode_entry_digest != \
            "8a7786a5e7ca0c128c5b5d2e53b00c61e34232a54837bebdf4d9e2e3a5328e70":
        raise AssertionError("Goodix public-democode exact function-entry set changed")
    goodix_adapter_rows = [
        row for row in ownership_rows
        if row["image"] == "application" and
        row["provider_family"] == "r1_goodix_provider_adapter"
    ]
    goodix_adapter_entry_digest = hashlib.sha256("".join(
        f"{row['entry']}\n" for row in goodix_adapter_rows
    ).encode()).hexdigest()
    if goodix_adapter_entry_digest != \
            "f75970812258a0fd17f204d80c682442669cb066aa46b15188112f2a55c36d7c":
        raise AssertionError("R1 Goodix exact adapter-entry set changed")
    wear_entries = {
        "0x0003cd80", "0x0003ce44", "0x0003ceec", "0x0003d06c",
        "0x0003d0c0", "0x0003d268", "0x0003d45c",
    }
    wear_rows = [
        ownership_by_key[("application", entry)] for entry in wear_entries
    ]
    if any(row["provider_family"] != "r1_product_specific" or
           row["source_disposition"] != "clean_room_behavior_only"
           for row in wear_rows):
        raise AssertionError("R1 wear-fusion ownership gate changed")
    wear_entry_digest = hashlib.sha256("".join(
        f"{entry}\n" for entry in sorted(wear_entries)
    ).encode()).hexdigest()
    if wear_entry_digest != \
            "6242a1ca265b4447dce86b3ef9d4779684668782827dbf92214b2f4f1d5c1a97":
        raise AssertionError("R1 wear-fusion exact entry set changed")
    connection_parameter_entries = {
        "0x0004cb34", "0x0004cba4", "0x00051aa0", "0x00072b80",
    }
    connection_parameter_rows = [
        ownership_by_key[("application", entry)]
        for entry in connection_parameter_entries
    ]
    if any(row["provider_family"] != "r1_product_specific" or
           row["source_disposition"] != "clean_room_behavior_only"
           for row in connection_parameter_rows):
        raise AssertionError("R1 connection-parameter ownership gate changed")
    connection_parameter_digest = hashlib.sha256("".join(
        f"{entry}\n" for entry in sorted(connection_parameter_entries)
    ).encode()).hexdigest()
    if connection_parameter_digest != \
            "410d423ac199ae2d7d17a8d6e7400fbafa2112acf6587844d55fff8706808c21":
        raise AssertionError("R1 connection-parameter exact entry set changed")
    sleep_sync_packet_row = ownership_by_key[("application", "0x0008da24")]
    if sleep_sync_packet_row["provider_family"] != "r1_product_specific" or \
            sleep_sync_packet_row["source_disposition"] != "clean_room_behavior_only":
        raise AssertionError("R1 sleep-sync packet ownership gate changed")
    peer_target_entries = {
        "0x0003d724", "0x0004cae4", "0x0004cccc",
    }
    peer_target_rows = [
        ownership_by_key[("application", entry)] for entry in peer_target_entries
    ]
    if any(row["provider_family"] != "r1_product_specific" or
           row["source_disposition"] != "clean_room_behavior_only"
           for row in peer_target_rows):
        raise AssertionError("R1 peer-target ownership gate changed")
    peer_target_digest = hashlib.sha256("".join(
        f"{entry}\n" for entry in sorted(peer_target_entries)
    ).encode()).hexdigest()
    if peer_target_digest != \
            "0208a636a3f582c9427e4c28c582864e849b6013969ebb63022377ae7c4f231b":
        raise AssertionError("R1 peer-target exact entry set changed")
    legacy_command_dispatch_entries = {"0x0004e258"}
    legacy_command_dispatch_rows = [
        ownership_by_key[("application", entry)]
        for entry in legacy_command_dispatch_entries
    ]
    if any(row["provider_family"] != "r1_product_specific" or
           row["source_disposition"] != "clean_room_behavior_only"
           for row in legacy_command_dispatch_rows):
        raise AssertionError("R1 legacy command-dispatch ownership gate changed")
    legacy_command_dispatch_digest = hashlib.sha256("".join(
        f"{entry}\n" for entry in sorted(legacy_command_dispatch_entries)
    ).encode()).hexdigest()
    if legacy_command_dispatch_digest != \
            "ac05f2d2ff7202f8fa2744b8c2d9eedc8ce07fd9d95351982a1b73771126760e":
        raise AssertionError("R1 legacy command-dispatch entry set changed")
    validated_sleep_delivery_entries = {
        "0x0005b890", "0x0008dc94", "0x0008dd90",
    }
    validated_sleep_delivery_rows = [
        ownership_by_key[("application", entry)]
        for entry in validated_sleep_delivery_entries
    ]
    if any(row["provider_family"] != "r1_product_specific" or
           row["source_disposition"] != "clean_room_behavior_only"
           for row in validated_sleep_delivery_rows):
        raise AssertionError("R1 validated-sleep delivery ownership gate changed")
    validated_sleep_delivery_digest = hashlib.sha256("".join(
        f"{entry}\n" for entry in sorted(validated_sleep_delivery_entries)
    ).encode()).hexdigest()
    if validated_sleep_delivery_digest != \
            "0d51e3f7c5b04d81370e82b8bfd2f868dae6aa3ab9b4c0766098892da55267ec":
        raise AssertionError("R1 validated-sleep delivery entry set changed")
    quantized_pooling_entries = {"0x00041816"}
    quantized_pooling_rows = [
        ownership_by_key[("application", entry)] for entry in quantized_pooling_entries
    ]
    if any(row["provider_family"] !=
           "unknown_shared_quantized_neural_runtime_candidate" or
           row["source_disposition"] != "investigate_before_implementing"
           for row in quantized_pooling_rows):
        raise AssertionError("shared quantized-pooling provider gate changed")
    quantized_pooling_digest = hashlib.sha256("".join(
        f"{entry}\n" for entry in sorted(quantized_pooling_entries)
    ).encode()).hexdigest()
    if quantized_pooling_digest != \
            "4048e9d367dbf18d68c879f132242a87b29ecc5938fe0f2799138e39e0a62588":
        raise AssertionError("shared quantized-pooling entry set changed")
    motion_adapter_rows = [
        row for row in ownership_rows
        if row["image"] == "application" and
        row["provider_family"] == "r1_motion_provider_adapter"
    ]
    motion_adapter_entry_digest = hashlib.sha256("".join(
        f"{row['entry']}\n" for row in motion_adapter_rows
    ).encode()).hexdigest()
    if motion_adapter_entry_digest != \
            "574928e2d2a3c2a4be1022a1ce7ab8ade28307bffd30698baf7d4f09a2606060":
        raise AssertionError("R1 common motion exact adapter-entry set changed")
    qma_adapter_rows = [
        row for row in ownership_rows
        if row["image"] == "application" and
        row["provider_family"] == "r1_qst_qma6100_provider_adapter"
    ]
    qma_adapter_entry_digest = hashlib.sha256("".join(
        f"{row['entry']}\n" for row in qma_adapter_rows
    ).encode()).hexdigest()
    if qma_adapter_entry_digest != \
            "d14aaa0d2eaf0b800d4ec66fe672f500baab09b5f166c9c3d8d639b97cb23d81":
        raise AssertionError("R1 QMA6100 exact adapter-entry set changed")
    internal_flash_rows = [
        row for row in ownership_rows
        if row["image"] == "application" and
        row["provider_family"] == "r1_internal_flash_provider_adapter"
    ]
    internal_flash_entry_digest = hashlib.sha256("".join(
        f"{row['entry']}\n" for row in internal_flash_rows
    ).encode()).hexdigest()
    if internal_flash_entry_digest != \
            "954a44bacf3a012343ae425ab35f7763e9b1ad1630324336d44c2f6f628eb082":
        raise AssertionError("R1 internal-flash exact adapter-entry set changed")
    analog_rows = [
        row for row in ownership_rows
        if row["image"] == "application" and
        row["provider_family"] == "r1_analog_provider_adapter"
    ]
    analog_entry_digest = hashlib.sha256("".join(
        f"{row['entry']}\n" for row in analog_rows
    ).encode()).hexdigest()
    if analog_entry_digest != \
            "ab6f7f1bf56bfced376fd6a4ab37c35c6b36c60404f9991b92a3b4b42611ad83":
        raise AssertionError("R1 analog exact adapter-entry set changed")
    iqs7211e_adapter_rows = [
        row for row in ownership_rows
        if row["image"] == "application" and
        row["provider_family"] == "r1_iqs7211e_provider_adapter"
    ]
    iqs7211e_adapter_entry_digest = hashlib.sha256("".join(
        f"{row['entry']}\n" for row in iqs7211e_adapter_rows
    ).encode()).hexdigest()
    if iqs7211e_adapter_entry_digest != \
            "81b2e89b28cbd6ca0b88a3db4f60c7f2ec01ee75beb2125495c1e0f5d1ffd266":
        raise AssertionError("R1 IQS7211E exact adapter-entry set changed")
    st25_rows = [
        row for row in ownership_rows
        if row["image"] == "application" and
        row["provider_family"] == "stmicro_st25dvxxkc_bsd_compatible"
    ]
    st25_entry_digest = hashlib.sha256("".join(
        f"{row['entry']}\n" for row in st25_rows
    ).encode()).hexdigest()
    if st25_entry_digest != \
            "9e0c33cc69749d60cd5095d0b75dbf4a05ea28856122be6271e0f5a57be83898":
        raise AssertionError("ST25DVxxKC exact function-entry set changed")
    st25_adapter_rows = [
        row for row in ownership_rows
        if row["image"] == "application" and
        row["provider_family"] == "r1_st25dvxxkc_provider_adapter"
    ]
    st25_adapter_entry_digest = hashlib.sha256("".join(
        f"{row['entry']}\n" for row in st25_adapter_rows
    ).encode()).hexdigest()
    if st25_adapter_entry_digest != \
            "bc429e369fe2677c6c0b0bf0a730ccb5f8fd1d77f1ec0b920e93f6d7c3d11098":
        raise AssertionError("R1 ST25DVxxKC exact adapter-entry set changed")

    application_correlation = (
        ROOT / "research" / "source-correlation" / "application-source-correlation" /
        "source-correlations-raw.csv"
    )
    if hashlib.sha256(application_correlation.read_bytes()).hexdigest() != \
            "6dea8106e8965d038976cd2e380af41f9121ed625d5bdb2bc62a36841612c535":
        raise AssertionError("application source-correlation corpus changed")
    with application_correlation.open(newline="") as handle:
        application_correlation_rows = list(csv.DictReader(handle))
    correlation_counts = Counter(
        row["r1_entry"] for row in application_correlation_rows
    )
    if len(application_correlation_rows) != 31776 or \
            len(correlation_counts) != 2648 or \
            set(correlation_counts.values()) != {12}:
        raise AssertionError("application source-correlation dimensions changed")

    st25_correlation = (
        ROOT / "research" / "source-correlation" / "st25dvxxkc-source-correlation" /
        "source-correlations-raw.csv"
    )
    if hashlib.sha256(st25_correlation.read_bytes()).hexdigest() != \
            "fd1692b73c5abdc2f8cadf2885ea77f48023097ec9d13dcee2bced7c5ea6cbe7":
        raise AssertionError("ST25DVxxKC source-correlation corpus changed")
    with st25_correlation.open(newline="") as handle:
        st25_correlation_rows = list(csv.DictReader(handle))
    st25_correlation_counts = Counter(
        row["r1_entry"] for row in st25_correlation_rows
    )
    if len(st25_correlation_rows) != 31776 or \
            len(st25_correlation_counts) != 2648 or \
            set(st25_correlation_counts.values()) != {12}:
        raise AssertionError("ST25DVxxKC source-correlation dimensions changed")
    exact_st25_bsim = {
        ("0x00031d78", "ST25DVxxKC_ReadReg"),
        ("0x00031f2c", "ST25DVxxKC_WriteReg"),
    }
    observed_exact_st25_bsim = {
        (row["r1_entry"], row["reference_name"])
        for row in st25_correlation_rows
        if row["rank"] == "1" and row["similarity"] == "1.000000000"
    }
    if not exact_st25_bsim <= observed_exact_st25_bsim:
        raise AssertionError("ST25DVxxKC exact BSim anchors changed")

    recovered = recovered_application_bytes()
    recovered_base = 0x00027000
    if len(recovered) != 646408:
        raise AssertionError("recovered application evidence length changed")
    gomore_supplement_expected = {
        0x00067488: (
            196, "gomore_health_algorithm_candidate",
            "vendor_source_required_not_redistributable", "",
            "b351faf207bd93a95557dd695eb7e034dfb92bb02be730ae6e118d8372602991",
        ),
        0x0006825C: (
            232, "gomore_health_algorithm_candidate",
            "vendor_source_required_not_redistributable", "",
            "346de4b3b4a920d11fd3aaf7dd930854b7ce8eb02fc26568f9016c9febe1cf84",
        ),
        0x0006B114: (
            164, "r1_gomore_provider_adapter",
            "clean_room_adapter_only_use_licensed_provider",
            "r1_gomore_acc_topic_adapter",
            "12d48128ccaab3563434e1020cafeae53af5c37848aa5e7df228776cfd3139e4",
        ),
        0x0006B228: (
            74, "r1_gomore_provider_adapter",
            "clean_room_adapter_only_use_licensed_provider",
            "r1_gomore_raw_hr_topic_adapter",
            "ab337651b4344af149b261e8c0e733690a02df92bffcb5b79ee4370e7b8b3134",
        ),
        0x0007D09C: (
            12, "gomore_health_algorithm_candidate",
            "vendor_source_required_not_redistributable", "",
            "90e8db1c4218cea4a6d0b8bfb3599ff589e62348c9b0160696c2decc158a8687",
        ),
        0x0008F49C: (
            24, "gomore_health_algorithm_candidate",
            "vendor_source_required_not_redistributable", "",
            "4a6d354d9870c5323d26f51a42612488eccd79558d670938dae0574926e17aa2",
        ),
    }
    for entry, (size, provider, disposition, symbol, digest) in \
            gomore_supplement_expected.items():
        row = ownership_by_key[("application", f"0x{entry:08x}")]
        start = entry - recovered_base
        body = recovered[start:start + size]
        if row["inventory_source"] != "manual_provenance_supplement" or \
                row["provider_family"] != provider or \
                row["source_disposition"] != disposition or \
                row["upstream_symbol"] != symbol or \
                row["size"] != str(size) or len(body) != size or \
                hashlib.sha256(body).hexdigest() != digest:
            raise AssertionError(
                f"GoMore audit supplement changed: 0x{entry:08x}"
            )

    bootloader = (ROOT / "research" / "decompilation" / "rebuild" /
                  "rebuilt-bootloader.bin").read_bytes()
    bootloader_base = 0x000F8000
    nanopb_promotions = {
        0x000FAD98: (
            "iter_from_extension", 46,
            "e240ed1adbdaeeaab9eb976ddfc11ac4b602e9bafe355392673e0ce5bd9fb032",
        ),
        0x000FC718: (
            "pb_dec_bytes", 66,
            "f9f58e1bdc6b89363210c58b89782f406c41d661e10c053708e19d0df224cd6e",
        ),
        0x000FC75A: (
            "pb_dec_fixed32", 6,
            "fb5d99e87950b6d01583e88f6da8f888496603b364550d82cc61c7a64cc01aa1",
        ),
        0x000FC760: (
            "pb_dec_fixed64", 6,
            "0617c29c70c231a1892f42ada8d30e40166cdd7051687c261e8fbd1d36879c7b",
        ),
        0x000FC766: (
            "pb_dec_string", 62,
            "71720366d9d25965459ff3b499bdbaca0bcc53880b962617c0ed0217bc5b897f",
        ),
        0x000FC8EC: (
            "pb_decode", 30,
            "9c8b2187530aa73659a40e2714e810f0ea1073785412a1f1d95042755e2ec45e",
        ),
        0x000FCE26: (
            "pb_message_set_to_defaults", 38,
            "fa371cfc257df9fcab9ad06b9e492ca546dbb50fc3652bdaa30f26abdb58a54e",
        ),
        0x000FCEA4: (
            "pb_readbyte", 32,
            "0d8fc491275587a480576ee1500dd95d32c57b87e5c558687cb778674f046686",
        ),
        0x000FCEC4: (
            "pb_skip_field", 90,
            "3a2052c759056e350581061bc8dbc5b73ff3a4e321aa9aad16612da6215fb486",
        ),
        0x000FD1E0: (
            "read_raw_value", 98,
            "0e9d44f2db0d7a0065fd69ec68ed8e6dcdab5e1ed61a10eefd412781694ab7a4",
        ),
    }
    for entry, (symbol, size, digest) in nanopb_promotions.items():
        row = ownership_by_key[("bootloader", f"0x{entry:08x}")]
        body = bootloader[entry - bootloader_base:entry - bootloader_base + size]
        if row["provider_family"] != "nanopb" or \
                row["source_disposition"] != "use_nordic_sdk_bundled_upstream" or \
                row["upstream_symbol"] != symbol or int(row["size"]) != size or \
                hashlib.sha256(body).hexdigest() != digest:
            raise AssertionError(f"nanopb promotion mismatch: 0x{entry:08x}")

    fstorage_api_promotions = {
        0x000FA99C: (
            "nrf_fstorage_nvmc_erase", 68,
            "e1fb6c5226667f82211a717a0221c1abfeb3b61c1537cb942c744664455c92c4",
        ),
        0x000FA9E4: (
            "nrf_fstorage_sd_erase", 72,
            "37497a0f30c9da5b4c2287c6294739f38c24e47d8d9a675699172ec7648bbde0",
        ),
        0x000FACD4: (
            "nrf_fstorage_nvmc_init", 8,
            "a344fd2ed6c8849b5075a787ab0ea4c4d393057b71534bb2f569b68d9b18bd74",
        ),
        0x000FACE0: (
            "nrf_fstorage_sd_init", 46,
            "28ff49295eb6ac6c5eccf82069fab52cee8d9e25a0d27d42e7afa7175946e757",
        ),
        0x000FAD18: (
            "nrf_fstorage_nvmc_is_busy", 12,
            "9409ea849640d70f4fa8db6c4696be986ee7995994fbe949d53d000e96c5e614",
        ),
        0x000FAD28: (
            "nrf_fstorage_sd_is_busy", 12,
            "5a6ca41d629f68b89ef994ddc19c96f991b80cdda4070c7a613e35532b9a9183",
        ),
        0x000FD1C4: (
            "nrf_fstorage_nvmc_read", 14,
            "c579a44c71c08de8c8d19bf0ced574ce28f36500f15b59f37f9ae16ad21471ca",
        ),
        0x000FD1D2: (
            "nrf_fstorage_sd_read", 14,
            "8b29da2417f84cb0536ce5fae6af5639f8dd853aec12468139ecb5fbee07bb6a",
        ),
        0x000FD298: (
            "nrf_fstorage_nvmc_rmap", 4,
            "551d2f51b714798f636aae0619271e7bdf2fd8bfdc6fabfd44404111ae5b82cf",
        ),
        0x000FD29C: (
            "nrf_fstorage_sd_rmap", 4,
            "551d2f51b714798f636aae0619271e7bdf2fd8bfdc6fabfd44404111ae5b82cf",
        ),
        0x000FD6E4: (
            "nrf_fstorage_nvmc_uninit", 12,
            "5e62870a724b207e7bcdaae70321add92ec23509168c214fd69641f04e28f9b7",
        ),
        0x000FD6F4: (
            "nrf_fstorage_sd_uninit", 22,
            "88cb069d401c3036ab94bbdb48c11e6c55ba8fa3d9936eabcf304cfb58cd9da6",
        ),
        0x000FD7CC: (
            "nrf_fstorage_nvmc_wmap", 4,
            "a7ddd513d149ea16fdd4db3f82267f83087aeaddd06b5dde5468adb704205fc4",
        ),
        0x000FD7D0: (
            "nrf_fstorage_sd_wmap", 4,
            "a7ddd513d149ea16fdd4db3f82267f83087aeaddd06b5dde5468adb704205fc4",
        ),
        0x000FD7D4: (
            "nrf_fstorage_nvmc_write", 64,
            "7e888f3123aa5161e476e1588e481dfb45bb9e0f39a8ed699de18ac9cca8da80",
        ),
        0x000FD818: (
            "nrf_fstorage_sd_write", 74,
            "c46fc9be40da04f839b43542fd130f18df8ff602454bdc24bd478e81129000bb",
        ),
    }
    for entry, (symbol, size, digest) in fstorage_api_promotions.items():
        row = ownership_by_key[("bootloader", f"0x{entry:08x}")]
        body = bootloader[entry - bootloader_base:entry - bootloader_base + size]
        if row["provider_family"] != "nordic_nrf5_sdk_17_1_0" or \
                row["source_disposition"] != "use_nordic_sdk" or \
                row["upstream_symbol"] != symbol or int(row["size"]) != size or \
                hashlib.sha256(body).hexdigest() != digest:
            raise AssertionError(f"fstorage API promotion mismatch: 0x{entry:08x}")

    toolchain_boot_promotions = {
        0x000F8208: (
            "armcc_runtime_entry_veneer", 4,
            "6b6b0f7315d31682c7f8059490eb3df143139881118c2c78a5b82ce1834d895d",
        ),
        0x000F84C8: (
            "armcc_scatterload", 30,
            "712bb4b9f2860f163b6b00a5389ff467a4e31d4897ed4b65e087828c806408db",
        ),
        0x000F9C44: (
            "armcc_scatterload_copy", 2,
            "570c0f7fa07ebb3c7ad727d0a0f5b7ffacd31fc86459c7cf35cad2c463cd56f8",
        ),
        0x000F9C4C: (
            "armcc_scatterload_copy_loop", 12,
            "be51fc010e6aa7ef0bc84bc35df6df82bbd6febb77d239855ace4e37fd0d2f4f",
        ),
    }
    for entry, (symbol, size, digest) in toolchain_boot_promotions.items():
        row = ownership_by_key[("bootloader", f"0x{entry:08x}")]
        if entry == 0x000F9C4C:
            body = bootloader[0x000F9C46 - bootloader_base:0x000F9C52 - bootloader_base]
        else:
            body = bootloader[entry - bootloader_base:entry - bootloader_base + size]
        if row["provider_family"] != "arm_toolchain_runtime" or \
                row["source_disposition"] != "use_toolchain_runtime" or \
                row["upstream_symbol"] != symbol or int(row["size"]) != size or \
                hashlib.sha256(body).hexdigest() != digest:
            raise AssertionError(f"toolchain bootloader promotion mismatch: 0x{entry:08x}")

    nordic_boot_promotions = {
        0x000F8218: (
            "nrf_atfifo_wspace_req", 56,
            "0570cadf2a25e32dd485590406673a43123490221fe70a0e390ef604b32e9520",
        ),
        0x000F8250: (
            "nrf_atfifo_wspace_close", 18,
            "6b65bd1569079ca479605bdca6fcc17ec07f611d3c456339f9a1bd4064bf7c52",
        ),
        0x000F8262: (
            "nrf_atfifo_rspace_req", 58,
            "efcce02d400b548797a5bdcc1a9ccba1f97c2457e1dbee9ca3df3bd8e8372133",
        ),
        0x000F829C: (
            "nrf_atfifo_rspace_close", 18,
            "92d0a6e674923229ae25b9b9aa5752884cc03f885d42587a7dfbcc71cb6b2bd2",
        ),
        0x000F82AE: (
            "nrf_atfifo_space_clear", 50,
            "4b7dc70c105bfae7efd9a2fd06f981d9737ee158430929dddb7fbc8a9a750123",
        ),
        0x000F9A10: (
            "SystemInit", 480,
            "da5d60f451e3a66dcc99164257f10d3749b0a9fa29e9247557ffd34ffc459985",
        ),
        0x000F9C64: (
            "__sd_nvic_app_accessible_irq", 32,
            "6550593b297ba9647a3266ddaf54b6aa7500f221db2f18f0f398c04fd063c901",
        ),
        0x000F9C88: (
            "addr_is_aligned32", 12,
            "b906512c3e519b44da44794a9b79297290919e3faeb7910b7fd70a2650f563bb",
        ),
        0x000F9C94: (
            "addr_is_within_bounds", 24,
            "b74e058e18af718a0f226725c9cb5f21b42d2d3091749ff4897d6c31185fc7d3",
        ),
        0x000F9D44: (
            "advertising_start", 44,
            "c0250e3eb13a02e0166397be663a2107ac61aafd7ad5709de9cfa5f2541e63db",
        ),
        0x000F9DC4: (
            "app_error_handler_bare", 4,
            "837b326c6823907e161ac6fdd339096c6e9f8a0abc15e3120885d20798904a6d",
        ),
        0x000F9DC8: (
            "app_sched_event_put", 154,
            "11bce1695b133d4e00572928e8d8d1bf65c1fec8e2aa789bbe789cc9a12a3920",
        ),
        0x000F9E68: (
            "app_sched_execute", 58,
            "465dfc0fa670ab460da2357349c09640c1d4282037e1e8c2f952a5469ad66a95",
        ),
        0x000F9EA8: (
            "app_sched_init", 40,
            "a7ac2f24767291b24347940b466cbeaf8ba76315d0637a946ccb0f2a5fca4862",
        ),
        0x000F9F9C: (
            "ble_dfu_init", 182,
            "eea61edc87f0e024a69e106495a3c6f91b160013f5b7b20d6576b4a1f7de7311",
        ),
        0x000FA060: (
            "ble_dfu_req_handler_callback", 170,
            "d92b00ad1ad16b1b96bc9af831d50a5cc7f237e90a83d4efe915606b79ecb9c2",
        ),
        0x000FA118: (
            "ble_dfu_transport_close", 82,
            "d3c5bbc8ff51c0c0286ed51e417d59a7129cd3d5c39debd12477e4017f57a424",
        ),
        0x000FA178: (
            "ble_dfu_transport_init", 134,
            "216b5a4902c909d1f099ea723f85e62bfc365598fcba7374f4aca4b248d6bac8",
        ),
        0x000FA210: (
            "ble_evt_handler", 456,
            "21b4babc60850280499e9cc2f6d4b6ba156aff1e0a55d958d2ac40857535a844",
        ),
        0x000FA3F0: (
            "boot_validate", 16,
            "54a05a3bcdb868802718615e76824a9af645fa448d2ac355a04ccc821522488b",
        ),
        0x000FA400: (
            "boot_validation_crc", 12,
            "4238f60b0fb3525ced2f52661e8c77efddac6e31f6c696df7a4a73b42358e805",
        ),
        0x000FA40C: (
            "boot_validation_extract", 146,
            "19eaaf42ca73ea4828d63bfb582470ca247057ce7c5470241b3ab1091c1f94df",
        ),
        0x000FA4A4: (
            "bootloader_reset", 64,
            "877e5205b0d5eeeb25a8c28e07bafc98d9515d69ce4d355cec0c8cc27e52f67f",
        ),
        0x000FA64C: (
            "cmd_response_offset_and_crc_set", 12,
            "58210c687111415b0d5829e7283caa9a5af913a458c972ac565aef5cf5e9471b",
        ),
        0x000FA698: (
            "crc_ok", 30,
            "03d833f80400007b98aca9a153ed9e7533feab1647074dd3dbf1249585768e5c",
        ),
        0x000FA6B8: (
            "crypto_init", 46,
            "5febe1e9679ce95edab322cd2e3bc14d4d453c37f63f1b15f8a992435faab257",
        ),
        0x000FA908: (
            "nrf_bootloader_dfu_observer", 56,
            "a9189c0de33c2b4ffd5444239c15927f8c9c423049ccdb1d79f19fe0320cdea7",
        ),
        0x000FA950: (
            "nrf_dfu_observer", 36,
            "5f27f84c79cec3e786edc20031d2fa9ecebc334b4c10d0261d9c85a7032fd4eb",
        ),
        0x000FAABA: (
            "ext_err_code_handle", 14,
            "ba35aaa98385c204cc5f41064121558f88314cee37ea6b3d10eb7d066e3689b3",
        ),
        0x000FAAC8: (
            "ext_error_get", 10,
            "647195b56ebceb02d0e6557fc1d44ccc4e6802bb22349ce339d8faa498bdfc1f",
        ),
        0x000FAAD8: (
            "ext_error_set", 8,
            "9daf1ee0cf9fcd1c8887a4f5ec0f42791aa548acf803c8aeda07007295491bc4",
        ),
        0x000FAA30: (
            "nrf_fstorage_nvmc_event_send", 54,
            "231d971d827e83543f844e0dd658811e064771d926ef387aab1878f3347bf69d",
        ),
        0x000FAAFC: (
            "fw_hash_ok", 8,
            "d1ca462b2b1c56e0a1c2e7cf0aba476b234df16f521e8d3be41a70f86143dbd2",
        ),
        0x000FAC3C: (
            "image_copy", 140,
            "50ecd8b2237a28008a645dbbeb0d5dcd2cfa7ce74b0dd65eec2a540f325192c0",
        ),
        0x000FAD38: (
            "is_major_softdevice_update", 88,
            "77a899e56f43d3d70ab4852601ef27dcffeab561db1f57b9bd6e5ddbb5ace729",
        ),
        0x000FADC8: (
            "main", 48,
            "8e8945bfff5170a33188cd5632d4d5d1f1f37ff9fdfb6d5552e9101ed85cced4",
        ),
        0x000FADF8: (
            "nrf_atfifo_clear", 16,
            "b66636949aaae719705addb30220da7dda0fcb43fa798a1312ea28f1b30b5a60",
        ),
        0x000FAE2E: (
            "nrf_atfifo_item_alloc", 22,
            "43f199308aa476cd9dd46f9279f875b2a9666a21f4b00a615339f72592e42490",
        ),
        0x000FAE44: (
            "nrf_atfifo_item_free", 22,
            "5097d7cfe1d97ea54f15eabeb7507fe85ace93ca9749b8eedd17bf313168eea0",
        ),
        0x000FAE5A: (
            "nrf_atfifo_item_get", 22,
            "86f478e790881f4e2134a95e311db068227d8e78ef90b0cf89479bdcd2589f8d",
        ),
        0x000FAE70: (
            "nrf_atfifo_item_put", 22,
            "090ebbc9ec27c43d1fa6271f253b6d0e218bb0382f2729ba38c758671dbf4f38",
        ),
        0x000FAE86: (
            "nrf_atomic_flag_clear", 18,
            "cf30d3e76f2b5d2e04c65b9b7777fbe834f94da5eb8eb9b4d33a0f2a370b2569",
        ),
        0x000FA978: (
            "__NVIC_SystemReset", 26,
            "4ea1bf89337cf4659a67c8d8f2468d27532846cf99c868b533e7c2196ce09327",
        ),
        0x000FAFDC: (
            "nrf_bootloader_dfu_inactivity_timer_restart", 34,
            "6bfaac965c985b9a607992f034762c67e529efcde7326b026cd25d84f615ff12",
        ),
        0x000FB198: (
            "nrf_bootloader_wdt_feed", 20,
            "0264afc58ce088bc4367ed0bad665b486a0ab154d943a13a84ba095bd6007d84",
        ),
        0x000FB1AC: (
            "nrf_bootloader_wdt_feed_timer_start", 16,
            "d40136eeec3bea67b6b1d1e8002826d04bd59e17ebef17e488ed58658cd04eb6",
        ),
        0x000FB1C0: (
            "nrf_bootloader_wdt_init", 60,
            "1cb2ae9120fc27e22697106f0eb125a93d20d6058fe0c67e2678bffb2b233726",
        ),
        0x000FB298: (
            "nrf_crypto_ecc_public_key_from_raw", 48,
            "45d9da8f0cbbb1e30a226a36b46bc841f9178cbb8559f981880f930a27f1993b",
        ),
        0x000FB3B8: (
            "nrf_crypto_hash_update", 46,
            "500a5ff46f17029f862a98d5a15fcb2223050bb210d16b5eb6fd40624769a724",
        ),
        0x000FB428: (
            "nrf_crypto_internal_double_swap_endian", 26,
            "d603a94358a5b30dbdea4bb821f264668fa60325fdec413fda6612c631b1b0a3",
        ),
        0x000FB4A0: (
            "nrf_crypto_internal_swap_endian", 20,
            "bac2cd00625bfc47c0f4ef772413509406d3c5ae6201300d9ebb221d1c4f4f31",
        ),
        0x000FB4D0: (
            "nrf_dfu_bank0_start_addr", 34,
            "b61b3f7421f251a02a73701164ee7727b49dee2543ce0a81b59334a0f9957460",
        ),
        0x000FB4F8: (
            "nrf_dfu_bank1_start_addr", 28,
            "6300f3e5776df3b331ad9264de9f9c6180bd24f6e7bdeb1bac914966e07b5fa5",
        ),
        0x000FB518: (
            "nrf_dfu_bank_invalidate", 14,
            "2ae2399d012407447b64fae017ff3b224f6dc8cd2e1bc6351c07a238c376abb6",
        ),
        0x000FB52C: (
            "nrf_dfu_cache_prepare", 140,
            "c5d75ac9dadb26f5237ba6e4f92a1382f6e8a40d9f043d30ffbfb42023f134fe",
        ),
        0x000FB5C4: (
            "nrf_dfu_command_req", 132,
            "1d668c7a2fb6c053ac4680a27d6af9b8bbd42a36a49b35415a11bb53206bb0d1",
        ),
        0x000FB658: (
            "nrf_dfu_data_req", 98,
            "9793d75d880237a13f8f53b7c22ed9d26d7fdcce96b6e774170269e80f383607",
        ),
        0x000FB6CC: (
            "nrf_dfu_flash_erase", 12,
            "694411ba6476eadc7bf482bf87573401ee1b8a2b40ee832ec4ac87bfd496d621",
        ),
        0x000FB6F8: (
            "nrf_dfu_flash_store", 18,
            "3b0c182477f644dc454d147592056cb887d8caf61e5e4155d852e69ffca8c477",
        ),
        0x000FB710: (
            "nrf_dfu_init", 96,
            "8a53bdcdd893820ceaa3182ee30ad7cef27c8a71994520c21b44036f9cdd6485",
        ),
        0x000FB73C: (
            "nrf_dfu_init_user", 4,
            "a7ddd513d149ea16fdd4db3f82267f83087aeaddd06b5dde5468adb704205fc4",
        ),
        0x000FB758: (
            "nrf_dfu_mbr_init_sd", 18,
            "d97f2ea709cb9ed3dbffaf1b083cedf19a2b542b0c03376da7e0370c41ef3b5b",
        ),
        0x000FB7D8: (
            "nrf_dfu_req_handler_req_process", 122,
            "96f0d637dabdf9ab01bdd48585964a7ccb06c98fc980bae8caa9f8a86c717a38",
        ),
        0x000FB8E4: (
            "nrf_dfu_settings_additional_erase", 46,
            "5c98715c76cc8849db2a3cf901be0a1163c1e0f3fc33a5b4d352cf23f4e31680",
        ),
        0x000FB918: (
            "nrf_dfu_settings_adv_name_copy", 20,
            "402d9ba54d878e381f61626f58cceca89a9088952106305a2ef196000ca67b55",
        ),
        0x000FB988: (
            "nrf_dfu_settings_backup", 6,
            "18f5eb6744bb9b72e0d56007e78b98cfc163d6cea4893ac3a8379f21a49b44fe",
        ),
        0x000FB9B0: (
            "nrf_dfu_settings_progress_reset", 34,
            "0017b2d2805e04992c78baaa7f6091b71b8a74294b27cfb69b0fe68c9b5dd441",
        ),
        0x000FBAAC: (
            "nrf_dfu_settings_write", 42,
            "16b6181cf9593fe599363c12de3ad6531232de77966a4d0314253fa03e62ab6b",
        ),
        0x000FBB00: (
            "nrf_dfu_softdevice_start_address", 6,
            "fce73b48c1bea4842c7e22803d0c63eaf4a58a8a8413927a3a2202d1e7b9c970",
        ),
        0x000FBC28: (
            "nrf_dfu_validation_init", 26,
            "0ee22e58d32651a0711b69f5d287019c8cbf867ccbcf2b5a10995f38f3379a93",
        ),
        0x000FBC4C: (
            "nrf_dfu_validation_init_cmd_append", 66,
            "4695a584d1f21d82160728543b0d2f14b37ed5779a28c24f55bfbd11bdfb7986",
        ),
        0x000FBCC8: (
            "nrf_dfu_validation_init_cmd_execute", 138,
            "5b0aecfac864453c1544186e36d4bb7b1f0527cdfd47f62caa8e62ff81feaf04",
        ),
        0x000FBD5C: (
            "nrf_dfu_validation_init_cmd_present", 6,
            "8f61f3207c802be9d89b3cfa1748adc458586b81abe646a9bf7b237057fa521b",
        ),
        0x000FBED4: (
            "nrf_fstorage_erase", 44,
            "525b0a0f25cd9c2531905b9405d2485cb45137081c1b2337ad4763f4aa978aae",
        ),
        0x000FBF90: (
            "nrf_fstorage_sys_evt_handler", 150,
            "5ed0479726e1305cc5c00502716b4e30b8f6c543848d845545db1901d69b085f",
        ),
        0x000FC030: (
            "nrf_fstorage_write", 62,
            "bc7df19ba95edede1ad801a7a7021b63a4b5e84498433c50cc2d107edaccde42",
        ),
        0x000FC070: (
            "nrf_nvmc_page_erase", 40,
            "9b6d989371241a975e1810e5f28d0154fd2580bc491e54d08242d17d02e7aa99",
        ),
        0x000FC0A0: (
            "nrf_nvmc_write_word", 38,
            "0fb5e186e897d8517694e64a08aa482d58869ac2e9ae41b99839beea8fb80b75",
        ),
        0x000FC0D0: (
            "nrf_nvmc_write_words", 56,
            "015e7090042faa30998de8a9f1479591a3e524c51cc6bba327d7c6fbc5ee53f1",
        ),
        0x000FAE8C: (
            "nrf_atomic_u32_fetch_or", 16,
            "96d2766b6865d63a8374d1eac17c94f929b68faef34859b72ffec4f4cfdabe74",
        ),
        0x000FAEA8: (
            "nrf_atomic_u32_fetch_store", 10,
            "ffbb49d572d43af5e5fc51e4636b48bb1e157aaeed4683aeb89db486ec14cf03",
        ),
        0x000FC440: (
            "nrf_wdt_started", 12,
            "9409ea849640d70f4fa8db6c4696be986ee7995994fbe949d53d000e96c5e614",
        ),
        0x000FC114: (
            "nrf_rtc_event_clear", 12,
            "5e1952a6b7b33b87b711a2742f043070d96e1cb4a2de8734e22f471f174ff60a",
        ),
        0x000FC134: (
            "nrf_sdh_ble_default_cfg_set", 156,
            "a6b481bb0e72e0c09d134581204635a4ac92d36cdd3125feb2b1ae29ea1479b5",
        ),
        0x000FC1D0: (
            "nrf_sdh_ble_enable", 14,
            "364f4f5677e9f3c1c14952601dc3e68bf2ddd8b2aaa770c87c4f7fa08e784a0e",
        ),
        0x000FC1E4: (
            "nrf_sdh_soc_evts_poll", 88,
            "1af6ca292ce48b2bd7a6eae6b69891dd5b6c709dca40ed59f3752ca754af5c3a",
        ),
        0x000FC244: (
            "nrf_sdh_disable_request", 80,
            "b7f991fa26dac1ebbb986557020dc8a8824333914df370e305c6d8a50ca2763f",
        ),
        0x000FC298: (
            "nrf_sdh_enable_request", 102,
            "dd4ea3564657ed94dcb5449a0f7dd5b93f7cf620f20d8ebbc31d3c356011c198",
        ),
        0x000FC330: (
            "nrf_sdh_is_enabled", 6,
            "8f61f3207c802be9d89b3cfa1748adc458586b81abe646a9bf7b237057fa521b",
        ),
        0x000FC394: (
            "nrf_section_iter_init", 46,
            "b28cfe6d01b836fea2101e5209ff8b1567cfa060f3efafe415d9388f4d9f3a71",
        ),
        0x000FC468: (
            "on_ctrl_pt_write", 102,
            "2ee0456eba7245e3a3eef2ec72073980f3a6808f00b2fa4f2eec10457a8c43a0",
        ),
        0x000FC684: (
            "on_flash_write", 8,
            "b5a40093755512a2dfd9e0e1a849bb314d3a75e31c84009ebb52a3fc6eb1014e",
        ),
        0x000FC654: (
            "app_error_fault_handler", 38,
            "52ef80ce5d98f9d709768c97c4ef59b5d2e21ef077209556a51ff9b0c3863c47",
        ),
        0x000FC690: (
            "on_rw_authorize_req", 128,
            "94be536bf2c32818e1b75f9d710789165f7f282ff3cae46afc2d7beeeafc88a2",
        ),
        0x000FCFF0: (
            "postvalidate", 244,
            "63a4122c5aecae004227914824e7bdc5c6f552900b236da149c9164d4ec5fa6c",
        ),
        0x000FD0F0: (
            "queue_free", 10,
            "e744d1a5450254363b396aebcbaeb3fc5e08ed69684433506e8684951e17ef8f",
        ),
        0x000FD104: (
            "queue_process", 144,
            "fe8134d73b64628f4d3ceaa86f6f251182723b2789e930e1b0eb82ed3b45dce6",
        ),
        0x000FD1A0: (
            "queue_start", 30,
            "c05ff0ea62cb6550ea1df807d19d30a7075c5bcb4d85c8d582859e64861e44d9",
        ),
        0x000FD242: (
            "response_crc_add", 32,
            "02fe105d8539c209065851ef23f69304578d1a25d39ba5a4c9120d101ee8a154",
        ),
        0x000FD264: (
            "response_send", 40,
            "bb2b8867321d35e51d9e96b5ecb5c79e7ff326eeabed5fd04272a569de653400",
        ),
        0x000FD2F4: (
            "sd_req_check", 64,
            "cf50713cf421329b1a598ebc59e58a17e858c4f0f148320cfe5ce2426de52106",
        ),
        0x000FD338: (
            "sd_req_ok", 100,
            "e4ecc8512b0bc7046bbf36f4b7fbb3992598a62627bfab502c28afb8f3237987",
        ),
        0x000FD3FC: (
            "settings_backup", 12,
            "6643bf28e6a39993ecc24185c74f5375bb3e602791c69ad3e86614a64f02b51a",
        ),
        0x000FD410: (
            "settings_crc_get", 10,
            "735feb9d7b2d61c1e072ab20a55cacb0b279ecaafb63d0609694cf1394c03158",
        ),
        0x000FD46C: (
            "softdevice_evt_irq_disable", 60,
            "6f0858643952038f6a988b417bf76b7c931659b2cbb9db50e1228269419f952e",
        ),
        0x000FD4AC: (
            "softdevices_evt_irq_enable", 80,
            "eb6c7d62f974917bcad52e80269a34e15af4d0cf87f79e1ec071bb7956e11c9e",
        ),
        0x000FD504: (
            "stored_init_cmd_decode", 172,
            "6a345006d3895793337a1789a768625d7ce87413263d61041a7a9d72a5bc15e0",
        ),
        0x000FD6A0: (
            "timer_start", 26,
            "a40a908dd9187f911b8eb0e22de20d7d4527e7ca2a5fbe3084099c6eabd16d7f",
        ),
        0x000FD62C: (
            "timer_init", 96,
            "9aca305f2347676599827273eadb7f27f4b76ce9dfb8207d28712e18d7c0da6b",
        ),
        0x000FD6BC: (
            "timer_stop", 16,
            "79f49349a0a43f4e27052ec3d49bf1ade875956495d9d362ce97a8f957e88eac",
        ),
        0x000FD6D0: (
            "uint32_encode", 18,
            "0111299d7841e5eb33fbbbffa536834512131a606ef63ba5d713abccd751b4f4",
        ),
        0x000FD78C: (
            "wdt_feed", 48,
            "7fb46498f42bbadc8287fde9899ba5fff302328024e9d819552bb9f1ba2be690",
        ),
        0x000FD76C: (
            "verify_context", 26,
            "48756f814ab11e6cc66a45ecc56a6b466698b0d9c44198a4fca744b8ae5d4fe1",
        ),
        0x000FD7C8: (
            "wdt_feed_timer_handler", 4,
            "9f55df6d28ca20571e0a8c6a8466f4ccbc476981a4304d8a74cc612327f1c457",
        ),
        0x000FD8B0: (
            "nrfx_coredep_delay_machine_code_dfu_timers", 6,
            "583d680532875ef2b855cbedbdfcdbdd74329d19ba88d3e52c36b6b634a75165",
        ),
        0x000FDAA0: (
            "nrfx_coredep_delay_machine_code_ble_dfu", 6,
            "583d680532875ef2b855cbedbdfcdbdd74329d19ba88d3e52c36b6b634a75165",
        ),
    }
    for entry, (symbol, size, digest) in nordic_boot_promotions.items():
        row = ownership_by_key[("bootloader", f"0x{entry:08x}")]
        if entry == 0x000FAE86:
            body = (
                bootloader[0x000FAE86 - bootloader_base:0x000FAE8C - bootloader_base]
                + bootloader[0x000FAE92 - bootloader_base:0x000FAE9E - bootloader_base]
            )
        elif entry == 0x000FAE8C:
            body = (
                bootloader[0x000FAE8C - bootloader_base:0x000FAE92 - bootloader_base]
                + bootloader[0x000FAE9E - bootloader_base:0x000FAEA8 - bootloader_base]
            )
        elif entry == 0x000FC0D0:
            body = (
                bootloader[0x000FC0D0 - bootloader_base:0x000FC0E6 - bootloader_base]
                + bootloader[0x000FC0E8 - bootloader_base:0x000FC10A - bootloader_base]
            )
        elif entry == 0x000FA060:
            body = (
                bootloader[0x000FA060 - bootloader_base:0x000FA0C8 - bootloader_base]
                + bootloader[0x000FA0D2 - bootloader_base:0x000FA114 - bootloader_base]
            )
        elif entry == 0x000FA908:
            body = (
                bootloader[0x000FA908 - bootloader_base:0x000FA916 - bootloader_base]
                + bootloader[0x000FA91C - bootloader_base:0x000FA946 - bootloader_base]
            )
        elif entry == 0x000FB5C4:
            body = (
                bootloader[0x000FB5C4 - bootloader_base:0x000FB5D2 - bootloader_base]
                + bootloader[0x000FB5DC - bootloader_base:0x000FB652 - bootloader_base]
            )
        elif entry == 0x000FB658:
            body = (
                bootloader[0x000FB658 - bootloader_base:0x000FB66A - bootloader_base]
                + bootloader[0x000FB674 - bootloader_base:0x000FB6C4 - bootloader_base]
            )
        elif entry == 0x000FB710:
            body = (
                bootloader[0x000FB710 - bootloader_base:0x000FB732 - bootloader_base]
                + bootloader[0x000FB77C - bootloader_base:0x000FB7BA - bootloader_base]
            )
        elif entry == 0x000FB7D8:
            body = (
                bootloader[0x000FB7D8 - bootloader_base:0x000FB7FA - bootloader_base]
                + bootloader[0x000FB808 - bootloader_base:0x000FB860 - bootloader_base]
            )
        elif entry == 0x000FB4A0:
            body = (
                bootloader[0x000FB4A0 - bootloader_base:0x000FB4A6 - bootloader_base]
                + bootloader[0x000FB4A8 - bootloader_base:0x000FB4B6 - bootloader_base]
            )
        else:
            body = bootloader[entry - bootloader_base:entry - bootloader_base + size]
        if row["provider_family"] != "nordic_nrf5_sdk_17_1_0" or \
                row["source_disposition"] != "use_nordic_sdk" or \
                row["upstream_symbol"] != symbol or int(row["size"]) != size or \
                hashlib.sha256(body).hexdigest() != digest:
            raise AssertionError(f"Nordic bootloader promotion mismatch: 0x{entry:08x}")

    cryptocell_backend_promotions = {
        0x000F852C: (
            "PkaAddAff", 216,
            "0d0b2ddc6ffcef0884e17d85ae735fca1a8814f82f8a7532aecdd85b09d55a19",
        ),
        0x000F8640: (
            "PkaAddJcbAfn2Mdf", 322,
            "70ed8e26a1bafc034001871fa2ec57728ff3bde11aaced5f500483216c3365a7",
        ),
        0x000F89D0: (
            "PkaDoubleMdf2Jcb", 296,
            "2ed05c14fae1a1bd3b88ea898ebd3d48d5743a21d26ed113d77a70ab46462b0a",
        ),
        0x000F8B48: (
            "PkaDoubleMdf2Mdf", 338,
            "b8f3707a05547580fefb5854be2118706c78347e7cf5b54ed1e249af33ac2651",
        ),
        0x000F8CF4: (
            "PkaEcdsaVerify", 530,
            "8f561de4492fd2208c4d6428a1e582cbd731692507dccf592d6c77314658c200",
        ),
        0x000F943C: (
            "SaSi_HalClearInterruptBit", 6,
            "0ea0eeeaa936aad60a1bc2a6f4bfe3b22a8689142dafe23415923eae2c53359e",
        ),
        0x000F9448: (
            "SaSi_HalMaskInterrupt", 6,
            "0ea0eeeaa936aad60a1bc2a6f4bfe3b22a8689142dafe23415923eae2c53359e",
        ),
        0x000F9488: (
            "SaSi_PalMemCopy", 4,
            "b31a78635019051792675597279d09f8d2dc56a9a81d583a58202ae1fb8c4b65",
        ),
        0x000F948C: (
            "SaSi_PalMemSet", 4,
            "f462a75c10eecacfc68c3018c2aacdc8fd13d64439590d2b2c425b28e303f912",
        ),
        0x000FA4E4: (
            "cc310_backend_mutex_trylock", 24,
            "5d19045ab33f24e7c1c5d1ad5c952467c65e48d856f37e97b6d36ec58af763fc",
        ),
        0x000FA500: (
            "cc310_backend_mutex_unlock", 12,
            "5725b882794cd6f230b2a690711e7d34646b679dd3ba2da8ff52d9501847f04a",
        ),
        0x000FA510: (
            "cc310_bl_backend_disable", 26,
            "ffadfa87676bbd9cf8ac67c602b14c1686d9f6cbb33e261873fea93c01a3ecf8",
        ),
        0x000FA534: (
            "cc310_bl_backend_enable", 16,
            "0922f39a6629398bb28ffbec54c1d670dd516af03196314c76fca47224bbd8a9",
        ),
        0x000FA54C: (
            "cc310_bl_backend_hash_sha256_finalize", 72,
            "3892de533a91fea2eb4474d1e136145ae0959e785a4cd93e07038f5f2a197e0c",
        ),
        0x000FA594: (
            "cc310_bl_backend_hash_sha256_init", 16,
            "35bb1e4cdbd0611a5cd565ff6e8a530213f2ecbb21b38ef97ead790867d1b2f9",
        ),
        0x000FA5A4: (
            "cc310_bl_backend_hash_sha256_update", 96,
            "63760d1a2e7b1f989835eeee504b1fcf32519a54cce84922f529b4e0328cfa03",
        ),
        0x000FA608: (
            "cc310_bl_backend_init", 46,
            "058d412ebaf0bdb581e8809d59f439b78e2396bf1cd25211f8aeb762fc3b503d",
        ),
        0x000FA640: (
            "cc310_bl_backend_uninit", 8,
            "2a2b97085986b02143a8171eac24af4f9b49691b9896ad89544ac517bfe5e159",
        ),
        0x000FABF4: (
            "hash_result_get", 64,
            "af82a60c8767bac6752b56d32023ea0081ee7d4a52fcb1140c5e67709f0947db",
        ),
    }
    for entry, (symbol, size, digest) in cryptocell_backend_promotions.items():
        row = ownership_by_key[("bootloader", f"0x{entry:08x}")]
        body = bootloader[entry - bootloader_base:entry - bootloader_base + size]
        if row["provider_family"] != "arm_cryptocell_cc310" or \
                row["source_disposition"] != "use_nordic_supplied_provider" or \
                row["upstream_symbol"] != symbol or int(row["size"]) != size or \
                hashlib.sha256(body).hexdigest() != digest:
            raise AssertionError(f"CryptoCell backend promotion mismatch: 0x{entry:08x}")

    gpio_groups = {
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
    gpio_entries = {
        entry for entries in gpio_groups.values() for entry in entries
    }
    if len(gpio_entries) != 52:
        raise AssertionError("Nordic GPIO correlation inventory changed")
    for symbol, entries in gpio_groups.items():
        for entry in entries:
            row = ownership_by_key[("application", f"0x{entry:08x}")]
            if row["provider_family"] != "nordic_nrf5_sdk_17_1_0" or \
                    row["source_disposition"] != "use_nordic_sdk" or \
                    row["upstream_symbol"] != symbol or \
                    "modules/nrfx/hal/nrf_gpio.h" not in row["evidence"]:
                raise AssertionError(f"Nordic GPIO ownership mismatch: 0x{entry:08x}")

    def recovered_function(entry: int) -> bytes:
        row = ownership_by_key[("application", f"0x{entry:08x}")]
        size = int(row["size"])
        offset = entry - recovered_base
        return recovered[offset:offset + size]

    gpio_decode = bytes.fromhex(
        "0168202902d24ff0a040704701f01f01016001487047"
    )
    for entry in gpio_groups["nrf_gpio_pin_port_decode"]:
        if recovered_function(entry) != gpio_decode:
            raise AssertionError(f"Nordic GPIO pin/port decoder changed: 0x{entry:08x}")
    for entry in gpio_groups["nrf_gpio_cfg"]:
        body = recovered_function(entry)
        packed = b"\x46\xea\x45\x01\x41\xea\x84\x01" in body or \
            b"\x41\xea\x42\x01\x41\xea\x83\x01" in body
        if not packed or bytes.fromhex("c0f80017") not in body:
            raise AssertionError(f"Nordic GPIO configuration body changed: 0x{entry:08x}")
    for entry in gpio_groups["nrf_gpio_pin_clear"]:
        if bytes.fromhex("c0f80c15") not in recovered_function(entry):
            raise AssertionError(f"Nordic GPIO clear body changed: 0x{entry:08x}")
    for entry in gpio_groups["nrf_gpio_pin_read"]:
        if bytes.fromhex("d0f81005") not in recovered_function(entry):
            raise AssertionError(f"Nordic GPIO read body changed: 0x{entry:08x}")
    for entry in gpio_groups["nrf_gpio_pin_set"]:
        if bytes.fromhex("c0f80815") not in recovered_function(entry):
            raise AssertionError(f"Nordic GPIO set body changed: 0x{entry:08x}")
    if bytes.fromhex("22f44032") not in recovered_function(0x00079120) or \
            bytes.fromhex("d1f82055") not in recovered_function(0x00079150):
        raise AssertionError("Nordic GPIO sense/latch bodies changed")
    gpiote_expected = {
        0x000794FC: (
            "nrf_gpiote_event_clear",
            bytes.fromhex("034908b50844002101600068009008bd"),
        ),
        0x00079510: (
            "nrf_gpiote_event_is_set",
            bytes.fromhex("02494058012800d000207047"),
        ),
    }
    for entry, (symbol, body) in gpiote_expected.items():
        row = ownership_by_key[("application", f"0x{entry:08x}")]
        if row["provider_family"] != "nordic_nrf5_sdk_17_1_0" or \
                row["upstream_symbol"] != symbol or \
                "modules/nrfx/hal/nrf_gpiote.h" not in row["evidence"] or \
                recovered_function(entry) != body:
            raise AssertionError(f"Nordic GPIOTE ownership/body mismatch: 0x{entry:08x}")
    hal_inline_expected = {
        0x0007A58A: ("nrf_spim_event_check", "nrf_spim.h",
                     "4058002800d001207047"),
        0x00079CDC: ("nrf_nfct_event_check", "nrf_nfct.h",
                     "02494058002800d001207047"),
        0x00079CEC: ("nrf_nfct_event_clear", "nrf_nfct.h",
                     "024a00218150bff34f8f7047"),
        0x00079CFC: ("nrf_nfct_int_enable_check", "nrf_nfct.h",
                     "0449d1f80413014201d00120704700207047"),
        0x00079D14: ("nrf_pdm_event_check", "nrf_pdm.h",
                     "02494058002800d001207047"),
        0x00079D24: ("nrf_pdm_event_clear", "nrf_pdm.h",
                     "034908b50844002202600068009008bd"),
        0x00079D38: ("nrf_pwm_event_check", "nrf_pwm.h",
                     "4058002800d001207047"),
        0x00079D42: ("nrf_pwm_event_clear", "nrf_pwm.h",
                     "08b5002242504058009008bd"),
        0x00079DE8: ("nrf_rtc_event_clear", "nrf_rtc.h",
                     "08b5002242504058009008bd"),
        0x00079DF4: ("nrf_rtc_event_clear", "nrf_rtc.h",
                     "08b5002242504058009008bd"),
        0x00079E00: ("nrf_saadc_buffer_init", "nrf_saadc.h",
                     "024a1060101d01607047"),
        0x00079E24: ("nrf_saadc_event_check", "nrf_saadc.h",
                     "02494058002800d001207047"),
        0x00079E34: ("nrf_saadc_event_clear", "nrf_saadc.h",
                     "034908b50844002202600068009008bd"),
        0x0007A60C: ("nrf_timer_event_clear", "nrf_timer.h",
                     "08b5002242504058009008bd"),
        0x0007A618: ("nrf_twim_event_check", "nrf_twim.h",
                     "4058002800d001207047"),
        0x0007A622: ("nrf_twim_event_clear", "nrf_twim.h",
                     "08b5002242504058009008bd"),
    }
    for entry, (symbol, source, body_hex) in hal_inline_expected.items():
        row = ownership_by_key[("application", f"0x{entry:08x}")]
        if row["provider_family"] != "nordic_nrf5_sdk_17_1_0" or \
                row["upstream_symbol"] != symbol or source not in row["evidence"] or \
                recovered_function(entry) != bytes.fromhex(body_hex):
            raise AssertionError(f"Nordic HAL inline mismatch: 0x{entry:08x}")
    clock_driver_expected = {
        0x0003BC78: (
            "__sd_nvic_app_accessible_irq", "components/softdevice/s140/headers/nrf_nvic.h",
            "0121202803da81400548014003e0402802da2038814009b10120704700207047",
        ),
        0x0004EBEC: (
            "sd_nvic_critical_region_enter", "components/softdevice/s140/headers/nrf_nvic.h",
            "30b5eff3108172b60d4a9468012324b10370002900d162b630bd93604ff0e023"
            "d3f88051074c25401560c3f88041d3f8844154605a17c3f8842100220270e8e7",
        ),
        0x0004EC34: (
            "sd_nvic_critical_region_exit", "components/softdevice/s140/headers/nrf_nvic.h",
            "0b498a68002a11d000280fd1eff3108072b60b684ff0e022c2f800314b68c2f8"
            "043100228a60002800d162b67047",
        ),
        0x000584AC: (
            "clock_clk_started_notify", "integration/nrfx/legacy/nrf_drv_clock.c",
            "70b5084c050009d010342168002907d008682060496828468847f6e70834f4e7",
        ),
        0x000584D4: (
            "clock_irq_handler", "integration/nrfx/legacy/nrf_drv_clock.c",
            "054a012120b1012805d19170fff7e4bf51700020fae77047",
        ),
        0x00072BCA: (
            "item_enqueue", "integration/nrfx/legacy/nrf_drv_clock.c",
            "0268134602e08a4204d01268002afad10b6001607047",
        ),
        0x000788C8: (
            "nrf_drv_clock_init", "integration/nrfx/legacy/nrf_drv_clock.c",
            "f8b5184c0125207808b185260ee00020a06060602061e060134801f0c3fe0646"
            "01f0f6fd08b901f0a7fe257001f09cfe00b1a57018f0f6fdc00703d118f0f2fd"
            "40070ad5304601f05dfe0090074b08a207a14ff0486018f08bfe18f0e3fd3046f8bd",
        ),
        0x00078990: (
            "nrf_drv_clock_lfclk_request", "integration/nrfx/legacy/nrf_drv_clock.c",
            "f8b5134d0446a878002648b114b16168012088478df800606846d6f71ff90ee0"
            "8df800606846d6f719f924b1084821461030faf702f9e86808b901f05ffee8684"
            "01ce8609df80000d6f72cf9f8bd",
        ),
        0x00090814: (
            "softdevice_evt_irq_disable", "components/softdevice/common/nrf_sdh.c",
            "10b51620abf72efa48b10c4882684ff4800152b1016821f48001016010bdbde8"
            "104042f20100bdf7bfbe4ff0e020c0f88011bff34f8fbff36f8f10bd",
        ),
        0x00090854: (
            "softdevices_evt_irq_enable", "components/softdevice/common/nrf_sdh.c",
            "10b51620abf70efaa0b1114890f800044009082811d20121814011f0ec0f0cd0"
            "0c4882684ff480016ab1016841f48001016010bd42f2010001e042f20200bde8"
            "1040bdf791be4ff0e020c0f8001110bd",
        ),
        0x0007A630: (
            "nrf_wdt_started", "modules/nrfx/hal/nrf_wdt.h",
            "02480068002800d001207047",
        ),
        0x0007A640: (
            "nrfx_clock_enable", "modules/nrfx/drivers/src/nrfx_clock.c",
            "08480068012110f0010f06d14ff0e020c02280f800248430c1670349002008607047",
        ),
        0x0007A66C: (
            "nrfx_clock_init", "modules/nrfx/drivers/src/nrfx_clock.c",
            "0649024600200b790bb18520704700238b710a6001220a714b717047",
        ),
        0x0007A68C: (
            "nrfx_clock_lfclk_start", "modules/nrfx/drivers/src/nrfx_clock.c",
            "10b54ff48270fdf704ff02204107c1f8040302490120086010bd",
        ),
    }
    for entry, (symbol, source, body_hex) in clock_driver_expected.items():
        row = ownership_by_key[("application", f"0x{entry:08x}")]
        if row["provider_family"] != "nordic_nrf5_sdk_17_1_0" or \
                row["upstream_symbol"] != symbol or source not in row["evidence"] or \
                recovered_function(entry) != bytes.fromhex(body_hex):
            raise AssertionError(f"Nordic CLOCK driver mismatch: 0x{entry:08x}")
    delay_twi_expected = {
        0x0002EB34: (
            "nrf_delay_ms", "components/libraries/delay/nrf_delay.h",
            "70b5040006d04ff47a7528464bf0f4fd641efad170bd",
        ),
        0x00078490: (
            "nrf_power_event_check", "modules/nrfx/hal/nrf_power.h",
            "00f180400068002800d001207047",
        ),
        0x0007849E: (
            "nrf_power_event_clear", "modules/nrfx/hal/nrf_power.h",
            "08b500f18040002101600068009008bd",
        ),
        0x0007A71C: (
            "nrfx_coredep_delay_us", "modules/nrfx/soc/nrfx_coredep.h",
            "002802d00149800108477047",
        ),
        0x0007A72C: (
            "nrfx_coredep_delay_us", "modules/nrfx/soc/nrfx_coredep.h",
            "002802d00149800108477047",
        ),
        0x000938BC: (
            "twi_clear_bus", "integration/nrfx/legacy/nrf_drv_twi.c",
            "38b5044640f20c602168890001f1a041c1f800076168890001f1a041c1f80007"
            "2068e5f703fe6068e5f700fe216840f20d60890001f1a041c1f8000761688900"
            "01f1a041c1f800070420e6f709ff0025606800906846e5f729fdd0f810050099"
            "c84010f0010f02d0002d1ad00ee02068e5f778fc0420e6f7f3fe2068e5f7d6fd"
            "0420e6f7edfe6d1c092de1db6068e5f769fc0420e6f7e4fe6068bde83840e5f7"
            "c5bd38bd",
        ),
    }
    delay_ms_entries = (
        0x000784B0, 0x000784D0, 0x000784F0, 0x00078510,
        0x00078530, 0x00078550, 0x00078570, 0x0007F15C,
    )
    for entry in delay_ms_entries:
        delay_twi_expected[entry] = (
            "nrf_delay_ms", "components/libraries/delay/nrf_delay.h",
            "2de9f041040007d0044e4ff47a47751c3846a847641efad1bde8f081",
        )
    delay_machine_code_entries = (
        0x00099340, 0x00099CB0, 0x00099CC0, 0x00099CD0, 0x00099CE0,
        0x00099CF0, 0x00099D00, 0x00099D10, 0x0009A5F0, 0x0009A610,
        0x0009A670, 0x0009A6A0, 0x0009A710, 0x0009BB10, 0x0009C9E0,
    )
    for entry in delay_machine_code_entries:
        delay_twi_expected[entry] = (
            "nrfx_coredep_delay_us::delay_machine_code",
            "modules/nrfx/soc/nrfx_coredep.h", "0338fdd87047",
        )
    for entry, (symbol, source, body_hex) in delay_twi_expected.items():
        row = ownership_by_key[("application", f"0x{entry:08x}")]
        if row["provider_family"] != "nordic_nrf5_sdk_17_1_0" or \
                row["upstream_symbol"] != symbol or source not in row["evidence"] or \
                recovered_function(entry) != bytes.fromhex(body_hex):
            raise AssertionError(f"Nordic delay/TWI mismatch: 0x{entry:08x}")
    gpiote_driver_expected = {
        0x00057934: (
            "channel_free", "modules/nrfx/drivers/src/nrfx_gpiote.c",
            "05494ff0ff32082841f8202002d3084480f868207047",
        ),
        0x00057950: (
            "channel_port_alloc", "modules/nrfx/drivers/src/nrfx_gpiote.c",
            "f0b54ff0ff3512b10023082601e0082310260c4c05e000bf54f823707f1c04d0"
            "5b1cb342f8d32846f0bd26185db286f8405044f82310002af5d1e11881f86800",
        ),
        0x00057998: (
            "channel_port_get", "modules/nrfx/drivers/src/nrfx_gpiote.c",
            "0249084490f940007047",
        ),
        0x00078176: (
            "nrf_bitmask_bit_is_set", "components/libraries/util/nrf_bitmask.h",
            "c20800f007030120895c984008407047",
        ),
        0x0007A73C: (
            "nrfx_gpiote_in_event_disable", "modules/nrfx/drivers/src/nrfx_gpiote.c",
            "10b5044604f0f4fc28b12046bde810400021fef7e7bc204604f0f6fc00280fd0"
            "2046ddf71bf9074a02eb8001d1f8103523f00103c1f8103501218140c2f8081310bd",
        ),
        0x0007A784: (
            "nrfx_gpiote_in_event_enable", "modules/nrfx/drivers/src/nrfx_gpiote.c",
            "2de9f0410d46064604f0cefc0028304615d0ddf7fff8083806f0ecfb032802d0"
            "01280ad003e03046fef737fe28b103213046bde8f041fef7b1bc0221f8e704f0"
            "bffc002822d03046ddf7e4f804464ff4807000eb84000e4f81b207eb8400d0f8"
            "102542f00102c0f810250846fef784fe002d0bd03046ddf7cdf8064951f82000"
            "002803d00120a040c7f80403bde8f081",
        ),
        0x0007A81C: (
            "nrfx_gpiote_in_init", "modules/nrfx/drivers/src/nrfx_gpiote.c",
            "2de9fc41dff8bc80044608eb0400002790f940001346c0170e46401c01d00827"
            "4de0b0781946c0f340022046ddf782f80546401c42d0b07841071ad4c0070dd0"
            "68460094fef766fd009900eb8101d1f8000720f00200c1f8000707e000217378"
            "204600910a460191fef77afb204604f041fcb078800718d51348317800eb8500"
            "d0f81025114b1a40c0f810254ff47c524ff4403302ea042203ea01410a43d0f8"
            "10150a43c0f8102509e008eb0500327810f8681f41ea8211017000e004273846"
            "bde8fc81",
        ),
        0x0007A8EC: (
            "nrfx_gpiote_in_uninit", "modules/nrfx/drivers/src/nrfx_gpiote.c",
            "70b50446fff724ff204604f025fc40b12046ddf74bf8104a002102eb8000c0f8"
            "1015204604f0e6fb28b12046fef791fb204604f0e9fb0948051995f94000c017"
            "401c05d02046ddf731f8c0b2dcf7fcffff2085f8400070bd",
        ),
        0x0007F0E0: (
            "pin_configured_check", "modules/nrfx/drivers/src/nrfx_gpiote.c",
            "10b50349f9f747f8002800d0012010bd",
        ),
        0x0007F0F4: (
            "pin_configured_clear", "modules/nrfx/drivers/src/nrfx_gpiote.c",
            "10b50549c20800f007008b5c01248440a3438b5410bd",
        ),
        0x0007F110: (
            "pin_configured_set", "modules/nrfx/drivers/src/nrfx_gpiote.c",
            "10b50549c20800f00703885c01249c402043885410bd",
        ),
        0x0007F12C: (
            "pin_in_use_by_port", "modules/nrfx/drivers/src/nrfx_gpiote.c",
            "0449084490f94000082801db0120704700207047",
        ),
        0x0007F144: (
            "pin_in_use_by_te", "modules/nrfx/drivers/src/nrfx_gpiote.c",
            "0449084490f94000082801d20120704700207047",
        ),
        0x00080F78: (
            "port_handler_polarity_get", "modules/nrfx/drivers/src/nrfx_gpiote.c",
            "0249084490f8700080097047",
        ),
    }
    for entry, (symbol, source, body_hex) in gpiote_driver_expected.items():
        row = ownership_by_key[("application", f"0x{entry:08x}")]
        if row["provider_family"] != "nordic_nrf5_sdk_17_1_0" or \
                row["upstream_symbol"] != symbol or source not in row["evidence"] or \
                recovered_function(entry) != bytes.fromhex(body_hex):
            raise AssertionError(f"Nordic GPIOTE driver mismatch: 0x{entry:08x}")
    gpiote_driver_hash_expected = {
        0x0002D3B4: (
            "nrfx_gpiote_irq_handler", 156,
            "c12bb41e77dbc3f28944d77d70f7b74d6348d9b5e64ca64ce7c5ed0484b5f7d8",
        ),
        0x00080EA8: (
            "port_event_handle", 202,
            "d918c863957baffde403996408d45c75a59dbfc123765ca46a5e0454a5326e81",
        ),
    }
    for entry, (symbol, size, digest) in gpiote_driver_hash_expected.items():
        row = ownership_by_key[("application", f"0x{entry:08x}")]
        body = recovered_function(entry)
        if row["provider_family"] != "nordic_nrf5_sdk_17_1_0" or \
                row["upstream_symbol"] != symbol or \
                "modules/nrfx/drivers/src/nrfx_gpiote.c" not in row["evidence"] or \
                len(body) != size or hashlib.sha256(body).hexdigest() != digest:
            raise AssertionError(f"Nordic GPIOTE exact function mismatch: 0x{entry:08x}")
    twi_init_entry = bytes.fromhex(
        "2de9f041064604780b4815460f4640f82420083040f82430487b10b108461af0"
        "5bff0db1054a00e0002223463946301dbde8f04102f038bc"
    )
    twim_init_tail = bytes.fromhex(
        "2de9fc410646007917460d4600eb8001324a01ebc00102eb8104984694f82d10"
        "11b10820bde8fc812d4951f820103068fff70afd08b11120f4e7c4e900780027"
        "a76084f8307084f82f70687b84f832004ff00608cde9008703233a4639462868"
        "fdf760fecde900870022032311466868fdf758fed5e900123068c0f80815c0f8"
        "0c25a968c0f824152068012208b3306840f30731287b00294fea401004db01f1"
        "e02181f8000405e001f00f0101f1e02181f8140d306840f30730002809db00f0"
        "1f0102fa01f14009800000f1e020c0f8001184f82d200020a4e7"
    )
    twi_init_row = ownership_by_key[("application", "0x000789e4")]
    if twi_init_row["provider_family"] != "nordic_nrf5_sdk_17_1_0" or \
            twi_init_row["upstream_symbol"] != "nrf_drv_twi_init" or \
            "integration/nrfx/legacy/nrf_drv_twi.c" not in twi_init_row["evidence"] or \
            recovered[0x000789E4 - recovered_base:0x00078A1C - recovered_base] != twi_init_entry or \
            recovered[0x0007B28C - recovered_base:0x0007B366 - recovered_base] != twim_init_tail:
        raise AssertionError("Nordic legacy TWI/TWIM merged initializer mismatch")
    twi_driver_expected = {
        0x00078A24: (
            "nrf_drv_twi_tx", "integration/nrfx/legacy/nrf_drv_twi.h",
            "38b5001d049c009402f0b8fc38bd",
        ),
        0x00078A32: (
            "nrf_drv_twi_tx", "integration/nrfx/legacy/nrf_drv_twi.h",
            "38b5001d049c009402f0b1fc38bd",
        ),
        0x0007AC04: (
            "nrfx_is_in_ram", "modules/nrfx/drivers/nrfx_common.h",
            "0121b1eb507f01d10120704700207047",
        ),
        0x0007ACD4: (
            "nrfx_prs_acquire", "modules/nrfx/drivers/src/prs/nrfx_prs.c",
            "38b50d4609f0feff040014d000208df800006846d3f780ff207928b19df80000"
            "d3f79eff112038bd0120256020719df80000d3f795ff002038bd",
        ),
        0x0007AD0E: (
            "nrfx_prs_release", "modules/nrfx/drivers/src/prs/nrfx_prs.c",
            "10b509f0e2ff002802d000210160017110bd",
        ),
        0x0007B22C: (
            "nrfx_twim_disable", "modules/nrfx/drivers/src/nrfx_twim.c",
            "0179006801eb810202ebc101094a02eb810100228a60084bc0f80833d0f80032"
            "23f4bc53c0f80032c0f80025012081f82d007047",
        ),
        0x0007B268: (
            "nrfx_twim_enable", "modules/nrfx/drivers/src/nrfx_twim.c",
            "0179006801eb810202ebc101044a02eb81010622c0f80025022081f82d007047",
        ),
        0x0007B370: (
            "nrfx_twim_rx", "modules/nrfx/drivers/src/nrfx_twim.c",
            "f0b585b015460e4607461c46142207496846acf7ebf98df80160002269463846"
            "0395019400f058f805b0f0bd",
        ),
        0x0007B3A0: (
            "nrfx_twim_tx", "modules/nrfx/drivers/src/nrfx_twim.c",
            "2de9f04186b00e4680461c461546142168460c9facf7f9f98df8016003950194"
            "0fb1202200e000226946404600f03cf806b0bde8f081",
        ),
        0x0007B3D8: (
            "nrfx_twim_uninit", "modules/nrfx/drivers/src/nrfx_twim.c",
            "70b50446007900eb800101ebc000174901eb8005286890b1206840f307310029"
            "0ddb01f01f02012090404909890001f1e021c1f88001bff34f8fbff36f8f2046"
            "fff708ff2068fff776fc95f8320048b92068d0f80805fdf70ffe2068d0f80c05"
            "fdf70afe002085f82d0070bd",
        ),
        0x00084CD8: (
            "prs_box_get", "modules/nrfx/drivers/src/prs/nrfx_prs.c",
            "0349884201d10348704700207047",
        ),
    }
    for entry, (symbol, source, body_hex) in twi_driver_expected.items():
        row = ownership_by_key[("application", f"0x{entry:08x}")]
        if row["provider_family"] != "nordic_nrf5_sdk_17_1_0" or \
                row["upstream_symbol"] != symbol or source not in row["evidence"] or \
                recovered_function(entry) != bytes.fromhex(body_hex):
            raise AssertionError(f"Nordic TWIM driver mismatch: 0x{entry:08x}")
    twim_xfer_row = ownership_by_key[("application", "0x0007b448")]
    twim_xfer_body = (
        recovered[0x0007B448 - recovered_base:0x0007B468 - recovered_base] +
        recovered[0x00093B34 - recovered_base:0x00093DC6 - recovered_base]
    )
    if twim_xfer_row["provider_family"] != "nordic_nrf5_sdk_17_1_0" or \
            twim_xfer_row["source_disposition"] != "use_nordic_sdk" or \
            twim_xfer_row["upstream_symbol"] != "nrfx_twim_xfer" or \
            "modules/nrfx/drivers/src/nrfx_twim.c" not in \
            twim_xfer_row["evidence"] or int(twim_xfer_row["size"]) != 690 or \
            len(twim_xfer_body) != 690 or \
            hashlib.sha256(twim_xfer_body).hexdigest() != \
            "ca9b6b6b52c1b6dd2b4d481f79c68223e524ff55989efc77c5254cff187b07ab":
        raise AssertionError("Nordic TWIM non-contiguous xfer body changed")
    twim0_irq_row = ownership_by_key[("application", "0x00031a74")]
    twim0_irq_body = recovered[
        0x00031A74 - recovered_base:0x00031A7C - recovered_base
    ]
    if twim0_irq_row["provider_family"] != "nordic_nrf5_sdk_17_1_0" or \
            twim0_irq_row["source_disposition"] != "use_nordic_sdk" or \
            twim0_irq_row["upstream_symbol"] != "nrfx_twim_0_irq_handler" or \
            "modules/nrfx/drivers/src/nrfx_twim.c" not in \
            twim0_irq_row["evidence"] or int(twim0_irq_row["size"]) != 8 or \
            len(twim0_irq_body) != 8 or \
            hashlib.sha256(twim0_irq_body).hexdigest() != \
            "f01a62125b504ea5bcb65497586eaea05b19d858fee9019e93014d72a84a1d8f":
        raise AssertionError("Nordic TWIM0 IRQ veneer changed")
    twim1_irq_row = ownership_by_key[("application", "0x00031a84")]
    twim1_irq_body = (
        recovered[0x00031A84 - recovered_base:0x00031A8E - recovered_base] +
        recovered[0x000939A0 - recovered_base:0x00093B30 - recovered_base]
    )
    if twim1_irq_row["provider_family"] != "nordic_nrf5_sdk_17_1_0" or \
            twim1_irq_row["source_disposition"] != "use_nordic_sdk" or \
            twim1_irq_row["upstream_symbol"] != "nrfx_twim_1_irq_handler" or \
            "modules/nrfx/drivers/src/nrfx_twim.c" not in \
            twim1_irq_row["evidence"] or int(twim1_irq_row["size"]) != 410 or \
            len(twim1_irq_body) != 410 or \
            hashlib.sha256(twim1_irq_body).hexdigest() != \
            "73db19284fddef49ec7adca5bee9bce5705cada5e1247e69e529eb910912d270":
        raise AssertionError("Nordic TWIM1 non-contiguous IRQ body changed")
    spim2_irq_row = ownership_by_key[("application", "0x00031a94")]
    spim2_irq_body = recovered[
        0x00031A94 - recovered_base:0x00031AE0 - recovered_base
    ]
    if spim2_irq_row["provider_family"] != "nordic_nrf5_sdk_17_1_0" or \
            spim2_irq_row["source_disposition"] != "use_nordic_sdk" or \
            spim2_irq_row["upstream_symbol"] != "nrfx_spim_2_irq_handler" or \
            "modules/nrfx/drivers/src/nrfx_spim.c" not in \
            spim2_irq_row["evidence"] or int(spim2_irq_row["size"]) != 76 or \
            len(spim2_irq_body) != 76 or \
            hashlib.sha256(spim2_irq_body).hexdigest() != \
            "8880914797b095ddd94c30fc9d2a848786a4c20e121d55d635d6116c042f4c64":
        raise AssertionError("Nordic SPIM2 IRQ body changed")
    rtc_timer_irq_expected = {
        0x00031750: (
            "nrfx_rtc_2_irq_handler", "modules/nrfx/drivers/src/nrfx_rtc.c",
            "04220021014841f0f9b8",
        ),
        0x00033828: (
            "nrfx_timer_2_irq_handler", "modules/nrfx/drivers/src/nrfx_timer.c",
            "0422024902483ff0ddb8",
        ),
        0x0003383C: (
            "nrfx_timer_4_irq_handler", "modules/nrfx/drivers/src/nrfx_timer.c",
            "0622024902483ff0d3b8",
        ),
        0x0007294C: (
            "irq_handler", "modules/nrfx/drivers/src/nrfx_rtc.c",
            "2de9f0479146884604464ff480354ff4a0760027dff884a016e000bfd4f80403"
            "28420dd0a05958b1c4f84853c4f808533146204607f038fa5af82810f8b28847"
            "361d6d00b6b27f1c4f45e7d3d4f804034ff4807110f0010f09d0d4f8000130"
            "b1204607f021fa5af8281004208847d4f804034ff4827110f0020f0cd0d4f804"
            "01002808d0204607f00ffa5af82810bde8f04705200847bde8f087",
        ),
        0x000729EC: (
            "irq_handler", "modules/nrfx/drivers/src/nrfx_timer.c",
            "2de9f041174688460646002417e000bf4ff4a07000eb84054ff480307159a040"
            "59b1d6f80413014207d02946304607f0f7fdd8e9002128469047641ce4b2bc42"
            "e6d3bde8f081",
        ),
    }
    for entry, (symbol, source, body_hex) in rtc_timer_irq_expected.items():
        row = ownership_by_key[("application", f"0x{entry:08x}")]
        expected_body = bytes.fromhex(body_hex)
        offset = entry - recovered_base
        if row["provider_family"] != "nordic_nrf5_sdk_17_1_0" or \
                row["upstream_symbol"] != symbol or source not in row["evidence"] or \
                recovered[offset:offset + len(expected_body)] != expected_body:
            raise AssertionError(f"Nordic RTC/TIMER IRQ mismatch: 0x{entry:08x}")
    rtc_timer_driver_expected = {
        0x0007AD20: (
            "nrfx_rtc_enable", "modules/nrfx/drivers/src/nrfx_rtc.c",
            "10b5016801220a6040790b4a00eb40000221115416f0dafbc00703d116f0d6fb"
            "400705d505a205a14ff0406016f074fcbde8104016f0cabb",
        ),
        0x0007AE4C: (
            "nrfx_rtc_tick_enable", "modules/nrfx/drivers/src/nrfx_rtc.c",
            "70b50e4605464ff4807101240068fef7cbff2868c0f8444316b12868c0f80443"
            "16f03efbc00703d116f03afb400705d504a204a14ff0406016f0d8fbbde87040"
            "16f02ebb",
        ),
        0x0007B1C4: (
            "nrfx_timer_clear", "modules/nrfx/drivers/src/nrfx_timer.c",
            "00680121c1607047",
        ),
        0x0007B1CC: (
            "nrfx_timer_enable", "modules/nrfx/drivers/src/nrfx_timer.c",
            "10b5044600680121016021790c4a01eb410102eb81010220087216f081f9c007"
            "03d116f07df9400706d5237905a205a14ff0446016f01afabde8104016f070b9",
        ),
    }
    for entry, (symbol, source, body_hex) in rtc_timer_driver_expected.items():
        row = ownership_by_key[("application", f"0x{entry:08x}")]
        if row["provider_family"] != "nordic_nrf5_sdk_17_1_0" or \
                row["upstream_symbol"] != symbol or source not in row["evidence"] or \
                recovered_function(entry) != bytes.fromhex(body_hex):
            raise AssertionError(f"Nordic RTC/TIMER driver mismatch: 0x{entry:08x}")
    nfct_driver_expected = {
        0x0007AC14: (
            "nrfx_nfct_field_check", "modules/nrfx/drivers/src/nrfx_nfct.c",
            "02480068800700d001207047",
        ),
        0x0007AC24: (
            "nrfx_nfct_field_event_handler", "modules/nrfx/drivers/src/nrfx_nfct.c",
            "31b5214984b0087a002826d19df81000032807d1fff7ecff08b1022000e00120"
            "8df810009df8102000200125174c012a15d0022a11d1627a002a0ed148728872"
            "0d72114800f0acfa0f4800f0adfa65720220009014e06846884705b030bd617a"
            "0029fad00a4a0a49083215604ff48f62c1f80823607204200090012000f00af8"
            "61680029e7d1e8e7",
        ),
        0x0007ACB8: (
            "nrfx_nfct_frame_delay_max_set", "modules/nrfx/drivers/src/nrfx_nfct.c",
            "044908b1881403e00348c068c0f3130008607047",
        ),
    }
    for entry, (symbol, source, body_hex) in nfct_driver_expected.items():
        row = ownership_by_key[("application", f"0x{entry:08x}")]
        if row["provider_family"] != "nordic_nrf5_sdk_17_1_0" or \
                row["upstream_symbol"] != symbol or source not in row["evidence"] or \
                recovered_function(entry) != bytes.fromhex(body_hex):
            raise AssertionError(f"Nordic NFCT driver mismatch: 0x{entry:08x}")
    nfct_irq_row = ownership_by_key[("application", "0x0003060c")]
    nfct_irq_body = recovered_function(0x0003060C)
    if nfct_irq_row["provider_family"] != "nordic_nrf5_sdk_17_1_0" or \
            nfct_irq_row["upstream_symbol"] != "nrfx_nfct_irq_handler" or \
            "modules/nrfx/drivers/src/nrfx_nfct.c" not in nfct_irq_row["evidence"] or \
            len(nfct_irq_body) != 480 or \
            hashlib.sha256(nfct_irq_body).hexdigest() != \
            "0c2bdbaae27f8ad3a0b1fb489b737653a4574f0d2b39e5965c941c1ad4998b60":
        raise AssertionError("Nordic NFCT IRQ driver mismatch: 0x0003060c")
    fstorage_sd_api = (
        0x000710A1, 0x00093EC5, 0x00087B21, 0x00096FE1,
        0x0005D515, 0x000883F9, 0x00096E09, 0x00072B71,
    )
    api_offset = 0x0009C86C - recovered_base
    expected_api = b"".join(pointer.to_bytes(4, "little") for pointer in fstorage_sd_api)
    if recovered[api_offset:api_offset + len(expected_api)] != expected_api:
        raise AssertionError("recovered nrf_fstorage_sd API table changed")
    fstorage_leaf_prefixes = {
        0x00072B70: bytes.fromhex("0248007a002800d001207047"),
        0x00078C80: bytes.fromhex(
            "2de9f04128b1016819b1c969bde8f04108470d4d0d480024461b14270de000bf"
            "04eb840005eb8000016829b1c969884710b10120bde8f081641cb6fbf7f0a042"
            "eed80020f6e7"
        ),
        0x00078CD0: bytes.fromhex("044801214174007a08b10020704701207047"),
        0x00078CE8: bytes.fromhex("012801d0032808d10449002201284a7400d0002008740ef00fbc7047"),
        0x00087B20: bytes.fromhex("10b510461a469ff719fe002010bd"),
        0x000883F8: bytes.fromhex("08467047"),
        0x00096E08: bytes.fromhex("00207047"),
    }
    for address, prefix in fstorage_leaf_prefixes.items():
        offset = address - recovered_base
        if recovered[offset:offset + len(prefix)] != prefix:
            raise AssertionError(f"recovered fstorage function bytes changed: {address:#010x}")
    sdh_core_prefixes = {
        0x00079E58: bytes.fromhex("20b1034909680160002070470e207047"),
        0x0007A38C: bytes.fromhex(
            "30b51548adf5017d0078002821d04ff4fa7500bfadf8005280a9684661df38b1"
            "052816d00df5017dbde83040d4f700b96c460a497da800f0bbf806e0d0e90021"
            "204690477da800f0caf87f980028e1d0f4e70df5017d30bd"
        ),
        0x0007A3EC: bytes.fromhex("f8b5134c2078c0b10120a0700ef0a6fe112814d0"),
        0x0007A440: bytes.fromhex("7cb5194c207808b108207cbd0120a07000200ef0"),
        0x0007A4B4: bytes.fromhex(
            "0eb50749684600f03ff805e0d0e900108847684600f04ff802980028f6d10ebd"
        ),
        0x0007A4D8: bytes.fromhex("014800787047"),
        0x0007A4E4: bytes.fromhex("0548817819b1007818b1fff77dbf08207047fff7a3bf"),
        0x0007A500: bytes.fromhex(
            "1fb568464bdf30b1052814d004b0bde81040d4f753b8084901a800f00ff806e0"
            "d0e900210098904701a800f01ef803980028e6d0f4e71fbd"
        ),
        0x0007A53C: bytes.fromhex("016009684160aff30080"),
        0x0007A56A: bytes.fromhex("816800290bd0026892680a4482604168"),
        0x00089148: bytes.fromhex("3eb5044609496846f1f7f4f908e000bf"),
        0x00089178: bytes.fromhex("3eb5044608496846f1f7dcf907e000bf"),
    }
    for address, prefix in sdh_core_prefixes.items():
        offset = address - recovered_base
        if recovered[offset:offset + len(prefix)] != prefix:
            raise AssertionError(f"recovered SoftDevice handler bytes changed: {address:#010x}")
    for entry in (
        "0x00048a28", "0x0004df18", "0x0004e4b4", "0x0004e66c",
        "0x000529bc", "0x000539b8", "0x00066c4c", "0x00095bb8",
        "0x00095bd0", "0x00095bfc",
    ):
        row = ownership_by_key[("application", entry)]
        if row["provider_family"] != "r1_provider_configuration_glue" or \
                row["source_disposition"] != \
                "clean_room_configuration_only_use_pinned_provider":
            raise AssertionError(f"Nordic configuration glue not source-admitted: {entry}")
    freertos_static_summary = summarize_freertos_static_memory(
        ROOT / "research" / "decompilation" / "rebuild" /
        "rebuilt-application.bin"
    )
    if freertos_static_summary["function_count"] != 2 or \
            freertos_static_summary["function_bytes"] != 36 or \
            freertos_static_summary["recovered_layout"] != {
                "static_task_control_block_bytes": 112,
                "stack_words": 256,
                "stack_word_bytes": 4,
                "stack_bytes": 1024,
                "allocation_bytes_per_task": 1136,
                "idle_buffer": "0x2002b4d0",
                "idle_stack": "0x2002b540",
                "timer_buffer": "0x2002b940",
                "timer_stack": "0x2002b9b0",
            } or freertos_static_summary["source_lineage"][
                "local_implementation_authorized"
            ] is not True or freertos_static_summary["source_lineage"][
                "provider_implementation_authorized"
            ] is not False:
        raise AssertionError("FreeRTOS static-memory configuration census changed")
    for function in FREERTOS_STATIC_MEMORY_FUNCTIONS:
        entry = int(function["entry"])
        row = ownership_by_key[("application", f"0x{entry:08x}")]
        body = recovered[entry - recovered_base:
                         int(function["end_exclusive"]) - recovered_base]
        if row["provider_family"] != "r1_provider_configuration_glue" or \
                row["source_disposition"] != \
                "clean_room_configuration_only_use_pinned_provider" or \
                row["upstream_symbol"] != function["symbol"] or \
                row["confidence"] != "high" or \
                int(row["size"]) != function["size"] or \
                hashlib.sha256(body).hexdigest() != function["sha256"]:
            raise AssertionError(
                f"FreeRTOS static-memory configuration changed: 0x{entry:08x}"
            )
    freertos_stack_summary = summarize_freertos_stack_overflow(
        ROOT / "research" / "decompilation" / "rebuild" /
        "rebuilt-application.bin"
    )
    if freertos_stack_summary["function_count"] != 1 or \
            freertos_stack_summary["function_bytes"] != 72 or \
            freertos_stack_summary["recovered_configuration"] != {
                "configCHECK_FOR_STACK_OVERFLOW": 2,
                "sentinel_word": "0xa5a5a5a5",
                "sentinel_words_checked": 4,
            } or freertos_stack_summary["source_lineage"][
                "local_callback_authorized"
            ] is not True or freertos_stack_summary["source_lineage"][
                "provider_implementation_authorized"
            ] is not False:
        raise AssertionError("FreeRTOS stack-overflow configuration census changed")
    for function in FREERTOS_STACK_OVERFLOW_FUNCTIONS:
        entry = int(function["entry"])
        row = ownership_by_key[("application", f"0x{entry:08x}")]
        body = recovered[entry - recovered_base:
                         int(function["end_exclusive"]) - recovered_base]
        if row["provider_family"] != "r1_provider_configuration_glue" or \
                row["source_disposition"] != \
                "clean_room_configuration_only_use_pinned_provider" or \
                row["upstream_symbol"] != function["symbol"] or \
                row["confidence"] != "high" or \
                int(row["size"]) != function["size"] or \
                hashlib.sha256(body).hexdigest() != function["sha256"]:
            raise AssertionError(
                f"FreeRTOS stack-overflow callback changed: 0x{entry:08x}"
            )
    nordic_system_summary = summarize_nordic_system_init(
        ROOT / "research" / "decompilation" / "rebuild" /
        "rebuilt-application.bin"
    )
    if nordic_system_summary["function_count"] != 2 or \
            nordic_system_summary["function_bytes"] != 544 or \
            nordic_system_summary["recovered_configuration"] != {
                "device": "NRF52840_XXAA",
                "hard_float": True,
                "CONFIG_NFCT_PINS_AS_GPIOS": True,
                "CONFIG_GPIO_AS_PINRESET": True,
                "reset_pin": 18,
                "system_core_clock_hz": 64000000,
            } or nordic_system_summary["provider"][
                "local_reimplementation_authorized"
            ] is not False:
        raise AssertionError("Nordic SystemInit provider census changed")
    for function in NORDIC_SYSTEM_INIT_FUNCTIONS:
        entry = int(function["entry"])
        row = ownership_by_key[("application", f"0x{entry:08x}")]
        body = recovered[entry - recovered_base:
                         int(function["end_exclusive"]) - recovered_base]
        if row["provider_family"] != "nordic_nrf5_sdk_17_1_0" or \
                row["source_disposition"] != "use_nordic_sdk" or \
                row["upstream_symbol"] != function["symbol"] or \
                row["confidence"] != "high" or \
                int(row["size"]) != function["size"] or \
                hashlib.sha256(body).hexdigest() != function["sha256"]:
            raise AssertionError(
                f"Nordic SystemInit provider boundary changed: 0x{entry:08x}"
            )
    nordic_twim_summary = summarize_nordic_twim_completeness(
        ROOT / "research" / "decompilation" / "rebuild" /
        "rebuilt-application.bin"
    )
    if nordic_twim_summary["function_count"] != 1 or \
            nordic_twim_summary["function_bytes"] != 98 or \
            nordic_twim_summary["semantics"]["reset_sequence"] != [
                "ENABLE=0", "ENABLE=6"
            ] or nordic_twim_summary["provider"][
                "local_reimplementation_authorized"
            ] is not False:
        raise AssertionError("Nordic TWIM completeness census changed")
    for function in NORDIC_TWIM_COMPLETENESS_FUNCTIONS:
        entry = int(function["entry"])
        row = ownership_by_key[("application", f"0x{entry:08x}")]
        body = recovered[entry - recovered_base:
                         int(function["end_exclusive"]) - recovered_base]
        if row["provider_family"] != "nordic_nrf5_sdk_17_1_0" or \
                row["source_disposition"] != "use_nordic_sdk" or \
                row["upstream_symbol"] != function["symbol"] or \
                row["confidence"] != "high" or \
                int(row["size"]) != function["size"] or \
                hashlib.sha256(body).hexdigest() != function["sha256"]:
            raise AssertionError(
                f"Nordic TWIM completeness boundary changed: 0x{entry:08x}"
            )
    gatt_cache_summary = summarize_nordic_gatt_cache_closure(
        ROOT / "research/decompilation/rebuild/rebuilt-application.bin")
    if gatt_cache_summary["function_count"] != 10 or gatt_cache_summary["function_bytes"] != 784:
        raise AssertionError("Nordic GATT-cache closure census changed")
    for function in NORDIC_GATT_CACHE_CLOSURE_FUNCTIONS:
        entry = int(function["entry"])
        row = ownership_by_key[("application", f"0x{entry:08x}")]
        body = recovered[entry - recovered_base:int(function["end_exclusive"]) - recovered_base]
        if row["provider_family"] != "nordic_nrf5_sdk_17_1_0" or \
                row["upstream_symbol"] != function["symbol"] or \
                hashlib.sha256(body).hexdigest() != function["sha256"]:
            raise AssertionError(f"Nordic GATT-cache closure changed: 0x{entry:08x}")
    freertos_version_summary = summarize_freertos_kernel_version(
        ROOT / "research/decompilation/rebuild/rebuilt-application.bin")
    if freertos_version_summary["function_count"] != 1 or \
            freertos_version_summary["function_bytes"] != 40:
        raise AssertionError("FreeRTOS version-discriminator census changed")
    resolved_thunk_summary = summarize_resolved_thunks(
        ROOT / "research/decompilation/rebuild/rebuilt-application.bin")
    if resolved_thunk_summary["function_count"] != 8 or \
            resolved_thunk_summary["function_bytes"] != 32 or \
            resolved_thunk_summary["local_reimplementation_required"] is not False:
        raise AssertionError("resolved branch-thunk census changed")
    for function in RESOLVED_THUNKS:
        entry = int(function["entry"])
        row = ownership_by_key[("application", f"0x{entry:08x}")]
        body = recovered[entry - recovered_base:entry - recovered_base + int(function["size"])]
        expected_thunk_family = function["provider"]
        if entry in goodix_democode_symbols:
            expected_thunk_family = "goodix_gh3x2x_democode_v1_6_drvlib_v4_3_0_0"
        if row["provider_family"] != expected_thunk_family or \
                row["confidence"] != "high" or \
                hashlib.sha256(body).hexdigest() != function["sha256"]:
            raise AssertionError(f"resolved branch thunk changed: 0x{entry:08x}")
    advertising_summary = summarize_nordic_advertising_closure(
        ROOT / "research/decompilation/rebuild/rebuilt-application.bin")
    if advertising_summary["function_count"] != 8 or \
            advertising_summary["function_bytes"] != 992 or \
            advertising_summary["extent_bytes"] != 998 or \
            advertising_summary["provider"][
                "local_reimplementation_authorized"
            ] is not False:
        raise AssertionError("Nordic BLE advertising closure census changed")
    for function in NORDIC_ADVERTISING_FUNCTIONS:
        entry = int(function["entry"])
        end = int(function["end_exclusive"])
        row = ownership_by_key[("application", f"0x{entry:08x}")]
        extent = recovered[entry - recovered_base:end - recovered_base]
        if "inline_data" in function:
            inline = function["inline_data"]
            inline_entry = int(inline["entry"])
            inline_end = int(inline["end_exclusive"])
            body = (recovered[entry - recovered_base:
                              inline_entry - recovered_base] +
                    recovered[inline_end - recovered_base:
                              end - recovered_base])
            body_digest = hashlib.sha256(body).hexdigest()
            expected_digest = function["body_sha256"]
        else:
            body_digest = hashlib.sha256(extent).hexdigest()
            expected_digest = function["extent_sha256"]
        if row["provider_family"] != "nordic_nrf5_sdk_17_1_0" or \
                row["source_disposition"] != "use_nordic_sdk" or \
                row["upstream_symbol"] != function["symbol"] or \
                function["source"] not in row["evidence"] or \
                row["confidence"] != "high" or \
                int(row["size"]) != function["size"] or \
                len(extent) != function["extent_size"] or \
                hashlib.sha256(extent).hexdigest() != \
                function["extent_sha256"] or body_digest != expected_digest:
            raise AssertionError(
                f"Nordic BLE advertising closure changed: 0x{entry:08x}"
            )
    buttonless_dfu_summary = summarize_nordic_buttonless_dfu_closure(
        ROOT / "research/decompilation/rebuild/rebuilt-application.bin")
    if buttonless_dfu_summary["function_count"] != 10 or \
            buttonless_dfu_summary["function_bytes"] != 958 or \
            buttonless_dfu_summary["ghidra_function_count"] != 9 or \
            buttonless_dfu_summary["ghidra_function_bytes"] != 830 or \
            buttonless_dfu_summary["manual_supplement_count"] != 1 or \
            buttonless_dfu_summary["provider"]["variant"] != \
            "NRF_DFU_BLE_BUTTONLESS_SUPPORTS_BONDS=0" or \
            buttonless_dfu_summary["provider"][
                "local_reimplementation_authorized"
            ] is not False:
        raise AssertionError("Nordic buttonless-DFU closure census changed")
    for function in NORDIC_BUTTONLESS_DFU_FUNCTIONS:
        entry = int(function["entry"])
        row = ownership_by_key[("application", f"0x{entry:08x}")]
        body = b"".join(
            recovered[int(start) - recovered_base:int(end) - recovered_base]
            for start, end in function["segments"]
        )
        expected_inventory = function.get(
            "inventory", "ghidra_functions_csv"
        )
        if row["provider_family"] != "nordic_nrf5_sdk_17_1_0" or \
                row["source_disposition"] != "use_nordic_sdk" or \
                row["upstream_symbol"] != function["symbol"] or \
                function["source"] not in row["evidence"] or \
                row["confidence"] != "high" or \
                row["inventory_source"] != expected_inventory or \
                int(row["size"]) != function["size"] or \
                len(body) != function["size"] or \
                hashlib.sha256(body).hexdigest() != function["sha256"]:
            raise AssertionError(
                f"Nordic buttonless-DFU closure changed: 0x{entry:08x}"
            )
    power_mgmt_summary = summarize_nordic_power_management_closure(
        ROOT / "research/decompilation/rebuild/rebuilt-application.bin")
    if power_mgmt_summary["function_count"] != 2 or \
            power_mgmt_summary["function_bytes"] != 332 or \
            power_mgmt_summary["configuration"] != {
                "NRF_PWR_MGMT_CONFIG_USE_SCHEDULER": 0,
                "SOFTDEVICE_PRESENT": True,
                "shutdown_continue_value": 4,
                "prepare_dfu_value": 2,
                "prepare_reset_value": 3,
            } or power_mgmt_summary["provider"][
                "local_reimplementation_authorized"
            ] is not False:
        raise AssertionError("Nordic power-management closure census changed")
    for function in NORDIC_POWER_MANAGEMENT_FUNCTIONS:
        entry = int(function["entry"])
        end = int(function["end_exclusive"])
        row = ownership_by_key[("application", f"0x{entry:08x}")]
        body = recovered[entry - recovered_base:end - recovered_base]
        if row["provider_family"] != "nordic_nrf5_sdk_17_1_0" or \
                row["source_disposition"] != "use_nordic_sdk" or \
                row["upstream_symbol"] != function["symbol"] or \
                "components/libraries/pwr_mgmt/nrf_pwr_mgmt.c" not in \
                row["evidence"] or row["confidence"] != "high" or \
                int(row["size"]) != function["size"] or \
                hashlib.sha256(body).hexdigest() != function["sha256"]:
            raise AssertionError(
                f"Nordic power-management closure changed: 0x{entry:08x}"
            )
    reset_trace_summary = summarize_r1_reset_trace_closure(
        ROOT / "research/decompilation/rebuild/rebuilt-application.bin")
    if reset_trace_summary["function_count"] != 12 or \
            reset_trace_summary["function_bytes"] != 598 or \
            reset_trace_summary["record"] != {
                "bytes": 16,
                "crc_input_bytes": 14,
                "crc": "Modbus CRC16",
                "field_bytes": 13,
                "persist_tag_index": 0,
                "reboot_caller_index": 1,
                "return_address_indices": [2, 3, 4, 5],
                "program_counter_indices": [6, 7, 8, 9],
                "fault_tag": 7,
            } or reset_trace_summary["source_boundary"] != {
                "provider_family": "r1_product_specific",
                "source_disposition": "clean_room_behavior_only",
                "reset_provider": "Nordic SDK 17.1.0 CMSIS NVIC_SystemReset",
            }:
        raise AssertionError("R1 reset-trace closure census changed")
    for function in R1_RESET_TRACE_FUNCTIONS:
        entry = int(function["entry"])
        row = ownership_by_key[("application", f"0x{entry:08x}")]
        body = reset_trace_function_bytes(recovered, function)
        is_reset_adapter = entry == 0x0007A5E0
        expected_family = (
            "r1_nordic_cmsis_provider_adapter" if is_reset_adapter
            else "r1_product_specific"
        )
        expected_disposition = (
            "clean_room_adapter_only_use_nordic_sdk_and_cmsis"
            if is_reset_adapter else "clean_room_behavior_only"
        )
        if row["provider_family"] != expected_family or \
                row["source_disposition"] != expected_disposition or \
                row["upstream_symbol"] != function["symbol"] and \
                not (is_reset_adapter and row["upstream_symbol"].startswith(
                    function["symbol"])) or \
                row["confidence"] != "high" or \
                int(row["size"]) != function["size"] or \
                len(body) != function["size"] or \
                hashlib.sha256(body).hexdigest() != function["sha256"]:
            raise AssertionError(
                f"R1 reset-trace closure changed: 0x{entry:08x}"
            )
    reset_reason_summary = summarize_r1_reset_reason_closure(
        ROOT / "research/decompilation/rebuild/rebuilt-application.bin")
    if reset_reason_summary["function_count"] != 2 or \
            reset_reason_summary["function_bytes"] != 834 or \
            reset_reason_summary["resetreas"]["register"] != "0x40000400" or \
            reset_reason_summary["resetreas"]["recognized_mask"] != \
            "0x0007000f" or \
            reset_reason_summary["resetreas"]["clear_policy"] != \
            "write_raw_mask_back_after_decode" or \
            reset_reason_summary["software_reset_trace"][
                "reboot_caller_only_when_persist_tag"] != 2:
        raise AssertionError("R1 reset-reason closure census changed")
    for function in R1_RESET_REASON_FUNCTIONS:
        entry = int(function["entry"])
        row = ownership_by_key[("application", f"0x{entry:08x}")]
        body = b"".join(
            recovered[int(start) - recovered_base:int(end) - recovered_base]
            for start, end in function["extents"]
        )
        is_nordic_adapter = entry == 0x00077E98
        expected_family = (
            "r1_nordic_sdk_provider_adapter" if is_nordic_adapter
            else "r1_product_specific"
        )
        expected_disposition = (
            "clean_room_adapter_only_use_nordic_sdk" if is_nordic_adapter
            else "clean_room_behavior_only"
        )
        if row["provider_family"] != expected_family or \
                row["source_disposition"] != expected_disposition or \
                row["upstream_symbol"] != function["symbol"] or \
                row["confidence"] != "high" or \
                int(row["size"]) != function["size"] or \
                len(body) != function["size"] or \
                hashlib.sha256(body).hexdigest() != function["sha256"]:
            raise AssertionError(
                f"R1 reset-reason closure changed: 0x{entry:08x}"
            )
    connection_control_summary = summarize_r1_connection_control(
        ROOT / "research/decompilation/rebuild/rebuilt-application.bin",
        recovered_base,
    )
    connection_closure = connection_control_summary["ownership_closure"]
    if connection_closure["function_count"] != 1 or \
            connection_closure["function_bytes"] != 1736 or \
            connection_closure["extent_bytes"] != 2450 or \
            connection_control_summary["pair_auth"][
                "consumer_requests_peer_manager_security_when_not_encrypted"] \
                is not True or \
            connection_control_summary["advertise_start"]["event_type"] != 0x200 or \
            connection_control_summary["source_boundary"][
                "unclassified_callees_absorbed"] is not False:
        raise AssertionError("R1 connection-control ownership closure changed")
    for function in R1_CONNECTION_CONTROL_FUNCTIONS:
        entry = int(function["entry"])
        end = int(function["end_exclusive"])
        row = ownership_by_key[("application", f"0x{entry:08x}")]
        extent = recovered[entry - recovered_base:end - recovered_base]
        if row["provider_family"] != "r1_product_specific" or \
                row["source_disposition"] != "clean_room_behavior_only" or \
                row["upstream_symbol"] != function["symbol"] or \
                row["confidence"] != "high" or \
                int(row["size"]) != function["size"] or \
                len(extent) != function["extent_bytes"] or \
                hashlib.sha256(extent).hexdigest() != function["sha256"]:
            raise AssertionError(
                f"R1 connection-control closure changed: 0x{entry:08x}"
            )
    peer_event_summary = summarize_r1_peer_manager_event_policy(
        ROOT / "research/decompilation/rebuild/rebuilt-application.bin"
    )
    if peer_event_summary["function_count"] != 1 or \
            peer_event_summary["function_bytes"] != 1052 or \
            peer_event_summary["registration"]["callback_pointer"] != \
            "0x0007f2b1" or \
            peer_event_summary["providers"]["standard_event_handler"] != \
            "pm_handler_on_pm_evt" or \
            peer_event_summary["providers"]["flash_clean_handler"] != \
            "pm_handler_flash_clean" or \
            peer_event_summary["security"]["allow_repairing"] is not True or \
            peer_event_summary["security"][
                "new_bond_whitelist_mutation_recovered"
            ] is not False or \
            peer_event_summary["security"]["recovered_ltk_logging_admitted"] \
            is not False:
        raise AssertionError("R1 Peer Manager event-policy closure changed")
    for function in R1_PEER_MANAGER_EVENT_FUNCTIONS:
        entry = int(function["entry"])
        row = ownership_by_key[("application", f"0x{entry:08x}")]
        body = b"".join(
            recovered[start - recovered_base:end - recovered_base]
            for start, end in function["segments"]
        )
        if row["provider_family"] != "r1_product_specific" or \
                row["source_disposition"] != "clean_room_behavior_only" or \
                row["upstream_symbol"] != function["symbol"] or \
                row["confidence"] != "high" or \
                int(row["size"]) != function["size"] or \
                len(body) != function["size"] or \
                hashlib.sha256(body).hexdigest() != function["sha256"]:
            raise AssertionError(
                f"R1 Peer Manager event-policy boundary changed: 0x{entry:08x}"
            )
    nv_recovery_summary = summarize_r1_nv_recovery_closure(
        ROOT / "research/decompilation/rebuild/rebuilt-application.bin"
    )
    if nv_recovery_summary["function_count"] != 4 or \
            nv_recovery_summary["function_bytes"] != 1740 or \
            nv_recovery_summary["ghidra_function_count"] != 2 or \
            nv_recovery_summary["ghidra_function_bytes"] != 1458 or \
            nv_recovery_summary["manual_supplement_count"] != 2 or \
            nv_recovery_summary["manual_supplement_bytes"] != 282 or \
            nv_recovery_summary["protocol"]["command"] != 2 or \
            nv_recovery_summary["protocol"]["body_bytes"] != 116 or \
            nv_recovery_summary["protocol"]["checksum"] != "CRC-16/MODBUS" or \
            nv_recovery_summary["security"]["normal_ble_command_enabled"] \
            is not False or \
            nv_recovery_summary["security"]["transport_sender_implemented"] \
            is not False or \
            nv_recovery_summary["security"][
                "persistent_commit_implemented_by_planner"
            ] is not False or \
            nv_recovery_summary["security"]["identity_logging_allowed"] \
            is not False:
        raise AssertionError("R1 NV-recovery closure metadata changed")
    for function in R1_NV_RECOVERY_FUNCTIONS:
        entry = int(function["entry"])
        row = ownership_by_key[("application", f"0x{entry:08x}")]
        body = b"".join(
            recovered[start - recovered_base:end - recovered_base]
            for start, end in function["segments"]
        )
        expected_inventory = (
            "manual_provenance_supplement"
            if function["inventory"] == "manual_provenance_supplement"
            else "ghidra_functions_csv"
        )
        if row["provider_family"] != "r1_product_specific" or \
                row["source_disposition"] != \
                "clean_room_behavior_only_security_preserving" or \
                row["upstream_symbol"] != function["symbol"] or \
                row["confidence"] != "high" or \
                row["inventory_source"] != expected_inventory or \
                int(row["size"]) != function["size"] or \
                len(body) != function["size"] or \
                hashlib.sha256(body).hexdigest() != function["sha256"]:
            raise AssertionError(
                f"R1 NV-recovery closure changed: 0x{entry:08x}"
            )
    nv_compiled_restore_summary = summarize_r1_nv_compiled_restore(
        ROOT / "research/decompilation/rebuild/rebuilt-application.bin"
    )
    if nv_compiled_restore_summary["function_count"] != 1 or \
            nv_compiled_restore_summary["function_bytes"] != 494 or \
            nv_compiled_restore_summary["event_route"]["internal_storage_event"] != \
            "0x2005" or \
            nv_compiled_restore_summary["event_route"]["ble_command"] is not False or \
            nv_compiled_restore_summary["restore_table"]["record_count"] != 59 or \
            nv_compiled_restore_summary["restore_table"]["record_bytes"] != 14 or \
            nv_compiled_restore_summary["restore_table"]["raw_identity_rows_emitted"] \
            is not False or \
            nv_compiled_restore_summary["behavior"]["commits_persistent_records"] \
            is not True or \
            nv_compiled_restore_summary["security"]["live_persistent_restore_enabled"] \
            is not False or \
            nv_compiled_restore_summary["security"]["identity_logging_enabled"] \
            is not False:
        raise AssertionError("R1 compiled-default restore metadata changed")
    for function in R1_NV_COMPILED_RESTORE_FUNCTIONS:
        entry = int(function["entry"])
        end = int(function["end_exclusive"])
        row = ownership_by_key[("application", f"0x{entry:08x}")]
        body = recovered[entry - recovered_base:end - recovered_base]
        if row["provider_family"] != "r1_product_specific" or \
                row["source_disposition"] != \
                "clean_room_behavior_only_security_preserving" or \
                row["upstream_symbol"] != function["symbol"] or \
                row["confidence"] != "high" or \
                int(row["size"]) != function["size"] or \
                len(body) != function["size"] or \
                hashlib.sha256(body).hexdigest() != function["sha256"]:
            raise AssertionError(
                f"R1 compiled-default restore changed: 0x{entry:08x}"
            )
    touch_slider_summary = summarize_r1_touch_slider_closure(
        ROOT / "research/decompilation/rebuild/rebuilt-application.bin"
    )
    if touch_slider_summary["function_count"] != 13 or \
            touch_slider_summary["function_bytes"] != 2784 or \
            touch_slider_summary["ghidra_function_count"] != 12 or \
            touch_slider_summary["ghidra_function_bytes"] != 2776 or \
            touch_slider_summary["manual_supplement_count"] != 1 or \
            touch_slider_summary["identity"]["callback_pointer"] != \
            "0x00092cbd" or \
            touch_slider_summary["identity"]["slider_state_machine"] != \
            "0x00092cbc" or \
            touch_slider_summary["initial_configuration"][
                "long_press_threshold_raw"
            ] != 1000 or \
            touch_slider_summary["events"]["0x80"] != "press timeout/error" or \
            touch_slider_summary["ownership"]["provider_family"] != \
            "r1_product_specific" or \
            touch_slider_summary["ownership"]["vendor_algorithm_included"] \
            is not False:
        raise AssertionError("R1 touch-slider closure metadata changed")
    for function in R1_TOUCH_SLIDER_FUNCTIONS:
        entry = int(function["entry"])
        row = ownership_by_key[("application", f"0x{entry:08x}")]
        body = b"".join(
            recovered[start - recovered_base:end - recovered_base]
            for start, end in function["segments"]
        )
        expected_inventory = (
            "manual_provenance_supplement"
            if function["inventory"] == "manual_provenance_supplement"
            else "ghidra_functions_csv"
        )
        if row["provider_family"] != "r1_product_specific" or \
                row["source_disposition"] != "clean_room_behavior_only" or \
                row["upstream_symbol"] != function["symbol"] or \
                row["confidence"] != "high" or \
                row["inventory_source"] != expected_inventory or \
                int(row["size"]) != function["size"] or \
                len(body) != function["size"] or \
                hashlib.sha256(body).hexdigest() != function["sha256"]:
            raise AssertionError(
                f"R1 touch-slider closure changed: 0x{entry:08x}"
            )
    health_daily_test_summary = summarize_r1_health_daily_test(
        ROOT / "research/decompilation/rebuild/rebuilt-application.bin"
    )
    if health_daily_test_summary["function_count"] != 1 or \
            health_daily_test_summary["function_bytes"] != 1344 or \
            health_daily_test_summary["direct_callers"] != [] or \
            health_daily_test_summary["behavior"]["maximum_hours"] != 24 or \
            health_daily_test_summary["behavior"][
                "production_reachability_proven"
            ] is not False:
        raise AssertionError("R1 health-daily test fixture metadata changed")
    for function in R1_HEALTH_DAILY_TEST_FUNCTIONS:
        entry = int(function["entry"])
        row = ownership_by_key[("application", f"0x{entry:08x}")]
        body = b"".join(
            recovered[start - recovered_base:end - recovered_base]
            for start, end in function["segments"]
        )
        if row["provider_family"] != "r1_product_specific" or \
                row["source_disposition"] != "clean_room_behavior_only" or \
                row["upstream_symbol"] != function["symbol"] or \
                len(body) != function["size"] or \
                hashlib.sha256(body).hexdigest() != function["sha256"]:
            raise AssertionError("R1 health-daily test fixture changed")
    gomore_neural_runtime_summary = summarize_r1_gomore_neural_runtime(
        ROOT / "research/decompilation/rebuild/rebuilt-application.bin"
    )
    if gomore_neural_runtime_summary["function_count"] != 1 or \
            gomore_neural_runtime_summary["function_bytes"] != 1234 or \
            gomore_neural_runtime_summary["indirect_dispatch"][
                "thumb_pointer"
            ] != "0x00076bdd" or \
            len(gomore_neural_runtime_summary["indirect_dispatch"][
                "constructor_callsites"
            ]) != 16 or \
            gomore_neural_runtime_summary["behavioral_census"][
                "specialized_kernel_widths"
            ] != [1, 3, 5] or \
            gomore_neural_runtime_summary["ownership"][
                "local_reimplementation_permitted"
            ] is not False:
        raise AssertionError("GoMore neural runtime metadata changed")
    for function in GOMORE_NEURAL_RUNTIME_FUNCTIONS:
        entry = int(function["entry"])
        end = int(function["end_exclusive"])
        row = ownership_by_key[("application", f"0x{entry:08x}")]
        body = recovered[entry - recovered_base:end - recovered_base]
        if row["provider_family"] != "gomore_health_algorithm_candidate" or \
                row["source_disposition"] != \
                "vendor_source_required_not_redistributable" or \
                row["confidence"] != "candidate" or \
                int(row["size"]) != function["size"] or \
                len(body) != function["size"] or \
                hashlib.sha256(body).hexdigest() != function["sha256"]:
            raise AssertionError("GoMore neural runtime ownership changed")
    gomore_sleep_graph_summary = summarize_r1_gomore_sleep_graphs(
        ROOT / "research/decompilation/rebuild/rebuilt-application.bin"
    )
    if gomore_sleep_graph_summary["function_count"] != 6 or \
            gomore_sleep_graph_summary["function_bytes"] != 2188 or \
            gomore_sleep_graph_summary["constructor_table"]["address"] != \
            "0x000bcf40" or \
            gomore_sleep_graph_summary["constructor_table"]["thumb_pointers"] != [
                "0x00072be1", "0x00048d23", "0x00028b8b"
            ] or \
            gomore_sleep_graph_summary["classifier_models"][
                "modes_below_100"
            ]["bytes"] != 21824 or \
            gomore_sleep_graph_summary["classifier_models"][
                "modes_at_least_100"
            ]["bytes"] != 21824 or \
            gomore_sleep_graph_summary["boundary"]["provider_family"] != \
            "gomore_health_algorithm_candidate" or \
            gomore_sleep_graph_summary["boundary"]["source_disposition"] != \
            "vendor_source_required_not_redistributable" or \
            gomore_sleep_graph_summary["boundary"][
                "local_graph_or_model_reimplementation_authorized"
            ] is not False or \
            gomore_sleep_graph_summary["boundary"][
                "goodix_graph_0x0004387c_included"
            ] is not False:
        raise AssertionError("GoMore sleep graph boundary metadata changed")
    for function in GOMORE_SLEEP_GRAPH_FUNCTIONS:
        entry = int(function["entry"])
        row = ownership_by_key[("application", f"0x{entry:08x}")]
        body = b"".join(
            recovered[start - recovered_base:end - recovered_base]
            for start, end in function["segments"]
        )
        if row["provider_family"] != "gomore_health_algorithm_candidate" or \
                row["source_disposition"] != \
                "vendor_source_required_not_redistributable" or \
                row["confidence"] != "candidate" or \
                int(row["size"]) != function["size"] or \
                len(body) != function["size"] or \
                hashlib.sha256(body).hexdigest() != function["sha256"]:
            raise AssertionError(
                f"GoMore sleep graph boundary changed: 0x{entry:08x}"
            )
    gomore_activity_state_summary = summarize_r1_gomore_activity_state_classifier(
        ROOT / "research/decompilation/rebuild/rebuilt-application.bin"
    )
    if gomore_activity_state_summary["function_count"] != 6 or \
            gomore_activity_state_summary["function_bytes"] != 1890 or \
            gomore_activity_state_summary["state_machine"]["state_count"] != 7 or \
            gomore_activity_state_summary["state_machine"]["window_samples"] != 25 or \
            gomore_activity_state_summary["state_machine"]["decision_samples"] != 250 or \
            len(gomore_activity_state_summary["state_machine"]["jump_tables"]) != 3 or \
            gomore_activity_state_summary["boundary"]["provider_family"] != \
            "gomore_health_algorithm_candidate" or \
            gomore_activity_state_summary["boundary"]["source_disposition"] != \
            "vendor_source_required_not_redistributable" or \
            gomore_activity_state_summary["boundary"][
                "local_classifier_reimplementation_authorized"
            ] is not False or \
            gomore_activity_state_summary["boundary"][
                "shared_toolchain_math_included"
            ] is not False:
        raise AssertionError("GoMore activity-state classifier metadata changed")
    for function in GOMORE_ACTIVITY_STATE_FUNCTIONS:
        entry = int(function["entry"])
        row = ownership_by_key[("application", f"0x{entry:08x}")]
        body = b"".join(
            recovered[start - recovered_base:end - recovered_base]
            for start, end in function["segments"]
        )
        if row["provider_family"] != "gomore_health_algorithm_candidate" or \
                row["source_disposition"] != \
                "vendor_source_required_not_redistributable" or \
                row["confidence"] != "candidate" or \
                int(row["size"]) != function["size"] or \
                len(body) != function["size"] or \
                hashlib.sha256(body).hexdigest() != function["sha256"]:
            raise AssertionError(
                f"GoMore activity-state classifier changed: 0x{entry:08x}"
            )
    gomore_energy_model_summary = summarize_r1_gomore_energy_model(
        ROOT / "research/decompilation/rebuild/rebuilt-application.bin"
    )
    if gomore_energy_model_summary["function_count"] != 9 or \
            gomore_energy_model_summary["function_bytes"] != 2360 or \
            gomore_energy_model_summary["identity"][
                "existing_energy_output_producer"] != "0x0005f56c" or \
            gomore_energy_model_summary["identity"]["dispatcher"] != \
            "0x0002f488" or \
            gomore_energy_model_summary["identity"]["largest_estimator"] != \
            "0x0007da30" or \
            gomore_energy_model_summary["closure"][
                "outside_caller_exclusivity"] is not True or \
            gomore_energy_model_summary["boundary"]["provider_family"] != \
            "gomore_health_algorithm_candidate" or \
            gomore_energy_model_summary["boundary"]["source_disposition"] != \
            "vendor_source_required_not_redistributable" or \
            gomore_energy_model_summary["boundary"][
                "local_algorithm_reimplementation_authorized"] is not False:
        raise AssertionError("GoMore energy-model boundary metadata changed")
    for function in GOMORE_ENERGY_MODEL_FUNCTIONS:
        entry = int(function["entry"])
        row = ownership_by_key[("application", f"0x{entry:08x}")]
        segments = function["segments"] or (
            (entry, int(function["end_exclusive"])),
        )
        body = b"".join(
            recovered[start - recovered_base:end - recovered_base]
            for start, end in segments
        )
        if row["provider_family"] != "gomore_health_algorithm_candidate" or \
                row["source_disposition"] != \
                "vendor_source_required_not_redistributable" or \
                row["confidence"] != "candidate" or \
                int(row["size"]) != function["size"] or \
                len(body) != function["size"] or \
                hashlib.sha256(body).hexdigest() != function["sha256"]:
            raise AssertionError(
                f"GoMore energy-model boundary changed: 0x{entry:08x}"
            )
    gomore_iir_summary = summarize_r1_gomore_iir_designer(
        ROOT / "research/decompilation/rebuild/rebuilt-application.bin"
    )
    if gomore_iir_summary["function_count"] != 1 or \
            gomore_iir_summary["function_bytes"] != 602 or \
            gomore_iir_summary["callgraph"]["sole_caller_function"] != \
            "0x00071d62" or \
            gomore_iir_summary["callgraph"]["sole_callsite"] != "0x00071d76" or \
            gomore_iir_summary["callgraph"]["outside_caller_exclusivity"] is not True or \
            gomore_iir_summary["dependencies"]["dependency_provider_family"] != \
            "arm_toolchain_runtime" or \
            gomore_iir_summary["dependencies"]["dependency_bodies_included"] is not False or \
            gomore_iir_summary["boundary"]["provider_family"] != \
            "gomore_health_algorithm_candidate" or \
            gomore_iir_summary["boundary"]["source_disposition"] != \
            "vendor_source_required_not_redistributable" or \
            gomore_iir_summary["boundary"][
                "local_algorithm_reimplementation_authorized"] is not False or \
            gomore_iir_summary["boundary"][
                "toolchain_math_reimplementation_authorized"] is not False or \
            gomore_iir_summary["safety"] != {
                "static_parser_only": True,
                "live_sensor_data_read": False,
                "algorithm_or_coefficients_emitted": False,
            }:
        raise AssertionError("GoMore IIR designer boundary metadata changed")
    for function in GOMORE_IIR_DESIGNER_FUNCTIONS:
        entry = int(function["entry"])
        end = int(function["end_exclusive"])
        row = ownership_by_key[("application", f"0x{entry:08x}")]
        body = recovered[entry - recovered_base:end - recovered_base]
        if row["provider_family"] != "gomore_health_algorithm_candidate" or \
                row["source_disposition"] != \
                "vendor_source_required_not_redistributable" or \
                row["confidence"] != "candidate" or \
                int(row["size"]) != function["size"] or \
                len(body) != function["size"] or \
                hashlib.sha256(body).hexdigest() != function["sha256"]:
            raise AssertionError(
                f"GoMore IIR designer boundary changed: 0x{entry:08x}"
            )
    gomore_auth_summary = summarize_r1_gomore_auth_parser(
        ROOT / "research/decompilation/rebuild/rebuilt-application.bin"
    )
    if gomore_auth_summary["function_count"] != 1 or \
            gomore_auth_summary["function_bytes"] != 528 or \
            gomore_auth_summary["callgraph"]["sole_caller_function"] != \
            "0x0006b27c" or \
            gomore_auth_summary["callgraph"]["sole_callsite"] != "0x0006b38a" or \
            gomore_auth_summary["callgraph"]["outside_caller_exclusivity"] is not True or \
            gomore_auth_summary["evidence"]["sdk_auth_diagnostics_present"] is not True or \
            gomore_auth_summary["evidence"]["gomore_authorization_caller_present"] is not True or \
            gomore_auth_summary["evidence"]["unclassified_helper_bodies_included"] is not False or \
            gomore_auth_summary["boundary"]["provider_family"] != \
            "gomore_health_algorithm_candidate" or \
            gomore_auth_summary["boundary"]["source_disposition"] != \
            "vendor_source_required_not_redistributable" or \
            any(gomore_auth_summary["boundary"][key] is not False for key in (
                "private_symbol_or_sdk_version_resolved",
                "local_authorization_reimplementation_authorized",
                "r1_crypto_or_toolchain_reimplemented",
                "unclassified_helpers_admitted",
            )) or \
            gomore_auth_summary["safety"] != {
                "static_parser_only": True,
                "private_key_material_read": False,
                "authorization_material_emitted": False,
                "live_authentication_exposed": False,
            }:
        raise AssertionError("GoMore authorization-parser boundary metadata changed")
    for function in GOMORE_AUTH_PARSER_FUNCTIONS:
        entry = int(function["entry"])
        end = int(function["end_exclusive"])
        row = ownership_by_key[("application", f"0x{entry:08x}")]
        body = b"".join(
            recovered[start - recovered_base:stop - recovered_base]
            for start, stop in function["segments"]
        )
        if row["provider_family"] != "gomore_health_algorithm_candidate" or \
                row["source_disposition"] != \
                "vendor_source_required_not_redistributable" or \
                row["confidence"] != "candidate" or \
                int(row["size"]) != function["size"] or \
                len(body) != function["size"] or \
                hashlib.sha256(body).hexdigest() != function["sha256"]:
            raise AssertionError(
                f"GoMore authorization-parser boundary changed: 0x{entry:08x}"
            )
    gomore_sleep_statistics_summary = summarize_r1_gomore_sleep_stage_statistics(
        ROOT / "research/decompilation/rebuild/rebuilt-application.bin"
    )
    if gomore_sleep_statistics_summary["function_count"] != 3 or \
            gomore_sleep_statistics_summary["function_bytes"] != 796 or \
            gomore_sleep_statistics_summary["callgraph"]["finalizer_function"] != \
            "0x00068f8c" or \
            gomore_sleep_statistics_summary["callgraph"][
                "stage_lookup_outside_caller_count"] != 0 or \
            gomore_sleep_statistics_summary["callgraph"][
                "outside_caller_exclusivity"] is not True or \
            gomore_sleep_statistics_summary["observable_contract"][
                "epoch_minutes"] != 0.5 or \
            gomore_sleep_statistics_summary["observable_contract"][
                "second_block_field_count"] != 12 or \
            gomore_sleep_statistics_summary["boundary"]["provider_family"] != \
            "gomore_health_algorithm_candidate" or \
            gomore_sleep_statistics_summary["boundary"]["source_disposition"] != \
            "vendor_source_required_not_redistributable" or \
            gomore_sleep_statistics_summary["boundary"][
                "local_algorithm_reimplementation_authorized"] is not False or \
            gomore_sleep_statistics_summary["safety"]["algorithm_executed"] is not False or \
            gomore_sleep_statistics_summary["safety"]["algorithm_code_emitted"] is not False:
        raise AssertionError("GoMore sleep-stage statistics boundary metadata changed")
    for function in GOMORE_SLEEP_STAGE_STATISTICS_FUNCTIONS:
        entry = int(function["entry"])
        end = int(function["end_exclusive"])
        row = ownership_by_key[("application", f"0x{entry:08x}")]
        body = recovered[entry - recovered_base:end - recovered_base]
        if row["provider_family"] != "gomore_health_algorithm_candidate" or \
                row["source_disposition"] != \
                "vendor_source_required_not_redistributable" or \
                row["confidence"] != "candidate" or \
                int(row["size"]) != function["size"] or \
                len(body) != function["size"] or \
                hashlib.sha256(body).hexdigest() != function["sha256"]:
            raise AssertionError(
                f"GoMore sleep-stage statistics boundary changed: 0x{entry:08x}"
            )
    structured_log_summary = summarize_r1_structured_log_cache(
        ROOT / "research/decompilation/rebuild/rebuilt-application.bin"
    )
    structured_log_record = structured_log_summary["record"]
    structured_log_boundary = structured_log_summary["boundary"]
    structured_log_safety = structured_log_summary["safety"]
    if structured_log_summary["function_count"] != 16 or \
            structured_log_summary["function_bytes"] != 1802 or \
            structured_log_summary["ghidra_function_count"] != 12 or \
            structured_log_summary["manual_function_count"] != 4 or \
            structured_log_record != {
                "magic": "0x7b",
                "sequence_bytes": 1,
                "tick_modulus": 1000,
                "fixed_header_bits": "0xdc000000",
                "nordic_std_address_bits": 22,
                "maximum_argument_payload_bytes": 32,
                "copied_string_bytes": 16,
                "normal_persistence_bytes": 4096,
                "periodic_gate_raw": 10000,
            } or \
            structured_log_boundary["provider_family"] != \
            "r1_product_specific" or \
            structured_log_boundary["source_disposition"] != \
            "clean_room_behavior_only" or \
            structured_log_boundary["third_party_implementation_identified"] is not False or \
            any(structured_log_boundary[key] is not False for key in (
                "nordic_log_frontend_reimplemented",
                "toolchain_runtime_reimplemented",
                "rtos_critical_section_reimplemented",
                "clock_calendar_provider_reimplemented",
                "generic_device_registry_reimplemented",
                "log_bin_writer_or_export_sender_emitted",
            )) or \
            structured_log_safety != {
                "static_parser_only": True,
                "private_log_content_read": False,
                "live_export_sender_exposed": False,
            }:
        raise AssertionError("R1 structured-log cache metadata changed")
    for function in R1_STRUCTURED_LOG_FUNCTIONS:
        entry = int(function["entry"])
        end = int(function["end_exclusive"])
        row = ownership_by_key[("application", f"0x{entry:08x}")]
        body = recovered[entry - recovered_base:end - recovered_base]
        if row["inventory_source"] != function["inventory"] or \
                row["provider_family"] != "r1_product_specific" or \
                row["source_disposition"] != "clean_room_behavior_only" or \
                row["upstream_symbol"] != function["symbol"] or \
                row["confidence"] != "high" or \
                int(row["size"]) != function["size"] or \
                len(body) != function["size"] or \
                hashlib.sha256(body).hexdigest() != function["sha256"]:
            raise AssertionError(
                f"R1 structured-log cache closure changed: 0x{entry:08x}"
            )
    log_bin_writer_summary = summarize_r1_log_bin_writer(
        ROOT / "research/decompilation/rebuild/rebuilt-application.bin"
    )
    log_bin_partition = log_bin_writer_summary["partition"]
    log_bin_writer = log_bin_writer_summary["writer"]
    log_bin_boundary = log_bin_writer_summary["boundary"]
    log_bin_safety = log_bin_writer_summary["safety"]
    if log_bin_writer_summary["function_count"] != 3 or \
            log_bin_writer_summary["function_bytes"] != 876 or \
            log_bin_partition != {
                "name": "log.bin",
                "relative_offset_bytes": 0x18000,
                "length_bytes": 0xC000,
                "sector_bytes": 0x1000,
                "sector_count": 12,
                "erased_probe_word_offset": 4,
            } or \
            log_bin_writer != {
                "maximum_input_bytes": 0x1000,
                "initialize_on_first_write": True,
                "advance_before_cross_page_write": True,
                "erase_selected_nonempty_page": True,
                "preerase_next_nonempty_page_after_write": True,
                "wrap_modulo_partition_sector_count": True,
                "full_partition_scan_fallback_sector": 0,
                "direct_caller": "0x000914d2",
            } or \
            log_bin_boundary["provider_family"] != "r1_product_specific" or \
            log_bin_boundary["source_disposition"] != "clean_room_behavior_only" or \
            log_bin_boundary["third_party_implementation_identified"] is not False or \
            any(log_bin_boundary[key] is not False for key in (
                "fal_lookup_reimplemented",
                "flash_read_write_erase_reimplemented",
                "nordic_logging_reimplemented",
                "structured_log_encoder_reimplemented",
                "virtual_export_or_transport_sender_emitted",
            )) or \
            log_bin_safety != {
                "static_parser_only": True,
                "private_log_content_read": False,
                "live_export_sender_exposed": False,
                "raw_flash_mutation_interface_exposed": False,
            }:
        raise AssertionError("R1 log.bin writer metadata changed")
    for function in R1_LOG_BIN_WRITER_FUNCTIONS:
        entry = int(function["entry"])
        end = int(function["end_exclusive"])
        row = ownership_by_key[("application", f"0x{entry:08x}")]
        body = recovered[entry - recovered_base:end - recovered_base]
        if row["inventory_source"] != function["inventory"] or \
                row["provider_family"] != "r1_product_specific" or \
                row["source_disposition"] != "clean_room_behavior_only" or \
                row["upstream_symbol"] != function["symbol"] or \
                row["confidence"] != "high" or \
                int(row["size"]) != function["size"] or \
                len(body) != function["size"] or \
                hashlib.sha256(body).hexdigest() != function["sha256"]:
            raise AssertionError(
                f"R1 log.bin writer closure changed: 0x{entry:08x}"
            )
    hrv_sync_flush_summary = summarize_r1_hrv_sync_flush(
        ROOT / "research/decompilation/rebuild/rebuilt-application.bin"
    )
    if hrv_sync_flush_summary["function_count"] != 2 or \
            hrv_sync_flush_summary["function_bytes"] != 616 or \
            hrv_sync_flush_summary["packet"] != {
                "hour_slots": 24,
                "bytes_per_present_slot": 7,
                "fixed_prefix_bytes": 13,
                "header_count_bytes": 1,
                "header_timezone_bytes": 2,
                "header_day_timestamp_bytes": 4,
                "header_latest_value_bytes": 6,
                "ack_context_bytes": 8,
                "future_packet_drop": True,
                "builder_reset_after_attempt": True,
            } or \
            hrv_sync_flush_summary["boundary"]["provider_family"] != \
            "r1_product_specific" or \
            hrv_sync_flush_summary["boundary"]["source_disposition"] != \
            "clean_room_behavior_only" or \
            hrv_sync_flush_summary["boundary"][
                "third_party_implementation_identified"] is not False or \
            any(hrv_sync_flush_summary["boundary"][key] is not False for key in (
                "freertos_allocator_reimplemented",
                "time_calendar_provider_reimplemented",
                "topic_or_transport_sender_reimplemented",
                "structured_logging_reimplemented",
                "sensor_or_biometric_algorithm_included",
            )) or \
            hrv_sync_flush_summary["safety"] != {
                "static_parser_only": True,
                "private_history_read": False,
                "live_sender_exposed": False,
            }:
        raise AssertionError("R1 HRV sync-flush metadata changed")
    for function in R1_HRV_SYNC_FLUSH_FUNCTIONS:
        entry = int(function["entry"])
        end = int(function["end_exclusive"])
        row = ownership_by_key[("application", f"0x{entry:08x}")]
        body = recovered[entry - recovered_base:end - recovered_base]
        if row["inventory_source"] != function["inventory"] or \
                row["provider_family"] != "r1_product_specific" or \
                row["source_disposition"] != "clean_room_behavior_only" or \
                row["upstream_symbol"] != function["symbol"] or \
                row["confidence"] != "high" or \
                int(row["size"]) != function["size"] or \
                len(body) != function["size"] or \
                hashlib.sha256(body).hexdigest() != function["sha256"]:
            raise AssertionError(
                f"R1 HRV sync-flush closure changed: 0x{entry:08x}"
            )
    hr_sync_flush_summary = summarize_r1_hr_sync_flush(
        ROOT / "research/decompilation/rebuild/rebuilt-application.bin"
    )
    if hr_sync_flush_summary["function_count"] != 2 or \
            hr_sync_flush_summary["function_bytes"] != 578 or \
            hr_sync_flush_summary["packet"] != {
                "hour_slots": 24,
                "bytes_per_present_slot": 4,
                "fixed_prefix_bytes": 12,
                "header_count_bytes": 1,
                "header_timezone_bytes": 2,
                "header_day_timestamp_bytes": 4,
                "header_latest_value_bytes": 5,
                "ack_context_bytes": 8,
                "future_packet_drop": True,
                "builder_reset_after_attempt": True,
            } or \
            hr_sync_flush_summary["boundary"]["provider_family"] != \
            "r1_product_specific" or \
            hr_sync_flush_summary["boundary"]["source_disposition"] != \
            "clean_room_behavior_only" or \
            hr_sync_flush_summary["boundary"][
                "third_party_implementation_identified"] is not False or \
            any(hr_sync_flush_summary["boundary"][key] is not False for key in (
                "freertos_allocator_reimplemented",
                "time_calendar_provider_reimplemented",
                "topic_or_transport_sender_reimplemented",
                "structured_logging_reimplemented",
                "sensor_or_biometric_algorithm_included",
            )) or \
            hr_sync_flush_summary["safety"] != {
                "static_parser_only": True,
                "private_history_read": False,
                "live_sender_exposed": False,
            }:
        raise AssertionError("R1 heart-rate sync-flush metadata changed")
    for function in R1_HR_SYNC_FLUSH_FUNCTIONS:
        entry = int(function["entry"])
        end = int(function["end_exclusive"])
        row = ownership_by_key[("application", f"0x{entry:08x}")]
        body = recovered[entry - recovered_base:end - recovered_base]
        if row["inventory_source"] != function["inventory"] or \
                row["provider_family"] != "r1_product_specific" or \
                row["source_disposition"] != "clean_room_behavior_only" or \
                row["upstream_symbol"] != function["symbol"] or \
                row["confidence"] != "high" or \
                int(row["size"]) != function["size"] or \
                len(body) != function["size"] or \
                hashlib.sha256(body).hexdigest() != function["sha256"]:
            raise AssertionError(
                f"R1 heart-rate sync-flush closure changed: 0x{entry:08x}"
            )
    spo2_sync_flush_summary = summarize_r1_spo2_sync_flush(
        ROOT / "research/decompilation/rebuild/rebuilt-application.bin"
    )
    if spo2_sync_flush_summary["function_count"] != 2 or \
            spo2_sync_flush_summary["function_bytes"] != 578 or \
            spo2_sync_flush_summary["packet"] != {
                "hour_slots": 24,
                "bytes_per_present_slot": 4,
                "fixed_prefix_bytes": 12,
                "header_count_bytes": 1,
                "header_timezone_bytes": 2,
                "header_day_timestamp_bytes": 4,
                "header_latest_value_bytes": 5,
                "ack_context_bytes": 8,
                "future_packet_drop": True,
                "builder_reset_after_attempt": True,
            } or \
            spo2_sync_flush_summary["boundary"]["provider_family"] != \
            "r1_product_specific" or \
            spo2_sync_flush_summary["boundary"]["source_disposition"] != \
            "clean_room_behavior_only" or \
            spo2_sync_flush_summary["boundary"][
                "third_party_implementation_identified"] is not False or \
            any(spo2_sync_flush_summary["boundary"][key] is not False for key in (
                "freertos_allocator_reimplemented",
                "time_calendar_provider_reimplemented",
                "topic_or_transport_sender_reimplemented",
                "structured_logging_reimplemented",
                "sensor_or_biometric_algorithm_included",
            )) or \
            spo2_sync_flush_summary["safety"] != {
                "static_parser_only": True,
                "private_history_read": False,
                "live_sender_exposed": False,
            }:
        raise AssertionError("R1 SpO2 sync-flush metadata changed")
    for function in R1_SPO2_SYNC_FLUSH_FUNCTIONS:
        entry = int(function["entry"])
        end = int(function["end_exclusive"])
        row = ownership_by_key[("application", f"0x{entry:08x}")]
        body = recovered[entry - recovered_base:end - recovered_base]
        if row["inventory_source"] != function["inventory"] or \
                row["provider_family"] != "r1_product_specific" or \
                row["source_disposition"] != "clean_room_behavior_only" or \
                row["upstream_symbol"] != function["symbol"] or \
                row["confidence"] != "high" or \
                int(row["size"]) != function["size"] or \
                len(body) != function["size"] or \
                hashlib.sha256(body).hexdigest() != function["sha256"]:
            raise AssertionError(
                f"R1 SpO2 sync-flush closure changed: 0x{entry:08x}"
            )
    touch_task_dispatcher_summary = summarize_r1_touch_task_dispatcher(
        ROOT / "research/decompilation/rebuild/rebuilt-application.bin"
    )
    if touch_task_dispatcher_summary["function_count"] != 1 or \
            touch_task_dispatcher_summary["function_bytes"] != 578 or \
            touch_task_dispatcher_summary["callgraph"] != {
                "direct_callsite": "0x00092822",
                "dispatch_parameter": "event-bit mask",
            } or \
            touch_task_dispatcher_summary["factory_transactions"] != {
                "count": 6,
                "marker_values": [1, 2, 3, 4, 5, 6],
                "communication_begin": "0x00046f60",
                "provider_communication_end": "0x0002f866",
                "communication_close": "0x00046f54",
            } or \
            touch_task_dispatcher_summary["boundary"]["provider_family"] != \
            "r1_iqs7211e_provider_adapter" or \
            touch_task_dispatcher_summary["boundary"]["source_disposition"] != \
            "clean_room_adapter_only_use_pinned_provider" or \
            any(touch_task_dispatcher_summary["boundary"][key] is not False for key in (
                "iqs7211e_controller_or_register_logic_reimplemented",
                "nordic_or_cmsis_rtos_reimplemented",
                "shared_power_provider_reimplemented",
                "logging_frontend_reimplemented",
                "unresolved_hardware_wrappers_admitted",
            )) or \
            touch_task_dispatcher_summary["safety"] != {
                "static_parser_only": True,
                "live_gpio_or_i2c_access": False,
                "factory_command_sender_exposed": False,
            }:
        raise AssertionError("R1 touch-task dispatcher metadata changed")
    for function in R1_TOUCH_TASK_DISPATCHER_FUNCTIONS:
        entry = int(function["entry"])
        row = ownership_by_key[("application", f"0x{entry:08x}")]
        body = b"".join(
            recovered[start - recovered_base:end - recovered_base]
            for start, end in function["segments"]
        )
        if row["inventory_source"] != function["inventory"] or \
                row["provider_family"] != "r1_iqs7211e_provider_adapter" or \
                row["source_disposition"] != \
                "clean_room_adapter_only_use_pinned_provider" or \
                row["upstream_symbol"] != function["symbol"] or \
                row["confidence"] != "high" or \
                int(row["size"]) != function["size"] or \
                len(body) != function["size"] or \
                hashlib.sha256(body).hexdigest() != function["sha256"]:
            raise AssertionError(
                f"R1 touch-task dispatcher closure changed: 0x{entry:08x}"
            )
    sensor_stream_unregister_summary = summarize_r1_sensor_stream_unregister(
        ROOT / "research/decompilation/rebuild/rebuilt-application.bin"
    )
    if sensor_stream_unregister_summary["function_count"] != 1 or \
            sensor_stream_unregister_summary["function_bytes"] != 562 or \
            sensor_stream_unregister_summary["callgraph"] != {
                "direct_callsite_count": 25,
                "unique_caller_function_count": 20,
                "cross_boundary_examples": {
                    "gomore_provider": "0x00049410",
                    "r1_motion_adapter": "0x0006f228",
                },
            } or \
            sensor_stream_unregister_summary["behavior"]["timer_period_formula"] != \
            "1024 / maximum listener rate" or \
            sensor_stream_unregister_summary["behavior"][
                "deferred_unregister_when_dispatching"] is not True or \
            sensor_stream_unregister_summary["behavior"][
                "empty_list_releases_buffer_and_timer"] is not True or \
            sensor_stream_unregister_summary["boundary"]["provider_family"] != \
            "unknown_sensor_stream_framework_candidate" or \
            sensor_stream_unregister_summary["boundary"]["source_disposition"] != \
            "investigate_before_implementing" or \
            sensor_stream_unregister_summary["boundary"][
                "attributable_source_identified"] is not False or \
            sensor_stream_unregister_summary["boundary"][
                "local_framework_reimplementation_authorized"] is not False or \
            sensor_stream_unregister_summary["boundary"][
                "dependent_list_allocator_timer_code_admitted"] is not False or \
            sensor_stream_unregister_summary["boundary"][
                "provider_close_hook_admitted"] is not False or \
            sensor_stream_unregister_summary["safety"] != {
                "static_parser_only": True,
                "live_sensor_data_read": False,
                "registration_or_unregistration_api_exposed": False,
            }:
        raise AssertionError("sensor-stream framework boundary metadata changed")
    for function in SENSOR_STREAM_UNREGISTER_FUNCTIONS:
        entry = int(function["entry"])
        row = ownership_by_key[("application", f"0x{entry:08x}")]
        body = b"".join(
            recovered[start - recovered_base:end - recovered_base]
            for start, end in function["segments"]
        )
        if row["inventory_source"] != function["inventory"] or \
                row["provider_family"] != \
                "unknown_sensor_stream_framework_candidate" or \
                row["source_disposition"] != "investigate_before_implementing" or \
                row["upstream_symbol"] != function["symbol"] or \
                row["confidence"] != "candidate" or \
                int(row["size"]) != function["size"] or \
                len(body) != function["size"] or \
                hashlib.sha256(body).hexdigest() != function["sha256"]:
            raise AssertionError(
                f"sensor-stream framework boundary changed: 0x{entry:08x}"
            )
    sensor_stream_register_summary = summarize_r1_sensor_stream_register(
        ROOT / "research/decompilation/rebuild/rebuilt-application.bin"
    )
    if sensor_stream_register_summary["function_count"] != 1 or \
            sensor_stream_register_summary["function_bytes"] != 464 or \
            sensor_stream_register_summary["behavior"] != {
                "listener_name_maximum_bytes": 8,
                "requested_order_capped_at": 1,
                "listener_list_offset": "0x2c",
                "listener_callback_offset": "0x10",
                "listener_rate_offset": "0x0d",
                "empty_list_allocates_sample_buffer": True,
                "higher_rate_resizes_existing_buffer": True,
                "timer_period_formula": "1024 / requested rate",
                "timer_callback_thumb_pointer": "0x0008a1e1",
                "optional_provider_open_hook": True,
            } or sensor_stream_register_summary["boundary"] != {
                "provider_family": "unknown_sensor_stream_framework_candidate",
                "source_disposition": "investigate_before_implementing",
                "attributable_source_identified": False,
                "local_framework_reimplementation_authorized": False,
                "list_allocator_timer_and_resize_dependencies_admitted": False,
                "provider_open_hook_admitted": False,
            } or sensor_stream_register_summary["safety"] != {
                "static_parser_only": True,
                "live_sensor_data_read": False,
                "registration_or_unregistration_api_exposed": False,
            }:
        raise AssertionError("sensor-stream registration boundary metadata changed")
    for function in SENSOR_STREAM_REGISTER_FUNCTIONS:
        entry = int(function["entry"])
        row = ownership_by_key[("application", f"0x{entry:08x}")]
        body = recovered[entry - recovered_base:
                         int(function["end_exclusive"]) - recovered_base]
        if row["inventory_source"] != function["inventory"] or \
                row["provider_family"] != \
                "unknown_sensor_stream_framework_candidate" or \
                row["source_disposition"] != "investigate_before_implementing" or \
                row["upstream_symbol"] != function["symbol"] or \
                row["confidence"] != "candidate" or \
                int(row["size"]) != function["size"] or \
                len(body) != function["size"] or \
                hashlib.sha256(body).hexdigest() != function["sha256"]:
            raise AssertionError(
                f"sensor-stream registration boundary changed: 0x{entry:08x}"
            )
    sensor_stream_dispatch_summary = summarize_r1_sensor_stream_dispatch(
        ROOT / "research/decompilation/rebuild/rebuilt-application.bin"
    )
    if sensor_stream_dispatch_summary["function_count"] != 1 or \
            sensor_stream_dispatch_summary["function_bytes"] != 422 or \
            sensor_stream_dispatch_summary["indirect_entry"] != {
                "pointer_location": "0x00089acc",
                "thumb_pointer": "0x0008a1e1",
                "direct_callsite_count": 0,
            } or sensor_stream_dispatch_summary["behavior"] != {
                "timer_context_object_offset": "0x0c",
                "provider_read_hook_offset": "provider operations + 0x08",
                "sample_buffer_offset": "0x14",
                "sample_buffer_cursor_offset": "0x18",
                "listener_list_offset": "0x2c",
                "listener_callback_offset": "0x10",
                "listener_rate_offset": "0x0d",
                "dispatch_active_flag": "bit 1 of object + 0x28",
                "pending_unregister_flag": "bit 2 of object + 0x28",
                "deferred_listener_flag": "bit 0 of listener + 0x14",
                "sample_buffer_wraps": True,
                "rate_mismatch_uses_resize_copy_helper": True,
                "deferred_cleanup_tail_target": "0x00089ba8",
                "empty_list_releases_buffer_and_timer": True,
            } or sensor_stream_dispatch_summary["boundary"] != {
                "provider_family": "unknown_sensor_stream_framework_candidate",
                "source_disposition": "investigate_before_implementing",
                "attributable_source_identified": False,
                "local_framework_reimplementation_authorized": False,
                "dependent_list_allocator_timer_code_admitted": False,
                "provider_read_and_listener_hooks_admitted": False,
            } or sensor_stream_dispatch_summary["safety"] != {
                "static_parser_only": True,
                "live_sensor_data_read": False,
                "timer_callback_exposed": False,
            }:
        raise AssertionError("sensor-stream dispatch boundary metadata changed")
    for function in SENSOR_STREAM_DISPATCH_FUNCTIONS:
        entry = int(function["entry"])
        row = ownership_by_key[("application", f"0x{entry:08x}")]
        body = b"".join(
            recovered[start - recovered_base:end - recovered_base]
            for start, end in function["segments"]
        )
        if row["inventory_source"] != function["inventory"] or \
                row["provider_family"] != \
                "unknown_sensor_stream_framework_candidate" or \
                row["source_disposition"] != "investigate_before_implementing" or \
                row["upstream_symbol"] != function["symbol"] or \
                row["confidence"] != "candidate" or \
                int(row["size"]) != function["size"] or \
                len(body) != function["size"] or \
                hashlib.sha256(body).hexdigest() != function["sha256"]:
            raise AssertionError(
                f"sensor-stream dispatch boundary changed: 0x{entry:08x}"
            )
    legacy_command_dispatch_summary = summarize_r1_legacy_command_dispatch(
        ROOT / "research/decompilation/rebuild/rebuilt-application.bin"
    )
    if legacy_command_dispatch_summary["function_count"] != 1 or \
            legacy_command_dispatch_summary["function_bytes"] != 464 or \
            legacy_command_dispatch_summary["behavior"] != {
                "workspace_bytes": 36,
                "workspace_pointer": "0x2001a174",
                "opcode_offset": 2,
                "recognized_opcode_count": 23,
                "opcode_handlers": {
                    f"0x{opcode:02x}": f"0x{handler:08x}"
                    for opcode, handler in R1_LEGACY_COMMAND_OPCODE_HANDLERS.items()
                },
                "unknown_return": "0xffffffff",
                "recognized_return": 0,
                "pair_auth_opcode": "0x88",
                "pair_auth_response_byte": 2,
            } or legacy_command_dispatch_summary["boundary"] != {
                "provider_family": "r1_product_specific",
                "source_disposition": "clean_room_behavior_only",
                "router_only_implemented": True,
                "handler_implementations_admitted_by_this_closure": False,
                "stock_unbounded_copy_preserved": False,
                "bounded_workspace_required": True,
            } or legacy_command_dispatch_summary["safety"] != {
                "pure_route_selection": True,
                "live_command_handler_invocation": False,
                "pairing_or_authorization_state_mutation": False,
            }:
        raise AssertionError("R1 legacy command-dispatch metadata changed")
    for function in R1_LEGACY_COMMAND_DISPATCH_FUNCTIONS:
        entry = int(function["entry"])
        row = ownership_by_key[("application", f"0x{entry:08x}")]
        body = recovered[entry - recovered_base:
                         int(function["end_exclusive"]) - recovered_base]
        if row["inventory_source"] != function["inventory"] or \
                row["provider_family"] != function["provider_family"] or \
                row["source_disposition"] != function["source_disposition"] or \
                row["upstream_symbol"] != function["symbol"] or \
                row["confidence"] != "high" or \
                int(row["size"]) != function["size"] or \
                len(body) != function["size"] or \
                hashlib.sha256(body).hexdigest() != function["sha256"]:
            raise AssertionError(
                f"R1 legacy command-dispatch boundary changed: 0x{entry:08x}"
            )
    ati_calibration_summary = summarize_r1_ati_calibration_command(
        ROOT / "research/decompilation/rebuild/rebuilt-application.bin"
    )
    if ati_calibration_summary["function_count"] != 1 or \
            ati_calibration_summary["function_bytes"] != 416 or \
            ati_calibration_summary["jump_table"] != {
                "address": "0x00062132",
                "bytes_hex": "06233a5362758496b1b5b900",
                "subcommand_count": 11,
            } or ati_calibration_summary["behavior"] != {
                "opcode": "0x91",
                "subcommand_offset": 3,
                "argument_0_offset": 4,
                "argument_1_offset": 5,
                "default_response_status": 5,
                "query_success_response_status": 6,
                "event_flags": {
                    "1": "0x00000040",
                    "2": "0x00000080",
                    "3": "0x00000100",
                    "4": "0x00000200",
                    "5": "0x00000400",
                    "6": "0x00000800",
                },
                "configuration_words": {
                    "3": [1, 1],
                    "4": [2, 2],
                    "5": [3, 1],
                    "6": [4, 1],
                },
                "subcommand_6_booleanizes_argument_0": True,
                "subcommand_7_query_failure_value": "0xff",
                "subcommands_8_9_touch_source": 2,
                "subcommand_10_returns_ring_size": True,
                "unknown_subcommand_uses_default_response": True,
            } or ati_calibration_summary["ownership"] != {
                "provider_family": "r1_product_specific",
                "source_disposition": "clean_room_behavior_only",
                "local_surface": "bounded side-effect-free command planner",
                "iqs7211e_provider_reimplemented": False,
                "nordic_cmsis_queue_reimplemented": False,
                "transport_or_logging_reimplemented": False,
            } or ati_calibration_summary["safety"] != {
                "pure_planner_only": True,
                "live_touch_operation": False,
                "calibration_mutation": False,
                "transport_send": False,
            }:
        raise AssertionError("R1 ATI calibration command metadata changed")
    for function in R1_ATI_CALIBRATION_COMMAND_FUNCTIONS:
        entry = int(function["entry"])
        row = ownership_by_key[("application", f"0x{entry:08x}")]
        body = b"".join(
            recovered[start - recovered_base:end - recovered_base]
            for start, end in function["segments"]
        )
        if row["inventory_source"] != function["inventory"] or \
                row["provider_family"] != "r1_product_specific" or \
                row["source_disposition"] != "clean_room_behavior_only" or \
                row["upstream_symbol"] != function["symbol"] or \
                row["confidence"] != "high" or \
                int(row["size"]) != function["size"] or \
                len(body) != function["size"] or \
                hashlib.sha256(body).hexdigest() != function["sha256"]:
            raise AssertionError(
                f"R1 ATI calibration command changed: 0x{entry:08x}"
            )
    battery_runtime_summary = summarize_r1_battery_runtime_service(
        ROOT / "research/decompilation/rebuild/rebuilt-application.bin"
    )
    if battery_runtime_summary["function_count"] != 1 or \
            battery_runtime_summary["function_bytes"] != 406 or \
            battery_runtime_summary["overlap_reconciliation"] != {
                "accepted_manual_extent": "0x00031fcc..<0x00032168",
                "accepted_manual_extent_bytes": 412,
                "native_ghidra_entry": "0x00031fd0",
                "leading_veneer_bytes": 4,
                "trailing_alignment_bytes": 2,
                "duplicate_algorithm_body_created": False,
            } or battery_runtime_summary["ownership"] != {
                "provider_family": "r1_product_specific",
                "source_disposition": "clean_room_behavior_only",
                "existing_clean_room_controller_reused": True,
                "provider_dependencies_admitted_by_this_closure": False,
            }:
        raise AssertionError("R1 battery runtime native-entry metadata changed")
    for function in R1_BATTERY_RUNTIME_SERVICE_FUNCTIONS:
        entry = int(function["entry"])
        end = int(function["end_exclusive"])
        row = ownership_by_key[("application", f"0x{entry:08x}")]
        body = recovered[entry - recovered_base:end - recovered_base]
        if row["inventory_source"] != function["inventory"] or \
                row["provider_family"] != "r1_product_specific" or \
                row["source_disposition"] != "clean_room_behavior_only" or \
                row["upstream_symbol"] != function["symbol"] or \
                row["confidence"] != "high" or \
                int(row["size"]) != function["size"] or \
                len(body) != function["size"] or \
                hashlib.sha256(body).hexdigest() != function["sha256"]:
            raise AssertionError(
                f"R1 battery runtime native entry changed: 0x{entry:08x}"
            )
    for function in R1_HRV_FLASH_MERGE_FUNCTIONS:
        entry = int(function["entry"])
        end = int(function["end_exclusive"])
        row = ownership_by_key[("application", f"0x{entry:08x}")]
        body = recovered[entry - recovered_base:end - recovered_base]
        if row["provider_family"] != "r1_product_specific" or \
                row["source_disposition"] != "clean_room_behavior_only" or \
                row["upstream_symbol"] != function["symbol"] or \
                int(row["size"]) != function["size"] or \
                len(body) != function["size"] or \
                hashlib.sha256(body).hexdigest() != function["sha256"]:
            raise AssertionError(f"R1 HRV flash merge changed: 0x{entry:08x}")
    scalar_flash_summary = summarize_r1_scalar_health_flash_merge(
        ROOT / "research/decompilation/rebuild/rebuilt-application.bin"
    )
    if scalar_flash_summary["function_count"] != 2 or \
            scalar_flash_summary["function_bytes"] != 788 or \
            scalar_flash_summary["behavior"] != {
                "required_record_bytes": 128,
                "future_timestamp_rejected": True,
                "local_hour_slot_policy": "hour 0 -> slot 23; otherwise hour - 1",
                "local_day_start_uses_hour_minute_second": True,
                "midnight_adjustment_seconds": -86400,
                "optional_previous_local_day_filter": True,
                "zero_average_ignored": True,
                "flush_on_day_or_timezone_change": True,
                "bytes_per_present_slot": 4,
                "duplicate_slot_not_overwritten": True,
                "newest_timestamp_monotonic": True,
            } or scalar_flash_summary["clean_room"] != {
                "shared_api": "r1_health_u8_flash_record_merge",
                "normalized_record_only": True,
                "first_record_wins": True,
                "provider_blob_parser_included": False,
                "calendar_provider_included": False,
                "transport_provider_included": False,
            }:
        raise AssertionError("R1 scalar health flash merge metadata changed")
    for function in R1_SCALAR_HEALTH_FLASH_MERGE_FUNCTIONS:
        entry = int(function["entry"])
        end = int(function["end_exclusive"])
        row = ownership_by_key[("application", f"0x{entry:08x}")]
        body = recovered[entry - recovered_base:end - recovered_base]
        if row["inventory_source"] != function["inventory"] or \
                row["provider_family"] != "r1_product_specific" or \
                row["source_disposition"] != "clean_room_behavior_only" or \
                row["upstream_symbol"] != function["symbol"] or \
                row["confidence"] != "high" or \
                int(row["size"]) != function["size"] or \
                len(body) != function["size"] or \
                hashlib.sha256(body).hexdigest() != function["sha256"]:
            raise AssertionError(
                f"R1 scalar health flash merge changed: 0x{entry:08x}"
            )
    hrv_timing_summary = summarize_r1_hrv_timing_start(
        ROOT / "research/decompilation/rebuild/rebuilt-application.bin"
    )
    if hrv_timing_summary["function_count"] != 1 or \
            hrv_timing_summary["function_bytes"] != 382 or \
            hrv_timing_summary["behavior"]["hourly_delay_seconds"] != 120 or \
            hrv_timing_summary["behavior"]["catchup_hour_phase_skip_start"] != 3450 or \
            hrv_timing_summary["behavior"]["workspace_clear_bytes"] != 208 or \
            hrv_timing_summary["boundary"]["clean_room_api"] != \
                "r1_hrv_plan_timing_start":
        raise AssertionError("R1 HRV timing-start metadata changed")
    for function in R1_HRV_TIMING_START_FUNCTIONS:
        entry = int(function["entry"])
        end = int(function["end_exclusive"])
        row = ownership_by_key[("application", f"0x{entry:08x}")]
        body = recovered[entry - recovered_base:end - recovered_base]
        if row["inventory_source"] != function["inventory"] or \
                row["provider_family"] != "r1_product_specific" or \
                row["source_disposition"] != "clean_room_behavior_only" or \
                row["upstream_symbol"] != function["symbol"] or \
                row["confidence"] != "high" or \
                int(row["size"]) != function["size"] or \
                len(body) != function["size"] or \
                hashlib.sha256(body).hexdigest() != function["sha256"]:
            raise AssertionError(
                f"R1 HRV timing-start function changed: 0x{entry:08x}"
            )
    hrv_ram_summary = summarize_r1_hrv_ram_cache_merge(
        ROOT / "research/decompilation/rebuild/rebuilt-application.bin"
    )
    if hrv_ram_summary["function_count"] != 1 or \
            hrv_ram_summary["function_bytes"] != 380 or \
            hrv_ram_summary["behavior"]["builder_ack_mode"] != 2 or \
            hrv_ram_summary["behavior"]["current_hour_index_capped"] != 23 or \
            not hrv_ram_summary["behavior"]["current_hour_included_outside_window"] or \
            hrv_ram_summary["behavior"]["latest_value_prefix_bytes"] != 6 or \
            hrv_ram_summary["boundary"]["clean_room_api"] != \
                "r1_health_u16_ram_cache_merge":
        raise AssertionError("R1 HRV RAM-cache merge metadata changed")
    for function in R1_HRV_RAM_CACHE_MERGE_FUNCTIONS:
        entry = int(function["entry"])
        end = int(function["end_exclusive"])
        row = ownership_by_key[("application", f"0x{entry:08x}")]
        body = recovered[entry - recovered_base:end - recovered_base]
        if row["inventory_source"] != function["inventory"] or \
                row["provider_family"] != "r1_product_specific" or \
                row["source_disposition"] != "clean_room_behavior_only" or \
                row["upstream_symbol"] != function["symbol"] or \
                row["confidence"] != "high" or \
                int(row["size"]) != function["size"] or \
                len(body) != function["size"] or \
                hashlib.sha256(body).hexdigest() != function["sha256"]:
            raise AssertionError(
                f"R1 HRV RAM-cache merge changed: 0x{entry:08x}"
            )
    scalar_ram_summary = summarize_r1_scalar_health_ram_cache_merge(
        ROOT / "research/decompilation/rebuild/rebuilt-application.bin"
    )
    if scalar_ram_summary["function_count"] != 2 or \
            scalar_ram_summary["function_bytes"] != 728 or \
            scalar_ram_summary["behavior"]["builder_ack_mode"] != 2 or \
            scalar_ram_summary["behavior"]["bytes_per_present_slot"] != 4 or \
            scalar_ram_summary["behavior"]["current_hour_index_capped"] != 23 or \
            not scalar_ram_summary["behavior"]["current_hour_included_outside_window"] or \
            scalar_ram_summary["boundary"]["clean_room_api"] != \
                "r1_health_u8_ram_cache_merge" or \
            not scalar_ram_summary["boundary"]["shared_between_metrics"]:
        raise AssertionError("R1 scalar-health RAM-cache merge metadata changed")
    for function in R1_SCALAR_HEALTH_RAM_CACHE_MERGE_FUNCTIONS:
        entry = int(function["entry"])
        end = int(function["end_exclusive"])
        row = ownership_by_key[("application", f"0x{entry:08x}")]
        body = recovered[entry - recovered_base:end - recovered_base]
        if row["inventory_source"] != function["inventory"] or \
                row["provider_family"] != "r1_product_specific" or \
                row["source_disposition"] != "clean_room_behavior_only" or \
                row["upstream_symbol"] != function["symbol"] or \
                row["confidence"] != "high" or \
                int(row["size"]) != function["size"] or \
                len(body) != function["size"] or \
                hashlib.sha256(body).hexdigest() != function["sha256"]:
            raise AssertionError(
                f"R1 scalar-health RAM-cache merge changed: 0x{entry:08x}"
            )
    response_summary = summarize_r1_protocol_response(
        ROOT / "research/decompilation/rebuild/rebuilt-application.bin"
    )
    if response_summary["function_count"] != 2 or \
            response_summary["function_bytes"] != 500 or \
            response_summary["behavior"]["encoded_length_overhead"] != 12 or \
            response_summary["behavior"]["module_index_maximum"] != 3 or \
            not response_summary["behavior"]["status_bit_zero_selects_generated_serial"] or \
            not response_summary["behavior"]["generated_serial_postincremented"] or \
            "MODBUS" not in response_summary["behavior"]["checksum"] or \
            response_summary["behavior"]["allocation_failure_result"] != 3 or \
            response_summary["behavior"]["transport_failure_result"] != 4 or \
            response_summary["behavior"]["no_active_link_result"] != 5 or \
            response_summary["boundary"]["clean_room_api"] != \
                "r1_protocol_send_response":
        raise AssertionError("R1 protocol-response metadata changed")
    for function in R1_PROTOCOL_RESPONSE_FUNCTIONS:
        entry = int(function["entry"])
        end = int(function["end_exclusive"])
        row = ownership_by_key[("application", f"0x{entry:08x}")]
        body = recovered[entry - recovered_base:end - recovered_base]
        if row["inventory_source"] != function["inventory"] or \
                row["provider_family"] != "r1_product_specific" or \
                row["source_disposition"] != "clean_room_behavior_only" or \
                row["upstream_symbol"] != function["symbol"] or \
                row["confidence"] != "high" or \
                int(row["size"]) != function["size"] or \
                len(body) != function["size"] or \
                hashlib.sha256(body).hexdigest() != function["sha256"]:
            raise AssertionError(
                f"R1 protocol-response boundary changed: 0x{entry:08x}"
            )
    export_summary = summarize_r1_export_state_machine(
        ROOT / "research/decompilation/rebuild/rebuilt-application.bin"
    )
    if export_summary["function_count"] != 1 or \
            export_summary["function_bytes"] != 364 or \
            export_summary["behavior"]["maximum_chunk_bytes"] != 4096 or \
            export_summary["behavior"]["interframe_delay_ms"] != 50 or \
            export_summary["behavior"]["retry_result"] != 2 or \
            export_summary["behavior"]["complete_status"] != 3 or \
            export_summary["boundary"]["clean_room_api"] != \
                "r1_export_plan_command" or \
            export_summary["boundary"]["raw_log_sender_included"]:
        raise AssertionError("R1 export state-machine metadata changed")
    for function in R1_EXPORT_STATE_MACHINE_FUNCTIONS:
        entry = int(function["entry"])
        end = int(function["end_exclusive"])
        row = ownership_by_key[("application", f"0x{entry:08x}")]
        body = recovered[entry - recovered_base:end - recovered_base]
        if row["inventory_source"] != function["inventory"] or \
                row["provider_family"] != "r1_product_specific" or \
                row["source_disposition"] != "clean_room_behavior_only" or \
                row["upstream_symbol"] != function["symbol"] or \
                row["confidence"] != "high" or \
                int(row["size"]) != function["size"] or \
                len(body) != function["size"] or \
                hashlib.sha256(body).hexdigest() != function["sha256"]:
            raise AssertionError(
                f"R1 export state machine changed: 0x{entry:08x}"
            )
    frontier_35x_summary = summarize_r1_frontier_35x(
        ROOT / "research/decompilation/rebuild/rebuilt-application.bin"
    )
    if frontier_35x_summary["function_count"] != 5 or \
            frontier_35x_summary["function_bytes"] != 1756 or \
            frontier_35x_summary["product_function_count"] != 4 or \
            frontier_35x_summary["gomore_function_count"] != 1 or \
            any(frontier_35x_summary["safety"].values()):
        raise AssertionError("R1 348...354-byte frontier metadata changed")
    for function in R1_FRONTIER_35X_FUNCTIONS:
        entry = int(function["entry"])
        end = int(function["end_exclusive"])
        row = ownership_by_key[("application", f"0x{entry:08x}")]
        body = recovered[entry - recovered_base:end - recovered_base]
        is_gomore = entry == 0x00094384
        expected_provider = (
            "gomore_health_algorithm_candidate"
            if is_gomore else "r1_product_specific"
        )
        expected_disposition = (
            "vendor_source_required_not_redistributable"
            if is_gomore else "clean_room_behavior_only"
        )
        expected_confidence = "candidate" if is_gomore else "high"
        if row["inventory_source"] != function["inventory"] or \
                row["provider_family"] != expected_provider or \
                row["source_disposition"] != expected_disposition or \
                row["upstream_symbol"] != function["symbol"] or \
                row["confidence"] != expected_confidence or \
                int(row["size"]) != function["size"] or \
                len(body) != function["size"] or \
                hashlib.sha256(body).hexdigest() != function["sha256"]:
            raise AssertionError(
                f"R1 348...354-byte frontier changed: 0x{entry:08x}"
            )
    frontier_334_342_summary = summarize_r1_frontier_334_342(
        ROOT / "research/decompilation/rebuild/rebuilt-application.bin"
    )
    if frontier_334_342_summary["function_count"] != 5 or \
            frontier_334_342_summary["function_bytes"] != 1684 or \
            frontier_334_342_summary["product_function_count"] != 2 or \
            frontier_334_342_summary["gomore_function_count"] != 2 or \
            frontier_334_342_summary["goodix_function_count"] != 1 or \
            any(frontier_334_342_summary["safety"].values()):
        raise AssertionError("R1 334...342-byte frontier metadata changed")
    for function in R1_FRONTIER_334_342_FUNCTIONS:
        function = apply_goodix_democode_attribution(function)
        entry = int(function["entry"])
        end = int(function["end_exclusive"])
        row = ownership_by_key[("application", f"0x{entry:08x}")]
        body = recovered[entry - recovered_base:end - recovered_base]
        expected_confidence = (
            "candidate"
            if function["provider_family"] ==
                "gomore_health_algorithm_candidate"
            else "high"
        )
        if row["inventory_source"] != function["inventory"] or \
                row["provider_family"] != function["provider_family"] or \
                row["source_disposition"] != function["source_disposition"] or \
                row["upstream_symbol"] != function["symbol"] or \
                row["confidence"] != expected_confidence or \
                int(row["size"]) != function["size"] or \
                len(body) != function["size"] or \
                hashlib.sha256(body).hexdigest() != function["sha256"]:
            raise AssertionError(
                f"R1 334...342-byte frontier changed: 0x{entry:08x}"
            )
    frontier_314_328_summary = summarize_r1_frontier_314_328(
        ROOT / "research/decompilation/rebuild/rebuilt-application.bin"
    )
    if frontier_314_328_summary["function_count"] != 5 or \
            frontier_314_328_summary["function_bytes"] != 1604 or \
            frontier_314_328_summary["inventory_bytes"] != 1602 or \
            frontier_314_328_summary["product_function_count"] != 2 or \
            frontier_314_328_summary["nordic_function_count"] != 1 or \
            frontier_314_328_summary["gomore_function_count"] != 2 or \
            any(frontier_314_328_summary["safety"].values()):
        raise AssertionError("R1 314...328-byte frontier metadata changed")
    for function in R1_FRONTIER_314_328_FUNCTIONS:
        function = apply_goodix_democode_attribution(function)
        entry = int(function["entry"])
        end = int(function["end_exclusive"])
        row = ownership_by_key[("application", f"0x{entry:08x}")]
        body = recovered[entry - recovered_base:end - recovered_base]
        expected_confidence = (
            "candidate"
            if function["provider_family"] ==
                "gomore_health_algorithm_candidate"
            else "high"
        )
        if row["inventory_source"] != function["inventory"] or \
                row["provider_family"] != function["provider_family"] or \
                row["source_disposition"] != function["source_disposition"] or \
                row["upstream_symbol"] != function["symbol"] or \
                row["confidence"] != expected_confidence or \
                int(row["size"]) != function["size"] or \
                len(body) != function["size"] or \
                hashlib.sha256(body).hexdigest() != function["sha256"]:
            raise AssertionError(
                f"R1 314...328-byte frontier changed: 0x{entry:08x}"
            )
    frontier_280_308_summary = summarize_r1_frontier_280_308(
        ROOT / "research/decompilation/rebuild/rebuilt-application.bin"
    )
    if frontier_280_308_summary["function_count"] != 5 or \
            frontier_280_308_summary["function_bytes"] != 1496 or \
            frontier_280_308_summary["inventory_bytes"] != 1494 or \
            frontier_280_308_summary["product_function_count"] != 4 or \
            frontier_280_308_summary["goodix_function_count"] != 1 or \
            any(frontier_280_308_summary["safety"].values()):
        raise AssertionError("R1 280...308-byte frontier metadata changed")
    for function in R1_FRONTIER_280_308_FUNCTIONS:
        function = apply_goodix_democode_attribution(function)
        entry = int(function["entry"])
        end = int(function["end_exclusive"])
        row = ownership_by_key[("application", f"0x{entry:08x}")]
        body = recovered[entry - recovered_base:end - recovered_base]
        expected_confidence = "high"
        if row["inventory_source"] != function["inventory"] or \
                row["provider_family"] != function["provider_family"] or \
                row["source_disposition"] != function["source_disposition"] or \
                row["upstream_symbol"] != function["symbol"] or \
                row["confidence"] != expected_confidence or \
                int(row["size"]) != function["size"] or \
                len(body) != function["size"] or \
                hashlib.sha256(body).hexdigest() != function["sha256"]:
            raise AssertionError(
                f"R1 280...308-byte frontier changed: 0x{entry:08x}"
            )
    frontier_264_274_summary = summarize_r1_frontier_264_274(
        ROOT / "research/decompilation/rebuild/rebuilt-application.bin"
    )
    if frontier_264_274_summary["function_count"] != 6 or \
            frontier_264_274_summary["function_bytes"] != 1386 or \
            frontier_264_274_summary["frontier_function_count"] != 5 or \
            frontier_264_274_summary["frontier_function_bytes"] != 1342 or \
            frontier_264_274_summary["exclusive_helper_count"] != 1 or \
            frontier_264_274_summary["product_function_count"] != 3 or \
            frontier_264_274_summary["gomore_function_count"] != 3 or \
            any(frontier_264_274_summary["safety"].values()):
        raise AssertionError("R1 264...274-byte frontier metadata changed")
    for function in R1_FRONTIER_264_274_FUNCTIONS:
        function = apply_goodix_democode_attribution(function)
        entry = int(function["entry"])
        end = int(function["end_exclusive"])
        row = ownership_by_key[("application", f"0x{entry:08x}")]
        body = recovered[entry - recovered_base:end - recovered_base]
        expected_confidence = (
            "candidate"
            if function["provider_family"] ==
                "gomore_health_algorithm_candidate"
            else "high"
        )
        if row["inventory_source"] != function["inventory"] or \
                row["provider_family"] != function["provider_family"] or \
                row["source_disposition"] != function["source_disposition"] or \
                row["upstream_symbol"] != function["symbol"] or \
                row["confidence"] != expected_confidence or \
                int(row["size"]) != function["size"] or \
                len(body) != function["size"] or \
                hashlib.sha256(body).hexdigest() != function["sha256"]:
            raise AssertionError(
                f"R1 264...274-byte frontier changed: 0x{entry:08x}"
            )
    frontier_256_262_summary = summarize_r1_frontier_256_262(
        ROOT / "research/decompilation/rebuild/rebuilt-application.bin"
    )
    if frontier_256_262_summary["function_count"] != 13 or \
            frontier_256_262_summary["function_bytes"] != 2100 or \
            frontier_256_262_summary["inventory_bytes"] != 2090 or \
            frontier_256_262_summary["frontier_function_count"] != 5 or \
            frontier_256_262_summary["frontier_function_bytes"] != 1306 or \
            frontier_256_262_summary["frontier_inventory_bytes"] != 1296 or \
            frontier_256_262_summary["exclusive_helper_count"] != 8 or \
            frontier_256_262_summary["exclusive_helper_bytes"] != 794 or \
            frontier_256_262_summary["product_function_count"] != 2 or \
            frontier_256_262_summary["goodix_adapter_count"] != 1 or \
            frontier_256_262_summary["gomore_function_count"] != 10 or \
            any(frontier_256_262_summary["safety"].values()):
        raise AssertionError("R1 256...262-byte frontier metadata changed")
    for function in R1_FRONTIER_256_262_FUNCTIONS:
        function = apply_goodix_democode_attribution(function)
        entry = int(function["entry"])
        end = int(function["end_exclusive"])
        row = ownership_by_key[("application", f"0x{entry:08x}")]
        body = recovered[entry - recovered_base:end - recovered_base]
        expected_confidence = (
            "candidate"
            if function["provider_family"] ==
                "gomore_health_algorithm_candidate"
            else "high"
        )
        if row["inventory_source"] != function["inventory"] or \
                row["provider_family"] != function["provider_family"] or \
                row["source_disposition"] != function["source_disposition"] or \
                row["upstream_symbol"] != function["symbol"] or \
                row["confidence"] != expected_confidence or \
                int(row["size"]) != function["size"] or \
                len(body) != function["size"] or \
                hashlib.sha256(body).hexdigest() != function["sha256"]:
            raise AssertionError(
                f"R1 256...262-byte frontier changed: 0x{entry:08x}"
            )
    frontier_230_248_summary = summarize_r1_frontier_230_248(
        ROOT / "research/decompilation/rebuild/rebuilt-application.bin"
    )
    if frontier_230_248_summary["function_count"] != 17 or \
            frontier_230_248_summary["function_bytes"] != 1934 or \
            frontier_230_248_summary["inventory_bytes"] != 1928 or \
            frontier_230_248_summary["frontier_function_count"] != 5 or \
            frontier_230_248_summary["frontier_function_bytes"] != 1214 or \
            frontier_230_248_summary["frontier_inventory_bytes"] != 1208 or \
            frontier_230_248_summary["supporting_helper_count"] != 12 or \
            frontier_230_248_summary["supporting_helper_bytes"] != 720 or \
            frontier_230_248_summary["product_function_count"] != 3 or \
            frontier_230_248_summary["product_helper_count"] != 8 or \
            frontier_230_248_summary["gomore_function_count"] != 3 or \
            frontier_230_248_summary["shared_quantized_runtime_count"] != 3 or \
            any(frontier_230_248_summary["safety"].values()):
        raise AssertionError("R1 230...248-byte frontier metadata changed")
    for function in R1_FRONTIER_230_248_FUNCTIONS:
        function = apply_goodix_democode_attribution(function)
        entry = int(function["entry"])
        end = int(function["end_exclusive"])
        row = ownership_by_key[("application", f"0x{entry:08x}")]
        body = recovered[entry - recovered_base:end - recovered_base]
        expected_confidence = (
            "candidate"
            if function["provider_family"] ==
                "gomore_health_algorithm_candidate"
            else "high"
        )
        if row["inventory_source"] != function["inventory"] or \
                row["provider_family"] != function["provider_family"] or \
                row["source_disposition"] != function["source_disposition"] or \
                row["upstream_symbol"] != function["symbol"] or \
                row["confidence"] != expected_confidence or \
                int(row["size"]) != function["size"] or \
                len(body) != function["size"] or \
                hashlib.sha256(body).hexdigest() != function["sha256"]:
            raise AssertionError(
                f"R1 230...248-byte frontier changed: 0x{entry:08x}"
            )
    frontier_224_230_summary = summarize_r1_frontier_224_230(
        ROOT / "research/decompilation/rebuild/rebuilt-application.bin"
    )
    if frontier_224_230_summary["function_count"] != 8 or \
            frontier_224_230_summary["function_bytes"] != 1458 or \
            frontier_224_230_summary["frontier_function_count"] != 6 or \
            frontier_224_230_summary["frontier_function_bytes"] != 1360 or \
            frontier_224_230_summary["supporting_helper_count"] != 2 or \
            frontier_224_230_summary["supporting_helper_bytes"] != 98 or \
            frontier_224_230_summary["product_function_count"] != 4 or \
            frontier_224_230_summary["product_helper_count"] != 2 or \
            frontier_224_230_summary["nordic_function_count"] != 1 or \
            frontier_224_230_summary["shared_quantized_runtime_count"] != 1 or \
            any(frontier_224_230_summary["safety"].values()):
        raise AssertionError("R1 224...230-byte frontier metadata changed")
    for function in R1_FRONTIER_224_230_FUNCTIONS:
        function = apply_goodix_democode_attribution(function)
        entry = int(function["entry"])
        end = int(function["end_exclusive"])
        row = ownership_by_key[("application", f"0x{entry:08x}")]
        body = recovered[entry - recovered_base:end - recovered_base]
        if row["inventory_source"] != function["inventory"] or \
                row["provider_family"] != function["provider_family"] or \
                row["source_disposition"] != function["source_disposition"] or \
                row["upstream_symbol"] != function["symbol"] or \
                row["confidence"] != "high" or \
                int(row["size"]) != function["size"] or \
                len(body) != function["size"] or \
                hashlib.sha256(body).hexdigest() != function["sha256"]:
            raise AssertionError(
                f"R1 224...230-byte frontier changed: 0x{entry:08x}"
            )
    frontier_212_222_summary = summarize_r1_frontier_212_222(
        ROOT / "research/decompilation/rebuild/rebuilt-application.bin"
    )
    if frontier_212_222_summary["function_count"] != 7 or \
            frontier_212_222_summary["function_bytes"] != 1542 or \
            frontier_212_222_summary["inventory_bytes"] != 1524 or \
            frontier_212_222_summary["product_function_count"] != 2 or \
            frontier_212_222_summary["nordic_adapter_count"] != 2 or \
            frontier_212_222_summary["cmbacktrace_adapter_count"] != 1 or \
            frontier_212_222_summary["goodix_function_count"] != 1 or \
            frontier_212_222_summary["unknown_sensor_stream_count"] != 1 or \
            any(frontier_212_222_summary["safety"].values()):
        raise AssertionError("R1 212...222-byte frontier metadata changed")
    for function in R1_FRONTIER_212_222_FUNCTIONS:
        function = apply_goodix_democode_attribution(function)
        entry = int(function["entry"])
        end = int(function["end_exclusive"])
        row = ownership_by_key[("application", f"0x{entry:08x}")]
        body = recovered[entry - recovered_base:end - recovered_base]
        expected_confidence = (
            "candidate"
            if function["provider_family"] ==
                "unknown_sensor_stream_framework_candidate"
            else "high"
        )
        if row["inventory_source"] != function["inventory"] or \
                row["provider_family"] != function["provider_family"] or \
                row["source_disposition"] != function["source_disposition"] or \
                row["upstream_symbol"] != function["symbol"] or \
                row["confidence"] != expected_confidence or \
                int(row["size"]) != function["size"] or \
                len(body) != function["size"] or \
                hashlib.sha256(body).hexdigest() != function["sha256"]:
            raise AssertionError(
                f"R1 212...222-byte frontier changed: 0x{entry:08x}"
            )
    frontier_204_210_summary = summarize_r1_frontier_204_210(
        ROOT / "research/decompilation/rebuild/rebuilt-application.bin"
    )
    if frontier_204_210_summary["function_count"] != 5 or \
            frontier_204_210_summary["function_bytes"] != 1030 or \
            frontier_204_210_summary["product_function_count"] != 2 or \
            frontier_204_210_summary["nordic_adapter_count"] != 1 or \
            frontier_204_210_summary["storage_adapter_count"] != 1 or \
            frontier_204_210_summary["shared_tensor_count"] != 1 or \
            any(frontier_204_210_summary["safety"].values()):
        raise AssertionError("R1 204...210-byte frontier metadata changed")
    for function in R1_FRONTIER_204_210_FUNCTIONS:
        function = apply_goodix_democode_attribution(function)
        entry = int(function["entry"])
        end = int(function["end_exclusive"])
        row = ownership_by_key[("application", f"0x{entry:08x}")]
        body = recovered[entry - recovered_base:end - recovered_base]
        if row["inventory_source"] != function["inventory"] or \
                row["provider_family"] != function["provider_family"] or \
                row["source_disposition"] != function["source_disposition"] or \
                row["upstream_symbol"] != function["symbol"] or \
                row["confidence"] != "high" or \
                int(row["size"]) != function["size"] or \
                len(body) != function["size"] or \
                hashlib.sha256(body).hexdigest() != function["sha256"]:
            raise AssertionError(
                f"R1 204...210-byte frontier changed: 0x{entry:08x}"
            )
    frontier_128_202_summary = summarize_r1_frontier_128_202(
        ROOT / "research/decompilation/rebuild/rebuilt-application.bin"
    )
    if frontier_128_202_summary["function_count"] != 63 or \
            frontier_128_202_summary["function_bytes"] != 10126 or \
            frontier_128_202_summary["pinned_bytes"] != 9716 or \
            frontier_128_202_summary["omitted_bytes"] != 410 or \
            frontier_128_202_summary["product_function_count"] != 40 or \
            frontier_128_202_summary["nordic_function_count"] != 1 or \
            frontier_128_202_summary["gomore_function_count"] != 9 or \
            frontier_128_202_summary["goodix_function_count"] != 4 or \
            frontier_128_202_summary["yhm_function_count"] != 2 or \
            frontier_128_202_summary["time_calendar_function_count"] != 1 or \
            frontier_128_202_summary["device_registry_function_count"] != 2 or \
            frontier_128_202_summary["sensor_stream_function_count"] != 1 or \
            frontier_128_202_summary["quantized_runtime_function_count"] != 3 or \
            any(frontier_128_202_summary["safety"].values()):
        raise AssertionError("R1 128...202-byte frontier metadata changed")


    frontier_128_202_confidence = {
        "r1_product_specific": "high",
        "nordic_nrf5_sdk_17_1_0": "high",
        "gomore_health_algorithm_candidate": "candidate",
        "goodix_gh3x2x_candidate": "high",
        "yhmicros_yhm2710_candidate": "high",
        "unknown_time_calendar_provider_candidate": "candidate",
        "unknown_generic_device_registry_candidate": "candidate",
        "unknown_sensor_stream_framework_candidate": "candidate",
        "unknown_shared_quantized_neural_runtime_candidate": "high",
    }
    frontier_128_202_labels = {
        0x0005D244: "quantized_runtime_float_softmax_executor",
        0x00074AAC: "quantized_runtime_descriptor_constructor",
        0x00098EDC: "quantized_runtime_float_add_executor",
        0x0005DB14: "device_registry_name_task_insert",
        0x000734E8: "device_registry_module_enabled_scan",
        0x000896F0: "sensor_stream_object_create",
        0x0008AC28: "time_calendar_local_datetime_fill",
    }
    frontier_128_202_confidence[
        "goodix_gh3x2x_democode_v1_6_drvlib_v4_3_0_0"] = "high"
    for function in R1_FRONTIER_128_202_FUNCTIONS:
        entry = int(function["entry"])
        row = ownership_by_key[("application", f"0x{entry:08x}")]
        if entry in goodix_democode_symbols:
            democode_symbol, democode_confidence = goodix_democode_symbols[entry]
            expected_function = dict(function)
            expected_function["provider_family"] = \
                "goodix_gh3x2x_democode_v1_6_drvlib_v4_3_0_0"
            expected_function["source_disposition"] = "use_pinned_upstream"
        else:
            expected_function = function
        expected_symbol = frontier_128_202_labels.get(
            entry, expected_function["symbol"])
        if entry in goodix_democode_symbols:
            expected_symbol = goodix_democode_symbols[entry][0]
        if row["inventory_source"] != expected_function["inventory"] or \
                row["provider_family"] != expected_function["provider_family"] or \
                row["source_disposition"] != expected_function["source_disposition"] or \
                row["upstream_symbol"] != expected_symbol or \
                row["confidence"] != (goodix_democode_symbols[entry][1]
                    if entry in goodix_democode_symbols else
                    frontier_128_202_confidence[
                        expected_function["provider_family"]]) or \
                int(row["size"]) != expected_function["size"]:
            raise AssertionError(
                f"R1 128...202-byte frontier changed: 0x{entry:08x}"
            )
    frontier_128_202_confidence["arm_toolchain_runtime"] = "high"
    frontier_128_202_confidence[
        "freertos_10_5_1_nordic_nrf52_port"] = "high"
    frontier_128_202_confidence[
        "unknown_rtc_device_provider_candidate"] = "high"
    frontier_tier2 = (
        ("64...127", summarize_r1_frontier_64_127, R1_FRONTIER_64_127_FUNCTIONS,
         {"function_count": 150, "function_bytes": 13652,
          "pinned_bytes": 13344, "omitted_bytes": 308,
          "r1_function_count": 96, "nordic_function_count": 1,
          "toolchain_function_count": 1, "gomore_function_count": 28,
          "goodix_function_count": 11, "yhm_function_count": 2,
          "device_registry_function_count": 2,
          "sensor_stream_function_count": 6,
          "quantized_runtime_function_count": 3}),
        ("32...63", summarize_r1_frontier_32_63, R1_FRONTIER_32_63_FUNCTIONS,
         {"function_count": 151, "function_bytes": 6636,
          "pinned_bytes": 6468, "omitted_bytes": 168,
          "r1_function_count": 79, "gomore_function_count": 16,
          "goodix_function_count": 27, "time_calendar_function_count": 1,
          "device_registry_function_count": 13,
          "sensor_stream_function_count": 6,
          "quantized_runtime_function_count": 9}),
        ("sub-32", summarize_r1_frontier_sub32, R1_FRONTIER_LT32_FUNCTIONS,
         {"function_count": 268, "function_bytes": 4326,
          "pinned_bytes": 4282, "omitted_bytes": 44,
          "r1_function_count": 165, "nordic_function_count": 3,
          "toolchain_function_count": 2, "gomore_function_count": 19,
          "goodix_function_count": 21, "yhm_function_count": 14,
          "device_registry_function_count": 4,
          "sensor_stream_function_count": 15,
          "quantized_runtime_function_count": 4,
          "sensor_heap_function_count": 21}),
        ("final-53", summarize_r1_frontier_final53, R1_FRONTIER_FINAL53_FUNCTIONS,
         {"function_count": 53, "function_bytes": 1548,
          "pinned_bytes": 1406, "omitted_bytes": 142,
          "r1_function_count": 4, "nordic_function_count": 4,
          "freertos_function_count": 1, "gomore_function_count": 21,
          "goodix_function_count": 9,
          "device_registry_function_count": 10,
          "rtc_device_function_count": 3,
          "quantized_runtime_function_count": 1}),
    )
    for tier_name, tier_summarize, tier_functions, tier_expected in frontier_tier2:
        tier_summary = tier_summarize(
            ROOT / "research/decompilation/rebuild/rebuilt-application.bin"
        )
        if any(tier_summary[key] != value for key, value in
               tier_expected.items()) or \
                any(tier_summary["safety"].values()):
            raise AssertionError(
                f"R1 {tier_name}-byte frontier metadata changed")
        for function in tier_functions:
            entry = int(function["entry"])
            row = ownership_by_key[("application", f"0x{entry:08x}")]
            if entry in goodix_democode_symbols:
                democode_symbol, democode_confidence = goodix_democode_symbols[entry]
                expected_family = "goodix_gh3x2x_democode_v1_6_drvlib_v4_3_0_0"
                expected_disposition = "use_pinned_upstream"
                expected_confidence = democode_confidence
                expected_tier_symbol = democode_symbol
            elif entry in GOODIX_ADAPTER_GLUE_SYMBOLS:
                expected_family = "r1_goodix_provider_adapter"
                expected_disposition = "clean_room_adapter_only_use_licensed_provider"
                expected_confidence = frontier_128_202_confidence.get(
                    "r1_goodix_provider_adapter", "high")
                expected_tier_symbol = GOODIX_ADAPTER_GLUE_SYMBOLS[entry]
            elif entry in SENSOR_ALGORITHM_HEAP_ROUTING:
                # The sub-32 frontier census still records these bodies under
                # their historical heap-family label; the ownership ledger
                # routes them per the resolved Goodix goodix_mem/GdMem
                # provenance (or R1 integrator glue for the two local bodies).
                expected_family, expected_disposition, expected_confidence, _ = \
                    SENSOR_ALGORITHM_HEAP_ROUTING[entry]
            else:
                expected_family = function["provider_family"]
                expected_disposition = function["source_disposition"]
                expected_confidence = frontier_128_202_confidence[
                    function["provider_family"]]
            if row["inventory_source"] != function["inventory"] or \
                    row["provider_family"] != expected_family or \
                    row["source_disposition"] != expected_disposition or \
                    row["confidence"] != expected_confidence or \
                    int(row["size"]) != function["size"] or \
                    ((expected_tier_symbol if entry in goodix_democode_symbols
                      else function["symbol"]) and
                     row["upstream_symbol"] != (expected_tier_symbol
                     if entry in goodix_democode_symbols
                     else function["symbol"])):
                raise AssertionError(
                    f"R1 {tier_name}-byte frontier changed: 0x{entry:08x}"
                )
    delayed_timer_summary = summarize_r1_delayed_event_timer(
        ROOT / "research/decompilation/rebuild/rebuilt-application.bin"
    )
    if delayed_timer_summary["function_count"] != 1 or \
            delayed_timer_summary["function_bytes"] != 376 or \
            delayed_timer_summary["behavior"]["slot_count"] != 64 or \
            delayed_timer_summary["behavior"]["direct_elapsed_tag"] != \
                "0xff000000" or \
            not delayed_timer_summary["recovered_quirks"][
                "empty_table_requests_uint32_max_timer"] or \
            delayed_timer_summary["boundary"]["clean_room_api"] != \
                "r1_delayed_event_timer_step":
        raise AssertionError("R1 delayed-event timer metadata changed")
    for function in R1_DELAYED_EVENT_TIMER_FUNCTIONS:
        entry = int(function["entry"])
        end = int(function["end_exclusive"])
        row = ownership_by_key[("application", f"0x{entry:08x}")]
        body = recovered[entry - recovered_base:end - recovered_base]
        if row["inventory_source"] != function["inventory"] or \
                row["provider_family"] != "r1_product_specific" or \
                row["source_disposition"] != "clean_room_behavior_only" or \
                row["upstream_symbol"] != function["symbol"] or \
                row["confidence"] != "high" or \
                int(row["size"]) != function["size"] or \
                len(body) != function["size"] or \
                hashlib.sha256(body).hexdigest() != function["sha256"]:
            raise AssertionError(
                f"R1 delayed-event timer changed: 0x{entry:08x}"
            )
    pmic_charge_summary = summarize_r1_pmic_charge_event(
        ROOT / "research/decompilation/rebuild/rebuilt-application.bin"
    )
    if pmic_charge_summary["function_count"] != 1 or \
            pmic_charge_summary["function_bytes"] != 402 or \
            pmic_charge_summary["thermal_policy"] != {
                "zero": "no register change",
                "low_band": "1..14",
                "low_target_word": "0x40808312",
                "mid_band": "15..44",
                "mid_target_word": "0x4160f5c3",
                "high_band": "45..63",
                "high_register": "0x02",
                "high_value": "0xf8",
                "skip_equal_target": True,
            } or pmic_charge_summary["boundary"] != {
                "provider_family": "r1_product_specific",
                "source_disposition": "clean_room_behavior_only",
                "yhm_provider_reimplemented": False,
                "st_provider_reimplemented": False,
                "nordic_or_timer_provider_reimplemented": False,
            }:
        raise AssertionError("R1 PMIC charge-event metadata changed")
    for function in R1_PMIC_CHARGE_EVENT_FUNCTIONS:
        entry = int(function["entry"])
        end = int(function["end_exclusive"])
        row = ownership_by_key[("application", f"0x{entry:08x}")]
        body = recovered[entry - recovered_base:end - recovered_base]
        if row["inventory_source"] != function["inventory"] or \
                row["provider_family"] != "r1_product_specific" or \
                row["source_disposition"] != "clean_room_behavior_only" or \
                row["upstream_symbol"] != function["symbol"] or \
                row["confidence"] != "high" or \
                int(row["size"]) != function["size"] or \
                len(body) != function["size"] or \
                hashlib.sha256(body).hexdigest() != function["sha256"]:
            raise AssertionError(
                f"R1 PMIC charge-event function changed: 0x{entry:08x}"
            )
    pmic_charged_summary = summarize_r1_pmic_charged_notification(
        ROOT / "research/decompilation/rebuild/rebuilt-application.bin"
    )
    if pmic_charged_summary["function_count"] != 1 or \
            pmic_charged_summary["function_bytes"] != 374 or \
            pmic_charged_summary["retry_policy"][
                "largest_old_counter_retried"] != 12 or \
            not pmic_charged_summary["retry_policy"][
                "not_charging_retains_incremented_counter"] or \
            pmic_charged_summary["completion_policy"][
                "post_charge_delay_milliseconds"] != 5120 or \
            pmic_charged_summary["boundary"]["clean_room_api"] != \
                "r1_pmic_plan_charged_notification":
        raise AssertionError("R1 PMIC-charged notification metadata changed")
    for function in R1_PMIC_CHARGED_NOTIFICATION_FUNCTIONS:
        entry = int(function["entry"])
        row = ownership_by_key[("application", f"0x{entry:08x}")]
        body = b"".join(
            recovered[start - recovered_base:end - recovered_base]
            for start, end in function["ranges"]
        )
        if row["inventory_source"] != function["inventory"] or \
                row["provider_family"] != "r1_product_specific" or \
                row["source_disposition"] != "clean_room_behavior_only" or \
                row["upstream_symbol"] != function["symbol"] or \
                row["confidence"] != "high" or \
                int(row["size"]) != function["size"] or \
                len(body) != function["size"] or \
                hashlib.sha256(body).hexdigest() != function["sha256"]:
            raise AssertionError(
                f"R1 PMIC-charged notification changed: 0x{entry:08x}"
            )
    iqs_ati_summary = summarize_r1_iqs7211e_ati_audit(
        ROOT / "research/decompilation/rebuild/rebuilt-application.bin"
    )
    if iqs_ati_summary["function_count"] != 1 or \
            iqs_ati_summary["function_bytes"] != 372 or \
            iqs_ati_summary["behavior"]["later_interval_ticks"] != 10000 or \
            iqs_ati_summary["behavior"]["eight_by_three_channels"] != 24 or \
            iqs_ati_summary["boundary"]["provider_family"] != \
                "r1_product_specific":
        raise AssertionError("R1 IQS7211E ATI audit metadata changed")
    for function in R1_IQS7211E_ATI_AUDIT_FUNCTIONS:
        entry = int(function["entry"])
        end = int(function["end_exclusive"])
        row = ownership_by_key[("application", f"0x{entry:08x}")]
        body = recovered[entry - recovered_base:end - recovered_base]
        if row["provider_family"] != "r1_product_specific" or \
                row["source_disposition"] != "clean_room_behavior_only" or \
                row["upstream_symbol"] != function["symbol"] or \
                int(row["size"]) != function["size"] or \
                hashlib.sha256(body).hexdigest() != function["sha256"]:
            raise AssertionError(
                f"R1 IQS7211E ATI audit changed: 0x{entry:08x}"
            )
    validated_sleep_delivery_summary = summarize_r1_validated_sleep_delivery(
        ROOT / "research/decompilation/rebuild/rebuilt-application.bin",
        0x00027000,
    )
    if validated_sleep_delivery_summary["function_count"] != 3 or \
            validated_sleep_delivery_summary["function_bytes"] != 850 or \
            validated_sleep_delivery_summary["validated_sleep_delivery"] != {
                "initial_system_event": "0x000d",
                "initial_consumer": "0x0008dd90",
                "minimum_unsigned_duration_seconds": 3600,
                "storage_system_event": "0x2000",
                "storage_event_failure": "direct call to 0x0008dc94",
                "storage_consumer": "0x0008dc94",
                "storage_append": "0x0005b890",
                "length": "UInt16 wrapping addition of 32 and compact-stage count",
                "automatic_sync": "only after storage append returns nonzero",
                "automatic_sync_trigger_argument": 6,
            } or validated_sleep_delivery_summary["storage_append"] != {
                "initialized_flag_address": "0x200067b4",
                "maximum_payload_bytes": 3888,
                "write_attempts": 2,
                "no_writable_sector_uses_rollover": True,
                "two_failed_writes_call_reset_wrapper": "0x0005b2f8",
            } or validated_sleep_delivery_summary["boundary"] != {
                "provider_family": "r1_product_specific",
                "source_disposition": "clean_room_behavior_only",
                "event_and_logging_frameworks_external": True,
                "flash_access_through_bounded_local_store": True,
                "stock_destructive_reset_preserved": False,
            }:
        raise AssertionError("R1 validated-sleep delivery metadata changed")
    for function in R1_VALIDATED_SLEEP_DELIVERY_FUNCTIONS:
        entry = int(function["entry"])
        row = ownership_by_key[("application", f"0x{entry:08x}")]
        body = recovered[entry - recovered_base:
                         int(function["end_exclusive"]) - recovered_base]
        if row["inventory_source"] != function["inventory"] or \
                row["provider_family"] != function["provider_family"] or \
                row["source_disposition"] != function["source_disposition"] or \
                row["upstream_symbol"] != function["symbol"] or \
                row["confidence"] != "high" or \
                int(row["size"]) != function["size"] or \
                len(body) != function["size"] or \
                hashlib.sha256(body).hexdigest() != function["sha256"]:
            raise AssertionError(
                f"R1 validated-sleep delivery boundary changed: 0x{entry:08x}"
            )
    quantized_pooling_summary = summarize_r1_quantized_pooling_boundary(
        ROOT / "research/decompilation/rebuild/rebuilt-application.bin"
    )
    if quantized_pooling_summary["function_count"] != 1 or \
            quantized_pooling_summary["function_bytes"] != 434 or \
            quantized_pooling_summary["behavioral_census"] != {
                "signed_int8_input_and_output": True,
                "maximum_pooling_windows": [2, 4],
                "average_pooling_window": 3,
                "average_rounds_away_from_zero_at_half": True,
                "success_return": 0,
            } or quantized_pooling_summary["boundary"] != {
                "provider_family": "unknown_shared_quantized_neural_runtime_candidate",
                "source_disposition": "investigate_before_implementing",
                "shared_by_gomore_and_goodix_graphs": True,
                "attributable_source_identified": False,
                "local_reimplementation_authorized": False,
            } or quantized_pooling_summary["safety"] != {
                "static_parser_only": True,
                "neural_executor_exposed": False,
                "model_or_sensor_data_access": False,
            }:
        raise AssertionError("shared quantized-pooling boundary metadata changed")
    for function in QUANTIZED_POOLING_RUNTIME_FUNCTIONS:
        entry = int(function["entry"])
        row = ownership_by_key[("application", f"0x{entry:08x}")]
        body = recovered[entry - recovered_base:
                         int(function["end_exclusive"]) - recovered_base]
        if row["inventory_source"] != function["inventory"] or \
                row["provider_family"] != \
                "unknown_shared_quantized_neural_runtime_candidate" or \
                row["source_disposition"] != "investigate_before_implementing" or \
                row["upstream_symbol"] != function["symbol"] or \
                row["confidence"] != "high" or \
                int(row["size"]) != function["size"] or \
                len(body) != function["size"] or \
                hashlib.sha256(body).hexdigest() != function["sha256"]:
            raise AssertionError(
                f"shared quantized-pooling boundary changed: 0x{entry:08x}"
            )
    connection_role_summary = summarize_r1_connection_role_assignment(
        ROOT / "research/decompilation/rebuild/rebuilt-application.bin"
    )
    if connection_role_summary["function_count"] != 2 or \
            connection_role_summary["function_bytes"] != 860 or \
            connection_role_summary["behavior"]["invalid_handle"] != "0xffff" or \
            connection_role_summary["behavior"]["successful_assignment_publishes_role"] != [1, 2] or \
            connection_role_summary["behavior"]["stock_cross_role_assertion_preserved"]:
        raise AssertionError("R1 connection-role assignment metadata changed")
    for function in R1_CONNECTION_ROLE_ASSIGNMENT_FUNCTIONS:
        entry = int(function["entry"])
        row = ownership_by_key[("application", f"0x{entry:08x}")]
        body = recovered[entry - recovered_base:
                         int(function["end_exclusive"]) - recovered_base]
        if row["provider_family"] != "r1_product_specific" or \
                row["source_disposition"] != "clean_room_behavior_only" or \
                row["upstream_symbol"] != function["symbol"] or \
                int(row["size"]) != function["size"] or \
                hashlib.sha256(body).hexdigest() != function["sha256"]:
            raise AssertionError(
                f"R1 connection-role assignment changed: 0x{entry:08x}"
            )
    eus_rx_summary = summarize_r1_eus_rx_reassembly(
        ROOT / "research/decompilation/rebuild/rebuilt-application.bin"
    )
    if eus_rx_summary["function_count"] != 1 or \
            eus_rx_summary["function_bytes"] != 424 or \
            eus_rx_summary["wire_contract"]["header_bytes"] != 5 or \
            eus_rx_summary["wire_contract"]["payload_bytes_per_full_fragment"] != 239 or \
            eus_rx_summary["wire_contract"]["maximum_sequence"] != 16 or \
            eus_rx_summary["wire_contract"]["maximum_inbound_logical_bytes"] != 4063 or \
            eus_rx_summary["clean_room_behavior"]["bounded_per_link_storage"] is not True or \
            eus_rx_summary["clean_room_behavior"]["duplicate_fragment_rejected"] is not True or \
            eus_rx_summary["clean_room_behavior"][
                "stock_malformed_train_acceptance_preserved"] is not False or \
            eus_rx_summary["boundary"]["provider_family"] != "r1_product_specific" or \
            eus_rx_summary["boundary"]["source_disposition"] != \
            "clean_room_behavior_only_security_preserving":
        raise AssertionError("R1 EUS receive reassembly metadata changed")
    for function in R1_EUS_RX_REASSEMBLY_FUNCTIONS:
        entry = int(function["entry"])
        end = int(function["end_exclusive"])
        row = ownership_by_key[("application", f"0x{entry:08x}")]
        body = recovered[entry - recovered_base:end - recovered_base]
        if row["provider_family"] != "r1_product_specific" or \
                row["source_disposition"] != \
                "clean_room_behavior_only_security_preserving" or \
                row["upstream_symbol"] != function["symbol"] or \
                row["confidence"] != "high" or \
                int(row["size"]) != function["size"] or \
                len(body) != function["size"] or \
                hashlib.sha256(body).hexdigest() != function["sha256"]:
            raise AssertionError(f"R1 EUS receive reassembly changed: 0x{entry:08x}")
    bae8_router_summary = summarize_r1_bae8_event_router(
        ROOT / "research/decompilation/rebuild/rebuilt-application.bin"
    )
    if bae8_router_summary["function_count"] != 1 or \
            bae8_router_summary["function_bytes"] != 418 or \
            bae8_router_summary["registration"]["callback_pointer_address"] != \
            "0x0004e6e4" or \
            bae8_router_summary["registration"]["callback_thumb_pointer"] != \
            "0x0005d5e1" or \
            bae8_router_summary["registration"]["direct_callers_expected"] != 0 or \
            bae8_router_summary["event_routes"]["3"] != \
            "EUS receive reassembly at 0x00032198" or \
            bae8_router_summary["clean_room_behavior"][
                "provider_operations_executed_by_planner"] is not False or \
            bae8_router_summary["dependencies"][
                "dependency_implementations_admitted"] is not False or \
            bae8_router_summary["boundary"]["provider_family"] != \
            "r1_product_specific" or \
            bae8_router_summary["boundary"]["source_disposition"] != \
            "clean_room_behavior_only":
        raise AssertionError("R1 BAE8 event-router metadata changed")
    for function in R1_BAE8_EVENT_ROUTER_FUNCTIONS:
        entry = int(function["entry"])
        end = int(function["end_exclusive"])
        row = ownership_by_key[("application", f"0x{entry:08x}")]
        body = recovered[entry - recovered_base:end - recovered_base]
        if row["provider_family"] != "r1_product_specific" or \
                row["source_disposition"] != "clean_room_behavior_only" or \
                row["upstream_symbol"] != function["symbol"] or \
                row["confidence"] != "high" or \
                int(row["size"]) != function["size"] or \
                len(body) != function["size"] or \
                hashlib.sha256(body).hexdigest() != function["sha256"]:
            raise AssertionError(f"R1 BAE8 event router changed: 0x{entry:08x}")
    ble_tx_queue_summary = summarize_r1_ble_tx_queue_dispatch(
        ROOT / "research/decompilation/rebuild/rebuilt-application.bin"
    )
    if ble_tx_queue_summary["function_count"] != 2 or \
            ble_tx_queue_summary["function_bytes"] != 560 or \
            ble_tx_queue_summary["message_envelope"] != {
                "message_id_offset": 0,
                "dispatch_type_offset": 4,
                "payload_length_offset": 8,
                "payload_offset": 12,
                "allocation_size_formula": "align4(payload_length + 15)",
                "known_veneer_dispatch_types": [0, 2],
            } or \
            ble_tx_queue_summary["queue_policy"] != {
                "near_full_threshold_percent": 90,
                "put_priority": 0,
                "put_timeout_raw": 100,
                "worker_signal_flag": 1,
                "free_envelope_on_put_failure": True,
                "return_success": 0,
                "return_failure": -1,
            } or \
            ble_tx_queue_summary["boundary"]["provider_family"] != \
            "r1_product_specific" or \
            ble_tx_queue_summary["boundary"]["source_disposition"] != \
            "clean_room_behavior_only" or \
            ble_tx_queue_summary["boundary"][
                "third_party_implementation_identified"] is not False or \
            any(ble_tx_queue_summary["boundary"][key] is not False for key in (
                "freertos_heap_reimplemented",
                "cmsis_queue_or_thread_flags_reimplemented",
                "toolchain_memmove_reimplemented",
                "nordic_logging_reimplemented",
                "ble_transport_worker_reimplemented",
                "connection_handle_accessors_admitted",
            )) or \
            ble_tx_queue_summary["safety"] != {
                "static_parser_only": True,
                "live_ble_sender_exposed": False,
                "private_payload_content_read": False,
            }:
        raise AssertionError("R1 BLE TX queue metadata changed")
    for function in R1_BLE_TX_QUEUE_FUNCTIONS:
        entry = int(function["entry"])
        row = ownership_by_key[("application", f"0x{entry:08x}")]
        body = b"".join(
            recovered[start - recovered_base:end - recovered_base]
            for start, end in function["segments"]
        )
        if row["inventory_source"] != function["inventory"] or \
                row["provider_family"] != "r1_product_specific" or \
                row["source_disposition"] != "clean_room_behavior_only" or \
                row["upstream_symbol"] != function["symbol"] or \
                row["confidence"] != "high" or \
                int(row["size"]) != function["size"] or \
                len(body) != function["size"] or \
                hashlib.sha256(body).hexdigest() != function["sha256"]:
            raise AssertionError(
                f"R1 BLE TX queue closure changed: 0x{entry:08x}"
            )
    ble_helper_summary = summarize_nordic_ble_static_helpers(
        ROOT / "research/decompilation/rebuild/rebuilt-application.bin")
    if ble_helper_summary["function_count"] != 5 or \
            ble_helper_summary["function_bytes"] != 158 or \
            ble_helper_summary["extent_bytes"] != 164:
        raise AssertionError("Nordic BLE static-helper census changed")
    for function in NORDIC_BLE_STATIC_HELPER_FUNCTIONS:
        entry = int(function["entry"])
        row = ownership_by_key[("application", f"0x{entry:08x}")]
        end = int(function["end_exclusive"])
        body = recovered[entry - recovered_base:end - recovered_base]
        if row["provider_family"] != "nordic_nrf5_sdk_17_1_0" or \
                row["source_disposition"] != "use_nordic_sdk" or \
                row["upstream_symbol"] != function["symbol"] or \
                row["confidence"] != "high" or \
                int(row["size"]) != function["size"] or \
                hashlib.sha256(body).hexdigest() != function["sha256"]:
            raise AssertionError(f"Nordic BLE static-helper closure changed: 0x{entry:08x}")
    nordic_expected = {
        "0x000272b8": "nrf_atfifo_wspace_req",
        "0x000272f0": "nrf_atfifo_wspace_close",
        "0x00027302": "nrf_atfifo_rspace_req",
        "0x0002733c": "nrf_atfifo_rspace_close",
        "0x0002734e": "nrf_atfifo_space_clear",
        "0x00027380": "nrf_atomic_internal_mov",
        "0x00027398": "nrf_atomic_internal_orr",
        "0x000273b2": "nrf_atomic_internal_and",
        "0x000273cc": "nrf_atomic_internal_eor",
        "0x000273e6": "nrf_atomic_internal_add",
        "0x00027400": "nrf_atomic_internal_sub",
        "0x0002741a": "nrf_atomic_internal_cmp_exch",
        "0x00027444": "nrf_atomic_internal_sub_hs",
        "0x00027488": "Reset_Handler",
        "0x0002749c": "NMI_Handler",
        "0x000274a2": "Default_Handler",
        "0x000309dc": "nrfx_pdm_irq_handler",
        "0x000317cc": "nrfx_saadc_irq_handler",
        "0x00033364": "SystemInit",
        "0x0007ca7c": "nvmc_config",
        "0x00098dc0": "xfer_completeness_check",
        "0x00074f20": "link_init",
        "0x00087a94": "ram_end_address_get",
        "0x00087aac": "rank_highest",
        "0x00087ac8": "rank_vars_update",
        "0x0008ee0a": "set_security_req",
        "0x0006edfc": "gscm_local_db_cache_apply",
        "0x0006f118": "gscm_service_changed_ind_send",
        "0x00075a08": "local_db_apply_in_evt",
        "0x00091084": "store_car_value",
        "0x0006edcc": "gscm_db_change_notification_done",
        "0x0006ede8": "internal_state_reset",
        "0x0006f0f8": "gscm_service_changed_ind_needed",
        "0x00075b10": "local_db_update",
        "0x0008a928": "service_changed_pending_flags_check",
        "0x00094ab0": "update_pending_flags_check",
        "0x00037530": "__NVIC_ClearPendingIRQ",
        "0x00031a74": "nrfx_twim_0_irq_handler",
        "0x00031a84": "nrfx_twim_1_irq_handler",
        "0x00031a94": "nrfx_spim_2_irq_handler",
        "0x00038166": "__NVIC_ClearPendingIRQ",
        "0x00038180": "__NVIC_SystemReset",
        "0x000381c8": "__NVIC_SystemReset",
        "0x0004826c": "active_flag_count",
        "0x0004898c": "addr_compare",
        "0x000489b2": "addr_is_aligned32",
        "0x000489be": "addr_is_within_bounds",
        "0x00048cd0": "ah",
        "0x0004fb6c": "auth_status_success_process",
        "0x00051440": "bcs_internal_state_reset",
        "0x000514e0": "blcm_link_ctx_get",
        "0x00051528": "ble_advdata_encode",
        "0x000516aa": "ble_advdata_parse",
        "0x000516ca": "ble_advdata_search",
        "0x00051e04": "ble_conn_state_conn_idx",
        "0x00051e18": "ble_conn_state_encrypted",
        "0x00051e38": "ble_conn_state_for_each_connected",
        "0x00051e4c": "ble_conn_state_for_each_set_user_flag",
        "0x00051e78": "ble_conn_state_init",
        "0x00051e7c": "ble_conn_state_lesc",
        "0x00051e9c": "ble_conn_state_mitm_protected",
        "0x00051ebc": "ble_conn_state_peripheral_conn_count",
        "0x00051edc": "ble_conn_state_role",
        "0x00051f00": "ble_conn_state_status",
        "0x00051f24": "ble_conn_state_user_flag_acquire",
        "0x00051f3c": "ble_conn_state_user_flag_get",
        "0x00051f6c": "ble_conn_state_user_flag_set",
        "0x00051fa4": "ble_conn_state_valid",
        "0x00051fb8": "ble_device_addr_encode",
        "0x00052018": "ble_dfu_buttonless_async_svci_init",
        "0x0005380c": "ble_evt_handler",
        "0x00053924": "ble_evt_handler",
        "0x000539a8": "ble_srv_is_indication_enabled",
        "0x000539b0": "ble_srv_is_notification_enabled",
        "0x0007b470": "nrfx_wdt_channel_alloc",
        "0x0007b508": "nrfx_wdt_channel_feed",
        "0x0007b520": "nrfx_wdt_enable",
        "0x0007b570": "nrfx_wdt_init",
        "0x0007b448": "nrfx_twim_xfer",
        "0x0007ad6c": "nrfx_rtc_init",
        "0x000566ac": "buf_prealloc",
        "0x00056774": "buffer_is_empty",
        "0x000578cc": "car_update_needed",
        "0x000579a8": "characteristic_add",
        "0x00058218": "claim",
        "0x00059ba0": "conn_handle_list_get",
        "0x00059bde": "conn_int_encode",
        "0x00059c68": "conn_sec_failure",
        "0x0005a65c": "data_length_update",
        "0x0005c110": "delete_execute",
        "0x0005ccfc": "dropped_sat16_get",
        "0x0005d314": "encryption_failure",
        "0x0005d514": "erase",
        "0x0005e5b0": "event_prepare",
        "0x0005e624": "event_send",
        "0x0005e644": "event_send",
        "0x0005ec88": "evt_send",
        "0x0005eca4": "evt_send",
        "0x0005ecc0": "evt_send",
        "0x0005ecec": "evt_send",
        "0x00063e30": "fds_file_delete",
        "0x00063e78": "fds_gc",
        "0x00063eb8": "fds_init",
        "0x00063fa4": "fds_record_close",
        "0x00063fec": "fds_record_find",
        "0x00063ffa": "fds_record_find_by_key",
        "0x0006400a": "fds_record_find_in_file",
        "0x0006401a": "fds_record_id_from_desc",
        "0x0006402c": "fds_record_open",
        "0x00064078": "fds_record_update",
        "0x00064088": "fds_record_write",
        "0x00064090": "fds_register",
        "0x000640c0": "fds_stat",
        "0x00064160": "record_key_within_pm_range",
        "0x00064eec": "flag_id_init",
        "0x00064efe": "flag_id_init",
        "0x00064f10": "flag_toggle",
        "0x00065094": "for_each_set_flag",
        "0x00066d24": "gc_execute",
        "0x00066e88": "gc_state_advance",
        "0x00066ef8": "gc_swap_pages",
        "0x00066f28": "gcm_ble_evt_handler",
        "0x000672e0": "gcm_im_evt_handler",
        "0x0006731c": "gcm_init",
        "0x0006eeb4": "gscm_local_db_cache_update",
        "0x0006fe60": "header_check",
        "0x0006fe8c": "header_has_next",
        "0x00070c1c": "im_address_resolve",
        "0x00070c64": "im_ble_addr_get",
        "0x00070c9c": "im_ble_evt_handler",
        "0x00070d78": "im_conn_handle_get",
        "0x00070db8": "im_find_duplicate_bonding_data",
        "0x00070df0": "im_is_duplicate_bonding_data",
        "0x00070e62": "im_master_id_is_valid",
        "0x00070e7a": "im_master_ids_compare",
        "0x00070ea4": "im_new_peer_id",
        "0x00070eb8": "im_peer_free",
        "0x00070ee4": "im_peer_id_get_by_conn_handle",
        "0x00070f08": "im_peer_id_get_by_master_id",
        "0x000710a0": "init",
        "0x000720f0": "init_execute",
        "0x00072848": "invalid_packets_omit",
        "0x00072b70": "is_busy",
        "0x00072bbe": "is_word_aligned",
        "0x00072baa": "is_valid_irk",
        "0x00075b20": "local_db_update_in_evt",
        "0x00075ce4": "log_skip",
        "0x00076088": "manuf_specific_data_encode",
        "0x00076178": "memobj_op",
        "0x000765dc": "mutex_lock_status_get",
        "0x000770bc": "name_encode",
        "0x000771e2": "next_id_get",
        "0x00077f30": "nrf_atfifo_clear",
        "0x00077f40": "nrf_atfifo_init",
        "0x00077f66": "nrf_atfifo_item_alloc",
        "0x00077f7c": "nrf_atfifo_item_free",
        "0x00077f92": "nrf_atfifo_item_get",
        "0x00077fa8": "nrf_atfifo_item_put",
        "0x00077fbe": "nrf_atflags_clear",
        "0x00077fd4": "nrf_atflags_fetch_set",
        "0x00077ff4": "nrf_atflags_find_and_set_flag",
        "0x0007803e": "nrf_atflags_get",
        "0x00078054": "nrf_atflags_set",
        "0x00078068": "nrf_atomic_flag_clear_fetch",
        "0x0007806e": "nrf_atomic_flag_set",
        "0x00078074": "nrf_atomic_flag_set_fetch",
        "0x0007807a": "nrf_atomic_u32_add",
        "0x00078086": "nrf_atomic_u32_and",
        "0x00078092": "nrf_atomic_u32_fetch_add",
        "0x000780a6": "nrf_atomic_u32_fetch_or",
        "0x000780b0": "nrf_atomic_u32_fetch_store",
        "0x000780c6": "nrf_atomic_u32_sub",
        "0x000780d2": "nrf_balloc_alloc",
        "0x00078116": "nrf_balloc_free",
        "0x00078146": "nrf_balloc_init",
        "0x00078186": "nrf_ble_gatt_init",
        "0x000781b4": "nrf_ble_gatt_on_ble_evt",
        "0x000783b6": "nrf_ble_qwr_init",
        "0x000783da": "nrf_ble_qwr_on_ble_evt",
        "0x00078590": "nrf_dfu_svci_vector_table_set",
        "0x00078c4c": "nrf_fstorage_erase",
        "0x00078c78": "nrf_fstorage_init",
        "0x00078c80": "nrf_fstorage_is_busy",
        "0x00078cd0": "nrf_fstorage_sdh_req_handler",
        "0x00078ce8": "nrf_fstorage_sdh_state_handler",
        "0x00078d08": "nrf_fstorage_sys_evt_handler",
        "0x00078dac": "nrf_fstorage_write",
        "0x00078a40": "nrf_fprintf",
        "0x00078a5a": "nrf_fprintf_buffer_flush",
        "0x00079520": "nrf_log_backend_add",
        "0x00079576": "nrf_log_backend_rtt_init",
        "0x00079598": "nrf_log_backend_serial_put",
        "0x0007965c": "nrf_log_color_id_get",
        "0x0007968c": "nrf_log_default_backends_init",
        "0x000796a8": "nrf_log_frontend_dequeue",
        "0x00079918": "nrf_log_frontend_hexdump",
        "0x000799c0": "nrf_log_frontend_std_0",
        "0x000799c8": "nrf_log_frontend_std_1",
        "0x000799d6": "nrf_log_frontend_std_2",
        "0x000799e6": "nrf_log_frontend_std_3",
        "0x000799f8": "nrf_log_frontend_std_4",
        "0x00079a0c": "nrf_log_frontend_std_5",
        "0x00079a28": "nrf_log_frontend_std_6",
        "0x00079a44": "nrf_log_hexdump_entry_process",
        "0x00079af4": "nrf_log_init",
        "0x00079b1c": "nrf_log_panic",
        "0x00079b48": "nrf_log_std_entry_process",
        "0x00079bfe": "nrf_memobj_alloc",
        "0x00079c5e": "nrf_memobj_free",
        "0x00079c90": "nrf_memobj_get",
        "0x00079c98": "nrf_memobj_pool_init",
        "0x00079c9c": "nrf_memobj_put",
        "0x00079cba": "nrf_memobj_read",
        "0x00079cca": "nrf_memobj_write",
        "0x00079dcc": "nrf_ringbuf_init",
        "0x00079e58": "nrf_sdh_ble_app_ram_start_get",
        "0x00079e6c": "nrf_sdh_ble_default_cfg_set",
        "0x0007a0ec": "nrf_sdh_ble_enable",
        "0x0007a38c": "nrf_sdh_ble_evts_poll",
        "0x0007a3ec": "nrf_sdh_disable_request",
        "0x0007a440": "nrf_sdh_enable_request",
        "0x0007a4b4": "nrf_sdh_evts_poll",
        "0x0007a4d8": "nrf_sdh_is_enabled",
        "0x0007a4e4": "nrf_sdh_request_continue",
        "0x0007a500": "nrf_sdh_soc_evts_poll",
        "0x0007a53c": "nrf_section_iter_init",
        "0x0007a56a": "nrf_section_iter_next",
        "0x0007a594": "nrf_strerror_find",
        "0x0007a5cc": "nrf_strerror_get",
        "0x0007ce34": "on_exchange_mtu_request_evt",
        "0x0007e0d4": "page_identify",
        "0x0007e0f8": "page_offsets_update",
        "0x0007e114": "page_scan",
        "0x0007e180": "page_tag_write_data",
        "0x0007e19c": "page_tag_write_swap",
        "0x0007e1c0": "pages_init",
        "0x0007e3d8": "params_req_send",
        "0x0005ed08": "evt_send",
        "0x0007e3f8": "pdb_evt_send",
        "0x0007e414": "pdb_init",
        "0x0007e574": "pdb_peer_data_ptr_get",
        "0x0007e57c": "pdb_peer_free",
        "0x0007e678": "pdb_write_buf_get",
        "0x0007e77c": "pdb_write_buf_release",
        "0x0007e790": "pdb_write_buf_store",
        "0x0007e7c8": "pds_evt_send",
        "0x0007e7d8": "pds_init",
        "0x0007e90c": "pds_next_deleted_peer_id_get",
        "0x0007e910": "pds_next_peer_id_get",
        "0x0007e914": "pds_peer_data_iterate",
        "0x0007e96c": "pds_peer_data_iterate_prepare",
        "0x0007e97c": "pds_peer_data_read",
        "0x0007e9f0": "pds_peer_data_store",
        "0x0007ead4": "pds_peer_id_allocate",
        "0x0007eadc": "pds_peer_id_free",
        "0x0007eaf2": "pds_peer_id_is_allocated",
        "0x0007eb30": "peer_data_delete_process",
        "0x0007ec04": "peer_data_find",
        "0x0007ec34": "peer_data_id_is_valid",
        "0x0007ec58": "peer_data_point_to_buffer",
        "0x0007ec74": "peer_id_allocate",
        "0x0007ec80": "peer_id_delete",
        "0x0007eca4": "peer_id_free",
        "0x0007ecc0": "peer_id_get_next_deleted",
        "0x0007eccc": "peer_id_get_next_used",
        "0x0007ecfc": "peer_id_init",
        "0x0007ed08": "peer_id_is_allocated",
        "0x0007ed1c": "peer_id_is_deleted",
        "0x0007f194": "pm_buffer_block_acquire",
        "0x0007f1f8": "pm_buffer_init",
        "0x0007f21c": "pm_buffer_ptr_get",
        "0x0007f244": "pm_buffer_release",
        "0x0007fa5c": "pm_handler_flash_clean",
        "0x0007fde4": "pm_handler_on_pm_evt",
        "0x0007fe74": "pm_handler_pm_evt_log",
        "0x0008056c": "pm_im_evt_handler",
        "0x00080570": "pm_init",
        "0x000813e0": "postfix_process",
        "0x0008743c": "queue_buf_get",
        "0x00087458": "queue_buf_store",
        "0x00087468": "queue_free",
        "0x0008747c": "queue_process",
        "0x00087520": "queue_process",
        "0x000875c0": "queue_start",
        "0x000875dc": "queue_start",
        "0x00087b20": "read",
        "0x00087f20": "record_find",
        "0x00087fb0": "record_find_by_desc",
        "0x00088050": "record_find_next",
        "0x000880ac": "record_header_flag_dirty",
        "0x000880e8": "records_stat",
        "0x000883f8": "rmap",
        "0x000881e4": "release",
        "0x000890cc": "service_changed_send_in_evt",
        "0x00089148": "sdh_request_observer_notify",
        "0x00089178": "sdh_state_observer_notify",
        "0x000892f4": "sec_keyset_fill",
        "0x000894c0": "sec_params_verify",
        "0x00089538": "sec_proc_start",
        "0x00090308": "sm_ble_evt_handler",
        "0x00090334": "smd_conn_sec_config_reply",
        "0x00090338": "sm_conn_sec_status_get",
        "0x000903dc": "sm_init",
        "0x0009045c": "sm_link_secure",
        "0x00090468": "sm_pdb_evt_handler",
        "0x000904ac": "sm_sec_is_sufficient",
        "0x000904d4": "sm_sec_params_set",
        "0x00090534": "smd_ble_evt_handler",
        "0x00090638": "smd_init",
        "0x00090fec": "std_n",
        "0x0008aba0": "service_data_encode",
        "0x00093ea2": "uint16_encode",
        "0x00093ec4": "uninit",
        "0x00094e30": "user_flag_is_acquired",
        "0x00095114": "user_mem_reply",
        "0x00095540": "uuid_list_encode",
        "0x00095570": "uuid_list_sized_encode",
        "0x00096e08": "wmap",
        "0x00096fe0": "write",
        "0x00097030": "write_buf_store",
        "0x00097214": "write_buf_store_in_event",
        "0x000972b4": "write_buffer_record_find",
        "0x000972e8": "write_buffer_record_find_next",
        "0x00097318": "write_buffer_record_invalidate",
        "0x00097334": "write_buffer_record_release",
        "0x00097360": "write_enqueue",
        "0x00097454": "write_execute",
        "0x000975c4": "write_space_free",
        "0x000975dc": "write_space_reserve",
    }
    for symbol, entries in gpio_groups.items():
        for entry in entries:
            nordic_expected[f"0x{entry:08x}"] = symbol
    for entry, (symbol, _) in gpiote_expected.items():
        nordic_expected[f"0x{entry:08x}"] = symbol
    for entry, (symbol, _, _) in hal_inline_expected.items():
        nordic_expected[f"0x{entry:08x}"] = symbol
    for entry, (symbol, _, _) in clock_driver_expected.items():
        nordic_expected[f"0x{entry:08x}"] = symbol
    for entry, (symbol, _, _) in delay_twi_expected.items():
        nordic_expected[f"0x{entry:08x}"] = symbol
    for entry, (symbol, _, _) in gpiote_driver_expected.items():
        nordic_expected[f"0x{entry:08x}"] = symbol
    for entry, (symbol, _, _) in gpiote_driver_hash_expected.items():
        nordic_expected[f"0x{entry:08x}"] = symbol
    nordic_expected["0x000789e4"] = "nrf_drv_twi_init"
    nordic_expected["0x00072a32"] = "irq_handler"
    nordic_expected["0x00087ed0"] = "reattempt_previous_operations"
    nordic_expected["0x00030ca8"] = "nrfx_pwm_0_irq_handler"
    nordic_expected["0x00030cb8"] = "nrfx_pwm_1_irq_handler"
    nordic_expected["0x00030cc8"] = "nrfx_pwm_2_irq_handler"
    nordic_expected["0x00093960"] = "twi_evt_handler"
    nordic_expected["0x0005c034"] = "db_update_pending_handle"
    nordic_expected["0x00034a7c"] = "nrfx_wdt_irq_handler"
    nordic_expected["0x00034410"] = "nrfx_prs_box_4_irq_handler"
    for entry, (symbol, _, _) in twi_driver_expected.items():
        nordic_expected[f"0x{entry:08x}"] = symbol
    for entry, (symbol, _, _) in rtc_timer_driver_expected.items():
        nordic_expected[f"0x{entry:08x}"] = symbol
    for entry, (symbol, _, _) in rtc_timer_irq_expected.items():
        nordic_expected[f"0x{entry:08x}"] = symbol
    nordic_expected["0x0003060c"] = "nrfx_nfct_irq_handler"
    for entry, (symbol, _, _) in nfct_driver_expected.items():
        nordic_expected[f"0x{entry:08x}"] = symbol
    nordic_expected.update({
        "0x0007aeac": "nrfx_saadc_channel_init",
        "0x0007af38": "nrfx_saadc_channel_uninit",
        "0x0007af7c": "nrfx_saadc_init",
        "0x0007b010": "nrfx_saadc_limits_set",
        "0x0007b090": "nrfx_saadc_sample_convert",
        "0x0007b150": "nrfx_saadc_uninit",
    })
    nordic_expected.update({
        "0x0007f276": "pm_conn_sec_config_reply",
        "0x0007f280": "pm_conn_sec_status_get",
        "0x0007f294": "pm_conn_secure",
        "0x00080980": "pm_pdb_evt_handler",
        "0x00080a98": "pm_peer_data_bonding_load",
        "0x00080aac": "pm_peer_data_load",
        "0x00080ad4": "pm_peer_delete",
        "0x00080ae8": "pm_peer_rank_highest",
        "0x00080c38": "pm_peer_ranks_get",
        "0x00080d5c": "pm_peers_delete",
        "0x00080e28": "pm_register",
        "0x00080e54": "pm_sec_params_set",
        "0x00080e68": "pm_sm_evt_handler",
        "0x0007e2f0": "pairing",
        "0x0004c6d0": "allow_repairing",
        "0x00074f38": "link_secure",
        "0x00075074": "link_secure_pending_handle",
        "0x00075038": "link_secure_failure",
        "0x0005eb94": "events_send_from_err_code",
        "0x00064f44": "flags_set_from_err_code",
        "0x0007719c": "new_context_get",
        "0x000771b0": "new_evt",
        "0x0007e3a4": "pairing_success_evt_send",
        "0x000891b8": "sec_info_request_process",
        "0x00089598": "sec_req_process",
        "0x0008965a": "send_config_req",
        "0x000896a0": "send_unexpected_error",
        "0x000896c8": "send_unexpected_error",
        "0x000906c8": "smd_link_secure",
        "0x000906f0": "smd_params_reply",
    })
    for function in NORDIC_ADVERTISING_FUNCTIONS:
        nordic_expected[f"0x{int(function['entry']):08x}"] = \
            str(function["symbol"])
    for function in NORDIC_BUTTONLESS_DFU_FUNCTIONS:
        nordic_expected[f"0x{int(function['entry']):08x}"] = \
            str(function["symbol"])
    for function in NORDIC_POWER_MANAGEMENT_FUNCTIONS:
        nordic_expected[f"0x{int(function['entry']):08x}"] = \
            str(function["symbol"])
    for entry, symbol in nordic_expected.items():
        row = ownership_by_key[("application", entry)]
        if row["provider_family"] != "nordic_nrf5_sdk_17_1_0" or \
                row["source_disposition"] != "use_nordic_sdk" or \
                row["upstream_symbol"] != symbol:
            raise AssertionError(f"Nordic provider function not source-routed: {entry}")
    if recovered_function(0x00037530) != recovered_function(0x00038166) or \
            len(recovered_function(0x00037530)) != 26 or \
            hashlib.sha256(recovered_function(0x00037530)).hexdigest() != \
            "80bb4d1eb778898e7ded5175ad7f5df44002ce265fe35a77b0f7a375daacb93c":
        raise AssertionError("CMSIS __NVIC_ClearPendingIRQ duplicate body changed")
    peer_database_exact_expected = {
        0x00097030: ("write_buf_store", 296, "ec130f7427b26145801164220f7b2df9a2f9f125a55130ad386476a6dd5bb950"),
        0x00097214: ("write_buf_store_in_event", 144, "65d17e552602e9d36b7bf5a7fd59bdd09b39046eccdf4a499318135ad67b2870"),
        0x000972B4: ("write_buffer_record_find", 52, "cb15be126dd2d167e341d03dd91a8105a120be104b5b7463b2072052aeaaf020"),
        0x000972E8: ("write_buffer_record_find_next", 42, "7319c08a0df9f0702c6aabbe968b990b8979befaaaa51000ba4dd25b2929c83a"),
        0x00097318: ("write_buffer_record_invalidate", 28, "9f98c66762e39676a78014d03f4673e402c9aa536883b924a00c21e03d254e45"),
        0x00097334: ("write_buffer_record_release", 38, "7a21b8bdf8fc9f85708b50840d38fe7deca5e0428d61a26d2279bc6e13852bb8"),
    }
    for entry, (symbol, size, digest) in peer_database_exact_expected.items():
        row = ownership_by_key[("application", f"0x{entry:08x}")]
        body = recovered_function(entry)
        if row["upstream_symbol"] != symbol or \
                "components/ble/peer_manager/peer_database.c" not in row["evidence"] or \
                len(body) != size or hashlib.sha256(body).hexdigest() != digest:
            raise AssertionError(f"Nordic peer-database exact function mismatch: 0x{entry:08x}")
    gatt_cache_exact_expected = {
        0x000578CC: (
            "car_update_needed", 36,
            "ed2dcdc6d6b7d62a46a2d0a09e2827514f8cbbdb6c6f11fcbc8083c2b21e7f55",
        ),
    }
    for entry, (symbol, size, digest) in gatt_cache_exact_expected.items():
        row = ownership_by_key[("application", f"0x{entry:08x}")]
        body = recovered_function(entry)
        if row["upstream_symbol"] != symbol or \
                "components/ble/peer_manager/gatt_cache_manager.c" not in row["evidence"] or \
                len(body) != size or hashlib.sha256(body).hexdigest() != digest:
            raise AssertionError(f"Nordic GATT-cache exact function mismatch: 0x{entry:08x}")
    qwr_exact_expected = {
        0x000783B6: ("nrf_ble_qwr_init", 36, "24503fa8e4d84772dca55732d75d983395207f4428640ac1f30e217719f6629a"),
        0x000783DA: ("nrf_ble_qwr_on_ble_evt", 182, "eac84d4736b8b6e2cbe9c364db3dced3e07f097cd33a2a760320d14427bcbb0e"),
        0x00095114: ("user_mem_reply", 36, "e8b29fb2de08c40d8bef0e69764a3e363ef63561cd93dbe8b08786d797680d1b"),
    }
    for entry, (symbol, size, digest) in qwr_exact_expected.items():
        row = ownership_by_key[("application", f"0x{entry:08x}")]
        body = recovered_function(entry)
        if row["upstream_symbol"] != symbol or \
                "components/ble/nrf_ble_qwr/nrf_ble_qwr.c" not in row["evidence"] or \
                len(body) != size or hashlib.sha256(body).hexdigest() != digest:
            raise AssertionError(f"Nordic QWR exact function mismatch: 0x{entry:08x}")
    advdata_exact_expected = {
        0x00051FB8: (
            "ble_device_addr_encode", 96,
            "fe422ece8219c7688d72c925330fecc49afc36d7ddacf5765bbb31a23fa598bb",
        ),
        0x00051528: ("ble_advdata_encode", 386, "4f9a516e587026639a443ec5595b1a5d3504c5797cfbb18874fd214b42cbae5f"),
        0x000516AA: ("ble_advdata_parse", 32, "964d6102a1c7444fcf41f4f015b9b564ccdf3a2e54bb9f56339284c516e4dd4b"),
        0x000516CA: ("ble_advdata_search", 70, "9ef3c05dbc8819614823e11b877ab578ea82db1e8b5e2db009443c8a2aea7d17"),
        0x00059BDE: ("conn_int_encode", 136, "caffa6db2ef744ac7fb09817328c6fb82c606d1d417dffeb61ecd6eef4e582e6"),
        0x00076088: ("manuf_specific_data_encode", 100, "b8d4a4a04f0a0bbee17e3f0160263f00c1cbb6ac6d1957577e85a23382bd5b72"),
        0x000770BC: ("name_encode", 166, "fcf1f9238306f59390c9d20a6c18cf60ee77b882a0065aa9250d924608274410"),
        0x0008ABA0: ("service_data_encode", 134, "2e64734f3b8c238e3575b43d0d173cb67d19a92142610a805cbb2c1188694b7b"),
        0x00095540: ("uuid_list_encode", 48, "4fa38b012136c21967851320aa797e04f32d4dcc30f610a41487e097f67d569e"),
        0x00095570: ("uuid_list_sized_encode", 158, "6228634b6a3e11c4268ad6fa422445dd78890ed88e7c3fcf386274ced686d164"),
    }
    for entry, (symbol, size, digest) in advdata_exact_expected.items():
        row = ownership_by_key[("application", f"0x{entry:08x}")]
        body = recovered_function(entry)
        if row["upstream_symbol"] != symbol or \
                "components/ble/common/ble_advdata.c" not in row["evidence"] or \
                len(body) != size or hashlib.sha256(body).hexdigest() != digest:
            raise AssertionError(f"Nordic advertising-data exact function mismatch: 0x{entry:08x}")
    uint16_encode_body = recovered_function(0x00093EA2)
    if len(uint16_encode_body) != 10 or hashlib.sha256(uint16_encode_body).hexdigest() != \
            "add1d19cf532ebb27f8405e56b7823fda004f2bed9e9d78297c526b68e316e66":
        raise AssertionError("Nordic uint16_encode body changed")
    nordic_application_rows = [
        row for row in ownership_rows
        if row["image"] == "application" and
        row["provider_family"] == "nordic_nrf5_sdk_17_1_0"
    ]
    if len(nordic_application_rows) != len(nordic_expected):
        raise AssertionError("Nordic application map contains an unreviewed broad classification")
    nordic_adapter_expected = {
        "0x000551e8": "r1_software_twi_i2c_2_shutdown_adapter",
        "0x0005520c": "r1_software_twi_i2c_3_shutdown_adapter",
        "0x00055230": "r1_software_twi_i2c_4_shutdown_adapter",
        "0x00055254": "r1_software_twi_i2c_5_shutdown_adapter",
        "0x0007cf4c": "Nordic ble_nus on_write skeleton + R1 four-characteristic BAE8 event adapter",
        "0x0008185c": "prefix_process + R1 wall-clock log prefix",
        "0x00077e98": "r1_reset_reason_nordic_adapter",
        "0x0003e7a8": "r1_bae8_hvx_serialized_send_adapter",
        "0x0004d4ac": "r1_connection_parameter_mode_adapter",
        "0x00063d50": "r1_fds_event_adapter",
    }
    for entry, symbol in nordic_adapter_expected.items():
        row = ownership_by_key[("application", entry)]
        if row["provider_family"] != "r1_nordic_sdk_provider_adapter" or \
                row["source_disposition"] != \
                "clean_room_adapter_only_use_nordic_sdk" or \
                row["upstream_symbol"] != symbol:
            raise AssertionError(f"R1 Nordic adapter is not bounded: {entry}")
    nordic_adapter_rows = [
        row for row in ownership_rows
        if row["image"] == "application" and
        row["provider_family"] == "r1_nordic_sdk_provider_adapter"
    ]
    if len(nordic_adapter_rows) != len(nordic_adapter_expected):
        raise AssertionError("R1 Nordic adapter map contains an unreviewed broad classification")
    for entry in (0x000551E8, 0x0005520C, 0x00055230, 0x00055254):
        body = recovered_function(entry)
        if len(body) != 30 or hashlib.sha256(body).hexdigest() != \
                "8e917b01e58d21741dc590879c8ed6bc70635db30b3c0037dc42f916e512801b":
            raise AssertionError(
                f"R1 software-TWI shutdown behavior changed: 0x{entry:08x}"
            )
    segger_expected = {
        "0x00031948": ("segger_rtt_6_18a_sdk_bundled", "SEGGER_RTT_Init"),
        "0x0003194c": ("segger_rtt_6_18a_sdk_bundled", "SEGGER_RTT_Read"),
        "0x00031964": ("segger_rtt_6_18a_sdk_bundled", "SEGGER_RTT_ReadNoLock"),
        "0x000319e0": ("segger_rtt_6_18a_sdk_bundled", "SEGGER_RTT_Write"),
        "0x00031a18": ("segger_rtt_6_18a_sdk_bundled", "SEGGER_RTT_WriteNoLock"),
        "0x00036d68": ("segger_rtt_6_18a_sdk_bundled", "SEGGER_RTT_Init"),
        "0x00036f72": ("segger_rtt_6_18a_sdk_bundled", "_GetAvailWriteSpace"),
        "0x00037eb6": ("segger_rtt_6_18a_sdk_bundled", "_WriteBlocking"),
        "0x00037f10": ("segger_rtt_6_18a_sdk_bundled", "_WriteNoCheck"),
        "0x00056744": ("segger_fprintf_6_14d_sdk_bundled", "buffer_add"),
        "0x00072310": ("segger_fprintf_6_14d_sdk_bundled", "int_print"),
        "0x00078a72": ("segger_fprintf_6_14d_sdk_bundled", "nrf_fprintf_fmt"),
        "0x00093ef8": ("segger_fprintf_6_14d_sdk_bundled", "unsigned_print"),
    }
    for entry, (provider, symbol) in segger_expected.items():
        row = ownership_by_key[("application", entry)]
        if row["provider_family"] != provider or \
                row["source_disposition"] != "use_nordic_sdk_bundled_upstream" or \
                row["upstream_symbol"] != symbol:
            raise AssertionError(f"SEGGER provider function not source-routed: {entry}")
    nordic_pm_buffer_exact = {
        0x000765DC: ("mutex_lock_status_get", 8, "66bb84564911a2ed578bf7319026427c8cb06691763ec1d13d02b9a1f4520641"),
        0x0007F194: ("pm_buffer_block_acquire", 100, "5cdc151ab6ae58a690692ac043f398cf6cce5399d7c5016f05b5a775b7cd6ee2"),
        0x0007F1F8: ("pm_buffer_init", 36, "1419174e6f6bc8f36ecf95c18601270ea6da05483a0be290a01a330944f60001"),
        0x0007F21C: ("pm_buffer_ptr_get", 40, "a40e1be372517a4eb20050d330e3bccc56f9075af2832816b1dd10bdb9d1950a"),
        0x0007F244: ("pm_buffer_release", 50, "7feca14469732e7b6c81226638adb141ba94fef22f8f57591d6b0a6d457c9a36"),
    }
    for entry, (symbol, size, digest) in nordic_pm_buffer_exact.items():
        row = ownership_by_key[("application", f"0x{entry:08x}")]
        body = recovered_function(entry)
        if row["provider_family"] != "nordic_nrf5_sdk_17_1_0" or \
                row["upstream_symbol"] != symbol or len(body) != size or \
                hashlib.sha256(body).hexdigest() != digest:
            raise AssertionError(f"Nordic PM buffer body changed: 0x{entry:08x}")
    nordic_peer_manager_exact = {
        # Ghidra assigned 0x7f276 a non-contiguous/overlapping extent ending at
        # 0x90631. The independently established executable body ends at the
        # next function entry, 0x7f280, and is intentionally sliced to 10 bytes.
        0x0007F276: ("pm_conn_sec_config_reply", 10, "c90228e857237dc06d0a15e67e895497b3597e51896ed207b31b2ded53d95f9a"),
        0x0007F280: ("pm_conn_sec_status_get", 14, "6c20158ede6142c554280a9989ae1c982632b63ba53f9d5aecf40e39605e5aa3"),
        0x0007F294: ("pm_conn_secure", 24, "346235692dc28f833c600a5d345be288ad41257f2ff2ba11444ba354a8a018cd"),
        0x00080980: ("pm_pdb_evt_handler", 276, "aad00dbea0fda16b9dbda73a087ddec42de24a82f2aa5175efa37e717fbf541a"),
        0x00080A98: ("pm_peer_data_bonding_load", 18, "e953a722c9862dc1b8eef146f4594801d1ac020f79b8d1e3535c4662a09f5543"),
        0x00080AAC: ("pm_peer_data_load", 34, "5d4e6c539dbd331712191b360895fbb5400e8c930b5cda4ea3150b12399191e0"),
        0x00080AD4: ("pm_peer_delete", 14, "85fe4f9526e24b80a2b87b341d84b906b27819b74c6ec1bf8d95bf6d557f4132"),
        0x00080AE8: ("pm_peer_rank_highest", 252, "ecd0533bca82aa77a2fdd2b1efd76dda519c0d3b4ae382d9005de083c5d85351"),
        0x00080C38: ("pm_peer_ranks_get", 272, "848b2d59148a824baa142f1023694392ad9502fade5ec1b049e47b7d45121ae6"),
        0x00080D5C: ("pm_peers_delete", 176, "456aa793603117e537bb01a8cd0531d7c13b6c5515ed0e06210bb3db01154c21"),
        0x00080E28: ("pm_register", 34, "ec0bdd96f2f9ca404a9c831752f200193d639cc1963f916330bd90e172e6430a"),
        0x00080E54: ("pm_sec_params_set", 14, "9b40ffc00d619853924ec66a95d84b282daaee02a842f742de683b533ed562e3"),
        0x00080E68: ("pm_sm_evt_handler", 10, "65c6972d1b6618b593d98291c9c04135662aed595924b9373dad70c77715f3ea"),
    }
    for entry, (symbol, size, digest) in nordic_peer_manager_exact.items():
        row = ownership_by_key[("application", f"0x{entry:08x}")]
        body = recovered[entry - recovered_base:entry - recovered_base + size]
        if row["provider_family"] != "nordic_nrf5_sdk_17_1_0" or \
                row["source_disposition"] != "use_nordic_sdk" or \
                row["upstream_symbol"] != symbol or \
                "components/ble/peer_manager/peer_manager.c" not in row["evidence"] or \
                len(body) != size or hashlib.sha256(body).hexdigest() != digest:
            raise AssertionError(f"Nordic Peer Manager body changed: 0x{entry:08x}")
    nordic_security_dispatcher_exact = {
        0x0004C6D0: ("allow_repairing", 8, "684e16eb0486e49e711abf5f3309bb3e9b25db3f1c09da7124466f049a1f3c11"),
        0x00059C68: ("conn_sec_failure", 60, "99d4d0f8dfa81bc7480aa1ff663f72fb465c55023c370fc7bba1b0aa77fb4971"),
        0x0007E2F0: ("pairing", 8, "ddd7756f9d64aa3d1811bb6cebc1500dcd2dbac242de23b907f79601d8fc117c"),
        0x0007E3A4: ("pairing_success_evt_send", 46, "34d20d2dc69d2b4fad2ff563b25ea0ca6005bded406575d278c573aab2014460"),
        0x000891B8: ("sec_info_request_process", 292, "b06ef26335bbb58c1c56c8447dc3cc91067cad8a2a7bb6cd6c5c29ad7e57917a"),
        0x0008965A: ("send_config_req", 34, "e6692144d216670416720ac0150dd0c5cde8980516e7bc926b3d52b34cf2efe0"),
        0x000896C8: ("send_unexpected_error", 34, "0179f2debec55065af5ddf14cb2dba11de96d1d08d59d29feacf00c7edba20c0"),
        0x000906C8: ("smd_link_secure", 40, "b740ac25d31a7e1f9590184a03ae0d10d1dad8e6aa1a24d83b4dec7d7c4e5e65"),
        0x000906F0: ("smd_params_reply", 162, "7346acfb3419f7931abd1e6fc21a5b96f1e7f5ce114267fa22a27967c83ec9cd"),
    }
    for entry, (symbol, size, digest) in nordic_security_dispatcher_exact.items():
        row = ownership_by_key[("application", f"0x{entry:08x}")]
        body = recovered_function(entry)
        if row["provider_family"] != "nordic_nrf5_sdk_17_1_0" or \
                row["upstream_symbol"] != symbol or \
                "components/ble/peer_manager/security_dispatcher.c" not in row["evidence"] or \
                len(body) != size or hashlib.sha256(body).hexdigest() != digest:
            raise AssertionError(f"Nordic Security Dispatcher body changed: 0x{entry:08x}")
    encryption_failure_row = ownership_by_key[("application", "0x0005d314")]
    encryption_failure_body = recovered[
        0x0005D314 - recovered_base:0x0005D31E - recovered_base
    ]
    if encryption_failure_row["provider_family"] != "nordic_nrf5_sdk_17_1_0" or \
            encryption_failure_row["upstream_symbol"] != "encryption_failure" or \
            "components/ble/peer_manager/security_dispatcher.c" not in \
            encryption_failure_row["evidence"] or len(encryption_failure_body) != 10 or \
            hashlib.sha256(encryption_failure_body).hexdigest() != \
            "a25e71d73c94e9d6e647ca72c6d23e6b7a5cd504816d0805ba06bcb9a45f941b":
        raise AssertionError("Nordic encryption_failure veneer changed")
    link_secure_failure_row = ownership_by_key[("application", "0x00075038")]
    link_secure_failure_body = b"".join((
        recovered[0x00075038 - recovered_base:0x0007506E - recovered_base],
        recovered[0x0007E2FC - recovered_base:0x0007E390 - recovered_base],
    ))
    if link_secure_failure_row["provider_family"] != "nordic_nrf5_sdk_17_1_0" or \
            link_secure_failure_row["upstream_symbol"] != "link_secure_failure" or \
            "components/ble/peer_manager/security_dispatcher.c" not in \
            link_secure_failure_row["evidence"] or \
            len(link_secure_failure_body) != 202 or \
            hashlib.sha256(link_secure_failure_body).hexdigest() != \
            "cbbcf77ccc8f9fef92196c82426587f9b580e9bc22b81a84c637e5212cc005dc":
        raise AssertionError("Nordic discontiguous link_secure_failure body changed")
    config_reply_row = ownership_by_key[("application", "0x00090334")]
    config_reply_body = b"".join((
        recovered[0x00090334 - recovered_base:0x00090338 - recovered_base],
        recovered[0x00090628 - recovered_base:0x00090632 - recovered_base],
    ))
    if config_reply_row["provider_family"] != "nordic_nrf5_sdk_17_1_0" or \
            config_reply_row["upstream_symbol"] != "smd_conn_sec_config_reply" or \
            "components/ble/peer_manager/security_dispatcher.c" not in \
            config_reply_row["evidence"] or len(config_reply_body) != 14 or \
            hashlib.sha256(config_reply_body).hexdigest() != \
            "d283609ff3bc9594fa15cd3010e8faedb7f911d5cea7c6349ee3312d662f68c2":
        raise AssertionError("Nordic discontiguous smd_conn_sec_config_reply body changed")
    nordic_security_manager_exact = {
        0x0005EB94: ("events_send_from_err_code", 220, "e573d91dc8d31e11946db2811624944b132b80bf56d0227c20a2ee456b007be2"),
        0x0005ED08: ("evt_send", 6, "295c2ca51cb5bd35678e7f18a35dfdfa58c360d3e83f83f4e5ffb81fd7b11b47"),
        0x00064F44: ("flags_set_from_err_code", 42, "b8a07877b9310fb5ab000e0789b47612c963c89764d014668513e556d9759bb9"),
        0x00074F38: ("link_secure", 236, "6b26f0ea41f34ebd0ae3a32839143c700532c359f88f6b6c6093656c10fbb12c"),
        0x00075074: ("link_secure_pending_handle", 38, "61b57236ff7711ca081a114e503ecbd89527678dee8d63ccd6994ade13a790f5"),
        0x0007719C: ("new_context_get", 14, "6d301c9430ff4c76b5b246301a31cd929ddf43dbe59cd76725f0e2f1fc9072a8"),
        0x000771B0: ("new_evt", 50, "8d8e587f78be9133602dded93f2e4a790109a08d8a5dda5e03a88e95a5097c33"),
        0x0007E3D8: ("params_req_send", 32, "ac0ad58b1eeb0968bf82eb697c9f719998fcad294217ef4bf52614163f2ea881"),
        0x00089598: (
            "sec_req_process", 86,
            "f298f3f5f5fc2737c410560c1c6be588e511c0c0194da698fcc78c0c8a695d8d",
        ),
    }
    for entry, (symbol, size, digest) in nordic_security_manager_exact.items():
        row = ownership_by_key[("application", f"0x{entry:08x}")]
        body = recovered_function(entry)
        if row["provider_family"] != "nordic_nrf5_sdk_17_1_0" or \
                row["upstream_symbol"] != symbol or \
                "components/ble/peer_manager/security_manager.c" not in row["evidence"] or \
                len(body) != size or hashlib.sha256(body).hexdigest() != digest:
            raise AssertionError(f"Nordic Security Manager body changed: 0x{entry:08x}")
    nordic_gatt_cache_exact = {
        0x000896A0: (
            "send_unexpected_error", 34,
            "fad4a152e384eb389ec943f9893a1d8c41c5d7a13d5cb45114392bbc14529a67",
        ),
    }
    for entry, (symbol, size, digest) in nordic_gatt_cache_exact.items():
        row = ownership_by_key[("application", f"0x{entry:08x}")]
        body = recovered_function(entry)
        if row["provider_family"] != "nordic_nrf5_sdk_17_1_0" or \
                row["upstream_symbol"] != symbol or \
                "components/ble/peer_manager/gatt_cache_manager.c" not in row["evidence"] or \
                len(body) != size or hashlib.sha256(body).hexdigest() != digest:
            raise AssertionError(f"Nordic GATT Cache body changed: 0x{entry:08x}")
    segger_rtt_exact = {
        0x00031948: (
            "SEGGER_RTT_Init", 4,
            "302b446685fd5b58025c48898e732aff21d97cc1f3546512a55dc10e36da0fbb",
        ),
        0x0003194C: (
            "SEGGER_RTT_Read", 24,
            "1544e6d031a3c719ef88955c67beb4b890197ab162e23167fc4ab1bc59980259",
        ),
        0x00031964: (
            "SEGGER_RTT_ReadNoLock", 120,
            "797aaf4baf0630fa4f2764074744b0ff04ffa27cc4224548af80b76b301538ed",
        ),
        0x000319E0: (
            "SEGGER_RTT_Write", 52,
            "c3281596a54e8def96dc5336336964f39b1e4511965cdccf7453b51012230629",
        ),
        0x00031A18: (
            "SEGGER_RTT_WriteNoLock", 86,
            "e452c90e4d891156e4ab3f782eb9933d93b16d6e6efaa77b840800de48af5fa8",
        ),
        0x00036F72: (
            "_GetAvailWriteSpace", 22,
            "91cb9720a3c94eeecbec56152ef32201148fc3631e70e5a860e12242a34e5bcb",
        ),
        0x00037EB6: (
            "_WriteBlocking", 90,
            "c94d1018f63cc9b0cc80f5fa5d302b823243ae8c7aea190fb3d248a8f2bc0f35",
        ),
        0x00037F10: (
            "_WriteNoCheck", 66,
            "f214fa90984cdd0675186c77a2d210324fad97bf677ed6b0f1b03dbddf0703cd",
        ),
    }
    for entry, (symbol, size, digest) in segger_rtt_exact.items():
        row = ownership_by_key[("application", f"0x{entry:08x}")]
        body = recovered_function(entry)
        if row["provider_family"] != "segger_rtt_6_18a_sdk_bundled" or \
                row["upstream_symbol"] != symbol or len(body) != size or \
                hashlib.sha256(body).hexdigest() != digest:
            raise AssertionError(f"SEGGER RTT body changed: 0x{entry:08x}")
    toolchain_runtime_expected = {
        "0x000274e8": "__aeabi_uldivmod",
        "0x0002754a": "__aeabi_ldivmod",
        "0x000275ac": "__aeabi_llsl",
        "0x000275ca": "__aeabi_llsr",
        "0x000275f4": "isspace",
        "0x00027606": "qsort",
        "0x000276a4": "rand",
        "0x000276b8": "srand",
        "0x000276c8": "gmtime",
        "0x0002775c": "memmove",
        "0x0002779c": "__aeabi_memset",
        "0x000277aa": "__aeabi_memclr",
        "0x000277ae": "memset",
        "0x000277c0": "strcat",
        "0x000277d8": "strncpy",
        "0x000277f0": "strlen",
        "0x000277fe": "strcmp",
        "0x0002781a": "memcmp",
        "0x00027834": "strncmp",
        "0x00027854": "strtok",
        "0x00027898": "sscanf",
        "0x00027afc": "__aeabi_dadd",
        "0x00027c3e": "__aeabi_dsub",
        "0x00027c44": "__aeabi_drsub",
        "0x00027c4a": "__aeabi_dmul",
        "0x00027d2e": "__aeabi_ddiv",
        "0x00027e0c": "__aeabi_l2f",
        "0x00027e38": "__aeabi_i2d",
        "0x00027e5a": "__aeabi_ui2d",
        "0x00027e74": "__aeabi_d2iz",
        "0x00027eb2": "__aeabi_d2uiz",
        "0x00027ee4": "__aeabi_f2d",
        "0x00027f0c": "__aeabi_cdrcmple",
        "0x00027f3c": "__aeabi_cdcmple",
        "0x00027f6c": "__aeabi_d2f",
        "0x00027fa4": "__aeabi_uidiv",
        "0x00027fd0": "__aeabi_lasr",
        "0x00028334": "__aeabi_d2ulz",
        "0x000283a0": "__scatterload",
        "0x000286f4": "__scatterload_decompress",
        "0x00038060": "printf",
        "0x00038080": "snprintf",
        "0x000380b4": "sprintf",
        "0x000380dc": "vsnprintf",
        "0x000381f0": "atan",
        "0x000384c8": "atan2f",
        "0x00038774": "atanf",
        "0x000388d8": "ceil",
        "0x000389f0": "ceilf",
        "0x00038a5c": "cosf",
        "0x00038bb0": "exp",
        "0x00038f08": "expf",
        "0x000390f0": "fabs",
        "0x00039108": "floor",
        "0x00039220": "floorf",
        "0x00039290": "fmaxf",
        "0x000392d8": "fminf",
        "0x00039320": "log",
        "0x000396e4": "log10f",
        "0x00039864": "logf",
        "0x000399d0": "pow",
        "0x0003a620": "powf",
        "0x0003ac88": "round",
        "0x0003ad68": "roundf",
        "0x0003ae04": "sinf",
        "0x0003af94": "sqrt",
        "0x0003b00e": "sqrtf",
        "0x0003b048": "tanf",
        "0x0003b1c8": "tanh",
        "0x0003b328": "tanhf",
        "0x0003b5c0": "expm1",
    }
    for entry, symbol in toolchain_runtime_expected.items():
        row = ownership_by_key[("application", entry)]
        if row["provider_family"] != "arm_toolchain_runtime" or \
                row["source_disposition"] != "use_toolchain_runtime" or \
                row["upstream_symbol"] != symbol:
            raise AssertionError(f"application runtime function not source-routed: {entry}")
    toolchain_internal_expected = {
        "0x000275ec": "internal:ctype_table_pointer_get",
        "0x000278d0": "internal:scanf_integer_conversion",
        "0x00027a1c": "internal:scanf_string_conversion",
        "0x00027ff4": "internal:scanf_digit_value",
        "0x00028010": "internal:scanf_format_getc",
        "0x0002801c": "internal:vsscanf_descriptor_init",
        "0x00028038": "internal:sscanf_input_getc",
        "0x00028056": "internal:sscanf_input_ungetc",
        "0x00028078": "internal:binary32_round_to_even",
        "0x0002808a": "internal:binary32_pack_from_u64",
        "0x000280e6": "internal:binary32_round_to_integral_even",
        "0x00028122": "internal:binary64_round_to_even",
        "0x00028140": "internal:binary64_pack",
        "0x000281dc": "internal:binary64_scale_pow2_flush_underflow",
        "0x0002820a": "internal:binary64_sqrt",
        "0x000282ac": "internal:binary64_round_to_integral_even",
        "0x00028364": "internal:binary32_compare_flags",
        "0x0002839a": "internal:floating_environment_control_stub",
        "0x000283c4": "internal:scanf_core",
        "0x00038110": "internal:binary64_classify",
        "0x00038140": "internal:binary32_classify",
        "0x0003f530": "internal:printf_binary64_decimal_conversion",
        "0x00043080": "internal:printf_core",
        "0x00043734": "internal:printf_left_padding",
        "0x00043758": "internal:printf_width_padding",
        "0x00043bbc": "internal:printf_bounded_buffer_putc",
        "0x00044a6c": "internal:printf_buffer_putc",
        "0x0006570a": "internal:printf_stdout_putc_adapter",
        "0x0003b40c": "internal:binary64_polynomial_evaluate",
        "0x0003b508": "internal:binary64_positive_infinity_raise_divzero",
        "0x0003b538": "internal:binary64_self_add",
        "0x0003b54c": "internal:binary64_add_pair",
        "0x0003b560": "internal:binary64_invalid_zero_div_zero",
        "0x0003b580": "internal:binary64_overflow_raise_square",
        "0x0003b5a0": "internal:binary64_underflow_raise_square",
        "0x0003bab4": "internal:binary32_positive_infinity_raise_divzero",
        "0x0003bac8": "internal:binary32_self_add",
        "0x0003bace": "internal:binary32_add_pair",
        "0x0003bad4": "internal:binary32_invalid_zero_div_zero",
        "0x0003bae4": "internal:binary32_overflow_raise_square",
        "0x0003baf4": "internal:binary32_underflow_raise_square",
        "0x0003bb04": "internal:binary32_trig_argument_reduce",
        "0x0003bc9c": "internal:errno_set",
    }
    for entry, symbol in toolchain_internal_expected.items():
        row = ownership_by_key[("application", entry)]
        if row["provider_family"] != "arm_toolchain_runtime" or \
                row["source_disposition"] != "use_toolchain_runtime" or \
                row["upstream_symbol"] != symbol:
            raise AssertionError(f"application runtime internal not source-routed: {entry}")
    recovered_internal_entries = {
        row["entry"] for row in ownership_rows
        if row["image"] == "application" and
        row["inventory_source"] == "manual_provenance_supplement"
    }
    for entry in (
        "0x00028010", "0x00028038", "0x00028056", "0x0002808a", "0x000283c4",
        "0x0003b538", "0x0003b54c", "0x0003b560", "0x0003bac8", "0x0003bace",
        "0x0003bad4",
        "0x00043bbc",
    ):
        if entry not in recovered_internal_entries:
            raise AssertionError(f"missing disassembly-visible runtime supplement: {entry}")
    cmsis_expected = {
        "0x0002febc": "IRQ_Context",
        "0x0007d154": "osDelay",
        "0x0007d172": "osEventFlagsNew",
        "0x0007d1a0": "osEventFlagsSet",
        "0x0007d200": "osEventFlagsWait",
        "0x0007d26c": "osKernelGetState",
        "0x0007d28c": "osKernelGetTickCount",
        "0x0007d2a4": "osKernelGetTickFreq",
        "0x0007d310": "osMessageQueueGet",
        "0x0007d388": "osMessageQueueGetCapacity",
        "0x0007d390": "osMessageQueueGetCount",
        "0x0007d3b4": "osMessageQueueNew",
        "0x0007d40c": "osMessageQueuePut",
        "0x0007d488": "osMutexAcquire",
        "0x0007d4d6": "osMutexNew",
        "0x0007d536": "osMutexRelease",
        "0x0007d57c": "osSemaphoreAcquire",
        "0x0007d5e8": "osSemaphoreGetCount",
        "0x0007d60c": "osSemaphoreNew",
        "0x0007d698": "osSemaphoreRelease",
        "0x0007d6f4": "osThreadFlagsSet",
        "0x0007d780": "osThreadFlagsWait",
        "0x0007d814": "osThreadGetId",
        "0x0007d818": "osThreadNew",
        "0x0007d8a6": "osThreadSetPriority",
        "0x0007d8d6": "osThreadTerminate",
        "0x0007d90c": "osTimerNew",
        "0x0007d9b0": "osTimerStart",
        "0x0007d9ea": "osTimerStop",
    }
    for entry, symbol in cmsis_expected.items():
        row = ownership_by_key[("application", entry)]
        if row["provider_family"] != "arm_cmsis_freertos_10_5_1" or \
                row["source_disposition"] != "use_authenticated_upstream_snapshot" or \
                row["upstream_symbol"] != symbol:
            raise AssertionError(f"CMSIS-FreeRTOS function not source-routed: {entry}")
    freertos_exact_expected = {
        0x0009566C: (
            "uxTaskGetNumberOfTasks", "external/freertos/source/tasks.c",
            6, "f9e9ed7deab97ba770020418c839a3824257d2e29c2f736e873b7a50a3efaeb8",
        ),
        0x00027218: (
            "vPortSVCHandler", "external/freertos/portable/GCC/nrf52/port.c",
            28, "fed6d2b19c846fee2dc54c1b05e078c6e7c792d7ae607a55dc873940484043bb",
        ),
        0x00027238: (
            "vPortStartFirstTask", "external/freertos/portable/GCC/nrf52/port.c",
            36, "19cfbd9e009d08a6d60a01fcc9746bca432828d2e997e267ada9114c6efb4e96",
        ),
        0x0002725C: (
            "xPortPendSVHandler", "external/freertos/portable/GCC/nrf52/port.c",
            88, "c3fd055dd525e61dc426730122767cfa249b4383fc37bdd32761a4d06aa4ff63",
        ),
        0x000316E8: (
            "xPortSysTickHandler",
            "external/freertos/portable/CMSIS/nrf52/port_cmsis_systick.c",
            96, "2b1c81c75ae57d57ad891d407e2d78dd2c4931905f6496c883846297ca936d98",
        ),
        0x0005CF78: (
            "eTaskConfirmSleepModeStatus", "external/freertos/source/tasks.c",
            44, "70b59a3005a346b2c50cae3a9be65513b49286f404194d4f047516e136da9f55",
        ),
        0x0005CFAC: (
            "eTaskGetState", "external/freertos/source/tasks.c",
            104, "53c4a553b209e61801b2eef5d768d077af485cab30c8f2eebf61ac977aeb0c56",
        ),
        0x00084CF0: (
            "prvAddCurrentTaskToDelayedList", "external/freertos/source/tasks.c",
            110, "c255fd0a9c8fefcf242ed03d07cad7802c4a6d9d50c45ea50435ed2f7b57d85c",
        ),
        0x00084D68: (
            "prvAddNewTaskToReadyList", "external/freertos/source/tasks.c",
            224, "695d11267b4be737cdb8b9d35c26254679db9a3844835c320c633d964029ebf1",
        ),
        0x0008522C: (
            "prvIsQueueEmpty", "external/freertos/source/queue.c",
            28, "cd5e69e86c718e9d0f7551cc019637042928d9d5bfd4362d29b91c75ccc38eb5",
        ),
        0x00085468: (
            "prvResetNextTaskUnblockTime", "external/freertos/source/tasks.c",
            24, "e0a3af0b4de44bb21de2ac73bcc23fcc506771541b04e733ef1ccb4a7096de9a",
        ),
        0x00085534: (
            "prvUnlockQueue", "external/freertos/source/queue.c",
            106, "d503caf39ab536a5b4ab3d7ee80f5ad45f6ac37eb6b6be999e46e2686032cf0b",
        ),
        0x00084E58: (
            "prvCheckForValidListAndQueue", "external/freertos/source/timers.c",
            62, "ccf736562f182ae0c2cf4dca5c9c61994a2868f7f5c26642b40f65ac668a5de5",
        ),
        0x00084EA4: (
            "prvCopyDataFromQueue", "external/freertos/source/queue.c",
            38, "4c58704f118800398fad5eb956cb6af3f387bec55746cbcec53e2b2d6010438b",
        ),
        0x00084ECA: (
            "prvCopyDataToQueue", "external/freertos/source/queue.c",
            108, "bb27865cdcf63f616744ad8f3c6f57a8740bc3bfad55a3dc988fc2e26284f623",
        ),
        0x00084F36: (
            "prvDeleteTCB", "external/freertos/source/tasks.c",
            50, "cdc02dc411157e46573fbbf51ab3f0fa87c622f6cf844ab91b36fefa36b098e5",
        ),
        0x00084F68: (
            "prvGetExpectedIdleTime", "external/freertos/source/tasks.c",
            40, "c9d8b3805f33d89d1ea7c1fdff6f26cc0a565528e65645dbf39ca601f0dabb4a",
        ),
        0x00084F98: (
            "prvHeapInit", "external/freertos/source/portable/MemMang/heap_4.c",
            68, "ef76690b1ceea6d4a5c9bdcd921db4e3685119217d238a784f5e7361acdcd559",
        ),
        0x0008507C: (
            "prvInitialiseMutex", "external/freertos/source/queue.c",
            22, "42e1f3c8ad53c7a8951b6f7c7a4ddd793e68183f9337a8793a42f13a396533b2",
        ),
        0x00085094: (
            "prvInitialiseNewQueue", "external/freertos/source/queue.c",
            34, "7763c36e1211f5e84e79344f7ff8c3870c2c28b2a5eeb37819ebbaf7e1a44d16",
        ),
        0x000850B6: (
            "prvInitialiseNewTask", "external/freertos/source/tasks.c",
            164, "e20f7b3effa0056d5ae45f0543ef311d062517cb412994710d0782639fb2b875",
        ),
        0x0008515A: (
            "prvInitialiseNewTimer", "external/freertos/source/timers.c",
            72, "261ef3d246db03a887d3fc78b74f24246870054b2eeafdff97855efcebf091ce",
        ),
        0x000851A4: (
            "prvInsertBlockIntoFreeList",
            "external/freertos/source/portable/MemMang/heap_4.c",
            70, "9c5dd6bb9ad8ada2699bd93f35dc9db94e1514fd925314bb74fceee2d7a94612",
        ),
        0x000851F4: (
            "prvInsertTimerInActiveList", "external/freertos/source/timers.c",
            52, "3a79d754e81bf5fe2ce812606e7e308fe908c9f479aed91383271042f5957d1b",
        ),
        0x00085248: (
            "prvListTasksWithinSingleList", "external/freertos/source/tasks.c",
            88, "168ec44c08ce8fbce47a3510efc313f147cb0c5c77d7f7958c7e9d38c9b8a947",
        ),
        0x000852A0: (
            "prvProcessExpiredTimer", "external/freertos/source/timers.c",
            58, "967eae1ac44b11121e52b4dd297430c8dd3ce0affcfcfe74531bcd9589b80c9f",
        ),
        0x000852E0: (
            "prvProcessReceivedCommands", "external/freertos/source/timers.c",
            228, "506f02dbb15d52cbc2fdcd1a4dc21aa7a80e7e6dae5a0a165c8af8da4d6b7ca0",
        ),
        0x000853D4: (
            "prvProcessTimerOrBlockTask", "external/freertos/source/timers.c",
            100, "7c665c0d2abc17a49daa247c03918cde1c492ca53fcab97b659b70befcc82863",
        ),
        0x00085440: (
            "prvReloadTimer", "external/freertos/source/timers.c",
            40, "d03d69b29abd0f1d1fd5c818b9cda349717d56534de9709497af868b7cb4b635",
        ),
        0x00085484: (
            "prvSampleTimeNow + inlined prvSwitchTimerLists",
            "external/freertos/source/timers.c",
            66, "42cc6f2ff1420a8c1cfcf1599e92d2b2b11daff5767745272d8d2974a6b9a213",
        ),
        0x000854CC: (
            "prvTaskCheckFreeStackSpace", "external/freertos/source/tasks.c",
            20, "5e7aff14af78ebf7c24acd0f816f60d41e166c00f32cce38d814a75a43406fe8",
        ),
        0x000854E0: (
            "prvTaskExitError", "external/freertos/portable/CMSIS/nrf52/port_cmsis.c",
            24, "c6bc0c0636c09b039a166352e8d0782ca80956a6981d28499c9f0d747f591e8f",
        ),
        0x000854FC: (
            "prvTestWaitCondition", "external/freertos/source/event_groups.c",
            20, "5cc09712cdb2263c931733e17094f3469ddc8a2840c60c71d52cf13f40915b39",
        ),
        0x000855A0: (
            "pvPortMalloc", "external/freertos/source/portable/MemMang/heap_4.c",
            220, "8a71078f92c19347c9336fa6f24b02892890ea08632b2675f4471c09fcd5ff74",
        ),
        0x00085684: (
            "pvTaskIncrementMutexHeldCount", "external/freertos/source/tasks.c",
            18, "91d19f8f48dfa0670fe745a5bc13a4ba57fd1ccc061184ab4f44508b45323696",
        ),
        0x0008569C: (
            "xTaskGetApplicationTaskTag", "external/freertos/source/tasks.c",
            34, "97b2b73ea33c04f7a36b09e2b2eaea0e4b76d207a161419ce17f0fe85739b92f",
        ),
        0x000856C0: (
            "pxPortInitialiseStack",
            "external/freertos/portable/CMSIS/nrf52/port_cmsis.c",
            36, "d288821b4263778ea8beccc7c702e96f9c6d923dea6153c6ba078f3f69e4d3d8",
        ),
        0x00093EAC: (
            "ulPortRaiseBASEPRI",
            "external/freertos/portable/CMSIS/nrf52/portmacro_cmsis.h",
            12, "3b7672e8d1fa8e0f87597cd70ca2eaefe805eb0aae2b7ee473b4233d3e273442",
        ),
        0x00093EB8: (
            "ulPortRaiseBASEPRI",
            "external/freertos/portable/CMSIS/nrf52/portmacro_cmsis.h",
            12, "3b7672e8d1fa8e0f87597cd70ca2eaefe805eb0aae2b7ee473b4233d3e273442",
        ),
        0x0009560E: (
            "uxListRemove", "external/freertos/source/list.c",
            38, "26f3b79f0deb08fae4f59aab028e8be9c76f8b5d339e74a796782635916bd4a0",
        ),
        0x00095678: (
            "uxTaskGetSystemState", "external/freertos/source/tasks.c",
            174, "93e15dceca0f0c26b10206b42a6adea5337cb9b34280f7e82b54bc7a46d36f35",
        ),
        0x00095738: (
            "uxTaskResetEventItemValue", "external/freertos/source/tasks.c",
            20, "0f7a9e9bc112e0d9a17db385f1f7ee1f68dc7426892a9422e464dce0730441e5",
        ),
        0x00095C90: (
            "vListInitialise", "external/freertos/source/list.c",
            22, "d24afeaed66209b730e9399c893f6d838dc8f5671aa5cd68abd69c6d244eb763",
        ),
        0x00095CA6: (
            "vListInitialiseItem", "external/freertos/source/list.c",
            6, "bc7f0bc51acf61c75c206ca28e5e0d2c7fb4e8dfdcb6076dffe45857be5d2369",
        ),
        0x00095CAC: (
            "vListInsert", "external/freertos/source/list.c",
            48, "a25d07bd872b3c19328b1e63fa3cdc242afd2fa29a076367bd7f46e115826ea6",
        ),
        0x00095CDC: (
            "vListInsertEnd", "external/freertos/source/list.c",
            24, "78e2f1765fd9ba8e71098dababdfc4a4a1aabb73ed1f730d4fc24b94b54a2aba",
        ),
        0x00095CF4: (
            "vPortEnterCritical", "external/freertos/portable/CMSIS/nrf52/port_cmsis.c",
            40, "59c8562a2e2664b486ba5e1d6a009afab0915030131c3185987377523bd3e23c",
        ),
        0x00095D24: (
            "vPortExitCritical", "external/freertos/portable/CMSIS/nrf52/port_cmsis.c",
            32, "e006b076e3759cd022b8b77a64aa9c210e55ea8eab9823cdadbc36a731a414a8",
        ),
        0x00095D48: (
            "vPortFree", "external/freertos/source/portable/MemMang/heap_4.c",
            88, "11afc60be6d97e9f0dcddb92e0f5c913cf6c39224c1c0acde020924f62c46356",
        ),
        0x00095DA4: (
            "vPortSetupTimerInterrupt",
            "external/freertos/portable/CMSIS/nrf52/port_cmsis_systick.c",
            54, "9811c3877842480b6515b2a3fc5c371679c4e0cb2cede6a8823d46df2c895db4",
        ),
        0x00095DE4: (
            "vPortSuppressTicksAndSleep",
            "components/libraries/pwr_mgmt/nrf_pwr_mgmt.c",
            286, "c0e9e7530f9759ba22a3e26f33931906cfeeb152991ef8d58d06f8dab4ac9654",
        ),
        0x00095F18: (
            "vPortValidateInterruptPriority",
            "external/freertos/portable/CMSIS/nrf52/port_cmsis.c",
            78, "3bb59fb18d8845ee115b85a48f8421e9b11da725450dc78174216255694ffd9c",
        ),
        0x00095F70: (
            "vQueueDelete", "external/freertos/source/queue.c",
            30, "88474f3e61c72229a1242b97464f1ff2459a30a03ac49bd25d77df2ceb241804",
        ),
        0x00095F8E: (
            "vQueueWaitForMessageRestricted", "external/freertos/source/queue.c",
            68, "0f88c2b6b1c05d09abd5c323d68432cf1f283bffe85fb6f7e848aadc4d00ff1f",
        ),
        0x00095FD4: (
            "vTaskDelay", "external/freertos/source/tasks.c",
            66, "0d7b334f741d473478530e67cc491777c27ee76ece869e340771cc19838dd032",
        ),
        0x00096020: (
            "vTaskDelete", "external/freertos/source/tasks.c",
            136, "1a0fe6cea48102ff2523e19cd9d8eb37e9a217f6a4dd6cf14667d4158be02b77",
        ),
        0x000960B4: (
            "vTaskGetInfo", "external/freertos/source/tasks.c",
            122, "d9b806380d54125b3f5911eff88f793c8f69c0953f11b513f84ba78911660fbd",
        ),
        0x00096160: ("vTaskSetTimeOutState", "external/freertos/source/tasks.c", 12, "fc27b9d118957ad9b53f1fafcdd311baeb971aedac6dd53e50340412007f5d85"),
        0x00096170: ("vTaskMissedYield", "external/freertos/source/tasks.c", 8, "05b2fb8d7590e72dd842febf80e8e7405ff294304e34e6c2165cb074870a641d"),
        0x00096188: ("vTaskPlaceOnUnorderedEventList", "external/freertos/source/tasks.c", 42, "8e38504acfd56fdc9866aa0a643f13a07c8426047051c22770298bc3c0059b3d"),
        0x000961B8: (
            "vTaskPlaceOnEventList", "external/freertos/source/tasks.c",
            74, "a9708dec47f1a320ccceccfe4e470c6ca6f2d3fd5d4c839a87d47e294d3dbb02",
        ),
        0x00096208: ("vTaskPlaceOnEventListRestricted", "external/freertos/source/tasks.c", 94, "d3a82f22dbf205ea568c3045df92276fbc27310524b7d596d6c16444fc35be63"),
        0x0009626C: ("vTaskPriorityDisinheritAfterTimeout", "external/freertos/source/tasks.c", 160, "b12953475779e153b068ef87a2a4fa16349ded0dc3ebb75580c5b0616e1f3d5e"),
        0x00096314: ("vTaskPrioritySet", "external/freertos/source/tasks.c", 198, "dad9d14a633f3430c65242de6382b7e33b906b987e0127c7c52e29c1ef35ce1d"),
        0x000963E8: ("xTaskRemoveFromUnorderedEventList", "external/freertos/source/tasks.c", 190, "a39b676c8ad6335cbd983e0eb19eb26cce9d68f2580f392602a8b4d2e0b425c0"),
        0x000964C8: ("vTaskStartScheduler", "external/freertos/source/tasks.c", 100, "938127df05db503674db8a8239df09b2e3fa6f90c7c90edf51628cd9e2401b53"),
        0x0009653C: (
            "vTaskStepTick", "external/freertos/source/tasks.c",
            90, "27399258477b669c3a6f8b1eb702758f11fc67f47dcb02241c58f3a5bbf45b91",
        ),
        0x0009659C: ("vTaskSuspendAll", "external/freertos/source/tasks.c", 10, "6c5de5010a8ef5e21a9e0772e45766244562fe465c339075da0ad34db4bab45a"),
        0x000965AC: ("vTaskSwitchContext", "external/freertos/source/tasks.c", 128, "80ffff75bdf0615f428448e5c5eb341a787981edbe61a4e93a504f30958d73e4"),
        0x0009779C: ("xEventGroupCreate", "external/freertos/source/event_groups.c", 28, "5d09a7c141553e5ba13c4b38be985b3829328ba613b49ed695c1af47948f42f3"),
        0x000977B8: ("xEventGroupCreateStatic", "external/freertos/source/event_groups.c", 38, "1d016a4dfb39aeff76a6ede9db69bb037a677615178d4ec4c911ecbdaf714644"),
        0x000977DE: ("xEventGroupGetBitsFromISR", "external/freertos/source/event_groups.c", 20, "0854d2edc8d15eaca3b949973a8d6c24e42d99e75d4b01ad11b731d91084953e"),
        0x000977F4: ("xEventGroupSetBits", "external/freertos/source/event_groups.c", 134, "4821f8a0a6b46a005aace9ed7f632af412fb26a5fec02d2fbabd37d488c9b494"),
        0x0009787C: ("xTimerPendFunctionCallFromISR", "external/freertos/source/timers.c", 46, "312f03fdc4c999bb7c4ce15f9a3ebd698fb6b1fc121e679f9921c2acdb2e7855"),
        0x0009788C: ("xEventGroupWaitBits", "external/freertos/source/event_groups.c", 244, "9ad25937a5c1b413fcf41df83c2a651b096f71848908a2b84ef5542554e7f9de"),
        0x000979DC: ("xPortStartScheduler", "external/freertos/portable/CMSIS/nrf52/port_cmsis.c", 158, "882d44ff1a286ac08e351040ea3571682fc2766d8701c380eb7ea2ab9c416277"),
        0x00097A88: ("xQueueCreateCountingSemaphore", "external/freertos/source/queue.c", 40, "476392ee1eac3c19756be573903d56e587518011a48fcf9cd106f74708563c53"),
        0x00097AB0: ("xQueueCreateCountingSemaphoreStatic", "external/freertos/source/queue.c", 46, "b07e323a4da3e74207869c20c1e9cff9a507d9b7725c00e8868da8bcdac566f6"),
        0x00097ADE: ("xQueueCreateMutex", "external/freertos/source/queue.c", 22, "1cab806ceefd842022d5bf57940c387e64429883cef9a07ec50f711aacf227ec"),
        0x00097AF4: ("xQueueCreateMutexStatic", "external/freertos/source/queue.c", 26, "ca2488ea686003240505a6fc8c5de54630feb524c3aa2034a44c34ff6b7c7879"),
        0x00097B0E: ("xQueueGenericCreate", "external/freertos/source/queue.c", 84, "fe2c8add52367c7208b6ca56a23c71711feacb5836c757b1d6bf5d684501e0a5"),
        0x00097B62: ("xQueueGenericCreateStatic", "external/freertos/source/queue.c", 66, "2262b135a3e7ba13931539fcb5845d771363a7a14e51625c363176dccc93e1df"),
        0x00097BA4: ("prvInitialiseNewQueue", "external/freertos/source/queue.c", 168, "f1146fd16c69173db9733247c30c1f8156e965c4c95a0093901be7b4999fb651"),
        0x00097C50: ("xQueueGenericSend", "external/freertos/source/queue.c", 334, "b13d1220b99841b01cc72422002eb841370b6449a0c8fde53e87fd6e4edc150c"),
        0x00097DA4: ("xQueueGenericSendFromISR", "external/freertos/source/queue.c", 200, "fa5cc44807da508be2c656101b8e42d5fc2030a0921684fd599d898e79373b7e"),
        0x00097E6C: ("xQueueGiveFromISR", "external/freertos/source/queue.c", 168, "4dd8f4d993c68c940cad1bc4e8caeb568f78701b51243b17f4aeb97c0f691357"),
        0x00097F14: ("xQueueGiveMutexRecursive", "external/freertos/source/queue.c", 60, "261552f3608e3bdbc976ea1549c82fb4aaba3aa0136d6c45521003fe82c42ca9"),
        0x00097F50: ("xQueueReceive", "external/freertos/source/queue.c", 296, "c86c19f8bdbd9ed817d12933837514eac6656299d57edfa885395d58c89fb713"),
        0x0009807C: ("xQueueReceiveFromISR", "external/freertos/source/queue.c", 164, "9edb56a2dfa44b1f74c5cbbe40bb82f77ee882c0099e510f411b256a7d9b0b58"),
        0x00098120: ("xQueueSemaphoreTake", "external/freertos/source/queue.c", 352, "80be87104227c9ed3a5f7abf6b5a169a9923baaa201d3571f151137820fa82a3"),
        0x00098284: ("xQueueTakeMutexRecursive", "external/freertos/source/queue.c", 62, "d522034c487efe92c83b33fc9edad4813db0d877a22a25a07101c68493c5256f"),
        0x00098340: ("xTaskCheckForTimeOut", "external/freertos/source/tasks.c", 114, "8128bef040f06ae5b97b134d9309639fadaee5be273411101ced7e0761e58f10"),
        0x000983B8: ("xTaskCreate", "external/freertos/source/tasks.c", 96, "e84c6ce0fefd0ba5f3900363069abbc6723473103b1c9d76a738afbbea3739b2"),
        0x00098418: ("xTaskCreateStatic", "external/freertos/source/tasks.c", 106, "f0adce7c65e69b764869995730a029930ba182df7c3b0c74787f9cc63a101b70"),
        0x00098484: ("xTaskGenericNotify", "external/freertos/source/tasks.c", 278, "268474f9989e1bd4441e93c4f28d6c1eaafdd49e837e5d648c01b02efbe8e6fe"),
        0x000985AC: ("xTaskGenericNotifyFromISR", "external/freertos/source/tasks.c", 320, "432175908a028d1b58de8e366429660c17cef29a09aa09e70e1356a3bf739ad2"),
        0x00098700: ("xTaskNotifyWait", "external/freertos/source/tasks.c", 148, "0b68d855582db87d10c1a6d71df272d53f76cc93028b384192c58e5b625a4e28"),
        0x0009879C: ("xTaskGetCurrentTaskHandle", "external/freertos/source/tasks.c", 6, "579f66b93cd2bbcb53693929db18e36025cdc6e5d94aa3e7590989e1d8a117b1"),
        0x000987A8: (
            "xTaskGetSchedulerState", "external/freertos/source/tasks.c",
            22, "25e3f32baa3f81ecf26a1ca4810d97a8a497f46b7255d12aa39bfb814bd230f0",
        ),
        0x000987C4: (
            "xTaskGetTickCount", "external/freertos/source/tasks.c",
            6, "3233d055cea937091c22e135724406d332850c0397ef14bfac7bc5e73e083fec",
        ),
        0x000987E0: (
            "xTaskIncrementTick", "external/freertos/source/tasks.c",
            294, "d0959774a6989e4b6f9aa14cc767d47cc670f4c4e608bf3094c53260fd5fc22b",
        ),
        0x00098910: ("xTaskPriorityDisinherit", "external/freertos/source/tasks.c", 148, "5231e7a0aee0583973ce7f2771d564ec3ac41470157b6fc23e2ef6a724d8856e"),
        0x000989AC: ("xTaskPriorityInherit", "external/freertos/source/tasks.c", 150, "799fbb857652bb7b68a6f2fdd1d7fc59741abbcf3a0047d9e84f0411d799ef11"),
        0x00098A4C: ("xTaskRemoveFromEventList", "external/freertos/source/tasks.c", 204, "81a0752d3333018d7717b51ac27f5d7b7552a8a3958b3b26f404a6a22e3a7eff"),
        0x00098B24: ("xTaskResumeAll", "external/freertos/source/tasks.c", 276, "02f5f476b2b00878abb4a025a0bae23f637bd49f6ae55f260e09f6bde1c6643e"),
        0x00098C48: ("xTimerCreate", "external/freertos/source/timers.c", 52, "de7496d7f99b3b8261fdc4166f1990601aaddb391c072316550c3f195331571b"),
        0x00098C7C: ("xTimerCreateStatic", "external/freertos/source/timers.c", 44, "37568676830da7a5ea9d59ea3d322d6665ed68a26ed096fc46231f8d62602009"),
        0x00098CA8: ("xTimerCreateTimerTask", "external/freertos/source/timers.c", 74, "da6e70efe47efa4ee943315e1c364890f8bbe6358977f385b86408003f9cfac8"),
        0x00098D04: ("xTimerGenericCommand", "external/freertos/source/timers.c", 96, "700c7c347bbe3d137b2ce0e66c6eecc7ac31f782b37000065f68c8f35b907867"),
        0x00098D68: ("xTimerIsTimerActive", "external/freertos/source/timers.c", 46, "2948e005448bdc7bb37a74461273bebc3a3b25f00fff3e2719d603b2f486c3bf"),
    }
    for entry, (symbol, source, size, digest) in freertos_exact_expected.items():
        row = ownership_by_key[("application", f"0x{entry:08x}")]
        body = recovered_function(entry)
        if row["provider_family"] != "freertos_10_5_1_nordic_nrf52_port" or \
                row["source_disposition"] != "use_authenticated_upstream_snapshot_and_nordic_port" or \
                row["upstream_symbol"] != symbol or source not in row["evidence"] or \
                len(body) != size or hashlib.sha256(body).hexdigest() != digest:
            raise AssertionError(f"FreeRTOS exact function mismatch: 0x{entry:08x}")
    freertos_rows = [
        row for row in ownership_rows
        if row["image"] == "application" and
        row["provider_family"] == "freertos_10_5_1_nordic_nrf52_port"
    ]
    if len(freertos_rows) != len(freertos_exact_expected) or any(
            row["source_disposition"] != "use_authenticated_upstream_snapshot_and_nordic_port" or
            not row["upstream_symbol"] for row in freertos_rows):
        raise AssertionError("FreeRTOS map contains a non-exact or anonymous attribution")
    flashdb_expected = {
        "0x0003f014": "_fdb_db_path",
        "0x0003f022": "_fdb_flash_erase",
        "0x0003f03e": "_fdb_flash_read",
        "0x0003f05a": "_fdb_flash_write",
        "0x0003f076": "_fdb_get_status",
        "0x0003f094": "_fdb_init_ex",
        "0x0003f2ec": "_fdb_init_finish",
        "0x0003f384": "_fdb_set_status",
        "0x0003f3b0": "_fdb_write_status",
        "0x00057eb4": "check_sec_hdr_cb",
        "0x0006366c": "fdb_blob_make",
        "0x00063672": "fdb_blob_read",
        "0x00063694": "fdb_tsdb_control",
        "0x00063814": "fdb_tsdb_init",
        "0x00063a28": "fdb_tsl_append",
        "0x00063ab8": "fdb_tsl_clean",
        "0x00063ad8": "fdb_tsl_iter_by_time",
        "0x00063cb4": "fdb_tsl_query_count",
        "0x00063d40": "fdb_tsl_to_blob",
        "0x000650c4": "format_all_cb",
        "0x000650d4": "format_sector",
        "0x0006a158": "get_last_sector_addr",
        "0x0006a176": "get_last_tsl_addr",
        "0x0006a194": "get_next_sector_addr",
        "0x0006a1b2": "get_next_tsl_addr",
        "0x00087428": "query_count_cb",
        "0x00087c24": "read_sector_info",
        "0x00087e14": "read_tsl",
        "0x000895f4": "sector_iterator",
        "0x00093744": "tsl_append",
        "0x00093828": "tsl_format_all",
        "0x00094ae0": "update_sec_status",
        "0x0009763c": "write_tsl",
    }
    for entry, symbol in flashdb_expected.items():
        row = ownership_by_key[("application", entry)]
        if row["provider_family"] != "flashdb_2_0_0" or \
                row["source_disposition"] != "use_pinned_upstream" or \
                row["upstream_symbol"] != symbol:
            raise AssertionError(f"FlashDB function not source-routed: {entry}")
    flashdb_callback_expected = {
        0x000650C4: (
            16, "4357dd95615cdf53ecf960b6fa9d9856657e11464eecd9e1eba19d1cef3e6699",
        ),
        0x00087428: (
            18, "c2d3ab8bf5e3e823fbfe012cce4613e911c156788d125a069d7b78ac61668067",
        ),
        0x0006A158: (
            30, "af7988d9e85304f6f4ca091de640dd56a45f6940fdfd6012ce41a5aa4b933d12",
        ),
        0x0006A176: (
            30, "25b7a8aed4da289dc6cdf852078b4c0d098a130b17afb948f720cf23ac3b8bc6",
        ),
    }
    for entry, (size, digest) in flashdb_callback_expected.items():
        body = recovered_function(entry)
        if len(body) != size or hashlib.sha256(body).hexdigest() != digest:
            raise AssertionError(f"FlashDB callback body changed: 0x{entry:08x}")
    fal_expected = {
        "0x00057e1c": "check_and_update_part_cache",
        "0x00062df4": "fal_flash_device_find",
        "0x00062e68": "fal_flash_init",
        "0x00062f40": "fal_init",
        "0x00062ff4": "fal_partition_erase",
        "0x00063150": "fal_partition_find",
        "0x000631c0": "fal_partition_init",
        "0x000631e8": "fal_partition_read",
        "0x00063358": "fal_partition_write",
        "0x00064f74": "flash_device_find_by_part",
    }
    for entry, symbol in fal_expected.items():
        row = ownership_by_key[("application", entry)]
        if row["provider_family"] != "fal_0_5_99_flashdb_bundled" or \
                row["source_disposition"] != "use_pinned_upstream" or \
                row["upstream_symbol"] != symbol:
            raise AssertionError(f"FAL function not source-routed: {entry}")
    internal_flash_adapter_expected = {
        0x00054970: ("r1_internal_flash_callback_configuration", 24,
                     "56204fd422647f465077ab12c708e8fbc8d03f8b4b04efb18331342360a93e1f"),
        0x0005498C: ("r1_internal_flash_erase_and_geometry_control", 90,
                     "b9cda39e0bc0f03ea42a6e1e44e1d5bac07fb8f3db369d0839e9acf0f4c27261"),
        0x000549F0: ("r1_internal_flash_fstorage_configuration", 78,
                     "77bc303edd609c87f797eee0a4ef4fa0a8cff8f6e91c834c07e953a37fd422ad"),
        0x00054A4C: ("r1_internal_flash_device_read", 58,
                     "566a087bf156d6362d518587719aa2228e6eb0bd6a2e424be8d9334a3a46faf1"),
        0x00054A8C: ("r1_internal_flash_device_registration", 20,
                     "723ed3bf811013e4c869ba673706de2eded7250fa726541ff9bad3b1faaec8bc"),
        0x00054AA4: ("r1_internal_flash_device_write", 72,
                     "d2491fed88741679c5f672f2f06b984e2d436a2265ff78069e5034f04b2bc5d4"),
        0x0005C40C: ("r1_internal_flash_fstorage_erase_adapter", 80,
                     "438c1250404d0cfc64595bb8156b3203ad789425ef37e59300903a0d619a01e2"),
        0x0005C464: ("r1_internal_flash_memory_mapped_read_adapter", 24,
                     "be5ff8a2ea57450c7d923fb100739955f6f731a6c30290dec76307733304bfcc"),
        0x0005C480: ("r1_internal_flash_fstorage_write_adapter", 62,
                     "8979301e314a9fb7aa1a97517eaef0d953c8b93efa791b115050eaa29ed795bc"),
        0x00064B24: ("r1_latest_valid_flash_slot_scan_adapter", 204,
                     "663ad294afe45f1be4f7c92c16c12738514aa40fb490b9acbfce4b4c9dc9b657"),
        0x00071054: ("r1_internal_flash_fal_binding", 50,
                     "d824c106b0c0f9734ddb41629fd6031a074aa9183fff47a94eac25f5b555d2af"),
    }
    for entry, (symbol, size, digest) in internal_flash_adapter_expected.items():
        row = ownership_by_key[("application", f"0x{entry:08x}")]
        body = recovered_function(entry)
        if row["provider_family"] != "r1_internal_flash_provider_adapter" or \
                row["source_disposition"] != \
                "clean_room_adapter_only_use_nordic_sdk_and_fal" or \
                row["upstream_symbol"] != symbol or len(body) != size or \
                hashlib.sha256(body).hexdigest() != digest:
            raise AssertionError(
                f"R1 internal-flash adapter changed: 0x{entry:08x}"
            )
    saadc_provider_expected = {
        0x0007AEAC: ("nrfx_saadc_channel_init", 140,
                     "f566b9bdb3566e82779475552d6222438d301d440895159507200c8deac41454"),
        0x0007AF38: ("nrfx_saadc_channel_uninit", 68,
                     "1c3000ad35f6c953143c68af804b71a12078d11a7baf5f25a033f345ca7e31bc"),
        0x0007AF7C: ("nrfx_saadc_init", 148,
                     "d5dd834663a4bf64fec41da0d5a66e5d06ae7fb143c33533a57b923169bb8d62"),
        0x0007B010: ("nrfx_saadc_limits_set", 128,
                     "15f87b4e90a39eeb7bd90fd5ec86956b623047e349042ad231f88d9dd0114b91"),
        0x0007B090: ("nrfx_saadc_sample_convert", 192,
                     "f6b5be2a7ac2024543c8b74d92bc19ec319e64d1486672a9e033c3fef1981aab"),
        0x0007B150: ("nrfx_saadc_uninit", 116,
                     "d1c097f7ef7d2b06624acbf65d5d8b652900352b3efded7a7201df5cfcda1fe2"),
    }
    for entry, (symbol, size, digest) in saadc_provider_expected.items():
        row = ownership_by_key[("application", f"0x{entry:08x}")]
        body = recovered_function(entry)
        if row["provider_family"] != "nordic_nrf5_sdk_17_1_0" or \
                row["source_disposition"] != "use_nordic_sdk" or \
                row["upstream_symbol"] != symbol or \
                "modules/nrfx/drivers/src/nrfx_saadc.c" not in row["evidence"] or \
                len(body) != size or hashlib.sha256(body).hexdigest() != digest:
            raise AssertionError(f"Nordic SAADC provider changed: 0x{entry:08x}")
    analog_adapter_expected = {
        0x00054864: ("r1_saadc_device_lookup_and_channel_configuration", 140,
                     "16ec92db60099eff5d5ffb34342fa43c9e0ee79dc4f8af8f180b281097a50385"),
        0x000548F0: ("r1_saadc_named_sample_adapter", 76,
                     "cc37f1a092c14c62a440e0b354cc109c5a1a47bbbda76763695e3cedddc6b2b6"),
        0x0005493C: ("r1_saadc_record_registration", 46,
                     "d78efd269f6b380c47dfe4ad35d3cff6782021b96d3a00f75a8d4c9047cc8483"),
        0x00091184: ("r1_battery_five_sample_filter_and_conversion", 182,
                     "deaf339da23f60478f08800d1dbea8b56f969f18bdd2d145dd252308863ca80b"),
    }
    for entry, (symbol, size, digest) in analog_adapter_expected.items():
        row = ownership_by_key[("application", f"0x{entry:08x}")]
        body = recovered_function(entry)
        if row["provider_family"] != "r1_analog_provider_adapter" or \
                row["source_disposition"] != \
                "clean_room_adapter_only_use_nordic_sdk" or \
                row["upstream_symbol"] != symbol or len(body) != size or \
                hashlib.sha256(body).hexdigest() != digest:
            raise AssertionError(f"R1 analog adapter changed: 0x{entry:08x}")
    battery_behavior_expected = {
        0x00031FCC: ("r1_battery_runtime_service", 0x00032168,
                     "863f83ebcc66161453cb498ddbef63e81ea83d42424291e15534367fb4cea5fb"),
        0x0003DB70: ("r1_battery_stuck_charge_recovery", 0x0003DC80,
                     "c4624ea1b01d6c199e5c5c94f2b9809860c30cf071a8c9fc02fce75b9b226324"),
        0x0003DD0C: ("r1_battery_charged_state_refresh", 0x0003DD9C,
                     "172542219c4cd2b4ec88c1b3c9d22231e42f77bc3d6bf34e36b2d82096a9d9db"),
        0x0004FE5C: ("r1_battery_charging_progress_reset", 0x0004FE6A,
                     "70abea51fe92f022617bae783fea1cb37223cfc1f9454003ea81b8493c3a7b68"),
        0x0004FE70: ("r1_battery_charging_cadence", 0x0004FF32,
                     "29f00e75116b1d16868e25b73f08a01ba21f20828cc22ddcdd4713dfba8710fb"),
        0x0004FF3C: ("r1_battery_charging_initial_curve", 0x00050004,
                     "9ea86a27b3e2625272a15695213e278f01c7feb31ed0a298ca78491a6afb5364"),
        0x00050004: ("r1_battery_discharge_curve", 0x000500BA,
                     "8220077c7133d7d5ce08ed96ba3f2e30d01086dafe1a6f12e259bb709343395b"),
    }
    for entry, (symbol, end, digest) in battery_behavior_expected.items():
        row = ownership_by_key[("application", f"0x{entry:08x}")]
        body = recovered[entry - recovered_base:end - recovered_base]
        if row["provider_family"] != "r1_product_specific" or \
                row["source_disposition"] != "clean_room_behavior_only" or \
                row["upstream_symbol"] != symbol or \
                hashlib.sha256(body).hexdigest() != digest:
            raise AssertionError(f"R1 battery behavior changed: 0x{entry:08x}")
    automatic_health_sync_expected = {
        0x0004CBB0: ("r1_authenticated_phone_connection_gate", 20,
                     "e746be099c4395ea100ed00817ebfeb3c5731834beb2747e8c4d6983f9139754"),
        0x0008B138: ("r1_automatic_health_sync_gate", 72,
                     "1a35e97a5125c92d884cf47bce5ec4f298c83074cedefa4bfe3f14f13f090a7b"),
        0x0008B818: ("r1_unsynchronized_sleep_batch_sync", 22,
                     "d6ebeeb0c6b17a81219a61d5c9748f595fd60ab32b07fa5188a186b235922021"),
        0x0008BAEC: ("r1_activity_history_sync", 848,
                     "02c16956b74720e338b7251b88d6af0f2b9c11895b734f66e317de9c4c5df15e"),
        0x0008C150: ("r1_heart_rate_history_sync", 842,
                     "dc1285911c51765504381c8177ca54c9619b9fe44c59ed063fac6e9d477d3c3f"),
        0x0008C750: ("r1_hrv_history_sync", 844,
                     "7acd63f9ecafc97fde7f19cba9446f51737e1ee7e47d56cd0359628d47648042"),
        0x0008CD60: ("r1_spo2_history_sync", 844,
                     "7828072e528c65a3f363768717ae2907681b96d1ce5dad7afbb95dd9e497ff89"),
    }
    for entry, (symbol, size, digest) in automatic_health_sync_expected.items():
        row = ownership_by_key[("application", f"0x{entry:08x}")]
        body = recovered_function(entry)
        if row["provider_family"] != "r1_product_specific" or \
                row["source_disposition"] != "clean_room_behavior_only" or \
                row["upstream_symbol"] != symbol or len(body) != size or \
                hashlib.sha256(body).hexdigest() != digest:
            raise AssertionError(
                f"R1 automatic health-sync behavior changed: 0x{entry:08x}"
            )
    activity_offline_expected = {
        0x0003BDD8: ("r1_activity_offline_queue_consume", 142,
                     "305cde7f9cb8be236cff6a630ec93abce98392eaba26f07e52e6eeea5c8fe0d2"),
        0x0003BED0: ("r1_activity_offline_queue_empty", 14,
                     "67fcd7ee83d2e426bbcd020ef70acfadb2ebe130f7656d220a0e2f1ef25a049e"),
        0x0003BEE4: ("r1_activity_offline_queue_enqueue", 242,
                     "99c1d053687332f6f6d9ab75132393c4ce1f7fb881760c2a9b843bd359c72fa5"),
        0x0003C0D8: ("r1_activity_sync_acknowledgement", 272,
                     "46e98644ffd3bd224644d25a0845fa0a88c22110c1930438947c4b2b94ffeb30"),
        0x0003CB80: ("r1_activity_offline_queue_merge", 334,
                     "39b683da864481896019553569aff64ee4b232954a5514500f501a1708d5fc64"),
    }
    for entry, (symbol, size, digest) in activity_offline_expected.items():
        row = ownership_by_key[("application", f"0x{entry:08x}")]
        body = recovered[entry - recovered_base:entry - recovered_base + size]
        if row["provider_family"] != "r1_product_specific" or \
                row["source_disposition"] != "clean_room_behavior_only" or \
                row["upstream_symbol"] != symbol or \
                row["size"] != str(size) or \
                hashlib.sha256(body).hexdigest() != digest:
            raise AssertionError(
                f"R1 activity offline-sync behavior changed: 0x{entry:08x}"
            )
    scalar_health_offline_expected = {
        0x0003FAA4: ("r1_heart_rate_offline_queue_consume", 142,
                     "601f73cde8a7bc1adf460265ed653eb26608827570cc74647704745b96b54487"),
        0x0003FB90: ("r1_heart_rate_offline_queue_empty", 14,
                     "67fcd7ee83d2e426bbcd020ef70acfadb2ebe130f7656d220a0e2f1ef25a049e"),
        0x0003FBA4: ("r1_heart_rate_offline_queue_enqueue", 186,
                     "528c888d328c0336195c1d7bd5ed0b71967c3e1edf21aa6ae9b68c3ea02724a3"),
        0x0003FCEC: ("r1_heart_rate_sync_acknowledgement", 272,
                     "c151aae5254e226d7e35ce1d5fb1ece7b4a938148c3441230d82423350d446ea"),
        0x00040700: ("r1_heart_rate_offline_queue_merge", 306,
                     "71aa183edeaf3bad5f358b853dd3c5d632bf694fea4a474fb9de946a14ea273d"),
        0x00040984: ("r1_hrv_offline_queue_consume", 148,
                     "cd659383195854fd85ebbaa2d837771d46ef7f46f175a5f891621664e5103d88"),
        0x00040A74: ("r1_hrv_offline_queue_empty", 14,
                     "67fcd7ee83d2e426bbcd020ef70acfadb2ebe130f7656d220a0e2f1ef25a049e"),
        0x00040A88: ("r1_hrv_offline_queue_enqueue", 190,
                     "8ac6c7231fce570c28ca84a06345b32b138ad7c2f9c106b05696f983cae176b6"),
        0x00040BD4: ("r1_hrv_sync_acknowledgement", 272,
                     "b8d57eff20cbf8bbf0974511706a14184316004c27a8101119e0244a4943f8b6"),
        0x00041638: ("r1_hrv_offline_queue_merge", 304,
                     "ae6d3409b7f2b8fcb5797463f6a9e60d6e8eb8713f41669fae46122da15b9640"),
        0x00043CA0: ("r1_spo2_offline_queue_consume", 142,
                     "721cbb521d61f9b7cecca16dc4fe7c5931b34f3c0117c87927ae63475d356aee"),
        0x00043D90: ("r1_spo2_offline_queue_empty", 14,
                     "67fcd7ee83d2e426bbcd020ef70acfadb2ebe130f7656d220a0e2f1ef25a049e"),
        0x00043DA4: ("r1_spo2_offline_queue_enqueue", 186,
                     "985d0a3f09c6adc8f3ca7141ddf28c1bb7f0441028fc63c01ea5fbf0152cd61f"),
        0x00043EB0: ("r1_spo2_sync_acknowledgement", 272,
                     "0acb6155808c2b7799476c43871f8a2ec38a81abed7ff6f90008277d8cbc383e"),
        0x000448B0: ("r1_spo2_offline_queue_merge", 306,
                     "5e41ad37d48c08635e372cc2364c04a98d05ac117d82ff481c286141e72ba591"),
    }
    for entry, (symbol, size, digest) in scalar_health_offline_expected.items():
        row = ownership_by_key[("application", f"0x{entry:08x}")]
        body = recovered[entry - recovered_base:entry - recovered_base + size]
        if row["provider_family"] != "r1_product_specific" or \
                row["source_disposition"] != "clean_room_behavior_only" or \
                row["upstream_symbol"] != symbol or row["size"] != str(size) or \
                hashlib.sha256(body).hexdigest() != digest:
            raise AssertionError(
                f"R1 scalar health offline-sync behavior changed: 0x{entry:08x}"
            )
    activity_daily_cache_expected = {
        0x00048288: ("r1_activity_daily_cache_reset", 30,
                     "7beb2d39482a69e371adffb65b14a0df64ac2763595d5eb4961f7f4b5880ee2e"),
        0x000482A8: ("r1_activity_daily_cache_read", 124,
                     "4ae6c99bb32b377253d86ace3629c39ecf7f12df7a381e527c4e58b05128c850"),
        0x0004832C: ("r1_activity_daily_cache_write", 30,
                     "8ff6f860f42ea830dae6f0cab97f770b3ae196e82a2775dc5ad4484e85a6bfc3"),
    }
    for entry, (symbol, size, digest) in activity_daily_cache_expected.items():
        row = ownership_by_key[("application", f"0x{entry:08x}")]
        body = recovered_function(entry)
        if row["provider_family"] != "r1_product_specific" or \
                row["source_disposition"] != "clean_room_behavior_only" or \
                row["upstream_symbol"] != symbol or len(body) != size or \
                hashlib.sha256(body).hexdigest() != digest:
            raise AssertionError(
                f"R1 activity daily-cache behavior changed: 0x{entry:08x}"
            )
    scalar_health_daily_cache_expected = {
        0x0007062C: ("r1_heart_rate_daily_cache_reset", 26,
                     "800b62608919a88d0cf34db07455c4335237a43b0d3c61f89af5e52982df5936"),
        0x00070648: ("r1_heart_rate_daily_cache_read", 88,
                     "7f98fbcbc10c0d7564e6dca198497fb89e47e4c4882a713b08c766d7acfdd106"),
        0x000706A4: ("r1_heart_rate_daily_cache_write", 26,
                     "ae498d295638441c1a6f46b46f4e31320b43cbcf4a6a8bb7b04a324ed887893b"),
        0x000706BE: ("r1_hrv_daily_cache_reset", 26,
                     "f4a86ec4286f18f864911061109b87063d94a31cd197c6abbfb756013734fbae"),
        0x000706D8: ("r1_hrv_daily_cache_read", 94,
                     "5241cad16c7e682056e5b6f25f103ad0c3d1b88af8ab97913360dfe0b6e76055"),
        0x0007073C: ("r1_hrv_daily_cache_write", 28,
                     "9dd7974520aa2ac186932885a80a7fdc9351078836a7e01a4f683aaea6a1f5b4"),
        0x00090DD4: ("r1_spo2_daily_cache_reset", 26,
                     "0fc63dc6ade30c59fe37b1c6f9fd6fd4f416986d8e245f9badcaf77f4070a79f"),
        0x00090DF0: ("r1_spo2_daily_cache_read", 88,
                     "dd590d0b7f810c1abd350573b42dbf593194b73873a54ad743b2151e4af9e928"),
        0x00090E4C: ("r1_spo2_daily_cache_write", 26,
                     "150e1b53fd4eb585b73557fbbdd9921ed3657099d4cbe1a3683854ef0e43966a"),
    }
    for entry, (symbol, size, digest) in scalar_health_daily_cache_expected.items():
        row = ownership_by_key[("application", f"0x{entry:08x}")]
        body = recovered_function(entry)
        if row["provider_family"] != "r1_product_specific" or \
                row["source_disposition"] != "clean_room_behavior_only" or \
                row["upstream_symbol"] != symbol or len(body) != size or \
                hashlib.sha256(body).hexdigest() != digest:
            raise AssertionError(
                f"R1 scalar health daily-cache behavior changed: 0x{entry:08x}"
            )
    scalar_health_storage_expected = {
        0x0005ACE0: ("r1_heart_rate_daily_cache_accessor", 4,
                     "06936d0536d64e86c623270163a043c1b484bbc978af8fbf56cd1650cbfb6587"),
        0x0005ACE8: ("r1_heart_rate_latest_sample_accessor", 28,
                     "da6a43bd3e679596d98d487f6b16e95f14d398b5f308b78819e58d56f18c65ee"),
        0x0005AD08: ("r1_heart_rate_daily_cache_refresh_metadata", 84,
                     "0149c2804e41a0e3d8a4935fa0628005b3480a93cc4a2d5f83452b14f0a117b3"),
        0x0005AD90: ("r1_heart_rate_sample_storage_aggregator", 220,
                     "2c2faf5817d9b459a42b0fb8469dfef737174aae0c0a3dfa9733d002bdd58dab"),
        0x0005AF18: ("r1_hrv_daily_cache_accessor", 4,
                     "06936d0536d64e86c623270163a043c1b484bbc978af8fbf56cd1650cbfb6587"),
        0x0005AF20: ("r1_hrv_latest_sample_accessor", 32,
                     "c45cfd732074c8b89858df45fd3977789e8b48463c2840592abab2a54cb40ada"),
        0x0005AF44: ("r1_hrv_daily_cache_refresh_metadata", 22,
                     "c5807aa54a723e84fbe3de5f99da9189c9f8f18c1c6af402e11f894f07e953b8"),
        0x0005AF60: ("r1_hrv_sample_storage_aggregator", 226,
                     "a3d50af5019c9c9df523d85e7394655468a7df18300610fcdabea0f315549406"),
        0x0005BAEC: ("r1_spo2_daily_cache_accessor", 4,
                     "06936d0536d64e86c623270163a043c1b484bbc978af8fbf56cd1650cbfb6587"),
        0x0005BAF4: ("r1_spo2_latest_sample_accessor", 28,
                     "da6a43bd3e679596d98d487f6b16e95f14d398b5f308b78819e58d56f18c65ee"),
        0x0005BB14: ("r1_spo2_daily_cache_refresh_metadata", 20,
                     "fcc1bfdaee98ac75b1b172b5e944d20fccd163a39ce9d30ee2f5f1f4be195e4a"),
        0x0005BB2C: ("r1_spo2_sample_storage_aggregator", 224,
                     "219518df0374821451f370f079250c5b9c0f2e59a3ea7218a7e84b0d7d0ef19d"),
        0x0008A80A: ("r1_heart_rate_event_storage_consumer", 52,
                     "7b38604669ced28aadd46d2798772ae71ed7dd3c7c5d9da3e792c9f9a7bff681"),
        0x0008A83E: ("r1_hrv_event_storage_consumer", 40,
                     "b903e154e0ef21e0da70d41b28519db011fbaefa66f2188f703d37bcb02b1a33"),
        0x0008A8AE: ("r1_spo2_event_storage_consumer", 42,
                     "5bc8f850dcfdeb2d7ec55fc779f0a92b7e3061c21c9c5267f819d1a38cdfe824"),
    }
    for entry, (symbol, size, digest) in scalar_health_storage_expected.items():
        row = ownership_by_key[("application", f"0x{entry:08x}")]
        body = recovered_function(entry)
        if row["provider_family"] != "r1_product_specific" or \
                row["source_disposition"] != "clean_room_behavior_only" or \
                row["upstream_symbol"] != symbol or len(body) != size or \
                hashlib.sha256(body).hexdigest() != digest:
            raise AssertionError(
                f"R1 scalar health sample-storage behavior changed: 0x{entry:08x}"
            )
    health_history_routing_expected = {
        0x00082BE8: ("r1_health_registration_dispatcher", 36,
                     "ff5e7848057eb0dea0cb0c7ab34611f8078e872058ed98ec2caed34c464c41c3"),
        0x00083298: ("r1_health_registration_binary_search", 58,
                     "08f095baacd3db6d15b3ba898b9bea78e5e88201eda5f4e5f3a6aeba34892313"),
        0x00082C10: ("r1_activity_refresh_handler", 52,
                     "38b7a30aaa28b66ced1d8db8098441027418b61c60a271b7d735b3061588bed3"),
        0x00082C44: ("r1_activity_daily_handler", 70,
                     "5e2461720215c94cc77eed9e32ff388a9cce6995c3682fd0999e68c7717c1187"),
        0x00082C8A: ("r1_heart_rate_daily_handler", 68,
                     "0d894dafa96718a3638b86f859c7f78749e510b9a65363804f00773e195a1b61"),
        0x00082CCE: ("r1_hrv_daily_handler", 70,
                     "e16ef0a20149f768089960c93ccce019a0389e3d40c936a15cb8c0946e91dde6"),
        0x00082D14: ("r1_sleep_daily_handler", 70,
                     "469a8cab4688bd659871bbeda25950bc45453c4a8327d6367cfa5f56b02f1e43"),
        0x00082D5A: ("r1_spo2_daily_handler", 68,
                     "9f70c796bdc8f65813c32e84196afdad27e2db4fec870653315ccb63ad40a941"),
        0x00082E34: ("r1_heart_rate_point_handler", 50,
                     "32ed4a2778d06affc3ebd1c2bf348c2fb3739a2d407fd2014e1375bf460228cc"),
        0x00082E66: ("r1_hrv_point_handler", 52,
                     "0315d7ca6369eb120efd44ec981a4291a073f30b1a7ad7a3124aa6717bdf2bae"),
        0x00082E9A: ("r1_spo2_point_handler", 52,
                     "0c84ec05328aa8a87b8132094fa6dfa5cf8dc6fb5d80e9445c9bf293196416cc"),
        0x0008B8E8: ("r1_health_event14_consumer", 408,
                     "2cc0295c20559ba8ea45db9c9a344edbb245d065daf4fa92871a7642c94329a4"),
    }
    for entry, (symbol, size, digest) in health_history_routing_expected.items():
        row = ownership_by_key[("application", f"0x{entry:08x}")]
        body = recovered_function(entry)
        if row["provider_family"] != "r1_product_specific" or \
                row["source_disposition"] != "clean_room_behavior_only" or \
                row["upstream_symbol"] != symbol or len(body) != size or \
                hashlib.sha256(body).hexdigest() != digest:
            raise AssertionError(
                f"R1 health-history routing behavior changed: 0x{entry:08x}"
            )
    activity_accumulator_expected = {
        0x00048D48: ("r1_activity_pending_delta_accessor", 78,
                     "b807b4e462d853fe5044855ff754544bc03b523dcbf68f8de44e837184bec661"),
        0x00048E68: ("r1_activity_periodic_accumulator", 380,
                     "9e8d594396de8cfaac2ec0bb9b6b66e954b1c07dbb8447da87bd362611fbb0fe"),
        0x00049068: ("r1_activity_explicit_refresh_accumulator", 252,
                     "a5436baeea82dcfdcd92ffa967adab36803e28864c6d6f0e32d3989ba3dcdbde"),
        0x0005AA14: ("r1_activity_delta_cache_accumulator", 246,
                     "90c63f8ffa27c90d548d4f0bb7f1400cf354a3aa8833e3314a249a61d7ca7f82"),
        0x0008A7F4: ("r1_activity_event_storage_consumer", 22,
                     "2c8c030600448ff01d2b39b56cedf3e5d64b5211934d814b71ee53143c769d29"),
    }
    for entry, (symbol, size, digest) in activity_accumulator_expected.items():
        row = ownership_by_key[("application", f"0x{entry:08x}")]
        body = recovered_function(entry)
        if row["provider_family"] != "r1_product_specific" or \
                row["source_disposition"] != "clean_room_behavior_only" or \
                row["upstream_symbol"] != symbol or len(body) != size or \
                hashlib.sha256(body).hexdigest() != digest:
            raise AssertionError(
                f"R1 activity accumulator behavior changed: 0x{entry:08x}"
            )
    activity_lifecycle_point_expected = {
        0x0005A9F0: ("r1_activity_daily_cache_accessor", 4,
                     "06936d0536d64e86c623270163a043c1b484bbc978af8fbf56cd1650cbfb6587"),
        0x0005A9F8: ("r1_activity_daily_cache_refresh_metadata", 22,
                     "7e8ac0b88c08644a1dcc7bb40debba51e3b478cf93b6107c7890248b4a3e8a66"),
        0x00083930: ("r1_heart_rate_point_response_wrapper", 66,
                     "e8525e642988dccd5218353948d9b90e269a42698ff6f0a049c94dd5bea50b35"),
        0x00083972: ("r1_hrv_point_response_wrapper", 66,
                     "5be0afbd7a6296c529e0df91825c13c8fb1645af137828d82eafdbad04a16741"),
    }
    for entry, (symbol, size, digest) in activity_lifecycle_point_expected.items():
        row = ownership_by_key[("application", f"0x{entry:08x}")]
        body = recovered_function(entry)
        if row["provider_family"] != "r1_product_specific" or \
                row["source_disposition"] != "clean_room_behavior_only" or \
                row["upstream_symbol"] != symbol or len(body) != size or \
                hashlib.sha256(body).hexdigest() != digest:
            raise AssertionError(
                f"R1 activity lifecycle/point behavior changed: 0x{entry:08x}"
            )
    health_crash_snapshot_expected = {
        0x00058914: ("r1_health_crash_provider_blob_clear", 34,
                     "7eb26f03d7b5a8707bced48531e9ebd2e909621d6aa02acb66f7d75cd9994dbf"),
        0x0005893C: ("r1_health_crash_snapshot_clear", 32,
                     "e67559e879afb244d2d2bd99ffd5228186b0393fb0fc7667279098895132d2f6"),
        0x00058960: ("r1_health_crash_time_clear", 28,
                     "419bbc925b895acd74a5f927d9382f43766aaa925fc4aceed878c5595973e2d7"),
        0x00058980: ("r1_health_crash_provider_blob_accessor", 42,
                     "c4d522e85c95c8668f46478e869d06446abac404694b569346f2ed95d25b2d6b"),
        0x000589B0: ("r1_health_crash_snapshot_accessor", 52,
                     "5bd3c20827924f79f7b4a29fe7e0a1bb0ccb1e1a616ff6efeaf19babfda560e4"),
        0x000589E8: ("r1_health_crash_time_accessor", 54,
                     "1b1762232d1e140abe54b8647965c420ecdbbf3a52dd6493e7e0faa00290b9f9"),
        0x00058A24: ("r1_health_crash_record_magic_probe", 22,
                     "b4d552ebdccaceccb6248c11714557bceed132e8a3793852a642be4b21483791"),
        0x00059EE4: ("r1_health_crash_snapshot_restore", 620,
                     "2563961270c5aa11adaf0e389b52fc3e7caed342539f9189c39cea9effa4c60a"),
        0x0005A28C: ("r1_health_crash_record_validator", 40,
                     "0649b54b32572df04c3e14b66122e968eb8521baafd599740efbdef11b830a7d"),
        0x0005A2B8: ("r1_health_crash_record_initializer", 104,
                     "c520dab61614b1e4647c24916cb5a06d68ebdb106a401ca18900c667aa1f5078"),
    }
    for entry, (symbol, size, digest) in health_crash_snapshot_expected.items():
        row = ownership_by_key[("application", f"0x{entry:08x}")]
        body = recovered_function(entry)
        if row["provider_family"] != "r1_product_specific" or \
                row["source_disposition"] != "clean_room_behavior_only" or \
                row["upstream_symbol"] != symbol or len(body) != size or \
                hashlib.sha256(body).hexdigest() != digest:
            raise AssertionError(
                f"R1 health crash-snapshot behavior changed: 0x{entry:08x}"
            )
    builder_row = ownership_by_key[("application", "0x0005a324")]
    builder_body = (
        recovered[0x0005A324 - 0x00027000:0x0005A3CE - 0x00027000] +
        recovered[0x0003F47C - 0x00027000:0x0003F530 - 0x00027000]
    )
    if builder_row["provider_family"] != "r1_product_specific" or \
            builder_row["source_disposition"] != "clean_room_behavior_only" or \
            builder_row["upstream_symbol"] != "r1_health_crash_snapshot_builder" or \
            int(builder_row["size"]) != 350 or len(builder_body) != 350 or \
            hashlib.sha256(builder_body).hexdigest() != \
            "8a1dfa00a7ffb6285c23c4456ccafa2fc0bc932311474dca1eadbfef7b27bbd2":
        raise AssertionError("R1 health crash-snapshot builder changed: 0x0005a324")
    retained_log_row = ownership_by_key[("application", "0x0007f030")]
    retained_log_body = recovered_function(0x0007F030)
    if retained_log_row["provider_family"] != "r1_product_specific" or \
            retained_log_row["source_disposition"] != "clean_room_behavior_only" or \
            retained_log_row["upstream_symbol"] != "r1_retained_log_printf_sink" or \
            len(retained_log_body) != 146 or \
            hashlib.sha256(retained_log_body).hexdigest() != \
            "c4537ceff474ee9645f623f81a6e5f86132a49f3170927b3c5d879aa1745f585":
        raise AssertionError("R1 retained-log behavior changed: 0x0007f030")
    health_db_accessor_row = ownership_by_key[("application", "0x00070028")]
    health_db_accessor_body = recovered_function(0x00070028)
    if health_db_accessor_row["provider_family"] != \
            "r1_health_storage_provider_adapter" or \
            health_db_accessor_row["source_disposition"] != \
            "clean_room_adapter_only_use_pinned_provider" or \
            health_db_accessor_row["upstream_symbol"] != \
            "r1_health_database_provider_handle_accessor" or \
            len(health_db_accessor_body) != 4 or \
            hashlib.sha256(health_db_accessor_body).hexdigest() != \
            "06936d0536d64e86c623270163a043c1b484bbc978af8fbf56cd1650cbfb6587":
        raise AssertionError(
            "R1 health database-accessor behavior changed: 0x00070028"
        )
    health_db_row = ownership_by_key[("application", "0x00070030")]
    health_db_body = recovered_function(0x00070030)
    if health_db_row["provider_family"] != "r1_product_specific" or \
            health_db_row["source_disposition"] != "clean_room_behavior_only" or \
            health_db_row["upstream_symbol"] != \
            "r1_health_database_startup_orchestrator" or \
            len(health_db_body) != 526 or \
            hashlib.sha256(health_db_body).hexdigest() != \
            "67cf421c59889f89122546e1bfc3b349b163d78a2b679c398144f13c9fec55db":
        raise AssertionError(
            "R1 health database-startup behavior changed: 0x00070030"
        )
    twi_sync_expected = {
        0x00054FF8: (
            "r1_twi_primary_register_read_adapter", 96,
            "c8acd79964fe902e645c7746a558e55c48193863ce1afd3ac589d89229230a64",
        ),
        0x0005505C: (
            "r1_twi_primary_register_write_adapter", 94,
            "85b332cad963abfdc137fb17b01ee74e1a49cdbe74fcae0b371b4c5a1c307ed0",
        ),
        0x000550C0: (
            "r1_twi_secondary_register_read_adapter", 90,
            "1f2765c8851ddaeda3f395bd94de4d461671d3b76daf54ae3bce067a1b3fe0ca",
        ),
        0x00055120: (
            "r1_twi_secondary_register_write_adapter", 90,
            "92b75b75fcbc59ee64b0a6ae5730da7e3429c19c79f642ea158d3e5af5ea9f9b",
        ),
        0x00055180: (
            "r1_twi_primary_shutdown_adapter", 44,
            "ef7e71c634d021e67e566cf392fe76491ce05b6130dbf74d23bd21ef5277df47",
        ),
        0x000551B4: (
            "r1_twi_secondary_shutdown_adapter", 44,
            "0885b4df0a2992d0477849ac51e3a37b72591056048b84fcaf94a0e31eacc52a",
        ),
        0x00055278: (
            "r1_twi_primary_initialize_configuration_adapter", 100,
            "4516b8fdac0d5e34250cc0b59617c94e06a17faf0d15e6d9bf880deadd81b08d",
        ),
        0x000552E4: (
            "r1_twi_secondary_initialize_configuration_adapter", 66,
            "9f391a5cad85e928b15715c8d0ead9bc34b40b4cd96797a96dbb4da73bc8c1fe",
        ),
        0x00070778: (
            "r1_twi_transfer_completion_adapter", 78,
            "ad1afebbb00454d0462173c6483d046232415ca58a07a27245e5ac8e3599a290",
        ),
        0x00070820: (
            "r1_twi_primary_wait_adapter", 100,
            "e01f111c235bb727f1c37721cde083152dcf02e91c05f3ba4a16e5a2a1d6c30b",
        ),
        0x0007088C: (
            "r1_twi_secondary_wait_adapter", 100,
            "5109e14190c48c15212304581af701dea173926b74dcc682d42aa6ad5dc599be",
        ),
    }
    for entry, (symbol, size, digest) in twi_sync_expected.items():
        row = ownership_by_key[("application", f"0x{entry:08x}")]
        body = recovered_function(entry)
        if row["provider_family"] != "r1_nordic_cmsis_provider_adapter" or \
                row["source_disposition"] != \
                "clean_room_adapter_only_use_nordic_sdk_and_cmsis" or \
                row["upstream_symbol"] != symbol or len(body) != size or \
                hashlib.sha256(body).hexdigest() != digest:
            raise AssertionError(
                f"R1 TWI synchronization behavior changed: 0x{entry:08x}"
            )
    bus_binding_expected = {
        0x00054F90: (
            "r1_twi_primary_device_binding_configuration", 44,
            "0e1b2dbfdc68ac597dc2f5cacc0e26a9b14466bb5afe1ce353fd89ce5766a7cc",
        ),
        0x00054FC4: (
            "r1_twi_secondary_device_binding_configuration", 44,
            "2a087f558d9bc124cf2ad77e0621ee2776ef8f87aee88270a35262dcf561d83b",
        ),
        0x00056508: (
            "r1_software_twi_i2c_2_binding_configuration", 18,
            "c7d415efc98ffaf074711600bdeaf04a11fec5528111b893e69c4797c499a826",
        ),
        0x00056520: (
            "r1_software_twi_i2c_3_binding_configuration", 18,
            "9e60cf6d29f5b93e12a23a50db834e92e71f77e55edadceb72f66bdb5a43d302",
        ),
        0x00056538: (
            "r1_software_twi_i2c_4_binding_configuration", 18,
            "0452b13b80732815593970ee5f5fbfd4e9ecf3f4c0e4e56f0496def65a6d0481",
        ),
        0x00056550: (
            "r1_software_twi_i2c_5_binding_configuration", 18,
            "c6003bad98c688df45118e27e1ef5b17b9f4552c584701d9e05b9aae86957979",
        ),
    }
    for entry, (symbol, size, digest) in bus_binding_expected.items():
        row = ownership_by_key[("application", f"0x{entry:08x}")]
        body = recovered_function(entry)
        if row["provider_family"] != \
                "r1_device_registry_configuration_adapter" or \
                row["source_disposition"] != \
                "clean_room_configuration_only_direct_typed_binding" or \
                row["upstream_symbol"] != symbol or len(body) != size or \
                hashlib.sha256(body).hexdigest() != digest:
            raise AssertionError(
                f"R1 bus binding configuration changed: 0x{entry:08x}"
            )
    software_twi_summary = summarize_software_twi(
        ROOT / "research" / "decompilation" / "rebuild" /
        "rebuilt-application.bin"
    )
    if software_twi_summary["function_count"] != 40 or \
            software_twi_summary["function_bytes"] != 3524 or \
            software_twi_summary["source_lineage"] != {
                "status": "unidentified_provider_candidate",
                "local_implementation_authorized": False,
                "reason": (
                    "Wire semantics and compiler-instantiated family structure are recovered, "
                    "but no exact attributable source, version, or license is established."
                ),
            }:
        raise AssertionError("software-TWI provider census metadata changed")
    for function in SOFTWARE_TWI_FUNCTIONS:
        entry = int(function["entry"])
        row = ownership_by_key[("application", f"0x{entry:08x}")]
        body = recovered_function(entry)
        if row["inventory_source"] != "manual_provenance_supplement" or \
                row["provider_family"] != \
                "unknown_software_twi_provider_candidate" or \
                row["source_disposition"] != \
                "investigate_before_implementing" or \
                row["upstream_symbol"] != function["symbol"] or \
                row["confidence"] != "high" or \
                len(body) != function["size"] or \
                hashlib.sha256(body).hexdigest() != function["sha256"]:
            raise AssertionError(
                f"software-TWI provider boundary changed: 0x{entry:08x}"
            )
    rtc_device_summary = summarize_rtc_device(
        ROOT / "research" / "decompilation" / "rebuild" /
        "rebuilt-application.bin"
    )
    if rtc_device_summary["function_count"] != 9 or \
            rtc_device_summary["function_bytes"] != 798 or \
            rtc_device_summary["provider_counts"] != {
                "unknown_rtc_device_provider_candidate": 7,
                "r1_device_registry_configuration_adapter": 1,
                "nordic_nrf5_sdk_17_1_0": 1,
            }:
        raise AssertionError("RTC-device boundary census metadata changed")
    rtc_manual_entries = {
        0x00056274, 0x00056318, 0x0005639C, 0x000563C4, 0x0007AD6C,
    }
    rtc_dispositions = {
        "unknown_rtc_device_provider_candidate":
            "investigate_before_implementing",
        "r1_device_registry_configuration_adapter":
            "clean_room_configuration_only_direct_typed_binding",
        "nordic_nrf5_sdk_17_1_0": "use_nordic_sdk",
    }
    for function in RTC_DEVICE_FUNCTIONS:
        entry = int(function["entry"])
        row = ownership_by_key[("application", f"0x{entry:08x}")]
        body = recovered_function(entry)
        expected_inventory = (
            "manual_provenance_supplement" if entry in rtc_manual_entries
            else "ghidra_functions_csv"
        )
        family = str(function["provider_family"])
        if row["inventory_source"] != expected_inventory or \
                row["provider_family"] != family or \
                row["source_disposition"] != rtc_dispositions[family] or \
                row["upstream_symbol"] != function["symbol"] or \
                row["confidence"] != "high" or \
                len(body) != function["size"] or \
                hashlib.sha256(body).hexdigest() != function["sha256"]:
            raise AssertionError(
                f"RTC-device/provider boundary changed: 0x{entry:08x}"
            )
    recovered_image_path = (
        ROOT / "research" / "decompilation" / "rebuild" /
        "rebuilt-application.bin"
    )
    pmic_transport_summary = summarize_pmic_transport(
        recovered_image_path,
        PMIC_DEFAULT_BASE,
        PMIC_DEFAULT_SCATTER_SOURCE,
        PMIC_DEFAULT_SCATTER_RUNTIME,
        PMIC_DEFAULT_SCATTER_LENGTH,
    )
    pmic_census = pmic_transport_summary["state_command_function_census"]
    if pmic_census["function_count"] != 15 or \
            pmic_census["function_bytes"] != 1018 or \
            pmic_census["vendor_candidate_bytes"] != 1000 or \
            pmic_census["local_transport_implementation_authorized"] is not False or \
            pmic_transport_summary["bus_descriptor"]["operations_address"] != \
            "0x200075a4" or \
            pmic_transport_summary["state_command_device"]["operations_address"] != \
            "0x20007614" or \
            pmic_transport_summary["state_command_device"]["operations"] != {
                "open": "0x0005657d", "close": "0x00056569",
                "read": "0x00056591", "write": "0x0005660d",
            }:
        raise AssertionError("YHM2710 STACMD boundary census metadata changed")
    yhm_manual_entries = {
        0x00028BB0, 0x00056568, 0x0005657C,
        0x00056590, 0x000565F4, 0x0005660C,
    }
    yhm_dispositions = {
        "yhmicros_yhm2710_candidate":
            "vendor_source_required_not_redistributable",
        "r1_device_registry_configuration_adapter":
            "clean_room_configuration_only_direct_typed_binding",
    }
    for function in YHM2710_STACMD_FUNCTIONS:
        entry = int(function["entry"])
        row = ownership_by_key[("application", f"0x{entry:08x}")]
        segments = function["segments"] or (
            (entry, int(function["end_exclusive"])),
        )
        body = b"".join(
            recovered[start - recovered_base:end - recovered_base]
            for start, end in segments
        )
        expected_inventory = (
            "manual_provenance_supplement" if entry in yhm_manual_entries
            else "ghidra_functions_csv"
        )
        family = str(function["provider_family"])
        if row["inventory_source"] != expected_inventory or \
                row["provider_family"] != family or \
                row["source_disposition"] != yhm_dispositions[family] or \
                row["upstream_symbol"] != function["symbol"] or \
                row["confidence"] != "high" or \
                int(row["size"]) != function["size"] or \
                len(body) != function["size"] or \
                hashlib.sha256(body).hexdigest() != function["sha256"]:
            raise AssertionError(
                f"YHM2710 STACMD provider boundary changed: 0x{entry:08x}"
            )
    watchdog_device_summary = summarize_watchdog_device(recovered_image_path)
    if watchdog_device_summary["function_count"] != 7 or \
            watchdog_device_summary["function_bytes"] != 386 or \
            watchdog_device_summary["provider_counts"] != {
                "r1_nordic_wdt_provider_adapter": 2,
                "r1_device_registry_configuration_adapter": 1,
                "nordic_nrf5_sdk_17_1_0": 4,
            } or watchdog_device_summary["recovered_configuration"] != {
                "behaviour": "run_in_sleep_pause_in_halt",
                "reload_milliseconds": 10_000,
                "interrupt_priority": 6,
                "reload_channels": 1,
            }:
        raise AssertionError("watchdog-device boundary census metadata changed")
    watchdog_dispositions = {
        "r1_nordic_wdt_provider_adapter":
            "clean_room_adapter_only_use_nordic_sdk",
        "r1_device_registry_configuration_adapter":
            "clean_room_configuration_only_direct_typed_binding",
        "nordic_nrf5_sdk_17_1_0": "use_nordic_sdk",
    }
    for function in WATCHDOG_DEVICE_FUNCTIONS:
        entry = int(function["entry"])
        row = ownership_by_key[("application", f"0x{entry:08x}")]
        body = recovered_function(entry)
        family = str(function["provider_family"])
        if row["inventory_source"] != "manual_provenance_supplement" or \
                row["provider_family"] != family or \
                row["source_disposition"] != watchdog_dispositions[family] or \
                row["upstream_symbol"] != function["symbol"] or \
                row["confidence"] != "high" or \
                len(body) != function["size"] or \
                hashlib.sha256(body).hexdigest() != function["sha256"]:
            raise AssertionError(
                f"watchdog-device/provider boundary changed: 0x{entry:08x}"
            )
    sensor_heap_summary = summarize_sensor_algorithm_heap(recovered_image_path)
    if sensor_heap_summary["function_count"] != 13 or \
            sensor_heap_summary["function_bytes"] != 1202 or \
            sensor_heap_summary["recovered_layout"] != {
                "control_pointer_storage": "0x20007c64",
                "pool_base_from_goodix_candidate_init": "0x2003024c",
                "control_block_bytes": 44,
                "bin_count": 2,
                "minimum_request_bytes": 8,
                "request_alignment_bytes": 4,
                "pool_start_alignment_bytes": 8,
                "block_header_bytes": 8,
                "minimum_split_remainder_bytes": 16,
                "minimum_pool_bytes_exclusive": 1024,
            } or sensor_heap_summary["source_lineage"][
                "local_implementation_authorized"
            ] is not False:
        raise AssertionError("sensor-algorithm heap provider census metadata changed")
    for function in SENSOR_ALGORITHM_HEAP_FUNCTIONS:
        entry = int(function["entry"])
        row = ownership_by_key[("application", f"0x{entry:08x}")]
        segments = function["segments"] or (
            (entry, int(function["end_exclusive"])),
        )
        body = b"".join(
            recovered[start - recovered_base:end - recovered_base]
            for start, end in segments
        )
        expected_family, expected_disposition, expected_confidence, _ = \
            SENSOR_ALGORITHM_HEAP_ROUTING[entry]
        if row["inventory_source"] != "ghidra_functions_csv" or \
                row["provider_family"] != expected_family or \
                row["source_disposition"] != expected_disposition or \
                row["upstream_symbol"] != function["symbol"] or \
                row["confidence"] != expected_confidence or \
                int(row["size"]) != function["size"] or \
                len(body) != function["size"] or \
                hashlib.sha256(body).hexdigest() != function["sha256"]:
            raise AssertionError(
                f"sensor-algorithm heap provider boundary changed: 0x{entry:08x}"
            )
    gomore_initializer_summary = summarize_gomore_initializer(recovered_image_path)
    if gomore_initializer_summary["function_count"] != 8 or \
            gomore_initializer_summary["function_bytes"] != 586 or \
            gomore_initializer_summary["root"] != "0x00071a32" or \
            gomore_initializer_summary["root_caller_entry"] != "0x0006fea0" or \
            gomore_initializer_summary["source_lineage"][
                "local_implementation_authorized"
            ] is not False:
        raise AssertionError("GoMore initializer boundary census metadata changed")
    for function in GOMORE_INITIALIZER_FUNCTIONS:
        entry = int(function["entry"])
        row = ownership_by_key[("application", f"0x{entry:08x}")]
        body = recovered[entry - recovered_base:
                         int(function["end_exclusive"]) - recovered_base]
        if row["inventory_source"] != "ghidra_functions_csv" or \
                row["provider_family"] != "gomore_health_algorithm_candidate" or \
                row["source_disposition"] != \
                "vendor_source_required_not_redistributable" or \
                row["confidence"] != "candidate" or \
                int(row["size"]) != function["size"] or \
                len(body) != function["size"] or \
                hashlib.sha256(body).hexdigest() != function["sha256"]:
            raise AssertionError(
                f"GoMore initializer boundary changed: 0x{entry:08x}"
            )
    crash_tail = recovered[0x0003F47C - 0x00027000:0x0003F530 - 0x00027000]
    if len(crash_tail) != 180 or hashlib.sha256(crash_tail).hexdigest() != \
            "3e93df87c819a5a0437f0088e8c46044c688c19cd8da4abb644ece9035ce29b3":
        raise AssertionError("R1 health crash-snapshot tail block changed")
    time_calendar_boundary_expected = {
        0x0005A7BC: ("time_calendar_unix_to_broken_down", 228, "ac4d22d58eb42e36457e68f4b787ccab86ea1a70f840da8c71ddd1c4fe4783ea"),
        0x0005A8AC: ("time_calendar_broken_down_to_unix", 216, "c46cb078d69f911a7f4ede4bbd0d0c12ba87b44535d05c615ec3bd44c564af78"),
        0x0005A990: ("time_clock_backend_snapshot", 32, "c49cbf15c91b3d21c6903b0c9c92d5c2d598c08fcfdd8a032ad85c6ebf9b6a62"),
        0x0005AC74: ("time_activity_ten_minute_bucket", 50, "8258898551d51a347e2dc9b680fdcd15334a7d92fcfc67700ba4e952ba2eff79"),
        0x0005ACA6: ("time_local_hour", 30, "db2097db7d8c2d10a00813bc7a975efb3d86cc2c3015450f731f54e5adec3c02"),
        0x0008AD40: ("time_local_timestamp", 28, "4e3cc9f66d44e4d5151bd11d0193c4c29defd429cad08d6c1b98428b9dae3213"),
        0x0008AD64: ("time_local_day_start", 44, "014d0d12283782cc42835fcacc42f5da85f00ec083fffffe8cf8d9e6dc5884ef"),
        0x0008AD98: ("time_status_accessor", 6, "83bf9b6c537471a134b89fdc8be3c871e03df2082c405ecdfaacfaceafedb021"),
        0x0008ADA4: ("time_backend_timestamp_thunk", 10, "571d07446347362a5115a6a056aecaeef7c5098efd08f2c2aa54a5b85fe8c63f"),
        0x0008ADB4: ("time_utc_offset_accessor", 8, "602c8c71b053148eff399239231d18cc077a6d08376289d9e4b489579c05cbcb"),
        0x0008AE58: ("time_calendar_to_utc_adapter", 76, "32b98c5ff754c88c235bede78d917bc7ec7613efbf5328ac53f691d3fc6a7bd7"),
        0x0008AEA4: ("time_update_flag_setter", 8, "e18ee6b3245d02a7240a6dab0254bc5b1818da0263db5fa9871088e533237371"),
        0x0008AEB0: ("time_backend_update_adapter", 136, "fe763046ecf9d9a8c09fbf0644ec1bcbd7089faf1d76f669f83dfb18339a0587"),
        0x0008AF40: ("time_utc_to_calendar_adapter", 74, "8442de58aab46b780dbd062ac008e8d7d045982de4f38a484206b3d14feb2b3d"),
    }
    for entry, (symbol, size, digest) in time_calendar_boundary_expected.items():
        row = ownership_by_key[("application", f"0x{entry:08x}")]
        body = recovered_function(entry)
        if row["provider_family"] != "unknown_time_calendar_provider_candidate" or \
                row["source_disposition"] != "investigate_before_implementing" or \
                row["upstream_symbol"] != symbol or len(body) != size or \
                hashlib.sha256(body).hexdigest() != digest:
            raise AssertionError(
                f"time/calendar provider boundary changed: 0x{entry:08x}"
            )
    temperature_stress_cache_expected = {
        0x0005AB6C: ("r1_shared_hourly_accumulator_snapshot", 48,
                     "b74c5922f418626358ebc50a329da3a21491332e4a71f37d51177f8d79d7cc6c"),
        0x0005ABA0: ("r1_shared_u8_hourly_average", 152,
                     "54736b7b56bde2c42c36c445bb119027c03a652f8416fc604ca82f1653cc6848"),
        0x0005BCCC: ("r1_stress_daily_cache_accessor", 4,
                     "06936d0536d64e86c623270163a043c1b484bbc978af8fbf56cd1650cbfb6587"),
        0x0005BCD4: ("r1_stress_daily_cache_refresh_metadata", 20,
                     "f3ca3c0277320be3a8cb0a53e34e75942aea91cea3cba9986cf7f5a81e1fa33c"),
        0x0005BCEC: ("r1_stress_sample_storage_aggregator", 220,
                     "5141c95e2effacf13e132c8bbf97e7ee2b1ddcde8226adc379acbf803724ea41"),
        0x0005BE5C: ("r1_temperature_daily_cache_accessor", 4,
                     "06936d0536d64e86c623270163a043c1b484bbc978af8fbf56cd1650cbfb6587"),
        0x0005BE64: ("r1_temperature_daily_cache_refresh_metadata", 20,
                     "ddffa6a9d531bb13b398e2be366b7d24f03b26a81e6a459f0c1d3edd13342abb"),
        0x0005BE7C: ("r1_temperature_sample_storage_aggregator", 248,
                     "7b8db4e9a6bf5ad8d8391f5ba9d1138e222a8a1cedb81ba754282e9dee68c489"),
        0x0005ACC4: ("r1_shared_hourly_accumulator_restore", 24,
                     "6aa6b17190d13347fb6ac54f11b0efb3f95c1c059b6a7d83f047648e2bc61c44"),
        0x0008A8D8: ("r1_stress_event_storage_consumer", 36,
                     "69f01f7386e5f6635632ee06563299c88f95c46ffe7027f954345bfdc9c72567"),
        0x0008A8FC: ("r1_temperature_event_storage_consumer", 44,
                     "9b7722026f3f79e3ddfc03fab438f004fd4b51f1aa0cc9a4ba272914ff2f4cf7"),
        0x00091124: ("r1_stress_daily_cache_reset", 26,
                     "6a2af6247e7a7644a10749e1bfa9f9e2c5b73c4b56e6ce1f82ecfeffbf491987"),
        0x0009113E: ("r1_stress_daily_cache_read", 26,
                     "be1a5a382df0d73d346bba550551db03de167a560f1c2e358bf51a4c36385967"),
        0x00091158: ("r1_stress_daily_cache_write", 26,
                     "30000ecadfe2a7b1ffd38113c40dda4f3ffdae43c5f1f020642368553d8d9842"),
        0x000918DE: ("r1_temperature_daily_cache_reset", 26,
                     "47bc9c4de0976d85ef7124264b097822457ea760c8834498fab08e28a949e18d"),
        0x00091918: ("r1_temperature_daily_cache_read", 56,
                     "79962b493ae679648063ea25a844f774629cca4f0042d72575ed38307c7de6b4"),
        0x00091954: ("r1_temperature_daily_cache_write", 26,
                     "6bdfc2d55b366385c677e0f1d6228b61d9d9adf9cf1c9c2aefbd9229304bffe6"),
    }
    for entry, (symbol, size, digest) in temperature_stress_cache_expected.items():
        row = ownership_by_key[("application", f"0x{entry:08x}")]
        body = recovered_function(entry)
        if row["provider_family"] != "r1_product_specific" or \
                row["source_disposition"] != "clean_room_behavior_only" or \
                row["upstream_symbol"] != symbol or len(body) != size or \
                hashlib.sha256(body).hexdigest() != digest:
            raise AssertionError(
                f"R1 temperature/stress cache behavior changed: 0x{entry:08x}"
            )
    time_health_rollover_expected = {
        0x0005DCE8: (
            "r1_health_hour_boundary_storage_orchestrator", 432,
            "6deba6a1fcfee07f3d002b8bffecd25311bb73e72e2fbfb67200cd2acb87c3d7",
        ),
        0x0005E698: (
            "r1_health_time_transition_storage_orchestrator", 702,
            "8023ab609d648f0a06c47864630803cce186b3281e8ed4dabf5253b88c5d2462",
        ),
    }
    for entry, (symbol, size, digest) in time_health_rollover_expected.items():
        row = ownership_by_key[("application", f"0x{entry:08x}")]
        body = recovered_function(entry)
        if row["provider_family"] != "r1_health_storage_provider_adapter" or \
                row["source_disposition"] != \
                "clean_room_adapter_only_use_pinned_provider" or \
                row["upstream_symbol"] != symbol or len(body) != size or \
                hashlib.sha256(body).hexdigest() != digest:
            raise AssertionError(
                f"R1 health time/hour adapter changed: 0x{entry:08x}"
            )
    gomore_time_adapter = ownership_by_key[("application", "0x0005dc08")]
    gomore_time_body = recovered_function(0x0005DC08)
    if gomore_time_adapter["inventory_source"] != "manual_provenance_supplement" or \
            gomore_time_adapter["provider_family"] != "r1_gomore_provider_adapter" or \
            gomore_time_adapter["source_disposition"] != \
            "clean_room_adapter_only_use_licensed_provider" or \
            gomore_time_adapter["upstream_symbol"] != \
            "r1_gomore_time_transition_adapter" or \
            len(gomore_time_body) != 86 or \
            hashlib.sha256(gomore_time_body).hexdigest() != \
            "fc72eda6d9921b4c09e94214ac0d1b66bc3afdfa40fbdda80a213e76e1999d85":
        raise AssertionError("R1 GoMore time-transition adapter changed")
    activity_day_merge_expected = {
        0x0003BCF8: ("r1_activity_acknowledgement_timestamp_clamp", 84,
                     "960f99f03806a862815a3c7956ad23fa6020069ebe3d6fceb29ba5d1cdd12fe1"),
        0x0003BDAC: ("r1_activity_day_builder_reset", 42,
                     "f266fe7c2459ffb46732cd756100bbc96544010ae1ec6efd12f052721ac923b0"),
        0x0003C304: ("r1_activity_ram_cache_merge", 414,
                     "58626295e722cc6b0ee3acdf461daa58b8cb417bcfc13617ff6a24a6d54b6f37"),
        0x0003C578: ("r1_activity_day_packet_flush", 542,
                     "691a2c3049261a3b526e71d1037e7ad85fd849dba1bed8c1f7d28bca94961780"),
        0x0003C958: ("r1_activity_flash_record_merge", 428,
                     "1b17689eb406f988a5049b9b697ed74c7bf550c30435f3a092ffd359822991c2"),
    }
    for entry, (symbol, size, digest) in activity_day_merge_expected.items():
        row = ownership_by_key[("application", f"0x{entry:08x}")]
        body = recovered_function(entry)
        if row["provider_family"] != "r1_product_specific" or \
                row["source_disposition"] != "clean_room_behavior_only" or \
                row["upstream_symbol"] != symbol or len(body) != size or \
                hashlib.sha256(body).hexdigest() != digest:
            raise AssertionError(
                f"R1 activity day-merge behavior changed: 0x{entry:08x}"
            )
    cmbacktrace_provider_expected = {
        "0x0002746a": "cmb_get_psp",
        "0x00027470": "cmb_get_sp",
        "0x000584f0": "cm_backtrace_call_stack_any",
        "0x000588a4": "cm_backtrace_init",
        "0x0005c568": "disassembly_ins_is_bl_blx",
        "0x0005cd14": "dump_stack",
        "0x000634cc": "fault_diagnosis",
    }
    for entry, symbol in cmbacktrace_provider_expected.items():
        row = ownership_by_key[("application", entry)]
        if row["provider_family"] != "armink_cmbacktrace_1_4_2_compatible" or \
                row["source_disposition"] != \
                "use_authenticated_upstream_snapshot" or \
                row["upstream_symbol"] != symbol:
            raise AssertionError(f"CmBacktrace provider function not routed: {entry}")
    cmbacktrace_machine_accessor_expected = {
        0x0002746A: (
            6, "8e4e19e92c6716850c14126bd4e27ba37c0ae28804278e410d30557268987b2a",
        ),
        0x00027470: (
            4, "b399bb91d6a08cd0b438f51e1de05f7bea45db4f557cee86d89c1147844f56d8",
        ),
    }
    for entry, (size, digest) in cmbacktrace_machine_accessor_expected.items():
        body = recovered_function(entry)
        if len(body) != size or hashlib.sha256(body).hexdigest() != digest:
            raise AssertionError(
                f"CmBacktrace machine accessor changed: 0x{entry:08x}"
            )
    for entry in (
        "0x000274ac", "0x000274b8", "0x000274c4", "0x000274d0",
        "0x000274dc", "0x000585bc", "0x0005882c", "0x0006a098",
        "0x0006a0b0", "0x00081918", "0x00096138", "0x0009613c",
        "0x000964b0", "0x000964bc",
        "0x0008ef28",
    ):
        row = ownership_by_key[("application", entry)]
        if row["provider_family"] != "r1_cmbacktrace_provider_adapter" or \
                row["source_disposition"] != \
                "clean_room_adapter_only_use_authenticated_provider":
            raise AssertionError(f"CmBacktrace adapter not bounded: {entry}")
    cmbacktrace_stack_accessor_expected = {
        0x00096138: (4, "a89b85f8bccd76763270edbe8d4a9000e557118189ef0a663b750b93593d16da"),
        0x0009613C: (30, "a17f6f6bcd131f398671567d197bc2515901f9d842dc40ebf1b05f936bab29ca"),
        0x000964B0: (8, "9cd316d2bba2c933a7ebdc6fd744ff6d57d624385b2451e75ed0abecbc440d88"),
        0x000964BC: (8, "10004dc66a53ea31d99cfb0989cb33e2f4633832af53441bebf444318459cabf"),
    }
    for entry, (size, digest) in cmbacktrace_stack_accessor_expected.items():
        body = recovered_function(entry)
        if len(body) != size or hashlib.sha256(body).hexdigest() != digest:
            raise AssertionError(f"CmBacktrace stack accessor changed: 0x{entry:08x}")
    tiny_aes_expected = {
        0x00048948: ("AddRoundKey", 24, "5305f01cc65dffe6d0c91b7059034b9ed0b7fec55700853f220cc8fc3f407805"),
        0x00048AC8: ("InvCipher", 58, "30a2101a3d293387c1452a151c190a4cac1b03fd6dddffbe2f68bcad0838bf3a"),
        0x00061740: ("KeyExpansion", 176, "ecda5007703afece9d2e4e83b477cc0911e184232feb12e8bbc0f0da074b31d4"),
        0x0007272E: ("InvMixColumns", 206, "dc1bf5f53c69b3fe65e09c27ce88228c18c5767a12f934ed7aab77fb86d0598a"),
        0x000727FC: ("InvShiftRows", 50, "194d6de33493d6c8606e9e06d758c2f81cdaead3ba44ffced415360b30103aa8"),
        0x00072830: ("InvSubBytes", 18, "7fe64ea12089cdf62367ddf1d886f237b99711e2d2d7cb776687aa5a87392f53"),
        0x00076570: ("Multiply", 108, "020943b537ad8e3d284f988dc9d3b433649bf0035a04636d6f04f73b95f28ae3"),
        0x00098E38: ("xtime", 20, "cf87ec783823c0f5d2eb6ee2215fe6bbb7b526c46dadcb397036be438c4a8e18"),
    }
    for entry, (symbol, size, digest) in tiny_aes_expected.items():
        row = ownership_by_key[("application", f"0x{entry:08x}")]
        body = recovered_function(entry)
        if row["provider_family"] != "kokke_tiny_aes_c_v1_0_0_compatible" or \
                row["source_disposition"] != "use_pinned_upstream" or \
                row["upstream_symbol"] != symbol or len(body) != size or \
                hashlib.sha256(body).hexdigest() != digest:
            raise AssertionError(f"tiny-AES-c provider function mismatch: 0x{entry:08x}")
    r1_crypto_product_expected = {
        0x00048B02: (
            "r1_dual_aes128_decrypt", 162,
            "6f9df679f4f70bb0bc98d13fb0c0212f85c27fbaa383f54f6004059e2ea8fc30",
        ),
        0x000891A4: (
            "r1_dual_aes128_decrypt_callback", 20,
            "4d2068ba464fdf4d211022a41b59f0a0a96f7492ba1d151072dabdee9943161c",
        ),
        0x00098E22: (
            "r1_xor_bytes", 22,
            "d12d9b92bc19b5ef724648a51e28b0b8475c91f96dfeca39ca3c6d9a708fc85c",
        ),
    }
    for entry, (symbol, size, digest) in r1_crypto_product_expected.items():
        row = ownership_by_key[("application", f"0x{entry:08x}")]
        body = recovered_function(entry)
        if row["provider_family"] != "r1_product_specific" or \
                row["source_disposition"] != "clean_room_behavior_only" or \
                row["upstream_symbol"] != symbol or len(body) != size or \
                hashlib.sha256(body).hexdigest() != digest:
            raise AssertionError(f"R1 crypto product function mismatch: 0x{entry:08x}")
    gomore_candidate_expected = {
        0x00049410: (506, "a5898f09a8c50776e5f37aa43887223d989544b89ad9c5408489a73c5456407b"),
        0x0004BD98: (768, "e7c30f46d5d286ac2caaf99aee96458c233d9b690376e947e693da62a30c3665"),
        0x0006AD80: (282, "538ef0577e0848c8ee0f4a53c0e5b743e6a0b35dcbaa7044536441f588f529ad"),
        0x0006AFB0: (180, "8e27cb74b1de910c0a6358e97a1f011762df1e624ed42a271a1b40c8e2605fc8"),
        0x0006B27C: (374, "2b593ce1c6b887e64f8016434c9f92e2aad3e3d5da5fa7f4c9f138393dac9a69"),
        0x0006B50C: (318, "a4becd15f14171d74d4321de59447ba8aae9e480e79d0f39bd0ebdaf1b8b5dfd"),
        0x0006BBB0: (824, "8bad5c89f7ef2cae30d6bfcae6157ae5c68b2310a70bde6dcd8e5242d99d5b3e"),
        0x0006C1C0: (114, "9f749003c19d8352717b8e06a49c31caaa34ae58eef28a572a1afc64ce3cc81a"),
        0x0006C294: (456, "868b40495fff401072e6c4e9b179ed22b3e824d929332353f9e5b772152d9c15"),
        0x000823D8: (106, "17b7aa15c050b7edca760d12444202017f07235b9454074d90ebf90558d52675"),
    }
    for entry, (size, digest) in gomore_candidate_expected.items():
        row = ownership_by_key[("application", f"0x{entry:08x}")]
        body = recovered_function(entry)
        if row["provider_family"] != "gomore_health_algorithm_candidate" or \
                row["source_disposition"] != \
                "vendor_source_required_not_redistributable" or \
                len(body) != size or hashlib.sha256(body).hexdigest() != digest:
            raise AssertionError(f"GoMore provider boundary changed: 0x{entry:08x}")
    iqs7211e_adapter_expected = {
        0x0002F866: ("r1_iqs7211e_factory_communication_end", 26, "c0be1a7263d61a284d93f8c515617c9dd67b154f472df92bb997451d27591398"),
        0x0002F880: ("r1_iqs7211e_configure", 1274, "0830ef249ab5667861df31b202524dd4408560ba980785efc0404cd63cb52779"),
        0x0002FDC8: ("r1_iqs7211e_irq_config_refresh", 26, "ca5ed53235e06a50818676c5be96ea8159d91d1ba9c6d324dd343519af34e928"),
        0x0002FDE2: ("r1_iqs7211e_communication_end", 20, "65403993dea45c16b8ff9d365dc30cb90e3cb55000a22d06ae47420ded60d5bc"),
        0x0002FDF8: ("r1_iqs7211e_suspend", 80, "f5092d330a775ec8e8802bc6769fee9e716c0a08c8972df3ea5a9de4e56c3760"),
        0x0002FE9C: ("r1_iqs7211e_register_read_port", 16, "2fada6b5898c52613ff6ef94fb08821102b5b0c23521e90ba9a85927e51b41c9"),
        0x0002FEAC: ("r1_iqs7211e_register_write_port", 52, "19fbbdad063a3d748cca926317d83bca4b2da03bf244358dc332e7aaf3092061"),
        0x00030E6C: ("r1_iqs7211e_irq_worker", 434, "eb01bdaf164f4abc29b72af4c94cdc69ba5df688796aec8828326592264af37f"),
        0x00046650: ("r1_iqs7211e_touch_task_dispatcher", 578, "3019299c9c23cbed488c51229722b18cf0166ccae126bef2cdc3a49b615fab00"),
        0x0006F9E4: ("r1_iqs7211e_ati_recovery_policy", 300, "1b508f0430a596d1b61b5a4e8bc92e4b1b0f2a86b0174b897c04809af50c3dcd"),
        0x0006FCE8: ("r1_iqs7211e_reset_reconfigure", 120, "2e373b0fca801d54c48d56616f8ebc356cff664741ec912c04982853c251f1d2"),
        0x00087BA4: ("r1_iqs7211e_read_word_adapter", 24, "6a33d9dd3c91afb15a8a6d3b8ae7bec62d3b91630877a7f5e15ce292bfcc9444"),
    }
    for entry, (symbol, size, digest) in iqs7211e_adapter_expected.items():
        row = ownership_by_key[("application", f"0x{entry:08x}")]
        body = (b"".join(
            recovered[start - recovered_base:end - recovered_base]
            for start, end in R1_TOUCH_TASK_DISPATCHER_FUNCTIONS[0]["segments"]
        ) if entry == 0x00046650 else recovered_function(entry))
        expected_disposition = ("clean_room_configuration_only_use_pinned_provider"
                                if entry == 0x0002F880 else
                                "clean_room_adapter_only_use_pinned_provider")
        if row["provider_family"] != "r1_iqs7211e_provider_adapter" or \
                row["source_disposition"] != expected_disposition or \
                row["upstream_symbol"] != symbol or \
                len(body) != size or hashlib.sha256(body).hexdigest() != digest:
            raise AssertionError(f"R1 IQS7211E adapter boundary changed: 0x{entry:08x}")
    named_peripheral_candidates = {
        "gxcas_gxt310_candidate": {
            0x00050F9C: (138, "e85aa5da2c0263ec52b56abad76046a18eca7a341efe9f9b8a1ebead6ce6276d"),
            0x0006F804: (8, "0a099318ad9c76b025b0aa229e8de6332ef6956114081adf0972d7ab88684700"),
            0x0006F818: (98, "4820600616f6417670ae3535521aa4e72c9759af8070d999489955bc1d26fd4e"),
            0x0006F81E: (8, "4811461d8532e3b7b0f3a00ac062c333edd814247df6d0f610af4887153ded1f"),
            0x0006F832: (6, "f90cb138b31c3ba9bccefdd8fff04b86cd25268c55f846f56b347f703d0273ec"),
        },
        "yhmicros_yhm2710_candidate": {
            0x0003510C: (224, "abec91957c0fa9eb17711fe536959bc508912b6625d683e220882717889e3181"),
            0x000355BC: (106, "460a383a2a811399bdcc6b424e0de7b4316228996121cac373000d3853cb05ca"),
            0x0004E9E8: (4, "f3e11bb0100d0c9e35506027d631a68d15b6969aa0c140d73164a86f1f1b2e27"),
            0x0005079C: (4, "b1322d2a50626c62b1d53606d9839bbd54b123ab62b7fe729766d35540450a2c"),
        },
    }
    for provider, expected_functions in named_peripheral_candidates.items():
        for entry, (size, digest) in expected_functions.items():
            row = ownership_by_key[("application", f"0x{entry:08x}")]
            body = recovered_function(entry)
            if row["provider_family"] != provider or row["source_disposition"] != \
                    "vendor_source_required_not_redistributable" or \
                    len(body) != size or hashlib.sha256(body).hexdigest() != digest:
                raise AssertionError(f"Named peripheral boundary changed: 0x{entry:08x}")
    goodix_integrity_summary = summarize_goodix_integrity(recovered_image_path)
    if goodix_integrity_summary["function_count"] != 7 or \
            goodix_integrity_summary["function_bytes"] != 236 or \
            goodix_integrity_summary["newly_resolved_function_count"] != 5 or \
            goodix_integrity_summary["newly_resolved_function_bytes"] != 162 or \
            goodix_integrity_summary["recovered_semantics"]["packed_word_bits"] != 24 or \
            goodix_integrity_summary["recovered_semantics"]["integrity_bit"] != 0 or \
            tuple(int(word, 16) for word in goodix_integrity_summary[
                "recovered_semantics"]["table_words"]
            ) != INTEGRITY_TABLE_WORDS or \
            any(table["sha256"] != INTEGRITY_TABLE_SHA256
                for table in goodix_integrity_summary["tables"]) or \
            goodix_integrity_summary["source_lineage"][
                "local_implementation_authorized"
            ] is not False:
        raise AssertionError("Goodix packed-word integrity census metadata changed")
    newly_resolved_integrity_entries = {
        int(function["entry"]) for function in GOODIX_INTEGRITY_NEW_FUNCTIONS
    }
    for function in GOODIX_INTEGRITY_FUNCTIONS:
        entry = int(function["entry"])
        row = ownership_by_key[("application", f"0x{entry:08x}")]
        body = recovered[entry - recovered_base:
                         int(function["end_exclusive"]) - recovered_base]
        if row["provider_family"] != "goodix_gh3x2x_candidate" or \
                row["source_disposition"] != \
                "vendor_source_required_not_redistributable" or \
                row["confidence"] != "high" or \
                int(row["size"]) != function["size"] or \
                len(body) != function["size"] or \
                hashlib.sha256(body).hexdigest() != function["sha256"]:
            raise AssertionError(
                f"Goodix packed-word integrity boundary changed: 0x{entry:08x}"
            )
        if entry in newly_resolved_integrity_entries and \
                "packed_24_bit_integrity" not in row["evidence"]:
            raise AssertionError(
                f"Goodix packed-word integrity role missing: 0x{entry:08x}"
            )
    goodix_nadt_summary = summarize_r1_goodix_nadt_boundary(recovered_image_path)
    if goodix_nadt_summary["function_count"] != 58 or \
            goodix_nadt_summary["function_bytes"] != 19274 or \
            goodix_nadt_summary["newly_routed_function_count"] != 57 or \
            goodix_nadt_summary["newly_routed_function_bytes"] != 19148 or \
            goodix_nadt_summary["identity"]["component"] != "Goodix GH_NADT" or \
            goodix_nadt_summary["identity"]["version"] != "v1.0.2.0" or \
            goodix_nadt_summary["identity"]["component_hash"] != "548d894d" or \
            goodix_nadt_summary["identity"]["streaming_period_samples"] != 25 or \
            goodix_nadt_summary["boundary"]["provider_family"] != \
            "goodix_gh3x2x_candidate" or \
            goodix_nadt_summary["boundary"]["source_disposition"] != \
            "vendor_source_required_not_redistributable" or \
            goodix_nadt_summary["boundary"][
                "local_algorithm_reimplementation_authorized"
            ] is not False or \
            goodix_nadt_summary["boundary"][
                "toolchain_runtime_and_sensor_heap_excluded"
            ] is not True:
        raise AssertionError("Goodix GH_NADT provider-boundary metadata changed")
    for function in GOODIX_NADT_FUNCTIONS:
        entry = int(function["entry"])
        row = ownership_by_key[("application", f"0x{entry:08x}")]
        segments = function["segments"] or (
            (entry, int(function["end_exclusive"])),
        )
        body = b"".join(
            recovered[start - recovered_base:end - recovered_base]
            for start, end in segments
        )
        if row["provider_family"] != "goodix_gh3x2x_candidate" or \
                row["source_disposition"] != \
                "vendor_source_required_not_redistributable" or \
                row["confidence"] != "high" or \
                int(row["size"]) != function["size"] or \
                len(body) != function["size"] or \
                hashlib.sha256(body).hexdigest() != function["sha256"]:
            raise AssertionError(
                f"Goodix GH_NADT provider boundary changed: 0x{entry:08x}"
            )
    goodix_hr_summary = summarize_r1_goodix_hr_boundary(recovered_image_path)
    if goodix_hr_summary["function_count"] != 31 or \
            goodix_hr_summary["function_bytes"] != 7144 or \
            goodix_hr_summary["identity"]["component"] != "Goodix GH_HR" or \
            goodix_hr_summary["identity"]["existing_provider_root"] != \
            "0x0006d51c" or \
            goodix_hr_summary["identity"]["root_callsite"] != "0x0006d5fa" or \
            goodix_hr_summary["identity"]["largest_new_entry"] != \
            "0x00032808" or \
            goodix_hr_summary["closure"]["maximum_call_depth"] != 4 or \
            goodix_hr_summary["closure"]["outside_direct_callers"] != 0 or \
            goodix_hr_summary["closure"][
                "toolchain_runtime_and_sensor_heap_excluded"
            ] is not True or \
            goodix_hr_summary["boundary"]["provider_family"] != \
            "goodix_gh3x2x_candidate" or \
            goodix_hr_summary["boundary"]["source_disposition"] != \
            "vendor_source_required_not_redistributable" or \
            goodix_hr_summary["boundary"][
                "local_algorithm_reimplementation_authorized"
            ] is not False:
        raise AssertionError("Goodix GH_HR processing boundary metadata changed")
    for function in GOODIX_HR_FUNCTIONS:
        entry = int(function["entry"])
        row = ownership_by_key[("application", f"0x{entry:08x}")]
        body = b"".join(
            recovered[start - recovered_base:end - recovered_base]
            for start, end in function["segments"]
        )
        if row["provider_family"] != "goodix_gh3x2x_candidate" or \
                row["source_disposition"] != \
                "vendor_source_required_not_redistributable" or \
                row["confidence"] != "high" or \
                int(row["size"]) != function["size"] or \
                len(body) != function["size"] or \
                hashlib.sha256(body).hexdigest() != function["sha256"]:
            raise AssertionError(
                f"Goodix GH_HR processing boundary changed: 0x{entry:08x}"
            )
    goodix_hrv_summary = summarize_r1_goodix_hrv_boundary(recovered_image_path)
    if goodix_hrv_summary["function_count"] != 9 or \
            goodix_hrv_summary["function_bytes"] != 1288 or \
            goodix_hrv_summary["newly_classified_count"] != 7 or \
            goodix_hrv_summary["newly_classified_bytes"] != 1154 or \
            goodix_hrv_summary["identity"]["component"] != \
            "Goodix GH_HRV_pre" or \
            goodix_hrv_summary["identity"]["component_version"] != \
            "v1.0.1.0" or \
            goodix_hrv_summary["identity"]["component_hash"] != \
            "ed953ff3" or \
            goodix_hrv_summary["identity"]["private_abi_version"] != \
            "pv_v1.1.0" or \
            goodix_hrv_summary["identity"]["initializer"] != \
            "0x0006db5c" or \
            goodix_hrv_summary["boundary"]["provider_family"] != \
            "goodix_gh3x2x_candidate" or \
            goodix_hrv_summary["boundary"]["source_disposition"] != \
            "vendor_source_required_not_redistributable" or \
            goodix_hrv_summary["boundary"][
                "local_algorithm_reimplementation_authorized"
            ] is not False or \
            goodix_hrv_summary["boundary"]["licensed_provider_required"] \
            is not True:
        raise AssertionError("Goodix GH_HRV lifecycle boundary metadata changed")
    for function in GOODIX_HRV_FUNCTIONS:
        entry = int(function["entry"])
        row = ownership_by_key[("application", f"0x{entry:08x}")]
        body = b"".join(
            recovered[start - recovered_base:end - recovered_base]
            for start, end in function["segments"]
        )
        if row["provider_family"] != "goodix_gh3x2x_candidate" or \
                row["source_disposition"] != \
                "vendor_source_required_not_redistributable" or \
                row["confidence"] != "high" or \
                int(row["size"]) != function["size"] or \
                len(body) != function["size"] or \
                hashlib.sha256(body).hexdigest() != function["sha256"]:
            raise AssertionError(
                f"Goodix GH_HRV lifecycle boundary changed: 0x{entry:08x}"
            )
    goodix_channel_summary = summarize_r1_goodix_channel_decoder(
        recovered_image_path
    )
    if goodix_channel_summary["function_count"] != 2 or \
            goodix_channel_summary["function_bytes"] != 856 or \
            goodix_channel_summary["callgraph"]["decoder_sole_callsite"] != \
            "0x0006e874" or \
            goodix_channel_summary["callgraph"]["helper_callsites"] != [
                "0x00061e42", "0x00061e86", "0x00061eca",
            ] or \
            goodix_channel_summary["callgraph"]["helper_outside_caller_count"] != 0 or \
            goodix_channel_summary["callgraph"]["version_qualifier_dependency"] != \
            "0x00066890" or \
            goodix_channel_summary["boundary"]["provider_family"] != \
            "goodix_gh3x2x_candidate" or \
            goodix_channel_summary["boundary"]["source_disposition"] != \
            "vendor_source_required_not_redistributable" or \
            any(goodix_channel_summary["boundary"][key] is not False for key in (
                "private_symbol_or_sdk_version_resolved",
                "local_decoder_or_scaling_reimplementation_authorized",
                "coefficient_tables_or_formula_emitted",
                "toolchain_math_reimplemented",
            )) or \
            goodix_channel_summary["safety"] != {
                "static_parser_only": True,
                "live_sensor_data_read": False,
                "private_coefficients_emitted": False,
            }:
        raise AssertionError("Goodix channel-decoder boundary metadata changed")
    for function in GOODIX_CHANNEL_DECODER_FUNCTIONS:
        entry = int(function["entry"])
        end = int(function["end_exclusive"])
        row = ownership_by_key[("application", f"0x{entry:08x}")]
        body = recovered[entry - recovered_base:end - recovered_base]
        if row["provider_family"] != "goodix_gh3x2x_candidate" or \
                row["source_disposition"] != \
                "vendor_source_required_not_redistributable" or \
                row["confidence"] != "high" or \
                int(row["size"]) != function["size"] or \
                len(body) != function["size"] or \
                hashlib.sha256(body).hexdigest() != function["sha256"]:
            raise AssertionError(
                f"Goodix channel-decoder boundary changed: 0x{entry:08x}"
            )
    goodix_nadt_quality_summary = summarize_r1_goodix_nadt_quality(
        recovered_image_path
    )
    if goodix_nadt_quality_summary["function_count"] != 1 or \
            goodix_nadt_quality_summary["function_bytes"] != 518 or \
            goodix_nadt_quality_summary["callgraph"]["sole_caller_function"] != \
            "0x0006e838" or \
            goodix_nadt_quality_summary["callgraph"]["sole_callsite"] != \
            "0x0006e916" or \
            goodix_nadt_quality_summary["callgraph"]["outside_caller_exclusivity"] is not True or \
            goodix_nadt_quality_summary["boundary"]["provider_family"] != \
            "goodix_gh3x2x_candidate" or \
            goodix_nadt_quality_summary["boundary"]["source_disposition"] != \
            "vendor_source_required_not_redistributable" or \
            any(goodix_nadt_quality_summary["boundary"][key] is not False for key in (
                "private_symbol_or_sdk_version_resolved",
                "local_quality_or_score_reimplementation_authorized",
                "thresholds_or_formula_emitted",
                "toolchain_math_reimplemented",
            )) or \
            goodix_nadt_quality_summary["safety"] != {
                "static_parser_only": True,
                "live_sensor_data_read": False,
                "private_thresholds_emitted": False,
            }:
        raise AssertionError("Goodix NADT quality boundary metadata changed")
    for function in GOODIX_NADT_QUALITY_FUNCTIONS:
        entry = int(function["entry"])
        end = int(function["end_exclusive"])
        row = ownership_by_key[("application", f"0x{entry:08x}")]
        body = recovered[entry - recovered_base:end - recovered_base]
        if row["provider_family"] != "goodix_gh3x2x_candidate" or \
                row["source_disposition"] != \
                "vendor_source_required_not_redistributable" or \
                row["confidence"] != "high" or \
                int(row["size"]) != function["size"] or \
                len(body) != function["size"] or \
                hashlib.sha256(body).hexdigest() != function["sha256"]:
            raise AssertionError(
                f"Goodix NADT quality boundary changed: 0x{entry:08x}"
            )
    goodix_nadt_peak_mask_summary = summarize_r1_goodix_nadt_peak_mask(
        recovered_image_path
    )
    if goodix_nadt_peak_mask_summary["function_count"] != 7 or \
            goodix_nadt_peak_mask_summary["function_bytes"] != 1098 or \
            goodix_nadt_peak_mask_summary["callgraph"]["existing_provider_root"] != \
            "0x0006e838" or \
            goodix_nadt_peak_mask_summary["callgraph"]["root_callsite"] != \
            "0x0006e8e6" or \
            goodix_nadt_peak_mask_summary["callgraph"]["outside_direct_callers"] != 0 or \
            goodix_nadt_peak_mask_summary["boundary"]["provider_family"] != \
            "goodix_gh3x2x_candidate" or \
            goodix_nadt_peak_mask_summary["boundary"]["source_disposition"] != \
            "vendor_source_required_not_redistributable" or \
            any(goodix_nadt_peak_mask_summary["boundary"][key] is not False for key in (
                "private_symbols_or_sdk_version_resolved",
                "local_peak_selection_reimplementation_authorized",
                "private_thresholds_or_formula_emitted",
            )) or \
            goodix_nadt_peak_mask_summary["safety"] != {
                "static_parser_only": True,
                "live_sensor_data_read": False,
                "algorithm_implementation_emitted": False,
            }:
        raise AssertionError("Goodix NADT peak-mask boundary metadata changed")
    for function in GOODIX_NADT_PEAK_MASK_FUNCTIONS:
        entry = int(function["entry"])
        end = int(function["end_exclusive"])
        row = ownership_by_key[("application", f"0x{entry:08x}")]
        body = recovered[entry - recovered_base:end - recovered_base]
        if row["provider_family"] != "goodix_gh3x2x_candidate" or \
                row["source_disposition"] != \
                "vendor_source_required_not_redistributable" or \
                row["confidence"] != "high" or \
                int(row["size"]) != function["size"] or \
                len(body) != function["size"] or \
                hashlib.sha256(body).hexdigest() != function["sha256"]:
            raise AssertionError(
                f"Goodix NADT peak-mask boundary changed: 0x{entry:08x}"
            )
    goodix_nadt_accumulation_summary = summarize_r1_goodix_nadt_accumulation(
        recovered_image_path
    )
    if goodix_nadt_accumulation_summary["function_count"] != 30 or \
            goodix_nadt_accumulation_summary["function_bytes"] != 5126 or \
            goodix_nadt_accumulation_summary["composite_function_count"] != 2 or \
            goodix_nadt_accumulation_summary["callgraph"]["existing_provider_root"] != \
            "0x0006e838" or \
            goodix_nadt_accumulation_summary["callgraph"]["outside_non_goodix_callers"] != 0 or \
            goodix_nadt_accumulation_summary["boundary"]["provider_family"] != \
            "goodix_gh3x2x_candidate" or \
            goodix_nadt_accumulation_summary["boundary"]["source_disposition"] != \
            "vendor_source_required_not_redistributable" or \
            goodix_nadt_accumulation_summary["boundary"][
                "local_algorithm_reimplementation_authorized"
            ] is not False or \
            goodix_nadt_accumulation_summary["boundary"][
                "private_constants_or_formula_emitted"
            ] is not False or \
            goodix_nadt_accumulation_summary["boundary"][
                "toolchain_and_sensor_heap_excluded"
            ] is not True:
        raise AssertionError("Goodix NADT accumulation boundary metadata changed")
    for function in GOODIX_NADT_ACCUMULATION_FUNCTIONS:
        entry = int(function["entry"])
        row = ownership_by_key[("application", f"0x{entry:08x}")]
        segments = function["segments"] or (
            (entry, int(function["end_exclusive"])),
        )
        body = b"".join(
            recovered[start - recovered_base:end - recovered_base]
            for start, end in segments
        )
        if row["provider_family"] != "goodix_gh3x2x_candidate" or \
                row["source_disposition"] != \
                "vendor_source_required_not_redistributable" or \
                row["confidence"] != "high" or \
                int(row["size"]) != function["size"] or \
                len(body) != function["size"] or \
                hashlib.sha256(body).hexdigest() != function["sha256"]:
            raise AssertionError(
                f"Goodix NADT accumulation boundary changed: 0x{entry:08x}"
            )
    goodix_register_profile_summary = summarize_r1_goodix_register_profile(
        recovered_image_path
    )
    if goodix_register_profile_summary["function_count"] != 1 or \
            goodix_register_profile_summary["function_bytes"] != 514 or \
            goodix_register_profile_summary["callgraph"]["sole_caller_thunk"] != \
            "0x0002a810" or \
            goodix_register_profile_summary["callgraph"]["caller_branch_kind"] != "B.W" or \
            goodix_register_profile_summary["callgraph"]["outside_caller_exclusivity"] is not True or \
            goodix_register_profile_summary["boundary"]["provider_family"] != \
            "goodix_gh3x2x_candidate" or \
            goodix_register_profile_summary["boundary"]["source_disposition"] != \
            "vendor_source_required_not_redistributable" or \
            any(goodix_register_profile_summary["boundary"][key] is not False for key in (
                "private_symbol_or_sdk_version_resolved",
                "local_profile_decoder_reimplementation_authorized",
                "private_profile_layout_emitted",
                "live_register_io_exposed",
            )) or \
            goodix_register_profile_summary["safety"] != {
                "static_parser_only": True,
                "live_device_access": False,
                "private_profile_blob_emitted": False,
            }:
        raise AssertionError("Goodix register-profile boundary metadata changed")
    for function in GOODIX_REGISTER_PROFILE_FUNCTIONS:
        entry = int(function["entry"])
        end = int(function["end_exclusive"])
        row = ownership_by_key[("application", f"0x{entry:08x}")]
        body = recovered[entry - recovered_base:end - recovered_base]
        if entry in goodix_democode_symbols:
            family_ok = row["provider_family"] == \
                "goodix_gh3x2x_democode_v1_6_drvlib_v4_3_0_0" and \
                row["source_disposition"] == "use_pinned_upstream"
        else:
            family_ok = row["provider_family"] == "goodix_gh3x2x_candidate" and \
                row["source_disposition"] == \
                "vendor_source_required_not_redistributable"
        if not family_ok or \
                row["confidence"] != "high" or \
                int(row["size"]) != function["size"] or \
                len(body) != function["size"] or \
                hashlib.sha256(body).hexdigest() != function["sha256"]:
            raise AssertionError(
                f"Goodix register-profile boundary changed: 0x{entry:08x}"
            )
    goodix_spo2_dlcom_summary = summarize_r1_goodix_spo2_dlcom_boundary(
        recovered_image_path
    )
    if goodix_spo2_dlcom_summary["function_count"] != 85 or \
            goodix_spo2_dlcom_summary["function_bytes"] != 19568 or \
            goodix_spo2_dlcom_summary["ghidra_function_count"] != 82 or \
            goodix_spo2_dlcom_summary["ghidra_function_bytes"] != 19520 or \
            goodix_spo2_dlcom_summary["manual_supplement_count"] != 3 or \
            goodix_spo2_dlcom_summary["manual_supplement_bytes"] != 48 or \
            goodix_spo2_dlcom_summary["identity"]["component"] != \
            "Goodix GH_SPO2 and dlCom" or \
            goodix_spo2_dlcom_summary["identity"]["root_callsite"] != \
            "0x0002ca24" or \
            goodix_spo2_dlcom_summary["identity"]["processing_root"] != \
            "0x0006c6a8" or \
            goodix_spo2_dlcom_summary["identity"]["input_diagnostic_formatter"] != \
            "0x0006ccc0" or \
            goodix_spo2_dlcom_summary["identity"]["dlcom_hash"] != \
            "c00c91c9" or \
            goodix_spo2_dlcom_summary["identity"]["spo2_hash"] != \
            "277e89de" or \
            goodix_spo2_dlcom_summary["identity"]["network_hash"] != \
            "1f1cf98b" or \
            goodix_spo2_dlcom_summary["identity"]["recurrent_executor"] != \
            "0x000739a8" or \
            goodix_spo2_dlcom_summary["identity"]["recurrent_executor_pointer"] != \
            "0x000739a9" or \
            goodix_spo2_dlcom_summary["closure"]["direct_root_descendants"] != 56 or \
            goodix_spo2_dlcom_summary["closure"][
                "recurrent_runtime_function_count"
            ] != 7 or \
            goodix_spo2_dlcom_summary["closure"]["recurrent_runtime_bytes"] != 2264 or \
            goodix_spo2_dlcom_summary["closure"][
                "dormant_graph_function_count"
            ] != 2 or \
            goodix_spo2_dlcom_summary["closure"]["dormant_graph_bytes"] != 2032 or \
            goodix_spo2_dlcom_summary["closure"]["input_diagnostic_bytes"] != 984 or \
            goodix_spo2_dlcom_summary["closure"][
                "dormant_graph_product_reachability"
            ] is not False or \
            goodix_spo2_dlcom_summary["closure"][
                "outside_caller_exclusivity_claimed"
            ] is not False or \
            goodix_spo2_dlcom_summary["boundary"]["provider_family"] != \
            "goodix_gh3x2x_candidate" or \
            goodix_spo2_dlcom_summary["boundary"]["source_disposition"] != \
            "vendor_source_required_not_redistributable" or \
            goodix_spo2_dlcom_summary["boundary"][
                "local_algorithm_reimplementation_authorized"
            ] is not False or \
            goodix_spo2_dlcom_summary["boundary"][
                "neural_network_reconstruction_authorized"
            ] is not False:
        raise AssertionError("Goodix GH_SPO2/dlCom boundary metadata changed")
    shared_quantized_by_entry = {
        int(function["entry"]): function
        for function in (
            SHARED_QUANTIZED_FRONTIER_230_248_FUNCTIONS
            + SHARED_QUANTIZED_FRONTIER_224_230_FUNCTIONS
            + SHARED_TENSOR_FRONTIER_204_210_FUNCTIONS
        )
    }
    for function in GOODIX_SPO2_DLCOM_ALL_FUNCTIONS:
        entry = int(function["entry"])
        row = ownership_by_key[("application", f"0x{entry:08x}")]
        body = b"".join(
            recovered[start - recovered_base:end - recovered_base]
            for start, end in function["segments"]
        )
        expected_inventory = (
            "manual_provenance_supplement"
            if function["inventory"] == "manual_provenance_supplement"
            else "ghidra_functions_csv"
        )
        shared_function = shared_quantized_by_entry.get(entry)
        expected_provider = (
            shared_function["provider_family"]
            if shared_function is not None else "goodix_gh3x2x_candidate"
        )
        expected_disposition = (
            shared_function["source_disposition"]
            if shared_function is not None
            else "vendor_source_required_not_redistributable"
        )
        expected_symbol = (
            shared_function["symbol"] if shared_function is not None else ""
        )
        if row["provider_family"] != expected_provider or \
                row["source_disposition"] != expected_disposition or \
                row["upstream_symbol"] != expected_symbol or \
                row["confidence"] != "high" or \
                row["inventory_source"] != expected_inventory or \
                int(row["size"]) != function["size"] or \
                len(body) != function["size"] or \
                hashlib.sha256(body).hexdigest() != function["sha256"]:
            raise AssertionError(
                f"Goodix GH_SPO2/dlCom boundary changed: 0x{entry:08x}"
            )
    goodix_hr_init_summary = summarize_r1_goodix_hr_init_boundary(
        recovered_image_path
    )
    if goodix_hr_init_summary["function_count"] != 2 or \
            goodix_hr_init_summary["function_bytes"] != 778 or \
            goodix_hr_init_summary["provider_evidence"][
                "secondary_context_bytes"] != "0x158" or \
            goodix_hr_init_summary["provider_evidence"][
                "secondary_context_initializer"] != "0x00072c48" or \
            goodix_hr_init_summary["boundary"]["provider_family"] != \
                "goodix_gh3x2x_candidate" or \
            goodix_hr_init_summary["boundary"][
                "local_reimplementation_authorized"] is not False:
        raise AssertionError("Goodix GH_HR initializer metadata changed")
    for function in GOODIX_HR_INIT_FUNCTIONS:
        entry = int(function["entry"])
        row = ownership_by_key[("application", f"0x{entry:08x}")]
        body = recovered[entry - recovered_base:
                         int(function["end_exclusive"]) - recovered_base]
        if row["provider_family"] != "goodix_gh3x2x_candidate" or \
                row["source_disposition"] != \
                "vendor_source_required_not_redistributable" or \
                int(row["size"]) != function["size"] or \
                len(body) != function["size"] or \
                hashlib.sha256(body).hexdigest() != function["sha256"]:
            raise AssertionError(
                f"Goodix GH_HR initializer changed: 0x{entry:08x}"
            )

    goodix_candidate_expected = {
        0x0002A0F4: (110, "ea0bd76b6cf6e5b485d103c94e4db183fae4fb8107a4d41b4509f120e52ebcf4"),
        0x0002A380: (166, "6820b8b10bc2283a34c89144aa8530e9667838122c9c90e91744a2497a7ff44b"),
        0x0002A55C: (4, "a9e46410b7de0d289c2610c9917b144a43b2368e1cd7e7aa2682f4b9b18b2cbe"),
        0x0002A598: (4, "a9e46410b7de0d289c2610c9917b144a43b2368e1cd7e7aa2682f4b9b18b2cbe"),
        0x0002A614: (4, "a9e46410b7de0d289c2610c9917b144a43b2368e1cd7e7aa2682f4b9b18b2cbe"),
        0x0002A754: (152, "d093aa52f833ddd398b8ccbd6f3c15cc6fec6151420247b90b85aac3172607c4"),
        0x0002AAD0: (6, "763da1d37075cb08ea6a3a8f85b2010f144ed087bfa7811e69343758f8fa7172"),
        0x0002AADC: (24, "328b09b6ec812d47fe957cad5d66cc96318d33e1a9512372b6545ee6aba05862"),
        0x0002AAF8: (54, "2ab3bdce655c1f92f1cc7931125308e0ef999b5067df1eaa3415484be0df3665"),
        0x0002ABFC: (14, "5b7385536dcb9fb5ab8f6cdc8cf613076351e2b7ae3b94b250fe87766036c66f"),
        0x0002AC1C: (16, "92eb13576114406ad6d719e1c9b7db745c59438f1ee7dadeed76d51c2e6bab7d"),
        0x0002C2EC: (222, "5726230529447a7687b757067b4fcbbf529c89e0c18eba02e0cf21202e0c3aca"),
        0x0002CD00: (132, "9a60dc12ad9660da385df6b063b222c667fad9cbec20d3c62d25253cbfd71d8f"),
        0x0002D670: (238, "601ba05a3d4a9a0c6fda2e84454fc1df71ad9a04f4a2fe8ba5f1420cf6caf145"),
        0x0002D824: (78, "28ef9f59cc5e1a11e8fd72b6f383177f8568afbcd477738883666847b58e1e3c"),
        0x0002D87C: (480, "0620fc04e2e4593429419a66b727323298dca6b8ac0f4228723f2ff7d716d485"),
        0x0002DB8C: (958, "3e7c6ce4f8f63529d411810cdca292e6972d4672a5deedc07b142881012e75e9"),
        0x0002E0D0: (454, "f0001aadcbb8fd537b28f7a0657d74cbe660d8a8dc206b583b80b5db1291fef0"),
        0x0002E358: (144, "30737398ed8575cd4c22e35ec13efdfa2bc3286fb2c2c5f0d19c1c7f5c2c2566"),
        0x0002E36C: (418, "d2397d1bb6c459bcaf3bd4b424fbceda0fe08f744969287a26175836450bd4ff"),
        0x0002E61C: (76, "9a03886809e75a27e3011c15ec21d23e5cd1e1906399aec56241d453583fc546"),
        0x0002E6A8: (42, "c571328e33acca3f393c3d086842d3e2492911b7029aecd093b1f0bd7aeafa62"),
        0x0002E6BC: (60, "0f5457538e3eb5afb7021da6ae28edd87f77e22766b894f33c7190f4413c89a5"),
        0x0002E778: (40, "8eff9ceda14d2f6f0f74744171cbd949e4f8548caf055396631a449eb648b6a3"),
        0x0002E7C4: (174, "53fb63dab233f6b39f2f44481fa58d8412abfe36a018f1be71da34d49d94577c"),
        0x0002E964: (374, "2a7522a548535b7e4c33d411b623dbd53fc31c9aba9d0b6946247b1f1c7f9ee4"),
        0x0002EB84: (444, "a3305daed0dc6e1ec32753789c121321f26b29814538275363eccd1e639b8bd6"),
        0x0002EDEC: (10, "c0b12904f12393e8b340a57281d7a0b6df4ff224a4a53438b4dfd0009c1ebffa"),
        0x0002EE28: (10, "8460c248bfdc27cd79eb8fed39bdfe9483254e8b1b7bee50e67edc1a16536c07"),
        0x0002EE50: (36, "ec688a587e4c8bb96dafb8f47ad7012f0c36b4e61420ad18cebfec931e8e4914"),
        0x0002EF6C: (210, "3cc38c8583cbc96c69f671604b6fa13bbc12b8773afb6bddfa2b3ce252299eaa"),
        0x0002F0F8: (10, "48acdc9748ddb642dab52d3f8f4251c33b0d60d1d775a20f0de837889c1ecedc"),
        0x00032788: (88, "86e4f0eae2a98e57cb659ca77a7144625a5864d7ae8ab48be71d99e5b4f9776b"),
        0x0005A5EC: (54, "f6556685cb2ed54dc42e8ff378ad47ff2fcc02ae4948b261bf5bb58ca4a78572"),
        0x00066840: (46, "705634343c2ab8fd87db97ee19a5780776b9b10d518453ef5ee99a60f15f4009"),
        0x00066890: (14, "90adccd38d123287636ef7637883eb8c9ccc271671ff979c131fde1b83b068bb"),
        0x0006A020: (8, "63129284b0ff79970010791bce08ca6610b4a5088c1e3096f86d5bdd1379d769"),
        0x0006A4D8: (376, "4031265491ab63c8833cd822ba96d8ce9198d5fe1be7b7b5753e54c5e3216b64"),
        0x0006A500: (110, "3aa2c9b56e1da81c5b7bbed0f325f5145eddd548e8c582b3ddfb8f67c5c5c1ee"),
        0x0006D204: (406, "65fe2de6a621441725d19f187806681c1fe9f1652fafb68f1d9b2bcb4a6aa001"),
        0x00072C48: (372, "045e1b10cfe230f567b3c6dc47365ede835ce38e07b7dcb388f9f026683b03d6"),
        0x0006D3C0: (96, "598666dfe6527115c8def19747898ff600ad31c9dd52ea8aa871b68306f13243"),
        0x0006D424: (180, "fff0823379759ec33727d7ade7c3c76b231195d284e6271cfa2d30417cdc027c"),
        0x0006D51C: (1382, "0f1b8fa8d247ca839a59cfffccb4f70e9cb1a689cd2f736c8514474c02358c9d"),
        0x0006DF14: (76, "b092cfc73f83ad7a4a6d152564c6b555d02614decd7d9097a0f48203e2b54e3b"),
        0x0006DF60: (58, "3f1a1e8b1dbb1338e45fd0df817491c0ffd54189e53828ed3ba313aa3a64a6b0"),
        0x0006E788: (126, "bf627bb8587f69473d9f39846a0e9979201e91e9d17cc6513ebba85a8e079c04"),
        0x0006EC28: (100, "e58547373b653c410d04957ab3d52b7352e85d7e9ceed2ce05ae088c645be1ef"),
        0x0006EC90: (182, "02bf9cb6f8334524f02c3a57f21db491395924e3e7c5f7d6523184e4074b06be"),
        0x000759F4: (20, "144db00be4dbeff89e673850917c4d4bcbbac8ba2740e7ea056d14a8da04cb80"),
    }
    goodix_democode_entries = {
        0x00029C98, 0x00029CC0, 0x00029CDC, 0x00029D0A,
        0x00029D34, 0x00029D58, 0x00029D5C, 0x00029E8C,
        0x00029F88, 0x00029F9C, 0x0002A090, 0x0002A0F4,
        0x0002A198, 0x0002A1F8, 0x0002A204, 0x0002A214,
        0x0002A266, 0x0002A2AC, 0x0002A31C, 0x0002A328,
        0x0002A380, 0x0002A474, 0x0002A488, 0x0002A4B4,
        0x0002A508, 0x0002A540, 0x0002A550, 0x0002A55C,
        0x0002A598, 0x0002A5C4, 0x0002A5D0, 0x0002A5EC,
        0x0002A604, 0x0002A614, 0x0002A630, 0x0002A658,
        0x0002A65A, 0x0002A754, 0x0002A7F4, 0x0002A810,
        0x0002A814, 0x0002A84C, 0x0002A86C, 0x0002A8DC,
        0x0002A968, 0x0002A99E, 0x0002A9D4, 0x0002A9EC,
        0x0002AA10, 0x0002AA74, 0x0002AA98, 0x0002AAD0,
        0x0002AADC, 0x0002AAF8, 0x0002ABA4, 0x0002ABDC,
        0x0002ABEC, 0x0002ABFC, 0x0002AC10, 0x0002AC1C,
        0x0002AC30, 0x0002AC40, 0x0002AC4C, 0x0002AC8C,
        0x0002ACCC, 0x0002ACF4, 0x0002AD14, 0x0002AD18,
        0x0002AD7C, 0x0002ADB0, 0x0002AE00, 0x0002AE04,
        0x0002AE06, 0x0002AE08, 0x0002AE28, 0x0002AEDC,
        0x0002AF32, 0x0002AF84, 0x0002B010, 0x0002B0B8,
        0x0002B0DC, 0x0002B148, 0x0002B180, 0x0002B218,
        0x0002B4C4, 0x0002B4D8, 0x0002B4F8, 0x0002B524,
        0x0002B6A4, 0x0002B6E0, 0x0002B8EC, 0x0002B91C,
        0x0002B998, 0x0002BD84, 0x0002BE24, 0x0002BFAA,
        0x0002C148, 0x0002C178, 0x0002C248, 0x0002C27C,
        0x0002C2A4, 0x0002C2EC, 0x0002C43C, 0x0002C4C0,
        0x0002C4E4, 0x0002C4FC, 0x0002C640, 0x0002C694,
        0x0002C930, 0x0002C944, 0x0002CAA4, 0x0002CAD8,
        0x0002CC94, 0x0002CCC0, 0x0002CCD0, 0x0002CCF4,
        0x0002CD00, 0x0002CDD4, 0x0002CFE8, 0x0002D16C,
        0x0002D184, 0x0002D324, 0x0002D33C, 0x0002D348,
        0x0002D354, 0x0002D3A8, 0x0002D658, 0x0002D670,
        0x0002D824, 0x0002D87C, 0x0002DB8C, 0x0002E0D0,
        0x0002E340, 0x0002E358, 0x0002E36C, 0x0002E61C,
        0x0002E6A8, 0x0002E6BC, 0x0002E746, 0x0002E778,
        0x0002E7A4, 0x0002E7C4, 0x0002E8C4, 0x0002E8C8,
        0x0002E8E8, 0x0002E964, 0x0002EB0C, 0x0002EB4E,
        0x0002EB84, 0x0002ED98, 0x0002EDAA, 0x0002EDEC,
        0x0002EDFC, 0x0002EE28, 0x0002EE38, 0x0002EE44,
        0x0002EE50, 0x0002EF6C, 0x0002F0F8, 0x0006A018,
        0x0006A020, 0x0006A130, 0x0006A148, 0x0006A500,
        0x0006CC34, 0x0006EAF8, 0x0006EB00, 0x0006EC28,
    }
    for entry, (size, digest) in goodix_candidate_expected.items():
        row = ownership_by_key[("application", f"0x{entry:08x}")]
        body = recovered_function(entry)
        goodix_adapter_glue_entries = {
        0x0002E734, 0x0003DDF4, 0x0006A4D8, 0x0006F920, 0x0006F964, 0x0006F9D4,
    }
        if entry in goodix_democode_entries:
            family_ok = row["provider_family"] == \
                "goodix_gh3x2x_democode_v1_6_drvlib_v4_3_0_0" and \
                row["source_disposition"] == "use_pinned_upstream"
        elif entry in goodix_adapter_glue_entries:
            family_ok = row["provider_family"] == \
                "r1_goodix_provider_adapter"
        else:
            family_ok = row["provider_family"] == "goodix_gh3x2x_candidate" and \
                row["source_disposition"] == \
                "vendor_source_required_not_redistributable"
        if not family_ok or \
                len(body) != size or hashlib.sha256(body).hexdigest() != digest:
            raise AssertionError(f"Goodix GH3X2X boundary changed: 0x{entry:08x}")
    # The 116-entry frozen direct-call-graph closure, pinned explicitly by
    # entry: 64 members are now attributed to the pinned public Goodix
    # democode, so the evidence-phrase filter can no longer see them.
    goodix_cluster_entries = {
        0x00029f9c, 0x0002a090, 0x0002a168, 0x0002a198,
        0x0002a1cc, 0x0002a1f8, 0x0002a204, 0x0002a214,
        0x0002a266, 0x0002a2ac, 0x0002a31c, 0x0002a328,
        0x0002a488, 0x0002a4b4, 0x0002a508, 0x0002a540,
        0x0002a550, 0x0002a5c4, 0x0002a5d0, 0x0002a5ec,
        0x0002a604, 0x0002a658, 0x0002a65a, 0x0002a7f4,
        0x0002a810, 0x0002a814, 0x0002a84c, 0x0002a86c,
        0x0002a8dc, 0x0002a968, 0x0002a99e, 0x0002a9d2,
        0x0002a9d4, 0x0002a9ec, 0x0002aa10, 0x0002aa74,
        0x0002aa98, 0x0002aba4, 0x0002abdc, 0x0002ac10,
        0x0002ac30, 0x0002ac40, 0x0002ac4c, 0x0002ac8c,
        0x0002accc, 0x0002ad14, 0x0002ad18, 0x0002ad7c,
        0x0002adb0, 0x0002ae04, 0x0002ae06, 0x0002ae08,
        0x0002ae28, 0x0002af84, 0x0002b010, 0x0002b0b8,
        0x0002b0dc, 0x0002b148, 0x0002b180, 0x0002b218,
        0x0002b4c4, 0x0002b4d8, 0x0002b4f8, 0x0002b524,
        0x0002b6a4, 0x0002b8ec, 0x0002b91c, 0x0002b998,
        0x0002bd84, 0x0002be24, 0x0002bfaa, 0x0002c148,
        0x0002c178, 0x0002c248, 0x0002c27c, 0x0002c2a4,
        0x0002c43c, 0x0002c4c0, 0x0002c4e4, 0x0002c4fc,
        0x0002c640, 0x0002c694, 0x0002c930, 0x0002c944,
        0x0002caa4, 0x0002cad8, 0x0002cc94, 0x0002ccc0,
        0x0002ccd0, 0x0002ccf4, 0x0002cdd4, 0x0002cfe8,
        0x0002d184, 0x0002d324, 0x0002d33c, 0x0002d348,
        0x0002d354, 0x0002d3a8, 0x0002d658, 0x0002d66c,
        0x0002e340, 0x0002e734, 0x0002e746, 0x0002e7a4,
        0x0002e8cc, 0x0002e8e8, 0x0002e950, 0x0002eb0c,
        0x0002eb4e, 0x0002eb80, 0x0002ed98, 0x0002edaa,
        0x0002ede0, 0x0002edfc, 0x0002ee38, 0x0002ee44,
    }
    goodix_cluster_rows = [
        row for row in ownership_rows
        if row["image"] == "application" and
        int(row["entry"], 16) in goodix_cluster_entries
    ]
    if len(goodix_cluster_rows) != 116:
        raise AssertionError("Goodix direct-call-graph closure changed")
    goodix_cluster_entry_digest = hashlib.sha256("".join(
        f"{row['entry']}\n" for row in goodix_cluster_rows
    ).encode()).hexdigest()
    if goodix_cluster_entry_digest != \
            "4decf6432c5a96fd2594f87f497c087c625988aa6e093fbbefcf5b04e0367cb9":
        raise AssertionError("Goodix cluster entry set changed")
    goodix_cluster_body_digest = hashlib.sha256("".join(
        f"{int(row['entry'], 16):08x}:{row['size']}:"
        f"{hashlib.sha256(recovered_function(int(row['entry'], 16))).hexdigest()}\n"
        for row in goodix_cluster_rows
    ).encode()).hexdigest()
    if goodix_cluster_body_digest != \
            "75c4f2bbe38b623a1d8c31642c450ea49e118016fadfda9bf0029f11eb596d2d":
        raise AssertionError("Goodix cluster byte aggregate changed")
    goodix_adapter_expected = {
        0x0005036C: (52, "19c0f82c427eac9f45ddc735809415c3f70582d288b726079a36e6c26defedc5"),
        0x00050372: (52, "3aa4cee1d4cad280277b5fab2059993db4b8479f566faa77d793434107955bc9"),
        0x00050870: (34, "f9623e7584a704a107341f881779f5924255b74cfbf8dd7dd21ec8e0097b0933"),
        0x00050892: (36, "bd033a4c11c42362e804586b316b74408c925e89964792dea6413fe11443e2a1"),
        0x000508B6: (36, "df3aca2b33e58c9577b7c4c7c60da8804ce2ccccbb72ba69ffe76a4ec50de9b3"),
        0x000508DA: (42, "dc8730cdcc42c8a5cc92e3d60544d2f15b0ca531d84b173cb3d2d65e9a7ccea1"),
        0x00050904: (62, "292ad52ccd6c0fad12127d5f221da2b81e9b7685bc280656fc87803bea94354e"),
        0x000509A4: (8, "170a67a2e0003906fc32d8f9f616f3cc58a9e53486753ab99f9030d7003a0d69"),
        0x000509B0: (8, "4c68a6dd82088b3ca5a63af340d183fe57e11281da0a484da7f94fd60225ba23"),
        0x000509E0: (140, "76d7291689c6c0a42f9b2acdfc0ae1be81eee382b76fd13f7de496978f6685a5"),
        0x00050AB0: (8, "fbd96146c5819a4542dc776d9966b62bf73c42c4b5064274bb19a4e7298c5476"),
        0x00050AE0: (12, "a86c74e3652c189682122da0fc5208b1986565b4fc6845d1ac06dd7c98ed55e2"),
        0x00050AF0: (12, "10be51fa9e2fb3388850bbdddfa1803b0b4eda21a77aa3e7a85e69dcdf60409e"),
        0x00050BE0: (154, "2cfe2214a45be03f503a7a5036cd8ee9de226e6acacf35feeaae4aa95486d51e"),
        0x0006249C: (44, "2d6ff473a0a0a5d3e7b9378e1e649a772d3b6a65d6131c31288131426955c613"),
        0x000624C8: (44, "de6acb1bfe3db9f29ecd05d9187633417a7d23b425caf64237cd2db4d728195b"),
    }
    for entry, (size, digest) in goodix_adapter_expected.items():
        row = ownership_by_key[("application", f"0x{entry:08x}")]
        body = recovered_function(entry)
        if row["provider_family"] != "r1_goodix_provider_adapter" or \
                row["source_disposition"] != \
                "clean_room_adapter_only_use_licensed_provider" or \
                len(body) != size or hashlib.sha256(body).hexdigest() != digest:
            raise AssertionError(f"R1 Goodix adapter changed: 0x{entry:08x}")
    st25_provider_expected = {
        0x00031B32: ("ST25DVxxKC_GetGPO1_ALL", 20, "17494acea6ec5faab251068f1301decfbd8c03369a5149ab057e87b2c3dbbd86"),
        0x00031B46: ("ST25DVxxKC_GetGPO2_ALL", 28, "8c2c82131c86a777f576f00c4f5612713d4749f617b7cc868189134b1abd919d"),
        0x00031B62: ("ST25DVxxKC_GetGPOStatus", 52, "ebd74e53498d1b2382c32642b4004049117c8f03053f70109b8afbbb49d65519"),
        0x00031B96: ("ST25DVxxKC_GetI2C_SSO_DYN_I2CSSO", 30, "a58a47d5abda44457598db3fc574bdade4307ab574969ea4fa61d6640a35751c"),
        0x00031BF4: ("ST25DVxxKC_GetMB_CTRL_DYN_ALL", 22, "0db7cb36335b0893211dd2548faf0902419b3ffa493aa6b08b421c0b44c56d3d"),
        0x00031C0A: ("ST25DVxxKC_GetFTM_MBMODE", 28, "30a7a638bb48a6b103765f91d6cba1e8177d5d33ea827a335c9f434c5b0e1a2f"),
        0x00031C26: ("ST25DVxxKC_Init", 42, "8e35360e141725fe0b3f8c307d3c319aff6b4253451bfbee3bd488eebd9b966e"),
        0x00031CA4: ("ST25DVxxKC_IsDeviceReady", 18, "8ade5ad4e1cd67b4c9c6852a199382869536bfec0edfbb953d48a4aaae0010b9"),
        0x00031CB6: ("ST25DVxxKC_ReadI2CSecuritySession_Dyn", 28, "a388f8857079b62b4049811491f79305904404bb00288e0b7fea9174a14a6c07"),
        0x00031CD2: ("ST25DVxxKC_ReadID", 26, "842c5de6e9651811b23be403f8a344cf72d1722d476e9ad3b6798a87e072e85c"),
        0x00031D36: ("ST25DVxxKC_ReadMBMode", 28, "00aeec5aaebc2839119efff5e3cc6fe0ffc62572c07f67c2f688b162935b87c3"),
        0x00031D78: ("ST25DVxxKC_ReadReg", 14, "42313322cbe3a025e50da4c7de6bf12ceaa3275e1de377e6405a5b2fcc2b765b"),
        0x00031D88: ("ST25DVxxKC_RegisterBusIO", 54, "c8bf5525d4b5cfa7d2496b0fbf5d1bb78c3a8c6e04c52df20a27bbe699a62555"),
        0x00031DC8: ("ST25DVxxKC_ResetEHENMode_Dyn", 18, "e1e0dcb3ba7d1a1545836a4ebf99f09f1ebeaa130237ff5c63b7e1219b097d32"),
        0x00031DDA: ("ST25DVxxKC_SetEH_CTRL_DYN_EH_EN", 52, "f9a952a72acdd5164009e48e2a2267b34e04068c730523fb0c9adaa9f9b45bb8"),
        0x00031E0E: ("ST25DVxxKC_SetGPO1_ALL", 20, "75dc5825d5429d2ab5260df34064b18e6c1a4a7d6678dccc02c0471ae7b779ba"),
        0x00031E22: ("ST25DVxxKC_SetGPO2_ALL", 48, "99eb358e6e982669c0af1e0a3299f6687db83c24b51ae6ec17dfe5d9ba430669"),
        0x00031E64: ("ST25DVxxKC_SetMB_CTRL_DYN_MBEN", 52, "42e1d5122af792fa74ac56b4e00d8517b2b39904ce3b3d3e0f36cb82dbc3ace4"),
        0x00031E98: ("ST25DVxxKC_WriteData", 114, "424c98547ccd08ce1d38c0df7a7f77a7199922f5622f1fb4266f8e8d48718596"),
        0x00031F2C: ("ST25DVxxKC_WriteReg", 14, "4686f17e2fd829e074144cf8f5dba05d1373a8b421b62c3857b1d26733e8dc63"),
        0x00031F3A: ("ST25DVxxKC_WriteRegister", 114, "9a324c0629aed0471d9831eea3ca3c214e760bef46093cfa6a45990dc5e5ab6c"),
        0x00077CE4: ("ST25DVxxKC_ReadITSTStatus_Dyn", 34, "461e439bc95c0885a60ea63dbbba67966d54994e1a5b7626069b5126e63a497b"),
        0x00077CF0: ("ST25DVxxKC_ReadMailboxData", 44, "06695f318196283e37e00af963fa132eadd316699816494727ca6075e89f82e8"),
        0x00077CFC: ("ST25DVxxKC_ReadMBCtrl_Dyn", 88, "8e24585728c01ddc578093f2d32008d974a0f250afb145f2e89b01cb3a04aff6"),
        0x00077D08: ("ST25DVxxKC_ReadMBLength_Dyn", 34, "7d2a5b02d17eb32cbeb80f23d3908589e4eb0da01b2d9fc47804823ea58032a8"),
        0x00077D14: ("ST25DVxxKC_SetMBEN_Dyn", 24, "982be46d076258d323a7d8466945aac08a208927762cf83b556b942c756fac1a"),
        0x00077D20: ("ST25DVxxKC_WriteMailboxData", 40, "56af8a4d668d7c64e3042a540d2f0ddfcce59722da0bb8c110a9af131bb79595"),
    }
    for entry, (symbol, size, digest) in st25_provider_expected.items():
        row = ownership_by_key[("application", f"0x{entry:08x}")]
        body = recovered_function(entry)
        if row["provider_family"] != "stmicro_st25dvxxkc_bsd_compatible" or \
                row["source_disposition"] != \
                "use_authenticated_upstream_snapshot" or \
                row["upstream_symbol"] != symbol or len(body) != size or \
                hashlib.sha256(body).hexdigest() != digest:
            raise AssertionError(f"ST25DVxxKC provider body changed: 0x{entry:08x}")
    st25_adapter_expected = {
        0x00044BEC: ("r1_st25dvxxkc_bus_registration", 72, "0e60bffb20b67f4b0411d0537529f39206b6686633214fd7873c4a9d6ec30455"),
        0x00044C90: ("r1_st25dvxxkc_password_present", 84, "a0944f76f5367421800deec4fdbe9640ba9ad03e517e55ca02f22b832d5ce2e1"),
        0x00044C9C: ("r1_st25dvxxkc_security_session", 64, "2ed77b5d3f910dccb19835cddf96d1fa2d65836b9ee9a446ff95c034e2664c75"),
        0x00044CE8: ("r1_st25dvxxkc_gpo_configuration", 230, "bbd0ac4278321eaf957967a966d6e130bb185ad949416f2ca976f33dbde17f5f"),
        0x000772A8: ("r1_st25dvxxkc_dock_advertisement_send", 142, "831d81b9484b6ed2e7551144aa1a831fb9cea0bec4afe5535e0cc7e1cd74ffa3"),
        0x00077430: ("r1_st25dvxxkc_dock_frame_policy", 466, "ae5760b9a6ac03ac46642f7e19b90b11b0e630c406e443902ce1cb31c99a30e1"),
        0x00077764: ("r1_st25dvxxkc_initialize_configuration", 590, "1158c4ef104e18bc79eee7e54f5d8bbb932211406077bfaa73a9eacbe74df002"),
        0x00077BE0: ("r1_st25dvxxkc_bounded_mailbox_receive", 108, "20db196236f5a4ee155ddc8cf6e36b7605b47f1970c745997c91ef1f7276b4d9"),
        0x00077C50: ("r1_st25dvxxkc_identity_log_adapter", 90, "e230c4f529d79cc3c27018199eac0360b3db661bfa83303e38e851034fe71e90"),
        0x00096A48: ("r1_st25dvxxkc_field_seen_get", 6, "8292370a09b6beb685b201c7106057995b3213e3f1681af6649f9a5c52de0d2d"),
        0x00096A54: ("r1_st25dvxxkc_field_seen_set", 6, "0594a3e6604c4c62a70819ee5094ceab26fb2eb8fbb5280fd4b92fff602100ce"),
    }
    for entry, (symbol, size, digest) in st25_adapter_expected.items():
        row = ownership_by_key[("application", f"0x{entry:08x}")]
        body = recovered_function(entry)
        if row["provider_family"] != "r1_st25dvxxkc_provider_adapter" or \
                row["source_disposition"] != \
                "clean_room_adapter_only_use_pinned_provider" or \
                row["upstream_symbol"] != symbol or len(body) != size or \
                hashlib.sha256(body).hexdigest() != digest:
            raise AssertionError(f"R1 ST25DVxxKC adapter changed: 0x{entry:08x}")
    i2c5_resource_expected = {
        0x00050464: ("r1_i2c5_nfc_resource_registration", 66, "15fcba3427ed758f3e6040449531392b360c046d2b8f27f23f7c7ebc6dd06509"),
        0x000504C0: ("r1_i2c5_nfc_resource_release", 20, "2a985eaced1ffba181347e060a1aa38cd3167807051d6ca7082ee42a28bfe318"),
        0x000504D8: ("r1_i2c5_nfc_resource_acquire", 52, "672d16c18e2add902d1916583a3b6e4cc974ef445782a7046fa0bd10e4605a27"),
        0x00050758: ("r1_shared_power_client_release", 48, "4b22fb4a06a2d023856499add6354c49714db435df0e5244ad0d097d5ceb8582"),
        0x00050778: ("r1_shared_power_client_acquire", 32, "dc1383f7285121c71e7525dcd20e3e4f272bc069eef3aeedabbe47a82cb03dc6"),
    }
    for entry, (symbol, size, digest) in i2c5_resource_expected.items():
        row = ownership_by_key[("application", f"0x{entry:08x}")]
        body = recovered_function(entry)
        if row["provider_family"] != "r1_i2c5_resource_adapter" or \
                row["source_disposition"] != \
                "clean_room_adapter_only_vendor_io_abstract" or \
                row["upstream_symbol"] != symbol or len(body) != size or \
                hashlib.sha256(body).hexdigest() != digest:
            raise AssertionError(f"R1 i2c_5 resource adapter changed: 0x{entry:08x}")
    for entry in (
        "0x000543c4", "0x00054408", "0x00054440", "0x0005447e",
        "0x00054534", "0x000545ca", "0x00054640", "0x0005468e",
        "0x000546d0", "0x0005475a", "0x00070fda", "0x0007b61c",
        "0x00087bbc", "0x00087e58", "0x0008edd8", "0x00096820",
        "0x0009756a", "0x000976b8",
    ):
        row = ownership_by_key[("application", entry)]
        if row["provider_family"] != "bosch_bma456_sensorapi_2_29_0" or \
                row["source_disposition"] != "use_pinned_upstream":
            raise AssertionError(f"Bosch provider function not routed: {entry}")
    for entry in (
        "0x00053aa4", "0x00053ab4", "0x00053ad0", "0x00053aec",
        "0x00053b2c", "0x00053c6c", "0x000541a8", "0x000544c8",
    ):
        row = ownership_by_key[("application", entry)]
        if row["provider_family"] != "r1_bosch_bma456_provider_adapter" or \
                row["source_disposition"] != \
                "clean_room_adapter_only_use_pinned_provider":
            raise AssertionError(f"Bosch adapter not bounded: {entry}")
    bma_port_exact_expected = {
        0x00053AA4: (12, "365d45f07ec7fae67922708c6a9ba072af22db02bb8419756150378123dcbf7d"),
        0x00053AB4: (28, "c435045bc637a872664f1a26b3e320916bffa296c24882157d7d7b69ff410b27"),
        0x00053AD0: (28, "38c0475f8d369413e75488c7da252c6d5294da5c0fe7d9b0b79cc975f24642a2"),
        0x00053AEC: (48, "fb8995e127c925da3b22fd0bbe9dbec23dad1095c31ee384a4b860f8d83a1f6c"),
    }
    for entry, (size, digest) in bma_port_exact_expected.items():
        body = recovered_function(entry)
        if len(body) != size or hashlib.sha256(body).hexdigest() != digest:
            raise AssertionError(f"Bosch R1 port body changed: 0x{entry:08x}")
    for entry in (
        "0x000750b8", "0x00075120", "0x0007517c", "0x000753ac",
        "0x000753c6", "0x000753f4", "0x00075422", "0x00075450",
        "0x000754ac", "0x000756cc", "0x000756da", "0x0007575a",
        "0x000757c4", "0x000757d2", "0x000757ec", "0x0007581a",
        "0x00075848", "0x00075876", "0x000758a4", "0x000758d2",
        "0x00075900", "0x0007592e", "0x0007595c", "0x0007598a",
        "0x000759b8", "0x000759e6",
    ):
        row = ownership_by_key[("application", entry)]
        if row["provider_family"] != \
                "stmicro_lis2dw12_pid_v2_1_0_compatible" or \
                row["source_disposition"] != "use_pinned_upstream":
            raise AssertionError(f"ST provider function not routed: {entry}")
    for entry in (
        "0x000750a0", "0x000750e8", "0x0007518a", "0x000751b8",
        "0x000754dc", "0x00075510",
    ):
        row = ownership_by_key[("application", entry)]
        if row["provider_family"] != "r1_st_lis2dw12_provider_adapter" or \
                row["source_disposition"] != \
                "clean_room_adapter_only_use_pinned_provider":
            raise AssertionError(f"ST adapter not bounded: {entry}")
    motion_adapter_expected = {
        0x00050128: ("r1_motion_interrupt_input_lookup", 24,
                     "7b1a5eeea76a528200c41629fc3b7518425da436a597a00216fe6fe9d76c9150"),
        0x00050150: ("r1_motion_bus_lookup", 20,
                     "9d9fdf5964a67dc0970f113e437f6af37fd95a0c6b373274f98905685ffb118e"),
        0x00050170: ("r1_motion_bus_release", 8,
                     "adc667c67c1bfc87b3ab58d27b281aa0b1d498fc8ee85cbc0cbc3064a86d0c20"),
        0x0005017C: ("r1_motion_bus_acquire", 8,
                     "0364d7415ac6f696d990f30b3d4eb60807faecef5753b82388f048772ddcf3aa"),
        0x00050188: ("r1_motion_bus_read_request", 60,
                     "de85eec528d613db766f5635e21aa932d5b41ba6c77d755ec1ff317e6141c4d7"),
        0x000501C8: ("r1_motion_bus_write_request", 60,
                     "74c934a6df049e1f7d6cba08106e74f5465ab742da85e29805b00edea50dadf6"),
        0x00050208: ("r1_motion_probe_and_select_provider", 74,
                     "b600f05c8d5202c4ff967e1410917e3db0bf676d7db2baa2e12420bb5c292421"),
        0x0005025C: ("r1_motion_refresh_selection", 16,
                     "b7353e4f9d5e586170912919e7bec46dca93d6a0bfd3129ea495c4f6a1629887"),
        0x00050270: ("r1_motion_selected_provider_initialize", 30,
                     "a0196d1ebe9f88bed57fbbcf05e6742bb4de088e27b043cecf59c11c8c974fa7"),
        0x00050294: ("r1_motion_selected_interrupt_dispatch", 18,
                     "328fcb6a767dcefd8243ca1298bc450ebac5db58bf9442fcf77f92a3d72961d1"),
        0x000502AC: ("r1_motion_selected_fifo_read", 20,
                     "db293b28ed4764d75755f301ea522c9f98452dd80c49f7958e9a0b15fdeb0c21"),
        0x0006F1A8: ("r1_bma456w_probe_wrapper", 20,
                     "069c87b4d47ac5359df00258426f00d17d9f136c59a9b23d24b3bef798e56f0b"),
        0x0006F1BC: ("r1_bma456w_configuration_wrapper", 30,
                     "7d00306fbc52f0bb6473517faea8da0af4c93ec28b8010d87717a25d77f3ea63"),
        0x0006F1DA: ("r1_bma456w_interrupt_noop", 2,
                     "c7dfbb7d02759eacb64dbc916c1bb6f21eabaff1c1032ea5c9176abf7fd28df8"),
        0x0006F1DC: ("r1_bma456w_fifo_normalize", 76,
                     "a9fd5d0455b96438e3c43c1fcb5bd4e8aa80ebda273ccbd70856fce3fbbcb6f0"),
        0x0006F228: ("r1_motion_orientation_accumulator", 204,
                     "4d9c9cd23ca6d583f79505470695867a94c640bcab5b25a2b7737482c914cd62"),
        0x0006F304: ("r1_motion_sample_event_adapter", 118,
                     "38fb7afeaf3eecc8716c9064b21a9a7a45620c553406039503f666e4f03c94cd"),
        0x0006F380: ("r1_lis2dw12_probe_wrapper", 20,
                     "f28f0141116633f35924a7c6659aa0bb2f46dd7fea41f570ba829d84845e7b4e"),
        0x0006F394: ("r1_lis2dw12_configuration_wrapper", 30,
                     "0c8edf12a19ec46b0f54283e89eaffb0df83e594aebddaaa60ba788666d8ca9d"),
        0x0006F3B2: ("r1_lis2dw12_interrupt_noop", 2,
                     "c7dfbb7d02759eacb64dbc916c1bb6f21eabaff1c1032ea5c9176abf7fd28df8"),
        0x0006F3B4: ("r1_lis2dw12_fifo_normalize", 76,
                     "8b1b12bc96b06a763af70923231996f4b094e0618eed09986de02cf8d193c9de"),
        0x0006F400: ("r1_motion_initialize_entry", 4,
                     "725c6758590b54cfadcd4a159e37e23094cf213f42a5bfafc37acce2034afc05"),
        0x0006F4A0: ("r1_motion_thirty_sample_batch_producer", 154,
                     "0d76880e4a9b6311042cc345ea11ffab5164c33c203a4b7ef6ec95e7e5389c26"),
    }
    for entry, (symbol, size, digest) in motion_adapter_expected.items():
        row = ownership_by_key[("application", f"0x{entry:08x}")]
        body = recovered_function(entry)
        if row["provider_family"] != "r1_motion_provider_adapter" or \
                row["source_disposition"] != \
                "clean_room_adapter_only_use_licensed_providers" or \
                row["upstream_symbol"] != symbol or len(body) != size or \
                hashlib.sha256(body).hexdigest() != digest:
            raise AssertionError(f"R1 motion adapter changed: 0x{entry:08x}")
    qma_provider_expected = {
        "0x00086e34": "qma6100_chip_id",
        "0x00087188": "qma6100_set_range",
        "0x000871c4": "qma6100_soft_reset",
    }
    for entry, symbol in qma_provider_expected.items():
        row = ownership_by_key[("application", entry)]
        if row["provider_family"] != \
                "qst_qma6100_v1_0_lineage_unlicensed" or \
                row["source_disposition"] != \
                "vendor_source_required_not_redistributable" or \
                row["upstream_symbol"] != symbol:
            raise AssertionError(f"QST QMA6100 provider body not gated: {entry}")
    qma_adapter_expected = {
        "0x0006f404": "r1_qma6100_probe_wrapper",
        "0x0006f418": "r1_qma6100_configuration_wrapper",
        "0x0006f436": "r1_qma6100_interrupt_wrapper",
        "0x0006f448": "r1_qma6100_fifo_normalize",
        "0x00086d40": "r1_qma6100_anymotion_configuration",
        "0x00086e48": "r1_qma6100_delay_port",
        "0x00086e68": "r1_qma6100_identity_and_layout_adapter",
        "0x00086ee4": "r1_qma6100_initialize_configuration",
        "0x00086fa8": "r1_qma6100_irq_event_adapter",
        "0x00086ff4": "r1_qma6100_bounded_fifo_read",
        "0x0008714c": "r1_qma6100_read_transport",
        "0x00087250": "r1_qma6100_step_configuration",
        "0x000872e4": "r1_qma6100_tap_configuration",
        "0x000873f4": "r1_qma6100_write_transport",
    }
    for entry, symbol in qma_adapter_expected.items():
        row = ownership_by_key[("application", entry)]
        if row["provider_family"] != "r1_qst_qma6100_provider_adapter" or \
                row["source_disposition"] != \
                "clean_room_adapter_only_use_licensed_provider" or \
                row["upstream_symbol"] != symbol:
            raise AssertionError(f"QST QMA6100 adapter not bounded: {entry}")
    qma_wrapper_exact_expected = {
        0x0006F404: (20, "a569ba70d7ed024938ee16539bf0a7182af65ee069a91bf455a3a2e443b0a1ff"),
        0x0006F418: (30, "bf5cdade8e56223363c4429f1dce08d62170ad08a89094c3f9805a10a6ddc7b5"),
        0x0006F436: (18, "443a2fac2784fd3089a8fbbc773d19872dce3ffb6e584a1ae30ef17a0b0f4ed0"),
        0x0006F448: (84, "a1188526e84dbec45782d4201f866cc3d17d746db9e187633f71bffcc5f8c3dc"),
    }
    for entry, (size, digest) in qma_wrapper_exact_expected.items():
        body = recovered_function(entry)
        if len(body) != size or hashlib.sha256(body).hexdigest() != digest:
            raise AssertionError(f"QST QMA6100 wrapper body changed: 0x{entry:08x}")
    ownership_summary = json.loads((DOCS / "FUNCTION-OWNERSHIP-SUMMARY.json").read_text())
    if ownership_summary["function_count"] != len(ownership_rows):
        raise AssertionError("function ownership summary count mismatch")
    if ownership_summary["manual_provenance_supplement_count"] != len(supplemental_keys):
        raise AssertionError("manual function supplement count mismatch")

    with (DOCS / "COVERAGE.csv").open(newline="") as handle:
        rows = list(csv.DictReader(handle))
    if len(rows) < 40:
        raise AssertionError(f"coverage ledger unexpectedly short: {len(rows)}")
    statuses = {row["status"] for row in rows}
    if not {"implemented", "partial", "withheld", "separate"} <= statuses:
        raise AssertionError(f"missing coverage dispositions: {statuses}")

    with (ROOT / "docs" / "reference" / "r1-capability-matrix.csv").open(newline="") as handle:
        audit_rows = list(csv.DictReader(handle))
    audit_ids = {row["id"] for row in audit_rows}
    if len(audit_rows) < 202:
        raise AssertionError(f"unexpected R1 audit ledger size: {len(audit_rows)}")
    coverage_text = (DOCS / "COVERAGE.csv").read_text()
    if "100/200/1000 scheduling and retry timing,R1-202,deferred" in coverage_text:
        raise AssertionError("R1-202 raw-tick runtime policy regressed to deferred")
    referenced_ids = set(re.findall(r"R1-\d{3}", coverage_text))
    unknown_ids = referenced_ids - audit_ids
    if unknown_ids:
        raise AssertionError(f"coverage references missing audit rows: {sorted(unknown_ids)}")
    required_recent = {f"R1-{number}" for number in range(193, 198)} | {
        "R1-200", "R1-201", "R1-202"
    }
    missing_recent = required_recent - referenced_ids
    if missing_recent:
        raise AssertionError(f"recent audit findings not reconciled: {sorted(missing_recent)}")

    for target in ("test", "sanitize", "arm-objects", "sim"):
        subprocess.run(["make", "-C", str(PROJECT), target], check=True)

    sdk_root = os.environ.get("OPENR1_SDK_ROOT")
    flashdb_root = os.environ.get("OPENR1_FLASHDB_ROOT")
    bma456_root = os.environ.get("OPENR1_BMA456_ROOT")
    lis2dw12_root = os.environ.get("OPENR1_LIS2DW12_ROOT")
    st25dvxxkc_root = os.environ.get("OPENR1_ST25DVXXKC_ROOT")
    tiny_aes_root = os.environ.get("OPENR1_TINY_AES_ROOT")
    iqs7211e_root = os.environ.get("OPENR1_IQS7211E_ROOT")
    azoteq_settings_root = os.environ.get("OPENR1_AZOTEQ_SETTINGS_ROOT")
    gnu_root = os.environ.get("OPENR1_GNU_INSTALL_ROOT")
    goodix_democode_root = os.environ.get("OPENR1_GOODIX_DEMOCODE_ROOT")
    vendor_checks = []
    if flashdb_root:
        subprocess.run([
            "make", "-C", str(PROJECT), "vendor-storage-test",
            f"FLASHDB_ROOT={flashdb_root}",
        ], check=True)
        vendor_checks.append("FlashDB/FAL")
    if tiny_aes_root:
        subprocess.run([
            "make", "-C", str(PROJECT), "vendor-crypto-test",
            f"TINY_AES_ROOT={tiny_aes_root}",
        ], check=True)
        vendor_checks.append("tiny-AES-c/R1 crypto")
    if goodix_democode_root:
        subprocess.run([
            "make", "-C", str(PROJECT), "vendor-goodix-test",
            f"GOODIX_DEMOCODE_ROOT={goodix_democode_root}",
        ], check=True)
        vendor_checks.append("Goodix GH3X2X democode")
    if sdk_root and flashdb_root and bma456_root and lis2dw12_root and \
            st25dvxxkc_root and tiny_aes_root and iqs7211e_root and \
            azoteq_settings_root:
        subprocess.run([
            "make", "-C", str(PROJECT), "vendor-audit",
            f"SDK_ROOT={sdk_root}", f"FLASHDB_ROOT={flashdb_root}",
            f"BMA456_ROOT={bma456_root}", f"LIS2DW12_ROOT={lis2dw12_root}",
            f"ST25DVXXKC_ROOT={st25dvxxkc_root}",
            f"TINY_AES_ROOT={tiny_aes_root}",
            f"IQS7211E_ROOT={iqs7211e_root}",
            f"AZOTEQ_SETTINGS_ROOT={azoteq_settings_root}",
        ] + ([f"GOODIX_DEMOCODE_ROOT={goodix_democode_root}"]
             if goodix_democode_root else []), check=True)
        vendor_checks.append("vendor provenance")
    if sdk_root and flashdb_root and bma456_root and lis2dw12_root and \
            st25dvxxkc_root and tiny_aes_root and gnu_root and \
            goodix_democode_root:
        subprocess.run([
            "make", "-C", str(PROJECT), "sdk-verify",
            f"SDK_ROOT={sdk_root}", f"BMA456_ROOT={bma456_root}",
            f"LIS2DW12_ROOT={lis2dw12_root}", f"TINY_AES_ROOT={tiny_aes_root}",
            f"ST25DVXXKC_ROOT={st25dvxxkc_root}",
            f"FLASHDB_ROOT={flashdb_root}",
            f"GNU_INSTALL_ROOT={gnu_root}",
            f"GOODIX_DEMOCODE_ROOT={goodix_democode_root}",
        ], check=True)
        vendor_checks.append("Nordic SDK image")

    print(
        f"openR1 verified: {len(rows)} coverage rows against {len(audit_rows)} audit rows; "
        f"{len(ownership_rows)} functions source-gated; host/sanitizer/ARM builds passed"
        + (f"; optional checks: {', '.join(vendor_checks)}" if vendor_checks else "")
    )


if __name__ == "__main__":
    main()
