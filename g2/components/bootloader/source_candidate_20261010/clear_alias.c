/* SPDX-License-Identifier: MIT
 * NOR timing wrapper fill binds to stock Thumb 0x426c11.
 */
#include <stdint.h>

__attribute__((naked)) void *opencfw_bl_clear(void *destination,
    int value, uint32_t length)
{
    __asm__ volatile("b.w memset");
}
