/* Native LV style property wrapper 0x44145a..0x44146a. */
#include <stdint.h>

extern void audio_uart_page_style_apply_44be4c(uint32_t, uint32_t,
                                                uint32_t, uint32_t);

void audio_uart_page_44145a(uint32_t object, uint32_t align,
                             uint32_t selector) {
    audio_uart_page_style_apply_44be4c(object, 0x5eu, (uint8_t)align, selector);
}
