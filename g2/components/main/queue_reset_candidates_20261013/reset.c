/* SPDX-License-Identifier: MIT
 * Main 0x53916e: reset the command queue's ring and hardware indices.
 */
#include <stdint.h>

uint32_t g2_main_queue_reset_53916e(uint32_t queue)
{
    if (queue == 0u) return 2u;
    volatile uint32_t *const state =
        (volatile uint32_t *)(uintptr_t)queue;
    if ((state[0] & UINT32_C(0x01ffffff)) != UINT32_C(0x01cdcdcd))
        return 2u;
    if ((state[0] & UINT32_C(0x02000000)) != 0u)
        return 7u;

    const uint32_t ops = state[9];
    volatile uint32_t *const control =
        (volatile uint32_t *)(uintptr_t)
        *(const volatile uint32_t *)(uintptr_t)ops;
    *control &= UINT32_C(0xfffffffe);
    const uint32_t initial = state[1];
    state[3] = initial;
    state[5] = initial;
    state[4] = initial;
    state[7] = 0u;
    state[8] = 0u;
    *(volatile uint32_t *)(uintptr_t)
        *(const volatile uint32_t *)(uintptr_t)(ops + 8u) = 0u;
    *(volatile uint32_t *)(uintptr_t)
        *(const volatile uint32_t *)(uintptr_t)(ops + 0xcu) = 0u;
    *(volatile uint32_t *)(uintptr_t)
        *(const volatile uint32_t *)(uintptr_t)(ops + 4u) = initial;
    state[0] &= UINT32_C(0xfdffffff);
    return 0u;
}
