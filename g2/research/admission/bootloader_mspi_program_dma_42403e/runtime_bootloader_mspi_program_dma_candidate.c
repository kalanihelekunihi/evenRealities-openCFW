/* SPDX-License-Identifier: BSD-3-Clause */
/*
 * Source-equivalent adapter for AmbiqSuite 5.1.0 program_dma.
 * The target body preserves the authenticated G2 ABI and instruction span;
 * the host path exposes clock and MMIO effects through software-only ports.
 */

#include "runtime_bootloader_mspi_program_dma_candidate.h"

#if defined(__arm__) || defined(__thumb__)
extern void open_cfw_bootloader_mode_enable_route_4222f0(void);

__attribute__((used, naked, noinline))
void open_cfw_bootloader_mspi_program_dma_42403e(void)
{
    __asm__ volatile(
        "push {r3, r4, r5, lr}\n"
        "ldr r4, [r0, #4]\n"
        "ldr.w r2, [r0, #0x850]\n"
        "adds r2, r2, #1\n"
        "ldr.w r1, [r0, #0x848]\n"
        "udiv r3, r2, r1\n"
        "mls r2, r1, r3, r2\n"
        "ldr.w r3, [r0, #0x854]\n"
        "movs r1, #0x18\n"
        "muls r2, r1, r2\n"
        "add.w r5, r3, r2\n"
        "ldr r1, [r0, #4]\n"
        "adds r1, #0x10\n"
        "uxtb r1, r1\n"
        "movs r0, #4\n"
        "bl open_cfw_bootloader_mode_enable_route_4222f0\n"
        "cmp r0, #0\n"
        "bne 1f\n"
        "ldr.w r0, [pc, #0xb64]\n"
        "movs r1, #0\n"
        "adds.w r2, r0, r4, lsl #12\n"
        "str.w r1, [r2, #0x100]\n"
        "ldr r1, [r5]\n"
        "adds.w r2, r0, r4, lsl #12\n"
        "str.w r1, [r2, #0x108]\n"
        "ldr r1, [r5, #4]\n"
        "adds.w r2, r0, r4, lsl #12\n"
        "str.w r1, [r2, #0x10c]\n"
        "ldr r1, [r5, #8]\n"
        "adds.w r2, r0, r4, lsl #12\n"
        "str.w r1, [r2, #0x110]\n"
        "ldr r1, [r5, #0xc]\n"
        "adds.w r0, r0, r4, lsl #12\n"
        "str.w r1, [r0, #0x100]\n"
        "movs r0, #0\n"
        "1:\n"
        "pop {r1, r4, r5, pc}\n");
}
#else
enum {
    OPEN_CFW_MSPI0_BASE = 0x40060000U,
    OPEN_CFW_MSPI_STRIDE = 0x1000U,
    OPEN_CFW_MSPI_DMACFG = 0x100U,
    OPEN_CFW_MSPI_DMATARGADDR = 0x108U,
    OPEN_CFW_MSPI_DMADEVADDR = 0x10CU,
    OPEN_CFW_MSPI_DMATOTCOUNT = 0x110U,
    OPEN_CFW_CLK_ID_HFRC = 4U,
    OPEN_CFW_CLK_USER_MSPI0 = 16U,
};

uint32_t open_cfw_bootloader_mspi_program_dma_42403e(
    const open_cfw_mspi_program_dma_context *instance,
    const open_cfw_mspi_program_dma_ports *ports)
{
    const uint32_t index =
        (instance->last_hp_index + 1U) % instance->max_hp_transactions;
    const open_cfw_mspi_program_dma_entry *entry =
        &instance->hp_transactions[index];
    const uint32_t status = ports->clock_request(
        ports->context, OPEN_CFW_CLK_ID_HFRC,
        (OPEN_CFW_CLK_USER_MSPI0 + instance->module) & 0xFFU);
    const uint32_t base = OPEN_CFW_MSPI0_BASE +
                          instance->module * OPEN_CFW_MSPI_STRIDE;

    if (status != 0U) {
        return status;
    }
    ports->write_reg(ports->context, base + OPEN_CFW_MSPI_DMACFG, 0U);
    ports->write_reg(ports->context, base + OPEN_CFW_MSPI_DMATARGADDR,
                     entry->dma_target_address);
    ports->write_reg(ports->context, base + OPEN_CFW_MSPI_DMADEVADDR,
                     entry->dma_device_address);
    ports->write_reg(ports->context, base + OPEN_CFW_MSPI_DMATOTCOUNT,
                     entry->dma_total_count);
    ports->write_reg(ports->context, base + OPEN_CFW_MSPI_DMACFG,
                     entry->dma_config);
    return 0U;
}
#endif
