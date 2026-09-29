
undefined4 FUN_00417290(undefined4 param_1,int param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 uVar1;
  int iVar2;
  
  if (param_2 != 0) {
    uVar1 = FUN_00416a90(param_2);
    iVar2 = FUN_00416a40(uVar1);
    if (iVar2 != 0) {
      FUN_00415734(DAT_00417338,DAT_00417330,0x4a4);
    }
    FUN_00416b22(uVar1);
    uVar1 = FUN_00416f62(param_1,uVar1);
    uVar1 = FUN_00416fc6(param_1,uVar1);
    FUN_00416e26(param_1,uVar1);
  }
  return param_4;
}

