
int FUN_0050c476(int param_1)

{
  int iVar1;
  
  iVar1 = 0;
  while( true ) {
    if (3 < iVar1) {
      return 0;
    }
    if (*(int *)(iVar1 * 0x30 + DAT_0050c97c + 0x20) == param_1) break;
    iVar1 = iVar1 + 1;
  }
  return DAT_0050c97c + iVar1 * 0x30;
}

