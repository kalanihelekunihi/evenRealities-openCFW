
undefined4 FUN_005bb1cc(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int *piVar1;
  int iVar2;
  
  piVar1 = DAT_005bbcd0;
  if ((*DAT_005bbcd0 != 0) && (iVar2 = FUN_0043e2ea(*DAT_005bbcd0), iVar2 == 1)) {
    if (param_1 == 0) {
      FUN_0043dfa4(*piVar1,1);
    }
    else {
      FUN_0043ded4(*piVar1,1);
    }
  }
  return param_4;
}

