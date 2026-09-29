
void APP_PbTerminalTxEncodeAgentInterrupt
               (undefined4 param_1,undefined4 param_2,undefined4 param_3,uint param_4)

{
  int iVar1;
  uint local_c;
  
  local_c = param_4;
  FUN_0043c0e4(&local_c,1,0,param_4,param_1,param_2,param_3);
  local_c = local_c & 0xffffff00;
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    FUN_0043d574(3,DAT_005cf1d8,DAT_005cf1d4,DAT_005cf264,0xcb,DAT_005cf260,*DAT_005cf204 + 1);
  }
  iVar1 = FUN_0043d0ce();
  if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
    compress_log_output(0xc400000,DAT_005cf268,DAT_005cf268,*DAT_005cf204 + 1);
  }
  terminal_encode_and_send(0xa4,0xc,&local_c,*DAT_005cf204 + 1,1);
  return;
}

