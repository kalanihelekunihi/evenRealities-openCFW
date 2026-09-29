
undefined4 FUN_005b9a68(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  int *piVar2;
  int iVar3;
  int iVar4;
  
  if (param_1 == 0) {
    for (iVar4 = 0; piVar2 = DAT_005b9cc8, iVar1 = DAT_005b9c44, iVar4 < 3; iVar4 = iVar4 + 1) {
      if ((*(int *)(DAT_005b9c44 + iVar4 * 4) != 0) &&
         (iVar3 = FUN_0043e2ea(*(undefined4 *)(DAT_005b9c44 + iVar4 * 4)), iVar3 == 1)) {
        FUN_0043ded4(*(undefined4 *)(iVar1 + iVar4 * 4),1);
      }
    }
    if ((*DAT_005b9cc8 != 0) && (iVar4 = FUN_0043e2ea(*DAT_005b9cc8), iVar4 == 1)) {
      FUN_0043dfa4(*piVar2,1);
    }
  }
  else {
    for (iVar4 = 0; piVar2 = DAT_005b9cc8, iVar1 = DAT_005b9c44, iVar4 < 3; iVar4 = iVar4 + 1) {
      if ((*(int *)(DAT_005b9c44 + iVar4 * 4) != 0) &&
         (iVar3 = FUN_0043e2ea(*(undefined4 *)(DAT_005b9c44 + iVar4 * 4)), iVar3 == 1)) {
        FUN_0043dfa4(*(undefined4 *)(iVar1 + iVar4 * 4),1);
      }
    }
    if ((*DAT_005b9cc8 != 0) && (iVar4 = FUN_0043e2ea(*DAT_005b9cc8), iVar4 == 1)) {
      FUN_0043ded4(*piVar2,1);
    }
  }
  return param_4;
}

