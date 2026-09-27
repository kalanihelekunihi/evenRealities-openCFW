/*
 * SPDX-License-Identifier: MIT
 *
 * Source-owned exact helpers from the AM-018 retained island.
 */

#if defined(OPEN_CFW_AM018_51B34_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am018_51b34(void)
{
    __asm__ volatile(
        "    push {r4, lr}\n    movs r4, r0\n    ldrb r0, [r4, #0x18]\n    ubfx r0, r0, #2, #1\n    uxtb r0, r0\n    cmp r0, #0\n    beq L_open_cfw_runtime_am018_51b34_0014\n    movs r0, #0\n    b L_open_cfw_runtime_am018_51b34_0058\nL_open_cfw_runtime_am018_51b34_0014:\n    ldr r0, [r4, #8]\n    subs r0, #0x2b\n    cmp r0, #1\n    bhi L_open_cfw_runtime_am018_51b34_0020\n    movs r0, #1\n    b L_open_cfw_runtime_am018_51b34_0058\nL_open_cfw_runtime_am018_51b34_0020:\n    mov.w r1, #0x4000\n    ldr r0, [r4]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am018_addr_0043e0e0\n    bl .\n    cmp r0, #0\n    bne L_open_cfw_runtime_am018_51b34_0032\n    movs r0, #0\n    b L_open_cfw_runtime_am018_51b34_0058\nL_open_cfw_runtime_am018_51b34_0032:\n    ldr r0, [r4, #8]\n    subs r0, #0x16\n    beq L_open_cfw_runtime_am018_51b34_0052\n    subs r0, r0, #4\n    cmp r0, #8\n    bls L_open_cfw_runtime_am018_51b34_0052\n    subs r0, #0xb\n    beq L_open_cfw_runtime_am018_51b34_0052\n    subs r0, r0, #4\n    cmp r0, #3\n    bls L_open_cfw_runtime_am018_51b34_0052\n    subs r0, #8\n    cmp r0, #1\n    bls L_open_cfw_runtime_am018_51b34_0052\n    subs r0, r0, #3\n    bne L_open_cfw_runtime_am018_51b34_0056\nL_open_cfw_runtime_am018_51b34_0052:\n    movs r0, #0\n    b L_open_cfw_runtime_am018_51b34_0058\nL_open_cfw_runtime_am018_51b34_0056:\n    movs r0, #1\nL_open_cfw_runtime_am018_51b34_0058:\n    pop {r4, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM018_51B90_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am018_51b90(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    movs r2, r1\n    movs r1, #0\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am018_addr_00454746\n    bl .\n    pop {r0, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM018_51B9C_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am018_51b9c(void)
{
    __asm__ volatile(
        "    push {r3, r4, r5, lr}\n    movs r4, r0\n    movs r1, #0x70\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am018_51b90\n    bl .\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am018_addr_00441094\n    bl .\n    str r0, [sp]\n    adds.w r0, r4, #0x21\n    mov r1, sp\n    movs r2, #3\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am018_addr_00439be4\n    bl .\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am018_addr_00441094\n    bl .\n    str r0, [sp]\n    adds.w r0, r4, #0x24\n    mov r1, sp\n    movs r2, #3\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am018_addr_00439be4\n    bl .\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am018_addr_004410a6\n    bl .\n    str r0, [sp]\n    adds.w r0, r4, #0x29\n    mov r1, sp\n    movs r2, #3\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am018_addr_00439be4\n    bl .\n    movs r5, #0xff\n    strb.w r5, [r4, #0x2d]\n    movs r0, #2\n    strb.w r0, [r4, #0x2e]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am018_addr_004410a6\n    bl .\n    str r0, [sp]\n    adds.w r0, r4, #0x3e\n    mov r1, sp\n    movs r2, #3\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am018_addr_00439be4\n    bl .\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am018_addr_004410a6\n    bl .\n    str r0, [sp]\n    adds.w r0, r4, #0x59\n    mov r1, sp\n    movs r2, #3\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am018_addr_00439be4\n    bl .\n    ldr.w r0, [pc, #0x698]\n    str r0, [r4, #0x34]\n    strb.w r5, [r4, #0x20]\n    strb.w r5, [r4, #0x3b]\n    strb.w r5, [r4, #0x58]\n    strb.w r5, [r4, #0x48]\n    strb.w r5, [r4, #0x6c]\n    ldrb.w r0, [r4, #0x49]\n    ands r0, r0, #0xe0\n    orrs r0, r0, #0xf\n    strb.w r0, [r4, #0x49]\n    pop {r0, r4, r5, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM018_51C3A_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am018_51c3a(void)
{
    __asm__ volatile(
        "    push {r4, lr}\n    movs r4, r0\n    movs r1, #0x30\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am018_51b90\n    bl .\n    movs r0, #0xff\n    strb.w r0, [r4, #0x20]\n    movs r0, #0x30\n    str r0, [r4, #0x14]\n    pop {r4, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM018_51C6E_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am018_51c6e(void)
{
    __asm__ volatile(
        "    push.w {r4, r5, r6, r7, r8, sb, sl, fp, lr}\n    sub sp, #0x64\n    movs r5, r1\n    ldr r1, [r5, #0x5c]\n    cmp r1, #0\n    beq L_open_cfw_runtime_am018_51c6e_002e\n    ldrb.w r1, [r5, #0x6c]\n    cmp r1, #3\n    blt L_open_cfw_runtime_am018_51c6e_002e\n    ldr r1, [r5, #0x5c]\n    cmp r1, #1\n    bne L_open_cfw_runtime_am018_51c6e_0032\n    ldr r1, [r5, #0x68]\n    cmp r1, #1\n    bge L_open_cfw_runtime_am018_51c6e_0032\n    ldr r1, [r5, #0x60]\n    cmp r1, #0\n    bne L_open_cfw_runtime_am018_51c6e_0032\n    ldr r1, [r5, #0x64]\n    cmp r1, #0\n    bne L_open_cfw_runtime_am018_51c6e_0032\nL_open_cfw_runtime_am018_51c6e_002e:\n    movs r3, #0\n    b L_open_cfw_runtime_am018_51c6e_0034\nL_open_cfw_runtime_am018_51c6e_0032:\n    movs r3, #1\nL_open_cfw_runtime_am018_51c6e_0034:\n    ldrb.w r1, [r5, #0x20]\n    cmp r1, #3\n    bge L_open_cfw_runtime_am018_51c6e_0042\n    movs.w r8, #0\n    b L_open_cfw_runtime_am018_51c6e_0046\nL_open_cfw_runtime_am018_51c6e_0042:\n    movs.w r8, #1\nL_open_cfw_runtime_am018_51c6e_0046:\n    ldrb.w r1, [r5, #0x3b]\n    cmp r1, #3\n    blt L_open_cfw_runtime_am018_51c6e_0054\n    ldr r1, [r5, #0x30]\n    cmp r1, #0\n    bne L_open_cfw_runtime_am018_51c6e_005a\nL_open_cfw_runtime_am018_51c6e_0054:\n    movs.w sb, #0\n    b L_open_cfw_runtime_am018_51c6e_005e\nL_open_cfw_runtime_am018_51c6e_005a:\n    movs.w sb, #1\nL_open_cfw_runtime_am018_51c6e_005e:\n    ldrb.w r1, [r5, #0x48]\n    cmp r1, #3\n    blt L_open_cfw_runtime_am018_51c6e_0084\n    ldr r1, [r5, #0x44]\n    cmp r1, #0\n    beq L_open_cfw_runtime_am018_51c6e_0084\n    ldrb.w r1, [r5, #0x49]\n    ubfx r1, r1, #5, #1\n    uxtb r1, r1\n    cmp r1, #0\n    bne L_open_cfw_runtime_am018_51c6e_0084\n    ldrb.w r1, [r5, #0x49]\n    tst.w r1, #0x1f\n    bne L_open_cfw_runtime_am018_51c6e_0088\nL_open_cfw_runtime_am018_51c6e_0084:\n    movs r6, #0\n    b L_open_cfw_runtime_am018_51c6e_008a\nL_open_cfw_runtime_am018_51c6e_0088:\n    movs r6, #1\nL_open_cfw_runtime_am018_51c6e_008a:\n    ldrb.w r1, [r5, #0x58]\n    cmp r1, #3\n    blt L_open_cfw_runtime_am018_51c6e_0098\n    ldr r1, [r5, #0x50]\n    cmp r1, #0\n    bne L_open_cfw_runtime_am018_51c6e_009c\nL_open_cfw_runtime_am018_51c6e_0098:\n    movs r7, #0\n    b L_open_cfw_runtime_am018_51c6e_009e\nL_open_cfw_runtime_am018_51c6e_009c:\n    movs r7, #1\nL_open_cfw_runtime_am018_51c6e_009e:\n    movs.w sl, #1\n    ldrb.w r1, [r5, #0x20]\n    cmp r1, #0xff\n    beq L_open_cfw_runtime_am018_51c6e_00b0\n    movs.w sl, #0\n    b L_open_cfw_runtime_am018_51c6e_00dc\nL_open_cfw_runtime_am018_51c6e_00b0:\n    ldrb.w r1, [r5, #0x2f]\n    tst.w r1, #0xf\n    beq L_open_cfw_runtime_am018_51c6e_00dc\n    movs r1, #0\n    b L_open_cfw_runtime_am018_51c6e_00c0\nL_open_cfw_runtime_am018_51c6e_00be:\n    adds r1, r1, #1\nL_open_cfw_runtime_am018_51c6e_00c0:\n    ldrb.w r4, [r5, #0x2e]\n    cmp r1, r4\n    bhs L_open_cfw_runtime_am018_51c6e_00dc\n    movs r4, #5\n    mul r4, r4, r1\n    add r4, r5\n    ldrb.w r4, [r4, #0x27]\n    cmp r4, #0xff\n    beq L_open_cfw_runtime_am018_51c6e_00be\n    movs.w sl, #0\nL_open_cfw_runtime_am018_51c6e_00dc:\n    movs r4, r0\n    str r2, [sp, #0xc]\n    uxtb r3, r3\n    cmp r3, #0\n    beq L_open_cfw_runtime_am018_51c6e_01b2\n    ldr r1, [sp, #0xc]\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am018_addr_004843ee\n    bl .\n    str r0, [sp]\n    movs r0, #0x38\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am018_addr_0044f718\n    bl .\n    mov fp, r0\n    cmp.w fp, #0\n    bne L_open_cfw_runtime_am018_51c6e_012a\n    ldr.w r0, [pc, #0x53c]\n    str r0, [sp, #8]\n    ldr.w r0, [pc, #0x544]\n    str r0, [sp, #4]\n    ldr.w r0, [pc, #0x534]\n    str r0, [sp]\n    ldr.w r3, [pc, #0x53c]\n    movs r2, #0xc8\n    ldr.w r1, [pc, #0x52c]\n    movs r0, #3\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am018_addr_0044d25c\n    bl .\nL_open_cfw_runtime_am018_51c6e_0120:\n    movs r0, #0\n    movs.w r1, #-1\n    str r0, [r1]\n    b L_open_cfw_runtime_am018_51c6e_0120\nL_open_cfw_runtime_am018_51c6e_012a:\n    ldr r0, [sp]\n    str.w fp, [r0, #0x54]\n    ldr r2, [r5, #0x68]\n    ldr r1, [r5, #0x68]\n    ldr r0, [sp]\n    adds r0, #0x18\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am018_addr_00450b98\n    bl .\n    ldr r2, [r5, #0x5c]\n    ldr r1, [r5, #0x5c]\n    ldr r0, [sp]\n    adds r0, #0x18\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am018_addr_00450b98\n    bl .\n    ldr r2, [r5, #0x64]\n    ldr r1, [r5, #0x60]\n    ldr r0, [sp]\n    adds r0, #0x18\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am018_addr_00450bb2\n    bl .\n    mov r0, fp\n    movs r1, r5\n    movs r2, #0x1c\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am018_addr_00439c04\n    bl .\n    movs r0, #0x38\n    str.w r0, [fp, #0x14]\n    ldr r0, [r5, #0x1c]\n    str.w r0, [fp, #0x1c]\n    adds.w r0, fp, #0x20\n    adds.w r1, r5, #0x59\n    movs r2, #3\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am018_addr_00439be4\n    bl .\n    ldr r0, [r5, #0x5c]\n    str.w r0, [fp, #0x24]\n    ldr r0, [r5, #0x68]\n    str.w r0, [fp, #0x28]\n    ldrb.w r0, [r5, #0x6c]\n    strb.w r0, [fp, #0x34]\n    ldr r0, [r5, #0x60]\n    str.w r0, [fp, #0x2c]\n    ldr r0, [r5, #0x64]\n    str.w r0, [fp, #0x30]\n    ldrb.w r0, [fp, #0x35]\n    bfi r0, sl, #0, #1\n    strb.w r0, [fp, #0x35]\n    movs r0, #3\n    ldr r1, [sp]\n    strb r0, [r1, #4]\n    ldr r1, [sp]\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am018_addr_00484476\n    bl .\nL_open_cfw_runtime_am018_51c6e_01b2:\n    uxtb.w r8, r8\n    cmp.w r8, #0\n    beq L_open_cfw_runtime_am018_51c6e_02b8\n    add r0, sp, #0x10\n    ldr r1, [sp, #0xc]\n    movs r2, #0x10\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am018_addr_00439c04\n    bl .\n    ldr r0, [r5, #0x44]\n    cmp r0, #2\n    blt L_open_cfw_runtime_am018_51c6e_0222\n    ldrb.w r0, [r5, #0x48]\n    cmp r0, #0xfd\n    blt L_open_cfw_runtime_am018_51c6e_0222\n    ldr r0, [r5, #0x1c]\n    cmp r0, #0\n    beq L_open_cfw_runtime_am018_51c6e_0222\n    ldr r0, [sp, #0x10]\n    ldrb.w r1, [r5, #0x49]\n    uxtb r1, r1\n    lsrs r1, r1, #2\n    ands r1, r1, #1\n    uxtab r0, r0, r1\n    str r0, [sp, #0x10]\n    ldr r0, [sp, #0x14]\n    ldrb.w r1, [r5, #0x49]\n    uxtb r1, r1\n    lsrs r1, r1, #1\n    ands r1, r1, #1\n    uxtab r0, r0, r1\n    str r0, [sp, #0x14]\n    ldr r0, [sp, #0x18]\n    ldrb.w r1, [r5, #0x49]\n    uxtb r1, r1\n    lsrs r1, r1, #3\n    ands r1, r1, #1\n    subs r0, r0, r1\n    str r0, [sp, #0x18]\n    ldr r0, [sp, #0x1c]\n    ldrb.w r1, [r5, #0x49]\n    ands r1, r1, #1\n    subs r0, r0, r1\n    str r0, [sp, #0x1c]\nL_open_cfw_runtime_am018_51c6e_0222:\n    add r1, sp, #0x10\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am018_addr_004843ee\n    bl .\n    mov sl, r0\n    movs r0, #0x30\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am018_addr_0044f718\n    bl .\n    mov r8, r0\n    cmp.w r8, #0\n    bne L_open_cfw_runtime_am018_51c6e_0266\n    ldr.w r0, [pc, #0x400]\n    str r0, [sp, #8]\n    ldr.w r0, [pc, #0x410]\n    str r0, [sp, #4]\n    ldr.w r0, [pc, #0x3f8]\n    str r0, [sp]\n    ldr.w r3, [pc, #0x400]\n    movs r2, #0xe8\n    ldr.w r1, [pc, #0x3f0]\n    movs r0, #3\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am018_addr_0044d25c\n    bl .\nL_open_cfw_runtime_am018_51c6e_025c:\n    movs r0, #0\n    movs.w r1, #-1\n    str r0, [r1]\n    b L_open_cfw_runtime_am018_51c6e_025c\nL_open_cfw_runtime_am018_51c6e_0266:\n    mov r0, r8\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am018_51c3a\n    bl .\n    str.w r8, [sl, #0x54]\n    mov r0, r8\n    movs r1, r5\n    movs r2, #0x1c\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am018_addr_00439c04\n    bl .\n    movs r0, #0x30\n    str.w r0, [r8, #0x14]\n    ldr r0, [r5, #0x1c]\n    str.w r0, [r8, #0x1c]\n    adds.w r0, r8, #0x21\n    adds.w r1, r5, #0x21\n    movs r2, #3\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am018_addr_00439be4\n    bl .\n    adds.w r0, r8, #0x24\n    adds.w r1, r5, #0x24\n    movs r2, #0xc\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am018_addr_00439be4\n    bl .\n    ldrb.w r0, [r5, #0x20]\n    strb.w r0, [r8, #0x20]\n    movs r0, #1\n    strb.w r0, [sl, #4]\n    mov r1, sl\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am018_addr_00484476\n    bl .\nL_open_cfw_runtime_am018_51c6e_02b8:\n    uxtb.w sb, sb\n    cmp.w sb, #0\n    beq.w #0x45213e\n    ldr r0, [r5, #0x30]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am018_addr_00488cb8\n    bl .\n    mov sb, r0\n    movs.w r8, #1\n    mov r0, sb\n    uxtb r0, r0\n    cmp r0, #0\n    beq L_open_cfw_runtime_am018_51c6e_02e0\n    mov r0, sb\n    uxtb r0, r0\n    cmp r0, #1\n    bne L_open_cfw_runtime_am018_51c6e_02ec\nL_open_cfw_runtime_am018_51c6e_02e0:\n    add r1, sp, #0x28\n    ldr r0, [r5, #0x30]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am018_addr_00488f6a\n    bl .\n    mov r8, r0\n    b L_open_cfw_runtime_am018_51c6e_0300\nL_open_cfw_runtime_am018_51c6e_02ec:\n    movs r1, #0xc\n    add r0, sp, #0x28\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am018_51b90\n    bl .\n    mov r0, sb\n    uxtb r0, r0\n    cmp r0, #3\n    bne L_open_cfw_runtime_am018_51c6e_0300\n    movs.w r8, #0\nL_open_cfw_runtime_am018_51c6e_0300:\n    uxtb.w r8, r8\n    cmp.w r8, #1\n    bne.w #0x45213e\n    mov r0, sb\n    uxtb r0, r0\n    cmp r0, #0\n    beq L_open_cfw_runtime_am018_51c6e_031e\n    uxtb.w sb, sb\n    cmp.w sb, #1\n    bne L_open_cfw_runtime_am018_51c6e_0414\nL_open_cfw_runtime_am018_51c6e_031e:\n    ldrb.w r0, [r5, #0x3d]\n    cmp r0, #0\n    beq L_open_cfw_runtime_am018_51c6e_0332\n    ldr r1, [sp, #0xc]\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am018_addr_004843ee\n    bl .\n    mov sb, r0\n    b L_open_cfw_runtime_am018_51c6e_0364\nL_open_cfw_runtime_am018_51c6e_0332:\n    add r0, sp, #0x34\n    movs r1, #0x10\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am018_addr_0048949c\n    bl .\n    ldr r0, [sp, #0x2c]\n    uxth r0, r0\n    subs r0, r0, #1\n    str r0, [sp, #0x3c]\n    ldr r0, [sp, #0x2c]\n    lsrs r0, r0, #0x10\n    subs r0, r0, #1\n    str r0, [sp, #0x40]\n    movs r0, #0\n    str r0, [sp]\n    movs r3, #0\n    movs r2, #9\n    add r1, sp, #0x34\n    ldr r0, [sp, #0xc]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am018_addr_00451082\n    bl .\n    add r1, sp, #0x34\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am018_addr_004843ee\n    bl .\n    mov sb, r0\nL_open_cfw_runtime_am018_51c6e_0364:\n    movs r0, #0x6c\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am018_addr_0044f718\n    bl .\n    mov r8, r0\n    cmp.w r8, #0\n    bne L_open_cfw_runtime_am018_51c6e_0396\n    ldr r0, [pc, #0x2c8]\n    str r0, [sp, #8]\n    ldr r0, [pc, #0x2dc]\n    str r0, [sp, #4]\n    ldr r0, [pc, #0x2c4]\n    str r0, [sp]\n    ldr r3, [pc, #0x2cc]\n    movw r2, #0x113\n    ldr r1, [pc, #0x2c0]\n    movs r0, #3\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am018_addr_0044d25c\n    bl .\nL_open_cfw_runtime_am018_51c6e_038c:\n    movs r0, #0\n    movs.w r1, #-1\n    str r0, [r1]\n    b L_open_cfw_runtime_am018_51c6e_038c\nL_open_cfw_runtime_am018_51c6e_0396:\n    mov r0, r8\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am018_addr_00488918\n    bl .\n    str.w r8, [sb, #0x54]\n    mov r0, r8\n    movs r1, r5\n    movs r2, #0x1c\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am018_addr_00439c04\n    bl .\n    movs r0, #0x6c\n    str.w r0, [r8, #0x14]\n    ldr r0, [r5, #0x30]\n    str.w r0, [r8, #0x1c]\n    ldrb.w r0, [r5, #0x3b]\n    strb.w r0, [r8, #0x50]\n    adds.w r0, r8, #0x4c\n    adds.w r1, r5, #0x38\n    movs r2, #3\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am018_addr_00439be4\n    bl .\n    ldrb.w r0, [r5, #0x3c]\n    strb.w r0, [r8, #0x4f]\n    ldrb.w r0, [r5, #0x3d]\n    ldrh.w r1, [r8, #0x50]\n    bfi r1, r0, #0xc, #1\n    strh.w r1, [r8, #0x50]\n    adds.w r0, r8, #0x20\n    add r1, sp, #0x28\n    ldm.w r1, {r2, r3, ip}\n    stm.w r0, {r2, r3, ip}\n    ldr r0, [r5, #0x1c]\n    str.w r0, [r8, #0x2c]\n    adds.w r0, r8, #0x58\n    ldr r1, [sp, #0xc]\n    movs r2, #0x10\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am018_addr_00439c04\n    bl .\n    movs r0, #6\n    strb.w r0, [sb, #4]\n    mov r1, sb\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am018_addr_00484476\n    bl .\n    b L_open_cfw_runtime_am018_51c6e_04d0\nL_open_cfw_runtime_am018_51c6e_0414:\n    movs r0, #0\n    str r0, [sp, #8]\n    mvns r0, #0xe0000000\n    str r0, [sp, #4]\n    movs r0, #0\n    str r0, [sp]\n    movs r3, #0\n    ldr r2, [r5, #0x34]\n    ldr r1, [r5, #0x30]\n    add r0, sp, #0x20\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am018_addr_00489546\n    bl .\n    add r0, sp, #0x44\n    movs r1, #0x10\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am018_addr_0048949c\n    bl .\n    ldr r0, [sp, #0x20]\n    subs r0, r0, #1\n    str r0, [sp, #0x4c]\n    ldr r0, [sp, #0x24]\n    subs r0, r0, #1\n    str r0, [sp, #0x50]\n    movs r0, #0\n    str r0, [sp]\n    movs r3, #0\n    movs r2, #9\n    add r1, sp, #0x44\n    ldr r0, [sp, #0xc]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am018_addr_00451082\n    bl .\n    add r1, sp, #0x44\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am018_addr_004843ee\n    bl .\n    mov sb, r0\n    movs r0, #0x64\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am018_addr_0044f718\n    bl .\n    mov r8, r0\n    cmp.w r8, #0\n    bne L_open_cfw_runtime_am018_51c6e_048e\n    ldr r0, [pc, #0x1d0]\n    str r0, [sp, #8]\n    ldr r0, [pc, #0x1e8]\n    str r0, [sp, #4]\n    ldr r0, [pc, #0x1cc]\n    str r0, [sp]\n    ldr r3, [pc, #0x1d4]\n    mov.w r2, #0x12c\n    ldr r1, [pc, #0x1c8]\n    movs r0, #3\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am018_addr_0044d25c\n    bl .\nL_open_cfw_runtime_am018_51c6e_0484:\n    movs r0, #0\n    movs.w r1, #-1\n    str r0, [r1]\n    b L_open_cfw_runtime_am018_51c6e_0484\nL_open_cfw_runtime_am018_51c6e_048e:\n    mov r0, r8\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am018_addr_00489f5e\n    bl .\n    str.w r8, [sb, #0x54]\n    mov r0, r8\n    movs r1, r5\n    movs r2, #0x1c\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am018_addr_00439c04\n    bl .\n    movs r0, #0x64\n    str.w r0, [r8, #0x14]\n    adds.w r0, r8, #0x24\n    adds.w r1, r5, #0x38\n    movs r2, #3\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am018_addr_00439be4\n    bl .\n    ldr r0, [r5, #0x34]\n    str.w r0, [r8, #0x20]\n    ldr r0, [r5, #0x30]\n    str.w r0, [r8, #0x1c]\n    movs r0, #5\n    strb.w r0, [sb, #4]\n    mov r1, sb\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am018_addr_00484476\n    bl .\nL_open_cfw_runtime_am018_51c6e_04d0:\n    uxtb r6, r6\n    cmp r6, #0\n    beq L_open_cfw_runtime_am018_51c6e_0564\n    ldr r1, [sp, #0xc]\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am018_addr_004843ee\n    bl .\n    mov r8, r0\n    movs r0, #0x2c\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am018_addr_0044f718\n    bl .\n    movs r6, r0\n    cmp r6, #0\n    bne L_open_cfw_runtime_am018_51c6e_0510\n    ldr r0, [pc, #0x150]\n    str r0, [sp, #8]\n    ldr r0, [pc, #0x16c]\n    str r0, [sp, #4]\n    ldr r0, [pc, #0x14c]\n    str r0, [sp]\n    ldr r3, [pc, #0x154]\n    mov.w r2, #0x13e\n    ldr r1, [pc, #0x144]\n    movs r0, #3\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am018_addr_0044d25c\n    bl .\nL_open_cfw_runtime_am018_51c6e_0506:\n    movs r0, #0\n    movs.w r1, #-1\n    str r0, [r1]\n    b L_open_cfw_runtime_am018_51c6e_0506\nL_open_cfw_runtime_am018_51c6e_0510:\n    str.w r6, [r8, #0x54]\n    movs r0, r6\n    movs r1, r5\n    movs r2, #0x1c\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am018_addr_00439c04\n    bl .\n    movs r0, #0x2c\n    str r0, [r6, #0x14]\n    ldr r0, [r5, #0x1c]\n    str r0, [r6, #0x1c]\n    adds.w r0, r6, #0x20\n    adds.w r1, r5, #0x3e\n    movs r2, #3\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am018_addr_00439be4\n    bl .\n    ldrb.w r0, [r5, #0x48]\n    strb.w r0, [r6, #0x28]\n    ldr r0, [r5, #0x44]\n    str r0, [r6, #0x24]\n    ldrb.w r0, [r5, #0x49]\n    ands r0, r0, #0x1f\n    ldrb.w r1, [r6, #0x29]\n    ands r1, r1, #0xe0\n    orrs r0, r1\n    strb.w r0, [r6, #0x29]\n    movs r0, #2\n    strb.w r0, [r8, #4]\n    mov r1, r8\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am018_addr_00484476\n    bl .\nL_open_cfw_runtime_am018_51c6e_0564:\n    uxtb r7, r7\n    cmp r7, #0\n    beq L_open_cfw_runtime_am018_51c6e_0634\n    add r0, sp, #0x54\n    ldr r1, [sp, #0xc]\n    movs r2, #0x10\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am018_addr_00439c04\n    bl .\n    ldr r2, [r5, #0x50]\n    ldr r0, [r5, #0x54]\n    adds r2, r0, r2\n    ldr r1, [r5, #0x50]\n    ldr r0, [r5, #0x54]\n    adds r1, r0, r1\n    add r0, sp, #0x54\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am018_addr_00450b98\n    bl .\n    add r1, sp, #0x54\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am018_addr_004843ee\n    bl .\n    movs r7, r0\n    movs r0, #0x2c\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am018_addr_0044f718\n    bl .\n    movs r6, r0\n    cmp r6, #0\n    bne L_open_cfw_runtime_am018_51c6e_05c0\n    ldr r0, [pc, #0xa0]\n    str r0, [sp, #8]\n    ldr r0, [pc, #0xc0]\n    str r0, [sp, #4]\n    ldr r0, [pc, #0x9c]\n    str r0, [sp]\n    ldr r3, [pc, #0xa4]\n    movw r2, #0x151\n    ldr r1, [pc, #0x94]\n    movs r0, #3\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am018_addr_0044d25c\n    bl .\nL_open_cfw_runtime_am018_51c6e_05b6:\n    movs r0, #0\n    movs.w r1, #-1\n    str r0, [r1]\n    b L_open_cfw_runtime_am018_51c6e_05b6\nL_open_cfw_runtime_am018_51c6e_05c0:\n    str r6, [r7, #0x54]\n    ldr r2, [r5, #0x50]\n    ldr r1, [r5, #0x50]\n    adds.w r0, r7, #0x18\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am018_addr_00450b98\n    bl .\n    ldr r2, [r5, #0x54]\n    ldr r1, [r5, #0x54]\n    adds.w r0, r7, #0x18\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am018_addr_00450b98\n    bl .\n    movs r0, r6\n    movs r1, r5\n    movs r2, #0x1c\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am018_addr_00439c04\n    bl .\n    movs r0, #0x2c\n    str r0, [r6, #0x14]\n    movw r0, #0x7fff\n    ldr r1, [r5, #0x1c]\n    cmp r1, r0\n    beq L_open_cfw_runtime_am018_51c6e_05fc\n    ldr r1, [r5, #0x1c]\n    ldr r0, [r5, #0x50]\n    adds r1, r0, r1\n    ldr r0, [r5, #0x54]\n    adds r0, r0, r1\nL_open_cfw_runtime_am018_51c6e_05fc:\n    str r0, [r6, #0x1c]\n    adds.w r0, r6, #0x20\n    adds.w r1, r5, #0x4a\n    movs r2, #3\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am018_addr_00439be4\n    bl .\n    ldrb.w r0, [r5, #0x58]\n    strb.w r0, [r6, #0x28]\n    ldr r0, [r5, #0x50]\n    str r0, [r6, #0x24]\n    ldrb.w r0, [r6, #0x29]\n    ands r0, r0, #0xe0\n    orrs r0, r0, #0xf\n    strb.w r0, [r6, #0x29]\n    movs r0, #2\n    strb r0, [r7, #4]\n    movs r1, r7\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am018_addr_00484476\n    bl .\nL_open_cfw_runtime_am018_51c6e_0634:\n    add sp, #0x64\n    pop.w {r4, r5, r6, r7, r8, sb, sl, fp, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM018_522D4_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am018_522d4(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    movs r2, #0x6a\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am018_addr_0044bdea\n    bl .\n    pop {r1, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM018_522DE_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am018_522de(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    movs r2, #0x6b\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am018_addr_0044bdea\n    bl .\n    pop {r1, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM018_522E8_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am018_522e8(void)
{
    __asm__ volatile(
        "    push {r3, r4, r5, lr}\n    movs r4, r0\n    movs r5, r1\n    movs r2, #0x1c\n    movs r1, r5\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am018_addr_0044bdea\n    bl .\n    movs r2, r0\n    movs r1, r5\n    movs r0, r4\n    movs r0, r2\n    mov r8, r8\n    str r0, [sp]\n    ldr r0, [sp]\n    pop {r1, r4, r5, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM018_52308_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am018_52308(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    movs r2, #0x1d\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am018_addr_0044bdea\n    bl .\n    uxtb r0, r0\n    pop {r1, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM018_52314_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am018_52314(void)
{
    __asm__ volatile(
        "    push {r3, r4, r5, lr}\n    movs r4, r0\n    movs r5, r1\n    movs r2, #0x23\n    movs r1, r5\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am018_addr_0044bdea\n    bl .\n    movs r2, r0\n    movs r1, r5\n    movs r0, r4\n    movs r0, r2\n    mov r8, r8\n    str r0, [sp]\n    ldr r0, [sp]\n    pop {r1, r4, r5, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM018_52334_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am018_52334(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    movs r2, #0x20\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am018_addr_0044bdea\n    bl .\n    uxtb r0, r0\n    pop {r1, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM018_52340_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am018_52340(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    movs r2, #0x21\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am018_addr_0044bdea\n    bl .\n    pop {r1, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM018_5234A_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am018_5234a(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    movs r2, #0x22\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am018_addr_0044bdea\n    bl .\n    pop {r1, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM018_52354_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am018_52354(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    movs r2, #0x24\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am018_addr_0044bdea\n    bl .\n    uxtb r0, r0\n    pop {r1, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM018_52360_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am018_52360(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    movs r2, #0x25\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am018_addr_0044bdea\n    bl .\n    uxtb r0, r0\n    pop {r1, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM018_5236C_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am018_5236c(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    movs r2, #0x26\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am018_addr_0044bdea\n    bl .\n    pop {r1, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM018_52376_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am018_52376(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    movs r2, #0x28\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am018_addr_0044bdea\n    bl .\n    pop {r1, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM018_52380_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am018_52380(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    movs r2, #0x29\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am018_addr_0044bdea\n    bl .\n    uxtb r0, r0\n    pop {r1, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM018_5238C_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am018_5238c(void)
{
    __asm__ volatile(
        "    push {r3, r4, r5, lr}\n    movs r4, r0\n    movs r5, r1\n    movs r2, #0x2a\n    movs r1, r5\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am018_addr_0044bdea\n    bl .\n    movs r2, r0\n    movs r1, r5\n    movs r0, r4\n    movs r0, r2\n    mov r8, r8\n    str r0, [sp]\n    ldr r0, [sp]\n    pop {r1, r4, r5, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM018_523AC_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am018_523ac(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    movs r2, #0x2b\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am018_addr_0044bdea\n    bl .\n    uxtb r0, r0\n    pop {r1, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM018_523B8_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am018_523b8(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    movs r2, #0x2c\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am018_addr_0044bdea\n    bl .\n    cmp r0, #0\n    beq L_open_cfw_runtime_am018_523b8_0010\n    movs r0, #1\n    b L_open_cfw_runtime_am018_523b8_0012\nL_open_cfw_runtime_am018_523b8_0010:\n    movs r0, #0\nL_open_cfw_runtime_am018_523b8_0012:\n    uxtb r0, r0\n    pop {r1, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM018_523CE_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am018_523ce(void)
{
    __asm__ volatile(
        "    push {r3, r4, r5, lr}\n    movs r4, r0\n    movs r5, r1\n    movs r2, #0x31\n    movs r1, r5\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am018_addr_0044bdea\n    bl .\n    movs r2, r0\n    movs r1, r5\n    movs r0, r4\n    movs r0, r2\n    mov r8, r8\n    str r0, [sp]\n    ldr r0, [sp]\n    pop {r1, r4, r5, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM018_523EE_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am018_523ee(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    movs r2, #0x32\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am018_addr_0044bdea\n    bl .\n    uxtb r0, r0\n    pop {r1, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM018_523FA_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am018_523fa(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    movs r2, #0x30\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am018_addr_0044bdea\n    bl .\n    pop {r1, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM018_52404_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am018_52404(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    movs r2, #0x34\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am018_addr_0044bdea\n    bl .\n    uxtb r0, r0\n    pop {r1, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM018_52410_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am018_52410(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    movs r2, #0x38\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am018_addr_0044bdea\n    bl .\n    pop {r1, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM018_5241A_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am018_5241a(void)
{
    __asm__ volatile(
        "    push {r3, r4, r5, lr}\n    movs r4, r0\n    movs r5, r1\n    movs r2, #0x39\n    movs r1, r5\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am018_addr_0044bdea\n    bl .\n    movs r2, r0\n    movs r1, r5\n    movs r0, r4\n    movs r0, r2\n    mov r8, r8\n    str r0, [sp]\n    ldr r0, [sp]\n    pop {r1, r4, r5, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM018_5243A_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am018_5243a(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    movs r2, #0x3a\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am018_addr_0044bdea\n    bl .\n    uxtb r0, r0\n    pop {r1, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM018_52446_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am018_52446(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    movs r2, #0x3b\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am018_addr_0044bdea\n    bl .\n    pop {r1, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM018_52450_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am018_52450(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    movs r2, #0x3c\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am018_addr_0044bdea\n    bl .\n    pop {r1, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM018_5245A_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am018_5245a(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    movs r2, #0x40\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am018_addr_0044bdea\n    bl .\n    pop {r1, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM018_52464_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am018_52464(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    movs r2, #0x41\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am018_addr_0044bdea\n    bl .\n    pop {r1, pc}\n"
    );
}
#endif
