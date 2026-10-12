/* Native 0x46f32c, shared by display-thread and BLE slave-sync callers. */
#include <stdint.h>
extern uint8_t *audio_ble_profile_connection_context; /* RAM pointer cell0x2007432c */
extern void audio_ble_slave_security_state(uint8_t); /* selected native0x4b82e8 */

void audio_uart_display_connected(void)
{
    audio_ble_slave_security_state(audio_ble_profile_connection_context[0x54u]!=0u);
}
