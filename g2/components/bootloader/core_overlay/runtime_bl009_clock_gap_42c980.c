/* SPDX-License-Identifier: MIT */
/* Clean-room in-place data: eight-byte clock-constant cell at 0x0042C980
 * between the hardware event service (ends 0x0042C980) and the hardware
 * configuration transaction (starts 0x0042C988).
 *
 * - 0x0042C980: 0x05B8D800 = 96,000,000, the 96 MHz Apollo clock
 *   dividend. Original consumer 0x0042C278 (`ldr.w r6, [pc, #0x704]`)
 *   feeds it to `udiv r2, r6, r0` in the clock-divider search.
 * - 0x0042C984: 0x0003D090 = 250,000, the companion divisor constant
 *   (original consumers 0x0042C39A / 0x0042C3AA).
 * The already-routed clock-divider successor
 * (runtime_hw_clock_encode_42c26a.c) embeds the decimal equivalents
 * 96000000/250000, so these cells are original-layout literal residue
 * with no live referent in the source build.
 */
typedef __UINT32_TYPE__ open_cfw_bl009_u32;

struct open_cfw_bl009_gap_42c980 {
    open_cfw_bl009_u32 clock_hz;
    open_cfw_bl009_u32 clock_divisor;
};

__attribute__((used))
const struct open_cfw_bl009_gap_42c980
open_cfw_bootloader_bl009_gap_42c980 = { 0x05B8D800u, 0x0003D090u };
