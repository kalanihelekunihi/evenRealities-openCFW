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
.incbin "/Users/kalani/Repo/evenRealities-openCFW/g2/analysis/c-source-completion-20261011/peripherals/root-freetype-filesystem-unicode-round380/oracle-data-bound.bin"
.section .bss.probe_root,"aw",%nobits
.balign 4
.global audio_uart_display_lv_root
audio_uart_display_lv_root: .space 4096





.section .text.audio_uart_lv_fs_file_open_4c6d9a,"ax"
.global audio_uart_lv_fs_file_open_4c6d9a
.thumb_func
audio_uart_lv_fs_file_open_4c6d9a: bx lr

.section .text.audio_uart_lv_pool_allocate_484180,"ax"
.global audio_uart_lv_pool_allocate_484180
.thumb_func
audio_uart_lv_pool_allocate_484180: bx lr

.section .text.audio_uart_lv_pool_free_48429e,"ax"
.global audio_uart_lv_pool_free_48429e
.thumb_func
audio_uart_lv_pool_free_48429e: bx lr

.section .text.audio_uart_lvgl_log,"ax"
.global audio_uart_lvgl_log
.thumb_func
audio_uart_lvgl_log: bx lr

.section .text.probe_seek,"ax"
.global probe_seek
.thumb_func
probe_seek: bx lr

.section .text.probe_tell,"ax"
.global probe_tell
.thumb_func
probe_tell: bx lr

.section .text.probe_read,"ax"
.global probe_read
.thumb_func
probe_read: bx lr

.section .text.probe_close,"ax"
.global probe_close
.thumb_func
probe_close: bx lr

.section .text.audio_uart_lv_fs_seek_cached_4c7364,"ax"
.global audio_uart_lv_fs_seek_cached_4c7364
.thumb_func
audio_uart_lv_fs_seek_cached_4c7364: bx lr

.section .text.audio_uart_lv_fs_read_cached_4c713c,"ax"
.global audio_uart_lv_fs_read_cached_4c713c
.thumb_func
audio_uart_lv_fs_read_cached_4c713c: bx lr

.section .text.audio_uart_lv_heap_free,"ax"
.global audio_uart_lv_heap_free
.thumb_func
audio_uart_lv_heap_free: bx lr
