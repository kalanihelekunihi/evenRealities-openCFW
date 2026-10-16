/* Apollo generic page factory, native 0x43de82..0x43ded3. */
#include <stdint.h>

extern void *audio_uart_page_create_44cf98(const void *descriptor, void *parent);
extern void audio_uart_page_initialize_44d0f0(void *page);
extern const uint8_t audio_uart_lv_base_class_7564f8[];

void *audio_uart_page_43de82(void *parent) {
    void *page = audio_uart_page_create_44cf98(audio_uart_lv_base_class_7564f8,
                                               parent);
    if (page == 0) __builtin_trap();
    audio_uart_page_initialize_44d0f0(page);
    return page;
}
