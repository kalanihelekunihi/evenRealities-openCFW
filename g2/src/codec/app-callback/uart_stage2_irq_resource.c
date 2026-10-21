/* SPDX-License-Identifier: MIT
 * Stage-2 IRQ resource allocator 0x100041b8 and callback table writer
 * 0x1000432c. The SRAM bases come from stock literal words at
 * 0x10004208 and 0x1000433c.
 */
#include <stdint.h>

extern uint32_t gx8002_uart_stage2_irq_save_3110(void);
extern void gx8002_uart_stage2_irq_restore_311c(uint32_t state);
extern void gx8002_uart_stage2_dispatch_4a48(uint32_t selector,
                                               uint32_t enabled);

int32_t gx8002_uart_stage2_irq_allocate_41b8(void)
{
    volatile uint8_t *const state =
        (volatile uint8_t *)(uintptr_t)UINT32_C(0x20009ddc);
    const uint32_t saved = gx8002_uart_stage2_irq_save_3110();
    int32_t slot = -1;
    const uint32_t count = *(const volatile uint32_t *)(state + 4);
    if (count != 0 && state[0x370] == 0) slot = 0;
    else if (count > 1 && state[0x371] == 0) slot = 1;
    if (slot >= 0) {
        state[0x370 + slot] = 1;
        gx8002_uart_stage2_dispatch_4a48(25u, 1u);
    }
    gx8002_uart_stage2_irq_restore_311c(saved);
    return slot;
}

void gx8002_uart_stage2_irq_set_callback_432c(uint32_t slot,
                                                uintptr_t callback,
                                                uintptr_t context)
{
    volatile uint32_t *const slots =
        (volatile uint32_t *)(uintptr_t)UINT32_C(0x20009950);
    slots[slot] = (uint32_t)callback;
    slots[slot + 2u] = (uint32_t)context;
}
