/* Apollo display iteration, idle callbacks and render-task refresh scheduling. */
#include <stdint.h>
/* Stock-RAM literals rewritten to named objects (sim-test wave 2026-10-26,
 * .waves/sim-fix/apply.py): g2ref_X is the linker symbol X. */
#include <stdint.h>
extern unsigned char g2ref_audio_uart_lv_tick_state[] __asm__("audio_uart_lv_tick_state");

extern uint32_t audio_uart_lv_render_task_evaluate_48458e(void *display, void *layer);
extern void audio_uart_lv_draw_dispatch_request_48462e(void);

/* Retired: stock 0x44fa22 is upstream lv_display_get_next (lvgl/src/display/lv_display.c); this name is a link alias. */
void *audio_uart_lv_display_next_44fa22(void *previous);

void audio_uart_lv_render_idle_callbacks_484528(void) {
    uint32_t node = *(volatile uint32_t *)(uintptr_t)((uint32_t)(uintptr_t)g2ref_audio_uart_lv_tick_state+0x84u);
    while (node != 0u) {
        uint32_t callback = *(uint32_t *)(uintptr_t)(node + 0x14u);
        if (callback != 0u)
            ((void (*)(void *))(uintptr_t)callback)((void *)(uintptr_t)node);
        node = *(uint32_t *)(uintptr_t)node;
    }
}

void audio_uart_lv_refresh_tasks_484548(void) {
    uint8_t work_pending = 0u;
    for (uint8_t *display = (uint8_t *)audio_uart_lv_display_next_44fa22(0);
         display != (void *)0;
         display = (uint8_t *)audio_uart_lv_display_next_44fa22(display)) {
        for (uint32_t layer = *(uint32_t *)(void *)(display + 0x2acu);
             layer != 0u;
             layer = *(uint32_t *)(uintptr_t)(layer + 0x4cu)) {
            if (audio_uart_lv_render_task_evaluate_48458e(display,
                    (void *)(uintptr_t)layer) != 0u)
                work_pending = 1u;
        }
        if (work_pending == 0u) {
            audio_uart_lv_render_idle_callbacks_484528();
            audio_uart_lv_draw_dispatch_request_48462e();
        }
    }
}
