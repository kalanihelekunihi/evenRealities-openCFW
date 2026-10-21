/* Stock 0x474910 is a stream sync facade despite the legacy caller name. */
#include <stdint.h>

extern int32_t audio_file_mutex_acquire(void *, uint32_t);
extern int32_t audio_file_mutex_release(void *);
extern int32_t audio_file_lfs_sync_4cfb08(void *, void *);
extern int32_t *audio_file_errno_location_439cc4(void);
extern void *audio_file_api_mutex;

int32_t audio_tracepoint_file_close_474910(void *stream) {
    uintptr_t value = (uintptr_t)stream;
    if (value == 0u || value == 0x200043f8u || value == 0x20004440u ||
        value == 0x200043b0u)
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
