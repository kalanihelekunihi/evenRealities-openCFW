/* SPDX-License-Identifier: MIT */
/* Complete board clock hook at package 0x39c64. */
extern int open_cfw_gx8002_stage1_clock_trim(void);
extern void open_cfw_gx8002_stage1_397f4(unsigned);
void spl_board_clk_init(void)
{
    if (open_cfw_gx8002_stage1_clock_trim() == 0)
        open_cfw_gx8002_stage1_397f4(1);
}
