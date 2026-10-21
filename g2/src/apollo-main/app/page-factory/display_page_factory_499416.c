/* Apollo page factory 0x499416..0x49942d. */
#include <stdint.h>

extern void *audio_uart_page_create_44cf98(const void *, void *);
extern void audio_uart_page_initialize_44d0f0(void *);
extern const uint8_t audio_uart_page_class_7561bc[];

void *audio_uart_page_499416(void *parent) {
    void *page = audio_uart_page_create_44cf98(audio_uart_page_class_7561bc, parent);
    audio_uart_page_initialize_44d0f0(page);
    return page;
}
