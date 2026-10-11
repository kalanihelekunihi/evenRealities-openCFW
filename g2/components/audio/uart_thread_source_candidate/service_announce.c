/* Native UART service announcement 0x4ac828..0x4ac88f. */
#include <stdint.h>
extern uint32_t audio_uart_service_version(void); /* 0x45a568 */
extern uint32_t audio_uart_service_nonce(uint8_t out[4]); /* 0x4ac776 */
extern void audio_uart_checksum_copy(void *destination,const void *source,uint32_t size); /* 0x439be4 */
extern uint32_t audio_uart_handshake_send(uint32_t channel,const void *bytes,uint32_t size,uint32_t flags,uint32_t timeout); /* 0x465480 */
void audio_uart_service_prepare3(uint32_t command)
{
    uint8_t packet[8]={0};
    uint8_t nonce[4]={0};
    uint8_t version=(uint8_t)audio_uart_service_version();
    audio_uart_service_nonce(nonce);
    packet[0]=(uint8_t)command;
    packet[1]=4u;
    packet[2]=version;
    packet[3]=version==1u ? 2u : 1u;
    audio_uart_checksum_copy(packet+4u,nonce,4u);
    (void)audio_uart_handshake_send(0x81u,packet,8u,0u,5u);
}
