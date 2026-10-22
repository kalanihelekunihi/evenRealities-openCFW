/* SPDX-License-Identifier: MIT
 * CASE 0x08004d04 peripheral interrupt clear. Native callbacks at 0x4d2c
 * and 0x4d00 are BX LR and have no side effect.
 */
#include <stdint.h>
/* Stock 0x08004D04 (case_dispatch_pending) */
void case_boot_irq_clear(uint32_t mask)
{
    volatile uint32_t *const status=(volatile uint32_t *)(uintptr_t)0x40021800u;
    if((status[3]&mask)!=0u)status[3]=mask;
    if((status[4]&mask)!=0u)status[4]=mask;
}
