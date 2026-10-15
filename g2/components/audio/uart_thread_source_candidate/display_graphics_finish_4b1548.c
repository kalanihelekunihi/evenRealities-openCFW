/* Apollo Main restore NEMA context rectangle, 0x4b1548..0x4b1587.
 * The stock 0x4b178c literal points at RAM cell 0x20074efc. */
#include <stdint.h>

extern volatile uint32_t audio_uart_nema_context_cell[];
extern void audio_uart_nema_child_514846(uint32_t, uint32_t);

void audio_uart_display_graphics_finish_4b1548(void) {
    const volatile uint32_t *context =
        (const volatile uint32_t *)(uintptr_t)audio_uart_nema_context_cell[0];
    uint32_t x = context[9];
    uint32_t y = context[10];
    uint32_t right = context[11] + x;
    uint32_t bottom = context[12] + y;
    uint32_t left = (int32_t)x < 0 ? 0u : x;
    uint32_t top = (int32_t)y < 0 ? 0u : y;
    audio_uart_nema_child_514846(0x110u, (left & 0xffffu) | (top << 16u));
    audio_uart_nema_child_514846(0x114u, (right & 0xffffu) | (bottom << 16u));
}
