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
.incbin "/Users/kalani/Repo/evenRealities-openCFW/g2/analysis/c-source-completion-20261011/peripherals/root-littlefs-directory-cores-connected-round351/native.bin"
.section .text.controlled_children,"ax"
.global audio_file_lfs_dir_find
.thumb_func
audio_file_lfs_dir_find: bx lr
.global g2_lfs_dir_getslice
.thumb_func
g2_lfs_dir_getslice: bx lr
.global g2_lfs_dir_fetch
.thumb_func
g2_lfs_dir_fetch: bx lr
.global audio_file_lfs_dir_getinfo_4cbf38
.thumb_func
audio_file_lfs_dir_getinfo_4cbf38: bx lr
