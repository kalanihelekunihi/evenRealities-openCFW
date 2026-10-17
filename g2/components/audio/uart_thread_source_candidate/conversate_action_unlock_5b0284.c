/* Native conversate_action_unlock 0x5b0284..0x5b02e3. */
#include <stdint.h>
extern uint32_t audio_conversate_action_mutex_20074398;
extern int32_t audio_file_mutex_release(void *); /* native 0x44981c */
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint32_t, const char *, const char *, const char *,
                               uint32_t, const char *, ...);
extern void audio_log_simple(uint32_t, const char *, const char *, ...);

static const char module[] = "conversate";
static const char path[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\conversate\\conversate.c";
static const char function[] = "conversate_action_unlock";
static const char failed[] =
    "Failed to release conversate action mutex, status: %d";
static const char short_failed[] =
    "[conversate]Failed to release conversate action mutex, status: %d";

void audio_conversate_leave_5b0284(void) {
    if (audio_conversate_action_mutex_20074398 == 0u) return;
    int32_t status = audio_file_mutex_release(
        (void *)(uintptr_t)audio_conversate_action_mutex_20074398);
    if (status == 0) return;
    if (audio_log_flags() & 2u)
        audio_log_extended(1u, module, path, function, 109u, failed, status);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        audio_log_simple(0x04400000u, short_failed, short_failed, status);
}
