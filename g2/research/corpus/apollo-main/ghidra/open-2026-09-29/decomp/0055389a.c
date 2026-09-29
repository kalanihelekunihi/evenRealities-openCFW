
undefined4 FUN_0055389a(void)

{
  int iVar1;
  undefined4 in_r3;
  int iVar2;
  
  if (*DAT_00553d44 != '\0') {
    for (iVar2 = 0; iVar1 = DAT_00553ff0, iVar2 < 4; iVar2 = iVar2 + 1) {
      if (*(int *)(DAT_00553ff0 + iVar2 * 4) != 0) {
        FUN_00463eee(*(undefined4 *)(DAT_00553ff0 + iVar2 * 4));
        iVar1 = FUN_00463e9a(*(undefined4 *)(iVar1 + iVar2 * 4));
        if (iVar1 != 0) {
          FUN_0043ded4(iVar1,1);
        }
      }
    }
  }
  return in_r3;
}

