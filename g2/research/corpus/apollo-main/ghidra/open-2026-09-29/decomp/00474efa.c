
bool FUN_00474efa(void)

{
  bool bVar1;
  
  bVar1 = (*DAT_00475194 & 0x300) == 0;
  if (bVar1) {
    DataSynchronizationBarrier(0xf);
    InstructionSynchronizationBarrier(0xf);
    *DAT_00475198 = *DAT_00475198 & 0xfffdffff;
    *DAT_0047519c = 0;
    DataSynchronizationBarrier(0xf);
    InstructionSynchronizationBarrier(0xf);
  }
  return !bVar1;
}

