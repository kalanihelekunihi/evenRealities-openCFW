/* Native bounded UTF-8 prefix counter 0x5b3ef8..0x5b3f93. */
#include <stdint.h>

uint32_t audio_conversate_prep_note_utf8_prefix_5b3ef8(const void *input,
                                                        uint32_t length) {
    const uint8_t *const bytes = input;
    uint32_t consumed = 0u;
    const uint16_t limit = (uint16_t)length;
    while ((uint16_t)consumed < limit) {
        uint8_t lead = bytes[(uint16_t)consumed];
        uint32_t width = 1u;
        if (lead & 0x80u) {
            if ((lead & 0xe0u) == 0xc0u)
                width = 2u;
            else if ((lead & 0xf0u) == 0xe0u)
                width = 3u;
            else if ((lead & 0xf8u) == 0xf0u)
                width = 4u;
        }
        if ((uint16_t)(consumed + width) > limit)
            break;
        uint32_t part = 1u;
        for (uint32_t i = 1u; (uint8_t)i < (uint8_t)width; ++i) {
            if ((bytes[(uint16_t)(consumed + i)] & 0xc0u) != 0x80u) {
                part = 0u;
                break;
            }
        }
        if (!part)
            break;
        consumed += width;
    }
    return (uint16_t)consumed;
}
