/*
 * SPDX-License-Identifier: MIT
 *
 * Source-owned exact helpers from the AM-010 retained island.
 */

#if defined(OPEN_CFW_AM010_4AA98_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am010_4aa98(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am010_addr_0044aa40\n    bl .\n    pop {r0, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM010_4AAA0_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am010_4aaa0(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am010_addr_0044aa56\n    bl .\n    pop {r0, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM010_4AAA8_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am010_4aaa8(void)
{
    __asm__ volatile(
        "    push {r4, lr}\n    sub sp, #0x40\n    add r0, sp, #0x18\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am010_addr_0044a19a\n    bl .\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am010_addr_004490cc\n    bl .\n    ldr r4, [pc, #0x50]\n    str r0, [sp, #0x14]\n    ldr r0, [sp, #0x38]\n    str r0, [sp, #0x10]\n    ldr r0, [sp, #0x34]\n    str r0, [sp, #0xc]\n    ldr r0, [sp, #0x30]\n    str r0, [sp, #8]\n    ldr r0, [sp, #0x2c]\n    str r0, [sp, #4]\n    ldr r0, [sp, #0x28]\n    str r0, [sp]\n    ldr r3, [sp, #0x24]\n    ldr r2, [pc, #0x38]\n    movs r1, #0x1c\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am010_4b728\n    bl .\n    movs r0, r4\n    add sp, #0x40\n    pop {r4, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM010_4AAE0_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am010_4aae0(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am010_addr_004558a4\n    bl .\n    cmp r0, #1\n    beq L_open_cfw_runtime_am010_4aae0_0014\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am010_addr_0045589c\n    bl .\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am010_addr_00454f16\n    bl .\n    b L_open_cfw_runtime_am010_4aae0_0016\nL_open_cfw_runtime_am010_4aae0_0014:\n    ldr r0, [pc, #0x18]\nL_open_cfw_runtime_am010_4aae0_0016:\n    pop {r1, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM010_4AB14_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am010_4ab14(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am010_4aae0\n    bl .\n    pop {r1, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM010_4AB1C_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am010_4ab1c(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am010_4aae0\n    bl .\n    pop {r1, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM010_4AB24_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am010_4ab24(void)
{
    __asm__ volatile(
        "    dsb sy\n    ldr.w r1, [pc, #0x9c8]\n    ldr r2, [r1]\n    ands r2, r2, #0x700\n    ldr.w r0, [pc, #0x9c4]\n    orrs r2, r0\n    str r2, [r1]\n    dsb sy\nL_open_cfw_runtime_am010_4ab24_001a:\n    nop\n    b L_open_cfw_runtime_am010_4ab24_001a\n"
    );
}
#endif

#if defined(OPEN_CFW_AM010_4AB42_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am010_4ab42(void)
{
    __asm__ volatile(
        "    push.w {r0, r4, r5, r6, r7, r8, sb, sl, fp, lr}\n    sub sp, #0x18\n    movs r7, #0\n    movs r0, #0\n    movs r6, #0\n    movs r5, #0\n    movs.w sl, #0\n    movs.w sb, #0\n    movs.w fp, #0\n    movs r0, #0x62\n    str r0, [sp, #0x10]\n    movs.w r8, #0\n    movs r4, #0\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am010_addr_00473940\n    bl .\n    str r0, [sp, #0xc]\n    add r0, sp, #4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am010_addr_00480008\n    bl .\n    ldrb.w r0, [sp, #4]\n    orrs.w fp, fp, r0, lsl #8\n    ldrb.w r0, [sp, #5]\n    orrs.w fp, fp, r0, lsl #4\n    ldrb.w r0, [sp, #6]\n    orrs.w fp, r0, fp\n    str.w fp, [sp, #0x14]\n    ldr.w r0, [pc, #0x970]\n    ldr r0, [r0]\n    ubfx r0, r0, #4, #2\n    cmp r0, #3\n    bne L_open_cfw_runtime_am010_4ab42_0060\n    movs.w fp, #1\n    b L_open_cfw_runtime_am010_4ab42_0064\nL_open_cfw_runtime_am010_4ab42_0060:\n    movs.w fp, #0\nL_open_cfw_runtime_am010_4ab42_0064:\n    ldrb.w r0, [sp, #0x18]\n    cmp r0, #1\n    bne.w #0x44ad8c\n    ldr.w r0, [pc, #0x950]\n    ldr r0, [r0]\n    ubfx r0, r0, #0x1b, #1\n    cmp r0, #0\n    bne.w #0x44ad8c\n    ldr.w r0, [pc, #0x944]\n    ldr r0, [r0]\n    str r0, [sp, #8]\n    ldrb.w r0, [sp, #4]\n    strb.w r0, [sp, #8]\n    ldrb.w r0, [sp, #5]\n    cmp r0, #3\n    bne L_open_cfw_runtime_am010_4ab42_009c\n    movs r0, #3\n    strb.w r0, [sp, #9]\nL_open_cfw_runtime_am010_4ab42_009c:\n    ldr r0, [sp, #8]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am010_addr_0047ffc4\n    bl .\n    movs r0, #2\n    strb.w r0, [sp]\n    mov r2, sp\n    movs r1, #0\n    movs r0, #0\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am010_addr_00480312\n    bl .\n    ldr.w r0, [pc, #0x914]\n    ldr r0, [r0]\n    ands r0, r0, #3\n    cmp r0, #2\n    beq L_open_cfw_runtime_am010_4ab42_00c8\n    movs r0, #0\n    strb.w r0, [sp]\n    b L_open_cfw_runtime_am010_4ab42_00ce\nL_open_cfw_runtime_am010_4ab42_00c8:\n    movs r0, #1\n    strb.w r0, [sp]\nL_open_cfw_runtime_am010_4ab42_00ce:\n    movs r5, #1\n    uxtb.w fp, fp\n    cmp.w fp, #0\n    beq L_open_cfw_runtime_am010_4ab42_014e\n    ldr.w r0, [pc, #0x8f0]\n    ldr r1, [r0]\n    and r1, r1, #0xff\n    cmp r1, #0x22\n    bne L_open_cfw_runtime_am010_4ab42_00f2\n    ldr.w r1, [pc, #0x8e8]\n    ldr r1, [r1]\n    cmp r1, #2\n    bhs L_open_cfw_runtime_am010_4ab42_012c\nL_open_cfw_runtime_am010_4ab42_00f2:\n    ldr r0, [r0]\n    and r0, r0, #0xff\n    cmp r0, #0x23\n    bne L_open_cfw_runtime_am010_4ab42_0106\n    ldr.w r0, [pc, #0x8d4]\n    ldr r0, [r0]\n    cmp r0, #0\n    bne L_open_cfw_runtime_am010_4ab42_012c\nL_open_cfw_runtime_am010_4ab42_0106:\n    ldr.w r0, [pc, #0x8cc]\n    ldr r0, [r0]\n    movw r1, #0x4c4\n    tst r0, r1\n    bne L_open_cfw_runtime_am010_4ab42_014e\n    ldr.w r0, [pc, #0x8ac]\n    ldr r0, [r0]\n    lsls r0, r0, #2\n    bne L_open_cfw_runtime_am010_4ab42_014e\n    ldr.w r0, [pc, #0x8b8]\n    ldr r0, [r0]\n    ubfx r0, r0, #0x1d, #1\n    cmp r0, #0\n    bne L_open_cfw_runtime_am010_4ab42_014e\nL_open_cfw_runtime_am010_4ab42_012c:\n    movs r6, #1\n    ldr.w r0, [pc, #0x888]\n    ldrb r0, [r0]\n    cmp r0, #0\n    bne L_open_cfw_runtime_am010_4ab42_014e\n    ldr.w r0, [pc, #0x8a4]\n    ldrb r0, [r0]\n    cmp r0, #0\n    bne L_open_cfw_runtime_am010_4ab42_014e\n    movs r7, #1\n    movs r0, #0\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am010_addr_0047fe6c\n    bl .\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am010_addr_00480408\n    bl .\nL_open_cfw_runtime_am010_4ab42_014e:\n    ldr.w r0, [pc, #0x890]\n    ldr r1, [r0]\n    orrs r1, r1, #4\n    str r1, [r0]\n    ldr.w fp, [pc, #0x86c]\n    ldr.w r0, [fp]\n    ands r0, r0, #3\n    cmp r0, #2\n    bne L_open_cfw_runtime_am010_4ab42_017e\n    b L_open_cfw_runtime_am010_4ab42_0172\nL_open_cfw_runtime_am010_4ab42_016c:\n    movs r0, #1\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am010_addr_004807a0\n    bl .\nL_open_cfw_runtime_am010_4ab42_0172:\n    ldr.w r0, [fp]\n    ubfx r0, r0, #3, #2\n    cmp r0, #2\n    bne L_open_cfw_runtime_am010_4ab42_016c\nL_open_cfw_runtime_am010_4ab42_017e:\n    ldr.w r0, [pc, #0x864]\n    ldrb r0, [r0]\n    cmp r0, #0\n    beq L_open_cfw_runtime_am010_4ab42_01ee\n    ldr.w r0, [pc, #0x860]\n    ldr.w r1, [pc, #0x860]\n    ldr r1, [r1, #0x68]\n    lsrs r1, r1, #0x14\n    ldr r2, [r0]\n    bfi r2, r1, #0, #5\n    str r2, [r0]\n    ldr.w r1, [pc, #0x854]\n    ldrb r0, [r1]\n    cmp r0, #0\n    beq L_open_cfw_runtime_am010_4ab42_01ba\n    ldr.w r0, [pc, #0x84c]\n    ldr r2, [r0]\n    bics r2, r2, #8\n    str r2, [r0]\n    ldr r2, [r0]\n    bics r2, r2, #0x40\n    str r2, [r0]\nL_open_cfw_runtime_am010_4ab42_01ba:\n    ldr.w r0, [pc, #0x83c]\n    ldrb r0, [r0]\n    cmp r0, #0\n    beq L_open_cfw_runtime_am010_4ab42_01ca\n    ldrb r0, [r1]\n    cmp r0, #0\n    bne L_open_cfw_runtime_am010_4ab42_01e4\nL_open_cfw_runtime_am010_4ab42_01ca:\n    ldr.w r0, [pc, #0x830]\n    ldrb r0, [r0]\n    cmp r0, #0\n    beq L_open_cfw_runtime_am010_4ab42_01ea\n    ldrb r0, [r1]\n    cmp r0, #0\n    beq L_open_cfw_runtime_am010_4ab42_01ea\n    ldr.w r0, [pc, #0x824]\n    ldrb r0, [r0]\n    cmp r0, #0\n    bne L_open_cfw_runtime_am010_4ab42_01ea\nL_open_cfw_runtime_am010_4ab42_01e4:\n    movs.w r8, #1\n    b L_open_cfw_runtime_am010_4ab42_01ee\nL_open_cfw_runtime_am010_4ab42_01ea:\n    movs.w r8, #0\nL_open_cfw_runtime_am010_4ab42_01ee:\n    ldr.w r0, [pc, #0x814]\n    ldrb r0, [r0]\n    cmp r0, #0\n    beq L_open_cfw_runtime_am010_4ab42_0206\n    ldr.w r0, [pc, #0x7f0]\n    movs r1, #0xb\n    ldr r2, [r0]\n    bfi r2, r1, #0, #5\n    str r2, [r0]\nL_open_cfw_runtime_am010_4ab42_0206:\n    ldr.w r1, [pc, #0x7e4]\n    ldr r0, [r1]\n    ldr.w r2, [pc, #0x7fc]\n    cmp r0, r2\n    bne L_open_cfw_runtime_am010_4ab42_02ac\n    ldr.w r0, [pc, #0x7e8]\n    ldrb r0, [r0]\n    cmp r0, #0\n    beq L_open_cfw_runtime_am010_4ab42_02ac\n    ldr.w r0, [pc, #0x7ec]\n    ldr r2, [r1, #0x54]\n    ubfx r2, r2, #5, #5\n    ldr r3, [r0]\n    ubfx r3, r3, #0x19, #5\n    cmp r2, r3\n    bge L_open_cfw_runtime_am010_4ab42_02ac\n    ldr r2, [r0]\n    ubfx sb, r2, #0x19, #5\n    ldr r1, [r1, #0x54]\n    lsrs r1, r1, #5\n    ldr r2, [r0]\n    bfi r2, r1, #0x19, #5\n    str r2, [r0]\n    movs.w sl, #1\n    b L_open_cfw_runtime_am010_4ab42_02ac\n    ldr.w r0, [pc, #0x7c4]\n    ldr r0, [r0]\n    ubfx r0, r0, #2, #1\n    cmp r0, #0\n    bne L_open_cfw_runtime_am010_4ab42_026e\n    ldrb.w r0, [sp, #4]\n    strb.w r0, [sp, #8]\n    movs r0, #1\n    strb.w r0, [sp, #9]\n    movs r0, #1\n    strb.w r0, [sp, #0xa]\n    b L_open_cfw_runtime_am010_4ab42_0282\nL_open_cfw_runtime_am010_4ab42_026e:\n    ldrb.w r0, [sp, #4]\n    strb.w r0, [sp, #8]\n    movs r0, #1\n    strb.w r0, [sp, #9]\n    movs r0, #1\n    strb.w r0, [sp, #0xa]\nL_open_cfw_runtime_am010_4ab42_0282:\n    ldrb.w r0, [sp, #5]\n    cmp r0, #3\n    beq L_open_cfw_runtime_am010_4ab42_0292\n    ldrb.w r0, [sp, #5]\n    cmp r0, #2\n    bne L_open_cfw_runtime_am010_4ab42_029a\nL_open_cfw_runtime_am010_4ab42_0292:\n    ldrb.w r0, [sp, #5]\n    strb.w r0, [sp, #9]\nL_open_cfw_runtime_am010_4ab42_029a:\n    ldr r0, [sp, #8]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am010_addr_0047ffc4\n    bl .\n    ldr.w r0, [pc, #0x740]\n    ldr r1, [r0]\n    bics r1, r1, #4\n    str r1, [r0]\nL_open_cfw_runtime_am010_4ab42_02ac:\n    ldr.w r0, [pc, #0x768]\n    ldr r0, [r0]\n    mov r8, r8\n    mov r8, r8\n    wfi\n    isb sy\n    mov r0, sl\n    uxtb r0, r0\n    cmp r0, #0\n    beq L_open_cfw_runtime_am010_4ab42_02d0\n    ldr.w r0, [pc, #0x748]\n    ldr r1, [r0]\n    bfi r1, sb, #0x19, #5\n    str r1, [r0]\nL_open_cfw_runtime_am010_4ab42_02d0:\n    ldr.w r0, [pc, #0x714]\n    ldrb r0, [r0]\n    cmp r0, #0\n    beq L_open_cfw_runtime_am010_4ab42_0302\n    mov r0, r8\n    uxtb r0, r0\n    cmp r0, #0\n    beq L_open_cfw_runtime_am010_4ab42_02f6\n    ldr.w r0, [pc, #0x710]\n    ldr r1, [r0]\n    orrs r1, r1, #8\n    str r1, [r0]\n    ldr r1, [r0]\n    orrs r1, r1, #0x40\n    str r1, [r0]\nL_open_cfw_runtime_am010_4ab42_02f6:\n    ldr.w r0, [pc, #0x6f0]\n    ldr r1, [r0]\n    lsrs r1, r1, #5\n    lsls r1, r1, #5\n    str r1, [r0]\nL_open_cfw_runtime_am010_4ab42_0302:\n    ldr.w fp, [pc, #0x700]\n    ldrb.w r0, [fp]\n    cmp r0, #0\n    beq L_open_cfw_runtime_am010_4ab42_031a\n    ldr.w r0, [pc, #0x6d8]\n    ldr r1, [r0]\n    lsrs r1, r1, #5\n    lsls r1, r1, #5\n    str r1, [r0]\nL_open_cfw_runtime_am010_4ab42_031a:\n    ldr.w r0, [pc, #0x6e0]\n    ldrb r0, [r0]\n    cmp r0, #0\n    bne L_open_cfw_runtime_am010_4ab42_0330\n    ldr.w r0, [pc, #0x6d4]\n    ldrb r0, [r0]\n    cmp r0, #0\n    beq.w #0x44affa\nL_open_cfw_runtime_am010_4ab42_0330:\n    ldr.w r0, [pc, #0x6e8]\n    ldr r0, [r0]\n    ubfx r0, r0, #0xc, #9\n    ldr r1, [sp, #0x10]\n    cmp r0, r1\n    bne.w #0x44affa\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am010_addr_0048039a\n    bl .\n    ldr.w r0, [pc, #0x6d0]\n    ldr r0, [r0]\n    lsls r0, r0, #0xb\n    lsrs r0, r0, #0x17\n    cmp r0, #0\n    bne.w #0x44affa\n    ldrb.w r0, [sp, #0x18]\n    cmp r0, #1\n    bne L_open_cfw_runtime_am010_4ab42_0392\n    ldr.w r0, [pc, #0x668]\n    ldr r0, [r0]\n    ands r0, r0, #3\n    cmp r0, #2\n    bne L_open_cfw_runtime_am010_4ab42_0392\n    b L_open_cfw_runtime_am010_4ab42_0374\nL_open_cfw_runtime_am010_4ab42_036e:\n    movs r0, #1\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am010_addr_004807a0\n    bl .\nL_open_cfw_runtime_am010_4ab42_0374:\n    ldr.w r0, [pc, #0x654]\n    ldr r0, [r0]\n    ubfx r0, r0, #3, #2\n    cmp r0, #2\n    beq L_open_cfw_runtime_am010_4ab42_0392\n    ldr.w r0, [pc, #0x694]\n    ldr r0, [r0]\n    lsls r0, r0, #0xb\n    lsrs r0, r0, #0x17\n    cmp r0, #0\n    beq L_open_cfw_runtime_am010_4ab42_036e\n    movs r4, #1\nL_open_cfw_runtime_am010_4ab42_0392:\n    uxtb r4, r4\n    cmp r4, #0\n    bne.w #0x44affa\n    movs r0, r5\n    uxtb r0, r0\n    cmp r0, #0\n    beq L_open_cfw_runtime_am010_4ab42_03be\n    mov r2, sp\n    movs r1, #0\n    movs r0, #0\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am010_addr_00480312\n    bl .\n    movs r0, #2\n    strb.w r0, [sp, #1]\n    add.w r2, sp, #1\n    movs r1, #0\n    movs r0, #0\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am010_addr_00480312\n    bl .\nL_open_cfw_runtime_am010_4ab42_03be:\n    uxtb r6, r6\n    cmp r6, #0\n    beq L_open_cfw_runtime_am010_4ab42_03e4\n    ldr.w r0, [pc, #0x5f4]\n    ldrb r0, [r0]\n    cmp r0, #0\n    bne L_open_cfw_runtime_am010_4ab42_03e4\n    ldr.w r0, [pc, #0x60c]\n    ldrb r0, [r0]\n    cmp r0, #0\n    bne L_open_cfw_runtime_am010_4ab42_03e4\n    movs r7, #1\n    movs r0, #0\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am010_addr_0047fe6c\n    bl .\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am010_addr_00480408\n    bl .\nL_open_cfw_runtime_am010_4ab42_03e4:\n    ldr.w r1, [pc, #0x600]\n    ldrb r0, [r1]\n    cmp r0, #0\n    beq L_open_cfw_runtime_am010_4ab42_0420\n    ldr.w r0, [pc, #0x5f8]\n    ldr.w r2, [pc, #0x5f8]\n    ldr r2, [r2, #0x68]\n    lsrs r2, r2, #0x14\n    ldr r3, [r0]\n    bfi r3, r2, #0, #5\n    str r3, [r0]\n    ldr.w r0, [pc, #0x5ec]\n    ldrb r0, [r0]\n    cmp r0, #0\n    beq L_open_cfw_runtime_am010_4ab42_0420\n    ldr.w r0, [pc, #0x5e8]\n    ldr r2, [r0]\n    bics r2, r2, #8\n    str r2, [r0]\n    ldr r2, [r0]\n    bics r2, r2, #0x40\n    str r2, [r0]\nL_open_cfw_runtime_am010_4ab42_0420:\n    ldrb.w r0, [fp]\n    cmp r0, #0\n    beq L_open_cfw_runtime_am010_4ab42_0436\n    ldr.w r0, [pc, #0x5c0]\n    movs r2, #0xb\n    ldr r3, [r0]\n    bfi r3, r2, #0, #5\n    str r3, [r0]\nL_open_cfw_runtime_am010_4ab42_0436:\n    mov r0, sl\n    uxtb r0, r0\n    cmp r0, #0\n    beq L_open_cfw_runtime_am010_4ab42_0452\n    ldr.w r0, [pc, #0x5cc]\n    ldr.w r2, [pc, #0x5a8]\n    ldr r2, [r2, #0x54]\n    lsrs r2, r2, #5\n    ldr r3, [r0]\n    bfi r3, r2, #0x19, #5\n    str r3, [r0]\nL_open_cfw_runtime_am010_4ab42_0452:\n    ldr.w r0, [pc, #0x5c0]\n    ldr r0, [r0]\n    wfi\n    isb sy\n    uxtb.w sl, sl\n    cmp.w sl, #0\n    beq L_open_cfw_runtime_am010_4ab42_0474\n    ldr.w r0, [pc, #0x5a4]\n    ldr r2, [r0]\n    bfi r2, sb, #0x19, #5\n    str r2, [r0]\nL_open_cfw_runtime_am010_4ab42_0474:\n    ldrb r0, [r1]\n    cmp r0, #0\n    beq L_open_cfw_runtime_am010_4ab42_04a4\n    uxtb.w r8, r8\n    cmp.w r8, #0\n    beq L_open_cfw_runtime_am010_4ab42_0498\n    ldr.w r0, [pc, #0x570]\n    ldr r1, [r0]\n    orrs r1, r1, #8\n    str r1, [r0]\n    ldr r1, [r0]\n    orrs r1, r1, #0x40\n    str r1, [r0]\nL_open_cfw_runtime_am010_4ab42_0498:\n    ldr.w r0, [pc, #0x550]\n    ldr r1, [r0]\n    lsrs r1, r1, #5\n    lsls r1, r1, #5\n    str r1, [r0]\nL_open_cfw_runtime_am010_4ab42_04a4:\n    ldrb.w r0, [fp]\n    cmp r0, #0\n    beq L_open_cfw_runtime_am010_4ab42_04b8\n    ldr.w r0, [pc, #0x53c]\n    ldr r1, [r0]\n    lsrs r1, r1, #5\n    lsls r1, r1, #5\n    str r1, [r0]\nL_open_cfw_runtime_am010_4ab42_04b8:\n    ldr.w r1, [pc, #0x52c]\n    ldrb r0, [r1]\n    cmp r0, #0\n    beq L_open_cfw_runtime_am010_4ab42_04ce\n    movs r0, #0\n    strb r0, [r1]\n    movs r0, #0\n    ldr.w r1, [pc, #0x528]\n    strb r0, [r1]\nL_open_cfw_runtime_am010_4ab42_04ce:\n    ldrb.w r0, [fp]\n    cmp r0, #0\n    beq L_open_cfw_runtime_am010_4ab42_04dc\n    movs r0, #0\n    strb.w r0, [fp]\nL_open_cfw_runtime_am010_4ab42_04dc:\n    uxtb r5, r5\n    cmp r5, #0\n    beq L_open_cfw_runtime_am010_4ab42_04ec\n    mov r2, sp\n    movs r1, #0\n    movs r0, #0\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am010_addr_00480312\n    bl .\nL_open_cfw_runtime_am010_4ab42_04ec:\n    uxtb r7, r7\n    cmp r7, #0\n    beq L_open_cfw_runtime_am010_4ab42_050e\n    ldr.w r0, [pc, #0x528]\n    ldr r1, [r0]\n    orrs r1, r1, #0x10000\n    str r1, [r0]\n    ldr r1, [r0]\n    orrs r1, r1, #1\n    str r1, [r0]\n    ldr r1, [r0]\n    orrs r1, r1, #0x20\n    str r1, [r0]\nL_open_cfw_runtime_am010_4ab42_050e:\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am010_addr_0048041e\n    bl .\n    ldr r0, [sp, #0x14]\n    ldr.w r1, [pc, #0x50c]\n    str r0, [r1]\n    ldr r0, [sp, #0xc]\n    msr primask, r0\n    add sp, #0x1c\n    pop.w {r4, r5, r6, r7, r8, sb, sl, fp, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM010_4B0AE_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am010_4b0ae(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am010_4ab24\n    bl .\n    pop {r0, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM010_4B0B6_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am010_4b0b6(void)
{
    __asm__ volatile(
        "    push {r2, r3, r4, lr}\n    movs r4, r0\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am010_addr_00473940\n    bl .\n    str r0, [sp]\n    ldr.w r0, [pc, #0x4ac]\n    uxtb r4, r4\n    ldr r1, [r0]\n    bfi r1, r4, #6, #1\n    str r1, [r0]\n    ldr r0, [sp]\n    msr primask, r0\n    pop {r0, r1, r4, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM010_4B0D6_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am010_4b0d6(void)
{
    __asm__ volatile(
        "    push {r2, r3, r4, r5, r6, lr}\n    movs r5, r0\n    movs r6, r1\n    movs r4, #0\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am010_addr_00473940\n    bl .\n    str r0, [sp]\n    ldr.w r2, [pc, #0x48c]\n    uxtb r5, r5\n    strb r6, [r2, r5]\n    movs r1, #0\n    b L_open_cfw_runtime_am010_4b0d6_0024\nL_open_cfw_runtime_am010_4b0d6_001a:\n    movs r0, r1\n    uxtb r0, r0\n    ldrb r0, [r2, r0]\n    orrs r4, r0\n    adds r1, r1, #1\nL_open_cfw_runtime_am010_4b0d6_0024:\n    movs r0, r1\n    uxtb r0, r0\n    cmp r0, #6\n    blt L_open_cfw_runtime_am010_4b0d6_001a\n    ldr.w r0, [pc, #0x46c]\n    movs r1, r4\n    uxtb r1, r1\n    ldr r2, [r0]\n    bfi r2, r1, #1, #1\n    str r2, [r0]\n    movs r1, r4\n    uxtb r1, r1\n    lsrs r1, r1, #1\n    uxtb r1, r1\n    ldr r2, [r0]\n    bfi r2, r1, #2, #1\n    str r2, [r0]\n    movs r1, r4\n    uxtb r1, r1\n    lsrs r1, r1, #2\n    uxtb r1, r1\n    ldr r2, [r0]\n    bfi r2, r1, #3, #1\n    str r2, [r0]\n    movs r1, r4\n    uxtb r1, r1\n    lsrs r1, r1, #3\n    uxtb r1, r1\n    ldr r2, [r0]\n    bfi r2, r1, #4, #1\n    str r2, [r0]\n    uxtb r4, r4\n    lsrs r4, r4, #4\n    uxtb r4, r4\n    ldr r1, [r0]\n    bfi r1, r4, #5, #1\n    str r1, [r0]\n    ldr r0, [sp]\n    msr primask, r0\n    pop {r0, r1, r4, r5, r6, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM010_4B158_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am010_4b158(void)
{
    __asm__ volatile(
        "    push.w {r1, r2, r3, r4, r5, r6, r7, r8, sb, lr}\n    ldr.w r0, [pc, #0x418]\n    ldr r0, [r0]\n    ubfx r0, r0, #1, #1\n    cmp r0, #0\n    bne L_open_cfw_runtime_am010_4b158_0026\n    ldr.w r0, [pc, #0x404]\n    ldr r0, [r0]\n    lsrs r0, r0, #0x10\n    movw r1, #0x5af0\n    cmp r0, r1\n    bne L_open_cfw_runtime_am010_4b158_0026\n    movs r0, #1\n    b L_open_cfw_runtime_am010_4b158_0028\nL_open_cfw_runtime_am010_4b158_0026:\n    movs r0, #0\nL_open_cfw_runtime_am010_4b158_0028:\n    uxtb r0, r0\n    cmp r0, #0\n    beq.w #0x44b4dc\n    ldr.w r4, [pc, #0x3e4]\n    ldr r0, [r4]\n    lsls r0, r0, #0x1f\n    bmi L_open_cfw_runtime_am010_4b158_006e\n    ldr r0, [r4]\n    ubfx r0, r0, #1, #1\n    cmp r0, #0\n    bne L_open_cfw_runtime_am010_4b158_006e\n    ldr r0, [r4]\n    ubfx r0, r0, #2, #1\n    cmp r0, #0\n    bne L_open_cfw_runtime_am010_4b158_006e\n    ldr r0, [r4]\n    ubfx r0, r0, #3, #1\n    cmp r0, #0\n    bne L_open_cfw_runtime_am010_4b158_006e\n    ldr r0, [r4]\n    ubfx r0, r0, #4, #1\n    cmp r0, #0\n    bne L_open_cfw_runtime_am010_4b158_006e\n    ldr r0, [r4]\n    ubfx r0, r0, #5, #1\n    ands r0, r0, #1\n    b L_open_cfw_runtime_am010_4b158_0070\nL_open_cfw_runtime_am010_4b158_006e:\n    movs r0, #1\nL_open_cfw_runtime_am010_4b158_0070:\n    uxtb r0, r0\n    cmp r0, #0\n    beq.w #0x44b4dc\n    ldr r0, [r4]\n    lsls r0, r0, #0x1f\n    bmi L_open_cfw_runtime_am010_4b158_008a\n    ldr r0, [r4]\n    ubfx r0, r0, #1, #1\n    ands r0, r0, #1\n    b L_open_cfw_runtime_am010_4b158_008c\nL_open_cfw_runtime_am010_4b158_008a:\n    movs r0, #1\nL_open_cfw_runtime_am010_4b158_008c:\n    uxtb r0, r0\n    cmp r0, #0\n    beq L_open_cfw_runtime_am010_4b158_009e\n    ldr.w r0, [pc, #0x390]\n    ldr r1, [r0]\n    orrs r1, r1, #1\n    str r1, [r0]\nL_open_cfw_runtime_am010_4b158_009e:\n    ldr r0, [r4]\n    lsls r0, r0, #0x1f\n    bpl L_open_cfw_runtime_am010_4b158_00bc\n    ldr.w r0, [pc, #0x380]\n    movs r1, #1\n    ldr r2, [r0]\n    bfi r2, r1, #2, #2\n    str r2, [r0]\n    ldr r0, [pc, #0x34c]\n    ldr r0, [r0]\n    movs r0, #1\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am010_addr_004807a0\n    bl .\nL_open_cfw_runtime_am010_4b158_00bc:\n    ldr r0, [r4]\n    ubfx r0, r0, #2, #1\n    cmp r0, #0\n    beq L_open_cfw_runtime_am010_4b158_00ea\n    ldr r0, [pc, #0x364]\n    ldr r1, [r0]\n    orrs r1, r1, #0x20\n    str r1, [r0]\n    movs r0, #1\n    str r0, [sp]\n    movs.w r3, #0x1000000\n    movs.w r2, #0x1000000\n    ldr r1, [pc, #0x350]\n    movs r0, #0xc8\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am010_addr_00480826\n    bl .\n    movs r0, #5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am010_addr_004807a0\n    bl .\nL_open_cfw_runtime_am010_4b158_00ea:\n    ldr r0, [r4]\n    ubfx r0, r0, #3, #1\n    cmp r0, #0\n    bne L_open_cfw_runtime_am010_4b158_0112\n    ldr r0, [r4]\n    ubfx r0, r0, #5, #1\n    cmp r0, #0\n    beq L_open_cfw_runtime_am010_4b158_010a\n    ldr r0, [r4]\n    ubfx r0, r0, #6, #1\n    ands r0, r0, #1\n    b L_open_cfw_runtime_am010_4b158_010c\nL_open_cfw_runtime_am010_4b158_010a:\n    movs r0, #1\nL_open_cfw_runtime_am010_4b158_010c:\n    eors r0, r0, #1\n    b L_open_cfw_runtime_am010_4b158_0114\nL_open_cfw_runtime_am010_4b158_0112:\n    movs r0, #1\nL_open_cfw_runtime_am010_4b158_0114:\n    uxtb r0, r0\n    cmp r0, #0\n    beq L_open_cfw_runtime_am010_4b158_0132\n    movs r0, #0\n    strb.w r0, [sp, #1]\n    add.w r1, sp, #1\n    movs r0, #2\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am010_addr_004809c4\n    bl .\n    movw r0, #0x5dc\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am010_addr_004807a0\n    bl .\nL_open_cfw_runtime_am010_4b158_0132:\n    ldr r0, [r4]\n    ubfx r0, r0, #4, #1\n    cmp r0, #0\n    bne L_open_cfw_runtime_am010_4b158_015e\n    ldr r0, [r4]\n    ubfx r0, r0, #5, #1\n    cmp r0, #0\n    beq L_open_cfw_runtime_am010_4b158_0156\n    ldr r0, [r4]\n    ubfx r0, r0, #6, #1\n    ands r0, r0, #1\n    eors r0, r0, #1\n    b L_open_cfw_runtime_am010_4b158_0158\nL_open_cfw_runtime_am010_4b158_0156:\n    movs r0, #1\nL_open_cfw_runtime_am010_4b158_0158:\n    eors r0, r0, #1\n    b L_open_cfw_runtime_am010_4b158_0160\nL_open_cfw_runtime_am010_4b158_015e:\n    movs r0, #1\nL_open_cfw_runtime_am010_4b158_0160:\n    uxtb r0, r0\n    cmp r0, #0\n    beq L_open_cfw_runtime_am010_4b158_017c\n    movs r0, #0xa\n    bfi r5, r0, #0, #4\n    add r1, sp, #4\n    movs r0, #0xf\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am010_addr_00480eee\n    bl .\n    movs r1, r5\n    movs r0, #0xf\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am010_addr_00480f0c\n    bl .\nL_open_cfw_runtime_am010_4b158_017c:\n    ldr r0, [r4]\n    ubfx r0, r0, #5, #1\n    cmp r0, #0\n    beq L_open_cfw_runtime_am010_4b158_01ba\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am010_addr_00480058\n    bl .\n    ldr r0, [pc, #0x238]\n    ldr r1, [r0]\n    bics r1, r1, #2\n    str r1, [r0]\n    ldr r1, [r0]\n    bics r1, r1, #4\n    str r1, [r0]\n    ldr r1, [r4]\n    ubfx r1, r1, #6, #1\n    ldr r2, [r0]\n    bfi r2, r1, #5, #1\n    str r2, [r0]\n    ldr r1, [r0]\n    orrs r1, r1, #0x100\n    str r1, [r0]\n    ldr r1, [r0]\n    orrs r1, r1, #0x20000000\n    str r1, [r0]\nL_open_cfw_runtime_am010_4b158_01ba:\n    movs r0, #0x1e\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am010_addr_0047f5b8\n    bl .\n    movs r0, #0x1f\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am010_addr_0047f5b8\n    bl .\n    movs r0, #0x20\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am010_addr_0047f5b8\n    bl .\n    movs r0, #0x21\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am010_addr_0047f5b8\n    bl .\n    movs r0, #0x1a\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am010_addr_0047f5b8\n    bl .\n    movs r0, #0x1b\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am010_addr_0047f5b8\n    bl .\n    ldr r5, [pc, #0x220]\n    ldr r0, [r5]\n    movs r0, #5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am010_addr_004807a0\n    bl .\n    ldr r6, [pc, #0x248]\n    ldr r0, [r6]\n    orrs r0, r0, #1\n    str r0, [r6]\n    ldr r7, [pc, #0x244]\n    ldr r0, [r7]\n    orrs r0, r0, #1\n    str r0, [r7]\n    ldr.w r8, [pc, #0x23c]\n    ldr.w r0, [r8]\n    orrs r0, r0, #1\n    str.w r0, [r8]\n    ldr.w sb, [pc, #0x230]\n    ldr.w r0, [sb]\n    lsrs r0, r0, #1\n    lsls r0, r0, #1\n    str.w r0, [sb]\n    ldr r0, [pc, #0x224]\n    ldr r1, [r0]\n    bics r1, r1, #0x7000000\n    str r1, [r0]\n    movs r1, #1\n    movs r0, #0\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am010_addr_00475014\n    bl .\n    movs r0, #1\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am010_addr_004807a0\n    bl .\n    ldr r0, [r4]\n    lsls r0, r0, #0x1f\n    bpl L_open_cfw_runtime_am010_4b158_0248\n    ldr r0, [pc, #0x1ec]\n    movs r1, #2\n    ldr r2, [r0]\n    bfi r2, r1, #2, #2\n    str r2, [r0]\n    ldr r0, [r5]\nL_open_cfw_runtime_am010_4b158_0248:\n    movs r0, #0x14\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am010_addr_004807a0\n    bl .\n    ldr r0, [r6]\n    orrs r0, r0, #1\n    str r0, [r6]\n    ldr r0, [r7]\n    orrs r0, r0, #1\n    str r0, [r7]\n    ldr.w r0, [r8]\n    orrs r0, r0, #1\n    str.w r0, [r8]\n    ldr.w r0, [sb]\n    lsrs r0, r0, #1\n    lsls r0, r0, #1\n    str.w r0, [sb]\n    movs r0, #0x1e\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am010_addr_0047f7ae\n    bl .\n    movs r0, #0x1f\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am010_addr_0047f7ae\n    bl .\n    movs r0, #0x20\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am010_addr_0047f7ae\n    bl .\n    movs r0, #0x21\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am010_addr_0047f7ae\n    bl .\n    movs r0, #0x1a\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am010_addr_0047f7ae\n    bl .\n    movs r0, #0x1b\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am010_addr_0047f7ae\n    bl .\n    ldr r0, [r4]\n    ubfx r0, r0, #5, #1\n    cmp r0, #0\n    beq L_open_cfw_runtime_am010_4b158_02d2\n    ldr r0, [pc, #0x11c]\n    ldr r1, [r0]\n    bics r1, r1, #0x20000000\n    str r1, [r0]\n    ldr r1, [r0]\n    bics r1, r1, #0x100\n    str r1, [r0]\n    ldr r1, [r0]\n    bics r1, r1, #0x20\n    str r1, [r0]\n    ldr r1, [r0]\n    orrs r1, r1, #4\n    str r1, [r0]\n    ldr r1, [r0]\n    orrs r1, r1, #2\n    str r1, [r0]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am010_addr_0048009e\n    bl .\nL_open_cfw_runtime_am010_4b158_02d2:\n    ldr r0, [r4]\n    ubfx r0, r0, #4, #1\n    cmp r0, #0\n    bne L_open_cfw_runtime_am010_4b158_02fe\n    ldr r0, [r4]\n    ubfx r0, r0, #5, #1\n    cmp r0, #0\n    beq L_open_cfw_runtime_am010_4b158_02f6\n    ldr r0, [r4]\n    ubfx r0, r0, #6, #1\n    ands r0, r0, #1\n    eors r0, r0, #1\n    b L_open_cfw_runtime_am010_4b158_02f8\nL_open_cfw_runtime_am010_4b158_02f6:\n    movs r0, #1\nL_open_cfw_runtime_am010_4b158_02f8:\n    eors r0, r0, #1\n    b L_open_cfw_runtime_am010_4b158_0300\nL_open_cfw_runtime_am010_4b158_02fe:\n    movs r0, #1\nL_open_cfw_runtime_am010_4b158_0300:\n    uxtb r0, r0\n    cmp r0, #0\n    beq L_open_cfw_runtime_am010_4b158_030e\n    ldr r1, [sp, #4]\n    movs r0, #0xf\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am010_addr_00480f0c\n    bl .\nL_open_cfw_runtime_am010_4b158_030e:\n    ldr r0, [r4]\n    ubfx r0, r0, #3, #1\n    cmp r0, #0\n    bne L_open_cfw_runtime_am010_4b158_0336\n    ldr r0, [r4]\n    ubfx r0, r0, #5, #1\n    cmp r0, #0\n    beq L_open_cfw_runtime_am010_4b158_032e\n    ldr r0, [r4]\n    ubfx r0, r0, #6, #1\n    ands r0, r0, #1\n    b L_open_cfw_runtime_am010_4b158_0330\nL_open_cfw_runtime_am010_4b158_032e:\n    movs r0, #1\nL_open_cfw_runtime_am010_4b158_0330:\n    eors r0, r0, #1\n    b L_open_cfw_runtime_am010_4b158_0338\nL_open_cfw_runtime_am010_4b158_0336:\n    movs r0, #1\nL_open_cfw_runtime_am010_4b158_0338:\n    uxtb r0, r0\n    cmp r0, #0\n    beq L_open_cfw_runtime_am010_4b158_034c\n    movs r0, #0\n    strb.w r0, [sp]\n    mov r1, sp\n    movs r0, #4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am010_addr_004809c4\n    bl .\nL_open_cfw_runtime_am010_4b158_034c:\n    ldr r0, [r4]\n    ubfx r0, r0, #2, #1\n    cmp r0, #0\n    beq L_open_cfw_runtime_am010_4b158_0360\n    ldr r0, [pc, #0xd4]\n    ldr r1, [r0]\n    bics r1, r1, #0x20\n    str r1, [r0]\nL_open_cfw_runtime_am010_4b158_0360:\n    ldr r0, [r4]\n    lsls r0, r0, #0x1f\n    bmi L_open_cfw_runtime_am010_4b158_0372\n    ldr r0, [r4]\n    ubfx r0, r0, #1, #1\n    ands r0, r0, #1\n    b L_open_cfw_runtime_am010_4b158_0374\nL_open_cfw_runtime_am010_4b158_0372:\n    movs r0, #1\nL_open_cfw_runtime_am010_4b158_0374:\n    uxtb r0, r0\n    cmp r0, #0\n    beq L_open_cfw_runtime_am010_4b158_0384\n    ldr r0, [pc, #0xa8]\n    ldr r1, [r0]\n    lsrs r1, r1, #1\n    lsls r1, r1, #1\n    str r1, [r0]\nL_open_cfw_runtime_am010_4b158_0384:\n    ldr r0, [pc, #0x90]\n    movs r1, #0\n    str r1, [r0]\n    movw r1, #0x5af0\n    ldr r2, [r0]\n    bfi r2, r1, #0x10, #0x10\n    str r2, [r0]\n    pop.w {r0, r1, r2, r4, r5, r6, r7, r8, sb, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM010_4B5A0_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am010_4b5a0(void)
{
    __asm__ volatile(
        "    push {r0, lr}\n    lsls r3, r1, #0x1e\n    bne L_open_cfw_runtime_am010_4b5a0_003c\nL_open_cfw_runtime_am010_4b5a0_0006:\n    lsls r3, r0, #0x1e\n    bne L_open_cfw_runtime_am010_4b5a0_0054\nL_open_cfw_runtime_am010_4b5a0_000a:\n    subs r2, r2, #4\n    blo L_open_cfw_runtime_am010_4b5a0_0052\n    ldr r3, [r1], #4\n    sub.w ip, r3, #0x1010101\n    bic.w ip, ip, r3\n    ands ip, ip, #0x80808080\n    itt eq\n    streq r3, [r0], #4\n    beq L_open_cfw_runtime_am010_4b5a0_000a\n    rev.w ip, ip\n    clz r1, ip\n    rsb.w r1, r1, #0x18\n    lsls r3, r1\n    lsrs r3, r1\n    str r3, [r0], #4\n    b L_open_cfw_runtime_am010_4b5a0_0064\nL_open_cfw_runtime_am010_4b5a0_003c:\n    cmp r2, #4\n    blo L_open_cfw_runtime_am010_4b5a0_0054\nL_open_cfw_runtime_am010_4b5a0_0040:\n    ldrb r3, [r1], #1\n    subs r2, r2, #1\n    strb r3, [r0], #1\n    cbz r3, L_open_cfw_runtime_am010_4b5a0_0064\n    lsls r3, r1, #0x1e\n    bne L_open_cfw_runtime_am010_4b5a0_0040\n    b L_open_cfw_runtime_am010_4b5a0_0006\nL_open_cfw_runtime_am010_4b5a0_0052:\n    adds r2, r2, #4\nL_open_cfw_runtime_am010_4b5a0_0054:\n    cbz r2, L_open_cfw_runtime_am010_4b5a0_006e\nL_open_cfw_runtime_am010_4b5a0_0056:\n    ldrb r3, [r1], #1\n    subs r2, r2, #1\n    strb r3, [r0], #1\n    cbz r3, L_open_cfw_runtime_am010_4b5a0_0064\n    bne L_open_cfw_runtime_am010_4b5a0_0056\nL_open_cfw_runtime_am010_4b5a0_0064:\n    movs r1, r2\n    itt ne\n    movne r2, #0\n    blne #0x43c0ec\nL_open_cfw_runtime_am010_4b5a0_006e:\n    pop {r0, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM010_4B610_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am010_4b610(void)
{
    __asm__ volatile(
        "    cbz r2, L_open_cfw_runtime_am010_4b610_0026\nL_open_cfw_runtime_am010_4b610_0002:\n    ldrb r3, [r1]\n    ldrb.w ip, [r0]\n    cmp ip, r3\n    bne L_open_cfw_runtime_am010_4b610_001a\n    ldrb r3, [r0], #1\n    cbz r3, L_open_cfw_runtime_am010_4b610_0026\n    adds r1, r1, #1\n    subs r2, r2, #1\n    bne L_open_cfw_runtime_am010_4b610_0002\n    b L_open_cfw_runtime_am010_4b610_0026\nL_open_cfw_runtime_am010_4b610_001a:\n    bhs L_open_cfw_runtime_am010_4b610_0022\n    mov.w r0, #-1\n    bx lr\nL_open_cfw_runtime_am010_4b610_0022:\n    movs r0, #1\n    bx lr\nL_open_cfw_runtime_am010_4b610_0026:\n    movs r0, #0\n    bx lr\n"
    );
}
#endif

#if defined(OPEN_CFW_AM010_4B63A_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am010_4b63a(void)
{
    __asm__ volatile(
        "    push {r4, r5, r6, lr}\n    mov r5, r1\n    ldrb r4, [r5]\n    cbnz r4, L_open_cfw_runtime_am010_4b63a_0016\n    pop {r4, r5, r6, pc}\nL_open_cfw_runtime_am010_4b63a_000a:\n    ldrb r3, [r1, #1]!\n    ldrb r6, [r2]\n    cmp r3, r6\n    beq L_open_cfw_runtime_am010_4b63a_0022\n    adds r0, r0, #1\nL_open_cfw_runtime_am010_4b63a_0016:\n    mov r1, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am010_addr_00481818\n    bl .\n    cbz r0, L_open_cfw_runtime_am010_4b63a_002a\n    mov r1, r0\n    mov r2, r5\nL_open_cfw_runtime_am010_4b63a_0022:\n    ldrb r3, [r2, #1]!\n    cmp r3, #0\n    bne L_open_cfw_runtime_am010_4b63a_000a\nL_open_cfw_runtime_am010_4b63a_002a:\n    pop {r4, r5, r6, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM010_4B728_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am010_4b728(void)
{
    __asm__ volatile(
        "    push {r3}\n    push {r3, r4, r5, lr}\n    sub sp, #0x14\n    add r4, sp, #0x24\n    movs r5, #0\n    str r4, [sp, #0x10]\n    str r5, [sp, #0xc]\n    cmp r1, #0\n    itee eq\n    streq r5, [sp, #4]\n    strne r0, [sp, #4]\n    subne r1, r1, #1\n    str r1, [sp, #8]\n    str r5, [sp]\n    add r3, sp, #0x10\n    add r1, sp, #4\n    ldr r0, [pc, #0x1c]\n    add r0, pc\n    adds r0, #0x1a\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am010_addr_00481836\n    bl .\n    ldr r1, [sp, #4]\n    cbz r1, L_open_cfw_runtime_am010_4b728_0030\n    strb r5, [r1]\nL_open_cfw_runtime_am010_4b728_0030:\n    cmp r0, #0\n    it pl\n    ldrpl r0, [sp, #0xc]\n    add sp, #0x18\n    pop {r4, r5}\n    ldr pc, [sp], #8\n"
    );
}
#endif

#if defined(OPEN_CFW_AM010_4B76C_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am010_4b76c(void)
{
    __asm__ volatile(
        "    push {r3, lr}\n    sub sp, #0x10\n    movs r3, #0\n    str r3, [sp, #0xc]\n    cmp r1, #0\n    itee eq\n    streq r3, [sp, #4]\n    strne r0, [sp, #4]\n    subne r1, r1, #1\n    str r1, [sp, #8]\n    str r3, [sp]\n    add r1, sp, #4\n    add r3, sp, #0x10\n    ldr r0, [pc, #0x1c]\n    add r0, pc\n    adds r0, #0x18\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am010_addr_00481836\n    bl .\n    ldr r1, [sp, #4]\n    cbz r1, L_open_cfw_runtime_am010_4b76c_002c\n    movs r2, #0\n    strb r2, [r1]\nL_open_cfw_runtime_am010_4b76c_002c:\n    cmp r0, #0\n    it pl\n    ldrpl r0, [sp, #0xc]\n    add sp, #0x14\n    pop {pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM010_4B7A8_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am010_4b7a8(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    movs r2, r1\n    movs r1, #0\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am010_addr_00454746\n    bl .\n    pop {r0, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM010_4B7B4_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am010_4b7b4(void)
{
    __asm__ volatile(
        "    ldrb r1, [r0]\n    cmp r1, #0\n    bne L_open_cfw_runtime_am010_4b7b4_000a\n    movs r1, #1\n    strb r1, [r0]\nL_open_cfw_runtime_am010_4b7b4_000a:\n    bx lr\n"
    );
}
#endif

#if defined(OPEN_CFW_AM010_4B7C0_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am010_4b7c0(void)
{
    __asm__ volatile(
        "    ldrb r0, [r0, #8]\n    cmp r0, #0xff\n    bne L_open_cfw_runtime_am010_4b7c0_000a\n    movs r0, #1\n    b L_open_cfw_runtime_am010_4b7c0_000c\nL_open_cfw_runtime_am010_4b7c0_000a:\n    movs r0, #0\nL_open_cfw_runtime_am010_4b7c0_000c:\n    bx lr\n"
    );
}
#endif

#if defined(OPEN_CFW_AM010_4B7CE_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am010_4b7ce(void)
{
    __asm__ volatile(
        "    push {r4, r5, r6, lr}\n    movs r6, r0\n    movs r5, r1\n    movs r4, r2\n    movs r0, r6\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am010_4b7c0\n    bl .\n    cmp r0, #0\n    beq L_open_cfw_runtime_am010_4b7ce_003a\n    ldr r1, [r6]\n    movs r2, #0\n    b L_open_cfw_runtime_am010_4b7ce_001a\nL_open_cfw_runtime_am010_4b7ce_0018:\n    adds r2, r2, #1\nL_open_cfw_runtime_am010_4b7ce_001a:\n    ldrb.w r0, [r1, r2, lsl #3]\n    cmp r0, #0\n    beq L_open_cfw_runtime_am010_4b7ce_0064\n    ldrb.w r0, [r1, r2, lsl #3]\n    movs r3, r5\n    uxtb r3, r3\n    cmp r0, r3\n    bne L_open_cfw_runtime_am010_4b7ce_0018\n    add.w r0, r1, r2, lsl #3\n    ldr r0, [r0, #4]\n    str r0, [r4]\n    movs r0, #1\n    b L_open_cfw_runtime_am010_4b7ce_0066\nL_open_cfw_runtime_am010_4b7ce_003a:\n    ldr r0, [r6]\n    ldrb r1, [r6, #8]\n    add.w r0, r0, r1, lsl #2\n    movs r1, #0\n    b L_open_cfw_runtime_am010_4b7ce_0048\nL_open_cfw_runtime_am010_4b7ce_0046:\n    adds r1, r1, #1\nL_open_cfw_runtime_am010_4b7ce_0048:\n    ldrb r2, [r6, #8]\n    cmp r1, r2\n    bhs L_open_cfw_runtime_am010_4b7ce_0064\n    ldrb r2, [r0, r1]\n    movs r3, r5\n    uxtb r3, r3\n    cmp r2, r3\n    bne L_open_cfw_runtime_am010_4b7ce_0046\n    ldr r0, [r6]\n    ldr.w r0, [r0, r1, lsl #2]\n    str r0, [r4]\n    movs r0, #1\n    b L_open_cfw_runtime_am010_4b7ce_0066\nL_open_cfw_runtime_am010_4b7ce_0064:\n    movs r0, #0\nL_open_cfw_runtime_am010_4b7ce_0066:\n    pop {r4, r5, r6, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM010_4B836_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am010_4b836(void)
{
    __asm__ volatile(
        "    uxtb r0, r0\n    lsrs r0, r0, #2\n    uxtb r0, r0\n    cmp r0, #0x1f\n    blo L_open_cfw_runtime_am010_4b836_000c\n    movs r0, #0x1f\nL_open_cfw_runtime_am010_4b836_000c:\n    bx lr\n"
    );
}
#endif

#if defined(OPEN_CFW_AM010_4B844_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am010_4b844(void)
{
    __asm__ volatile(
        "    push {r4, lr}\n    movs r4, r1\n    uxtb r0, r0\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am010_addr_00482a6a\n    bl .\n    tst r0, r4\n    beq L_open_cfw_runtime_am010_4b844_0012\n    movs r0, #1\n    b L_open_cfw_runtime_am010_4b844_0014\nL_open_cfw_runtime_am010_4b844_0012:\n    movs r0, #0\nL_open_cfw_runtime_am010_4b844_0014:\n    uxtb r0, r0\n    pop {r4, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM010_4B85C_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am010_4b85c(void)
{
    __asm__ volatile(
        "    uxth r0, r0\n    bx lr\n"
    );
}
#endif

#if defined(OPEN_CFW_AM010_4B860_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am010_4b860(void)
{
    __asm__ volatile(
        "    ands r0, r0, #0xff0000\n    bx lr\n"
    );
}
#endif

#if defined(OPEN_CFW_AM010_4B866_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am010_4b866(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    movs r2, #1\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am010_addr_0044bdea\n    bl .\n    pop {r1, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM010_4B870_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am010_4b870(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    movs r2, #2\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am010_addr_0044bdea\n    bl .\n    pop {r1, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM010_4B87A_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am010_4b87a(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    movs r2, #0x6e\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am010_addr_0044bdea\n    bl .\n    pop {r1, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM010_4B884_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am010_4b884(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    movs r2, #0x6f\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am010_addr_0044bdea\n    bl .\n    pop {r1, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM010_4B88E_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am010_4b88e(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    movs r2, #0x70\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am010_addr_0044bdea\n    bl .\n    pop {r1, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM010_4B898_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am010_4b898(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    movs r2, #0x73\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am010_addr_0044bdea\n    bl .\n    pop {r1, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM010_4B8A2_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am010_4b8a2(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    movs r2, #0x74\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am010_addr_0044bdea\n    bl .\n    pop {r1, pc}\n"
    );
}
#endif
