/* SPDX-License-Identifier: MIT */
/* Hardware IRQ entry; valid external vector numbers are 32..63. Stock does
 * not bounds-check the vector before indexing its 32 registration slots. */
#include <core_ck804.h>
typedef int (*open_cfw_irq_handler)(int, void *);
struct open_cfw_irq_entry {
    open_cfw_irq_handler handler;
    void *private_data;
};
extern struct open_cfw_irq_entry open_cfw_gx8002_irq_table[32];

#ifdef OPEN_CFW_GX8002_IRQ_BODY_ONLY
void open_cfw_gx8002_irq_dispatch_body(void)
#else
__attribute__((interrupt)) void open_cfw_gx8002_irq_dispatch(void)
#endif
{
    unsigned int irq = csi_vic_get_active_irq() - 32U;
    if (open_cfw_gx8002_irq_table[irq].handler)
        (void)open_cfw_gx8002_irq_table[irq].handler(
            (int)irq, open_cfw_gx8002_irq_table[irq].private_data);
}
