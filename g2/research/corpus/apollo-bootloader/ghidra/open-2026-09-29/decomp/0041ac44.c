
void FUN_0041ac44(void)

{
  *DAT_0041b0c0 = *DAT_0041b0c0 | 0xf00000;
  DataSynchronizationBarrier(0xf);
  InstructionSynchronizationBarrier(0xf);
  return;
}

