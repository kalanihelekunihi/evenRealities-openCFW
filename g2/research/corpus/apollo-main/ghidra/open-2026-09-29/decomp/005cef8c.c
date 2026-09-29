
void APP_PbTerminalTxEncodeNewSessionCancel
               (undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 uStack_c;
  
  uStack_c = param_4;
  FUN_0043c0e4(&uStack_c,1,0,param_4,param_1,param_2,param_3);
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    FUN_0043d574(3,DAT_005cf1d8,DAT_005cf1d4,DAT_005cf288,0xf6,DAT_005cf284,*DAT_005cf204 + 1);
  }
  iVar1 = FUN_0043d0ce();
  if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
    compress_log_output(0xc400000,DAT_005cf28c,DAT_005cf28c,*DAT_005cf204 + 1);
  }
  terminal_encode_and_send(0xa8,0x16,&uStack_c,*DAT_005cf204 + 1,1);
  return;
}

