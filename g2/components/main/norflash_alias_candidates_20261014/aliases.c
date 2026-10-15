/* Main caller names for the selected Apollo MX25U and osDelay providers.
 * Native addresses 0x46f65e, 0x46f674, and 0x449376 are shared by the
 * corresponding audio-side source bodies; these bridges add no policy. */
#include <stdint.h>

extern void audio_uart_ring_config_lock(void);
extern void audio_uart_ring_config_unlock(void);
extern void audio_os_delay(uint32_t ticks);

void g2_norflash_lock_46f65e(void)
{
    audio_uart_ring_config_lock();
}

void g2_norflash_unlock_46f674(void)
{
    audio_uart_ring_config_unlock();
}

void g2_norflash_scheduler_delay_449376(uint32_t ticks)
{
    audio_os_delay(ticks);
}
