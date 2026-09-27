/*
 * SPDX-License-Identifier: MIT
 *
 * Source-owned exact helpers from the AM-062 retained island.
 */

#if defined(OPEN_CFW_AM062_CF564_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am062_cf564(void)
{
    __asm__ volatile(
        "    uxtb r1, r1\n    ldr r2, [r0, #0x30]\n    bfi r2, r1, #9, #1\n    str r2, [r0, #0x30]\n    bx lr\n"
    );
}
#endif

#if defined(OPEN_CFW_AM062_CF570_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am062_cf570(void)
{
    __asm__ volatile(
        "    push {r3, r4, r5, lr}\n    movs r4, r0\n    movs r5, r1\n    ldr r0, [r4, #0x30]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am062_addr_004caeb8\n    bl .\n    cmp r0, #0\n    bne L_open_cfw_runtime_am062_cf570_002c\n    movs r0, r5\n    sxtb r0, r0\n    cmp r0, #0\n    bpl L_open_cfw_runtime_am062_cf570_002c\n    movw r2, #0x131c\n    ldr.w r1, [pc, #0x49c]\n    ldr.w r0, [pc, #0x71c]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am062_addr_004d09b4\n    bl .\n    nop.w\nL_open_cfw_runtime_am062_cf570_002c:\n    ldr r0, [r4, #0x30]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am062_addr_004caeb8\n    bl .\n    movw r1, #0x1ff\n    cmp r0, r1\n    blo L_open_cfw_runtime_am062_cf570_0056\n    movs r0, r5\n    sxtb r0, r0\n    cmp r0, #1\n    blt L_open_cfw_runtime_am062_cf570_0056\n    movw r2, #0x131d\n    ldr.w r1, [pc, #0x474]\n    ldr.w r0, [pc, #0x6f8]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am062_addr_004d09b4\n    bl .\n    nop.w\nL_open_cfw_runtime_am062_cf570_0056:\n    ldr r0, [r4, #0x30]\n    sxtab r0, r0, r5\n    str r0, [r4, #0x30]\n    adds.w r0, r4, #0x30\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am062_addr_004caf0c\n    bl .\n    uxtb r0, r0\n    ldr r1, [r4, #0x30]\n    bfi r1, r0, #0x1f, #1\n    str r1, [r4, #0x30]\n    movs r0, #0\n    pop {r1, r4, r5, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM062_CF5EC_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am062_cf5ec(void)
{
    __asm__ volatile(
        "    push {r4, r5}\n    movw r3, #0x3ff\n    movs r4, r1\n    movs r5, r3\n    uxth r4, r4\n    cmp r4, r5\n    beq L_open_cfw_runtime_am062_cf5ec_001e\n    movs r5, r1\n    uxth r5, r5\n    ldr.w r4, [pc, #0x6b4]\n    orrs.w r4, r4, r5, lsl #10\n    b L_open_cfw_runtime_am062_cf5ec_0020\nL_open_cfw_runtime_am062_cf5ec_001e:\n    movs r4, #0\nL_open_cfw_runtime_am062_cf5ec_0020:\n    ldr r5, [r0, #0x30]\n    bfc r5, #0xa, #0x15\n    orrs r4, r5\n    str r4, [r0, #0x30]\n    movs r4, r1\n    movs r5, r3\n    uxth r4, r4\n    cmp r4, r5\n    beq L_open_cfw_runtime_am062_cf5ec_0038\n    ldr r4, [r2]\n    b L_open_cfw_runtime_am062_cf5ec_003a\nL_open_cfw_runtime_am062_cf5ec_0038:\n    movs r4, #0\nL_open_cfw_runtime_am062_cf5ec_003a:\n    str r4, [r0, #0x34]\n    uxth r1, r1\n    cmp r1, r3\n    beq L_open_cfw_runtime_am062_cf5ec_0046\n    ldr r1, [r2, #4]\n    b L_open_cfw_runtime_am062_cf5ec_0048\nL_open_cfw_runtime_am062_cf5ec_0046:\n    movs r1, #0\nL_open_cfw_runtime_am062_cf5ec_0048:\n    str r1, [r0, #0x38]\n    pop {r4, r5}\n    bx lr\n"
    );
}
#endif

#if defined(OPEN_CFW_AM062_CF648_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am062_cf648(void)
{
    __asm__ volatile(
        "    push {r4, lr}\n    sub sp, #0x40\n    movs r4, r0\n    adds.w r0, r4, #0x30\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am062_addr_004caf44\n    bl .\n    cmp r0, #0\n    bne L_open_cfw_runtime_am062_cf648_0016\n    movs r0, #0\n    b L_open_cfw_runtime_am062_cf648_0090\nL_open_cfw_runtime_am062_cf648_0016:\n    adr r0, #0x2e4\n    str r0, [sp, #4]\n    ldr r0, [r4, #0x24]\n    str r0, [sp]\n    ldr r3, [r4, #0x20]\n    movw r2, #0x1338\n    ldr.w r1, [pc, #0x3bc]\n    ldr.w r0, [pc, #0x648]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am062_addr_004733ee\n    bl .\n    adds.w r2, r4, #0x20\n    add r1, sp, #0x20\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am062_addr_004cbedc\n    bl .\n    cmp r0, #0\n    bne L_open_cfw_runtime_am062_cf648_0090\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am062_addr_004cb0c4\n    bl .\n    str r0, [sp]\n    ldr r0, [r4, #0x68]\n    ldr r0, [r0, #0x1c]\n    str r0, [sp, #4]\n    ldr r0, [r4, #0x6c]\n    str r0, [sp, #8]\n    ldr r0, [r4, #0x70]\n    str r0, [sp, #0xc]\n    ldr r0, [r4, #0x74]\n    str r0, [sp, #0x10]\n    ldr r0, [r4, #0x78]\n    str r0, [sp, #0x14]\n    mov r0, sp\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am062_addr_004cb04c\n    bl .\n    add r0, sp, #0x18\n    ldr.w r1, [pc, #0x610]\n    ldrd r2, r3, [r1]\n    strd r2, r3, [r0]\n    mov r0, sp\n    str r0, [sp, #0x1c]\n    movs r3, #1\n    add r2, sp, #0x18\n    add r1, sp, #0x20\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am062_addr_004cd388\n    bl .\n    cmp r0, #0\n    bne L_open_cfw_runtime_am062_cf648_0090\n    movs r1, #0\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am062_cf564\n    bl .\n    movs r0, #0\nL_open_cfw_runtime_am062_cf648_0090:\n    add sp, #0x40\n    pop {r4, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM062_CF6E8_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am062_cf6e8(void)
{
    __asm__ volatile(
        "    push {r4, r5, lr}\n    sub sp, #0x34\n    movs r4, r0\n    adds.w r0, r4, #0x3c\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am062_addr_004caf2e\n    bl .\n    cmp r0, #0\n    bne L_open_cfw_runtime_am062_cf6e8_0016\n    movs r0, #0\n    b L_open_cfw_runtime_am062_cf6e8_00a8\nL_open_cfw_runtime_am062_cf6e8_0016:\n    ldr r0, [r4, #0x3c]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am062_addr_004caeb0\n    bl .\n    ldr.w r5, [pc, #0x324]\n    adr r1, #0x238\n    str r1, [sp, #8]\n    uxth r0, r0\n    str r0, [sp, #4]\n    ldr r0, [r4, #0x44]\n    str r0, [sp]\n    ldr r3, [r4, #0x40]\n    movw r2, #0x1361\n    movs r1, r5\n    ldr.w r0, [pc, #0x5a4]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am062_addr_004733ee\n    bl .\n    ldr r0, [r4, #0x3c]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am062_addr_004cae98\n    bl .\n    movw r1, #0x4ff\n    cmp r0, r1\n    beq L_open_cfw_runtime_am062_cf6e8_005c\n    movw r2, #0x1365\n    movs r1, r5\n    ldr.w r0, [pc, #0x58c]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am062_addr_004d09b4\n    bl .\n    nop.w\nL_open_cfw_runtime_am062_cf6e8_005c:\n    adds.w r2, r4, #0x40\n    add r1, sp, #0x14\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am062_addr_004cbedc\n    bl .\n    cmp r0, #0\n    bne L_open_cfw_runtime_am062_cf6e8_00a8\n    ldr r0, [r4, #0x3c]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am062_addr_004caeb0\n    bl .\n    movs r5, r0\n    movs r2, #0\n    movw r1, #0x3ff\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am062_cf5ec\n    bl .\n    add r0, sp, #0xc\n    movs r1, #0\n    movs r2, #0\n    strd r1, r2, [r0]\n    uxth r5, r5\n    ldr.w r0, [pc, #0x540]\n    orrs.w r0, r0, r5, lsl #10\n    str r0, [sp, #0xc]\n    movs r3, #1\n    add r2, sp, #0xc\n    add r1, sp, #0x14\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am062_addr_004cd388\n    bl .\n    cmp r0, #0\n    bne L_open_cfw_runtime_am062_cf6e8_00a8\n    movs r0, #0\nL_open_cfw_runtime_am062_cf6e8_00a8:\n    add sp, #0x34\n    pop {r4, r5, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM062_CF7AC_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am062_cf7ac(void)
{
    __asm__ volatile(
        "    push.w {r3, r4, r5, r6, r7, r8, sb, sl, fp, lr}\n    sub sp, #0x90\n    movs r5, r0\n    movs r6, r1\n    adds.w r0, r5, #0x30\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am062_addr_004caf0c\n    bl .\n    cmp r0, #0\n    bne L_open_cfw_runtime_am062_cf7ac_001a\n    movs r0, #0\n    b L_open_cfw_runtime_am062_cf7ac_0222\nL_open_cfw_runtime_am062_cf7ac_001a:\n    movs r4, #0\n    b L_open_cfw_runtime_am062_cf7ac_0020\n    movs r4, #0\nL_open_cfw_runtime_am062_cf7ac_0020:\n    cmp r4, #2\n    bge.w #0x4cf9b8\n    add r0, sp, #0x18\n    ldr.w r1, [pc, #0x4f4]\n    movs r2, #0x20\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am062_addr_00439c04\n    bl .\n    movs r7, #0\n    b L_open_cfw_runtime_am062_cf7ac_003e\n    cmp.w r8, #3\n    bne L_open_cfw_runtime_am062_cf7ac_003e\n    movs r7, #1\nL_open_cfw_runtime_am062_cf7ac_003e:\n    add r0, sp, #0x30\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am062_addr_004cadd0\n    bl .\n    cmp r0, #0\n    bne.w #0x4cf9ac\n    add r2, sp, #0x30\n    add r1, sp, #0x50\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am062_addr_004cbedc\n    bl .\n    cmp r0, #0\n    bne L_open_cfw_runtime_am062_cf7ac_013e\n    ldrb.w r0, [sp, #0x2f]\n    cmp r0, #0\n    bne.w #0x4cf9a0\n    add r2, sp, #0x70\n    add r1, sp, #0x30\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am062_addr_004cf4da\n    bl .\n    mov r8, r0\n    cmp.w r8, #0\n    bpl L_open_cfw_runtime_am062_cf7ac_007a\n    cmn.w r8, #2\n    bne L_open_cfw_runtime_am062_cf7ac_0140\nL_open_cfw_runtime_am062_cf7ac_007a:\n    cmp r4, #0\n    bne L_open_cfw_runtime_am062_cf7ac_016e\n    cmn.w r8, #2\n    beq L_open_cfw_runtime_am062_cf7ac_016e\n    add r0, sp, #0x10\n    str r0, [sp]\n    mov r3, r8\n    ldr r2, [pc, #0x218]\n    add r1, sp, #0x70\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am062_addr_004cb3c8\n    bl .\n    cmp r0, #0\n    bmi L_open_cfw_runtime_am062_cf7ac_0144\n    add r0, sp, #0x10\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am062_addr_004cae3e\n    bl .\n    add r1, sp, #0x30\n    add r0, sp, #0x10\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am062_addr_004cae14\n    bl .\n    cmp r0, #0\n    bne L_open_cfw_runtime_am062_cf7ac_016e\n    ldr.w sb, [pc, #0x1d4]\n    addw sl, pc, #0xe8\n    str.w sl, [sp, #0xc]\n    ldr r0, [sp, #0x14]\n    str r0, [sp, #8]\n    ldr r0, [sp, #0x10]\n    str r0, [sp, #4]\n    ldr r0, [sp, #0x34]\n    str r0, [sp]\n    ldr r3, [sp, #0x30]\n    movw r2, #0x13ae\n    mov r1, sb\n    ldr.w r0, [pc, #0x458]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am062_addr_004733ee\n    bl .\n    movw fp, #0x3ff\n    mov r8, fp\n    add r1, sp, #0x18\n    adds.w r0, r5, #0x30\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am062_addr_004caf5c\n    bl .\n    cmp r0, #0\n    beq L_open_cfw_runtime_am062_cf7ac_0116\n    ldr r0, [r5, #0x30]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am062_addr_004caeb0\n    bl .\n    mov r8, r0\n    str.w sl, [sp, #8]\n    mov r0, r8\n    uxth r0, r0\n    str r0, [sp, #4]\n    ldr r0, [sp, #0x1c]\n    str r0, [sp]\n    ldr r3, [sp, #0x18]\n    movw r2, #0x13b8\n    mov r1, sb\n    ldr.w r0, [pc, #0x420]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am062_addr_004733ee\n    bl .\n    movs r2, #0\n    mov r1, fp\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am062_cf5ec\n    bl .\nL_open_cfw_runtime_am062_cf7ac_0116:\n    add r0, sp, #0x10\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am062_addr_004cae54\n    bl .\n    add r0, sp, #0x40\n    ldr.w r1, [pc, #0x40c]\n    movs r2, #0x10\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am062_addr_00439c04\n    bl .\n    mov r0, r8\n    uxth r0, r0\n    cmp r0, fp\n    beq L_open_cfw_runtime_am062_cf7ac_0146\n    uxth.w r8, r8\n    ldr.w r0, [pc, #0x3d4]\n    orrs.w r0, r0, r8, lsl #10\n    b L_open_cfw_runtime_am062_cf7ac_0148\nL_open_cfw_runtime_am062_cf7ac_013e:\n    b L_open_cfw_runtime_am062_cf7ac_0222\nL_open_cfw_runtime_am062_cf7ac_0140:\n    mov r0, r8\n    b L_open_cfw_runtime_am062_cf7ac_0222\nL_open_cfw_runtime_am062_cf7ac_0144:\n    b L_open_cfw_runtime_am062_cf7ac_0222\nL_open_cfw_runtime_am062_cf7ac_0146:\n    movs r0, #0\nL_open_cfw_runtime_am062_cf7ac_0148:\n    str r0, [sp, #0x40]\n    add r0, sp, #0x10\n    str r0, [sp, #0x4c]\n    movs r3, #2\n    add r2, sp, #0x40\n    add r1, sp, #0x18\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am062_addr_004ccf7c\n    bl .\n    mov r8, r0\n    add r0, sp, #0x10\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am062_addr_004cae3e\n    bl .\n    cmp.w r8, #0\n    bpl.w #0x4cf7e2\n    mov r0, r8\n    b L_open_cfw_runtime_am062_cf7ac_0222\nL_open_cfw_runtime_am062_cf7ac_016e:\n    cmp r4, #1\n    bne L_open_cfw_runtime_am062_cf7ac_01f4\n    cmn.w r8, #2\n    bne L_open_cfw_runtime_am062_cf7ac_01f4\n    movs r0, r6\n    uxtb r0, r0\n    cmp r0, #0\n    beq L_open_cfw_runtime_am062_cf7ac_01f4\n    adr r0, #0x14\n    str r0, [sp, #4]\n    ldr r0, [sp, #0x34]\n    str r0, [sp]\n    ldr r3, [sp, #0x30]\n    movw r2, #0x13d7\n    ldr r1, [pc, #0xf0]\n    ldr.w r0, [pc, #0x39c]\n    b L_open_cfw_runtime_am062_cf7ac_019c\n    nop\n    movs r0, r0\n    movs r0, r0\nL_open_cfw_runtime_am062_cf7ac_019c:\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am062_addr_004733ee\n    bl .\n    adds.w r2, r5, #0x48\n    add r1, sp, #0x50\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am062_addr_004cbefc\n    bl .\n    cmp r0, #0\n    bne L_open_cfw_runtime_am062_cf7ac_0222\n    add r0, sp, #0x68\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am062_addr_004cae54\n    bl .\n    ldrb.w r0, [sp, #0x67]\n    adds.w r0, r0, #0x600\n    ldr.w r1, [pc, #0x374]\n    orrs.w r1, r1, r0, lsl #20\n    str r1, [sp, #0x38]\n    add r0, sp, #0x68\n    str r0, [sp, #0x3c]\n    movs r3, #1\n    add r2, sp, #0x38\n    add r1, sp, #0x18\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am062_addr_004ccf7c\n    bl .\n    mov r8, r0\n    add r0, sp, #0x68\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am062_addr_004cae3e\n    bl .\n    cmp.w r8, #0\n    bpl L_open_cfw_runtime_am062_cf7ac_01ea\n    mov r0, r8\n    b L_open_cfw_runtime_am062_cf7ac_0222\nL_open_cfw_runtime_am062_cf7ac_01ea:\n    cmp.w r8, #3\n    bne L_open_cfw_runtime_am062_cf7ac_01f2\n    movs r7, #1\nL_open_cfw_runtime_am062_cf7ac_01f2:\n    b L_open_cfw_runtime_am062_cf7ac_003e\nL_open_cfw_runtime_am062_cf7ac_01f4:\n    add r0, sp, #0x18\n    add r1, sp, #0x50\n    movs r2, #0x20\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am062_addr_00439c04\n    bl .\n    b L_open_cfw_runtime_am062_cf7ac_003e\n    uxtb r7, r7\n    cmp r7, #0\n    bne.w #0x4cf7ca\n    adds r4, r4, #1\n    b L_open_cfw_runtime_am062_cf7ac_0020\n    adds.w r0, r5, #0x30\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am062_addr_004caf22\n    bl .\n    uxtb r0, r0\n    rsbs r0, r0, #0\n    movs r1, r0\n    sxtb r1, r1\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am062_cf570\n    bl .\nL_open_cfw_runtime_am062_cf7ac_0222:\n    add sp, #0x94\n    pop.w {r4, r5, r6, r7, r8, sb, sl, fp, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM062_CF9E0_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am062_cf9e0(void)
{
    __asm__ volatile(
        "    push {r4, lr}\n    movs r4, r0\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am062_cf648\n    bl .\n    cmp r0, #0\n    bne L_open_cfw_runtime_am062_cf9e0_0026\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am062_cf6e8\n    bl .\n    cmp r0, #0\n    bne L_open_cfw_runtime_am062_cf9e0_0026\n    movs r1, #1\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am062_cf7ac\n    bl .\n    cmp r0, #0\n    bne L_open_cfw_runtime_am062_cf9e0_0026\n    movs r0, #0\nL_open_cfw_runtime_am062_cf9e0_0026:\n    pop {r4, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM062_CFA12_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am062_cfa12(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    movs r1, #0\n    str r1, [sp]\n    movs r3, #0\n    mov r2, sp\n    ldr.w r1, [pc, #0x2c4]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am062_addr_004cf284\n    bl .\n    cmp r0, #0\n    bne L_open_cfw_runtime_am062_cfa12_0018\n    ldr r0, [sp]\nL_open_cfw_runtime_am062_cfa12_0018:\n    pop {r1, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM062_CFA58_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am062_cfa58(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    movs r2, #0\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am062_addr_004cee2a\n    bl .\n    pop {r1, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM062_CFA62_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am062_cfa62(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    movs r2, #0\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am062_addr_004cef78\n    bl .\n    pop {r1, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM062_CFA6C_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am062_cfa6c(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    movs r1, #0\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am062_addr_004cf274\n    bl .\n    pop {r1, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM062_CFA76_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am062_cfa76(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    movs r2, #0\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am062_addr_004ce4dc\n    bl .\n    pop {r1, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM062_CFA80_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am062_cfa80(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    movs r3, #0\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am062_addr_004ce614\n    bl .\n    pop {r1, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM062_CFA8A_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am062_cfa8a(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    movs r3, #0\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am062_addr_004ce48a\n    bl .\n    pop {r1, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM062_CFA94_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am062_cfa94(void)
{
    __asm__ volatile(
        "    push {r3, r4, r5, r6, r7, lr}\n    movs r4, r0\n    movs r5, r1\n    movs r6, r2\n    movs r7, r3\n    movs r0, #0\n    movs r1, r5\n    ldr r0, [r4, #0x28]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am062_addr_004cb082\n    bl .\n    cmp r0, #0\n    beq L_open_cfw_runtime_am062_cfa94_0028\n    movw r2, #0x17e7\n    ldr r1, [pc, #0x234]\n    ldr r0, [pc, #0x238]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am062_addr_004d09b4\n    bl .\n    nop.w\nL_open_cfw_runtime_am062_cfa94_0028:\n    movs r3, r7\n    movs r2, r6\n    movs r1, r5\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am062_addr_004cdcc8\n    bl .\n    pop {r1, r4, r5, r6, r7, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM062_CFAD0_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am062_cfad0(void)
{
    __asm__ volatile(
        "    push {r3, r4, r5, lr}\n    movs r4, r0\n    movs r5, r1\n    movs r0, #0\n    movs r1, r5\n    ldr r0, [r4, #0x28]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am062_addr_004cb082\n    bl .\n    cmp r0, #0\n    bne L_open_cfw_runtime_am062_cfad0_0024\n    movw r2, #0x180b\n    ldr r1, [pc, #0x1fc]\n    ldr r0, [pc, #0x204]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am062_addr_004d09b4\n    bl .\n    nop.w\nL_open_cfw_runtime_am062_cfad0_0024:\n    movs r1, r5\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am062_addr_004cdce4\n    bl .\n    pop {r1, r4, r5, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM062_CFB08_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am062_cfb08(void)
{
    __asm__ volatile(
        "    push {r3, r4, r5, lr}\n    movs r4, r0\n    movs r5, r1\n    movs r0, #0\n    movs r1, r5\n    ldr r0, [r4, #0x28]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am062_addr_004cb082\n    bl .\n    cmp r0, #0\n    bne L_open_cfw_runtime_am062_cfb08_0024\n    movw r2, #0x181b\n    ldr r1, [pc, #0x1c4]\n    ldr r0, [pc, #0x1cc]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am062_addr_004d09b4\n    bl .\n    nop.w\nL_open_cfw_runtime_am062_cfb08_0024:\n    movs r1, r5\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am062_addr_004cdf74\n    bl .\n    pop {r1, r4, r5, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM062_CFB40_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am062_cfb40(void)
{
    __asm__ volatile(
        "    push {r3, r4, r5, r6, r7, lr}\n    movs r4, r0\n    movs r5, r1\n    movs r6, r2\n    movs r7, r3\n    movs r0, #0\n    movs r1, r5\n    ldr r0, [r4, #0x28]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am062_addr_004cb082\n    bl .\n    cmp r0, #0\n    bne L_open_cfw_runtime_am062_cfb40_0028\n    movw r2, #0x182d\n    ldr r1, [pc, #0x188]\n    ldr r0, [pc, #0x190]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am062_addr_004d09b4\n    bl .\n    nop.w\nL_open_cfw_runtime_am062_cfb40_0028:\n    movs r3, r7\n    movs r2, r6\n    movs r1, r5\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am062_addr_004ce158\n    bl .\n    pop {r1, r4, r5, r6, r7, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM062_CFB7C_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am062_cfb7c(void)
{
    __asm__ volatile(
        "    push {r3, r4, r5, r6, r7, lr}\n    movs r4, r0\n    movs r5, r1\n    movs r6, r2\n    movs r7, r3\n    movs r0, #0\n    movs r1, r5\n    ldr r0, [r4, #0x28]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am062_addr_004cb082\n    bl .\n    cmp r0, #0\n    bne L_open_cfw_runtime_am062_cfb7c_0028\n    movw r2, #0x183f\n    ldr r1, [pc, #0x14c]\n    ldr r0, [pc, #0x154]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am062_addr_004d09b4\n    bl .\n    nop.w\nL_open_cfw_runtime_am062_cfb7c_0028:\n    movs r3, r7\n    movs r2, r6\n    movs r1, r5\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am062_addr_004ce308\n    bl .\n    pop {r1, r4, r5, r6, r7, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM062_CFBB2_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am062_cfbb2(void)
{
    __asm__ volatile(
        "    push {r3, r4, r5, r6, r7, lr}\n    movs r4, r0\n    movs r5, r1\n    movs r6, r2\n    movs r7, r3\n    movs r0, #0\n    movs r1, r5\n    ldr r0, [r4, #0x28]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am062_addr_004cb082\n    bl .\n    cmp r0, #0\n    bne L_open_cfw_runtime_am062_cfbb2_0028\n    movw r2, #0x1851\n    ldr r1, [pc, #0x118]\n    ldr r0, [pc, #0x11c]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am062_addr_004d09b4\n    bl .\n    nop.w\nL_open_cfw_runtime_am062_cfbb2_0028:\n    movs r3, r7\n    movs r2, r6\n    movs r1, r5\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am062_addr_004ce3bc\n    bl .\n    pop {r1, r4, r5, r6, r7, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM062_CFBE8_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am062_cfbe8(void)
{
    __asm__ volatile(
        "    push {r3, r4, r5, lr}\n    movs r4, r0\n    movs r5, r1\n    movs r0, #0\n    movs r1, r5\n    ldr r0, [r4, #0x28]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am062_addr_004cb082\n    bl .\n    cmp r0, #0\n    bne L_open_cfw_runtime_am062_cfbe8_0024\n    movw r2, #0x1872\n    ldr r1, [pc, #0xe4]\n    ldr r0, [pc, #0xec]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am062_addr_004d09b4\n    bl .\n    nop.w\nL_open_cfw_runtime_am062_cfbe8_0024:\n    movs r1, r5\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am062_addr_004ce45c\n    bl .\n    pop {r1, r4, r5, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM062_CFC24_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am062_cfc24(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    movs r2, #0\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am062_addr_004ce460\n    bl .\n    pop {r1, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM062_CFC2E_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am062_cfc2e(void)
{
    __asm__ volatile(
        "    b.w #0x7b7190\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n"
    );
}
#endif

#if defined(OPEN_CFW_AM062_CFC5C_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am062_cfc5c(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    movs r2, #0\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am062_addr_004cd3aa\n    bl .\n    pop {r1, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM062_CFC66_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am062_cfc66(void)
{
    __asm__ volatile(
        "    push {r4, r5, r6, lr}\n    movs r4, r0\n    movs r5, r1\n    movs r6, r2\n    movs r0, #0\n    movs r1, r5\n    ldr r0, [r4, #0x28]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am062_addr_004cb082\n    bl .\n    cmp r0, #0\n    beq L_open_cfw_runtime_am062_cfc66_0026\n    movw r2, #0x18ae\n    ldr r1, [pc, #0x64]\n    ldr r0, [pc, #0x70]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am062_addr_004d09b4\n    bl .\n    nop.w\nL_open_cfw_runtime_am062_cfc66_0026:\n    movs r2, r6\n    movs r1, r5\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am062_addr_004cd558\n    bl .\n    pop {r4, r5, r6, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM062_CFCF8_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am062_cfcf8(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    movs r2, #0\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am062_addr_004cd604\n    bl .\n    pop {r1, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM062_CFD02_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am062_cfd02(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    movs r3, #0\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am062_addr_004cd60e\n    bl .\n    pop {r1, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM062_CFD0C_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am062_cfd0c(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    movs r1, #0\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am062_cfa12\n    bl .\n    pop {r1, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM062_CFD18_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am062_cfd18(void)
{
    __asm__ volatile(
        "    movs r1, r0\n    movs r0, #0x20\n    cmp r1, #0\n    bne L_open_cfw_runtime_am062_cfd18_000a\n    subs r0, r0, #1\nL_open_cfw_runtime_am062_cfd18_000a:\n    lsrs r2, r1, #0x10\n    lsls r2, r2, #0x10\n    cmp r2, #0\n    bne L_open_cfw_runtime_am062_cfd18_0016\n    lsls r1, r1, #0x10\n    subs r0, #0x10\nL_open_cfw_runtime_am062_cfd18_0016:\n    tst.w r1, #-0x1000000\n    bne L_open_cfw_runtime_am062_cfd18_0020\n    lsls r1, r1, #8\n    subs r0, #8\nL_open_cfw_runtime_am062_cfd18_0020:\n    tst.w r1, #-0x10000000\n    bne L_open_cfw_runtime_am062_cfd18_002a\n    lsls r1, r1, #4\n    subs r0, r0, #4\nL_open_cfw_runtime_am062_cfd18_002a:\n    tst.w r1, #-0x40000000\n    bne L_open_cfw_runtime_am062_cfd18_0034\n    lsls r1, r1, #2\n    subs r0, r0, #2\nL_open_cfw_runtime_am062_cfd18_0034:\n    cmp r1, #0\n    bmi L_open_cfw_runtime_am062_cfd18_003c\n    lsls r1, r1, #1\n    subs r0, r0, #1\nL_open_cfw_runtime_am062_cfd18_003c:\n    bx lr\n"
    );
}
#endif

#if defined(OPEN_CFW_AM062_CFD56_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am062_cfd56(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    mvns r1, r0\n    adds r1, r1, #1\n    ands r0, r1\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am062_cfd18\n    bl .\n    subs r0, r0, #1\n    pop {r1, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM062_CFD66_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am062_cfd66(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am062_cfd18\n    bl .\n    subs r0, r0, #1\n    pop {r1, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM062_CFD70_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am062_cfd70(void)
{
    __asm__ volatile(
        "    ldr r0, [r0, #4]\n    ldr.w r1, [pc, #0x890]\n    ldr r2, [r1]\n    ldr.w r1, [pc, #0x95c]\n    ldr r1, [r1]\n    orrs r2, r1\n    bics r0, r2\n    bx lr\n"
    );
}
#endif
