/* SPDX-License-Identifier: MIT
 * Native CASE 0x0800c57c scheduler peripheral start and context handoff.
 */
#include <stdint.h>
extern void case_boot_systick_start(void); /* 0xc078 */
extern void case_boot_context_switch(void); /* 0x00cc, architectural PSP handoff */
void case_boot_scheduler_run(void)
{
    volatile uint32_t *priority=(volatile uint32_t *)(uintptr_t)0xe000ed20u;
    *priority=*priority|0x00ff0000u;
    *priority=*priority|0xff000000u;
    case_boot_systick_start();
    *(volatile uint32_t *)(uintptr_t)0x2000019cu=0u;
    case_boot_context_switch();
}
