/* Stock 0x4b1588..0x4b15a5: Nema mode cache update. */
#include <stdint.h>

extern volatile uint32_t audio_uart_ambiq_unit_cell[1];

void display_driver_nema_cache_4b1588(uint32_t enabled)
{
    volatile uint32_t *const state =
        (volatile uint32_t *)(uintptr_t)audio_uart_ambiq_unit_cell[0];
    const uint32_t flag = enabled ? 0x08000000u : 0u;
    state[0x14u / 4u] = flag;
    state[0x18u / 4u] = state[0x0cu / 4u] | flag |
                          state[0x10u / 4u] | state[0x1cu / 4u];
}
