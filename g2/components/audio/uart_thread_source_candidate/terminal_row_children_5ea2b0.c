/* Stock Terminal row image position, color and source selectors. */
#include <stdint.h>

extern uint32_t audio_terminal_row_image_hint_5ea4f0(uint32_t index, uint32_t item);

uint32_t audio_terminal_image_y_5ea2b0(void) {
    return 6u; /* (0x1c - 0x10) / 2 */
}

uint32_t audio_terminal_row_color_5ea2f2(uint32_t item) {
    if (item == 0u)
        return 0u;
    uint8_t kind = *(const uint8_t *)(const void *)(uintptr_t)item;
    return kind == 1u || kind == 3u ? 1u : 0u;
}

uint32_t audio_terminal_row_image_5ea524(uint32_t index, uint32_t item) {
    const uint8_t *record = (const uint8_t *)(uintptr_t)item;
    uint8_t kind = record[1];
    if (kind == 1u)
        return 0x007733a8u;
    if (kind == 2u)
        return 0x00770890u;
    if (kind != 0u)
        return 0u;
    if (audio_terminal_row_image_hint_5ea4f0((uint16_t)index, item) != 0u ||
        audio_terminal_row_color_5ea2f2(item) != 0u)
        return 0x00773258u;
    return 0u;
}
