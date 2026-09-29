
undefined8 FUN_005899a4(undefined4 param_1,undefined4 param_2,undefined4 param_3)

{
  int *piVar1;
  int iVar2;
  undefined4 uVar3;
  
  piVar1 = DAT_0058a30c;
  if (*DAT_0058a30c == 0) {
    iVar2 = osMutexNew(DAT_0058a310);
    *piVar1 = iVar2;
    if (*piVar1 == 0) {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        param_3 = 0x4e;
        FUN_0043d574(1,DAT_0058a320,DAT_0058a31c,DAT_0058a318,0x4e,DAT_0058a314);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0x4000000,DAT_0058a324,DAT_0058a324);
      }
      uVar3 = 0xffffffff;
      goto LAB_00589a4c;
    }
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      param_3 = 0x51;
      FUN_0043d574(4,DAT_0058a320,DAT_0058a31c,DAT_0058a318,0x51,DAT_0058a328);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x10000000,DAT_0058a32c,DAT_0058a32c);
    }
  }
  uVar3 = 0;
LAB_00589a4c:
  return CONCAT44(param_3,uVar3);
}

