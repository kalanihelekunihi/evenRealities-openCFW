
void case_clear_irq(uint param_1)

{
  if (-1 < (int)param_1) {
    *DAT_08005008 = 1 << (param_1 & 0x1f);
    DataSynchronizationBarrier(0xf);
    InstructionSynchronizationBarrier(0xf);
  }
  return;
}

