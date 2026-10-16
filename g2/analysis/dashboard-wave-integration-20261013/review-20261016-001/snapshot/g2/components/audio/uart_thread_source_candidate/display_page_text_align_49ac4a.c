/* Apollo LV line alignment, native 0x49ac4a..0x49acad. */
#include <stdint.h>

extern int32_t audio_uart_text_width_4899a4(const char *text, uint32_t length,
                                             const void *font, int32_t spacing,
                                             uint32_t flags);
extern int32_t audio_uart_lv_area_width_451598(const void *area);

void audio_uart_page_text_align_49ac4a(int32_t *x, uint32_t align,
                                        const char *text, uint32_t length,
                                        const void *font, int32_t spacing,
                                        const void *area, uint32_t flags) {
    uint32_t mode = align & 0xffu;
    if (mode != 2u && mode != 3u) return;
    int32_t width = audio_uart_text_width_4899a4(text, length, font,
                                                  spacing, flags & 0xffu);
    int32_t available = audio_uart_lv_area_width_451598(area);
    uint32_t old = (uint32_t)*x;
    if (mode == 2u)
        *x = (int32_t)(old + (uint32_t)(available / 2) -
                       (uint32_t)(width / 2));
    else
        *x = (int32_t)(old + (uint32_t)available - (uint32_t)width);
}
