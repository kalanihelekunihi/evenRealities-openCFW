
void FT_List_Remove(int *param_1,int *param_2)

{
  int *piVar1;
  int iVar2;
  
  if ((param_1 != (int *)0x0) && (param_2 != (int *)0x0)) {
    iVar2 = *param_2;
    piVar1 = (int *)param_2[1];
    if (iVar2 == 0) {
      *param_1 = (int)piVar1;
    }
    else {
      *(int **)(iVar2 + 4) = piVar1;
    }
    if (piVar1 == (int *)0x0) {
      param_1[1] = iVar2;
    }
    else {
      *piVar1 = iVar2;
    }
  }
  return;
}

