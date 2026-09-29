
void APP_PbTerminalTxEncodeNewSessionRequest(undefined4 param_1)

{
  int iVar1;
  undefined4 local_10;
  
  FUN_0043c0e4(&local_10,4,0);
  local_10 = param_1;
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    FUN_0043d574(3,DAT_005cf1d8,DAT_005cf1d4,DAT_005cf27c,0xe9,DAT_005cf278,*DAT_005cf204 + 1,
                 param_1);
  }
  iVar1 = FUN_0043d0ce();
  if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
    compress_log_output(0xc800000,DAT_005cf280,DAT_005cf280,*DAT_005cf204 + 1,param_1);
  }
  terminal_encode_and_send(0xa6,0x13,&local_10,*DAT_005cf204 + 1,1);
  return;
}

