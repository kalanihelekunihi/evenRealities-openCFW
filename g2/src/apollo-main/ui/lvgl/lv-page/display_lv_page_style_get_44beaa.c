/* Native LV object style lookup 0x44beaa and byte-property adapter 0x482946. */
#include <stdint.h>

extern uint32_t audio_uart_lv_style_lookup_482716(const void *, uint32_t,
                                                    uint32_t *);

uint32_t audio_uart_lv_style_get_482946(const void *style, uint32_t property,
                                       uint32_t *value) {
    return audio_uart_lv_style_lookup_482716(style, (uint8_t)property, value);
}

uint32_t audio_uart_page_style_get_44beaa(uint32_t object, uint32_t property,
                                          uint32_t *value, uint32_t selector) {
    const uint8_t *root = (const uint8_t *)(uintptr_t)object;
    uint32_t count = (*(const uint16_t *)(const void *)(root + 0x2au) >> 4) & 0x3fu;
    for (uint32_t i = 0; i < count; ++i) {
        const uint8_t *rows = *(const uint8_t *const *)(const void *)(root + 0x0cu);
        const uint8_t *row = rows + i * 8u;
        uint32_t descriptor = *(const uint32_t *)(const void *)(row + 4u);
        if ((descriptor & 0x01000000u) == 0u ||
            (descriptor & 0x00ffffffu) != selector)
            continue;
        const void *style = *(const void *const *)(const void *)row;
        return audio_uart_lv_style_get_482946(style, (uint8_t)property, value);
    }
    return 0u;
}
