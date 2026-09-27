/*
 * SPDX-License-Identifier: MIT
 *
 * Source-owned exact helpers from the AM-009 retained island.
 */

#if defined(OPEN_CFW_AM009_48B96_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am009_48b96(void)
{
    __asm__ volatile(
        "    push {r1, r2, r3, r4, r5, r6, r7, lr}\n    movs r5, #0\n    b L_open_cfw_runtime_am009_48b96_0006\nL_open_cfw_runtime_am009_48b96_0006:\n    ldr.w r6, [pc, #0x418]\n    movs r0, r6\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am009_addr_00448938\n    bl .\n    str r0, [sp]\n    adds r7, r6, #4\n    movs r0, r7\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am009_addr_00448938\n    bl .\n    str r0, [sp, #4]\n    ldr r0, [sp]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am009_addr_00448938\n    bl .\n    movs r4, r0\n    adds r5, r5, #1\n    movw r0, #0x2711\n    cmp r5, r0\n    bge L_open_cfw_runtime_am009_48b96_003c\n    movs r0, r6\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am009_addr_00448938\n    bl .\n    ldr r1, [sp]\n    cmp r1, r0\n    bne L_open_cfw_runtime_am009_48b96_0006\n    b L_open_cfw_runtime_am009_48b96_004a\nL_open_cfw_runtime_am009_48b96_003c:\n    ldr.w r0, [pc, #0x3e8]\n    ldr r1, [r0, #0x2c]\n    adds r1, r1, #1\n    str r1, [r0, #0x2c]\n    movs r0, #0\n    b L_open_cfw_runtime_am009_48b96_00dc\nL_open_cfw_runtime_am009_48b96_004a:\n    ldr r0, [sp]\n    ldr r1, [sp, #4]\n    cmp r0, r1\n    bne L_open_cfw_runtime_am009_48b96_0066\n    cmp r4, #0\n    bne L_open_cfw_runtime_am009_48b96_005a\n    movs r0, #0\n    b L_open_cfw_runtime_am009_48b96_00dc\nL_open_cfw_runtime_am009_48b96_005a:\n    movs r2, r4\n    add r1, sp, #4\n    movs r0, r7\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am009_addr_00448940\n    bl .\n    b L_open_cfw_runtime_am009_48b96_0006\nL_open_cfw_runtime_am009_48b96_0066:\n    cmp r4, #0\n    beq L_open_cfw_runtime_am009_48b96_0006\n    movs r2, r4\n    mov r1, sp\n    movs r0, r6\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am009_addr_00448940\n    bl .\n    cmp r0, #0\n    beq L_open_cfw_runtime_am009_48b96_0006\n    ldr.w r1, [pc, #0x3ac]\n    ldr r2, [r1, #0x24]\n    subs r0, r5, #1\n    adds r2, r0, r2\n    str r2, [r1, #0x24]\n    ldr r0, [r1, #0x28]\n    cmp r0, r5\n    bhs L_open_cfw_runtime_am009_48b96_008c\n    str r5, [r1, #0x28]\nL_open_cfw_runtime_am009_48b96_008c:\n    ldr r0, [sp]\n    ldr.w r1, [pc, #0x38c]\n    cmp r0, r1\n    bne L_open_cfw_runtime_am009_48b96_00ba\n    ldrh r2, [r4, #8]\n    adds r2, r2, #1\n    adds.w r1, r4, #0xd\n    ldr r0, [sp]\n    adds.w r5, r0, #0xd\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am009_addr_00439be4\n    bl .\n    ldrh r0, [r4, #8]\n    ldr r1, [sp]\n    strh r0, [r1, #8]\n    ldrh r0, [r4, #0xa]\n    ldr r1, [sp]\n    strh r0, [r1, #0xa]\n    ldr r0, [sp]\n    b L_open_cfw_runtime_am009_48b96_00dc\nL_open_cfw_runtime_am009_48b96_00ba:\n    ldrh r2, [r4, #8]\n    adds r2, r2, #1\n    adds.w r1, r4, #0xd\n    ldr r0, [sp]\n    adds.w r5, r0, #0xd\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am009_addr_00439be4\n    bl .\n    ldrh r0, [r4, #8]\n    ldr r1, [sp]\n    strh r0, [r1, #8]\n    ldrh r0, [r4, #0xa]\n    ldr r1, [sp]\n    strh r0, [r1, #0xa]\n    ldr r0, [sp]\nL_open_cfw_runtime_am009_48b96_00dc:\n    pop {r1, r2, r3, r4, r5, r6, r7, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM009_48C74_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am009_48c74(void)
{
    __asm__ volatile(
        "    push {r3, r4, r5, lr}\n    ldr.w r4, [pc, #0x34c]\n    ldrb r0, [r4]\n    cmp r0, #0\n    beq L_open_cfw_runtime_am009_48c74_0010\n    movs r0, #0\n    b L_open_cfw_runtime_am009_48c74_0034\nL_open_cfw_runtime_am009_48c74_0010:\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am009_addr_0044895e\n    bl .\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am009_addr_004489e8\n    bl .\n    movs r1, #0x30\n    movs r2, #0\n    ldr.w r5, [pc, #0x328]\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am009_addr_0043c0e4\n    bl .\n    movs r0, #1\n    ldr.w r1, [pc, #0x328]\n    strb r0, [r1]\n    movs r0, #1\n    strb r0, [r4]\n    movs r0, #0\nL_open_cfw_runtime_am009_48c74_0034:\n    pop {r1, r4, r5, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM009_48CB8_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am009_48cb8(void)
{
    __asm__ volatile(
        "    ldr.w r2, [pc, #0x310]\n    strb r0, [r2, #8]\n    str r1, [r2, #0xc]\n    movs r0, #0\n    bx lr\n"
    );
}
#endif

#if defined(OPEN_CFW_AM009_48DD2_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am009_48dd2(void)
{
    __asm__ volatile(
        "    push {r4, r5, r6, lr}\n    ldr r0, [pc, #0x1ec]\n    ldrb r0, [r0]\n    cmp r0, #0\n    bne L_open_cfw_runtime_am009_48dd2_000e\n    movs r0, #0\n    b L_open_cfw_runtime_am009_48dd2_0056\nL_open_cfw_runtime_am009_48dd2_000e:\n    movs r5, #0\n    movs r6, #0\n    b L_open_cfw_runtime_am009_48dd2_0044\nL_open_cfw_runtime_am009_48dd2_0014:\n    ldrb r0, [r4, #0xa]\n    lsls r0, r0, #0x1f\n    bpl L_open_cfw_runtime_am009_48dd2_0032\n    ldr r2, [pc, #0x1dc]\n    ldrb r0, [r2]\n    cmp r0, #0\n    beq L_open_cfw_runtime_am009_48dd2_0032\n    ldr r0, [r2, #4]\n    cmp r0, #0\n    beq L_open_cfw_runtime_am009_48dd2_0032\n    ldrh r1, [r4, #8]\n    adds.w r0, r4, #0xd\n    ldr r2, [r2, #4]\n    blx r2\nL_open_cfw_runtime_am009_48dd2_0032:\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am009_addr_00448a8e\n    bl .\n    adds r5, r5, #1\n    ldr r0, [pc, #0x1ac]\n    ldr r1, [r0]\n    adds r1, r1, #1\n    str r1, [r0]\n    adds r6, r6, #1\nL_open_cfw_runtime_am009_48dd2_0044:\n    cmp.w r6, #0x100\n    bhs L_open_cfw_runtime_am009_48dd2_0054\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am009_48b96\n    bl .\n    movs r4, r0\n    cmp r4, #0\n    bne L_open_cfw_runtime_am009_48dd2_0014\nL_open_cfw_runtime_am009_48dd2_0054:\n    movs r0, r5\nL_open_cfw_runtime_am009_48dd2_0056:\n    pop {r4, r5, r6, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM009_48E2A_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am009_48e2a(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    ldr r0, [pc, #0x1a4]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am009_addr_0047db02\n    bl .\n    pop {r1, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM009_48E34_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am009_48e34(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    ldr r2, [pc, #0x1a0]\n    ldr r0, [r2]\n    cmp r0, #0\n    beq L_open_cfw_runtime_am009_48e34_0012\n    movs r1, #4\n    ldr r0, [r2]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am009_495e4\n    bl .\nL_open_cfw_runtime_am009_48e34_0012:\n    pop {r0, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM009_48E48_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am009_48e48(void)
{
    __asm__ volatile(
        "    push {r5, r6, r7, lr}\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am009_48e2a\n    bl .\n    cmp r0, #0\n    beq L_open_cfw_runtime_am009_48e48_0044\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am009_addr_0043d0ce\n    bl .\n    lsls r0, r0, #0x1e\n    bpl L_open_cfw_runtime_am009_48e48_0028\n    ldr r0, [pc, #0x180]\n    str r0, [sp, #4]\n    movw r0, #0x3fa\n    str r0, [sp]\n    ldr r3, [pc, #0x178]\n    ldr r2, [pc, #0x17c]\n    ldr r1, [pc, #0x17c]\n    movs r0, #2\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am009_addr_0043d574\n    bl .\nL_open_cfw_runtime_am009_48e48_0028:\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am009_addr_0043d0ce\n    bl .\n    lsls r0, r0, #0x1f\n    bmi L_open_cfw_runtime_am009_48e48_0038\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am009_addr_0043d0ce\n    bl .\n    lsls r0, r0, #0x1d\n    bpl L_open_cfw_runtime_am009_48e48_0044\nL_open_cfw_runtime_am009_48e48_0038:\n    ldr r1, [pc, #0x168]\n    movs r2, r1\n    movs.w r0, #0x8000000\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am009_addr_0043ce9e\n    bl .\nL_open_cfw_runtime_am009_48e48_0044:\n    pop {r0, r1, r2, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM009_48F7C_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am009_48f7c(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    ldr r2, [pc, #0x58]\n    ldr r0, [r2]\n    cmp r0, #0\n    beq L_open_cfw_runtime_am009_48f7c_0012\n    movs r1, #2\n    ldr r0, [r2]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am009_495e4\n    bl .\nL_open_cfw_runtime_am009_48f7c_0012:\n    pop {r0, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM009_48F98_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am009_48f98(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    ldr r2, [pc, #0x3c]\n    ldr r0, [r2]\n    cmp r0, #0\n    beq L_open_cfw_runtime_am009_48f98_0012\n    movs r1, #8\n    ldr r0, [r2]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am009_495e4\n    bl .\nL_open_cfw_runtime_am009_48f98_0012:\n    pop {r0, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM009_4900C_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am009_4900c(void)
{
    __asm__ volatile(
        "    bx lr\n"
    );
}
#endif

#if defined(OPEN_CFW_AM009_4900E_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am009_4900e(void)
{
    __asm__ volatile(
        "    b.w #0x7b448c\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n"
    );
}
#endif

#if defined(OPEN_CFW_AM009_490CC_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am009_490cc(void)
{
    __asm__ volatile(
        "    b.w #0x7b44bc\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n"
    );
}
#endif

#if defined(OPEN_CFW_AM009_491AA_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am009_491aa(void)
{
    __asm__ volatile(
        "    b.w #0x7b44d4\n    nop\n    nop\n"
    );
}
#endif

#if defined(OPEN_CFW_AM009_491E4_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am009_491e4(void)
{
    __asm__ volatile(
        "    b.w #0x7b4550\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n"
    );
}
#endif

#if defined(OPEN_CFW_AM009_49398_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am009_49398(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am009_addr_0047eb26\n    bl .\n    movs r1, r0\n    lsrs r1, r1, #1\n    lsls r1, r1, #1\n    cmp r1, #0\n    beq L_open_cfw_runtime_am009_49398_0016\n    ldr r0, [r1, #4]\n    ldr r1, [r1]\n    blx r1\nL_open_cfw_runtime_am009_49398_0016:\n    pop {r0, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM009_493B0_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am009_493b0(void)
{
    __asm__ volatile(
        "    b.w #0x7b4908\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n"
    );
}
#endif

#if defined(OPEN_CFW_AM009_49498_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am009_49498(void)
{
    __asm__ volatile(
        "    b.w #0x7b46b0\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n"
    );
}
#endif

#if defined(OPEN_CFW_AM009_494D8_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am009_494d8(void)
{
    __asm__ volatile(
        "    b.w #0x7b46f8\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n"
    );
}
#endif

#if defined(OPEN_CFW_AM009_49522_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am009_49522(void)
{
    __asm__ volatile(
        "    b.w #0x7b45b8\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n"
    );
}
#endif

#if defined(OPEN_CFW_AM009_4953E_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am009_4953e(void)
{
    __asm__ volatile(
        "    b.w #0x7b4748\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n"
    );
}
#endif

#if defined(OPEN_CFW_AM009_49590_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am009_49590(void)
{
    __asm__ volatile(
        "    b.w #0x7b47a0\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n"
    );
}
#endif

#if defined(OPEN_CFW_AM009_495E4_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am009_495e4(void)
{
    __asm__ volatile(
        "    b.w #0x7b47d0\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n"
    );
}
#endif

#if defined(OPEN_CFW_AM009_49642_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am009_49642(void)
{
    __asm__ volatile(
        "    b.w #0x7b4830\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n"
    );
}
#endif

#if defined(OPEN_CFW_AM009_4969C_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am009_4969c(void)
{
    __asm__ volatile(
        "    b.w #0x7b4884\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n"
    );
}
#endif

#if defined(OPEN_CFW_AM009_497B6_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am009_497b6(void)
{
    __asm__ volatile(
        "    b.w #0x7b45d4\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n"
    );
}
#endif

#if defined(OPEN_CFW_AM009_4981C_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am009_4981c(void)
{
    __asm__ volatile(
        "    b.w #0x7b461c\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n"
    );
}
#endif

#if defined(OPEN_CFW_AM009_4986E_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am009_4986e(void)
{
    __asm__ volatile(
        "    b.w #0x7b4590\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n"
    );
}
#endif

#if defined(OPEN_CFW_AM009_499B8_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am009_499b8(void)
{
    __asm__ volatile(
        "    b.w #0x7b465c\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n"
    );
}
#endif

#if defined(OPEN_CFW_AM009_49A0E_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am009_49a0e(void)
{
    __asm__ volatile(
        "    b.w #0x7b44e4\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n    nop\n"
    );
}
#endif

#if defined(OPEN_CFW_AM009_4AA2C_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am009_4aa2c(void)
{
    __asm__ volatile(
        "    push {r4, lr}\n    ldr r4, [pc, #0xcc]\n    ldr r0, [r4]\n    cmp r0, #0\n    bne L_open_cfw_runtime_am009_4aa2c_0012\n    ldr r0, [pc, #0xc8]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am009_addr_0044971c\n    bl .\n    str r0, [r4]\nL_open_cfw_runtime_am009_4aa2c_0012:\n    pop {r4, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM009_4AA40_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am009_4aa40(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    ldr r2, [pc, #0xb8]\n    ldr r0, [r2]\n    cmp r0, #0\n    beq L_open_cfw_runtime_am009_4aa40_0014\n    mov.w r1, #0x3e8\n    ldr r0, [r2]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am009_497b6\n    bl .\nL_open_cfw_runtime_am009_4aa40_0014:\n    pop {r0, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM009_4AA56_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am009_4aa56(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    ldr r1, [pc, #0xa0]\n    ldr r0, [r1]\n    cmp r0, #0\n    beq L_open_cfw_runtime_am009_4aa56_0010\n    ldr r0, [r1]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am009_4981c\n    bl .\nL_open_cfw_runtime_am009_4aa56_0010:\n    pop {r0, pc}\n"
    );
}
#endif
