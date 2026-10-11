/* SPDX-License-Identifier: MIT
 * Attributed CASE initial clock and scheduler state from authenticated CRT.
 * Clock consumers: SysTick 0x8420, clock plan 0x4f14, console 0x4480.
 * Scheduler start 0xc57c replaces the native 0xaaaaaaaa fill sentinel.
 */
#include <stdint.h>

enum { CASE_INITIAL_SYSTEM_CLOCK_HZ=16000000u };

void case_crt_init_clock_scheduler_defaults(void)
{
    *(volatile uint8_t *)(uintptr_t)0x20000118u=1u;
    *(volatile uint32_t *)(uintptr_t)0x2000011cu=4u;
    *(volatile uint32_t *)(uintptr_t)0x20000124u=CASE_INITIAL_SYSTEM_CLOCK_HZ;
    *(volatile uint32_t *)(uintptr_t)0x2000019cu=0xaaaaaaaau;
}
