# Apollo core-overlay provenance and license

`core_helpers.c`, `evenhub_decompression.c`, `evenhub_container.c`,
`evenhub_lifecycle.c`, `evenhub_page_event.c`, and
`evenhub_common_data.c`, `evenhub_ui_event.c`, and
`ui_module_registry.c`, `ui_display_switch.c`, `ui_startup_app.c`, and
`ui_onboarding_gate.c`, `ui_input_event.c`, `ui_display_thread.c`, and
`ui_display_callback.c`, `ui_display_setup.c`, and
`ui_display_initializer.c`, `runtime_string.c`, `runtime_strchr.c`, and
`runtime_ascii_fold.c`, `runtime_integer_format.c`,
`runtime_decimal_scale.c`, `runtime_emit_span.c`, and
`runtime_memory_zero.c`, `runtime_lookup_is_static.c`,
`runtime_byte_map_lookup.c`, `runtime_lookup_bucket_index.c`,
`runtime_style_init.c`, `runtime_style_reset.c`,
`runtime_style_remove_property.c`, `runtime_style_set_property.c`,
`runtime_byte_map_lookup_u8.c`, `runtime_transition_descriptor_init.c`,
`runtime_style_default_value.c`, `runtime_style_is_empty.c`,
`runtime_style_prop_lookup_flags.c`, `runtime_linked_list_init.c`,
`runtime_linked_list_insertions.c`, `runtime_linked_list_remove.c`,
`runtime_linked_list_clear_custom.c`, `runtime_linked_list_accessors.c`,
`runtime_linked_list_move_before.c`, and
`runtime_linked_list_pointer_setters.c`, `runtime_color_mix.c`,
`runtime_color_math.c`, `runtime_color_over32.c`, `runtime_theme.c`,
`runtime_theme_traversal.c`, and `runtime_format_parse_helpers.c`,
`format_span.c`, `format_buffer_writer.c`,
`format_varint.c`, `format_append.c`, `format_fixed.c`, and `format_field.c`
plus `format_scalar.c`, `format_complex.c`, `format_message.c`, and
`format_regular.c`, `format_default.c`, `format_repeated.c`, `format_value.c`,
`format_indirect.c`, `format_extension.c`, `log_format_dispatch.c`, and
`log_divide.c`, `log_format_helpers.c`, `log_format_core.c`, and
`log_format_float.c`, plus `lv_tick.c`, `lv_memory.c`, `lv_global.c`, and
`lv_init.c`, `lv_buffer_sync.c`, `lv_display_sync.c`, and
`lv_display_setup.c`, `lv_display_lock.c`, `lv_runtime.c`, and
`display_thread_init.c`, `display_runtime.c`, and
`display_manager_thread.c`, plus `display_queue_senders.c` and
`display_lifecycle.c`, plus the shared file
open/close/read/write/seek/tell/size/flush/remove/rename/mkdir/opendir/readdir/
closedir runtime and synchronized allocation/free/reallocation wrappers in
`file_runtime.c`, including their two-mutex initializer, and the
application-wide comparator in `memory_compare.c`, plus the BLE
message-transmit thread entry and lifecycle runtime in `ble_msgtx_thread.c`
and `ble_msgtx_runtime.c`, its setup/thread-handle lifecycle in
`ble_msgtx_thread_lifecycle.c`, and its queue/thread-flag dispatch path in
`ble_msgtx_dispatch.c`, including queue clearing, plus message construction,
backpressure, enqueue, and wakeup in `ble_msgtx_enqueue.c`, and the direct
protobuf-send and notification OTA gates plus the guarded OTA/left-side
protobuf sender, guarded OTA/left-side/command-role notification sender,
streaming notification, ungated transport-three sender, and EFS send/notify
wrappers in `ble_msgtx_pb_direct.c`, plus the variadic string-scanner adapter
and source input callback in `scan_string.c`, and the littlefs directory,
recovery, initialization, boot-count, flash callback, and sync cluster in
`file_system.c`, plus the CMSIS event-loop object initializer, blocking
worker, queue push, timer scheduler, delayed insertion, and delayed removal
cluster in `event_loop.c`, and the BLE connection-parameter immediate-update
and delayed-scheduling routine in `ble_connection_schedule.c`, plus both
connection-mode selectors in `ble_connection_mode.c`, the connection-mode
coordinator in `ble_connection_coordinator.c`, and its delayed callback in
`ble_connection_callback.c`, plus the remote connection-parameter handler in
`ble_connection_remote_parameters.c` and the connection-update event state
machine in `ble_connection_event.c`, plus the connection-global initializer
in `ble_connection_globals.c` and the stream/mode control helpers in
`ble_connection_control.c`, plus the connection-event message dispatcher in
`ble_connection_dispatch.c`, and the MRAM zero-region programmer and protected
update-flag setter in `mram_persistence.c`, plus the protected-MRAM record
diagnostic dump in `mram_diagnostic_dump.c` and two-pass protected-record
synchronizer in `mram_sync_records.c`, plus the protected-MRAM-to-RAM
record-list loader in `mram_load_records.c` and the split-transaction
single-record programmer in `mram_update_record.c`, plus the application
record-database update and replacement selector in `mram_app_db_update.c` and
record-deactivation adapter in `mram_deactivate_record.c` and record-activation
adapter in `mram_activate_record.c`, plus the conditional deactivation adapter
in `mram_deactivate_if_unconfirmed.c` and protected-record membership,
traversal, counting, presence, and oldest-selection helpers in
`mram_record_queries.c`, plus the threshold-evicting protected-record
allocator in `mram_allocate_record.c` and the record-list startup wrapper in
`mram_initialize_records.c`, plus the Cordio application-database address
resolver in `mram_resolve_address.c` and resolved-address callback in
`mram_handle_resolved_address.c`, plus the application-database delete-all
adapter in `mram_delete_all_records.c`, the application-database address
lookup in `mram_find_by_address.c`, and the security-database LTK-request
lookup in `mram_find_by_ltk_request.c`, plus the key, peer-address, and
peer-address-type accessors in `mram_record_accessors.c`, and the Cordio
key-event writer in `mram_set_key.c`, plus the Cordio application-database
hash, cache, CCC, client-supported-features, discovery, handle-list,
sign-counter, and address-resolution accessors in `mram_record_metadata.c`,
and the Cordio resolving-list reload wrapper in
`mram_reload_resolving_list.c`,
plus the Cordio complete-record clearing wrapper in
`mram_clear_record_by_mac.c`,
and the protected-MRAM write verifier in
`mram_verify_write.c`,
plus the protected-MRAM record-status reporter in
`mram_show_records_status.c`,
and the Cordio record timestamp-update wrapper in
`mram_update_record_timestamp.c`,
plus the Cordio record timestamp-renumbering routine in
`mram_reset_record_timestamps.c`,
plus the Cordio persistent-record status reporter in
`mram_show_nvm_status.c`,
plus the Cordio pairing-failure handler in
`mram_handle_pairing_failure.c`,
`mram_clear_record_by_connection.c`,
`mram_dump_all_records.c`,
`efs_crc32c_msb.c`,
`mram_program_bytes.c`,
`aeabi_divmod.c`,
`status_packets.c`,
`lens_status_control.c`,
`sarc_state.c`,
`monotonic_time.c`,
`wall_time.c`,
`boot_identity.c`,
`tracepoint_defer.c`,
`tracepoint_storage.c`,
`tracepoint_file_io.c`,
`tracepoint_bootstrap.c`,
`onboarding_control.c`,
`onboarding_wear_status.c`,
`onboarding_flag_persist.c`,
`onboarding_flag_update.c`,
`onboarding_peer_flag.c`,
`onboarding_peer_flag_reply.c`,
`onboarding_process_sync.c`,
`onboarding_runtime_init.c`,
`rtos_timer_dynamic_create.c`,
`rtos_timer_static_create.c`,
`rtos_timer_initialize.c`,
`rtos_timer_command.c`,
`rtos_timer_reload.c`,
`rtos_timer_expire.c`,
`rtos_timer_service_loop.c`,
`rtos_timer_wait_or_expire.c`,
`rtos_timer_query.c`,
`rtos_timer_sample.c`,
`rtos_timer_insert.c`,
`rtos_timer_drain.c`,
`rtos_timer_switch_lists.c`,
`rtos_timer_runtime_initialize.c`,
`rtos_timer_is_active.c`,
`rtos_timer_get_context.c`,
`rtos_timer_pend_from_isr.c`,
`rtos_event_group_create.c`,
`rtos_event_group_wait.c`,
`rtos_event_group_test_wait_condition.c`,
`rtos_event_group_clear.c`,
`rtos_event_group_clear_from_isr.c`,
`rtos_event_group_get_bits_from_isr.c`,
`rtos_event_group_set.c`,
`rtos_event_group_set_callback.c`,
`rtos_event_group_set_from_isr.c`,
`rtos_event_group_clear_callback.c`,
are
openCFW source
implementations written from
the bounded behavioral evidence in `EVIDENCE.md`. They are licensed under
GPL-3.0-only so they can be compiled into the same overlay as the
GPL-3.0-only ring-gesture source.

`lv_init.c` also follows the enabled subsystem ordering and guards in LVGL
`v9.3.0`:
[`lvgl/lvgl`](https://github.com/lvgl/lvgl/blob/v9.3.0/src/lv_init.c).
Copyright (c) 2025 LVGL Kft. Its MIT terms are retained in
`LICENSE-LVGL-MIT`.

`runtime_format_out_reverse.c`, `runtime_ntoa_format.c`,
`runtime_ntoa_integer.c`, `runtime_ftoa.c`, `runtime_etoa.c`,
`runtime_strnlen_s.c`, `runtime_vsnprintf.c`, and
`runtime_printf_wrappers.c` are bounded adaptations of the reverse-output,
integer, floating-point, bounded-length, variadic-dispatch, and public-wrapper
functions from mpaland/printf at
commit `d3b984684bb8a8bdc48cc7a1abecb93ce59bbe3e`:
[`mpaland/printf`](https://github.com/mpaland/printf/blob/d3b984684bb8a8bdc48cc7a1abecb93ce59bbe3e/printf.c).
`runtime_vsnprintf.c` additionally contains the independently recovered G2
pointer-formatting and recursive `%PV`/`%pV` extensions.
Copyright (c) 2014-2019 Marco Paland. Its MIT terms are retained in
`LICENSE-mpaland-MIT`.

`runtime_bounded_string_length.c`, `runtime_heap_coordinator.c`,
`runtime_heap_adapters.c`, and `runtime_heap_wrappers.c` are bounded openCFW
reimplementations licensed under MIT. The coordinator owns the generic heap
descriptor initialization, locking, accounting, allocation, aligned-
allocation, reallocation, and free behavior. The coordinator's TLSF calls now
enter the source-integrated allocator described below through the reviewed
stock entry identities.

The production TinyFrame closure compiles the immutable `TinyFrame.c` and
`TinyFrame.h` blobs introduced by MightyPork/TinyFrame commit
`eb75483e035916ef9f3e9fce0d2ae389cb09785f`, together with the separately
recovered G2 configuration and openCFW object/transport boundary. Copyright
(c) 2017 Ondřej Hruška. Its MIT terms are retained in
`LICENSE-TinyFrame-MIT`.

`components/shared/freertos_cli/runtime_freertos_cli_get_parameter.c` is the
independently named production adaptation of `FreeRTOS_CLIGetParameter` from
the classic FreeRTOS+CLI V1.0.4-compatible source selected at commit
`43defa566cc440251dbd6b48d1fcca27f88cfcdd`. Copyright (C) 2017 Amazon.com,
Inc. or its affiliates. Its MIT permission and warranty notice is retained in
the production source and in `LICENSE-FreeRTOS-Plus-CLI-MIT`. The separately
named `_candidate` file remains a production-excluded qualification artifact.

`runtime_freertos_queue.c`, `runtime_freertos_queue_create.c`,
`runtime_freertos_queue_wrappers.c`,
`runtime_freertos_queue_state.c`,
`components/shared/freertos/runtime_freertos_queue_semaphore_take_upstream_candidate.c`,
`components/shared/freertos/runtime_freertos_queue_get_disinherit_priority_after_timeout.c`,
`runtime_freertos_list_initialise.c`,
`runtime_freertos_list_insert_end.c`, `runtime_freertos_list_insert.c`, and
`runtime_freertos_list_remove.c`, plus
`runtime_freertos_task_current.c`, `runtime_freertos_task_count.c`, and
`runtime_freertos_scheduler_state.c`, plus
`components/shared/freertos/runtime_freertos_tick_count.c` and
`components/shared/freertos/runtime_freertos_missed_yield.c`, and the
separately compiled
`runtime_freertos_pc_task_get_name.c`, are a bounded, freestanding port of
`xQueueGenericCreateStatic`, `xQueueGenericCreate`,
`prvInitialiseNewQueue`, `prvInitialiseMutex`, `xQueueCreateMutex`,
`xQueueCreateMutexStatic`, `xQueueCreateCountingSemaphoreStatic`,
`xQueueCreateCountingSemaphore`,
`xQueueGiveMutexRecursive`,
`xQueueTakeMutexRecursive`, `xQueueGenericSend`, and
`xQueueSemaphoreTake`, plus the private queue-empty and queue-full state
predicates from `queue.c`, plus `vListInitialise`, `vListInsertEnd`,
`vListInsert`, and `uxListRemove` from `list.c`, and
`xTaskGetCurrentTaskHandle`, `uxTaskGetNumberOfTasks`,
`xTaskGetSchedulerState`, `xTaskGetTickCount`,
`xTaskGetTickCountFromISR`, `vTaskMissedYield`, and `pcTaskGetName` from
`tasks.c`, from
FreeRTOS Kernel V10.5.1 pinned
to commit `def7d2df2b0506d3d249334974f51e427c17a41c`. Copyright (C)
2021 Amazon.com, Inc. or its affiliates. Its MIT terms are retained in
`LICENSE-FreeRTOS-MIT` and in the source file. The port preserves the recovered
80-byte G2 `Queue_t` ABI. The static and dynamic generic creators and their
private initializers retain explicit reset, `heap_4`, and assertion seams.
The three constructor wrappers call the source-owned generic creators and
mutex initializer; only the recovered G2 assertion target remains a
fixed-address compatibility seam.
Generic send calls the private full predicate as a source-to-source dependency.
The promoted semaphore/mutex take operation retains the authenticated stock
empty-predicate seam, and resolves its post-timeout priority calculation to the
appended upstream-derived source helper. Recursive give/take reach the public
operations; recursive take materializes the patched odd semaphore entry and
calls it with `BLX`. The task-query leaves retain the authenticated
G2 SRAM addresses for `pxCurrentTCB`, `uxCurrentNumberOfTasks`,
`xSchedulerRunning`, and `uxSchedulerSuspended` as explicit compatibility
state. `pcTaskGetName` additionally retains the recovered 32-byte task name at
TCB offset `0x34` and closes its fail-stop assertion directly over the
source-owned `ulSetInterruptMask` leaf. Other reviewed stock task, list, and
port helpers remain binary compatibility seams.

The 3,412-byte shared tick-count source has SHA-256
`948d1b2de6026adc7cf84a34a359c859c32126b3afcafe92c2347f5f7ab56363`;
its 1,186-byte header hashes to
`adc4065b3504a7eacb2e29e2d357636917e2b690afc49b265689e36d66171dae`.
It preserves the authenticated G2 32-bit atomic-tick configuration and one
volatile compatibility-state read from `xTickCount` word `0x20074A34`.
The complete official functions are `xTaskGetTickCount` at
`[0x00454EFE,0x00454F06)` and `xTaskGetTickCountFromISR` at
`[0x00454F06,0x00454F10)`; the latter begins at `0x00454F06`, while
`0x00454F08` is its second instruction and has no direct or stored entry
reference. The complete 18-byte pair has SHA-256
`d0b93ff29439d26b92dcd56fd012a9dab842364f7c5f4b4f7f39a27ed8cfe077`.
The normal getter has nine direct callers with ordered-address
SHA-256
`3b032511b7c47b3afe47149262380345e354dea6d00f2b9dda369d10ce89abcd`;
the ISR getter has one caller at `0x004490D6`.

Production places the source provider at
`[0x007B07EC,0x007B07F8)`, the normal getter at
`[0x007B07F8,0x007B07FC)`, and the ISR getter at
`[0x007B07FC,0x007B0800)`. The provider and getters are 20
`source_compiled` bytes. Two generated alignment bytes precede the provider,
and generated non-linking `B.W` plus NOP sequences cover all 18 stock bytes;
those alignment/redirect bytes are build products, not source ownership.
That preceding 115,932-byte overlay hashes to
`272ba0e0492b0c6b721adec53a007809158d6871ccdb7ec52d4b6ceadd4b4529`;
the 3,639,328-byte Apollo-main component hashes to
`615304858150f5ee6b7b4c62a714629375010c6f4ab20bea1b6958daa6a5b4af`;
and the 4,417,782-byte package hashes to
`3bf635fb81439451e67642dc5ce11dde47a1773bda8ef11c12b35cd9bbbec01d`.
These pins establish reproducible structural ownership only. Validation was
offline and hardware-free; no G2 was flashed, reset, or executed, and no
serial endpoint or debugger was accessed.

The 1,749-byte shared missed-yield source has SHA-256
`1f7ec93d00e35dcc4cf156d4559924493e46f6cc89c30de1ed7e53442177013c`;
its 1,055-byte header hashes to
`0008f68d1196ea92a33a8cfa7bee339733354ccf8d64b96279acf6a43a1a21af`.
It preserves the authenticated V10.5.1
`xYieldPending = pdTRUE` operation and binds the recovered G2 word at
`0x20074A44`. The complete official leaf is
`[0x004555E6,0x004555F0)`; its two callers remain at `0x00441FA2` and
`0x00441FD8`. The source leaf occupies `[0x007B0800,0x007B080E)` in the
canonical overlay. The preceding 115,946-byte overlay, 3,639,342-byte
component, and 4,417,796-byte package hash to
`a24cd67ac1d308b8812c329a294f3f07cbe9db4bc815be3fe081ba0c2fd9008c`,
`f037745e9b85d16fc048ba2fedb282f7fc498a524a90b803b652556e286cf77d`,
and
`f06fdc7a1e9034e72321680b35fbd542b12dad06135e6f01f701d670dba676ae`.

The preceding tranche additionally source-owns exact FreeRTOS-Kernel V10.5.1
`uxTaskResetEventItemValue` and `pvTaskIncrementMutexHeldCount`. Their
complete official spans are `[0x00455ACA,0x00455AE0)` and
`[0x00455AE0,0x00455AF6)`, both 22 bytes. Their source leaves occupy
`[0x007B0810,0x007B082A)` and `[0x007B082C,0x007B0844)`, after two
alignment bytes before each. Both bind the recovered `pxCurrentTCB` word at
`0x20074A20`; reset pins event-item `+0x18`, priority `+0x2C`, and 56
priorities, while mutex-held pins field `+0x64` and
`configUSE_MUTEXES=1`.

The preceding 116,000-byte overlay, 3,639,396-byte component, and
4,417,850-byte package hash to
`203b31ea09e03c919da51b4d194cab2c3325ad5d5eed3efc7464018af90e2059`,
`78375130a88e6ec0d14bc936b8f16f4535056344288419baba83d81fd4f3bdc3`,
and
`9ffe927fdb587db9fae07043d7dc0938d2519c95d29e71cd0dca021cadf31d85`.
The corresponding focused evidence is in
`docs/research/freertos-reset-event-item-value-source-boundary-audit.md` and
`docs/research/freertos-mutex-held-source-boundary-audit.md`.

That production tranche source-owned the authenticated V10.5.1
`vTaskSuspendAll` and `vTaskInternalSetTimeOutState` bodies. Suspend binds
the 32-bit nested scheduler depth at `0x20074A58`; timeout capture binds
`xNumOfOverflows` at `0x20074A48`, `xTickCount` at `0x20074A34`, and the
two-word `TimeOut_t` layout. Their complete stock spans are
`[0x00454D7C,0x00454D88)` and `[0x00455556,0x00455566)`. Canonical source
placement is `[0x007B0844,0x007B0854)` and
`[0x007B0854,0x007B0866)`; Linux placement is
`[0x007B0F7C,0x007B0F8C)` and `[0x007B0F8C,0x007B0F9E)`.

That tranche's canonical overlay, component, and package were 116,034,
3,639,430, and 4,417,884 bytes, with SHA-256 values
`d0b36ab3661f3b3487e3962bfe58d9f588f6a6f1ea14e1d9389f7e45d98094bd`,
`8a747653cc4d938e447197f2bec199933b68072318f0743e3cd85dcf656db8bc`,
and
`e3b7f29a19a4b3c19a14377a8ea8a77d14458a48678955d406ef7eea274dd6e7`.
The corresponding suspend evidence is in
`docs/research/freertos-suspend-all-source-boundary-audit.md`. The shared
adapters and authenticated upstream kernel retain the FreeRTOS MIT license.

`runtime_freertos_interrupt_mask.S` is an exact, sectionized Clang-syntax
adaptation of `ulSetInterruptMask` and `vClearInterruptMask` from the same
MIT-licensed FreeRTOS-Kernel V10.5.1 release, specifically
`portable/IAR/ARM_CM55_NTZ/non_secure/portasm.s` at the commit pinned above.
The adapted source has SHA-256
`28f16b37970b5529fe63cf250365b955b0c65fe2a016efda1ba718ee3b768de5`.
It source-assembles the byte-exact pair both in place at
`[0x005FA0A4,0x005FA0BA)` and `[0x005FA0BA,0x005FA0C8)`, with respective
SHA-256 values
`f6bd0708e653c8e8880e33e298f9dc8ede1305c9386ea4ca5ff554d4022dc323`
and
`97532a7902b38e1551198dd647d0fcdc3a6f19315b6491058a813c7643e0028a`,
and as independently addressable isolated leaves at
`[0x007B0158,0x007B016E)` and `[0x007B016E,0x007B017C)`.

`runtime_freertos_ntz_port.S` is a 5,487-byte, sectionized Clang-syntax
adaptation of the remaining five context and exception-handler leaves from
the same FreeRTOS-Kernel V10.5.1
`portable/IAR/ARM_CM55_NTZ/non_secure/portasm.s` source. Its SHA-256 is
`38c6a259ca2fbfbefb373ef5a80216f2e5f1cad998173ca2b4c9cfde6c01aee8`.
The production build assembles `vRestoreContextOfFirstTask`,
`vRaisePrivilege`, `vStartFirstTask`, `PendSV_Handler`, and `SVC_Handler`
into their exact stock spans at `[0x005FA058,0x005FA0A4)` and
`[0x005FA0C8,0x005FA132)`, preserving the shared literal words, vectors, and
two outgoing fixed-address seams. Copyright (C) 2021 Amazon.com, Inc. or its
affiliates. The adapter and authenticated upstream kernel source retain the
FreeRTOS MIT license in `LICENSE-FreeRTOS-MIT` and the source file. The
selected V10.5.1 source is an authenticated reconstruction baseline and does
not assert Even Realities' historical checkout identity.

`runtime_littlefs_util.c`, `runtime_littlefs_util_bitops.c`,
`runtime_littlefs_util_endian.c`,
`runtime_littlefs_scmp.c`, `runtime_littlefs_alloc_ckpoint.c`,
`runtime_littlefs_alloc_drop.c`, `runtime_littlefs_disk_version.c`,
`runtime_littlefs_disk_version_parts.c`,
`runtime_littlefs_alloc_lookahead.c`,
`runtime_littlefs_mlist_isopen.c`,
`runtime_littlefs_mlist_append.c`, `runtime_littlefs_mlist_remove.c`, and
`runtime_littlefs_file_tell_private.c` port the exact `lfs_max`, `lfs_min`,
`lfs_aligndown`, `lfs_alignup`, `lfs_npw2`, `lfs_ctz`, `lfs_popc`,
`lfs_fromle32`, `lfs_tole32`,
`lfs_frombe32`, and `lfs_tobe32` utility leaves and private `lfs_scmp`,
`lfs_alloc_ckpoint`, `lfs_alloc_drop`, `lfs_fs_disk_version`,
`lfs_fs_disk_version_major`, `lfs_fs_disk_version_minor`,
`lfs_alloc_lookahead`,
`lfs_mlist_isopen`, `lfs_mlist_append`, `lfs_mlist_remove`, and
`lfs_file_tell_` leaves from
littlefs v2.10.1, commit
`0494ce7169f06a734a7bd7585f49a9fa91fa7318`. Copyright (c) 2022, The
littlefs authors. Copyright (c) 2017, Arm Limited. All rights reserved. Their
BSD-3-Clause terms are retained in `third_party/littlefs/LICENSE.md` and the
source files retain the upstream copyright and SPDX identifier. The shared
utility source has SHA-256
`2730d0f39e02d7b6e07396894b796b26d9f73332deff23a685b5a06da0f7fb22`;
the shared metadata-list predicate source has SHA-256
`7d0bc398c8ecd85fd00b34cc6dcc2b9fc75c754e1aed0bfbca01dd58ae9d6e0c`.
The shared endian-conversion source has SHA-256
`830d49b043181d270ac0aedda432c5e232ce8d6ce65e8e537b80b1a706fd6cac`.
The shared fallback-bitops source has SHA-256
`405092c6e8fc65a740f951cb2affaad8766e2553c7b8d290ff58f435e8830f47`.
The shared disk-version-parts source has SHA-256
`920d03e80c9d16a1d0b4299f8151eefe4d9f3ac1ba89c2d40bcc5830335eb5a7`.
The shared allocator-lookahead source has SHA-256
`44ab9037747a4cb209404423d52cf817b035cbab5177a8c0cb05090df4b68491`.
These shared sources are compiled independently for the Apollo-main and
bootloader profiles.

`runtime_easylogger_control.c` is a bounded Apollo-main adaptation of
EasyLogger's `elog_set_output_enabled`, `elog_set_text_color_enabled`,
`elog_set_fmt`, `elog_set_filter_lvl`, `elog_set_filter_tag`,
`elog_output_lock`, `elog_output_unlock`, and `elog_output_lock_enabled`
behavior from the authenticated `2.2.99`-labeled source-equivalent snapshot at
commit `a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24`. Copyright (c) 2015-2019
Armink. The upstream MIT terms are retained in
`LICENSE-EasyLogger-MIT`, `third_party/easylogger/LICENSE`, and the source
file. The adaptation preserves the recovered G2 logger-object layout and
retains the downstream asynchronous transport, assertion hook, and port
lock/unlock behavior as explicit stock seams. The later shared helper tranche
source-owns the bounded string-copy algorithm.

`runtime_easylogger_filter.c` is a bounded adaptation of EasyLogger's private
five-slot tag-level default initializer and public `elog_get_filter_tag_lvl`
from the same authenticated snapshot and copyright. It preserves the
recovered G2 logger-object ABI, owns the bounded tag clear/comparison helpers,
and links directly to the source EasyLogger lock/unlock functions. The MIT
terms are retained in `LICENSE-EasyLogger-MIT`,
`third_party/easylogger/LICENSE`, and the source file.

`components/shared/easylogger/runtime_easylogger_helpers.c` and
`runtime_easylogger_helpers.h` are source-equivalent bounded adaptations of
EasyLogger's `get_fmt_enabled`, argument-aware unsigned and pointer format
predicates, and `elog_strcpy` from the same authenticated commit. They are
4,975 and 6,505 bytes with SHA-256 values
`8f2850f789fba3b08bdc3e1fa8f3a4646aaef7e4b16862f3be53478071aa22b5`
and
`f3a7e9bce0f136a2ff4a76929c317aef7bbc7c29dfc60d58311d94e58f6e2393`.
Copyright (c) 2015-2019 Armink. The upstream MIT terms remain in
`LICENSE-EasyLogger-MIT`, `third_party/easylogger/LICENSE`, and both shared
source files.

`components/shared/easylogger/runtime_easylogger_output_candidate.c` is the
production bounded adaptation of EasyLogger's `elog_output` from that same
authenticated commit. The historical filename is retained for stable audit
links. Copyright (c) 2015-2019 Armink; the upstream MIT terms remain in
`LICENSE-EasyLogger-MIT`, `third_party/easylogger/LICENSE`, and the source.

`runtime_easylogger_hexdump.c` is the production bounded Apollo-main
adaptation of EasyLogger's `elog_hexdump` from the same authenticated commit.
Copyright (c) 2015-2018 Armink. The upstream MIT terms are retained in
`LICENSE-EasyLogger-MIT`, `third_party/easylogger/LICENSE`, and the production
source file.

The G2 asynchronous submit and corrected single-owner record-builder files
are separately authored openCFW glue distributed under this component's
GPL-3.0-only terms. The stock-compatible builder is retained only as a host
and audit oracle. Their ABI and behavior are derived from observed G2
compatibility requirements, not attributed to upstream EasyLogger.

`components/shared/easylogger/runtime_easylogger_helper_seams.c` is a
7,068-byte MIT-licensed openCFW image-binding adapter with SHA-256
`78dc5aa9a7eb4f072b3169ae1837855007f25e1adccec7deaefecc486c8f0823`.
It binds the shared algorithms to the recovered Apollo-main or bootloader
logger object and assertion policy. Official assertion strings, hook globals,
diagnostic-output entries, and wait wrappers remain proprietary compatibility
seams and are not relicensed by this notice.

`third_party/tlsf/tlsf.c` and `third_party/tlsf/tlsf.h` are a byte-identical,
source-integrated snapshot of Matthew Conte TLSF v3.1 at source-equivalent
candidate commit `deff9ab509341f264addbd3c8ada533678591905`. The nine stock
TLSF entries reached by external firmware callers are redirected to functions
compiled from this BSD-3-Clause source. Copyright (c) 2006-2016 Matthew Conte.
The BSD-3-Clause copyright notice, redistribution conditions, endorsement
restriction, and disclaimer are retained verbatim in
`third_party/tlsf/tlsf.h` and apply to the integrated vendor source in source
and binary distributions. The selected candidate and bounded
firmware-equivalence range are documented in
`third_party/tlsf/README.openCFW.md`.

`runtime_tlsf.c` and the headers under
`components/apollo_main/core_overlay/tlsf_compat/` are openCFW's
GPL-3.0-only freestanding Apollo510 ABI, namespacing, assertion, diagnostic,
byte-copy, and hosted-header compatibility port around that unmodified
BSD-3-Clause source. Combining the files in the firmware does not remove or
replace the upstream BSD-3-Clause notice and conditions.

`runtime_async_call.c` is a bounded adaptation of the LVGL 9.3 asynchronous
call lifecycle. Copyright (c) 2025 LVGL Kft. Its MIT terms are retained in
`LICENSE-LVGL-MIT`.

`evenhub_lz4.c` retains the earlier bounded, decompression-only LZ4-family
implementation as an inactive compatibility section. The active production
decoder is pristine `LZ4_decompress_safe` from the authenticated LZ4 v1.10.0
snapshot at commit `ebb370ca83af193212df4dcbadcc5d87bc0de2f0`, with the
G2 ABI and EvenHub mode-2 adapters in `evenhub_lz4_upstream_adapter.c`:
[`lz4/lz4`](https://github.com/lz4/lz4/tree/v1.10.0).
Selecting v1.10.0 as maintained replacement source does not claim that exact
point release for the stripped stock decoder. Copyright (C) 2011-2020, Yann
Collet. Its BSD-2-Clause terms are retained in
`LICENSE-LZ4-BSD-2-Clause` and `third_party/lz4/LICENSE`.

`gpio_state.c`, `gpio_pinconfig.c`, `gpio_interrupt.c`, `cachectrl.c`,
`duration_delay.c`, `secure_ota.c`, `rtc_initialize.c`, `rtc_time_set.c`,
`rtc_time_get.c`, `pwrctrl_peripheral_descriptor.c`,
`pwrctrl_trim_version.c`, `pwrctrl_mcu_switch_sequence.c`, and
`pwrctrl_mcu_mode_select.c`, plus `pwrctrl_gpu_mode_status.c` and
`pwrctrl_gpu_mode_select.c`, plus `pwrctrl_mcu_memory_config.c` and
`pwrctrl_rom_enable.c`, `pwrctrl_rom_disable.c`, and
`pwrctrl_sram_config.c`, `pwrctrl_crypto_quiesce.c`, and
`pwrctrl_periph_enable.c`, plus
`pwrctrl_periph_disable_mask_check.c`, `pwrctrl_periph_disable.c`, and
`pwrctrl_periph_enabled.c`, plus `pwrctrl_info1_populate.c` and
`pwrctrl_low_power_init.c`, plus
`pwrctrl_buck_ldo_override_init.c` and
`pwrctrl_buck_ldo_update_override.c`, are bounded adaptations of AmbiqSuite SDK
`am_hal_gpio_state_read`, `am_hal_gpio_state_write`,
`am_hal_gpio_pinconfig_get`, `am_hal_gpio_pinconfig`, and
`am_hal_gpio_interrupt_control`, `am_hal_gpio_interrupt_status_get`, and
`am_hal_gpio_interrupt_clear`, plus the IRQ-specific status and clear helpers,
pinned to Ambiq's public SDK 5.1.0 import commit. The same module adapts
`am_hal_gpio_interrupt_register` and `am_hal_gpio_interrupt_service`, bound to
the reviewed stock RAM tables. `gpio_interrupt.c` also contains the SDK's
private `gpionum_intreg_index_get` helper. `cachectrl.c` adapts instruction-
cache enable/disable and data-cache enable/invalidate/clean.
`duration_delay.c` adapts
`am_hal_delay_us`, its adjacent millisecond/microsecond application wrappers,
and the exact `br_util_delay_cycles` ITCM loop plus its reviewed scatter-load
literal. `secure_ota.c` adapts `am_hal_ota_add` with the reviewed Apollo510
state, MRAM-programmer, and OTA-pointer bindings. `rtc_initialize.c` adapts
the XTAL clock selection and RTC oscillator enable operations from
`am_hal_clkgen_control`, `am_hal_rtc_osc_select`, and
`am_hal_rtc_osc_enable`. `rtc_time_set.c` adapts
`am_util_time_computeDayofWeek`, `am_hal_rtc_time_set`, their validation and
BCD helpers, and the reviewed application diagnostic wrapper.
`rtc_time_get.c` adapts `am_hal_rtc_time_get`, its BCD helper and RTC
clock-edge polling workaround, and the reviewed void application wrapper.
`pwrctrl_peripheral_descriptor.c` adapts the private `am_get_pwrctrl` helper
and its complete 34-entry `am_hal_pwrctrl_peripheral_control` table.
`pwrctrl_trim_version.c` adapts the private `TrimVersionGet` helper's shipped
cache and INFO1-read behavior. `pwrctrl_mcu_switch_sequence.c` adapts the
private `mcu_hp_lp_switch_sequence` helper, including SPOT coordination,
HFRC2 readiness handling, bounded performance-frequency acknowledgement,
mode-cache updates, and critical-section restoration.
`pwrctrl_mcu_mode_select.c` adapts the public
`am_hal_pwrctrl_mcu_mode_select` validation, SIMOBUCK gate, transition
dispatch, and performance-status verification.
`pwrctrl_gpu_mode_status.c` adapts the public
`am_hal_pwrctrl_gpu_mode_status` null validation and cached-byte copy.
`pwrctrl_gpu_mode_select.c` adapts the public
`am_hal_pwrctrl_gpu_mode_select` validation, SIMOBUCK and GFX-use gates,
voltage/performance sequencing, cached-mode maintenance, SPOT TON
coordination, settle delays, and critical-section restoration.
`pwrctrl_mcu_memory_config.c` adapts the public
`am_hal_pwrctrl_mcu_memory_config` ROM/TCM/NVM power transitions, bounded
status waits, SPOT coordination, AXI-clock forcing, hardware verification,
and retention policy. `pwrctrl_rom_enable.c` adapts the public
`am_hal_pwrctrl_rom_enable` AUTO-mode SPOT notification, ROM power enable,
bounded readiness poll, and timeout behavior. `pwrctrl_rom_disable.c` adapts
the public `am_hal_pwrctrl_rom_disable` AUTO-mode ROM power disable, bounded
status polling, post-clear SPOT notification, and timeout behavior.
`pwrctrl_sram_config.c` adapts the public `am_hal_pwrctrl_sram_config`
shared-bank power transition, active-client and retention fields, SPOT
coordination, status verification, and MMIO override clearing.
`pwrctrl_crypto_quiesce.c` adapts the private `crypto_quiesce` helper's MRAM
crypto-ready check, crypto-idle fallback, power-down-bit update, and final
ready check. `pwrctrl_periph_enable.c` adapts the public
`am_hal_pwrctrl_periph_enable` descriptor lookup, already-enabled and OTP
gates, GPU/device/audio SPOT policy, critical enable write, readiness checks,
and crypto/OTP post-power behavior.
`pwrctrl_periph_disable_mask_check.c` adapts the private shared-domain
last-enabled-member predicate used by peripheral disable.
`pwrctrl_periph_disable.c` adapts the public peripheral-disable sequence,
including OTP/crypto and debug gates, the critical power clear, shared-domain
status policy, GPU/clock handling, device/audio SPOT updates, and TempCo
coordination.
`pwrctrl_periph_enabled.c` adapts the public peripheral enabled-state query,
including null validation, descriptor error handling, low-byte enum ABI, and
the status-register predicate. `pwrctrl_info1_populate.c` adapts the private
INFO1 cache-population routine, including hardware-validity gates, all nine
ordered INFO1 reads, partial commits, and final validity publication.
`pwrctrl_low_power_init.c` adapts the public low-power initializer, including
reset/debug errata, CPDLP/WIC and OTP policy, INFO1 fallback, memory/clock and
factory-trim setup, retention, SPOT/SIMOBUCK coordination, critical-section
restoration, and revision-gated MRAM policy.
`pwrctrl_buck_ldo_override_init.c` adapts the private buck/LDO override
initializer's ten ordered volatile `MCUCTRL->VRCTRL` updates for SIMOBUCK,
CoreLDO, and MemLDO while preserving unrelated register bits.
`pwrctrl_buck_ldo_update_override.c` adapts the private dynamic override
updater's low-bit enable semantics and three ordered volatile register
updates. `pwrctrl_control.c` adapts the public miscellaneous power-control
dispatcher's SIMOBUCK initialization, conditional crypto power-down,
deep-sleep crystal shutdown, and ordered all-peripheral disable policy.
`pwrctrl_cpdlp_config.c` adapts the public CPDLPSTATE configurator's packed
short-enum ABI, cache-safety gate, field packing, and status behavior.
`pwrctrl_cpdlp_get.c` adapts the public CPDLPSTATE getter's single register
read and three-byte short-enum output layout.
`pwrctrl_temp_update.c` adapts the public temperature-update routine's
hard-float entry ABI, retained SPOT-manager call, threshold copy, and
normalized failure output.
`pwrctrl_syspll_enable.c` adapts the public system-PLL enable routine's
revision-gated isolation release, ordered rail-power updates, critical
section, and stabilization delays.
`pwrctrl_syspll_disable.c` adapts the public system-PLL disable routine's
ordered rail-power-down updates, revision-gated isolation assertion, and
critical section.
`pwrctrl_syspll_enabled.c` adapts the public system-PLL enabled-state query's
single register read, boolean result, and success status.
`spotmgr_timer_init.c` adapts the public SPOT-manager timer initializer's
ordered disable/configuration writes, compare resets, interrupt clear, and
interrupt-enable update.
`spotmgr_timer_start.c` adapts the public SPOT-manager timer-start routine's
clock request, compare scaling, global enable, mandatory clear-bit toggle,
NVIC enable, and final timer enable.
`spotmgr_timer_restart.c` adapts the public SPOT-manager timer-restart
routine's ordered disable and clear pulse, compare scaling, interrupt
acknowledgement, pending-IRQ clear, and final timer enable.
`spotmgr_timer_stop.c` adapts the public SPOT-manager timer-stop routine's
ordered timer/global disable, clock release, IRQ disable and acknowledgement,
APB write flush, and pending-IRQ clear.
`spotmgr_init.c` adapts the public SPOT-manager initializer's ordered
15-slot state clear, Apollo510 revision/trim matrix, six cached revision flags,
patch-tracker gate, ACRG/VRCTRL analog repair, callback-table selection, and
fresh call-time initializer dispatch.
`delay_status.c` adapts the public `am_hal_delay_us_status_change` and
`am_hal_delay_us_status_check` helpers, including masked volatile polling,
equal/not-equal selection, exact timeout budgets, one-microsecond delays, and
success/timeout status results.
`read_words.c` adapts the public `am_hal_read_words` wrapper and its private
ITCM implementation as one source-owned forward volatile word-copy routine,
preserving the reviewed nonzero-count precondition.
`mcuctrl_device_info.c` adapts Apollo510's private `device_info_get` helper,
preserving the reviewed register reads, fresh SKU indexing, RAM/MRAM lookup
tables, JEDEC PID/CID assembly, and stock ten-microsecond delay cadence.
`mcuctrl_control.c` adapts the public `am_hal_mcuctrl_control` dispatcher,
preserving its low-byte command ABI, exact oscillator register transactions,
argument validation and reread behavior, clock request/release ordering, and
returned backend failures.
`mcuctrl_extclk32m_status.c` adapts the public external-32-MHz-clock status
getter, preserving external-clock precedence, the fresh second powered-state
read, one-byte short-enum store, and constant success result.
`mcuctrl_trim_version.c` adapts Apollo510's private `trim_version_get`
helper, preserving its INFO1 word `0x244` read, chip-revision qualification,
PCM/non-PCM numbering, packed feature-word output, and returned reader
status.
`mcuctrl_info.c` adapts the public `am_hal_mcuctrl_info_get` dispatcher,
preserving its low-byte selector ABI, status-six argument handling, nine
fresh SKU reads, feature-field mappings, and direct calls to the source-owned
trim-version and device-information helpers.
`spotmgr_dispatch.c` adapts the public SPOT-manager power-state, TempCo,
SIMOBUCK initialization, timer-interrupt, TON configuration, post-LP-to-HP,
and SIMOBUCK low-power-autoswitch callback dispatchers. It preserves their
reviewed `0x20073270` state-table slots, null-success/no-op behavior, fresh
second volatile callback reads, byte-truncated arguments, and power-state
third-argument forwarding.
All forty-eight source modules are
pinned to `e8baebd44008dfec7197d40d53c8a62f3a36b38b`. Ambiq's BSD-3-Clause
copyright and complete license terms are retained in
`LICENSE-Ambiq-BSD-3-Clause`.

The production overlay also compiles the complete, unmodified
`third_party/ambiqsuite-apollo510/mcu/apollo510/hal/mcu/am_hal_mspi.c`
translation unit from AmbiqSuite 5.1.0 commit
`5efc0228528a8adce5eae0d226fac85d2551eb3b`. Section garbage collection
retains only the exact-upstream `am_hal_mspi_interrupt_clear` leaf and
discards unrelated code and private `g_MSPIState`. Ambiq's BSD-3-Clause terms
are retained in `third_party/ambiqsuite-apollo510/LICENSE`. The reached Arm
CMSIS Core headers are pinned at commit
`d23a6949a0331ca96853bcd98b0fdcc4db47184c`; their Apache-2.0 terms are
retained in `third_party/cmsis-core/LICENSE.txt`.

`runtime_cmsis_message_queue_new.c` is a bounded freestanding port of the
exact `osMessageQueueNew` allocation and validation algorithm from
authenticated CMSIS-FreeRTOS v10.5.1 `cmsis_os2.c`, commit
`d213f261b5be6bb29a7cce8b84071706b72f4d53`. The 8,427-byte source has
SHA-256
`8897019aa7a2beca32a88dc60808fb1f99b1538933b8ab4fbd9ed4fed38d433c`.
Copyright (c) 2013-2022 Arm Limited. All rights reserved. Its Apache-2.0
terms are retained in the source and
`third_party/cmsis-freertos/CMSIS_5/LICENSE.txt`.
The separately reached FreeRTOS V10.5.1 functions retain MIT terms in
`third_party/freertos-kernel/LICENSE.md`.

`runtime_cmsis_mutex_new.c` is a bounded freestanding port of the exact
`osMutexNew` allocation and validation algorithm from the same authenticated
CMSIS-FreeRTOS v10.5.1 `cmsis_os2.c` and commit. The 9,798-byte source has
SHA-256
`28081734a384c089635681014ed028414b75d375c22f0a52a64f53e22842cf2d`.
Copyright (c) 2013-2022 Arm Limited. All rights reserved. Its Apache-2.0
terms are retained in the source and
`third_party/cmsis-freertos/CMSIS_5/LICENSE.txt`. The separately reached
FreeRTOS V10.5.1 scheduler-state and mutex-creator functions retain MIT terms
in `third_party/freertos-kernel/LICENSE.md`.

`runtime_freertos_heap4.c` is a bounded freestanding port of the exact
FreeRTOS-Kernel V10.5.1 `heap_4` initialization, allocation, free, and
free-list insertion/coalescing algorithms from commit
`def7d2df2b0506d3d249334974f51e427c17a41c`. The 16,885-byte source has
SHA-256
`d848b90a00da24db963c49dbff2472314b2a76c6cf269efef46e6cac56889986`.
`runtime_freertos_queue_delete.c` ports the exact V10.5.1 `vQueueDelete`
algorithm from the same commit. The 5,851-byte source has SHA-256
`fa8033f61e418dbfb304dd7443dea340bfff88958df493e276ea92db4491da2b`.
Both retain upstream MIT terms in `third_party/freertos-kernel/LICENSE.md`.

`runtime_freertos_queue_next_closure.c` is a bounded freestanding adaptation
of the exact FreeRTOS-Kernel V10.5.1 `xQueueGiveFromISR` and
`xTaskRemoveFromEventList` algorithms from commit
`def7d2df2b0506d3d249334974f51e427c17a41c`. The 7,277-byte source has
SHA-256
`b13a24bf4538016109194500c9ff7d9bfe5feac0b9f2c9708b390b028aad6f61`.
`runtime_freertos_task_check_free_stack_space.c` adapts the exact V10.5.1
`prvTaskCheckFreeStackSpace` algorithm from the same commit. Its 2,269-byte
source has SHA-256
`ba8cd2018984f4e6a131698d86a0eb4abd0d07dd1e81e75979211f00bf3904de`.
Both retain upstream MIT terms in `third_party/freertos-kernel/LICENSE.md`;
the separate adapters record the recovered G2 configuration and ABI seams
without claiming those device-specific values came from upstream.

`runtime_freertos_task_check_for_timeout.c` is a bounded freestanding
adaptation of the exact FreeRTOS-Kernel V10.5.1 `xTaskCheckForTimeOut`
algorithm from the same authenticated commit. The 3,506-byte source has
SHA-256
`d0d84996ae7ab897cf53655962e86574577b98bf367df52c9ae8ac076a8dc89e`.
It retains upstream MIT terms in `third_party/freertos-kernel/LICENSE.md`.
Its separate header and implementation record recovered G2 timeout-state,
tick-width, feature-gate, critical-section, and fixed-address bindings; those
device-specific parameters are not represented as upstream provenance.

The authenticated FreeRTOS-Kernel V10.5.1 snapshot retains the exact
20,608-byte `portable/MemMang/heap_4.c`, SHA-256
`d48a51e34caed771e6650d95f6c2527e52fde2a6ebc6f83b49d003aef0135e05`,
under its upstream MIT terms. The pristine file is the authenticated
algorithm reference; production selection, recovered G2 layout, fixed
scheduler/hook seams, and freestanding leaf boundaries live in the separate
adapter above.

`components/shared/freertos/g2-tcb-v10.5.1.patch` records the minimal
vendor-derived compatibility delta to the authenticated V10.5.1 `tasks.c` and
`include/FreeRTOS.h`: one stored creation-depth word after the task name, its
`StaticTask_t` mirror, and its initializer assignment. The upstream base
retains FreeRTOS MIT terms. The semantic patch is reconstructed from the
official G2 binary; no proprietary source text, original identifier, or
private commit is claimed.

`runtime_cmsis_semaphore_new.c` is a bounded freestanding port of the exact
`osSemaphoreNew` algorithm from authenticated CMSIS-FreeRTOS v10.5.1
`cmsis_os2.c`, commit
`d213f261b5be6bb29a7cce8b84071706b72f4d53`. The 11,566-byte source has
SHA-256
`a947868d3fbcfc7f41d021210355e0ff777d49d3db84fa0da71a255d319c1527`.
Copyright (c) 2013-2022 Arm Limited. All rights reserved. Its Apache-2.0
terms are retained in the source and CMSIS-FreeRTOS snapshot. Its reached
FreeRTOS scheduler, queue creation/send/delete, semaphore wrapper, heap, and
interrupt-mask dependencies retain MIT terms.

`runtime_cmsis_core_leaves.c` is a bounded freestanding port of private
`IRQ_Context`, `osKernelGetTickCount`, `osThreadGetId`, and
`osMessageQueueGetCapacity` from the same authenticated CMSIS-FreeRTOS
v10.5.1 `cmsis_os2.c` and commit. The 5,750-byte source has SHA-256
`483723544fed146ef9d843c215736a748a5fcab13196ee2bd8938c5419f6570b`.
Copyright (c) 2013-2022 Arm Limited. All rights reserved. Its Apache-2.0
terms are retained in the source and CMSIS-FreeRTOS snapshot. The reached
FreeRTOS scheduler-state, tick, current-task, and queue-layout dependencies
retain MIT terms; the recovered G2 bindings are recorded separately and are
not attributed to upstream.

`runtime_cmsis_count_leaves.c` is a bounded freestanding port of
`osSemaphoreGetCount` and `osMessageQueueGetCount` from the same authenticated
CMSIS-FreeRTOS v10.5.1 source and commit. The 3,306-byte source has SHA-256
`cb17116f9e29706cb5e43dc718299d97a41db798b2a02905800266e9f9d285bf`.
Copyright (c) 2013-2022 Arm Limited. All rights reserved. Its Apache-2.0
terms are retained. Both leaves select only the separately source-owned
normal/ISR FreeRTOS queue-count providers through the source-owned IRQ helper;
those FreeRTOS providers retain MIT terms.

`runtime_cmsis_message_queue_delete.c` is a bounded freestanding port of
`osMessageQueueDelete` from the same authenticated CMSIS-FreeRTOS v10.5.1
source and commit. The 2,254-byte source has SHA-256
`2a58f7ecbbc10e3a36430c5afbbd78483475afa68baf0023cd6d587c10846994`.
Its Apache-2.0 terms are retained. The reached IRQ helper is Apache-2.0 and
the separately source-owned FreeRTOS `vQueueDelete` provider retains MIT
terms.

`runtime_cmsis_thread_yield.c` is a production-integrated bounded port of
`osThreadYield` from the same source. Its 1,748 bytes have SHA-256
`c03ff1c35cd5ace0c26d927594960674b6e8a3c0fd1a8fb79f02d3d49c2552a5`.
It retains Apache-2.0 terms and calls only the Apache-2.0 IRQ helper and MIT
FreeRTOS `vPortYield` provider.

`runtime_cmsis_kernel_get_state.c` is a production-integrated bounded port
for `osKernelGetState` from the same authenticated source. Its 1,741 bytes
have SHA-256
`4a8af24ddb5a0bd0449322f98a681c9903eb6406739a27153cac9b4cccf2e34f`.
It retains Apache-2.0 terms, calls the source-owned MIT FreeRTOS scheduler-state
provider, and reads the separately authenticated G2 CMSIS wrapper-state word.

`runtime_cmsis_mutex_delete.c` is a production-integrated bounded port of
`osMutexDelete` from the same authenticated source. Its 1,462 bytes have
SHA-256
`91d73236a38148437740f7cdb5816acbbe8965991f29a1282271d63193394895`.
It retains Apache-2.0 terms and calls only the Apache-2.0 IRQ helper and MIT
FreeRTOS `vQueueDelete` provider.

`runtime_cmsis_timer_is_running.c` is a production-integrated bounded port
for `osTimerIsRunning` from the same authenticated source. Its 813 bytes have
SHA-256
`9e9b8ca7a42f214b381935cf2c32729f7292e3857d166d34f1f6194e40b8845b`.
It retains Apache-2.0 terms and calls only the Apache-2.0 IRQ helper and the
separately source-owned FreeRTOS timer-active provider.

The separate `third_party/cmsis-freertos` snapshot preserves
unmodified CMSIS-FreeRTOS v10.5.1 wrapper inputs and the package-declared
CMSIS_5 5.9.0 header dependency. Their official unsigned tag objects, peeled
commits, trees, Git blobs, byte counts, and SHA-256 values are recorded in
`third_party/cmsis-freertos/PROVENANCE.json`. CMSIS-FreeRTOS wrapper source
and CMSIS headers retain Apache-2.0 notices and the full CMSIS_5 license in
`third_party/cmsis-freertos/CMSIS_5/LICENSE.txt`; the retained
CMSIS-FreeRTOS `License/license.txt` records MIT terms for the separately
supplied FreeRTOS kernel. This snapshot does not establish the historical G2
checkout.

Candidate-only local shims under
`components/apollo_main/core_overlay/candidates/cmsis_freertos_constructors/`
(`FreeRTOSConfig.h`, `portmacro.h`, `cmsis_freertos_target.h`, and `string.h`)
permit the authenticated, unmodified `cmsis_os2.c` to compile for Cortex-M55
with `-Oz -Werror`. The broad proof retains 370 text bytes (`IRQ_Context` 46,
`osMessageQueueNew` 88, `osMutexNew` 98, `osSemaphoreNew` 138), no read-only
or writable data, and four 8-byte EHABI `.ARM.exidx` sections; 6/6 isolated
tests pass in 0.231 seconds. These broad shims and results remain
candidate-only for unrelated services:
there is no authenticated G2 RTE/device header, `SystemCoreClock` and MVE are
unresolved, `INCLUDE_*` switches are compile-only, assert/NVIC/libc seams are
outside the retained root, candidate `StaticTask_t` is 108 bytes versus the
112-byte stock G2 TCB, and no stock byte identity is claimed for those
remaining candidates. The bounded production `osMessageQueueNew`,
`osMutexNew`, and `osSemaphoreNew` leaves are covered by the separate notices
above; the semaphore cleanup path is closed over production `vQueueDelete`
and `heap_4` adapters rather than this broad compile proof.

The ring-gesture module is derived from
[`jimrandomh/g2flash`](https://github.com/jimrandomh/g2flash), pinned at commit
`6d5c58598e047ca5980065a9ee7570ce2d172ca7`. Its detailed provenance and the
complete GPLv3 text are retained in the sibling `ring_gesture` component.

Vendor compatibility blobs remain proprietary and are not relicensed by this
notice.

`components/shared/freertos/runtime_freertos_queue_messages_waiting.c`,
`components/shared/freertos/runtime_freertos_queue_messages_waiting_from_isr.c`,
and `runtime_freertos_queue_messages_waiting.h` are bounded freestanding
adaptations of the exact FreeRTOS-Kernel V10.5.1
`uxQueueMessagesWaiting` and `uxQueueMessagesWaitingFromISR` algorithms from
authenticated commit `def7d2df2b0506d3d249334974f51e427c17a41c`. They
retain the upstream MIT terms in `third_party/freertos-kernel/LICENSE.md` and
in the source files. The recovered G2 `Queue_t` layout, fixed assertion and
critical-section providers, caller topology, and production patch addresses
are openCFW compatibility evidence and are not represented as upstream
provenance.

`components/shared/freertos/runtime_freertos_queue_generic_reset.c` and
`components/shared/freertos/runtime_freertos_task_remove_from_unordered_event_list.c`
are bounded freestanding adaptations of the exact FreeRTOS-Kernel V10.5.1
`xQueueGenericReset` and `vTaskRemoveFromUnorderedEventList` algorithms from
authenticated commit `def7d2df2b0506d3d249334974f51e427c17a41c`. They
retain the upstream MIT terms in
`third_party/freertos-kernel/LICENSE.md`. Their separate headers and adapters
record recovered G2 ABI, configuration, fixed-address state, assertion, and
provider bindings; those device-specific parameters are not represented as
upstream provenance.

`components/shared/freertos/runtime_freertos_task_lists_initialize.c` and
`runtime_freertos_task_lists_initialize.h` are a bounded freestanding
adaptation of the exact FreeRTOS-Kernel V10.5.1 `prvInitialiseTaskLists`
algorithm from authenticated commit
`def7d2df2b0506d3d249334974f51e427c17a41c`. They retain the upstream MIT
terms in `third_party/freertos-kernel/LICENSE.md` and in the production files.
The recovered G2 priority count, list layout, Apollo-main RAM addresses,
selector words, caller topology, placement, and entry replacement are openCFW
compatibility evidence rather than upstream provenance. The six production
calls bind directly to the separately source-owned
`open_cfw_freertos_list_initialise`; the distinct bootloader homolog remains
outside this reuse and is not patched.

`components/shared/nanopb/runtime_nanopb_decode_varint.c` is an altered,
bounded production adaptation of nanopb `pb_decode_varint`, selected against
the authenticated official nanopb 0.4.9 compatibility baseline at commit
`98bf4db69897b53434f3d0ba72e0a3ab1a902824`. nanopb is distributed under
the Zlib license. The complete unchanged upstream license is retained at
`third_party/nanopb/LICENSE.txt`, and the altered production source and header
retain the complete notice. The selected baseline is compatible with the
recovered pristine 0.4.7–0.4.9 runtime evidence; it is not proof that Even
Realities used nanopb 0.4.9. The recovered G2 stream layout, stock
`pb_readbyte` address, placement, and entry replacement are openCFW
compatibility evidence rather than upstream provenance. The broader pristine
`pb_common.c`, `pb_decode.c`, and `pb_encode.c` translation units remain
unregistered production inputs.

`components/shared/nanopb/runtime_nanopb_skip_varint.c` and
`runtime_nanopb_skip_varint.h` are an altered, bounded production adaptation
of nanopb `pb_skip_varint`, selected against the same authenticated official
nanopb 0.4.9 compatibility baseline at commit
`98bf4db69897b53434f3d0ba72e0a3ab1a902824`. They retain the complete Zlib
notice and plainly identify the source as altered. The selected 0.4.9 release
is compatible with authenticated pristine 0.4.7–0.4.9 evidence; it does not
prove the vendor's historical point release. The recovered G2 stream ABI,
stock `pb_read` address `0x0048F3BE`, caller topology, placement, and entry
replacement are openCFW compatibility evidence rather than upstream
provenance. The broader pristine nanopb translation units remain unregistered.

`components/shared/nanopb/runtime_nanopb_close_string_substream.c` and
`runtime_nanopb_close_string_substream.h` are the third altered, bounded
production adaptation selected from the same authenticated nanopb
compatibility evidence. They adapt `pb_close_string_substream`, retain the
complete Zlib notice, and plainly identify the files as altered. The selected
nanopb 0.4.9 commit
`98bf4db69897b53434f3d0ba72e0a3ab1a902824` has the same relevant pristine
semantics as authenticated 0.4.7 and 0.4.8; it is a compatibility baseline,
not proof of Even Realities' historical version. The recovered 16-byte G2
stream ABI, stock span and callers, `pb_read` seam at `0x0048F3BE`, placement,
and full-span entry replacement are openCFW compatibility evidence rather than
upstream provenance. No broader nanopb translation unit is admitted by this
leaf, and no claim is made that the remaining firmware is source-authenticated.

`runtime_littlefs_file_size_private.c` and
`runtime_littlefs_file_size_private.h` are a bounded freestanding adaptation
of `lfs_file_size_` from the authenticated littlefs v2.10.1 source-equivalent
release at commit `0494ce7169f06a734a7bd7585f49a9fa91fa7318`. littlefs is
distributed under BSD-3-Clause; the complete unchanged upstream terms are
retained at `third_party/littlefs/LICENSE.md`, and the adaptation retains the
upstream copyright and SPDX identifier. The recovered G2 `lfs_file_t` layout,
official address and caller topology, placement, and entry replacement are
openCFW compatibility evidence rather than upstream provenance. Its sole
runtime dependency closes over the separately source-owned littlefs
`open_cfw_littlefs_util_max`. This reuse includes no G2 block-device port and
does not authorize hardware format or erase.

`components/shared/cmbacktrace/runtime_cmbacktrace_get_cur_thread_name.c` is
a bounded production adaptation of CmBacktrace `get_cur_thread_name`, selected
against authenticated compatibility-baseline commit
`73714489f9d8af130aacb515586b397b604a5768`. CmBacktrace is distributed under
the MIT license; the unchanged upstream text is retained in
`third_party/cmbacktrace/LICENSE` and copied for this component in
`LICENSE-CmBacktrace-MIT`. The selected commit is an openCFW compatibility
choice, not a claim that Even Realities used that exact checkout.

The companion
`runtime_cmbacktrace_pc_task_get_name_current.c` is openCFW recovered source,
not upstream CmBacktrace code. It preserves the authenticated G2 adapter
semantics: load the current TCB from `0x20074A20`, add task-name offset `0x34`,
and retain the observed null-to-0x34 result. The broader snapshot and the
independently named research candidate remain excluded from production.

`components/shared/freertos_cli/runtime_freertos_cli_console_*.c` and
`runtime_freertos_cli_console.h` are GPL-3.0-only clean-room openCFW source for
the recovered G2 console-task glue. They are not attributed to upstream
FreeRTOS-Plus-CLI. Production retains the existing FreeRTOS+CLI interpreter
ABI, 22 proprietary registration groups, 76 proprietary command descriptors,
display and receive seams, and fixed SRAM bindings. The retained interpreter
is compatible with the classic MIT FreeRTOS-Plus-CLI lineage; the selected
`43defa56` snapshot is an openCFW compatibility baseline and does not establish
Even Realities' exact historical checkout. The pristine snapshot and the
independently named console candidate remain excluded from production.

The source console reserves the last byte of the 128-byte input buffer for
NUL and consumes a receive only when its return count is exactly one. These
reviewed safety choices differ from stock G2 behavior. The earlier two-byte
collector-capacity source fragment is no longer a production input because
the complete source task owns that bound directly. Compact placement changes
to the already promoted nanopb and CmBacktrace leaves do not change their
Zlib/MIT notices or expand their attribution boundaries.

`runtime_littlefs_file_rewind_private.c` and its header are a bounded
freestanding adaptation of private `lfs_file_rewind_` from authenticated
littlefs v2.10.1 commit `0494ce7169f06a734a7bd7585f49a9fa91fa7318`.
littlefs is distributed under BSD-3-Clause; the unchanged upstream terms are
retained at `third_party/littlefs/LICENSE.md`, and the adaptation retains its
SPDX identifier and copyright notice. The recovered G2 seek-provider address,
caller topology, ABI seam, placement, and generated entry replacement are
OpenCFW compatibility evidence rather than upstream provenance. This leaf
does not include or authorize any block-device driver, format, erase, mount,
signing, flashing, or G2 hardware operation.

`components/shared/nanopb/runtime_nanopb_decode_fixed32.c` and
`runtime_nanopb_decode_fixed32.h` are the fourth altered, bounded nanopb
production adaptation selected against authenticated nanopb 0.4.9 commit
`98bf4db69897b53434f3d0ba72e0a3ab1a902824`. nanopb is distributed under
the Zlib license; the complete unchanged upstream terms remain at
`third_party/nanopb/LICENSE.txt`, and the altered source and header retain the
required notice.

The exact `pb_decode_fixed32` definition is compatible with authenticated
pristine nanopb 0.4.7, 0.4.8, and 0.4.9. Selecting 0.4.9 is an openCFW
compatibility baseline, not proof of Even Realities' historical version or
checkout. The recovered G2 stock boundary, sole caller, little-endian target
behavior, placement, and generated full-span entry replacement are openCFW
compatibility evidence rather than upstream provenance. The production leaf
calls source-owned `pb_read` through its stable trampoline at `0x0048F3BE`;
private `buf_read` identity and two error strings remain binary-owned, and no
broader nanopb translation unit or surrounding opaque firmware is reclassified
as source-owned. All qualification was offline, with no signing, flashing, or
hardware operation.

`components/shared/littlefs/runtime_littlefs_tag_type2.c` and
`runtime_littlefs_tag_type2.h` are a bounded altered production adaptation of
private `lfs_tag_type2` from the authenticated littlefs v2.10.1
source-equivalent baseline at commit
`0494ce7169f06a734a7bd7585f49a9fa91fa7318`. littlefs is distributed under
BSD-3-Clause; the complete unchanged upstream terms remain at
`third_party/littlefs/LICENSE.md`, and both local files retain the upstream
copyright and SPDX notice.

The recovered scalar ABI, official Apollo-main range
`[0x004CAE90,0x004CAE98)`, two caller addresses, overlay placements, and
generated full-span entry replacement are openCFW compatibility evidence,
not proof of the exact historical vendor checkout. The production leaf has no
provider, relocation, global state, filesystem object, allocator, callback,
or hardware path. The surrounding littlefs implementation, the bootloader
homolog, and both G2 block-device ports remain outside this source-ownership
claim. Qualification was offline and does not authorize signing, flashing,
filesystem format or erase, or any G2 hardware operation.

`components/shared/littlefs/runtime_littlefs_tag_chunk.c` and
`runtime_littlefs_tag_chunk.h` are a bounded altered BSD-3-Clause adaptation
of private `lfs_tag_chunk` from authenticated littlefs v2.10.1 commit
`0494ce7169f06a734a7bd7585f49a9fa91fa7318`. Their upstream copyright and
SPDX notices are retained, and the complete unchanged terms remain at
`third_party/littlefs/LICENSE.md`.

The stock ranges, caller sets, scalar ABI, placements, and generated full-span
entry redirects in Apollo main and the bootloader are openCFW compatibility
evidence. The selected commit is a source-equivalent baseline, not proof of
Even Realities' historical checkout. This leaf brings no broad littlefs
translation unit, block-device port, format/erase path, signing, flashing, or
hardware authorization into production.

`components/shared/littlefs/runtime_littlefs_tag_isvalid.c`,
`runtime_littlefs_tag_isvalid.h`, `runtime_littlefs_tag_type1.c`, and
`runtime_littlefs_tag_type1.h` are bounded altered BSD-3-Clause adaptations of
the private `lfs_tag_isvalid` and `lfs_tag_type1` definitions from the same
authenticated littlefs v2.10.1 source-equivalent baseline. They retain the
upstream copyright and SPDX notices; the complete unchanged license remains
at `third_party/littlefs/LICENSE.md`.

The recovered scalar ABI, stock ranges, caller sets, overlay placements, and
generated full-span redirects in Apollo main and the bootloader are openCFW
compatibility evidence, not proof of Even Realities' exact historical
checkout. These pure scalar leaves do not import the broader littlefs library,
a G2 block-device port, or any mount/format/erase path. Their offline
production registration does not authorize signing, flashing, reset, boot,
filesystem mutation, or hardware operation.

`components/shared/littlefs/runtime_littlefs_tag_type3.c` and
`runtime_littlefs_tag_type3.h` are a bounded altered BSD-3-Clause adaptation
of private `lfs_tag_type3` from authenticated littlefs v2.10.1 commit
`0494ce7169f06a734a7bd7585f49a9fa91fa7318`. They retain the upstream
copyright and SPDX notices; the complete unchanged license remains at
`third_party/littlefs/LICENSE.md`.

The recovered scalar ABI, complete Apollo-main and bootloader stock ranges,
caller sets, placements, and full-span redirects are openCFW compatibility
evidence. The selected commit is a source-equivalent baseline, not proof of
Even Realities' exact historical checkout. This pure scalar leaf imports no
block-device, mount, format, or erase path, and its offline production
registration does not authorize signing, flashing, reset, boot, filesystem
mutation, or hardware operation.

`components/shared/littlefs/runtime_littlefs_tag_id.c` and
`runtime_littlefs_tag_id.h` are a bounded altered BSD-3-Clause adaptation of
private `lfs_tag_id` from authenticated littlefs v2.10.1 commit
`0494ce7169f06a734a7bd7585f49a9fa91fa7318`. They retain the upstream
copyright and SPDX notices; the complete unchanged license remains at
`third_party/littlefs/LICENSE.md`.

The recovered 32-bit scalar ABI, complete Apollo-main and bootloader stock
ranges, 50/41 direct-caller sets, final overlay placements, and generated
full-span redirects are openCFW compatibility evidence. The selected commit
is a source-equivalent baseline, not proof of Even Realities' exact historical
checkout. This pure mask-and-shift leaf imports no filesystem object,
block-device provider, mount, format, program, or erase path, and its offline
production registration does not authorize signing, flashing, reset, boot,
filesystem mutation, or hardware operation.

`components/shared/littlefs/runtime_littlefs_tag_size.c` and
`runtime_littlefs_tag_size.h` are the current bounded altered BSD-3-Clause
production adaptation of private `lfs_tag_size` from authenticated littlefs
v2.10.1 commit `0494ce7169f06a734a7bd7585f49a9fa91fa7318`. They retain the
upstream copyright and SPDX notices; the complete unchanged license remains
at `third_party/littlefs/LICENSE.md`.

The production boundary is limited to the exact stock spans
`[0x004CAEB8,0x004CAEBE)` and `[0x00410BC0,0x00410BC6)`, their 15/14 direct
caller sets, the recovered 32-bit scalar ABI, and the authenticated low-ten-bit
mask. Build-dependent placement and artifact pins are closed in the explicit
evidence ledgers; tag-ID remains the settled preceding production milestone.
This promotion imports no filesystem object,
block-device provider, mount, format, program, or erase path and authorizes no
signing, flashing, reset, boot, filesystem mutation, or hardware operation.

`components/shared/nanopb/runtime_nanopb_decode_fixed64.c` and
`runtime_nanopb_decode_fixed64.h` are the fifth altered, bounded nanopb
production adaptation selected against authenticated nanopb 0.4.9 commit
`98bf4db69897b53434f3d0ba72e0a3ab1a902824`. nanopb is distributed under
the Zlib license; the complete unchanged upstream terms remain at
`third_party/nanopb/LICENSE.txt`, and both altered files retain the required
notice.

The exact `pb_decode_fixed64` definition is source-identical in authenticated
pristine nanopb 0.4.7, 0.4.8, and 0.4.9. Selecting 0.4.9 is an openCFW
compatibility baseline, not proof of Even Realities' historical checkout. The
production boundary is the complete Apollo-main stock span
`[0x004901AC,0x004901CC)`, its sole caller, the recovered little-endian stream
ABI, and the `pb_read` ABI entry at `0x0048F3BE`. The succeeding bounded
`pb_read` promotion now source-owns that implementation through a full-span
entry trampoline. No bootloader homolog or broader nanopb translation unit is
included. Qualification and assembly were offline; no signing, flashing, or
hardware operation was performed.

`components/shared/nanopb/runtime_nanopb_read.c` and
`runtime_nanopb_read.h` are the sixth altered, bounded nanopb production
adaptation selected against authenticated nanopb 0.4.9 commit
`98bf4db69897b53434f3d0ba72e0a3ab1a902824`. nanopb is distributed under
the Zlib license; the complete unchanged upstream terms remain at
`third_party/nanopb/LICENSE.txt`, and both altered files retain the required
notice.

The exact `pb_read` definition is source-identical in authenticated pristine
nanopb 0.4.7, 0.4.8, and 0.4.9. Selecting 0.4.9 is an openCFW compatibility
baseline, not proof of Even Realities' historical checkout. The production
boundary is the complete Apollo-main stock span
`[0x0048F3BE,0x0048F454)`, its 13 external callers, recovered 16-byte stream
ABI, and no-interior-ingress topology. Three binary dependencies remain
explicit: private `buf_read` Thumb identity `0x0048F3A5` and the two runtime
error strings at `0x00787C70` and `0x0078B690`. No broader nanopb translation
unit or bootloader homolog is included. Qualification and packaging were
offline; no signing, flashing, reset, boot, or hardware operation was
performed.

`components/shared/nanopb/runtime_nanopb_buf_read.c`,
`runtime_nanopb_readbyte.c`, and `runtime_nanopb_private_read_pair.h` are the
current bounded altered nanopb production adaptation of private `buf_read`
and `pb_readbyte`, selected against authenticated nanopb 0.4.9 commit
`98bf4db69897b53434f3d0ba72e0a3ab1a902824`. nanopb is distributed under
the Zlib license; the complete unchanged upstream terms remain at
`third_party/nanopb/LICENSE.txt`, and all three local files retain the required
notice.

The definitions are source-identical in authenticated pristine nanopb 0.4.7,
0.4.8, and 0.4.9. Selecting 0.4.9 is an openCFW compatibility baseline, not
proof of Even Realities' historical checkout. The production boundary is the
complete Apollo-main spans `[0x0048F3A4,0x0048F3BE)` and
`[0x0048F454,0x0048F49C)`, their closed ingress topology, and their recovered
16-byte stream ABI. Full-span redirects preserve canonical callback identity
`0x0048F3A5`; exact-root Linux places the leaves at `0x007B31C4` and
`0x007B31E4`, and closes the overlay/component/package at the hashes recorded
in `EVIDENCE.md`. At that read-pair milestone the stock constructor,
`__aeabi_memcpy`, and two error strings remained binary-backed; the subsequent
bounded constructor tranche source-owns the constructor. No broader nanopb translation unit or
bootloader homolog is included. Qualification and packaging were offline; no
signing, flashing, reset, boot, or hardware operation was performed.

`components/shared/nanopb/runtime_nanopb_istream_from_buffer.c` and its header
are the ninth bounded altered nanopb production function, selected against
authenticated nanopb 0.4.9 commit
`98bf4db69897b53434f3d0ba72e0a3ab1a902824`. nanopb is distributed under
the Zlib license; the unchanged upstream terms remain at
`third_party/nanopb/LICENSE.txt`, and both altered files retain the notice.
The source-equivalent 0.4.7--0.4.9 range does not prove the vendor checkout.
Production replaces only `[0x0048F49C,0x0048F4B8)`, retains the 16-byte stream
ABI and callback identity `0x0048F3A5`, and leaves the bootloader excluded.

The overlay also contains the altered Zlib-licensed nanopb 0.4.9-compatible
`open_cfw_nanopb_decode_svarint` leaf. Its authenticated upstream definition
is `pb_decode.c[42912:43210]` at commit
`98bf4db69897b53434f3d0ba72e0a3ab1a902824`; its only executable relocation
binds directly to the separately source-owned
`open_cfw_nanopb_decode_varint`. This compatibility selection does not prove
the vendor's historical nanopb checkout. See
`docs/research/nanopb-decode-svarint-source-audit.md`.

`components/shared/nanopb/runtime_nanopb_decode_varint32.c` and `.h` are
altered Zlib-licensed compatibility adaptations of authenticated nanopb 0.4.9
`pb_decode_varint32_eof` and `pb_decode_varint32`. They are registered as two
bounded functions, not a combined opaque record. The selected 0.4.9 source is
compatible with the recovered 0.4.7--0.4.9 range and does not prove Even
Realities' historical point release or checkout. The unchanged upstream terms
remain at `third_party/nanopb/LICENSE.txt`. No bootloader homolog is included;
signing, flashing, reset, boot, and hardware execution remain deferred.

`components/shared/nanopb/runtime_nanopb_skip_string.c` and `.h` are altered
Zlib-licensed adaptations of authenticated nanopb `pb_skip_string`, selected
against 0.4.9 within the indistinguishable 0.4.7--0.4.9 range. They call only
the separately source-owned varint32 and read providers. This does not prove
the vendor checkout. No bootloader homolog exists; signing, flashing, reset,
boot, and hardware execution remain deferred.

`components/shared/nanopb/runtime_nanopb_skip_field.c` and `.h` are altered
Zlib-licensed adaptations of authenticated nanopb `pb_skip_field`, selected
against commit `98bf4db69897b53434f3d0ba72e0a3ab1a902824` within the
indistinguishable 0.4.7--0.4.9 range. They call only the separately
source-owned read, skip-varint, and skip-string providers and own their
diagnostic literal. This does not prove the vendor checkout. No bootloader
homolog exists; signing, flashing, reset, boot, and hardware execution remain
deferred.

`runtime_cmsis_event_flags.c` is a production-integrated bounded adapter for
CMSIS-FreeRTOS v10.5.1 `osEventFlagsNew`, `osEventFlagsSet`,
`osEventFlagsClear`, and `osEventFlagsWait`, selected at commit
`d213f261b5be6bb29a7cce8b84071706b72f4d53`. Copyright (c) 2013-2022 Arm
Limited. Its Apache-2.0 notice is retained in the source and pristine snapshot.
All fixed dependencies resolve to separately production-integrated IRQ and
FreeRTOS event-group providers. Four authenticated complete stock entries are
redirected atomically under independently recorded and ordinarily replayed
Apple/Linux placement and package pins. This makes no claim that Even used an
unmodified upstream checkout. Signing, flashing, and hardware execution remain
deferred.

`runtime_cmsis_timer_new.c` is a production-integrated bounded adapter for
CMSIS-FreeRTOS v10.5.1 `osTimerNew` and private `TimerCallback`, selected at
commit `d213f261b5be6bb29a7cce8b84071706b72f4d53`. Copyright (c) 2013-2022 Arm
Limited. Its Apache-2.0 notice is retained in the source and pristine snapshot.
The pair preserves the recovered 44-byte static timer threshold, 8-byte
callback record, bit-zero dynamic-allocation tag, and selective cleanup. Every
fixed dependency resolves to a separately source-owned IRQ, heap, or FreeRTOS
timer provider. Only the authenticated public constructor entry is redirected;
source-created timers store the source callback. Apple and Linux placement and
package pins were independently recorded and ordinarily replayed. This makes
no claim that Even used an unmodified upstream checkout. Signing, flashing,
and hardware execution remain deferred.

`components/shared/nanopb/runtime_nanopb_dec_varint.c` and `.h` are altered
Zlib-licensed adaptations of authenticated nanopb private `pb_dec_varint` at
commit `98bf4db69897b53434f3d0ba72e0a3ab1a902824`. They replace the complete
stock function, call only separately source-owned nanopb providers, and own
both diagnostic strings. This does not prove the vendor checkout; Linux
reproduction and hardware execution remain deferred.

`components/shared/nanopb/runtime_nanopb_dec_bytes.c` and `.h` are altered
Zlib-licensed adaptations of authenticated nanopb private `pb_dec_bytes` at
commit `98bf4db69897b53434f3d0ba72e0a3ab1a902824`. They replace the complete
stock function, call only the separately source-owned varint32 and stream-read
providers, and own all three diagnostic strings. This does not prove the
vendor checkout; Linux reproduction and hardware execution remain deferred.

`components/shared/nanopb/runtime_nanopb_dec_string.c` and `.h` are altered
Zlib-licensed adaptations of authenticated nanopb private `pb_dec_string` at
commit `98bf4db69897b53434f3d0ba72e0a3ab1a902824`. They replace the complete
stock function, call only the separately source-owned varint32 and stream-read
providers, and own all three diagnostic strings. This does not prove the
vendor checkout; Linux reproduction and hardware execution remain deferred.

`components/shared/nanopb/runtime_nanopb_dec_submessage.c` and `.h` are
altered Zlib-licensed adaptations of authenticated nanopb private
`pb_dec_submessage` at commit
`98bf4db69897b53434f3d0ba72e0a3ab1a902824`. They replace the complete stock
function, resolve substream construction/closure to source-owned providers,
own the diagnostic string, and retain the larger `pb_decode_inner` routine as
an explicit stock seam at `0x0048FE98`. This does not prove the vendor
checkout; Linux reproduction and hardware execution remain deferred.

`components/shared/nanopb/runtime_nanopb_read_raw_value.c` and `.h` are
altered Zlib-licensed adaptations of authenticated nanopb private
`read_raw_value`, selected against commit
`98bf4db69897b53434f3d0ba72e0a3ab1a902824` within the indistinguishable
0.4.7--0.4.9 range. They call only the separately source-owned `pb_read`
provider and own both diagnostic literals. This does not prove the vendor
checkout. No bootloader homolog exists; signing, flashing, reset, boot, and
hardware execution remain deferred.

`runtime_cmsis_sync_ops.c` is a production-integrated bounded adapter
for CMSIS-FreeRTOS v10.5.1 `osMutexAcquire`, `osMutexRelease`, and
`osSemaphoreRelease`, selected at commit
`d213f261b5be6bb29a7cce8b84071706b72f4d53`. Copyright (c) 2013-2022 Arm
Limited. The Apache-2.0 terms are retained in the source and in
`third_party/cmsis-freertos/LICENSE`.

The candidate reproduces the recursive-mutex tag ABI, CMSIS status mapping,
task/ISR semaphore-release split, and PendSV request. Its six fixed call
dependencies resolve to separately production-integrated FreeRTOS V10.5.1
queue providers and private `IRQ_Context`. Three authenticated complete stock
entries are redirected atomically under independently recorded and replayed
Apple/Linux placement and package pins. This makes no claim that Even used an
unmodified upstream checkout. Signing, flashing, and hardware execution remain
deferred.

`runtime_cmsis_memory_pool_new.c` is a production-integrated bounded adapter
for CMSIS-FreeRTOS v10.5.1 `osMemoryPoolNew`, selected at commit
`d213f261b5be6bb29a7cce8b84071706b72f4d53`. Copyright (c) 2013-2022 Arm
Limited. Its Apache-2.0 notice is retained in the source and pristine snapshot.
The adapter preserves the recovered 116-byte pool control block, embedded
static counting semaphore, 32-bit block-array sizing, storage ownership bits,
and authenticated v10.5.1 mixed-storage quirks. Every fixed dependency resolves
to separately source-owned IRQ, heap_4, or FreeRTOS queue providers. Apple and
Linux placement and package pins were independently recorded and ordinarily
replayed. This makes no claim that Even used an unmodified upstream checkout.
Signing, flashing, and hardware execution remain deferred.

`components/shared/freertos/runtime_freertos_queue_receive_from_isr.c` and
`runtime_freertos_queue_copy_data_from_queue.c` are altered MIT-licensed
adaptations of FreeRTOS-Kernel V10.5.1 `queue.c`, selected at commit
`def7d2df2b0506d3d249334974f51e427c17a41c`. They replace complete stock
`xQueueReceiveFromISR` and `prvCopyDataFromQueue` entries. The upstream license
is retained in the source and `third_party/freertos-kernel/LICENSE.md`.

`runtime_cmsis_semaphore_acquire.c` and
`runtime_cmsis_memory_pool_ops.c` are production-integrated bounded adapters
for CMSIS-FreeRTOS v10.5.1 at commit
`d213f261b5be6bb29a7cce8b84071706b72f4d53`. Copyright (c) 2013-2022 Arm
Limited. Their Apache-2.0 notices are retained in source and
`third_party/cmsis-freertos/LICENSE`. They replace complete stock
`osSemaphoreAcquire`, `osMemoryPoolAlloc`, `osMemoryPoolFree`, `CreateBlock`,
`AllocBlock`, and `FreeBlock` entries under independently recorded Apple and
Linux placement pins. This does not prove Even used an unmodified upstream
checkout. Signing, flashing, and hardware execution remain deferred.

`runtime_cmsis_timer_ops.c` is a production-integrated bounded adapter
for CMSIS-FreeRTOS v10.5.1 `osTimerStart`, `osTimerStop`, and
`osTimerDelete`, selected at commit
`d213f261b5be6bb29a7cce8b84071706b72f4d53`. Copyright (c) 2013-2022 Arm
Limited. Its Apache-2.0 notice is retained in the source and the pristine
snapshot. The adapter calls only production source-owned IRQ, FreeRTOS
timer-command/state/context, and heap-free providers and preserves the tagged
dynamic callback allocation ABI. Three authenticated complete stock entries
are redirected atomically under independently recorded and ordinarily replayed
Apple/Linux placement and package pins. This makes no claim that Even used an
unmodified upstream checkout. Signing, flashing, and hardware execution remain
deferred.

`components/shared/nanopb/runtime_nanopb_make_string_substream.c` and `.h`
are altered Zlib-licensed adaptations of authenticated nanopb
`pb_make_string_substream` at commit
`98bf4db69897b53434f3d0ba72e0a3ab1a902824`. The production source replaces
the stock compiler-runtime copy with explicit assignments for the four
recovered stream fields. This does not prove the vendor checkout; Linux
reproduction and hardware execution remain deferred.

`components/shared/nanopb/runtime_nanopb_decode_bool.c`,
`runtime_nanopb_decode_bool.h`, `runtime_nanopb_dec_bool.c`, and
`runtime_nanopb_dec_bool.h` are altered Zlib-licensed adaptations of
authenticated nanopb public `pb_decode_bool` and private `pb_dec_bool` at
commit `98bf4db69897b53434f3d0ba72e0a3ab1a902824`. They are bounded to complete
stock spans and call only source-owned nanopb providers. This does not prove
the vendor checkout; Linux reproduction and hardware execution remain
deferred.

`components/shared/nanopb/runtime_nanopb_iterator_cluster.c` and `.h` are
altered Zlib-licensed adaptations of authenticated nanopb `pb_common.c` at
compatibility commit `98bf4db69897b53434f3d0ba72e0a3ab1a902824`. Nine
selector-isolated leaves implement the descriptor provider, seven iterator
entry points, and default field callback. Eight complete stock entries redirect
to those leaves; application/schema callback dispatch remains explicit ABI.
This does not prove the vendor checkout. Linux reproduction and hardware
execution remain deferred.

`components/shared/nanopb/runtime_nanopb_defaults_pair.c` and `.h` are altered
Zlib-licensed adaptations of authenticated nanopb 0.4.9 private
`pb_field_set_to_default` and `pb_message_set_to_defaults` at compatibility
commit `98bf4db69897b53434f3d0ba72e0a3ab1a902824`. Two selector-isolated leaves
replace both complete stock entries. Stream, tag, iterator, and recursive
defaults edges bind to separately reviewed source providers; private
`decode_field @ 0x0048FBE4` remains an explicit fixed executable seam. This
does not prove the vendor checkout. Linux reproduction and hardware execution
remain deferred.

`components/shared/nanopb/runtime_nanopb_dispatch_extension.c` and `.h` are
altered Zlib-licensed adaptations of authenticated nanopb private
`decode_field`, `default_extension_decoder`, and `decode_extension` at
compatibility commit `98bf4db69897b53434f3d0ba72e0a3ab1a902824`. They replace
all three complete executable stock entries, own both diagnostic literals,
and retain only dynamic application/schema callback ABI; the adjacent
field-decoder closure is separately production-integrated. Exact definition identity through checked
official 0.4.4--0.4.9.1 tags does not prove the vendor checkout. Linux
reproduction and hardware execution remain deferred.

`components/shared/nanopb/runtime_nanopb_field_decoder_cluster.c` and `.h`
are altered Zlib-licensed adaptations of authenticated nanopb private
`decode_basic_field`, `decode_static_field`, `decode_pointer_field`,
`decode_callback_field`, and `pb_dec_fixed_length_bytes` at compatibility
commit `98bf4db69897b53434f3d0ba72e0a3ab1a902824`. Five selector-isolated
closures replace all five complete stock entries and bind every fixed call to
separately reviewed source-owned nanopb providers. Two dynamic callback sites
remain explicit application/schema ABI. Official-tag definition intervals
establish compatibility no earlier than 0.4.6 for the complete unit but do
not prove the vendor checkout. Linux reproduction and hardware execution
remain deferred.

`components/shared/ring_buffer/runtime_ring_buffer.c` is a bounded
MIT-licensed production adaptation of AndersKaloer/Ring-Buffer's dynamic
buffer implementation. The maintained compatibility source is upstream commit
`190e30bebcec22d7311fd941179d70b4f439c441`; authenticated stock behavior
proves the source-equivalent interval begins at
`cda00e1efb815bad5100757f0d10d117f633ced6` but cannot distinguish the exact
Even checkout within that interval. Seven selector-isolated leaves replace all
seven live stock entries. Linux reproduction and hardware execution remain
deferred.

`components/apollo_main/core_overlay/candidates/iar_runtime_memory.S` is
GPL-3.0-only clean-room openCFW source recreating the authenticated G2 IAR
void-EABI public memcpy, aligned-entry memcpy, and memmove semantics. It does
not contain or claim provenance from IAR library source. Three
selector-isolated relocation-free sections replace the complete callable stock
spans after randomized target emulation and instruction-count qualification.
Apple and Linux production artifacts are independently pinned; hardware timing
remains deferred.

`components/apollo_main/core_overlay/candidates/iar_runtime_math_errno.S` is
GPL-3.0-only clean-room openCFW source recreating the bounded G2 hard-float
`sqrtf`, EDOM/ERANGE setters, and errno-address semantics. It contains no IAR
library source and makes no exact EWARM provenance claim. The candidate is
target-qualified and installed by guarded stock redirects under independently
recorded and replayed Apple/Linux placement profiles; hardware execution
remains deferred.
`components/shared/freertos/runtime_freertos_queue_receive.c` and `.h` are
MIT-licensed bounded adaptations of FreeRTOS-Kernel V10.5.1 `xQueueReceive`,
`prvUnlockQueue`, `vTaskPlaceOnEventList`, and
`prvAddCurrentTaskToDelayedList` at commit
`def7d2df2b0506d3d249334974f51e427c17a41c`. Selector-isolated strict builds
replace all four complete stock entries and bind fixed dependencies only to
separately source-owned providers.

`components/shared/freertos/runtime_freertos_queue_copy_data_to_queue.c`,
`runtime_freertos_queue_generic_send_from_isr.c`, and
`runtime_freertos_task_priority_disinherit.c` are MIT-licensed bounded
adaptations from the same authenticated commit. They replace the complete
generic ISR-send dependency chain.

`runtime_cmsis_message_queue_put.c` and
`runtime_cmsis_message_queue_get.c` are Apache-2.0 bounded adaptations of
CMSIS-FreeRTOS v10.5.1 at commit
`d213f261b5be6bb29a7cce8b84071706b72f4d53`. Both complete public stock
entries redirect to source leaves whose task and ISR dependencies are wholly
source-owned. This does not claim the unique historical vendor checkout.
`components/shared/freertos/runtime_freertos_task_delay.c` is an MIT-licensed
bounded adaptation of FreeRTOS-Kernel V10.5.1 `vTaskDelay` at commit
`def7d2df2b0506d3d249334974f51e427c17a41c`.
`runtime_cmsis_delay.c` is an Apache-2.0 bounded adaptation of
CMSIS-FreeRTOS v10.5.1 `osDelay` at commit
`d213f261b5be6bb29a7cce8b84071706b72f4d53`. Both complete stock entries
redirect to strict source leaves; all fixed task-delay dependencies are
separately source-owned.

`components/shared/freertos/runtime_freertos_task_priority_set.c` and `.h`
are MIT-licensed bounded adaptations of FreeRTOS-Kernel V10.5.1
`vTaskPrioritySet` at commit
`def7d2df2b0506d3d249334974f51e427c17a41c` over the recovered G2 TCB and
ready-list ABI. `runtime_cmsis_thread_set_priority.c` is an Apache-2.0 bounded
adaptation of CMSIS-FreeRTOS v10.5.1 `osThreadSetPriority` at commit
`d213f261b5be6bb29a7cce8b84071706b72f4d53`. Both complete stock entries
redirect to strict source leaves and all fixed dependencies are separately
source-owned. This does not claim the unique historical vendor checkout.

`components/shared/freertos/runtime_freertos_task_delete.c` and `.h` are
MIT-licensed bounded adaptations of FreeRTOS-Kernel V10.5.1
`eTaskGetState`, `prvDeleteTCB`, and `vTaskDelete` at commit
`def7d2df2b0506d3d249334974f51e427c17a41c` over the recovered G2 scheduler,
list, allocation-status, and 112-byte TCB ABI. `runtime_cmsis_thread_terminate.c`
is an Apache-2.0 bounded adaptation of CMSIS-FreeRTOS v10.5.1
`osThreadTerminate` at commit
`d213f261b5be6bb29a7cce8b84071706b72f4d53`. All four complete stock entries
redirect to strict source leaves and every fixed dependency is separately
source-owned. This does not claim the unique historical vendor checkout.

`components/shared/freertos/runtime_freertos_task_notify.c` and `.h` are
MIT-licensed bounded adaptations of FreeRTOS-Kernel V10.5.1
`xTaskGenericNotifyWait`, `xTaskGenericNotify`, and
`xTaskGenericNotifyFromISR` at commit
`def7d2df2b0506d3d249334974f51e427c17a41c` over the independently recovered
G2 notification, TCB, list, interrupt-mask, and scheduler ABI.
`runtime_cmsis_thread_flags.c` is an Apache-2.0 bounded adaptation of
CMSIS-FreeRTOS v10.5.1 `osThreadFlagsSet` and `osThreadFlagsWait` at commit
`d213f261b5be6bb29a7cce8b84071706b72f4d53`. It intentionally preserves the
stock behavior before the later `bb8a350a` re-notification repair. All five
complete callable spans redirect to strict source leaves; the adjacent literal
and alignment gaps remain explicitly stock-owned. This does not claim the
unique historical vendor checkout or the provenance of the G2 TCB patch.

`runtime_cmsis_thread_new.c` is an Apache-2.0 bounded adaptation of
CMSIS-FreeRTOS v10.5.1 `osThreadNew` at commit
`d213f261b5be6bb29a7cce8b84071706b72f4d53`. The complete stock wrapper
redirects to a strict source leaf. Its calls bind to the source-owned IRQ
helper and the authenticated retained FreeRTOS V10.5.1 static/dynamic task
creators; the separately documented `0x70` G2 TCB extension remains a vendor
compatibility seam and is not attributed to Arm.

`runtime_cmsis_kernel_lifecycle.c` is an Apache-2.0 bounded adaptation of
CMSIS-FreeRTOS v10.5.1 `osKernelInitialize` and `osKernelStart` at commit
`d213f261b5be6bb29a7cce8b84071706b72f4d53`. The writer pair is admitted
atomically with the CMSIS `KernelState` word already read by the source-owned
get-state wrapper. It calls source-owned IRQ/scheduler-state providers and the
authenticated retained FreeRTOS V10.5.1 scheduler-start boundary; it does not
claim ownership of the G2 scheduler globals or Apollo port integration.

`at_tp.c` is an independently authored GPL-3.0-only clean-room reconstruction
of the retained G2 `platform/service/eAT/at_tp.c` behavior. It uses only
authenticated command behavior, retained literal addresses, and explicit
output/touch-driver/CMSIS-delay ABI bindings; no historical vendor source or
stock object bytes are included. Hardware validation remains blocked by
unavailable authorized physical G2 touch-panel evidence.

`at_buzzer.c` is an independently authored GPL-3.0-only clean-room
reconstruction of the retained G2 `platform/service/eAT/at_buzzer.c` command
behavior. It contains no historical vendor source or stock object bytes. One
strict-relocation Thumb leaf replaces the complete stock handler and pool while
binding only to authenticated retained response strings, AT output, and buzzer
driver entries. Audible output, frequency/pitch, duty-cycle, beat timing,
predefined playback, and stop behavior remain blocked by unavailable authorized
physical G2 buzzer evidence.

`service_gesture_processor.c` is an independently authored GPL-3.0-only
clean-room reconstruction of the retained G2
`platform/input/service_gesture_processor.c` behavior. It contains no
historical vendor source or stock object bytes. Five strict-relocation Thumb
leaves replace the complete stock object and pools while binding only to
authenticated touch, buzzer, product-mode, event-publish, logging, SRAM, and
retained-string interfaces. Physical touch/proximity electrical behavior,
event timing, debounce, and gesture interpretation remain blocked by
unavailable authorized G2 hardware evidence.

`drv_cy8c4046fni.c` is an independently authored GPL-3.0-only clean-room
reconstruction of the retained G2 `driver/touch/drv_cy8c4046fni.c` host-driver
behavior. It contains no historical vendor source or stock executable bytes.
Twenty-three strict-relocation Thumb leaves replace every executable stock
function while binding to authenticated retained HAL-I2C, board-control,
delay, SRAM, callback-table, and sibling-source interfaces. The directly
addressed callback/string pool remains authenticated stock data. Stock
EasyLogger diagnostics are intentionally omitted because they do not control
controller behavior. Physical I2C, reset/DFU, report timing, and CapSense
validation remains blocked by unavailable authorized G2 hardware evidence.

`cordio_gatt_profile.c` is an Apache-2.0 production adaptation of Packetcraft
Cordio r20.05c `ble-profiles/sources/profiles/gatt/gatt_main.c` at commit
`3656312d6b73e2a2c1c8b33ee0385bc199dd97e6`. It preserves the six linked
functional definitions over the recovered G2 control-block, handle-list, and
provider ABI. The stock-only EasyLogger expansion in `GattDiscover` is omitted
as non-controlling diagnostics. The exact upstream source, header, license,
and offline verifier are retained in `third_party/packetcraft-gatt-profile`.
This selected compatible commit is not a claim about the unrecoverable private
historical G2 checkout. Physical ATT/CCCD/indication and peer interoperability
validation remains blocked by unavailable authorized G2/EM9305 evidence.

`ble_ota_profile.c` is a BSD-3-Clause bounded production adaptation of the
AmbiqSuite 2.5.1 AMOTA application skeleton at commit
`de5c6ba3044f4ef0f0c907c3f83fbbaa5795262f` plus independently reconstructed
G2-local event, connection, and transport actions. It contains no historical
private G2 source or stock executable bytes. All seven linked functions route
to strict-relocation Thumb leaves; the authenticated 80-byte stock
literal/callback pool is retained. The selected public revision is an oracle,
not a claim about Even's historical checkout. Physical OTA CCC, reset,
disconnect, notification timing, and peer interoperability validation remains
blocked by unavailable authorized G2/EM9305 evidence.

`ble_ring_profile.c` is an independently authored GPL-3.0-only clean-room
reconstruction of the retained G2 `platform/ble/profiles/ring/profile_ring.c`
behavior. It contains no historical private G2 source or stock executable
bytes. All seven linked functions route to strict-relocation Thumb leaves;
the authenticated 134-byte stock callback/literal pool is retained. Stock
EasyLogger and hexdump calls are omitted as non-controlling diagnostics.
Physical service discovery, delayed CCC timing, ATT RX/TX behavior, controller
concurrency, and peer interoperability validation remains blocked by
unavailable authorized G2/EM9305 evidence.

`callback_facades.c` is an independently authored GPL-3.0-only clean-room
reconstruction of the retained G2
`platform/service/callback_mgr/cb_charge.c` and `cb_msg_notif.c` facade
behavior. It contains no historical private G2 source or stock executable
bytes. Ten strict-relocation Thumb leaves replace all linked functions while
binding only to the retained generic callback-manager ABI. Both 34-byte stock
diagnostic/type pools are retained; EasyLogger calls are omitted as
non-controlling diagnostics. These pure facades perform no direct hardware
operation.

`callback_manager.c` is an independently authored GPL-3.0-only clean-room
reconstruction of the retained G2
`platform/service/callback_mgr/callback_manager.c` behavior. It contains no
historical private G2 source or stock executable bytes. Eight strict-relocation
Thumb leaves replace all linked manager functions and bind only to the already
source-owned synchronized heap wrappers or redirected manager helpers. The
118-byte stock diagnostic pool is retained; EasyLogger calls are omitted as
non-controlling observability.

`cb_ring_battery.c` is an independently authored GPL-3.0-only clean-room
reconstruction of the retained G2
`platform/service/callback_mgr/cb_ring_battery.c` behavior. It contains no
historical private G2 source or stock executable bytes. Five strict-relocation
Thumb leaves replace all linked facade functions and bind only to the
source-owned callback manager or retained ring-battery consumer. The 30-byte
stock type/diagnostic/path/literal pool is retained; EasyLogger calls are
omitted as non-controlling observability.

`ux_battery_sync.c` is an independently authored GPL-3.0-only clean-room
reconstruction of the retained G2 `app/ux/ux_battery_sync/ux_battery_sync.c`
service-record callback. It contains no historical private G2 source or stock
executable bytes. Its strict relocations bind only to bounded first-party
providers; the 84-byte stock diagnostic/path/literal pool is retained.

`service_ring_battery.c` is an independently authored GPL-3.0-only clean-room
reconstruction of the retained G2
`platform/service/ring_battery/service_ring_battery.c` behavior. It contains no
historical private G2 source or stock executable bytes. Five strict-contract
Thumb leaves replace all linked functions; their two relocations bind only to
the recovered local and peer service-record transports. The 44-byte stock
diagnostic/path/literal pool is retained. EasyLogger diagnostics are omitted as
non-controlling observability.

`pb_service_ring.c` is an independently authored GPL-3.0-only clean-room
reconstruction of the four linked entries from the retained G2
`platform/protocols/pb_service_ring/pb_service_ring.c` object plus the bounded
nanopb output callback required by the recovered encoder ABI. It contains no
historical private G2 source or stock executable bytes. Five selector-isolated
strict-relocation Thumb leaves replace all 1,362 linked stock function bytes;
the 150-byte official alignment/literal tail remains retained. Stock
EasyLogger diagnostics are omitted as non-controlling observability. Live
paired-G2 relay, nanopb interoperability, and physical Ring-event behavior are
blocked by unavailable authorized physical evidence.

`pb_service_glasses_case.c` is an independently authored GPL-3.0-only
clean-room reconstruction of the four linked entries from the retained G2
`platform/protocols/pb_service_glasses_case/pb_service_glasses_case.c` object
plus the bounded nanopb output callback required by the recovered encoder ABI.
It contains no historical private G2 source or stock executable bytes. Five
selector-isolated strict-relocation Thumb leaves replace all 1,360 linked stock
function bytes; the 124-byte official literal pool remains retained. Stock
EasyLogger diagnostics are omitted as non-controlling observability. Live
service-`0x81` temple/case interoperability and physical case-state validation
are blocked by unavailable authorized physical evidence.

`pb_service_conversate.c` is an independently authored GPL-3.0-only clean-room
reconstruction of the six linked entries from the retained G2
`platform/protocols/pb_service_conversate/pb_service_conversate.c` object plus
bounded output-buffer and message-zero helpers required by the recovered ABI.
It contains no historical private G2 source or stock executable bytes. Eight
selector-isolated strict-relocation Thumb leaves replace all 1,776 linked stock
function bytes; the 128-byte official literal pool remains retained. Stock
EasyLogger/hexdump diagnostics are omitted as non-controlling observability.
Live service-`0x0B` master/peer BLE, timing, and conversate UI validation are
blocked by unavailable authorized physical evidence.

`pb_service_teleprompt.c` is an independently authored GPL-3.0-only clean-room
reconstruction of the seven linked entries from the retained G2
`platform/protocols/pb_service_teleprompt/pb_service_teleprompt.c` object plus
bounded output-buffer and message-zero helpers required by the recovered ABI.
It contains no historical private G2 source or stock executable bytes. Nine
selector-isolated strict-relocation Thumb leaves replace all 1,854 linked stock
function bytes; the 130-byte official alignment/literal tail remains retained.
Stock EasyLogger/hexdump diagnostics are omitted as non-controlling
observability. Live service-6 master/peer BLE, timing, and teleprompt UI
validation are blocked by unavailable authorized physical evidence.

`pb_service_even_ai.c` is an independently authored GPL-3.0-only clean-room
reconstruction of the 25 linked entries from the retained G2
`platform/protocols/pb_service_even_ai/pb_service_even_ai.c` object plus the
bounded output-buffer and message-zero helpers required by the recovered ABI.
It contains no historical private G2 source or stock executable bytes.
Twenty-seven selector-isolated strict-relocation Thumb leaves replace all
8,404 linked stock function bytes; 552 distributed official alignment/literal
pool bytes remain retained. Stock EasyLogger/hexdump/assert diagnostics are
omitted as non-controlling observability. Live service-7 master/peer BLE and
Even-AI UI validation are blocked by unavailable authorized physical evidence.

`pb_service_onboarding.c` is an independently authored GPL-3.0-only clean-room
reconstruction of the nine linked entries from the retained G2
`platform/protocols/pb_service_onboarding/pb_service_onboarding.c` object plus
bounded output-buffer, zero-fill, and common-encode helpers required by the
recovered ABI. It contains no historical private G2 source or stock executable
bytes. Twelve selector-isolated strict-relocation Thumb leaves replace all
3,024 linked stock function bytes; 192 distributed official alignment/literal
bytes remain retained. Stock EasyLogger/assert diagnostics are omitted as
non-controlling observability. Live service-`0x10` peer BLE, display-ready,
onboarding-control, response, notification, and nanopb interoperability are
blocked by unavailable authorized physical evidence.

`pb_service_notification.c` is an independently authored GPL-3.0-only
clean-room reconstruction of the nine linked entries from the retained G2
`platform/protocols/pb_service_notification/pb_service_notification.c` object
plus bounded output-buffer, zero-fill, and common-encode helpers required by
the recovered ABI. It contains no historical private G2 source or stock
executable bytes. Twelve selector-isolated strict-relocation Thumb leaves
replace all 3,318 linked stock function bytes; 238 distributed official
alignment/literal/descriptor bytes remain retained. Stock EasyLogger/assert
diagnostics are omitted as non-controlling observability. Live service-4 peer
BLE, notification-control, whitelist-control, whitelist-check,
app-not-whitelisted, and nanopb interoperability are blocked by unavailable
authorized physical evidence.

`pb_service_pair_mgr.c` is an independently authored GPL-3.0-only clean-room
reconstruction of the 20 linked entries from the retained G2
`platform/protocols/pb_service_dev_config/pb_service_pair_mgr.c` object plus a
bounded output-buffer writer required by the recovered ABI. It contains no
historical private G2 source or stock executable bytes. Twenty-one selector-
isolated strict-relocation Thumb leaves replace all 6,564 linked stock function
bytes; 724 distributed official alignment/literal bytes remain retained. Stock
EasyLogger/assert diagnostics are omitted as non-controlling observability.
Live service-`0x80` security-auth, pipe-role, ring-connect, BLE-parameter,
disconnect, unpair, peer BLE, and nanopb interoperability are blocked by
unavailable authorized responsive physical evidence.

`pb_service_setting.c` is an independently authored GPL-3.0-only clean-room
reconstruction of the eleven linked entries from the retained G2
`platform/protocols/pb_service_setting/pb_service_setting.c` object plus
bounded output-buffer and zero-fill helpers required by the recovered ABI. It
contains no historical private G2 source or stock executable bytes. Thirteen
selector-isolated strict-relocation Thumb leaves replace all 3,466 linked
stock function bytes; 334 distributed official alignment/literal bytes remain
retained. Stock EasyLogger diagnostics are omitted as non-controlling
observability. Live service-9 peer BLE, full-status, recalibration, silent-
mode, and nanopb interoperability are blocked by unavailable authorized
physical evidence.

`pb_service_dev_setting.c` is an independently authored GPL-3.0-only
clean-room reconstruction of the ten linked entries from the retained G2
`platform/protocols/pb_service_dev_config/pb_service_dev_setting.c` object plus
bounded output-buffer and common-encode/transport helpers required by the
recovered ABI. It contains no historical private G2 source or stock executable
bytes. Twelve selector-isolated strict-relocation Thumb leaves replace all
3,432 linked stock function bytes; 284 distributed official alignment/literal
bytes remain retained. Stock EasyLogger/assert diagnostics are omitted as
non-controlling observability. Live service-`0x80` peer BLE, destructive
factory-reset, restart, heartbeat, clock-sync, persistence, audio-control, and
nanopb interoperability are blocked by unavailable authorized physical
evidence.

`pb_service_quicklist.c` is an independently authored GPL-3.0-only clean-room
reconstruction of the ten linked entries from the retained G2
`platform/protocols/pb_service_quicklist/pb_service_quicklist.c` object plus
bounded buffer-write, message-zero, and common-transport helpers required by
the recovered ABI. It contains no historical private G2 source or stock
executable bytes. Thirteen selector-isolated strict-relocation Thumb leaves
replace all 3,468 linked stock function bytes; 280 distributed official
alignment/literal bytes remain retained. The multi-item notification copy is
limited to the twenty records that fit the recovered message workspace. Stock
EasyLogger/assert diagnostics are omitted as non-controlling observability.
Live service-`0x0C` peer BLE, persistent quicklist load/save, response,
notification, and nanopb interoperability are blocked by unavailable
authorized physical evidence.

`transport_protocol.c`, `ota_transport.c`, `efs_transport.c`,
`efs_service.c`, and `ota_service.c` are independently authored
GPL-3.0-only clean-room reconstructions of the authenticated G2-local packet
transports and EFS/OTA file-service policy. They contain no historical private
G2 source or stock executable bytes. Fifty-nine selector-isolated
strict-relocation Thumb leaves replace 32,798 linked stock function bytes while
retaining 2,392 authenticated official alignment/literal-pool bytes. Stock
EasyLogger diagnostics are omitted as non-controlling observability. Live peer,
dual-glasses, OTA receiver, EFS filesystem/media, disconnect, timeout, and
recovery validation are blocked by unavailable authorized responsive physical
evidence.

`ble_transport_profiles.c` is an independently authored GPL-3.0-only
clean-room reconstruction of the authenticated G2-local EUS, ESS, EFS, and NUS
Cordio application adapters. It contains no historical private G2 source or
stock executable bytes. Twenty-five selector-isolated strict-relocation Thumb
leaves replace all 2,698 linked stock function bytes while retaining 302
authenticated official literal/alignment bytes. Live CCC/RX/TX timing,
controller concurrency, and dual-device interoperability are blocked by the
absence of an authorized responsive G2/EM9305 peer and physical capture.

`system_alert.c` is an independently authored GPL-3.0-only clean-room
reconstruction of the seven callable entries in the authenticated G2
`app/gui/SystemAlert/systemAlert.c` object. It contains no historical private
G2 source or stock executable bytes. Seven selector-isolated strict-relocation
Thumb leaves replace all 2,174 callable stock bytes; the entry-alignment NOP
and 170-byte official pool remain retained. Live display, event-timing, IMU,
and paired-temple validation is blocked by unavailable authorized physical
evidence.

`system_close.c` is an independently authored GPL-3.0-only clean-room
reconstruction of all twenty callable entries in the authenticated G2
`app/gui/SystemClose/systemClose.c` object. It contains no historical private
G2 source or stock executable bytes. Twenty selector-isolated strict-relocation
Thumb leaves replace all 4,960 stock function bytes while 408 authenticated
official alignment/literal bytes remain retained. Live close-page display,
selection animation, IMU reflash, shutdown/minimize, and paired-temple
synchronization validation is blocked by unavailable authorized physical
evidence.

`freertos_cli_filesystem.c` is an independently authored GPL-3.0-only
clean-room reconstruction of all twelve callable entries in the authenticated
G2 `app/freertos_cli/freertos_cli_filesystem.c` object. It contains no
historical private G2 source or stock executable bytes. Twelve
selector-isolated strict-relocation Thumb leaves replace all 3,200 callable
stock bytes; 56 authenticated official alignment/literal bytes remain
retained. The implementation binds through the already bounded littlefs seam.
Live mounted-media mutation, persistence, corruption recovery, and concurrent
CLI validation is blocked by unavailable authorized responsive G2 hardware
and writable physical test media.

`service_nvdb.c` is an independently authored GPL-3.0-only clean-room
reconstruction of all five callable entries in the authenticated G2 factory
NVDB lifecycle object. Five strict-relocation Thumb leaves replace all 930
callable stock bytes while 122 authenticated official pool/alignment bytes
remain. Its default policy refuses destructive factory reset on missing or
mismatched media. Live persistence, recovery, and schema validation is blocked
by unavailable authorized responsive hardware and a golden `NVdb` capture.
