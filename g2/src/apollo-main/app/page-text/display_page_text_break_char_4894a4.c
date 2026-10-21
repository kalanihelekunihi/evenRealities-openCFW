/* Apollo LV line-break trailing ASCII table, native 0x4894a4..0x4894cf. */
#include <stdint.h>

uint32_t audio_uart_text_is_break_char_4894a4(uint32_t glyph) {
    static const uint8_t chars[] = " ,.;:-_)]}"; /* stock ROM 0x78b528 */
    for (uint32_t i = 0u; chars[i] != 0u; ++i)
        if (glyph == chars[i]) return 1u;
    return 0u;
}
