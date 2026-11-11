#include <stdint.h>
/* Stock-RAM literals rewritten to named objects (sim-test wave 2026-10-26,
 * .waves/sim-fix/apply.py): g2ref_X is the linker symbol X. */
#include <stdint.h>
extern unsigned char g2ref_g2_audio_codec_check_timer[] __asm__("g2_audio_codec_check_timer");

/* Original 0x53c31c reads the codec watchdog timer cell, returns for NULL,
 * and otherwise rereads the handle and invokes CMSIS osTimerStop. The
 * archive's audio_timer_stop import is bound to that same original entry. */
extern uint32_t audio_timer_stop(uint32_t handle);

/* Stock 0x53C31C (aud_codec_audio_check_timer_stop) */
void audio_watchdog_stop(void) {
    volatile const uint32_t *const timer =
        (volatile const uint32_t *)(uintptr_t)((uint32_t)(uintptr_t)g2ref_g2_audio_codec_check_timer);
    if (*timer != 0u) {
        (void)audio_timer_stop(*timer);
    }
}
