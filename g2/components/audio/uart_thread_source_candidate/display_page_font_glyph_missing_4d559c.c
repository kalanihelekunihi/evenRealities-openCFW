/* Apollo LV non-rendering glyph predicate, native 0x4d559c..0x4d5611. */
#include <stdint.h>

uint32_t audio_uart_font_glyph_is_missing_4d559c(uint32_t glyph) {
    if (glyph < 0x20u || glyph == 0x061cu || glyph == 0x115fu ||
        glyph == 0x1160u || glyph == 0xfeffu || glyph == 0xf8ffu)
        return 1u;
    if (glyph >= 0x180bu && glyph < 0x180fu) return 1u;
    if (glyph >= 0x200bu && glyph < 0x2010u) return 1u;
    if (glyph >= 0x2028u && glyph < 0x2030u) return 1u;
    if (glyph >= 0x205fu && glyph < 0x2070u) return 1u;
    return 0u;
}
