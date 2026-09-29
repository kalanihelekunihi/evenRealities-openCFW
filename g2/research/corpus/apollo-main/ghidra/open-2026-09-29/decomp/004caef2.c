
undefined4 FUN_004caef2(int param_1)

{
  int iVar1;
  
  iVar1 = 0;
  while( true ) {
    if (2 < iVar1) {
      return 1;
    }
    if (*(int *)(param_1 + iVar1 * 4) != 0) break;
    iVar1 = iVar1 + 1;
  }
  return 0;
}

