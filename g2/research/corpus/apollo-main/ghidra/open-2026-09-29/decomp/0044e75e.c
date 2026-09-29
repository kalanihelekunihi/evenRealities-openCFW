
undefined4 FUN_0044e75e(undefined4 param_1,int *param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  
  iVar1 = FUN_00450566(param_1,DAT_0044eb1c);
  if (iVar1 == 0) {
    iVar1 = FUN_0044e486(param_1);
  }
  else {
    iVar1 = -*(int *)(iVar1 + 0x2c);
  }
  *param_2 = iVar1;
  iVar1 = FUN_00450566(param_1,DAT_0044eb20);
  if (iVar1 == 0) {
    iVar1 = FUN_0044e498(param_1);
  }
  else {
    iVar1 = -*(int *)(iVar1 + 0x2c);
  }
  param_2[1] = iVar1;
  return param_4;
}

