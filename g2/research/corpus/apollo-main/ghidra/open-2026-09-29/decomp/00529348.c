
int FT_List_Iterate(int *param_1,code *param_2,undefined4 param_3)

{
  int iVar1;
  int iVar2;
  int iVar3;
  
  if ((param_1 == (int *)0x0) || (param_2 == (code *)0x0)) {
    iVar1 = 6;
  }
  else {
    iVar2 = *param_1;
    do {
      if (iVar2 == 0) {
        return 0;
      }
      iVar3 = *(int *)(iVar2 + 4);
      iVar1 = (*param_2)(iVar2,param_3);
      iVar2 = iVar3;
    } while (iVar1 == 0);
  }
  return iVar1;
}

