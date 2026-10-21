/* Native 0x47dd92; literals resolve RAM words 0x20074acc/0x20074ad0. */
#include <stdint.h>
extern volatile uint32_t audio_uart_ring_persist_event_object; /* 0x20074acc */
extern volatile uint32_t audio_uart_ring_persist_event_pending; /* 0x20074ad0 */
extern void audio_uart_ring_persist_event_set_47dd62(void);
void audio_uart_ring_persist_notify_47dd92(void) {
    if(audio_uart_ring_persist_event_object!=0u) {
        audio_uart_ring_persist_event_pending=0u;
        audio_uart_ring_persist_event_set_47dd62();
    }
}
