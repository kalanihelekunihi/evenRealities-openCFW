
undefined8 FUN_00482d02(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  
  iVar2 = 0;
  for (iVar1 = FUN_00482cd8(param_1); iVar1 != 0; iVar1 = FUN_00482cf0(param_1,iVar1)) {
    iVar2 = iVar2 + 1;
  }
  return CONCAT44(param_4,iVar2);
}

