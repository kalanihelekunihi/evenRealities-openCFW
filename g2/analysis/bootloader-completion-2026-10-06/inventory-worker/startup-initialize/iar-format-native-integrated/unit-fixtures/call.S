.syntax unified
.thumb
.text
.global call_engine
.thumb_func
call_engine:
 push.w {r4-r11,lr}
 sub sp,#12
 mov r12,r0
 ldr r0,[r12,#20]
 str r0,[sp]
 sub.w r0,sp,#232
 sub.w r1,sp,#40
 movw r2,#12593
 movt r2,#12593
1: str r2,[r0],#4
 cmp r0,r1
 blo 1b
 movw r4,#0x0004
 movt r4,#0xaac0
 adds r5,r4,#1
 adds r6,r4,#2
 adds r7,r4,#3
 adds r8,r4,#4
 adds r9,r4,#5
 adds r10,r4,#6
 adds r11,r4,#7
 ldr r0,[r12,#4]
 ldr r1,[r12,#8]
 ldr r2,[r12,#12]
 ldr r3,[r12,#16]
 ldr r12,[r12]
 blx r12
 ldr r12,=abi_result
 str r0,[r12],#4
 stmia.w r12!,{r4-r11}
 mov r1,sp
 str r1,[r12],#4
 mrs r1,primask
 str r1,[r12],#4
 vmrs r1,fpscr
 str r1,[r12]
 add sp,#12
 pop.w {r4-r11,pc}
