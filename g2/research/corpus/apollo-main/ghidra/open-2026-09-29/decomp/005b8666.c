
undefined4 FUN_005b8666(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int *piVar1;
  undefined1 uVar2;
  int iVar3;
  undefined4 uVar4;
  
  piVar1 = DAT_005b8990;
  if ((*DAT_005b8990 != 0) && (iVar3 = FUN_0043e2ea(*DAT_005b8990), iVar3 != 0)) {
    if (param_1 == 0) {
      FUN_00498680(*piVar1,DAT_005b8994);
    }
    else {
      uVar2 = FUN_0049c5bc();
      uVar4 = FUN_005b7a02(uVar2);
      FUN_00498680(*piVar1,uVar4);
    }
  }
  return param_4;
}

