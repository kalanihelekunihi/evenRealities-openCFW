/* Apollo QuickList storage mutex operations 0x4ffac8 and 0x4ffb26. */
#include <stdint.h>

extern void *audio_quicklist_storage_mutex; /* native RAM 0x200748f0 */
extern int32_t audio_file_mutex_acquire(void *, uint32_t); /* native 0x4497b6 */
extern int32_t audio_file_mutex_release(void *);          /* native 0x44981c */
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t, const char *, const char *, const char *,
                               uint32_t, const char *, ...);
extern uint32_t compressed_log_output(uint32_t, const char *, const char *, ...);

static const char module[] = "quicklist.page";
static const char path[] = "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\quicklist\\quicklist.c";
static const char function[] = "quicklist_lock_storage";
static const char message[] = "mutex is NULL";
static const char compact[] = "[quicklist.page]mutex is NULL";

uint32_t audio_quicklist_refresh_lock_4ffac8(void) {
    void *mutex = audio_quicklist_storage_mutex;
    if (mutex == 0) {
        if ((audio_log_flags() & 2u) != 0u)
            audio_log_extended(2u, module, path, function, 51u, message);
        if ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)
            (void)compressed_log_output(0x08000000u, compact, compact);
        return 0u;
    }
    return audio_file_mutex_acquire(mutex, UINT32_MAX) == 0 ? 1u : 0u;
}

void audio_quicklist_refresh_unlock_4ffb26(void) {
    void *mutex = audio_quicklist_storage_mutex;
    if (mutex != 0)
        (void)audio_file_mutex_release(mutex);
}
