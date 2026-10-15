/* Apollo LV UTF-8 traversal callbacks 0x489dbc..0x489e91. */
#include <stdint.h>

extern uint32_t audio_uart_text_utf8_length_489b74(const char *text);
extern uint32_t audio_uart_text_decode_489c5e(const char *text,
                                               uint32_t *offset);

uint64_t audio_uart_text_utf8_previous_489dbc(const char *text,
                                               uint32_t *offset,
                                               uint32_t fallback_high,
                                               uint32_t unused) {
    (void)unused;
    uint32_t high = fallback_high;
    *offset -= 1u;
    for (uint32_t tries = 0u; tries < 4u; ++tries) {
        uint32_t length = audio_uart_text_utf8_length_489b74(text + *offset);
        if (length != 0u) {
            uint32_t local = *offset;
            uint32_t glyph = audio_uart_text_decode_489c5e(text, &local);
            high = local;
            return ((uint64_t)high << 32u) | glyph;
        }
        if (*offset == 0u) return ((uint64_t)high << 32u);
        *offset -= 1u;
    }
    return ((uint64_t)high << 32u);
}

uint64_t audio_uart_text_utf8_bytes_for_count_489e14(const char *text,
                                                       uint32_t count,
                                                       uint32_t unused,
                                                       uint32_t high) {
    (void)unused;
    uint32_t bytes = 0u;
    uint32_t chars = 0u;
    while (chars < count && text[bytes] != '\0') {
        uint32_t length = audio_uart_text_utf8_length_489b74(text + bytes);
        bytes += length == 0u ? 1u : length;
        chars++;
    }
    return ((uint64_t)high << 32u) | bytes;
}

uint64_t audio_uart_text_utf8_count_to_bytes_489e4a(const char *text,
                                                      uint32_t bytes,
                                                      uint32_t high,
                                                      uint32_t unused) {
    (void)high; (void)unused;
    uint32_t offset = 0u;
    uint32_t count = 0u;
    while (offset < bytes) {
        (void)audio_uart_text_decode_489c5e(text, &offset);
        count++;
    }
    return ((uint64_t)offset << 32u) | count;
}

uint64_t audio_uart_text_utf8_count_489e6e(const char *text,
                                            uint32_t unused1,
                                            uint32_t unused2,
                                            uint32_t high) {
    (void)unused1; (void)unused2; (void)high;
    uint32_t offset = 0u;
    uint32_t count = 0u;
    while (text[offset] != '\0') {
        (void)audio_uart_text_decode_489c5e(text, &offset);
        count++;
    }
    return ((uint64_t)offset << 32u) | count;
}
