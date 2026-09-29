
undefined4 APP_PbTerminalTxEncodeStatusReply(undefined1 *param_1)

{
  int iVar1;
  undefined4 uVar2;
  
  if (param_1 == (undefined1 *)0x0) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(1,DAT_005cf1d8,DAT_005cf1d4,DAT_005cf228,0x99,DAT_005cf224);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_005cf22c,DAT_005cf22c);
    }
    uVar2 = 6;
  }
  else {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(3,DAT_005cf1d8,DAT_005cf1d4,DAT_005cf228,0x9d,DAT_005cf230,*DAT_005cf204 + 1,
                   *param_1,param_1[1]);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0xcc00000,DAT_005cf234,DAT_005cf234,*DAT_005cf204 + 1,*param_1,param_1[1])
      ;
    }
    uVar2 = terminal_encode_and_send(0xa1,9,param_1,*DAT_005cf204 + 1,1);
  }
  return uVar2;
}

