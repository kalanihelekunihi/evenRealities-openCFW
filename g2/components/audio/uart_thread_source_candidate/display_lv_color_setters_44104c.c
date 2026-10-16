/* Native RGB888 constructor and three LV style-color wrappers.
 * The stock wrappers copy three bytes; the upper stack byte is unspecified. */
#include <stdint.h>

extern void audio_uart_page_style_apply_44be4c(void *, uint8_t, uint32_t,
                                                 uint32_t);

uint32_t audio_uart_page_44104c(uint32_t rgb) {
    return rgb & 0x00ffffffu;
}

void audio_uart_page_44127e(void *object, uint32_t rgb,
                            uint32_t selector) {
    audio_uart_page_style_apply_44be4c(object, 0x1cu,
                                       rgb & 0x00ffffffu, selector);
}

void audio_uart_page_4412ec(void *object, uint32_t rgb,
                            uint32_t selector) {
    audio_uart_page_style_apply_44be4c(object, 0x31u,
                                       rgb & 0x00ffffffu, selector);
}

void audio_uart_page_44140e(void *object, uint32_t rgb,
                            uint32_t selector) {
    audio_uart_page_style_apply_44be4c(object, 0x58u,
                                       rgb & 0x00ffffffu, selector);
}
