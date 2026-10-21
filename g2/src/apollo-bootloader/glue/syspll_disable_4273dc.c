/* SPDX-License-Identifier: MIT
 * Stock 0x4273dc..0x42740c, with token and register address read from the
 * locked literal pool at 0x4275ac and 0x4275b4 respectively. MMIO execution
 * remains hardware dependent.
 */
#include <stdint.h>
#include <stddef.h>

uint32_t opencfw_boot_syspll_disable(void *handle)
{
    volatile uint32_t *const state = (volatile uint32_t *)handle;
    if (state == NULL || (*state & UINT32_C(0x01ffffff)) != UINT32_C(0x01504c30))
        return 2u;

    volatile uint32_t *const pll = (volatile uint32_t *)(uintptr_t)UINT32_C(0x400204d8);
    *pll &= UINT32_C(0xdfffffff);
    *state &= UINT32_C(0xfdffffff);
    return 0u;
}
