/* Native uart_sync_receive_callback 0x5417a4..0x5417c3. */
#include <stdint.h>
extern void *g2_uart_thread_transport; /* cell 0x20074b14 */
extern void *g2_uart_thread_event; /* cell 0x20074b10 */
extern uint32_t audio_uart_transport_write(void *,const void *,uint32_t,uint32_t *); /* 0x57e05e */
extern uint32_t g2_log_event_set_task(uint32_t,uint32_t); /* selected 0x4495e4 */
void audio_uart_sync_callback(const void *bytes,uint32_t length)
{
    uint32_t wake=0u;
    (void)audio_uart_transport_write(g2_uart_thread_transport,bytes,length,&wake);
    (void)g2_log_event_set_task((uint32_t)(uintptr_t)g2_uart_thread_event,1u);
}
