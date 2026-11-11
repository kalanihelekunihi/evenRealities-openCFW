/* SPDX-License-Identifier: MIT
 * GX8002 UART stage-2 external interrupt entry at 0x10003124.
 * Stock code reads the VIC active-vector field at 0xe000ec00, subtracts
 * 32 for the external IRQ number, then dispatches the {handler, context}
 * cell at 0x2000984c. The table is filled by irq_register_30e8.
 */
#include <stdint.h>

struct gx8002_uart_stage2_irq_slot {
    void (*handler)(uint32_t irq, uint32_t context);
    uint32_t context;
};

__attribute__((isr, section(".text.gx8002_uart_stage2_irq_entry_3124")))
void gx8002_uart_stage2_irq_entry_3124(void)
{
    uint32_t irq =
        (*(const volatile uint32_t *)(uintptr_t)UINT32_C(0xe000ec00) & 511u) - 32u;
    const struct gx8002_uart_stage2_irq_slot *const slots =
        (const struct gx8002_uart_stage2_irq_slot *)(uintptr_t)UINT32_C(0x2000984c);
    void (*const handler)(uint32_t, uint32_t) = slots[irq].handler;
    if (handler != 0)
        handler(irq, slots[irq].context);
}
