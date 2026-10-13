.syntax unified
.thumb
.section .note.GNU-stack,"",%progbits
.section .vectors,"a"
.word 0x2007ff00
.word probe_stop
.rept 14
.word probe_stop
.endr
.section .reset,"ax"
.global probe_stop
.thumb_func
probe_stop: b .
.section .native_main,"ax"
.incbin "/Users/kalani/Repo/evenRealities-openCFW/g2/analysis/c-source-completion-20261011/peripherals/root-lvgl-refr-size-native-round339/oracle-data-bound.bin"
.section .text.controlled_children,"ax"
.global audio_uart_lvgl_log
.thumb_func
audio_uart_lvgl_log: bx lr
.global audio_uart_lv_obj_parent_44dca2
.thumb_func
audio_uart_lv_obj_parent_44dca2: bx lr
.global audio_uart_lv_obj_width_43fd9e
.thumb_func
audio_uart_lv_obj_width_43fd9e: bx lr
.global audio_uart_lv_obj_height_43fdda
.thumb_func
audio_uart_lv_obj_height_43fdda: bx lr
.global audio_uart_lv_style_width_43eea6
.thumb_func
audio_uart_lv_style_width_43eea6: bx lr
.global audio_uart_lv_style_min_width_43eeb0
.thumb_func
audio_uart_lv_style_min_width_43eeb0: bx lr
.global audio_uart_lv_style_max_width_43eeba
.thumb_func
audio_uart_lv_style_max_width_43eeba: bx lr
.global audio_uart_lv_style_height_43eec4
.thumb_func
audio_uart_lv_style_height_43eec4: bx lr
.global audio_uart_lv_style_min_height_43eece
.thumb_func
audio_uart_lv_style_min_height_43eece: bx lr
.global audio_uart_lv_style_max_height_43eed8
.thumb_func
audio_uart_lv_style_max_height_43eed8: bx lr
.global audio_uart_lv_obj_content_width_43fe16
.thumb_func
audio_uart_lv_obj_content_width_43fe16: bx lr
.global audio_uart_lv_obj_content_height_43fe70
.thumb_func
audio_uart_lv_obj_content_height_43fe70: bx lr
.global audio_uart_lv_calc_content_width_440a3c
.thumb_func
audio_uart_lv_calc_content_width_440a3c: bx lr
.global audio_uart_lv_calc_content_height_440c2e
.thumb_func
audio_uart_lv_calc_content_height_440c2e: bx lr
.global audio_uart_lv_style_pad_left_43efc6
.thumb_func
audio_uart_lv_style_pad_left_43efc6: bx lr
.global audio_uart_lv_style_pad_right_43eff4
.thumb_func
audio_uart_lv_style_pad_right_43eff4: bx lr
.global audio_uart_lv_style_pad_top_43f022
.thumb_func
audio_uart_lv_style_pad_top_43f022: bx lr
.global audio_uart_lv_style_pad_bottom_43f050
.thumb_func
audio_uart_lv_style_pad_bottom_43f050: bx lr
.global audio_uart_lv_style_margin_left_43ef84
.thumb_func
audio_uart_lv_style_margin_left_43ef84: bx lr
.global audio_uart_lv_style_margin_right_43ef8e
.thumb_func
audio_uart_lv_style_margin_right_43ef8e: bx lr
.global audio_uart_lv_style_margin_top_43ef70
.thumb_func
audio_uart_lv_style_margin_top_43ef70: bx lr
.global audio_uart_lv_style_margin_bottom_43ef7a
.thumb_func
audio_uart_lv_style_margin_bottom_43ef7a: bx lr
.global audio_uart_lv_clamp_width_4408d6
.thumb_func
audio_uart_lv_clamp_width_4408d6: bx lr
.global audio_uart_lv_clamp_height_440968
.thumb_func
audio_uart_lv_clamp_height_440968: bx lr
.global audio_uart_display_size_changed
.thumb_func
audio_uart_display_size_changed: bx lr
.global audio_uart_lv_obj_coords_43fc2a
.thumb_func
audio_uart_lv_obj_coords_43fc2a: bx lr
.global audio_uart_lv_obj_content_coords_43feca
.thumb_func
audio_uart_lv_obj_content_coords_43feca: bx lr
.global audio_uart_lv_area_contains_450f28
.thumb_func
audio_uart_lv_area_contains_450f28: bx lr
.global audio_uart_lv_scrollbar_invalidate_44f2ca
.thumb_func
audio_uart_lv_scrollbar_invalidate_44f2ca: bx lr
.global audio_uart_lv_style_base_dir_43efba
.thumb_func
audio_uart_lv_style_base_dir_43efba: bx lr
.global audio_uart_lv_obj_event_451670
.thumb_func
audio_uart_lv_obj_event_451670: bx lr
.global audio_uart_lv_refresh_draw_452d42
.thumb_func
audio_uart_lv_refresh_draw_452d42: bx lr
