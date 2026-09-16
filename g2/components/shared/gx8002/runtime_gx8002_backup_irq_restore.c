/* SPDX-License-Identifier: MIT */
#include <stdint.h>

/* Two saved interrupt-enable words, read in order by stock entry 0x3d16c.
 * This definition supplies relocatable storage; its other readers/writers
 * must be reconstructed before moving it from its original BSS location.
 */
__attribute__((section(".bss.backup_irq_saved"), aligned(4)))
volatile uint32_t open_cfw_gx8002_backup_irq_saved[2];

void open_cfw_gx8002_backup_irq_restore(void)
{
    volatile uint32_t *enable = (volatile uint32_t *)(uintptr_t)0xe000e100u;
    enable[0] = open_cfw_gx8002_backup_irq_saved[0];
    enable[1] = open_cfw_gx8002_backup_irq_saved[1];
}
