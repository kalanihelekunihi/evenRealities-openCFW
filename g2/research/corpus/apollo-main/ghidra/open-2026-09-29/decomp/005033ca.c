
undefined8 AppConnOpen(undefined1 param_1,undefined4 param_2,undefined4 param_3)

{
  int iVar1;
  undefined4 uVar2;
  undefined4 uVar3;
  
  uVar3 = param_3;
  iVar1 = appMasterScanMode();
  if (iVar1 == 0) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      uVar3 = 0x7c;
      FUN_0043d574(4,DAT_00503470,DAT_0050346c,DAT_00503488,0x7c,DAT_00503490);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x10000000,DAT_00503494,DAT_00503494);
    }
    uVar2 = 0;
  }
  else {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      uVar3 = 0x79;
      FUN_0043d574(4,DAT_00503470,DAT_0050346c,DAT_00503488,0x79,DAT_00503484);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x10000000,DAT_0050348c,DAT_0050348c);
    }
    uVar2 = FUN_00503d1e(1,param_1,param_2,param_3);
  }
  return CONCAT44(uVar3,uVar2);
}

