/*
 * SPDX-License-Identifier: MIT
 *
 * Source-owned exact helpers from the AM-017 retained island.
 */

#if defined(OPEN_CFW_AM017_50B80_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am017_50b80(void)
{
    __asm__ volatile(
        "    movs r1, r0\n    ldr r2, [r1, #8]\n    ldr r0, [r1]\n    subs r2, r2, r0\n    adds r2, r2, #1\n    ldr r0, [r1, #0xc]\n    ldr r1, [r1, #4]\n    subs r0, r0, r1\n    adds r0, r0, #1\n    mul r0, r0, r2\n    bx lr\n"
    );
}
#endif

#if defined(OPEN_CFW_AM017_50B98_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am017_50b98(void)
{
    __asm__ volatile(
        "    ldr r3, [r0]\n    subs r3, r3, r1\n    str r3, [r0]\n    ldr r3, [r0, #8]\n    adds r1, r1, r3\n    str r1, [r0, #8]\n    ldr r1, [r0, #4]\n    subs r1, r1, r2\n    str r1, [r0, #4]\n    ldr r1, [r0, #0xc]\n    adds r2, r2, r1\n    str r2, [r0, #0xc]\n    bx lr\n"
    );
}
#endif

#if defined(OPEN_CFW_AM017_50BB2_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am017_50bb2(void)
{
    __asm__ volatile(
        "    ldr r3, [r0]\n    adds r3, r1, r3\n    str r3, [r0]\n    ldr r3, [r0, #8]\n    adds r1, r1, r3\n    str r1, [r0, #8]\n    ldr r1, [r0, #4]\n    adds r1, r2, r1\n    str r1, [r0, #4]\n    ldr r1, [r0, #0xc]\n    adds r2, r2, r1\n    str r2, [r0, #0xc]\n    bx lr\n"
    );
}
#endif

#if defined(OPEN_CFW_AM017_50BCC_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am017_50bcc(void)
{
    __asm__ volatile(
        "    push {r4}\n    ldr r3, [r2]\n    ldr r4, [r1]\n    cmp r3, r4\n    bge L_open_cfw_runtime_am017_50bcc_000e\n    ldr r3, [r1]\n    b L_open_cfw_runtime_am017_50bcc_0010\nL_open_cfw_runtime_am017_50bcc_000e:\n    ldr r3, [r2]\nL_open_cfw_runtime_am017_50bcc_0010:\n    str r3, [r0]\n    ldr r3, [r2, #4]\n    ldr r4, [r1, #4]\n    cmp r3, r4\n    bge L_open_cfw_runtime_am017_50bcc_001e\n    ldr r3, [r1, #4]\n    b L_open_cfw_runtime_am017_50bcc_0020\nL_open_cfw_runtime_am017_50bcc_001e:\n    ldr r3, [r2, #4]\nL_open_cfw_runtime_am017_50bcc_0020:\n    str r3, [r0, #4]\n    ldr r3, [r1, #8]\n    ldr r4, [r2, #8]\n    cmp r3, r4\n    bge L_open_cfw_runtime_am017_50bcc_002e\n    ldr r3, [r1, #8]\n    b L_open_cfw_runtime_am017_50bcc_0030\nL_open_cfw_runtime_am017_50bcc_002e:\n    ldr r3, [r2, #8]\nL_open_cfw_runtime_am017_50bcc_0030:\n    str r3, [r0, #8]\n    ldr r3, [r1, #0xc]\n    ldr r4, [r2, #0xc]\n    cmp r3, r4\n    bge L_open_cfw_runtime_am017_50bcc_003e\n    ldr r1, [r1, #0xc]\n    b L_open_cfw_runtime_am017_50bcc_0040\nL_open_cfw_runtime_am017_50bcc_003e:\n    ldr r1, [r2, #0xc]\nL_open_cfw_runtime_am017_50bcc_0040:\n    str r1, [r0, #0xc]\n    movs r1, #1\n    ldr r2, [r0, #8]\n    ldr r3, [r0]\n    cmp r2, r3\n    blt L_open_cfw_runtime_am017_50bcc_0054\n    ldr r2, [r0, #0xc]\n    ldr r0, [r0, #4]\n    cmp r2, r0\n    bge L_open_cfw_runtime_am017_50bcc_0056\nL_open_cfw_runtime_am017_50bcc_0054:\n    movs r1, #0\nL_open_cfw_runtime_am017_50bcc_0056:\n    movs r0, r1\n    uxtb r0, r0\n    pop {r4}\n    bx lr\n"
    );
}
#endif

#if defined(OPEN_CFW_AM017_50C2A_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am017_50c2a(void)
{
    __asm__ volatile(
        "    push.w {r0, r1, r2, r3, r4, r5, r6, r7, r8, sb, sl, lr}\n    movs r4, r0\n    movs r5, r1\n    movs r6, r2\n    movs r1, r6\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am017_50f00\n    bl .\n    cmp r0, #0\n    bne L_open_cfw_runtime_am017_50c2a_001c\n    movs.w r0, #-1\n    b L_open_cfw_runtime_am017_50c2a_015e\nL_open_cfw_runtime_am017_50c2a_001c:\n    movs r2, #0\n    movs r1, r6\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am017_50f28\n    bl .\n    cmp r0, #0\n    beq L_open_cfw_runtime_am017_50c2a_002e\n    movs r0, #0\n    b L_open_cfw_runtime_am017_50c2a_015e\nL_open_cfw_runtime_am017_50c2a_002e:\n    movs.w r8, #0\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am017_51598\n    bl .\n    movs r7, r0\n    subs r7, r7, #1\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am017_515a4\n    bl .\n    mov sb, r0\n    subs.w sb, sb, #1\n    ldr r1, [r6, #4]\n    ldr r0, [r5, #4]\n    subs r1, r1, r0\n    cmp r1, #1\n    blt L_open_cfw_runtime_am017_50c2a_007a\n    ldr r0, [r5]\n    str r0, [sp]\n    ldr r0, [r5, #4]\n    str r0, [sp, #4]\n    ldr r0, [r5, #8]\n    str r0, [sp, #8]\n    ldr r0, [r5, #4]\n    adds r1, r1, r0\n    subs r1, r1, #1\n    str r1, [sp, #0xc]\n    mov r0, r8\n    sxtb r0, r0\n    lsls r0, r0, #4\n    add r0, r4\n    mov r1, sp\n    movs r2, #0x10\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am017_addr_00439c04\n    bl .\n    adds.w r8, r8, #1\nL_open_cfw_runtime_am017_50c2a_007a:\n    ldr r0, [r6, #0xc]\n    subs.w sb, sb, r0\n    ldr r0, [r5, #4]\n    adds.w sb, r0, sb\n    cmp.w sb, #1\n    blt L_open_cfw_runtime_am017_50c2a_00c0\n    ldr r0, [r6, #0xc]\n    ldr r1, [r5, #0xc]\n    cmp r0, r1\n    bge L_open_cfw_runtime_am017_50c2a_00c0\n    ldr r0, [r5]\n    str r0, [sp]\n    ldr r0, [r6, #0xc]\n    adds r0, r0, #1\n    str r0, [sp, #4]\n    ldr r0, [r5, #8]\n    str r0, [sp, #8]\n    ldr r0, [r6, #0xc]\n    adds.w sb, sb, r0\n    str.w sb, [sp, #0xc]\n    mov r0, r8\n    sxtb r0, r0\n    lsls r0, r0, #4\n    add r0, r4\n    mov r1, sp\n    movs r2, #0x10\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am017_addr_00439c04\n    bl .\n    adds.w r8, r8, #1\nL_open_cfw_runtime_am017_50c2a_00c0:\n    ldr r0, [r5, #4]\n    ldr r1, [r6, #4]\n    cmp r0, r1\n    bge L_open_cfw_runtime_am017_50c2a_00ce\n    ldr.w sb, [r6, #4]\n    b L_open_cfw_runtime_am017_50c2a_00d2\nL_open_cfw_runtime_am017_50c2a_00ce:\n    ldr.w sb, [r5, #4]\nL_open_cfw_runtime_am017_50c2a_00d2:\n    ldr r0, [r6, #0xc]\n    ldr r1, [r5, #0xc]\n    cmp r0, r1\n    bge L_open_cfw_runtime_am017_50c2a_00e0\n    ldr.w sl, [r6, #0xc]\n    b L_open_cfw_runtime_am017_50c2a_00e4\nL_open_cfw_runtime_am017_50c2a_00e0:\n    ldr.w sl, [r5, #0xc]\nL_open_cfw_runtime_am017_50c2a_00e4:\n    subs.w sl, sl, sb\n    ldr r1, [r6]\n    ldr r0, [r5]\n    subs r1, r1, r0\n    cmp r1, #1\n    blt L_open_cfw_runtime_am017_50c2a_0122\n    cmp.w sl, #1\n    blt L_open_cfw_runtime_am017_50c2a_0122\n    ldr r0, [r5]\n    str r0, [sp]\n    str.w sb, [sp, #4]\n    ldr r0, [r5]\n    adds r1, r1, r0\n    subs r1, r1, #1\n    str r1, [sp, #8]\n    adds.w r0, sl, sb\n    str r0, [sp, #0xc]\n    mov r0, r8\n    sxtb r0, r0\n    lsls r0, r0, #4\n    add r0, r4\n    mov r1, sp\n    movs r2, #0x10\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am017_addr_00439c04\n    bl .\n    adds.w r8, r8, #1\nL_open_cfw_runtime_am017_50c2a_0122:\n    ldr r0, [r6, #8]\n    subs r7, r7, r0\n    ldr r0, [r5]\n    adds r7, r0, r7\n    cmp r7, #1\n    blt L_open_cfw_runtime_am017_50c2a_015a\n    ldr r0, [r6, #8]\n    adds r0, r0, #1\n    str r0, [sp]\n    str.w sb, [sp, #4]\n    ldr r0, [r6, #8]\n    adds r7, r7, r0\n    str r7, [sp, #8]\n    adds.w sb, sl, sb\n    str.w sb, [sp, #0xc]\n    mov r0, r8\n    sxtb r0, r0\n    lsls r0, r0, #4\n    add r0, r4\n    mov r1, sp\n    movs r2, #0x10\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am017_addr_00439c04\n    bl .\n    adds.w r8, r8, #1\nL_open_cfw_runtime_am017_50c2a_015a:\n    mov r0, r8\n    sxtb r0, r0\nL_open_cfw_runtime_am017_50c2a_015e:\n    add sp, #0x10\n    pop.w {r4, r5, r6, r7, r8, sb, sl, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM017_50D8E_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am017_50d8e(void)
{
    __asm__ volatile(
        "    push {r4}\n    ldr r3, [r1]\n    ldr r4, [r2]\n    cmp r3, r4\n    bge L_open_cfw_runtime_am017_50d8e_000e\n    ldr r3, [r1]\n    b L_open_cfw_runtime_am017_50d8e_0010\nL_open_cfw_runtime_am017_50d8e_000e:\n    ldr r3, [r2]\nL_open_cfw_runtime_am017_50d8e_0010:\n    str r3, [r0]\n    ldr r3, [r1, #4]\n    ldr r4, [r2, #4]\n    cmp r3, r4\n    bge L_open_cfw_runtime_am017_50d8e_001e\n    ldr r3, [r1, #4]\n    b L_open_cfw_runtime_am017_50d8e_0020\nL_open_cfw_runtime_am017_50d8e_001e:\n    ldr r3, [r2, #4]\nL_open_cfw_runtime_am017_50d8e_0020:\n    str r3, [r0, #4]\n    ldr r3, [r2, #8]\n    ldr r4, [r1, #8]\n    cmp r3, r4\n    bge L_open_cfw_runtime_am017_50d8e_002e\n    ldr r3, [r1, #8]\n    b L_open_cfw_runtime_am017_50d8e_0030\nL_open_cfw_runtime_am017_50d8e_002e:\n    ldr r3, [r2, #8]\nL_open_cfw_runtime_am017_50d8e_0030:\n    str r3, [r0, #8]\n    ldr r3, [r2, #0xc]\n    ldr r4, [r1, #0xc]\n    cmp r3, r4\n    bge L_open_cfw_runtime_am017_50d8e_003e\n    ldr r1, [r1, #0xc]\n    b L_open_cfw_runtime_am017_50d8e_0040\nL_open_cfw_runtime_am017_50d8e_003e:\n    ldr r1, [r2, #0xc]\nL_open_cfw_runtime_am017_50d8e_0040:\n    str r1, [r0, #0xc]\n    pop {r4}\n    bx lr\n"
    );
}
#endif

#if defined(OPEN_CFW_AM017_50DD4_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am017_50dd4(void)
{
    __asm__ volatile(
        "L_open_cfw_runtime_am017_50dd4_0000:\n    push {r3, r4, r5, r6, r7, lr}\n    sub sp, #0x10\n    movs r4, r0\n    movs r5, r1\n    movs r6, r2\n    movs r0, #0\n    ldr r1, [r5]\n    ldr r2, [r4]\n    cmp r1, r2\n    blt L_open_cfw_runtime_am017_50dd4_002e\n    ldr r1, [r4, #8]\n    ldr r2, [r5]\n    cmp r1, r2\n    blt L_open_cfw_runtime_am017_50dd4_002e\n    ldr r1, [r5, #4]\n    ldr r2, [r4, #4]\n    cmp r1, r2\n    blt L_open_cfw_runtime_am017_50dd4_002e\n    ldr r1, [r4, #0xc]\n    ldr r2, [r5, #4]\n    cmp r1, r2\n    blt L_open_cfw_runtime_am017_50dd4_002e\n    movs r0, #1\nL_open_cfw_runtime_am017_50dd4_002e:\n    uxtb r0, r0\n    cmp r0, #0\n    bne L_open_cfw_runtime_am017_50dd4_0038\n    movs r0, #0\n    b L_open_cfw_runtime_am017_50dd4_0128\nL_open_cfw_runtime_am017_50dd4_0038:\n    cmp r6, #1\n    bge L_open_cfw_runtime_am017_50dd4_0040\n    movs r0, #1\n    b L_open_cfw_runtime_am017_50dd4_0128\nL_open_cfw_runtime_am017_50dd4_0040:\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am017_51598\n    bl .\n    movs r1, #2\n    sdiv r7, r0, r1\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am017_515a4\n    bl .\n    movs r1, #2\n    sdiv r0, r0, r1\n    cmp r7, r0\n    blt L_open_cfw_runtime_am017_50dd4_005e\n    movs r7, r0\nL_open_cfw_runtime_am017_50dd4_005e:\n    cmp r7, r6\n    bge L_open_cfw_runtime_am017_50dd4_0064\n    movs r6, r7\nL_open_cfw_runtime_am017_50dd4_0064:\n    ldr r0, [r4]\n    str r0, [sp]\n    ldr r0, [r4]\n    adds r0, r6, r0\n    str r0, [sp, #8]\n    ldr r0, [r4, #4]\n    str r0, [sp, #4]\n    ldr r0, [r4, #4]\n    adds r0, r6, r0\n    str r0, [sp, #0xc]\n    movs r2, #0\n    movs r1, r5\n    mov r0, sp\n    bl L_open_cfw_runtime_am017_50dd4_0000\n    cmp r0, #0\n    beq L_open_cfw_runtime_am017_50dd4_009c\n    ldr r0, [sp, #8]\n    adds r0, r6, r0\n    str r0, [sp, #8]\n    ldr r0, [sp, #0xc]\n    adds r6, r6, r0\n    str r6, [sp, #0xc]\n    movs r1, r5\n    mov r0, sp\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am017_5163c\n    bl .\n    b L_open_cfw_runtime_am017_50dd4_0128\nL_open_cfw_runtime_am017_50dd4_009c:\n    ldr r0, [r4, #0xc]\n    subs r0, r0, r6\n    str r0, [sp, #4]\n    ldr r0, [r4, #0xc]\n    str r0, [sp, #0xc]\n    movs r2, #0\n    movs r1, r5\n    mov r0, sp\n    bl L_open_cfw_runtime_am017_50dd4_0000\n    cmp r0, #0\n    beq L_open_cfw_runtime_am017_50dd4_00ca\n    ldr r0, [sp, #8]\n    adds r0, r6, r0\n    str r0, [sp, #8]\n    ldr r0, [sp, #4]\n    subs r6, r0, r6\n    str r6, [sp, #4]\n    movs r1, r5\n    mov r0, sp\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am017_5163c\n    bl .\n    b L_open_cfw_runtime_am017_50dd4_0128\nL_open_cfw_runtime_am017_50dd4_00ca:\n    ldr r0, [r4, #8]\n    subs r0, r0, r6\n    str r0, [sp]\n    ldr r0, [r4, #8]\n    str r0, [sp, #8]\n    movs r2, #0\n    movs r1, r5\n    mov r0, sp\n    bl L_open_cfw_runtime_am017_50dd4_0000\n    cmp r0, #0\n    beq L_open_cfw_runtime_am017_50dd4_00f8\n    ldr r0, [sp]\n    subs r0, r0, r6\n    str r0, [sp]\n    ldr r0, [sp, #4]\n    subs r6, r0, r6\n    str r6, [sp, #4]\n    movs r1, r5\n    mov r0, sp\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am017_5163c\n    bl .\n    b L_open_cfw_runtime_am017_50dd4_0128\nL_open_cfw_runtime_am017_50dd4_00f8:\n    ldr r0, [r4, #4]\n    str r0, [sp, #4]\n    ldr r0, [r4, #4]\n    adds r0, r6, r0\n    str r0, [sp, #0xc]\n    movs r2, #0\n    movs r1, r5\n    mov r0, sp\n    bl L_open_cfw_runtime_am017_50dd4_0000\n    cmp r0, #0\n    beq L_open_cfw_runtime_am017_50dd4_0126\n    ldr r0, [sp]\n    subs r0, r0, r6\n    str r0, [sp]\n    ldr r0, [sp, #0xc]\n    adds r6, r6, r0\n    str r6, [sp, #0xc]\n    movs r1, r5\n    mov r0, sp\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am017_5163c\n    bl .\n    b L_open_cfw_runtime_am017_50dd4_0128\nL_open_cfw_runtime_am017_50dd4_0126:\n    movs r0, #1\nL_open_cfw_runtime_am017_50dd4_0128:\n    add sp, #0x14\n    pop {r4, r5, r6, r7, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM017_50F00_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am017_50f00(void)
{
    __asm__ volatile(
        "    ldr r2, [r1, #8]\n    ldr r3, [r0]\n    cmp r2, r3\n    blt L_open_cfw_runtime_am017_50f00_0024\n    ldr r2, [r0, #8]\n    ldr r3, [r1]\n    cmp r2, r3\n    blt L_open_cfw_runtime_am017_50f00_0024\n    ldr r2, [r1, #0xc]\n    ldr r3, [r0, #4]\n    cmp r2, r3\n    blt L_open_cfw_runtime_am017_50f00_0024\n    ldr r0, [r0, #0xc]\n    ldr r1, [r1, #4]\n    cmp r0, r1\n    blt L_open_cfw_runtime_am017_50f00_0024\n    movs r0, #1\n    b L_open_cfw_runtime_am017_50f00_0026\nL_open_cfw_runtime_am017_50f00_0024:\n    movs r0, #0\nL_open_cfw_runtime_am017_50f00_0026:\n    bx lr\n"
    );
}
#endif

#if defined(OPEN_CFW_AM017_50F28_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am017_50f28(void)
{
    __asm__ volatile(
        "    push {r2, r3, r4, r5, r6, lr}\n    movs r5, r0\n    movs r6, r1\n    movs r4, r2\n    movs r0, #0\n    ldr r1, [r5]\n    ldr r2, [r6]\n    cmp r1, r2\n    blt L_open_cfw_runtime_am017_50f28_002c\n    ldr r1, [r5, #4]\n    ldr r2, [r6, #4]\n    cmp r1, r2\n    blt L_open_cfw_runtime_am017_50f28_002c\n    ldr r1, [r6, #8]\n    ldr r2, [r5, #8]\n    cmp r1, r2\n    blt L_open_cfw_runtime_am017_50f28_002c\n    ldr r1, [r6, #0xc]\n    ldr r2, [r5, #0xc]\n    cmp r1, r2\n    blt L_open_cfw_runtime_am017_50f28_002c\n    movs r0, #1\nL_open_cfw_runtime_am017_50f28_002c:\n    uxtb r0, r0\n    cmp r0, #0\n    bne L_open_cfw_runtime_am017_50f28_0036\n    movs r0, #0\n    b L_open_cfw_runtime_am017_50f28_00b0\nL_open_cfw_runtime_am017_50f28_0036:\n    cmp r4, #0\n    bne L_open_cfw_runtime_am017_50f28_003e\n    movs r0, #1\n    b L_open_cfw_runtime_am017_50f28_00b0\nL_open_cfw_runtime_am017_50f28_003e:\n    ldr r2, [r5, #4]\n    ldr r1, [r5]\n    mov r0, sp\n    str r1, [r0]\n    str r2, [r0, #4]\n    movs r2, r4\n    mov r1, sp\n    movs r0, r6\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am017_50dd4\n    bl .\n    cmp r0, #0\n    bne L_open_cfw_runtime_am017_50f28_005a\n    movs r0, #0\n    b L_open_cfw_runtime_am017_50f28_00b0\nL_open_cfw_runtime_am017_50f28_005a:\n    ldr r2, [r5, #4]\n    ldr r1, [r5, #8]\n    mov r0, sp\n    str r1, [r0]\n    str r2, [r0, #4]\n    movs r2, r4\n    mov r1, sp\n    movs r0, r6\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am017_50dd4\n    bl .\n    cmp r0, #0\n    bne L_open_cfw_runtime_am017_50f28_0076\n    movs r0, #0\n    b L_open_cfw_runtime_am017_50f28_00b0\nL_open_cfw_runtime_am017_50f28_0076:\n    ldr r2, [r5, #0xc]\n    ldr r1, [r5]\n    mov r0, sp\n    str r1, [r0]\n    str r2, [r0, #4]\n    movs r2, r4\n    mov r1, sp\n    movs r0, r6\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am017_50dd4\n    bl .\n    cmp r0, #0\n    bne L_open_cfw_runtime_am017_50f28_0092\n    movs r0, #0\n    b L_open_cfw_runtime_am017_50f28_00b0\nL_open_cfw_runtime_am017_50f28_0092:\n    ldr r2, [r5, #0xc]\n    ldr r1, [r5, #8]\n    mov r0, sp\n    str r1, [r0]\n    str r2, [r0, #4]\n    movs r2, r4\n    mov r1, sp\n    movs r0, r6\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am017_50dd4\n    bl .\n    cmp r0, #0\n    bne L_open_cfw_runtime_am017_50f28_00ae\n    movs r0, #0\n    b L_open_cfw_runtime_am017_50f28_00b0\nL_open_cfw_runtime_am017_50f28_00ae:\n    movs r0, #1\nL_open_cfw_runtime_am017_50f28_00b0:\n    pop {r1, r2, r4, r5, r6, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM017_50FDA_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am017_50fda(void)
{
    __asm__ volatile(
        "    push {r2, r3, r4, r5, r6, lr}\n    movs r5, r0\n    movs r6, r1\n    movs r4, r2\n    ldr r0, [r5, #8]\n    ldr r1, [r6]\n    cmp r0, r1\n    blt L_open_cfw_runtime_am017_50fda_0028\n    ldr r0, [r5, #0xc]\n    ldr r1, [r6, #4]\n    cmp r0, r1\n    blt L_open_cfw_runtime_am017_50fda_0028\n    ldr r0, [r6, #8]\n    ldr r1, [r5]\n    cmp r0, r1\n    blt L_open_cfw_runtime_am017_50fda_0028\n    ldr r0, [r6, #0xc]\n    ldr r1, [r5, #4]\n    cmp r0, r1\n    bge L_open_cfw_runtime_am017_50fda_002c\nL_open_cfw_runtime_am017_50fda_0028:\n    movs r0, #1\n    b L_open_cfw_runtime_am017_50fda_00a6\nL_open_cfw_runtime_am017_50fda_002c:\n    cmp r4, #0\n    bne L_open_cfw_runtime_am017_50fda_0034\n    movs r0, #0\n    b L_open_cfw_runtime_am017_50fda_00a6\nL_open_cfw_runtime_am017_50fda_0034:\n    ldr r2, [r5, #4]\n    ldr r1, [r5]\n    mov r0, sp\n    str r1, [r0]\n    str r2, [r0, #4]\n    movs r2, r4\n    mov r1, sp\n    movs r0, r6\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am017_50dd4\n    bl .\n    cmp r0, #0\n    beq L_open_cfw_runtime_am017_50fda_0050\n    movs r0, #0\n    b L_open_cfw_runtime_am017_50fda_00a6\nL_open_cfw_runtime_am017_50fda_0050:\n    ldr r2, [r5, #4]\n    ldr r1, [r5, #8]\n    mov r0, sp\n    str r1, [r0]\n    str r2, [r0, #4]\n    movs r2, r4\n    mov r1, sp\n    movs r0, r6\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am017_50dd4\n    bl .\n    cmp r0, #0\n    beq L_open_cfw_runtime_am017_50fda_006c\n    movs r0, #0\n    b L_open_cfw_runtime_am017_50fda_00a6\nL_open_cfw_runtime_am017_50fda_006c:\n    ldr r2, [r5, #0xc]\n    ldr r1, [r5]\n    mov r0, sp\n    str r1, [r0]\n    str r2, [r0, #4]\n    movs r2, r4\n    mov r1, sp\n    movs r0, r6\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am017_50dd4\n    bl .\n    cmp r0, #0\n    beq L_open_cfw_runtime_am017_50fda_0088\n    movs r0, #0\n    b L_open_cfw_runtime_am017_50fda_00a6\nL_open_cfw_runtime_am017_50fda_0088:\n    ldr r2, [r5, #0xc]\n    ldr r1, [r5, #8]\n    mov r0, sp\n    str r1, [r0]\n    str r2, [r0, #4]\n    movs r2, r4\n    mov r1, sp\n    movs r0, r6\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am017_50dd4\n    bl .\n    cmp r0, #0\n    beq L_open_cfw_runtime_am017_50fda_00a4\n    movs r0, #0\n    b L_open_cfw_runtime_am017_50fda_00a6\nL_open_cfw_runtime_am017_50fda_00a4:\n    movs r0, #1\nL_open_cfw_runtime_am017_50fda_00a6:\n    pop {r1, r2, r4, r5, r6, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM017_51082_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am017_51082(void)
{
    __asm__ volatile(
        "    push.w {r3, r4, r5, r6, r7, r8, sb, lr}\n    movs r5, r0\n    movs r6, r1\n    movs r4, r3\n    uxtb r2, r2\n    cmp r2, #1\n    beq L_open_cfw_runtime_am017_51082_00a8\n    blo.w #0x451364\n    cmp r2, #3\n    beq L_open_cfw_runtime_am017_51082_00d0\n    blo L_open_cfw_runtime_am017_51082_00b0\n    cmp r2, #5\n    beq L_open_cfw_runtime_am017_51082_00fc\n    blo L_open_cfw_runtime_am017_51082_00e6\n    cmp r2, #7\n    beq.w #0x4511d0\n    blo.w #0x4511ac\n    cmp r2, #9\n    beq L_open_cfw_runtime_am017_51082_0070\n    blo.w #0x4511f0\n    cmp r2, #0xb\n    beq.w #0x45122e\n    blo.w #0x45121e\n    cmp r2, #0xd\n    beq.w #0x451274\n    blo.w #0x451256\n    cmp r2, #0xf\n    beq.w #0x4512a4\n    blo.w #0x451280\n    cmp r2, #0x11\n    beq.w #0x4512ce\n    blo.w #0x4512be\n    cmp r2, #0x13\n    beq.w #0x451314\n    blo.w #0x4512f6\n    cmp r2, #0x15\n    beq.w #0x451348\n    blo.w #0x451322\n    b L_open_cfw_runtime_am017_51082_02e2\nL_open_cfw_runtime_am017_51082_0070:\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am017_51598\n    bl .\n    movs r1, #2\n    sdiv r7, r0, r1\n    movs r0, r6\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am017_51598\n    bl .\n    movs r1, #2\n    sdiv r0, r0, r1\n    subs r7, r7, r0\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am017_515a4\n    bl .\n    movs r1, #2\n    sdiv sb, r0, r1\n    movs r0, r6\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am017_515a4\n    bl .\n    movs r1, #2\n    sdiv r0, r0, r1\n    subs.w sb, sb, r0\n    b L_open_cfw_runtime_am017_51082_02e8\nL_open_cfw_runtime_am017_51082_00a8:\n    movs r7, #0\n    movs.w sb, #0\n    b L_open_cfw_runtime_am017_51082_02e8\nL_open_cfw_runtime_am017_51082_00b0:\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am017_51598\n    bl .\n    movs r1, #2\n    sdiv r7, r0, r1\n    movs r0, r6\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am017_51598\n    bl .\n    movs r1, #2\n    sdiv r0, r0, r1\n    subs r7, r7, r0\n    movs.w sb, #0\n    b L_open_cfw_runtime_am017_51082_02e8\nL_open_cfw_runtime_am017_51082_00d0:\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am017_51598\n    bl .\n    movs r7, r0\n    movs r0, r6\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am017_51598\n    bl .\n    subs r7, r7, r0\n    movs.w sb, #0\n    b L_open_cfw_runtime_am017_51082_02e8\nL_open_cfw_runtime_am017_51082_00e6:\n    movs r7, #0\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am017_515a4\n    bl .\n    mov sb, r0\n    movs r0, r6\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am017_515a4\n    bl .\n    subs.w sb, sb, r0\n    b L_open_cfw_runtime_am017_51082_02e8\nL_open_cfw_runtime_am017_51082_00fc:\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am017_51598\n    bl .\n    movs r1, #2\n    sdiv r7, r0, r1\n    movs r0, r6\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am017_51598\n    bl .\n    movs r1, #2\n    sdiv r0, r0, r1\n    subs r7, r7, r0\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am017_515a4\n    bl .\n    mov sb, r0\n    movs r0, r6\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am017_515a4\n    bl .\n    subs.w sb, sb, r0\n    b L_open_cfw_runtime_am017_51082_02e8\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am017_51598\n    bl .\n    movs r7, r0\n    movs r0, r6\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am017_51598\n    bl .\n    subs r7, r7, r0\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am017_515a4\n    bl .\n    mov sb, r0\n    movs r0, r6\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am017_515a4\n    bl .\n    subs.w sb, sb, r0\n    b L_open_cfw_runtime_am017_51082_02e8\n    movs r7, #0\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am017_515a4\n    bl .\n    movs r1, #2\n    sdiv sb, r0, r1\n    movs r0, r6\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am017_515a4\n    bl .\n    movs r1, #2\n    sdiv r0, r0, r1\n    subs.w sb, sb, r0\n    b L_open_cfw_runtime_am017_51082_02e8\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am017_51598\n    bl .\n    movs r7, r0\n    movs r0, r6\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am017_51598\n    bl .\n    subs r7, r7, r0\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am017_515a4\n    bl .\n    movs r1, #2\n    sdiv sb, r0, r1\n    movs r0, r6\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am017_515a4\n    bl .\n    movs r1, #2\n    sdiv r0, r0, r1\n    subs.w sb, sb, r0\n    b L_open_cfw_runtime_am017_51082_02e8\n    movs r7, #0\n    movs r0, r6\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am017_515a4\n    bl .\n    mov sb, r0\n    rsbs.w sb, sb, #0\n    b L_open_cfw_runtime_am017_51082_02e8\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am017_51598\n    bl .\n    movs r1, #2\n    sdiv r7, r0, r1\n    movs r0, r6\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am017_51598\n    bl .\n    movs r1, #2\n    sdiv r0, r0, r1\n    subs r7, r7, r0\n    movs r0, r6\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am017_515a4\n    bl .\n    mov sb, r0\n    rsbs.w sb, sb, #0\n    b L_open_cfw_runtime_am017_51082_02e8\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am017_51598\n    bl .\n    movs r7, r0\n    movs r0, r6\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am017_51598\n    bl .\n    subs r7, r7, r0\n    movs r0, r6\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am017_515a4\n    bl .\n    mov sb, r0\n    rsbs.w sb, sb, #0\n    b L_open_cfw_runtime_am017_51082_02e8\n    movs r7, #0\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am017_515a4\n    bl .\n    mov sb, r0\n    b L_open_cfw_runtime_am017_51082_02e8\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am017_51598\n    bl .\n    movs r1, #2\n    sdiv r7, r0, r1\n    movs r0, r6\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am017_51598\n    bl .\n    movs r1, #2\n    sdiv r0, r0, r1\n    subs r7, r7, r0\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am017_515a4\n    bl .\n    mov sb, r0\n    b L_open_cfw_runtime_am017_51082_02e8\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am017_51598\n    bl .\n    movs r7, r0\n    movs r0, r6\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am017_51598\n    bl .\n    subs r7, r7, r0\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am017_515a4\n    bl .\n    mov sb, r0\n    b L_open_cfw_runtime_am017_51082_02e8\n    movs r0, r6\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am017_51598\n    bl .\n    movs r7, r0\n    rsbs r7, r7, #0\n    movs.w sb, #0\n    b L_open_cfw_runtime_am017_51082_02e8\n    movs r0, r6\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am017_51598\n    bl .\n    movs r7, r0\n    rsbs r7, r7, #0\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am017_515a4\n    bl .\n    movs r1, #2\n    sdiv sb, r0, r1\n    movs r0, r6\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am017_515a4\n    bl .\n    movs r1, #2\n    sdiv r0, r0, r1\n    subs.w sb, sb, r0\n    b L_open_cfw_runtime_am017_51082_02e8\n    movs r0, r6\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am017_51598\n    bl .\n    movs r7, r0\n    rsbs r7, r7, #0\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am017_515a4\n    bl .\n    mov sb, r0\n    movs r0, r6\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am017_515a4\n    bl .\n    subs.w sb, sb, r0\n    b L_open_cfw_runtime_am017_51082_02e8\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am017_51598\n    bl .\n    movs r7, r0\n    movs.w sb, #0\n    b L_open_cfw_runtime_am017_51082_02e8\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am017_51598\n    bl .\n    movs r7, r0\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am017_515a4\n    bl .\n    movs r1, #2\n    sdiv sb, r0, r1\n    movs r0, r6\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am017_515a4\n    bl .\n    movs r1, #2\n    sdiv r0, r0, r1\n    subs.w sb, sb, r0\n    b L_open_cfw_runtime_am017_51082_02e8\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am017_51598\n    bl .\n    movs r7, r0\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am017_515a4\n    bl .\n    mov sb, r0\n    movs r0, r6\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am017_515a4\n    bl .\n    subs.w sb, sb, r0\n    b L_open_cfw_runtime_am017_51082_02e8\nL_open_cfw_runtime_am017_51082_02e2:\n    movs r7, #0\n    movs.w sb, #0\nL_open_cfw_runtime_am017_51082_02e8:\n    ldr.w r8, [sp, #0x20]\n    ldr r0, [r5]\n    adds r7, r0, r7\n    ldr r0, [r5, #4]\n    adds.w sb, r0, sb\n    mov r5, sb\n    movs r0, r6\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am017_51598\n    bl .\n    mov sb, r0\n    movs r0, r6\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am017_515a4\n    bl .\n    adds r4, r4, r7\n    str r4, [r6]\n    adds.w r8, r8, r5\n    str.w r8, [r6, #4]\n    ldr r1, [r6]\n    adds.w sb, sb, r1\n    subs.w sb, sb, #1\n    str.w sb, [r6, #8]\n    ldr r1, [r6, #4]\n    adds r0, r0, r1\n    subs r0, r0, #1\n    str r0, [r6, #0xc]\n    pop.w {r0, r4, r5, r6, r7, r8, sb, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM017_513AE_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am017_513ae(void)
{
    __asm__ volatile(
        "    push {r0, r1, r2, r3, r4, lr}\n    ldrb.w r4, [sp, #0x1c]\n    str r4, [sp, #8]\n    ldr r4, [sp, #0x18]\n    str r4, [sp, #4]\n    str r3, [sp]\n    movs r3, r2\n    movs r2, r1\n    movs r1, #1\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am017_513c8\n    bl .\n    pop {r0, r1, r2, r3, r4, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM017_513C8_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am017_513c8(void)
{
    __asm__ volatile(
        "    push.w {r1, r2, r3, r4, r5, r6, r7, r8, sb, sl, fp, lr}\n    movs r6, r3\n    ldr r7, [sp, #0x30]\n    cmp r2, #0\n    bne L_open_cfw_runtime_am017_513c8_001a\n    cmp.w r6, #0x100\n    bne L_open_cfw_runtime_am017_513c8_001a\n    cmp.w r7, #0x100\n    beq.w #0x451594\nL_open_cfw_runtime_am017_513c8_001a:\n    movs r3, #0\n    movs r4, r0\n    str r1, [sp]\n    ldr.w r8, [sp, #0x34]\n    b L_open_cfw_runtime_am017_513c8_0048\nL_open_cfw_runtime_am017_513c8_0026:\n    ldr.w r1, [r4, r3, lsl #3]\n    ldr.w r0, [r8]\n    subs r1, r1, r0\n    str.w r1, [r4, r3, lsl #3]\n    add.w r0, r4, r3, lsl #3\n    ldr r1, [r0, #4]\n    ldr.w r0, [r8, #4]\n    subs r1, r1, r0\n    add.w r0, r4, r3, lsl #3\n    str r1, [r0, #4]\n    adds r3, r3, #1\nL_open_cfw_runtime_am017_513c8_0048:\n    ldr r0, [sp]\n    cmp r3, r0\n    blo L_open_cfw_runtime_am017_513c8_0026\n    cmp r2, #0\n    bne L_open_cfw_runtime_am017_513c8_0088\n    movs r0, #0\n    b L_open_cfw_runtime_am017_513c8_0080\nL_open_cfw_runtime_am017_513c8_0056:\n    ldr.w r1, [r4, r0, lsl #3]\n    muls r1, r6, r1\n    ldr.w r2, [r8]\n    adds.w r2, r2, r1, asr #8\n    str.w r2, [r4, r0, lsl #3]\n    add.w r1, r4, r0, lsl #3\n    ldr r1, [r1, #4]\n    muls r1, r7, r1\n    ldr.w r2, [r8, #4]\n    adds.w r2, r2, r1, asr #8\n    add.w r1, r4, r0, lsl #3\n    str r2, [r1, #4]\n    adds r0, r0, #1\nL_open_cfw_runtime_am017_513c8_0080:\n    ldr r1, [sp]\n    cmp r0, r1\n    blo L_open_cfw_runtime_am017_513c8_0056\n    b L_open_cfw_runtime_am017_513c8_01cc\nL_open_cfw_runtime_am017_513c8_0088:\n    movw r0, #0xe11\n    cmp r2, r0\n    blt L_open_cfw_runtime_am017_513c8_0094\n    subs.w r2, r2, #0xe10\nL_open_cfw_runtime_am017_513c8_0094:\n    cmp r2, #0\n    bpl L_open_cfw_runtime_am017_513c8_009c\n    adds.w r2, r2, #0xe10\nL_open_cfw_runtime_am017_513c8_009c:\n    movs r0, #0xa\n    sdiv sb, r2, r0\n    adds.w r0, sb, #1\n    str r0, [sp, #4]\n    mvns r0, #9\n    mla r2, r0, sb, r2\n    movs r5, r2\n    mov r0, sb\n    sxth r0, r0\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am017_addr_004885f0\n    bl .\n    mov sl, r0\n    ldr r0, [sp, #4]\n    sxth r0, r0\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am017_addr_004885f0\n    bl .\n    mov fp, r0\n    adds.w sb, sb, #0x5a\n    mov r0, sb\n    sxth r0, r0\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am017_addr_004885f0\n    bl .\n    mov sb, r0\n    ldr r0, [sp, #4]\n    adds r0, #0x5a\n    sxth r0, r0\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am017_addr_004885f0\n    bl .\n    rsbs.w r1, r5, #0xa\n    mul fp, r5, fp\n    mla sl, r1, sl, fp\n    movs r1, #0xa\n    sdiv r1, sl, r1\n    asrs r1, r1, #5\n    rsbs.w r2, r5, #0xa\n    mul r5, r5, r0\n    mla r5, r2, sb, r5\n    movs r0, #0xa\n    sdiv r3, r5, r0\n    asrs r3, r3, #5\n    movs r2, #0\n    ldr r0, [sp, #0x38]\n    b L_open_cfw_runtime_am017_513c8_0180\nL_open_cfw_runtime_am017_513c8_010c:\n    mul lr, r5, r3\n    mls lr, ip, r1, lr\n    mul lr, r6, lr\n    ldr.w sb, [r8]\n    adds.w sb, sb, lr, asr #18\n    str.w sb, [r4, r2, lsl #3]\n    mul ip, ip, r3\n    mla r5, r5, r1, ip\n    muls r5, r7, r5\n    ldr.w ip, [r8, #4]\n    adds.w ip, ip, r5, asr #18\n    add.w r5, r4, r2, lsl #3\n    str.w ip, [r5, #4]\n    b L_open_cfw_runtime_am017_513c8_017e\nL_open_cfw_runtime_am017_513c8_0140:\n    mov lr, r0\n    uxtb.w lr, lr\n    cmp.w lr, #0\n    beq L_open_cfw_runtime_am017_513c8_010c\n    muls r5, r6, r5\n    mul ip, r7, ip\n    mul lr, r5, r3\n    mls lr, ip, r1, lr\n    ldr.w sb, [r8]\n    adds.w sb, sb, lr, asr #18\n    str.w sb, [r4, r2, lsl #3]\n    mul ip, ip, r3\n    mla r5, r5, r1, ip\n    ldr.w ip, [r8, #4]\n    adds.w ip, ip, r5, asr #18\n    add.w r5, r4, r2, lsl #3\n    str.w ip, [r5, #4]\nL_open_cfw_runtime_am017_513c8_017e:\n    adds r2, r2, #1\nL_open_cfw_runtime_am017_513c8_0180:\n    ldr r5, [sp]\n    cmp r2, r5\n    bhs L_open_cfw_runtime_am017_513c8_01cc\n    ldr.w r5, [r4, r2, lsl #3]\n    add.w ip, r4, r2, lsl #3\n    ldr.w ip, [ip, #4]\n    cmp.w r6, #0x100\n    bne L_open_cfw_runtime_am017_513c8_0140\n    cmp.w r7, #0x100\n    bne L_open_cfw_runtime_am017_513c8_0140\n    mul lr, r5, r3\n    mls lr, ip, r1, lr\n    ldr.w sb, [r8]\n    adds.w sb, sb, lr, asr #10\n    str.w sb, [r4, r2, lsl #3]\n    mul ip, ip, r3\n    mla r5, r5, r1, ip\n    ldr.w ip, [r8, #4]\n    adds.w ip, ip, r5, asr #10\n    add.w r5, r4, r2, lsl #3\n    str.w ip, [r5, #4]\n    b L_open_cfw_runtime_am017_513c8_017e\nL_open_cfw_runtime_am017_513c8_01cc:\n    pop.w {r0, r1, r2, r4, r5, r6, r7, r8, sb, sl, fp, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM017_51598_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am017_51598(void)
{
    __asm__ volatile(
        "    movs r1, r0\n    ldr r0, [r1, #8]\n    ldr r1, [r1]\n    subs r0, r0, r1\n    adds r0, r0, #1\n    bx lr\n"
    );
}
#endif

#if defined(OPEN_CFW_AM017_515A4_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am017_515a4(void)
{
    __asm__ volatile(
        "    movs r1, r0\n    ldr r0, [r1, #0xc]\n    ldr r1, [r1, #4]\n    subs r0, r0, r1\n    adds r0, r0, #1\n    bx lr\n"
    );
}
#endif

#if defined(OPEN_CFW_AM017_515B0_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am017_515b0(void)
{
    __asm__ volatile(
        "    vldr s0, [r0]\n    vcvt.f32.s32 s0, s0\n    vmov.f32 s2, s0\n    vldr s0, [r0, #4]\n    vcvt.f32.s32 s0, s0\n    vmov.f32 s3, s0\n    vmov.f32 s0, s2\n    vmov.f32 s1, s3\n    bx lr\n"
    );
}
#endif

#if defined(OPEN_CFW_AM017_515D2_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am017_515d2(void)
{
    __asm__ volatile(
        "    cmp r0, #0\n    bpl L_open_cfw_runtime_am017_515d2_0014\n    ldr r1, [pc, #0x20]\n    cmp r0, r1\n    bge L_open_cfw_runtime_am017_515d2_000c\n    ldr r0, [pc, #0x1c]\nL_open_cfw_runtime_am017_515d2_000c:\n    mvns r1, #0xf0000000\n    subs r0, r1, r0\n    b L_open_cfw_runtime_am017_515d2_001e\nL_open_cfw_runtime_am017_515d2_0014:\n    mvns r1, #0xf0000000\n    cmp r0, r1\n    blt L_open_cfw_runtime_am017_515d2_001e\n    movs r0, r1\nL_open_cfw_runtime_am017_515d2_001e:\n    orrs r0, r0, #0x20000000\n    bx lr\n"
    );
}
#endif

#if defined(OPEN_CFW_AM017_51600_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am017_51600(void)
{
    __asm__ volatile(
        "    ands r2, r0, #0x60000000\n    cmp.w r2, #0x20000000\n    bne L_open_cfw_runtime_am017_51600_003a\n    bics r2, r0, #0x60000000\n    mvns r3, #0xe0000000\n    cmp r2, r3\n    bge L_open_cfw_runtime_am017_51600_003a\n    bics r2, r0, #0x60000000\n    cmp.w r2, #0x10000000\n    blt L_open_cfw_runtime_am017_51600_002c\n    mvns r2, #0xf0000000\n    bics r0, r0, #0x60000000\n    subs r0, r2, r0\n    b L_open_cfw_runtime_am017_51600_0030\nL_open_cfw_runtime_am017_51600_002c:\n    bics r0, r0, #0x60000000\nL_open_cfw_runtime_am017_51600_0030:\n    muls r0, r1, r0\n    movs r1, #0x64\n    sdiv r0, r0, r1\n    b L_open_cfw_runtime_am017_51600_003a\nL_open_cfw_runtime_am017_51600_003a:\n    bx lr\n"
    );
}
#endif

#if defined(OPEN_CFW_AM017_5163C_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am017_5163c(void)
{
    __asm__ volatile(
        "    push {r4}\n    ldr r3, [r0, #8]\n    ldr r2, [r0]\n    subs r3, r3, r2\n    movs r2, #2\n    sdiv r2, r3, r2\n    ldr r3, [r0]\n    adds r3, r2, r3\n    ldr r0, [r0, #4]\n    adds r0, r2, r0\n    ldr r4, [r1]\n    subs r3, r4, r3\n    ldr r1, [r1, #4]\n    subs r0, r1, r0\n    muls r2, r2, r2\n    muls r0, r0, r0\n    mla r3, r3, r3, r0\n    cmp r2, r3\n    blo L_open_cfw_runtime_am017_5163c_002e\n    movs r0, #1\n    b L_open_cfw_runtime_am017_5163c_0030\nL_open_cfw_runtime_am017_5163c_002e:\n    movs r0, #0\nL_open_cfw_runtime_am017_5163c_0030:\n    pop {r4}\n    bx lr\n"
    );
}
#endif

#if defined(OPEN_CFW_AM017_51670_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am017_51670(void)
{
    __asm__ volatile(
        "    push {r3, r4, lr}\n    sub sp, #0x1c\n    cmp r0, #0\n    bne L_open_cfw_runtime_am017_51670_000c\n    movs r0, #1\n    b L_open_cfw_runtime_am017_51670_0084\nL_open_cfw_runtime_am017_51670_000c:\n    cmp r0, #0\n    bne L_open_cfw_runtime_am017_51670_003c\n    ldr.w r0, [pc, #0x3a8]\n    str r0, [sp, #8]\n    ldr.w r0, [pc, #0x3a8]\n    str r0, [sp, #4]\n    ldr.w r0, [pc, #0x3a4]\n    str r0, [sp]\n    ldr.w r3, [pc, #0x3a4]\n    movs r2, #0x34\n    ldr.w r1, [pc, #0x3a0]\n    movs r0, #3\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am017_addr_0044d25c\n    bl .\nL_open_cfw_runtime_am017_51670_0032:\n    movs r0, #0\n    movs.w r1, #-1\n    str r0, [r1]\n    b L_open_cfw_runtime_am017_51670_0032\nL_open_cfw_runtime_am017_51670_003c:\n    str r0, [sp]\n    str r0, [sp, #4]\n    str r1, [sp, #8]\n    movs r0, #0\n    str r0, [sp, #0xc]\n    str r2, [sp, #0x10]\n    ldrb.w r0, [sp, #0x18]\n    ands r0, r0, #0xfe\n    strb.w r0, [sp, #0x18]\n    ldrb.w r0, [sp, #0x18]\n    ands r0, r0, #0xfb\n    strb.w r0, [sp, #0x18]\n    ldrb.w r0, [sp, #0x18]\n    ands r0, r0, #0xfd\n    strb.w r0, [sp, #0x18]\n    mov r0, sp\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am017_addr_0044ffd0\n    bl .\n    mov r0, sp\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am017_51a6c\n    bl .\n    movs r4, r0\n    mov r0, sp\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am017_addr_0044ffdc\n    bl .\n    movs r0, r4\n    uxtb r0, r0\nL_open_cfw_runtime_am017_51670_0084:\n    add sp, #0x20\n    pop {r4, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM017_516F8_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am017_516f8(void)
{
    __asm__ volatile(
        "    push {r4, lr}\n    movs r4, r1\n    cmp r0, #0\n    bne L_open_cfw_runtime_am017_516f8_000e\n    ldr r0, [r4]\n    ldr r0, [r0]\n    b L_open_cfw_runtime_am017_516f8_0014\nL_open_cfw_runtime_am017_516f8_000e:\n    ldr r0, [r0]\n    b L_open_cfw_runtime_am017_516f8_0014\nL_open_cfw_runtime_am017_516f8_0012:\n    ldr r0, [r0]\nL_open_cfw_runtime_am017_516f8_0014:\n    cmp r0, #0\n    beq L_open_cfw_runtime_am017_516f8_001e\n    ldr r1, [r0, #0xc]\n    cmp r1, #0\n    beq L_open_cfw_runtime_am017_516f8_0012\nL_open_cfw_runtime_am017_516f8_001e:\n    cmp r0, #0\n    bne L_open_cfw_runtime_am017_516f8_0026\n    movs r0, #1\n    b L_open_cfw_runtime_am017_516f8_0046\nL_open_cfw_runtime_am017_516f8_0026:\n    ldr r1, [r0, #0xc]\n    cmp r1, #0\n    bne L_open_cfw_runtime_am017_516f8_0030\n    movs r0, #1\n    b L_open_cfw_runtime_am017_516f8_0046\nL_open_cfw_runtime_am017_516f8_0030:\n    movs r1, #0\n    str r1, [r4, #0xc]\n    movs r1, r4\n    ldr r2, [r0, #0xc]\n    blx r2\n    movs r0, #1\n    ldrb r1, [r4, #0x18]\n    lsls r1, r1, #0x1f\n    bpl L_open_cfw_runtime_am017_516f8_0044\n    movs r0, #0\nL_open_cfw_runtime_am017_516f8_0044:\n    uxtb r0, r0\nL_open_cfw_runtime_am017_516f8_0046:\n    pop {r4, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM017_51740_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am017_51740(void)
{
    __asm__ volatile(
        "    push {r1, r2, r3, r4, r5, r6, r7, lr}\n    movs r4, r0\n    movs r5, r1\n    movs r6, r2\n    movs r7, r3\n    cmp r4, #0\n    bne L_open_cfw_runtime_am017_51740_003a\n    ldr.w r0, [pc, #0x2dc]\n    str r0, [sp, #8]\n    ldr.w r0, [pc, #0x2d8]\n    str r0, [sp, #4]\n    ldr.w r0, [pc, #0x2d8]\n    str r0, [sp]\n    ldr.w r3, [pc, #0x2dc]\n    movs r2, #0x66\n    ldr.w r1, [pc, #0x2d4]\n    movs r0, #3\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am017_addr_0044d25c\n    bl .\nL_open_cfw_runtime_am017_51740_0030:\n    movs r0, #0\n    movs.w r1, #-1\n    str r0, [r1]\n    b L_open_cfw_runtime_am017_51740_0030\nL_open_cfw_runtime_am017_51740_003a:\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am017_addr_0043e1fa\n    bl .\n    movs r3, r7\n    movs r2, r6\n    movs r1, r5\n    ldr r0, [r4, #8]\n    adds r0, #8\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am017_addr_004500e4\n    bl .\n    pop {r1, r2, r3, r4, r5, r6, r7, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM017_51790_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am017_51790(void)
{
    __asm__ volatile(
        "    push {r5, r6, r7, lr}\n    cmp r0, #0\n    bne L_open_cfw_runtime_am017_51790_0032\n    ldr.w r0, [pc, #0x294]\n    str r0, [sp, #8]\n    ldr.w r0, [pc, #0x290]\n    str r0, [sp, #4]\n    ldr.w r0, [pc, #0x290]\n    str r0, [sp]\n    ldr.w r3, [pc, #0x298]\n    movs r2, #0x6e\n    ldr.w r1, [pc, #0x28c]\n    movs r0, #3\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am017_addr_0044d25c\n    bl .\nL_open_cfw_runtime_am017_51790_0028:\n    movs r0, #0\n    movs.w r1, #-1\n    str r0, [r1]\n    b L_open_cfw_runtime_am017_51790_0028\nL_open_cfw_runtime_am017_51790_0032:\n    ldr r1, [r0, #8]\n    cmp r1, #0\n    bne L_open_cfw_runtime_am017_51790_003c\n    movs r0, #0\n    b L_open_cfw_runtime_am017_51790_0044\nL_open_cfw_runtime_am017_51790_003c:\n    ldr r0, [r0, #8]\n    adds r0, #8\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am017_addr_00450158\n    bl .\nL_open_cfw_runtime_am017_51790_0044:\n    pop {r1, r2, r3, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM017_517D6_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am017_517d6(void)
{
    __asm__ volatile(
        "    push {r5, r6, r7, lr}\n    cmp r0, #0\n    bne L_open_cfw_runtime_am017_517d6_0032\n    ldr.w r0, [pc, #0x24c]\n    str r0, [sp, #8]\n    ldr.w r0, [pc, #0x24c]\n    str r0, [sp, #4]\n    ldr.w r0, [pc, #0x248]\n    str r0, [sp]\n    ldr.w r3, [pc, #0x258]\n    movs r2, #0x75\n    ldr.w r1, [pc, #0x244]\n    movs r0, #3\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am017_addr_0044d25c\n    bl .\nL_open_cfw_runtime_am017_517d6_0028:\n    movs r0, #0\n    movs.w r1, #-1\n    str r0, [r1]\n    b L_open_cfw_runtime_am017_517d6_0028\nL_open_cfw_runtime_am017_517d6_0032:\n    ldr r2, [r0, #8]\n    cmp r2, #0\n    bne L_open_cfw_runtime_am017_517d6_003c\n    movs r0, #0\n    b L_open_cfw_runtime_am017_517d6_0044\nL_open_cfw_runtime_am017_517d6_003c:\n    ldr r0, [r0, #8]\n    adds r0, #8\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am017_addr_00450190\n    bl .\nL_open_cfw_runtime_am017_517d6_0044:\n    pop {r1, r2, r3, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM017_5181C_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am017_5181c(void)
{
    __asm__ volatile(
        "    push {r5, r6, r7, lr}\n    cmp r0, #0\n    bne L_open_cfw_runtime_am017_5181c_0032\n    ldr.w r0, [pc, #0x208]\n    str r0, [sp, #8]\n    ldr.w r0, [pc, #0x204]\n    str r0, [sp, #4]\n    ldr.w r0, [pc, #0x204]\n    str r0, [sp]\n    ldr.w r3, [pc, #0x214]\n    movs r2, #0x7c\n    ldr.w r1, [pc, #0x200]\n    movs r0, #3\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am017_addr_0044d25c\n    bl .\nL_open_cfw_runtime_am017_5181c_0028:\n    movs r0, #0\n    movs.w r1, #-1\n    str r0, [r1]\n    b L_open_cfw_runtime_am017_5181c_0028\nL_open_cfw_runtime_am017_5181c_0032:\n    ldr r2, [r0, #8]\n    cmp r2, #0\n    bne L_open_cfw_runtime_am017_5181c_003c\n    movs r0, #0\n    b L_open_cfw_runtime_am017_5181c_0044\nL_open_cfw_runtime_am017_5181c_003c:\n    ldr r0, [r0, #8]\n    adds r0, #8\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am017_addr_004501d2\n    bl .\nL_open_cfw_runtime_am017_5181c_0044:\n    pop {r1, r2, r3, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM017_51862_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am017_51862(void)
{
    __asm__ volatile(
        "    push.w {r0, r1, r2, r3, r4, r5, r6, r7, r8, lr}\n    movs r4, r0\n    movs r5, r1\n    cmp r4, #0\n    bne L_open_cfw_runtime_am017_51862_0038\n    ldr.w r0, [pc, #0x1bc]\n    str r0, [sp, #8]\n    ldr.w r0, [pc, #0x1b8]\n    str r0, [sp, #4]\n    ldr.w r0, [pc, #0x1b8]\n    str r0, [sp]\n    ldr.w r3, [pc, #0x1cc]\n    movs r2, #0x8b\n    ldr.w r1, [pc, #0x1b4]\n    movs r0, #3\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am017_addr_0044d25c\n    bl .\nL_open_cfw_runtime_am017_51862_002e:\n    movs r0, #0\n    movs.w r1, #-1\n    str r0, [r1]\n    b L_open_cfw_runtime_am017_51862_002e\nL_open_cfw_runtime_am017_51862_0038:\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am017_51790\n    bl .\n    movs r6, r0\n    movs r7, #0\n    movs.w r8, #0\n    b L_open_cfw_runtime_am017_51862_006a\nL_open_cfw_runtime_am017_51862_0048:\n    mov r1, r8\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am017_517d6\n    bl .\n    cmp r0, #0\n    beq L_open_cfw_runtime_am017_51862_0066\n    ldr r0, [r0]\n    movs r1, r5\n    cmp r0, r1\n    bne L_open_cfw_runtime_am017_51862_0066\n    mov r1, r8\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am017_5181c\n    bl .\n    adds r7, r7, #1\nL_open_cfw_runtime_am017_51862_0066:\n    adds.w r8, r8, #1\nL_open_cfw_runtime_am017_51862_006a:\n    cmp r8, r6\n    blo L_open_cfw_runtime_am017_51862_0048\n    movs r0, r7\n    add sp, #0x10\n    pop.w {r4, r5, r6, r7, r8, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM017_518D8_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am017_518d8(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    ldr r1, [r0, #8]\n    cmp r1, #1\n    beq L_open_cfw_runtime_am017_518d8_006e\n    ldr r1, [r0, #8]\n    cmp r1, #2\n    beq L_open_cfw_runtime_am017_518d8_006e\n    ldr r1, [r0, #8]\n    cmp r1, #3\n    beq L_open_cfw_runtime_am017_518d8_006e\n    ldr r1, [r0, #8]\n    cmp r1, #4\n    beq L_open_cfw_runtime_am017_518d8_006e\n    ldr r1, [r0, #8]\n    cmp r1, #8\n    beq L_open_cfw_runtime_am017_518d8_006e\n    ldr r1, [r0, #8]\n    cmp r1, #9\n    beq L_open_cfw_runtime_am017_518d8_006e\n    ldr r1, [r0, #8]\n    cmp r1, #0xa\n    beq L_open_cfw_runtime_am017_518d8_006e\n    ldr r1, [r0, #8]\n    cmp r1, #0xb\n    beq L_open_cfw_runtime_am017_518d8_006e\n    ldr r1, [r0, #8]\n    cmp r1, #0xc\n    beq L_open_cfw_runtime_am017_518d8_006e\n    ldr r1, [r0, #8]\n    cmp r1, #0xe\n    beq L_open_cfw_runtime_am017_518d8_006e\n    ldr r1, [r0, #8]\n    cmp r1, #0xf\n    beq L_open_cfw_runtime_am017_518d8_006e\n    ldr r1, [r0, #8]\n    cmp r1, #0x10\n    beq L_open_cfw_runtime_am017_518d8_006e\n    ldr r1, [r0, #8]\n    cmp r1, #0x11\n    beq L_open_cfw_runtime_am017_518d8_006e\n    ldr r1, [r0, #8]\n    cmp r1, #0x13\n    beq L_open_cfw_runtime_am017_518d8_006e\n    ldr r1, [r0, #8]\n    cmp r1, #0x14\n    beq L_open_cfw_runtime_am017_518d8_006e\n    ldr r1, [r0, #8]\n    cmp r1, #0x15\n    beq L_open_cfw_runtime_am017_518d8_006e\n    ldr r1, [r0, #8]\n    cmp r1, #0x18\n    beq L_open_cfw_runtime_am017_518d8_006e\n    ldr r1, [r0, #8]\n    cmp r1, #0x19\n    bne L_open_cfw_runtime_am017_518d8_0074\nL_open_cfw_runtime_am017_518d8_006e:\n    ldr r0, [r0, #0x10]\n    mov r8, r8\n    b L_open_cfw_runtime_am017_518d8_0086\nL_open_cfw_runtime_am017_518d8_0074:\n    ldr r0, [pc, #0x104]\n    str r0, [sp]\n    ldr r3, [pc, #0x104]\n    movs r2, #0xd0\n    ldr r1, [pc, #0xe4]\n    movs r0, #2\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am017_addr_0044d25c\n    bl .\n    movs r0, #0\nL_open_cfw_runtime_am017_518d8_0086:\n    pop {r1, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM017_51960_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am017_51960(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    ldr r1, [r0, #8]\n    cmp r1, #0x1d\n    beq L_open_cfw_runtime_am017_51960_0026\n    ldr r1, [r0, #8]\n    cmp r1, #0x1c\n    beq L_open_cfw_runtime_am017_51960_0026\n    ldr r1, [r0, #8]\n    cmp r1, #0x1e\n    beq L_open_cfw_runtime_am017_51960_0026\n    ldr r1, [r0, #8]\n    cmp r1, #0x20\n    beq L_open_cfw_runtime_am017_51960_0026\n    ldr r1, [r0, #8]\n    cmp r1, #0x1f\n    beq L_open_cfw_runtime_am017_51960_0026\n    ldr r1, [r0, #8]\n    cmp r1, #0x21\n    bne L_open_cfw_runtime_am017_51960_002c\nL_open_cfw_runtime_am017_51960_0026:\n    ldr r0, [r0, #0x10]\n    mov r8, r8\n    b L_open_cfw_runtime_am017_51960_003e\nL_open_cfw_runtime_am017_51960_002c:\n    ldr r0, [pc, #0xc4]\n    str r0, [sp]\n    ldr r3, [pc, #0xc8]\n    movs r2, #0xe0\n    ldr r1, [pc, #0xa4]\n    movs r0, #2\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am017_addr_0044d25c\n    bl .\n    movs r0, #0\nL_open_cfw_runtime_am017_51960_003e:\n    pop {r1, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM017_519A0_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am017_519a0(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    ldr r1, [r0, #8]\n    cmp r1, #0x11\n    bne L_open_cfw_runtime_am017_519a0_0018\n    ldr r0, [r0, #0x10]\n    mov r8, r8\n    cmp r0, #0\n    beq L_open_cfw_runtime_am017_519a0_0014\n    ldr r0, [r0]\n    b L_open_cfw_runtime_am017_519a0_002a\nL_open_cfw_runtime_am017_519a0_0014:\n    movs r0, #0\n    b L_open_cfw_runtime_am017_519a0_002a\nL_open_cfw_runtime_am017_519a0_0018:\n    ldr r0, [pc, #0x98]\n    str r0, [sp]\n    ldr r3, [pc, #0xa0]\n    movs r2, #0xf8\n    ldr r1, [pc, #0x78]\n    movs r0, #2\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am017_addr_0044d25c\n    bl .\n    movs r0, #0\nL_open_cfw_runtime_am017_519a0_002a:\n    pop {r1, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM017_519CC_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am017_519cc(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    ldr r1, [r0, #8]\n    cmp r1, #0x12\n    bne L_open_cfw_runtime_am017_519cc_0018\n    ldr r0, [r0, #0x10]\n    mov r8, r8\n    cmp r0, #0\n    beq L_open_cfw_runtime_am017_519cc_0014\n    ldr r0, [r0]\n    b L_open_cfw_runtime_am017_519cc_002c\nL_open_cfw_runtime_am017_519cc_0014:\n    movs r0, #0\n    b L_open_cfw_runtime_am017_519cc_002c\nL_open_cfw_runtime_am017_519cc_0018:\n    ldr r0, [pc, #0x6c]\n    str r0, [sp]\n    ldr r3, [pc, #0x78]\n    movw r2, #0x105\n    ldr r1, [pc, #0x4c]\n    movs r0, #2\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am017_addr_0044d25c\n    bl .\n    movs r0, #0\nL_open_cfw_runtime_am017_519cc_002c:\n    pop {r1, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM017_519FA_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am017_519fa(void)
{
    __asm__ volatile(
        "    push {r2, r3, r4, lr}\n    movs r4, r1\n    ldr r1, [r0, #8]\n    cmp r1, #0x1b\n    bne L_open_cfw_runtime_am017_519fa_001c\n    ldr r0, [r0, #0x10]\n    mov r8, r8\n    ldr r1, [r0]\n    cmp r4, r1\n    bge L_open_cfw_runtime_am017_519fa_0018\n    ldr r4, [r0]\n    b L_open_cfw_runtime_am017_519fa_0018\nL_open_cfw_runtime_am017_519fa_0018:\n    str r4, [r0]\n    b L_open_cfw_runtime_am017_519fa_002e\nL_open_cfw_runtime_am017_519fa_001c:\n    ldr r0, [pc, #0x3c]\n    str r0, [sp]\n    ldr r3, [pc, #0x4c]\n    mov.w r2, #0x11c\n    ldr r1, [pc, #0x18]\n    movs r0, #2\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am017_addr_0044d25c\n    bl .\nL_open_cfw_runtime_am017_519fa_002e:\n    pop {r0, r1, r4, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM017_51A6C_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am017_51a6c(void)
{
    __asm__ volatile(
        "L_open_cfw_runtime_am017_51a6c_0000:\n    push {r4, r5, r6, lr}\n    movs r5, r0\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am017_addr_00452ef8\n    bl .\n    cmp r0, #0\n    beq L_open_cfw_runtime_am017_51a6c_0026\n    ldrb r0, [r5, #0x18]\n    ubfx r0, r0, #1, #1\n    uxtb r0, r0\n    cmp r0, #0\n    beq L_open_cfw_runtime_am017_51a6c_001c\n    movs r0, #1\n    b L_open_cfw_runtime_am017_51a6c_00c6\nL_open_cfw_runtime_am017_51a6c_001c:\n    ldrb r0, [r5, #0x18]\n    lsls r0, r0, #0x1f\n    bpl L_open_cfw_runtime_am017_51a6c_0026\n    movs r0, #0\n    b L_open_cfw_runtime_am017_51a6c_00c6\nL_open_cfw_runtime_am017_51a6c_0026:\n    ldr r1, [r5]\n    movs r0, #1\n    ldr r0, [r1, #8]\n    cmp r0, #0\n    beq L_open_cfw_runtime_am017_51a6c_0038\n    ldr r0, [r1, #8]\n    adds.w r4, r0, #8\n    b L_open_cfw_runtime_am017_51a6c_003a\nL_open_cfw_runtime_am017_51a6c_0038:\n    movs r4, #0\nL_open_cfw_runtime_am017_51a6c_003a:\n    movs r2, #1\n    movs r1, r5\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am017_addr_0044ffe6\n    bl .\n    movs r1, r0\n    uxtb r1, r1\n    cmp r1, #1\n    bne L_open_cfw_runtime_am017_51a6c_0058\n    ldrb r1, [r5, #0x18]\n    ubfx r1, r1, #1, #1\n    uxtb r1, r1\n    cmp r1, #0\n    beq L_open_cfw_runtime_am017_51a6c_005c\nL_open_cfw_runtime_am017_51a6c_0058:\n    uxtb r0, r0\n    b L_open_cfw_runtime_am017_51a6c_00c6\nL_open_cfw_runtime_am017_51a6c_005c:\n    movs r1, r5\n    movs r0, #0\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am017_516f8\n    bl .\n    movs r1, r0\n    uxtb r1, r1\n    cmp r1, #1\n    bne L_open_cfw_runtime_am017_51a6c_0078\n    ldrb r1, [r5, #0x18]\n    ubfx r1, r1, #1, #1\n    uxtb r1, r1\n    cmp r1, #0\n    beq L_open_cfw_runtime_am017_51a6c_007c\nL_open_cfw_runtime_am017_51a6c_0078:\n    uxtb r0, r0\n    b L_open_cfw_runtime_am017_51a6c_00c6\nL_open_cfw_runtime_am017_51a6c_007c:\n    movs r2, #0\n    movs r1, r5\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am017_addr_0044ffe6\n    bl .\n    movs r6, r0\n    movs r0, r6\n    uxtb r0, r0\n    cmp r0, #1\n    bne L_open_cfw_runtime_am017_51a6c_009c\n    ldrb r0, [r5, #0x18]\n    ubfx r0, r0, #1, #1\n    uxtb r0, r0\n    cmp r0, #0\n    beq L_open_cfw_runtime_am017_51a6c_00a2\nL_open_cfw_runtime_am017_51a6c_009c:\n    movs r0, r6\n    uxtb r0, r0\n    b L_open_cfw_runtime_am017_51a6c_00c6\nL_open_cfw_runtime_am017_51a6c_00a2:\n    ldr r0, [r5]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am017_addr_0044dca2\n    bl .\n    movs r4, r0\n    cmp r4, #0\n    beq L_open_cfw_runtime_am017_51a6c_00c2\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am017_addr_00451b34\n    bl .\n    cmp r0, #0\n    beq L_open_cfw_runtime_am017_51a6c_00c2\n    str r4, [r5]\n    movs r0, r5\n    bl L_open_cfw_runtime_am017_51a6c_0000\n    movs r6, r0\nL_open_cfw_runtime_am017_51a6c_00c2:\n    movs r0, r6\n    uxtb r0, r0\nL_open_cfw_runtime_am017_51a6c_00c6:\n    pop {r4, r5, r6, pc}\n"
    );
}
#endif
