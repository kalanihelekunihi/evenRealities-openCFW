
void APP_PbTerminalTxEncodeSessionSwitchRequest
               (undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 local_1c;
  undefined4 local_18;
  undefined4 uStack_14;
  
  uStack_14 = param_4;
  FUN_0043c0e4(&local_1c,8,0);
  local_1c = param_2;
  local_18 = param_1;
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    FUN_0043d574(3,DAT_005cf1d8,DAT_005cf1d4,DAT_005cf270,0xdb,DAT_005cf26c,*DAT_005cf204 + 1,
                 param_1,param_2);
  }
  iVar1 = FUN_0043d0ce();
  if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
    compress_log_output(0xcc00000,DAT_005cf274,DAT_005cf274,*DAT_005cf204 + 1,param_1,param_2);
  }
  terminal_encode_and_send(0xa5,0x12,&local_1c,*DAT_005cf204 + 1,1);
  return;
}

