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
.section .text.probe_compare,"ax"
.global probe_compare
.thumb_func
probe_compare:
 push {r4-r7,lr}
 ldr r4,=0x20003c00
 ldr r5,[r4]
 cmp r5,#60
 bcs 1f
 add r6,r5,r5,lsl #1
 add r6,r4,r6,lsl #2
 str r0,[r6,#4]
 str r1,[r6,#8]
1:
 add r5,r5,#1
 str r5,[r4]
 ldr r0,[r0]
 ldr r1,[r1]
 cmp r0,r1
 it lt
 movlt r0,#-1
 it gt
 movgt r0,#1
 it eq
 moveq r0,#0
 pop {r4-r7,pc}
