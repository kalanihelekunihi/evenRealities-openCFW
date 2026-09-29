
void FUN_005d1d2a(int *param_1,int param_2)

{
  int iVar1;
  int iVar2;
  
  iVar2 = *param_1;
  iVar1 = *(int *)(iVar2 + 0x1e8);
  param_1[6] = *(int *)(iVar2 + 0x1a4);
  param_1[7] = *(int *)(iVar2 + 0x1a8);
  param_1[5] = *(int *)(iVar1 + 0x14);
  if (param_2 == 0) {
    iVar1 = *(int *)(iVar1 + 0x18);
  }
  else {
    iVar1 = *(int *)(iVar1 + 0x1c);
  }
  param_1[4] = iVar1;
  return;
}

