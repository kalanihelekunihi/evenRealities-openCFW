/* Stock text-stream dispatch and completion decision, 0x552df0. */
#include <stddef.h>
#include <stdint.h>

extern size_t strlen(const char *);
extern char *strcpy(char *, const char *);
extern void audio_text_stream_pause_552d40(void *);
extern uint32_t audio_text_stream_buffer_create_553338(void *, void **, uint32_t *, uint32_t);
extern uint32_t audio_text_stream_prefix_match_552ecc(const char *, const char *);
extern void audio_text_stream_begin_552f0a(void *, uint32_t);
extern void audio_text_stream_finish_552f14(void *, uint32_t, uint32_t);

static uint32_t get_word(const void *object, uint32_t offset) {
    return *(const uint32_t *)((const uint8_t *)object + offset);
}
static void set_word(void *object, uint32_t offset, uint32_t value) {
    *(uint32_t *)((uint8_t *)object + offset) = value;
}
static void callback(void *object) {
    uint32_t address = get_word(object, 0x18u);
    if (address)
        ((void (*)(void *))(uintptr_t)address)((void *)(uintptr_t)get_word(object, 0u));
}

void audio_text_stream_dispatch_552df0(void *object, uint32_t mode, uint32_t notify) {
    if (!object)
        return;
    audio_text_stream_pause_552d40(object);
    uint32_t input = get_word(object, 4u);
    uint32_t total = get_word(object, 0x10u);
    if (!input || !total) {
        uint32_t output = get_word(object, 0u);
        if (output)
            *(uint8_t *)(uintptr_t)output = 0u;
        set_word(object, 0x0cu, 0u);
        callback(object);
        return;
    }
    switch ((uint8_t)mode) {
    case 1u:
        ((uint8_t *)object)[0x2c] = 1u;
        audio_text_stream_begin_552f0a(object, (uint8_t)notify);
        return;
    case 2u:
        ((uint8_t *)object)[0x2c] = 0u;
        audio_text_stream_finish_552f14(object, 0u, (uint8_t)notify);
        return;
    case 0u:
        break;
    default:
        return;
    }
    uint32_t output = get_word(object, 0u);
    uint32_t length = (uint32_t)strlen((const char *)(uintptr_t)output);
    if (length >= total) {
        if (!audio_text_stream_buffer_create_553338(object, (void **)object,
                                                      (uint32_t *)((uint8_t *)object + 0x24u),
                                                      total + 1u))
            return;
        strcpy((char *)(uintptr_t)get_word(object, 0u),
               (const char *)(uintptr_t)get_word(object, 4u));
        set_word(object, 0x0cu, total);
        callback(object);
        return;
    }
    uint32_t prefix = audio_text_stream_prefix_match_552ecc(
        (const char *)(uintptr_t)output, (const char *)(uintptr_t)input);
    if (prefix == length && length < total) {
        ((uint8_t *)object)[0x2c] = 1u;
        audio_text_stream_begin_552f0a(object, (uint8_t)notify);
    } else {
        ((uint8_t *)object)[0x2c] = 0u;
        audio_text_stream_finish_552f14(object, 0u, (uint8_t)notify);
    }
}
