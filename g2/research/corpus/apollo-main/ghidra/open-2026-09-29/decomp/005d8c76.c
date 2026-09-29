
undefined4
FUN_005d8c76(undefined4 *param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  
  iVar2 = param_1[2];
  for (iVar1 = param_1[1]; iVar1 != 0; iVar1 = iVar1 + -1) {
    FUN_005d8ba2(iVar2,param_2);
    iVar2 = iVar2 + 0x10;
  }
  ft_mem_free(param_2,param_1[2]);
  param_1[2] = 0;
  *param_1 = 0;
  param_1[1] = 0;
  return param_4;
}

