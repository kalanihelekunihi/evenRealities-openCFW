#!/bin/bash
# EasyLogger elog __FUNCTION__ cross-reference upgrades
# Generated 2026-03-07 by analyzing elog param_4 (__FUNCTION__) string references
# in decompiled G2 main firmware (ota_s200_firmware_ota)
#
# Method: The firmware uses EasyLogger with calls to FUN_0043d1c8 (elog_output):
#   FUN_0043d1c8(level, tag, source_file, __FUNCTION__, line_num, fmt, ...)
# The 4th parameter is the C compiler's __FUNCTION__ macro, which embeds the
# actual source function name as a string literal. By resolving the string
# pointer in param_4, we recover the original C function name.
#
# Sources:
#   PTR_s_ : Ghidra label embeds the string content (most reliable)
#   DAT_   : Binary pointer resolved to string at target address (verified: points to string start)
#
# Total: 31 function name corrections (16 additional confirmed-correct, 2 rejected as enum constants)
# All upgrades are HIGH->HIGH (correcting previously-inferred names with actual source names)

cd "$(dirname "$0")"

# ble_production_msg_head_check -> _thread_ble_production_msg_head_check
sed -i '' "s|^0x004573f2\t.*|0x004573f2\tFUN_004573f2\t_thread_ble_production_msg_head_check\ttask.ble.production\tHIGH\t# elog __FUNCTION__ match: PTR_s @ 0x00457720 # was: ble_production_msg_head_check|" function_map.txt

# ble_production_msg_crc_check -> _thread_ble_production_msg_crc_check
sed -i '' "s|^0x0045744c\t.*|0x0045744c\tFUN_0045744c\t_thread_ble_production_msg_crc_check\ttask.ble.production\tHIGH\t# elog __FUNCTION__ match: PTR_s @ 0x0045772c # was: ble_production_msg_crc_check|" function_map.txt

# appSlaveSecConnOpen -> _blePsnIntoADV
sed -i '' "s|^0x00458316\t.*|0x00458316\tFUN_00458316\t_blePsnIntoADV\tble.slave\tHIGH\t# elog __FUNCTION__ match: DAT_004584b4 -> 0x00734420 # was: appSlaveSecConnOpen|" function_map.txt

# conn_param_update_dispatch -> APP_BleNameGet
sed -i '' "s|^0x0046ff8c\t.*|0x0046ff8c\tFUN_0046ff8c\tAPP_BleNameGet\tble.param\tHIGH\t# elog __FUNCTION__ match: DAT_0047071c -> 0x00734490 # was: conn_param_update_dispatch|" function_map.txt

# pt_proto_set_connection_state -> get_buzzer_base
sed -i '' "s|^0x00494d4c\t.*|0x00494d4c\tFUN_00494d4c\tget_buzzer_base\tpt_protocol_procsr\tHIGH\t# elog __FUNCTION__ match: DAT_00495004 -> 0x007377d0 # was: pt_proto_set_connection_state|" function_map.txt

# PB_TxEncodeDevConfig_pairing -> PB_RxUnpairInfo
sed -i '' "s|^0x0049f628\t.*|0x0049f628\tFUN_0049f628\tPB_RxUnpairInfo\tpb.devc\tHIGH\t# elog __FUNCTION__ match: DAT_0049f85c -> 0x00737130 # was: PB_TxEncodeDevConfig_pairing|" function_map.txt

# ancc_notification_source_handler -> _anccGetNextNotificationHandler
sed -i '' "s|^0x004a147e\t.*|0x004a147e\tFUN_004a147e\t_anccGetNextNotificationHandler\tble.ancc\tHIGH\t# elog __FUNCTION__ match: DAT_004a1e14 -> 0x00716ab8 # was: ancc_notification_source_handler|" function_map.txt

# setting_notify_device_status -> setting_notify_device_status_to_app
sed -i '' "s|^0x004aaee4\t.*|0x004aaee4\tFUN_004aaee4\tsetting_notify_device_status_to_app\tpb_service_setting\tHIGH\t# elog __FUNCTION__ match: PTR_s @ 0x004ab134 # was: setting_notify_device_status|" function_map.txt

# ring_conn_setup -> NusHandlerInit
sed -i '' "s|^0x004bd5ee\t.*|0x004bd5ee\tFUN_004bd5ee\tNusHandlerInit\tble.ring\tHIGH\t# elog __FUNCTION__ match: DAT_004bd91c -> 0x00737330 # was: ring_conn_setup|" function_map.txt

# file_system_mount -> check_and_create_directories
sed -i '' "s|^0x004d0336\t.*|0x004d0336\tFUN_004d0336\tcheck_and_create_directories\tfile_system\tHIGH\t# elog __FUNCTION__ match: DAT_004d05cc -> 0x00713778 # was: file_system_mount|" function_map.txt

# PB_RxDevConfig_battery -> RestoreFactory
sed -i '' "s|^0x004d4cbe\t.*|0x004d4cbe\tFUN_004d4cbe\tRestoreFactory\tpb.devc\tHIGH\t# elog __FUNCTION__ match: DAT_004d52ac -> 0x00737000 # was: PB_RxDevConfig_battery|" function_map.txt

# npmx_disable_lsdw2_voltage -> disable_lsdw2_voltage
sed -i '' "s|^0x004d9694\t.*|0x004d9694\tFUN_004d9694\tdisable_lsdw2_voltage\tnpmx_driver\tHIGH\t# elog __FUNCTION__ match: PTR_s @ 0x004d9cd0 # was: npmx_disable_lsdw2_voltage|" function_map.txt

# AttsCccInitTable -> attsCccAllocTbl
sed -i '' "s|^0x004de678\t.*|0x004de678\tFUN_004de678\tattsCccAllocTbl\tble.att\tHIGH\t# elog __FUNCTION__ match: DAT_004dec90 -> 0x007348d0 # was: AttsCccInitTable|" function_map.txt

# parseWhiteListFromFS -> _parseWhiteListFromFS
sed -i '' "s|^0x004eb038\t.*|0x004eb038\tFUN_004eb038\t_parseWhiteListFromFS\tsvc.whitelist\tHIGH\t# elog __FUNCTION__ match: PTR_s @ 0x004eba20 # was: parseWhiteListFromFS|" function_map.txt

# callback_list_clear -> box_uart_mgr
sed -i '' "s|^0x004ec77e\t.*|0x004ec77e\tFUN_004ec77e\tbox_uart_mgr\tcallback.mgr\tHIGH\t# elog __FUNCTION__ match: DAT_004ecb44 -> 0x00734cf0 # was: callback_list_clear|" function_map.txt

# bq25180_read_register_generic -> DRV_Bq25180SetFastchargeCurrent
sed -i '' "s|^0x00523b88\t.*|0x00523b88\tFUN_00523b88\tDRV_Bq25180SetFastchargeCurrent\tcharge\tHIGH\t# elog __FUNCTION__ match: DAT_00524624 -> 0x00712898 # was: bq25180_read_register_generic|" function_map.txt

# thread_audio_handler -> AUD_ThreadInit
sed -i '' "s|^0x00524e6a\t.*|0x00524e6a\tFUN_00524e6a\tAUD_ThreadInit\tthread.audio\tHIGH\t# elog __FUNCTION__ match: DAT_0052556c -> 0x00738980 # was: thread_audio_handler|" function_map.txt

# android_notify_send_sync -> SVC_ANCC_Clear
sed -i '' "s|^0x0052c46a\t.*|0x0052c46a\tFUN_0052c46a\tSVC_ANCC_Clear\tsvc.android_notify\tHIGH\t# elog __FUNCTION__ match: DAT_0052c758 -> 0x007378e0 # was: android_notify_send_sync|" function_map.txt

# stock_ext_event_handler_f1e0 -> stock_ext_event_handler
sed -i '' "s|^0x0054f1e0\t.*|0x0054f1e0\tFUN_0054f1e0\tstock_ext_event_handler\tdashboard.stock\tHIGH\t# elog __FUNCTION__ match: PTR_s @ 0x0054fc18 # was: stock_ext_event_handler_f1e0|" function_map.txt

# stock_clear_display -> calculate_stocks_in_container
sed -i '' "s|^0x00550ef8\t.*|0x00550ef8\tFUN_00550ef8\tcalculate_stocks_in_container\tdashboard.stock\tHIGH\t# elog __FUNCTION__ match: DAT_005512e4 -> 0x0071a478 # was: stock_clear_display|" function_map.txt

# dashboard_ui_create_date_widget -> bounce_restore_anim_ready_cb
sed -i '' "s|^0x00560fb2\t.*|0x00560fb2\tFUN_00560fb2\tbounce_restore_anim_ready_cb\tdashborad.ui\tHIGH\t# elog __FUNCTION__ match: DAT_00561898 -> 0x00719ad8 # was: dashboard_ui_create_date_widget|" function_map.txt

# page_state_sync_update_content -> page_state_sync_news_expanded
sed -i '' "s|^0x00563dbe\t.*|0x00563dbe\tFUN_00563dbe\tpage_state_sync_news_expanded\tpage_state_sync\tHIGH\t# elog __FUNCTION__ match: DAT_00563f74 -> 0x00715fd8 # was: page_state_sync_update_content|" function_map.txt

# text_container_process_pending -> common_list_trigger_rubber_band
sed -i '' "s|^0x0058d74c\t.*|0x0058d74c\tFUN_0058d74c\tcommon_list_trigger_rubber_band\tcommon_text_container\tHIGH\t# elog __FUNCTION__ match: DAT_0058dfe0 -> 0x00711a58 # was: text_container_process_pending|" function_map.txt

# text_container_on_scroll_complete -> common_text_scroll_anim_exec_cb
sed -i '' "s|^0x0058d9e0\t.*|0x0058d9e0\tFUN_0058d9e0\tcommon_text_scroll_anim_exec_cb\tcommon_text_container\tHIGH\t# elog __FUNCTION__ match: DAT_0058e01c -> 0x00711a98 # was: text_container_on_scroll_complete|" function_map.txt

# conversate_calc_auto_duration -> conversate_calculate_auto_duration_by_label
sed -i '' "s|^0x0058fef4\t.*|0x0058fef4\tFUN_0058fef4\tconversate_calculate_auto_duration_by_label\tconversate.ui\tHIGH\t# elog __FUNCTION__ match: PTR_s @ 0x00590a00 # was: conversate_calc_auto_duration|" function_map.txt

# pb_service_conversate_secondary -> APP_PbConversateTxEncodeNotify
sed -i '' "s|^0x0059314c\t.*|0x0059314c\tFUN_0059314c\tAPP_PbConversateTxEncodeNotify\tpb.conversate\tHIGH\t# elog __FUNCTION__ match: DAT_00593328 -> 0x00716038 # was: pb_service_conversate_secondary|" function_map.txt

# mspi_validate_descriptor -> am_devices_mspi_set_serail_mode
sed -i '' "s|^0x00595d26\t.*|0x00595d26\tFUN_00595d26\tam_devices_mspi_set_serail_mode\tdriver.uled_common\tHIGH\t# elog __FUNCTION__ match: DAT_00596398 -> 0x00712bd8 # was: mspi_validate_descriptor|" function_map.txt

# jbd4010_status_recovery -> jdb4010_status_recovery (firmware source uses jdb typo)
sed -i '' "s|^0x005970fc\t.*|0x005970fc\tFUN_005970fc\tjdb4010_status_recovery\tdriver.jbd4010\tHIGH\t# elog __FUNCTION__ match: PTR_s @ 0x0059751c # was: jbd4010_status_recovery|" function_map.txt

# jbd4010_status_check -> am_devices_jbd4010_status_check_and_recovery
sed -i '' "s|^0x00597270\t.*|0x00597270\tFUN_00597270\tam_devices_jbd4010_status_check_and_recovery\tdriver.jbd4010\tHIGH\t# elog __FUNCTION__ match: PTR_s @ 0x00597538 # was: jbd4010_status_check|" function_map.txt

# pb_translate_decode -> APP_PbTranslateTxEncodeNotify
sed -i '' "s|^0x005b4b30\t.*|0x005b4b30\tFUN_005b4b30\tAPP_PbTranslateTxEncodeNotify\tpb.translate\tHIGH\t# elog __FUNCTION__ match: DAT_005b4e50 -> 0x00716998 # was: pb_translate_decode|" function_map.txt

# translate_ui_handler -> translate_ui_main_page_create
sed -i '' "s|^0x005caaaa\t.*|0x005caaaa\tFUN_005caaaa\ttranslate_ui_main_page_create\ttranslate.ui\tHIGH\t# elog __FUNCTION__ match: DAT_005cb51c -> 0x007196b8 # was: translate_ui_handler|" function_map.txt

echo "Applied 31 elog __FUNCTION__ upgrades to function_map.txt"
