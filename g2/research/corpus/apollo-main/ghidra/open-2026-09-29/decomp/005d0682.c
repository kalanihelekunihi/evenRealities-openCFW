
int FUN_005d0682(int *param_1,undefined4 param_2,undefined4 param_3,int param_4)

{
  int iVar1;
  int iVar2;
  int iVar3;
  int local_18;
  
  iVar3 = param_1[8];
  iVar2 = *param_1;
  local_18 = param_4;
  if (iVar2 != 0) {
    iVar1 = ft_mem_alloc(iVar3,param_1[1],&local_18);
    *param_1 = iVar1;
    if (local_18 == 0) {
      FUN_00439be4(*param_1,iVar2,param_1[1]);
      FUN_005d0574(param_1,iVar2);
      param_1[2] = param_1[1];
      ft_mem_free(iVar3,iVar2);
    }
  }
  return local_18;
}

