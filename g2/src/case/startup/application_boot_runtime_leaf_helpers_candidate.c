/* SPDX-License-Identifier: MIT
 * Native CASE 0x080001e6 zero-fill, 0x080001ea preserving-fill wrapper,
 * and 0x0800a794/0xa7a2 delay leaves.
 */
#include <stdint.h>
extern void case_boot_task_fill(uint32_t,uint32_t,uint8_t); /* 0x01d8 */
/* Stock 0x080001E6 (case_boot_zero_fill) */
void case_boot_zero_fill(uint32_t destination,uint32_t count)
{case_boot_task_fill(destination,count,0u);}
/* Stock 0x080001EA (case_boot_memset_return_start) */
void *case_boot_memset_return_start(void *destination,uint32_t value,uint32_t count)
{
    case_boot_task_fill((uint32_t)(uintptr_t)destination,count,value);
    return destination;
}
/* Single-wire bus bit timing (2510 on PA3, 4005 on PB2). Stock loop is
 * "nop; adds; cmp; blt" = 5 cycles per count on Cortex-M0+ (64 MHz, flash
 * 2 WS with prefetch+ICACHE, so the loop runs from cache): 78 ns per count.
 * The NOP takes the counter as an operand so the compiler must keep the
 * up-counting compare loop (it would otherwise emit a 4-cycle "subs; bne"
 * loop, 20% short). Checked with build/case-link/timing.py. */
/* Stock 0x0800A794 (case_busy_delay) */
void case_boot_short_delay_a794(uint32_t count)
{for(int32_t i=0;i<(int32_t)count;++i)__asm__ volatile("nop":"+r"(i));}
/* Stock 0x0800A7A2 (case_busy_delay_alt) */
void case_boot_short_delay_a7a2(uint32_t count)
{for(int32_t i=0;i<(int32_t)count;++i)__asm__ volatile("nop":"+r"(i));}
/* Dedup: legacy name of stock 0x0800a7a2 (was a volatile stack loop in
 * legacy-default/bus_pin_leaves_candidate.c, 2.2x slower than stock). */
__typeof__(case_boot_short_delay_a7a2) case_bus_delay __attribute__((alias("case_boot_short_delay_a7a2")));
