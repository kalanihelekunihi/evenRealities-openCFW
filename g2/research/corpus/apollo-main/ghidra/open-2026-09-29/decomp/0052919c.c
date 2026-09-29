
undefined8
ft_mem_realloc(undefined4 param_1,int param_2,int param_3,int param_4,undefined4 param_5,
              int *param_6)

{
  int iVar1;
  int local_18;
  
  local_18 = 0;
  iVar1 = ft_mem_qrealloc(param_1,param_2,param_3,param_4,param_5,&local_18);
  if ((local_18 == 0) && (param_3 < param_4)) {
    FUN_0043c0e4(param_2 * param_3 + iVar1,param_2 * (param_4 - param_3),0);
  }
  *param_6 = local_18;
  return CONCAT44(param_5,iVar1);
}

