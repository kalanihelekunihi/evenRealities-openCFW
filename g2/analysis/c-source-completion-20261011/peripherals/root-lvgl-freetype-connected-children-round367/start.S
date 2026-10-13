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
.incbin "/Users/kalani/Repo/evenRealities-openCFW/g2/analysis/c-source-completion-20261011/peripherals/root-lvgl-freetype-connected-children-round367/oracle-data-bound.bin"
.section .bss.probe_root,"aw",%nobits
.balign 4
.global audio_uart_display_lv_root
audio_uart_display_lv_root: .space 4096



.section .text.audio_uart_ft_new_memory_5676a0,"ax"
.global audio_uart_ft_new_memory_5676a0
.thumb_func
audio_uart_ft_new_memory_5676a0: bx lr

.section .text.audio_uart_ft_new_library_5274b2,"ax"
.global audio_uart_ft_new_library_5274b2
.thumb_func
audio_uart_ft_new_library_5274b2: bx lr

.section .text.audio_uart_ft_done_memory_5676c6,"ax"
.global audio_uart_ft_done_memory_5676c6
.thumb_func
audio_uart_ft_done_memory_5676c6: bx lr

.section .text.audio_uart_ft_add_default_modules_5242fc,"ax"
.global audio_uart_ft_add_default_modules_5242fc
.thumb_func
audio_uart_ft_add_default_modules_5242fc: bx lr

.section .text.audio_uart_ft_set_transform_525444,"ax"
.global audio_uart_ft_set_transform_525444
.thumb_func
audio_uart_ft_set_transform_525444: bx lr

.section .text.audio_uart_lv_lock_core,"ax"
.global audio_uart_lv_lock_core
.thumb_func
audio_uart_lv_lock_core: bx lr

.section .text.audio_uart_lv_unlock_core,"ax"
.global audio_uart_lv_unlock_core
.thumb_func
audio_uart_lv_unlock_core: bx lr

.section .text.audio_uart_lv_heap_free,"ax"
.global audio_uart_lv_heap_free
.thumb_func
audio_uart_lv_heap_free: bx lr

.section .text.audio_queue_delete,"ax"
.global audio_queue_delete
.thumb_func
audio_queue_delete: bx lr

.section .text.audio_uart_lvgl_log,"ax"
.global audio_uart_lvgl_log
.thumb_func
audio_uart_lvgl_log: bx lr

.section .text.probe_cache_destroy,"ax"
.global probe_cache_destroy
.thumb_func
probe_cache_destroy: bx lr
