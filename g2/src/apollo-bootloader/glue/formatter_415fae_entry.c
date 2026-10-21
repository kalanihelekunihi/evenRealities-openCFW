/* SPDX-License-Identifier: MIT
 * Source-owned entry for stock 0x415fae..0x415fda. It preserves the
 * nonstandard return R1 = incoming R3 as well as the variadic stack cursor.
 * The parser and callback bodies remain separate providers.
 */
#include <stdint.h>

__attribute__((naked)) uint32_t opencfw_provider_415fae(const char *format, ...)
{
    __asm__ volatile(
        "push {r1, r2, r3}\n"
        "push {r3, r4, r5, r6, lr}\n"
        "mov r1, r0\n"
        "ldr r5, =0x200270cc\n"
        "ldr r0, [r5]\n"
        "cmp r0, #0\n"
        "bne 1f\n"
        "movs r0, #0\n"
        "b 2f\n"
        "1:\n"
        "add r2, sp, #20\n"
        "ldr r6, =0x20024cd0\n"
        "mov r0, r6\n"
        "bl opencfw_boot_plain_vsprintf\n"
        "mov r4, r0\n"
        "mov r0, r6\n"
        "ldr r1, [r5]\n"
        "blx r1\n"
        "mov r0, r4\n"
        "2:\n"
        "pop {r1, r4, r5, r6}\n"
        "ldr pc, [sp], #16\n"
    );
}
