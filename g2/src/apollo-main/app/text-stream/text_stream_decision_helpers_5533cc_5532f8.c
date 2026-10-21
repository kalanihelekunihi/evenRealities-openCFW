/* Stock text-stream validation and interval decisions. */
#include <stdint.h>

extern int32_t audio_uart_font_path_compare(const char *, const char *);
extern uint32_t strlen(const char *);

static uint32_t word(const void *object, uint32_t offset) {
    return *(const uint32_t *)((const uint8_t *)object + offset);
}

uint32_t audio_text_stream_validate_5533cc(void *object, const char *text,
                                            uint32_t mode) {
    if (!object)
        return 0u;
    mode = (uint8_t)mode;
    if (mode == 0u || mode == 2u)
        return audio_uart_font_path_compare(
                   text, (const char *)(uintptr_t)word(object, 0u)) == 0 ? 1u : 0u;
    if (mode == 1u)
        return strlen(text) == 0u ? 1u : 0u;
    return 0u;
}

uint32_t audio_text_stream_next_interval_5532f8(const void *object) {
    if (!object)
        return 0u;
    uint32_t interval = word(object, 8u);
    if (!word(object, 4u) || !word(object, 0x10u))
        return interval;
    uint32_t remaining = word(object, 0x10u) - word(object, 0x0cu);
    if ((int32_t)remaining < 1)
        return interval;
    if (((const uint8_t *)object)[0x2cu] == 0u)
        remaining += 1u;
    return interval * remaining;
}
