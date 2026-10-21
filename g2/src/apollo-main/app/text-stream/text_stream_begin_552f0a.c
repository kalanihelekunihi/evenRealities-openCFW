/* Stock text-stream begin wrapper, 0x552f0a. */
#include <stdint.h>

extern void audio_text_stream_schedule_552f6a(void *, uint32_t);

void audio_text_stream_begin_552f0a(void *object, uint32_t notify) {
    audio_text_stream_schedule_552f6a(object, (uint8_t)notify);
}
