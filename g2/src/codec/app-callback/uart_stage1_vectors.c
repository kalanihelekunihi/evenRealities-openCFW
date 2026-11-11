/* SPDX-License-Identifier: MIT
 * GX8002 UART boot stage-1 interrupt vectors. The locked FWPK stage has a
 * 64-word table at IRAM 0x10000000: reset, 31 exception slots, 32 IRQ slots.
 * The linker fixes the three C entry points to their stock addresses.
 */
#include <stdint.h>

extern void gx8002_uart_stage1_reset(void);
extern void gx8002_uart_stage1_traps(void);
extern void gx8002_uart_stage1_irq_traps(void);

#define RESET (uintptr_t)&gx8002_uart_stage1_reset
#define EXCEPTION (uintptr_t)&gx8002_uart_stage1_traps
#define IRQ (uintptr_t)&gx8002_uart_stage1_irq_traps
#define E8 EXCEPTION, EXCEPTION, EXCEPTION, EXCEPTION, EXCEPTION, EXCEPTION, EXCEPTION, EXCEPTION
#define I8 IRQ, IRQ, IRQ, IRQ, IRQ, IRQ, IRQ, IRQ

__attribute__((used, section(".gx8002.uart.stage1.vectors"), aligned(4)))
const uintptr_t gx8002_uart_stage1_vectors[64] = {
    RESET, E8, E8, E8, EXCEPTION, EXCEPTION, EXCEPTION, EXCEPTION,
    EXCEPTION, EXCEPTION, EXCEPTION, I8, I8, I8, I8,
};

_Static_assert(sizeof(gx8002_uart_stage1_vectors) == 0x100,
               "stage-1 vector table must occupy 256 bytes");

#undef I8
#undef E8
#undef IRQ
#undef EXCEPTION
#undef RESET
