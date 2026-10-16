/* Stock getRunningAppID entry at 0x443504. The full state and logging
 * implementation is owned by terminal_running_app_ids.c. */
#include <stdint.h>

extern uint32_t audio_get_running_app_ids(uint32_t *, uint32_t *);

uint32_t audio_system_close_active_app_get_443504(uint32_t *background,
                                                   uint32_t *foreground)
{
    return audio_get_running_app_ids(background, foreground);
}
