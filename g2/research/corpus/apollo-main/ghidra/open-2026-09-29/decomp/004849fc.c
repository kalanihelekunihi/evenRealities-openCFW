
int FUN_004849fc(int param_1)

{
  int iVar1;
  
  iVar1 = *(int *)(param_1 + 0x44);
  if ((iVar1 != 0) && (*(int *)(iVar1 + 0x50) != 1)) {
    iVar1 = 0;
  }
  return iVar1;
}

