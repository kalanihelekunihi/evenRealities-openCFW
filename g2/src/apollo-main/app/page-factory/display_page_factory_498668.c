/* Apollo page factory 0x498668..0x49867f. The descriptor address is a
 * stock ROM binding; final source-owned layout must replace this literal. */
#include <stdint.h>

extern void *audio_uart_page_create_44cf98(const void *, void *);
extern const uint8_t audio_uart_image_class_756108[]; /* display_lv_image_class_756108.c */
extern void audio_uart_page_initialize_44d0f0(void *);

void *audio_uart_page_498668(void *parent) {
    void *const page = audio_uart_page_create_44cf98(
        audio_uart_image_class_756108 /* Fix 48: stock lv_image_class 0x756108 */, parent);
    audio_uart_page_initialize_44d0f0(page);
    return page;
}
