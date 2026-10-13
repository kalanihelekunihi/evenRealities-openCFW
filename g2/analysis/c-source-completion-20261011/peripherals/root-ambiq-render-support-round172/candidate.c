#include <stdint.h>
extern void audio_uart_ambiq_execute_drawing_4c7752(void *);
extern void audio_uart_lv_draw_dispatch_request_48462e(void);
extern int32_t audio_queue_delete(void *);
/* Native4c752e..4c7548: drawing may mutate the task's draw unit. */
void audio_uart_ambiq_execute_unit_4c752e(void *task) {
    volatile uint8_t *t=task;
    audio_uart_ambiq_execute_drawing_4c7752(task);
    volatile uint8_t *unit=(void *)(uintptr_t)*(volatile uint32_t *)(t+76u);
    *(volatile uint32_t *)(t+80u)=3u;
    *(volatile uint32_t *)(unit+28u)=0u;
    audio_uart_lv_draw_dispatch_request_48462e();
}
/* Native4d475c..4d4768; waiter at word2 intentionally retained. */
uint32_t audio_uart_lv_thread_sync_delete_4d475c(void *cell) {
    volatile uint32_t *s=cell;
    s[1]=0u;
    s[0]=0u;
    return 1u;
}
/* Native4d46c2..4d46de; queue deletion precedes clearing initialized. */
uint32_t audio_uart_lv_mutex_delete_4d46c2(void *cell) {
    volatile uint32_t *s=cell;
    if(!s[0])return 0u;
    audio_queue_delete((void *)(uintptr_t)s[1]);
    s[0]=0u;
    return 1u;
}
