/* Gesture/touch input local-source selector, firmware 2.2.6.10.
 * Stock range 0x4c5874..0x4c5885 (no literal pool). */
#include <stdint.h>

extern uint8_t audio_uart_device_role_get(void); /* 0x45a568, 1 = master */

/* Stock 0x004C5874 (input_local_source_4c5874) */
uint32_t input_local_source_4c5874(void)
{
    return (audio_uart_device_role_get() == 1u) ? 1u : 0u;
}
