/* Apollo base object constructor and style getters, native 0x43dd86..0x43dd99
 * and 0x43e33e..0x43e3dd. */
#include <stdint.h>

extern uint32_t audio_uart_lv_style_property_44bdea(void *object,
                                                     uint32_t selector,
                                                     uint32_t property);
extern int32_t audio_uart_lv_scroll_left_44e586(void *object);
extern int32_t audio_uart_lv_scroll_top_44e4aa(void *object);

int32_t audio_uart_lv_metric_43dd86(void *object, uint32_t selector) {
    return (int32_t)audio_uart_lv_style_property_44bdea(object, selector, 0x10u);
}

int32_t audio_uart_lv_metric_43dd90(void *object, uint32_t selector) {
    return (int32_t)audio_uart_lv_style_property_44bdea(object, selector, 0x12u);
}

static uint32_t get32(const uint8_t *p) {
    return (uint32_t)p[0] | ((uint32_t)p[1] << 8u) |
           ((uint32_t)p[2] << 16u) | ((uint32_t)p[3] << 24u);
}

static void put32(uint8_t *p, uint32_t value) {
    p[0] = (uint8_t)value; p[1] = (uint8_t)(value >> 8u);
    p[2] = (uint8_t)(value >> 16u); p[3] = (uint8_t)(value >> 24u);
}

void audio_uart_lv_base_ctor_43e33e(void *unused, void *object) {
    (void)unused;
    uint8_t *child = (uint8_t *)object;
    uint32_t parent_address = get32(child + 4u);
    if (parent_address != 0u) {
        uint8_t *parent = (uint8_t *)(uintptr_t)parent_address;
        int32_t scroll_left = audio_uart_lv_scroll_left_44e586(parent);
        int32_t scroll_top = audio_uart_lv_scroll_top_44e4aa(parent);
        uint32_t y = (uint32_t)audio_uart_lv_metric_43dd86(parent, 0u) +
                     get32(parent + 0x18u) - (uint32_t)scroll_top;
        put32(child + 0x18u, y);
        put32(child + 0x20u, y - 1u);
        uint32_t x = (uint32_t)audio_uart_lv_metric_43dd90(parent, 0u) +
                     get32(parent + 0x14u) - (uint32_t)scroll_left;
        put32(child + 0x14u, x);
        put32(child + 0x1cu, x - 1u);
    }
    put32(child + 0x24u, 0x1876u | (parent_address != 0u ? 0xa300u : 0u));
}
