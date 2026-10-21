/* Apollo Nema stencil state at 0x52266e and 0x5226b2. */
#include <stdint.h>

extern volatile uint32_t audio_uart_nema_context_cell[]; /* RAM 0x20074efc */

uint32_t audio_uart_nema_stencil_save_52266e(uint32_t a, uint32_t b,
                                               uint32_t c, uint32_t d) {
    uint32_t flags=(a ? 0x04000000u : 0u) |
                   (b ? 0x02000000u : 0u) |
                   (c ? 0x01000000u : 0u) |
                   (d ? 0x00800000u : 0u);
    volatile uint32_t *const context=(volatile uint32_t *)(uintptr_t)
        audio_uart_nema_context_cell[0];
    const uint32_t old=context[7];
    context[7]=flags;
    context[6]=context[3] | context[4] | context[5] | flags;
    return old;
}

void audio_uart_nema_stencil_restore_5226b2(uint32_t previous) {
    volatile uint32_t *const context=(volatile uint32_t *)(uintptr_t)
        audio_uart_nema_context_cell[0];
    const uint32_t flags=previous & 0x07800000u;
    context[7]=flags;
    context[6]=context[3] | context[4] | context[5] | flags;
}
