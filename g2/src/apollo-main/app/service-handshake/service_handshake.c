/* Native UART sync handshake 0x584e94..0x584ee3. */
#include <stdint.h>
extern uint32_t audio_uart_handshake_send(uint32_t channel,const void *bytes,uint32_t size,uint32_t flags,uint32_t timeout); /* 0x465480 */
void audio_uart_service_prepare2(void)
{
    uint8_t packet[10]={0x55u,0x04u,0x12u,0x34u,0x56u,0x78u,0u,0u,0u,0u};
    (void)audio_uart_handshake_send(0xffu,packet,6u,0u,5u);
}
