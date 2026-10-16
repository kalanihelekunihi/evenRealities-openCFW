/* Apollo LV pair iterator, native 0x489b3c..0x489b73. */
#include <stdint.h>

extern uint32_t audio_uart_text_decode_489c5e(const char *text,
                                               uint32_t *offset);

void audio_uart_text_next_glyph_489b3c(const char *text,
                                        uint32_t *glyph,
                                        uint32_t *next,
                                        uint32_t *offset) {
    uint32_t current = audio_uart_text_decode_489c5e(text, offset);
    *glyph = current;
    *next = current == 0u ? 0u :
        audio_uart_text_decode_489c5e(text + *offset, 0);
}
