/* Native UX_SendRingStatusToPeer 0x47ced6 and UX_SendRingQueryToPeer
 * 0x47cf28. ROM template bytes and live status word remain typed
 * product-data contracts. */
#include <stdint.h>

extern const uint8_t audio_uart_ring_status_template[5]; /* PTR_DAT_0047d904 */
extern const uint8_t audio_uart_ring_query_template[6]; /* PTR_DAT_0047d908 */
extern const volatile uint32_t *const audio_uart_ring_status_word; /* DAT_0047d900 */
extern uint8_t audio_uart_device_role_get(void); /* 0x45a568 */
extern uint32_t audio_uart_request_send(uint32_t,const void *,uint32_t,uint32_t);

void audio_uart_ring_sync_active(void) {
    uint8_t packet[8];
    for(uint32_t i=0;i<5u;i++) packet[i]=audio_uart_ring_status_template[i];
    packet[5]=audio_uart_device_role_get();
    packet[6]=(audio_uart_device_role_get()==1u) ? 2u : 1u;
    packet[7]=(((*audio_uart_ring_status_word & 0x1fu)>>4)==0u) ? 2u : 3u;
    (void)audio_uart_request_send(0x103u,packet,8u,0u);
}

void audio_uart_ring_sync_idle(void) {
    uint8_t packet[8];
    for(uint32_t i=0;i<6u;i++) packet[i]=audio_uart_ring_query_template[i];
    packet[6]=audio_uart_device_role_get();
    packet[7]=(audio_uart_device_role_get()==1u) ? 2u : 1u;
    (void)audio_uart_request_send(0x103u,packet,8u,0u);
}
