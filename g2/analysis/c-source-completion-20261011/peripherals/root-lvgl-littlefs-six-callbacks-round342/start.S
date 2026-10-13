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
.global audio_file_lfs_read
.thumb_func
audio_file_lfs_read: bx lr
.global audio_file_lfs_seek
.thumb_func
audio_file_lfs_seek: bx lr
.global audio_file_lfs_tell
.thumb_func
audio_file_lfs_tell: bx lr
.global audio_file_lfs_close_4cfad0
.thumb_func
audio_file_lfs_close_4cfad0: bx lr
.global audio_file_lfs_write_4cfb7c
.thumb_func
audio_file_lfs_write_4cfb7c: bx lr
.global audio_file_lfs_dir_close_4cfcf8
.thumb_func
audio_file_lfs_dir_close_4cfcf8: bx lr
.global audio_uart_lv_heap_free
.thumb_func
audio_uart_lv_heap_free: bx lr
