/* SPDX-License-Identifier: MIT */
/* Reconstructed stock SNPU clock gate. Candidate pending ordered MMIO and
 * interrupt-state save/restore qualification. */
#include <stdint.h>
extern uint32_t open_cfw_gx8002_irq_save(void);
extern void open_cfw_gx8002_irq_restore(uint32_t state);
void gx_clock_set_module_snpu_enable(int enable)
{
    uint32_t state = open_cfw_gx8002_irq_save();
    volatile uint32_t *gate = (volatile uint32_t *)(uintptr_t)0xa0300018u;
    uint32_t value = *gate;
    if (enable)
        value &= ~UINT32_C(0x100);
    else
        value |= UINT32_C(0x100);
    *gate = value;
    open_cfw_gx8002_irq_restore(state);
}
