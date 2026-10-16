/* Apollo main 0x4e1fa6 and 0x4e1fbe: guard the shared EvenAI state.
 * Cell 0x20074580 is initialized separately by 0x4e1f7c.
 */
#include <stdint.h>

extern uint32_t audio_even_ai_mutex_20074580;
extern int32_t audio_file_mutex_acquire(void *, uint32_t); /* stock 0x4497b6 */
extern int32_t audio_file_mutex_release(void *);           /* stock 0x44981c */

void audio_even_ai_state_lock_4e1fa6(void) {
    uint32_t mutex = audio_even_ai_mutex_20074580;
    if (mutex != 0u)
        (void)audio_file_mutex_acquire((void *)(uintptr_t)mutex, UINT32_MAX);
}

void audio_even_ai_state_unlock_4e1fbe(void) {
    uint32_t mutex = audio_even_ai_mutex_20074580;
    if (mutex != 0u)
        (void)audio_file_mutex_release((void *)(uintptr_t)mutex);
}
