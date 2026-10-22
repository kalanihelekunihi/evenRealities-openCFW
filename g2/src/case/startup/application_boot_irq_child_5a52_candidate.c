/* SPDX-License-Identifier: MIT
 * CASE 0x08005a52 IRQ child. The native 0x5a50 child is BX LR.
 */
#include <stdint.h>
/* Stock 0x08005A52 (case_mark_controller_ready) */
void case_irq_child_5a52(uint32_t state)
{
    uint32_t device=*(volatile uint32_t *)(uintptr_t)state;
    volatile uint32_t *status=(volatile uint32_t *)(uintptr_t)(device+0x50u);
    if((*status&4u)!=0u){
        volatile uint32_t *clear=(volatile uint32_t *)(uintptr_t)(device+0x5cu);
        *clear|=4u;
    }
    *(volatile uint8_t *)(uintptr_t)(state+41u)=1u;
}
