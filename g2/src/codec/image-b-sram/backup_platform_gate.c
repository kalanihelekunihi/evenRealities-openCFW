/* SPDX-License-Identifier: MIT
 * Image-B 0x10003be8 gate wrapper. Pinned NationalChip source
 * arch/soc/grus/spl/spl_clk.c calls the two static-inline clk_priv.h
 * operations in this order; the native body has their two-stage CFG.
 */
#include <stdint.h>
#include <stddef.h>
/* The SDK's gx_clock.h selector requires generated autoconf.h. Both the
 * pinned gx8002b Grus config and SDK Makefile select the v2 clock header. */
#include <driver/gx_clock/gx_clock_v2.h>
#define __GX_CLOCK_H__
#pragma GCC diagnostic push
#pragma GCC diagnostic ignored "-Wsign-compare"
#pragma GCC diagnostic ignored "-Wincompatible-pointer-types"
#include <clk_priv.h>
#pragma GCC diagnostic pop

/* Stock 0x1001295C (gx8002_platform_gate_switches) */
void gx8002_image_b_platform_gate_10003be8(uint32_t module, uint32_t enable)
{
    _clk_set_high_gate((GX_CLOCK_MODULE)module, enable);
    (void)_clk_set_all_gate((GX_CLOCK_MODULE)module, enable);
}
