/* Apollo display owner walk, stock 0x45fcd2..0x45fd04. */
#include <stdint.h>

extern void *audio_uart_lv_obj_parent_44dca2(void *object);

static uint32_t get32(const uint8_t *p) {
    return (uint32_t)p[0] | ((uint32_t)p[1] << 8u) |
        ((uint32_t)p[2] << 16u) | ((uint32_t)p[3] << 24u);
}

void *audio_uart_display_audio_find_owner_45fcd2(void *object) {
    if (object == 0) return 0;
    uint8_t *parent = (uint8_t *)audio_uart_lv_obj_parent_44dca2(object);
    while (parent != 0) {
        uint32_t candidate = get32(parent + 16u);
        if (candidate != 0u &&
            get32((const uint8_t *)(uintptr_t)candidate + 24u) ==
                (uint32_t)(uintptr_t)parent)
            return (void *)(uintptr_t)candidate;
        parent = (uint8_t *)audio_uart_lv_obj_parent_44dca2(parent);
    }
    return 0;
}
