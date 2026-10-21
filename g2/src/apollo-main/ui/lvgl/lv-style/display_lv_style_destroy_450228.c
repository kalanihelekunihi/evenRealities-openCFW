/* Apollo Main event-list destruction 0x450228..0x450285 and descriptor
 * invalidation 0x45036c..0x45037d. The parent call at 0x44df80 supplies
 * the object's event array at spec+8. */
#include <stdint.h>

extern uint32_t audio_uart_lv_event_count_450388(void *);
extern void *audio_uart_lv_event_slot_450390(void *, uint32_t);
extern void audio_uart_lv_event_compact_450346(void *);
extern void audio_uart_lvgl_log(uint32_t, const char *, uint32_t,
                                const char *, const char *, ...);

void audio_uart_lv_event_mark_invalid_45036c(void *list, void *descriptor) {
    uint8_t *bytes = (uint8_t *)list;
    bytes[0x14u] = (uint8_t)(bytes[0x14u] | 2u);
    uint8_t *item = (uint8_t *)descriptor;
    *(uint32_t *)(void *)(item + 8u) |= 0x10000u;
}

void audio_uart_lv_style_destroy_450228(void *list) {
    if (list == 0) {
        audio_uart_lvgl_log(3u, "lv_event", 0xc3u, "lv_event_remove_all",
                            "list is null");
        __builtin_trap();
    }
    uint32_t count = audio_uart_lv_event_count_450388(list);
    for (uint32_t index = 0; index < count; ++index) {
        void *slot = audio_uart_lv_event_slot_450390(list, index);
        void *descriptor = (void *)(uintptr_t)*(uint32_t *)slot;
        audio_uart_lv_event_mark_invalid_45036c(list, descriptor);
    }
    audio_uart_lv_event_compact_450346(list);
}
