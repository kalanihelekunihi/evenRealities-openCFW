/* Stock text-stream restart eligibility and timer start, 0x552db2. */
#include <stdint.h>

extern int32_t audio_file_mutex_acquire(void *, uint32_t);
extern int32_t audio_file_mutex_release(void *);
extern int32_t audio_timer_start(void *, uint32_t);

static uint32_t word(const void *object, uint32_t offset) {
    return *(const uint32_t *)((const uint8_t *)object + offset);
}

void audio_text_stream_restart_552db2(void *object) {
    if (!object)
        return;
    if ((int32_t)word(object, 0x0cu) >= (int32_t)word(object, 0x10u))
        return;
    ((uint8_t *)object)[0x14] = 0u;
    void *mutex = (void *)(uintptr_t)word(object, 0x20u);
    if (!mutex || audio_file_mutex_acquire(mutex, UINT32_MAX) != 0)
        return;
    void *timer = (void *)(uintptr_t)word(object, 0x1cu);
    if (timer)
        (void)audio_timer_start(timer, word(object, 8u));
    (void)audio_file_mutex_release(mutex);
}
