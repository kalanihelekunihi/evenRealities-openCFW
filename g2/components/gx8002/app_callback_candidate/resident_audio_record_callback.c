/* SPDX-License-Identifier: MIT
 * Image-A SRAM 0x10026214. Control flow and register arguments follow
 * direct native C-SKY disassembly. The VAD query is a separate XIP body;
 * its actual implementation remains a typed import.
 */
#include <stdint.h>

extern uint32_t gx8002_xip_audio_vad_query_10207404(void *pcm);
extern const uint32_t *gx8002_xip_tws_clock_10206e9c(void);
extern uint32_t gx8002_xip_tws_frames_per_channel_10206f74(void);
extern uint32_t gx8002_xip_tws_frame_count_10206f50(void);
extern uint32_t gx8002_xip_tws_context_count_10206f84(void);
extern uint32_t gx8002_xip_tws_context_gap_10206f80(void);

static int32_t native_signed_divide(uint32_t numerator, uint32_t denominator)
{
    int32_t quotient;
    __asm__ volatile("divs %0, %1, %2" : "=r"(quotient)
                     : "r"(numerator), "r"(denominator) : "cc");
    return quotient;
}

uint32_t gx8002_resident_audio_record_callback_26214(
    uint32_t flags, void *packet)
{
    if ((flags & 4u) == 0u) return 0u;
    uint8_t *const pcm = (uint8_t *)packet + 8u;
    volatile uint32_t *const state =
        (volatile uint32_t *)(uintptr_t)UINT32_C(0x2002ecb0);
    volatile uint32_t *const auxiliary =
        (volatile uint32_t *)(uintptr_t)UINT32_C(0x2002dfa0);
    uint32_t vad = gx8002_xip_audio_vad_query_10207404(pcm);
    volatile uint8_t *const flag_byte = (volatile uint8_t *)(void *)state + 0x10u;
    *flag_byte = (uint8_t)((*flag_byte & 0xf0u) | (vad & 15u));

    const uint32_t *header = gx8002_xip_tws_clock_10206e9c();
    uint32_t pcm_bytes = *(uint32_t *)(void *)pcm;
    uint32_t factor = header[0x24u / 4u] * header[0x6cu / 4u] * 2u;
    uint32_t index = pcm_bytes / factor;
    int32_t cycle = native_signed_divide(
        gx8002_xip_tws_frames_per_channel_10206f74(),
        gx8002_xip_tws_frame_count_10206f50());

    if ((*flag_byte & 0xf0u) != 0u) {
        state[1] = index + 2u;
        state[0] = index + 2u;
        state[2] = index;
        *flag_byte = 1u;
        state[3] = 1u;
    }

    for (;;) {
        uint32_t sequence = state[1];
        uint32_t remainder = sequence % (uint32_t)cycle;
        if (index == remainder) return 0u;

        if (gx8002_xip_tws_context_count_10206f84() < sequence) {
            uint32_t difference = sequence - state[0];
            uint32_t available = gx8002_xip_tws_context_count_10206f84();
            uint32_t gap = gx8002_xip_tws_context_gap_10206f80();
            if (difference >= available - gap) return 0u;
        }

        if (vad != 0u ||
            (uint32_t)native_signed_divide(
                gx8002_xip_tws_frames_per_channel_10206f74(),
                gx8002_xip_tws_frame_count_10206f50()) >= sequence) {
            state[3] = 1u;
            auxiliary[2] = 0u;
        } else {
            uint32_t counter = auxiliary[2] + 1u;
            auxiliary[2] = counter;
            state[3] = (int32_t)counter < 25 ? 1u : 0u;
        }

        uintptr_t callback = auxiliary[0];
        ((void (*)(uint32_t, void *))callback)(sequence, pcm);
        state[1] = state[1] + 1u;
    }
}
