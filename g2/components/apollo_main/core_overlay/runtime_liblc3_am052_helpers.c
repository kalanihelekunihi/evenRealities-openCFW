/*
 * SPDX-License-Identifier: MIT
 *
 * Source-owned exact helpers from the AM-052 retained island.
 */

#if defined(OPEN_CFW_AM052_B3BD2_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am052_b3bd2(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    movs r2, r1\n    ldrb r0, [r0, #3]\n    cmp r0, #0\n    bne L_open_cfw_runtime_am052_b3bd2_0018\n    ldr r0, [r2]\n    cmp r0, #0\n    beq L_open_cfw_runtime_am052_b3bd2_0018\n    movs r1, #0\n    ldr r0, [r2]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am052_addr_0047b4ce\n    bl .\nL_open_cfw_runtime_am052_b3bd2_0018:\n    pop {r0, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM052_B3C02_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am052_b3c02(void)
{
    __asm__ volatile(
        "    push {r4, r5, r6, lr}\n    movs r1, #0x80\n    movs r2, #0\n    ldr r4, [pc, #0x80]\n    movs r5, r4\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am052_addr_0043c0e4\n    bl .\n    movs r5, #0\n    b L_open_cfw_runtime_am052_b3c02_0060\nL_open_cfw_runtime_am052_b3c02_0014:\n    movs r0, #3\n    movs r1, r5\n    uxtb r1, r1\n    add r1, r4\n    strb.w r0, [r1, #0x57]\n    movs r0, #0\n    movs r1, r5\n    uxtb r1, r1\n    add r1, r4\n    strb.w r0, [r1, #0x59]\n    movs r0, #0\n    movs r1, r5\n    uxtb r1, r1\n    add r1, r4\n    strb.w r0, [r1, #0x5b]\n    movs r0, #0\n    movs r1, r5\n    uxtb r1, r1\n    add r1, r4\n    strb.w r0, [r1, #0x6a]\n    movs r1, #6\n    movs r2, #0\n    movs r3, r5\n    uxtb r3, r3\n    movs r0, #6\n    muls r3, r0, r3\n    add.w r0, r4, r3\n    adds.w r6, r0, #0x5e\n    movs r0, r6\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am052_addr_0043c0e4\n    bl .\n    adds r5, r5, #1\nL_open_cfw_runtime_am052_b3c02_0060:\n    movs r0, r5\n    uxtb r0, r0\n    cmp r0, #2\n    blt L_open_cfw_runtime_am052_b3c02_0014\n    movs r0, #0xff\n    strb.w r0, [r4, #0x5d]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am052_addr_004b32d4\n    bl .\n    movs r0, #0\n    strb.w r0, [r4, #0x74]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am052_addr_00479418\n    bl .\n    ldr.w r0, [pc, #0xa24]\n    ldr.w r1, [pc, #0xa68]\n    str r0, [r1]\n    pop {r4, r5, r6, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM052_B4240_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am052_b4240(void)
{
    __asm__ volatile(
        "    push {r3, r4, r5, r6, r7, lr}\n    ldr r4, [sp, #0x18]\n    ldr r5, [sp, #0x1c]\n    ldr.w r6, [pc, #0x4ac]\n    movs r7, r0\n    uxtb r7, r7\n    lsls r7, r7, #4\n    add r7, r6\n    mov ip, r1\n    uxtb.w ip, ip\n    str.w r3, [r7, ip, lsl #2]\n    movs r3, r0\n    uxtb r3, r3\n    add.w r3, r6, r3, lsl #3\n    movs r7, r1\n    uxtb r7, r7\n    add.w r3, r3, r7, lsl #1\n    strh r2, [r3, #0x20]\n    movs r3, r0\n    uxtb r3, r3\n    add.w r3, r6, r3, lsl #3\n    movs r7, r1\n    uxtb r7, r7\n    add.w r3, r3, r7, lsl #1\n    strh r4, [r3, #0x30]\n    movs r3, r0\n    uxtb r3, r3\n    add.w r3, r6, r3, lsl #1\n    strh.w r5, [r3, #0x50]\n    movs r3, r0\n    uxtb r3, r3\n    add.w r3, r6, r3, lsl #3\n    movs r4, r1\n    uxtb r4, r4\n    add.w r3, r3, r4, lsl #1\n    movs r4, #0\n    strh.w r4, [r3, #0x40]\n    movs r3, r0\n    uxtb r3, r3\n    add r3, r6\n    ldrb.w r3, [r3, #0x57]\n    cmp r3, #3\n    beq L_open_cfw_runtime_am052_b4240_0098\n    movs r3, r1\n    uxtb r3, r3\n    lsrs r3, r3, #1\n    ldrb.w r4, [r6, #0x5d]\n    cmp r3, r4\n    bne L_open_cfw_runtime_am052_b4240_0098\n    movs r3, r2\n    uxth r3, r3\n    cmp r3, #0xfc\n    bge L_open_cfw_runtime_am052_b4240_0098\n    uxth r5, r5\n    uxth r2, r2\n    cmp r5, r2\n    blo L_open_cfw_runtime_am052_b4240_0098\n    uxtb r1, r1\n    uxtb r0, r0\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am052_addr_004b3416\n    bl .\n    b L_open_cfw_runtime_am052_b4240_00a2\nL_open_cfw_runtime_am052_b4240_0098:\n    movs r1, #0\n    uxtb r0, r0\n    add r0, r6\n    strb.w r1, [r0, #0x55]\nL_open_cfw_runtime_am052_b4240_00a2:\n    pop {r0, r4, r5, r6, r7, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM052_B42F0_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am052_b42f0(void)
{
    __asm__ volatile(
        "    push.w {r3, r4, r5, r6, r7, r8, sb, lr}\n    mov r8, r0\n    movs r7, r1\n    movs r6, r2\n    movs r4, r3\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am052_addr_0046efec\n    bl .\n    cmp r0, #0\n    bne L_open_cfw_runtime_am052_b42f0_0104\n    movs r1, r7\n    mov r0, r8\n    uxtb r0, r0\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am052_addr_004b32e2\n    bl .\n    movs r5, r0\n    movs r0, #1\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am052_addr_004bacf0\n    bl .\n    ldr.w r1, [pc, #0x400]\n    ldr r1, [r1]\n    ldrb r1, [r1]\n    uxtb r5, r5\n    cmp r5, #0\n    beq L_open_cfw_runtime_am052_b42f0_003c\n    uxtb r0, r0\n    uxtb r1, r1\n    cmp r0, r1\n    bhs L_open_cfw_runtime_am052_b42f0_00e0\nL_open_cfw_runtime_am052_b42f0_003c:\n    movs.w sb, #0\n    ldr r5, [sp, #0x24]\n    b L_open_cfw_runtime_am052_b42f0_00c4\nL_open_cfw_runtime_am052_b42f0_0044:\n    movs r0, r5\n    uxtb r0, r0\n    cmp r0, #0\n    beq L_open_cfw_runtime_am052_b42f0_009e\n    mov r0, sb\n    uxtb r0, r0\n    ldrh.w r2, [r6, r0, lsl #1]\n    mov r0, sb\n    uxtb r0, r0\n    ldrh.w r1, [r6, r0, lsl #1]\n    mov r0, sb\n    uxtb r0, r0\n    ldrb r0, [r7, r0]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am052_addr_004b3292\n    bl .\n    ldr.w r1, [pc, #0x39c]\n    mov r0, sb\n    uxtb r0, r0\n    ldrb r2, [r7, r0]\n    movs r0, #6\n    muls r2, r0, r2\n    add.w r0, r1, r2\n    adds.w r3, r0, #0x5e\n    mov r0, sb\n    uxtb r0, r0\n    ldrb r0, [r7, r0]\n    add r0, r1\n    ldrb.w r2, [r0, #0x6a]\n    mov r0, sb\n    uxtb r0, r0\n    ldrb r0, [r7, r0]\n    add r0, r1\n    ldrb.w r1, [r0, #0x59]\n    mov r0, sb\n    uxtb r0, r0\n    ldrb r0, [r7, r0]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am052_addr_004b3166\n    bl .\nL_open_cfw_runtime_am052_b42f0_009e:\n    ldr.w r1, [pc, #0x364]\n    mov r0, sb\n    uxtb r0, r0\n    ldrb r0, [r7, r0]\n    add r0, r1\n    ldrb.w r0, [r0, #0x55]\n    cmp r0, #0\n    bne L_open_cfw_runtime_am052_b42f0_00c0\n    ldrb.w r1, [r1, #0x5d]\n    mov r0, sb\n    uxtb r0, r0\n    ldrb r0, [r7, r0]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am052_addr_004b3514\n    bl .\nL_open_cfw_runtime_am052_b42f0_00c0:\n    adds.w sb, sb, #1\nL_open_cfw_runtime_am052_b42f0_00c4:\n    mov r0, sb\n    mov r1, r8\n    uxtb r0, r0\n    uxtb r1, r1\n    cmp r0, r1\n    blo L_open_cfw_runtime_am052_b42f0_0044\n    ldr r3, [sp, #0x20]\n    movs r2, r4\n    movs r1, r7\n    mov r0, r8\n    uxtb r0, r0\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am052_addr_004b31ea\n    bl .\n    b L_open_cfw_runtime_am052_b42f0_0104\nL_open_cfw_runtime_am052_b42f0_00e0:\n    movs r0, #0\n    b L_open_cfw_runtime_am052_b42f0_00f8\nL_open_cfw_runtime_am052_b42f0_00e4:\n    ldr.w r1, [pc, #0x31c]\n    movs r2, r0\n    uxtb r2, r2\n    ldrb r2, [r7, r2]\n    add r1, r2\n    movs r2, #3\n    strb.w r2, [r1, #0x57]\n    adds r0, r0, #1\nL_open_cfw_runtime_am052_b42f0_00f8:\n    movs r1, r0\n    mov r2, r8\n    uxtb r1, r1\n    uxtb r2, r2\n    cmp r1, r2\n    blo L_open_cfw_runtime_am052_b42f0_00e4\nL_open_cfw_runtime_am052_b42f0_0104:\n    pop.w {r0, r4, r5, r6, r7, r8, sb, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM052_B43FC_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am052_b43fc(void)
{
    __asm__ volatile(
        "    push {r3, r4, r5, lr}\n    movs r4, r0\n    movs r5, r1\n    movs r0, r4\n    uxtb r0, r0\n    cmp r0, #0\n    bne L_open_cfw_runtime_am052_b43fc_002c\n    movs r0, #0\nL_open_cfw_runtime_am052_b43fc_0010:\n    movs r1, r0\n    uxtb r1, r1\n    cmp r1, #2\n    bge L_open_cfw_runtime_am052_b43fc_0050\n    movs r1, #3\n    ldr.w r2, [pc, #0x2dc]\n    movs r3, r0\n    uxtb r3, r3\n    add r2, r3\n    strb.w r1, [r2, #0x57]\n    adds r0, r0, #1\n    b L_open_cfw_runtime_am052_b43fc_0010\nL_open_cfw_runtime_am052_b43fc_002c:\n    movs r0, #0\n    b L_open_cfw_runtime_am052_b43fc_0044\nL_open_cfw_runtime_am052_b43fc_0030:\n    ldr.w r1, [pc, #0x2c4]\n    movs r2, r0\n    uxtb r2, r2\n    ldrb r2, [r5, r2]\n    add r1, r2\n    movs r2, #3\n    strb.w r2, [r1, #0x57]\n    adds r0, r0, #1\nL_open_cfw_runtime_am052_b43fc_0044:\n    movs r1, r0\n    movs r2, r4\n    uxtb r1, r1\n    uxtb r2, r2\n    cmp r1, r2\n    blo L_open_cfw_runtime_am052_b43fc_0030\nL_open_cfw_runtime_am052_b43fc_0050:\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am052_b46a8\n    bl .\n    cmp r0, #0\n    bne L_open_cfw_runtime_am052_b43fc_0062\n    movs r0, #0xff\n    ldr.w r1, [pc, #0x29c]\n    strb.w r0, [r1, #0x5d]\nL_open_cfw_runtime_am052_b43fc_0062:\n    movs r1, r5\n    movs r0, r4\n    uxtb r0, r0\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am052_addr_004b3250\n    bl .\n    pop {r0, r4, r5, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM052_B446A_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am052_b446a(void)
{
    __asm__ volatile(
        "    push.w {r2, r3, r4, r5, r6, r7, r8, sb, sl, lr}\n    movs r7, r0\n    movs r6, r1\n    movs r4, r2\n    movs r5, r3\n    ldr.w sl, [sp, #0x30]\n    ldr.w r8, [pc, #0x278]\n    ldrb.w sb, [r8, #0x5d]\n    mov r0, sl\n    uxtb r0, r0\n    cmp r0, #2\n    bne L_open_cfw_runtime_am052_b446a_0044\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am052_addr_0047a600\n    bl .\n    cmp r0, #0\n    bne L_open_cfw_runtime_am052_b446a_0036\n    movs r0, #1\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am052_b467c\n    bl .\n    movs r0, #1\n    strb.w r0, [r8, #0x5d]\n    b L_open_cfw_runtime_am052_b446a_004e\nL_open_cfw_runtime_am052_b446a_0036:\n    movs r0, #0\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am052_b467c\n    bl .\n    movs r0, #0\n    strb.w r0, [r8, #0x5d]\n    b L_open_cfw_runtime_am052_b446a_004e\nL_open_cfw_runtime_am052_b446a_0044:\n    movs r0, #1\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am052_b467c\n    bl .\n    strb.w sl, [r8, #0x5d]\nL_open_cfw_runtime_am052_b446a_004e:\n    ldrb.w r0, [r8, #0x5d]\n    uxtb.w sb, sb\n    cmp sb, r0\n    beq L_open_cfw_runtime_am052_b446a_007e\n    movs.w sb, #0\n    b L_open_cfw_runtime_am052_b446a_0072\nL_open_cfw_runtime_am052_b446a_0060:\n    ldrb.w r1, [r8, #0x5d]\n    mov r0, sb\n    uxtb r0, r0\n    ldrb r0, [r6, r0]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am052_addr_004b33d2\n    bl .\n    adds.w sb, sb, #1\nL_open_cfw_runtime_am052_b446a_0072:\n    mov r0, sb\n    movs r1, r7\n    uxtb r0, r0\n    uxtb r1, r1\n    cmp r0, r1\n    blo L_open_cfw_runtime_am052_b446a_0060\nL_open_cfw_runtime_am052_b446a_007e:\n    movs r3, r5\n    movs r2, r4\n    movs r0, #1\n    str r0, [sp, #4]\n    ldr r0, [sp, #0x28]\n    str r0, [sp]\n    movs r1, r6\n    movs r0, r7\n    uxtb r0, r0\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am052_b42f0\n    bl .\n    pop.w {r0, r1, r4, r5, r6, r7, r8, sb, sl, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM052_B4510_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am052_b4510(void)
{
    __asm__ volatile(
        "    push {r0, r2, r3, r4, lr}\n    sub sp, #0xc\n    movs r0, r1\n    uxtb r0, r0\n    cmp r0, #1\n    beq L_open_cfw_runtime_am052_b4510_0014\n    movs r0, r1\n    uxtb r0, r0\n    cmp r0, #4\n    bne L_open_cfw_runtime_am052_b4510_0016\nL_open_cfw_runtime_am052_b4510_0014:\n    b L_open_cfw_runtime_am052_b4510_0096\nL_open_cfw_runtime_am052_b4510_0016:\n    ldr r4, [pc, #0x1cc]\n    ldrb.w r0, [sp, #0xc]\n    add r0, r4\n    ldrb.w r0, [r0, #0x59]\n    movs r2, r1\n    uxtb r2, r2\n    cmp r0, r2\n    beq L_open_cfw_runtime_am052_b4510_0096\n    ldrb.w r0, [sp, #0xc]\n    add r0, r4\n    strb.w r1, [r0, #0x59]\n    ldrb.w r0, [r4, #0x5d]\n    cmp r0, #0xff\n    beq L_open_cfw_runtime_am052_b4510_0096\n    ldrb.w r0, [sp, #0xc]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am052_addr_004b334c\n    bl .\n    ldrb.w r0, [sp, #0xc]\n    add r0, r4\n    ldrb.w r0, [r0, #0x57]\n    cmp r0, #3\n    bne L_open_cfw_runtime_am052_b4510_0076\n    movs r0, #0\n    ldrb.w r1, [sp, #0xc]\n    add r1, r4\n    strb.w r0, [r1, #0x57]\n    ldrb.w r0, [sp, #0x24]\n    str r0, [sp, #4]\n    add r0, sp, #0x20\n    str r0, [sp]\n    add r3, sp, #0x14\n    add r2, sp, #0x10\n    add r1, sp, #0xc\n    movs r0, #1\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am052_b42f0\n    bl .\n    b L_open_cfw_runtime_am052_b4510_0096\nL_open_cfw_runtime_am052_b4510_0076:\n    movs r0, #1\n    ldrb.w r1, [sp, #0xc]\n    add r1, r4\n    strb.w r0, [r1, #0x5b]\n    movs r0, #3\n    ldrb.w r1, [sp, #0xc]\n    add r1, r4\n    strb.w r0, [r1, #0x57]\n    add r1, sp, #0xc\n    movs r0, #1\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am052_addr_004b3250\n    bl .\nL_open_cfw_runtime_am052_b4510_0096:\n    add sp, #0x18\n    pop {r4, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM052_B45B0_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am052_b45b0(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    movs r1, #0\n    ldrb r2, [r0, #2]\n    cmp r2, #0x3f\n    beq L_open_cfw_runtime_am052_b45b0_002a\n    ldrh r2, [r0]\n    cmp r2, #0\n    beq L_open_cfw_runtime_am052_b45b0_002a\n    ldrh r2, [r0]\n    cmp r2, #0\n    beq L_open_cfw_runtime_am052_b45b0_002a\n    ldrh r2, [r0]\n    cmp r2, #4\n    bge L_open_cfw_runtime_am052_b45b0_002a\n    ldr r2, [pc, #0x120]\n    ldrh r3, [r0]\n    movs r1, #0x30\n    muls r3, r1, r3\n    add.w r1, r2, r3\n    subs r1, #0x30\nL_open_cfw_runtime_am052_b45b0_002a:\n    ldrb r2, [r0, #2]\n    cmp r2, #0x27\n    beq L_open_cfw_runtime_am052_b45b0_005e\n    cmp r2, #0x28\n    beq L_open_cfw_runtime_am052_b45b0_0068\n    cmp r2, #0x2a\n    beq L_open_cfw_runtime_am052_b45b0_0072\n    cmp r2, #0x2b\n    beq L_open_cfw_runtime_am052_b45b0_007c\n    cmp r2, #0x2c\n    beq L_open_cfw_runtime_am052_b45b0_0086\n    cmp r2, #0x2d\n    beq L_open_cfw_runtime_am052_b45b0_0090\n    cmp r2, #0x2f\n    beq L_open_cfw_runtime_am052_b45b0_0092\n    cmp r2, #0x30\n    beq L_open_cfw_runtime_am052_b45b0_00a6\n    cmp r2, #0x31\n    beq L_open_cfw_runtime_am052_b45b0_009c\n    cmp r2, #0x3a\n    beq L_open_cfw_runtime_am052_b45b0_00b6\n    cmp r2, #0x3b\n    beq L_open_cfw_runtime_am052_b45b0_00c0\n    cmp r2, #0x3f\n    beq L_open_cfw_runtime_am052_b45b0_00b0\n    b L_open_cfw_runtime_am052_b45b0_00ca\nL_open_cfw_runtime_am052_b45b0_005e:\n    cmp r1, #0\n    beq L_open_cfw_runtime_am052_b45b0_0066\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am052_addr_004b3944\n    bl .\nL_open_cfw_runtime_am052_b45b0_0066:\n    b L_open_cfw_runtime_am052_b45b0_00ca\nL_open_cfw_runtime_am052_b45b0_0068:\n    cmp r1, #0\n    beq L_open_cfw_runtime_am052_b45b0_0070\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am052_addr_004b39de\n    bl .\nL_open_cfw_runtime_am052_b45b0_0070:\n    b L_open_cfw_runtime_am052_b45b0_00ca\nL_open_cfw_runtime_am052_b45b0_0072:\n    cmp r1, #0\n    beq L_open_cfw_runtime_am052_b45b0_007a\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am052_addr_004b3aa8\n    bl .\nL_open_cfw_runtime_am052_b45b0_007a:\n    b L_open_cfw_runtime_am052_b45b0_00ca\nL_open_cfw_runtime_am052_b45b0_007c:\n    cmp r1, #0\n    beq L_open_cfw_runtime_am052_b45b0_0084\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am052_addr_004b3aea\n    bl .\nL_open_cfw_runtime_am052_b45b0_0084:\n    b L_open_cfw_runtime_am052_b45b0_00ca\nL_open_cfw_runtime_am052_b45b0_0086:\n    cmp r1, #0\n    beq L_open_cfw_runtime_am052_b45b0_008e\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am052_addr_004b3aec\n    bl .\nL_open_cfw_runtime_am052_b45b0_008e:\n    b L_open_cfw_runtime_am052_b45b0_00ca\nL_open_cfw_runtime_am052_b45b0_0090:\n    b L_open_cfw_runtime_am052_b45b0_00ca\nL_open_cfw_runtime_am052_b45b0_0092:\n    cmp r1, #0\n    beq L_open_cfw_runtime_am052_b45b0_009a\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am052_addr_004b3a86\n    bl .\nL_open_cfw_runtime_am052_b45b0_009a:\n    b L_open_cfw_runtime_am052_b45b0_00ca\nL_open_cfw_runtime_am052_b45b0_009c:\n    cmp r1, #0\n    beq L_open_cfw_runtime_am052_b45b0_00a4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am052_addr_004b39f6\n    bl .\nL_open_cfw_runtime_am052_b45b0_00a4:\n    b L_open_cfw_runtime_am052_b45b0_00ca\nL_open_cfw_runtime_am052_b45b0_00a6:\n    cmp r1, #0\n    beq L_open_cfw_runtime_am052_b45b0_00ae\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am052_addr_004b3b4c\n    bl .\nL_open_cfw_runtime_am052_b45b0_00ae:\n    b L_open_cfw_runtime_am052_b45b0_00ca\nL_open_cfw_runtime_am052_b45b0_00b0:\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am052_addr_004b3ba0\n    bl .\n    b L_open_cfw_runtime_am052_b45b0_00ca\nL_open_cfw_runtime_am052_b45b0_00b6:\n    cmp r1, #0\n    beq L_open_cfw_runtime_am052_b45b0_00be\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am052_addr_004b3bb4\n    bl .\nL_open_cfw_runtime_am052_b45b0_00be:\n    b L_open_cfw_runtime_am052_b45b0_00ca\nL_open_cfw_runtime_am052_b45b0_00c0:\n    cmp r1, #0\n    beq L_open_cfw_runtime_am052_b45b0_00c8\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am052_b3bd2\n    bl .\nL_open_cfw_runtime_am052_b45b0_00c8:\n    b L_open_cfw_runtime_am052_b45b0_00ca\nL_open_cfw_runtime_am052_b45b0_00ca:\n    pop {r0, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM052_B467C_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am052_b467c(void)
{
    __asm__ volatile(
        "    ldr r1, [pc, #0x74]\n    strb.w r0, [r1, #0x54]\n    bx lr\n"
    );
}
#endif

#if defined(OPEN_CFW_AM052_B4684_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am052_b4684(void)
{
    __asm__ volatile(
        "    push {r4, lr}\n    movs r4, r0\n    movs r0, r4\n    uxtb r0, r0\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am052_addr_004b71b2\n    bl .\n    cmp r0, #0\n    bne L_open_cfw_runtime_am052_b4684_001e\n    ldr r0, [pc, #0x84]\n    ldr r0, [r0]\n    ldrb r1, [r0]\n    movs r0, r4\n    uxtb r0, r0\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am052_addr_0052bb00\n    bl .\nL_open_cfw_runtime_am052_b4684_001e:\n    pop {r4, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM052_B46A8_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am052_b46a8(void)
{
    __asm__ volatile(
        "    movs r0, #0\n    b L_open_cfw_runtime_am052_b46a8_0006\nL_open_cfw_runtime_am052_b46a8_0004:\n    adds r0, r0, #1\nL_open_cfw_runtime_am052_b46a8_0006:\n    movs r1, r0\n    uxtb r1, r1\n    cmp r1, #2\n    bge L_open_cfw_runtime_am052_b46a8_0022\n    ldr r1, [pc, #0x3c]\n    movs r2, r0\n    uxtb r2, r2\n    add r1, r2\n    ldrb.w r1, [r1, #0x57]\n    cmp r1, #3\n    bge L_open_cfw_runtime_am052_b46a8_0004\n    movs r0, #1\n    b L_open_cfw_runtime_am052_b46a8_0024\nL_open_cfw_runtime_am052_b46a8_0022:\n    movs r0, #0\nL_open_cfw_runtime_am052_b46a8_0024:\n    bx lr\n"
    );
}
#endif

#if defined(OPEN_CFW_AM052_B46CE_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am052_b46ce(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am052_addr_0047acf8\n    bl .\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am052_addr_004d28b0\n    bl .\n    ldr r0, [pc, #0x18]\n    movs r1, #0\n    strb.w r1, [r0, #0x74]\n    movs r1, #0\n    str r1, [r0, #0x70]\n    movs r1, #0\n    strb.w r1, [r0, #0x6c]\n    pop {r0, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM052_B4720_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am052_b4720(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am052_addr_0047b4d4\n    bl .\n    pop {r0, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM052_B4728_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am052_b4728(void)
{
    __asm__ volatile(
        "    push {r2, r3}\n    push {r4, r5, lr}\n    sub sp, #0xc\n    mov r2, r1\n    add r1, sp, #0x18\n    str r1, [sp, #8]\n    mov r4, r0\n    movs r5, #0\n    str r4, [sp, #4]\n    str r5, [sp]\n    add r3, sp, #8\n    add r1, sp, #4\n    ldr r0, [pc, #0x20]\n    add r0, pc\n    adds r0, #0x1e\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am052_addr_00481836\n    bl .\n    ldr r2, [sp, #4]\n    strb r5, [r2]\n    cmp r0, #0\n    itee mi\n    movmi r4, r0\n    ldrpl r0, [sp, #4]\n    subpl r4, r0, r4\n    mov r0, r4\n    add sp, #0xc\n    pop {r4, r5}\n    ldr pc, [sp], #0xc\n"
    );
}
#endif

#if defined(OPEN_CFW_AM052_B4768_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am052_b4768(void)
{
    __asm__ volatile(
        "    movs r1, r0\n    sxth r1, r1\n    cmp r1, #0\n    bmi L_open_cfw_runtime_am052_b4768_001c\n    movs r2, #1\n    ands r1, r0, #0x1f\n    lsls r2, r1\n    ldr.w r1, [pc, #0x5b4]\n    sxth r0, r0\n    lsrs r0, r0, #5\n    str.w r2, [r1, r0, lsl #2]\nL_open_cfw_runtime_am052_b4768_001c:\n    bx lr\n"
    );
}
#endif

#if defined(OPEN_CFW_AM052_B4786_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am052_b4786(void)
{
    __asm__ volatile(
        "    movs r2, r0\n    sxth r2, r2\n    cmp r2, #0\n    bmi L_open_cfw_runtime_am052_b4786_0014\n    lsls r1, r1, #4\n    ldr.w r2, [pc, #0x5a0]\n    sxth r0, r0\n    strb r1, [r2, r0]\n    b L_open_cfw_runtime_am052_b4786_0026\nL_open_cfw_runtime_am052_b4786_0014:\n    lsls r1, r1, #4\n    ldr.w r2, [pc, #0x598]\n    sxth r0, r0\n    ands r0, r0, #0xf\n    add r0, r2\n    strb r1, [r0, #-0x4]\nL_open_cfw_runtime_am052_b4786_0026:\n    bx lr\n"
    );
}
#endif

#if defined(OPEN_CFW_AM052_B47CC_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am052_b47cc(void)
{
    __asm__ volatile(
        "    push {r3, r4, r5, lr}\n    movs r2, r1\n    movs r1, #3\n    b L_open_cfw_runtime_am052_b47cc_000a\nL_open_cfw_runtime_am052_b47cc_0008:\n    subs r1, r1, #1\nL_open_cfw_runtime_am052_b47cc_000a:\n    cmp r1, #0\n    bmi L_open_cfw_runtime_am052_b47cc_0030\n    lsls r4, r1, #3\n    movs r3, r0\n    lsrs r3, r4\n    lsls r5, r1, #3\n    movs r4, r2\n    lsrs r4, r5\n    uxtb r3, r3\n    uxtb r4, r4\n    cmp r3, r4\n    bhs L_open_cfw_runtime_am052_b47cc_0008\n    movs r1, r0\n    ldr.w r0, [pc, #0x550]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am052_addr_004733ee\n    bl .\n    movs r0, #1\n    b L_open_cfw_runtime_am052_b47cc_003c\nL_open_cfw_runtime_am052_b47cc_0030:\n    movs r1, r0\n    ldr.w r0, [pc, #0x548]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am052_addr_004733ee\n    bl .\n    movs r0, #0\nL_open_cfw_runtime_am052_b47cc_003c:\n    pop {r1, r4, r5, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM052_B480A_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am052_b480a(void)
{
    __asm__ volatile(
        "    push {r3, r4, r5, r6, r7, lr}\n    movs r5, r0\n    movs r0, #0\n    movs r7, #0\n    movs r6, #1\n    ldr.w r0, [pc, #0x534]\n    ldr r2, [r0]\n    movs r1, #4\n    ldr.w r0, [pc, #0x530]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am052_addr_0052e5ce\n    bl .\n    ldr.w r0, [pc, #0x52c]\n    ldr r1, [r0]\n    uxtb r1, r1\n    ldr.w r0, [pc, #0x528]\n    ldr r0, [r0]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am052_addr_0052e5f2\n    bl .\nL_open_cfw_runtime_am052_b480a_002c:\n    adds r7, r7, #1\n    movs r1, r6\n    uxtb r1, r1\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am052_addr_0052edf0\n    bl .\n    movs r4, r0\n    cmp r4, #0\n    bne L_open_cfw_runtime_am052_b480a_005e\n    ldr.w r0, [pc, #0x510]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am052_addr_004733ee\n    bl .\n    ldr.w r0, [pc, #0x50c]\n    ldr r1, [r0]\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am052_addr_0052eefa\n    bl .\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am052_addr_0044b0ae\n    bl .\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am052_addr_0052e4b4\n    bl .\n    b L_open_cfw_runtime_am052_b480a_0070\nL_open_cfw_runtime_am052_b480a_005e:\n    movs r1, r4\n    ldr.w r0, [pc, #0x4f8]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am052_addr_004733ee\n    bl .\n    movs r6, #1\n    movs r0, #1\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am052_addr_0052edd8\n    bl .\nL_open_cfw_runtime_am052_b480a_0070:\n    movs r0, r7\n    uxtb r0, r0\n    cmp r0, #2\n    bge L_open_cfw_runtime_am052_b480a_007c\n    cmp r4, #0\n    bne L_open_cfw_runtime_am052_b480a_002c\nL_open_cfw_runtime_am052_b480a_007c:\n    pop {r0, r4, r5, r6, r7, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM052_B4888_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am052_b4888(void)
{
    __asm__ volatile(
        "    push {r4, lr}\n    ldr.w r0, [pc, #0x4dc]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am052_addr_004733ee\n    bl .\n    ldr.w r4, [pc, #0x4d8]\n    movs r0, #1\n    strb r0, [r4]\n    movs r0, #0\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am052_b48a6\n    bl .\n    movs r0, #0\n    strb r0, [r4]\n    pop {r4, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM052_B48A6_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am052_b48a6(void)
{
    __asm__ volatile(
        "    push {r3, r4, r5, r6, r7, lr}\n    sub sp, #0x48\n    movs r4, r0\n    movs r0, #1\n    movs r0, #0\n    movs r0, #0\n    ldr.w r0, [pc, #0x4bc]\n    str r0, [sp]\n    movs r0, #0x40\n    str r0, [sp, #4]\n    ldr.w r6, [pc, #0x4b4]\n    ldr.w r3, [pc, #0x4b4]\n    movs r2, r6\n    mov r1, sp\n    movs r0, #6\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am052_addr_0052dd94\n    bl .\n    movs r5, r0\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am052_addr_0052deee\n    bl .\n    movs r2, r0\n    uxtb r2, r2\n    movs r1, r5\n    ldr.w r0, [pc, #0x4a0]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am052_addr_004733ee\n    bl .\n    movs r0, #0x64\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am052_addr_00491102\n    bl .\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am052_addr_0052deee\n    bl .\n    cmp r0, #0\n    beq L_open_cfw_runtime_am052_b48a6_005a\n    ldr.w r0, [pc, #0x48c]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am052_addr_004733ee\n    bl .\n    movs r0, #1\n    ldr.w r1, [pc, #0x470]\n    strb r0, [r1]\nL_open_cfw_runtime_am052_b48a6_005a:\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am052_addr_0052f38c\n    bl .\n    ldr.w r7, [pc, #0x458]\n    movs r0, r7\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am052_addr_0052fcfc\n    bl .\n    cmp r0, #0\n    beq L_open_cfw_runtime_am052_b48a6_00a4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am052_addr_0052dee6\n    bl .\n    ldr r1, [r7]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am052_b47cc\n    bl .\n    uxtb r0, r0\n    cmp r0, #0\n    bne L_open_cfw_runtime_am052_b48a6_0086\n    ldr.w r0, [pc, #0x448]\n    ldrb r0, [r0]\n    cmp r0, #0\n    beq L_open_cfw_runtime_am052_b48a6_00a4\nL_open_cfw_runtime_am052_b48a6_0086:\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am052_addr_0052fb58\n    bl .\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am052_addr_0052f38c\n    bl .\n    ldr r0, [r6]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am052_b480a\n    bl .\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am052_addr_0052f38c\n    bl .\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am052_addr_0052fc04\n    bl .\n    movs r0, #0\n    ldr.w r1, [pc, #0x424]\n    strb r0, [r1]\nL_open_cfw_runtime_am052_b48a6_00a4:\n    movs r0, #0\n    ldr.w r1, [pc, #0x434]\n    str r0, [r1]\n    movs r0, #0\n    ldr.w r1, [pc, #0x430]\n    str r0, [r1]\n    mov.w r3, #0x820\n    mov.w r2, #0x104\n    ldr.w r1, [pc, #0x428]\n    ldr.w r0, [pc, #0x428]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am052_addr_0053006c\n    bl .\n    movs r0, #0\n    ldr.w r1, [pc, #0x420]\n    str r0, [r1]\n    uxtb r4, r4\n    cmp r4, #0\n    beq L_open_cfw_runtime_am052_b48a6_0102\n    add r1, sp, #8\n    movs r0, #1\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am052_addr_00480d72\n    bl .\n    movs r2, #4\n    add r1, sp, #0x10\n    ldr.w r4, [pc, #0x40c]\n    movs r6, r4\n    movs r0, r6\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am052_addr_00439be4\n    bl .\n    ldr r0, [sp, #0xc]\n    lsrs r0, r0, #8\n    strb r0, [r4, #4]\n    ldr r0, [sp, #0xc]\n    lsrs r0, r0, #0x10\n    strb r0, [r4, #5]\n    ldrb r0, [r4, #5]\n    ands r0, r0, #0xfc\n    strb r0, [r4, #5]\nL_open_cfw_runtime_am052_b48a6_0102:\n    movs r1, #0x75\n    movs r3, #0\n    addw r2, pc, #0xe9\n    movs r0, #0\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am052_addr_0048162c\n    bl .\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am052_addr_0052dd58\n    bl .\n    movs r1, #4\n    movs r0, #0x3b\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am052_b4786\n    bl .\n    movs r0, #0x3b\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am052_b4768\n    bl .\n    movs r0, r5\n    add sp, #0x4c\n    pop {r4, r5, r6, r7, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM052_B49CE_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am052_b49ce(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    ldr.w r0, [pc, #0x3c8]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am052_addr_0052a4d2\n    bl .\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am052_addr_0052dd6a\n    bl .\n    movs r0, #0\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am052_addr_0052eece\n    bl .\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am052_addr_0052dd7c\n    bl .\n    movs r0, #0\n    ldr.w r1, [pc, #0x398]\n    str r0, [r1]\n    movs r0, #0\n    ldr.w r1, [pc, #0x394]\n    str r0, [r1]\n    ldr.w r0, [pc, #0x37c]\n    ldr r0, [r0]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am052_addr_0052df12\n    bl .\n    pop {r0, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM052_B4AB2_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am052_b4ab2(void)
{
    __asm__ volatile(
        "    push.w {r3, r4, r5, r6, r7, r8, sb, sl, fp, lr}\n    movs.w r8, #0\n    movs.w sb, #0\n    movs r5, #0\n    cmp r1, #0\n    beq L_open_cfw_runtime_am052_b4ab2_002a\n    ldrb r0, [r1, #2]\n    cmp r0, #2\n    bne L_open_cfw_runtime_am052_b4ab2_002a\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am052_addr_0052b620\n    bl .\n    movw r1, #0x2710\n    ldr.w r0, [pc, #0x2c8]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am052_addr_0052a4c4\n    bl .\n    b L_open_cfw_runtime_am052_b4ab2_01d4\nL_open_cfw_runtime_am052_b4ab2_002a:\n    ldr r6, [pc, #0x2a4]\n    ldr r7, [pc, #0x2a8]\n    ldr r0, [r7]\n    ldr r1, [r6]\n    cmp r0, r1\n    bhs L_open_cfw_runtime_am052_b4ab2_0096\n    ldr r1, [r6]\n    ldr r0, [r7]\n    subs r1, r1, r0\n    uxth r1, r1\n    ldr r0, [pc, #0x2b8]\n    ldr r0, [r0]\n    ldr r2, [r7]\n    add r0, r2\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am052_addr_00530186\n    bl .\n    ldr r1, [r7]\n    uxtah r0, r1, r0\n    str r0, [r7]\n    ldr r0, [r7]\n    ldr r1, [r6]\n    cmp r0, r1\n    beq L_open_cfw_runtime_am052_b4ab2_0066\n    movs r1, #1\n    ldr r0, [pc, #0x294]\n    ldrb r0, [r0]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am052_addr_0052b91e\n    bl .\n    b L_open_cfw_runtime_am052_b4ab2_01d4\nL_open_cfw_runtime_am052_b4ab2_0066:\n    movs r0, #0\n    str r0, [r6]\n    movs r0, #0\n    str r0, [r7]\n    b L_open_cfw_runtime_am052_b4ab2_0096\n    ldr.w r8, [pc, #0x278]\n    mov r0, r8\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am052_addr_0052a4d2\n    bl .\n    movw r1, #0x2710\n    mov r0, r8\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am052_addr_0052a4c4\n    bl .\n    movs r2, #1\n    movs r1, #0\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am052_addr_005300e2\n    bl .\n    movs.w r8, #0\n    movs.w sb, #0\nL_open_cfw_runtime_am052_b4ab2_0096:\n    mov r0, sb\n    adds.w sb, r0, #1\n    cmp.w r0, #0x3e8\n    bhs.w #0x4b4c66\n    ldr.w sl, [pc, #0x258]\n    ldr.w r0, [sl]\n    ubfx r0, r0, #0x15, #1\n    cmp r0, #0\n    beq L_open_cfw_runtime_am052_b4ab2_0178\n    ldr.w fp, [pc, #0x22c]\n    ldr.w r0, [fp]\n    str r0, [sp]\n    ldr r4, [pc, #0x228]\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am052_addr_0052a4d2\n    bl .\n    movw r1, #0x2710\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am052_addr_0052a4c4\n    bl .\n    movs r0, #0\n    str r0, [r6]\n    movs r2, r6\n    ldr r1, [pc, #0x228]\n    ldr r0, [pc, #0x1e8]\n    ldr r0, [r0]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am052_addr_0052e1ea\n    bl .\n    movs r4, r0\n    ldr r0, [r6]\n    movw r1, #0x101\n    cmp r0, r1\n    blo L_open_cfw_runtime_am052_b4ab2_00f2\n    ldr r0, [pc, #0x218]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am052_addr_004b47ae\n    bl .\nL_open_cfw_runtime_am052_b4ab2_00f2:\n    cmp r4, #0\n    bne L_open_cfw_runtime_am052_b4ab2_015a\n    movs r4, #0\n    b L_open_cfw_runtime_am052_b4ab2_0102\nL_open_cfw_runtime_am052_b4ab2_00fa:\n    movs r0, #1\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am052_addr_00491102\n    bl .\n    adds r4, r4, #1\nL_open_cfw_runtime_am052_b4ab2_0102:\n    cmp.w r4, #0x7d0\n    bhs L_open_cfw_runtime_am052_b4ab2_011e\n    ldr.w r0, [sl]\n    ubfx r0, r0, #0x15, #1\n    cmp r0, #0\n    beq L_open_cfw_runtime_am052_b4ab2_011e\n    ldr.w r0, [fp]\n    ldr r1, [sp]\n    cmp r0, r1\n    beq L_open_cfw_runtime_am052_b4ab2_00fa\nL_open_cfw_runtime_am052_b4ab2_011e:\n    ldr r1, [r6]\n    uxth r1, r1\n    ldr r0, [pc, #0x1d4]\n    ldr r0, [r0]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am052_addr_00530186\n    bl .\n    str r0, [r7]\n    ldr r0, [r7]\n    ldr r1, [r6]\n    cmp r0, r1\n    beq L_open_cfw_runtime_am052_b4ab2_0140\n    movs r1, #1\n    ldr r0, [pc, #0x1b8]\n    ldrb r0, [r0]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am052_addr_0052b91e\n    bl .\n    b L_open_cfw_runtime_am052_b4ab2_01b4\nL_open_cfw_runtime_am052_b4ab2_0140:\n    movs r0, #0\n    str r0, [r6]\n    movs r0, #0\n    str r0, [r7]\n    adds r5, r5, #1\nL_open_cfw_runtime_am052_b4ab2_014a:\n    cmp r5, #4\n    blo L_open_cfw_runtime_am052_b4ab2_0096\n    movs r1, #1\n    ldr r0, [pc, #0x1a0]\n    ldrb r0, [r0]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am052_addr_0052b91e\n    bl .\n    b L_open_cfw_runtime_am052_b4ab2_01b4\nL_open_cfw_runtime_am052_b4ab2_015a:\n    cmp r4, #0\n    beq L_open_cfw_runtime_am052_b4ab2_014a\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am052_addr_004b47ae\n    bl .\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am052_b49ce\n    bl .\n    movs r0, #0\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am052_b48a6\n    bl .\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am052_addr_004b4d18\n    bl .\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am052_addr_004b3026\n    bl .\n    b L_open_cfw_runtime_am052_b4ab2_01d4\nL_open_cfw_runtime_am052_b4ab2_0178:\n    ldr r4, [pc, #0x164]\n    ldr r0, [r4, #8]\n    cmp r0, #0\n    beq L_open_cfw_runtime_am052_b4ab2_01a8\n    ldr r0, [r4, #0x14]\n    ldr r1, [r4, #4]\n    add r0, r1\n    ldr r2, [r0]\n    adds r1, r0, #4\n    ldr r0, [pc, #0x134]\n    ldr r0, [r0]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am052_addr_0052e0d2\n    bl .\n    cmp r0, #0\n    beq.w #0x4b4b22\n    adds.w r8, r8, #1\n    movw r0, #0x2711\n    cmp r8, r0\n    blo.w #0x4b4b48\n    b L_open_cfw_runtime_am052_b4ab2_01aa\nL_open_cfw_runtime_am052_b4ab2_01a8:\n    b L_open_cfw_runtime_am052_b4ab2_01b4\nL_open_cfw_runtime_am052_b4ab2_01aa:\n    movs r1, #1\n    ldr r0, [pc, #0x144]\n    ldrb r0, [r0]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am052_addr_0052b91e\n    bl .\nL_open_cfw_runtime_am052_b4ab2_01b4:\n    cmp.w sb, #0x3e8\n    bne L_open_cfw_runtime_am052_b4ab2_01d4\n    ldr r0, [pc, #0x14c]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am052_addr_004b47ae\n    bl .\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am052_b49ce\n    bl .\n    movs r0, #0\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am052_b48a6\n    bl .\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am052_addr_004b4d18\n    bl .\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am052_addr_004b3026\n    bl .\n    b L_open_cfw_runtime_am052_b4ab2_01d4\nL_open_cfw_runtime_am052_b4ab2_01d4:\n    pop.w {r0, r4, r5, r6, r7, r8, sb, sl, fp, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM052_B4EEE_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am052_b4eee(void)
{
    __asm__ volatile(
        "    push {r0, r1, r2, r3, r4, lr}\n    movs r4, r0\n    movs r0, r4\n    uxtb r0, r0\n    cmp r0, #0\n    bne.w #0x4b4ffc\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am052_addr_004c9c50\n    bl .\n    cmp r0, #0\n    beq L_open_cfw_runtime_am052_b4eee_0048\n    movs r2, #3\n    adr r1, #0x108\n    ldr r0, [pc, #0x2c8]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am052_addr_0044b610\n    bl .\n    cmp r0, #0\n    bne L_open_cfw_runtime_am052_b4eee_0048\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am052_addr_0043d0ce\n    bl .\n    lsls r0, r0, #0x1e\n    bpl L_open_cfw_runtime_am052_b4eee_0046\n    uxtb r4, r4\n    str r4, [sp, #8]\n    ldr r0, [pc, #0x2c0]\n    str r0, [sp, #4]\n    movw r0, #0x13f\n    str r0, [sp]\n    ldr r3, [pc, #0x2b8]\n    ldr r2, [pc, #0x2ac]\n    adr r1, #0x108\n    movs r0, #1\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am052_addr_0043d574\n    bl .\nL_open_cfw_runtime_am052_b4eee_0046:\n    b L_open_cfw_runtime_am052_b4eee_010a\nL_open_cfw_runtime_am052_b4eee_0048:\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am052_addr_004c9c50\n    bl .\n    cmp r0, #0\n    beq L_open_cfw_runtime_am052_b4eee_0082\n    ldr r1, [pc, #0x294]\n    movs r2, #4\n    movs r0, r1\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am052_addr_0044b610\n    bl .\n    cmp r0, #0\n    bne L_open_cfw_runtime_am052_b4eee_0082\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am052_addr_0043d0ce\n    bl .\n    lsls r0, r0, #0x1e\n    bpl L_open_cfw_runtime_am052_b4eee_0080\n    uxtb r4, r4\n    str r4, [sp, #8]\n    ldr r0, [pc, #0x284]\n    str r0, [sp, #4]\n    movw r0, #0x13f\n    str r0, [sp]\n    ldr r3, [pc, #0x280]\n    ldr r2, [pc, #0x270]\n    adr r1, #0xd0\n    movs r0, #2\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am052_addr_0043d574\n    bl .\nL_open_cfw_runtime_am052_b4eee_0080:\n    b L_open_cfw_runtime_am052_b4eee_010a\nL_open_cfw_runtime_am052_b4eee_0082:\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am052_addr_004c9c50\n    bl .\n    cmp r0, #0\n    beq L_open_cfw_runtime_am052_b4eee_00bc\n    movs r2, #4\n    ldr r1, [pc, #0x260]\n    ldr r0, [pc, #0x254]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am052_addr_0044b610\n    bl .\n    cmp r0, #0\n    bne L_open_cfw_runtime_am052_b4eee_00bc\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am052_addr_0043d0ce\n    bl .\n    lsls r0, r0, #0x1e\n    bpl L_open_cfw_runtime_am052_b4eee_00ba\n    uxtb r4, r4\n    str r4, [sp, #8]\n    ldr r0, [pc, #0x24c]\n    str r0, [sp, #4]\n    movw r0, #0x13f\n    str r0, [sp]\n    ldr r3, [pc, #0x244]\n    ldr r2, [pc, #0x238]\n    adr r1, #0x94\n    movs r0, #3\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am052_addr_0043d574\n    bl .\nL_open_cfw_runtime_am052_b4eee_00ba:\n    b L_open_cfw_runtime_am052_b4eee_010a\nL_open_cfw_runtime_am052_b4eee_00bc:\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am052_addr_004c9c50\n    bl .\n    cmp r0, #0\n    beq L_open_cfw_runtime_am052_b4eee_00e8\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am052_addr_0043d0ce\n    bl .\n    lsls r0, r0, #0x1e\n    bpl L_open_cfw_runtime_am052_b4eee_00e6\n    uxtb r4, r4\n    str r4, [sp, #8]\n    ldr r0, [pc, #0x220]\n    str r0, [sp, #4]\n    movw r0, #0x13f\n    str r0, [sp]\n    ldr r3, [pc, #0x218]\n    ldr r2, [pc, #0x20c]\n    adr r1, #0x68\n    movs r0, #4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am052_addr_0043d574\n    bl .\nL_open_cfw_runtime_am052_b4eee_00e6:\n    b L_open_cfw_runtime_am052_b4eee_010a\nL_open_cfw_runtime_am052_b4eee_00e8:\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am052_addr_004c9c50\n    bl .\n    cmp r0, #0\n    beq L_open_cfw_runtime_am052_b4eee_00fe\n    movs r2, #3\n    adr r1, #0x108\n    adr r0, #0x54\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am052_addr_0044b610\n    bl .\n    cmp r0, #0\n    beq L_open_cfw_runtime_am052_b4eee_010a\nL_open_cfw_runtime_am052_b4eee_00fe:\n    uxtb r4, r4\n    movs r2, r4\n    ldr r1, [pc, #0x1ec]\n    ldr r0, [pc, #0x1e0]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am052_addr_0052a63c\n    bl .\nL_open_cfw_runtime_am052_b4eee_010a:\n    movs r0, #0\n    b L_open_cfw_runtime_am052_b4eee_011c\n    ldr r1, [pc, #0x1d0]\n    uxtb r4, r4\n    movs r0, #0x14\n    muls r4, r0, r4\n    add.w r0, r1, r4\n    subs r0, #0x14\nL_open_cfw_runtime_am052_b4eee_011c:\n    add sp, #0x10\n    pop {r4, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM052_B5014_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am052_b5014(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    ldr r3, [pc, #0x1d0]\n    ldrb r2, [r0]\n    strb r2, [r3, #0xc]\n    ldrb r0, [r0, #1]\n    strb r0, [r3, #0xd]\n    movs r2, #0x10\n    movs r0, r3\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am052_addr_004751c8\n    bl .\n    cmp r0, #0\n    bne L_open_cfw_runtime_am052_b5014_001c\n    movs r0, #1\n    b L_open_cfw_runtime_am052_b5014_001e\nL_open_cfw_runtime_am052_b5014_001c:\n    movs r0, #0\nL_open_cfw_runtime_am052_b5014_001e:\n    uxtb r0, r0\n    pop {r1, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM052_B503C_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am052_b503c(void)
{
    __asm__ volatile(
        "    push {r3, r4, r5, lr}\n    movs r4, r2\n    movs r5, r3\n    uxth r4, r4\n    uxth r5, r5\n    cmp r4, r5\n    blo L_open_cfw_runtime_am052_b503c_0010\n    movs r2, r3\nL_open_cfw_runtime_am052_b503c_0010:\n    movs r3, r1\n    uxtb r3, r3\n    ldrh.w r3, [r0, r3, lsl #2]\n    movs r4, r2\n    uxth r4, r4\n    cmp r3, r4\n    beq L_open_cfw_runtime_am052_b503c_0036\n    uxtb r1, r1\n    strh.w r2, [r0, r1, lsl #2]\n    uxth r2, r2\n    str r2, [sp]\n    movs r3, #0\n    movs r2, #0\n    movs r1, #0x16\n    ldrb r0, [r0, #0xe]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am052_b5074\n    bl .\nL_open_cfw_runtime_am052_b503c_0036:\n    pop {r0, r4, r5, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM052_B5074_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am052_b5074(void)
{
    __asm__ volatile(
        "    push {r3, r4, r5, lr}\n    sub sp, #0x10\n    ldr r5, [pc, #0x154]\n    ldr r4, [r5, #0x58]\n    cmp r4, #0\n    beq L_open_cfw_runtime_am052_b5074_0036\n    ldr r4, [sp, #0x20]\n    uxtb r0, r0\n    strh.w r0, [sp]\n    strb.w r1, [sp, #2]\n    strb.w r3, [sp, #3]\n    movs r0, #0\n    strh.w r0, [sp, #8]\n    strh.w r2, [sp, #0xa]\n    movs r0, #0\n    strb.w r0, [sp, #0xc]\n    strh.w r4, [sp, #0xe]\n    mov r0, sp\n    ldr r1, [r5, #0x58]\n    blx r1\nL_open_cfw_runtime_am052_b5074_0036:\n    add sp, #0x14\n    pop {r4, r5, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM052_B50AE_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am052_b50ae(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    movs r1, #0\n    uxth r0, r0\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am052_addr_004bf990\n    bl .\n    pop {r1, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM052_B50BA_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am052_b50ba(void)
{
    __asm__ volatile(
        "    push {r3, r4, r5, lr}\n    movs r4, r1\n    uxtb r4, r4\n    cmp r4, #0\n    bne L_open_cfw_runtime_am052_b50ba_0016\n    uxth r2, r2\n    ldrh r1, [r0, #0xc]\n    movs r0, #4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am052_addr_00530bbc\n    bl .\n    b L_open_cfw_runtime_am052_b50ba_002e\nL_open_cfw_runtime_am052_b50ba_0016:\n    ldr r5, [pc, #0xfc]\n    ldr r4, [r5, #0x54]\n    cmp r4, #0\n    beq L_open_cfw_runtime_am052_b50ba_0028\n    uxth r2, r2\n    uxtb r1, r1\n    ldr r4, [r5, #0x54]\n    blx r4\n    b L_open_cfw_runtime_am052_b50ba_002e\nL_open_cfw_runtime_am052_b50ba_0028:\n    movs r0, r3\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am052_addr_004bf9b0\n    bl .\nL_open_cfw_runtime_am052_b50ba_002e:\n    pop {r0, r4, r5, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM052_B50F0_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am052_b50f0(void)
{
    __asm__ volatile(
        "    uxtb r0, r0\n    movs r2, #3\n    uxtb r1, r1\n    mla r0, r2, r0, r1\n    uxth r0, r0\n    bx lr\n"
    );
}
#endif

#if defined(OPEN_CFW_AM052_B50FE_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am052_b50fe(void)
{
    __asm__ volatile(
        "    push {r4, r5}\n    movs r3, r0\n    uxth r3, r3\n    movs r4, #3\n    sdiv r5, r3, r4\n    mls r3, r4, r5, r3\n    strb r3, [r2]\n    uxth r0, r0\n    movs r2, #3\n    sdiv r0, r0, r2\n    strb r0, [r1]\n    pop {r4, r5}\n    bx lr\n"
    );
}
#endif

#if defined(OPEN_CFW_AM052_B5204_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am052_b5204(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    uxtb r0, r0\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am052_b4eee\n    bl .\n    ldrh r0, [r0]\n    pop {r1, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM052_B5210_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am052_b5210(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    uxtb r1, r1\n    cmp r1, #0x1b\n    beq L_open_cfw_runtime_am052_b5210_000c\n    cmp r1, #0x1d\n    bne L_open_cfw_runtime_am052_b5210_0010\nL_open_cfw_runtime_am052_b5210_000c:\n    movs r1, #0xb\n    b L_open_cfw_runtime_am052_b5210_0012\nL_open_cfw_runtime_am052_b5210_0010:\n    movs r1, #0\nL_open_cfw_runtime_am052_b5210_0012:\n    uxtb r1, r1\n    rsbs r1, r1, #0\n    add r0, r1\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am052_addr_004bf9b0\n    bl .\n    pop {r0, pc}\n"
    );
}
#endif
