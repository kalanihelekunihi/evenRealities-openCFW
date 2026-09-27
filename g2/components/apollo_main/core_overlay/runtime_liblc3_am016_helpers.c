/*
 * SPDX-License-Identifier: MIT
 *
 * Source-owned exact helpers from the AM-016 retained island.
 */

#if defined(OPEN_CFW_AM016_501D2_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am016_501d2(void)
{
    __asm__ volatile(
        "    push {r0, r1, r2, r3, r4, lr}\n    movs r4, r0\n    cmp r4, #0\n    bne L_open_cfw_runtime_am016_501d2_0034\n    ldr.w r0, [pc, #0xdc]\n    str r0, [sp, #8]\n    ldr.w r0, [pc, #0xe8]\n    str r0, [sp, #4]\n    ldr.w r0, [pc, #0xd8]\n    str r0, [sp]\n    ldr.w r3, [pc, #0xe8]\n    movs r2, #0xb9\n    ldr.w r1, [pc, #0xd4]\n    movs r0, #3\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am016_addr_0044d25c\n    bl .\nL_open_cfw_runtime_am016_501d2_002a:\n    movs r0, #0\n    movs.w r1, #-1\n    str r0, [r1]\n    b L_open_cfw_runtime_am016_501d2_002a\nL_open_cfw_runtime_am016_501d2_0034:\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am016_addr_00450190\n    bl .\n    movs r1, r0\n    cmp r1, #0\n    bne L_open_cfw_runtime_am016_501d2_0044\n    movs r0, #0\n    b L_open_cfw_runtime_am016_501d2_0052\nL_open_cfw_runtime_am016_501d2_0044:\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am016_5036c\n    bl .\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am016_50346\n    bl .\n    movs r0, #1\nL_open_cfw_runtime_am016_501d2_0052:\n    add sp, #0x10\n    pop {r4, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM016_50228_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am016_50228(void)
{
    __asm__ volatile(
        "    push {r0, r1, r2, r3, r4, r5, r6, lr}\n    movs r4, r0\n    cmp r4, #0\n    bne L_open_cfw_runtime_am016_50228_0034\n    ldr.w r0, [pc, #0x84]\n    str r0, [sp, #8]\n    ldr.w r0, [pc, #0x94]\n    str r0, [sp, #4]\n    ldr.w r0, [pc, #0x80]\n    str r0, [sp]\n    ldr.w r3, [pc, #0x98]\n    movs r2, #0xc3\n    ldr.w r1, [pc, #0x7c]\n    movs r0, #3\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am016_addr_0044d25c\n    bl .\nL_open_cfw_runtime_am016_50228_002a:\n    movs r0, #0\n    movs.w r1, #-1\n    str r0, [r1]\n    b L_open_cfw_runtime_am016_50228_002a\nL_open_cfw_runtime_am016_50228_0034:\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am016_50388\n    bl .\n    movs r5, r0\n    movs r6, #0\n    b L_open_cfw_runtime_am016_50228_0052\nL_open_cfw_runtime_am016_50228_0040:\n    movs r1, r6\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am016_50390\n    bl .\n    ldr r1, [r0]\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am016_5036c\n    bl .\n    adds r6, r6, #1\nL_open_cfw_runtime_am016_50228_0052:\n    cmp r6, r5\n    blo L_open_cfw_runtime_am016_50228_0040\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am016_50346\n    bl .\n    pop {r0, r1, r2, r3, r4, r5, r6, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM016_50286_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am016_50286(void)
{
    __asm__ volatile(
        "    ldr r0, [r0, #8]\n    bics r0, r0, #0x8000\n    bx lr\n"
    );
}
#endif

#if defined(OPEN_CFW_AM016_5028E_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am016_5028e(void)
{
    __asm__ volatile(
        "    ldr.w r1, [pc, #0x24]\n    ldr r1, [r1, #0x6c]\n    b L_open_cfw_runtime_am016_5028e_001e\nL_open_cfw_runtime_am016_5028e_0008:\n    ldr r2, [r1, #4]\n    cmp r2, r0\n    beq L_open_cfw_runtime_am016_5028e_0014\n    ldr r2, [r1]\n    cmp r2, r0\n    bne L_open_cfw_runtime_am016_5028e_001c\nL_open_cfw_runtime_am016_5028e_0014:\n    ldrb r2, [r1, #0x18]\n    orrs r2, r2, #1\n    strb r2, [r1, #0x18]\nL_open_cfw_runtime_am016_5028e_001c:\n    ldr r1, [r1, #0x14]\nL_open_cfw_runtime_am016_5028e_001e:\n    cmp r1, #0\n    bne L_open_cfw_runtime_am016_5028e_0008\n    bx lr\n"
    );
}
#endif

#if defined(OPEN_CFW_AM016_502E0_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am016_502e0(void)
{
    __asm__ volatile(
        "    push.w {r3, r4, r5, r6, r7, r8, sb, lr}\n    movs r5, r0\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am016_addr_0044ffcc\n    bl .\n    movs r6, r0\n    movs r4, #0\n    movs r7, #0\n    b L_open_cfw_runtime_am016_502e0_004a\nL_open_cfw_runtime_am016_502e0_0014:\n    ldr.w r0, [sb]\n    str.w r0, [r8]\n    adds r4, r4, #1\n    b L_open_cfw_runtime_am016_502e0_0048\nL_open_cfw_runtime_am016_502e0_0020:\n    movs r1, r7\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am016_addr_00488578\n    bl .\n    mov sb, r0\n    movs r1, r4\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am016_addr_00488578\n    bl .\n    mov r8, r0\n    ldr.w r0, [sb]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am016_5037e\n    bl .\n    cmp r0, #0\n    beq L_open_cfw_runtime_am016_502e0_0014\n    ldr.w r0, [sb]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am016_addr_0044f758\n    bl .\nL_open_cfw_runtime_am016_502e0_0048:\n    adds r7, r7, #1\nL_open_cfw_runtime_am016_502e0_004a:\n    cmp r7, r6\n    blo L_open_cfw_runtime_am016_502e0_0020\n    cmp r4, #0\n    bne L_open_cfw_runtime_am016_502e0_005a\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am016_addr_00488478\n    bl .\n    b L_open_cfw_runtime_am016_502e0_0062\nL_open_cfw_runtime_am016_502e0_005a:\n    movs r1, r4\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am016_addr_0048849c\n    bl .\nL_open_cfw_runtime_am016_502e0_0062:\n    pop.w {r0, r4, r5, r6, r7, r8, sb, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM016_50346_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am016_50346(void)
{
    __asm__ volatile(
        "    push {r4, lr}\n    movs r4, r0\n    ldrb r0, [r4, #0x14]\n    lsls r0, r0, #0x1f\n    bmi L_open_cfw_runtime_am016_50346_0024\n    ldrb r0, [r4, #0x14]\n    ubfx r0, r0, #1, #1\n    uxtb r0, r0\n    cmp r0, #0\n    beq L_open_cfw_runtime_am016_50346_0024\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am016_502e0\n    bl .\n    ldrb r0, [r4, #0x14]\n    ands r0, r0, #0xfd\n    strb r0, [r4, #0x14]\nL_open_cfw_runtime_am016_50346_0024:\n    pop {r4, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM016_5036C_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am016_5036c(void)
{
    __asm__ volatile(
        "    ldrb r2, [r0, #0x14]\n    orrs r2, r2, #2\n    strb r2, [r0, #0x14]\n    ldr r0, [r1, #8]\n    orrs r0, r0, #0x10000\n    str r0, [r1, #8]\n    bx lr\n"
    );
}
#endif

#if defined(OPEN_CFW_AM016_5037E_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am016_5037e(void)
{
    __asm__ volatile(
        "    ldr r0, [r0, #8]\n    lsrs r0, r0, #0x10\n    ands r0, r0, #1\n    bx lr\n"
    );
}
#endif

#if defined(OPEN_CFW_AM016_50388_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am016_50388(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am016_addr_0044ffcc\n    bl .\n    pop {r1, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM016_50390_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am016_50390(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am016_addr_00488578\n    bl .\n    pop {r1, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM016_50398_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am016_50398(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    movs r2, r1\n    movs r1, #0\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am016_addr_00454746\n    bl .\n    pop {r0, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM016_503A4_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am016_503a4(void)
{
    __asm__ volatile(
        "    push {r4, lr}\n    ldr.w r4, [pc, #0x788]\n    movs r1, #0x60\n    adds.w r0, r4, #0xac\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am016_addr_00482b00\n    bl .\n    movs r2, #0\n    movs r1, #0x10\n    addw r0, pc, #0x39d\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am016_addr_00464466\n    bl .\n    str.w r0, [r4, #0xa8]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am016_509da\n    bl .\n    movs r0, #0\n    strb.w r0, [r4, #0xa4]\n    movs r0, #0\n    strb.w r0, [r4, #0xa5]\n    pop {r4, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM016_503D6_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am016_503d6(void)
{
    __asm__ volatile(
        "    push {r4, lr}\n    movs r4, r0\n    movs r1, #0x60\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am016_50398\n    bl .\n    mov.w r0, #0x1f4\n    str r0, [r4, #0x30]\n    movs r0, #0\n    str r0, [r4, #0x24]\n    movs r0, #0x64\n    str r0, [r4, #0x2c]\n    movs r0, #1\n    str r0, [r4, #0x44]\n    addw r0, pc, #0x23d\n    str r0, [r4, #0x20]\n    ldrb.w r0, [r4, #0x5c]\n    orrs r0, r0, #0x10\n    strb.w r0, [r4, #0x5c]\n    pop {r4, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM016_50408_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am016_50408(void)
{
    __asm__ volatile(
        "    push {r0, r1, r2, r3, r4, r5, r6, lr}\n    movs r5, r0\n    ldrb.w r0, [r5, #0x5c]\n    ubfx r0, r0, #4, #1\n    uxtb r0, r0\n    cmp r0, #0\n    beq L_open_cfw_runtime_am016_50408_0024\n    ldr r0, [r5, #4]\n    cmp r0, #0\n    bne L_open_cfw_runtime_am016_50408_001e\n    ldr r0, [r5, #8]\n    cmp r0, #0\n    beq L_open_cfw_runtime_am016_50408_0024\nL_open_cfw_runtime_am016_50408_001e:\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am016_50a74\n    bl .\nL_open_cfw_runtime_am016_50408_0024:\n    ldr.w r6, [pc, #0x700]\n    adds.w r0, r6, #0xac\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am016_addr_00482b12\n    bl .\n    movs r4, r0\n    cmp r4, #0\n    bne L_open_cfw_runtime_am016_50408_0062\n    ldr.w r0, [pc, #0x6f4]\n    str r0, [sp, #8]\n    ldr.w r0, [pc, #0x6f0]\n    str r0, [sp, #4]\n    ldr.w r0, [pc, #0x6f0]\n    str r0, [sp]\n    ldr.w r3, [pc, #0x6ec]\n    movs r2, #0x69\n    ldr.w r1, [pc, #0x6ec]\n    movs r0, #3\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am016_addr_0044d25c\n    bl .\nL_open_cfw_runtime_am016_50408_0058:\n    movs r0, #0\n    movs.w r1, #-1\n    str r0, [r1]\n    b L_open_cfw_runtime_am016_50408_0058\nL_open_cfw_runtime_am016_50408_0062:\n    cmp r4, #0\n    bne L_open_cfw_runtime_am016_50408_006a\n    movs r0, #0\n    b L_open_cfw_runtime_am016_50408_00f4\nL_open_cfw_runtime_am016_50408_006a:\n    movs r2, #0x60\n    movs r1, r5\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am016_addr_00454738\n    bl .\n    ldr r0, [r5]\n    cmp r0, r5\n    bne L_open_cfw_runtime_am016_50408_007c\n    str r4, [r4]\nL_open_cfw_runtime_am016_50408_007c:\n    ldrb.w r0, [r6, #0xa5]\n    ldrb.w r1, [r4, #0x5c]\n    bfi r1, r0, #2, #1\n    strb.w r1, [r4, #0x5c]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am016_addr_00473482\n    bl .\n    str r0, [r4, #0x50]\n    ldrb.w r0, [r4, #0x5c]\n    ands r0, r0, #0xfe\n    strb.w r0, [r4, #0x5c]\n    ldrb.w r0, [r4, #0x5c]\n    ubfx r0, r0, #4, #1\n    uxtb r0, r0\n    cmp r0, #0\n    beq L_open_cfw_runtime_am016_50408_00ee\n    ldr r0, [r4, #0x18]\n    cmp r0, #0\n    beq L_open_cfw_runtime_am016_50408_00c4\n    movs r0, r4\n    ldr r1, [r4, #0x18]\n    blx r1\n    ldr r1, [r4, #0x24]\n    adds r1, r0, r1\n    str r1, [r4, #0x24]\n    ldr r1, [r4, #0x2c]\n    adds r0, r0, r1\n    str r0, [r4, #0x2c]\nL_open_cfw_runtime_am016_50408_00c4:\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am016_50a3e\n    bl .\n    movs r0, r4\n    ldr r1, [r4, #0x20]\n    blx r1\n    str r0, [r4, #0x28]\n    ldr r0, [r4, #4]\n    cmp r0, #0\n    beq L_open_cfw_runtime_am016_50408_00e0\n    ldr r1, [r4, #0x28]\n    ldr r0, [r4]\n    ldr r2, [r4, #4]\n    blx r2\nL_open_cfw_runtime_am016_50408_00e0:\n    ldr r0, [r4, #8]\n    cmp r0, #0\n    beq L_open_cfw_runtime_am016_50408_00ee\n    ldr r1, [r4, #0x28]\n    movs r0, r4\n    ldr r2, [r4, #8]\n    blx r2\nL_open_cfw_runtime_am016_50408_00ee:\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am016_509da\n    bl .\n    movs r0, r4\nL_open_cfw_runtime_am016_50408_00f4:\n    add sp, #0x10\n    pop {r4, r5, r6, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM016_50500_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am016_50500(void)
{
    __asm__ volatile(
        "    push.w {r4, r5, r6, r7, r8, lr}\n    movs r4, r0\n    mov r8, r1\n    movs r6, #0\n    ldr.w r7, [pc, #0x63c]\n    movs r0, r7\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am016_addr_00482cd8\n    bl .\n    movs r5, r0\n    b L_open_cfw_runtime_am016_50500_005a\nL_open_cfw_runtime_am016_50500_0018:\n    movs r1, r5\n    movs r0, r7\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am016_addr_00482cf0\n    bl .\n    movs r5, r0\n    b L_open_cfw_runtime_am016_50500_005a\nL_open_cfw_runtime_am016_50500_0024:\n    movs r0, #0\n    ldr r1, [r5]\n    cmp r1, r4\n    beq L_open_cfw_runtime_am016_50500_0030\n    cmp r4, #0\n    bne L_open_cfw_runtime_am016_50500_004c\nL_open_cfw_runtime_am016_50500_0030:\n    ldr r1, [r5, #4]\n    mov r2, r8\n    cmp r1, r2\n    beq L_open_cfw_runtime_am016_50500_003e\n    mov r1, r8\n    cmp r1, #0\n    bne L_open_cfw_runtime_am016_50500_004c\nL_open_cfw_runtime_am016_50500_003e:\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am016_50b0c\n    bl .\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am016_509da\n    bl .\n    movs r6, #1\n    movs r0, #1\nL_open_cfw_runtime_am016_50500_004c:\n    uxtb r0, r0\n    cmp r0, #0\n    beq L_open_cfw_runtime_am016_50500_0018\n    movs r0, r7\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am016_addr_00482cd8\n    bl .\n    movs r5, r0\nL_open_cfw_runtime_am016_50500_005a:\n    cmp r5, #0\n    bne L_open_cfw_runtime_am016_50500_0024\n    movs r0, r6\n    uxtb r0, r0\n    pop.w {r4, r5, r6, r7, r8, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM016_50566_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am016_50566(void)
{
    __asm__ volatile(
        "    push {r4, r5, r6, lr}\n    movs r4, r0\n    movs r5, r1\n    ldr.w r6, [pc, #0x5d8]\n    movs r0, r6\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am016_addr_00482cd8\n    bl .\n    movs r1, r0\n    b L_open_cfw_runtime_am016_50566_001c\nL_open_cfw_runtime_am016_50566_0014:\n    movs r0, r6\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am016_addr_00482cf0\n    bl .\n    movs r1, r0\nL_open_cfw_runtime_am016_50566_001c:\n    cmp r1, #0\n    beq L_open_cfw_runtime_am016_50566_0038\n    ldr r0, [r1]\n    cmp r0, r4\n    bne L_open_cfw_runtime_am016_50566_0014\n    ldr r0, [r1, #4]\n    movs r2, r5\n    cmp r0, r2\n    beq L_open_cfw_runtime_am016_50566_0034\n    movs r0, r5\n    cmp r0, #0\n    bne L_open_cfw_runtime_am016_50566_0014\nL_open_cfw_runtime_am016_50566_0034:\n    movs r0, r1\n    b L_open_cfw_runtime_am016_50566_003a\nL_open_cfw_runtime_am016_50566_0038:\n    movs r0, #0\nL_open_cfw_runtime_am016_50566_003a:\n    pop {r4, r5, r6, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM016_505A2_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am016_505a2(void)
{
    __asm__ volatile(
        "    push {r1, r2, r3, r4, r5, r6, r7, lr}\n    movs r6, r0\n    movs r5, r1\n    movs r4, r2\n    movw r7, #0x2711\n    cmp r6, r7\n    blo L_open_cfw_runtime_am016_505a2_002c\n    str r6, [sp, #4]\n    ldr.w r0, [pc, #0x594]\n    str r0, [sp]\n    ldr.w r3, [pc, #0x594]\n    movs r2, #0xd8\n    ldr.w r1, [pc, #0x580]\n    movs r0, #2\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am016_addr_0044d25c\n    bl .\n    movw r6, #0x27f6\nL_open_cfw_runtime_am016_505a2_002c:\n    cmp r5, r7\n    blo L_open_cfw_runtime_am016_505a2_004c\n    str r5, [sp, #4]\n    ldr.w r0, [pc, #0x57c]\n    str r0, [sp]\n    ldr.w r3, [pc, #0x574]\n    movs r2, #0xdc\n    ldr.w r1, [pc, #0x560]\n    movs r0, #2\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am016_addr_0044d25c\n    bl .\n    movw r5, #0x27f6\nL_open_cfw_runtime_am016_505a2_004c:\n    cmp r4, r7\n    blo L_open_cfw_runtime_am016_505a2_006c\n    str r4, [sp, #4]\n    ldr.w r0, [pc, #0x560]\n    str r0, [sp]\n    ldr.w r3, [pc, #0x554]\n    movs r2, #0xe0\n    ldr.w r1, [pc, #0x540]\n    movs r0, #2\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am016_addr_0044d25c\n    bl .\n    movw r4, #0x27f6\nL_open_cfw_runtime_am016_505a2_006c:\n    adds r6, r6, #5\n    movs r0, #0xa\n    udiv r0, r6, r0\n    adds r5, r5, #5\n    movs r1, #0xa\n    udiv r1, r5, r1\n    adds r4, r4, #5\n    movs r2, #0xa\n    udiv r2, r4, r2\n    lsls r1, r1, #0xa\n    adds.w r1, r1, r2, lsl #20\n    adds r0, r0, r1\n    adds.w r0, r0, #-0x80000000\n    pop {r1, r2, r3, r4, r5, r6, r7, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM016_50634_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am016_50634(void)
{
    __asm__ volatile(
        "    push {r2, r3, r4, lr}\n    movs r4, r0\n    mov.w r0, #0x400\n    str r0, [sp]\n    movs r3, #0\n    ldr r2, [r4, #0x30]\n    movs r1, #0\n    ldr r0, [r4, #0x34]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am016_addr_004888b4\n    bl .\n    ldr r2, [r4, #0x2c]\n    ldr r1, [r4, #0x24]\n    subs r2, r2, r1\n    muls r0, r2, r0\n    asrs r0, r0, #0xa\n    ldr r1, [r4, #0x24]\n    adds r0, r1, r0\n    pop {r1, r2, r4, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM016_506CE_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am016_506ce(void)
{
    __asm__ volatile(
        "    str r1, [r0, #0x24]\n    movs.w r1, #-0x80000000\n    str r1, [r0, #0x28]\n    str r2, [r0, #0x2c]\n    bx lr\n"
    );
}
#endif

#if defined(OPEN_CFW_AM016_506DA_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am016_506da(void)
{
    __asm__ volatile(
        "    ldrb.w r2, [r0, #0x5c]\n    bfi r2, r1, #4, #1\n    strb.w r2, [r0, #0x5c]\n    bx lr\n"
    );
}
#endif

#if defined(OPEN_CFW_AM016_506E8_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am016_506e8(void)
{
    __asm__ volatile(
        "    push {r4}\n    ldrsh.w r4, [sp, #4]\n    adds r0, #0x48\n    strh r1, [r0]\n    strh r3, [r0, #4]\n    strh r2, [r0, #2]\n    strh r4, [r0, #6]\n    pop {r4}\n    bx lr\n"
    );
}
#endif

#if defined(OPEN_CFW_AM016_506FC_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am016_506fc(void)
{
    __asm__ volatile(
        "    push {r4, r5}\n    cmp r0, #0\n    bpl L_open_cfw_runtime_am016_506fc_0058\n    subs r3, r1, r2\n    cmp r3, #1\n    blt L_open_cfw_runtime_am016_506fc_0010\n    subs r1, r1, r2\n    b L_open_cfw_runtime_am016_506fc_0012\nL_open_cfw_runtime_am016_506fc_0010:\n    subs r1, r2, r1\nL_open_cfw_runtime_am016_506fc_0012:\n    lsls r3, r0, #0x16\n    lsrs r3, r3, #0x16\n    movs r2, #0x64\n    muls r1, r2, r1\n    udiv r1, r1, r3\n    ubfx r2, r0, #0x14, #0xa\n    ubfx r0, r0, #0xa, #0xa\n    movs r3, #0xa\n    mul r4, r3, r2\n    cmp r1, r4\n    bhs L_open_cfw_runtime_am016_506fc_0034\n    movs r4, r1\n    b L_open_cfw_runtime_am016_506fc_0038\nL_open_cfw_runtime_am016_506fc_0034:\n    mul r4, r3, r2\nL_open_cfw_runtime_am016_506fc_0038:\n    mul r5, r3, r0\n    cmp r4, r5\n    bhs L_open_cfw_runtime_am016_506fc_0048\n    movs r1, r3\n    mul r1, r1, r0\n    b L_open_cfw_runtime_am016_506fc_0056\nL_open_cfw_runtime_am016_506fc_0048:\n    mul r0, r3, r2\n    cmp r1, r0\n    blo L_open_cfw_runtime_am016_506fc_0056\n    movs r1, r3\n    mul r1, r1, r2\nL_open_cfw_runtime_am016_506fc_0056:\n    movs r0, r1\nL_open_cfw_runtime_am016_506fc_0058:\n    pop {r4, r5}\n    bx lr\n"
    );
}
#endif

#if defined(OPEN_CFW_AM016_50758_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am016_50758(void)
{
    __asm__ volatile(
        "    push.w {r3, r4, r5, r6, r7, r8, sb, lr}\n    ldr.w r5, [pc, #0x3d0]\n    ldrb.w r0, [r5, #0xa5]\n    cmp r0, #0\n    bne L_open_cfw_runtime_am016_50758_0014\n    movs r0, #1\n    b L_open_cfw_runtime_am016_50758_0016\nL_open_cfw_runtime_am016_50758_0014:\n    movs r0, #0\nL_open_cfw_runtime_am016_50758_0016:\n    strb.w r0, [r5, #0xa5]\n    adds.w r6, r5, #0xac\n    movs r0, r6\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am016_addr_00482cd8\n    bl .\n    movs r4, r0\n    b L_open_cfw_runtime_am016_50758_0030\n    movs r0, r6\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am016_addr_00482cd8\n    bl .\n    movs r4, r0\nL_open_cfw_runtime_am016_50758_0030:\n    cmp r4, #0\n    beq.w #0x45090c\n    ldr r0, [r4, #0x50]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am016_addr_004734a0\n    bl .\n    ldrb.w r1, [r4, #0x5c]\n    lsls r1, r1, #0x1f\n    bpl L_open_cfw_runtime_am016_50758_0096\n    ldr r0, [r4, #0x54]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am016_addr_004734a0\n    bl .\n    ldr r1, [r4, #0x58]\n    cmn.w r1, #1\n    beq L_open_cfw_runtime_am016_50758_005c\n    ldr r1, [r4, #0x58]\n    cmp r0, r1\n    blo L_open_cfw_runtime_am016_50758_005c\n    movs r1, #1\n    b L_open_cfw_runtime_am016_50758_005e\nL_open_cfw_runtime_am016_50758_005c:\n    movs r1, #0\nL_open_cfw_runtime_am016_50758_005e:\n    uxtb r1, r1\n    cmp r1, #0\n    beq L_open_cfw_runtime_am016_50758_009c\n    ldr r1, [r4, #0x58]\n    subs r0, r0, r1\n    ldrb.w r1, [r4, #0x5c]\n    ands r1, r1, #0xfe\n    strb.w r1, [r4, #0x5c]\n    ldr r1, [r4, #0x34]\n    adds r0, r0, r1\n    str r0, [r4, #0x34]\n    ldrb.w r0, [r5, #0xa5]\n    cmp r0, #0\n    bne L_open_cfw_runtime_am016_50758_0086\n    movs r0, #1\n    b L_open_cfw_runtime_am016_50758_0088\nL_open_cfw_runtime_am016_50758_0086:\n    movs r0, #0\nL_open_cfw_runtime_am016_50758_0088:\n    ldrb.w r1, [r4, #0x5c]\n    bfi r1, r0, #2, #1\n    strb.w r1, [r4, #0x5c]\n    b L_open_cfw_runtime_am016_50758_009c\nL_open_cfw_runtime_am016_50758_0096:\n    ldr r1, [r4, #0x34]\n    adds r0, r0, r1\n    str r0, [r4, #0x34]\nL_open_cfw_runtime_am016_50758_009c:\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am016_addr_00473482\n    bl .\n    str r0, [r4, #0x50]\n    movs r0, #0\n    strb.w r0, [r5, #0xa4]\n    ldrb.w r0, [r4, #0x5c]\n    lsls r0, r0, #0x1f\n    bmi L_open_cfw_runtime_am016_50758_019e\n    ldrb.w r0, [r4, #0x5c]\n    ubfx r0, r0, #2, #1\n    ands r0, r0, #1\n    ldrb.w r1, [r5, #0xa5]\n    cmp r0, r1\n    beq L_open_cfw_runtime_am016_50758_019e\n    ldrb.w r0, [r5, #0xa5]\n    ldrb.w r1, [r4, #0x5c]\n    bfi r1, r0, #2, #1\n    strb.w r1, [r4, #0x5c]\n    ldrb.w r0, [r4, #0x5c]\n    ubfx r0, r0, #3, #1\n    uxtb r0, r0\n    cmp r0, #0\n    bne L_open_cfw_runtime_am016_50758_0132\n    ldr r0, [r4, #0x34]\n    cmp r0, #0\n    bmi L_open_cfw_runtime_am016_50758_0132\n    ldrb.w r0, [r4, #0x5c]\n    ubfx r0, r0, #4, #1\n    uxtb r0, r0\n    cmp r0, #0\n    bne L_open_cfw_runtime_am016_50758_010e\n    ldr r0, [r4, #0x18]\n    cmp r0, #0\n    beq L_open_cfw_runtime_am016_50758_010e\n    movs r0, r4\n    ldr r1, [r4, #0x18]\n    blx r1\n    ldr r1, [r4, #0x24]\n    adds r1, r0, r1\n    str r1, [r4, #0x24]\n    ldr r1, [r4, #0x2c]\n    adds r0, r0, r1\n    str r0, [r4, #0x2c]\nL_open_cfw_runtime_am016_50758_010e:\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am016_50a3e\n    bl .\n    ldr r0, [r4, #0xc]\n    cmp r0, #0\n    beq L_open_cfw_runtime_am016_50758_0120\n    movs r0, r4\n    ldr r1, [r4, #0xc]\n    blx r1\nL_open_cfw_runtime_am016_50758_0120:\n    ldrb.w r0, [r4, #0x5c]\n    orrs r0, r0, #8\n    strb.w r0, [r4, #0x5c]\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am016_50a74\n    bl .\nL_open_cfw_runtime_am016_50758_0132:\n    ldr r0, [r4, #0x34]\n    cmp r0, #0\n    bmi L_open_cfw_runtime_am016_50758_019e\n    ldr r7, [r4, #0x34]\n    ldr r0, [r4, #0x30]\n    ldr r1, [r4, #0x34]\n    cmp r0, r1\n    bge L_open_cfw_runtime_am016_50758_0146\n    ldr r0, [r4, #0x30]\n    str r0, [r4, #0x34]\nL_open_cfw_runtime_am016_50758_0146:\n    ldr.w r8, [r4, #0x34]\n    movs r0, r4\n    ldr r1, [r4, #0x20]\n    blx r1\n    mov sb, r0\n    ldr r0, [r4, #0x28]\n    cmp sb, r0\n    beq L_open_cfw_runtime_am016_50758_0180\n    str.w sb, [r4, #0x28]\n    ldr r0, [r4, #4]\n    cmp r0, #0\n    beq L_open_cfw_runtime_am016_50758_016a\n    mov r1, sb\n    ldr r0, [r4]\n    ldr r2, [r4, #4]\n    blx r2\nL_open_cfw_runtime_am016_50758_016a:\n    ldrb.w r0, [r5, #0xa4]\n    cmp r0, #0\n    bne L_open_cfw_runtime_am016_50758_0180\n    ldr r0, [r4, #8]\n    cmp r0, #0\n    beq L_open_cfw_runtime_am016_50758_0180\n    mov r1, sb\n    movs r0, r4\n    ldr r2, [r4, #8]\n    blx r2\nL_open_cfw_runtime_am016_50758_0180:\n    ldrb.w r0, [r5, #0xa4]\n    cmp r0, #0\n    bne L_open_cfw_runtime_am016_50758_019e\n    ldr r0, [r4, #0x34]\n    cmp r0, r8\n    bne L_open_cfw_runtime_am016_50758_0190\n    str r7, [r4, #0x34]\nL_open_cfw_runtime_am016_50758_0190:\n    ldr r0, [r4, #0x34]\n    ldr r1, [r4, #0x30]\n    cmp r0, r1\n    blt L_open_cfw_runtime_am016_50758_019e\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am016_50910\n    bl .\nL_open_cfw_runtime_am016_50758_019e:\n    ldrb.w r0, [r5, #0xa4]\n    cmp r0, #0\n    bne.w #0x450780\n    movs r1, r4\n    movs r0, r6\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am016_addr_00482cf0\n    bl .\n    movs r4, r0\n    b L_open_cfw_runtime_am016_50758_0030\n    pop.w {r0, r4, r5, r6, r7, r8, sb, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM016_50910_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am016_50910(void)
{
    __asm__ volatile(
        "    push {r4, lr}\n    movs r4, r0\n    ldrb.w r0, [r4, #0x5c]\n    ubfx r0, r0, #1, #1\n    uxtb r0, r0\n    cmp r0, #0\n    bne L_open_cfw_runtime_am016_50910_0026\n    ldr r0, [r4, #0x44]\n    cmp r0, #0\n    beq L_open_cfw_runtime_am016_50910_0026\n    ldr r0, [r4, #0x44]\n    cmn.w r0, #1\n    beq L_open_cfw_runtime_am016_50910_0026\n    ldr r0, [r4, #0x44]\n    subs r0, r0, #1\n    str r0, [r4, #0x44]\nL_open_cfw_runtime_am016_50910_0026:\n    ldr r0, [r4, #0x44]\n    cmp r0, #0\n    bne L_open_cfw_runtime_am016_50910_006c\n    ldr r0, [r4, #0x3c]\n    cmp r0, #0\n    beq L_open_cfw_runtime_am016_50910_0040\n    ldrb.w r0, [r4, #0x5c]\n    ubfx r0, r0, #1, #1\n    uxtb r0, r0\n    cmp r0, #0\n    beq L_open_cfw_runtime_am016_50910_006c\nL_open_cfw_runtime_am016_50910_0040:\n    movs r1, r4\n    ldr r0, [pc, #0x1f4]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am016_addr_00482c0e\n    bl .\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am016_509da\n    bl .\n    ldr r0, [r4, #0x10]\n    cmp r0, #0\n    beq L_open_cfw_runtime_am016_50910_0058\n    movs r0, r4\n    ldr r1, [r4, #0x10]\n    blx r1\nL_open_cfw_runtime_am016_50910_0058:\n    ldr r0, [r4, #0x14]\n    cmp r0, #0\n    beq L_open_cfw_runtime_am016_50910_0064\n    movs r0, r4\n    ldr r1, [r4, #0x14]\n    blx r1\nL_open_cfw_runtime_am016_50910_0064:\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am016_addr_0044f758\n    bl .\n    b L_open_cfw_runtime_am016_50910_00c8\nL_open_cfw_runtime_am016_50910_006c:\n    movs r1, #0\n    ldr r0, [r4, #0x30]\n    ldr r2, [r4, #0x34]\n    cmp r0, r2\n    bge L_open_cfw_runtime_am016_50910_007c\n    ldr r1, [r4, #0x34]\n    ldr r0, [r4, #0x30]\n    subs r1, r1, r0\nL_open_cfw_runtime_am016_50910_007c:\n    ldr r0, [r4, #0x40]\n    subs r1, r1, r0\n    str r1, [r4, #0x34]\n    ldr r0, [r4, #0x3c]\n    cmp r0, #0\n    beq L_open_cfw_runtime_am016_50910_00c8\n    ldrb.w r0, [r4, #0x5c]\n    ubfx r0, r0, #1, #1\n    uxtb r0, r0\n    cmp r0, #0\n    bne L_open_cfw_runtime_am016_50910_009c\n    ldr r0, [r4, #0x38]\n    rsbs r0, r0, #0\n    str r0, [r4, #0x34]\nL_open_cfw_runtime_am016_50910_009c:\n    ldrb.w r0, [r4, #0x5c]\n    uxtb r0, r0\n    lsrs r0, r0, #1\n    ands r0, r0, #1\n    eors r0, r0, #1\n    ldrb.w r1, [r4, #0x5c]\n    bfi r1, r0, #1, #1\n    strb.w r1, [r4, #0x5c]\n    ldr r0, [r4, #0x24]\n    ldr r1, [r4, #0x2c]\n    str r1, [r4, #0x24]\n    str r0, [r4, #0x2c]\n    ldr r0, [r4, #0x30]\n    ldr r1, [r4, #0x3c]\n    str r1, [r4, #0x30]\n    str r0, [r4, #0x3c]\nL_open_cfw_runtime_am016_50910_00c8:\n    pop {r4, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM016_509DA_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am016_509da(void)
{
    __asm__ volatile(
        "    push {r4, lr}\n    ldr r4, [pc, #0x150]\n    movs r0, #1\n    strb.w r0, [r4, #0xa4]\n    adds.w r0, r4, #0xac\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am016_addr_00482cd8\n    bl .\n    cmp r0, #0\n    bne L_open_cfw_runtime_am016_509da_0020\n    ldr.w r0, [r4, #0xa8]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am016_addr_0046450c\n    bl .\n    b L_open_cfw_runtime_am016_509da_0028\nL_open_cfw_runtime_am016_509da_0020:\n    ldr.w r0, [r4, #0xa8]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am016_addr_0046453e\n    bl .\nL_open_cfw_runtime_am016_509da_0028:\n    pop {r4, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM016_50A04_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am016_50a04(void)
{
    __asm__ volatile(
        "    push {r3, r4, r5, r6, r7, lr}\n    movs r4, r0\n    movs r5, r1\n    movs r6, r2\n    movs r7, r3\n    mov.w r0, #0x400\n    str r0, [sp]\n    movs r3, #0\n    ldr r2, [r4, #0x30]\n    movs r1, #0\n    ldr r0, [r4, #0x34]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am016_addr_004888b4\n    bl .\n    ldr r1, [sp, #0x18]\n    str r1, [sp]\n    movs r3, r7\n    movs r2, r6\n    movs r1, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am016_addr_0048869a\n    bl .\n    ldr r2, [r4, #0x2c]\n    ldr r1, [r4, #0x24]\n    subs r2, r2, r1\n    muls r0, r2, r0\n    asrs r0, r0, #0xa\n    ldr r1, [r4, #0x24]\n    adds r0, r1, r0\n    pop {r1, r4, r5, r6, r7, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM016_50A3E_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am016_50a3e(void)
{
    __asm__ volatile(
        "    push {r4, lr}\n    movs r4, r0\n    ldr r2, [r4, #0x2c]\n    ldr r1, [r4, #0x24]\n    ldr r0, [r4, #0x30]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am016_506fc\n    bl .\n    str r0, [r4, #0x30]\n    ldr r2, [r4, #0x2c]\n    ldr r1, [r4, #0x24]\n    ldr r0, [r4, #0x3c]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am016_506fc\n    bl .\n    str r0, [r4, #0x3c]\n    ldr r2, [r4, #0x2c]\n    ldr r1, [r4, #0x24]\n    ldr r0, [r4, #0x38]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am016_506fc\n    bl .\n    str r0, [r4, #0x38]\n    ldr r2, [r4, #0x2c]\n    ldr r1, [r4, #0x24]\n    ldr r0, [r4, #0x40]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am016_506fc\n    bl .\n    str r0, [r4, #0x40]\n    pop {r4, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM016_50A74_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am016_50a74(void)
{
    __asm__ volatile(
        "    push {r3, r4, r5, r6, r7, lr}\n    movs r5, r0\n    ldr r0, [r5, #4]\n    cmp r0, #0\n    bne L_open_cfw_runtime_am016_50a74_0014\n    ldr r0, [r5, #8]\n    cmp r0, #0\n    bne L_open_cfw_runtime_am016_50a74_0014\n    movs r0, #0\n    b L_open_cfw_runtime_am016_50a74_0096\nL_open_cfw_runtime_am016_50a74_0014:\n    movs r7, #0\n    ldr r6, [pc, #0xbc]\n    movs r0, r6\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am016_addr_00482cd8\n    bl .\n    movs r4, r0\n    b L_open_cfw_runtime_am016_50a74_008e\nL_open_cfw_runtime_am016_50a74_0022:\n    movs r1, r4\n    movs r0, r6\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am016_addr_00482cf0\n    bl .\n    movs r4, r0\n    b L_open_cfw_runtime_am016_50a74_008e\nL_open_cfw_runtime_am016_50a74_002e:\n    movs r1, #0\n    cmp r4, r5\n    beq L_open_cfw_runtime_am016_50a74_0080\n    ldr r0, [r4, #0x34]\n    cmp r0, #0\n    bpl L_open_cfw_runtime_am016_50a74_0048\n    ldrb.w r0, [r4, #0x5c]\n    ubfx r0, r0, #4, #1\n    uxtb r0, r0\n    cmp r0, #0\n    beq L_open_cfw_runtime_am016_50a74_0080\nL_open_cfw_runtime_am016_50a74_0048:\n    ldr r0, [r4]\n    ldr r2, [r5]\n    cmp r0, r2\n    bne L_open_cfw_runtime_am016_50a74_0080\n    ldr r0, [r4, #4]\n    cmp r0, #0\n    beq L_open_cfw_runtime_am016_50a74_0080\n    ldr r0, [r4, #4]\n    ldr r2, [r5, #4]\n    cmp r0, r2\n    bne L_open_cfw_runtime_am016_50a74_0080\n    movs r1, r4\n    movs r0, r6\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am016_addr_00482c0e\n    bl .\n    ldr r0, [r4, #0x14]\n    cmp r0, #0\n    beq L_open_cfw_runtime_am016_50a74_0072\n    movs r0, r4\n    ldr r1, [r4, #0x14]\n    blx r1\nL_open_cfw_runtime_am016_50a74_0072:\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am016_addr_0044f758\n    bl .\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am016_509da\n    bl .\n    movs r7, #1\n    movs r1, #1\nL_open_cfw_runtime_am016_50a74_0080:\n    uxtb r1, r1\n    cmp r1, #0\n    beq L_open_cfw_runtime_am016_50a74_0022\n    movs r0, r6\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am016_addr_00482cd8\n    bl .\n    movs r4, r0\nL_open_cfw_runtime_am016_50a74_008e:\n    cmp r4, #0\n    bne L_open_cfw_runtime_am016_50a74_002e\n    movs r0, r7\n    uxtb r0, r0\nL_open_cfw_runtime_am016_50a74_0096:\n    pop {r1, r4, r5, r6, r7, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM016_50B0C_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am016_50b0c(void)
{
    __asm__ volatile(
        "    push {r3, r4, r5, lr}\n    movs r4, r0\n    movs r5, r4\n    movs r1, r4\n    ldr r0, [pc, #0x30]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am016_addr_00482c0e\n    bl .\n    ldr r0, [r5, #0x14]\n    cmp r0, #0\n    beq L_open_cfw_runtime_am016_50b0c_001a\n    movs r0, r5\n    ldr r1, [r5, #0x14]\n    blx r1\nL_open_cfw_runtime_am016_50b0c_001a:\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am016_addr_0044f758\n    bl .\n    pop {r0, r4, r5, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM016_50B5C_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am016_50b5c(void)
{
    __asm__ volatile(
        "    push {r4}\n    ldr r4, [sp, #4]\n    str r1, [r0]\n    str r2, [r0, #4]\n    str r3, [r0, #8]\n    str r4, [r0, #0xc]\n    pop {r4}\n    bx lr\n"
    );
}
#endif

#if defined(OPEN_CFW_AM016_50B6C_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am016_50b6c(void)
{
    __asm__ volatile(
        "    ldr r2, [r0]\n    adds r1, r1, r2\n    subs r1, r1, #1\n    str r1, [r0, #8]\n    bx lr\n"
    );
}
#endif

#if defined(OPEN_CFW_AM016_50B76_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am016_50b76(void)
{
    __asm__ volatile(
        "    ldr r2, [r0, #4]\n    adds r1, r1, r2\n    subs r1, r1, #1\n    str r1, [r0, #0xc]\n    bx lr\n"
    );
}
#endif
