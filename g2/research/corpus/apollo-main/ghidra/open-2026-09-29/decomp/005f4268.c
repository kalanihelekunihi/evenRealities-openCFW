
undefined4
TT_Done_Context(undefined4 *param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 uVar1;
  
  uVar1 = param_1[2];
  *(undefined2 *)(param_1 + 0x6f) = 0;
  *(undefined2 *)((int)param_1 + 0x1be) = 0;
  ft_mem_free(uVar1,param_1[6]);
  param_1[6] = 0;
  param_1[5] = 0;
  ft_mem_free(uVar1,param_1[0x6e]);
  param_1[0x6e] = 0;
  param_1[0x6d] = 0;
  param_1[0x6c] = 0;
  ft_mem_free(uVar1,param_1[99]);
  param_1[99] = 0;
  param_1[0x62] = 0;
  param_1[1] = 0;
  *param_1 = 0;
  ft_mem_free(uVar1,param_1);
  return param_4;
}

