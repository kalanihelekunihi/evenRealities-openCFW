
void hal_i2c_irq_enable(ushort param_1)

{
  if (-1 < (short)param_1) {
    *(int *)(DAT_0050475c + ((uint)(int)(short)param_1 >> 5) * 4) = 1 << (param_1 & 0x1f);
  }
  return;
}

