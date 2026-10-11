/* SPDX-License-Identifier: MIT
 * Isolated ABI-preserving lead for platform bringup's seven direct calls to
 * stock formatter 0x415fae. That caller includes two binary64 `%f` formats.
 * The selected formatter entry exists, but a composed FP64/FPSCR/output
 * oracle for these callsites has not qualified archive selection.
 */
#include <stdint.h>

__attribute__((naked)) uint32_t opencfw_bl_generic_log(const char *format, ...)
{
    __asm__ volatile("b.w opencfw_provider_415fae");
}
