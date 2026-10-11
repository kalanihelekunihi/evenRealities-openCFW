/* SPDX-License-Identifier: MIT
 * Direct native transfer-controller release 0x1000420c and service
 * 0x10004250. Callback table is RAM 0x20009950, controller state
 * is RAM 0x20009ddc, and the active channel count is two.
 */
#include <stdint.h>

extern uint32_t gx8002_uart_stage2_irq_save_3110(void);
extern void gx8002_uart_stage2_irq_restore_311c(uint32_t state);
extern void gx8002_uart_stage2_dispatch_4a48(uint32_t selector,
                                               uint32_t enabled);

void gx8002_uart_stage2_irq_release_420c(uint32_t slot)
{
    volatile uint8_t *const state =
        (volatile uint8_t *)(uintptr_t)UINT32_C(0x20009ddc);
    const uint32_t saved = gx8002_uart_stage2_irq_save_3110();
    state[0x370 + slot] = 0;
    const uint32_t count = *(const volatile uint32_t *)(state + 4);
    if (!(count != 0 && state[0x370] == 1) &&
        !(count > 1 && state[0x371] == 1))
        gx8002_uart_stage2_dispatch_4a48(25u, 0u);
    gx8002_uart_stage2_irq_restore_311c(saved);
}

uint32_t gx8002_uart_stage2_irq_service_4250(void)
{
    volatile uint32_t *const state =
        (volatile uint32_t *)(uintptr_t)UINT32_C(0x20009ddc);
    volatile uint32_t *const callbacks =
        (volatile uint32_t *)(uintptr_t)UINT32_C(0x20009950);
    volatile uint32_t *const root =
        (volatile uint32_t *)(uintptr_t)state[0];
    const uint32_t pending = root[0x2e8 / 4];
    for (uint32_t slot = 0; slot < 2u; ++slot) {
        if (((pending >> slot) & 1u) == 0) continue;
        const uint32_t mask = 1u << slot;
        root[0x338 / 4] = mask;
        root[0x340 / 4] = mask;
        root[0x348 / 4] = mask;
        root[0x350 / 4] = mask;
        root[0x358 / 4] = mask;
        root[0x310 / 4] = UINT32_C(0x100) << slot;
        gx8002_uart_stage2_irq_release_420c(slot);
        uintptr_t target = callbacks[slot];
        if (target != 0) {
            void (*callback)(uint32_t) = (void (*)(uint32_t))target;
            callback(callbacks[slot + 2u]);
        }
    }
    return 0;
}
