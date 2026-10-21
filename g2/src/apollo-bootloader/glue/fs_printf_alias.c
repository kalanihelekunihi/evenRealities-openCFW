/* SPDX-License-Identifier: MIT
 * Littlefs NOR callbacks pass a format pointer followed by ordinary ARM
 * variadic words. Their locked-image call target is the formatter at
 * 0x415fae, whose selected source entry is opencfw_provider_415fae.
 * Preserve argument registers and caller stack by branching directly.
 */
#include <stdint.h>

__attribute__((naked)) void opencfw_boot_fs_printf(uintptr_t format, ...)
{
    __asm__ volatile("b.w opencfw_provider_415fae");
}
