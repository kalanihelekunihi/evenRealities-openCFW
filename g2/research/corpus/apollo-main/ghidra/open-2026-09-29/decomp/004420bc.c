
void FUN_004420bc(void)

{
  *DAT_0044221c = 0x10000000;
  DataSynchronizationBarrier(0xf);
  InstructionSynchronizationBarrier(0xf);
  return;
}

