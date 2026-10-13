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
.incbin "/tmp/opencfw-main-native.bin"
.section .text.controlled_children,"ax"
.global audio_uart_lv_area_set_450b5c
.thumb_func
audio_uart_lv_area_set_450b5c: bx lr
.global audio_uart_lv_obj_has_flag_43e0e0
.thumb_func
audio_uart_lv_obj_has_flag_43e0e0: bx lr
.global audio_uart_lv_get_scrollbar_mode_44e42c
.thumb_func
audio_uart_lv_get_scrollbar_mode_44e42c: bx lr
.global audio_uart_lv_input_next_452edc
.thumb_func
audio_uart_lv_input_next_452edc: bx lr
.global audio_uart_lv_input_scroll_object_452fae
.thumb_func
audio_uart_lv_input_scroll_object_452fae: bx lr
.global audio_uart_lv_input_scroll_direction_452f8c
.thumb_func
audio_uart_lv_input_scroll_direction_452f8c: bx lr
.global audio_uart_lv_obj_y_44e498
.thumb_func
audio_uart_lv_obj_y_44e498: bx lr
.global audio_uart_lv_scroll_bottom_44e4bc
.thumb_func
audio_uart_lv_scroll_bottom_44e4bc: bx lr
.global audio_uart_lv_scroll_left_44e586
.thumb_func
audio_uart_lv_scroll_left_44e586: bx lr
.global audio_uart_lv_scroll_right_44e67a
.thumb_func
audio_uart_lv_scroll_right_44e67a: bx lr
.global audio_uart_lv_get_scroll_dir_44e442
.thumb_func
audio_uart_lv_get_scroll_dir_44e442: bx lr
.global audio_uart_lv_style_base_dir_43efba
.thumb_func
audio_uart_lv_style_base_dir_43efba: bx lr
.global audio_uart_lv_style_raw_pad_top_44e230
.thumb_func
audio_uart_lv_style_raw_pad_top_44e230: bx lr
.global audio_uart_lv_style_raw_pad_bottom_44e23a
.thumb_func
audio_uart_lv_style_raw_pad_bottom_44e23a: bx lr
.global audio_uart_lv_style_raw_pad_left_44e244
.thumb_func
audio_uart_lv_style_raw_pad_left_44e244: bx lr
.global audio_uart_lv_style_raw_pad_right_44e24e
.thumb_func
audio_uart_lv_style_raw_pad_right_44e24e: bx lr
.global audio_uart_lv_style_width_43eea6
.thumb_func
audio_uart_lv_style_width_43eea6: bx lr
.global audio_uart_lv_style_length_44e226
.thumb_func
audio_uart_lv_style_length_44e226: bx lr
.global audio_uart_lv_obj_height_43fdda
.thumb_func
audio_uart_lv_obj_height_43fdda: bx lr
.global audio_uart_lv_obj_width_43fd9e
.thumb_func
audio_uart_lv_obj_width_43fd9e: bx lr
.global audio_uart_lv_style_background_opacity_44e276
.thumb_func
audio_uart_lv_style_background_opacity_44e276: bx lr
.global audio_uart_lv_style_border_opacity_44e282
.thumb_func
audio_uart_lv_style_border_opacity_44e282: bx lr
.global audio_uart_lv_display_dpi_44fbe6
.thumb_func
audio_uart_lv_display_dpi_44fbe6: bx lr
