
int FT_Lookup_Renderer(int param_1,int param_2,int *param_3)

{
  int iVar1;
  int iVar2;
  
  if (param_1 != 0) {
    iVar1 = *(int *)(param_1 + 0x94);
    if (param_3 != (int *)0x0) {
      if (*param_3 != 0) {
        iVar1 = *(int *)(*param_3 + 4);
      }
      *param_3 = 0;
    }
    for (; iVar1 != 0; iVar1 = *(int *)(iVar1 + 4)) {
      iVar2 = *(int *)(iVar1 + 8);
      if (*(int *)(iVar2 + 0x10) == param_2) {
        if (param_3 == (int *)0x0) {
          return iVar2;
        }
        *param_3 = iVar1;
        return iVar2;
      }
    }
  }
  return 0;
}

