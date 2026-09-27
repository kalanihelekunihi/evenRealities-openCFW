/*
 * SPDX-License-Identifier: MIT
 *
 * Source-owned exact helpers from the AM-041 retained island.
 */

#if defined(OPEN_CFW_AM041_8D868_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am041_8d868(void)
{
    __asm__ volatile(
        "    .reloc ., R_ARM_THM_JUMP11, open_cfw_runtime_am041_8d86c\n    b .\n"
    );
}
#endif

#if defined(OPEN_CFW_AM041_8D86C_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am041_8d86c(void)
{
    __asm__ volatile(
        "    movs r2, #0xa\n    movs r1, #0\n    .reloc ., R_ARM_THM_JUMP11, open_cfw_runtime_am041_addr_0048d866\n    b .\n"
    );
}
#endif

#if defined(OPEN_CFW_AM041_8D874_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am041_8d874(void)
{
    __asm__ volatile(
        "    nop\n    movs r3, #0\n    .reloc ., R_ARM_THM_JUMP11, open_cfw_runtime_am041_addr_0048d724\n    b .\n"
    );
}
#endif

#if defined(OPEN_CFW_AM041_8E1CC_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am041_8e1cc(void)
{
    __asm__ volatile(
        "    bx lr\n"
    );
}
#endif

#if defined(OPEN_CFW_AM041_8E52E_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am041_8e52e(void)
{
    __asm__ volatile(
        "    push {r1, r2, r3, r4, r5, lr}\n    movs r4, r0\n    movs r5, r1\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am041_addr_0043d0ce\n    bl .\n    lsls r0, r0, #0x1e\n    bpl L_open_cfw_runtime_am041_8e52e_0026\n    ldr.w r0, [pc, #0x32c]\n    str r0, [sp, #4]\n    movs r0, #0x31\n    str r0, [sp]\n    ldr.w r3, [pc, #0x328]\n    ldr r2, [pc, #0x30c]\n    ldr r1, [pc, #0x30c]\n    movs r0, #4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am041_addr_0043d574\n    bl .\nL_open_cfw_runtime_am041_8e52e_0026:\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am041_addr_0043d0ce\n    bl .\n    lsls r0, r0, #0x1f\n    bmi L_open_cfw_runtime_am041_8e52e_0036\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am041_addr_0043d0ce\n    bl .\n    lsls r0, r0, #0x1d\n    bpl L_open_cfw_runtime_am041_8e52e_0042\nL_open_cfw_runtime_am041_8e52e_0036:\n    ldr r2, [pc, #0x30c]\n    movs r1, r2\n    movs.w r0, #0x10000000\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am041_addr_0043ce9e\n    bl .\nL_open_cfw_runtime_am041_8e52e_0042:\n    ldr r3, [pc, #0x304]\n    movs r2, r5\n    uxth r2, r2\n    movs r1, r4\n    movw r0, #0x101\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am041_addr_00464d1c\n    bl .\n    pop {r0, r1, r2, r4, r5, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM041_8E582_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am041_8e582(void)
{
    __asm__ volatile(
        "    push.w {r3, r4, r5, r6, r7, r8, sb, sl, fp, lr}\n    sub sp, #0x10\n    mov fp, r1\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am041_addr_004d7f7e\n    bl .\n    str r0, [sp, #8]\n    ldr r0, [sp, #8]\n    cmp r0, #0\n    bne L_open_cfw_runtime_am041_8e582_004e\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am041_addr_0043d0ce\n    bl .\n    lsls r0, r0, #0x1e\n    bpl L_open_cfw_runtime_am041_8e582_0030\n    ldr r0, [pc, #0x2dc]\n    str r0, [sp, #4]\n    movs r0, #0x39\n    str r0, [sp]\n    ldr r3, [pc, #0x2d8]\n    ldr r2, [pc, #0x2ac]\n    ldr r1, [pc, #0x2b0]\n    movs r0, #1\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am041_addr_0043d574\n    bl .\nL_open_cfw_runtime_am041_8e582_0030:\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am041_addr_0043d0ce\n    bl .\n    lsls r0, r0, #0x1f\n    bmi L_open_cfw_runtime_am041_8e582_0040\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am041_addr_0043d0ce\n    bl .\n    lsls r0, r0, #0x1d\n    bpl L_open_cfw_runtime_am041_8e582_004c\nL_open_cfw_runtime_am041_8e582_0040:\n    ldr r2, [pc, #0x2c0]\n    movs r1, r2\n    movs.w r0, #0x4000000\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am041_addr_0043ce9e\n    bl .\nL_open_cfw_runtime_am041_8e582_004c:\n    b L_open_cfw_runtime_am041_8e582_01a4\nL_open_cfw_runtime_am041_8e582_004e:\n    ldr r1, [pc, #0x2b4]\n    ldr r0, [sp, #8]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am041_addr_004d83aa\n    bl .\n    mov sl, r0\n    cmp.w sl, #0\n    bne L_open_cfw_runtime_am041_8e582_009e\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am041_addr_0043d0ce\n    bl .\n    lsls r0, r0, #0x1e\n    bpl L_open_cfw_runtime_am041_8e582_007a\n    ldr r0, [pc, #0x2a0]\n    str r0, [sp, #4]\n    movs r0, #0x3f\n    str r0, [sp]\n    ldr r3, [pc, #0x28c]\n    ldr r2, [pc, #0x264]\n    ldr r1, [pc, #0x264]\n    movs r0, #1\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am041_addr_0043d574\n    bl .\nL_open_cfw_runtime_am041_8e582_007a:\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am041_addr_0043d0ce\n    bl .\n    lsls r0, r0, #0x1f\n    bmi L_open_cfw_runtime_am041_8e582_008a\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am041_addr_0043d0ce\n    bl .\n    lsls r0, r0, #0x1d\n    bpl L_open_cfw_runtime_am041_8e582_0096\nL_open_cfw_runtime_am041_8e582_008a:\n    ldr r1, [pc, #0x280]\n    movs r2, r1\n    movs.w r0, #0x4000000\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am041_addr_0043ce9e\n    bl .\nL_open_cfw_runtime_am041_8e582_0096:\n    ldr r0, [sp, #8]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am041_addr_004d79fa\n    bl .\n    b L_open_cfw_runtime_am041_8e582_01a4\nL_open_cfw_runtime_am041_8e582_009e:\n    ldr r1, [pc, #0x270]\n    mov r0, sl\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am041_addr_004d83aa\n    bl .\n    str r0, [sp, #0xc]\n    ldr r1, [pc, #0x26c]\n    mov r0, sl\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am041_addr_004d83aa\n    bl .\n    str r0, [sp, #4]\n    ldr r1, [pc, #0x264]\n    mov r0, sl\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am041_addr_004d83aa\n    bl .\n    movs r4, r0\n    ldr r1, [pc, #0x260]\n    mov r0, sl\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am041_addr_004d83aa\n    bl .\n    movs r5, r0\n    ldr r1, [pc, #0x258]\n    mov r0, sl\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am041_addr_004d83aa\n    bl .\n    movs r6, r0\n    ldr r1, [pc, #0x254]\n    mov r0, sl\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am041_addr_004d83aa\n    bl .\n    movs r7, r0\n    ldr r1, [pc, #0x24c]\n    mov r0, sl\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am041_addr_004d83aa\n    bl .\n    mov r8, r0\n    ldr r1, [pc, #0x248]\n    mov r0, sl\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am041_addr_004d83aa\n    bl .\n    mov sb, r0\n    ldr r1, [pc, #0x240]\n    mov r0, sl\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am041_addr_004d83aa\n    bl .\n    mov sl, r0\n    mov.w r1, #0x2fc\n    movs r2, #0\n    str.w fp, [sp]\n    ldr r0, [sp]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am041_addr_0043c0e4\n    bl .\n    ldr r0, [sp]\n    ldr r0, [sp, #4]\n    cmp r0, #0\n    beq L_open_cfw_runtime_am041_8e582_0118\n    ldr r0, [sp, #4]\n    ldr r0, [r0, #0x14]\n    str.w r0, [fp]\nL_open_cfw_runtime_am041_8e582_0118:\n    cmp r4, #0\n    beq L_open_cfw_runtime_am041_8e582_0122\n    ldr r0, [r4, #0x14]\n    strb.w r0, [fp, #0x2f8]\nL_open_cfw_runtime_am041_8e582_0122:\n    cmp r5, #0\n    beq L_open_cfw_runtime_am041_8e582_012c\n    ldr r0, [r5, #0x14]\n    strb.w r0, [fp, #4]\nL_open_cfw_runtime_am041_8e582_012c:\n    ldr r0, [sp, #0xc]\n    cmp r0, #0\n    beq L_open_cfw_runtime_am041_8e582_0140\n    movs r2, #0x3f\n    ldr r0, [sp, #0xc]\n    ldr r1, [r0, #0x10]\n    adds.w r0, fp, #8\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am041_addr_0044b5a0\n    bl .\nL_open_cfw_runtime_am041_8e582_0140:\n    cmp r6, #0\n    beq L_open_cfw_runtime_am041_8e582_0150\n    movs r2, #0x3f\n    ldr r1, [r6, #0x10]\n    adds.w r0, fp, #0x68\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am041_addr_0044b5a0\n    bl .\nL_open_cfw_runtime_am041_8e582_0150:\n    cmp.w r8, #0\n    beq L_open_cfw_runtime_am041_8e582_0166\n    movw r2, #0x1ff\n    ldr.w r1, [r8, #0x10]\n    adds.w r0, fp, #0xe8\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am041_addr_0044b5a0\n    bl .\nL_open_cfw_runtime_am041_8e582_0166:\n    cmp r7, #0\n    beq L_open_cfw_runtime_am041_8e582_0176\n    movs r2, #0x3f\n    ldr r1, [r7, #0x10]\n    adds.w r0, fp, #0xa8\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am041_addr_0044b5a0\n    bl .\nL_open_cfw_runtime_am041_8e582_0176:\n    cmp.w sb, #0\n    beq L_open_cfw_runtime_am041_8e582_018a\n    movs r2, #0xf\n    ldr.w r1, [sb, #0x10]\n    adds.w r0, fp, #0x2e8\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am041_addr_0044b5a0\n    bl .\nL_open_cfw_runtime_am041_8e582_018a:\n    cmp.w sl, #0\n    beq L_open_cfw_runtime_am041_8e582_019e\n    movs r2, #0x1f\n    ldr.w r1, [sl, #0x10]\n    adds.w r0, fp, #0x48\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am041_addr_0044b5a0\n    bl .\nL_open_cfw_runtime_am041_8e582_019e:\n    ldr r0, [sp, #8]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am041_addr_004d79fa\n    bl .\nL_open_cfw_runtime_am041_8e582_01a4:\n    add sp, #0x14\n    pop.w {r4, r5, r6, r7, r8, sb, sl, fp, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM041_8E72C_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am041_8e72c(void)
{
    __asm__ volatile(
        "    push {r0, r1, r2, r3, r4, r5, r6, lr}\n    movs r5, r0\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am041_addr_004972a2\n    bl .\n    cmp r0, #0\n    beq.w #0x48e84e\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am041_addr_004bf8ac\n    bl .\n    movs r4, r0\n    movs r1, r4\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am041_8e582\n    bl .\n    movs r5, r4\n    movs r0, #2\n    adds.w r0, r5, #8\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am041_addr_004d67b8\n    bl .\n    movs r6, r0\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am041_addr_0043d0ce\n    bl .\n    lsls r0, r0, #0x1e\n    bpl L_open_cfw_runtime_am041_8e72c_004c\n    movs r0, r6\n    uxtb r0, r0\n    str r0, [sp, #8]\n    ldr r0, [pc, #0x150]\n    str r0, [sp, #4]\n    movs r0, #0x89\n    str r0, [sp]\n    ldr r3, [pc, #0x14c]\n    ldr r2, [pc, #0xe8]\n    ldr r1, [pc, #0xe8]\n    movs r0, #4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am041_addr_0043d574\n    bl .\nL_open_cfw_runtime_am041_8e72c_004c:\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am041_addr_0043d0ce\n    bl .\n    lsls r0, r0, #0x1f\n    bmi L_open_cfw_runtime_am041_8e72c_005c\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am041_addr_0043d0ce\n    bl .\n    lsls r0, r0, #0x1d\n    bpl L_open_cfw_runtime_am041_8e72c_006c\nL_open_cfw_runtime_am041_8e72c_005c:\n    ldr r1, [pc, #0x134]\n    movs r3, r6\n    uxtb r3, r3\n    movs r2, r1\n    movs.w r0, #0x10400000\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am041_addr_0043ce9e\n    bl .\nL_open_cfw_runtime_am041_8e72c_006c:\n    movs r0, r6\n    uxtb r0, r0\n    cmp r0, #2\n    beq L_open_cfw_runtime_am041_8e72c_007a\n    uxtb r6, r6\n    cmp r6, #3\n    bne L_open_cfw_runtime_am041_8e72c_00d4\nL_open_cfw_runtime_am041_8e72c_007a:\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am041_addr_0043d0ce\n    bl .\n    lsls r0, r0, #0x1e\n    bpl L_open_cfw_runtime_am041_8e72c_00a2\n    adds.w r0, r5, #0x48\n    str r0, [sp, #0xc]\n    adds.w r0, r5, #8\n    str r0, [sp, #8]\n    ldr r0, [pc, #0x108]\n    str r0, [sp, #4]\n    movs r0, #0x8e\n    str r0, [sp]\n    ldr r3, [pc, #0xf8]\n    ldr r2, [pc, #0x90]\n    ldr r1, [pc, #0x94]\n    movs r0, #3\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am041_addr_0043d574\n    bl .\nL_open_cfw_runtime_am041_8e72c_00a2:\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am041_addr_0043d0ce\n    bl .\n    lsls r0, r0, #0x1f\n    bmi L_open_cfw_runtime_am041_8e72c_00b2\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am041_addr_0043d0ce\n    bl .\n    lsls r0, r0, #0x1d\n    bpl L_open_cfw_runtime_am041_8e72c_00c8\nL_open_cfw_runtime_am041_8e72c_00b2:\n    ldr r2, [pc, #0xe8]\n    adds.w r0, r5, #0x48\n    str r0, [sp]\n    adds.w r3, r5, #8\n    movs r1, r2\n    movs.w r0, #0xc800000\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am041_addr_0043ce9e\n    bl .\nL_open_cfw_runtime_am041_8e72c_00c8:\n    mov.w r1, #0x2fc\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am041_8e52e\n    bl .\n    b L_open_cfw_runtime_am041_8e72c_0122\nL_open_cfw_runtime_am041_8e72c_00d4:\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am041_addr_0043d0ce\n    bl .\n    lsls r0, r0, #0x1e\n    bpl L_open_cfw_runtime_am041_8e72c_00fc\n    adds.w r0, r5, #0x48\n    str r0, [sp, #0xc]\n    adds.w r0, r5, #8\n    str r0, [sp, #8]\n    ldr r0, [pc, #0xb4]\n    str r0, [sp, #4]\n    movs r0, #0x92\n    str r0, [sp]\n    ldr r3, [pc, #0x9c]\n    ldr r2, [pc, #0x38]\n    ldr r1, [pc, #0x38]\n    movs r0, #3\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am041_addr_0043d574\n    bl .\nL_open_cfw_runtime_am041_8e72c_00fc:\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am041_addr_0043d0ce\n    bl .\n    lsls r0, r0, #0x1f\n    bmi L_open_cfw_runtime_am041_8e72c_010c\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am041_addr_0043d0ce\n    bl .\n    lsls r0, r0, #0x1d\n    bpl L_open_cfw_runtime_am041_8e72c_0122\nL_open_cfw_runtime_am041_8e72c_010c:\n    ldr r1, [pc, #0x94]\n    adds.w r0, r5, #0x48\n    str r0, [sp]\n    adds.w r3, r5, #8\n    movs r2, r1\n    movs.w r0, #0xc800000\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am041_addr_0043ce9e\n    bl .\nL_open_cfw_runtime_am041_8e72c_0122:\n    pop {r0, r1, r2, r3, r4, r5, r6, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM041_8E8D4_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am041_8e8d4(void)
{
    __asm__ volatile(
        "    ldr.w r2, [pc, #0x49c]\n    ubfx r0, r0, #2, #0xa\n    str.w r1, [r2, r0, lsl #2]\n    bx lr\n"
    );
}
#endif

#if defined(OPEN_CFW_AM041_8E8E2_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am041_8e8e2(void)
{
    __asm__ volatile(
        "    ldr.w r1, [pc, #0x490]\n    ubfx r0, r0, #2, #0xa\n    ldr.w r0, [r1, r0, lsl #2]\n    bx lr\n"
    );
}
#endif

#if defined(OPEN_CFW_AM041_8E8F0_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am041_8e8f0(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am041_8e8e2\n    bl .\n    lsls r0, r0, #2\n    ands r0, r0, #0x3c\n    adds r0, #8\n    pop {r1, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM041_8E900_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am041_8e900(void)
{
    __asm__ volatile(
        "    push {r3, r4, r5, r6, r7, lr}\n    ldr.w r0, [pc, #0x474]\n    ldr r4, [r0, #0xc]\n    ldr r1, [r0, #0x10]\n    ldr r5, [r0, #8]\n    ldr r2, [r0]\n    ldr.w r3, [pc, #0x46c]\n    cmp r2, r3\n    bne L_open_cfw_runtime_am041_8e900_001e\n    ldr r0, [r0, #4]\n    cmp.w r0, #0x1000\n    beq L_open_cfw_runtime_am041_8e900_0022\nL_open_cfw_runtime_am041_8e900_001e:\n    movs r0, #0\n    b L_open_cfw_runtime_am041_8e900_009a\nL_open_cfw_runtime_am041_8e900_0022:\n    orrs.w r0, r1, r4\n    orrs r0, r5\n    tst.w r0, #3\n    beq L_open_cfw_runtime_am041_8e900_0032\n    movs r0, #0\n    b L_open_cfw_runtime_am041_8e900_009a\nL_open_cfw_runtime_am041_8e900_0032:\n    subs r0, r5, r4\n    movw r2, #0x1001\n    cmp r0, r2\n    blo L_open_cfw_runtime_am041_8e900_0040\n    movs r0, #0\n    b L_open_cfw_runtime_am041_8e900_009a\nL_open_cfw_runtime_am041_8e900_0040:\n    subs r0, r5, r4\n    subs r1, r1, r4\n    cmp r0, r1\n    bhs L_open_cfw_runtime_am041_8e900_004c\n    movs r0, #0\n    b L_open_cfw_runtime_am041_8e900_009a\nL_open_cfw_runtime_am041_8e900_004c:\n    movs r7, r4\n    movw r6, #0x202\nL_open_cfw_runtime_am041_8e900_0052:\n    cmp r7, r5\n    beq L_open_cfw_runtime_am041_8e900_0098\n    movs r0, r6\n    subs r6, r0, #1\n    cmp r0, #0\n    beq L_open_cfw_runtime_am041_8e900_008c\n    movs r0, r7\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am041_8e8e2\n    bl .\n    and r0, r0, #0xff\n    ands r1, r0, #0xf0\n    cmp r1, #0xa0\n    bne L_open_cfw_runtime_am041_8e900_0090\n    ands r1, r0, #0xf\n    cmp r1, #9\n    bhs L_open_cfw_runtime_am041_8e900_0090\n    lsls r0, r0, #2\n    ands r0, r0, #0x3c\n    adds r7, r0, r7\n    adds r7, #8\n    subs r0, r5, r4\n    subs r1, r7, r4\n    cmp r0, r1\n    bhs L_open_cfw_runtime_am041_8e900_0052\n    b L_open_cfw_runtime_am041_8e900_0094\nL_open_cfw_runtime_am041_8e900_008c:\n    movs r0, #0\n    b L_open_cfw_runtime_am041_8e900_009a\nL_open_cfw_runtime_am041_8e900_0090:\n    movs r0, #0\n    b L_open_cfw_runtime_am041_8e900_009a\nL_open_cfw_runtime_am041_8e900_0094:\n    movs r0, #0\n    b L_open_cfw_runtime_am041_8e900_009a\nL_open_cfw_runtime_am041_8e900_0098:\n    movs r0, #1\nL_open_cfw_runtime_am041_8e900_009a:\n    pop {r1, r4, r5, r6, r7, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM041_8E99C_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am041_8e99c(void)
{
    __asm__ volatile(
        "    ldr.w r0, [pc, #0x3d8]\n    ldr.w r1, [pc, #0x3d8]\n    str r1, [r0]\n    mov.w r1, #0x1000\n    str r1, [r0, #4]\n    movs r1, #0\n    str r1, [r0, #8]\n    movs r1, #0\n    str r1, [r0, #0xc]\n    movs r1, #0\n    str r1, [r0, #0x10]\n    movs r1, #0\n    str r1, [r0, #0x14]\n    bx lr\n"
    );
}
#endif

#if defined(OPEN_CFW_AM041_8E9BE_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am041_8e9be(void)
{
    __asm__ volatile(
        "    push.w {r0, r1, r4, r5, r6, r7, r8, sb, sl, fp, lr}\n    sub sp, #4\n    mov sl, r0\n    movs r6, r2\n    movs r4, r3\n    ldr r7, [sp, #8]\n    lsls r7, r7, #2\n    adds r7, #8\n    ldr.w sb, [sp, #8]\n    ands sb, sb, #0xf\n    orrs sb, sb, #0xa0\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am041_addr_0047dce4\n    bl .\n    str r0, [sp]\n    ldr.w r8, [pc, #0x394]\n    ldr.w r5, [r8, #8]\n    b L_open_cfw_runtime_am041_8e9be_005a\nL_open_cfw_runtime_am041_8e9be_002e:\n    ldr.w fp, [r8, #0xc]\n    mov r0, fp\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am041_8e8f0\n    bl .\n    adds.w fp, r0, fp\n    str.w fp, [r8, #0xc]\n    ldr.w r0, [r8, #0x10]\n    subs.w r0, r0, fp\n    cmp r0, #0\n    bpl L_open_cfw_runtime_am041_8e9be_005a\n    str.w fp, [r8, #0x10]\n    ldr.w r0, [r8, #0x14]\n    adds r0, r0, #1\n    str.w r0, [r8, #0x14]\nL_open_cfw_runtime_am041_8e9be_005a:\n    ldr.w r0, [r8, #0xc]\n    subs r0, r5, r0\n    adds r0, r7, r0\n    movw r1, #0x1001\n    cmp r0, r1\n    bhs L_open_cfw_runtime_am041_8e9be_002e\n    orrs.w sb, sb, sl, lsl #8\n    mov r1, sb\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am041_8e8d4\n    bl .\n    movs r1, r4\n    adds r0, r5, #4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am041_8e8d4\n    bl .\n    movs r4, #0\n    b L_open_cfw_runtime_am041_8e9be_0092\nL_open_cfw_runtime_am041_8e9be_0082:\n    ldr.w r1, [r6, r4, lsl #2]\n    adds.w r0, r5, r4, lsl #2\n    adds r0, #8\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am041_8e8d4\n    bl .\n    adds r4, r4, #1\nL_open_cfw_runtime_am041_8e9be_0092:\n    ldr r0, [sp, #8]\n    cmp r4, r0\n    blo L_open_cfw_runtime_am041_8e9be_0082\n    adds r7, r7, r5\n    str.w r7, [r8, #8]\n    ldr r0, [sp]\n    msr primask, r0\n    pop.w {r0, r1, r2, r4, r5, r6, r7, r8, sb, sl, fp, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM041_8EA66_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am041_8ea66(void)
{
    __asm__ volatile(
        "    push.w {r0, r1, r2, r3, r4, r5, r6, r7, r8, lr}\n    movs r4, r0\n    movs r5, r1\n    movs r6, r2\n    movs r0, #0\n    strb.w r0, [sp]\n    mov r0, sp\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am041_addr_0047dcb4\n    bl .\n    movs r7, r0\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am041_addr_0047dc74\n    bl .\n    mov r8, r0\n    ldrb.w r0, [sp]\n    cmp r0, #0\n    beq L_open_cfw_runtime_am041_8ea66_0048\n    ldr.w r1, [pc, #0x2f0]\n    ldrb r0, [r1]\n    cmp r0, #0\n    bne L_open_cfw_runtime_am041_8ea66_0048\n    movs r0, #1\n    strb r0, [r1]\n    str.w r8, [sp, #4]\n    str r7, [sp, #8]\n    movs r3, r7\n    add r2, sp, #4\n    movs r1, #2\n    ldr.w r0, [pc, #0x2dc]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am041_8e9be\n    bl .\nL_open_cfw_runtime_am041_8ea66_0048:\n    ldrb.w r0, [sp]\n    cmp r0, #0\n    bne L_open_cfw_runtime_am041_8ea66_0052\n    mov r7, r8\nL_open_cfw_runtime_am041_8ea66_0052:\n    movs r3, r7\n    movs r2, r6\n    movs r1, r5\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am041_8e9be\n    bl .\n    pop.w {r0, r1, r2, r3, r4, r5, r6, r7, r8, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM041_8EAC8_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am041_8eac8(void)
{
    __asm__ volatile(
        "    push {r1, r2, r3, r4, r5, lr}\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am041_addr_0047dce4\n    bl .\n    movs r4, r0\n    ldr.w r5, [pc, #0x2b4]\n    ldrb r0, [r5]\n    cmp r0, #0\n    beq L_open_cfw_runtime_am041_8eac8_001a\n    movs r0, r4\n    msr primask, r0\n    b L_open_cfw_runtime_am041_8eac8_0068\nL_open_cfw_runtime_am041_8eac8_001a:\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am041_8e900\n    bl .\n    cmp r0, #0\n    beq L_open_cfw_runtime_am041_8eac8_0042\n    ldr.w r1, [pc, #0x28c]\n    ldr r0, [r1, #0x10]\n    ldr r1, [r1, #8]\n    cmp r0, r1\n    beq L_open_cfw_runtime_am041_8eac8_0038\n    movs r0, #1\n    ldr.w r1, [pc, #0x290]\n    strb r0, [r1]\n    b L_open_cfw_runtime_am041_8eac8_0046\nL_open_cfw_runtime_am041_8eac8_0038:\n    movs r0, #0\n    ldr.w r1, [pc, #0x288]\n    strb r0, [r1]\n    b L_open_cfw_runtime_am041_8eac8_0046\nL_open_cfw_runtime_am041_8eac8_0042:\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am041_8e99c\n    bl .\nL_open_cfw_runtime_am041_8eac8_0046:\n    movs r0, #1\n    strb r0, [r5]\n    movs r0, r4\n    msr primask, r0\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am041_addr_0047dcec\n    bl .\n    str r0, [sp]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am041_addr_0047dd08\n    bl .\n    str r0, [sp, #4]\n    mov r2, sp\n    movs r1, #2\n    ldr.w r0, [pc, #0x264]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am041_8ea66\n    bl .\nL_open_cfw_runtime_am041_8eac8_0068:\n    pop {r0, r1, r2, r4, r5, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM041_8EB32_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am041_8eb32(void)
{
    __asm__ volatile(
        "    push {r4, r5, r6, lr}\n    movs r5, r0\n    movs r6, r1\n    movs r4, r2\n    cmp r6, #9\n    blo L_open_cfw_runtime_am041_8eb32_000e\n    movs r6, #8\nL_open_cfw_runtime_am041_8eb32_000e:\n    cmp r4, #0\n    bne L_open_cfw_runtime_am041_8eb32_0014\n    movs r6, #0\nL_open_cfw_runtime_am041_8eb32_0014:\n    ldr.w r0, [pc, #0x240]\n    ldrb r0, [r0]\n    cmp r0, #0\n    bne L_open_cfw_runtime_am041_8eb32_0022\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am041_8eac8\n    bl .\nL_open_cfw_runtime_am041_8eb32_0022:\n    movs r2, r4\n    movs r1, r6\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am041_8ea66\n    bl .\n    ldr.w r0, [pc, #0x218]\n    ldr r3, [r0, #8]\n    ldr r4, [r0, #0x10]\n    ldr.w r1, [pc, #0x22c]\n    ldrb r0, [r1]\n    ldr.w r2, [pc, #0x228]\n    ldrb r2, [r2]\n    subs r3, r3, r4\n    cmp.w r3, #0xc00\n    blo L_open_cfw_runtime_am041_8eb32_005c\n    uxtb r0, r0\n    cmp r0, #0\n    bne L_open_cfw_runtime_am041_8eb32_005c\n    uxtb r2, r2\n    cmp r2, #0\n    bne L_open_cfw_runtime_am041_8eb32_005c\n    movs r0, #1\n    strb r0, [r1]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am041_addr_0047dd92\n    bl .\nL_open_cfw_runtime_am041_8eb32_005c:\n    pop {r4, r5, r6, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM041_8EB90_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am041_8eb90(void)
{
    __asm__ volatile(
        "    push.w {r3, r4, r5, r6, r7, r8, sb, sl, lr}\n    sub sp, #0x44\n    ldr.w r0, [pc, #0x1f0]\n    ldrb r0, [r0]\n    cmp r0, #0\n    bne L_open_cfw_runtime_am041_8eb90_0014\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am041_8eac8\n    bl .\nL_open_cfw_runtime_am041_8eb90_0014:\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am041_addr_0047dce4\n    bl .\n    ldr.w r6, [pc, #0x1ec]\n    ldrb r1, [r6]\n    cmp r1, #0\n    beq L_open_cfw_runtime_am041_8eb90_002c\n    msr primask, r0\n    mvns r0, #0xf\n    b L_open_cfw_runtime_am041_8eb90_0108\nL_open_cfw_runtime_am041_8eb90_002c:\n    movs r1, #1\n    strb r1, [r6]\n    movs r1, #0\n    ldr.w r2, [pc, #0x1d0]\n    strb r1, [r2]\n    msr primask, r0\n    movs r4, #0\n    ldr.w r5, [pc, #0x1cc]\n    ldrb r0, [r5]\n    cmp r0, #0\n    bne L_open_cfw_runtime_am041_8eb90_0056\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am041_addr_0047dfec\n    bl .\n    movs r4, r0\n    cmp r4, #0\n    bne L_open_cfw_runtime_am041_8eb90_008a\n    movs r0, #1\n    strb r0, [r5]\nL_open_cfw_runtime_am041_8eb90_0056:\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am041_addr_0047dce4\n    bl .\n    ldr r7, [pc, #0x18c]\n    ldr r1, [r7, #0x14]\n    str r1, [sp]\n    movs r1, #0\n    str r1, [r7, #0x14]\n    msr primask, r0\n    ldr r0, [sp]\n    cmp r0, #0\n    beq L_open_cfw_runtime_am041_8eb90_0078\n    mov r2, sp\n    movs r1, #1\n    ldr r0, [pc, #0x19c]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am041_8ea66\n    bl .\nL_open_cfw_runtime_am041_8eb90_0078:\n    movs r5, #0\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am041_addr_0047dce4\n    bl .\n    mov r8, r0\n    ldr.w sb, [r7, #0x10]\n    ldr.w sl, [r7, #8]\n    b L_open_cfw_runtime_am041_8eb90_009c\nL_open_cfw_runtime_am041_8eb90_008a:\n    ldr r0, [pc, #0x188]\n    ldr r1, [r0]\n    adds r1, r1, #1\n    str r1, [r0]\n    movs r0, #0\n    strb r0, [r6]\n    movs r0, r4\n    b L_open_cfw_runtime_am041_8eb90_0108\nL_open_cfw_runtime_am041_8eb90_009a:\n    adds r5, r0, r5\nL_open_cfw_runtime_am041_8eb90_009c:\n    adds.w r0, r5, sb\n    cmp r0, sl\n    beq L_open_cfw_runtime_am041_8eb90_00b2\n    adds.w r0, r5, sb\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am041_8e8f0\n    bl .\n    adds r1, r0, r5\n    cmp r1, #0x41\n    blo L_open_cfw_runtime_am041_8eb90_009a\nL_open_cfw_runtime_am041_8eb90_00b2:\n    movs.w sl, #0\n    b L_open_cfw_runtime_am041_8eb90_00ce\nL_open_cfw_runtime_am041_8eb90_00b8:\n    adds.w r0, sl, sb\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am041_8e8e2\n    bl .\n    add r1, sp, #4\n    mov r2, sl\n    lsrs r2, r2, #2\n    str.w r0, [r1, r2, lsl #2]\n    adds.w sl, sl, #4\nL_open_cfw_runtime_am041_8eb90_00ce:\n    cmp sl, r5\n    blo L_open_cfw_runtime_am041_8eb90_00b8\n    adds.w sb, r5, sb\n    str.w sb, [r7, #0x10]\n    mov r0, r8\n    msr primask, r0\n    cmp r5, #0\n    beq L_open_cfw_runtime_am041_8eb90_00f4\n    movs r1, r5\n    add r0, sp, #4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am041_addr_0047e178\n    bl .\n    movs r4, r0\n    cmp r4, #0\n    beq L_open_cfw_runtime_am041_8eb90_0078\n    b L_open_cfw_runtime_am041_8eb90_00f6\nL_open_cfw_runtime_am041_8eb90_00f4:\n    b L_open_cfw_runtime_am041_8eb90_00fe\nL_open_cfw_runtime_am041_8eb90_00f6:\n    ldr r0, [pc, #0x11c]\n    ldr r1, [r0]\n    adds r1, r1, #1\n    str r1, [r0]\nL_open_cfw_runtime_am041_8eb90_00fe:\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am041_addr_0047e220\n    bl .\n    movs r0, #0\n    strb r0, [r6]\n    movs r0, r4\nL_open_cfw_runtime_am041_8eb90_0108:\n    add sp, #0x48\n    pop.w {r4, r5, r6, r7, r8, sb, sl, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM041_8EC9E_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am041_8ec9e(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am041_8eb90\n    bl .\n    cmp r0, #0\n    bne L_open_cfw_runtime_am041_8ec9e_000e\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am041_addr_0047e1ec\n    bl .\nL_open_cfw_runtime_am041_8ec9e_000e:\n    pop {r1, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM041_8ECAE_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am041_8ecae(void)
{
    __asm__ volatile(
        "    push {r4, r5}\n    movs r3, r0\n    movs.w r0, #-1\nL_open_cfw_runtime_am041_8ecae_0008:\n    movs r2, r1\n    subs r1, r2, #1\n    cmp r2, #0\n    beq L_open_cfw_runtime_am041_8ecae_002e\n    ldrb r2, [r3]\n    eors r0, r2\n    adds r3, r3, #1\n    movs r4, #0\nL_open_cfw_runtime_am041_8ecae_0018:\n    cmp r4, #8\n    bge L_open_cfw_runtime_am041_8ecae_0008\n    ands r5, r0, #1\n    rsbs r5, r5, #0\n    ldr r2, [pc, #0xd4]\n    ands r5, r2\n    eors.w r0, r5, r0, lsr #1\n    adds r4, r4, #1\n    b L_open_cfw_runtime_am041_8ecae_0018\nL_open_cfw_runtime_am041_8ecae_002e:\n    mvns r0, r0\n    pop {r4, r5}\n    bx lr\n"
    );
}
#endif

#if defined(OPEN_CFW_AM041_8ECE2_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am041_8ece2(void)
{
    __asm__ volatile(
        "    strb r1, [r0]\n    uxth r1, r1\n    lsrs r1, r1, #8\n    strb r1, [r0, #1]\n    bx lr\n"
    );
}
#endif

#if defined(OPEN_CFW_AM041_8ECEC_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am041_8ecec(void)
{
    __asm__ volatile(
        "    strb r1, [r0]\n    movs r2, r1\n    lsrs r2, r2, #8\n    strb r2, [r0, #1]\n    movs r2, r1\n    lsrs r2, r2, #0x10\n    strb r2, [r0, #2]\n    lsrs r1, r1, #0x18\n    strb r1, [r0, #3]\n    bx lr\n"
    );
}
#endif

#if defined(OPEN_CFW_AM041_8ED00_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am041_8ed00(void)
{
    __asm__ volatile(
        "    push {r4, r5, r6, lr}\n    movs r4, r0\n    movs r5, r1\n    movs r6, r2\n    movs r0, #0x54\n    strb r0, [r4]\n    movs r0, #0x50\n    strb r0, [r4, #1]\n    movs r0, #0x46\n    strb r0, [r4, #2]\n    movs r0, #0x31\n    strb r0, [r4, #3]\n    movs r1, #3\n    adds r0, r4, #4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am041_8ece2\n    bl .\n    movs r1, #0x20\n    adds r0, r4, #6\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am041_8ece2\n    bl .\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am041_addr_0047dd08\n    bl .\n    movs r1, r0\n    adds.w r0, r4, #8\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am041_8ecec\n    bl .\n    mov.w r1, #0x200\n    adds.w r0, r4, #0xc\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am041_8ecec\n    bl .\n    movs r1, r5\n    adds.w r0, r4, #0x10\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am041_8ecec\n    bl .\n    movs r1, r6\n    adds.w r0, r4, #0x14\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am041_8ecec\n    bl .\n    ldr r1, [pc, #0x54]\n    adds.w r0, r4, #0x18\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am041_8ecec\n    bl .\n    movs r1, #0x1c\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am041_8ecae\n    bl .\n    movs r1, r0\n    adds.w r0, r4, #0x1c\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am041_8ecec\n    bl .\n    pop {r4, r5, r6, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM041_8EE28_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am041_8ee28(void)
{
    __asm__ volatile(
        "    bx lr\n"
    );
}
#endif

#if defined(OPEN_CFW_AM041_8EE2A_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am041_8ee2a(void)
{
    __asm__ volatile(
        "    push {r4, lr}\n    ldr.w r4, [pc, #0x4f4]\n    movs r2, #0\n    movs r1, #4\n    movs r0, #0x96\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am041_addr_00449a32\n    bl .\n    str r0, [r4, #0xc]\n    ldr r0, [r4, #0xc]\n    cmp r0, #0\n    bne L_open_cfw_runtime_am041_8ee2a_0026\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am041_addr_005fa0a4\n    bl .\n    movs r0, #0\n    movs.w r1, #-1\n    str r0, [r1]\nL_open_cfw_runtime_am041_8ee2a_0024:\n    b L_open_cfw_runtime_am041_8ee2a_0024\nL_open_cfw_runtime_am041_8ee2a_0026:\n    pop {r4, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM041_8EE52_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am041_8ee52(void)
{
    __asm__ volatile(
        "    bx lr\n"
    );
}
#endif

#if defined(OPEN_CFW_AM041_8EE54_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am041_8ee54(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    movs r0, #7\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am041_addr_004c9b86\n    bl .\n    pop {r0, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM041_8EE5E_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am041_8ee5e(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    movs r0, #7\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am041_addr_004c9be2\n    bl .\n    pop {r0, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM041_8EEAC_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am041_8eeac(void)
{
    __asm__ volatile(
        "    push {r5, r6, r7, lr}\n    movs r0, #0\n    str r0, [sp, #8]\n    b L_open_cfw_runtime_am041_8eeac_0008\nL_open_cfw_runtime_am041_8eeac_0008:\n    movs r3, #0\n    movs r2, #0\n    add r1, sp, #8\n    ldr.w r0, [pc, #0x468]\n    ldr r0, [r0, #0xc]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am041_addr_00449b3c\n    bl .\n    cmp r0, #0\n    bne L_open_cfw_runtime_am041_8eeac_00fe\n    ldr r0, [sp, #8]\n    cmp r0, #0\n    beq L_open_cfw_runtime_am041_8eeac_0008\n    ldr r0, [sp, #8]\n    ldr r0, [r0]\n    subs r0, #0x80\n    beq L_open_cfw_runtime_am041_8eeac_0048\n    subs r0, #0x40\n    cmp r0, #3\n    bls L_open_cfw_runtime_am041_8eeac_0058\n    subs r0, r0, #4\n    cmp r0, #3\n    bls L_open_cfw_runtime_am041_8eeac_0070\n    mov.w r1, #0x13c\n    subs r0, r0, r1\n    beq L_open_cfw_runtime_am041_8eeac_008e\n    mov.w r1, #0x200\n    subs r0, r0, r1\n    beq L_open_cfw_runtime_am041_8eeac_0088\n    b L_open_cfw_runtime_am041_8eeac_00f2\nL_open_cfw_runtime_am041_8eeac_0048:\n    ldr r0, [sp, #8]\n    ldr r1, [r0, #4]\n    uxth r1, r1\n    ldr r0, [sp, #8]\n    adds r0, #8\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am041_addr_004d83d8\n    bl .\n    b L_open_cfw_runtime_am041_8eeac_00f2\nL_open_cfw_runtime_am041_8eeac_0058:\n    ldr r0, [sp, #8]\n    ldr r2, [r0, #4]\n    uxth r2, r2\n    ldr r0, [sp, #8]\n    adds.w r1, r0, #8\n    ldr r0, [sp, #8]\n    ldr r0, [r0]\n    uxtb r0, r0\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am041_addr_00448670\n    bl .\n    b L_open_cfw_runtime_am041_8eeac_00f2\nL_open_cfw_runtime_am041_8eeac_0070:\n    ldr r0, [sp, #8]\n    ldr r2, [r0, #4]\n    uxth r2, r2\n    ldr r0, [sp, #8]\n    adds.w r1, r0, #8\n    ldr r0, [sp, #8]\n    ldr r0, [r0]\n    uxtb r0, r0\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am041_addr_00458b60\n    bl .\n    b L_open_cfw_runtime_am041_8eeac_00f2\nL_open_cfw_runtime_am041_8eeac_0088:\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am041_addr_00458c5e\n    bl .\n    b L_open_cfw_runtime_am041_8eeac_00f2\nL_open_cfw_runtime_am041_8eeac_008e:\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am041_addr_0043d0ce\n    bl .\n    lsls r0, r0, #0x1e\n    bpl L_open_cfw_runtime_am041_8eeac_00b2\n    ldr.w r0, [pc, #0x400]\n    str r0, [sp, #4]\n    movs r0, #0xe9\n    str r0, [sp]\n    ldr.w r3, [pc, #0x3f8]\n    ldr.w r2, [pc, #0x3d4]\n    ldr.w r1, [pc, #0x3d4]\n    movs r0, #4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am041_addr_0043d574\n    bl .\nL_open_cfw_runtime_am041_8eeac_00b2:\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am041_addr_0043d0ce\n    bl .\n    lsls r0, r0, #0x1f\n    bmi L_open_cfw_runtime_am041_8eeac_00c2\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am041_addr_0043d0ce\n    bl .\n    lsls r0, r0, #0x1d\n    bpl L_open_cfw_runtime_am041_8eeac_00d0\nL_open_cfw_runtime_am041_8eeac_00c2:\n    ldr.w r2, [pc, #0x3dc]\n    movs r1, r2\n    movs.w r0, #0x10000000\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am041_addr_0043ce9e\n    bl .\nL_open_cfw_runtime_am041_8eeac_00d0:\n    ldr r0, [sp, #8]\n    ldr r3, [r0, #4]\n    uxth r3, r3\n    ldr r0, [sp, #8]\n    adds.w r2, r0, #8\n    movs r1, #0x10\n    adr r0, #0x19c\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am041_addr_0043dacc\n    bl .\n    ldr r0, [sp, #8]\n    adds.w r1, r0, #8\n    movs r0, #3\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am041_addr_004d9010\n    bl .\n    b L_open_cfw_runtime_am041_8eeac_00f2\nL_open_cfw_runtime_am041_8eeac_00f2:\n    ldr r0, [sp, #8]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am041_addr_00474d16\n    bl .\n    movs r0, #0\n    str r0, [sp, #8]\n    b L_open_cfw_runtime_am041_8eeac_0008\nL_open_cfw_runtime_am041_8eeac_00fe:\n    pop {r0, r1, r2, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM041_8EFAC_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am041_8efac(void)
{
    __asm__ volatile(
        "    push {r4, lr}\n    movs r4, r0\n    lsls r0, r4, #9\n    bpl L_open_cfw_runtime_am041_8efac_000c\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am041_8eeac\n    bl .\nL_open_cfw_runtime_am041_8efac_000c:\n    lsls r0, r4, #8\n    bpl L_open_cfw_runtime_am041_8efac_0014\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am041_8efc2\n    bl .\nL_open_cfw_runtime_am041_8efac_0014:\n    pop {r4, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM041_8EFC2_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am041_8efc2(void)
{
    __asm__ volatile(
        "    push {r5, r6, r7, lr}\n    movs r0, #7\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am041_addr_004c9c3c\n    bl .\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am041_addr_0043d0ce\n    bl .\n    lsls r0, r0, #0x1e\n    bpl L_open_cfw_runtime_am041_8efc2_002e\n    ldr.w r0, [pc, #0x37c]\n    str r0, [sp, #4]\n    mov.w r0, #0x10a\n    str r0, [sp]\n    ldr.w r3, [pc, #0x374]\n    ldr.w r2, [pc, #0x344]\n    ldr.w r1, [pc, #0x344]\n    movs r0, #4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am041_addr_0043d574\n    bl .\nL_open_cfw_runtime_am041_8efc2_002e:\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am041_addr_0043d0ce\n    bl .\n    lsls r0, r0, #0x1f\n    bmi L_open_cfw_runtime_am041_8efc2_003e\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am041_addr_0043d0ce\n    bl .\n    lsls r0, r0, #0x1d\n    bpl L_open_cfw_runtime_am041_8efc2_004c\nL_open_cfw_runtime_am041_8efc2_003e:\n    ldr.w r1, [pc, #0x354]\n    movs r2, r1\n    movs.w r0, #0x10000000\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am041_addr_0043ce9e\n    bl .\nL_open_cfw_runtime_am041_8efc2_004c:\n    movs.w r0, #-1\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am041_addr_00449376\n    bl .\n    b L_open_cfw_runtime_am041_8efc2_004c\n"
    );
}
#endif

#if defined(OPEN_CFW_AM041_8F018_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am041_8f018(void)
{
    __asm__ volatile(
        "    push {r3, r4, r5, r6, lr}\n    sub sp, #0x14\n    movs r4, #0\n    movs r0, #0\n    str r0, [sp, #0x10]\n    ldr r5, [pc, #0x300]\n    ldr r0, [r5, #0xc]\n    cmp r0, #0\n    bne L_open_cfw_runtime_am041_8f018_0054\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am041_addr_0043d0ce\n    bl .\n    lsls r0, r0, #0x1e\n    bpl L_open_cfw_runtime_am041_8f018_0034\n    ldr.w r0, [pc, #0x328]\n    str r0, [sp, #4]\n    mov.w r0, #0x11c\n    str r0, [sp]\n    ldr.w r3, [pc, #0x320]\n    ldr r2, [pc, #0x2e4]\n    ldr r1, [pc, #0x2e4]\n    movs r0, #2\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am041_addr_0043d574\n    bl .\nL_open_cfw_runtime_am041_8f018_0034:\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am041_addr_0043d0ce\n    bl .\n    lsls r0, r0, #0x1f\n    bmi L_open_cfw_runtime_am041_8f018_0044\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am041_addr_0043d0ce\n    bl .\n    lsls r0, r0, #0x1d\n    bpl L_open_cfw_runtime_am041_8f018_0050\nL_open_cfw_runtime_am041_8f018_0044:\n    ldr r1, [pc, #0x304]\n    movs r2, r1\n    movs.w r0, #0x8000000\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am041_addr_0043ce9e\n    bl .\nL_open_cfw_runtime_am041_8f018_0050:\n    movs r0, #0\n    b L_open_cfw_runtime_am041_8f018_010a\nL_open_cfw_runtime_am041_8f018_0054:\n    ldr r0, [r5, #0xc]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am041_addr_00449bc8\n    bl .\n    movs r6, r0\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am041_addr_0043d0ce\n    bl .\n    lsls r0, r0, #0x1e\n    bpl L_open_cfw_runtime_am041_8f018_007c\n    str r6, [sp, #8]\n    ldr r0, [pc, #0x2e8]\n    str r0, [sp, #4]\n    movw r0, #0x121\n    str r0, [sp]\n    ldr r3, [pc, #0x2d4]\n    ldr r2, [pc, #0x29c]\n    ldr r1, [pc, #0x29c]\n    movs r0, #4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am041_addr_0043d574\n    bl .\nL_open_cfw_runtime_am041_8f018_007c:\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am041_addr_0043d0ce\n    bl .\n    lsls r0, r0, #0x1f\n    bmi L_open_cfw_runtime_am041_8f018_008c\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am041_addr_0043d0ce\n    bl .\n    lsls r0, r0, #0x1d\n    bpl L_open_cfw_runtime_am041_8f018_009a\nL_open_cfw_runtime_am041_8f018_008c:\n    ldr r2, [pc, #0x2c4]\n    movs r3, r6\n    movs r1, r2\n    movs.w r0, #0x10400000\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am041_addr_0043ce9e\n    bl .\nL_open_cfw_runtime_am041_8f018_009a:\n    b L_open_cfw_runtime_am041_8f018_00a8\nL_open_cfw_runtime_am041_8f018_009c:\n    ldr r0, [sp, #0x10]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am041_addr_00474d16\n    bl .\n    movs r0, #0\n    str r0, [sp, #0x10]\n    adds r4, r4, #1\nL_open_cfw_runtime_am041_8f018_00a8:\n    movs r3, #0\n    movs r2, #0\n    add r1, sp, #0x10\n    ldr r0, [r5, #0xc]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am041_addr_00449b3c\n    bl .\n    cmp r0, #0\n    bne L_open_cfw_runtime_am041_8f018_00be\n    ldr r0, [sp, #0x10]\n    cmp r0, #0\n    bne L_open_cfw_runtime_am041_8f018_009c\nL_open_cfw_runtime_am041_8f018_00be:\n    ldr r0, [r5, #0xc]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am041_addr_00449bc8\n    bl .\n    movs r5, r0\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am041_addr_0043d0ce\n    bl .\n    lsls r0, r0, #0x1e\n    bpl L_open_cfw_runtime_am041_8f018_00e8\n    str r5, [sp, #0xc]\n    str r4, [sp, #8]\n    ldr r0, [pc, #0x284]\n    str r0, [sp, #4]\n    mov.w r0, #0x130\n    str r0, [sp]\n    ldr r3, [pc, #0x268]\n    ldr r2, [pc, #0x230]\n    ldr r1, [pc, #0x230]\n    movs r0, #4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am041_addr_0043d574\n    bl .\nL_open_cfw_runtime_am041_8f018_00e8:\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am041_addr_0043d0ce\n    bl .\n    lsls r0, r0, #0x1f\n    bmi L_open_cfw_runtime_am041_8f018_00f8\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am041_addr_0043d0ce\n    bl .\n    lsls r0, r0, #0x1d\n    bpl L_open_cfw_runtime_am041_8f018_0108\nL_open_cfw_runtime_am041_8f018_00f8:\n    ldr r1, [pc, #0x260]\n    str r5, [sp]\n    movs r3, r4\n    movs r2, r1\n    movs.w r0, #0x10800000\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am041_addr_0043ce9e\n    bl .\nL_open_cfw_runtime_am041_8f018_0108:\n    movs r0, r4\nL_open_cfw_runtime_am041_8f018_010a:\n    add sp, #0x18\n    pop {r4, r5, r6, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM041_8F12C_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am041_8f12c(void)
{
    __asm__ volatile(
        "    push.w {r4, r5, r6, r7, r8, sb, lr}\n    sub sp, #0x14\n    mov r8, r0\n    movs r4, r1\n    movs r6, r2\n    cmp r4, #0\n    bne L_open_cfw_runtime_am041_8f12c_0050\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am041_addr_0043d0ce\n    bl .\n    lsls r0, r0, #0x1e\n    bpl L_open_cfw_runtime_am041_8f12c_002e\n    ldr r0, [pc, #0x230]\n    str r0, [sp, #4]\n    mov.w r0, #0x13e\n    str r0, [sp]\n    ldr r3, [pc, #0x22c]\n    ldr r2, [pc, #0x1d4]\n    ldr r1, [pc, #0x1d8]\n    movs r0, #1\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am041_addr_0043d574\n    bl .\nL_open_cfw_runtime_am041_8f12c_002e:\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am041_addr_0043d0ce\n    bl .\n    lsls r0, r0, #0x1f\n    bmi L_open_cfw_runtime_am041_8f12c_003e\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am041_addr_0043d0ce\n    bl .\n    lsls r0, r0, #0x1d\n    bpl L_open_cfw_runtime_am041_8f12c_004a\nL_open_cfw_runtime_am041_8f12c_003e:\n    ldr r1, [pc, #0x214]\n    movs r2, r1\n    movs.w r0, #0x4000000\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am041_addr_0043ce9e\n    bl .\nL_open_cfw_runtime_am041_8f12c_004a:\n    movs.w r0, #-1\n    b L_open_cfw_runtime_am041_8f12c_01f2\nL_open_cfw_runtime_am041_8f12c_0050:\n    ldr r5, [pc, #0x1a4]\n    ldr r0, [r5, #0xc]\n    cmp r0, #0\n    bne L_open_cfw_runtime_am041_8f12c_0098\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am041_addr_0043d0ce\n    bl .\n    lsls r0, r0, #0x1e\n    bpl L_open_cfw_runtime_am041_8f12c_0076\n    ldr r0, [pc, #0x1f4]\n    str r0, [sp, #4]\n    movw r0, #0x143\n    str r0, [sp]\n    ldr r3, [pc, #0x1e4]\n    ldr r2, [pc, #0x18c]\n    ldr r1, [pc, #0x190]\n    movs r0, #1\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am041_addr_0043d574\n    bl .\nL_open_cfw_runtime_am041_8f12c_0076:\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am041_addr_0043d0ce\n    bl .\n    lsls r0, r0, #0x1f\n    bmi L_open_cfw_runtime_am041_8f12c_0086\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am041_addr_0043d0ce\n    bl .\n    lsls r0, r0, #0x1d\n    bpl L_open_cfw_runtime_am041_8f12c_0092\nL_open_cfw_runtime_am041_8f12c_0086:\n    ldr r1, [pc, #0x1d4]\n    movs r2, r1\n    movs.w r0, #0x4000000\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am041_addr_0043ce9e\n    bl .\nL_open_cfw_runtime_am041_8f12c_0092:\n    movs.w r0, #-1\n    b L_open_cfw_runtime_am041_8f12c_01f2\nL_open_cfw_runtime_am041_8f12c_0098:\n    movs r0, #0\n    str r0, [sp, #0x10]\n    movs r0, r6\n    uxth r0, r0\n    adds r0, #0xb\n    lsrs r0, r0, #2\n    lsls r0, r0, #2\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am041_addr_00474cd2\n    bl .\n    str r0, [sp, #0x10]\n    ldr r0, [sp, #0x10]\n    cmp r0, #0\n    bne L_open_cfw_runtime_am041_8f12c_00fc\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am041_addr_0043d0ce\n    bl .\n    lsls r0, r0, #0x1e\n    bpl L_open_cfw_runtime_am041_8f12c_00d6\n    movs r0, r6\n    uxth r0, r0\n    str r0, [sp, #8]\n    ldr r0, [pc, #0x19c]\n    str r0, [sp, #4]\n    movw r0, #0x14d\n    str r0, [sp]\n    ldr r3, [pc, #0x184]\n    ldr r2, [pc, #0x12c]\n    ldr r1, [pc, #0x130]\n    movs r0, #1\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am041_addr_0043d574\n    bl .\nL_open_cfw_runtime_am041_8f12c_00d6:\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am041_addr_0043d0ce\n    bl .\n    lsls r0, r0, #0x1f\n    bmi L_open_cfw_runtime_am041_8f12c_00e6\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am041_addr_0043d0ce\n    bl .\n    lsls r0, r0, #0x1d\n    bpl L_open_cfw_runtime_am041_8f12c_00f6\nL_open_cfw_runtime_am041_8f12c_00e6:\n    ldr r1, [pc, #0x17c]\n    uxth r6, r6\n    movs r3, r6\n    movs r2, r1\n    movs.w r0, #0x4400000\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am041_addr_0043ce9e\n    bl .\nL_open_cfw_runtime_am041_8f12c_00f6:\n    movs.w r0, #-1\n    b L_open_cfw_runtime_am041_8f12c_01f2\nL_open_cfw_runtime_am041_8f12c_00fc:\n    movs r7, #0\n    movs r0, #0\n    movs r1, r6\n    uxth r1, r1\n    movs r2, #0\n    ldr r0, [sp, #0x10]\n    adds.w sb, r0, #8\n    mov r0, sb\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am041_addr_0043c0e4\n    bl .\n    ldr r0, [sp, #0x10]\n    str.w r8, [r0]\n    movs r0, r6\n    uxth r0, r0\n    ldr r1, [sp, #0x10]\n    str r0, [r1, #4]\n    uxth r6, r6\n    ldr r0, [sp, #0x10]\n    adds.w r8, r0, #8\n    movs r2, r6\n    movs r1, r4\n    mov r0, r8\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am041_addr_00439be4\n    bl .\n    ldr r0, [r5, #0xc]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am041_addr_00449bc8\n    bl .\n    movs r4, r0\n    ldr r0, [r5, #0xc]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am041_addr_00449bbc\n    bl .\n    movs r6, r0\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am041_addr_0043d0ce\n    bl .\n    lsls r0, r0, #0x1e\n    bpl L_open_cfw_runtime_am041_8f12c_0164\n    str r6, [sp, #0xc]\n    str r4, [sp, #8]\n    ldr r0, [pc, #0x118]\n    str r0, [sp, #4]\n    movw r0, #0x15d\n    str r0, [sp]\n    ldr r3, [pc, #0xf4]\n    ldr r2, [pc, #0xa0]\n    ldr r1, [pc, #0xa0]\n    movs r0, #4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am041_addr_0043d574\n    bl .\nL_open_cfw_runtime_am041_8f12c_0164:\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am041_addr_0043d0ce\n    bl .\n    lsls r0, r0, #0x1f\n    bmi L_open_cfw_runtime_am041_8f12c_0174\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am041_addr_0043d0ce\n    bl .\n    lsls r0, r0, #0x1d\n    bpl L_open_cfw_runtime_am041_8f12c_0184\nL_open_cfw_runtime_am041_8f12c_0174:\n    ldr r1, [pc, #0xf4]\n    str r6, [sp]\n    movs r3, r4\n    movs r2, r1\n    movs.w r0, #0x10800000\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am041_addr_0043ce9e\n    bl .\nL_open_cfw_runtime_am041_8f12c_0184:\n    mov.w r3, #0x1f4\n    movs r2, #0\n    add r1, sp, #0x10\n    ldr r0, [r5, #0xc]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am041_addr_00449abe\n    bl .\n    movs r4, r0\n    cmp r4, #0\n    beq L_open_cfw_runtime_am041_8f12c_01e6\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am041_addr_0043d0ce\n    bl .\n    lsls r0, r0, #0x1e\n    bpl L_open_cfw_runtime_am041_8f12c_01b8\n    str r4, [sp, #8]\n    ldr r0, [pc, #0xcc]\n    str r0, [sp, #4]\n    mov.w r0, #0x160\n    str r0, [sp]\n    ldr r3, [pc, #0xa0]\n    ldr r2, [pc, #0x4c]\n    ldr r1, [pc, #0x4c]\n    movs r0, #1\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am041_addr_0043d574\n    bl .\nL_open_cfw_runtime_am041_8f12c_01b8:\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am041_addr_0043d0ce\n    bl .\n    lsls r0, r0, #0x1f\n    bmi L_open_cfw_runtime_am041_8f12c_01c8\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am041_addr_0043d0ce\n    bl .\n    lsls r0, r0, #0x1d\n    bpl L_open_cfw_runtime_am041_8f12c_01d6\nL_open_cfw_runtime_am041_8f12c_01c8:\n    ldr r1, [pc, #0xa8]\n    movs r3, r4\n    movs r2, r1\n    movs.w r0, #0x4400000\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am041_addr_0043ce9e\n    bl .\nL_open_cfw_runtime_am041_8f12c_01d6:\n    ldr r0, [sp, #0x10]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am041_addr_00474d16\n    bl .\n    movs r0, #0\n    str r0, [sp, #0x10]\n    movs.w r7, #-1\n    b L_open_cfw_runtime_am041_8f12c_01f0\nL_open_cfw_runtime_am041_8f12c_01e6:\n    movs.w r1, #0x400000\n    ldr r0, [r5, #8]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am041_addr_00449238\n    bl .\nL_open_cfw_runtime_am041_8f12c_01f0:\n    movs r0, r7\nL_open_cfw_runtime_am041_8f12c_01f2:\n    add sp, #0x14\n    pop.w {r4, r5, r6, r7, r8, sb, pc}\n"
    );
}
#endif
