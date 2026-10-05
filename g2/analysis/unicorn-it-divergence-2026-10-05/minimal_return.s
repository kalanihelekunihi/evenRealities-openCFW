.syntax unified
.thumb
.cpu cortex-m4
.text
.global minimal
.type minimal,%function
.thumb_func
minimal:
    push {r4, lr}
    bl conditional
    movs r0, #0
    str r0, [r3]
    pop {r4, pc}
conditional:
    push {r4, r5, r6, r7, r8, r9, lr}
    movs r4, #1
    cmp r1, #0
    it ne
    movne r4, #1
    mov r0, r4
    pop {r4, r5, r6, r7, r8, r9, pc}
.size minimal, .-minimal
