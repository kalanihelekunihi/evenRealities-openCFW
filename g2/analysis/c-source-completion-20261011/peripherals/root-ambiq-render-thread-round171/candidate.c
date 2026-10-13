#include <stdint.h>
extern void audio_uart_lv_anim_init_4d46de(void *);
extern uint32_t audio_uart_lv_thread_sync_wait_4d46e8(void *);
extern void audio_uart_ambiq_execute_unit_4c752e(void *);
extern uint32_t audio_uart_lv_thread_sync_delete_4d475c(void *);
extern uint32_t audio_uart_lv_mutex_delete_4d46c2(void *);
/* Native4c7700..4c7752. All shared field loads retained. */
void audio_uart_ambiq_render_thread_4c7700(void *unit) {
    volatile uint8_t *u=unit;
    audio_uart_lv_anim_init_4d46de((void *)(u+32u));
    u[56]=1u;
    for(;;) {
        while(!*(volatile uint32_t *)(u+28u)&&!u[57])
            audio_uart_lv_thread_sync_wait_4d46e8((void *)(u+32u));
        if(u[57])break;
        audio_uart_ambiq_execute_unit_4c752e((void *)(uintptr_t)*(volatile uint32_t *)(u+28u));
    }
    u[56]=0u;
    audio_uart_lv_thread_sync_delete_4d475c((void *)(u+32u));
    audio_uart_lv_mutex_delete_4d46c2((void *)(u+132u));
}
