/* Apollo page update wrappers 0x44d45c and 0x44d4b6.
 * Null-page logger calls are source-owned; logger internals are separate. */
#include <stdint.h>

extern uint32_t audio_uart_page_update_core_44d63a(
    void *, void *(*)(void *), void *(*)(void *, void *));
extern void *audio_uart_lv_list_first(void *); /* native 0x482cd8 */
extern void *audio_uart_lv_list_next(void *, void *); /* native 0x482cf0 */
extern void *audio_uart_lv_list_first_482ce4(void *); /* native 0x482ce4 */
extern void *audio_uart_lv_list_next_482cfa(void *, void *); /* native 0x482cfa */
extern void audio_uart_lvgl_log(uint32_t, const char *, uint32_t, const char *, ...);

static const char page_source[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\core\\lv_group.c";
static const char assertion[] = "Asserted at expression: %s (%s)";
static const char group_nonnull[] = "group != NULL";
static const char null_pointer[] = "NULL pointer";

typedef void (*page_update_callback)(void *, uint32_t);

static page_update_callback callback_at(void *page) {
    uintptr_t raw = *(const uint32_t *)(const void *)((const uint8_t *)page + 0x14u);
    return (page_update_callback)raw;
}

void audio_uart_page_update_unbound_44d45c(void *page) {
    if (page == 0) {
        audio_uart_lvgl_log(3u, page_source, 0x102u, "lv_group_focus_next",
                            assertion, group_nonnull, null_pointer);
        for (;;) { }
    }
    const uint32_t changed = audio_uart_page_update_core_44d63a(
        page, audio_uart_lv_list_first,
        audio_uart_lv_list_next);
    page_update_callback const callback = callback_at(page);
    if (callback != 0 && (uint8_t)changed == 0u)
        callback(page, 1u);
}

void audio_uart_page_update_bound_44d4b6(void *page) {
    if (page == 0) {
        audio_uart_lvgl_log(3u, page_source, 0x10du, "lv_group_focus_prev",
                            assertion, group_nonnull, null_pointer);
        for (;;) { }
    }
    const uint32_t changed = audio_uart_page_update_core_44d63a(
        page, audio_uart_lv_list_first_482ce4,
        audio_uart_lv_list_next_482cfa);
    page_update_callback const callback = callback_at(page);
    if (callback != 0 && (uint8_t)changed == 0u)
        callback(page, 0u);
}
