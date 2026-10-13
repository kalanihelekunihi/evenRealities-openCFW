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
.incbin "/Users/kalani/Repo/evenRealities-openCFW/g2/analysis/c-source-completion-20261011/peripherals/root-freetype-memory-adapters-round369/oracle-data-bound.bin"
.section .bss.probe_root,"aw",%nobits
.balign 4
.global audio_uart_display_lv_root
audio_uart_display_lv_root: .space 4096



.section .text.audio_uart_lv_pool_allocate_484180,"ax"
.global audio_uart_lv_pool_allocate_484180
.thumb_func
audio_uart_lv_pool_allocate_484180: bx lr

.section .text.audio_uart_lv_pool_free_48429e,"ax"
.global audio_uart_lv_pool_free_48429e
.thumb_func
audio_uart_lv_pool_free_48429e: bx lr

.section .text.audio_uart_lv_pool_realloc_484234,"ax"
.global audio_uart_lv_pool_realloc_484234
.thumb_func
audio_uart_lv_pool_realloc_484234: bx lr
