/* SPDX-License-Identifier: MIT
 * Recovered stock helper ABI: parameter pointer in r0, base address in r1.
 * Matches the pinned SDK __module_get_div calculation without aggregate spills.
 */
#include <stdint.h>
#include <stddef.h>
#include <clk_priv.h>
unsigned int open_cfw_gx8002_clock_divider(const GX_CLOCK_MODULE_PARAM *param,
                                         unsigned int base)
{
    const GX_CLOCK_DIV *divider = param->div;
    if (!divider)
        return 0;
    unsigned int address = base + divider->addr;
    unsigned int shift = divider->offs;
    unsigned int value = *(volatile uint32_t *)(uintptr_t)address;
    value = (value >> shift) & divider->mask;
    return value == 0 ? 0 : value + 1;
}
