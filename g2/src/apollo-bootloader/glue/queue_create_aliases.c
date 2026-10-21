/* SPDX-License-Identifier: MIT
 * Both public queue-create callers bind to stock Thumb 0x416817.
 */
#include <stdint.h>

__attribute__((naked)) uintptr_t opencfw_provider_416816(uint32_t count,
    uint32_t size, const void *attributes)
{
    __asm__ volatile("b.w opencfw_bl_queue_create");
}

__attribute__((naked)) uint32_t opencfw_boot_dfu_queue_new(uint32_t count,
    uint32_t size, uintptr_t attributes)
{
    __asm__ volatile("b.w opencfw_bl_queue_create");
}
