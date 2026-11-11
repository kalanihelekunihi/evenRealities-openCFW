/* SPDX-License-Identifier: MIT
 * Image-B three-word audio buffer target 0x10005a5c. Native selector 1/2/4
 * chooses a0a00010/30/50; the invalid selector writes addresses 8/c/10.
 */
#include <stdint.h>
#include "../csky_ops.h"

static void store_triplet(uintptr_t base, uint32_t first,
                          uint32_t second, uint32_t third)
{
    volatile uint32_t *words = (volatile uint32_t *)base;
    words[2] = first;
    words[3] = second;
    words[4] = third;
}

uint32_t gx8002_image_b_audio_triplet_10005a5c(
    uint32_t channel, uint32_t first, uint32_t second, uint32_t third)
{
    uintptr_t base;
    if (channel == 1u) {
        base = UINT32_C(0xa0a00010);
    } else if (channel == 2u) {
        base = UINT32_C(0xa0a00030);
        volatile uint32_t *control = (volatile uint32_t *)base;
        *control = *control & ~(1u << 28);
    } else if (channel == 4u) {
        base = UINT32_C(0xa0a00050);
        volatile uint32_t *control = (volatile uint32_t *)base;
        *control = *control & ~(1u << 28);
    } else {
        /* Stock stores to 0x8/0xc/0x10 for an invalid channel (base 0). */
        volatile uint32_t *const null_page = csky_word_ptr(0u);
        null_page[0x8 / 4] = first;
        null_page[0xc / 4] = second;
        null_page[0x10 / 4] = third;
        return 0u;
    }
    store_triplet(base, first, second, third);
    return 0u;
}
