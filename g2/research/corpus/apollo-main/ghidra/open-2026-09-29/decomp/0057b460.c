
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __NVIC_DisableIRQ(ushort param_1)

{
  if (-1 < (short)param_1) {
    *(int *)(_DAT_0057b6ac + ((uint)(int)(short)param_1 >> 5) * 4) = 1 << (param_1 & 0x1f);
    DataSynchronizationBarrier(0xf);
    InstructionSynchronizationBarrier(0xf);
  }
  return;
}

