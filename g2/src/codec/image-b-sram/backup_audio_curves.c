/* SPDX-License-Identifier: MIT
 * Image-B native FFT VAD setters 0x10005b34, 0x10005b68, 0x10005b9c,
 * 0x10005bdc, 0x10005c10. Native MOVIH 0xa0a0 and offsets 0x184..194
 * identify actual MMIO words. The first four setters perform two distinct
 * volatile read/modify/write cycles; the decompiler collapsed these.
 */
#include <stdint.h>

#define AUDIO_WORD(offset) (*(volatile uint32_t *)(uintptr_t)(UINT32_C(0xa0a00000) + (offset)))

static void set_two_halves(volatile uint32_t *word, uint32_t a, uint32_t b)
{
    *word = (*word & UINT32_C(0xffff0000)) | (a & 0xffffu);
    *word = (*word & UINT32_C(0x0000ffff)) | ((b & 0xffffu) << 16);
}

int32_t gx8002_image_b_set_fftvad_curve_1_10005b34(uint32_t a, uint32_t b)
{
    if (a > 0x0c00u || b > 0x4600u) return -1;
    set_two_halves(&AUDIO_WORD(0x184u), a, b);
    return 0;
}

int32_t gx8002_image_b_set_fftvad_curve_2_10005b68(uint32_t a, uint32_t b)
{
    if (a > 0x0c00u || b > 0x1e00u) return -1;
    set_two_halves(&AUDIO_WORD(0x188u), a, b);
    return 0;
}

int32_t gx8002_image_b_set_fftvad_curve_3_10005b9c(
    uint16_t a, int16_t b)
{
    if (a > 0x1000u || (uint16_t)(b + 0x1400) > 0x2800u) return -1;
    set_two_halves(&AUDIO_WORD(0x18cu), a, (uint16_t)b);
    return 0;
}

int32_t gx8002_image_b_set_fftvad_curve_4_10005bdc(uint32_t a, uint32_t b)
{
    if (a > 0x1400u || b > 0x1400u) return -1;
    set_two_halves(&AUDIO_WORD(0x190u), a, b);
    return 0;
}

int32_t gx8002_image_b_set_fftvad_curve_5_10005c10(uint32_t value)
{
    if (value > 0x2000u) return -1;
    uint32_t old = AUDIO_WORD(0x194u);
    AUDIO_WORD(0x194u) = (old & 0xffff0000u) | value;
    return 0;
}
