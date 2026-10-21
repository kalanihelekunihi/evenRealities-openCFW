/* SPDX-License-Identifier: MIT
 * Image-B 0x10011344 forward copy, including its native access schedule.
 */
#include <stdint.h>
#include <stddef.h>

void gx8002_image_b_copy_10011344(void *destination,
                                   const void *source, uint32_t count)
{
    volatile uint8_t *to = (volatile uint8_t *)destination;
    const volatile uint8_t *from = (const volatile uint8_t *)source;

    if ((((uintptr_t)to | (uintptr_t)from) & 3u) != 0u) {
        while (count != 0u) {
            *to++ = *from++;
            --count;
        }
        return;
    }

    while ((int32_t)count >= 16) {
        const volatile uint32_t *words_from =
            (const volatile uint32_t *)from;
        volatile uint32_t *words_to = (volatile uint32_t *)to;
        uint32_t first = words_from[0];
        uint32_t second = words_from[1];
        uint32_t third = words_from[2];
        words_to[0] = first;
        uint32_t fourth = words_from[3];
        words_to[1] = second;
        words_to[2] = third;
        words_to[3] = fourth;
        from += 16;
        to += 16;
        count -= 16u;
    }
    while ((int32_t)count >= 4) {
        uint32_t word = *(const volatile uint32_t *)from;
        from += 4;
        *(volatile uint32_t *)to = word;
        to += 4;
        count -= 4u;
    }
    while (count != 0u) {
        uint8_t byte = *from++;
        *to++ = byte;
        --count;
    }
}
