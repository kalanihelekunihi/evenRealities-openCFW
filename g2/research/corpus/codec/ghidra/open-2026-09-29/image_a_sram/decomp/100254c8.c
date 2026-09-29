
void csi_vic_disable_irq(uint param_1)

{
  *(int *)(iRam100254e0 + (((param_1 & 0x3f) >> 5) + 0x20) * 4) = 1 << (param_1 & 0x1f);
  return;
}

