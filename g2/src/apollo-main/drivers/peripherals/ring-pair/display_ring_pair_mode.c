/* Native ring protocol four-byte pairing-mode packet 0x472546. */
#include <stdint.h>
extern void audio_uart_buffer_zero(void *,uint32_t,uint32_t); /* selected 0x43c0e4 */
extern uint32_t audio_uart_ring_ble_send_data_4c4b7e(const void *,uint32_t); /* selected */
uint32_t audio_uart_ring_pair_mode_472546(void) {
    uint8_t packet[254];
    audio_uart_buffer_zero(packet,sizeof(packet),0u);
    packet[0]=0u;
    packet[1]=0x35u;
    packet[2]=0x88u;
    packet[3]=0u;
    (void)audio_uart_ring_ble_send_data_4c4b7e(packet,4u);
    return 0u;
}
