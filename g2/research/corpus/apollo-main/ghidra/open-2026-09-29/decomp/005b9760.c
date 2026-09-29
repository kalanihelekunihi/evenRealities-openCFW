
undefined8 FUN_005b9760(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int *piVar1;
  int iVar2;
  undefined4 uStack_20;
  undefined4 uStack_1c;
  undefined4 uStack_18;
  
  piVar1 = DAT_005b9c88;
  uStack_20 = param_2;
  uStack_1c = param_3;
  if ((*DAT_005b9c88 != 0) && (uStack_18 = param_4, iVar2 = FUN_0043e2ea(*DAT_005b9c88), iVar2 != 0)
     ) {
    FUN_0043c0e4(&uStack_20,8,0);
    FUN_004b4728(&uStack_20,DAT_005b9c8c,param_1,param_2);
    FUN_0049942e(*piVar1,&uStack_20);
  }
  return CONCAT44(uStack_1c,uStack_20);
}

