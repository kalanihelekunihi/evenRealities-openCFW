# Nordic SDK function correlation

This note records function-level source admission for Nordic code retained in the R1 application.
The production implementation must compile these functions from nRF5 SDK 17.1.0 (`ddde560`);
their recovered bodies are compatibility evidence and are not eligible for local reconstruction.
R1-specific parameters, callbacks, board ports, and application policy remain separate adapters.

## Method

The stock application is based at `0x00027000`. Exact printable literals and instruction bodies
were indexed in the application image and compared with the pinned SDK. A function was admitted
only when a function-local SDK fingerprint and the surrounding control flow, constants, event
cases, field accesses, and callees agreed. A diagnostic match by itself was not sufficient.

The build changes Nordic log-module decoration to `[RING]`, but preserves the SDK message payloads.
Generic strings such as service link-context failures, hexadecimal alphabets, or example-level Peer
Manager text remain unclassified where they do not uniquely identify a provider function. Some
Ghidra function `end` values include shared or non-contiguous compiler blocks; this map asserts the
entry and upstream function identity, not an unreliable recovered extent.

## Admitted functions

| Stock entry | Nordic SDK symbol | Pinned source |
| --- | --- | --- |
| `0x000272B8` | `nrf_atfifo_wspace_req` | `components/libraries/atomic_fifo/nrf_atfifo_internal.h` |
| `0x000272F0` | `nrf_atfifo_wspace_close` | `components/libraries/atomic_fifo/nrf_atfifo_internal.h` |
| `0x00027302` | `nrf_atfifo_rspace_req` | `components/libraries/atomic_fifo/nrf_atfifo_internal.h` |
| `0x0002733C` | `nrf_atfifo_rspace_close` | `components/libraries/atomic_fifo/nrf_atfifo_internal.h` |
| `0x0002734E` | `nrf_atfifo_space_clear` | `components/libraries/atomic_fifo/nrf_atfifo_internal.h` |
| `0x00027380` | `nrf_atomic_internal_mov` | `components/libraries/atomic/nrf_atomic_internal.h` |
| `0x00027398` | `nrf_atomic_internal_orr` | `components/libraries/atomic/nrf_atomic_internal.h` |
| `0x000273B2` | `nrf_atomic_internal_and` | `components/libraries/atomic/nrf_atomic_internal.h` |
| `0x000273CC` | `nrf_atomic_internal_eor` | `components/libraries/atomic/nrf_atomic_internal.h` |
| `0x000273E6` | `nrf_atomic_internal_add` | `components/libraries/atomic/nrf_atomic_internal.h` |
| `0x00027400` | `nrf_atomic_internal_sub` | `components/libraries/atomic/nrf_atomic_internal.h` |
| `0x0002741A` | `nrf_atomic_internal_cmp_exch` | `components/libraries/atomic/nrf_atomic_internal.h` |
| `0x00027444` | `nrf_atomic_internal_sub_hs` | `components/libraries/atomic/nrf_atomic_internal.h` |
| `0x00027488` | `Reset_Handler` | `modules/nrfx/mdk/arm_startup_nrf52840.s` |
| `0x0002749C` | `NMI_Handler` | `modules/nrfx/mdk/arm_startup_nrf52840.s` |
| `0x000274A2` | `Default_Handler` | `modules/nrfx/mdk/arm_startup_nrf52840.s` |
| `0x00031A74` | `nrfx_twim_0_irq_handler` | `modules/nrfx/drivers/src/nrfx_twim.c` |
| `0x00031A84` | `nrfx_twim_1_irq_handler` | `modules/nrfx/drivers/src/nrfx_twim.c` |
| `0x00031A94` | `nrfx_spim_2_irq_handler` | `modules/nrfx/drivers/src/nrfx_spim.c` |
| `0x00033364` | `SystemInit` | `modules/nrfx/mdk/system_nrf52.c` |
| `0x0007CA7C` | `nvmc_config` | `modules/nrfx/mdk/system_nrf52.c` |
| `0x00098DC0` | `xfer_completeness_check` | `modules/nrfx/drivers/src/nrfx_twim.c` |
| `0x00037530` / `0x00038166` | `__NVIC_ClearPendingIRQ` | `components/toolchain/cmsis/include/core_cm4.h` |
| `0x00038180` | `__NVIC_SystemReset` | `components/toolchain/cmsis/include/core_cm4.h` |
| `0x000381C8` | `__NVIC_SystemReset` | `components/toolchain/cmsis/include/core_cm4.h` |
| `0x0004826C` | `active_flag_count` | `components/ble/common/ble_conn_state.c` |
| `0x0004898C` | `addr_compare` | `components/ble/peer_manager/id_manager.c` |
| `0x000489B2` | `addr_is_aligned32` | `components/libraries/fstorage/nrf_fstorage.c` |
| `0x000489BE` | `addr_is_within_bounds` | `components/libraries/fstorage/nrf_fstorage.c` |
| `0x0004C6D0` | `allow_repairing` | `components/ble/peer_manager/security_dispatcher.c` |
| `0x00048CD0` | `ah` | `components/ble/peer_manager/id_manager.c` |
| `0x0004FB6C` | `auth_status_success_process` | `components/ble/peer_manager/security_dispatcher.c` |
| `0x00051440` | `bcs_internal_state_reset` | `components/ble/common/ble_conn_state.c` |
| `0x000514E0` | `blcm_link_ctx_get` | `components/ble/ble_link_ctx_manager/ble_link_ctx_manager.c` |
| `0x00051528` | `ble_advdata_encode` | `components/ble/common/ble_advdata.c` |
| `0x000516AA` | `ble_advdata_parse` | `components/ble/common/ble_advdata.c` |
| `0x000516CA` | `ble_advdata_search` | `components/ble/common/ble_advdata.c` |
| `0x00051E04` | `ble_conn_state_conn_idx` | `components/ble/common/ble_conn_state.c` |
| `0x00051E18` | `ble_conn_state_encrypted` | `components/ble/common/ble_conn_state.c` |
| `0x00051E38` | `ble_conn_state_for_each_connected` | `components/ble/common/ble_conn_state.c` |
| `0x00051E4C` | `ble_conn_state_for_each_set_user_flag` | `components/ble/common/ble_conn_state.c` |
| `0x00051E78` | `ble_conn_state_init` | `components/ble/common/ble_conn_state.c` |
| `0x00051E7C` | `ble_conn_state_lesc` | `components/ble/common/ble_conn_state.c` |
| `0x00051E9C` | `ble_conn_state_mitm_protected` | `components/ble/common/ble_conn_state.c` |
| `0x00051EBC` | `ble_conn_state_peripheral_conn_count` | `components/ble/common/ble_conn_state.c` |
| `0x00051EDC` | `ble_conn_state_role` | `components/ble/common/ble_conn_state.c` |
| `0x00051F00` | `ble_conn_state_status` | `components/ble/common/ble_conn_state.c` |
| `0x00051F24` | `ble_conn_state_user_flag_acquire` | `components/ble/common/ble_conn_state.c` |
| `0x00051F3C` | `ble_conn_state_user_flag_get` | `components/ble/common/ble_conn_state.c` |
| `0x00051F6C` | `ble_conn_state_user_flag_set` | `components/ble/common/ble_conn_state.c` |
| `0x00051FA4` | `ble_conn_state_valid` | `components/ble/common/ble_conn_state.c` |
| `0x00051FB8` | `ble_device_addr_encode` | `components/ble/common/ble_advdata.c` |
| `0x00052018` | `ble_dfu_buttonless_async_svci_init` | `components/ble/ble_services/ble_dfu/ble_dfu_unbonded.c` |
| `0x0005380C` | `ble_evt_handler` | `components/ble/common/ble_conn_state.c` |
| `0x00053924` | `ble_evt_handler` | `components/ble/peer_manager/peer_manager.c` |
| `0x000539A8` | `ble_srv_is_indication_enabled` | `components/ble/common/ble_srv_common.c` |
| `0x000539B0` | `ble_srv_is_notification_enabled` | `components/ble/common/ble_srv_common.c` |
| `0x000566AC` | `buf_prealloc` | `components/libraries/log/src/nrf_log_frontend.c` |
| `0x00056774` | `buffer_is_empty` | `components/libraries/log/src/nrf_log_frontend.c` |
| `0x000578CC` | `car_update_needed` | `components/ble/peer_manager/gatt_cache_manager.c` |
| `0x000579A8` | `characteristic_add` | `components/ble/common/ble_srv_common.c` |
| `0x00058218` | `claim` | `components/ble/peer_manager/peer_id.c` |
| `0x00059BA0` | `conn_handle_list_get` | `components/ble/common/ble_conn_state.c` |
| `0x00059BDE` | `conn_int_encode` | `components/ble/common/ble_advdata.c` |
| `0x00059C68` | `conn_sec_failure` | `components/ble/peer_manager/security_dispatcher.c` |
| `0x0005A65C` | `data_length_update` | `components/ble/nrf_ble_gatt/nrf_ble_gatt.c` |
| `0x0005C110` | `delete_execute` | `components/libraries/fds/fds.c` |
| `0x0005CCFC` | `dropped_sat16_get` | `components/libraries/log/src/nrf_log_frontend.c` |
| `0x0005D314` | `encryption_failure` | `components/ble/peer_manager/security_dispatcher.c` |
| `0x0005D514` | `erase` | `components/libraries/fstorage/nrf_fstorage_sd.c` |
| `0x0005E5B0` | `event_prepare` | `components/libraries/fds/fds.c` |
| `0x0005E624` | `event_send` | `components/libraries/fds/fds.c` |
| `0x0005E644` | `event_send` | `components/libraries/fstorage/nrf_fstorage_sd.c` |
| `0x0005EB94` | `events_send_from_err_code` | `components/ble/peer_manager/security_manager.c` |
| `0x0005ED08` | `evt_send` | `components/ble/peer_manager/security_manager.c` |
| `0x0005EC88` | `evt_send` | `components/ble/peer_manager/gatt_cache_manager.c` |
| `0x0005ECA4` | `evt_send` | `components/ble/peer_manager/gatts_cache_manager.c` |
| `0x0005ECC0` | `evt_send` | `components/ble/peer_manager/peer_manager.c` |
| `0x0005ECEC` | `evt_send` | `components/ble/peer_manager/security_dispatcher.c` |
| `0x00063E30` | `fds_file_delete` | `components/libraries/fds/fds.c` |
| `0x00063E78` | `fds_gc` | `components/libraries/fds/fds.c` |
| `0x00063EB8` | `fds_init` | `components/libraries/fds/fds.c` |
| `0x00063FA4` | `fds_record_close` | `components/libraries/fds/fds.c` |
| `0x00063FEC` | `fds_record_find` | `components/libraries/fds/fds.c` |
| `0x00063FFA` | `fds_record_find_by_key` | `components/libraries/fds/fds.c` |
| `0x0006400A` | `fds_record_find_in_file` | `components/libraries/fds/fds.c` |
| `0x0006401A` | `fds_record_id_from_desc` | `components/libraries/fds/fds.c` |
| `0x0006402C` | `fds_record_open` | `components/libraries/fds/fds.c` |
| `0x00064078` | `fds_record_update` | `components/libraries/fds/fds.c` |
| `0x00064088` | `fds_record_write` | `components/libraries/fds/fds.c` |
| `0x00064090` | `fds_register` | `components/libraries/fds/fds.c` |
| `0x000640C0` | `fds_stat` | `components/libraries/fds/fds.c` |
| `0x00064160` | `record_key_within_pm_range` | `components/ble/peer_manager/peer_data_storage.c` |
| `0x00064EEC` | `flag_id_init` | `components/ble/peer_manager/security_dispatcher.c` |
| `0x00064EFE` | `flag_id_init` | `components/ble/peer_manager/security_manager.c` |
| `0x00064F10` | `flag_toggle` | `components/ble/common/ble_conn_state.c` |
| `0x00064F44` | `flags_set_from_err_code` | `components/ble/peer_manager/security_manager.c` |
| `0x00065094` | `for_each_set_flag` | `components/ble/common/ble_conn_state.c` |
| `0x00066D24` | `gc_execute` | `components/libraries/fds/fds.c` |
| `0x00066E88` | `gc_state_advance` | `components/libraries/fds/fds.c` |
| `0x00066EF8` | `gc_swap_pages` | `components/libraries/fds/fds.c` |
| `0x00066F28` | `gcm_ble_evt_handler` | `components/ble/peer_manager/gatt_cache_manager.c` |
| `0x000672E0` | `gcm_im_evt_handler` | `components/ble/peer_manager/gatt_cache_manager.c` |
| `0x0006731C` | `gcm_init` | `components/ble/peer_manager/gatt_cache_manager.c` |
| `0x0006EEB4` | `gscm_local_db_cache_update` | `components/ble/peer_manager/gatts_cache_manager.c` |
| `0x0006FE60` | `header_check` | `components/libraries/fds/fds.c` |
| `0x0006FE8C` | `header_has_next` | `components/libraries/fds/fds.c` |
| `0x00070C1C` | `im_address_resolve` | `components/ble/peer_manager/id_manager.c` |
| `0x00070C64` | `im_ble_addr_get` | `components/ble/peer_manager/id_manager.c` |
| `0x00070C9C` | `im_ble_evt_handler` | `components/ble/peer_manager/id_manager.c` |
| `0x00070D78` | `im_conn_handle_get` | `components/ble/peer_manager/id_manager.c` |
| `0x00070DB8` | `im_find_duplicate_bonding_data` | `components/ble/peer_manager/id_manager.c` |
| `0x00070DF0` | `im_is_duplicate_bonding_data` | `components/ble/peer_manager/id_manager.c` |
| `0x00070E62` | `im_master_id_is_valid` | `components/ble/peer_manager/id_manager.c` |
| `0x00070E7A` | `im_master_ids_compare` | `components/ble/peer_manager/id_manager.c` |
| `0x00070EA4` | `im_new_peer_id` | `components/ble/peer_manager/id_manager.c` |
| `0x00070EB8` | `im_peer_free` | `components/ble/peer_manager/id_manager.c` |
| `0x00070EE4` | `im_peer_id_get_by_conn_handle` | `components/ble/peer_manager/id_manager.c` |
| `0x00070F08` | `im_peer_id_get_by_master_id` | `components/ble/peer_manager/id_manager.c` |
| `0x000710A0` | `init` | `components/libraries/fstorage/nrf_fstorage_sd.c` |
| `0x000720F0` | `init_execute` | `components/libraries/fds/fds.c` |
| `0x00072848` | `invalid_packets_omit` | `components/libraries/log/src/nrf_log_frontend.c` |
| `0x00072B70` | `is_busy` | `components/libraries/fstorage/nrf_fstorage_sd.c` |
| `0x00072BBE` | `is_word_aligned` | `components/libraries/util/app_util.h` |
| `0x00072BAA` | `is_valid_irk` | `components/ble/peer_manager/id_manager.c` |
| `0x00074F20` | `link_init` | `components/ble/nrf_ble_gatt/nrf_ble_gatt.c` |
| `0x00074F38` | `link_secure` | `components/ble/peer_manager/security_manager.c` |
| `0x00075038` | `link_secure_failure` | `components/ble/peer_manager/security_dispatcher.c` |
| `0x00075074` | `link_secure_pending_handle` | `components/ble/peer_manager/security_manager.c` |
| `0x00075B20` | `local_db_update_in_evt` | `components/ble/peer_manager/gatt_cache_manager.c` |
| `0x00075CE4` | `log_skip` | `components/libraries/log/src/nrf_log_frontend.c` |
| `0x00076088` | `manuf_specific_data_encode` | `components/ble/common/ble_advdata.c` |
| `0x00076178` | `memobj_op` | `components/libraries/memobj/nrf_memobj.c` |
| `0x000765DC` | `mutex_lock_status_get` | `components/ble/peer_manager/pm_buffer.c` |
| `0x000770BC` | `name_encode` | `components/ble/common/ble_advdata.c` |
| `0x0007719C` | `new_context_get` | `components/ble/peer_manager/security_manager.c` |
| `0x000771B0` | `new_evt` | `components/ble/peer_manager/security_manager.c` |
| `0x000771E2` | `next_id_get` | `components/ble/peer_manager/peer_id.c` |
| `0x00077F30` | `nrf_atfifo_clear` | `components/libraries/atomic_fifo/nrf_atfifo.c` |
| `0x00077F40` | `nrf_atfifo_init` | `components/libraries/atomic_fifo/nrf_atfifo.c` |
| `0x00077F66` | `nrf_atfifo_item_alloc` | `components/libraries/atomic_fifo/nrf_atfifo.c` |
| `0x00077F7C` | `nrf_atfifo_item_free` | `components/libraries/atomic_fifo/nrf_atfifo.c` |
| `0x00077F92` | `nrf_atfifo_item_get` | `components/libraries/atomic_fifo/nrf_atfifo.c` |
| `0x00077FA8` | `nrf_atfifo_item_put` | `components/libraries/atomic_fifo/nrf_atfifo.c` |
| `0x00077FBE` | `nrf_atflags_clear` | `components/libraries/atomic_flags/nrf_atflags.c` |
| `0x00077FD4` | `nrf_atflags_fetch_set` | `components/libraries/atomic_flags/nrf_atflags.c` |
| `0x00077FF4` | `nrf_atflags_find_and_set_flag` | `components/libraries/atomic_flags/nrf_atflags.c` |
| `0x0007803E` | `nrf_atflags_get` | `components/libraries/atomic_flags/nrf_atflags.c` |
| `0x00078054` | `nrf_atflags_set` | `components/libraries/atomic_flags/nrf_atflags.c` |
| `0x00078068` | `nrf_atomic_flag_clear_fetch` | `components/libraries/atomic/nrf_atomic.c` |
| `0x0007806E` | `nrf_atomic_flag_set` | `components/libraries/atomic/nrf_atomic.c` |
| `0x00078074` | `nrf_atomic_flag_set_fetch` | `components/libraries/atomic/nrf_atomic.c` |
| `0x0007807A` | `nrf_atomic_u32_add` | `components/libraries/atomic/nrf_atomic.c` |
| `0x00078086` | `nrf_atomic_u32_and` | `components/libraries/atomic/nrf_atomic.c` |
| `0x00078092` | `nrf_atomic_u32_fetch_add` | `components/libraries/atomic/nrf_atomic.c` |
| `0x000780A6` | `nrf_atomic_u32_fetch_or` | `components/libraries/atomic/nrf_atomic.c` |
| `0x000780B0` | `nrf_atomic_u32_fetch_store` | `components/libraries/atomic/nrf_atomic.c` |
| `0x000780C6` | `nrf_atomic_u32_sub` | `components/libraries/atomic/nrf_atomic.c` |
| `0x000780D2` | `nrf_balloc_alloc` | `components/libraries/balloc/nrf_balloc.c` |
| `0x00078116` | `nrf_balloc_free` | `components/libraries/balloc/nrf_balloc.c` |
| `0x00078146` | `nrf_balloc_init` | `components/libraries/balloc/nrf_balloc.c` |
| `0x00078186` | `nrf_ble_gatt_init` | `components/ble/nrf_ble_gatt/nrf_ble_gatt.c` |
| `0x000781B4` | `nrf_ble_gatt_on_ble_evt` | `components/ble/nrf_ble_gatt/nrf_ble_gatt.c` |
| `0x000783B6` | `nrf_ble_qwr_init` | `components/ble/nrf_ble_qwr/nrf_ble_qwr.c` |
| `0x000783DA` | `nrf_ble_qwr_on_ble_evt` | `components/ble/nrf_ble_qwr/nrf_ble_qwr.c` |
| `0x00078590` | `nrf_dfu_svci_vector_table_set` | `components/libraries/bootloader/dfu/nrf_dfu_svci.c` |
| `0x00078C4C` | `nrf_fstorage_erase` | `components/libraries/fstorage/nrf_fstorage.c` |
| `0x00078C78` | `nrf_fstorage_init` | `components/libraries/fstorage/nrf_fstorage.c` |
| `0x00078C80` | `nrf_fstorage_is_busy` | `components/libraries/fstorage/nrf_fstorage.c` |
| `0x00078CD0` | `nrf_fstorage_sdh_req_handler` | `components/libraries/fstorage/nrf_fstorage_sd.c` |
| `0x00078CE8` | `nrf_fstorage_sdh_state_handler` | `components/libraries/fstorage/nrf_fstorage_sd.c` |
| `0x00078D08` | `nrf_fstorage_sys_evt_handler` | `components/libraries/fstorage/nrf_fstorage_sd.c` |
| `0x00078DAC` | `nrf_fstorage_write` | `components/libraries/fstorage/nrf_fstorage.c` |
| `0x00078A40` | `nrf_fprintf` | `external/fprintf/nrf_fprintf.c` |
| `0x00078A5A` | `nrf_fprintf_buffer_flush` | `external/fprintf/nrf_fprintf.c` |
| `0x00079520` | `nrf_log_backend_add` | `components/libraries/log/src/nrf_log_frontend.c` |
| `0x00079576` | `nrf_log_backend_rtt_init` | `components/libraries/log/src/nrf_log_backend_rtt.c` |
| `0x00079598` | `nrf_log_backend_serial_put` | `components/libraries/log/src/nrf_log_backend_serial.c` |
| `0x0007965C` | `nrf_log_color_id_get` | `components/libraries/log/src/nrf_log_str_formatter.c` |
| `0x0007968C` | `nrf_log_default_backends_init` | `components/libraries/log/src/nrf_log_default_backends.c` |
| `0x000796A8` | `nrf_log_frontend_dequeue` | `components/libraries/log/src/nrf_log_frontend.c` |
| `0x00079918` | `nrf_log_frontend_hexdump` | `components/libraries/log/src/nrf_log_frontend.c` |
| `0x000799C0` | `nrf_log_frontend_std_0` | `components/libraries/log/src/nrf_log_frontend.c` |
| `0x000799C8` | `nrf_log_frontend_std_1` | `components/libraries/log/src/nrf_log_frontend.c` |
| `0x000799D6` | `nrf_log_frontend_std_2` | `components/libraries/log/src/nrf_log_frontend.c` |
| `0x000799E6` | `nrf_log_frontend_std_3` | `components/libraries/log/src/nrf_log_frontend.c` |
| `0x000799F8` | `nrf_log_frontend_std_4` | `components/libraries/log/src/nrf_log_frontend.c` |
| `0x00079A0C` | `nrf_log_frontend_std_5` | `components/libraries/log/src/nrf_log_frontend.c` |
| `0x00079A28` | `nrf_log_frontend_std_6` | `components/libraries/log/src/nrf_log_frontend.c` |
| `0x00079A44` | `nrf_log_hexdump_entry_process` | `components/libraries/log/src/nrf_log_str_formatter.c` |
| `0x00079AF4` | `nrf_log_init` | `components/libraries/log/src/nrf_log_frontend.c` |
| `0x00079B1C` | `nrf_log_panic` | `components/libraries/log/src/nrf_log_frontend.c` |
| `0x00079B48` | `nrf_log_std_entry_process` | `components/libraries/log/src/nrf_log_str_formatter.c` |
| `0x00079BFE` | `nrf_memobj_alloc` | `components/libraries/memobj/nrf_memobj.c` |
| `0x00079C5E` | `nrf_memobj_free` | `components/libraries/memobj/nrf_memobj.c` |
| `0x00079C90` | `nrf_memobj_get` | `components/libraries/memobj/nrf_memobj.c` |
| `0x00079C98` | `nrf_memobj_pool_init` | `components/libraries/memobj/nrf_memobj.c` |
| `0x00079C9C` | `nrf_memobj_put` | `components/libraries/memobj/nrf_memobj.c` |
| `0x00079CBA` | `nrf_memobj_read` | `components/libraries/memobj/nrf_memobj.c` |
| `0x00079CCA` | `nrf_memobj_write` | `components/libraries/memobj/nrf_memobj.c` |
| `0x00079DCC` | `nrf_ringbuf_init` | `components/libraries/ringbuf/nrf_ringbuf.c` |
| `0x00079E58` | `nrf_sdh_ble_app_ram_start_get` | `components/softdevice/common/nrf_sdh_ble.c` |
| `0x00079E6C` | `nrf_sdh_ble_default_cfg_set` | `components/softdevice/common/nrf_sdh_ble.c` |
| `0x0007A0EC` | `nrf_sdh_ble_enable` | `components/softdevice/common/nrf_sdh_ble.c` |
| `0x0007A38C` | `nrf_sdh_ble_evts_poll` | `components/softdevice/common/nrf_sdh_ble.c` |
| `0x0007A3EC` | `nrf_sdh_disable_request` | `components/softdevice/common/nrf_sdh.c` |
| `0x0007A440` | `nrf_sdh_enable_request` | `components/softdevice/common/nrf_sdh.c` |
| `0x0007A4B4` | `nrf_sdh_evts_poll` | `components/softdevice/common/nrf_sdh.c` |
| `0x0007A4D8` | `nrf_sdh_is_enabled` | `components/softdevice/common/nrf_sdh.c` |
| `0x0007A4E4` | `nrf_sdh_request_continue` | `components/softdevice/common/nrf_sdh.c` |
| `0x0007A500` | `nrf_sdh_soc_evts_poll` | `components/softdevice/common/nrf_sdh_soc.c` |
| `0x0007A53C` | `nrf_section_iter_init` | `components/libraries/experimental_section_vars/nrf_section_iter.c` |
| `0x0007A56A` | `nrf_section_iter_next` | `components/libraries/experimental_section_vars/nrf_section_iter.c` |
| `0x0007A594` | `nrf_strerror_find` | `components/libraries/strerror/nrf_strerror.c` |
| `0x0007A5CC` | `nrf_strerror_get` | `components/libraries/strerror/nrf_strerror.c` |
| `0x0007CE34` | `on_exchange_mtu_request_evt` | `components/ble/nrf_ble_gatt/nrf_ble_gatt.c` |
| `0x0007E0D4` | `page_identify` | `components/libraries/fds/fds.c` |
| `0x0007E0F8` | `page_offsets_update` | `components/libraries/fds/fds.c` |
| `0x0007E114` | `page_scan` | `components/libraries/fds/fds.c` |
| `0x0007E180` | `page_tag_write_data` | `components/libraries/fds/fds.c` |
| `0x0007E19C` | `page_tag_write_swap` | `components/libraries/fds/fds.c` |
| `0x0007E1C0` | `pages_init` | `components/libraries/fds/fds.c` |
| `0x0007E2F0` | `pairing` | `components/ble/peer_manager/security_dispatcher.c` |
| `0x0007E3A4` | `pairing_success_evt_send` | `components/ble/peer_manager/security_dispatcher.c` |
| `0x0007E3D8` | `params_req_send` | `components/ble/peer_manager/security_manager.c` |
| `0x0007E3F8` | `pdb_evt_send` | `components/ble/peer_manager/peer_database.c` |
| `0x0007E414` | `pdb_init` | `components/ble/peer_manager/peer_database.c` |
| `0x0007E574` | `pdb_peer_data_ptr_get` | `components/ble/peer_manager/peer_database.c` |
| `0x0007E57C` | `pdb_peer_free` | `components/ble/peer_manager/peer_database.c` |
| `0x0007E678` | `pdb_write_buf_get` | `components/ble/peer_manager/peer_database.c` |
| `0x0007E77C` | `pdb_write_buf_release` | `components/ble/peer_manager/peer_database.c` |
| `0x0007E790` | `pdb_write_buf_store` | `components/ble/peer_manager/peer_database.c` |
| `0x0007E7C8` | `pds_evt_send` | `components/ble/peer_manager/peer_data_storage.c` |
| `0x0007E7D8` | `pds_init` | `components/ble/peer_manager/peer_data_storage.c` |
| `0x0007E90C` | `pds_next_deleted_peer_id_get` | `components/ble/peer_manager/peer_data_storage.c` |
| `0x0007E910` | `pds_next_peer_id_get` | `components/ble/peer_manager/peer_data_storage.c` |
| `0x0007E914` | `pds_peer_data_iterate` | `components/ble/peer_manager/peer_data_storage.c` |
| `0x0007E96C` | `pds_peer_data_iterate_prepare` | `components/ble/peer_manager/peer_data_storage.c` |
| `0x0007E97C` | `pds_peer_data_read` | `components/ble/peer_manager/peer_data_storage.c` |
| `0x0007E9F0` | `pds_peer_data_store` | `components/ble/peer_manager/peer_data_storage.c` |
| `0x0007EAD4` | `pds_peer_id_allocate` | `components/ble/peer_manager/peer_data_storage.c` |
| `0x0007EADC` | `pds_peer_id_free` | `components/ble/peer_manager/peer_data_storage.c` |
| `0x0007EAF2` | `pds_peer_id_is_allocated` | `components/ble/peer_manager/peer_data_storage.c` |
| `0x0007EB30` | `peer_data_delete_process` | `components/ble/peer_manager/peer_data_storage.c` |
| `0x0007EC04` | `peer_data_find` | `components/ble/peer_manager/peer_data_storage.c` |
| `0x0007EC34` | `peer_data_id_is_valid` | `components/ble/peer_manager/peer_data_storage.c` |
| `0x0007EC58` | `peer_data_point_to_buffer` | `components/ble/peer_manager/peer_database.c` |
| `0x0007EC74` | `peer_id_allocate` | `components/ble/peer_manager/peer_id.c` |
| `0x0007EC80` | `peer_id_delete` | `components/ble/peer_manager/peer_id.c` |
| `0x0007ECA4` | `peer_id_free` | `components/ble/peer_manager/peer_id.c` |
| `0x0007ECC0` | `peer_id_get_next_deleted` | `components/ble/peer_manager/peer_id.c` |
| `0x0007ECCC` | `peer_id_get_next_used` | `components/ble/peer_manager/peer_id.c` |
| `0x0007ECFC` | `peer_id_init` | `components/ble/peer_manager/peer_id.c` |
| `0x0007ED08` | `peer_id_is_allocated` | `components/ble/peer_manager/peer_id.c` |
| `0x0007ED1C` | `peer_id_is_deleted` | `components/ble/peer_manager/peer_id.c` |
| `0x0007F194` | `pm_buffer_block_acquire` | `components/ble/peer_manager/pm_buffer.c` |
| `0x0007F1F8` | `pm_buffer_init` | `components/ble/peer_manager/pm_buffer.c` |
| `0x0007F21C` | `pm_buffer_ptr_get` | `components/ble/peer_manager/pm_buffer.c` |
| `0x0007F244` | `pm_buffer_release` | `components/ble/peer_manager/pm_buffer.c` |
| `0x0007F276` | `pm_conn_sec_config_reply` | `components/ble/peer_manager/peer_manager.c` |
| `0x0007F280` | `pm_conn_sec_status_get` | `components/ble/peer_manager/peer_manager.c` |
| `0x0007F294` | `pm_conn_secure` | `components/ble/peer_manager/peer_manager.c` |
| `0x0007FA5C` | `pm_handler_flash_clean` | `components/ble/peer_manager/peer_manager_handler.c` |
| `0x0007FDE4` | `pm_handler_on_pm_evt` | `components/ble/peer_manager/peer_manager_handler.c` |
| `0x0007FE74` | `pm_handler_pm_evt_log` | `components/ble/peer_manager/peer_manager_handler.c` |
| `0x0008056C` | `pm_im_evt_handler` | `components/ble/peer_manager/peer_manager.c` |
| `0x00080570` | `pm_init` | `components/ble/peer_manager/peer_manager.c` |
| `0x00080980` | `pm_pdb_evt_handler` | `components/ble/peer_manager/peer_manager.c` |
| `0x00080A98` | `pm_peer_data_bonding_load` | `components/ble/peer_manager/peer_manager.c` |
| `0x00080AAC` | `pm_peer_data_load` | `components/ble/peer_manager/peer_manager.c` |
| `0x00080AD4` | `pm_peer_delete` | `components/ble/peer_manager/peer_manager.c` |
| `0x00080AE8` | `pm_peer_rank_highest` | `components/ble/peer_manager/peer_manager.c` |
| `0x00080C38` | `pm_peer_ranks_get` | `components/ble/peer_manager/peer_manager.c` |
| `0x00080D5C` | `pm_peers_delete` | `components/ble/peer_manager/peer_manager.c` |
| `0x00080E28` | `pm_register` | `components/ble/peer_manager/peer_manager.c` |
| `0x00080E54` | `pm_sec_params_set` | `components/ble/peer_manager/peer_manager.c` |
| `0x00080E68` | `pm_sm_evt_handler` | `components/ble/peer_manager/peer_manager.c` |
| `0x000813E0` | `postfix_process` | `components/libraries/log/src/nrf_log_str_formatter.c` |
| `0x0008743C` | `queue_buf_get` | `components/libraries/fds/fds.c` |
| `0x00087458` | `queue_buf_store` | `components/libraries/fds/fds.c` |
| `0x00087468` | `queue_free` | `components/libraries/fstorage/nrf_fstorage_sd.c` |
| `0x0008747C` | `queue_process` | `components/libraries/fds/fds.c` |
| `0x00087520` | `queue_process` | `components/libraries/fstorage/nrf_fstorage_sd.c` |
| `0x000875C0` | `queue_start` | `components/libraries/fds/fds.c` |
| `0x000875DC` | `queue_start` | `components/libraries/fstorage/nrf_fstorage_sd.c` |
| `0x00087A94` | `ram_end_address_get` | `components/softdevice/common/nrf_sdh_ble.c` |
| `0x00087AAC` | `rank_highest` | `components/ble/peer_manager/peer_manager_handler.c` |
| `0x00087AC8` | `rank_vars_update` | `components/ble/peer_manager/peer_manager.c` |
| `0x00087B20` | `read` | `components/libraries/fstorage/nrf_fstorage_sd.c` |
| `0x00087F20` | `record_find` | `components/libraries/fds/fds.c` |
| `0x00087FB0` | `record_find_by_desc` | `components/libraries/fds/fds.c` |
| `0x00088050` | `record_find_next` | `components/libraries/fds/fds.c` |
| `0x000880AC` | `record_header_flag_dirty` | `components/libraries/fds/fds.c` |
| `0x000880E8` | `records_stat` | `components/libraries/fds/fds.c` |
| `0x000881E4` | `release` | `components/ble/peer_manager/peer_id.c` |
| `0x000883F8` | `rmap` | `components/libraries/fstorage/nrf_fstorage_sd.c` |
| `0x000890CC` | `sc_send_pending_handle` | `components/ble/peer_manager/gatt_cache_manager.c` |
| `0x00089148` | `sdh_request_observer_notify` | `components/softdevice/common/nrf_sdh.c` |
| `0x00089178` | `sdh_state_observer_notify` | `components/softdevice/common/nrf_sdh.c` |
| `0x000891B8` | `sec_info_request_process` | `components/ble/peer_manager/security_dispatcher.c` |
| `0x000892F4` | `sec_keyset_fill` | `components/ble/peer_manager/security_dispatcher.c` |
| `0x000894C0` | `sec_params_verify` | `components/ble/peer_manager/security_manager.c` |
| `0x00089538` | `sec_proc_start` | `components/ble/peer_manager/security_dispatcher.c` |
| `0x00089598` | `sec_req_process` | `components/ble/peer_manager/security_manager.c` |
| `0x0008965A` | `send_config_req` | `components/ble/peer_manager/security_dispatcher.c` |
| `0x000896A0` | `send_unexpected_error` | `components/ble/peer_manager/gatt_cache_manager.c` |
| `0x000896C8` | `send_unexpected_error` | `components/ble/peer_manager/security_dispatcher.c` |
| `0x00090308` | `sm_ble_evt_handler` | `components/ble/peer_manager/security_manager.c` |
| `0x00090334` | `smd_conn_sec_config_reply` | `components/ble/peer_manager/security_dispatcher.c` |
| `0x00090338` | `sm_conn_sec_status_get` | `components/ble/peer_manager/security_manager.c` |
| `0x000903DC` | `sm_init` | `components/ble/peer_manager/security_manager.c` |
| `0x0009045C` | `sm_link_secure` | `components/ble/peer_manager/security_manager.c` |
| `0x00090468` | `sm_pdb_evt_handler` | `components/ble/peer_manager/security_manager.c` |
| `0x000904AC` | `sm_sec_is_sufficient` | `components/ble/peer_manager/security_manager.c` |
| `0x000904D4` | `sm_sec_params_set` | `components/ble/peer_manager/security_manager.c` |
| `0x00090534` | `smd_ble_evt_handler` | `components/ble/peer_manager/security_dispatcher.c` |
| `0x00090638` | `smd_init` | `components/ble/peer_manager/security_dispatcher.c` |
| `0x000906C8` | `smd_link_secure` | `components/ble/peer_manager/security_dispatcher.c` |
| `0x000906F0` | `smd_params_reply` | `components/ble/peer_manager/security_dispatcher.c` |
| `0x00090FEC` | `std_n` | `components/libraries/log/src/nrf_log_frontend.c` |
| `0x0008A928` | `service_changed_pending_flags_check` | `components/ble/peer_manager/gatt_cache_manager.c` |
| `0x0008ABA0` | `service_data_encode` | `components/ble/common/ble_advdata.c` |
| `0x0008EE0A` | `set_security_req` | `components/ble/common/ble_srv_common.c` |
| `0x00093EA2` | `uint16_encode` | `components/libraries/util/app_util.h` |
| `0x00093EC4` | `uninit` | `components/libraries/fstorage/nrf_fstorage_sd.c` |
| `0x00094E30` | `user_flag_is_acquired` | `components/ble/common/ble_conn_state.c` |
| `0x00095114` | `user_mem_reply` | `components/ble/nrf_ble_qwr/nrf_ble_qwr.c` |
| `0x00095540` | `uuid_list_encode` | `components/ble/common/ble_advdata.c` |
| `0x00095570` | `uuid_list_sized_encode` | `components/ble/common/ble_advdata.c` |
| `0x00096E08` | `wmap` | `components/libraries/fstorage/nrf_fstorage_sd.c` |
| `0x00096FE0` | `write` | `components/libraries/fstorage/nrf_fstorage_sd.c` |
| `0x00097030` | `write_buf_store` | `components/ble/peer_manager/peer_database.c` |
| `0x00097214` | `write_buf_store_in_event` | `components/ble/peer_manager/peer_database.c` |
| `0x000972B4` | `write_buffer_record_find` | `components/ble/peer_manager/peer_database.c` |
| `0x000972E8` | `write_buffer_record_find_next` | `components/ble/peer_manager/peer_database.c` |
| `0x00097318` | `write_buffer_record_invalidate` | `components/ble/peer_manager/peer_database.c` |
| `0x00097334` | `write_buffer_record_release` | `components/ble/peer_manager/peer_database.c` |
| `0x00097360` | `write_enqueue` | `components/libraries/fds/fds.c` |
| `0x00097454` | `write_execute` | `components/libraries/fds/fds.c` |
| `0x000975C4` | `write_space_free` | `components/libraries/fds/fds.c` |
| `0x000975DC` | `write_space_reserve` | `components/libraries/fds/fds.c` |

## Revision and variant discriminators

- `0x000272B8` through `0x00027461` reproduce the SDK's `__CC_ARM` inline assembly instruction
  sequences for atomic FIFO position tags and atomic `mov/orr/and/eor/add/sub/compare-exchange`
  operations, including the exclusive-monitor retry loops and output-register conventions.
- `0x00027488` is the SDK startup's exact `SystemInit` then `__main` load/branch sequence;
  `0x0002749C` and `0x000274A2` are its retained NMI and shared weak-default infinite loops.
- `0x00038166` is the CMSIS Cortex-M4 non-negative IRQ guard and indexed `NVIC->ICPR` write.
  `0x00038180` and `0x000381C8` are two retained copies of the CMSIS system-reset helper: DSB,
  AIRCR priority-group preservation plus `VECTKEY`/`SYSRESETREQ`, DSB, then the wait loop.
- `0x00077F30` through `0x000780D1` reproduce the corresponding public FIFO, flag-array, and
  atomic wrappers, including the SDK's old-value/new-value selection and tail-call aliases. Ghidra
  overstates some overlapping ends in this compact wrapper block; only entries are asserted.
- `0x00097030`, `0x00097214`, `0x000972B4`, `0x000972E8`, `0x00097318`, and `0x00097334`
  reproduce Peer Database write-buffer storage, event conversion, record lookup, invalidation, and
  release control flow. Each complete body is pinned independently by its recovered length and
  SHA-256 digest; adjacent Peer Manager, FDS, and product functions are not included by range.
- `0x000783B6`, `0x000783DA`, and `0x00095114` reproduce the SDK Queued Write module with
  `NRF_BLE_QWR_MAX_ATTR == 0`: initializer magic `0xDE`, invalid connection handle `0xFFFF`,
  user-memory request/release handling, queued-write authorization for prepare/execute/cancel, and
  the `NRF_ERROR_BUSY` retry flag. Their complete bodies are length/SHA-pinned.
- `0x00052018` performs vector-table set, SVCI function `3`, then vector-table unset. Nordic's
  `NRF_DFU_SVCI_SET_ADV_NAME` is function `3`, selecting the SDK's unbonded buttonless-DFU path
  rather than the similarly named bonded implementation.
- `0x0004826C`, `0x00051440`, `0x0005380C`, `0x00059BA0`, and `0x00051E04` through `0x00051FA4`,
  together with helpers at `0x00064F10`, `0x00065094`, and `0x00094E30`, reproduce the SDK 17.1.0
  connection-state module.
  The recovered 124-byte state has the exact `acquired`, `valid`, `connected`, `central`,
  `encrypted`, `mitm_protected`, `lesc`, and 24-user-flag ordering. Literal targets at
  `0x2002BDB0` through `0x2002BDC8` disambiguate accessors that otherwise share the same body.
- `0x000514E0` preserves every `blcm_link_ctx_get` validation and error code, including 4-byte
  context alignment, the 20-connection invalid index, max-link bounds, and indexed pool address.
  `0x000539A8` and `0x000539B0` are the SDK's indication/notification CCCD-bit helpers.
- `0x00078590` reads the MBR/UICR bootloader address, handles `0xFFFFFFFF`, invokes the SoftDevice
  vector-table SVC, and retains Nordic's “No bootloader was found” and vector-table diagnostics.
- `0x000796A8` reproduces the logger's circular-header handling, memobj allocation, backend fanout,
  overflow-safe read-index update, backend flush loop, and “Backends flushed” terminal path.
- The surrounding logging cluster preserves the exact standard-argument wrappers, hex-dump header,
  packet omission, overflow skip, saturated drop counter, backend registration/panic handling, and
  compile-time-disabled branches. Its memobj chain matches Nordic's chunk header, reference count,
  bounded cross-chunk copy, balloc stack, and ring-buffer initialization layouts.
- `0x0007A0EC` preserves the `sd_ble_enable` RAM-start comparison and all three RAM-sizing
  diagnostics, including the application maximum derived from the nRF52840 RAM end.
- `0x00079E58` and `0x00079E6C` are the stock BLE RAM-start accessor and default SoftDevice
  configuration body. The recovered three-link count, role split, ATT MTU, UUID count, attribute
  table, and service-changed values are compile-time `sdk_config` inputs, not locally recreated
  vendor logic. `0x0007A38C` completes this provider path with the byte-exact BLE event poller:
  enabled guard, 500-byte aligned event buffer, `sd_ble_evt_get` SVC `0x61`, terminal error `5`,
  and BLE observer-section dispatch.
- The `nrf_sdh` state-machine block preserves the SDK's enabled/suspended/continue byte layout,
  enable/disable request ordering, request-observer busy result `0x11`, state events `0...3`,
  SoftDevice SVC enable/disable calls, IRQ transition, and observer-section iteration. The direct
  `nrf_fstorage_sd` call to `nrf_sdh_request_continue` links this block to the recovered pause
  protocol. `0x0007A3EC`, `0x0007A4E4`, and `0x0007A500` are raw instruction entries missed by
  Ghidra and are admitted as manual supplements. The last includes the exact `sd_evt_get` SVC
  `0x4B`, `NRF_ERROR_NOT_FOUND` terminal result `5`, and SoC-observer iterator. The verifier pins
  their bytes along with the seven surrounding retained functions.
- The adjacent `nrf_strerror_find`/`get` pair is Nordic's ordered 37-entry error table lookup and
  `"Unknown error code"` fallback used by the SoftDevice configuration diagnostics. It is linked
  from the SDK instead of being recreated locally.
- The Peer Manager entries preserve the exact initialization order
  `pds -> pdb -> sm -> smd -> gcm -> gscm`, storage-full cleanup/rank queue, PM event cases, GATT
  cache state transitions, and security-dispatch buffer behavior from SDK 17.1.0.
- The thirteen newly resolved Peer Manager bodies at `0x0007F276...0x00080E68` are each pinned by
  executable length and SHA-256. They cover the public connection-security wrappers, PDB event
  forwarding, peer-data load/delete APIs, peer rank scan/update, delete-all sequencing,
  registration, security-parameter dispatch, and the null-checked SM event forwarder. Ghidra gave
  `0x0007F276` a non-contiguous extent overlapping later code; its independently established body
  ends at the next entry, `0x0007F280`, and only those ten bytes are admitted.
- `0x00075038` is the Security Dispatcher `link_secure_failure` routine. The Arm linker emitted a
  54-byte entry chunk at `0x00075038...0x0007506D` and a 148-byte tail at
  `0x0007E2FC...0x0007E38F`; the verifier concatenates and SHA-pins exactly those 202 executable
  bytes. It does not attribute or hash the unrelated address interval between the chunks.
- `0x00059C68` is the complete 60-byte `conn_sec_failure` implementation recovered from a callable
  entry Ghidra omitted from its function inventory. `0x0005D314` is the ten-byte inlined
  `encryption_failure` veneer that fixes the procedure to encryption before tail-calling it;
  Ghidra's reported 70-byte extent overlaps the unrelated next function, so only the independently
  bounded veneer is hashed.
- `0x00090334` is the Security Dispatcher configuration-reply entry. Its four-byte veneer branches
  to a ten-byte tail at `0x00090628...0x00090631`; the verifier concatenates only those fourteen
  executable bytes and excludes the intervening Security Manager/Dispatcher code and tail literal.
- The FDS public block at `0x00063E30...0x000640C0` preserves the SDK's initialization and
  flash-bound selection, four-user callback limit, record open/close/find/write/update paths,
  operation queue codes, reservation rollback, garbage-collection resume flag, record IDs, and
  two-data-page statistics for the recovered three-virtual-page configuration. The compact
  `fds_record_update` veneer and adjacent `fds_record_write` share compiler blocks in Ghidra, so
  only their independently recovered entries are asserted. `0x00064160` is separately owned by
  Peer Data Storage: its `0xC000...0xFFFE` predicate is exactly
  `record_key_within_pm_range`, not an FDS core routine.
- The common fstorage wrappers and SoftDevice backend remain a separate Nordic layer. The admitted
  entries preserve bounds and word/page alignment, backend dispatch, the 28-byte atomic-FIFO
  operation layout, 4096-byte erase unit, 4-byte program unit, 4096-byte write chunking, SoftDevice
  flash SVCs, retry limit, pause/resume state, result events, and queue ownership. The FDS and
  fstorage functions named `event_send`, `queue_process`, and `queue_start` are distinct routines;
  their source paths are part of the identity. `0x00087468` is specifically the fstorage
  `queue_free`; FDS inlines its corresponding free operation.
- Stock `fds_init` at `0x00063EB8` subtracts `0x24000` before its own `0x3000` extent. This is the
  exact compiled form of `FDS_VIRTUAL_PAGES_RESERVED=36` with three FDS pages: FDS ends where the
  R1 `device_flash` region begins. The clean target uses the same Nordic source/configuration,
  limits application linking below the three FDS pages, and gives the 36-page region a separate
  `nrf_fstorage_sd` instance. Ten byte-pinned product adapters remain local geometry, bounds,
  synchronization, and FAL glue; see `INTERNAL-FLASH-CORRELATION.md`.
- The recovered `nrf_fstorage_sd` API table at `0x0009C86C` contains, in SDK structure order,
  Thumb pointers to `init`, `uninit`, `read`, `write`, `erase`, `rmap`, `wmap`, and `is_busy`.
  Five independently established entries anchor that table and resolve the four otherwise generic
  leaf bodies at `0x00072B70`, `0x00087B20`, `0x000883F8`, and `0x00096E08` without relying on a
  guessed name. The adjacent raw instruction entries `0x00078CD0` and `0x00078CE8` exactly set the
  recovered pause/state bytes and dispatch `queue_process`, proving the SDK request/state observer
  handlers. Ghidra omitted these six small entry points from `functions.csv`, so they remain
  explicit manual provenance supplements with no invented end address.
- The Peer Database/Data Storage block at `0x0007E3F8...0x0007ED1C`, with bitmap helpers at
  `0x00058218`, `0x000771E2`, and `0x000881E4`, preserves Nordic's four-buffer PDB allocator,
  FDS record read/write/update/iteration error mapping, seven accepted peer-data IDs, 256-peer
  used/deleted bitmaps, deferred deletion, and next-used/next-deleted traversal. Provider source
  therefore owns persistence and peer-ID state; local code supplies only R1 policy at its callers.
- The PM buffer bodies at `0x0007F194...0x0007F244` match Nordic's validity checks, `0xFF`
  invalid ID, contiguous atomic-flag acquisition, pointer arithmetic, and release behavior.
  Static `mutex_lock_status_get` at `0x000765DC` preserves the SDK's leading DMB before
  `nrf_atflags_get`; every complete body is byte-pinned.
- The resolved Peer Manager dispatcher chain at `0x00053924`, `0x0005EC88...0x0005ECC0`, `0x000672E0`,
  `0x0006731C`, `0x00070C64...0x00070EE4`, `0x0008056C`, and `0x00090308` preserves connection
  exclusion, event fanout, GATT-cache user flags, identity lookup, bonded-peer matching, and
  security-manager pending-procedure dispatch. The ID Manager callback table points directly to
  `0x0008056D`, disambiguating the otherwise one-tail-call `pm_im_evt_handler` body.
- The ID Manager group at `0x0004898C`, `0x00048CD0`, `0x00070C1C`,
  `0x00070DB8...0x00070F08`, and `0x00072BAA` matches the SDK's address comparison, reversed-key
  AES-ECB `ah` hash, resolvable-private-address check, duplicate bond selection, master-ID rules,
  peer free/update behavior, and all-zero IRK rejection. These cryptographic and storage semantics
  distinguish the provider code from ordinary application-side connection bookkeeping.
- The Security Manager/Dispatcher group at `0x0005ECEC`, `0x00064EEC`, `0x00064EFE`,
  `0x000894C0`, `0x00089538`, and `0x00090308...0x000906F0` preserves the SDK's event fanout,
  four user-flag initialization paths, connection
  security status bit packing, bonded/encrypted/MITM/LESC sufficiency test, retry dispatch after
  database events, security-parameter validation/store, and complete SoftDevice security-event
  switch. These routines remain compiled from Nordic source; no local security-state rewrite is
  admitted.

## GPIO HAL inline provider cluster

Fifty-six application entries in `0x00078DEA...0x00079510` are compiler-emitted instances of
Nordic `modules/nrfx/hal/nrf_gpio.h` or adjacent `nrf_gpiote.h` helpers, not independent product drivers. The same inline helper is
retained more than once because multiple translation units emitted their own out-of-line copy.
The source gate records every instance rather than collapsing distinct executable addresses:

| Helper | Recovered entries | Function-local discriminator |
| --- | ---: | --- |
| `nrf_gpio_cfg` | 9 | exact six-field `PIN_CNF` packing at offset `0x700`, including P0/P1 decode variants |
| `nrf_gpio_cfg_default` | 3 | input + disconnected + no-pull + S0S1 + no-sense constants |
| `nrf_gpio_cfg_input` | 5 | input + connected + caller pull + S0S1 + no-sense constants |
| `nrf_gpio_cfg_output` | 5 | output + disconnected + no-pull + S0S1 + no-sense constants |
| `nrf_gpio_cfg_sense_set` | 1 | clears mask `0x00030000`, then inserts the new sense field |
| `nrf_gpio_latches_read_and_clear` | 1 | reads each port `LATCH` at `0x520` and writes the same mask back |
| `nrf_gpio_pin_clear` | 3 | decoded pin bit written to `OUTCLR` at `0x50C` |
| `nrf_gpio_pin_port_decode` | 11 | byte-identical 22-byte P0/P1 split at pin 32 and `pin &= 0x1F` |
| `nrf_gpio_pin_read` | 6 | decoded pin bit read from `IN` at `0x510` |
| `nrf_gpio_pin_set` | 10 | decoded pin bit written to `OUTSET` at `0x508` |
| `nrf_gpiote_event_clear` | 1 | writes zero to `NRF_GPIOTE + event`, then performs the Cortex-M4 required dummy read |
| `nrf_gpiote_event_is_set` | 1 | exact `NRF_GPIOTE + event` load and equality test against one |

The verifier pins the byte-identical decoder copies and the register/bit-pack discriminators for
the other groups. Production code must include the SDK header; these generic HAL operations are
not clean-room R1 functions. Nearby entries without a complete header or nrfx-driver identity
remain unclassified.

The adjacent `0x00079CDC...0x00079E34` block adds 13 source-routed header helpers across NFCT,
PDM, PWM, RTC, and SAADC. All match the current headers exactly. The three first bodies use the
literal base `0x40005000` and are `nrf_nfct_event_check`, `nrf_nfct_event_clear`, and
`nrf_nfct_int_enable_check`; NFCT's current SDK event clear intentionally uses DSB. The remaining
event-check/event-clear shapes, two RTC copies, and SAADC `RESULT.PTR`/`MAXCNT` pair provide their
function-local identities. Only those leaf helpers are admitted; callers remain separately
classified or gated.

Four linked NFCT driver bodies now route to `modules/nrfx/drivers/src/nrfx_nfct.c`:

| Recovered entry | Nordic symbol | Function-local discriminator |
| --- | --- | --- |
| `0x0003060C` | `nrfx_nfct_irq_handler` | complete FIELDDETECTED/FIELDLOST, RX/TX frame, SELECTED, ERROR, and TXFRAMESTART event sequence with exact masks and callback payloads |
| `0x0007AC14` | `nrfx_nfct_field_check` | `FIELDPRESENT` at `0x4000543C` and combined PRESENT/LOCK mask test |
| `0x0007AC24` | `nrfx_nfct_field_event_handler` | exact field transition suppression, nRF52840 anomaly-190 timer start, SENSE/RX/TX interrupt disable, anomaly-218 frame-delay reset, and event IDs |
| `0x0007ACB8` | `nrfx_nfct_frame_delay_max_set` | exact default-versus-control-block delay selection and `FRAMEDELAYMAX` write at `0x40005508` |

The IRQ body is pinned by its 480-byte length and SHA-256; the three linked helpers are pinned byte
for byte. Product code owns only NFC application callbacks and tag behavior, not this driver path.

Four further exact leaf helpers at `0x0007A58A...0x0007A622` route to `nrf_timer.h`,
`nrf_spim.h`, and `nrf_twim.h`: `nrf_timer_event_clear`, one emitted `nrf_spim_event_check`, and
the `nrf_twim_event_check` / `nrf_twim_event_clear` pair used by the recovered TWIM0/TWIM1 IRQ
core. The TIMER caller iterates six compare events from register offset `0x140` with masks
`0x10000 << i`; the SPIM check is called with the SPIM2 base `0x40023000` and event offset
`0x118`. The type-neutral event-check and Cortex-M4 event-clear machine bodies are byte-identical
across the relevant pinned Nordic headers, so caller peripheral bases and the complete IRQ core
provide the header/symbol discriminator.
The surrounding TIMER and SPIM driver paths remain separately gated.

## Clock driver provider cluster

Fourteen linked functions now route to the Nordic clock and SoftDevice sources rather than a local
clock or interrupt-masking rewrite:

| Entry | Nordic symbol | Function-local discriminator |
| --- | --- | --- |
| `0x0003BC78` | `__sd_nvic_app_accessible_irq` | exact `<32`, `<64`, and system-exception branches with recovered S140 application IRQ mask `0xBDFF06FC` |
| `0x0004EBEC` / `0x0004EC34` | `sd_nvic_critical_region_enter` / `exit` | exact nested flag, S140 application IRQ mask preservation, NVIC bank 0/1 disable/restore, and prior PRIMASK preservation |
| `0x000584AC` | `clock_clk_started_notify` | exact HF/LF handler-list selection, dequeue loop, and per-item callback dispatch; recovered as a 32-byte static entry omitted by Ghidra |
| `0x000584D4` | `clock_irq_handler` | exact HF/LF state-byte update followed by tail dispatch to `clock_clk_started_notify`; recovered as a 24-byte callback entry omitted by Ghidra |
| `0x00072BCA` | `item_enqueue` | exact duplicate-suppressing singly linked handler-item insertion |
| `0x000788C8` | `nrf_drv_clock_init` | exact legacy control-block clearing, `nrfx_clock_init(clock_irq_handler)`, SoftDevice-enabled branch, watchdog-running propagation, and SDK log exit |
| `0x00078990` | `nrf_drv_clock_lfclk_request` | exact already-running callback, nested critical section, queued handler, zero-to-one LF start, and request count update |
| `0x00090814` / `0x00090854` | `softdevice_evt_irq_disable` / `softdevices_evt_irq_enable` | exact S140 `SD_EVT_IRQn` 22 accessibility/priority checks, nested mask update, direct NVIC path, and SDK `APP_ERROR_CHECK` results `0x2001`/`0x2002` |
| `0x0007A630` | `nrf_wdt_started` | direct `NRF_WDT->RUNSTATUS` boolean read at `0x40010400` |
| `0x0007A640` | `nrfx_clock_enable` | shared IRQ 0 enabled check, priority 6 setup, LF RC source write to `LFCLKSRC` |
| `0x0007A66C` | `nrfx_clock_init` | exact handler/initialized/HF-start/calibration-state control-block layout and `NRFX_ERROR_ALREADY_INITIALIZED` result |
| `0x0007A68C` | `nrfx_clock_lfclk_start` | LFCLKSTARTED clear, interrupt mask `2`, and LFCLKSTART task trigger |

The verifier pins every recovered body. These identities depend on their linked call sequence and
state/register layouts; they are not inferred from log strings alone. Other clock/power callers
remain gated until their complete upstream identity is established.

## Delay and legacy TWI recovery provider cluster

Six emitted `nrfx_coredep_delay_us` copies at `0x0007A6DC...0x0007A72C` multiply a nonzero
microsecond count by the recovered 64 MHz CPU frequency and branch to their translation-unit-local
Nordic aligned `SUBS #3; BHI; BX LR` delay loops. Four wrappers and all six literal targets were
omitted by Ghidra and are independently pinned in
[`NORDIC-OMITTED-DELAY-CLUSTER-CORRELATION.md`](NORDIC-OMITTED-DELAY-CLUSTER-CORRELATION.md).
The wrapper at `0x0002EB34`
is the SDK `nrf_delay_ms`: it invokes the microsecond helper with 1000 until the millisecond count
reaches zero.

Eight more byte-identical `nrf_delay_ms` copies survive at `0x000784B0`, `0x000784D0`,
`0x000784F0`, `0x00078510`, `0x00078530`, `0x00078550`, `0x00078570`, and `0x0007F15C`.
Each 28-byte body invokes its translation-unit-local delay array with the recovered 64,000 cycles
per millisecond. Ghidra also promoted 15 other aligned arrays into its function inventory:
`0x00099340`, `0x00099CB0`, `0x00099CC0`, `0x00099CD0`, `0x00099CE0`, `0x00099CF0`,
`0x00099D00`, `0x00099D10`, `0x0009A5F0`, `0x0009A610`, `0x0009A670`, `0x0009A6A0`,
`0x0009A710`, `0x0009BB10`, and `0x0009C9E0`. They are executable data emitted from
`nrfx_coredep_delay_us`, not separately authored application functions; all 21 six-byte
`03 38 FD D8 70 47` body is pinned explicitly.

The adjacent `0x00078490` and `0x0007849E` bodies are the SDK's `nrf_power_event_check` and
`nrf_power_event_clear` inlines. Their direct `NRF_POWER` base (`0x40000000`) access and the
Cortex-M4 read-back after clearing distinguish them from the similar CLOCK helpers.

`0x000938BC` is the complete static `integration/nrfx/legacy/nrf_drv_twi.c::twi_clear_bus`
implementation. Its argument is the legacy configuration pointer: the body loads `scl` and `sda`
from the first two words, sets and configures them as S0D1 pull-up outputs, delays 4 microseconds,
pulses SCL at most nine times while SDA is low, then generates the recovered SDA STOP sequence.
This call signature and its caller distinguish it from the newer two-pin
`nrfx_twi_twim_bus_recover` API. Its full body and both aligned delay targets are pinned by the
verifier; application code must compile the legacy Nordic provider rather than reproduce the
bus-recovery algorithm.

The same legacy/TWIM path yields six further exact source-routed entries:

| Recovered entry | Nordic symbol | Pinned source / discriminator |
| --- | --- | --- |
| `0x000789E4` | `nrf_drv_twi_init` | `integration/nrfx/legacy/nrf_drv_twi.c`; exact handler/context stores, `clear_bus_init` gate, static recovery call, handler adapter selection, and tail call into `nrfx_twim_init` |
| `0x00078A24` / `0x00078A32` | `nrf_drv_twi_tx` | two emitted `nrf_drv_twi.h` inline wrappers; preserve the fifth `no_stop` argument, advance to the embedded TWIM instance, and call `nrfx_twim_tx` |
| `0x0007B22C` | `nrfx_twim_disable` | `nrfx_twim.c`; clears control-block interrupt mask, all TWIM interrupts/shorts, peripheral enable, and returns state to initialized |
| `0x0007B268` | `nrfx_twim_enable` | `nrfx_twim.c`; writes TWIM enable value six and changes state to powered-on |
| `0x0007B370` | `nrfx_twim_rx` | exact RX descriptor construction and zero-flag `nrfx_twim_xfer` call |
| `0x0007B3A0` | `nrfx_twim_tx` | exact TX descriptor construction and conditional `NRFX_TWIM_FLAG_TX_NO_STOP` |
| `0x0007B3D8` | `nrfx_twim_uninit` | exact conditional IRQ disable, TWIM disable, PRS release, optional SCL/SDA GPIO reset, and uninitialized state |
| `0x0007AC04` | `nrfx_is_in_ram` | `nrfx_common.h`; exact nRF52 SRAM-region test `(address >> 29) == 1` used by EasyDMA transfer validation |
| `0x0007ACD4` / `0x0007AD0E` | `nrfx_prs_acquire` / `nrfx_prs_release` | exact PRS lookup, SoftDevice-aware critical section, busy result, handler/acquired writes, and release clears |
| `0x00084CD8` | `prs_box_get` | exact enabled single-box address comparison and box/null return from `nrfx_prs.c` |

The compiler tail-merges `nrf_drv_twi_init` with the `nrfx_twim_init` entry at `0x0007B28C`.
Ghidra therefore records a discontiguous range under the legacy wrapper. The verifier pins the
56-byte wrapper entry block and the 218-byte shared TWIM-init block separately; it does not hash a
false contiguous span.

## TWIM interrupt provider

The recovered entries at `0x00031A74` and `0x00031A84` are Nordic's public
`nrfx_twim_0_irq_handler` and `nrfx_twim_1_irq_handler`. The first is an 8-byte veneer loading the
TWIM0 control block and nRF52840 base `0x40003000`; its body SHA-256 is
`f01a62125b504ea5bcb65497586eaea05b19d858fee9019e93014d72a84a1d8f`. The second is a 10-byte
veneer loading the TWIM1 control block and base `0x40004000`, then tail-calling the 400-byte static
`nrfx_twim.c::twim_irq_handler` at `0x000939A0`. Ghidra assigns that shared core only to the TWIM1
entry and therefore reports a non-contiguous 410-byte body ending at `0x00093B2F`; its four-byte
literal at `0x00031A90` is data and is excluded.

The shared core handles ERROR, STOPPED, and SUSPENDED events; maintains transfer descriptors,
interrupt masks, busy/error/repeated flags, and EasyDMA completeness; performs the enabled Nordic
anomaly-109 path; clears the pending shared-peripheral IRQ through CMSIS; and calls the registered
`(event, context)` handler. The ordered
`0x00031A84..<0x00031A8E` plus `0x000939A0..<0x00093B30` bytes have SHA-256
`73db19284fddef49ec7adca5bee9bce5705cada5e1247e69e529eb910912d270`. This is provider evidence,
not authorization for a local TWI-driver rewrite: the functional image compiles
`modules/nrfx/drivers/src/nrfx_twim.c` with both recovered hardware instances enabled. The SDK's
MDK aliases expose these linked functions as the shared-peripheral vector names
`SPIM0_SPIS0_TWIM0_TWIS0_SPI0_TWI0_IRQHandler` and
`SPIM1_SPIS1_TWIM1_TWIS1_SPI1_TWI1_IRQHandler`; the linked-image verifier requires both symbols.

## SPIM2 interrupt provider

The 76-byte recovered body at `0x00031A94` is Nordic's `nrfx_spim_2_irq_handler` with its static
IRQ and transfer-finishing helpers inlined. It checks SPIM2 base `0x40023000` event offset `0x118`,
clears the event with the required Cortex-M4 read-back, deasserts an optional software slave-select
using the recovered polarity bit, clears `transfer_in_progress`, constructs `NRFX_SPIM_EVENT_DONE`,
and invokes the registered `(event, context)` callback. Its SHA-256 is
`8880914797b095ddd94c30fc9d2a848786a4c20e121d55d635d6116c042f4c64`.

The clean target compiles unmodified `modules/nrfx/drivers/src/nrfx_spim.c` with SPIM2 enabled,
extended mode disabled, and the recovered non-extended control-block shape. The linked-image
verifier requires both `nrfx_spim.c.o` and the MDK shared vector alias
`SPIM2_SPIS2_SPI2_IRQHandler`. This supplies only Nordic transport; no proprietary Goodix or other
sensor-provider algorithm is implemented by enabling the driver.

## RTC and TIMER driver APIs

Nine recovered nrfx entries are separately pinned:

| Recovered entry | Nordic symbol | Function-local discriminator |
| --- | --- | --- |
| `0x00031750` | `nrfx_rtc_2_irq_handler` | exact RTC2 base `0x40024000`, instance index zero, four compare channels, and tail dispatch |
| `0x00033828` | `nrfx_timer_2_irq_handler` | exact TIMER2 base `0x4000A000`, first 12-byte control block, four compare channels, and tail dispatch |
| `0x0003383C` | `nrfx_timer_4_irq_handler` | exact TIMER4 base `0x4001B000`, second 12-byte control block, six compare channels, and tail dispatch |
| `0x0007294C` | RTC `irq_handler` | complete four-channel compare loop plus TICK/OVERFLOW branches, event/interrupt disabling, event clears, and callback IDs `0...5` through the recovered handler table |
| `0x000729EC` | `irq_handler` | complete compare-event loop: `0x140 + 4*i`, `0x10000 << i`, event/interrupt conjunction, Cortex-M4 event clear, and `(event, context)` callback |
| `0x0007AD20` | `nrfx_rtc_enable` | START task, three-byte RTC control-block stride, powered-on state, and exact SDK log path |
| `0x0007AD6C` | `nrfx_rtc_init` | exact instance handler binding, initialized-state gate, NVIC priority/enable path, PRESCALER write, reliable/tick-latency state, and SDK logging; Ghidra omitted this complete 180-byte body |
| `0x0007AE4C` | `nrfx_rtc_tick_enable` | TICK event clear, event mask one, optional interrupt mask one, and exact SDK log path |
| `0x0007B1C4` | `nrfx_timer_clear` | direct CLEAR task at TIMER offset `0x0C` |
| `0x0007B1CC` | `nrfx_timer_enable` | START task, 12-byte TIMER control-block stride, powered-on state, and instance log path |

These drivers compile from `nrfx_rtc.c` and `nrfx_timer.c`; product code supplies only the chosen
instances, prescalers, callback behavior, and scheduling policy. Ghidra attached the shared RTC and
TIMER dispatchers at `0x0007294C` and `0x000729EC` to their corresponding veneers as discontiguous
ranges. The ownership inventory therefore records the proven 154-byte RTC and 70-byte TIMER
dispatchers as manual supplements, and the verifier pins every veneer and shared body independently.

## GPIOTE input driver provider cluster

Five complete public driver bodies, ten same-unit static/inline helpers, and the emitted
`nrf_bitmask_bit_is_set` body route to Nordic source:

| Recovered entry | Nordic symbol | Function-local discriminator |
| --- | --- | --- |
| `0x0002D3B4` | `nrfx_gpiote_irq_handler` | complete eight-channel IN-event collection, PORT clear/latch read, handler dispatch, and low-power PORT tail path |
| `0x0007A73C` | `nrfx_gpiote_in_event_disable` | exact PORT-path sense disable and channel-path event plus interrupt disable |
| `0x0007A784` | `nrfx_gpiote_in_event_enable` | exact toggle/LoToHi/HiToLo sense selection, high-accuracy event clear/enable, and handler-gated interrupt enable |
| `0x0007A81C` | `nrfx_gpiote_in_init` | exact allocation/error results, `hi_accuracy`, `skip_gpio_setup`, and `is_watcher` flag handling, channel event configuration, and low-power polarity packing |
| `0x0007A8EC` | `nrfx_gpiote_in_uninit` | exact disable, task/event reset, conditional GPIO reset, channel release, and pin-assignment clear order |
| `0x00057934` | `channel_free` | stores `FORBIDDEN_HANDLER_ADDRESS == -1` and clears low-power pin slots for channel IDs above seven |
| `0x00057950` | `channel_port_alloc` | exact `0...7` high-accuracy versus `8...15` low-power search, assignment, handler store, and port-pin store |
| `0x00057998` | `channel_port_get` | signed pin-assignment byte at recovered `m_cb + 0x40 + pin` |
| `0x00078176` | `nrf_bitmask_bit_is_set` | exact byte-index, relative-bit, mask-load, and result expression from `components/libraries/util/nrf_bitmask.h` |
| `0x0007F0E0` | `pin_configured_check` | exact configured-bitmask call and boolean normalization |
| `0x0007F0F4` / `0x0007F110` | `pin_configured_clear` / `pin_configured_set` | exact byte-index and bit clear/set against recovered `m_cb.configured_pins` |
| `0x0007F12C` / `0x0007F144` | `pin_in_use_by_port` / `pin_in_use_by_te` | exact signed assignment thresholds at channel count eight |
| `0x00080EA8` | `port_event_handle` | complete nRF52840 LATCH loop, opposite-sense reconfiguration, latch clear, polarity filter, callback dispatch, and pending-latch retry |
| `0x00080F78` | `port_handler_polarity_get` | exact low-power pin/polarity byte load and top-two-bit extraction |

The recovered control-block offsets, GPIOTE register offsets, GPIO helper callees, polarity values,
and complete function bytes are verifier-pinned. These are compiled from nrfx; R1-owned code is
limited to board pin choices and application callbacks.

## R1-owned boundary

The separately admitted entries `0x00048A28`, `0x0004DF18`, `0x0004E4B4`, `0x0004E66C`,
`0x000529BC`, `0x000539B8`, and `0x00066C4C` are product configuration or service glue. They may be implemented
locally only to provide recovered advertising, GATT, security, BAE8, and identity parameters around
the SDK APIs. Application event handlers containing Nordic example text are not promoted to SDK
ownership unless their complete function identity is independently established.

`0x0008185C` retains Nordic's `prefix_process` skeleton but substitutes an R1 wall-clock/date log
prefix for the SDK timestamp formatter. It is therefore a bounded
`clean_room_adapter_only_use_nordic_sdk` seam: the formatter remains vendor source and only the
R1-specific clock/prefix hook may be local.

`0x0007CF4C` retains the Nordic UART Service `ble_nus.c::on_write`/link-context skeleton but
expands it into an R1 four-characteristic BAE8 event adapter with two CCCDs, two value-write paths,
R1 event IDs, and
product logging. It is not admitted as an exact Nordic function: the SDK supplies link-context and
CCCD helpers, while only the recovered service/event seam may be implemented locally.

## SDK-bundled FreeRTOS RTC port

One hundred eight complete Cortex-M4F/RTC-port/kernel functions route to Nordic SDK's bundled FreeRTOS
10.0.0 source.
The central tick/list/task path is:

| Recovered entry | Upstream symbol | Exact discriminator |
| --- | --- | --- |
| `0x00027218` | `vPortSVCHandler` | exact `pxCurrentTCB` stack restore, `r4-r11`/exception-return load, PSP update, ISB, BASEPRI clear, and exception return |
| `0x00027238` | `vPortStartFirstTask` | exact vector-table MSP restore, IRQ/FIQ enable, DSB/ISB, kernel BASEPRI, and SVC 0 startup sequence; the pinned extent includes its compiler literal pool |
| `0x0002725C` | `xPortPendSVHandler` | exact PSP and conditional `s16-s31` save/restore, `r4-r11`/exception-return context, BASEPRI `0x40`, and call to recovered `vTaskSwitchContext` at `0x000965AC` |
| `0x000316E8` | `xPortSysTickHandler` | RTC1 compare/tick clears, 24-bit counter correction against the kernel tick, scheduler-suspended single-step rule, BASEPRI `0x40`, PendSV, and `SEV` |
| `0x0005CF78` | `eTaskConfirmSleepModeStatus` | exact pending-yield, pending-ready-list, delayed-list, and expected-idle-time decision tree returning abort/standard/no-timeout sleep states |
| `0x0005CFAC` | `eTaskGetState` | exact current/ready/blocked/suspended/deleted task-state classification against the recovered kernel lists |
| `0x00084CF0` | `prvAddCurrentTaskToDelayedList` | exact ready-list removal, indefinite suspended-list branch, overflow/current delayed-list selection, wake-time ordering, and next-unblock update |
| `0x00084D68` | `prvAddNewTaskToReadyList` | exact first-task list initialization for 56 priorities, current-task selection before scheduler start, task/TCB numbering, ready-list insertion, and PendSV request |
| `0x0008522C` | `prvIsQueueEmpty` | exact critical-section-protected `uxMessagesWaiting == 0` predicate |
| `0x00085468` | `prvResetNextTaskUnblockTime` | exact empty delayed-list `portMAX_DELAY` selection or head-owner wake-time load |
| `0x00085534` | `prvUnlockQueue` | exact signed RX/TX lock-count drains, event-list wakeups, missed-yield recording, unlock sentinels, and two critical sections |
| `0x0009560E` | `uxListRemove` | exact backlink repair, list-index correction, container clear, and item-count decrement |
| `0x00084E58` / `0x0008515A` | `prvCheckForValidListAndQueue` / `prvInitialiseNewTimer` | exact timer list/queue one-time initialization and timer name/period/callback/ID/status/list-item setup |
| `0x00084EA4` / `0x00084ECA` / `0x0008507C` / `0x00085094` | queue copy/mutex/new-queue statics | exact ring read/write pointer wrapping, overwrite accounting, mutex initialization, queue geometry, list initialization, and queue type |
| `0x00084F36` / `0x000850B6` / `0x000854CC` | task delete/initialize/free-stack statics | exact allocation-mode deletion, A5 stack fill, bounded task-name copy, priority/list/stack-frame initialization, and high-water scan |
| `0x00084F98` / `0x000851A4` / `0x000855A0` | `heap_4` init/free-list insertion/allocation | exact aligned 51,200-byte heap, end marker, ordered coalescing, allocated-bit/header rules, split threshold, accounting, and scheduler suspension |
| `0x000854E0` / `0x000854FC` | `prvTaskExitError` / `prvTestWaitCondition` | exact fatal task-return guard and event-group any/all-bit wait predicate |
| `0x000851F4...0x00085484` | timer insertion/expiry/command/block/sample statics | exact active-list selection, expired callback/autoreload handling, daemon command cases, scheduler-suspended blocking, tick-wrap list switching, and last-time update; the compiler inlines `prvSwitchTimerLists` into `prvSampleTimeNow` |
| `0x00093EAC` / `0x00093EB8` | `ulPortRaiseBASEPRI` | two identical emitted copies of the CMSIS port inline: read BASEPRI, set recovered syscall mask `0x40`, return the prior mask |
| `0x00084F68` | `prvGetExpectedIdleTime` | exact idle-priority/current-task, idle-ready-list length, higher-priority bitmap, and next-unblock-minus-tick decision tree |
| `0x00085248` / `0x00095678` | `prvListTasksWithinSingleList` / `uxTaskGetSystemState` | exact 56-priority ready traversal plus blocked, overflow, deleted, and suspended list enumeration into recovered 36-byte task-status records |
| `0x00085684` / `0x0008569C` | `pvTaskIncrementMutexHeldCount` / `xTaskGetApplicationTaskTag` | exact nullable current-TCB mutex count update and critical-section-protected application-tag read |
| `0x000856C0` | `pxPortInitialiseStack` | exact initial xPSR, task entry, task-return guard, parameter, exception-return token, and software-saved-register frame layout for the CMSIS nRF52 port |
| `0x00095738` | `uxTaskResetEventItemValue` | exact prior event-list value return and reset to `56 - current priority` |
| `0x00095C90` / `0x00095CA6` | `vListInitialise` / `vListInitialiseItem` | exact sentinel, count, index, owner-container initialization for the 20-byte list and item layouts |
| `0x00095CAC` / `0x00095CDC` | `vListInsert` / `vListInsertEnd` | exact ordered insertion including `portMAX_DELAY`, and index-relative end insertion with backlink/container/count updates |
| `0x00095CF4` / `0x00095D24` | `vPortEnterCritical` / `vPortExitCritical` | exact BASEPRI `0x40`, nesting count, handler-mode assertion, and zero-depth unmask behavior |
| `0x00095D48` | `vPortFree` | exact `heap_4` allocated-bit validation, header recovery, free-byte update, ordered coalescing, and allocation counter update |
| `0x00095DA4` | `vPortSetupTimerInterrupt` | LFCLK request, RTC1 prescaler `31`, TICK interrupt, CLEAR/START tasks, overflow event, IRQ priority `7`, and enable |
| `0x00095DE4` | `vPortSuppressTicksAndSleep` | complete 24-bit wakeup clamp, S140 nested critical region, RTC compare programming, DSB, Nordic FPU/power-management pre-sleep hook, SoftDevice/WFE wait, tick restoration, pending-IRQ clear, and `vTaskStepTick` |
| `0x00095F18` | `vPortValidateInterruptPriority` | exact IPSR/current-priority check and AIRCR priority-bit assertion used by ISR-safe APIs |
| `0x00095F70` / `0x00095F8E` | `vQueueDelete` / `vQueueWaitForMessageRestricted` | exact static-allocation-aware queue deletion and timer-task queue wait wrapper: lock, conditional restricted event-list placement, then the separately recovered `prvUnlockQueue` |
| `0x00095FD4` / `0x00096020` | `vTaskDelay` / `vTaskDelete` | exact scheduler suspension, delayed-list placement/yield, task-list removal, deletion accounting, cleanup, and reschedule paths |
| `0x000960B4` | `vTaskGetInfo` | exact recovered `TaskStatus_t` population, state resolution, and optional stack high-water mark |
| `0x000961B8` | `vTaskPlaceOnEventList` | exact event-list insertion, delayed-list placement, and indefinite-wait handling |
| `0x0009653C` | `vTaskStepTick` | exact next-unblock assertion, tick addition, and overflow-sensitive trace path for tickless correction |
| `0x000987A8` | `xTaskGetSchedulerState` | exact not-started/suspended/running state selection from scheduler and suspension globals |
| `0x000987C4` | `xTaskGetTickCount` | direct recovered kernel tick read |
| `0x000987E0` | `xTaskIncrementTick` | complete suspended/non-suspended tick update, delayed-list expiry loop, ready-list moves, priority/preemption checks, and tick-hook path |

Authenticated CMSIS-RTOS2 wrapper calls additionally pin these public provider targets without
using address-range order as a naming assumption:

- event groups: `xEventGroupCreate`/`CreateStatic`, `GetBitsFromISR`, `SetBits`, and `WaitBits` at
  `0x0009779C...0x0009788C`, plus `xTimerPendFunctionCallFromISR` at `0x0009787C`;
- queues, semaphores, and mutexes: create/static-create, generic send/ISR send, give-from-ISR,
  recursive give/take, receive/receive-from-ISR, and semaphore take at
  `0x00097A88...0x00098284`;
- tasks: `vTaskPrioritySet`, dynamic/static task creation, generic notification in task/ISR
  context, and notification wait at `0x00096314` and `0x000983B8...0x00098700`; and
- software timers: `xTimerCreate`, `xTimerCreateStatic`, `xTimerGenericCommand`, and
  `xTimerIsTimerActive` at `0x00098C48...0x00098D95`.

The first two compile directly from
`external/freertos/portable/CMSIS/nrf52/port_cmsis_systick.c`. The tickless function compiles that
same upstream port with Nordic's `components/libraries/pwr_mgmt/nrf_pwr_mgmt.c` selected through
`configPRE_SLEEP_PROCESSING`; the local implementation is limited to the recovered 1024 Hz RTC,
tickless-idle, and hook configuration. The five kernel callees compile from
`external/freertos/source/tasks.c`; the list, queue, heap, and CMSIS port entries compile from their
corresponding bundled sources. The verifier pins all one hundred eight full bodies by length and
SHA-256.

## Linked IQS7211E board providers

The clean-room IQS7211E product adapter now links Nordic's SDK driver implementations from
`modules/nrfx/drivers/src/nrfx_twim.c` and `nrfx_gpiote.c`. The local
`platform/nrf52840/sdk/openr1_touch.c` file is limited to recovered R1 pin selection, lifecycle
timing, lease policy, and provider glue. The linked-image verifier requires all three objects and
the retained TWIM, GPIOTE, IRQ, CMSIS timer, and CMSIS thread-flag symbols. This source selection
does not reclassify a stock function merely because Nordic supplies a compatible primitive; the
eleven recovered IQS7211E entries retain the product/provider ownership split documented in
`IQS7211E-PROVIDER-BOUNDARY.md`.

## Linked motion board providers

The motion port links Nordic `nrfx_twim.c` to the separately attributed Bosch BMA456 SensorAPI
v2.29.0 and ST LIS2DW12 v2.1.0-compatible provider sources. Local
`platform/nrf52840/sdk/openr1_motion.c` owns only the recovered TWIM1 400 kHz P0.11/P0.14 board
mapping, P0.15 input setup, address-`0x18` callbacks, fixed provider configuration, selection, and
bounded FIFO seam. The variant-neutral normalization and policy layer is `src/r1_motion.c`.

The linked-image verifier requires both official provider objects, both clean adapter objects, the
retained `.openr1_motion_api` table, Nordic TWIM calls, the exact Bosch/ST configuration calls, and
the public read/disable/query surface. QMA6100 is not linked because its available correlation
snapshot has no usable license. P0.15 interrupt-to-worker processing and downstream motion
ingestion remain unimplemented.

## Linked ST25DVxxKC board providers

The NFC board port links Nordic `nrfx_twim.c` and `nrfx_gpiote.c` with ST's separately
attributed BSD-3-Clause `st25dvxxkc.c` and `st25dvxxkc_reg.c`. Local code selects the
recovered `i2c_5` SCL P1.11, SDA P1.14, and GPO P0.03 topology, converts ST's `0xA6` data
and `0xAE` system-memory wire addresses for Nordic's seven-bit API, and supplies only bus,
resource-lease, interrupt-to-worker, and R1 policy adapters. TWIM1 keeps the IQS7211E TWIM0
provider independent, but motion now owns TWIM1 on P0.11/P0.14. NFC therefore remains disabled
until its recovered software-`i2c_5` transport or another evidence-backed coexistence design is
implemented; the current hardware-TWIM NFC adapter must not be enabled concurrently with motion.

The linked-image verifier requires the ST component objects, the R1 adapter objects, and
retained symbols for ST bus registration, initialization, identity, password presentation,
security-session state, mailbox mode/status/length/data, energy-harvesting reset, mailbox
enable, and GPO1/GPO2 access. Nordic startup installs the exact P1.10 board-enable sequence and a
static CMSIS mutex for exclusive `i2c_5` ownership; NFC still starts disabled and exposes no BLE or
raw register surface. The seven recovered product seams and five adjacent resource seams retain
their ownership split in `ST25DVXXKC-CORRELATION.md` and
`YHM2710-I2C5-RESOURCE-BOUNDARY.md`.

## Linked SAADC provider

Seven complete stock bodies include the IRQ handler at `0x000317CC..<0x0003190C` and the
`0x0007AEAC...0x0007B1C3` API range from the pinned SDK. They are
`nrfx_saadc_irq_handler`,
`nrfx_saadc_channel_init`, `nrfx_saadc_channel_uninit`, `nrfx_saadc_init`,
`nrfx_saadc_limits_set`, `nrfx_saadc_sample_convert`, and `nrfx_saadc_uninit`. Their state checks,
channel/register setup, blocking event polling, limits validation, and callback ABI match
`modules/nrfx/drivers/src/nrfx_saadc.c`; openR1 compiles that source rather than reconstructing it.

The local `openr1_analog.c` adapter is limited to the recovered 12-bit/no-oversample/priority-6
configuration, AIN5/AIN3/AIN2 routes, gains/acquisition times, startup settling, serialization, and
calls into Nordic. Conversion, curve, and charge-state behavior is separately R1-owned. Exact
extents and hashes are in `ANALOG-BATTERY-CORRELATION.md`. The linked-image verifier requires the
Nordic object and retained analog API. The legacy Nordic image still leaves battery power abstract;
the alternate Zephyr image binds the reconstructed YHM service. Neither target adds a raw ADC BLE
surface.

## Linked watchdog provider

Four omitted stock bodies are exact semantic matches for SDK 17.1.0
`modules/nrfx/drivers/src/nrfx_wdt.c`: `nrfx_wdt_channel_alloc` at
`0x0007B470..<0x0007B4D6`, `nrfx_wdt_channel_feed` at
`0x0007B508..<0x0007B516`, `nrfx_wdt_enable` at `0x0007B520..<0x0007B556`, and
`nrfx_wdt_init` at `0x0007B570..<0x0007B5E6`. Together they account for 288 executable bytes.

OpenR1 compiles that Nordic source. Its local adapter supplies only the recovered behavior value
1, 10,000-millisecond reload, interrupt priority 6, one reload channel, no-op timeout callback,
and low-priority scheduler feed. Exact hashes and the adjacent R1 operation/binding split are in
`WATCHDOG-DEVICE-CORRELATION.md`.

## SDK-bundled SEGGER providers

Presence inside the Nordic archive does not make third-party code Nordic-owned. The SDK contains
SEGGER RTT 6.18a and a SEGGER 6.14d-derived printf formatter, both with identifiable source and
license text. These entries route to the bundled provider sources:

| Stock entry | SEGGER symbol | Pinned SDK source |
| --- | --- | --- |
| `0x00031948` | `SEGGER_RTT_Init` thunk | `external/segger_rtt/SEGGER_RTT.c` |
| `0x0003194C` | `SEGGER_RTT_Read` | `external/segger_rtt/SEGGER_RTT.c` |
| `0x00031964` | `SEGGER_RTT_ReadNoLock` | `external/segger_rtt/SEGGER_RTT.c` |
| `0x000319E0` | `SEGGER_RTT_Write` | `external/segger_rtt/SEGGER_RTT.c` |
| `0x00031A18` | `SEGGER_RTT_WriteNoLock` | `external/segger_rtt/SEGGER_RTT.c` |
| `0x00036D68` | `SEGGER_RTT_Init` | `external/segger_rtt/SEGGER_RTT.c` |
| `0x00036F72` | `_GetAvailWriteSpace` | `external/segger_rtt/SEGGER_RTT.c` |
| `0x00037EB6` | `_WriteBlocking` | `external/segger_rtt/SEGGER_RTT.c` |
| `0x00037F10` | `_WriteNoCheck` | `external/segger_rtt/SEGGER_RTT.c` |
| `0x00056744` | `buffer_add` | `external/fprintf/nrf_fprintf_format.c` |
| `0x00072310` | `int_print` | `external/fprintf/nrf_fprintf_format.c` |
| `0x00078A72` | `nrf_fprintf_fmt` | `external/fprintf/nrf_fprintf_format.c` |
| `0x00093EF8` | `unsigned_print` | `external/fprintf/nrf_fprintf_format.c` |

The RTT match includes the exact `Terminal` channel, 512-byte up buffer, 64-byte down buffer, two
up/down descriptors, zeroed indices/flags, 16-byte reversed control-block ID initialization, and
the read/write ring-buffer paths with their BASEPRI `0x20` locking wrappers. The three internal
write helpers are separately pinned and cover free-space calculation, blocking wraparound, and
the caller-prechecked two-copy path.
The formatter matches flag parsing, decimal/hex conversion, padding/sign behavior, and buffered
character emission. Nordic's `nrf_fprintf` and flush wrappers remain listed in the Nordic table.

The application PDM vector at `0x000270B4` points to `0x000309DC`, whose complete 224-byte body
matches `modules/nrfx/drivers/src/nrfx_pdm.c::nrfx_pdm_irq_handler`: STARTED/STOPPED event handling,
double-buffer release, overflow reporting, active-buffer selection, and deferred buffer request.
OpenR1 uses the pinned Nordic translation unit when validated PDM hardware requires it and does not
recreate or enable the peripheral driver locally. See
[`FRONTIER-224-230-CORRELATION.md`](FRONTIER-224-230-CORRELATION.md).

The function ownership generator and verifier encode 782 Nordic source-routed entries in total:
564 application entries documented here and 218 bootloader entries, plus thirteen SDK-bundled SEGGER
entries and six bounded R1/Nordic adapters. Any new match must
meet the same function-local standard before its disposition changes from
`investigate_before_implementing` to `use_nordic_sdk`.

The application startup pair and recovered `CONFIG_NFCT_PINS_AS_GPIOS` /
`CONFIG_GPIO_AS_PINRESET` build switches are independently body- and callsite-pinned in
[`NORDIC-SYSTEM-INIT-CORRELATION.md`](NORDIC-SYSTEM-INIT-CORRELATION.md).
The exact static transfer-completeness helper is separately pinned in
[`NORDIC-TWIM-COMPLETENESS-CORRELATION.md`](NORDIC-TWIM-COMPLETENESS-CORRELATION.md).
Thirteen exact Peer Manager GATT-cache functions are separately pinned in
[`NORDIC-GATT-CACHE-CLOSURE.md`](../closures/NORDIC-GATT-CACHE-CLOSURE.md).
Five exact BLE/Peer Manager static helpers are separately pinned in
[`NORDIC-BLE-STATIC-HELPERS-CORRELATION.md`](NORDIC-BLE-STATIC-HELPERS-CORRELATION.md).
Eight exact BLE advertising functions are separately pinned in
[`NORDIC-ADVERTISING-START-CLOSURE.md`](../closures/NORDIC-ADVERTISING-START-CLOSURE.md):
`ble_advertising_conn_cfg_tag_set` at `0x00051710`, `ble_advertising_init` at `0x00051716`,
`ble_advertising_modes_config_set` at `0x000517FE`, `ble_advertising_on_ble_evt` at `0x00051806`,
`ble_advertising_start` at `0x00051870`, `flags_set` at `0x00064F1A`, `phy_is_valid` at
`0x0007F0C8`, and `use_whitelist` at `0x00094DD8`, all from
`components/ble/ble_advertising/ble_advertising.c`.
Ten exact unbonded buttonless Secure DFU provider functions are separately pinned in
[`NORDIC-BUTTONLESS-DFU-CLOSURE.md`](../closures/NORDIC-BUTTONLESS-DFU-CLOSURE.md). Eight are Ghidra inventory
entries; `ble_dfu_buttonless_bootloader_start_finalize` at `0x00052050` and
`ble_dfu_buttonless_on_ble_evt` at `0x00052154` are independently bounded manual supplements.
They come from `components/ble/ble_services/ble_dfu/ble_dfu.c` and
`ble_dfu_unbonded.c` with `NRF_DFU_BLE_BUTTONLESS_SUPPORTS_BONDS=0`.
Nordic's exact `nrf_pwr_mgmt_shutdown` at `0x00079D50` and static `shutdown_process` at
`0x0008F234` are separately pinned in
[`NORDIC-POWER-MANAGEMENT-CLOSURE.md`](../closures/NORDIC-POWER-MANAGEMENT-CLOSURE.md), including the recovered
no-scheduler and SoftDevice-present configuration.
