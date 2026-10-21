/* Apollo main nanopb input context at 0x48f49c and reader at 0x48f3a4.
 * Stock initializer writes reader thumb pointer, input cursor, size, zero.
 */
#include "even_ai_decoder_context_48f49c.h"

_Static_assert(sizeof(struct even_ai_decode_context) == 16u,
               "stock decoder context size");

uint32_t audio_even_ai_decoder_read_48f3a4(struct even_ai_decode_context *context,
                                           void *destination, uint32_t count) {
    const uint8_t *source = context->cursor;
    context->cursor = (const uint8_t *)((uintptr_t)source + count);
    if (destination != 0) {
        uint8_t *out = destination;
        for (uint32_t i = 0; i < count; ++i)
            out[i] = source[i];
    }
    return 1u;
}

void audio_even_ai_decoder_context_init_48f49c(struct even_ai_decode_context *context,
                                                const void *data, uint32_t length) {
    context->read = audio_even_ai_decoder_read_48f3a4;
    context->cursor = data;
    context->length = length;
    context->reserved = 0u;
}
