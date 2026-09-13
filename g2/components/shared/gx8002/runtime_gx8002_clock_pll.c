/* SPDX-License-Identifier: MIT
 * Use the authenticated NationalChip PLL configuration implementation.
 */
#include <stdint.h>
#include <stddef.h>
#include <clk_priv.h>
void open_cfw_gx8002_clock_pll(GX_CLOCK_PLL *pll)
{
    _clk_set_pll(pll);
}
