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
.incbin "/Users/kalani/Repo/evenRealities-openCFW/g2/analysis/c-source-completion-20261011/peripherals/root-lvgl-content-helper-m55-round325/oracle-data-bound.bin"
.section .text.controlled_children,"ax"
.global audio_uart_lv_style_property_44bdea
.thumb_func
audio_uart_lv_style_property_44bdea: bx lr
.global audio_uart_lv_obj_has_flag_any_43e11c
.thumb_func
audio_uart_lv_obj_has_flag_any_43e11c: bx lr
.global audio_uart_lv_obj_parent_44dca2
.thumb_func
audio_uart_lv_obj_parent_44dca2: bx lr
.global audio_uart_lv_obj_event_451670
.thumb_func
audio_uart_lv_obj_event_451670: bx lr
