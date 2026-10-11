/* SPDX-License-Identifier: MIT
 * Stage-2 IRQ hardware setup at 0x10004340. The outer calls the
 * descriptor programmer 0x10004020 with all five original arguments,
 * then flushes the selected 416-byte mode buffer and arms VIC masks.
 */
#include <stdint.h>

extern int32_t gx8002_uart_stage2_irq_program_4020(
    uint32_t buffer, uint32_t uart_base, uint32_t transfer_bytes,
    uint32_t slot, const uint32_t *mode);
extern void gx8002_uart_stage2_cache_range_3274(uint32_t address,
                                                  int32_t length);

int32_t gx8002_uart_stage2_irq_hardware_setup_4340(
    uint32_t buffer, uint32_t uart_base, uint32_t transfer_bytes,
    uint32_t slot, const uint32_t *mode)
{
    if (gx8002_uart_stage2_irq_program_4020(buffer, uart_base,
                                              transfer_bytes, slot, mode) == -1)
        return -1;
    volatile uint32_t *const state =
        (volatile uint32_t *)(uintptr_t)UINT32_C(0x20009ddc);
    volatile uint32_t *const root =
        (volatile uint32_t *)(uintptr_t)state[0];
    const uint32_t mask = UINT32_C(0x101) << (slot & 31u);
    root[0x310 / 4] = mask;
    gx8002_uart_stage2_cache_range_3274(state[slot + 0xda], 0x1a0);
    root[0x3a0 / 4] = mask;
    return 0;
}
