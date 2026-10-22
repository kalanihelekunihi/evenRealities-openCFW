#include <stdint.h>

/* Original 0x53c31c reads the codec watchdog timer cell, returns for NULL,
 * and otherwise rereads the handle and invokes CMSIS osTimerStop. The
 * archive's audio_timer_stop import is bound to that same original entry. */
extern uint32_t audio_timer_stop(uint32_t handle);

/* Stock 0x53C31C (aud_codec_audio_check_timer_stop) */
void audio_watchdog_stop(void) {
    volatile const uint32_t *const timer =
        (volatile const uint32_t *)(uintptr_t)0x20074a98u;
    if (*timer != 0u) {
        (void)audio_timer_stop(*timer);
    }
}
