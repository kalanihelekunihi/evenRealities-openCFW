
int FUN_004cbefc(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 uStack_14;
  undefined4 uStack_10;
  undefined4 uStack_c;
  
  uStack_14 = param_2;
  uStack_10 = param_3;
  uStack_c = param_4;
  iVar1 = FUN_004cb3c8(param_1,param_2,DAT_004cc1e4,DAT_004ccb68,&uStack_14);
  if ((-1 < iVar1) || (iVar1 == -2)) {
    if (iVar1 != -2) {
      FUN_004caf82(&uStack_14);
      FUN_004caed4(param_3,&uStack_14);
    }
    iVar1 = 0;
  }
  return iVar1;
}

