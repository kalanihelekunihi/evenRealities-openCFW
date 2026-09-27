/*
 * SPDX-License-Identifier: MIT
 *
 * Source-owned exact helpers from bounded AM-008 retained rows.
 */

#if defined(OPEN_CFW_AM008_420A6_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am008_420a6(void)
{
    __asm__ volatile(
        "    ldr r0, [pc, #0x16c]\n    ldr r1, [r0]\n    orrs r1, r1, #0xf00000\n    str r1, [r0]\n    ldr r0, [pc, #0x164]\n    ldr r1, [r0]\n    orrs r1, r1, #0xc0000000\n    str r1, [r0]\n    bx lr\n"
    );
}
#endif

#if defined(OPEN_CFW_AM008_42114_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am008_42114(void)
{
    __asm__ volatile(
        "    push {r4, lr}\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am008_addr_005fa0a4\n    bl .\n    movs r4, r0\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am008_addr_0045504c\n    bl .\n    cmp r0, #0\n    beq L_open_cfw_runtime_am008_42114_0018\n    movs.w r0, #0x10000000\n    ldr r1, [pc, #0xf0]\n    str r0, [r1]\nL_open_cfw_runtime_am008_42114_0018:\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am008_addr_005fa0ba\n    bl .\n    pop {r4, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM008_4215A_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am008_4215a(void)
{
    __asm__ volatile(
        "    push {r4}\n    subs r0, r0, #4\n    movs.w r4, #0x1000000\n    str r4, [r0]\n    subs r0, r0, #4\n    str r2, [r0]\n    subs r0, r0, #4\n    ldr r2, [pc, #0xb4]\n    str r2, [r0]\n    subs r0, r0, #4\n    movs.w r2, #0x12121212\n    str r2, [r0]\n    subs r0, r0, #4\n    movs.w r2, #0x3030303\n    str r2, [r0]\n    subs r0, r0, #4\n    movs.w r2, #0x2020202\n    str r2, [r0]\n    subs r0, r0, #4\n    movs.w r2, #0x1010101\n    str r2, [r0]\n    subs r0, r0, #4\n    str r3, [r0]\n    subs r0, r0, #4\n    movs.w r2, #0x11111111\n    str r2, [r0]\n    subs r0, r0, #4\n    movs.w r2, #0x10101010\n    str r2, [r0]\n    subs r0, r0, #4\n    movs.w r2, #0x9090909\n    str r2, [r0]\n    subs r0, r0, #4\n    movs.w r2, #0x8080808\n    str r2, [r0]\n    subs r0, r0, #4\n    movs.w r2, #0x7070707\n    str r2, [r0]\n    subs r0, r0, #4\n    movs.w r2, #0x6060606\n    str r2, [r0]\n    subs r0, r0, #4\n    movs.w r2, #0x5050505\n    str r2, [r0]\n    subs r0, r0, #4\n    movs.w r2, #0x4040404\n    str r2, [r0]\n    subs r0, r0, #4\n    mvns r2, #2\n    str r2, [r0]\n    subs r0, r0, #4\n    str r1, [r0]\n    pop {r4}\n    bx lr\n"
    );
}
#endif

#if defined(OPEN_CFW_AM008_42228_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am008_42228(void)
{
    __asm__ volatile(
        "    mrs r0, ipsr\n    cmp r0, #0\n    bne L_open_cfw_runtime_am008_42228_000c\n    movs r0, #0\n    b L_open_cfw_runtime_am008_42228_000e\nL_open_cfw_runtime_am008_42228_000c:\n    movs r0, #1\nL_open_cfw_runtime_am008_42228_000e:\n    bx lr\n"
    );
}
#endif

#if defined(OPEN_CFW_AM008_42238_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am008_42238(void)
{
    __asm__ volatile(
        "    movs r1, r0\n    sxth r1, r1\n    cmp r1, #0\n    bmi L_open_cfw_runtime_am008_42238_001c\n    movs r2, #1\n    ands r1, r0, #0x1f\n    lsls r2, r1\n    ldr.w r1, [pc, #0xa7c]\n    sxth r0, r0\n    lsrs r0, r0, #5\n    str.w r2, [r1, r0, lsl #2]\nL_open_cfw_runtime_am008_42238_001c:\n    bx lr\n"
    );
}
#endif

#if defined(OPEN_CFW_AM008_42256_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am008_42256(void)
{
    __asm__ volatile(
        "    movs r2, r0\n    sxth r2, r2\n    cmp r2, #0\n    bmi L_open_cfw_runtime_am008_42256_0014\n    lsls r1, r1, #4\n    ldr.w r2, [pc, #0xa68]\n    sxth r0, r0\n    strb r1, [r2, r0]\n    b L_open_cfw_runtime_am008_42256_0026\nL_open_cfw_runtime_am008_42256_0014:\n    lsls r1, r1, #4\n    ldr.w r2, [pc, #0xa60]\n    sxth r0, r0\n    ands r0, r0, #0xf\n    add r0, r2\n    strb r1, [r0, #-0x4]\nL_open_cfw_runtime_am008_42256_0026:\n    bx lr\n"
    );
}
#endif

#if defined(OPEN_CFW_AM008_4227E_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am008_4227e(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am008_addr_00458c48\n    bl .\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am008_addr_00458e48\n    bl .\n    pop {r0, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM008_4347A_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am008_4347a(void)
{
    __asm__ volatile(
        "    ldr.w r0, [pc, #0x354]\n    bx lr\n"
    );
}
#endif

#if defined(OPEN_CFW_AM008_43484_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am008_43484(void)
{
    __asm__ volatile(
        "    ldr.w r0, [pc, #0x348]\n    ldrb r0, [r0]\n    cmp r0, #1\n    bne L_open_cfw_runtime_am008_43484_000e\n    movs r0, #1\n    b L_open_cfw_runtime_am008_43484_0010\nL_open_cfw_runtime_am008_43484_000e:\n    movs r0, #0\nL_open_cfw_runtime_am008_43484_0010:\n    bx lr\n"
    );
}
#endif

#if defined(OPEN_CFW_AM008_4349C_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am008_4349c(void)
{
    __asm__ volatile(
        "    ldr r0, [pc, #0x2c8]\n    ldr r0, [r0]\n    cmp r0, #0\n    beq L_open_cfw_runtime_am008_4349c_000c\n    movs r0, #1\n    b L_open_cfw_runtime_am008_4349c_000e\nL_open_cfw_runtime_am008_4349c_000c:\n    movs r0, #0\nL_open_cfw_runtime_am008_4349c_000e:\n    bx lr\n"
    );
}
#endif

#if defined(OPEN_CFW_AM008_434B4_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am008_434b4(void)
{
    __asm__ volatile(
        "    ldr r0, [pc, #0x31c]\n    ldr r0, [r0]\n    cmp r0, #0\n    beq L_open_cfw_runtime_am008_434b4_0014\n    ldr r0, [pc, #0x2ac]\n    ldr r0, [r0]\n    cmp r0, #1\n    bne L_open_cfw_runtime_am008_434b4_0014\n    movs r0, #1\n    b L_open_cfw_runtime_am008_434b4_0016\nL_open_cfw_runtime_am008_434b4_0014:\n    movs r0, #0\nL_open_cfw_runtime_am008_434b4_0016:\n    bx lr\n"
    );
}
#endif

#if defined(OPEN_CFW_AM008_434D0_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am008_434d0(void)
{
    __asm__ volatile(
        "    ldr r1, [pc, #0x300]\n    ldr r1, [r1]\n    cmp r0, r1\n    beq L_open_cfw_runtime_am008_434d0_0010\n    ldr r1, [pc, #0x28c]\n    ldr r1, [r1]\n    cmp r0, r1\n    bne L_open_cfw_runtime_am008_434d0_0014\nL_open_cfw_runtime_am008_434d0_0010:\n    movs r0, #1\n    b L_open_cfw_runtime_am008_434d0_0016\nL_open_cfw_runtime_am008_434d0_0014:\n    movs r0, #0\nL_open_cfw_runtime_am008_434d0_0016:\n    bx lr\n"
    );
}
#endif

#if defined(OPEN_CFW_AM008_43504_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am008_43504(void)
{
    __asm__ volatile(
        "    push {r3, r4, r5, lr}\n    sub sp, #0x10\n    movs r4, r0\n    movs r5, r1\n    cmp r4, #0\n    beq L_open_cfw_runtime_am008_43504_0010\n    cmp r5, #0\n    bne L_open_cfw_runtime_am008_43504_0016\nL_open_cfw_runtime_am008_43504_0010:\n    movs.w r0, #-1\n    b L_open_cfw_runtime_am008_43504_0186\nL_open_cfw_runtime_am008_43504_0016:\n    ldr r0, [pc, #0x2b4]\n    ldrb r0, [r0]\n    cmp r0, #1\n    bne.w #0x443636\n    ldr r0, [pc, #0x244]\n    ldr r1, [r0]\n    cmp r1, #1\n    bne L_open_cfw_runtime_am008_43504_0080\n    ldr r0, [pc, #0x2a4]\n    ldr r0, [r0]\n    str r0, [r4]\n    ldr r0, [pc, #0x234]\n    ldr r0, [r0]\n    str r0, [r5]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am008_addr_0043d0ce\n    bl .\n    lsls r0, r0, #0x1e\n    bpl L_open_cfw_runtime_am008_43504_005a\n    ldr r0, [r5]\n    str r0, [sp, #0xc]\n    ldr r0, [r4]\n    str r0, [sp, #8]\n    ldr r0, [pc, #0x28c]\n    str r0, [sp, #4]\n    mov.w r0, #0x244\n    str r0, [sp]\n    ldr r3, [pc, #0x288]\n    ldr r2, [pc, #0x204]\n    ldr r1, [pc, #0x208]\n    movs r0, #4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am008_addr_0043d574\n    bl .\nL_open_cfw_runtime_am008_43504_005a:\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am008_addr_0043d0ce\n    bl .\n    lsls r0, r0, #0x1f\n    bmi L_open_cfw_runtime_am008_43504_006a\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am008_addr_0043d0ce\n    bl .\n    lsls r0, r0, #0x1d\n    bpl L_open_cfw_runtime_am008_43504_007e\nL_open_cfw_runtime_am008_43504_006a:\n    ldr.w r2, [pc, #0xc70]\n    ldr r0, [r5]\n    str r0, [sp]\n    ldr r3, [r4]\n    movs r1, r2\n    movs.w r0, #0x10800000\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am008_addr_0043ce9e\n    bl .\nL_open_cfw_runtime_am008_43504_007e:\n    b L_open_cfw_runtime_am008_43504_012e\nL_open_cfw_runtime_am008_43504_0080:\n    ldr r0, [r0]\n    cmp r0, #2\n    bne L_open_cfw_runtime_am008_43504_00dc\n    movs r0, #0\n    str r0, [r4]\n    ldr r0, [pc, #0x244]\n    ldr r0, [r0]\n    str r0, [r5]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am008_addr_0043d0ce\n    bl .\n    lsls r0, r0, #0x1e\n    bpl L_open_cfw_runtime_am008_43504_00b6\n    ldr r0, [r5]\n    str r0, [sp, #0xc]\n    ldr r0, [r4]\n    str r0, [sp, #8]\n    ldr r0, [pc, #0x230]\n    str r0, [sp, #4]\n    movw r0, #0x249\n    str r0, [sp]\n    ldr r3, [pc, #0x22c]\n    ldr r2, [pc, #0x1a8]\n    ldr r1, [pc, #0x1ac]\n    movs r0, #4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am008_addr_0043d574\n    bl .\nL_open_cfw_runtime_am008_43504_00b6:\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am008_addr_0043d0ce\n    bl .\n    lsls r0, r0, #0x1f\n    bmi L_open_cfw_runtime_am008_43504_00c6\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am008_addr_0043d0ce\n    bl .\n    lsls r0, r0, #0x1d\n    bpl L_open_cfw_runtime_am008_43504_00da\nL_open_cfw_runtime_am008_43504_00c6:\n    ldr.w r1, [pc, #0xc14]\n    ldr r0, [r5]\n    str r0, [sp]\n    ldr r3, [r4]\n    movs r2, r1\n    movs.w r0, #0x10800000\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am008_addr_0043ce9e\n    bl .\nL_open_cfw_runtime_am008_43504_00da:\n    b L_open_cfw_runtime_am008_43504_012e\nL_open_cfw_runtime_am008_43504_00dc:\n    movs r0, #0\n    str r0, [r4]\n    movs r0, #0\n    str r0, [r5]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am008_addr_0043d0ce\n    bl .\n    lsls r0, r0, #0x1e\n    bpl L_open_cfw_runtime_am008_43504_010a\n    ldr r0, [r5]\n    str r0, [sp, #0xc]\n    ldr r0, [r4]\n    str r0, [sp, #8]\n    ldr r0, [pc, #0x1dc]\n    str r0, [sp, #4]\n    movw r0, #0x24d\n    str r0, [sp]\n    ldr r3, [pc, #0x1d8]\n    ldr r2, [pc, #0x154]\n    ldr r1, [pc, #0x158]\n    movs r0, #4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am008_addr_0043d574\n    bl .\nL_open_cfw_runtime_am008_43504_010a:\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am008_addr_0043d0ce\n    bl .\n    lsls r0, r0, #0x1f\n    bmi L_open_cfw_runtime_am008_43504_011a\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am008_addr_0043d0ce\n    bl .\n    lsls r0, r0, #0x1d\n    bpl L_open_cfw_runtime_am008_43504_012e\nL_open_cfw_runtime_am008_43504_011a:\n    ldr.w r1, [pc, #0xbc0]\n    ldr r0, [r5]\n    str r0, [sp]\n    ldr r3, [r4]\n    movs r2, r1\n    movs.w r0, #0x10800000\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am008_addr_0043ce9e\n    bl .\nL_open_cfw_runtime_am008_43504_012e:\n    movs r0, #0\n    b L_open_cfw_runtime_am008_43504_0186\n    movs r0, #0\n    str r0, [r4]\n    movs r0, #0\n    str r0, [r5]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am008_addr_0043d0ce\n    bl .\n    lsls r0, r0, #0x1e\n    bpl L_open_cfw_runtime_am008_43504_0160\n    ldr r0, [r5]\n    str r0, [sp, #0xc]\n    ldr r0, [r4]\n    str r0, [sp, #8]\n    ldr r0, [pc, #0x188]\n    str r0, [sp, #4]\n    movw r0, #0x253\n    str r0, [sp]\n    ldr r3, [pc, #0x180]\n    ldr r2, [pc, #0x100]\n    ldr r1, [pc, #0x100]\n    movs r0, #4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am008_addr_0043d574\n    bl .\nL_open_cfw_runtime_am008_43504_0160:\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am008_addr_0043d0ce\n    bl .\n    lsls r0, r0, #0x1f\n    bmi L_open_cfw_runtime_am008_43504_0170\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am008_addr_0043d0ce\n    bl .\n    lsls r0, r0, #0x1d\n    bpl L_open_cfw_runtime_am008_43504_0184\nL_open_cfw_runtime_am008_43504_0170:\n    ldr.w r1, [pc, #0xb68]\n    ldr r0, [r5]\n    str r0, [sp]\n    ldr r3, [r4]\n    movs r2, r1\n    movs.w r0, #0x10800000\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am008_addr_0043ce9e\n    bl .\nL_open_cfw_runtime_am008_43504_0184:\n    movs r0, #0\nL_open_cfw_runtime_am008_43504_0186:\n    add sp, #0x14\n    pop {r4, r5, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM008_4368E_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am008_4368e(void)
{
    __asm__ volatile(
        "    push {r4, lr}\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am008_addr_00460106\n    bl .\n    movs r4, r0\n    cmp r4, #0\n    bne L_open_cfw_runtime_am008_4368e_0010\n    movs r0, #0\n    b L_open_cfw_runtime_am008_4368e_0098\nL_open_cfw_runtime_am008_4368e_0010:\n    adr r1, #0x9c\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am008_addr_0046cacc\n    bl .\n    cmp r0, #0\n    bne L_open_cfw_runtime_am008_4368e_0020\n    movs r0, #1\n    b L_open_cfw_runtime_am008_4368e_0098\nL_open_cfw_runtime_am008_4368e_0020:\n    ldr.w r1, [pc, #0xb34]\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am008_addr_0046cacc\n    bl .\n    cmp r0, #0\n    bne L_open_cfw_runtime_am008_4368e_0032\n    movs r0, #0\n    b L_open_cfw_runtime_am008_4368e_0098\nL_open_cfw_runtime_am008_4368e_0032:\n    adr r1, #0x7c\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am008_addr_0046cacc\n    bl .\n    cmp r0, #0\n    bne L_open_cfw_runtime_am008_4368e_0042\n    movs r0, #2\n    b L_open_cfw_runtime_am008_4368e_0098\nL_open_cfw_runtime_am008_4368e_0042:\n    adr r1, #0x70\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am008_addr_0046cacc\n    bl .\n    cmp r0, #0\n    bne L_open_cfw_runtime_am008_4368e_0052\n    movs r0, #4\n    b L_open_cfw_runtime_am008_4368e_0098\nL_open_cfw_runtime_am008_4368e_0052:\n    adr r1, #0x64\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am008_addr_0046cacc\n    bl .\n    cmp r0, #0\n    bne L_open_cfw_runtime_am008_4368e_0062\n    movs r0, #3\n    b L_open_cfw_runtime_am008_4368e_0098\nL_open_cfw_runtime_am008_4368e_0062:\n    adr r1, #0x58\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am008_addr_0046cacc\n    bl .\n    cmp r0, #0\n    bne L_open_cfw_runtime_am008_4368e_0072\n    movs r0, #5\n    b L_open_cfw_runtime_am008_4368e_0098\nL_open_cfw_runtime_am008_4368e_0072:\n    ldr.w r1, [pc, #0xae4]\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am008_addr_0046cacc\n    bl .\n    cmp r0, #0\n    bne L_open_cfw_runtime_am008_4368e_0084\n    movs r0, #6\n    b L_open_cfw_runtime_am008_4368e_0098\nL_open_cfw_runtime_am008_4368e_0084:\n    ldr.w r1, [pc, #0xc8c]\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am008_addr_0046cacc\n    bl .\n    cmp r0, #0\n    bne L_open_cfw_runtime_am008_4368e_0096\n    movs r0, #7\n    b L_open_cfw_runtime_am008_4368e_0098\nL_open_cfw_runtime_am008_4368e_0096:\n    movs r0, #0\nL_open_cfw_runtime_am008_4368e_0098:\n    pop {r4, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM008_441EC_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am008_441ec(void)
{
    __asm__ volatile(
        "    push {r3, r4, r5, r6, r7, lr}\n    sub sp, #0x18\n    movs r5, r0\n    movs r6, r1\n    movs r4, r2\n    movs r1, #0xc\n    movs r2, #0\n    add r7, sp, #0xc\n    movs r0, r7\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am008_addr_0043c0e4\n    bl .\n    movw r0, #0x2801\n    cmp r4, r0\n    blo L_open_cfw_runtime_am008_441ec_006e\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am008_addr_0043d0ce\n    bl .\n    lsls r0, r0, #0x1e\n    bpl L_open_cfw_runtime_am008_441ec_0046\n    mov.w r0, #0x2800\n    str r0, [sp, #8]\n    ldr.w r0, [pc, #0x660]\n    str r0, [sp, #4]\n    movw r0, #0x36d\n    str r0, [sp]\n    ldr.w r3, [pc, #0x658]\n    ldr r2, [pc, #0x17c]\n    ldr r1, [pc, #0x180]\n    movs r0, #2\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am008_addr_0043d574\n    bl .\nL_open_cfw_runtime_am008_441ec_0046:\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am008_addr_0043d0ce\n    bl .\n    lsls r0, r0, #0x1f\n    bmi L_open_cfw_runtime_am008_441ec_0056\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am008_addr_0043d0ce\n    bl .\n    lsls r0, r0, #0x1d\n    bpl L_open_cfw_runtime_am008_441ec_0068\nL_open_cfw_runtime_am008_441ec_0056:\n    ldr.w r1, [pc, #0x640]\n    mov.w r3, #0x2800\n    movs r2, r1\n    movs.w r0, #0x8400000\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am008_addr_0043ce9e\n    bl .\nL_open_cfw_runtime_am008_441ec_0068:\n    movs.w r0, #-1\n    b L_open_cfw_runtime_am008_441ec_00cc\nL_open_cfw_runtime_am008_441ec_006e:\n    movs r1, #0xc\n    movs r2, #0\n    add r7, sp, #0xc\n    movs r0, r7\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am008_addr_0043c0e4\n    bl .\n    movs r0, #2\n    strb.w r0, [sp, #0xc]\n    str r5, [sp, #0x10]\n    ldr r5, [pc, #0x158]\n    movs.w r1, #-1\n    ldr r0, [r5]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am008_addr_004497b6\n    bl .\n    movs r2, r4\n    movs r1, r6\n    ldr r0, [pc, #0x228]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am008_addr_0046d8c4\n    bl .\n    ldr r0, [r5]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am008_addr_0044981c\n    bl .\n    str r4, [sp, #0x14]\n    mov.w r3, #0x3e8\n    movs r2, #0\n    add r1, sp, #0xc\n    ldr r0, [pc, #0x12c]\n    ldr r0, [r0]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am008_addr_00449abe\n    bl .\n    cmp r0, #0\n    beq L_open_cfw_runtime_am008_441ec_00ca\n    ldr.w r0, [pc, #0x5e4]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am008_addr_004733ee\n    bl .\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am008_addr_005fa0a4\n    bl .\n    movs r0, #0\n    movs.w r1, #-1\n    str r0, [r1]\nL_open_cfw_runtime_am008_441ec_00c8:\n    b L_open_cfw_runtime_am008_441ec_00c8\nL_open_cfw_runtime_am008_441ec_00ca:\n    movs r0, #0\nL_open_cfw_runtime_am008_441ec_00cc:\n    add sp, #0x1c\n    pop {r4, r5, r6, r7, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM008_442D0_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am008_442d0(void)
{
    __asm__ volatile(
        "    push {r3, r4, r5, r6, r7, lr}\n    sub sp, #0x18\n    movs r5, r0\n    movs r6, r1\n    movs r4, r2\n    movs r1, #0xc\n    movs r2, #0\n    add r7, sp, #0xc\n    movs r0, r7\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am008_addr_0043c0e4\n    bl .\n    movw r0, #0x2801\n    cmp r4, r0\n    blo L_open_cfw_runtime_am008_442d0_006e\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am008_addr_0043d0ce\n    bl .\n    lsls r0, r0, #0x1e\n    bpl L_open_cfw_runtime_am008_442d0_0046\n    mov.w r0, #0x2800\n    str r0, [sp, #8]\n    ldr.w r0, [pc, #0x57c]\n    str r0, [sp, #4]\n    movw r0, #0x38b\n    str r0, [sp]\n    ldr.w r3, [pc, #0x580]\n    ldr r2, [pc, #0x98]\n    ldr r1, [pc, #0x9c]\n    movs r0, #2\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am008_addr_0043d574\n    bl .\nL_open_cfw_runtime_am008_442d0_0046:\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am008_addr_0043d0ce\n    bl .\n    lsls r0, r0, #0x1f\n    bmi L_open_cfw_runtime_am008_442d0_0056\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am008_addr_0043d0ce\n    bl .\n    lsls r0, r0, #0x1d\n    bpl L_open_cfw_runtime_am008_442d0_0068\nL_open_cfw_runtime_am008_442d0_0056:\n    ldr.w r1, [pc, #0x55c]\n    mov.w r3, #0x2800\n    movs r2, r1\n    movs.w r0, #0x8400000\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am008_addr_0043ce9e\n    bl .\nL_open_cfw_runtime_am008_442d0_0068:\n    movs.w r0, #-1\n    b L_open_cfw_runtime_am008_442d0_00cc\nL_open_cfw_runtime_am008_442d0_006e:\n    movs r1, #0xc\n    movs r2, #0\n    add r7, sp, #0xc\n    movs r0, r7\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am008_addr_0043c0e4\n    bl .\n    movs r0, #3\n    strb.w r0, [sp, #0xc]\n    str r5, [sp, #0x10]\n    ldr r5, [pc, #0x74]\n    movs.w r1, #-1\n    ldr r0, [r5]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am008_addr_004497b6\n    bl .\n    movs r2, r4\n    movs r1, r6\n    ldr r0, [pc, #0x144]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am008_addr_0046d8c4\n    bl .\n    ldr r0, [r5]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am008_addr_0044981c\n    bl .\n    str r4, [sp, #0x14]\n    mov.w r3, #0x3e8\n    movs r2, #0\n    add r1, sp, #0xc\n    ldr r0, [pc, #0x48]\n    ldr r0, [r0]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am008_addr_00449abe\n    bl .\n    cmp r0, #0\n    beq L_open_cfw_runtime_am008_442d0_00ca\n    ldr.w r0, [pc, #0x508]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am008_addr_004733ee\n    bl .\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am008_addr_005fa0a4\n    bl .\n    movs r0, #0\n    movs.w r1, #-1\n    str r0, [r1]\nL_open_cfw_runtime_am008_442d0_00c8:\n    b L_open_cfw_runtime_am008_442d0_00c8\nL_open_cfw_runtime_am008_442d0_00ca:\n    movs r0, #0\nL_open_cfw_runtime_am008_442d0_00cc:\n    add sp, #0x1c\n    pop {r4, r5, r6, r7, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM008_443CC_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am008_443cc(void)
{
    __asm__ volatile(
        "    push {r3, r4, r5, r6, r7, lr}\n    sub sp, #0x18\n    movs r5, r0\n    movs r6, r1\n    movs r4, r2\n    movs r1, #0xc\n    movs r2, #0\n    add r7, sp, #0xc\n    movs r0, r7\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am008_addr_0043c0e4\n    bl .\n    movw r0, #0x2801\n    cmp r4, r0\n    blo L_open_cfw_runtime_am008_443cc_0072\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am008_addr_0043d0ce\n    bl .\n    lsls r0, r0, #0x1e\n    bpl L_open_cfw_runtime_am008_443cc_004a\n    mov.w r0, #0x2800\n    str r0, [sp, #8]\n    ldr.w r0, [pc, #0x480]\n    str r0, [sp, #4]\n    movw r0, #0x3a9\n    str r0, [sp]\n    ldr.w r3, [pc, #0x48c]\n    ldr.w r2, [pc, #0x48c]\n    ldr.w r1, [pc, #0x48c]\n    movs r0, #2\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am008_addr_0043d574\n    bl .\nL_open_cfw_runtime_am008_443cc_004a:\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am008_addr_0043d0ce\n    bl .\n    lsls r0, r0, #0x1f\n    bmi L_open_cfw_runtime_am008_443cc_005a\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am008_addr_0043d0ce\n    bl .\n    lsls r0, r0, #0x1d\n    bpl L_open_cfw_runtime_am008_443cc_006c\nL_open_cfw_runtime_am008_443cc_005a:\n    ldr.w r1, [pc, #0x45c]\n    mov.w r3, #0x2800\n    movs r2, r1\n    movs.w r0, #0x8400000\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am008_addr_0043ce9e\n    bl .\nL_open_cfw_runtime_am008_443cc_006c:\n    movs.w r0, #-1\n    b L_open_cfw_runtime_am008_443cc_00d4\nL_open_cfw_runtime_am008_443cc_0072:\n    movs r1, #0xc\n    movs r2, #0\n    add r7, sp, #0xc\n    movs r0, r7\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am008_addr_0043c0e4\n    bl .\n    movs r0, #5\n    strb.w r0, [sp, #0xc]\n    str r5, [sp, #0x10]\n    ldr.w r5, [pc, #0x44c]\n    movs.w r1, #-1\n    ldr r0, [r5]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am008_addr_004497b6\n    bl .\n    movs r2, r4\n    movs r1, r6\n    ldr r0, [pc, #0x40]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am008_addr_0046d8c4\n    bl .\n    ldr r0, [r5]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am008_addr_0044981c\n    bl .\n    str r4, [sp, #0x14]\n    mov.w r3, #0x3e8\n    movs r2, #0\n    add r1, sp, #0xc\n    ldr.w r0, [pc, #0x428]\n    ldr r0, [r0]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am008_addr_00449abe\n    bl .\n    cmp r0, #0\n    beq L_open_cfw_runtime_am008_443cc_00d2\n    ldr.w r0, [pc, #0x41c]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am008_addr_004733ee\n    bl .\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am008_addr_005fa0a4\n    bl .\n    movs r0, #0\n    movs.w r1, #-1\n    str r0, [r1]\nL_open_cfw_runtime_am008_443cc_00d0:\n    b L_open_cfw_runtime_am008_443cc_00d0\nL_open_cfw_runtime_am008_443cc_00d2:\n    movs r0, #0\nL_open_cfw_runtime_am008_443cc_00d4:\n    add sp, #0x1c\n    pop {r4, r5, r6, r7, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM008_444B8_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am008_444b8(void)
{
    __asm__ volatile(
        "    push {r4, r5, r6, lr}\n    sub sp, #0x18\n    movs r5, r0\n    movs r4, r1\n    movs r1, #0xc\n    movs r2, #0\n    add r6, sp, #0xc\n    movs r0, r6\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am008_addr_0043c0e4\n    bl .\n    movw r0, #0x2801\n    cmp r4, r0\n    blo L_open_cfw_runtime_am008_444b8_0070\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am008_addr_0043d0ce\n    bl .\n    lsls r0, r0, #0x1e\n    bpl L_open_cfw_runtime_am008_444b8_0048\n    mov.w r0, #0x2800\n    str r0, [sp, #8]\n    ldr.w r0, [pc, #0x398]\n    str r0, [sp, #4]\n    movw r0, #0x3c5\n    str r0, [sp]\n    ldr.w r3, [pc, #0x3bc]\n    ldr.w r2, [pc, #0x3a4]\n    ldr.w r1, [pc, #0x3a4]\n    movs r0, #2\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am008_addr_0043d574\n    bl .\nL_open_cfw_runtime_am008_444b8_0048:\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am008_addr_0043d0ce\n    bl .\n    lsls r0, r0, #0x1f\n    bmi L_open_cfw_runtime_am008_444b8_0058\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am008_addr_0043d0ce\n    bl .\n    lsls r0, r0, #0x1d\n    bpl L_open_cfw_runtime_am008_444b8_006a\nL_open_cfw_runtime_am008_444b8_0058:\n    ldr.w r1, [pc, #0x370]\n    mov.w r3, #0x2800\n    movs r2, r1\n    movs.w r0, #0x8400000\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am008_addr_0043ce9e\n    bl .\nL_open_cfw_runtime_am008_444b8_006a:\n    movs.w r0, #-1\n    b L_open_cfw_runtime_am008_444b8_00ce\nL_open_cfw_runtime_am008_444b8_0070:\n    movs r1, #0xc\n    movs r2, #0\n    add r6, sp, #0xc\n    movs r0, r6\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am008_addr_0043c0e4\n    bl .\n    movs r0, #8\n    strb.w r0, [sp, #0xc]\n    movs r0, #0\n    str r0, [sp, #0x10]\n    ldr r6, [pc, #0x360]\n    movs.w r1, #-1\n    ldr r0, [r6]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am008_addr_004497b6\n    bl .\n    movs r2, r4\n    movs r1, r5\n    ldr r0, [pc, #0x360]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am008_addr_0046d8c4\n    bl .\n    ldr r0, [r6]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am008_addr_0044981c\n    bl .\n    str r4, [sp, #0x14]\n    mov.w r3, #0x3e8\n    movs r2, #0\n    add r1, sp, #0xc\n    ldr r0, [pc, #0x33c]\n    ldr r0, [r0]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am008_addr_00449abe\n    bl .\n    cmp r0, #0\n    beq L_open_cfw_runtime_am008_444b8_00cc\n    ldr r0, [pc, #0x334]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am008_addr_004733ee\n    bl .\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am008_addr_005fa0a4\n    bl .\n    movs r0, #0\n    movs.w r1, #-1\n    str r0, [r1]\nL_open_cfw_runtime_am008_444b8_00ca:\n    b L_open_cfw_runtime_am008_444b8_00ca\nL_open_cfw_runtime_am008_444b8_00cc:\n    movs r0, #0\nL_open_cfw_runtime_am008_444b8_00ce:\n    add sp, #0x18\n    pop {r4, r5, r6, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM008_445A4_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am008_445a4(void)
{
    __asm__ volatile(
        "    push {r3, r4, r5, r6, r7, lr}\n    sub sp, #0x18\n    movs r4, r0\n    movs r5, r1\n    movs r6, r2\n    movs r1, #0xc\n    movs r2, #0\n    add r7, sp, #0xc\n    movs r0, r7\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am008_addr_0043c0e4\n    bl .\n    movs r1, #0xc\n    movs r2, #0\n    add r7, sp, #0xc\n    movs r0, r7\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am008_addr_0043c0e4\n    bl .\n    movs r0, #7\n    strb.w r0, [sp, #0xc]\n    movs r0, #0\n    str r0, [sp, #0x10]\n    movs r1, #0xa\n    movs r2, #0\n    mov r7, sp\n    movs r0, r7\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am008_addr_0043c0e4\n    bl .\n    movs r0, r4\n    strb.w r0, [sp]\n    uxth r4, r4\n    lsrs r4, r4, #8\n    strb.w r4, [sp, #1]\n    movs r0, r5\n    strb.w r0, [sp, #2]\n    movs r0, r5\n    lsrs r0, r0, #8\n    strb.w r0, [sp, #3]\n    mov r0, sp\n    movs r1, r5\n    lsrs r1, r1, #0x10\n    strb r1, [r0, #4]\n    lsrs r5, r5, #0x18\n    strb.w r5, [sp, #5]\n    movs r1, r6\n    strb.w r1, [sp, #6]\n    movs r1, r6\n    asrs r1, r1, #8\n    strb r1, [r0, #7]\n    movs r1, r6\n    asrs r1, r1, #0x10\n    strb r1, [r0, #8]\n    asrs r6, r6, #0x18\n    strb.w r6, [sp, #9]\n    ldr r4, [pc, #0x280]\n    movs.w r1, #-1\n    ldr r0, [r4]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am008_addr_004497b6\n    bl .\n    movs r2, #0xa\n    mov r1, sp\n    ldr r0, [pc, #0x280]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am008_addr_0046d8c4\n    bl .\n    ldr r0, [r4]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am008_addr_0044981c\n    bl .\n    movs r0, #0xa\n    str r0, [sp, #0x14]\n    mov.w r3, #0x3e8\n    movs r2, #0\n    add r1, sp, #0xc\n    ldr r0, [pc, #0x25c]\n    ldr r0, [r0]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am008_addr_00449abe\n    bl .\n    cmp r0, #0\n    beq L_open_cfw_runtime_am008_445a4_00c2\n    ldr r0, [pc, #0x260]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am008_addr_004733ee\n    bl .\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am008_addr_005fa0a4\n    bl .\n    movs r0, #0\n    movs.w r1, #-1\n    str r0, [r1]\nL_open_cfw_runtime_am008_445a4_00c0:\n    b L_open_cfw_runtime_am008_445a4_00c0\nL_open_cfw_runtime_am008_445a4_00c2:\n    movs r0, #0\n    add sp, #0x1c\n    pop {r4, r5, r6, r7, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM008_4466C_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am008_4466c(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    mov r1, sp\n    movs r0, #0\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am008_addr_00471e9e\n    bl .\n    ldr r0, [sp]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am008_addr_00471ebc\n    bl .\n    movs r0, #1\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am008_addr_00473474\n    bl .\n    pop {r0, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM008_488EC_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am008_488ec(void)
{
    __asm__ volatile(
        "    str r1, [r0]\n    dmb sy\n    bx lr\n"
    );
}
#endif

#if defined(OPEN_CFW_AM008_488F4_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am008_488f4(void)
{
    __asm__ volatile(
        "    ldr r0, [r0]\n    dmb sy\n    bx lr\n"
    );
}
#endif

#if defined(OPEN_CFW_AM008_488FC_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am008_488fc(void)
{
    __asm__ volatile(
        "    push {r4, r5}\n    ldr r5, [r1]\nL_open_cfw_runtime_am008_488fc_0004:\n    ldrex r3, [r0]\n    cmp r3, r5\n    bne L_open_cfw_runtime_am008_488fc_0014\n    strex r4, r2, [r0]\n    cmp r4, #0\n    bne L_open_cfw_runtime_am008_488fc_0004\nL_open_cfw_runtime_am008_488fc_0014:\n    dmb sy\n    ldr r0, [r1]\n    cmp r3, r0\n    bne L_open_cfw_runtime_am008_488fc_0022\n    movs r0, #1\n    b L_open_cfw_runtime_am008_488fc_0024\nL_open_cfw_runtime_am008_488fc_0022:\n    movs r0, #0\nL_open_cfw_runtime_am008_488fc_0024:\n    movs r2, r0\n    uxtb r2, r2\n    cmp r2, #0\n    bne L_open_cfw_runtime_am008_488fc_002e\n    str r3, [r1]\nL_open_cfw_runtime_am008_488fc_002e:\n    uxtb r0, r0\n    pop {r4, r5}\n    bx lr\n"
    );
}
#endif

#if defined(OPEN_CFW_AM008_48930_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am008_48930(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am008_488ec\n    bl .\n    pop {r0, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM008_48938_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am008_48938(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am008_488f4\n    bl .\n    pop {r1, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM008_48940_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am008_48940(void)
{
    __asm__ volatile(
        "    push {r2, r3, r4, lr}\n    movs r4, r1\n    ldr r1, [r4]\n    str r1, [sp]\n    mov r1, sp\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am008_488fc\n    bl .\n    movs r1, r0\n    uxtb r1, r1\n    cmp r1, #0\n    bne L_open_cfw_runtime_am008_48940_001a\n    ldr r1, [sp]\n    str r1, [r4]\nL_open_cfw_runtime_am008_48940_001a:\n    uxtb r0, r0\n    pop {r1, r2, r4, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM008_4895E_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am008_4895e(void)
{
    __asm__ volatile(
        "    push {r3, r4, r5, r6, r7, lr}\n    movs r4, #0\n    b L_open_cfw_runtime_am008_4895e_0046\nL_open_cfw_runtime_am008_4895e_0006:\n    mov.w r5, #0x110\n    movs r1, r5\n    movs r2, #0\n    ldr.w r6, [pc, #0x5d0]\n    mul r0, r5, r4\n    add.w r7, r6, r0\n    movs r0, r7\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am008_addr_0043c0e4\n    bl .\n    movs r1, #0\n    mul r0, r5, r4\n    add r0, r6\n    adds r0, r0, #4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am008_488ec\n    bl .\n    mul r0, r5, r4\n    add r0, r6\n    adds.w r1, r0, #0x110\n    mul r5, r5, r4\n    add.w r0, r6, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am008_48930\n    bl .\n    adds r4, r4, #1\nL_open_cfw_runtime_am008_4895e_0046:\n    cmp r4, #0xfe\n    blt L_open_cfw_runtime_am008_4895e_0006\n    ldr.w r4, [pc, #0x594]\n    movs r1, #0\n    ldr.w r0, [pc, #0x5c8]\n    add r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am008_488ec\n    bl .\n    movs r1, #0\n    ldr.w r0, [pc, #0x5d4]\n    add r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am008_48930\n    bl .\n    movs r1, #0\n    ldr.w r0, [pc, #0x5cc]\n    add r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am008_488ec\n    bl .\n    movs r1, #0\n    ldr.w r0, [pc, #0x5d8]\n    add r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am008_48930\n    bl .\n    movs r1, r4\n    ldr.w r0, [pc, #0x5d0]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am008_48930\n    bl .\n    pop {r0, r4, r5, r6, r7, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM008_489E8_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am008_489e8(void)
{
    __asm__ volatile(
        "    push {r3, r4, r5, lr}\n    ldr.w r4, [pc, #0x5c8]\n    movs r1, #0\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am008_48930\n    bl .\n    ldr.w r5, [pc, #0x5c0]\n    movs r1, r4\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am008_48930\n    bl .\n    movs r1, r4\n    adds r0, r5, #4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am008_48930\n    bl .\n    pop {r0, r4, r5, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM008_48A0C_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am008_48a0c(void)
{
    __asm__ volatile(
        "    push {r3, r4, r5, lr}\n    movs r4, #0\nL_open_cfw_runtime_am008_48a0c_0004:\n    ldr.w r5, [pc, #0x59c]\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am008_48938\n    bl .\n    str r0, [sp]\n    ldr r0, [sp]\n    cmp r0, #0\n    beq L_open_cfw_runtime_am008_48a0c_0036\n    ldr r0, [sp]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am008_48938\n    bl .\n    adds r4, r4, #1\n    movw r1, #0x3e9\n    cmp r4, r1\n    bge L_open_cfw_runtime_am008_48a0c_0044\n    movs r2, r0\n    mov r1, sp\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am008_48940\n    bl .\n    cmp r0, #0\n    beq L_open_cfw_runtime_am008_48a0c_0004\n    b L_open_cfw_runtime_am008_48a0c_0058\nL_open_cfw_runtime_am008_48a0c_0036:\n    ldr.w r0, [pc, #0x578]\n    ldr r1, [r0, #4]\n    adds r1, r1, #1\n    str r1, [r0, #4]\n    movs r0, #0\n    b L_open_cfw_runtime_am008_48a0c_0080\nL_open_cfw_runtime_am008_48a0c_0044:\n    ldr.w r0, [pc, #0x568]\n    ldr r1, [r0, #0x2c]\n    adds r1, r1, #1\n    str r1, [r0, #0x2c]\n    ldr r1, [r0, #4]\n    adds r1, r1, #1\n    str r1, [r0, #4]\n    movs r0, #0\n    b L_open_cfw_runtime_am008_48a0c_0080\nL_open_cfw_runtime_am008_48a0c_0058:\n    ldr.w r1, [pc, #0x554]\n    ldr r2, [r1, #0xc]\n    subs r0, r4, #1\n    adds r2, r0, r2\n    str r2, [r1, #0xc]\n    ldr r0, [r1, #0x10]\n    cmp r0, r4\n    bhs L_open_cfw_runtime_am008_48a0c_006c\n    str r4, [r1, #0x10]\nL_open_cfw_runtime_am008_48a0c_006c:\n    movs r1, #1\n    ldr r0, [sp]\n    adds r0, r0, #4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am008_488ec\n    bl .\n    movs r1, #0\n    ldr r0, [sp]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am008_48930\n    bl .\n    ldr r0, [sp]\nL_open_cfw_runtime_am008_48a0c_0080:\n    pop {r1, r4, r5, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM008_48A8E_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am008_48a8e(void)
{
    __asm__ volatile(
        "    push {r2, r3, r4, r5, r6, lr}\n    movs r4, r0\n    cmp r4, #0\n    beq L_open_cfw_runtime_am008_48a8e_0060\n    movs r5, #0\n    movs r1, #0\n    adds r0, r4, #4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am008_488ec\n    bl .\nL_open_cfw_runtime_am008_48a8e_0012:\n    ldr.w r6, [pc, #0x50c]\n    movs r0, r6\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am008_48938\n    bl .\n    str r0, [sp]\n    ldr r1, [sp]\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am008_48930\n    bl .\n    adds r5, r5, #1\n    movw r0, #0x3e9\n    cmp r5, r0\n    bge L_open_cfw_runtime_am008_48a8e_0040\n    movs r2, r4\n    mov r1, sp\n    movs r0, r6\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am008_48940\n    bl .\n    cmp r0, #0\n    beq L_open_cfw_runtime_am008_48a8e_0012\n    b L_open_cfw_runtime_am008_48a8e_004c\nL_open_cfw_runtime_am008_48a8e_0040:\n    ldr.w r0, [pc, #0x4ec]\n    ldr r1, [r0, #0x2c]\n    adds r1, r1, #1\n    str r1, [r0, #0x2c]\n    b L_open_cfw_runtime_am008_48a8e_0060\nL_open_cfw_runtime_am008_48a8e_004c:\n    ldr.w r1, [pc, #0x4e0]\n    ldr r2, [r1, #0x14]\n    subs r0, r5, #1\n    adds r2, r0, r2\n    str r2, [r1, #0x14]\n    ldr r0, [r1, #0x18]\n    cmp r0, r5\n    bhs L_open_cfw_runtime_am008_48a8e_0060\n    str r5, [r1, #0x18]\nL_open_cfw_runtime_am008_48a8e_0060:\n    pop {r0, r1, r4, r5, r6, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM008_48AF0_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am008_48af0(void)
{
    __asm__ volatile(
        "    push {r2, r3, r4, r5, r6, lr}\n    movs r4, r0\n    cmp r4, #0\n    bne L_open_cfw_runtime_am008_48af0_000c\n    movs r0, #0\n    b L_open_cfw_runtime_am008_48af0_00a4\nL_open_cfw_runtime_am008_48af0_000c:\n    movs r5, #0\n    movs r1, #2\n    adds r0, r4, #4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am008_488ec\n    bl .\n    movs r1, #0\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am008_48930\n    bl .\n    b L_open_cfw_runtime_am008_48af0_002a\nL_open_cfw_runtime_am008_48af0_0020:\n    ldr r2, [sp, #4]\n    mov r1, sp\n    movs r0, r6\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am008_48940\n    bl .\nL_open_cfw_runtime_am008_48af0_002a:\n    ldr.w r6, [pc, #0x4a4]\n    movs r0, r6\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am008_48938\n    bl .\n    str r0, [sp]\n    ldr r0, [sp]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am008_48938\n    bl .\n    str r0, [sp, #4]\n    adds r5, r5, #1\n    movw r0, #0x2711\n    cmp r5, r0\n    bge L_open_cfw_runtime_am008_48af0_006a\n    movs r0, r6\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am008_48938\n    bl .\n    ldr r1, [sp]\n    cmp r1, r0\n    bne L_open_cfw_runtime_am008_48af0_002a\n    ldr r0, [sp, #4]\n    cmp r0, #0\n    bne L_open_cfw_runtime_am008_48af0_0020\n    movs r2, r4\n    add r1, sp, #4\n    ldr r0, [sp]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am008_48940\n    bl .\n    cmp r0, #0\n    beq L_open_cfw_runtime_am008_48af0_002a\n    b L_open_cfw_runtime_am008_48af0_0084\nL_open_cfw_runtime_am008_48af0_006a:\n    ldr.w r0, [pc, #0x460]\n    ldr r1, [r0, #0x2c]\n    adds r1, r1, #1\n    str r1, [r0, #0x2c]\n    ldr r1, [r0, #4]\n    adds r1, r1, #1\n    str r1, [r0, #4]\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am008_48a8e\n    bl .\n    movs r0, #0\n    b L_open_cfw_runtime_am008_48af0_00a4\nL_open_cfw_runtime_am008_48af0_0084:\n    ldr.w r1, [pc, #0x444]\n    ldr r2, [r1, #0x1c]\n    subs r0, r5, #1\n    adds r2, r0, r2\n    str r2, [r1, #0x1c]\n    ldr r0, [r1, #0x20]\n    cmp r0, r5\n    bhs L_open_cfw_runtime_am008_48af0_0098\n    str r5, [r1, #0x20]\nL_open_cfw_runtime_am008_48af0_0098:\n    movs r2, r4\n    mov r1, sp\n    movs r0, r6\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am008_48940\n    bl .\n    movs r0, #1\nL_open_cfw_runtime_am008_48af0_00a4:\n    pop {r1, r2, r4, r5, r6, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM008_42134_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am008_42134(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    ldr r0, [r0, #0x18]\n    ldrb r0, [r0, #-0x2]\n    uxtb r0, r0\n    cmp r0, #2\n    bne L_open_cfw_runtime_am008_42134_0018\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am008_420a6\n    bl .\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am008_addr_005fa058\n    bl .\n    pop {r0, pc}\nL_open_cfw_runtime_am008_42134_0018:\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am008_addr_005fa0a4\n    bl .\n    movs r0, #0\n    movs.w r1, #-1\n    str r0, [r1]\nL_open_cfw_runtime_am008_42134_0024:\n    b L_open_cfw_runtime_am008_42134_0024\n"
    );
}
#endif
