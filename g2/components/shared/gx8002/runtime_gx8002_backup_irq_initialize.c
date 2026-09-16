/* SPDX-License-Identifier: MIT */
/* Backup gx_irq_init restores the two saved enable banks, in order.
 * This is the same operation as runtime_gx8002_irq.c's restore_enabled;
 * explicit register accesses preserve the recovered backup access sequence. */
#include <stdint.h>
extern uint32_t open_cfw_gx8002_irq_saved_enable[2];
void gx_irq_init(void)
{
    volatile uint32_t *enable = (volatile uint32_t *)(uintptr_t)0xe000e100;
    enable[0] = open_cfw_gx8002_irq_saved_enable[0];
    enable[1] = open_cfw_gx8002_irq_saved_enable[1];
}
