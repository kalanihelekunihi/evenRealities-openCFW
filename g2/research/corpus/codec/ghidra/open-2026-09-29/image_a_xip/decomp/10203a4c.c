
int gx8002_dma_select(void)

{
  undefined4 uVar1;
  int iVar2;
  
  uVar1 = func_0x10025560();
  iVar2 = 0;
  while( true ) {
    if (iVar2 == *(int *)(DAT_10203a94 + 4)) {
      func_0x1002556c(uVar1);
      return -1;
    }
    if (*(char *)(DAT_10203a94 + iVar2 + 0x370) == '\0') break;
    iVar2 = iVar2 + 1;
  }
  *(undefined1 *)(DAT_10203a94 + iVar2 + 0x370) = 1;
  func_0x10025080(0x19,1);
  func_0x1002556c(uVar1);
  return iVar2;
}

