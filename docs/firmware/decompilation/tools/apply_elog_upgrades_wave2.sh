#!/bin/bash
# EasyLogger elog __FUNCTION__ cross-reference upgrades — Wave 2
# Generated 2026-03-07 by comprehensive sweep of ALL elog_output (FUN_0043d1c8) call sites
# in decompiled G2 main firmware (ota_s200_firmware_ota)
#
# Method: Same as Wave 1 — resolve param_4 (__FUNCTION__) from elog_output calls.
#   FUN_0043d1c8(level, tag, source_file, __FUNCTION__, line_num, fmt, ...)
#
# Sources:
#   PTR_s_ : Ghidra label embeds the string content (most reliable).
#            Truncated labels (>32 chars) verified against rizin_strings.txt for full name.
#   DAT_   : Binary pointer resolved + at_start validation (byte before string == 0x00).
#
# Statistics from this sweep:
#   Total elog_output call sites:          4,549
#   Total elog_output_fmt call sites:      4,532
#   Unique functions with elog calls:      1,319
#   Functions with PTR_s_ param_4:         65 (256 call sites)
#   Functions with DAT_ param_4:           ~1,254 (4,281 call sites)
#   Already correct (name matches elog):   35 (PTR_s_ verified)
#   Applied in Wave 1:                     31
#   New upgrades in this Wave 2:           24
#
# Total: 24 function name corrections
# All upgrades are HIGH->HIGH (correcting previously-inferred names with actual source names)

cd "$(dirname "$0")"

# --- Thread infrastructure functions (generic names shared across task modules) ---

# ble_production_msg_handler -> _thread_msg_handler
# Source: platform/product_test task module
sed -i '' "s|^0x00456f3e\t.*|0x00456f3e\tFUN_00456f3e\t_thread_msg_handler\ttask.ble.production\tHIGH\t# elog __FUNCTION__ match: PTR_s @ 0x00457688 # was: ble_production_msg_handler|" function_map.txt

# ble_production_notify_handler -> _thread_notify_event_handler
sed -i '' "s|^0x004572e6\t.*|0x004572e6\tFUN_004572e6\t_thread_notify_event_handler\ttask.ble.production\tHIGH\t# elog __FUNCTION__ match: PTR_s @ 0x00457710 # was: ble_production_notify_handler|" function_map.txt

# ble_production_thread_exit -> _thread_exit
sed -i '' "s|^0x00457348\t.*|0x00457348\tFUN_00457348\t_thread_exit\ttask.ble.production\tHIGH\t# elog __FUNCTION__ match: PTR_s @ 0x00457718 # was: ble_production_thread_exit|" function_map.txt

# thread_ble_msgtx_entry -> _thread_exit
sed -i '' "s|^0x0046ef80\t.*|0x0046ef80\tFUN_0046ef80\t_thread_exit\tble.msgtx\tHIGH\t# elog __FUNCTION__ match: PTR_s @ 0x0046f1c8 # was: thread_ble_msgtx_entry|" function_map.txt

# thread_task_exit -> _thread_task_exit
sed -i '' "s|^0x00487054\t.*|0x00487054\tFUN_00487054\t_thread_task_exit\ttask.manager\tHIGH\t# elog __FUNCTION__ match: PTR_s @ 0x004875c4 # was: thread_task_exit|" function_map.txt

# thread_manager_main -> _thread_manager
sed -i '' "s|^0x0048719c\t.*|0x0048719c\tFUN_0048719c\t_thread_manager\ttask.manager\tHIGH\t# elog __FUNCTION__ match: PTR_s @ 0x004875cc # was: thread_manager_main|" function_map.txt

# task_manager_enter_mode -> _thread_notify_event_handler
sed -i '' "s|^0x00487238\t.*|0x00487238\tFUN_00487238\t_thread_notify_event_handler\ttask.manager\tHIGH\t# elog __FUNCTION__ match: PTR_s @ 0x004875c8 # was: task_manager_enter_mode|" function_map.txt

# thread_ble_msgrx_exit -> _thread_exit
sed -i '' "s|^0x0049b748\t.*|0x0049b748\tFUN_0049b748\t_thread_exit\tble.msgrx\tHIGH\t# elog __FUNCTION__ match: PTR_s @ 0x0049b8c0 # was: thread_ble_msgrx_exit|" function_map.txt

# task_ring_msg_handler -> _thread_msg_handler
sed -i '' "s|^0x004bda68\t.*|0x004bda68\tFUN_004bda68\t_thread_msg_handler\ttask.ring\tHIGH\t# elog __FUNCTION__ match: PTR_s @ 0x004bdd14 # was: task_ring_msg_handler|" function_map.txt

# task_evenai_notify_handler -> _thread_notify_event_handler
sed -i '' "s|^0x004edc50\t.*|0x004edc50\tFUN_004edc50\t_thread_notify_event_handler\ttask.evenai\tHIGH\t# elog __FUNCTION__ match: PTR_s @ 0x004edfc8 # was: task_evenai_notify_handler|" function_map.txt

# task_evenai_thread_exit -> _thread_exit
sed -i '' "s|^0x004edcac\t.*|0x004edcac\tFUN_004edcac\t_thread_exit\ttask.evenai\tHIGH\t# elog __FUNCTION__ match: PTR_s @ 0x004edfd0 # was: task_evenai_thread_exit|" function_map.txt

# task_notif_notify_handler -> _thread_notify_event_handler
sed -i '' "s|^0x0052c1fc\t.*|0x0052c1fc\tFUN_0052c1fc\t_thread_notify_event_handler\ttask.notif\tHIGH\t# elog __FUNCTION__ match: PTR_s @ 0x0052c750 # was: task_notif_notify_handler|" function_map.txt

# task_notif_thread_exit -> _thread_exit
sed -i '' "s|^0x0052c292\t.*|0x0052c292\tFUN_0052c292\t_thread_exit\ttask.notif\tHIGH\t# elog __FUNCTION__ match: PTR_s @ 0x0052c758 # was: task_notif_thread_exit|" function_map.txt

# --- BLE / Cordio stack ---

# dmAdvStopDirected -> dmAdvActStop
# Only DAT_-based upgrade in this wave (binary-verified, at_start=True)
sed -i '' "s|^0x0049ce68\t.*|0x0049ce68\tFUN_0049ce68\tdmAdvActStop\tble.dm_adv\tHIGH\t# elog __FUNCTION__ match: DAT_0049d458 -> 0x002fcff0 (rizin) # was: dmAdvStopDirected|" function_map.txt

# --- Whitelist / service layer ---

# parseJsonWhitelistToStruct -> _parseJsonWhitelistToStruct
sed -i '' "s|^0x004ea65e\t.*|0x004ea65e\tFUN_004ea65e\t_parseJsonWhitelistToStruct\tsvc.whitelist\tHIGH\t# elog __FUNCTION__ match: PTR_s @ 0x004eb9e0 # was: parseJsonWhitelistToStruct|" function_map.txt

# printAppWhiteListInfo -> _printAppWhiteListInfo
sed -i '' "s|^0x004eac1c\t.*|0x004eac1c\tFUN_004eac1c\t_printAppWhiteListInfo\tsvc.whitelist\tHIGH\t# elog __FUNCTION__ match: PTR_s @ 0x004eba18 # was: printAppWhiteListInfo|" function_map.txt

# --- Protobuf service handlers ---

# pb_evenai_tx_encode_reply -> APP_PbNotifyEncodeEvenAIEvent
sed -i '' "s|^0x004efd78\t.*|0x004efd78\tFUN_004efd78\tAPP_PbNotifyEncodeEvenAIEvent\tpb.evenai\tHIGH\t# elog __FUNCTION__ match: PTR_s @ 0x004f08e4 # was: pb_evenai_tx_encode_reply|" function_map.txt

# --- Exit prompt UI ---

# exit_prompt_fade_step2 -> common_exit_prompt_fade_cb_step2
sed -i '' "s|^0x0056d90c\t.*|0x0056d90c\tFUN_0056d90c\tcommon_exit_prompt_fade_cb_step2\texit_prompt\tHIGH\t# elog __FUNCTION__ match: PTR_s @ 0x0056db24 # was: exit_prompt_fade_step2|" function_map.txt

# exit_prompt_fade_step1 -> common_exit_prompt_fade_cb_step1
sed -i '' "s|^0x0056d986\t.*|0x0056d986\tFUN_0056d986\tcommon_exit_prompt_fade_cb_step1\texit_prompt\tHIGH\t# elog __FUNCTION__ match: PTR_s @ 0x0056db38 # was: exit_prompt_fade_step1|" function_map.txt

# --- Conversate module ---

# conversate_fsm_action_config -> conversate_action_app_config
sed -i '' "s|^0x00593740\t.*|0x00593740\tFUN_00593740\tconversate_action_app_config\tconversate.fsm\tHIGH\t# elog __FUNCTION__ match: PTR_s @ 0x00593b28 # was: conversate_fsm_action_config|" function_map.txt

# conversate_timer_auto_extend -> conversate_timer_auto_extend_start
# PTR_s_ label truncated at 32 chars; full name from rizin_strings @ 0x002cf2b4
sed -i '' "s|^0x0059458e\t.*|0x0059458e\tFUN_0059458e\tconversate_timer_auto_extend_start\tconversate.timer\tHIGH\t# elog __FUNCTION__ match: PTR_s @ 0x00594ab8 (truncated, rizin-verified) # was: conversate_timer_auto_extend|" function_map.txt

# conversate_ui_event -> conversate_ui_title_container_create
# PTR_s_ label truncated at 32 chars; full name from rizin_strings @ 0x002c6798
sed -i '' "s|^0x0058f676\t.*|0x0058f676\tFUN_0058f676\tconversate_ui_title_container_create\tconversate.ui\tHIGH\t# elog __FUNCTION__ match: PTR_s @ 0x005902fc (truncated, rizin-verified) # was: conversate_ui_event|" function_map.txt

# conversate_tag_get_data_by_auto -> conversate_tag_get_data_by_auto_disp_node_prev
# PTR_s_ label truncated at 32 chars; full name from rizin_strings @ 0x002b3bc8
sed -i '' "s|^0x00540328\t.*|0x00540328\tFUN_00540328\tconversate_tag_get_data_by_auto_disp_node_prev\tconversate.tag\tHIGH\t# elog __FUNCTION__ match: PTR_s @ 0x005404fc (truncated, rizin-verified) # was: conversate_tag_get_data_by_auto|" function_map.txt

# --- EasyLogger internal ---

# elog_async_file_store_init -> elog_async_ext_flieStore_Init
# Note: "flie" is a typo in the firmware source code (should be "file")
# The __FUNCTION__ macro preserves the typo from the original C function name
sed -i '' "s|^0x00447606\t.*|0x00447606\tFUN_00447606\telog_async_ext_flieStore_Init\telog.async\tHIGH\t# elog __FUNCTION__ match: PTR_s @ 0x00447774 (source typo: flie not file) # was: elog_async_file_store_init|" function_map.txt

echo "Applied 24 elog __FUNCTION__ upgrades (Wave 2) to function_map.txt"
