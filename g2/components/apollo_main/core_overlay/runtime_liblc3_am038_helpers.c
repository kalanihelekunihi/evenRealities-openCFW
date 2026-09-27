/*
 * SPDX-License-Identifier: MIT
 *
 * Source-owned exact helpers from the AM-038 retained island.
 */

#if defined(OPEN_CFW_AM038_8AA54_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am038_8aa54(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    movs r2, r1\n    movs r1, #0\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am038_addr_00454746\n    bl .\n    pop {r0, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM038_8AA60_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am038_8aa60(void)
{
    __asm__ volatile(
        "    push {r4, lr}\n    ldr.w r4, [pc, #0xcc0]\n    adds.w r0, r4, #0xc8\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am038_8aa80\n    bl .\n    adds.w r0, r4, #0xe8\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am038_8aa80\n    bl .\n    adds.w r0, r4, #0x108\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am038_8aa80\n    bl .\n    pop {r4, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM038_8AA80_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am038_8aa80(void)
{
    __asm__ volatile(
        "    push {r5, r6, r7, lr}\n    ldr.w r1, [pc, #0xa9c]\n    str r1, [sp, #8]\n    movs r1, #0\n    str r1, [sp, #4]\n    movs r1, #0\n    str r1, [sp]\n    ldr.w r3, [pc, #0xa90]\n    ldr.w r2, [pc, #0xa90]\n    ldr.w r1, [pc, #0xc8c]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am038_8aaa2\n    bl .\n    pop {r0, r1, r2, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM038_8AAA2_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am038_8aaa2(void)
{
    __asm__ volatile(
        "    push.w {r4, r5, r6, r7, r8, sb, sl, lr}\n    movs r4, r0\n    movs r5, r1\n    movs r6, r2\n    movs r7, r3\n    ldr.w r8, [sp, #0x20]\n    ldr.w sb, [sp, #0x24]\n    ldr.w sl, [sp, #0x28]\n    movs r1, #0x20\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am038_8aa54\n    bl .\n    str r5, [r4]\n    str r6, [r4, #4]\n    str r7, [r4, #8]\n    str.w r8, [r4, #0xc]\n    str.w sb, [r4, #0x10]\n    str.w sl, [r4, #0x14]\n    pop.w {r4, r5, r6, r7, r8, sb, sl, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM038_8AAD8_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am038_8aad8(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    movs r2, r1\n    uxtb r2, r2\n    movs r1, r0\n    ldr.w r0, [pc, #0xc4c]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am038_8aaea\n    bl .\n    pop {r1, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM038_8AAEA_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am038_8aaea(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    movs r3, r0\n    movs r0, r1\n    movs r1, r2\n    ldr r2, [r3, #0x14]\n    cmp r2, #0\n    beq L_open_cfw_runtime_am038_8aaea_0016\n    uxtb r1, r1\n    ldr r2, [r3, #0x14]\n    blx r2\n    b L_open_cfw_runtime_am038_8aaea_0018\nL_open_cfw_runtime_am038_8aaea_0016:\n    movs r0, #0\nL_open_cfw_runtime_am038_8aaea_0018:\n    pop {r1, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM038_8AB04_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am038_8ab04(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    movs r2, r1\n    uxtb r2, r2\n    movs r1, r0\n    ldr.w r0, [pc, #0xc20]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am038_8ab16\n    bl .\n    pop {r1, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM038_8AB16_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am038_8ab16(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    movs r3, r0\n    movs r0, r1\n    movs r1, r2\n    ldr r2, [r3, #8]\n    cmp r2, #0\n    beq L_open_cfw_runtime_am038_8ab16_0016\n    uxtb r1, r1\n    ldr r2, [r3, #8]\n    blx r2\n    b L_open_cfw_runtime_am038_8ab16_0018\nL_open_cfw_runtime_am038_8ab16_0016:\n    movs r0, #0\nL_open_cfw_runtime_am038_8ab16_0018:\n    pop {r1, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM038_8AB30_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am038_8ab30(void)
{
    __asm__ volatile(
        "    push {r3, r4, r5, lr}\n    sub sp, #0x10\n    movs r4, r0\n    cmp r4, #0\n    bne L_open_cfw_runtime_am038_8ab30_0036\n    ldr.w r0, [pc, #0x9f0]\n    str r0, [sp, #8]\n    ldr.w r0, [pc, #0x9ec]\n    str r0, [sp, #4]\n    ldr.w r0, [pc, #0x9ec]\n    str r0, [sp]\n    ldr.w r3, [pc, #0x9e8]\n    movs r2, #0x79\n    ldr.w r1, [pc, #0xbe0]\n    movs r0, #3\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am038_addr_0044d25c\n    bl .\nL_open_cfw_runtime_am038_8ab30_002c:\n    movs r0, #0\n    movs.w r1, #-1\n    str r0, [r1]\n    b L_open_cfw_runtime_am038_8ab30_002c\nL_open_cfw_runtime_am038_8ab30_0036:\n    ldr r0, [r4, #0x18]\n    cmp r0, #0\n    bne L_open_cfw_runtime_am038_8ab30_0068\n    ldr.w r0, [pc, #0x9bc]\n    str r0, [sp, #8]\n    ldr.w r0, [pc, #0x9c8]\n    str r0, [sp, #4]\n    ldr.w r0, [pc, #0x9b8]\n    str r0, [sp]\n    ldr.w r3, [pc, #0x9b8]\n    movs r2, #0x7a\n    ldr.w r1, [pc, #0xbac]\n    movs r0, #3\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am038_addr_0044d25c\n    bl .\nL_open_cfw_runtime_am038_8ab30_005e:\n    movs r0, #0\n    movs.w r1, #-1\n    str r0, [r1]\n    b L_open_cfw_runtime_am038_8ab30_005e\nL_open_cfw_runtime_am038_8ab30_0068:\n    ldr r5, [r4, #0x18]\n    ldr r0, [r5, #0xc]\n    cmp r0, #0\n    beq L_open_cfw_runtime_am038_8ab30_0084\n    cmp r1, #0\n    bne L_open_cfw_runtime_am038_8ab30_007e\n    mov r1, sp\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am038_8b8d8\n    bl .\n    mov r1, sp\nL_open_cfw_runtime_am038_8ab30_007e:\n    movs r0, r4\n    ldr r2, [r5, #0xc]\n    blx r2\nL_open_cfw_runtime_am038_8ab30_0084:\n    add sp, #0x14\n    pop {r4, r5, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM038_8ABB8_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am038_8abb8(void)
{
    __asm__ volatile(
        "    push {r3, r4, r5, lr}\n    sub sp, #0x10\n    movs r4, r0\n    cmp r4, #0\n    bne L_open_cfw_runtime_am038_8abb8_0036\n    ldr.w r0, [pc, #0x968]\n    str r0, [sp, #8]\n    ldr.w r0, [pc, #0x964]\n    str r0, [sp, #4]\n    ldr.w r0, [pc, #0x964]\n    str r0, [sp]\n    ldr.w r3, [pc, #0xb54]\n    movs r2, #0x8f\n    ldr.w r1, [pc, #0xb58]\n    movs r0, #3\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am038_addr_0044d25c\n    bl .\nL_open_cfw_runtime_am038_8abb8_002c:\n    movs r0, #0\n    movs.w r1, #-1\n    str r0, [r1]\n    b L_open_cfw_runtime_am038_8abb8_002c\nL_open_cfw_runtime_am038_8abb8_0036:\n    ldr r0, [r4, #0x18]\n    cmp r0, #0\n    bne L_open_cfw_runtime_am038_8abb8_0068\n    ldr.w r0, [pc, #0x934]\n    str r0, [sp, #8]\n    ldr.w r0, [pc, #0x940]\n    str r0, [sp, #4]\n    ldr.w r0, [pc, #0x930]\n    str r0, [sp]\n    ldr.w r3, [pc, #0xb24]\n    movs r2, #0x90\n    ldr.w r1, [pc, #0xb24]\n    movs r0, #3\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am038_addr_0044d25c\n    bl .\nL_open_cfw_runtime_am038_8abb8_005e:\n    movs r0, #0\n    movs.w r1, #-1\n    str r0, [r1]\n    b L_open_cfw_runtime_am038_8abb8_005e\nL_open_cfw_runtime_am038_8abb8_0068:\n    ldr r5, [r4, #0x18]\n    ldr r0, [r5, #0x10]\n    cmp r0, #0\n    beq L_open_cfw_runtime_am038_8abb8_0084\n    cmp r1, #0\n    bne L_open_cfw_runtime_am038_8abb8_007e\n    mov r1, sp\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am038_8b8d8\n    bl .\n    mov r1, sp\nL_open_cfw_runtime_am038_8abb8_007e:\n    movs r0, r4\n    ldr r2, [r5, #0x10]\n    blx r2\nL_open_cfw_runtime_am038_8abb8_0084:\n    add sp, #0x14\n    pop {r4, r5, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM038_8AC40_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am038_8ac40(void)
{
    __asm__ volatile(
        "    push.w {r3, r4, r5, r6, r7, r8, sb, lr}\n    sub sp, #0x20\n    movs r4, r0\n    movs r5, r1\n    cmp r4, #0\n    bne L_open_cfw_runtime_am038_8ac40_003a\n    ldr.w r0, [pc, #0x8dc]\n    str r0, [sp, #8]\n    ldr.w r0, [pc, #0x8d8]\n    str r0, [sp, #4]\n    ldr.w r0, [pc, #0x8d8]\n    str r0, [sp]\n    ldr.w r3, [pc, #0xad4]\n    movs r2, #0xa5\n    ldr.w r1, [pc, #0xacc]\n    movs r0, #3\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am038_addr_0044d25c\n    bl .\nL_open_cfw_runtime_am038_8ac40_0030:\n    movs r0, #0\n    movs.w r1, #-1\n    str r0, [r1]\n    b L_open_cfw_runtime_am038_8ac40_0030\nL_open_cfw_runtime_am038_8ac40_003a:\n    ldr r2, [r4, #0x18]\n    ldr r0, [r2, #0x18]\n    cmp r0, #0\n    beq L_open_cfw_runtime_am038_8ac40_004c\n    movs r1, r5\n    movs r0, r4\n    ldr r2, [r2, #0x18]\n    blx r2\n    b L_open_cfw_runtime_am038_8ac40_00fc\nL_open_cfw_runtime_am038_8ac40_004c:\n    movs r6, r4\n    ldr r7, [r6, #8]\n    uxth r7, r7\n    cmp r5, #0\n    bne L_open_cfw_runtime_am038_8ac40_0078\n    movs r2, #0\n    movs r1, #0\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am038_8b2aa\n    bl .\n    ldr r1, [r6, #4]\n    lsrs r1, r1, #0x10\n    mul r7, r7, r1\n    movs r1, r7\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am038_8aa54\n    bl .\n    movs r1, r5\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am038_8abb8\n    bl .\n    b L_open_cfw_runtime_am038_8ac40_00fc\nL_open_cfw_runtime_am038_8ac40_0078:\n    movs r0, #0\n    str r0, [sp, #0x10]\n    movs r0, #0\n    str r0, [sp, #0x14]\n    ldr r0, [r4, #4]\n    uxth r0, r0\n    subs r0, r0, #1\n    str r0, [sp, #0x18]\n    ldr r0, [r4, #4]\n    lsrs r0, r0, #0x10\n    subs r0, r0, #1\n    str r0, [sp, #0x1c]\n    add r2, sp, #0x10\n    movs r1, r5\n    mov r0, sp\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am038_addr_00450bcc\n    bl .\n    cmp r0, #0\n    beq L_open_cfw_runtime_am038_8ac40_00fc\n    mov r0, sp\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am038_addr_00451598\n    bl .\n    cmp r0, #1\n    blt L_open_cfw_runtime_am038_8ac40_00fc\n    mov r0, sp\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am038_addr_004515a4\n    bl .\n    cmp r0, #1\n    blt L_open_cfw_runtime_am038_8ac40_00fc\n    ldr r2, [sp, #4]\n    ldr r1, [sp]\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am038_8b2aa\n    bl .\n    mov r8, r0\n    ldr r0, [r6]\n    lsrs r0, r0, #8\n    uxtb r0, r0\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am038_addr_00440f44\n    bl .\n    movs r6, r0\n    mov r0, sp\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am038_addr_00451598\n    bl .\n    uxtb r6, r6\n    mul r6, r6, r0\n    adds r6, r6, #7\n    asrs r6, r6, #3\n    ldr.w sb, [sp, #4]\n    b L_open_cfw_runtime_am038_8ac40_00ee\nL_open_cfw_runtime_am038_8ac40_00e0:\n    movs r1, r6\n    mov r0, r8\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am038_8aa54\n    bl .\n    add r8, r7\n    adds.w sb, sb, #1\nL_open_cfw_runtime_am038_8ac40_00ee:\n    ldr r0, [sp, #0xc]\n    cmp r0, sb\n    bge L_open_cfw_runtime_am038_8ac40_00e0\n    movs r1, r5\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am038_8abb8\n    bl .\nL_open_cfw_runtime_am038_8ac40_00fc:\n    add sp, #0x24\n    pop.w {r4, r5, r6, r7, r8, sb, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM038_8AD42_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am038_8ad42(void)
{
    __asm__ volatile(
        "    push.w {r3, r4, r5, r6, r7, r8, sb, sl, fp, lr}\n    sub sp, #0x10\n    movs r6, r0\n    movs r4, r1\n    movs r7, r2\n    movs r5, r3\n    ldr.w ip, [r6, #0x18]\n    ldr.w r0, [ip, #0x1c]\n    cmp r0, #0\n    beq L_open_cfw_runtime_am038_8ad42_002a\n    movs r3, r5\n    movs r2, r7\n    movs r1, r4\n    movs r0, r6\n    ldr.w r4, [ip, #0x1c]\n    blx r4\n    b L_open_cfw_runtime_am038_8ad42_01b0\nL_open_cfw_runtime_am038_8ad42_002a:\n    ldr r0, [r6]\n    ubfx r0, r0, #8, #8\n    ldr r1, [r7]\n    ubfx r1, r1, #8, #8\n    cmp r0, r1\n    beq L_open_cfw_runtime_am038_8ad42_0070\n    ldr r0, [r7]\n    ubfx r0, r0, #8, #8\n    str r0, [sp, #0xc]\n    ldr r0, [r6]\n    ubfx r0, r0, #8, #8\n    str r0, [sp, #8]\n    ldr.w r0, [pc, #0xa18]\n    str r0, [sp, #4]\n    ldr.w r0, [pc, #0xa18]\n    str r0, [sp]\n    ldr.w r3, [pc, #0xa14]\n    movs r2, #0xeb\n    ldr.w r1, [pc, #0x994]\n    movs r0, #3\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am038_addr_0044d25c\n    bl .\nL_open_cfw_runtime_am038_8ad42_0066:\n    movs r0, #0\n    movs.w r1, #-1\n    str r0, [r1]\n    b L_open_cfw_runtime_am038_8ad42_0066\nL_open_cfw_runtime_am038_8ad42_0070:\n    cmp r4, #0\n    bne L_open_cfw_runtime_am038_8ad42_007e\n    ldr.w r8, [r6, #4]\n    uxth.w r8, r8\n    b L_open_cfw_runtime_am038_8ad42_0086\nL_open_cfw_runtime_am038_8ad42_007e:\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am038_addr_00451598\n    bl .\n    mov r8, r0\nL_open_cfw_runtime_am038_8ad42_0086:\n    cmp r4, #0\n    beq L_open_cfw_runtime_am038_8ad42_008e\n    cmp r5, #0\n    bne L_open_cfw_runtime_am038_8ad42_00e0\nL_open_cfw_runtime_am038_8ad42_008e:\n    ldr r0, [r6]\n    ubfx r0, r0, #8, #8\n    subs r0, r0, #7\n    cmp r0, #4\n    bhs L_open_cfw_runtime_am038_8ad42_00e0\n    ldr r0, [r6]\n    ubfx r0, r0, #8, #8\n    cmp r0, #7\n    bne L_open_cfw_runtime_am038_8ad42_00a8\n    movs r2, #2\n    b L_open_cfw_runtime_am038_8ad42_00d6\nL_open_cfw_runtime_am038_8ad42_00a8:\n    ldr r0, [r6]\n    ubfx r0, r0, #8, #8\n    cmp r0, #8\n    bne L_open_cfw_runtime_am038_8ad42_00b6\n    movs r2, #4\n    b L_open_cfw_runtime_am038_8ad42_00d6\nL_open_cfw_runtime_am038_8ad42_00b6:\n    ldr r0, [r6]\n    ubfx r0, r0, #8, #8\n    cmp r0, #9\n    bne L_open_cfw_runtime_am038_8ad42_00c4\n    movs r2, #0x10\n    b L_open_cfw_runtime_am038_8ad42_00d6\nL_open_cfw_runtime_am038_8ad42_00c4:\n    ldr r0, [r6]\n    ubfx r0, r0, #8, #8\n    cmp r0, #0xa\n    bne L_open_cfw_runtime_am038_8ad42_00d4\n    mov.w r2, #0x100\n    b L_open_cfw_runtime_am038_8ad42_00d6\nL_open_cfw_runtime_am038_8ad42_00d4:\n    movs r2, #0\nL_open_cfw_runtime_am038_8ad42_00d6:\n    lsls r2, r2, #2\n    ldr r1, [r7, #0x10]\n    ldr r0, [r6, #0x10]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am038_addr_00454738\n    bl .\nL_open_cfw_runtime_am038_8ad42_00e0:\n    cmp r5, #0\n    bne L_open_cfw_runtime_am038_8ad42_00ec\n    ldr r0, [r7, #4]\n    uxth r0, r0\n    cmp r8, r0\n    bne L_open_cfw_runtime_am038_8ad42_00fa\nL_open_cfw_runtime_am038_8ad42_00ec:\n    cmp r5, #0\n    beq L_open_cfw_runtime_am038_8ad42_0124\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am038_addr_00451598\n    bl .\n    cmp r8, r0\n    beq L_open_cfw_runtime_am038_8ad42_0124\nL_open_cfw_runtime_am038_8ad42_00fa:\n    ldr.w r0, [pc, #0x974]\n    str r0, [sp, #8]\n    adr r0, #0x2ec\n    str r0, [sp, #4]\n    ldr.w r0, [pc, #0x6ec]\n    str r0, [sp]\n    ldr.w r3, [pc, #0x960]\n    movs r2, #0xfa\n    ldr.w r1, [pc, #0x8e0]\n    movs r0, #3\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am038_addr_0044d25c\n    bl .\nL_open_cfw_runtime_am038_8ad42_011a:\n    movs r0, #0\n    movs.w r1, #-1\n    str r0, [r1]\n    b L_open_cfw_runtime_am038_8ad42_011a\nL_open_cfw_runtime_am038_8ad42_0124:\n    cmp r5, #0\n    beq L_open_cfw_runtime_am038_8ad42_0136\n    ldr r2, [r5, #4]\n    ldr r1, [r5]\n    movs r0, r7\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am038_8b2aa\n    bl .\n    movs r5, r0\n    b L_open_cfw_runtime_am038_8ad42_0142\nL_open_cfw_runtime_am038_8ad42_0136:\n    movs r2, #0\n    movs r1, #0\n    movs r0, r7\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am038_8b2aa\n    bl .\n    movs r5, r0\nL_open_cfw_runtime_am038_8ad42_0142:\n    cmp r4, #0\n    beq L_open_cfw_runtime_am038_8ad42_0154\n    ldr r2, [r4, #4]\n    ldr r1, [r4]\n    movs r0, r6\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am038_8b2aa\n    bl .\n    mov sb, r0\n    b L_open_cfw_runtime_am038_8ad42_0160\nL_open_cfw_runtime_am038_8ad42_0154:\n    movs r2, #0\n    movs r1, #0\n    movs r0, r6\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am038_8b2aa\n    bl .\n    mov sb, r0\nL_open_cfw_runtime_am038_8ad42_0160:\n    cmp r4, #0\n    beq L_open_cfw_runtime_am038_8ad42_016c\n    ldr.w sl, [r4, #4]\n    ldr r4, [r4, #0xc]\n    b L_open_cfw_runtime_am038_8ad42_0176\nL_open_cfw_runtime_am038_8ad42_016c:\n    movs.w sl, #0\n    ldr r4, [r6, #4]\n    lsrs r4, r4, #0x10\n    subs r4, r4, #1\nL_open_cfw_runtime_am038_8ad42_0176:\n    ldr.w fp, [r6, #8]\n    uxth.w fp, fp\n    ldr r7, [r7, #8]\n    uxth r7, r7\n    ldr r0, [r6]\n    lsrs r0, r0, #8\n    uxtb r0, r0\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am038_addr_00440f44\n    bl .\n    mul r8, r0, r8\n    adds.w r8, r8, #7\n    asrs.w r8, r8, #3\n    b L_open_cfw_runtime_am038_8ad42_01ac\nL_open_cfw_runtime_am038_8ad42_019a:\n    mov r2, r8\n    movs r1, r5\n    mov r0, sb\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am038_addr_00454738\n    bl .\n    add sb, fp\n    add r5, r7\n    adds.w sl, sl, #1\nL_open_cfw_runtime_am038_8ad42_01ac:\n    cmp r4, sl\n    bge L_open_cfw_runtime_am038_8ad42_019a\nL_open_cfw_runtime_am038_8ad42_01b0:\n    add sp, #0x14\n    pop.w {r4, r5, r6, r7, r8, sb, sl, fp, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM038_8AEF8_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am038_8aef8(void)
{
    __asm__ volatile(
        "    push.w {r0, r1, r2, r3, r4, r5, r6, r7, r8, lr}\n    movs r4, r0\n    movs r7, r1\n    mov r8, r2\n    movs r6, r3\n    cmp r4, #0\n    bne L_open_cfw_runtime_am038_8aef8_003e\n    ldr.w r0, [pc, #0x620]\n    str r0, [sp, #8]\n    ldr.w r0, [pc, #0x620]\n    str r0, [sp, #4]\n    ldr.w r0, [pc, #0x61c]\n    str r0, [sp]\n    ldr.w r3, [pc, #0x89c]\n    mov.w r2, #0x11e\n    ldr.w r1, [pc, #0x810]\n    movs r0, #3\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am038_addr_0044d25c\n    bl .\nL_open_cfw_runtime_am038_8aef8_0034:\n    movs r0, #0\n    movs.w r1, #-1\n    str r0, [r1]\n    b L_open_cfw_runtime_am038_8aef8_0034\nL_open_cfw_runtime_am038_8aef8_003e:\n    cmp r4, #0\n    bne L_open_cfw_runtime_am038_8aef8_0046\n    movs r0, #0\n    b L_open_cfw_runtime_am038_8aef8_00fc\nL_open_cfw_runtime_am038_8aef8_0046:\n    ldr r5, [sp, #0x28]\n    movs r1, #0x1c\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am038_8aa54\n    bl .\n    cmp r5, #0\n    bne L_open_cfw_runtime_am038_8aef8_0060\n    movs r1, r6\n    uxtb r1, r1\n    movs r0, r7\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am038_8aad8\n    bl .\n    movs r5, r0\nL_open_cfw_runtime_am038_8aef8_0060:\n    ldr r1, [sp, #0x30]\n    mul r0, r8, r5\n    cmp r1, r0\n    bhs L_open_cfw_runtime_am038_8aef8_0090\n    str r1, [sp, #8]\n    mul r8, r8, r5\n    str.w r8, [sp, #4]\n    ldr.w r0, [pc, #0x84c]\n    str r0, [sp]\n    ldr.w r3, [pc, #0x844]\n    movw r2, #0x125\n    ldr.w r1, [pc, #0x7b8]\n    movs r0, #2\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am038_addr_0044d25c\n    bl .\n    movs r0, #0\n    b L_open_cfw_runtime_am038_8aef8_00fc\nL_open_cfw_runtime_am038_8aef8_0090:\n    ldr r0, [sp, #0x2c]\n    movs r2, r4\n    ldr r3, [r2, #4]\n    bfi r3, r7, #0, #0x10\n    str r3, [r2, #4]\n    ldr r3, [r2, #4]\n    bfi r3, r8, #0x10, #0x10\n    str r3, [r2, #4]\n    movs r3, r6\n    uxtb r3, r3\n    ldr r7, [r2]\n    bfi r7, r3, #8, #8\n    str r7, [r2]\n    ldr r3, [r2, #8]\n    bfi r3, r5, #0, #0x10\n    str r3, [r2, #8]\n    ldr r3, [r2]\n    uxth r3, r3\n    str r3, [r2]\n    movs r3, #0x19\n    ldr r5, [r2]\n    bfi r5, r3, #0, #8\n    str r5, [r2]\n    str r0, [r4, #0x10]\n    str r0, [r4, #0x14]\n    ldr.w r2, [pc, #0x768]\n    str r2, [r4, #0x18]\n    str r1, [r4, #0xc]\n    movs r1, r6\n    uxtb r1, r1\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am038_8ab04\n    bl .\n    ldr r1, [r4, #0x14]\n    cmp r0, r1\n    beq L_open_cfw_runtime_am038_8aef8_00fa\n    ldr.w r0, [pc, #0x7e4]\n    str r0, [sp]\n    ldr.w r3, [pc, #0x7d4]\n    mov.w r2, #0x136\n    ldr.w r1, [pc, #0x748]\n    movs r0, #2\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am038_addr_0044d25c\n    bl .\nL_open_cfw_runtime_am038_8aef8_00fa:\n    movs r0, #1\nL_open_cfw_runtime_am038_8aef8_00fc:\n    add sp, #0x10\n    pop.w {r4, r5, r6, r7, r8, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM038_8AFFA_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am038_8affa(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    str r3, [sp]\n    movs r3, r2\n    uxtb r3, r3\n    movs r2, r1\n    movs r1, r0\n    ldr.w r0, [pc, #0x7bc]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am038_8b010\n    bl .\n    pop {r1, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM038_8B010_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am038_8b010(void)
{
    __asm__ volatile(
        "    push.w {r3, r4, r5, r6, r7, r8, sb, sl, fp, lr}\n    sub sp, #0x18\n    movs r7, r0\n    mov r8, r1\n    mov sl, r2\n    mov sb, r3\n    movs r0, #0x1c\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am038_addr_0044f730\n    bl .\n    movs r4, r0\n    cmp r4, #0\n    bne L_open_cfw_runtime_am038_8b010_0048\n    ldr.w r0, [pc, #0x79c]\n    str r0, [sp, #8]\n    ldr.w r0, [pc, #0x4fc]\n    str r0, [sp, #4]\n    ldr.w r0, [pc, #0x4fc]\n    str r0, [sp]\n    ldr.w r3, [pc, #0x78c]\n    movw r2, #0x145\n    ldr.w r1, [pc, #0x6ec]\n    movs r0, #3\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am038_addr_0044d25c\n    bl .\nL_open_cfw_runtime_am038_8b010_003e:\n    movs r0, #0\n    movs.w r1, #-1\n    str r0, [r1]\n    b L_open_cfw_runtime_am038_8b010_003e\nL_open_cfw_runtime_am038_8b010_0048:\n    cmp r4, #0\n    bne L_open_cfw_runtime_am038_8b010_0050\n    movs r0, #0\n    b L_open_cfw_runtime_am038_8b010_0116\nL_open_cfw_runtime_am038_8b010_0050:\n    ldr r5, [sp, #0x40]\n    cmp r5, #0\n    bne L_open_cfw_runtime_am038_8b010_0062\n    mov r1, sb\n    uxtb r1, r1\n    mov r0, r8\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am038_8aad8\n    bl .\n    movs r5, r0\nL_open_cfw_runtime_am038_8b010_0062:\n    movs r3, r5\n    mov r2, sb\n    uxtb r2, r2\n    mov r1, sl\n    mov r0, r8\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am038_8b86c\n    bl .\n    mov fp, r0\n    mov r2, sb\n    uxtb r2, r2\n    mov r1, fp\n    movs r0, r7\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am038_8b840\n    bl .\n    movs r6, r0\n    cmp r6, #0\n    bne L_open_cfw_runtime_am038_8b010_00bc\n    str.w fp, [sp, #0x14]\n    str r5, [sp, #0x10]\n    uxtb.w sb, sb\n    str.w sb, [sp, #0xc]\n    str.w sl, [sp, #8]\n    str.w r8, [sp, #4]\n    ldr.w r0, [pc, #0x724]\n    str r0, [sp]\n    ldr.w r3, [pc, #0x718]\n    mov.w r2, #0x152\n    ldr.w r1, [pc, #0x678]\n    movs r0, #2\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am038_addr_0044d25c\n    bl .\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am038_addr_0044f758\n    bl .\n    movs r0, #0\n    b L_open_cfw_runtime_am038_8b010_0116\nL_open_cfw_runtime_am038_8b010_00bc:\n    movs r0, r4\n    ldr r1, [r0, #4]\n    bfi r1, r8, #0, #0x10\n    str r1, [r0, #4]\n    movs r0, r4\n    ldr r1, [r0, #4]\n    bfi r1, sl, #0x10, #0x10\n    str r1, [r0, #4]\n    movs r0, r4\n    mov r1, sb\n    uxtb r1, r1\n    ldr r2, [r0]\n    bfi r2, r1, #8, #8\n    str r2, [r0]\n    movs r0, r4\n    movs r1, #0x30\n    ldr r2, [r0]\n    bfi r2, r1, #0x10, #0x10\n    str r2, [r0]\n    movs r0, r4\n    ldr r1, [r0, #8]\n    bfi r1, r5, #0, #0x10\n    str r1, [r0, #8]\n    movs r0, r4\n    movs r1, #0x19\n    ldr r2, [r0]\n    bfi r2, r1, #0, #8\n    str r2, [r0]\n    mov r1, sb\n    uxtb r1, r1\n    movs r0, r6\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am038_8ab04\n    bl .\n    str r0, [r4, #0x10]\n    str r6, [r4, #0x14]\n    str.w fp, [r4, #0xc]\n    str r7, [r4, #0x18]\n    movs r0, r4\nL_open_cfw_runtime_am038_8b010_0116:\n    add sp, #0x1c\n    pop.w {r4, r5, r6, r7, r8, sb, sl, fp, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM038_8B134_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am038_8b134(void)
{
    __asm__ volatile(
        "    push {r3, r4, r5, lr}\n    movs r5, r1\n    movs r1, r5\n    ldr r2, [r1, #8]\n    uxth r2, r2\n    str r2, [sp]\n    ldr r3, [r1]\n    lsrs r3, r3, #8\n    uxtb r3, r3\n    ldr r2, [r1, #4]\n    lsrs r2, r2, #0x10\n    ldr r1, [r1, #4]\n    uxth r1, r1\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am038_8b010\n    bl .\n    movs r4, r0\n    cmp r4, #0\n    bne L_open_cfw_runtime_am038_8b134_0028\n    movs r0, #0\n    b L_open_cfw_runtime_am038_8b134_0060\nL_open_cfw_runtime_am038_8b134_0028:\n    ldr r0, [r5]\n    lsrs r0, r0, #0x10\n    movs r1, r4\n    ldr r2, [r1]\n    bfi r2, r0, #0x10, #0x10\n    str r2, [r1]\n    movs r0, r4\n    ldr r1, [r0]\n    lsrs r1, r1, #0x10\n    orrs r1, r1, #0x30\n    ldr r2, [r0]\n    bfi r2, r1, #0x10, #0x10\n    str r2, [r0]\n    ldr r0, [r5, #0xc]\n    ldr r1, [r4, #0xc]\n    cmp r0, r1\n    bhs L_open_cfw_runtime_am038_8b134_0054\n    ldr r2, [r5, #0xc]\n    b L_open_cfw_runtime_am038_8b134_0056\nL_open_cfw_runtime_am038_8b134_0054:\n    ldr r2, [r4, #0xc]\nL_open_cfw_runtime_am038_8b134_0056:\n    ldr r1, [r5, #0x10]\n    ldr r0, [r4, #0x10]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am038_addr_00454738\n    bl .\n    movs r0, r4\nL_open_cfw_runtime_am038_8b134_0060:\n    pop {r1, r4, r5, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM038_8B196_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am038_8b196(void)
{
    __asm__ volatile(
        "    push.w {r4, r5, r6, r7, r8, lr}\n    movs r4, r0\n    mov r8, r1\n    movs r7, r2\n    movs r6, r3\n    cmp r4, #0\n    bne L_open_cfw_runtime_am038_8b196_0014\n    movs r0, #0\n    b L_open_cfw_runtime_am038_8b196_007c\nL_open_cfw_runtime_am038_8b196_0014:\n    mov r0, r8\n    uxtb r0, r0\n    cmp r0, #0\n    bne L_open_cfw_runtime_am038_8b196_0024\n    ldr.w r8, [r4]\n    lsrs.w r8, r8, #8\nL_open_cfw_runtime_am038_8b196_0024:\n    ldr r5, [sp, #0x18]\n    cmp r5, #0\n    bne L_open_cfw_runtime_am038_8b196_0036\n    mov r1, r8\n    uxtb r1, r1\n    movs r0, r7\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am038_8aad8\n    bl .\n    movs r5, r0\nL_open_cfw_runtime_am038_8b196_0036:\n    movs r3, r5\n    mov r2, r8\n    uxtb r2, r2\n    movs r1, r6\n    movs r0, r7\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am038_8b86c\n    bl .\n    ldr r1, [r4, #0xc]\n    cmp r1, r0\n    bhs L_open_cfw_runtime_am038_8b196_004e\n    movs r0, #0\n    b L_open_cfw_runtime_am038_8b196_007c\nL_open_cfw_runtime_am038_8b196_004e:\n    movs r0, r4\n    uxtb.w r8, r8\n    ldr r1, [r0]\n    bfi r1, r8, #8, #8\n    str r1, [r0]\n    movs r0, r4\n    ldr r1, [r0, #4]\n    bfi r1, r7, #0, #0x10\n    str r1, [r0, #4]\n    movs r0, r4\n    ldr r1, [r0, #4]\n    bfi r1, r6, #0x10, #0x10\n    str r1, [r0, #4]\n    movs r0, r4\n    ldr r1, [r0, #8]\n    bfi r1, r5, #0, #0x10\n    str r1, [r0, #8]\n    movs r0, r4\nL_open_cfw_runtime_am038_8b196_007c:\n    pop.w {r4, r5, r6, r7, r8, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM038_8B216_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am038_8b216(void)
{
    __asm__ volatile(
        "    push {r0, r1, r2, r3, r4, lr}\n    movs r4, r0\n    cmp r4, #0\n    bne L_open_cfw_runtime_am038_8b216_0030\n    ldr r0, [pc, #0x30c]\n    str r0, [sp, #8]\n    ldr r0, [pc, #0x30c]\n    str r0, [sp, #4]\n    ldr r0, [pc, #0x30c]\n    str r0, [sp]\n    ldr.w r3, [pc, #0x5a8]\n    mov.w r2, #0x19e\n    ldr.w r1, [pc, #0x500]\n    movs r0, #3\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am038_addr_0044d25c\n    bl .\nL_open_cfw_runtime_am038_8b216_0026:\n    movs r0, #0\n    movs.w r1, #-1\n    str r0, [r1]\n    b L_open_cfw_runtime_am038_8b216_0026\nL_open_cfw_runtime_am038_8b216_0030:\n    cmp r4, #0\n    beq L_open_cfw_runtime_am038_8b216_0092\n    ldr r0, [r4]\n    lsrs r0, r0, #0x10\n    lsls r0, r0, #0x1b\n    bpl L_open_cfw_runtime_am038_8b216_007a\n    ldr r0, [r4, #0x18]\n    cmp r0, #0\n    bne L_open_cfw_runtime_am038_8b216_006a\n    ldr r0, [pc, #0x2d0]\n    str r0, [sp, #8]\n    ldr r0, [pc, #0x2dc]\n    str r0, [sp, #4]\n    ldr r0, [pc, #0x2d0]\n    str r0, [sp]\n    ldr.w r3, [pc, #0x56c]\n    movw r2, #0x1a3\n    ldr.w r1, [pc, #0x4c4]\n    movs r0, #3\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am038_addr_0044d25c\n    bl .\nL_open_cfw_runtime_am038_8b216_0060:\n    movs r0, #0\n    movs.w r1, #-1\n    str r0, [r1]\n    b L_open_cfw_runtime_am038_8b216_0060\nL_open_cfw_runtime_am038_8b216_006a:\n    ldr r0, [r4, #0x18]\n    ldr r1, [r4, #0x14]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am038_8b85a\n    bl .\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am038_addr_0044f758\n    bl .\n    b L_open_cfw_runtime_am038_8b216_0092\nL_open_cfw_runtime_am038_8b216_007a:\n    ldr.w r0, [pc, #0x544]\n    str r0, [sp]\n    ldr.w r3, [pc, #0x53c]\n    mov.w r2, #0x1aa\n    ldr.w r1, [pc, #0x494]\n    movs r0, #3\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am038_addr_0044d25c\n    bl .\nL_open_cfw_runtime_am038_8b216_0092:\n    pop {r0, r1, r2, r3, r4, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM038_8B2AA_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am038_8b2aa(void)
{
    __asm__ volatile(
        "    push {r1, r2, r3, r4, r5, lr}\n    movs r4, r1\n    cmp r0, #0\n    bne L_open_cfw_runtime_am038_8b2aa_0032\n    ldr r0, [pc, #0x278]\n    str r0, [sp, #8]\n    ldr.w r0, [pc, #0x524]\n    str r0, [sp, #4]\n    ldr r0, [pc, #0x274]\n    str r0, [sp]\n    ldr.w r3, [pc, #0x51c]\n    movw r2, #0x1b1\n    ldr.w r1, [pc, #0x468]\n    movs r0, #3\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am038_addr_0044d25c\n    bl .\nL_open_cfw_runtime_am038_8b2aa_0028:\n    movs r0, #0\n    movs.w r1, #-1\n    str r0, [r1]\n    b L_open_cfw_runtime_am038_8b2aa_0028\nL_open_cfw_runtime_am038_8b2aa_0032:\n    cmp r0, #0\n    bne L_open_cfw_runtime_am038_8b2aa_003a\n    movs r0, #0\n    b L_open_cfw_runtime_am038_8b2aa_00a2\nL_open_cfw_runtime_am038_8b2aa_003a:\n    ldr r1, [r0, #0x10]\n    ldr r3, [r0]\n    ubfx r3, r3, #8, #8\n    cmp r3, #7\n    bne L_open_cfw_runtime_am038_8b2aa_004a\n    movs r3, #2\n    b L_open_cfw_runtime_am038_8b2aa_0078\nL_open_cfw_runtime_am038_8b2aa_004a:\n    ldr r3, [r0]\n    ubfx r3, r3, #8, #8\n    cmp r3, #8\n    bne L_open_cfw_runtime_am038_8b2aa_0058\n    movs r3, #4\n    b L_open_cfw_runtime_am038_8b2aa_0078\nL_open_cfw_runtime_am038_8b2aa_0058:\n    ldr r3, [r0]\n    ubfx r3, r3, #8, #8\n    cmp r3, #9\n    bne L_open_cfw_runtime_am038_8b2aa_0066\n    movs r3, #0x10\n    b L_open_cfw_runtime_am038_8b2aa_0078\nL_open_cfw_runtime_am038_8b2aa_0066:\n    ldr r3, [r0]\n    ubfx r3, r3, #8, #8\n    cmp r3, #0xa\n    bne L_open_cfw_runtime_am038_8b2aa_0076\n    mov.w r3, #0x100\n    b L_open_cfw_runtime_am038_8b2aa_0078\nL_open_cfw_runtime_am038_8b2aa_0076:\n    movs r3, #0\nL_open_cfw_runtime_am038_8b2aa_0078:\n    add.w r1, r1, r3, lsl #2\n    ldr r3, [r0, #8]\n    uxth r3, r3\n    mul r2, r2, r3\n    add.w r5, r1, r2\n    cmp r4, #0\n    bne L_open_cfw_runtime_am038_8b2aa_0090\n    movs r0, r5\n    b L_open_cfw_runtime_am038_8b2aa_00a2\nL_open_cfw_runtime_am038_8b2aa_0090:\n    ldr r0, [r0]\n    lsrs r0, r0, #8\n    uxtb r0, r0\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am038_addr_00440f44\n    bl .\n    muls r4, r0, r4\n    lsrs r4, r4, #3\n    add.w r0, r5, r4\nL_open_cfw_runtime_am038_8b2aa_00a2:\n    pop {r1, r2, r3, r4, r5, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM038_8B34E_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am038_8b34e(void)
{
    __asm__ volatile(
        "    push.w {r1, r2, r3, r4, r5, r6, r7, r8, sb, sl, fp, lr}\n    movs r4, r0\n    movs r5, r1\n    cmp r4, #0\n    bne L_open_cfw_runtime_am038_8b34e_0036\n    ldr r0, [pc, #0x1d0]\n    str r0, [sp, #8]\n    ldr.w r0, [pc, #0x484]\n    str r0, [sp, #4]\n    ldr r0, [pc, #0x1cc]\n    str r0, [sp]\n    ldr.w r3, [pc, #0x47c]\n    movw r2, #0x1c1\n    ldr.w r1, [pc, #0x3c0]\n    movs r0, #3\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am038_addr_0044d25c\n    bl .\nL_open_cfw_runtime_am038_8b34e_002c:\n    movs r0, #0\n    movs.w r1, #-1\n    str r0, [r1]\n    b L_open_cfw_runtime_am038_8b34e_002c\nL_open_cfw_runtime_am038_8b34e_0036:\n    ldr r0, [r4, #0x10]\n    cmp r0, #0\n    bne L_open_cfw_runtime_am038_8b34e_0066\n    ldr r0, [pc, #0x1a0]\n    str r0, [sp, #8]\n    ldr.w r0, [pc, #0x45c]\n    str r0, [sp, #4]\n    ldr r0, [pc, #0x19c]\n    str r0, [sp]\n    ldr.w r3, [pc, #0x44c]\n    mov.w r2, #0x1c2\n    ldr.w r1, [pc, #0x390]\n    movs r0, #3\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am038_addr_0044d25c\n    bl .\nL_open_cfw_runtime_am038_8b34e_005c:\n    movs r0, #0\n    movs.w r1, #-1\n    str r0, [r1]\n    b L_open_cfw_runtime_am038_8b34e_005c\nL_open_cfw_runtime_am038_8b34e_0066:\n    cmp r4, #0\n    bne L_open_cfw_runtime_am038_8b34e_006e\n    movs r0, #0\n    b L_open_cfw_runtime_am038_8b34e_01cc\nL_open_cfw_runtime_am038_8b34e_006e:\n    ldr r0, [r4, #0x10]\n    cmp r0, #0\n    bne L_open_cfw_runtime_am038_8b34e_0078\n    movs r0, #0\n    b L_open_cfw_runtime_am038_8b34e_01cc\nL_open_cfw_runtime_am038_8b34e_0078:\n    movs r7, r4\n    ldr.w sb, [r7, #4]\n    uxth.w sb, sb\n    ldr.w r8, [r7, #4]\n    lsrs.w r8, r8, #0x10\n    movs r1, #0x20\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am038_8b73c\n    bl .\n    cmp r0, #0\n    bne L_open_cfw_runtime_am038_8b34e_009a\n    movs r0, #0\n    b L_open_cfw_runtime_am038_8b34e_01cc\nL_open_cfw_runtime_am038_8b34e_009a:\n    cmp r5, #0\n    bne L_open_cfw_runtime_am038_8b34e_00ac\n    ldr r1, [r7]\n    lsrs r1, r1, #8\n    uxtb r1, r1\n    mov r0, sb\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am038_8aad8\n    bl .\n    movs r5, r0\nL_open_cfw_runtime_am038_8b34e_00ac:\n    ldr r0, [r7, #8]\n    uxth r0, r0\n    cmp r0, r5\n    bne L_open_cfw_runtime_am038_8b34e_00b8\n    movs r0, #1\n    b L_open_cfw_runtime_am038_8b34e_01cc\nL_open_cfw_runtime_am038_8b34e_00b8:\n    ldr r0, [r7]\n    lsrs r0, r0, #8\n    uxtb r0, r0\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am038_addr_00440f44\n    bl .\n    movs r6, r0\n    mul r6, r6, sb\n    adds r6, r6, #7\n    lsrs r6, r6, #3\n    cmp r5, r6\n    bhs L_open_cfw_runtime_am038_8b34e_00ee\n    str r6, [sp, #4]\n    ldr.w r0, [pc, #0x3cc]\n    str r0, [sp]\n    ldr.w r3, [pc, #0x3c0]\n    movw r2, #0x1dd\n    ldr.w r1, [pc, #0x304]\n    movs r0, #2\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am038_addr_0044d25c\n    bl .\n    movs r0, #0\n    b L_open_cfw_runtime_am038_8b34e_01cc\nL_open_cfw_runtime_am038_8b34e_00ee:\n    movs r3, r5\n    ldr r2, [r7]\n    lsrs r2, r2, #8\n    uxtb r2, r2\n    mov r1, r8\n    mov r0, sb\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am038_8b86c\n    bl .\n    ldr r1, [r4, #0xc]\n    cmp r1, r0\n    bhs L_open_cfw_runtime_am038_8b34e_0108\n    movs r0, #0\n    b L_open_cfw_runtime_am038_8b34e_01cc\nL_open_cfw_runtime_am038_8b34e_0108:\n    ldr r0, [r7]\n    ubfx r0, r0, #8, #8\n    cmp r0, #7\n    bne L_open_cfw_runtime_am038_8b34e_0116\n    movs r1, #2\n    b L_open_cfw_runtime_am038_8b34e_0144\nL_open_cfw_runtime_am038_8b34e_0116:\n    ldr r0, [r7]\n    ubfx r0, r0, #8, #8\n    cmp r0, #8\n    bne L_open_cfw_runtime_am038_8b34e_0124\n    movs r1, #4\n    b L_open_cfw_runtime_am038_8b34e_0144\nL_open_cfw_runtime_am038_8b34e_0124:\n    ldr r0, [r7]\n    ubfx r0, r0, #8, #8\n    cmp r0, #9\n    bne L_open_cfw_runtime_am038_8b34e_0132\n    movs r1, #0x10\n    b L_open_cfw_runtime_am038_8b34e_0144\nL_open_cfw_runtime_am038_8b34e_0132:\n    ldr r0, [r7]\n    ubfx r0, r0, #8, #8\n    cmp r0, #0xa\n    bne L_open_cfw_runtime_am038_8b34e_0142\n    mov.w r1, #0x100\n    b L_open_cfw_runtime_am038_8b34e_0144\nL_open_cfw_runtime_am038_8b34e_0142:\n    movs r1, #0\nL_open_cfw_runtime_am038_8b34e_0144:\n    lsls r1, r1, #2\n    ldr r0, [r7, #8]\n    uxth r0, r0\n    cmp r0, r5\n    bhs L_open_cfw_runtime_am038_8b34e_0196\n    ldr r0, [r4, #0x10]\n    add.w r2, r0, r1\n    ldr r3, [r7, #8]\n    uxth r3, r3\n    subs.w r0, r8, #1\n    muls r3, r0, r3\n    add.w sb, r2, r3\n    ldr r0, [r4, #0x10]\n    add r0, r1\n    subs.w r1, r8, #1\n    mul r1, r1, r5\n    add.w sl, r0, r1\n    movs.w fp, #0\nL_open_cfw_runtime_am038_8b34e_0176:\n    cmp fp, r8\n    bhs L_open_cfw_runtime_am038_8b34e_01c2\n    movs r2, r6\n    mov r1, sb\n    mov r0, sl\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am038_addr_0045475a\n    bl .\n    ldr r0, [r7, #8]\n    uxth r0, r0\n    rsbs r0, r0, #0\n    add sb, r0\n    rsbs r0, r5, #0\n    add sl, r0\n    adds.w fp, fp, #1\n    b L_open_cfw_runtime_am038_8b34e_0176\nL_open_cfw_runtime_am038_8b34e_0196:\n    ldr r0, [r4, #0x10]\n    add.w sb, r0, r1\n    ldr r0, [r4, #0x10]\n    add.w sl, r0, r1\n    movs.w fp, #0\n    b L_open_cfw_runtime_am038_8b34e_01be\nL_open_cfw_runtime_am038_8b34e_01a8:\n    movs r2, r6\n    mov r1, sb\n    mov r0, sl\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am038_addr_0045475a\n    bl .\n    ldr r0, [r7, #8]\n    uxth r0, r0\n    add sb, r0\n    add sl, r5\n    adds.w fp, fp, #1\nL_open_cfw_runtime_am038_8b34e_01be:\n    cmp fp, r8\n    blo L_open_cfw_runtime_am038_8b34e_01a8\nL_open_cfw_runtime_am038_8b34e_01c2:\n    ldr r0, [r4, #8]\n    bfi r0, r5, #0, #0x10\n    str r0, [r4, #8]\n    movs r0, #1\nL_open_cfw_runtime_am038_8b34e_01cc:\n    pop.w {r1, r2, r3, r4, r5, r6, r7, r8, sb, sl, fp, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM038_8B540_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am038_8b540(void)
{
    __asm__ volatile(
        "    push.w {r1, r2, r3, r4, r5, r6, r7, r8, sb, sl, fp, lr}\n    movs r4, r0\n    cmp r4, #0\n    bne L_open_cfw_runtime_am038_8b540_0036\n    ldr.w r0, [pc, #0x2a8]\n    str r0, [sp, #8]\n    ldr.w r0, [pc, #0x2a4]\n    str r0, [sp, #4]\n    ldr.w r0, [pc, #0x2a4]\n    str r0, [sp]\n    ldr.w r3, [pc, #0x2a0]\n    mov.w r2, #0x208\n    ldr r1, [pc, #0x1cc]\n    movs r0, #3\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am038_addr_0044d25c\n    bl .\nL_open_cfw_runtime_am038_8b540_002c:\n    movs r0, #0\n    movs.w r1, #-1\n    str r0, [r1]\n    b L_open_cfw_runtime_am038_8b540_002c\nL_open_cfw_runtime_am038_8b540_0036:\n    cmp r4, #0\n    bne L_open_cfw_runtime_am038_8b540_003e\n    movs r0, #0\n    b L_open_cfw_runtime_am038_8b540_01de\nL_open_cfw_runtime_am038_8b540_003e:\n    ldr r0, [r4]\n    ubfx r0, r0, #0x10, #1\n    cmp r0, #0\n    beq L_open_cfw_runtime_am038_8b540_004c\n    movs r0, #0\n    b L_open_cfw_runtime_am038_8b540_01de\nL_open_cfw_runtime_am038_8b540_004c:\n    ldr r0, [r4]\n    lsrs r0, r0, #0x10\n    lsls r0, r0, #0x1a\n    bmi L_open_cfw_runtime_am038_8b540_0070\n    ldr r0, [r4]\n    lsrs r0, r0, #0x10\n    str r0, [sp, #4]\n    ldr r0, [pc, #0x268]\n    str r0, [sp]\n    ldr r3, [pc, #0x260]\n    movw r2, #0x20d\n    ldr r1, [pc, #0x18c]\n    movs r0, #2\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am038_addr_0044d25c\n    bl .\n    movs r0, #0\n    b L_open_cfw_runtime_am038_8b540_01de\nL_open_cfw_runtime_am038_8b540_0070:\n    ldr r0, [r4]\n    lsrs r0, r0, #8\n    movs r1, r0\n    uxtb r1, r1\n    subs r1, r1, #7\n    cmp r1, #4\n    bhs L_open_cfw_runtime_am038_8b540_00c6\n    movs r1, r0\n    uxtb r1, r1\n    cmp r1, #7\n    bne L_open_cfw_runtime_am038_8b540_008a\n    movs r5, #2\n    b L_open_cfw_runtime_am038_8b540_00b0\nL_open_cfw_runtime_am038_8b540_008a:\n    movs r1, r0\n    uxtb r1, r1\n    cmp r1, #8\n    bne L_open_cfw_runtime_am038_8b540_0096\n    movs r5, #4\n    b L_open_cfw_runtime_am038_8b540_00b0\nL_open_cfw_runtime_am038_8b540_0096:\n    movs r1, r0\n    uxtb r1, r1\n    cmp r1, #9\n    bne L_open_cfw_runtime_am038_8b540_00a2\n    movs r5, #0x10\n    b L_open_cfw_runtime_am038_8b540_00b0\nL_open_cfw_runtime_am038_8b540_00a2:\n    uxtb r0, r0\n    cmp r0, #0xa\n    bne L_open_cfw_runtime_am038_8b540_00ae\n    mov.w r5, #0x100\n    b L_open_cfw_runtime_am038_8b540_00b0\nL_open_cfw_runtime_am038_8b540_00ae:\n    movs r5, #0\nL_open_cfw_runtime_am038_8b540_00b0:\n    ldr r6, [r4, #0x10]\n    movs r7, #0\nL_open_cfw_runtime_am038_8b540_00b4:\n    cmp r7, r5\n    bge.w #0x48b70c\n    add.w r0, r6, r7, lsl #2\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am038_addr_004410b8\n    bl .\n    adds r7, r7, #1\n    b L_open_cfw_runtime_am038_8b540_00b4\nL_open_cfw_runtime_am038_8b540_00c6:\n    movs r1, r0\n    uxtb r1, r1\n    cmp r1, #0x10\n    bne L_open_cfw_runtime_am038_8b540_0108\n    ldr r5, [r4, #4]\n    lsrs r5, r5, #0x10\n    ldr r6, [r4, #4]\n    uxth r6, r6\n    ldr r7, [r4, #8]\n    uxth r7, r7\n    ldr.w r8, [r4, #0x10]\n    movs.w sb, #0\n    b L_open_cfw_runtime_am038_8b540_00fc\nL_open_cfw_runtime_am038_8b540_00e4:\n    mov r0, sl\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am038_addr_004410b8\n    bl .\n    adds.w sl, sl, #4\n    adds.w fp, fp, #1\nL_open_cfw_runtime_am038_8b540_00f2:\n    cmp fp, r6\n    blo L_open_cfw_runtime_am038_8b540_00e4\n    add r8, r7\n    adds.w sb, sb, #1\nL_open_cfw_runtime_am038_8b540_00fc:\n    cmp sb, r5\n    bhs L_open_cfw_runtime_am038_8b540_01cc\n    mov sl, r8\n    movs.w fp, #0\n    b L_open_cfw_runtime_am038_8b540_00f2\nL_open_cfw_runtime_am038_8b540_0108:\n    movs r1, r0\n    uxtb r1, r1\n    cmp r1, #0x14\n    bne L_open_cfw_runtime_am038_8b540_0164\n    ldr r0, [r4, #4]\n    lsrs r0, r0, #0x10\n    str r0, [sp]\n    ldr r5, [r4, #4]\n    uxth r5, r5\n    ldr r6, [r4, #8]\n    uxth r6, r6\n    movs r0, r6\n    lsrs r0, r0, #1\n    str r0, [sp, #4]\n    ldr r7, [r4, #0x10]\n    ldr r0, [sp]\n    mul r0, r0, r6\n    add.w sb, r7, r0\n    movs.w r8, #0\n    b L_open_cfw_runtime_am038_8b540_0156\nL_open_cfw_runtime_am038_8b540_0136:\n    ldrb.w r1, [sb, sl]\n    mov r0, fp\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am038_addr_004410ee\n    bl .\n    adds.w fp, fp, #2\n    adds.w sl, sl, #1\nL_open_cfw_runtime_am038_8b540_0148:\n    cmp sl, r5\n    blo L_open_cfw_runtime_am038_8b540_0136\n    add r7, r6\n    ldr r0, [sp, #4]\n    add sb, r0\n    adds.w r8, r8, #1\nL_open_cfw_runtime_am038_8b540_0156:\n    ldr r0, [sp]\n    cmp r8, r0\n    bhs L_open_cfw_runtime_am038_8b540_01cc\n    mov fp, r7\n    movs.w sl, #0\n    b L_open_cfw_runtime_am038_8b540_0148\nL_open_cfw_runtime_am038_8b540_0164:\n    movs r1, r0\n    uxtb r1, r1\n    cmp r1, #0x13\n    bne L_open_cfw_runtime_am038_8b540_01ac\n    ldr r5, [r4, #4]\n    lsrs r5, r5, #0x10\n    ldr r6, [r4, #4]\n    uxth r6, r6\n    ldr r7, [r4, #8]\n    uxth r7, r7\n    ldr.w r8, [r4, #0x10]\n    movs.w sb, #0\n    b L_open_cfw_runtime_am038_8b540_01a0\nL_open_cfw_runtime_am038_8b540_0182:\n    ldrb.w r1, [sl, #2]\n    uxtb r1, r1\n    mov r0, sl\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am038_addr_004410ee\n    bl .\n    adds.w sl, sl, #3\n    adds.w fp, fp, #1\nL_open_cfw_runtime_am038_8b540_0196:\n    cmp fp, r6\n    blo L_open_cfw_runtime_am038_8b540_0182\n    add r8, r7\n    adds.w sb, sb, #1\nL_open_cfw_runtime_am038_8b540_01a0:\n    cmp sb, r5\n    bhs L_open_cfw_runtime_am038_8b540_01cc\n    mov sl, r8\n    movs.w fp, #0\n    b L_open_cfw_runtime_am038_8b540_0196\nL_open_cfw_runtime_am038_8b540_01ac:\n    movs r1, r0\n    uxtb r1, r1\n    subs r1, #0xb\n    cmp r1, #4\n    blo L_open_cfw_runtime_am038_8b540_01cc\n    uxtb r0, r0\n    str r0, [sp, #4]\n    ldr r0, [pc, #0x10c]\n    str r0, [sp]\n    ldr r3, [pc, #0x100]\n    movw r2, #0x24d\n    ldr r1, [pc, #0x2c]\n    movs r0, #2\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am038_addr_0044d25c\n    bl .\nL_open_cfw_runtime_am038_8b540_01cc:\n    ldr r0, [r4]\n    lsrs r0, r0, #0x10\n    orrs r0, r0, #1\n    ldr r1, [r4]\n    bfi r1, r0, #0x10, #0x10\n    str r1, [r4]\n    movs r0, #1\nL_open_cfw_runtime_am038_8b540_01de:\n    pop.w {r1, r2, r3, r4, r5, r6, r7, r8, sb, sl, fp, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM038_8B73C_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am038_8b73c(void)
{
    __asm__ volatile(
        "    ldr r0, [r0]\n    lsrs r0, r0, #0x10\n    uxth r0, r0\n    tst r0, r1\n    beq L_open_cfw_runtime_am038_8b73c_000e\n    movs r0, #1\n    b L_open_cfw_runtime_am038_8b73c_0010\nL_open_cfw_runtime_am038_8b73c_000e:\n    movs r0, #0\nL_open_cfw_runtime_am038_8b73c_0010:\n    uxtb r0, r0\n    bx lr\n"
    );
}
#endif

#if defined(OPEN_CFW_AM038_8B750_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am038_8b750(void)
{
    __asm__ volatile(
        "    ldr r2, [r0]\n    uxth r1, r1\n    orrs.w r1, r1, r2, lsr #16\n    ldr r2, [r0]\n    bfi r2, r1, #0x10, #0x10\n    str r2, [r0]\n    bx lr\n"
    );
}
#endif

#if defined(OPEN_CFW_AM038_8B762_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am038_8b762(void)
{
    __asm__ volatile(
        "    push {r1, r2, r3, r4, r5, lr}\n    movs r4, r0\n    movs r5, r1\n    ldr r0, [r5, #0xc]\n    str r0, [sp, #8]\n    ldr r0, [r5, #0x10]\n    str r0, [sp, #4]\n    ldr r0, [r5, #8]\n    uxth r0, r0\n    str r0, [sp]\n    ldr r3, [r5]\n    lsrs r3, r3, #8\n    uxtb r3, r3\n    ldr r2, [r5, #4]\n    lsrs r2, r2, #0x10\n    ldr r1, [r5, #4]\n    uxth r1, r1\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am038_8aef8\n    bl .\n    movs r1, r0\n    uxtb r1, r1\n    cmp r1, #1\n    beq L_open_cfw_runtime_am038_8b762_0034\n    uxtb r0, r0\n    b L_open_cfw_runtime_am038_8b762_0042\nL_open_cfw_runtime_am038_8b762_0034:\n    ldr r1, [r5]\n    lsrs r1, r1, #0x10\n    ldr r2, [r4]\n    bfi r2, r1, #0x10, #0x10\n    str r2, [r4]\n    uxtb r0, r0\nL_open_cfw_runtime_am038_8b762_0042:\n    pop {r1, r2, r3, r4, r5, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM038_8B840_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am038_8b840(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    movs r3, r0\n    movs r0, r1\n    movs r1, r2\n    ldr r2, [r3]\n    cmp r2, #0\n    beq L_open_cfw_runtime_am038_8b840_0016\n    uxtb r1, r1\n    ldr r2, [r3]\n    blx r2\n    b L_open_cfw_runtime_am038_8b840_0018\nL_open_cfw_runtime_am038_8b840_0016:\n    movs r0, #0\nL_open_cfw_runtime_am038_8b840_0018:\n    pop {r1, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM038_8B85A_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am038_8b85a(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    movs r2, r0\n    movs r0, r1\n    ldr r1, [r2, #4]\n    cmp r1, #0\n    beq L_open_cfw_runtime_am038_8b85a_0010\n    ldr r1, [r2, #4]\n    blx r1\nL_open_cfw_runtime_am038_8b85a_0010:\n    pop {r0, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM038_8B86C_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am038_8b86c(void)
{
    __asm__ volatile(
        "    push {r3, r4, r5, lr}\n    movs r5, r1\n    movs r4, r2\n    cmp r3, #0\n    bne L_open_cfw_runtime_am038_8b86c_0014\n    movs r1, r4\n    uxtb r1, r1\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am038_8aad8\n    bl .\n    movs r3, r0\nL_open_cfw_runtime_am038_8b86c_0014:\n    mul r0, r5, r3\n    movs r1, r4\n    uxtb r1, r1\n    cmp r1, #0x14\n    bne L_open_cfw_runtime_am038_8b86c_002a\n    lsrs r3, r3, #1\n    mla r5, r5, r3, r0\n    movs r0, r5\n    b L_open_cfw_runtime_am038_8b86c_006a\nL_open_cfw_runtime_am038_8b86c_002a:\n    movs r1, r4\n    uxtb r1, r1\n    subs r1, r1, #7\n    cmp r1, #4\n    bhs L_open_cfw_runtime_am038_8b86c_006a\n    movs r1, r4\n    uxtb r1, r1\n    cmp r1, #7\n    bne L_open_cfw_runtime_am038_8b86c_0040\n    movs r1, #2\n    b L_open_cfw_runtime_am038_8b86c_0066\nL_open_cfw_runtime_am038_8b86c_0040:\n    movs r1, r4\n    uxtb r1, r1\n    cmp r1, #8\n    bne L_open_cfw_runtime_am038_8b86c_004c\n    movs r1, #4\n    b L_open_cfw_runtime_am038_8b86c_0066\nL_open_cfw_runtime_am038_8b86c_004c:\n    movs r1, r4\n    uxtb r1, r1\n    cmp r1, #9\n    bne L_open_cfw_runtime_am038_8b86c_0058\n    movs r1, #0x10\n    b L_open_cfw_runtime_am038_8b86c_0066\nL_open_cfw_runtime_am038_8b86c_0058:\n    uxtb r4, r4\n    cmp r4, #0xa\n    bne L_open_cfw_runtime_am038_8b86c_0064\n    mov.w r1, #0x100\n    b L_open_cfw_runtime_am038_8b86c_0066\nL_open_cfw_runtime_am038_8b86c_0064:\n    movs r1, #0\nL_open_cfw_runtime_am038_8b86c_0066:\n    adds.w r0, r0, r1, lsl #2\nL_open_cfw_runtime_am038_8b86c_006a:\n    pop {r1, r4, r5, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM038_8B8D8_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am038_8b8d8(void)
{
    __asm__ volatile(
        "    push {r2, r3, r4, lr}\n    movs r4, r1\n    ldr r1, [r0, #4]\n    lsrs r1, r1, #0x10\n    subs r1, r1, #1\n    str r1, [sp]\n    ldr r3, [r0, #4]\n    uxth r3, r3\n    subs r3, r3, #1\n    movs r2, #0\n    movs r1, #0\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am038_addr_00450b5c\n    bl .\n    pop {r0, r1, r4, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM038_8B8F8_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am038_8b8f8(void)
{
    __asm__ volatile(
        "    ldr r2, [r1]\n    str r2, [r0]\n    ldr r2, [r1, #4]\n    str r2, [r0, #4]\n    ldr r2, [r1, #8]\n    str r2, [r0, #8]\n    ldr r1, [r1, #0xc]\n    str r1, [r0, #0xc]\n    bx lr\n"
    );
}
#endif

#if defined(OPEN_CFW_AM038_8B90A_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am038_8b90a(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    movs r2, #1\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am038_addr_0044bdea\n    bl .\n    pop {r1, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM038_8B914_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am038_8b914(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    movs r2, #4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am038_addr_0044bdea\n    bl .\n    pop {r1, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM038_8B91E_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am038_8b91e(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    movs r2, #5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am038_addr_0044bdea\n    bl .\n    pop {r1, pc}\n"
    );
}
#endif
