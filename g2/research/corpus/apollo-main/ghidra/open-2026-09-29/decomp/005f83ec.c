
undefined4 tt_glyphzone_done(int *param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  
  iVar1 = *param_1;
  if (iVar1 != 0) {
    ft_mem_free(iVar1,param_1[7]);
    param_1[7] = 0;
    ft_mem_free(iVar1,param_1[6]);
    param_1[6] = 0;
    ft_mem_free(iVar1,param_1[4]);
    param_1[4] = 0;
    ft_mem_free(iVar1,param_1[3]);
    param_1[3] = 0;
    ft_mem_free(iVar1,param_1[5]);
    param_1[5] = 0;
    *(undefined2 *)(param_1 + 2) = 0;
    *(short *)(param_1 + 1) = (short)param_1[2];
    *(undefined2 *)((int)param_1 + 10) = 0;
    *(undefined2 *)((int)param_1 + 6) = *(undefined2 *)((int)param_1 + 10);
    *param_1 = 0;
  }
  return param_4;
}

