
void APP_PbTerminalTxEncodeDisplayStateNotify(char param_1,undefined4 param_2,undefined1 param_3)

{
  int iVar1;
  char local_20 [4];
  undefined4 local_1c;
  undefined1 local_18;
  
  FUN_0043c0e4(local_20,0xc,0);
  local_1c = param_2;
  if (param_1 != '\x04') {
    local_1c = 0;
    param_3 = 0;
  }
  local_20[0] = param_1;
  local_18 = param_3;
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    FUN_0043d574(3,DAT_005cf1d8,DAT_005cf1d4,DAT_005cf294,0x108,DAT_005cf290,*DAT_005cf204 + 1,
                 param_1,local_1c,local_18);
  }
  iVar1 = FUN_0043d0ce();
  if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
    compress_log_output(0xd000000,DAT_005cf298,DAT_005cf298,*DAT_005cf204 + 1,param_1,local_1c,
                        local_18);
  }
  terminal_encode_and_send(0xa7,0x14,local_20,*DAT_005cf204 + 1,1);
  return;
}

