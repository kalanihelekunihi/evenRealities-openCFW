#include <stdint.h>
extern void audio_uart_lv_anim_mutex_ensure_4d47fa(uint32_t *);
extern void *receiver_current_task(void);
extern void stock_enter_critical(void);
extern void stock_exit_critical(void);
extern uint32_t audio_uart_notify_take_455afc(uint32_t,int32_t,uint32_t);
/* Native4d46e8..4d4724: consume pending signal, otherwise register and wait. */
uint32_t audio_uart_lv_thread_sync_wait_4d46e8(void *cell) {
    volatile uint32_t *s=cell;
    audio_uart_lv_anim_mutex_ensure_4d47fa(cell);
    uint32_t current=(uint32_t)(uintptr_t)receiver_current_task();
    stock_enter_critical();
    uint32_t pending=s[1];
    s[1]=0u;
    if(!pending)s[2]=current;
    stock_exit_critical();
    if(!pending)audio_uart_notify_take_455afc(0u,1,UINT32_MAX);
    return 1u;
}
