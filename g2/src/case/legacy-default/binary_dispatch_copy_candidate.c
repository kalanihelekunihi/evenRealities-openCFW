/* SPDX-License-Identifier: MIT
 * Stock 0x080001b4 forward-copy body shared by 0x3d and common-forward routes.
 */
#include <stdint.h>

uint32_t case_binary_3d_dispatch(uint32_t destination, const uint8_t *frame,
                                  uint32_t length)
{
    volatile uint8_t *out = (volatile uint8_t *)(uintptr_t)destination;
    for (uint32_t i = 0; i < length; ++i)
        out[i] = frame[i];
    return destination + length;
}

uint32_t case_binary_forward_dispatch(uint32_t destination,
                                       const uint8_t *frame,
                                       uint32_t length)
    __attribute__((alias("case_binary_3d_dispatch")));
