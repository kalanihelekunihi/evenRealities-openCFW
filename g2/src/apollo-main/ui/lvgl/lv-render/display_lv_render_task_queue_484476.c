/* Apollo LV render-task queue finalization, native 0x484476..0x484527. */
#include <stdint.h>
/* Stock-RAM literals rewritten to named objects (sim-test wave 2026-10-26,
 * .waves/sim-fix/apply.py): g2ref_X is the linker symbol X. */
#include <stdint.h>
extern unsigned char g2ref_audio_uart_lv_tick_state[] __asm__("audio_uart_lv_tick_state");

extern uint32_t audio_uart_lv_obj_has_flag_43e0e0(void *object, uint32_t flags);
extern uint32_t audio_uart_lv_obj_event_451670(void *object, uint32_t code, void *param);
extern void lv_log_add(uint32_t level, const char *source, uint32_t line,
                                const char *format, ...);
extern void audio_uart_lv_refresh_tasks_484548(void);

/* Stock 0x73f4d0; also the function's return value on the error path. */
static const char g2_draw_task_not_taken[] = "the draw task was not taken by any units";

uint32_t audio_uart_lv_render_task_queue_484476(void *descriptor, void *task,
                                                 uint32_t passthrough) {
    uint8_t *t = (uint8_t *)task;
    uint8_t *d = (uint8_t *)(uintptr_t)*(uint32_t *)(void *)(t + 0x54u);
    *(uint32_t *)(void *)(d + 0x10u) = (uint32_t)(uintptr_t)descriptor;
    volatile uint8_t *state = (volatile uint8_t *)(uintptr_t)((uint32_t)(uintptr_t)g2ref_audio_uart_lv_tick_state+0x84u);
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
            lv_log_add(2u, "D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\draw\\lv_draw.c" /* stock 0x6e859c */, 0x9fu,
                                "lv_draw_finalize_task_creation" /* stock 0x760a90 */,
                                g2_draw_task_not_taken /* stock 0x73f4d0 */);
            *(uint32_t *)(void *)(t + 0x50u) = 3u;
            passthrough = (uint32_t)(uintptr_t)g2_draw_task_not_taken;
        } else {
            audio_uart_lv_refresh_tasks_484548();
        }
    }
    return passthrough;
}
