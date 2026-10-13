.syntax unified
.thumb
.section .note.GNU-stack,"",%progbits
.section .body,"ax",%progbits
.global native_lv_obj_refr_size
.type native_lv_obj_refr_size,%function
.thumb_func
native_lv_obj_refr_size:
$t:
.incbin "/tmp/opencfw-main-native.bin",29092,796
.size native_lv_obj_refr_size,.-native_lv_obj_refr_size
.section .pool,"a",%progbits
$d4455628:
.incbin "/tmp/opencfw-main-native.bin",31948,200
.section .string0,"a",%progbits
$d7740752:
.incbin "/tmp/opencfw-main-native.bin",3317072,32
.section .string1,"a",%progbits
$d7894720:
.incbin "/tmp/opencfw-main-native.bin",3471040,13
.section .string2,"a",%progbits
$d7910420:
.incbin "/tmp/opencfw-main-native.bin",3486740,12
.section .string3,"a",%progbits
$d7868228:
.incbin "/tmp/opencfw-main-native.bin",3444548,17
.section .string4,"a",%progbits
$d7225448:
.incbin "/tmp/opencfw-main-native.bin",2801768,85
