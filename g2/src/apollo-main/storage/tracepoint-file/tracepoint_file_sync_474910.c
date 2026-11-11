/* Stock 0x474910 is a stream sync facade despite the legacy caller name. */
#include <stdint.h>
extern unsigned char g2ref_g2_iar_stdout_200043f8[] __asm__("g2_iar_stdout_200043f8"); /* Fix 45: stock owner (owner.py) */

extern int32_t audio_file_mutex_acquire(void *, uint32_t);
extern int32_t audio_file_mutex_release(void *);
extern int32_t audio_file_lfs_sync_4cfb08(void *, void *);
extern int32_t *audio_file_errno_location_439cc4(void);
extern void *audio_file_api_mutex;

int32_t audio_tracepoint_file_close_474910(void *stream) {
    uintptr_t value = (uintptr_t)stream;
    if (value == 0u || value == ((uint32_t)(uintptr_t)g2ref_g2_iar_stdout_200043f8+0x0u) || value == ((uint32_t)(uintptr_t)g2ref_g2_iar_stdout_200043f8+0x48u))
        /* Fix 46: stock also skipped 0x200043b0 (IAR __iar_Stdin FILE, 0x48 below stdout).
         * This build has no stdin FILE (owner.py: NONE), so a raw compare could only
         * false-match an unrelated object; dropped. */
        return 0;
    if (audio_file_mutex_acquire(audio_file_api_mutex, 1000u) != 0) {
        *audio_file_errno_location_439cc4() = 16;
        return -1;
    }
    void *filesystem = (void *)(uintptr_t)*(uint32_t *)stream;
    int32_t result = audio_file_lfs_sync_4cfb08(filesystem,
                                                  (uint8_t *)stream + 4u);
    (void)audio_file_mutex_release(audio_file_api_mutex);
    if (result < 0) {
        *audio_file_errno_location_439cc4() = 5;
        return -1;
    }
    return 0;
}
