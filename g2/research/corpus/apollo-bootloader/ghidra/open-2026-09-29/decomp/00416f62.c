
undefined4 FUN_00416f62(undefined4 param_1,undefined4 param_2)

{
  int iVar1;
  int iVar2;
  
  iVar1 = FUN_00416a68(param_2);
  if (iVar1 != 0) {
    iVar1 = FUN_00416aaa(param_2);
    if (iVar1 == 0) {
      FUN_00415734(DAT_0041730c,DAT_00417200,0x2ad);
    }
    iVar2 = FUN_00416a40(iVar1);
    if (iVar2 == 0) {
      FUN_00415734(DAT_00417310,DAT_00417200,0x2ae);
    }
    FUN_00416e04(param_1,iVar1);
    param_2 = FUN_00416f20(iVar1,param_2);
  }
  return param_2;
}

