@ Unexecuted exploratory assembly; not a valid test fixture or validation evidence.
.syntax unified
.thumb
.cpu cortex-m4
.text
.global minimal
.type minimal,%function
.thumb_func
minimal:
 push {r4,r5,r6,r7,r8,lr}
 mov r6,r0
 mov r7,r1
 movs r4,#2
 movs r5,#0
loop:
 ldr r0,[r7,#44]
 ldr r1,[r6,#20]
 cmp r0,r1
 itt hi
 strhi r0,[r6,#20]
 ldrhi r0,[r7,#44]
 add.w r0,r0,r0,lsl #2
 add.w r0,r8,r0,lsl #2
 mov r1,r5
 bl leaf
 subs r4,#1
 bne loop
 pop {r4,r5,r6,r7,r8,pc}
leaf:
 ldr r2,[r0,#4]
 ldr.w ip,[r0]
 ldr r3,[r2,#8]
 str r2,[r1,#4]
 str r3,[r1,#8]
 str r1,[r3,#4]
 str r1,[r2,#8]
 str r0,[r1,#16]
 add.w r1,ip,#1
 str r1,[r0]
 bx lr
.size minimal,.-minimal
