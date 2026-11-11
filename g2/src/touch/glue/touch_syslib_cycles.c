/* SPDX-License-Identifier: Apache-2.0
 * Freestanding C providers for the PSoC 4000T SysLib runtime. Clang's
 * integrated assembler rejects GNU .func/.endfunc in cy_syslib_gcc.S.
 * The stock delay divides the requested cycles by four, rounding with +2,
 * and executes one add/subtract loop per resulting count. Keep that loop
 * shared by application and PDL callers so both observe the same delay.
 */
#include <stdint.h>

void Cy_SysLib_DelayCycles(uint32_t cycles)
{
    cycles = (cycles + 2u) >> 2;
    if (cycles != 0u) {
        do {
            cycles += 1u;
            /* Keep the two arithmetic steps separate like stock. The empty
             * constraint changes no registers or emitted instructions. */
            __asm__ volatile("" : "+r"(cycles));
            cycles -= 2u;
        } while (cycles != 0u);
        __asm__ volatile("nop");
    }
    __asm__ volatile("nop");
}

uint32_t Cy_SysLib_EnterCriticalSection(void)
{
    uint32_t primask;
    __asm__ volatile("mrs %0, primask" : "=r"(primask));
    __asm__ volatile("cpsid i" ::: "memory");
    return primask;
}

void Cy_SysLib_ExitCriticalSection(uint32_t savedIntrStatus)
{
    __asm__ volatile("msr primask, %0" :: "r"(savedIntrStatus) : "memory");
}
