/* Native EFS startup request 0x458c48: one initialized stack byte sent via
 * the authenticated thread message ABI 0x48f12c. */
#include <stdint.h>
extern uint32_t audio_uart_thread_msg_rx_from_ble_48f12c(uint32_t,uint8_t *,uint32_t);

void audio_uart_efs_service_init_458c48(void)
{
    uint8_t argument=0u;
    (void)audio_uart_thread_msg_rx_from_ble_48f12c(0x400u,&argument,1u);
}
