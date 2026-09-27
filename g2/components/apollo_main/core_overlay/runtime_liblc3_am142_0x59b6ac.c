/*
 * SPDX-License-Identifier: MIT
 *
 * Source-owned AM142 flag helpers at 0x0059b6ac.
 */

__attribute__((used, naked))
void open_cfw_runtime_am142_0x0059b6ac(void)
{
    __asm__ volatile(
        "movs r0, #1\n"
        "b L_open_cfw_runtime_am142_0x0059b6ac_0006\n"
        "movs r0, #0\n"
        "L_open_cfw_runtime_am142_0x0059b6ac_0006:\n"
        "uxtb r0, r0\n"
        "bx lr\n"
        "ldr r0, [r0]\n"
        "lsrs r0, r0, #4\n"
        "ands r0, r0, #1\n"
        "uxtb r0, r0\n"
        "bx lr\n"
        "ldr r0, [r0]\n"
        "lsrs r0, r0, #5\n"
        "ands r0, r0, #1\n"
        "uxtb r0, r0\n"
        "bx lr\n"
        "ldr r1, [r0]\n"
    );
}
