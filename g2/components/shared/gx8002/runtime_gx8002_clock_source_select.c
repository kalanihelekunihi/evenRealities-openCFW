/* SPDX-License-Identifier: MIT
 * Recovered _clk_set_source ABI with the separately reconstructed register helper.
 */
#include <stdint.h>
#include <stddef.h>
#include <clk_priv.h>
/* Clock ABI uses bit offsets 0..31. Unsigned value avoids signed-shift UB. */
__attribute__((noinline)) void open_cfw_clock_register_set(unsigned int address,
        unsigned int offset, unsigned int value, unsigned int mask)
{
    volatile uint32_t *reg=(volatile uint32_t *)(uintptr_t)address;
    *reg=(*reg & ~(mask<<offset)) | (value<<offset);
}
void open_cfw_gx8002_clock_source_select(GX_CLOCK_SOURCE_TABLE *table)
{
    open_cfw_clock_register_set(GX_REG_BASE_PMU_CONFIG + GX_CLOCK_PMU_SOURCE_SEL,
                               table->source, table->clk, 1);
}
