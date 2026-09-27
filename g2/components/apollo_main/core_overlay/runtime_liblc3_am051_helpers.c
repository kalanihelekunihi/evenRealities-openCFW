/*
 * SPDX-License-Identifier: MIT
 *
 * Source-owned exact helpers from the AM-051 retained island.
 */

#if defined(OPEN_CFW_AM051_B201E_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am051_b201e(void)
{
    __asm__ volatile(
        "    movs r2, r1\n    movw r1, #0x366a\n    muls r2, r1, r2\n    adds.w r0, r0, r2, asr #16\n    bx lr\n"
    );
}
#endif

#if defined(OPEN_CFW_AM051_B202C_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am051_b202c(void)
{
    __asm__ volatile(
        "    push {r3, r4, r5, lr}\n    movs r4, r0\n    movs r5, r1\n    lsls r0, r5, #1\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am051_addr_005293c0\n    bl .\n    cmp r0, #0\n    bne L_open_cfw_runtime_am051_b202c_0024\n    ldr r0, [pc, #0x294]\n    str r0, [sp]\n    ldr r3, [pc, #0x294]\n    movs r2, #0xf2\n    ldr r1, [pc, #0x224]\n    movs r0, #3\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am051_addr_0044d25c\n    bl .\n    movs r0, #0\n    b L_open_cfw_runtime_am051_b202c_007c\nL_open_cfw_runtime_am051_b202c_0024:\n    ldr r1, [r4, #0x34]\n    str r0, [r1, #0x18]\n    movs r0, #0\n    ldrb.w r0, [r4, #0x2d]\n    cmp r0, #0\n    bne L_open_cfw_runtime_am051_b202c_0052\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am051_addr_005297b8\n    bl .\nL_open_cfw_runtime_am051_b202c_0038:\n    cmp r0, #0\n    bne L_open_cfw_runtime_am051_b202c_0076\n    ldr r0, [pc, #0x270]\n    str r0, [sp]\n    ldr r3, [pc, #0x268]\n    mov.w r2, #0x104\n    ldr r1, [pc, #0x1f8]\n    movs r0, #3\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am051_addr_0044d25c\n    bl .\n    movs r0, #0\n    b L_open_cfw_runtime_am051_b202c_007c\nL_open_cfw_runtime_am051_b202c_0052:\n    ldrb.w r0, [r4, #0x2d]\n    cmp r0, #1\n    bne L_open_cfw_runtime_am051_b202c_0062\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am051_addr_00529b38\n    bl .\n    b L_open_cfw_runtime_am051_b202c_0038\nL_open_cfw_runtime_am051_b202c_0062:\n    ldr r0, [pc, #0x250]\n    str r0, [sp]\n    ldr r3, [pc, #0x244]\n    movs r2, #0xff\n    ldr r1, [pc, #0x1d4]\n    movs r0, #3\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am051_addr_0044d25c\n    bl .\n    movs r0, #0\n    b L_open_cfw_runtime_am051_b202c_007c\nL_open_cfw_runtime_am051_b202c_0076:\n    ldr r1, [r4, #0x34]\n    str r0, [r1, #0x1c]\n    movs r0, #1\nL_open_cfw_runtime_am051_b202c_007c:\n    pop {r1, r4, r5, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM051_B20AA_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am051_b20aa(void)
{
    __asm__ volatile(
        "    push {r4, lr}\n    movs r4, r0\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am051_addr_00529406\n    bl .\n    ldrb.w r0, [r4, #0x2d]\n    cmp r0, #0\n    bne L_open_cfw_runtime_am051_b20aa_001a\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am051_addr_005297f8\n    bl .\n    b L_open_cfw_runtime_am051_b20aa_0028\nL_open_cfw_runtime_am051_b20aa_001a:\n    ldrb.w r0, [r4, #0x2d]\n    cmp r0, #1\n    bne L_open_cfw_runtime_am051_b20aa_0028\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am051_addr_00529b7e\n    bl .\nL_open_cfw_runtime_am051_b20aa_0028:\n    pop {r4, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM051_B20D4_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am051_b20d4(void)
{
    __asm__ volatile(
        "    push {r0, r1, r2, r3, r4, r5, r6, lr}\n    movs r4, r0\n    movs r5, r1\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am051_addr_00454768\n    bl .\n    cmp r0, #0\n    bne L_open_cfw_runtime_am051_b20d4_0030\n    ldr r0, [pc, #0x1fc]\n    str r0, [sp, #4]\n    ldr r0, [pc, #0x1b4]\n    str r0, [sp]\n    ldr r3, [pc, #0x1f8]\n    movw r2, #0x129\n    ldr r1, [pc, #0x178]\n    movs r0, #3\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am051_addr_0044d25c\n    bl .\nL_open_cfw_runtime_am051_b20d4_0026:\n    movs r0, #0\n    movs.w r1, #-1\n    str r0, [r1]\n    b L_open_cfw_runtime_am051_b20d4_0026\nL_open_cfw_runtime_am051_b20d4_0030:\n    adds r6, r4, #4\n    movs r0, r6\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am051_addr_00482cd8\n    bl .\n    movs r4, r0\n    b L_open_cfw_runtime_am051_b20d4_0046\nL_open_cfw_runtime_am051_b20d4_003c:\n    movs r1, r4\n    movs r0, r6\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am051_addr_00482cf0\n    bl .\n    movs r4, r0\nL_open_cfw_runtime_am051_b20d4_0046:\n    cmp r4, #0\n    beq L_open_cfw_runtime_am051_b20d4_0060\n    movs r1, r5\n    ldr r0, [r4]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am051_addr_0046cacc\n    bl .\n    cmp r0, #0\n    bne L_open_cfw_runtime_am051_b20d4_003c\n    ldr r0, [r4, #4]\n    adds r0, r0, #1\n    str r0, [r4, #4]\n    ldr r0, [r4]\n    b L_open_cfw_runtime_am051_b20d4_00c8\nL_open_cfw_runtime_am051_b20d4_0060:\n    movs r0, r6\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am051_addr_00482bca\n    bl .\n    movs r4, r0\n    cmp r4, #0\n    bne L_open_cfw_runtime_am051_b20d4_0090\n    ldr r0, [pc, #0x12c]\n    str r0, [sp, #8]\n    ldr r0, [pc, #0x1a4]\n    str r0, [sp, #4]\n    ldr r0, [pc, #0x12c]\n    str r0, [sp]\n    ldr r3, [pc, #0x198]\n    movw r2, #0x139\n    ldr r1, [pc, #0x118]\n    movs r0, #3\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am051_addr_0044d25c\n    bl .\nL_open_cfw_runtime_am051_b20d4_0086:\n    movs r0, #0\n    movs.w r1, #-1\n    str r0, [r1]\n    b L_open_cfw_runtime_am051_b20d4_0086\nL_open_cfw_runtime_am051_b20d4_0090:\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am051_addr_004547c6\n    bl .\n    str r0, [r4]\n    ldr r0, [r4]\n    cmp r0, #0\n    bne L_open_cfw_runtime_am051_b20d4_00c2\n    ldr r0, [pc, #0x11c]\n    str r0, [sp, #8]\n    ldr r0, [pc, #0x178]\n    str r0, [sp, #4]\n    ldr r0, [pc, #0xfc]\n    str r0, [sp]\n    ldr r3, [pc, #0x168]\n    mov.w r2, #0x148\n    ldr r1, [pc, #0xe4]\n    movs r0, #3\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am051_addr_0044d25c\n    bl .\nL_open_cfw_runtime_am051_b20d4_00b8:\n    movs r0, #0\n    movs.w r1, #-1\n    str r0, [r1]\n    b L_open_cfw_runtime_am051_b20d4_00b8\nL_open_cfw_runtime_am051_b20d4_00c2:\n    movs r0, #1\n    str r0, [r4, #4]\n    ldr r0, [r4]\nL_open_cfw_runtime_am051_b20d4_00c8:\n    add sp, #0x10\n    pop {r4, r5, r6, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM051_B21A0_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am051_b21a0(void)
{
    __asm__ volatile(
        "    push {r0, r1, r2, r3, r4, r5, r6, lr}\n    movs r5, r1\n    adds r6, r0, #4\n    movs r0, r6\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am051_addr_00482cd8\n    bl .\n    movs r4, r0\n    b L_open_cfw_runtime_am051_b21a0_001a\nL_open_cfw_runtime_am051_b21a0_0010:\n    movs r1, r4\n    movs r0, r6\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am051_addr_00482cf0\n    bl .\n    movs r4, r0\nL_open_cfw_runtime_am051_b21a0_001a:\n    cmp r4, #0\n    beq L_open_cfw_runtime_am051_b21a0_0046\n    ldr r0, [r4]\n    cmp r5, r0\n    bne L_open_cfw_runtime_am051_b21a0_0010\n    ldr r0, [r4, #4]\n    subs r0, r0, #1\n    str r0, [r4, #4]\n    ldr r0, [r4, #4]\n    cmp r0, #0\n    bne L_open_cfw_runtime_am051_b21a0_0044\n    movs r1, r4\n    movs r0, r6\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am051_addr_00482c0e\n    bl .\n    ldr r0, [r4]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am051_addr_0044f758\n    bl .\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am051_addr_0044f758\n    bl .\nL_open_cfw_runtime_am051_b21a0_0044:\n    pop {r0, r1, r2, r3, r4, r5, r6, pc}\nL_open_cfw_runtime_am051_b21a0_0046:\n    ldr r0, [pc, #0x10c]\n    str r0, [sp, #8]\n    ldr r0, [pc, #0x10c]\n    str r0, [sp, #4]\n    ldr r0, [pc, #0x88]\n    str r0, [sp]\n    ldr r3, [pc, #0x108]\n    movw r2, #0x163\n    ldr r1, [pc, #0x70]\n    movs r0, #3\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am051_addr_0044d25c\n    bl .\nL_open_cfw_runtime_am051_b21a0_0060:\n    movs r0, #0\n    movs.w r1, #-1\n    str r0, [r1]\n    b L_open_cfw_runtime_am051_b21a0_0060\n"
    );
}
#endif

#if defined(OPEN_CFW_AM051_B26A4_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am051_b26a4(void)
{
    __asm__ volatile(
        "    push.w {r4, r5, r6, r7, r8, sb, sl, lr}\n    mov r8, r0\n    movs r5, r1\n    mov sb, r3\n    cmp r2, #9\n    bne L_open_cfw_runtime_am051_b26a4_0012\n    movs r6, #1\n    b L_open_cfw_runtime_am051_b26a4_0014\nL_open_cfw_runtime_am051_b26a4_0012:\n    movs r6, #0\nL_open_cfw_runtime_am051_b26a4_0014:\n    movs r0, r6\n    uxtb r0, r0\n    cmp r0, #0\n    beq L_open_cfw_runtime_am051_b26a4_001e\n    movs r2, #0x20\nL_open_cfw_runtime_am051_b26a4_001e:\n    ldr.w r7, [r8, #0x18]\n    movs r1, r2\n    mov r0, r8\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am051_b2774\n    bl .\n    movs r4, r0\n    cmp r4, #0\n    bne L_open_cfw_runtime_am051_b26a4_0034\n    movs r0, #0\n    b L_open_cfw_runtime_am051_b26a4_00cc\nL_open_cfw_runtime_am051_b26a4_0034:\n    movs.w sl, #0\n    ldr r0, [r7, #0xc]\n    cmp r0, #0\n    beq L_open_cfw_runtime_am051_b26a4_0056\n    mov r1, sb\n    mov r0, r8\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am051_b2774\n    bl .\n    cmp r0, #0\n    beq L_open_cfw_runtime_am051_b26a4_0056\n    movs r2, r0\n    movs r1, r4\n    mov r0, r8\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am051_b28ee\n    bl .\n    mov sl, r0\nL_open_cfw_runtime_am051_b26a4_0056:\n    ldr r0, [r7, #4]\n    lsls r1, r4, #4\n    add r1, r0\n    sxtb.w sl, sl\n    ldrh r0, [r7, #0x10]\n    mul sl, r0, sl\n    asrs.w sl, sl, #4\n    ldr r0, [r1, #4]\n    movs r2, r6\n    uxtb r2, r2\n    cmp r2, #0\n    beq L_open_cfw_runtime_am051_b26a4_0076\n    lsls r0, r0, #1\nL_open_cfw_runtime_am051_b26a4_0076:\n    adds.w sl, sl, r0\n    adds.w sl, sl, #8\n    lsrs.w sl, sl, #4\n    strh.w sl, [r5, #4]\n    ldrh r0, [r1, #0xa]\n    strh r0, [r5, #8]\n    ldrh r0, [r1, #8]\n    strh r0, [r5, #6]\n    ldrh r0, [r1, #0xc]\n    strh r0, [r5, #0xa]\n    ldrh r0, [r1, #0xe]\n    strh r0, [r5, #0xc]\n    ldrh r0, [r7, #0x12]\n    uxth r0, r0\n    lsrs r0, r0, #9\n    ands r0, r0, #0xf\n    strb r0, [r5, #0xe]\n    ldrh r0, [r7, #0x12]\n    uxth r0, r0\n    lsrs r0, r0, #0xe\n    uxth r0, r0\n    cmp r0, #3\n    bne L_open_cfw_runtime_am051_b26a4_00b4\n    ldrb r0, [r5, #0xe]\n    adds r0, #0x10\n    strb r0, [r5, #0xe]\nL_open_cfw_runtime_am051_b26a4_00b4:\n    ldrb r0, [r5, #0xf]\n    ands r0, r0, #0xfe\n    strb r0, [r5, #0xf]\n    str r4, [r5, #0x18]\n    uxtb r6, r6\n    cmp r6, #0\n    beq L_open_cfw_runtime_am051_b26a4_00ca\n    ldrh r0, [r5, #6]\n    lsls r0, r0, #1\n    strh r0, [r5, #6]\nL_open_cfw_runtime_am051_b26a4_00ca:\n    movs r0, #1\nL_open_cfw_runtime_am051_b26a4_00cc:\n    pop.w {r4, r5, r6, r7, r8, sb, sl, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM051_B2774_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am051_b2774(void)
{
    __asm__ volatile(
        "    push {r1, r2, r3, r4, r5, r6, r7, lr}\n    cmp r1, #0\n    bne L_open_cfw_runtime_am051_b2774_000a\n    movs r0, #0\n    b L_open_cfw_runtime_am051_b2774_0178\nL_open_cfw_runtime_am051_b2774_000a:\n    ldr r4, [r0, #0x18]\n    movs r5, #0\n    b L_open_cfw_runtime_am051_b2774_0044\nL_open_cfw_runtime_am051_b2774_0010:\n    b L_open_cfw_runtime_am051_b2774_0042\nL_open_cfw_runtime_am051_b2774_0012:\n    ldr r0, [r4, #8]\n    movs r3, r5\n    uxth r3, r3\n    muls r3, r6, r3\n    add r0, r3\n    ldrb r0, [r0, #0x12]\n    cmp r0, #0\n    bne L_open_cfw_runtime_am051_b2774_00a6\n    ldr r0, [r4, #8]\n    movs r3, r5\n    uxth r3, r3\n    muls r3, r6, r3\n    add r0, r3\n    ldr r3, [r0, #0xc]\n    ldrb r0, [r3, r2]\n    cmp r0, #0\n    bne L_open_cfw_runtime_am051_b2774_0094\n    ldr r0, [r4, #8]\n    movs r7, r5\n    uxth r7, r7\n    muls r7, r6, r7\n    ldr r0, [r0, r7]\n    cmp r1, r0\n    beq L_open_cfw_runtime_am051_b2774_0094\nL_open_cfw_runtime_am051_b2774_0042:\n    adds r5, r5, #1\nL_open_cfw_runtime_am051_b2774_0044:\n    movs r0, r5\n    ldrh r2, [r4, #0x12]\n    lsls r2, r2, #0x17\n    lsrs r2, r2, #0x17\n    uxth r0, r0\n    cmp r0, r2\n    bhs.w #0x4b28ea\n    movs r6, #0x14\n    ldr r0, [r4, #8]\n    movs r2, r5\n    uxth r2, r2\n    muls r2, r6, r2\n    ldr r2, [r0, r2]\n    subs r2, r1, r2\n    ldr r0, [r4, #8]\n    movs r3, r5\n    uxth r3, r3\n    muls r3, r6, r3\n    add r0, r3\n    ldrh r0, [r0, #4]\n    cmp r2, r0\n    bhs L_open_cfw_runtime_am051_b2774_0010\n    movs r7, #0\n    ldr r0, [r4, #8]\n    movs r3, r5\n    uxth r3, r3\n    muls r3, r6, r3\n    add r0, r3\n    ldrb r0, [r0, #0x12]\n    cmp r0, #2\n    bne L_open_cfw_runtime_am051_b2774_0012\n    ldr r0, [r4, #8]\n    uxth r5, r5\n    muls r5, r6, r5\n    add r0, r5\n    ldrh r0, [r0, #6]\n    uxtah r7, r2, r0\n    b L_open_cfw_runtime_am051_b2774_0172\nL_open_cfw_runtime_am051_b2774_0094:\n    ldr r0, [r4, #8]\n    uxth r5, r5\n    muls r5, r6, r5\n    add r0, r5\n    ldrh r0, [r0, #6]\n    ldrb r1, [r3, r2]\n    uxtah r7, r1, r0\n    b L_open_cfw_runtime_am051_b2774_0172\nL_open_cfw_runtime_am051_b2774_00a6:\n    ldr r0, [r4, #8]\n    movs r1, r5\n    uxth r1, r1\n    muls r1, r6, r1\n    add r0, r1\n    ldrb r0, [r0, #0x12]\n    cmp r0, #3\n    bne L_open_cfw_runtime_am051_b2774_0106\n    strh.w r2, [sp, #6]\n    addw r0, pc, #0x1a1\n    str r0, [sp]\n    movs r3, #2\n    ldr r0, [r4, #8]\n    movs r1, r5\n    uxth r1, r1\n    muls r1, r6, r1\n    add r0, r1\n    ldrh r2, [r0, #0x10]\n    ldr r0, [r4, #8]\n    movs r1, r5\n    uxth r1, r1\n    muls r1, r6, r1\n    add r0, r1\n    ldr r1, [r0, #8]\n    add.w r0, sp, #6\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am051_addr_0052a284\n    bl .\n    cmp r0, #0\n    beq L_open_cfw_runtime_am051_b2774_0172\n    ldr r1, [r4, #8]\n    movs r2, r5\n    uxth r2, r2\n    muls r2, r6, r2\n    add r1, r2\n    ldr r1, [r1, #8]\n    subs r0, r0, r1\n    asrs r0, r0, #1\n    ldr r1, [r4, #8]\n    uxth r5, r5\n    muls r5, r6, r5\n    add r1, r5\n    ldrh r1, [r1, #6]\n    uxtah r7, r0, r1\n    b L_open_cfw_runtime_am051_b2774_0172\nL_open_cfw_runtime_am051_b2774_0106:\n    ldr r0, [r4, #8]\n    movs r1, r5\n    uxth r1, r1\n    muls r1, r6, r1\n    add r0, r1\n    ldrb r0, [r0, #0x12]\n    cmp r0, #1\n    bne L_open_cfw_runtime_am051_b2774_0172\n    strh.w r2, [sp, #4]\n    addw r0, pc, #0x141\n    str r0, [sp]\n    movs r3, #2\n    ldr r0, [r4, #8]\n    movs r1, r5\n    uxth r1, r1\n    muls r1, r6, r1\n    add r0, r1\n    ldrh r2, [r0, #0x10]\n    ldr r0, [r4, #8]\n    movs r1, r5\n    uxth r1, r1\n    muls r1, r6, r1\n    add r0, r1\n    ldr r1, [r0, #8]\n    add r0, sp, #4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am051_addr_0052a284\n    bl .\n    cmp r0, #0\n    beq L_open_cfw_runtime_am051_b2774_0172\n    ldr r1, [r4, #8]\n    movs r2, r5\n    uxth r2, r2\n    muls r2, r6, r2\n    add r1, r2\n    ldr r1, [r1, #8]\n    subs r0, r0, r1\n    asrs r0, r0, #1\n    ldr r1, [r4, #8]\n    movs r2, r5\n    uxth r2, r2\n    muls r2, r6, r2\n    add r1, r2\n    ldr r1, [r1, #0xc]\n    ldr r2, [r4, #8]\n    uxth r5, r5\n    muls r5, r6, r5\n    add r2, r5\n    ldrh r2, [r2, #6]\n    ldrh.w r0, [r1, r0, lsl #1]\n    uxtah r7, r0, r2\nL_open_cfw_runtime_am051_b2774_0172:\n    movs r0, r7\n    b L_open_cfw_runtime_am051_b2774_0178\n    movs r0, #0\nL_open_cfw_runtime_am051_b2774_0178:\n    pop {r1, r2, r3, r4, r5, r6, r7, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM051_B28EE_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am051_b28ee(void)
{
    __asm__ volatile(
        "    push {r3, r4, r5, r6, lr}\n    sub sp, #0x14\n    ldr r0, [r0, #0x18]\n    movs r4, #0\n    ldrh r3, [r0, #0x12]\n    ubfx r3, r3, #0xd, #1\n    uxth r3, r3\n    cmp r3, #0\n    bne L_open_cfw_runtime_am051_b28ee_007a\n    ldr r5, [r0, #0xc]\n    ldr r0, [r5, #8]\n    lsrs r0, r0, #0x1e\n    cmp r0, #0\n    bne L_open_cfw_runtime_am051_b28ee_0048\n    ldr r6, [r5]\n    str r1, [sp, #0xc]\n    str r2, [sp, #0x10]\n    addw r0, pc, #0x8d\n    str r0, [sp]\n    movs r3, #2\n    ldr r2, [r5, #8]\n    bic r2, r2, #0xc0000000\n    movs r1, r6\n    add r0, sp, #0xc\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am051_addr_0052a284\n    bl .\n    cmp r0, #0\n    beq L_open_cfw_runtime_am051_b28ee_00aa\n    subs r6, r0, r6\n    asrs r6, r6, #1\n    ldr r0, [r5, #4]\n    ldrsb r4, [r0, r6]\n    b L_open_cfw_runtime_am051_b28ee_00aa\nL_open_cfw_runtime_am051_b28ee_0048:\n    ldr r0, [r5, #8]\n    lsrs r0, r0, #0x1e\n    cmp r0, #1\n    bne L_open_cfw_runtime_am051_b28ee_00aa\n    ldr r6, [r5]\n    str r1, [sp, #4]\n    str r2, [sp, #8]\n    addw r0, pc, #0x71\n    str r0, [sp]\n    movs r3, #4\n    ldr r2, [r5, #8]\n    bic r2, r2, #0xc0000000\n    movs r1, r6\n    add r0, sp, #4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am051_addr_0052a284\n    bl .\n    cmp r0, #0\n    beq L_open_cfw_runtime_am051_b28ee_00aa\n    subs r6, r0, r6\n    asrs r6, r6, #2\n    ldr r0, [r5, #4]\n    ldrsb r4, [r0, r6]\n    b L_open_cfw_runtime_am051_b28ee_00aa\nL_open_cfw_runtime_am051_b28ee_007a:\n    ldr r0, [r0, #0xc]\n    ldr r3, [r0, #4]\n    ldrb r1, [r3, r1]\n    ldr r3, [r0, #8]\n    ldrb r2, [r3, r2]\n    movs r3, r1\n    uxtb r3, r3\n    cmp r3, #0\n    beq L_open_cfw_runtime_am051_b28ee_00aa\n    movs r3, r2\n    uxtb r3, r3\n    cmp r3, #0\n    beq L_open_cfw_runtime_am051_b28ee_00aa\n    ldr r3, [r0]\n    uxtb r1, r1\n    subs r1, r1, #1\n    ldrb r0, [r0, #0xd]\n    uxtb r2, r2\n    mla r1, r0, r1, r2\n    add.w r0, r3, r1\n    ldrsb r4, [r0, #-0x1]\nL_open_cfw_runtime_am051_b28ee_00aa:\n    movs r0, r4\n    sxtb r0, r0\n    add sp, #0x18\n    pop {r4, r5, r6, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM051_B29F8_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am051_b29f8(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    movs r0, #0\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am051_addr_0052a3da\n    bl .\n    pop {r0, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM051_B32D4_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am051_b32d4(void)
{
    __asm__ volatile(
        "    ldr.w r0, [pc, #0x9b4]\n    movs r1, #0\n    str r1, [r0, #0x78]\n    movs r1, #0\n    str r1, [r0, #0x7c]\n    bx lr\n"
    );
}
#endif

#if defined(OPEN_CFW_AM051_B32E2_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am051_b32e2(void)
{
    __asm__ volatile(
        "    push {r4, r5}\n    movs r2, r0\n    movs r3, #0\n    b L_open_cfw_runtime_am051_b32e2_000a\nL_open_cfw_runtime_am051_b32e2_0008:\n    adds r3, r3, #1\nL_open_cfw_runtime_am051_b32e2_000a:\n    movs r0, r3\n    movs r4, r2\n    uxtb r0, r0\n    uxtb r4, r4\n    cmp r0, r4\n    bhs L_open_cfw_runtime_am051_b32e2_0064\n    movs r4, #0\n    b L_open_cfw_runtime_am051_b32e2_001c\nL_open_cfw_runtime_am051_b32e2_001a:\n    adds r4, r4, #1\nL_open_cfw_runtime_am051_b32e2_001c:\n    movs r0, r4\n    uxtb r0, r0\n    cmp r0, #2\n    bge L_open_cfw_runtime_am051_b32e2_0008\n    movs r0, r3\n    uxtb r0, r0\n    ldrb r0, [r1, r0]\n    movs r5, r4\n    uxtb r5, r5\n    cmp r0, r5\n    bne L_open_cfw_runtime_am051_b32e2_001a\n    ldr.w r5, [pc, #0x974]\n    movs r0, r4\n    uxtb r0, r0\n    add r0, r5\n    ldrb.w r0, [r0, #0x59]\n    cmp r0, #0\n    beq L_open_cfw_runtime_am051_b32e2_0060\n    movs r0, r4\n    uxtb r0, r0\n    add r0, r5\n    ldrb.w r0, [r0, #0x59]\n    cmp r0, #4\n    beq L_open_cfw_runtime_am051_b32e2_0060\n    movs r0, r4\n    uxtb r0, r0\n    add r0, r5\n    ldrb.w r0, [r0, #0x59]\n    cmp r0, #5\n    bne L_open_cfw_runtime_am051_b32e2_001a\nL_open_cfw_runtime_am051_b32e2_0060:\n    movs r0, #1\n    b L_open_cfw_runtime_am051_b32e2_0066\nL_open_cfw_runtime_am051_b32e2_0064:\n    movs r0, #0\nL_open_cfw_runtime_am051_b32e2_0066:\n    pop {r4, r5}\n    bx lr\n"
    );
}
#endif

#if defined(OPEN_CFW_AM051_B334C_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am051_b334c(void)
{
    __asm__ volatile(
        "    push {r4, r5, r6}\n    movs r4, #0\n    ldr.w r2, [pc, #0x938]\n    ldrb.w r5, [r2, #0x5d]\n    lsls r5, r5, #1\n    ldrb.w r3, [r2, #0x5d]\n    lsls r3, r3, #1\n    adds r3, r3, #1\n    movs r1, r0\n    uxtb r1, r1\n    add.w r1, r2, r1, lsl #3\n    movs r6, r5\n    uxtb r6, r6\n    add.w r1, r1, r6, lsl #1\n    ldrh.w r1, [r1, #0x40]\n    cmp r1, #0\n    beq L_open_cfw_runtime_am051_b334c_0044\n    movs r1, r0\n    uxtb r1, r1\n    add.w r1, r2, r1, lsl #3\n    uxtb r5, r5\n    add.w r1, r1, r5, lsl #1\n    movs r4, #0\n    strh.w r4, [r1, #0x40]\n    movs r4, #1\nL_open_cfw_runtime_am051_b334c_0044:\n    movs r1, r0\n    uxtb r1, r1\n    add.w r1, r2, r1, lsl #3\n    movs r5, r3\n    uxtb r5, r5\n    add.w r1, r1, r5, lsl #1\n    ldrh.w r1, [r1, #0x40]\n    cmp r1, #0\n    beq L_open_cfw_runtime_am051_b334c_0072\n    movs r1, r0\n    uxtb r1, r1\n    add.w r1, r2, r1, lsl #3\n    uxtb r3, r3\n    add.w r1, r1, r3, lsl #1\n    movs r3, #0\n    strh.w r3, [r1, #0x40]\n    movs r4, #1\nL_open_cfw_runtime_am051_b334c_0072:\n    uxtb r4, r4\n    cmp r4, #0\n    beq L_open_cfw_runtime_am051_b334c_0082\n    movs r1, #0\n    uxtb r0, r0\n    add r0, r2\n    strb.w r1, [r0, #0x55]\nL_open_cfw_runtime_am051_b334c_0082:\n    pop {r4, r5, r6}\n    bx lr\n"
    );
}
#endif

#if defined(OPEN_CFW_AM051_B33D2_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am051_b33d2(void)
{
    __asm__ volatile(
        "    push {r4}\n    lsls r2, r1, #1\n    uxtb r1, r1\n    lsls r1, r1, #1\n    adds r1, r1, #1\n    ldr.w r3, [pc, #0x8ac]\n    movs r4, r0\n    uxtb r4, r4\n    add.w r4, r3, r4, lsl #3\n    uxtb r2, r2\n    add.w r2, r4, r2, lsl #1\n    movs r4, #0\n    strh.w r4, [r2, #0x40]\n    movs r2, r0\n    uxtb r2, r2\n    add.w r2, r3, r2, lsl #3\n    uxtb r1, r1\n    add.w r1, r2, r1, lsl #1\n    movs r2, #0\n    strh.w r2, [r1, #0x40]\n    movs r1, #0\n    uxtb r0, r0\n    add r0, r3\n    strb.w r1, [r0, #0x55]\n    pop {r4}\n    bx lr\n"
    );
}
#endif

#if defined(OPEN_CFW_AM051_B3416_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am051_b3416(void)
{
    __asm__ volatile(
        "    push.w {r3, r4, r5, r6, r7, r8, sb, lr}\n    movs r4, r0\n    movs r5, r1\n    movs r1, #1\n    ldr.w r6, [pc, #0x868]\n    movs r0, r4\n    uxtb r0, r0\n    lsls r0, r0, #4\n    add r0, r6\n    movs r2, r5\n    uxtb r2, r2\n    ldr.w r7, [r0, r2, lsl #2]\n    movs r0, r4\n    uxtb r0, r0\n    add.w r0, r6, r0, lsl #3\n    movs r2, r5\n    uxtb r2, r2\n    add.w r0, r0, r2, lsl #1\n    ldrh.w r8, [r0, #0x20]\n    movs r0, r4\n    uxtb r0, r0\n    add.w r0, r6, r0, lsl #3\n    movs r2, r5\n    uxtb r2, r2\n    add.w r0, r0, r2, lsl #1\n    ldrh.w r0, [r0, #0x40]\n    subs.w r8, r8, r0\n    movs r0, r4\n    uxtb r0, r0\n    add.w r0, r6, r0, lsl #1\n    ldrh.w r0, [r0, #0x50]\n    mov r2, r8\n    uxth r2, r2\n    cmp r0, r2\n    bhs L_open_cfw_runtime_am051_b3416_00d8\n    movs r0, r4\n    uxtb r0, r0\n    add.w r0, r6, r0, lsl #1\n    ldrh.w r8, [r0, #0x50]\n    b L_open_cfw_runtime_am051_b3416_00d8\nL_open_cfw_runtime_am051_b3416_006c:\n    movs r1, #2\n    b L_open_cfw_runtime_am051_b3416_007a\nL_open_cfw_runtime_am051_b3416_0070:\n    mov sb, r8\n    uxtb r1, r1\n    cmp r1, #0\n    beq L_open_cfw_runtime_am051_b3416_006c\n    movs r1, #3\nL_open_cfw_runtime_am051_b3416_007a:\n    movs r0, r4\n    uxtb r0, r0\n    add.w r0, r6, r0, lsl #3\n    movs r2, r5\n    uxtb r2, r2\n    add.w r0, r0, r2, lsl #1\n    ldrh.w r0, [r0, #0x40]\n    add r0, r7\n    str r0, [sp]\n    mov r3, sb\n    uxtb r3, r3\n    ands r2, r5, #1\n    uxtb r1, r1\n    movs r0, r4\n    uxtb r0, r0\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am051_addr_004b319e\n    bl .\n    movs r0, r4\n    uxtb r0, r0\n    add.w r0, r6, r0, lsl #3\n    movs r1, r5\n    uxtb r1, r1\n    add.w r0, r0, r1, lsl #1\n    movs r1, r4\n    uxtb r1, r1\n    add.w r1, r6, r1, lsl #3\n    movs r2, r5\n    uxtb r2, r2\n    add.w r1, r1, r2, lsl #1\n    ldrh.w r1, [r1, #0x40]\n    adds.w r1, sb, r1\n    strh.w r1, [r0, #0x40]\n    subs.w sb, r8, sb\n    mov r8, sb\n    movs r1, #0\nL_open_cfw_runtime_am051_b3416_00d8:\n    mov r0, r8\n    uxth r0, r0\n    cmp r0, #0\n    beq L_open_cfw_runtime_am051_b3416_00fa\n    mov r0, r8\n    uxth r0, r0\n    cmp r0, #0xfc\n    blt L_open_cfw_runtime_am051_b3416_0070\n    movs.w sb, #0xfb\n    uxtb r1, r1\n    cmp r1, #0\n    beq L_open_cfw_runtime_am051_b3416_00f6\n    movs r1, #1\n    b L_open_cfw_runtime_am051_b3416_007a\nL_open_cfw_runtime_am051_b3416_00f6:\n    movs r1, #0\n    b L_open_cfw_runtime_am051_b3416_007a\nL_open_cfw_runtime_am051_b3416_00fa:\n    pop.w {r0, r4, r5, r6, r7, r8, sb, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM051_B3514_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am051_b3514(void)
{
    __asm__ volatile(
        "    push {r3, r4, r5, r6, r7, lr}\n    movs r4, r0\n    movs r7, r1\n    lsls r5, r7, #1\n    uxtb r7, r7\n    lsls r7, r7, #1\n    adds r7, r7, #1\n    ldr.w r6, [pc, #0x768]\n    movs r0, r4\n    uxtb r0, r0\n    add.w r0, r6, r0, lsl #3\n    movs r1, r5\n    uxtb r1, r1\n    add.w r0, r0, r1, lsl #1\n    ldrh.w r0, [r0, #0x40]\n    movs r1, r4\n    uxtb r1, r1\n    add.w r1, r6, r1, lsl #3\n    movs r2, r5\n    uxtb r2, r2\n    add.w r1, r1, r2, lsl #1\n    ldrh r1, [r1, #0x20]\n    cmp r0, r1\n    bhs L_open_cfw_runtime_am051_b3514_0048\n    movs r1, r5\n    uxtb r1, r1\n    movs r0, r4\n    uxtb r0, r0\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am051_b3416\n    bl .\nL_open_cfw_runtime_am051_b3514_0048:\n    movs r0, r4\n    uxtb r0, r0\n    add.w r0, r6, r0, lsl #3\n    movs r1, r7\n    uxtb r1, r1\n    add.w r0, r0, r1, lsl #1\n    ldrh.w r0, [r0, #0x40]\n    movs r1, r4\n    uxtb r1, r1\n    add.w r1, r6, r1, lsl #3\n    movs r2, r7\n    uxtb r2, r2\n    add.w r1, r1, r2, lsl #1\n    ldrh r1, [r1, #0x20]\n    cmp r0, r1\n    bhs L_open_cfw_runtime_am051_b3514_007e\n    movs r1, r7\n    uxtb r1, r1\n    movs r0, r4\n    uxtb r0, r0\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am051_b3416\n    bl .\nL_open_cfw_runtime_am051_b3514_007e:\n    movs r0, r4\n    uxtb r0, r0\n    add.w r0, r6, r0, lsl #3\n    movs r1, r5\n    uxtb r1, r1\n    add.w r0, r0, r1, lsl #1\n    ldrh.w r0, [r0, #0x40]\n    movs r1, r4\n    uxtb r1, r1\n    add.w r1, r6, r1, lsl #3\n    uxtb r5, r5\n    add.w r1, r1, r5, lsl #1\n    ldrh r1, [r1, #0x20]\n    cmp r0, r1\n    blo L_open_cfw_runtime_am051_b3514_00da\n    movs r0, r4\n    uxtb r0, r0\n    add.w r0, r6, r0, lsl #3\n    movs r1, r7\n    uxtb r1, r1\n    add.w r0, r0, r1, lsl #1\n    ldrh.w r0, [r0, #0x40]\n    movs r1, r4\n    uxtb r1, r1\n    add.w r1, r6, r1, lsl #3\n    uxtb r7, r7\n    add.w r1, r1, r7, lsl #1\n    ldrh r1, [r1, #0x20]\n    cmp r0, r1\n    blo L_open_cfw_runtime_am051_b3514_00da\n    movs r0, #1\n    uxtb r4, r4\n    add.w r1, r6, r4\n    strb.w r0, [r1, #0x55]\nL_open_cfw_runtime_am051_b3514_00da:\n    pop {r0, r4, r5, r6, r7, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM051_B35F0_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am051_b35f0(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    ldr.w r1, [pc, #0xc3c]\n    ldr r1, [r1]\n    ldr r1, [r1]\n    cmp r1, #0\n    beq L_open_cfw_runtime_am051_b35f0_0014\n    adds r0, #0x10\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am051_addr_0052a4d2\n    bl .\nL_open_cfw_runtime_am051_b35f0_0014:\n    pop {r0, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM051_B36B2_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am051_b36b2(void)
{
    __asm__ volatile(
        "    push {r2, r3, r4, lr}\n    movs r4, r0\n    movs r3, #0\n    ldr r0, [r4]\n    cmp r0, #0\n    beq L_open_cfw_runtime_am051_b36b2_0018\n    mov r2, sp\n    movs r1, #1\n    ldr r0, [r4]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am051_addr_0047ae78\n    bl .\n    movs r3, r0\nL_open_cfw_runtime_am051_b36b2_0018:\n    cmp r3, #0\n    beq L_open_cfw_runtime_am051_b36b2_0038\n    ldrb r0, [r4, #5]\n    cmp r0, #0\n    bne L_open_cfw_runtime_am051_b36b2_0026\n    movs r0, #1\n    b L_open_cfw_runtime_am051_b36b2_0028\nL_open_cfw_runtime_am051_b36b2_0026:\n    movs r0, #0\nL_open_cfw_runtime_am051_b36b2_0028:\n    strb r0, [r4, #6]\n    ldrb.w r2, [sp]\n    movs r1, #1\n    ldrb r0, [r4, #4]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am051_addr_0052bb20\n    bl .\n    b L_open_cfw_runtime_am051_b36b2_0048\nL_open_cfw_runtime_am051_b36b2_0038:\n    movs r0, #0\n    strb r0, [r4, #6]\n    movs r3, #0\n    movs r2, #0\n    movs r1, #0\n    ldrb r0, [r4, #4]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am051_addr_0052bb20\n    bl .\nL_open_cfw_runtime_am051_b36b2_0048:\n    pop {r0, r1, r4, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM051_B36FC_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am051_b36fc(void)
{
    __asm__ volatile(
        "    push {r4, lr}\n    movs r4, r0\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am051_b3746\n    bl .\n    ldr.w r1, [pc, #0x584]\n    ldr r0, [r1, #0x7c]\n    cmp r0, #0\n    beq L_open_cfw_runtime_am051_b36fc_001a\n    movs r0, r4\n    ldr r1, [r1, #0x7c]\n    blx r1\nL_open_cfw_runtime_am051_b36fc_001a:\n    ldrh r0, [r4]\n    uxtb r0, r0\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am051_addr_004bb25c\n    bl .\n    pop {r4, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM051_B3720_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am051_b3720(void)
{
    __asm__ volatile(
        "    push {r3, r4, r5, lr}\n    movs r4, r0\n    movs r5, r1\n    ldr r0, [r5]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am051_addr_004bb21c\n    bl .\n    movs r1, r5\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am051_b374c\n    bl .\n    ldr.w r1, [pc, #0x554]\n    ldr r0, [r1, #0x7c]\n    cmp r0, #0\n    beq L_open_cfw_runtime_am051_b3720_0024\n    movs r0, r4\n    ldr r1, [r1, #0x7c]\n    blx r1\nL_open_cfw_runtime_am051_b3720_0024:\n    pop {r0, r4, r5, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM051_B3746_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am051_b3746(void)
{
    __asm__ volatile(
        "    ldrh r0, [r0]\n    strb r0, [r1, #4]\n    bx lr\n"
    );
}
#endif

#if defined(OPEN_CFW_AM051_B374C_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am051_b374c(void)
{
    __asm__ volatile(
        "    push {r4, lr}\n    movs r4, r1\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am051_b35f0\n    bl .\n    movs r0, #0\n    strb r0, [r4, #4]\n    movs r0, #0\n    strb r0, [r4, #0xd]\n    ldr.w r1, [pc, #0x52c]\n    movs r0, #0\n    strb.w r0, [r1, #0x74]\n    ldrb r0, [r4, #9]\n    cmp r0, #0\n    beq L_open_cfw_runtime_am051_b374c_0044\n    movs r0, #0\n    strb r0, [r4, #9]\n    movs r0, #0\n    strb.w r0, [r1, #0x5d]\n    movs r4, #0\n    b L_open_cfw_runtime_am051_b374c_003c\nL_open_cfw_runtime_am051_b374c_0030:\n    movs r1, #0\n    movs r0, r4\n    uxtb r0, r0\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am051_b33d2\n    bl .\n    adds r4, r4, #1\nL_open_cfw_runtime_am051_b374c_003c:\n    movs r0, r4\n    uxtb r0, r0\n    cmp r0, #2\n    blt L_open_cfw_runtime_am051_b374c_0030\nL_open_cfw_runtime_am051_b374c_0044:\n    pop {r4, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM051_B38F2_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am051_b38f2(void)
{
    __asm__ volatile(
        "    push {r5, r6, r7, lr}\n    movs r2, r1\n    ldr.w r3, [pc, #0xc14]\n    ldr r1, [r3]\n    ldrb r1, [r1]\n    cmp r1, #0\n    bne L_open_cfw_runtime_am051_b38f2_0040\n    ldrh r1, [r0, #6]\n    strh.w r1, [sp]\n    ldrh r1, [r0, #8]\n    strh.w r1, [sp, #2]\n    ldrh r1, [r0, #0xa]\n    strh.w r1, [sp, #4]\n    ldrh r0, [r0, #0xc]\n    strh.w r0, [sp, #6]\n    movs r0, #0\n    strh.w r0, [sp, #0xa]\n    ldrh.w r0, [sp, #0xa]\n    strh.w r0, [sp, #8]\n    mov r1, sp\n    ldrb r0, [r2, #4]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am051_addr_004b6e14\n    bl .\n    b L_open_cfw_runtime_am051_b38f2_0050\nL_open_cfw_runtime_am051_b38f2_0040:\n    ldr r0, [r3]\n    ldrb r0, [r0]\n    cmp r0, #1\n    bne L_open_cfw_runtime_am051_b38f2_0050\n    movs r1, #0x11\n    ldrb r0, [r2, #4]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am051_addr_004b6e46\n    bl .\nL_open_cfw_runtime_am051_b38f2_0050:\n    pop {r0, r1, r2, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM051_B3944_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am051_b3944(void)
{
    __asm__ volatile(
        "    push {r1, r2, r3, r4, r5, lr}\n    movs r4, r0\n    movs r5, r1\n    movs r0, #0\n    strb r0, [r5, #6]\n    movs r0, #0\n    strb r0, [r5, #7]\n    adds.w r1, r4, #0xa\n    ldrb r0, [r4, #9]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am051_addr_0047ad74\n    bl .\n    str r0, [r5]\n    ldr r0, [r5]\n    cmp r0, #0\n    bne L_open_cfw_runtime_am051_b3944_003c\n    ldrb r0, [r4, #9]\n    cmp r0, #1\n    bne L_open_cfw_runtime_am051_b3944_003c\n    ldrb r0, [r4, #0xf]\n    ands r0, r0, #0xc0\n    cmp r0, #0x40\n    bne L_open_cfw_runtime_am051_b3944_003c\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am051_addr_00479418\n    bl .\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am051_addr_004b3606\n    bl .\n    b L_open_cfw_runtime_am051_b3944_0078\nL_open_cfw_runtime_am051_b3944_003c:\n    ldr r0, [r5]\n    cmp r0, #0\n    beq L_open_cfw_runtime_am051_b3944_0078\n    movs r0, #1\n    ldr.w r1, [pc, #0xa6c]\n    strb r0, [r1]\n    ldr r0, [r5]\n    cmp r0, #0\n    beq L_open_cfw_runtime_am051_b3944_0078\n    ldr r0, [r5]\n    adds r0, #0x6c\n    mov r8, r8\n    cmp r0, #0\n    beq L_open_cfw_runtime_am051_b3944_0062\n    movs r1, r0\n    ldrb r0, [r5, #4]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am051_addr_0052c244\n    bl .\nL_open_cfw_runtime_am051_b3944_0062:\n    add r2, sp, #4\n    mov r1, sp\n    ldr r0, [r5]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am051_addr_0047b40c\n    bl .\n    ldr r2, [sp, #4]\n    ldrb.w r1, [sp]\n    ldrb r0, [r5, #4]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am051_addr_0052d370\n    bl .\nL_open_cfw_runtime_am051_b3944_0078:\n    ldr.w r5, [pc, #0xb48]\n    ldr r0, [r5]\n    ldrb r0, [r0, #4]\n    cmp r0, #0\n    beq L_open_cfw_runtime_am051_b3944_0098\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am051_addr_0047a600\n    bl .\n    cmp r0, #0\n    beq L_open_cfw_runtime_am051_b3944_0098\n    ldr r0, [r5]\n    ldrb r1, [r0]\n    ldrh r0, [r4]\n    uxtb r0, r0\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am051_addr_0052bb00\n    bl .\nL_open_cfw_runtime_am051_b3944_0098:\n    pop {r0, r1, r2, r4, r5, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM051_B39DE_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am051_b39de(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    ldr r0, [r1]\n    cmp r0, #0\n    beq L_open_cfw_runtime_am051_b39de_000e\n    ldr r0, [r1]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am051_addr_0047a5c0\n    bl .\nL_open_cfw_runtime_am051_b39de_000e:\n    movs r0, #0\n    ldr.w r1, [pc, #0xa08]\n    strb r0, [r1]\n    pop {r0, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM051_B39F6_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am051_b39f6(void)
{
    __asm__ volatile(
        "    push.w {r2, r3, r4, r5, r6, r7, r8, lr}\n    movs r6, r0\n    movs r4, r1\n    movs r0, #1\n    ldr r1, [pc, #0x288]\n    strb.w r0, [r1, #0x54]\n    ldr.w r5, [pc, #0xb00]\n    ldrb r0, [r6, #4]\n    ands r0, r0, #1\n    ldr r1, [r5]\n    ldrb r1, [r1]\n    ands r1, r1, #1\n    ands r0, r1\n    strb r0, [r4, #7]\n    ldrb r0, [r4, #7]\n    cmp r0, #0\n    beq L_open_cfw_runtime_am051_b39f6_004c\n    ldr r0, [r4]\n    cmp r0, #0\n    bne L_open_cfw_runtime_am051_b39f6_004c\n    ldrb r0, [r4, #4]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am051_addr_004b6eea\n    bl .\n    movs r7, r0\n    ldrb r0, [r4, #4]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am051_addr_004b6ed8\n    bl .\n    movs r2, #0\n    movs r1, r7\n    uxtb r0, r0\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am051_addr_0047a71c\n    bl .\n    str r0, [r4]\nL_open_cfw_runtime_am051_b39f6_004c:\n    movs r0, #0\n    strb r0, [r4, #0xb]\n    ldr r0, [r5]\n    ldrb.w r8, [r0, #2]\n    ldr r0, [r5]\n    ldrb r7, [r0, #1]\n    ldrb r0, [r4, #4]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am051_addr_004b6ed8\n    bl .\n    cmp r0, #1\n    bne L_open_cfw_runtime_am051_b39f6_0068\n    orrs r7, r7, #2\nL_open_cfw_runtime_am051_b39f6_0068:\n    ldrb r0, [r6, #7]\n    ands.w r8, r0, r8\n    ldrb r0, [r6, #6]\n    ands r7, r0\n    uxtb.w r8, r8\n    str.w r8, [sp]\n    movs r3, r7\n    uxtb r3, r3\n    ldr r0, [r5]\n    ldrb r2, [r0]\n    ldr r0, [r5]\n    ldrb r1, [r0, #3]\n    ldrb r0, [r4, #4]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am051_addr_0052bacc\n    bl .\n    pop.w {r0, r1, r4, r5, r6, r7, r8, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM051_B3A86_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am051_b3a86(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    movs r2, r1\n    ldrb r1, [r2, #7]\n    cmp r1, #0\n    beq L_open_cfw_runtime_am051_b3a86_0020\n    ldr r1, [r2]\n    cmp r1, #0\n    beq L_open_cfw_runtime_am051_b3a86_0020\n    ldrb r3, [r2, #0xb]\n    ldrb r1, [r0, #0x1e]\n    orrs r3, r1\n    strb r3, [r2, #0xb]\n    movs r1, r0\n    ldr r0, [r2]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am051_addr_0047aed4\n    bl .\nL_open_cfw_runtime_am051_b3a86_0020:\n    pop {r0, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM051_B3AA8_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am051_b3aa8(void)
{
    __asm__ volatile(
        "    push {r3, r4, r5, lr}\n    movs r4, r0\n    movs r5, r1\n    ldrb r0, [r5, #7]\n    cmp r0, #0\n    beq L_open_cfw_runtime_am051_b3aa8_0040\n    movs r0, #1\n    strb r0, [r5, #5]\n    ldr r0, [r5]\n    cmp r0, #0\n    beq L_open_cfw_runtime_am051_b3aa8_001e\n    ldrb r1, [r5, #0xb]\n    ldr r0, [r5]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am051_addr_0047a49c\n    bl .\nL_open_cfw_runtime_am051_b3aa8_001e:\n    movs r0, #0\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am051_addr_004b467c\n    bl .\n    ldr r0, [pc, #0x1bc]\n    ldrb.w r0, [r0, #0x5d]\n    cmp r0, #1\n    bne L_open_cfw_runtime_am051_b3aa8_0032\n    movs r0, #1\n    strb r0, [r5, #9]\nL_open_cfw_runtime_am051_b3aa8_0032:\n    ldr r0, [r5]\n    cmp r0, #0\n    beq L_open_cfw_runtime_am051_b3aa8_0040\n    ldrb r1, [r5, #4]\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am051_addr_004bb098\n    bl .\nL_open_cfw_runtime_am051_b3aa8_0040:\n    pop {r0, r4, r5, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM051_B3AEA_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am051_b3aea(void)
{
    __asm__ volatile(
        "    bx lr\n"
    );
}
#endif

#if defined(OPEN_CFW_AM051_B3AEC_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am051_b3aec(void)
{
    __asm__ volatile(
        "    push {r4, r5, r6, lr}\n    ldrb r2, [r1, #6]\n    cmp r2, #0\n    beq L_open_cfw_runtime_am051_b3aec_0016\n    ldrb r2, [r0, #4]\n    cmp r2, #0\n    beq L_open_cfw_runtime_am051_b3aec_0016\n    movs r2, #1\n    strb r2, [r1, #5]\n    movs r2, #0\n    strb r2, [r1, #6]\nL_open_cfw_runtime_am051_b3aec_0016:\n    ldr.w r1, [pc, #0x8f4]\n    ldrb r1, [r1]\n    cmp r1, #0\n    beq L_open_cfw_runtime_am051_b3aec_005e\n    movs r1, #0\n    ldrh r6, [r0]\n    movs r0, r6\n    uxtb r0, r0\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am051_addr_004bb07c\n    bl .\n    adds r0, #0x6c\n    mov r8, r8\n    movs r4, r0\n    cmp r4, #0\n    beq L_open_cfw_runtime_am051_b3aec_005e\n    movs r5, #0\n    b L_open_cfw_runtime_am051_b3aec_0052\nL_open_cfw_runtime_am051_b3aec_003a:\n    ldrh r0, [r4]\n    cmp r0, #0\n    beq L_open_cfw_runtime_am051_b3aec_004e\n    ldrh r2, [r4]\n    movs r1, r5\n    uxtb r1, r1\n    movs r0, r6\n    uxtb r0, r0\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am051_addr_0052c60e\n    bl .\nL_open_cfw_runtime_am051_b3aec_004e:\n    adds r5, r5, #1\n    adds r4, r4, #2\nL_open_cfw_runtime_am051_b3aec_0052:\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am051_addr_0052c664\n    bl .\n    movs r1, r5\n    uxtb r1, r1\n    cmp r1, r0\n    blo L_open_cfw_runtime_am051_b3aec_003a\nL_open_cfw_runtime_am051_b3aec_005e:\n    pop {r4, r5, r6, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM051_B3B4C_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am051_b3b4c(void)
{
    __asm__ volatile(
        "    push {r3, r4, r5, lr}\n    movs r5, r0\n    movs r4, r1\n    ldr r0, [r4]\n    cmp r0, #0\n    bne L_open_cfw_runtime_am051_b3b4c_003a\n    ldrh r0, [r5, #0xe]\n    cmp r0, #0\n    bne L_open_cfw_runtime_am051_b3b4c_0022\n    movs r2, #8\n    ldr.w r1, [pc, #0xa48]\n    adds r0, r5, #6\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am051_addr_004751c8\n    bl .\n    cmp r0, #0\n    beq L_open_cfw_runtime_am051_b3b4c_0042\nL_open_cfw_runtime_am051_b3b4c_0022:\n    adds r1, r5, #6\n    ldrh r0, [r5, #0xe]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am051_addr_0047add4\n    bl .\n    str r0, [r4]\n    ldr r0, [r4]\n    cmp r0, #0\n    beq L_open_cfw_runtime_am051_b3b4c_003a\n    movs r0, #0\n    ldr r1, [pc, #0x108]\n    strb.w r0, [r1, #0x74]\nL_open_cfw_runtime_am051_b3b4c_003a:\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am051_b36b2\n    bl .\nL_open_cfw_runtime_am051_b3b4c_0040:\n    pop {r0, r4, r5, pc}\nL_open_cfw_runtime_am051_b3b4c_0042:\n    ldr r1, [pc, #0xfc]\n    ldrb.w r0, [r1, #0x74]\n    cmp r0, #0\n    beq L_open_cfw_runtime_am051_b3b4c_003a\n    movs r0, #1\n    strb.w r0, [r1, #0x6c]\n    b L_open_cfw_runtime_am051_b3b4c_0040\n"
    );
}
#endif

#if defined(OPEN_CFW_AM051_B3BA0_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am051_b3ba0(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    ldrb r0, [r0, #3]\n    cmp r0, #0\n    bne L_open_cfw_runtime_am051_b3ba0_0012\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am051_addr_004d2a7e\n    bl .\n    uxtb r0, r0\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am051_addr_0052dc24\n    bl .\nL_open_cfw_runtime_am051_b3ba0_0012:\n    pop {r0, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM051_B3BB4_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am051_b3bb4(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    movs r2, r1\n    ldrb r0, [r0, #3]\n    cmp r0, #0\n    bne L_open_cfw_runtime_am051_b3bb4_001c\n    cmp r2, #0\n    beq L_open_cfw_runtime_am051_b3bb4_001c\n    ldr r0, [r2]\n    cmp r0, #0\n    beq L_open_cfw_runtime_am051_b3bb4_001c\n    movs r1, #1\n    ldr r0, [r2]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am051_addr_0047b4ce\n    bl .\nL_open_cfw_runtime_am051_b3bb4_001c:\n    pop {r0, pc}\n"
    );
}
#endif
