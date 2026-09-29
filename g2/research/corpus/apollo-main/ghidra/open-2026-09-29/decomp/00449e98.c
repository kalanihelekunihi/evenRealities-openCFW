
int CreateBlock(int param_1)

{
  int iVar1;
  
  iVar1 = 0;
  if (*(uint *)(param_1 + 0x1c) < *(uint *)(param_1 + 0x18)) {
    iVar1 = *(int *)(param_1 + 8) + *(int *)(param_1 + 0x1c) * *(int *)(param_1 + 0x14);
    *(int *)(param_1 + 0x1c) = *(int *)(param_1 + 0x1c) + 1;
  }
  return iVar1;
}

