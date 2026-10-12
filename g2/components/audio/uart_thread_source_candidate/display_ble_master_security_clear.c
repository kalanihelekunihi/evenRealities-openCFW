/* AppMasterSecClearAddr 0x4d8ff6. Literal at 0x4d9128 resolves RAM 0x200003d8. */
#include <stdint.h>
extern volatile uint8_t audio_ble_master_security_address[7]; /* RAM 0x200003d8 */
extern void audio_uart_buffer_zero(void *,uint32_t,uint32_t); /* selected 0x43c0e4 */
void audio_ble_master_security_clear_address(void) {
    audio_uart_buffer_zero((void *)audio_ble_master_security_address,7u,0u);
    audio_ble_master_security_address[6]=0xffu;
}
