/* Native FreeRTOS vTaskDelay at 0x454b4c. The CMSIS osDelay provider
 * contains this logic privately, but this direct FreeRTOS entry has no
 * CMSIS interrupt-context return contract. */
#include <stdint.h>

extern void audio_delay_scheduler_assert(void);     /* 0x5fa0a4 */
extern void audio_suspend(void);                    /* 0x454d7c */
extern void audio_add_current_to_delayed(uint32_t,uint32_t); /* 0x455fa8 */
extern int32_t audio_resume(void);                  /* 0x454dcc */
extern void audio_yield(void);                      /* 0x4420bc */

void audio_uart_task_delay(uint32_t ticks) {
    int32_t yielded=0;
    if(ticks!=0u) {
        if(*(volatile uint32_t *)0x20074a58u!=0u)
            audio_delay_scheduler_assert();
        audio_suspend();
        audio_add_current_to_delayed(ticks,0u);
        yielded=audio_resume();
    }
    if(yielded==0) audio_yield();
}
