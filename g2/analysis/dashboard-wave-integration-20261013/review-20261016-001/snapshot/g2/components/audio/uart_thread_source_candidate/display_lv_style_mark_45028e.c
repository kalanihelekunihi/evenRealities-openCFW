/* Apollo active style-use marker, native 0x45028e..0x4502b1. */
#include <stdint.h>

extern uint8_t audio_uart_display_lv_state[];

static uint32_t get32(const uint8_t *p) {
    return (uint32_t)p[0] | ((uint32_t)p[1] << 8u) |
           ((uint32_t)p[2] << 16u) | ((uint32_t)p[3] << 24u);
}

void audio_uart_lv_style_mark_45028e(const void *style) {
    uint32_t node_address = get32(audio_uart_display_lv_state + 0x6cu);
    uint32_t style_address = (uint32_t)(uintptr_t)style;
    while (node_address != 0u) {
        uint8_t *node = (uint8_t *)(uintptr_t)node_address;
        if (get32(node + 4u) == style_address ||
            get32(node) == style_address)
            node[0x18u] |= 1u;
        node_address = get32(node + 0x14u);
    }
}
