/* Apollo LV render-task queue finalization, native 0x484476..0x484527. */
#include <stdint.h>

extern uint32_t audio_uart_lv_obj_has_flag_43e0e0(void *object, uint32_t flags);
extern uint32_t audio_uart_lv_obj_event_451670(void *object, uint32_t code, void *param);
extern void audio_uart_lvgl_log(uint32_t level, const char *source, uint32_t line,
                                const char *format, ...);
extern void audio_uart_lv_refresh_tasks_484548(void);

uint32_t audio_uart_lv_render_task_queue_484476(void *descriptor, void *task,
                                                 uint32_t passthrough) {
    uint8_t *t = (uint8_t *)task;
    uint8_t *d = (uint8_t *)(uintptr_t)*(uint32_t *)(void *)(t + 0x54u);
    *(uint32_t *)(void *)(d + 0x10u) = (uint32_t)(uintptr_t)descriptor;
    volatile uint8_t *state = (volatile uint8_t *)(uintptr_t)0x2006f684u;
    const uint8_t busy = state[0x20u];
    if (busy == 0u) {
        void *object = (void *)(uintptr_t)*(uint32_t *)(void *)d;
        if (object != (void *)0 &&
            audio_uart_lv_obj_has_flag_43e0e0(object, 0x80000u) != 0u) {
            state[0x20u] = 1u;
            (void)audio_uart_lv_obj_event_451670(object, 0x22u, task);
            state[0x20u] = 0u;
        }
    }
    t[0x59u] = 100u;
    t[0x58u] = 0u;
    for (uint32_t node = *(volatile uint32_t *)(void *)state; node != 0u;
         node = *(uint32_t *)(uintptr_t)node) {
        uint32_t callback = *(uint32_t *)(uintptr_t)(node + 0x10u);
        if (callback != 0u)
            ((void (*)(void *, void *))(uintptr_t)callback)((void *)(uintptr_t)node, task);
    }
    if (busy == 0u) {
        if (t[0x58u] == 0u) {
            audio_uart_lvgl_log(2u, (const char *)(uintptr_t)0x6e859cu, 0x9fu,
                                (const char *)(uintptr_t)0x760a90u,
                                (const char *)(uintptr_t)0x73f4d0u);
            *(uint32_t *)(void *)(t + 0x50u) = 3u;
            passthrough = 0x73f4d0u;
        } else {
            audio_uart_lv_refresh_tasks_484548();
        }
    }
    return passthrough;
}
