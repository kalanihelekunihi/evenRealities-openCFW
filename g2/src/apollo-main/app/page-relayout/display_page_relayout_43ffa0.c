/* Apollo page relative-size relayout trigger 0x43ffa0..0x43ffcf. */
#include <stdint.h>

extern int32_t audio_uart_lv_style_width_43eea6(void *, uint32_t);
extern int32_t audio_uart_lv_style_height_43eec4(void *, uint32_t);
extern void audio_uart_lv_mark_layout_43f648(void *);

uint32_t audio_uart_page_relayout_43ffa0(void *object) {
    const int32_t width = audio_uart_lv_style_width_43eea6(object, 0u);
    const int32_t height = audio_uart_lv_style_height_43eec4(object, 0u);
    if (width == 0x3fffffff || height == 0x3fffffff) {
        audio_uart_lv_mark_layout_43f648(object);
        return 1u;
    }
    return 0u;
}
