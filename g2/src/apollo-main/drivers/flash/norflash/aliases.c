/* Main caller names for the selected Apollo MX25U providers.
 * Native addresses 0x46f65e and 0x46f674 are shared by the corresponding
 * audio-side source bodies; these bridges add no policy. The osDelay
 * (0x449376) caller name g2_norflash_scheduler_delay_449376 is a payload
 * defsym to upstream CMSIS-FreeRTOS osDelay (U4-freertos). */
#include <stdint.h>

extern void audio_uart_ring_config_lock(void);
extern void audio_uart_ring_config_unlock(void);

void g2_norflash_lock_46f65e(void)
{
    audio_uart_ring_config_lock();
}

void g2_norflash_unlock_46f674(void)
{
    audio_uart_ring_config_unlock();
}
