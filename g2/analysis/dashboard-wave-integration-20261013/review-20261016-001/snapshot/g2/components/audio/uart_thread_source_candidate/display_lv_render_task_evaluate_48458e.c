/* Apollo LV render-task evaluation, native 0x48458e..0x484621. */
#include <stdint.h>

extern void audio_uart_lv_render_task_free_4848e8(void *task, void *display);
extern void audio_uart_lv_draw_dispatch_request_48462e(void);

uint32_t audio_uart_lv_render_task_evaluate_48458e(void *display, void *layer) {
    uint8_t *l = (uint8_t *)layer;
    uint32_t previous = 0u;
    uint32_t task = *(uint32_t *)(void *)(l + 0x44u);
    while (task != 0u) {
        uint32_t next = *(uint32_t *)(uintptr_t)task;
        if (*(uint32_t *)(uintptr_t)(task + 0x50u) == 3u) {
            audio_uart_lv_render_task_free_4848e8((void *)(uintptr_t)task, display);
            if (previous == 0u)
                *(uint32_t *)(void *)(l + 0x44u) = next;
            else
                *(uint32_t *)(uintptr_t)previous = next;
        } else {
            previous = task;
        }
        task = next;
    }
    if (*(uint32_t *)(void *)(l + 0x48u) != 0u && l[0x50u] != 0u &&
        *(uint32_t *)(void *)(l + 0x44u) == 0u) {
        uint8_t *parent = (uint8_t *)(uintptr_t)*(uint32_t *)(void *)(l + 0x48u);
        for (uint32_t candidate = *(uint32_t *)(void *)(parent + 0x44u);
             candidate != 0u;
             candidate = *(uint32_t *)(uintptr_t)candidate) {
            uint8_t *p = (uint8_t *)(uintptr_t)candidate;
            if (p[4] == 7u && *(uint32_t *)(void *)(p + 0x50u) == 0u &&
                *(uint32_t *)(uintptr_t)(*(uint32_t *)(void *)(p + 0x54u) + 0x1cu) ==
                    (uint32_t)(uintptr_t)layer) {
                *(uint32_t *)(void *)(p + 0x50u) = 1u;
                audio_uart_lv_draw_dispatch_request_48462e();
                break;
            }
        }
        return 0u;
    }
    uint32_t work_pending = 0u;
    for (uint32_t backend = *(volatile uint32_t *)(uintptr_t)0x2006f684u;
         backend != 0u;
         backend = *(uint32_t *)(uintptr_t)backend) {
        uint32_t callback = *(uint32_t *)(uintptr_t)(backend + 0x0cu);
        int32_t status = ((int32_t (*)(void *, void *))(uintptr_t)callback)(
            (void *)(uintptr_t)backend, layer);
        if (status != -1) work_pending = 1u;
    }
    return work_pending;
}
