#include <stdint.h>

/* Both call names refer to the native 0x474d16 body. The selected
 * audio_file_heap_free candidate owns its full mutex/TLSF effects. */
extern void audio_file_heap_free(void *buffer);
void codec_release(void *buffer) {
    audio_file_heap_free(buffer);
}
