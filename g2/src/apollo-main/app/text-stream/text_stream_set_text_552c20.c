/* Stock text-stream set/append dispatcher at Apollo 0x552c20. */
#include <stdint.h>

extern uint32_t audio_text_stream_validate_5533cc(void *, const char *, uint32_t);
extern void audio_text_stream_pause_552d40(void *);
extern uint32_t strlen(const char *);
extern uint32_t audio_text_stream_buffer_create_553338(void *, void *, void *, uint32_t);
extern void audio_text_stream_restart_552db2(void *);
extern char *strcat(char *, const char *);
extern char *strcpy(char *, const char *);
extern void audio_text_stream_dispatch_552df0(void *, uint32_t, uint32_t);
extern uint32_t audio_text_stream_next_interval_5532f8(void *);

static uint32_t word(const void *object, uint32_t offset) {
    return *(const uint32_t *)((const uint8_t *)object + offset);
}

uint32_t audio_text_stream_set_text_552c20(void *object, const char *text,
                                            uint32_t interval, uint32_t mode,
                                            uint32_t notify) {
    if (!object || !text)
        return 0u;
    if ((int32_t)interval >= 1)
        *(uint32_t *)((uint8_t *)object + 8u) = interval;
    uint32_t narrow_mode = (uint8_t)mode;
    if (audio_text_stream_validate_5533cc(object, text, narrow_mode))
        return 0u;
    audio_text_stream_pause_552d40(object);
    uint32_t length = strlen(text);
    if (narrow_mode == 1u)
        length += word(object, 0x10u);
    if (!audio_text_stream_buffer_create_553338(
            object, (uint8_t *)object + 4u, (uint8_t *)object + 0x28u,
            length + 1u)) {
        audio_text_stream_restart_552db2(object);
        return 0u;
    }
    char *second = (char *)(uintptr_t)word(object, 4u);
    if (narrow_mode == 1u)
        (void)strcat(second, text);
    else
        (void)strcpy(second, text);
    *(uint32_t *)((uint8_t *)object + 0x10u) = length;
    audio_text_stream_dispatch_552df0(object, narrow_mode, (uint8_t)notify);
    return audio_text_stream_next_interval_5532f8(object);
}
