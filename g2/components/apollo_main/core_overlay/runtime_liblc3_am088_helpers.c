/*
 * SPDX-License-Identifier: MIT
 *
 * Source-owned exact helpers from the AM-088 retained island.
 */

#if defined(OPEN_CFW_AM088_0X00513E2E_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am088_0x00513e2e(void)
{
    __asm__ volatile(
        "L_am088_start:\n"
        "ldr r2, [sp, #4]\n"
        ".reloc ., R_ARM_THM_JUMP11, open_cfw_runtime_am088_branch_513d88\n"
        "b .\n"
        "cmp.w fp, #0\n"
        "bne.n L_am088_use_zero\n"
        "mov.w r3, #0x2000\n"
        "mov.w ip, #0x800000\n"
        ".reloc ., R_ARM_THM_JUMP11, open_cfw_runtime_am088_branch_513dba\n"
        "b .\n"
        "L_am088_use_zero:\n"
        "cmp.w fp, #1\n"
        "bne.n L_am088_start\n"
        "movs r3, #0\n"
        "mov ip, r0\n"
        ".reloc ., R_ARM_THM_JUMP11, open_cfw_runtime_am088_branch_513dba\n"
        "b .\n"
        "push {r4, lr}\n"
        "mov r4, r0\n"
        "mov r1, r4\n"
        "movs r0, #1\n"
    );
}
#endif
