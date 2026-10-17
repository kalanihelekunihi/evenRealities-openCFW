/* Apollo Main LVGL refresh layout pass, stock 0x45383c..0x4539b2. */
#include <stdint.h>

extern uint8_t audio_uart_display_lv_root[];
extern void audio_uart_lv_display_pre_refresh_454692(void *);
extern uint32_t audio_uart_lv_display_width_44fa7e(void *);
extern uint32_t audio_uart_lv_display_height_44faa8(void *);
extern void *audio_uart_lv_list_first(void *);
extern void *audio_uart_lv_list_next(void *, void *);
extern void *audio_uart_lv_list_insert_before_482b56(void *, void *);
extern void audio_uart_lv_list_remove_482c0e(void *, void *);
extern void audio_uart_lv_heap_free(void *);
extern int32_t audio_uart_lv_area_subtract_450c2a(int32_t *, const int32_t *,
                                                    const int32_t *);
extern void *audio_uart_display_area_copy_439c04(void *, const void *, uint32_t);
extern uint32_t audio_uart_lv_area_intersect_450bcc(int32_t *, const int32_t *,
                                                      const int32_t *);
extern void audio_uart_lv_draw_buf_copy_48ad42(void *, const void *,
                                                 const void *, const void *);
extern void audio_uart_lv_list_clear_custom_482c9a(void *, void (*)(void *));

static uint32_t word(const uint8_t *bytes, uint32_t offset)
{
    return *(const uint32_t *)(const void *)(bytes + offset);
}

static void clear(uint8_t *bytes, uint32_t size)
{
    for (uint32_t i = 0; i < size; ++i) bytes[i] = 0u;
}

void audio_uart_lv_refresh_layout_45383c(void)
{
    uint8_t *const display = (uint8_t *)(uintptr_t)word(
        audio_uart_display_lv_root, 0x10u);
    if (display[0x39u] != 1u || word(display, 0x20u) == 0u) return;
    uint8_t *const list = display + 0x268u;
    if (word(list, 4u) == 0u && word(list, 8u) == 0u) return;
    audio_uart_lv_display_pre_refresh_454692(display);

    void *const buffer = (void *)(uintptr_t)word(display, 0x24u);
    void *const source = (void *)(uintptr_t)word(
        display, word(display, 0x24u) == word(display, 0x1cu) ? 0x20u : 0x1cu);
    const uint32_t width = audio_uart_lv_display_width_44fa7e(display);
    const uint32_t height = audio_uart_lv_display_height_44faa8(display);
    int32_t pieces[16];
    clear((uint8_t *)pieces, sizeof pieces);

    for (uint32_t index = 0u;
         (uint16_t)index < word(display, 0x260u); ++index) {
        const uint32_t slot = (uint16_t)index;
        if (display[0x240u + slot] != 0u) continue;
        void *node = audio_uart_lv_list_first(list);
        while (node != 0) {
            void *const next = audio_uart_lv_list_next(list, node);
            const int32_t count = audio_uart_lv_area_subtract_450c2a(
                pieces, (const int32_t *)node,
                (const int32_t *)(const void *)(display + 0x40u + slot * 16u));
            if ((int8_t)count != -1) {
                for (int32_t part = 0; part < (int8_t)count; ++part) {
                    void *const inserted = audio_uart_lv_list_insert_before_482b56(
                        list, node);
                    (void)audio_uart_display_area_copy_439c04(
                        inserted, pieces + part * 4, 16u);
                }
                audio_uart_lv_list_remove_482c0e(list, node);
                audio_uart_lv_heap_free(node);
            }
            node = next;
        }
    }

    int32_t bounds[4];
    clear((uint8_t *)bounds, sizeof bounds);
    bounds[2] = (int32_t)(width - 1u);
    bounds[3] = (int32_t)(height - 1u);
    for (void *node = audio_uart_lv_list_first(list); node != 0;
         node = audio_uart_lv_list_next(list, node)) {
        (void)audio_uart_lv_area_intersect_450bcc(
            (int32_t *)node, (const int32_t *)node, bounds);
        audio_uart_lv_draw_buf_copy_48ad42(buffer, node, source, node);
    }
    audio_uart_lv_list_clear_custom_482c9a(list, 0);
}
