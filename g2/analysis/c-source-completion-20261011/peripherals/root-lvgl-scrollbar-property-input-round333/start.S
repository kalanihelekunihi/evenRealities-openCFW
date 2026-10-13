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
.global audio_uart_lv_style_property_44bdea
.thumb_func
audio_uart_lv_style_property_44bdea: bx lr
.section .bss.root,"aw",%nobits
.global audio_uart_display_lv_root
.balign 4
audio_uart_display_lv_root: .space 512
