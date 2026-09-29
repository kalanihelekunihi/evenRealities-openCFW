
undefined4 FUN_00416fc6(undefined4 param_1,undefined4 param_2)

{
  int iVar1;
  int iVar2;
  
  iVar1 = FUN_00416ad0(param_2);
  if (iVar1 == 0) {
    FUN_00415734(DAT_00417314,DAT_00417200,0x2ba);
  }
  iVar2 = FUN_00416a40(iVar1);
  if (iVar2 != 0) {
    iVar2 = FUN_00416a2c(param_2);
    if (iVar2 != 0) {
      FUN_00415734(DAT_00417318,DAT_00417200,0x2be);
    }
    FUN_00416e04(param_1,iVar1);
    param_2 = FUN_00416f20(param_2,iVar1);
  }
  return param_2;
}

