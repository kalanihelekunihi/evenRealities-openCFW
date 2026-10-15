/* Apollo scrollbar draw-task descriptor, native 0x43e6a6..0x43e7d1. */
#include <stdint.h>

extern void audio_uart_lv_draw_task_init_451b9c(void *task);
extern uint32_t audio_uart_lv_event_state_metric_43dda8(void *, uint32_t);
extern uint32_t audio_uart_lv_scrollbar_metric_43dd9a(void *, uint32_t);
extern uint32_t audio_uart_lv_scrollbar_metric_43ddf0(void *, uint32_t);
extern uint32_t audio_uart_lv_event_state_metric_43ddfc(void *, uint32_t);
extern uint32_t audio_uart_lv_scrollbar_metric_43dde2(void *, uint32_t);
extern uint32_t audio_uart_lv_scrollbar_metric_43de3e(void *, uint32_t);
extern int32_t audio_uart_lv_scrollbar_metric_43de1c(void *, uint32_t);
extern uint32_t audio_uart_lv_scrollbar_metric_43de26(void *, uint32_t);
extern uint32_t audio_uart_lv_scrollbar_metric_43de30(void *, uint32_t);
extern uint32_t audio_uart_lv_effective_opacity_44c47a(void *, uint32_t);
extern uint32_t audio_uart_lv_event_state_metric_43de4a(void *, uint32_t);
extern void *audio_queue_copy_bytes(void *, const void *, uint32_t);

static void put32(uint8_t *p, uint32_t value) {
    p[0] = (uint8_t)value; p[1] = (uint8_t)(value >> 8u);
    p[2] = (uint8_t)(value >> 16u); p[3] = (uint8_t)(value >> 24u);
}
static void color3(uint8_t *out, uint32_t color) {
    (void)audio_queue_copy_bytes(out, &color, 3u);
}

uint32_t audio_uart_lv_scrollbar_draw_descriptor_43e6a6(void *object, void *descriptor) {
    uint8_t *task = (uint8_t *)descriptor;
    const uint32_t selector = 0x10000u;
    audio_uart_lv_draw_task_init_451b9c(task);
    task[0x20] = (uint8_t)audio_uart_lv_event_state_metric_43dda8(object, selector);
    if (task[0x20] > 2u)
        color3(task + 0x21u, audio_uart_lv_scrollbar_metric_43dd9a(object, selector));
    task[0x48] = (uint8_t)audio_uart_lv_scrollbar_metric_43ddf0(object, selector);
    if (task[0x48] > 2u) {
        int32_t width = (int32_t)audio_uart_lv_event_state_metric_43ddfc(object, selector);
        put32(task + 0x44u, (uint32_t)width);
        if (width < 1)
            task[0x48] = 0u;
        else
            color3(task + 0x3eu, audio_uart_lv_scrollbar_metric_43dde2(object, selector));
    }
    task[0x6c] = (uint8_t)audio_uart_lv_scrollbar_metric_43de3e(object, selector);
    if (task[0x6c] > 2u) {
        int32_t width = audio_uart_lv_scrollbar_metric_43de1c(object, selector);
        put32(task + 0x5cu, (uint32_t)width);
        if (width < 1)
            task[0x6c] = 0u;
        else {
            put32(task + 0x68u,
                  audio_uart_lv_scrollbar_metric_43de26(object, selector));
            color3(task + 0x59u,
                   audio_uart_lv_scrollbar_metric_43de30(object, selector));
        }
    }
    uint8_t opacity = (uint8_t)audio_uart_lv_effective_opacity_44c47a(object, selector);
    if (opacity < 0xfdu) {
        uint8_t scaled = (uint8_t)(((uint32_t)opacity * task[0x20]) >> 8u);
        task[0x20] = scaled;
        task[0x48] = scaled;
        task[0x6c] = scaled;
    }
    if (task[0x20] == 0u && task[0x48] == 0u && task[0x6c] == 0u)
        return 0u;
    put32(task + 0x1cu, audio_uart_lv_event_state_metric_43de4a(object, selector));
    return 1u;
}
