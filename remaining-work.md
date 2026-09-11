# G2 source-only firmware: remaining work

Generated 2026-09-11 from the production flash plan (`g2/build/source/flash-plan.json`), the Apollo
function database (`make -C g2 transparent-db`), the codec ownership ledger, and the EM9305
readiness ledgers. Machine-readable detail for every row (function lists, addresses, tiers,
buckets, region descriptions) is in `remaining-work.json`; `continue-analysis.sh` reads both.

**Goal (from `g2/docs/source-only-goal.md`):** every selected component builds from reviewed
source and pinned upstream dependencies; required data, assets, model parameters, and
accelerator programs have a maintainable source representation or a functionally qualified
source-authored replacement; the original firmware is only an oracle and supplies no bytes.
Typed provider interfaces, opaque bytes as C arrays, trap stubs, and merely compilable
decompilation do **not** count. macOS is the build host; Linux support is not required.

## How the status column is maintained

`continue-analysis.sh` is the only writer of the `Status`, `Owner`, and `Notes` cells.
Status values: `todo`, `in-progress`, `done`, `blocked`, `failed`. An item is `done` only
when its bytes are produced from reviewed source that is production-routed (or, for data,
from a source-authored representation), the narrow tests and the component build pass, and the
research audit / progress entry is written. Retry a `failed` row with
`./continue-analysis.sh run --retry-failed`. Manual overrides: `./continue-analysis.sh done|fail|block|release <ID>`.

Priority: `P1` identified upstream source or routing work; `P2` first-party clean-room C;
`P3` investigation-required code, data/assets, and long-tail tooling.

## Summary

| Component | Items | Release-blocking bytes | Notes |
|---|---:|---:|---|
| apollo_main | 235 | 3,080,790 | 3,046,598 release-blocking bytes; 5,481 retained functions (1.0 MB) + ~2.0 MB data |
| apollo_bootloader | 12 | 87,985 | 87,985 retained bytes in 151 official regions |
| ble_em9305 | 30 | 210,584 | 210,584 retained controller bytes; needs macOS ARC toolchain (XC-003) |
| codec | 35 | 307,615 | 307,615 retained bytes incl. 129,964 B KWS model/NPU payload |
| touch | 3 | 33,952 | candidate source complete (178 fns) but not production-routed |
| case | 2 | 55,752 | candidate source complete (222 fns) but not production-routed |
| cross-cutting | 9 | 0 | gates, toolchains, generators |

Total items: 326. Package under audit: EVENOTA `s200_v2.2.6.10`, expected SHA-256 `1bb3f8c84d288a30cfd252e832ec4a51ac5eca42b5de8e8817db11a938c6a771`.

## Apollo main application - retained executable code

Flash: Apollo510B MRAM, application at `0x00438000..0x00794324` (file offset = address - 0x437FE0).
Evidence: `g2/research/corpus/apollo-main/ghidra/decomp/functions.jsonl` (decompilation per
address), `g2/build/transparent/function-db.json` (names, tiers, buckets), 200+ function maps
in `g2/tools/manifests/*-function-map.tsv`, and the per-family audits in `g2/docs/research/`.
Admission path: reviewed C in `g2/components/apollo_main/core_overlay/` registered in
`overlay.json` (relocated leaf + entry redirect / patch site), built by `make -C g2 core-component`,
then `make -C g2 source` must place it with zero unresolved flash regions. Identified upstream
families (LVGL, Cordio host, AmbiqSuite, littlefs, nanopb, CMSIS-FreeRTOS, TLSF, cJSON, TinyFrame,
liblc3, EasyLogger, FreeType) must use the pinned vendored snapshot under `g2/components/shared/`
with the recovered configuration, not a rewrite. Also register reviewed functions in
`g2/tools/transparent/reviewed_sources.json` so the transparent image stops trapping them.

| ID | Pri | Status | Flash range | Bytes | Kind | Targets | Owner | Notes |
|---|---|---|---|---:|---|---|---|---|
| AM-001 | P3 | todo | `0x00438504..0x0043A11E` | 7,194 | code | FUN_00438504, FUN_00438770, FUN_004387b0, FUN_00438924 |  |  |
| AM-002 | P3 | todo | `0x0043A11E..0x0043DD7C` | 15,454 | code | FUN_0043a11e, FUN_0043a19c, FUN_0043a1b0, FUN_0043a5a0 |  |  |
| AM-003 | P3 | todo | `0x0043DD7C..0x0043E1FA` | 1,150 | code | FUN_0043dd7c, FUN_0043dd86, FUN_0043dd90, FUN_0043dd9a |  |  |
| AM-004 | P1 | failed | `0x0043E1FA..0x0043EF70` | 3,446 | code | FUN_0043e1fa, FUN_0043e2bc, FUN_0043e2d4, FUN_0043e2ea |  | started 2026-09-11 12:31 / 2026-09-11 13:10 failed: You've hit your session limit · resets 4:30pm (America/Chicago) |
| AM-005 | P3 | todo | `0x0043EF70..0x0043FD8C` | 3,612 | code | FUN_0043ef70, FUN_0043ef7a, FUN_0043ef84, FUN_0043ef8e |  |  |
| AM-006 | P1 | failed | `0x0043FD9E..0x00441004` | 4,710 | code | thunk_FUN_00440a1c |  | started 2026-09-11 12:32 / 2026-09-11 13:10 failed: You've hit your session limit · resets 4:30pm (America/Chicago) |
| AM-007 | P3 | todo | `0x00441004..0x004420A6` | 4,258 | code | FUN_00441004, FUN_00441016, FUN_0044102e, FUN_0044104c |  |  |
| AM-008 | P3 | todo | `0x004420A6..0x00448B96` | 27,376 | code | FUN_004420a6, FUN_00442114, FUN_005fa120, FUN_0044215a |  |  |
| AM-009 | P1 | failed | `0x00448B96..0x0044AA68` | 7,890 | code | IRQ_Context, osKernelGetTickCount, osThreadGetId, osThreadYield, TimerCallback |  | started 2026-09-11 12:34 / 2026-09-11 13:10 failed: You've hit your session limit · resets 4:30pm (America/Chicago) |
| AM-010 | P3 | todo | `0x0044AA98..0x0044B8AC` | 3,604 | code | FUN_0044aa98, FUN_0044aaa0, FUN_0044aaa8, FUN_0044aae0 |  |  |
| AM-011 | P1 | failed | `0x0044B8AC..0x0044CAD8` | 4,652 | code | FUN_0044b8ac, FUN_0044b8b8, FUN_0044b8c4, FUN_0044b8d0 |  | started 2026-09-11 12:35 / 2026-09-11 13:10 failed: You've hit your session limit · resets 4:30pm (America/Chicago) |
| AM-012 | P1 | failed | `0x0044CC8C..0x0044DBC4` | 3,896 | code | thunk_FUN_0044d234 |  | started 2026-09-11 12:36 / 2026-09-11 13:10 failed: You've hit your session limit · resets 4:30pm (America/Chicago) |
| AM-013 | P3 | todo | `0x0044DBC4..0x0044E412` | 2,126 | code | FUN_0044dbc4, FUN_0044dc0a, FUN_0044dca2, FUN_0044dce2 |  |  |
| AM-014 | P1 | failed | `0x0044E412..0x0044FA5E` | 5,708 | code | FUN_0044e412, FUN_0044e42c, FUN_0044e442, FUN_0044e45a |  | started 2026-09-11 12:37 / 2026-09-11 13:10 failed: You've hit your session limit · resets 4:30pm (America/Chicago) |
| AM-015 | P1 | failed | `0x0044FA5E..0x004501D2` | 1,908 | code | FUN_0044fa5e, FUN_0044fa7e, FUN_0044faa8, FUN_0044fad2 |  | started 2026-09-11 12:38 / 2026-09-11 13:10 failed: You've hit your session limit · resets 4:30pm (America/Chicago) |
| AM-016 | P1 | failed | `0x004501D2..0x00450B80` | 2,478 | code | FUN_004501d2, FUN_00450228, FUN_00450286, FUN_0045028e |  | started 2026-09-11 12:39 / 2026-09-11 13:10 failed: You've hit your session limit · resets 4:30pm (America/Chicago) |
| AM-017 | P1 | failed | `0x00450B80..0x00451B34` | 4,020 | code | FUN_00450b80, FUN_00450b98, FUN_00450bb2, FUN_00450bcc |  | started 2026-09-11 12:40 / 2026-09-11 13:10 failed: You've hit your session limit · resets 4:30pm (America/Chicago) |
| AM-018 | P3 | todo | `0x00451B34..0x0045246E` | 2,362 | code | FUN_00451b34, FUN_00451b90, FUN_00451b9c, FUN_00451c3a |  |  |
| AM-019 | P1 | failed | `0x0045246E..0x00452C66` | 2,040 | code | FUN_0045246e, FUN_00452478, FUN_00452498, FUN_004524a4 |  | started 2026-09-11 12:41 / 2026-09-11 13:10 failed: You've hit your session limit · resets 4:30pm (America/Chicago) |
| AM-020 | P1 | failed | `0x00452C66..0x0045316A` | 1,284 | code | FUN_00452c66, FUN_00452d42, FUN_00452dc8, FUN_00452dd8 |  | started 2026-09-11 12:41 / 2026-09-11 13:10 failed: You've hit your session limit · resets 4:30pm (America/Chicago) |
| AM-021 | P1 | failed | `0x0045316A..0x004547AE` | 5,700 | code | FUN_0045316a, FUN_00453180, FUN_0045318c, FUN_00453198 |  | started 2026-09-11 12:42 / 2026-09-11 13:10 failed: You've hit your session limit · resets 4:30pm (America/Chicago) |
| AM-022 | P3 | todo | `0x004547AE..0x00456606` | 7,768 | code | FUN_004547ae, FUN_004547b6, FUN_004547be, FUN_004547c6 |  |  |
| AM-023 | P3 | todo | `0x00456606..0x0045D536` | 28,464 | code | loggerSetting_set_ble_transmit, loggerSetting_ble_transmit_enabled, loggerSetting_cancel_ble_transmit |  |  |
| AM-024 | P3 | todo | `0x0045E664..0x0045FC5A` | 5,622 | code | FUN_0045e664, FUN_0045e8d0, FUN_0045ec7c, FUN_0045ef24 |  |  |
| AM-025 | P3 | todo | `0x0045FC5A..0x00461026` | 5,068 | code | FUN_0045fc5a, FUN_0045fcb2, FUN_0045fcd2, FUN_0045fd06 |  |  |
| AM-026 | P3 | todo | `0x00461044..0x004631AA` | 8,550 | code | FUN_00461044, FUN_004611d4, FUN_004611d6, FUN_004612f8 |  |  |
| AM-027 | P3 | todo | `0x0046327E..0x00464C36` | 6,584 | code | FUN_0046327e, FUN_00463c68, FUN_00463e1c, FUN_00463e9a |  |  |
| AM-028 | P3 | todo | `0x00464C36..0x0046919E` | 17,768 | code | onboarding_get_style_bg_color, onboarding_get_style_image_recolor, onboarding_saved_color_state_reset, onboarding_process_mutex_init, onboarding_should_run |  |  |
| AM-029 | P2 | todo | `0x0046919E..0x0046CADE` | 14,656 | code | silent_mode_status_get, SilentMode_SetStatus, SilentMode_ToggleByLocalLongPress, silent_mode_noop_callback, silent_mode_common_data_handler |  |  |
| AM-030 | P2 | todo | `0x0046D8A0..0x0046F4C2` | 7,202 | code | _bleAdvInit, _blePsnIntoADV, dmSlaveAdvFormatData, dmSlaveAdvSetScanRsp, ble_Slave_handler_1 |  |  |
| AM-031 | P3 | todo | `0x0046F4C2..0x004709B2` | 5,360 | code | FUN_0046f4c2, FUN_0046f4ea, FUN_0046f50c, FUN_0046f52c |  |  |
| AM-032 | P3 | todo | `0x004709C0..0x0048431E` | 80,222 | code | sync_info_fn_00471ee8, sync_info_fn_00471fa4, sync_info_fn_00472102 |  |  |
| AM-033 | P3 | todo | `0x00484380..0x00484A96` | 1,814 | code | FUN_00484380, FUN_0048438c, FUN_00484398, FUN_004843ee |  |  |
| AM-034 | P1 | failed | `0x00484A98..0x0048834C` | 14,516 | code | FUN_00484a98, FUN_00487022, FUN_00487156, FUN_0048716c |  | started 2026-09-11 12:43 / 2026-09-11 13:10 failed: You've hit your session limit · resets 4:30pm (America/Chicago) |
| AM-035 | P3 | todo | `0x0048834C..0x0048949A` | 4,430 | code | FUN_0048834c, FUN_004883f0, FUN_004883fc, FUN_00488440 |  |  |
| AM-036 | P3 | todo | `0x0048949C..0x0048D4E8` | 16,460 | code | FUN_0048949c |  |  |
| AM-037 | P1 | in-progress | `0x004894A4..0x0048AA38` | 5,524 | code | FUN_004894a4, FUN_004894d0, FUN_00489546, FUN_00489652 | claude-sonnet-5 session=32fd5b41-ee6b-4dbc-bf61-8756016170ff run=20260911-131038 | started 2026-09-11 13:10 |
| AM-038 | P3 | todo | `0x0048AA54..0x0048B928` | 3,796 | code | FUN_0048aa54, FUN_0048aa60, FUN_0048aa80, FUN_0048aaa2 |  |  |
| AM-039 | P3 | todo | `0x0048B928..0x0048C7B2` | 3,722 | code | FUN_0048b928, FUN_0048b932, FUN_0048b93c, FUN_0048b946 |  |  |
| AM-040 | P1 | todo | `0x0048C7B4..0x0048D866` | 4,274 | code | FUN_0048c7b4, FUN_0048c7d8, FUN_0048c7fc, FUN_0048c80e |  |  |
| AM-041 | P2 | todo | `0x0048D868..0x0048F324` | 6,844 | code | thunk_FUN_0048d86c, thread_notification_init_hook, _androidSendCompleteNotificationMsg, _androidParseNotification, SVC_ANDROID_ParseNotification |  |  |
| AM-042 | P3 | todo | `0x00490120..0x00492F8C` | 11,884 | code | FUN_00490120, FUN_004905e0, FUN_004905f4, FUN_00491184 |  |  |
| AM-043 | P3 | todo | `0x00492FDC..0x00498654` | 22,136 | code | service_ancc_state_get, service_ancc_state_byte0_get, service_ancc_state_byte1_get, service_ancc_state_byte4_set, service_ancc_state_byte4_get |  |  |
| AM-044 | P3 | todo | `0x00498654..0x00499678` | 4,132 | code | FUN_00498654, FUN_0049865e, FUN_00498668, FUN_00498680 |  |  |
| AM-045 | P3 | todo | `0x00499678..0x0049EB96` | 21,790 | code | FUN_00499678, FUN_00499716, FUN_00499752, FUN_004997f8 |  |  |
| AM-046 | P2 | todo | `0x0049EB96..0x004A235E` | 14,280 | code | _ringLinkStateName, _SetRingLinkState, ring_master_reconnect, ring_master_scan_start, _bleMasterScanStop |  |  |
| AM-047 | P2 | todo | `0x004A23AC..0x004A625A` | 16,046 | code | APP_MasterSysStartTryConnectRing, central_schedule_master_connect_004a2618, APP_MasterResetSceneConnectPending, ring_address_is_unset_004a26e8, APP_MasterPublis |  |  |
| AM-048 | P2 | todo | `0x004A6270..0x004A9ED0` | 15,456 | code | DRV_IMUStopRawDataCollection, DRV_IMUReadWhoAmI, DRV_MAGReadWhoAmI, semantic_get_flag_20074fdc, ui_onboarding_main_sub_004A8560 |  |  |
| AM-049 | P3 | todo | `0x004A9EDC..0x004B0D38` | 28,252 | code | ui_onboarding_main_sub_004A9EDC, ui_onboarding_main_sub_004A9F84, ui_onboarding_main_sub_004AA048, ui_onboarding_main_sub_004AA0C8, ui_onboarding_main_sub_004AA |  |  |
| AM-050 | P1 | todo | `0x004B0D38..0x004B201E` | 4,838 | code | FUN_004b0d38, FUN_004b0ea6, FUN_004b0f50, FUN_004b10c0 |  |  |
| AM-051 | P1 | todo | `0x004B201E..0x004B3BD2` | 7,092 | code | FUN_004b201e, FUN_004b202c, FUN_004b20aa, FUN_004b20d4 |  |  |
| AM-052 | P1 | todo | `0x004B3BD2..0x004B522E` | 5,724 | code | HciDrvRadioBoot, HciDrvRadioShutdown, HciDrvHandler, attCcbByConnId, attUuidCmp16to128 |  |  |
| AM-053 | P2 | todo | `0x004B7478..0x004BFD6E` | 35,062 | code | bleSubsystemInit, bleDmCback, bleProcMsg, _bleCommHandler, bleCommHandlerInit |  |  |
| AM-054 | P3 | todo | `0x004BFD6E..0x004C23DE` | 9,840 | code | FUN_004bfd6e, FUN_004bfdf4, FUN_004bfe60, FUN_004bfed6 |  |  |
| AM-055 | P3 | todo | `0x004C240E..0x004C427E` | 7,792 | code | FUN_004c240e, FUN_004c26e0, FUN_004c2ae8, FUN_004c2b30 |  |  |
| AM-056 | P3 | todo | `0x004C427E..0x004C706E` | 11,760 | code | thread_ring_init_hook, thread_ring_resource_hook, device_mgr_fn_004c659a, device_mgr_fn_004c6810, device_mgr_fn_004c691c |  |  |
| AM-057 | P3 | todo | `0x004C706E..0x004C91DE` | 8,560 | code | FUN_004c706e, FUN_004c70b4, FUN_004c70e4, FUN_004c7116 |  |  |
| AM-058 | P2 | todo | `0x004C91E0..0x004CA662` | 5,250 | code | uled_mspi_term, uled_driver_identify, uled_mspi_init, uled_clearScreen, uled_driver_init |  |  |
| AM-059 | P3 | todo | `0x004CA80A..0x004CAFBE` | 1,972 | code | FUN_004ca80a, FUN_004ca812, FUN_004ca81a, FUN_004ca822 |  |  |
| AM-060 | P3 | todo | `0x004CAFBE..0x004CD550` | 9,618 | code | FUN_004cafbe, FUN_004cafd4, FUN_004cafea, FUN_004cb000 |  |  |
| AM-061 | P3 | todo | `0x004CD558..0x004CF554` | 8,188 | code | FUN_004cd558, FUN_004cd604, FUN_004cd60e, FUN_004cd6e4 |  |  |
| AM-062 | P3 | todo | `0x004CF564..0x004CFD84` | 2,080 | code | FUN_004cf564, FUN_004cf570, FUN_004cf5ec, FUN_004cf648 |  |  |
| AM-063 | P3 | todo | `0x004CFD84..0x004D039E` | 1,562 | code | FUN_004cfd84, FUN_004cfda0, FUN_004cfdb4, FUN_004cfdc0 |  |  |
| AM-064 | P1 | todo | `0x004D039E..0x004D3944` | 13,734 | code | threadBleWsfTakeTxReady, thread_ble_wsf_wait_tx_ready, thread_ble_wsf_tx_complete_notify |  |  |
| AM-065 | P3 | todo | `0x004D3944..0x004D4354` | 2,576 | code | FUN_004d3944, FUN_004d3952, FUN_004d3992, FUN_004d39e4 |  |  |
| AM-066 | P3 | todo | `0x004D4354..0x004D483E` | 1,258 | code | FUN_004d4354, FUN_004d43a4, FUN_004d43a8, FUN_004d43b4 |  |  |
| AM-067 | P3 | todo | `0x004D483E..0x004D522C` | 2,542 | code | FUN_004d483e, FUN_004d484a, FUN_004d4856, FUN_004d4862 |  |  |
| AM-068 | P2 | todo | `0x004D5278..0x004D9384` | 16,652 | code | semantic_whitelist_file_size_preserving_position, _parseJsonWhitelistToStruct, _printAppWhiteListInfo, _parseWhiteListFromFS, SVC_IsOnWhitelistByIdentifier |  |  |
| AM-069 | P3 | todo | `0x004D94B8..0x004DCBA8` | 14,064 | code | FUN_004d94b8, FUN_004d9522, FUN_004d9b34, FUN_004d9b4a |  |  |
| AM-070 | P3 | todo | `0x004DCC98..0x004E0286` | 13,806 | code | FUN_004dcc98, FUN_004dccd8, FUN_004dcd0a, FUN_004dcd32 |  |  |
| AM-071 | P3 | todo | `0x004E033C..0x004E8DA6` | 35,434 | code | even_ai_tick_get, even_ai_layout_refresh, even_ai_stream_interval_get, even_ai_text_stream_service_get, even_ai_stream_init_from_service |  |  |
| AM-072 | P3 | todo | `0x004E92F4..0x004EC218` | 12,068 | code | FUN_004e92f4, FUN_004e9dd4, FUN_004e9e06, FUN_004e9e32 |  |  |
| AM-073 | P3 | todo | `0x004EC2DC..0x004EEBDC` | 10,496 | code | FUN_004ec2dc, FUN_004ece5c, FUN_004ecec4, FUN_004ecee8 |  |  |
| AM-074 | P3 | todo | `0x004EEBDC..0x004F153A` | 10,590 | code | FUN_004eebdc, FUN_004eef7c, FUN_004ef9a4, FUN_004efcb8 |  |  |
| AM-075 | P3 | todo | `0x004F1544..0x004F3F6E` | 10,794 | code | FUN_004f1544, FUN_004f18ac, FUN_004f1ab8, FUN_004f2210 |  |  |
| AM-076 | P3 | todo | `0x004F4030..0x004F6864` | 10,292 | code | FUN_004f4030, FUN_004f4670, FUN_004f4678, FUN_004f4688 |  |  |
| AM-077 | P3 | todo | `0x004F6880..0x004F81D4` | 6,484 | code | FUN_004f6880, FUN_004f6a10, FUN_004f6d50, FUN_004f6d84 |  |  |
| AM-078 | P3 | todo | `0x004F81F0..0x004FAC3A` | 10,826 | code | FUN_004f81f0, FUN_004f8298, FUN_004f82d0, FUN_004f82e4 |  |  |
| AM-079 | P3 | todo | `0x004FAC74..0x0050072C` | 23,224 | code | quicklist_lock_storage, quicklist_unlock_storage, dashboard_watchface_manager_call_08, dashboard_watchface_manager_call_0c, dashboard_watchface_manager_call_14 |  |  |
| AM-080 | P3 | todo | `0x0050072C..0x00503568` | 11,836 | code | dashboard_watchface_manager_call_30, dashboard_watchface_manager_call_34, dashboard_watchface_manager_call_38, buzzer_pwm_config, buzzer_pwm_start |  |  |
| AM-081 | P2 | todo | `0x00503568..0x00505692` | 8,490 | code | hal_i2c_irq_enable, hal_i2c_power_down, hal_i2c_power_up, HAL_I2CInit, hal_i2c_transfer_full |  |  |
| AM-082 | P2 | todo | `0x00505692..0x00508ED2` | 14,400 | code | FUN_00505692, FUN_005056d2, FUN_00505888, FUN_0050594a |  |  |
| AM-083 | P2 | todo | `0x00508ED2..0x0050AC18` | 7,494 | code | APP_errorFaultHandler, ui_common_api_fn_00509c1c, ui_common_api_fn_00509c96, ui_common_api_fn_00509ca2, ui_common_api_fn_00509dfa |  |  |
| AM-084 | P3 | todo | `0x0050AC5C..0x0050CB30` | 7,892 | code | ui_onboarding_stock_sub_0050CA24, ui_onboarding_stock_sub_0050CA56, ui_onboarding_stock_sub_0050CB28 |  |  |
| AM-085 | P2 | todo | `0x0050CB30..0x0050F88A` | 11,610 | code | ui_onboarding_stock_sub_0050CB30, ui_onboarding_stock_sub_0050D35A, ui_onboarding_stock_sub_0050D532, ui_onboarding_stock_sub_0050D578, ui_onboarding_stock_sub_ |  |  |
| AM-086 | P3 | todo | `0x0050F8CC..0x00513070` | 14,244 | code | input_tick_read, thread_input_state_enter, thread_input_state_exit, INP_ResourceInit, INP_HardwareInit |  |  |
| AM-087 | P3 | todo | `0x00513070..0x00513E2E` | 3,518 | code | input_msg_send_id1, input_msg_send_id2, input_msg_send_id3, input_msg_send_id4, input_queue_drain |  |  |
| AM-088 | P3 | todo | `0x00513E2E..0x0051B8F0` | 31,426 | code | FUN_00513e2e |  |  |
| AM-089 | P3 | todo | `0x00513E4C..0x00514846` | 2,554 | code | FUN_00513e4c, FUN_00513e56, FUN_00513ed0, FUN_00513eee |  |  |
| AM-090 | P3 | todo | `0x00514846..0x00514F34` | 1,774 | code | FUN_00514846, FUN_00514aec, FUN_00514b7c, FUN_00514cf2 |  |  |
| AM-091 | P3 | todo | `0x00514F3C..0x0051B8F0` | 27,060 | code | FUN_00514f3c |  |  |
| AM-092 | P3 | todo | `0x00514F60..0x00517788` | 10,280 | code | FUN_00514f60, FUN_00515048, FUN_00515096, FUN_005150ea |  |  |
| AM-093 | P3 | todo | `0x0051778C..0x00519280` | 6,900 | code | FUN_0051778c, FUN_00517796, FUN_005177a4, FUN_0051785c |  |  |
| AM-094 | P3 | todo | `0x00519290..0x0051B8EA` | 9,818 | code | FUN_00519290, FUN_0051a660, FUN_0051a694, FUN_0051a8ec |  |  |
| AM-095 | P2 | todo | `0x0051D2E0..0x0051F78E` | 9,390 | code | FUN_0051d2e0 |  |  |
| AM-096 | P2 | todo | `0x0051F798..0x005202D0` | 2,872 | code | FUN_0051f798 |  |  |
| AM-097 | P3 | todo | `0x005202EC..0x00522B30` | 10,308 | code | FUN_005202ec, FUN_005223a2, FUN_00522400, FUN_005224b6 |  |  |
| AM-098 | P3 | todo | `0x00522B30..0x00524588` | 6,744 | code | FUN_00522b30, FUN_00522db4, FUN_00522e9c, FUN_00522f1c |  |  |
| AM-099 | P3 | todo | `0x00524588..0x0052502A` | 2,722 | code | FUN_00524588, FUN_005245e0, FUN_00524606, FUN_00524690 |  |  |
| AM-100 | P3 | todo | `0x0052502A..0x005267EE` | 6,084 | code | FUN_0052502a, FUN_0052504c, FUN_005250a2, FUN_005250de |  |  |
| AM-101 | P3 | todo | `0x00526814..0x005274F6` | 3,298 | code | FUN_00526814, FUN_0052687e, FUN_00526944, FUN_00526a02 |  |  |
| AM-102 | P3 | todo | `0x00527508..0x00528914` | 5,132 | code | FUN_00527508, FUN_005278c2, FUN_0052797a, FUN_0052798c |  |  |
| AM-103 | P3 | todo | `0x00528914..0x00529262` | 2,382 | code | FUN_00528914, FUN_00528928, FUN_00528936, FUN_00528992 |  |  |
| AM-104 | P3 | todo | `0x00529262..0x00529F62` | 3,328 | code | thunk_FUN_005292c8 |  |  |
| AM-105 | P1 | todo | `0x00529F8E..0x0052B5A2` | 5,652 | code | HciDisconnectCmd, HciLeConnUpdateCmd, HciLeCreateConnCmd, HciLeCreateConnCancelCmd, HciLeRemoteConnParamReqReply |  |  |
| AM-106 | P3 | todo | `0x0052B5A2..0x0052DF50` | 10,670 | code | HciLeStartEncryptionCmd, HciReadBdAddrCmd, HciReadBufSizeCmd, HciReadRssiCmd, HciSetEventMaskCmd |  |  |
| AM-107 | P3 | todo | `0x0052DF50..0x0052EFEC` | 4,252 | code | FUN_0052df50, FUN_0052e058, FUN_0052e072, FUN_0052e0a2 |  |  |
| AM-108 | P3 | todo | `0x0052EFEC..0x005369EA` | 31,230 | code | FUN_0052efec, FUN_0052f094, FUN_0052f0f8, FUN_0052f38c |  |  |
| AM-109 | P2 | todo | `0x00536A00..0x0053935C` | 10,588 | code | threadBleProductionLoopInit, _thread_resource_init, threadBleProductionStart, threadBleProductionEnter, threadBleProductionReady |  |  |
| AM-110 | P3 | todo | `0x0053935C..0x0053B076` | 7,450 | code | bq25180_write_register, bq25180_read_register, bq25180_update_field, bq25180_configure_event_mask, bq25180_mask_events |  |  |
| AM-111 | P3 | todo | `0x0053B076..0x0053DB3C` | 10,950 | code | bq27427_i2c_read_block, bq27427_i2c_write_block, bq27427_cfgupdate_priv, AUD_MessageProcesser, AUD_SendMessage |  |  |
| AM-112 | P3 | todo | `0x0053DB3C..0x00540036` | 9,466 | code | FUN_0053db3c, FUN_0053dc24, FUN_0053dc38, FUN_0053df00 |  |  |
| AM-113 | P3 | todo | `0x00540036..0x00542A52` | 10,780 | code | _flashDBInit, _flashDBRead, _flashDBWrite, _flashDBMutexInit, _flashDBMutexUnlock |  |  |
| AM-114 | P2 | todo | `0x00542A52..0x00544CD4` | 8,834 | code | FUN_00542a52, FUN_00542a80, FUN_00542c20, FUN_00542d48 |  |  |
| AM-115 | P3 | todo | `0x00544CEC..0x00547868` | 11,132 | code | FUN_00544cec, FUN_00544cf6, FUN_00544d60, FUN_00544f6c |  |  |
| AM-116 | P3 | todo | `0x0054787C..0x00549B6C` | 8,944 | code | FUN_0054787c, FUN_005479c8, FUN_00547abc, FUN_00547ad2 |  |  |
| AM-117 | P3 | todo | `0x00549C24..0x0054C3F2` | 10,190 | code | FUN_00549c24, FUN_0054c1f2, FUN_0054c240, FUN_0054c268 |  |  |
| AM-118 | P3 | todo | `0x0054C3F2..0x0054EF06` | 11,028 | code | FUN_0054c3f2, FUN_0054c5b0, FUN_0054c83c, FUN_0054c844 |  |  |
| AM-119 | P3 | todo | `0x0054EF08..0x005511B4` | 8,876 | code | AUDM_activeAppCount, AUDM_appAcquire, AUDM_appRelease, AUDM_SendSyncMsgToPeer, AUDM_common_data_handler |  |  |
| AM-120 | P3 | todo | `0x005511BC..0x0055462E` | 13,426 | code | text_stream_current_text, text_stream_pending_text, text_stream_current_length, text_stream_pending_length, text_stream_reset |  |  |
| AM-121 | P3 | todo | `0x0055462E..0x0055819E` | 15,216 | code | FUN_0055462e, FUN_0055468c, FUN_005546be, FUN_005548c4 |  |  |
| AM-122 | P3 | todo | `0x00558632..0x0055CC10` | 17,886 | code | FUN_00558632, FUN_0055876a, FUN_00558804, FUN_0055b2a4 |  |  |
| AM-123 | P3 | todo | `0x0055CC1C..0x0055E262` | 5,702 | code | FUN_0055cc1c, FUN_0055cf40, FUN_0055d280, FUN_0055d2c2 |  |  |
| AM-124 | P3 | todo | `0x0055E288..0x0055EFE6` | 3,422 | code | FUN_0055e288, FUN_0055e2a6, FUN_0055e2ce, FUN_0055e346 |  |  |
| AM-125 | P3 | todo | `0x0055EFF0..0x0055FACE` | 2,782 | code | FUN_0055eff0, FUN_0055f07a, FUN_0055f0d8, FUN_0055f134 |  |  |
| AM-126 | P3 | todo | `0x0055FACE..0x005657D4` | 23,814 | code | FUN_0055face, FUN_0055fad8, FUN_0055fae2, FUN_0055fb7c |  |  |
| AM-127 | P2 | todo | `0x005657D8..0x00568176` | 10,654 | code | FUN_005657d8, FUN_00567230, FUN_005675a8, FUN_005675b4 |  |  |
| AM-128 | P3 | todo | `0x00568176..0x00569954` | 6,110 | code | FUN_00568176, FUN_005682de, FUN_0056834a, FUN_005683f2 |  |  |
| AM-129 | P2 | todo | `0x00569954..0x0057E220` | 84,172 | code | service_audio_pcm_sample_bytes, SVC_PcmAppRegister, SVC_PcmAppUnregister, SVC_PcmAppProcessData, service_audio_format_recording_path |  |  |
| AM-130 | P3 | todo | `0x0057E220..0x00582924` | 18,180 | code | FUN_0057e220, FUN_0057e268, FUN_0057e2f6, FUN_0057e38c |  |  |
| AM-131 | P2 | todo | `0x00582924..0x00584EE4` | 9,664 | code | FUN_00582924, FUN_00582942, FUN_00582960, FUN_005829e0 |  |  |
| AM-132 | P2 | todo | `0x00585134..0x00587238` | 8,452 | code | navigation_send_type_1_allocating, navigation_send_type_13_allocating, navigation_send_type_17_allocating, navigation_send_type_16_allocating, navigation_send_t |  |  |
| AM-133 | P3 | todo | `0x00587240..0x00589EB6` | 11,382 | code | navigation_send_type_1_shared, navigation_icon_name_for_code, navigation_record_second_field_lookup, navigation_record_third_field_lookup, navigation_apply_name |  |  |
| AM-134 | P2 | todo | `0x0058A130..0x0058C892` | 10,082 | code | page_data_lock, semantic_page_data_unlock, teleprompt_preload_timer_ensure_created, semantic_page_to_slot, semantic_slot_loaded |  |  |
| AM-135 | P2 | todo | `0x0058C892..0x0058F8E4` | 12,370 | code | production_pcm_callback_single, production_codec_mic_func_init, production_codec_mic_func_deinit, production_pdm_mic_func_init, production_pdm_mic_func_deinit |  |  |
| AM-136 | P3 | todo | `0x0058F8E4..0x00590F78` | 5,780 | code | FUN_0058f8e4, FUN_0058f922, FUN_0058f92c, FUN_0058f936 |  |  |
| AM-137 | P2 | todo | `0x00590F78..0x0059364A` | 9,938 | code | jbd4010_vtable_init, jbd4010_write_command, jbd4010_write_data_block, jbd4010_read_response, jbd4010_read_die_response |  |  |
| AM-138 | P2 | todo | `0x00593660..0x00596C98` | 13,880 | code | jbd4010_standby_mode, am_devices_jbd4010_status_check_and_recovery |  |  |
| AM-139 | P2 | todo | `0x00596C98..0x0059758E` | 2,294 | code | td_ring_index_wrap, td_session_ring_reset, td_state_reset, td_ring_reset_wrapper, td_notify_state_clear |  |  |
| AM-140 | P3 | todo | `0x0059758E..0x0059898A` | 5,116 | code | td_flag_b_get, terminal_data_start_response_timer, td_record_timer_clear, td_record_flags_clear_all, td_record_elapsed_get |  |  |
| AM-141 | P3 | todo | `0x0059898C..0x0059AA84` | 8,440 | code | FUN_0059898c, FUN_00598994, FUN_00598ab8, FUN_00598dec |  |  |
| AM-142 | P2 | todo | `0x0059AA84..0x0059D9D4` | 12,112 | code | NVIC_EnableIRQ, NVIC_SetPriority, mspi_transfer_callback, am_devices_mspi_device_reconfigure, am_devices_mspi_set_serail_mode |  |  |
| AM-143 | P2 | todo | `0x0059D9D4..0x005A05E0` | 11,276 | code | translate_ui_0059d9d4, translate_ui_0059db5c, translate_ui_0059db66, translate_ui_0059db80, translate_ui_0059db9a |  |  |
| AM-144 | P2 | todo | `0x005A05E0..0x005A3260` | 11,392 | code | FUN_005a05e0, FUN_005a0786, FUN_005a08e4, FUN_005a0a70 |  |  |
| AM-145 | P2 | todo | `0x005A326C..0x005A710A` | 16,030 | code | FUN_005a326c, FUN_005a34ca, FUN_005a35a4, FUN_005a36ac |  |  |
| AM-146 | P3 | todo | `0x005A710A..0x005A9628` | 9,502 | code | FUN_005a710a, FUN_005a719e, FUN_005a71ec, FUN_005a731e |  |  |
| AM-147 | P3 | todo | `0x005A9628..0x005B0120` | 27,384 | code | FUN_005a9628, FUN_005a9700, FUN_005a99e8, FUN_005a9f98 |  |  |
| AM-148 | P3 | todo | `0x005B0120..0x005B4000` | 16,096 | code | FUN_005b0120, FUN_005b01ca, FUN_005b0284, FUN_005b02e4 |  |  |
| AM-149 | P3 | todo | `0x005B4000..0x005B7966` | 14,694 | code | conversate_ui_send_start_request, conversate_ui_menu_input_handler, conversate_tag_extend_page_input_event_handler, conversate_tag_page_deinit |  |  |
| AM-150 | P3 | todo | `0x005B7966..0x005B9D1E` | 9,144 | code | FUN_005b7966, FUN_005b7a02, FUN_005b7a4c, FUN_005b7aba |  |  |
| AM-151 | P2 | todo | `0x005B9D1E..0x005BC690` | 10,610 | code | am_devices_mspi_hongshi_init, driver_a6ng_write_register, driver_a6ng_read_register, am_devices_mspi_hongshi_read_bank, am_devices_mspi_hongshi_configure |  |  |
| AM-152 | P2 | todo | `0x005BC690..0x005BF092` | 10,754 | code | driver_a6ng_set_gpio_output, am_devices_mspi_hongshi_setBrightness, am_devices_mspi_hongshi_read_chipId, am_device_mspi_hongshi_read_sn, driver_a6ng_clear_frame |  |  |
| AM-153 | P1 | todo | `0x005BF114..0x005C173E` | 9,770 | code | FUN_005bf114, FUN_005bf146, FUN_005bf24e, FUN_005bf298 |  |  |
| AM-154 | P1 | todo | `0x005C173E..0x005C2D30` | 5,618 | code | FUN_005c173e, FUN_005c17e0, FUN_005c1858, FUN_005c18fc |  |  |
| AM-155 | P3 | todo | `0x005C2D30..0x005C45E2` | 6,322 | code | thunk_FUN_005c379c |  |  |
| AM-156 | P3 | todo | `0x005C45E2..0x005C5ADC` | 5,370 | code | FUN_005c45e2, FUN_005c45ec, FUN_005c4732, FUN_005c48d8 |  |  |
| AM-157 | P1 | todo | `0x005C5CF0..0x005C78DE` | 7,150 | code | FUN_005c5cf0, FUN_005c5f38, FUN_005c6414, FUN_005c681c |  |  |
| AM-158 | P3 | todo | `0x005C78DE..0x005C8FB2` | 5,844 | code | FUN_005c78de, FUN_005c78e8, FUN_005c78f6, FUN_005c7900 |  |  |
| AM-159 | P1 | todo | `0x005C8FE8..0x005C9E68` | 3,712 | code | FUN_005c8fe8, FUN_005c8ffc, FUN_005c9314, FUN_005c931e |  |  |
| AM-160 | P1 | todo | `0x005C9E68..0x005CC70E` | 10,406 | code | FUN_005c9e68, FUN_005c9e74, FUN_005c9e7e, FUN_005c9e88 |  |  |
| AM-161 | P1 | todo | `0x005CC70E..0x005CD7AC` | 4,254 | code | FUN_005cc70e, FUN_005cc718, FUN_005cc722, FUN_005cc72c |  |  |
| AM-162 | P3 | todo | `0x005CD7AC..0x005D05E6` | 11,834 | code | FUN_005cd7ac, FUN_005cd7b6, FUN_005cd7c0, FUN_005cd7cc |  |  |
| AM-163 | P3 | todo | `0x005D05E6..0x005D1848` | 4,706 | code | FUN_005d05e6, FUN_005d0682, FUN_005d071c, FUN_005d0736 |  |  |
| AM-164 | P3 | todo | `0x005D185E..0x005D2A18` | 4,538 | code | FUN_005d185e, FUN_005d188a, FUN_005d18c8, FUN_005d18ee |  |  |
| AM-165 | P3 | todo | `0x005D2A18..0x005D350C` | 2,804 | code | FUN_005d2a18, FUN_005d2bae, FUN_005d2e0c, FUN_005d2ea8 |  |  |
| AM-166 | P3 | todo | `0x005D350C..0x005D4B14` | 5,640 | code | FUN_005d350c, FUN_005d351c, FUN_005d352e, FUN_005d3544 |  |  |
| AM-167 | P3 | todo | `0x005D4B14..0x005D72A8` | 10,132 | code | FUN_005d4b14, FUN_005d4b18, FUN_005d4b1c, FUN_005d4b20 |  |  |
| AM-168 | P3 | todo | `0x005D72A8..0x005D8BC0` | 6,424 | code | FUN_005d72a8, FUN_005d7340, FUN_005d739c, FUN_005d73d0 |  |  |
| AM-169 | P3 | todo | `0x005D8BC0..0x005D96F8` | 2,872 | code | FUN_005d8bc0, FUN_005d8c00, FUN_005d8c1e, FUN_005d8c3e |  |  |
| AM-170 | P3 | todo | `0x005D96F8..0x005DCE22` | 14,122 | code | FUN_005d96f8, FUN_005d9716, FUN_005d9840, FUN_005d9890 |  |  |
| AM-171 | P3 | todo | `0x005DCE22..0x005DF484` | 9,826 | code | FUN_005dce22, FUN_005dcff6, FUN_005dd39e, FUN_005dd584 |  |  |
| AM-172 | P3 | todo | `0x005DF484..0x005E1F44` | 10,944 | code | FUN_005df484, FUN_005df4d4, FUN_005df504, FUN_005df5b6 |  |  |
| AM-173 | P3 | todo | `0x005E1F44..0x005E818A` | 25,158 | code | terminal_request_display, semantic_terminal_reset_output_tracking |  |  |
| AM-174 | P2 | todo | `0x005E818A..0x005EA810` | 9,862 | code | terminal_message_session_matches, terminal_refresh_session_list_if_visible, semantic_terminal_state_allows_runtime_event, semantic_terminal_state_is_processing, |  |  |
| AM-175 | P3 | todo | `0x005EA810..0x005ECA64` | 8,788 | code | FUN_005ea810, FUN_005ea868, FUN_005ea8ce, FUN_005ea926 |  |  |
| AM-176 | P2 | todo | `0x005ECA64..0x005EE1F8` | 6,036 | code | tracepoint_role_char, tracepoint_parse_file_sequence, tracepoint_get_file_size, tracepoint_format_file_path, tracepoint_insert_file_sorted |  |  |
| AM-177 | P2 | todo | `0x005EE1F8..0x005F1556` | 13,150 | code | tracepoint_handle_request_file_name, tracepoint_handle_delete_file, tracepoint_handle_slave_file_list |  |  |
| AM-178 | P2 | todo | `0x005F1564..0x005F3960` | 9,212 | code | FUN_005f1564, FUN_005f1908, FUN_005f1a32, FUN_005f1bac |  |  |
| AM-179 | P2 | todo | `0x005F3960..0x005F4F2A` | 5,578 | code | FUN_005f3960, FUN_005f3ff0, FUN_005f404e, FUN_005f40d6 |  |  |
| AM-180 | P2 | todo | `0x005F4F2A..0x005F5A80` | 2,902 | code | FUN_005f4f2a, FUN_005f4f30, FUN_005f4f44, FUN_005f4f58 |  |  |
| AM-181 | P2 | todo | `0x005F5A80..0x005F63A2` | 2,338 | code | FUN_005f5a80, FUN_005f5a88, FUN_005f5a90, FUN_005f5aa6 |  |  |
| AM-182 | P2 | todo | `0x005F63A2..0x005F881C` | 9,338 | code | FUN_005f63a2, FUN_005f642c, FUN_005f64ee, FUN_005f658c |  |  |
| AM-183 | P2 | todo | `0x005F881C..0x005FA84A` | 8,238 | code | FUN_005f881c, FUN_005f89bc, FUN_005f8a38, FUN_005f8afa |  |  |

## Apollo main application - retained data, tables, and assets

Same flash as above. These regions have no recovered functions (or large non-code remainders).
Identify each structure from its referencing code (LVGL image/font descriptors, FreeType payloads,
Cordio/SMP tables, protobuf descriptors, string pools, peripheral descriptor tables) and give it
a source representation per XC-005: generated from source assets or authored C data with a
derivation. A byte array copied from the stock image does not close an item.

| ID | Pri | Status | Flash range | Bytes | Kind | Targets | Owner | Notes |
|---|---|---|---|---:|---|---|---|---|
| AD-001 | P3 | todo | `0x0045A6D0..0x00469BF4` | 62,756 | data | non-code region |  |  |
| AD-002 | P3 | todo | `0x00492CB4..0x0049AD0C` | 32,856 | data | non-code region |  |  |
| AD-003 | P3 | todo | `0x0049C070..0x0049F020` | 12,208 | data | non-code region |  |  |
| AD-004 | P3 | todo | `0x004E54C8..0x004FB1FA` | 89,394 | data | non-code region |  |  |
| AD-005 | P3 | todo | `0x00503FF0..0x005093D4` | 21,476 | data | non-code region |  |  |
| AD-006 | P3 | todo | `0x0054F356..0x0055894C` | 38,390 | data | non-code region |  |  |
| AD-007 | P3 | todo | `0x0057F550..0x005848FC` | 21,420 | data | non-code region |  |  |
| AD-008 | P3 | todo | `0x005B22BC..0x005BF7B8` | 54,524 | data | non-code region |  |  |
| AD-009 | P3 | todo | `0x005BF7BC..0x005CDB46` | 58,250 | data | non-code region |  |  |
| AD-010 | P3 | todo | `0x005DA080..0x005E267C` | 34,300 | data | non-code region |  |  |
| AD-011 | P3 | todo | `0x005E4228..0x005F958C` | 86,884 | data | non-code region |  |  |
| AD-012 | P3 | todo | `0x005FA132..0x0061A132` | 131,072 | data | non-code region part 1/7 |  |  |
| AD-013 | P3 | todo | `0x0061A132..0x0063A132` | 131,072 | data | non-code region part 2/7 |  |  |
| AD-014 | P3 | todo | `0x0063A132..0x0065A132` | 131,072 | data | non-code region part 3/7 |  |  |
| AD-015 | P3 | todo | `0x0065A132..0x0067A132` | 131,072 | data | non-code region part 4/7 |  |  |
| AD-016 | P3 | todo | `0x0067A132..0x0069A132` | 131,072 | data | non-code region part 5/7 |  |  |
| AD-017 | P3 | todo | `0x0069A132..0x006BA132` | 131,072 | data | non-code region part 6/7 |  |  |
| AD-018 | P3 | todo | `0x006BA132..0x006BECB0` | 19,326 | data | non-code region part 7/7 |  |  |
| AD-019 | P3 | todo | `0x006BEED0..0x006C92B8` | 41,960 | data | non-code region |  |  |
| AD-020 | P3 | todo | `0x006C92DB..0x006D0B64` | 30,857 | data | non-code region |  |  |
| AD-021 | P3 | todo | `0x006D12E0..0x006D33F8` | 8,472 | data | non-code region |  |  |
| AD-022 | P3 | todo | `0x006D3A18..0x006D7E7C` | 17,508 | data | non-code region |  |  |
| AD-023 | P3 | todo | `0x006D7EE8..0x006DBAC4` | 15,324 | data | non-code region |  |  |
| AD-024 | P3 | todo | `0x006DBB28..0x006FBB28` | 131,072 | data | non-code region part 1/2 |  |  |
| AD-025 | P3 | todo | `0x006FBB28..0x00718E50` | 119,592 | data | non-code region part 2/2 |  |  |
| AD-026 | P3 | todo | `0x00718E8C..0x007235E8` | 42,844 | data | non-code region |  |  |
| AD-027 | P3 | todo | `0x00723620..0x0073EF00` | 112,864 | data | non-code region |  |  |
| AD-028 | P3 | todo | `0x0073EF04..0x0075EF04` | 131,072 | data | non-code region part 1/2 |  |  |
| AD-029 | P3 | todo | `0x0075EF04..0x00771E1C` | 77,592 | data | non-code region part 2/2 |  |  |
| AD-030 | P3 | todo | `0x00771E53..0x0077BF8C` | 41,273 | data | non-code region |  |  |
| AD-031 | P3 | todo | `0x0077C064..0x007839B0` | 31,052 | data | non-code region |  |  |
| AD-032 | P3 | todo | `0x00783AB2..0x007892B0` | 22,526 | data | non-code region |  |  |
| AD-033 | P3 | todo | `0x0078949F..0x0078C2B4` | 11,797 | data | non-code region |  |  |
| AD-034 | P3 | todo | `0x0078C4B8..0x0078E74C` | 8,852 | data | non-code region |  |  |
| AD-035 | P3 | todo | `0x0078E95A..0x00794310` | 22,966 | data | non-code region |  |  |
| AD-036 | P3 | todo | `0x00438000..0x00441516` | 5,494 | data-sweep | 5494 non-code bytes across 16 official regions (literal pools/tables/strings) |  |  |
| AD-037 | P3 | todo | `0x00442030..0x0045A568` | 13,992 | data-sweep | 13992 non-code bytes across 79 official regions (literal pools/tables/strings) |  |  |
| AD-038 | P3 | todo | `0x0046A3D6..0x0047FFC4` | 13,172 | data-sweep | 13172 non-code bytes across 93 official regions (literal pools/tables/strings) |  |  |
| AD-039 | P3 | todo | `0x00480002..0x004A35B0` | 8,158 | data-sweep | 8158 non-code bytes across 53 official regions (literal pools/tables/strings) |  |  |
| AD-040 | P3 | todo | `0x004A35B0..0x004C23DE` | 20,864 | data-sweep | 20864 non-code bytes across 108 official regions (literal pools/tables/strings) |  |  |
| AD-041 | P3 | todo | `0x004C240E..0x004E0C0C` | 21,284 | data-sweep | 21284 non-code bytes across 56 official regions (literal pools/tables/strings) |  |  |
| AD-042 | P3 | todo | `0x004E1442..0x00500378` | 12,850 | data-sweep | 12850 non-code bytes across 45 official regions (literal pools/tables/strings) |  |  |
| AD-043 | P3 | todo | `0x005003F2..0x0052A3FC` | 26,230 | data-sweep | 26230 non-code bytes across 18 official regions (literal pools/tables/strings) |  |  |
| AD-044 | P3 | todo | `0x0052A614..0x005412E0` | 12,942 | data-sweep | 12942 non-code bytes across 91 official regions (literal pools/tables/strings) |  |  |
| AD-045 | P3 | todo | `0x005412E4..0x0055FCB4` | 7,524 | data-sweep | 7524 non-code bytes across 35 official regions (literal pools/tables/strings) |  |  |
| AD-046 | P3 | todo | `0x005608B0..0x0057F530` | 15,060 | data-sweep | 15060 non-code bytes across 64 official regions (literal pools/tables/strings) |  |  |
| AD-047 | P3 | todo | `0x00584960..0x005A4FA4` | 38,040 | data-sweep | 38040 non-code bytes across 31 official regions (literal pools/tables/strings) |  |  |
| AD-048 | P3 | todo | `0x005A4FA8..0x005B22BC` | 6,427 | data-sweep | 6427 non-code bytes across 14 official regions (literal pools/tables/strings) |  |  |
| AD-049 | P3 | todo | `0x005CDB7E..0x005DA080` | 4,848 | data-sweep | 4848 non-code bytes across 15 official regions (literal pools/tables/strings) |  |  |
| AD-050 | P3 | todo | `0x005E30E2..0x006BEED0` | 2,420 | data-sweep | 2420 non-code bytes across 10 official regions (literal pools/tables/strings) |  |  |
| AD-051 | P3 | todo | `0x006C92BB..0x006D3980` | 2,774 | data-sweep | 2774 non-code bytes across 4 official regions (literal pools/tables/strings) |  |  |
| AD-052 | P3 | todo | `0x00771E37..0x00794324` | 940 | data-sweep | 940 non-code bytes across 98 official regions (literal pools/tables/strings) |  |  |

## Apollo bootloader - retained bytes

Flash: `0x00410000..0x00438000` (64 KiB secure bootloader at 0x00400000 is out of scope).
Evidence: `g2/tools/manifests/g2-bootloader-*.tsv`, `g2/docs/research/g2-bootloader-*.md`,
`g2/tools/analyze_g2_bootloader_*.py`, and the dual-image littlefs/EasyLogger/AmbiqSuite audits.
Admission path: `g2/components/bootloader/core_overlay/` (in-place exact source or relocated
leaves with entry redirects), `make -C g2 bootloader-component`, then `make -C g2 source`.
No Ghidra harvest exists for the bootloader yet (XC-009); disassemble from the official blob.

| ID | Pri | Status | Flash range | Bytes | Kind | Targets | Owner | Notes |
|---|---|---|---|---:|---|---|---|---|
| BL-001 | P2 | failed | `0x00410000..0x00410D8A` | 3,146 | code-and-data | Official Apollo bootloader bytes before the source-replaced littlefs utility quartet; Official Apollo bootloader bytes between the source-replaced littlefs 32-b |  | started 2026-09-11 12:32 / 2026-09-11 13:10 failed: You've hit your session limit · resets 4:30pm (America/Chicago) |
| BL-002 | P2 | failed | `0x00410E36..0x00415590` | 18,266 | code-and-data | Official Apollo bootloader bytes before recovered redirect_init |  | started 2026-09-11 12:33 / 2026-09-11 13:10 failed: You've hit your session limit · resets 4:30pm (America/Chicago) |
| BL-003 | P2 | failed | `0x004155E8..0x0041A648` | 11,158 | code-and-data | Authenticated 0x200270D4 SRAM address literal retained between the event-flags set and wait wrappers; Authenticated EasyLogger CSI-start literal and alignment b |  | started 2026-09-11 12:34 / 2026-09-11 13:10 failed: You've hit your session limit · resets 4:30pm (America/Chicago) |
| BL-004 | P2 | failed | `0x0041A6DA..0x0041B854` | 4,296 | code-and-data | Authenticated EasyLogger percent-d format, mutex-handle, mutex-attribute, time-buffer, and unknown-name pointe; Authenticated bootloader compatibility bytes ret |  | started 2026-09-11 12:35 / 2026-09-11 13:10 failed: You've hit your session limit · resets 4:30pm (America/Chicago) |
| BL-005 | P2 | failed | `0x0041B862..0x0041F918` | 16,566 | code-and-data | Authenticated bootloader compatibility bytes retained between the EasyLogger output driver and four-channel tr |  | started 2026-09-11 12:36 / 2026-09-11 13:10 failed: You've hit your session limit · resets 4:30pm (America/Chicago) |
| BL-006 | P2 | todo | `0x0041F9B6..0x00428378` | 5,892 | code-and-data | Authenticated alignment and G2 MSPI state-base literal between initialize and configure; Authenticated alignment and literal pool between MSPI deinitialize and |  | started 2026-09-11 12:37 / 2026-09-11 13:10 partial: 0 of 5892 bytes admitted as source. Added a whole-image reachability/data-reference survey tool that corroborates all 77 official_blob regions as either confirm |
| BL-007 | P2 | failed | `0x004283E2..0x00428A94` | 1,714 | code-and-data | Authenticated retained literal, table, and alignment bytes between the source-owned SPOT-manager transitions |  | started 2026-09-11 12:38 / 2026-09-11 13:10 failed: You've hit your session limit · resets 4:30pm (America/Chicago) |
| BL-008 | P2 | failed | `0x00428BA8..0x0042B6B8` | 5,488 | code-and-data | Authenticated 28-byte literal and alignment gap before the hardware-state decoder; Authenticated SPOT-manager shared literals and alignment before the temperatu |  | started 2026-09-11 12:39 / 2026-09-11 13:10 failed: You've hit your session limit · resets 4:30pm (America/Chicago) |
| BL-009 | P2 | todo | `0x0042B9BA..0x00430470` | 5,978 | code-and-data | Authenticated four-byte literal/alignment gap between channel normalization and enumeration services; Authenticated fourteen-byte literal/alignment gap before t |  | started 2026-09-11 12:40 / 2026-09-11 13:10 partial: Census only, 0 bytes closed: 7/25 spans are real Thumb code not filler; 5 code spans + a 192B pointer table call/point into BL-005/BL-011/BL-012 (in progress). |
| BL-010 | P2 | failed | `0x00430610..0x00431E38` | 5,906 | code-and-data | Authenticated four-byte alignment gap before critical word transfer; Authenticated retained code and data between critical word transfer and platform service in |  | started 2026-09-11 12:41 / 2026-09-11 13:10 failed: You've hit your session limit · resets 4:30pm (America/Chicago) |
| BL-011 | P2 | failed | `0x00431E70..0x004329C4` | 2,754 | code-and-data | Authenticated alignment between the FPU initialization service and runtime startup dispatcher; Authenticated alignment between the runtime startup dispatcher an |  | started 2026-09-11 12:42 / 2026-09-11 13:10 failed: You've hit your session limit · resets 4:30pm (America/Chicago) |
| BL-012 | P2 | failed | `0x004329D2..0x00434477` | 6,821 | code-and-data | Authenticated retained bootloader bytes after the source-owned Cortex-M runtime startup tail |  | started 2026-09-11 12:43 / 2026-09-11 13:10 failed: You've hit your session limit · resets 4:30pm (America/Chicago) |

## EM9305 Bluetooth controller - retained application bytes

Flash: controller records `0x00300000` (224 B), `0x00300400` (656 B), `0x00302000` (FHDR),
application `0x00302400..0x00335BC8` (ARCv2 EM). Evidence: `g2/docs/research/em9305-*.md`,
`g2/tools/manifests/em9305-*.tsv`, `g2/research/corpus/em9305/`, `g2/tools/analyze_em9305_*.py`.
Most bytes are exact matches of proprietary Packetcraft controller / EM vendor objects for which
no source is available; closing them means clean-room C reconstruction from decompilation and the
public Packetcraft host conventions, admitted through `g2/components/em9305/source_overlay/`
(tail branches + relocated C in the same sector). Every EM item depends on XC-003 (ARC toolchain).

| ID | Pri | Status | Flash range | Bytes | Kind | Targets | Owner | Notes |
|---|---|---|---|---:|---|---|---|---|
| EM-001 | P2 | todo | `0x00300000..0x00303F68` | 7,096 | code-and-data | packetcraft_modern_controller:4, reconstructible_accessor:2, em_vendor_rom_stub:1 |  |  |
| EM-002 | P2 | todo | `0x00303F72..0x00304EB4` | 3,892 | code-and-data | packetcraft_modern_controller:4, reconstructible_accessor:1, provider-required:1 |  |  |
| EM-003 | P3 | todo | `0x00304EBA..0x003069B8` | 6,910 | code-and-data | em_vendor_system:4, packetcraft_modern_controller:1 |  |  |
| EM-004 | P2 | todo | `0x003069C2..0x00307DD8` | 5,128 | code-and-data | packetcraft_modern_controller:5, reconstructible_accessor:1, external_provider:1 |  |  |
| EM-005 | P3 | todo | `0x00307DE6..0x00309DE6` | 8,192 | code-and-data | packetcraft_modern_controller:3 |  |  |
| EM-006 | P3 | todo | `0x00309DE6..0x0030BDE6` | 8,192 | code-and-data | packetcraft_modern_controller:10, external_provider:2 |  |  |
| EM-007 | P3 | todo | `0x0030BDE6..0x0030DDE6` | 8,192 | code-and-data | packetcraft_modern_controller:7, external_provider:2 |  |  |
| EM-008 | P2 | todo | `0x0030DDE6..0x0030F710` | 6,432 | code-and-data | provider-required:3, packetcraft_modern_controller:2, em_vendor_system:2 |  |  |
| EM-009 | P2 | todo | `0x0030F72E..0x003108F4` | 4,528 | code-and-data | packetcraft_modern_controller:11, em_vendor_system:3, external_provider:1 |  |  |
| EM-010 | P2 | todo | `0x003108FE..0x003122F0` | 6,632 | code-and-data | em_vendor_system:5, named_provider_boundary:2, packetcraft_modern_controller:2 |  |  |
| EM-011 | P2 | todo | `0x003122FA..0x003137F4` | 5,344 | code-and-data | em_vendor_system:1, packetcraft_modern_controller:1, reconstructible_memory:1 |  |  |
| EM-012 | P3 | todo | `0x003137FA..0x003157FA` | 8,192 | code-and-data | packetcraft_modern_controller:4, external_provider:3, em_vendor_system:2 |  |  |
| EM-013 | P3 | todo | `0x003157FA..0x003177FA` | 8,192 | code-and-data | packetcraft_modern_controller:11 |  |  |
| EM-014 | P3 | todo | `0x003177FA..0x003197FA` | 8,192 | code-and-data | packetcraft_modern_controller:6, external_provider:1 |  |  |
| EM-015 | P3 | todo | `0x003197FA..0x0031B2F8` | 6,910 | code-and-data | packetcraft_modern_controller:4, external_provider:1 |  |  |
| EM-016 | P3 | todo | `0x0031B2FC..0x0031D2FC` | 8,192 | code-and-data | packetcraft_modern_controller:2 |  |  |
| EM-017 | P2 | todo | `0x0031D2FC..0x0031F2FC` | 8,192 | code-and-data | packetcraft_modern_controller:2, three_entry_master_connection_boundary:1, external_provider:1 |  |  |
| EM-018 | P3 | todo | `0x0031F2FC..0x003212FC` | 8,192 | code-and-data | packetcraft_modern_controller:2 |  |  |
| EM-019 | P2 | todo | `0x003212FC..0x003232FC` | 8,192 | code-and-data | lctrMstPerScanRxPerAdvPktPostHandler, lctrMstPerScanTransferOpCommit, lctrMstPerScanWithRspAbortOp, lctrMstPerScanWithRspCommitOp |  |  |
| EM-020 | P3 | todo | `0x003232FC..0x003252FC` | 8,192 | code-and-data | packetcraft_modern_controller:3, external_provider:1 |  |  |
| EM-021 | P3 | todo | `0x003252FC..0x003272FC` | 8,192 | code-and-data | packetcraft_modern_controller:7 |  |  |
| EM-022 | P3 | todo | `0x003272FC..0x003292FC` | 8,192 | code-and-data | packetcraft_modern_controller:1 |  |  |
| EM-023 | P2 | todo | `0x003292FC..0x0032B2FC` | 8,192 | code-and-data | lctrSlvConnEndOp, lctrSlvConnExecute, lctrSlvConnExecuteSm, lctrSlvConnResetHandler, lctrSlvConnRxCompletion |  |  |
| EM-024 | P3 | todo | `0x0032B2FC..0x0032CAC4` | 6,088 | code-and-data | packetcraft_modern_controller:1 |  |  |
| EM-025 | P3 | todo | `0x0032CAE2..0x0032EAE2` | 8,192 | code-and-data | packetcraft_modern_controller:4 |  |  |
| EM-026 | P3 | todo | `0x0032EAE2..0x00330AE2` | 8,192 | code-and-data | unnamed retained controller bytes |  |  |
| EM-027 | P3 | todo | `0x00330AE2..0x00332AE2` | 8,192 | code-and-data | unnamed retained controller bytes |  |  |
| EM-028 | P3 | todo | `0x00332AE2..0x00332FC4` | 1,250 | code-and-data | external_provider:1 |  |  |
| EM-029 | P3 | todo | `0x00333062..0x00335062` | 8,192 | code-and-data | packetcraft_modern_controller:3 |  |  |
| EM-030 | P3 | todo | `0x00335062..0x00335BC8` | 2,918 | code-and-data | unnamed retained controller bytes |  |  |

## GX8002 codec/DSP - retained stock bytes (package offsets; runtime addresses where resolved)

Two-segment FWPK: UART boot stages load to IRAM `0x10000000`/`0x10002800`; the dual BINH main
image is written to codec SPI-NOR offset 0 (image A stage-2 XIP text runs from the public XIP
base `0x10200000`, SRAM text at `0x10023400`; image B SRAM text at `0x10003000`).
`Flash range` below is the resolved runtime address where the section map gives one, otherwise
the package offset; `remaining-work.json` always carries both. Evidence:
`g2/docs/research/gx8002-*.md` (700+ audits), `gx8002-upstream-object-candidates.json` (68 named
driver symbols from the NationalChip LVP KWS SDK), `gx8002-known-function-harvest.json`, and the
C-SKY Ghidra processor. Admission path: C in `g2/components/shared/gx8002/`, a
`tools/verify_gx8002_<x>.py` decoded-trace verifier, `tests/test_gx8002_<x>.py`, registration in
`tools/build_gx8002_source_candidate.py`, `make -C g2 gx8002-source-candidate`, then
`make -C g2 codec-source-experimental`. Public SDK C may be used under its MIT license; the SDK's
prebuilt `.o`/`.a` files must never be linked.

| ID | Pri | Status | Flash range | Bytes | Kind | Targets | Owner | Notes |
|---|---|---|---|---:|---|---|---|---|
| CD-001 | P1 | todo | `0x10000000..0x10002000` | 8,192 | code | UART boot stage 1 (IRAM) (1 retained span) |  | started 2026-09-11 12:31 / 2026-09-11 13:10 partial: Fixed CK804EF decode of the retained 8,192B UART boot stage-1 span; mapped vector table/reset/div-mod/baud routines and a chain-load hint. No bytes reclassified |
| CD-002 | P1 | todo | `0x10002000..0x10002800` | 2,048 | code | UART boot stage 1 (IRAM) (1 retained span) |  | started 2026-09-11 12:32 / 2026-09-11 13:10 partial: Range is stage1 .data/.bss (87.5% zero), not code; found non-coincidental uart_new_baudrate=115200 match to vendored grus SDK spl.c, but rebuild only reached ~1 |
| CD-003 | P1 | failed | `0x10002800..0x10003194` | 2,452 | code | UART boot stage 2 (IRAM) (1 retained span) |  | started 2026-09-11 12:34 / 2026-09-11 13:10 failed: agent exited 0 without a result file |
| CD-004 | P1 | failed | `0x100031B4..0x100051B4` | 8,192 | code | UART boot stage 2 (IRAM) (1 retained span) |  | started 2026-09-11 12:35 / 2026-09-11 13:10 failed: You've hit your session limit · resets 4:30pm (America/Chicago) |
| CD-005 | P1 | failed | `0x100051B4..0x100071B4` | 8,192 | code | UART boot stage 2 (IRAM) (1 retained span) |  | started 2026-09-11 12:36 / 2026-09-11 13:10 failed: You've hit your session limit · resets 4:30pm (America/Chicago) |
| CD-006 | P1 | failed | `0x100071B4..0x100091B4` | 8,192 | code | UART boot stage 2 (IRAM) (1 retained span) |  | started 2026-09-11 12:37 / 2026-09-11 13:10 failed: You've hit your session limit · resets 4:30pm (America/Chicago) |
| CD-007 | P1 | failed | `0x100091B4..0x1000953C` | 904 | code | UART boot stage 2 (IRAM) (1 retained span) |  | started 2026-09-11 12:38 / 2026-09-11 13:10 failed: You've hit your session limit · resets 4:30pm (America/Chicago) |
| CD-008 | P1 | failed | `0x00958C..0x00B58C` | 8,192 | code | image A BINH header + stage-1 block (flash 0x0 -> IRAM 0x10000000, vectors at block+0x18) (1 retained span) |  | started 2026-09-11 12:39 / 2026-09-11 13:10 failed: You've hit your session limit · resets 4:30pm (America/Chicago) |
| CD-009 | P1 | failed | `0x00B58C..0x00C650` | 4,292 | code | image A BINH header + stage-1 block (flash 0x0 -> IRAM 0x10000000, vectors at block+0x18) (3 retained spans) |  | started 2026-09-11 12:40 / 2026-09-11 13:10 failed: You've hit your session limit · resets 4:30pm (America/Chicago) |
| CD-010 | P1 | failed | `0x102030E4..0x10204984` | 5,560 | code | image A stage-2 XIP text (executes in place; public XIP base 0x10200000 + flash offset) (12 retained spans) |  | started 2026-09-11 12:41 / 2026-09-11 13:10 failed: You've hit your session limit · resets 4:30pm (America/Chicago) |
| CD-011 | P1 | failed | `0x102049B0..0x10207AC0` | 6,548 | code | image A stage-2 XIP text (executes in place; public XIP base 0x10200000 + flash offset) (12 retained spans) |  | started 2026-09-11 12:42 / 2026-09-11 13:10 failed: You've hit your session limit · resets 4:30pm (America/Chicago) |
| CD-012 | P1 | failed | `0x10207ADC..0x102099CC` | 6,546 | code | image A stage-2 XIP text (executes in place; public XIP base 0x10200000 + flash offset) (12 retained spans) |  | started 2026-09-11 12:42 / 2026-09-11 13:10 failed: You've hit your session limit · resets 4:30pm (America/Chicago) |
| CD-013 | P1 | todo | `0x10209A6C..0x1020BE1C` | 7,418 | code | image A stage-2 XIP text (executes in place; public XIP base 0x10200000 + flash offset) (10 retained spans) |  |  |
| CD-014 | P1 | todo | `0x10023400..0x10026884` | 5,977 | code | image A SRAM text (IRAM 0x10023400, entry 0x10023500) (16 retained spans) |  |  |
| CD-015 | P2 | todo | `0x100268C8..0x10026D7C` | 1,028 | data | image A SRAM data (0x100264E8) (2 retained spans) |  |  |
| CD-016 | P3 | todo | `0x20003304..0x200056D0` | 9,164 | accelerator-program | image A KWS NPU command stream (DRAM 0x20003304) (1 retained span) |  |  |
| CD-017 | P3 | todo | `0x200056D0..0x2000D6D0` | 32,768 | model | image A KWS model weights (DRAM 0x200056D0) (1 retained span) |  |  |
| CD-018 | P3 | todo | `0x2000D6D0..0x200156D0` | 32,768 | model | image A KWS model weights (DRAM 0x200056D0) (1 retained span) |  |  |
| CD-019 | P3 | todo | `0x200156D0..0x2001D6D0` | 32,768 | model | image A KWS model weights (DRAM 0x200056D0) (1 retained span) |  |  |
| CD-020 | P3 | todo | `0x2001D6D0..0x20022EB0` | 22,496 | model | image A KWS model weights (DRAM 0x200056D0) (1 retained span) |  |  |
| CD-021 | P1 | todo | `0x03893C..0x03A93C` | 8,192 | code | image B BINH header + stage-1 block (1 retained span) |  |  |
| CD-022 | P1 | todo | `0x03A93C..0x03B940` | 4,100 | code | image B BINH header + stage-1 block (1 retained span) |  |  |
| CD-023 | P1 | todo | `0x10003000..0x10004D94` | 7,572 | code | image B SRAM text (IRAM 0x10003000, entry 0x10003100) (1 retained span) |  |  |
| CD-024 | P1 | todo | `0x10004DB4..0x10005C10` | 3,478 | code | image B SRAM text (IRAM 0x10003000, entry 0x10003100) (5 retained spans) |  |  |
| CD-025 | P1 | todo | `0x10005C30..0x10007C30` | 8,192 | code | image B SRAM text (IRAM 0x10003000, entry 0x10003100) (1 retained span) |  |  |
| CD-026 | P1 | todo | `0x10007C30..0x10008048` | 1,048 | code | image B SRAM text (IRAM 0x10003000, entry 0x10003100) (1 retained span) |  |  |
| CD-027 | P1 | todo | `0x100080F4..0x1000A0F4` | 8,192 | code | image B SRAM text (IRAM 0x10003000, entry 0x10003100) (1 retained span) |  |  |
| CD-028 | P1 | todo | `0x1000A0F4..0x1000C0F4` | 8,192 | code | image B SRAM text (IRAM 0x10003000, entry 0x10003100) (1 retained span) |  |  |
| CD-029 | P1 | todo | `0x1000C0F4..0x1000E0F4` | 8,192 | code | image B SRAM text (IRAM 0x10003000, entry 0x10003100) (1 retained span) |  |  |
| CD-030 | P1 | todo | `0x1000E0F4..0x100100F4` | 8,192 | code | image B SRAM text (IRAM 0x10003000, entry 0x10003100) (1 retained span) |  |  |
| CD-031 | P1 | todo | `0x100100F4..0x100120F4` | 8,192 | code | image B SRAM text (IRAM 0x10003000, entry 0x10003100) (1 retained span) |  |  |
| CD-032 | P1 | todo | `0x100120F4..0x100140F4` | 8,192 | code | image B SRAM text (IRAM 0x10003000, entry 0x10003100) (1 retained span) |  |  |
| CD-033 | P1 | todo | `0x100140F4..0x100160F4` | 8,192 | code | image B SRAM text (IRAM 0x10003000, entry 0x10003100) (1 retained span) |  |  |
| CD-034 | P1 | todo | `0x100160F4..0x1001651C` | 1,064 | code | image B SRAM text (IRAM 0x10003000, entry 0x10003100) (1 retained span) |  |  |
| CD-035 | P2 | todo | `0x1001651C..0x1001708C` | 2,928 | data | image B SRAM data (0x1001651C) (1 retained span) |  |  |

## PSoC 4000T touch controller

Shipped image `0x00000000..0x00008680` (34,432 B raw in a 32-byte FWPK wrapper). The candidate
source image (`g2/components/touch/source_image`, 31 TUs, 15,560 B) links with zero undefined
symbols but is not production-routed because resident-ABI facts could not be confirmed on hardware.
Software completion means routing it under explicit, documented assumptions and accounting for
the bytes it does not produce.

| ID | Pri | Status | Flash range | Bytes | Kind | Targets | Owner | Notes |
|---|---|---|---|---:|---|---|---|---|
| TC-001 | P1 | failed | `0x00000000..0x00008680` | 34,432 | routing | components/touch/source_image -> production provider in a source manifest profile |  | started 2026-09-11 12:31 / 2026-09-11 13:10 done: exit 1 but result says done: Routed 31-TU touch source image as touch's production source_build provider via new manifest; NVIC vector-slot config now explicit/tested, not prose. MMIO behav |
| TC-002 | P2 | todo | `0x00000000..0x00008680` | 19,442 | data-and-code-accounting | 19,442 typed-retained touch bytes not represented by the 15,560-byte source image |  | started 2026-09-11 12:33 / 2026-09-11 13:10 partial: Independently reconstructed+verified 134/19,442 typed-retained Touch bytes (scattered NOP/legacy-NOP padding) against pinned stock digests; not production-route |
| TC-003 | P3 | blocked | `0x00008680..0x00010000` | 0 | blocked-proprietary | resident flash >= 0x8680 (dispatch tables, HAL descriptors, resident DFU engine, boot vectors) is not shipped in any blob |  |  |

## STM32G0 charging case

Shipped image logical `0x08000000..0x0800D9C8` (55,752 B). The candidate source image
(`g2/components/case/source_image`, 8 TUs, 18,916 B) is link-complete but unrouted for the same
hardware-evidence reason. Same completion rule as touch.

| ID | Pri | Status | Flash range | Bytes | Kind | Targets | Owner | Notes |
|---|---|---|---|---:|---|---|---|---|
| CS-001 | P1 | failed | `0x08000000..0x0800D9C8` | 55,752 | routing | components/case/source_image -> production provider in a source manifest profile |  | started 2026-09-11 12:31 / 2026-09-11 13:10 failed: You've hit your session limit · resets 4:30pm (America/Chicago) |
| CS-002 | P2 | todo | `0x08000000..0x0800D9C8` | 40,866 | data-and-code-accounting | 40,866 typed-retained case bytes not produced by the 18,916-byte source image |  | started 2026-09-11 12:33 / 2026-09-11 13:10 partial: Reconciled the 40,866-byte case typed_external_or_unsupported bucket into 1,104 platform/2,120 gap/428 fill/7,826 strings/29,388 still-opaque; 0 bytes moved to |

## Cross-cutting tooling, gates, and toolchains

Items that unblock whole components or define what counts as done.

| ID | Pri | Status | Flash range | Bytes | Kind | Targets | Owner | Notes |
|---|---|---|---|---:|---|---|---|---|
| XC-001 | P1 | failed | `-` | 0 | tooling | source-only manifest and package gate |  | started 2026-09-11 12:32 / 2026-09-11 13:10 failed: You've hit your session limit · resets 4:30pm (America/Chicago) |
| XC-002 | P1 | todo | `-` | 0 | tooling | completion-readiness and transparent ledgers track progress |  | started 2026-09-11 12:33 / 2026-09-11 13:10 partial: Fixed 4 live census drifts blocking completion-readiness/license gates (regex false-positive + 3 stale MIT manifests, all now clean). Blocked on Touch-owned rec |
| XC-003 | P1 | failed | `-` | 0 | tooling | macOS ARC (EM9305) toolchain |  | started 2026-09-11 12:34 / 2026-09-11 13:10 failed: You've hit your session limit · resets 4:30pm (America/Chicago) |
| XC-004 | P2 | failed | `-` | 0 | tooling | transparent-image envelope fitting |  | started 2026-09-11 12:35 / 2026-09-11 13:10 failed: You've hit your session limit · resets 4:30pm (America/Chicago) |
| XC-005 | P2 | done | `-` | 0 | tooling | Apollo data/asset source representation | claude-sonnet-5 session=2cc368af-ffba-42f4-a767-ef7109636521 run=20260911-123100 | started 2026-09-11 12:36 / 2026-09-11 13:10 done: Built+tested generator tooling for LVGL images/fonts, string pools, and nanopb protobuf descriptors; documented no-new-tool decisions for Cordio tables and Free |
| XC-006 | P2 | todo | `-` | 0 | tooling | codec model and NPU command source pipeline |  | started 2026-09-11 12:37 / 2026-09-11 13:10 partial: Built source-authored gxDNN command emitter+half quantizer (copy/tensor_vector/tensor_tensor, oracle-verified). 9,164 cmd + 120,800 weight bytes still retained: |
| XC-007 | P2 | failed | `-` | 0 | tooling | codec KWS parameter and data reconstruction |  | started 2026-09-11 12:38 / 2026-09-11 13:10 failed: You've hit your session limit · resets 4:30pm (America/Chicago) |
| XC-008 | P3 | todo | `-` | 0 | tooling | documentation re-pin sweep |  | started 2026-09-11 12:39 / 2026-09-11 13:10 partial: Re-pinned stale docs/linux-reproducible-build.md hash (commit d794c28e drifted it, benign rename). Other 3 pinned docs already matched; no new audit prose to fo |
| XC-009 | P3 | failed | `-` | 0 | tooling | bootloader Ghidra harvest |  | started 2026-09-11 12:40 / 2026-09-11 13:10 failed: You've hit your session limit · resets 4:30pm (America/Chicago) |

## Definition of done for a row

1. Every executable byte in the range is produced by reviewed C (or reviewed assembly where the
   ABI forces it) that is production-routed by the component build; entry addresses and caller
   contracts are preserved or the change is a documented, tested divergence.
2. Every data byte in the range has a source-authored representation or generator.
3. Narrow tests pass, the component build passes, `make -C g2 source` (or the component's
   candidate build) places the result with zero unresolved regions, and no trap/copied-array
   remains for the range in the transparent ledger.
4. A research audit (`g2/docs/research/<family>-<closure>.md`), a dated `g2/docs/progress.md`
   entry, and a checkpoint in `g2/docs/source-only-goal.md` record what was proven and what remains.
5. No hardware operation was performed; hardware qualification stays explicitly deferred.
