/*
 * SPDX-License-Identifier: MIT
 *
 * Source-owned exact helpers from the AM-044 retained island.
 */

#if defined(OPEN_CFW_AM044_98654_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am044_98654(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    movs r2, #0x5c\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am044_addr_0044bdea\n    bl .\n    pop {r1, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM044_9865E_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am044_9865e(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    movs r2, #0xc\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am044_addr_0044bdea\n    bl .\n    pop {r1, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM044_98668_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am044_98668(void)
{
    __asm__ volatile(
        "    push {r4, lr}\n    movs r1, r0\n    ldr.w r0, [pc, #0x5d8]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am044_addr_0044cf98\n    bl .\n    movs r4, r0\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am044_addr_0044d0f0\n    bl .\n    movs r0, r4\n    pop {r4, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM044_98680_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am044_98680(void)
{
    __asm__ volatile(
        "    push.w {r3, r4, r5, r6, r7, r8, sb, lr}\n    sub sp, #0x38\n    movs r4, r0\n    movs r5, r1\n    cmp r4, #0\n    bne L_open_cfw_runtime_am044_98680_003a\n    ldr.w r0, [pc, #0x5bc]\n    str r0, [sp, #8]\n    ldr.w r0, [pc, #0x5b8]\n    str r0, [sp, #4]\n    ldr.w r0, [pc, #0x5b8]\n    str r0, [sp]\n    ldr.w r3, [pc, #0x528]\n    movs r2, #0x96\n    ldr.w r1, [pc, #0x80c]\n    movs r0, #3\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am044_addr_0044d25c\n    bl .\nL_open_cfw_runtime_am044_98680_0030:\n    movs r0, #0\n    movs.w r1, #-1\n    str r0, [r1]\n    b L_open_cfw_runtime_am044_98680_0030\nL_open_cfw_runtime_am044_98680_003a:\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am044_addr_00440656\n    bl .\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am044_addr_00488cb8\n    bl .\n    mov r8, r0\n    movs r7, r4\n    mov r0, r8\n    uxtb r0, r0\n    cmp r0, #3\n    bne L_open_cfw_runtime_am044_98680_0098\n    cmp r5, #0\n    beq L_open_cfw_runtime_am044_98680_006c\n    ldr.w r0, [pc, #0x580]\n    str r0, [sp]\n    ldr.w r3, [pc, #0x4ec]\n    movs r2, #0xaf\n    ldr.w r1, [pc, #0x7d0]\n    movs r0, #2\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am044_addr_0044d25c\n    bl .\nL_open_cfw_runtime_am044_98680_006c:\n    ldrb.w r0, [r7, #0x58]\n    ands r0, r0, #3\n    cmp r0, #2\n    beq L_open_cfw_runtime_am044_98680_0084\n    ldrb.w r0, [r7, #0x58]\n    ands r0, r0, #3\n    cmp r0, #1\n    bne L_open_cfw_runtime_am044_98680_008a\nL_open_cfw_runtime_am044_98680_0084:\n    ldr r0, [r7, #0x2c]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am044_addr_0044f758\n    bl .\nL_open_cfw_runtime_am044_98680_008a:\n    movs r0, #0\n    str r0, [r7, #0x2c]\n    ldr r0, [r7, #0x58]\n    orrs r0, r0, #3\n    str r0, [r7, #0x58]\n    b L_open_cfw_runtime_am044_98680_0252\nL_open_cfw_runtime_am044_98680_0098:\n    add r1, sp, #0xc\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am044_addr_00488f6a\n    bl .\n    uxtb r0, r0\n    cmp r0, #1\n    beq L_open_cfw_runtime_am044_98680_00d8\n    uxtb.w r8, r8\n    cmp.w r8, #1\n    beq L_open_cfw_runtime_am044_98680_00be\n    movs r3, r5\n    adr r2, #0x1a4\n    movs r1, #0x18\n    add r0, sp, #0x20\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am044_addr_00483fd0\n    bl .\n    add r5, sp, #0x20\nL_open_cfw_runtime_am044_98680_00be:\n    str r5, [sp, #4]\n    ldr.w r0, [pc, #0x518]\n    str r0, [sp]\n    ldr.w r3, [pc, #0x484]\n    movs r2, #0xbe\n    ldr.w r1, [pc, #0x764]\n    movs r0, #2\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am044_addr_0044d25c\n    bl .\n    b L_open_cfw_runtime_am044_98680_0252\nL_open_cfw_runtime_am044_98680_00d8:\n    mov r0, r8\n    uxtb r0, r0\n    cmp r0, #0\n    bne L_open_cfw_runtime_am044_98680_0138\n    ldr r0, [sp, #0xc]\n    lsrs r0, r0, #0x10\n    lsls r0, r0, #0x1b\n    bpl L_open_cfw_runtime_am044_98680_0116\n    movs r1, r5\n    ldr r0, [r1, #0x14]\n    cmp r0, #0\n    beq L_open_cfw_runtime_am044_98680_00f6\n    ldr r0, [r1, #0x18]\n    cmp r0, #0\n    bne L_open_cfw_runtime_am044_98680_0116\nL_open_cfw_runtime_am044_98680_00f6:\n    ldr r0, [r1, #0x18]\n    str r0, [sp, #8]\n    ldr r0, [r1, #0x14]\n    str r0, [sp, #4]\n    ldr.w r0, [pc, #0x4e0]\n    str r0, [sp]\n    ldr.w r3, [pc, #0x444]\n    movs r2, #0xc9\n    ldr.w r1, [pc, #0x728]\n    movs r0, #3\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am044_addr_0044d25c\n    bl .\n    b L_open_cfw_runtime_am044_98680_0252\nL_open_cfw_runtime_am044_98680_0116:\n    ldrb.w r0, [r7, #0x58]\n    ands r0, r0, #3\n    cmp r0, #1\n    beq L_open_cfw_runtime_am044_98680_012e\n    ldrb.w r0, [r7, #0x58]\n    ands r0, r0, #3\n    cmp r0, #2\n    bne L_open_cfw_runtime_am044_98680_0134\nL_open_cfw_runtime_am044_98680_012e:\n    ldr r0, [r7, #0x2c]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am044_addr_0044f758\n    bl .\nL_open_cfw_runtime_am044_98680_0134:\n    str r5, [r7, #0x2c]\n    b L_open_cfw_runtime_am044_98680_01b0\nL_open_cfw_runtime_am044_98680_0138:\n    mov r0, r8\n    uxtb r0, r0\n    cmp r0, #1\n    beq L_open_cfw_runtime_am044_98680_0148\n    mov r0, r8\n    uxtb r0, r0\n    cmp r0, #2\n    bne L_open_cfw_runtime_am044_98680_01b0\nL_open_cfw_runtime_am044_98680_0148:\n    ldr r0, [r7, #0x2c]\n    cmp r0, r5\n    beq L_open_cfw_runtime_am044_98680_01b0\n    movs r6, #0\n    ldrb.w r0, [r7, #0x58]\n    ands r0, r0, #3\n    cmp r0, #1\n    beq L_open_cfw_runtime_am044_98680_0168\n    ldrb.w r0, [r7, #0x58]\n    ands r0, r0, #3\n    cmp r0, #2\n    bne L_open_cfw_runtime_am044_98680_016a\nL_open_cfw_runtime_am044_98680_0168:\n    ldr r6, [r7, #0x2c]\nL_open_cfw_runtime_am044_98680_016a:\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am044_addr_004547c6\n    bl .\n    cmp r0, #0\n    bne L_open_cfw_runtime_am044_98680_01a0\n    ldr.w r0, [pc, #0x46c]\n    str r0, [sp, #8]\n    ldr.w r0, [pc, #0x46c]\n    str r0, [sp, #4]\n    ldr.w r0, [pc, #0x450]\n    str r0, [sp]\n    ldr.w r3, [pc, #0x3c4]\n    movs r2, #0xdf\n    ldr.w r1, [pc, #0x6a4]\n    movs r0, #3\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am044_addr_0044d25c\n    bl .\nL_open_cfw_runtime_am044_98680_0196:\n    movs r0, #0\n    movs.w r1, #-1\n    str r0, [r1]\n    b L_open_cfw_runtime_am044_98680_0196\nL_open_cfw_runtime_am044_98680_01a0:\n    cmp r0, #0\n    beq L_open_cfw_runtime_am044_98680_0252\n    str r0, [r7, #0x2c]\n    cmp r6, #0\n    beq L_open_cfw_runtime_am044_98680_01b0\n    movs r0, r6\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am044_addr_0044f758\n    bl .\nL_open_cfw_runtime_am044_98680_01b0:\n    mov r0, r8\n    uxtb r0, r0\n    cmp r0, #2\n    bne L_open_cfw_runtime_am044_98680_0200\n    movs r1, #0\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am044_addr_00498640\n    bl .\n    movs r6, r0\n    movs r1, #0\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am044_addr_0049864a\n    bl .\n    mov sb, r0\n    movs r1, #0\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am044_98654\n    bl .\n    movs r1, #0\n    str r1, [sp, #8]\n    mvns r1, #0xe0000000\n    str r1, [sp, #4]\n    str r0, [sp]\n    mov r3, sb\n    movs r2, r6\n    movs r1, r5\n    add r0, sp, #0x18\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am044_addr_00489546\n    bl .\n    ldr r0, [sp, #0x18]\n    ldr r1, [sp, #0x10]\n    bfi r1, r0, #0, #0x10\n    str r1, [sp, #0x10]\n    ldr r0, [sp, #0x1c]\n    ldr r1, [sp, #0x10]\n    bfi r1, r0, #0x10, #0x10\n    str r1, [sp, #0x10]\nL_open_cfw_runtime_am044_98680_0200:\n    uxtb.w r8, r8\n    ldr r0, [r7, #0x58]\n    bfi r0, r8, #0, #2\n    str r0, [r7, #0x58]\n    ldr r0, [sp, #0x10]\n    uxth r0, r0\n    str r0, [r7, #0x3c]\n    ldr r0, [sp, #0x10]\n    lsrs r0, r0, #0x10\n    str r0, [r7, #0x40]\n    ldr r0, [sp, #0xc]\n    lsrs r0, r0, #8\n    ldr r1, [r7, #0x58]\n    bfi r1, r0, #2, #5\n    str r1, [r7, #0x58]\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am044_addr_0043ffa0\n    bl .\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am044_992cc\n    bl .\n    ldr r0, [r7, #0x44]\n    cmp r0, #0\n    bne L_open_cfw_runtime_am044_98680_0246\n    ldr r0, [r7, #0x48]\n    cmp.w r0, #0x100\n    bne L_open_cfw_runtime_am044_98680_0246\n    ldr r0, [r7, #0x4c]\n    cmp.w r0, #0x100\n    beq L_open_cfw_runtime_am044_98680_024c\nL_open_cfw_runtime_am044_98680_0246:\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am044_addr_00452d42\n    bl .\nL_open_cfw_runtime_am044_98680_024c:\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am044_addr_00440656\n    bl .\nL_open_cfw_runtime_am044_98680_0252:\n    add sp, #0x3c\n    pop.w {r4, r5, r6, r7, r8, sb, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM044_988DC_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am044_988dc(void)
{
    __asm__ volatile(
        "    push.w {r3, r4, r5, r6, r7, r8, lr}\n    sub sp, #0x24\n    movs r4, r0\n    mov r8, r1\n    cmp r4, #0\n    bne L_open_cfw_runtime_am044_988dc_003c\n    ldr.w r0, [pc, #0x360]\n    str r0, [sp, #8]\n    ldr.w r0, [pc, #0x35c]\n    str r0, [sp, #4]\n    ldr.w r0, [pc, #0x35c]\n    str r0, [sp]\n    ldr.w r3, [pc, #0x5b8]\n    movw r2, #0x119\n    ldr.w r1, [pc, #0x5ac]\n    movs r0, #3\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am044_addr_0044d25c\n    bl .\nL_open_cfw_runtime_am044_988dc_0032:\n    movs r0, #0\n    movs.w r1, #-1\n    str r0, [r1]\n    b L_open_cfw_runtime_am044_988dc_0032\nL_open_cfw_runtime_am044_988dc_003c:\n    movs r5, r4\n    ldr r0, [r5, #0x58]\n    ubfx r0, r0, #8, #4\n    cmp r0, #0xb\n    blt L_open_cfw_runtime_am044_988dc_0058\n    movs.w r8, #0\nL_open_cfw_runtime_am044_988dc_004c:\n    ldr r0, [r5, #0x44]\n    cmp r8, r0\n    bne L_open_cfw_runtime_am044_988dc_006a\n    b L_open_cfw_runtime_am044_988dc_0132\nL_open_cfw_runtime_am044_988dc_0054:\n    subs.w r8, r8, #0xe10\nL_open_cfw_runtime_am044_988dc_0058:\n    cmp.w r8, #0xe10\n    bge L_open_cfw_runtime_am044_988dc_0054\nL_open_cfw_runtime_am044_988dc_005e:\n    cmp.w r8, #0\n    bpl L_open_cfw_runtime_am044_988dc_004c\n    adds.w r8, r8, #0xe10\n    b L_open_cfw_runtime_am044_988dc_005e\nL_open_cfw_runtime_am044_988dc_006a:\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am044_addr_0043f66c\n    bl .\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am044_addr_0043fd9e\n    bl .\n    movs r6, r0\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am044_addr_0043fdda\n    bl .\n    movs r7, r0\n    add r1, sp, #0x1c\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am044_98b82\n    bl .\n    add r0, sp, #0x1c\n    str r0, [sp, #8]\n    ldr r0, [r5, #0x4c]\n    uxth r0, r0\n    str r0, [sp, #4]\n    ldr r0, [r5, #0x48]\n    uxth r0, r0\n    str r0, [sp]\n    ldr r3, [r5, #0x44]\n    movs r2, r7\n    movs r1, r6\n    add r0, sp, #0xc\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am044_addr_00488cda\n    bl .\n    ldr r1, [sp, #0xc]\n    ldr r0, [r4, #0x14]\n    adds r1, r0, r1\n    str r1, [sp, #0xc]\n    ldr r1, [sp, #0x10]\n    ldr r0, [r4, #0x18]\n    adds r1, r0, r1\n    str r1, [sp, #0x10]\n    ldr r1, [sp, #0x14]\n    ldr r0, [r4, #0x14]\n    adds r1, r0, r1\n    str r1, [sp, #0x14]\n    ldr r1, [sp, #0x18]\n    ldr r0, [r4, #0x18]\n    adds r1, r0, r1\n    str r1, [sp, #0x18]\n    add r1, sp, #0xc\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am044_addr_004405d4\n    bl .\n    str.w r8, [r5, #0x44]\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am044_addr_0044dc0a\n    bl .\n    mov r8, r0\n    movs r1, #0\n    mov r0, r8\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am044_addr_0044fe8e\n    bl .\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am044_addr_00452d42\n    bl .\n    movs r1, #1\n    mov r0, r8\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am044_addr_0044fe8e\n    bl .\n    add r0, sp, #0x1c\n    str r0, [sp, #8]\n    ldr r0, [r5, #0x4c]\n    uxth r0, r0\n    str r0, [sp, #4]\n    ldr r0, [r5, #0x48]\n    uxth r0, r0\n    str r0, [sp]\n    ldr r3, [r5, #0x44]\n    movs r2, r7\n    movs r1, r6\n    add r0, sp, #0xc\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am044_addr_00488cda\n    bl .\n    ldr r1, [sp, #0xc]\n    ldr r0, [r4, #0x14]\n    adds r1, r0, r1\n    str r1, [sp, #0xc]\n    ldr r1, [sp, #0x10]\n    ldr r0, [r4, #0x18]\n    adds r1, r0, r1\n    str r1, [sp, #0x10]\n    ldr r1, [sp, #0x14]\n    ldr r0, [r4, #0x14]\n    adds r1, r0, r1\n    str r1, [sp, #0x14]\n    ldr r1, [sp, #0x18]\n    ldr r0, [r4, #0x18]\n    adds r1, r0, r1\n    str r1, [sp, #0x18]\n    add r1, sp, #0xc\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am044_addr_004405d4\n    bl .\nL_open_cfw_runtime_am044_988dc_0132:\n    add sp, #0x28\n    pop.w {r4, r5, r6, r7, r8, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM044_98A14_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am044_98a14(void)
{
    __asm__ volatile(
        "    push.w {r4, r5, r6, r7, r8, sb, lr}\n    sub sp, #0x24\n    movs r4, r0\n    mov r8, r1\n    mov sb, r2\n    cmp r4, #0\n    bne L_open_cfw_runtime_am044_98a14_003e\n    ldr.w r0, [pc, #0x224]\n    str r0, [sp, #8]\n    ldr.w r0, [pc, #0x224]\n    str r0, [sp, #4]\n    ldr.w r0, [pc, #0x220]\n    str r0, [sp]\n    ldr.w r3, [pc, #0x484]\n    mov.w r2, #0x146\n    ldr.w r1, [pc, #0x474]\n    movs r0, #3\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am044_addr_0044d25c\n    bl .\nL_open_cfw_runtime_am044_98a14_0034:\n    movs r0, #0\n    movs.w r1, #-1\n    str r0, [r1]\n    b L_open_cfw_runtime_am044_98a14_0034\nL_open_cfw_runtime_am044_98a14_003e:\n    movs r5, r4\n    ldr r0, [r5, #0x58]\n    ubfx r0, r0, #8, #4\n    cmp r0, #0xb\n    blt L_open_cfw_runtime_am044_98a14_0052\n    movs.w r8, #0\n    movs.w sb, #0\nL_open_cfw_runtime_am044_98a14_0052:\n    ldr r0, [r5, #0x50]\n    cmp r0, r8\n    bne L_open_cfw_runtime_am044_98a14_005e\n    ldr r0, [r5, #0x54]\n    cmp r0, sb\n    beq L_open_cfw_runtime_am044_98a14_0136\nL_open_cfw_runtime_am044_98a14_005e:\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am044_addr_0043f66c\n    bl .\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am044_addr_0043fd9e\n    bl .\n    movs r6, r0\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am044_addr_0043fdda\n    bl .\n    movs r7, r0\n    add r1, sp, #0x1c\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am044_98b82\n    bl .\n    add r0, sp, #0x1c\n    str r0, [sp, #8]\n    ldr r0, [r5, #0x4c]\n    uxth r0, r0\n    str r0, [sp, #4]\n    ldr r0, [r5, #0x48]\n    uxth r0, r0\n    str r0, [sp]\n    ldr r3, [r5, #0x44]\n    movs r2, r7\n    movs r1, r6\n    add r0, sp, #0xc\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am044_addr_00488cda\n    bl .\n    ldr r1, [sp, #0xc]\n    ldr r0, [r4, #0x14]\n    adds r1, r0, r1\n    str r1, [sp, #0xc]\n    ldr r1, [sp, #0x10]\n    ldr r0, [r4, #0x18]\n    adds r1, r0, r1\n    str r1, [sp, #0x10]\n    ldr r1, [sp, #0x14]\n    ldr r0, [r4, #0x14]\n    adds r1, r0, r1\n    str r1, [sp, #0x14]\n    ldr r1, [sp, #0x18]\n    ldr r0, [r4, #0x18]\n    adds r1, r0, r1\n    str r1, [sp, #0x18]\n    add r1, sp, #0xc\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am044_addr_004405d4\n    bl .\n    mov r2, sb\n    mov r1, r8\n    adds.w r0, r5, #0x50\n    str r1, [r0]\n    str r2, [r0, #4]\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am044_addr_0044dc0a\n    bl .\n    mov r8, r0\n    movs r1, #0\n    mov r0, r8\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am044_addr_0044fe8e\n    bl .\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am044_addr_00452d42\n    bl .\n    movs r1, #1\n    mov r0, r8\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am044_addr_0044fe8e\n    bl .\n    add r1, sp, #0x1c\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am044_98b82\n    bl .\n    add r0, sp, #0x1c\n    str r0, [sp, #8]\n    ldr r0, [r5, #0x4c]\n    uxth r0, r0\n    str r0, [sp, #4]\n    ldr r0, [r5, #0x48]\n    uxth r0, r0\n    str r0, [sp]\n    ldr r3, [r5, #0x44]\n    movs r2, r7\n    movs r1, r6\n    add r0, sp, #0xc\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am044_addr_00488cda\n    bl .\n    ldr r1, [sp, #0xc]\n    ldr r0, [r4, #0x14]\n    adds r1, r0, r1\n    str r1, [sp, #0xc]\n    ldr r1, [sp, #0x10]\n    ldr r0, [r4, #0x18]\n    adds r1, r0, r1\n    str r1, [sp, #0x10]\n    ldr r1, [sp, #0x14]\n    ldr r0, [r4, #0x14]\n    adds r1, r0, r1\n    str r1, [sp, #0x14]\n    ldr r1, [sp, #0x18]\n    ldr r0, [r4, #0x18]\n    adds r1, r0, r1\n    str r1, [sp, #0x18]\n    add r1, sp, #0xc\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am044_addr_004405d4\n    bl .\nL_open_cfw_runtime_am044_98a14_0136:\n    add sp, #0x24\n    pop.w {r4, r5, r6, r7, r8, sb, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM044_98B50_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am044_98b50(void)
{
    __asm__ volatile(
        "    push {r5, r6, r7, lr}\n    cmp r0, #0\n    bne L_open_cfw_runtime_am044_98b50_002e\n    ldr r0, [pc, #0xf4]\n    str r0, [sp, #8]\n    ldr r0, [pc, #0xf4]\n    str r0, [sp, #4]\n    ldr r0, [pc, #0xf4]\n    str r0, [sp]\n    ldr.w r3, [pc, #0x65c]\n    mov.w r2, #0x1d8\n    ldr.w r1, [pc, #0x348]\n    movs r0, #3\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am044_addr_0044d25c\n    bl .\nL_open_cfw_runtime_am044_98b50_0024:\n    movs r0, #0\n    movs.w r1, #-1\n    str r0, [r1]\n    b L_open_cfw_runtime_am044_98b50_0024\nL_open_cfw_runtime_am044_98b50_002e:\n    ldr r0, [r0, #0x2c]\n    pop {r1, r2, r3, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM044_98B82_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am044_98b82(void)
{
    __asm__ volatile(
        "    push {r1, r2, r3, r4, r5, lr}\n    movs r4, r0\n    movs r5, r1\n    cmp r4, #0\n    bne L_open_cfw_runtime_am044_98b82_0032\n    ldr r0, [pc, #0xbc]\n    str r0, [sp, #8]\n    ldr r0, [pc, #0xbc]\n    str r0, [sp, #4]\n    ldr r0, [pc, #0xbc]\n    str r0, [sp]\n    ldr.w r3, [pc, #0x628]\n    mov.w r2, #0x1fc\n    ldr.w r1, [pc, #0x310]\n    movs r0, #3\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am044_addr_0044d25c\n    bl .\nL_open_cfw_runtime_am044_98b82_0028:\n    movs r0, #0\n    movs.w r1, #-1\n    str r0, [r1]\n    b L_open_cfw_runtime_am044_98b82_0028\nL_open_cfw_runtime_am044_98b82_0032:\n    ldr r1, [r4, #0x3c]\n    ldr r0, [r4, #0x50]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am044_addr_00451600\n    bl .\n    str r0, [r5]\n    ldr r1, [r4, #0x40]\n    ldr r0, [r4, #0x54]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am044_addr_00451600\n    bl .\n    str r0, [r5, #4]\n    pop {r0, r1, r2, r4, r5, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM044_98C9C_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am044_98c9c(void)
{
    __asm__ volatile(
        "    push {r4, r5, r6, r7, lr}\n    sub sp, #0x44\n    movs r5, r1\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am044_addr_00450286\n    bl .\n    movs r7, r0\n    movs r1, r5\n    ldr.w r0, [pc, #0x51c]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am044_addr_004516f8\n    bl .\n    uxtb r0, r0\n    cmp r0, #1\n    bne.w #0x498eb0\n    movs r0, r5\n    ldr r0, [r0]\n    mov r8, r8\n    movs r4, r0\n    movs r6, r4\n    add r1, sp, #0x2c\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am044_98b82\n    bl .\n    cmp r7, #0x32\n    bne L_open_cfw_runtime_am044_98c9c_0054\n    ldrb.w r0, [r6, #0x58]\n    ands r0, r0, #3\n    cmp r0, #2\n    bne L_open_cfw_runtime_am044_98c9c_004c\n    ldr r1, [r6, #0x2c]\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am044_98680\n    bl .\n    b L_open_cfw_runtime_am044_98c9c_0214\nL_open_cfw_runtime_am044_98c9c_004c:\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am044_addr_00452d42\n    bl .\n    b L_open_cfw_runtime_am044_98c9c_0214\nL_open_cfw_runtime_am044_98c9c_0054:\n    cmp r7, #0x1b\n    bne L_open_cfw_runtime_am044_98c9c_00f6\n    movs r0, r5\n    ldr r0, [r0, #0x10]\n    mov r8, r8\n    movs r5, r0\n    ldr r0, [r6, #0x44]\n    cmp r0, #0\n    bne L_open_cfw_runtime_am044_98c9c_0078\n    ldr r0, [r6, #0x48]\n    cmp.w r0, #0x100\n    bne L_open_cfw_runtime_am044_98c9c_0078\n    ldr r0, [r6, #0x4c]\n    cmp.w r0, #0x100\n    beq.w #0x498eb0\nL_open_cfw_runtime_am044_98c9c_0078:\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am044_addr_0043fd9e\n    bl .\n    movs r7, r0\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am044_addr_0043fdda\n    bl .\n    movs r4, r0\n    add r0, sp, #0x2c\n    str r0, [sp, #8]\n    ldr r0, [r6, #0x4c]\n    uxth r0, r0\n    str r0, [sp, #4]\n    ldr r0, [r6, #0x48]\n    uxth r0, r0\n    str r0, [sp]\n    ldr r3, [r6, #0x44]\n    movs r2, r4\n    movs r1, r7\n    add r0, sp, #0x1c\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am044_addr_00488cda\n    bl .\n    ldr r0, [sp, #0x1c]\n    rsbs r0, r0, #0\n    ldr r1, [r5]\n    cmp r0, r1\n    bge L_open_cfw_runtime_am044_98c9c_00b2\n    ldr r0, [r5]\n    b L_open_cfw_runtime_am044_98c9c_00b6\nL_open_cfw_runtime_am044_98c9c_00b2:\n    ldr r0, [sp, #0x1c]\n    rsbs r0, r0, #0\nL_open_cfw_runtime_am044_98c9c_00b6:\n    str r0, [r5]\n    ldr r0, [sp, #0x20]\n    rsbs r0, r0, #0\n    ldr r1, [r5]\n    cmp r0, r1\n    bge L_open_cfw_runtime_am044_98c9c_00c6\n    ldr r0, [r5]\n    b L_open_cfw_runtime_am044_98c9c_00ca\nL_open_cfw_runtime_am044_98c9c_00c6:\n    ldr r0, [sp, #0x20]\n    rsbs r0, r0, #0\nL_open_cfw_runtime_am044_98c9c_00ca:\n    str r0, [r5]\n    ldr r0, [sp, #0x24]\n    subs r0, r0, r7\n    ldr r1, [r5]\n    cmp r0, r1\n    bge L_open_cfw_runtime_am044_98c9c_00da\n    ldr r7, [r5]\n    b L_open_cfw_runtime_am044_98c9c_00de\nL_open_cfw_runtime_am044_98c9c_00da:\n    ldr r0, [sp, #0x24]\n    subs r7, r0, r7\nL_open_cfw_runtime_am044_98c9c_00de:\n    str r7, [r5]\n    ldr r0, [sp, #0x28]\n    subs r0, r0, r4\n    ldr r1, [r5]\n    cmp r0, r1\n    bge L_open_cfw_runtime_am044_98c9c_00ee\n    ldr r4, [r5]\n    b L_open_cfw_runtime_am044_98c9c_00f2\nL_open_cfw_runtime_am044_98c9c_00ee:\n    ldr r0, [sp, #0x28]\n    subs r4, r0, r4\nL_open_cfw_runtime_am044_98c9c_00f2:\n    str r4, [r5]\n    b L_open_cfw_runtime_am044_98c9c_0214\nL_open_cfw_runtime_am044_98c9c_00f6:\n    cmp r7, #0x31\n    bne L_open_cfw_runtime_am044_98c9c_012a\n    ldr r0, [r6, #0x58]\n    ubfx r0, r0, #8, #4\n    cmp r0, #0xb\n    bne.w #0x498eb0\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am044_992cc\n    bl .\n    ldr r0, [r6, #0x44]\n    cmp r0, #0\n    bne L_open_cfw_runtime_am044_98c9c_0122\n    ldr r0, [r6, #0x48]\n    cmp.w r0, #0x100\n    bne L_open_cfw_runtime_am044_98c9c_0122\n    ldr r0, [r6, #0x4c]\n    cmp.w r0, #0x100\n    beq L_open_cfw_runtime_am044_98c9c_0214\nL_open_cfw_runtime_am044_98c9c_0122:\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am044_addr_00452d42\n    bl .\n    b L_open_cfw_runtime_am044_98c9c_0214\nL_open_cfw_runtime_am044_98c9c_012a:\n    cmp r7, #0x16\n    bne L_open_cfw_runtime_am044_98c9c_01ee\n    movs r0, r5\n    ldr r0, [r0, #0x10]\n    mov r8, r8\n    movs r5, r0\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am044_addr_0043fd9e\n    bl .\n    ldr r1, [r6, #0x3c]\n    cmp r1, r0\n    bne L_open_cfw_runtime_am044_98c9c_01d8\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am044_addr_0043fdda\n    bl .\n    ldr r1, [r6, #0x40]\n    cmp r1, r0\n    bne L_open_cfw_runtime_am044_98c9c_01d8\n    ldr r0, [r6, #0x48]\n    cmp.w r0, #0x100\n    bne L_open_cfw_runtime_am044_98c9c_0180\n    ldr r0, [r6, #0x4c]\n    cmp.w r0, #0x100\n    bne L_open_cfw_runtime_am044_98c9c_0180\n    ldr r0, [r6, #0x44]\n    cmp r0, #0\n    bne L_open_cfw_runtime_am044_98c9c_0180\n    ldr r0, [r6, #0x50]\n    ldr r1, [r6, #0x3c]\n    movs r2, #2\n    sdiv r1, r1, r2\n    cmp r0, r1\n    bne L_open_cfw_runtime_am044_98c9c_0180\n    ldr r0, [r6, #0x54]\n    ldr r1, [r6, #0x40]\n    movs r2, #2\n    sdiv r1, r1, r2\n    cmp r0, r1\n    beq L_open_cfw_runtime_am044_98c9c_01d8\nL_open_cfw_runtime_am044_98c9c_0180:\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am044_addr_0043fd9e\n    bl .\n    movs r7, r0\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am044_addr_0043fdda\n    bl .\n    movs r2, r0\n    add r0, sp, #0x2c\n    str r0, [sp, #8]\n    ldr r0, [r6, #0x4c]\n    uxth r0, r0\n    str r0, [sp, #4]\n    ldr r0, [r6, #0x48]\n    uxth r0, r0\n    str r0, [sp]\n    ldr r3, [r6, #0x44]\n    movs r1, r7\n    add r0, sp, #0xc\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am044_addr_00488cda\n    bl .\n    ldr r1, [sp, #0xc]\n    ldr r0, [r4, #0x14]\n    adds r1, r0, r1\n    str r1, [sp, #0xc]\n    ldr r1, [sp, #0x10]\n    ldr r0, [r4, #0x18]\n    adds r1, r0, r1\n    str r1, [sp, #0x10]\n    ldr r1, [sp, #0x14]\n    ldr r0, [r4, #0x14]\n    adds r1, r0, r1\n    str r1, [sp, #0x14]\n    ldr r1, [sp, #0x18]\n    ldr r0, [r4, #0x18]\n    adds r1, r0, r1\n    str r1, [sp, #0x18]\n    movs r2, #0\n    ldr r1, [r5]\n    add r0, sp, #0xc\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am044_addr_00450dd4\n    bl .\n    strb r0, [r5, #4]\n    b L_open_cfw_runtime_am044_98c9c_0214\nL_open_cfw_runtime_am044_98c9c_01d8:\n    add r1, sp, #0x34\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am044_addr_004408b0\n    bl .\n    movs r2, #0\n    ldr r1, [r5]\n    add r0, sp, #0x34\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am044_addr_00450dd4\n    bl .\n    strb r0, [r5, #4]\n    b L_open_cfw_runtime_am044_98c9c_0214\nL_open_cfw_runtime_am044_98c9c_01ee:\n    cmp r7, #0x34\n    bne L_open_cfw_runtime_am044_98c9c_0202\n    movs r0, r5\n    ldr r0, [r0, #0x10]\n    mov r8, r8\n    ldr r1, [r6, #0x3c]\n    str r1, [r0]\n    ldr r1, [r6, #0x40]\n    str r1, [r0, #4]\n    b L_open_cfw_runtime_am044_98c9c_0214\nL_open_cfw_runtime_am044_98c9c_0202:\n    cmp r7, #0x1d\n    beq L_open_cfw_runtime_am044_98c9c_020e\n    cmp r7, #0x20\n    beq L_open_cfw_runtime_am044_98c9c_020e\n    cmp r7, #0x1a\n    bne L_open_cfw_runtime_am044_98c9c_0214\nL_open_cfw_runtime_am044_98c9c_020e:\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am044_98ec0\n    bl .\nL_open_cfw_runtime_am044_98c9c_0214:\n    add sp, #0x44\n    pop {r4, r5, r6, r7, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM044_98EC0_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am044_98ec0(void)
{
    __asm__ volatile(
        "    push {r4, r5, r6, r7, lr}\n    sub sp, #0x114\n    movs r6, r0\n    movs r0, r6\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am044_addr_00450286\n    bl .\n    movs r7, r0\n    movs r0, r6\n    ldr r0, [r0]\n    mov r8, r8\n    movs r4, r0\n    movs r5, r4\n    cmp r7, #0x1a\n    bne L_open_cfw_runtime_am044_98ec0_0118\n    movs r0, r6\n    ldr r0, [r0, #0x10]\n    mov r8, r8\n    movs r6, r0\n    ldrb r0, [r6]\n    cmp r0, #2\n    beq.w #0x4991bc\n    ldrb.w r0, [r5, #0x58]\n    ands r0, r0, #3\n    cmp r0, #3\n    beq L_open_cfw_runtime_am044_98ec0_0044\n    ldrb.w r0, [r5, #0x58]\n    ands r0, r0, #3\n    cmp r0, #2\n    bne L_open_cfw_runtime_am044_98ec0_004a\nL_open_cfw_runtime_am044_98ec0_0044:\n    movs r0, #1\n    strb r0, [r6]\n    b L_open_cfw_runtime_am044_98ec0_02fc\nL_open_cfw_runtime_am044_98ec0_004a:\n    ldr r0, [r5, #0x58]\n    ubfx r0, r0, #2, #5\n    uxtb r0, r0\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am044_addr_00440fc4\n    bl .\n    cmp r0, #0\n    beq L_open_cfw_runtime_am044_98ec0_0060\n    movs r0, #1\n    strb r0, [r6]\n    b L_open_cfw_runtime_am044_98ec0_02fc\nL_open_cfw_runtime_am044_98ec0_0060:\n    movs r1, #0\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am044_addr_00498634\n    bl .\n    cmp r0, #0xff\n    beq L_open_cfw_runtime_am044_98ec0_0072\n    movs r0, #1\n    strb r0, [r6]\n    b L_open_cfw_runtime_am044_98ec0_02fc\nL_open_cfw_runtime_am044_98ec0_0072:\n    ldr r0, [r5, #0x44]\n    cmp r0, #0\n    beq L_open_cfw_runtime_am044_98ec0_007e\n    movs r0, #1\n    strb r0, [r6]\n    b L_open_cfw_runtime_am044_98ec0_02fc\nL_open_cfw_runtime_am044_98ec0_007e:\n    ldr r0, [r5, #0x48]\n    cmp.w r0, #0x100\n    bne L_open_cfw_runtime_am044_98ec0_00a4\n    ldr r0, [r5, #0x4c]\n    cmp.w r0, #0x100\n    bne L_open_cfw_runtime_am044_98ec0_00a4\n    movs r2, #0\n    adds.w r1, r4, #0x14\n    ldr r0, [r6, #4]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am044_addr_00450f28\n    bl .\n    cmp r0, #0\n    bne L_open_cfw_runtime_am044_98ec0_010a\n    movs r0, #1\n    strb r0, [r6]\n    b L_open_cfw_runtime_am044_98ec0_02fc\nL_open_cfw_runtime_am044_98ec0_00a4:\n    add r1, sp, #0x1c\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am044_98b82\n    bl .\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am044_addr_0043fdda\n    bl .\n    movs r7, r0\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am044_addr_0043fd9e\n    bl .\n    movs r1, r0\n    add r0, sp, #0x1c\n    str r0, [sp, #8]\n    ldr r0, [r5, #0x4c]\n    uxth r0, r0\n    str r0, [sp, #4]\n    ldr r0, [r5, #0x48]\n    uxth r0, r0\n    str r0, [sp]\n    movs r3, #0\n    movs r2, r7\n    add r0, sp, #0xc\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am044_addr_00488cda\n    bl .\n    ldr r1, [sp, #0xc]\n    ldr r0, [r4, #0x14]\n    adds r1, r0, r1\n    str r1, [sp, #0xc]\n    ldr r1, [sp, #0x10]\n    ldr r0, [r4, #0x18]\n    adds r1, r0, r1\n    str r1, [sp, #0x10]\n    ldr r1, [sp, #0x14]\n    ldr r0, [r4, #0x14]\n    adds r1, r0, r1\n    str r1, [sp, #0x14]\n    ldr r1, [sp, #0x18]\n    ldr r0, [r4, #0x18]\n    adds r1, r0, r1\n    str r1, [sp, #0x18]\n    movs r2, #0\n    add r1, sp, #0xc\n    ldr r0, [r6, #4]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am044_addr_00450f28\n    bl .\n    cmp r0, #0\n    bne L_open_cfw_runtime_am044_98ec0_010a\n    movs r0, #1\n    strb r0, [r6]\n    b L_open_cfw_runtime_am044_98ec0_02fc\nL_open_cfw_runtime_am044_98ec0_010a:\n    ldr r0, [r5, #0x30]\n    cmp r0, #0\n    beq.w #0x4991bc\n    movs r0, #1\n    strb r0, [r6]\n    b L_open_cfw_runtime_am044_98ec0_02fc\nL_open_cfw_runtime_am044_98ec0_0118:\n    cmp r7, #0x1d\n    bne.w #0x4991bc\n    ldr r0, [r5, #0x40]\n    cmp r0, #0\n    beq L_open_cfw_runtime_am044_98ec0_012a\n    ldr r0, [r5, #0x3c]\n    cmp r0, #0\n    bne L_open_cfw_runtime_am044_98ec0_012c\nL_open_cfw_runtime_am044_98ec0_012a:\n    b L_open_cfw_runtime_am044_98ec0_02fc\nL_open_cfw_runtime_am044_98ec0_012c:\n    ldr r0, [r5, #0x48]\n    cmp r0, #0\n    beq L_open_cfw_runtime_am044_98ec0_0138\n    ldr r0, [r5, #0x4c]\n    cmp r0, #0\n    bne L_open_cfw_runtime_am044_98ec0_013a\nL_open_cfw_runtime_am044_98ec0_0138:\n    b L_open_cfw_runtime_am044_98ec0_02fc\nL_open_cfw_runtime_am044_98ec0_013a:\n    movs r0, r6\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am044_addr_00451960\n    bl .\n    movs r6, r0\n    ldrb.w r0, [r5, #0x58]\n    ands r0, r0, #3\n    cmp r0, #1\n    beq L_open_cfw_runtime_am044_98ec0_015a\n    ldrb.w r0, [r5, #0x58]\n    tst.w r0, #3\n    bne.w #0x499160\nL_open_cfw_runtime_am044_98ec0_015a:\n    add r0, sp, #0x44\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am044_addr_00488918\n    bl .\n    str r6, [sp, #0x54]\n    add r2, sp, #0x44\n    movs r1, #0\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am044_addr_00452a34\n    bl .\n    add r0, sp, #0x34\n    adds.w r1, r6, #0x18\n    movs r2, #0x10\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am044_addr_00439c04\n    bl .\n    add r1, sp, #0x88\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am044_98b82\n    bl .\n    ldr r0, [r5, #0x48]\n    str r0, [sp, #0x78]\n    ldr r0, [r5, #0x4c]\n    str r0, [sp, #0x7c]\n    ldr r0, [r5, #0x44]\n    str r0, [sp, #0x74]\n    ldr r0, [r5, #0x58]\n    lsrs r0, r0, #7\n    ldrh.w r1, [sp, #0x94]\n    bfi r1, r0, #0xb, #1\n    strh.w r1, [sp, #0x94]\n    ldr r0, [r5, #0x58]\n    lsrs r0, r0, #0xc\n    ands r0, r0, #7\n    ldrb.w r1, [sp, #0x95]\n    ands r1, r1, #0xf8\n    orrs r0, r1\n    strb.w r0, [sp, #0x95]\n    ldr r0, [r5, #0x30]\n    str r0, [sp, #0xac]\n    ldr r0, [r5, #0x2c]\n    str r0, [sp, #0x60]\n    ldr r1, [r4, #0x18]\n    ldr r0, [r5, #0x40]\n    adds r1, r0, r1\n    subs r1, r1, #1\n    str r1, [sp]\n    ldr r3, [r4, #0x14]\n    ldr r0, [r5, #0x3c]\n    adds r3, r0, r3\n    subs r3, r3, #1\n    ldr r2, [r4, #0x18]\n    ldr r1, [r4, #0x14]\n    add r0, sp, #0x9c\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am044_addr_00450b5c\n    bl .\n    movs r1, #0\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am044_9865e\n    bl .\n    str r0, [sp, #0x70]\n    ldr r0, [r5, #0x58]\n    ubfx r0, r0, #8, #4\n    cmp r0, #0xa\n    bge L_open_cfw_runtime_am044_98ec0_020e\n    ldr r0, [r5, #0x38]\n    str r0, [sp]\n    ldr r3, [r5, #0x34]\n    ldr r2, [r5, #0x58]\n    lsrs r2, r2, #8\n    ands r2, r2, #0xf\n    add r1, sp, #0x9c\n    adds.w r0, r4, #0x14\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am044_addr_00451082\n    bl .\n    add r0, sp, #0x24\n    add r1, sp, #0x9c\n    movs r2, #0x10\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am044_addr_00439c04\n    bl .\n    b L_open_cfw_runtime_am044_98ec0_0288\nL_open_cfw_runtime_am044_98ec0_020e:\n    ldr r0, [r5, #0x58]\n    ubfx r0, r0, #8, #4\n    cmp r0, #0xc\n    bne L_open_cfw_runtime_am044_98ec0_027e\n    adds.w r2, r4, #0x14\n    adds.w r1, r6, #0x18\n    adds.w r0, r6, #0x18\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am044_addr_00450bcc\n    bl .\n    ldr r2, [r5, #0x38]\n    ldr r1, [r5, #0x34]\n    add r0, sp, #0x9c\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am044_addr_00450bb2\n    bl .\n    ldr r1, [r6, #0x1c]\n    ldr r0, [sp, #0xa0]\n    subs r1, r1, r0\n    ldr r0, [r5, #0x40]\n    subs r1, r1, r0\n    adds r1, r1, #1\n    ldr r0, [r5, #0x40]\n    sdiv r2, r1, r0\n    ldr r0, [r5, #0x40]\n    muls r2, r0, r2\n    ldr r1, [r6, #0x18]\n    ldr r0, [sp, #0x9c]\n    subs r1, r1, r0\n    ldr r0, [r5, #0x3c]\n    subs r1, r1, r0\n    adds r1, r1, #1\n    ldr r0, [r5, #0x3c]\n    sdiv r1, r1, r0\n    ldr r0, [r5, #0x3c]\n    muls r1, r0, r1\n    add r0, sp, #0x9c\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am044_addr_00450bb2\n    bl .\n    add r0, sp, #0x24\n    adds.w r1, r6, #0x18\n    movs r2, #0x10\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am044_addr_00439c04\n    bl .\n    ldrh.w r0, [sp, #0x94]\n    orrs r0, r0, #0x1000\n    strh.w r0, [sp, #0x94]\n    b L_open_cfw_runtime_am044_98ec0_0288\nL_open_cfw_runtime_am044_98ec0_027e:\n    add r0, sp, #0x24\n    add r1, sp, #0x9c\n    movs r2, #0x10\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am044_addr_00439c04\n    bl .\nL_open_cfw_runtime_am044_98ec0_0288:\n    add r2, sp, #0x24\n    add r1, sp, #0x44\n    movs r0, r6\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am044_addr_00488a38\n    bl .\n    adds.w r0, r6, #0x18\n    add r1, sp, #0x34\n    movs r2, #0x10\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am044_addr_00439c04\n    bl .\n    b L_open_cfw_runtime_am044_98ec0_02fc\n    ldrb.w r0, [r5, #0x58]\n    ands r0, r0, #3\n    cmp r0, #2\n    bne L_open_cfw_runtime_am044_98ec0_02d0\n    add r0, sp, #0xb0\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am044_addr_00489f5e\n    bl .\n    str r6, [sp, #0xc0]\n    add r2, sp, #0xb0\n    movs r1, #0\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am044_addr_00452988\n    bl .\n    ldr r0, [r5, #0x2c]\n    str r0, [sp, #0xcc]\n    adds.w r2, r4, #0x14\n    add r1, sp, #0xb0\n    movs r0, r6\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am044_addr_00489fe0\n    bl .\n    b L_open_cfw_runtime_am044_98ec0_02fc\nL_open_cfw_runtime_am044_98ec0_02d0:\n    ldr r0, [r5, #0x2c]\n    cmp r0, #0\n    bne L_open_cfw_runtime_am044_98ec0_02ea\n    ldr r0, [pc, #0x38]\n    str r0, [sp]\n    ldr r3, [pc, #0x38]\n    movw r2, #0x339\n    ldr r1, [pc, #0x34]\n    movs r0, #2\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am044_addr_0044d25c\n    bl .\n    b L_open_cfw_runtime_am044_98ec0_02fc\nL_open_cfw_runtime_am044_98ec0_02ea:\n    ldr r0, [pc, #0x30]\n    str r0, [sp]\n    ldr r3, [pc, #0x24]\n    movw r2, #0x33d\n    ldr r1, [pc, #0x20]\n    movs r0, #2\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am044_addr_0044d25c\n    bl .\nL_open_cfw_runtime_am044_98ec0_02fc:\n    add sp, #0x114\n    pop {r4, r5, r6, r7, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM044_991E0_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am044_991e0(void)
{
    __asm__ volatile(
        "    push.w {r4, r5, r6, r7, r8, sb, lr}\n    sub sp, #0x24\n    movs r4, r0\n    movs r5, r1\n    movs r6, r2\n    movs r7, r4\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am044_addr_0043f66c\n    bl .\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am044_addr_0043fd9e\n    bl .\n    mov r8, r0\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am044_addr_0043fdda\n    bl .\n    mov sb, r0\n    add r1, sp, #0x1c\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am044_98b82\n    bl .\n    add r0, sp, #0x1c\n    str r0, [sp, #8]\n    ldr r0, [r7, #0x4c]\n    uxth r0, r0\n    str r0, [sp, #4]\n    ldr r0, [r7, #0x48]\n    uxth r0, r0\n    str r0, [sp]\n    ldr r3, [r7, #0x44]\n    mov r2, sb\n    mov r1, r8\n    add r0, sp, #0xc\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am044_addr_00488cda\n    bl .\n    ldr r1, [sp, #0xc]\n    ldr r0, [r4, #0x14]\n    adds r1, r0, r1\n    subs r1, r1, #1\n    str r1, [sp, #0xc]\n    ldr r1, [sp, #0x10]\n    ldr r0, [r4, #0x18]\n    adds r1, r0, r1\n    subs r1, r1, #1\n    str r1, [sp, #0x10]\n    ldr r1, [sp, #0x14]\n    ldr r0, [r4, #0x14]\n    adds r1, r0, r1\n    adds r1, r1, #1\n    str r1, [sp, #0x14]\n    ldr r1, [sp, #0x18]\n    ldr r0, [r4, #0x18]\n    adds r1, r0, r1\n    adds r1, r1, #1\n    str r1, [sp, #0x18]\n    add r1, sp, #0xc\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am044_addr_004405d4\n    bl .\n    str r5, [r7, #0x48]\n    str r6, [r7, #0x4c]\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am044_addr_0044dc0a\n    bl .\n    movs r5, r0\n    movs r1, #0\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am044_addr_0044fe8e\n    bl .\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am044_addr_00452d42\n    bl .\n    movs r1, #1\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am044_addr_0044fe8e\n    bl .\n    add r0, sp, #0x1c\n    str r0, [sp, #8]\n    ldr r0, [r7, #0x4c]\n    uxth r0, r0\n    str r0, [sp, #4]\n    ldr r0, [r7, #0x48]\n    uxth r0, r0\n    str r0, [sp]\n    ldr r3, [r7, #0x44]\n    mov r2, sb\n    mov r1, r8\n    add r0, sp, #0xc\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am044_addr_00488cda\n    bl .\n    ldr r1, [sp, #0xc]\n    ldr r0, [r4, #0x14]\n    adds r1, r0, r1\n    subs r1, r1, #1\n    str r1, [sp, #0xc]\n    ldr r1, [sp, #0x10]\n    ldr r0, [r4, #0x18]\n    adds r1, r0, r1\n    subs r1, r1, #1\n    str r1, [sp, #0x10]\n    ldr r1, [sp, #0x14]\n    ldr r0, [r4, #0x14]\n    adds r1, r0, r1\n    adds r1, r1, #1\n    str r1, [sp, #0x14]\n    ldr r1, [sp, #0x18]\n    ldr r0, [r4, #0x18]\n    adds r1, r0, r1\n    adds r1, r1, #1\n    str r1, [sp, #0x18]\n    add r1, sp, #0xc\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am044_addr_004405d4\n    bl .\n    add sp, #0x24\n    pop.w {r4, r5, r6, r7, r8, sb, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM044_992CC_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am044_992cc(void)
{
    __asm__ volatile(
        "    push {r4, r5, r6, lr}\n    movs r4, r0\n    movs r5, r4\n    ldr r0, [r5, #0x58]\n    ubfx r0, r0, #8, #4\n    cmp r0, #0xb\n    bne L_open_cfw_runtime_am044_992cc_005a\n    movs r1, #0\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am044_988dc\n    bl .\n    movs r2, #0\n    movs r1, #0\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am044_98a14\n    bl .\n    ldr r0, [r5, #0x3c]\n    cmp r0, #0\n    beq L_open_cfw_runtime_am044_992cc_0084\n    ldr r0, [r5, #0x40]\n    cmp r0, #0\n    beq L_open_cfw_runtime_am044_992cc_0084\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am044_addr_0043f66c\n    bl .\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am044_addr_0043fd9e\n    bl .\n    lsls r0, r0, #8\n    ldr r1, [r5, #0x3c]\n    sdiv r6, r0, r1\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am044_addr_0043fdda\n    bl .\n    lsls r0, r0, #8\n    ldr r1, [r5, #0x40]\n    sdiv r2, r0, r1\n    movs r1, r6\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am044_991e0\n    bl .\n    b L_open_cfw_runtime_am044_992cc_0084\nL_open_cfw_runtime_am044_992cc_005a:\n    ldr r0, [r5, #0x58]\n    ubfx r0, r0, #8, #4\n    cmp r0, #0xc\n    bne L_open_cfw_runtime_am044_992cc_0084\n    movs r1, #0\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am044_988dc\n    bl .\n    movs r2, #0\n    movs r1, #0\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am044_98a14\n    bl .\n    mov.w r2, #0x100\n    mov.w r1, #0x100\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am044_991e0\n    bl .\nL_open_cfw_runtime_am044_992cc_0084:\n    pop {r4, r5, r6, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM044_99354_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am044_99354(void)
{
    __asm__ volatile(
        "    ldrb r1, [r0]\n    cmp r1, #0\n    bne L_open_cfw_runtime_am044_99354_000a\n    movs r1, #1\n    strb r1, [r0]\nL_open_cfw_runtime_am044_99354_000a:\n    bx lr\n"
    );
}
#endif

#if defined(OPEN_CFW_AM044_99360_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am044_99360(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    movs r2, #1\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am044_addr_0044bdea\n    bl .\n    pop {r1, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM044_9936A_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am044_9936a(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    movs r2, #5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am044_addr_0044bdea\n    bl .\n    pop {r1, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM044_99374_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am044_99374(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    movs r2, #7\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am044_addr_0044bdea\n    bl .\n    pop {r1, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM044_9937E_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am044_9937e(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    movs r2, #0x10\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am044_addr_0044bdea\n    bl .\n    pop {r1, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM044_99388_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am044_99388(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    movs r2, #0x12\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am044_addr_0044bdea\n    bl .\n    pop {r1, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM044_99392_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am044_99392(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    movs r2, #0x1c\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am044_addr_0044bdea\n    bl .\n    str r0, [sp]\n    ldr r0, [sp]\n    pop {r1, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM044_993A0_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am044_993a0(void)
{
    __asm__ volatile(
        "    push {r3, r4, r5, lr}\n    movs r4, r0\n    movs r5, r1\n    movs r2, #0x58\n    movs r1, r5\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am044_addr_0044bdea\n    bl .\n    movs r2, r0\n    movs r1, r5\n    movs r0, r4\n    movs r0, r2\n    mov r8, r8\n    str r0, [sp]\n    ldr r0, [sp]\n    pop {r1, r4, r5, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM044_993C0_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am044_993c0(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    movs r2, #0x5a\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am044_addr_0044bdea\n    bl .\n    pop {r1, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM044_993CA_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am044_993ca(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    movs r2, #0x5b\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am044_addr_0044bdea\n    bl .\n    pop {r1, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM044_993D4_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am044_993d4(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    movs r2, #0x5c\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am044_addr_0044bdea\n    bl .\n    pop {r1, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM044_993DE_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am044_993de(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    movs r2, #0x61\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am044_addr_0044bdea\n    bl .\n    str r0, [sp]\n    ldr r0, [sp]\n    pop {r1, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM044_993EC_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am044_993ec(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    movs r2, #0x5f\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am044_addr_0044bdea\n    bl .\n    pop {r1, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM044_993F6_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am044_993f6(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    movs r2, #0x60\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am044_addr_0044bdea\n    bl .\n    uxtb r0, r0\n    pop {r1, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM044_99402_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am044_99402(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    movs r2, #0x66\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am044_addr_0044bdea\n    bl .\n    pop {r1, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM044_9940C_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am044_9940c(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    movs r2, #0x67\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am044_addr_0044bdea\n    bl .\n    pop {r1, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM044_99416_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am044_99416(void)
{
    __asm__ volatile(
        "    push {r4, lr}\n    movs r1, r0\n    ldr.w r0, [pc, #0xc98]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am044_addr_0044cf98\n    bl .\n    movs r4, r0\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am044_addr_0044d0f0\n    bl .\n    movs r0, r4\n    pop {r4, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM044_9942E_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am044_9942e(void)
{
    __asm__ volatile(
        "    push {r1, r2, r3, r4, r5, r6, r7, lr}\n    movs r4, r0\n    movs r5, r1\n    cmp r4, #0\n    bne L_open_cfw_runtime_am044_9942e_0036\n    ldr.w r0, [pc, #0xb64]\n    str r0, [sp, #8]\n    ldr.w r0, [pc, #0xb64]\n    str r0, [sp, #4]\n    ldr.w r0, [pc, #0xb60]\n    str r0, [sp]\n    ldr.w r3, [pc, #0xb14]\n    movs r2, #0x87\n    ldr.w r1, [pc, #0xc64]\n    movs r0, #3\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am044_addr_0044d25c\n    bl .\nL_open_cfw_runtime_am044_9942e_002c:\n    movs r0, #0\n    movs.w r1, #-1\n    str r0, [r1]\n    b L_open_cfw_runtime_am044_9942e_002c\nL_open_cfw_runtime_am044_9942e_0036:\n    movs r6, r4\n    cmp r5, #0\n    bne L_open_cfw_runtime_am044_9942e_003e\n    ldr r5, [r6, #0x2c]\nL_open_cfw_runtime_am044_9942e_003e:\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am044_addr_0049aacc\n    bl .\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am044_addr_0049abd4\n    bl .\n    movs r7, r0\n    ldr r0, [r6, #0x2c]\n    cmp r0, r5\n    bne L_open_cfw_runtime_am044_9942e_00a4\n    ldrb.w r0, [r6, #0x5c]\n    ubfx r0, r0, #4, #1\n    uxtb r0, r0\n    cmp r0, #0\n    bne L_open_cfw_runtime_am044_9942e_00a4\n    movs r1, r7\n    ldr r0, [r6, #0x2c]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am044_addr_0044f76a\n    bl .\n    str r0, [r6, #0x2c]\n    ldr r0, [r6, #0x2c]\n    cmp r0, #0\n    bne L_open_cfw_runtime_am044_9942e_009c\n    ldr.w r0, [pc, #0xb0c]\n    str r0, [sp, #8]\n    ldr.w r0, [pc, #0xb08]\n    str r0, [sp, #4]\n    ldr.w r0, [pc, #0xafc]\n    str r0, [sp]\n    ldr.w r3, [pc, #0xaac]\n    movs r2, #0x93\n    ldr.w r1, [pc, #0xc00]\n    movs r0, #3\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am044_addr_0044d25c\n    bl .\nL_open_cfw_runtime_am044_9942e_0092:\n    movs r0, #0\n    movs.w r1, #-1\n    str r0, [r1]\n    b L_open_cfw_runtime_am044_9942e_0092\nL_open_cfw_runtime_am044_9942e_009c:\n    ldr r0, [r6, #0x2c]\n    cmp r0, #0\n    bne L_open_cfw_runtime_am044_9942e_0116\n    b L_open_cfw_runtime_am044_9942e_011c\nL_open_cfw_runtime_am044_9942e_00a4:\n    ldr r0, [r6, #0x2c]\n    cmp r0, #0\n    beq L_open_cfw_runtime_am044_9942e_00c2\n    ldrb.w r0, [r6, #0x5c]\n    ubfx r0, r0, #4, #1\n    uxtb r0, r0\n    cmp r0, #0\n    bne L_open_cfw_runtime_am044_9942e_00c2\n    ldr r0, [r6, #0x2c]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am044_addr_0044f758\n    bl .\n    movs r0, #0\n    str r0, [r6, #0x2c]\nL_open_cfw_runtime_am044_9942e_00c2:\n    movs r0, r7\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am044_addr_0044f718\n    bl .\n    str r0, [r6, #0x2c]\n    ldr r0, [r6, #0x2c]\n    cmp r0, #0\n    bne L_open_cfw_runtime_am044_9942e_00fc\n    ldr.w r0, [pc, #0xaac]\n    str r0, [sp, #8]\n    ldr.w r0, [pc, #0xaa8]\n    str r0, [sp, #4]\n    ldr.w r0, [pc, #0xa9c]\n    str r0, [sp]\n    ldr.w r3, [pc, #0xa4c]\n    movs r2, #0xa3\n    ldr.w r1, [pc, #0xba0]\n    movs r0, #3\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am044_addr_0044d25c\n    bl .\nL_open_cfw_runtime_am044_9942e_00f2:\n    movs r0, #0\n    movs.w r1, #-1\n    str r0, [r1]\n    b L_open_cfw_runtime_am044_9942e_00f2\nL_open_cfw_runtime_am044_9942e_00fc:\n    ldr r0, [r6, #0x2c]\n    cmp r0, #0\n    beq L_open_cfw_runtime_am044_9942e_011c\n    movs r1, r5\n    movs r0, r6\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am044_addr_0049abe0\n    bl .\n    ldrb.w r0, [r6, #0x5c]\n    ands r0, r0, #0xef\n    strb.w r0, [r6, #0x5c]\nL_open_cfw_runtime_am044_9942e_0116:\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am044_addr_0049a602\n    bl .\nL_open_cfw_runtime_am044_9942e_011c:\n    pop {r0, r1, r2, r4, r5, r6, r7, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM044_9954C_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am044_9954c(void)
{
    __asm__ volatile(
        "    push {r2, r3}\n    push {r0, r1, r2, r3, r4, r5, r6, lr}\n    movs r5, r0\n    movs r4, r1\n    cmp r5, #0\n    bne L_open_cfw_runtime_am044_9954c_0038\n    ldr.w r0, [pc, #0xa44]\n    str r0, [sp, #8]\n    ldr.w r0, [pc, #0xa44]\n    str r0, [sp, #4]\n    ldr.w r0, [pc, #0xa40]\n    str r0, [sp]\n    ldr.w r3, [pc, #0xa48]\n    movs r2, #0xb1\n    ldr.w r1, [pc, #0xb44]\n    movs r0, #3\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am044_addr_0044d25c\n    bl .\nL_open_cfw_runtime_am044_9954c_002e:\n    movs r0, #0\n    movs.w r1, #-1\n    str r0, [r1]\n    b L_open_cfw_runtime_am044_9954c_002e\nL_open_cfw_runtime_am044_9954c_0038:\n    cmp r4, #0\n    bne L_open_cfw_runtime_am044_9954c_0068\n    ldr.w r0, [pc, #0xa14]\n    str r0, [sp, #8]\n    ldr.w r0, [pc, #0xb20]\n    str r0, [sp, #4]\n    ldr.w r0, [pc, #0xa10]\n    str r0, [sp]\n    ldr.w r3, [pc, #0xa18]\n    movs r2, #0xb2\n    ldr.w r1, [pc, #0xb14]\n    movs r0, #3\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am044_addr_0044d25c\n    bl .\nL_open_cfw_runtime_am044_9954c_005e:\n    movs r0, #0\n    movs.w r1, #-1\n    str r0, [r1]\n    b L_open_cfw_runtime_am044_9954c_005e\nL_open_cfw_runtime_am044_9954c_0068:\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am044_addr_00440656\n    bl .\n    movs r6, r5\n    cmp r4, #0\n    bne L_open_cfw_runtime_am044_9954c_007c\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am044_addr_0049a602\n    bl .\n    b L_open_cfw_runtime_am044_9954c_00b6\nL_open_cfw_runtime_am044_9954c_007c:\n    ldr r0, [r6, #0x2c]\n    cmp r0, #0\n    beq L_open_cfw_runtime_am044_9954c_009a\n    ldrb.w r0, [r6, #0x5c]\n    ubfx r0, r0, #4, #1\n    uxtb r0, r0\n    cmp r0, #0\n    bne L_open_cfw_runtime_am044_9954c_009a\n    ldr r0, [r6, #0x2c]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am044_addr_0044f758\n    bl .\n    movs r0, #0\n    str r0, [r6, #0x2c]\nL_open_cfw_runtime_am044_9954c_009a:\n    add r1, sp, #0x20\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am044_addr_00489ad2\n    bl .\n    str r0, [r6, #0x2c]\n    ldrb.w r0, [r6, #0x5c]\n    ands r0, r0, #0xef\n    strb.w r0, [r6, #0x5c]\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am044_addr_0049a602\n    bl .\nL_open_cfw_runtime_am044_9954c_00b6:\n    pop {r0, r1, r2, r3, r4, r5, r6}\n    ldr pc, [sp], #0xc\n"
    );
}
#endif

#if defined(OPEN_CFW_AM044_99608_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am044_99608(void)
{
    __asm__ volatile(
        "    push {r0, r1, r2, r3, r4, r5, r6, lr}\n    movs r5, r0\n    movs r4, r1\n    cmp r5, #0\n    bne L_open_cfw_runtime_am044_99608_0036\n    ldr.w r0, [pc, #0x98c]\n    str r0, [sp, #8]\n    ldr.w r0, [pc, #0x988]\n    str r0, [sp, #4]\n    ldr.w r0, [pc, #0x988]\n    str r0, [sp]\n    ldr.w r3, [pc, #0xa94]\n    movs r2, #0xcd\n    ldr.w r1, [pc, #0xa8c]\n    movs r0, #3\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am044_addr_0044d25c\n    bl .\nL_open_cfw_runtime_am044_99608_002c:\n    movs r0, #0\n    movs.w r1, #-1\n    str r0, [r1]\n    b L_open_cfw_runtime_am044_99608_002c\nL_open_cfw_runtime_am044_99608_0036:\n    movs r6, r5\n    ldrb.w r0, [r6, #0x5c]\n    ubfx r0, r0, #4, #1\n    uxtb r0, r0\n    cmp r0, #0\n    bne L_open_cfw_runtime_am044_99608_0056\n    ldr r0, [r6, #0x2c]\n    cmp r0, #0\n    beq L_open_cfw_runtime_am044_99608_0056\n    ldr r0, [r6, #0x2c]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am044_addr_0044f758\n    bl .\n    movs r0, #0\n    str r0, [r6, #0x2c]\nL_open_cfw_runtime_am044_99608_0056:\n    cmp r4, #0\n    beq L_open_cfw_runtime_am044_99608_0068\n    ldrb.w r0, [r6, #0x5c]\n    orrs r0, r0, #0x10\n    strb.w r0, [r6, #0x5c]\n    str r4, [r6, #0x2c]\nL_open_cfw_runtime_am044_99608_0068:\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am044_addr_0049a602\n    bl .\n    pop {r0, r1, r2, r3, r4, r5, r6, pc}\n"
    );
}
#endif
