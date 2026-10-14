/* SPDX-License-Identifier: MIT
 * Main 0x538e8c command queue disable, compared with the locked image.
 */
#include <stdint.h>

uint32_t g2_main_cq_disable_538e8c(uint32_t *queue)
{
    if (queue == 0 || (queue[0] & UINT32_C(0x01ffffff)) !=
                          UINT32_C(0x01cdcdcd))
        return 2u;
    if ((queue[0] & UINT32_C(0x02000000)) == 0u)
        return 0u;

    const uintptr_t ops = queue[9];
    const uintptr_t option_register =
        *(const volatile uint32_t *)ops;
    volatile uint32_t *const option =
        (volatile uint32_t *)option_register;
    *option &= ~UINT32_C(1);
    queue[0] &= ~UINT32_C(0x02000000);
    return 0u;
}
