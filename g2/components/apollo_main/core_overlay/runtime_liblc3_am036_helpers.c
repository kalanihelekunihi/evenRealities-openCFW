/*
 * SPDX-License-Identifier: MIT
 *
 * Source-owned exact helper thunk from the AM-036 rejected-envelope entry.
 */

#if defined(OPEN_CFW_AM036_48949C_ONLY)
__attribute__((used, naked))
void open_cfw_runtime_am036_48949c(void)
{
    __asm__ volatile(
        "movs r2, #0\n"
        ".reloc ., R_ARM_THM_JUMP24, open_cfw_runtime_am036_target_4d555c\n"
        "b.w .\n"
        "movs r0, r0\n"
    );
}
#endif
