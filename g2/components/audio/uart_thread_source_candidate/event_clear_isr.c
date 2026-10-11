/* Native xEventGroupClearBitsFromISR 0x47ed52, timer-pend bridge 0x47eb4a,
 * and callback wrapper 0x47ee28. */
#include <stdint.h>
extern void *g2_audio_timer_command_queue; /* pointer cell 0x20074ab0 */
extern int32_t opencfw_event_queue_send_isr(void *queue,const void *message,int32_t *wake,uint32_t position); /* selected 0x441952 */
extern uint32_t audio_uart_event_clear_task(void *event,uint32_t flags);
uint32_t audio_uart_event_clear_callback(void *event,uint32_t flags)
{
    return audio_uart_event_clear_task(event,flags);
}
uint32_t audio_uart_event_clear_isr(void *event,uint32_t flags)
{
    struct {int32_t message_type; void *callback; void *event; uint32_t flags;} message={
        -2,(void *)(uintptr_t)audio_uart_event_clear_callback,event,flags
    };
    return (uint32_t)opencfw_event_queue_send_isr(g2_audio_timer_command_queue,&message,0,0u);
}
