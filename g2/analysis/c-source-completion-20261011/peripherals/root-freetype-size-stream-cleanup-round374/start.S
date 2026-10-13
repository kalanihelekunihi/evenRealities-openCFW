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
.incbin "/Users/kalani/Repo/evenRealities-openCFW/g2/analysis/c-source-completion-20261011/peripherals/root-freetype-size-stream-cleanup-round374/oracle-data-bound.bin"
.section .bss.probe_root,"aw",%nobits
.balign 4
.global audio_uart_display_lv_root
audio_uart_display_lv_root: .space 4096





.section .text.probe_generic,"ax"
.global probe_generic
.thumb_func
probe_generic: bx lr

.section .text.probe_class,"ax"
.global probe_class
.thumb_func
probe_class: bx lr

.section .text.probe_close,"ax"
.global probe_close
.thumb_func
probe_close: bx lr

.section .text.probe_free,"ax"
.global probe_free
.thumb_func
probe_free: bx lr
