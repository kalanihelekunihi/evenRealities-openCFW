/* SPDX-License-Identifier: MIT */
#include <driver/gx_clock.h>
extern GX_CLOCK_PLL pll;
extern int stage2_trim_done;
/* Recovered backup oscillator path. Offsets are relative to the divider
 * sampled once at entry, including if the PLL setter mutates its descriptor.
 * The stock initializer waits forever after the fifth unsuccessful attempt. */
void open_cfw_gx8002_backup_pll_retry(void)
{
    static const int adjustment[] = {0, 10, 15, -10, -15};
    stage2_trim_done = 1;
    unsigned int original = pll.pll_div_fb;
    for (unsigned int i = 0; i < sizeof(adjustment) / sizeof(adjustment[0]); ++i) {
        pll.pll_div_fb = original + (unsigned int)adjustment[i];
        if (gx_clock_set_pll_no_block(&pll, 40) == 0)
            return;
    }
    for (;;) { }
}
