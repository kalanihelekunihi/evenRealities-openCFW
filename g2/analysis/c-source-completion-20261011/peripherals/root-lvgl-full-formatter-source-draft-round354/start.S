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
.incbin "/Users/kalani/Repo/evenRealities-openCFW/g2/analysis/c-source-completion-20261011/peripherals/root-lvgl-full-formatter-source-draft-round354/oracle-data-bound.bin"
.section .text.arithmetic_boundaries,"ax"
.global __aeabi_d2iz
.thumb_func
__aeabi_d2iz: bx lr
.global __aeabi_d2uiz
.thumb_func
__aeabi_d2uiz: bx lr
.global __aeabi_dadd
.thumb_func
__aeabi_dadd: bx lr
.global __aeabi_dcmpge
.thumb_func
__aeabi_dcmpge: bx lr
.global __aeabi_dcmpgt
.thumb_func
__aeabi_dcmpgt: bx lr
.global __aeabi_dcmple
.thumb_func
__aeabi_dcmple: bx lr
.global __aeabi_dcmplt
.thumb_func
__aeabi_dcmplt: bx lr
.global __aeabi_dcmpun
.thumb_func
__aeabi_dcmpun: bx lr
.global __aeabi_ddiv
.thumb_func
__aeabi_ddiv: bx lr
.global __aeabi_dmul
.thumb_func
__aeabi_dmul: bx lr
.global __aeabi_dsub
.thumb_func
__aeabi_dsub: bx lr
.global __aeabi_i2d
.thumb_func
__aeabi_i2d: bx lr
.global __aeabi_ui2d
.thumb_func
__aeabi_ui2d: bx lr
.global __aeabi_uldivmod
.thumb_func
__aeabi_uldivmod: bx lr
