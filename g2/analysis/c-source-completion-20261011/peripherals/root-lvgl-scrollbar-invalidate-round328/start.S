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
.global audio_uart_lv_get_scrollbar_areas_44eb28
.thumb_func
audio_uart_lv_get_scrollbar_areas_44eb28: bx lr
.global audio_uart_display_invalidate_area
.thumb_func
audio_uart_display_invalidate_area: bx lr
