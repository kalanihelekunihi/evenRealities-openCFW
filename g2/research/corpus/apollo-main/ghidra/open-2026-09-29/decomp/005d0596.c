
undefined8 FUN_005d0596(int *param_1,int param_2,int param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  int iVar3;
  int local_20;
  undefined4 uStack_1c;
  
  iVar3 = param_1[8];
  iVar2 = *param_1;
  local_20 = param_3;
  uStack_1c = param_4;
  iVar1 = ft_mem_alloc(iVar3,param_2,&local_20);
  *param_1 = iVar1;
  if (local_20 == 0) {
    if (iVar2 != 0) {
      FUN_00439be4(*param_1,iVar2,param_1[2]);
      FUN_005d0574(param_1,iVar2);
      ft_mem_free(iVar3,iVar2);
    }
    param_1[2] = param_2;
    iVar1 = 0;
  }
  else {
    *param_1 = iVar2;
    iVar1 = local_20;
  }
  return CONCAT44(local_20,iVar1);
}

