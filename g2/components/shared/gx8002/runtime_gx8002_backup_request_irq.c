/* SPDX-License-Identifier: MIT */
#include <stdint.h>
#include <stddef.h>
typedef int (*backup_irq_handler)(int, void *);
struct backup_irq_entry { backup_irq_handler handler; void *private_data; };
extern struct backup_irq_entry open_cfw_gx8002_backup_irq_table[32];
_Static_assert(sizeof(struct backup_irq_entry) == 8, "IRQ entry stride");
_Static_assert(offsetof(struct backup_irq_entry, private_data) == 4, "IRQ context offset");
/* Backup 0x3d184: registration precedes the write-one enable operation. */
void open_cfw_gx8002_backup_request_irq(int irq, backup_irq_handler handler, void *private_data)
{
    if ((uint32_t)irq >= 32 || !handler)
        return;
    open_cfw_gx8002_backup_irq_table[irq].handler = handler;
    open_cfw_gx8002_backup_irq_table[irq].private_data = private_data;
    *(volatile uint32_t *)(uintptr_t)0xe000e100 = 1u << (uint32_t)irq;
}
