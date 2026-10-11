/* SPDX-License-Identifier: MIT
 * Exact-address caller adapters for stock Thumb 0x4160ff.
 */
#include <stdint.h>

__attribute__((naked)) uint32_t opencfw_boot_dfu_thread_new(uintptr_t entry,
    uintptr_t argument, const void *attributes)
{
    __asm__ volatile("b.w opencfw_boot_thread_new");
}

__attribute__((naked)) uintptr_t opencfw_provider_4160fe(uintptr_t entry,
    uintptr_t argument, const uint32_t *attributes)
{
    __asm__ volatile("b.w opencfw_boot_thread_new");
}
