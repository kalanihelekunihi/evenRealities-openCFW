/* Native 0x47e7b0: three-word event packet and FreeRTOS queue routing.
 * The fifth argument is read from caller stack at entry+0x20; native
 * 0x47dd62 explicitly writes zero to that stack slot. */
#include <stdint.h>
extern volatile uintptr_t audio_uart_ring_persist_queue_handle_20074ab0;
extern uint32_t audio_scheduler_state(void); /* selected 0x4558a4 */
extern uint32_t audio_wsf_interrupt_mask_set(void); /* selected 0x5fa0a4 */
extern int32_t xQueueGenericSend(void *,const void *,uint32_t,int32_t);
extern int32_t xQueueGenericSendFromISR(void *,const void *,int32_t *,int32_t);
uint32_t audio_uart_ring_persist_wait_event_47e7b0(uint32_t event,uint32_t priority,
                                                     uint32_t value,void *isr_woken,
                                                     uint32_t wait_ticks) {
    if(event==0u) {
        (void)audio_wsf_interrupt_mask_set();
        uint32_t zero=0u,invalid=UINT32_MAX;
        __asm__ volatile("str %0, [%1]\n1: b 1b" :: "r"(zero),"r"(invalid) : "memory");
        __builtin_unreachable();
    }
    void *queue=(void *)audio_uart_ring_persist_queue_handle_20074ab0;
    if(queue!=0) {
        uint32_t packet[3]={priority,value,event};
        if((int32_t)priority<6) {
            uint32_t delay=audio_scheduler_state()==2u ? wait_ticks : 0u;
            return (uint32_t)xQueueGenericSend(queue,packet,delay,0);
        } else {
            return (uint32_t)xQueueGenericSendFromISR(queue,packet,(int32_t *)isr_woken,0);
        }
    }
    return 0u;
}
