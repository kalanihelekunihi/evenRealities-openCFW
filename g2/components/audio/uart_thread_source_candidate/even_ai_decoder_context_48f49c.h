#ifndef OPENCFW_EVEN_AI_DECODER_CONTEXT_48F49C_H
#define OPENCFW_EVEN_AI_DECODER_CONTEXT_48F49C_H
#include <stdint.h>

struct even_ai_decode_context {
    uint32_t (*read)(struct even_ai_decode_context *, void *, uint32_t);
    const uint8_t *cursor;
    uint32_t length;
    uint32_t reserved;
};

uint32_t audio_even_ai_decoder_read_48f3a4(struct even_ai_decode_context *,
                                           void *, uint32_t);
void audio_even_ai_decoder_context_init_48f49c(struct even_ai_decode_context *,
                                                const void *, uint32_t);
#endif
