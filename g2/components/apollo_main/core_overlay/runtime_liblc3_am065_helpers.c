/*
 * SPDX-License-Identifier: MIT
 *
 * Source-owned exact helpers from the AM-065 retained island.
 */

#if defined(OPEN_CFW_AM065_D3944_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am065_d3944(void)
{
    __asm__ volatile(
        "    ldr r0, [pc, #0xc4]\n    ldr r1, [r0]\n    lsrs r1, r1, #1\n    lsls r1, r1, #1\n    str r1, [r0]\n    movs r0, #0\n    bx lr\n"
    );
}
#endif

#if defined(OPEN_CFW_AM065_D3952_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am065_d3952(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    uxtb r0, r0\n    cmp r0, #0\n    beq L_open_cfw_runtime_am065_d3952_0032\n    ldr r1, [pc, #0xac]\n    ldr r0, [r1]\n    ubfx r0, r0, #5, #1\n    cmp r0, #0\n    bne L_open_cfw_runtime_am065_d3952_003c\n    ldr r0, [r1]\n    orrs r0, r0, #0x20\n    str r0, [r1]\n    movs r0, #1\n    str r0, [sp]\n    movs.w r3, #0x1000000\n    movs.w r2, #0x1000000\n    ldr r1, [pc, #0x94]\n    movs r0, #0x64\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am065_addr_00480826\n    bl .\n    b L_open_cfw_runtime_am065_d3952_003e\nL_open_cfw_runtime_am065_d3952_0032:\n    ldr r0, [pc, #0x80]\n    ldr r1, [r0]\n    bics r1, r1, #0x20\n    str r1, [r0]\nL_open_cfw_runtime_am065_d3952_003c:\n    movs r0, #0\nL_open_cfw_runtime_am065_d3952_003e:\n    pop {r1, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM065_D3992_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am065_d3992(void)
{
    __asm__ volatile(
        "    push {r4}\n    cmp r0, #0\n    bne L_open_cfw_runtime_am065_d3992_000a\n    movs r0, #6\n    b L_open_cfw_runtime_am065_d3992_004e\nL_open_cfw_runtime_am065_d3992_000a:\n    ldr r1, [pc, #0x74]\n    ldr r2, [r1]\n    orrs r2, r2, #7\n    str r2, [r1]\n    ldrb r1, [r0]\n    ands r1, r1, #1\n    ldr r2, [pc, #0x68]\n    ldr r3, [r2]\n    bfi r3, r1, #0x1d, #1\n    str r3, [r2]\n    ldrb r1, [r0, #1]\n    ands r1, r1, #3\n    ldr r3, [pc, #0x5c]\n    ldr r4, [r3]\n    lsrs r4, r4, #2\n    lsls r4, r4, #2\n    orrs r1, r4\n    str r1, [r3]\n    ldr r0, [r0, #4]\n    bic r0, r0, #0xe0000000\n    ldr r1, [r3]\n    bfi r1, r0, #2, #0x1d\n    str r1, [r3]\n    ldr r0, [r2]\n    orrs r0, r0, #1\n    str r0, [r2]\n    movs r0, #0\nL_open_cfw_runtime_am065_d3992_004e:\n    pop {r4}\n    bx lr\n"
    );
}
#endif

#if defined(OPEN_CFW_AM065_D39E4_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am065_d39e4(void)
{
    __asm__ volatile(
        "    ldr r0, [pc, #0x30]\n    ldr r1, [r0]\n    lsrs r1, r1, #1\n    lsls r1, r1, #1\n    str r1, [r0]\n    movs r0, #0\n    bx lr\n"
    );
}
#endif

#if defined(OPEN_CFW_AM065_D3A20_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am065_d3a20(void)
{
    __asm__ volatile(
        "    movs r1, r0\n    uxtb r1, r1\n    lsrs r1, r1, #4\n    uxtb r1, r1\n    movs r2, #0xa\n    uxtb r0, r0\n    ands r0, r0, #0xf\n    mla r0, r2, r1, r0\n    uxtb r0, r0\n    bx lr\n"
    );
}
#endif

#if defined(OPEN_CFW_AM065_D3A38_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am065_d3a38(void)
{
    __asm__ volatile(
        "    movs r1, r0\n    movs r0, r1\n    uxtb r0, r0\n    movs r2, #0xa\n    uxtb r1, r1\n    movs r3, #0xa\n    sdiv r1, r1, r3\n    sdiv r3, r0, r2\n    mls r0, r2, r3, r0\n    orrs.w r0, r0, r1, lsl #4\n    uxtb r0, r0\n    bx lr\n"
    );
}
#endif

#if defined(OPEN_CFW_AM065_D3A58_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am065_d3a58(void)
{
    __asm__ volatile(
        "    movs r2, r0\n    movs r0, #1\n    ldr r1, [r2, #0x24]\n    cmp r1, #0x64\n    blo L_open_cfw_runtime_am065_d3a58_0010\n    movs r0, #0\n    uxtb r0, r0\n    b L_open_cfw_runtime_am065_d3a58_0072\nL_open_cfw_runtime_am065_d3a58_0010:\n    ldr r1, [r2, #0x20]\n    cmp r1, #0x3c\n    blo L_open_cfw_runtime_am065_d3a58_001c\n    movs r0, #0\n    uxtb r0, r0\n    b L_open_cfw_runtime_am065_d3a58_0072\nL_open_cfw_runtime_am065_d3a58_001c:\n    ldr r1, [r2, #0x1c]\n    cmp r1, #0x3c\n    blo L_open_cfw_runtime_am065_d3a58_0028\n    movs r0, #0\n    uxtb r0, r0\n    b L_open_cfw_runtime_am065_d3a58_0072\nL_open_cfw_runtime_am065_d3a58_0028:\n    ldr r1, [r2, #0x18]\n    cmp r1, #0x18\n    blo L_open_cfw_runtime_am065_d3a58_0034\n    movs r0, #0\n    uxtb r0, r0\n    b L_open_cfw_runtime_am065_d3a58_0072\nL_open_cfw_runtime_am065_d3a58_0034:\n    ldr r1, [r2, #0x14]\n    cmp r1, #0\n    beq L_open_cfw_runtime_am065_d3a58_0040\n    ldr r1, [r2, #0x14]\n    cmp r1, #0x20\n    blo L_open_cfw_runtime_am065_d3a58_0046\nL_open_cfw_runtime_am065_d3a58_0040:\n    movs r0, #0\n    uxtb r0, r0\n    b L_open_cfw_runtime_am065_d3a58_0072\nL_open_cfw_runtime_am065_d3a58_0046:\n    ldr r1, [r2, #0x10]\n    cmp r1, #0\n    beq L_open_cfw_runtime_am065_d3a58_0052\n    ldr r1, [r2, #0x10]\n    cmp r1, #0xd\n    blo L_open_cfw_runtime_am065_d3a58_0058\nL_open_cfw_runtime_am065_d3a58_0052:\n    movs r0, #0\n    uxtb r0, r0\n    b L_open_cfw_runtime_am065_d3a58_0072\nL_open_cfw_runtime_am065_d3a58_0058:\n    ldr r1, [r2, #0xc]\n    cmp r1, #0x65\n    blo L_open_cfw_runtime_am065_d3a58_0064\n    movs r0, #0\n    uxtb r0, r0\n    b L_open_cfw_runtime_am065_d3a58_0072\nL_open_cfw_runtime_am065_d3a58_0064:\n    ldr r1, [r2, #4]\n    cmp r1, #7\n    blo L_open_cfw_runtime_am065_d3a58_0070\n    movs r0, #0\n    uxtb r0, r0\n    b L_open_cfw_runtime_am065_d3a58_0072\nL_open_cfw_runtime_am065_d3a58_0070:\n    uxtb r0, r0\nL_open_cfw_runtime_am065_d3a58_0072:\n    bx lr\n"
    );
}
#endif

#if defined(OPEN_CFW_AM065_D3ADC_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am065_d3adc(void)
{
    __asm__ volatile(
        "    push {r3, r4, r5, r6, r7, lr}\n    movs r4, r0\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am065_d3a58\n    bl .\n    cmp r0, #0\n    bne L_open_cfw_runtime_am065_d3adc_0012\n    movs r0, #1\n    b L_open_cfw_runtime_am065_d3adc_00bc\nL_open_cfw_runtime_am065_d3adc_0012:\n    ldr.w r5, [pc, #0x1e4]\n    ldr r0, [r5]\n    orrs r0, r0, #1\n    str r0, [r5]\n    ldr r0, [r4, #0x18]\n    uxtb r0, r0\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am065_d3a38\n    bl .\n    movs r6, r0\n    ldr r0, [r4, #0x1c]\n    uxtb r0, r0\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am065_d3a38\n    bl .\n    movs r7, r0\n    ldr r0, [r4, #0x20]\n    uxtb r0, r0\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am065_d3a38\n    bl .\n    uxtb r6, r6\n    lsls r6, r6, #0x18\n    ands r6, r6, #0x3f000000\n    uxtb r7, r7\n    lsls r7, r7, #0x10\n    ands r7, r7, #0x7f0000\n    orrs r6, r7\n    uxtb r0, r0\n    lsls r0, r0, #8\n    ands r0, r0, #0x7f00\n    orrs r6, r0\n    ldr r0, [r4, #0x24]\n    uxtb r0, r0\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am065_d3a38\n    bl .\n    orrs r6, r0\n    ldr.w r0, [pc, #0x198]\n    str r6, [r0]\n    ldr r0, [r4, #0xc]\n    uxtb r0, r0\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am065_d3a38\n    bl .\n    movs r6, r0\n    ldr r0, [r4, #0x10]\n    uxtb r0, r0\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am065_d3a38\n    bl .\n    movs r7, r0\n    ldr r0, [r4, #0x14]\n    uxtb r0, r0\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am065_d3a38\n    bl .\n    ldr r1, [r4, #8]\n    lsls r1, r1, #0x1c\n    ands r1, r1, #0x10000000\n    ldr r2, [r4, #4]\n    lsls r2, r2, #0x18\n    ands r2, r2, #0x7000000\n    orrs r1, r2\n    uxtb r6, r6\n    orrs.w r1, r1, r6, lsl #16\n    uxtb r7, r7\n    lsls r7, r7, #8\n    ands r7, r7, #0x1f00\n    orrs r7, r1\n    uxtb r0, r0\n    ands r0, r0, #0x3f\n    orrs r7, r0\n    ldr.w r0, [pc, #0x150]\n    str r7, [r0]\n    ldr r0, [r5]\n    lsrs r0, r0, #1\n    lsls r0, r0, #1\n    str r0, [r5]\n    movs r0, #0\nL_open_cfw_runtime_am065_d3adc_00bc:\n    pop {r1, r4, r5, r6, r7, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM065_D3B9A_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am065_d3b9a(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    movs r0, #0\n    ldr r0, [pc, #0x140]\n    ldr r1, [r0]\n    lsrs r1, r1, #1\n    lsls r1, r1, #1\n    str r1, [r0]\n    ldr r1, [pc, #0x124]\n    ldr r1, [r1]\n    lsls r1, r1, #0x18\n    bpl L_open_cfw_runtime_am065_d3b9a_001a\n    movs r1, #6\n    b L_open_cfw_runtime_am065_d3b9a_001c\nL_open_cfw_runtime_am065_d3b9a_001a:\n    movs r1, #0xa\nL_open_cfw_runtime_am065_d3b9a_001c:\n    ldr r2, [pc, #0x12c]\n    ands.w r2, r2, r1, lsl #8\n    orrs r2, r2, #0x10\n    str r2, [r0]\n    movs.w r1, #-1\n    ldr r2, [pc, #0x120]\n    str r1, [r2]\n    ldr r2, [pc, #0x120]\n    str r1, [r2]\n    ldr r1, [pc, #0x120]\n    ldr r2, [r1]\n    orrs r2, r2, #0x4000\n    str r2, [r1]\n    ldr r1, [r0]\n    orrs r1, r1, #2\n    str r1, [r0]\n    ldr r1, [r0]\n    bics r1, r1, #2\n    str r1, [r0]\n    ldr r1, [r0]\n    orrs r1, r1, #1\n    str r1, [r0]\n    ldr r2, [pc, #0x100]\n    ldr r1, [r2]\nL_open_cfw_runtime_am065_d3b9a_005a:\n    ldr r3, [r2]\n    cmp r1, r3\n    beq L_open_cfw_runtime_am065_d3b9a_005a\n    ldr r1, [r0]\n    lsrs r1, r1, #1\n    lsls r1, r1, #1\n    str r1, [r0]\n    movs r0, #0xa\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am065_addr_004807a0\n    bl .\n    pop {r0, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM065_D3C0A_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am065_d3c0a(void)
{
    __asm__ volatile(
        "    push {r2, r3, r4, r5, r6, lr}\n    movs r4, r0\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am065_addr_00473940\n    bl .\n    str r0, [sp]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am065_d3b9a\n    bl .\n    ldr r0, [pc, #0xbc]\n    ldr r6, [r0]\n    ldr r0, [pc, #0xbc]\n    ldr r5, [r0]\n    ldr r0, [sp]\n    msr primask, r0\n    movs r0, r5\n    lsrs r0, r0, #0x1f\n    str r0, [r4]\n    ldr r0, [r4]\n    cmp r0, #0\n    beq L_open_cfw_runtime_am065_d3c0a_002c\n    movs r0, #1\n    b L_open_cfw_runtime_am065_d3c0a_00a2\nL_open_cfw_runtime_am065_d3c0a_002c:\n    ubfx r0, r6, #0x18, #6\n    uxtb r0, r0\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am065_d3a20\n    bl .\n    str r0, [r4, #0x18]\n    ubfx r0, r6, #0x10, #7\n    uxtb r0, r0\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am065_d3a20\n    bl .\n    str r0, [r4, #0x1c]\n    ubfx r0, r6, #8, #7\n    uxtb r0, r0\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am065_d3a20\n    bl .\n    str r0, [r4, #0x20]\n    and r6, r6, #0xff\n    movs r0, r6\n    uxtb r0, r0\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am065_d3a20\n    bl .\n    str r0, [r4, #0x24]\n    ubfx r0, r5, #0x1c, #1\n    str r0, [r4, #8]\n    ubfx r0, r5, #0x18, #3\n    uxtb r0, r0\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am065_d3a20\n    bl .\n    str r0, [r4, #4]\n    ubfx r0, r5, #0x10, #8\n    uxtb r0, r0\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am065_d3a20\n    bl .\n    str r0, [r4, #0xc]\n    ubfx r0, r5, #8, #5\n    uxtb r0, r0\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am065_d3a20\n    bl .\n    str r0, [r4, #0x10]\n    ands r5, r5, #0x3f\n    movs r0, r5\n    uxtb r0, r0\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am065_d3a20\n    bl .\n    str r0, [r4, #0x14]\n    ldr r0, [r4]\n    cmp r0, #0\n    beq L_open_cfw_runtime_am065_d3c0a_00a0\n    movs r0, #1\n    b L_open_cfw_runtime_am065_d3c0a_00a2\nL_open_cfw_runtime_am065_d3c0a_00a0:\n    movs r0, #0\nL_open_cfw_runtime_am065_d3c0a_00a2:\n    pop {r1, r2, r4, r5, r6, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM065_D3CF8_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am065_d3cf8(void)
{
    __asm__ volatile(
        "    push {r4, r5, r6, r7}\n    movs r4, #0\n    subs r3, r1, #1\n    cmp r3, #0xc\n    bhs L_open_cfw_runtime_am065_d3cf8_0012\n    cmp r0, #0\n    bmi L_open_cfw_runtime_am065_d3cf8_0012\n    cmp r2, #1\n    bge L_open_cfw_runtime_am065_d3cf8_0016\nL_open_cfw_runtime_am065_d3cf8_0012:\n    movs r0, #7\n    b L_open_cfw_runtime_am065_d3cf8_00c8\nL_open_cfw_runtime_am065_d3cf8_0016:\n    ldr r3, [pc, #0xb4]\n    add.w r3, r3, r1, lsl #2\n    ldr r3, [r3, #-0x4]\n    cmp r3, r2\n    bhs L_open_cfw_runtime_am065_d3cf8_0058\n    cmp r1, #2\n    bne L_open_cfw_runtime_am065_d3cf8_0054\n    tst.w r0, #3\n    bne L_open_cfw_runtime_am065_d3cf8_0054\n    movs r3, #0x64\n    sdiv r5, r0, r3\n    mls r3, r3, r5, r0\n    cmp r3, #0\n    bne L_open_cfw_runtime_am065_d3cf8_004c\n    mov.w r3, #0x190\n    sdiv r5, r0, r3\n    mls r3, r3, r5, r0\n    cmp r3, #0\n    beq L_open_cfw_runtime_am065_d3cf8_0054\nL_open_cfw_runtime_am065_d3cf8_004c:\n    cmp r2, #0x1d\n    bne L_open_cfw_runtime_am065_d3cf8_0054\n    movs r3, #0\n    b L_open_cfw_runtime_am065_d3cf8_005a\nL_open_cfw_runtime_am065_d3cf8_0054:\n    movs r3, #1\n    b L_open_cfw_runtime_am065_d3cf8_005a\nL_open_cfw_runtime_am065_d3cf8_0058:\n    movs r3, #0\nL_open_cfw_runtime_am065_d3cf8_005a:\n    uxtb r3, r3\n    cmp r3, #0\n    beq L_open_cfw_runtime_am065_d3cf8_0064\n    movs r0, #7\n    b L_open_cfw_runtime_am065_d3cf8_00c8\nL_open_cfw_runtime_am065_d3cf8_0064:\n    movs r3, #4\n    sdiv r6, r0, r3\n    adds r6, r6, r0\n    adds r6, r6, #2\n    movs r3, #0x64\n    sdiv r3, r0, r3\n    subs r6, r6, r3\n    mov.w r3, #0x190\n    sdiv r5, r0, r3\n    adds r5, r5, r6\n    ldr r3, [pc, #0x4c]\n    add.w r3, r3, r1, lsl #2\n    ldr r6, [r3, #-0x4]\n    tst.w r0, #3\n    bne L_open_cfw_runtime_am065_d3cf8_00b6\n    movs r3, #0x64\n    sdiv r7, r0, r3\n    mls r3, r3, r7, r0\n    cmp r3, #0\n    bne L_open_cfw_runtime_am065_d3cf8_00ae\n    mov.w r3, #0x190\n    sdiv r7, r0, r3\n    mls r0, r3, r7, r0\n    cmp r0, #0\n    beq L_open_cfw_runtime_am065_d3cf8_00b6\nL_open_cfw_runtime_am065_d3cf8_00ae:\n    cmp r1, #3\n    bge L_open_cfw_runtime_am065_d3cf8_00b6\n    movs.w r4, #-1\nL_open_cfw_runtime_am065_d3cf8_00b6:\n    adds r2, r5, r2\n    adds r2, r6, r2\n    adds r2, r4, r2\n    movs r0, #7\n    sdiv r1, r2, r0\n    mls r2, r0, r1, r2\n    movs r0, r2\nL_open_cfw_runtime_am065_d3cf8_00c8:\n    pop {r4, r5, r6, r7}\n    bx lr\n"
    );
}
#endif

#if defined(OPEN_CFW_AM065_D3DCC_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am065_d3dcc(void)
{
    __asm__ volatile(
        "    bx lr\n"
    );
}
#endif

#if defined(OPEN_CFW_AM065_D3DCE_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am065_d3dce(void)
{
    __asm__ volatile(
        "    cmp.w r0, #0x200\n    blo L_open_cfw_runtime_am065_d3dce_000a\n    adds.w r0, r0, #0x280\nL_open_cfw_runtime_am065_d3dce_000a:\n    bx lr\n"
    );
}
#endif

#if defined(OPEN_CFW_AM065_D3DDA_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am065_d3dda(void)
{
    __asm__ volatile(
        "    push.w {r4, r5, r6, r7, r8, lr}\n    movs r6, r0\n    movs r0, r1\n    movs r4, r3\n    movs r5, #0\n    ldr.w r1, [pc, #0x17c]\n    ldr r1, [r1]\n    mov ip, r1\n    lsrs.w ip, ip, #4\n    ands ip, ip, #1\n    lsrs r1, r1, #3\n    ands r1, r1, #1\n    ldr.w r7, [pc, #0x168]\n    ldr r7, [r7]\n    ubfx lr, r7, #0x1b, #1\n    ands lr, lr, #1\n    cmp r4, #0\n    bne L_open_cfw_runtime_am065_d3dda_0038\n    movs r0, #6\n    b L_open_cfw_runtime_am065_d3dda_015e\nL_open_cfw_runtime_am065_d3dda_0038:\n    movs r7, r6\n    uxtb r7, r7\n    cmp r7, #0\n    beq L_open_cfw_runtime_am065_d3dda_0052\n    cmp r7, #2\n    beq L_open_cfw_runtime_am065_d3dda_0070\n    blo L_open_cfw_runtime_am065_d3dda_007c\n    cmp r7, #4\n    beq L_open_cfw_runtime_am065_d3dda_0076\n    blo L_open_cfw_runtime_am065_d3dda_0090\n    cmp r7, #5\n    beq L_open_cfw_runtime_am065_d3dda_0096\n    b L_open_cfw_runtime_am065_d3dda_009c\nL_open_cfw_runtime_am065_d3dda_0052:\n    mov r7, ip\n    uxtb r7, r7\n    cmp r7, #0\n    beq L_open_cfw_runtime_am065_d3dda_0060\n    movs.w r8, #0x40\n    b L_open_cfw_runtime_am065_d3dda_0064\nL_open_cfw_runtime_am065_d3dda_0060:\n    mov.w r8, #0x200\nL_open_cfw_runtime_am065_d3dda_0064:\n    movs r7, r2\n    adds r2, r7, r0\n    cmp r8, r2\n    bhs L_open_cfw_runtime_am065_d3dda_00a0\n    movs r0, #5\n    b L_open_cfw_runtime_am065_d3dda_015e\nL_open_cfw_runtime_am065_d3dda_0070:\n    movs.w r8, #0x40\n    b L_open_cfw_runtime_am065_d3dda_0064\nL_open_cfw_runtime_am065_d3dda_0076:\n    mov.w r8, #0x200\n    b L_open_cfw_runtime_am065_d3dda_0064\nL_open_cfw_runtime_am065_d3dda_007c:\n    movs r7, r1\n    uxtb r7, r7\n    cmp r7, #0\n    beq L_open_cfw_runtime_am065_d3dda_008a\n    mov.w r8, #0x2c0\n    b L_open_cfw_runtime_am065_d3dda_008e\nL_open_cfw_runtime_am065_d3dda_008a:\n    mov.w r8, #0x600\nL_open_cfw_runtime_am065_d3dda_008e:\n    b L_open_cfw_runtime_am065_d3dda_0064\nL_open_cfw_runtime_am065_d3dda_0090:\n    mov.w r8, #0x2c0\n    b L_open_cfw_runtime_am065_d3dda_0064\nL_open_cfw_runtime_am065_d3dda_0096:\n    mov.w r8, #0x600\n    b L_open_cfw_runtime_am065_d3dda_0064\nL_open_cfw_runtime_am065_d3dda_009c:\n    movs r0, #6\n    b L_open_cfw_runtime_am065_d3dda_015e\nL_open_cfw_runtime_am065_d3dda_00a0:\n    uxtb r6, r6\n    cmp r6, #0\n    beq L_open_cfw_runtime_am065_d3dda_00b8\n    cmp r6, #2\n    beq L_open_cfw_runtime_am065_d3dda_010e\n    blo L_open_cfw_runtime_am065_d3dda_00e6\n    cmp r6, #4\n    beq L_open_cfw_runtime_am065_d3dda_013a\n    blo L_open_cfw_runtime_am065_d3dda_0124\n    cmp r6, #5\n    beq L_open_cfw_runtime_am065_d3dda_0144\n    b L_open_cfw_runtime_am065_d3dda_014c\nL_open_cfw_runtime_am065_d3dda_00b8:\n    uxtb.w ip, ip\n    cmp.w ip, #0\n    beq L_open_cfw_runtime_am065_d3dda_00d8\n    uxtb.w lr, lr\n    cmp.w lr, #0\n    bne L_open_cfw_runtime_am065_d3dda_00d0\n    movs r0, #9\n    b L_open_cfw_runtime_am065_d3dda_015e\nL_open_cfw_runtime_am065_d3dda_00d0:\n    ldr r3, [pc, #0xc0]\n    adds.w r3, r3, r0, lsl #2\n    b L_open_cfw_runtime_am065_d3dda_00e4\nL_open_cfw_runtime_am065_d3dda_00d8:\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am065_d3dcc\n    bl .\n    movs r3, r0\n    lsls r3, r3, #2\n    adds.w r3, r3, #0x42000000\nL_open_cfw_runtime_am065_d3dda_00e4:\n    b L_open_cfw_runtime_am065_d3dda_014e\nL_open_cfw_runtime_am065_d3dda_00e6:\n    uxtb r1, r1\n    cmp r1, #0\n    beq L_open_cfw_runtime_am065_d3dda_0102\n    uxtb.w lr, lr\n    cmp.w lr, #0\n    bne L_open_cfw_runtime_am065_d3dda_00fa\n    movs r0, #9\n    b L_open_cfw_runtime_am065_d3dda_015e\nL_open_cfw_runtime_am065_d3dda_00fa:\n    ldr r3, [pc, #0x98]\n    adds.w r3, r3, r0, lsl #2\n    b L_open_cfw_runtime_am065_d3dda_010c\nL_open_cfw_runtime_am065_d3dda_0102:\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am065_d3dce\n    bl .\n    ldr r3, [pc, #0x90]\n    adds.w r3, r3, r0, lsl #2\nL_open_cfw_runtime_am065_d3dda_010c:\n    b L_open_cfw_runtime_am065_d3dda_014e\nL_open_cfw_runtime_am065_d3dda_010e:\n    uxtb.w lr, lr\n    cmp.w lr, #0\n    bne L_open_cfw_runtime_am065_d3dda_011c\n    movs r0, #9\n    b L_open_cfw_runtime_am065_d3dda_015e\nL_open_cfw_runtime_am065_d3dda_011c:\n    ldr r3, [pc, #0x74]\n    adds.w r3, r3, r0, lsl #2\n    b L_open_cfw_runtime_am065_d3dda_014e\nL_open_cfw_runtime_am065_d3dda_0124:\n    uxtb.w lr, lr\n    cmp.w lr, #0\n    bne L_open_cfw_runtime_am065_d3dda_0132\n    movs r0, #9\n    b L_open_cfw_runtime_am065_d3dda_015e\nL_open_cfw_runtime_am065_d3dda_0132:\n    ldr r3, [pc, #0x60]\n    adds.w r3, r3, r0, lsl #2\n    b L_open_cfw_runtime_am065_d3dda_014e\nL_open_cfw_runtime_am065_d3dda_013a:\n    lsls r0, r0, #2\n    adds.w r0, r0, #0x42000000\n    movs r3, r0\n    b L_open_cfw_runtime_am065_d3dda_014e\nL_open_cfw_runtime_am065_d3dda_0144:\n    ldr r3, [pc, #0x54]\n    adds.w r3, r3, r0, lsl #2\n    b L_open_cfw_runtime_am065_d3dda_014e\nL_open_cfw_runtime_am065_d3dda_014c:\n    movs r5, #6\nL_open_cfw_runtime_am065_d3dda_014e:\n    cmp r5, #0\n    bne L_open_cfw_runtime_am065_d3dda_015c\n    movs r2, r7\n    movs r1, r4\n    movs r0, r3\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am065_addr_0048086a\n    bl .\nL_open_cfw_runtime_am065_d3dda_015c:\n    movs r0, r5\nL_open_cfw_runtime_am065_d3dda_015e:\n    pop.w {r4, r5, r6, r7, r8, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM065_D3F3C_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am065_d3f3c(void)
{
    __asm__ volatile(
        "    push {r4, lr}\n    movs r4, r0\n    uxtb r4, r4\n    cmp r4, #1\n    beq L_open_cfw_runtime_am065_d3f3c_001e\n    movs r4, r0\n    uxtb r4, r4\n    cmp r4, #3\n    beq L_open_cfw_runtime_am065_d3f3c_001e\n    movs r4, r0\n    uxtb r4, r4\n    cmp r4, #5\n    beq L_open_cfw_runtime_am065_d3f3c_001e\n    movs r0, #6\n    b L_open_cfw_runtime_am065_d3f3c_0024\nL_open_cfw_runtime_am065_d3f3c_001e:\n    uxtb r0, r0\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am065_d3dda\n    bl .\nL_open_cfw_runtime_am065_d3f3c_0024:\n    pop {r4, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM065_D3F78_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am065_d3f78(void)
{
    __asm__ volatile(
        "    push {r2, r3, r4, lr}\n    movs r0, #0\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am065_addr_00473940\n    bl .\n    str r0, [sp]\n    ldr r1, [pc, #0x104]\n    ldrb r0, [r1]\n    cmp r0, #0\n    beq L_open_cfw_runtime_am065_d3f78_0018\n    ldrb r0, [r1]\n    subs r0, r0, #1\n    strb r0, [r1]\nL_open_cfw_runtime_am065_d3f78_0018:\n    ldrb r0, [r1]\n    cmp r0, #0\n    beq L_open_cfw_runtime_am065_d3f78_0022\n    movs r0, #3\n    b L_open_cfw_runtime_am065_d3f78_0034\nL_open_cfw_runtime_am065_d3f78_0022:\n    ldr r0, [pc, #0xf0]\n    ldr r1, [r0]\n    lsrs r1, r1, #1\n    lsls r1, r1, #1\n    str r1, [r0]\n    ldr r1, [r0]\n    bics r1, r1, #0xe\n    str r1, [r0]\nL_open_cfw_runtime_am065_d3f78_0034:\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am065_d403e\n    bl .\n    movs r0, #0\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am065_d3fc2\n    bl .\n    movs r4, r0\n    ldr r0, [sp]\n    msr primask, r0\n    movs r0, r4\n    pop {r1, r2, r4, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM065_D3FC2_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am065_d3fc2(void)
{
    __asm__ volatile(
        "    push {r1, r2, r3, r4, r5, lr}\n    movs r5, r0\n    movs r4, #0\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am065_addr_00473940\n    bl .\n    str r0, [sp, #4]\n    uxtb r5, r5\n    cmp r5, #0\n    beq L_open_cfw_runtime_am065_d3fc2_0048\n    ldr r0, [pc, #0xb8]\n    ldrb r1, [r0]\n    adds r1, r1, #1\n    strb r1, [r0]\n    ldr r5, [pc, #0xb4]\n    ldrb r0, [r5]\n    cmp r0, #0\n    bne L_open_cfw_runtime_am065_d3fc2_0072\n    movs r0, #1\n    strb r0, [r5]\n    mov r1, sp\n    movs r0, #0x1c\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am065_addr_0047f90c\n    bl .\n    ldrb.w r0, [sp]\n    cmp r0, #0\n    beq L_open_cfw_runtime_am065_d3fc2_0040\n    ldrb r0, [r5]\n    orrs r0, r0, #2\n    strb r0, [r5]\n    b L_open_cfw_runtime_am065_d3fc2_0072\nL_open_cfw_runtime_am065_d3fc2_0040:\n    movs r0, #0x1c\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am065_addr_0047f5b8\n    bl .\n    b L_open_cfw_runtime_am065_d3fc2_0072\nL_open_cfw_runtime_am065_d3fc2_0048:\n    ldr r1, [pc, #0x84]\n    ldrb r0, [r1]\n    cmp r0, #0\n    beq L_open_cfw_runtime_am065_d3fc2_0056\n    ldrb r0, [r1]\n    subs r0, r0, #1\n    strb r0, [r1]\nL_open_cfw_runtime_am065_d3fc2_0056:\n    ldrb r0, [r1]\n    cmp r0, #0\n    beq L_open_cfw_runtime_am065_d3fc2_0060\n    movs r4, #3\n    b L_open_cfw_runtime_am065_d3fc2_0072\nL_open_cfw_runtime_am065_d3fc2_0060:\n    ldr r5, [pc, #0x70]\n    ldrb r0, [r5]\n    cmp r0, #1\n    bne L_open_cfw_runtime_am065_d3fc2_006e\n    movs r0, #0x1c\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am065_addr_0047f7ae\n    bl .\nL_open_cfw_runtime_am065_d3fc2_006e:\n    movs r0, #0\n    strb r0, [r5]\nL_open_cfw_runtime_am065_d3fc2_0072:\n    ldr r0, [sp, #4]\n    msr primask, r0\n    movs r0, r4\n    pop {r1, r2, r3, r4, r5, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM065_D403E_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am065_d403e(void)
{
    __asm__ volatile(
        "    push {r2, r3, r4, lr}\n    movs r0, #0\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am065_addr_00473940\n    bl .\n    str r0, [sp]\n    ldr r1, [pc, #0x4c]\n    ldrb r0, [r1]\n    cmp r0, #0\n    beq L_open_cfw_runtime_am065_d403e_0018\n    ldrb r0, [r1]\n    subs r0, r0, #1\n    strb r0, [r1]\nL_open_cfw_runtime_am065_d403e_0018:\n    ldrb r0, [r1]\n    cmp r0, #0\n    beq L_open_cfw_runtime_am065_d403e_0022\n    movs r4, #3\n    b L_open_cfw_runtime_am065_d403e_003c\nL_open_cfw_runtime_am065_d403e_0022:\n    ldr r0, [pc, #0x38]\n    ldr r1, [r0]\n    bics r1, r1, #0x1000000\n    str r1, [r0]\n    movs r3, #0\n    movs.w r2, #0x1000000\n    ldr r1, [pc, #0x28]\n    movs r0, #0xa\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am065_addr_004807fc\n    bl .\n    movs r4, r0\nL_open_cfw_runtime_am065_d403e_003c:\n    ldr r0, [sp]\n    msr primask, r0\n    movs r0, r4\n    pop {r1, r2, r4, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM065_D40A0_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am065_d40a0(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    cbnz r0, L_open_cfw_runtime_am065_d40a0_0006\n    adr r0, #0x18\nL_open_cfw_runtime_am065_d40a0_0006:\n    ldr r1, [pc, #0x14]\n    ldr r3, [r1]\n    cbz r3, L_open_cfw_runtime_am065_d40a0_0014\n    movs r2, #0x22\n    movs r1, #0\n    blx r3\n    b L_open_cfw_runtime_am065_d40a0_0018\nL_open_cfw_runtime_am065_d40a0_0014:\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am065_addr_00541b74\n    bl .\nL_open_cfw_runtime_am065_d40a0_0018:\n    movs r0, #0x22\n    pop {r1, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM065_D40E0_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am065_d40e0(void)
{
    __asm__ volatile(
        "    uxtb r1, r1\nL_open_cfw_runtime_am065_d40e0_0002:\n    lsls r3, r0, #0x1e\n    beq L_open_cfw_runtime_am065_d40e0_0014\n    subs r2, r2, #1\n    blo L_open_cfw_runtime_am065_d40e0_0050\n    ldrb r3, [r0], #1\n    cmp r1, r3\n    bne L_open_cfw_runtime_am065_d40e0_0002\n    b L_open_cfw_runtime_am065_d40e0_0054\nL_open_cfw_runtime_am065_d40e0_0014:\n    subs r2, #8\n    blo L_open_cfw_runtime_am065_d40e0_0040\n    add.w r2, r2, #4\n    orr.w r1, r1, r1, lsl #8\n    orr.w r1, r1, r1, lsl #16\nL_open_cfw_runtime_am065_d40e0_0024:\n    ldr r3, [r0], #4\n    subs r2, r2, #4\n    itttt hs\n    eorhs r3, r1\n    subhs.w ip, r3, #0x1010101\n    bichs.w ip, ip, r3\n    tsths.w ip, #-0x7f7f7f80\n    beq L_open_cfw_runtime_am065_d40e0_0024\n    uxtb r1, r1\n    subs r0, r0, #4\nL_open_cfw_runtime_am065_d40e0_0040:\n    adds r2, #8\nL_open_cfw_runtime_am065_d40e0_0042:\n    ldrb r3, [r0], #1\n    subs r2, r2, #1\n    it hs\n    teqhs.w r1, r3\n    bhi L_open_cfw_runtime_am065_d40e0_0042\nL_open_cfw_runtime_am065_d40e0_0050:\n    it ne\n    movne r0, #1\nL_open_cfw_runtime_am065_d40e0_0054:\n    subs r0, r0, #1\n    bx lr\n"
    );
}
#endif

#if defined(OPEN_CFW_AM065_D4138_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am065_d4138(void)
{
    __asm__ volatile(
        "    push {r4, lr}\n    mov r2, r0\n    vmov r0, r1, d0\n    mov r4, r2\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am065_d415c\n    bl .\n    vmov d0, r0, r1\n    str r2, [r4]\n    pop {r4, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM065_D4150_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am065_d4150(void)
{
    __asm__ volatile(
        "    push {r4, lr}\n    mov r4, r2\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am065_d415c\n    bl .\n    str r2, [r4]\n    pop {r4, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM065_D415C_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am065_d415c(void)
{
    __asm__ volatile(
        "    ubfx r3, r1, #0x14, #0xb\n    cbz r3, L_open_cfw_runtime_am065_d415c_0018\n    lsls r2, r1, #1\n    cmn.w r2, #0x200000\n    bhs L_open_cfw_runtime_am065_d415c_0060\n    subw r2, r3, #0x3fe\n    sub.w r1, r1, r2, lsl #20\n    bx lr\nL_open_cfw_runtime_am065_d415c_0018:\n    orrs.w ip, r0, r1, lsl #1\n    beq L_open_cfw_runtime_am065_d415c_0060\n    and ip, r1, #0x80000000\n    bics.w r1, r1, ip\n    clz r2, r1\n    itt eq\n    clzeq r3, r0\n    addeq r2, r2, r3\n    subs r2, #0xb\n    subs.w r3, r2, #0x20\n    ite hs\n    lslhs.w r1, r0, r3\n    lsllo r1, r2\n    orr.w r1, r1, ip\n    ittt lo\n    rsblo.w ip, r2, #0x20\n    lsrlo.w r3, r0, ip\n    orrlo r1, r3\n    lsls r0, r2\n    rsbs r2, r2, #0\n    movw r3, #0x3fd\n    subs r2, r2, r3\n    add.w r1, r1, r3, lsl #20\n    bx lr\nL_open_cfw_runtime_am065_d415c_0060:\n    movs r2, #0\n    bx lr\n"
    );
}
#endif

#if defined(OPEN_CFW_AM065_D41C0_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am065_d41c0(void)
{
    __asm__ volatile(
        "    orr.w ip, r1, r3\n    orrs.w ip, r0, ip, lsl #1\n    orrs.w ip, r2, ip\n    mov.w ip, #0x200000\n    blo L_open_cfw_runtime_am065_d41c0_0026\n    beq L_open_cfw_runtime_am065_d41c0_0024\n    cmn.w ip, r1, lsl #1\n    itt ls\n    cmnls.w ip, r3, lsl #1\n    cmpls r3, r1\n    it eq\n    cmpeq r2, r0\nL_open_cfw_runtime_am065_d41c0_0024:\n    bx lr\nL_open_cfw_runtime_am065_d41c0_0026:\n    cmn.w ip, r3, lsl #1\n    bhi L_open_cfw_runtime_am065_d41c0_0024\n    cmp r1, r3\n    it eq\n    cmpeq r0, r2\n    bx lr\n"
    );
}
#endif

#if defined(OPEN_CFW_AM065_D41F4_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am065_d41f4(void)
{
    __asm__ volatile(
        "    push {lr}\n    vmov d0, r0, r1\n    mov r0, r2\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am065_d4208\n    bl .\n    vmov r0, r1, d0\n    pop {pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM065_D4208_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am065_d4208(void)
{
    __asm__ volatile(
        "    movs r2, r0\n    vmov.32 r1, d0[1]\n    movw ip, #0x7ff\n    bmi L_open_cfw_runtime_am065_d4208_007c\n    ands.w r3, ip, r1, lsr #20\n    beq L_open_cfw_runtime_am065_d4208_003a\n    cmp r3, ip\n    beq L_open_cfw_runtime_am065_d4208_00ee\n    adds r3, r3, r2\nL_open_cfw_runtime_am065_d4208_0018:\n    cmp r3, ip\n    bhs L_open_cfw_runtime_am065_d4208_0026\n    add.w r1, r1, r2, lsl #20\n    vmov.32 d0[1], r1\n    bx lr\nL_open_cfw_runtime_am065_d4208_0026:\n    and r1, r1, #0x80000000\n    orr.w r1, r1, ip, lsl #20\n    movs r0, #0\n    vmov d0, r0, r1\nL_open_cfw_runtime_am065_d4208_0034:\n    b.w #0x439cb2\n    bx lr\nL_open_cfw_runtime_am065_d4208_003a:\n    vmov.32 r0, d0[0]\n    orrs.w r0, r0, r1, lsl #1\n    beq L_open_cfw_runtime_am065_d4208_00ee\n    cmp.w r2, #0x3fc\n    bhs L_open_cfw_runtime_am065_d4208_005c\n    add.w r1, r2, ip, lsr #1\n    lsls r1, r1, #0x14\n    movs r0, #0\n    vmov d1, r0, r1\n    vmul.f64 d0, d0, d1\n    bx lr\nL_open_cfw_runtime_am065_d4208_005c:\n    mov.w r1, #0x7f000000\n    movs r3, #0\n    vmov d1, r3, r1\n    vmul.f64 d0, d0, d1\n    subs.w r2, r2, #0x3f8\n    vmov.32 r1, d0[1]\n    lsl.w r3, r1, #1\n    adc.w r3, r2, r3, lsr #21\n    b L_open_cfw_runtime_am065_d4208_0018\nL_open_cfw_runtime_am065_d4208_007c:\n    rsbs r2, r2, #0\n    ands.w r3, ip, r1, lsr #20\n    beq L_open_cfw_runtime_am065_d4208_00b2\n    cmp r3, ip\n    beq L_open_cfw_runtime_am065_d4208_00ee\n    cmp r2, r3\n    bhs L_open_cfw_runtime_am065_d4208_0096\n    sub.w r1, r1, r2, lsl #20\n    vmov.32 d0[1], r1\n    bx lr\nL_open_cfw_runtime_am065_d4208_0096:\n    subs r3, r3, #1\n    subs r2, r2, r3\n    sub.w r1, r1, r3, lsl #20\n    vmov.32 d0[1], r1\n    cmp r2, #0x37\n    blo L_open_cfw_runtime_am065_d4208_00c0\nL_open_cfw_runtime_am065_d4208_00a6:\n    movs r0, #0\n    and r1, r1, #0x80000000\n    vmov d0, r0, r1\n    b L_open_cfw_runtime_am065_d4208_0034\nL_open_cfw_runtime_am065_d4208_00b2:\n    vmov.32 r0, d0[0]\n    orrs.w r0, r0, r1, lsl #1\n    beq L_open_cfw_runtime_am065_d4208_00ee\n    cmp r2, #0x37\n    bhs L_open_cfw_runtime_am065_d4208_00a6\nL_open_cfw_runtime_am065_d4208_00c0:\n    rsb r2, r2, ip, lsr #1\n    lsls r1, r2, #0x14\n    movs r0, #0\n    vmov d1, r0, r1\n    vmrs r0, fpscr\n    bic r1, r0, #0x1f\n    bic r1, r1, #0x1f00\n    vmsr fpscr, r1\n    vmul.f64 d0, d0, d1\n    vmrs r1, fpscr\n    vmsr fpscr, r0\n    tst.w r1, #8\n    bne L_open_cfw_runtime_am065_d4208_0034\nL_open_cfw_runtime_am065_d4208_00ee:\n    bx lr\n"
    );
}
#endif

#if defined(OPEN_CFW_AM065_D42F8_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am065_d42f8(void)
{
    __asm__ volatile(
        "    vmov d0, r0, r1\n    vcvt.s32.f64 s0, d0\n    vmov r0, s0\n    bx lr\n"
    );
}
#endif

#if defined(OPEN_CFW_AM065_D4306_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am065_d4306(void)
{
    __asm__ volatile(
        "    vmov s0, r0\n    vcvt.f64.s32 d0, s0\n    vmov r0, r1, d0\n    bx lr\n"
    );
}
#endif

#if defined(OPEN_CFW_AM065_D4314_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am065_d4314(void)
{
    __asm__ volatile(
        "    vmov d0, r0, r1\n    vmov d1, r2, r3\n    vsub.f64 d0, d0, d1\n    vmov r0, r1, d0\n    bx lr\n"
    );
}
#endif

#if defined(OPEN_CFW_AM065_D4326_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am065_d4326(void)
{
    __asm__ volatile(
        "    vmov d0, r0, r1\n    vmov d1, r2, r3\n    vdiv.f64 d0, d0, d1\n    vmov r0, r1, d0\n    bx lr\n"
    );
}
#endif

#if defined(OPEN_CFW_AM065_D4338_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am065_d4338(void)
{
    __asm__ volatile(
        "    vmov d0, r0, r1\n    vcvt.u32.f64 s0, d0\n    vmov r0, s0\n    bx lr\n"
    );
}
#endif

#if defined(OPEN_CFW_AM065_D4346_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am065_d4346(void)
{
    __asm__ volatile(
        "    vmov s0, r0\n    vcvt.f64.u32 d0, s0\n    vmov r0, r1, d0\n    bx lr\n"
    );
}
#endif
