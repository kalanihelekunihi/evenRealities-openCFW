/* SPDX-License-Identifier: BSD-3-Clause */
/*
 * Source-equivalent adapter for AmbiqSuite 5.1.0 mspi_cq_pause.
 * The target body preserves the authenticated G2 ABI and instruction span;
 * the host path replaces MMIO and delay calls with explicit software ports.
 */

#include "runtime_bootloader_mspi_cq_pause_candidate.h"

#if defined(__arm__) || defined(__thumb__)
extern void open_cfw_bootloader_retained_delay_us_41d1c0(void);
extern void open_cfw_bootloader_retained_status_check_41d246(void);

__attribute__((used, naked, noinline))
void open_cfw_bootloader_mspi_cq_pause_423fb8(void)
{
    __asm__ volatile(
        "push {r3, r4, r5, r6, r7, lr}\n"
        "movs r4, r0\n"
        "movs r0, #0\n"
        "ldr.w r5, [pc, #0xc14]\n"
        "movs r6, r5\n"
        "ldr.w r7, [pc, #0xc10]\n"
        "ldr r0, [r4, #4]\n"
        "adds.w r0, r7, r0, lsl #12\n"
        "movs.w r1, #0x800000\n"
        "str.w r1, [r0, #0x2b4]\n"
        "b 2f\n"
        "1:\n"
        "movs r0, r6\n"
        "subs r6, r0, #1\n"
        "cmp r0, #0\n"
        "beq 5f\n"
        "movs r0, #1\n"
        "bl open_cfw_bootloader_retained_delay_us_41d1c0\n"
        "2:\n"
        "ldr r0, [r4, #4]\n"
        "adds.w r0, r7, r0, lsl #12\n"
        "ldr.w r0, [r0, #0x2a0]\n"
        "lsls r0, r0, #31\n"
        "bpl 4f\n"
        "ldr r0, [r4, #4]\n"
        "adds.w r0, r7, r0, lsl #12\n"
        "ldr.w r0, [r0, #0x2ac]\n"
        "ubfx r0, r0, #3, #1\n"
        "cmp r0, #0\n"
        "beq 3f\n"
        "ldr r0, [r4, #4]\n"
        "adds.w r0, r7, r0, lsl #12\n"
        "ldr.w r0, [r0, #0x2b8]\n"
        "lsrs r0, r0, #7\n"
        "ands r0, r0, #1\n"
        "b 6f\n"
        "3:\n"
        "movs r0, #0\n"
        "6:\n"
        "uxtb r0, r0\n"
        "cmp r0, #0\n"
        "beq 1b\n"
        "4:\n"
        "movs r0, #1\n"
        "str r0, [sp]\n"
        "movs r3, #0\n"
        "movs r2, #1\n"
        "ldr r0, [r4, #4]\n"
        "adds.w r7, r7, r0, lsl #12\n"
        "adds.w r1, r7, #0x104\n"
        "movs r0, r5\n"
        "bl open_cfw_bootloader_retained_status_check_41d246\n"
        "7:\n"
        "pop {r1, r4, r5, r6, r7, pc}\n"
        "5:\n"
        "movs r0, #4\n"
        "b 7b\n");
}
#else
enum {
    OPEN_CFW_MSPI0_BASE = 0x40060000U,
    OPEN_CFW_MSPI_STRIDE = 0x1000U,
    OPEN_CFW_MSPI_DMASTAT = 0x104U,
    OPEN_CFW_MSPI_CQCFG = 0x2A0U,
    OPEN_CFW_MSPI_CQSTAT = 0x2ACU,
    OPEN_CFW_MSPI_CQSETCLEAR = 0x2B4U,
    OPEN_CFW_MSPI_CQPAUSE = 0x2B8U,
    OPEN_CFW_MSPI_PAUSE_LIMIT = 100000U,
    OPEN_CFW_MSPI_SC_PAUSE_CQ = 0x00800000U,
    OPEN_CFW_STATUS_TIMEOUT = 4U,
};

uint32_t open_cfw_bootloader_mspi_cq_pause_423fb8(
    const open_cfw_mspi_cq_pause_context *instance,
    const open_cfw_mspi_cq_pause_ports *ports)
{
    const uint32_t base = OPEN_CFW_MSPI0_BASE +
                          instance->module * OPEN_CFW_MSPI_STRIDE;
    uint32_t remaining = OPEN_CFW_MSPI_PAUSE_LIMIT;

    ports->write_reg(ports->context, base + OPEN_CFW_MSPI_CQSETCLEAR,
                     OPEN_CFW_MSPI_SC_PAUSE_CQ);
    while ((ports->read_reg(ports->context, base + OPEN_CFW_MSPI_CQCFG) & 1U)
           != 0U) {
        const uint32_t paused =
            (ports->read_reg(ports->context, base + OPEN_CFW_MSPI_CQSTAT) >> 3)
            & 1U;
        if (paused != 0U &&
            ((ports->read_reg(ports->context, base + OPEN_CFW_MSPI_CQPAUSE) >> 7)
             & 1U) != 0U) {
            break;
        }
        if (remaining == 0U) {
            return OPEN_CFW_STATUS_TIMEOUT;
        }
        remaining--;
        ports->delay_us(ports->context, 1U);
    }
    return ports->status_check(
        ports->context, OPEN_CFW_MSPI_PAUSE_LIMIT,
        base + OPEN_CFW_MSPI_DMASTAT, 1U, 0U, 1U);
}
#endif
