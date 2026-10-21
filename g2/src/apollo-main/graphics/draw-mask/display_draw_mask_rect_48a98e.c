/* Apollo Main LVGL mask rectangle task, native 0x48a98e..0x48aa38.
 * Based on pinned LVGL 9.3 lv_draw_mask.c with stock offsets and events. */
#include <stdint.h>

extern uint32_t audio_uart_lv_color_has_alpha_440fc4(uint32_t);
extern void audio_uart_lvgl_log(uint32_t, const char *, uint32_t,
                                const char *, const char *, ...);
extern void *audio_uart_lv_render_task_alloc_4843ee(void *, const void *);
extern void *audio_uart_lv_malloc(uint32_t);
extern void *audio_uart_lv_grid_copy_454738(void *, const void *, uint32_t);
extern uint32_t audio_uart_lv_obj_has_flag_43e0e0(void *, uint32_t);
extern void audio_lv_object_clear_flag_43dfa4(uint32_t, uint32_t);
extern void audio_lv_object_flag_43ded4(uint32_t, uint32_t);
extern uint32_t audio_uart_lv_obj_event_451670(void *, uint32_t, void *);
extern uint32_t audio_uart_lv_render_task_queue_484476(void *, void *, uint32_t);

static const char source_path[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\draw\\lv_draw_mask.c";
static const char function_name[] = "lv_draw_mask_rect";
static const char no_alpha[] = "Only layers with alpha channel can be masked";
static const char alloc_assert[] = "t->draw_dsc != NULL";
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

void audio_uart_lv_draw_mask_rect_48a98e(void *layer_arg, const void *dsc_arg)
{
    uint8_t *const layer = (uint8_t *)layer_arg;
    const uint8_t *const dsc = (const uint8_t *)dsc_arg;
    if (audio_uart_lv_color_has_alpha_440fc4(layer[0x14u]) == 0u) {
        audio_uart_lvgl_log(2u, source_path, 0x35u, function_name, no_alpha);
        return;
    }
    uint8_t *const task = (uint8_t *)audio_uart_lv_render_task_alloc_4843ee(
        layer, layer + 4u);
    uint8_t *const copy = (uint8_t *)audio_uart_lv_malloc(0x34u);
    wr(task, 0x54u, (uint32_t)(uintptr_t)copy);
    if (copy == 0) {
        audio_uart_lvgl_log(3u, source_path, 0x3du, function_name,
                            assert_format, alloc_assert, alloc_failed);
        for (;;) *(volatile uint32_t *)(uintptr_t)0xffffffffu = 0u;
    }
    (void)audio_uart_lv_grid_copy_454738(copy, dsc, 0x34u);
    task[4u] = 0x0bu;
    wr(copy, 0x10u, (uint32_t)(uintptr_t)layer);
    const uint32_t object = rd(copy, 0u);
    if (object != 0u && audio_uart_lv_obj_has_flag_43e0e0(
            (void *)(uintptr_t)object, 0x80000u) != 0u) {
        audio_lv_object_clear_flag_43dfa4(object, 0x80000u);
        (void)audio_uart_lv_obj_event_451670(
            (void *)(uintptr_t)rd(dsc, 0u), 0x22u, task);
        audio_lv_object_flag_43ded4(object, 0x80000u);
    }
    (void)audio_uart_lv_render_task_queue_484476(layer, task, 0u);
}
