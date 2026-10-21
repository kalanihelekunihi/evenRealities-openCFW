/* SPDX-License-Identifier: MIT
 * Stock 0x423e14..0x423e40 MSPI mode-word transition. This body operates on
 * the state word at offset 0x838; its caller owns the surrounding sequence.
 */
#include <stdint.h>

uint32_t opencfw_boot_mspi_stage_two_mode_flags(void *context, uint32_t flags)
{
    volatile uint32_t *const mode = (volatile uint32_t *)
        ((volatile uint8_t *)context + 0x838u);
    const uint32_t current = *mode;
    if (current == 1u) {
        *mode = 2u;
        return flags | 0x40a0u;
    }
    if (current == 2u)
        return 0x4000u;
    return flags | 0x4080u;
}
