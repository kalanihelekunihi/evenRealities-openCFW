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
.incbin "/Users/kalani/Repo/evenRealities-openCFW/g2/analysis/c-source-completion-20261011/peripherals/root-lvgl-draw-task-independence-connected-round361/oracle-data-bound.bin"
.section .bss.probe_root,"aw",%nobits
.balign 4
.global audio_uart_display_lv_root
audio_uart_display_lv_root: .space 4096
.section .text.controlled_children,"ax"
.global audio_uart_lv_heap_alloc
.thumb_func
audio_uart_lv_heap_alloc: bx lr
.global audio_uart_lvgl_log
.thumb_func
audio_uart_lvgl_log: bx lr
.global audio_uart_lv_anim_mutex_ensure_4d47fa
.thumb_func
audio_uart_lv_anim_mutex_ensure_4d47fa: bx lr
.global stock_enter_critical
.thumb_func
stock_enter_critical: bx lr
.global stock_exit_critical
.thumb_func
stock_exit_critical: bx lr
.global audio_notify_task
.thumb_func
audio_notify_task: bx lr
.global audio_uart_display_default_get
.thumb_func
audio_uart_display_default_get: bx lr
