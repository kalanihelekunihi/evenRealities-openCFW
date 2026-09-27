/*
 * SPDX-License-Identifier: MIT
 *
 * Source-owned exact helpers from the AM-004 retained island.
 */

#if defined(OPEN_CFW_AM004_E1FA_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am004_e1fa(void)
{
    __asm__ volatile(
        "    push {r0, r1, r2, r3, r4, lr}\n    movs r4, r0\n    cmp r4, #0\n    bne L_open_cfw_runtime_am004_e1fa_002e\n    ldr r0, [pc, #0x84]\n    str r0, [sp, #8]\n    ldr r0, [pc, #0x84]\n    str r0, [sp, #4]\n    ldr r0, [pc, #0x84]\n    str r0, [sp]\n    ldr.w r3, [pc, #0xc24]\n    mov.w r2, #0x178\n    ldr r1, [pc, #0x80]\n    movs r0, #3\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am004_addr_0044d25c\n    bl .\nL_open_cfw_runtime_am004_e1fa_0024:\n    movs r0, #0\n    movs.w r1, #-1\n    str r0, [r1]\n    b L_open_cfw_runtime_am004_e1fa_0024\nL_open_cfw_runtime_am004_e1fa_002e:\n    ldr r0, [r4, #8]\n    cmp r0, #0\n    bne L_open_cfw_runtime_am004_e1fa_0086\n    movs r0, #0x34\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am004_addr_0044f730\n    bl .\n    str r0, [r4, #8]\n    ldr r0, [r4, #8]\n    cmp r0, #0\n    bne L_open_cfw_runtime_am004_e1fa_006c\n    ldr.w r0, [pc, #0xbf8]\n    str r0, [sp, #8]\n    ldr.w r0, [pc, #0xbf8]\n    str r0, [sp, #4]\n    ldr r0, [pc, #0x44]\n    str r0, [sp]\n    ldr.w r3, [pc, #0xbe4]\n    mov.w r2, #0x17c\n    ldr r1, [pc, #0x40]\n    movs r0, #3\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am004_addr_0044d25c\n    bl .\nL_open_cfw_runtime_am004_e1fa_0062:\n    movs r0, #0\n    movs.w r1, #-1\n    str r0, [r1]\n    b L_open_cfw_runtime_am004_e1fa_0062\nL_open_cfw_runtime_am004_e1fa_006c:\n    ldr r0, [r4, #8]\n    cmp r0, #0\n    beq L_open_cfw_runtime_am004_e1fa_0086\n    ldr r0, [r4, #8]\n    ldrh r1, [r0, #0x32]\n    orrs r1, r1, #0x3c0\n    strh r1, [r0, #0x32]\n    ldr r0, [r4, #8]\n    ldrh r1, [r0, #0x32]\n    orrs r1, r1, #3\n    strh r1, [r0, #0x32]\nL_open_cfw_runtime_am004_e1fa_0086:\n    pop {r0, r1, r2, r3, r4, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM004_E2BC_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am004_e2bc(void)
{
    __asm__ volatile(
        "    cmp r0, #0\n    bne L_open_cfw_runtime_am004_e2bc_0008\n    movs r0, #0\n    b L_open_cfw_runtime_am004_e2bc_0016\nL_open_cfw_runtime_am004_e2bc_0008:\n    ldr r0, [r0]\n    cmp r0, r1\n    bne L_open_cfw_runtime_am004_e2bc_0012\n    movs r0, #1\n    b L_open_cfw_runtime_am004_e2bc_0014\nL_open_cfw_runtime_am004_e2bc_0012:\n    movs r0, #0\nL_open_cfw_runtime_am004_e2bc_0014:\n    uxtb r0, r0\nL_open_cfw_runtime_am004_e2bc_0016:\n    bx lr\n"
    );
}
#endif

#if defined(OPEN_CFW_AM004_E2D4_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am004_e2d4(void)
{
    __asm__ volatile(
        "    ldr r0, [r0]\n    b L_open_cfw_runtime_am004_e2d4_0006\nL_open_cfw_runtime_am004_e2d4_0004:\n    ldr r0, [r0]\nL_open_cfw_runtime_am004_e2d4_0006:\n    cmp r0, #0\n    beq L_open_cfw_runtime_am004_e2d4_0012\n    cmp r0, r1\n    bne L_open_cfw_runtime_am004_e2d4_0004\n    movs r0, #1\n    b L_open_cfw_runtime_am004_e2d4_0014\nL_open_cfw_runtime_am004_e2d4_0012:\n    movs r0, #0\nL_open_cfw_runtime_am004_e2d4_0014:\n    bx lr\n"
    );
}
#endif

#if defined(OPEN_CFW_AM004_E2EA_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am004_e2ea(void)
{
    __asm__ volatile(
        "    push {r4, r5, r6, lr}\n    movs r5, r0\n    movs r0, #0\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am004_addr_0044fa22\n    bl .\n    movs r4, r0\n    b L_open_cfw_runtime_am004_e2ea_0016\nL_open_cfw_runtime_am004_e2ea_000e:\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am004_addr_0044fa22\n    bl .\n    movs r4, r0\nL_open_cfw_runtime_am004_e2ea_0016:\n    cmp r4, #0\n    beq L_open_cfw_runtime_am004_e2ea_0050\n    movs r6, #0\n    b L_open_cfw_runtime_am004_e2ea_0034\nL_open_cfw_runtime_am004_e2ea_001e:\n    movs r1, r5\n    ldr.w r0, [r4, #0x2b8]\n    ldr.w r0, [r0, r6, lsl #2]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am004_ee54\n    bl .\n    uxtb r0, r0\n    cmp r0, #0\n    bne L_open_cfw_runtime_am004_e2ea_004c\n    adds r6, r6, #1\nL_open_cfw_runtime_am004_e2ea_0034:\n    ldr.w r0, [r4, #0x2d4]\n    cmp r6, r0\n    bhs L_open_cfw_runtime_am004_e2ea_000e\n    ldr.w r0, [r4, #0x2b8]\n    ldr.w r0, [r0, r6, lsl #2]\n    cmp r0, r5\n    bne L_open_cfw_runtime_am004_e2ea_001e\n    movs r0, #1\n    b L_open_cfw_runtime_am004_e2ea_0052\nL_open_cfw_runtime_am004_e2ea_004c:\n    movs r0, #1\n    b L_open_cfw_runtime_am004_e2ea_0052\nL_open_cfw_runtime_am004_e2ea_0050:\n    movs r0, #0\nL_open_cfw_runtime_am004_e2ea_0052:\n    pop {r4, r5, r6, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM004_E33E_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am004_e33e(void)
{
    __asm__ volatile(
        "    push {r3, r4, r5, r6, r7, lr}\n    movs r5, r1\n    ldr r4, [r5, #4]\n    cmp r4, #0\n    beq L_open_cfw_runtime_am004_e33e_0046\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am004_addr_0044e586\n    bl .\n    movs r6, r0\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am004_addr_0044e4aa\n    bl .\n    movs r7, r0\n    movs r1, #0\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am004_addr_0043dd86\n    bl .\n    ldr r1, [r4, #0x18]\n    adds r0, r0, r1\n    subs r7, r0, r7\n    str r7, [r5, #0x18]\n    ldr r0, [r5, #0x18]\n    subs r0, r0, #1\n    str r0, [r5, #0x20]\n    movs r1, #0\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am004_addr_0043dd90\n    bl .\n    ldr r1, [r4, #0x14]\n    adds r0, r0, r1\n    subs r6, r0, r6\n    str r6, [r5, #0x14]\n    ldr r0, [r5, #0x14]\n    subs r0, r0, #1\n    str r0, [r5, #0x1c]\nL_open_cfw_runtime_am004_e33e_0046:\n    movs r0, #2\n    str r0, [r5, #0x24]\n    ldr r0, [r5, #0x24]\n    orrs r0, r0, #0x1000\n    str r0, [r5, #0x24]\n    cmp r4, #0\n    beq L_open_cfw_runtime_am004_e33e_005e\n    ldr r0, [r5, #0x24]\n    orrs r0, r0, #0x2000\n    str r0, [r5, #0x24]\nL_open_cfw_runtime_am004_e33e_005e:\n    cmp r4, #0\n    beq L_open_cfw_runtime_am004_e33e_006a\n    ldr r0, [r5, #0x24]\n    orrs r0, r0, #0x300\n    str r0, [r5, #0x24]\nL_open_cfw_runtime_am004_e33e_006a:\n    ldr r0, [r5, #0x24]\n    orrs r0, r0, #4\n    str r0, [r5, #0x24]\n    ldr r0, [r5, #0x24]\n    orrs r0, r0, #0x10\n    str r0, [r5, #0x24]\n    ldr r0, [r5, #0x24]\n    orrs r0, r0, #0x20\n    str r0, [r5, #0x24]\n    ldr r0, [r5, #0x24]\n    orrs r0, r0, #0x40\n    str r0, [r5, #0x24]\n    ldr r0, [r5, #0x24]\n    orrs r0, r0, #0x800\n    str r0, [r5, #0x24]\n    cmp r4, #0\n    beq L_open_cfw_runtime_am004_e33e_009e\n    ldr r0, [r5, #0x24]\n    orrs r0, r0, #0x8000\n    str r0, [r5, #0x24]\nL_open_cfw_runtime_am004_e33e_009e:\n    pop {r0, r4, r5, r6, r7, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM004_E442_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am004_e442(void)
{
    __asm__ volatile(
        "    push.w {r4, r5, r6, r7, r8, lr}\n    sub sp, #0x110\n    movs r5, r0\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am004_addr_00450286\n    bl .\n    movs r6, r0\n    movs r0, r5\n    ldr r0, [r0]\n    mov r8, r8\n    movs r4, r0\n    cmp r6, #0x1a\n    bne L_open_cfw_runtime_am004_e442_0104\n    movs r0, r5\n    ldr r0, [r0, #0x10]\n    mov r8, r8\n    movs r5, r0\n    ldrb r0, [r5]\n    cmp r0, #2\n    beq.w #0x43e638\n    movs r1, #0\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am004_addr_0043de54\n    bl .\n    cmp r0, #0\n    beq L_open_cfw_runtime_am004_e442_003e\n    movs r0, #2\n    strb r0, [r5]\n    b L_open_cfw_runtime_am004_e442_01f6\nL_open_cfw_runtime_am004_e442_003e:\n    movs r1, #0\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am004_addr_0043de4a\n    bl .\n    movs r6, r0\n    movs r1, #0\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am004_addr_0043dd72\n    bl .\n    movs r7, r0\n    movs r1, #0\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am004_addr_0043dd7c\n    bl .\n    mov r8, r0\n    adds.w r1, r4, #0x14\n    add r0, sp, #0x20\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am004_addr_0043dcc0\n    bl .\n    mov r2, r8\n    movs r1, r7\n    add r0, sp, #0x20\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am004_addr_00450b98\n    bl .\n    movs r2, r6\n    add r1, sp, #0x20\n    ldr r0, [r5, #4]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am004_addr_00450f28\n    bl .\n    cmp r0, #0\n    bne L_open_cfw_runtime_am004_e442_0084\n    movs r0, #1\n    strb r0, [r5]\n    b L_open_cfw_runtime_am004_e442_01f6\nL_open_cfw_runtime_am004_e442_0084:\n    movs r1, #0\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am004_addr_0043dda8\n    bl .\n    cmp r0, #0xfd\n    bge L_open_cfw_runtime_am004_e442_0096\n    movs r0, #1\n    strb r0, [r5]\n    b L_open_cfw_runtime_am004_e442_01f6\nL_open_cfw_runtime_am004_e442_0096:\n    movs r1, #0\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am004_addr_0043de6a\n    bl .\n    cmp r0, #0xfd\n    bge L_open_cfw_runtime_am004_e442_00a8\n    movs r0, #1\n    strb r0, [r5]\n    b L_open_cfw_runtime_am004_e442_01f6\nL_open_cfw_runtime_am004_e442_00a8:\n    movs r1, #0\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am004_addr_0043ddb4\n    bl .\n    cmp r0, #0\n    beq L_open_cfw_runtime_am004_e442_00d2\n    movs r1, #0\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am004_addr_0043ddcc\n    bl .\n    cmp r0, #0xfd\n    blt L_open_cfw_runtime_am004_e442_00cc\n    movs r1, #0\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am004_addr_0043ddc0\n    bl .\n    cmp r0, #0xfd\n    bge L_open_cfw_runtime_am004_e442_00d2\nL_open_cfw_runtime_am004_e442_00cc:\n    movs r0, #1\n    strb r0, [r5]\n    b L_open_cfw_runtime_am004_e442_01f6\nL_open_cfw_runtime_am004_e442_00d2:\n    movs r1, #0\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am004_addr_0043ddd8\n    bl .\n    cmp r0, #0\n    beq L_open_cfw_runtime_am004_e442_00fe\n    movs r1, #0\n    b L_open_cfw_runtime_am004_e442_00e4\nL_open_cfw_runtime_am004_e442_00e2:\n    adds r1, r1, #1\nL_open_cfw_runtime_am004_e442_00e4:\n    ldrb r2, [r0, #0xa]\n    cmp r1, r2\n    bhs L_open_cfw_runtime_am004_e442_00fe\n    movs r2, #5\n    mul r2, r2, r1\n    add r2, r0\n    ldrb r2, [r2, #3]\n    cmp r2, #0xfd\n    bge L_open_cfw_runtime_am004_e442_00e2\n    movs r0, #1\n    strb r0, [r5]\n    b L_open_cfw_runtime_am004_e442_01f6\nL_open_cfw_runtime_am004_e442_00fe:\n    movs r0, #0\n    strb r0, [r5]\n    b L_open_cfw_runtime_am004_e442_01f6\nL_open_cfw_runtime_am004_e442_0104:\n    cmp r6, #0x1d\n    bne L_open_cfw_runtime_am004_e442_016e\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am004_addr_00451960\n    bl .\n    movs r5, r0\n    add r0, sp, #0xa0\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am004_addr_00451b9c\n    bl .\n    str r5, [sp, #0xb0]\n    add r2, sp, #0xa0\n    movs r1, #0\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am004_addr_00452616\n    bl .\n    movs r1, #0\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am004_addr_0043de06\n    bl .\n    cmp r0, #0\n    beq L_open_cfw_runtime_am004_e442_013a\n    ldrb.w r0, [sp, #0xe9]\n    orrs r0, r0, #0x20\n    strb.w r0, [sp, #0xe9]\nL_open_cfw_runtime_am004_e442_013a:\n    movs r1, #0\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am004_addr_0043dd72\n    bl .\n    movs r6, r0\n    movs r1, #0\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am004_addr_0043dd7c\n    bl .\n    movs r7, r0\n    adds.w r1, r4, #0x14\n    add r0, sp, #0x10\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am004_addr_0043dcc0\n    bl .\n    movs r2, r7\n    movs r1, r6\n    add r0, sp, #0x10\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am004_addr_00450b98\n    bl .\n    add r2, sp, #0x10\n    add r1, sp, #0xa0\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am004_addr_00451c6e\n    bl .\n    b L_open_cfw_runtime_am004_e442_01f6\nL_open_cfw_runtime_am004_e442_016e:\n    cmp r6, #0x20\n    bne L_open_cfw_runtime_am004_e442_01f6\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am004_addr_00451960\n    bl .\n    movs r5, r0\n    movs r1, r5\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am004_e63e\n    bl .\n    movs r1, #0\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am004_addr_0043ddfc\n    bl .\n    cmp r0, #0\n    beq L_open_cfw_runtime_am004_e442_01f6\n    movs r1, #0\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am004_addr_0043de06\n    bl .\n    cmp r0, #0\n    beq L_open_cfw_runtime_am004_e442_01f6\n    add r0, sp, #0x30\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am004_addr_00451b9c\n    bl .\n    movs r0, #0\n    strb.w r0, [sp, #0x50]\n    movs r0, #0\n    strb.w r0, [sp, #0x6b]\n    movs r0, #0\n    strb.w r0, [sp, #0x88]\n    movs r0, #0\n    strb.w r0, [sp, #0x9c]\n    str r5, [sp, #0x40]\n    add r2, sp, #0x30\n    movs r1, #0\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am004_addr_00452616\n    bl .\n    movs r1, #0\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am004_addr_0043dd72\n    bl .\n    movs r6, r0\n    movs r1, #0\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am004_addr_0043dd7c\n    bl .\n    movs r7, r0\n    adds.w r1, r4, #0x14\n    mov r0, sp\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am004_addr_0043dcc0\n    bl .\n    movs r2, r7\n    movs r1, r6\n    mov r0, sp\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am004_addr_00450b98\n    bl .\n    mov r2, sp\n    add r1, sp, #0x30\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am004_addr_00451c6e\n    bl .\nL_open_cfw_runtime_am004_e442_01f6:\n    add sp, #0x110\n    pop.w {r4, r5, r6, r7, r8, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM004_E63E_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am004_e63e(void)
{
    __asm__ volatile(
        "    push {r3, r4, r5, lr}\n    sub sp, #0x90\n    movs r4, r0\n    movs r5, r1\n    mov r2, sp\n    add r1, sp, #0x10\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am004_addr_0044eb28\n    bl .\n    add r0, sp, #0x10\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am004_addr_00450b80\n    bl .\n    cmp r0, #0\n    bne L_open_cfw_runtime_am004_e63e_0026\n    mov r0, sp\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am004_addr_00450b80\n    bl .\n    cmp r0, #0\n    beq L_open_cfw_runtime_am004_e63e_0064\nL_open_cfw_runtime_am004_e63e_0026:\n    add r1, sp, #0x20\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am004_e6a6\n    bl .\n    uxtb r0, r0\n    cmp r0, #1\n    bne L_open_cfw_runtime_am004_e63e_0064\n    add r0, sp, #0x10\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am004_addr_00450b80\n    bl .\n    cmp r0, #0\n    beq L_open_cfw_runtime_am004_e63e_004c\n    movs r0, #0\n    str r0, [sp, #0x28]\n    add r2, sp, #0x10\n    add r1, sp, #0x20\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am004_addr_00451c6e\n    bl .\nL_open_cfw_runtime_am004_e63e_004c:\n    mov r0, sp\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am004_addr_00450b80\n    bl .\n    cmp r0, #0\n    beq L_open_cfw_runtime_am004_e63e_0064\n    movs r0, #1\n    str r0, [sp, #0x28]\n    mov r2, sp\n    add r1, sp, #0x20\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am004_addr_00451c6e\n    bl .\nL_open_cfw_runtime_am004_e63e_0064:\n    add sp, #0x94\n    pop {r4, r5, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM004_E6A6_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am004_e6a6(void)
{
    __asm__ volatile(
        "    push {r3, r4, r5, lr}\n    movs r4, r0\n    movs r5, r1\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am004_addr_00451b9c\n    bl .\n    movs.w r1, #0x10000\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am004_addr_0043dda8\n    bl .\n    strb.w r0, [r5, #0x20]\n    ldrb.w r0, [r5, #0x20]\n    cmp r0, #3\n    blt L_open_cfw_runtime_am004_e6a6_003a\n    movs.w r1, #0x10000\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am004_addr_0043dd9a\n    bl .\n    str r0, [sp]\n    adds.w r0, r5, #0x21\n    mov r1, sp\n    movs r2, #3\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am004_addr_00439be4\n    bl .\nL_open_cfw_runtime_am004_e6a6_003a:\n    movs.w r1, #0x10000\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am004_addr_0043ddf0\n    bl .\n    strb.w r0, [r5, #0x48]\n    ldrb.w r0, [r5, #0x48]\n    cmp r0, #3\n    blt L_open_cfw_runtime_am004_e6a6_0082\n    movs.w r1, #0x10000\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am004_addr_0043ddfc\n    bl .\n    str r0, [r5, #0x44]\n    ldr r0, [r5, #0x44]\n    cmp r0, #1\n    blt L_open_cfw_runtime_am004_e6a6_007c\n    movs.w r1, #0x10000\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am004_addr_0043dde2\n    bl .\n    str r0, [sp]\n    adds.w r0, r5, #0x3e\n    mov r1, sp\n    movs r2, #3\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am004_addr_00439be4\n    bl .\n    b L_open_cfw_runtime_am004_e6a6_0082\nL_open_cfw_runtime_am004_e6a6_007c:\n    movs r0, #0\n    strb.w r0, [r5, #0x48]\nL_open_cfw_runtime_am004_e6a6_0082:\n    movs.w r1, #0x10000\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am004_addr_0043de3e\n    bl .\n    strb.w r0, [r5, #0x6c]\n    ldrb.w r0, [r5, #0x6c]\n    cmp r0, #3\n    blt L_open_cfw_runtime_am004_e6a6_00d6\n    movs.w r1, #0x10000\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am004_addr_0043de1c\n    bl .\n    str r0, [r5, #0x5c]\n    ldr r0, [r5, #0x5c]\n    cmp r0, #1\n    blt L_open_cfw_runtime_am004_e6a6_00d0\n    movs.w r1, #0x10000\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am004_addr_0043de26\n    bl .\n    str r0, [r5, #0x68]\n    movs.w r1, #0x10000\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am004_addr_0043de30\n    bl .\n    str r0, [sp]\n    adds.w r0, r5, #0x59\n    mov r1, sp\n    movs r2, #3\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am004_addr_00439be4\n    bl .\n    b L_open_cfw_runtime_am004_e6a6_00d6\nL_open_cfw_runtime_am004_e6a6_00d0:\n    movs r0, #0\n    strb.w r0, [r5, #0x6c]\nL_open_cfw_runtime_am004_e6a6_00d6:\n    movs.w r1, #0x10000\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am004_addr_0044c47a\n    bl .\n    movs r1, r0\n    uxtb r1, r1\n    cmp r1, #0xfd\n    bge L_open_cfw_runtime_am004_e6a6_0100\n    ldrb.w r1, [r5, #0x20]\n    uxtb r0, r0\n    mul r0, r0, r1\n    asrs r0, r0, #8\n    strb.w r0, [r5, #0x20]\n    strb.w r0, [r5, #0x48]\n    strb.w r0, [r5, #0x6c]\nL_open_cfw_runtime_am004_e6a6_0100:\n    ldrb.w r0, [r5, #0x20]\n    cmp r0, #0\n    bne L_open_cfw_runtime_am004_e6a6_0118\n    ldrb.w r0, [r5, #0x48]\n    cmp r0, #0\n    bne L_open_cfw_runtime_am004_e6a6_0118\n    ldrb.w r0, [r5, #0x6c]\n    cmp r0, #0\n    beq L_open_cfw_runtime_am004_e6a6_0128\nL_open_cfw_runtime_am004_e6a6_0118:\n    movs.w r1, #0x10000\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am004_addr_0043de4a\n    bl .\n    str r0, [r5, #0x1c]\n    movs r0, #1\n    b L_open_cfw_runtime_am004_e6a6_012a\nL_open_cfw_runtime_am004_e6a6_0128:\n    movs r0, #0\nL_open_cfw_runtime_am004_e6a6_012a:\n    pop {r1, r4, r5, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM004_E7D2_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am004_e7d2(void)
{
    __asm__ volatile(
        "    push.w {r4, r5, r6, r7, r8, lr}\n    sub sp, #0x20\n    movs r6, r1\n    movs r0, r6\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am004_addr_00450286\n    bl .\n    movs r4, r0\n    movs r0, r6\n    ldr r0, [r0]\n    mov r8, r8\n    movs r5, r0\n    cmp r4, #1\n    bne L_open_cfw_runtime_am004_e7d2_0026\n    movs r1, #0x20\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am004_addr_0043e046\n    bl .\n    b L_open_cfw_runtime_am004_e7d2_0414\nL_open_cfw_runtime_am004_e7d2_0026:\n    cmp r4, #0xb\n    bne L_open_cfw_runtime_am004_e7d2_0080\n    movs r1, #0x20\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am004_addr_0043e086\n    bl .\n    movs r0, r6\n    ldr r0, [r0, #0x10]\n    mov r8, r8\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am004_addr_00452fae\n    bl .\n    cmp r0, #0\n    bne.w #0x43ebe6\n    movs r1, #8\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am004_addr_0043e0e0\n    bl .\n    cmp r0, #0\n    beq.w #0x43ebe6\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am004_addr_0043e156\n    bl .\n    lsls r0, r0, #0x1f\n    bmi L_open_cfw_runtime_am004_e7d2_0064\n    movs r1, #1\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am004_addr_0043e046\n    bl .\n    b L_open_cfw_runtime_am004_e7d2_006c\nL_open_cfw_runtime_am004_e7d2_0064:\n    movs r1, #1\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am004_addr_0043e086\n    bl .\nL_open_cfw_runtime_am004_e7d2_006c:\n    movs r2, #0\n    movs r1, #0x23\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am004_addr_00451670\n    bl .\n    uxtb r0, r0\n    cmp r0, #1\n    beq.w #0x43ebe6\n    b L_open_cfw_runtime_am004_e7d2_0414\nL_open_cfw_runtime_am004_e7d2_0080:\n    cmp r4, #3\n    bne L_open_cfw_runtime_am004_e7d2_008e\n    movs r1, #0x20\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am004_addr_0043e086\n    bl .\n    b L_open_cfw_runtime_am004_e7d2_0414\nL_open_cfw_runtime_am004_e7d2_008e:\n    cmp r4, #0x32\n    bne L_open_cfw_runtime_am004_e7d2_00b2\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am004_addr_0044ddea\n    bl .\n    movs r4, r0\n    movs r6, #0\nL_open_cfw_runtime_am004_e7d2_009c:\n    cmp r6, r4\n    bhs.w #0x43ebe6\n    ldr r0, [r5, #8]\n    ldr r0, [r0]\n    ldr.w r0, [r0, r6, lsl #2]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am004_addr_0043f648\n    bl .\n    adds r6, r6, #1\n    b L_open_cfw_runtime_am004_e7d2_009c\nL_open_cfw_runtime_am004_e7d2_00b2:\n    cmp r4, #0x11\n    bne.w #0x43ea24\n    movs r1, #8\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am004_addr_0043e0e0\n    bl .\n    cmp r0, #0\n    beq L_open_cfw_runtime_am004_e7d2_0108\n    movs r0, r6\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am004_addr_004519a0\n    bl .\n    movs r4, r0\n    cmp r4, #0x13\n    beq L_open_cfw_runtime_am004_e7d2_00d4\n    cmp r4, #0x11\n    bne L_open_cfw_runtime_am004_e7d2_00de\nL_open_cfw_runtime_am004_e7d2_00d4:\n    movs r1, #1\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am004_addr_0043e046\n    bl .\n    b L_open_cfw_runtime_am004_e7d2_00ee\nL_open_cfw_runtime_am004_e7d2_00de:\n    cmp r4, #0x14\n    beq L_open_cfw_runtime_am004_e7d2_00e6\n    cmp r4, #0x12\n    bne L_open_cfw_runtime_am004_e7d2_00ee\nL_open_cfw_runtime_am004_e7d2_00e6:\n    movs r1, #1\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am004_addr_0043e086\n    bl .\nL_open_cfw_runtime_am004_e7d2_00ee:\n    cmp r4, #0xa\n    beq.w #0x43ebe6\n    movs r2, #0\n    movs r1, #0x23\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am004_addr_00451670\n    bl .\n    uxtb r0, r0\n    cmp r0, #1\n    beq.w #0x43ebe6\n    b L_open_cfw_runtime_am004_e7d2_0414\nL_open_cfw_runtime_am004_e7d2_0108:\n    mov.w r1, #0x810\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am004_addr_0043e0e0\n    bl .\n    cmp r0, #0\n    beq.w #0x43ebe6\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am004_addr_0044d19a\n    bl .\n    cmp r0, #0\n    bne.w #0x43ebe6\n    movs r4, #0\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am004_addr_0044e586\n    bl .\n    movs r7, r0\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am004_addr_0044e67a\n    bl .\n    mov r8, r0\n    movs r0, r6\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am004_addr_004519a0\n    bl .\n    cmp r0, #0x12\n    bne L_open_cfw_runtime_am004_e7d2_0164\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am004_addr_0044e498\n    bl .\n    movs r6, r0\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am004_addr_0043fdda\n    bl .\n    movs r2, r4\n    uxtb r2, r2\n    movs r1, #4\n    sdiv r0, r0, r1\n    adds r6, r0, r6\n    movs r1, r6\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am004_addr_0044ea04\n    bl .\n    b L_open_cfw_runtime_am004_e7d2_0414\nL_open_cfw_runtime_am004_e7d2_0164:\n    cmp r0, #0x11\n    bne L_open_cfw_runtime_am004_e7d2_018c\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am004_addr_0044e498\n    bl .\n    movs r6, r0\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am004_addr_0043fdda\n    bl .\n    movs r2, r4\n    uxtb r2, r2\n    movs r1, #4\n    sdiv r0, r0, r1\n    subs r6, r6, r0\n    movs r1, r6\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am004_addr_0044ea04\n    bl .\n    b L_open_cfw_runtime_am004_e7d2_0414\nL_open_cfw_runtime_am004_e7d2_018c:\n    cmp r0, #0x13\n    bne L_open_cfw_runtime_am004_e7d2_01ee\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am004_addr_0044e442\n    bl .\n    tst.w r0, #3\n    beq L_open_cfw_runtime_am004_e7d2_01a6\n    cmp r7, #1\n    bge L_open_cfw_runtime_am004_e7d2_01ca\n    cmp.w r8, #1\n    bge L_open_cfw_runtime_am004_e7d2_01ca\nL_open_cfw_runtime_am004_e7d2_01a6:\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am004_addr_0044e498\n    bl .\n    movs r6, r0\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am004_addr_0043fdda\n    bl .\n    movs r2, r4\n    uxtb r2, r2\n    movs r1, #4\n    sdiv r0, r0, r1\n    adds r6, r0, r6\n    movs r1, r6\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am004_addr_0044ea04\n    bl .\n    b L_open_cfw_runtime_am004_e7d2_0414\nL_open_cfw_runtime_am004_e7d2_01ca:\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am004_addr_0044e486\n    bl .\n    movs r6, r0\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am004_addr_0043fd9e\n    bl .\n    movs r2, r4\n    uxtb r2, r2\n    movs r1, #4\n    sdiv r0, r0, r1\n    adds r6, r0, r6\n    movs r1, r6\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am004_addr_0044e9da\n    bl .\n    b L_open_cfw_runtime_am004_e7d2_0414\nL_open_cfw_runtime_am004_e7d2_01ee:\n    cmp r0, #0x14\n    bne.w #0x43ebe6\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am004_addr_0044e442\n    bl .\n    tst.w r0, #3\n    beq L_open_cfw_runtime_am004_e7d2_020a\n    cmp r7, #1\n    bge L_open_cfw_runtime_am004_e7d2_022e\n    cmp.w r8, #1\n    bge L_open_cfw_runtime_am004_e7d2_022e\nL_open_cfw_runtime_am004_e7d2_020a:\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am004_addr_0044e498\n    bl .\n    movs r6, r0\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am004_addr_0043fdda\n    bl .\n    movs r2, r4\n    uxtb r2, r2\n    movs r1, #4\n    sdiv r0, r0, r1\n    subs r6, r6, r0\n    movs r1, r6\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am004_addr_0044ea04\n    bl .\n    b L_open_cfw_runtime_am004_e7d2_0414\nL_open_cfw_runtime_am004_e7d2_022e:\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am004_addr_0044e486\n    bl .\n    movs r6, r0\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am004_addr_0043fd9e\n    bl .\n    movs r2, r4\n    uxtb r2, r2\n    movs r1, #4\n    sdiv r0, r0, r1\n    subs r6, r6, r0\n    movs r1, r6\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am004_addr_0044e9da\n    bl .\n    b L_open_cfw_runtime_am004_e7d2_0414\n    cmp r4, #0x13\n    bne L_open_cfw_runtime_am004_e7d2_02ca\n    mov.w r1, #0x400\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am004_addr_0043e0e0\n    bl .\n    cmp r0, #0\n    beq L_open_cfw_runtime_am004_e7d2_026c\n    movs r1, #1\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am004_addr_0044ea56\n    bl .\nL_open_cfw_runtime_am004_e7d2_026c:\n    movs r0, #0\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am004_addr_0043e1be\n    bl .\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am004_addr_0044d5a4\n    bl .\n    movs r4, r0\n    movs r7, #2\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am004_addr_00452ef8\n    bl .\n    cmp r0, #0\n    bne L_open_cfw_runtime_am004_e7d2_028a\n    movs r0, r6\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am004_addr_004518d8\n    bl .\nL_open_cfw_runtime_am004_e7d2_028a:\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am004_addr_00452f00\n    bl .\n    movs r1, r0\n    uxtb r1, r1\n    cmp r1, #2\n    beq L_open_cfw_runtime_am004_e7d2_029c\n    uxtb r0, r0\n    cmp r0, #4\n    bne L_open_cfw_runtime_am004_e7d2_02a0\nL_open_cfw_runtime_am004_e7d2_029c:\n    orrs r7, r7, #4\nL_open_cfw_runtime_am004_e7d2_02a0:\n    uxtb r4, r4\n    cmp r4, #0\n    beq L_open_cfw_runtime_am004_e7d2_02b6\n    orrs r7, r7, #8\n    movs r1, r7\n    uxth r1, r1\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am004_addr_0043e046\n    bl .\n    b L_open_cfw_runtime_am004_e7d2_0414\nL_open_cfw_runtime_am004_e7d2_02b6:\n    movs r1, r7\n    uxth r1, r1\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am004_addr_0043e046\n    bl .\n    movs r1, #8\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am004_addr_0043e086\n    bl .\n    b L_open_cfw_runtime_am004_e7d2_0414\nL_open_cfw_runtime_am004_e7d2_02ca:\n    cmp r4, #0xc\n    bne L_open_cfw_runtime_am004_e7d2_02d8\n    movs r1, #0x40\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am004_addr_0043e046\n    bl .\n    b L_open_cfw_runtime_am004_e7d2_0414\nL_open_cfw_runtime_am004_e7d2_02d8:\n    cmp r4, #0xe\n    bne L_open_cfw_runtime_am004_e7d2_030c\n    movs r1, #0x40\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am004_addr_0043e086\n    bl .\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am004_addr_0044e42c\n    bl .\n    cmp r0, #2\n    bne.w #0x43ebe6\n    mov r2, sp\n    add r1, sp, #0x10\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am004_addr_0044eb28\n    bl .\n    add r1, sp, #0x10\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am004_addr_004405d4\n    bl .\n    mov r1, sp\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am004_addr_004405d4\n    bl .\n    b L_open_cfw_runtime_am004_e7d2_0414\nL_open_cfw_runtime_am004_e7d2_030c:\n    cmp r4, #0x14\n    bne L_open_cfw_runtime_am004_e7d2_031a\n    movs r1, #0xe\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am004_addr_0043e086\n    bl .\n    b L_open_cfw_runtime_am004_e7d2_0414\nL_open_cfw_runtime_am004_e7d2_031a:\n    cmp r4, #0x31\n    bne L_open_cfw_runtime_am004_e7d2_035e\n    movs r1, #0\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am004_addr_0043dd66\n    bl .\n    movs r4, r0\n    movs r1, #0\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am004_addr_0043de76\n    bl .\n    uxth r0, r0\n    cmp r0, #0\n    bne L_open_cfw_runtime_am004_e7d2_033a\n    cmp r4, #0\n    beq L_open_cfw_runtime_am004_e7d2_0340\nL_open_cfw_runtime_am004_e7d2_033a:\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am004_addr_0043f648\n    bl .\nL_open_cfw_runtime_am004_e7d2_0340:\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am004_addr_0044ddea\n    bl .\n    movs r6, r0\n    movs r4, #0\nL_open_cfw_runtime_am004_e7d2_034a:\n    cmp r4, r6\n    bhs L_open_cfw_runtime_am004_e7d2_0414\n    ldr r0, [r5, #8]\n    ldr r0, [r0]\n    ldr.w r0, [r0, r4, lsl #2]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am004_addr_0043f648\n    bl .\n    adds r4, r4, #1\n    b L_open_cfw_runtime_am004_e7d2_034a\nL_open_cfw_runtime_am004_e7d2_035e:\n    cmp r4, #0x2a\n    bne L_open_cfw_runtime_am004_e7d2_03a6\n    movs r1, #0\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am004_addr_0043dd52\n    bl .\n    movs r6, r0\n    movs r1, #0\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am004_addr_0043dd5c\n    bl .\n    movs r7, r0\n    movs r1, #0\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am004_addr_0043dd66\n    bl .\n    movs r4, r0\n    movs r1, #0\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am004_addr_0043de76\n    bl .\n    uxth r0, r0\n    cmp r0, #0\n    bne L_open_cfw_runtime_am004_e7d2_039e\n    cmp r4, #0\n    bne L_open_cfw_runtime_am004_e7d2_039e\n    mvns r0, #0xc0000000\n    cmp r6, r0\n    beq L_open_cfw_runtime_am004_e7d2_039e\n    cmp r7, r0\n    bne L_open_cfw_runtime_am004_e7d2_0414\nL_open_cfw_runtime_am004_e7d2_039e:\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am004_addr_0043f648\n    bl .\n    b L_open_cfw_runtime_am004_e7d2_0414\nL_open_cfw_runtime_am004_e7d2_03a6:\n    cmp r4, #0x2c\n    bne L_open_cfw_runtime_am004_e7d2_03ba\n    ldrh r0, [r5, #0x2a]\n    orrs r0, r0, #2\n    strh r0, [r5, #0x2a]\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am004_addr_0043f648\n    bl .\n    b L_open_cfw_runtime_am004_e7d2_0414\nL_open_cfw_runtime_am004_e7d2_03ba:\n    cmp r4, #0x1b\n    bne L_open_cfw_runtime_am004_e7d2_03d0\n    movs r1, #0\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am004_addr_00452c66\n    bl .\n    movs r1, r0\n    movs r0, r6\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am004_addr_004519fa\n    bl .\n    b L_open_cfw_runtime_am004_e7d2_0414\nL_open_cfw_runtime_am004_e7d2_03d0:\n    cmp r4, #0x1d\n    beq L_open_cfw_runtime_am004_e7d2_03dc\n    cmp r4, #0x20\n    beq L_open_cfw_runtime_am004_e7d2_03dc\n    cmp r4, #0x1a\n    bne L_open_cfw_runtime_am004_e7d2_03e4\nL_open_cfw_runtime_am004_e7d2_03dc:\n    movs r0, r6\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am004_e442\n    bl .\n    b L_open_cfw_runtime_am004_e7d2_0414\nL_open_cfw_runtime_am004_e7d2_03e4:\n    cmp r4, #0x17\n    bne L_open_cfw_runtime_am004_e7d2_03fa\n    movs r1, #0x20\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am004_addr_0043e086\n    bl .\n    movs r1, #0x40\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am004_addr_0043e086\n    bl .\n    b L_open_cfw_runtime_am004_e7d2_0414\nL_open_cfw_runtime_am004_e7d2_03fa:\n    cmp r4, #0x18\n    bne L_open_cfw_runtime_am004_e7d2_0408\n    movs r1, #0x10\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am004_addr_0043e046\n    bl .\n    b L_open_cfw_runtime_am004_e7d2_0414\nL_open_cfw_runtime_am004_e7d2_0408:\n    cmp r4, #0x19\n    bne L_open_cfw_runtime_am004_e7d2_0414\n    movs r1, #0x10\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am004_addr_0043e086\n    bl .\nL_open_cfw_runtime_am004_e7d2_0414:\n    add sp, #0x20\n    pop.w {r4, r5, r6, r7, r8, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM004_EBEC_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am004_ebec(void)
{
    __asm__ volatile(
        "    push.w {r0, r1, r4, r5, r6, r7, r8, sb, sl, fp, lr}\n    sub sp, #0x1c\n    ldr r0, [sp, #0x1c]\n    ldrh r0, [r0, #0x28]\n    ldrh.w r1, [sp, #0x20]\n    cmp r0, r1\n    beq.w #0x43ee26\n    ldr r0, [sp, #0x1c]\n    cmp r0, #0\n    bne L_open_cfw_runtime_am004_ebec_003e\n    ldr r0, [pc, #0x238]\n    str r0, [sp, #8]\n    ldr r0, [pc, #0x238]\n    str r0, [sp, #4]\n    ldr r0, [pc, #0x238]\n    str r0, [sp]\n    ldr r3, [pc, #0x238]\n    movw r2, #0x38f\n    ldr r1, [pc, #0x234]\n    movs r0, #3\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am004_addr_0044d25c\n    bl .\nL_open_cfw_runtime_am004_ebec_0034:\n    movs r0, #0\n    movs.w r1, #-1\n    str r0, [r1]\n    b L_open_cfw_runtime_am004_ebec_0034\nL_open_cfw_runtime_am004_ebec_003e:\n    ldr r0, [sp, #0x1c]\n    ldrh r0, [r0, #0x28]\n    strh.w r0, [sp, #8]\n    ldrh.w r2, [sp, #0x20]\n    ldrh.w r1, [sp, #8]\n    ldr r0, [sp, #0x1c]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am004_addr_0044c178\n    bl .\n    strb.w r0, [sp, #4]\n    ldrb.w r0, [sp, #4]\n    cmp r0, #0\n    bne L_open_cfw_runtime_am004_ebec_006a\n    ldrh.w r0, [sp, #0x20]\n    ldr r1, [sp, #0x1c]\n    strh r0, [r1, #0x28]\n    b L_open_cfw_runtime_am004_ebec_023a\nL_open_cfw_runtime_am004_ebec_006a:\n    ldr r0, [sp, #0x1c]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am004_addr_00440656\n    bl .\n    ldrh.w r0, [sp, #0x20]\n    ldr r1, [sp, #0x1c]\n    strh r0, [r1, #0x28]\n    ldr r0, [sp, #0x1c]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am004_addr_0044c50e\n    bl .\n    mov.w r0, #0x280\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am004_addr_0044f730\n    bl .\n    movs r4, r0\n    movs r5, #0\n    movs r0, #0\n    str r0, [sp]\n    b L_open_cfw_runtime_am004_ebec_0096\nL_open_cfw_runtime_am004_ebec_0090:\n    ldr r0, [sp]\n    adds r0, r0, #1\n    str r0, [sp]\nL_open_cfw_runtime_am004_ebec_0096:\n    ldr r0, [sp]\n    ldr r1, [sp, #0x1c]\n    ldrh r1, [r1, #0x2a]\n    ubfx r1, r1, #4, #6\n    uxth r1, r1\n    cmp r0, r1\n    bhs.w #0x43edae\n    cmp r5, #0x20\n    bhs.w #0x43edae\n    ldr r0, [sp, #0x1c]\n    ldr r0, [r0, #0xc]\n    ldr r1, [sp]\n    add.w r0, r0, r1, lsl #3\n    str r0, [sp, #0xc]\n    ldr r0, [sp, #0x1c]\n    ldr r0, [r0, #0xc]\n    ldr r1, [sp]\n    add.w r0, r0, r1, lsl #3\n    ldr r0, [r0, #4]\n    bic r0, r0, #0xff000000\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am004_addr_0043dd48\n    bl .\n    strh.w r0, [sp, #6]\n    ldr r0, [sp, #0x1c]\n    ldr r0, [r0, #0xc]\n    ldr r1, [sp]\n    add.w r0, r0, r1, lsl #3\n    ldr r0, [r0, #4]\n    bic r0, r0, #0xff000000\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am004_addr_0043dd4c\n    bl .\n    str r0, [sp, #0x14]\n    ldrh.w r0, [sp, #6]\n    ldrh.w r1, [sp, #0x20]\n    mvns r1, r1\n    tst r0, r1\n    bne L_open_cfw_runtime_am004_ebec_0090\n    ldr r0, [sp, #0xc]\n    ldr r0, [r0, #4]\n    ubfx r0, r0, #0x19, #1\n    cmp r0, #0\n    bne L_open_cfw_runtime_am004_ebec_0090\n    add r2, sp, #0x10\n    movs r1, #0x68\n    ldr r0, [sp, #0xc]\n    ldr r0, [r0]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am004_addr_0043dce0\n    bl .\n    cmp r0, #1\n    bne L_open_cfw_runtime_am004_ebec_0090\n    ldr r6, [sp, #0x10]\n    movs r7, #0\n    b L_open_cfw_runtime_am004_ebec_01ac\nL_open_cfw_runtime_am004_ebec_0118:\n    adds.w r8, r8, #1\nL_open_cfw_runtime_am004_ebec_011c:\n    cmp r8, r5\n    bhs L_open_cfw_runtime_am004_ebec_0160\n    movs.w sb, #0x14\n    mul r0, sb, r8\n    add r0, r4\n    ldr.w fp, [r0, #4]\n    mov r0, fp\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am004_addr_0043dd48\n    bl .\n    mov sl, r0\n    mov r0, fp\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am004_addr_0043dd4c\n    bl .\n    mul sb, sb, r8\n    add.w r1, r4, sb\n    ldrb r1, [r1, #8]\n    ldr r2, [r6]\n    ldrb r2, [r2, r7]\n    cmp r1, r2\n    bne L_open_cfw_runtime_am004_ebec_0118\n    ldr r1, [sp, #0x14]\n    cmp r0, r1\n    bne L_open_cfw_runtime_am004_ebec_0118\n    ldrh.w r0, [sp, #6]\n    uxth.w sl, sl\n    cmp sl, r0\n    blo L_open_cfw_runtime_am004_ebec_0118\nL_open_cfw_runtime_am004_ebec_0160:\n    cmp r8, r5\n    bne L_open_cfw_runtime_am004_ebec_01aa\n    movs r0, #0x14\n    ldr r1, [r6, #0xc]\n    mul r2, r0, r5\n    strh r1, [r4, r2]\n    ldr r1, [r6, #0x10]\n    mul r2, r0, r5\n    add r2, r4\n    strh r1, [r2, #2]\n    ldr r1, [r6, #8]\n    mul r2, r0, r5\n    add r2, r4\n    str r1, [r2, #0xc]\n    ldr r1, [r6]\n    ldrb r1, [r1, r7]\n    mul r2, r0, r5\n    add r2, r4\n    strb r1, [r2, #8]\n    ldr r1, [r6, #4]\n    mul r2, r0, r5\n    add r2, r4\n    str r1, [r2, #0x10]\n    ldr r1, [sp, #0xc]\n    ldr r1, [r1, #4]\n    bic r1, r1, #0xff000000\n    mul r0, r0, r5\n    add r0, r4\n    str r1, [r0, #4]\n    adds r5, r5, #1\nL_open_cfw_runtime_am004_ebec_01aa:\n    adds r7, r7, #1\nL_open_cfw_runtime_am004_ebec_01ac:\n    ldr r0, [r6]\n    ldrb r0, [r0, r7]\n    cmp r0, #0\n    beq.w #0x43ec7c\n    cmp r5, #0x20\n    bhs.w #0x43ec7c\n    movs.w r8, #0\n    b L_open_cfw_runtime_am004_ebec_011c\n    movs r6, #0\n    b L_open_cfw_runtime_am004_ebec_01f0\nL_open_cfw_runtime_am004_ebec_01c6:\n    movs r7, #0x14\n    mul r0, r7, r6\n    add r0, r4\n    ldr r0, [r0, #4]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am004_addr_0043dd4c\n    bl .\n    mul r7, r7, r6\n    add.w r1, r4, r7\n    str r1, [sp]\n    ldrh.w r3, [sp, #0x20]\n    ldrh.w r2, [sp, #8]\n    movs r1, r0\n    ldr r0, [sp, #0x1c]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am004_addr_0044bfae\n    bl .\n    adds r6, r6, #1\nL_open_cfw_runtime_am004_ebec_01f0:\n    cmp r6, r5\n    blo L_open_cfw_runtime_am004_ebec_01c6\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am004_addr_0044f758\n    bl .\n    ldrb.w r0, [sp, #4]\n    cmp r0, #1\n    bne L_open_cfw_runtime_am004_ebec_0210\n    movs r2, #0xff\n    movs.w r1, #0xf0000\n    ldr r0, [sp, #0x1c]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am004_addr_0044bc8c\n    bl .\n    b L_open_cfw_runtime_am004_ebec_023a\nL_open_cfw_runtime_am004_ebec_0210:\n    ldrb.w r0, [sp, #4]\n    cmp r0, #3\n    bne L_open_cfw_runtime_am004_ebec_0226\n    movs r2, #0xff\n    movs.w r1, #0xf0000\n    ldr r0, [sp, #0x1c]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am004_addr_0044bc8c\n    bl .\n    b L_open_cfw_runtime_am004_ebec_023a\nL_open_cfw_runtime_am004_ebec_0226:\n    ldrb.w r0, [sp, #4]\n    cmp r0, #2\n    bne L_open_cfw_runtime_am004_ebec_023a\n    ldr r0, [sp, #0x1c]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am004_addr_00440656\n    bl .\n    ldr r0, [sp, #0x1c]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am004_addr_00452d42\n    bl .\nL_open_cfw_runtime_am004_ebec_023a:\n    add sp, #0x24\n    pop.w {r4, r5, r6, r7, r8, sb, sl, fp, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM004_EE54_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am004_ee54(void)
{
    __asm__ volatile(
        "L_open_cfw_runtime_am004_ee54_0000:\n    push {r3, r4, r5, r6, r7, lr}\n    movs r4, r0\n    movs r5, r1\n    movs r6, #0\n    ldr r0, [r4, #8]\n    cmp r0, #0\n    beq L_open_cfw_runtime_am004_ee54_0012\n    ldr r0, [r4, #8]\n    ldrh r6, [r0, #0x30]\nL_open_cfw_runtime_am004_ee54_0012:\n    movs r7, #0\n    b L_open_cfw_runtime_am004_ee54_0024\nL_open_cfw_runtime_am004_ee54_0016:\n    movs r1, r5\n    bl L_open_cfw_runtime_am004_ee54_0000\n    uxtb r0, r0\n    cmp r0, #0\n    bne L_open_cfw_runtime_am004_ee54_0038\n    adds r7, r7, #1\nL_open_cfw_runtime_am004_ee54_0024:\n    cmp r7, r6\n    bhs L_open_cfw_runtime_am004_ee54_003c\n    ldr r0, [r4, #8]\n    ldr r0, [r0]\n    ldr.w r0, [r0, r7, lsl #2]\n    cmp r0, r5\n    bne L_open_cfw_runtime_am004_ee54_0016\n    movs r0, #1\n    b L_open_cfw_runtime_am004_ee54_003e\nL_open_cfw_runtime_am004_ee54_0038:\n    movs r0, #1\n    b L_open_cfw_runtime_am004_ee54_003e\nL_open_cfw_runtime_am004_ee54_003c:\n    movs r0, #0\nL_open_cfw_runtime_am004_ee54_003e:\n    pop {r1, r4, r5, r6, r7, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM004_EE94_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am004_ee94(void)
{
    __asm__ volatile(
        "    ldr r2, [r1]\n    str r2, [r0]\n    ldr r2, [r1, #4]\n    str r2, [r0, #4]\n    ldr r2, [r1, #8]\n    str r2, [r0, #8]\n    ldr r1, [r1, #0xc]\n    str r1, [r0, #0xc]\n    bx lr\n"
    );
}
#endif

#if defined(OPEN_CFW_AM004_EEA6_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am004_eea6(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    movs r2, #1\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am004_addr_0044bdea\n    bl .\n    pop {r1, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM004_EEB0_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am004_eeb0(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    movs r2, #4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am004_addr_0044bdea\n    bl .\n    pop {r1, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM004_EEBA_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am004_eeba(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    movs r2, #5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am004_addr_0044bdea\n    bl .\n    pop {r1, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM004_EEC4_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am004_eec4(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    movs r2, #2\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am004_addr_0044bdea\n    bl .\n    pop {r1, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM004_EECE_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am004_eece(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    movs r2, #6\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am004_addr_0044bdea\n    bl .\n    pop {r1, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM004_EED8_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am004_eed8(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    movs r2, #7\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am004_addr_0044bdea\n    bl .\n    pop {r1, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM004_EEE2_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am004_eee2(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    movs r2, #8\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am004_addr_0044bdea\n    bl .\n    pop {r1, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM004_EEEC_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am004_eeec(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    movs r2, #9\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am004_addr_0044bdea\n    bl .\n    pop {r1, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM004_EEF6_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am004_eef6(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    movs r2, #0xa\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am004_addr_0044bdea\n    bl .\n    uxtb r0, r0\n    pop {r1, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM004_EF02_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am004_ef02(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    movs r2, #0x6c\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am004_addr_0044bdea\n    bl .\n    pop {r1, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM004_EF0C_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am004_ef0c(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    movs r2, #0x6d\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am004_addr_0044bdea\n    bl .\n    pop {r1, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM004_EF16_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am004_ef16(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    movs r2, #0x6e\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am004_addr_0044bdea\n    bl .\n    pop {r1, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM004_EF20_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am004_ef20(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    movs r2, #0x6f\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am004_addr_0044bdea\n    bl .\n    pop {r1, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM004_EF2A_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am004_ef2a(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    movs r2, #0x70\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am004_addr_0044bdea\n    bl .\n    pop {r1, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM004_EF34_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am004_ef34(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    movs r2, #0x71\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am004_addr_0044bdea\n    bl .\n    pop {r1, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM004_EF3E_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am004_ef3e(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    movs r2, #0x72\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am004_addr_0044bdea\n    bl .\n    pop {r1, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM004_EF48_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am004_ef48(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    movs r2, #0x10\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am004_addr_0044bdea\n    bl .\n    pop {r1, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM004_EF52_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am004_ef52(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    movs r2, #0x11\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am004_addr_0044bdea\n    bl .\n    pop {r1, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM004_EF5C_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am004_ef5c(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    movs r2, #0x12\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am004_addr_0044bdea\n    bl .\n    pop {r1, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM004_EF66_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am004_ef66(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    movs r2, #0x13\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am004_addr_0044bdea\n    bl .\n    pop {r1, pc}\n"
    );
}
#endif
