/* Apollo render-task allocation and layer insertion, native 0x4843ee..0x484475. */
#include <stdint.h>

extern void *audio_uart_lv_heap_alloc(uint32_t bytes);
extern void audio_uart_lvgl_log(uint32_t level, const char *source, uint32_t line,
                                const char *format, ...);

void *audio_uart_lv_render_task_alloc_4843ee(void *layer, const void *area) {
    uint8_t *task = (uint8_t *)audio_uart_lv_heap_alloc(0x5cu);
    if (task == (void *)0) {
        /* Stock treats allocator failure as fatal. Return is unreachable in that path. */
        for (;;) { }
    }
    const uint8_t *box = (const uint8_t *)area;
    const uint8_t *layer_area = (const uint8_t *)layer + 0x18u;
    for (unsigned i = 0; i < 16u; ++i) {
        task[8u + i] = box[i];
        task[0x18u + i] = box[i];
        task[0x38u + i] = layer_area[i];
    }
    *(uint32_t *)(void *)(task + 0x48u) = (uint32_t)(uintptr_t)layer;
    *(uint32_t *)(void *)(task + 0x50u) = 1u;
    uint32_t *link = (uint32_t *)(void *)((uint8_t *)layer + 0x44u);
    while (*link != 0u) link = (uint32_t *)(uintptr_t)*link;
    *link = (uint32_t)(uintptr_t)task;
    return task;
}
