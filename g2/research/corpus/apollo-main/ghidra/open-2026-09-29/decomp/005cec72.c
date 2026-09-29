
undefined4
APP_PbTerminalTxEncodeVoiceInput
          (undefined1 *param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 uVar2;
  
  if (param_1 == (undefined1 *)0x0) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(1,DAT_005cf1d8,DAT_005cf1d4,DAT_005cf23c,0xa9,DAT_005cf238,param_3,param_4);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_005cf240,DAT_005cf240);
    }
    uVar2 = 6;
  }
  else {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(3,DAT_005cf1d8,DAT_005cf1d4,DAT_005cf23c,0xad,DAT_005cf244,*DAT_005cf204 + 1,
                   *param_1);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0xc800000,DAT_005cf248,DAT_005cf248,*DAT_005cf204 + 1,*param_1);
    }
    uVar2 = terminal_encode_and_send(0xa2,10,param_1,*DAT_005cf204 + 1,1);
  }
  return uVar2;
}

