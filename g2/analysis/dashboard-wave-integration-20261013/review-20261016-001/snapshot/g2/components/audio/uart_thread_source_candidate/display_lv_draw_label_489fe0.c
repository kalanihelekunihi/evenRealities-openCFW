/* Apollo LVGL draw-label task submission 0x489fe0..0x48a0bd and
 * local text duplication 0x4547f2. Based on pinned LVGL lv_draw_label.c.
 */
#include <stdint.h>

extern void *audio_uart_lv_render_task_alloc_4843ee(void *, const void *);
extern void *audio_uart_lv_malloc(uint32_t);
extern void audio_uart_lv_grid_copy_454738(void *, const void *, uint32_t);
extern uint32_t audio_uart_lv_render_task_queue_484476(void *, void *, uint32_t);
extern uint32_t audio_uart_lv_string_length_454768(const char *);
extern void audio_uart_lvgl_log(uint32_t, const char *, uint32_t,
    const char *, const char *, ...);

static uint32_t get32(const uint8_t *p) {
    return (uint32_t)p[0] | ((uint32_t)p[1] << 8u) |
           ((uint32_t)p[2] << 16u) | ((uint32_t)p[3] << 24u);
}
static void put32(uint8_t *p, uint32_t v) {
    p[0] = (uint8_t)v; p[1] = (uint8_t)(v >> 8u);
    p[2] = (uint8_t)(v >> 16u); p[3] = (uint8_t)(v >> 24u);
}

char *audio_uart_lv_draw_task_strdup_4547f2(const char *text) {
    uint32_t length = audio_uart_lv_string_length_454768(text);
    char *copy = (char *)audio_uart_lv_malloc(length + 1u);
    if (copy == 0) return 0;
    audio_uart_lv_grid_copy_454738(copy, text, length);
    copy[length] = '\0';
    return copy;
}

void audio_uart_lv_draw_label_489fe0(void *layer, const void *descriptor,
                                      const void *area) {
    const uint8_t *d = (const uint8_t *)descriptor;
    if (d[0x50u] < 3u) return;
    const uint8_t *text = (const uint8_t *)(uintptr_t)get32(d + 0x1cu);
    if (text == 0 || text[0] == 0u) return;
    if (get32(d + 0x20u) == 0u) {
        audio_uart_lvgl_log(2u,
            "D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\draw\\lv_draw_label.c",
            0x6au, "lv_draw_label", "dsc->font == NULL");
        return;
    }
    uint8_t *task = (uint8_t *)audio_uart_lv_render_task_alloc_4843ee(layer, area);
    uint8_t *copy = (uint8_t *)audio_uart_lv_malloc(0x64u);
    put32(task + 0x54u, (uint32_t)(uintptr_t)copy);
    if (copy == 0) {
        audio_uart_lvgl_log(3u,
            "D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\draw\\lv_draw_label.c",
            0x72u, "lv_draw_label",
            "Asserted at expression: %s (%s)", "new_dsc != NULL", "Out of memory");
        for (;;) *(volatile uint32_t *)(uintptr_t)0xffffffffu = 0u;
    }
    audio_uart_lv_grid_copy_454738(copy, d, 0x64u);
    task[4u] = 5u;
    if ((d[0x54u] & 1u) != 0u) {
        const char *local = audio_uart_lv_draw_task_strdup_4547f2((const char *)text);
        put32(copy + 0x1cu, (uint32_t)(uintptr_t)local);
        if (local == 0) {
            audio_uart_lvgl_log(3u,
                "D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\draw\\lv_draw_label.c",
                0x7au, "lv_draw_label",
                "Asserted at expression: %s (%s)", "new_dsc->text != NULL", "Out of memory");
            for (;;) *(volatile uint32_t *)(uintptr_t)0xffffffffu = 0u;
        }
    }
    (void)audio_uart_lv_render_task_queue_484476(layer, task, 0u);
}
