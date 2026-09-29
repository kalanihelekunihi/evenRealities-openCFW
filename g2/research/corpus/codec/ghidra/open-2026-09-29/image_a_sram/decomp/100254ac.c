
void csi_vic_enable_irq(uint param_1)

{
  *(int *)(DAT_100254c4 + ((param_1 & 0x3f) >> 5) * 4) = 1 << (param_1 & 0x1f);
  return;
}

