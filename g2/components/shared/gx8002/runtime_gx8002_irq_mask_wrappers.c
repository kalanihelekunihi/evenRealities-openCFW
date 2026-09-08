/* SPDX-License-Identifier: MIT */
/* Reconstructed GX8002 public IRQ wrappers. Keep these distinct call entries
 * and the already-qualified signed internal IRQ interface. */
extern void open_cfw_gx8002_irq_enable(int irq);
extern void open_cfw_gx8002_irq_disable(int irq);
void gx_mask_irq(unsigned int irq)
{
    open_cfw_gx8002_irq_disable((int)irq);
}
void gx_unmask_irq(unsigned int irq)
{
    open_cfw_gx8002_irq_enable((int)irq);
}
