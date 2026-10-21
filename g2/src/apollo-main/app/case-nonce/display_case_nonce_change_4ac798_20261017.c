/* Stock Main BoxDetect four-byte nonce state update 0x4ac798. */
#include <stdint.h>
extern uint8_t audio_uart_device_role_get(void); /* 0x45a568 */
extern void audio_uart_buffer_zero(void *,uint32_t,uint32_t); /* 0x43c0e4 */
extern uint32_t audio_uart_service_nonce(uint8_t out[4]); /* 0x4ac776 */
extern uint8_t audio_uart_case_nonce_state_200036d8[4];
extern void audio_uart_service_prepare3(uint32_t); /* 0x4ac828 */

void audio_uart_case_force_out_apply_4ac798(void)
{
    (void)audio_uart_device_role_get();
    uint8_t current[4];
    audio_uart_buffer_zero(current,4u,0u);
    (void)audio_uart_service_nonce(current);
    uint8_t changed=0u;
    for (uint32_t i=0u;i<4u;i++) {
        if (audio_uart_case_nonce_state_200036d8[i]!=current[i]) {
            audio_uart_case_nonce_state_200036d8[i]=current[i];
            changed=1u;
        }
    }
    if (changed!=0u)
        audio_uart_service_prepare3(3u);
}
