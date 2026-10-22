## from w2-display
- third-party/upstream/ambiq-lvgl @5be8e0a src/draw/ambiq/lv_draw_ambiq_border.c (lv_draw_ambiq_border 0x53DF00), lv_draw_ambiq_line.c (nema_raster_line_aa 0x53EBBC, lv_draw_ambiq_line 0x53ECFC); lv_area_copy out-of-line copies 0x53DC24/0x540024/0x5409DC/0x53FA94 come with fill/box_shadow/mask_rect TUs. Stock uses LV_USE_FLOAT=1.
## from w2-kvdb
- Stock FlashDB is **2.1.1** (third-party/upstream/flashdb is an empty checkout; only flashdb-2.0.0 present). fdb_kvdb_control 0x545320, fdb_kvdb_init 0x5453fe, fdb_kv_set_default 0x5450a4, fdb_kv_get_blob 0x54454a, fdb_kv_set_blob 0x54503a (kvdb code calls the first three by upstream name).
- (w2-nvdb) same FlashDB calls, under suffix names fdb_kvdb_control_545320 / fdb_kvdb_init_5453fe / fdb_kv_set_default_5450a4.
## naming conflicts to unify at merge
- audio_uart_buffer_zero is used for both 0x43c0e4 and 0x48949c; audio_uart_checksum_copy for both 0x439be4 and 0x439c04 (pre-existing).
## from p-01
- Google liblc3 v1.1.3 (96a3af0b; submodule third-party/upstream/liblc3 pinned but not checked out): src/ltpf.c and src/bits.c at 0x438400..0x439B78 (resample_16k/32k/48k/8k/24k/96k/x192k_12k8, dot, correlate, interpolate, interpolate_corr, lc3_ltpf_analyse, lc3_ltpf_get_nbits, lc3_ltpf_put_data; ac_get_range_bits, get_bits_left, lc3_setup_bits, lc3_get_bits_left, accu_flush, ac_shift, lc3_flush_bits, lc3_put_bits_generic, lc3_ac_write_renorm). Generic C path (ltpf_arm.h disabled). Encoder caller 0x59138A.
## BLOCKED (license) — needs user decision
- Nordic nrf_fuel_gauge (closed, LICENSE clause 5 forbids RE): ~0x439CE0..0x43C260, 0x55F74C..0x55FA20, 0x58EAC4. Not reconstructed.
## duplicates to retire
- runtime/startup-unpack/unpack.c audio_startup_unpack duplicates 0x43A11E (now iar_lz77_init_single3_43a11e in p-01) with a different ABI.
## from w2-ble-ll
- Cordio r20.05c dual_chip/hci_cmd.c: hciCmdInit 0x52AEC6, HciLeGenerateDHKey 0x52B20E (whole-file unit would clash with hand-written HciLeRandCmd/hciCmdAlloc/hciCmdSend/HciResetCmd -> slice or hand-write). hci_core_ps.c HciLlPrivacySupported 0x530D54 (TSV mislabels it HciLeAdvExtSupported).
- TSV "cordio-ll-island" rows 0x5D2418..0x5D4ED0 are FreeType 2.9.1 psaux (cf2_*), covered by experimental unit third-party/upstream/freetype/src/psaux/psaux.c (promote/anchor).
- Ambiq HCI reset variants match AmbiqSuite R3.2.0 (third-party/local-vendor, ignored); third-party/upstream/ambiqsuite-sdk is empty.
## check at merge
- opencfw_radio_gpio_callback (0x4B4A98 HciDrvIntService) defined in both ble/radio-gpio/radio_gpio_callback_bridge.c and apollo-common/radio-gpio/radio_gpio.c.
## from w2-pmic
- npmx v1.0.1 (submodule empty): npmx core/gpio/vbusin/timer/charger/adc/buck/ldsw/backend/ship functions at 0x55EB3E..0x55FC6A (list in pmic report; suffix names npmx_*_<addr>). Some already exist as display_driver_uled_pmic_* (0x55fa0e.., 0x55face.., 0x55fb7c, 0x55fc2c/38) -> retire in favour of upstream.
- AmbiqSuite timer HAL 0x471C9A..0x471E78 (am_hal_timer_*), product UART HAL 0x55E5BC..0x55E956 (hal_uart_*) are referenced by suffix names; check for existing defs.
## rename at merge
- DRV_BuzzerPlay 0x502BF0 exists only as audio_wear_child_502bf0 (callers use stock name) -> defsym or rename; DRV_BuzzerPlayAfterQueue prototype mismatch (signed).
## from w2-iom
- TDK invensense-icm45608: inv_imu_i2cm.c (0x55D280..0x55D560), Ict1531x.c (0x55D588..0x55D7D8); stock wait_us 0x55D63C variant calls delay 0x491102 (override).
- AmbiqSuite 5.1.0 hal/am_hal_adc.c 0x55D94C..0x55E09C (FP profile; unused fns absent in stock).
- npmx core/vbusin/timer/charger/adc 0x55EA40..0x55F6F0 HAND-WRITTEN in drivers/power/npmx-core/npmx_core.c because submodule was empty — now checked out at e1aaec53: compare and replace with upstream units if equal.
- nrf_fuel_gauge ext_state_update byte-identical (mod relocs) to sdk-nrfxlib 8f9ab9b0 cortex-m33/hard-float libnrf_fuel_gauge.a; process differs (other release). Binary-only candidate.
- dedupe track: 251 addresses with >1 definition (scratchpad/dupaddr.json); productModeGet 0x4abe60 = audio_uart_command_pending + audio_role
## from w2-rtos
- CMSIS-FreeRTOS cmsis_os2.c @d213f261: osKernelInitialize, osKernelStart, osThreadGetId, osThreadSetPriority, osTimerIsRunning (+ 17 hand-written anchored copies and 3 pool statics are upstream-identical -> replace with one upstream unit; libraries.md rates all 43 Proven).
## dedupe notes
- app/input-msg/input_msg_send_record.c audio_input_message_state[16] overlaps g2_input_thread_desc (0x2000408c) data definition.
- audio_ble_scan_core (bounded) should be replaced by scanf_core_4d1638.
## from p-08
- FreeType 2.9.1 src/base/ftstroke.c starts at 0x567FC6 (ft_pos_abs, ft_angle_mean upstream-only); 12 hand-written stroker ports in ui/freetype/font-freetype duplicate it (names swapped for subpath_start/process_corner) -> replace with upstream unit (prepared: scratchpad/upstream-ftstroke.json).
## BLOCKED (license) — NemaVG
- NemaVG stroker module 0x5640E4..0x56722A (0x5657D8 tessellator, 0x567230 stroke draw, 0x5675A8, 0x5675B4). Earlier trees already contain reconstructed NemaVG internals (graphics/nema-vg/, ambiq-buffer-handlers/vector_path_state.c) -> flag for user decision.
- (p-02) nrf_fuel_gauge internals 0x43A698, 0x43BA6C, 0x43BB14, 0x43BC58, 0x43BC84, 0x43BE18, 0x43BFAC not reconstructed (license). 0x43C08E..0x43C0AE unreferenced code, no row.
## from p-03
- ambiqhal-apollo510 hal/am_hal_timer.c (default_config_set 0x471CAE, output_config 0x471E20, compare0/1_set 0x471E5E/78, interrupt_enable/status_get/clear 0x471E92/9E/BC); hal/mcu/am_hal_cachectrl.c dcache_enable 0x474F32; hal/mcu/am_hal_secure_ota.c am_hal_ota_add 0x475230.
- AmbiqSuite utils/am_util_stdio.c (statics 0x472C7C..0x472EF6, vsprintf 0x473036, printf 0x4733EE) — only in local-vendor R3.2.0; need pinned SDK 5.x utils.
- ambiq-lvgl v9.3: lv_tick_inc 0x473474, lv_tick_elaps 0x4734A0, lv_memzero out-of-line 0x4734C0.
- (p-04) ble-comm/display_ble_comm_forwards.c calls 0x4782dc as audio_ble_msgtx_message -> APP_ConnectParamHandler (defsym)
- (p-05) tracepoint_write_state_47df28.c uses audio_tracepoint_crc32_48ecae but stock calls 0x47ddfe (tracepoint_state_crc_47ddfe) — fix in dedupe pass. ui_registry_table.c references audio_uart_registry_callback_47cf60 = UX_LocalSystemStatusSyncHandler (defsym).
## from p-07
- LVGL 9.3 (third-party/upstream/lvgl; config g2/config-recovered/lvgl/g2-config/lv_conf_recovered.h): lv_sprintf_builtin.c lv_vsnprintf_inner 0x483960 (+_ftoa 0x483350, _etoa 0x48364C, _ntoa_long 0x48320A, _ntoa_long_long 0x48329C, snprintf/vsnprintf 0x483FD0/0x483FEA); lv_theme_default.c (get 0x487156, style_init_reset 0x488198; init/_is_inited hand-written as audio_uart_page_487022/_48716c); lv_palette.c (lighten 0x4882D2, darken 0x48834C; main = audio_uart_page_488290); lv_math.c (atan2 0x4887BC, rand_set_seed 0x4888F6; trigo_sin = audio_uart_lv_sin_4885f0, bezier3 = audio_uart_lv_anim_bezier_curve_48869a); lv_draw_label.c lv_draw_glyph_dsc_init 0x489FD6. LV_USE_BIDI=0. DECISION: upstream units + retire hand-written per-function copies (repo rule: consume upstream, never re-implement).
- npmx_ship.c task_trigger 0x55FC44, npmx_ship_get 0x55FC60, npmx_ship_config_get 0x55FC74.
- BLOCKED nema: 0x5619F2 nema_mat3x3_mul, 0x56395C, 0x5639E8, 0x5640E4, 0x564974, 0x5653A0. nrf_fuel_gauge ttf 0x55F9A0.
## from p-12 (liblc3 track)
- liblc3 v1.1.3 @96a3af0 (LC3_PLUS_HR=1): sns.c, tns.c, spec.c at ~0x5990CC..0x59C78C (link order sns, tns, spec) + tables.c data; plus ltpf.c, bits.c (p-01). Needs FP profile (g2-apollo-main-7 base) + -I liblc3/include + math.h shim (fabsf fmaxf fminf floorf roundf truncf sqrtf). Upstream non-const tables q_thr/q_inv/ge_table are in RAM (0x20004144/0x20004164/0x20003a78). No G2 changes found.
- (p-15) all 34 PCM2.1/2.2 SPOT power rows anchored (comment only). Dedupe: 0x5A423C implemented twice (callback_voltage + pcm22_ton_adjust); pcm22_sequence_6/_10/_23 call other sequences' bodies instead of separate functions. Anchoring for qualify needs suffix renames (later rename pass).
## from p-09
- ambiqhal am_hal_uart.c: read_transaction_save 0x58DF5C, am_hal_uart_transfer 0x58E3F8, blocking_read 0x58E49E, nonblocking_read 0x58E50A (stock layout: compat.h one-byte enums, handle 0x11c; stock dma_transfer_complete/abort don't clear bDMABusy). UART HAL has several overlapping copies in g2/src (uart-tx, uart-irq, uart-power-config, uart-rx-stream, sync-driver) -> consolidate.
- npmx_errlog.c: npmx_errlog_get 0x58EA08 (extern npmx_retained_get_58ea08), npmx_errlog_scratch_set 0x58EA12, npmx_errlog_scratch_get 0x58EA68 (npmx_retained_read_58ea68).
- FreeType ftbitmap.c: ft_gray_for_premultiplied_srgb_bgra 0x58EE58, FT_Bitmap_Convert 0x58EE9E. FreeType stroker hand-written copies anchored at 0x568E52/0x569160/0x569748.
- Cordio wsf/util/bstream.c BstreamToUint64 0x58F182.
- BLOCKED fuel gauge: 0x58EAB0, 0x58EABC, 0x58EAC4.
## from p-06 (needs "slices": whole-file units would collide with hand-written copies or stock variants)
- freertos-kernel timers.c @def7d2df: xTimerCreateTimerTask 0x47E674 (prio 54), xTimerIsTimerActive 0x47EAF6.
- ambiqhal am_hal_pwrctrl.c (gpu_mode_status 0x47F108, mcu_memory_config 0x47F204, sram_config 0x47F46A, crypto_quiesce 0x47F56E, periph_disable_msk_check 0x47F6F2, low_power_init 0x47FAE8, buck_ldo_override_init 0x47FE12, control 0x47FEA0, pwrmodctl_cpdlp_get 0x480008); stock TrimVersionGet differs.
- ambiqhal am_hal_spotmgr.c timer_* 0x4801FC..0x4802CE, simobuck_* / boost / ton / post_lptohp / lp_autosw 0x480358..0x48041E; stock spotmgr_init differs (hand-written). Built with NO_TEMPSENSE_IN_DEEPSLEEP=0, AM_HAL_PWRCTRL_SIMOLP_AUTOSWITCH=1.
- ambiqhal am_hal_gpio.c interrupt_status_get 0x4812F6, interrupt_clear 0x481468.
- LVGL 344c7c31: lv_memzero 0x4826FC, lv_style_get_prop_group 0x48277E, lv_style_init 0x48278C, lv_style_transition_dsc_init 0x482950, lv_style_is_empty 0x482A5A, lv_ll get_len/is_empty/node_set_prev/next 0x482D02/0x482D88/0x482DAE/0x482DC2.
- dedupe: 0x47EB26 twice (audio_freertos_timer_get_id vs audio_aux_get_id); g2_spotmgr_state 0x20073270 = audio_ble_flash_callbacks.
## TOOLING IDEA for slices: per-unit objcopy --weaken-symbol / --strip-symbol on upstream objects so stock-variant hand-writes override; or whole-file + retire hand-written copies.
## from p-19
- All 29 rows 0x5DA202..0x5DDD38 are FreeType 2.9.1 src/sfnt (sfdriver.c, sfobjs.c, ttbdf.c, ttcmap.c), covered by existing experimental unit third-party/upstream/freetype/src/sfnt/sfnt.c (promote/anchor). Stock config = upstream default ftoption.h (GX var, zlib/WOFF, BDF on). sfnt_find_encoding table at ROM 0x6D51D4 (11x12 B) identical to upstream. 0x5DA1E8 = fmix32 (not in p-19).
- (p-11) ring-buffer submodule empty (pinned 190e30be) -> checkout; FAL hand-written but matches FlashDB port/fal @714d615 (could replace with upstream fal*.c + fal_cfg.h).
## GENERAL (from p-17): IAR keeps every static function out of line — upstream units need a -fno-inline (+ -ffunction-sections) profile to emit them; rows identified as upstream should get TSV names (g2/symbols/apollo_main.tsv) so qualify_sources can anchor them. FreeType psaux island 0x5D1ED0..~0x5D6F00 (incl. cf2_interpT2CharString 0x5D4ED0).
- (p-16) dedupe: 0x4D3F3C twice (audio_ble_hci_radio_read_word_4d3f3c vs audio_platform_read_words_restricted); distortion_screen zero_four_styles inline should call semantic_zero_four_object_styles.
- (p-20) FreeType sfnt unit failed qualification with 'ft2build.h not found' (source-qualification.json) -> fix profile include path. Inventory lacks many FreeType rows (cmap12/13/14 init/index/next..., kern/load/sbit helpers).
- (p-10) CmBacktrace upstream unit would clash with hand-written stock-variant cm_backtrace_fault_5944bc (vendor patch: prints ' ', calls thread dump 0x594334 + crash commit). cmb_println binding found.
- (p-14) p-06 am_hal_spotmgr_init.c externs spotmgr_pcm2_1_*_5a0bcc etc. resolve via suffix defsym to pcm21_* (anchored); p-06 pcm0_7/2_0 externs declared (void) but definitions take args — fix prototypes in dedupe pass.
- (boot-02) dedupe: 0x42ddda twice (opencfw_boot_dfu_thread_deinit vs _native); opencfw_boot_crc32 bitwise vs stock table (0x42FB00) -> replace. IOM clock fns 42c222/42c256/42c26a + configure 42cc34 are older-rev stock variants (keep hand-written).
- (boot-01) bootloader MSPI is upstream am_hal_mspi.c (with -fshort-enums offsets match); 10 upstream-only fns no C (mspi_cq_init/term, seq_loopback, configure/enable/disable/deinitialize/interrupt_enable, clkgen hfrcadj, interrupt_master_disable in .S). Dedupe: startup_clock_config.c hf1_apply/hf2_default/_hf2_apply dup provider4/5 leaves; glue/syspll_disable_4273dc.c dups pll_disable; opencfw_bl_delay_us empty body.
## codec-a-02/03, em9305-01, case-reconcile, u-04
- codec: image A SRAM text = unmodified NationalChip drivers_lib + lvp sources (link order documented); clk_init = SDK clock_board.c + 1-line patch (PDM source OSC_1M) -> replace 5 resident_clock_* files with patched upstream; dup 0x100260D0 _SnpuCallback (resident_kws_queue.c vs resident_tws_buffer_update.c); spurious fragment gx8002_resident_clock_subband_hz_25e38 (not an entry). XIP libgcc byte-identical to toolchain libgcc.a (ck803 hard-fp). Link blocker: gx8002_fpadd_parts_nan static in resident_xip_fpadd_parts.c must be exported.
- em9305: 185 rows blocked SDK archives + 19 probable-SDK; existing g2/src/em9305 already contains reconstructed proprietary PML/ProtTimer/SLEEP_MANAGER/WSF/lctr code (listed in em01 report) -> license decision. QP/C 6.5.1 @416dcec8 submodule not checked out.
- case: 405 rows anchored, 102 duplicate definitions over 86 rows (legacy-default vs startup vs glue) -> dedupe; stm32g0xx-hal-driver and cmsis-device-g0 submodules empty; Arm C library (armlib) proprietary, hand-written equivalents only.
- u-04: "g2-freetype-engine-census" range 0x514xxx..0x52xxxx is likely NemaGFX/NemaVG, not FreeType (blocked). Existing graphics/ambiq-buffer-handlers/stencil.c, nema_trigonometry.c, matrix_rotate.c look like NemaGFX internals.
## UPSTREAM INTEGRATION TODO (consolidated specs from u-01/u-03/u-08)
- LVGL 14 files (core/lv_obj*.c, lv_refr, lv_display, lv_log, lv_timer, lv_anim, lv_indev, themes) + lv_style_gen.c + widgets/roller: profile g2-apollo-main-22 + -fshort-enums -fno-inline -DLV_CONF_INCLUDE_SIMPLE -DLV_DRAW_THREAD_STACK_SIZE=32768 + shim dir (lv_conf.h -> g2/config-recovered/lvgl/g2-config/lv_conf_recovered.h, inttypes.h, FreeRTOSConfig.h) + freertos include/port. Needs lvgl-g2-ambiq-draw-buffer-abi.patch (lv_display_t sys_layer +0x2BC); lv_global config incomplete (custom_log_print_cb +0x16C).
- FreeRTOS queue.c/tasks.c/heap_4.c: profile -3 + FreeRTOSConfig.h (libraries.md §1.2) + g2-tcb-v10.5.1.patch for tasks.c.
- EasyLogger elog.c @a596b264 (submodule not initialised): elog_cfg.h (FILTER_TAG_MAX_LEN 30, LINE_BUF 1024, no ASYNC/BUF), stdio shim.
- AmbiqSuite am_hal_infoc.c: profile -2 + ambiqhal includes + -fno-inline.
- Cordio: stock = AmbiqSuite R3.2.0 copies (local-vendor, gitignored): dm_main.c, app_master.c, atts_write.c (connId-1 fix), app_db.c G2-modified. Needs cordio_recovered_config.h (+ ATT_NUM_SIMUL_NTF=10).
- FreeType units: already compile (g2-apollo-main-4); need -fno-inline. Stale 'ft2build.h' failure was from old gcc scan.
- Touch: CAPSENSE (6.10, 247a9a0; pinned gitlink is 3.0.1) and emeeprom are Cypress EULA (clause iii forbids RE) -> license question; ~75 existing reconstructions. Profile g2-touch-1 needs -fshort-enums.
- Dedupe additions: ble/cordio-bda/bda_is_zeros.c dup strong BdaIsZeros (non-faithful) -> retire; nvdb am_hal_otp_* names -> am_hal_infoc_*; ring_node_add count bug; extern audio_ble_pair_record_ccc_set_47b3e2 vs AppDbSetCccTblValue_47b3e2; audio_uart_ambiq_vector_shape_draw_5202ec is nema_vg_draw_path (blocked); 0x526F32 name check.
- (u-12) FreeRTOS IAR portasm.s (0x5FA058..0x5FA132) needs a GNU-syntax .S equivalent for byte faithfulness (GCC portasm.c differs in layout); no recovered FreeRTOSConfig.h outside build/ (gap).
- (u-09) stock LVGL inlines cross-file trivial accessors (lv_event_get_current_target, lv_font_get_line_height) -> IAR multi-file compilation; profile -22 can't compile lvgl-global/global.c (no LV_CONF_PATH). Widget files lv_arc/button/buttonmatrix/rb/dropdown/chart/calendar compile with spec.
## from u-02 (integration specs)
- littlefs v2.10.1 lfs.c+lfs_util.c: base -O2 + -DLFS_NO_INTRINSICS -DLFS_DEFINES=g2_lfs_defines.h -I g2/src/apollo-main/storage/u-02-littlefs-config{,/include} -I third-party/upstream/littlefs -I g2/src/apollo-bootloader/filesystem/freestanding_include -fno-inline (compiles; no clashes).
- nanopb 0.4.9: -DPB_SYSTEM_HEADER="pb_g2_system.h" -include g2/config-recovered/nanopb/g2-config/pb_g2_options.h -I g2/config-recovered/nanopb/g2-config -I third-party/upstream/nanopb (compiles).
- Cordio r20.05c host files compile with Ambiq R3.2.0 include tree + cordio_recovered_config.h; app framework is AmbiqSuite-2.5.1-family (app_slave.c needs variant). Collides with hand-written DmConnRole/DmPrivClearResList/DmDevReset (display_ble_dm_pair_children.c) -> retire first.
- TLSF 3.1: vendored g2/src/apollo-bootloader/allocator/upstream/tlsf.c compiles for main; submodules tlsf, tinyframe not checked out.
- Duplicates of upstream to retire: storage/file/file-sync/* (g2_lfs_*), storage/file-lfs/display_file_lfs_*, mlist_*; app/pb-*; module_parser.c parser_start; tlsf_absorb_leaves/lists; ble/ble-app/* (6); dm_priv statics, AttGetMtu/AttcMtuReq, AttcRead/WriteReq, DmConnClose (+2nd copy audio_ble_ota_connection_route).
## from u-07
- Cordio: G2 ATT MTU floor patched to 247 (attsProcMtuReq_56c6fc variant); product WSF_TRACE -> elog dispatch (a recovered wsf_trace.h would let upstream files with traces compile unchanged). Ambiq R3.2.0 atts_read.c. Upstream units: dm_scan.c, dm_conn_master.c, attc_disc.c, attc_read.c, atts_proc.c (needs MTU patch), smp_sc_main.c.
- LVGL lv_bar.c (15 rows); liblc3 lc3.c (9 rows, -DLC3_PLUS_HR=1, math/string shim).
- dups: attsUuidCmp 0x56c550 / attsFindUuidInRange 0x56d93c hand copies; audio_app_hardware_core_59123a = lc3_hr_setup_encoder, audio_app_hardware_open_591374 = lc3_setup_encoder; display_page_create/initialize = lv_obj_class_create_obj/init_obj.
- (u-11) truetype.c unit needs -fno-inline -U__arm__ (stock uses portable TT_MulFix14/TT_DotFix14) + wrapper TU keeping empty Ins_POP/AA/EIF/SANGW (build/u11/tt_wrap.c). LVGL lv_tabview.c/lv_table.c units (table needs FreeRTOSConfig.h). LV_USE_USER_DATA on.
## CROSS-CUTTING (u-10): stock Apollo main uses the HARD-FLOAT calling convention (float args in s0; e.g. lv_line resolve_point_coord 0x5C9344). Our FP profiles -3/-20 use -mfloat-abi=softfp; agents worked around with pcs("aapcs-vfp"). A hard-float profile (fpv5-d16, -mfloat-abi=hard) is needed for all FP units. Also IAR ILINK inlines one-instruction functions at call sites (str; nop) -> byte identity needs linker-level emulation.
- LVGL widget units (chart, checkbox, keyboard, textarea, led, line, scale, slider, switch, table) compile with -22 + -fshort-enums -fno-inline -mfpu=fpv5-sp-d16 -mfloat-abi=hard -DLV_CONF_INCLUDE_SIMPLE -DLV_DRAW_THREAD_STACK_SIZE=32768 + shims. lv_conf_recovered.h updated (LV_USE_FLOAT 1 etc.).
## from u-06
- FreeType: ftcalc.c needs -DFT_CONFIG_OPTION_NO_ASSEMBLER -fno-inline (IAR path: ft_multo64/ft_div64by32/FT_Add64/FT_MSB real fns); new units fttrigon.c, ftfntfmt.c; fthash/ftgloadr -fno-inline.
- Cordio Ambiq copies atts_ccc/ind/main/sign, dm_sec_slave, sec_cmac_hci, wsf_queue, wsf_buf compile with -9 + include + cordio_recovered_config.h; stock adds connId-0 WARN traces (variants hand-written). Stock wsf_trace.h = elog cascade (documented). wsf_os.c needs FreeRTOSConfig.h. Ambiq wsf_os.c/wsf_buf.c carry Wicentric/ARM proprietary headers (license note).
- LZ4 v1.10.0 via lvgl/src/libs/lz4/lz4.c (flags in u-06 report). am_hal_wdt.c needs a main profile with HAL includes.
- dups: WsfSetEvent (display_ble_hci_driver_children.c), WsfQueueDeq (display_wsf_buf_queue.c) second copies.
## from a-01/a-04/a-05/a-07/a-08/a-09
- a-01: _RPC_SystemOtaStatusSync used by a-02 = audio_ble_rpc_ota_status_sync (alias). FreeRTOS queue.c 16 hand copies anchored; port.c ARM_CM55_NTZ rows upstream.
- a-04: Ambiq FreeRTOS STIMER port (port.c not pinned) hand-written; g2-tcb patch should add vTaskStackAddr/Size/Name + field name uxSizeOfStack; dups: xTaskRemoveFromEventList strong in tasks_subset.c AND ready_adapter.c; 0x455F5E twice; 0x454DCC twice.
- a-05: efs_transfer_state_ram.c reserves 0x76 but stock clears 0x78 -> widen.
- a-08: name conflict 0x44ea04 audio_uart_lv_scroll_to_y_44ea04 vs extern audio_terminal_display_status_44ea04.
- a-07: getStartUpAppID called with 3 args, defined with 2.
- (a-06) dedupe: 0x45a568 three defs (audio_uart_device_role_get, audio_settings_device_role, audio_uart_service_version); loggerSetting_set_ble_transmit = audio_uart_logger_ble_transmit_set_458df0 (alias); Thread_MsgPbTxByBle = audio_ring_pb_tx_ble_475b14 (alias).
- (a-10) audio_ble_status_register_callback (0x4abcc6) returns void but stock returns status (onboarding branches on it) -> fix; untabled fns 0x4aba58/0x4abba4.

## a-17 follow-ups
- Unify types before LTO: audio_ble_master_registration_table (byte array vs appMasterCfg_t), audio_onboarding_event_state_200f623c (u8[16] vs struct), audio_ble_master_context/mode_slot/state_shadow (u8* vs typed).
- onboarding_common_data_handler 0x47e2d0 takes 3 args (r2 = submsg size); p-06 definition has 2.
- 0x4a8368 unit calls 0x439be4 where stock uses word-aligned entry 0x439c04.
- Invented names: elog_hexdump_43dacc, app_db_paired_count_47a676, ble_pair_record_remove_47b59c, app_conn_close_4bb04a, rpc_system_ble_status_sync_4b82e8.

## a-13 / a-15 follow-ups
- ui-registry: audio_uart_registry_callback_492fdc -> evenhub_loading_page_ui_event_handler_492fdc (defsym or rename).
- registry_callback_48e484.c: audio_uart_registry_child_497960 -> service_ancc_notification_process.
- TinyFrame eb75483e (0x4916B8..0x49225A) upstream; unanchored hand copies under app/module-*, app/frame-* to retire; frame_response.c mislabels 0x492200 TF_SendFrame, 0x49224C TF_Query.
- Prototype conflicts: 0x464C36 audio_system_alert_close returns int32 (used at 0x492F3C); 0x464bb2 audio_uart_master_display_refresh returns u32.
- onboarding.c getters 0x31/0x58 are border_color/text_color, not bg_color/image_recolor.
- lv_label.c 344c7c31 rows (9) need the LVGL upstream unit with -fno-inline; stock lv_image.c is a different revision (assert line 472).
- Undefined RAM cells: g2_even_ai_last_wakeup_tick 0x20074978, g2_dashboard_* (see a-15), g2_evenhub_loading_* 0x20074590.., g2_ble_msgrx_thread_attr ROM 0x75B880.
- a-18: onboarding process record 0x200f4800 has a tick word at +4 (other units use a 3-byte struct). 0x4A8E6C returns u32 (a-10 declares void).
- a-11: ui_registry_table.c audio_uart_registry_callback_469580 -> silent_mode_ui_event_handler; _46aeea -> system_close_ui_event_handler.
- a-11: lwrb v3.x (MIT, C11 atomics) at 0x46D8A0..0x46DB04, 7 rows; candidate for a pinned submodule. Existing hand copies (audio_uart_input_ring_*, audio_uart_display_ring_*) lack atomics and fold 0x46D9C8.
- a-11: 0x46CACC strcmp written as string_compare_46cacc — check vs IAR DLIB strcmp unit (possible duplicate).
- a-12: audio_uart_ring_parse_uint_48d874 is an approximate _Stoulx copy; reconcile with iar_stoulx_48d724.
- a-12: APP_PbRxNotificationFrameDataProcess (0x4d6ba8) vs existing audio_message_notify_frame_process_4d6ba8 — defsym or rename.
- a-12: STIMER HAL 0x48D570..0x48D704 is an older Ambiq variant (no AM_CRITICAL) — hand-written, not upstream.
- a-12: lv_draw_buf.c / lv_draw_label.c rows match ambiq-lvgl, not third-party/upstream/lvgl.
- a-16: ui_registry_table.c audio_uart_registry_callback_49ddb8/_49e68c/_49ed04 -> Dashboard_common_data_handler_49ddb8 / Dashboard_ui_event_handler_49e68c / WearDetect_DataHandler_49ed04.
- a-16 calls a-15 dashboard rows 0x49c09a..0x49cb50 under its own invented names; resolve via _addr suffix aliases.
- 0x464bb2 return type: three segments now say it returns a value — change the definition from void.
- a-20: 0x478110 ble_state_skip_manual_start vs extern audio_tracepoint_reset_pull_478110 (undefined). Prototype fixes: APP_EvenOtaWriteCback (7-arg ATTS cb, app_ble_startup.c says void), TPL_SendPacket returns u8 (thread_ble_msgtx.c says u32), APP_BleSlaveDisconnect takes r0.
- a-23: littlefs v2.10.1 (19 rows) + TLSF 3.1 (17 rows) upstream; 26 hand copies under storage/file-lfs, file-sync, file-pool-free to retire when upstream units land. Stock tlsf.c is vendored line +1 (one-line shim). am_hal_mram.c needs an apollo-main unit (compiles with -fno-inline + ambiqhal/CMSIS includes).
- a-21: efs_receive_packet_4d0d80 (a-21 caller) vs efs_transport_receive_4d0d80 (a-23 def) — rename caller. profile_get_conn_state_byte vs audio_ble_profile_get_connection_state (0x46efd8). app_ble_startup.c write callbacks declared void — should be attsWriteCback_t.
- a-22: stop.c audio_stop_one is a partial copy of 0x4c95bc, superseded by thread_sync_4c95bc — retire. 0x20075019 is the aging/production-test flag (misnamed g2_audio_pdm_variant / g2_pdm_production_bypass). Undefined g2_dev_* / g2_tm_ota_exit_started globals.
- a-25: thread_ble_msgrx.c protos for APP_PbRxDevCfgFrameDataProcess (returns u32) and AppBleMasterPeerMgrUnpairDev (u8 dev type). nanopb pb_common iter_reset hand copy in app/pb-iter.
- Inventory rows missing (callback-only functions): 0x4DCC80 (a-26), 0x4DCED2, 0x4DD052, 0x4DD05A, 0x4DD31E (a-27).
- a-19: 0x4B5A44 GattSendServiceChangedInd vs audio_ble_dm_advertising_resume_4b5a44; WsfTrace vs audio_ble_wsf_trace; slave_finish.c mislabels 0x4B45B0 as AppSlaveProcDmMsg (real one 0x4B3CA4); tpl_schedule_rx_timeout_004b8c44 arg count 3 vs 4. 0x200746E0 has two names.
- evenhub_ui_private.h text config +0x10 flag_10 is text_align.
- a-29: undefined RAM globals g2_even_ai_dialogs 0x200739fc, g2_even_ai_layout_cache 0x20073f04, g2_even_ai_current_streaming_node 0x20074c08, g2_even_ai_stream_flag 0x2007503b.
- a-24 DEDUPE: 0x464d1c defined as audio_uart_input_event_send_464d1c (app/input-event) AND audio_ble_send_status_message (ble/ble-status). Retire one.
- a-24: whitelist record 0x20054718 is 0x1f42 bytes; audio_ble_whitelist_info[0x100] too small.
- a-24 upstream to retire: ui/freetype/font-cache copies (lv_cache_*), system/glue/trace_disable_provider.c, hal/clock clkgen leaves (am_hal_clkgen privates). cJSON 1.7.12 needs a unit (profile -20 + minimal libc includes + strtod/sscanf shim). ambiqhal clkgen/rtc/info/global need units.
- Inventory rows missing (a-28): 0x4dfcb8, 0x4e0caa, 0x4e0cb2, 0x4e0cba, 0x4e0cc4, 0x497db4. Handlers 0x4e0d3a/0x4e1c42/0x4e2a5c have no static refs (likely registered via compressed RAM init data).
- a-31: inventory gap 0x4e74fa..0x4e772c has unlisted functions 0x4e75b0, 0x4e75e2. stock_page_push_data_4e9e32 returns u32 (caller in a-16 declares void).
- a-30: a-16 dashboard_handlers.c externs need prototypes: dashboard_main_screen_event_4e814c int32, Dashboard_ReflashEventHandler_4e8dec(const u8*,u32), dashboard_main_screen_tick_4e923c int32. a-31 calls a-30 rows by other names (resolver _addr aliases). 0x200746e0 three names.
- a-33: Calendar_Page_Reflash_4ed9b6 takes (data,len) (a-32 defines 1 arg); Calendar_expire_update_4efcb8 takes u32 (a-30 declares u8).
- a-34: a-30 externs NewsWidget_AutoReflash_4f2cec (void, returns int) and news_widget_ext_event_handler_4f3440 (returns int). News cache +1 is source name, not title.
- a-35: a-37 callers -> lv_obj_set_style_pad_all_4f5068, quicklist_get_item_geometry_4f6fc4 (fix when a-37 lands). News_Widget_ext_init_4f4670 returns int32 (a-30 says void).
- RAM-GLOBAL UNIFICATION PASS NEEDED: dashboard/quicklist/news cells have different names across a-30..a-37 (0x2012a72c, 0x20074e1c, 0x20074e20, 0x200741a8, 0x20075040, 0x200042c0, 0x20074e60, 0x200746e0, 0x20074b9c...). Resolver must cover data symbols by _addr suffix; any defined twice under two names is a real behaviour bug.
- a-36: inventory gap 0x4f78cc quicklist_border_fade_in_ready_cb. a-30 externs quicklist_widget_tick_4f8878 (no args, int), Quicklist_Page_Reflash_4f8644 (int); a-31 QuicklistWidget_MainPage_init_4f891c (int).
- a-37: inventory gap 0x4fb1f2 health_page_reset. a-30 externs Quicklist_ext_Widget_init_4faf9c / quicklist_widget_deinit_4fb08c / Health_Page_Reflash_4fb5e8 return int32.
- a-40: ICM-45608 TDK upstream (26 rows) — integrating the invensense submodule unit needs invn_mag_init excluded (stock variant in drivers/a-40-invn-mag) and static mag_read_reg/mag_write_reg/self/mag_dev reachable. g2_app_sec_cfg 0x20074358 vs audio_ble_comm_profile_slot.
- a-42: inventory gaps 0x50BFB0, 0x50C150, 0x50C768. a-18 globals g2_onboarding_stock_flag_20074db8 / g2_onboarding_stock_page_20071048 are news-page cells (misnamed). a-18 0050D894 and a-19 0050DCBC externs return int32.
- a-39: ui_registry_table audio_uart_registry_callback_4ffca2 -> Health_common_data_handler. a-40 names 0x5020f0/0x502108 dashboard_ext_layout_text0/1_get vs a-39 callers text_a/b_get (resolver suffix).
- a-38: prototype fixes: a-30 Health_ext_Widget_init_4fd7b0/health_ext_event_handler_4fc360 int32; a-37 health_ext_widget_page_create_4fc644 int32; a-16 dashboard_respond_* return status; 4ff09c u32 vs a-39 int32.
- INVENTORY HOLES: agents keep finding functions with no apollo_main.tsv row (0x4DCC80, 0x4DCED2, 0x4DD052, 0x4DD05A, 0x4DD31E, 0x4dfcb8, 0x4e0caa..0x4e0cc4, 0x497db4, 0x4e75b0, 0x4e75e2, 0x4f78cc, 0x4fb1f2, 0x50BFB0, 0x50C150, 0x50C768, 0x4FD93C..0x4FDF74). gaps.py only measures TSV rows, so after the waves run a byte-coverage pass over code ranges not covered by any row and regenerate segments for uncovered code.
- a-45 DEDUPE: 0x44B610 strncmp defined twice (audio_l2c_strncmp, audio_ble_hci_vendor_compare_44b610). 0x5354C2 audio_ble_comm_disconnect_delayed is really APP_StartServiceDiscovery (rename).
- a-41: inv_imu_transport.c (8 rows) upstream unit needed; 0x509FDC lv_obj_set_style_pad_all_509fdc needs an inline-copy unit; ADC HAL am_hal_adc_* 0x55D94C..0x55E09C (13 fns, likely upstream). 0x20000064 as a "global" (audio_uart_display_page_size_cell) is actually LV_PCT(100) — audit. 0x20074368 is board info (widened to 4 bytes).
- Inventory rows to add (x-01): 0x4FD93C..0x4FDA24, 0x4FDA24..0x4FDAD4, 0x4FDAD4..0x4FDD6E, 0x4FDF08..0x4FDF74, 0x4FDF74..0x4FE0AA.
- a-46: Cordio sec_ecc_hci.c SecEccGenSharedSecret 0x536774 and ambiq-lvgl draw/ambiq/* (5 fns) need upstream units. am_hal_gpio_interrupt_* existing names are misleading (audio_ble_hci_radio_pin_mask_4810b0 = interrupt_control, audio_ble_hci_radio_register_48162c = interrupt_register).
- a-43: callback_manager static helpers + audio_callback_mgr_* need TSV names for qualify anchoring. CALLBACK_MGR_Deinit is void (callers declare u32). Fixed process_fuel_gauge_51201c to aapcs-vfp (stock s0). lv_roller/lv_tileview rows upstream.
- a-50: audio_uart_master_display_refresh (0x464bb2) return value used by 5+ segments — change its definition in app/master-requests/display_master_requests.c from void. navigation_ui_create_location_list_page_5485c4 takes page root in r0. navigation_send_type_* 0x5866c0..0x587240 have no C yet. FUN_0054c1f2/FUN_0054c240 are part of 0x549C24 (do not assign).
- a-51: a-48 header g2_nav_var_/flag_/buf_<addr> vs a-49 g2_navigation_* for same RAM (0x2007479c, 0x20074fe8, 0x20072c68...). 0x450500 lv_anim_delete has three names.
- a-47: FlashDB 2.1.1 fdb_kvdb.c upstream unit (30 rows; 20 hand copies in storage/flashdb + settings-flashdb to retire). Needs inttypes.h PRI* shim, fal_cfg.h, FDB_PRINT -> 0x4733ee; flags -2 + freestanding/flashdb includes + -fshort-enums -fno-inline. Fixed _Dtento/_Stodx to aapcs-vfp. hal_uart_send_55e7fa len is u32. Inventory hole 0x542D4C (restore-factory helper).
- a-55: apollo_main.tsv pt_cmd_XX_handler names wrong for 51/66 handlers (real map: pt_protocol_dispatch 0x56f50c..0x56f828; see case comments in app/a-55-pt-protocol/pt_protocol_procsr.c) — fix TSV names in the symbol pass. Inventory hole 0x55a350 APP_PbRxHealthFrameDataProcess (no row). Health UI headers place metric[] at +0, real is +4; "ring_state" +0xc0 is PRODUCTIVITY trend. Undefined globals g2_health_data 0x200f41b4, g2_health_pb_*, g2_quicklist_notify_seq 0x20074ffd, g2_pt_*.
- a-52 DEDUPE: 0x45a568 defined as audio_uart_device_role_get (ring_getters.c) and display_driver_uled_mode_45a568 (display-uled). Inventory holes 0x5505d0/5da/5e2, 0x550bf4, 0x550cc4, 0x550ed0. TSV names wrong: 0x588598 is app-icon-from-bundle-id, 0x588550 is bundle-id->display-name. AUDM_Init returns int32 (thread_audio.c says void). lz4.c (5 rows) upstream unit with LZ4_FORCE_MEMORY_ACCESS=0.
- AMB pairs (same address, two defs): 0x509b48 audio_fault_unmapped_code_message vs audio_ring_pb_assert; 0x450500 audio_lv_object_call vs audio_uart_lv_style_unlink; 0x499678 audio_lv_label_mode vs audio_uart_page_layout.
- a-53: TSV labels 0x55341c..0x5537cb are even_ai_animation.c (not text_stream_service.c). text_stream_current/pending_length return int32 (a-29 declares u16). Inventory holes 0x5540f0, 0x5540f8, 0x554102.
- a-56: g2/research/corpus/apollo-main/ghidra/pt-protocol/command-map.tsv is off by one (real map in a-55/a-56 comments). 0x20003838 is the NVDB record-pointer table. Existing names display_driver_case4_apply (0x4ca1ee, really uled_mspi_setBrightness) and display_driver_brightness_ratio_cell_4af73a (really SVC_NvdbGetSysData) are misleading.
- UNRESOLVED (wave-a50, 1671): ~1012 data symbols (348 RAM-suffixed + 664 g2_* no-addr) that nothing defines — needs a storage-definition pass (one .c per subsystem defining the RAM/ROM objects with recovered size/initialiser, .data initial values from the image); 482 code-suffixed callees (inventory holes / not yet written); 177 plain names (mostly Cordio/WSF API not yet compiled from upstream).
- a-54: inventory holes 0x5540f0/0x5540f8 (written in a-54), 0x554102 teleprompt_ui_pause_notify_send (unwritten). lv_bar.c 4 rows upstream.
- a-57: pt handler return types differ (a-55 extern u32, a-56 defs int32). ROM identity matrix 0x758e08 local static in pt_procsr_calib.c (data row?).
- a-58 DEDUPE: fmodf twice (audio_fmodf math.c, audio_uart_float_remainder_577c3c). math.c soft-float link:false vs stock hard-float entries. liblc3 0x590e64.. (lc3_frame_samples/bytes/setup_encoder/encode) upstream; existing audio_app_hardware_open_591374 is lc3_setup_encoder. SVC_PcmAppProcessData/SVC_PcmRecoderProcess return void (externs say int32). kvdbOnboardingConfigUpdateAndPersist returns status (g2_kvdb.h void).
- a-65: roundf_577d08 (a-65 extern) vs audio_roundf (math.c, soft-float, link:false) — stock is hard-float s0. FreeType ftgzip.c (zlib 1.1.4) unit exists experimentally on profile -16; needs -fno-inline. adler32 0x5BEEFC / zcfree 0x5BEFEC inventory holes. a-39 watchface ops fn_0c(hour,minute) arg order likely swapped.
- a-59: hal/uart/uart-rx-*/stream_buffer.c duplicates the FreeRTOS stream_buffer functions also anchored in transport_*.c/ring_*.c (dedupe). CLI handlers missing from inventory (see a-59 report list). at_core.c comment says 8 KiB AT stack; real 32 KiB.
- a-62: cmbacktrace cmb_fault.S (HardFault_Handler 0x5b0114, Fault_Loop 0x5b011c) needs an assembly upstream unit. g2_teleprompt_fsm_ctrl now defined in app/a-62-teleprompt/teleprompt_fsm.c. Existing name teleprompt_is_current_file_58a83e is really bounce_anim_is_running.
- a-66: LVGL upstream units spec in build/a-66/lv.sh (13 TUs, -fshort-enums -mfloat-abi=hard -fno-inline). Stock lv_draw_arc/line pre-#8070 (lvgl@b4fdabbdce), lv_chart pre-d6f147feb1 (lvgl@6e522e7579) — u-09 draw_series_line upstream claim inexact. IAR __LINE__ = last line of multi-line macro. 12 hand copies in ui/freetype/font-lru, font-rb to retire. LV_ASSERT_HANDLER recovered into lv_conf_recovered.h.
- a-64: temperature unit 1 = Celsius (existing comments saying 1 = Fahrenheit are wrong, 0x466512). Weekday key table 0x20004240 differs from 0x2000425c.
- codec-a-r1: GX8002 build banner board grus_gx8002b_dev_1v, build 2026-03-26 17:07:25, NationalChip; LDO trim table 0x1020aea2 (950..661 mV); aout dB table 0x1020a910 (-18..+18 dB). TSV row 0x10209C74 gx8002_uart_transmit_dma is bogus (interior of __udivdi3).
- codec-a-r2: image-A XIP rodata tail 0x1020B218..0x1020BE88 mislabeled as functions in codec TSV; crc_table 0x1020B908 upstream (nationalchip-lvp-kws crc32.c). Suspect TSV boundaries: 0x10209c74 swallows udivdi3 pool 0x10209dd4; 0x102093d8 belongs to gx8002_app_commands.
- a-60: FreeRTOS-Plus-CLI 43defa5 (5 rows, needs g2-patches/0001) + FlashDB fdb_utils.c/fdb.c (10 rows) upstream units. Callers use freertos_cli_register_command_5847ac / g2_flashdb_* names (alias). display_background_app_running_44349c / display_foreground_app_running_4434b4 are swapped (logs). 0x585120 IAR exit stub inventory hole. Fixed: _Stopfx endptr arg; sync_write DMA helpers exported as uart_sync_dma_{stop_584a64,start_584a38}.
- residual-r1: bootloader littlefs leaves (25) upstream via existing filesystem/upstream/lfs.c — needs -fno-inline on g2-apollo-bootloader-3. EasyLogger elog_utils.c elog_strcpy upstream (no unit). Stock bootloader elog.c is pinned a596b26 shifted +8 lines.
- LICENSE FLAG (for the user): g2/src/em9305 controller_init.c (opencfw_em9305_controller_initialize_stack 0x302a20, link_command_native 0x306a20, ll_record_release_request_3077b8 0x30b0f0) and initializer_lowers/init_packet_switch_known.c reconstruct proprietary Packetcraft/EM Bleu controller bodies; ~71 more packetcraft_modern_controller rows count as covered only via address mentions. Same open question as the other blocked libraries.
- a-63: conversate TSV names shifted by one around 0x5b5bf0..0x5b6688. common_fade_in_animation 0x58c238 third arg is completed_cb (existing def calls it start_alpha). Watchface manager weather arg 'fahrenheit' inverted (1 = Celsius).
- a-68 DEDUPE: 0x4b1588 (NemaGFX nema_enable_gradient) defined twice (display_driver_gpu_mode_mask_4b1588, display_driver_nema_cache_4b1588) — also part of the NemaGFX licence question. Ambiq LVGL port helpers lv_ambiq_gradient_create/dashline_create (gpu_patch.c, not in pinned ambiq-lvgl) written in graphics/a-68.
- x-03: inventory rows to add (start..end): 0x47ef74..0x47f0a0, 0x47f0a0..0x47f108, 0x4b29d8..0x4b29f8, 0x5bf0b4..0x5bf0bc, 0x5bf0bc..0x5bf114, 0x5ed0b8..0x5ed152, 0x5ed152..0x5ed1d6, 0x497db4..0x497dc0, 0x497dc0..0x497ddc, 0x497ddc..0x497de6, 0x55a350..0x55a558, 0x542d4c..0x542dc4, 0x554102..0x554170, 0x4e75b0..0x4e75e2, 0x4e75e2..0x4e7712, 0x4e7712..0x4e772c, 0x5b87ec..0x5b8844, 0x5b8844..0x5b8852, 0x5b8852..0x5b8860, 0x5b8880..0x5b8986, 0x5baa44..0x5baa76, 0x5bab24..0x5bab2c; upstream 0x44b068, 0x44b07e, 0x52a2d8, 0x52a32c, 0x52a38a, 0x5939ae, 0x5beefc, 0x5befec.
- x-03: main_config.c uses suffixed names for upstream fns (am_hal_sysctrl_fpu_enable_44b068, _stacking_enable_44b07e, app_version_info_set_5939ae=cm_backtrace_init, am_hal_wdt_restart_52a3da) — alias when upstream units land. Stock pwrctrl MCU mode switch 0x47ef74 is older than pinned SDK 5.1.0. Watchdog: LFRC/64, reset 480 (~30 s). cm_backtrace: code 0x438400..0x5fa056.
- a-67: lv_tabview.c (6) + lv_win.c (1) upstream, no unit yet. Inventory hole 0x5eca32 terminal_session_select_pack (unwritten). Reset handler TSV size wrong (spans 0x5e4232..0x5e4241). Brown-out reset triggers immediate SW POR (firmware policy). Stock build git describe master:v2.2.6.10-0-gb79923a139f5, Jul 6 2026 21:37:52.
- x-02: 71 CLI handlers + helpers written (inventory rows listed in x-02 report; all CLI handlers 0x57e3e6..0x584702 lack TSV rows). Hardware revision byte: 1 EVT1, 2 EVT2, 3 EVT3, 4 DVT1, 5 DVT2. XIP NOR window 0x80000000..0x81FFFFFF. Touch is CY8C4046FNI. JBD4010 panel die id 12 bytes. BoxDetect_SyncForceOutBox_4ac672 / kvdbOnboardingConfigUpdateAndPersist return values are used (defs void). EasyLogger elog_start/stop/set_filter_tag at 0x43d19a/0x43d1fc/0x43d406 (upstream).
- final-r2: all 64 mapped (40 upstream: TDK inv_imu_i2cm.c + Ict1531x.c, am_hal_adc.c main copy, npmx_ship.c, Cordio hci_cmd/hci_core_ps, ambiq-lvgl border/line; 19 blocked NemaGFX/NemaVG + nrf_fuel_gauge; 5 labels). TSV module g2-freetype-engine-census 0x514D2C..0x5179D0 is NemaGFX/NemaVG. TSV row 0x55F994 size bogus (192 KB; real 6 B). Ict1531x.c upstream unit needs stock wait_us 0x55D63C variant.
- final-r3: all 52 mapped (38 upstream: FreeType ftstroke/ftbitmap/psaux cf2_*, am_hal_uart 5.1.0 (-fshort-enums; hand copies in hal/uart/uart-tx/am_hal_uart.c to consolidate), npmx_errlog.c (rename externs npmx_retained_get_58ea08/read_58ea68), Cordio bstream, liblc3 v1.1.3 sns/tns/spec; 12 blocked NemaVG + nrf_fuel_gauge; 2 labels). TSV module cordio-ll-island 0x5D2418..0x5D6D98 is FreeType psaux.
- final-r1: 5 written, 16 anchored, 72 upstream (liblc3 ltpf/bits, FreeRTOS port/timers, CMSIS-RTOS2, am_hal_timer/cachectrl/secure_ota/pwrctrl/spotmgr/gpio, LVGL 17), 15 blocked nrf_fuel_gauge. am_hal_pwrctrl.c is older than 5.1.0 (can't build as pinned file). Missing TSV rows: accu_load 0x439b78, resample_16k_12k8 0x438400, resample_48k_12k8 0x438604. 0x480826 has three names.
