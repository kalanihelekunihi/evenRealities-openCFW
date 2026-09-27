/*
 * SPDX-License-Identifier: MIT
 *
 * Source-owned exact helpers from the AM-005 retained island.
 */

#if defined(OPEN_CFW_AM005_EF70_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am005_ef70(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    movs r2, #0x18\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am005_addr_0044bdea\n    bl .\n    pop {r1, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM005_EF7A_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am005_ef7a(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    movs r2, #0x19\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am005_addr_0044bdea\n    bl .\n    pop {r1, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM005_EF84_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am005_ef84(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    movs r2, #0x1a\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am005_addr_0044bdea\n    bl .\n    pop {r1, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM005_EF8E_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am005_ef8e(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    movs r2, #0x1b\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am005_addr_0044bdea\n    bl .\n    pop {r1, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM005_EF98_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am005_ef98(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    movs r2, #0x30\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am005_addr_0044bdea\n    bl .\n    pop {r1, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM005_EFA2_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am005_efa2(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    movs r2, #0x34\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am005_addr_0044bdea\n    bl .\n    uxtb r0, r0\n    pop {r1, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM005_EFAE_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am005_efae(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    movs r2, #0x16\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am005_addr_0044bdea\n    bl .\n    uxth r0, r0\n    pop {r1, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM005_EFBA_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am005_efba(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    movs r2, #0x27\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am005_addr_0044bdea\n    bl .\n    uxtb r0, r0\n    pop {r1, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM005_EFC6_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am005_efc6(void)
{
    __asm__ volatile(
        "    push {r3, r4, r5, r6, r7, lr}\n    movs r4, r0\n    movs r5, r1\n    movs r1, r5\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am005_addr_0043ef5c\n    bl .\n    movs r6, r0\n    movs r1, r5\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am005_ef98\n    bl .\n    movs r7, r0\n    movs r1, r5\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am005_efa2\n    bl .\n    lsls r0, r0, #0x1d\n    bpl L_open_cfw_runtime_am005_efc6_002a\n    adds r6, r7, r6\n    b L_open_cfw_runtime_am005_efc6_002a\nL_open_cfw_runtime_am005_efc6_002a:\n    movs r0, r6\n    pop {r1, r4, r5, r6, r7, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM005_EFF4_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am005_eff4(void)
{
    __asm__ volatile(
        "    push {r3, r4, r5, r6, r7, lr}\n    movs r4, r0\n    movs r5, r1\n    movs r1, r5\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am005_addr_0043ef66\n    bl .\n    movs r6, r0\n    movs r1, r5\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am005_ef98\n    bl .\n    movs r7, r0\n    movs r1, r5\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am005_efa2\n    bl .\n    lsls r0, r0, #0x1c\n    bpl L_open_cfw_runtime_am005_eff4_002a\n    adds r6, r7, r6\n    b L_open_cfw_runtime_am005_eff4_002a\nL_open_cfw_runtime_am005_eff4_002a:\n    movs r0, r6\n    pop {r1, r4, r5, r6, r7, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM005_F022_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am005_f022(void)
{
    __asm__ volatile(
        "    push {r3, r4, r5, r6, r7, lr}\n    movs r4, r0\n    movs r5, r1\n    movs r1, r5\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am005_addr_0043ef48\n    bl .\n    movs r6, r0\n    movs r1, r5\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am005_ef98\n    bl .\n    movs r7, r0\n    movs r1, r5\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am005_efa2\n    bl .\n    lsls r0, r0, #0x1e\n    bpl L_open_cfw_runtime_am005_f022_002a\n    adds r6, r7, r6\n    b L_open_cfw_runtime_am005_f022_002a\nL_open_cfw_runtime_am005_f022_002a:\n    movs r0, r6\n    pop {r1, r4, r5, r6, r7, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM005_F050_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am005_f050(void)
{
    __asm__ volatile(
        "    push {r3, r4, r5, r6, r7, lr}\n    movs r4, r0\n    movs r5, r1\n    movs r1, r5\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am005_addr_0043ef52\n    bl .\n    movs r6, r0\n    movs r1, r5\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am005_ef98\n    bl .\n    movs r7, r0\n    movs r1, r5\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am005_efa2\n    bl .\n    lsls r0, r0, #0x1f\n    bpl L_open_cfw_runtime_am005_f050_002a\n    adds r6, r7, r6\n    b L_open_cfw_runtime_am005_f050_002a\nL_open_cfw_runtime_am005_f050_002a:\n    movs r0, r6\n    pop {r1, r4, r5, r6, r7, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM005_F07E_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am005_f07e(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am005_addr_0043ef16\n    bl .\n    cmp r0, #1\n    bge L_open_cfw_runtime_am005_f07e_000c\n    movs r0, #1\nL_open_cfw_runtime_am005_f07e_000c:\n    pop {r1, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM005_F08C_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am005_f08c(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am005_addr_0043ef20\n    bl .\n    cmp r0, #1\n    bge L_open_cfw_runtime_am005_f08c_000c\n    movs r0, #1\nL_open_cfw_runtime_am005_f08c_000c:\n    pop {r1, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM005_F09A_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am005_f09a(void)
{
    __asm__ volatile(
        "    push {r1, r2, r3, r4, r5, lr}\n    movs r4, r0\n    movs r5, r2\n    cmp r4, #0\n    bne L_open_cfw_runtime_am005_f09a_0036\n    ldr.w r0, [pc, #0xbbc]\n    str r0, [sp, #8]\n    ldr.w r0, [pc, #0xbbc]\n    str r0, [sp, #4]\n    ldr.w r0, [pc, #0xc18]\n    str r0, [sp]\n    ldr.w r3, [pc, #0xbb4]\n    movs r2, #0x35\n    ldr.w r1, [pc, #0xc80]\n    movs r0, #3\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am005_addr_0044d25c\n    bl .\nL_open_cfw_runtime_am005_f09a_002c:\n    movs r0, #0\n    movs.w r1, #-1\n    str r0, [r1]\n    b L_open_cfw_runtime_am005_f09a_002c\nL_open_cfw_runtime_am005_f09a_0036:\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am005_f0e0\n    bl .\n    movs r1, r5\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am005_f142\n    bl .\n    pop {r0, r1, r2, r4, r5, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM005_F0E0_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am005_f0e0(void)
{
    __asm__ volatile(
        "    push {r1, r2, r3, r4, r5, lr}\n    movs r4, r0\n    movs r5, r1\n    cmp r4, #0\n    bne L_open_cfw_runtime_am005_f0e0_0036\n    ldr.w r0, [pc, #0xb78]\n    str r0, [sp, #8]\n    ldr.w r0, [pc, #0xb74]\n    str r0, [sp, #4]\n    ldr.w r0, [pc, #0xbd4]\n    str r0, [sp]\n    ldr.w r3, [pc, #0xbd0]\n    movs r2, #0x3d\n    ldr.w r1, [pc, #0xc3c]\n    movs r0, #3\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am005_addr_0044d25c\n    bl .\nL_open_cfw_runtime_am005_f0e0_002c:\n    movs r0, #0\n    movs.w r1, #-1\n    str r0, [r1]\n    b L_open_cfw_runtime_am005_f0e0_002c\nL_open_cfw_runtime_am005_f0e0_0036:\n    movs r3, #0\n    mov r2, sp\n    movs r1, #8\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am005_addr_0044beaa\n    bl .\n    movs r1, r0\n    uxtb r1, r1\n    cmp r1, #1\n    bne L_open_cfw_runtime_am005_f0e0_0050\n    ldr r1, [sp]\n    cmp r1, r5\n    bne L_open_cfw_runtime_am005_f0e0_0056\nL_open_cfw_runtime_am005_f0e0_0050:\n    uxtb r0, r0\n    cmp r0, #0\n    bne L_open_cfw_runtime_am005_f0e0_0060\nL_open_cfw_runtime_am005_f0e0_0056:\n    movs r2, #0\n    movs r1, r5\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am005_addr_004411b8\n    bl .\nL_open_cfw_runtime_am005_f0e0_0060:\n    pop {r0, r1, r2, r4, r5, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM005_F142_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am005_f142(void)
{
    __asm__ volatile(
        "    push {r1, r2, r3, r4, r5, lr}\n    movs r4, r0\n    movs r5, r1\n    cmp r4, #0\n    bne L_open_cfw_runtime_am005_f142_0036\n    ldr.w r0, [pc, #0xb14]\n    str r0, [sp, #8]\n    ldr.w r0, [pc, #0xb14]\n    str r0, [sp, #4]\n    ldr.w r0, [pc, #0xb70]\n    str r0, [sp]\n    ldr.w r3, [pc, #0xb7c]\n    movs r2, #0x4b\n    ldr.w r1, [pc, #0xbd8]\n    movs r0, #3\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am005_addr_0044d25c\n    bl .\nL_open_cfw_runtime_am005_f142_002c:\n    movs r0, #0\n    movs.w r1, #-1\n    str r0, [r1]\n    b L_open_cfw_runtime_am005_f142_002c\nL_open_cfw_runtime_am005_f142_0036:\n    movs r3, #0\n    mov r2, sp\n    movs r1, #9\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am005_addr_0044beaa\n    bl .\n    movs r1, r0\n    uxtb r1, r1\n    cmp r1, #1\n    bne L_open_cfw_runtime_am005_f142_0050\n    ldr r1, [sp]\n    cmp r1, r5\n    bne L_open_cfw_runtime_am005_f142_0056\nL_open_cfw_runtime_am005_f142_0050:\n    uxtb r0, r0\n    cmp r0, #0\n    bne L_open_cfw_runtime_am005_f142_0060\nL_open_cfw_runtime_am005_f142_0056:\n    movs r2, #0\n    movs r1, r5\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am005_addr_004411c6\n    bl .\nL_open_cfw_runtime_am005_f142_0060:\n    pop {r0, r1, r2, r4, r5, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM005_F1A4_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am005_f1a4(void)
{
    __asm__ volatile(
        "    push.w {r3, r4, r5, r6, r7, r8, sb, sl, fp, lr}\n    sub sp, #0x20\n    movs r4, r0\n    cmp r4, #0\n    bne L_open_cfw_runtime_am005_f1a4_0038\n    ldr.w r0, [pc, #0xb20]\n    str r0, [sp, #8]\n    ldr.w r0, [pc, #0xb20]\n    str r0, [sp, #4]\n    ldr.w r0, [pc, #0xb0c]\n    str r0, [sp]\n    ldr.w r3, [pc, #0xbc8]\n    movs r2, #0x59\n    ldr.w r1, [pc, #0xbc4]\n    movs r0, #3\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am005_addr_0044d25c\n    bl .\nL_open_cfw_runtime_am005_f1a4_002e:\n    movs r0, #0\n    movs.w r1, #-1\n    str r0, [r1]\n    b L_open_cfw_runtime_am005_f1a4_002e\nL_open_cfw_runtime_am005_f1a4_0038:\n    ldrh r0, [r4, #0x2a]\n    ands r0, r0, #0xc00\n    cmp.w r0, #0xc00\n    bne L_open_cfw_runtime_am005_f1a4_0048\n    movs r0, #0\n    b L_open_cfw_runtime_am005_f1a4_0316\nL_open_cfw_runtime_am005_f1a4_0048:\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am005_addr_0044dca2\n    bl .\n    movs r5, r0\n    cmp r5, #0\n    bne L_open_cfw_runtime_am005_f1a4_0058\n    movs r0, #0\n    b L_open_cfw_runtime_am005_f1a4_0316\nL_open_cfw_runtime_am005_f1a4_0058:\n    movs r0, #0\n    movs r0, #0\n    ldrh r0, [r4, #0x2a]\n    ubfx r0, r0, #0xb, #1\n    uxth r0, r0\n    cmp r0, #0\n    beq L_open_cfw_runtime_am005_f1a4_0072\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am005_addr_0043fd9e\n    bl .\n    movs r7, r0\n    b L_open_cfw_runtime_am005_f1a4_0158\nL_open_cfw_runtime_am005_f1a4_0072:\n    movs r1, #0\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am005_addr_0043eea6\n    bl .\n    movs r7, r0\n    mvns r8, #0xc0000000\n    cmp r7, r8\n    bne L_open_cfw_runtime_am005_f1a4_008a\n    movs.w sb, #1\n    b L_open_cfw_runtime_am005_f1a4_008e\nL_open_cfw_runtime_am005_f1a4_008a:\n    movs.w sb, #0\nL_open_cfw_runtime_am005_f1a4_008e:\n    ands r0, r7, #0x60000000\n    cmp.w r0, #0x20000000\n    bne L_open_cfw_runtime_am005_f1a4_00aa\n    bics r0, r7, #0x60000000\n    mvns r1, #0xe0000000\n    cmp r0, r1\n    bge L_open_cfw_runtime_am005_f1a4_00aa\n    movs.w sl, #1\n    b L_open_cfw_runtime_am005_f1a4_00ae\nL_open_cfw_runtime_am005_f1a4_00aa:\n    movs.w sl, #0\nL_open_cfw_runtime_am005_f1a4_00ae:\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am005_addr_0043fe16\n    bl .\n    movs r6, r0\n    uxtb.w sb, sb\n    cmp.w sb, #0\n    beq L_open_cfw_runtime_am005_f1a4_00ca\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am005_addr_00440a3c\n    bl .\n    movs r7, r0\n    b L_open_cfw_runtime_am005_f1a4_0138\nL_open_cfw_runtime_am005_f1a4_00ca:\n    uxtb.w sl, sl\n    cmp.w sl, #0\n    beq L_open_cfw_runtime_am005_f1a4_0138\n    ldrh r0, [r5, #0x2a]\n    ubfx r0, r0, #0xb, #1\n    uxth r0, r0\n    cmp r0, #0\n    bne L_open_cfw_runtime_am005_f1a4_0102\n    movs r1, #0\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am005_addr_0043eea6\n    bl .\n    cmp r0, r8\n    bne L_open_cfw_runtime_am005_f1a4_0102\n    movs r1, #0\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am005_efc6\n    bl .\n    movs r7, r0\n    movs r1, #0\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am005_eff4\n    bl .\n    adds r7, r0, r7\n    b L_open_cfw_runtime_am005_f1a4_0138\nL_open_cfw_runtime_am005_f1a4_0102:\n    bics r0, r7, #0x60000000\n    cmp.w r0, #0x10000000\n    blt L_open_cfw_runtime_am005_f1a4_0118\n    mvns r0, #0xf0000000\n    bics r7, r7, #0x60000000\n    subs r7, r0, r7\n    b L_open_cfw_runtime_am005_f1a4_011c\nL_open_cfw_runtime_am005_f1a4_0118:\n    bics r7, r7, #0x60000000\nL_open_cfw_runtime_am005_f1a4_011c:\n    muls r7, r6, r7\n    movs r0, #0x64\n    sdiv r7, r7, r0\n    movs r1, #0\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am005_ef84\n    bl .\n    subs r7, r7, r0\n    movs r1, #0\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am005_ef8e\n    bl .\n    subs r7, r7, r0\nL_open_cfw_runtime_am005_f1a4_0138:\n    movs r1, #0\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am005_addr_0043eeb0\n    bl .\n    mov r8, r0\n    movs r1, #0\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am005_addr_0043eeba\n    bl .\n    movs r2, r0\n    movs r3, r6\n    mov r1, r8\n    movs r0, r7\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am005_addr_004408d6\n    bl .\n    movs r7, r0\nL_open_cfw_runtime_am005_f1a4_0158:\n    movs r0, #0\n    movs r0, #0\n    ldrh r0, [r4, #0x2a]\n    ubfx r0, r0, #0xa, #1\n    uxth r0, r0\n    cmp r0, #0\n    beq L_open_cfw_runtime_am005_f1a4_0172\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am005_addr_0043fdda\n    bl .\n    mov r8, r0\n    b L_open_cfw_runtime_am005_f1a4_025a\nL_open_cfw_runtime_am005_f1a4_0172:\n    movs r1, #0\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am005_addr_0043eec4\n    bl .\n    movs r6, r0\n    mvns sb, #0xc0000000\n    cmp r6, sb\n    bne L_open_cfw_runtime_am005_f1a4_018a\n    movs.w sl, #1\n    b L_open_cfw_runtime_am005_f1a4_018e\nL_open_cfw_runtime_am005_f1a4_018a:\n    movs.w sl, #0\nL_open_cfw_runtime_am005_f1a4_018e:\n    ands r0, r6, #0x60000000\n    cmp.w r0, #0x20000000\n    bne L_open_cfw_runtime_am005_f1a4_01aa\n    bics r0, r6, #0x60000000\n    mvns r1, #0xe0000000\n    cmp r0, r1\n    bge L_open_cfw_runtime_am005_f1a4_01aa\n    movs.w fp, #1\n    b L_open_cfw_runtime_am005_f1a4_01ae\nL_open_cfw_runtime_am005_f1a4_01aa:\n    movs.w fp, #0\nL_open_cfw_runtime_am005_f1a4_01ae:\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am005_addr_0043fe70\n    bl .\n    mov r8, r0\n    uxtb.w sl, sl\n    cmp.w sl, #0\n    beq L_open_cfw_runtime_am005_f1a4_01ca\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am005_addr_00440c2e\n    bl .\n    movs r6, r0\n    b L_open_cfw_runtime_am005_f1a4_023a\nL_open_cfw_runtime_am005_f1a4_01ca:\n    uxtb.w fp, fp\n    cmp.w fp, #0\n    beq L_open_cfw_runtime_am005_f1a4_023a\n    ldrh r0, [r5, #0x2a]\n    ubfx r0, r0, #0xa, #1\n    uxth r0, r0\n    cmp r0, #0\n    bne L_open_cfw_runtime_am005_f1a4_0202\n    movs r1, #0\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am005_addr_0043eec4\n    bl .\n    cmp r0, sb\n    bne L_open_cfw_runtime_am005_f1a4_0202\n    movs r1, #0\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am005_f022\n    bl .\n    movs r6, r0\n    movs r1, #0\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am005_f050\n    bl .\n    adds r6, r0, r6\n    b L_open_cfw_runtime_am005_f1a4_023a\nL_open_cfw_runtime_am005_f1a4_0202:\n    bics r0, r6, #0x60000000\n    cmp.w r0, #0x10000000\n    blt L_open_cfw_runtime_am005_f1a4_0218\n    mvns r0, #0xf0000000\n    bics r6, r6, #0x60000000\n    subs r6, r0, r6\n    b L_open_cfw_runtime_am005_f1a4_021c\nL_open_cfw_runtime_am005_f1a4_0218:\n    bics r6, r6, #0x60000000\nL_open_cfw_runtime_am005_f1a4_021c:\n    mul r6, r8, r6\n    movs r0, #0x64\n    sdiv r6, r6, r0\n    movs r1, #0\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am005_ef70\n    bl .\n    subs r6, r6, r0\n    movs r1, #0\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am005_ef7a\n    bl .\n    subs r6, r6, r0\nL_open_cfw_runtime_am005_f1a4_023a:\n    movs r1, #0\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am005_addr_0043eece\n    bl .\n    mov sb, r0\n    movs r1, #0\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am005_addr_0043eed8\n    bl .\n    mov r3, r8\n    movs r2, r0\n    mov r1, sb\n    movs r0, r6\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am005_addr_00440968\n    bl .\n    mov r8, r0\nL_open_cfw_runtime_am005_f1a4_025a:\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am005_addr_0043fd9e\n    bl .\n    cmp r0, r7\n    bne L_open_cfw_runtime_am005_f1a4_0272\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am005_addr_0043fdda\n    bl .\n    cmp r0, r8\n    bne L_open_cfw_runtime_am005_f1a4_0272\n    movs r0, #0\n    b L_open_cfw_runtime_am005_f1a4_0316\nL_open_cfw_runtime_am005_f1a4_0272:\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am005_addr_00440656\n    bl .\n    add r1, sp, #0x10\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am005_fc2a\n    bl .\n    mov r1, sp\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am005_addr_0043feca\n    bl .\n    movs r2, #0\n    mov r1, sp\n    add r0, sp, #0x10\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am005_addr_00450f28\n    bl .\n    movs r6, r0\n    movs r0, r6\n    uxtb r0, r0\n    cmp r0, #0\n    bne L_open_cfw_runtime_am005_f1a4_02a2\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am005_addr_0044f2ca\n    bl .\nL_open_cfw_runtime_am005_f1a4_02a2:\n    ldr r0, [r4, #0x18]\n    adds.w r8, r8, r0\n    subs.w r8, r8, #1\n    str.w r8, [r4, #0x20]\n    movs r1, #0\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am005_efba\n    bl .\n    cmp r0, #1\n    bne L_open_cfw_runtime_am005_f1a4_02c6\n    ldr r0, [r4, #0x1c]\n    subs r7, r0, r7\n    adds r7, r7, #1\n    str r7, [r4, #0x14]\n    b L_open_cfw_runtime_am005_f1a4_02ce\nL_open_cfw_runtime_am005_f1a4_02c6:\n    ldr r0, [r4, #0x14]\n    adds r7, r7, r0\n    subs r7, r7, #1\n    str r7, [r4, #0x1c]\nL_open_cfw_runtime_am005_f1a4_02ce:\n    add r2, sp, #0x10\n    movs r1, #0x31\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am005_addr_00451670\n    bl .\n    movs r2, r4\n    movs r1, #0x2a\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am005_addr_00451670\n    bl .\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am005_addr_00440656\n    bl .\n    ldrh r0, [r4, #0x2a]\n    orrs r0, r0, #2\n    strh r0, [r4, #0x2a]\n    movs r2, #0\n    mov r1, sp\n    adds.w r0, r4, #0x14\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am005_addr_00450f28\n    bl .\n    uxtb r6, r6\n    cmp r6, #0\n    bne L_open_cfw_runtime_am005_f1a4_0308\n    uxtb r0, r0\n    cmp r0, #0\n    beq L_open_cfw_runtime_am005_f1a4_030e\nL_open_cfw_runtime_am005_f1a4_0308:\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am005_addr_0044f2ca\n    bl .\nL_open_cfw_runtime_am005_f1a4_030e:\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am005_addr_00452d42\n    bl .\n    movs r0, #1\nL_open_cfw_runtime_am005_f1a4_0316:\n    add sp, #0x24\n    pop.w {r4, r5, r6, r7, r8, sb, sl, fp, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM005_F4C0_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am005_f4c0(void)
{
    __asm__ volatile(
        "    push {r1, r2, r3, r4, r5, lr}\n    movs r4, r0\n    movs r5, r2\n    cmp r4, #0\n    bne L_open_cfw_runtime_am005_f4c0_0036\n    ldr.w r0, [pc, #0x808]\n    str r0, [sp, #8]\n    ldr.w r0, [pc, #0x804]\n    str r0, [sp, #4]\n    ldr.w r0, [pc, #0x7f4]\n    str r0, [sp]\n    ldr.w r3, [pc, #0xa9c]\n    movs r2, #0xd7\n    ldr.w r1, [pc, #0x8ac]\n    movs r0, #3\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am005_addr_0044d25c\n    bl .\nL_open_cfw_runtime_am005_f4c0_002c:\n    movs r0, #0\n    movs.w r1, #-1\n    str r0, [r1]\n    b L_open_cfw_runtime_am005_f4c0_002c\nL_open_cfw_runtime_am005_f4c0_0036:\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am005_f506\n    bl .\n    movs r1, r5\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am005_f568\n    bl .\n    pop {r0, r1, r2, r4, r5, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM005_F506_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am005_f506(void)
{
    __asm__ volatile(
        "    push {r1, r2, r3, r4, r5, lr}\n    movs r4, r0\n    movs r5, r1\n    cmp r4, #0\n    bne L_open_cfw_runtime_am005_f506_0036\n    ldr.w r0, [pc, #0x7c0]\n    str r0, [sp, #8]\n    ldr.w r0, [pc, #0x7c0]\n    str r0, [sp, #4]\n    ldr.w r0, [pc, #0x7ac]\n    str r0, [sp]\n    ldr.w r3, [pc, #0xa5c]\n    movs r2, #0xdf\n    ldr.w r1, [pc, #0x864]\n    movs r0, #3\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am005_addr_0044d25c\n    bl .\nL_open_cfw_runtime_am005_f506_002c:\n    movs r0, #0\n    movs.w r1, #-1\n    str r0, [r1]\n    b L_open_cfw_runtime_am005_f506_002c\nL_open_cfw_runtime_am005_f506_0036:\n    movs r3, #0\n    mov r2, sp\n    movs r1, #1\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am005_addr_0044beaa\n    bl .\n    movs r1, r0\n    uxtb r1, r1\n    cmp r1, #1\n    bne L_open_cfw_runtime_am005_f506_0050\n    ldr r1, [sp]\n    cmp r1, r5\n    bne L_open_cfw_runtime_am005_f506_0056\nL_open_cfw_runtime_am005_f506_0050:\n    uxtb r0, r0\n    cmp r0, #0\n    bne L_open_cfw_runtime_am005_f506_0060\nL_open_cfw_runtime_am005_f506_0056:\n    movs r2, #0\n    movs r1, r5\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am005_addr_00441164\n    bl .\nL_open_cfw_runtime_am005_f506_0060:\n    pop {r0, r1, r2, r4, r5, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM005_F568_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am005_f568(void)
{
    __asm__ volatile(
        "    push {r1, r2, r3, r4, r5, lr}\n    movs r4, r0\n    movs r5, r1\n    cmp r4, #0\n    bne L_open_cfw_runtime_am005_f568_0036\n    ldr.w r0, [pc, #0x760]\n    str r0, [sp, #8]\n    ldr.w r0, [pc, #0x75c]\n    str r0, [sp, #4]\n    ldr.w r0, [pc, #0x74c]\n    str r0, [sp]\n    ldr.w r3, [pc, #0x9fc]\n    movs r2, #0xec\n    ldr.w r1, [pc, #0x804]\n    movs r0, #3\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am005_addr_0044d25c\n    bl .\nL_open_cfw_runtime_am005_f568_002c:\n    movs r0, #0\n    movs.w r1, #-1\n    str r0, [r1]\n    b L_open_cfw_runtime_am005_f568_002c\nL_open_cfw_runtime_am005_f568_0036:\n    movs r3, #0\n    mov r2, sp\n    movs r1, #2\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am005_addr_0044beaa\n    bl .\n    movs r1, r0\n    uxtb r1, r1\n    cmp r1, #1\n    bne L_open_cfw_runtime_am005_f568_0050\n    ldr r1, [sp]\n    cmp r1, r5\n    bne L_open_cfw_runtime_am005_f568_0056\nL_open_cfw_runtime_am005_f568_0050:\n    uxtb r0, r0\n    cmp r0, #0\n    bne L_open_cfw_runtime_am005_f568_0060\nL_open_cfw_runtime_am005_f568_0056:\n    movs r2, #0\n    movs r1, r5\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am005_addr_0044118e\n    bl .\nL_open_cfw_runtime_am005_f568_0060:\n    pop {r0, r1, r2, r4, r5, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM005_F5CA_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am005_f5ca(void)
{
    __asm__ volatile(
        "    push {r0, r1, r2, r3, r4, lr}\n    movs r4, r0\n    cmp r4, #0\n    bne L_open_cfw_runtime_am005_f5ca_0036\n    ldr.w r0, [pc, #0x700]\n    str r0, [sp, #8]\n    ldr.w r0, [pc, #0x6fc]\n    str r0, [sp, #4]\n    ldr.w r0, [pc, #0x6ec]\n    str r0, [sp]\n    ldr.w r3, [pc, #0x9a0]\n    movw r2, #0x107\n    ldr.w r1, [pc, #0x7a0]\n    movs r0, #3\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am005_addr_0044d25c\n    bl .\nL_open_cfw_runtime_am005_f5ca_002c:\n    movs r0, #0\n    movs.w r1, #-1\n    str r0, [r1]\n    b L_open_cfw_runtime_am005_f5ca_002c\nL_open_cfw_runtime_am005_f5ca_0036:\n    movs r2, #0\n    uxth r1, r1\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am005_addr_004414a6\n    bl .\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am005_f648\n    bl .\n    pop {r0, r1, r2, r3, r4, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM005_F612_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am005_f612(void)
{
    __asm__ volatile(
        "    push {r4, lr}\n    movs r4, r0\n    ldr.w r1, [pc, #0x974]\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am005_addr_0043e11c\n    bl .\n    cmp r0, #0\n    beq L_open_cfw_runtime_am005_f612_0016\n    movs r0, #0\n    b L_open_cfw_runtime_am005_f612_0034\nL_open_cfw_runtime_am005_f612_0016:\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am005_addr_0044dca2\n    bl .\n    cmp r0, #0\n    bne L_open_cfw_runtime_am005_f612_0024\n    movs r0, #0\n    b L_open_cfw_runtime_am005_f612_0034\nL_open_cfw_runtime_am005_f612_0024:\n    movs r1, #0\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am005_efae\n    bl .\n    cmp r0, #0\n    beq L_open_cfw_runtime_am005_f612_0032\n    movs r0, #1\n    b L_open_cfw_runtime_am005_f612_0034\nL_open_cfw_runtime_am005_f612_0032:\n    movs r0, #0\nL_open_cfw_runtime_am005_f612_0034:\n    pop {r4, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM005_F648_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am005_f648(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    ldrh r1, [r0, #0x2a]\n    orrs r1, r1, #1\n    strh r1, [r0, #0x2a]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am005_addr_0044dbc4\n    bl .\n    ldrh r1, [r0, #0x2a]\n    orrs r1, r1, #4\n    strh r1, [r0, #0x2a]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am005_addr_0044dc0a\n    bl .\n    movs r2, #0\n    movs r1, #0x38\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am005_addr_0044fdbe\n    bl .\n    pop {r0, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM005_F66C_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am005_f66c(void)
{
    __asm__ volatile(
        "    push {r3, r4, r5, lr}\n    ldr.w r4, [pc, #0x920]\n    ldrb.w r1, [r4, #0x60]\n    cmp r1, #0\n    bne L_open_cfw_runtime_am005_f66c_003e\n    movs r1, #1\n    strb.w r1, [r4, #0x60]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am005_addr_0044dbc4\n    bl .\n    movs r5, r0\n    b L_open_cfw_runtime_am005_f66c_002c\nL_open_cfw_runtime_am005_f66c_001c:\n    ldrh r1, [r5, #0x2a]\n    movw r0, #0xfffb\n    ands r1, r0\n    strh r1, [r5, #0x2a]\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am005_addr_00440d70\n    bl .\nL_open_cfw_runtime_am005_f66c_002c:\n    ldrh r0, [r5, #0x2a]\n    ubfx r0, r0, #2, #1\n    uxth r0, r0\n    cmp r0, #0\n    bne L_open_cfw_runtime_am005_f66c_001c\n    movs r0, #0\n    strb.w r0, [r4, #0x60]\nL_open_cfw_runtime_am005_f66c_003e:\n    pop {r0, r4, r5, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM005_F6AC_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am005_f6ac(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    movs r2, #0\n    uxtb r1, r1\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am005_addr_004411d4\n    bl .\n    pop {r0, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM005_F6B8_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am005_f6b8(void)
{
    __asm__ volatile(
        "    push {r4, r5, r6, lr}\n    movs r4, r0\n    movs r5, r2\n    movs r6, r3\n    movs r2, #0\n    uxtb r1, r1\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am005_addr_004411d4\n    bl .\n    movs r2, r6\n    movs r1, r5\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am005_f09a\n    bl .\n    pop {r4, r5, r6, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM005_F6D6_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am005_f6d6(void)
{
    __asm__ volatile(
        "    push.w {r2, r3, r4, r5, r6, r7, r8, sb, sl, fp, lr}\n    sub sp, #0xc\n    movs r6, r0\n    mov sb, r2\n    cmp r6, #0\n    bne L_open_cfw_runtime_am005_f6d6_003c\n    ldr.w r0, [pc, #0x57c]\n    str r0, [sp, #8]\n    ldr.w r0, [pc, #0x57c]\n    str r0, [sp, #4]\n    ldr.w r0, [pc, #0x5d8]\n    str r0, [sp]\n    ldr.w r3, [pc, #0x89c]\n    mov.w r2, #0x14a\n    ldr.w r1, [pc, #0x640]\n    movs r0, #3\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am005_addr_0044d25c\n    bl .\nL_open_cfw_runtime_am005_f6d6_0032:\n    movs r0, #0\n    movs.w r1, #-1\n    str r0, [r1]\n    b L_open_cfw_runtime_am005_f6d6_0032\nL_open_cfw_runtime_am005_f6d6_003c:\n    movs r4, r1\n    movs r0, r6\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am005_f66c\n    bl .\n    cmp r4, #0\n    bne L_open_cfw_runtime_am005_f6d6_0050\n    movs r0, r6\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am005_addr_0044dca2\n    bl .\n    movs r4, r0\nL_open_cfw_runtime_am005_f6d6_0050:\n    cmp r4, #0\n    bne L_open_cfw_runtime_am005_f6d6_0082\n    ldr.w r0, [pc, #0x538]\n    str r0, [sp, #8]\n    ldr.w r0, [pc, #0x864]\n    str r0, [sp, #4]\n    ldr.w r0, [pc, #0x594]\n    str r0, [sp]\n    ldr.w r3, [pc, #0x854]\n    movw r2, #0x14f\n    ldr.w r1, [pc, #0x5f8]\n    movs r0, #3\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am005_addr_0044d25c\n    bl .\nL_open_cfw_runtime_am005_f6d6_0078:\n    movs r0, #0\n    movs.w r1, #-1\n    str r0, [r1]\n    b L_open_cfw_runtime_am005_f6d6_0078\nL_open_cfw_runtime_am005_f6d6_0082:\n    movs.w r8, #0\n    movs r5, #0\n    movs r0, r6\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am005_addr_0044dca2\n    bl .\n    movs r7, r0\n    cmp r7, #0\n    bne L_open_cfw_runtime_am005_f6d6_00c2\n    ldr.w r0, [pc, #0x4f8]\n    str r0, [sp, #8]\n    ldr.w r0, [pc, #0x828]\n    str r0, [sp, #4]\n    ldr.w r0, [pc, #0x554]\n    str r0, [sp]\n    ldr.w r3, [pc, #0x814]\n    mov.w r2, #0x156\n    ldr.w r1, [pc, #0x5b8]\n    movs r0, #3\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am005_addr_0044d25c\n    bl .\nL_open_cfw_runtime_am005_f6d6_00b8:\n    movs r0, #0\n    movs.w r1, #-1\n    str r0, [r1]\n    b L_open_cfw_runtime_am005_f6d6_00b8\nL_open_cfw_runtime_am005_f6d6_00c2:\n    movs r1, #0\n    movs r0, r7\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am005_efc6\n    bl .\n    str r0, [sp]\n    movs r1, #0\n    movs r0, r7\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am005_f022\n    bl .\n    str r0, [sp, #4]\n    movs r1, #0\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am005_efc6\n    bl .\n    mov fp, r0\n    movs r1, #0\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am005_f022\n    bl .\n    mov sl, r0\n    mov r0, sb\n    uxtb r0, r0\n    cmp r0, #0\n    bne L_open_cfw_runtime_am005_f6d6_0108\n    movs r1, #0\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am005_efba\n    bl .\n    cmp r0, #1\n    bne L_open_cfw_runtime_am005_f6d6_0104\n    movs.w sb, #3\n    b L_open_cfw_runtime_am005_f6d6_0108\nL_open_cfw_runtime_am005_f6d6_0104:\n    movs.w sb, #1\nL_open_cfw_runtime_am005_f6d6_0108:\n    uxtb.w sb, sb\n    cmp.w sb, #0\n    beq.w #0x43fb16\n    cmp.w sb, #2\n    beq L_open_cfw_runtime_am005_f6d6_01d6\n    blo L_open_cfw_runtime_am005_f6d6_01d0\n    cmp.w sb, #4\n    beq L_open_cfw_runtime_am005_f6d6_0214\n    blo L_open_cfw_runtime_am005_f6d6_01fa\n    cmp.w sb, #6\n    beq.w #0x43f940\n    blo.w #0x43f906\n    cmp.w sb, #8\n    beq.w #0x43f996\n    blo.w #0x43f970\n    cmp.w sb, #0xa\n    beq.w #0x43f9d0\n    blo L_open_cfw_runtime_am005_f6d6_018c\n    cmp.w sb, #0xc\n    beq.w #0x43fa08\n    blo.w #0x43f9e0\n    cmp.w sb, #0xe\n    beq.w #0x43fa34\n    blo.w #0x43fa26\n    cmp.w sb, #0x10\n    beq.w #0x43fa76\n    blo.w #0x43fa5a\n    cmp.w sb, #0x12\n    beq.w #0x43faae\n    blo.w #0x43fa86\n    cmp.w sb, #0x14\n    beq.w #0x43fad8\n    blo.w #0x43facc\n    cmp.w sb, #0x15\n    beq.w #0x43fafc\n    b L_open_cfw_runtime_am005_f6d6_0440\nL_open_cfw_runtime_am005_f6d6_018c:\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am005_addr_0043fe16\n    bl .\n    movs r1, #2\n    sdiv r5, r0, r1\n    movs r0, r6\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am005_addr_0043fd9e\n    bl .\n    movs r1, #2\n    sdiv r0, r0, r1\n    subs r5, r5, r0\n    mov r8, fp\n    adds.w r8, r8, r5\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am005_addr_0043fe70\n    bl .\n    movs r1, #2\n    sdiv sb, r0, r1\n    movs r0, r6\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am005_addr_0043fdda\n    bl .\n    movs r1, #2\n    sdiv r0, r0, r1\n    subs.w sb, sb, r0\n    mov r5, sl\n    adds.w r5, r5, sb\n    b L_open_cfw_runtime_am005_f6d6_0440\nL_open_cfw_runtime_am005_f6d6_01d0:\n    mov r8, fp\n    mov r5, sl\n    b L_open_cfw_runtime_am005_f6d6_0440\nL_open_cfw_runtime_am005_f6d6_01d6:\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am005_addr_0043fe16\n    bl .\n    movs r1, #2\n    sdiv r5, r0, r1\n    movs r0, r6\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am005_addr_0043fd9e\n    bl .\n    movs r1, #2\n    sdiv r0, r0, r1\n    subs r5, r5, r0\n    mov r8, fp\n    adds.w r8, r8, r5\n    mov r5, sl\n    b L_open_cfw_runtime_am005_f6d6_0440\nL_open_cfw_runtime_am005_f6d6_01fa:\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am005_addr_0043fe16\n    bl .\n    movs r5, r0\n    movs r0, r6\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am005_addr_0043fd9e\n    bl .\n    subs r5, r5, r0\n    mov r8, fp\n    adds.w r8, r8, r5\n    mov r5, sl\n    b L_open_cfw_runtime_am005_f6d6_0440\nL_open_cfw_runtime_am005_f6d6_0214:\n    mov r8, fp\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am005_addr_0043fe70\n    bl .\n    mov sb, r0\n    movs r0, r6\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am005_addr_0043fdda\n    bl .\n    subs.w sb, sb, r0\n    mov r5, sl\n    adds.w r5, r5, sb\n    b L_open_cfw_runtime_am005_f6d6_0440\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am005_addr_0043fe16\n    bl .\n    movs r1, #2\n    sdiv r5, r0, r1\n    movs r0, r6\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am005_addr_0043fd9e\n    bl .\n    movs r1, #2\n    sdiv r0, r0, r1\n    subs r5, r5, r0\n    mov r8, fp\n    adds.w r8, r8, r5\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am005_addr_0043fe70\n    bl .\n    mov sb, r0\n    movs r0, r6\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am005_addr_0043fdda\n    bl .\n    subs.w sb, sb, r0\n    mov r5, sl\n    adds.w r5, r5, sb\n    b L_open_cfw_runtime_am005_f6d6_0440\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am005_addr_0043fe16\n    bl .\n    movs r5, r0\n    movs r0, r6\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am005_addr_0043fd9e\n    bl .\n    subs r5, r5, r0\n    mov r8, fp\n    adds.w r8, r8, r5\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am005_addr_0043fe70\n    bl .\n    mov sb, r0\n    movs r0, r6\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am005_addr_0043fdda\n    bl .\n    subs.w sb, sb, r0\n    mov r5, sl\n    adds.w r5, r5, sb\n    b L_open_cfw_runtime_am005_f6d6_0440\n    mov r8, fp\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am005_addr_0043fe70\n    bl .\n    movs r1, #2\n    sdiv sb, r0, r1\n    movs r0, r6\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am005_addr_0043fdda\n    bl .\n    movs r1, #2\n    sdiv r0, r0, r1\n    subs.w sb, sb, r0\n    mov r5, sl\n    adds.w r5, r5, sb\n    b L_open_cfw_runtime_am005_f6d6_0440\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am005_addr_0043fe16\n    bl .\n    movs r5, r0\n    movs r0, r6\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am005_addr_0043fd9e\n    bl .\n    subs r5, r5, r0\n    mov r8, fp\n    adds.w r8, r8, r5\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am005_addr_0043fe70\n    bl .\n    movs r1, #2\n    sdiv sb, r0, r1\n    movs r0, r6\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am005_addr_0043fdda\n    bl .\n    movs r1, #2\n    sdiv r0, r0, r1\n    subs.w sb, sb, r0\n    mov r5, sl\n    adds.w r5, r5, sb\n    b L_open_cfw_runtime_am005_f6d6_0440\n    movs.w r8, #0\n    movs r0, r6\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am005_addr_0043fdda\n    bl .\n    movs r5, r0\n    rsbs r5, r5, #0\n    b L_open_cfw_runtime_am005_f6d6_0440\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am005_addr_0043fd9e\n    bl .\n    movs r1, #2\n    sdiv r8, r0, r1\n    movs r0, r6\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am005_addr_0043fd9e\n    bl .\n    movs r1, #2\n    sdiv r0, r0, r1\n    subs.w r8, r8, r0\n    movs r0, r6\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am005_addr_0043fdda\n    bl .\n    movs r5, r0\n    rsbs r5, r5, #0\n    b L_open_cfw_runtime_am005_f6d6_0440\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am005_addr_0043fd9e\n    bl .\n    mov r8, r0\n    movs r0, r6\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am005_addr_0043fd9e\n    bl .\n    subs.w r8, r8, r0\n    movs r0, r6\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am005_addr_0043fdda\n    bl .\n    movs r5, r0\n    rsbs r5, r5, #0\n    b L_open_cfw_runtime_am005_f6d6_0440\n    movs.w r8, #0\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am005_addr_0043fdda\n    bl .\n    movs r5, r0\n    b L_open_cfw_runtime_am005_f6d6_0440\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am005_addr_0043fd9e\n    bl .\n    movs r1, #2\n    sdiv r8, r0, r1\n    movs r0, r6\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am005_addr_0043fd9e\n    bl .\n    movs r1, #2\n    sdiv r0, r0, r1\n    subs.w r8, r8, r0\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am005_addr_0043fdda\n    bl .\n    movs r5, r0\n    b L_open_cfw_runtime_am005_f6d6_0440\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am005_addr_0043fd9e\n    bl .\n    mov r8, r0\n    movs r0, r6\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am005_addr_0043fd9e\n    bl .\n    subs.w r8, r8, r0\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am005_addr_0043fdda\n    bl .\n    movs r5, r0\n    b L_open_cfw_runtime_am005_f6d6_0440\n    movs r0, r6\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am005_addr_0043fd9e\n    bl .\n    mov r8, r0\n    rsbs.w r8, r8, #0\n    movs r5, #0\n    b L_open_cfw_runtime_am005_f6d6_0440\n    movs r0, r6\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am005_addr_0043fd9e\n    bl .\n    mov r8, r0\n    rsbs.w r8, r8, #0\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am005_addr_0043fdda\n    bl .\n    movs r1, #2\n    sdiv r5, r0, r1\n    movs r0, r6\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am005_addr_0043fdda\n    bl .\n    movs r1, #2\n    sdiv r0, r0, r1\n    subs r5, r5, r0\n    b L_open_cfw_runtime_am005_f6d6_0440\n    movs r0, r6\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am005_addr_0043fd9e\n    bl .\n    mov r8, r0\n    rsbs.w r8, r8, #0\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am005_addr_0043fdda\n    bl .\n    movs r5, r0\n    movs r0, r6\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am005_addr_0043fdda\n    bl .\n    subs r5, r5, r0\n    b L_open_cfw_runtime_am005_f6d6_0440\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am005_addr_0043fd9e\n    bl .\n    mov r8, r0\n    movs r5, #0\n    b L_open_cfw_runtime_am005_f6d6_0440\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am005_addr_0043fd9e\n    bl .\n    mov r8, r0\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am005_addr_0043fdda\n    bl .\n    movs r1, #2\n    sdiv r5, r0, r1\n    movs r0, r6\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am005_addr_0043fdda\n    bl .\n    movs r1, #2\n    sdiv r0, r0, r1\n    subs r5, r5, r0\n    b L_open_cfw_runtime_am005_f6d6_0440\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am005_addr_0043fd9e\n    bl .\n    mov r8, r0\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am005_addr_0043fdda\n    bl .\n    movs r5, r0\n    movs r0, r6\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am005_addr_0043fdda\n    bl .\n    subs r5, r5, r0\n    b L_open_cfw_runtime_am005_f6d6_0440\nL_open_cfw_runtime_am005_f6d6_0440:\n    ldr.w sb, [sp, #0x10]\n    ands r0, sb, #0x60000000\n    cmp.w r0, #0x20000000\n    bne L_open_cfw_runtime_am005_f6d6_0486\n    bics r0, sb, #0x60000000\n    mvns r1, #0xe0000000\n    cmp r0, r1\n    bge L_open_cfw_runtime_am005_f6d6_0486\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am005_addr_0043fd9e\n    bl .\n    bics r1, sb, #0x60000000\n    cmp.w r1, #0x10000000\n    blt L_open_cfw_runtime_am005_f6d6_0478\n    mvns r1, #0xf0000000\n    bics sb, sb, #0x60000000\n    subs.w sb, r1, sb\n    b L_open_cfw_runtime_am005_f6d6_047c\nL_open_cfw_runtime_am005_f6d6_0478:\n    bics sb, sb, #0x60000000\nL_open_cfw_runtime_am005_f6d6_047c:\n    mul r0, sb, r0\n    movs r1, #0x64\n    sdiv sb, r0, r1\nL_open_cfw_runtime_am005_f6d6_0486:\n    ldr.w sl, [sp, #0x38]\n    ands r0, sl, #0x60000000\n    cmp.w r0, #0x20000000\n    bne L_open_cfw_runtime_am005_f6d6_04cc\n    bics r0, sl, #0x60000000\n    mvns r1, #0xe0000000\n    cmp r0, r1\n    bge L_open_cfw_runtime_am005_f6d6_04cc\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am005_addr_0043fdda\n    bl .\n    bics r1, sl, #0x60000000\n    cmp.w r1, #0x10000000\n    blt L_open_cfw_runtime_am005_f6d6_04be\n    mvns r1, #0xf0000000\n    bics sl, sl, #0x60000000\n    subs.w sl, r1, sl\n    b L_open_cfw_runtime_am005_f6d6_04c2\nL_open_cfw_runtime_am005_f6d6_04be:\n    bics sl, sl, #0x60000000\nL_open_cfw_runtime_am005_f6d6_04c2:\n    mul r0, sl, r0\n    movs r1, #0x64\n    sdiv sl, r0, r1\nL_open_cfw_runtime_am005_f6d6_04cc:\n    movs r1, #0\n    movs r0, r7\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am005_efba\n    bl .\n    cmp r0, #1\n    bne L_open_cfw_runtime_am005_f6d6_04fa\n    movs r0, r7\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am005_addr_0044e67a\n    bl .\n    adds.w sb, sb, r8\n    ldr r1, [r4, #0x14]\n    adds.w sb, r1, sb\n    ldr r1, [r7, #0x14]\n    subs.w sb, sb, r1\n    adds.w sb, r0, sb\n    ldr r0, [sp]\n    subs.w sb, sb, r0\n    b L_open_cfw_runtime_am005_f6d6_051a\nL_open_cfw_runtime_am005_f6d6_04fa:\n    movs r0, r7\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am005_addr_0044e586\n    bl .\n    adds.w sb, sb, r8\n    ldr r1, [r4, #0x14]\n    adds.w sb, r1, sb\n    ldr r1, [r7, #0x14]\n    subs.w sb, sb, r1\n    adds.w sb, r0, sb\n    ldr r0, [sp]\n    subs.w sb, sb, r0\nL_open_cfw_runtime_am005_f6d6_051a:\n    movs r0, r7\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am005_addr_0044e4aa\n    bl .\n    adds.w sl, sl, r5\n    ldr r1, [r4, #0x18]\n    adds.w sl, r1, sl\n    ldr r1, [r7, #0x18]\n    subs.w sl, sl, r1\n    adds.w sl, r0, sl\n    ldr r0, [sp, #4]\n    subs.w sl, sl, r0\n    movs r2, #0\n    movs r1, #1\n    movs r0, r6\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am005_addr_004411d4\n    bl .\n    mov r2, sl\n    mov r1, sb\n    movs r0, r6\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am005_f09a\n    bl .\n    add sp, #0x14\n    pop.w {r4, r5, r6, r7, r8, sb, sl, fp, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM005_FC2A_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am005_fc2a(void)
{
    __asm__ volatile(
        "    push {r5, r6, r7, lr}\n    movs r2, r1\n    cmp r0, #0\n    bne L_open_cfw_runtime_am005_fc2a_002e\n    ldr r0, [pc, #0xa0]\n    str r0, [sp, #8]\n    ldr r0, [pc, #0xa0]\n    str r0, [sp, #4]\n    ldr r0, [pc, #0x90]\n    str r0, [sp]\n    ldr.w r3, [pc, #0xa7c]\n    mov.w r2, #0x1e0\n    ldr r1, [pc, #0x148]\n    movs r0, #3\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am005_addr_0044d25c\n    bl .\nL_open_cfw_runtime_am005_fc2a_0024:\n    movs r0, #0\n    movs.w r1, #-1\n    str r0, [r1]\n    b L_open_cfw_runtime_am005_fc2a_0024\nL_open_cfw_runtime_am005_fc2a_002e:\n    adds.w r1, r0, #0x14\n    movs r0, r2\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am005_addr_0043ee94\n    bl .\n    pop {r0, r1, r2, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM005_FC70_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am005_fc70(void)
{
    __asm__ volatile(
        "    push {r1, r2, r3, r4, r5, lr}\n    movs r5, r0\n    cmp r5, #0\n    bne L_open_cfw_runtime_am005_fc70_002e\n    ldr r0, [pc, #0x58]\n    str r0, [sp, #8]\n    ldr r0, [pc, #0x58]\n    str r0, [sp, #4]\n    ldr r0, [pc, #0x48]\n    str r0, [sp]\n    ldr.w r3, [pc, #0xa38]\n    movw r2, #0x1e7\n    ldr r1, [pc, #0x100]\n    movs r0, #3\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am005_addr_0044d25c\n    bl .\nL_open_cfw_runtime_am005_fc70_0024:\n    movs r0, #0\n    movs.w r1, #-1\n    str r0, [r1]\n    b L_open_cfw_runtime_am005_fc70_0024\nL_open_cfw_runtime_am005_fc70_002e:\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am005_addr_0044dca2\n    bl .\n    movs r4, r0\n    cmp r4, #0\n    beq L_open_cfw_runtime_am005_fc70_0054\n    ldr r5, [r5, #0x14]\n    ldr r0, [r4, #0x14]\n    subs r5, r5, r0\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am005_addr_0044e486\n    bl .\n    adds r5, r0, r5\n    movs r1, #0\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am005_efc6\n    bl .\n    subs r5, r5, r0\n    b L_open_cfw_runtime_am005_fc70_0056\nL_open_cfw_runtime_am005_fc70_0054:\n    ldr r5, [r5, #0x14]\nL_open_cfw_runtime_am005_fc70_0056:\n    movs r0, r5\n    pop {r1, r2, r3, r4, r5, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM005_FCE0_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am005_fce0(void)
{
    __asm__ volatile(
        "    push {r1, r2, r3, r4, r5, lr}\n    movs r5, r0\n    cmp r5, #0\n    bne L_open_cfw_runtime_am005_fce0_0034\n    ldr.w r0, [pc, #0xb5c]\n    str r0, [sp, #8]\n    ldr.w r0, [pc, #0xb5c]\n    str r0, [sp, #4]\n    ldr.w r0, [pc, #0xb58]\n    str r0, [sp]\n    ldr.w r3, [pc, #0xb9c]\n    movw r2, #0x1ff\n    ldr r1, [pc, #0x8c]\n    movs r0, #3\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am005_addr_0044d25c\n    bl .\nL_open_cfw_runtime_am005_fce0_002a:\n    movs r0, #0\n    movs.w r1, #-1\n    str r0, [r1]\n    b L_open_cfw_runtime_am005_fce0_002a\nL_open_cfw_runtime_am005_fce0_0034:\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am005_addr_0044dca2\n    bl .\n    movs r4, r0\n    cmp r4, #0\n    beq L_open_cfw_runtime_am005_fce0_005a\n    ldr r5, [r5, #0x18]\n    ldr r0, [r4, #0x18]\n    subs r5, r5, r0\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am005_addr_0044e498\n    bl .\n    adds r5, r0, r5\n    movs r1, #0\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am005_f022\n    bl .\n    subs r5, r5, r0\n    b L_open_cfw_runtime_am005_fce0_005c\nL_open_cfw_runtime_am005_fce0_005a:\n    ldr r5, [r5, #0x18]\nL_open_cfw_runtime_am005_fce0_005c:\n    movs r0, r5\n    pop {r1, r2, r3, r4, r5, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM005_FD44_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am005_fd44(void)
{
    __asm__ volatile(
        "    push {r1, r2, r3, r4, r5, lr}\n    movs r4, r0\n    cmp r4, #0\n    bne L_open_cfw_runtime_am005_fd44_0034\n    ldr.w r0, [pc, #0xaf8]\n    str r0, [sp, #8]\n    ldr.w r0, [pc, #0xaf8]\n    str r0, [sp, #4]\n    ldr.w r0, [pc, #0xaf4]\n    str r0, [sp]\n    ldr.w r3, [pc, #0xb3c]\n    mov.w r2, #0x210\n    ldr r1, [pc, #0x28]\n    movs r0, #3\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am005_addr_0044d25c\n    bl .\nL_open_cfw_runtime_am005_fd44_002a:\n    movs r0, #0\n    movs.w r1, #-1\n    str r0, [r1]\n    b L_open_cfw_runtime_am005_fd44_002a\nL_open_cfw_runtime_am005_fd44_0034:\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am005_fce0\n    bl .\n    movs r5, r0\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am005_addr_0043fdda\n    bl .\n    adds r5, r0, r5\n    movs r0, r5\n    pop {r1, r2, r3, r4, r5, pc}\n"
    );
}
#endif
