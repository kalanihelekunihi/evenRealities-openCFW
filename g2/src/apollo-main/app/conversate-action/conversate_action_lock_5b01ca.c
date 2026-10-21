/* Native conversate_action_lock 0x5b01ca..0x5b0283. */
#include <stdint.h>
extern uint32_t audio_conversate_action_mutex_20074398;
extern uint32_t audio_conversate_mutex_init_5b0120(void);
extern int32_t audio_file_mutex_acquire(void *, uint32_t); /* native 0x4497b6 */
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint32_t, const char *, const char *, const char *,
                               uint32_t, const char *, ...);
extern void audio_log_simple(uint32_t, const char *, const char *, ...);

static const char module[] = "conversate";
static const char path[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\conversate\\conversate.c";
static const char function[] = "conversate_action_lock";
static const char init_failed[] = "Failed to initialize conversate action mutex";
static const char init_short[] =
    "[conversate]Failed to initialize conversate action mutex";
static const char acquire_failed[] =
    "Failed to acquire conversate action mutex, status: %d";
static const char acquire_short[] =
    "[conversate]Failed to acquire conversate action mutex, status: %d";

uint32_t audio_conversate_enter_5b01ca(void) {
    if (audio_conversate_action_mutex_20074398 == 0u &&
        audio_conversate_mutex_init_5b0120() != 0u) {
        if (audio_log_flags() & 2u)
            audio_log_extended(1u, module, path, function, 88u, init_failed);
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            audio_log_simple(0x04000000u, init_short, init_short);
        return 0u;
    }
    int32_t result = audio_file_mutex_acquire(
        (void *)(uintptr_t)audio_conversate_action_mutex_20074398, UINT32_MAX);
    if (result == 0) return 1u;
    if (audio_log_flags() & 2u)
        audio_log_extended(1u, module, path, function, 95u,
                           acquire_failed, result);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        audio_log_simple(0x04400000u, acquire_short, acquire_short, result);
    return 0u;
}
