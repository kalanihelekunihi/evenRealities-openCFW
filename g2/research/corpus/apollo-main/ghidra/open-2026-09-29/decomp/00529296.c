
void ft_mem_strdup(undefined4 param_1,int param_2,undefined4 param_3)

{
  int iVar1;
  
  if (param_2 == 0) {
    iVar1 = 0;
  }
  else {
    iVar1 = FUN_0044a43c(param_2);
    iVar1 = iVar1 + 1;
  }
  ft_mem_dup(param_1,param_2,iVar1,param_3);
  return;
}

