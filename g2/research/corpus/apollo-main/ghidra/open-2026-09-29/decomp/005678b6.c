
void FUN_005678b6(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4,
                 code *param_5)

{
  int iVar1;
  
  iVar1 = (*param_5)(param_2,param_1);
  if (iVar1 < 0) {
    FUN_005677a8(param_1,param_2,param_4);
  }
  iVar1 = (*param_5)(param_3,param_2);
  if (iVar1 < 0) {
    FUN_005677a8(param_2,param_3,param_4);
  }
  iVar1 = (*param_5)(param_2,param_1);
  if (iVar1 < 0) {
    FUN_005677a8(param_1,param_2,param_4);
    return;
  }
  return;
}

