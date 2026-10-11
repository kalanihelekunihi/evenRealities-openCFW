/* SPDX-License-Identifier: MIT
 * Platform initializer binds to stock semaphore Thumb 0x416763.
 */
#include <stdint.h>

__attribute__((naked)) uintptr_t opencfw_bl_semaphore_create(uint32_t maximum,
    uint32_t initial, const uint32_t *attributes)
{
    __asm__ volatile("b.w opencfw_boot_semaphore_create");
}
