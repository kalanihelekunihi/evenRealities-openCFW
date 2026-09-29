
undefined4
remove_subset_prefix(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  bool bVar1;
  int iVar2;
  int iVar3;
  
  iVar2 = FUN_0044a43c(param_1);
  iVar2 = iVar2 + 1;
  bVar1 = true;
  while (bVar1) {
    if ((iVar2 < 7) || (*(char *)(param_1 + 6) != '+')) {
      bVar1 = false;
    }
    else {
      for (iVar3 = 0; iVar3 < 6; iVar3 = iVar3 + 1) {
        if (0x19 < *(byte *)(param_1 + iVar3) - 0x41) {
          bVar1 = false;
        }
      }
      if (bVar1) {
        for (iVar3 = 7; iVar3 < iVar2; iVar3 = iVar3 + 1) {
          *(undefined1 *)(param_1 + iVar3 + -7) = *(undefined1 *)(param_1 + iVar3);
        }
        iVar2 = iVar2 + -7;
      }
    }
  }
  return param_4;
}

