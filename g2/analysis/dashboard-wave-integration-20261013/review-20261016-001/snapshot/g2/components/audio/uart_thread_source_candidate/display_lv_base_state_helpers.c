/* Apollo LV object state and scrolling-chain check, native 0x43e156..0x43e183
 * and 0x44d19a..0x44d1cb. */
#include <stdint.h>

static uint32_t get32(const uint8_t *p) {
    return (uint32_t)p[0] | ((uint32_t)p[1] << 8u) |
           ((uint32_t)p[2] << 16u) | ((uint32_t)p[3] << 24u);
}

uint32_t audio_uart_lv_obj_state_43e156(const void *object) {
    if (object == 0) __builtin_trap();
    const uint8_t *p = (const uint8_t *)object + 0x28u;
    return (uint32_t)p[0] | ((uint32_t)p[1] << 8u);
}

uint32_t audio_uart_lv_obj_is_scrolling_44d19a(const void *object) {
    uint32_t node_address = get32((const uint8_t *)object);
    while (node_address != 0u) {
        const uint8_t *node = (const uint8_t *)(uintptr_t)node_address;
        uint8_t state = node[0x20u] & 3u;
        if (state != 0u) return state == 1u ? 1u : 0u;
        node_address = get32(node);
    }
    return 0u;
}
