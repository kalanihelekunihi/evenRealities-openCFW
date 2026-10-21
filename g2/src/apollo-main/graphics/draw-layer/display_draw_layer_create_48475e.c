/* Apollo Main LVGL layer constructor, stock 0x48475e..0x4847c4.
 * Based on pinned LVGL 9.3 lv_draw.c, with stock layer size and offsets. */
#include <stdint.h>

extern void *audio_uart_lv_heap_alloc(uint32_t);
extern void audio_uart_lv_render_layer_init_4847c4(void *, void *,
                                                    uint32_t, const void *);
extern void audio_uart_lvgl_log(uint32_t, const char *, uint32_t,
                                const char *, const char *, ...);

static const char source[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\draw\\lv_draw.c";
static const char function[] = "lv_draw_layer_create";
static const char format[] = "Asserted at expression: %s (%s)";
static const char expression[] = "new_layer != NULL";
static const char detail[] = "Out of memory";

void *audio_uart_lv_draw_layer_create_48475e(void *parent_arg,
                                               uint32_t color_format,
                                               const void *area)
{
    uint8_t *const child = (uint8_t *)audio_uart_lv_heap_alloc(0x58u);
    if (child == 0) {
        audio_uart_lvgl_log(3u, source, 0x18fu, function, format,
                            expression, detail);
        for (;;) *(volatile uint32_t *)(uintptr_t)0xffffffffu = 0u;
    }
    audio_uart_lv_render_layer_init_4847c4(child, parent_arg,
                                            (uint8_t)color_format, area);
    if (parent_arg != 0) {
        const uint8_t *const parent = (const uint8_t *)parent_arg;
        child[0x38u] = parent[0x38u];
        *(uint32_t *)(void *)(child + 0x39u) =
            *(const uint32_t *)(const void *)(parent + 0x39u);
    }
    return child;
}
