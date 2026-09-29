
undefined4 FUN_00474eb4(void)

{
  uint *puVar1;
  undefined4 uVar2;
  
  puVar1 = DAT_00475198;
  if ((*DAT_00475194 & 0x300) == 0) {
    if (-1 < (int)(*DAT_00475198 << 0xe)) {
      DataSynchronizationBarrier(0xf);
      InstructionSynchronizationBarrier(0xf);
      *DAT_0047519c = 0;
      DataSynchronizationBarrier(0xf);
      InstructionSynchronizationBarrier(0xf);
      *puVar1 = *puVar1 | 0x20000;
      DataSynchronizationBarrier(0xf);
      InstructionSynchronizationBarrier(0xf);
    }
    uVar2 = 0;
  }
  else {
    uVar2 = 1;
  }
  return uVar2;
}

