/* SPDX-License-Identifier: MIT
 * Manager and DFU send callers bind to stock Thumb 0x4168a3.
 */
#include <stdint.h>

__attribute__((naked)) int32_t opencfw_provider_4168a2(uintptr_t queue,
    const void *message, uint32_t priority, uint32_t timeout)
{
    __asm__ volatile("b.w opencfw_bl_queue_put");
}

__attribute__((naked)) uint32_t opencfw_boot_dfu_queue_put(uint32_t queue,
    const void *message, uint32_t priority, uint32_t timeout)
{
    __asm__ volatile("b.w opencfw_bl_queue_put");
}
