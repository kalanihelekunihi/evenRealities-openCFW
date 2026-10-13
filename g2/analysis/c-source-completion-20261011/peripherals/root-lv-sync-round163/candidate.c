#include <stdint.h>
extern void audio_uart_lv_anim_mutex_ensure_4d47fa(uint32_t *);
extern void stock_enter_critical(void);
extern void stock_exit_critical(void);
extern uint32_t audio_notify_task(void *,uint32_t,uint32_t,uint32_t,uint32_t *);
/* Native4d4724..4d475c; consume waiter atomically, defer notification. */
uint32_t audio_uart_lv_thread_sync_signal_4d4724(void *cell) {
    volatile uint32_t *s=cell;
    audio_uart_lv_anim_mutex_ensure_4d47fa(cell);
    stock_enter_critical();
    uint32_t waiter=s[2];
    s[2]=0u;
    if(waiter==0u)s[1]=1u;
    stock_exit_critical();
    if(waiter!=0u)(void)audio_notify_task((void *)(uintptr_t)waiter,0u,0u,2u,0);
    return 1u;
}
