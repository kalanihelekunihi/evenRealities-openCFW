/* SPDX-License-Identifier: MIT
 * Both public queue-get callers bind to stock Thumb 0x416921.
 */
#include <stdint.h>

__attribute__((naked)) int32_t opencfw_provider_416920(uintptr_t queue,
    void *message, uintptr_t priority, uint32_t timeout)
{
    __asm__ volatile("b.w opencfw_bl_queue_get");
}

__attribute__((naked)) uint32_t opencfw_boot_dfu_queue_get(uint32_t queue,
    void *message, uint32_t priority, uint32_t timeout)
{
    __asm__ volatile("b.w opencfw_bl_queue_get");
}
