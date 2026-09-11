/* SPDX-License-Identifier: MIT */
#include <stdint.h>
#include <stddef.h>
/* Matches the reconstructed registration and dispatch interface. Startup must
 * zero this storage before interrupt registration or delivery. */
typedef int (*open_cfw_irq_handler)(int, void *);
struct open_cfw_irq_entry {
    open_cfw_irq_handler handler;
    void *private_data;
};
struct open_cfw_irq_entry open_cfw_gx8002_irq_table[32];
uint32_t open_cfw_gx8002_irq_saved_enable[2];
_Static_assert(sizeof(struct open_cfw_irq_entry)==8,"IRQ entry width");
_Static_assert(offsetof(struct open_cfw_irq_entry,private_data)==4,"IRQ private offset");
_Static_assert(sizeof(open_cfw_gx8002_irq_table)==256,"IRQ table extent");
