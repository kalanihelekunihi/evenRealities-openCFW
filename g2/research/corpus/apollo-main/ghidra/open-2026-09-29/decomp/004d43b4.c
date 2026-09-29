
void FUN_004d43b4(uint param_1)

{
  DataMemoryBarrier(0x1f);
  *DAT_004d4604 = param_1 | 1;
  *DAT_004d4608 = *DAT_004d4608 | 0x10000;
  DataSynchronizationBarrier(0xf);
  InstructionSynchronizationBarrier(0xf);
  return;
}

