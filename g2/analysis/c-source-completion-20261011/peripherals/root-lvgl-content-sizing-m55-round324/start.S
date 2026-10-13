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
.global audio_uart_lv_obj_x_44e486
.thumb_func
audio_uart_lv_obj_x_44e486: bx lr
.global audio_uart_lv_obj_y_44e498
.thumb_func
audio_uart_lv_obj_y_44e498: bx lr
.global audio_uart_lv_child_count_44ddea
.thumb_func
audio_uart_lv_child_count_44ddea: bx lr
.global audio_uart_lv_obj_has_flag_any_43e11c
.thumb_func
audio_uart_lv_obj_has_flag_any_43e11c: bx lr
.global audio_uart_lv_layout_positioned_43f612
.thumb_func
audio_uart_lv_layout_positioned_43f612: bx lr
.global audio_uart_lv_self_width_43ff44
.thumb_func
audio_uart_lv_self_width_43ff44: bx lr
.global audio_uart_lv_self_height_43ff5e
.thumb_func
audio_uart_lv_self_height_43ff5e: bx lr
.global audio_uart_lv_style_x_43eee2
.thumb_func
audio_uart_lv_style_x_43eee2: bx lr
.global audio_uart_lv_style_y_43eeec
.thumb_func
audio_uart_lv_style_y_43eeec: bx lr
.global audio_uart_lv_style_align_43eef6
.thumb_func
audio_uart_lv_style_align_43eef6: bx lr
.global audio_uart_lv_style_base_dir_43efba
.thumb_func
audio_uart_lv_style_base_dir_43efba: bx lr
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
.global audio_uart_lv_area_width_451598
.thumb_func
audio_uart_lv_area_width_451598: bx lr
.global audio_uart_lv_area_height_4515a4
.thumb_func
audio_uart_lv_area_height_4515a4: bx lr
