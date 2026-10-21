/* SPDX-License-Identifier: MIT
 * Platform-finish transfer transaction binds to stock Thumb 0x42c989.
 */
#include <stdint.h>

__attribute__((naked)) uint32_t opencfw_bl_config_transaction(uint32_t handle,
    uint32_t command, uint32_t retain)
{
    __asm__ volatile("b.w opencfw_boot_context_transaction");
}
