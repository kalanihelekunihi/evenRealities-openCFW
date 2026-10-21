#include <stdint.h>

/* audio_flags_set and audio_thread_flags_set both identify native
 * osThreadFlagsSet at 0x449238, whose full C body is selected in
 * thread_flags_offline/flags.c and has a 1,440-case stock oracle. */
extern uint32_t audio_thread_flags_set(void *thread, uint32_t flags);
uint32_t audio_flags_set(void *thread, uint32_t flags) {
    return audio_thread_flags_set(thread, flags);
}
