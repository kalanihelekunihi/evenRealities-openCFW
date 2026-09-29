
undefined4 FUN_0041e266(char param_1)

{
  uint *puVar1;
  undefined4 uVar2;
  uint uVar3;
  uint uVar4;
  uint uVar5;
  bool bVar6;
  
  if ((*DAT_0041e444 & 0x300) == 0) {
    *DAT_0041e454 =
         (*DAT_0041e450 & 7) << 7 | (DAT_0041e450[1] & 7) << 4 | (DAT_0041e450[2] & 7) << 1 | 1;
    puVar1 = DAT_0041e448;
    if (-1 < (int)(*DAT_0041e448 << 0xf)) {
      *DAT_0041e458 = 0;
      DataSynchronizationBarrier(0xf);
      uVar4 = *DAT_0041e45c;
      uVar3 = (uVar4 & 0xfffffff) >> 0xd;
      do {
        uVar5 = (uVar4 & 0x1fff) >> 3;
        do {
          *DAT_0041e460 = (uVar3 & 0x1ff) << 5 | uVar5 << 0x1e;
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
      *DAT_0041e458 = 0;
      DataSynchronizationBarrier(0xf);
      uVar4 = *DAT_0041e45c;
      uVar3 = (uVar4 & 0xfffffff) >> 0xd;
      do {
        uVar5 = (uVar4 & 0x1fff) >> 3;
        do {
          *DAT_0041e464 = (uVar3 & 0x1ff) << 5 | uVar5 << 0x1e;
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

