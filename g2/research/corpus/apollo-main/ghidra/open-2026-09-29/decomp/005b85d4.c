
void FUN_005b85d4(int param_1,undefined1 param_2)

{
  int *piVar1;
  int *piVar2;
  int iVar3;
  undefined4 uVar4;
  
  piVar1 = DAT_005b887c;
  if ((*DAT_005b887c != 0) &&
     (iVar3 = FUN_0043e2ea(*DAT_005b887c), piVar2 = DAT_005b8990, iVar3 != 0)) {
    if (param_1 == 0) {
      if ((*DAT_005b8990 != 0) && (iVar3 = FUN_0043e2ea(*DAT_005b8990), iVar3 != 0)) {
        FUN_0044d7b8(*piVar2);
      }
      *piVar2 = 0;
    }
    else if ((*DAT_005b8990 == 0) || (iVar3 = FUN_0043e2ea(*DAT_005b8990), iVar3 == 0)) {
      iVar3 = FUN_00498668(*piVar1);
      *piVar2 = iVar3;
      FUN_0043ded4(*piVar2,0x10000);
      FUN_0043dfa4(*piVar2,0x10);
      iVar3 = FUN_0047d9cc();
      if (iVar3 == 0) {
        FUN_00498680(*piVar2,DAT_005b8994);
      }
      else {
        uVar4 = FUN_005b7a02(param_2);
        FUN_00498680(*piVar2,uVar4);
      }
    }
  }
  return;
}

