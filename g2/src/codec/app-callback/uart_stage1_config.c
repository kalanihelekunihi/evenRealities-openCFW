/* SPDX-License-Identifier: MIT
 * UART boot stage-1 spl_clk_set_pll_no_block (NationalChip lvp_kws 8bf9ee5c
 * arch/soc/grus/spl/spl_clk.c) at stock 0x10000c9c, with the clk_priv.h
 * _clk_set_pll register sequence: every field is cleared and then set by a
 * separate read-modify-write, as in the stock body. The PLL registers are
 * GX_REG_BASE_HW_I2C (0xa0005000); lock is bit 3 of 0xa0005098.
 *
 * config is GX_CLOCK_PLL: [0] enable, [4] div_in, [5] div_fb, [6] icpsel,
 * [7] bwsel_lpf, [8] vco_subband, [9] div_out, [11] vco_trim.
 */
#include <stdint.h>

extern void gx8002_uart_stage1_railcfg(void);     /* spl_delay_init */
extern uint32_t gx8002_uart_stage1_time_ms(void); /* spl_get_time_ms */

#define PLL_REG(offset) (*(volatile uint32_t *)(uintptr_t)(UINT32_C(0xa0005000) + (offset)))

/* Stock 0x10000C9C */
int32_t gx8002_uart_stage1_uart_config(const uint32_t *config,
                                        uint32_t timeout_ms)
{
    if (config[0] == 0u)
        return 0;

    PLL_REG(0x3c) &= ~UINT32_C(2);            /* disable */
    PLL_REG(0x3c) &= ~UINT32_C(1);            /* reset */

    PLL_REG(0x1c) &= ~UINT32_C(0x3f);
    PLL_REG(0x1c) |= config[4];
    PLL_REG(0x20) &= ~UINT32_C(0xff);
    PLL_REG(0x24) &= ~UINT32_C(0x1f);
    PLL_REG(0x20) |= config[5] & 0xffu;
    PLL_REG(0x24) |= (config[5] >> 8) & 0x1fu;
    PLL_REG(0x28) &= ~UINT32_C(7);
    PLL_REG(0x28) |= config[9];
    PLL_REG(0x2c) &= ~UINT32_C(0x7f);
    PLL_REG(0x2c) |= config[6];
    PLL_REG(0x30) &= ~UINT32_C(7);
    PLL_REG(0x30) |= config[11] & 7u;
    PLL_REG(0x30) &= ~UINT32_C(0x30);
    PLL_REG(0x30) |= config[8] << 4;
    PLL_REG(0x3c) &= ~UINT32_C(4);
    PLL_REG(0x3c) |= (config[7] << 2) & 4u;
    PLL_REG(0x3c) |= UINT32_C(2);             /* enable */
    PLL_REG(0x3c) |= UINT32_C(1);             /* release reset */

    gx8002_uart_stage1_railcfg();
    const uint32_t start = gx8002_uart_stage1_time_ms();
    while ((PLL_REG(0x98) & 8u) == 0u) {
        if (gx8002_uart_stage1_time_ms() - start > timeout_ms)
            return -1;
    }
    return 0;
}
