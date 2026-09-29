
void FUN_005ba930(int param_1,undefined1 param_2)

{
  int *piVar1;
  int *piVar2;
  int iVar3;
  undefined4 uVar4;
  
  piVar1 = DAT_005bab04;
  if ((*DAT_005bab04 != 0) &&
     (iVar3 = FUN_0043e2ea(*DAT_005bab04), piVar2 = DAT_005bab14, iVar3 != 0)) {
    if (param_1 == 0) {
      if ((*DAT_005bab14 != 0) && (iVar3 = FUN_0043e2ea(*DAT_005bab14), iVar3 != 0)) {
        FUN_0044d7b8(*piVar2);
      }
      *piVar2 = 0;
    }
    else {
      if ((*DAT_005bab14 != 0) && (iVar3 = FUN_0043e2ea(*DAT_005bab14), iVar3 != 0)) {
        return;
      }
      iVar3 = FUN_00498668(*piVar1);
      *piVar2 = iVar3;
      FUN_0043ded4(*piVar2,0x10000);
      FUN_0043dfa4(*piVar2,0x10);
      iVar3 = FUN_0047d9cc();
      if (iVar3 == 0) {
        FUN_00498680(*piVar2,PTR_DAT_005bab18);
      }
      else {
        uVar4 = FUN_005b9d66(param_2);
        FUN_00498680(*piVar2,uVar4);
      }
    }
    FUN_0043f66c(*DAT_005baac8);
    iVar3 = FUN_0043fdda(*piVar1);
    FUN_005b9d36(*piVar1,0x11e - iVar3);
  }
  return;
}

