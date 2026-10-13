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
.incbin "/Users/kalani/Repo/evenRealities-openCFW/g2/analysis/c-source-completion-20261011/peripherals/root-lvgl-littlefs-open-directory-native-round345/oracle-data-bound.bin"
.section .text.controlled_children,"ax"
.global audio_uart_lv_malloc
.thumb_func
audio_uart_lv_malloc: bx lr
.global audio_uart_lv_heap_free
.thumb_func
audio_uart_lv_heap_free: bx lr
.global audio_uart_lvgl_log
.thumb_func
audio_uart_lvgl_log: bx lr
.global audio_uart_lv_snprintf_483fd0
.thumb_func
audio_uart_lv_snprintf_483fd0: bx lr
.global audio_uart_lv_strlcpy_454778
.thumb_func
audio_uart_lv_strlcpy_454778: bx lr
.global audio_file_lfs_open
.thumb_func
audio_file_lfs_open: bx lr
.global audio_file_lfs_dir_open_4cfc66
.thumb_func
audio_file_lfs_dir_open_4cfc66: bx lr
.global audio_file_lfs_dir_read_4cfd02
.thumb_func
audio_file_lfs_dir_read_4cfd02: bx lr
