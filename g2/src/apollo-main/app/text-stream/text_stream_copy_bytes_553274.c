/* Stock text-stream copy/notification body at Apollo 0x553274. */
#include <stdint.h>

extern int32_t audio_file_mutex_acquire(void *, uint32_t);
extern int32_t audio_file_mutex_release(void *);
extern uint32_t audio_text_stream_buffer_create_553338(void *, void *, uint32_t *, uint32_t);
extern void *audio_queue_copy_bytes(void *, const void *, uint32_t);

static uint32_t get_word(const void *object, uint32_t offset) {
    return *(const uint32_t *)((const uint8_t *)object + offset);
}

void audio_text_stream_copy_bytes_553274(void *object, uint32_t requested,
                                          uint32_t notify) {
    if (!object)
        return;
    uint32_t mutex = get_word(object, 0x20u);
    if (mutex && audio_file_mutex_acquire((void *)(uintptr_t)mutex, UINT32_MAX) == 0) {
        uint32_t available = get_word(object, 0x10u);
        if ((uint16_t)available < (uint16_t)requested)
            requested = available;
        uint32_t count = (uint16_t)requested;
        if (!audio_text_stream_buffer_create_553338(
                object, object, (uint32_t *)((uint8_t *)object + 0x24u), count + 1u)) {
            (void)audio_file_mutex_release((void *)(uintptr_t)mutex);
            return;
        }
        uint8_t *first = (uint8_t *)(uintptr_t)get_word(object, 0u);
        const uint8_t *second = (const uint8_t *)(uintptr_t)get_word(object, 4u);
        (void)audio_queue_copy_bytes(first, second, count);
        first[count] = 0u;
        *(uint32_t *)((uint8_t *)object + 0x0cu) = count;
        (void)audio_file_mutex_release((void *)(uintptr_t)mutex);
    }
    if ((uint8_t)notify) {
        uint32_t callback = get_word(object, 0x18u);
        if (callback)
            ((void (*)(void *))(uintptr_t)callback)(
                (void *)(uintptr_t)get_word(object, 0u));
    }
}
