/* SPDX-License-Identifier: MIT */
/*
 * Reviewed stage-1 data-cell and clock-source leaves for the GX8002 UART
 * boot stage 1 (IRAM) image.
 *
 * Clean-room C implementing the decoded stock behavior of two tiny leaves,
 * identified against the pinned NationalChip grus SDK
 * `arch/soc/grus/include/base_addr.h` at commit
 * 8bf9ee5cb6eeb226011e61c15fa4981b83b93bd5 (MIT; the SDK repo carries the
 * repo-level MIT LICENSE, and this file reproduces no SDK text):
 * only the numeric register address (PMU_CFG_SOURCE_SEL0,
 * GX_REG_BASE_PMU_CONFIG + 0x8C = 0xA001008C, the clock-source-select
 * register the SDK's own boards/.../clock_board.c reads) and the
 * call/return conventions cross the boundary. The bodies below were written
 * from the decoded stock control flow and are verified by decoded-target
 * execution comparison against the stock bytes plus an independent oracle.
 * See docs/research/gx8002-uart-stage1-idbit-source.md.
 *
 * The 32-bit word at 0x20002008 is stage-1-local recovered configuration:
 * the early init routine (runtime 0x100001FC) stores the chip-revision
 * low nibble there (read from 0xA0010068, masked to 4 bits) alongside the
 * neighbouring nibble at 0x2000200C, and the UART configure routine
 * (runtime 0x100005C4) branches on it. The getter leaf below is its only
 * in-image reader (single `bsr` caller at 0x100001CE).
 *
 * Stock envelopes (package offsets into firmware_codec.bin):
 *   open_cfw_gx8002_uart_stage1_get_stored_id  runtime 0x100002BC, package 0x30C, 12 bytes
 *   open_cfw_gx8002_uart_stage1_pmu_bit_modify runtime 0x10000840, package 0x890, 30 bytes
 */
#include <stdint.h>

#ifndef GX8002_STAGE1_ID_CELL
#define GX8002_STAGE1_ID_CELL ((volatile uint32_t *)0x20002008u)
#endif
#ifndef GX8002_STAGE1_PMU_SOURCE_SEL0
#define GX8002_STAGE1_PMU_SOURCE_SEL0 ((volatile uint32_t *)0xa001008cu)
#endif

uint32_t open_cfw_gx8002_uart_stage1_get_stored_id(void)
{
    return *GX8002_STAGE1_ID_CELL;
}

void open_cfw_gx8002_uart_stage1_pmu_bit_modify(const uint32_t *desc)
{
    uint32_t bit = desc[0];
    uint32_t value = ((const unsigned char *)desc)[4];
    uint32_t current = *GX8002_STAGE1_PMU_SOURCE_SEL0;
    uint32_t all = 0xfffffffeu;
    uint32_t mask = (all << bit) | (all >> (32u - bit));

    *GX8002_STAGE1_PMU_SOURCE_SEL0 = (current & mask) | (value << bit);
}
