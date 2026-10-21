/* Native Cordio WsfTimerInit 0x52a474 and timer callback 0x52a468. */
#include <stdint.h>
extern void *audio_freertos_timer_create_dynamic(const char *,uint32_t,uint32_t,
                                                uintptr_t,void (*)(void *)); /* 0x47e6dc */
extern uint32_t audio_tick(void); /* selected xTaskGetTickCount 0x454efe */
extern void audio_wsf_task_set_ready(uint8_t,uint8_t); /* selected 0x52b95e */
extern uint32_t audio_wsf_interrupt_mask_set(void); /* native ulSetInterruptMask 0x5fa0a4 */
uint32_t audio_wsf_timer_list[2]; /* RAM 0x200741b0 */
void *audio_wsf_timer_handle; /* RAM 0x20074ef4 */
uint32_t audio_wsf_timer_last_tick; /* RAM 0x20074ef8 */
static const char timer_name[]="WSF Timer"; /* stock string 0x78c95c */
void audio_wsf_timer_callback(void *argument) {
    (void)argument;
    audio_wsf_task_set_ready(0u,2u);
}
void WsfTimerInit(void) {
    audio_wsf_timer_list[0]=0u;
    audio_wsf_timer_list[1]=0u;
    if(audio_wsf_timer_handle!=0) return;
    audio_wsf_timer_handle=audio_freertos_timer_create_dynamic(timer_name,10u,
                                                              0u,0u,audio_wsf_timer_callback);
    if(audio_wsf_timer_handle==0) {
        (void)audio_wsf_interrupt_mask_set();
        *(volatile uint32_t *)(uintptr_t)UINT32_MAX=0u;
        for(;;) {}
    }
    audio_wsf_timer_last_tick=audio_tick();
}
