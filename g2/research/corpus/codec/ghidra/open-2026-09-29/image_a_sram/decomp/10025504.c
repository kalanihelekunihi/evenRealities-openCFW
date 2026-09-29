
void gx_unmask_irq(void)

{
  csi_vic_enable_irq();
  return;
}

