/* Apollo LVGL page editing state 0x44d510..0x44d5b7. */
#include <stdint.h>

extern void *audio_uart_page_context_find_44d77a(void *);
extern uint32_t audio_uart_lv_obj_event_451670(void *, uint32_t, void *);
extern void audio_uart_display_size_changed(void *);
extern void audio_uart_lvgl_log(uint32_t, const char *, uint32_t, const char *, ...);

static const char page_source[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\core\\lv_group.c";

void *audio_uart_page_active_object_44d58c(void *page) {
    if (page == 0)
        return 0;
    const uint8_t *const p = (const uint8_t *)page;
    const uint32_t node = *(const uint32_t *)(const void *)(p + 0x0cu);
    return node == 0u ? 0 : (void *)(uintptr_t)*(const uint32_t *)(uintptr_t)node;
}

uint32_t audio_uart_page_get_editing_44d5a4(const void *page) {
    return page == 0 ? 0u : ((const uint8_t *)page)[0x1cu] >> 1u & 1u;
}

uint32_t audio_uart_page_set_editing_44d510(void *page, uint32_t requested) {
    if (page == 0) {
        audio_uart_lvgl_log(3u, page_source, 0x13au, "lv_group_set_editing",
                            "Asserted at expression: %s (%s)", "group != NULL",
                            "NULL pointer");
        for (;;) { }
    }
    uint8_t *const flags = (uint8_t *)page + 0x1cu;
    const uint32_t editing = (uint8_t)requested != 0u;
    if (editing != ((*flags >> 1u) & 1u)) {
        *flags = (uint8_t)((*flags & 0xfdu) | (editing << 1u));
        void *const selected = audio_uart_page_active_object_44d58c(page);
        if (selected != 0) {
            void *const context = audio_uart_page_context_find_44d77a(page);
            if ((uint8_t)audio_uart_lv_obj_event_451670(
                    selected, 0x13u, context) == 1u)
                audio_uart_display_size_changed(selected);
        }
    }
    return requested;
}
