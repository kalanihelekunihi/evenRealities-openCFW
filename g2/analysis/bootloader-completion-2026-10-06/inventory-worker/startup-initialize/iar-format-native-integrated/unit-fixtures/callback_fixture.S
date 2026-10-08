.syntax unified
.thumb
.section .put,"ax"
.global callback_put
.thumb_func
callback_put:
 ldr r2,=0x20008000
 ldr r3,[r2]
 add.w r12,r3,#1
 str.w r12,[r2]
 ldr r2,[r2,#4]
 cmp r3,r2
 ite eq
 moveq r0,#0
 addne r0,#4
 bx lr
.section .handler,"ax"
.global callback_handler
.thumb_func
callback_handler:
 ldr r0,=0x20008008
 ldr r0,[r0]
 bx lr
