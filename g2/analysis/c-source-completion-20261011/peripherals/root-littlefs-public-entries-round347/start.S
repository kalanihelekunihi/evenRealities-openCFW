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
.incbin "/Users/kalani/Repo/evenRealities-openCFW/g2/analysis/c-source-completion-20261011/peripherals/root-littlefs-public-entries-round347/oracle-data-bound.bin"
.section .text.controlled_children,"ax"
.global g2_lfs_mlist_isopen
.thumb_func
g2_lfs_mlist_isopen: bx lr
.global g2_file_close_error
.thumb_func
g2_file_close_error: bx lr
.global g2_lfs_file_close
.thumb_func
g2_lfs_file_close: bx lr
.global audio_file_lfs_write_core_4ce308
.thumb_func
audio_file_lfs_write_core_4ce308: bx lr
.global audio_file_lfs_dir_open_core_4cd558
.thumb_func
audio_file_lfs_dir_open_core_4cd558: bx lr
.global audio_file_lfs_dir_read_core_4cd60e
.thumb_func
audio_file_lfs_dir_read_core_4cd60e: bx lr
.global g2_lfs_mlist_remove
.thumb_func
g2_lfs_mlist_remove: bx lr
