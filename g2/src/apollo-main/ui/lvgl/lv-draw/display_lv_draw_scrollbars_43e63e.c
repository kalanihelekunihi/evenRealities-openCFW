/* Apollo LV event scrollbar drawing wrapper, native 0x43e63e..0x43e6a5. */
#include <stdint.h>

extern void audio_uart_lv_get_scrollbar_areas_44eb28(void *, void *, void *);
extern uint32_t audio_uart_lv_area_size_450b80(const void *);
extern uint32_t audio_uart_lv_scrollbar_draw_descriptor_43e6a6(void *, void *);
extern void audio_uart_lv_draw_task_render_451c6e(void *, void *, const void *);

static void put32(uint8_t *p, uint32_t value) {
    p[0] = (uint8_t)value; p[1] = (uint8_t)(value >> 8u);
    p[2] = (uint8_t)(value >> 16u); p[3] = (uint8_t)(value >> 24u);
}

void audio_uart_lv_draw_scrollbars_43e63e(void *object, void *layer) {
    uint8_t first[16], second[16];
    uint8_t task[0x70];
    audio_uart_lv_get_scrollbar_areas_44eb28(object, first, second);
    if (audio_uart_lv_area_size_450b80(first) == 0u &&
        audio_uart_lv_area_size_450b80(second) == 0u)
        return;
    if ((uint8_t)audio_uart_lv_scrollbar_draw_descriptor_43e6a6(object, task) != 1u)
        return;
    if (audio_uart_lv_area_size_450b80(first) != 0u) {
        put32(task + 8u, 0u);
        audio_uart_lv_draw_task_render_451c6e(layer, task, first);
    }
    if (audio_uart_lv_area_size_450b80(second) != 0u) {
        put32(task + 8u, 1u);
        audio_uart_lv_draw_task_render_451c6e(layer, task, second);
    }
}
