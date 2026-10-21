/* SPDX-License-Identifier: MIT
 * Stock stage2 0x100042e8 transfer-controller setup variant. Native entry
 * preserves r3 as the slot and forwards its fifth stack argument to 0x4020.
 */
#include <stdint.h>

extern int32_t gx8002_uart_stage2_irq_program_4020(
    uint32_t buffer, uint32_t uart_base, uint32_t transfer_bytes,
    uint32_t slot, const uint32_t *mode);
extern void gx8002_uart_stage2_cache_range_3274(uint32_t address,
                                                  int32_t length);

int32_t gx8002_uart_stage2_irq_hardware_alt_42e8(
    uint32_t buffer, uint32_t uart_base, uint32_t transfer_bytes,
    uint32_t slot, const uint32_t *mode)
{
    int32_t result = gx8002_uart_stage2_irq_program_4020(
        buffer, uart_base, transfer_bytes, slot, mode);
    if (result == -1) return -1;
    volatile uint32_t *const state =
        (volatile uint32_t *)(uintptr_t)UINT32_C(0x20009ddc);
    gx8002_uart_stage2_cache_range_3274(state[slot + 0xdau], 0x1a0);
    volatile uint32_t *const root =
        (volatile uint32_t *)(uintptr_t)state[0];
    root[0x3a0u / 4u] = UINT32_C(0x101) << (slot & 31u);
    return 0;
}
