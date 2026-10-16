/* Apollo audio opacity style wrapper, stock 0x441488..0x441496. */
#include <stdint.h>

extern void audio_uart_page_style_apply_44be4c(uint32_t object,
                                                uint32_t property,
                                                uint32_t value,
                                                uint32_t selector);

void audio_uart_display_audio_reset_441488(uint32_t object,
                                           uint32_t value,
                                           uint32_t selector) {
    audio_uart_page_style_apply_44be4c(object, 0x62u, (uint8_t)value, selector);
}
