/*
 * SPDX-License-Identifier: MIT
 *
 * Source-owned exact helpers from the AM-022 retained island.
 */

#if defined(OPEN_CFW_AM022_547AE_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am022_547ae(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am022_addr_0044b5a0\n    bl .\n    pop {r1, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM022_547B6_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am022_547b6(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am022_addr_0048d540\n    bl .\n    pop {r1, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM022_547BE_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am022_547be(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am022_addr_0046cacc\n    bl .\n    pop {r1, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM022_547C6_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am022_547c6(void)
{
    __asm__ volatile(
        "    push {r4, r5, r6, lr}\n    movs r5, r0\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am022_addr_00454768\n    bl .\n    movs r6, r0\n    adds r6, r6, #1\n    movs r0, r6\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am022_addr_0044f718\n    bl .\n    movs r4, r0\n    cmp r4, #0\n    bne L_open_cfw_runtime_am022_547c6_001e\n    movs r0, #0\n    b L_open_cfw_runtime_am022_547c6_002a\nL_open_cfw_runtime_am022_547c6_001e:\n    movs r2, r6\n    movs r1, r5\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am022_addr_00454738\n    bl .\n    movs r0, r4\nL_open_cfw_runtime_am022_547c6_002a:\n    pop {r4, r5, r6, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM022_547F2_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am022_547f2(void)
{
    __asm__ volatile(
        "    push {r4, r5, r6, lr}\n    movs r5, r0\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am022_addr_00454770\n    bl .\n    movs r6, r0\n    adds r0, r6, #1\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am022_addr_0044f718\n    bl .\n    movs r4, r0\n    cmp r4, #0\n    bne L_open_cfw_runtime_am022_547f2_001c\n    movs r0, #0\n    b L_open_cfw_runtime_am022_547f2_002c\nL_open_cfw_runtime_am022_547f2_001c:\n    movs r2, r6\n    movs r1, r5\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am022_addr_00454738\n    bl .\n    movs r0, #0\n    strb r0, [r4, r6]\n    movs r0, r4\nL_open_cfw_runtime_am022_547f2_002c:\n    pop {r4, r5, r6, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM022_54820_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am022_54820(void)
{
    __asm__ volatile(
        "    push.w {r3, r4, r5, r6, r7, r8, sb, sl, lr}\n    sub sp, #0x14\n    movs r7, r0\n    mov r8, r1\n    mov sb, r2\n    mov sl, r3\n    ldr r4, [sp, #0x3c]\n    cmp r4, #0\n    bne L_open_cfw_runtime_am022_54820_0022\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am022_addr_005fa0a4\n    bl .\n    movs r0, #0\n    movs.w r1, #-1\n    str r0, [r1]\nL_open_cfw_runtime_am022_54820_0020:\n    b L_open_cfw_runtime_am022_54820_0020\nL_open_cfw_runtime_am022_54820_0022:\n    ldr r5, [sp, #0x40]\n    cmp r5, #0\n    bne L_open_cfw_runtime_am022_54820_0036\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am022_addr_005fa0a4\n    bl .\n    movs r0, #0\n    movs.w r1, #-1\n    str r0, [r1]\nL_open_cfw_runtime_am022_54820_0034:\n    b L_open_cfw_runtime_am022_54820_0034\nL_open_cfw_runtime_am022_54820_0036:\n    movs r0, #0x70\n    str r0, [sp]\n    ldr r0, [sp]\n    cmp r0, #0x70\n    beq L_open_cfw_runtime_am022_54820_004e\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am022_addr_005fa0a4\n    bl .\n    movs r0, #0\n    movs.w r1, #-1\n    str r0, [r1]\nL_open_cfw_runtime_am022_54820_004c:\n    b L_open_cfw_runtime_am022_54820_004c\nL_open_cfw_runtime_am022_54820_004e:\n    ldr r0, [sp]\n    cmp r5, #0\n    beq L_open_cfw_runtime_am022_54820_008e\n    cmp r4, #0\n    beq L_open_cfw_runtime_am022_54820_008e\n    movs r1, #0x70\n    movs r2, #0\n    movs r6, r5\n    movs r0, r6\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am022_addr_0043c0e4\n    bl .\n    str r4, [r5, #0x30]\n    movs r0, #2\n    strb.w r0, [r5, #0x6d]\n    movs r0, #0\n    str r0, [sp, #0xc]\n    str r5, [sp, #8]\n    add r0, sp, #0x10\n    str r0, [sp, #4]\n    ldr r0, [sp, #0x38]\n    str r0, [sp]\n    mov r3, sl\n    mov r2, sb\n    mov r1, r8\n    movs r0, r7\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am022_54938\n    bl .\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am022_549fc\n    bl .\n    b L_open_cfw_runtime_am022_54820_0092\nL_open_cfw_runtime_am022_54820_008e:\n    movs r0, #0\n    str r0, [sp, #0x10]\nL_open_cfw_runtime_am022_54820_0092:\n    ldr r0, [sp, #0x10]\n    add sp, #0x18\n    pop.w {r4, r5, r6, r7, r8, sb, sl, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM022_548BA_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am022_548ba(void)
{
    __asm__ volatile(
        "    push.w {r0, r1, r2, r3, r4, r5, r6, r7, r8, sb, sl, lr}\n    movs r6, r0\n    movs r7, r1\n    mov r8, r2\n    mov sb, r3\n    mov r0, r8\n    uxth r0, r0\n    lsls r0, r0, #2\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am022_addr_00456110\n    bl .\n    movs r5, r0\n    cmp r5, #0\n    beq L_open_cfw_runtime_am022_548ba_0040\n    movs r0, #0x70\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am022_addr_00456110\n    bl .\n    movs r4, r0\n    cmp r4, #0\n    beq L_open_cfw_runtime_am022_548ba_0038\n    movs r1, #0x70\n    movs r2, #0\n    mov sl, r4\n    mov r0, sl\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am022_addr_0043c0e4\n    bl .\n    str r5, [r4, #0x30]\n    b L_open_cfw_runtime_am022_548ba_0042\nL_open_cfw_runtime_am022_548ba_0038:\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am022_addr_00456210\n    bl .\n    b L_open_cfw_runtime_am022_548ba_0042\nL_open_cfw_runtime_am022_548ba_0040:\n    movs r4, #0\nL_open_cfw_runtime_am022_548ba_0042:\n    cmp r4, #0\n    beq L_open_cfw_runtime_am022_548ba_0074\n    movs r0, #0\n    strb.w r0, [r4, #0x6d]\n    movs r0, #0\n    str r0, [sp, #0xc]\n    str r4, [sp, #8]\n    ldr r0, [sp, #0x34]\n    str r0, [sp, #4]\n    ldr r0, [sp, #0x30]\n    str r0, [sp]\n    mov r3, sb\n    uxth.w r8, r8\n    mov r2, r8\n    movs r1, r7\n    movs r0, r6\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am022_54938\n    bl .\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am022_549fc\n    bl .\n    movs r0, #1\n    b L_open_cfw_runtime_am022_548ba_0078\nL_open_cfw_runtime_am022_548ba_0074:\n    movs.w r0, #-1\nL_open_cfw_runtime_am022_548ba_0078:\n    add sp, #0x10\n    pop.w {r4, r5, r6, r7, r8, sb, sl, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM022_54938_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am022_54938(void)
{
    __asm__ volatile(
        "    push.w {r3, r4, r5, r6, r7, r8, sb, lr}\n    movs r5, r0\n    movs r4, r1\n    mov sb, r2\n    mov r8, r3\n    ldr r6, [sp, #0x28]\n    lsls.w r1, sb, #2\n    movs r2, #0xa5\n    ldr r7, [r6, #0x30]\n    movs r0, r7\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am022_addr_0043c0e4\n    bl .\n    ldr r0, [r6, #0x30]\n    add.w r0, r0, sb, lsl #2\n    subs r7, r0, #4\n    lsrs r7, r7, #3\n    lsls r7, r7, #3\n    ands r0, r7, #7\n    cmp r0, #0\n    beq L_open_cfw_runtime_am022_54938_003e\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am022_addr_005fa0a4\n    bl .\n    movs r0, #0\n    movs.w r1, #-1\n    str r0, [r1]\nL_open_cfw_runtime_am022_54938_003c:\n    b L_open_cfw_runtime_am022_54938_003c\nL_open_cfw_runtime_am022_54938_003e:\n    str.w sb, [r6, #0x54]\n    cmp r4, #0\n    beq L_open_cfw_runtime_am022_54938_0066\n    movs r1, #0\n    b L_open_cfw_runtime_am022_54938_004c\nL_open_cfw_runtime_am022_54938_004a:\n    adds r1, r1, #1\nL_open_cfw_runtime_am022_54938_004c:\n    cmp r1, #0x20\n    bhs L_open_cfw_runtime_am022_54938_0060\n    ldrb r0, [r4, r1]\n    add.w r2, r6, r1\n    strb.w r0, [r2, #0x34]\n    ldrb r0, [r4, r1]\n    cmp r0, #0\n    bne L_open_cfw_runtime_am022_54938_004a\nL_open_cfw_runtime_am022_54938_0060:\n    movs r0, #0\n    strb.w r0, [r6, #0x53]\nL_open_cfw_runtime_am022_54938_0066:\n    ldr.w sb, [sp, #0x20]\n    cmp.w sb, #0x38\n    blo L_open_cfw_runtime_am022_54938_007e\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am022_addr_005fa0a4\n    bl .\n    movs r0, #0\n    movs.w r1, #-1\n    str r0, [r1]\nL_open_cfw_runtime_am022_54938_007c:\n    b L_open_cfw_runtime_am022_54938_007c\nL_open_cfw_runtime_am022_54938_007e:\n    cmp.w sb, #0x38\n    blo L_open_cfw_runtime_am022_54938_0088\n    movs.w sb, #0x37\nL_open_cfw_runtime_am022_54938_0088:\n    ldr r4, [sp, #0x24]\n    str.w sb, [r6, #0x2c]\n    str.w sb, [r6, #0x60]\n    adds r0, r6, #4\n    movs r1, #0\n    str r1, [r0, #0x10]\n    adds.w r0, r6, #0x18\n    movs r1, #0\n    str r1, [r0, #0x10]\n    str r6, [r6, #0x10]\n    rsbs.w sb, sb, #0x38\n    str.w sb, [r6, #0x18]\n    str r6, [r6, #0x24]\n    mov r3, r8\n    movs r2, r5\n    ldr r1, [r6, #0x30]\n    movs r0, r7\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am022_addr_0044215a\n    bl .\n    str r0, [r6]\n    cmp r4, #0\n    beq L_open_cfw_runtime_am022_54938_00c0\n    str r6, [r4]\nL_open_cfw_runtime_am022_54938_00c0:\n    pop.w {r0, r4, r5, r6, r7, r8, sb, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM022_549FC_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am022_549fc(void)
{
    __asm__ volatile(
        "    push {r4, r5, r6, lr}\n    movs r4, r0\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am022_addr_004420d0\n    bl .\n    ldr.w r1, [pc, #0x798]\n    ldr r0, [r1]\n    adds r0, r0, #1\n    str r0, [r1]\n    ldr.w r5, [pc, #0x794]\n    ldr r0, [r5]\n    cmp r0, #0\n    bne L_open_cfw_runtime_am022_549fc_002a\n    str r4, [r5]\n    ldr r0, [r1]\n    cmp r0, #1\n    bne L_open_cfw_runtime_am022_549fc_0040\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am022_addr_0045568c\n    bl .\n    b L_open_cfw_runtime_am022_549fc_0040\nL_open_cfw_runtime_am022_549fc_002a:\n    ldr.w r0, [pc, #0x8ec]\n    ldr r0, [r0]\n    cmp r0, #0\n    bne L_open_cfw_runtime_am022_549fc_0040\n    ldr r0, [r4, #0x2c]\n    ldr r1, [r5]\n    ldr r1, [r1, #0x2c]\n    cmp r0, r1\n    blo L_open_cfw_runtime_am022_549fc_0040\n    str r4, [r5]\nL_open_cfw_runtime_am022_549fc_0040:\n    ldr.w r0, [pc, #0x768]\n    ldr r1, [r0]\n    adds r1, r1, #1\n    str r1, [r0]\n    ldr r0, [r0]\n    str r0, [r4, #0x58]\n    ldr.w r0, [pc, #0x760]\n    ldr r1, [r0]\n    ldr r2, [r4, #0x2c]\n    cmp r1, r2\n    bhs L_open_cfw_runtime_am022_549fc_005e\n    ldr r1, [r4, #0x2c]\n    str r1, [r0]\nL_open_cfw_runtime_am022_549fc_005e:\n    movs r0, #0x14\n    ldr.w r1, [pc, #0x750]\n    ldr r2, [r4, #0x2c]\n    muls r2, r0, r2\n    add r2, r1\n    ldr r2, [r2, #4]\n    str r2, [r4, #8]\n    ldr r3, [r2, #8]\n    str r3, [r4, #0xc]\n    adds r3, r4, #4\n    ldr r6, [r2, #8]\n    str r3, [r6, #4]\n    adds r3, r4, #4\n    str r3, [r2, #8]\n    ldr r2, [r4, #0x2c]\n    muls r2, r0, r2\n    add r2, r1\n    str r2, [r4, #0x14]\n    ldr r2, [r4, #0x2c]\n    muls r2, r0, r2\n    ldr r3, [r4, #0x2c]\n    mul r0, r0, r3\n    ldr r0, [r1, r0]\n    adds r0, r0, #1\n    str r0, [r1, r2]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am022_addr_004420e8\n    bl .\n    ldr.w r0, [pc, #0x87c]\n    ldr r0, [r0]\n    cmp r0, #0\n    beq L_open_cfw_runtime_am022_549fc_00b0\n    ldr r0, [r5]\n    ldr r0, [r0, #0x2c]\n    ldr r1, [r4, #0x2c]\n    cmp r0, r1\n    bhs L_open_cfw_runtime_am022_549fc_00b0\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am022_addr_004420bc\n    bl .\nL_open_cfw_runtime_am022_549fc_00b0:\n    pop {r4, r5, r6, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM022_54D88_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am022_54d88(void)
{
    __asm__ volatile(
        "    movs r1, #0\n    ldr.w r0, [pc, #0x420]\n    ldr r0, [r0]\n    cmp r0, #0\n    beq L_open_cfw_runtime_am022_54d88_000e\n    movs r1, #1\nL_open_cfw_runtime_am022_54d88_000e:\n    ldr.w r0, [pc, #0x40c]\n    ldr r0, [r0]\n    ldr r0, [r0, #0x2c]\n    cmp r0, #0\n    beq L_open_cfw_runtime_am022_54d88_001e\n    movs r0, #0\n    b L_open_cfw_runtime_am022_54d88_0042\nL_open_cfw_runtime_am022_54d88_001e:\n    ldr.w r0, [pc, #0x408]\n    ldr r0, [r0]\n    cmp r0, #2\n    blo L_open_cfw_runtime_am022_54d88_002c\n    movs r0, #0\n    b L_open_cfw_runtime_am022_54d88_0042\nL_open_cfw_runtime_am022_54d88_002c:\n    cmp r1, #0\n    beq L_open_cfw_runtime_am022_54d88_0034\n    movs r0, #0\n    b L_open_cfw_runtime_am022_54d88_0042\nL_open_cfw_runtime_am022_54d88_0034:\n    ldr.w r0, [pc, #0x964]\n    ldr r0, [r0]\n    ldr.w r1, [pc, #0x6a8]\n    ldr r1, [r1]\n    subs r0, r0, r1\nL_open_cfw_runtime_am022_54d88_0042:\n    bx lr\n"
    );
}
#endif

#if defined(OPEN_CFW_AM022_54F38_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am022_54f38(void)
{
    __asm__ volatile(
        "    push.w {r4, r5, r6, r7, r8, lr}\n    movs r7, r0\n    mov r8, r1\n    movs r5, r2\n    movs r6, #0\n    movs r4, #0x38\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am022_addr_00454d7c\n    bl .\n    ldr r0, [pc, #0x254]\n    ldr r0, [r0]\n    cmp r8, r0\n    blo L_open_cfw_runtime_am022_54f38_0096\nL_open_cfw_runtime_am022_54f38_001a:\n    subs r4, r4, #1\n    movs.w r8, #0x24\n    movs r2, #1\n    ldr r0, [pc, #0x254]\n    movs r1, #0x14\n    mul r1, r1, r4\n    add r1, r0\n    mul r0, r8, r6\n    add r0, r7\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am022_557b0\n    bl .\n    adds r6, r0, r6\n    cmp r4, #0\n    bne L_open_cfw_runtime_am022_54f38_001a\n    movs r2, #2\n    ldr.w r0, [pc, #0x4f8]\n    ldr r1, [r0]\n    mul r0, r8, r6\n    add r0, r7\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am022_557b0\n    bl .\n    adds r6, r0, r6\n    movs r2, #2\n    ldr.w r0, [pc, #0x4e8]\n    ldr r1, [r0]\n    mul r0, r8, r6\n    add r0, r7\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am022_557b0\n    bl .\n    adds r6, r0, r6\n    movs r2, #4\n    ldr.w r1, [pc, #0x378]\n    mul r0, r8, r6\n    add r0, r7\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am022_557b0\n    bl .\n    adds r6, r0, r6\n    movs r4, r6\n    movs r2, #3\n    ldr.w r1, [pc, #0x4c4]\n    mul r8, r8, r4\n    add.w r0, r7, r8\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am022_557b0\n    bl .\n    movs r6, r0\n    adds r6, r6, r4\n    cmp r5, #0\n    beq L_open_cfw_runtime_am022_54f38_0096\n    movs r0, #0\n    str r0, [r5]\nL_open_cfw_runtime_am022_54f38_0096:\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am022_addr_00454dcc\n    bl .\n    movs r0, r6\n    pop.w {r4, r5, r6, r7, r8, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM022_54FD8_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am022_54fd8(void)
{
    __asm__ volatile(
        "    push {r3, r4, r5, lr}\n    movs r4, r0\n    ldr.w r0, [pc, #0x744]\n    ldr r1, [r0]\n    ldr.w r5, [pc, #0x488]\n    ldr r2, [r5]\n    adds r2, r4, r2\n    cmp r1, r2\n    bhs L_open_cfw_runtime_am022_54fd8_0024\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am022_addr_005fa0a4\n    bl .\n    movs r0, #0\n    movs.w r1, #-1\n    str r0, [r1]\nL_open_cfw_runtime_am022_54fd8_0022:\n    b L_open_cfw_runtime_am022_54fd8_0022\nL_open_cfw_runtime_am022_54fd8_0024:\n    ldr r1, [r5]\n    adds r1, r4, r1\n    ldr r0, [r0]\n    cmp r1, r0\n    bne L_open_cfw_runtime_am022_54fd8_006c\n    ldr.w r0, [pc, #0x460]\n    ldr r0, [r0]\n    cmp r0, #0\n    bne L_open_cfw_runtime_am022_54fd8_0046\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am022_addr_005fa0a4\n    bl .\n    movs r0, #0\n    movs.w r1, #-1\n    str r0, [r1]\nL_open_cfw_runtime_am022_54fd8_0044:\n    b L_open_cfw_runtime_am022_54fd8_0044\nL_open_cfw_runtime_am022_54fd8_0046:\n    cmp r4, #0\n    bne L_open_cfw_runtime_am022_54fd8_0058\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am022_addr_005fa0a4\n    bl .\n    movs r0, #0\n    movs.w r1, #-1\n    str r0, [r1]\nL_open_cfw_runtime_am022_54fd8_0056:\n    b L_open_cfw_runtime_am022_54fd8_0056\nL_open_cfw_runtime_am022_54fd8_0058:\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am022_addr_004420d0\n    bl .\n    ldr.w r0, [pc, #0x9e0]\n    ldr r1, [r0]\n    adds r1, r1, #1\n    str r1, [r0]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am022_addr_004420e8\n    bl .\n    subs r4, r4, #1\nL_open_cfw_runtime_am022_54fd8_006c:\n    ldr r0, [r5]\n    adds r4, r4, r0\n    str r4, [r5]\n    pop {r0, r4, r5, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM022_552AE_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am022_552ae(void)
{
    __asm__ volatile(
        "    push {r3, r4, r5, lr}\n    cmp r0, #0\n    bne L_open_cfw_runtime_am022_552ae_0014\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am022_addr_005fa0a4\n    bl .\n    movs r0, #0\n    movs.w r1, #-1\n    str r0, [r1]\nL_open_cfw_runtime_am022_552ae_0012:\n    b L_open_cfw_runtime_am022_552ae_0012\nL_open_cfw_runtime_am022_552ae_0014:\n    ldr r3, [pc, #0x1a4]\n    ldr r3, [r3]\n    cmp r3, #0\n    bne L_open_cfw_runtime_am022_552ae_002a\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am022_addr_005fa0a4\n    bl .\n    movs r0, #0\n    movs.w r1, #-1\n    str r0, [r1]\nL_open_cfw_runtime_am022_552ae_0028:\n    b L_open_cfw_runtime_am022_552ae_0028\nL_open_cfw_runtime_am022_552ae_002a:\n    ldr.w r3, [pc, #0x958]\n    orrs r1, r1, #0x80000000\n    ldr r4, [r3]\n    str r1, [r4, #0x18]\n    ldr r1, [r0, #4]\n    ldr r4, [r3]\n    str r1, [r4, #0x1c]\n    ldr r4, [r1, #8]\n    ldr r5, [r3]\n    str r4, [r5, #0x20]\n    ldr r4, [r3]\n    adds r4, #0x18\n    ldr r5, [r1, #8]\n    str r4, [r5, #4]\n    ldr r4, [r3]\n    adds r4, #0x18\n    str r4, [r1, #8]\n    ldr r1, [r3]\n    str r0, [r1, #0x28]\n    ldr r1, [r0]\n    adds r1, r1, #1\n    str r1, [r0]\n    movs r1, #1\n    movs r0, r2\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am022_addr_00455fa8\n    bl .\n    pop {r0, r4, r5, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM022_55320_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am022_55320(void)
{
    __asm__ volatile(
        "    push {r4, r5, r6, lr}\n    movs r3, r1\n    cmp r0, #0\n    bne L_open_cfw_runtime_am022_55320_0016\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am022_addr_005fa0a4\n    bl .\n    movs r0, #0\n    movs.w r1, #-1\n    str r0, [r1]\nL_open_cfw_runtime_am022_55320_0014:\n    b L_open_cfw_runtime_am022_55320_0014\nL_open_cfw_runtime_am022_55320_0016:\n    ldr r1, [r0, #4]\n    ldr.w r4, [pc, #0x8f8]\n    ldr r5, [r4]\n    str r1, [r5, #0x1c]\n    ldr r5, [r1, #8]\n    ldr r6, [r4]\n    str r5, [r6, #0x20]\n    ldr r5, [r4]\n    adds r5, #0x18\n    ldr r6, [r1, #8]\n    str r5, [r6, #4]\n    ldr r5, [r4]\n    adds r5, #0x18\n    str r5, [r1, #8]\n    ldr r1, [r4]\n    str r0, [r1, #0x28]\n    ldr r1, [r0]\n    adds r1, r1, #1\n    str r1, [r0]\n    cmp r2, #0\n    beq L_open_cfw_runtime_am022_55320_0046\n    movs.w r3, #-1\nL_open_cfw_runtime_am022_55320_0046:\n    movs r1, r2\n    movs r0, r3\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am022_addr_00455fa8\n    bl .\n    pop {r4, r5, r6, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM022_55648_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am022_55648(void)
{
    __asm__ volatile(
        "    movs r2, #1\n    movs r0, #1\n    ldr r1, [pc, #0x158]\n    ldr r1, [r1]\n    cmp r1, #0\n    beq L_open_cfw_runtime_am022_55648_0010\n    movs r0, #0\n    b L_open_cfw_runtime_am022_55648_0040\nL_open_cfw_runtime_am022_55648_0010:\n    ldr.w r1, [pc, #0x3b8]\n    ldr r1, [r1]\n    cmp r1, #0\n    beq L_open_cfw_runtime_am022_55648_001e\n    movs r0, #0\n    b L_open_cfw_runtime_am022_55648_0040\nL_open_cfw_runtime_am022_55648_001e:\n    ldr.w r1, [pc, #0x3b0]\n    ldr r1, [r1]\n    cmp r1, #0\n    beq L_open_cfw_runtime_am022_55648_002c\n    movs r0, #0\n    b L_open_cfw_runtime_am022_55648_0040\nL_open_cfw_runtime_am022_55648_002c:\n    ldr.w r1, [pc, #0x9c4]\n    ldr r1, [r1]\n    ldr.w r3, [pc, #0x9c4]\n    ldr r3, [r3]\n    subs r2, r3, r2\n    cmp r1, r2\n    bne L_open_cfw_runtime_am022_55648_0040\n    movs r0, #2\nL_open_cfw_runtime_am022_55648_0040:\n    uxtb r0, r0\n    bx lr\n"
    );
}
#endif

#if defined(OPEN_CFW_AM022_556E0_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am022_556e0(void)
{
    __asm__ volatile(
        "    push {r3, r4, r5, lr}\n    b L_open_cfw_runtime_am022_556e0_0030\nL_open_cfw_runtime_am022_556e0_0004:\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am022_addr_004420d0\n    bl .\n    ldr.w r0, [pc, #0x960]\n    ldr r0, [r0, #0xc]\n    ldr r4, [r0, #0xc]\n    adds r0, r4, #4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am022_addr_004560e8\n    bl .\n    ldr.w r0, [pc, #0x948]\n    ldr r1, [r0]\n    subs r1, r1, #1\n    str r1, [r0]\n    ldr r0, [r5]\n    subs r0, r0, #1\n    str r0, [r5]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am022_addr_004420e8\n    bl .\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am022_addr_00455836\n    bl .\nL_open_cfw_runtime_am022_556e0_0030:\n    ldr.w r5, [pc, #0x944]\n    ldr r0, [r5]\n    cmp r0, #0\n    bne L_open_cfw_runtime_am022_556e0_0004\n    pop {r0, r4, r5, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM022_557B0_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am022_557b0(void)
{
    __asm__ volatile(
        "    push.w {r3, r4, r5, r6, r7, r8, sb, lr}\n    movs r6, r0\n    movs r4, r1\n    movs r7, r2\n    movs r5, #0\n    ldr r0, [r4]\n    cmp r0, #0\n    beq L_open_cfw_runtime_am022_557b0_006a\n    movs r0, r4\n    ldr r1, [r0, #4]\n    ldr r1, [r1, #4]\n    str r1, [r0, #4]\n    ldr r1, [r0, #4]\n    adds.w r2, r0, #8\n    cmp r1, r2\n    bne L_open_cfw_runtime_am022_557b0_002a\n    ldr r1, [r0, #4]\n    ldr r1, [r1, #4]\n    str r1, [r0, #4]\nL_open_cfw_runtime_am022_557b0_002a:\n    ldr r0, [r0, #4]\n    ldr.w r8, [r0, #0xc]\nL_open_cfw_runtime_am022_557b0_0030:\n    movs r0, r4\n    ldr r1, [r0, #4]\n    ldr r1, [r1, #4]\n    str r1, [r0, #4]\n    ldr r1, [r0, #4]\n    adds.w r2, r0, #8\n    cmp r1, r2\n    bne L_open_cfw_runtime_am022_557b0_0048\n    ldr r1, [r0, #4]\n    ldr r1, [r1, #4]\n    str r1, [r0, #4]\nL_open_cfw_runtime_am022_557b0_0048:\n    ldr r0, [r0, #4]\n    ldr.w sb, [r0, #0xc]\n    movs r3, r7\n    uxtb r3, r3\n    movs r2, #1\n    movs r0, #0x24\n    mul r0, r0, r5\n    add.w r1, r6, r0\n    mov r0, sb\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am022_addr_00455728\n    bl .\n    adds r5, r5, #1\n    cmp sb, r8\n    bne L_open_cfw_runtime_am022_557b0_0030\nL_open_cfw_runtime_am022_557b0_006a:\n    movs r0, r5\n    pop.w {r1, r4, r5, r6, r7, r8, sb, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM022_558CC_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am022_558cc(void)
{
    __asm__ volatile(
        "    b.w #0x7b7018\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n"
    );
}
#endif

#if defined(OPEN_CFW_AM022_55A1C_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am022_55a1c(void)
{
    __asm__ volatile(
        "    b.w #0x7b709c\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n"
    );
}
#endif

#if defined(OPEN_CFW_AM022_55AFC_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am022_55afc(void)
{
    __asm__ volatile(
        "    push {r3, r4, r5, r6, r7, lr}\n    movs r4, r0\n    movs r5, r1\n    movs r6, r2\n    cmp r4, #0\n    beq L_open_cfw_runtime_am022_55afc_001a\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am022_addr_005fa0a4\n    bl .\n    movs r0, #0\n    movs.w r1, #-1\n    str r0, [r1]\nL_open_cfw_runtime_am022_55afc_0018:\n    b L_open_cfw_runtime_am022_55afc_0018\nL_open_cfw_runtime_am022_55afc_001a:\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am022_addr_004420d0\n    bl .\n    ldr.w r7, [pc, #0x540]\n    ldr r0, [r7]\n    add.w r0, r0, r4, lsl #2\n    ldr r0, [r0, #0x68]\n    cmp r0, #0\n    bne L_open_cfw_runtime_am022_55afc_0048\n    movs r0, #1\n    ldr r1, [r7]\n    add r1, r4\n    strb.w r0, [r1, #0x6c]\n    cmp r6, #0\n    beq L_open_cfw_runtime_am022_55afc_0048\n    movs r1, #1\n    movs r0, r6\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am022_addr_00455fa8\n    bl .\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am022_addr_004420bc\n    bl .\nL_open_cfw_runtime_am022_55afc_0048:\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am022_addr_004420e8\n    bl .\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am022_addr_004420d0\n    bl .\n    ldr r0, [r7]\n    add.w r0, r0, r4, lsl #2\n    ldr r6, [r0, #0x68]\n    cmp r6, #0\n    beq L_open_cfw_runtime_am022_55afc_0076\n    cmp r5, #0\n    beq L_open_cfw_runtime_am022_55afc_006c\n    movs r0, #0\n    ldr r1, [r7]\n    add.w r1, r1, r4, lsl #2\n    str r0, [r1, #0x68]\n    b L_open_cfw_runtime_am022_55afc_0076\nL_open_cfw_runtime_am022_55afc_006c:\n    subs r0, r6, #1\n    ldr r1, [r7]\n    add.w r1, r1, r4, lsl #2\n    str r0, [r1, #0x68]\nL_open_cfw_runtime_am022_55afc_0076:\n    movs r0, #0\n    ldr r1, [r7]\n    add r1, r4\n    strb.w r0, [r1, #0x6c]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am022_addr_004420e8\n    bl .\n    movs r0, r6\n    pop {r1, r4, r5, r6, r7, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM022_55F5E_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am022_55f5e(void)
{
    __asm__ volatile(
        "    push {r3, r4, r5, lr}\n    movs r5, r0\n    movs r4, r1\n    cmp r4, #0\n    beq L_open_cfw_runtime_am022_55f5e_0018\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am022_addr_005fa0a4\n    bl .\n    movs r0, #0\n    movs.w r1, #-1\n    str r0, [r1]\nL_open_cfw_runtime_am022_55f5e_0016:\n    b L_open_cfw_runtime_am022_55f5e_0016\nL_open_cfw_runtime_am022_55f5e_0018:\n    cmp r5, #0\n    bne L_open_cfw_runtime_am022_55f5e_0022\n    ldr r0, [pc, #0xe0]\n    ldr r5, [r0]\n    b L_open_cfw_runtime_am022_55f5e_0022\nL_open_cfw_runtime_am022_55f5e_0022:\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am022_addr_004420d0\n    bl .\n    add.w r0, r5, r4\n    ldrb.w r0, [r0, #0x6c]\n    cmp r0, #2\n    bne L_open_cfw_runtime_am022_55f5e_0040\n    movs r0, #0\n    add.w r1, r5, r4\n    strb.w r0, [r1, #0x6c]\n    movs r4, #1\n    b L_open_cfw_runtime_am022_55f5e_0042\nL_open_cfw_runtime_am022_55f5e_0040:\n    movs r4, #0\nL_open_cfw_runtime_am022_55f5e_0042:\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am022_addr_004420e8\n    bl .\n    movs r0, r4\n    pop {r1, r4, r5, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM022_5601E_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am022_5601e(void)
{
    __asm__ volatile(
        "    ldr r0, [pc, #0x3c]\n    ldr r0, [r0]\n    ldr r0, [r0, #0x30]\n    bx lr\n"
    );
}
#endif

#if defined(OPEN_CFW_AM022_56026_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am022_56026(void)
{
    __asm__ volatile(
        "    ldr r0, [pc, #0x34]\n    ldr r0, [r0]\n    ldr r0, [r0, #0x54]\n    bx lr\n"
    );
}
#endif

#if defined(OPEN_CFW_AM022_5602E_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am022_5602e(void)
{
    __asm__ volatile(
        "    ldr r0, [pc, #0x2c]\n    ldr r0, [r0]\n    adds r0, #0x34\n    bx lr\n"
    );
}
#endif

#if defined(OPEN_CFW_AM022_56358_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am022_56358(void)
{
    __asm__ volatile(
        "    movs r1, r0\n    sxth r1, r1\n    cmp r1, #0\n    bmi L_open_cfw_runtime_am022_56358_001a\n    movs r2, #1\n    ands r1, r0, #0x1f\n    lsls r2, r1\n    ldr r1, [pc, #0x1f0]\n    sxth r0, r0\n    lsrs r0, r0, #5\n    str.w r2, [r1, r0, lsl #2]\nL_open_cfw_runtime_am022_56358_001a:\n    bx lr\n"
    );
}
#endif

#if defined(OPEN_CFW_AM022_56374_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am022_56374(void)
{
    __asm__ volatile(
        "    movs r1, r0\n    sxth r1, r1\n    cmp r1, #0\n    bmi L_open_cfw_runtime_am022_56374_001a\n    movs r2, #1\n    ands r1, r0, #0x1f\n    lsls r2, r1\n    ldr r1, [pc, #0x1d8]\n    sxth r0, r0\n    lsrs r0, r0, #5\n    str.w r2, [r1, r0, lsl #2]\nL_open_cfw_runtime_am022_56374_001a:\n    bx lr\n"
    );
}
#endif

#if defined(OPEN_CFW_AM022_56390_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am022_56390(void)
{
    __asm__ volatile(
        "    movs r2, r0\n    sxth r2, r2\n    cmp r2, #0\n    bmi L_open_cfw_runtime_am022_56390_0012\n    lsls r1, r1, #4\n    ldr r2, [pc, #0x1c8]\n    sxth r0, r0\n    strb r1, [r2, r0]\n    b L_open_cfw_runtime_am022_56390_0022\nL_open_cfw_runtime_am022_56390_0012:\n    lsls r1, r1, #4\n    ldr r2, [pc, #0x1c0]\n    sxth r0, r0\n    ands r0, r0, #0xf\n    add r0, r2\n    strb r1, [r0, #-0x4]\nL_open_cfw_runtime_am022_56390_0022:\n    bx lr\n"
    );
}
#endif

#if defined(OPEN_CFW_AM022_563B4_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am022_563b4(void)
{
    __asm__ volatile(
        "    push {r3, r4, r5, r6, r7, lr}\n    movs r0, #0\n    movs r4, #0\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am022_addr_0048d654\n    bl .\n    ldr r3, [pc, #0x1ac]\n    ldr r1, [r3]\n    cmp r0, r1\n    bhs L_open_cfw_runtime_am022_563b4_001e\n    movs.w r1, #-1\n    ldr r2, [r3]\n    subs r1, r1, r2\n    adds r1, r0, r1\n    b L_open_cfw_runtime_am022_563b4_0022\nL_open_cfw_runtime_am022_563b4_001e:\n    ldr r1, [r3]\n    subs r1, r0, r1\nL_open_cfw_runtime_am022_563b4_0022:\n    ldr r6, [pc, #0x198]\n    ldr r2, [r6]\n    udiv r5, r1, r2\n    ldr r2, [r6]\n    udiv r7, r1, r2\n    ldr r2, [r6]\n    mls r1, r2, r7, r1\n    subs r0, r0, r1\n    str r0, [r3]\n    ldr r0, [r6]\n    subs r1, r0, r1\n    movs r0, #0\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am022_addr_0048d670\n    bl .\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am022_addr_005fa0a4\n    bl .\n    b L_open_cfw_runtime_am022_563b4_004c\nL_open_cfw_runtime_am022_563b4_004a:\n    movs r4, #1\nL_open_cfw_runtime_am022_563b4_004c:\n    movs r0, r5\n    subs r5, r0, #1\n    cmp r0, #0\n    beq L_open_cfw_runtime_am022_563b4_005e\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am022_addr_0045504c\n    bl .\n    cmp r0, #0\n    bne L_open_cfw_runtime_am022_563b4_004a\n    b L_open_cfw_runtime_am022_563b4_004c\nL_open_cfw_runtime_am022_563b4_005e:\n    cmp r4, #0\n    beq L_open_cfw_runtime_am022_563b4_006a\n    movs.w r0, #0x10000000\n    ldr r1, [pc, #0x158]\n    str r0, [r1]\nL_open_cfw_runtime_am022_563b4_006a:\n    movs r0, #0\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am022_addr_005fa0ba\n    bl .\n    pop {r0, r4, r5, r6, r7, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM022_56426_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am022_56426(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    movs r0, #0\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am022_addr_0048d6f0\n    bl .\n    lsls r0, r0, #0x1f\n    bpl L_open_cfw_runtime_am022_56426_0016\n    movs r0, #1\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am022_addr_0048d6e6\n    bl .\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am022_563b4\n    bl .\nL_open_cfw_runtime_am022_56426_0016:\n    pop {r0, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM022_5643E_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am022_5643e(void)
{
    __asm__ volatile(
        "    push {r3, r4, r5, lr}\n    ldr r5, [pc, #0x12c]\n    movs r0, #0x20\n    str r0, [r5]\n    movs.w r0, #-1\n    ldr r1, [r5]\n    udiv r0, r0, r1\n    subs r0, r0, #4\n    ldr r1, [pc, #0x124]\n    str r0, [r1]\n    movs r0, #1\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am022_addr_0048d6dc\n    bl .\n    movs r1, #0xff\n    movs r0, #0x20\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am022_56390\n    bl .\n    movs r0, #0x20\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am022_56358\n    bl .\n    movs.w r0, #-0x80000000\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am022_addr_0048d588\n    bl .\n    movs r4, r0\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am022_addr_0048d654\n    bl .\n    ldr r1, [pc, #0xf0]\n    str r0, [r1]\n    ldr r1, [r5]\n    movs r0, #0\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am022_addr_0048d670\n    bl .\n    ldr r0, [pc, #0xf4]\n    ands r4, r0\n    movw r0, #0x103\n    orrs r4, r0\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am022_addr_0048d588\n    bl .\n    pop {r0, r4, r5, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM022_56498_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am022_56498(void)
{
    __asm__ volatile(
        "    push.w {r4, r5, r6, r7, r8, lr}\n    movs r4, r0\n    ldr r0, [pc, #0xd8]\n    ldr r1, [r0]\n    cmp r1, r4\n    bhs L_open_cfw_runtime_am022_56498_0010\n    ldr r4, [r0]\nL_open_cfw_runtime_am022_56498_0010:\n    cpsid i\n    dsb sy\n    isb sy\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am022_55648\n    bl .\n    cmp r0, #0\n    bne L_open_cfw_runtime_am022_56498_0026\n    cpsie i\n    b L_open_cfw_runtime_am022_56498_00c0\nL_open_cfw_runtime_am022_56498_0026:\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am022_addr_0048d654\n    bl .\n    ldr r5, [pc, #0xa8]\n    ldr r1, [r5]\n    cmp r0, r1\n    bhs L_open_cfw_runtime_am022_56498_003e\n    movs.w r2, #-1\n    ldr r1, [r5]\n    subs r2, r2, r1\n    adds r0, r0, r2\n    b L_open_cfw_runtime_am022_56498_0042\nL_open_cfw_runtime_am022_56498_003e:\n    ldr r1, [r5]\n    subs r0, r0, r1\nL_open_cfw_runtime_am022_56498_0042:\n    ldr r6, [pc, #0x94]\n    ldr r1, [r6]\n    muls r1, r4, r1\n    subs r1, r1, r0\n    movs r0, #0\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am022_addr_0048d670\n    bl .\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am022_addr_0046d836\n    bl .\n    cmp r0, #0\n    beq L_open_cfw_runtime_am022_56498_0064\n    dsb sy\n    wfi\n    isb sy\nL_open_cfw_runtime_am022_56498_0064:\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am022_addr_0046d856\n    bl .\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am022_addr_0048d654\n    bl .\n    ldr r1, [r5]\n    cmp r0, r1\n    bhs L_open_cfw_runtime_am022_56498_0080\n    movs.w r7, #-1\n    ldr r1, [r5]\n    subs r7, r7, r1\n    adds r7, r0, r7\n    b L_open_cfw_runtime_am022_56498_0084\nL_open_cfw_runtime_am022_56498_0080:\n    ldr r7, [r5]\n    subs r7, r0, r7\nL_open_cfw_runtime_am022_56498_0084:\n    ldr r1, [r6]\n    udiv r8, r7, r1\n    ldr r1, [r6]\n    udiv r2, r7, r1\n    ldr r1, [r6]\n    mls r7, r1, r2, r7\n    subs r0, r0, r7\n    str r0, [r5]\n    movs r0, #1\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am022_addr_0048d6e6\n    bl .\n    movs r0, #0x20\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am022_56374\n    bl .\n    ldr r0, [r6]\n    subs r7, r0, r7\n    movs r1, r7\n    movs r0, #0\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am022_addr_0048d670\n    bl .\n    cmp r4, r8\n    bhs L_open_cfw_runtime_am022_56498_00b8\n    mov r8, r4\nL_open_cfw_runtime_am022_56498_00b8:\n    mov r0, r8\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am022_54fd8\n    bl .\n    cpsie i\nL_open_cfw_runtime_am022_56498_00c0:\n    pop.w {r4, r5, r6, r7, r8, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM022_56580_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am022_56580(void)
{
    __asm__ volatile(
        "    push.w {r3, r4, r5, r6, r7, r8, sb, lr}\n    movs r4, r0\n    ldr.w r8, [pc, #0x624]\n    ldr.w sb, [pc, #0x624]\n    mov r0, r8\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am022_addr_0044a43c\n    bl .\n    movs r7, r0\n    mov r0, sb\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am022_addr_0044a43c\n    bl .\n    movs r5, r0\n    cmp r4, #0\n    bne L_open_cfw_runtime_am022_56580_0026\n    movs r0, #0\n    b L_open_cfw_runtime_am022_56580_0082\nL_open_cfw_runtime_am022_56580_0026:\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am022_addr_0044a43c\n    bl .\n    movs r6, r0\n    adds r0, r5, r7\n    cmp r0, r6\n    bhs L_open_cfw_runtime_am022_56580_0054\n    movs r2, r7\n    mov r1, r8\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am022_addr_0044b610\n    bl .\n    cmp r0, #0\n    bne L_open_cfw_runtime_am022_56580_0054\n    mov r1, sb\n    add.w r0, r4, r6\n    rsbs r2, r5, #0\n    add r0, r2\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am022_addr_0046cacc\n    bl .\n    cmp r0, #0\n    beq L_open_cfw_runtime_am022_56580_0058\nL_open_cfw_runtime_am022_56580_0054:\n    movs r0, #0\n    b L_open_cfw_runtime_am022_56580_0082\nL_open_cfw_runtime_am022_56580_0058:\n    movs r0, #0\n    str r0, [sp]\n    movs r2, #0xa\n    mov r1, sp\n    add.w r0, r4, r7\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am022_addr_0048d874\n    bl .\n    cmp r0, #0\n    beq L_open_cfw_runtime_am022_56580_007e\n    ldr r0, [sp]\n    add.w r1, r4, r6\n    rsbs r5, r5, #0\n    add r1, r5\n    cmp r0, r1\n    bne L_open_cfw_runtime_am022_56580_007e\n    movs r0, #1\n    b L_open_cfw_runtime_am022_56580_0080\nL_open_cfw_runtime_am022_56580_007e:\n    movs r0, #0\nL_open_cfw_runtime_am022_56580_0080:\n    uxtb r0, r0\nL_open_cfw_runtime_am022_56580_0082:\n    pop.w {r1, r4, r5, r6, r7, r8, sb, pc}\n"
    );
}
#endif
