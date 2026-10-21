/* Native 0x47dd62 and its 0x448f98 fallback. */
#include <stdint.h>
extern volatile uint32_t audio_uart_ring_persist_event_object; /* RAM 0x20074acc */
extern uint32_t audio_log_wake_allowed(void); /* selected 0x443484 */
extern uint32_t g2_audio_log_event_handle; /* RAM 0x20074570 */
extern uint32_t osEventFlagsSet(void *,uint32_t); /* selected 0x4495e4 */
extern uint32_t audio_uart_ring_persist_wait_event_47e7b0(uint32_t,uint32_t,uint32_t,void *,uint32_t);
void audio_uart_ring_persist_event_set_47dd62(void) {
    if(audio_log_wake_allowed()==0u) {
        if(g2_audio_log_event_handle!=0u)
            (void)osEventFlagsSet((void *)(uintptr_t)g2_audio_log_event_handle,8u);
    } else {
        (void)audio_uart_ring_persist_wait_event_47e7b0(audio_uart_ring_persist_event_object,
                                                        4u,2000u,(void *)0,0u);
    }
}
