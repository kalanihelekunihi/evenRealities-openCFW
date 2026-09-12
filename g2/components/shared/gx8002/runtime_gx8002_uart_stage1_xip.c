/* SPDX-License-Identifier: MIT */
/*
 * Reviewed XIP-controller transfer leaves for the GX8002 UART boot
 * stage 1 (IRAM) image.
 *
 * Clean-room C implementing the decoded stock behavior of two
 * register-level flash-transfer routines, identified against the pinned
 * NationalChip grus SDK `arch/soc/grus/include/base_addr.h`
 * (`GX_REG_BASE_XIP = 0xA2000000`, commit
 * 8bf9ee5cb6eeb226011e61c15fa4981b83b93bd5, blob
 * 536d2e51e19f12f3a7f4e354fba53be906e05702; SDK repo-level MIT LICENSE
 * blob 37a1e362999f2040c2c0cda1a3231b6b5913efbf). Only the numeric
 * controller base crosses the boundary; every register offset, control
 * word, poll bit, and the transfer-loop shapes below were written from
 * the decoded stock control flow and are verified by decoded-target
 * execution comparison against the stock bytes plus an independent
 * oracle. No SDK text is reproduced. See
 * docs/research/gx8002-uart-stage1-xip-source.md.
 *
 * Both routines drive the XIP flash controller at 0xA2000000: wait for
 * idle, snapshot the masked idle bit (the stock masks the status with
 * `andi` before testing it, so the snapshot stored into the
 * configuration registers is always zero) into registers 0x08 and 0x4c,
 * issue a command word through the data register, move `len` bytes,
 * then wait for the residual count and idle. The read leaf (control
 * 0xC07, count = len - 1) polls data-ready bit 3, stores each received
 * word narrowed to a byte, and waits on the residual register at 0x24;
 * the write leaf (control 0x407, count = len, count shadow shifted into
 * the mode register) polls transmit-ready bit 1, writes each source
 * byte widened to a word, and waits on the residual register at 0x20.
 *
 * Stock envelopes (package offsets into firmware_codec.bin):
 *   open_cfw_gx8002_uart_stage1_xip_read   runtime 0x100018c0, package 0x1910, 128 bytes
 *   open_cfw_gx8002_uart_stage1_xip_write  runtime 0x10001940, package 0x1990, 128 bytes
 */
#include <stdint.h>

#ifndef GX8002_STAGE1_XIP_BASE
#define GX8002_STAGE1_XIP_BASE ((uintptr_t)0xA2000000u)
#endif
#ifndef GX8002_STAGE1_XIP_UNLOCK
#define GX8002_STAGE1_XIP_UNLOCK ((uintptr_t)0xA20000F4u)
#endif
#define GX8002_STAGE1_XIP_CTRL_WORD_READ 0xC07u
#define GX8002_STAGE1_XIP_CTRL_WORD_WRITE 0x407u
#define GX8002_STAGE1_XIP_BUSY_BIT 0u
#define GX8002_STAGE1_XIP_RX_READY_BIT 3u
#define GX8002_STAGE1_XIP_TX_READY_BIT 1u

static volatile uint32_t *gx8002_stage1_xip_at(uintptr_t offset)
{
    return (volatile uint32_t *)(GX8002_STAGE1_XIP_BASE + offset);
}

void open_cfw_gx8002_uart_stage1_xip_read(uint32_t cmd, unsigned char *dst,
    uint32_t len)
{
    volatile uint32_t *xip = (volatile uint32_t *)GX8002_STAGE1_XIP_BASE;
    volatile uint32_t *unlock = (volatile uint32_t *)GX8002_STAGE1_XIP_UNLOCK;
    uint32_t status;

    do {
        status = xip[0x0Au] & (1u << GX8002_STAGE1_XIP_BUSY_BIT);
    } while (status != 0u);
    xip[0x02u] = status;
    xip[0x13u] = status;
    xip[0x00u] = GX8002_STAGE1_XIP_CTRL_WORD_READ;
    xip[0x01u] = len - 1u;
    xip[0x04u] = 1u;
    xip[0x06u] = status;
    *unlock = status;
    xip[0x02u] = 1u;
    xip[0x18u] = cmd;
    while (len != 0u) {
        do {
            status = xip[0x0Au];
        } while (!(status & (1u << GX8002_STAGE1_XIP_RX_READY_BIT)));
        *dst++ = (unsigned char)xip[0x18u];
        len--;
    }
    while (*gx8002_stage1_xip_at(0x24u)) {
    }
    do {
        status = xip[0x0Au];
    } while (status & (1u << GX8002_STAGE1_XIP_BUSY_BIT));
}

void open_cfw_gx8002_uart_stage1_xip_write(uint32_t cmd,
    const unsigned char *src, uint32_t len)
{
    volatile uint32_t *xip = (volatile uint32_t *)GX8002_STAGE1_XIP_BASE;
    volatile uint32_t *unlock = (volatile uint32_t *)GX8002_STAGE1_XIP_UNLOCK;
    uint32_t status;

    do {
        status = xip[0x0Au] & (1u << GX8002_STAGE1_XIP_BUSY_BIT);
    } while (status != 0u);
    xip[0x02u] = status;
    xip[0x13u] = status;
    xip[0x00u] = GX8002_STAGE1_XIP_CTRL_WORD_WRITE;
    xip[0x01u] = len;
    xip[0x04u] = 1u;
    xip[0x06u] = len << 16u;
    *unlock = status;
    xip[0x02u] = 1u;
    xip[0x18u] = cmd;
    while (len != 0u) {
        do {
            status = xip[0x0Au];
        } while (!(status & (1u << GX8002_STAGE1_XIP_TX_READY_BIT)));
        xip[0x18u] = (uint32_t)*src++;
        len--;
    }
    while (*gx8002_stage1_xip_at(0x20u)) {
    }
    do {
        status = xip[0x0Au];
    } while (status & (1u << GX8002_STAGE1_XIP_BUSY_BIT));
}
