
undefined4 APP_PbTerminalTxEncodeQueryReply(undefined4 *param_1)

{
  int iVar1;
  undefined4 uVar2;
  
  if (param_1 == (undefined4 *)0x0) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(1,DAT_005cf1d8,DAT_005cf1d4,DAT_005cf250,0xb9,DAT_005cf24c);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_005cf254,DAT_005cf254);
    }
    uVar2 = 6;
  }
  else {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(3,DAT_005cf1d8,DAT_005cf1d4,DAT_005cf250,0xbd,DAT_005cf258,*DAT_005cf204 + 1,
                   *param_1,param_1[1]);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0xcc00000,DAT_005cf25c,DAT_005cf25c,*DAT_005cf204 + 1,*param_1,param_1[1])
      ;
    }
    uVar2 = terminal_encode_and_send(0xa3,0xb,param_1,*DAT_005cf204 + 1,1);
  }
  return uVar2;
}

