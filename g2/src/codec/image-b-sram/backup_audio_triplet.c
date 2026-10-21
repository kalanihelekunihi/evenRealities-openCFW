/* SPDX-License-Identifier: MIT
 * Image-B three-word audio buffer target 0x10005a5c. Native selector 1/2/4
 * chooses a0a00010/30/50; the invalid selector writes addresses 8/c/10.
 */
#include <stdint.h>

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
        /* C null dereference is undefined; native deliberately stores to
         * 0x8/0xc/0x10. Emit those three authenticated stores directly. */
        __asm__ volatile (
            "movi r3, 0\n"
            "st.w %0, (r3, 0x8)\n"
            "st.w %1, (r3, 0xc)\n"
            "st.w %2, (r3, 0x10)\n"
            : : "r"(first), "r"(second), "r"(third) : "r3", "memory");
        return 0u;
    }
    store_triplet(base, first, second, third);
    return 0u;
}
