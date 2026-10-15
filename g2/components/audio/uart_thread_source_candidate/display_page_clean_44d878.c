/* LVGL object clean 0x44d878..0x44d90d. */
#include <stdint.h>

extern void audio_uart_display_size_changed(void *);
extern uint32_t audio_uart_lv_child_count_44ddea(void *);
extern void *audio_uart_lv_first_live_child_44e164(void *);
extern void audio_uart_lv_child_delete_44df80(void *);
extern void audio_uart_lv_position_reset_44e9ba(void *, uint32_t, uint32_t, uint32_t);
extern uint32_t audio_uart_lv_obj_event_451670(void *, uint32_t, void *);
extern void audio_uart_lvgl_log(uint32_t, const char *, uint32_t, const char *, ...);

void audio_uart_page_44d878(void *object) {
    if (object == 0) {
        audio_uart_lvgl_log(3u,
            "D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\core\\lv_obj_tree.c",
            0x61u, "lv_obj_clean", "Asserted at expression: %s (%s)",
            "obj != NULL", "NULL pointer");
        for (;;) { }
    }
    audio_uart_display_size_changed(object);
    const uint32_t before = audio_uart_lv_child_count_44ddea(object);
    for (void *child = audio_uart_lv_first_live_child_44e164(object);
         child != 0;
         child = audio_uart_lv_first_live_child_44e164(object))
        audio_uart_lv_child_delete_44df80(child);
    audio_uart_lv_position_reset_44e9ba(object, 0u, 0u, 0u);
    uint8_t *const layer = *(uint8_t **)(void *)((uint8_t *)object + 8u);
    if (layer != 0) {
        *(uint32_t *)(void *)(layer + 0x20u) = 0u;
        *(uint32_t *)(void *)(layer + 0x24u) = 0u;
    }
    if (audio_uart_lv_child_count_44ddea(object) < before) {
        (void)audio_uart_lv_obj_event_451670(object, 0x2au, 0);
        (void)audio_uart_lv_obj_event_451670(object, 0x2cu, 0);
    }
}
