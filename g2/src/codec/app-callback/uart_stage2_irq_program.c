/* SPDX-License-Identifier: MIT
 * Stage-2 transfer controller configuration at 0x10004020.
 * Source fields and validation follow the retained full body; controller
 * root/descriptor pointers are the product SRAM state at 0x20009ddc.
 */
#include <stdint.h>

extern uint32_t gx8002_uart_stage2_address_mask_29c0(uint32_t address);
extern void gx8002_uart_stage2_irq_descriptors_3f1c(const uint32_t *base,
    volatile uint32_t *output, int32_t count, int32_t bytes, uint8_t mode);

int32_t gx8002_uart_stage2_irq_program_4020(
    uint32_t buffer, uint32_t uart_base, uint32_t transfer_bytes,
    uint32_t slot, const uint32_t *mode)
{
    volatile uint32_t *const state =
        (volatile uint32_t *)(uintptr_t)UINT32_C(0x20009ddc);
    uint32_t control = (mode[6] << 11) | (mode[1] << 14) |
        UINT32_C(0x18000001) | (mode[0] << 1) | (mode[0] << 4);
    if (mode[7] != 0) {
        if (mode[7] != 1) return -1;
        control |= 0x100u;
    }
    if (mode[2] != 0) {
        if (mode[2] != 1) return -1;
        control |= 0x400u;
    }
    switch (mode[9]) {
    case 0: break;
    case 1: control |= UINT32_C(0x800000); break;
    case 2: control |= UINT32_C(0x1000000); break;
    case 3: control |= UINT32_C(0x1800000); break;
    default: return -1;
    }
    switch (mode[4]) {
    case 0: break;
    case 1: control |= UINT32_C(0x2000000); break;
    case 2: control |= UINT32_C(0x4000000); break;
    case 3: control |= UINT32_C(0x6000000); break;
    default: return -1;
    }
    control |= mode[11] << 20;
    uint32_t flags = 0;
    if (mode[10] != 0) {
        if (mode[10] != 1) return -1;
        flags |= 0x400u;
    }
    if (mode[5] != 0) {
        if (mode[5] != 1) return -1;
        flags |= 0x800u;
    }
    volatile uint32_t *const root =
        (volatile uint32_t *)(uintptr_t)state[0];
    const uint32_t bit = UINT32_C(1) << (slot & 31u);
    root[0x338 / 4] = bit;
    root[0x340 / 4] = bit;
    root[0x348 / 4] = bit;
    root[0x350 / 4] = bit;
    root[0x358 / 4] = bit;
    volatile uint32_t *const channel =
        (volatile uint32_t *)((uintptr_t)root + slot * 0x58u);
    const uint32_t uart_address =
        gx8002_uart_stage2_address_mask_29c0(uart_base);
    const uint32_t buffer_address =
        gx8002_uart_stage2_address_mask_29c0(buffer);
    channel[0] = uart_address;
    channel[8 / 4] = buffer_address;
    channel[0x18 / 4] = control;
    channel[0x40 / 4] = flags;
    channel[0x44 / 4] = (mode[8] << 11) | (mode[3] << 7) | 2u;
    const int32_t signed_bytes = (int32_t)transfer_bytes;
    const int32_t count = (signed_bytes / 0xfff) +
        (signed_bytes % 0xfff != 0);
    if ((uint32_t)(count * 0x18) > 0x1a0u) return -1;
    volatile uint32_t *const descriptors =
        (volatile uint32_t *)(uintptr_t)state[slot + 0xdau];
    /* The stock helper only reads words 0, 1, and 3 of this base block. */
    uint32_t base[4];
    base[0] = uart_address;
    base[1] = buffer_address;
    base[3] = control;
    gx8002_uart_stage2_irq_descriptors_3f1c(base, descriptors,
        count, (int32_t)transfer_bytes,
        (uint8_t)(UINT32_C(1) << (mode[0] & 31u)));
    channel[0x10 / 4] = gx8002_uart_stage2_address_mask_29c0(
        (uint32_t)(uintptr_t)descriptors);
    return 0;
}
