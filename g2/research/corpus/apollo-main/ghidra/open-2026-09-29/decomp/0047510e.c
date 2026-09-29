
undefined4 FUN_0047510e(uint *param_1)

{
  uint uVar1;
  int iVar2;
  uint uVar3;
  uint uVar4;
  bool bVar5;
  
  if (*DAT_00475198 << 0xf < 0) {
    if (param_1 == (uint *)0x0) {
      *DAT_004751a8 = 0;
      DataSynchronizationBarrier(0xf);
      uVar1 = *DAT_004751ac;
      uVar3 = (uVar1 & 0xfffffff) >> 0xd;
      do {
        uVar4 = (uVar1 & 0x1fff) >> 3;
        do {
          *DAT_004751b4 = (uVar3 & 0x1ff) << 5 | uVar4 << 0x1e;
          bVar5 = uVar4 != 0;
          uVar4 = uVar4 - 1;
        } while (bVar5);
        bVar5 = uVar3 != 0;
        uVar3 = uVar3 - 1;
      } while (bVar5);
      DataSynchronizationBarrier(0xf);
      InstructionSynchronizationBarrier(0xf);
    }
    else {
      uVar3 = *param_1;
      if (0 < (int)param_1[1]) {
        iVar2 = (uVar3 & 0x1f) + param_1[1];
        DataSynchronizationBarrier(0xf);
        do {
          *DAT_004751c4 = uVar3;
          uVar3 = uVar3 + 0x20;
          iVar2 = iVar2 + -0x20;
        } while (0 < iVar2);
        DataSynchronizationBarrier(0xf);
        InstructionSynchronizationBarrier(0xf);
      }
    }
  }
  else {
    DataSynchronizationBarrier(0xf);
    InstructionSynchronizationBarrier(0xf);
  }
  return 0;
}

