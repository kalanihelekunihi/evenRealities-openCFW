#include <stdint.h>
extern void *audio_uart_lv_draw_get_available_task_48463a(void *,void *,uint32_t);
extern void *audio_uart_lv_draw_layer_alloc_buf_484836(void *);
extern uint32_t audio_uart_lv_thread_sync_signal_4d4724(void *);
/* Native4c76a8..4c7700; pinned Ambiq dispatch policy. */
int32_t audio_uart_ambiq_dispatch_4c76a8(void *unit,void *layer) {
    volatile uint8_t *u=unit;
    if(*(volatile uint32_t *)(u+28u))return 0;
    volatile uint8_t *task=audio_uart_lv_draw_get_available_task_48463a(layer,0,9u);
    if(!task)return -1;
    if(!audio_uart_lv_draw_layer_alloc_buf_484836(layer))return -1;
    *(volatile uint32_t *)(task+80u)=2u;
    *(volatile uint32_t *)(task+76u)=(uint32_t)(uintptr_t)unit;
    *(volatile uint32_t *)(u+28u)=(uint32_t)(uintptr_t)task;
    if(u[56])audio_uart_lv_thread_sync_signal_4d4724((void *)(u+32u));
    return 1;
}
