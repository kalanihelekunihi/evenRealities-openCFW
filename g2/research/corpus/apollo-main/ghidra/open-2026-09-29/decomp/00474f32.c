
undefined4 FUN_00474f32(char param_1)

{
  uint *puVar1;
  undefined4 uVar2;
  uint uVar3;
  uint uVar4;
  uint uVar5;
  bool bVar6;
  
  if ((*DAT_00475194 & 0x300) == 0) {
    *DAT_004751a4 =
         (*DAT_004751a0 & 7) << 7 | (DAT_004751a0[1] & 7) << 4 | (DAT_004751a0[2] & 7) << 1 | 1;
    puVar1 = DAT_00475198;
    if (-1 < (int)(*DAT_00475198 << 0xf)) {
      *DAT_004751a8 = 0;
      DataSynchronizationBarrier(0xf);
      uVar4 = *DAT_004751ac;
      uVar3 = (uVar4 & 0xfffffff) >> 0xd;
      do {
        uVar5 = (uVar4 & 0x1fff) >> 3;
        do {
          *DAT_004751b0 = (uVar3 & 0x1ff) << 5 | uVar5 << 0x1e;
          bVar6 = uVar5 != 0;
          uVar5 = uVar5 - 1;
        } while (bVar6);
        bVar6 = uVar3 != 0;
        uVar3 = uVar3 - 1;
      } while (bVar6);
      DataSynchronizationBarrier(0xf);
      *puVar1 = *puVar1 | 0x10000;
      DataSynchronizationBarrier(0xf);
      InstructionSynchronizationBarrier(0xf);
    }
    if (param_1 != '\0') {
      *DAT_004751a8 = 0;
      DataSynchronizationBarrier(0xf);
      uVar4 = *DAT_004751ac;
      uVar3 = (uVar4 & 0xfffffff) >> 0xd;
      do {
        uVar5 = (uVar4 & 0x1fff) >> 3;
        do {
          *DAT_004751b4 = (uVar3 & 0x1ff) << 5 | uVar5 << 0x1e;
          bVar6 = uVar5 != 0;
          uVar5 = uVar5 - 1;
        } while (bVar6);
        bVar6 = uVar3 != 0;
        uVar3 = uVar3 - 1;
      } while (bVar6);
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

