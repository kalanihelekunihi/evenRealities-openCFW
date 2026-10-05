.syntax unified
.thumb
.cpu cortex-m4
.text
.global minimal
.type minimal,%function
.thumb_func
minimal:
    push {r4, lr}
    movs r4, #4
loop:
    and r0, r4, #1
    bl conditional
    subs r4, #1
    bne loop
    pop {r4, pc}
conditional:
    cmp r0, #0
    it ne
    strne.w r1, [r2]
    movs r0, #0
    str r0, [r3]
    bx lr
.size minimal, .-minimal
