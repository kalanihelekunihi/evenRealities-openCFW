
int Update_Max(undefined4 param_1,uint *param_2,int param_3,undefined4 *param_4,uint param_5)

{
  undefined4 uVar1;
  int local_18;
  undefined4 *puStack_14;
  
  if (*param_2 < param_5) {
    local_18 = param_3;
    puStack_14 = param_4;
    uVar1 = ft_mem_realloc(param_1,1,param_3 * *param_2,param_3 * param_5,*param_4,&local_18);
    *param_4 = uVar1;
    if (local_18 != 0) {
      return local_18;
    }
    *param_2 = param_5;
  }
  return 0;
}

