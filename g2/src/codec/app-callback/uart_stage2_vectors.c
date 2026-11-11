/* SPDX-License-Identifier: MIT
 * GX8002 UART boot stage-2 vector table at IRAM 0x10002800. The locked
 * image has reset in slot 0, the default exception bridge in slots 1..31,
 * and the common external IRQ entry in slots 32..63.
 */
#include <stdint.h>

extern void gx8002_uart_stage1_second_entry(void);
extern void gx8002_uart_stage2_exception_bridge_2994(void);
extern void gx8002_uart_stage2_irq_entry_3124(void);

#define RESET (uintptr_t)&gx8002_uart_stage1_second_entry
#define EXCEPTION (uintptr_t)&gx8002_uart_stage2_exception_bridge_2994
#define IRQ (uintptr_t)&gx8002_uart_stage2_irq_entry_3124
#define E8 EXCEPTION, EXCEPTION, EXCEPTION, EXCEPTION, EXCEPTION, EXCEPTION, EXCEPTION, EXCEPTION
#define I8 IRQ, IRQ, IRQ, IRQ, IRQ, IRQ, IRQ, IRQ

__attribute__((used, section(".gx8002.uart.stage2.vectors"), aligned(4)))
const uintptr_t gx8002_uart_stage2_vectors[64] = {
    RESET, E8, E8, E8, EXCEPTION, EXCEPTION, EXCEPTION, EXCEPTION,
    EXCEPTION, EXCEPTION, EXCEPTION, I8, I8, I8, I8,
};

_Static_assert(sizeof(gx8002_uart_stage2_vectors) == 0x100,
               "stage-2 vector table must occupy 256 bytes");

#undef I8
#undef E8
#undef IRQ
#undef EXCEPTION
#undef RESET
