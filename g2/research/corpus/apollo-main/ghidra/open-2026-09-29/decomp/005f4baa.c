
int Round_Super_45(int param_1,int param_2,int param_3)

{
  int iVar1;
  
  if (param_2 < 0) {
    iVar1 = -*(int *)(param_1 + 0x1e4) -
            *(int *)(param_1 + 0x1e0) *
            (((param_3 + (*(int *)(param_1 + 0x1e8) - *(int *)(param_1 + 0x1e4))) - param_2) /
            *(int *)(param_1 + 0x1e0));
    if (0 < iVar1) {
      iVar1 = -*(int *)(param_1 + 0x1e4);
    }
  }
  else {
    iVar1 = *(int *)(param_1 + 0x1e4) +
            *(int *)(param_1 + 0x1e0) *
            ((param_3 + ((*(int *)(param_1 + 0x1e8) + param_2) - *(int *)(param_1 + 0x1e4))) /
            *(int *)(param_1 + 0x1e0));
    if (iVar1 < 0) {
      iVar1 = *(int *)(param_1 + 0x1e4);
    }
  }
  return iVar1;
}

