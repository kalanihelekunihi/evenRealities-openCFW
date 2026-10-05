.syntax unified
.thumb
.cpu cortex-m4
.text
.global minimal
.type minimal,%function
.thumb_func
minimal:
    push {r4, r5, lr}
    movs r4, #2
    movs r5, #0
loop:
    movs r0, #3
    cmp r0, r5
    itt hi
    strhi r0, [r2]
    ldrhi r0, [r2]
    mov r5, r0
    mov.w r1, #0
    bl leaf
    subs r4, #1
    bne loop
    pop {r4, r5, pc}
leaf:
    ldr r1, [r2]
    str r1, [r3]
    bx lr
.size minimal, .-minimal
