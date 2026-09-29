
undefined4 cff_charset_done(undefined4 *param_1,int param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 uVar1;
  
  uVar1 = *(undefined4 *)(param_2 + 0x1c);
  cff_charset_free_cids(param_1,uVar1);
  ft_mem_free(uVar1,param_1[2]);
  param_1[2] = 0;
  *param_1 = 0;
  param_1[1] = 0;
  return param_4;
}

