.syntax unified
.thumb
.cpu cortex-m4
.text
.global minimal
.type minimal,%function
.thumb_func
minimal:
    cmp r0, #0
    it ne
    strne.w r1, [r2]
    movs r0, #0
    str r0, [r3]
    bx lr
.size minimal, .-minimal
