
int FUN_004f5636(int param_1)

{
  int iVar1;
  
  iVar1 = 0;
  while( true ) {
    if ((int)(uint)*DAT_004f5c3c <= iVar1) {
      return -1;
    }
    if (*(int *)(DAT_004f5c3c + iVar1 * 0x94 + 0x8a) == param_1) break;
    iVar1 = iVar1 + 1;
  }
  return iVar1;
}

