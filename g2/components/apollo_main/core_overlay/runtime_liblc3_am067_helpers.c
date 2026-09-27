/*
 * SPDX-License-Identifier: MIT
 *
 * Source-owned exact helpers from the AM-067 retained island.
 */

#if defined(OPEN_CFW_AM067_D483E_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am067_d483e(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    movs r2, r1\n    movs r1, #3\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am067_addr_00482868\n    bl .\n    pop {r0, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM067_D484A_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am067_d484a(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    movs r2, r1\n    movs r1, #0x6a\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am067_addr_00482868\n    bl .\n    pop {r0, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM067_D4856_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am067_d4856(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    movs r2, r1\n    movs r1, #0x6b\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am067_addr_00482868\n    bl .\n    pop {r0, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM067_D4862_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am067_d4862(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    movs r2, r1\n    movs r1, #0x10\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am067_addr_00482868\n    bl .\n    pop {r0, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM067_D486E_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am067_d486e(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    movs r2, r1\n    movs r1, #0x11\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am067_addr_00482868\n    bl .\n    pop {r0, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM067_D487A_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am067_d487a(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    movs r2, r1\n    movs r1, #0x12\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am067_addr_00482868\n    bl .\n    pop {r0, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM067_D4886_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am067_d4886(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    movs r2, r1\n    movs r1, #0x13\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am067_addr_00482868\n    bl .\n    pop {r0, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM067_D4892_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am067_d4892(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    movs r2, r1\n    movs r1, #0x14\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am067_addr_00482868\n    bl .\n    pop {r0, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM067_D489E_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am067_d489e(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    movs r2, r1\n    movs r1, #0x15\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am067_addr_00482868\n    bl .\n    pop {r0, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM067_D48AA_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am067_d48aa(void)
{
    __asm__ volatile(
        "    push {r0, r1, r4, lr}\n    movs r4, r0\n    mov r0, sp\n    add r1, sp, #4\n    movs r2, #3\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am067_addr_00439be4\n    bl .\n    ldr r2, [sp]\n    movs r1, #0x1c\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am067_addr_00482868\n    bl .\n    pop {r0, r1, r4, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM067_D48C4_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am067_d48c4(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    movs r2, r1\n    uxtb r2, r2\n    movs r1, #0x1d\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am067_addr_00482868\n    bl .\n    pop {r0, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM067_D48D2_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am067_d48d2(void)
{
    __asm__ volatile(
        "    push {r0, r1, r4, lr}\n    movs r4, r0\n    mov r0, sp\n    add r1, sp, #4\n    movs r2, #3\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am067_addr_00439be4\n    bl .\n    ldr r2, [sp]\n    movs r1, #0x23\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am067_addr_00482868\n    bl .\n    pop {r0, r1, r4, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM067_D48EC_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am067_d48ec(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    movs r2, r1\n    movs r1, #0x28\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am067_addr_00482868\n    bl .\n    pop {r0, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM067_D48F8_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am067_d48f8(void)
{
    __asm__ volatile(
        "    push {r0, r1, r4, lr}\n    movs r4, r0\n    mov r0, sp\n    add r1, sp, #4\n    movs r2, #3\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am067_addr_00439be4\n    bl .\n    ldr r2, [sp]\n    movs r1, #0x31\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am067_addr_00482868\n    bl .\n    pop {r0, r1, r4, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM067_D4912_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am067_d4912(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    movs r2, r1\n    uxtb r2, r2\n    movs r1, #0x32\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am067_addr_00482868\n    bl .\n    pop {r0, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM067_D4920_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am067_d4920(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    movs r2, r1\n    movs r1, #0x30\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am067_addr_00482868\n    bl .\n    pop {r0, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM067_D492C_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am067_d492c(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    movs r2, r1\n    uxtb r2, r2\n    movs r1, #0x34\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am067_addr_00482868\n    bl .\n    pop {r0, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM067_D493A_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am067_d493a(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    movs r2, r1\n    uxtb r2, r2\n    movs r1, #0x35\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am067_addr_00482868\n    bl .\n    pop {r0, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM067_D4948_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am067_d4948(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    movs r2, r1\n    movs r1, #0x38\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am067_addr_00482868\n    bl .\n    pop {r0, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM067_D4954_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am067_d4954(void)
{
    __asm__ volatile(
        "    push {r0, r1, r4, lr}\n    movs r4, r0\n    mov r0, sp\n    add r1, sp, #4\n    movs r2, #3\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am067_addr_00439be4\n    bl .\n    ldr r2, [sp]\n    movs r1, #0x39\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am067_addr_00482868\n    bl .\n    pop {r0, r1, r4, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM067_D496E_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am067_d496e(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    movs r2, r1\n    uxtb r2, r2\n    movs r1, #0x3a\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am067_addr_00482868\n    bl .\n    pop {r0, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM067_D497C_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am067_d497c(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    movs r2, r1\n    movs r1, #0x3b\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am067_addr_00482868\n    bl .\n    pop {r0, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM067_D4988_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am067_d4988(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    movs r2, r1\n    movs r1, #0x3c\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am067_addr_00482868\n    bl .\n    pop {r0, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM067_D4994_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am067_d4994(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    movs r2, r1\n    movs r1, #0x41\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am067_addr_00482868\n    bl .\n    pop {r0, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM067_D49A0_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am067_d49a0(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    movs r2, r1\n    movs r1, #0x42\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am067_addr_00482868\n    bl .\n    pop {r0, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM067_D49AC_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am067_d49ac(void)
{
    __asm__ volatile(
        "    push {r0, r1, r4, lr}\n    movs r4, r0\n    mov r0, sp\n    add r1, sp, #4\n    movs r2, #3\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am067_addr_00439be4\n    bl .\n    ldr r2, [sp]\n    movs r1, #0x3d\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am067_addr_00482868\n    bl .\n    pop {r0, r1, r4, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM067_D49C6_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am067_d49c6(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    movs r2, r1\n    uxtb r2, r2\n    movs r1, #0x3e\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am067_addr_00482868\n    bl .\n    pop {r0, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM067_D49D4_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am067_d49d4(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    movs r2, r1\n    movs r1, #0x48\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am067_addr_00482868\n    bl .\n    pop {r0, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM067_D49E0_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am067_d49e0(void)
{
    __asm__ volatile(
        "    push {r0, r1, r4, lr}\n    movs r4, r0\n    mov r0, sp\n    add r1, sp, #4\n    movs r2, #3\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am067_addr_00439be4\n    bl .\n    ldr r2, [sp]\n    movs r1, #0x4c\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am067_addr_00482868\n    bl .\n    pop {r0, r1, r4, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM067_D49FA_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am067_d49fa(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    movs r2, r1\n    movs r1, #0x50\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am067_addr_00482868\n    bl .\n    pop {r0, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM067_D4A06_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am067_d4a06(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    movs r2, r1\n    uxtb r2, r2\n    movs r1, #0x51\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am067_addr_00482868\n    bl .\n    pop {r0, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM067_D4A14_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am067_d4a14(void)
{
    __asm__ volatile(
        "    push {r0, r1, r4, lr}\n    movs r4, r0\n    mov r0, sp\n    add r1, sp, #4\n    movs r2, #3\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am067_addr_00439be4\n    bl .\n    ldr r2, [sp]\n    movs r1, #0x52\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am067_addr_00482868\n    bl .\n    pop {r0, r1, r4, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM067_D4A2E_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am067_d4a2e(void)
{
    __asm__ volatile(
        "    push {r0, r1, r4, lr}\n    movs r4, r0\n    mov r0, sp\n    add r1, sp, #4\n    movs r2, #3\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am067_addr_00439be4\n    bl .\n    ldr r2, [sp]\n    movs r1, #0x58\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am067_addr_00482868\n    bl .\n    pop {r0, r1, r4, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM067_D4A48_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am067_d4a48(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    movs r2, r1\n    movs r1, #0x5a\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am067_addr_00482868\n    bl .\n    pop {r0, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM067_D4A54_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am067_d4a54(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    movs r2, r1\n    movs r1, #0x5c\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am067_addr_00482868\n    bl .\n    pop {r0, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM067_D4A60_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am067_d4a60(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    movs r2, r1\n    uxtb r2, r2\n    movs r1, #0x5e\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am067_addr_00482868\n    bl .\n    pop {r0, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM067_D4A6E_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am067_d4a6e(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    movs r2, r1\n    movs r1, #0xc\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am067_addr_00482868\n    bl .\n    pop {r0, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM067_D4A7A_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am067_d4a7a(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    movs r2, r1\n    uxtb r2, r2\n    movs r1, #0x2d\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am067_addr_00482868\n    bl .\n    pop {r0, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM067_D4A88_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am067_d4a88(void)
{
    __asm__ volatile(
        "    push {r0, r1, r4, lr}\n    movs r4, r0\n    mov r0, sp\n    add r1, sp, #4\n    movs r2, #3\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am067_addr_00439be4\n    bl .\n    ldr r2, [sp]\n    movs r1, #0x78\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am067_addr_00482868\n    bl .\n    pop {r0, r1, r4, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM067_D4AA2_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am067_d4aa2(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    movs r2, r1\n    uxtb r2, r2\n    movs r1, #0x79\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am067_addr_00482868\n    bl .\n    pop {r0, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM067_D4AB0_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am067_d4ab0(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    movs r2, r1\n    movs r1, #0x67\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am067_addr_00482868\n    bl .\n    pop {r0, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM067_D4ABC_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am067_d4abc(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    movs r2, r1\n    movs r1, #0x68\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am067_addr_00482868\n    bl .\n    pop {r0, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM067_D4AC8_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am067_d4ac8(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    movs r2, r1\n    movs r1, #0x76\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am067_addr_00482868\n    bl .\n    pop {r0, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM067_D4AD4_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am067_d4ad4(void)
{
    __asm__ volatile(
        "    push {r1, r2, r3, r4, r5, lr}\n    movs r4, r0\n    ldr r5, [pc, #0xf0]\n    ldr.w r0, [r5, #0x134]\n    cmp r0, #0\n    beq L_open_cfw_runtime_am067_d4ad4_0012\n    movs r0, #1\n    b L_open_cfw_runtime_am067_d4ad4_004e\nL_open_cfw_runtime_am067_d4ad4_0012:\n    ldr r0, [pc, #0xe8]\n    sub sp, #4\n    mov r1, sp\n    ldm r0!, {r2, r3}\n    stm r1!, {r2, r3}\n    ldr r2, [r0]\n    str r2, [r1]\n    subs r0, #8\n    subs r1, #8\n    pop {r3}\n    movs r2, r4\n    movs r1, #0x18\n    ldr r0, [pc, #0xd4]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am067_d4cd4\n    bl .\n    str.w r0, [r5, #0x134]\n    ldr r1, [pc, #0xcc]\n    ldr.w r0, [r5, #0x134]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am067_d5114\n    bl .\n    ldr.w r0, [r5, #0x134]\n    cmp r0, #0\n    beq L_open_cfw_runtime_am067_d4ad4_004a\n    movs r0, #1\n    b L_open_cfw_runtime_am067_d4ad4_004c\nL_open_cfw_runtime_am067_d4ad4_004a:\n    movs r0, #0\nL_open_cfw_runtime_am067_d4ad4_004c:\n    uxtb r0, r0\nL_open_cfw_runtime_am067_d4ad4_004e:\n    pop {r1, r2, r3, r4, r5, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM067_D4B24_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am067_d4b24(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    ldr r0, [pc, #0xa4]\n    ldr.w r0, [r0, #0x134]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am067_d5104\n    bl .\n    pop {r1, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM067_D4B32_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am067_d4b32(void)
{
    __asm__ volatile(
        "    push {r3, r4, r5, lr}\n    movs r4, r1\n    movs r5, r3\n    uxtb r4, r4\n    uxtb r5, r5\n    cmp r4, r5\n    bne L_open_cfw_runtime_am067_d4b32_004e\n    movs r3, r1\n    uxtb r3, r3\n    cmp r3, #1\n    bne L_open_cfw_runtime_am067_d4b32_0030\n    movs r1, r2\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am067_addr_004547be\n    bl .\n    cmp r0, #0\n    beq L_open_cfw_runtime_am067_d4b32_004a\n    cmp r0, #1\n    blt L_open_cfw_runtime_am067_d4b32_0028\n    movs r0, #1\n    b L_open_cfw_runtime_am067_d4b32_002c\nL_open_cfw_runtime_am067_d4b32_0028:\n    movs.w r0, #-1\nL_open_cfw_runtime_am067_d4b32_002c:\n    sxtb r0, r0\n    b L_open_cfw_runtime_am067_d4b32_0060\nL_open_cfw_runtime_am067_d4b32_0030:\n    uxtb r1, r1\n    cmp r1, #0\n    bne L_open_cfw_runtime_am067_d4b32_004a\n    cmp r0, r2\n    beq L_open_cfw_runtime_am067_d4b32_004a\n    cmp r2, r0\n    bhs L_open_cfw_runtime_am067_d4b32_0042\n    movs r0, #1\n    b L_open_cfw_runtime_am067_d4b32_0046\nL_open_cfw_runtime_am067_d4b32_0042:\n    movs.w r0, #-1\nL_open_cfw_runtime_am067_d4b32_0046:\n    sxtb r0, r0\n    b L_open_cfw_runtime_am067_d4b32_0060\nL_open_cfw_runtime_am067_d4b32_004a:\n    movs r0, #0\n    b L_open_cfw_runtime_am067_d4b32_0060\nL_open_cfw_runtime_am067_d4b32_004e:\n    uxtb r3, r3\n    uxtb r1, r1\n    cmp r3, r1\n    bhs L_open_cfw_runtime_am067_d4b32_005a\n    movs r0, #1\n    b L_open_cfw_runtime_am067_d4b32_005e\nL_open_cfw_runtime_am067_d4b32_005a:\n    movs.w r0, #-1\nL_open_cfw_runtime_am067_d4b32_005e:\n    sxtb r0, r0\nL_open_cfw_runtime_am067_d4b32_0060:\n    pop {r1, r4, r5, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM067_D4B94_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am067_d4b94(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    ldrb r3, [r1, #8]\n    ldr r2, [r1, #4]\n    ldrb r1, [r0, #8]\n    ldr r0, [r0, #4]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am067_d4b32\n    bl .\n    pop {r1, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM067_D4BDC_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am067_d4bdc(void)
{
    __asm__ volatile(
        "    push {r1, r2, r3, r4, r5, lr}\n    movs r4, r0\n    ldr r5, [pc, #0xd8]\n    ldr.w r0, [r5, #0x138]\n    cmp r0, #0\n    beq L_open_cfw_runtime_am067_d4bdc_0012\n    movs r0, #1\n    b L_open_cfw_runtime_am067_d4bdc_004e\nL_open_cfw_runtime_am067_d4bdc_0012:\n    ldr r0, [pc, #0xd0]\n    sub sp, #4\n    mov r1, sp\n    ldm r0!, {r2, r3}\n    stm r1!, {r2, r3}\n    ldr r2, [r0]\n    str r2, [r1]\n    subs r0, #8\n    subs r1, #8\n    pop {r3}\n    movs r2, r4\n    movs r1, #0x18\n    ldr r0, [pc, #0xbc]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am067_d4cd4\n    bl .\n    str.w r0, [r5, #0x138]\n    ldr r1, [pc, #0xb4]\n    ldr.w r0, [r5, #0x138]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am067_d5114\n    bl .\n    ldr.w r0, [r5, #0x138]\n    cmp r0, #0\n    beq L_open_cfw_runtime_am067_d4bdc_004a\n    movs r0, #1\n    b L_open_cfw_runtime_am067_d4bdc_004c\nL_open_cfw_runtime_am067_d4bdc_004a:\n    movs r0, #0\nL_open_cfw_runtime_am067_d4bdc_004c:\n    uxtb r0, r0\nL_open_cfw_runtime_am067_d4bdc_004e:\n    pop {r1, r2, r3, r4, r5, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM067_D4C2C_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am067_d4c2c(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    ldr r0, [pc, #0x8c]\n    ldr.w r0, [r0, #0x138]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am067_d5104\n    bl .\n    pop {r1, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM067_D4C3A_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am067_d4c3a(void)
{
    __asm__ volatile(
        "    push {r3, r4, r5, lr}\n    movs r4, r1\n    movs r5, r3\n    uxtb r4, r4\n    uxtb r5, r5\n    cmp r4, r5\n    bne L_open_cfw_runtime_am067_d4c3a_004e\n    movs r3, r1\n    uxtb r3, r3\n    cmp r3, #1\n    bne L_open_cfw_runtime_am067_d4c3a_0030\n    movs r1, r2\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am067_addr_004547be\n    bl .\n    cmp r0, #0\n    beq L_open_cfw_runtime_am067_d4c3a_004a\n    cmp r0, #1\n    blt L_open_cfw_runtime_am067_d4c3a_0028\n    movs r0, #1\n    b L_open_cfw_runtime_am067_d4c3a_002c\nL_open_cfw_runtime_am067_d4c3a_0028:\n    movs.w r0, #-1\nL_open_cfw_runtime_am067_d4c3a_002c:\n    sxtb r0, r0\n    b L_open_cfw_runtime_am067_d4c3a_0060\nL_open_cfw_runtime_am067_d4c3a_0030:\n    uxtb r1, r1\n    cmp r1, #0\n    bne L_open_cfw_runtime_am067_d4c3a_004a\n    cmp r0, r2\n    beq L_open_cfw_runtime_am067_d4c3a_004a\n    cmp r2, r0\n    bhs L_open_cfw_runtime_am067_d4c3a_0042\n    movs r0, #1\n    b L_open_cfw_runtime_am067_d4c3a_0046\nL_open_cfw_runtime_am067_d4c3a_0042:\n    movs.w r0, #-1\nL_open_cfw_runtime_am067_d4c3a_0046:\n    sxtb r0, r0\n    b L_open_cfw_runtime_am067_d4c3a_0060\nL_open_cfw_runtime_am067_d4c3a_004a:\n    movs r0, #0\n    b L_open_cfw_runtime_am067_d4c3a_0060\nL_open_cfw_runtime_am067_d4c3a_004e:\n    uxtb r3, r3\n    uxtb r1, r1\n    cmp r3, r1\n    bhs L_open_cfw_runtime_am067_d4c3a_005a\n    movs r0, #1\n    b L_open_cfw_runtime_am067_d4c3a_005e\nL_open_cfw_runtime_am067_d4c3a_005a:\n    movs.w r0, #-1\nL_open_cfw_runtime_am067_d4c3a_005e:\n    sxtb r0, r0\nL_open_cfw_runtime_am067_d4c3a_0060:\n    pop {r1, r4, r5, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM067_D4C9C_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am067_d4c9c(void)
{
    __asm__ volatile(
        "    push {r7, lr}\n    ldrb r3, [r1, #4]\n    ldr r2, [r1]\n    ldrb r1, [r0, #4]\n    ldr r0, [r0]\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am067_d4c3a\n    bl .\n    pop {r1, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM067_D4CCC_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am067_d4ccc(void)
{
    __asm__ volatile(
        "    movs r2, #0\n    b.w #0x43c0ec\n"
    );
}
#endif

#if defined(OPEN_CFW_AM067_D4CD4_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am067_d4cd4(void)
{
    __asm__ volatile(
        "    push {r3}\n    push {r0, r1, r2, r3, r4, r5, r6, r7, lr}\n    movs r5, r0\n    movs r6, r1\n    movs r7, r2\n    ldr r0, [r5]\n    blx r0\n    movs r4, r0\n    cmp r4, #0\n    bne L_open_cfw_runtime_am067_d4cd4_0040\n    ldr.w r0, [pc, #0x540]\n    str r0, [sp, #8]\n    ldr.w r0, [pc, #0x540]\n    str r0, [sp, #4]\n    ldr.w r0, [pc, #0x53c]\n    str r0, [sp]\n    ldr.w r3, [pc, #0x53c]\n    movs r2, #0x33\n    ldr.w r1, [pc, #0x538]\n    movs r0, #3\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am067_addr_0044d25c\n    bl .\nL_open_cfw_runtime_am067_d4cd4_0036:\n    movs r0, #0\n    movs.w r1, #-1\n    str r0, [r1]\n    b L_open_cfw_runtime_am067_d4cd4_0036\nL_open_cfw_runtime_am067_d4cd4_0040:\n    str r5, [r4]\n    str r6, [r4, #4]\n    str r7, [r4, #8]\n    movs r0, #0\n    str r0, [r4, #0xc]\n    adds.w r0, r4, #0x10\n    add r1, sp, #0x24\n    ldm.w r1, {r2, r3, r5}\n    stm.w r0, {r2, r3, r5}\n    movs r0, r4\n    ldr r1, [r4]\n    ldr r1, [r1, #4]\n    blx r1\n    cmp r0, #0\n    bne L_open_cfw_runtime_am067_d4cd4_0084\n    ldr.w r0, [pc, #0x504]\n    str r0, [sp]\n    ldr.w r3, [pc, #0x4f8]\n    movs r2, #0x3c\n    ldr.w r1, [pc, #0x4f4]\n    movs r0, #3\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am067_addr_0044d25c\n    bl .\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am067_addr_0044f758\n    bl .\n    movs r0, #0\n    b L_open_cfw_runtime_am067_d4cd4_008e\nL_open_cfw_runtime_am067_d4cd4_0084:\n    adds.w r0, r4, #0x1c\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am067_addr_004d465c\n    bl .\n    movs r0, r4\nL_open_cfw_runtime_am067_d4cd4_008e:\n    add sp, #0x10\n    pop {r4, r5, r6, r7}\n    ldr pc, [sp], #8\n"
    );
}
#endif

#if defined(OPEN_CFW_AM067_D4D6A_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am067_d4d6a(void)
{
    __asm__ volatile(
        "    push {r1, r2, r3, r4, r5, lr}\n    movs r4, r0\n    movs r5, r1\n    cmp r4, #0\n    bne L_open_cfw_runtime_am067_d4d6a_0036\n    ldr.w r0, [pc, #0x4cc]\n    str r0, [sp, #8]\n    ldr.w r0, [pc, #0x4b4]\n    str r0, [sp, #4]\n    ldr.w r0, [pc, #0x4b0]\n    str r0, [sp]\n    ldr.w r3, [pc, #0x4c0]\n    movs r2, #0x48\n    ldr.w r1, [pc, #0x4ac]\n    movs r0, #3\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am067_addr_0044d25c\n    bl .\nL_open_cfw_runtime_am067_d4d6a_002c:\n    movs r0, #0\n    movs.w r1, #-1\n    str r0, [r1]\n    b L_open_cfw_runtime_am067_d4d6a_002c\nL_open_cfw_runtime_am067_d4d6a_0036:\n    adds.w r0, r4, #0x1c\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am067_addr_004d4666\n    bl .\n    movs r1, r5\n    movs r0, r4\n    ldr r2, [r4]\n    ldr r2, [r2, #8]\n    blx r2\n    adds.w r0, r4, #0x1c\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am067_addr_004d4696\n    bl .\n    adds.w r0, r4, #0x1c\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am067_addr_004d46c2\n    bl .\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am067_addr_0044f758\n    bl .\n    pop {r0, r1, r2, r4, r5, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM067_D4DCA_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am067_d4dca(void)
{
    __asm__ volatile(
        "    push {r0, r1, r2, r3, r4, r5, r6, lr}\n    movs r5, r0\n    movs r4, r1\n    movs r6, r2\n    cmp r5, #0\n    bne L_open_cfw_runtime_am067_d4dca_0038\n    ldr.w r0, [pc, #0x46c]\n    str r0, [sp, #8]\n    ldr.w r0, [pc, #0x450]\n    str r0, [sp, #4]\n    ldr.w r0, [pc, #0x450]\n    str r0, [sp]\n    ldr.w r3, [pc, #0x460]\n    movs r2, #0x53\n    ldr.w r1, [pc, #0x44c]\n    movs r0, #3\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am067_addr_0044d25c\n    bl .\nL_open_cfw_runtime_am067_d4dca_002e:\n    movs r0, #0\n    movs.w r1, #-1\n    str r0, [r1]\n    b L_open_cfw_runtime_am067_d4dca_002e\nL_open_cfw_runtime_am067_d4dca_0038:\n    cmp r4, #0\n    bne L_open_cfw_runtime_am067_d4dca_0068\n    ldr.w r0, [pc, #0x43c]\n    str r0, [sp, #8]\n    ldr.w r0, [pc, #0x440]\n    str r0, [sp, #4]\n    ldr.w r0, [pc, #0x420]\n    str r0, [sp]\n    ldr.w r3, [pc, #0x430]\n    movs r2, #0x54\n    ldr.w r1, [pc, #0x41c]\n    movs r0, #3\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am067_addr_0044d25c\n    bl .\nL_open_cfw_runtime_am067_d4dca_005e:\n    movs r0, #0\n    movs.w r1, #-1\n    str r0, [r1]\n    b L_open_cfw_runtime_am067_d4dca_005e\nL_open_cfw_runtime_am067_d4dca_0068:\n    adds.w r0, r5, #0x1c\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am067_addr_004d4666\n    bl .\n    ldr r0, [r5, #0xc]\n    cmp r0, #0\n    bne L_open_cfw_runtime_am067_d4dca_0082\n    adds.w r0, r5, #0x1c\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am067_addr_004d4696\n    bl .\n    movs r0, #0\n    b L_open_cfw_runtime_am067_d4dca_00a4\nL_open_cfw_runtime_am067_d4dca_0082:\n    movs r2, r6\n    movs r1, r4\n    movs r0, r5\n    ldr r3, [r5]\n    ldr r3, [r3, #0xc]\n    blx r3\n    movs r4, r0\n    cmp r4, #0\n    beq L_open_cfw_runtime_am067_d4dca_009a\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am067_addr_004d53c6\n    bl .\nL_open_cfw_runtime_am067_d4dca_009a:\n    adds.w r0, r5, #0x1c\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am067_addr_004d4696\n    bl .\n    movs r0, r4\nL_open_cfw_runtime_am067_d4dca_00a4:\n    add sp, #0x10\n    pop {r4, r5, r6, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM067_D4E72_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am067_d4e72(void)
{
    __asm__ volatile(
        "    push {r0, r1, r2, r3, r4, r5, r6, lr}\n    movs r5, r0\n    movs r4, r1\n    movs r6, r2\n    cmp r4, #0\n    bne L_open_cfw_runtime_am067_d4e72_0038\n    ldr.w r0, [pc, #0x3c4]\n    str r0, [sp, #8]\n    ldr.w r0, [pc, #0x3cc]\n    str r0, [sp, #4]\n    ldr.w r0, [pc, #0x3a8]\n    str r0, [sp]\n    ldr.w r3, [pc, #0x3c4]\n    movs r2, #0x6c\n    ldr.w r1, [pc, #0x3a4]\n    movs r0, #3\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am067_addr_0044d25c\n    bl .\nL_open_cfw_runtime_am067_d4e72_002e:\n    movs r0, #0\n    movs.w r1, #-1\n    str r0, [r1]\n    b L_open_cfw_runtime_am067_d4e72_002e\nL_open_cfw_runtime_am067_d4e72_0038:\n    adds.w r0, r5, #0x1c\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am067_addr_004d4666\n    bl .\n    movs r1, r6\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am067_addr_004d5400\n    bl .\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am067_addr_004d5312\n    bl .\n    cmp r0, #0\n    bne L_open_cfw_runtime_am067_d4e72_006e\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am067_addr_004d536a\n    bl .\n    cmp r0, #0\n    beq L_open_cfw_runtime_am067_d4e72_006e\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am067_addr_004d5396\n    bl .\n    movs r1, r6\n    ldr r2, [r5, #0x18]\n    blx r2\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am067_addr_004d54da\n    bl .\nL_open_cfw_runtime_am067_d4e72_006e:\n    adds.w r0, r5, #0x1c\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am067_addr_004d4696\n    bl .\n    pop {r0, r1, r2, r3, r4, r5, r6, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM067_D4EEA_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am067_d4eea(void)
{
    __asm__ volatile(
        "    push {r0, r1, r2, r3, r4, r5, r6, lr}\n    movs r5, r0\n    movs r4, r1\n    movs r6, r2\n    cmp r5, #0\n    bne L_open_cfw_runtime_am067_d4eea_0038\n    ldr.w r0, [pc, #0x34c]\n    str r0, [sp, #8]\n    ldr.w r0, [pc, #0x330]\n    str r0, [sp, #4]\n    ldr.w r0, [pc, #0x330]\n    str r0, [sp]\n    ldr.w r3, [pc, #0x350]\n    movs r2, #0x7d\n    ldr.w r1, [pc, #0x32c]\n    movs r0, #3\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am067_addr_0044d25c\n    bl .\nL_open_cfw_runtime_am067_d4eea_002e:\n    movs r0, #0\n    movs.w r1, #-1\n    str r0, [r1]\n    b L_open_cfw_runtime_am067_d4eea_002e\nL_open_cfw_runtime_am067_d4eea_0038:\n    cmp r4, #0\n    bne L_open_cfw_runtime_am067_d4eea_0068\n    ldr.w r0, [pc, #0x31c]\n    str r0, [sp, #8]\n    ldr.w r0, [pc, #0x320]\n    str r0, [sp, #4]\n    ldr.w r0, [pc, #0x300]\n    str r0, [sp]\n    ldr.w r3, [pc, #0x320]\n    movs r2, #0x7e\n    ldr.w r1, [pc, #0x2fc]\n    movs r0, #3\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am067_addr_0044d25c\n    bl .\nL_open_cfw_runtime_am067_d4eea_005e:\n    movs r0, #0\n    movs.w r1, #-1\n    str r0, [r1]\n    b L_open_cfw_runtime_am067_d4eea_005e\nL_open_cfw_runtime_am067_d4eea_0068:\n    adds.w r0, r5, #0x1c\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am067_addr_004d4666\n    bl .\n    ldr r0, [r5, #8]\n    cmp r0, #0\n    bne L_open_cfw_runtime_am067_d4eea_0082\n    adds.w r0, r5, #0x1c\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am067_addr_004d4696\n    bl .\n    movs r0, #0\n    b L_open_cfw_runtime_am067_d4eea_00a2\nL_open_cfw_runtime_am067_d4eea_0082:\n    movs r2, r6\n    movs r1, r4\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am067_d51c0\n    bl .\n    movs r4, r0\n    cmp r4, #0\n    beq L_open_cfw_runtime_am067_d4eea_0098\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am067_addr_004d53c6\n    bl .\nL_open_cfw_runtime_am067_d4eea_0098:\n    adds.w r0, r5, #0x1c\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am067_addr_004d4696\n    bl .\n    movs r0, r4\nL_open_cfw_runtime_am067_d4eea_00a2:\n    add sp, #0x10\n    pop {r4, r5, r6, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM067_D4F90_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am067_d4f90(void)
{
    __asm__ volatile(
        "    push {r1, r2, r3, r4, r5, r6, r7, lr}\n    movs r4, r0\n    movs r5, r1\n    movs r7, r2\n    cmp r4, #0\n    bne L_open_cfw_runtime_am067_d4f90_0038\n    ldr.w r0, [pc, #0x2a4]\n    str r0, [sp, #8]\n    ldr.w r0, [pc, #0x28c]\n    str r0, [sp, #4]\n    ldr.w r0, [pc, #0x288]\n    str r0, [sp]\n    ldr.w r3, [pc, #0x2b0]\n    movs r2, #0x95\n    ldr.w r1, [pc, #0x284]\n    movs r0, #3\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am067_addr_0044d25c\n    bl .\nL_open_cfw_runtime_am067_d4f90_002e:\n    movs r0, #0\n    movs.w r1, #-1\n    str r0, [r1]\n    b L_open_cfw_runtime_am067_d4f90_002e\nL_open_cfw_runtime_am067_d4f90_0038:\n    cmp r5, #0\n    bne L_open_cfw_runtime_am067_d4f90_0068\n    ldr.w r0, [pc, #0x274]\n    str r0, [sp, #8]\n    ldr.w r0, [pc, #0x27c]\n    str r0, [sp, #4]\n    ldr.w r0, [pc, #0x258]\n    str r0, [sp]\n    ldr.w r3, [pc, #0x280]\n    movs r2, #0x96\n    ldr.w r1, [pc, #0x254]\n    movs r0, #3\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am067_addr_0044d25c\n    bl .\nL_open_cfw_runtime_am067_d4f90_005e:\n    movs r0, #0\n    movs.w r1, #-1\n    str r0, [r1]\n    b L_open_cfw_runtime_am067_d4f90_005e\nL_open_cfw_runtime_am067_d4f90_0068:\n    adds.w r0, r4, #0x1c\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am067_addr_004d4666\n    bl .\n    movs r0, #0\n    ldr r0, [r4, #0xc]\n    cmp r0, #0\n    beq L_open_cfw_runtime_am067_d4f90_009c\n    movs r2, r7\n    movs r1, r5\n    movs r0, r4\n    ldr r3, [r4]\n    ldr r3, [r3, #0xc]\n    blx r3\n    movs r6, r0\n    cmp r6, #0\n    beq L_open_cfw_runtime_am067_d4f90_009c\n    movs r0, r6\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am067_addr_004d53c6\n    bl .\n    adds.w r0, r4, #0x1c\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am067_addr_004d4696\n    bl .\n    movs r0, r6\n    b L_open_cfw_runtime_am067_d4f90_0102\nL_open_cfw_runtime_am067_d4f90_009c:\n    ldr r0, [r4, #8]\n    cmp r0, #0\n    bne L_open_cfw_runtime_am067_d4f90_00ae\n    adds.w r0, r4, #0x1c\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am067_addr_004d4696\n    bl .\n    movs r0, #0\n    b L_open_cfw_runtime_am067_d4f90_0102\nL_open_cfw_runtime_am067_d4f90_00ae:\n    movs r2, r7\n    movs r1, r5\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am067_d51c0\n    bl .\n    movs r5, r0\n    cmp r5, #0\n    bne L_open_cfw_runtime_am067_d4f90_00ca\n    adds.w r0, r4, #0x1c\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am067_addr_004d4696\n    bl .\n    movs r0, #0\n    b L_open_cfw_runtime_am067_d4f90_0102\nL_open_cfw_runtime_am067_d4f90_00ca:\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am067_addr_004d5396\n    bl .\n    movs r1, r7\n    ldr r2, [r4, #0x14]\n    blx r2\n    uxtb r0, r0\n    cmp r0, #0\n    bne L_open_cfw_runtime_am067_d4f90_00f2\n    movs r2, r7\n    movs r1, r5\n    movs r0, r4\n    ldr r3, [r4]\n    ldr r3, [r3, #0x14]\n    blx r3\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am067_addr_004d54da\n    bl .\n    movs r5, #0\n    b L_open_cfw_runtime_am067_d4f90_00f8\nL_open_cfw_runtime_am067_d4f90_00f2:\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am067_addr_004d53c6\n    bl .\nL_open_cfw_runtime_am067_d4f90_00f8:\n    adds.w r0, r4, #0x1c\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am067_addr_004d4696\n    bl .\n    movs r0, r5\nL_open_cfw_runtime_am067_d4f90_0102:\n    pop {r1, r2, r3, r4, r5, r6, r7, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM067_D5094_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am067_d5094(void)
{
    __asm__ volatile(
        "    push {r0, r1, r2, r3, r4, r5, r6, lr}\n    movs r5, r0\n    movs r4, r1\n    movs r6, r2\n    cmp r5, #0\n    bne L_open_cfw_runtime_am067_d5094_002e\n    ldr r0, [pc, #0x1a0]\n    str r0, [sp, #8]\n    ldr r0, [pc, #0x188]\n    str r0, [sp, #4]\n    ldr r0, [pc, #0x188]\n    str r0, [sp]\n    ldr r3, [pc, #0x1b4]\n    movs r2, #0xd3\n    ldr r1, [pc, #0x188]\n    movs r0, #3\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am067_addr_0044d25c\n    bl .\nL_open_cfw_runtime_am067_d5094_0024:\n    movs r0, #0\n    movs.w r1, #-1\n    str r0, [r1]\n    b L_open_cfw_runtime_am067_d5094_0024\nL_open_cfw_runtime_am067_d5094_002e:\n    cmp r4, #0\n    bne L_open_cfw_runtime_am067_d5094_0054\n    ldr r0, [pc, #0x17c]\n    str r0, [sp, #8]\n    ldr r0, [pc, #0x184]\n    str r0, [sp, #4]\n    ldr r0, [pc, #0x164]\n    str r0, [sp]\n    ldr r3, [pc, #0x190]\n    movs r2, #0xd4\n    ldr r1, [pc, #0x164]\n    movs r0, #3\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am067_addr_0044d25c\n    bl .\nL_open_cfw_runtime_am067_d5094_004a:\n    movs r0, #0\n    movs.w r1, #-1\n    str r0, [r1]\n    b L_open_cfw_runtime_am067_d5094_004a\nL_open_cfw_runtime_am067_d5094_0054:\n    adds.w r0, r5, #0x1c\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am067_addr_004d4666\n    bl .\n    movs r2, r6\n    movs r1, r4\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am067_d511c\n    bl .\n    adds.w r0, r5, #0x1c\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am067_addr_004d4696\n    bl .\n    pop {r0, r1, r2, r3, r4, r5, r6, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM067_D5104_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am067_d5104(void)
{
    __asm__ volatile(
        "    ldr r0, [r0, #8]\n    cmp r0, #0\n    beq L_open_cfw_runtime_am067_d5104_000a\n    movs r0, #1\n    b L_open_cfw_runtime_am067_d5104_000c\nL_open_cfw_runtime_am067_d5104_000a:\n    movs r0, #0\nL_open_cfw_runtime_am067_d5104_000c:\n    uxtb r0, r0\n    bx lr\n"
    );
}
#endif

#if defined(OPEN_CFW_AM067_D5114_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am067_d5114(void)
{
    __asm__ volatile(
        "    cmp r0, #0\n    beq L_open_cfw_runtime_am067_d5114_0006\n    str r1, [r0, #0x24]\nL_open_cfw_runtime_am067_d5114_0006:\n    bx lr\n"
    );
}
#endif

#if defined(OPEN_CFW_AM067_D511C_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am067_d511c(void)
{
    __asm__ volatile(
        "    push {r4, r5, r6, lr}\n    movs r5, r0\n    movs r6, r2\n    movs r2, r6\n    movs r0, r5\n    ldr r3, [r5]\n    ldr r3, [r3, #0xc]\n    blx r3\n    movs r4, r0\n    cmp r4, #0\n    beq L_open_cfw_runtime_am067_d511c_0054\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am067_addr_004d5312\n    bl .\n    cmp r0, #0\n    bne L_open_cfw_runtime_am067_d511c_0040\n    movs r2, r6\n    movs r1, r4\n    movs r0, r5\n    ldr r3, [r5]\n    ldr r3, [r3, #0x14]\n    blx r3\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am067_addr_004d5396\n    bl .\n    movs r1, r6\n    ldr r2, [r5, #0x18]\n    blx r2\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am067_addr_004d54da\n    bl .\n    b L_open_cfw_runtime_am067_d511c_0054\nL_open_cfw_runtime_am067_d511c_0040:\n    movs r1, #1\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am067_addr_004d533e\n    bl .\n    movs r2, r6\n    movs r1, r4\n    movs r0, r5\n    ldr r3, [r5]\n    ldr r3, [r3, #0x14]\n    blx r3\nL_open_cfw_runtime_am067_d511c_0054:\n    pop {r4, r5, r6, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM067_D5172_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am067_d5172(void)
{
    __asm__ volatile(
        "    push {r2, r3, r4, r5, r6, lr}\n    movs r5, r0\n    movs r6, r1\n    movs r1, r6\n    movs r0, r5\n    ldr r2, [r5]\n    ldr r2, [r2, #0x20]\n    blx r2\n    movs r4, r0\n    cmp r4, #0\n    bne L_open_cfw_runtime_am067_d5172_002c\n    ldr r0, [pc, #0xdc]\n    str r0, [sp]\n    ldr r3, [pc, #0xdc]\n    movw r2, #0x14b\n    ldr r1, [pc, #0xa8]\n    movs r0, #3\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am067_addr_0044d25c\n    bl .\n    movs r0, #0\n    b L_open_cfw_runtime_am067_d5172_004c\nL_open_cfw_runtime_am067_d5172_002c:\n    movs r2, r6\n    movs r1, r4\n    movs r0, r5\n    ldr r3, [r5]\n    ldr r3, [r3, #0x14]\n    blx r3\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am067_addr_004d5396\n    bl .\n    movs r1, r6\n    ldr r2, [r5, #0x18]\n    blx r2\n    movs r0, r4\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am067_addr_004d54da\n    bl .\n    movs r0, #1\nL_open_cfw_runtime_am067_d5172_004c:\n    pop {r1, r2, r4, r5, r6, pc}\n"
    );
}
#endif

#if defined(OPEN_CFW_AM067_D51C0_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am067_d51c0(void)
{
    __asm__ volatile(
        "    push {r1, r2, r3, r4, r5, r6, r7, lr}\n    movs r5, r0\n    movs r4, r1\n    movs r6, r2\n    movs r3, r6\n    movs r2, #0\n    movs r1, r4\n    movs r0, r5\n    ldr r7, [r5]\n    ldr r7, [r7, #0x24]\n    blx r7\n    movs r1, r0\n    uxtb r1, r1\n    cmp r1, #1\n    bne L_open_cfw_runtime_am067_d51c0_0048\n    ldr r0, [r5, #8]\n    str r0, [sp, #8]\n    str r4, [sp, #4]\n    ldr r0, [pc, #0x88]\n    str r0, [sp]\n    ldr r3, [pc, #0x88]\n    movw r2, #0x159\n    ldr r1, [pc, #0x4c]\n    movs r0, #3\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am067_addr_0044d25c\n    bl .\n    movs r0, #0\n    b L_open_cfw_runtime_am067_d51c0_006a\nL_open_cfw_runtime_am067_d51c0_003a:\n    movs r3, r6\n    movs r2, #0\n    movs r1, r4\n    movs r0, r5\n    ldr r7, [r5]\n    ldr r7, [r7, #0x24]\n    blx r7\nL_open_cfw_runtime_am067_d51c0_0048:\n    uxtb r0, r0\n    cmp r0, #2\n    bne L_open_cfw_runtime_am067_d51c0_005e\n    movs r1, r6\n    movs r0, r5\n    .reloc ., R_ARM_THM_CALL, open_cfw_runtime_am067_d5172\n    bl .\n    cmp r0, #0\n    bne L_open_cfw_runtime_am067_d51c0_003a\n    movs r0, #0\n    b L_open_cfw_runtime_am067_d51c0_006a\nL_open_cfw_runtime_am067_d51c0_005e:\n    movs r2, r6\n    movs r1, r4\n    movs r0, r5\n    ldr r3, [r5]\n    ldr r3, [r3, #0x10]\n    blx r3\nL_open_cfw_runtime_am067_d51c0_006a:\n    pop {r1, r2, r3, r4, r5, r6, r7, pc}\n"
    );
}
#endif
