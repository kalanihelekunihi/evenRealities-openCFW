/* Terminal ABI name for the existing stock 0x44ea04 scroll-to-Y provider. */
#include <stdint.h>

extern void audio_uart_lv_scroll_to_y_44ea04(void *object, int32_t target,
                                              uint32_t animated);

void audio_terminal_display_status_44ea04(uint32_t object, uint32_t target,
                                           uint32_t animated) {
    audio_uart_lv_scroll_to_y_44ea04((void *)(uintptr_t)object,
                                      (int32_t)target, animated);
}
