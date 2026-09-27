/*
 * SPDX-License-Identifier: MIT
 *
 * Source-owned exact helpers from the AM-035 retained island.
 */

#if defined(OPEN_CFW_AM035_8834C_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am035_8834c(void)
{
    __asm__ volatile(
        "    push {r2, r3, r4, lr}\n    movs r2, r0\n    movs r0, r2\n    uxtb r0, r0\n    cmp r0, #0x13\n    blt L_open_cfw_runtime_am035_8834c_002a\n    uxtb r2, r2\n    str r2, [sp, #4]\n    ldr r0, [pc, #0x68]\n    str r0, [sp]\n    ldr r3, [pc, #0x80]\n    movs r2, #0x76\n    ldr r1, [pc, #0x68]\n    movs r0, #2\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am035_addr_0044d25c\n    bl .\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am035_addr_004410a6\n    bl .\n    str r0, [sp]\n    ldr r0, [sp]\n    b L_open_cfw_runtime_am035_8834c_0078\nL_open_cfw_runtime_am035_8834c_002a:\n    movs r0, r1\n    uxtb r0, r0\n    cmp r0, #0\n    beq L_open_cfw_runtime_am035_8834c_003a\n    movs r0, r1\n    uxtb r0, r0\n    cmp r0, #5\n    blt L_open_cfw_runtime_am035_8834c_0058\nL_open_cfw_runtime_am035_8834c_003a:\n    uxtb r1, r1\n    str r1, [sp, #4]\n    ldr r0, [pc, #0x5c]\n    str r0, [sp]\n    ldr r3, [pc, #0x54]\n    movs r2, #0x7b\n    ldr r1, [pc, #0x3c]\n    movs r0, #2\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am035_addr_0044d25c\n    bl .\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am035_addr_004410a6\n    bl .\n    str r0, [sp]\n    ldr r0, [sp]\n    b L_open_cfw_runtime_am035_8834c_0078\nL_open_cfw_runtime_am035_8834c_0058:\n    subs r3, r1, #1\n    mov r0, sp\n    ldr r4, [pc, #0x40]\n    uxtb r2, r2\n    movs r1, #0xc\n    muls r2, r1, r2\n    add r2, r4\n    uxtb r3, r3\n    movs r1, #3\n    muls r3, r1, r3\n    add.w r1, r2, r3\n    movs r2, #3\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am035_addr_00439be4\n    bl .\n    ldr r0, [sp]\nL_open_cfw_runtime_am035_8834c_0078:\n    pop {r1, r2, r4, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM035_883F0_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am035_883f0(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    movs r2, r1\n    movs r1, #0\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am035_addr_00454746\n    bl .\n    pop {r0, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM035_883FC_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am035_883fc(void)
{
    __asm__ volatile(
        "    push {r0, r1, r2, r3, r4, lr}\n    movs r4, r0\n    movs r0, r1\n    movs r1, #0\n    str r1, [r4, #4]\n    str r0, [r4, #8]\n    str r2, [r4, #0xc]\n    muls r0, r2, r0\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am035_addr_0044f718\n    bl .\n    str r0, [r4]\n    movs r0, #1\n    strb r0, [r4, #0x10]\n    ldr r0, [r4]\n    cmp r0, #0\n    bne L_open_cfw_runtime_am035_883fc_0042\n    ldr r0, [pc, #0x19c]\n    str r0, [sp, #8]\n    ldr r0, [pc, #0x19c]\n    str r0, [sp, #4]\n    ldr r0, [pc, #0x19c]\n    str r0, [sp]\n    ldr r3, [pc, #0x19c]\n    movs r2, #0x2e\n    ldr r1, [pc, #0x19c]\n    movs r0, #3\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am035_addr_0044d25c\n    bl .\nL_open_cfw_runtime_am035_883fc_0038:\n    movs r0, #0\n    movs.w r1, #-1\n    str r0, [r1]\n    b L_open_cfw_runtime_am035_883fc_0038\nL_open_cfw_runtime_am035_883fc_0042:\n    pop {r0, r1, r2, r3, r4, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM035_88440_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am035_88440(void)
{
    __asm__ volatile(
        "    push {r0, r1, r2, r3, r4, lr}\n    cmp r1, #0\n    bne L_open_cfw_runtime_am035_88440_0028\n    ldr r0, [pc, #0x188]\n    str r0, [sp, #8]\n    ldr r0, [pc, #0x188]\n    str r0, [sp, #4]\n    ldr r0, [pc, #0x174]\n    str r0, [sp]\n    ldr r3, [pc, #0x184]\n    movs r2, #0x33\n    ldr r1, [pc, #0x174]\n    movs r0, #3\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am035_addr_0044d25c\n    bl .\nL_open_cfw_runtime_am035_88440_001e:\n    movs r0, #0\n    movs.w r1, #-1\n    str r0, [r1]\n    b L_open_cfw_runtime_am035_88440_001e\nL_open_cfw_runtime_am035_88440_0028:\n    movs r4, #0\n    str r4, [r0, #4]\n    str r2, [r0, #8]\n    str r3, [r0, #0xc]\n    str r1, [r0]\n    movs r1, #0\n    strb r1, [r0, #0x10]\n    pop {r0, r1, r2, r3, r4, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM035_88478_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am035_88478(void)
{
    __asm__ volatile(
        "    push {r4, lr}\n    movs r4, r0\n    ldr r0, [r4]\n    cmp r0, #0\n    beq L_open_cfw_runtime_am035_88478_001a\n    ldrb r0, [r4, #0x10]\n    cmp r0, #0\n    beq L_open_cfw_runtime_am035_88478_0016\n    ldr r0, [r4]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am035_addr_0044f758\n    bl .\nL_open_cfw_runtime_am035_88478_0016:\n    movs r0, #0\n    str r0, [r4]\nL_open_cfw_runtime_am035_88478_001a:\n    movs r0, #0\n    str r0, [r4, #4]\n    movs r0, #0\n    str r0, [r4, #8]\n    pop {r4, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM035_8849C_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am035_8849c(void)
{
    __asm__ volatile(
        "    push {r1, r2, r3, r4, r5, lr}\n    movs r4, r0\n    movs r5, r1\n    ldrb r0, [r4, #0x10]\n    cmp r0, #0\n    bne L_open_cfw_runtime_am035_8849c_0020\n    ldr r0, [pc, #0x130]\n    str r0, [sp]\n    ldr r3, [pc, #0x130]\n    movs r2, #0x8c\n    ldr r1, [pc, #0x118]\n    movs r0, #2\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am035_addr_0044d25c\n    bl .\n    movs r0, #0\n    b L_open_cfw_runtime_am035_8849c_0068\nL_open_cfw_runtime_am035_8849c_0020:\n    ldr r1, [r4, #0xc]\n    mul r1, r1, r5\n    ldr r0, [r4]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am035_addr_0044f76a\n    bl .\n    cmp r0, #0\n    bne L_open_cfw_runtime_am035_8849c_0052\n    ldr r0, [pc, #0x100]\n    str r0, [sp, #8]\n    ldr r0, [pc, #0x110]\n    str r0, [sp, #4]\n    ldr r0, [pc, #0xec]\n    str r0, [sp]\n    ldr r3, [pc, #0x104]\n    movs r2, #0x91\n    ldr r1, [pc, #0xec]\n    movs r0, #3\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am035_addr_0044d25c\n    bl .\nL_open_cfw_runtime_am035_8849c_0048:\n    movs r0, #0\n    movs.w r1, #-1\n    str r0, [r1]\n    b L_open_cfw_runtime_am035_8849c_0048\nL_open_cfw_runtime_am035_8849c_0052:\n    cmp r0, #0\n    bne L_open_cfw_runtime_am035_8849c_005a\n    movs r0, #0\n    b L_open_cfw_runtime_am035_8849c_0068\nL_open_cfw_runtime_am035_8849c_005a:\n    str r0, [r4]\n    str r5, [r4, #8]\n    ldr r0, [r4, #4]\n    cmp r5, r0\n    bhs L_open_cfw_runtime_am035_8849c_0066\n    str r5, [r4, #4]\nL_open_cfw_runtime_am035_8849c_0066:\n    movs r0, #1\nL_open_cfw_runtime_am035_8849c_0068:\n    pop {r1, r2, r3, r4, r5, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM035_88506_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am035_88506(void)
{
    __asm__ volatile(
        "    push {r1, r2, r3, r4, r5, lr}\n    movs r5, r0\n    movs r4, r1\n    ldr r0, [r5]\n    cmp r0, #0\n    bne L_open_cfw_runtime_am035_88506_002e\n    ldr r0, [pc, #0xbc]\n    str r0, [sp, #8]\n    ldr r0, [pc, #0xa8]\n    str r0, [sp, #4]\n    ldr r0, [pc, #0xa8]\n    str r0, [sp]\n    ldr r3, [pc, #0xc8]\n    movs r2, #0xb0\n    ldr r1, [pc, #0xa8]\n    movs r0, #3\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am035_addr_0044d25c\n    bl .\nL_open_cfw_runtime_am035_88506_0024:\n    movs r0, #0\n    movs.w r1, #-1\n    str r0, [r1]\n    b L_open_cfw_runtime_am035_88506_0024\nL_open_cfw_runtime_am035_88506_002e:\n    ldr r0, [r5, #4]\n    ldr r1, [r5, #8]\n    cmp r0, r1\n    bne L_open_cfw_runtime_am035_88506_0048\n    ldr r1, [r5, #8]\n    adds r1, r1, #4\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am035_8849c\n    bl .\n    cmp r0, #0\n    bne L_open_cfw_runtime_am035_88506_0048\n    movs r0, #0\n    b L_open_cfw_runtime_am035_88506_0070\nL_open_cfw_runtime_am035_88506_0048:\n    ldr r1, [r5]\n    ldr r2, [r5, #4]\n    ldr r0, [r5, #0xc]\n    muls r2, r0, r2\n    add.w r0, r1, r2\n    cmp r4, #0\n    beq L_open_cfw_runtime_am035_88506_0062\n    ldr r2, [r5, #0xc]\n    movs r1, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am035_addr_00454738\n    bl .\n    b L_open_cfw_runtime_am035_88506_0068\nL_open_cfw_runtime_am035_88506_0062:\n    ldr r1, [r5, #0xc]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am035_883f0\n    bl .\nL_open_cfw_runtime_am035_88506_0068:\n    ldr r0, [r5, #4]\n    adds r0, r0, #1\n    str r0, [r5, #4]\n    movs r0, #1\nL_open_cfw_runtime_am035_88506_0070:\n    pop {r1, r2, r3, r4, r5, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM035_88578_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am035_88578(void)
{
    __asm__ volatile(
        "    push {r5, r6, r7, lr}\n    ldr r2, [r0, #4]\n    cmp r1, r2\n    blo L_open_cfw_runtime_am035_88578_000c\n    movs r0, #0\n    b L_open_cfw_runtime_am035_88578_003e\nL_open_cfw_runtime_am035_88578_000c:\n    ldr r2, [r0]\n    cmp r2, #0\n    bne L_open_cfw_runtime_am035_88578_0034\n    ldr r0, [pc, #0x44]\n    str r0, [sp, #8]\n    ldr r0, [pc, #0x30]\n    str r0, [sp, #4]\n    ldr r0, [pc, #0x30]\n    str r0, [sp]\n    ldr r3, [pc, #0x54]\n    movs r2, #0xca\n    ldr r1, [pc, #0x30]\n    movs r0, #3\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am035_addr_0044d25c\n    bl .\nL_open_cfw_runtime_am035_88578_002a:\n    movs r0, #0\n    movs.w r1, #-1\n    str r0, [r1]\n    b L_open_cfw_runtime_am035_88578_002a\nL_open_cfw_runtime_am035_88578_0034:\n    ldr r2, [r0]\n    ldr r0, [r0, #0xc]\n    muls r1, r0, r1\n    add.w r0, r2, r1\nL_open_cfw_runtime_am035_88578_003e:\n    pop {r1, r2, r3, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM035_885F0_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am035_885f0(void)
{
    __asm__ volatile(
        "    movs r1, #0\n    b L_open_cfw_runtime_am035_885f0_0008\nL_open_cfw_runtime_am035_885f0_0004:\n    adds.w r0, r0, #0x168\nL_open_cfw_runtime_am035_885f0_0008:\n    movs r1, r0\n    sxth r1, r1\n    cmp r1, #0\n    bmi L_open_cfw_runtime_am035_885f0_0004\nL_open_cfw_runtime_am035_885f0_0010:\n    movs r1, r0\n    sxth r1, r1\n    cmp.w r1, #0x168\n    blt L_open_cfw_runtime_am035_885f0_0020\n    subs.w r0, r0, #0x168\n    b L_open_cfw_runtime_am035_885f0_0010\nL_open_cfw_runtime_am035_885f0_0020:\n    movs r1, r0\n    sxth r1, r1\n    cmp r1, #0x5a\n    bge L_open_cfw_runtime_am035_885f0_0034\n    ldr.w r1, [pc, #0x2e0]\n    sxth r0, r0\n    ldrh.w r0, [r1, r0, lsl #1]\n    b L_open_cfw_runtime_am035_885f0_0078\nL_open_cfw_runtime_am035_885f0_0034:\n    movs r1, r0\n    sxth r1, r1\n    subs r1, #0x5a\n    cmp r1, #0x5a\n    bhs L_open_cfw_runtime_am035_885f0_004e\n    rsbs.w r0, r0, #0xb4\n    ldr.w r1, [pc, #0x2c8]\n    sxth r0, r0\n    ldrh.w r0, [r1, r0, lsl #1]\n    b L_open_cfw_runtime_am035_885f0_0078\nL_open_cfw_runtime_am035_885f0_004e:\n    movs r1, r0\n    sxth r1, r1\n    subs r1, #0xb4\n    cmp r1, #0x5a\n    bhs L_open_cfw_runtime_am035_885f0_0068\n    subs r0, #0xb4\n    ldr.w r1, [pc, #0x2b0]\n    sxth r0, r0\n    ldrh.w r0, [r1, r0, lsl #1]\n    rsbs r0, r0, #0\n    b L_open_cfw_runtime_am035_885f0_0078\nL_open_cfw_runtime_am035_885f0_0068:\n    rsbs.w r0, r0, #0x168\n    ldr.w r1, [pc, #0x29c]\n    sxth r0, r0\n    ldrh.w r0, [r1, r0, lsl #1]\n    rsbs r0, r0, #0\nL_open_cfw_runtime_am035_885f0_0078:\n    movw r1, #0x7fff\n    cmp r0, r1\n    bne L_open_cfw_runtime_am035_885f0_0086\n    mov.w r0, #0x8000\n    b L_open_cfw_runtime_am035_885f0_0094\nL_open_cfw_runtime_am035_885f0_0086:\n    ldr.w r1, [pc, #0x288]\n    cmp r0, r1\n    bne L_open_cfw_runtime_am035_885f0_0094\n    ldr.w r0, [pc, #0x284]\n    b L_open_cfw_runtime_am035_885f0_0094\nL_open_cfw_runtime_am035_885f0_0094:\n    bx lr\n"
    );
}
#endif

#if defined(OPEN_CFW_AM035_88686_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am035_88686(void)
{
    __asm__ volatile(
        "    muls r1, r0, r1\n    asrs r1, r1, #0xa\n    adds r1, r2, r1\n    muls r1, r0, r1\n    asrs r1, r1, #0xa\n    adds r1, r3, r1\n    mul r0, r0, r1\n    asrs r0, r0, #0xa\n    bx lr\n"
    );
}
#endif

#if defined(OPEN_CFW_AM035_8869A_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am035_8869a(void)
{
    __asm__ volatile(
        "    push.w {r1, r2, r3, r4, r5, r6, r7, r8, sb, sl, fp, lr}\n    movs r4, r0\n    cmp r4, #0\n    beq L_open_cfw_runtime_am035_8869a_0010\n    cmp.w r4, #0x400\n    bne L_open_cfw_runtime_am035_8869a_0014\nL_open_cfw_runtime_am035_8869a_0010:\n    movs r0, r4\n    b L_open_cfw_runtime_am035_8869a_011e\nL_open_cfw_runtime_am035_8869a_0014:\n    ldr r6, [sp, #0x30]\n    movs.w sb, #3\n    mul sb, sb, r1\n    subs r1, r3, r1\n    movs r0, #3\n    muls r1, r0, r1\n    subs.w r1, r1, sb\n    mov sl, r1\n    rsbs.w r5, sb, #0x400\n    subs.w r5, r5, sl\n    movs r0, #3\n    mul r0, r0, r2\n    str r0, [sp]\n    subs r2, r6, r2\n    movs r0, #3\n    muls r2, r0, r2\n    ldr r0, [sp]\n    subs r2, r2, r0\n    str r2, [sp, #4]\n    ldr.w r8, [sp]\n    rsbs.w r8, r8, #0x400\n    ldr r0, [sp, #4]\n    subs.w r8, r8, r0\n    movs r6, r4\n    movs r7, #0\n    b L_open_cfw_runtime_am035_8869a_0072\nL_open_cfw_runtime_am035_8869a_005a:\n    asrs r1, r0, #0x1f\n    lsls r1, r1, #0xa\n    orr.w r1, r1, r0, lsr #22\n    lsls r0, r0, #0xa\n    asrs r3, r2, #0x1f\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am035_addr_0047cc1c\n    bl .\n    cmp r0, #0\n    beq L_open_cfw_runtime_am035_8869a_00ba\n    subs r6, r6, r0\n    adds r7, r7, #1\nL_open_cfw_runtime_am035_8869a_0072:\n    cmp r7, #8\n    bge L_open_cfw_runtime_am035_8869a_00ba\n    mov r3, sb\n    mov r2, sl\n    movs r1, r5\n    movs r0, r6\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am035_88686\n    bl .\n    subs r0, r0, r4\n    cmp r0, #1\n    blt L_open_cfw_runtime_am035_8869a_008c\n    movs r1, r0\n    b L_open_cfw_runtime_am035_8869a_008e\nL_open_cfw_runtime_am035_8869a_008c:\n    rsbs r1, r0, #0\nL_open_cfw_runtime_am035_8869a_008e:\n    cmp r1, #2\n    blt L_open_cfw_runtime_am035_8869a_00b0\n    movs r2, r5\n    muls r2, r6, r2\n    movs r1, #3\n    muls r2, r1, r2\n    asrs r2, r2, #0xa\n    adds.w r2, r2, sl, lsl #1\n    muls r2, r6, r2\n    asrs r2, r2, #0xa\n    adds.w r2, sb, r2\n    cmp r2, #1\n    blt L_open_cfw_runtime_am035_8869a_00b2\n    movs r1, r2\n    b L_open_cfw_runtime_am035_8869a_00b4\nL_open_cfw_runtime_am035_8869a_00b0:\n    b L_open_cfw_runtime_am035_8869a_0112\nL_open_cfw_runtime_am035_8869a_00b2:\n    rsbs r1, r2, #0\nL_open_cfw_runtime_am035_8869a_00b4:\n    cmp r1, #2\n    bge L_open_cfw_runtime_am035_8869a_005a\n    b L_open_cfw_runtime_am035_8869a_00ba\nL_open_cfw_runtime_am035_8869a_00ba:\n    movs r7, #0\n    mov.w fp, #0x400\n    movs r6, r4\n    cmp r6, r7\n    bge L_open_cfw_runtime_am035_8869a_00ca\n    movs r6, r7\n    b L_open_cfw_runtime_am035_8869a_0112\nL_open_cfw_runtime_am035_8869a_00ca:\n    cmp fp, r6\n    bge L_open_cfw_runtime_am035_8869a_00d2\n    mov r6, fp\n    b L_open_cfw_runtime_am035_8869a_0112\nL_open_cfw_runtime_am035_8869a_00d2:\n    cmp r7, fp\n    bge L_open_cfw_runtime_am035_8869a_0112\n    mov r3, sb\n    mov r2, sl\n    movs r1, r5\n    movs r0, r6\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am035_88686\n    bl .\n    subs r1, r0, r4\n    cmp r1, #1\n    blt L_open_cfw_runtime_am035_8869a_00ec\n    subs r1, r0, r4\n    b L_open_cfw_runtime_am035_8869a_00ee\nL_open_cfw_runtime_am035_8869a_00ec:\n    subs r1, r4, r0\nL_open_cfw_runtime_am035_8869a_00ee:\n    cmp r1, #2\n    blt L_open_cfw_runtime_am035_8869a_00fc\n    cmp r0, r4\n    bge L_open_cfw_runtime_am035_8869a_00fe\n    movs r7, r6\n    movs r0, r7\n    b L_open_cfw_runtime_am035_8869a_0102\nL_open_cfw_runtime_am035_8869a_00fc:\n    b L_open_cfw_runtime_am035_8869a_0112\nL_open_cfw_runtime_am035_8869a_00fe:\n    mov fp, r6\n    mov r0, fp\nL_open_cfw_runtime_am035_8869a_0102:\n    subs.w r0, fp, r7\n    movs r1, #2\n    sdiv r6, r0, r1\n    adds r6, r7, r6\n    cmp r6, r7\n    bne L_open_cfw_runtime_am035_8869a_00d2\nL_open_cfw_runtime_am035_8869a_0112:\n    ldr r3, [sp]\n    ldr r2, [sp, #4]\n    mov r1, r8\n    movs r0, r6\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am035_88686\n    bl .\nL_open_cfw_runtime_am035_8869a_011e:\n    pop.w {r1, r2, r3, r4, r5, r6, r7, r8, sb, sl, fp, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM035_887BC_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am035_887bc(void)
{
    __asm__ volatile(
        "    push {r4}\n    movs r3, #0\n    cmp r0, #0\n    bpl L_open_cfw_runtime_am035_887bc_000c\n    adds r3, r3, #1\n    rsbs r0, r0, #0\nL_open_cfw_runtime_am035_887bc_000c:\n    cmp r1, #0\n    bpl L_open_cfw_runtime_am035_887bc_0014\n    adds r3, r3, #2\n    rsbs r1, r1, #0\nL_open_cfw_runtime_am035_887bc_0014:\n    cmp r1, r0\n    bhs L_open_cfw_runtime_am035_887bc_0024\n    movs r2, #0x2d\n    muls r1, r2, r1\n    udiv r2, r1, r0\n    adds r3, #0x10\n    b L_open_cfw_runtime_am035_887bc_002c\nL_open_cfw_runtime_am035_887bc_0024:\n    movs r2, #0x2d\n    muls r0, r2, r0\n    udiv r2, r0, r1\nL_open_cfw_runtime_am035_887bc_002c:\n    movs r1, #0\n    movs r0, r2\n    movs r4, r0\n    uxtb r4, r4\n    cmp r4, #0x17\n    blt L_open_cfw_runtime_am035_887bc_0060\n    movs r4, r0\n    uxtb r4, r4\n    cmp r4, #0x2d\n    bge L_open_cfw_runtime_am035_887bc_0042\n    adds r1, r1, #1\nL_open_cfw_runtime_am035_887bc_0042:\n    movs r4, r0\n    uxtb r4, r4\n    cmp r4, #0x2a\n    bge L_open_cfw_runtime_am035_887bc_004c\n    adds r1, r1, #1\nL_open_cfw_runtime_am035_887bc_004c:\n    movs r4, r0\n    uxtb r4, r4\n    cmp r4, #0x26\n    bge L_open_cfw_runtime_am035_887bc_0056\n    adds r1, r1, #1\nL_open_cfw_runtime_am035_887bc_0056:\n    uxtb r0, r0\n    cmp r0, #0x21\n    bge L_open_cfw_runtime_am035_887bc_0086\n    adds r1, r1, #1\n    b L_open_cfw_runtime_am035_887bc_0086\nL_open_cfw_runtime_am035_887bc_0060:\n    movs r4, r0\n    uxtb r4, r4\n    cmp r4, #2\n    blt L_open_cfw_runtime_am035_887bc_006a\n    adds r1, r1, #1\nL_open_cfw_runtime_am035_887bc_006a:\n    movs r4, r0\n    uxtb r4, r4\n    cmp r4, #6\n    blt L_open_cfw_runtime_am035_887bc_0074\n    adds r1, r1, #1\nL_open_cfw_runtime_am035_887bc_0074:\n    movs r4, r0\n    uxtb r4, r4\n    cmp r4, #0xa\n    blt L_open_cfw_runtime_am035_887bc_007e\n    adds r1, r1, #1\nL_open_cfw_runtime_am035_887bc_007e:\n    uxtb r0, r0\n    cmp r0, #0xf\n    blt L_open_cfw_runtime_am035_887bc_0086\n    adds r1, r1, #1\nL_open_cfw_runtime_am035_887bc_0086:\n    uxtab r0, r2, r1\n    lsls r1, r3, #0x1b\n    bpl L_open_cfw_runtime_am035_887bc_0092\n    rsbs.w r0, r0, #0x5a\nL_open_cfw_runtime_am035_887bc_0092:\n    lsls r1, r3, #0x1e\n    bpl L_open_cfw_runtime_am035_887bc_00a4\n    lsls r1, r3, #0x1f\n    bpl L_open_cfw_runtime_am035_887bc_009e\n    adds r0, #0xb4\n    b L_open_cfw_runtime_am035_887bc_00ac\nL_open_cfw_runtime_am035_887bc_009e:\n    rsbs.w r0, r0, #0xb4\n    b L_open_cfw_runtime_am035_887bc_00ac\nL_open_cfw_runtime_am035_887bc_00a4:\n    lsls r1, r3, #0x1f\n    bpl L_open_cfw_runtime_am035_887bc_00ac\n    rsbs.w r0, r0, #0x168\nL_open_cfw_runtime_am035_887bc_00ac:\n    uxth r0, r0\n    pop {r4}\n    bx lr\n"
    );
}
#endif

#if defined(OPEN_CFW_AM035_888B4_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am035_888b4(void)
{
    __asm__ volatile(
        "    push {r4}\n    movs r4, r0\n    ldr r0, [sp, #4]\n    cmp r2, r1\n    blt L_open_cfw_runtime_am035_888b4_000e\n    cmp r4, r2\n    bge L_open_cfw_runtime_am035_888b4_003e\nL_open_cfw_runtime_am035_888b4_000e:\n    cmp r2, r1\n    blt L_open_cfw_runtime_am035_888b4_001a\n    cmp r1, r4\n    blt L_open_cfw_runtime_am035_888b4_001a\n    movs r0, r3\n    b L_open_cfw_runtime_am035_888b4_003e\nL_open_cfw_runtime_am035_888b4_001a:\n    cmp r1, r2\n    blt L_open_cfw_runtime_am035_888b4_0022\n    cmp r2, r4\n    bge L_open_cfw_runtime_am035_888b4_003e\nL_open_cfw_runtime_am035_888b4_0022:\n    cmp r1, r2\n    blt L_open_cfw_runtime_am035_888b4_002e\n    cmp r4, r1\n    blt L_open_cfw_runtime_am035_888b4_002e\n    movs r0, r3\n    b L_open_cfw_runtime_am035_888b4_003e\nL_open_cfw_runtime_am035_888b4_002e:\n    subs r2, r2, r1\n    subs r0, r0, r3\n    subs r4, r4, r1\n    muls r4, r0, r4\n    sdiv r0, r4, r2\n    adds r3, r3, r0\n    movs r0, r3\nL_open_cfw_runtime_am035_888b4_003e:\n    pop {r4}\n    bx lr\n"
    );
}
#endif

#if defined(OPEN_CFW_AM035_888F6_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am035_888f6(void)
{
    __asm__ volatile(
        "    ldr r1, [pc, #0x10]\n    str r0, [r1, #0x68]\n    bx lr\n"
    );
}
#endif

#if defined(OPEN_CFW_AM035_8890C_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am035_8890c(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    movs r2, r1\n    movs r1, #0\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am035_addr_00454746\n    bl .\n    pop {r0, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM035_88918_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am035_88918(void)
{
    __asm__ volatile(
        "    push {r2, r3, r4, lr}\n    movs r4, r0\n    movs r1, #0x6c\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am035_8890c\n    bl .\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am035_addr_004410a6\n    bl .\n    str r0, [sp]\n    adds.w r0, r4, #0x4c\n    mov r1, sp\n    movs r2, #3\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am035_addr_00439be4\n    bl .\n    movs r0, #0xff\n    strb.w r0, [r4, #0x50]\n    mov.w r0, #0x100\n    str r0, [r4, #0x34]\n    str r0, [r4, #0x38]\n    ldrh.w r1, [r4, #0x50]\n    movw r0, #0xf7ff\n    ands r1, r0\n    strh.w r1, [r4, #0x50]\n    ldr.w r0, [pc, #0x5c4]\n    str r0, [r4, #0x60]\n    movs r0, #0x6c\n    str r0, [r4, #0x14]\n    pop {r0, r1, r4, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM035_8895E_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am035_8895e(void)
{
    __asm__ volatile(
        "    push.w {r1, r2, r3, r4, r5, r6, r7, r8, sb, lr}\n    movs r5, r0\n    movs r6, r1\n    movs r7, r2\n    ldr r0, [r6, #0x34]\n    cmp r0, #1\n    blt L_open_cfw_runtime_am035_8895e_0016\n    ldr r0, [r6, #0x38]\n    cmp r0, #1\n    bge L_open_cfw_runtime_am035_8895e_0018\nL_open_cfw_runtime_am035_8895e_0016:\n    b L_open_cfw_runtime_am035_8895e_00d6\nL_open_cfw_runtime_am035_8895e_0018:\n    movs r1, r7\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am035_addr_004843ee\n    bl .\n    mov r8, r0\n    movs r0, #0x6c\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am035_addr_0044f718\n    bl .\n    movs r4, r0\n    cmp r4, #0\n    bne L_open_cfw_runtime_am035_8895e_005a\n    ldr.w r0, [pc, #0x58c]\n    str r0, [sp, #8]\n    ldr.w r0, [pc, #0x58c]\n    str r0, [sp, #4]\n    ldr.w r0, [pc, #0x588]\n    str r0, [sp]\n    ldr.w r3, [pc, #0x588]\n    movs r2, #0x4f\n    ldr.w r1, [pc, #0x584]\n    movs r0, #3\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am035_addr_0044d25c\n    bl .\nL_open_cfw_runtime_am035_8895e_0050:\n    movs r0, #0\n    movs.w r1, #-1\n    str r0, [r1]\n    b L_open_cfw_runtime_am035_8895e_0050\nL_open_cfw_runtime_am035_8895e_005a:\n    str.w r4, [r8, #0x54]\n    movs r2, #0x6c\n    movs r1, r6\n    ldr.w r0, [r8, #0x54]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am035_addr_00454738\n    bl .\n    movs r0, #7\n    strb.w r0, [r8, #4]\n    movs r0, #0\n    str.w r0, [r8, #0x50]\n    movs r0, r7\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am035_addr_004515a4\n    bl .\n    mov sb, r0\n    movs r0, r7\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am035_addr_00451598\n    bl .\n    adds.w r1, r6, #0x44\n    str r1, [sp, #8]\n    ldr r1, [r6, #0x38]\n    uxth r1, r1\n    str r1, [sp, #4]\n    ldr r1, [r6, #0x34]\n    uxth r1, r1\n    str r1, [sp]\n    ldr r3, [r6, #0x30]\n    mov r2, sb\n    movs r1, r0\n    adds.w r0, r8, #0x18\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am035_88cda\n    bl .\n    ldr r2, [r7, #4]\n    ldr r1, [r7]\n    adds.w r0, r8, #0x18\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am035_addr_00450bb2\n    bl .\n    ldr r0, [r4, #0x60]\n    ldr.w r1, [pc, #0x504]\n    cmp r0, r1\n    bne L_open_cfw_runtime_am035_8895e_00c6\n    adds.w r0, r4, #0x58\n    movs r1, r7\n    movs r2, #0x10\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am035_addr_00439c04\n    bl .\nL_open_cfw_runtime_am035_8895e_00c6:\n    ldr r0, [r6, #0x1c]\n    movs r1, #1\n    strb.w r1, [r0, #0x50]\n    mov r1, r8\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am035_addr_00484476\n    bl .\nL_open_cfw_runtime_am035_8895e_00d6:\n    pop.w {r0, r1, r2, r4, r5, r6, r7, r8, sb, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM035_88A38_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am035_88a38(void)
{
    __asm__ volatile(
        "    push.w {r4, r5, r6, r7, r8, lr}\n    sub sp, #0x98\n    movs r5, r0\n    movs r6, r1\n    movs r7, r2\n    ldr r0, [r6, #0x1c]\n    cmp r0, #0\n    bne L_open_cfw_runtime_am035_88a38_002a\n    ldr.w r0, [pc, #0x4e4]\n    str r0, [sp]\n    ldr.w r3, [pc, #0x4e0]\n    movs r2, #0x69\n    ldr.w r1, [pc, #0x4d4]\n    movs r0, #2\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am035_addr_0044d25c\n    bl .\n    b L_open_cfw_runtime_am035_88a38_027a\nL_open_cfw_runtime_am035_88a38_002a:\n    ldrb.w r0, [r6, #0x50]\n    cmp r0, #3\n    blt.w #0x488cb2\n    ldr r0, [r6, #0x34]\n    cmp r0, #1\n    blt L_open_cfw_runtime_am035_88a38_0040\n    ldr r0, [r6, #0x38]\n    cmp r0, #1\n    bge L_open_cfw_runtime_am035_88a38_0042\nL_open_cfw_runtime_am035_88a38_0040:\n    b L_open_cfw_runtime_am035_88a38_027a\nL_open_cfw_runtime_am035_88a38_0042:\n    movs r0, #0x6c\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am035_addr_0044f718\n    bl .\n    movs r4, r0\n    cmp r4, #0\n    bne L_open_cfw_runtime_am035_88a38_007a\n    ldr.w r0, [pc, #0x494]\n    str r0, [sp, #8]\n    ldr.w r0, [pc, #0x490]\n    str r0, [sp, #4]\n    ldr.w r0, [pc, #0x490]\n    str r0, [sp]\n    ldr.w r3, [pc, #0x498]\n    movs r2, #0x76\n    ldr.w r1, [pc, #0x48c]\n    movs r0, #3\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am035_addr_0044d25c\n    bl .\nL_open_cfw_runtime_am035_88a38_0070:\n    movs r0, #0\n    movs.w r1, #-1\n    str r0, [r1]\n    b L_open_cfw_runtime_am035_88a38_0070\nL_open_cfw_runtime_am035_88a38_007a:\n    movs r2, #0x6c\n    movs r1, r6\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am035_addr_00454738\n    bl .\n    adds.w r1, r4, #0x20\n    ldr r0, [r4, #0x1c]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am035_88f6a\n    bl .\n    uxtb r0, r0\n    cmp r0, #1\n    beq L_open_cfw_runtime_am035_88a38_00b2\n    ldr.w r0, [pc, #0x468]\n    str r0, [sp]\n    ldr.w r3, [pc, #0x460]\n    movs r2, #0x7a\n    ldr.w r1, [pc, #0x450]\n    movs r0, #2\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am035_addr_0044d25c\n    bl .\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am035_addr_0044f758\n    bl .\n    b L_open_cfw_runtime_am035_88a38_027a\nL_open_cfw_runtime_am035_88a38_00b2:\n    ldr r0, [r4, #0x60]\n    ldr.w r1, [pc, #0x428]\n    cmp r0, r1\n    bne L_open_cfw_runtime_am035_88a38_00c8\n    adds.w r0, r4, #0x58\n    movs r1, r7\n    movs r2, #0x10\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am035_addr_00439c04\n    bl .\nL_open_cfw_runtime_am035_88a38_00c8:\n    ldr r0, [r4, #0x20]\n    lsrs r0, r0, #0x10\n    lsls r0, r0, #0x19\n    bmi L_open_cfw_runtime_am035_88a38_0128\n    movs r1, r7\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am035_addr_004843ee\n    bl .\n    mov r8, r0\n    str.w r4, [r8, #0x54]\n    movs r0, #6\n    strb.w r0, [r8, #4]\n    movs r0, r7\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am035_addr_004515a4\n    bl .\n    movs r4, r0\n    movs r0, r7\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am035_addr_00451598\n    bl .\n    adds.w r1, r6, #0x44\n    str r1, [sp, #8]\n    ldr r1, [r6, #0x38]\n    uxth r1, r1\n    str r1, [sp, #4]\n    ldr r1, [r6, #0x34]\n    uxth r1, r1\n    str r1, [sp]\n    ldr r3, [r6, #0x30]\n    movs r2, r4\n    movs r1, r0\n    adds.w r0, r8, #0x18\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am035_88cda\n    bl .\n    ldr r2, [r7, #4]\n    ldr r1, [r7]\n    adds.w r0, r8, #0x18\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am035_addr_00450bb2\n    bl .\n    mov r1, r8\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am035_addr_00484476\n    bl .\n    b L_open_cfw_runtime_am035_88a38_027a\nL_open_cfw_runtime_am035_88a38_0128:\n    movs r2, #0\n    ldr r1, [r4, #0x1c]\n    add r0, sp, #0x4c\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am035_88f9c\n    bl .\n    uxtb r0, r0\n    cmp r0, #1\n    beq L_open_cfw_runtime_am035_88a38_0150\n    ldr.w r0, [pc, #0x3c8]\n    str r0, [sp]\n    ldr.w r3, [pc, #0x3bc]\n    movs r2, #0x97\n    ldr.w r1, [pc, #0x3ac]\n    movs r0, #3\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am035_addr_0044d25c\n    bl .\n    b L_open_cfw_runtime_am035_88a38_027a\nL_open_cfw_runtime_am035_88a38_0150:\n    ldr r0, [sp, #0x4c]\n    cmp r0, #0\n    beq.w #0x488cac\n    ldr r0, [sp, #0x4c]\n    ldr r0, [r0, #0x10]\n    cmp r0, #0\n    beq.w #0x488cac\n    add r0, sp, #0x3c\n    adds r1, r5, #4\n    movs r2, #0x10\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am035_addr_00439c04\n    bl .\n    add r0, sp, #0xc\n    movs r1, r7\n    movs r2, #0x10\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am035_addr_00439c04\n    bl .\n    add r0, sp, #0x2c\n    ldr r1, [r6]\n    adds r1, #0x14\n    movs r2, #0x10\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am035_addr_00439c04\n    bl .\n    ldr r0, [r5, #0x48]\n    cmp r0, #0\n    beq L_open_cfw_runtime_am035_88a38_01d0\n    add r2, sp, #0x2c\n    add r1, sp, #0xc\n    add r0, sp, #0xc\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am035_addr_00450bcc\n    bl .\n    cmp r0, #0\n    beq L_open_cfw_runtime_am035_88a38_0274\n    ldr r1, [r7]\n    ldr r0, [sp, #0x3c]\n    subs r1, r1, r0\n    ldr r2, [r7, #4]\n    ldr r0, [sp, #0x40]\n    subs r2, r2, r0\n    ldr r0, [r7, #4]\n    subs r2, r2, r0\n    ldr r0, [r7]\n    subs r1, r1, r0\n    add r0, sp, #0xc\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am035_addr_00450bb2\n    bl .\n    adds.w r0, r5, #0x18\n    add r1, sp, #0xc\n    movs r2, #0x10\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am035_addr_00439c04\n    bl .\n    add r0, sp, #0xc\n    str r0, [sp]\n    movs r3, r4\n    add r2, sp, #0xc\n    add r1, sp, #0x4c\n    movs r0, r5\n    ldr r5, [sp, #0x4c]\n    ldr r5, [r5, #0x10]\n    blx r5\n    b L_open_cfw_runtime_am035_88a38_0274\nL_open_cfw_runtime_am035_88a38_01d0:\n    add r0, sp, #0x1c\n    add r1, sp, #0x3c\n    movs r2, #0x10\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am035_addr_00439c04\n    bl .\n    add r2, sp, #0xc\n    add r1, sp, #0x1c\n    add r0, sp, #0x1c\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am035_addr_00450bcc\n    bl .\n    cmp r0, #0\n    beq L_open_cfw_runtime_am035_88a38_0274\n    movs r0, r7\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am035_addr_004515a4\n    bl .\n    mov r8, r0\n    movs r0, r7\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am035_addr_00451598\n    bl .\n    adds.w r1, r6, #0x44\n    str r1, [sp, #8]\n    ldr r1, [r6, #0x38]\n    uxth r1, r1\n    str r1, [sp, #4]\n    ldr r1, [r6, #0x34]\n    uxth r1, r1\n    str r1, [sp]\n    ldr r3, [r6, #0x30]\n    mov r2, r8\n    movs r1, r0\n    add r0, sp, #0xc\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am035_88cda\n    bl .\n    ldr r2, [r7, #4]\n    ldr r1, [r7]\n    add r0, sp, #0xc\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am035_addr_00450bb2\n    bl .\n    movs r0, r7\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am035_addr_004515a4\n    bl .\n    mov r8, r0\n    movs r0, r7\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am035_addr_00451598\n    bl .\n    adds.w r1, r6, #0x44\n    str r1, [sp, #8]\n    ldr r1, [r6, #0x38]\n    uxth r1, r1\n    str r1, [sp, #4]\n    ldr r1, [r6, #0x34]\n    uxth r1, r1\n    str r1, [sp]\n    ldr r3, [r6, #0x30]\n    mov r2, r8\n    movs r1, r0\n    add r0, sp, #0x1c\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am035_88cda\n    bl .\n    ldr r2, [r7, #4]\n    ldr r1, [r7]\n    add r0, sp, #0x1c\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am035_addr_00450bb2\n    bl .\n    add r2, sp, #0x2c\n    add r1, sp, #0x1c\n    add r0, sp, #0x1c\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am035_addr_00450bcc\n    bl .\n    cmp r0, #0\n    beq L_open_cfw_runtime_am035_88a38_0274\n    add r0, sp, #0x1c\n    str r0, [sp]\n    movs r3, r4\n    add r2, sp, #0xc\n    add r1, sp, #0x4c\n    movs r0, r5\n    ldr r5, [sp, #0x4c]\n    ldr r5, [r5, #0x10]\n    blx r5\nL_open_cfw_runtime_am035_88a38_0274:\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am035_addr_0044f758\n    bl .\nL_open_cfw_runtime_am035_88a38_027a:\n    add sp, #0x98\n    pop.w {r4, r5, r6, r7, r8, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM035_88CB8_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am035_88cb8(void)
{
    __asm__ volatile(
        "    cmp r0, #0\n    bne L_open_cfw_runtime_am035_88cb8_0008\n    movs r0, #3\n    b L_open_cfw_runtime_am035_88cb8_0020\nL_open_cfw_runtime_am035_88cb8_0008:\n    ldrb r1, [r0]\n    subs r1, #0x20\n    cmp r1, #0x60\n    bhs L_open_cfw_runtime_am035_88cb8_0014\n    movs r0, #1\n    b L_open_cfw_runtime_am035_88cb8_0020\nL_open_cfw_runtime_am035_88cb8_0014:\n    ldrb r0, [r0]\n    cmp r0, #0x80\n    blt L_open_cfw_runtime_am035_88cb8_001e\n    movs r0, #2\n    b L_open_cfw_runtime_am035_88cb8_0020\nL_open_cfw_runtime_am035_88cb8_001e:\n    movs r0, #0\nL_open_cfw_runtime_am035_88cb8_0020:\n    bx lr\n"
    );
}
#endif

#if defined(OPEN_CFW_AM035_88CDA_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am035_88cda(void)
{
    __asm__ volatile(
        "    push.w {r3, r4, r5, r6, r7, r8, sb, sl, fp, lr}\n    sub sp, #0x28\n    movs r7, r0\n    mov r8, r1\n    mov sl, r2\n    movs r4, r3\n    ldr r5, [sp, #0x50]\n    ldr r6, [sp, #0x54]\n    cmp r4, #0\n    bne L_open_cfw_runtime_am035_88cda_0044\n    movs r0, r5\n    uxth r0, r0\n    cmp.w r0, #0x100\n    bne L_open_cfw_runtime_am035_88cda_0044\n    movs r0, r6\n    uxth r0, r0\n    cmp.w r0, #0x100\n    bne L_open_cfw_runtime_am035_88cda_0044\n    movs r0, #0\n    str r0, [r7]\n    movs r0, #0\n    str r0, [r7, #4]\n    subs.w r8, r8, #1\n    str.w r8, [r7, #8]\n    subs.w sl, sl, #1\n    str.w sl, [r7, #0xc]\n    b L_open_cfw_runtime_am035_88cda_0238\nL_open_cfw_runtime_am035_88cda_0044:\n    ldr.w sb, [sp, #0x58]\n    add r0, sp, #8\n    movs r1, #0x20\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am035_addr_0048949c\n    bl .\n    add.w fp, sp, #8\n    str.w r8, [fp, #8]\n    str.w sl, [fp, #0x14]\n    str.w r8, [fp, #0x18]\n    str.w sl, [fp, #0x1c]\n    movs r0, #1\n    str r0, [sp, #4]\n    str.w sb, [sp]\n    movs r3, r6\n    uxth r3, r3\n    movs r2, r5\n    uxth r2, r2\n    movs r1, r4\n    add r0, sp, #8\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am035_addr_004513ae\n    bl .\n    movs r0, #1\n    str r0, [sp, #4]\n    str.w sb, [sp]\n    movs r3, r6\n    uxth r3, r3\n    movs r2, r5\n    uxth r2, r2\n    movs r1, r4\n    add r0, sp, #0x10\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am035_addr_004513ae\n    bl .\n    movs r0, #1\n    str r0, [sp, #4]\n    str.w sb, [sp]\n    movs r3, r6\n    uxth r3, r3\n    movs r2, r5\n    uxth r2, r2\n    movs r1, r4\n    add r0, sp, #0x18\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am035_addr_004513ae\n    bl .\n    movs r0, #1\n    str r0, [sp, #4]\n    str.w sb, [sp]\n    uxth r6, r6\n    movs r3, r6\n    uxth r5, r5\n    movs r2, r5\n    movs r1, r4\n    add r0, sp, #0x20\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am035_addr_004513ae\n    bl .\n    ldr r0, [sp, #8]\n    ldr.w r1, [fp, #8]\n    cmp r0, r1\n    bge L_open_cfw_runtime_am035_88cda_00d2\n    ldr r0, [sp, #8]\n    b L_open_cfw_runtime_am035_88cda_00d6\nL_open_cfw_runtime_am035_88cda_00d2:\n    ldr.w r0, [fp, #8]\nL_open_cfw_runtime_am035_88cda_00d6:\n    ldr.w r1, [fp, #0x10]\n    ldr.w r2, [fp, #0x18]\n    cmp r1, r2\n    bge L_open_cfw_runtime_am035_88cda_00e8\n    ldr.w r1, [fp, #0x10]\n    b L_open_cfw_runtime_am035_88cda_00ec\nL_open_cfw_runtime_am035_88cda_00e8:\n    ldr.w r1, [fp, #0x18]\nL_open_cfw_runtime_am035_88cda_00ec:\n    cmp r0, r1\n    bge L_open_cfw_runtime_am035_88cda_0104\n    ldr r0, [sp, #8]\n    ldr.w r1, [fp, #8]\n    cmp r0, r1\n    bge L_open_cfw_runtime_am035_88cda_00fe\n    ldr r0, [sp, #8]\n    b L_open_cfw_runtime_am035_88cda_011a\nL_open_cfw_runtime_am035_88cda_00fe:\n    ldr.w r0, [fp, #8]\n    b L_open_cfw_runtime_am035_88cda_011a\nL_open_cfw_runtime_am035_88cda_0104:\n    ldr.w r0, [fp, #0x10]\n    ldr.w r1, [fp, #0x18]\n    cmp r0, r1\n    bge L_open_cfw_runtime_am035_88cda_0116\n    ldr.w r0, [fp, #0x10]\n    b L_open_cfw_runtime_am035_88cda_011a\nL_open_cfw_runtime_am035_88cda_0116:\n    ldr.w r0, [fp, #0x18]\nL_open_cfw_runtime_am035_88cda_011a:\n    str r0, [r7]\n    ldr.w r0, [fp, #0x18]\n    ldr.w r1, [fp, #0x10]\n    cmp r0, r1\n    bge L_open_cfw_runtime_am035_88cda_012e\n    ldr.w r0, [fp, #0x10]\n    b L_open_cfw_runtime_am035_88cda_0132\nL_open_cfw_runtime_am035_88cda_012e:\n    ldr.w r0, [fp, #0x18]\nL_open_cfw_runtime_am035_88cda_0132:\n    ldr.w r1, [fp, #8]\n    ldr r2, [sp, #8]\n    cmp r1, r2\n    bge L_open_cfw_runtime_am035_88cda_0140\n    ldr r1, [sp, #8]\n    b L_open_cfw_runtime_am035_88cda_0144\nL_open_cfw_runtime_am035_88cda_0140:\n    ldr.w r1, [fp, #8]\nL_open_cfw_runtime_am035_88cda_0144:\n    cmp r0, r1\n    bge L_open_cfw_runtime_am035_88cda_015c\n    ldr.w r0, [fp, #8]\n    ldr r1, [sp, #8]\n    cmp r0, r1\n    bge L_open_cfw_runtime_am035_88cda_0156\n    ldr r0, [sp, #8]\n    b L_open_cfw_runtime_am035_88cda_0172\nL_open_cfw_runtime_am035_88cda_0156:\n    ldr.w r0, [fp, #8]\n    b L_open_cfw_runtime_am035_88cda_0172\nL_open_cfw_runtime_am035_88cda_015c:\n    ldr.w r0, [fp, #0x18]\n    ldr.w r1, [fp, #0x10]\n    cmp r0, r1\n    bge L_open_cfw_runtime_am035_88cda_016e\n    ldr.w r0, [fp, #0x10]\n    b L_open_cfw_runtime_am035_88cda_0172\nL_open_cfw_runtime_am035_88cda_016e:\n    ldr.w r0, [fp, #0x18]\nL_open_cfw_runtime_am035_88cda_0172:\n    subs r0, r0, #1\n    str r0, [r7, #8]\n    ldr.w r0, [fp, #4]\n    ldr.w r1, [fp, #0xc]\n    cmp r0, r1\n    bge L_open_cfw_runtime_am035_88cda_0188\n    ldr.w r0, [fp, #4]\n    b L_open_cfw_runtime_am035_88cda_018c\nL_open_cfw_runtime_am035_88cda_0188:\n    ldr.w r0, [fp, #0xc]\nL_open_cfw_runtime_am035_88cda_018c:\n    ldr.w r1, [fp, #0x14]\n    ldr.w r2, [fp, #0x1c]\n    cmp r1, r2\n    bge L_open_cfw_runtime_am035_88cda_019e\n    ldr.w r1, [fp, #0x14]\n    b L_open_cfw_runtime_am035_88cda_01a2\nL_open_cfw_runtime_am035_88cda_019e:\n    ldr.w r1, [fp, #0x1c]\nL_open_cfw_runtime_am035_88cda_01a2:\n    cmp r0, r1\n    bge L_open_cfw_runtime_am035_88cda_01be\n    ldr.w r0, [fp, #4]\n    ldr.w r1, [fp, #0xc]\n    cmp r0, r1\n    bge L_open_cfw_runtime_am035_88cda_01b8\n    ldr.w r0, [fp, #4]\n    b L_open_cfw_runtime_am035_88cda_01d4\nL_open_cfw_runtime_am035_88cda_01b8:\n    ldr.w r0, [fp, #0xc]\n    b L_open_cfw_runtime_am035_88cda_01d4\nL_open_cfw_runtime_am035_88cda_01be:\n    ldr.w r0, [fp, #0x14]\n    ldr.w r1, [fp, #0x1c]\n    cmp r0, r1\n    bge L_open_cfw_runtime_am035_88cda_01d0\n    ldr.w r0, [fp, #0x14]\n    b L_open_cfw_runtime_am035_88cda_01d4\nL_open_cfw_runtime_am035_88cda_01d0:\n    ldr.w r0, [fp, #0x1c]\nL_open_cfw_runtime_am035_88cda_01d4:\n    str r0, [r7, #4]\n    ldr.w r0, [fp, #0x1c]\n    ldr.w r1, [fp, #0x14]\n    cmp r0, r1\n    bge L_open_cfw_runtime_am035_88cda_01e8\n    ldr.w r0, [fp, #0x14]\n    b L_open_cfw_runtime_am035_88cda_01ec\nL_open_cfw_runtime_am035_88cda_01e8:\n    ldr.w r0, [fp, #0x1c]\nL_open_cfw_runtime_am035_88cda_01ec:\n    ldr.w r1, [fp, #0xc]\n    ldr.w r2, [fp, #4]\n    cmp r1, r2\n    bge L_open_cfw_runtime_am035_88cda_01fe\n    ldr.w r1, [fp, #4]\n    b L_open_cfw_runtime_am035_88cda_0202\nL_open_cfw_runtime_am035_88cda_01fe:\n    ldr.w r1, [fp, #0xc]\nL_open_cfw_runtime_am035_88cda_0202:\n    cmp r0, r1\n    bge L_open_cfw_runtime_am035_88cda_021e\n    ldr.w r0, [fp, #0xc]\n    ldr.w r1, [fp, #4]\n    cmp r0, r1\n    bge L_open_cfw_runtime_am035_88cda_0218\n    ldr.w r0, [fp, #4]\n    b L_open_cfw_runtime_am035_88cda_0234\nL_open_cfw_runtime_am035_88cda_0218:\n    ldr.w r0, [fp, #0xc]\n    b L_open_cfw_runtime_am035_88cda_0234\nL_open_cfw_runtime_am035_88cda_021e:\n    ldr.w r0, [fp, #0x1c]\n    ldr.w r1, [fp, #0x14]\n    cmp r0, r1\n    bge L_open_cfw_runtime_am035_88cda_0230\n    ldr.w r0, [fp, #0x14]\n    b L_open_cfw_runtime_am035_88cda_0234\nL_open_cfw_runtime_am035_88cda_0230:\n    ldr.w r0, [fp, #0x1c]\nL_open_cfw_runtime_am035_88cda_0234:\n    subs r0, r0, #1\n    str r0, [r7, #0xc]\nL_open_cfw_runtime_am035_88cda_0238:\n    add sp, #0x2c\n    pop.w {r4, r5, r6, r7, r8, sb, sl, fp, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM035_88F40_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am035_88f40(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    movs r2, r1\n    movs r1, #0\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am035_addr_00454746\n    bl .\n    pop {r0, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM035_88F4C_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am035_88f4c(void)
{
    __asm__ volatile(
        "    push {r3, r4, r5, lr}\n    movs r4, r0\n    movs r5, r1\n    movs r1, #0x1c\n    ldr.w r0, [pc, #0x4c4]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am035_addr_00482b00\n    bl .\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am035_addr_004d4ad4\n    bl .\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am035_addr_004d4bdc\n    bl .\n    pop {r0, r4, r5, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM035_88F6A_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am035_88f6a(void)
{
    __asm__ volatile(
        "    push {r4, r5, lr}\n    sub sp, #0x4c\n    movs r4, r0\n    movs r5, r1\n    movs r1, #0x4c\n    mov r0, sp\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am035_88f40\n    bl .\n    str r4, [sp, #0xc]\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am035_88cb8\n    bl .\n    strb.w r0, [sp, #0x10]\n    movs r1, r5\n    mov r0, sp\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am035_8925a\n    bl .\n    cmp r0, #0\n    bne L_open_cfw_runtime_am035_88f6a_002c\n    movs r0, #0\n    b L_open_cfw_runtime_am035_88f6a_002e\nL_open_cfw_runtime_am035_88f6a_002c:\n    movs r0, #1\nL_open_cfw_runtime_am035_88f6a_002e:\n    add sp, #0x4c\n    pop {r4, r5, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM035_88F9C_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am035_88f9c(void)
{
    __asm__ volatile(
        "    push {r0, r1, r2, r3, r4, r5, r6, lr}\n    movs r6, r0\n    movs r5, r1\n    movs r4, r2\n    movs r1, #0x4c\n    movs r0, r6\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am035_88f40\n    bl .\n    cmp r5, #0\n    bne L_open_cfw_runtime_am035_88f9c_0018\n    movs r0, #0\n    b L_open_cfw_runtime_am035_88f9c_00ec\nL_open_cfw_runtime_am035_88f9c_0018:\n    str r5, [r6, #0xc]\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am035_88cb8\n    bl .\n    strb r0, [r6, #0x10]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am035_addr_004d4b24\n    bl .\n    cmp r0, #0\n    beq L_open_cfw_runtime_am035_88f9c_004c\n    ldr.w r0, [pc, #0x458]\n    ldr.w r0, [r0, #0x134]\n    str r0, [r6, #0x40]\n    cmp r4, #0\n    beq L_open_cfw_runtime_am035_88f9c_003e\n    ldrb r0, [r4, #2]\n    cmp r0, #0\n    bne L_open_cfw_runtime_am035_88f9c_004c\nL_open_cfw_runtime_am035_88f9c_003e:\n    movs r0, r6\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am035_89460\n    bl .\n    cmp r0, #1\n    bne L_open_cfw_runtime_am035_88f9c_004c\n    movs r0, #1\n    b L_open_cfw_runtime_am035_88f9c_00ec\nL_open_cfw_runtime_am035_88f9c_004c:\n    adds.w r1, r6, #0x20\n    movs r0, r6\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am035_8925a\n    bl .\n    str r0, [r6]\n    ldr r0, [r6]\n    cmp r0, #0\n    bne L_open_cfw_runtime_am035_88f9c_0062\n    movs r0, #0\n    b L_open_cfw_runtime_am035_88f9c_00ec\nL_open_cfw_runtime_am035_88f9c_0062:\n    cmp r4, #0\n    beq L_open_cfw_runtime_am035_88f9c_0072\n    mov r0, sp\n    movs r1, r4\n    movs r2, #5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am035_addr_00439be4\n    bl .\n    b L_open_cfw_runtime_am035_88f9c_007a\nL_open_cfw_runtime_am035_88f9c_0072:\n    mov r0, sp\n    movs r1, #5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am035_addr_004d4ccc\n    bl .\nL_open_cfw_runtime_am035_88f9c_007a:\n    adds r0, r6, #4\n    mov r1, sp\n    movs r2, #5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am035_addr_00439be4\n    bl .\n    movs r1, r6\n    ldr r0, [r6]\n    ldr r2, [r6]\n    ldr r2, [r2, #4]\n    blx r2\n    movs r4, r0\n    movs r0, r4\n    uxtb r0, r0\n    cmp r0, #1\n    bne L_open_cfw_runtime_am035_88f9c_00e8\n    ldr r0, [r6, #0x2c]\n    cmp r0, #0\n    beq L_open_cfw_runtime_am035_88f9c_00e8\n    ldr r0, [r6, #0x2c]\n    ldr r0, [r0, #0x14]\n    cmp r0, #0\n    beq L_open_cfw_runtime_am035_88f9c_00ae\n    ldr r0, [r6, #0x2c]\n    ldr r0, [r0, #0x18]\n    cmp r0, #0\n    bne L_open_cfw_runtime_am035_88f9c_00da\nL_open_cfw_runtime_am035_88f9c_00ae:\n    ldr.w r0, [pc, #0x3d8]\n    str r0, [sp, #8]\n    ldr.w r0, [pc, #0x3d4]\n    str r0, [sp, #4]\n    ldr.w r0, [pc, #0x3d4]\n    str r0, [sp]\n    ldr.w r3, [pc, #0x3d0]\n    movs r2, #0x84\n    ldr.w r1, [pc, #0x3d0]\n    movs r0, #3\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am035_addr_0044d25c\n    bl .\nL_open_cfw_runtime_am035_88f9c_00d0:\n    movs r0, #0\n    movs.w r1, #-1\n    str r0, [r1]\n    b L_open_cfw_runtime_am035_88f9c_00d0\nL_open_cfw_runtime_am035_88f9c_00da:\n    ldrb r0, [r6, #8]\n    cmp r0, #0\n    beq L_open_cfw_runtime_am035_88f9c_00e8\n    movs r1, #0\n    ldr r0, [r6, #0x2c]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am035_addr_0048abb8\n    bl .\nL_open_cfw_runtime_am035_88f9c_00e8:\n    movs r0, r4\n    uxtb r0, r0\nL_open_cfw_runtime_am035_88f9c_00ec:\n    add sp, #0x10\n    pop {r4, r5, r6, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM035_8908C_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am035_8908c(void)
{
    __asm__ volatile(
        "    push {r4, lr}\n    movs r4, r0\n    ldr r0, [r4]\n    cmp r0, #0\n    beq L_open_cfw_runtime_am035_8908c_003a\n    ldr r0, [r4]\n    ldr r0, [r0, #0xc]\n    cmp r0, #0\n    beq L_open_cfw_runtime_am035_8908c_001c\n    movs r1, r4\n    ldr r0, [r4]\n    ldr r2, [r4]\n    ldr r2, [r2, #0xc]\n    blx r2\nL_open_cfw_runtime_am035_8908c_001c:\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am035_addr_004d4b24\n    bl .\n    cmp r0, #0\n    beq L_open_cfw_runtime_am035_8908c_003a\n    ldr r0, [r4, #0x40]\n    cmp r0, #0\n    beq L_open_cfw_runtime_am035_8908c_003a\n    ldr r0, [r4, #0x44]\n    cmp r0, #0\n    beq L_open_cfw_runtime_am035_8908c_003a\n    movs r2, #0\n    ldr r1, [r4, #0x44]\n    ldr r0, [r4, #0x40]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am035_addr_004d4e72\n    bl .\nL_open_cfw_runtime_am035_8908c_003a:\n    pop {r4, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM035_890C8_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am035_890c8(void)
{
    __asm__ volatile(
        "    push {r0, r1, r2, r3, r4, lr}\n    ldr.w r0, [pc, #0x350]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am035_addr_00482b12\n    bl .\n    movs r4, r0\n    cmp r4, #0\n    bne L_open_cfw_runtime_am035_890c8_003c\n    ldr.w r0, [pc, #0x35c]\n    str r0, [sp, #8]\n    ldr.w r0, [pc, #0x35c]\n    str r0, [sp, #4]\n    ldr.w r0, [pc, #0x344]\n    str r0, [sp]\n    ldr.w r3, [pc, #0x354]\n    movs r2, #0xb3\n    ldr.w r1, [pc, #0x340]\n    movs r0, #3\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am035_addr_0044d25c\n    bl .\nL_open_cfw_runtime_am035_890c8_0032:\n    movs r0, #0\n    movs.w r1, #-1\n    str r0, [r1]\n    b L_open_cfw_runtime_am035_890c8_0032\nL_open_cfw_runtime_am035_890c8_003c:\n    cmp r4, #0\n    bne L_open_cfw_runtime_am035_890c8_0044\n    movs r0, #0\n    b L_open_cfw_runtime_am035_890c8_004e\nL_open_cfw_runtime_am035_890c8_0044:\n    movs r1, #0x1c\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am035_88f40\n    bl .\n    movs r0, r4\nL_open_cfw_runtime_am035_890c8_004e:\n    add sp, #0x10\n    pop {r4, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM035_8911A_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am035_8911a(void)
{
    __asm__ volatile(
        "    push.w {r4, r5, r6, r7, r8, lr}\n    movs r5, r0\n    movs r6, r2\n    movs r7, r3\n    movs r2, #0\n    ldr r0, [pc, #0x2f8]\n    ldr.w r0, [r0, #0x134]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am035_addr_004d4eea\n    bl .\n    movs r4, r0\n    cmp r4, #0\n    bne L_open_cfw_runtime_am035_8911a_0020\n    movs r0, #0\n    b L_open_cfw_runtime_am035_8911a_004a\nL_open_cfw_runtime_am035_8911a_0020:\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am035_addr_004d5396\n    bl .\n    mov r8, r0\n    str.w r6, [r8, #0xc]\n    ldrb.w r0, [r8, #8]\n    cmp r0, #1\n    bne L_open_cfw_runtime_am035_8911a_0040\n    ldr.w r0, [r8, #4]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am035_addr_004547c6\n    bl .\n    str.w r0, [r8, #4]\nL_open_cfw_runtime_am035_8911a_0040:\n    str.w r7, [r8, #0x14]\n    str.w r5, [r8, #0x10]\n    movs r0, r4\nL_open_cfw_runtime_am035_8911a_004a:\n    pop.w {r4, r5, r6, r7, r8, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM035_89168_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am035_89168(void)
{
    __asm__ volatile(
        "    push {r2, r3, r4, r5, r6, lr}\n    movs r4, r1\n    cmp r4, #0\n    bne L_open_cfw_runtime_am035_89168_000c\n    movs r0, #0\n    b L_open_cfw_runtime_am035_89168_00f0\nL_open_cfw_runtime_am035_89168_000c:\n    adds r6, r0, #4\n    ldrb r0, [r6]\n    cmp r0, #0\n    beq L_open_cfw_runtime_am035_89168_0084\n    ldr r0, [r4]\n    ubfx r0, r0, #8, #8\n    cmp r0, #0x14\n    beq L_open_cfw_runtime_am035_89168_0084\n    ldr r1, [r4]\n    lsrs r1, r1, #8\n    uxtb r1, r1\n    ldr r0, [r4, #4]\n    uxth r0, r0\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am035_addr_0048aad8\n    bl .\n    movs r5, r0\n    ldr r0, [r4, #8]\n    uxth r0, r0\n    cmp r0, r5\n    beq L_open_cfw_runtime_am035_89168_0084\n    movs r1, r5\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am035_addr_0048b34e\n    bl .\n    uxtb r0, r0\n    cmp r0, #1\n    beq L_open_cfw_runtime_am035_89168_0084\n    str r5, [sp]\n    ldr r3, [r4]\n    lsrs r3, r3, #8\n    uxtb r3, r3\n    ldr r2, [r4, #4]\n    lsrs r2, r2, #0x10\n    ldr r1, [r4, #4]\n    uxth r1, r1\n    ldr r0, [pc, #0x284]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am035_addr_0048b010\n    bl .\n    movs r5, r0\n    cmp r5, #0\n    bne L_open_cfw_runtime_am035_89168_0076\n    ldr r0, [pc, #0x27c]\n    str r0, [sp]\n    ldr r3, [pc, #0x27c]\n    mov.w r2, #0x102\n    ldr r1, [pc, #0x260]\n    movs r0, #3\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am035_addr_0044d25c\n    bl .\n    movs r0, #0\n    b L_open_cfw_runtime_am035_89168_00f0\nL_open_cfw_runtime_am035_89168_0076:\n    movs r3, #0\n    movs r2, r4\n    movs r1, #0\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am035_addr_0048ad42\n    bl .\n    movs r4, r5\nL_open_cfw_runtime_am035_89168_0084:\n    ldrb r0, [r6, #1]\n    cmp r0, #0\n    beq L_open_cfw_runtime_am035_89168_00ee\n    ldr r0, [r4]\n    ubfx r0, r0, #8, #8\n    subs r0, #0xb\n    cmp r0, #4\n    blo L_open_cfw_runtime_am035_89168_00ee\n    ldr r0, [r4]\n    lsrs r0, r0, #8\n    uxtb r0, r0\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am035_addr_00440fc4\n    bl .\n    cmp r0, #0\n    beq L_open_cfw_runtime_am035_89168_00ee\n    movs r1, #1\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am035_addr_0048b73c\n    bl .\n    cmp r0, #0\n    bne L_open_cfw_runtime_am035_89168_00ee\n    movs r1, #0x20\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am035_addr_0048b73c\n    bl .\n    cmp r0, #0\n    beq L_open_cfw_runtime_am035_89168_00c4\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am035_addr_0048b540\n    bl .\n    b L_open_cfw_runtime_am035_89168_00ee\nL_open_cfw_runtime_am035_89168_00c4:\n    movs r1, r4\n    ldr r0, [pc, #0x214]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am035_addr_0048b134\n    bl .\n    movs r4, r0\n    cmp r4, #0\n    bne L_open_cfw_runtime_am035_89168_00e8\n    ldr r0, [pc, #0x214]\n    str r0, [sp]\n    ldr r3, [pc, #0x20c]\n    mov.w r2, #0x11a\n    ldr r1, [pc, #0x1ec]\n    movs r0, #3\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am035_addr_0044d25c\n    bl .\n    movs r0, #0\n    b L_open_cfw_runtime_am035_89168_00f0\nL_open_cfw_runtime_am035_89168_00e8:\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am035_addr_0048b540\n    bl .\nL_open_cfw_runtime_am035_89168_00ee:\n    movs r0, r4\nL_open_cfw_runtime_am035_89168_00f0:\n    pop {r1, r2, r4, r5, r6, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM035_8925A_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am035_8925a(void)
{
    __asm__ volatile(
        "    push.w {r3, r4, r5, r6, r7, r8, sb, sl, fp, lr}\n    sub sp, #0x30\n    movs r5, r0\n    movs r6, r1\n    movs r1, #0xc\n    movs r0, r6\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am035_88f40\n    bl .\n    ldr r7, [r5, #0xc]\n    ldrb.w r8, [r5, #0x10]\n    mov r0, r8\n    uxtb r0, r0\n    cmp r0, #0\n    bne L_open_cfw_runtime_am035_8925a_002c\n    movs r0, r7\n    ldr r0, [r0, #0x10]\n    cmp r0, #0\n    bne L_open_cfw_runtime_am035_8925a_002c\n    movs r0, #0\n    b L_open_cfw_runtime_am035_8925a_0186\nL_open_cfw_runtime_am035_8925a_002c:\n    mov r0, r8\n    uxtb r0, r0\n    cmp r0, #1\n    beq L_open_cfw_runtime_am035_8925a_0034\nL_open_cfw_runtime_am035_8925a_0034:\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am035_addr_004d4c2c\n    bl .\n    mov sb, r0\n    mov r0, sb\n    uxtb r0, r0\n    cmp r0, #0\n    beq L_open_cfw_runtime_am035_8925a_008a\n    mov r0, r8\n    uxtb r0, r0\n    cmp r0, #1\n    bne L_open_cfw_runtime_am035_8925a_008a\n    strb.w r8, [sp, #0x1c]\n    str r7, [sp, #0x18]\n    ldr.w sl, [pc, #0x174]\n    movs r2, #0\n    add r1, sp, #0x18\n    ldr.w r0, [sl, #0x138]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am035_addr_004d4dca\n    bl .\n    movs r4, r0\n    cmp r4, #0\n    beq L_open_cfw_runtime_am035_8925a_008a\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am035_addr_004d5396\n    bl .\n    adds.w r1, r0, #8\n    ldm.w r1, {r2, r3, r5}\n    stm.w r6, {r2, r3, r5}\n    ldr r5, [r0, #0x14]\n    movs r2, #0\n    movs r1, r4\n    ldr.w r0, [sl, #0x138]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am035_addr_004d4e72\n    bl .\n    movs r0, r5\n    b L_open_cfw_runtime_am035_8925a_0186\nL_open_cfw_runtime_am035_8925a_008a:\n    mov r0, r8\n    uxtb r0, r0\n    cmp r0, #1\n    bne L_open_cfw_runtime_am035_8925a_00c0\n    movs r2, #2\n    movs r1, r7\n    adds.w r0, r5, #0x14\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am035_addr_004c6d9a\n    bl .\n    movs r1, r0\n    uxtb r1, r1\n    cmp r1, #0\n    beq L_open_cfw_runtime_am035_8925a_00c0\n    uxtb r0, r0\n    str r0, [sp, #4]\n    ldr r0, [pc, #0x14c]\n    str r0, [sp]\n    ldr r3, [pc, #0x14c]\n    mov.w r2, #0x150\n    ldr r1, [pc, #0x124]\n    movs r0, #3\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am035_addr_0044d25c\n    bl .\n    movs r0, #0\n    b L_open_cfw_runtime_am035_8925a_0186\nL_open_cfw_runtime_am035_8925a_00c0:\n    ldr.w sl, [pc, #0x104]\n    adds.w fp, sl, #0x128\n    mov r0, fp\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am035_addr_00482cd8\n    bl .\n    movs r4, r0\n    b L_open_cfw_runtime_am035_8925a_00dc\nL_open_cfw_runtime_am035_8925a_00d2:\n    movs r1, r4\n    mov r0, fp\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am035_addr_00482cf0\n    bl .\n    movs r4, r0\nL_open_cfw_runtime_am035_8925a_00dc:\n    cmp r4, #0\n    beq L_open_cfw_runtime_am035_8925a_011c\n    ldr r0, [r4]\n    cmp r0, #0\n    beq L_open_cfw_runtime_am035_8925a_00d2\n    ldr r0, [r4, #4]\n    cmp r0, #0\n    beq L_open_cfw_runtime_am035_8925a_00d2\n    movs r2, #0\n    movs r1, #0\n    adds.w r0, r5, #0x14\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am035_addr_004c6fba\n    bl .\n    movs r2, r6\n    movs r1, r5\n    movs r0, r4\n    ldr r3, [r4]\n    blx r3\n    uxtb r0, r0\n    cmp r0, #1\n    bne L_open_cfw_runtime_am035_8925a_00d2\n    ldr r0, [r6, #8]\n    lsls r0, r0, #0x10\n    bne L_open_cfw_runtime_am035_8925a_011c\n    movs r0, r6\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am035_893e6\n    bl .\n    ldr r1, [r6, #8]\n    bfi r1, r0, #0, #0x10\n    str r1, [r6, #8]\nL_open_cfw_runtime_am035_8925a_011c:\n    cmp r4, #0\n    beq L_open_cfw_runtime_am035_8925a_0120\nL_open_cfw_runtime_am035_8925a_0120:\n    mov r0, r8\n    uxtb r0, r0\n    cmp r0, #1\n    bne L_open_cfw_runtime_am035_8925a_0130\n    adds.w r0, r5, #0x14\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am035_addr_004c6ee0\n    bl .\nL_open_cfw_runtime_am035_8925a_0130:\n    uxtb.w sb, sb\n    cmp.w sb, #0\n    beq L_open_cfw_runtime_am035_8925a_0184\n    mov r0, r8\n    uxtb r0, r0\n    cmp r0, #1\n    bne L_open_cfw_runtime_am035_8925a_0184\n    cmp r4, #0\n    beq L_open_cfw_runtime_am035_8925a_0184\n    strb.w r8, [sp, #4]\n    movs r0, r7\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am035_addr_004547c6\n    bl .\n    str r0, [sp]\n    str r4, [sp, #0x14]\n    add r0, sp, #8\n    ldm.w r6, {r1, r2, r3}\n    stm.w r0, {r1, r2, r3}\n    movs r2, #0\n    mov r1, sp\n    ldr.w r0, [sl, #0x138]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am035_addr_004d4eea\n    bl .\n    cmp r0, #0\n    bne L_open_cfw_runtime_am035_8925a_0178\n    ldr r0, [sp]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am035_addr_0044f758\n    bl .\n    movs r0, #0\n    b L_open_cfw_runtime_am035_8925a_0186\nL_open_cfw_runtime_am035_8925a_0178:\n    movs r2, #0\n    movs r1, r0\n    ldr.w r0, [sl, #0x138]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am035_addr_004d4e72\n    bl .\nL_open_cfw_runtime_am035_8925a_0184:\n    movs r0, r4\nL_open_cfw_runtime_am035_8925a_0186:\n    add sp, #0x34\n    pop.w {r4, r5, r6, r7, r8, sb, sl, fp, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM035_893E6_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am035_893e6(void)
{
    __asm__ volatile(
        "    push {r4, lr}\n    movs r4, r0\n    ldr r0, [r4]\n    ubfx r0, r0, #8, #8\n    cmp r0, #0x14\n    bne L_open_cfw_runtime_am035_893e6_0018\n    ldr r1, [r4, #4]\n    ldr r0, [pc, #0x64]\n    ands.w r0, r0, r1, lsl #1\n    b L_open_cfw_runtime_am035_893e6_0030\nL_open_cfw_runtime_am035_893e6_0018:\n    ldr r0, [r4]\n    lsrs r0, r0, #8\n    uxtb r0, r0\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am035_addr_00440f44\n    bl .\n    ldr r1, [r4, #4]\n    uxth r1, r1\n    uxtb r0, r0\n    mul r0, r0, r1\n    adds r0, r0, #7\n    lsrs r0, r0, #3\nL_open_cfw_runtime_am035_893e6_0030:\n    pop {r4, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM035_89460_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am035_89460(void)
{
    __asm__ volatile(
        "    push {r3, r4, r5, lr}\n    sub sp, #0x18\n    movs r5, r0\n    ldr r0, [r5, #0x40]\n    ldrb r1, [r5, #0x10]\n    strb.w r1, [sp, #8]\n    ldr r1, [r5, #0xc]\n    str r1, [sp, #4]\n    movs r2, #0\n    mov r1, sp\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am035_addr_004d4dca\n    bl .\n    movs r4, r0\n    cmp r4, #0\n    beq L_open_cfw_runtime_am035_89460_0034\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am035_addr_004d5396\n    bl .\n    ldr r1, [r0, #0xc]\n    str r1, [r5, #0x2c]\n    ldr r0, [r0, #0x10]\n    str r0, [r5]\n    str r4, [r5, #0x44]\n    movs r0, #1\n    b L_open_cfw_runtime_am035_89460_0036\nL_open_cfw_runtime_am035_89460_0034:\n    movs r0, #0\nL_open_cfw_runtime_am035_89460_0036:\n    add sp, #0x1c\n    pop {r4, r5, pc}\n"
    );
}
#endif
