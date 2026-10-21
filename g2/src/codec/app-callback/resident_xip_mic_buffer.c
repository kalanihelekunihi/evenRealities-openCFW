/* SPDX-License-Identifier: MIT
 * Native image-A XIP 0x10208e80..0x10208ef8. Direct DIVU instructions
 * make context words +0x08 and the derived frame span nonzero native
 * preconditions; no fallback divisor or clamp is introduced.
 */
#include <stdint.h>

extern uint32_t gx8002_xip_tws_publish_10206c24(const char *, ...);

uint32_t gx8002_xip_mic_buffer_10208e80(
    const uint8_t *context, uint32_t channel, uint32_t cursor,
    uint32_t *address, uint32_t *span_out)
{
    const char *error =
        "ERR: invalid param for gx_audio_get_mic_buffer\n";
    if (context != (void *)0 && address != (void *)0 &&
        span_out != (void *)0) {
        const uint32_t channels =
            *(const uint32_t *)(const void *)(context + 0x08u);
        if (channel < channels) {
            uint32_t frame_span =
                *(const uint32_t *)(const void *)(context + 0x1cu) *
                *(const uint32_t *)(const void *)(context + 0x24u);
            frame_span *= 2u;
            frame_span *= *(const uint32_t *)(const void *)(context + 0x20u);
            frame_span /= 1000u;
            uint32_t channel_bytes =
                *(const uint32_t *)(const void *)(context + 0x54u) / channels;
            uint32_t frame_count = channel_bytes / frame_span;
            error = "ERR: buf_len_per_ctx too large for mic buffer\n";
            if (frame_count != 0u) {
                uint32_t wrapped = cursor - (cursor / frame_count) * frame_count;
                *address = channel_bytes * channel + wrapped * frame_span +
                    *(const uint32_t *)(const void *)(context + 0x50u);
                *span_out = frame_span;
                return 0u;
            }
        }
    }
    (void)gx8002_xip_tws_publish_10206c24(error);
    return UINT32_MAX;
}
