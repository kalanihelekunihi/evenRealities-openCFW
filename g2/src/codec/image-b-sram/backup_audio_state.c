/* SPDX-License-Identifier: MIT
 * Image-B FFT VAD state 0x10005c80, log-filter-bank control 0x10005ab4,
 * spectral distance 0x10005af8, and chipping 0x10005c30.
 * Type/field order follows pinned NationalChip gx_audio_in_v2.h. Native
 * MOVIH 0xa0a0 plus register offsets gives exact MMIO addresses. Ordered
 * volatile writes preserve the multi-step native hardware transitions.
 */
#include <stdint.h>

typedef struct {
    uint32_t vad_state_l;
    uint32_t vad_state_m;
    uint32_t vad_state_h;
    uint16_t vad_state_index;
} gx8002_image_b_fftvad_state;

typedef struct {
    uint8_t w1;
    uint8_t w2;
    uint8_t w3;
} gx8002_image_b_fftvad_w;

typedef struct {
    uint16_t chipping_1;
    uint16_t chipping_2;
    uint16_t chipping_3;
    uint16_t chipping_4;
} gx8002_image_b_fftvad_chipping;

#define AUDIO_WORD(offset) (*(volatile uint32_t *)(uintptr_t)(UINT32_C(0xa0a00000) + (offset)))

/* Stock 0x10005C80 (gx_audio_in_get_fftvad_state) */
int32_t gx8002_image_b_get_fftvad_state_10005c80(
    gx8002_image_b_fftvad_state *state)
{
    if (state == 0) return -1;
    state->vad_state_h = AUDIO_WORD(0x174u);
    state->vad_state_m = AUDIO_WORD(0x178u);
    state->vad_state_l = AUDIO_WORD(0x17cu);
    state->vad_state_index =
        (uint16_t)((AUDIO_WORD(0x10cu) >> 16) & 0x3fu);
    return 0;
}

/* Stock 0x10005AB4 (gx_audio_in_set_logfbank_enable) */
int32_t gx8002_image_b_set_logfbank_enable_10005ab4(
    uint32_t module_enable, uint32_t hmt_enable)
{
    uint32_t old = AUDIO_WORD(0x180u);
    AUDIO_WORD(0x180u) = (old & ~(1u << 28)) | ((hmt_enable & 1u) << 28);
    old = AUDIO_WORD(0x180u);
    AUDIO_WORD(0x180u) = (old & ~(1u << 29)) | ((module_enable & 1u) << 29);
    old = AUDIO_WORD(0x180u);
    AUDIO_WORD(0x180u) = (old & ~(1u << 30)) | ((module_enable & 1u) << 30);
    old = AUDIO_WORD(0x180u);
    AUDIO_WORD(0x180u) = (old & ~(1u << 31)) |
        ((module_enable == 0u ? 1u : 0u) << 31);
    return 0;
}

/* Stock 0x10005AF8 (gx_audio_in_set_fftvad_w) */
int32_t gx8002_image_b_set_fftvad_w_10005af8(gx8002_image_b_fftvad_w w)
{
    uint32_t old = AUDIO_WORD(0x158u);
    AUDIO_WORD(0x158u) = (old & ~(0xfu << 8)) |
        (((uint32_t)w.w1 & 0xfu) << 8);
    old = AUDIO_WORD(0x158u);
    AUDIO_WORD(0x158u) = (old & ~(0xfu << 12)) |
        (((uint32_t)w.w2 & 0xfu) << 12);
    old = AUDIO_WORD(0x158u);
    AUDIO_WORD(0x158u) = (old & ~(0xfu << 16)) |
        (((uint32_t)w.w3 & 0xfu) << 16);
    return 0;
}

/* Stock 0x10005C30 (gx_audio_in_set_fftvad_chipping) */
int32_t gx8002_image_b_set_fftvad_chipping_10005c30(
    gx8002_image_b_fftvad_chipping c)
{
    uint32_t old = AUDIO_WORD(0x198u);
    AUDIO_WORD(0x198u) = (old & 0xffff0000u) | c.chipping_1;
    old = AUDIO_WORD(0x198u);
    AUDIO_WORD(0x198u) = (old & 0x0000ffffu) | ((uint32_t)c.chipping_2 << 16);
    old = AUDIO_WORD(0x19cu);
    AUDIO_WORD(0x19cu) = (old & 0xffff0000u) | c.chipping_3;
    old = AUDIO_WORD(0x19cu);
    AUDIO_WORD(0x19cu) = (old & 0x0000ffffu) | ((uint32_t)c.chipping_4 << 16);
    return 0;
}
