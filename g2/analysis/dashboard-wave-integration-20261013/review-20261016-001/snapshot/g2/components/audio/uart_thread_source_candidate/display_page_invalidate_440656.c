/* Apollo LV object invalidate, native 0x440656..0x4406bb. */
#include <stdint.h>

extern uint32_t audio_uart_lv_draw_size_get_452dc8(void *object);
extern void audio_uart_lv_area_copy_43ee94(void *destination,
                                            const void *source);
extern void audio_uart_display_invalidate_area(void *object,
                                               const int32_t *area);

void audio_uart_page_invalidate_440656(void *object) {
    /* Stock asserts and traps on null before the object path. */
    if (object == 0) __builtin_trap();
    uint32_t size = audio_uart_lv_draw_size_get_452dc8(object);
    int32_t area[4];
    audio_uart_lv_area_copy_43ee94(area, (const uint8_t *)object + 0x14u);
    area[0] = (int32_t)((uint32_t)area[0] - size);
    area[1] = (int32_t)((uint32_t)area[1] - size);
    area[2] = (int32_t)((uint32_t)area[2] + size);
    area[3] = (int32_t)((uint32_t)area[3] + size);
    audio_uart_display_invalidate_area(object, area);
}
