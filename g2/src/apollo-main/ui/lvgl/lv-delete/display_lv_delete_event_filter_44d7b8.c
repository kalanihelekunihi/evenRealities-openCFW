/* Apollo Main LVGL object delete coordination, native 0x44d7b8..0x44d877.
 * Called by the deferred deletion callback at 0x44df20. */
#include <stdint.h>

extern void audio_uart_display_size_changed(void *);
extern void *audio_uart_lv_obj_parent_44dca2(void *);
extern void *audio_uart_lv_display_for_object(void *);
extern void audio_uart_lv_child_delete_44df80(void *);
extern void audio_uart_lv_scrollbar_invalidate_44f2ca(void *);
extern uint32_t audio_uart_lv_obj_event_451670(void *, uint32_t, void *);
extern void audio_uart_lvgl_log(uint32_t, const char *, uint32_t,
                                const char *, const char *, ...);

static uint16_t flags(const void *object) {
    return *(const uint16_t *)(const void *)((const uint8_t *)object + 0x2au);
}

void audio_uart_page_delete_event_filter_44d7b8(void *object) {
    if ((flags(object) & 0x1000u) != 0u) return;
    audio_uart_display_size_changed(object);
    uint8_t *parent = (uint8_t *)audio_uart_lv_obj_parent_44dca2(object);
    uint8_t *display = 0;
    uint32_t current_screen = 0u;
    if (parent == 0) {
        display = (uint8_t *)audio_uart_lv_display_for_object(object);
        if (display == 0) return;
        current_screen = *(uint32_t *)(void *)(display + 0x2c4u) ==
                         (uint32_t)(uintptr_t)object;
    }
    audio_uart_lv_child_delete_44df80(object);
    if (parent != 0 && (flags(parent) & 0x1000u) == 0u) {
        audio_uart_lv_scrollbar_invalidate_44f2ca(parent);
        (void)audio_uart_lv_obj_event_451670(parent, 0x2au, 0);
        (void)audio_uart_lv_obj_event_451670(parent, 0x2cu, 0);
    }
    if (current_screen != 0u) {
        audio_uart_lvgl_log(2u, "lv_obj", 0x56u, "lv_obj_delete",
                            "current screen deleted");
        *(uint32_t *)(void *)(display + 0x2c4u) = 0u;
    }
}

/* display_audio_release.c identifies its delete import as the same
 * stock 0x44d7b8 entry. Keep both source call sites on one implementation. */
void audio_uart_display_object_delete(void *)
    __attribute__((alias("audio_uart_page_delete_event_filter_44d7b8")));
