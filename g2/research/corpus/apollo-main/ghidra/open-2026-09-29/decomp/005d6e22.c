
undefined4
FUN_005d6e22(undefined4 *param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 uVar1;
  
  if (param_1 != (undefined4 *)0x0) {
    uVar1 = *param_1;
    ft_mem_free(uVar1,param_1[2]);
    param_1[2] = 0;
    ft_mem_free(uVar1,param_1);
  }
  return param_4;
}

