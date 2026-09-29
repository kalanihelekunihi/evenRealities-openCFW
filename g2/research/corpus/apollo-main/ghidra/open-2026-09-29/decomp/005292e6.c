
int FT_List_Find(int *param_1,int param_2)

{
  int iVar1;
  
  if (param_1 != (int *)0x0) {
    for (iVar1 = *param_1; iVar1 != 0; iVar1 = *(int *)(iVar1 + 4)) {
      if (*(int *)(iVar1 + 8) == param_2) {
        return iVar1;
      }
    }
  }
  return 0;
}

