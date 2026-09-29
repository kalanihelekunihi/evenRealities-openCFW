
int FUN_005b6a06(void)

{
  int iVar1;
  int iVar2;
  
  if (*(int *)(DAT_005b7604 + 0x24) == 0) {
    iVar1 = 0;
  }
  else {
    iVar1 = FUN_0043fdda(*(undefined4 *)(DAT_005b7604 + 0x24));
    iVar2 = FUN_005b4770();
    if (iVar1 < iVar2 * 0x1c) {
      iVar1 = iVar2 * 0x1c - iVar1;
    }
    else {
      iVar1 = 0;
    }
  }
  return iVar1;
}

