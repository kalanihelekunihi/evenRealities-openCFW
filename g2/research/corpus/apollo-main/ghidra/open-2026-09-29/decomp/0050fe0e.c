
undefined4 FUN_0050fe0e(void)

{
  int iVar1;
  int iVar2;
  undefined4 in_r3;
  int iVar3;
  
  if (*DAT_0050fe7c != '\0') {
    for (iVar3 = 0; iVar1 = DAT_0050fe9c, iVar3 < 4; iVar3 = iVar3 + 1) {
      if (*(int *)(DAT_0050fe9c + iVar3 * 4) != 0) {
        FUN_00463eee(*(undefined4 *)(DAT_0050fe9c + iVar3 * 4));
        iVar1 = FUN_00463e9a(*(undefined4 *)(iVar1 + iVar3 * 4));
        if ((iVar1 != 0) && (iVar2 = FUN_0043e2ea(iVar1), iVar2 != 0)) {
          FUN_0043ded4(iVar1,1);
        }
      }
    }
  }
  return in_r3;
}

