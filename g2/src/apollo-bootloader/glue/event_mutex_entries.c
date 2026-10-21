/* SPDX-License-Identifier: MIT
 * Event timer callback calls stock mutex entries 0x4166aa and 0x416710.
 * Preserve the AAPCS R0/R1 input words by tail branching to selected bodies.
 */
#include <stdint.h>

__attribute__((naked)) int32_t opencfw_provider_4166aa(uintptr_t handle,
                                                           uint32_t timeout)
{
    __asm__ volatile("b.w opencfw_boot_mutex_acquire");
}

__attribute__((naked)) int32_t opencfw_provider_416710(uintptr_t handle)
{
    __asm__ volatile("b.w opencfw_boot_mutex_release");
}
