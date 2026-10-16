/* Terminal's historical symbol name for stock lv_label_set_text at 0x49942e. */
#include <stdint.h>
extern const char *audio_uart_page_49942e(uint8_t *page, const char *text);
void audio_lv_anim_start_49942e(uint32_t label, const void *text) {
    (void)audio_uart_page_49942e((uint8_t *)(uintptr_t)label,
                                 (const char *)text);
}
