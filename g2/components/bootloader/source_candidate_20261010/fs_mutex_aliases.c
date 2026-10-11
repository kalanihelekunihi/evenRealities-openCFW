/* SPDX-License-Identifier: MIT
 * Filesystem/allocator mutex entries bind to stock Thumb 0x4166ab/0x416711.
 */
#include <stdint.h>

__attribute__((naked)) uint32_t opencfw_boot_fs_mutex_acquire(uintptr_t handle,
    uint32_t timeout)
{
    __asm__ volatile("b.w opencfw_boot_mutex_acquire");
}

__attribute__((naked)) uint32_t opencfw_boot_fs_mutex_release(uintptr_t handle)
{
    __asm__ volatile("b.w opencfw_boot_mutex_release");
}
