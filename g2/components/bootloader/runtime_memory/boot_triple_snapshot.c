/* SPDX-License-Identifier: MIT
 * Native 0x422aac captures three consecutive reads of one volatile source
 * under PRIMASK, restores the incoming mask, then publishes the three words.
 * The source pointer is borrowed; the destination owns at least three words.
 */
#include <stdint.h>

void opencfw_boot_triple_snapshot(const volatile uint32_t *source,
                                  uint32_t output[3])
{
    uint32_t previous_mask;
    __asm volatile("mrs %0, primask\n\tcpsid i"
                   : "=r"(previous_mask) :: "memory");
    const uint32_t first = *source;
    const uint32_t second = *source;
    const uint32_t third = *source;
    __asm volatile("msr primask, %0" :: "r"(previous_mask) : "memory");
    output[0] = first;
    output[1] = second;
    output[2] = third;
}
