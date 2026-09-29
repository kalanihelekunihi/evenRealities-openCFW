
undefined4 FUN_005ba9e4(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int *piVar1;
  undefined1 uVar2;
  int iVar3;
  undefined4 uVar4;
  
  piVar1 = DAT_005bab14;
  if ((*DAT_005bab14 != 0) && (iVar3 = FUN_0043e2ea(*DAT_005bab14), iVar3 != 0)) {
    if (param_1 == 0) {
      FUN_00498680(*piVar1,PTR_DAT_005bab18);
    }
    else {
      uVar2 = FUN_0049c5bc();
      uVar4 = FUN_005b9d66(uVar2);
      FUN_00498680(*piVar1,uVar4);
    }
  }
  return param_4;
}

