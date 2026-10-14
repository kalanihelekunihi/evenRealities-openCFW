/* SPDX-License-Identifier: MIT
 * Main 0x53909a command queue term. Index refresh remains a named lower.
 */
#include <stdint.h>

extern void g2_main_cq_update_indices_538d18(uint32_t *);

uint32_t g2_main_cq_term_53909a(uint32_t *queue, uint32_t force)
{
    if (queue == 0 || (queue[0] & UINT32_C(0x01ffffff)) !=
                          UINT32_C(0x01cdcdcd))
        return 2u;

    g2_main_cq_update_indices_538d18(queue);
    if ((uint8_t)force == 0u && queue[7] != queue[8])
        return 3u;

    queue[0] &= ~UINT32_C(0x01000000);
    const uintptr_t ops = queue[9];
    const uintptr_t option_register = *(const volatile uint32_t *)ops;
    volatile uint32_t *const option = (volatile uint32_t *)option_register;
    *option &= ~UINT32_C(1);
    const uintptr_t control_register =
        *(const volatile uint32_t *)(ops + 0x10u);
    const uint32_t control_mask =
        *(const volatile uint32_t *)(ops + 0x14u);
    *(volatile uint32_t *)control_register &= ~control_mask;
    return 0u;
}
