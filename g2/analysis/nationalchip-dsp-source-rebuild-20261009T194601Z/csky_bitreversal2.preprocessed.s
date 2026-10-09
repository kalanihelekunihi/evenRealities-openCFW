.section .text
    .file "csky_bitreversal2.S"
    .section .text.csky_bitreversal_32,"ax",@progbits
    .align 2
    .global csky_bitreversal_32
    .type csky_bitreversal_32, @function
csky_bitreversal_32:
    addi a3, a1, 1
    push r4-r6
    mov a1, a2
    lsri a3, a3, 1
csky_bitreversal_32_0:
    ldh a2, (a1, 0x2)
    ldh r6, (a1, 0x0)
    addu a2, a0, a2
    addu r6, a0, r6
    ldw r5, (a2, 0x0)
    ldw r4, (r6, 0x0)
    stw r5, (r6, 0x0)
    stw r4, (a2, 0x0)
    ldw r5, (a2, 0x4)
    ldw r4, (r6, 0x4)
    addi a1, a1, 4
    stw r5, (r6, 0x4)
.L2:
    stw r4, (a2, 0x4)
    bloop a3, csky_bitreversal_32_0, .L2
    pop r4-r6
    jmp lr
    .size csky_bitreversal_32, .-csky_bitreversal_32
    .section .text.csky_bitreversal_16,"ax",@progbits
    .align 2
    .global csky_bitreversal_16
    .type csky_bitreversal_16, @function
csky_bitreversal_16:
    addi a3, a1, 1
    push r4-r6
    mov a1, a2
    lsri a3, a3, 1
csky_bitreversal_16_0:
    ldh a2, (a1, 0x2)
    ldh r6, (a1, 0x0)
    lsri a2, a2, 1
    lsri r6, r6, 1
    addu a2, a0, a2
    addu r6, a0, r6
    ldw r5, (a2, 0x0)
    ldw r4, (r6, 0x0)
    addi a1, a1, 4
    stw r5, (r6, 0x0)
.L3:
    stw r4, (a2, 0x0)
    bloop a3, csky_bitreversal_16_0, .L3
    pop r4-r6
    jmp lr
    .size csky_bitreversal_16, .-csky_bitreversal_16
