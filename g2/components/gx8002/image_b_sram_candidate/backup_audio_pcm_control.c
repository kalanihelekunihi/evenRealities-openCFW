/* SPDX-License-Identifier: MIT
 * Image-B 0x10005978: native per-channel PCM control and busy wait.
 * Each register update is a separate volatile operation in the original.
 */
#include <stdint.h>

#define AUDIO_ENABLE (*(volatile uint32_t *)(uintptr_t)UINT32_C(0xa0a00100))
static void set_field(volatile uint32_t *word, uint32_t mask, uint32_t value)
{
    *word = (*word & ~mask) | (value & mask);
}

void gx8002_image_b_audio_pcm_control_10005978(uint32_t channel,
                                                 uint32_t active,
                                                 uint32_t direction,
                                                 uint32_t sign)
{
    volatile uint32_t *control;
    if (channel == 1u) {
        control = (volatile uint32_t *)(uintptr_t)UINT32_C(0xa0a00010);
        set_field(&AUDIO_ENABLE, 1u << 18, (active & 1u) << 18);
    } else if (channel == 2u) {
        control = (volatile uint32_t *)(uintptr_t)UINT32_C(0xa0a00030);
        *control &= ~(1u << 28);
        set_field(&AUDIO_ENABLE, 1u << 19, (active & 1u) << 19);
    } else if (channel == 4u) {
        control = (volatile uint32_t *)(uintptr_t)UINT32_C(0xa0a00050);
        *control &= ~(1u << 28);
        set_field(&AUDIO_ENABLE, 1u << 20, (active & 1u) << 20);
    } else {
        /* Native invalid-channel path dereferences null. Retain its actual
         * architectural memory access rather than inventing a return. */
        __asm__ volatile ("movi r3, 0\nld.w r2, (r3, 0)\nst.w r2, (r3, 0)"
                          : : : "r2", "r3", "memory");
        return;
    }
    set_field(control, 1u << 26, 1u << 26);
    while (control[5] != 0u) { }
    set_field(control, 1u << 26, 0u);
    set_field(control, 1u << 27, (active == 0u) ? 1u << 27 : 0u);
    set_field(control, 1u << 25, (direction == 0u) ? 1u << 25 : 0u);
    set_field(control, 1u << 24, 1u << 24);
    set_field(control, 0xffffu, 0x6000u);
    set_field(control, 1u << 31, (sign & 1u) << 31);
    set_field(control + 1, 0xffu << 16, 0u);
    set_field(control + 1, 0xffffu, 0x10u);
}
