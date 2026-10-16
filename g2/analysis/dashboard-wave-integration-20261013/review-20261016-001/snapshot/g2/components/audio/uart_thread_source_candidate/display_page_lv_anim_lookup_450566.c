/* Apollo LV animation lookup, native 0x450566..0x4505a1. */
#include <stdint.h>

extern uint8_t audio_uart_display_lv_state[];
extern void *audio_uart_lv_list_first(void *list);
extern void *audio_uart_lv_list_next(void *list, void *current);

static uint32_t get32(const uint8_t *p) {
    return (uint32_t)p[0] | ((uint32_t)p[1] << 8u) |
           ((uint32_t)p[2] << 16u) | ((uint32_t)p[3] << 24u);
}

void *audio_uart_page_lv_anim_lookup_450566(void *variable,
                                             void *callback) {
    uint8_t *list = audio_uart_display_lv_state + 0xacu;
    uint8_t *node = (uint8_t *)audio_uart_lv_list_first(list);
    while (node != 0) {
        if (get32(node) == (uint32_t)(uintptr_t)variable &&
            (callback == 0 ||
             get32(node + 4u) == (uint32_t)(uintptr_t)callback))
            return node;
        node = (uint8_t *)audio_uart_lv_list_next(list, node);
    }
    return 0;
}
