
undefined4
eusWriteCallback(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4,
                undefined2 param_5,undefined4 param_6)

{
  int iVar1;
  int iVar2;
  
  iVar1 = TPL_ReceivePacket(0,param_6,param_5,param_4,param_1,param_2,param_3,param_4);
  if (iVar1 != 0) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(1,DAT_004be1d8,DAT_004be1d4,DAT_004be1e8,0x93,DAT_004be1e4,iVar1);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x4400000,DAT_004be1ec,DAT_004be1ec,iVar1);
    }
  }
  fw_event_loop_remove_delayed(DAT_004be1f0);
  return 0;
}

