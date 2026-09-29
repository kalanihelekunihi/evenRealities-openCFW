
undefined4 FUN_005b86a0(undefined1 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int *piVar1;
  int iVar2;
  undefined4 uVar3;
  
  piVar1 = DAT_005b8990;
  if (((*DAT_005b8990 != 0) && (iVar2 = FUN_0043e2ea(*DAT_005b8990), iVar2 != 0)) &&
     (iVar2 = FUN_0047d9cc(), iVar2 != 0)) {
    uVar3 = FUN_005b7a02(param_1);
    FUN_00498680(*piVar1,uVar3);
  }
  return param_4;
}

