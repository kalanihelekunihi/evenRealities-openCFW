/*
 * SPDX-License-Identifier: MIT
 *
 * Source-owned AM142 stack accumulator fragment at 0x0059c866.
 */

__attribute__((used, naked))
void open_cfw_runtime_am142_0x0059c866(void)
{
    __asm__ volatile(
        "adds r1, r0, r1\n"
        "str r1, [sp, #0x20]\n"
        "ldr r0, [sp, #0x10]\n"
        "adds.w r0, r0, sl\n"
        "str r0, [sp, #0x14]\n"
        "ldr r0, [sp, #0xc]\n"
        "adds r0, r0, r5\n"
    );
}
