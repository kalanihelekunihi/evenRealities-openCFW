
void _evenOtaReplyToAPP(undefined1 param_1,undefined1 param_2,undefined1 param_3,undefined4 param_4)

{
  int iVar1;
  undefined1 local_1c;
  undefined1 local_1b;
  undefined4 uStack_18;
  
  uStack_18 = param_4;
  FUN_0043c0e4(&local_1c,2,0);
  local_1c = param_2;
  local_1b = param_3;
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    FUN_0043d574(4,DAT_004455b0,DAT_004455ac,DAT_004455a8,0x328,DAT_004455a4,param_3);
  }
  iVar1 = FUN_0043d0ce();
  if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
    compress_log_output(0x10400000,DAT_004455b4,DAT_004455b4,param_3);
  }
  if (*DAT_004455b8 == '\0') {
    Thread_MsgTransport3TxByBle(1,param_1,&local_1c,2);
  }
  return;
}

