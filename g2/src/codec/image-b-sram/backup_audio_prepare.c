/* SPDX-License-Identifier: MIT
 * Full image-B audio preparation 0x100051ec..0x10005327. Ghidra stopped
 * at the bit-8 wait; native branch 0x10005284 resumes at 0x10005288.
 */
#include <stdint.h>

#define AUDIO_WORD(offset) (*(volatile uint32_t *)(uintptr_t)(UINT32_C(0xa0a00000) + (offset)))

static void set_bit(volatile uint32_t *word, uint32_t bit, uint32_t enabled)
{
    uint32_t mask = UINT32_C(1) << bit;
    *word = (*word & ~mask) | (enabled != 0u ? mask : 0u);
}

void gx8002_image_b_audio_prepare_100051ec(void)
{
    AUDIO_WORD(0x100u) = 0u;
    AUDIO_WORD(0x104u) = ~UINT32_C(0x700);
    set_bit(&AUDIO_WORD(0x00u), 31u, 0u);
    set_bit(&AUDIO_WORD(0x00u), 15u, 1u);
    set_bit(&AUDIO_WORD(0x00u), 14u, 0u);
    set_bit(&AUDIO_WORD(0x00u), 7u, 1u);
    set_bit(&AUDIO_WORD(0x00u), 6u, 0u);
    set_bit(&AUDIO_WORD(0x04u), 31u, 1u);
    set_bit(&AUDIO_WORD(0x04u), 30u, 0u);
    set_bit(&AUDIO_WORD(0x08u), 31u, 1u);
    set_bit(&AUDIO_WORD(0x08u), 30u, 0u);
    set_bit(&AUDIO_WORD(0x0cu), 9u, 0u);
    set_bit(&AUDIO_WORD(0x28u), 9u, 0u);
    set_bit(&AUDIO_WORD(0x2cu), 9u, 0u);
    set_bit(&AUDIO_WORD(0x48u), 9u, 0u);
    set_bit(&AUDIO_WORD(0x4cu), 9u, 0u);
    AUDIO_WORD(0x104u) = UINT32_C(0x200);
    while ((AUDIO_WORD(0x104u) & UINT32_C(0x100)) == 0u) { }
    AUDIO_WORD(0x104u) = UINT32_C(0x100);
    AUDIO_WORD(0x104u) = UINT32_C(0x400);
    AUDIO_WORD(0x104u) = UINT32_C(0x071f003f);
    set_bit(&AUDIO_WORD(0x108u), 15u, 1u);
    set_bit(&AUDIO_WORD(0x108u), 14u, 0u);
    set_bit(&AUDIO_WORD(0x108u), 7u, 1u);
    set_bit(&AUDIO_WORD(0x108u), 6u, 0u);
    set_bit(&AUDIO_WORD(0x108u), 23u, 1u);
    set_bit(&AUDIO_WORD(0x108u), 22u, 0u);
    set_bit(&AUDIO_WORD(0x158u), 31u, 1u);
    set_bit(&AUDIO_WORD(0x158u), 30u, 0u);
    set_bit(&AUDIO_WORD(0x180u), 31u, 1u);
    set_bit(&AUDIO_WORD(0x180u), 30u, 0u);
    set_bit(&AUDIO_WORD(0x180u), 29u, 0u);
}
