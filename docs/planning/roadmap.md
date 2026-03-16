# openCFW Cleanup Plan

## Goal
Systematically remove placeholder, decompiler-derived, Rizin/Ghidra-style, or otherwise generic names and strings under `openCFW/` until the repo-owned tree no longer contains unidentified variables, functions, parameters, return values, struct-field comments, misleading string labels, or evidence-backed entries that still live in `_unclassified.c` instead of a concrete destination file.

## Scope Rules
- Focus on repo-owned code under `openCFW/src/`.
- Exclude bundled `third_party/` content unless the cleanup scope is explicitly expanded later.
- `_unclassified.c` files are in scope as migration backlogs, not permanent exclusions.
- When a function, helper, data block, or comment in `_unclassified.c` has enough evidence to place it in a concrete source file, move it there in the same wave and remove the dump copy.
- Rename or move entries only when surrounding code, callers, strings, tables, data layout, or protocol behavior provide enough evidence to justify the result.
- Treat stale comments, anonymous field-offset notes, and misleading string labels as part of the same cleanup queue, not as a separate polish pass.

## Per-Wave Workflow
- Scan the backlog and choose one bounded subsystem or destination-file cluster.
- Rename placeholders, decompiler artifacts, weak helper names, vague parameter names, vague return-value names, stale comments, and misleading labels that have clear local evidence.
- Triage any nearby `_unclassified.c` entries that now have an obvious owning file, move them into that file, and delete the dump copy.
- Re-scan the touched files plus the `_unclassified.c` inventory to see what still remains.
- Run lightweight validation on touched files when feasible, and record any pre-existing translation-unit recovery blockers instead of treating them as cleanup regressions.
- Rewrite this file after each wave so it always reflects only the remaining actionable backlog.

## Verification / CI Expectations
- Run the broad placeholder scan against repo-owned `openCFW/src/` after each wave.
- Run targeted follow-up searches for stale comments, struct-field notes, misleading labels, leftover wrapper/decompiler naming, and any moved `_unclassified.c` symbol names that should no longer remain in the dump file.
- Use `clang -std=gnu89 -fsyntax-only` on touched files when the translation unit is recoverable enough for a meaningful probe.
- Treat a wave as incomplete if the touched scope still has evidence-backed rename, comment, string-label, or `_unclassified.c` migration opportunities after the rescan.

## Current Baseline
Waves 34-53 completed the remaining repo-owned normal-source placeholder
cleanup plus the next evidence-backed main-firmware and bootloader owner
migrations:
- Moved the box-detect protobuf RX / notify / display helper cluster into
  `openCFW/src/platform/apollo510b/main_firmware/platform/service/box_detect/service_box_detect.c`,
  recovering `APP_PbRxGlassesCaseFrameDataProcess`,
  `box_detect_send_case_state_notify(...)`, and
  `box_detect_enqueue_display_message(...)` from
  `openCFW/src/platform/apollo510b/main_firmware/_unclassified.c`.
- Renamed the stale full-state copier to
  `box_detect_copy_full_state(...)`, updated the product-test caller in
  `openCFW/src/platform/apollo510b/main_firmware/platform/product_test/pt_protocol_procsr.c`,
  rebound the display-message payload pack in `DEV_BoxDetectMsgProcess(...)`
  onto the actual masked status word, and cleared the last `local_*`
  scratch names in the peer-merge path.
- Cleared the final normal-source placeholder tail in
  `openCFW/src/peripherals/touch_controller/capsense/capsense_core.c` by
  renaming `capsense_set_param_if_unset(int config_id, ...)` and aligning its
  forward declaration.
- Retired the duplicate teleprompter protobuf owner slice from
  `openCFW/src/platform/apollo510b/main_firmware/_unclassified.c` now that
  `APP_PbRxTelepromptFrameDataProcess`,
  `APP_PbTelepromptTxEncodeCommResp`,
  `APP_PbTxEncodeStatusNotify`,
  `APP_PbTxEncodeFileListRequest`,
  `APP_PbTxEncodeFileSelect`,
  `APP_PbTxEncodePageDataRequest`, and
  `APP_PbTxEncodeScrollSync` already live in
  `openCFW/src/platform/apollo510b/main_firmware/platform/protocols/pb_teleprompter_handler.c`.
- Restored the missing standard `stdint.h` / `string.h` includes in
  `pb_teleprompter_handler.c`, narrowing its standalone syntax failure to the
  remaining recovered-header / extern gap instead of basic C type / libc
  fallout.
- Retired the duplicate notification / health / conversate / ring /
  translate protobuf owner slices from
  `openCFW/src/platform/apollo510b/main_firmware/_unclassified.c`, leaving
  `APP_PbRxNotificationFrameDataProcess`,
  `APP_PbTxEncodeNotifCtrl`,
  `APP_PbTxEncodeNotifCommResp`,
  `APP_PbTxEncodeNotifAppIDNotInWhitelist`,
  `APP_PbTxEncodeNotifWhitelistCtrl`,
  `APP_PbRxHealthFrameDataProcess`,
  `APP_PbTxEncodeHealthSingleData`,
  `APP_PbTxEncodeHealthMultData`,
  `APP_PbTxEncodeHealthSingleHighlight`,
  `APP_PbTxEncodeHealthMultHighlight`,
  `APP_PbConversateTxEncodeNotify`,
  `APP_PbConversateTxEncodeCommResp`,
  `APP_PbRxRingFrameDataProcess`,
  `APP_PbTxEncodeRingEvent`,
  `APP_PbTranslateTxEncodeNotify`,
  `APP_PbTranslateTxEncodeCommResp`, and
  `APP_PbTranslateTxEncodeModeSwitch` owned solely by
  `platform/protocols/pb_notification_handler.c`,
  `platform/protocols/pb_health_handler.c`,
  `platform/protocols/pb_conversate_handler.c`,
  `platform/protocols/pb_ring_handler.c`, and
  `platform/protocols/pb_translate_handler.c`.
- Restored the missing standard `stdint.h` / `string.h` includes in those
  five protobuf owner files, narrowing their standalone syntax failures past
  basic fixed-width type / libc fallout and onto the still-missing shared
  protocol headers and extern layers.
- Targeted rescans now show `0` broad-placeholder hits in the touched
  owner files plus `capsense_core.c`. The repo-owned normal-source sweep,
  excluding `_unclassified.c` and bundled `third_party/`, still returns `0`
  placeholder / decompiler-name matches overall.
- The retired box-detect dump symbols
  `APP_PbRxGlassesCaseFrameDataProcess`, `DEV_ThreadInit`, and
  `DEV_SendMessage` no longer appear in
  `openCFW/src/platform/apollo510b/main_firmware/_unclassified.c`. The
  remaining actionable backlog is now `_unclassified.c` placement / ABI
  recovery plus the pre-existing translation-unit blockers.
- The retired teleprompter handler start-address comments
  `0x0054ca54` / `0x0054ccaa` / `0x0054cd8a` / `0x0054ce70` /
  `0x0054cf56` / `0x0054d034` / `0x0054d102` no longer appear in
  `openCFW/src/platform/apollo510b/main_firmware/_unclassified.c`; the lone
  remaining `APP_PbTxEncodeStatusNotify(...)` mention there is now just the
  live `Teleprompt_ui_event_handler(...)` caller rather than a duplicate dump
  copy.
- The retired notification / health / conversate / ring / translate
  start-address comments `0x004ebb9c` / `0x004ebe76` / `0x004ec00c` /
  `0x004ec190` / `0x004ec450` / `0x00569edc` / `0x0056a28e` /
  `0x0056a5a0` / `0x0056a904` / `0x0056abf8` / `0x00592fde` /
  `0x0059314c` / `0x005b41fc` / `0x005b4506` / `0x005b49c2` /
  `0x005b4b30` / `0x005b4ca2` no longer appear in
  `openCFW/src/platform/apollo510b/main_firmware/_unclassified.c`; the
  remaining `APP_PbRxNotificationFrameDataProcess(...)`,
  `APP_PbRxRingFrameDataProcess(...)`, and
  `APP_PbTranslateTxEncodeNotify(...)` mentions there are now just live
  callers rather than duplicate dump copies.
- The separate decompiler-token sweep, again excluding `_unclassified.c` and
  bundled `third_party/`, still returns no `FUN_`, `DAT_`, `LAB_`, numeric
  `param_*`, or address-suffixed `g_*` tokens in normal-source files.
- Moved the shared display-owner tail
  `teleprompter_build_text_view(...)` and `display_subsystem_init(...)` into
  `openCFW/src/platform/apollo510b/main_firmware/app/gui/common/display_common.c`,
  replacing the placeholder comment stubs there with concrete recovered
  implementations from `_unclassified.c`.
- Removed the stale quicklist-only duplicate helpers from
  `display_common.c`, leaving `display_config_region_type_lookup(...)` and
  `display_config_region_name(...)` owned solely by
  `platform/protocols/pb_quicklist_handler.c` and
  `gui_quicklist_data_manager_log_handler(...)` owned solely by
  `app/gui/quicklist/quicklist_ui_widgets.c`.
- Retired the duplicate dump copies of `common_ui_get_scroll_y(...)`,
  `teleprompter_build_text_view(...)`, `common_exit_prompt_show(...)`,
  `common_fade_in_animation(...)`, `common_fade_out_animation(...)`,
  `gui_quicklist_data_manager_log_handler(...)`, and
  `display_subsystem_init(...)` from
  `openCFW/src/platform/apollo510b/main_firmware/_unclassified.c`.
- Targeted rescans now show the retired display / quicklist owner symbols no
  longer appear in `_unclassified.c`, and `display_common.c` no longer
  contains the stale `display_config_region_type_lookup(...)`,
  `display_config_region_name(...)`,
  `gui_quicklist_data_manager_log_handler(...)`, or
  `APP_PbRxHealthFrameDataProcess` dump marker.
- Retired the duplicate `_unclassified.c` copies of `slave_uart_init(...)`,
  `slave_uart_send(...)`, and `slave_uart_config_baudrate(...)` in favor of
  the recovered inter-eye UART owner slice in
  `openCFW/src/platform/apollo510b/main_firmware/comms/slave_inter_eye.c`.
- Retired the remaining `_unclassified.c` copies of
  `slave_get_display_mode(...)`, `slave_frame_extract_payload(...)`,
  `slave_set_display_mode(...)`, `slave_display_cmd_complete(...)`,
  `slave_display_cmd_init(...)`, `slave_cmd_extract_pipe(...)`,
  `slave_cmd_reset(...)`, `slave_audio_route_cmd(...)`, and
  `slave_get_ring_state(...)` in favor of the recovered inter-eye display /
  routing owner slice in
  `openCFW/src/platform/apollo510b/main_firmware/comms/slave_inter_eye.c`.
- Retired the `_unclassified.c` queue/helper dump copies at `0x004775f4`,
  `0x004777ac`, `0x00477a48`, `0x00477b08`, `0x00477b2c`, `0x00477b66`,
  `0x00477b7a`, `0x00486b54`, `0x00486c2a`, and `0x00487516`, leaving their
  recovered `rtos_queue_*`, `task_nv_*`, `rtos_queue_get_highest_waiter_priority(...)`,
  `prvCopyDataToQueue(...)`, and task-init/signal helper names in
  `openCFW/src/platform/apollo510b/main_firmware/rtos/rtos_cmsis_wrappers.c`.
- Targeted rescans show the retired inter-eye display / routing
  start-address comments `0x00495d2c`, `0x00495e08`, `0x00495fd8`,
  `0x00496022`, `0x00496046`, `0x0049606c`, `0x00496072`, `0x00496894`,
  and `0x00496bd2` no longer appear in
  `openCFW/src/platform/apollo510b/main_firmware/_unclassified.c`; the lone
  remaining `slave_get_display_mode(...)` mention there is now just the live
  `auth_send_response(...)` caller rather than a duplicate dump definition.
- Targeted rescans show those retired start-address comments no longer appear
  in `openCFW/src/platform/apollo510b/main_firmware/_unclassified.c`; the
  remaining `rtos_cmsis_event_flags(...)`,
  `task_init_entry_critical(...)`, and
  `slave_uart_config_baudrate(...)` mentions there are now just live callers
  rather than duplicate dump definitions.
- Moved the stranded EvenAI heartbeat-arm helper out of
  `openCFW/src/platform/apollo510b/main_firmware/_unclassified.c` into
  `openCFW/src/platform/apollo510b/main_firmware/app/gui/EvenAI/even_ai.c`,
  renaming `task_queue_enqueue_sub(...)` to
  `even_ai_heartbeat_timer_mgr_start(...)` so it matches the `even_g`
  heartbeat timer state machine already owned by the EvenAI GUI code.
- Renamed the misidentified `0x004ee30c` heartbeat poller in
  `openCFW/src/platform/apollo510b/main_firmware/app/gui/EvenAI/even_ai.c`
  to `even_ai_heartbeat_timer_mgr_poll_expiry(...)`, and rebound
  `openCFW/src/platform/apollo510b/main_firmware/platform/service/evenAI/service_even_ai.c`
  onto the recovered owner slice with
  `EVENAI_HEARTBEAT_TIMEOUT_WINDOW` /
  `even_ai_heartbeat_timer_mgr_start(...)` naming instead of the stale
  queue-oriented wrapper name.
- Retired the duplicate EvenAI dump copies of `evenai_state_lock(...)`,
  `evenai_state_unlock(...)`, `EvenAI_InputEventWarp(...)`, and
  `task_queue_enqueue_sub(...)` from
  `openCFW/src/platform/apollo510b/main_firmware/_unclassified.c`.
- Targeted rescans show the retired EvenAI start-address comments
  `0x004edb40`, `0x004edb58`, `0x004ee2a4`, and `0x00598970` no longer
  appear in
  `openCFW/src/platform/apollo510b/main_firmware/_unclassified.c`.
- Cleaned the navigation startup / mode-select compass-start reflash path in
  `openCFW/src/platform/apollo510b/main_firmware/app/gui/navigation/navigation_ui.c`
  by replacing the anonymous `reflash_param_*` scratch bytes with a named
  `compass_start_reflash_cmd[...]` frame and a shared
  `NAV_UI_REFLASH_CMD_SIZE` constant, so the two
  `RequestDisplayReflash(..., 6, 0)` call sites now describe the actual
  six-byte command payload instead of five unlabeled trailing locals.
- Renamed the stale settings helpers
  `setting_respond_with_local_data(...)` and
  `setting_respond_with_local_data_serialize(...)` in
  `openCFW/src/platform/apollo510b/main_firmware/app/gui/setting/setting.c`
  to `setting_respond_with_status_snapshot(...)` and
  `setting_serialize_status_snapshot_response(...)`, and rebound the touched
  response-path elog references onto file-local `STATUS_SNAPSHOT` aliases so
  the owner slice now matches the surrounding device-status terminology.
- Targeted rescans now show `0` remaining `reflash_param_*` hits in
  `navigation_ui.c` and `0` remaining
  `setting_respond_with_local_data*` hits in `setting.c`.
- The post-wave lower-case heuristic sweep now narrows to the EvenAI
  `local_data` callback / log identifiers in
  `openCFW/src/platform/apollo510b/main_firmware/platform/service/evenAI/service_even_ai.c`.
  Re-triage against the recovered `STR_EvenAI_*local_data*` symbols and the
  live `pb_service_even_ai.c` call sites keeps those names as
  evidence-backed source / protocol terminology rather than cleanup residue,
  so the remaining actionable backlog stays `_unclassified.c` placement /
  ABI recovery plus the pre-existing translation-unit blockers.
- This turn explicitly continued from the regenerated
  `split_firmware.py` output after user confirmation, clearing the prior
  workspace-integrity blocker and re-baselining the live `_unclassified.c`
  counts below against the regenerated split tree.
- Re-retired the regenerated quicklist protobuf / display-config duplicate
  owner slice from
  `openCFW/src/platform/apollo510b/main_firmware/_unclassified.c`, leaving
  `APP_PbRxQuicklistFrameDataProcess`,
  `APP_DecodePbRxQuicklistData`,
  `APP_PbTxEncodeQuicklistItem`,
  `APP_PbTxEncodeQuicklistMultItems`,
  `APP_PbNotifyEncodeQuicklistMultItems`,
  `APP_PbTxEncodeQuicklistEvent`,
  `APP_PbNotifyEncodeQuicklistEvent`,
  `display_config_region_type_lookup(...)`, and
  `display_config_region_name(...)` owned solely by
  `openCFW/src/platform/apollo510b/main_firmware/platform/protocols/pb_quicklist_handler.c`.
- Targeted rescans now show the retired quicklist symbols and start-address
  comments `0x005684d8` / `0x005686c8` / `0x0056892a` / `0x00568b8a` /
  `0x00568d3c` / `0x00568ffc` / `0x00569198` / `0x005693c2` /
  `0x005693e0` no longer appear in
  `openCFW/src/platform/apollo510b/main_firmware/_unclassified.c`, while
  the broad normal-source decompiler-token sweep still returns `0` hits
  outside `_unclassified.c` and bundled `third_party/`.
- Moved the missing bootloader LittleFS event-loop rate helper
  `fw_evt_loop_default_handler(...)` into
  `openCFW/src/platform/apollo510b/bootloader/littlefs/port/fw_evt_loop.c`,
  leaving the full recovered `fw_evt_loop_*` owner slice there instead of
  split across `_unclassified.c`.
- Rebound the bootloader LittleFS bootstrap call sites in
  `openCFW/src/platform/apollo510b/bootloader/littlefs/port/littlefs_porting.c`
  onto the recovered owner `littlefs_ensure_boot_directories(void)` in
  `littlefs_bootstrap.c`, then retired the stale `0x00421048`
  `check_and_create_directories_1048(...)` dump copy from
  `openCFW/src/platform/apollo510b/bootloader/_unclassified.c`.
- Retired the duplicate bootloader LittleFS event-loop dump copies of
  `fw_evt_loop_memset_zero(...)`, `fw_evt_loop_default_handler(...)`,
  `fw_evt_loop_queue_init(...)`, `fw_evt_loop_timer_create(...)`,
  `fw_evt_loop_thread_flags_wait(...)`, `fw_evt_loop_dispatch_event(...)`,
  `fw_evt_loop_timer_start(...)`, `fw_evt_loop_push_to_queue(...)`,
  `fw_evt_loop_push(...)`, `fw_evt_loop_timer_callback(...)`,
  `fw_evt_loop_task(...)`, `fw_evt_loop_init(...)`,
  `fw_evt_loop_register_handler(...)`, `fw_evt_loop_unregister_handler(...)`,
  `fw_evt_loop_set_filter(...)`, `fw_evt_loop_get_current_event(...)`,
  `fw_evt_loop_push_delayed(...)`, `fw_evt_loop_remove_delayed(...)`,
  `fw_evt_loop_push_urgent(...)`, `fw_evt_loop_create_worker(...)`,
  `fw_evt_loop_destroy(...)`, `fw_evt_loop_is_running(...)`,
  `fw_evt_loop_flush_pending(...)`, `fw_evt_loop_set_priority(...)`,
  `fw_evt_loop_get_pending_count(...)`, `fw_evt_loop_timer_stop(...)`,
  `fw_evt_loop_timer_restart(...)`, `fw_evt_loop_send_sync(...)`,
  `fw_evt_loop_alloc_event(...)`, `fw_evt_loop_free_event(...)`,
  `fw_evt_loop_broadcast(...)`, `fw_evt_loop_subscribe(...)`,
  `fw_evt_loop_unsubscribe(...)`, `fw_evt_loop_wait_for(...)`, and
  `fw_evt_loop_peek(...)` from
  `openCFW/src/platform/apollo510b/bootloader/_unclassified.c`.
- Targeted rescans now show the retired bootloader LittleFS event-loop
  start-address comments `0x00426b5c` / `0x00426b70` / `0x00426ba4` /
  `0x00426bbe` / `0x00426bd8` / `0x00426c18` / `0x00426c6a` /
  `0x00426c94` / `0x00426d00` / `0x00426df8` / `0x00426eb8` /
  `0x00426f8c` / `0x004270ac` / `0x004271f8` / `0x0042725c` /
  `0x004272ac` / `0x00427328` / `0x00427358` / `0x0042746e` /
  `0x00427536` / `0x0042754e` / `0x004275ac` / `0x00427608` /
  `0x004276a0` / `0x004276e0` / `0x004277c4` / `0x00427814` /
  `0x00427856` / `0x0042790a` / `0x0042793c` / `0x004279a2` /
  `0x00427a22` / `0x00427a84` / `0x00427af6` / `0x00427b5e` no longer
  appear in `openCFW/src/platform/apollo510b/bootloader/_unclassified.c`;
  the remaining `fw_evt_loop_memset_zero(...)` and
  `fw_evt_loop_default_handler(...)` mentions there are now just live callers
  rather than duplicate dump definitions.
- Moved the case-MCU GLS-detect / YHM2510 / UART helper cluster out of
  `openCFW/src/peripherals/case_mcu/_unclassified.c`, placing
  `reset_all_gls_counters()` in
  `openCFW/src/peripherals/case_mcu/power/battery.c`,
  `init_pmic_gpio_and_yhm2510()` and `dump_yhm2510_regs()` in
  `openCFW/src/peripherals/case_mcu/diagnostics/self_check.c`,
  `restart_led_timer_1s()` and `glasses_detect_ir_scan()` in
  `openCFW/src/peripherals/case_mcu/app/main_task.c`,
  `check_debug_prefix_de()` in
  `openCFW/src/peripherals/case_mcu/driver/uart.c`, and
  `backup_yhm2510_regs()` in
  `openCFW/src/peripherals/case_mcu/driver/fuel_gauge.c`.
- Targeted rescans now show those retired case-MCU dump symbols no longer
  appear in `openCFW/src/peripherals/case_mcu/_unclassified.c`; the remaining
  nearby `gls_l_toggle_5v_on_aging()` helper stays there only because its
  call into `gpio_set_gls_l_5v(...)` still has unrecovered ABI / owner
  ambiguity.
- Retired the duplicate UX settings dump copies of
  `settings_get_state_ptr()`, `UX_LocalSystemStatusSyncHandler(...)`,
  `ux_setting_init_display_options()`, `ux_setting_apply_locale(...)`, and
  `UX_BatterySyncHandler(...)` from
  `openCFW/src/platform/apollo510b/main_firmware/_unclassified.c`, leaving
  that owner slice solely in
  `openCFW/src/platform/apollo510b/main_firmware/system/ux_settings.c`.
- Retired the adjacent duplicate OTA ring-state dump copies
  `ota.service_4760ba()` and `ota.service_4760c4()` from
  `openCFW/src/platform/apollo510b/main_firmware/_unclassified.c`, leaving
  the ring-state accessors owned solely by
  `openCFW/src/platform/apollo510b/main_firmware/firmware/ota_update.c` as
  `ota_get_active_flag()` and `ota_get_ready_status()`.
- Removed the stale `ux_settings.c` file-header line-range note now that the
  `_unclassified.c` offsets for that recovered owner slice are no longer
  stable after retiring the duplicate dump copy.
- Targeted rescans now show the retired UX settings / OTA start-address
  comments `0x00467254` / `0x00475a00` / `0x00476078` / `0x004760ba` /
  `0x004760c4` / `0x004ccd14` / `0x005d630c` no longer appear in
  `openCFW/src/platform/apollo510b/main_firmware/_unclassified.c`; the
  remaining `settings_get_state_ptr()` mentions there are now just live
  callers rather than duplicate dump definitions.
- Retired the duplicate bootloader DFU runtime / thread-manager dump copies
  from `openCFW/src/platform/apollo510b/bootloader/_unclassified.c`, leaving
  `dfu_select_open_mode(...)`, `dfu_get_config()`,
  `app_dfu_image_crc_check(...)`, `dfu_flash_erase_range(...)`,
  `dfu_verify_flash_content(...)`, `app_dfu_system_program(...)`,
  `dfu_task_msg_send(...)`, `thread_dfu_task(...)`,
  `dfu_init_config()`, `dfu_create_message_queue()`,
  `dfu_noop_callback()`, `dfu_sync_start()`, `dfu_sync_end()`,
  `dfu_pre_jump_deinit()`, `bootloader_error_reset()`,
  `dfu_process_task_message()`, `dfu_event_dispatch()`, `dfu_error_halt()`,
  `crc32_update()`, and the bootloader `thread_manager_*` owner slice
  solely in `openCFW/src/platform/apollo510b/bootloader/dfu/dfu_core.c`,
  `openCFW/src/platform/apollo510b/bootloader/dfu/dfu_task.c`,
  `openCFW/src/platform/apollo510b/bootloader/threads/thread_manager.c`,
  and `openCFW/src/platform/apollo510b/bootloader/boot/bootloader.c`,
  with the renamed update-flag helper now owned as
  `thread_manager_needs_update_image(void)`.
- Cleaned the recovered bootloader DFU / thread-manager semantic tail in
  `openCFW/src/platform/apollo510b/bootloader/dfu/dfu_core.c`,
  `openCFW/src/platform/apollo510b/bootloader/dfu/dfu_task.c`,
  `openCFW/src/platform/apollo510b/bootloader/threads/thread_manager.c`,
  and `openCFW/src/platform/apollo510b/bootloader/boot/bootloader.c` by
  rebinding the OTA path / open-mode / runtime-context labels onto
  `dfu_ota_image_path`, `dfu_open_mode_{a-f}`,
  `dfu_task_runtime_{config,ctx}`, `dfu_install_{begin,progress,complete}_fmt`,
  and `dfu_verify_buffer`, renaming the stale helpers to
  `dfu_select_open_mode(...)`, `dfu_verify_flash_content(...)`, and
  `dfu_process_task_message()`, renaming the thread-manager OTA flag / runtime
  globals to `thread_mgr_ota_flag_ptr` / `thread_mgr_runtime_ctx`, and
  replacing the decompiler-only `boot_jump_to_app(int)` handoff cast with the
  concrete `SCB->VTOR` register write plus typed reset-vector call in
  `bootloader.c`.
- Targeted rescans now show the retired owner-file names
  `dfu_get_ota_path`, `_verifyFlashContent`, `_thread_msg_handler`,
  `thread_mgr_dfu_thread_ptr`, `thread_mgr_ctx`, `thread_mgr_config_a`,
  `dfu_verify_result_str`, `dfu_task_str_a`, `dfu_task_str_b`,
  `dfu_task_config_a`, `dfu_config_e`, `dfu_config_f`, `dfu_verify_fmt`,
  `dfu_verify_str`, `_scb_vtor`, and the decompiler-era `code **` handoff
  cast no longer appear in the touched bootloader owner files, and the
  touched owner slice no longer contains `param*` / `p*` placeholders.
- Targeted rescans now show the retired bootloader DFU / thread-manager
  start-address comments `0x0042d798` / `0x0042d7d6` / `0x0042d7dc` /
  `0x0042d93c` / `0x0042d96a` / `0x0042da34` / `0x0042dbee` /
  `0x0042dc60` / `0x0042dcb4` / `0x0042dcbc` / `0x0042dce4` /
  `0x0042dce6` / `0x0042dcf0` / `0x0042dd3e` / `0x0042dd5a` /
  `0x0042dda4` / `0x0042e110` / `0x0042e126` / `0x0042e138` /
  `0x0042e170` / `0x0042e1a0` / `0x0042e1c2` / `0x0042e1c4` /
  `0x0042e1d0` / `0x0042e1ee` / `0x0042e236` / `0x0042e244` /
  `0x0042e2e6` / `0x0042e2e8` / `0x0042e316` / `0x0042e32c` /
  `0x0042e35e` / `0x0042e390` / `0x0042e3ec` no longer appear in
  `openCFW/src/platform/apollo510b/bootloader/_unclassified.c`; the retired
  symbol names `dfu_get_ota_path`, `dfu_task_msg_send`, `thread_dfu_task`,
  `dfu_event_dispatch`, and `thread_manager_error_log` no longer appear
  there either.
- The broad normal-source decompiler-token sweep, again excluding
  `_unclassified.c` and bundled `third_party/`, still returns no `FUN_`,
  `DAT_`, `LAB_`, numeric `param_*`, or address-suffixed `g_*` tokens.
- Retired the duplicate common list / text widget owner slice from
  `openCFW/src/platform/apollo510b/main_firmware/_unclassified.c`, leaving
  `list_container_calc_item_y(...)`, `get_color_from_index(...)`,
  `list_container_deselect_current(...)`,
  `list_container_update_item_styles(...)`,
  `list_container_calc_scroll_offset(...)`,
  `common_list_scroll_anim_complete_cb(...)`,
  `common_list_rubber_band_anim_cb(...)`,
  `common_list_trigger_rubber_band(...)`,
  `list_container_process_pending(...)`,
  `list_container_scroll_to_top_anim(...)`, `common_list_create(...)`,
  `common_list_destroy(...)`, `common_list_inject_event(...)`,
  `common_text_create(...)`, `common_text_destroy(...)`,
  `common_text_update_scroll_state(...)`,
  `common_text_calc_line_height(...)`,
  `common_text_scroll_anim_exec_cb(...)`,
  `common_text_scroll_anim_complete_cb(...)`,
  `common_text_scroll_with_anim(...)`,
  `common_text_rubber_band_anim_complete_cb(...)`,
  `common_text_trigger_rubber_band(...)`,
  `common_text_try_extend_animation(...)`, and
  `common_text_inject_event(...)` owned solely by
  `openCFW/src/platform/apollo510b/main_firmware/app/gui/common/display_common.c`.
- Targeted rescans now show the retired common list / text dump-address
  comments `0x0058aa2a` through `0x0058e05c` no longer appear in
  `openCFW/src/platform/apollo510b/main_firmware/_unclassified.c`, while the
  concrete owner slice remains present in `display_common.c`.
- Re-retired the regenerated ring / translate protobuf duplicate owner slice
  from `openCFW/src/platform/apollo510b/main_firmware/_unclassified.c`,
  leaving `APP_PbRxRingFrameDataProcess`,
  `APP_PbTxEncodeRingEvent`,
  `RingDataRelay_common_data_handler`,
  `APP_PbTranslateTxEncodeNotify`,
  `APP_PbTranslateTxEncodeCommResp`, and
  `APP_PbTranslateTxEncodeModeSwitch` owned solely by
  `openCFW/src/platform/apollo510b/main_firmware/platform/protocols/pb_ring_handler.c`
  and
  `openCFW/src/platform/apollo510b/main_firmware/platform/protocols/pb_translate_handler.c`.
- Moved the stranded translate UI owner
  `Translate_ui_event_handler(...)` into
  `openCFW/src/platform/apollo510b/main_firmware/app/gui/translate/translate_ui.c`,
  restored the missing standard `stdbool.h` / `stdint.h` / `string.h`
  includes there, and retired the matching dump copy from
  `openCFW/src/platform/apollo510b/main_firmware/_unclassified.c`.
- Targeted rescans now show the retired ring / translate / translate-UI
  start-address comments `0x005b41fc` / `0x005b4506` / `0x005b46b0` /
  `0x005b49c2` / `0x005b4b30` / `0x005b4ca2` / `0x005ca026` no longer
  appear in
  `openCFW/src/platform/apollo510b/main_firmware/_unclassified.c`; the
  retired owner names likewise no longer appear there.
- Retired the duplicate bootloader HAL I2C owner slice from
  `openCFW/src/platform/apollo510b/bootloader/_unclassified.c`, leaving
  `HAL_I2CInit(...)` and `HAL_I2CTransfer(...)` owned solely by
  `openCFW/src/platform/apollo510b/bootloader/hal/hal_i2c.c`.
- Retired the duplicate bootloader MSPI timing owner slice from
  `openCFW/src/platform/apollo510b/bootloader/_unclassified.c`, leaving
  `mspi_timing_scan_txneg(...)`, `mspi_timing_scan_rxneg(...)`,
  `mspi_timing_scan_rxcap(...)`, `mspi_timing_scan_turnaround(...)`,
  `mspi_timing_set_default(...)`, `mspi_timing_apply(...)`,
  `mspi_timing_validate(...)`, `mspi_timing_scan_pass_check(...)`,
  `mspi_timing_scan_window(...)`, `mspi_timing_scan_center(...)`,
  `mspi_timing_scan_result(...)`, `mspi_timing_scan_iterate(...)`,
  `mspi_timing_check(...)`, and `mspi_timing_auto_check(...)` owned solely
  by
  `openCFW/src/platform/apollo510b/bootloader/hal/norflash_timing.c`.
- Targeted rescans now show the retired bootloader HAL / MSPI timing
  start-address comments `0x0041df20`, `0x0041df9e`, `0x0041fdba`,
  `0x0041fde2`, `0x0041fe04`, `0x0041fe24`, `0x0041fe3e`, `0x0041fe78`,
  `0x0041feb0`, `0x0041fee4`, `0x0041fefa`, `0x0041ff10`, `0x0041ff3c`,
  `0x0041ff50`, `0x0041ffde`, and `0x00420196` no longer appear in
  `openCFW/src/platform/apollo510b/bootloader/_unclassified.c`; the
  remaining `mspi_timing_*` mentions there are now just live callers rather
  than duplicate dump definitions.

Current `_unclassified.c` migration backlog:
- `openCFW/src/platform/apollo510b/main_firmware/_unclassified.c` (`69527` lines)
- `openCFW/src/platform/apollo510b/bootloader/_unclassified.c` (`6162` lines)
- `openCFW/src/peripherals/case_mcu/_unclassified.c` (`1812` lines)
- `openCFW/src/peripherals/touch_controller/_unclassified.c` (`8` lines, empty stub)

Syntax-only probes in these waves:
- `openCFW/src/platform/apollo510b/bootloader/hal/hal_i2c.c` and
  `openCFW/src/platform/apollo510b/bootloader/hal/norflash_timing.c` now
  pass bare `clang -std=gnu89 -fsyntax-only` probes after the duplicate dump
  retirement wave, so the bootloader HAL I2C / MSPI timing owner slices are
  now validated in their concrete owner files instead of also living in
  `_unclassified.c`.
- The touched case-MCU owner files (`power/battery.c`,
  `diagnostics/self_check.c`, `app/main_task.c`, `driver/uart.c`, and
  `driver/fuel_gauge.c`) still fail under bare
  `clang -std=gnu89 -fsyntax-only` probes because their recovered
  translation units still lack the shared typedef / extern preamble that
  defines `bool`, `byte`, `ushort`, `uint{8,16,32}_t`, the CMSIS-RTOS entry
  points, and the surrounding GPIO / debug / YHM2510 globals; the failure
  remains translation-unit recovery fallout rather than a regression from
  the helper migrations landed in this wave.
- `display_common.c` still fails under a bare
  `clang -std=gnu89 -fsyntax-only` probe because the recovered translation
  unit still lacks the shared GUI / LVGL / standard-type header layer that
  defines `uint{8,16,32,64}_t`, `int16_t`, `byte`, and the surrounding extern
  declarations; the failure remains translation-unit recovery fallout rather
  than a regression from the moved display-owner helpers or the retired
  common list / text widget owner slice.
- `slave_inter_eye.c` still fails under a bare
  `clang -std=gnu89 -fsyntax-only` probe because the recovered translation
  unit still lacks the shared type / extern layer that defines `bool`,
  `byte`, `appdb_active_record`, and the surrounding WSF / device-manager /
  memcpy helper declarations; the failure remains translation-unit recovery
  fallout rather than a regression from retiring the dump copies.
- `rtos_cmsis_wrappers.c` still fails under a bare
  `clang -std=gnu89 -fsyntax-only` probe because the recovered translation
  unit still lacks the shared standard-type and RTOS / EasyLogger header
  layer that defines `uint{16,32,64}_t`, `bool`, `elog_ringbuf_data`, and the
  surrounding kernel helper declarations; the failure remains translation-unit
  recovery fallout rather than a regression from retiring the dump copies.
- The touched RTOS wrapper caller files
  (`rtos/freertos_queues.c`, `platform/threads/thread_ble_wsf.c`,
  `platform/audio/service_codec_host.c`, and
  `driver/uled/drv_mspi_uled_common.c`) still fail under bare
  `clang -std=gnu89 -fsyntax-only` probes because their recovered translation
  units still lack the shared standard-type / macro layer that defines
  `uint`, `uint8_t`, `uint32_t`, `uint64_t`, and `MERGE_4_4`, plus the
  surrounding queue / BLE / audio / MSPI helper declarations; the failure
  remains translation-unit recovery fallout rather than a regression from
  rebinding the RTOS wrapper call sites onto their recovered owner names.
- `even_ai.c` still fails under a bare `clang -std=gnu89 -fsyntax-only`
  probe because the recovered translation unit still lacks the shared EvenAI
  GUI / service extern layer that declares `even_ai_timer_ctx_ptr`, `even_g`,
  `even_widget`, the EvenAI elog strings/tags, the LVGL helpers, and the
  surrounding protobuf / BLE helpers such as
  `APP_PbNotifyEncodeEvenAIEvent(...)`, `SVC_EvenAICtrl(...)`,
  `ble_connection_state_check(...)`, and `timer_check_elapsed(...)`; the
  failure remains translation-unit recovery fallout rather than a regression
  from moving the heartbeat helper into its owner file.
- `service_even_ai.c` still fails under a bare
  `clang -std=gnu89 -fsyntax-only` probe because the recovered translation
  unit still lacks the shared EvenAI protocol header layer that defines
  `byte` and the surrounding state-buffer / elog / BLE helper declarations;
  the failure remains translation-unit recovery fallout rather than a
  regression from rebinding the heartbeat timer owner call.
- `navigation_ui.c` still fails under a bare
  `clang -std=gnu89 -fsyntax-only` probe because the recovered translation
  unit still lacks the shared navigation / trig / LVGL header layer that
  defines `uint32_t`, `ABS`, the `TRIG_*` constants,
  `VectorSignedFixedToFloat(...)`, and the surrounding Nema / LVGL /
  navigation extern declarations; the failure remains translation-unit
  recovery fallout rather than a regression from the compass-start reflash
  frame cleanup.
- `translate_ui.c` now gets past missing standard types / libc headers under
  a bare `clang -std=gnu89 -fsyntax-only` probe, but it still fails because
  the recovered translation unit lacks the shared translate UI / LVGL / BLE /
  audio extern layer that declares the translate event-state globals, the
  elog strings, and the surrounding UI / transport helpers such as
  `translate_action_{lock,unlock}()`, `translate_result_format()`,
  `translate_ui_{init,deinit,fsm_handler,text_refresh_check}()`,
  `translate_heartbeat_check()`, `APP_PbTranslateTxEncodeNotify(...)`,
  `ble_state_skip_manual_start(...)`, `ble_param_reset_delayed_event(...)`,
  `AUDM_appRelease(...)`, and the LVGL entry points; the failure remains
  translation-unit recovery fallout rather than a regression from moving the
  event handler into its owner file and restoring the standard includes.
- `setting.c` still fails under a bare `clang -std=gnu89 -fsyntax-only`
  probe because the recovered translation unit still lacks the shared
  settings / protobuf / elog header layer that defines `byte`, the
  `g_setting_*` globals, the `ELOG_*` format/tag symbols, and the
  surrounding `pb_*`, `Thread_MsgPbTxByBle(...)`, and `elog_*` helper
  declarations; the failure remains translation-unit recovery fallout rather
  than a regression from the status-snapshot rename / alias cleanup.
- `ux_settings.c` still fails under a bare
  `clang -std=gnu89 -fsyntax-only` probe because the recovered translation
  unit still lacks the shared standard-type and UX-settings / ring / battery
  extern layer that defines `uint{8,16,32}_t`, `byte`,
  `settings_dump_state_ptr`, `ring_protocol_state`,
  `ux_status_sync_ring_paired_evt`, `ux_status_sync_display_options_data`,
  `system_alert_reflasheventhandl_f08`, and the surrounding
  `fw_evt_loop_*`, `SendDataTo{Peer,Both}`, `CHG_*`,
  `ble_connection_state_check(...)`, `ring_proto_is_paired(...)`,
  `ux_setting_kvdb_read(...)`, `timer_check_elapsed(...)`, and `elog_*`
  helper declarations; the failure remains translation-unit recovery
  fallout rather than a regression from retiring the duplicate dump copies.
- `pb_quicklist_handler.c` still fails under a bare
  `clang -std=gnu89 -fsyntax-only` probe because the recovered translation
  unit still lacks the shared protocol header layer that defines
  `uint{8,16,32}_t`, `byte`, the protobuf / elog helper declarations, and
  the quicklist buffer / fault-template / string externs referenced
  throughout the file; the failure remains translation-unit recovery fallout
  rather than a regression from re-retiring the duplicate quicklist dump
  slice.
- `fw_evt_loop.c` now passes a bare `clang -std=gnu89 -fsyntax-only` probe;
  the remaining output is the pre-existing recovered-ABI warning tail from
  non-prototype math / allocator helper externs rather than a syntax blocker.
- `dfu_core.c`, `dfu_task.c`, `thread_manager.c`, and `bootloader.c` now pass
  bare `clang -std=gnu89 -fsyntax-only` probes after the bootloader DFU /
  thread-manager owner cleanup and the follow-on semantic rename wave; the
  `boot_jump_to_app(...)` owner file no longer depends on the decompiler-only
  `_scb_vtor` alias or `code` function-pointer typedef for a standalone probe.
- Retired the duplicate production-test battery / canvas / version / IMU /
  press-key owner slice from
  `openCFW/src/platform/apollo510b/main_firmware/_unclassified.c`, leaving
  `product_mode_config(...)`, `get_battery_status(...)`,
  `get_battery_info(...)`, `set_canvas_pos_info(...)`,
  `get_canvas_pos_info(...)`, `get_version(...)`, `get_imu_info(...)`, and
  `get_press_key_val(...)` owned solely by
  `openCFW/src/platform/apollo510b/main_firmware/system/production_test.c`.
- Targeted rescans show the retired dump start-address comments
  `0x0048d328`, `0x0048d4d4`, `0x0048d6d8`, `0x0048d924`, `0x0048dbc4`,
  `0x0048dd00`, `0x0048df18`, and `0x0048e160` no longer appear in
  `openCFW/src/platform/apollo510b/main_firmware/_unclassified.c`, while the
  broad placeholder / decompiler-token sweep excluding `_unclassified.c` and
  bundled `third_party/` still returns no matches.
- Rebound the repo-owned RTOS wrapper callers in
  `openCFW/src/platform/apollo510b/main_firmware/driver/uled/drv_mspi_uled_common.c`,
  `openCFW/src/platform/apollo510b/main_firmware/platform/audio/service_codec_host.c`,
  `openCFW/src/platform/apollo510b/main_firmware/platform/threads/thread_ble_wsf.c`,
  and `openCFW/src/platform/apollo510b/main_firmware/rtos/freertos_queues.c`
  from the dump aliases `rtos.cmsis_44809e`, `rtos.cmsis_453ca8`, and
  `rtos.cmsis_453d6c` onto the recovered owner names
  `rtos_queue_semaphore_take_dispatch(...)`,
  `rtos_task_priority_set(...)`, and
  `rtos_task_record_mutex_hold()` in
  `openCFW/src/platform/apollo510b/main_firmware/rtos/rtos_cmsis_wrappers.c`.
- Retired the duplicate dump copies of that RTOS queue / priority wrapper
  slice from `openCFW/src/platform/apollo510b/main_firmware/_unclassified.c`,
  leaving the recovered `0x0044809e`, `0x00453ca8`, and `0x00453d6c`
  helpers owned solely by
  `openCFW/src/platform/apollo510b/main_firmware/rtos/rtos_cmsis_wrappers.c`.
- Targeted rescans now show the retired aliases no longer appear in
  repo-owned normal-source callers, the retired dump addresses `0x0044809e`,
  `0x00453ca8`, and `0x00453d6c` no longer appear in
  `openCFW/src/platform/apollo510b/main_firmware/_unclassified.c`, and the
  broad decompiler-token sweep excluding `_unclassified.c` and bundled
  `third_party/` still returns no bare `FUN_`, `DAT_`, `LAB_`, numeric
  `param_*`, or `g_<hex>` tokens in normal-source files.

## Active Wave Checklist
- [x] Wave 10: attack the highest-volume normal-source placeholder leaders in `platform/apollo510b/main_firmware/platform/ble/cordio_stack.c`, `platform/apollo510b/main_firmware/hal/am_hal.c`, `platform/apollo510b/main_firmware/app/gui/dashboard/dashboard_ui_widgets.c`, `platform/apollo510b/main_firmware/app/gui/stock/stock_widget.c`, `platform/apollo510b/bootloader/hal/am_hal.c`, `platform/apollo510b/main_firmware/system/production_test.c`, and `platform/apollo510b/main_firmware/platform/ble/app_ble.c`.
- [x] Wave 11: continue shrinking `platform/apollo510b/main_firmware/_unclassified.c` by moving evidence-backed main-firmware helpers, data blocks, comments, and string labels uncovered while working through the Wave 10 leaders.
- [x] Wave 12: resume `platform/apollo510b/bootloader/_unclassified.c` migration, prioritizing the remaining LittleFS event-loop path, MSPI lock/timing helpers, and the NOR / DFU owner splits once their ABIs are recoverable.
- [x] Wave 13a: move the case-MCU FreeRTOS list / critical / heap-free primitive cluster (`0x0800ade4`, `0x0800bd44` through `0x0800be48`) into `peripherals/case_mcu/rtos/freertos.c`, restore the split-block argument in `xTimerCreateStatic()`, and delete the duplicate dump copies.
- [x] Wave 13b1: move the case-MCU timer active-list / sample-time / queue-empty/full helper slice (`0x0800ae3c`, `0x0800ae7c`, `0x0800ae98`, `0x0800b09c`) into `peripherals/case_mcu/rtos/freertos.c` and delete the stale `freertos_idle_hook_stub` dump copy.
- [x] Wave 13b2a: move the case-MCU delayed-list / timeout / scheduler primitive slice (`0x0800a9c8`, `0x0800bf74`, `0x0800bf90`, `0x0800bfb4`, `0x0800c198`, `0x0800c1a8`, `0x0800c760`) into `peripherals/case_mcu/rtos/freertos.c` with evidence-backed names.
- [x] Wave 13b2b1: move the case-MCU queue / event-descriptor / scheduler-bootstrap helper slice (`0x0800b078`, `0x0800be90`, `0x0800beb8`, `0x0800bed0`, `0x0800bef8`, `0x0800bfe4`, `0x0800c040`, `0x0800c09c`, `0x0800c110`, `0x0800c264`, `0x0800c290`, `0x0800c2a4`, `0x0800c2c2`, `0x0800c2e4`, `0x0800c380`, `0x0800c394`, `0x0800c3e8`, `0x0800c42e`, `0x0800c864`, `0x0800cb38`, `0x0800cbfc`) into `peripherals/case_mcu/rtos/freertos.c` and repair the locally provable ABI drops.
- [x] Wave 13b2b2a: move the case-MCU scheduler delay / queue send / queue receive helper slice (`0x0800bf40`, `0x0800c49e`, `0x0800c5c0`, `0x0800c652`) into `peripherals/case_mcu/rtos/freertos.c`, restore the missing delay argument, and rebind the remaining timer-command wrappers to the recovered queue helpers.
- [x] Wave 13b2b2b: recover and move the remaining `9` case-MCU FreeRTOS timer-command / constructor / event-broadcast helpers in `peripherals/case_mcu/_unclassified.c`, prioritizing the packed timer-command message ABI, the event-group waiter-list sentinel recovery, and the dynamic/static timer-task constructors.
- [x] Wave 14: clean the touch-controller CapSense baseline/status naming in `peripherals/touch_controller/signal/baseline.c` and `peripherals/touch_controller/capsense/capsense_core.c`, including the process-status stub rename, the corrected negative-drift commentary, and the dead baseline-slot plumbing.
- [x] Wave 15: clean the touch-controller startup / libc compatibility stub naming in `peripherals/touch_controller/startup/startup.c`, `peripherals/touch_controller/startup/hardware_init.c`, and `peripherals/touch_controller/libc/libc_math.c`, including the reserved phase-2 hook renames, the ignored interrupt handler renames, the `noop_return_zero_stub()` rename, and the recovered divider wrapper call arities.
- [x] Wave 16: clean the touch-controller gesture / report runtime globals in `peripherals/touch_controller/touch/gesture_detect.c`, `peripherals/touch_controller/touch/touch_handler.c`, `peripherals/touch_controller/touch/proximity.c`, `peripherals/touch_controller/host/host_interface.c`, and `peripherals/touch_controller/utils/debug.c`, including the direct ring-index remainder recovery, the shared CapSense / host IRQ context renames, and the repaired variadic debug-stub signature.
- [x] Wave 17: clean the touch-controller CapSense scan/runtime naming in `peripherals/touch_controller/capsense/capsense_core.c`, including the slot-programming cursor names, the self/mutual scan state locals, the calibration-path status/config names, and the CP-estimation context names.
- [x] Wave 18: clean the remaining touch-controller CapSense divider / autotune / self-scan helper naming in `peripherals/touch_controller/capsense/capsense_core.c`, including the `scan_runtime` / `slot_config_cursor` / `pre_scan_callback` names and the recovered `capsense_calc_idac_value(...)` call site.
- [x] Wave 19: clean the touch-controller CapSense calibration / verification helper naming in `peripherals/touch_controller/capsense/capsense_core.c`, including the recovered `find_min_raw_count` / `get_baseline_ref` / IDAC-wrapper return values and the repaired `capsense_measure_all_slots(widget_id, ...)` / `capsense_is_widget_enabled(widget_id, ...)` calibration call sites.
- [x] Wave 20: clean the remaining CapSense startup / process / accessor helper signatures in `peripherals/touch_controller/capsense/capsense_core.c`, including the recovered `capsense_context` entry points, callback / timeout helper signatures, null-pointer guard, and post-calibration accessor constants.
- [x] Wave 21: clean the remaining early CapSense filter / start-scan / slot-config fallout in `peripherals/touch_controller/capsense/capsense_core.c`, including the prox-config externs, raw/history pointer typing, repaired debounce/clamp helper call sites, and the recovered `_1cd0` / `_1df8` / `_2058` / `_205c` / `_220c` data-label references.
- [x] Wave 22: recover the remaining mid-file CapSense config-table / scan-state / callback / mask typing blockers in `peripherals/touch_controller/capsense/capsense_core.c`, including the `_2480` / `_2864` / `_2884` / `_48c8` / `_48cc` / `_29c0` / `_2a2c` / `_2db8` data-label rebinding and the repaired wrapper / callback pointer contracts through the update-period path.
- [x] Wave 23: recover the late CapSense auto-tune / self-cap / scan-start-stop / trigger / wait / reset / setup-self / setup-mutual labels and callback typing in `peripherals/touch_controller/capsense/capsense_core.c`, and restore the explicit `math_count_leading_zeros(...)` return contract in `peripherals/touch_controller/utils/math.c`.
- [x] Wave 24: continue the CapSense full-init / calibration / IDAC-search / verify-all-sensors recovery band in `peripherals/touch_controller/capsense/capsense_core.c`, starting with the missing helper declarations, dispatcher / init callback ABI damage, `capsense_full_init_and_calibrate_cfg`, `capsense_binary_search_comp_cfg`, `math_abs_diff(...)`, and the remaining pointer/context typing around `capsense_run_single_calibration(...)` and `capsense_clamp_widget_if_not_prox(...)`.
- [x] Wave 25: recover the late CapSense config / slot-offset / trim-literal pool in `peripherals/touch_controller/capsense/capsense_core.c`, including the bottom-helper return codes, the mutual/common slot-config blocks at `0x3000-0x3034`, the per-channel config block at `0x600-0x618`, and the SFLASH trim base / profile byte selectors.
- [x] Wave 26: clean the remaining Apollo bootloader HAL table-base placeholders in `platform/apollo510b/bootloader/hal/hal_i2c.c`, renaming the per-GPIO saved-value / mask / transfer-word tables and confirming the `bootloader/hal/` owner cluster is clear of address-suffixed normal-source names.
- [x] Wave 27: clean the touch-controller CapSense scan-control literal-pool band in `peripherals/touch_controller/capsense/capsense_core.c` and `peripherals/touch_controller/utils/math.c`, including the start / stop / trigger / wait masks, the calibration scan constants, the self / mutual scan setup masks, the operating-mode handler table, and the `math_count_leading_zeros(...)` seed literal.
- [x] Wave 28: clean the next evidence-backed CapSense literal-pool tail in `peripherals/touch_controller/capsense/capsense_core.c`, including the sub-conversion masks, the sensor-fail clear mask, the self-cap result register offsets, the scan-timing / target-IDAC preserve masks, and the recovered saturation constants.
- [x] Wave 29: clean the bootloader NOR flash timing helper labels in `platform/apollo510b/bootloader/hal/norflash_timing.c`, including the operation-lock handle / context labels, the selected-profile / expected-probe labels, and the timing-scan summary / profile / center log formats.
- [x] Wave 30: clean the remaining address-suffixed OTA context references in `platform/apollo510b/main_firmware/platform/protocols/efs_service/efs_service.c`, rebinding the command/result/raw-data paths to `ota_fw_info_ctx` / `ota_service_ctx` and clearing the last `g_5a7c` / `g_61f8` normal-source tail.
- [x] Wave 31: clean the stock widget stock-entry overlay locals in `platform/apollo510b/main_firmware/app/gui/stock/stock_widget.c`, including the symbol / subtitle / price / change / chart aliases in `stock_scroll_load_stock_data(...)`, the split third-row change buffer, and the adjacent summary-row / chart-validation helper locals.
- [x] Wave 32: clean the SVG arc-decomposition band in `platform/apollo510b/main_firmware/app/gui/navigation/navigation_ui.c`, including the packed radii / saved-endpoint scratch slots, the unit-circle cubic control points, and the ellipse center / radius / tilt transform terms in `navigation_ui_svg_path_interpret(...)`.
- [x] Wave 33: clean the quicklist protobuf owner cluster in `platform/apollo510b/main_firmware/platform/protocols/pb_service_quicklist.c` and `platform/apollo510b/main_firmware/platform/protocols/pb_quicklist_handler.c`, including the recovered RX / encode log labels, the quicklist field-staging locals, and the duplicate quicklist / display-config dump copies in `platform/apollo510b/main_firmware/_unclassified.c`.
- [x] Wave 34: clean the box-detect service / protobuf / display owner cluster in `platform/apollo510b/main_firmware/platform/service/box_detect/service_box_detect.c` and `platform/apollo510b/main_firmware/platform/product_test/pt_protocol_procsr.c`, including the recovered case-state notify / display enqueue helpers, the stale full-state accessor rename, and the duplicate box-detect dump copies in `platform/apollo510b/main_firmware/_unclassified.c`.
- [x] Wave 35: clear the final normal-source placeholder tail in `peripherals/touch_controller/capsense/capsense_core.c`, including the recovered `capsense_set_param_if_unset(int config_id, ...)` signature and the aligned forward declaration.
- [x] Wave 36: retire the duplicate teleprompter protobuf RX / TX owner cluster in `platform/apollo510b/main_firmware/_unclassified.c`, leaving `APP_PbRxTelepromptFrameDataProcess`, `APP_PbTelepromptTxEncodeCommResp`, `APP_PbTxEncodeStatusNotify`, `APP_PbTxEncodeFileListRequest`, `APP_PbTxEncodeFileSelect`, `APP_PbTxEncodePageDataRequest`, and `APP_PbTxEncodeScrollSync` owned solely by `platform/protocols/pb_teleprompter_handler.c`, and restore the missing standard includes needed for a meaningful standalone probe there.
- [x] Wave 37: retire the duplicate notification / health / conversate / ring / translate protobuf owner slices in `platform/apollo510b/main_firmware/_unclassified.c`, leaving the `APP_Pb{Rx,Tx}*` handler functions owned solely by `platform/protocols/pb_notification_handler.c`, `pb_health_handler.c`, `pb_conversate_handler.c`, `pb_ring_handler.c`, and `pb_translate_handler.c`, and restore the missing standard includes needed for meaningful standalone probes there.
- [x] Wave 38: clean the shared display / quicklist owner tail in `platform/apollo510b/main_firmware/app/gui/common/display_common.c` and `platform/apollo510b/main_firmware/_unclassified.c`, moving `teleprompter_build_text_view(...)` and `display_subsystem_init(...)` into `display_common.c`, removing the stale quicklist display-config / data-manager duplicate helpers from that file, and retiring the matching dump copies of the common display helpers from `_unclassified.c`.
- [x] Wave 39: retire the recovered inter-eye UART and RTOS queue/task helper dump copies from `platform/apollo510b/main_firmware/_unclassified.c`, leaving the `slave_uart_*` owner slice in `comms/slave_inter_eye.c` and the recovered `rtos_queue_*` / `task_nv_*` / `prvCopyDataToQueue(...)` / `task_init_*` / `task_signal_event_bit(...)` helpers in `rtos/rtos_cmsis_wrappers.c`.
- [x] Wave 40: retire the remaining recovered inter-eye display / routing dump copies from `platform/apollo510b/main_firmware/_unclassified.c`, leaving `slave_get_display_mode(...)`, `slave_frame_extract_payload(...)`, `slave_set_display_mode(...)`, `slave_display_cmd_complete(...)`, `slave_display_cmd_init(...)`, `slave_cmd_extract_pipe(...)`, `slave_cmd_reset(...)`, `slave_audio_route_cmd(...)`, and `slave_get_ring_state(...)` owned solely by `comms/slave_inter_eye.c`.
- [x] Wave 41: retire the EvenAI lock / input / heartbeat dump copies from `platform/apollo510b/main_firmware/_unclassified.c`, move the heartbeat-arm helper into `app/gui/EvenAI/even_ai.c` as `even_ai_heartbeat_timer_mgr_start(...)`, and rename the misidentified `0x004ee30c` poller to `even_ai_heartbeat_timer_mgr_poll_expiry(...)` while rebinding `platform/service/evenAI/service_even_ai.c` onto the recovered owner slice.
- [x] Wave 42: clean the remaining navigation / settings semantic tail in `platform/apollo510b/main_firmware/app/gui/navigation/navigation_ui.c` and `app/gui/setting/setting.c`, replacing the compass-start `reflash_param_*` scratch bytes with a named six-byte request frame, renaming the status-snapshot response helpers, and rebinding the touched settings elog references onto status-snapshot terminology while retaining the evidence-backed EvenAI `local_data` names.
- [x] Wave 43: re-retire the regenerated quicklist protobuf / display-config owner slice from `platform/apollo510b/main_firmware/_unclassified.c`, leaving `APP_PbRxQuicklistFrameDataProcess`, `APP_DecodePbRxQuicklistData`, `APP_PbTxEncodeQuicklistItem`, `APP_PbTxEncodeQuicklistMultItems`, `APP_PbNotifyEncodeQuicklistMultItems`, `APP_PbTxEncodeQuicklistEvent`, `APP_PbNotifyEncodeQuicklistEvent`, `display_config_region_type_lookup(...)`, and `display_config_region_name(...)` owned solely by `platform/protocols/pb_quicklist_handler.c`, and confirm the retired dump addresses `0x005684d8` through `0x005693e0` no longer appear there.
- [x] Wave 44: retire the duplicate bootloader LittleFS owner tail from `platform/apollo510b/bootloader/_unclassified.c`, rebind the `0x00421048` bootstrap call sites to `littlefs_ensure_boot_directories(void)`, move `fw_evt_loop_default_handler(...)` into `bootloader/littlefs/port/fw_evt_loop.c`, and confirm the retired dump addresses `0x00421048` and `0x00426b5c` through `0x00427b5e` no longer appear in the bootloader dump file.
- [x] Wave 45: retire the case-MCU GLS-detect / YHM2510 / UART helper cluster from `peripherals/case_mcu/_unclassified.c`, moving `reset_all_gls_counters()` into `power/battery.c`, `init_pmic_gpio_and_yhm2510()` and `dump_yhm2510_regs()` into `diagnostics/self_check.c`, `restart_led_timer_1s()` and `glasses_detect_ir_scan()` into `app/main_task.c`, `check_debug_prefix_de()` into `driver/uart.c`, and `backup_yhm2510_regs()` into `driver/fuel_gauge.c`, then confirm those dump symbols no longer appear in the case-MCU backlog file.
- [x] Wave 46: retire the duplicate UX settings / battery-sync owner slice from `platform/apollo510b/main_firmware/_unclassified.c`, leaving `settings_get_state_ptr()`, `UX_LocalSystemStatusSyncHandler(...)`, `ux_setting_init_display_options()`, `ux_setting_apply_locale(...)`, and `UX_BatterySyncHandler(...)` owned solely by `system/ux_settings.c`, retire the adjacent OTA ring-state dump copies in favor of `ota_get_active_flag()` / `ota_get_ready_status()` in `firmware/ota_update.c`, and confirm the retired dump addresses `0x00467254`, `0x00475a00`, `0x00476078`, `0x004760ba`, `0x004760c4`, `0x004ccd14`, and `0x005d630c` no longer appear in the main-firmware backlog file.
- [x] Wave 47: retire the duplicate bootloader DFU runtime / thread-manager owner slice from `platform/apollo510b/bootloader/_unclassified.c`, leaving the recovered `dfu_{get_ota_path,get_config,task_msg_send,init_config,create_message_queue,noop_callback,sync_start,sync_end,pre_jump_deinit}` helpers, `app_dfu_image_crc_check(...)`, `dfu_flash_erase_range(...)`, `_verifyFlashContent(...)`, `app_dfu_system_program(...)`, `_thread_msg_handler()`, `dfu_event_dispatch()`, `dfu_error_halt()`, `thread_dfu_task()`, `crc32_update()`, and the bootloader `thread_manager_*` owner slice solely in `dfu/dfu_core.c`, `dfu/dfu_task.c`, `threads/thread_manager.c`, and `boot/bootloader.c`, and confirm the retired dump addresses `0x0042d798` through `0x0042e3ec` no longer appear in the bootloader dump file.
- [x] Wave 48: clean the recovered bootloader DFU / thread-manager semantic tail in `bootloader/dfu/dfu_core.c`, `bootloader/dfu/dfu_task.c`, `bootloader/threads/thread_manager.c`, and `bootloader/boot/bootloader.c`, rebinding the OTA path / open-mode / runtime-context labels, renaming `dfu_get_ota_path(...)` to `dfu_select_open_mode(...)`, `_verifyFlashContent(...)` to `dfu_verify_flash_content(...)`, `_thread_msg_handler()` to `dfu_process_task_message()`, and replacing the decompiler-only `boot_jump_to_app(int)` handoff cast with the concrete `SCB->VTOR` register write plus typed reset-vector call so all four touched owner files pass standalone `clang -std=gnu89 -fsyntax-only` probes.
- [x] Wave 49: retire the duplicate production-test battery / canvas / version / IMU / press-key owner slice from `platform/apollo510b/main_firmware/_unclassified.c`, leaving `product_mode_config(...)`, `get_battery_status(...)`, `get_battery_info(...)`, `set_canvas_pos_info(...)`, `get_canvas_pos_info(...)`, `get_version(...)`, `get_imu_info(...)`, and `get_press_key_val(...)` owned solely by `system/production_test.c`, and confirm the retired dump addresses `0x0048d328`, `0x0048d4d4`, `0x0048d6d8`, `0x0048d924`, `0x0048dbc4`, `0x0048dd00`, `0x0048df18`, and `0x0048e160` no longer appear in the main-firmware backlog file.
- [x] Wave 50: retire the duplicate main-firmware RTOS queue / priority wrapper slice from `platform/apollo510b/main_firmware/_unclassified.c`, rebind the repo-owned caller sites onto `rtos_queue_semaphore_take_dispatch(...)`, `rtos_task_priority_set(...)`, and `rtos_task_record_mutex_hold()` in `rtos/rtos_cmsis_wrappers.c`, and confirm the retired dump addresses `0x0044809e`, `0x00453ca8`, and `0x00453d6c` no longer appear in the main-firmware backlog file.
- [x] Wave 51: retire the duplicate main-firmware common list / text widget owner slice from `platform/apollo510b/main_firmware/_unclassified.c`, leaving `list_container_calc_item_y(...)`, `get_color_from_index(...)`, the `common_list_*` lifecycle / scroll helpers, and the `common_text_*` lifecycle / scroll helpers owned solely by `app/gui/common/display_common.c`, and confirm the retired dump addresses `0x0058aa2a` through `0x0058e05c` no longer appear in the backlog file.
- [x] Wave 52: re-retire the regenerated ring / translate protobuf owner slice from `platform/apollo510b/main_firmware/_unclassified.c`, move `Translate_ui_event_handler(...)` into `app/gui/translate/translate_ui.c`, restore the missing standard includes needed to narrow standalone validation there, and confirm the retired dump addresses `0x005b41fc`, `0x005b4506`, `0x005b46b0`, `0x005b49c2`, `0x005b4b30`, `0x005b4ca2`, and `0x005ca026` no longer appear in the backlog file.
- [x] Wave 53: retire the duplicate bootloader HAL I2C / MSPI timing owner slice from `platform/apollo510b/bootloader/_unclassified.c`, leaving `HAL_I2C{Init,Transfer}(...)` owned solely by `bootloader/hal/hal_i2c.c` and `mspi_timing_{scan_txneg,scan_rxneg,scan_rxcap,scan_turnaround,set_default,apply,validate,scan_pass_check,scan_window,scan_center,scan_result,scan_iterate,check,auto_check}(...)` owned solely by `bootloader/hal/norflash_timing.c`, then confirm the retired dump addresses `0x0041df20`, `0x0041df9e`, and `0x0041fdba` through `0x00420196` no longer appear in the bootloader dump file while both owner files pass standalone `clang -std=gnu89 -fsyntax-only` probes.
- [ ] Repeat bounded rename-and-migrate waves until rescans no longer surface evidence-backed improvements to identifiers, comments, string labels, or `_unclassified.c` placement anywhere in repo-owned `openCFW/`.

## BLOCKED
- Meaningful whole-file syntax validation for the case-MCU RTOS sources is
  still blocked by existing translation-unit recovery damage. Unblock by
  restoring the missing `memcpy_impl` source arguments in
  `vTaskPrioritySet()` around lines `965` / `973`, then fixing the heap
  pointer typing in `vTaskDelete()` / the heap-init path around lines
  `1088` / `1095` / `1101` and the rest of that allocator setup. That is the
  remaining blocker for a meaningful full-file `freertos.c` syntax probe.
- Meaningful standalone syntax validation for the touched case-MCU owner
  cluster (`power/battery.c`, `diagnostics/self_check.c`, `app/main_task.c`,
  `driver/uart.c`, and `driver/fuel_gauge.c`) is still blocked by missing
  translation-unit context. Unblock by restoring the shared case-MCU header /
  typedef layer that defines `bool`, `byte`, `ushort`, `uint{8,16,32}_t`,
  the CMSIS-RTOS entry points (`osThreadNew`, `osTimerChangePeriod`, and
  related APIs), and the surrounding GPIO / debug / YHM2510 globals and
  helper declarations used throughout those files before retrying standalone
  `clang -std=gnu89 -fsyntax-only` probes there.
- Meaningful standalone syntax validation for
  `openCFW/src/platform/apollo510b/main_firmware/system/production_test.c`
  is still blocked by missing translation-unit context. Unblock by restoring
  the shared production-test header / extern layer that defines `byte`,
  declares the mic-recording state globals
  (`enter_mic_recording_buffer_pointer`,
  `enter_mic_recording_state_counter_{1,2,3}`,
  `enter_mic_recording_buffer_space_fill`, `mic_recording_data_ptr`,
  `mic_recording_active_flag`, `transfer_mic_byte_count`,
  `transfer_mic_recording_total_size`, and `mic_recording_filename`), and
  exposes the surrounding utility / RTOS / BLE / peer helper declarations
  such as `am_util_string_strlen`, `rtos_mem_free`,
  `ble_connection_state_check(...)`, and `SendDataToPeer(...)` before
  retrying a standalone `clang -std=gnu89 -fsyntax-only` probe there.
- The remaining case-MCU helper `gls_l_toggle_5v_on_aging()` is still
  stranded in `openCFW/src/peripherals/case_mcu/_unclassified.c`. Unblock by
  recovering the missing dataflow into `gpio_set_gls_l_5v(...)` and deciding
  whether the toggled byte at `dma_ch2_flag_te_mask + 0xc` is the true 5V
  output state or only a mirror, then place the helper in either
  `production/aging_test.c` or `driver/gpio.c` without preserving a
  misleading no-argument call signature.
- Meaningful standalone syntax validation for
  `openCFW/src/platform/apollo510b/main_firmware/app/gui/navigation/navigation_ui.c`
  is still blocked by missing translation-unit context above the cleaned SVG
  interpreter. Unblock by restoring the header / macro layer that defines
  `uint32_t`, `ABS`, the `TRIG_*` constants, `VectorSignedFixedToFloat(...)`,
  and the other Nema / LVGL / navigation extern declarations referenced near
  the top of the file before retrying a standalone
  `clang -std=gnu89 -fsyntax-only` probe there.
- Meaningful standalone syntax validation for
  `openCFW/src/platform/apollo510b/main_firmware/app/gui/translate/translate_ui.c`
  is still blocked by missing translation-unit context around the recovered
  translate UI owner slice. The standard `stdbool.h` / `stdint.h` /
  `string.h` includes are now restored there; unblock the remaining probe by
  restoring the shared translate UI / LVGL / BLE / audio header layer that
  defines `byte`, declares the translate event-state globals
  (`translate_ui_event_ctx_f0c`, `translate_ui_event_ctx_f10`,
  `Translate_ui_event_a240`), exposes the translate / system-close elog
  strings used by the moved handler, and provides the surrounding UI /
  transport helper declarations
  (`lv_obj_set_local_style_prop`, `translate_language_lookup`,
  `translate_action_{lock,unlock}`, `translate_result_format`,
  `translate_ui_{init,deinit,fsm_handler,text_refresh_check}`,
  `translate_heartbeat_check`, `APP_PbTranslateTxEncodeNotify(...)`,
  `ble_state_skip_manual_start(...)`, `ble_param_reset_delayed_event(...)`,
  `AUDM_appRelease(...)`, and the LVGL animation entry points) before
  retrying a standalone `clang -std=gnu89 -fsyntax-only` probe there.
- Meaningful standalone syntax validation for
  `openCFW/src/platform/apollo510b/main_firmware/system/ux_settings.c` is
  still blocked by missing translation-unit context around the recovered UX
  settings / ring-status / battery-sync owner slice. Unblock by restoring the
  shared standard-type and UX-settings header layer that defines
  `uint{8,16,32}_t`, `byte`, `settings_dump_state_ptr`,
  `ring_protocol_state`, `ux_status_sync_ring_paired_evt`,
  `ux_status_sync_display_options_data`, and
  `system_alert_reflasheventhandl_f08`, plus the surrounding
  `fw_evt_loop_*`, `SendDataTo{Peer,Both}`, `CHG_*`,
  `ble_connection_state_check(...)`, `ring_proto_is_paired(...)`,
  `ux_setting_kvdb_read(...)`, `timer_check_elapsed(...)`, and `elog_*`
  helper declarations before retrying a standalone
  `clang -std=gnu89 -fsyntax-only` probe there.
- Meaningful standalone syntax validation for
  `openCFW/src/platform/apollo510b/main_firmware/app/gui/setting/setting.c`
  is still blocked by missing translation-unit context around the recovered
  settings / protobuf owner slice. Unblock by restoring the shared settings
  header layer that defines `byte`, the `g_setting_*` globals, the
  `ELOG_*` format/tag symbols, and the surrounding `pb_*`,
  `Thread_MsgPbTxByBle(...)`, and `elog_*` helper declarations before
  retrying a standalone `clang -std=gnu89 -fsyntax-only` probe there.
- Meaningful standalone syntax validation for the quicklist protobuf owner
  cluster is still blocked by missing translation-unit context in
  `openCFW/src/platform/apollo510b/main_firmware/platform/protocols/pb_service_quicklist.c`
  and
  `openCFW/src/platform/apollo510b/main_firmware/platform/protocols/pb_quicklist_handler.c`.
  Unblock by restoring the shared protocol header layer that defines
  `uint{8,16,32}_t`, `byte`, the protobuf / elog helper declarations, and the
  quicklist buffer / fault-template / string externs referenced throughout
  those files before retrying standalone `clang -std=gnu89 -fsyntax-only`
  probes there.
- Meaningful standalone syntax validation for the notification / health /
  conversate / ring / translate protobuf owner cluster is still blocked by
  missing translation-unit context in
  `openCFW/src/platform/apollo510b/main_firmware/platform/protocols/pb_notification_handler.c`,
  `pb_health_handler.c`, `pb_conversate_handler.c`, `pb_ring_handler.c`, and
  `pb_translate_handler.c`. Unblock by restoring the shared protocol header
  layer that defines `byte`, the protobuf / elog helper declarations, and the
  service-specific buffer / counter / field-table / string externs referenced
  throughout those files, including the notification whitelist / JSON helpers,
  the health decode / encode buffers and field tables, the conversate / ring /
  translate `pb_encode_buf_*` and `pb_ostream_buf_*` globals, the
  `msg_id_counter_{conversate,translate}` counters, and the surrounding
  `Thread_MsgPb{Tx,Notify}ByBle`, `debug_ringbuf_write`, and `elog_*`
  declarations, before retrying standalone `clang -std=gnu89 -fsyntax-only`
  probes there.
- Meaningful standalone syntax validation for the teleprompter protobuf owner
  cluster is still blocked by missing translation-unit context in
  `openCFW/src/platform/apollo510b/main_firmware/platform/protocols/pb_teleprompter_handler.c`.
  Unblock by restoring the shared teleprompter / protocol header layer that
  declares the frame-context base (`teleprompter_frame_ctx_base`), the
  teleprompter protobuf buffers and counter globals
  (`pb_encode_buf_teleprompter`, `pb_ostream_buf_teleprompter`,
  `pb_field_table_teleprompter`, `msg_id_counter_teleprompter`), the
  `PROTO_TYPE_*` and BLE service / direction constants, and the surrounding
  protobuf / elog / BLE-send helper declarations
  (`pb_ostream_init`, `pb_encode`, `debug_ringbuf_write`,
  `Thread_MsgPb{Tx,Notify}ByBle`, `elog_*`) before retrying a standalone
  `clang -std=gnu89 -fsyntax-only` probe there.
- Meaningful standalone syntax validation for
  `openCFW/src/platform/apollo510b/main_firmware/app/gui/common/display_common.c`
  is still blocked by missing translation-unit context around the shared GUI
  display helpers. Unblock by restoring the header layer that defines
  `uint{8,16,32,64}_t`, `int16_t`, `byte`, the LVGL object / animation helper
  declarations, and the surrounding display / teleprompt externs referenced
  throughout the file before retrying a standalone
  `clang -std=gnu89 -fsyntax-only` probe there.
- Meaningful standalone syntax validation for
  `openCFW/src/platform/apollo510b/main_firmware/comms/slave_inter_eye.c`
  is still blocked by missing translation-unit context around the recovered
  inter-eye UART owner slice. Unblock by restoring the shared type / extern
  layer that defines `bool`, `byte`, `appdb_active_record`, and the
  surrounding `WsfMsg{Alloc,Send}`, `am_util_memcpy_6bytes`, `dm_g`, and
  related device-manager / BLE helper declarations before retrying a
  standalone `clang -std=gnu89 -fsyntax-only` probe there.
- Meaningful standalone syntax validation for
  `openCFW/src/platform/apollo510b/main_firmware/rtos/rtos_cmsis_wrappers.c`
  is still blocked by missing translation-unit context around the recovered
  RTOS helper owner slice. Unblock by restoring the shared header layer that
  defines `uint{16,32,64}_t`, `bool`, and the surrounding `elog_ringbuf_data`,
  queue / task / critical-section, and EasyLogger helper declarations before
  retrying a standalone `clang -std=gnu89 -fsyntax-only` probe there.
- Meaningful standalone syntax validation for the touched RTOS wrapper caller
  cluster (`openCFW/src/platform/apollo510b/main_firmware/rtos/freertos_queues.c`,
  `openCFW/src/platform/apollo510b/main_firmware/platform/threads/thread_ble_wsf.c`,
  `openCFW/src/platform/apollo510b/main_firmware/platform/audio/service_codec_host.c`,
  and
  `openCFW/src/platform/apollo510b/main_firmware/driver/uled/drv_mspi_uled_common.c`)
  is still blocked by missing translation-unit context. Unblock by restoring
  the shared standard-type / macro layer that defines `uint`, `uint8_t`,
  `uint32_t`, `uint64_t`, and `MERGE_4_4`, plus the surrounding queue / BLE /
  audio / MSPI helper declarations referenced in those files, including
  `osmessageq_g_8308`, `rtos_thread_mgmt(...)`,
  `lv_ambiq_display_batch_process(...)`,
  `rom_mve_complex_butterfly_body(...)`,
  `hal_heap_check_and_i2c_init(...)`, and the recovered semaphore wrapper
  owner `rtos_queue_semaphore_take_dispatch(...)`, before retrying
  standalone `clang -std=gnu89 -fsyntax-only` probes there.
- Meaningful standalone syntax validation for
  `openCFW/src/platform/apollo510b/main_firmware/platform/service/box_detect/service_box_detect.c`
  is still blocked by missing translation-unit context around the recovered
  box-detect owner cluster. Unblock by restoring the shared service header /
  extern layer that declares the local and merged state accessors
  (`box_detect_get_merged_*`, `case_get_in_case`), the EasyLogger string/tag
  externs, the box-detect buffer / counter globals
  (`case_rx_decode_buf`, `pb_ostream_buf_box_detect`,
  `msg_id_counter_box_detect`, `box_detect_trigger_count`,
  `box_detect_msg_ctx`), and the surrounding device-manager / graphics /
  protobuf helper declarations before retrying a standalone
  `clang -std=gnu89 -fsyntax-only` probe there.
- The remaining `check_and_create_directories(int, char *)` duplicate in
  `openCFW/src/platform/apollo510b/bootloader/_unclassified.c` is still a
  misnamed LittleFS helper even after the concrete directory bootstrap was
  renamed to `littlefs_ensure_boot_directories(void)`. Unblock by recovering
  its real semantic name, the exact 12-byte buffer layout that its caller
  still treats as raw `flash_config_buf[12]`, and the stable op-5 / op-6
  transaction contract that seeds `littlefs_boot_count_fmt` before moving it
  into the `littlefs/port/` owner cluster.
- The remaining LittleFS event-loop semantic recovery is still blocked.
  The recovered owner slice now lives in
  `openCFW/src/platform/apollo510b/bootloader/littlefs/port/fw_evt_loop.c`
  but it still carries damaged queue-geometry math, split-global collapse, or
  ABI recovery. Unblock by:
  recovering the 12-byte handler-config struct that
  `fw_evt_loop_register_handler` copies into its caller buffer;
  splitting the overloaded `fw_evt_delayed` references into the distinct
  threshold, nibble-table, and cost-table globals already implied by the
  cleaned decompile; and repairing the phantom extra-argument / stack-alias
  damage in `fw_evt_loop_default_handler`, `fw_evt_loop_task`, and
  `fw_evt_loop_register_handler` well enough to finish cleaning that path
  inside
  `openCFW/src/platform/apollo510b/bootloader/littlefs/port/fw_evt_loop.c`
  and retire the remaining bootstrap tail without preserving misleading helper
  names.
- The MSPI timing snapshot helper pair `mspi_flash_mutex_init` /
  `mspi_flash_mutex_lock` is still stranded in `_unclassified.c`. Unblock by
  reconciling it with the cleaned main-firmware MRAM analog
  `am_hal_mram_read_write` / `am_hal_mram_op_dispatch`, recovering the
  wrapper's stable 4-argument snapshot ABI, the exact region-selector
  semantics encoded by `flash_wrapper_lock_[abcd]` /
  `flash_wrapper_unlock_a`, the real copy/read contract of the helper
  currently decompiled as `am_hal_interrupt_save_and_disable`, and the units
  and output layout for the live `0x25c`, `0x270`, and `0x278` timing
  snapshots. Also unblock by aligning the bootloader call sites plus the
  misowned helper pair currently exposed as `flash_wrapper_sync_nop` and
  `flash_wrapper_erase_impl` before moving that path into the correct
  bootloader HAL / MRAM owner cluster without preserving a misleading mutex
  name.
- The main bootloader NOR / flash-driver cluster is still stranded in
  `_unclassified.c`. Unblock by recovering the broken pseudo-assignments and
  call-arity mismatches in `DRV_Mx25u25643g_*` and `mx25u25643g_*` so they can
  move into a concrete HAL / flash-driver owner without copying unresolved
  decompiler corruption.
- The remaining bootloader startup / main / OTA transition cluster
  (`bootloader_early_init` through `main_fatal_error`) still shares damaged
  config-table layouts, register-pair return recovery, and indirect dispatch
  through `main_ota_state_g`. Unblock by recovering the table element layouts
  and the app-jump / OTA-state callback contracts well enough to split that
  path into concrete `boot/` owner files without keeping misleading `main_*`
  names.
- The remaining bootloader DFU file / install engine (`dfu_file_*`,
  `dfu_install_*`) plus the deeper semantic cleanup now isolated in
  `openCFW/src/platform/apollo510b/bootloader/dfu/dfu_core.c` still has
  broken OTA-header field recovery, queue-handle typing, and block-device
  callback signatures. Unblock by recovering the OTA header struct layout and
  the LittleFS / flash callback contracts well enough to replace the raw
  header-word / callback-offset access patterns in `dfu_core.c` and continue
  moving the remaining DFU path into
  `openCFW/src/platform/apollo510b/bootloader/dfu/`.
- The remaining UART redirect cluster (`redirect_uart_write`,
  `redirect_buffer_flush`, `redirect_mutex_init`, `redirect_init`,
  `redirect_register_callback`, `redirect_set_default_output`, `redirect_lock`,
  `redirect_output`) still depends on broken semihost and soft-float helper
  recovery. Unblock by recovering the backend callback ABI and the soft-float
  helper contracts well enough to move that slice into a dedicated
  `bootloader/elog/` or `bootloader/libc/` owner without preserving misleading
  math-wrapper names.
- Meaningful standalone syntax validation for the EvenAI owner cluster is
  still blocked by missing translation-unit context in
  `openCFW/src/platform/apollo510b/main_firmware/app/gui/EvenAI/even_ai.c`,
  `openCFW/src/platform/apollo510b/main_firmware/app/gui/EvenAI/evenai_ui_widgets.c`,
  and
  `openCFW/src/platform/apollo510b/main_firmware/platform/service/evenAI/service_even_ai.c`.
  Unblock by restoring the shared EvenAI header / extern layer that defines
  `byte`, declares the heartbeat/common timer globals (`even_g`,
  `even_ai_timer_ctx_ptr`) and the EvenAI state/sync buffers
  (`evenai_state_ctx`, `evenai_sync_event_config`), and exposes the
  surrounding elog / protobuf / BLE / LVGL helpers and strings used by those
  files, including `APP_PbNotifyEncodeEvenAIEvent(...)`,
  `SVC_EvenAICtrl(...)`, `RequestDisplayStop(...)`, `ble_connection_state_check(...)`,
  `timer_check_elapsed(...)`, `even_widget`, and the EvenAI elog tag/source
  constants, before retrying standalone `clang -std=gnu89 -fsyntax-only`
  probes there.

## Done Criteria
- No remaining evidence-backed placeholder or decompiler-style names in repo-owned `openCFW/src/`.
- No remaining stale struct-field comments or misleading string labels that can be made more explicit from available evidence.
- No remaining evidence-backed entries stranded in `_unclassified.c`; any residual dump content is still there only because a destination file cannot yet be justified without speculation.
