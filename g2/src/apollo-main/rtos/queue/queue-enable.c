/* SPDX-License-Identifier: MIT
 * Main 0x539994 queue enable after peripheral readiness bits settle.
 */
#include <stdint.h>

uint32_t g2_main_queue_enable_539994(uint32_t queue)
{
    if (queue == 0u ||
        (*(const volatile uint32_t *)(uintptr_t)queue &
         UINT32_C(0x01ffffff)) != UINT32_C(0x01504c30))
        return 2u;
    volatile uint32_t *const handle =
        (volatile uint32_t *)(uintptr_t)queue;
    if ((*handle & UINT32_C(0x02000000)) != 0u)
        return 0u;
    const uint32_t status =
        *(const volatile uint32_t *)(uintptr_t)UINT32_C(0x40020060);
    if ((status & UINT32_C(0x000f0000)) != UINT32_C(0x000f0000))
        return 7u;
    volatile uint32_t *const control =
        (volatile uint32_t *)(uintptr_t)UINT32_C(0x400204d8);
    *control |= UINT32_C(0x20000000);
    *handle |= UINT32_C(0x02000000);
    return 0u;
}
