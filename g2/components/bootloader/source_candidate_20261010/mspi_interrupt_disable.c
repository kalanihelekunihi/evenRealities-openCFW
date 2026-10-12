/* SPDX-License-Identifier: BSD-3-Clause
 * Stock bootloader 0x426484..0x4264ba; Ambiq HAL 5.1.0
 * am_hal_mspi_interrupt_disable. The handle token, module stride, and INTEN
 * offset are also present in the locked native pseudocode. Hardware effects
 * have not been exercised on a physical Apollo510.
 */
#include <stdint.h>
#include <stddef.h>

uint32_t am_hal_mspi_interrupt_disable(void *handle, uint32_t mask)
{
    const volatile uint32_t *const state = (const volatile uint32_t *)handle;
    if (state == NULL || (state[0] & UINT32_C(0x01ffffff)) != UINT32_C(0x01bebebe))
        return 2u;

    const uint32_t module = state[1];
    volatile uint32_t *const inten = (volatile uint32_t *)(uintptr_t)
        (UINT32_C(0x40060000) + module * UINT32_C(0x1000) + UINT32_C(0x200));
    *inten &= ~mask;
    return 0u;
}
