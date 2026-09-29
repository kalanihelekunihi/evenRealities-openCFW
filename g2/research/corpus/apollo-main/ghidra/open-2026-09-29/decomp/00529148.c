
undefined8 ft_mem_alloc(undefined4 param_1,int param_2,int *param_3,int param_4)

{
  undefined4 uVar1;
  int local_18;
  
  local_18 = param_4;
  uVar1 = ft_mem_qalloc(param_1,param_2,&local_18);
  if ((local_18 == 0) && (0 < param_2)) {
    FUN_0043c0e4(uVar1,param_2,0);
  }
  *param_3 = local_18;
  return CONCAT44(local_18,uVar1);
}

