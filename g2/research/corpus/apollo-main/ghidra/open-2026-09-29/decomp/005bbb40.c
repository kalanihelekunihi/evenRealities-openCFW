
undefined4 FUN_005bbb40(undefined1 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int *piVar1;
  int iVar2;
  undefined4 uVar3;
  
  piVar1 = DAT_005bbd2c;
  if ((*DAT_005bbd2c != 0) && (iVar2 = FUN_0043e2ea(*DAT_005bbd2c), iVar2 != 0)) {
    uVar3 = FUN_005baba6(param_1);
    FUN_00498680(*piVar1,uVar3);
  }
  return param_4;
}

