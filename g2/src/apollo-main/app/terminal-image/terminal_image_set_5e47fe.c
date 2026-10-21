/* Stock Terminal image source and style reset at 0x5e47fe. */
#include <stdint.h>

extern uint32_t audio_uart_lv_style_unlink_450500(void *object, void *style);
extern void audio_uart_display_audio_reset_441488(uint32_t object,
                                                   uint32_t value,
                                                   uint32_t selector);
extern void audio_uart_page_498680(void *object, const void *source);

void audio_terminal_image_set_5e47fe(uint32_t object, uint32_t source) {
    if (object == 0u || source == 0u)
        return;
    (void)audio_uart_lv_style_unlink_450500((void *)(uintptr_t)object, 0);
    audio_uart_display_audio_reset_441488(object, 0xffu, 0u);
    audio_uart_page_498680((void *)(uintptr_t)object,
                            (const void *)(uintptr_t)source);
}
