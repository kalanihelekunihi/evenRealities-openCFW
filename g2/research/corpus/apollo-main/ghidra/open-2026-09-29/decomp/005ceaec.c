
undefined4 APP_PbTerminalTxEncodeCommResp(undefined1 *param_1,uint param_2)

{
  int iVar1;
  undefined4 uVar2;
  
  if (param_1 == (undefined1 *)0x0) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(1,DAT_005cf1d8,DAT_005cf1d4,DAT_005cf214,0x8a,DAT_005cf210);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_005cf218);
    }
    uVar2 = 6;
  }
  else {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(3,DAT_005cf1d8,DAT_005cf1d4,DAT_005cf214,0x8d,DAT_005cf21c,param_2,*param_1);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0xc800000,DAT_005cf220,DAT_005cf220,param_2,*param_1);
    }
    uVar2 = terminal_encode_and_send(0xf0,0xd,param_1,param_2 & 0xff,0);
  }
  return uVar2;
}

