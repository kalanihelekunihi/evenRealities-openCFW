
undefined8 FUN_0041f440(uint param_1,uint param_2,uint param_3)

{
  bool bVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  undefined4 uVar5;
  undefined4 uVar6;
  uint local_20;
  
  uVar6 = 0;
  iVar3 = FUN_0041f424();
  iVar4 = iVar3;
  if (param_1 < 8) {
    while ((iVar2 = DAT_0041f4f0, iVar4 == *(int *)(DAT_0041f4f0 + param_1 * 4) ||
           (iVar4 == *(int *)(DAT_0041f4f0 + param_1 * 4) + 1))) {
      iVar4 = FUN_0041f424();
    }
    local_20 = critical_save();
    iVar4 = FUN_0041f424();
    if ((iVar4 - iVar3) + 3U < param_2) {
      iVar4 = iVar3 + (param_2 - iVar4) + -3;
    }
    else {
      iVar4 = 1;
      uVar6 = 0x8000000;
    }
    *(int *)(DAT_0041f4dc + param_1 * 4) = iVar4;
    uVar5 = FUN_0041f424();
    *(undefined4 *)(iVar2 + param_1 * 4) = uVar5;
    bVar1 = (bool)isCurrentModePrivileged();
    if (bVar1) {
      enableIRQinterrupts((local_20 & 1) == 1);
    }
  }
  else {
    uVar6 = 5;
    local_20 = param_3;
  }
  return CONCAT44(local_20,uVar6);
}

