
undefined8 FUN_005b6a52(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 uVar2;
  undefined4 uStack_18;
  undefined4 local_14;
  undefined4 uStack_10;
  
  iVar1 = DAT_005b7604;
  uStack_18 = param_2;
  local_14 = param_3;
  uStack_10 = param_4;
  FUN_0043c0e4(&uStack_18,8,0);
  if (*(int *)(iVar1 + 0x28) == 0) {
    uVar2 = 0;
  }
  else {
    FUN_0044e75e(*(undefined4 *)(iVar1 + 0x24),&uStack_18);
    uVar2 = FUN_005b6a3a(local_14);
  }
  return CONCAT44(uStack_18,uVar2);
}

