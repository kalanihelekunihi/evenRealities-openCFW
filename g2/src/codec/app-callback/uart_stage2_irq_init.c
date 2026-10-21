/* SPDX-License-Identifier: MIT
 * Direct native transfer-controller initialization 0x10004388.
 * Product SRAM state is 0x20009ddc; MMIO root is 0xa1000000.
 */
#include <stdint.h>

extern void gx8002_uart_stage2_dispatch_4a48(uint32_t selector,
                                               uint32_t enabled);
extern void gx8002_uart_stage2_irq_register_30e8(uint32_t irq,
                                                   uintptr_t callback,
                                                   uintptr_t context);
extern uint32_t gx8002_uart_stage2_irq_service_4250(void);

void gx8002_uart_stage2_setup_4388(void)
{
    volatile uint8_t *const state =
        (volatile uint8_t *)(uintptr_t)UINT32_C(0x20009ddc);
    *(volatile uint32_t *)(state + 0) = UINT32_C(0xa1000000);
    *(volatile uint32_t *)(state + 4) = 2;
    *(volatile uint32_t *)(state + 0x368) =
        ((uint32_t)(uintptr_t)(state + 23) & ~UINT32_C(15));
    *(volatile uint32_t *)(state + 0x36c) =
        ((uint32_t)(uintptr_t)(state + 455) & ~UINT32_C(15));
    state[0x370] = 0;
    state[0x371] = 0;
    gx8002_uart_stage2_dispatch_4a48(25u, 1u);
    volatile uint32_t *const root =
        (volatile uint32_t *)(uintptr_t)UINT32_C(0xa1000000);
    root[0x398 / 4] = 0;
    root[0x338 / 4] = UINT32_MAX;
    root[0x340 / 4] = UINT32_MAX;
    root[0x348 / 4] = UINT32_MAX;
    root[0x350 / 4] = UINT32_MAX;
    root[0x358 / 4] = UINT32_MAX;
    root[0x398 / 4] = 1;
    gx8002_uart_stage2_dispatch_4a48(25u, 0u);
    gx8002_uart_stage2_irq_register_30e8(10u,
        (uintptr_t)&gx8002_uart_stage2_irq_service_4250, 0);
}
