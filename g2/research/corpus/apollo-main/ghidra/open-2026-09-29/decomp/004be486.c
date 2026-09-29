
undefined4
efsWriteCallback(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4,
                undefined2 param_5,undefined4 param_6)

{
  int iVar1;
  int iVar2;
  
  iVar1 = semantic_OtaTransferActive();
  if (iVar1 == 0) {
    iVar1 = FUN_004d0d80(param_6,param_5);
    if (iVar1 != 0) {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        FUN_0043d574(1,DAT_004be6a4,DAT_004be6a0,DAT_004be6b4,0x99,DAT_004be6bc,iVar1,param_4);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0x4400000,DAT_004be6c0,DAT_004be6c0,iVar1);
      }
    }
    fw_event_loop_remove_delayed(DAT_004be6c4);
  }
  else {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(4,DAT_004be6a4,DAT_004be6a0,DAT_004be6b4,0x93,DAT_004be6b0,param_3,param_4);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x10000000,DAT_004be6b8,DAT_004be6b8);
    }
  }
  return 0;
}

