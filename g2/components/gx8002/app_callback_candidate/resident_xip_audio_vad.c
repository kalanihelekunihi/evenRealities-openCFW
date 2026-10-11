/* SPDX-License-Identifier: MIT
 * Native image-A XIP 0x10207404 and ten direct audio-register children.
 * The retained decompiler missed the disjoint noise windows; the direct
 * C-SKY branches at 0x10207434/0x102074fc define them below.
 */
#include <stdint.h>

/* Existing 0x10206c24 import is stock gx8002_printf. */
extern void gx8002_xip_tws_publish_10206c24(const char *format, ...);
static volatile uint32_t *const audio =
    (volatile uint32_t *)(uintptr_t)UINT32_C(0xa0a00000);

static void field(uint32_t offset, uint32_t mask, uint32_t value)
{
    volatile uint32_t *reg = &audio[offset / 4u];
    *reg = (*reg & ~mask) | (value & mask);
}

uint32_t gx8002_xip_audio_vad_weight_102045f4(uint32_t word)
{
    field(0x158u, UINT32_C(0x00000f00), (word & 15u) << 8u);
    field(0x158u, UINT32_C(0x0000f000), ((word >> 8u) & 15u) << 12u);
    field(0x158u, UINT32_C(0x000f0000), ((word >> 16u) & 15u) << 16u);
    return 0u;
}

uint32_t gx8002_xip_audio_vad_curve1_10204630(uint32_t first, uint32_t second)
{
    if (first >= 0xc01u || second >= 0x4601u) return UINT32_MAX;
    field(0x184u, 0xffffu, first);
    field(0x184u, 0xffff0000u, second << 16u);
    return 0u;
}

uint32_t gx8002_xip_audio_vad_curve2_10204664(uint32_t first, uint32_t second)
{
    if (first >= 0xc01u || second >= 0x1e01u) return UINT32_MAX;
    field(0x188u, 0xffffu, first);
    field(0x188u, 0xffff0000u, second << 16u);
    return 0u;
}

uint32_t gx8002_xip_audio_vad_curve3_10204698(uint16_t first, int16_t second)
{
    if (first >= 0x1001u || (uint16_t)(second + 0x1400u) >= 0x2801u)
        return UINT32_MAX;
    field(0x18cu, 0xffffu, first);
    field(0x18cu, 0xffff0000u, (uint32_t)(uint16_t)second << 16u);
    return 0u;
}

uint32_t gx8002_xip_audio_vad_curve4_102046d8(uint32_t first, uint32_t second)
{
    if (first >= 0x1401u || second >= 0x1401u) return UINT32_MAX;
    field(0x190u, 0xffffu, first);
    field(0x190u, 0xffff0000u, second << 16u);
    return 0u;
}

uint32_t gx8002_xip_audio_vad_curve5_1020470c(uint32_t value)
{
    if (value >= 0x2001u) return UINT32_MAX;
    field(0x194u, 0xffffu, value);
    return 0u;
}

uint32_t gx8002_xip_audio_vad_chipping_1020472c(uint32_t first,
                                                   uint32_t second)
{
    field(0x198u, 0xffffu, first);
    field(0x198u, 0xffff0000u, first);
    field(0x19cu, 0xffffu, second);
    field(0x19cu, 0xffff0000u, second);
    return 0u;
}

struct vad_state {
    uint32_t masks[3];
    uint16_t position;
    uint16_t padding;
};

uint32_t gx8002_xip_audio_vad_state_1020477c(struct vad_state *state)
{
    if (state == 0) return UINT32_MAX;
    state->masks[2] = audio[0x174u / 4u];
    state->masks[1] = audio[0x178u / 4u];
    state->masks[0] = audio[0x17cu / 4u];
    state->position = (uint16_t)((audio[0x10cu / 4u] >> 16u) & 0x3fu);
    return 0u;
}

uint32_t gx8002_xip_audio_noise_102047ac(void)
{
    return audio[0x1b8u / 4u];
}

uint32_t gx8002_xip_audio_vad_query_10207404(void *ignored_pcm)
{
    (void)ignored_pcm; /* Native r0 is replaced by noise at entry. */
    uint32_t noise = gx8002_xip_audio_noise_102047ac();
    volatile uint32_t *const mode =
        (volatile uint32_t *)(uintptr_t)UINT32_C(0x2002dfa4);
    uint32_t target = 0u;
    if (noise < UINT32_C(0x300000)) target = 4u;
    else if ((uint32_t)(noise - UINT32_C(0x300000)) < UINT32_C(0x300000))
        target = 3u;
    else if ((uint32_t)(noise - UINT32_C(0x600000)) <= UINT32_C(0xe00000))
        target = 2u;
    else if (noise > UINT32_C(0x1400000)) target = 1u;

    if (target != 0u && *mode != target) {
        switch (target) {
        case 4u: gx8002_xip_tws_publish_10206c24("[LVP_AUD]vad param 4 [%d]\n", noise); break;
        case 3u: gx8002_xip_tws_publish_10206c24("[LVP_AUD]vad param 3 [%d]\n", noise); break;
        case 2u: gx8002_xip_tws_publish_10206c24("[LVP_AUD]vad param 2 [%d]\n", noise); break;
        default: gx8002_xip_tws_publish_10206c24("[LVP_AUD]vad param 1 [%d]\n", noise); break;
        }
        *mode = target;
        gx8002_xip_audio_vad_curve1_10204630(0x400u, 0xf00u);
        gx8002_xip_audio_vad_curve2_10204664(0x4cdu, 0x600u);
        gx8002_xip_audio_vad_curve3_10204698(0x4cdu, 0x2000);
        gx8002_xip_audio_vad_curve4_102046d8(0x733u, 0x333u);
        gx8002_xip_audio_vad_curve5_1020470c(0xa00u);
        gx8002_xip_audio_vad_chipping_1020472c(0x0106028fu, 0x00210083u);
        gx8002_xip_audio_vad_weight_102045f4(0x101u);
    }

    struct vad_state state;
    gx8002_xip_audio_vad_state_1020477c(&state);
    uint32_t position = ((uint32_t)state.position + 94u) % 95u;
    uint32_t mask_word = state.masks[position / 32u];
    uint32_t selected = mask_word & (UINT32_C(1) << (position & 31u));
    return *mode == 1u || selected != 0u;
}

/* Native 0x102075c8 is the environment-noise state transition called by
 * the audio callback. The old candidate import name says "tws_commit" but
 * its address and ABI are this function; retain that link name for now. */
uint32_t gx8002_xip_tws_commit_102075c8(void *context)
{
    uint32_t noise = gx8002_xip_audio_noise_102047ac();
    volatile uint32_t *const state =
        (volatile uint32_t *)(uintptr_t)UINT32_C(0x2002dfa0);
    volatile uint8_t *const marker = (volatile uint8_t *)context + 0xeu;
    uint32_t selected;
    if (noise > UINT32_C(0x3f00000)) {
        uint32_t count = state[0x0cu / 4u] + 1u;
        state[0x0cu / 4u] = count;
        if ((int32_t)count < 151) goto retain;
        state[0x10u / 4u] = 0u;
        state[0x14u / 4u] = 0u;
        selected = 2u;
    } else if (noise > UINT32_C(0x600000)) {
        uint32_t count = state[0x10u / 4u] + 1u;
        state[0x10u / 4u] = count;
        if ((int32_t)count < 51) goto retain;
        state[0x0cu / 4u] = 0u;
        state[0x14u / 4u] = 0u;
        selected = 1u;
    } else {
        uint32_t count = state[0x14u / 4u] + 1u;
        state[0x14u / 4u] = count;
        if ((int32_t)count < 151) goto retain;
        state[0x0cu / 4u] = 0u;
        state[0x14u / 4u] = 0u;
        selected = 0u;
    }
    state[0x18u / 4u] = selected;
    *marker = (uint8_t)((*marker & 0xf8u) | (selected & 7u));
    return 0u;

retain:
    *marker = (uint8_t)((*marker & 0xf8u) | (state[0x18u / 4u] & 7u));
    return 0u;
}
