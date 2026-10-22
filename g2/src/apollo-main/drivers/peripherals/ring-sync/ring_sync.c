/* Native UX_SendRingStatusToPeer 0x47ced6 and UX_SendRingQueryToPeer
 * 0x47cf28. ROM template bytes and live status byte remain typed
 * product-data contracts. */
#include <stdint.h>

extern const uint8_t audio_uart_ring_status_template[8]; /* PTR_DAT_0047d904 */
extern const uint8_t audio_uart_ring_query_template[8]; /* PTR_DAT_0047d908 */
extern const volatile uint8_t *const audio_uart_ring_status_word; /* DAT_0047d900 */
extern uint8_t audio_uart_device_role_get(void); /* 0x45a568 */
extern uint32_t audio_uart_request_send(uint32_t,const void *,uint32_t,uint32_t);

/* Stock 0x47CED6 (UX_SendRingStatusToPeer) */
void audio_uart_ring_sync_active(void) {
    uint8_t packet[8];
    for(uint32_t i=0;i<8u;i++) packet[i]=audio_uart_ring_status_template[i];
    packet[4]=audio_uart_device_role_get();
    packet[5]=(audio_uart_device_role_get()==1u) ? 2u : 1u;
    packet[6]=((*audio_uart_ring_status_word & 0x10u)==0u) ? 2u : 3u;
    (void)audio_uart_request_send(0x103u,packet,8u,0u);
}

/* Stock 0x47CF28 (UX_SendRingQueryToPeer) */
void audio_uart_ring_sync_idle(void) {
    uint8_t packet[8];
    for(uint32_t i=0;i<8u;i++) packet[i]=audio_uart_ring_query_template[i];
    packet[4]=audio_uart_device_role_get();
    packet[5]=(audio_uart_device_role_get()==1u) ? 2u : 1u;
    (void)audio_uart_request_send(0x103u,packet,8u,0u);
}
