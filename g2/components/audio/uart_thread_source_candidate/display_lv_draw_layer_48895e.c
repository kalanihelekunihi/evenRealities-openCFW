/* Apollo Main LVGL layer draw task, native 0x48895e..0x488a38.
 * Control flow follows pinned LVGL 9.3 lv_draw_image.c lv_draw_layer. */
#include <stdint.h>

extern void *audio_uart_lv_render_task_alloc_4843ee(void *, const void *);
extern void *audio_uart_lv_malloc(uint32_t);
extern void *audio_uart_lv_grid_copy_454738(void *, const void *, uint32_t);
extern void *audio_uart_display_area_copy_439c04(void *, const void *, uint32_t);
extern int32_t audio_uart_lv_area_width_451598(const void *);
extern int32_t audio_uart_lv_area_height_4515a4(const void *);
extern void audio_uart_ambiq_transform_area_488cda(void *, int32_t, int32_t,
                                                     int32_t, int32_t, int32_t,
                                                     const void *);
extern void audio_uart_ambiq_area_move_450bb2(void *, int32_t, int32_t);
extern uint32_t audio_uart_lv_render_task_queue_484476(void *, void *, uint32_t);
extern void audio_uart_lvgl_log(uint32_t, const char *, uint32_t,
                                const char *, const char *, ...);

static const char source_path[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\draw\\lv_draw_image.c";
static const char source_func[] = "lv_draw_layer";
static const char alloc_assert[] = "new_image_dsc != NULL";
static const char assert_format[] = "Asserted at expression: %s (%s)";
static const char alloc_failed[] = "Out of memory";

static uint32_t rd(const uint8_t *p, uint32_t offset)
{
    return *(const uint32_t *)(const void *)(p + offset);
}
static void wr(uint8_t *p, uint32_t offset, uint32_t value)
{
    *(uint32_t *)(void *)(p + offset) = value;
}

void audio_uart_lv_draw_layer_48895e(void *layer_arg, const void *dsc_arg,
                                      const void *coords_arg)
{
    uint8_t *const layer = (uint8_t *)layer_arg;
    const uint8_t *const dsc = (const uint8_t *)dsc_arg;
    const uint8_t *const coords = (const uint8_t *)coords_arg;
    if ((int32_t)rd(dsc, 0x34u) < 1 || (int32_t)rd(dsc, 0x38u) < 1)
        return;

    uint8_t *const task = (uint8_t *)audio_uart_lv_render_task_alloc_4843ee(
        layer, coords);
    uint8_t *const image_dsc = (uint8_t *)audio_uart_lv_malloc(0x6cu);
    if (image_dsc == 0) {
        audio_uart_lvgl_log(3u, source_path, 0x4fu, source_func,
                            assert_format, alloc_assert, alloc_failed);
        for (;;) *(volatile uint32_t *)(uintptr_t)0xffffffffu = 0u;
    }
    wr(task, 0x54u, (uint32_t)(uintptr_t)image_dsc);
    (void)audio_uart_lv_grid_copy_454738(image_dsc, dsc, 0x6cu);
    task[4u] = 7u;
    wr(task, 0x50u, 0u);
    const int32_t height = audio_uart_lv_area_height_4515a4(coords);
    const int32_t width = audio_uart_lv_area_width_451598(coords);
    audio_uart_ambiq_transform_area_488cda(task + 0x18u, width, height,
        (int32_t)rd(dsc, 0x30u), (int32_t)(uint16_t)rd(dsc, 0x34u),
        (int32_t)(uint16_t)rd(dsc, 0x38u), dsc + 0x44u);
    audio_uart_ambiq_area_move_450bb2(task + 0x18u,
        (int32_t)rd(coords, 0u), (int32_t)rd(coords, 4u));
    if (rd(image_dsc, 0x60u) == 0xe0000001u)
        (void)audio_uart_display_area_copy_439c04(image_dsc + 0x58u,
                                                   coords, 0x10u);
    uint8_t *const child = (uint8_t *)(uintptr_t)rd(dsc, 0x1cu);
    child[0x50u] = 1u;
    (void)audio_uart_lv_render_task_queue_484476(layer, task, 0u);
}
