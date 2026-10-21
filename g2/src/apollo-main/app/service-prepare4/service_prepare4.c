/* Native RPC initial sync request 0x471528. The ten-byte local command is
 * zeroed, first byte2, second byte0; only two bytes are transmitted. */
#include <stdint.h>
extern uint32_t audio_uart_handshake_send(uint32_t channel,const void *data,
                                          uint32_t size,uint32_t flags,
                                          uint32_t timeout);
void audio_uart_service_prepare4(void) {
    uint8_t message[10]={0};
    message[0]=2u;
    (void)audio_uart_handshake_send(0x20u,message,2u,0u,5u);
}
