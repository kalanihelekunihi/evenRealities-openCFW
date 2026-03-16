/*
 * G2 Main Firmware - Annotated Key Functions
 * Base: 0x00438000, ARM Cortex-M55 (Ambiq Apollo510b)
 * Source: Ghidra headless decompilation + manual annotation
 *
 * Naming convention:
 *   FUN_XXXXXXXX → original Ghidra name
 *   elog_*       → EasyLogger framework
 *   pb_*         → Protocol Buffer service handlers
 *   ble_*        → BLE communication layer
 *   pt_*         → Protocol transport (OTA)
 *   SVC_*        → System services
 *   DAT_*        → Global data references
 *   PTR_s_*      → String literal references
 */

/* ========================================================================
 * LOGGING INFRASTRUCTURE (EasyLogger)
 * ======================================================================== */

/*
 * elog_output (FUN_0043ccc8) - Main log output function
 * Called 9083 times across firmware. First param is a bitmask of log levels.
 *
 * @param level_mask  Bitmask: bit31=error, bit30=warn, bit29=info, bit28=debug (approx)
 * @param format      Format string (PTR_s_ reference)
 * @param ...         Printf-style variadic args
 *
 * Pattern: Always preceded by elog_level_check() to avoid formatting overhead.
 */
/* 0x0043ccc8  elog_output */

/*
 * elog_assert_trace (FUN_0043d1c8) - Debug trace with source location
 *
 * @param level       Log level (1=error, 2=warn, 3=info, 4=debug)
 * @param module      Module name string (e.g., "pb_conversate")
 * @param source_file Source file path (e.g., "D:\01_workspace\...\pb_service_conversate.c")
 * @param func_name   Function name string
 * @param line_num    Source line number (hex in code, e.g., 0x55 = line 85)
 * @param ...         Additional context values
 */
/* 0x0043d1c8  elog_assert_trace */

/*
 * elog_level_check (FUN_0043cd6c) - Check if current log level allows output
 *
 * @return  Bitmask of active levels. Callers test with bit shifts:
 *          (ret << 0x1e < 0) → debug level active
 *          (ret << 0x1f < 0) → info level active
 *          (ret << 0x1d < 0) → warn level active
 */
/* 0x0043cd6c  elog_level_check */


/* ========================================================================
 * BLE MESSAGE LAYER
 * ======================================================================== */

/*
 * ble_msgtx_send (FUN_0046f6ca) - Send BLE protobuf message
 *
 * Primary TX function for all protobuf service responses.
 * Checks connection state before sending.
 *
 * @param pipe        BLE pipe (0=EUS control, 1=EUS data)
 * @param service_id  Service ID byte (e.g., 0x0B=conversate, 0x07=evenai)
 * @param data        Encoded protobuf data pointer
 * @param length      Data length (masked to 16-bit)
 * @return            0=success, 8=not connected, other=error
 *
 * Call chain: ble_msgtx_send → ble_msgtx_send_impl (FUN_0046f0fe) → BLE stack
 */
/* 0x0046f6ca  ble_msgtx_send */
/* See decompiled.c for full implementation */


/* ========================================================================
 * PROTOBUF SERVICE: CONVERSATE (0x0B-20)
 * Source: platform\protocols\pb_service_conversate\pb_service_conversate.c
 * ======================================================================== */

/*
 * pb_service_conversate_handler (FUN_00592fde)
 *
 * Handles incoming conversate commands on service 0x0B-20.
 * Builds COMM_RSP response and sends via BLE.
 *
 * @param cmd_data  Pointer to received command type (uint16). NULL = error.
 * @return          0=success, 5=encode fail, 6=null input
 *
 * Response format:
 *   byte[0] = 0xA1 (161 = COMM_RSP marker)
 *   byte[1] = glasses_counter + 1 (message ID)
 *   byte[2:3] = 8 (status flags)
 *   byte[4:5] = *cmd_data (echo of received command type)
 *
 * After encoding, sends via: ble_msgtx_send(1, 0x0B, data, len)
 *
 * Key internals:
 *   DAT_0059330c = response buffer pointer (0x1D6C = 7532 bytes)
 *   DAT_005932e8 = glasses-side message counter
 *   FUN_004a2278  = protobuf_stream_init(stream, descriptor, max_size)
 *   FUN_00439c04  = protobuf_ostream_init(ostream, stream, capacity)
 *   FUN_004a28b6  = pb_encode_28b6(ostream, fields_desc, data) → bool
 */
/* 0x00592fde  pb_service_conversate_handler */


/*
 * conversate_fsm_handler (FUN_005934cc) - Conversate state machine
 *
 * Module: [conversate.fsm]
 * Handles state transitions for conversate feature:
 *   NONE(0) → START(1) → active → PAUSE(2) / RESUME(3) → CLOSE(4)
 *   CONFIG(5) = configuration update
 *
 * Log strings reveal parameters:
 *   "conversate app open - summary_and_tag: %d, transcribe: %d,
 *    auto_pop_en: %d, use_audio: %d, cue_duration: %d"
 *   "conversate app config - summary_and_tag: %d, transcribe: %d,
 *    auto_pop_en: %d, use_audio: %d, cue_duration: %d"
 */
/* 0x005934cc  conversate_fsm_handler */


/* ========================================================================
 * PROTOBUF SERVICE: NOTIFICATION (0x02-20)
 * Source: platform\protocols\pb_service_notification\pb_service_notification.c
 * ======================================================================== */

/*
 * pb_service_notification_handler (FUN_004ebb9c)
 *
 * Handles incoming notification commands on service 0x02-20.
 *
 * @param data     Raw protobuf data
 * @param length   Data length
 * @param param_3  Context (unused?)
 * @param param_4  Context (unused?)
 * @return         0=success, 2=null data, 0x2B=decode fail
 *
 * Command dispatch (via command_id = first decoded byte):
 *   command_id 1 → pb_notif_decode (FUN_004ebd84) + pb_notif_process (FUN_004ebe76)
 *                   = Notification display control
 *   command_id 3 → pb_notif_whitelist_decode (FUN_004ec39a) + pb_notif_whitelist_send (FUN_004ec450)
 *                   = Notification whitelist management
 *
 * Decoding pipeline:
 *   FUN_00482358 = memset(dest, 0, 0x4C) - clear decode buffer (76 bytes)
 *   FUN_004a380c = protobuf_istream_from_buffer(istream, data, len)
 *   FUN_00439c04 = protobuf_ostream_init(ostream, istream, 0x10)
 *   FUN_004a4490 = pb_decode_4490(istream, fields_desc, &output_struct) → bool
 */
/* 0x004ebb9c  pb_service_notification_handler */


/* ========================================================================
 * PROTOBUF SERVICE: TELEPROMPTER (0x06-20)
 * Source: platform\protocols\pb_service_teleprompt\pb_service_teleprompt.c
 * ======================================================================== */

/*
 * pb_service_teleprompt_handler (FUN_0054ccaa)
 *
 * Handles teleprompter commands on service 0x06-20.
 *
 * @param msg_id   Message ID from phone
 * @param data     Protobuf-encoded command data
 * @return         0=success, 5=encode fail, 6=null
 *
 * Response format:
 *   byte[0] = 0xA6 (166) ← matches our observed f1=0xA6 ACK
 *   byte[1] = msg_id (echo)
 *   byte[2:3] = 0x0C (12)
 *   byte[4] = *data (command echo)
 *
 * Response buffer: DAT_0054d218 (0xF58 = 3928 bytes)
 *
 * Teleprompter parameters (from FSM strings):
 *   mode, start_page, start_line, total_pages, total_lines,
 *   display_width, scroll_interval_ms, countdown_seconds, use_audio
 *
 * Scroll progress: "scrollbar set: page_id=%d, line_id=%d,
 *   line_in_total=%d/%d, visible_lines=%d, scrollable_lines=%d, y_pos=%d/%d"
 */
/* 0x0054ccaa  pb_service_teleprompt_handler */


/* ========================================================================
 * PROTOBUF SERVICE: TRANSLATE (0x05-20)
 * Source: platform\protocols\pb_service_translate\pb_service_translate.c
 * ======================================================================== */

/*
 * pb_service_translate_handler (FUN_005b49c2)
 *
 * Handles translate commands on service 0x05-20.
 * Uses magic_random for deduplication:
 *   "[pb.translate]command_id: %d, magic number = %d, last magic number = %d"
 *
 * Response: G2TranslateResponse (f1=cmd_type echo, f1=161 COMM_RSP)
 */
/* 0x005b49c2  pb_service_translate_handler */


/* ========================================================================
 * PROTOBUF SERVICE: EVEN AI (0x07-20)
 * Source: platform\protocols\pb_service_even_ai\pb_service_even_ai.c
 * ======================================================================== */

/*
 * pb_service_even_ai_handler (FUN_004ee854)
 *
 * Master handler for EvenAI commands on service 0x07-20.
 * Dispatches to type-specific handlers:
 *
 *   Type 1 (CTRL)    → pb_evenai_ctrl (FUN_004ee9e0)
 *   Type 3 (ASK)     → pb_evenai_ask (FUN_004eeb72)
 *   Type 4 (ANALYSE) → pb_evenai_analyse (FUN_004eec42)
 *   Type 5 (REPLY)   → pb_evenai_reply (FUN_004ef50c)
 *   Type 6 (SKILL)   → pb_evenai_skill (FUN_004ef5f8)
 *   Type 7 (PROMPT)  → pb_evenai_prompt (FUN_004efae0)
 *   Type 8 (EVENT)   → pb_evenai_event (FUN_004efd78)
 *   Type 9 (HB)      → (heartbeat, inline)
 *   Type 10 (CONFIG) → (config, inline)
 *
 * Guard conditions (from string):
 *   "warn: can not ctrl evenai, product_mode = %d, ota_status = %d,
 *    voice_switch = %d, onboarding_status = %d, calibration_ui_status = %d"
 *
 * APP_PbNotifyEncodeEvenAIEvent (FUN_004eff10):
 *   Encodes EvenAI events for BLE notification.
 *   COMM_RSP: f12.f1=7 for EvenAI, f12.f1=8 for EvenHub
 */
/* 0x004ee854  pb_service_even_ai_handler */


/* ========================================================================
 * PROTOBUF SERVICE: SETTINGS (0x0D-00/0x0D-20)
 * Source: platform\protocols\pb_service_setting\pb_service_setting.c
 * ======================================================================== */

/*
 * The settings service is the most complex, handling:
 *
 * Decode: "[pb_service_setting]decode successful: command_id = %d, which_command_data = %d"
 *
 * Features (from debug strings):
 *   - Brightness: auto_brightness_switch, auto_brightness_level, y/x_coordinate_level
 *   - Head-up: head_up_switch, head_up_angle, head_up_angle_calibration
 *   - Silent mode: toggle + timeout with RequestDisplayReflash
 *   - Gesture config: screen_off=[type1,type2,type3], screen_on=[type1,type2,type3]
 *   - Universal settings: metric_unit, date_format, distance_unit, temperature_unit,
 *                        time_format, dominant_hand
 *   - Unread message count
 *   - Recalibration status
 *
 * Deduplication: magic_random field
 * Response types: [Response APP], [Send Local Data], [Respond Local Data], [Notify]
 *
 * setting_notify_device_status (FUN_004aaee4):
 *   Pushes device status notifications to phone.
 */


/* ========================================================================
 * SYSTEM CLOSE (0x22-20)
 * ======================================================================== */

/*
 * system_close_handler (FUN_005b83e2)
 *
 * Handles system close dialog on service 0x22-20.
 * Response: selection = YES(1) / NO(2) / MINIMIZE(3)
 *
 * Module tag: [system_close]
 */
/* 0x005b83e2  system_close_handler */


/* ========================================================================
 * PROTOBUF ENCODING/DECODING HELPERS
 * ======================================================================== */

/*
 * These functions form the nanopb-like protobuf codec used throughout:
 *
 * FUN_004a2278 = pb_stream_init(stream, descriptor, max_size)
 *   Initialize a protobuf output stream with field descriptor
 *
 * FUN_00439c04 = pb_ostream_init(ostream, buffer, capacity)
 *   Create output stream from buffer
 *
 * FUN_004a28b6 = pb_encode_28b6(ostream, fields, data) → bool
 *   Encode struct to protobuf. Returns 1 on success.
 *
 * FUN_004a380c = pb_istream_from_buffer(istream, data, len)
 *   Create input stream from received data buffer
 *
 * FUN_004a4490 = pb_decode_4490(istream, fields, dest) → bool
 *   Decode protobuf into struct. Returns 1 on success.
 *
 * FUN_00482358 = memset(ptr, 0, size)
 *   Clear buffer before decode
 *
 * FUN_0043c0e4 = memset(ptr, fill, size)
 *   General memory fill (used to clear response buffers)
 */


/* ========================================================================
 * CONVERSATE UI MODULE
 * ======================================================================== */

/*
 * conversate_ui layout parameters (from strings):
 *   main_page_display_height, extend_page_display_height,
 *   transcribe_display_height, auto_pop_en, cue_duration
 *
 * conversate_ui components:
 *   FUN_0058f278 = conversate_ui_init
 *   FUN_0058f2da = conversate_ui_create
 *   FUN_0058f43a = conversate_ui_update
 *   FUN_0058f50a = conversate_ui_destroy
 *   FUN_0058f676 = conversate_ui_event_handler
 *   FUN_0058fef4 = conversate_calculate_auto_duration
 *   FUN_00590ba0 = conversate_ui_text_height_calc
 *   FUN_00591314 = conversate_ui_layout_engine
 *   FUN_0059179c = conversate_ui_tag_display
 *   FUN_00591a20 = conversate_ui_keypoint_display
 *   FUN_00592018 = conversate_ui_title_display
 *   FUN_00592930 = conversate_ui_container_setup
 */


/* ========================================================================
 * TELEPROMPTER TIMER MODULE
 * ======================================================================== */

/*
 * Timer functions for teleprompter auto-scroll:
 *   FUN_0056b018 = teleprompt_timer_auto_scroll_start
 *   FUN_0056b0d8 = teleprompt_timer_countdown_start
 *   FUN_0056b234 = teleprompt_timer_start_by_config
 *   FUN_0056b286 = teleprompt_timer_stop_by_config
 *
 * pt_ prefix functions (teleprompter protocol transport):
 *   pt_action_scroll_sync  - Inter-eye scroll synchronization
 *   pt_action_ai_sync      - AI mode sync between eyes
 *   pt_action_app_resume   - Resume after background
 *   pt_action_app_start    - Start teleprompter
 *   pt_action_heartbeat    - Teleprompter heartbeat
 *   pt_action_page_data    - Page data transfer
 *   pt_preload_start       - Preload page data
 *   pt_request_display     - Request display activation
 *   pt_request_page_data   - Request page from phone
 */


/* ========================================================================
 * BUZZER DRIVER
 * ======================================================================== */

/*
 * drv_buzzer (FUN_004d7e54 region) - Piezo buzzer driver
 *
 * Module: [drv.buzzer]
 *
 * Play types (0-10, confirmed from CLI help):
 *   0 = touch key
 *   1 = clock alarm
 *   2 = phone call
 *   3 = test1
 *   4 = test2
 *   5 = single click
 *   6 = double click
 *   7 = long press
 *   8 = swipe left
 *   9 = swipe right
 *   10 = wear
 *
 * Musical note API:
 *   DRV_BuzzerPlayNote(note, tone, beat)
 *     note: 1-7 (do,re,mi,fa,sol,la,si), 0=silence
 *     tone: 0=low, 1=middle, 2=high, 3=super high
 *     beat: quarter-beat units
 *
 * Internal: _buzzerPlayStart(times, interval), _buzzerPlayVoice
 * Queue: DRV_BuzzerPlayAfterQueue (type range check: 0-10)
 */


/* ========================================================================
 * SENSOR: AMBIENT LIGHT (ALS)
 * ======================================================================== */

/*
 * sensor_als_polling (FUN_004f5e02)
 * Module: [sensor_als]
 *
 * Polling string: "ALS polling, als_value:%d, peak_value:%d,
 *   brightness_level_converted:%d, current_brightness_level:%d"
 *
 * Connected to: SVC_Settings_AutoBrightnessOpen/Close
 * Output: SVC_Settings_BrightnessLevelToLumAndCurrent
 */


/* ========================================================================
 * DISPLAY DRIVER: JBD4010
 * ======================================================================== */

/*
 * Module: [driver.jbd4010]
 *
 * FUN_00596f60 = jbd4010_init / jdb4010_configure
 * FUN_005970fc = jbd4010_status_recovery
 * FUN_00597270 = am_devices_jbd4010_status_check
 *
 * Display: 576x288 Gray4, monoscopic micro-OLED
 * Interface: MSPI (via JBD4010 controller)
 */


/* ========================================================================
 * CODEC HOST: GX8002B
 * ======================================================================== */

/*
 * Module: [codec.host]
 *
 * FUN_004dcd44 = codec_host_init
 * FUN_004dd4b4 = codec_host_message_handler
 *
 * Protocol: TinyFrame serial
 *   Pack: "cmd=0x%04X(NR=0x%02X, TYPE=0x%02X), seq=0x%02X,
 *          flags=0x%02X, length=%d, crc32=0x%08X"
 *   Unpack: same format
 *   Response: same format
 *
 * Voice events: "voice event: cmd_id=0x%04X, event_id=0x%04X"
 *
 * Control:
 *   SVC_CodecDMICOpen  - Enable digital microphone
 *   SVC_CodecDMICClose - Disable digital microphone
 *   SVC_CodecDfu       - Firmware update
 *   SVC_CodecCheckAndUpgrade - Auto-check and upgrade
 *   SVC_I2SOutputCtrl  - I2S audio output
 *   SVC_Lc3EncodeMono  - LC3 audio encoding
 */


/* ========================================================================
 * SESSION 5 DISCOVERIES - Library Identification (71.8% coverage)
 * ======================================================================== */

/*
 * zlib inflate (FUN_005a3cc4) - Decompression entry point
 * Identified by error strings: "incorrect header check", "unknown compression method",
 * "need dictionary", "invalid window size"
 *
 * Used for: OTA firmware decompression, possibly asset decompression
 * Related: zlib_inflate_table (FUN_005a31d4), zlib_inflate_codes (FUN_005a2b28)
 */

/*
 * FreeType font engine
 *
 * FT_Add_Module (FUN_005c0a48) - Module registration
 *   Strings: "metrics-variations", "multi-masters", "postscript-cmaps", "sfnt", "truetype"
 *   Registers font format handlers at init time
 *
 * ft_face_init (FUN_0057e1d0) - Font face initialization
 *   Strings: "Bold", "pshinter", "sfnt"
 *   Parses font tables, sets up rendering pipeline
 *
 * ft_var_get_axes (FUN_005cf61e) - Variable font axis enumeration
 *   Strings: "OpticalSize", "Slant", "Weight", "Width"
 *   G2 uses variable fonts for UI text with weight/width control
 *
 * lv_freetype_font_create (FUN_004b8114) - LVGL-FreeType bridge
 *   Creates LVGL font objects backed by FreeType rendering
 *   LVGL assert-named (HIGH confidence)
 *
 * ~57 additional FreeType internal functions identified by call patterns
 * (calling lvgl_lv_freetype_internal_* and teleprompt_render_internal_*)
 */

/*
 * NemaGFX GPU rendering pipeline
 *
 * 8+ functions identified calling lv_draw_ambiq_arc_internal and
 * lv_draw_ambiq_triangle_internal. These are the Ambiq-specific GPU
 * acceleration layer for LVGL drawing operations using the NemaGFX engine.
 *
 * Largest: FUN_00507764 (9322B), FUN_0050a770 (8300B)
 * These implement the GPU-accelerated arc and triangle rasterizers.
 */

/*
 * LVGL v9.3 - Additional named functions (from assert strings)
 *
 * lv_obj_class_create_obj (FUN_0044b458) - Widget instantiation
 * lv_event_add (FUN_0044e5a4) - Event handler registration
 * lv_timer_create (FUN_0046be52) - Software timer creation
 * lv_draw_buf_create_ex (FUN_00483ecc) - Draw buffer allocation
 *
 * 20 lv_chart_* functions identified by call patterns:
 *   lv_chart_draw_arc, lv_chart_draw_line, lv_chart_draw_label,
 *   lv_chart_draw_rect, lv_chart_internal
 *   Used for health data visualization (heart rate, SpO2, steps graphs)
 */

/*
 * sensor_hub_calibrate (FUN_0051fb20) - IMU/sensor calibration
 * Strings: "calib", "close", "matrix", "mode", "open"
 * Calls: sensor_hub_process, sensor_hub_report, display_mutex_acquire
 * Manages ICM-45608 IMU calibration and sensor fusion processing
 */

/*
 * drv_opt_handler (FUN_004d9df8) - OPT3007 Ambient Light Sensor Driver
 * Strings: "drv.opt.r", "ti_opt3007_assignRegistermap"
 * EasyLogger module tag: [drv.opt]
 * The TI OPT3007 measures ambient light for auto-brightness control.
 * Cross-references: ALSSyncHandler (brightness sync) in main firmware strings.
 */

/*
 * UI Event Handlers (from LVGL widget analysis)
 *
 * message_notify_ui_event (FUN_004eda08) - Notification display events
 * stock_ext_event_handler (FUN_0054fc18) - Dashboard stock widget events
 * quicklist_widget_event (FUN_0055bd50) - Quicklist/task list widget events
 * health_widget_event (FUN_0055d4f8) - Health dashboard widget events
 * health_ext_event (FUN_0055e3b4) - Health extended view events
 *
 * These are registered via LVGL's event system and called during
 * widget state changes (click, scroll, value change, etc.)
 */

/* ========================================================================
 * SESSION 5 ANALYSIS SUMMARY
 * ========================================================================
 *
 * Coverage: 7,268 / 7,278 functions (99.9% mapped, 100% specifically named)
 *
 * Module distribution (top 10):
 *   LVGL UI library:    1,064 functions (widget rendering, events, layout)
 *   Third-party libs:     885 functions (FreeType, zlib, FlashDB, NemaGFX)
 *   BLE stack:            563 functions (Cordio DM/SMP/ATT/HCI, WSF)
 *   Protocol handlers:    182 functions (18 protobuf service handlers)
 *   Application layer:    166 functions (UI pages, state machines)
 *   Hardware drivers:     143 functions (MSPI, I2C, GPIO, OPT3007, IMU)
 *   RTOS framework:       128 functions (FreeRTOS, CMSIS-RTOS2 wrappers)
 *
 * Key negative result: Cross-binary function size matching (bootloader
 * to main firmware) is unreliable — only 20% match rate for known LittleFS
 * functions due to different compiler optimization levels between images.
 *
 * === SESSION 6: Callee-pattern + reverse-caller + string-reference analysis ===
 * Added 276 more functions (5,672 → 5,948, 81.7% coverage):
 *   Callee-pattern:   196 functions (calling 2+ named APIs from same library)
 *   Reverse-caller:    52 functions (80%+ of callers from one module)
 *   String-reference:  28 functions (DAT_ addresses resolving to identifiable strings)
 *
 * Notable string-identified functions:
 *   0x0056d5ec  systemClose_ui_event_handler  (strings: ID_GENERAL_CONFIRMATION_POPUP)
 *   0x004ee30c  even_ai_common_timer_mgr_deinit (exact function name in string)
 *   0x00574190  at_core_init               (strings: AT_CoreInit[%d], AT^NUS)
 *   0x005956f8  gx8002b_i2s_deinit         (string: gx8002b i2s already deinit)
 *   0x004c9f78  tlsf_block_free_assert     (strings: block must be free)
 *   0x004c9ec4  tlsf_thread_notification   (string: thread_notification.c)
 *   0x004d6ce4  audio_frame_decode         (string: frame_samples=%d, nbytes=%d)
 *   0x0051f2b8  ota_progress_log           (string: progress %d%%)
 *   0x005d6124  rtos_deadlock_detect       (string: possible deadlock or timeout)
 *
 * Ghidra/rizin scripts generated: tools/ghidra_scripts/apply_function_names.py/.r2
 *
 * === SESSION 7: Vtable + wrapper + neighbor + call-graph convergence ===
 * Added 460 more functions (5,966 → 6,426, 88.3% coverage):
 *   Vtable entries:      25 (function pointer tables in firmware binary)
 *   Class structures:    12 (FreeType module constructor/destructor pairs)
 *   Wrapper functions:  177 (small functions calling exactly one named function)
 *   Call-graph prop:     85 (iterative 100%-consensus callee+caller propagation)
 *   Neighbor consensus: 161 (unmapped functions between same-module neighbors)
 *
 * Session 7 continued: Agent callee-only call-graph propagation added 348 more,
 * final neighbor consensus pass added 54 more. Total session 7: +862 functions.
 *
 * Session 8 (450 entries): Relaxed consensus (32), FreeType TT_RunIns dispatch
 * analysis (10 new + 230 name upgrades to proper opcode names), two-hop call
 * graph propagation with 7 iterative rounds (337), deep manual analysis of
 * final 71 holdouts (MSPI DMA, FreeRTOS heap, libc math, NVIC, LVGL anim).
 *
 * COMPLETE: 7,278 / 7,278 mapped (100.0%). Every function in the firmware named.
 * Key final identifications: sqrtf (69 callers), NVIC_SetPriority (209 callers),
 * lv_anim_start (86 callers), FT_MulDiv (75 callers), pvPortMalloc, 19 MSPI DMA
 * register-level driver functions, 119 TrueType bytecode opcode handlers.
 */
