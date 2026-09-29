
undefined4 FUN_0041e1e8(void)

{
  uint *puVar1;
  undefined4 uVar2;
  
  puVar1 = DAT_0041e448;
  if ((*DAT_0041e444 & 0x300) == 0) {
    if (-1 < (int)(*DAT_0041e448 << 0xe)) {
      DataSynchronizationBarrier(0xf);
      InstructionSynchronizationBarrier(0xf);
      *DAT_0041e44c = 0;
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

