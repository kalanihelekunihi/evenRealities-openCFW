/*
 * SPDX-License-Identifier: MIT
 *
 * Source-owned exact helpers from the AM-013 retained island.
 */

#if defined(OPEN_CFW_AM013_4DBC4_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am013_4dbc4(void)
{
    __asm__ volatile(
        "    push {r0, r1, r2, r3, r4, lr}\n    cmp r0, #0\n    bne L_open_cfw_runtime_am013_4dbc4_0034\n    ldr.w r0, [pc, #0x570]\n    str r0, [sp, #8]\n    ldr.w r0, [pc, #0x56c]\n    str r0, [sp, #4]\n    ldr.w r0, [pc, #0x56c]\n    str r0, [sp]\n    ldr.w r3, [pc, #0x5f8]\n    mov.w r2, #0x124\n    ldr.w r1, [pc, #0x568]\n    movs r0, #3\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am013_addr_0044d25c\n    bl .\nL_open_cfw_runtime_am013_4dbc4_002a:\n    movs r0, #0\n    movs.w r1, #-1\n    str r0, [r1]\n    b L_open_cfw_runtime_am013_4dbc4_002a\nL_open_cfw_runtime_am013_4dbc4_0034:\n    movs r4, r0\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am013_4dca2\n    bl .\n    cmp r0, #0\n    bne L_open_cfw_runtime_am013_4dbc4_0034\n    movs r0, r4\n    add sp, #0x10\n    pop {r4, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM013_4DC0A_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am013_4dc0a(void)
{
    __asm__ volatile(
        "    push {r1, r2, r3, r4, r5, lr}\n    movs r4, r0\n    cmp r4, #0\n    bne L_open_cfw_runtime_am013_4dc0a_0036\n    ldr.w r0, [pc, #0x528]\n    str r0, [sp, #8]\n    ldr.w r0, [pc, #0x524]\n    str r0, [sp, #4]\n    ldr.w r0, [pc, #0x524]\n    str r0, [sp]\n    ldr.w r3, [pc, #0x5b4]\n    movw r2, #0x133\n    ldr.w r1, [pc, #0x520]\n    movs r0, #3\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am013_addr_0044d25c\n    bl .\nL_open_cfw_runtime_am013_4dc0a_002c:\n    movs r0, #0\n    movs.w r1, #-1\n    str r0, [r1]\n    b L_open_cfw_runtime_am013_4dc0a_002c\nL_open_cfw_runtime_am013_4dc0a_0036:\n    ldr r0, [r4, #4]\n    cmp r0, #0\n    beq L_open_cfw_runtime_am013_4dc0a_0044\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am013_4dbc4\n    bl .\n    movs r4, r0\nL_open_cfw_runtime_am013_4dc0a_0044:\n    ldr.w r5, [pc, #0x590]\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am013_addr_00482cd8\n    bl .\n    movs r1, r0\n    b L_open_cfw_runtime_am013_4dc0a_005a\nL_open_cfw_runtime_am013_4dc0a_0052:\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am013_addr_00482cf0\n    bl .\n    movs r1, r0\nL_open_cfw_runtime_am013_4dc0a_005a:\n    cmp r1, #0\n    beq L_open_cfw_runtime_am013_4dc0a_007c\n    movs r0, #0\n    b L_open_cfw_runtime_am013_4dc0a_0064\nL_open_cfw_runtime_am013_4dc0a_0062:\n    adds r0, r0, #1\nL_open_cfw_runtime_am013_4dc0a_0064:\n    ldr.w r2, [r1, #0x2d4]\n    cmp r0, r2\n    bhs L_open_cfw_runtime_am013_4dc0a_0052\n    ldr.w r2, [r1, #0x2b8]\n    ldr.w r2, [r2, r0, lsl #2]\n    cmp r2, r4\n    bne L_open_cfw_runtime_am013_4dc0a_0062\n    movs r0, r1\n    b L_open_cfw_runtime_am013_4dc0a_0096\nL_open_cfw_runtime_am013_4dc0a_007c:\n    ldr.w r0, [pc, #0x55c]\n    str r0, [sp]\n    ldr.w r3, [pc, #0x54c]\n    movw r2, #0x143\n    ldr.w r1, [pc, #0x4b8]\n    movs r0, #2\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am013_addr_0044d25c\n    bl .\n    movs r0, #0\nL_open_cfw_runtime_am013_4dc0a_0096:\n    pop {r1, r2, r3, r4, r5, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM013_4DCA2_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am013_4dca2(void)
{
    __asm__ volatile(
        "    push {r5, r6, r7, lr}\n    cmp r0, #0\n    bne L_open_cfw_runtime_am013_4dca2_000a\n    movs r0, #0\n    b L_open_cfw_runtime_am013_4dca2_003e\nL_open_cfw_runtime_am013_4dca2_000a:\n    cmp r0, #0\n    bne L_open_cfw_runtime_am013_4dca2_003c\n    ldr.w r0, [pc, #0x488]\n    str r0, [sp, #8]\n    ldr.w r0, [pc, #0x488]\n    str r0, [sp, #4]\n    ldr.w r0, [pc, #0x484]\n    str r0, [sp]\n    ldr.w r3, [pc, #0x524]\n    mov.w r2, #0x14a\n    ldr.w r1, [pc, #0x484]\n    movs r0, #3\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am013_addr_0044d25c\n    bl .\nL_open_cfw_runtime_am013_4dca2_0032:\n    movs r0, #0\n    movs.w r1, #-1\n    str r0, [r1]\n    b L_open_cfw_runtime_am013_4dca2_0032\nL_open_cfw_runtime_am013_4dca2_003c:\n    ldr r0, [r0, #4]\nL_open_cfw_runtime_am013_4dca2_003e:\n    pop {r1, r2, r3, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM013_4DCE2_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am013_4dce2(void)
{
    __asm__ volatile(
        "    push {r5, r6, r7, lr}\n    cmp r0, #0\n    bne L_open_cfw_runtime_am013_4dce2_0034\n    ldr.w r0, [pc, #0x450]\n    str r0, [sp, #8]\n    ldr.w r0, [pc, #0x450]\n    str r0, [sp, #4]\n    ldr.w r0, [pc, #0x44c]\n    str r0, [sp]\n    ldr.w r3, [pc, #0x4f0]\n    movw r2, #0x151\n    ldr.w r1, [pc, #0x44c]\n    movs r0, #3\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am013_addr_0044d25c\n    bl .\nL_open_cfw_runtime_am013_4dce2_002a:\n    movs r0, #0\n    movs.w r1, #-1\n    str r0, [r1]\n    b L_open_cfw_runtime_am013_4dce2_002a\nL_open_cfw_runtime_am013_4dce2_0034:\n    ldr r2, [r0, #8]\n    cmp r2, #0\n    bne L_open_cfw_runtime_am013_4dce2_003e\n    movs r0, #0\n    b L_open_cfw_runtime_am013_4dce2_006a\nL_open_cfw_runtime_am013_4dce2_003e:\n    cmp r1, #0\n    bpl L_open_cfw_runtime_am013_4dce2_0054\n    ldr r2, [r0, #8]\n    ldrh r2, [r2, #0x30]\n    adds r1, r1, r2\n    cmp r1, #0\n    bpl L_open_cfw_runtime_am013_4dce2_0050\n    movs r0, #0\n    b L_open_cfw_runtime_am013_4dce2_006a\nL_open_cfw_runtime_am013_4dce2_0050:\n    movs r2, r1\n    b L_open_cfw_runtime_am013_4dce2_0056\nL_open_cfw_runtime_am013_4dce2_0054:\n    movs r2, r1\nL_open_cfw_runtime_am013_4dce2_0056:\n    ldr r3, [r0, #8]\n    ldrh r3, [r3, #0x30]\n    cmp r2, r3\n    blo L_open_cfw_runtime_am013_4dce2_0062\n    movs r0, #0\n    b L_open_cfw_runtime_am013_4dce2_006a\nL_open_cfw_runtime_am013_4dce2_0062:\n    ldr r0, [r0, #8]\n    ldr r0, [r0]\n    ldr.w r0, [r0, r1, lsl #2]\nL_open_cfw_runtime_am013_4dce2_006a:\n    pop {r1, r2, r3, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM013_4DD4E_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am013_4dd4e(void)
{
    __asm__ volatile(
        "    push {r1, r2, r3, r4, r5, lr}\n    cmp r0, #0\n    bne L_open_cfw_runtime_am013_4dd4e_0034\n    ldr.w r0, [pc, #0x3e4]\n    str r0, [sp, #8]\n    ldr.w r0, [pc, #0x3e4]\n    str r0, [sp, #4]\n    ldr.w r0, [pc, #0x3e0]\n    str r0, [sp]\n    ldr.w r3, [pc, #0x488]\n    movw r2, #0x165\n    ldr.w r1, [pc, #0x3e0]\n    movs r0, #3\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am013_addr_0044d25c\n    bl .\nL_open_cfw_runtime_am013_4dd4e_002a:\n    movs r0, #0\n    movs.w r1, #-1\n    str r0, [r1]\n    b L_open_cfw_runtime_am013_4dd4e_002a\nL_open_cfw_runtime_am013_4dd4e_0034:\n    ldr r3, [r0, #8]\n    cmp r3, #0\n    bne L_open_cfw_runtime_am013_4dd4e_003e\n    movs r0, #0\n    b L_open_cfw_runtime_am013_4dd4e_009a\nL_open_cfw_runtime_am013_4dd4e_003e:\n    ldr r3, [r0, #8]\n    ldrh r3, [r3, #0x30]\n    cmp r1, #0\n    bmi L_open_cfw_runtime_am013_4dd4e_006e\n    movs r4, #0\n    b L_open_cfw_runtime_am013_4dd4e_004e\nL_open_cfw_runtime_am013_4dd4e_004a:\n    subs r1, r1, #1\nL_open_cfw_runtime_am013_4dd4e_004c:\n    adds r4, r4, #1\nL_open_cfw_runtime_am013_4dd4e_004e:\n    cmp r4, r3\n    bge L_open_cfw_runtime_am013_4dd4e_0098\n    ldr r5, [r0, #8]\n    ldr r5, [r5]\n    ldr.w r5, [r5, r4, lsl #2]\n    ldr r5, [r5]\n    cmp r5, r2\n    bne L_open_cfw_runtime_am013_4dd4e_004c\n    cmp r1, #0\n    bne L_open_cfw_runtime_am013_4dd4e_004a\n    ldr r0, [r0, #8]\n    ldr r0, [r0]\n    ldr.w r0, [r0, r4, lsl #2]\n    b L_open_cfw_runtime_am013_4dd4e_009a\nL_open_cfw_runtime_am013_4dd4e_006e:\n    adds r1, r1, #1\n    subs r3, r3, #1\n    b L_open_cfw_runtime_am013_4dd4e_0078\nL_open_cfw_runtime_am013_4dd4e_0074:\n    adds r1, r1, #1\nL_open_cfw_runtime_am013_4dd4e_0076:\n    subs r3, r3, #1\nL_open_cfw_runtime_am013_4dd4e_0078:\n    cmp r3, #0\n    bmi L_open_cfw_runtime_am013_4dd4e_0098\n    ldr r4, [r0, #8]\n    ldr r4, [r4]\n    ldr.w r4, [r4, r3, lsl #2]\n    ldr r4, [r4]\n    cmp r4, r2\n    bne L_open_cfw_runtime_am013_4dd4e_0076\n    cmp r1, #0\n    bne L_open_cfw_runtime_am013_4dd4e_0074\n    ldr r0, [r0, #8]\n    ldr r0, [r0]\n    ldr.w r0, [r0, r3, lsl #2]\n    b L_open_cfw_runtime_am013_4dd4e_009a\nL_open_cfw_runtime_am013_4dd4e_0098:\n    movs r0, #0\nL_open_cfw_runtime_am013_4dd4e_009a:\n    pop {r1, r2, r3, r4, r5, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM013_4DDEA_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am013_4ddea(void)
{
    __asm__ volatile(
        "    push {r5, r6, r7, lr}\n    cmp r0, #0\n    bne L_open_cfw_runtime_am013_4ddea_0034\n    ldr.w r0, [pc, #0x348]\n    str r0, [sp, #8]\n    ldr.w r0, [pc, #0x348]\n    str r0, [sp, #4]\n    ldr.w r0, [pc, #0x344]\n    str r0, [sp]\n    ldr.w r3, [pc, #0x3f4]\n    movw r2, #0x195\n    ldr.w r1, [pc, #0x344]\n    movs r0, #3\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am013_addr_0044d25c\n    bl .\nL_open_cfw_runtime_am013_4ddea_002a:\n    movs r0, #0\n    movs.w r1, #-1\n    str r0, [r1]\n    b L_open_cfw_runtime_am013_4ddea_002a\nL_open_cfw_runtime_am013_4ddea_0034:\n    ldr r1, [r0, #8]\n    cmp r1, #0\n    bne L_open_cfw_runtime_am013_4ddea_003e\n    movs r0, #0\n    b L_open_cfw_runtime_am013_4ddea_0042\nL_open_cfw_runtime_am013_4ddea_003e:\n    ldr r0, [r0, #8]\n    ldrh r0, [r0, #0x30]\nL_open_cfw_runtime_am013_4ddea_0042:\n    pop {r1, r2, r3, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM013_4DE2E_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am013_4de2e(void)
{
    __asm__ volatile(
        "    push {r0, r1, r2, r3, r4, lr}\n    movs r2, r0\n    cmp r2, #0\n    bne L_open_cfw_runtime_am013_4de2e_0036\n    ldr.w r0, [pc, #0x304]\n    str r0, [sp, #8]\n    ldr.w r0, [pc, #0x300]\n    str r0, [sp, #4]\n    ldr.w r0, [pc, #0x300]\n    str r0, [sp]\n    ldr.w r3, [pc, #0x3b0]\n    mov.w r2, #0x19c\n    ldr.w r1, [pc, #0x2fc]\n    movs r0, #3\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am013_addr_0044d25c\n    bl .\nL_open_cfw_runtime_am013_4de2e_002c:\n    movs r0, #0\n    movs.w r1, #-1\n    str r0, [r1]\n    b L_open_cfw_runtime_am013_4de2e_002c\nL_open_cfw_runtime_am013_4de2e_0036:\n    ldr r0, [r2, #8]\n    cmp r0, #0\n    bne L_open_cfw_runtime_am013_4de2e_0040\n    movs r0, #0\n    b L_open_cfw_runtime_am013_4de2e_0060\nL_open_cfw_runtime_am013_4de2e_0040:\n    movs r0, #0\n    movs r3, #0\n    b L_open_cfw_runtime_am013_4de2e_0058\nL_open_cfw_runtime_am013_4de2e_0046:\n    ldr r4, [r2, #8]\n    ldr r4, [r4]\n    ldr.w r4, [r4, r3, lsl #2]\n    ldr r4, [r4]\n    cmp r4, r1\n    bne L_open_cfw_runtime_am013_4de2e_0056\n    adds r0, r0, #1\nL_open_cfw_runtime_am013_4de2e_0056:\n    adds r3, r3, #1\nL_open_cfw_runtime_am013_4de2e_0058:\n    ldr r4, [r2, #8]\n    ldrh r4, [r4, #0x30]\n    cmp r3, r4\n    blo L_open_cfw_runtime_am013_4de2e_0046\nL_open_cfw_runtime_am013_4de2e_0060:\n    add sp, #0x10\n    pop {r4, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM013_4DE92_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am013_4de92(void)
{
    __asm__ volatile(
        "    push {r0, r1, r2, r3, r4, lr}\n    movs r4, r0\n    cmp r4, #0\n    bne L_open_cfw_runtime_am013_4de92_0036\n    ldr.w r0, [pc, #0x2a0]\n    str r0, [sp, #8]\n    ldr.w r0, [pc, #0x29c]\n    str r0, [sp, #4]\n    ldr.w r0, [pc, #0x29c]\n    str r0, [sp]\n    ldr.w r3, [pc, #0x350]\n    movw r2, #0x217\n    ldr.w r1, [pc, #0x298]\n    movs r0, #3\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am013_addr_0044d25c\n    bl .\nL_open_cfw_runtime_am013_4de92_002c:\n    movs r0, #0\n    movs.w r1, #-1\n    str r0, [r1]\n    b L_open_cfw_runtime_am013_4de92_002c\nL_open_cfw_runtime_am013_4de92_0036:\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am013_4dca2\n    bl .\n    cmp r0, #0\n    bne L_open_cfw_runtime_am013_4de92_0048\n    movs.w r0, #-1\nL_open_cfw_runtime_am013_4de92_0044:\n    add sp, #0x10\n    pop {r4, pc}\nL_open_cfw_runtime_am013_4de92_0048:\n    movs r1, #0\n    movs r1, #0\n    b L_open_cfw_runtime_am013_4de92_0050\nL_open_cfw_runtime_am013_4de92_004e:\n    adds r1, r1, #1\nL_open_cfw_runtime_am013_4de92_0050:\n    ldr r2, [r0, #8]\n    ldrh r2, [r2, #0x30]\n    cmp r1, r2\n    bge L_open_cfw_runtime_am013_4de92_0068\n    ldr r2, [r0, #8]\n    ldr r2, [r2]\n    ldr.w r2, [r2, r1, lsl #2]\n    cmp r2, r4\n    bne L_open_cfw_runtime_am013_4de92_004e\n    movs r0, r1\n    b L_open_cfw_runtime_am013_4de92_0044\nL_open_cfw_runtime_am013_4de92_0068:\n    adr r0, #0x58\n    str r0, [sp, #4]\n    ldr.w r0, [pc, #0x2d4]\n    str r0, [sp]\n    ldr.w r3, [pc, #0x2f8]\n    movw r2, #0x222\n    ldr.w r1, [pc, #0x240]\n    movs r0, #3\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am013_addr_0044d25c\n    bl .\nL_open_cfw_runtime_am013_4de92_0084:\n    movs r0, #0\n    movs.w r1, #-1\n    str r0, [r1]\n    b L_open_cfw_runtime_am013_4de92_0084\n"
    );
}
#endif

#if defined(OPEN_CFW_AM013_4DF60_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am013_4df60(void)
{
    __asm__ volatile(
        "    push {r3, r4, r5, lr}\n    movs r4, r0\n    movs r5, r1\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am013_addr_00452f0c\n    bl .\n    cmp r0, #0\n    beq L_open_cfw_runtime_am013_4df60_0016\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am013_addr_00452fec\n    bl .\nL_open_cfw_runtime_am013_4df60_0016:\n    movs r1, r5\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am013_addr_00452f26\n    bl .\n    pop {r0, r4, r5, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM013_4DF80_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am013_4df80(void)
{
    __asm__ volatile(
        "L_open_cfw_runtime_am013_4df80_0000:\n    push {r4, r5, r6, lr}\n    movs r5, r0\n    ldrh r0, [r5, #0x2a]\n    ubfx r0, r0, #0xc, #1\n    uxth r0, r0\n    cmp r0, #0\n    bne.w #0x44e138\n    ldrh r0, [r5, #0x2a]\n    orrs r0, r0, #0x1000\n    strh r0, [r5, #0x2a]\n    movs r2, #0\n    movs r1, #0x29\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am013_addr_00451670\n    bl .\n    uxtb r0, r0\n    cmp r0, #0\n    bne L_open_cfw_runtime_am013_4df80_0036\n    ldrh r1, [r5, #0x2a]\n    movw r0, #0xefff\n    ands r1, r0\n    strh r1, [r5, #0x2a]\n    b L_open_cfw_runtime_am013_4df80_01b8\nL_open_cfw_runtime_am013_4df80_0036:\n    ldr r0, [r5, #8]\n    cmp r0, #0\n    beq L_open_cfw_runtime_am013_4df80_0044\n    ldr r0, [r5, #8]\n    adds r0, #8\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am013_addr_00450228\n    bl .\nL_open_cfw_runtime_am013_4df80_0044:\n    movs r1, #0\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am013_4dce2\n    bl .\n    b L_open_cfw_runtime_am013_4df80_005a\nL_open_cfw_runtime_am013_4df80_004e:\n    bl L_open_cfw_runtime_am013_4df80_0000\n    movs r1, #0\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am013_4dce2\n    bl .\nL_open_cfw_runtime_am013_4df80_005a:\n    cmp r0, #0\n    bne L_open_cfw_runtime_am013_4df80_004e\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am013_addr_0043e1be\n    bl .\n    movs r6, r0\n    movs r0, #0\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am013_addr_00452edc\n    bl .\n    movs r4, r0\n    b L_open_cfw_runtime_am013_4df80_00d2\nL_open_cfw_runtime_am013_4df80_0070:\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am013_addr_00452f00\n    bl .\n    movs r1, r0\n    uxtb r1, r1\n    cmp r1, #1\n    beq L_open_cfw_runtime_am013_4df80_0084\n    uxtb r0, r0\n    cmp r0, #3\n    bne L_open_cfw_runtime_am013_4df80_00b2\nL_open_cfw_runtime_am013_4df80_0084:\n    ldr r0, [r4, #0x68]\n    cmp r0, r5\n    beq L_open_cfw_runtime_am013_4df80_0096\n    ldr r0, [r4, #0x6c]\n    cmp r0, r5\n    beq L_open_cfw_runtime_am013_4df80_0096\n    ldr r0, [r4, #0x70]\n    cmp r0, r5\n    bne L_open_cfw_runtime_am013_4df80_009e\nL_open_cfw_runtime_am013_4df80_0096:\n    movs r1, r5\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am013_4df60\n    bl .\nL_open_cfw_runtime_am013_4df80_009e:\n    ldr r0, [r4, #0x74]\n    cmp r0, r5\n    bne L_open_cfw_runtime_am013_4df80_00a8\n    movs r0, #0\n    str r0, [r4, #0x74]\nL_open_cfw_runtime_am013_4df80_00a8:\n    ldr r0, [r4, #0x78]\n    cmp r0, r5\n    bne L_open_cfw_runtime_am013_4df80_00b2\n    movs r0, #0\n    str r0, [r4, #0x78]\nL_open_cfw_runtime_am013_4df80_00b2:\n    ldr.w r0, [r4, #0xb8]\n    cmp r0, r6\n    bne L_open_cfw_runtime_am013_4df80_00ca\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am013_addr_00452ffa\n    bl .\n    cmp r5, r0\n    bne L_open_cfw_runtime_am013_4df80_00ca\n    movs r1, r5\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am013_4df60\n    bl .\nL_open_cfw_runtime_am013_4df80_00ca:\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am013_addr_00452edc\n    bl .\n    movs r4, r0\nL_open_cfw_runtime_am013_4df80_00d2:\n    cmp r4, #0\n    bne L_open_cfw_runtime_am013_4df80_0070\n    movs r0, #1\n    b L_open_cfw_runtime_am013_4df80_00e2\nL_open_cfw_runtime_am013_4df80_00da:\n    movs r1, r5\n    ldr r0, [pc, #0x1a8]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am013_addr_00484052\n    bl .\nL_open_cfw_runtime_am013_4df80_00e2:\n    uxtb r0, r0\n    cmp r0, #1\n    beq L_open_cfw_runtime_am013_4df80_00da\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am013_addr_0044d16e\n    bl .\n    ldr r0, [r5, #4]\n    cmp r0, #0\n    bne L_open_cfw_runtime_am013_4df80_0154\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am013_4dc0a\n    bl .\n    movs r4, r0\n    movs r0, #0\n    b L_open_cfw_runtime_am013_4df80_0102\nL_open_cfw_runtime_am013_4df80_0100:\n    adds r0, r0, #1\nL_open_cfw_runtime_am013_4df80_0102:\n    ldr.w r1, [r4, #0x2d4]\n    cmp r0, r1\n    bhs L_open_cfw_runtime_am013_4df80_0116\n    ldr.w r1, [r4, #0x2b8]\n    ldr.w r1, [r1, r0, lsl #2]\n    cmp r1, r5\n    bne L_open_cfw_runtime_am013_4df80_0100\nL_open_cfw_runtime_am013_4df80_0116:\n    b L_open_cfw_runtime_am013_4df80_012c\nL_open_cfw_runtime_am013_4df80_0118:\n    ldr.w r1, [r4, #0x2b8]\n    add.w r1, r1, r0, lsl #2\n    ldr r1, [r1, #4]\n    ldr.w r2, [r4, #0x2b8]\n    str.w r1, [r2, r0, lsl #2]\n    adds r0, r0, #1\nL_open_cfw_runtime_am013_4df80_012c:\n    ldr.w r1, [r4, #0x2d4]\n    subs r1, r1, #1\n    cmp r0, r1\n    blo L_open_cfw_runtime_am013_4df80_0118\n    ldr.w r0, [r4, #0x2d4]\n    subs r0, r0, #1\n    str.w r0, [r4, #0x2d4]\n    ldr.w r1, [r4, #0x2d4]\n    lsls r1, r1, #2\n    ldr.w r0, [r4, #0x2b8]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am013_addr_0044f76a\n    bl .\n    str.w r0, [r4, #0x2b8]\n    b L_open_cfw_runtime_am013_4df80_01b2\nL_open_cfw_runtime_am013_4df80_0154:\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am013_4de92\n    bl .\n    b L_open_cfw_runtime_am013_4df80_017c\nL_open_cfw_runtime_am013_4df80_015c:\n    ldr r1, [r5, #4]\n    ldr r1, [r1, #8]\n    ldr r1, [r1]\n    movs r2, r0\n    uxth r2, r2\n    ldr r3, [r5, #4]\n    ldr r3, [r3, #8]\n    ldr r3, [r3]\n    movs r4, r0\n    uxth r4, r4\n    add.w r3, r3, r4, lsl #2\n    ldr r3, [r3, #4]\n    str.w r3, [r1, r2, lsl #2]\n    adds r0, r0, #1\nL_open_cfw_runtime_am013_4df80_017c:\n    movs r1, r0\n    uxth r1, r1\n    ldr r2, [r5, #4]\n    ldr r2, [r2, #8]\n    ldrh r2, [r2, #0x30]\n    subs r2, r2, #1\n    cmp r1, r2\n    blt L_open_cfw_runtime_am013_4df80_015c\n    ldr r0, [r5, #4]\n    ldr r0, [r0, #8]\n    ldrh r0, [r0, #0x30]\n    subs r0, r0, #1\n    ldr r1, [r5, #4]\n    ldr r1, [r1, #8]\n    strh r0, [r1, #0x30]\n    ldr r0, [r5, #4]\n    ldr r0, [r0, #8]\n    ldrh r1, [r0, #0x30]\n    lsls r1, r1, #2\n    ldr r0, [r5, #4]\n    ldr r0, [r0, #8]\n    ldr r0, [r0]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am013_addr_0044f76a\n    bl .\n    ldr r1, [r5, #4]\n    ldr r1, [r1, #8]\n    str r0, [r1]\nL_open_cfw_runtime_am013_4df80_01b2:\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am013_addr_0044f758\n    bl .\nL_open_cfw_runtime_am013_4df80_01b8:\n    pop {r4, r5, r6, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM013_4E164_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am013_4e164(void)
{
    __asm__ volatile(
        "    push {r5, r6, r7, lr}\n    cmp r0, #0\n    bne L_open_cfw_runtime_am013_4e164_002a\n    ldr r0, [pc, #0xa0]\n    str r0, [sp, #8]\n    ldr r0, [pc, #0xa0]\n    str r0, [sp, #4]\n    ldr r0, [pc, #0xa0]\n    str r0, [sp]\n    ldr r3, [pc, #0xa0]\n    movw r2, #0x2fb\n    ldr r1, [pc, #0x74]\n    movs r0, #3\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am013_addr_0044d25c\n    bl .\nL_open_cfw_runtime_am013_4e164_0020:\n    movs r0, #0\n    movs.w r1, #-1\n    str r0, [r1]\n    b L_open_cfw_runtime_am013_4e164_0020\nL_open_cfw_runtime_am013_4e164_002a:\n    ldr r1, [r0, #8]\n    cmp r1, #0\n    bne L_open_cfw_runtime_am013_4e164_0034\n    movs r0, #0\n    b L_open_cfw_runtime_am013_4e164_0062\nL_open_cfw_runtime_am013_4e164_0034:\n    ldr r1, [r0, #8]\n    ldrh r2, [r1, #0x30]\n    movs r1, #0\n    b L_open_cfw_runtime_am013_4e164_003e\nL_open_cfw_runtime_am013_4e164_003c:\n    adds r1, r1, #1\nL_open_cfw_runtime_am013_4e164_003e:\n    cmp r1, r2\n    bge L_open_cfw_runtime_am013_4e164_0060\n    ldr r3, [r0, #8]\n    ldr r3, [r3]\n    ldr.w r3, [r3, r1, lsl #2]\n    ldrh r3, [r3, #0x2a]\n    ubfx r3, r3, #0xc, #1\n    uxth r3, r3\n    cmp r3, #0\n    bne L_open_cfw_runtime_am013_4e164_003c\n    ldr r0, [r0, #8]\n    ldr r0, [r0]\n    ldr.w r0, [r0, r1, lsl #2]\n    b L_open_cfw_runtime_am013_4e164_0062\nL_open_cfw_runtime_am013_4e164_0060:\n    movs r0, #0\nL_open_cfw_runtime_am013_4e164_0062:\n    pop {r1, r2, r3, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM013_4E21C_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am013_4e21c(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    movs r2, #1\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am013_addr_0044bdea\n    bl .\n    pop {r1, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM013_4E226_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am013_4e226(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    movs r2, #3\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am013_addr_0044bdea\n    bl .\n    pop {r1, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM013_4E230_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am013_4e230(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    movs r2, #0x10\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am013_addr_0044bdea\n    bl .\n    pop {r1, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM013_4E23A_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am013_4e23a(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    movs r2, #0x11\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am013_addr_0044bdea\n    bl .\n    pop {r1, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM013_4E244_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am013_4e244(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    movs r2, #0x12\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am013_addr_0044bdea\n    bl .\n    pop {r1, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM013_4E24E_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am013_4e24e(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    movs r2, #0x13\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am013_addr_0044bdea\n    bl .\n    pop {r1, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM013_4E258_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am013_4e258(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    movs r2, #0x19\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am013_addr_0044bdea\n    bl .\n    pop {r1, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM013_4E262_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am013_4e262(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    movs r2, #0x1a\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am013_addr_0044bdea\n    bl .\n    pop {r1, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM013_4E26C_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am013_4e26c(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    movs r2, #0x1b\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am013_addr_0044bdea\n    bl .\n    pop {r1, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM013_4E276_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am013_4e276(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    movs r2, #0x1d\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am013_addr_0044bdea\n    bl .\n    uxtb r0, r0\n    pop {r1, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM013_4E282_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am013_4e282(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    movs r2, #0x32\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am013_addr_0044bdea\n    bl .\n    uxtb r0, r0\n    pop {r1, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM013_4E28E_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am013_4e28e(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    movs r2, #0x30\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am013_addr_0044bdea\n    bl .\n    pop {r1, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM013_4E298_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am013_4e298(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    movs r2, #0x34\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am013_addr_0044bdea\n    bl .\n    uxtb r0, r0\n    pop {r1, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM013_4E2A4_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am013_4e2a4(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    movs r2, #0x27\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am013_addr_0044bdea\n    bl .\n    uxtb r0, r0\n    pop {r1, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM013_4E2B0_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am013_4e2b0(void)
{
    __asm__ volatile(
        "    push {r3, r4, r5, r6, r7, lr}\n    movs r4, r0\n    movs r5, r1\n    movs r1, r5\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am013_4e244\n    bl .\n    movs r6, r0\n    movs r1, r5\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am013_4e28e\n    bl .\n    movs r7, r0\n    movs r1, r5\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am013_4e298\n    bl .\n    lsls r0, r0, #0x1d\n    bpl L_open_cfw_runtime_am013_4e2b0_002a\n    adds r6, r7, r6\n    b L_open_cfw_runtime_am013_4e2b0_002a\nL_open_cfw_runtime_am013_4e2b0_002a:\n    movs r0, r6\n    pop {r1, r4, r5, r6, r7, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM013_4E2DE_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am013_4e2de(void)
{
    __asm__ volatile(
        "    push {r3, r4, r5, r6, r7, lr}\n    movs r4, r0\n    movs r5, r1\n    movs r1, r5\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am013_4e24e\n    bl .\n    movs r6, r0\n    movs r1, r5\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am013_4e28e\n    bl .\n    movs r7, r0\n    movs r1, r5\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am013_4e298\n    bl .\n    lsls r0, r0, #0x1c\n    bpl L_open_cfw_runtime_am013_4e2de_002a\n    adds r6, r7, r6\n    b L_open_cfw_runtime_am013_4e2de_002a\nL_open_cfw_runtime_am013_4e2de_002a:\n    movs r0, r6\n    pop {r1, r4, r5, r6, r7, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM013_4E30C_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am013_4e30c(void)
{
    __asm__ volatile(
        "    push {r3, r4, r5, r6, r7, lr}\n    movs r4, r0\n    movs r5, r1\n    movs r1, r5\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am013_4e230\n    bl .\n    movs r6, r0\n    movs r1, r5\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am013_4e28e\n    bl .\n    movs r7, r0\n    movs r1, r5\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am013_4e298\n    bl .\n    lsls r0, r0, #0x1e\n    bpl L_open_cfw_runtime_am013_4e30c_002a\n    adds r6, r7, r6\n    b L_open_cfw_runtime_am013_4e30c_002a\nL_open_cfw_runtime_am013_4e30c_002a:\n    movs r0, r6\n    pop {r1, r4, r5, r6, r7, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM013_4E33A_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am013_4e33a(void)
{
    __asm__ volatile(
        "    push {r3, r4, r5, r6, r7, lr}\n    movs r4, r0\n    movs r5, r1\n    movs r1, r5\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am013_4e23a\n    bl .\n    movs r6, r0\n    movs r1, r5\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am013_4e28e\n    bl .\n    movs r7, r0\n    movs r1, r5\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am013_4e298\n    bl .\n    lsls r0, r0, #0x1f\n    bpl L_open_cfw_runtime_am013_4e33a_002a\n    adds r6, r7, r6\n    b L_open_cfw_runtime_am013_4e33a_002a\nL_open_cfw_runtime_am013_4e33a_002a:\n    movs r0, r6\n    pop {r1, r4, r5, r6, r7, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM013_4E368_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am013_4e368(void)
{
    __asm__ volatile(
        "    push {r1, r2, r3, r4, r5, lr}\n    movs r4, r0\n    movs r5, r1\n    cmp r4, #0\n    bne L_open_cfw_runtime_am013_4e368_0036\n    ldr.w r0, [pc, #0x780]\n    str r0, [sp, #8]\n    ldr.w r0, [pc, #0x77c]\n    str r0, [sp, #4]\n    ldr.w r0, [pc, #0x77c]\n    str r0, [sp]\n    ldr.w r3, [pc, #0x778]\n    movs r2, #0x3c\n    ldr.w r1, [pc, #0x778]\n    movs r0, #3\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am013_addr_0044d25c\n    bl .\nL_open_cfw_runtime_am013_4e368_002c:\n    movs r0, #0\n    movs.w r1, #-1\n    str r0, [r1]\n    b L_open_cfw_runtime_am013_4e368_002c\nL_open_cfw_runtime_am013_4e368_0036:\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am013_addr_0043e1fa\n    bl .\n    ldr r0, [r4, #8]\n    ldrb.w r0, [r0, #0x32]\n    ands r0, r0, #3\n    movs r1, r5\n    uxtb r1, r1\n    cmp r0, r1\n    beq L_open_cfw_runtime_am013_4e368_0060\n    ldr r0, [r4, #8]\n    uxtb r5, r5\n    ldrh r1, [r0, #0x32]\n    bfi r1, r5, #0, #2\n    strh r1, [r0, #0x32]\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am013_addr_00440656\n    bl .\nL_open_cfw_runtime_am013_4e368_0060:\n    pop {r0, r1, r2, r4, r5, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM013_4E3CA_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am013_4e3ca(void)
{
    __asm__ volatile(
        "    push {r3, r4, r5, lr}\n    movs r4, r0\n    movs r5, r1\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am013_addr_0043e1fa\n    bl .\n    movs r0, r5\n    uxtb r0, r0\n    ldr r1, [r4, #8]\n    ldrh r1, [r1, #0x32]\n    ubfx r1, r1, #6, #4\n    uxth r0, r0\n    uxth r1, r1\n    cmp r0, r1\n    beq L_open_cfw_runtime_am013_4e3ca_002c\n    ldr r0, [r4, #8]\n    uxtb r5, r5\n    ldrh r1, [r0, #0x32]\n    bfi r1, r5, #6, #4\n    strh r1, [r0, #0x32]\nL_open_cfw_runtime_am013_4e3ca_002c:\n    pop {r0, r4, r5, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM013_4E3F8_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am013_4e3f8(void)
{
    __asm__ volatile(
        "    push {r3, r4, r5, lr}\n    movs r4, r0\n    movs r5, r1\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am013_addr_0043e1fa\n    bl .\n    ldr r0, [r4, #8]\n    uxtb r5, r5\n    ldrh r1, [r0, #0x32]\n    bfi r1, r5, #2, #2\n    strh r1, [r0, #0x32]\n    pop {r0, r4, r5, pc}\n"
    );
}
#endif
