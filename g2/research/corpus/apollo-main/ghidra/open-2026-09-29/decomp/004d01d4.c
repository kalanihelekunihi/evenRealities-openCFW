
undefined8 FUN_004d01d4(undefined4 param_1,int param_2,undefined4 param_3,undefined4 param_4)

{
  int *piVar1;
  undefined4 uVar2;
  int iVar3;
  undefined4 uVar4;
  int iVar5;
  uint uVar6;
  int iVar7;
  
  uVar2 = FUN_004cfe10(param_1);
  piVar1 = DAT_004d06b0;
  uVar2 = FUN_004cfe1a(uVar2,param_2 - *DAT_004d06b0);
  iVar3 = FUN_004cfd70(param_1);
  iVar7 = (iVar3 - param_2) - *piVar1;
  iVar3 = FUN_004cfe10(uVar2);
  uVar4 = FUN_004cfe10(uVar2);
  iVar5 = FUN_004cff18(uVar4,4);
  if (iVar3 != iVar5) {
    FUN_004d09b4(DAT_004d0954,DAT_004d06ac,0x291);
  }
  iVar3 = FUN_004cfd70(param_1);
  if (iVar3 != *piVar1 + param_2 + iVar7) {
    FUN_004d09b4(DAT_004d0958,DAT_004d06ac,0x293);
  }
  FUN_004cfd84(uVar2,iVar7);
  uVar6 = FUN_004cfd70(uVar2);
  if (uVar6 < *DAT_004d0854) {
    FUN_004d09b4(DAT_004d095c,DAT_004d06ac,0x295);
  }
  FUN_004cfd84(param_1,param_2);
  FUN_004cfe96(uVar2);
  return CONCAT44(param_4,uVar2);
}

