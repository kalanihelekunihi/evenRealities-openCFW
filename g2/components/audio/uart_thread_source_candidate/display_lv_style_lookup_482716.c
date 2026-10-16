/* Native LV style-property lookup at 0x482708 and 0x482716. */
#include <stdint.h>

uint32_t audio_uart_lv_style_is_sparse_482708(const void *style) {
    return ((const uint8_t *)style)[8] == 0xffu;
}

uint32_t audio_uart_lv_style_lookup_482716(const void *style,
                                           uint32_t property, uint32_t *value) {
    const uint8_t *header = (const uint8_t *)style;
    const uint8_t *data = *(const uint8_t *const *)(const void *)header;
    const uint8_t wanted = (uint8_t)property;
    if (audio_uart_lv_style_is_sparse_482708(style)) {
        for (uint32_t i = 0;; ++i) {
            const uint8_t *row = data + i * 8u;
            uint8_t key = row[0];
            if (key == 0u) return 0u;
            if (key == wanted) {
                *value = *(const uint32_t *)(const void *)(row + 4u);
                return 1u;
            }
        }
    }
    uint32_t count = header[8];
    const uint8_t *keys = data + count * 4u;
    for (uint32_t i = 0; i < count; ++i) {
        if (keys[i] == wanted) {
            *value = ((const uint32_t *)(const void *)data)[i];
            return 1u;
        }
    }
    return 0u;
}
