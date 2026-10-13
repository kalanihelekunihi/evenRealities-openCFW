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
.incbin "/Users/kalani/Repo/evenRealities-openCFW/g2/analysis/c-source-completion-20261011/peripherals/root-lvgl-draw-buffer-clear-round363/fatal-oracle.bin"
.section .bss.probe_root,"aw",%nobits
.balign 4
.global audio_uart_display_lv_root
audio_uart_display_lv_root: .space 4096

.section .text.audio_uart_lv_basic_box_clear_454746,"ax"
.global audio_uart_lv_basic_box_clear_454746
.thumb_func
audio_uart_lv_basic_box_clear_454746: bx lr

.section .text.audio_uart_lvgl_log,"ax"
.global audio_uart_lvgl_log
.thumb_func
audio_uart_lvgl_log: bx lr

.section .text.probe_clear_callback,"ax"
.global probe_clear_callback
.thumb_func
probe_clear_callback: bx lr

.section .text.probe_flush_callback,"ax"
.global probe_flush_callback
.thumb_func
probe_flush_callback: bx lr
