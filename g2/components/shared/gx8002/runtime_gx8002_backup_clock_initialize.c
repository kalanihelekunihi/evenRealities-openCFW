/* SPDX-License-Identifier: MIT */
#include <driver/gx_clock.h>

extern GX_CLOCK_PLL pll;
extern int stage2_trim_done;
extern GX_CLOCK_SOURCE_TABLE clk_src_xtal_table[10];
extern GX_CLOCK_SOURCE_TABLE clk_src_osc_table[10];
extern volatile unsigned int open_cfw_gx8002_saved_clock_gates;
extern int open_cfw_gx8002_backup_preserve_memory(void);
extern int open_cfw_gx8002_backup_trim_state(void);
extern void open_cfw_gx8002_backup_ldo_control(unsigned int control);
extern void open_cfw_gx8002_backup_pll_retry(void);
extern void open_cfw_gx8002_backup_clock_module_initialize(void);
extern void open_cfw_gx8002_backup_clock_dividers(void);

/* Complete backup clk_init control flow, recovered from 0x3bbd4..0x3be14.
 * The return value of the start predicate is retained across all setup calls.
 * Only value 1 selects resume; other nonzero values skip source selection. */
void open_cfw_gx8002_backup_clock_initialize(void)
{
    open_cfw_gx8002_backup_ldo_control(2);
    gx_clock_set_div(CLOCK_MODULE_SRAM, 2);
    int start = open_cfw_gx8002_backup_preserve_memory();
    if (start == 0) {
        GX_CLOCK_SOURCE_TABLE *table;
        if (open_cfw_gx8002_backup_trim_state() == 1) {
            open_cfw_gx8002_backup_pll_retry();
            table = clk_src_osc_table;
        } else {
            table = clk_src_xtal_table;
        }
        for (unsigned int i = 0; i < 10; ++i)
            gx_clock_set_source(&table[i]);
    } else if (start == 1) {
        GX_CLOCK_SOURCE_TABLE resume[2];
        resume[0].source = CLOCK_SOURCE_24M;
        resume[0].clk = 0;
        resume[1].source = CLOCK_SOURCE_24M_PLL;
        resume[1].clk = 1;
        if (stage2_trim_done == 1)
            gx_clock_set_pll(&pll);
        gx_clock_set_source(&resume[0]);
        gx_clock_set_source(&resume[1]);
    }
    open_cfw_gx8002_backup_clock_module_initialize();
    open_cfw_gx8002_backup_clock_dividers();
    if (start == 1) {
        for (unsigned int module = CLOCK_MODULE_AUDIO_PLAY;
             module < CLOCK_MODULE_MAX; ++module)
            gx_clock_set_module_enable(module,
                (open_cfw_gx8002_saved_clock_gates >> module) & 1);
    }
    gx_clock_set_module_enable(CLOCK_MODULE_HW_I2C, 1);
    *(volatile unsigned int *)0xa0005084 &= ~1u;
    *(volatile unsigned int *)0xa0005060 &= ~2u;
    open_cfw_gx8002_backup_ldo_control(2);
}
