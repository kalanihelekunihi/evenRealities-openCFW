/* SPDX-License-Identifier: MIT
 * Main 0x538e3c command queue enable, sourced from locked instruction flow.
 */
#include <stdint.h>

uint32_t g2_main_cq_enable_538e3c(uint32_t *queue)
{
    if (queue == 0 || (queue[0] & UINT32_C(0x01ffffff)) !=
                          UINT32_C(0x01cdcdcd))
        return 2u;
    if (queue[0] & UINT32_C(0x02000000))
        return 0u;

    if (queue[2] >= UINT32_C(0x20080000))
        __asm__ volatile("dmb sy" ::: "memory");
    const uintptr_t ops = queue[9];
    const uintptr_t option_register =
        *(const volatile uint32_t *)ops;
    *(volatile uint32_t *)option_register |= UINT32_C(1);
    queue[0] |= UINT32_C(0x02000000);
    return 0u;
}
