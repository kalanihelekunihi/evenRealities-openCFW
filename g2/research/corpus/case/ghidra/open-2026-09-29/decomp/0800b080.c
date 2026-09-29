
bool FUN_0800b080(int param_1)

{
  int iVar1;
  int iVar2;
  
  FUN_0800bffc();
  iVar1 = *(int *)(param_1 + 0x38);
  iVar2 = *(int *)(param_1 + 0x3c);
  FUN_0800c014();
  return iVar1 == iVar2;
}

