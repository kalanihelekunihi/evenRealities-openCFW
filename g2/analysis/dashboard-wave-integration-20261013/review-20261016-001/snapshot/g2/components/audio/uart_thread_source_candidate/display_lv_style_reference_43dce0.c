/* Apollo LV style property reference lookup, native 0x43dce0..0x43dd47. */
#include <stdint.h>

static uint32_t rd32(const uint8_t *p) {
    return (uint32_t)p[0] | ((uint32_t)p[1] << 8u) |
        ((uint32_t)p[2] << 16u) | ((uint32_t)p[3] << 24u);
}
static void wr32(uint8_t *p, uint32_t value) {
    for (unsigned i = 0; i < 4u; ++i) p[i] = (uint8_t)(value >> (8u * i));
}

uint32_t audio_uart_lv_style_reference_43dce0(void *style,
                                                uint32_t property,
                                                void *result) {
    const uint8_t *s = (const uint8_t *)style;
    const uint8_t *data = (const uint8_t *)(uintptr_t)rd32(s);
    uint8_t key = (uint8_t)property;
    if (s[8] != 0xffu) {
        uint32_t count = s[8];
        for (uint32_t i = 0; i < count; ++i) {
            if (data[count * 4u + i] == key) {
                wr32((uint8_t *)result, rd32(data + i * 4u));
                return 1u;
            }
        }
    } else {
        for (uint32_t i = 0; data[i * 8u] != 0u; ++i) {
            if (data[i * 8u] == key) {
                wr32((uint8_t *)result, rd32(data + i * 8u + 4u));
                return 1u;
            }
        }
    }
    return 0u;
}
