/* Stock text-stream finish/copy path, 0x552f14. */
#include <stddef.h>
#include <stdint.h>

extern size_t strlen(const char *);
extern char *strncpy(char *, const char *, size_t);
extern uint32_t audio_text_stream_buffer_create_553338(void *, void **, uint32_t *, uint32_t);
extern void audio_text_stream_schedule_552f6a(void *, uint32_t);

static uint32_t word(const void *object, uint32_t offset) {
    return *(const uint32_t *)((const uint8_t *)object + offset);
}
static void callback(void *object) {
    uint32_t address = word(object, 0x18u);
    if (address)
        ((void (*)(void *))(uintptr_t)address)((void *)(uintptr_t)word(object, 0u));
}

void audio_text_stream_finish_552f14(void *object, uint32_t ignored,
                                      uint32_t notify) {
    (void)ignored;
    if (!object)
        return;
    uint32_t length = (uint32_t)strlen((const char *)(uintptr_t)word(object, 0u));
    *(uint32_t *)((uint8_t *)object + 0x0cu) = length;
    if (!audio_text_stream_buffer_create_553338(
            object, (void **)object, (uint32_t *)((uint8_t *)object + 0x24u),
            length + 1u))
        return;
    char *output = (char *)(uintptr_t)word(object, 0u);
    strncpy(output, (const char *)(uintptr_t)word(object, 4u), length);
    output[length] = 0;
    callback(object);
    if ((int32_t)word(object, 0x0cu) < (int32_t)word(object, 0x10u))
        audio_text_stream_schedule_552f6a(object, (uint8_t)notify);
}
