
undefined8 FUN_00482b56(int *param_1,int param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 uVar2;
  
  if ((param_1 == (int *)0x0) || (param_2 == 0)) {
    iVar1 = 0;
  }
  else {
    iVar1 = FUN_00482cd8(param_1);
    if (iVar1 == param_2) {
      iVar1 = FUN_00482b12(param_1);
      if (iVar1 == 0) {
        iVar1 = 0;
      }
    }
    else {
      iVar1 = FUN_0044f718(*param_1 + 8);
      if (iVar1 == 0) {
        iVar1 = 0;
      }
      else {
        uVar2 = FUN_00482cfa(param_1,param_2);
        FUN_00482dc2(param_1,uVar2,iVar1);
        FUN_00482dae(param_1,iVar1,uVar2);
        FUN_00482dae(param_1,param_2,iVar1);
        FUN_00482dc2(param_1,iVar1,param_2);
      }
    }
  }
  return CONCAT44(param_4,iVar1);
}

