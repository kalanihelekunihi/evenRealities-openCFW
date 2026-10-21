/* SPDX-License-Identifier: MIT
 * Historical entry at stock 0x41b2f8. Selected C provider emits the exact
 * 22-byte BASEPRI save/mask/barrier body under this candidate's M55 flags.
 */
#include <stdint.h>

__attribute__((naked)) uint32_t opencfw_provider_41b2f8(void)
{
    __asm__ volatile("b.w opencfw_bl_mask_interrupts");
}
