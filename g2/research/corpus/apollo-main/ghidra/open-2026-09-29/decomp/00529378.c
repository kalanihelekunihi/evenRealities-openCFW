
undefined4 FT_List_Finalize(int *param_1,code *param_2,int param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  
  if ((param_1 != (int *)0x0) && (param_3 != 0)) {
    iVar1 = *param_1;
    while (iVar1 != 0) {
      iVar2 = *(int *)(iVar1 + 4);
      if (param_2 != (code *)0x0) {
        (*param_2)(param_3,*(undefined4 *)(iVar1 + 8),param_4);
      }
      ft_mem_free(param_3,iVar1);
      iVar1 = iVar2;
    }
    *param_1 = 0;
    param_1[1] = 0;
  }
  return param_4;
}

