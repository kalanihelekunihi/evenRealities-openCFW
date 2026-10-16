/* Apollo Main graphics target rectangle, 0x4b1516..0x4b1547. */
#include <stdint.h>

extern void audio_uart_nema_child_514846(uint32_t, uint32_t);

void audio_uart_display_graphics_target_4b1516(int32_t x, int32_t y,
                                                uint32_t width, uint32_t height) {
    uint32_t right = (uint32_t)x + width;
    uint32_t bottom = (uint32_t)y + height;
    uint32_t left = x < 0 ? 0u : (uint32_t)x;
    uint32_t top = y < 0 ? 0u : (uint32_t)y;
    audio_uart_nema_child_514846(0x110u, (left & 0xffffu) | (top << 16u));
    audio_uart_nema_child_514846(0x114u, (right & 0xffffu) | (bottom << 16u));
}
