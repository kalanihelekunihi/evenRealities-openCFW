/* Stock text-stream timer callback and UTF-8 advance, 0x553054. */
#include <stdint.h>

extern uint32_t audio_text_stream_buffer_create_553338(void *, void **, uint32_t *, uint32_t);
extern int32_t audio_file_mutex_acquire(void *, uint32_t);
extern int32_t audio_file_mutex_release(void *);
extern int32_t audio_timer_stop(void *);

static uint32_t word(const void *object, uint32_t offset) {
    return *(const uint32_t *)((const uint8_t *)object + offset);
}
static void stop_locked(void *object) {
    void *mutex = (void *)(uintptr_t)word(object, 0x20u);
    if (!mutex || audio_file_mutex_acquire(mutex, UINT32_MAX) != 0)
        return;
    void *timer = (void *)(uintptr_t)word(object, 0x1cu);
    if (timer)
        (void)audio_timer_stop(timer);
    (void)audio_file_mutex_release(mutex);
}

void audio_text_stream_tick_553054(void *object) {
    if (!object)
        return;
    if (((uint8_t *)object)[0x14]) {
        stop_locked(object);
        return;
    }
    uint32_t copied = word(object, 0x0cu);
    uint32_t total = word(object, 0x10u);
    if ((int32_t)copied >= (int32_t)total) {
        stop_locked(object);
        return;
    }
    if (!audio_text_stream_buffer_create_553338(
            object, (void **)object, (uint32_t *)((uint8_t *)object + 0x24u),
            total + 1u)) {
        stop_locked(object);
        return;
    }
    const uint8_t *input = (const uint8_t *)(uintptr_t)word(object, 4u);
    uint8_t lead = input[copied];
    uint32_t width = 1u;
    if (lead >= 0x80u) {
        if ((lead & 0xe0u) == 0xc0u)
            width = 2u;
        else if ((lead & 0xf0u) == 0xe0u)
            width = 3u;
        else if ((lead & 0xf8u) == 0xf0u)
            width = 4u;
    }
    uint8_t *output = (uint8_t *)(uintptr_t)word(object, 0u);
    for (uint32_t index = 0; index < width; ++index) {
        if (copied + index >= total)
            break;
        output[copied + index] = input[copied + index];
    }
    output[copied + width] = 0u;
    copied += width;
    *(uint32_t *)((uint8_t *)object + 0x0cu) = copied;
    uint32_t address = word(object, 0x18u);
    if (address)
        ((void (*)(void *))(uintptr_t)address)((void *)(uintptr_t)word(object, 0u));
    if ((int32_t)word(object, 0x0cu) >= (int32_t)word(object, 0x10u))
        stop_locked(object);
}
