/* Apollo Main LV font descriptor at stock ROM 0x755610..0x755633.
 * The first two words are Thumb callbacks; keeping relocations makes a
 * custom link target the compiled callback bodies instead of stock flash. */
#include <stdint.h>

extern void audio_uart_lv_font_glyph_dsc_4b26a4(void);
extern void audio_uart_lv_font_glyph_bitmap_4b239c(void);

struct audio_uart_display_page_style_layout {
    uintptr_t glyph_dsc;
    uintptr_t glyph_bitmap;
    uint32_t fields[7];
};

_Static_assert(sizeof(struct audio_uart_display_page_style_layout) == 36u,
               "Apollo LV font descriptor size");

const struct audio_uart_display_page_style_layout audio_uart_display_page_style = {
    (uintptr_t)&audio_uart_lv_font_glyph_dsc_4b26a4,
    (uintptr_t)&audio_uart_lv_font_glyph_bitmap_4b239c,
    {0u, 0x10u, 3u, 0x0001ff00u, 0x0078001cu, 0u, 0u}
};
