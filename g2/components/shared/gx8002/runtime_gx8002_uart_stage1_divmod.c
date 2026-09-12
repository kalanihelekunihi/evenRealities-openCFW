/* SPDX-License-Identifier: MIT */
/*
 * Reviewed unsigned divide/modulo leaves for the GX8002 UART boot stage 1
 * (IRAM) image, plus its init-sequence no-op placeholder.
 *
 * These are clean-room C implementations of the restoring-division algorithm
 * identified in the pinned NationalChip grus SDK
 * (arch/soc/grus/spl/spl.c, uint32_divmodsi4/uint32_div/uint32_mod at commit
 * 8bf9ee5cb6eeb226011e61c15fa4981b83b93bd5, GPL-2.0+), which the UART-boot
 * stage 1 reuses for its baud-rate divisor computation. No SDK text is
 * reproduced here; the bodies below were written from the decoded stock
 * control flow and verified by decoded-target execution comparison against
 * the stock bytes plus an independent arithmetic oracle. See
 * docs/research/gx8002-uart-stage1-divmod-source.md.
 *
 * Stock envelopes (package offsets into firmware_codec.bin):
 *   open_cfw_gx8002_uart_stage1_udiv      runtime 0x1000013c, package 0x18c, 66 bytes
 *   open_cfw_gx8002_uart_stage1_umod      runtime 0x10000180, package 0x1d0, 58 bytes
 *   open_cfw_gx8002_uart_stage1_clear_bss runtime 0x10000138, package 0x188, 4 bytes
 *
 * The clear_bss placeholder is a bare return, matching the position and body
 * of upstream spl_start.S spl_clear_bss (MIT, same SDK commit): the SPL stage
 * never clears BSS through it, so no BSS-clearing behavior is claimed.
 */
#include <stdint.h>

uint32_t open_cfw_gx8002_uart_stage1_udiv(uint32_t num, uint32_t den)
{
    uint32_t bit = 1u;
    uint32_t res = 0u;

    if (den < num && (int32_t)den >= 0) {
        do {
            den <<= 1;
            bit <<= 1;
        } while (den < num && bit != 0u && (int32_t)den >= 0);
    }
    while (bit != 0u) {
        if (num >= den) {
            num -= den;
            res |= bit;
        }
        bit >>= 1;
        den >>= 1;
    }
    return res;
}

uint32_t open_cfw_gx8002_uart_stage1_umod(uint32_t num, uint32_t den)
{
    uint32_t bit = 1u;

    if (den < num && (int32_t)den >= 0) {
        do {
            den <<= 1;
            bit <<= 1;
        } while (den < num && bit != 0u && (int32_t)den >= 0);
    }
    while (bit != 0u) {
        if (num >= den) {
            num -= den;
        }
        bit >>= 1;
        den >>= 1;
    }
    return num;
}

void open_cfw_gx8002_uart_stage1_clear_bss(void)
{
}
