/* Native Apollo Main ALS reset helper 0x4adcd8..0x4add02. */
#include <stdint.h>

uint32_t audio_als_manual_accumulator; /* stock RAM 0x200741cc */
uint32_t audio_als_manual_sample;      /* stock RAM 0x200741c8 */
uint8_t audio_als_manual_window[20];  /* stock RAM 0x20073c98..0x20073cab */
extern uint32_t audio_als_active_previous; /* stock RAM 0x200741e0 */
extern void audio_uart_buffer_zero(void *, uint32_t, uint32_t); /* 0x43c0e4 */

void audio_als_manual_recalculate_4adcd8(void)
{
    audio_als_manual_accumulator = 0u;
    audio_als_manual_sample = 0u;
    audio_als_active_previous = 0u;
    audio_uart_buffer_zero(audio_als_manual_window, 20u, 0u);
}
