/* SPDX-License-Identifier: MIT
 * NOR program/erase callers BL stock 0x415fae with format in R0 and
 * variadic words in R1-R3/on stack. Preserve all words by tail branch.
 */
#include <stdint.h>

__attribute__((naked)) uint32_t opencfw_bl_printf(const char *format, ...)
{
    __asm__ volatile("b.w opencfw_provider_415fae");
}
