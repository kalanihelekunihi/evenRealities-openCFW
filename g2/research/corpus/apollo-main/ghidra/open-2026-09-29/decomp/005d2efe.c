
undefined4
FUN_005d2efe(undefined4 *param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 uVar1;
  
  if (param_1 != (undefined4 *)0x0) {
    uVar1 = *param_1;
    ft_mem_free(uVar1,param_1[0x1b]);
    param_1[0x1b] = 0;
    ft_mem_free(uVar1,param_1[0x1d]);
    param_1[0x1d] = 0;
  }
  return param_4;
}

