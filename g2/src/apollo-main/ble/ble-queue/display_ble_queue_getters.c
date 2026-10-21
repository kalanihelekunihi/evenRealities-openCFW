/* Native CMSIS osMessageQueueGetCapacity/Count 0x449bbc/0x449bc8. */
#include <stdint.h>
extern uint32_t audio_irq_context(void); /* selected IRQ_Context 0x44900e */
extern uint32_t uxQueueMessagesWaiting(void *); /* selected FreeRTOS 0x441e66 */
extern uint32_t uxQueueMessagesWaitingFromISR(void *); /* selected 0x441e8a */
uint32_t audio_cmsis_queue_get_capacity(const void *queue) {
    if(queue==0) return 0u;
    const uint8_t *p=(const uint8_t *)queue;
    return (uint32_t)p[60]|((uint32_t)p[61]<<8)|((uint32_t)p[62]<<16)|((uint32_t)p[63]<<24);
}
uint32_t audio_cmsis_queue_get_count(void *queue) {
    if(queue==0) return 0u;
    if(audio_irq_context()==0u) return uxQueueMessagesWaiting(queue);
    return uxQueueMessagesWaitingFromISR(queue);
}
