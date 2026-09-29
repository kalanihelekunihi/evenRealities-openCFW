
undefined4
FUN_005d7742(undefined4 *param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 uVar1;
  
  uVar1 = param_1[4];
  FUN_005d70c6(param_1 + 0x11,uVar1);
  FUN_005d70c6(param_1 + 7,uVar1);
  ft_mem_free(uVar1,param_1[2]);
  param_1[2] = 0;
  ft_mem_free(uVar1,param_1[3]);
  param_1[3] = 0;
  *param_1 = 0;
  param_1[1] = 0;
  param_1[4] = 0;
  return param_4;
}

