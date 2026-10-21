/* Apollo Main prep-note indexed line text 0x5b4776..0x5b4845. */
#include <stdint.h>

extern uint8_t audio_conversate_prep_note_ram_200d7630[];
extern uint32_t audio_conversate_prep_note_utf8_prefix_5b3ef8(const void *, uint32_t);
extern void *audio_queue_copy_bytes(void *, const void *, uint32_t);

static uint16_t half(const uint8_t *bytes, uint32_t offset) {
    return (uint16_t)bytes[offset] | ((uint16_t)bytes[offset + 1u] << 8u);
}

uint32_t audio_conversate_prep_note_line_text_5b4776(
    uint32_t line, char *output, uint32_t capacity) {
    const uint16_t limit = (uint16_t)capacity;
    if (output == 0 || limit == 0u) return 0u;
    output[0] = '\0';
    const uint8_t *const meta = audio_conversate_prep_note_ram_200d7630 + 0x1094u;
    const uint8_t *const text = audio_conversate_prep_note_ram_200d7630 + 0x7e00u;
    const uint16_t index = (uint16_t)line;
    if (index >= half(meta, 6u)) return 0u;
    const uint16_t start = half(meta, 10u + (uint32_t)index * 2u);
    uint16_t end = half(meta, 12u + (uint32_t)index * 2u);
    if (end < start || end > half(meta, 4u)) return 0u;
    while (start < end && (text[end - 1u] == '\n' || text[end - 1u] == '\r'))
        --end;
    uint16_t length = (uint16_t)(end - start);
    if (length >= limit)
        length = (uint16_t)audio_conversate_prep_note_utf8_prefix_5b3ef8(
            text + start, (uint16_t)(limit - 1u));
    if (length != 0u) (void)audio_queue_copy_bytes(output, text + start, length);
    output[length] = '\0';
    return length;
}
