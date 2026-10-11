/* CMSIS osMessageQueueGet, native 0x449b3c, backed by selected FreeRTOS
 * xQueueReceive and xQueueReceiveFromISR C bodies. */
#include <stdint.h>
extern uint32_t audio_cmsis_irq_context(void); /* 0x44900e */
extern int32_t xQueueReceive(void *,void *,uint32_t); /* 0x441b0a */
extern int32_t xQueueReceiveFromISR(void *,void *,int32_t *); /* 0x441da6 */
int32_t audio_uart_queue_receive(void *queue,void *message,uint32_t priority,
                                  uint32_t timeout) {
    (void)priority; /* stock does not read the message priority output */
    if(audio_cmsis_irq_context()==0u) {
        if(queue==0 || message==0) return -4;
        if(xQueueReceive(queue,message,timeout)!=1)
            return timeout==0u ? -3 : -2;
        return 0;
    }
    if(queue==0 || message==0 || timeout!=0u) return -4;
    int32_t woken=0;
    if(xQueueReceiveFromISR(queue,message,&woken)!=1) return -3;
    if(woken!=0) *(volatile uint32_t *)(uintptr_t)0xe000ed04u=0x10000000u;
    return 0;
}
