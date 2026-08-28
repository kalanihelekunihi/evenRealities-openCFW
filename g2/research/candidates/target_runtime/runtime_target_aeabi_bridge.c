/*
 * SPDX-License-Identifier: MIT
 *
 * Exact-symbol bridge to the existing division-free ARM EABI provider in
 * components/apollo_main/core_overlay/aeabi_divmod.c.
 */

#if !defined(__arm__) && !defined(__thumb__)
#error "the __aeabi_uldivmod bridge is target-only"
#endif

extern void open_cfw_aeabi_uldivmod(void);

__attribute__((used, naked))
void __aeabi_uldivmod(void)
{
    __asm__ volatile("b.w open_cfw_aeabi_uldivmod");
}
