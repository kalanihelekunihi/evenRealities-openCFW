/* SPDX-License-Identifier: MIT
 * Image-B 0x10009968 overlap-safe move with native direction decision.
 */
#include <stdint.h>

extern void gx8002_image_b_copy_10011344(void *destination,
                                           const void *source, uint32_t count);

void *gx8002_image_b_move_10009968(void *destination,
                                    const void *source, uint32_t count)
{
    volatile uint8_t *to = (volatile uint8_t *)destination;
    const volatile uint8_t *from = (const volatile uint8_t *)source;
    if ((uintptr_t)to >= (uintptr_t)from) {
        to += count;
        from += count;
        while (count != 0u) {
            *--to = *--from;
            --count;
        }
    } else {
        gx8002_image_b_copy_10011344(destination, source, count);
    }
    return destination;
}
