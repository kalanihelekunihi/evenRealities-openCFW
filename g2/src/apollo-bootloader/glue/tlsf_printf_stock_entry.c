/* SPDX-License-Identifier: MIT
 * Pinned TLSF add_pool/create diagnostics at stock 0x41715c/0x417208 call
 * stock formatter 0x415fae directly. This C-compilable Thumb entry preserves
 * the variadic AAPCS register/stack argument layout by tail branching to the
 * selected source-owned 0x415fae formatter entry. The optional upstream
 * walker formats are bounded separately; runtime sink/hardware remain open.
 */
#include <stdint.h>

__attribute__((naked)) int printf(const char *format, ...)
{
    __asm__ volatile("b.w opencfw_provider_415fae");
}
