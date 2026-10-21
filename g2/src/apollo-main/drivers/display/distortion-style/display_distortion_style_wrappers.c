/* Stock page style wrappers at 0x441246, 0x441254, 0x44130c,
 * 0x44142e, 0x48ba78 and 0x48ba92. The stock leaf setters delegate to
 * 0x44be4c; the two composites delegate to four of those setters. */
#include <stdint.h>

extern void audio_uart_page_style_apply_44be4c(void *object, uint8_t index,
                                                uint32_t value, uint32_t selector);

void audio_uart_page_441246(void *object, uint32_t value, uint32_t selector) {
    audio_uart_page_style_apply_44be4c(object, 0x14u, value, selector);
}

void audio_uart_page_441254(void *object, uint32_t value, uint32_t selector) {
    audio_uart_page_style_apply_44be4c(object, 0x15u, value, selector);
}

void audio_uart_page_44130c(void *object, uint32_t value, uint32_t selector) {
    audio_uart_page_style_apply_44be4c(object, 0x32u, (uint8_t)value, selector);
}

void audio_uart_page_44142e(void *object, uint32_t value, uint32_t selector) {
    audio_uart_page_style_apply_44be4c(object, 0x59u, (uint8_t)value, selector);
}

void audio_uart_page_48ba78(void *object, uint32_t value) {
    audio_uart_page_style_apply_44be4c(object, 0x7au, (uint8_t)value, 0u);
    audio_uart_page_style_apply_44be4c(object, 0x16u, 1u, 0u);
}

void audio_uart_page_48ba92(void *object, uint32_t first, uint32_t second,
                            uint32_t third) {
    audio_uart_page_style_apply_44be4c(object, 0x7bu, (uint8_t)first, 0u);
    audio_uart_page_style_apply_44be4c(object, 0x7cu, (uint8_t)second, 0u);
    audio_uart_page_style_apply_44be4c(object, 0x7du, (uint8_t)third, 0u);
    audio_uart_page_style_apply_44be4c(object, 0x16u, 1u, 0u);
}
