
int FUN_004effda(void)

{
  int iVar1;
  int iVar2;
  
  iVar1 = 0;
  for (iVar2 = 0; iVar2 < 5; iVar2 = iVar2 + 1) {
    if (*(char *)(DAT_004f0dfc + iVar2 * 0x1c98) == '\x01') {
      iVar1 = iVar1 + 1;
    }
  }
  return iVar1;
}

