/*
 * SPDX-License-Identifier: MIT
 *
 * Source-owned exact helpers from the AM-059 retained island.
 */

#if defined(OPEN_CFW_AM059_CA80A_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am059_ca80a(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am059_addr_00474cd2\n    bl .\n    pop {r1, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM059_CA812_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am059_ca812(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am059_addr_00474d16\n    bl .\n    pop {r0, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM059_CA81A_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am059_ca81a(void)
{
    __asm__ volatile(
        "    movs.w r0, #-1\n    str r0, [r1]\n    bx lr\n"
    );
}
#endif

#if defined(OPEN_CFW_AM059_CA822_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am059_ca822(void)
{
    __asm__ volatile(
        "    push {r3, r4, r5, lr}\n    movs r4, r1\n    ldr r0, [r0, #0x68]\n    ldr r1, [r0, #0x28]\n    movs r2, #0xff\n    ldr r5, [r4, #0xc]\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am059_addr_0043c0e4\n    bl .\n    movs.w r0, #-1\n    str r0, [r4]\n    pop {r0, r4, r5, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM059_CA83C_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am059_ca83c(void)
{
    __asm__ volatile(
        "    push.w {r1, r2, r3, r4, r5, r6, r7, r8, sb, sl, fp, lr}\n    movs r6, r0\n    ldr.w sb, [sp, #0x34]\n    ldr.w r8, [sp, #0x38]\n    ldr r5, [sp, #0x3c]\n    ldr r0, [r6, #0x68]\n    ldr r0, [r0, #0x1c]\n    adds.w r4, r5, sb\n    cmp r0, r4\n    blo L_open_cfw_runtime_am059_ca83c_0030\n    movs r4, r1\n    movs r7, r2\n    str r3, [sp, #4]\n    ldr r0, [r6, #0x6c]\n    cmp r0, #0\n    beq L_open_cfw_runtime_am059_ca83c_0064\n    ldr r0, [sp, #0x30]\n    ldr r1, [r6, #0x6c]\n    cmp r0, r1\n    blo L_open_cfw_runtime_am059_ca83c_0064\nL_open_cfw_runtime_am059_ca83c_0030:\n    mvns r0, #0x53\n    b L_open_cfw_runtime_am059_ca83c_01c4\nL_open_cfw_runtime_am059_ca83c_0036:\n    ldr r1, [r4, #8]\n    subs.w r1, r1, sb\n    ldr r2, [r4, #4]\n    adds r1, r2, r1\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am059_addr_004ca700\n    bl .\n    mov sl, r0\n    mov r2, sl\n    ldr r0, [r4, #0xc]\n    ldr r1, [r4, #4]\n    subs.w r1, sb, r1\n    add r1, r0\n    mov fp, r8\n    mov r0, fp\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am059_addr_00439be4\n    bl .\n    add r8, sl\n    adds.w sb, sl, sb\n    subs.w r5, r5, sl\nL_open_cfw_runtime_am059_ca83c_0064:\n    cmp r5, #0\n    beq.w #0x4ca9fe\n    movs r0, r5\n    cmp r4, #0\n    beq L_open_cfw_runtime_am059_ca83c_0092\n    ldr r1, [sp, #0x30]\n    ldr r2, [r4]\n    cmp r1, r2\n    bne L_open_cfw_runtime_am059_ca83c_0092\n    ldr r2, [r4, #4]\n    ldr r1, [r4, #8]\n    adds r2, r1, r2\n    cmp sb, r2\n    bhs L_open_cfw_runtime_am059_ca83c_0092\n    ldr r1, [r4, #4]\n    cmp sb, r1\n    bhs L_open_cfw_runtime_am059_ca83c_0036\n    ldr r1, [r4, #4]\n    subs.w r1, r1, sb\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am059_addr_004ca700\n    bl .\nL_open_cfw_runtime_am059_ca83c_0092:\n    ldr r1, [sp, #0x30]\n    ldr r2, [r7]\n    cmp r1, r2\n    bne L_open_cfw_runtime_am059_ca83c_00e4\n    ldr r2, [r7, #4]\n    ldr r1, [r7, #8]\n    adds r2, r1, r2\n    cmp sb, r2\n    bhs L_open_cfw_runtime_am059_ca83c_00e4\n    ldr r1, [r7, #4]\n    cmp sb, r1\n    blo L_open_cfw_runtime_am059_ca83c_00da\n    ldr r1, [r7, #8]\n    subs.w r1, r1, sb\n    ldr r2, [r7, #4]\n    adds r1, r2, r1\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am059_addr_004ca700\n    bl .\n    mov sl, r0\n    mov r2, sl\n    ldr r0, [r7, #0xc]\n    ldr r1, [r7, #4]\n    subs.w r1, sb, r1\n    add r1, r0\n    mov fp, r8\n    mov r0, fp\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am059_addr_00439be4\n    bl .\n    add r8, sl\n    adds.w sb, sl, sb\n    subs.w r5, r5, sl\n    b L_open_cfw_runtime_am059_ca83c_0064\nL_open_cfw_runtime_am059_ca83c_00da:\n    ldr r1, [r7, #4]\n    subs.w r1, r1, sb\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am059_addr_004ca700\n    bl .\nL_open_cfw_runtime_am059_ca83c_00e4:\n    ldr r1, [sp, #4]\n    cmp r5, r1\n    blo L_open_cfw_runtime_am059_ca83c_0132\n    ldr r1, [r6, #0x68]\n    ldr r1, [r1, #0x14]\n    udiv r2, sb, r1\n    mls r1, r1, r2, sb\n    cmp r1, #0\n    bne L_open_cfw_runtime_am059_ca83c_0132\n    ldr r1, [r6, #0x68]\n    ldr r1, [r1, #0x14]\n    cmp r5, r1\n    blo L_open_cfw_runtime_am059_ca83c_0132\n    ldr r1, [r6, #0x68]\n    ldr r1, [r1, #0x14]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am059_addr_004ca708\n    bl .\n    mov sl, r0\n    str.w sl, [sp]\n    mov r3, r8\n    mov r2, sb\n    ldr r1, [sp, #0x30]\n    ldr r0, [r6, #0x68]\n    ldr.w ip, [r6, #0x68]\n    ldr.w ip, [ip, #4]\n    blx ip\n    cmp r0, #0\n    bne L_open_cfw_runtime_am059_ca83c_01c4\n    add r8, sl\n    adds.w sb, sl, sb\n    subs.w r5, r5, sl\n    b L_open_cfw_runtime_am059_ca83c_0064\nL_open_cfw_runtime_am059_ca83c_0132:\n    ldr r0, [r6, #0x6c]\n    cmp r0, #0\n    beq L_open_cfw_runtime_am059_ca83c_0152\n    ldr r0, [sp, #0x30]\n    ldr r1, [r6, #0x6c]\n    cmp r0, r1\n    blo L_open_cfw_runtime_am059_ca83c_0152\n    movs r2, #0x6b\n    ldr.w r1, [pc, #0xc14]\n    ldr.w r0, [pc, #0xc14]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am059_addr_004d09b4\n    bl .\n    nop.w\nL_open_cfw_runtime_am059_ca83c_0152:\n    ldr r0, [sp, #0x30]\n    str r0, [r7]\n    ldr r0, [r6, #0x68]\n    ldr r1, [r0, #0x14]\n    mov r0, sb\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am059_addr_004ca708\n    bl .\n    str r0, [r7, #4]\n    ldr r0, [r6, #0x68]\n    ldr r1, [r0, #0x14]\n    ldr r0, [sp, #4]\n    adds.w r0, r0, sb\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am059_addr_004ca714\n    bl .\n    ldr r1, [r6, #0x68]\n    ldr r1, [r1, #0x1c]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am059_addr_004ca700\n    bl .\n    ldr r1, [r6, #0x68]\n    ldr r1, [r1, #0x28]\n    ldr r2, [r7, #4]\n    subs r0, r0, r2\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am059_addr_004ca700\n    bl .\n    str r0, [r7, #8]\n    ldr r0, [r7, #8]\n    str r0, [sp]\n    ldr r3, [r7, #0xc]\n    ldr r2, [r7, #4]\n    ldr r1, [r7]\n    ldr r0, [r6, #0x68]\n    ldr.w ip, [r6, #0x68]\n    ldr.w ip, [ip, #4]\n    blx ip\n    mov sl, r0\n    cmp.w sl, #1\n    blt L_open_cfw_runtime_am059_ca83c_01b6\n    movs r2, #0x76\n    ldr.w r1, [pc, #0xbb0]\n    ldr.w r0, [pc, #0xbb4]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am059_addr_004d09b4\n    bl .\n    nop.w\nL_open_cfw_runtime_am059_ca83c_01b6:\n    cmp.w sl, #0\n    beq.w #0x4ca8a0\n    mov r0, sl\n    b L_open_cfw_runtime_am059_ca83c_01c4\n    movs r0, #0\nL_open_cfw_runtime_am059_ca83c_01c4:\n    pop.w {r1, r2, r3, r4, r5, r6, r7, r8, sb, sl, fp, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM059_CAA04_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am059_caa04(void)
{
    __asm__ volatile(
        "    push.w {r4, r5, r6, r7, r8, sb, sl, fp, lr}\n    sub sp, #0x1c\n    movs r4, r0\n    movs r5, r1\n    movs r6, r2\n    movs r7, r3\n    ldr.w r8, [sp, #0x44]\n    ldr.w sb, [sp, #0x4c]\n    ldr r0, [sp, #0x48]\n    str r0, [sp, #0x10]\n    movs r0, #0\n    movs.w sl, #0\n    b L_open_cfw_runtime_am059_caa04_003a\nL_open_cfw_runtime_am059_caa04_0022:\n    mov r2, fp\n    ldr r0, [sp, #0x10]\n    add.w r1, r0, sl\n    add r0, sp, #0x14\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am059_addr_004751c8\n    bl .\n    cmp r0, #0\n    bne L_open_cfw_runtime_am059_caa04_0070\n    adds.w fp, fp, sl\n    mov sl, fp\nL_open_cfw_runtime_am059_caa04_003a:\n    cmp sl, sb\n    bhs L_open_cfw_runtime_am059_caa04_007c\n    movs r1, #8\n    subs.w r0, sb, sl\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am059_addr_004ca700\n    bl .\n    mov fp, r0\n    str.w fp, [sp, #0xc]\n    add r0, sp, #0x14\n    str r0, [sp, #8]\n    adds.w r0, sl, r8\n    str r0, [sp, #4]\n    ldr r0, [sp, #0x40]\n    str r0, [sp]\n    subs.w r3, r7, sl\n    movs r2, r6\n    movs r1, r5\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am059_ca83c\n    bl .\n    cmp r0, #0\n    beq L_open_cfw_runtime_am059_caa04_0022\n    b L_open_cfw_runtime_am059_caa04_007e\nL_open_cfw_runtime_am059_caa04_0070:\n    cmp r0, #0\n    bpl L_open_cfw_runtime_am059_caa04_0078\n    movs r0, #1\n    b L_open_cfw_runtime_am059_caa04_007a\nL_open_cfw_runtime_am059_caa04_0078:\n    movs r0, #2\nL_open_cfw_runtime_am059_caa04_007a:\n    b L_open_cfw_runtime_am059_caa04_007e\nL_open_cfw_runtime_am059_caa04_007c:\n    movs r0, #0\nL_open_cfw_runtime_am059_caa04_007e:\n    add sp, #0x1c\n    pop.w {r4, r5, r6, r7, r8, sb, sl, fp, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM059_CAA88_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am059_caa88(void)
{
    __asm__ volatile(
        "    push.w {r0, r4, r5, r6, r7, r8, sb, sl, fp, lr}\n    sub sp, #0x18\n    movs r4, r1\n    movs r5, r2\n    movs r6, r3\n    ldr r7, [sp, #0x44]\n    ldr.w r8, [sp, #0x48]\n    ldr.w sb, [sp, #0x4c]\n    movs r0, #0\n    movs.w sl, #0\n    b L_open_cfw_runtime_am059_caa88_0034\nL_open_cfw_runtime_am059_caa88_001e:\n    mov r2, fp\n    add r1, sp, #0x10\n    ldr.w r0, [sb]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am059_addr_00541af8\n    bl .\n    str.w r0, [sb]\n    adds.w fp, fp, sl\n    mov sl, fp\nL_open_cfw_runtime_am059_caa88_0034:\n    cmp sl, r8\n    bhs L_open_cfw_runtime_am059_caa88_006a\n    movs r1, #8\n    subs.w r0, r8, sl\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am059_addr_004ca700\n    bl .\n    mov fp, r0\n    str.w fp, [sp, #0xc]\n    add r0, sp, #0x10\n    str r0, [sp, #8]\n    adds.w r0, sl, r7\n    str r0, [sp, #4]\n    ldr r0, [sp, #0x40]\n    str r0, [sp]\n    subs.w r3, r6, sl\n    movs r2, r5\n    movs r1, r4\n    ldr r0, [sp, #0x18]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am059_ca83c\n    bl .\n    cmp r0, #0\n    beq L_open_cfw_runtime_am059_caa88_001e\n    b L_open_cfw_runtime_am059_caa88_006c\nL_open_cfw_runtime_am059_caa88_006a:\n    movs r0, #0\nL_open_cfw_runtime_am059_caa88_006c:\n    add sp, #0x1c\n    pop.w {r4, r5, r6, r7, r8, sb, sl, fp, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM059_CAAFA_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am059_caafa(void)
{
    __asm__ volatile(
        "    push.w {r3, r4, r5, r6, r7, r8, sb, lr}\n    sub sp, #0x10\n    movs r6, r1\n    movs r7, r2\n    mov r8, r3\n    ldr r1, [r6]\n    cmn.w r1, #1\n    beq L_open_cfw_runtime_am059_caafa_00ba\n    ldr r1, [r6]\n    cmn.w r1, #2\n    beq L_open_cfw_runtime_am059_caafa_00ba\n    movs r5, r0\n    ldr r0, [r6]\n    ldr r1, [r5, #0x6c]\n    cmp r0, r1\n    blo L_open_cfw_runtime_am059_caafa_0038\n    movs r2, #0xb3\n    ldr.w r1, [pc, #0xa70]\n    ldr.w r0, [pc, #0xa78]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am059_addr_004d09b4\n    bl .\n    nop.w\nL_open_cfw_runtime_am059_caafa_0038:\n    ldr r0, [r5, #0x68]\n    ldr r1, [r0, #0x18]\n    ldr r0, [r6, #8]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am059_addr_004ca714\n    bl .\n    mov sb, r0\n    str.w sb, [sp]\n    ldr r3, [r6, #0xc]\n    ldr r2, [r6, #4]\n    ldr r1, [r6]\n    ldr r0, [r5, #0x68]\n    ldr r4, [r5, #0x68]\n    ldr r4, [r4, #8]\n    blx r4\n    movs r4, r0\n    cmp r4, #1\n    blt L_open_cfw_runtime_am059_caafa_006e\n    movs r2, #0xb7\n    ldr.w r1, [pc, #0xa38]\n    ldr.w r0, [pc, #0xa3c]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am059_addr_004d09b4\n    bl .\n    nop.w\nL_open_cfw_runtime_am059_caafa_006e:\n    cmp r4, #0\n    beq L_open_cfw_runtime_am059_caafa_0076\n    movs r0, r4\n    b L_open_cfw_runtime_am059_caafa_00bc\nL_open_cfw_runtime_am059_caafa_0076:\n    uxtb.w r8, r8\n    cmp.w r8, #0\n    beq L_open_cfw_runtime_am059_caafa_00b2\n    movs r1, r7\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am059_ca81a\n    bl .\n    str.w sb, [sp, #0xc]\n    ldr r0, [r6, #0xc]\n    str r0, [sp, #8]\n    ldr r0, [r6, #4]\n    str r0, [sp, #4]\n    ldr r0, [r6]\n    str r0, [sp]\n    mov r3, sb\n    movs r2, r7\n    movs r1, #0\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am059_caa04\n    bl .\n    cmp r0, #0\n    bmi L_open_cfw_runtime_am059_caafa_00bc\n    cmp r0, #0\n    beq L_open_cfw_runtime_am059_caafa_00b2\n    mvns r0, #0x53\n    b L_open_cfw_runtime_am059_caafa_00bc\nL_open_cfw_runtime_am059_caafa_00b2:\n    movs r1, r6\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am059_ca822\n    bl .\nL_open_cfw_runtime_am059_caafa_00ba:\n    movs r0, #0\nL_open_cfw_runtime_am059_caafa_00bc:\n    add sp, #0x14\n    pop.w {r4, r5, r6, r7, r8, sb, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM059_CABBC_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am059_cabbc(void)
{
    __asm__ volatile(
        "    push {r3, r4, r5, r6, r7, lr}\n    movs r4, r0\n    movs r5, r1\n    movs r6, r2\n    movs r7, r3\n    movs r1, r6\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am059_ca81a\n    bl .\n    movs r3, r7\n    uxtb r3, r3\n    movs r2, r6\n    movs r1, r5\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am059_caafa\n    bl .\n    cmp r0, #0\n    bne L_open_cfw_runtime_am059_cabbc_0046\n    ldr r0, [r4, #0x68]\n    ldr r1, [r4, #0x68]\n    ldr r1, [r1, #0x10]\n    blx r1\n    movs r4, r0\n    cmp r4, #1\n    blt L_open_cfw_runtime_am059_cabbc_0044\n    movs r2, #0xdd\n    ldr.w r1, [pc, #0x9a0]\n    ldr.w r0, [pc, #0x9a4]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am059_addr_004d09b4\n    bl .\n    nop.w\nL_open_cfw_runtime_am059_cabbc_0044:\n    movs r0, r4\nL_open_cfw_runtime_am059_cabbc_0046:\n    pop {r1, r4, r5, r6, r7, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM059_CAC04_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am059_cac04(void)
{
    __asm__ volatile(
        "    push.w {r1, r2, r3, r4, r5, r6, r7, r8, sb, sl, fp, lr}\n    movs r5, r0\n    mov sb, r1\n    mov sl, r2\n    mov fp, r3\n    ldr r6, [sp, #0x30]\n    ldr r7, [sp, #0x38]\n    cmn.w r6, #2\n    beq L_open_cfw_runtime_am059_cac04_002e\n    ldr r0, [r5, #0x6c]\n    cmp r6, r0\n    blo L_open_cfw_runtime_am059_cac04_002e\n    movs r2, #0xe8\n    ldr.w r1, [pc, #0x970]\n    ldr.w r0, [pc, #0x97c]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am059_addr_004d09b4\n    bl .\n    nop.w\nL_open_cfw_runtime_am059_cac04_002e:\n    ldr r4, [sp, #0x3c]\n    ldr.w r8, [sp, #0x34]\n    str.w sl, [sp, #4]\n    strb.w fp, [sp]\n    ldr r0, [r5, #0x68]\n    ldr r0, [r0, #0x1c]\n    adds.w r1, r4, r8\n    cmp r0, r1\n    bhs L_open_cfw_runtime_am059_cac04_005c\n    movs r2, #0xe9\n    ldr.w r1, [pc, #0x944]\n    ldr.w r0, [pc, #0x954]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am059_addr_004d09b4\n    bl .\n    nop.w\n    b L_open_cfw_runtime_am059_cac04_005c\nL_open_cfw_runtime_am059_cac04_005c:\n    cmp r4, #0\n    beq L_open_cfw_runtime_am059_cac04_0124\n    ldr.w r0, [sb]\n    cmp r6, r0\n    bne L_open_cfw_runtime_am059_cac04_00ec\n    ldr.w r0, [sb, #4]\n    cmp r8, r0\n    blo L_open_cfw_runtime_am059_cac04_00ec\n    ldr.w r1, [sb, #4]\n    ldr r0, [r5, #0x68]\n    ldr r0, [r0, #0x28]\n    adds r1, r0, r1\n    cmp r8, r1\n    bhs L_open_cfw_runtime_am059_cac04_00ec\n    ldr r0, [r5, #0x68]\n    ldr r1, [r0, #0x28]\n    subs.w r1, r1, r8\n    ldr.w r0, [sb, #4]\n    adds r1, r0, r1\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am059_addr_004ca700\n    bl .\n    mov sl, r0\n    mov r2, sl\n    movs r1, r7\n    ldr.w r0, [sb, #0xc]\n    ldr.w r3, [sb, #4]\n    subs.w r3, r8, r3\n    add.w fp, r0, r3\n    mov r0, fp\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am059_addr_00439be4\n    bl .\n    add r7, sl\n    adds.w r8, sl, r8\n    subs.w r4, r4, sl\n    ldr.w r1, [sb, #4]\n    subs.w r1, r8, r1\n    ldr.w r0, [sb, #8]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am059_addr_004ca6f8\n    bl .\n    str.w r0, [sb, #8]\n    ldr.w r0, [sb, #8]\n    ldr r1, [r5, #0x68]\n    ldr r1, [r1, #0x28]\n    cmp r0, r1\n    bne L_open_cfw_runtime_am059_cac04_005c\n    ldrb.w r3, [sp]\n    ldr r2, [sp, #4]\n    mov r1, sb\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am059_caafa\n    bl .\n    cmp r0, #0\n    beq L_open_cfw_runtime_am059_cac04_005c\n    b L_open_cfw_runtime_am059_cac04_0126\nL_open_cfw_runtime_am059_cac04_00ec:\n    ldr.w r0, [sb]\n    cmn.w r0, #1\n    beq L_open_cfw_runtime_am059_cac04_010a\n    mov.w r2, #0x106\n    ldr.w r1, [pc, #0x894]\n    ldr.w r0, [pc, #0xc58]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am059_addr_004d09b4\n    bl .\n    nop.w\nL_open_cfw_runtime_am059_cac04_010a:\n    str.w r6, [sb]\n    ldr r0, [r5, #0x68]\n    ldr r1, [r0, #0x18]\n    mov r0, r8\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am059_addr_004ca708\n    bl .\n    str.w r0, [sb, #4]\n    movs r0, #0\n    str.w r0, [sb, #8]\n    b L_open_cfw_runtime_am059_cac04_005c\nL_open_cfw_runtime_am059_cac04_0124:\n    movs r0, #0\nL_open_cfw_runtime_am059_cac04_0126:\n    pop.w {r1, r2, r3, r4, r5, r6, r7, r8, sb, sl, fp, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM059_CAD2E_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am059_cad2e(void)
{
    __asm__ volatile(
        "    push {r3, r4, r5, lr}\n    movs r4, r0\n    movs r5, r1\n    ldr r0, [r4, #0x6c]\n    cmp r5, r0\n    blo L_open_cfw_runtime_am059_cad2e_0020\n    mov.w r2, #0x114\n    ldr.w r1, [pc, #0x854]\n    ldr.w r0, [pc, #0xc1c]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am059_addr_004d09b4\n    bl .\n    nop.w\nL_open_cfw_runtime_am059_cad2e_0020:\n    movs r1, r5\n    ldr r0, [r4, #0x68]\n    ldr r2, [r4, #0x68]\n    ldr r2, [r2, #0xc]\n    blx r2\n    movs r4, r0\n    cmp r4, #1\n    blt L_open_cfw_runtime_am059_cad2e_0044\n    mov.w r2, #0x116\n    ldr.w r1, [pc, #0x830]\n    ldr.w r0, [pc, #0x834]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am059_addr_004d09b4\n    bl .\n    nop.w\nL_open_cfw_runtime_am059_cad2e_0044:\n    movs r0, r4\n    pop {r1, r4, r5, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM059_CAD76_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am059_cad76(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    adr r1, #0x2c\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am059_addr_00541b30\n    bl .\n    pop {r1, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM059_CAD80_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am059_cad80(void)
{
    __asm__ volatile(
        "    push {r3, r4, r5, lr}\n    movs r4, r0\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am059_cad76\n    bl .\n    movs r5, r0\n    adr r1, #0x18\n    add.w r0, r4, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am059_addr_00541b52\n    bl .\n    adds r5, r0, r5\n    ldrb r0, [r4, r5]\n    cmp r0, #0\n    bne L_open_cfw_runtime_am059_cad80_0022\n    movs r0, #1\n    b L_open_cfw_runtime_am059_cad80_0024\nL_open_cfw_runtime_am059_cad80_0022:\n    movs r0, #0\nL_open_cfw_runtime_am059_cad80_0024:\n    uxtb r0, r0\n    pop {r1, r4, r5, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM059_CADAC_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am059_cadac(void)
{
    __asm__ volatile(
        "    push {r4, lr}\n    movs r4, r0\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am059_cad76\n    bl .\n    ldrb r0, [r4, r0]\n    cmp r0, #0\n    beq L_open_cfw_runtime_am059_cadac_0014\n    movs r0, #1\n    b L_open_cfw_runtime_am059_cadac_0016\nL_open_cfw_runtime_am059_cadac_0014:\n    movs r0, #0\nL_open_cfw_runtime_am059_cadac_0016:\n    uxtb r0, r0\n    pop {r4, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM059_CADC6_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am059_cadc6(void)
{
    __asm__ volatile(
        "    ldr r1, [r0]\n    ldr r2, [r0, #4]\n    str r2, [r0]\n    str r1, [r0, #4]\n    bx lr\n"
    );
}
#endif

#if defined(OPEN_CFW_AM059_CADD0_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am059_cadd0(void)
{
    __asm__ volatile(
        "    ldr r1, [r0]\n    cmn.w r1, #1\n    beq L_open_cfw_runtime_am059_cadd0_0010\n    ldr r0, [r0, #4]\n    cmn.w r0, #1\n    bne L_open_cfw_runtime_am059_cadd0_0014\nL_open_cfw_runtime_am059_cadd0_0010:\n    movs r0, #1\n    b L_open_cfw_runtime_am059_cadd0_0016\nL_open_cfw_runtime_am059_cadd0_0014:\n    movs r0, #0\nL_open_cfw_runtime_am059_cadd0_0016:\n    uxtb r0, r0\n    bx lr\n"
    );
}
#endif

#if defined(OPEN_CFW_AM059_CADEA_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am059_cadea(void)
{
    __asm__ volatile(
        "    ldr r2, [r0]\n    ldr r3, [r1]\n    cmp r2, r3\n    beq L_open_cfw_runtime_am059_cadea_0024\n    ldr r2, [r0, #4]\n    ldr r3, [r1, #4]\n    cmp r2, r3\n    beq L_open_cfw_runtime_am059_cadea_0024\n    ldr r2, [r0]\n    ldr r3, [r1, #4]\n    cmp r2, r3\n    beq L_open_cfw_runtime_am059_cadea_0024\n    ldr r0, [r0, #4]\n    ldr r1, [r1]\n    cmp r0, r1\n    beq L_open_cfw_runtime_am059_cadea_0024\n    movs r0, #1\n    b L_open_cfw_runtime_am059_cadea_0026\nL_open_cfw_runtime_am059_cadea_0024:\n    movs r0, #0\nL_open_cfw_runtime_am059_cadea_0026:\n    uxtb r0, r0\n    bx lr\n"
    );
}
#endif

#if defined(OPEN_CFW_AM059_CAE14_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am059_cae14(void)
{
    __asm__ volatile(
        "    ldr r2, [r0]\n    ldr r3, [r1]\n    cmp r2, r3\n    bne L_open_cfw_runtime_am059_cae14_0010\n    ldr r2, [r0, #4]\n    ldr r3, [r1, #4]\n    cmp r2, r3\n    beq L_open_cfw_runtime_am059_cae14_0020\nL_open_cfw_runtime_am059_cae14_0010:\n    ldr r2, [r0]\n    ldr r3, [r1, #4]\n    cmp r2, r3\n    bne L_open_cfw_runtime_am059_cae14_0024\n    ldr r0, [r0, #4]\n    ldr r1, [r1]\n    cmp r0, r1\n    bne L_open_cfw_runtime_am059_cae14_0024\nL_open_cfw_runtime_am059_cae14_0020:\n    movs r0, #1\n    b L_open_cfw_runtime_am059_cae14_0026\nL_open_cfw_runtime_am059_cae14_0024:\n    movs r0, #0\nL_open_cfw_runtime_am059_cae14_0026:\n    uxtb r0, r0\n    bx lr\n"
    );
}
#endif

#if defined(OPEN_CFW_AM059_CAE3E_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am059_cae3e(void)
{
    __asm__ volatile(
        "    push {r4, lr}\n    movs r4, r0\n    ldr r0, [r4]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am059_addr_004ca7b6\n    bl .\n    str r0, [r4]\n    ldr r0, [r4, #4]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am059_addr_004ca7b6\n    bl .\n    str r0, [r4, #4]\n    pop {r4, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM059_CAE54_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am059_cae54(void)
{
    __asm__ volatile(
        "    push {r4, lr}\n    movs r4, r0\n    ldr r0, [r4]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am059_addr_004ca7d8\n    bl .\n    str r0, [r4]\n    ldr r0, [r4, #4]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am059_addr_004ca7d8\n    bl .\n    str r0, [r4, #4]\n    pop {r4, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM059_CAE74_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am059_cae74(void)
{
    __asm__ volatile(
        "    lsls r0, r0, #0x16\n    asrs r0, r0, #0x16\n    cmn.w r0, #1\n    bne L_open_cfw_runtime_am059_cae74_000e\n    movs r0, #1\n    b L_open_cfw_runtime_am059_cae74_0010\nL_open_cfw_runtime_am059_cae74_000e:\n    movs r0, #0\nL_open_cfw_runtime_am059_cae74_0010:\n    uxtb r0, r0\n    bx lr\n"
    );
}
#endif

#if defined(OPEN_CFW_AM059_CAEA6_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am059_caea6(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am059_addr_004caea0\n    bl .\n    sxtb r0, r0\n    pop {r1, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM059_CAEBE_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am059_caebe(void)
{
    __asm__ volatile(
        "    push {r4, lr}\n    movs r4, r0\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am059_cae74\n    bl .\n    uxtab r0, r4, r0\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am059_addr_004caeb8\n    bl .\n    adds r0, r0, #4\n    pop {r4, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM059_CAED4_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am059_caed4(void)
{
    __asm__ volatile(
        "    push {r4}\n    movs r3, #0\n    b L_open_cfw_runtime_am059_caed4_0016\nL_open_cfw_runtime_am059_caed4_0006:\n    ldr.w r4, [r0, r3, lsl #2]\n    ldr.w r2, [r1, r3, lsl #2]\n    eors r4, r2\n    str.w r4, [r0, r3, lsl #2]\n    adds r3, r3, #1\nL_open_cfw_runtime_am059_caed4_0016:\n    cmp r3, #3\n    blt L_open_cfw_runtime_am059_caed4_0006\n    pop {r4}\n    bx lr\n"
    );
}
#endif

#if defined(OPEN_CFW_AM059_CAEF2_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am059_caef2(void)
{
    __asm__ volatile(
        "    movs r2, #0\n    b L_open_cfw_runtime_am059_caef2_0006\nL_open_cfw_runtime_am059_caef2_0004:\n    adds r2, r2, #1\nL_open_cfw_runtime_am059_caef2_0006:\n    cmp r2, #3\n    bge L_open_cfw_runtime_am059_caef2_0016\n    ldr.w r1, [r0, r2, lsl #2]\n    cmp r1, #0\n    beq L_open_cfw_runtime_am059_caef2_0004\n    movs r0, #0\n    b L_open_cfw_runtime_am059_caef2_0018\nL_open_cfw_runtime_am059_caef2_0016:\n    movs r0, #1\nL_open_cfw_runtime_am059_caef2_0018:\n    bx lr\n"
    );
}
#endif

#if defined(OPEN_CFW_AM059_CAF0C_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am059_caf0c(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    ldr r0, [r0]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am059_addr_004caeb8\n    bl .\n    cmp r0, #0\n    beq L_open_cfw_runtime_am059_caf0c_0010\n    movs r0, #1\n    b L_open_cfw_runtime_am059_caf0c_0012\nL_open_cfw_runtime_am059_caf0c_0010:\n    movs r0, #0\nL_open_cfw_runtime_am059_caf0c_0012:\n    uxtb r0, r0\n    pop {r1, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM059_CAF22_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am059_caf22(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    ldr r0, [r0]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am059_addr_004caeb8\n    bl .\n    uxtb r0, r0\n    pop {r1, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM059_CAF2E_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am059_caf2e(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    ldr r0, [r0]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am059_addr_004cae88\n    bl .\n    cmp r0, #0\n    beq L_open_cfw_runtime_am059_caf2e_0010\n    movs r0, #1\n    b L_open_cfw_runtime_am059_caf2e_0012\nL_open_cfw_runtime_am059_caf2e_0010:\n    movs r0, #0\nL_open_cfw_runtime_am059_caf2e_0012:\n    uxtb r0, r0\n    pop {r1, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM059_CAF44_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am059_caf44(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    ldr r0, [r0]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am059_addr_004caeb8\n    bl .\n    lsrs r0, r0, #9\n    cmp r0, #0\n    beq L_open_cfw_runtime_am059_caf44_0012\n    movs r0, #1\n    b L_open_cfw_runtime_am059_caf44_0014\nL_open_cfw_runtime_am059_caf44_0012:\n    movs r0, #0\nL_open_cfw_runtime_am059_caf44_0014:\n    uxtb r0, r0\n    pop {r1, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM059_CAF5C_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am059_caf5c(void)
{
    __asm__ volatile(
        "    push {r3, r4, r5, lr}\n    movs r4, r0\n    movs r5, r1\n    ldr r0, [r4]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am059_addr_004cae88\n    bl .\n    cmp r0, #0\n    beq L_open_cfw_runtime_am059_caf5c_0020\n    movs r1, r5\n    adds r0, r4, #4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am059_cadea\n    bl .\n    cmp r0, #0\n    bne L_open_cfw_runtime_am059_caf5c_0020\n    movs r0, #1\n    b L_open_cfw_runtime_am059_caf5c_0022\nL_open_cfw_runtime_am059_caf5c_0020:\n    movs r0, #0\nL_open_cfw_runtime_am059_caf5c_0022:\n    uxtb r0, r0\n    pop {r1, r4, r5, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM059_CAF82_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am059_caf82(void)
{
    __asm__ volatile(
        "    push {r4, lr}\n    movs r4, r0\n    ldr r0, [r4]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am059_addr_004ca7b6\n    bl .\n    str r0, [r4]\n    ldr r0, [r4, #4]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am059_addr_004ca7b6\n    bl .\n    str r0, [r4, #4]\n    ldr r0, [r4, #8]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am059_addr_004ca7b6\n    bl .\n    str r0, [r4, #8]\n    pop {r4, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM059_CAFA0_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am059_cafa0(void)
{
    __asm__ volatile(
        "    push {r4, lr}\n    movs r4, r0\n    ldr r0, [r4]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am059_addr_004ca7d8\n    bl .\n    str r0, [r4]\n    ldr r0, [r4, #4]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am059_addr_004ca7d8\n    bl .\n    str r0, [r4, #4]\n    ldr r0, [r4, #8]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am059_addr_004ca7d8\n    bl .\n    str r0, [r4, #8]\n    pop {r4, pc}\n"
    );
}
#endif
