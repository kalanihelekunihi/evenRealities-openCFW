/* Stock ensure_text_capacity at 0x553338. */
#include <stdint.h>

extern void *audio_file_heap_realloc(void *, uint32_t);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t, const char *, const char *, const char *,
                               uint32_t, const char *, ...);
extern uint32_t compressed_log_output(uint32_t, const char *, const char *, ...);

static const char module[] = "text_stream_service";
static const char path[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\EvenAI\\text_stream_service.c";
static const char function[] = "ensure_text_capacity";
static const char message[] = "newText realloc failed";
static const char short_message[] =
    "[text_stream_service]newText realloc failed";

uint32_t audio_text_stream_buffer_create_553338(void *owner, void **buffer,
                                                 uint32_t *capacity,
                                                 uint32_t required) {
    if (!owner)
        return 0u;
    if (*capacity >= required)
        return 1u;
    uint32_t next = *capacity << 1;
    if (next < required)
        next = required;
    void *new_buffer = audio_file_heap_realloc(*buffer, next);
    if (!new_buffer) {
        if (audio_log_flags() & 2u)
            audio_log_extended(1u, module, path, function, 0x2a6u, message);
        uint32_t flags = audio_log_flags();
        if ((flags & 1u) || (!(flags & 1u) && (audio_log_flags() & 4u)))
            (void)compressed_log_output(0x04000000u, short_message,
                                        short_message);
        return 0u;
    }
    *buffer = new_buffer;
    *capacity = next;
    return 1u;
}
