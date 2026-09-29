
void FUN_005b9fd6(int param_1)

{
  bool bVar1;
  int *piVar2;
  int iVar3;
  undefined4 uVar4;
  
  piVar2 = DAT_005baa9c;
  if ((*DAT_005baa98 == '\0') || (param_1 == 0)) {
    bVar1 = false;
  }
  else {
    bVar1 = true;
  }
  if ((*DAT_005baa9c != 0) && (iVar3 = FUN_0043e2ea(*DAT_005baa9c), iVar3 == 1)) {
    if (param_1 == 0) {
      FUN_0043dfa4(*piVar2,1);
    }
    else {
      FUN_0043ded4(*piVar2,1);
    }
  }
  piVar2 = DAT_005baaa0;
  if ((*DAT_005baaa0 != 0) && (iVar3 = FUN_0043e2ea(*DAT_005baaa0), iVar3 == 1)) {
    if (bVar1) {
      FUN_0043dfa4(*piVar2,1);
    }
    else {
      FUN_0043ded4(*piVar2,1);
    }
  }
  piVar2 = DAT_005baaa4;
  if ((*DAT_005baaa4 != 0) && (iVar3 = FUN_0043e2ea(*DAT_005baaa4), iVar3 == 1)) {
    if (bVar1) {
      uVar4 = 0xe2;
    }
    else {
      uVar4 = 0xf6;
    }
    FUN_005b9d36(*piVar2,uVar4);
  }
  return;
}

