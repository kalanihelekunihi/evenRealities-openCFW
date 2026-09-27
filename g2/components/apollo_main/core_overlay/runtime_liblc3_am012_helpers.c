/*
 * SPDX-License-Identifier: MIT
 *
 * Source-owned exact helpers from the AM-012 retained island.
 */

#if defined(OPEN_CFW_AM012_4CC8C_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am012_4cc8c(void)
{
    __asm__ volatile(
        "    push {r4, r5, r6, lr}\n    ldr r4, [r0]\n    ldr r0, [r4, #8]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am012_addr_0044b860\n    bl .\n    movs r5, r0\n    ldrb r2, [r4, #4]\n    movs r1, r5\n    ldr r0, [r4]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am012_addr_0044bdea\n    bl .\n    str r0, [r4, #0xc]\n    ldrb r6, [r4, #4]\n    movs r0, #0\n    strb r0, [r4, #4]\n    movs r3, r4\n    movs r2, r6\n    uxtb r2, r2\n    movs r1, r5\n    ldr r0, [r4]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am012_addr_0044ca18\n    bl .\n    strb r6, [r4, #4]\n    ldr r1, [r4, #8]\n    ldr r0, [r4]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am012_addr_0044c72c\n    bl .\n    ldr r2, [r4, #0xc]\n    ldrb r1, [r4, #4]\n    ldr r0, [r0]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am012_addr_00482868\n    bl .\n    ldrb r2, [r4, #4]\n    ldr r1, [r4, #8]\n    ldr r0, [r4]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am012_addr_0044bc8c\n    bl .\n    pop {r4, r5, r6, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM012_4CD9E_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am012_4cd9e(void)
{
    __asm__ volatile(
        "    push {r4, lr}\n    movs r4, r0\n    movs r1, #0\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am012_addr_0044b88e\n    bl .\n    cmp r0, #0\n    beq L_open_cfw_runtime_am012_4cd9e_0014\n    movs r0, #2\n    b L_open_cfw_runtime_am012_4cd9e_008a\nL_open_cfw_runtime_am012_4cd9e_0014:\n    movs r1, #0\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am012_addr_0044b87a\n    bl .\n    cmp.w r0, #0x100\n    beq L_open_cfw_runtime_am012_4cd9e_0026\n    movs r0, #2\n    b L_open_cfw_runtime_am012_4cd9e_008a\nL_open_cfw_runtime_am012_4cd9e_0026:\n    movs r1, #0\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am012_addr_0044b884\n    bl .\n    cmp.w r0, #0x100\n    beq L_open_cfw_runtime_am012_4cd9e_0038\n    movs r0, #2\n    b L_open_cfw_runtime_am012_4cd9e_008a\nL_open_cfw_runtime_am012_4cd9e_0038:\n    movs r1, #0\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am012_addr_0044b898\n    bl .\n    cmp r0, #0\n    beq L_open_cfw_runtime_am012_4cd9e_0048\n    movs r0, #2\n    b L_open_cfw_runtime_am012_4cd9e_008a\nL_open_cfw_runtime_am012_4cd9e_0048:\n    movs r1, #0\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am012_addr_0044b8a2\n    bl .\n    cmp r0, #0\n    beq L_open_cfw_runtime_am012_4cd9e_0058\n    movs r0, #2\n    b L_open_cfw_runtime_am012_4cd9e_008a\nL_open_cfw_runtime_am012_4cd9e_0058:\n    movs r1, #0\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am012_addr_0044b8c4\n    bl .\n    cmp r0, #0xff\n    beq L_open_cfw_runtime_am012_4cd9e_0068\n    movs r0, #1\n    b L_open_cfw_runtime_am012_4cd9e_008a\nL_open_cfw_runtime_am012_4cd9e_0068:\n    movs r1, #0\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am012_addr_0044b902\n    bl .\n    cmp r0, #0\n    beq L_open_cfw_runtime_am012_4cd9e_0078\n    movs r0, #1\n    b L_open_cfw_runtime_am012_4cd9e_008a\nL_open_cfw_runtime_am012_4cd9e_0078:\n    movs r1, #0\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am012_addr_0044b8ea\n    bl .\n    cmp r0, #0\n    beq L_open_cfw_runtime_am012_4cd9e_0088\n    movs r0, #1\n    b L_open_cfw_runtime_am012_4cd9e_008a\nL_open_cfw_runtime_am012_4cd9e_0088:\n    movs r0, #0\nL_open_cfw_runtime_am012_4cd9e_008a:\n    pop {r4, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM012_4CE2A_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am012_4ce2a(void)
{
    __asm__ volatile(
        "    bx lr\n"
    );
}
#endif

#if defined(OPEN_CFW_AM012_4CE2C_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am012_4ce2c(void)
{
    __asm__ volatile(
        "    push {r3, r4, r5, r6, r7, lr}\n    movs r5, r0\n    movs r4, r1\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am012_addr_0044b7c0\n    bl .\n    cmp r0, #0\n    beq L_open_cfw_runtime_am012_4ce2c_0034\n    ldr r5, [r5]\n    movs r6, #0\n    b L_open_cfw_runtime_am012_4ce2c_0018\nL_open_cfw_runtime_am012_4ce2c_0016:\n    adds r6, r6, #1\nL_open_cfw_runtime_am012_4ce2c_0018:\n    ldrb.w r0, [r5, r6, lsl #3]\n    cmp r0, #0\n    beq L_open_cfw_runtime_am012_4ce2c_005a\n    movs r1, r4\n    uxtb r1, r1\n    ldrb.w r0, [r5, r6, lsl #3]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am012_addr_0044b844\n    bl .\n    cmp r0, #0\n    beq L_open_cfw_runtime_am012_4ce2c_0016\n    movs r0, #1\n    b L_open_cfw_runtime_am012_4ce2c_005c\nL_open_cfw_runtime_am012_4ce2c_0034:\n    ldr r0, [r5]\n    ldrb r1, [r5, #8]\n    add.w r6, r0, r1, lsl #2\n    movs r7, #0\n    b L_open_cfw_runtime_am012_4ce2c_0042\nL_open_cfw_runtime_am012_4ce2c_0040:\n    adds r7, r7, #1\nL_open_cfw_runtime_am012_4ce2c_0042:\n    ldrb r0, [r5, #8]\n    cmp r7, r0\n    bhs L_open_cfw_runtime_am012_4ce2c_005a\n    movs r1, r4\n    uxtb r1, r1\n    ldrb r0, [r6, r7]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am012_addr_0044b844\n    bl .\n    cmp r0, #0\n    beq L_open_cfw_runtime_am012_4ce2c_0040\n    movs r0, #1\n    b L_open_cfw_runtime_am012_4ce2c_005c\nL_open_cfw_runtime_am012_4ce2c_005a:\n    movs r0, #0\nL_open_cfw_runtime_am012_4ce2c_005c:\n    pop {r1, r4, r5, r6, r7, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM012_4CE8A_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am012_4ce8a(void)
{
    __asm__ volatile(
        "    push.w {r4, r5, r6, r7, r8, lr}\n    movs r4, r0\n    mov r8, r1\n    movs r6, r2\n    movs r7, r3\n    mov r0, r8\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am012_addr_0044b860\n    bl .\n    movs r5, r0\n    movs r3, r7\n    movs r2, r6\n    uxtb r2, r2\n    mov r1, r8\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am012_addr_0044c834\n    bl .\n    uxtb r0, r0\n    cmp r0, #1\n    bne L_open_cfw_runtime_am012_4ce8a_002c\n    movs r0, #1\n    b L_open_cfw_runtime_am012_4ce8a_00d2\nL_open_cfw_runtime_am012_4ce8a_002c:\n    movs r1, #0\n    movs r0, r6\n    uxtb r0, r0\n    cmp r0, #0x8a\n    bge L_open_cfw_runtime_am012_4ce8a_0044\n    ldr r0, [pc, #0xcc]\n    movs r1, r6\n    uxtb r1, r1\n    ldrb r1, [r0, r1]\n    ands r1, r1, #1\n    b L_open_cfw_runtime_am012_4ce8a_005c\nL_open_cfw_runtime_am012_4ce8a_0044:\n    ldr r2, [pc, #0xc4]\n    ldr r0, [r2, #0x30]\n    cmp r0, #0\n    beq L_open_cfw_runtime_am012_4ce8a_005c\n    ldr r0, [r2, #0x30]\n    movs r1, r6\n    uxtb r1, r1\n    add r0, r1\n    ldrb r1, [r0, #-0x8a]\n    ands r1, r1, #1\nL_open_cfw_runtime_am012_4ce8a_005c:\n    uxtb r1, r1\n    cmp r1, #0\n    beq L_open_cfw_runtime_am012_4ce8a_008e\n    cmp r5, #0\n    beq L_open_cfw_runtime_am012_4ce8a_006a\n    movs r5, #0\n    b L_open_cfw_runtime_am012_4ce8a_0070\nL_open_cfw_runtime_am012_4ce8a_006a:\n    ldr r4, [r4, #4]\n    b L_open_cfw_runtime_am012_4ce8a_0070\nL_open_cfw_runtime_am012_4ce8a_006e:\n    ldr r4, [r4, #4]\nL_open_cfw_runtime_am012_4ce8a_0070:\n    cmp r4, #0\n    beq L_open_cfw_runtime_am012_4ce8a_00d0\n    ldrh r1, [r4, #0x28]\n    orrs r1, r5\n    movs r3, r7\n    movs r2, r6\n    uxtb r2, r2\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am012_addr_0044c834\n    bl .\n    uxtb r0, r0\n    cmp r0, #1\n    bne L_open_cfw_runtime_am012_4ce8a_006e\n    movs r0, #1\n    b L_open_cfw_runtime_am012_4ce8a_00d2\nL_open_cfw_runtime_am012_4ce8a_008e:\n    cmp r5, #0\n    bne L_open_cfw_runtime_am012_4ce8a_00d0\n    movs r0, r6\n    uxtb r0, r0\n    cmp r0, #1\n    beq L_open_cfw_runtime_am012_4ce8a_00a2\n    movs r0, r6\n    uxtb r0, r0\n    cmp r0, #2\n    bne L_open_cfw_runtime_am012_4ce8a_00d0\nL_open_cfw_runtime_am012_4ce8a_00a2:\n    ldr r1, [r4]\n    b L_open_cfw_runtime_am012_4ce8a_00a8\nL_open_cfw_runtime_am012_4ce8a_00a6:\n    ldr r1, [r1]\nL_open_cfw_runtime_am012_4ce8a_00a8:\n    cmp r1, #0\n    beq L_open_cfw_runtime_am012_4ce8a_00d0\n    movs r0, r6\n    uxtb r0, r0\n    cmp r0, #1\n    bne L_open_cfw_runtime_am012_4ce8a_00c2\n    ldr r0, [r1, #0x18]\n    cmp r0, #0\n    beq L_open_cfw_runtime_am012_4ce8a_00a6\n    ldr r0, [r1, #0x18]\n    str r0, [r7]\n    movs r0, #1\n    b L_open_cfw_runtime_am012_4ce8a_00d2\nL_open_cfw_runtime_am012_4ce8a_00c2:\n    ldr r0, [r1, #0x1c]\n    cmp r0, #0\n    beq L_open_cfw_runtime_am012_4ce8a_00a6\n    ldr r0, [r1, #0x1c]\n    str r0, [r7]\n    movs r0, #1\n    b L_open_cfw_runtime_am012_4ce8a_00d2\nL_open_cfw_runtime_am012_4ce8a_00d0:\n    movs r0, #0\nL_open_cfw_runtime_am012_4ce8a_00d2:\n    pop.w {r4, r5, r6, r7, r8, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM012_4CF98_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am012_4cf98(void)
{
    __asm__ volatile(
        "    push {r0, r1, r2, r3, r4, r5, r6, lr}\n    movs r6, r0\n    movs r4, r1\n    movs r0, r6\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am012_4d230\n    bl .\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am012_addr_0044f730\n    bl .\n    movs r5, r0\n    cmp r5, #0\n    bne L_open_cfw_runtime_am012_4cf98_001a\n    movs r0, #0\n    b L_open_cfw_runtime_am012_4cf98_0134\nL_open_cfw_runtime_am012_4cf98_001a:\n    str r6, [r5]\n    str r4, [r5, #4]\n    cmp r4, #0\n    bne L_open_cfw_runtime_am012_4cf98_00d4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am012_addr_0044fa1a\n    bl .\n    movs r4, r0\n    cmp r4, #0\n    bne L_open_cfw_runtime_am012_4cf98_0046\n    ldr r0, [pc, #0x108]\n    str r0, [sp]\n    ldr r3, [pc, #0x108]\n    movs r2, #0x3d\n    ldr r1, [pc, #0x108]\n    movs r0, #2\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am012_4d25c\n    bl .\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am012_addr_0044f758\n    bl .\n    movs r0, #0\n    b L_open_cfw_runtime_am012_4cf98_0134\nL_open_cfw_runtime_am012_4cf98_0046:\n    ldr.w r0, [r4, #0x2b8]\n    cmp r0, #0\n    bne L_open_cfw_runtime_am012_4cf98_0054\n    movs r0, #0\n    str.w r0, [r4, #0x2d4]\nL_open_cfw_runtime_am012_4cf98_0054:\n    ldr.w r1, [r4, #0x2d4]\n    adds r1, r1, #1\n    lsls r1, r1, #2\n    ldr.w r0, [r4, #0x2b8]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am012_addr_0044f76a\n    bl .\n    cmp r0, #0\n    bne L_open_cfw_runtime_am012_4cf98_008a\n    ldr r0, [pc, #0xd8]\n    str r0, [sp, #8]\n    ldr r0, [pc, #0xd8]\n    str r0, [sp, #4]\n    ldr r0, [pc, #0xd8]\n    str r0, [sp]\n    ldr r3, [pc, #0xc4]\n    movs r2, #0x47\n    ldr r1, [pc, #0xc4]\n    movs r0, #3\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am012_4d25c\n    bl .\nL_open_cfw_runtime_am012_4cf98_0080:\n    movs r0, #0\n    movs.w r1, #-1\n    str r0, [r1]\n    b L_open_cfw_runtime_am012_4cf98_0080\nL_open_cfw_runtime_am012_4cf98_008a:\n    cmp r0, #0\n    bne L_open_cfw_runtime_am012_4cf98_0098\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am012_addr_0044f758\n    bl .\n    movs r0, #0\n    b L_open_cfw_runtime_am012_4cf98_0134\nL_open_cfw_runtime_am012_4cf98_0098:\n    ldr.w r1, [r4, #0x2d4]\n    adds r1, r1, #1\n    str.w r1, [r4, #0x2d4]\n    str.w r0, [r4, #0x2b8]\n    ldr.w r0, [r4, #0x2b8]\n    ldr.w r1, [r4, #0x2d4]\n    add.w r0, r0, r1, lsl #2\n    str r5, [r0, #-0x4]\n    movs r0, #0\n    str r0, [r5, #0x14]\n    movs r0, #0\n    str r0, [r5, #0x18]\n    movs r0, #0\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am012_addr_0044fa7e\n    bl .\n    subs r0, r0, #1\n    str r0, [r5, #0x1c]\n    movs r0, #0\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am012_addr_0044faa8\n    bl .\n    subs r0, r0, #1\n    str r0, [r5, #0x20]\n    b L_open_cfw_runtime_am012_4cf98_0132\nL_open_cfw_runtime_am012_4cf98_00d4:\n    cmp r4, #0\n    bne L_open_cfw_runtime_am012_4cf98_00fa\n    ldr r0, [pc, #0x74]\n    str r0, [sp, #8]\n    ldr r0, [pc, #0x74]\n    str r0, [sp, #4]\n    ldr r0, [pc, #0x68]\n    str r0, [sp]\n    ldr r3, [pc, #0x54]\n    movs r2, #0x5a\n    ldr r1, [pc, #0x54]\n    movs r0, #3\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am012_4d25c\n    bl .\nL_open_cfw_runtime_am012_4cf98_00f0:\n    movs r0, #0\n    movs.w r1, #-1\n    str r0, [r1]\n    b L_open_cfw_runtime_am012_4cf98_00f0\nL_open_cfw_runtime_am012_4cf98_00fa:\n    ldr r0, [r4, #8]\n    cmp r0, #0\n    bne L_open_cfw_runtime_am012_4cf98_0106\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am012_addr_0043e1fa\n    bl .\nL_open_cfw_runtime_am012_4cf98_0106:\n    ldr r0, [r4, #8]\n    ldrh r0, [r0, #0x30]\n    adds r0, r0, #1\n    ldr r1, [r4, #8]\n    strh r0, [r1, #0x30]\n    ldr r0, [r4, #8]\n    ldrh r1, [r0, #0x30]\n    lsls r1, r1, #2\n    ldr r0, [r4, #8]\n    ldr r0, [r0]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am012_addr_0044f76a\n    bl .\n    ldr r1, [r4, #8]\n    str r0, [r1]\n    ldr r0, [r4, #8]\n    ldr r0, [r0]\n    ldr r1, [r4, #8]\n    ldrh r1, [r1, #0x30]\n    add.w r0, r0, r1, lsl #2\n    str r5, [r0, #-0x4]\nL_open_cfw_runtime_am012_4cf98_0132:\n    movs r0, r5\nL_open_cfw_runtime_am012_4cf98_0134:\n    add sp, #0x10\n    pop {r4, r5, r6, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM012_4D0F0_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am012_4d0f0(void)
{
    __asm__ volatile(
        "    push {r3, r4, r5, lr}\n    movs r5, r0\n    cmp r5, #0\n    beq L_open_cfw_runtime_am012_4d0f0_007c\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am012_addr_0043f648\n    bl .\n    movs r0, #0\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am012_addr_0044bde0\n    bl .\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am012_addr_00482f8a\n    bl .\n    movs r1, r5\n    ldr r0, [r5]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am012_4d1fc\n    bl .\n    movs r0, #1\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am012_addr_0044bde0\n    bl .\n    movs r2, #0xff\n    movs.w r1, #0xf0000\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am012_addr_0044bc8c\n    bl .\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am012_addr_0043ffa0\n    bl .\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am012_4d33a\n    bl .\n    movs r4, r0\n    cmp r4, #0\n    beq L_open_cfw_runtime_am012_4d0f0_0056\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am012_4d1cc\n    bl .\n    cmp r0, #0\n    beq L_open_cfw_runtime_am012_4d0f0_0056\n    movs r1, r5\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am012_4d342\n    bl .\nL_open_cfw_runtime_am012_4d0f0_0056:\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am012_addr_0044dca2\n    bl .\n    movs r4, r0\n    cmp r4, #0\n    beq L_open_cfw_runtime_am012_4d0f0_007c\n    movs r2, r5\n    movs r1, #0x2a\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am012_addr_00451670\n    bl .\n    movs r2, r5\n    movs r1, #0x2b\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am012_addr_00451670\n    bl .\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am012_addr_00440656\n    bl .\nL_open_cfw_runtime_am012_4d0f0_007c:\n    pop {r0, r4, r5, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM012_4D16E_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am012_4d16e(void)
{
    __asm__ volatile(
        "L_open_cfw_runtime_am012_4d16e_0000:\n    push {r4, lr}\n    movs r4, r0\n    ldr r0, [r4]\n    ldr r0, [r0, #8]\n    cmp r0, #0\n    beq L_open_cfw_runtime_am012_4d16e_0016\n    movs r1, r4\n    ldr r0, [r4]\n    ldr r2, [r4]\n    ldr r2, [r2, #8]\n    blx r2\nL_open_cfw_runtime_am012_4d16e_0016:\n    ldr r0, [r4]\n    ldr r0, [r0]\n    cmp r0, #0\n    beq L_open_cfw_runtime_am012_4d16e_002a\n    ldr r0, [r4]\n    ldr r0, [r0]\n    str r0, [r4]\n    movs r0, r4\n    bl L_open_cfw_runtime_am012_4d16e_0000\nL_open_cfw_runtime_am012_4d16e_002a:\n    pop {r4, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM012_4D19A_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am012_4d19a(void)
{
    __asm__ volatile(
        "    ldr r0, [r0]\n    b L_open_cfw_runtime_am012_4d19a_0006\nL_open_cfw_runtime_am012_4d19a_0004:\n    ldr r0, [r0]\nL_open_cfw_runtime_am012_4d19a_0006:\n    cmp r0, #0\n    beq L_open_cfw_runtime_am012_4d19a_0014\n    ldrb.w r1, [r0, #0x20]\n    tst.w r1, #3\n    beq L_open_cfw_runtime_am012_4d19a_0004\nL_open_cfw_runtime_am012_4d19a_0014:\n    cmp r0, #0\n    bne L_open_cfw_runtime_am012_4d19a_001c\n    movs r0, #0\n    b L_open_cfw_runtime_am012_4d19a_0030\nL_open_cfw_runtime_am012_4d19a_001c:\n    ldrb.w r0, [r0, #0x20]\n    ands r0, r0, #3\n    cmp r0, #1\n    bne L_open_cfw_runtime_am012_4d19a_002c\n    movs r0, #1\n    b L_open_cfw_runtime_am012_4d19a_002e\nL_open_cfw_runtime_am012_4d19a_002c:\n    movs r0, #0\nL_open_cfw_runtime_am012_4d19a_002e:\n    uxtb r0, r0\nL_open_cfw_runtime_am012_4d19a_0030:\n    bx lr\n"
    );
}
#endif

#if defined(OPEN_CFW_AM012_4D1CC_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am012_4d1cc(void)
{
    __asm__ volatile(
        "    ldr r0, [r0]\n    b L_open_cfw_runtime_am012_4d1cc_0006\nL_open_cfw_runtime_am012_4d1cc_0004:\n    ldr r0, [r0]\nL_open_cfw_runtime_am012_4d1cc_0006:\n    cmp r0, #0\n    beq L_open_cfw_runtime_am012_4d1cc_0014\n    ldr r1, [r0, #0x20]\n    ubfx r1, r1, #2, #2\n    cmp r1, #0\n    beq L_open_cfw_runtime_am012_4d1cc_0004\nL_open_cfw_runtime_am012_4d1cc_0014:\n    cmp r0, #0\n    bne L_open_cfw_runtime_am012_4d1cc_001c\n    movs r0, #0\n    b L_open_cfw_runtime_am012_4d1cc_002e\nL_open_cfw_runtime_am012_4d1cc_001c:\n    ldr r0, [r0, #0x20]\n    ubfx r0, r0, #2, #2\n    cmp r0, #1\n    bne L_open_cfw_runtime_am012_4d1cc_002a\n    movs r0, #1\n    b L_open_cfw_runtime_am012_4d1cc_002c\nL_open_cfw_runtime_am012_4d1cc_002a:\n    movs r0, #0\nL_open_cfw_runtime_am012_4d1cc_002c:\n    uxtb r0, r0\nL_open_cfw_runtime_am012_4d1cc_002e:\n    bx lr\n"
    );
}
#endif

#if defined(OPEN_CFW_AM012_4D1FC_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am012_4d1fc(void)
{
    __asm__ volatile(
        "L_open_cfw_runtime_am012_4d1fc_0000:\n    push {r4, r5, r6, lr}\n    movs r4, r0\n    movs r5, r1\n    ldr r0, [r5]\n    ldr r0, [r0]\n    cmp r0, #0\n    beq L_open_cfw_runtime_am012_4d1fc_0020\n    ldr r6, [r5]\n    ldr r0, [r5]\n    ldr r0, [r0]\n    str r0, [r5]\n    movs r1, r5\n    movs r0, r4\n    bl L_open_cfw_runtime_am012_4d1fc_0000\n    str r6, [r5]\nL_open_cfw_runtime_am012_4d1fc_0020:\n    ldr r0, [r5]\n    ldr r0, [r0, #4]\n    cmp r0, #0\n    beq L_open_cfw_runtime_am012_4d1fc_0032\n    movs r1, r5\n    movs r0, r4\n    ldr r2, [r5]\n    ldr r2, [r2, #4]\n    blx r2\nL_open_cfw_runtime_am012_4d1fc_0032:\n    pop {r4, r5, r6, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM012_4D230_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am012_4d230(void)
{
    __asm__ volatile(
        "    .reloc ., R_ARM_THM_JUMP11, open_cfw_runtime_am012_addr_0044d234\n    b .\n"
    );
}
#endif

#if defined(OPEN_CFW_AM012_4D232_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am012_4d232(void)
{
    __asm__ volatile(
        "L_open_cfw_runtime_am012_4d232_0000:\n    ldr r0, [r0]\n    cmp r0, #0\n    beq L_open_cfw_runtime_am012_4d232_0010\n    ldr r1, [r0, #0x20]\n    lsls r1, r1, #0xc\n    lsrs r1, r1, #0x10\n    cmp r1, #0\n    beq L_open_cfw_runtime_am012_4d232_0000\nL_open_cfw_runtime_am012_4d232_0010:\n    cmp r0, #0\n    bne L_open_cfw_runtime_am012_4d232_0018\n    movs r0, #0\n    b L_open_cfw_runtime_am012_4d232_001e\nL_open_cfw_runtime_am012_4d232_0018:\n    ldr r0, [r0, #0x20]\n    ubfx r0, r0, #4, #0x10\nL_open_cfw_runtime_am012_4d232_001e:\n    bx lr\n"
    );
}
#endif

#if defined(OPEN_CFW_AM012_4D254_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am012_4d254(void)
{
    __asm__ volatile(
        "    ldr r1, [pc, #0xc8]\n    str.w r0, [r1, #0x16c]\n    bx lr\n"
    );
}
#endif

#if defined(OPEN_CFW_AM012_4D25C_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am012_4d25c(void)
{
    __asm__ volatile(
        "    push.w {r4, r5, r6, r7, r8, sb, sl, fp, lr}\n    sub.w sp, sp, #0x31c\n    movs r6, r0\n    movs r7, r2\n    mov r8, r3\n    movs r0, r6\n    sxtb r0, r0\n    cmp r0, #6\n    bge L_open_cfw_runtime_am012_4d25c_00ba\n    movs r0, r6\n    sxtb r0, r0\n    cmp r0, #2\n    blt L_open_cfw_runtime_am012_4d25c_00ba\n    movs r5, r1\n    add.w sb, sp, #0x344\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am012_addr_00454768\n    bl .\n    movs r4, r0\n    b L_open_cfw_runtime_am012_4d25c_0030\nL_open_cfw_runtime_am012_4d25c_002e:\n    subs r4, r4, #1\nL_open_cfw_runtime_am012_4d25c_0030:\n    cmp r4, #0\n    beq L_open_cfw_runtime_am012_4d25c_0042\n    ldrb r0, [r5, r4]\n    cmp r0, #0x2f\n    beq L_open_cfw_runtime_am012_4d25c_0040\n    ldrb r0, [r5, r4]\n    cmp r0, #0x5c\n    bne L_open_cfw_runtime_am012_4d25c_002e\nL_open_cfw_runtime_am012_4d25c_0040:\n    adds r4, r4, #1\nL_open_cfw_runtime_am012_4d25c_0042:\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am012_addr_00473482\n    bl .\n    mov sl, r0\n    ldr.w fp, [pc, #0x78]\n    ldr.w r0, [fp, #0x16c]\n    cmp r0, #0\n    beq L_open_cfw_runtime_am012_4d25c_00b6\n    ldr r2, [sp, #0x340]\n    mov r3, sb\n    mov.w r1, #0x100\n    add r0, sp, #0x1c\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am012_addr_00483fea\n    bl .\n    mov.w r0, #0x3e8\n    str r7, [sp, #0x18]\n    add.w r1, r5, r4\n    str r1, [sp, #0x14]\n    add r1, sp, #0x1c\n    str r1, [sp, #0x10]\n    str.w r8, [sp, #0xc]\n    ldr.w r1, [fp, #0x170]\n    subs.w r1, sl, r1\n    str r1, [sp, #8]\n    udiv r1, sl, r0\n    mls r0, r0, r1, sl\n    str r0, [sp, #4]\n    mov.w r0, #0x3e8\n    udiv r0, sl, r0\n    str r0, [sp]\n    ldr r0, [pc, #0x30]\n    movs r1, r6\n    sxtb r1, r1\n    ldr.w r3, [r0, r1, lsl #2]\n    ldr r2, [pc, #0x2c]\n    mov.w r1, #0x200\n    add r0, sp, #0x11c\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am012_addr_00483fd0\n    bl .\n    add r1, sp, #0x11c\n    movs r0, r6\n    sxtb r0, r0\n    ldr.w r2, [fp, #0x16c]\n    blx r2\nL_open_cfw_runtime_am012_4d25c_00b6:\n    str.w sl, [fp, #0x170]\nL_open_cfw_runtime_am012_4d25c_00ba:\n    add.w sp, sp, #0x31c\n    pop.w {r4, r5, r6, r7, r8, sb, sl, fp, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM012_4D32C_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am012_4d32c(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    movs r1, #0x20\n    ldr.w r0, [pc, #0x284]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am012_addr_00482b00\n    bl .\n    pop {r0, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM012_4D33A_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am012_4d33a(void)
{
    __asm__ volatile(
        "    ldr.w r0, [pc, #0x294]\n    ldr r0, [r0, #0x40]\n    bx lr\n"
    );
}
#endif

#if defined(OPEN_CFW_AM012_4D342_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am012_4d342(void)
{
    __asm__ volatile(
        "    push {r0, r1, r2, r3, r4, r5, r6, lr}\n    movs r5, r0\n    movs r6, r1\n    cmp r5, #0\n    beq L_open_cfw_runtime_am012_4d342_006e\n    movs r0, r6\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am012_4d3b2\n    bl .\n    ldr r0, [r6, #8]\n    cmp r0, #0\n    bne L_open_cfw_runtime_am012_4d342_001c\n    movs r0, r6\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am012_addr_0043e1fa\n    bl .\nL_open_cfw_runtime_am012_4d342_001c:\n    ldr r0, [r6, #8]\n    str r5, [r0, #4]\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am012_addr_00482bca\n    bl .\n    movs r4, r0\n    cmp r4, #0\n    bne L_open_cfw_runtime_am012_4d342_0058\n    ldr.w r0, [pc, #0x24c]\n    str r0, [sp, #8]\n    ldr.w r0, [pc, #0x25c]\n    str r0, [sp, #4]\n    ldr.w r0, [pc, #0x248]\n    str r0, [sp]\n    ldr.w r3, [pc, #0x254]\n    movs r2, #0x81\n    ldr.w r1, [pc, #0x240]\n    movs r0, #3\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am012_4d25c\n    bl .\nL_open_cfw_runtime_am012_4d342_004e:\n    movs r0, #0\n    movs.w r1, #-1\n    str r0, [r1]\n    b L_open_cfw_runtime_am012_4d342_004e\nL_open_cfw_runtime_am012_4d342_0058:\n    cmp r4, #0\n    beq L_open_cfw_runtime_am012_4d342_006e\n    str r6, [r4]\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am012_addr_00482cd8\n    bl .\n    cmp r0, r4\n    bne L_open_cfw_runtime_am012_4d342_006e\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am012_4d5f8\n    bl .\nL_open_cfw_runtime_am012_4d342_006e:\n    pop {r0, r1, r2, r3, r4, r5, r6, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM012_4D3B2_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am012_4d3b2(void)
{
    __asm__ volatile(
        "    push {r4, r5, r6, lr}\n    movs r6, r0\n    movs r0, r6\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am012_addr_0043e1be\n    bl .\n    movs r5, r0\n    cmp r5, #0\n    beq L_open_cfw_runtime_am012_4d3b2_00a8\n    ldr r0, [r5, #0xc]\n    cmp r0, #0\n    beq L_open_cfw_runtime_am012_4d3b2_005e\n    ldr r0, [r5, #0xc]\n    ldr r0, [r0]\n    cmp r0, r6\n    bne L_open_cfw_runtime_am012_4d3b2_005e\n    ldrb r0, [r5, #0x1c]\n    lsls r0, r0, #0x1f\n    bpl L_open_cfw_runtime_am012_4d3b2_002c\n    ldrb r0, [r5, #0x1c]\n    ands r0, r0, #0xfe\n    strb r0, [r5, #0x1c]\nL_open_cfw_runtime_am012_4d3b2_002c:\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am012_addr_00482cd8\n    bl .\n    ldr r1, [r5, #0xc]\n    cmp r0, r1\n    bne L_open_cfw_runtime_am012_4d3b2_0058\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am012_addr_00482ce4\n    bl .\n    ldr r1, [r5, #0xc]\n    cmp r0, r1\n    bne L_open_cfw_runtime_am012_4d3b2_0058\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am012_4d77a\n    bl .\n    movs r2, r0\n    movs r1, #0x14\n    ldr r0, [r5, #0xc]\n    ldr r0, [r0]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am012_addr_00451670\n    bl .\n    b L_open_cfw_runtime_am012_4d3b2_005e\nL_open_cfw_runtime_am012_4d3b2_0058:\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am012_4d5f8\n    bl .\nL_open_cfw_runtime_am012_4d3b2_005e:\n    ldr r0, [r5, #0xc]\n    cmp r0, #0\n    beq L_open_cfw_runtime_am012_4d3b2_0070\n    ldr r0, [r5, #0xc]\n    ldr r0, [r0]\n    cmp r0, r6\n    bne L_open_cfw_runtime_am012_4d3b2_0070\n    movs r0, #0\n    str r0, [r5, #0xc]\nL_open_cfw_runtime_am012_4d3b2_0070:\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am012_addr_00482cd8\n    bl .\n    movs r4, r0\n    b L_open_cfw_runtime_am012_4d3b2_0084\nL_open_cfw_runtime_am012_4d3b2_007a:\n    movs r1, r4\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am012_addr_00482cf0\n    bl .\n    movs r4, r0\nL_open_cfw_runtime_am012_4d3b2_0084:\n    cmp r4, #0\n    beq L_open_cfw_runtime_am012_4d3b2_00a8\n    ldr r0, [r4]\n    cmp r0, r6\n    bne L_open_cfw_runtime_am012_4d3b2_007a\n    movs r1, r4\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am012_addr_00482c0e\n    bl .\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am012_addr_0044f758\n    bl .\n    ldr r0, [r6, #8]\n    cmp r0, #0\n    beq L_open_cfw_runtime_am012_4d3b2_00a8\n    movs r0, #0\n    ldr r1, [r6, #8]\n    str r0, [r1, #4]\nL_open_cfw_runtime_am012_4d3b2_00a8:\n    pop {r4, r5, r6, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM012_4D45C_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am012_4d45c(void)
{
    __asm__ volatile(
        "    push {r0, r1, r2, r3, r4, lr}\n    movs r4, r0\n    cmp r4, #0\n    bne L_open_cfw_runtime_am012_4d45c_0036\n    ldr.w r0, [pc, #0x164]\n    str r0, [sp, #8]\n    ldr.w r0, [pc, #0x154]\n    str r0, [sp, #4]\n    ldr.w r0, [pc, #0x150]\n    str r0, [sp]\n    ldr.w r3, [pc, #0x164]\n    mov.w r2, #0x102\n    ldr.w r1, [pc, #0x148]\n    movs r0, #3\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am012_4d25c\n    bl .\nL_open_cfw_runtime_am012_4d45c_002c:\n    movs r0, #0\n    movs.w r1, #-1\n    str r0, [r1]\n    b L_open_cfw_runtime_am012_4d45c_002c\nL_open_cfw_runtime_am012_4d45c_0036:\n    ldr.w r2, [pc, #0x14c]\n    ldr.w r1, [pc, #0x14c]\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am012_4d63a\n    bl .\n    ldr r1, [r4, #0x14]\n    cmp r1, #0\n    beq L_open_cfw_runtime_am012_4d45c_0058\n    uxtb r0, r0\n    cmp r0, #0\n    bne L_open_cfw_runtime_am012_4d45c_0058\n    movs r1, #1\n    movs r0, r4\n    ldr r2, [r4, #0x14]\n    blx r2\nL_open_cfw_runtime_am012_4d45c_0058:\n    pop {r0, r1, r2, r3, r4, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM012_4D4B6_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am012_4d4b6(void)
{
    __asm__ volatile(
        "    push {r0, r1, r2, r3, r4, lr}\n    movs r4, r0\n    cmp r4, #0\n    bne L_open_cfw_runtime_am012_4d4b6_0036\n    ldr.w r0, [pc, #0x10c]\n    str r0, [sp, #8]\n    ldr.w r0, [pc, #0xf8]\n    str r0, [sp, #4]\n    ldr.w r0, [pc, #0xf8]\n    str r0, [sp]\n    ldr.w r3, [pc, #0x114]\n    movw r2, #0x10d\n    ldr.w r1, [pc, #0xec]\n    movs r0, #3\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am012_4d25c\n    bl .\nL_open_cfw_runtime_am012_4d4b6_002c:\n    movs r0, #0\n    movs.w r1, #-1\n    str r0, [r1]\n    b L_open_cfw_runtime_am012_4d4b6_002c\nL_open_cfw_runtime_am012_4d4b6_0036:\n    ldr.w r2, [pc, #0xfc]\n    ldr.w r1, [pc, #0xfc]\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am012_4d63a\n    bl .\n    ldr r1, [r4, #0x14]\n    cmp r1, #0\n    beq L_open_cfw_runtime_am012_4d4b6_0058\n    uxtb r0, r0\n    cmp r0, #0\n    bne L_open_cfw_runtime_am012_4d4b6_0058\n    movs r1, #0\n    movs r0, r4\n    ldr r2, [r4, #0x14]\n    blx r2\nL_open_cfw_runtime_am012_4d4b6_0058:\n    pop {r0, r1, r2, r3, r4, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM012_4D510_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am012_4d510(void)
{
    __asm__ volatile(
        "    push {r1, r2, r3, r4, r5, lr}\n    movs r5, r0\n    cmp r5, #0\n    bne L_open_cfw_runtime_am012_4d510_002c\n    ldr r0, [pc, #0xb0]\n    str r0, [sp, #8]\n    ldr r0, [pc, #0xa0]\n    str r0, [sp, #4]\n    ldr r0, [pc, #0xa0]\n    str r0, [sp]\n    ldr r3, [pc, #0xcc]\n    mov.w r2, #0x13a\n    ldr r1, [pc, #0x9c]\n    movs r0, #3\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am012_4d25c\n    bl .\nL_open_cfw_runtime_am012_4d510_0022:\n    movs r0, #0\n    movs.w r1, #-1\n    str r0, [r1]\n    b L_open_cfw_runtime_am012_4d510_0022\nL_open_cfw_runtime_am012_4d510_002c:\n    uxtb r1, r1\n    cmp r1, #0\n    beq L_open_cfw_runtime_am012_4d510_0036\n    movs r0, #1\n    b L_open_cfw_runtime_am012_4d510_0038\nL_open_cfw_runtime_am012_4d510_0036:\n    movs r0, #0\nL_open_cfw_runtime_am012_4d510_0038:\n    movs r1, r0\n    ldrb r2, [r5, #0x1c]\n    ubfx r2, r2, #1, #1\n    uxtb r1, r1\n    uxtb r2, r2\n    cmp r1, r2\n    beq L_open_cfw_runtime_am012_4d510_007a\n    ldrb r1, [r5, #0x1c]\n    bfi r1, r0, #1, #1\n    strb r1, [r5, #0x1c]\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am012_4d58c\n    bl .\n    movs r4, r0\n    cmp r4, #0\n    beq L_open_cfw_runtime_am012_4d510_007a\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am012_4d77a\n    bl .\n    movs r2, r0\n    movs r1, #0x13\n    ldr r0, [r5, #0xc]\n    ldr r0, [r0]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am012_addr_00451670\n    bl .\n    uxtb r0, r0\n    cmp r0, #1\n    bne L_open_cfw_runtime_am012_4d510_007a\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am012_addr_00440656\n    bl .\nL_open_cfw_runtime_am012_4d510_007a:\n    pop {r0, r1, r2, r4, r5, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM012_4D58C_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am012_4d58c(void)
{
    __asm__ volatile(
        "    cmp r0, #0\n    bne L_open_cfw_runtime_am012_4d58c_0008\n    movs r0, #0\n    b L_open_cfw_runtime_am012_4d58c_0016\nL_open_cfw_runtime_am012_4d58c_0008:\n    ldr r1, [r0, #0xc]\n    cmp r1, #0\n    bne L_open_cfw_runtime_am012_4d58c_0012\n    movs r0, #0\n    b L_open_cfw_runtime_am012_4d58c_0016\nL_open_cfw_runtime_am012_4d58c_0012:\n    ldr r0, [r0, #0xc]\n    ldr r0, [r0]\nL_open_cfw_runtime_am012_4d58c_0016:\n    bx lr\n"
    );
}
#endif

#if defined(OPEN_CFW_AM012_4D5A4_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am012_4d5a4(void)
{
    __asm__ volatile(
        "    cmp r0, #0\n    bne L_open_cfw_runtime_am012_4d5a4_0008\n    movs r0, #0\n    b L_open_cfw_runtime_am012_4d5a4_0012\nL_open_cfw_runtime_am012_4d5a4_0008:\n    ldrb r0, [r0, #0x1c]\n    uxtb r0, r0\n    lsrs r0, r0, #1\n    ands r0, r0, #1\nL_open_cfw_runtime_am012_4d5a4_0012:\n    bx lr\n"
    );
}
#endif

#if defined(OPEN_CFW_AM012_4D5F8_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am012_4d5f8(void)
{
    __asm__ volatile(
        "    push {r3, r4, r5, lr}\n    movs r4, r0\n    ldrb r0, [r4, #0x1c]\n    ubfx r5, r0, #3, #1\n    ldrb r0, [r4, #0x1c]\n    orrs r0, r0, #8\n    strb r0, [r4, #0x1c]\n    ldrb r0, [r4, #0x1c]\n    ubfx r0, r0, #2, #1\n    uxtb r0, r0\n    cmp r0, #0\n    bne L_open_cfw_runtime_am012_4d5f8_0026\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am012_4d45c\n    bl .\n    b L_open_cfw_runtime_am012_4d5f8_0038\nL_open_cfw_runtime_am012_4d5f8_0026:\n    ldrb r0, [r4, #0x1c]\n    ubfx r0, r0, #2, #1\n    uxtb r0, r0\n    cmp r0, #0\n    beq L_open_cfw_runtime_am012_4d5f8_0038\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am012_4d4b6\n    bl .\nL_open_cfw_runtime_am012_4d5f8_0038:\n    ldrb r0, [r4, #0x1c]\n    bfi r0, r5, #3, #1\n    strb r0, [r4, #0x1c]\n    pop {r0, r4, r5, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM012_4D63A_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am012_4d63a(void)
{
    __asm__ volatile(
        "    push.w {r3, r4, r5, r6, r7, r8, sb, sl, fp, lr}\n    movs r7, r0\n    mov r8, r2\n    movs.w sb, #0\n    ldrb r0, [r7, #0x1c]\n    lsls r0, r0, #0x1f\n    bpl L_open_cfw_runtime_am012_4d63a_0018\n    mov r0, sb\n    uxtb r0, r0\n    b L_open_cfw_runtime_am012_4d63a_013c\nL_open_cfw_runtime_am012_4d63a_0018:\n    ldr r6, [r7, #0xc]\n    movs r4, #0\n    movs.w sl, #1\n    movs.w fp, #1\n    str r1, [sp]\n    b L_open_cfw_runtime_am012_4d63a_0060\nL_open_cfw_runtime_am012_4d63a_0028:\n    movs r0, r7\n    ldr r1, [sp]\n    blx r1\n    movs r6, r0\n    movs.w sl, #0\n    movs.w fp, #0\nL_open_cfw_runtime_am012_4d63a_0038:\n    cmp r4, #0\n    bne L_open_cfw_runtime_am012_4d63a_0042\n    movs r4, r6\n    cmp r4, #0\n    beq L_open_cfw_runtime_am012_4d63a_0084\nL_open_cfw_runtime_am012_4d63a_0042:\n    uxtb.w sl, sl\n    cmp.w sl, #0\n    beq L_open_cfw_runtime_am012_4d63a_0058\n    movs r1, r6\n    movs r0, r7\n    blx r8\n    movs r6, r0\n    cmp r6, r4\n    beq L_open_cfw_runtime_am012_4d63a_0090\nL_open_cfw_runtime_am012_4d63a_0058:\n    movs.w sl, #1\n    cmp r6, #0\n    bne L_open_cfw_runtime_am012_4d63a_0096\nL_open_cfw_runtime_am012_4d63a_0060:\n    cmp r6, #0\n    bne L_open_cfw_runtime_am012_4d63a_0038\n    ldrb r0, [r7, #0x1c]\n    ubfx r0, r0, #3, #1\n    uxtb r0, r0\n    cmp r0, #0\n    bne L_open_cfw_runtime_am012_4d63a_0074\n    cmp r4, #0\n    bne L_open_cfw_runtime_am012_4d63a_008a\nL_open_cfw_runtime_am012_4d63a_0074:\n    uxtb.w fp, fp\n    cmp.w fp, #0\n    bne L_open_cfw_runtime_am012_4d63a_0028\n    mov r0, sb\n    uxtb r0, r0\n    b L_open_cfw_runtime_am012_4d63a_013c\nL_open_cfw_runtime_am012_4d63a_0084:\n    mov r0, sb\n    uxtb r0, r0\n    b L_open_cfw_runtime_am012_4d63a_013c\nL_open_cfw_runtime_am012_4d63a_008a:\n    mov r0, sb\n    uxtb r0, r0\n    b L_open_cfw_runtime_am012_4d63a_013c\nL_open_cfw_runtime_am012_4d63a_0090:\n    mov r0, sb\n    uxtb r0, r0\n    b L_open_cfw_runtime_am012_4d63a_013c\nL_open_cfw_runtime_am012_4d63a_0096:\n    ldr r0, [r6]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am012_addr_0043e156\n    bl .\n    lsls r0, r0, #0x18\n    bmi L_open_cfw_runtime_am012_4d63a_0060\n    ldr r5, [r6]\n    b L_open_cfw_runtime_am012_4d63a_00ac\nL_open_cfw_runtime_am012_4d63a_00a4:\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am012_addr_0044dca2\n    bl .\n    movs r5, r0\nL_open_cfw_runtime_am012_4d63a_00ac:\n    cmp r5, #0\n    beq L_open_cfw_runtime_am012_4d63a_00bc\n    movs r1, #1\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am012_addr_0043e0e0\n    bl .\n    cmp r0, #0\n    beq L_open_cfw_runtime_am012_4d63a_00a4\nL_open_cfw_runtime_am012_4d63a_00bc:\n    cmp r5, #0\n    beq L_open_cfw_runtime_am012_4d63a_00cc\n    movs r1, #1\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am012_addr_0043e0e0\n    bl .\n    cmp r0, #0\n    bne L_open_cfw_runtime_am012_4d63a_0060\nL_open_cfw_runtime_am012_4d63a_00cc:\n    ldr r0, [r7, #0xc]\n    cmp r6, r0\n    bne L_open_cfw_runtime_am012_4d63a_00d8\n    mov r0, sb\n    uxtb r0, r0\n    b L_open_cfw_runtime_am012_4d63a_013c\nL_open_cfw_runtime_am012_4d63a_00d8:\n    ldr r0, [r7, #0xc]\n    cmp r0, #0\n    beq L_open_cfw_runtime_am012_4d63a_0104\n    movs r0, r7\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am012_4d77a\n    bl .\n    movs r2, r0\n    movs r1, #0x14\n    ldr r0, [r7, #0xc]\n    ldr r0, [r0]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am012_addr_00451670\n    bl .\n    uxtb r0, r0\n    cmp r0, #1\n    beq L_open_cfw_runtime_am012_4d63a_00fc\n    mov r0, sb\n    uxtb r0, r0\n    b L_open_cfw_runtime_am012_4d63a_013c\nL_open_cfw_runtime_am012_4d63a_00fc:\n    ldr r0, [r7, #0xc]\n    ldr r0, [r0]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am012_addr_00440656\n    bl .\nL_open_cfw_runtime_am012_4d63a_0104:\n    str r6, [r7, #0xc]\n    movs r0, r7\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am012_4d77a\n    bl .\n    movs r2, r0\n    movs r1, #0x13\n    ldr r0, [r7, #0xc]\n    ldr r0, [r0]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am012_addr_00451670\n    bl .\n    uxtb r0, r0\n    cmp r0, #1\n    beq L_open_cfw_runtime_am012_4d63a_0124\n    mov r0, sb\n    uxtb r0, r0\n    b L_open_cfw_runtime_am012_4d63a_013c\nL_open_cfw_runtime_am012_4d63a_0124:\n    ldr r0, [r7, #0xc]\n    ldr r0, [r0]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am012_addr_00440656\n    bl .\n    ldr r0, [r7, #0x10]\n    cmp r0, #0\n    beq L_open_cfw_runtime_am012_4d63a_0138\n    movs r0, r7\n    ldr r1, [r7, #0x10]\n    blx r1\nL_open_cfw_runtime_am012_4d63a_0138:\n    movs r0, #1\n    uxtb r0, r0\nL_open_cfw_runtime_am012_4d63a_013c:\n    pop.w {r1, r4, r5, r6, r7, r8, sb, sl, fp, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM012_4D77A_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am012_4d77a(void)
{
    __asm__ volatile(
        "    push {r4, r5, r6, lr}\n    movs r5, r0\n    movs r6, #0\n    movs r0, #0\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am012_addr_00452edc\n    bl .\n    movs r4, r0\n    b L_open_cfw_runtime_am012_4d77a_0024\nL_open_cfw_runtime_am012_4d77a_0010:\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am012_addr_00452f18\n    bl .\n    cmp r0, r5\n    bne L_open_cfw_runtime_am012_4d77a_001c\n    movs r6, r4\nL_open_cfw_runtime_am012_4d77a_001c:\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am012_addr_00452edc\n    bl .\n    movs r4, r0\nL_open_cfw_runtime_am012_4d77a_0024:\n    cmp r4, #0\n    beq L_open_cfw_runtime_am012_4d77a_0038\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am012_addr_00452f00\n    bl .\n    uxtb r0, r0\n    cmp r0, #1\n    bne L_open_cfw_runtime_am012_4d77a_0010\n    movs r0, r4\n    b L_open_cfw_runtime_am012_4d77a_003a\nL_open_cfw_runtime_am012_4d77a_0038:\n    movs r0, r6\nL_open_cfw_runtime_am012_4d77a_003a:\n    pop {r4, r5, r6, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM012_4D7B8_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am012_4d7b8(void)
{
    __asm__ volatile(
        "    push {r1, r2, r3, r4, r5, r6, r7, lr}\n    movs r6, r0\n    ldrh r0, [r6, #0x2a]\n    ubfx r0, r0, #0xc, #1\n    uxth r0, r0\n    cmp r0, #0\n    bne L_open_cfw_runtime_am012_4d7b8_00be\n    cmp r6, #0\n    bne L_open_cfw_runtime_am012_4d7b8_0040\n    ldr.w r0, [pc, #0x96c]\n    str r0, [sp, #8]\n    ldr.w r0, [pc, #0x96c]\n    str r0, [sp, #4]\n    ldr.w r0, [pc, #0x968]\n    str r0, [sp]\n    ldr.w r3, [pc, #0x778]\n    movs r2, #0x3e\n    ldr.w r1, [pc, #0x968]\n    movs r0, #3\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am012_4d25c\n    bl .\nL_open_cfw_runtime_am012_4d7b8_0036:\n    movs r0, #0\n    movs.w r1, #-1\n    str r0, [r1]\n    b L_open_cfw_runtime_am012_4d7b8_0036\nL_open_cfw_runtime_am012_4d7b8_0040:\n    movs r0, r6\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am012_addr_00440656\n    bl .\n    movs r0, r6\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am012_addr_0044dca2\n    bl .\n    movs r4, r0\n    movs r5, #0\n    movs r7, #0\n    cmp r4, #0\n    bne L_open_cfw_runtime_am012_4d7b8_006c\n    movs r0, r6\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am012_addr_0044dc0a\n    bl .\n    movs r5, r0\n    cmp r5, #0\n    beq L_open_cfw_runtime_am012_4d7b8_00be\n    ldr.w r0, [r5, #0x2c4]\n    cmp r0, r6\n    bne L_open_cfw_runtime_am012_4d7b8_006c\n    movs r7, #1\nL_open_cfw_runtime_am012_4d7b8_006c:\n    movs r0, r6\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am012_addr_0044df80\n    bl .\n    cmp r4, #0\n    beq L_open_cfw_runtime_am012_4d7b8_009c\n    ldrh r0, [r4, #0x2a]\n    ubfx r0, r0, #0xc, #1\n    uxth r0, r0\n    cmp r0, #0\n    bne L_open_cfw_runtime_am012_4d7b8_009c\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am012_addr_0044f2ca\n    bl .\n    movs r2, #0\n    movs r1, #0x2a\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am012_addr_00451670\n    bl .\n    movs r2, #0\n    movs r1, #0x2c\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am012_addr_00451670\n    bl .\nL_open_cfw_runtime_am012_4d7b8_009c:\n    uxtb r7, r7\n    cmp r7, #0\n    beq L_open_cfw_runtime_am012_4d7b8_00be\n    ldr.w r0, [pc, #0x700]\n    str r0, [sp]\n    ldr.w r3, [pc, #0x6f4]\n    movs r2, #0x56\n    ldr.w r1, [pc, #0x8e8]\n    movs r0, #2\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am012_4d25c\n    bl .\n    movs r0, #0\n    str.w r0, [r5, #0x2c4]\nL_open_cfw_runtime_am012_4d7b8_00be:\n    pop {r0, r1, r2, r4, r5, r6, r7, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM012_4D878_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am012_4d878(void)
{
    __asm__ volatile(
        "    push {r1, r2, r3, r4, r5, lr}\n    movs r4, r0\n    cmp r4, #0\n    bne L_open_cfw_runtime_am012_4d878_0034\n    ldr.w r0, [pc, #0x8b8]\n    str r0, [sp, #8]\n    ldr.w r0, [pc, #0x8b8]\n    str r0, [sp, #4]\n    ldr.w r0, [pc, #0x8b4]\n    str r0, [sp]\n    ldr.w r3, [pc, #0x8b4]\n    movs r2, #0x61\n    ldr.w r1, [pc, #0x8b4]\n    movs r0, #3\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am012_4d25c\n    bl .\nL_open_cfw_runtime_am012_4d878_002a:\n    movs r0, #0\n    movs.w r1, #-1\n    str r0, [r1]\n    b L_open_cfw_runtime_am012_4d878_002a\nL_open_cfw_runtime_am012_4d878_0034:\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am012_addr_00440656\n    bl .\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am012_addr_0044ddea\n    bl .\n    movs r5, r0\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am012_addr_0044e164\n    bl .\n    b L_open_cfw_runtime_am012_4d878_0054\nL_open_cfw_runtime_am012_4d878_004a:\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am012_addr_0044df80\n    bl .\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am012_addr_0044e164\n    bl .\nL_open_cfw_runtime_am012_4d878_0054:\n    cmp r0, #0\n    bne L_open_cfw_runtime_am012_4d878_004a\n    movs r3, #0\n    movs r2, #0\n    movs r1, #0\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am012_addr_0044e9ba\n    bl .\n    ldr r0, [r4, #8]\n    cmp r0, #0\n    beq L_open_cfw_runtime_am012_4d878_0076\n    movs r0, #0\n    ldr r1, [r4, #8]\n    str r0, [r1, #0x20]\n    movs r0, #0\n    ldr r1, [r4, #8]\n    str r0, [r1, #0x24]\nL_open_cfw_runtime_am012_4d878_0076:\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am012_addr_0044ddea\n    bl .\n    cmp r0, r5\n    bhs L_open_cfw_runtime_am012_4d878_0094\n    movs r2, #0\n    movs r1, #0x2a\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am012_addr_00451670\n    bl .\n    movs r2, #0\n    movs r1, #0x2c\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am012_addr_00451670\n    bl .\nL_open_cfw_runtime_am012_4d878_0094:\n    pop {r0, r1, r2, r4, r5, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM012_4D90E_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am012_4d90e(void)
{
    __asm__ volatile(
        "    push {r5, r6, r7, lr}\n    movs r1, r0\n    cmp r1, #0\n    bne L_open_cfw_runtime_am012_4d90e_0034\n    ldr.w r0, [pc, #0x824]\n    str r0, [sp, #8]\n    ldr.w r0, [pc, #0x820]\n    str r0, [sp, #4]\n    ldr.w r0, [pc, #0x820]\n    str r0, [sp]\n    ldr.w r3, [pc, #0x820]\n    movs r2, #0x8f\n    ldr.w r1, [pc, #0x820]\n    movs r0, #3\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am012_4d25c\n    bl .\nL_open_cfw_runtime_am012_4d90e_002a:\n    movs r0, #0\n    movs.w r1, #-1\n    str r0, [r1]\n    b L_open_cfw_runtime_am012_4d90e_002a\nL_open_cfw_runtime_am012_4d90e_0034:\n    addw r0, pc, #0x5dd\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am012_addr_00484014\n    bl .\n    pop {r0, r1, r2, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM012_4D94C_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am012_4d94c(void)
{
    __asm__ volatile(
        "    push {r1, r2, r3, r4, r5, r6, r7, lr}\n    movs r5, r0\n    movs r4, r1\n    cmp r5, #0\n    bne L_open_cfw_runtime_am012_4d94c_0036\n    ldr.w r0, [pc, #0x7e4]\n    str r0, [sp, #8]\n    ldr.w r0, [pc, #0x7e0]\n    str r0, [sp, #4]\n    ldr.w r0, [pc, #0x7e0]\n    str r0, [sp]\n    ldr.w r3, [pc, #0x7e8]\n    movs r2, #0x95\n    ldr.w r1, [pc, #0x7e0]\n    movs r0, #3\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am012_4d25c\n    bl .\nL_open_cfw_runtime_am012_4d94c_002c:\n    movs r0, #0\n    movs.w r1, #-1\n    str r0, [r1]\n    b L_open_cfw_runtime_am012_4d94c_002c\nL_open_cfw_runtime_am012_4d94c_0036:\n    cmp r4, #0\n    bne L_open_cfw_runtime_am012_4d94c_0066\n    ldr.w r0, [pc, #0x7b4]\n    str r0, [sp, #8]\n    ldr.w r0, [pc, #0x7c8]\n    str r0, [sp, #4]\n    ldr.w r0, [pc, #0x7b0]\n    str r0, [sp]\n    ldr.w r3, [pc, #0x7b8]\n    movs r2, #0x96\n    ldr.w r1, [pc, #0x7b0]\n    movs r0, #3\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am012_4d25c\n    bl .\nL_open_cfw_runtime_am012_4d94c_005c:\n    movs r0, #0\n    movs.w r1, #-1\n    str r0, [r1]\n    b L_open_cfw_runtime_am012_4d94c_005c\nL_open_cfw_runtime_am012_4d94c_0066:\n    ldr r0, [r5, #4]\n    cmp r0, #0\n    bne L_open_cfw_runtime_am012_4d94c_0084\n    ldr.w r0, [pc, #0x7a0]\n    str r0, [sp]\n    ldr.w r3, [pc, #0x794]\n    movs r2, #0x99\n    ldr.w r1, [pc, #0x788]\n    movs r0, #2\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am012_4d25c\n    bl .\n    b L_open_cfw_runtime_am012_4d94c_017c\nL_open_cfw_runtime_am012_4d94c_0084:\n    cmp r4, #0\n    bne L_open_cfw_runtime_am012_4d94c_00a0\n    ldr.w r0, [pc, #0x788]\n    str r0, [sp]\n    ldr.w r3, [pc, #0x778]\n    movs r2, #0x9e\n    ldr.w r1, [pc, #0x76c]\n    movs r0, #2\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am012_4d25c\n    bl .\n    b L_open_cfw_runtime_am012_4d94c_017c\nL_open_cfw_runtime_am012_4d94c_00a0:\n    ldr r0, [r5, #4]\n    cmp r4, r0\n    beq L_open_cfw_runtime_am012_4d94c_017c\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am012_addr_00440656\n    bl .\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am012_addr_0043e1fa\n    bl .\n    ldr r6, [r5, #4]\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am012_addr_0044de92\n    bl .\n    movs r7, r0\n    b L_open_cfw_runtime_am012_4d94c_00d2\nL_open_cfw_runtime_am012_4d94c_00be:\n    ldr r0, [r6, #8]\n    ldr r0, [r0]\n    add.w r0, r0, r7, lsl #2\n    ldr r0, [r0, #4]\n    ldr r1, [r6, #8]\n    ldr r1, [r1]\n    str.w r0, [r1, r7, lsl #2]\n    adds r7, r7, #1\nL_open_cfw_runtime_am012_4d94c_00d2:\n    movs r0, r6\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am012_addr_0044ddea\n    bl .\n    subs r0, r0, #2\n    cmp r0, r7\n    bge L_open_cfw_runtime_am012_4d94c_00be\n    ldr r0, [r6, #8]\n    ldrh r0, [r0, #0x30]\n    subs r0, r0, #1\n    ldr r1, [r6, #8]\n    strh r0, [r1, #0x30]\n    ldr r0, [r6, #8]\n    ldrh r0, [r0, #0x30]\n    cmp r0, #0\n    beq L_open_cfw_runtime_am012_4d94c_0104\n    ldr r0, [r6, #8]\n    ldrh r1, [r0, #0x30]\n    lsls r1, r1, #2\n    ldr r0, [r6, #8]\n    ldr r0, [r0]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am012_addr_0044f76a\n    bl .\n    ldr r1, [r6, #8]\n    str r0, [r1]\n    b L_open_cfw_runtime_am012_4d94c_0112\nL_open_cfw_runtime_am012_4d94c_0104:\n    ldr r0, [r6, #8]\n    ldr r0, [r0]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am012_addr_0044f758\n    bl .\n    movs r0, #0\n    ldr r1, [r6, #8]\n    str r0, [r1]\nL_open_cfw_runtime_am012_4d94c_0112:\n    ldr r0, [r4, #8]\n    ldrh r0, [r0, #0x30]\n    adds r0, r0, #1\n    ldr r1, [r4, #8]\n    strh r0, [r1, #0x30]\n    ldr r0, [r4, #8]\n    ldrh r1, [r0, #0x30]\n    lsls r1, r1, #2\n    ldr r0, [r4, #8]\n    ldr r0, [r0]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am012_addr_0044f76a\n    bl .\n    ldr r1, [r4, #8]\n    str r0, [r1]\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am012_addr_0044ddea\n    bl .\n    ldr r1, [r4, #8]\n    ldr r1, [r1]\n    add.w r0, r1, r0, lsl #2\n    str r5, [r0, #-0x4]\n    str r4, [r5, #4]\n    movs r0, r6\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am012_addr_0044f2ca\n    bl .\n    movs r2, r5\n    movs r1, #0x2a\n    movs r0, r6\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am012_addr_00451670\n    bl .\n    movs r2, #0\n    movs r1, #0x2c\n    movs r0, r6\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am012_addr_00451670\n    bl .\n    movs r2, r5\n    movs r1, #0x2a\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am012_addr_00451670\n    bl .\n    movs r2, #0\n    movs r1, #0x2b\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am012_addr_00451670\n    bl .\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am012_addr_0043f648\n    bl .\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am012_addr_00440656\n    bl .\nL_open_cfw_runtime_am012_4d94c_017c:\n    pop {r0, r1, r2, r4, r5, r6, r7, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM012_4DACA_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am012_4daca(void)
{
    __asm__ volatile(
        "    push {r1, r2, r3, r4, r5, r6, r7, lr}\n    movs r4, r0\n    movs r6, r1\n    cmp r4, #0\n    bne L_open_cfw_runtime_am012_4daca_0036\n    ldr.w r0, [pc, #0x664]\n    str r0, [sp, #8]\n    ldr.w r0, [pc, #0x664]\n    str r0, [sp, #4]\n    ldr.w r0, [pc, #0x660]\n    str r0, [sp]\n    ldr.w r3, [pc, #0x6e0]\n    movs r2, #0xd2\n    ldr.w r1, [pc, #0x660]\n    movs r0, #3\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am012_4d25c\n    bl .\nL_open_cfw_runtime_am012_4daca_002c:\n    movs r0, #0\n    movs.w r1, #-1\n    str r0, [r1]\n    b L_open_cfw_runtime_am012_4daca_002c\nL_open_cfw_runtime_am012_4daca_0036:\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am012_addr_0044dca2\n    bl .\n    movs r5, r0\n    cmp r5, #0\n    bne L_open_cfw_runtime_am012_4daca_005a\n    ldr.w r0, [pc, #0x6bc]\n    str r0, [sp]\n    ldr.w r3, [pc, #0x6b4]\n    movs r2, #0xd7\n    ldr.w r1, [pc, #0x634]\n    movs r0, #2\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am012_4d25c\n    bl .\n    b L_open_cfw_runtime_am012_4daca_00f8\nL_open_cfw_runtime_am012_4daca_005a:\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am012_addr_0044ddea\n    bl .\n    movs r7, r0\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am012_addr_0044de92\n    bl .\n    cmp r0, #0\n    bpl L_open_cfw_runtime_am012_4daca_0092\n    ldr.w r0, [pc, #0x698]\n    str r0, [sp, #4]\n    ldr.w r0, [pc, #0x694]\n    str r0, [sp]\n    ldr.w r3, [pc, #0x684]\n    movs r2, #0xde\n    ldr.w r1, [pc, #0x604]\n    movs r0, #3\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am012_4d25c\n    bl .\nL_open_cfw_runtime_am012_4daca_0088:\n    movs r0, #0\n    movs.w r1, #-1\n    str r0, [r1]\n    b L_open_cfw_runtime_am012_4daca_0088\nL_open_cfw_runtime_am012_4daca_0092:\n    cmp r6, #0\n    bpl L_open_cfw_runtime_am012_4daca_0098\n    adds r6, r7, r6\nL_open_cfw_runtime_am012_4daca_0098:\n    cmp r6, #0\n    bmi L_open_cfw_runtime_am012_4daca_00a4\n    cmp r6, r7\n    bge L_open_cfw_runtime_am012_4daca_00a4\n    cmp r6, r0\n    bne L_open_cfw_runtime_am012_4daca_00a6\nL_open_cfw_runtime_am012_4daca_00a4:\n    b L_open_cfw_runtime_am012_4daca_00f8\nL_open_cfw_runtime_am012_4daca_00a6:\n    movs r1, r0\n    cmp r6, r0\n    bge L_open_cfw_runtime_am012_4daca_00dc\nL_open_cfw_runtime_am012_4daca_00ac:\n    cmp r6, r1\n    bge L_open_cfw_runtime_am012_4daca_00e0\n    ldr r0, [r5, #8]\n    ldr r0, [r0]\n    add.w r0, r0, r1, lsl #2\n    ldr r0, [r0, #-0x4]\n    ldr r2, [r5, #8]\n    ldr r2, [r2]\n    str.w r0, [r2, r1, lsl #2]\n    subs r1, r1, #1\n    b L_open_cfw_runtime_am012_4daca_00ac\nL_open_cfw_runtime_am012_4daca_00c8:\n    ldr r0, [r5, #8]\n    ldr r0, [r0]\n    add.w r0, r0, r1, lsl #2\n    ldr r0, [r0, #4]\n    ldr r2, [r5, #8]\n    ldr r2, [r2]\n    str.w r0, [r2, r1, lsl #2]\n    adds r1, r1, #1\nL_open_cfw_runtime_am012_4daca_00dc:\n    cmp r1, r6\n    blt L_open_cfw_runtime_am012_4daca_00c8\nL_open_cfw_runtime_am012_4daca_00e0:\n    ldr r0, [r5, #8]\n    ldr r0, [r0]\n    str.w r4, [r0, r6, lsl #2]\n    movs r2, #0\n    movs r1, #0x2a\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am012_addr_00451670\n    bl .\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am012_addr_00440656\n    bl .\nL_open_cfw_runtime_am012_4daca_00f8:\n    pop {r0, r1, r2, r4, r5, r6, r7, pc}\n"
    );
}
#endif
