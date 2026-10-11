/* SPDX-License-Identifier: MIT
 * CASE 0x0800ade8 timer-list wait selection.
 */
#include <stdint.h>
static uint32_t rd(uint32_t a){return *(volatile uint32_t *)(uintptr_t)a;}
uint32_t case_boot_timer_wait_next(uint32_t *deadline)
{
    uint32_t list=rd(0x20000170u);
    if(rd(list)==0u){*deadline=1u;return 0u;}
    *deadline=0u;
    return rd(rd(list+12u));
}
