
int FUN_00544374(int param_1,int param_2,int param_3)

{
  int iVar1;
  
  if (*(int *)(param_2 + 0xc) == -1) {
    iVar1 = *(int *)(param_1 + 0xc);
  }
  else {
    iVar1 = *(int *)(param_1 + 0xc) * *(int *)(param_2 + 0xc);
  }
  if (*(uint *)(param_1 + 0x10) < (uint)(iVar1 + param_3)) {
    iVar1 = -1;
  }
  else if ((uint)(iVar1 + *(int *)(param_2 + 4)) < *(uint *)(param_1 + 0x10)) {
    iVar1 = iVar1 + *(int *)(param_2 + 4);
  }
  else {
    iVar1 = 0;
  }
  return iVar1;
}

