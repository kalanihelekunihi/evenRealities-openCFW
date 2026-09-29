
undefined8 FUN_00416e60(undefined4 param_1,int param_2,undefined4 param_3,undefined4 param_4)

{
  int *piVar1;
  undefined4 uVar2;
  int iVar3;
  undefined4 uVar4;
  int iVar5;
  uint uVar6;
  int iVar7;
  
  uVar2 = FUN_00416a9c(param_1);
  piVar1 = DAT_00417204;
  uVar2 = FUN_00416aa6(uVar2,param_2 - *DAT_00417204);
  iVar3 = FUN_004169fc(param_1);
  iVar7 = (iVar3 - param_2) - *piVar1;
  iVar3 = FUN_00416a9c(uVar2);
  uVar4 = FUN_00416a9c(uVar2);
  iVar5 = FUN_00416ba4(uVar4,4);
  if (iVar3 != iVar5) {
    FUN_00415734(DAT_004172f8,DAT_00417200,0x291);
  }
  iVar3 = FUN_004169fc(param_1);
  if (iVar3 != *piVar1 + param_2 + iVar7) {
    FUN_00415734(DAT_004172fc,DAT_00417200,0x293);
  }
  FUN_00416a10(uVar2,iVar7);
  uVar6 = FUN_004169fc(uVar2);
  if (uVar6 < *DAT_004172dc) {
    FUN_00415734(DAT_00417300,DAT_00417200,0x295);
  }
  FUN_00416a10(param_1,param_2);
  FUN_00416b22(uVar2);
  return CONCAT44(param_4,uVar2);
}

