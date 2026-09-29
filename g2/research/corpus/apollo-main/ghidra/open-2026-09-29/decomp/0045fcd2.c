
int FUN_0045fcd2(int param_1)

{
  int iVar1;
  int iVar2;
  
  if (param_1 != 0) {
    for (iVar1 = FUN_0044dca2(); iVar1 != 0; iVar1 = FUN_0044dca2(iVar1)) {
      iVar2 = *(int *)(iVar1 + 0x10);
      if ((iVar2 != 0) && (*(int *)(iVar2 + 0x18) == iVar1)) {
        return iVar2;
      }
    }
  }
  return 0;
}

