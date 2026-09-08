/* SPDX-License-Identifier: MIT */
/* VIC access comes from the pinned Apache-2.0 C-SKY CSI implementation. */
#include <core_ck804.h>

typedef int (*open_cfw_irq_handler)(int, void *);
struct open_cfw_irq_entry {
    open_cfw_irq_handler handler;
    void *private_data;
};
extern struct open_cfw_irq_entry open_cfw_gx8002_irq_table[32];
extern uint32_t open_cfw_gx8002_irq_saved_enable[2];

uint32_t open_cfw_gx8002_irq_save(void)
{
    return csi_irq_save();
}

void open_cfw_gx8002_irq_restore(uint32_t state)
{
    csi_irq_restore(state);
}

__attribute__((noinline)) void open_cfw_gx8002_irq_enable(int irq)
{
    csi_vic_enable_irq(irq);
}

__attribute__((noinline)) void open_cfw_gx8002_irq_disable(int irq)
{
    csi_vic_disable_irq(irq);
}

/* Stock saves both banks, but disables only the first 32 interrupt lines. */
void open_cfw_gx8002_irq_restore_enabled(void)
{
    VIC->ISER[0] = open_cfw_gx8002_irq_saved_enable[0];
    VIC->ISER[1] = open_cfw_gx8002_irq_saved_enable[1];
}

__attribute__((noinline)) void open_cfw_gx8002_irq_save_disable(void)
{
    open_cfw_gx8002_irq_saved_enable[0] = VIC->ISER[0];
    open_cfw_gx8002_irq_saved_enable[1] = VIC->ISER[1];
    for (int irq = 0; irq < 32; ++irq)
        open_cfw_gx8002_irq_disable(irq);
}

void open_cfw_gx8002_request_irq(int irq, open_cfw_irq_handler handler,
                               void *private_data)
{
    if ((uint32_t)irq >= 32 || !handler)
        return;
    open_cfw_gx8002_irq_table[irq].handler = handler;
    open_cfw_gx8002_irq_table[irq].private_data = private_data;
    open_cfw_gx8002_irq_enable(irq);
}
