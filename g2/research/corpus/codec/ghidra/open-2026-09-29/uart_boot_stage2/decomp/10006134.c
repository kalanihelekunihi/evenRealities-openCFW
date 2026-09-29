
uint FUN_10006134(int param_1)

{
  int iVar1;
  uint uVar2;
  
  iVar1 = FUN_100060b0(param_1 + 0x24);
  uVar2 = 0;
  if (iVar1 != 0) {
    uVar2 = iVar1 + 0x23U & 0xffffffe0;
    *(int *)(uVar2 - 4) = iVar1;
  }
  return uVar2;
}

