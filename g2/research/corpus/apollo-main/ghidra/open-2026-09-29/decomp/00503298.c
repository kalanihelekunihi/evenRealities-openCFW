
undefined4 appMasterScanMode(undefined4 param_1,undefined4 param_2,uint param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 uVar2;
  int iVar3;
  
  iVar3 = DAT_00503460;
  if (*(char *)(DAT_00503460 + 0x9d) == -1) {
    *(undefined1 *)(DAT_00503460 + 0x9d) = 0;
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      param_3 = (uint)*(byte *)(iVar3 + 0x9d);
      param_1 = 0x32;
      param_2 = DAT_00503464;
      FUN_0043d574(4,DAT_00503470,DAT_0050346c,DAT_00503468,0x32,DAT_00503464,param_3,param_4);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x10400000,DAT_00503474,DAT_00503474,*(undefined1 *)(iVar3 + 0x9d),param_1
                          ,param_2,param_3);
    }
    uVar2 = 1;
  }
  else if (*(char *)(DAT_00503460 + 0x9d) == '\0') {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(4,DAT_00503470,DAT_0050346c,DAT_00503468,0x38,DAT_00503464,
                   *(undefined1 *)(iVar3 + 0x9d));
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x10400000,DAT_00503474,DAT_00503474,*(undefined1 *)(iVar3 + 0x9d));
    }
    uVar2 = 1;
  }
  else {
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      FUN_0043d574(4,DAT_00503470,DAT_0050346c,DAT_00503468,0x3c,DAT_00503478);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0x10000000,DAT_0050347c,DAT_0050347c);
    }
    uVar2 = 0;
  }
  return uVar2;
}

