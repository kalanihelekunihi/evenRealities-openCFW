
undefined4
FUN_005d70c6(undefined4 *param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  ft_mem_free(param_2,param_1[6]);
  param_1[6] = 0;
  param_1[5] = 0;
  param_1[7] = 0;
  ft_mem_free(param_2,param_1[3]);
  param_1[3] = 0;
  ft_mem_free(param_2,param_1[2]);
  param_1[2] = 0;
  param_1[1] = 0;
  *param_1 = 0;
  param_1[4] = 0;
  return param_4;
}

