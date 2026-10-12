/* Native 0x448e34 signals bit 4 on event handle RAM 0x20074570. */
#include <stdint.h>
extern uint32_t g2_audio_log_event_handle; /* selected live pointer cell */
extern uint32_t osEventFlagsSet(void *,uint32_t); /* selected 0x4495e4 */
void audio_uart_hand_mismatch_448e34(void) {
    if(g2_audio_log_event_handle!=0u)
        (void)osEventFlagsSet((void *)(uintptr_t)g2_audio_log_event_handle,4u);
}
