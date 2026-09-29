
undefined4 FUN_00482d22(int param_1,int param_2,int param_3,undefined4 param_4)

{
  int iVar1;
  
  if (param_2 != param_3) {
    if (param_3 == 0) {
      iVar1 = FUN_00482ce4(param_1);
    }
    else {
      iVar1 = FUN_00482cfa(param_1,param_3);
    }
    if (param_2 != iVar1) {
      FUN_00482c0e(param_1,param_2);
      FUN_00482dc2(param_1,iVar1,param_2);
      FUN_00482dae(param_1,param_2,iVar1);
      FUN_00482dae(param_1,param_3,param_2);
      FUN_00482dc2(param_1,param_2,param_3);
      if (param_3 == 0) {
        *(int *)(param_1 + 8) = param_2;
      }
      if (iVar1 == 0) {
        *(int *)(param_1 + 4) = param_2;
      }
    }
  }
  return param_4;
}

