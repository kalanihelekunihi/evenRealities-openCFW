/* SPDX-License-Identifier: MIT */
/* Adapter to pinned NationalChip GRUS clock source. Full dependency and
 * register-table qualification is required before firmware admission. */
#include <stddef.h>
#include <stdint.h>
#include <clk_priv.h>

/* Keep the lookup's public input contract visible to interprocedural passes.
 * Stock callers can pass NULL; the gate's local stack object alone would let
 * the compiler specialize the static upstream helper and remove that check. */
int open_cfw_gx8002_clock_lookup(unsigned int module, GX_CLOCK_MODULE_INFO *info)
{
    return __module_get_info((GX_CLOCK_MODULE)module, info);
}

void open_cfw_gx8002_platform_gate(unsigned int module, unsigned int enable)
{
    _clk_set_high_gate((GX_CLOCK_MODULE)module, enable);
    (void)_clk_set_all_gate((GX_CLOCK_MODULE)module, enable);
}
