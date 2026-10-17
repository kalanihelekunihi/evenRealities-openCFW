/* Apollo Main LVGL label rule wrapper, native 0x43f6ac..0x43f6b7. */
#include <stdint.h>

extern void audio_uart_page_4411d4(uint32_t, uint32_t, uint32_t);

void audio_uart_page_43f6ac(uint32_t object, uint32_t value) {
    audio_uart_page_4411d4(object, (uint8_t)value, 0u);
}
