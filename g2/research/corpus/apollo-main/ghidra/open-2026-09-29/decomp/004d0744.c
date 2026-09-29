
void FUN_004d0744(undefined4 param_1,uint param_2,undefined4 param_3)

{
  int iVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  uint uVar5;
  uint uVar6;
  
  iVar1 = FUN_004cff42(param_3,4);
  iVar2 = FUN_004cff42(param_2 + iVar1 + 0x10,param_2);
  if ((iVar1 == 0) || (param_2 < 5)) {
    iVar2 = iVar1;
  }
  iVar2 = FUN_004d0484(param_1,iVar2);
  if (*DAT_004d0964 + *DAT_004d0854 != 0x10) {
    FUN_004d09b4(DAT_004d09a8,DAT_004d09a0,0x47d);
  }
  if (iVar2 != 0) {
    iVar3 = FUN_004cfe10(iVar2);
    iVar4 = FUN_004cff18(iVar3,param_2);
    uVar5 = iVar4 - iVar3;
    if ((uVar5 != 0) && (uVar5 < 0x10)) {
      uVar6 = 0x10 - uVar5;
      if (0x10 - uVar5 <= param_2) {
        uVar6 = param_2;
      }
      iVar4 = FUN_004cff18(uVar6 + iVar4,param_2);
      uVar5 = iVar4 - iVar3;
    }
    if (uVar5 != 0) {
      if (uVar5 < 0x10) {
        FUN_004d09b4(DAT_004d09ac,DAT_004d09a0,0x495);
      }
      iVar2 = FUN_004d0444(param_1,iVar2,uVar5);
    }
  }
  FUN_004d04e6(param_1,iVar2,iVar1);
  return;
}

