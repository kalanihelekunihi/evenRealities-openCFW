#!/usr/bin/env python3
"""Aggregate source/binding/link gate for the G2 PT protocol implementation."""
# SPDX-License-Identifier: MIT

from __future__ import annotations
import argparse,csv,hashlib,importlib.util,json,os,re,shutil,struct,subprocess,tempfile
from pathlib import Path

try:
 from . import analyze_g2_pt_protocol as stock_pt
except ImportError:
 import analyze_g2_pt_protocol as stock_pt

ROOT=Path(__file__).resolve().parents[1]
COMPONENT=ROOT/"components/apollo_main/core_overlay"
CORPUS=ROOT/"research/corpus/apollo-main/ghidra/pt-protocol"
AUTHENTICATED_DECOMP_INDEX=(
 ROOT/"research/corpus/apollo-main/ghidra/decomp/functions.jsonl")
AUTHENTICATED_DECOMP_BUNDLE=(
 ROOT/"research/corpus/apollo-main/ghidra/decomp/bundles/apollo-decomp-02.c")
OUTPUT=ROOT/"tools/manifests/g2-pt-protocol-source-summary.json"
CORE_CONFIG=COMPONENT/"overlay.json"
PT_BUILDER=ROOT/"components/apollo_main/pt_protocol/build_component.py"
OFFICIAL_COMPONENT=(ROOT/"blobs/official/g2-2.2.6.10"/
 "ota_s200_firmware_ota.bin")
SOURCES=[COMPONENT/name for name in (
 "pt_protocol_procsr.c","pt_protocol_handlers_basic.c",
 "pt_protocol_handlers_config.c","pt_protocol_handlers_data.c",
 "pt_protocol_handlers_display.c","pt_protocol_handlers_sensors.c",
 "pt_protocol_handlers_services.c","pt_protocol_handlers_audio.c",
 "pt_protocol_handlers_transfer.c","pt_protocol_service.c",
 "pt_protocol_platform_adapter.c","pt_protocol_production_entry.c",
 "pt_protocol_board_backend.c","pt_protocol_board_leaf_candidates.c",
 "pt_protocol_lc3_setup.c")]
LC3_SETUP_SOURCE=COMPONENT/"pt_protocol_lc3_setup.c"
HANDLERS=[p for p in SOURCES if "handlers_" in p.name]
HEADERS=sorted(COMPONENT.glob("pt_protocol*.h"))
STOCK_BODY_BYTES=32866
CORPUS_DIGESTS={
 "HARVEST.json":"acd2966b7aaad1c036c4b96f513b3fafd10057850b31926010567d30de041eec",
 "command-map.tsv":"c4e15781296be7ec8309589c16ada131045e91af25fb4f20df2f3083fe5cb4af",
 "functions.jsonl":"1ad1d5f642570530887920a913934b4cc804254ff9d806445687d47d6ef2aaa5",
}
OFFICIAL_COMPONENT_SIZE=3523396
OFFICIAL_COMPONENT_SHA256=(
 "36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863")
OFFICIAL_RUN_BASE=0x00438000
OFFICIAL_PREAMBLE_BYTES=32
AUTHENTICATED_DECOMP_INDEX_SHA256=(
 "9fd9c1c34e17abb977f2ccb32a931d9b96743db2db10707de19bf9ea6ae42662")
LENS_SYNC_TRANSPORT_ABI=(
 "int32_t (*)(uint16_t, const void *, uint32_t, uint32_t, uint8_t, "
 "uint8_t, uint32_t)")
LENS_SYNC_TRANSPORT_EVIDENCE={
 "stock_wrapper_runtime_address":0x00464C36,
 "stock_wrapper_size":132,
 "stock_wrapper_sha256":(
  "dcd1d05418ab3f4e6a90d23398f03b8cba1ed7632e480ac7563a358179009753"),
 "stock_transport_runtime_address":0x00464772,
 "stock_transport_thumb_pointer":0x00464773,
 "stock_transport_size":956,
 "stock_transport_sha256":(
  "6cb194e4428db0c9c66747ffaa0c77daf605f07c1e4face23c68287d681f34aa"),
 "stock_wrapper_transport_callsite":0x00464CB2,
 "stock_trailing_arguments":[5,2,0],
 "stock_wrapper_signature":(
  "void FUN_00464c36(undefined2 param_1,undefined4 param_2,undefined2 "
  "param_3,undefined4 param_4);"),
 "stock_transport_signature":(
  "undefined4 FUN_00464772(undefined2 param_1,int param_2,uint param_3,"
  "undefined4 param_4,undefined1 param_5,byte param_6,undefined4 param_7);"),
 "stock_wrapper_decompilation_sha256":(
  "41d3c036d53486c1e128740012f81b5157683f0e4f67f321932a100d59b541aa"),
 "stock_wrapper_call_expression":(
  "FUN_00464772(param_1,param_2,param_3,param_4,5,2,0);"),
}
LC3_SETUP_ABI="void *(*)(int, int, int, void *)"
LC3_SETUP_BOUNDED_ABI="void *(*)(int, int, int, void *, size_t)"
LC3_SETUP_EVIDENCE={
 "stock_primary_runtime_address":0x0059123A,
 "stock_primary_size":314,
 "stock_primary_sha256":(
  "04f7f722ef30afdfae612d0f6622cb4811918c8a8f4dc30b1ee99f95f42572c8"),
 "stock_runtime_address":0x00591374,
 "stock_thumb_pointer":0x00591375,
 "stock_size":22,
 "stock_sha256":(
  "98ecf298571e96939bfefd863c514116a4e5ccf638b8023c395a465175da635d"),
 "stock_wrapper_primary_callsite":0x00591382,
 "stock_service_setup_runtime_address":0x0057A926,
 "stock_service_setup_size":26,
 "stock_service_setup_sha256":(
  "043e57c0075b4e4c1043d93fe1c9cb7fb3abe91ba6ed24af5160a198f7eb3851"),
 "stock_service_setup_callsites":[0x0054F4B6,0x0058F7A2,0x0058F7A8,0x0058F85E],
 "fixed_context_starts":[
  0x20106A7C,0x201074C0,0x20107F04,0x20108948],
 "next_allocation_start":0x2010938C,
 "fixed_context_slot_bytes":0xA44,
 "fixed_context_header_bytes":0x1C,
 "fixed_context_storage_bytes":2600,
 "stock_context_pointer_table_runtime_address":0x0058F880,
 "stock_context_pointer_table_size":16,
 "stock_context_pointer_table_sha256":(
  "fffba463d4f37a1a2f9f2afa67dedf142206dbf5459bf50f7923918aad8c6410"),
 "stock_next_context_literal_cells":[0x0054F9A0,0x0057B3E4],
 "stock_next_slot_literal_cell":0x0058A3A8,
 "configuration_initialization":"runtime-provided; statically unproven",
 "configuration_safety":"computed size must fit authenticated 2600-byte storage",
 "upstream":"Google/liblc3",
 "upstream_source":"third_party/liblc3/src/lc3.c",
 "upstream_commit":"96a3af0beb5487aca3b98a4b992a539a1f6d80d1",
 "upstream_license":"Apache-2.0",
 "upstream_license_path":"third_party/liblc3/LICENSE",
 "adapted_source":"components/apollo_main/core_overlay/pt_protocol_lc3_setup.c",
 "upstream_copyright":"Copyright 2022 Google LLC",
 "upstream_license_sha256":(
  "cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30"),
 "production_source_routed":True,
 "routing":"source_local_authenticated_layout",
}
BOARD_OPERATIONS={
 "OPEN_CFW_PT_OP_SET_BOX_DETECTED","OPEN_CFW_PT_OP_CODEC_DELAY",
 "OPEN_CFW_PT_OP_STORE_TERMINAL_MODE","OPEN_CFW_PT_OP_LOAD_TERMINAL_MODE",
 "OPEN_CFW_PT_OP_POST_INPUT_MESSAGE","OPEN_CFW_PT_OP_GET_PRODUCT_MODE",
 "OPEN_CFW_PT_OP_SET_PRODUCT_MODE","OPEN_CFW_PT_OP_READ_TOUCH_DIAGNOSTIC",
 "OPEN_CFW_PT_OP_WRITE_PSN_14","OPEN_CFW_PT_OP_WRITE_SENSOR_CALIBRATION_36",
 "OPEN_CFW_PT_OP_BUZZER_TEST","OPEN_CFW_PT_OP_BUZZER_READ",
 "OPEN_CFW_PT_OP_BUZZER_WRITE","OPEN_CFW_PT_OP_UPDATE_ONBOARDING",
 "OPEN_CFW_PT_OP_PRODUCTION_RESET","OPEN_CFW_PT_OP_SET_CHARGER_TEST",
 "OPEN_CFW_PT_OP_READ_IDENTIFIER_6","OPEN_CFW_PT_OP_READ_SYSTEM_TEXT",
 "OPEN_CFW_PT_OP_SET_SYNC_READY","OPEN_CFW_PT_OP_READ_BOOLEAN_FLAG",
 "OPEN_CFW_PT_OP_READ_PAIR_STATE","OPEN_CFW_PT_OP_READ_DIAGNOSTIC_BLOB_36",
 "OPEN_CFW_PT_OP_READ_FONT_VERSION","OPEN_CFW_PT_OP_READ_DISPLAY_VALUE",
 "OPEN_CFW_PT_OP_READ_IMU_SAMPLE_36","OPEN_CFW_PT_OP_READ_TOUCH_DIFFERENCES",
 "OPEN_CFW_PT_OP_READ_CALIBRATION_ORIENTATION",
 "OPEN_CFW_PT_OP_READ_PLATFORM_IDENTIFIER",
 "OPEN_CFW_PT_OP_SET_DISPLAY_RUNTIME_FLAG","OPEN_CFW_PT_OP_GET_AGING_MODE",
 "OPEN_CFW_PT_OP_READ_SESSION_STATUS","OPEN_CFW_PT_OP_SET_BOX_STATE",
 "OPEN_CFW_PT_OP_READ_BOX_SUMMARY_7","OPEN_CFW_PT_OP_READ_BOX_DETAIL_6",
 "OPEN_CFW_PT_OP_WRITE_TIME_21",
 "OPEN_CFW_PT_OP_STORAGE_READY","OPEN_CFW_PT_OP_READ_METADATA_32",
 "OPEN_CFW_PT_OP_OPEN_PAYLOAD","OPEN_CFW_PT_OP_READ_PAYLOAD_AT",
 "OPEN_CFW_PT_OP_CLOSE_PAYLOAD",
 "OPEN_CFW_PT_OP_OTA_INITIALIZE","OPEN_CFW_PT_OP_OTA_DISPATCH",
 "OPEN_CFW_PT_OP_OTA_STATUS",
 "OPEN_CFW_PT_OP_STORAGE_SELF_TEST",
 "OPEN_CFW_PT_OP_READ_HARDWARE_IDENTIFIER",
 "OPEN_CFW_PT_OP_UART_SYNC_TEST",
 "OPEN_CFW_PT_OP_LENS_SYNC_TEST",
 "OPEN_CFW_PT_OP_SET_TEST_SCREEN","OPEN_CFW_PT_OP_SET_DISPLAY_PARAMETERS",
 "OPEN_CFW_PT_OP_AUDIO_READ_VERSION_5",
 "OPEN_CFW_PT_OP_AUDIO_READ_CHUNK",
 "OPEN_CFW_PT_OP_AUDIO_CONTROL",
 "OPEN_CFW_PT_OP_SET_AGING_MODE",
 "OPEN_CFW_PT_OP_CALIBRATE_AMBIENT",
 "OPEN_CFW_PT_OP_AUDIO_READ_METRICS_32",
 "OPEN_CFW_PT_OP_POST_RESPONSE",
}
BOARD_SOURCE_OVERLAY_TARGETS={
 0x004751C8:"open_cfw_memory_compare",
 0x00474550:"open_cfw_file_open",
 0x004745F4:"open_cfw_file_close",
 0x00474634:"open_cfw_file_read",
 0x00474682:"open_cfw_file_write",
 0x00474814:"open_cfw_file_seek",
 0x00474870:"open_cfw_file_tell",
 0x004748B4:"open_cfw_file_size",
 0x0047498C:"open_cfw_file_remove",
 0x00454EFE:"open_cfw_freertos_task_get_tick_count",
 0x004487E4:"OTA_SetInterface",
 0x00448670:"OTA_FrameDispatch",
 0x004491AA:"open_cfw_cmsis_thread_get_id",
 0x004491B2:"open_cfw_cmsis_thread_set_priority",
 0x00449376:"open_cfw_cmsis_delay",
 0x0045A568:"open_cfw_lens_side",
 0x004A7820:"open_cfw_kvdb_onboarding_config_update_and_persist",
 0x0046D584:"open_cfw_font_manager_xip_name",
 0x005135E0:"open_cfw_opt3007_assign_register_map",
 0x004A6BCE:"open_cfw_sensor_hub_calibration_init",
 0x005099F8:"open_cfw_nvdb_sensor_caldata_ag_read",
 0x004AFC10:"open_cfw_nvdb_sys_dt_reset_aging",
 0x004ABE66:"open_cfw_nvdb_product_mode_update",
 0x004ABE8C:"open_cfw_nvdb_product_mode_read",
 0x004AC744:"open_cfw_box_detect_set_local_lid",
 0x004AC718:"open_cfw_box_detect_set_local_level",
 0x004AC72E:"open_cfw_box_detect_set_local_charging",
 0x004AC798:"open_cfw_box_detect_state_updated",
 0x004AF11C:"open_cfw_nvdb_sys_dt_write",
 0x004AF73A:"open_cfw_nvdb_sys_dt_get",
 0x004AF7B8:"open_cfw_nvdb_sys_dt_read",
 0x004AFFC0:"open_cfw_nvdb_sys_dt_write_psn_to_otp",
 0x00502DAE:"open_cfw_gesture_get_proximity",
 0x0050999E:"open_cfw_nvdb_sensor_caldata_ag_update",
 0x0055B6A8:"open_cfw_cy8c_read_difference",
 0x0057D870:"open_cfw_svc_codec_mic_delay_1bit",
 0x0058FA60:"open_cfw_nvdb_buzzer_frequency_get",
 0x0058FA66:"open_cfw_nvdb_buzzer_duty_get",
 0x0058FA6C:"open_cfw_nvdb_buzzer_update",
}
BOARD_RETAINED_PROVIDERS={
 0x004A5B90:"imu_get_latest_complete_sample",
 0x004A5D38:"imu_get_orientation_vector",
 0x004A6456:"imu_read_who_am_i",
 0x004A64C8:"mag_read_who_am_i",
 0x00502C88:"DRV_BuzzerStart",
 0x00502D4C:"DRV_BuzzerStop",
 0x005130A6:"input_msg_send_id3",
 0x0058F950:"production_reset_action",
 0x005128F8:"charger_test_disable",
 0x0051299C:"charger_test_enable",
 0x0052DEE6:"codec_platform_identifier",
 0x00512C84:"hardware_identifier_0",
 0x004700B4:"hardware_identifier_1",
 0x00512B20:"hardware_identifier_2",
 0x004CA070:"display_hardware_identifier",
 0x0058F936:"ambient_identifier_initialize",
 0x0058F8CC:"ambient_identifier_step_1",
 0x0058F8D8:"ambient_identifier_step_2",
 0x0058F922:"ambient_identifier_low",
 0x0058F92C:"ambient_identifier_high",
 0x00541790:"uart_sync_write",
 0x004651E0:"lens_sync_send",
 0x004441EC:"screen_show",
 0x004443CC:"screen_hide",
 0x0044347A:"display_state",
 0x004CA1EE:"display_brightness",
 0x0046C984:"display_stage_1",
 0x0046C9DC:"display_stage_2",
 0x0046C9AA:"display_stage_3",
 0x004CA24A:"display_offset",
 0x0050938E:"audio_status_get",
 0x0057B352:"audio_path_format",
 0x0058F69A:"audio_channel_0_start",
 0x0058F7B0:"audio_channel_0_stop",
 0x0058F74A:"audio_channel_1_start",
 0x0058F806:"audio_channel_1_stop",
 0x0053A5BE:"audio_codec_route",
 0x0044A1FE:"time_configure",
 0x0044A19A:"time_capture",
 0x0058F8E4:"ambient_read",
 0x0044B0AE:"system_reset",
 0x00542D4C:"display_postprocess",
 0x0058F486:"font_crc_check_0",
 0x0058F490:"font_crc_check_1",
}
BOARD_LEAF_CANDIDATES={
 0x0044347A:("open_cfw_pt_board_display_state",6),
 0x004441EC:("open_cfw_pt_board_screen_show",208),
 0x004443CC:("open_cfw_pt_board_screen_hide",216),
 0x0044A1FE:("open_cfw_pt_board_time_configure",180),
 0x004651E0:("open_cfw_pt_board_lens_sync_send",636),
 0x004700B4:("open_cfw_pt_board_hardware_identifier_1",162),
 0x0044A19A:("open_cfw_pt_board_time_capture",44),
 0x0046C984:("open_cfw_pt_board_display_stage_1",38),
 0x0046C9AA:("open_cfw_pt_board_display_stage_3",38),
 0x0046C9DC:("open_cfw_pt_board_display_stage_2",56),
 0x004CA070:("open_cfw_pt_board_display_hardware_identifier",182),
 0x004CA1EE:("open_cfw_pt_board_display_brightness",92),
 0x004CA24A:("open_cfw_pt_board_display_offset",96),
 0x00502C88:("open_cfw_pt_board_buzzer_start",32),
 0x00502D4C:("open_cfw_pt_board_buzzer_stop",10),
 0x0050938E:("open_cfw_pt_board_audio_status_get",30),
 0x005128F8:("open_cfw_pt_board_charger_test_disable",158),
 0x0051299C:("open_cfw_pt_board_charger_test_enable",152),
 0x00512B20:("open_cfw_pt_board_hardware_identifier_2",146),
 0x00512C84:("open_cfw_pt_board_hardware_identifier_0",34),
 0x0052DEE6:("open_cfw_pt_board_codec_platform_identifier",8),
 0x0053A5BE:("open_cfw_pt_board_audio_codec_route",34),
 0x00541790:("open_cfw_pt_board_uart_sync_write",20),
 0x0057B352:("open_cfw_pt_board_audio_path_format",38),
 0x0058F69A:("open_cfw_pt_board_audio_channel_0_start",176),
 0x0058F74A:("open_cfw_pt_board_audio_channel_1_start",102),
 0x0058F7B0:("open_cfw_pt_board_audio_channel_0_stop",86),
 0x0058F806:("open_cfw_pt_board_audio_channel_1_stop",96),
 0x005130A6:("open_cfw_pt_board_post_input_message_id3",26),
 0x0058F8CC:("open_cfw_pt_board_ambient_identifier_step_1",12),
 0x0058F8D8:("open_cfw_pt_board_ambient_identifier_step_2",12),
 0x0058F8E4:("open_cfw_pt_board_ambient_read",62),
 0x0058F922:("open_cfw_pt_board_ambient_identifier_low",10),
 0x0058F92C:("open_cfw_pt_board_ambient_identifier_high",10),
 0x0058F936:("open_cfw_pt_board_ambient_identifier_initialize",26),
 0x0058F950:("open_cfw_pt_board_production_reset",20),
 0x0044B0AE:("open_cfw_pt_board_system_reset",8),
 0x00542D4C:("open_cfw_pt_board_display_postprocess",120),
 0x0058F486:("open_cfw_pt_board_font_crc_check_0",10),
 0x0058F490:("open_cfw_pt_board_font_crc_check_1",10),
}

# The semantic-C board leaves are not themselves a closed provider graph.  Pin
# every fixed-address callable they invoke so a new stock dependency cannot be
# hidden behind the source-owned top-level leaf count.  Thumb callable values
# retain bit zero here; ownership is resolved against the even overlay entry.
BOARD_LEAF_CALLABLE_BINDINGS={
 "OPEN_CFW_PT_INPUT_LOG_FAILURE":("unsigned int (*)(const char *, ...)",0x004733EF),
 "OPEN_CFW_PT_AUDIO_STRUCTURED_LOG":("void (*)(uint32_t, const char *, const char *, const char *, uint32_t, const char *, ...)",0x0043D575),
 "OPEN_CFW_PT_AUDIO_TRACE_LOG":(
  "void (*)(uint32_t, const char *, ...)",0x0043CE9F),
 "OPEN_CFW_PT_DISPLAY_POSTPROCESS_REFRESH":("void (*)(void)",0x004D9A85),
 "OPEN_CFW_PT_DISPLAY_POSTPROCESS_ONBOARDING":("int (*)(uint8_t, const uint8_t *)",0x004A7821),
 "OPEN_CFW_PT_DISPLAY_POSTPROCESS_REMOVE":("int (*)(const void *)",0x0047498D),
 "OPEN_CFW_PT_MRAM_DELETE_ALL_RECORDS":("void (*)(void)",0x0047ACF9),
 "OPEN_CFW_PT_PRIVACY_CLEAR":("void (*)(void)",0x004D28B1),
 "OPEN_CFW_PT_BUZZER_PWM_UPDATE":(
  "void (*)(uint32_t, uint8_t)",0x00502791),
 "OPEN_CFW_PT_BUZZER_PWM_START":("void (*)(void)",0x0050276F),
 "OPEN_CFW_PT_BUZZER_PWM_STOP":("void (*)(void)",0x0050277F),
 "OPEN_CFW_PT_BUZZER_TIMER_STOP":("int (*)(void *)",0x004494D9),
 "OPEN_CFW_PT_HARDWARE_IDENTIFIER_READ":("void (*)(uint32_t, uint32_t *)",0x00480D73),
 "OPEN_CFW_PT_HARDWARE_IDENTIFIER_1_INITIALIZE":("int (*)(void)",0x0046FE39),
 "OPEN_CFW_PT_HARDWARE_IDENTIFIER_1_PREPARE":("void (*)(void)",0x00470F69),
 "OPEN_CFW_PT_HARDWARE_IDENTIFIER_1_READ":("int (*)(uint32_t *)",0x00470029),
 "OPEN_CFW_PT_HARDWARE_IDENTIFIER_1_FINISH":("void (*)(void)",0x00470E91),
 "OPEN_CFW_PT_MSPI_CONTROL":("int32_t (*)(void *, uint32_t, uint32_t)",0x004C26E1),
 "OPEN_CFW_PT_UART_TICK_GET":("uint32_t (*)(void)",0x004490CD),
 "OPEN_CFW_PT_UART_SEMAPHORE_ACQUIRE":("int (*)(void *, uint32_t)",0x0044994F),
 "OPEN_CFW_PT_UART_DELAY_US":("void (*)(uint32_t)",0x00491103),
 "OPEN_CFW_PT_CODEC_ROUTE_SET":("int (*)(uint32_t, uint8_t)",0x00480FD7),
 "OPEN_CFW_PT_PCM_ROUTE":("void (*)(uint32_t)",0x0057B12D),
 "OPEN_CFW_PT_DISPLAY_REINITIALIZE":("void (*)(void)",0x0047381F),
 "OPEN_CFW_PT_DISPLAY_APPLY":("void (*)(uint32_t, uint32_t, uint32_t, uint32_t, uint32_t, uint32_t)",0x00474067),
 "OPEN_CFW_PT_LENS_SYNC_TRANSPORT":(LENS_SYNC_TRANSPORT_ABI,0x00464773),
 "OPEN_CFW_PT_MUTEX_ACQUIRE":("int (*)(void *, uint32_t)",0x004497B7),
 "OPEN_CFW_PT_MUTEX_RELEASE":("int (*)(void *)",0x0044981D),
 "OPEN_CFW_PT_QUEUE_SEND":("int (*)(void *, const void *, uint32_t, uint32_t)",0x00449ABF),
 "OPEN_CFW_PT_FAIL_STOP":("void (*)(void)",0x005FA0A5),
 "OPEN_CFW_PT_FILE_HEAP_ALLOCATE":("void *(*)(uint32_t)",0x00474CD3),
 "OPEN_CFW_PT_LENS_SYNC_RELEASE":("void (*)(void *)",0x00474D17),
 "OPEN_CFW_PT_EVENT_FLAGS_SET":("uint32_t (*)(void *, uint32_t)",0x004495E5),
 "OPEN_CFW_PT_THREAD_FLAGS_SET":("uint32_t (*)(void *, uint32_t)",0x00449239),
 "OPEN_CFW_PT_FILE_CLOSE":("int (*)(void *)",0x004745F5),
 "OPEN_CFW_PT_TIME_READ":("void (*)(void *)",0x0047EF11),
 "OPEN_CFW_PT_RTC_SET_TIME":("void (*)(const void *)",0x0047EE79),
 "OPEN_CFW_PT_AMBIENT_BUS_READ":("int (*)(uint32_t, uint32_t, const void *, uint32_t, void *, uint32_t)",0x0050436F),
 "OPEN_CFW_PT_AMBIENT_BUS_WRITE":("int (*)(uint32_t, uint32_t, const void *, uint32_t, const void *, uint32_t)",0x005044B5),
 "OPEN_CFW_PT_LENS_SIDE":("uint8_t (*)(void)",0x0045A569),
 "OPEN_CFW_PT_AUDIO_CODEC_ROUTE":("void (*)(uint32_t, uint32_t)",0x00480F0D),
 "OPEN_CFW_PT_DELAY_TICKS":("int (*)(uint32_t)",0x00449377),
}
BOARD_LEAF_LOCAL_SOURCE_CALLABLES={
 "OPEN_CFW_PT_LC3_SETUP_ENCODER":(
  LC3_SETUP_BOUNDED_ABI,"open_cfw_pt_lc3_setup_encoder_bounded"),
 "OPEN_CFW_PT_AUDIO_LOG_FILTER":(
  "uint32_t (*)(void)","open_cfw_pt_audio_log_filter"),
 "OPEN_CFW_PT_DISPLAY_POSTPROCESS_SEND":(
  "void (*)(uint32_t, uint32_t, uint32_t, uint32_t)",
  "open_cfw_pt_display_postprocess_send"),
 "OPEN_CFW_PT_UART_WRITE":(
  "int (*)(const uint8_t *, uint32_t, uint32_t)",
  "open_cfw_pt_uart_write"),
 "OPEN_CFW_PT_BUZZER_APPLY":(
  "void (*)(uint32_t, uint8_t)","open_cfw_pt_buzzer_apply"),
 "OPEN_CFW_PT_BUZZER_DISABLE":(
  "void (*)(uint32_t)","open_cfw_pt_buzzer_disable"),
 "OPEN_CFW_PT_BUZZER_PREPARE":(
  "void (*)(void)","open_cfw_pt_buzzer_prepare"),
 "OPEN_CFW_PT_AUDIO_ENCODER_SETUP":(
  "void (*)(void *)","open_cfw_pt_audio_encoder_setup"),
 "OPEN_CFW_PT_UART_TRANSFER_ABORT":(
  "void (*)(void)","open_cfw_pt_uart_transfer_abort"),
 "OPEN_CFW_PT_UART_TRANSFER_START":(
  "void (*)(const void *, uint32_t)","open_cfw_pt_uart_transfer_start"),
 "OPEN_CFW_PT_UART_STATUS_GET":(
  "int (*)(void *, uint32_t *)","open_cfw_pt_uart_status_get"),
 "OPEN_CFW_PT_SYSTEM_RESET_INNER":(
  "void (*)(void)","open_cfw_pt_system_reset_inner"),
 "OPEN_CFW_PT_DISPLAY_POSTPROCESS_STATE_0":(
  "uint8_t (*)(void)","open_cfw_pt_display_postprocess_state_0"),
 "OPEN_CFW_PT_DISPLAY_POSTPROCESS_STATE_1":(
  "uint8_t (*)(void)","open_cfw_pt_display_postprocess_state_1"),
 "OPEN_CFW_PT_DISPLAY_POSTPROCESS_STATE_2":(
  "uint8_t (*)(void)","open_cfw_pt_display_postprocess_state_2"),
 "OPEN_CFW_PT_SECONDS_TO_TIME":(
  "void (*)(uint32_t, void *)","open_cfw_pt_seconds_to_time"),
 "OPEN_CFW_PT_TIME_TO_SECONDS":(
  "int32_t (*)(const void *)","open_cfw_pt_time_to_seconds"),
 "OPEN_CFW_PT_TIME_OUTPUT":(
  "void (*)(uint32_t, void *)","open_cfw_pt_time_output"),
 "OPEN_CFW_PT_DISPLAY_BUFFER_WRITE":(
  "uint32_t (*)(void *, uintptr_t, uint32_t)",
  "open_cfw_pt_display_buffer_write"),
 "OPEN_CFW_PT_LENS_SYNC_ALLOCATE":(
  "void *(*)(uint32_t)","open_cfw_pt_lens_sync_allocate"),
 "OPEN_CFW_PT_INPUT_MESSAGE_SEND":(
  "void (*)(const void *)","open_cfw_pt_input_message_send"),
 "OPEN_CFW_PT_CODEC_MIC_ENABLE":(
  "void (*)(uint32_t)","open_cfw_pt_codec_mic_enable"),
 "OPEN_CFW_PT_PDM_MIC_ENABLE":(
  "void (*)(uint32_t)","open_cfw_pt_pdm_mic_enable"),
 "OPEN_CFW_PT_AUDIO_PATH_FORMAT_PROVIDER":(
  "void (*)(uint8_t, uint16_t, char *, uint32_t)",
  "open_cfw_pt_audio_path_format_provider"),
 "OPEN_CFW_PT_AUDIO_REGISTER":(
  "int (*)(uint32_t, uint8_t, const void *)",
  "open_cfw_pt_audio_register"),
 "OPEN_CFW_PT_AUDIO_REMOVE":(
  "int (*)(uint32_t, uint8_t)","open_cfw_pt_audio_remove"),
 "OPEN_CFW_PT_AUDIO_UNREGISTER":(
  "void (*)(uint8_t)","open_cfw_pt_audio_unregister"),
 "OPEN_CFW_PT_AMBIENT_ASSIGN":(
  "void (*)(void *, uint32_t)","open_cfw_pt_ambient_assign"),
 "OPEN_CFW_PT_AMBIENT_SAMPLE":(
  "uint16_t (*)(void *)","open_cfw_pt_ambient_sample"),
 "OPEN_CFW_PT_AMBIENT_RAW_READ":(
  "uint32_t (*)(uint32_t)","open_cfw_pt_ambient_raw_read"),
 "OPEN_CFW_PT_FONT_XIP_ACQUIRE":(
  "void (*)(void)","open_cfw_pt_font_xip_acquire"),
 "OPEN_CFW_PT_FONT_XIP_RELEASE":(
  "void (*)(void)","open_cfw_pt_font_xip_release"),
 "OPEN_CFW_PT_HARDWARE_IDENTIFIER_1_ACQUIRE":(
  "void (*)(void)","open_cfw_pt_font_xip_acquire"),
 "OPEN_CFW_PT_HARDWARE_IDENTIFIER_1_RELEASE":(
  "void (*)(void)","open_cfw_pt_font_xip_release"),
 "OPEN_CFW_PT_DISPLAY_POSTPROCESS_COMMIT":(
  "void (*)(void)","open_cfw_pt_display_postprocess_commit"),
 "OPEN_CFW_PT_CHARGER_OPEN":(
  "void *(*)(const void *, uint8_t)","open_cfw_pt_charger_open"),
 "OPEN_CFW_PT_CHARGER_DISABLE":(
  "int32_t (*)(void *, uint32_t)","open_cfw_pt_charger_disable"),
 "OPEN_CFW_PT_CHARGER_ENABLE":(
  "int32_t (*)(void *, uint32_t)","open_cfw_pt_charger_enable"),
 "OPEN_CFW_PT_HARDWARE_IDENTIFIER_2_READ":(
  "int32_t (*)(const void *, uint32_t, uint8_t *, uint32_t)",
  "open_cfw_pt_hardware_identifier_2_read"),
}
BOARD_LEAF_SOURCE_OVERLAY_TARGETS={
 "OPEN_CFW_PT_INPUT_LOG_FAILURE":"open_cfw_log_format_dispatch",
 "OPEN_CFW_PT_AUDIO_STRUCTURED_LOG":"open_cfw_easylogger_output",
 "OPEN_CFW_PT_DISPLAY_POSTPROCESS_REFRESH":"open_cfw_service_kvdb_invalidate_magic",
 "OPEN_CFW_PT_DISPLAY_POSTPROCESS_ONBOARDING":"open_cfw_kvdb_onboarding_config_update_and_persist",
 "OPEN_CFW_PT_DISPLAY_POSTPROCESS_REMOVE":"open_cfw_file_remove",
 "OPEN_CFW_PT_HARDWARE_IDENTIFIER_READ":"open_cfw_mcuctrl_info_get",
 "OPEN_CFW_PT_CODEC_ROUTE_SET":"open_cfw_gpio_state_write",
 "OPEN_CFW_PT_DISPLAY_REINITIALIZE":"open_cfw_lv_display_lock",
 "OPEN_CFW_PT_DISPLAY_APPLY":"open_cfw_display_send_reflash",
 "OPEN_CFW_PT_MUTEX_ACQUIRE":"open_cfw_cmsis_mutex_acquire",
 "OPEN_CFW_PT_MUTEX_RELEASE":"open_cfw_cmsis_mutex_release",
 "OPEN_CFW_PT_QUEUE_SEND":"open_cfw_cmsis_message_queue_put",
 "OPEN_CFW_PT_FAIL_STOP":"ulSetInterruptMask",
 "OPEN_CFW_PT_LENS_SYNC_RELEASE":"open_cfw_file_heap_free",
 "OPEN_CFW_PT_EVENT_FLAGS_SET":"open_cfw_cmsis_event_flags_set",
 "OPEN_CFW_PT_THREAD_FLAGS_SET":"open_cfw_cmsis_thread_flags_set",
 "OPEN_CFW_PT_FILE_HEAP_ALLOCATE":"open_cfw_file_heap_allocate",
 "OPEN_CFW_PT_FILE_CLOSE":"open_cfw_file_close",
 "OPEN_CFW_PT_MRAM_DELETE_ALL_RECORDS":"open_cfw_mram_delete_all_records",
 "OPEN_CFW_PT_PRIVACY_CLEAR":"open_cfw_cordio_dm_privacy_clear",
 "OPEN_CFW_PT_TIME_READ":"open_cfw_rtc_time_get",
 "OPEN_CFW_PT_RTC_SET_TIME":"open_cfw_rtc_time_set",
 "OPEN_CFW_PT_LENS_SIDE":"open_cfw_lens_side",
 "OPEN_CFW_PT_AUDIO_CODEC_ROUTE":"open_cfw_gpio_pinconfig",
 "OPEN_CFW_PT_DELAY_TICKS":"open_cfw_cmsis_delay",
 "OPEN_CFW_PT_UART_TICK_GET":"open_cfw_cmsis_kernel_get_tick_count",
 "OPEN_CFW_PT_UART_SEMAPHORE_ACQUIRE":"open_cfw_cmsis_semaphore_acquire",
 "OPEN_CFW_PT_UART_DELAY_US":"open_cfw_delay_us_passthrough",
 "OPEN_CFW_PT_BUZZER_TIMER_STOP":"open_cfw_cmsis_timer_stop",
}

# Fixed data is a separate supported ABI from the 53 top-level board-table
# entries.  Pinning the cast, address, and category prevents the leaf layer from
# silently acquiring a new SRAM, XIP, callback, or MMIO dependency.
BOARD_LEAF_DATA_BINDINGS={
 "OPEN_CFW_PT_AUDIO_LOG_FILTER_WORD":(
  "const volatile uint8_t *",0x20004543,"runtime_sram_data"),
 "OPEN_CFW_PT_AUDIO_LOG_FILE":("const char *",0x00706FEC,"immutable_flash_data"),
 "OPEN_CFW_PT_AUDIO_LOG_FUNCTION":("const char *",0x007899D0,"immutable_flash_data"),
 "OPEN_CFW_PT_AUDIO_LOG_MESSAGE":("const char *",0x007667B0,"immutable_flash_data"),
 "OPEN_CFW_PT_AUDIO_LOG_TAG":("const char *",0x007899A0,"immutable_flash_data"),
 "OPEN_CFW_PT_AUDIO_TRACE_MESSAGE":("const char *",0x007451A0,"immutable_flash_data"),
 "OPEN_CFW_PT_SERVICE_AUDIO_LOG_TAG":(
  "const char *",0x0078BE1C,"immutable_flash_data"),
 "OPEN_CFW_PT_SERVICE_AUDIO_LOG_FILE":(
  "const char *",0x007053C4,"immutable_flash_data"),
 "OPEN_CFW_PT_SERVICE_AUDIO_REGISTER_FUNCTION":(
  "const char *",0x00782E34,"immutable_flash_data"),
 "OPEN_CFW_PT_SERVICE_AUDIO_REGISTER_INVALID_MESSAGE":(
  "const char *",0x0074D82C,"immutable_flash_data"),
 "OPEN_CFW_PT_SERVICE_AUDIO_REGISTER_INVALID_TRACE":(
  "const char *",0x0072CE6C,"immutable_flash_data"),
 "OPEN_CFW_PT_SERVICE_AUDIO_REGISTER_OCCUPIED_MESSAGE":(
  "const char *",0x006FCB6C,"immutable_flash_data"),
 "OPEN_CFW_PT_SERVICE_AUDIO_REGISTER_OCCUPIED_TRACE":(
  "const char *",0x006E9AF0,"immutable_flash_data"),
 "OPEN_CFW_PT_SERVICE_AUDIO_REGISTER_SUCCESS_MESSAGE":(
  "const char *",0x0074D854,"immutable_flash_data"),
 "OPEN_CFW_PT_SERVICE_AUDIO_REGISTER_SUCCESS_TRACE":(
  "const char *",0x00737C34,"immutable_flash_data"),
 "OPEN_CFW_PT_SERVICE_AUDIO_REMOVE_FUNCTION":(
  "const char *",0x0077B314,"immutable_flash_data"),
 "OPEN_CFW_PT_SERVICE_AUDIO_REMOVE_EMPTY_MESSAGE":(
  "const char *",0x0077B32C,"immutable_flash_data"),
 "OPEN_CFW_PT_SERVICE_AUDIO_REMOVE_EMPTY_TRACE":(
  "const char *",0x007591B0,"immutable_flash_data"),
 "OPEN_CFW_PT_SERVICE_AUDIO_REMOVE_MISMATCH_MESSAGE":(
  "const char *",0x00742A9C,"immutable_flash_data"),
 "OPEN_CFW_PT_SERVICE_AUDIO_REMOVE_MISMATCH_TRACE":(
  "const char *",0x00722628,"immutable_flash_data"),
 "OPEN_CFW_PT_SERVICE_AUDIO_REMOVE_SUCCESS_MESSAGE":(
  "const char *",0x00770BD8,"immutable_flash_data"),
 "OPEN_CFW_PT_SERVICE_AUDIO_REMOVE_SUCCESS_TRACE":(
  "const char *",0x0074D87C,"immutable_flash_data"),
 "OPEN_CFW_PT_FONT_LOG_TAG":("const char *",0x00785CD0,"immutable_flash_data"),
 "OPEN_CFW_PT_FONT_LOG_FILE":("const char *",0x0070258C,"immutable_flash_data"),
 "OPEN_CFW_PT_FONT_ACQUIRE_FUNCTION":("const char *",0x00776EA4,"immutable_flash_data"),
 "OPEN_CFW_PT_FONT_ACQUIRE_MESSAGE":("const char *",0x00753E28,"immutable_flash_data"),
 "OPEN_CFW_PT_FONT_ACQUIRE_TRACE":("const char *",0x00729114,"immutable_flash_data"),
 "OPEN_CFW_PT_FONT_RELEASE_FUNCTION":("const char *",0x00776EBC,"immutable_flash_data"),
 "OPEN_CFW_PT_FONT_RELEASE_MESSAGE":("const char *",0x00749A74,"immutable_flash_data"),
 "OPEN_CFW_PT_FONT_RELEASE_TRACE":("const char *",0x00729148,"immutable_flash_data"),
 "OPEN_CFW_PT_INPUT_QUEUE_FAILURE_FORMAT":("const char *",0x00739E54,"immutable_flash_data"),
 "OPEN_CFW_PT_UART_INITIALIZED":("const volatile uint8_t *",0x20074FC9,"runtime_sram_data"),
 "OPEN_CFW_PT_UART_DEVICE_LINK":("void *const volatile *",0x20074610,"runtime_sram_data"),
 "OPEN_CFW_PT_UART_MUTEX_LINK":("void *const volatile *",0x20074620,"runtime_sram_data"),
 "OPEN_CFW_PT_UART_SEMAPHORE_LINK":("void *const volatile *",0x2007461C,"runtime_sram_data"),
 "OPEN_CFW_PT_UART_ERROR_FLAG":("volatile uint8_t *",0x20074FCA,"runtime_sram_data"),
 "OPEN_CFW_PT_UART_TX_BUFFER":("uint8_t *",0x20379DA0,"runtime_sram_data"),
 "OPEN_CFW_PT_UART_CACHE_CLEAN_REGISTER":("volatile uint32_t *",0xE000EF68,"peripheral_mmio"),
 "OPEN_CFW_PT_UART_REGISTER_BASE":(
  "volatile uint32_t *",0x40039000,"peripheral_mmio"),
 "OPEN_CFW_PT_SYSTEM_RESET_CONTROL":("volatile uint32_t *",0xE000ED0C,"peripheral_mmio"),
 "OPEN_CFW_PT_DISPLAY_POSTPROCESS_PATH":("const void *",0x0076F518,"immutable_flash_data"),
 "OPEN_CFW_PT_DISPLAY_POSTPROCESS_READY":("const volatile uint8_t *",0x20074F2C,"runtime_sram_data"),
 "OPEN_CFW_PT_DISPLAY_POSTPROCESS_ACTIVE":("const volatile uint32_t *",0x200744E0,"runtime_sram_data"),
 "OPEN_CFW_PT_DISPLAY_POSTPROCESS_PRIMARY":("const volatile uint32_t *",0x200744D8,"runtime_sram_data"),
 "OPEN_CFW_PT_DISPLAY_POSTPROCESS_MODE":("const volatile uint32_t *",0x200744DC,"runtime_sram_data"),
 "OPEN_CFW_PT_FONT_0_BASE":("uint32_t address constant",0x80100000,"external_xip_data"),
 "OPEN_CFW_PT_FONT_1_BASE":("uint32_t address constant",0x80700000,"external_xip_data"),
 "OPEN_CFW_PT_FONT_XIP_START":("uint32_t address constant",0x80000000,"external_xip_bound"),
 "OPEN_CFW_PT_FONT_XIP_END":("uint32_t address constant",0x82000000,"external_xip_bound"),
 "OPEN_CFW_PT_DISPLAY_STATE":("const uint8_t *",0x20074F2C,"runtime_sram_data"),
 "OPEN_CFW_PT_CODEC_IDENTIFIER_WORD":("const volatile uint32_t *",0x20074224,"runtime_sram_data"),
 "OPEN_CFW_PT_BUZZER_ROUTE_WORD":("const volatile uint32_t *",0x20000724,"runtime_sram_data"),
 "OPEN_CFW_PT_BUZZER_PIN_CONFIGURATION":(
  "const volatile uint32_t *",0x0078EE48,"immutable_flash_data"),
 "OPEN_CFW_PT_BUZZER_TIMER_LINK":(
  "void *const volatile *",0x20074504,"runtime_sram_data"),
 "OPEN_CFW_PT_BUZZER_SCRIPT_STATE":(
  "volatile uint32_t *",0x20074500,"runtime_sram_data"),
 "OPEN_CFW_PT_BUZZER_ACTIVE_FLAG":(
  "volatile uint8_t *",0x20074FB5,"runtime_sram_data"),
 "OPEN_CFW_PT_BUZZER_PENDING_FLAG":(
  "volatile uint8_t *",0x20074FB4,"runtime_sram_data"),
 "OPEN_CFW_PT_HARDWARE_IDENTIFIER_1_STATE":("const volatile uint32_t *",0x20074544,"runtime_sram_data"),
 "OPEN_CFW_PT_HARDWARE_IDENTIFIER_2_DEVICE":("const void *",0x20074068,"runtime_sram_data"),
 "OPEN_CFW_PT_CHARGER_DEVICE":("const void *",0x20070F78,"runtime_sram_data"),
 "OPEN_CFW_PT_AUDIO_STATUS_BASE":("const uint8_t *",0x20074368,"runtime_sram_data"),
 "OPEN_CFW_PT_AUDIO_CAPTURE_ACTIVE":("volatile uint32_t *",0x20074890,"runtime_sram_data"),
 "OPEN_CFW_PT_AUDIO_SINGLE_CALLBACK":("const void *",0x0058F5E1,"retained_callback_entry"),
 "OPEN_CFW_PT_AUDIO_STEREO_CALLBACK":("const void *",0x0058F4E5,"retained_callback_entry"),
 "OPEN_CFW_PT_AUDIO_CODEC_BUFFER_0":("void *",0x20106A7C,"runtime_sram_data"),
 "OPEN_CFW_PT_AUDIO_CODEC_BUFFER_1":("void *",0x201074C0,"runtime_sram_data"),
 "OPEN_CFW_PT_AUDIO_PDM_BUFFER":("void *",0x20107F04,"runtime_sram_data"),
 "OPEN_CFW_PT_DISPLAY_STAGE_1_WORD":("volatile uint32_t *",0x2000064C,"runtime_sram_data"),
 "OPEN_CFW_PT_DISPLAY_STAGE_3_WORD":("volatile uint32_t *",0x20000648,"runtime_sram_data"),
 "OPEN_CFW_PT_DISPLAY_STAGE_2_FIRST_WORD":("volatile uint32_t *",0x20000650,"runtime_sram_data"),
 "OPEN_CFW_PT_DISPLAY_STAGE_2_SECOND_WORD":("volatile uint32_t *",0x200744C8,"runtime_sram_data"),
 "OPEN_CFW_PT_ULED_OPERATIONS_LINK":("const struct open_cfw_pt_uled_operations *const volatile *",0x20074530,"runtime_sram_data"),
 "OPEN_CFW_PT_DISPLAY_MUTEX_LINK":("void *const volatile *",0x200744E8,"runtime_sram_data"),
 "OPEN_CFW_PT_DISPLAY_QUEUE_LINK":("void *const volatile *",0x200744E4,"runtime_sram_data"),
 "OPEN_CFW_PT_DISPLAY_BUFFER":("open_cfw_pt_display_buffer_descriptor *",0x20073B60,"runtime_sram_data"),
 "OPEN_CFW_PT_LENS_SYNC_QUEUE_LINK":("void *const volatile *",0x200749CC,"runtime_sram_data"),
 "OPEN_CFW_PT_LENS_SYNC_EVENT_LINK":("void *const volatile *",0x20074B10,"runtime_sram_data"),
 "OPEN_CFW_PT_AUDIO_PATH_TABLE":("const uint8_t *",0x20073C08,"runtime_sram_data"),
 "OPEN_CFW_PT_TIME_CONFIGURATION_LINK":("const uint8_t *const volatile *",0x200036FC,"runtime_sram_data"),
 "OPEN_CFW_PT_TIME_FORMAT_WORD":("const volatile uint32_t *",0x200736EC,"runtime_sram_data"),
 "OPEN_CFW_PT_INPUT_THREAD_LINK":("void *const volatile *",0x20004094,"runtime_sram_data"),
 "OPEN_CFW_PT_INPUT_QUEUE_LINK":("void *const volatile *",0x20004098,"runtime_sram_data"),
 "OPEN_CFW_PT_AUDIO_THREAD_LINK":("void *const volatile *",0x20003FA0,"runtime_sram_data"),
 "OPEN_CFW_PT_AUDIO_QUEUE_LINK":("void *const volatile *",0x20003FA4,"runtime_sram_data"),
 "OPEN_CFW_PT_AUDIO_NAME_TABLE":("const char *const volatile *",0x200036D0,"runtime_sram_data"),
 "OPEN_CFW_PT_AUDIO_REGISTRATION_TABLE":("volatile struct open_cfw_pt_audio_registration *",0x20073C20,"runtime_sram_data"),
 "OPEN_CFW_PT_AUDIO_RECORDER_TABLE":("volatile struct open_cfw_pt_audio_recorder *",0x20073C08,"runtime_sram_data"),
 "OPEN_CFW_PT_FONT_XIP_CONFIGURATION_FLAG":("const volatile uint8_t *",0x20074FB8,"runtime_sram_data"),
 "OPEN_CFW_PT_FONT_XIP_ACTIVE":("volatile uint8_t *",0x20074FB9,"runtime_sram_data"),
 "OPEN_CFW_PT_FONT_XIP_MUTEX_LINK":("void *const volatile *",0x20074548,"runtime_sram_data"),
 "OPEN_CFW_PT_FONT_XIP_DEVICE_LINK":("void *const volatile *",0x20074544,"runtime_sram_data"),
 "OPEN_CFW_PT_PAIRING_FLAG_0":("volatile uint8_t *",0x20071A34,"runtime_sram_data"),
 "OPEN_CFW_PT_PAIRING_WORD":("volatile uint32_t *",0x20071A38,"runtime_sram_data"),
 "OPEN_CFW_PT_PAIRING_FLAG_1":("volatile uint8_t *",0x20071A3C,"runtime_sram_data"),
 "OPEN_CFW_PT_AMBIENT_ROUTE_WORD":("const volatile uint32_t *",0x0078EE40,"immutable_flash_data"),
 "OPEN_CFW_PT_AMBIENT_INIT_REGISTER":("volatile uint32_t *",0x4001044C,"peripheral_mmio"),
 "OPEN_CFW_PT_AMBIENT_RESET_REGISTER":("volatile uint32_t *",0x40010468,"peripheral_mmio"),
}

# The production table is an ABI, not an address bag.  Pinning the field and
# cast together prevents a field swap or width/signature drift from passing
# merely because the same set of Apollo entry addresses remains present.
BOARD_FUNCTION_BINDINGS={
 "set_local_lid":("void (*)(uint8_t)",0x004AC744),
 "set_local_level":("void (*)(uint8_t)",0x004AC718),
 "set_local_charging":("void (*)(uint8_t)",0x004AC72E),
 "codec_mic_delay_1bit":("int32_t (*)(void)",0x0057D870),
 "system_data_write":("int (*)(uint8_t, const void *)",0x004AF11C),
 "system_data_get":("void *(*)(uint8_t)",0x004AF73A),
 "system_data_read":("void *(*)(uint8_t)",0x004AF7B8),
 "post_input_message_id3":("void (*)(void)",0x005130A6),
 "product_mode_read":("uint8_t (*)(void)",0x004ABE8C),
 "product_mode_update":("void (*)(uint8_t)",0x004ABE66),
 "touch_proximity":("uint8_t (*)(void)",0x00502DAE),
 "touch_read_differences":("int32_t (*)(uint8_t [10])",0x0055B6A8),
 "psn_write_otp":("int (*)(const char *)",0x004AFFC0),
 "memory_compare":("int (*)(const void *, const void *, unsigned int)",0x004751C8),
 "sensor_calibration_update":("void (*)(const float *, const float *, const float [9])",0x0050999E),
 "buzzer_start":("void (*)(uint32_t, uint8_t)",0x00502C88),
 "buzzer_stop":("void (*)(void)",0x00502D4C),
 "buzzer_frequency_get":("uint32_t (*)(void)",0x0058FA60),
 "buzzer_duty_get":("uint8_t (*)(void)",0x0058FA66),
 "buzzer_update":("void (*)(uint32_t, uint8_t)",0x0058FA6C),
 "onboarding_update":("int (*)(uint8_t, const uint8_t *)",0x004A7820),
 "production_reset":("void (*)(void)",0x0058F950),
 "charger_test_disable":("void (*)(void)",0x005128F8),
 "charger_test_enable":("void (*)(void)",0x0051299C),
 "font_version":("const char *(*)(void)",0x0046D584),
 "imu_latest_sample":("const float *(*)(void)",0x004A5B90),
 "sensor_calibration_initialize":("void (*)(void)",0x004A6BCE),
 "sensor_calibration_read":("int (*)(float [3], float [3], float [9])",0x005099F8),
 "imu_orientation":("const float *(*)(void)",0x004A5D38),
 "codec_platform_identifier":("uint32_t (*)(void)",0x0052DEE6),
 "file_open":("void *(*)(const void *, const char *)",0x00474550),
 "file_close":("int (*)(void *)",0x004745F4),
 "file_read":("unsigned int (*)(void *, unsigned int, unsigned int, void *)",0x00474634),
 "file_write":("unsigned int (*)(const void *, unsigned int, unsigned int, void *)",0x00474682),
 "file_seek":("int (*)(void *, int, unsigned int)",0x00474814),
 "file_tell":("int (*)(void *)",0x00474870),
 "file_size":("int (*)(void *)",0x004748B4),
 "file_remove":("int (*)(const void *)",0x0047498C),
 "tick_count":("uint32_t (*)(void)",0x00454EFE),
 "ota_set_interface":("void (*)(uint32_t, uint32_t, void *, uint32_t)",0x004487E4),
 "ota_frame_dispatch":("int (*)(uint8_t, const uint8_t *, uint16_t)",0x00448670),
 "thread_get_id":("void *(*)(void)",0x004491AA),
 "thread_set_priority":("int (*)(void *, int)",0x004491B2),
 "hardware_identifier_0":("int (*)(uint32_t *)",0x00512C84),
 "hardware_identifier_1":("int (*)(uint32_t *)",0x004700B4),
 "hardware_identifier_2":("int (*)(uint32_t *)",0x00512B20),
 "imu_who_am_i":("int (*)(uint32_t *)",0x004A6456),
 "mag_who_am_i":("int (*)(uint32_t *)",0x004A64C8),
 "display_hardware_identifier":("uint32_t (*)(void)",0x004CA070),
 "ambient_identifier_initialize":("void (*)(void)",0x0058F936),
 "ambient_identifier_assign":("void (*)(void *)",0x005135E0),
 "ambient_identifier_step_1":("void (*)(void *)",0x0058F8CC),
 "ambient_identifier_step_2":("void (*)(void *)",0x0058F8D8),
 "ambient_identifier_low":("uint16_t (*)(void *)",0x0058F922),
 "ambient_identifier_high":("uint16_t (*)(void *)",0x0058F92C),
 "uart_sync_write":("int (*)(const uint8_t *, uint32_t, uint32_t)",0x00541790),
 "delay_ticks":("int (*)(uint32_t)",0x00449376),
 "lens_side":("uint8_t (*)(void)",0x0045A568),
 "lens_sync_send":("int (*)(uint32_t, const void *, uint32_t, uint32_t)",0x004651E0),
 "screen_show":("void (*)(uint16_t, uint32_t, uint32_t)",0x004441EC),
 "screen_hide":("void (*)(uint16_t, uint32_t, uint32_t)",0x004443CC),
 "display_state":("const uint8_t *(*)(void)",0x0044347A),
 "display_brightness":("void (*)(uint32_t, uint32_t, uint32_t)",0x004CA1EE),
 "display_stage_1":("void (*)(uint32_t)",0x0046C984),
 "display_stage_2":("void (*)(uint32_t, uint32_t)",0x0046C9DC),
 "display_stage_3":("void (*)(uint32_t)",0x0046C9AA),
 "display_offset":("void (*)(uint8_t, uint8_t)",0x004CA24A),
 "audio_status_get":("const uint8_t *(*)(uint32_t)",0x0050938E),
 "audio_path_format":("void (*)(uint8_t, char *, uint32_t)",0x0057B352),
 "audio_channel_0_start":("void (*)(uint8_t)",0x0058F69A),
 "audio_channel_0_stop":("void (*)(void)",0x0058F7B0),
 "audio_channel_1_start":("void (*)(void)",0x0058F74A),
 "audio_channel_1_stop":("void (*)(void)",0x0058F806),
 "audio_codec_route":("void (*)(uint32_t, uint32_t)",0x0053A5BE),
 "system_data_reset_aging":("void (*)(void)",0x004AFC10),
 "time_configure":("void (*)(uint32_t, int)",0x0044A1FE),
 "time_capture":("void (*)(void *)",0x0044A19A),
 "ambient_read":("double (*)(void)",0x0058F8E4),
 "system_reset":("void (*)(void)",0x0044B0AE),
 "box_state_updated":("void (*)(void)",0x004AC798),
 "display_postprocess":("void (*)(void)",0x00542D4C),
 "font_crc_check_0":("uint8_t (*)(void)",0x0058F486),
 "font_crc_check_1":("uint8_t (*)(void)",0x0058F490),
}

# Each retained data entry records its exact C type, Apollo address, and the
# minimum byte extent touched by the reconstructed behavior.  Entries ending
# in [n] are the four elements of storage_required_paths.
BOARD_DATA_BINDINGS={
 "identifier_record_link":("const uint8_t *const *",0x20003844,4),
 "sync_ready":("volatile uint8_t *",0x20075003,1),
 "boolean_flag":("const uint8_t *",0x20075019,1),
 "pair_state":("const uint8_t *",0x20073B18,0x2E),
 "pair_state_mutable":("volatile uint8_t *",0x20073B18,0x2E),
 "session_record":("const uint8_t *",0x20003994,0xAC),
 "session_record_mutable":("uint8_t *",0x20003994,0xAC),
 "diagnostic_blob_36":("const uint8_t *",0x2000396C,36),
 "display_value":("const uint8_t *",0x20004552,1),
 "display_value_mutable":("volatile uint8_t *",0x20004552,1),
 "display_runtime_flag":("volatile uint8_t *",0x20004551,1),
 "aging_mode":("const uint8_t *",0x20075019,1),
 "aging_mode_mutable":("volatile uint8_t *",0x20075019,1),
 "calibration_reference_matrix":("const float *",0x00758E08,36),
 "touch_platform_identifier":("const uint32_t *",0x20074508,4),
 "apollo_platform_identifier":("const uint32_t *",0x20074940,4),
 "payload_path":("const char *",0x00782BF0,18),
 "file_read_mode":("const char *",0x00575E78,2),
 "file_write_mode":("const char *",0x0057301C,2),
 "storage_test_path":("const char *",0x0078BD20,11),
 "storage_required_paths[0]":("const char *",0x007705F0,25),
 "storage_required_paths[1]":("const char *",0x00782BF0,18),
 "storage_required_paths[2]":("const char *",0x00782C04,20),
 "storage_required_paths[3]":("const char *",0x00782C18,20),
 "cleanup_paths[0]":("const char *",0x00770430,25),
 "cleanup_paths[1]":("const char *",0x0077AC9C,22),
 "cleanup_paths[2]":("const char *",0x0077ACB4,23),
 "metadata_word":("volatile uint32_t *",0x200748E8,4),
 "payload_handle_slot":("void *volatile *",0x200748E4,4),
 "payload_active":("volatile uint8_t *",0x20075009,1),
 "payload_open_seconds":("volatile uint32_t *",0x200748EC,4),
 "ota_stock_sequence":("volatile uint8_t *",0x20075005,1),
 "ota_stock_initialized":("volatile uint8_t *",0x2007500A,1),
 "ota_stock_staging_length":("volatile uint32_t *",0x200748DC,4),
 "ota_async_data":("uint8_t *",0x20059EF8,6000),
 "ota_async_length":("volatile uint32_t *",0x200748E0,4),
 "ota_async_ready":("volatile uint8_t *",0x20075008,1),
 "ota_status":("const uint8_t *",0x20075007,1),
 "uart_sync_state":("volatile uint8_t *",0x20074080,8),
 "uart_sync_expected":("const uint8_t *",0x0078E44C,7),
 "lens_sync_ready":("volatile uint8_t *",0x20075004,1),
 "lens_sync_template_12":("const uint8_t *",0x0078BD68,12),
 "firmware_version":("const char *",0x0078BD44,9),
 "audio_channel_0_template_12":("const uint8_t *",0x0078BD50,12),
 "audio_channel_1_template_12":("const uint8_t *",0x0078BD5C,12),
 "audio_handle_slot":("void *volatile *",0x200748D0,4),
 "audio_active":("volatile uint8_t *",0x20075006,1),
 "audio_length_state":("volatile uint32_t *",0x200748D4,4),
 "audio_offset_state":("volatile uint32_t *",0x200748D8,4),
 "audio_path_state_32":("uint8_t *",0x2007393C,32),
 "time_configuration":("const uint8_t *",0x2000380C,9),
 "ambient_baseline":("volatile uint32_t *",0x200748C8,4),
 "ambient_secondary":("volatile uint32_t *",0x200748C4,4),
}
BOARD_IMMUTABLE_FLASH_DATA_FIELDS={
 "calibration_reference_matrix", "payload_path", "file_read_mode",
 "file_write_mode", "storage_test_path", "storage_required_paths[0]",
 "storage_required_paths[1]", "storage_required_paths[2]",
 "storage_required_paths[3]", "uart_sync_expected", "lens_sync_template_12",
 "cleanup_paths[0]", "cleanup_paths[1]", "cleanup_paths[2]",
 "firmware_version", "audio_channel_0_template_12",
 "audio_channel_1_template_12",
}
BOARD_RUNTIME_SRAM_DATA_FIELDS=set(BOARD_DATA_BINDINGS)-BOARD_IMMUTABLE_FLASH_DATA_FIELDS

def sha(data:bytes)->str:return hashlib.sha256(data).hexdigest()
def component_slice(data:bytes,start:int,size:int)->bytes:
 offset=OFFICIAL_PREAMBLE_BYTES+start-OFFICIAL_RUN_BASE
 if offset<0 or offset+size>len(data):
  raise RuntimeError(f"PT authenticated component slice is out of range: {start:#x}")
 return data[offset:offset+size]
def decode_thumb_bl(address:int,encoded:bytes)->int|None:
 if len(encoded)!=4:return None
 first,second=struct.unpack("<HH",encoded)
 if first&0xF800!=0xF000 or second&0xD000!=0xD000:return None
 sign=(first>>10)&1
 i1=1^((second>>13)&1)^sign
 i2=1^((second>>11)&1)^sign
 immediate=((sign<<24)|(i1<<23)|(i2<<22)|
            ((first&0x3FF)<<12)|((second&0x7FF)<<1))
 if immediate&(1<<24):immediate-=1<<25
 return address+4+immediate
def elf_section_totals(path:Path)->dict[str,int]:
 data=path.read_bytes()
 if len(data)<52 or data[:6]!=b"\x7fELF\x01\x01":
  raise RuntimeError("PT target link is not ELF32 little-endian")
 section_offset=struct.unpack_from("<I",data,0x20)[0]
 entry_size,count,names_index=struct.unpack_from("<HHH",data,0x2E)
 if entry_size!=40 or count<1 or names_index>=count:
  raise RuntimeError("PT target link section table changed")
 sections=[struct.unpack_from("<IIIIIIIIII",data,section_offset+i*entry_size)
  for i in range(count)]
 names_section=sections[names_index]
 names=data[names_section[4]:names_section[4]+names_section[5]]
 totals={"text":0,"rodata":0,"data":0,"bss":0}
 loadable_ranges=[]
 for section in sections:
  offset=section[0]
  end=names.find(b"\0",offset)
  if offset>=len(names) or end<0:raise RuntimeError("PT ELF section name changed")
  name=names[offset:end].decode("ascii")
  for kind in totals:
   if (name=="."+kind or name.startswith("."+kind+".") or
       (kind=="text" and name.startswith(".pt_legacy_"))):
    totals[kind]+=section[5]
    if kind in ("text","rodata","data") and section[5]:
     loadable_ranges.append((section[3],section[3]+section[5]))
    break
 totals["loadable"]=totals["text"]+totals["rodata"]+totals["data"]
 totals["loadable_start"]=min((start for start,_ in loadable_ranges),default=0)
 totals["loadable_end_exclusive"]=max((end for _,end in loadable_ranges),default=0)
 return totals
def elf_virtual_range(path:Path,start:int,end:int)->bytes:
 data=path.read_bytes()
 if end<start or len(data)<52 or data[:6]!=b"\x7fELF\x01\x01":
  raise RuntimeError("PT target byte gate requires ELF32 little-endian")
 section_offset=struct.unpack_from("<I",data,0x20)[0]
 entry_size,count=struct.unpack_from("<HH",data,0x2E)[:2]
 if entry_size!=40 or count<1:
  raise RuntimeError("PT target byte gate section table changed")
 for index in range(count):
  section=struct.unpack_from(
   "<IIIIIIIIII",data,section_offset+index*entry_size)
  section_type,address,offset,size=section[1],section[3],section[4],section[5]
  if section_type!=8 and address<=start and end<=address+size:
   begin=offset+start-address
   return data[begin:begin+end-start]
 raise RuntimeError(f"PT target byte range is not loadable: {start:#x}..{end:#x}")
def normalized_c_type(value:str)->str:return " ".join(value.split())
def validate_lc3_license_boundary(apache_source:str,mit_leaf_source:str)->None:
 required=(
  "SPDX-License-Identifier: Apache-2.0",
  LC3_SETUP_EVIDENCE["upstream_copyright"],
  LC3_SETUP_EVIDENCE["upstream_source"],
  LC3_SETUP_EVIDENCE["upstream_commit"],
  LC3_SETUP_EVIDENCE["upstream_license_path"],
  "open_cfw_pt_lc3_setup_encoder",
 )
 if (apache_source.count(required[0])!=1 or
     any(marker not in apache_source for marker in required[1:]) or
     "SPDX-License-Identifier: MIT" in apache_source or
     mit_leaf_source.count("SPDX-License-Identifier: MIT")!=1 or
     "SPDX-License-Identifier: Apache-2.0" in mit_leaf_source or
     re.search(
      r"^[A-Za-z_][^\n]*\bopen_cfw_pt_lc3_setup_encoder\s*\([^;{}]*\)\s*\{",
      mit_leaf_source,re.M) is not None):
  raise RuntimeError("PT LC3 source license/provenance boundary changed")
def authenticated_decomp_block(text:str,address:int)->str:
 marker=f"/* FUN 0x{address:08x} "
 try:
  start=text.index(marker)
  end=text.index("\n/* FUN 0x",start+1)
 except ValueError as exc:
  raise RuntimeError(
   f"authenticated decompilation block missing: {address:#010x}") from exc
 return text[start:end]
def require_tool(environment:str,*names:str)->str:
 configured=os.environ.get(environment)
 if configured:
  path=shutil.which(configured) if "/" not in configured else configured
  if path and Path(path).is_file():return path
 for name in names:
  path=shutil.which(name)
  if path:return path
 raise RuntimeError(f"required tool is unavailable: {environment} ({', '.join(names)})")
def verify_corpus()->tuple[list[dict[str,str]],list[dict]]:
 for name,digest in CORPUS_DIGESTS.items():
  if sha((CORPUS/name).read_bytes())!=digest:raise RuntimeError(f"PT corpus changed: {name}")
 ledger={line.split("  ",1)[1]:line.split("  ",1)[0] for line in (CORPUS/"SHA256SUMS").read_text().splitlines()}
 if ledger!=CORPUS_DIGESTS:raise RuntimeError("PT corpus SHA256SUMS ledger changed")
 with (CORPUS/"command-map.tsv").open(newline="") as f:commands=list(csv.DictReader(f,delimiter="\t"))
 functions=[json.loads(line) for line in (CORPUS/"functions.jsonl").read_text().splitlines()]
 if len(functions)!=73 or len(commands)!=66:raise RuntimeError("PT corpus surface changed")
 if sum(int(item["stock_end_exclusive"],0)-int(item["stock_start"],0) for item in functions)!=STOCK_BODY_BYTES:raise RuntimeError("PT stock byte accounting changed")
 by_command={int(item["command"],0):item for item in functions if item["command"] is not None}
 if len(by_command)!=66:raise RuntimeError("PT corpus command ownership changed")
 for row in commands:
  command=int(row["command"],0);item=by_command.get(command)
  if item is None or item["stock_start"]!=row["handler_stock_start"] or item["decompilation_sha256"]!=row["decompilation_sha256"]:raise RuntimeError(f"PT corpus command row changed: 0x{command:02X}")
 return commands,functions
def analyze(*,enforce_canonical_pin:bool=True)->dict:
 rows,functions=verify_corpus()
 stock_boundary=stock_pt.analyze()
 external_entries=stock_boundary["surface"]["external_direct_bl_entries"]
 if external_entries!=[
  {"callsite":"0x00538716","target":"0x0056F4A0"},
  {"callsite":"0x0053A218","target":"0x0056F4A0"},
  {"callsite":"0x0053A356","target":"0x0056F92C"}]:
  raise RuntimeError("PT external entry topology changed")
 expected={int(r["command"],0) for r in rows}
 found=[]
 for path in HANDLERS:
  found.extend((int(c,16),path.name) for c in re.findall(r"\{0x([0-9A-Fa-f]{2})U,\s*[A-Za-z_]",path.read_text()))
 counts={c:sum(x==c for x,_ in found) for c in expected|{x for x,_ in found}}
 duplicate=sorted(c for c,n in counts.items() if n>1);missing=sorted(expected-{x for x,_ in found});extra=sorted({x for x,_ in found}-expected)
 if len(rows)!=66 or duplicate or missing or extra:raise RuntimeError(f"binding closure failed: duplicate={duplicate}, missing={missing}, extra={extra}")
 owned=SOURCES+HEADERS
 for path in owned:
  text=path.read_text()
  expected_spdx=("Apache-2.0" if path==LC3_SETUP_SOURCE else "MIT")
  if (text.count(f"SPDX-License-Identifier: {expected_spdx}")!=1 or
      (path==LC3_SETUP_SOURCE and "SPDX-License-Identifier: MIT" in text) or
      (path!=LC3_SETUP_SOURCE and
       "SPDX-License-Identifier: Apache-2.0" in text)):
   raise RuntimeError(f"PT source license marker changed: {path.name}")
  if re.search(r"\.(?:byte|short|hword|word|inst)\b|__asm\b|(?<![0-9A-Fa-f])[0-9A-Fa-f]{256,}(?![0-9A-Fa-f])",text):raise RuntimeError(f"PT source contains a raw executable encoding: {path.name}")
 owned_digest=sha(b"".join(path.name.encode()+b"\0"+path.read_bytes() for path in owned))
 official=OFFICIAL_COMPONENT.read_bytes()
 if (len(official)!=OFFICIAL_COMPONENT_SIZE or
     sha(official)!=OFFICIAL_COMPONENT_SHA256):
  raise RuntimeError("PT authenticated official component changed")
 lens_wrapper=component_slice(
  official,LENS_SYNC_TRANSPORT_EVIDENCE["stock_wrapper_runtime_address"],
  LENS_SYNC_TRANSPORT_EVIDENCE["stock_wrapper_size"])
 lens_transport=component_slice(
 official,LENS_SYNC_TRANSPORT_EVIDENCE["stock_transport_runtime_address"],
  LENS_SYNC_TRANSPORT_EVIDENCE["stock_transport_size"])
 decomp_index_bytes=AUTHENTICATED_DECOMP_INDEX.read_bytes()
 if sha(decomp_index_bytes)!=AUTHENTICATED_DECOMP_INDEX_SHA256:
  raise RuntimeError("PT authenticated decompilation index changed")
 decomp_records={item["entry"]:item for item in (
  json.loads(line) for line in decomp_index_bytes.decode().splitlines())}
 lens_wrapper_record=decomp_records.get("00464c36")
 lens_transport_record=decomp_records.get("00464772")
 lens_wrapper_decomp=authenticated_decomp_block(
  AUTHENTICATED_DECOMP_BUNDLE.read_text(),
  LENS_SYNC_TRANSPORT_EVIDENCE["stock_wrapper_runtime_address"])
 lens_callsite=LENS_SYNC_TRANSPORT_EVIDENCE[
  "stock_wrapper_transport_callsite"]
 lens_sync_transport_authenticated=(
  sha(lens_wrapper)==LENS_SYNC_TRANSPORT_EVIDENCE["stock_wrapper_sha256"] and
  sha(lens_transport)==LENS_SYNC_TRANSPORT_EVIDENCE[
   "stock_transport_sha256"] and
  decode_thumb_bl(lens_callsite,component_slice(official,lens_callsite,4))==
   LENS_SYNC_TRANSPORT_EVIDENCE["stock_transport_runtime_address"] and
  lens_wrapper_record is not None and lens_transport_record is not None and
  lens_wrapper_record["body_bytes"]==
   LENS_SYNC_TRANSPORT_EVIDENCE["stock_wrapper_size"] and
  lens_wrapper_record["body_sha256"]==
   LENS_SYNC_TRANSPORT_EVIDENCE["stock_wrapper_sha256"] and
  lens_wrapper_record["signature"]==
   LENS_SYNC_TRANSPORT_EVIDENCE["stock_wrapper_signature"] and
  lens_wrapper_record["callees"]==[
   "0043ce9e","0043d0ce","0043d574","00464772"] and
  lens_transport_record["body_bytes"]==
   LENS_SYNC_TRANSPORT_EVIDENCE["stock_transport_size"] and
  lens_transport_record["body_sha256"]==
   LENS_SYNC_TRANSPORT_EVIDENCE["stock_transport_sha256"] and
  lens_transport_record["signature"]==
   LENS_SYNC_TRANSPORT_EVIDENCE["stock_transport_signature"] and
  sha(lens_wrapper_decomp.encode())==LENS_SYNC_TRANSPORT_EVIDENCE[
   "stock_wrapper_decompilation_sha256"] and
  LENS_SYNC_TRANSPORT_EVIDENCE["stock_wrapper_call_expression"] in
   lens_wrapper_decomp)
 if not lens_sync_transport_authenticated:
  raise RuntimeError("PT stock postprocess lens-sync transport evidence changed")
 lc3_primary=component_slice(
  official,LC3_SETUP_EVIDENCE["stock_primary_runtime_address"],
  LC3_SETUP_EVIDENCE["stock_primary_size"])
 lc3_setup=component_slice(
  official,LC3_SETUP_EVIDENCE["stock_runtime_address"],
  LC3_SETUP_EVIDENCE["stock_size"])
 lc3_service_setup=component_slice(
  official,LC3_SETUP_EVIDENCE["stock_service_setup_runtime_address"],
  LC3_SETUP_EVIDENCE["stock_service_setup_size"])
 lc3_context_table=component_slice(
  official,LC3_SETUP_EVIDENCE["stock_context_pointer_table_runtime_address"],
  LC3_SETUP_EVIDENCE["stock_context_pointer_table_size"])
 lc3_primary_record=decomp_records.get("0059123a")
 lc3_wrapper_record=decomp_records.get("00591374")
 lc3_service_record=decomp_records.get("0057a926")
 lc3_context_values=struct.unpack("<IIII",lc3_context_table)
 fixed_context_starts=LC3_SETUP_EVIDENCE["fixed_context_starts"]
 lc3_slot_layout_authenticated=(
  sha(lc3_context_table)==LC3_SETUP_EVIDENCE[
   "stock_context_pointer_table_sha256"] and
  list(lc3_context_values[index] for index in (0,1,3))==
   fixed_context_starts[:3] and
  all(struct.unpack("<I",component_slice(official,address,4))[0]==
      fixed_context_starts[3]
      for address in LC3_SETUP_EVIDENCE["stock_next_context_literal_cells"]) and
  struct.unpack("<I",component_slice(
   official,LC3_SETUP_EVIDENCE["stock_next_slot_literal_cell"],4))[0]==
   LC3_SETUP_EVIDENCE["next_allocation_start"] and
  all(right-left==LC3_SETUP_EVIDENCE["fixed_context_slot_bytes"]
      for left,right in zip(
       fixed_context_starts,
       fixed_context_starts[1:]+[LC3_SETUP_EVIDENCE["next_allocation_start"]])) and
  LC3_SETUP_EVIDENCE["fixed_context_slot_bytes"]-
   LC3_SETUP_EVIDENCE["fixed_context_header_bytes"]==
   LC3_SETUP_EVIDENCE["fixed_context_storage_bytes"])
 lc3_license=ROOT/"third_party/liblc3/LICENSE"
 lc3_adaptation=LC3_SETUP_SOURCE.read_text()
 lc3_setup_boundary_authenticated=(
  sha(lc3_primary)==LC3_SETUP_EVIDENCE["stock_primary_sha256"] and
  sha(lc3_setup)==LC3_SETUP_EVIDENCE["stock_sha256"] and
  sha(lc3_service_setup)==LC3_SETUP_EVIDENCE[
   "stock_service_setup_sha256"] and
  decode_thumb_bl(
   LC3_SETUP_EVIDENCE["stock_wrapper_primary_callsite"],component_slice(
    official,LC3_SETUP_EVIDENCE["stock_wrapper_primary_callsite"],4))==
   LC3_SETUP_EVIDENCE["stock_primary_runtime_address"] and
  all(decode_thumb_bl(callsite,component_slice(official,callsite,4))==
      LC3_SETUP_EVIDENCE["stock_service_setup_runtime_address"]
      for callsite in LC3_SETUP_EVIDENCE["stock_service_setup_callsites"]) and
  lc3_primary_record is not None and lc3_wrapper_record is not None and
  lc3_service_record is not None and
  lc3_primary_record["body_bytes"]==LC3_SETUP_EVIDENCE[
   "stock_primary_size"] and
  lc3_primary_record["body_sha256"]==LC3_SETUP_EVIDENCE[
   "stock_primary_sha256"] and
  lc3_primary_record["callees"]==[
   "00439c04","0048949c","004d4ccc","00590d3c","00590d74"] and
  lc3_wrapper_record["body_bytes"]==LC3_SETUP_EVIDENCE["stock_size"] and
  lc3_wrapper_record["body_sha256"]==LC3_SETUP_EVIDENCE["stock_sha256"] and
  lc3_wrapper_record["callees"]==["0059123a"] and
  lc3_service_record["body_bytes"]==LC3_SETUP_EVIDENCE[
   "stock_service_setup_size"] and
  lc3_service_record["body_sha256"]==LC3_SETUP_EVIDENCE[
   "stock_service_setup_sha256"] and
  lc3_service_record["callees"]==["00591374"] and
  lc3_slot_layout_authenticated and
  sha(lc3_license.read_bytes())==LC3_SETUP_EVIDENCE[
   "upstream_license_sha256"] and
  lc3_adaptation.count("SPDX-License-Identifier: Apache-2.0")==1 and
  LC3_SETUP_EVIDENCE["upstream_copyright"] in lc3_adaptation and
  LC3_SETUP_EVIDENCE["upstream_source"] in lc3_adaptation and
  LC3_SETUP_EVIDENCE["upstream_commit"] in lc3_adaptation and
  LC3_SETUP_EVIDENCE["upstream_license_path"] in lc3_adaptation)
 if not lc3_setup_boundary_authenticated:
  raise RuntimeError("PT retained Apache liblc3 setup boundary changed")
 adapter_header=(COMPONENT/"pt_protocol_platform_adapter.h").read_text()
 adapter_source=(COMPONENT/"pt_protocol_platform_adapter.c").read_text()
 board_source=(COMPONENT/"pt_protocol_board_backend.c").read_text()
 board_header=(COMPONENT/"pt_protocol_board_backend.h").read_text()
 board_fixture=(ROOT/"tests/fixtures/pt_protocol_board_backend_host.c").read_text()
 operations=set(re.findall(r"OPEN_CFW_PT_OP_[A-Z0-9_]+",adapter_header))-{"OPEN_CFW_PT_OP_COUNT"}
 forwarded_operations=re.findall(r"OPEN_CFW_PT_OP_[A-Z0-9_]+",adapter_source)
 handler_operations=operations-{"OPEN_CFW_PT_OP_POST_RESPONSE"}
 if (len(operations)!=56 or len(forwarded_operations)!=55 or
     set(forwarded_operations)!=handler_operations):
  raise RuntimeError("PT platform operation forwarding surface changed")
 board_operations=set(re.findall(r"case\s+(OPEN_CFW_PT_OP_[A-Z0-9_]+)\s*:",board_source))
 board_callbacks=set(re.findall(r"\(\*([a-z_][a-z0-9_]*)\)\s*\(",board_header))
 initializer_start=board_source.index(
  "static const struct open_cfw_pt_board_calls calls = {")
 initializer_end=board_source.index("\n    };",initializer_start)
 initializer=board_source[initializer_start:initializer_end]
 direct_function_matches=re.findall(
  r"\.([a-z_][a-z0-9_]*)\s*=\s*FUNCTION\(\s*(.*?)\s*,\s*"
  r"0x([0-9A-Fa-f]{8})U\s*\)",initializer,re.S)
 retained_function_matches=re.findall(
  r"\.([a-z_][a-z0-9_]*)\s*=\s*RETAINED_FUNCTION\(\s*(.*?)\s*,\s*"
  r"0x([0-9A-Fa-f]{8})U\s*,\s*([a-z_][a-z0-9_]*)\s*\)",
  initializer,re.S)
 function_matches=[(field,abi,address) for field,abi,address in
  direct_function_matches]+[(field,abi,address) for field,abi,address,_ in
  retained_function_matches]
 function_bindings={field:(normalized_c_type(abi),int(address,16))
  for field,abi,address in function_matches}
 if len(function_matches)!=len(function_bindings) or function_bindings!=BOARD_FUNCTION_BINDINGS:
  raise RuntimeError("PT Apollo board field/address/function-ABI binding changed")
 retained_symbols={int(address,16):symbol for _,_,address,symbol in
  retained_function_matches}
 expected_retained_symbols={address:symbol for address,(symbol,_) in
  BOARD_LEAF_CANDIDATES.items()}
 if retained_symbols!=expected_retained_symbols:
  raise RuntimeError("PT production source-provider selection changed")
 if board_callbacks!=set(BOARD_FUNCTION_BINDINGS):
  raise RuntimeError("PT board callback declaration/binding association changed")
 board_addresses={address for _,address in function_bindings.values()}
 expected_board_addresses=set(BOARD_SOURCE_OVERLAY_TARGETS)|set(BOARD_RETAINED_PROVIDERS)
 if board_operations!=BOARD_OPERATIONS:raise RuntimeError("PT board operation tranche changed")
 if len(board_callbacks)!=83:raise RuntimeError("PT board callback surface changed")
 if board_addresses!=expected_board_addresses:raise RuntimeError("PT Apollo board provider address set changed")
 direct_data_matches=re.findall(
  r"\.([a-z_][a-z0-9_]*)\s*=\s*\(([^()]+(?:\*[^()]*)?)\)"
  r"\(uintptr_t\)0x([0-9A-Fa-f]{8})U",initializer,re.S)
 data_bindings={field:(normalized_c_type(abi),int(address,16))
  for field,abi,address in direct_data_matches}
 required_paths=re.search(
  r"\.storage_required_paths\s*=\s*\{(.*?)\}",initializer,re.S)
 if required_paths is None:raise RuntimeError("PT storage path binding array missing")
 path_matches=re.findall(
  r"\(([^()]+)\)\(uintptr_t\)0x([0-9A-Fa-f]{8})U",
  required_paths.group(1))
 for index,(abi,address) in enumerate(path_matches):
  data_bindings[f"storage_required_paths[{index}]"]=(
   normalized_c_type(abi),int(address,16))
 cleanup_paths=re.search(
  r"\.cleanup_paths\s*=\s*\{(.*?)\}",initializer,re.S)
 if cleanup_paths is None:raise RuntimeError("PT cleanup path binding array missing")
 cleanup_matches=re.findall(
  r"\(([^()]+)\)\(uintptr_t\)0x([0-9A-Fa-f]{8})U",
  cleanup_paths.group(1))
 for index,(abi,address) in enumerate(cleanup_matches):
  data_bindings[f"cleanup_paths[{index}]"]=(
   normalized_c_type(abi),int(address,16))
 expected_data={field:(abi,address)
  for field,(abi,address,_) in BOARD_DATA_BINDINGS.items()}
 if (len(direct_data_matches)!=46 or len(path_matches)!=4 or
     len(cleanup_matches)!=3 or data_bindings!=expected_data):
  raise RuntimeError("PT Apollo board field/address/data-ABI binding changed")
 for field,(abi,address,extent) in BOARD_DATA_BINDINGS.items():
  if address<0x20000000:
   if address<0x00438000 or address+extent>0x007F0000:
    raise RuntimeError(f"PT retained flash-data extent invalid: {field}")
  elif address<0x20000000 or address+extent>0x20100000:
   raise RuntimeError(f"PT retained RAM-data extent invalid: {field}")
  if any(word in abi for word in ("uint32_t","float","void *volatile *")) and address%4:
   raise RuntimeError(f"PT retained data ABI alignment invalid: {field}")
 if board_source.count("board->calls = calls;")!=1:
  raise RuntimeError("PT board immutable call-table binding changed")
 lifetime_contract=("The caller owns calls.",
  "remain valid and immutable for the full",
  "lifetime of board and the platform backend")
 if any(marker not in board_header for marker in lifetime_contract):
  raise RuntimeError("PT board calls-table lifetime contract changed")
 if (BOARD_IMMUTABLE_FLASH_DATA_FIELDS|BOARD_RUNTIME_SRAM_DATA_FIELDS !=
     set(BOARD_DATA_BINDINGS) or
     BOARD_IMMUTABLE_FLASH_DATA_FIELDS&BOARD_RUNTIME_SRAM_DATA_FIELDS):
  raise RuntimeError("PT board retained-data support policy changed")
 if any(BOARD_DATA_BINDINGS[field][1] >= 0x20000000
        for field in BOARD_IMMUTABLE_FLASH_DATA_FIELDS):
  raise RuntimeError("PT immutable-flash data binding left flash")
 if any(BOARD_DATA_BINDINGS[field][1] < 0x20000000
        for field in BOARD_RUNTIME_SRAM_DATA_FIELDS):
  raise RuntimeError("PT runtime-SRAM data binding left SRAM")
 source_fields={field for field,(_,address) in function_bindings.items()
  if address in BOARD_SOURCE_OVERLAY_TARGETS}
 retained_fields={field for field,(_,address) in function_bindings.items()
  if address in BOARD_RETAINED_PROVIDERS}
 if source_fields|retained_fields!=set(function_bindings) or source_fields&retained_fields:
  raise RuntimeError("PT board source/retained field classification changed")
 leaf_source=(COMPONENT/"pt_protocol_board_leaf_candidates.c").read_text()
 leaf_header=(COMPONENT/"pt_protocol_board_leaf_candidates.h").read_text()
 validate_lc3_license_boundary(lc3_adaptation,leaf_source)
 leaf_blocks={name:body for name,body in re.findall(
  r"(?ms)^#ifndef\s+(OPEN_CFW_PT_[A-Z0-9_]+)\s*$\n"
  r"^#define\s+\1\s+(.*?)^#endif\s*$",leaf_source)}
 leaf_callable_bindings={}
 leaf_data_bindings={}
 for name,body in leaf_blocks.items():
  address_match=re.search(r"0x([0-9A-Fa-f]{8})U?",body)
  if address_match is None:continue
  address=int(address_match.group(1),16)
  cast_match=re.search(
   r"\(\((.*?)\)\s*\\?\s*\(uintptr_t\)\s*0x[0-9A-Fa-f]{8}U?\)",
   body,re.S)
  if cast_match is not None and "(*" in cast_match.group(1):
   leaf_callable_bindings[name]=(
    normalized_c_type(cast_match.group(1)),address)
  else:
   abi=(normalized_c_type(cast_match.group(1)) if cast_match is not None else
        "uint32_t address constant")
   category=BOARD_LEAF_DATA_BINDINGS.get(name,(None,None,None))[2]
   leaf_data_bindings[name]=(abi,address,category)
 if leaf_callable_bindings!=BOARD_LEAF_CALLABLE_BINDINGS:
  raise RuntimeError("PT board leaf fixed callable/ABI census changed")
 if leaf_data_bindings!=BOARD_LEAF_DATA_BINDINGS:
  raise RuntimeError("PT board leaf fixed data/category/ABI census changed")
 for macro,(abi,symbol) in BOARD_LEAF_LOCAL_SOURCE_CALLABLES.items():
  body=leaf_blocks.get(macro)
  if body is None or body.strip().replace("\\\n", " ").strip()!=symbol:
   raise RuntimeError(f"PT board local source binding changed: {macro}")
  provider_source=(lc3_adaptation if symbol.startswith(
   "open_cfw_pt_lc3_") else leaf_source)
  if (len(re.findall(
      rf"(?m)^[A-Za-z_][^\n]*\b{re.escape(symbol)}\s*\([^;{{}}]*\)\s*\{{",
      provider_source))!=1 or symbol not in leaf_header):
   raise RuntimeError(f"PT board local source provider changed: {symbol}")
 postprocess_send=re.search(
  r"void\s+open_cfw_pt_display_postprocess_send\s*\([^)]*\)\s*\{(.*?)\n\}",
  leaf_source,re.S)
 if (postprocess_send is None or
     "OPEN_CFW_PT_LENS_SYNC_TRANSPORT" not in postprocess_send.group(1) or
     "fourth, 5U, 2U, 0U" not in postprocess_send.group(1) or
     "OPEN_CFW_PT_DISPLAY_APPLY" in postprocess_send.group(1)):
  raise RuntimeError("PT display postprocess lens-sync semantics changed")
 uart_cache_source_pattern=(
  r"OPEN_CFW_PT_UART_CACHE_DSB\(\);\s*while\s*\([^)]*\)\s*\{\s*"
  r"\*OPEN_CFW_PT_UART_CACHE_CLEAN_REGISTER\s*=.*?\}\s*"
  r"OPEN_CFW_PT_UART_CACHE_DSB\(\);\s*"
  r"OPEN_CFW_PT_UART_CACHE_ISB\(\);")
 if re.search(uart_cache_source_pattern,leaf_source,re.S) is None:
  raise RuntimeError("PT UART cache-maintenance source sequence changed")
 lc3_source=re.search(
  r"void\s*\*\s*open_cfw_pt_lc3_setup_encoder\s*\([^)]*\)\s*\{(.*?)\n\}",
  lc3_adaptation,re.S)
 lc3_bounded_source=re.search(
  r"void\s*\*\s*open_cfw_pt_lc3_setup_encoder_bounded\s*\([^)]*\)\s*\{(.*?)\n\}",
  lc3_adaptation,re.S)
 lc3_fixed_wrapper=re.search(
  r"void\s+open_cfw_pt_audio_encoder_setup\s*\([^)]*\)\s*\{(.*?)\n\}",
  leaf_source,re.S)
 if (lc3_source is None or
     "case 2500U" not in lc3_source.group(1) or
     "case 10000U" not in lc3_source.group(1) or
     "case 48000U" not in lc3_source.group(1) or
     "pcm_sample_rate_hz <= 0" not in lc3_source.group(1) or
     "pcm_samples_4m = 192U" not in lc3_source.group(1) or
     "bytes[0] = (uint8_t)duration_index" not in lc3_source.group(1) or
     "bytes[1] = (uint8_t)codec_rate_index" not in lc3_source.group(1) or
     "bytes[2] = (uint8_t)pcm_rate_index" not in lc3_source.group(1) or
     "0x4A0U / sizeof(uint32_t)" not in lc3_source.group(1) or
     "0x4A8U / sizeof(uint32_t)" not in lc3_source.group(1) or
     "codec_rate_index > pcm_rate_index" not in lc3_source.group(1) or
     "(uintptr_t)storage & (sizeof(uint32_t) - 1U)" not in
      lc3_source.group(1) or
     "words[0] =" in lc3_source.group(1) or
     "pcm_samples_4m = 160U" in lc3_source.group(1) or
     lc3_bounded_source is None or
     "required > storage_capacity" not in lc3_bounded_source.group(1) or
     "open_cfw_pt_lc3_encoder_size" not in lc3_bounded_source.group(1) or
     lc3_fixed_wrapper is None or
     "OPEN_CFW_PT_AUDIO_CODEC_STORAGE_BYTES" not in
      lc3_fixed_wrapper.group(1) or
     "OPEN_CFW_PT_AUDIO_CODEC_SLOT_BYTES UINT32_C(0xA44)" not in
      leaf_source or
     "OPEN_CFW_PT_AUDIO_CODEC_HEADER_BYTES UINT32_C(0x1C)" not in
      leaf_source or
     re.search(
      r"^[A-Za-z_][^\n]*\bopen_cfw_pt_lc3_setup_encoder\s*\([^;{}]*\)\s*\{",
      leaf_source,re.M) is not None):
  raise RuntimeError("PT Apache LC3 encoder setup semantics changed")
 if (len({address&~1 for _,address in leaf_callable_bindings.values()})!=42 or
     len({address for _,address,_ in leaf_data_bindings.values()})!=94 or
     set(address for _,address,_ in leaf_data_bindings.values())&
     set(address for _,address,_ in BOARD_DATA_BINDINGS.values())):
  raise RuntimeError("PT board leaf fixed dependency uniqueness changed")
 leaf_candidate_fields={field for field,(_,address) in function_bindings.items()
  if address in BOARD_LEAF_CANDIDATES}
 leaf_candidate_symbols={symbol for symbol,_ in BOARD_LEAF_CANDIDATES.values()}
 if len(leaf_candidate_fields)!=len(BOARD_LEAF_CANDIDATES):
  raise RuntimeError("PT retained-provider leaf candidate field coverage changed")
 for symbol in leaf_candidate_symbols:
  definitions=re.findall(
   rf"(?m)^[A-Za-z_][^\n]*\b{re.escape(symbol)}\s*\([^;{{}}]*\)\s*\{{",
   leaf_source)
  if len(definitions)!=1 or symbol not in leaf_header:
   raise RuntimeError(f"PT retained-provider leaf candidate changed: {symbol}")
 overlay=json.loads((COMPONENT/"overlay.json").read_text())
 all_routed={item.get("runtime_address"):item.get("target_function")
  for item in overlay["patch_sites"]}
 if (all_routed.get(
      LENS_SYNC_TRANSPORT_EVIDENCE["stock_transport_runtime_address"])
      is not None):
  raise RuntimeError("PT retained lens-sync boundary unexpectedly routed")
 leaf_source_routes={name:all_routed.get(address&~1)
  for name,(_,address) in leaf_callable_bindings.items()
  if all_routed.get(address&~1) is not None}
 if leaf_source_routes!=BOARD_LEAF_SOURCE_OVERLAY_TARGETS:
  raise RuntimeError("PT board leaf second-order source routing changed")
 leaf_retained_callable_bindings=(set(leaf_callable_bindings)-
  set(leaf_source_routes))
 leaf_source_callable_addresses={
  leaf_callable_bindings[name][1]&~1 for name in leaf_source_routes}
 leaf_retained_callable_addresses={
  leaf_callable_bindings[name][1]&~1 for name in leaf_retained_callable_bindings}
 leaf_data_categories={}
 for _,_,category in leaf_data_bindings.values():
  leaf_data_categories[category]=leaf_data_categories.get(category,0)+1
 leaf_callable_census=[]
 for name in sorted(leaf_callable_bindings):
  abi,pointer=leaf_callable_bindings[name]
  target=leaf_source_routes.get(name)
  leaf_callable_census.append({
   "macro":name,"abi":abi,"thumb_pointer":pointer,
   "runtime_address":pointer&~1,
   "category":("source_overlay_callable" if target is not None else
               "retained_callable"),
   "ownership":("source_owned" if target is not None else
                "supported_retained_service_boundary"),
   "target_function":target,
  })
 for name,(abi,symbol) in sorted(BOARD_LEAF_LOCAL_SOURCE_CALLABLES.items()):
  leaf_callable_census.append({
   "macro":name,"abi":abi,"thumb_pointer":None,"runtime_address":None,
   "category":"source_local_callable","ownership":"source_owned",
   "target_function":symbol,
  })
 leaf_data_census=[{
  "macro":name,"abi":abi,"runtime_address":address,"category":category,
  "ownership":"supported_retained_external_abi",
 } for name,(abi,address,category) in sorted(leaf_data_bindings.items())]
 routed_leaf_candidates={address:all_routed.get(address)
  for address in BOARD_LEAF_CANDIDATES
  if all_routed.get(address) is not None}
 if routed_leaf_candidates:
  raise RuntimeError(
   "PT retained-provider leaf candidates unexpectedly production-routed: "
   f"{routed_leaf_candidates}")
 host_operations=set(re.findall(
  r"OPEN_CFW_PT_OP_[A-Z0-9_]+",board_fixture))-{"OPEN_CFW_PT_OP_COUNT"}
 if host_operations!=BOARD_OPERATIONS:
  raise RuntimeError("PT board host operation coverage changed")
 failure_markers=(
  "OPEN_CFW_PT_OP_COUNT", "OPEN_CFW_PT_HANDLER_FAILED",
  "open_cfw_pt_board_backend_initialize(NULL",
  "missing_backend.perform(OPEN_CFW_PT_OP_SET_BOX_DETECTED")
 if any(marker not in board_fixture for marker in failure_markers):
  raise RuntimeError("PT board host failure/unsupported semantics gate changed")
 routed={item.get("runtime_address"):item.get("target_function") for item in overlay["patch_sites"] if item.get("runtime_address") in BOARD_SOURCE_OVERLAY_TARGETS}
 if routed!=BOARD_SOURCE_OVERLAY_TARGETS:raise RuntimeError("PT Apollo board source-overlay routing changed")
 install_references=sum(path.read_text().count("open_cfw_pt_protocol_production_install(") for path in COMPONENT.glob("*.c"))
 production_entry=(COMPONENT/"pt_protocol_production_entry.c").read_text()
 production_header=(COMPONENT/"pt_protocol_production_entry.h").read_text()
 bootstrap_markers=(
  "open_cfw_pt_protocol_production_bootstrap(",
  "open_cfw_pt_board_backend_initialize_production(",
  "production_install_with_storage(",
  "state->board.calls->ota_async_data,",
  "OPEN_CFW_PT_PRODUCTION_OTA_STORAGE_BYTES - sizeof(*state)",
  'OPEN_CFW_PT_LEGACY_SECTION(".pt_legacy_entry")',
  'OPEN_CFW_PT_LEGACY_SECTION(".pt_legacy_postprocess")')
 if (install_references!=1 or
     any(marker not in production_entry for marker in bootstrap_markers) or
     "open_cfw_pt_protocol_production_bootstrap(" not in production_header):
  raise RuntimeError("PT production backend bootstrap surface changed")
 bootstrap_reachability_markers=(
  "state->magic != OPEN_CFW_PT_PRODUCTION_STATE_MAGIC",
  "state->installed == 0U",
  "open_cfw_pt_protocol_production_bootstrap();")
 if any(marker not in production_entry for marker in
        bootstrap_reachability_markers):
  raise RuntimeError("PT production lazy bootstrap reachability changed")
 platform_backend_production_bound=True
 production_routed=False
 cc=require_tool("OPENCFW_CLANG","clang");ld=require_tool("OPENCFW_LLD","ld.lld","lld");nm=require_tool("OPENCFW_NM","llvm-nm","nm")
 with tempfile.TemporaryDirectory(prefix="g2-pt-source-") as d:
  profiles={}
  for profile,cpu in (("apollo510","cortex-m55"),("cortex_m0plus","cortex-m0plus")):
   objects=[];profile_dir=Path(d)/profile;profile_dir.mkdir()
   for source in SOURCES:
    obj=profile_dir/(source.stem+".o");subprocess.run([cc,"--target=arm-none-eabi",f"-mcpu={cpu}","-mthumb","-std=c11","-Oz","-ffreestanding","-fno-builtin","-ffunction-sections","-fdata-sections","-fno-unwind-tables","-fno-asynchronous-unwind-tables","-Wall","-Wextra","-Werror","-DOPEN_CFW_PT_PRODUCTION_SOURCE_PROVIDERS=1","-I",str(COMPONENT),"-c",str(source),"-o",str(obj)],check=True,capture_output=True,text=True);objects.append(obj)
   linked=Path(d)/(profile+"-pt-protocol.o");subprocess.run([ld,"-r","-o",str(linked),*[str(x) for x in objects]],check=True,capture_output=True,text=True)
   undefined=[line for line in subprocess.run([nm,"-u",str(linked)],check=True,capture_output=True,text=True).stdout.splitlines() if line.strip()]
   if undefined:raise RuntimeError(f"{profile} undefined target symbols: {undefined}")
   profiles[profile]={"undefined_symbols":len(undefined),"relocatable_size":linked.stat().st_size,"relocatable_sha256":sha(linked.read_bytes()),"sections":elf_section_totals(linked)}
  linked_size=profiles["apollo510"]["relocatable_size"];linked_sha=profiles["apollo510"]["relocatable_sha256"]
 target_sections=profiles["apollo510"]["sections"]
 if target_sections["bss"]!=0 or target_sections["data"]!=0:
  raise RuntimeError("PT target still requires unbound writable storage")
 with tempfile.TemporaryDirectory(prefix="g2-pt-placement-") as d:
  placement_dir=Path(d);objects=[]
  for source in SOURCES:
   obj=placement_dir/(source.stem+".o")
   subprocess.run([cc,"--target=arm-none-eabi","-mcpu=cortex-m55","-mthumb",
    "-std=c11","-Oz","-ffreestanding","-fno-builtin","-ffunction-sections",
    "-fdata-sections","-fno-unwind-tables","-fno-asynchronous-unwind-tables",
    "-Wall","-Wextra","-Werror","-DOPEN_CFW_PT_PRODUCTION_SOURCE_PROVIDERS=1",
    "-I",str(COMPONENT),"-c",str(source),
    "-o",str(obj)],check=True,capture_output=True,text=True);objects.append(obj)
  linker=placement_dir/"pt.ld"
  linker.write_text(
   "SECTIONS { . = 0x0056F4A0; .pt_legacy_entry : "
   "{ KEEP(*(.pt_legacy_entry)) } . = 0x0056F92C; "
   ".pt_legacy_postprocess : { KEEP(*(.pt_legacy_postprocess)) } "
   ". = 0x0056F940; .text : { *(.text*) *(.rodata*) } "
   "/DISCARD/ : { *(.ARM.exidx*) *(.ARM.extab*) *(.comment) "
   "*(.ARM.attributes) } } "
   "ASSERT(ADDR(.pt_legacy_entry) == 0x0056F4A0, \"PT entry ABI moved\") "
   "ASSERT(ADDR(.pt_legacy_postprocess) == 0x0056F92C, "
   "\"PT postprocess ABI moved\") "
   "ASSERT(ADDR(.text) + SIZEOF(.text) <= 0x00577C3C, "
   "\"PT interval overflow\")\n")
  placed=placement_dir/"pt.elf"
  subprocess.run([ld,"-T",str(linker),"-e",
   "open_cfw_pt_protocol_production_entry","-o",str(placed),
   *[str(x) for x in objects]],check=True,capture_output=True,text=True)
  placement_sections=elf_section_totals(placed)
  symbols=subprocess.run([nm,"-n",str(placed)],check=True,
   capture_output=True,text=True).stdout
  symbol_addresses={name:int(address,16) for address,kind,name in
   (line.split() for line in symbols.splitlines() if len(line.split())==3)}
  dispatcher_address=symbol_addresses["open_cfw_pt_protocol_production_entry"]
  uart_start=symbol_addresses["open_cfw_pt_uart_write"]
  uart_end=min(address for address in symbol_addresses.values()
               if address>uart_start)
  uart_machine=elf_virtual_range(placed,uart_start,uart_end)
  dsb_encoding=b"\xbf\xf3\x4f\x8f"
  isb_encoding=b"\xbf\xf3\x6f\x8f"
  dmb_encoding=b"\xbf\xf3\x5f\x8f"
  dsb_offsets=[index for index in range(len(uart_machine)-3)
               if uart_machine[index:index+4]==dsb_encoding]
  isb_offsets=[index for index in range(len(uart_machine)-3)
               if uart_machine[index:index+4]==isb_encoding]
  dmb_offsets=[index for index in range(len(uart_machine)-3)
               if uart_machine[index:index+4]==dmb_encoding]
  uart_cache_maintenance_verified=(
   len(dsb_offsets)==2 and len(isb_offsets)==1 and not dmb_offsets and
   dsb_offsets[0]<dsb_offsets[1] and
   dsb_offsets[1]<isb_offsets[0]<=dsb_offsets[1]+32 and
   struct.pack("<I",0xE000EF68) in uart_machine)
  if not uart_cache_maintenance_verified:
   raise RuntimeError(
    "PT target UART cache maintenance is not DSB/DCCMVAC/DSB/ISB: "
    f"dsb={dsb_offsets}, isb={isb_offsets}, dmb={dmb_offsets}, "
    f"dccmvac={struct.pack('<I',0xE000EF68) in uart_machine}")
  uart_cache_evidence={
   "function":"open_cfw_pt_uart_write",
   "function_runtime_address":uart_start,
   "function_size":uart_end-uart_start,
   "function_sha256":sha(uart_machine),
   "dccmvac_register":0xE000EF68,
   "dsb_runtime_addresses":[uart_start+offset for offset in dsb_offsets],
   "isb_runtime_addresses":[uart_start+offset for offset in isb_offsets],
   "dmb_runtime_addresses":[uart_start+offset for offset in dmb_offsets],
   "required_sequence":"DSB; DCCMVAC loop; DSB; ISB",
   "target_bytes_verified":True,
  }
  placement_interval_start=0x0056F178
  placement_start=placement_sections["loadable_start"]
  placement_end=placement_sections["loadable_end_exclusive"]
  placement_capacity=0x00577C3C-placement_interval_start
  placement_complete=(placement_sections["data"]==0 and
   placement_sections["bss"]==0 and placement_end<=0x00577C3C and
   placement_interval_start<=placement_start and
   placement_start<=dispatcher_address<placement_end and
   symbol_addresses.get("open_cfw_pt_protocol_legacy_entry")==0x0056F4A0 and
   symbol_addresses.get("open_cfw_pt_protocol_legacy_postprocess")==0x0056F92C)
 specification=importlib.util.spec_from_file_location(
  "open_cfw_pt_protocol_source_gate_builder",PT_BUILDER)
 if specification is None or specification.loader is None:
  raise RuntimeError("PT bounded provider builder unavailable")
 provider_builder=importlib.util.module_from_spec(specification)
 specification.loader.exec_module(provider_builder)
 core_config=json.loads(CORE_CONFIG.read_text())
 official_expected={
  "size":int(core_config["base"]["size"]),
  "sha256":core_config["base"]["sha256"],
 }
 with tempfile.TemporaryDirectory(prefix="g2-pt-provider-proof-") as d:
  pt_provider=provider_builder.build(
   base_path=OFFICIAL_COMPONENT,output_dir=Path(d),clang=cc,
   profile="apple-clang",source_uart_routed=False,
   ingress_authentication_base_path=OFFICIAL_COMPONENT,
   ingress_authentication_base_expected=official_expected)
 routes=pt_provider.get("source_provider_routes",[])
 production_routed=(len(routes)==len(BOARD_LEAF_CANDIDATES) and
  {item.get("target_function") for item in routes}==leaf_candidate_symbols and
  int(pt_provider.get("placement",{}).get("writable_bytes",-1))==0 and
  pt_provider.get("patch_sites")==[])
 pt_profile=(core_config.get("post_link_providers",{}).get("pt_protocol",{})
  .get("profiles",{}).get("apple-clang"))
 if not isinstance(pt_profile,dict):
  raise RuntimeError("PT canonical Apple profile missing")
 live_pt_profile={
  "payload_size":int(pt_provider["placement"]["loadable_size"]),
  "payload_sha256":pt_provider["placement"]["payload_sha256"],
  "interval_sha256":pt_provider["placement"]["interval_sha256"],
 }
 canonical_apple_profile_matches=pt_profile==live_pt_profile
 if enforce_canonical_pin and not canonical_apple_profile_matches:
  raise RuntimeError("PT canonical Apple profile pin changed")
 if "linux-clang" not in (core_config.get("post_link_providers",{})
                           .get("pt_protocol",{}).get("profiles",{})):
  raise RuntimeError("PT canonical Linux profile missing")
 overlay_end=(int(core_config["run_base"])+
  int(core_config["expected"]["component_size"])-
  int(core_config["preamble_bytes"]))
 placement_free=max(0,0x007FE000-overlay_end)
 placement_shortfall=max(0,target_sections["loadable"]-placement_free)
 report={"schema_version":1,"evidence":{"corpus_functions":len(functions),"command_handlers":len(rows),"stock_function_body_bytes":STOCK_BODY_BYTES,"corpus_sha256":CORPUS_DIGESTS["functions.jsonl"],"corpus_ledger_verified":True},"ownership":{"license":"mixed","licenses":{"MIT":"OpenCFW PT protocol and G2 wiring","Apache-2.0":"Google/liblc3 encoder-setup adaptation"},"source_files":len(owned),"source_bytes":sum(path.stat().st_size for path in owned),"source_sha256":owned_digest,"stock_machine_code_bytes_in_source":0,"retained_vendor_data_bytes_embedded_in_source":0},"software":{"translation_units":len(SOURCES),"bound_commands":len(found),"duplicate_commands":0,"missing_commands":0,"target_undefined_symbols":0,"apollo510_undefined_symbols":profiles["apollo510"]["undefined_symbols"],"cortex_m0plus_undefined_symbols":profiles["cortex_m0plus"]["undefined_symbols"],"target_relocatable_size":linked_size,"target_relocatable_sha256":linked_sha,"target_text_bytes":target_sections["text"],"target_rodata_bytes":target_sections["rodata"],"target_data_bytes":target_sections["data"],"target_bss_bytes":target_sections["bss"],"target_loadable_bytes":target_sections["loadable"],"production_text_placement_free_bytes":placement_free,"production_text_placement_shortfall_bytes":placement_shortfall,"production_in_place_interval_start":placement_interval_start,"production_in_place_interval_end_exclusive":0x00577C3C,"production_in_place_linked_start":placement_start,"production_in_place_capacity_bytes":placement_capacity,"production_in_place_loadable_bytes":placement_sections["loadable"],"production_in_place_end_exclusive":placement_end,"production_dispatcher_address":dispatcher_address,"external_entry_callsites":external_entries,"production_ingress_sites":pt_provider.get("ingress_sites",[]),"production_ram_binding_remaining_bytes":target_sections["bss"],"production_placement_complete":placement_complete,"handler_surface_complete":True,"provider_operation_count":len(operations),"provider_callback_count":58,"provider_adapters_complete":True,"platform_backend_contract_complete":True,"stock_abi_entry_complete":True,"production_bootstrap_complete":True,"production_bootstrap_reachable":True,"board_calls_table_lifetime_contract":True,"board_operations_implemented":len(board_operations),"board_operations_remaining":len(operations-board_operations),"board_host_operations_exercised":len(host_operations),"board_failure_semantics_exercised":True,"board_callback_count":len(board_callbacks),"board_service_bindings":len(board_addresses),"board_function_binding_associations_verified":True,"board_function_abis_verified":True,"board_source_routed_service_bindings":len(source_fields),"board_retained_service_bindings":len(retained_fields),"board_retained_provider_candidate_bindings":len(leaf_candidate_fields),"board_retained_provider_bindings_remaining":len(retained_fields-leaf_candidate_fields),"board_retained_provider_candidate_stock_body_bytes":sum(size for _,size in BOARD_LEAF_CANDIDATES.values()),"board_retained_provider_candidates_semantic_c":True,"board_retained_provider_candidates_production_routed":production_routed,"board_retained_providers_source_owned":False,"board_stock_layout_data_bindings":len(data_bindings),"board_data_binding_associations_verified":True,"board_data_abis_and_extents_verified":True,"board_stock_layout_data_immutable_flash_bindings":len(BOARD_IMMUTABLE_FLASH_DATA_FIELDS),"board_stock_layout_data_runtime_sram_bindings":len(BOARD_RUNTIME_SRAM_DATA_FIELDS),"board_stock_layout_data_deliberately_supported":True,"board_stock_layout_data_software_gap":False,"board_stock_layout_data_source_owned":False,"board_apollo_binding_available":True,"platform_backend_production_bound":platform_backend_production_bound,"production_routed":production_routed},"hardware":{"validation":"blocked by unavailable physical evidence","qualification_complete":False}}
 report["evidence"].update({
 "official_component_sha256":OFFICIAL_COMPONENT_SHA256,
 "postprocess_lens_sync_transport":dict(LENS_SYNC_TRANSPORT_EVIDENCE,
   abi=LENS_SYNC_TRANSPORT_ABI,authenticated=True,
   authenticated_decomp_index_sha256=AUTHENTICATED_DECOMP_INDEX_SHA256),
  "lc3_setup_boundary":dict(LC3_SETUP_EVIDENCE,abi=LC3_SETUP_ABI,
   authenticated=True),
 })
 report["software"].update({
  "board_top_level_retained_provider_bindings_remaining":
   len(retained_fields-leaf_candidate_fields),
  "board_retained_provider_bindings_remaining":
   len(leaf_retained_callable_bindings),
  "board_retained_providers_source_owned":False,
  "board_source_complete":False,
  "board_second_order_abis_verified":False,
  "board_second_order_binding_inventory_verified":True,
  "board_postprocess_lens_sync_transport_abi_and_address_authenticated":
   lens_sync_transport_authenticated,
  "board_postprocess_lens_sync_transport_evidence":
   report["evidence"]["postprocess_lens_sync_transport"],
  "board_uart_cache_maintenance_target_verified":
   uart_cache_maintenance_verified,
  "board_uart_cache_maintenance_evidence":uart_cache_evidence,
  "board_lc3_setup_boundary_authenticated":lc3_setup_boundary_authenticated,
  "board_lc3_setup_license":LC3_SETUP_EVIDENCE["upstream_license"],
  "board_lc3_setup_source_routed":True,
  "board_lc3_setup_fail_closed":True,
  "board_lc3_setup_pending_software_gates":[],
  "canonical_apple_profile_matches":canonical_apple_profile_matches,
  "canonical_pin_enforced":enforce_canonical_pin,
  "board_second_order_callable_bindings":(
   len(leaf_callable_bindings)+len(BOARD_LEAF_LOCAL_SOURCE_CALLABLES)),
  "board_second_order_callable_census":leaf_callable_census,
  "board_second_order_callable_unique_addresses":
   len({address&~1 for _,address in leaf_callable_bindings.values()}),
  "board_second_order_source_overlay_callable_bindings":
   len(leaf_source_routes),
  "board_second_order_source_local_callable_bindings":
   len(BOARD_LEAF_LOCAL_SOURCE_CALLABLES),
  "board_second_order_source_callable_bindings":
   len(leaf_source_routes)+len(BOARD_LEAF_LOCAL_SOURCE_CALLABLES),
  "board_second_order_source_overlay_callable_unique_addresses":
   len(leaf_source_callable_addresses),
  "board_second_order_retained_callable_bindings":
   len(leaf_retained_callable_bindings),
  "board_second_order_retained_callable_unique_addresses":
   len(leaf_retained_callable_addresses),
  "board_second_order_data_bindings":len(leaf_data_bindings),
  "board_second_order_data_census":leaf_data_census,
  "board_second_order_data_unique_addresses":
   len({address for _,address,_ in leaf_data_bindings.values()}),
  "board_second_order_data_source_owned":0,
  "board_second_order_retained_data_bindings":len(leaf_data_bindings),
  "board_second_order_data_categories":leaf_data_categories,
  "board_second_order_retained_boundaries_deliberately_supported":True,
 })
 report["hardware"]={
  "validation":"blocked by unavailable physical evidence",
  "qualification_complete":False,
 }
 return report
def main()->int:
 ap=argparse.ArgumentParser();ap.add_argument("--write-manifest",action="store_true");ap.add_argument("--allow-stale-canonical-pin",action="store_true");a=ap.parse_args();r=analyze(enforce_canonical_pin=not a.allow_stale_canonical_pin);
 if a.write_manifest:OUTPUT.write_text(json.dumps(r,indent=2,sort_keys=True)+"\n")
 print(json.dumps(r,indent=2,sort_keys=True));return 0
if __name__=="__main__":raise SystemExit(main())
