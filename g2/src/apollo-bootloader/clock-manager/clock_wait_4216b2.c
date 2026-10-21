/* SPDX-License-Identifier: MIT
 * Stock 0x4216b2..0x4216d4. The callers at 0x421ba4, 0x421d28, and
 * 0x421e8c pass a byte-active flag and a mutable timeout. The recovered
 * two-argument body delays 10 us before each decrement, then returns when
 * either the count or the active byte reaches zero. Its decompiler's R3
 * return is ambient register state ignored by each authenticated caller.
 */
#include "clock_wait_4216b2.h"

extern void opencfw_bl_delay_us(uint32_t microseconds);

void opencfw_bl_clock_wait_active(volatile const uint8_t *active,
                                  uint32_t *remaining)
{
    while (*remaining != 0u && *active != 0u) {
        opencfw_bl_delay_us(10u);
        *remaining -= 1u;
    }
}
