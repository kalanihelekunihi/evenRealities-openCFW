/* Stock text-stream pause (0x552d40) and stop (0x552d10). */
#include <stdint.h>

extern int32_t audio_file_mutex_acquire(void *, uint32_t);
extern int32_t audio_file_mutex_release(void *);
extern int32_t audio_timer_stop(void *);

static uint32_t word(const void *object, uint32_t offset) {
    return *(const uint32_t *)((const uint8_t *)object + offset);
}

void audio_text_stream_pause_552d40(void *object) {
    if (!object)
        return;
    ((uint8_t *)object)[0x14] = 1u;
    void *mutex = (void *)(uintptr_t)word(object, 0x20u);
    if (!mutex)
        return;
    if (audio_file_mutex_acquire(mutex, UINT32_MAX) != 0)
        return;
    void *timer = (void *)(uintptr_t)word(object, 0x1cu);
    if (timer)
        (void)audio_timer_stop(timer);
    (void)audio_file_mutex_release(mutex);
}

void audio_text_stream_stop_552d10(void *object) {
    if (!object)
        return;
    audio_text_stream_pause_552d40(object);
    uint8_t *first = (uint8_t *)(uintptr_t)word(object, 0u);
    if (first)
        *first = 0u;
    uint8_t *second = (uint8_t *)(uintptr_t)word(object, 4u);
    if (second)
        *second = 0u;
    *(uint32_t *)((uint8_t *)object + 0x0cu) = 0u;
    *(uint32_t *)((uint8_t *)object + 0x10u) = 0u;
}
