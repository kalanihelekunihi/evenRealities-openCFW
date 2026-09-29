
undefined8 FUN_005ba7ac(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int *piVar1;
  int iVar2;
  undefined4 uVar3;
  undefined4 uStack_20;
  undefined4 uStack_1c;
  undefined4 uStack_18;
  
  piVar1 = DAT_005baad8;
  uStack_20 = param_2;
  uStack_1c = param_3;
  uStack_18 = param_4;
  if ((*DAT_005baad8 != 0) && (iVar2 = FUN_0043e2ea(*DAT_005baad8), iVar2 == 1)) {
    FUN_0043c0e4(&uStack_20,8,0);
    FUN_005b9f06(param_1,param_2,&uStack_20,8);
    FUN_0049942e(*piVar1,&uStack_20);
  }
  piVar1 = DAT_005baad0;
  if ((*DAT_005baad0 != 0) && (iVar2 = FUN_0043e2ea(*DAT_005baad0), iVar2 == 1)) {
    uVar3 = FUN_005b9dfa(param_1);
    FUN_00498680(*piVar1,uVar3);
  }
  piVar1 = DAT_005baad4;
  if ((*DAT_005baad4 != 0) && (iVar2 = FUN_0043e2ea(*DAT_005baad4), iVar2 == 1)) {
    uVar3 = FUN_005b9e7e(param_2);
    FUN_00498680(*piVar1,uVar3);
  }
  return CONCAT44(uStack_1c,uStack_20);
}

