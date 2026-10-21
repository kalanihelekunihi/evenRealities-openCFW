/* Apollo LV base event-state callback, native 0x43e442..0x43e63d.
 * Draw providers retain their native address labels until separately owned. */
#include <stdint.h>

extern uint32_t audio_uart_page_event_code_450286(const void *);
extern void *audio_uart_lv_event_layer_451960(void *);
extern uint32_t audio_uart_lv_event_state_metric_43de54(void *, uint32_t);
extern uint32_t audio_uart_lv_event_state_metric_43de4a(void *, uint32_t);
extern uint32_t audio_uart_lv_event_state_metric_43dd72(void *, uint32_t);
extern uint32_t audio_uart_lv_event_state_metric_43dd7c(void *, uint32_t);
extern uint32_t audio_uart_lv_event_state_metric_43dda8(void *, uint32_t);
extern uint32_t audio_uart_lv_event_state_metric_43de6a(void *, uint32_t);
extern uint32_t audio_uart_lv_event_state_metric_43ddb4(void *, uint32_t);
extern uint32_t audio_uart_lv_event_state_metric_43ddcc(void *, uint32_t);
extern uint32_t audio_uart_lv_event_state_metric_43ddc0(void *, uint32_t);
extern uint32_t audio_uart_lv_event_state_metric_43ddd8(void *, uint32_t);
extern uint32_t audio_uart_lv_event_state_metric_43de06(void *, uint32_t);
extern uint32_t audio_uart_lv_event_state_metric_43ddfc(void *, uint32_t);
extern void audio_uart_lv_event_area_copy_43dcc0(void *, const void *);
extern void audio_uart_lv_area_expand_450b98(void *, int32_t, int32_t);
extern uint32_t audio_uart_lv_area_contains_450f28(const void *, const void *, uint32_t);
extern void audio_uart_lv_draw_task_init_451b9c(void *);
extern void audio_uart_lv_draw_task_build_452616(void *, uint32_t, void *);
extern void audio_uart_lv_draw_task_render_451c6e(void *, void *, const void *);
extern void audio_uart_lv_draw_scrollbars_43e63e(void *, void *);

static uint32_t word(const uint8_t *p) {
    return (uint32_t)p[0] | ((uint32_t)p[1] << 8u) |
           ((uint32_t)p[2] << 16u) | ((uint32_t)p[3] << 24u);
}

static void draw_area(void *object, void *layer, uint32_t clear_fields,
                      uint32_t test_style) {
    uint8_t task[0x70];
    uint8_t area[16];
    audio_uart_lv_draw_task_init_451b9c(task);
    if (clear_fields != 0u) {
        task[0x20] = 0u;
        task[0x3b] = 0u;
        task[0x58] = 0u;
        task[0x6c] = 0u;
    }
    uint32_t layer_address = (uint32_t)(uintptr_t)layer;
    task[0x10] = (uint8_t)layer_address;
    task[0x11] = (uint8_t)(layer_address >> 8u);
    task[0x12] = (uint8_t)(layer_address >> 16u);
    task[0x13] = (uint8_t)(layer_address >> 24u);
    audio_uart_lv_draw_task_build_452616(object, 0u, task);
    if (test_style != 0u && audio_uart_lv_event_state_metric_43de06(object, 0u) != 0u)
        task[0x49] = (uint8_t)(task[0x49] | 0x20u);
    uint32_t x = audio_uart_lv_event_state_metric_43dd72(object, 0u);
    uint32_t y = audio_uart_lv_event_state_metric_43dd7c(object, 0u);
    audio_uart_lv_event_area_copy_43dcc0(area, (const uint8_t *)object + 0x14u);
    audio_uart_lv_area_expand_450b98(area, (int32_t)x, (int32_t)y);
    audio_uart_lv_draw_task_render_451c6e(layer, task, area);
}

void audio_uart_lv_obj_event_state_43e442(void *event) {
    uint8_t *e = (uint8_t *)event;
    uint32_t code = audio_uart_page_event_code_450286(event);
    void *object = (void *)(uintptr_t)word(e);
    if (code == 0x1au) {
        uint8_t *param = (uint8_t *)(uintptr_t)word(e + 0x10u);
        if (param[0] == 2u) return;
        if (audio_uart_lv_event_state_metric_43de54(object, 0u) != 0u) {
            param[0] = 2u;
            return;
        }
        uint32_t radius = audio_uart_lv_event_state_metric_43de4a(object, 0u);
        int32_t x = (int32_t)audio_uart_lv_event_state_metric_43dd72(object, 0u);
        int32_t y = (int32_t)audio_uart_lv_event_state_metric_43dd7c(object, 0u);
        uint8_t area[16];
        audio_uart_lv_event_area_copy_43dcc0(area, (const uint8_t *)object + 0x14u);
        audio_uart_lv_area_expand_450b98(area, x, y);
        void *clip = (void *)(uintptr_t)word(param + 4u);
        if (audio_uart_lv_area_contains_450f28(clip, area, radius) == 0u) {
            param[0] = 1u;
            return;
        }
        if (audio_uart_lv_event_state_metric_43dda8(object, 0u) < 0xfdu ||
            audio_uart_lv_event_state_metric_43de6a(object, 0u) < 0xfdu ||
            (audio_uart_lv_event_state_metric_43ddb4(object, 0u) != 0u &&
             (audio_uart_lv_event_state_metric_43ddcc(object, 0u) < 0xfdu ||
              audio_uart_lv_event_state_metric_43ddc0(object, 0u) < 0xfdu))) {
            param[0] = 1u;
            return;
        }
        uint32_t table = audio_uart_lv_event_state_metric_43ddd8(object, 0u);
        if (table != 0u) {
            const uint8_t *entries = (const uint8_t *)(uintptr_t)table;
            for (uint32_t index = 0; index < entries[10]; ++index) {
                if (entries[3u + index * 5u] < 0xfdu) {
                    param[0] = 1u;
                    return;
                }
            }
        }
        param[0] = 0u;
    } else if (code == 0x1du) {
        void *layer = audio_uart_lv_event_layer_451960(event);
        draw_area(object, layer, 0u, 1u);
    } else if (code == 0x20u) {
        void *layer = audio_uart_lv_event_layer_451960(event);
        audio_uart_lv_draw_scrollbars_43e63e(object, layer);
        if (audio_uart_lv_event_state_metric_43ddfc(object, 0u) != 0u &&
            audio_uart_lv_event_state_metric_43de06(object, 0u) != 0u)
            draw_area(object, layer, 1u, 0u);
    }
}
