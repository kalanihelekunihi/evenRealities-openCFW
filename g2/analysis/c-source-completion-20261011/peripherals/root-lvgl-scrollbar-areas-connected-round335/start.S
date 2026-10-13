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
.global audio_uart_lv_obj_has_flag_43e0e0
.thumb_func
audio_uart_lv_obj_has_flag_43e0e0: bx lr
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
.global audio_uart_lv_obj_height_43fdda
.thumb_func
audio_uart_lv_obj_height_43fdda: bx lr
.global audio_uart_lv_obj_width_43fd9e
.thumb_func
audio_uart_lv_obj_width_43fd9e: bx lr
.global audio_uart_lv_style_property_44bdea
.thumb_func
audio_uart_lv_style_property_44bdea: bx lr
.global audio_uart_display_default_get
.thumb_func
audio_uart_display_default_get: bx lr
.section .bss.root,"aw",%nobits
.global audio_uart_display_lv_root
.balign 4
audio_uart_display_lv_root: .space 512
