/* Address-labeled bridge to the existing source-owned 0x4405d4 body. */
#include <stdint.h>

extern void audio_uart_display_invalidate_area(void *object,
                                               const int32_t *area);

void audio_uart_lv_invalidate_area_4405d4(void *object, const void *area) {
    audio_uart_display_invalidate_area(object, (const int32_t *)area);
}
