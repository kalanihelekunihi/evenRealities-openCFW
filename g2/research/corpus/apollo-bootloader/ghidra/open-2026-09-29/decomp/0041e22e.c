
bool FUN_0041e22e(void)

{
  bool bVar1;
  
  bVar1 = (*DAT_0041e444 & 0x300) == 0;
  if (bVar1) {
    DataSynchronizationBarrier(0xf);
    InstructionSynchronizationBarrier(0xf);
    *DAT_0041e448 = *DAT_0041e448 & 0xfffdffff;
    *DAT_0041e44c = 0;
    DataSynchronizationBarrier(0xf);
    InstructionSynchronizationBarrier(0xf);
  }
  return !bVar1;
}

