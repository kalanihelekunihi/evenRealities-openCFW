/* SPDX-License-Identifier: BSD-3-Clause */
/*
 * Source-equivalent adapter for AmbiqSuite 5.1.0 sched_hiprio.
 * The target body preserves the authenticated G2 ABI and instruction span;
 * the host path exposes critical-section and MMIO effects through ports.
 */

#include "runtime_bootloader_mspi_sched_hiprio_candidate.h"

#if defined(__arm__) || defined(__thumb__)
extern void open_cfw_bootloader_critical_save_41b8ec(void);
extern void open_cfw_bootloader_mspi_cq_pause_423fb8(void);
extern void open_cfw_bootloader_mspi_program_dma_42403e(void);

__attribute__((used, naked, noinline))
void open_cfw_bootloader_mspi_sched_hiprio_4240aa(void)
{
    __asm__ volatile(
        "push {r3, r4, r5, r6, r7, lr}\n"
        "movs r6, r0\n"
        "movs r7, r1\n"
        "movs r5, #0\n"
        "bl open_cfw_bootloader_critical_save_41b8ec\n"
        "str r0, [sp]\n"
        "ldr.w r4, [r6, #0x840]\n"
        "ldr.w r0, [r6, #0x840]\n"
        "adds r7, r7, r0\n"
        "str.w r7, [r6, #0x840]\n"
        "ldr r0, [sp]\n"
        "msr primask, r0\n"
        "cmp r4, #0\n"
        "bne 2f\n"
        "movs r0, r6\n"
        "bl open_cfw_bootloader_mspi_cq_pause_423fb8\n"
        "cmp r0, #0\n"
        "bne 3f\n"
        "movs r0, #0\n"
        "str r0, [r6, #0x24]\n"
        "ldr.w r0, [pc, #0xaf8]\n"
        "ldr r1, [r6, #4]\n"
        "adds.w r1, r0, r1, lsl #12\n"
        "movs r2, #0x40\n"
        "str.w r2, [r1, #0x208]\n"
        "ldr r1, [r6, #4]\n"
        "adds.w r1, r0, r1, lsl #12\n"
        "ldr r2, [r6, #4]\n"
        "adds.w r0, r0, r2, lsl #12\n"
        "ldr.w r0, [r0, #0x200]\n"
        "orrs r0, r0, #0x40\n"
        "str.w r0, [r1, #0x200]\n"
        "movs r0, #1\n"
        "strb.w r0, [r6, #0x83c]\n"
        "movs r0, r6\n"
        "bl open_cfw_bootloader_mspi_program_dma_42403e\n"
        "movs r5, r0\n"
        "cmp r5, #0\n"
        "beq 2f\n"
        "movs r0, r5\n"
        "b 3f\n"
        "2:\n"
        "movs r0, r5\n"
        "3:\n"
        "pop {r1, r4, r5, r6, r7, pc}\n");
}
#else
enum {
    OPEN_CFW_MSPI0_BASE = 0x40060000U,
    OPEN_CFW_MSPI_STRIDE = 0x1000U,
    OPEN_CFW_MSPI_INTEN = 0x200U,
    OPEN_CFW_MSPI_INTCLR = 0x208U,
    OPEN_CFW_MSPI_INT_DMACMP = 0x40U,
};

uint32_t open_cfw_bootloader_mspi_sched_hiprio_4240aa(
    open_cfw_mspi_sched_hiprio_context *instance, uint32_t transaction_count,
    const open_cfw_mspi_sched_hiprio_ports *ports)
{
    const uint32_t token = ports->critical_save(ports->context);
    const uint32_t pending = instance->high_priority_entries;
    uint32_t status = 0U;
    uint32_t base;
    uint32_t interrupt_enable;

    instance->high_priority_entries += transaction_count;
    ports->critical_restore(ports->context, token);
    if (pending != 0U) {
        return 0U;
    }
    status = ports->command_queue_pause(ports->context);
    if (status != 0U) {
        return status;
    }
    instance->transaction_interrupt = 0U;
    base = OPEN_CFW_MSPI0_BASE + instance->module * OPEN_CFW_MSPI_STRIDE;
    ports->write_reg(ports->context, base + OPEN_CFW_MSPI_INTCLR,
                     OPEN_CFW_MSPI_INT_DMACMP);
    interrupt_enable = ports->read_reg(ports->context,
                                       base + OPEN_CFW_MSPI_INTEN);
    ports->write_reg(ports->context, base + OPEN_CFW_MSPI_INTEN,
                     interrupt_enable | OPEN_CFW_MSPI_INT_DMACMP);
    instance->high_priority_active = 1U;
    return ports->program_dma(ports->context);
}
#endif
