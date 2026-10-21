/* Native 0x4411d4 and 0x43f6b8: paired LV style setters. */
#include <stdint.h>

extern void audio_uart_page_style_apply_44be4c(void *, uint8_t, uint32_t,
                                                uint32_t);
extern void audio_uart_page_43f09a(uint32_t, uint32_t, uint32_t);

void audio_uart_page_4411d4(uint32_t object, uint32_t index,
                            uint32_t selector) {
    audio_uart_page_style_apply_44be4c((void *)(uintptr_t)object, 0x0au,
                                        (uint8_t)index, selector);
}

void audio_uart_page_43f6b8(uint32_t object, uint32_t index,
                            uint32_t value, uint32_t selector) {
    audio_uart_page_4411d4(object, (uint8_t)index, 0u);
    audio_uart_page_43f09a(object, value, selector);
}
