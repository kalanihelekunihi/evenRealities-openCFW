.syntax unified
.thumb
.section .note.GNU-stack,"",%progbits
.section .body_read,"ax",%progbits
.global native_fs_read
.type native_fs_read,%function
.thumb_func
native_fs_read:
$t.callback_0:
.incbin "/tmp/opencfw-main-native.bin",593904,28
.size native_fs_read,.-native_fs_read
.section .body_write,"ax",%progbits
.global native_fs_write
.type native_fs_write,%function
.thumb_func
native_fs_write:
$t.callback_1:
.incbin "/tmp/opencfw-main-native.bin",593932,28
.size native_fs_write,.-native_fs_write
.section .body_seek,"ax",%progbits
.global native_fs_seek
.type native_fs_seek,%function
.thumb_func
native_fs_seek:
$t.callback_2:
.incbin "/tmp/opencfw-main-native.bin",593960,58
.size native_fs_seek,.-native_fs_seek
.section .body_tell,"ax",%progbits
.global native_fs_tell
.type native_fs_tell,%function
.thumb_func
native_fs_tell:
$t.callback_3:
.incbin "/tmp/opencfw-main-native.bin",594020,28
.size native_fs_tell,.-native_fs_tell
.section .body_close,"ax",%progbits
.global native_fs_close
.type native_fs_close,%function
.thumb_func
native_fs_close:
$t.callback_4:
.incbin "/tmp/opencfw-main-native.bin",593880,22
.size native_fs_close,.-native_fs_close
.section .body_dir_close,"ax",%progbits
.global native_fs_dir_close
.type native_fs_dir_close,%function
.thumb_func
native_fs_dir_close:
$t.callback_5:
.incbin "/tmp/opencfw-main-native.bin",594148,30
.size native_fs_dir_close,.-native_fs_dir_close
