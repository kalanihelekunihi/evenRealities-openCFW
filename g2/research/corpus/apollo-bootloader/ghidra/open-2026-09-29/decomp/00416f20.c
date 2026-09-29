
undefined8 FUN_00416f20(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  
  iVar1 = FUN_00416a2c(param_1);
  if (iVar1 != 0) {
    FUN_00415734(DAT_00417304,DAT_00417200,0x2a0);
  }
  iVar1 = FUN_004169fc(param_2);
  *(int *)(param_1 + 4) = *DAT_00417308 + iVar1 + *(int *)(param_1 + 4);
  FUN_00416b14(param_1);
  return CONCAT44(param_4,param_1);
}

