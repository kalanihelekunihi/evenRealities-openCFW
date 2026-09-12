/* SPDX-License-Identifier: MIT */
/*
 * Reviewed polled-UART leaves for the GX8002 UART boot stage 1 (IRAM) image.
 *
 * Clean-room C implementing the decoded stock behavior of three tiny
 * register-level UART routines, identified against the pinned NationalChip
 * grus SDK `arch/soc/grus/spl/spl_uart.c` (`serial_put`, `serial_try_get`,
 * `serial_get_char` at commit 8bf9ee5cb6eeb226011e61c15fa4981b83b93bd5,
 * which carries no per-file license header and is used here under the SDK
 * repo-level MIT LICENSE). Only numeric register offsets, bit positions,
 * and the call/return conventions cross the boundary; the bodies below were
 * written from the decoded stock control flow and are verified by
 * decoded-target execution comparison against the stock bytes plus an
 * independent oracle. The GPL-licensed SDK headers (`common.h`, `spl.h`)
 * are deliberately not used: no SDK text is reproduced. See
 * docs/research/gx8002-uart-stage1-serial-source.md.
 *
 * The UART register block base is kept in the stage-1 data word at
 * 0x20002014 (the linked image's `dw_serialbase` variable: every stage-1
 * UART routine reads it through its own literal pool, so each envelope
 * below is self-contained). The line-status register is at block offset
 * 0x14: bit 6 is transmitter-empty (polled before every THR write) and
 * bit 0 is data-ready (polled/tested before every RBR read); data is at
 * block offset 0x0 (word write for transmit, word read narrowed to a byte
 * for receive on this little-endian core).
 *
 * Stock envelopes (package offsets into firmware_codec.bin):
 *   open_cfw_gx8002_uart_stage1_put      runtime 0x10000584, package 0x5d4, 28 bytes
 *   open_cfw_gx8002_uart_stage1_try_get  runtime 0x10000620, package 0x670, 32 bytes
 *   open_cfw_gx8002_uart_stage1_get_char runtime 0x10000640, package 0x690, 28 bytes
 * (The sibling blocking-write-then-wait leaf at runtime 0x100005a0 lives in
 * runtime_gx8002_uart_stage1_putsync.S: every probed C shape for it
 * compiles to 38 bytes against a 36-byte stock envelope, so that one leaf
 * is reviewed assembly. See the audit.)
 */
#include <stdint.h>

#ifndef GX8002_STAGE1_UART_BASE_CELL
#define GX8002_STAGE1_UART_BASE_CELL ((volatile uint32_t *)0x20002014u)
#endif
#define GX8002_STAGE1_UART_LSR_OFFSET 0x14u
#define GX8002_STAGE1_UART_TEMT_BIT 6u
#define GX8002_STAGE1_UART_DR_BIT 0u

void open_cfw_gx8002_uart_stage1_put(int ch)
{
    uintptr_t base = (uintptr_t)*GX8002_STAGE1_UART_BASE_CELL;
    uintptr_t lsr = base + GX8002_STAGE1_UART_LSR_OFFSET;
    uint32_t state;

    do {
        state = *(volatile uint32_t *)lsr;
    } while (!(state & (1u << GX8002_STAGE1_UART_TEMT_BIT)));
    *(volatile uint32_t *)base = (uint32_t)ch;
}

int open_cfw_gx8002_uart_stage1_try_get(unsigned char *c)
{
    uintptr_t base = (uintptr_t)*GX8002_STAGE1_UART_BASE_CELL;
    uint32_t state = *(volatile uint32_t *)(base + GX8002_STAGE1_UART_LSR_OFFSET);

    if (state & (1u << GX8002_STAGE1_UART_DR_BIT)) {
        *c = (unsigned char)*(volatile uint32_t *)base;
        return 0;
    }
    return -1;
}

int open_cfw_gx8002_uart_stage1_get_char(void)
{
    uintptr_t base = (uintptr_t)*GX8002_STAGE1_UART_BASE_CELL;
    uintptr_t lsr = base + GX8002_STAGE1_UART_LSR_OFFSET;
    uint32_t state;
    uint32_t ch;

    do {
        state = *(volatile uint32_t *)lsr;
    } while (!(state & (1u << GX8002_STAGE1_UART_DR_BIT)));
    ch = *(volatile uint32_t *)base;
    return (int)(ch & 0xffu);
}
