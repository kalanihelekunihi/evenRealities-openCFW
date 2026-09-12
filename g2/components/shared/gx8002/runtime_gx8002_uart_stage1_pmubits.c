/* SPDX-License-Identifier: MIT */
/*
 * Reviewed PMU OSC-trim state bit leaves for the GX8002 UART boot stage 1
 * (IRAM) image.
 *
 * These are clean-room C implementations of the four tiny register
 * read-modify-write/read routines the stage-1 body applies to the PMU
 * power-on-reset register 1 (OSC trim state), identified in the pinned
 * NationalChip grus SDK as
 *   PMU_CFG_POWER_ON_RESET_REG1 (GX_REG_BASE_PMU_CONFIG + 0x30)
 * (arch/soc/grus/include/base_addr.h at commit
 * 8bf9ee5cb6eeb226011e61c15fa4981b83b93bd5, MIT). Only the address and the
 * bit positions cross the boundary; the bodies below were written from the
 * decoded stock control flow and verified by decoded-target execution
 * comparison against the stock bytes. See
 * docs/research/gx8002-uart-stage1-pmubits-source.md.
 *
 * Stock envelopes (package offsets into firmware_codec.bin):
 *   open_cfw_gx8002_uart_stage1_pmu_set_bit0  runtime 0x10000374, package 0x3c4, 24 bytes
 *   open_cfw_gx8002_uart_stage1_pmu_get_bit0  runtime 0x100003a4, package 0x3f4, 12 bytes
 *   open_cfw_gx8002_uart_stage1_pmu_get_bit1  runtime 0x100003b0, package 0x400, 12 bytes
 * (The sibling set_bit1 leaf at runtime 0x1000038c lives in
 * runtime_gx8002_uart_stage1_pmusbit.S: this toolchain lowers the bit-clear
 * to a 4-byte andni while the stock envelope only fits the 2-byte bclri, so
 * that one leaf is reviewed assembly. See the audit.)
 *
 * The set leaves preserve the stock clear-then-set access pattern (clear the
 * bit, re-read the register, OR in the new bit): other bits of this register
 * carry live hardware state, so the re-read is behavior, not redundancy.
 */
#include <stdint.h>

#define GX8002_PMU_CONFIG_BASE 0xA0010000u
#ifndef GX8002_UART_STAGE1_PMU_POR1
#define GX8002_UART_STAGE1_PMU_POR1 (GX8002_PMU_CONFIG_BASE + 0x30u)
#endif

void open_cfw_gx8002_uart_stage1_pmu_set_bit0(uint32_t value)
{
    volatile uint32_t *reg = (volatile uint32_t *)GX8002_UART_STAGE1_PMU_POR1;

    *reg &= (uint32_t)~1u;
    *reg |= value & 1u;
}

uint32_t open_cfw_gx8002_uart_stage1_pmu_get_bit0(void)
{
    return *(volatile uint32_t *)GX8002_UART_STAGE1_PMU_POR1 & 1u;
}

uint32_t open_cfw_gx8002_uart_stage1_pmu_get_bit1(void)
{
    return (*(volatile uint32_t *)GX8002_UART_STAGE1_PMU_POR1 >> 1) & 1u;
}
