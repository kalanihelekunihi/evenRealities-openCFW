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
.incbin "/Users/kalani/Repo/evenRealities-openCFW/g2/analysis/c-source-completion-20261011/peripherals/root-lvgl-scroll-extents-native-round337/oracle-data-bound.bin"
.section .text.controlled_children,"ax"
.global audio_uart_lv_child_count_44ddea
.thumb_func
audio_uart_lv_child_count_44ddea: bx lr
.global audio_uart_lv_obj_has_flag_any_43e11c
.thumb_func
audio_uart_lv_obj_has_flag_any_43e11c: bx lr
.global audio_uart_lv_style_property_44bdea
.thumb_func
audio_uart_lv_style_property_44bdea: bx lr
.global audio_uart_lv_obj_event_451670
.thumb_func
audio_uart_lv_obj_event_451670: bx lr
.global audio_uart_lv_obj_width_43fd9e
.thumb_func
audio_uart_lv_obj_width_43fd9e: bx lr
.global audio_uart_lv_obj_height_43fdda
.thumb_func
audio_uart_lv_obj_height_43fdda: bx lr
.global audio_uart_lv_obj_x_44e486
.thumb_func
audio_uart_lv_obj_x_44e486: bx lr
.global audio_uart_lv_obj_y_44e498
.thumb_func
audio_uart_lv_obj_y_44e498: bx lr
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
.global audio_uart_lvgl_log
.thumb_func
audio_uart_lvgl_log: bx lr
