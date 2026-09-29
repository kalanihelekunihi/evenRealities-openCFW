
undefined8 ft_mem_dup(undefined4 param_1,int param_2,int param_3,int *param_4)

{
  undefined4 uVar1;
  int local_20;
  int *piStack_1c;
  
  local_20 = param_3;
  piStack_1c = param_4;
  uVar1 = ft_mem_qalloc(param_1,param_3,&local_20);
  if ((local_20 == 0) && (param_2 != 0)) {
    FUN_00439be4(uVar1,param_2,param_3);
  }
  *param_4 = local_20;
  return CONCAT44(local_20,uVar1);
}

