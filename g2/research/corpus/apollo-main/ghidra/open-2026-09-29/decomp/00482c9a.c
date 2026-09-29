
undefined4 FUN_00482c9a(undefined4 param_1,code *param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  
  iVar1 = FUN_00482cd8(param_1);
  while (iVar1 != 0) {
    iVar2 = FUN_00482cf0(param_1,iVar1);
    if (param_2 == (code *)0x0) {
      FUN_00482c0e(param_1,iVar1);
      FUN_0044f758(iVar1);
      iVar1 = iVar2;
    }
    else {
      (*param_2)(iVar1);
      iVar1 = iVar2;
    }
  }
  return param_4;
}

