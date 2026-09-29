
undefined8 FUN_00482bca(int *param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  
  iVar1 = FUN_0044f718(*param_1 + 8);
  if (iVar1 != 0) {
    FUN_00482dc2(param_1,iVar1,0);
    FUN_00482dae(param_1,iVar1,param_1[2]);
    if (param_1[2] != 0) {
      FUN_00482dc2(param_1,param_1[2],iVar1);
    }
    param_1[2] = iVar1;
    if (param_1[1] == 0) {
      param_1[1] = iVar1;
    }
  }
  return CONCAT44(param_4,iVar1);
}

