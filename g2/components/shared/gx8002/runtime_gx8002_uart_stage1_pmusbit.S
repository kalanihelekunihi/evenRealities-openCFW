/* SPDX-License-Identifier: MIT */
/* Reviewed PMU OSC-trim state bit-1 write leaf for the GX8002 UART boot
 * stage 1 (IRAM) image: runtime 0x1000038c, package 0x3dc, 24 bytes.
 *
 * Clean-room assembly implementing the decoded stock behavior against the
 * pinned NationalChip grus SDK register definition
 *   PMU_CFG_POWER_ON_RESET_REG1 (GX_REG_BASE_PMU_CONFIG + 0x30)
 * (arch/soc/grus/include/base_addr.h at commit
 * 8bf9ee5cb6eeb226011e61c15fa4981b83b93bd5, MIT): clear bit 1 of the
 * register, re-read it, then OR in bit 0 of the argument shifted to bit 1.
 * The re-read is behavior (other bits carry live hardware state), matching
 * the sibling C leaf open_cfw_gx8002_uart_stage1_pmu_set_bit0.
 *
 * Assembly (rather than C) because this toolchain lowers the bit-clear to a
 * 4-byte andni while the 24-byte stock envelope only fits the 2-byte bclri;
 * every C shape probed compiles to 26 bytes. The sequence below is verified
 * by decoded-target execution comparison against the stock bytes (see
 * docs/research/gx8002-uart-stage1-pmubits-source.md), not by byte identity.
 */
.section .text.open_cfw_gx8002_uart_stage1_pmu_set_bit1,"ax",@progbits
.balign 4
.global open_cfw_gx8002_uart_stage1_pmu_set_bit1
.type open_cfw_gx8002_uart_stage1_pmu_set_bit1,@function
open_cfw_gx8002_uart_stage1_pmu_set_bit1:
    movih r3, 0xA001
    lsli r0, r0, 1
    ld.w r2, (r3, 0x30)
    bclri r2, 1
    st.w r2, (r3, 0x30)
    ld.w r2, (r3, 0x30)
    andi r0, r0, 2
    or r0, r2
    st.w r0, (r3, 0x30)
    rts
.size open_cfw_gx8002_uart_stage1_pmu_set_bit1, .-open_cfw_gx8002_uart_stage1_pmu_set_bit1
